from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP, getcontext
from typing import List, Optional

from flask import current_app
from sqlalchemy.orm import Session

from app.forms.home_forms import NovaReservaForm
from app.repositories.margem_repository import MargemRepository

# Precisão global para cálculos financeiros
getcontext().prec = 18


# Dataclasses de retorno
@dataclass
class FluxoParcela:
    tipo_parcela: int  # 1 = entrada, 2 = parcela
    numero_parcela: int  # 0 para entrada
    prazo_dias: int
    percentual_base: Decimal
    valor_nominal: Decimal
    taxa_efetiva: Decimal
    valor_presente: Decimal
    custo_financeiro: Decimal


@dataclass
class CalculoMargemResultado:
    valor_venda_total: Decimal

    impostos_venda_total: Decimal
    valor_dn: Decimal
    impostos_compra_total: Decimal
    cmv_total: Decimal

    valor_opcionais: Decimal
    frete_compra: Decimal
    credito_impostos_frete_compra: Decimal
    custo_mao_obra: Decimal
    contrato_manutencao: Decimal
    valor_pdi_garantia: Decimal

    lucro_bruto_valor: Decimal
    margem_bruta_percent: Decimal

    frete_venda: Decimal
    credito_impostos_frete_venda: Decimal
    custo_financeiro_total: Decimal
    valor_carta_fianca: Decimal
    valor_cortesia: Decimal

    comissao_bruta: Decimal
    comissao_dsr: Decimal
    comissao_encargos: Decimal
    comissao_total: Decimal

    margem_contrib_valor: Decimal
    margem_contrib_percent: Decimal

    fluxo_parcelas: List[FluxoParcela]


class CalculoMargemError(RuntimeError):
    """Erro de negócio previsível durante o cálculo de margem"""


# Códigos esperados na tb_cm_margem_parametro_geral
PARAM_ICMS_VENDA = "ICMS_VENDA"
PARAM_PISCOFINS_VENDA = "PIS_COFINS_VENDA"
PARAM_ICMS_PISCOFINS_COMPRA = "ICMS_PIS_COFINS_COMPRA"
PARAM_PISCOFINS_COMPRA = "PIS_COFINS_COMPRA"
PARAM_CREDITO_IMP_FRETE_COMPRA = "CREDITO_IMPOSTOS_FRETE_COMPRA"
PARAM_CREDITO_IMP_FRETE_VENDA = "CREDITO_IMPOSTOS_FRETE_VENDA"
PARAM_PDI_GARANTIA = "PDI_GARANTIA_PERC"
PARAM_TAXA_JUROS_MENSAL = "TAXA_JUROS_MENSAL"
PARAM_COMISSAO_BRUTA = "COMISSAO_BRUTA_PERC"
PARAM_COMISSAO_DSR = "COMISSAO_DSR_PERC"
PARAM_COMISSAO_ENCARGOS = "COMISSAO_ENCARGOS_PERC"
PARAM_CARTA_FIANCA = "CARTA_FIANCA_PERC"


def _q2(value: Decimal) -> Decimal:
    # Arredonda para 2 casas decimais (valores monetários)
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _q6(value: Decimal) -> Decimal:
    # Arredonda para 6 casas decimais (percentuais)
    return value.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)


