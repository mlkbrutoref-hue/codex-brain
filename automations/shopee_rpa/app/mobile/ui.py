"""Single action boundary. Real RPC runs in a terminable child process."""
from dataclasses import dataclass
import multiprocessing as mp
import hashlib
import json
import re
import time
import xml.etree.ElementTree as ET
from app.operational.config import ActionType, FeatureMode
from app.operational.deadlines import OperationalStop
from app.operational.modes import OperationModeEngine


def raw_product_add_selector(xml, path):
    """Resolve our raw XML path without the SDK's class-tag XPath conversion."""
    if not re.fullmatch(r'/hierarchy(?:/node\[\d+\])+',path):
        raise OperationalStop('UNAPPROVED_XPATH')
    root=ET.fromstring(xml)
    nodes=root.findall('.'+path[len('/'+root.tag):])
    if len(nodes)!=1 or nodes[0].get('text')!='Adicionar' or nodes[0].get('package')!='com.shopee.br' or nodes[0].get('enabled')!='true':
        raise OperationalStop('PRODUCT_CARD_CHANGED')
    target=nodes[0]
    matches=[n for n in root.iter('node') if n.get('text')=='Adicionar' and n.get('package')==target.get('package') and n.get('class')==target.get('class')]
    return dict(text='Adicionar',packageName=target.get('package'),className=target.get('class'),instance=matches.index(target))


