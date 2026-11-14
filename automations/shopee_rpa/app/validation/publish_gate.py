from dataclasses import dataclass
from app.operational.config import FeatureMode, ActionType
from app.operational.deadlines import OperationalStop
from app.operational.modes import OperationMode
from app.validation.product_media_truth import CheckStatus


@dataclass(frozen=True)
class PublishAuthorization:
    token: str
    job_id: str


class PublishGate:
    def __init__(self, ledger, validator, budget, breaker, deadline, modes, config):
        self.ledger, self.validator, self.budget, self.breaker = ledger, validator, budget, breaker
        self.deadline, self.modes, self.config = deadline, modes, config

    def _validate(self, candidate, context):
        self.deadline.raise_if_expired()
        operator_scope=bool(context.get('operator_authorized') and self.validator.operator_listing_approval(candidate))
        if self.config.mode != FeatureMode.LIVE_PUBLISH or not (context.get('platform_authorized') or operator_scope):
            raise OperationalStop('LIVE_PUBLISH_DISABLED_OR_UNAUTHORIZED')
        if context.get('account_id') != candidate.account_id or not context.get('account_current'):
            raise OperationalStop('ACCOUNT_IDENTITY_NOT_PROVEN')
        if not context.get('app_expected') or not context.get('screen_expected') or not context.get('media_selected'):
            raise OperationalStop('APP_SCREEN_OR_MEDIA_NOT_PROVEN')
        if context.get('product') != candidate.product:
            raise OperationalStop('PRODUCT_IDENTITY_NOT_PROVEN')
        if self.modes.mode not in (OperationMode.NORMAL, OperationMode.CAUTIOUS):
            raise OperationalStop('OPERATION_MODE_FORBIDS_PUBLISH')
        report = self.validator.validate(candidate, observed_product=context['product'])
        if report.status != CheckStatus.PASS:
            raise OperationalStop('CONTENT_GATE_' + report.status.value)
        return report

    def authorize(self, job, owner, candidate, context):
        self._validate(candidate, context)
        with self.ledger.store.transaction() as db:
            self.breaker.check(db=db)
            if self.ledger.duplicate(candidate, db, exclude=job):
                raise OperationalStop('DUPLICATE_MEDIA')
            self.budget.consume(ActionType.PUBLISH_ATTEMPT, db=db)
            token = self.ledger.reserve_publish_attempt(db, job, owner, candidate.fingerprint(), self.config.authorization_ttl)
        return PublishAuthorization(token, job)

    def consume(self, authorization, owner, candidate, context):
        self._validate(candidate, context)
        with self.ledger.store.transaction() as db:
            self.breaker.check(db=db)
            self.ledger.consume_authorization(db, authorization, candidate, owner)
