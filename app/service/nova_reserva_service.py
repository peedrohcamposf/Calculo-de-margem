from __future__ import annotations

from decimal import Decimal
from typing import Any, Iterable, Sequence, Optional

from app.forms.home_forms import NovaReservaForm
from app.repository.maquina_repository import MaquinaRepository
from app.utils.formatacao import formatar_brl
from app.utils.calculos_margem import (
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
    calcular_total_comissao_vendedor,
    calcular_percentual_comissao_sobre_venda,
    calcular_margem_contribuicao,
    calcular_percentual_rb,
    calcular_percentual_margem_rb,
)


_CALCULO_KEYS = (
    "impostos_venda",
    "impostos_venda_formatado",
    "impostos_compra",
    "impostos_compra_formatado",
    "valor_maquina_base",
    "valor_maquina_base_formatado",
    "cmv_valor",
    "cmv_valor_formatado",
    "mao_obra_agrega_desagrega_valor",
    "mao_obra_agrega_desagrega_valor_formatado",
    "credito_impostos_valor",
    "credito_impostos_valor_formatado",
    "credito_impostos_venda_valor",
    "credito_impostos_venda_valor_formatado",
    "contrato_manutencao_valor",
    "contrato_manutencao_valor_formatado",
    "entrega_tecnica_pdi_garantia_valor",
    "entrega_tecnica_pdi_garantia_valor_formatado",
    "lucro_bruto_valor",
    "lucro_bruto_valor_formatado",
    "carta_fianca_valor",
    "carta_fianca_valor_formatado",
    "comissao_bruta_valor",
    "comissao_bruta_valor_formatado",
    "dsr_valor",
    "dsr_valor_formatado",
    "encargos_comissao_valor",
    "encargos_comissao_valor_formatado",
    "comissao_total_vendedor_valor",
    "comissao_total_vendedor_valor_formatado",
    "comissao_total_vendedor_percent",
    "comissao_total_vendedor_percent_formatado",
    "margem_contribuicao_valor",
    "margem_contribuicao_valor_formatado",
    "percentual_rb_valor",
    "percentual_rb_valor_formatado",
    "percentual_margem_rb_valor",
    "percentual_margem_rb_valor_formatado",
)


# Cria um dicionário com todas as chaves esperadas pelo template inicializadas com None
def _contexto_vazio() -> dict[str, Any]:
    return {k: None for k in _CALCULO_KEYS}


