import os
import logging
from datetime import timedelta
from urllib.parse import quote_plus


def env_bool(key: str, default: bool = False) -> bool:
    val = os.getenv(key)
    if val is None:
        return default
    return str(val).strip().lower() in {"1", "true", "yes", "y", "on"}


def env_int(key: str, default: int) -> int:
    try:
        return int(str(os.getenv(key, str(default))).strip())
    except Exception:
        return default


def env_csv(key: str, default: str = "") -> list[str]:
    raw = os.getenv(key, default)
    if not raw:
        return []
    return [s.strip() for s in str(raw).split(",") if s and str(s).strip()]


# Lê um inteiro (segundos) do env e converte para timedelta
def env_timedelta_seconds(key: str, default_seconds: int):
    return timedelta(seconds=env_int(key, default_seconds))


class Config:
    # Flask / Cookies
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
    PREFERRED_URL_SCHEME = os.getenv("PREFERRED_URL_SCHEME", "https")

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    SESSION_COOKIE_NAME = os.getenv("SESSION_COOKIE_NAME", "cm_session")
    SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
    SESSION_COOKIE_SECURE = env_bool("SESSION_COOKIE_SECURE", True)
    SESSION_COOKIE_HTTPONLY = env_bool("SESSION_COOKIE_HTTPONLY", True)

    # Flask-Login remember cookie
    REMEMBER_COOKIE_DURATION = env_timedelta_seconds(
        "REMEMBER_COOKIE_DURATION", 60 * 60 * 24 * 7
    )  # 7 dias
    REMEMBER_COOKIE_HTTPONLY = env_bool("REMEMBER_COOKIE_HTTPONLY", True)
    REMEMBER_COOKIE_SECURE = env_bool("REMEMBER_COOKIE_SECURE", True)

    # Tempo de vida da sessão permanente
    PERMANENT_SESSION_LIFETIME = env_timedelta_seconds(
        "PERMANENT_SESSION_LIFETIME", 60 * 60 * 8
    )  # 8h

    # SQL Server (ODBC 17)
    _DATABASE_URL = os.getenv("DATABASE_URL", "").strip().strip('"').strip("'")

    _DRIVER = os.getenv("SQL_ODBC_DRIVER", "ODBC Driver 17 for SQL Server")
    _HOST = os.getenv("SQLSERVER_HOST", "")
    _DB = os.getenv("SQLSERVER_DB", "")
    _USER = os.getenv("SQLSERVER_USER", "")
    _PWD = os.getenv("SQLSERVER_PASSWORD", "")
    _ENCRYPT = os.getenv("SQL_ENCRYPT", "yes")
    _TRUST = os.getenv("SQL_TRUST_CERT", "no")
    _TIMEOUT = os.getenv("SQL_TIMEOUT", "30")
    _MARS = os.getenv("SQL_MARS", "no")

    if _DATABASE_URL:
        SQLALCHEMY_DATABASE_URI = _DATABASE_URL
    else:
        _ODBC = (
            f"Driver={{{_DRIVER}}};"
            f"Server={_HOST};"
            f"Database={_DB};"
            f"UID={_USER};PWD={_PWD};"
            f"Encrypt={_ENCRYPT};"
            f"TrustServerCertificate={_TRUST};"
            f"Connection Timeout={_TIMEOUT};"
            f"MARS_Connection={_MARS};"
        )
        SQLALCHEMY_DATABASE_URI = f"mssql+pyodbc:///?odbc_connect={quote_plus(_ODBC)}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = env_bool("SQLALCHEMY_ECHO", False)
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": env_int("SQL_POOL_RECYCLE", 300),
        "pool_size": env_int("SQL_POOL_SIZE", 10),
        "max_overflow": env_int("SQL_MAX_OVERFLOW", 20),
        "pool_timeout": env_int("SQL_POOL_TIMEOUT", 30),
    }

    # MSAL / Entra ID
    AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID", "")
    AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID", "")
    AZURE_CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET", "")
    AZURE_AUTHORITY = (
        f"https://login.microsoftonline.com/{AZURE_TENANT_ID}"
        if AZURE_TENANT_ID
        else ""
    )
    AZURE_REDIRECT_PATH = os.getenv("AZURE_REDIRECT_PATH", "/getAToken")

    AZURE_SCOPES = env_csv("AZURE_SCOPES", "User.Read")

    GRAPH_APP_SCOPE = os.getenv("GRAPH_APP_SCOPE", ".default")

    BRASIF_ALLOWED_DOMAINS = env_csv("BRASIF_ALLOWED_DOMAINS", "brasif.com.br")

    @staticmethod
    def emit_startup_warnings(logger: logging.Logger | None = None) -> None:
        lg = logger or logging.getLogger(__name__)
        if not Config.SECRET_KEY or Config.SECRET_KEY == "change-me":
            lg.warning("SECRET_KEY não configurada (use uma chave forte em produção).")
        if (
            not Config.AZURE_TENANT_ID
            or not Config.AZURE_CLIENT_ID
            or not Config.AZURE_CLIENT_SECRET
        ):
            lg.warning(
                "AZURE_TENANT_ID / AZURE_CLIENT_ID / AZURE_CLIENT_SECRET não configurados."
            )

    # Rate Limit / Proxy
    RATELIMIT_ENABLED = env_bool("RATELIMIT_ENABLED", True)
    RATELIMIT_STORAGE_URI = os.getenv("RATELIMIT_STORAGE_URI", "memory://")
    RATELIMIT_STRATEGY = os.getenv("RATELIMIT_STRATEGY", "moving-window")

    DEFAULT_RATE_LIMITS = env_csv("DEFAULT_RATE_LIMITS", "200 per minute")

    LIMITER_EXEMPT_PATH_PREFIXES = env_csv("LIMITER_EXEMPT_PATH_PREFIXES", "")

    USE_PROXY_FIX = env_bool("USE_PROXY_FIX", False)
    PROXY_FIX_X_FOR = env_int("PROXY_FIX_X_FOR", 1)
    PROXY_FIX_X_PROTO = env_int("PROXY_FIX_X_PROTO", 1)
    PROXY_FIX_X_HOST = env_int("PROXY_FIX_X_HOST", 0)
    PROXY_FIX_X_PORT = env_int("PROXY_FIX_X_PORT", 0)
    PROXY_FIX_X_PREFIX = env_int("PROXY_FIX_X_PREFIX", 0)
