"""Sb_MORPHO_PROFILE_READMODEL_01 — rendre le profil inspectable, sans pouvoir.

Deux propriétés portent cette tranche, et les deux se testent par ce que la page
**ne dit pas** : elle n'affiche pas de valeur de remplacement pour un fait
absent, et elle ne promet aucun effet sur le programme.
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

# Même contrainte que la tranche 1 : la fixture `client` purge `sys.modules`,
# donc aucun import `app.*` au niveau module.

PROFILE_URL = "/profile"
MORPHO_TITLE = "Mesures morphologiques"
WINGSPAN_MISSING = "Envergure non renseignée"


@pytest.fixture(autouse=True)
def _app_db(client):
    return client


def _add(db, uid, *, days_ago=0, **fields):
    from app.models.measurement import BodyMeasurement

    row = BodyMeasurement(
        user_id=uid,
        measured_at=datetime.now(UTC) - timedelta(days=days_ago),
        **fields,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def _set_height(db, uid, height):
    from sqlalchemy import select

    from app.models.user import User

    db.execute(select(User).where(User.id == uid)).scalar_one().height_cm = height
    db.commit()


def _session():
    from app.database import SessionLocal

    return SessionLocal()


def _uid():
    from tests.helpers import get_test_user_id

    return get_test_user_id()


def _readmodel():
    from app.services.morphology_readmodel import build_morphology_readmodel

    with _session() as db:
        return build_morphology_readmodel(db, _uid())


def _section(client) -> str:
    """The morphology card only, so neighbouring copy cannot mask a defect."""
    page = client.get(PROFILE_URL).text
    start = page.index(MORPHO_TITLE)
    return page[start:page.index("</section>", start)]


def _visible_text(client) -> str:
    """The section with markup removed — what a reader actually sees.

    Needed because inline styles carry `width:100%`, which is a layout value
    and not a confidence shown to anyone. Scanning raw HTML for a percentage
    would fail on CSS and prove nothing about the copy.
    """
    import re

    return re.sub(r"<[^>]+>", " ", _section(client))


# ── États de données ─────────────────────────────────────────────────────────


def test_a_new_user_sees_the_surface_without_inventing_a_single_value(client):
    """**Migré par `UX4_01`, invariant conservé.**

    La garde exigeait que la surface ÉNUMÈRE chaque mesure absente
    (« Envergure non renseignée · Tour de taille non renseigné · … »). La
    décision opérateur du 2026-08-20 l'interdit : *un seul état vide représente
    le domaine et donne au plus un prochain pas véridique*. Sept façons de dire
    la même absence, et la liste s'allongeait à chaque champ ajouté au modèle.

    **L'invariant qui compte n'est pas l'énumération — c'est de ne rien
    inventer.** Il est conservé et durci : aucun chiffre ne doit apparaître
    dans l'état vide. Le read-model, lui, continue de nommer chaque manque —
    les gardes sur `rm.missing` sont inchangées.
    """
    section = _section(client)
    assert "Aucune mesure morphologique" in section
    # Aucune valeur inventée : pas un seul chiffre dans l'état vide.
    import re
    assert not re.search(r"\d", _visible_text(client)), (
        "un nombre apparaît alors qu'aucune mesure n'existe"
    )


def test_partial_measurements_show_what_exists_and_name_what_does_not():
    with _session() as db:
        _add(db, _uid(), waist_cm=80.0)
    rm = _readmodel()
    keys = {f.key for f in rm.facts}
    assert "waist_cm" in keys
    assert "chest_cm" not in keys
    assert WINGSPAN_MISSING in rm.missing


def test_a_full_profile_exposes_every_supported_fact():
    with _session() as db:
        uid = _uid()
        _set_height(db, uid, 180)
        _add(db, uid, wingspan_cm=186.0, waist_cm=78.0, chest_cm=104.0,
             thigh_cm_left=60.0, thigh_cm_right=60.0,
             calf_cm_left=38.0, calf_cm_right=38.0)
    rm = _readmodel()
    assert {f.key for f in rm.facts} == {
        "height_cm", "wingspan_cm", "waist_cm", "chest_cm", "thigh_cm", "calf_cm",
    }
    assert rm.missing == ()


def test_mixed_date_facts_are_announced_as_such():
    with _session() as db:
        uid = _uid()
        _add(db, uid, days_ago=60, chest_cm=100.0)
        _add(db, uid, days_ago=1, waist_cm=80.0)
    rm = _readmodel()
    assert rm.is_mixed_date is True
    assert "dates différentes" in rm.mixed_date_notice


def test_the_readmodel_runs_without_any_observation():
    """No observation surface exists; the read model must not require one."""
    with _session() as db:
        uid = _uid()
        _set_height(db, uid, 180)
        _add(db, uid, waist_cm=78.0, chest_cm=104.0)
    rm = _readmodel()
    assert rm.has_anything


# ── Envergure absente ────────────────────────────────────────────────────────


def test_a_missing_wingspan_is_named_not_neutralised():
    with _session() as db:
        uid = _uid()
        _set_height(db, uid, 180)
        _add(db, uid, waist_cm=80.0)
    rm = _readmodel()
    assert rm.ape_index is None
    assert WINGSPAN_MISSING in rm.missing


def test_the_page_never_shows_a_neutral_ape_index(client):
    """Absence of the row is the invariant — not the absence of a phrasing.

    An earlier version only banned the literals "ape index neutre" and
    "ape index : 0". Planting a `value=0.0, basis="neutre"` fallback left this
    test green, because the rendered cells never spell either phrase. It now
    asserts the row is simply not there.
    """
    with _session() as db:
        uid = _uid()
        _set_height(db, uid, 180)
        _add(db, uid, waist_cm=80.0)
    text = _visible_text(client).lower()
    assert "ape index" not in text
    # `UX4_01` — la surface n'énumère plus les manques (décision n°5) ; c'est
    # le read-model qui les nomme, et les gardes sur `rm.missing` le vérifient.
    # Ce qui est gardé ici reste l'essentiel : **aucun indice dérivé n'apparaît
    # tant que ses deux faits n'existent pas**.
    assert WINGSPAN_MISSING in _readmodel().missing


def test_the_ape_index_appears_only_when_both_facts_exist():
    with _session() as db:
        uid = _uid()
        _set_height(db, uid, 180)
        _add(db, uid, wingspan_cm=186.0)
    rm = _readmodel()
    assert rm.ape_index is not None
    assert rm.ape_index.value == 6.0


# ── Interprétations ──────────────────────────────────────────────────────────


def test_every_interpretation_exposes_layer_confidence_and_evidence():
    with _session() as db:
        uid = _uid()
        _set_height(db, uid, 180)
        _add(db, uid, wingspan_cm=186.0, waist_cm=78.0, chest_cm=104.0)
    rm = _readmodel()
    assert rm.interpretations
    for i in rm.interpretations:
        assert i.layer_label
        assert i.confidence_label
        assert i.evidence
        assert i.rationale


def test_confidence_is_a_category_never_a_percentage():
    with _session() as db:
        uid = _uid()
        _set_height(db, uid, 180)
        _add(db, uid, wingspan_cm=186.0, waist_cm=78.0, chest_cm=104.0)
    rm = _readmodel()
    for i in rm.interpretations:
        assert "%" not in i.confidence_label


def test_descriptors_are_deterministic():
    with _session() as db:
        uid = _uid()
        _set_height(db, uid, 180)
        _add(db, uid, wingspan_cm=186.0, waist_cm=78.0, chest_cm=104.0)
    first = _readmodel()
    second = _readmodel()
    assert [i.descriptor_id for i in first.interpretations] == \
        [i.descriptor_id for i in second.interpretations]


def test_fact_descriptors_are_not_duplicated_as_interpretations():
    with _session() as db:
        uid = _uid()
        _set_height(db, uid, 180)
        _add(db, uid, waist_cm=78.0)
    rm = _readmodel()
    assert not any(i.descriptor_id.startswith("fact_") for i in rm.interpretations)


# ── Garde de formulation ─────────────────────────────────────────────────────

FORBIDDEN_COPY = (
    "diagnostic", "diagnostique", "pathologie", "posture", "insertion",
    "fémur", "humérus", "longueur osseuse", "masse grasse", "body fat",
    "morphotype", "ectomorphe", "endomorphe", "mésomorphe",
    "blessure", "risque de blessure", "morphologie optimale", "optimal",
    "tu es fait pour", "génétique",
)


@pytest.mark.parametrize("banned", FORBIDDEN_COPY)
def test_the_rendered_section_never_uses_forbidden_wording(client, banned):
    with _session() as db:
        uid = _uid()
        _set_height(db, uid, 180)
        _add(db, uid, wingspan_cm=186.0, waist_cm=78.0, chest_cm=104.0,
             thigh_cm_left=60.0, thigh_cm_right=60.0, calf_cm_left=38.0,
             calf_cm_right=38.0)
    assert banned not in _section(client).lower()


def test_the_rendered_section_shows_no_percentage_confidence(client):
    import re

    with _session() as db:
        uid = _uid()
        _set_height(db, uid, 180)
        _add(db, uid, wingspan_cm=186.0, waist_cm=78.0, chest_cm=104.0)
    assert not re.search(r"\d+\s*%", _visible_text(client))


def test_the_engine_denial_is_not_rendered_to_the_user(client):
    """The guardrail is a denial — printing it puts the medical frame in view.

    It stays available on the read model for audit, and off the page.
    """
    with _session() as db:
        uid = _uid()
        _set_height(db, uid, 180)
        _add(db, uid, wingspan_cm=186.0, waist_cm=78.0, chest_cm=104.0)
    rm = _readmodel()
    assert any(i.guardrail for i in rm.interpretations)   # kept for audit
    assert "aucun diagnostic" not in _section(client).lower()


# ── Aucune promesse de conséquence ───────────────────────────────────────────


def test_the_surface_states_that_the_program_is_not_affected_yet(client):
    section = _section(client)
    assert "ne modifient pas encore automatiquement ton programme" in section


@pytest.mark.parametrize(
    "promise",
    ["change ton programme", "adapte ton programme", "ton programme a été"],
)
def test_the_surface_promises_no_planner_effect(client, promise):
    assert promise not in _section(client).lower()


# ── Surface ──────────────────────────────────────────────────────────────────


def test_the_surface_lives_on_the_existing_profile_page(client):
    assert MORPHO_TITLE in client.get(PROFILE_URL).text


def test_no_dedicated_morphology_route_is_added(client):
    for path in ("/morphologie", "/morphology"):
        assert client.get(path, follow_redirects=False).status_code == 404


def test_the_section_is_labelled_for_assistive_technology(client):
    page = client.get(PROFILE_URL).text
    assert 'aria-labelledby="morpho-title"' in page
    assert 'id="morpho-title"' in page


def test_the_table_has_scoped_headers_and_a_caption(client):
    with _session() as db:
        _add(db, _uid(), waist_cm=80.0)
    section = _section(client)
    assert "<caption" in section
    assert 'scope="col"' in section
    assert 'scope="row"' in section


# ── Isolation du planificateur ───────────────────────────────────────────────


def test_the_readmodel_module_is_read_only_by_construction():
    """No write API reaches the database from this module."""
    import pathlib

    import app.services as services_pkg

    src = (pathlib.Path(services_pkg.__file__).parent
           / "morphology_readmodel.py").read_text(encoding="utf-8")
    for banned in ("db.add(", "db.commit(", "db.delete(", "db.merge("):
        assert banned not in src


def test_no_frozen_planner_module_imports_the_readmodel():
    import pathlib

    import app.services as services_pkg

    root = pathlib.Path(services_pkg.__file__).parent
    for name in ("weekly_volume_budget", "weekly_planner",
                 "weekly_capacity_allocator", "weekly_set_allocation",
                 "weekly_plan_materialization", "set_contribution",
                 "adaptive_replan", "recommendation"):
        src = (root / f"{name}.py").read_text(encoding="utf-8")
        assert "morphology_readmodel" not in src, name


def test_reading_the_profile_does_not_move_the_weekly_plan(client):
    from app.services.training_preferences import TrainingPreferencesData
    from app.services.weekly_planner import build_weekly_plan

    prefs = TrainingPreferencesData(
        sessions_per_week=4, focus_priorities=("arms",),
    )
    before = build_weekly_plan(prefs)

    with _session() as db:
        uid = _uid()
        _set_height(db, uid, 180)
        _add(db, uid, wingspan_cm=188.0, waist_cm=78.0, chest_cm=104.0)
    client.get(PROFILE_URL)

    after = build_weekly_plan(prefs)
    assert after.fingerprint == before.fingerprint