def assert_product_screen(xml, expected_digest):
    from app.mobile.shopee_video import Screen
    screen = Screen(xml)
    screen.guard()
    digest = hashlib.sha256(json.dumps(screen.nodes,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    if digest != expected_digest:
        raise OperationalStop('PRODUCT_CARD_CHANGED_REVIEW')


def _device_process(pipe, serial):
    # Imported only in the explicit external-operation process, never by offline tests.
    from app.mobile.shopee_video import connect
    try:
        device = connect(serial)
        pipe.send(('OK', None))
        while True:
            operation, args = pipe.recv()
            if operation == 'close': break
            try:
                if operation in ('dump_hierarchy', 'app_current', 'app_info', 'screenshot', 'shell', 'press'):
                    value = getattr(device, operation)(*args)
                elif operation in ('click', 'set_text'):
                    selector, params = args
                    value = getattr(device(**selector), operation)(**params)
                elif operation == 'xpath_count':
                    root=ET.fromstring(device.dump_hierarchy())
                    value=len(root.findall('.'+args[0][len('/'+root.tag):]))
                elif operation == 'open_shopee' and args == ['com.shopee.br']:
                    value = device.app_start('com.shopee.br', stop=False)
                elif operation == 'xpath_click':
                    xml = device.dump_hierarchy()
                    if len(args) == 3:
                        assert_product_screen(xml, args[2])
                    selector=raw_product_add_selector(xml,args[0])
                    value=device(**selector).click(timeout=args[1])
                else:
                    raise ValueError('UNSUPPORTED_RPC')
                pipe.send(('OK', value))
            except Exception as exc:
                pipe.send(('ERROR', type(exc).__name__))
    except BaseException:
        try: pipe.send(('ERROR', 'DEVICE_PROCESS_FAILED'))
        except Exception: pass
    finally:
        pipe.close()


class IsolatedAndroidDevice:
    is_offline_fake = False

    def __init__(self, serial, deadline, rpc_seconds, *, process_target=None):
        self.serial = serial
        self.deadline, self.rpc_seconds = deadline, rpc_seconds
        context = mp.get_context('spawn')
        self.pipe, child = context.Pipe()
        self.is_offline_fake = process_target is not None
        self.process = context.Process(target=process_target or _device_process, args=(child, serial), daemon=True)
        self.process.start()
        child.close()
        try:
            self._receive()
        except BaseException:
            self.close()
            raise

    def _receive(self):
        if not self.pipe.poll(self.deadline.child_timeout(self.rpc_seconds)):
            self.close()
            raise OperationalStop('RPC_TIMEOUT')
        try:
            status, value = self.pipe.recv()
        except EOFError:
            self.close()
            raise OperationalStop('DEVICE_PROCESS_LOST') from None
        self.deadline.raise_if_expired()
        if status != 'OK':
            raise OperationalStop('DEVICE_RPC_FAILED')
        return value

    def invoke(self, operation, args):
        self.deadline.raise_if_expired()
        if not self.process.is_alive():
            raise OperationalStop('DEVICE_PROCESS_LOST')
        self.pipe.send((operation, args))
        return self._receive()

    def close(self):
        if self.process.is_alive():
            self.process.terminate()
            self.process.join(timeout=1)
            if self.process.is_alive():
                self.process.kill()
                self.process.join(timeout=1)
        self.pipe.close()


class UISelector:
    def __init__(self, ui, selector): self.ui, self.selector = ui, selector
    def click(self, timeout=10): return self.ui.click(self.selector, timeout)
    def set_text(self, text, timeout=10): return self.ui.set_text(self.selector, text, timeout)


class UIXPath:
    def __init__(self, ui, path): self.ui, self.path = ui, path
    def all(self): return [None] * self.ui._execute(ActionType.READ_STATE, 'xpath_count', [self.path], 'xpath')
    def click(self, timeout=10, expected_screen_sha256=None):
        xml = self.ui.dump_hierarchy()
        if expected_screen_sha256 is not None:
            assert_product_screen(xml, expected_screen_sha256)
        root = ET.fromstring(xml)
        path = '.' + self.path[len('/' + root.tag):]
        nodes = root.findall(path)
        if len(nodes) != 1 or nodes[0].get('text') != 'Adicionar' or nodes[0].get('package') != 'com.shopee.br':
            raise OperationalStop('PRODUCT_CARD_CHANGED')
        args = [self.path, self.ui.deadline.child_timeout(timeout)]
        if expected_screen_sha256 is not None:
            args.append(expected_screen_sha256)
        return self.ui._execute(ActionType.CLICK, 'xpath_click', args, 'product_card')


class ShopeeUI:
    # Maximum age in seconds for cached hierarchy XML before re-fetch.
    _SNAPSHOT_MAX_AGE = 0.5

    def __init__(self, device, config, deadline, budget, breaker, logger, modes=None, ledger=None, job=None, owner=None):
        self.device, self.config, self.deadline, self.budget, self.breaker, self.logger = device, config, deadline, budget, breaker, logger
        self.modes = modes or OperationModeEngine()
        self.ledger, self.job, self.owner = ledger, job, owner
        self.account_proven = False
        self._final_dispatch_ready = False
        self.pending_effect = False
        self._account_discovery_active = False
        # Hierarchy snapshot cache: avoids redundant XML dumps within a short
        # window (e.g. observe() followed immediately by _resolve_click()).
        self._cached_hierarchy = None
        self._cached_hierarchy_at = 0.0
        self._cached_screenshot = None
        self._cached_screenshot_at = 0.0
        self._cached_app_current = None
        self._cached_app_current_at = 0.0

    def __call__(self, **selector): return UISelector(self, selector)
    def xpath(self, path):
        # Helpers cannot hide final publishing behind a broad XPath.
        if not re.fullmatch(r'/hierarchy(?:/node\[\d+\])+', path):
            raise OperationalStop('UNAPPROVED_XPATH')
        return UIXPath(self, path)

    def _check_mode(self, action):
        """Apply the same live stop controls to RPCs and cached observations."""
        self.deadline.raise_if_expired()
        if self.config.mode == FeatureMode.DRY_RUN:
            raise OperationalStop('DRY_RUN_EXTERNAL_ACTION_BLOCKED')
        state = self.breaker.snapshot()['state']
        self.modes.evaluate(dict(circuit=state, kill_switch=self.breaker.store.killed(), deadline_expired=self.deadline.expired(),
                                budget_low=self.budget.remaining_tokens() < 20))
        if not self.modes.can_execute(action):
            raise OperationalStop('OPERATION_MODE_BLOCKED')

    def _check_cached_read(self):
        self._check_mode(ActionType.READ_STATE)
        self.breaker.check(read_only=True)
        self.deadline.raise_if_expired()

    def _execute(self, action, operation, args, element, *, final=False):
        allowed = {'dump_hierarchy':ActionType.READ_STATE,'app_current':ActionType.READ_STATE,
            'app_info':ActionType.READ_STATE,'screenshot':ActionType.READ_STATE,'shell':ActionType.READ_STATE,
            'xpath_count':ActionType.READ_STATE,'click':ActionType.PUBLISH_ATTEMPT if final else ActionType.CLICK,
            'set_text':ActionType.CLICK,'press':ActionType.NAVIGATION,'xpath_click':ActionType.CLICK,'open_shopee':ActionType.NAVIGATION}
        if allowed.get(operation) != action:
            raise OperationalStop('ACTION_TYPE_OPERATION_MISMATCH')
        if operation == 'open_shopee' and (args != ['com.shopee.br'] or self.config.mode != FeatureMode.ASSISTED_MODE or self.account_proven):
            raise OperationalStop('UNAPPROVED_BOOTSTRAP')
        if operation == 'press' and (len(args) != 1 or args[0] not in ('enter', 'back')):
            raise OperationalStop('UNAPPROVED_KEY')
        if action != ActionType.READ_STATE and self.pending_effect:
            raise OperationalStop('PREVIOUS_EFFECT_REQUIRES_VALIDATION')
        if operation == 'shell':
            command=args[0]
            if not isinstance(command,list) or not command or command[0] not in ('content','sha256sum') or (command[0]=='content' and command[1:2]!=['query']):
                raise OperationalStop('SHELL_MUTATION_BLOCKED')
        if operation == 'xpath_click':
            path=args[0]
            if not re.fullmatch(r'/hierarchy(?:/node\[\d+\])+',path):
                raise OperationalStop('UNAPPROVED_XPATH')
            root=ET.fromstring(self.dump_hierarchy())
            nodes=root.findall('.'+path[len('/'+root.tag):])
            if len(nodes)!=1 or nodes[0].get('text')!='Adicionar' or nodes[0].get('package')!='com.shopee.br':
                raise OperationalStop('PRODUCT_CARD_CHANGED')
        if action == ActionType.PUBLISH_ATTEMPT or final:
            if not final or not self._final_dispatch_ready:
                raise OperationalStop('PUBLISH_AUTHORIZATION_REQUIRED')
            if self.config.mode != FeatureMode.LIVE_PUBLISH:
                raise OperationalStop('LIVE_PUBLISH_EXPLICIT_CONFIG_REQUIRED')
            self._final_dispatch_ready = False
        if operation == 'click' and not final:
            # Keep the low-level dispatcher guarded too; private helpers cannot bypass click().
            selector = args[0]
            reviewed_target = self._resolve_click(selector)
        self._check_mode(action)
        discovery = (self._account_discovery_active and self.config.mode == FeatureMode.ASSISTED_MODE and
            operation == 'click' and action == ActionType.CLICK and self._resolve_click(args[0]).get('text') in ('Mim','Eu'))
        bootstrap = (operation == 'open_shopee' and args == ['com.shopee.br'] and
            self.config.mode == FeatureMode.ASSISTED_MODE and not self.account_proven and action == ActionType.NAVIGATION)
        if action != ActionType.READ_STATE and not self.account_proven and not discovery and not bootstrap:
            raise OperationalStop('ACCOUNT_PREFLIGHT_REQUIRED')
        self.breaker.check(read_only=action == ActionType.READ_STATE)
        if action != ActionType.READ_STATE:
            from app.mobile.shopee_video import Screen
            screen = Screen(self.dump_hierarchy(force=True))
            try:
                screen.guard()
            except Exception:
                self.breaker.failure('HUMAN_ACCOUNT_VERIFICATION_REQUIRED', critical=True)
                raise
            if operation == 'click' and not final:
                # The fresh guard must validate the actual target, not just the
                # screen. Cached selectors may now resolve to another button.
                current_target = self._resolve_click(args[0], root=screen.root)
                identity = ('package', 'resource-id', 'class', 'text', 'content-desc', 'enabled')
                if any(current_target.get(key) != reviewed_target.get(key) for key in identity):
                    raise OperationalStop('CLICK_TARGET_CHANGED_REVIEW')
            if operation == 'xpath_click' and len(args) == 3:
                assert_product_screen(ET.tostring(screen.root, encoding='unicode'), args[2])
            if self.app_current().get('package') != 'com.shopee.br' and not bootstrap:
                raise OperationalStop('UNEXPECTED_FOREGROUND_APP')
            # Enter is only a search submission; it cannot activate a focused Post button.
            if operation == 'press' and args[0] == 'enter':
                searches = [n for n in screen.nodes if n.get('class') == 'android.widget.EditText']
                if len(searches) != 1 or not screen.texts('Minhas Curtidas') or screen.has('btn_post'):
                    raise OperationalStop('ENTER_REQUIRES_PRODUCT_SEARCH_CONTEXT')
        cost = 0 if final else self.budget.consume(action)
        # Recheck after persistent IO, immediately before RPC.
        self.deadline.raise_if_expired()
        self.breaker.check(read_only=action == ActionType.READ_STATE)
        start = time.monotonic()
        if action != ActionType.READ_STATE:
            self.pending_effect = True
            self._invalidate_cache()
        try:
            value = self.device.invoke(operation, args)
            self.deadline.raise_if_expired()
        except Exception:
            status = 'ERROR' if action == ActionType.READ_STATE else 'UNKNOWN'
            if status == 'UNKNOWN':
                self.modes.on_unknown_result()
                if self.ledger and self.job:
                    self.ledger.mark_unknown(self.job, self.owner, 'RPC_EFFECT_UNKNOWN')
                self.breaker.failure('RPC_EFFECT_UNKNOWN', critical=True, job_id=self.job)
            else:
                self.modes.on_failure('RPC_ERROR')
                self.breaker.failure('RPC_ERROR')
            self.logger.log_action(operation_mode=self.modes.mode.value, action_type=action.value,
                element=element, token_cost=cost, latency_ms=(time.monotonic() - start) * 1000, status=status)
            raise
        self.logger.log_action(operation_mode=self.modes.mode.value, action_type=action.value,
            element=element, token_cost=cost, latency_ms=(time.monotonic() - start) * 1000, status='SUCCESS')
        self.modes.on_success()
        self.breaker.success()
        return value

    def _invalidate_cache(self):
        """Discard cached hierarchy, screenshot and foreground package after any state-mutating action."""
        self._cached_hierarchy = None
        self._cached_hierarchy_at = 0.0
        self._cached_screenshot = None
        self._cached_screenshot_at = 0.0
        self._cached_app_current = None
        self._cached_app_current_at = 0.0

    def dump_hierarchy(self, force=False):
        now = time.monotonic()
        if (not force
                and self._cached_hierarchy is not None
                and not self.pending_effect
                and now - self._cached_hierarchy_at < self._SNAPSHOT_MAX_AGE):
            self._check_cached_read()
            if time.monotonic() - self._cached_hierarchy_at < self._SNAPSHOT_MAX_AGE:
                return self._cached_hierarchy
        xml = self._execute(ActionType.READ_STATE, 'dump_hierarchy', [], 'hierarchy')
        self._cached_hierarchy = xml
        self._cached_hierarchy_at = time.monotonic()
        return xml
    def app_current(self, *, force=False):
        now = time.monotonic()
        if (not force
                and self._cached_app_current is not None
                and not self.pending_effect
                and now - self._cached_app_current_at < self._SNAPSHOT_MAX_AGE):
            self._check_cached_read()
            if time.monotonic() - self._cached_app_current_at < self._SNAPSHOT_MAX_AGE:
                return self._cached_app_current
        pkg = self._execute(ActionType.READ_STATE, 'app_current', [], 'foreground')
        self._cached_app_current = pkg
        self._cached_app_current_at = time.monotonic()
        return pkg
    def app_info(self, package): return self._execute(ActionType.READ_STATE, 'app_info', [package], 'app_version')
    def screenshot(self, path=None, *, force=False):
        now = time.monotonic()
        use_cache = (not force and self._cached_screenshot is not None
                and not self.pending_effect
                and now - self._cached_screenshot_at < self._SNAPSHOT_MAX_AGE)
        if use_cache:
            self._check_cached_read()
            use_cache = time.monotonic() - self._cached_screenshot_at < self._SNAPSHOT_MAX_AGE
        if use_cache:
            image = self._cached_screenshot
        else:
            image = self._execute(ActionType.READ_STATE, 'screenshot', [], 'screenshot')
            self._cached_screenshot = image
            self._cached_screenshot_at = time.monotonic()
        if path is not None: image.save(path)
        return image

    def shell(self, command):
        if not isinstance(command, list) or not command or command[0] not in ('content', 'sha256sum'):
            raise OperationalStop('SHELL_MUTATION_BLOCKED')
        if command[0] == 'content' and (len(command) < 2 or command[1] != 'query'):
            raise OperationalStop('SHELL_MUTATION_BLOCKED')
        return self._execute(ActionType.READ_STATE, 'shell', [command], 'read_shell')

    def click(self, selector, timeout=10):
        if any('btn_post' in str(v) or str(v).casefold() in ('postar', 'publicar') for v in selector.values()):
            raise OperationalStop('PUBLISH_AUTHORIZATION_REQUIRED')
        self._resolve_click(selector)
        return self._execute(ActionType.CLICK, 'click', [selector, dict(timeout=self.deadline.child_timeout(timeout))], 'selector')

    def _resolve_click(self, selector, *, root=None):
        if root is None:
            root = ET.fromstring(self.dump_hierarchy())
        mappings = {'resourceId':'resource-id','description':'content-desc','text':'text','className':'class','packageName':'package'}
        if not selector or set(selector) - set(mappings) - {'instance'}:
            raise OperationalStop('UNAPPROVED_SELECTOR')
        nodes = [n for n in root.iter('node') if all(n.get(mappings[k]) == v for k,v in selector.items() if k != 'instance')]
        if 'instance' in selector:
            index = selector['instance']
            nodes = nodes[index:index+1] if isinstance(index,int) and index >= 0 else []
        if len(nodes) != 1 or not nodes[0].get('package','').startswith('com.shopee.br'):
            raise OperationalStop('MISSING_OR_AMBIGUOUS_SELECTOR')
        if nodes[0].get('resource-id','').endswith('/btn_post') or nodes[0].get('text','').casefold() in ('postar','publicar'):
            raise OperationalStop('PUBLISH_AUTHORIZATION_REQUIRED')
        return nodes[0]

    def set_text(self, selector, text, timeout=10):
        return self._execute(ActionType.CLICK, 'set_text', [selector, dict(text=text, timeout=self.deadline.child_timeout(timeout))], 'text_field')

    def press(self, key):
        if key not in ('enter', 'back'):
            raise OperationalStop('UNAPPROVED_KEY')
        return self._execute(ActionType.NAVIGATION, 'press', [key], 'key')

    def navigate_account_profile(self):
        """Only the observed Mim/Eu account tab may precede identity confirmation."""
        if self.config.mode != FeatureMode.ASSISTED_MODE or self.account_proven:
            raise OperationalStop('ACCOUNT_DISCOVERY_NOT_APPLICABLE')
        from app.mobile.shopee_video import Screen
        screen=Screen(self.dump_hierarchy());screen.guard()
        labels=[label for label in ('Mim','Eu') if screen.texts(label)]
        if len(labels)!=1 or (labels[0]=='Eu' and not screen.has('home_view')):
            raise OperationalStop('ACCOUNT_PROFILE_TAB_NOT_PROVEN')
        selector = dict(text=labels[0], packageName='com.shopee.br')
        node = self._resolve_click(selector)
        if node.get('enabled') != 'true':
            raise OperationalStop('ACCOUNT_PROFILE_TAB_NOT_ACTIONABLE')
        self._account_discovery_active = True
        try:
            return self.click(selector)
        finally:
            self._account_discovery_active = False

    def open_shopee_for_account_check(self):
        """One package-specific bootstrap; all subsequent actions require identity."""
        if self.config.mode != FeatureMode.ASSISTED_MODE or self.account_proven:
            raise OperationalStop('ACCOUNT_DISCOVERY_NOT_APPLICABLE')
        self._execute(ActionType.NAVIGATION,'open_shopee',['com.shopee.br'],'shopee_bootstrap')
        end=time.monotonic()+self.deadline.child_timeout(20)
        while self.app_current().get('package') != 'com.shopee.br':
            if time.monotonic() >= end:
                raise OperationalStop('UNEXPECTED_FOREGROUND_APP')
            self.deadline.wait(.25)
        self.pending_effect=False

    def final_click(self, selector, authorization, gate, candidate, context):
        if self.config.mode != FeatureMode.LIVE_PUBLISH:
            raise OperationalStop('LIVE_PUBLISH_EXPLICIT_CONFIG_REQUIRED')
        if getattr(self.device, 'is_offline_fake', True):
            raise OperationalStop('LIVE_PUBLISH_FORBIDDEN_ON_FAKE')
        if not str(selector.get('resourceId', '')).endswith('/btn_post'):
            raise OperationalStop('FINAL_SELECTOR_NOT_PROVEN')
        gate.consume(authorization, self.owner, candidate, context)
        self.logger.log_publish_attempt(status='RESERVED')
        self._final_dispatch_ready = True
        try:
            return self._execute(ActionType.PUBLISH_ATTEMPT, 'click', [selector, dict(timeout=self.deadline.child_timeout(5))], 'btn_post', final=True)
        finally:
            self._final_dispatch_ready = False


def confirm_account(screen, expected):
    if not expected.account_id or not expected.username or not expected.stable_profile_marker:
        raise OperationalStop('ACCOUNT_CONFIG_REQUIRED')
    labels = {n.get('text', '') for n in screen.nodes} | {n.get('content-desc', '') for n in screen.nodes}
    if (not ({expected.username, 'Nome de usuário: '+expected.username} & labels)
            or expected.stable_profile_marker not in labels):
        raise OperationalStop('ACCOUNT_MISMATCH')
    return expected.account_id
