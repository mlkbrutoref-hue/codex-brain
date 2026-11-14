"""Experimental state-driven Shopee Video USB publisher. No coordinate table."""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import threading
import time
import unicodedata
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from app.operational.deadlines import OperationalStop
from app.operational.config import ActionType, FeatureMode

PACKAGE = "com.shopee.br"
ADB_DIR = Path(r"C:\Users\GAMER\Downloads\platform-tools-latest-windows\platform-tools")
STATES = (
    "DEVICE_READY SHOPEE_PROFILE MEDIA_PICKER_OPEN MEDIA_FOUND MEDIA_SELECTED "
    "MEDIA_PREVIEW EDITOR_MEDIA_REVIEW EDITOR_READY CAPTION_READY CAPTION_FILLED PRODUCT_SELECTOR_OPEN "
    "LIKED_PRODUCTS_OPEN PRODUCT_FOUND PRODUCT_SELECTED PRODUCT_LINKED "
    "POST_VALIDATION READY_TO_PUBLISH READY_FOR_PUBLISH ASSISTED_VALIDATED PUBLISHING PUBLISHED REVIEW ERROR"
).split()


class RpaError(RuntimeError):
    pass


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def normalized(value):
    return " ".join("".join(c for c in unicodedata.normalize("NFKD", value.casefold())
                             if not unicodedata.combining(c)).split())


def compose_caption(caption, hashtags):
    caption = " ".join(caption.split())
    tags = ["#" + tag.lstrip("#") for tag in hashtags]
    if not caption or not tags or any(not re.fullmatch(r"#\w+", tag) for tag in tags):
        raise RpaError("INVALID_CAPTION_OR_HASHTAGS")
    if len(set(tag.casefold() for tag in tags)) != len(tags):
        raise RpaError("DUPLICATE_HASHTAGS")
    value = caption + " " + " ".join(tags)
    # Android length filters count UTF-16 code units, not Python code points.
    if len(value.encode("utf-16-le")) // 2 > 150:
        raise RpaError("CAPTION_EXCEEDS_OBSERVED_150_LIMIT")
    return value


def video_profile_account_matches(screen, username):
    """Accept exact native username labels, never nickname/substrings."""
    return bool(username and any(n.get('text') in (username, 'Nome de usuário: '+username) for n in screen.nodes))


class Screen:
    def __init__(self, xml):
        self.root = ET.fromstring(xml)
        self.nodes = [n.attrib for n in self.root.iter("node")
                      if n.get("package", "").startswith(PACKAGE)]

    def ids(self, suffix):
        return [n for n in self.nodes if n.get("resource-id", "").endswith("/" + suffix)]

    def texts(self, text):
        return [n for n in self.nodes if n.get("text") == text]

    def has(self, suffix):
        return bool(self.ids(suffix))

    def guard(self):
        # Never persist account verification text or screenshots containing codes.
        labels = " ".join(normalized(n.get("text", "") + " " + n.get("content-desc", ""))
                          for n in self.nodes if not n.get("resource-id", "").endswith("/et_caption"))
        if any(n.get("password") == "true" for n in self.nodes) or any(
            marker in labels for marker in ("captcha", "codigo de verificacao", "codigo sms",
            "verifique sua identidade", "verificacao de seguranca", "verifique que voce",
            "confirmar sua identidade", "faca login", "entrar na shopee")):
            raise RpaError("HUMAN_ACCOUNT_VERIFICATION_REQUIRED")
        if any(marker in labels for marker in ("nao foi possivel", "falha ao", "erro de rede",
                                                "tente novamente", "problema de conexao")):
            raise RpaError("VISIBLE_APP_ERROR")
        if any(marker in labels for marker in ('conta restrita', 'conta suspensa', 'alerta de seguranca',
            'confirmar dispositivo', 'autenticacao de dois fatores', 'senha', 'dados bancarios', 'cartao de credito')):
            raise RpaError('HUMAN_ACCOUNT_VERIFICATION_REQUIRED')


def share_icon_is_inactive(node, screenshot):
    bounds = tuple(map(int, re.findall(r"\d+", node.get("bounds", ""))))
    if len(bounds) != 4 or bounds[2] <= bounds[0] or bounds[3] <= bounds[1]:
        return False
    crop = screenshot.convert("RGB").crop(bounds)
    pixels = list(crop.getdata())
    # Observed inactive share icons are grey; selected WhatsApp is green.
    return (bool(pixels) and len(set(pixels)) > 1
            and sum(35 < max(p) < 225 for p in pixels) / len(pixels) > .05
            and sum(max(p) - min(p) > 25 for p in pixels) / len(pixels) < .02)


def validation_checks(screen, expected_caption, product_title, media_ok, sharing_ok=False):
    caption_nodes = screen.ids("et_caption")
    products = screen.ids("tv_product_title")
    buttons = screen.ids("btn_post")
    text = caption_nodes[0].get("text", "") if len(caption_nodes) == 1 else ""
    tags = re.findall(r"#\w+", expected_caption)
    try:
        screen.guard()
        no_error = True
    except RpaError:
        no_error = False
    return dict(
        video_selected=bool(media_ok and screen.has("iv_video_preview")),
        caption_exact=text == expected_caption,
        hashtags_present=all(tag in re.findall(r"#\w+", text) for tag in tags),
        product_linked=len(products) == 1 and products[0].get("text") == product_title,
        no_visible_error=no_error,
        automatic_sharing_disabled=bool(sharing_ok),
        caption_overlay_closed=not screen.has("tv_right") and not screen.has("rv_hashtag"),
        post_enabled=len(buttons) == 1 and buttons[0].get("enabled") == "true"
            and buttons[0].get("clickable") == "true"
            and buttons[0].get("visible-to-user", "true") == "true",
    )


