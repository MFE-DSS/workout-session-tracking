"""Sb_TRAINING_PREFERENCES_01 — préférences d'entraînement déclarées.

Première persistance de préférences du dépôt. Les tests portent donc autant sur
ce qui est **stocké** que sur ce qui ne l'est **pas** : la garantie centrale de
la tranche est qu'une préférence non déclarée ne devient jamais un fait.

Quatre familles :

1. **contrat de valeur** — vocabulaires fermés, bornes, `NULL` ≠ `[]` ;
2. **aucun défaut caché** — rien n'invente 3 séances ni « tout le matériel » ;
3. **propriété** — un utilisateur ne lit ni n'écrit les préférences d'un autre,
   et un `user_id` forgé dans le formulaire n'échappe pas au scope authentifié ;
4. **isolation** — recommandation, chaîne P0.4 et moteur de qualité inchangés.
"""
from __future__ import annotations

import inspect
import json

import pytest

from tests.helpers import get_test_user_id

PROFILE_URL = "/profile"
PREFERENCES_URL = "/profile/preferences"
LABEL_MEDIUM_CADENCE = "Séances souhaitées par semaine"
AXIS_LOWER = "lower"
AXIS_ARMS = "arms"
FAM_CABLE = "cable"
FAM_BARBELL = "barbell"
FIELD_CADENCE = "sessions_per_week"
FIELD_FOCUS_1 = "focus_1"
FIELD_FOCUS_2 = "focus_2"


# ─────────────────── helpers ───────────────────


def _service():
    from app.services import training_preferences

    return training_preferences


def _code_only(module) -> str:
    """Source du module **sans les docstrings**.

    Les gardes de ce fichier interdisent des symboles (`WeeklyPlanner`,
    `WorkoutSession`…) dans le **code**. Les docstrings, elles, doivent pouvoir
    nommer ces concepts pour expliquer précisément ce qui n'est PAS fait — un
    scan brut ferait échouer le module sur sa propre documentation.
    """
    import ast

    tree = ast.parse(inspect.getsource(module))
    for node in ast.walk(tree):
        if not isinstance(
            node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
        ):
            continue
        body = node.body
        if (
            body
            and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)
        ):
            body.pop(0)
    return ast.unparse(tree)


def _read(uid):
    from app.database import SessionLocal
    from app.services.training_preferences import get_training_preferences

    with SessionLocal() as db:
        return get_training_preferences(db, uid)


def _write(uid, **kwargs):
    from app.database import SessionLocal
    from app.services.training_preferences import save_training_preferences

    with SessionLocal() as db:
        return save_training_preferences(db, uid, **kwargs)


# ─────────────────── modèle / migration ───────────────────


class TestModelAndMigration:
    def test_the_table_exists_at_head(self, client):
        from sqlalchemy import inspect as sa_inspect

        from app.database import engine

        assert "training_preferences" in sa_inspect(engine).get_table_names()

    def test_no_row_is_fabricated_by_the_migration(self, client):
        """La garantie la plus importante : zéro backfill, pour personne."""
        from app.database import SessionLocal
        from app.models.training_preferences import TrainingPreferences

        with SessionLocal() as db:
            assert db.query(TrainingPreferences).count() == 0

    def test_an_existing_user_is_valid_without_a_row(self, client):
        assert _read(get_test_user_id()).is_empty is True

    def test_a_user_without_a_row_gets_the_named_undeclared_object(self, client):
        from app.services.training_preferences import UNDECLARED

        assert _read(get_test_user_id()) == UNDECLARED

    def test_one_row_per_user_is_enforced_by_the_database(self, client):
        """L'unicité est une contrainte, pas une convention applicative."""
        from sqlalchemy.exc import IntegrityError

        from app.database import SessionLocal
        from app.models.training_preferences import TrainingPreferences

        uid = get_test_user_id()
        _write(uid, sessions_per_week=3)
        with SessionLocal() as db:
            db.add(TrainingPreferences(user_id=uid))
            with pytest.raises(IntegrityError):
                db.commit()

    def test_existing_user_data_is_untouched(self, client):
        """La migration n'écrit rien ailleurs."""
        from app.database import SessionLocal
        from app.models.user import User

        uid = get_test_user_id()
        with SessionLocal() as db:
            before = db.get(User, uid).username
        _write(uid, sessions_per_week=4)
        with SessionLocal() as db:
            assert db.get(User, uid).username == before

    def test_the_migration_is_additive_only(self, client):
        import pathlib

        source = pathlib.Path(
            "migrations/versions/20260813_add_training_preferences.py"
        ).read_text(encoding="utf-8")
        upgrade = source.split("def upgrade", 1)[1].split("def downgrade", 1)[0]
        for forbidden in ("drop_column", "DELETE", "UPDATE", "drop_constraint"):
            assert forbidden not in upgrade

    def test_the_migration_creates_no_row(self, client):
        import pathlib

        source = pathlib.Path(
            "migrations/versions/20260813_add_training_preferences.py"
        ).read_text(encoding="utf-8")
        assert "INSERT" not in source.upper()