# Service que orquestra o cálculo de margem
class NovaReservaService:

    def __init__(self, session: Session) -> None:
        self._session = session
        self._repo = MargemRepository(session)

    # Preparação do formulário
    def preencher_choices_form(self, form: NovaReservaForm) -> None:
        
        # Carrega as opções dos selects
        clientes = self._repo.listar_clientes_ativos()
        form.cliente_id.choices = [
            (row["id_cliente"], f"{row['codigo_sap']} - {row['razao_social']}")
            for row in clientes
        ]

        filiais = self._repo.listar_filiais_ativas()
        form.filial_id.choices = [
            (row["id_filial"], f"{row['codigo_sap']} - {row['nome']}")
            for row in filiais
        ]

        produtos = self._repo.listar_produtos_ativos()
        form.produto_id.choices = [
            (row["id_produto"], f"{row['codigo_sap']} - {row['descricao']}")
            for row in produtos
        ]

        tipos = self._repo.listar_tipos_venda_ativos()
        form.tipo_venda_id.choices = [
            (row["id_tipo_venda"], row["nome"]) for row in tipos
        ]

        modalidades = self._repo.listar_modalidades_ativas()
        form.modalidade_fin_id.choices = [(-1, "Sem modalidade vinculada")]
        form.modalidade_fin_id.choices += [
            (row["id_modalidade_fin"], row["nome"]) for row in modalidades
        ]

        bancos = self._repo.listar_bancos_ativos()
        form.banco_financiador_id.choices = [(-1, "Sem banco vinculado")]
        form.banco_financiador_id.choices += [
            (row["id_banco_financiador"], row["nome"]) for row in bancos
        ]

    # Cálculo principal (sem persistência dos dados)
    def calcular(self, form: NovaReservaForm) -> CalculoMargemResultado:
        if not form.validate():
            raise CalculoMargemError("Dados inválidos para cálculo de margem.")

        data_reserva = form.data_reserva.data or date.today()
        previsao_entrega = form.previsao_entrega.data

        id_filial = form.filial_id.data
        id_tipo_venda = form.tipo_venda_id.data
        id_modalidade_fin = (
            None if form.modalidade_fin_id.data in (None, -1) else form.modalidade_fin_id.data
        )


        # DN (Desconto / custo base da máquina) - Célula E22 na planilha
        ano_dn, mes_dn = self._resolver_ano_mes_dn(previsao_entrega or data_reserva)
        dn_config = self._repo.obter_config_dn(
            id_produto=form.produto_id.data,
            id_filial=id_filial,
            id_tipo_venda=id_tipo_venda,
            id_modalidade_fin=id_modalidade_fin,
            possui_af=bool(form.possui_af.data),
            ano=ano_dn,
            mes=mes_dn,
        )
        if not dn_config:
            raise CalculoMargemError(
                "Não foi encontrada configuração de DN para a combinação informada. "
                "Revise previsão de entrega, produto, filial, tipo de venda e modalidade."
            )


        # Valor de venda (Célula E14)
        quantidade = form.quantidade.data or 0
        valor_unitario = Decimal(str(form.valor_venda_unitario.data or 0))
        valor_venda_total = _q2(Decimal(quantidade) * valor_unitario)

        if valor_venda_total <= 0:
            raise CalculoMargemError("Valor de venda total deve ser maior que zero.")


        # Parâmetros (impostos, comissão, juros, etc.)
        data_param = data_reserva
        p_icms_venda = self._obter_param_ou_default(
            PARAM_ICMS_VENDA, data_param, id_filial, id_tipo_venda, id_modalidade_fin,
            default=Decimal("0.03"),
        )
        p_piscofins_venda = self._obter_param_ou_default(
            PARAM_PISCOFINS_VENDA, data_param, id_filial, id_tipo_venda, id_modalidade_fin,
            default=Decimal("0.00"),
        )
        p_icms_piscofins_compra = self._obter_param_ou_default(
            PARAM_ICMS_PISCOFINS_COMPRA, data_param, id_filial, id_tipo_venda, id_modalidade_fin,
            default=Decimal("0.03"),
        )
        p_piscofins_compra = self._obter_param_ou_default(
            PARAM_PISCOFINS_COMPRA, data_param, id_filial, id_tipo_venda, id_modalidade_fin,
            default=Decimal("0.00"),
        )
        p_credito_imp_frete_compra = self._obter_param_ou_default(
            PARAM_CREDITO_IMP_FRETE_COMPRA, data_param, id_filial, id_tipo_venda, id_modalidade_fin,
            default=Decimal("0.00"),
        )
        p_credito_imp_frete_venda = self._obter_param_ou_default(
            PARAM_CREDITO_IMP_FRETE_VENDA, data_param, id_filial, id_tipo_venda, id_modalidade_fin,
            default=Decimal("0.00"),
        )
        p_pdi_garantia = self._obter_param_ou_default(
            PARAM_PDI_GARANTIA, data_param, id_filial, id_tipo_venda, id_modalidade_fin,
            default=Decimal("0.02"),
        )
        p_taxa_juros_mensal = self._obter_param_ou_default(
            PARAM_TAXA_JUROS_MENSAL, data_param, id_filial, id_tipo_venda, id_modalidade_fin,
            default=Decimal("0.0172"),
        )
        p_comissao_bruta = self._obter_param_ou_default(
            PARAM_COMISSAO_BRUTA, data_param, id_filial, id_tipo_venda, id_modalidade_fin,
            default=Decimal("0.006"),
        )
        p_comissao_dsr = self._obter_param_ou_default(
            PARAM_COMISSAO_DSR, data_param, id_filial, id_tipo_venda, id_modalidade_fin,
            default=Decimal("0.20"),
        )
        p_comissao_encargos = self._obter_param_ou_default(
            PARAM_COMISSAO_ENCARGOS, data_param, id_filial, id_tipo_venda, id_modalidade_fin,
            default=Decimal("0.3595"),
        )
        p_carta_fianca = self._obter_param_ou_default(
            PARAM_CARTA_FIANCA, data_param, id_filial, id_tipo_venda, id_modalidade_fin,
            default=Decimal("0.00"),
        )


        # Impostos de venda (Célula E16: ICMS + PIS/COFINS)
        impostos_venda_icms = _q2(valor_venda_total * p_icms_venda)
        impostos_venda_piscofins = _q2(valor_venda_total * p_piscofins_venda)
        impostos_venda_total = impostos_venda_icms + impostos_venda_piscofins


        # CMV (Célula E20), DN máquina (E22), impostos compra (E24), opcionais (E28), frete compra (E39), crédito imposto frete (E40), mão de obra (E37)
        valor_dn = _q2(dn_config.valor_dn)

        impostos_compra_icms_piscofins = _q2(valor_dn * p_icms_piscofins_compra)
        impostos_compra_piscofins = _q2(valor_dn * p_piscofins_compra)
        impostos_compra_total = impostos_compra_icms_piscofins + impostos_compra_piscofins

        valor_opcionais = _q2(Decimal(str(form.valor_opcionais.data or 0)))
        frete_compra = _q2(Decimal(str(form.frete_compra.data or 0)))
        custo_mao_obra = _q2(Decimal(str(form.custo_mao_obra.data or 0)))

        credito_impostos_frete_compra = _q2(frete_compra * p_credito_imp_frete_compra)

        cmv_total = (
            valor_dn
            - impostos_compra_total
            + valor_opcionais
            + frete_compra
            - credito_impostos_frete_compra
            + custo_mao_obra
        )
        cmv_total = _q2(cmv_total)


        # Custos adicionais e lucro bruto (E45, E46)
        contrato_manutencao = _q2(Decimal(str(form.contrato_manutencao.data or 0)))
        perc_pdi_garantia = Decimal(str(form.perc_pdi_garantia.data or p_pdi_garantia))
        valor_pdi_garantia = _q2(valor_venda_total * perc_pdi_garantia)

        lucro_bruto_valor = (
            valor_venda_total
            - impostos_venda_total
            - cmv_total
            - contrato_manutencao
            - valor_pdi_garantia
        )
        lucro_bruto_valor = _q2(lucro_bruto_valor)
        margem_bruta_percent = _q6(lucro_bruto_valor / valor_venda_total)


        # Fluxo de pagamento e custo financeiro (E51 / O21)
        perc_entrada = Decimal(str(form.perc_entrada.data or 0))
        if perc_entrada < 0 or perc_entrada > 1:
            raise CalculoMargemError("% de entrada deve estar entre 0 e 1.")

        base_financiado = valor_venda_total  # Simplificação: tudo é base
        valor_entrada = _q2(base_financiado * perc_entrada)
        qtd_parcelas = form.qtd_parcelas.data or 0
        prazo_primeira = form.prazo_primeira_parcela_dias.data or 0
        intervalo = form.intervalo_parcelas_dias.data or 30

        fluxo_parcelas = self._montar_fluxo_pagamento(
            base_financiado=base_financiado,
            valor_entrada=valor_entrada,
            qtd_parcelas=qtd_parcelas,
            prazo_primeira=prazo_primeira,
            intervalo=intervalo,
            taxa_juros_mensal=p_taxa_juros_mensal,
        )
        custo_financeiro_total = _q2(
            sum(parcela.custo_financeiro for parcela in fluxo_parcelas)
        )


        # Comissão do vendedor (E54-E57)
        comissao_bruta = _q2(valor_venda_total * p_comissao_bruta)
        comissao_dsr = _q2(comissao_bruta * p_comissao_dsr)
        comissao_encargos = _q2((comissao_bruta + comissao_dsr) * p_comissao_encargos)
        comissao_total = comissao_bruta + comissao_dsr + comissao_encargos


        # Carta fiança, frete venda e margem de contribuição (E59, E60)
        frete_venda = _q2(Decimal(str(form.frete_venda.data or 0)))
        credito_impostos_frete_venda = _q2(frete_venda * p_credito_imp_frete_venda)

        perc_carta_fianca = Decimal(str(form.perc_carta_fianca.data or p_carta_fianca))
        valor_carta_fianca = _q2(valor_venda_total * perc_carta_fianca)

        valor_cortesia = _q2(Decimal(str(form.valor_cortesia.data or 0)))

        margem_contrib_valor = (
            lucro_bruto_valor
            - frete_venda
            + credito_impostos_frete_venda
            - custo_financeiro_total
            - valor_carta_fianca
            - valor_cortesia
            - comissao_total
        )
        margem_contrib_valor = _q2(margem_contrib_valor)
        margem_contrib_percent = _q6(margem_contrib_valor / valor_venda_total)

        return CalculoMargemResultado(
            valor_venda_total=valor_venda_total,
            impostos_venda_total=impostos_venda_total,
            valor_dn=valor_dn,
            impostos_compra_total=impostos_compra_total,
            cmv_total=cmv_total,
            valor_opcionais=valor_opcionais,
            frete_compra=frete_compra,
            credito_impostos_frete_compra=credito_impostos_frete_compra,
            custo_mao_obra=custo_mao_obra,
            contrato_manutencao=contrato_manutencao,
            valor_pdi_garantia=valor_pdi_garantia,
            lucro_bruto_valor=lucro_bruto_valor,
            margem_bruta_percent=margem_bruta_percent,
            frete_venda=frete_venda,
            credito_impostos_frete_venda=credito_impostos_frete_venda,
            custo_financeiro_total=custo_financeiro_total,
            valor_carta_fianca=valor_carta_fianca,
            valor_cortesia=valor_cortesia,
            comissao_bruta=comissao_bruta,
            comissao_dsr=comissao_dsr,
            comissao_encargos=comissao_encargos,
            comissao_total=comissao_total,
            margem_contrib_valor=margem_contrib_valor,
            margem_contrib_percent=margem_contrib_percent,
            fluxo_parcelas=fluxo_parcelas,
        )

    # Helpers internos
    def _resolver_ano_mes_dn(self, data_ref: date) -> tuple[int, Optional[int]]:
        # Obtem o ano e mês para lookup de DN
        return data_ref.year, data_ref.month

    def _obter_param_ou_default(
        self,
        codigo: str,
        data_ref: date,
        id_filial: Optional[int],
        id_tipo_venda: Optional[int],
        id_modalidade_fin: Optional[int],
        default: Decimal,
    ) -> Decimal:
        valor = self._repo.obter_parametro_decimal(
            codigo=codigo,
            data_ref=data_ref,
            id_filial=id_filial,
            id_tipo_venda=id_tipo_venda,
            id_modalidade_fin=id_modalidade_fin,
        )
        if valor is None:
            current_app.logger.warning(
                "Parâmetro %s não encontrado, usando default=%s",
                codigo,
                default,
                extra={"event": "margem.parametro_default"},
            )
            return default
        return valor

    def _montar_fluxo_pagamento(
        self,
        *,
        base_financiado: Decimal,
        valor_entrada: Decimal,
        qtd_parcelas: int,
        prazo_primeira: int,
        intervalo: int,
        taxa_juros_mensal: Decimal,
    ) -> List[FluxoParcela]:
        # Fluxo de entrada + parcelas e calcula custo financeiro
        fluxo: List[FluxoParcela] = []

        if base_financiado <= 0 or qtd_parcelas < 0:
            return fluxo

        restante = base_financiado
        if valor_entrada > 0:
            restante -= valor_entrada
            fluxo.append(
                self._criar_parcela(
                    tipo_parcela=1,
                    numero_parcela=0,
                    prazo_dias=prazo_primeira,
                    valor_nominal=valor_entrada,
                    base_financiado=base_financiado,
                    taxa_juros_mensal=taxa_juros_mensal,
                )
            )

        valor_parcela = _q2(restante / qtd_parcelas) if qtd_parcelas > 0 else Decimal("0")

        for i in range(1, qtd_parcelas + 1):
            prazo = prazo_primeira + intervalo * i
            fluxo.append(
                self._criar_parcela(
                    tipo_parcela=2,
                    numero_parcela=i,
                    prazo_dias=prazo,
                    valor_nominal=valor_parcela,
                    base_financiado=base_financiado,
                    taxa_juros_mensal=taxa_juros_mensal,
                )
            )

        return fluxo

    def _criar_parcela(
        self,
        *,
        tipo_parcela: int,
        numero_parcela: int,
        prazo_dias: int,
        valor_nominal: Decimal,
        base_financiado: Decimal,
        taxa_juros_mensal: Decimal,
    ) -> FluxoParcela:
        if base_financiado <= 0:
            percentual_base = Decimal("0.0")
        else:
            percentual_base = _q6(valor_nominal / base_financiado)

        fator = (Decimal("1.0") + taxa_juros_mensal) ** (Decimal(prazo_dias) / Decimal(30))
        taxa_efetiva = _q6(fator - Decimal("1.0"))
        valor_presente = valor_nominal / (Decimal("1.0") + taxa_efetiva)
        custo_financeiro = valor_nominal - valor_presente

        return FluxoParcela(
            tipo_parcela=tipo_parcela,
            numero_parcela=numero_parcela,
            prazo_dias=prazo_dias,
            percentual_base=percentual_base,
            valor_nominal=_q2(valor_nominal),
            taxa_efetiva=taxa_efetiva,
            valor_presente=_q2(valor_presente),
            custo_financeiro=_q2(custo_financeiro),
        )
