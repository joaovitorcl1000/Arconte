"""Testes do módulo de identidade de organizações do Arconte.

Execute na raiz backend/genealogy::

    python3 -m pytest test/test_organization.py -v

Um único arquivo concentra TODOS os testes de organization.organization.
Não requer servidor, internet, banco de dados ou arquivos de projeto.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import FrozenInstanceError, fields, replace
import json
from types import MappingProxyType
from uuid import UUID, uuid4

import pytest

from organization.organization import Organization, OrganizationType


OPTIONAL_TEXT_FIELDS = ("headquarters", "motto", "emblem", "description")
ALL_FIELDS = {
    "id", "name", "type", "founder_id", "founded_year", "dissolved_year",
    *OPTIONAL_TEXT_FIELDS, "custom_attributes",
}


@pytest.fixture
def sample() -> Organization:
    return Organization(
        name="Ordem do Falcão Vermelho",
        type=OrganizationType.KNIGHTLY_ORDER,
        founder_id=uuid4(),
        founded_year=12,
        dissolved_year=75,
        headquarters="Castelo no Morro do Falcão, Sarnília",
        motto="A fortuna favorece os audazes",
        emblem="Um falcão vermelho",
        description="Primeiro parágrafo.\n\nSegundo parágrafo sobre a ordem.",
        custom_attributes={
            "hierarquia": ["Grão-mestre", "Cavaleiro", "Escudeiro"],
            "símbolo": {"cor": "vermelho", "animal": "falcão"},
            "ativos": True,
        },
    )


def test_default_minimal_organization():
    org = Organization(name="Grupo")
    assert org.name == "Grupo"
    assert org.type is OrganizationType.ORGANIZATION
    assert isinstance(org.id, UUID)
    assert org.founder_id is None
    assert org.founded_year is None
    assert org.dissolved_year is None
    assert org.custom_attributes == {}
    for name in OPTIONAL_TEXT_FIELDS:
        assert getattr(org, name) is None


def test_expected_fields():
    assert {entry.name for entry in fields(Organization)} == ALL_FIELDS


def test_keyword_only_constructor():
    with pytest.raises(TypeError):
        Organization("Grupo")


def test_auto_generated_ids_differ():
    assert Organization(name="A").id != Organization(name="B").id


def test_identity_is_explicit_and_preserved():
    uid = uuid4()
    org = Organization(name="Conselho", id=uid)
    assert org.id is uid
    assert replace(org, name="Conselho Novo").id == uid


def test_valid_reference_to_founder_does_not_create_character():
    uid = uuid4()
    org = Organization(name="Instituição", founder_id=uid)
    assert org.founder_id == uid
    assert not hasattr(org, "members")
    assert not hasattr(org, "genealogy")


def test_name_is_trimmed_and_internal_spaces_preserved():
    org = Organization(name="  Ordem  de   Mezena  ")
    assert org.name == "Ordem  de   Mezena"
    assert str(org) == org.name


@pytest.mark.parametrize("name", ["", " ", "\n\t  "])
def test_name_rejects_blanks(name):
    with pytest.raises(ValueError, match="name"):
        Organization(name=name)


@pytest.mark.parametrize("name", [None, 5, 1.0, False, [], {}, b"name"])
def test_name_rejects_non_strings(name):
    with pytest.raises(TypeError, match="name"):
        Organization(name=name)


def test_unicode_and_nonhuman_culture_names():
    org = Organization(name="  Irmandade de ÓCuillan 🦅  ")
    assert org.name == "Irmandade de ÓCuillan 🦅"


@pytest.mark.parametrize("kind", list(OrganizationType))
def test_all_types_are_supported(kind):
    org = Organization(name="Exemplo", type=kind)
    assert org.type is kind
    assert OrganizationType(kind.value) is kind


def test_types_have_distinct_values():
    values = [member.value for member in OrganizationType]
    assert len(set(values)) == len(values)
    assert "guild" in values
    assert "religious_order" in values
    assert "secret_society" in values
    assert "political_faction" in values


@pytest.mark.parametrize("kind", ["guild", "knightly_order", None, 4, True, [], {}])
def test_constructor_rejects_non_enum_type(kind):
    with pytest.raises(TypeError, match="type"):
        Organization(name="Exemplo", type=kind)


@pytest.mark.parametrize("value", ["", "\t  ", "\n\n"])
@pytest.mark.parametrize("attribute", OPTIONAL_TEXT_FIELDS)
def test_optional_texts_normalize_blanks(attribute, value):
    org = Organization(name="A", **{attribute: value})
    assert getattr(org, attribute) is None


@pytest.mark.parametrize("attribute", OPTIONAL_TEXT_FIELDS)
def test_optional_texts_accept_none(attribute):
    org = Organization(name="A", **{attribute: None})
    assert getattr(org, attribute) is None


@pytest.mark.parametrize("attribute", OPTIONAL_TEXT_FIELDS)
def test_optional_texts_preserve_multiline_and_unicode(attribute):
    value = "  Sarnília e ÓFiachra\n\nTexto 2.  "
    org = Organization(name="A", **{attribute: value})
    assert getattr(org, attribute) == "Sarnília e ÓFiachra\n\nTexto 2."


@pytest.mark.parametrize("attribute", OPTIONAL_TEXT_FIELDS)
@pytest.mark.parametrize("value", [0, 1.5, True, False, [], {}, (), b"x"])
def test_optional_texts_reject_bad_types(attribute, value):
    with pytest.raises(TypeError, match=attribute):
        Organization(name="A", **{attribute: value})


def test_emblem_is_description_not_url_or_image():
    org = Organization(name="Ordem", emblem="Um falcão vermelho")
    assert org.emblem == "Um falcão vermelho"


def test_descriptions_can_be_large_and_multiple_paragraphs():
    description = ("História da instituição.\n\n" * 400).strip()
    org = Organization(name="Ordem", description=description)
    assert org.description == description


@pytest.mark.parametrize("bad", [False, True, 3.5, "12", [], {}, object()])
@pytest.mark.parametrize("field_name", ["founded_year", "dissolved_year"])
def test_rejects_invalid_year_types(field_name, bad):
    with pytest.raises(TypeError, match=field_name):
        Organization(name="A", **{field_name: bad})


@pytest.mark.parametrize("value", [-100, -1, 0, 1, 67, 10000])
@pytest.mark.parametrize("field_name", ["founded_year", "dissolved_year"])
def test_accepts_fictional_years(field_name, value):
    org = Organization(name="A", **{field_name: value})
    assert getattr(org, field_name) == value


def test_accepts_equal_foundation_and_dissolution():
    assert Organization(name="A", founded_year=10, dissolved_year=10).is_active_at(10)


def test_rejects_dissolution_before_foundation():
    with pytest.raises(ValueError, match="dissolved_year"):
        Organization(name="A", founded_year=20, dissolved_year=19)


def test_dissolution_without_foundation():
    assert Organization(name="A", dissolved_year=19).is_active_at(-100)


def test_foundation_without_dissolution():
    org = Organization(name="A", founded_year=19)
    assert org.is_active_at(19)
    assert org.is_active_at(500)
    assert not org.is_active_at(18)


@pytest.mark.parametrize("year, expected", [
    (-30, False), (11, False), (12, True), (13, True),
    (67, True), (75, True), (76, False), (1000, False),
])
def test_period_is_inclusive(sample, year, expected):
    assert sample.is_active_at(year) is expected


def test_unknown_dates_have_unbounded_range():
    org = Organization(name="A")
    assert org.is_active_at(-999999)
    assert org.is_active_at(0)
    assert org.is_active_at(999999)


@pytest.mark.parametrize("bad", [None, True, False, 2.5, "67", [], {}, object()])
def test_is_active_at_requires_integer(bad):
    org = Organization(name="A")
    with pytest.raises(TypeError, match="year"):
        org.is_active_at(bad)


@pytest.mark.parametrize("field_name", ["id", "founder_id"])
@pytest.mark.parametrize("bad", ["1234", "", 5, None, False, b"1234", {}, []])
def test_constructor_checks_uuid_fields(field_name, bad):
    if field_name == "founder_id" and bad is None:
        assert Organization(name="A", founder_id=None).founder_id is None
    else:
        with pytest.raises(TypeError, match=field_name):
            Organization(name="A", **{field_name: bad})


def test_immutable_dataclass(sample):
    with pytest.raises((FrozenInstanceError, AttributeError)):
        sample.name = "Nova Ordem"
    with pytest.raises((FrozenInstanceError, AttributeError, TypeError)):
        sample.extra = "não permitido"


def test_replace_preserves_identity(sample):
    modified = replace(sample, name="Ordem Renovada", motto="Novo lema")
    assert modified.id == sample.id
    assert modified.name == "Ordem Renovada"
    assert sample.name == "Ordem do Falcão Vermelho"
    assert modified.motto == "Novo lema"
    assert sample.motto == "A fortuna favorece os audazes"


def test_replace_revalidates_years(sample):
    with pytest.raises(ValueError):
        replace(sample, founded_year=100)
    assert sample.founded_year == 12


def test_replace_can_clear_optional_fields(sample):
    modified = replace(sample, founder_id=None, headquarters=None)
    assert modified.founder_id is None
    assert modified.headquarters is None
    assert sample.headquarters is not None


def test_empty_custom_attributes_are_independent_between_objects():
    org1 = Organization(name="A")
    org2 = Organization(name="B")
    assert org1.custom_attributes == org2.custom_attributes
    assert org1.custom_attributes is not org2.custom_attributes


@pytest.mark.parametrize("bad", [None, [], (), "text", 1, False, object()])
def test_custom_attributes_top_level_must_be_mapping(bad):
    with pytest.raises(TypeError, match="custom_attributes"):
        Organization(name="A", custom_attributes=bad)


def test_custom_attributes_accept_primitive_json_values():
    source = {
        "nothing": None, "text": "Corvo", "n": -13,
        "f": 2.75, "bool_true": True, "bool_false": False,
    }
    org = Organization(name="A", custom_attributes=source)
    assert org.to_dict()["custom_attributes"] == source


def test_custom_attributes_are_deeply_frozen_and_copied():
    nested = {"cores": ["vermelho", {"tom": "escuro"}]}
    org = Organization(name="A", custom_attributes={"brasão": nested})
    nested["cores"][0] = "azul"
    nested["cores"][1]["tom"] = "claro"
    assert org.custom_attributes["brasão"]["cores"][0] == "vermelho"
    assert org.custom_attributes["brasão"]["cores"][1]["tom"] == "escuro"
    assert isinstance(org.custom_attributes, MappingProxyType)
    assert isinstance(org.custom_attributes["brasão"], MappingProxyType)
    assert isinstance(org.custom_attributes["brasão"]["cores"], tuple)
    with pytest.raises(TypeError):
        org.custom_attributes["novo"] = "x"
    with pytest.raises(TypeError):
        org.custom_attributes["brasão"]["cores"][1]["tom"] = "azul"


def test_custom_attributes_accept_shared_non_cyclic_reference():
    shared = [1, 2]
    org = Organization(name="A", custom_attributes={"a": shared, "b": shared})
    assert org.custom_attributes["a"] == (1, 2)
    assert org.custom_attributes["b"] == (1, 2)


def test_custom_attributes_accept_tuple_as_input():
    org = Organization(name="A", custom_attributes={"postos": ("mestre", "iniciado")})
    assert org.to_dict()["custom_attributes"]["postos"] == ["mestre", "iniciado"]


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), -float("inf")])
def test_custom_attributes_reject_nonfinite_numbers(bad):
    with pytest.raises(ValueError):
        Organization(name="A", custom_attributes={"numero": {"outro": [bad]}})


@pytest.mark.parametrize("bad", [set([1]), object(), uuid4(), complex(1, 2), b"bytes"])
def test_custom_attributes_reject_non_json_values(bad):
    with pytest.raises(TypeError):
        Organization(name="A", custom_attributes={"item": bad})


@pytest.mark.parametrize("bad", [1, False, None, ("a",)])
def test_custom_attributes_reject_nonstring_nested_keys(bad):
    with pytest.raises(TypeError):
        Organization(name="A", custom_attributes={"nested": {bad: "x"}})


@pytest.mark.parametrize("bad", ["", " ", "\t\n"])
def test_custom_attributes_reject_blank_keys(bad):
    with pytest.raises(ValueError):
        Organization(name="A", custom_attributes={bad: 1})


def test_custom_attributes_normalize_keys():
    org = Organization(name="A", custom_attributes={"  título  ": "Grão-mestre"})
    assert org.custom_attributes["título"] == "Grão-mestre"


def test_custom_attributes_reject_duplicate_normalized_keys():
    with pytest.raises(ValueError, match="duplicada"):
        Organization(name="A", custom_attributes={"cor": "vermelho", " cor ": "azul"})


def test_custom_attributes_reject_direct_mapping_cycle():
    cycle = {}
    cycle["self"] = cycle
    with pytest.raises(ValueError, match="circulares"):
        Organization(name="A", custom_attributes=cycle)


def test_custom_attributes_reject_indirect_cycle():
    nested: list[object] = []
    root = {"next": nested}
    nested.append(root)
    with pytest.raises(ValueError, match="circulares"):
        Organization(name="A", custom_attributes=root)


def test_custom_attributes_snapshot_is_independent_of_to_dict(sample):
    data = sample.to_dict()
    data["custom_attributes"]["hierarquia"].append("Recruta")
    data["custom_attributes"]["símbolo"]["cor"] = "azul"
    assert sample.custom_attributes["hierarquia"] == (
        "Grão-mestre", "Cavaleiro", "Escudeiro",
    )
    assert sample.custom_attributes["símbolo"]["cor"] == "vermelho"


def test_to_dict_has_complete_schema(sample):
    data = sample.to_dict()
    assert set(data) == ALL_FIELDS
    assert data["name"] == sample.name
    assert data["id"] == str(sample.id)
    assert data["founder_id"] == str(sample.founder_id)
    assert data["type"] == "knightly_order"
    assert data["founded_year"] == 12
    assert data["dissolved_year"] == 75
    assert data["emblem"] == "Um falcão vermelho"


def test_json_dumps_works_with_unicode_and_nested_values(sample):
    serialized = json.dumps(sample.to_dict(), ensure_ascii=False, allow_nan=False)
    decoded = json.loads(serialized)
    assert decoded["headquarters"].endswith("Sarnília")
    assert decoded["custom_attributes"]["símbolo"]["animal"] == "falcão"


def test_round_trip_json_preserves_identity_and_value(sample):
    data = json.loads(json.dumps(sample.to_dict(), ensure_ascii=False))
    restored = Organization.from_dict(data)
    assert restored == sample
    assert restored.id == sample.id
    assert restored.to_dict() == sample.to_dict()


def test_round_trip_minimal_document():
    sample = Organization(name="Grupo")
    restored = Organization.from_dict(json.loads(json.dumps(sample.to_dict())))
    assert restored == sample


def test_round_trip_negative_years():
    sample = Organization(name="Ordem Antiga", founded_year=-999, dissolved_year=-200)
    assert Organization.from_dict(sample.to_dict()) == sample


def test_from_dict_optional_fields_may_be_omitted():
    uid = uuid4()
    org = Organization.from_dict({"id": str(uid), "name": "  A  "})
    assert org.id == uid
    assert org.name == "A"
    assert org.type is OrganizationType.ORGANIZATION
    assert org.custom_attributes == {}


@pytest.mark.parametrize("bad", [None, [], (), "x", 3, False])
def test_from_dict_requires_mapping(bad):
    with pytest.raises(TypeError, match="mapeamento"):
        Organization.from_dict(bad)


@pytest.mark.parametrize("missing", ["id", "name"])
def test_from_dict_requires_id_and_name(missing):
    data = {"id": str(uuid4()), "name": "A"}
    del data[missing]
    with pytest.raises(ValueError, match="ausentes"):
        Organization.from_dict(data)


def test_from_dict_rejects_unknown_keys():
    with pytest.raises(ValueError, match="desconhecidos"):
        Organization.from_dict({"id": str(uuid4()), "name": "A", "members": []})


@pytest.mark.parametrize("bad", [None, 5, True, [], {}, uuid4(), "abc", ""])
def test_from_dict_rejects_malformed_id(bad):
    with pytest.raises((ValueError, TypeError), match="id"):
        Organization.from_dict({"id": bad, "name": "A"})


@pytest.mark.parametrize("bad", [0, True, "abc", uuid4(), [], {}])
def test_from_dict_rejects_malformed_founder_id(bad):
    with pytest.raises((ValueError, TypeError), match="founder_id"):
        Organization.from_dict({"id": str(uuid4()), "name": "A", "founder_id": bad})


def test_from_dict_accepts_null_founder():
    org = Organization.from_dict({"id": str(uuid4()), "name": "A", "founder_id": None})
    assert org.founder_id is None


@pytest.mark.parametrize("bad", ["magos", "KNIGHTLY_ORDER", "", None, 5, True, [], {}])
def test_from_dict_rejects_invalid_type(bad):
    with pytest.raises((ValueError, TypeError), match="[Tt]ipo|type"):
        Organization.from_dict({"id": str(uuid4()), "name": "A", "type": bad})


@pytest.mark.parametrize("kind", list(OrganizationType))
def test_from_dict_accepts_every_enum_value(kind):
    org = Organization.from_dict({"id": str(uuid4()), "name": "A", "type": kind.value})
    assert org.type is kind


def test_from_dict_revalidates_periods():
    data = {"id": str(uuid4()), "name": "A", "founded_year": 68, "dissolved_year": 67}
    with pytest.raises(ValueError, match="dissolved_year"):
        Organization.from_dict(data)


def test_from_dict_revalidates_custom_attributes():
    data = {"id": str(uuid4()), "name": "A", "custom_attributes": {"a": float("nan")}}
    with pytest.raises(ValueError):
        Organization.from_dict(data)


def test_from_dict_does_not_share_input_custom_attributes():
    data = {"id": str(uuid4()), "name": "A", "custom_attributes": {"ranks": ["a"]}}
    org = Organization.from_dict(data)
    data["custom_attributes"]["ranks"].append("b")
    assert org.custom_attributes["ranks"] == ("a",)


def test_round_trip_organization_belongs_to_no_religion_by_default():
    org = Organization(name="Templo de Mezena", type=OrganizationType.RELIGIOUS_INSTITUTION)
    assert org.type is OrganizationType.RELIGIOUS_INSTITUTION
    assert not hasattr(org, "religion_id")
    assert not hasattr(org, "memberships")
    assert not hasattr(org, "deities")


def test_families_and_relationships_remain_separate_from_organizations():
    org = Organization(name="Guarda da Sarnília", type=OrganizationType.MILITARY)
    assert not hasattr(org, "family_id")
    assert not hasattr(org, "character_ids")
    assert not hasattr(org, "parent_ids")


def test_no_external_dependencies_or_project_mutation():
    org = Organization(name="Ordem", custom_attributes={"sede": "Morro do Falcão"})
    assert org.to_dict()["custom_attributes"]["sede"] == "Morro do Falcão"
    assert isinstance(org.custom_attributes, Mapping)