# ─────────────────── cadence ───────────────────


class TestSessionsPerWeek:
    @pytest.mark.parametrize("value", [1, 2, 3, 4, 5, 6, 7])
    def test_the_whole_declared_range_is_accepted(self, client, value):
        assert _write(get_test_user_id(),
                      sessions_per_week=value).sessions_per_week == value

    def test_zero_is_rejected(self, client):
        from app.services.training_preferences import PreferenceValidationError

        uid = get_test_user_id()
        with pytest.raises(PreferenceValidationError):
            _write(uid, sessions_per_week=0)

    def test_eight_is_rejected(self, client):
        from app.services.training_preferences import PreferenceValidationError

        uid = get_test_user_id()
        with pytest.raises(PreferenceValidationError):
            _write(uid, sessions_per_week=8)

    def test_none_is_preserved_as_undeclared(self, client):
        _write(get_test_user_id(), sessions_per_week=None)
        assert _read(get_test_user_id()).sessions_per_week is None

    def test_a_boolean_is_not_a_cadence(self, client):
        """`True` vaut 1 en Python — il ne vaut pas « une séance »."""
        from app.services.training_preferences import PreferenceValidationError

        uid = get_test_user_id()
        with pytest.raises(PreferenceValidationError):
            _write(uid, sessions_per_week=True)

    def test_a_string_is_rejected(self, client):
        from app.services.training_preferences import PreferenceValidationError

        uid = get_test_user_id()
        with pytest.raises(PreferenceValidationError):
            _write(uid, sessions_per_week="3")

    def test_a_rejected_value_persists_nothing(self, client):
        """Valider avant de persister : un refus ne laisse pas d'état partiel."""
        from app.services.training_preferences import PreferenceValidationError

        uid = get_test_user_id()
        _write(uid, sessions_per_week=4)
        with pytest.raises(PreferenceValidationError):
            _write(uid, sessions_per_week=99, focus_priorities=[AXIS_ARMS])
        assert _read(uid).sessions_per_week == 4


# ─────────────────── priorités ───────────────────


