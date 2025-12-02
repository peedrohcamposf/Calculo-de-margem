from __future__ import annotations

import os
from typing import Iterable

from flask import current_app, request
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()

login_manager = LoginManager()
login_manager.login_view = "auth.login"  # Rota de login
login_manager.login_message_category = "warning"  # Categoria padrão dos flashes

# CSRF global
csrf = CSRFProtect()


# Helpers de env/CSV
def _csv_to_list(value: str | Iterable[str] | None) -> list[str]:
    if not value:
        return []
    if isinstance(value, str):
        return [v.strip() for v in value.split(",") if v.strip()]
    return [str(v).strip() for v in value if str(v).strip()]


def _csv_env(key: str, default_csv: str) -> list[str]:
    raw = os.getenv(key)
    if not raw or not raw.strip():
        return _csv_to_list(default_csv)
    return _csv_to_list(raw)


def _bool_env(key: str, default: bool) -> bool:
    raw = os.getenv(key)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


# Rate limit key segura
def rate_limit_key() -> str:
    try:
        if getattr(current_user, "is_authenticated", False):
            uid = (
                getattr(current_user, "id", None)
                or getattr(current_user, "oid", None)
                or (current_user.get_id() if hasattr(current_user, "get_id") else None)
            )
            if uid:
                return f"user:{uid}"
    except Exception:
        pass

    # IP do cliente
    ip = None
    try:
        if request.access_route:
            ip = request.access_route[0]
    except Exception:
        ip = None
    if not ip:
        xff = request.headers.get("X-Forwarded-For", "")
        if xff:
            ip = xff.split(",")[0].strip()
    ip = ip or (request.remote_addr or "unknown")
    return f"ip:{ip}"


# Filtro para ignorar rate limit no static e em prefixos extras em LIMITER_EXEMPT_PATH_PREFIXES
def _limiter_skip_static_and_health() -> bool:
    p = request.path or ""
    if p == "/health" or p.startswith("/static/") or p == "/favicon.ico":
        return True
    for prefix in current_app.config.get("LIMITER_EXEMPT_PATH_PREFIXES", []):
        if prefix and p.startswith(prefix):
            return True
    return False


# Valores resolvidos
_DEFAULT_LIMITS = _csv_env("DEFAULT_RATE_LIMITS", "200 per minute")
_STORAGE_URI = os.getenv("RATELIMIT_STORAGE_URI", "memory://")
_STRATEGY = os.getenv("RATELIMIT_STRATEGY", "moving-window")
_ENABLED = _bool_env("RATELIMIT_ENABLED", True)

# Limiter
limiter = Limiter(
    key_func=rate_limit_key if _ENABLED else get_remote_address,
    default_limits=_DEFAULT_LIMITS,  # Exemplo: ["200 per minute"]
    storage_uri=_STORAGE_URI,  # Exemplo: "memory://"
    strategy=_STRATEGY,  # "moving-window" ou "fixed-window"
    headers_enabled=True,
    enabled=_ENABLED,  # bool
)


@limiter.request_filter
def _skip_static_health_and_whitelist() -> bool:
    return _limiter_skip_static_and_health()


# Limite padrão para APIs Admin
ADMIN_RATE_LIMIT = "30 per minute"
