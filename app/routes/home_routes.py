from __future__ import annotations

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

    # Só valida os dados, não insere nada no BD
    if form.validate_on_submit():
        flash(
            "Dados da reserva validados com sucesso (ainda sem gravar no banco).",
            "success",
        )

    return render_template(
        "nova_reserva.html",
        form=form,
    )
