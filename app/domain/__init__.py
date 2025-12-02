from __future__ import annotations

from .base import Base, TimestampMixin
from .cliente import ClienteMargemModel
from .filial import FilialMargemModel
from .produto import ProdutoMargemModel
from .vendedor import VendedorMargemModel
from .usuario import UsuarioMargemModel
from .tipo_venda import TipoVendaMargemModel
from .modalidade_financiamento import ModalidadeFinanciamentoMargemModel
from .banco_financiador import BancoFinanciadorMargemModel
from .config_dn import ConfigDNMargemModel
from .parametro_geral import ParametroGeralMargemModel
from .reserva import ReservaMargemModel
from .reserva_item import ReservaItemMargemModel
from .reserva_item_opcional import ReservaItemOpcionalMargemModel
from .reserva_item_fluxo import ReservaItemFluxoMargemModel
from .reserva_item_comissao import ReservaItemComissaoMargemModel
from .log_integracao_sap import LogIntegracaoSapMargemModel

__all__ = [
    "Base",
    "TimestampMixin",
    "ClienteMargemModel",
    "FilialMargemModel",
    "ProdutoMargemModel",
    "VendedorMargemModel",
    "UsuarioMargemModel",
    "TipoVendaMargemModel",
    "ModalidadeFinanciamentoMargemModel",
    "BancoFinanciadorMargemModel",
    "ConfigDNMargemModel",
    "ParametroGeralMargemModel",
    "ReservaMargemModel",
    "ReservaItemMargemModel",
    "ReservaItemOpcionalMargemModel",
    "ReservaItemFluxoMargemModel",
    "ReservaItemComissaoMargemModel",
    "LogIntegracaoSapMargemModel",
]
