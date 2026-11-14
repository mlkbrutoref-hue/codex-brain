"""Controlled inspection session. No selector, text, key or shell mutation API."""
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import uuid
from app.mobile.ui import ShopeeUI, IsolatedAndroidDevice, confirm_account
from app.operational.config import OperationalConfig, FeatureMode
from app.operational.store import OperationalStore
from app.operational.deadlines import ExecutionDeadline, OperationalStop
from app.operational.action_budget import AccountBudget, ActionBudget
from app.operational.circuit_breaker import OperationCircuitBreaker
from app.observability.operation_logger import OperationLogger
from app.validation.product_media_truth import ExpectedAccount


class ReadOnlyShopeeUI(ShopeeUI):
    def _execute(self,action,*args,**kwargs):
        from app.operational.config import ActionType
        if action != ActionType.READ_STATE:
            raise OperationalStop('READ_ONLY_ACTION_BLOCKED')
        return super()._execute(action,*args,**kwargs)
    def click(self,*a,**kw): raise OperationalStop('READ_ONLY_ACTION_BLOCKED')
    def set_text(self,*a,**kw): raise OperationalStop('READ_ONLY_ACTION_BLOCKED')
    def press(self,*a,**kw): raise OperationalStop('READ_ONLY_ACTION_BLOCKED')
    def xpath(self,*a,**kw): raise OperationalStop('READ_ONLY_ACTION_BLOCKED')
    def final_click(self,*a,**kw): raise OperationalStop('READ_ONLY_ACTION_BLOCKED')


@contextmanager
def read_only_session(config, root=Path('.'), *, store=None, device=None, verify_account=True):
    from app.mobile.shopee_video import Screen
    operational=OperationalConfig.from_dict(config.get('operational'))
    expected=ExpectedAccount(**config['account'])
    if operational.mode == FeatureMode.DRY_RUN:
        raise OperationalStop('DRY_RUN_EXTERNAL_ACTION_BLOCKED')
    if operational.mode != FeatureMode.ASSISTED_MODE:
        raise OperationalStop('READ_ONLY_REQUIRES_ASSISTED_MODE')
    store=store or OperationalStore()
    deadline=ExecutionDeadline(operational.session_seconds)
    breaker=OperationCircuitBreaker(store,expected.account_id,operational)
    breaker.check(read_only=True)
    owner=uuid.uuid4().hex
    budget=ActionBudget(store,AccountBudget(store,expected.account_id,owner,config.get('worker_id','probe:'+config['serial']),operational),breaker,operational)
    logger=OperationLogger(Path(root)/'logs/operational'/f'probe_{owner}.jsonl',session_id=owner,job_id='probe',account_id=expected.account_id)
    with store.transaction() as db:
        try:
            for key in ('account:'+expected.account_id,'device:'+config['serial']):
                db.execute('INSERT INTO leases VALUES (?,?)',(key,owner))
        except Exception:
            raise OperationalStop('ACCOUNT_OR_DEVICE_ALREADY_IN_USE') from None
    ui=None
    try:
        if device is not None and not getattr(device,'is_offline_fake',False):
            raise OperationalStop('UNBOUNDED_DEVICE_INJECTION_FORBIDDEN')
        device=device or IsolatedAndroidDevice(config['serial'],deadline,operational.rpc_seconds)
        ui=ReadOnlyShopeeUI(device,operational,deadline,budget,breaker,logger)
        screen=Screen(ui.dump_hierarchy()); screen.guard()
        # Diagnostic inspection may report identity as unknown; mutation APIs
        # remain unavailable. Normal callers still require confirmed identity.
        if verify_account:
            confirm_account(screen,expected)
        if ui.app_current().get('package') != 'com.shopee.br': raise OperationalStop('UNEXPECTED_FOREGROUND_APP')
        if str(ui.app_info('com.shopee.br').get('versionName','')) not in operational.allowed_app_versions:
            raise OperationalStop('APP_VERSION_CHANGED_REVIEW_REQUIRED')
        yield ui
    except Exception as exc:
        reason=str(exc).split(':',1)[0] if isinstance(exc,RuntimeError) else type(exc).__name__
        breaker.failure(reason,critical=reason in ('ACCOUNT_MISMATCH','HUMAN_ACCOUNT_VERIFICATION_REQUIRED'))
        raise
    finally:
        if ui and hasattr(ui.device,'close'): ui.device.close()
        with store.transaction() as db: db.execute('DELETE FROM leases WHERE owner=?',(owner,))


def capture_read_only(ui):
    from app.mobile.shopee_video import Screen
    screen=Screen(ui.dump_hierarchy()); screen.guard()
    # Retain structural evidence and hashes, never full screen text or screenshot.
    fields=('resource-id','class','bounds','clickable','enabled','selected','checked')
    return dict(app=ui.app_current(),screen_sha256=hashlib.sha256(json.dumps(screen.nodes,sort_keys=True,ensure_ascii=False).encode()).hexdigest(),
        linked_node_sha256=hashlib.sha256(json.dumps(screen.ids('tv_product_title'),sort_keys=True,ensure_ascii=False).encode()).hexdigest(),
        nodes=[{key:n[key] for key in fields if key in n} for n in screen.nodes],read_only=True)
