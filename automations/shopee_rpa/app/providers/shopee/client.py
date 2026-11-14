"""Shopee Affiliate GraphQL Client implementing the validated protocol."""
import json
import time
import hashlib
import urllib.request
import urllib.error
from typing import Dict, Any, Optional
from app.providers.shopee.credentials import AffiliateCredentials
from enum import Enum
from email.utils import parsedate_to_datetime
import uuid
from app.operational.config import OperationalConfig
from app.operational.store import OperationalStore
from app.operational.deadlines import ExecutionDeadline, OperationalStop
from app.operational.circuit_breaker import OperationCircuitBreaker
from app.operational.action_budget import AccountBudget
from app.operational.http_transport import BoundedHTTPTransport

ENDPOINT = "https://open-api.affiliate.shopee.com.br/graphql"
EXPLORER = "https://open-api.affiliate.shopee.com.br/explorer"


class AffiliateErrorKind(str, Enum):
    RATE_LIMITED = 'RATE_LIMITED'
    AUTH_OR_ACCESS = 'AUTH_OR_ACCESS'
    REMOTE_FAILURE = 'REMOTE_FAILURE'
    NETWORK_UNKNOWN = 'NETWORK_UNKNOWN'
    INVALID_RESPONSE = 'INVALID_RESPONSE'
    IDENTITY_MISMATCH = 'IDENTITY_MISMATCH'


def retry_after_seconds(value, stamp=None):
    stamp = time.time() if stamp is None else stamp
    try:
        return max(0., float(value))
    except (TypeError,ValueError):
        try: return max(0., parsedate_to_datetime(value).timestamp()-stamp)
        except (TypeError,ValueError,OverflowError): return 0.


class AffiliateAPIError(RuntimeError):
    """Controlled error message; never leaks credentials, requests or sensitive dumps."""
    def __init__(self, message, kind=AffiliateErrorKind.INVALID_RESPONSE, *, status=None, retry_after=0):
        super().__init__(message)
        self.kind, self.status, self.retry_after = kind, status, retry_after


class ShopeeAffiliateClient:
    """Client protocol confirmed and validated against the Brazilian Shopee Affiliate API."""

    def __init__(self, credentials: Optional[AffiliateCredentials] = None, timeout_seconds: float = 30.0,
                 *, operational_config=None, store=None, deadline=None, transport=None, account_id=None):
        self._credentials = credentials or AffiliateCredentials()
        self.timeout_seconds = timeout_seconds
        self.operational = operational_config or OperationalConfig()
        self.store = store or OperationalStore()
        self.deadline = deadline or ExecutionDeadline(self.operational.session_seconds)
        self.transport = transport or BoundedHTTPTransport()
        self.session_id = uuid.uuid4().hex
        self.account_id = account_id

    def execute(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Executes a GraphQL query using exact serialization and SHA256 signature."""
        app_id = self._credentials.app_id
        secret = self._credentials.secret
        account = self.account_id or ('affiliate:' + hashlib.sha256(app_id.encode()).hexdigest())
        breaker = OperationCircuitBreaker(self.store,account,self.operational)
        self.deadline.raise_if_expired()
        breaker.check(read_only=True)
        budgets = AccountBudget(self.store,account,self.session_id,self.session_id,self.operational)
        day, session, _ = budgets.scopes()
        with self.store.transaction() as db:
            breaker.check(read_only=True,db=db)
            for scope, maximum in ((day,self.operational.limits.affiliate_requests_day),(session,self.operational.limits.affiliate_requests_session)):
                row=db.execute('SELECT amount FROM counters WHERE scope=? AND name=\'affiliate_requests\'',(scope,)).fetchone()
                if (row['amount'] if row else 0)+1>maximum:
                    raise AffiliateAPIError('AFFILIATE_BUDGET_EXCEEDED',AffiliateErrorKind.RATE_LIMITED)
            for scope in (day,session):
                db.execute('INSERT INTO counters VALUES (?,\'affiliate_requests\',1) ON CONFLICT(scope,name) DO UPDATE SET amount=amount+1',(scope,))

        payload = json.dumps(
            {"query": query, "variables": variables or {}},
            ensure_ascii=False,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")

        timestamp = str(int(time.time()))
        
        # Validated signature: app_id + timestamp + payload + secret (plain SHA256)
        signature = hashlib.sha256(
            app_id.encode("utf-8") + timestamp.encode("utf-8") + payload + secret.encode("utf-8")
        ).hexdigest()

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"SHA256 Credential={app_id}, Timestamp={timestamp}, Signature={signature}",
            "User-Agent": "AICommerceContentFactory/1.0",
        }

        try:
            status_code,retry_after,raw_bytes=self.transport(ENDPOINT,payload,headers,self.deadline,self.timeout_seconds)
        except (OperationalStop,TimeoutError,OSError):
            breaker.failure('NETWORK_UNKNOWN')
            raise AffiliateAPIError('Shopee API: NETWORK_UNKNOWN',AffiliateErrorKind.NETWORK_UNKNOWN) from None
        self.deadline.raise_if_expired()
        if status_code != 200:
            kind = (AffiliateErrorKind.RATE_LIMITED if status_code==429 else
                    AffiliateErrorKind.AUTH_OR_ACCESS if status_code in (401,403) else AffiliateErrorKind.REMOTE_FAILURE)
            delay=retry_after_seconds(retry_after)
            breaker.failure(kind.value,critical=status_code in (401,403),retry_after=max(1,delay) if status_code==429 else delay)
            raise AffiliateAPIError('Shopee API: '+kind.value,kind,status=status_code,retry_after=delay)
        try:
            body=json.loads(raw_bytes.decode('utf-8'))
        except (UnicodeError,ValueError,AttributeError):
            breaker.failure('INVALID_RESPONSE')
            raise AffiliateAPIError('Resposta GraphQL não contém JSON válido.') from None

        if not isinstance(body, dict):
            raise AffiliateAPIError("Resposta GraphQL não é um dicionário.")

        if body.get("errors"):
            # Never propagate remote text (it may mirror secrets or request data).
            breaker.failure('REMOTE_FAILURE')
            raise AffiliateAPIError('Shopee API: GraphQL error',AffiliateErrorKind.REMOTE_FAILURE)

        data = body.get("data")
        if not isinstance(data, dict):
            raise AffiliateAPIError("Resposta GraphQL sem objeto data válido.")

        # Security check: ensure no secrets were mirrored in response
        serialized = json.dumps(data, ensure_ascii=False)
        if any(v in serialized for v in (app_id, secret, signature)):
            raise AffiliateAPIError("Resposta bloqueada pela proteção de credenciais.")

        breaker.success()
        return data

    def check_connection(self) -> bool:
        """Runs a minimal introspection query to verify credentials and connectivity."""
        data = self.execute("query ConnectionCheck { __typename }")
        return data.get("__typename") == "Query"
