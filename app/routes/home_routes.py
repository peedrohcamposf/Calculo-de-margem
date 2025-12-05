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
    calcular_total_horas_opcionais,
    calcular_mao_obra_agrega_desagrega,
    calcular_credito_impostos,
    calcular_entrega_tecnica_pdi_garantia,
    calcular_cmv,
    calcular_lucro_bruto,
    calcular_carta_fianca,
    calcular_comissao_bruta,
    calcular_dsr,
    calcular_encargos_comissao,
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

    # Opcionais / Agrega / Desagrega
    opcionais_itens: list[dict[str, str]] = []
    total_horas_opcionais: Decimal | None = None
    total_horas_opcionais_formatado: str | None = None

    if request.method == "POST":
        nomes = request.form.getlist("opcional_nome")
        horas = request.form.getlist("opcional_horas")

        # Limita de 100 linhas
        max_len = min(len(nomes), len(horas), 100)
        horas_para_soma: list[str] = []

        for idx in range(max_len):
            nome_raw = (nomes[idx] or "").strip()
            horas_raw = (horas[idx] or "").strip()

            # Ignora linha totalmente em branco
            if not nome_raw and not horas_raw:
                continue

            opcionais_itens.append(
                {
                    "nome": nome_raw,
                    "horas": horas_raw,
                }
            )

            if horas_raw:
                horas_para_soma.append(horas_raw)

        if horas_para_soma:
            total_horas_opcionais = calcular_total_horas_opcionais(horas_para_soma)
            total_horas_opcionais_formatado = _formatar_brl(total_horas_opcionais)
        else:
            total_horas_opcionais = None
            total_horas_opcionais_formatado = None

    impostos_venda = None
    impostos_venda_formatado = None

    impostos_compra = None
    impostos_compra_formatado = None

    mao_obra_agrega_desagrega_valor = None
    mao_obra_agrega_desagrega_valor_formatado = None

    credito_impostos_valor = None
    credito_impostos_valor_formatado = None

    credito_impostos_venda_valor = None
    credito_impostos_venda_valor_formatado = None

    valor_maquina_base = None
    valor_maquina_base_formatado = None

    cmv_valor = None
    cmv_valor_formatado = None

    contrato_manutencao_valor = None
    contrato_manutencao_valor_formatado = None

    entrega_tecnica_pdi_garantia_valor = None
    entrega_tecnica_pdi_garantia_valor_formatado = None

    lucro_bruto_valor = None
    lucro_bruto_valor_formatado = None

    carta_fianca_valor = None
    carta_fianca_valor_formatado = None

    comissao_bruta_valor = None
    comissao_bruta_valor_formatado = None

    dsr_valor = None
    dsr_valor_formatado = None

    encargos_comissao_valor = None
    encargos_comissao_valor_formatado = None

    # Só valida os dados, não insere nada no BD
    if form.validate_on_submit():
        # Cálculo de impostos de venda (ICMS + PIS/COFINS) * Valor de venda
        impostos_venda = calcular_impostos_venda(
            form.valor_venda.data,
            form.icms_percent.data,
            form.pis_cofins_percent.data,
        )
        impostos_venda_formatado = _formatar_brl(impostos_venda)

        # Carta fiança bancária = % sobre valor de venda
        if (
            form.valor_venda.data is not None
            and form.carta_fianca_percent.data is not None
        ):
            carta_fianca_valor = calcular_carta_fianca(
                form.valor_venda.data,
                form.carta_fianca_percent.data,
            )
            carta_fianca_valor_formatado = _formatar_brl(carta_fianca_valor)

        # Contrato de manutenção (valor direto informado)
        if form.contrato_manutencao.data is not None:
            contrato_manutencao_valor = form.contrato_manutencao.data
            contrato_manutencao_valor_formatado = _formatar_brl(
                contrato_manutencao_valor
            )

        # Entrega técnica / PDI / Garantia (percentual sobre valor de venda)
        if (
            form.valor_venda.data is not None
            and form.entrega_tecnica_pdi_garantia_percent.data is not None
        ):
            entrega_tecnica_pdi_garantia_valor = calcular_entrega_tecnica_pdi_garantia(
                form.valor_venda.data,
                form.entrega_tecnica_pdi_garantia_percent.data,
            )
            entrega_tecnica_pdi_garantia_valor_formatado = _formatar_brl(
                entrega_tecnica_pdi_garantia_valor
            )

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

        valor_maquina_base = valor_base_compra
        if valor_maquina_base is not None:
            valor_maquina_base_formatado = _formatar_brl(valor_maquina_base)

        impostos_compra = calcular_impostos_compra(
            valor_base_compra,
            form.icms_pis_compra_percent.data,
            form.pis_cofins_compra_percent.data,
        )
        impostos_compra_formatado = (
            _formatar_brl(impostos_compra) if impostos_compra is not None else None
        )

        # Mão de obra agrega/desagrega (horas x 200)
        if form.mao_obra_agrega_desagrega_horas.data is not None:
            mao_obra_agrega_desagrega_valor = calcular_mao_obra_agrega_desagrega(
                form.mao_obra_agrega_desagrega_horas.data
            )
            mao_obra_agrega_desagrega_valor_formatado = _formatar_brl(
                mao_obra_agrega_desagrega_valor
            )

        # Crédito de impostos (frete compra * % crédito)
        if (
            form.frete_compra.data is not None
            and form.credito_impostos_percent.data is not None
        ):
            credito_impostos_valor = calcular_credito_impostos(
                form.frete_compra.data,
                form.credito_impostos_percent.data,
            )
            credito_impostos_valor_formatado = _formatar_brl(credito_impostos_valor)

        # Crédito de impostos (frete venda * % crédito)
        if (
            form.frete_venda.data is not None
            and form.credito_impostos_venda_percent.data is not None
        ):
            credito_impostos_venda_valor = calcular_credito_impostos(
                form.frete_venda.data,
                form.credito_impostos_venda_percent.data,
            )
            credito_impostos_venda_valor_formatado = _formatar_brl(
                credito_impostos_venda_valor
            )

        # CMV
        if valor_maquina_base is not None:
            cmv_valor = calcular_cmv(
                valor_maquina=valor_maquina_base,
                impostos_compra=impostos_compra,
                opcionais_valor=total_horas_opcionais,
                frete_compra=form.frete_compra.data,
                credito_impostos_valor=credito_impostos_valor,
                mao_obra_valor=mao_obra_agrega_desagrega_valor,
            )
            cmv_valor_formatado = _formatar_brl(cmv_valor)

        # Lucro Bruto
        if (
            form.valor_venda.data is not None
            and impostos_venda is not None
            and cmv_valor is not None
        ):
            lucro_bruto_valor = calcular_lucro_bruto(
                valor_venda=form.valor_venda.data,
                impostos_venda=impostos_venda,
                cmv=cmv_valor,
                contrato_manutencao=contrato_manutencao_valor,
                entrega_tecnica_valor=entrega_tecnica_pdi_garantia_valor,
            )
            lucro_bruto_valor_formatado = _formatar_brl(lucro_bruto_valor)

        # Comissão Bruta = % * valor de venda
        if (
            form.valor_venda.data is not None
            and form.comissao_bruta_percent.data is not None
        ):
            comissao_bruta_valor = calcular_comissao_bruta(
                form.valor_venda.data,
                form.comissao_bruta_percent.data,
            )
            comissao_bruta_valor_formatado = _formatar_brl(comissao_bruta_valor)

        # DSR = % * comissão bruta
        if comissao_bruta_valor is not None and form.dsr_percent.data is not None:
            dsr_valor = calcular_dsr(
                comissao_bruta_valor,
                form.dsr_percent.data,
            )
            dsr_valor_formatado = _formatar_brl(dsr_valor)

        # Encargos comissão = % * (comissão bruta + DSR)
        if (
            comissao_bruta_valor is not None
            and dsr_valor is not None
            and form.encargos_comissao_percent.data is not None
        ):
            encargos_comissao_valor = calcular_encargos_comissao(
                comissao_bruta_valor,
                dsr_valor,
                form.encargos_comissao_percent.data,
            )
            encargos_comissao_valor_formatado = _formatar_brl(encargos_comissao_valor)

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
        opcionais_itens=opcionais_itens,
        total_horas_opcionais=total_horas_opcionais,
        total_horas_opcionais_formatado=total_horas_opcionais_formatado,
        mao_obra_agrega_desagrega_valor=mao_obra_agrega_desagrega_valor,
        mao_obra_agrega_desagrega_valor_formatado=mao_obra_agrega_desagrega_valor_formatado,
        credito_impostos_valor=credito_impostos_valor,
        credito_impostos_valor_formatado=credito_impostos_valor_formatado,
        credito_impostos_venda_valor=credito_impostos_venda_valor,
        credito_impostos_venda_valor_formatado=credito_impostos_venda_valor_formatado,
        valor_maquina_base=valor_maquina_base,
        valor_maquina_base_formatado=valor_maquina_base_formatado,
        cmv_valor=cmv_valor,
        cmv_valor_formatado=cmv_valor_formatado,
        contrato_manutencao_valor=contrato_manutencao_valor,
        contrato_manutencao_valor_formatado=contrato_manutencao_valor_formatado,
        entrega_tecnica_pdi_garantia_valor=entrega_tecnica_pdi_garantia_valor,
        entrega_tecnica_pdi_garantia_valor_formatado=entrega_tecnica_pdi_garantia_valor_formatado,
        lucro_bruto_valor=lucro_bruto_valor,
        lucro_bruto_valor_formatado=lucro_bruto_valor_formatado,
        carta_fianca_valor=carta_fianca_valor,
        carta_fianca_valor_formatado=carta_fianca_valor_formatado,
        comissao_bruta_valor=comissao_bruta_valor,
        comissao_bruta_valor_formatado=comissao_bruta_valor_formatado,
        dsr_valor=dsr_valor,
        dsr_valor_formatado=dsr_valor_formatado,
        encargos_comissao_valor=encargos_comissao_valor,
        encargos_comissao_valor_formatado=encargos_comissao_valor_formatado,
    )
