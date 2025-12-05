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
    # crédito = frete_compra * (percentual / 100)
    if frete_compra is None:
        return None

    base = _to_decimal(frete_compra)
    percentual = _to_decimal(credito_percent) / Decimal("100")

    total = base * percentual
    return total.quantize(Decimal("0.01"))
