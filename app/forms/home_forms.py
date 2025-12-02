from __future__ import annotations

from datetime import date
from decimal import Decimal

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateField,
    DecimalField,
    IntegerField,
    SelectField,
    SubmitField,
)
from wtforms.validators import DataRequired, NumberRange, Optional as OptionalValidator


class NovaReservaForm(FlaskForm):

    # Cabeçalho / dimensões comerciais
    cliente_id = SelectField(
        "Cliente",
        coerce=int,
        validators=[DataRequired(message="Selecione um cliente.")],
    )

    filial_id = SelectField(
        "Filial",
        coerce=int,
        validators=[DataRequired(message="Selecione uma filial.")],
    )

    produto_id = SelectField(
        "Produto / Modelo",
        coerce=int,
        validators=[DataRequired(message="Selecione um produto.")],
    )

    tipo_venda_id = SelectField(
        "Tipo de venda",
        coerce=int,
        validators=[DataRequired(message="Selecione o tipo de venda.")],
    )

    modalidade_fin_id = SelectField(
        "Modalidade de financiamento",
        coerce=int,
        validators=[OptionalValidator()],
    )

    banco_financiador_id = SelectField(
        "Banco financiador",
        coerce=int,
        validators=[OptionalValidator()],
    )

    quantidade = IntegerField(
        "Quantidade",
        default=1,
        validators=[
            DataRequired(message="Informe a quantidade."),
            NumberRange(min=1, message="Quantidade deve ser pelo menos 1."),
        ],
    )

    valor_venda_unitario = DecimalField(
        "Valor de venda unitário",
        places=2,
        rounding=None,
        validators=[
            DataRequired(message="Informe o valor de venda unitário."),
            NumberRange(min=0, message="Valor de venda deve ser positivo."),
        ],
    )

    data_reserva = DateField(
        "Data da reserva",
        default=date.today,
        validators=[DataRequired(message="Informe a data da reserva.")],
        format="%Y-%m-%d",
    )

    previsao_entrega = DateField(
        "Previsão de entrega",
        validators=[OptionalValidator()],
        format="%Y-%m-%d",
    )

    possui_af = BooleanField("Possui AF?")

    # Bloco de financiamento / fluxo de pagamento, (entrada + parcelas, para custo financeiro tipo planilha)
    perc_entrada = DecimalField(
        "% de entrada sobre o valor de venda",
        places=4,
        rounding=None,
        default=Decimal("0.00"),
        validators=[
            NumberRange(min=0, max=1, message="Informe um valor entre 0 e 1."),
            OptionalValidator(),
        ],
        description="Ex.: 0,10 = 10% de entrada.",
    )

    qtd_parcelas = IntegerField(
        "Quantidade de parcelas",
        default=5,
        validators=[
            DataRequired(message="Informe a quantidade de parcelas."),
            NumberRange(min=0, max=120, message="Quantidade de parcelas inválida."),
        ],
    )

    prazo_primeira_parcela_dias = IntegerField(
        "Prazo (dias) da primeira parcela",
        default=30,
        validators=[
            DataRequired(message="Informe o prazo da primeira parcela."),
            NumberRange(min=0, max=3650, message="Prazo inválido."),
        ],
    )

    intervalo_parcelas_dias = IntegerField(
        "Intervalo padrão entre parcelas (dias)",
        default=30,
        validators=[
            DataRequired(message="Informe o intervalo entre parcelas."),
            NumberRange(min=0, max=3650, message="Intervalo inválido."),
        ],
    )

    # Custos adicionais (opcionais, fretes, PDI, comissão etc.)
    valor_opcionais = DecimalField(
        "Opcionais / Agrega / Desagrega (total)",
        places=2,
        rounding=None,
        default=Decimal("0.00"),
        validators=[
            NumberRange(min=0, message="Valor deve ser positivo."),
            OptionalValidator(),
        ],
    )

    custo_mao_obra = DecimalField(
        "Mão de obra agrega / desagrega",
        places=2,
        rounding=None,
        default=Decimal("0.00"),
        validators=[
            NumberRange(min=0, message="Valor deve ser positivo."),
            OptionalValidator(),
        ],
    )

    frete_compra = DecimalField(
        "Frete compra (até Brasif)",
        places=2,
        rounding=None,
        default=Decimal("0.00"),
        validators=[
            NumberRange(min=0, message="Valor deve ser positivo."),
            OptionalValidator(),
        ],
    )

    frete_venda = DecimalField(
        "Frete venda (até cliente)",
        places=2,
        rounding=None,
        default=Decimal("0.00"),
        validators=[
            NumberRange(min=0, message="Valor deve ser positivo."),
            OptionalValidator(),
        ],
    )

    contrato_manutencao = DecimalField(
        "Contrato de manutenção",
        places=2,
        rounding=None,
        default=Decimal("0.00"),
        validators=[
            NumberRange(min=0, message="Valor deve ser positivo."),
            OptionalValidator(),
        ],
    )

    perc_pdi_garantia = DecimalField(
        "% Entrega técnica / PDI / Garantia",
        places=6,
        rounding=None,
        default=Decimal("0.00"),
        validators=[
            NumberRange(min=0, max=1, message="Informe um valor entre 0 e 1."),
            OptionalValidator(),
        ],
        description="Ex.: 0,02 = 2% sobre o valor de venda.",
    )

    perc_carta_fianca = DecimalField(
        "% Carta fiança",
        places=6,
        rounding=None,
        default=Decimal("0.00"),
        validators=[
            NumberRange(min=0, max=1, message="Informe um valor entre 0 e 1."),
            OptionalValidator(),
        ],
        description="Ex.: 0,01 = 1% sobre o valor de venda.",
    )

    valor_cortesia = DecimalField(
        "Cortesia (valor)",
        places=2,
        rounding=None,
        default=Decimal("0.00"),
        validators=[
            NumberRange(min=0, message="Valor deve ser positivo."),
            OptionalValidator(),
        ],
    )

    submit = SubmitField("Calcular margem")
