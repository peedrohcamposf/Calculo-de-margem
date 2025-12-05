from __future__ import annotations

import re

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SelectField,
    DecimalField,
    DateField,
)
from wtforms.validators import (
    DataRequired,
    Optional,
    Length,
    NumberRange,
    ValidationError,
)

# Empresa x filiais permitidas
EMPRESA_FILIAIS = {
    "brasif": [
        "Belo Horizonte",
        "Brasilia",
        "Cuiabá",
        "Curitiba",
        "Goiânia",
        "Jundiaí",
        "Palmas",
        "Ribeirão Preto",
        "Rio de Janeiro",
        "Serra",
    ],
    "brasifagro": [
        "Luís Eduardo Magalhães",
        "Roda Velha",
        "Correntina",
        "Formosa do Rio Preto",
        "Bom Jesus",
    ],
}


class NovaReservaForm(FlaskForm):

    cliente = StringField(
        "Cliente",
        validators=[
            DataRequired(message="Informe o cliente."),
            Length(max=150),
        ],
    )

    # Controla quais filiais são válidas
    empresa = SelectField(
        "Empresa",
        choices=[
            ("", "Selecione..."),
            ("brasif", "Brasif"),
            ("brasifagro", "Brasif Agro"),
        ],
        validators=[DataRequired(message="Selecione a empresa.")],
    )

    filial = SelectField(
        "Filial",
        choices=[],
        validators=[DataRequired(message="Selecione a filial.")],
    )

    # Máquina do BD (tb_cm_maquinas)
    maquina_id = SelectField(
        "Modelo",
        coerce=int,
        choices=[],
        validators=[DataRequired(message="Selecione o modelo da máquina.")],
    )

    # Campo pra filtrar/buscar máquina (não obrigatório)
    filtro_maquina = StringField(
        "Buscar máquina",
        validators=[Optional(), Length(max=100)],
    )

    tipo_venda = SelectField(
        "Tipo de venda",
        choices=[
            ("", "Selecione..."),
            ("venda_financiada", "Venda financiada"),
            ("venda_vista", "Venda à vista"),
            ("venda_orgao_publico", "Venda a órgão público"),
            ("consorcio", "Consórcio"),
            ("cartao_bndes", "Cartão BNDES"),
            ("car", "Car"),
            ("a_definir", "A definir"),
        ],
        validators=[DataRequired(message="Informe o tipo de venda.")],
    )

    modalidade_financiamento = StringField(
        "Modalidade de financiamento",
        validators=[Optional(), Length(max=100)],
    )

    quantidade = DecimalField(
        "Quantidade",
        places=2,
        validators=[
            DataRequired(message="Informe a quantidade."),
            NumberRange(min=0.01, message="Quantidade deve ser maior que zero."),
        ],
    )

    data_reserva = DateField(
        "Data da Reserva",
        format="%Y-%m-%d",
        validators=[DataRequired(message="Informe a data da reserva.")],
        render_kw={"type": "date"},
    )

    banco_financiamento = StringField(
        "Banco do Financiamento",
        validators=[Optional(), Length(max=100)],
    )

    contato_banco = StringField(
        "Contato do Banco (nome / telefone)",
        validators=[Optional(), Length(max=150)],
    )

    nome_vendedor = StringField(
        "Nome do Vendedor",
        validators=[
            DataRequired(message="Informe o nome do vendedor."),
            Length(max=150),
        ],
    )

    possui_af = SelectField(
        "Possui AF?",
        choices=[
            ("", "Selecione..."),
            ("sim", "Sim"),
            ("nao", "Não"),
        ],
        validators=[DataRequired(message="Informe se possui AF.")],
    )

    previsao_entrega = StringField(
        "Previsão de Entrega (mm/aa)",
        validators=[Optional(), Length(max=7)],
        description="Use o formato mm/aa, por exemplo 10/25",
    )

    # Análise de Margens / Impostos Venda
    valor_venda = DecimalField(
        "Valor de venda",
        places=2,
        validators=[
            DataRequired(message="Informe o valor de venda."),
            NumberRange(min=0.01, message="Valor de venda deve ser maior que zero."),
        ],
    )

    icms_percent = DecimalField(
        "% ICMS (venda)",
        places=2,
        default=0,
        validators=[
            Optional(),
            NumberRange(min=0, max=100, message="ICMS deve estar entre 0% e 100%."),
        ],
    )

    pis_cofins_percent = DecimalField(
        "% PIS/COFINS (venda)",
        places=2,
        default=0,
        validators=[
            Optional(),
            NumberRange(
                min=0,
                max=100,
                message="PIS/COFINS deve estar entre 0% e 100%.",
            ),
        ],
    )

    # Análise de Margens / Impostos Compra
    icms_pis_compra_percent = DecimalField(
        "% ICMS + PIS/COFINS (compra)",
        places=2,
        default=0,
        validators=[
            Optional(),
            NumberRange(
                min=0,
                max=100,
                message="Percentual deve estar entre 0% e 100%.",
            ),
        ],
    )

    pis_cofins_compra_percent = DecimalField(
        "% PIS/COFINS (compra)",
        places=2,
        default=0,
        validators=[
            Optional(),
            NumberRange(
                min=0,
                max=100,
                message="Percentual deve estar entre 0% e 100%.",
            ),
        ],
    )

    # Mão de Obra Agrega/Desagrega
    mao_obra_agrega_desagrega_horas = DecimalField(
        "Mão de Obra Agrega/Desagrega (horas)",
        places=2,
        default=0,
        validators=[
            Optional(),
            NumberRange(
                min=0,
                message="As horas de mão de obra não podem ser negativas.",
            ),
        ],
    )

    # Crédito de Impostos (Frete de compra)
    frete_compra = DecimalField(
        "Frete compra (até Brasif)",
        places=2,
        default=0,
        validators=[
            Optional(),
            NumberRange(min=0, message="O frete não pode ser negativo."),
        ],
    )

    credito_impostos_percent = DecimalField(
        "% Crédito impostos",
        places=2,
        default=0,
        validators=[
            Optional(),
            NumberRange(
                min=0,
                max=100,
                message="Percentual de crédito deve estar entre 0% e 100%.",
            ),
        ],
    )

    # Frete Venda (até cliente)
    frete_venda = DecimalField(
        "Frete venda (de Brasif até cliente)",
        places=2,
        default=0,
        validators=[
            Optional(),
            NumberRange(min=0, message="O frete não pode ser negativo."),
        ],
    )

    credito_impostos_venda_percent = DecimalField(
        "% Crédito impostos (venda)",
        places=2,
        default=0,
        validators=[
            Optional(),
            NumberRange(
                min=0,
                max=100,
                message="Percentual de crédito deve estar entre 0% e 100%.",
            ),
        ],
    )

    # Contrato de manutenção (R$)
    contrato_manutencao = DecimalField(
        "Contrato de Manutenção",
        places=2,
        default=0,
        validators=[
            Optional(),
            NumberRange(
                min=0,
                message="O valor do contrato não pode ser negativo.",
            ),
        ],
    )

    # Entrega Técnica / PDI / Garantia (%)
    entrega_tecnica_pdi_garantia_percent = DecimalField(
        "% Entrega Técnica / PDI / Garantia",
        places=2,
        default=0,
        validators=[
            Optional(),
            NumberRange(
                min=0,
                max=100,
                message="Percentual deve estar entre 0% e 100%.",
            ),
        ],
    )

    # Custo financeiro (R$)
    custo_financeiro = DecimalField(
        "Custo financeiro",
        places=2,
        default=0,
        validators=[
            Optional(),
            NumberRange(
                min=0,
                message="O custo financeiro não pode ser negativo.",
            ),
        ],
    )

    # Carta fiança bancária (% sobre o valor de venda)
    carta_fianca_percent = DecimalField(
        "% Carta fiança bancária",
        places=2,
        default=0,
        validators=[
            Optional(),
            NumberRange(
                min=0,
                max=100,
                message="Percentual deve estar entre 0% e 100%.",
            ),
        ],
    )

    # Cortesia (R$)
    cortesia = DecimalField(
        "Cortesia",
        places=2,
        default=0,
        validators=[
            Optional(),
            NumberRange(
                min=0,
                message="O valor da cortesia não pode ser negativo.",
            ),
        ],
    )

    # Comissão do vendedor
    comissao_bruta_percent = DecimalField(
        "% Comissão bruta",
        places=2,
        default=0,
        validators=[
            Optional(),
            NumberRange(
                min=0,
                max=100,
                message="Percentual deve estar entre 0% e 100%.",
            ),
        ],
    )

    dsr_percent = DecimalField(
        "% DSR sobre comissão",
        places=2,
        default=0,
        validators=[
            Optional(),
            NumberRange(
                min=0,
                max=100,
                message="Percentual deve estar entre 0% e 100%.",
            ),
        ],
    )

    encargos_comissao_percent = DecimalField(
        "% Encargos sobre comissão + DSR",
        places=2,
        default=0,
        validators=[
            Optional(),
            NumberRange(
                min=0,
                max=100,
                message="Percentual deve estar entre 0% e 100%.",
            ),
        ],
    )

    # Validações customizadas
    def validate_filial(self, field: SelectField) -> None:
        empresa = self.empresa.data
        allowed = EMPRESA_FILIAIS.get(empresa, [])
        if empresa and allowed and field.data not in allowed:
            raise ValidationError("Filial inválida para a empresa selecionada.")

    def validate_previsao_entrega(self, field: StringField) -> None:
        if not field.data:
            return

        # Formato mm/aa, ex: 12/25
        if not re.match(r"^(0[1-9]|1[0-2])/\d{2}$", field.data.strip()):
            raise ValidationError("Use o formato mm/aa, por exemplo 12/25.")
