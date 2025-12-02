from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Mapping, Optional

from sqlalchemy import MetaData, Table, select, or_, case
from sqlalchemy.orm import Session


# Dataclasses
@dataclass(frozen=True)
class DnConfig:

    # Configuração de Desconto Negociado (tb_cm_margem_config_dn)
    id_dn: int
    valor_dn: Decimal
    ano: int
    mes: Optional[int]


class MargemRepository:

    def __init__(self, session: Session) -> None:
        self._session = session

        metadata = MetaData()
        bind = session.get_bind()

        self._cliente = Table(
            "tb_cm_margem_cliente",
            metadata,
            autoload_with=bind,
        )
        self._filial = Table(
            "tb_cm_margem_filial",
            metadata,
            autoload_with=bind,
        )
        self._produto = Table(
            "tb_cm_margem_produto",
            metadata,
            autoload_with=bind,
        )
        self._tipo_venda = Table(
            "tb_cm_margem_tipo_venda",
            metadata,
            autoload_with=bind,
        )
        self._modalidade_fin = Table(
            "tb_cm_margem_modalidade_financiamento",
            metadata,
            autoload_with=bind,
        )
        self._banco = Table(
            "tb_cm_margem_banco_financiador",
            metadata,
            autoload_with=bind,
        )
        self._parametro_geral = Table(
            "tb_cm_margem_parametro_geral",
            metadata,
            autoload_with=bind,
        )
        self._config_dn = Table(
            "tb_cm_margem_config_dn",
            metadata,
            autoload_with=bind,
        )

    # Listas para preencher selects do formulário
    def listar_clientes_ativos(self) -> list[Mapping]:
        stmt = (
            select(
                self._cliente.c.id_cliente,
                self._cliente.c.codigo_sap,
                self._cliente.c.razao_social,
            )
            .where(self._cliente.c.ativo == 1)
            .order_by(self._cliente.c.razao_social_ci)
        )
        return list(self._session.execute(stmt).mappings().all())

    def listar_filiais_ativas(self) -> list[Mapping]:
        stmt = (
            select(
                self._filial.c.id_filial,
                self._filial.c.codigo_sap,
                self._filial.c.nome,
            )
            .where(self._filial.c.ativo == 1)
            .order_by(self._filial.c.nome_ci)
        )
        return list(self._session.execute(stmt).mappings().all())

    def listar_produtos_ativos(self) -> list[Mapping]:
        stmt = (
            select(
                self._produto.c.id_produto,
                self._produto.c.codigo_sap,
                self._produto.c.descricao,
            )
            .where(self._produto.c.ativo == 1)
            .order_by(self._produto.c.descricao_ci)
        )
        return list(self._session.execute(stmt).mappings().all())

    def listar_tipos_venda_ativos(self) -> list[Mapping]:
        stmt = (
            select(
                self._tipo_venda.c.id_tipo_venda,
                self._tipo_venda.c.nome,
            )
            .where(self._tipo_venda.c.ativo == 1)
            .order_by(self._tipo_venda.c.nome)
        )
        return list(self._session.execute(stmt).mappings().all())

    def listar_modalidades_ativas(self) -> list[Mapping]:
        stmt = (
            select(
                self._modalidade_fin.c.id_modalidade_fin,
                self._modalidade_fin.c.nome,
            )
            .where(self._modalidade_fin.c.ativo == 1)
            .order_by(self._modalidade_fin.c.nome)
        )
        return list(self._session.execute(stmt).mappings().all())

    def listar_bancos_ativos(self) -> list[Mapping]:
        stmt = (
            select(
                self._banco.c.id_banco_financiador,
                self._banco.c.nome,
            )
            .where(self._banco.c.ativo == 1)
            .order_by(self._banco.c.nome)
        )
        return list(self._session.execute(stmt).mappings().all())

    # Parâmetros de negócio (tb_cm_margem_parametro_geral)
    def obter_parametro_decimal(
        self,
        codigo: str,
        data_ref: date,
        id_filial: Optional[int],
        id_tipo_venda: Optional[int],
        id_modalidade_fin: Optional[int],
    ) -> Optional[Decimal]:

        p = self._parametro_geral

        stmt = select(p.c.valor_decimal).where(
            p.c.codigo == codigo,
            p.c.ativo == 1,
            p.c.data_inicio <= data_ref,
            or_(p.c.data_fim.is_(None), p.c.data_fim >= data_ref),
        )

        if id_filial is not None:
            stmt = stmt.where(or_(p.c.id_filial.is_(None), p.c.id_filial == id_filial))
        if id_tipo_venda is not None:
            stmt = stmt.where(
                or_(p.c.id_tipo_venda.is_(None), p.c.id_tipo_venda == id_tipo_venda)
            )
        if id_modalidade_fin is not None:
            stmt = stmt.where(
                or_(
                    p.c.id_modalidade_fin.is_(None),
                    p.c.id_modalidade_fin == id_modalidade_fin,
                )
            )

        # Score de especificidade, quanto mais campos não nulos, maior
        score = (
            case((p.c.id_filial.is_(None), 0), else_=1)
            + case((p.c.id_tipo_venda.is_(None), 0), else_=1)
            + case((p.c.id_modalidade_fin.is_(None), 0), else_=1)
        )

        stmt = stmt.order_by(score.desc(), p.c.data_inicio.desc()).limit(1)

        result = self._session.execute(stmt).scalar_one_or_none()
        if result is None:
            return None

        return Decimal(str(result))

    # Configuração de desconto negociado (DN)
    def obter_config_dn(
        self,
        *,
        id_produto: int,
        id_filial: int,
        id_tipo_venda: int,
        id_modalidade_fin: Optional[int],
        possui_af: bool,
        ano: int,
        mes: Optional[int],
    ) -> Optional[DnConfig]:

        c = self._config_dn

        id_modalidade_fin_zero = id_modalidade_fin or 0
        mes_zero = mes or 0

        stmt = (
            select(
                c.c.id_dn,
                c.c.valor_dn,
                c.c.ano,
                c.c.mes,
            )
            .where(
                c.c.id_produto == id_produto,
                c.c.id_filial == id_filial,
                c.c.id_tipo_venda == id_tipo_venda,
                c.c.id_modalidade_fin_zero == id_modalidade_fin_zero,
                c.c.possui_af == (1 if possui_af else 0),
                c.c.ano == ano,
                c.c.mes_zero == mes_zero,
            )
            .order_by(c.c.data_referencia.desc())
            .limit(1)
        )

        row = self._session.execute(stmt).first()
        if not row:
            return None

        return DnConfig(
            id_dn=row.id_dn,
            valor_dn=Decimal(str(row.valor_dn)),
            ano=row.ano,
            mes=row.mes,
        )
