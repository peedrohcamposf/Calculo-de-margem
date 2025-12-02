from __future__ import annotations

import logging
import secrets
from typing import Sequence, Any

import msal
from flask import (
    Blueprint,
    current_app,
    redirect,
    render_template,
    request,
    session,
    flash,
    url_for,
)
from flask_login import (
    current_user,
    login_user,
    logout_user,
    login_required,
)
from werkzeug.exceptions import BadRequest
from werkzeug.routing import BuildError
from urllib.parse import urlparse, urljoin

from app.extensions import db, limiter
from app.domain.usuario import UsuarioMargemModel

auth_bp = Blueprint("auth", __name__)

# Limite específico para rotas de auth
LOGIN_RATE_LIMIT = "10 per minute"


def _build_msal_app() -> msal.ConfidentialClientApplication:
    # Cria o client MSAL com base na configuração do app
    cfg = current_app.config

    client_id = cfg.get("AZURE_CLIENT_ID")
    client_secret = cfg.get("AZURE_CLIENT_SECRET")
    authority = cfg.get("AZURE_AUTHORITY")

    if not client_id or not client_secret or not authority:
        current_app.logger.error("Azure AD não configurado corretamente.")
        raise RuntimeError(
            "Azure AD não configurado. Verifique as variáveis de ambiente."
        )

    return msal.ConfidentialClientApplication(
        client_id=client_id,
        client_credential=client_secret,
        authority=authority,
    )


def _get_scopes() -> list[str]:
    scopes = current_app.config.get("AZURE_SCOPES") or ["User.Read"]
    if isinstance(scopes, str):
        return [s.strip() for s in scopes.split(",") if s.strip()]
    return list(scopes)


def _get_redirect_uri() -> str:
    scheme = current_app.config.get("PREFERRED_URL_SCHEME", "https")
    return url_for("auth.callback", _external=True, _scheme=scheme)


def _is_safe_next_url(target: str | None) -> bool:
    if not target:
        return False

    host_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))

    return test_url.scheme in ("http", "https") and host_url.netloc == test_url.netloc


def _redirect_home():
    try:
        return redirect(url_for("home.index"))
    except BuildError:
        return redirect("/")


def _extract_claim(claims: dict[str, Any], *keys: str) -> str | None:
    for key in keys:
        value = claims.get(key)
        if value:
            return str(value)
    return None


def _email_domain_allowed(email: str) -> bool:
    # Verifica se o domínio do e-mail no BRASIF_ALLOWED_DOMAINS
    allowed: Sequence[str] = current_app.config.get("BRASIF_ALLOWED_DOMAINS") or []
    if not allowed:
        return True

    if "@" not in email:
        return False

    domain = email.split("@", 1)[1].lower().strip()
    allowed_norm = {d.lower().strip() for d in allowed if d.strip()}
    return domain in allowed_norm


def _normalize_cargo(value: str, max_length: int = 30) -> str | None:
    raw = str(value).strip()
    if not raw:
        return None

    normalized = " ".join(raw.split())
    if not normalized:
        return None

    return normalized[:max_length]


def _extract_cargo_from_claims(claims: dict[str, Any]) -> str | None:
    raw = _extract_claim(
        claims,
        "jobTitle",
        "job_title",
        "title",
    )
    if not raw:
        return None
    return _normalize_cargo(raw)


def _fetch_cargo_from_graph(access_token: str) -> str | None:
    if not access_token:
        return None

    try:
        import requests

        resp = requests.get(
            "https://graph.microsoft.com/v1.0/me?$select=jobTitle",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=5,
        )
    except Exception as exc:  # noqa: BLE001
        current_app.logger.warning("Falha ao chamar Graph para obter jobTitle: %s", exc)
        return None

    if resp.status_code != 200:
        current_app.logger.warning(
            "Graph /me retornou status %s ao buscar jobTitle.",
            resp.status_code,
        )
        return None

    try:
        data = resp.json() or {}
    except Exception as exc:  # noqa: BLE001
        current_app.logger.warning(
            "Falha ao parsear JSON do Graph ao obter jobTitle: %s", exc
        )
        return None

    raw = data.get("jobTitle")
    if not raw:
        return None

    return _normalize_cargo(raw)


def _get_cargo_from_ad(result: dict[str, Any], claims: dict[str, Any]) -> str | None:
    cargo = _extract_cargo_from_claims(claims)
    if cargo:
        return cargo

    access_token = result.get("access_token")
    if not access_token:
        return None

    return _fetch_cargo_from_graph(access_token)


# Tela de login apenas para renreziação do template
@auth_bp.get("/login-page")
def login_page():
    if current_user.is_authenticated:
        return _redirect_home()

    return render_template("auth/login.html")


# Início do fluxo de login usando MSAL
@auth_bp.route("/login")
@limiter.limit(LOGIN_RATE_LIMIT)
def login():
    if current_user.is_authenticated:
        flash("Você já está autenticado.", "info")
        return _redirect_home()

    # CSRF do fluxo de OAuth (state)
    state = secrets.token_urlsafe(32)
    session["auth_state"] = state

    cca = _build_msal_app()
    scopes = _get_scopes()
    redirect_uri = _get_redirect_uri()

    auth_url = cca.get_authorization_request_url(
        scopes=scopes,
        state=state,
        redirect_uri=redirect_uri,
        prompt="select_account",  # Força escolha de conta quando necessário
    )

    return redirect(auth_url)


