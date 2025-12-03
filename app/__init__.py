from __future__ import annotations

import importlib
import logging

from flask import Flask, render_template, request, current_app, g
from flask_login import current_user
from flask_wtf.csrf import generate_csrf
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_limiter.errors import RateLimitExceeded

from sqlalchemy import text as sa_text

from .app_config import Config
from .extensions import db, limiter, csrf
from .security.login_manager import init_login
from app.forms.auth_forms import LogoutForm

# Flag de processo de warmup global
_APP_WARMUP_DONE: bool = False


def _optional_import(
    path: str, logger, *, quiet_if_missing: bool = True
) -> object | None:
    try:
        return importlib.import_module(path)
    except ModuleNotFoundError:
        if not quiet_if_missing:
            logger.warning("Módulo '%s' não encontrado (ok)", path)
        else:
            logger.debug("Módulo '%s' não encontrado (ok)", path)
        return None
    except Exception:
        logger.exception("Módulo '%s' não carregado", path)
        return None


def _run_global_warmup(app: Flask) -> None:
    try:
        with app.app_context():
            db.session.execute(sa_text("SELECT 1")).scalar()
        app.logger.info("[Warmup] DB ping=ok, catalogs primed")
    except Exception as exc:
        app.logger.warning("[Warmup] DB ping falhou: %s", exc)


def create_app(config_class: type[Config] = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Logging
    level_name = (app.config.get("LOG_LEVEL") or "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(level=level)

    Config.emit_startup_warnings(app.logger)

    # ProxyFix (se estiver atrás de proxy)
    if app.config.get("USE_PROXY_FIX"):
        app.wsgi_app = ProxyFix(
            app.wsgi_app,
            x_for=app.config.get("PROXY_FIX_X_FOR", 1),
            x_proto=app.config.get("PROXY_FIX_X_PROTO", 1),
            x_host=app.config.get("PROXY_FIX_X_HOST", 0),
            x_port=app.config.get("PROXY_FIX_X_PORT", 0),
            x_prefix=app.config.get("PROXY_FIX_X_PREFIX", 0),
        )

    # Extensões
    db.init_app(app)
    init_login(app)
    limiter.init_app(app)
    csrf.init_app(app)

    # Disponibiliza csrf_token() para templates
    app.jinja_env.globals.update(csrf_token=generate_csrf)

    # Blueprints
    msal_mod = _optional_import("app.security.msal_auth", app.logger)
    if msal_mod and hasattr(msal_mod, "auth_bp"):
        app.register_blueprint(msal_mod.auth_bp)

    home_mod = _optional_import("app.routes.home_routes", app.logger)
    if home_mod and hasattr(home_mod, "home_bp"):
        app.register_blueprint(home_mod.home_bp)


    # Controle do warmup
    @app.before_request
    def _ensure_global_warmup():
        global _APP_WARMUP_DONE

        if getattr(g, "_warmup_done", False):
            return

        if _APP_WARMUP_DONE:
            return

        # Faz o warmup pesado uma vez só
        _run_global_warmup(app)

        _APP_WARMUP_DONE = True
        g._warmup_done = True

    # Contexto global para templates
    @app.context_processor
    def inject_nav_flags():

        def _user_uid(u) -> str:
            try:
                return str(
                    getattr(u, "id_azure_ad", None)
                    or getattr(u, "azure_ad_id", None)
                    or getattr(u, "oid", None)
                    or ""
                )
            except Exception:
                return ""

        can = False
        if current_user.is_authenticated:
            admin = bool(getattr(current_user, "is_admin", False))
            allowed_ids = {
                str(x) for x in current_app.config.get("AD_SYNC_ALLOWED_IDS", [])
            }
            uid = _user_uid(current_user)
            in_allowed = bool(uid) and (uid in allowed_ids)
            can = admin or in_allowed

        return dict(can_sync_ad=can)

    @app.context_processor
    def inject_logout_form():
        return dict(logout_form=LogoutForm())

    # Error handlers (fallbacks simples)
    @app.errorhandler(401)
    def _handle_401(_e):
        try:
            return render_template("errors/401.html"), 401
        except Exception:
            return ("Não autenticado. Faça login para continuar.", 401)

    @app.errorhandler(403)
    def _handle_403(_e):
        try:
            return render_template("errors/403.html"), 403
        except Exception:
            return ("Acesso negado. Você não tem permissão para esta página.", 403)

    @app.errorhandler(RateLimitExceeded)
    def _handle_429(e: RateLimitExceeded):
        # Retry-After
        try:
            retry_after = int(getattr(e, "retry_after", 0) or 0)
        except Exception:
            retry_after = 0

        # Log estruturado
        try:
            uid = (
                getattr(current_user, "id", None)
                or getattr(current_user, "oid", None)
                or (current_user.get_id() if hasattr(current_user, "get_id") else None)
            )
        except Exception:
            uid = None

        ip = None
        try:
            if request.access_route:
                ip = request.access_route[0]
        except Exception:
            ip = None
        ip = ip or request.remote_addr or "unknown"

        rule = getattr(e, "limit", str(e))
        app.logger.warning(
            "rate_limit_exceeded ip=%s user_id=%s endpoint=%s rule=%s retry_after=%s",
            ip,
            uid,
            request.endpoint,
            rule,
            retry_after,
        )

        # Cabeçalhos padrão do Flask-Limiter e Retry-After
        headers = dict(e.get_headers()) if hasattr(e, "get_headers") else {}
        if retry_after:
            headers["Retry-After"] = str(retry_after)

        try:
            return (
                render_template("errors/429.html", retry_after=retry_after, rule=rule),
                429,
                headers,
            )
        except Exception:
            msg = (
                f"Você excedeu o limite de requisições ({rule}). "
                f"Tente novamente em {retry_after or 'alguns'} segundo(s)."
            )
            return msg, 429, headers

    return app