@dataclass(frozen=True)
class ProductCard:
    title: str
    button_xpath: str
    shop_id: str | None = None
    item_id: str | None = None


def product_cards(screen, query, exact_title=None):
    """Bound the title/button to one observed card; ambiguous ancestors are refused."""
    parents = {child: parent for parent in screen.root.iter() for child in parent}
    matches = []
    terms = normalized(query).split()
    if not terms and not exact_title:
        raise RpaError("PRODUCT_QUERY_REQUIRED")
    for node in screen.root.iter("node"):
        title = node.get("text", "")
        if exact_title and title != exact_title:
            continue
        if not exact_title and not all(term in normalized(title).split() for term in terms):
            continue
        ancestor = parents.get(node)
        depth = 0
        while ancestor is not None and ancestor.tag == 'node' and depth < 3:
            if any(v in ancestor.get('class', '') for v in ('RecyclerView', 'ListView', 'ScrollView')):
                break
            buttons = [n for n in ancestor.iter("node") if n.get("text") == "Adicionar"]
            if buttons:
                labels = [n.get('text', '') for n in ancestor.iter('node') if n.get('text') and n not in buttons and n is not node]
                # A foreign product title anywhere in the candidate card makes binding unsafe.
                safe_labels = all(re.fullmatch(r'(?:R\$\s*)?[\d.,%\s]+|R\$\s*[\d.,]+\s*[-–]\s*R\$\s*[\d.,]+|Taxa de comissão \d+(?:[.,]\d+)?%|[\d.,]+(?:mil|mi)?\+? vendido\(s\)', v) for v in labels)
                if len(buttons) == 1 and safe_labels:
                    parts = []
                    current = buttons[0]
                    while current is not screen.root:
                        parent = parents[current]
                        siblings = [n for n in parent if n.tag == current.tag]
                        parts.append(f'{current.tag}[{siblings.index(current)+1}]')
                        current = parent
                    path = '/' + screen.root.tag + '/' + '/'.join(reversed(parts))
                    labels = ' '.join(n.get('text','') + ' ' + n.get('content-desc','') for n in ancestor.iter('node'))
                    ids = set(re.findall(r'shopee\.com\.br/product/(\d+)/(\d+)',labels))
                    identity = next(iter(ids)) if len(ids)==1 else (None,None)
                    matches.append(ProductCard(title, path, *identity))
                break
            ancestor = parents.get(ancestor)
            depth += 1
    return matches


def matching_product_rows(screen, query, exact_title=None):
    return [card.title for card in product_cards(screen, query, exact_title)]


def product_sheet_matches(screen, title):
    # Native sheet repeats the same title in the card and editable name preview.
    return (len(screen.texts('Editar informações do produto')) == 1
            and 1 <= len(screen.texts(title)) <= 2 and len(screen.texts('Feito')) == 1)


def xpath_literal(value):
    if "'" not in value:
        return "'" + value + "'"
    if '"' not in value:
        return '"' + value + '"'
    return "concat(" + ',"\'",'.join("'" + part + "'" for part in value.split("'")) + ")"


def parse_media_inventory(output, *, preserve_query_order=False):
    pattern = re.compile(r"_id=(\d+), _display_name=(.*?), _data=(.*?), date_added=(\d+), duration=(\d+), _size=(\d+)")
    rows = []
    for line in output.splitlines():
        match = pattern.search(line)
        if match:
            media_id, name, path, added, duration, size = match.groups()
            rows.append(dict(media_id=media_id, name=name, video_path=path,
                             date_added=int(added), duration_ms=int(duration), size=int(size)))
    return rows if preserve_query_order else sorted(rows, key=lambda row: (row["date_added"], int(row["media_id"])), reverse=True)


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8") as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(temp, path)


@contextmanager
def device_lock(serial, folder):
    if not re.fullmatch(r"[A-Za-z0-9_-]+", serial):
        raise RpaError("INVALID_SERIAL")
    path = Path(folder) / f"{serial}.lock"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+b") as f:
        if path.stat().st_size == 0:
            f.write(b"0")
            f.flush()
        f.seek(0)
        if os.name == "nt":
            import msvcrt
            try:
                msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError as exc:
                raise RpaError("DEVICE_ALREADY_IN_USE") from exc
            try:
                yield
            finally:
                f.seek(0)
                msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            try:
                yield
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)


