from __future__ import annotations

from decimal import Decimal

from flask import Blueprint, render_template, request, flash
from flask_login import login_required

from app.forms.home_forms import NovaReservaForm, EMPRESA_FILIAIS
from app.repository.maquina_repository import MaquinaRepository
from app.service.nova_reserva_service import NovaReservaService
from app.extensions import db

home_bp = Blueprint("home", __name__)


@home_bp.route("/", methods=["GET", "POST"])
@login_required
def nova_reserva():
    form = NovaReservaForm()

    # Empresa x Filial (choices do Select)
    empresa_selecionada = form.empresa.data or ""
    if empresa_selecionada:
        form.filial.choices = [
            (nome, nome) for nome in EMPRESA_FILIAIS.get(empresa_selecionada, [])
        ]
    else:
        form.filial.choices = []

    # Filtro de máquina (modelo, código e etc.)
    filtro_maquina = (form.filtro_maquina.data or "").strip()
    if not filtro_maquina:
        # Permite também filtrar via querystring ?q=...
        filtro_maquina = (request.args.get("q") or "").strip()

    maquina_repo = MaquinaRepository(db.session)
    service = NovaReservaService(maquina_repo)

    # Carrega máquinas do BD via repository
    maquinas = service.carregar_maquinas(filtro_maquina)
    form.maquina_id.choices = service.montar_choices_maquina(maquinas)

    # Opcionais / Agrega / Desagrega
    if request.method == "POST":
        (
            opcionais_itens,
            total_horas_opcionais,
            total_horas_opcionais_formatado,
        ) = service.processar_opcionais(
            nomes=request.form.getlist("opcional_nome"),
            horas=request.form.getlist("opcional_horas"),
        )
    else:
        opcionais_itens: list[dict[str, str]] = []
        total_horas_opcionais: Decimal | None = None
        total_horas_opcionais_formatado: str | None = None

    # Contexto de cálculo (inicialmente vazio)
    contexto_calculos = service.contexto_inicial()

    # Só valida os dados, não insere nada no BD
    if form.validate_on_submit():
        contexto_calculos = service.calcular_contexto(
            form=form,
            total_horas_opcionais=total_horas_opcionais,
        )

        flash(
            "Dados da reserva validados com sucesso.",
            "success",
        )

    return render_template(
        "nova_reserva.html",
        form=form,
        opcionais_itens=opcionais_itens,
        total_horas_opcionais=total_horas_opcionais,
        total_horas_opcionais_formatado=total_horas_opcionais_formatado,
        **contexto_calculos,
    )
