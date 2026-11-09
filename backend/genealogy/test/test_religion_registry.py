"""Testes do registro religioso. Mantido distinto de test_registry.py (organizações)."""
import json
from dataclasses import replace
from uuid import UUID, uuid4

import pytest

from religion.deity import Deity
from religion.doctrine import Doctrine, DoctrineCategory
from religion.religion import Religion, ReligionType
from religion.registry import ReligionRegistry


@pytest.fixture
def registry():
    return ReligionRegistry()


@pytest.fixture
def sample():
    r = Religion(name="Culto de Mezena", founded_year=12, ended_year=100,
                 type=ReligionType.POLYTHEISTIC, scriptures=["Cânticos"])
    d1 = Deity(name="Mezena", domains=["Fé"])
    d2 = Deity(name="Divindade do Bosque", domains=["Bosques"])
    rule = Doctrine(religion_id=r.id, title="Oração", content="Cantar ao amanhecer.",
                    category=DoctrineCategory.RITUAL, start_year=30, end_year=60)
    reg = ReligionRegistry()
    reg.add_religion(r)
    reg.add_deity(d1)
    reg.add_deity(d2)
    reg.add_doctrine(rule)
    reg.link_deity(r.id, d1.id)
    reg.link_deity(r.id, d2.id)
    return reg, r, d1, d2, rule


def test_empty_registry_serializes():
    reg = ReligionRegistry()
    assert reg.get_all_religions() == ()
    assert reg.get_all_deities() == ()
    assert reg.get_doctrines() == ()
    assert reg.to_dict() == {"religions": [], "deities": [], "doctrines": [], "religion_deities": []}


def test_add_religion_and_identity(registry):
    r = Religion(name=" Sagrada Luz ")
    registry.add_religion(r)
    assert registry.get_religion(r.id) is r
    assert registry.get_all_religions() == (r,)


@pytest.mark.parametrize("bad", [None, [], 3, "religion"])
def test_add_religion_invalid_type(registry, bad):
    with pytest.raises(TypeError):
        registry.add_religion(bad)


def test_duplicate_religion_id_not_name(registry):
    r = Religion(name="Mezena")
    registry.add_religion(r)
    with pytest.raises(ValueError, match="UUID"):
        registry.add_religion(replace(r, name="Outro"))
    registry.add_religion(Religion(name="Mezena"))
    assert len(registry.get_all_religions()) == 2


def test_religions_sorted_case_insensitive(registry):
    for name in ("zeta", "Áurea", "beta", "Alpha"):
        registry.add_religion(Religion(name=name))
    assert [r.name for r in registry.get_all_religions()] == ["Alpha", "beta", "zeta", "Áurea"]


def test_parent_religion_missing_rejected(registry):
    with pytest.raises(ValueError, match="origem inexistente"):
        registry.add_religion(Religion(name="Derivada", parent_religion_id=uuid4()))
    assert registry.get_all_religions() == ()


def test_parent_child_and_grandchild(registry):
    origin = Religion(name="Origem")
    registry.add_religion(origin)
    child = Religion(name="Cisma", parent_religion_id=origin.id)
    registry.add_religion(child)
    grandchild = Religion(name="Reforma", parent_religion_id=child.id)
    registry.add_religion(grandchild)
    assert registry.get_derived_religions(origin.id) == (child,)
    assert registry.get_derived_religions(origin.id, recursive=True) == (child, grandchild)
    assert registry.get_derived_religions(child.id) == (grandchild,)


def test_cycle_detected_on_update_and_transactional(registry):
    ancestor = Religion(name="Antiga")
    registry.add_religion(ancestor)
    child = Religion(name="Nova", parent_religion_id=ancestor.id)
    registry.add_religion(child)
    with pytest.raises(ValueError, match="Ciclo"):
        registry.update_religion(replace(ancestor, parent_religion_id=child.id))
    assert registry.get_religion(ancestor.id).parent_religion_id is None
    registry.validate_integrity()


