from __future__ import annotations

from flask import Blueprint, current_app, flash, render_template, request
from flask_login import current_user, login_required

from app.extensions import db
from app.forms.home_forms import NovaReservaForm
from app.services.margem_service import CalculoMargemError, NovaReservaService

home_bp = Blueprint(
    "home",
    __name__,
    url_prefix="",
    template_folder="templates",
    static_folder="static",
)


@home_bp.route("/", methods=["GET", "POST"])
@login_required
def index():

    service = NovaReservaService(db.session)
    form = NovaReservaForm()

    # Sempre preenche as choices antes de validar
    service.preencher_choices_form(form)

    calculo_resultado = None

    if request.method == "POST":
        if form.validate_on_submit():
            try:
                calculo_resultado = service.calcular(form)
                flash("Margem calculada com sucesso.", "success")
            except CalculoMargemError as exc:
                current_app.logger.warning(
                    "Erro de negócio ao calcular margem: %s",
                    exc,
                    extra={"event": "home.calculo_margem"},
                )
                flash(str(exc), "warning")
            except Exception:
                current_app.logger.exception(
                    "Erro inesperado ao calcular margem",
                    extra={"event": "home.calculo_margem_erro"},
                )
                flash(
                    "Ocorreu um erro inesperado ao calcular a margem. "
                    "Tente novamente e, se persistir, contate o suporte.",
                    "danger",
                )
        else:
            flash("Corrija os erros do formulário antes de calcular.", "warning")

    # Template ainda será criado; por enquanto, a view já entrega:
    # - form: com selects carregados e valores enviados
    # - calculo: objeto CalculoMargemResultado (ou None)
    return render_template(
        "home/index.html",
        form=form,
        calculo=calculo_resultado,
        usuario=current_user,
    )
