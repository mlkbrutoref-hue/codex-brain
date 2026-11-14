"""Integration of the existing Android worker with local operational contracts."""
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import re
import time
import uuid

from app.operational.config import OperationalConfig, FeatureMode, ActionType
from app.operational.store import OperationalStore
from app.operational.deadlines import ExecutionDeadline, OperationalStop
from app.operational.action_budget import ActionBudget, AccountBudget
from app.operational.circuit_breaker import OperationCircuitBreaker
from app.operational.modes import OperationModeEngine
from app.observability.operation_logger import OperationLogger
from app.publishing.ledger import JobLedger
from app.validation.product_media_truth import PostCandidate, ExpectedAccount, ContentValidator, ProductIdentity
from app.validation.publish_gate import PublishGate
from app.media.identity import file_sha256
from app.media.normalization import MediaProcessor
from app.mobile.ui import ShopeeUI, IsolatedAndroidDevice, confirm_account


class AndroidSafetyRuntime:
    def __init__(self, config, root, *, store=None):
        self.input, self.root = config, Path(root)
        self.config = OperationalConfig.from_dict(config.get('operational'))
        try:
            self.candidate = PostCandidate.from_dict(config['candidate'])
            self.expected = ExpectedAccount(**config['account'])
        except (KeyError, TypeError, ValueError):
            raise OperationalStop('MIGRATION_REQUIRED_CANDIDATE_AND_ACCOUNT') from None
        c = self.candidate
        if self.expected.account_id != c.account_id or not re.fullmatch(r'[A-Za-z0-9_.@-]{1,100}', c.account_id):
            raise OperationalStop('ACCOUNT_CONFIG_MISMATCH')
        self.owner = uuid.uuid4().hex
        self.deadline = ExecutionDeadline(self.config.session_seconds)
        self.store = store or OperationalStore(timeout=min(2, self.config.rpc_seconds))
        self.breaker = OperationCircuitBreaker(self.store,c.account_id,self.config)
        self.account_budget = AccountBudget(self.store,c.account_id,config['job_id'],config.get('worker_id',config['serial']),self.config)
        self.budget = ActionBudget(self.store,self.account_budget,self.breaker,self.config)
        self.ledger = JobLedger(self.store,self.config)
        self.validator = ContentValidator(self.config)
        self.modes = OperationModeEngine()
        self.logger = OperationLogger(self.root/'logs/operational'/f'{config["job_id"]}.jsonl',
            session_id=config['job_id'],job_id=config['job_id'],account_id=c.account_id)
        self.gate = PublishGate(self.ledger,self.validator,self.budget,self.breaker,self.deadline,self.modes,self.config)
        self.job = None
        self.ui = None
        self._selected_card_binding = None
        self._pending_card_binding = None

    def local_preflight(self, caption):
        c = self.candidate
        from app.mobile.shopee_video import compose_caption
        if compose_caption(c.caption,c.hashtags) != caption or self.input.get('video_sha256') != c.media.prepared_asset_hash or self.input.get('product_title') != c.product_title:
            raise OperationalStop('CANDIDATE_WORKER_INPUT_MISMATCH')
        duplicate = False
        with self.store.transaction() as db:
            exclude = self.job
            if exclude is None:
                identity = self.ledger.identity(c)
                old = self.ledger.get(identity,db)
                if old and not old['attempted'] and old['state'] in ('ASSISTED_VALIDATED','FAILED','CANCELLED','PREPARATION_ABANDONED'):
                    exclude = identity
            duplicate = self.ledger.duplicate(c, db, exclude=exclude)
        scope = self.input.get('validation_scope')
        assisted = self.config.mode == FeatureMode.ASSISTED_MODE or (self.config.mode == FeatureMode.DRY_RUN and scope == 'ASSISTED_UI_VALIDATION')
        report = self.validator.validate_assisted(c, duplicate=duplicate) if assisted else self.validator.validate(c, duplicate=duplicate)
        for check,status in report.checks.items():
            self.logger.log_validation(check=check,status=status)
        if report.status != 'PASS':
            raise OperationalStop('CONTENT_GATE_' + report.status.value + ':' + ','.join(report.reasons))
        source = self.input.get('local_media_path')
        if not source or file_sha256(source) != c.media.prepared_asset_hash:
            raise OperationalStop('LOCAL_MEDIA_HASH_MISMATCH')
        MediaProcessor(deadline=self.deadline).inspect(source,self.config.media_profile)
        self.deadline.raise_if_expired()
        return report

    def platform_authorized(self):
        value = self.input.get('platform_authorization',{})
        return bool(value.get('reference') and value.get('scope') == 'shopee_video_android_interaction' and
                    isinstance(value.get('expires_at'),(int,float)) and value['expires_at'] > time.time())

    def start(self, caption, screen_factory, device=None):
        report = self.local_preflight(caption)
        if self.config.mode == FeatureMode.DRY_RUN:
            return dict(state='DRY_RUN',validation_scope='ASSISTED_UI_VALIDATION' if self.input.get('validation_scope') == 'ASSISTED_UI_VALIDATION' else 'PUBLICATION',validation=asdict(report),external_actions=0,ready_for_publish=False)
        if not (self.platform_authorized() or self.validator.operator_listing_approval(self.candidate)):
            raise OperationalStop('PLATFORM_AUTHORIZATION_REQUIRED')
        if not self.config.allowed_app_versions:
            raise OperationalStop('APP_VERSION_ALLOWLIST_REQUIRED')
        self.breaker.check()
        self.ledger.import_legacy(self.root,self.candidate.account_id)
        canonical = Path(__file__).resolve().parents[2]
        if canonical != self.root.resolve():
            self.ledger.import_legacy(canonical,self.candidate.account_id)
        # Central reserve precedes connection/navigation/selection. Old sessions remain intact.
        self.job = self.ledger.reserve_job(self.candidate,self.owner,self.input['serial'])
        self.ledger.transition(self.job,self.owner,'PREPARING')
        bounded_reuse = (device is not None and not getattr(device,'is_offline_fake',False)
            and self.config.mode == FeatureMode.ASSISTED_MODE and isinstance(device,IsolatedAndroidDevice)
            and device.deadline is self.deadline and device.serial == self.input['serial'])
        if device is not None and not getattr(device,'is_offline_fake',False) and not bounded_reuse:
            raise OperationalStop('UNBOUNDED_DEVICE_INJECTION_FORBIDDEN')
        device = device or IsolatedAndroidDevice(self.input['serial'],self.deadline,self.config.rpc_seconds)
        self.ui = ShopeeUI(device,self.config,self.deadline,self.budget,self.breaker,self.logger,self.modes,self.ledger,self.job,self.owner)
        if self.config.mode == FeatureMode.ASSISTED_MODE and self.ui.app_current().get('package') != 'com.shopee.br':
            self.ui.open_shopee_for_account_check()
        screen = screen_factory(self.ui.dump_hierarchy())
        screen.guard()
        try:
            confirm_account(screen,self.expected)
        except OperationalStop:
            # Account discovery is bounded to the observed Mim tab. No picker,
            # caption, product or editor mutation is possible before identity.
            if self.config.mode == FeatureMode.ASSISTED_MODE and (screen.texts('Mim') or screen.texts('Eu')) and not screen.texts(self.expected.username):
                self.check_app()
                self.ui.navigate_account_profile()
                end = time.monotonic() + self.deadline.child_timeout(20)
                while True:
                    screen = screen_factory(self.ui.dump_hierarchy()); screen.guard()
                    if screen.texts(self.expected.username):
                        self.ui.pending_effect = False
                        confirm_account(screen, self.expected)
                        break
                    if time.monotonic() >= end:
                        raise OperationalStop('ACCOUNT_IDENTITY_NOT_PROVEN')
                    self.deadline.wait(.25)
            else:
                self._confirm_reviewed_account(screen)
        self.ui.account_proven = True
        self.check_app()
        return None

    def _confirm_reviewed_account(self, screen):
        proof=self.input.get('account_preflight_review',{})
        digest=hashlib.sha256(json.dumps(screen.nodes,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
        valid=proof.get('status')=='APPROVED' and proof.get('account_id')==self.expected.account_id and proof.get('username')==self.expected.username
        valid=valid and proof.get('reviewer') and proof.get('evidence_reference') and proof.get('screen_sha256')==digest
        valid=valid and 0 <= time.time()-proof.get('timestamp',0) <= self.config.approval_ttl
        if not valid:
            raise OperationalStop('ACCOUNT_IDENTITY_NOT_PROVEN') from None

    def check_app(self):
        current = self.ui.app_current()
        if current.get('package') != 'com.shopee.br':
            raise OperationalStop('UNEXPECTED_FOREGROUND_APP')
        info = self.ui.app_info('com.shopee.br')
        if str(info.get('versionName','')) not in self.config.allowed_app_versions:
            raise OperationalStop('APP_VERSION_CHANGED_REVIEW_REQUIRED')

    # Attributes that change on UI reflow without semantic identity change.
    _TRANSIENT_ATTRS = frozenset({'bounds','index','focused','selected','drawing-order','display-id'})

    @staticmethod
    def _evidence_digest(value):
        return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False).encode()).hexdigest()

    @classmethod
    def _semantic_node_filter(cls, attrib):
        """Strip layout-transient attributes so reflow does not invalidate identity."""
        return {k: v for k, v in attrib.items() if k not in cls._TRANSIENT_ATTRS}

    @classmethod
    def _semantic_digest(cls, value):
        """Digest that ignores transient layout attributes (bounds, index, focus state)."""
        if isinstance(value, dict):
            return cls._evidence_digest(cls._semantic_node_filter(value))
        if isinstance(value, list):
            return cls._evidence_digest([cls._semantic_node_filter(n) if isinstance(n, dict) else n for n in value])
        return cls._evidence_digest(value)

    def product_card_evidence(self, screen, card):
        """Reuse the existing review contract for an exact, observed native card."""
        expected = self.candidate.product
        if card.title != self.candidate.product_title:
            raise OperationalStop('PRODUCT_CARD_MISMATCH_REVIEW')
        if (card.shop_id,card.item_id) == (expected.shop_id,expected.item_id) and not expected.variant_id and not expected.attributes:
            return None
        if card.shop_id is not None or card.item_id is not None:
            if (card.shop_id,card.item_id) != (expected.shop_id,expected.item_id):
                raise OperationalStop('PRODUCT_CARD_IDS_MISMATCH_REVIEW')
        # A title/hidden-ID attestation is restricted to UI validation.
        operator_live=self.config.mode==FeatureMode.LIVE_PUBLISH and bool(self.validator.operator_listing_approval(self.candidate))
        if self.config.mode != FeatureMode.ASSISTED_MODE and not operator_live:
            raise OperationalStop('PRODUCT_CARD_IDS_OR_VARIANT_REVIEW_REQUIRED')
        proof_path = self.input.get('product_card_review')
        try:
            raw = Path(proof_path).read_bytes()
            proof = json.loads(raw)
            observed = ProductIdentity(**proof['product'])
            screenshot_hash = file_sha256(proof['screenshot_reference'])
            button = screen.root.findall('.'+card.button_xpath[len('/hierarchy'):])
        except (OSError,KeyError,TypeError,ValueError):
            raise OperationalStop('PRODUCT_CARD_REVIEW_REQUIRED') from None
        timestamp = proof.get('reviewed_at',0)
        expected_status='APPROVED_OPERATOR_PUBLICATION' if operator_live else 'APPROVED_UI_ONLY'
        valid = (proof.get('status') == expected_status and observed == expected
            and proof.get('reviewer') and proof.get('candidate_fingerprint') == self.candidate.fingerprint()
            and proof.get('official_source_url') == f'https://shopee.com.br/product/{expected.shop_id}/{expected.item_id}'
            and proof.get('card') == asdict(card) and proof.get('title_exact') is True
            and len(button) == 1 and proof.get('button_node_sha256') in (self._evidence_digest(button[0].attrib), self._semantic_digest(button[0].attrib))
            and proof.get('screen_sha256') in (self._evidence_digest(screen.nodes), self._semantic_digest(screen.nodes))
            and screenshot_hash == proof.get('screenshot_sha256')
            and isinstance(timestamp,(int,float)) and 0 <= time.time()-timestamp <= self.config.approval_ttl)
        validation=self.validator.validate(self.candidate) if operator_live else self.validator.validate_assisted(self.candidate)
        if not valid or validation.status != 'PASS':
            raise OperationalStop('PRODUCT_CARD_REVIEW_INVALID_OR_EXPIRED')
        evidence = dict(validation_scope='OPERATOR_ACCEPTED_PUBLICATION' if operator_live else 'ASSISTED_UI_VALIDATION', product=asdict(expected),
            candidate_fingerprint=self.candidate.fingerprint(), reviewer=proof['reviewer'], timestamp=timestamp,
            source_url=proof['official_source_url'], evidence_reference=str(Path(proof_path).resolve()),
            evidence_sha256=hashlib.sha256(raw).hexdigest(), card=asdict(card),
            card_screen_sha256=proof['screen_sha256'], screenshot_sha256=screenshot_hash)
        self._pending_card_binding = evidence
        return evidence

    def bind_selected_card(self, screen, evidence):
        # Called only after Add -> product information sheet -> Feito -> editor.
        nodes = screen.ids('tv_product_title')
        if evidence is None:
            return
        allowed=self.config.mode==FeatureMode.ASSISTED_MODE or (self.config.mode==FeatureMode.LIVE_PUBLISH and self.validator.operator_listing_approval(self.candidate))
        if (evidence != self._pending_card_binding or not allowed or not screen.has('btn_post')
                or len(nodes) != 1 or nodes[0].get('text') != self.candidate.product_title):
            raise OperationalStop('PRODUCT_LINK_NOT_CONFIRMED')
        self._selected_card_binding = dict(evidence, linked_node_sha256=self._linked_product_digest(nodes))
        self._pending_card_binding = None

    @classmethod
    def _linked_product_digest(cls, nodes):
        # Caption entry may reflow the same linked product. Identity must retain
        # text/package/resource/class semantics without treating layout as identity.
        return cls._semantic_digest(nodes)

    def product_evidence(self, screen):
        # Prefer an actual URL exposed by the observed screen; never derive IDs from a title.
        labels=' '.join(n.get('text','')+' '+n.get('content-desc','') for n in screen.nodes)
        identities=set(re.findall(r'shopee\.com\.br/product/(\d+)/(\d+)',labels))
        expected=self.candidate.product
        if identities == {(expected.shop_id,expected.item_id)} and not expected.variant_id and not expected.attributes:
            return expected
        binding = self._selected_card_binding
        if binding is not None and (self.config.mode == FeatureMode.ASSISTED_MODE or self.validator.operator_listing_approval(self.candidate)):
            nodes = screen.ids('tv_product_title')
            valid = (binding['candidate_fingerprint'] == self.candidate.fingerprint()
                and binding['product'] == asdict(expected) and len(nodes) == 1
                and nodes[0].get('text') == self.candidate.product_title
                and binding['linked_node_sha256'] == self._linked_product_digest(nodes)
                and 0 <= time.time()-binding['timestamp'] <= self.config.approval_ttl
                and file_sha256(binding['evidence_reference']) == binding['evidence_sha256'])
            if not valid:
                raise OperationalStop('PRODUCT_BINDING_REVIEW_INVALID')
            return expected
        # Native editor may hide IDs: an explicit operator attestation binds CURRENT linked node
        # to exact IDs/variant and an official product URL. Missing/stale/changed proof stops.
        proof=self.input.get('product_binding_review',{})
        nodes=screen.ids('tv_product_title')
        digest=self._semantic_digest(nodes)
        url=f'https://shopee.com.br/product/{expected.shop_id}/{expected.item_id}'
        try:
            observed=ProductIdentity(**proof['product'])
        except (KeyError,TypeError):
            raise OperationalStop('PRODUCT_IDS_NOT_OBSERVABLE_REVIEW_REQUIRED') from None
        valid=observed == expected and len(nodes)==1 and nodes[0].get('text')==self.candidate.product_title
        valid=valid and proof.get('status')=='APPROVED' and proof.get('reviewer') and proof.get('evidence_reference') and proof.get('source_url')==url
        valid=valid and proof.get('candidate_fingerprint')==self.candidate.fingerprint() and proof.get('linked_node_sha256') in (digest, hashlib.sha256(json.dumps(nodes,sort_keys=True,ensure_ascii=False).encode()).hexdigest())
        valid=valid and 0 <= time.time()-proof.get('timestamp',0) <= self.config.approval_ttl
        if not valid:
            raise OperationalStop('PRODUCT_BINDING_REVIEW_INVALID')
        return observed

    def context(self, screen, media_matches):
        self.check_app()
        return dict(platform_authorized=self.platform_authorized(),account_id=self.expected.account_id,
            operator_authorized=bool(self.validator.operator_listing_approval(self.candidate)),
            account_current=bool(self.ui.account_proven),app_expected=True,screen_expected=screen.has('btn_post') and not self.ui.pending_effect,
            media_selected=bool(media_matches),product=self.product_evidence(screen))

    def complete_assisted(self, screen, media_matches, validation):
        if self.config.mode != FeatureMode.ASSISTED_MODE:
            raise OperationalStop('ASSISTED_MODE_REQUIRED')
        if not media_matches:
            raise OperationalStop('MEDIA_IDENTITY_NOT_PROVEN')
        context = self.context(screen, media_matches)
        if (not all(context.get(key) is True for key in ('platform_authorized','account_current','app_expected','screen_expected','media_selected'))
                or context.get('account_id') != self.candidate.account_id or context.get('product') != self.candidate.product):
            raise OperationalStop('ASSISTED_CONTEXT_NOT_PROVEN')
        from app.mobile.shopee_video import compose_caption, validation_checks
        current = validation_checks(screen, compose_caption(self.candidate.caption,self.candidate.hashtags),
            self.candidate.product_title, media_matches, validation.get('automatic_sharing_disabled') is True)
        report = self.validator.validate_assisted(self.candidate)
        if report.status != 'PASS' or validation != current or not all(current.values()):
            raise OperationalStop('ASSISTED_VALIDATION_INCOMPLETE')
        evidence = dict(validation_scope='ASSISTED_UI_VALIDATION', candidate_fingerprint=self.candidate.fingerprint(),
            rights=self.candidate.provenance.rights_status.value, provenance=self.candidate.provenance.source_category,
            ready_for_publish=False, final_button_clicked=False, validation=validation)
        if self._selected_card_binding is not None:
            evidence['product_binding'] = dict(self._selected_card_binding)
        self.ledger.transition(self.job, self.owner, 'ASSISTED_VALIDATED', evidence)
        return evidence

    def fail(self, reason):
        reason=str(reason).split(':',1)[0]
        if self.job:
            row=self.ledger.get(self.job)
            if row['attempted'] or row['state'] in ('UPLOADING','PUBLISHING','UNKNOWN') or (self.ui and self.ui.pending_effect):
                self.ledger.mark_unknown(self.job,self.owner,reason)
                self.breaker.failure('PUBLICATION_UNKNOWN',critical=True,job_id=self.job)
            elif row['state'] in ('RESERVED','PREPARING','READY'):
                self.ledger.transition(self.job,self.owner,'FAILED',dict(reason=reason))
        critical=reason in ('ACCOUNT_MISMATCH','ACCOUNT_IDENTITY_NOT_PROVEN','PRODUCT_BINDING_REVIEW_INVALID','MEDIA_HASH_MISMATCH','HUMAN_ACCOUNT_VERIFICATION_REQUIRED') or ('MISMATCH' in reason and any(name in reason for name in ('ACCOUNT','PRODUCT','MEDIA')))
        self.breaker.failure(reason,critical=critical)
        self.logger.log_error(error_code=reason,status='ERROR')

    def close(self):
        if self.ui and hasattr(self.ui.device,'close'):
            self.ui.device.close()