def test_parent_can_change_if_no_cycle(registry):
    old, new = Religion(name="Antiga"), Religion(name="Outra")
    registry.add_religion(old)
    registry.add_religion(new)
    child = Religion(name="Nova", parent_religion_id=old.id)
    registry.add_religion(child)
    registry.update_religion(replace(child, parent_religion_id=new.id))
    assert registry.get_derived_religions(old.id) == ()
    assert registry.get_derived_religions(new.id)[0].id == child.id


def test_remove_ancestor_requires_explicit_detach(registry):
    origin = Religion(name="Antiga")
    child = Religion(name="Nova", parent_religion_id=origin.id)
    registry.add_religion(origin)
    registry.add_religion(child)
    with pytest.raises(ValueError, match="derivadas"):
        registry.remove_religion(origin.id)
    assert registry.get_religion(child.id).parent_religion_id == origin.id
    assert registry.remove_religion(origin.id, on_children="detach") == origin
    assert registry.get_religion(child.id).parent_religion_id is None


def test_invalid_children_policy_keeps_data(registry):
    r = Religion(name="A")
    registry.add_religion(r)
    with pytest.raises(ValueError):
        registry.remove_religion(r.id, on_children="all")
    assert registry.get_religion(r.id) == r


@pytest.mark.parametrize("value", [None, "true", 1, [], 2.0])
def test_recursive_query_requires_bool(registry, value):
    r = Religion(name="A")
    registry.add_religion(r)
    with pytest.raises(TypeError):
        registry.get_derived_religions(r.id, recursive=value)


def test_update_religion_preserves_id(registry):
    r = Religion(name="A")
    registry.add_religion(r)
    newer = replace(r, name="B", type=ReligionType.NON_THEISTIC)
    registry.update_religion(newer)
    assert registry.get_religion(r.id) == newer
    assert registry.get_religion(r.id).id == r.id


def test_unknown_religion_access(registry):
    with pytest.raises(KeyError):
        registry.get_religion(uuid4())
    with pytest.raises(TypeError):
        registry.get_religion("bad")


def test_add_deity_and_sort(registry):
    d1 = Deity(name="Z")
    d2 = Deity(name="A")
    registry.add_deity(d1)
    registry.add_deity(d2)
    assert registry.get_all_deities() == (d2, d1)


@pytest.mark.parametrize("bad", [None, 1, "Mezena"])
def test_add_deity_wrong_type(registry, bad):
    with pytest.raises(TypeError):
        registry.add_deity(bad)


def test_duplicate_deity_id(registry):
    d = Deity(name="Mezena")
    registry.add_deity(d)
    with pytest.raises(ValueError, match="UUID"):
        registry.add_deity(d)


def test_update_deity_preserves_links(sample):
    reg, r, d1, d2, rule = sample
    reg.update_deity(replace(d1, name="Outro nome", domains=["Fé", "Mistério"]))
    assert [d.name for d in reg.get_deities(r.id)] == ["Divindade do Bosque", "Outro nome"]
    assert reg.get_deity(d1.id).id == d1.id


def test_same_deity_multiple_religions(registry):
    d = Deity(name="Divindade compartilhada")
    ra, rb = Religion(name="Culto A"), Religion(name="Culto B")
    registry.add_deity(d)
    registry.add_religion(ra)
    registry.add_religion(rb)
    registry.link_deity(ra.id, d.id)
    registry.link_deity(rb.id, d.id)
    assert registry.get_religions_for_deity(d.id) == (ra, rb)
    assert registry.get_deities(ra.id) == (d,)
    assert registry.get_deities(rb.id) == (d,)
    assert registry.get_deity(d.id) == d


def test_non_theistic_religion_needs_no_deity(registry):
    r = Religion(name="Caminho sem deuses", type=ReligionType.NON_THEISTIC)
    registry.add_religion(r)
    assert registry.get_deities(r.id) == ()
    assert registry.to_dict()["religion_deities"] == []


