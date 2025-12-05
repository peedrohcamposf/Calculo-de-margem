from __future__ import annotations

from decimal import Decimal
from typing import Optional

from .numeros import to_decimal, normalizar_numero_ptbr


# Impostos Venda = (ICMS * Valor de Venda) + (PIS/COFINS * Valor de Venda)
def calcular_impostos_venda(
    valor_venda,
    icms_percent,
    pis_cofins_percent,
) -> Decimal:

    base = to_decimal(valor_venda)
    icms = to_decimal(icms_percent) / Decimal("100")
    pis = to_decimal(pis_cofins_percent) / Decimal("100")

    total = base * (icms + pis)
    return total.quantize(Decimal("0.01"))


# Impostos Compra = (ICMS + PIS/COFINS * Valor da Máquina) + (PIS/COFINS * Valor da Máquina)
def calcular_impostos_compra(
    valor_maquina,
    icms_pis_percent,
    pis_cofins_percent,
) -> Optional[Decimal]:

    if valor_maquina is None:
        return None

    base = to_decimal(valor_maquina)
    if base == 0:
        return None

    icms_pis = base * (to_decimal(icms_pis_percent) / Decimal("100"))
    pis = base * (to_decimal(pis_cofins_percent) / Decimal("100"))

    total = (icms_pis + pis).quantize(Decimal("0.01"))
    return total


# Soma as horas informadas nos opcionais / agrega / desagrega
def calcular_total_horas_opcionais(lista_horas) -> Decimal:
    total = Decimal("0")
    if not lista_horas:
        return total

    for valor in lista_horas:
        normalizado = normalizar_numero_ptbr(valor)
        dec = to_decimal(normalizado)
        if dec < 0:
            continue
        total += dec

    return total.quantize(Decimal("0.01"))


# Horas * 200
def calcular_mao_obra_agrega_desagrega(horas) -> Decimal:
    base_horas = to_decimal(horas)
    total = base_horas * Decimal("200")
    return total.quantize(Decimal("0.01"))


# crédito = frete * (percentual / 100)
def calcular_credito_impostos(
    frete_compra,
    credito_percent,
) -> Optional[Decimal]:
    if frete_compra is None:
        return None

    base = to_decimal(frete_compra)
    percentual = to_decimal(credito_percent) / Decimal("100")

    total = base * percentual
    return total.quantize(Decimal("0.01"))


# Entrega Técnica / PDI / Garantia (R$) = (% / 100) * Valor de venda
def calcular_entrega_tecnica_pdi_garantia(
    valor_venda,
    percent,
) -> Optional[Decimal]:
    if valor_venda is None:
        return None

    base = to_decimal(valor_venda)
    percentual = to_decimal(percent) / Decimal("100")

    total = base * percentual
    return total.quantize(Decimal("0.01"))


# Carta fiança bancária (R$) = (% / 100) * Valor de venda
def calcular_carta_fianca(
    valor_venda,
    carta_fianca_percent,
) -> Optional[Decimal]:
    if valor_venda is None:
        return None

    base = to_decimal(valor_venda)
    percentual = to_decimal(carta_fianca_percent) / Decimal("100")

    total = base * percentual
    return total.quantize(Decimal("0.01"))


# CMV = Valor da máquina - Impostos de compra + Opcionais/Agrega/Desagrega + Frete compra - Crédito de impostos + Mão de obra agrega/desagrega
def calcular_cmv(
    valor_maquina,
    impostos_compra=None,
    opcionais_valor=None,
    frete_compra=None,
    credito_impostos_valor=None,
    mao_obra_valor=None,
) -> Optional[Decimal]:
    if valor_maquina is None:
        return None

    total = to_decimal(valor_maquina)

    if impostos_compra is not None:
        total -= to_decimal(impostos_compra)

    if opcionais_valor is not None:
        total += to_decimal(opcionais_valor)

    if frete_compra is not None:
        total += to_decimal(frete_compra)

    if credito_impostos_valor is not None:
        total -= to_decimal(credito_impostos_valor)

    if mao_obra_valor is not None:
        total += to_decimal(mao_obra_valor)

    return total.quantize(Decimal("0.01"))


# Lucro Bruto = Valor de Venda - Impostos de venda - CMV - Contrato de manutenção - Entrega técnica / PDI / Garantia
def calcular_lucro_bruto(
    valor_venda,
    impostos_venda=None,
    cmv=None,
    contrato_manutencao=None,
    entrega_tecnica_valor=None,
) -> Optional[Decimal]:
    if valor_venda is None:
        return None

    total = to_decimal(valor_venda)

    if impostos_venda is not None:
        total -= to_decimal(impostos_venda)

    if cmv is not None:
        total -= to_decimal(cmv)

    if contrato_manutencao is not None:
        total -= to_decimal(contrato_manutencao)

    if entrega_tecnica_valor is not None:
        total -= to_decimal(entrega_tecnica_valor)

    return total.quantize(Decimal("0.01"))


