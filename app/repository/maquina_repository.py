from __future__ import annotations

from typing import Sequence, Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.domain import MaquinaModel


class MaquinaRepository:

    def __init__(self, session: Session) -> None:
        self._session = session

    # Retorna a lista de máquinas, opcionalmente filtrada por texto livre (marca, modelo, código ou tipo)
    def buscar(self, filtro: Optional[str] = None) -> list[MaquinaModel]:

        query = self._session.query(MaquinaModel)

        if filtro:
            like = f"%{filtro}%"
            query = query.filter(
                or_(
                    MaquinaModel.marca.ilike(like),
                    MaquinaModel.modelo.ilike(like),
                    MaquinaModel.codigo.ilike(like),
                    MaquinaModel.tipo.ilike(like),
                )
            )

        return query.order_by(
            MaquinaModel.marca,
            MaquinaModel.modelo,
        ).all()

    # Obtem uma máquina pelo ID
    def obter_por_id(self, id_maquina: int | None) -> MaquinaModel | None:
        if id_maquina is None:
            return None
        return self._session.get(MaquinaModel, id_maquina)

    # Monta as opções para SelectField a partir da lista de máquinas
    @staticmethod
    def montar_choices_select(
        maquinas: Sequence[MaquinaModel],
    ) -> list[tuple[int, str]]:
        return [(m.id_maquina, f"{m.codigo} - {m.modelo}") for m in maquinas]