class TestFocusPriorities:
    def test_the_vocabulary_is_the_canonical_radar_axes(self, client):
        from app.services.muscle_mapping import RADAR_AXIS_ORDER
        from app.services.training_preferences import FOCUS_PRIORITY_VOCAB

        assert list(FOCUS_PRIORITY_VOCAB) == list(RADAR_AXIS_ORDER)

    def test_canonical_values_are_accepted(self, client):
        saved = _write(get_test_user_id(), focus_priorities=[AXIS_ARMS, AXIS_LOWER])
        assert saved.focus_priorities == (AXIS_ARMS, AXIS_LOWER)

    def test_order_is_preserved_exactly(self, client):
        uid = get_test_user_id()
        _write(uid, focus_priorities=[AXIS_LOWER, "pecs", AXIS_ARMS])
        assert _read(uid).focus_priorities == (AXIS_LOWER, "pecs", AXIS_ARMS)

    def test_order_survives_a_full_round_trip(self, client):
        uid = get_test_user_id()
        ordered = ["back_thickness", "shoulders", "back_width"]
        _write(uid, focus_priorities=ordered)
        first = _read(uid).focus_priorities
        _write(uid, focus_priorities=list(first))
        assert _read(uid).focus_priorities == tuple(ordered)

    def test_an_unknown_priority_is_rejected(self, client):
        from app.services.training_preferences import PreferenceValidationError

        uid = get_test_user_id()
        with pytest.raises(PreferenceValidationError):
            _write(uid, focus_priorities=["biceps_peak"])

    def test_a_duplicate_is_rejected_not_silently_deduplicated(self, client):
        """Dans une liste ordonnée, un doublon rend le rang ambigu."""
        from app.services.training_preferences import PreferenceValidationError

        uid = get_test_user_id()
        with pytest.raises(PreferenceValidationError):
            _write(uid, focus_priorities=[AXIS_ARMS, AXIS_ARMS])

    def test_null_is_not_empty(self, client):
        uid = get_test_user_id()
        _write(uid, focus_priorities=None)
        assert _read(uid).focus_priorities is None

    def test_empty_is_an_explicit_declaration(self, client):
        uid = get_test_user_id()
        _write(uid, focus_priorities=[])
        assert _read(uid).focus_priorities == ()

    def test_empty_and_null_are_distinguishable_in_storage(self, client):
        from app.database import SessionLocal
        from app.models.training_preferences import TrainingPreferences

        uid = get_test_user_id()
        _write(uid, focus_priorities=[])
        with SessionLocal() as db:
            row = db.query(TrainingPreferences).filter_by(user_id=uid).one()
            assert row.focus_priorities == "[]"

    def test_null_is_stored_as_sql_null(self, client):
        from app.database import SessionLocal
        from app.models.training_preferences import TrainingPreferences

        uid = get_test_user_id()
        _write(uid, focus_priorities=None)
        with SessionLocal() as db:
            row = db.query(TrainingPreferences).filter_by(user_id=uid).one()
            assert row.focus_priorities is None

    def test_a_morphology_candidate_is_never_auto_written(self, client):
        """Priorité déclarée ≠ candidat morphologique : sources séparées."""
        source = _code_only(_service())
        assert "build_morphology_profile" not in source

    def test_the_service_does_not_read_morphology_at_all(self, client):
        assert "morphology_profile" not in _code_only(_service())

    def test_the_morphology_vocabulary_is_not_reused(self, client):
        """Les 4 jetons morphologiques ne sont pas un vocabulaire de priorité."""
        from app.services.morphology_profile import FOCUS_CANDIDATE_VOCAB
        from app.services.training_preferences import FOCUS_PRIORITY_VOCAB

        assert not (set(FOCUS_CANDIDATE_VOCAB) & set(FOCUS_PRIORITY_VOCAB))

    def test_core_cannot_be_prioritised(self, client):
        """`core` n'appartient à aucun axe radar — limite assumée, pas un oubli."""
        from app.services.training_preferences import PreferenceValidationError

        uid = get_test_user_id()
        with pytest.raises(PreferenceValidationError):
            _write(uid, focus_priorities=["core"])


# ─────────────────── équipement ───────────────────


