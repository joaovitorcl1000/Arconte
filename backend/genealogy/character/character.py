"""Entidade de domínio que representa um personagem fictício.

Este módulo não depende de API, banco de dados ou interface gráfica.
As relações familiares e as afiliações são modeladas separadamente.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from uuid import UUID, uuid4

from character.physical import PhysicalAttributes
from character.personality import PersonalityProfile
from character.social import SocialProfile
from character.history import CharacterHistory


def _required_text(value: str, field_name: str) -> str:
    """Valida e normaliza um campo textual obrigatório."""
    if not isinstance(value, str):
        raise TypeError(f"{field_name} deve ser uma string.")

    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} não pode estar vazio.")

    return normalized


def _optional_text(value: str | None, field_name: str) -> str | None:
    """Normaliza texto opcional; strings vazias viram None."""
    if value is None:
        return None
    if not isinstance(value, str):
        raise TypeError(f"{field_name} deve ser uma string ou None.")

    return value.strip() or None


@dataclass(frozen=True, slots=True, kw_only=True)
class Character:
    """Representa um personagem e suas características individuais.

    `id` identifica o personagem, inclusive se ele mudar de nome.
    Anos podem ser negativos para calendários ficcionais; datas mais
    elaboradas serão tratadas por um módulo próprio, futuramente.

    A entidade é imutável: para editar, utilize dataclasses.replace().
    Os quatro perfis são módulos independentes, com valores padrão vazios.
    O campo biography é mantido por compatibilidade com APIs anteriores:
    Editor.update_history() atualiza biography e history em conjunto.
    """

    name: str
    surname: str | None = None
    gender: str | None = None
    birth_year: int | None = None
    death_year: int | None = None
    biography: str | None = None
    id: UUID = field(default_factory=uuid4)
    physical: PhysicalAttributes = field(default_factory=PhysicalAttributes)
    personality: PersonalityProfile = field(default_factory=PersonalityProfile)
    social: SocialProfile = field(default_factory=SocialProfile)
    history: CharacterHistory = field(default_factory=CharacterHistory)

    def __post_init__(self) -> None:
        if not isinstance(self.id, UUID):
            raise TypeError("id deve ser um UUID.")

        object.__setattr__(self, "name", _required_text(self.name, "name"))

        for field_name in ("surname", "gender", "biography"):
            value = getattr(self, field_name)
            object.__setattr__(
                self, field_name, _optional_text(value, field_name)
            )

        for field_name, expected in (
            ("physical", PhysicalAttributes),
            ("personality", PersonalityProfile),
            ("social", SocialProfile),
            ("history", CharacterHistory),
        ):
            if not isinstance(getattr(self, field_name), expected):
                raise TypeError(f"{field_name} deve ser {expected.__name__}.")

        # biography permanece para as APIs legadas e o visualizador atual.
        # A história guarda a versão canônica. No conflito, o campo legado
        # prevalece para preservar dataclasses.replace(c, biography=...).
        # Alterações diretas da história devem também informar biography,
        # ou usar Editor.update_history(), que sincroniza ambos.
        if self.biography is None and self.history.biography is not None:
            object.__setattr__(self, "biography", self.history.biography)
        elif self.biography != self.history.biography:
            object.__setattr__(
                self, "history", replace(self.history, biography=self.biography)
            )

        for field_name in ("birth_year", "death_year"):
            value = getattr(self, field_name)
            # bool é subtipo de int em Python, mas não é um ano válido.
            if value is not None and type(value) is not int:
                raise TypeError(f"{field_name} deve ser um inteiro ou None.")

        if (
            self.birth_year is not None
            and self.death_year is not None
            and self.death_year < self.birth_year
        ):
            raise ValueError("death_year não pode ser anterior a birth_year.")

    def __hash__(self) -> int:
        # UUID é estável e evita hashear perfis personalizados (mapeamentos).
        return hash(self.id)

    @property
    def full_name(self) -> str:
        """Nome completo apresentado ao usuário."""
        return (
            f"{self.name} {self.surname}"
            if self.surname is not None
            else self.name
        )

    def __str__(self) -> str:
        return self.full_name
