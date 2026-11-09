"""Testes da composição Character e compatibilidade da biografia legada."""
from dataclasses import FrozenInstanceError, replace
from uuid import uuid4
import pytest
from character.character import Character
from character.physical import PhysicalAttributes
from character.personality import PersonalityProfile
from character.social import SocialProfile
from character.history import CharacterHistory, HistoryEvent


def test_new_character_has_four_empty_profiles():
    c = Character(name="Aioria")
    assert c.physical == PhysicalAttributes()
    assert c.personality == PersonalityProfile()
    assert c.social == SocialProfile()
    assert c.history == CharacterHistory()
    assert c.biography is None


def test_new_character_with_all_profiles():
    c = Character(
        name="Artuin", surname="Hauck",
        physical=PhysicalAttributes(height_m=1.68),
        personality=PersonalityProfile(flaws=["Cruel"]),
        social=SocialProfile(title="Conde"),
        history=CharacterHistory(biography="História", events=[HistoryEvent(title="Reinado")]),
    )
    assert c.physical.height_m == 1.68
    assert c.personality.flaws == ("Cruel",)
    assert c.social.title == "Conde"
    assert c.biography == "História"
    assert c.history.events[0].title == "Reinado"


def test_legacy_biography_is_migrated_in_memory():
    c = Character(name="Sofia", biography="Biografia antiga")
    assert c.history.biography == c.biography


def test_legacy_dataclasses_replace_biography():
    c = Character(name="Sofia", biography="Antiga")
    updated = replace(c, biography="Nova")
    assert updated.history.biography == "Nova"
    assert c.history.biography == "Antiga"


def test_old_fields_still_have_validation():
    with pytest.raises(TypeError):
        Character(name="X", birth_year=True)
    with pytest.raises(ValueError):
        Character(name="X", birth_year=10, death_year=3)


@pytest.mark.parametrize("field,value", [
    ("physical", "not profile"),
    ("personality", {}),
    ("social", None),
    ("history", []),
])
def test_invalid_profiles_rejected(field,value):
    with pytest.raises(TypeError):
        Character(name="X", **{field:value})


def test_hashable_and_stable_for_genealogy_sets():
    c = Character(name="X", physical=PhysicalAttributes(custom_attributes={"species": "dragão"}))
    other = replace(c, physical=PhysicalAttributes(height_m=2.3))
    assert hash(c) == hash(other)
    assert c in {c}
    assert c.id == other.id


def test_profiles_not_shared():
    a = Character(name="A")
    b = Character(name="B")
    assert a.physical is not b.physical
    assert a.history is not b.history


def test_profiles_are_immutable():
    c = Character(name="A")
    with pytest.raises(FrozenInstanceError):
        c.physical = PhysicalAttributes(height_m=1.8)
