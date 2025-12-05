from __future__ import annotations
from typing import List, Dict, Tuple


# Mapeamento estático de empresas x filiais
EMPRESA_FILIAIS: Dict[str, List[str]] = {
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

# Choices para o SelectField de Empresa no formulário
EMPRESA_CHOICES: List[Tuple[str, str]] = [
    ("", "Selecione..."),
    ("brasif", "Brasif"),
    ("brasifagro", "Brasif Agro"),
]


# Retorna a lista de filiais válidas para a empresa informada
def get_filiais_da_empresa(empresa: str) -> List[str]:
    return EMPRESA_FILIAIS.get(empresa, [])
