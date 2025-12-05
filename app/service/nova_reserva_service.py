from decimal import Decimal, InvalidOperation
from typing import Optional


def _to_decimal(value) -> Decimal:
    if value is None:
        return Decimal("0")
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal("0")


def _normalizar_numero_ptbr(value) -> str:
    if value is None:
        return "0"
    if isinstance(value, (int, float, Decimal)):
        return str(value)

    s = str(value).strip()
    if not s:
        return "0"

    s = s.replace(".", "").replace(",", ".")
    return s


def calcular_impostos_venda(
    valor_venda,
    icms_percent,
    pis_cofins_percent,
) -> Decimal:
    # Impostos Venda = (ICMS * Valor de Venda) + (PIS/COFINS * Valor de Venda)

    base = _to_decimal(valor_venda)
    icms = _to_decimal(icms_percent) / Decimal("100")
    pis = _to_decimal(pis_cofins_percent) / Decimal("100")

    total = base * (icms + pis)
    return total.quantize(Decimal("0.01"))


def calcular_impostos_compra(
    valor_maquina,
    icms_pis_percent,
    pis_cofins_percent,
) -> Optional[Decimal]:
    # Impostos Compra = (ICMS + PIS/COFINS * Valor da Máquina) + (PIS/COFINS * Valor da Máquina)

    if valor_maquina is None:
        return None

    base = _to_decimal(valor_maquina)
    if base == 0:
        return None

    icms_pis = base * (_to_decimal(icms_pis_percent) / Decimal("100"))
    pis = base * (_to_decimal(pis_cofins_percent) / Decimal("100"))

    total = (icms_pis + pis).quantize(Decimal("0.01"))
    return total


def calcular_total_horas_opcionais(lista_horas) -> Decimal:
    # Soma as horas informadas nos opcionais / agrega / desagrega
    total = Decimal("0")
    if not lista_horas:
        return total

    for valor in lista_horas:
        normalizado = _normalizar_numero_ptbr(valor)
        dec = _to_decimal(normalizado)
        if dec < 0:
            continue
        total += dec

    return total.quantize(Decimal("0.01"))


def calcular_mao_obra_agrega_desagrega(horas) -> Decimal:
    # Horas * 200
    base_horas = _to_decimal(horas)
    total = base_horas * Decimal("200")
    return total.quantize(Decimal("0.01"))


def calcular_credito_impostos(
    frete_compra,
    credito_percent,
) -> Optional[Decimal]:
    # crédito = frete * (percentual / 100)
    if frete_compra is None:
        return None

    base = _to_decimal(frete_compra)
    percentual = _to_decimal(credito_percent) / Decimal("100")

    total = base * percentual
    return total.quantize(Decimal("0.01"))


def calcular_entrega_tecnica_pdi_garantia(
    valor_venda,
    percent,
) -> Optional[Decimal]:
    # Entrega Técnica / PDI / Garantia (R$) = (% / 100) * Valor de venda
    if valor_venda is None:
        return None

    base = _to_decimal(valor_venda)
    percentual = _to_decimal(percent) / Decimal("100")

    total = base * percentual
    return total.quantize(Decimal("0.01"))


def calcular_carta_fianca(
    valor_venda,
    carta_fianca_percent,
) -> Optional[Decimal]:
    # Carta fiança bancária (R$) = (% / 100) * Valor de venda
    if valor_venda is None:
        return None

    base = _to_decimal(valor_venda)
    percentual = _to_decimal(carta_fianca_percent) / Decimal("100")

    total = base * percentual
    return total.quantize(Decimal("0.01"))


def calcular_cmv(
    valor_maquina,
    impostos_compra=None,
    opcionais_valor=None,
    frete_compra=None,
    credito_impostos_valor=None,
    mao_obra_valor=None,
) -> Optional[Decimal]:
    # CMV = Valor da máquina - Impostos de compra + Opcionais/Agrega/Desagrega + Frete compra - Crédito de impostos + Mão de obra agrega/desagrega
    if valor_maquina is None:
        return None

    total = _to_decimal(valor_maquina)

    if impostos_compra is not None:
        total -= _to_decimal(impostos_compra)

    if opcionais_valor is not None:
        total += _to_decimal(opcionais_valor)

    if frete_compra is not None:
        total += _to_decimal(frete_compra)

    if credito_impostos_valor is not None:
        total -= _to_decimal(credito_impostos_valor)

    if mao_obra_valor is not None:
        total += _to_decimal(mao_obra_valor)

    return total.quantize(Decimal("0.01"))