def test_link_unknown_entities_fails_without_effect(registry):
    r = Religion(name="Culto")
    d = Deity(name="Deusa")
    registry.add_religion(r)
    with pytest.raises(KeyError):
        registry.link_deity(r.id, d.id)
    registry.add_deity(d)
    with pytest.raises(KeyError):
        registry.link_deity(uuid4(), d.id)
    assert registry.get_deities(r.id) == ()


def test_duplicate_deity_association_rejected(sample):
    reg, r, d1, _, _ = sample
    with pytest.raises(ValueError, match="existe"):
        reg.link_deity(r.id, d1.id)
    assert len(reg.get_deities(r.id)) == 2


def test_unlink_deity(sample):
    reg, r, d1, _, _ = sample
    reg.unlink_deity(r.id, d1.id)
    assert d1 not in reg.get_deities(r.id)
    with pytest.raises(KeyError):
        reg.unlink_deity(r.id, d1.id)


def test_remove_deity_cleans_links(sample):
    reg, r, d1, d2, _ = sample
    reg.remove_deity(d1.id)
    assert reg.get_deities(r.id) == (d2,)
    with pytest.raises(KeyError):
        reg.get_deity(d1.id)
    reg.validate_integrity()


def test_remove_religion_cleans_doctrines_and_links(sample):
    reg, r, d1, d2, rule = sample
    assert reg.remove_religion(r.id) == r
    assert reg.get_all_religions() == ()
    assert reg.get_doctrines() == ()
    assert reg.get_all_deities() == tuple(sorted((d1, d2), key=lambda d: d.name.casefold()))
    assert reg.get_religions_for_deity(d1.id) == ()
    reg.validate_integrity()


def test_add_doctrine(sample):
    reg, r, _, _, rule = sample
    assert reg.get_doctrine(rule.id) == rule
    assert reg.get_doctrines(religion_id=r.id) == (rule,)
    assert reg.get_doctrines(at_year=40) == (rule,)
    assert reg.get_doctrines(at_year=30) == (rule,)
    assert reg.get_doctrines(at_year=60) == (rule,)
    assert reg.get_doctrines(at_year=61) == ()


def test_doctrine_category_and_religion_filter(sample):
    reg, r, _, _, rule = sample
    ethical = Doctrine(religion_id=r.id, title="Ética", content="Não ferir.", category=DoctrineCategory.ETHICS)
    reg.add_doctrine(ethical)
    assert reg.get_doctrines(category=DoctrineCategory.ETHICS) == (ethical,)
    assert reg.get_doctrines(religion_id=r.id, category=DoctrineCategory.RITUAL) == (rule,)


def test_doctrine_can_be_reassigned_to_another_religion(sample):
    reg, r, _, _, rule = sample
    r2 = Religion(name="Outra", founded_year=20)
    reg.add_religion(r2)
    reg.update_doctrine(replace(rule, religion_id=r2.id))
    assert reg.get_doctrines(religion_id=r.id) == ()
    assert reg.get_doctrines(religion_id=r2.id)[0].id == rule.id


def test_duplicate_doctrine_id(sample):
    reg, _, _, _, rule = sample
    with pytest.raises(ValueError, match="UUID"):
        reg.add_doctrine(replace(rule, title="Outra"))


def test_missing_religion_rejects_doctrine(registry):
    d = Doctrine(religion_id=uuid4(), title="Texto", content="Regra")
    with pytest.raises(KeyError):
        registry.add_doctrine(d)
    assert registry.get_doctrines() == ()


@pytest.mark.parametrize("start,end", [(11, 15), (30, 101), (0, 120), (1, 9)])
def test_doctrine_outside_religion_lifetime_rejected(sample, start, end):
    reg, r, _, _, _ = sample
    with pytest.raises(ValueError, match="Doutrina datada"):
        reg.add_doctrine(Doctrine(religion_id=r.id, title="Incompatível", content="Regra", start_year=start, end_year=end))