class TestAvailableEquipment:
    def test_the_vocabulary_matches_the_canonical_referential(self, client):
        """Aligné sur la donnée, prouvé par test plutôt que supposé."""
        from app.services.substitution import load_exercise_properties
        from app.services.training_preferences import EQUIPMENT_FAMILY_VOCAB

        families = {
            props.get("equipment_family")
            for props in load_exercise_properties().values()
            if props.get("equipment_family")
        }
        assert set(EQUIPMENT_FAMILY_VOCAB) == families

    def test_canonical_families_are_accepted(self, client):
        saved = _write(get_test_user_id(),
                       available_equipment=["dumbbell", FAM_CABLE])
        assert set(saved.available_equipment) == {"dumbbell", FAM_CABLE}

    def test_an_unknown_family_is_rejected(self, client):
        from app.services.training_preferences import PreferenceValidationError

        uid = get_test_user_id()
        with pytest.raises(PreferenceValidationError):
            _write(uid, available_equipment=["kettlebell"])

    def test_duplicates_are_normalised_deterministically(self, client):
        """Sémantique d'ensemble : deux fois la même famille est la même chose."""
        saved = _write(get_test_user_id(),
                       available_equipment=[FAM_CABLE, FAM_CABLE, FAM_BARBELL])
        assert saved.available_equipment == (FAM_BARBELL, FAM_CABLE)

    def test_the_stored_order_is_canonical_not_input_order(self, client):
        first = _write(get_test_user_id(),
                       available_equipment=["smith", FAM_BARBELL])
        second = _write(get_test_user_id(),
                        available_equipment=[FAM_BARBELL, "smith"])
        assert first.available_equipment == second.available_equipment

    def test_null_is_not_empty(self, client):
        uid = get_test_user_id()
        _write(uid, available_equipment=None)
        assert _read(uid).available_equipment is None

    def test_empty_is_an_explicit_declaration(self, client):
        uid = get_test_user_id()
        _write(uid, available_equipment=[])
        assert _read(uid).available_equipment == ()

    def test_nothing_is_inferred_from_logged_history(self, client):
        source = _code_only(_service())
        assert "WorkoutSession" not in source

    def test_no_specific_gym_is_assumed(self, client):
        source = inspect.getsource(_service()).lower()
        assert "fitness park" not in source


# ─────────────────── aucun défaut caché ───────────────────


class TestNoHiddenDefaults:
    def test_a_fresh_user_declares_nothing(self, client):
        prefs = _read(get_test_user_id())
        assert (prefs.sessions_per_week, prefs.focus_priorities,
                prefs.available_equipment) == (None, None, None)

    def test_saving_only_a_cadence_leaves_the_rest_undeclared(self, client):
        uid = get_test_user_id()
        _write(uid, sessions_per_week=5)
        prefs = _read(uid)
        assert (prefs.focus_priorities, prefs.available_equipment) == (None, None)

    def test_no_default_cadence_appears_in_the_service(self, client):
        source = inspect.getsource(_service())
        assert "sessions_per_week = 3" not in source

    def test_no_all_equipment_shortcut_exists(self, client):
        source = inspect.getsource(_service())
        assert "all_equipment" not in source

    def test_none_never_becomes_a_list_on_persistence(self, client):
        from app.services.training_preferences import _dump

        assert _dump(None) is None

    def test_an_empty_tuple_is_stored_distinctly(self, client):
        from app.services.training_preferences import _dump

        assert _dump(()) == "[]"

    def test_a_corrupt_stored_list_is_reported_not_replaced(self, client):
        """Du JSON illisible ne devient pas « aucune priorité déclarée »."""
        from app.database import SessionLocal
        from app.models.training_preferences import TrainingPreferences
        from app.services.training_preferences import PreferenceValidationError

        uid = get_test_user_id()
        _write(uid, focus_priorities=[AXIS_ARMS])
        with SessionLocal() as db:
            row = db.query(TrainingPreferences).filter_by(user_id=uid).one()
            row.focus_priorities = "{not json"
            db.commit()
        with pytest.raises(PreferenceValidationError):
            _read(uid)

    def test_a_non_list_stored_value_is_reported(self, client):
        from app.database import SessionLocal
        from app.models.training_preferences import TrainingPreferences
        from app.services.training_preferences import PreferenceValidationError

        uid = get_test_user_id()
        _write(uid, available_equipment=[FAM_CABLE])
        with SessionLocal() as db:
            row = db.query(TrainingPreferences).filter_by(user_id=uid).one()
            row.available_equipment = json.dumps({FAM_CABLE: True})
            db.commit()
        with pytest.raises(PreferenceValidationError):
            _read(uid)


# ─────────────────── service ───────────────────