class ShopeeVideoPublisher:
    def __init__(self, device, config, root=Path(".")):
        self.d = device
        self.config = config
        self.root = Path(root).resolve()
        self.expected_caption = compose_caption(config["caption"], config["hashtags"])
        job = config["job_id"]
        if not re.fullmatch(r"[A-Za-z0-9_-]+", job):
            raise RpaError("INVALID_JOB_ID")
        self.debug = self.root / "debug/shopee_android" / job
        self.logs = self.root / "logs/shopee_android"
        self.debug.mkdir(parents=True, exist_ok=True)
        self.logs.mkdir(parents=True, exist_ok=True)
        self.session_path = self.debug / "session.json"
        self.session = json.loads(self.session_path.read_text(encoding="utf-8")) if self.session_path.exists() else dict(
            job_id=job, state="DEVICE_READY", created_at=now(), transitions=[], publish_attempted=False)
        fingerprint = hashlib.sha256(json.dumps(config, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        if self.session.get("config_sha256", fingerprint) != fingerprint:
            raise RpaError("SESSION_INPUT_CHANGED")
        self.session["config_sha256"] = fingerprint
        self.last_action = {"action": "observe", "selector": None}
        self.safety = None
        self._device_hash_cache = {}

    def get_device_video_hash(self, video_path):
        if not hasattr(self, "_device_hash_cache"):
            self._device_hash_cache = {}
        if video_path in self._device_hash_cache:
            return self._device_hash_cache[video_path]
        remote = self.d.shell(["sha256sum", video_path])
        if remote.exit_code or not re.match(r"^[a-f0-9]{64}\b", remote.output):
            raise RpaError("MEDIA_HASH_UNAVAILABLE")
        h = remote.output.split()[0]
        self._device_hash_cache[video_path] = h
        return h

    def require_ui(self):
        from app.mobile.ui import ShopeeUI
        if self.safety is None or not isinstance(self.d, ShopeeUI):
            raise RpaError('OPERATIONAL_UI_REQUIRED')

    def observe(self):
        self.require_ui()
        screen = Screen(self.d.dump_hierarchy())
        screen.guard()
        if self.d.app_current().get("package") != PACKAGE:
            raise RpaError("UNEXPECTED_FOREGROUND_APP")
        return screen

    def wait(self, predicate, timeout=20):
        self.require_ui()
        timeout = self.safety.deadline.child_timeout(timeout)
        deadline = time.monotonic() + timeout
        while True:
            try:
                screen = self.observe()
            except RpaError as error:
                # During a dispatched native transition, Android can report a
                # temporary foreground. Only poll; never act until Shopee returns.
                if str(error) != 'UNEXPECTED_FOREGROUND_APP' or not self.d.pending_effect:
                    raise
                if time.monotonic() >= deadline:
                    raise RpaError('EXPECTED_STATE_TIMEOUT') from error
                self.safety.deadline.wait(min(.25,max(.001,deadline-time.monotonic())))
                continue
            if predicate(screen):
                self.d.pending_effect = False
                return screen
            if time.monotonic() >= deadline:
                raise RpaError("EXPECTED_STATE_TIMEOUT")
            self.safety.deadline.wait(min(.25, max(.001, deadline - time.monotonic())))

    def checkpoint(self, state, error=None, extra=None):
        if state not in STATES:
            raise RpaError('INVALID_STATE')
        # Do not retain full XML, screenshots, user text, OTP, or selector values.
        event = dict(timestamp=now(), state=state, result='ERROR' if error else 'OBSERVED',
                     error=error, action=self.last_action.get('action'), evidence={})
        self.session['state'] = state
        self.session['transitions'].append(event)
        atomic_json(self.session_path, self.session)
        if self.safety:
            self.safety.logger.log_transition(state=state,status=event['result'])
        return event

    def tap_id(self, suffix, condition, target, precondition=None):
        self.require_ui()
        screen = self.observe()
        if precondition is not None and not precondition(screen):
            raise RpaError('MEDIA_SELECTION_CHANGED_REVIEW_REQUIRED')
        nodes = screen.ids(suffix)
        if len(nodes) != 1 or nodes[0].get("enabled") != "true":
            raise RpaError("MISSING_OR_AMBIGUOUS_SELECTOR:" + suffix)
        selector = dict(resourceId=nodes[0]["resource-id"])
        self.last_action = dict(action="click", selector=selector)
        self.d(**selector).click(timeout=10)
        screen = self.wait(condition)
        self.checkpoint(target)
        return screen

    def fill_caption(self):
        self.require_ui()
        screen = self.observe()
        nodes = screen.ids("et_caption")
        if len(nodes) != 1:
            raise RpaError("CAPTION_FIELD_NOT_UNIQUE")
        selector = dict(resourceId=nodes[0]["resource-id"])
        self.last_action = dict(action="set_text", selector=selector)
        self.d(**selector).set_text(self.expected_caption, timeout=10)
        screen = self.wait(lambda s: len(s.ids("et_caption")) == 1 and s.ids("et_caption")[0].get("text") == self.expected_caption)
        if screen.has("tv_right"):
            self.tap_id("tv_right", lambda s: s.has("btn_post") and not s.has("tv_right"), "CAPTION_FILLED")
        else:
            self.checkpoint("CAPTION_FILLED")

    def sharing_disabled(self):
        self.require_ui()
        screen = self.observe()
        controls = [screen.ids(suffix) for suffix in ('iv_whatsapp','iv_instagram','iv_facebook')]
        if all(len(nodes)==1 and nodes[0].get('checkable')=='true' and nodes[0].get('checked')=='false' for nodes in controls):
            return True
        if not self.safety.config.ui_pixel_fallback:
            return False
        image = self.d.screenshot()
        return all(len(screen.ids(suffix)) == 1 and share_icon_is_inactive(screen.ids(suffix)[0], image)
                   for suffix in ("iv_whatsapp", "iv_instagram", "iv_facebook"))

    def ensure_shopee_only(self):
        self.require_ui()
        if self.sharing_disabled():
            return
        if not self.safety.config.ui_pixel_fallback:
            raise RpaError('SHARING_STATE_REVIEW_REQUIRED')
        for suffix in ("iv_whatsapp", "iv_instagram", "iv_facebook"):
            screen = self.observe()
            nodes = screen.ids(suffix)
            if len(nodes) != 1:
                raise RpaError("SHARE_CONTROL_NOT_UNIQUE")
            if not share_icon_is_inactive(nodes[0], self.d.screenshot()):
                self.tap_id(suffix, lambda s: len(s.ids(suffix)) == 1 and share_icon_is_inactive(s.ids(suffix)[0], self.d.screenshot()), "POST_VALIDATION")
        if not self.sharing_disabled():
            raise RpaError("AUTOMATIC_SHARING_NOT_DISABLED")

    def tap_text(self, text, condition, target):
        self.require_ui()
        nodes = self.observe().texts(text)
        if len(nodes) != 1 or nodes[0].get("enabled") != "true":
            raise RpaError("MISSING_OR_AMBIGUOUS_TEXT_SELECTOR")
        self.last_action = dict(action="click", selector=dict(text=text))
        self.d(text=text).click(timeout=10)
        screen = self.wait(condition)
        self.checkpoint(target)
        return screen

    def liked_tab_active(self, screen):
        self.require_ui()
        tab_nodes = screen.texts('Minhas Curtidas')
        if len(tab_nodes)==1 and tab_nodes[0].get('selected')=='true':
            return True
        if not self.safety.config.ui_pixel_fallback:
            return False
        # RN tabs do not expose selected/color. Inspect the underline pixels
        # within the tab's CURRENT XML bounds; no hard-coded screen coordinates.
        nodes = [n for n in screen.root.iter("node") if n.get("text") == "Minhas Curtidas"]
        if len(nodes) != 1:
            return False
        parents = {child: parent for parent in screen.root.iter() for child in parent}
        parent = parents.get(nodes[0])
        if parent is None:
            return False
        bounds = tuple(map(int, re.findall(r"\d+", parent.get("bounds", ""))))
        if len(bounds) != 4:
            return False
        left, top, right, bottom = bounds
        crop = self.d.screenshot().convert("RGB").crop((left, max(top, bottom - 6), right, bottom))
        pixels = list(crop.getdata())
        return bool(pixels) and sum(r > 180 and g < 140 and b < 130 for r, g, b in pixels) / len(pixels) > .25

    def select_product(self):
        self.require_ui()
        screen = self.observe()
        self.safety.budget.consume(ActionType.PRODUCT_LOOKUP)
        if screen.has("tv_product_title"):
            titles = screen.ids("tv_product_title")
            if len(titles) != 1 or titles[0].get("text") != self.config.get("product_title"):
                raise RpaError("EXISTING_PRODUCT_MISMATCH")
            self.safety.product_evidence(screen)
            self.checkpoint("PRODUCT_LINKED")
            return
        if screen.has("ll_add_product_symbol"):
            screen = self.tap_id("ll_add_product_symbol", lambda s: bool(s.texts("Minhas Curtidas")), "PRODUCT_SELECTOR_OPEN")
        if not self.liked_tab_active(screen):
            screen = self.tap_text("Minhas Curtidas", self.liked_tab_active, "LIKED_PRODUCTS_OPEN")
        else:
            self.checkpoint("LIKED_PRODUCTS_OPEN")
        if not self.config.get('product_title'):
            raise RpaError('EXACT_PRODUCT_TITLE_REQUIRED_REVIEW')
        cards = product_cards(screen, self.config['product_query'], self.config['product_title'])
        if not cards:
            # Do not search to resolve duplicates or malformed visible exact cards.
            if screen.texts(self.config['product_title']):
                raise RpaError('AMBIGUOUS_PRODUCT_CARD_REVIEW')
            searches = [n for n in screen.nodes if n.get("class") == "android.widget.EditText"]
            if len(searches) != 1:
                raise RpaError("PRODUCT_SEARCH_FIELD_NOT_UNIQUE")
            self.last_action = dict(action="set_product_query", selector=dict(className="android.widget.EditText"))
            self.d(className="android.widget.EditText", packageName=PACKAGE).set_text(self.config["product_query"])
            self.wait(lambda s: self.liked_tab_active(s) and any(n.get("class") == "android.widget.EditText" and n.get("text") == self.config["product_query"] for n in s.nodes))
            self.d.press("enter")
            screen = self.wait(lambda s: self.liked_tab_active(s) and bool(matching_product_rows(s, self.config["product_query"], self.config['product_title'])))
        if not self.liked_tab_active(screen):
            raise RpaError("LIKED_TAB_NOT_CONFIRMED_AFTER_SEARCH")
        matches = matching_product_rows(screen, self.config["product_query"], self.config.get("product_title"))
        if len(matches) != 1:
            raise RpaError("AMBIGUOUS_PRODUCT_MATCH")
        title = matches[0]
        # Persist discovered exact title; do not mutate the input fingerprint.
        self.session["product_title"] = title
        self.checkpoint("PRODUCT_FOUND", extra=dict(matched_title=title))
        cards = product_cards(screen, self.config['product_query'], self.config.get('product_title'))
        if len(cards) != 1:
            raise RpaError('AMBIGUOUS_PRODUCT_CARD')
        card_evidence = self.safety.product_card_evidence(screen, cards[0])
        xpath = cards[0].button_xpath
        buttons = self.d.xpath(xpath)
        if len(buttons.all()) != 1:
            raise RpaError("PRODUCT_ROW_BUTTON_NOT_UNIQUE")
        self.last_action = dict(action="link_product", selector=dict(xpath=xpath))
        buttons.click(timeout=10, expected_screen_sha256=self.safety._evidence_digest(screen.nodes))
        self.wait(lambda s: product_sheet_matches(s, title))
        self.checkpoint("PRODUCT_SELECTED")
        screen = self.tap_text("Feito", lambda s: s.has('btn_post') and len(s.ids("tv_product_title")) == 1 and s.ids("tv_product_title")[0].get("text") == title, "PRODUCT_LINKED")
        self.safety.bind_selected_card(screen, card_evidence)
        self.safety.product_evidence(screen)

    def media_inventory(self):
        self.require_ui()
        order=self.config.get('media_sort_order','date_added DESC')
        if order not in ('date_added DESC','date_modified DESC'):
            raise RpaError('UNAPPROVED_MEDIA_SORT_ORDER')
        return self.d.shell(['content','query','--uri','content://media/external/video/media',
            '--projection','_id:_display_name:_data:date_added:duration:_size','--sort',order])

    def select_media(self):
        self.require_ui()
        screen = self.observe()
        if any(n.get("content-desc") == "click to post video" for n in screen.nodes):
            expected_account = self.config.get("expected_account")
            if expected_account and not video_profile_account_matches(screen, expected_account):
                raise RpaError("PROFILE_ACCOUNT_MISMATCH")
            self.checkpoint("SHOPEE_PROFILE")
            self.last_action = dict(action="click", selector=dict(description="click to post video"))
            self.d(description="click to post video").click(timeout=10)
            self.wait(lambda s: s.has("ll_gallery_entrance") or s.has("rv_gallery"))
            screen = self.observe()
        if screen.has("ll_gallery_entrance"):
            self.tap_id("ll_gallery_entrance", lambda s: s.has("rv_gallery"), "MEDIA_PICKER_OPEN")
        elif screen.has("rv_gallery"):
            self.checkpoint("MEDIA_PICKER_OPEN")
        else:
            raise RpaError("UNSUPPORTED_START_STATE_USE_BOUND_RESUME_EVIDENCE")
        self.last_action = dict(action="choose_video_tab", selector=dict(description="Vídeo"))
        self.d(description="Vídeo").click(timeout=10)
        self.wait(lambda s: any(n.get("content-desc") == "Vídeo" and n.get("selected") == "true" for n in s.nodes))
        output = self.media_inventory()
        if output.exit_code:
            raise RpaError("MEDIASTORE_QUERY_FAILED")
        rows = parse_media_inventory(output.output,preserve_query_order=self.config.get('media_sort_order')=='date_modified DESC')
        if not rows:
            raise RpaError("NO_VIDEO_MEDIA")
        candidates = rows
        for key, config_key in (("video_path", "video_path"), ("name", "video_name"), ("date_added", "video_date_added")):
            if self.config.get(config_key) is not None:
                candidates = [row for row in candidates if row[key] == self.config[config_key]]
        if not any(self.config.get(key) is not None for key in ("video_path", "video_name", "video_date_added")):
            raise RpaError("EXPLICIT_MEDIA_IDENTITY_REQUIRED")
        if len(candidates) != 1:
            raise RpaError("AMBIGUOUS_MEDIA_IDENTITY")
        media = candidates[0]
        if (sum(abs(row['duration_ms']-media['duration_ms']) <= 1100 for row in rows[:6]) != 1
                and not self.config.get('supervised_duration_collision_review',False)):
            raise RpaError('MEDIA_PICKER_AMBIGUOUS_REVIEW_REQUIRED')
        index = rows.index(media)
        if index >= 6:
            raise RpaError("MEDIA_OUTSIDE_OBSERVED_FIRST_SIX_MAPPING")
        durations = self.observe().ids("tv_duration")
        if len(durations) < min(6, len(rows)):
            raise RpaError("MEDIA_GRID_NOT_AT_TOP")
        for row, node in zip(rows[:6], durations[:6]):
            value = node.get("text", "")
            if not re.fullmatch(r"\d+:\d{2}", value):
                raise RpaError("MEDIA_DURATION_UNREADABLE")
            minutes, seconds = map(int, value.split(":"))
            if abs(minutes * 60 + seconds - row["duration_ms"] / 1000) > 1.1:
                raise RpaError("MEDIASTORE_GRID_ORDER_NOT_CORROBORATED")
        if any(n.get("selected") == "true" for n in self.observe().ids("check")):
            raise RpaError("UNKNOWN_PREEXISTING_MEDIA_SELECTION")
        media["video_sha256"] = self.get_device_video_hash(media["video_path"])
        if self.config.get("video_sha256") and self.config["video_sha256"] != media["video_sha256"]:
            raise RpaError("EXPECTED_MEDIA_HASH_MISMATCH")
        self.session["media"] = media
        self.checkpoint("MEDIA_FOUND", extra=dict(media=media))
        checks = self.observe().ids("ll_check")
        if index >= len(checks):
            raise RpaError("MEDIA_CELL_NOT_VISIBLE")
        selector = dict(resourceId=checks[index]["resource-id"], instance=index)
        self.safety.budget.consume(ActionType.MEDIA_SELECT)
        self.last_action = dict(action="select_video", selector=selector)
        self.d(**selector).click(timeout=10)
        self.wait(lambda s: bool(s.texts("1 Selecionado")) and sum(n.get("selected") == "true" for n in s.ids("check")) == 1
                  and any(n.get("text") == "1" and n.get("selected") == "true" for n in s.ids("check"))
                  and any(n.get("enabled") == "true" for n in s.ids("tv_pick_top_next")))
        self.checkpoint('MEDIA_SELECTED')
        # Selection is a review checkpoint BEFORE rendering/upload/editor side effects.
        self.session['selection_evidence'] = dict(serial=self.config['serial'], **media,
            expected_account=self.safety.expected.username, visual_preview_reviewed=False,
            inventory_snapshot=rows, selected_cell=dict(index=index,selector=selector,duration=durations[index].get('text')),
            files=[], identity_limitation='Picker exposes no filename; operator must review thumbnail and prepared preview')
        atomic_json(self.session_path,self.session)
        raise RpaError('MEDIA_SELECTION_REVIEW_REQUIRED')

    def adopt_selection(self, evidence_path):
        self.require_ui()
        evidence = json.loads(Path(evidence_path).read_text(encoding="utf-8"))
        for key in ("serial", "video_path", "video_sha256"):
            if evidence.get(key) != self.config.get(key):
                raise RpaError("RESUME_MEDIA_IDENTITY_MISMATCH")
        for ref in evidence["files"]:
            if sha256(ref["path"]) != ref["sha256"]:
                raise RpaError("RESUME_EVIDENCE_HASH_MISMATCH")
        from app.mobile.media_selection import selection_unambiguous
        if not selection_unambiguous(evidence,self.config['video_path'],self.config['video_sha256']):
            raise RpaError('MEDIA_SELECTION_EVIDENCE_INCOMPLETE')
        if evidence.get('candidate_fingerprint') != self.safety.candidate.fingerprint() or not evidence.get('reviewer') or not 0 <= time.time()-evidence.get('reviewed_at',0) <= self.safety.config.approval_ttl:
            raise RpaError('SELECTION_REVIEW_INVALID_OR_EXPIRED')
        if not evidence.get("visual_preview_reviewed"):
            raise RpaError("RESUME_PREVIEW_REVIEW_MISSING")
        if evidence.get("expected_account") != self.safety.expected.username:
            raise RpaError("RESUME_ACCOUNT_MISMATCH")
        self.session["selection_evidence"] = evidence
        self.session["media"] = {key: evidence[key] for key in ("video_path", "video_sha256")}
        # Proof adoption is not a claim that the native editor has been reached.
        atomic_json(self.session_path, self.session)

    def continue_selected_media(self):
        """Continue only a reviewed selection; never select/reselect on resume."""
        self.require_ui()
        evidence = self.session.get('selection_evidence')
        if not evidence or not evidence.get('visual_preview_reviewed'):
            raise RpaError('MEDIA_SELECTION_REVIEW_REQUIRED')
        from app.mobile.media_selection import selection_unambiguous
        if (not selection_unambiguous(evidence,self.config['video_path'],self.config['video_sha256'])
                or evidence.get('candidate_fingerprint') != self.safety.candidate.fingerprint()
                or not evidence.get('reviewer')
                or not 0 <= time.time()-evidence.get('reviewed_at',0) <= self.safety.config.approval_ttl
                or any(sha256(ref['path']) != ref['sha256'] for ref in evidence.get('files',[]))):
            raise RpaError('SELECTION_REVIEW_INVALID_OR_EXPIRED')
        screen = self.observe()
        selected_in_this_flow = False
        if screen.has('rv_gallery'):
            inventory = self.media_inventory()
            rows = parse_media_inventory(inventory.output,preserve_query_order=self.config.get('media_sort_order')=='date_modified DESC') if not inventory.exit_code else []
            index = evidence['selected_cell']['index']
            expected_rows = evidence['inventory_snapshot'][:6]
            keys = ('media_id', 'video_path', 'date_added', 'duration_ms', 'size')
            stable = len(rows[:6]) == len(expected_rows) and all(
                all(a.get(k) == b.get(k) for k in keys) for a, b in zip(rows[:6], expected_rows))
            def same_selection(current):
                selected = current.ids('check')
                durations = current.ids('tv_duration')
                labels = [n.get('text','') for n in durations[:len(expected_rows)]]
                grid_ok = len(labels) == len(expected_rows) and all(
                    re.fullmatch(r'\d+:\d{2}', label) and abs(
                        sum(int(v)*m for v,m in zip(label.split(':'),(60,1)))-row['duration_ms']/1000) <= 1.1
                    for label,row in zip(labels,expected_rows))
                return (current.has('rv_gallery') and grid_ok and 0 <= index < min(6,len(selected),len(durations))
                    and sum(n.get('selected') == 'true' for n in selected) == 1
                    and selected[index].get('selected') == 'true' and selected[index].get('text') == '1'
                    and durations[index].get('text') == evidence['selected_cell']['duration']
                    and bool(current.texts('1 Selecionado')))
            if not stable or not same_selection(screen):
                raise RpaError('MEDIA_SELECTION_CHANGED_REVIEW_REQUIRED')
            if self.get_device_video_hash(self.config['video_path']) != self.config['video_sha256']:
                raise RpaError('EXPECTED_MEDIA_HASH_MISMATCH')
            self.checkpoint('MEDIA_SELECTED')
            screen = self.tap_id('tv_pick_top_next', lambda s: s.has('edit_compose_view') and s.has('player_container') and s.has('tv_compress'), 'MEDIA_PREVIEW', precondition=same_selection)
            selected_in_this_flow = True
        if screen.has('edit_compose_view') and screen.has('player_container') and screen.has('tv_compress'):
            if (not selected_in_this_flow
                    and evidence.get('preview_screen_sha256') != self.safety._evidence_digest(screen.nodes)):
                raise RpaError('PREVIEW_CONTINUITY_REVIEW_REQUIRED')
            self.checkpoint('MEDIA_PREVIEW')
            screen = self.tap_id('tv_compress', lambda s: s.has('btn_post') and s.has('iv_video_preview') and s.has('et_caption'), 'EDITOR_READY')
        if not (screen.has('btn_post') and screen.has('iv_video_preview') and screen.has('et_caption')):
            raise RpaError('UNSUPPORTED_MEDIA_RESUME_STATE_REVIEW')
        if not evidence.get('preview_pixel_sha256'):
            self.checkpoint('EDITOR_MEDIA_REVIEW')
            raise RpaError('EDITOR_MEDIA_REVIEW_REQUIRED')
        if not self.media_matches():
            raise RpaError('MEDIA_SELECTION_REVIEW_REQUIRED')
        self.checkpoint('EDITOR_READY')

    def review_editor_preview(self, reviewed_screenshot, reviewer):
        """Bind the observed editor cover to an explicitly reviewed screenshot."""
        self.require_ui()
        from app.mobile.media_selection import selection_unambiguous
        from PIL import Image
        evidence=self.session.get('selection_evidence',{})
        if (self.session.get('state')!='EDITOR_MEDIA_REVIEW' or not reviewer or
                evidence.get('candidate_fingerprint')!=self.safety.candidate.fingerprint() or
                not selection_unambiguous(evidence,self.config['video_path'],self.config['video_sha256'])):
            raise RpaError('EDITOR_PREVIEW_REVIEW_TRACE_INVALID')
        screen=self.observe();nodes=screen.ids('iv_video_preview')
        if not screen.has('btn_post') or len(nodes)!=1 or screen.ids('tv_product_title'):
            raise RpaError('EDITOR_PREVIEW_REVIEW_SCREEN_CHANGED')
        bounds=tuple(map(int,re.findall(r'\d+',nodes[0]['bounds'])))
        image=self.d.screenshot().convert('RGB').crop(bounds)
        with Image.open(reviewed_screenshot) as reviewed:
            if image.tobytes()!=reviewed.convert('RGB').crop(bounds).tobytes():
                raise RpaError('EDITOR_PREVIEW_REVIEW_PIXELS_CHANGED')
        evidence.update(preview_pixel_sha256=hashlib.sha256(image.tobytes()).hexdigest(),
                        editor_preview_reviewer=reviewer,editor_preview_reviewed_at=time.time())
        evidence['files'].append(dict(path=str(reviewed_screenshot),sha256=sha256(reviewed_screenshot)))
        atomic_json(self.session_path,self.session)
        if not self.media_matches():raise RpaError('EDITOR_PREVIEW_REVIEW_MEDIA_CHANGED')
        self.checkpoint('EDITOR_READY')

    def media_matches(self):
        self.require_ui()
        evidence = self.session.get("selection_evidence")
        if not evidence or not evidence.get('visual_preview_reviewed'):
            return False
        from app.mobile.media_selection import selection_unambiguous
        if not selection_unambiguous(evidence,self.config['video_path'],self.config['video_sha256']):
            return False
        if evidence.get('candidate_fingerprint') != self.safety.candidate.fingerprint() or not evidence.get('reviewer') or not 0 <= time.time()-evidence.get('reviewed_at',0) <= self.safety.config.approval_ttl:
            return False
        for ref in evidence["files"]:
            if sha256(ref["path"]) != ref["sha256"]:
                return False
        media = self.session.get("media", self.config)
        try:
            if self.get_device_video_hash(media["video_path"]) != media.get("video_sha256"):
                return False
        except Exception:
            return False
        nodes = self.observe().ids("iv_video_preview")
        if len(nodes) != 1:
            return False
        bounds = tuple(map(int, re.findall(r"\d+", nodes[0]["bounds"])))
        crop = self.d.screenshot().convert("RGB").crop(bounds)
        return hashlib.sha256(crop.tobytes()).hexdigest() == evidence.get("preview_pixel_sha256")

    def reserve_attempt(self):
        raise RpaError('PUBLISH_GATE_AUTHORIZATION_REQUIRED')

    def begin_publication(self):
        """Dispatch once and retain PUBLISHING until explicit evidence arrives.

        Used by supervised operation through the same PublishGate; no retry or
        success inference. Closing without evidence must mark the attempt UNKNOWN.
        """
        if self.session.get('publish_attempted'):
            raise RpaError('PREVIOUS_PUBLISH_ATTEMPT_REQUIRES_RECONCILIATION')
        if not self.config.get('publish_authorized') or not self.config.get('authorization_source'):
            raise RpaError('PUBLICATION_NOT_AUTHORIZED')
        self.checkpoint('POST_VALIDATION')
        product_title=self.session.get('product_title',self.config.get('product_title'))
        screen=self.observe()
        checks=validation_checks(screen,self.expected_caption,product_title,self.media_matches(),self.sharing_disabled())
        self.session['validation']=checks
        if not all(checks.values()):
            raise RpaError('PRE_PUBLISH_VALIDATION_FAILED:' + ','.join(k for k,v in checks.items() if not v))
        self.require_ui()
        context=self.safety.context(screen,True)
        authorization=self.safety.gate.authorize(self.safety.job,self.safety.owner,self.safety.candidate,context)
        self.session['publish_attempted']=True
        self.session['central_job_id']=self.safety.job
        atomic_json(self.session_path,self.session)
        self.last_action=dict(action='publish_once')
        self.checkpoint('PUBLISHING')
        final_screen=self.observe()
        if not all(validation_checks(final_screen,self.expected_caption,product_title,self.media_matches(),self.sharing_disabled()).values()):
            raise RpaError('FINAL_SCREEN_CHANGED_ATTEMPT_RESERVED_NO_RETRY')
        context=self.safety.context(final_screen,True)
        self.d.final_click(dict(resourceId=final_screen.ids('btn_post')[0]['resource-id']),authorization,
                           self.safety.gate,self.safety.candidate,context)
        return dict(state='PUBLISHING',job_id=self.safety.job,publish_attempted=True)

    def publish(self, timeout=60):
        self.begin_publication()
        # UI toast/profile return cannot prove the exact asset, product and post ID.
        from app.publishing.reconciliation import PublicationReconciler
        PublicationReconciler(self.safety.ledger,self.safety.logger).reconcile(self.safety.job)
        self.safety.breaker.failure('PUBLICATION_UNKNOWN',critical=True,job_id=self.safety.job)
        raise RpaError('PUBLICATION_UNCONFIRMED_DO_NOT_REPOST')

    def run_prepared(self, evidence_path=None, publish=False):
        from app.mobile.safety_runtime import AndroidSafetyRuntime
        # Old attempted sessions stop locally, before connection or UI reads.
        if self.session.get('publish_attempted'):
            raise RpaError('PREVIOUS_PUBLISH_ATTEMPT_REQUIRES_RECONCILIATION')
        try:
            self.safety=AndroidSafetyRuntime(self.config,self.root)
            if publish and self.safety.config.mode != FeatureMode.LIVE_PUBLISH:
                raise RpaError('LIVE_PUBLISH_EXPLICIT_CONFIG_REQUIRED')
            result=self.safety.start(self.expected_caption,Screen,self.d)
            if result is not None:
                return result
            self.d=self.safety.ui
            with device_lock(self.config['serial'],self.logs/'locks'):
                self.observe()
                self.checkpoint('DEVICE_READY')
                if evidence_path:
                    self.adopt_selection(evidence_path)
                else:
                    self.select_media()
                self.continue_selected_media()
                self.select_product()
                self.fill_caption()
                self.ensure_shopee_only()
                screen=self.observe()
                media_ok = self.media_matches()
                checks=validation_checks(screen,self.expected_caption,self.config.get('product_title'),media_ok,self.sharing_disabled())
                if not all(checks.values()):
                    raise RpaError('PRE_PUBLISH_VALIDATION_FAILED')
                self.safety.context(screen,media_ok)
                self.session['central_job_id']=self.safety.job
                self.session['validation']=checks
                if self.safety.config.mode == FeatureMode.ASSISTED_MODE:
                    self.session['assisted_validation'] = self.safety.complete_assisted(screen, media_ok, checks)
                    self.session['ready_for_publish'] = False
                    self.checkpoint('ASSISTED_VALIDATED')
                    return self.session
                self.safety.ledger.transition(self.safety.job,self.safety.owner,'READY')
                self.session['ready_for_publish'] = True
                self.checkpoint('READY_FOR_PUBLISH')
                if publish:
                    return self.publish()
                return self.session
        except Exception as exc:
            reason=str(exc) if isinstance(exc,(RpaError,OperationalStop)) else type(exc).__name__
            if self.safety:
                self.safety.fail(reason)
            if reason not in ('JOB_ALREADY_RESERVED','ACCOUNT_OR_DEVICE_ALREADY_IN_USE'):
                review = ('REVIEW' in reason or 'AMBIGUOUS' in reason or reason.startswith('MEDIA_SELECTION_')) and not getattr(self.d,'pending_effect',False)
                self.checkpoint('REVIEW' if review else 'ERROR',error=reason)
            raise RpaError(reason) from exc
        finally:
            if self.safety:
                self.safety.close()


def connect(serial):
    os.environ["PATH"] = str(ADB_DIR) + os.pathsep + os.environ.get("PATH", "")
    output = subprocess.run([str(ADB_DIR / "adb.exe"), "devices"], check=True,
                            capture_output=True, text=True, timeout=15).stdout
    if not re.search(r"^" + re.escape(serial) + r"\s+device\s*$", output, re.MULTILINE):
        raise RpaError("DEVICE_NOT_READY")
    import uiautomator2 as u2
    return u2.connect(serial)


def publish_video(*, video_path=None, product_query, caption, hashtags, job_id,
                  serial="R9QYA0227VX", product_title=None, expected_account=None,
                  video_name=None, video_date_added=None, video_sha256=None,
                  publish_authorized=False, authorization_source=None,
                  resume_evidence=None, publish=False, root=Path("."), candidate=None, account=None,
                  operational=None, local_media_path=None, platform_authorization=None, product_binding_review=None,
                  product_card_review=None):
    """Publish from observed profile/camera/picker, or resume bound selection.

    Paths refer to Android MediaStore; this module does not transfer/edit media.
    Name/path/time select among the first six corroborated visible videos.
    SHA-256 verifies the chosen source; it is not a gallery-wide hash search.
    """
    config = dict(video_path=video_path, product_query=product_query, caption=caption,
                  hashtags=list(hashtags), job_id=job_id, serial=serial,
                  product_title=product_title, expected_account=expected_account,
                  video_name=video_name, video_date_added=video_date_added,
                  video_sha256=video_sha256, publish_authorized=publish_authorized,
                  authorization_source=authorization_source, candidate=candidate, account=account, operational=operational,
                  local_media_path=local_media_path, platform_authorization=platform_authorization, product_binding_review=product_binding_review,
                  product_card_review=product_card_review)
    worker = ShopeeVideoPublisher(None, config, root)
    return worker.run_prepared(resume_evidence, publish=publish)