def test_doctrine_on_religion_lifetime_boundaries(sample):
    reg, r, _, _, _ = sample
    doc = Doctrine(religion_id=r.id, title="Limites", content="Regra", start_year=12, end_year=100)
    reg.add_doctrine(doc)
    assert doc in reg.get_doctrines(at_year=12)
    assert doc in reg.get_doctrines(at_year=100)


def test_unknown_doctrine_bounds_allowed(sample):
    reg, r, _, _, _ = sample
    doc = Doctrine(religion_id=r.id, title="Sem data", content="Regra")
    reg.add_doctrine(doc)
    assert doc in reg.get_doctrines(at_year=12)
    assert doc not in reg.get_doctrines(at_year=101)


def test_update_religion_incompatible_with_doctrine_is_atomic(sample):
    reg, r, _, _, rule = sample
    with pytest.raises(ValueError, match="Doutrina datada"):
        reg.update_religion(replace(r, founded_year=40))
    assert reg.get_religion(r.id).founded_year == 12
    assert reg.get_doctrine(rule.id) == rule


def test_update_doctrine_bad_time_is_atomic(sample):
    reg, r, _, _, rule = sample
    with pytest.raises(ValueError, match="Doutrina datada"):
        reg.update_doctrine(replace(rule, start_year=1))
    assert reg.get_doctrine(rule.id) == rule


def test_remove_doctrine(sample):
    reg, r, _, _, rule = sample
    assert reg.remove_doctrine(rule.id) == rule
    assert reg.get_doctrines(religion_id=r.id) == ()
    with pytest.raises(KeyError):
        reg.remove_doctrine(rule.id)


@pytest.mark.parametrize("bad", [True, False, 67.5, "67", []])
def test_doctrine_query_bad_year(sample, bad):
    reg, *_ = sample
    with pytest.raises(TypeError):
        reg.get_doctrines(at_year=bad)


def test_doctrine_query_bad_category(sample):
    reg, *_ = sample
    with pytest.raises(TypeError):
        reg.get_doctrines(category="ritual")


def test_deity_and_doctrine_are_independent(sample):
    reg, r, d1, _, rule = sample
    reg.unlink_deity(r.id, d1.id)
    assert rule in reg.get_doctrines(religion_id=r.id)


def test_valid_json_roundtrip(sample):
    reg, r, d1, d2, rule = sample
    payload = json.loads(json.dumps(reg.to_dict(), ensure_ascii=False, allow_nan=False))
    restored = ReligionRegistry.from_dict(payload)
    assert restored.to_dict() == reg.to_dict()
    assert restored.get_religion(r.id).id == r.id
    assert restored.get_doctrine(rule.id).religion_id == r.id
    assert {d.id for d in restored.get_deities(r.id)} == {d1.id, d2.id}


def test_roundtrip_child_before_parent_in_json(registry):
    origin = Religion(name="Z Antiga")
    reform = Religion(name="A Nova", parent_religion_id=origin.id)
    registry.add_religion(origin)
    registry.add_religion(reform)
    doc = registry.to_dict()
    assert doc["religions"][0]["name"] == "A Nova"
    restored = ReligionRegistry.from_dict(doc)
    assert restored.get_derived_religions(origin.id) == (reform,)


def test_serialization_detached(sample):
    reg, r, _, _, rule = sample
    output = reg.to_dict()
    output["religions"][0]["name"] = "Alterado"
    output["religion_deities"].clear()
    assert reg.get_religion(r.id).name == "Culto de Mezena"
    assert len(reg.get_deities(r.id)) == 2


@pytest.mark.parametrize("bad", [None, 1, [], "texto"])
def test_from_dict_rejects_non_mapping(bad):
    with pytest.raises(TypeError):
        ReligionRegistry.from_dict(bad)


def test_from_dict_missing_and_unknown_keys():
    with pytest.raises(ValueError, match="ausentes"):
        ReligionRegistry.from_dict({"religions": []})
    with pytest.raises(ValueError, match="desconhecidos"):
        ReligionRegistry.from_dict({"religions": [], "deities": [], "doctrines": [], "religion_deities": [], "other": []})