class TestServiceBoundary:
    def test_reading_performs_no_write(self, client):
        from sqlalchemy import event

        from app.database import SessionLocal, engine

        uid = get_test_user_id()
        _write(uid, sessions_per_week=3)
        seen: list[str] = []

        def listener(_c, _cur, statement, *_a, **_k):
            seen.append(statement)

        event.listen(engine, "before_cursor_execute", listener)
        try:
            with SessionLocal() as db:
                from app.services.training_preferences import (
                    get_training_preferences,
                )

                get_training_preferences(db, uid)
        finally:
            event.remove(engine, "before_cursor_execute", listener)
        writes = [
            s for s in seen
            if s.strip().split()[0].upper() in {"INSERT", "UPDATE", "DELETE"}
        ]
        assert writes == []

    def test_upsert_is_stable_and_creates_one_row(self, client):
        from app.database import SessionLocal
        from app.models.training_preferences import TrainingPreferences

        uid = get_test_user_id()
        _write(uid, sessions_per_week=2)
        _write(uid, sessions_per_week=6)
        with SessionLocal() as db:
            assert db.query(TrainingPreferences).filter_by(user_id=uid).count() == 1

    def test_the_second_save_wins(self, client):
        uid = get_test_user_id()
        _write(uid, sessions_per_week=2)
        _write(uid, sessions_per_week=6)
        assert _read(uid).sessions_per_week == 6

    def test_a_save_replaces_the_whole_declared_state(self, client):
        """Le seul moyen de RETIRER une déclaration est de la réécrire."""
        uid = get_test_user_id()
        _write(uid, sessions_per_week=3, focus_priorities=[AXIS_ARMS])
        _write(uid, sessions_per_week=3)
        assert _read(uid).focus_priorities is None

    def test_no_module_level_cache_is_used(self, client):
        source = inspect.getsource(_service())
        assert "lru_cache" not in source

    def test_the_domain_object_is_immutable(self, client):
        from dataclasses import FrozenInstanceError

        from app.services.training_preferences import TrainingPreferencesData

        prefs = TrainingPreferencesData(sessions_per_week=3)
        with pytest.raises(FrozenInstanceError):
            prefs.sessions_per_week = 4


# ─────────────────── propriété / autorisation ───────────────────


def _make_second_user(client):
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.auth import hash_password

    with SessionLocal() as db:
        other = User(username="prefs-other", password_hash=hash_password("x" * 12))
        db.add(other)
        db.commit()
        return other.id


class TestOwnership:
    def test_a_user_reads_their_own_preferences(self, client):
        uid = get_test_user_id()
        _write(uid, sessions_per_week=5)
        assert _read(uid).sessions_per_week == 5

    def test_another_users_preferences_are_not_visible(self, client):
        uid = get_test_user_id()
        other = _make_second_user(client)
        _write(uid, sessions_per_week=5)
        assert _read(other).sessions_per_week is None

    def test_writing_for_one_user_does_not_mutate_the_other(self, client):
        uid = get_test_user_id()
        other = _make_second_user(client)
        _write(uid, sessions_per_week=5)
        _write(other, sessions_per_week=2)
        assert _read(uid).sessions_per_week == 5

    def test_the_route_ignores_a_forged_user_id(self, client):
        """Le propriétaire vient de la session, jamais du formulaire."""
        other = _make_second_user(client)
        client.post(PREFERENCES_URL,
                    data={FIELD_CADENCE: "6", "user_id": str(other)})
        assert _read(other).sessions_per_week is None

    def test_the_forged_post_still_wrote_to_the_authenticated_owner(self, client):
        other = _make_second_user(client)
        client.post(PREFERENCES_URL,
                    data={FIELD_CADENCE: "6", "user_id": str(other)})
        assert _read(get_test_user_id()).sessions_per_week == 6

    def test_the_route_rejects_an_unauthenticated_caller(self, client):
        from fastapi.testclient import TestClient

        from app.database import SessionLocal
        from app.main import app
        from app.models.user import User

        with SessionLocal() as db:
            assert db.query(User).count() >= 1
        with TestClient(app) as anon:
            response = anon.post(PREFERENCES_URL, data={FIELD_CADENCE: "5"},
                                 follow_redirects=False)
        assert response.status_code in (302, 303, 401, 403)


