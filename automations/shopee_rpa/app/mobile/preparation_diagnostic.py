"""Incident-bound, read-only inspection while the ordinary breaker stays OPEN."""
from contextlib import contextmanager
import hashlib
import json
import time
import uuid

from app.mobile.read_only import ReadOnlyShopeeUI
from app.mobile.shopee_video import Screen, device_lock, video_profile_account_matches
from app.mobile.ui import IsolatedAndroidDevice, confirm_account
from app.operational.config import FeatureMode, ActionType
from app.operational.circuit_breaker import OperationCircuitBreaker
from app.operational.action_budget import AccountBudget, ActionBudget
from app.operational.modes import OperationModeEngine, OperationMode
from app.operational.deadlines import OperationalStop
from app.observability.operation_logger import OperationLogger


class IncidentReadBreaker(OperationCircuitBreaker):
    """Permission to inspect one UNKNOWN preparation, never to release a circuit."""
    def __init__(self, runtime, job, serial):
        super().__init__(runtime.store, runtime.candidate.account_id, runtime.config)
        self.job, self.serial = job, serial
        self.fingerprint = runtime.candidate.fingerprint()

    def check(self, *, read_only=False, db=None):
        if not read_only:
            raise OperationalStop('DIAGNOSTIC_MUTATION_BLOCKED')
        def verify(connection):
            if self.store.killed(connection):
                raise OperationalStop('KILL_SWITCH')
            row = connection.execute('SELECT * FROM jobs WHERE id=?',(self.job,)).fetchone()
            if (not row or row['account'] != self.account or row['fingerprint'] != self.fingerprint
                    or row['state'] != 'UNKNOWN' or row['attempted']
                    or json.loads(row['evidence'] or '{}').get('reason') not in ('RPC_EFFECT_UNKNOWN','EXPECTED_STATE_TIMEOUT','SUPERVISED_FLOW_INCOMPLETE')):
                raise OperationalStop('PREPARATION_DIAGNOSTIC_SCOPE_INVALID')
            if connection.execute('SELECT 1 FROM authorizations WHERE job=?',(self.job,)).fetchone():
                raise OperationalStop('PUBLISH_AUTHORIZATION_REQUIRES_RECONCILIATION')
            for key in ('account:'+self.account,'device:'+self.serial):
                lease = connection.execute('SELECT owner FROM leases WHERE key=?',(key,)).fetchone()
                if not lease or lease['owner'] != row['owner']:
                    raise OperationalStop('PREPARATION_DIAGNOSTIC_LEASE_MISMATCH')
        if db is not None: verify(db)
        else:
            with self.store.transaction() as connection: verify(connection)

    def release(self, **kwargs):
        raise OperationalStop('DIAGNOSTIC_CANNOT_RELEASE_BREAKER')


class IncidentReadModes(OperationModeEngine):
    def evaluate(self, context):
        super().evaluate(context)
        # Only this read-only session uses this engine. Kill/deadline still pause.
        if not any(context.get(k) for k in ('kill_switch','deadline_expired','budget_empty')):
            self.mode = OperationMode.RECOVERY
        return self.mode

    def can_execute(self, action_type):
        return action_type == ActionType.READ_STATE and self.mode == OperationMode.RECOVERY


class PreparationReadUI(ReadOnlyShopeeUI):
    def __init__(self, *args, media_path, **kwargs):
        super().__init__(*args, **kwargs)
        self.media_path = media_path

    def _execute(self, action, operation, args, *rest, **kwargs):
        if action != ActionType.READ_STATE or operation not in ('dump_hierarchy','app_current','app_info','screenshot','shell'):
            raise OperationalStop('READ_ONLY_ACTION_BLOCKED')
        if operation == 'app_info' and args != ['com.shopee.br']:
            raise OperationalStop('DIAGNOSTIC_PACKAGE_MISMATCH')
        if operation == 'shell':
            inventory = ['content', 'query', '--uri', 'content://media/external/video/media',
                '--projection', '_id:_display_name:_data:date_added:duration:_size', '--sort', 'date_added DESC']
            if args != [inventory] and (not self.media_path or args != [['sha256sum', self.media_path]]):
                raise OperationalStop('DIAGNOSTIC_SHELL_MUTATION_OR_SCOPE_BLOCKED')
        return super()._execute(action,operation,args,*rest,**kwargs)


