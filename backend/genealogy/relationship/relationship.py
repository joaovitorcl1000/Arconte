"""Relações entre personagens do Arconte.

Entidade independente de interface, API e banco de dados.
Os extremos de uma relação são IDs de Character, não objetos Character.

Convenções:
* BIOLOGICAL_PARENT / ADOPTIVE_PARENT: source_id é responsável parental,
  target_id é filho(a). São relações direcionadas.
* MARRIAGE / PARTNERSHIP: os dois participantes têm papéis equivalentes.
  Seus UUIDs são armazenados em ordem canônica para facilitar comparação.
* start_year/end_year são opcionais e usam o calendário fictício da obra.

As validações que exigem o conjunto de personagens (existência dos IDs,
ciclos de ascendência, duplicidade e incompatibilidades cronológicas entre
personagens) pertencem ao futuro módulo de genealogia.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from uuid import UUID, uuid4


class RelationshipType(str, Enum):
    """Tipos de vínculos diretamente informados pelo escritor."""

    BIOLOGICAL_PARENT = "biological_parent"
    ADOPTIVE_PARENT = "adoptive_parent"
    MARRIAGE = "marriage"
    PARTNERSHIP = "partnership"

    @property
    def is_directed(self) -> bool:
        """Se a ordem dos participantes possui significado."""
        return self in {
            RelationshipType.BIOLOGICAL_PARENT,
            RelationshipType.ADOPTIVE_PARENT,
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class Relationship:
    """Vínculo entre dois personagens identificados por UUID.

    Para filiação, source_id -> target_id significa pai/mãe/responsável -> filho.
    Para casamento e união, a relação é simétrica e os IDs são normalizados.
    A entidade é imutável: edições podem ser feitas com dataclasses.replace().
    """

    source_id: UUID
    target_id: UUID
    type: RelationshipType
    start_year: int | None = None
    end_year: int | None = None
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        for field_name in ("id", "source_id", "target_id"):
            if not isinstance(getattr(self, field_name), UUID):
                raise TypeError(f"{field_name} deve ser um UUID.")

        if not isinstance(self.type, RelationshipType):
            raise TypeError("type deve ser um RelationshipType.")

        if self.source_id == self.target_id:
            raise ValueError("Um personagem não pode ter uma relação consigo mesmo.")

        for field_name in ("start_year", "end_year"):
            value = getattr(self, field_name)
            if value is not None and type(value) is not int:
                raise TypeError(f"{field_name} deve ser um inteiro ou None.")

        if (
            self.start_year is not None
            and self.end_year is not None
            and self.end_year < self.start_year
        ):
            raise ValueError("end_year não pode ser anterior a start_year.")

        # Casamento e parceria não têm orientação: A-B equivale a B-A.
        if not self.type.is_directed and self.source_id.int > self.target_id.int:
            original_source = self.source_id
            original_target = self.target_id
            object.__setattr__(self, "source_id", original_target)
            object.__setattr__(self, "target_id", original_source)

    @property
    def is_directed(self) -> bool:
        """Informa se a relação tem direção (ex.: responsável -> filho)."""
        return self.type.is_directed

    def connects(self, first_id: UUID, second_id: UUID) -> bool:
        """Verifica os participantes; respeita a direção quando houver."""
        if self.is_directed:
            return self.source_id == first_id and self.target_id == second_id
        return {self.source_id, self.target_id} == {first_id, second_id}
