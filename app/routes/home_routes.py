from __future__ import annotations

from decimal import Decimal

from flask import (
    Blueprint,
    render_template,
    request,
    flash,
)
from flask_login import login_required
from sqlalchemy import or_

from app.domain import MaquinaModel
from app.forms.home_forms import NovaReservaForm, EMPRESA_FILIAIS
from app.service.nova_reserva_service import (
    calcular_impostos_venda,
    calcular_impostos_compra,
)
from app.extensions import db

home_bp = Blueprint("home", __name__)


def _formatar_brl(valor: Decimal | None) -> str | None:
    if valor is None:
        return None
    s = f"{valor:,.2f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


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

    sa_session = db.session

    query = sa_session.query(MaquinaModel)
    if filtro_maquina:
        like = f"%{filtro_maquina}%"
        query = query.filter(
            or_(
                MaquinaModel.marca.ilike(like),
                MaquinaModel.modelo.ilike(like),
                MaquinaModel.codigo.ilike(like),
                MaquinaModel.tipo.ilike(like),
            )
        )

    maquinas = query.order_by(
        MaquinaModel.marca,
        MaquinaModel.modelo,
    ).all()

    # Popula o SelectField da máquina com as opções do BD
    form.maquina_id.choices = [
        (m.id_maquina, f"{m.codigo} - {m.modelo}") for m in maquinas
    ]

    impostos_venda = None
    impostos_venda_formatado = None

    impostos_compra = None
    impostos_compra_formatado = None

    # Só valida os dados, não insere nada no BD
    if form.validate_on_submit():
        # Cálculo de impostos de venda (ICMS + PIS/COFINS) * Valor de venda
        impostos_venda = calcular_impostos_venda(
            form.valor_venda.data,
            form.icms_percent.data,
            form.pis_cofins_percent.data,
        )
        impostos_venda_formatado = _formatar_brl(impostos_venda)

        # Impostos sobre compra
        # base = valor_compra da máquina escolhida no BD
        maquina_escolhida = None
        if form.maquina_id.data:
            mid = form.maquina_id.data
            maquina_escolhida = next(
                (m for m in maquinas if m.id_maquina == mid),
                None,
            )

        valor_base_compra = (
            maquina_escolhida.valor_compra if maquina_escolhida is not None else None
        )

        impostos_compra = calcular_impostos_compra(
            valor_base_compra,
            form.icms_pis_compra_percent.data,
            form.pis_cofins_compra_percent.data,
        )
        impostos_compra_formatado = _formatar_brl(impostos_compra)

        flash(
            "Dados da reserva validados com sucesso (ainda sem gravar no banco).",
            "success",
        )

    return render_template(
        "nova_reserva.html",
        form=form,
        impostos_venda=impostos_venda,
        impostos_venda_formatado=impostos_venda_formatado,
        impostos_compra=impostos_compra,
        impostos_compra_formatado=impostos_compra_formatado,
    )