# Endpoint de callback do Azure AD
@auth_bp.route("/getAToken")
@limiter.limit(LOGIN_RATE_LIMIT)
def callback():
    expected_state = session.pop("auth_state", None)
    received_state = request.args.get("state")

    if not expected_state or received_state != expected_state:
        current_app.logger.warning(
            "Estado inválido no callback do Azure AD. expected=%r received=%r",
            expected_state,
            received_state,
        )
        raise BadRequest("Estado de autenticação inválido. Tente novamente o login.")

    # Se houve erro no lado do Azure, trata e informa
    error = request.args.get("error")
    if error:
        desc = request.args.get("error_description") or ""
        current_app.logger.warning("Erro no login Azure AD: %s - %s", error, desc)
        flash("Não foi possível autenticar no Azure. Tente novamente.", "danger")
        return redirect(url_for("auth.login"))

    code = request.args.get("code")
    if not code:
        raise BadRequest("Código de autorização ausente.")

    cca = _build_msal_app()
    scopes = _get_scopes()
    redirect_uri = _get_redirect_uri()

    result = cca.acquire_token_by_authorization_code(
        code=code,
        scopes=scopes,
        redirect_uri=redirect_uri,
    )

    if "error" in result:
        current_app.logger.error(
            "Erro ao trocar código por token no Azure AD: %s - %s",
            result.get("error"),
            result.get("error_description"),
        )
        flash("Erro ao finalizar o login no Azure. Tente novamente.", "danger")
        return redirect(url_for("auth.login"))

    claims: dict[str, Any] = result.get("id_token_claims") or {}
    if not claims:
        current_app.logger.error("id_token_claims ausente na resposta do Azure.")
        flash("Erro de autenticação. Tente novamente.", "danger")
        return redirect(url_for("auth.login"))

    azure_oid = _extract_claim(claims, "oid", "sub")
    email = _extract_claim(claims, "preferred_username", "upn", "email")
    nome = _extract_claim(claims, "name", "given_name")

    if not azure_oid or not email:
        current_app.logger.error(
            "Claims obrigatórios ausentes. oid=%r email=%r claims_keys=%r",
            azure_oid,
            email,
            sorted(claims.keys()),
        )
        flash(
            "Não foi possível obter seus dados de login. Contate o suporte.",
            "danger",
        )
        return redirect(url_for("auth.login"))

    if not _email_domain_allowed(email):
        current_app.logger.warning(
            "Login bloqueado para domínio não permitido: %s", email
        )
        flash("Seu e-mail não é permitido neste sistema.", "danger")
        return redirect(url_for("auth.login"))

    # Obtém cargo diretamente do AD (claims + Graph)
    cargo_ad = _get_cargo_from_ad(result, claims)

    # Upsert seguro do usuário
    try:
        user = (
            db.session.query(UsuarioMargemModel)
            .filter(UsuarioMargemModel.azure_oid == azure_oid)
            .one_or_none()
        )

        if not user:
            # Fallback: procura por email_login
            user = (
                db.session.query(UsuarioMargemModel)
                .filter(UsuarioMargemModel.email_login == email)
                .one_or_none()
            )

        created = False
        if not user:
            # Novo usuário exige cargo vindo do AD
            if not cargo_ad:
                current_app.logger.error(
                    "Novo usuário sem cargo nas claims/Graph. oid=%r email=%r keys=%r",
                    azure_oid,
                    email,
                    sorted(claims.keys()),
                )
                flash(
                    "Não foi possível obter seu cargo no AD. "
                    "Fale com o suporte para liberar seu acesso.",
                    "danger",
                )
                return redirect(url_for("auth.login"))

            user = UsuarioMargemModel(
                azure_oid=azure_oid,
                email_login=email,
                nome=nome,
                cargo=cargo_ad,
                ativo=True,
            )
            db.session.add(user)
            created = True
        else:
            # Usuário existente, atualiza dados principais
            user.azure_oid = azure_oid
            user.email_login = email
            if nome:
                user.nome = nome

            # Atualiza cargo pelo AD se veio algo
            if cargo_ad:
                user.cargo = cargo_ad

            # Se o usuário não tiver cargo no AD, não loga para manter NOT NULL
            if not user.cargo:
                current_app.logger.error(
                    "Usuário existente sem cargo e AD não retornou cargo. "
                    "oid=%r email=%r",
                    azure_oid,
                    email,
                )
                db.session.rollback()
                flash(
                    "Seu usuário está sem cargo configurado. "
                    "Fale com o suporte para regularizar.",
                    "danger",
                )
                return redirect(url_for("auth.login"))

        db.session.commit()

    except Exception as exc:
        db.session.rollback()
        current_app.logger.exception(
            "Erro ao criar/atualizar usuário de login: %s", exc
        )
        flash("Erro interno ao processar seu login. Tente novamente.", "danger")
        return redirect(url_for("auth.login"))

    if not getattr(user, "ativo", True):
        flash("Seu usuário está inativo. Fale com o suporte.", "danger")
        return redirect(url_for("auth.login"))

    # Autentica no Flask-Login
    login_user(user, remember=True)

    if created:
        flash("Seu acesso foi criado com sucesso.", "success")
    else:
        flash("Login realizado com sucesso.", "success")

    # Trata ?next=...
    next_url = request.args.get("next")
    if next_url and _is_safe_next_url(next_url):
        return redirect(next_url)

    return _redirect_home()


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    email = getattr(current_user, "email_login", None)
    current_app.logger.info("Usuário fazendo logout: %s", email)

    # Limpa sessão de login
    logout_user()

    # Limpa outros dados de sessão
    session.clear()

    flash("Você saiu da sessão com sucesso.", "info")
    return redirect(url_for("auth.login"))