class NovaReservaService:

    def __init__(self, maquina_repository: MaquinaRepository) -> None:
        self._maquina_repository = maquina_repository

    # Máquinas
    def carregar_maquinas(self, filtro: str | None) -> Sequence:
        return self._maquina_repository.buscar(filtro)

    @staticmethod
    def montar_choices_maquina(maquinas: Sequence) -> list[tuple[int, str]]:
        return MaquinaRepository.montar_choices_select(maquinas)

    # Opcionais / Agrega / Desagrega
    @staticmethod
    def processar_opcionais(
        nomes: Iterable[str],
        horas: Iterable[str],
        limite_linhas: int = 100,
    ) -> tuple[list[dict[str, str]], Optional[Decimal], Optional[str]]:

        nomes_list = list(nomes)
        horas_list = list(horas)

        itens: list[dict[str, str]] = []
        horas_para_soma: list[str] = []

        max_len = min(len(nomes_list), len(horas_list), limite_linhas)

        for idx in range(max_len):
            nome_raw = (nomes_list[idx] or "").strip()
            horas_raw = (horas_list[idx] or "").strip()

            # Ignora linha totalmente vazia
            if not nome_raw and not horas_raw:
                continue

            itens.append({"nome": nome_raw, "horas": horas_raw})

            if horas_raw:
                horas_para_soma.append(horas_raw)

        if horas_para_soma:
            total_horas = calcular_total_horas_opcionais(horas_para_soma)
            total_horas_formatado = formatar_brl(total_horas)
        else:
            total_horas = None
            total_horas_formatado = None

        return itens, total_horas, total_horas_formatado

    # Retorna o contexto vazio para a tela (sem cálculos)
    @staticmethod
    def contexto_inicial() -> dict[str, Any]:
        return _contexto_vazio()

    # Cálculos principais
    def calcular_contexto(
        self,
        form: NovaReservaForm,
        total_horas_opcionais: Optional[Decimal],
    ) -> dict[str, Any]:
        # Calcula todos os valores da margem de contribuição a partir do formulário já validado
        ctx = _contexto_vazio()

        # Impostos de venda
        impostos_venda = calcular_impostos_venda(
            form.valor_venda.data,
            form.icms_percent.data,
            form.pis_cofins_percent.data,
        )
        ctx["impostos_venda"] = impostos_venda
        ctx["impostos_venda_formatado"] = formatar_brl(impostos_venda)

        # Carta fiança bancária = % sobre valor de venda
        carta_fianca_valor: Optional[Decimal] = None
        if (
            form.valor_venda.data is not None
            and form.carta_fianca_percent.data is not None
        ):
            carta_fianca_valor = calcular_carta_fianca(
                form.valor_venda.data,
                form.carta_fianca_percent.data,
            )
            ctx["carta_fianca_valor"] = carta_fianca_valor
            ctx["carta_fianca_valor_formatado"] = formatar_brl(carta_fianca_valor)

        # Contrato de manutenção (valor direto)
        contrato_manutencao_valor: Optional[Decimal] = None
        if form.contrato_manutencao.data is not None:
            contrato_manutencao_valor = form.contrato_manutencao.data
            ctx["contrato_manutencao_valor"] = contrato_manutencao_valor
            ctx["contrato_manutencao_valor_formatado"] = formatar_brl(
                contrato_manutencao_valor
            )

        # Entrega técnica / PDI / Garantia (% sobre o valor de venda)
        entrega_tecnica_pdi_garantia_valor: Optional[Decimal] = None
        if (
            form.valor_venda.data is not None
            and form.entrega_tecnica_pdi_garantia_percent.data is not None
        ):
            entrega_tecnica_pdi_garantia_valor = calcular_entrega_tecnica_pdi_garantia(
                form.valor_venda.data,
                form.entrega_tecnica_pdi_garantia_percent.data,
            )
            ctx["entrega_tecnica_pdi_garantia_valor"] = (
                entrega_tecnica_pdi_garantia_valor
            )
            ctx["entrega_tecnica_pdi_garantia_valor_formatado"] = formatar_brl(
                entrega_tecnica_pdi_garantia_valor
            )

        # Impostos de compra / valor da máquina

        valor_maquina_base: Optional[Decimal] = None
        if form.maquina_id.data:
            maquina = self._maquina_repository.obter_por_id(form.maquina_id.data)
            if maquina is not None:
                valor_maquina_base = maquina.valor_compra

        ctx["valor_maquina_base"] = valor_maquina_base
        ctx["valor_maquina_base_formatado"] = (
            formatar_brl(valor_maquina_base) if valor_maquina_base is not None else None
        )

        impostos_compra = calcular_impostos_compra(
            valor_maquina_base,
            form.icms_pis_compra_percent.data,
            form.pis_cofins_compra_percent.data,
        )
        ctx["impostos_compra"] = impostos_compra
        ctx["impostos_compra_formatado"] = (
            formatar_brl(impostos_compra) if impostos_compra is not None else None
        )

        # Mão de obra agrega/desagrega (horas x 200)
        mao_obra_agrega_desagrega_valor: Optional[Decimal] = None
        if form.mao_obra_agrega_desagrega_horas.data is not None:
            mao_obra_agrega_desagrega_valor = calcular_mao_obra_agrega_desagrega(
                form.mao_obra_agrega_desagrega_horas.data
            )
            ctx["mao_obra_agrega_desagrega_valor"] = mao_obra_agrega_desagrega_valor
            ctx["mao_obra_agrega_desagrega_valor_formatado"] = formatar_brl(
                mao_obra_agrega_desagrega_valor
            )

        # Crédito de impostos (frete compra * % crédito)
        credito_impostos_valor: Optional[Decimal] = None
        if (
            form.frete_compra.data is not None
            and form.credito_impostos_percent.data is not None
        ):
            credito_impostos_valor = calcular_credito_impostos(
                form.frete_compra.data,
                form.credito_impostos_percent.data,
            )
            ctx["credito_impostos_valor"] = credito_impostos_valor
            ctx["credito_impostos_valor_formatado"] = formatar_brl(
                credito_impostos_valor
            )

        # Crédito de impostos (frete venda * % crédito)
        credito_impostos_venda_valor: Optional[Decimal] = None
        if (
            form.frete_venda.data is not None
            and form.credito_impostos_venda_percent.data is not None
        ):
            credito_impostos_venda_valor = calcular_credito_impostos(
                form.frete_venda.data,
                form.credito_impostos_venda_percent.data,
            )
            ctx["credito_impostos_venda_valor"] = credito_impostos_venda_valor
            ctx["credito_impostos_venda_valor_formatado"] = formatar_brl(
                credito_impostos_venda_valor
            )

        # CMV
        cmv_valor: Optional[Decimal] = None
        if valor_maquina_base is not None:
            cmv_valor = calcular_cmv(
                valor_maquina=valor_maquina_base,
                impostos_compra=impostos_compra,
                opcionais_valor=total_horas_opcionais,
                frete_compra=form.frete_compra.data,
                credito_impostos_valor=credito_impostos_valor,
                mao_obra_valor=mao_obra_agrega_desagrega_valor,
            )
            ctx["cmv_valor"] = cmv_valor
            ctx["cmv_valor_formatado"] = formatar_brl(cmv_valor)

        # Lucro Bruto
        lucro_bruto_valor: Optional[Decimal] = None
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
            ctx["lucro_bruto_valor"] = lucro_bruto_valor
            ctx["lucro_bruto_valor_formatado"] = formatar_brl(lucro_bruto_valor)

        # Comissão Vendedor
        comissao_bruta_valor: Optional[Decimal] = None
        if (
            form.valor_venda.data is not None
            and form.comissao_bruta_percent.data is not None
        ):
            comissao_bruta_valor = calcular_comissao_bruta(
                form.valor_venda.data,
                form.comissao_bruta_percent.data,
            )
            ctx["comissao_bruta_valor"] = comissao_bruta_valor
            ctx["comissao_bruta_valor_formatado"] = formatar_brl(comissao_bruta_valor)

        dsr_valor: Optional[Decimal] = None
        if comissao_bruta_valor is not None and form.dsr_percent.data is not None:
            dsr_valor = calcular_dsr(
                comissao_bruta_valor,
                form.dsr_percent.data,
            )
            ctx["dsr_valor"] = dsr_valor
            ctx["dsr_valor_formatado"] = formatar_brl(dsr_valor)

        encargos_comissao_valor: Optional[Decimal] = None
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
            ctx["encargos_comissao_valor"] = encargos_comissao_valor
            ctx["encargos_comissao_valor_formatado"] = formatar_brl(
                encargos_comissao_valor
            )

        comissao_total_vendedor_valor: Optional[Decimal] = None
        comissao_total_vendedor_percent: Optional[Decimal] = None
        if (
            comissao_bruta_valor is not None
            and dsr_valor is not None
            and encargos_comissao_valor is not None
            and form.valor_venda.data is not None
        ):
            comissao_total_vendedor_valor = calcular_total_comissao_vendedor(
                comissao_bruta_valor,
                dsr_valor,
                encargos_comissao_valor,
            )
            ctx["comissao_total_vendedor_valor"] = comissao_total_vendedor_valor
            ctx["comissao_total_vendedor_valor_formatado"] = formatar_brl(
                comissao_total_vendedor_valor
            )

            comissao_total_vendedor_percent = calcular_percentual_comissao_sobre_venda(
                comissao_total_vendedor_valor,
                form.valor_venda.data,
            )
            ctx["comissao_total_vendedor_percent"] = comissao_total_vendedor_percent
            ctx["comissao_total_vendedor_percent_formatado"] = (
                formatar_brl(comissao_total_vendedor_percent)
                if comissao_total_vendedor_percent is not None
                else None
            )

        # Margem de Contribuição / %RB
        if lucro_bruto_valor is not None and form.valor_venda.data is not None:
            margem_contribuicao_valor = calcular_margem_contribuicao(
                lucro_bruto=lucro_bruto_valor,
                frete_venda=form.frete_venda.data,
                credito_impostos_venda=credito_impostos_venda_valor,
                custo_financeiro=form.custo_financeiro.data,
                carta_fianca=carta_fianca_valor,
                cortesia=form.cortesia.data,
                comissao_total_vendedor=comissao_total_vendedor_valor,
            )
            ctx["margem_contribuicao_valor"] = margem_contribuicao_valor
            ctx["margem_contribuicao_valor_formatado"] = formatar_brl(
                margem_contribuicao_valor
            )

            percentual_rb_valor = calcular_percentual_rb(
                margem_contribuicao_valor,
                form.valor_venda.data,
            )
            ctx["percentual_rb_valor"] = percentual_rb_valor
            ctx["percentual_rb_valor_formatado"] = (
                formatar_brl(percentual_rb_valor)
                if percentual_rb_valor is not None
                else None
            )

            percentual_margem_rb_valor = calcular_percentual_margem_rb(
                lucro_bruto_valor,
                form.valor_venda.data,
            )
            ctx["percentual_margem_rb_valor"] = percentual_margem_rb_valor
            ctx["percentual_margem_rb_valor_formatado"] = (
                formatar_brl(percentual_margem_rb_valor)
                if percentual_margem_rb_valor is not None
                else None
            )

        return ctx