# Comissão Bruta (R$) = (% / 100) * Valor de venda
def calcular_comissao_bruta(
    valor_venda,
    comissao_percent,
) -> Optional[Decimal]:
    if valor_venda is None:
        return None

    base = to_decimal(valor_venda)
    percentual = to_decimal(comissao_percent) / Decimal("100")

    total = base * percentual
    return total.quantize(Decimal("0.01"))


# DSR (R$) = (% / 100) * Comissão Bruta
def calcular_dsr(
    comissao_bruta,
    dsr_percent,
) -> Optional[Decimal]:
    if comissao_bruta is None:
        return None

    base = to_decimal(comissao_bruta)
    percentual = to_decimal(dsr_percent) / Decimal("100")

    total = base * percentual
    return total.quantize(Decimal("0.01"))


# Encargos comissão (R$) = (% / 100) * (Comissão Bruta + DSR)
def calcular_encargos_comissao(
    comissao_bruta,
    dsr,
    encargos_percent,
) -> Optional[Decimal]:
    if comissao_bruta is None or dsr is None:
        return None

    soma_base = to_decimal(comissao_bruta) + to_decimal(dsr)
    percentual = to_decimal(encargos_percent) / Decimal("100")

    total = soma_base * percentual
    return total.quantize(Decimal("0.01"))


# Comissão total (R$) = Comissão Bruta + DSR + Encargos Comissão
def calcular_total_comissao_vendedor(
    comissao_bruta,
    dsr,
    encargos_comissao,
) -> Optional[Decimal]:
    if comissao_bruta is None and dsr is None and encargos_comissao is None:
        return None

    total = to_decimal(comissao_bruta) + to_decimal(dsr) + to_decimal(encargos_comissao)
    return total.quantize(Decimal("0.01"))


# % Comissão = (Comissão total / Valor de venda) * 100
def calcular_percentual_comissao_sobre_venda(
    total_comissao,
    valor_venda,
) -> Optional[Decimal]:
    if total_comissao is None or valor_venda is None:
        return None

    base_venda = to_decimal(valor_venda)
    if base_venda == 0:
        return None

    fracao = to_decimal(total_comissao) / base_venda
    percentual = fracao * Decimal("100")
    return percentual.quantize(Decimal("0.01"))


# Margem de Contribuição (R$) = Lucro Bruto - Frete venda + Crédito impostos (venda) - Custo financeiro - Carta fiança bancária - Cortesia - Comissão total do vendedor (R$)
def calcular_margem_contribuicao(
    lucro_bruto,
    frete_venda=None,
    credito_impostos_venda=None,
    custo_financeiro=None,
    carta_fianca=None,
    cortesia=None,
    comissao_total_vendedor=None,
) -> Optional[Decimal]:

    if lucro_bruto is None:
        return None

    total = to_decimal(lucro_bruto)

    if frete_venda is not None:
        total -= to_decimal(frete_venda)

    if credito_impostos_venda is not None:
        total += to_decimal(credito_impostos_venda)

    if custo_financeiro is not None:
        total -= to_decimal(custo_financeiro)

    if carta_fianca is not None:
        total -= to_decimal(carta_fianca)

    if cortesia is not None:
        total -= to_decimal(cortesia)

    if comissao_total_vendedor is not None:
        total -= to_decimal(comissao_total_vendedor)

    return total.quantize(Decimal("0.01"))


# %RB = (Margem de Contribuição / Valor de venda) * 100
def calcular_percentual_rb(
    margem_contribuicao,
    valor_venda,
) -> Optional[Decimal]:
    if margem_contribuicao is None or valor_venda is None:
        return None

    base_venda = to_decimal(valor_venda)
    if base_venda == 0:
        return None

    fracao = to_decimal(margem_contribuicao) / base_venda
    percentual = fracao * Decimal("100")
    return percentual.quantize(Decimal("0.01"))


# Margem %RB = (Lucro Bruto / Valor de venda) * 100
def calcular_percentual_margem_rb(
    lucro_bruto,
    valor_venda,
) -> Optional[Decimal]:
    if lucro_bruto is None or valor_venda is None:
        return None

    base_venda = to_decimal(valor_venda)
    if base_venda == 0:
        return None

    fracao = to_decimal(lucro_bruto) / base_venda
    percentual = fracao * Decimal("100")
    return percentual.quantize(Decimal("0.01"))
