"""Credentials management for Shopee Affiliate API with strict secrecy boundaries."""
import os
from pathlib import Path
from typing import Optional


class AffiliateCredentials:
    """Securely resolves Shopee Affiliate API credentials without echoing or exposing them."""

    DEFAULT_FALLBACK_ENV = Path(
        r"C:\Users\GAMER\Documents\Codex\2026-08-30\files-pasted-by-the-user-projeto\outputs\shopee-video-automation\.env"
    )

    def __init__(self, env_path: Optional[Path] = None):
        self._app_id = ""
        self._secret = ""

        # 1. Direct environment variables
        app_id_env = os.getenv("SHOPEE_APP_ID", "").strip()
        secret_env = os.getenv("SHOPEE_SECRET", "").strip()
        if app_id_env and secret_env:
            self._app_id = app_id_env
            self._secret = secret_env
            return

        # 2. Specified or local .env file
        candidate_paths = []
        if env_path:
            candidate_paths.append(Path(env_path))
        
        local_env = Path(__file__).resolve().parents[3] / ".env"
        candidate_paths.append(local_env)
        
        # 3. Validated external project path (read directly in place, without copying)
        if self.DEFAULT_FALLBACK_ENV.exists():
            candidate_paths.append(self.DEFAULT_FALLBACK_ENV)

        for p in candidate_paths:
            if p.exists() and p.is_file():
                self._load_from_file(p)
                if self._app_id and self._secret:
                    return

        if not self._app_id or not self._secret:
            raise RuntimeError(
                "Credenciais da Shopee ausentes. Configure SHOPEE_APP_ID e SHOPEE_SECRET para usar o modo LIVE."
            )

    def _load_from_file(self, file_path: Path) -> None:
        try:
            with open(file_path, "r", encoding="utf-8-sig") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip("'\"")
                        if k == "SHOPEE_APP_ID" and v:
                            self._app_id = v
                        elif k == "SHOPEE_SECRET" and v:
                            self._secret = v
        except Exception:
            pass

    @property
    def app_id(self) -> str:
        return self._app_id

    @property
    def secret(self) -> str:
        return self._secret

    def is_configured(self) -> bool:
        return bool(self._app_id and self._secret)

    def __repr__(self) -> str:
        return "AffiliateCredentials([REDACTED])"