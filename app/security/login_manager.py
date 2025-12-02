from __future__ import annotations

from typing import Optional

from flask import Flask, redirect, url_for, request, flash
from flask_login import current_user
from werkzeug.routing import BuildError

from app.extensions import login_manager, db
from app.domain.usuario import UsuarioMargemModel


def _safe_redirect_login(next_url: str | None = None):
    # Redireciona para a tela de login carregando com o parâmetro ?next=...
    try:
        if next_url:
            return redirect(url_for("auth.login", next=next_url))
        return redirect(url_for("auth.login"))
    except BuildError:
        return redirect("/")


def init_login(app: Flask) -> None:
    # Configura o Flask-Login no app e registra callbacks de segurança
    login_manager.init_app(app)
    login_manager.session_protection = "strong"
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id: str) -> Optional[UsuarioMargemModel]:
        # Carrega o usuário a partir do ID salvo na sessão
        if not user_id:
            return None

        try:
            user_id_int = int(user_id)
        except (TypeError, ValueError):
            app.logger.warning("user_loader recebeu id inválido: %r", user_id)
            return None

        try:
            user = db.session.get(UsuarioMargemModel, user_id_int)
        except Exception:
            app.logger.exception(
                "Erro ao carregar usuário no user_loader (id=%s)", user_id_int
            )
            return None

        if not user:
            return None

        # Se foi desativado no banco, não loga mais
        if not getattr(user, "ativo", True):
            app.logger.info(
                "Tentativa de carregar usuário inativo (id=%s, email=%s)",
                getattr(user, "id_usuario", None),
                getattr(user, "email_login", None),
            )
            return None

        return user

    @login_manager.unauthorized_handler
    def _unauthorized():
        if getattr(current_user, "is_authenticated", False):
            flash("Você não tem permissão para acessar esta página.", "danger")
            return redirect("/")

        flash("Faça login para acessar esta página.", "warning")
        next_url = request.url
        return _safe_redirect_login(next_url)
