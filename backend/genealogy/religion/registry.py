"""Registro de religiões, divindades e doutrinas do Arconte.

Os dados são independentes de Project e de personagens/organizações nesta etapa.
Uma religião pode estar associada a várias divindades, e a mesma divindade a
várias religiões. A associação não implica necessariamente adoração: pode
significar reconhecimento, mitologia compartilhada ou referência histórica.

``to_dict``/``from_dict`` fazem intercâmbio JSON independente; NÃO alteram o
schema de ``storage.py``. A associação com ordens, templos e personagens será
realizada quando Project e OrganizationRegistry forem integrados.
"""
from __future__ import annotations

from dataclasses import replace
from typing import Any
from collections.abc import Mapping
from uuid import UUID

from religion.deity import Deity
from religion.doctrine import Doctrine, DoctrineCategory
from religion.religion import Religion, _json_uuid, _optional_year, _parse_mapping, _uuid


def _sorted_by_name(items: Any) -> tuple[Any, ...]:
    return tuple(sorted(items, key=lambda value: (value.name.casefold(), str(value.id))))


class ReligionRegistry:
    """Agrega religiões, divindades e doutrinas, validando referências.

    - Fundadores são UUIDs e ainda NÃO são validados contra personagens.
    - Excluir religião remove suas doutrinas e associações com divindades;
      excluir divindade apenas desfaz suas associações.
    - Excluir uma religião ancestral, por padrão, é proibido enquanto houver
      religiões derivadas. Use ``on_children='detach'`` conscientemente.
    """

    def __init__(self) -> None:
        self._religions: dict[UUID, Religion] = {}
        self._deities: dict[UUID, Deity] = {}
        self._doctrines: dict[UUID, Doctrine] = {}
        self._religion_deities: dict[UUID, set[UUID]] = {}

    # -- Religiões ------------------------------------------------------
    def add_religion(self, religion: Religion) -> None:
        if not isinstance(religion, Religion):
            raise TypeError("religion deve ser Religion.")
        if religion.id in self._religions:
            raise ValueError("Religião com UUID já cadastrado.")
        self._check_parent(religion)
        self._religions[religion.id] = religion
        self._religion_deities[religion.id] = set()

    def update_religion(self, religion: Religion) -> None:
        if not isinstance(religion, Religion):
            raise TypeError("religion deve ser Religion.")
        self.get_religion(religion.id)
        self._check_parent(religion)
        for doctrine in self._doctrines.values():
            if doctrine.religion_id == religion.id:
                self._check_doctrine_period(doctrine, religion)
        self._religions[religion.id] = religion

    def get_religion(self, religion_id: UUID) -> Religion:
        _uuid(religion_id, "religion_id")
        return self._religions[religion_id]

    def get_all_religions(self) -> tuple[Religion, ...]:
        return _sorted_by_name(self._religions.values())

    def get_derived_religions(self, parent_id: UUID, *, recursive: bool = False) -> tuple[Religion, ...]:
        self.get_religion(parent_id)
        if type(recursive) is not bool:
            raise TypeError("recursive deve ser bool.")
        found: set[UUID] = set()
        queue = [parent_id]
        while queue:
            current = queue.pop()
            for religion in self._religions.values():
                if religion.parent_religion_id == current and religion.id not in found:
                    found.add(religion.id)
                    if recursive:
                        queue.append(religion.id)
        return _sorted_by_name(self._religions[oid] for oid in found)

    def remove_religion(self, religion_id: UUID, *, on_children: str = "reject") -> Religion:
        religion = self.get_religion(religion_id)
        if on_children not in ("reject", "detach"):
            raise ValueError("on_children deve ser 'reject' ou 'detach'.")
        children = self.get_derived_religions(religion_id)
        if children and on_children == "reject":
            raise ValueError("Esta religião possui religiões derivadas.")
        if children:
            for child in children:
                self._religions[child.id] = replace(child, parent_religion_id=None)
        for did in tuple(self._doctrines):
            if self._doctrines[did].religion_id == religion_id:
                del self._doctrines[did]
        del self._religion_deities[religion_id]
        del self._religions[religion_id]
        return religion

    def _check_parent(self, religion: Religion) -> None:
        parent = religion.parent_religion_id
        if parent is None:
            return
        if parent == religion.id:
            raise ValueError("Uma religião não pode derivar de si própria.")
        if parent not in self._religions:
            raise ValueError("Religião de origem inexistente.")
        seen: set[UUID] = {religion.id}
        current = parent
        while current is not None:
            if current in seen:
                raise ValueError("Ciclo nas religiões derivadas.")
            seen.add(current)
            if current not in self._religions:
                raise ValueError("Religião de origem inexistente.")
            current = self._religions[current].parent_religion_id

    # -- Divindades -----------------------------------------------------
    def add_deity(self, deity: Deity) -> None:
        if not isinstance(deity, Deity):
            raise TypeError("deity deve ser Deity.")
        if deity.id in self._deities:
            raise ValueError("Divindade com UUID já cadastrado.")
        self._deities[deity.id] = deity

    def update_deity(self, deity: Deity) -> None:
        if not isinstance(deity, Deity):
            raise TypeError("deity deve ser Deity.")
        self.get_deity(deity.id)
        self._deities[deity.id] = deity

    def get_deity(self, deity_id: UUID) -> Deity:
        _uuid(deity_id, "deity_id")
        return self._deities[deity_id]

    def get_all_deities(self) -> tuple[Deity, ...]:
        return _sorted_by_name(self._deities.values())

    def remove_deity(self, deity_id: UUID) -> Deity:
        deity = self.get_deity(deity_id)
        for linked in self._religion_deities.values():
            linked.discard(deity_id)
        del self._deities[deity_id]
        return deity

    def link_deity(self, religion_id: UUID, deity_id: UUID) -> None:
        """Associa uma divindade a uma tradição, sem definir forma de culto."""
        self.get_religion(religion_id)
        self.get_deity(deity_id)
        if deity_id in self._religion_deities[religion_id]:
            raise ValueError("Associação entre religião e divindade já existe.")
        self._religion_deities[religion_id].add(deity_id)

    def unlink_deity(self, religion_id: UUID, deity_id: UUID) -> None:
        self.get_religion(religion_id)
        self.get_deity(deity_id)
        if deity_id not in self._religion_deities[religion_id]:
            raise KeyError("Associação entre religião e divindade inexistente.")
        self._religion_deities[religion_id].remove(deity_id)

    def get_deities(self, religion_id: UUID) -> tuple[Deity, ...]:
        self.get_religion(religion_id)
        return _sorted_by_name(self._deities[did] for did in self._religion_deities[religion_id])

    def get_religions_for_deity(self, deity_id: UUID) -> tuple[Religion, ...]:
        self.get_deity(deity_id)
        return _sorted_by_name(
            religion for religion in self._religions.values()
            if deity_id in self._religion_deities[religion.id]
        )

    # -- Doutrinas ------------------------------------------------------
    def _check_doctrine_period(self, doctrine: Doctrine, religion: Religion) -> None:
        if religion.founded_year is not None:
            for name in ("start_year", "end_year"):
                year = getattr(doctrine, name)
                if year is not None and year < religion.founded_year:
                    raise ValueError("Doutrina datada de antes da fundação da religião.")
        if religion.ended_year is not None:
            for name in ("start_year", "end_year"):
                year = getattr(doctrine, name)
                if year is not None and year > religion.ended_year:
                    raise ValueError("Doutrina datada após o fim da religião.")

    def add_doctrine(self, doctrine: Doctrine) -> None:
        if not isinstance(doctrine, Doctrine):
            raise TypeError("doctrine deve ser Doctrine.")
        if doctrine.id in self._doctrines:
            raise ValueError("Doutrina com UUID já cadastrado.")
        religion = self.get_religion(doctrine.religion_id)
        self._check_doctrine_period(doctrine, religion)
        self._doctrines[doctrine.id] = doctrine

    def update_doctrine(self, doctrine: Doctrine) -> None:
        if not isinstance(doctrine, Doctrine):
            raise TypeError("doctrine deve ser Doctrine.")
        self.get_doctrine(doctrine.id)
        religion = self.get_religion(doctrine.religion_id)
        self._check_doctrine_period(doctrine, religion)
        self._doctrines[doctrine.id] = doctrine

    def get_doctrine(self, doctrine_id: UUID) -> Doctrine:
        _uuid(doctrine_id, "doctrine_id")
        return self._doctrines[doctrine_id]

    def remove_doctrine(self, doctrine_id: UUID) -> Doctrine:
        doctrine = self.get_doctrine(doctrine_id)
        del self._doctrines[doctrine_id]
        return doctrine

    def get_doctrines(
        self, *, religion_id: UUID | None = None,
        category: DoctrineCategory | None = None, at_year: int | None = None,
    ) -> tuple[Doctrine, ...]:
        if religion_id is not None:
            self.get_religion(religion_id)
        if category is not None and not isinstance(category, DoctrineCategory):
            raise TypeError("category deve ser DoctrineCategory ou None.")
        _optional_year(at_year, "at_year")
        return tuple(sorted((doc for doc in self._doctrines.values()
            if (religion_id is None or doc.religion_id == religion_id)
            and (category is None or doc.category == category)
            and (at_year is None or (
                doc.is_active_at(at_year)
                and self._religions[doc.religion_id].is_active_at(at_year)
            ))), key=lambda d: (d.title.casefold(), str(d.religion_id), str(d.id))))

    # -- Integridade / intercâmbio -------------------------------------
    def validate_integrity(self) -> None:
        """Valida referências, ciclos, índices e períodos, mesmo após manipulação externa."""
        if set(self._religions) != set(self._religion_deities):
            raise ValueError("Índice de associações religiosas inconsistente.")
        for key, religion in self._religions.items():
            if key != religion.id:
                raise ValueError("Índice de religiões inconsistente.")
            self._check_parent(religion)
        for key, deity in self._deities.items():
            if key != deity.id:
                raise ValueError("Índice de divindades inconsistente.")
        for did, doctrine in self._doctrines.items():
            if did != doctrine.id:
                raise ValueError("Índice de doutrinas inconsistente.")
            if doctrine.religion_id not in self._religions:
                raise ValueError("Doutrina aponta para religião inexistente.")
            self._check_doctrine_period(doctrine, self._religions[doctrine.religion_id])
        for linked in self._religion_deities.values():
            if not linked <= set(self._deities):
                raise ValueError("Associação aponta para divindade inexistente.")

    def to_dict(self) -> dict[str, Any]:
        """Gera objeto JSON independente, sem alterar Project/storage."""
        self.validate_integrity()
        return {
            "religions": [r.to_dict() for r in self.get_all_religions()],
            "deities": [d.to_dict() for d in self.get_all_deities()],
            "doctrines": [d.to_dict() for d in self.get_doctrines()],
            "religion_deities": [
                {"religion_id": str(religion.id), "deity_id": str(deity.id)}
                for religion in self.get_all_religions()
                for deity in self.get_deities(religion.id)
            ],
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> ReligionRegistry:
        required = {"religions", "deities", "doctrines", "religion_deities"}
        values = _parse_mapping(data, "registro religioso", required, required)
        for key in required:
            if type(values[key]) is not list:
                raise TypeError(f"{key} deve ser uma lista JSON.")
        result = cls()
        # Carregamento em duas fases para aceitar religiões filhas que aparecem
        # antes das ancestrais no JSON. A verificação de referências segue depois.
        for raw in values["religions"]:
            religion = Religion.from_dict(raw)
            if religion.id in result._religions:
                raise ValueError("Religião com UUID duplicado no JSON.")
            result._religions[religion.id] = religion
            result._religion_deities[religion.id] = set()
        for raw in values["deities"]:
            result.add_deity(Deity.from_dict(raw))
        for raw in values["doctrines"]:
            result.add_doctrine(Doctrine.from_dict(raw))
        for raw in values["religion_deities"]:
            entry = _parse_mapping(raw, "associação", {"religion_id", "deity_id"}, {"religion_id", "deity_id"})
            result.link_deity(_json_uuid(entry["religion_id"], "religion_id"),
                              _json_uuid(entry["deity_id"], "deity_id"))
        result.validate_integrity()
        return result


__all__ = ["ReligionRegistry"]