# ─────────────────── surface de saisie ───────────────────


class TestCaptureSurface:
    def test_the_profile_page_exposes_the_form(self, client):
        assert LABEL_MEDIUM_CADENCE in client.get(PROFILE_URL).text

    def test_a_new_user_has_no_preselected_cadence(self, client):
        """Aucune valeur par défaut ne doit être proposée comme choix fait."""
        page = client.get(PROFILE_URL).text
        section = page.split(LABEL_MEDIUM_CADENCE, 1)[1][:600]
        assert "selected" not in section

    def test_the_undeclared_equipment_state_is_visible(self, client):
        page = client.get(PROFILE_URL).text
        assert "pas encore renseigné mon équipement" in page

    def test_saved_values_round_trip_to_the_page(self, client):
        client.post(PREFERENCES_URL, data={
            FIELD_CADENCE: "4",
            FIELD_FOCUS_1: AXIS_ARMS,
            "equipment_declared": "1",
            "equipment": [FAM_CABLE],
        })
        assert _read(get_test_user_id()).sessions_per_week == 4

    def test_saved_priorities_round_trip(self, client):
        client.post(PREFERENCES_URL, data={
            FIELD_CADENCE: "",
            FIELD_FOCUS_1: AXIS_LOWER,
            FIELD_FOCUS_2: AXIS_ARMS,
        })
        assert _read(get_test_user_id()).focus_priorities == (AXIS_LOWER, AXIS_ARMS)

    def test_an_untouched_equipment_section_declares_nothing(self, client):
        client.post(PREFERENCES_URL, data={FIELD_CADENCE: "3"})
        assert _read(get_test_user_id()).available_equipment is None

    def test_a_submitted_empty_equipment_section_is_an_explicit_declaration(
        self, client
    ):
        client.post(PREFERENCES_URL,
                    data={FIELD_CADENCE: "3", "equipment_declared": "1"})
        assert _read(get_test_user_id()).available_equipment == ()

    def test_a_duplicate_priority_does_not_crash_the_route(self, client):
        response = client.post(PREFERENCES_URL,
                               data={FIELD_FOCUS_1: AXIS_ARMS, FIELD_FOCUS_2: AXIS_ARMS},
                               follow_redirects=False)
        assert response.status_code == 303

    def test_a_duplicate_priority_persists_nothing(self, client):
        client.post(PREFERENCES_URL, data={FIELD_FOCUS_1: AXIS_ARMS, FIELD_FOCUS_2: AXIS_ARMS})
        assert _read(get_test_user_id()).focus_priorities is None

    @pytest.mark.parametrize("banned", [
        "optimal", "idéal", "fréquence recommandée", "meilleure fréquence",
        "conseillé", "tu devrais",
    ])
    def test_the_page_presents_no_frequency_as_optimal(self, client, banned):
        """Une cadence déclarée n'est jamais présentée comme la bonne.

        Le mot « recommandé » n'est **pas** banni tel quel : la section dit
        explicitement qu'elle ne modifie pas « la séance recommandée
        aujourd'hui », et cette phrase est précisément la garantie produit.
        Ce qui est interdit, c'est de qualifier **la fréquence**.
        """
        page = client.get(PROFILE_URL).text.lower()
        section = page.split("préférences d'entraînement", 1)[-1][:2500]
        assert banned not in section

    def test_the_form_labels_the_cadence_as_a_wish(self, client):
        assert "souhaitées" in client.get(PROFILE_URL).text

    def test_equipment_is_shown_with_presentation_labels(self, client):
        page = client.get(PROFILE_URL).text
        assert "Haltères" in page

    def test_priorities_use_the_canonical_axis_labels(self, client):
        from app.services.muscle_mapping import RADAR_AXES

        page = client.get(PROFILE_URL).text
        assert RADAR_AXES[AXIS_LOWER]["label"] in page

    def test_the_form_adds_no_javascript(self, client):
        import pathlib

        markup = pathlib.Path("app/templates/profile.html").read_text(
            encoding="utf-8")
        block = markup.split("Sb_TRAINING_PREFERENCES_01", 1)[-1].split(
            "Changer le mot de passe", 1)[0]
        assert "<script" not in block

    def test_the_form_adds_no_horizontal_overflow(self, client):
        import pathlib

        markup = pathlib.Path("app/templates/profile.html").read_text(
            encoding="utf-8")
        block = markup.split("Sb_TRAINING_PREFERENCES_01", 1)[-1].split(
            "Changer le mot de passe", 1)[0]
        assert "white-space:nowrap" not in block

    def test_every_control_has_a_label(self, client):
        page = client.get(PROFILE_URL).text
        assert f'for="{FIELD_CADENCE}"' in page