@pytest.mark.parametrize("field", ["religions", "deities", "doctrines", "religion_deities"])
@pytest.mark.parametrize("bad", [None, {}, (), 1])
def test_from_dict_bad_lists(field, bad):
    payload = ReligionRegistry().to_dict()
    payload[field] = bad
    with pytest.raises(TypeError):
        ReligionRegistry.from_dict(payload)


def test_from_dict_duplicate_religion(sample):
    reg, *_ = sample
    data = reg.to_dict()
    data["religions"].append(data["religions"][0].copy())
    with pytest.raises(ValueError, match="duplicado"):
        ReligionRegistry.from_dict(data)


def test_from_dict_duplicate_deity(sample):
    reg, *_ = sample
    data = reg.to_dict()
    data["deities"].append(data["deities"][0].copy())
    with pytest.raises(ValueError, match="UUID"):
        ReligionRegistry.from_dict(data)


def test_from_dict_duplicate_doctrine(sample):
    reg, *_ = sample
    data = reg.to_dict()
    data["doctrines"].append(data["doctrines"][0].copy())
    with pytest.raises(ValueError, match="UUID"):
        ReligionRegistry.from_dict(data)


def test_from_dict_duplicate_link(sample):
    reg, *_ = sample
    data = reg.to_dict()
    data["religion_deities"].append(data["religion_deities"][0].copy())
    with pytest.raises(ValueError, match="existe"):
        ReligionRegistry.from_dict(data)


def test_from_dict_unknown_deity_link(sample):
    reg, *_ = sample
    data = reg.to_dict()
    data["religion_deities"][0]["deity_id"] = str(uuid4())
    with pytest.raises(KeyError):
        ReligionRegistry.from_dict(data)


def test_from_dict_unknown_doctrine_religion(sample):
    reg, *_ = sample
    data = reg.to_dict()
    data["doctrines"][0]["religion_id"] = str(uuid4())
    with pytest.raises(KeyError):
        ReligionRegistry.from_dict(data)


def test_from_dict_orphan_parent(sample):
    reg, *_ = sample
    data = reg.to_dict()
    data["religions"][0]["parent_religion_id"] = str(uuid4())
    with pytest.raises(ValueError, match="origem inexistente"):
        ReligionRegistry.from_dict(data)


def test_from_dict_parent_cycle_detected(sample):
    reg, r, *_ = sample
    second = Religion(name="Nova", parent_religion_id=r.id)
    reg.add_religion(second)
    data = reg.to_dict()
    for record in data["religions"]:
        if record["id"] == str(r.id):
            record["parent_religion_id"] = str(second.id)
    with pytest.raises(ValueError, match="Ciclo"):
        ReligionRegistry.from_dict(data)


def test_from_dict_bad_link_format(sample):
    reg, *_ = sample
    data = reg.to_dict()
    data["religion_deities"][0]["notes"] = "x"
    with pytest.raises(ValueError, match="desconhecidos"):
        ReligionRegistry.from_dict(data)


def test_from_dict_bad_uuid_link(sample):
    reg, *_ = sample
    data = reg.to_dict()
    data["religion_deities"][0]["religion_id"] = "not-uuid"
    with pytest.raises(ValueError):
        ReligionRegistry.from_dict(data)


def test_integrity_detects_external_broken_reference(sample):
    reg, r, d1, _, rule = sample
    reg._deities.pop(d1.id)
    with pytest.raises(ValueError, match="divindade inexistente"):
        reg.validate_integrity()


def test_integrity_detects_orphan_doctrine(sample):
    reg, r, *_ = sample
    reg._religions.pop(r.id)
    with pytest.raises(ValueError):
        reg.validate_integrity()


def test_no_character_or_organization_registration_implicit(sample):
    reg = ReligionRegistry()
    origin = Religion(name="Tradição", founder_id=uuid4())
    reg.add_religion(origin)
    assert reg.to_dict()["religions"][0]["founder_id"] == str(origin.founder_id)
    assert not hasattr(reg, "add_membership")