@contextmanager
def preparation_diagnostic(runtime, job, *, authorization_reference, device=None):
    """Borrow the incident's retained leases under its existing exclusive USB lock.

    Neither leases, job state nor breaker are released. Normal reads/actions keep
    using the ordinary circuit rules. Read counters and sanitized logs are charged.
    """
    if runtime.config.mode != FeatureMode.ASSISTED_MODE or not authorization_reference:
        raise OperationalStop('EXPLICIT_ASSISTED_DIAGNOSTIC_REQUIRED')
    if runtime.ledger.identity(runtime.candidate) != job:
        raise OperationalStop('PREPARATION_DIAGNOSTIC_JOB_MISMATCH')
    runtime.deadline.raise_if_expired()
    breaker = IncidentReadBreaker(runtime,job,runtime.input['serial'])
    breaker.check(read_only=True)
    if device is not None and not getattr(device,'is_offline_fake',False):
        raise OperationalStop('UNBOUNDED_DEVICE_INJECTION_FORBIDDEN')
    owner = 'diagnostic_'+uuid.uuid4().hex
    logger = OperationLogger(runtime.root/'logs/operational'/f'{owner}.jsonl',session_id=owner,
        job_id=job,account_id=runtime.candidate.account_id)
    logger.log_validation(check='diagnostic_authorization_sha256:'+hashlib.sha256(authorization_reference.encode()).hexdigest(),status='PASS')
    budget = ActionBudget(runtime.store,AccountBudget(runtime.store,runtime.candidate.account_id,owner,
        'diagnostic:'+runtime.input['serial'],runtime.config),breaker,runtime.config)
    ui = None
    with device_lock(runtime.input['serial'],runtime.root/'logs/shopee_android/locks'):
        try:
            breaker.check(read_only=True)
            device = device or IsolatedAndroidDevice(runtime.input['serial'],runtime.deadline,runtime.config.rpc_seconds)
            ui = PreparationReadUI(device,runtime.config,runtime.deadline,budget,breaker,logger,IncidentReadModes(),
                media_path=runtime.input.get('video_path'))
            yield ui
        finally:
            if ui and hasattr(ui.device,'close'): ui.device.close()


def observe_preparation(ui, runtime):
    """Report UNKNOWNs explicitly; no selector/navigation is available here."""
    current = ui.app_current()
    result = dict(read_only=True,observed_at=time.time(),expected_account=runtime.expected.username,account_username=None,
        account_match='UNKNOWN',product_binding='UNKNOWN',native_upload_status='UNKNOWN',
        app=current,editor=False,publish_button_reached=False)
    if current.get('package') != 'com.shopee.br':
        return dict(result,blocker='SHOPEE_NOT_FOREGROUND')
    info = ui.app_info('com.shopee.br')
    if str(info.get('versionName','')) not in runtime.config.allowed_app_versions:
        return dict(result,blocker='APP_VERSION_CHANGED_REVIEW_REQUIRED')
    screen = Screen(ui.dump_hierarchy()); screen.guard()
    result['screen_sha256'] = hashlib.sha256(json.dumps(screen.nodes,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    try:
        confirm_account(screen,runtime.expected)
        result['account_match'] = 'PASS'
        result['account_username'] = runtime.expected.username
        if screen.texts('Nome de usuário: '+runtime.expected.username):
            result['account_validation_scope'] = 'READ_ONLY_NATIVE_VIDEO_PROFILE'
    except OperationalStop:
        # Existing Video profile parser accepts the exact native username prefix.
        # This report never substitutes for the operational mutation preflight.
        labels = {n.get('text','') for n in screen.nodes} | {n.get('content-desc','') for n in screen.nodes}
        if video_profile_account_matches(screen,runtime.expected.username) and runtime.expected.stable_profile_marker in labels:
            result['account_match'] = 'PASS'
            result['account_username'] = runtime.expected.username
            result['account_validation_scope'] = 'READ_ONLY_NATIVE_VIDEO_PROFILE'
    result['editor'] = screen.has('btn_post') and screen.has('iv_video_preview') and screen.has('et_caption')
    result['publish_button_reached'] = screen.has('btn_post')
    products = screen.ids('tv_product_title')
    if result['editor']:
        if len(products) == 1 and products[0].get('text') == runtime.candidate.product_title:
            result['product_binding'] = 'TITLE_MATCH_REVIEW_REQUIRED'
        elif not products and len(screen.ids('ll_add_product_symbol')) == 1:
            result['product_binding'] = 'CURRENT_EDITOR_UNBOUND'
        else:
            result['product_binding'] = 'AMBIGUOUS'
    result['blocker'] = 'ACCOUNT_IDENTITY_NOT_PROVEN' if result['account_match'] != 'PASS' else 'EDITOR_NOT_VISIBLE' if not result['editor'] else 'CURRENT_MEDIA_AND_PRODUCT_REVIEW_REQUIRED'
    return result