def calcular_lucro_bruto(
    valor_venda,
    impostos_venda=None,
    cmv=None,
    contrato_manutencao=None,
    entrega_tecnica_valor=None,
) -> Optional[Decimal]:
    # Lucro Bruto = Valor de Venda - Impostos de venda - CMV - Contrato de manutenção - Entrega técnica / PDI / Garantia (R$)
    if valor_venda is None:
        return None

    total = _to_decimal(valor_venda)

    if impostos_venda is not None:
        total -= _to_decimal(impostos_venda)

    if cmv is not None:
        total -= _to_decimal(cmv)

    if contrato_manutencao is not None:
        total -= _to_decimal(contrato_manutencao)

    if entrega_tecnica_valor is not None:
        total -= _to_decimal(entrega_tecnica_valor)

    return total.quantize(Decimal("0.01"))


def calcular_comissao_bruta(
    valor_venda,
    comissao_percent,
) -> Optional[Decimal]:
    # Comissão Bruta (R$) = (% / 100) * Valor de venda
    if valor_venda is None:
        return None

    base = _to_decimal(valor_venda)
    percentual = _to_decimal(comissao_percent) / Decimal("100")

    total = base * percentual
    return total.quantize(Decimal("0.01"))


def calcular_dsr(
    comissao_bruta,
    dsr_percent,
) -> Optional[Decimal]:
    # DSR (R$) = (% / 100) * Comissão Bruta
    if comissao_bruta is None:
        return None

    base = _to_decimal(comissao_bruta)
    percentual = _to_decimal(dsr_percent) / Decimal("100")

    total = base * percentual
    return total.quantize(Decimal("0.01"))


def calcular_encargos_comissao(
    comissao_bruta,
    dsr,
    encargos_percent,
) -> Optional[Decimal]:
    # Encargos comissão (R$) = (% / 100) * (Comissão Bruta + DSR)
    if comissao_bruta is None or dsr is None:
        return None

    soma_base = _to_decimal(comissao_bruta) + _to_decimal(dsr)
    percentual = _to_decimal(encargos_percent) / Decimal("100")

    total = soma_base * percentual
    return total.quantize(Decimal("0.01"))


def calcular_total_comissao_vendedor(
    comissao_bruta,
    dsr,
    encargos_comissao,
) -> Optional[Decimal]:

    # Comissão total (R$) = Comissão Bruta + DSR + Encargos Comissão
    if comissao_bruta is None and dsr is None and encargos_comissao is None:
        return None

    total = (
        _to_decimal(comissao_bruta) + _to_decimal(dsr) + _to_decimal(encargos_comissao)
    )
    return total.quantize(Decimal("0.01"))


def calcular_percentual_comissao_sobre_venda(
    total_comissao,
    valor_venda,
) -> Optional[Decimal]:
    # % Comissão = (Comissão total / Valor de venda) * 100
    if total_comissao is None or valor_venda is None:
        return None

    base_venda = _to_decimal(valor_venda)
    if base_venda == 0:
        return None

    fracao = _to_decimal(total_comissao) / base_venda
    percentual = fracao * Decimal("100")
    return percentual.quantize(Decimal("0.01"))


def calcular_margem_contribuicao(
    lucro_bruto,
    frete_venda=None,
    credito_impostos_venda=None,
    custo_financeiro=None,
    carta_fianca=None,
    cortesia=None,
    comissao_total_vendedor=None,
) -> Optional[Decimal]:
    # Margem de Contribuição (R$) = Lucro Bruto - Frete venda + Crédito de impostos (venda) - Custo financeiro - Carta fiança bancária - Cortesia - Comissão total do vendedor (R$)
    if lucro_bruto is None:
        return None

    total = _to_decimal(lucro_bruto)

    if frete_venda is not None:
        total -= _to_decimal(frete_venda)

    if credito_impostos_venda is not None:
        total += _to_decimal(credito_impostos_venda)

    if custo_financeiro is not None:
        total -= _to_decimal(custo_financeiro)

    if carta_fianca is not None:
        total -= _to_decimal(carta_fianca)

    if cortesia is not None:
        total -= _to_decimal(cortesia)

    if comissao_total_vendedor is not None:
        total -= _to_decimal(comissao_total_vendedor)

    return total.quantize(Decimal("0.01"))


def calcular_percentual_rb(
    margem_contribuicao,
    valor_venda,
) -> Optional[Decimal]:
    # %RB = (Margem de Contribuição / Valor de venda) * 100
    if margem_contribuicao is None or valor_venda is None:
        return None

    base_venda = _to_decimal(valor_venda)
    if base_venda == 0:
        return None

    fracao = _to_decimal(margem_contribuicao) / base_venda
    percentual = fracao * Decimal("100")
    return percentual.quantize(Decimal("0.01"))


def calcular_percentual_margem_rb(
    lucro_bruto,
    valor_venda,
) -> Optional[Decimal]:
    # Margem %RB = (Lucro Bruto / Valor de venda) * 100
    if lucro_bruto is None or valor_venda is None:
        return None

    base_venda = _to_decimal(valor_venda)
    if base_venda == 0:
        return None

    fracao = _to_decimal(lucro_bruto) / base_venda
    percentual = fracao * Decimal("100")
    return percentual.quantize(Decimal("0.01"))