# ─────────────────── isolation ───────────────────


class TestIsolation:
    def test_the_recommendation_engine_never_reads_preferences(self, client):
        from app.services import recommendation

        assert "training_preferences" not in inspect.getsource(recommendation)

    def test_the_behavioural_producer_never_reads_preferences(self, client):
        from app.services import behavioral

        assert "training_preferences" not in inspect.getsource(behavioral)

    def test_the_recommendation_is_unchanged_by_declared_preferences(self, client):
        """Preuve exécutée : déclarer des préférences ne déplace pas la reco."""
        from app.database import SessionLocal
        from app.models.user import User
        from app.services.home import build_home_payload

        uid = get_test_user_id()
        with SessionLocal() as db:
            before = build_home_payload(db, db.get(User, uid))
        _write(uid, sessions_per_week=7, focus_priorities=[AXIS_ARMS, AXIS_LOWER],
               available_equipment=[FAM_BARBELL])
        with SessionLocal() as db:
            after = build_home_payload(db, db.get(User, uid))
        assert after["today"] == before["today"]

    def test_the_recovery_chain_is_unchanged_by_declared_preferences(self, client):
        from datetime import UTC, datetime

        from app.database import SessionLocal
        from app.services.training_state import build_training_state

        now = datetime(2026, 8, 13, 9, 0, tzinfo=UTC)
        uid = get_test_user_id()
        with SessionLocal() as db:
            before = build_training_state(db, uid, now=now)
        _write(uid, available_equipment=[FAM_BARBELL, "machine"])
        with SessionLocal() as db:
            after = build_training_state(db, uid, now=now)
        assert after == before

    def test_declared_equipment_does_not_populate_training_state(self, client):
        """Déféré exprès : la disponibilité déclarée n'est pas biologique."""
        from datetime import UTC, datetime

        from app.database import SessionLocal
        from app.services.training_state import build_training_state

        uid = get_test_user_id()
        _write(uid, available_equipment=[FAM_BARBELL])
        with SessionLocal() as db:
            state = build_training_state(
                db, uid, now=datetime(2026, 8, 13, 9, 0, tzinfo=UTC))
        assert state.equipment is None

    def test_the_pure_quality_profile_stays_pure(self, client):
        from app.services import program_quality_engine

        source = inspect.getsource(program_quality_engine)
        assert "training_preferences" not in source

    def test_the_service_writes_no_program_or_session_data(self, client):
        source = _code_only(_service())
        for foreign in ("UserProgram", "WorkoutSession", "BodyZone"):
            assert foreign not in source

    def test_no_weekly_planner_was_started(self, client):
        source = _code_only(_service())
        assert "WeeklyPlan" not in source

    def test_no_volume_budget_was_started(self, client):
        source = _code_only(_service())
        assert "VolumeBudget" not in source


# ─────────────────── garde-fou scientifique ───────────────────


class TestScientificGuardrail:
    def test_the_service_makes_no_optimality_claim(self, client):
        source = inspect.getsource(_service()).lower()
        assert "optimal" not in source

    def test_the_service_uses_no_medical_language(self, client):
        source = inspect.getsource(_service()).lower()
        for banned in ("diagnostic", "blessure", "patholog", "thérapeut"):
            assert banned not in source

    def test_the_cadence_bounds_are_documented_as_structural(self, client):
        source = inspect.getsource(_service())
        assert "sept jours" in source
