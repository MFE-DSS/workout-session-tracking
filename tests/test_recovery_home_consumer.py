"""Sb_RECOVERY_HOME_CONSUMER_01 — la chaîne P0.4 rendue visible sur la Home.

Premier consommateur vivant. Ces tests portent donc sur **la Home réellement
rendue** depuis une base persistée, pas seulement sur la vue-modèle : ce qui
compte désormais est ce qu'un humain lit.

Trois familles de garanties :

1. **produit** — ce qui s'affiche, avec quelle confiance, et ce qui reste
   silencieux quand la preuve manque ;
2. **non-régression de décision** — la recommandation existante est identique
   avec et sans la tuile ;
3. **exploitation** — une seule agrégation par requête, aucune écriture, et une
   panne de la tuile ne coûte pas la Home.
"""
from __future__ import annotations

import html
import inspect
import pathlib
from datetime import UTC, datetime, timedelta

from sqlalchemy import event

from tests.helpers import get_test_user_id

#: Ancré sur l'horloge **réelle**, et non sur une date figée.
#:
#: Correctif d'un défaut introduit par `Sb_RECOVERY_HOME_CONSUMER_01` : plusieurs
#: tests comparent la vue-modèle (construite avec ce `NOW`) au HTML rendu par
#: `GET /`, qui utilise forcément l'horloge réelle. Avec une date figée, les deux
#: coïncidaient le jour de l'écriture puis divergeaient : une séance « il y a
#: 1 jour » relative à la constante vieillit d'un jour de plus chaque jour réel,
#: change de bande de récupération, et le message rendu cesse de correspondre.
#: Le test échouait donc à retardement, sans qu'aucun code produit n'ait bougé.
#:
#: Toutes les échéances de ce fichier sont **relatives** à cette ancre, donc la
#: rendre réelle aligne les deux horloges définitivement.
NOW = datetime.now(UTC)

CHEST = "Développé couché barre"
LEGS = "Hack squat"
#: Nom présent dans le référentiel canonique : résout par la table de mapping,
#: donc `Confidence.MEDIUM`. Les autres retombent sur le classifieur par
#: sous-chaîne et restent en `LOW`.
CANONICAL = "Traction assistée machine"
#: Fixture cardio unique — le vélo est une modalité nommable du
#: vocabulaire fermé, et les calories/BPM sont présents exprès pour
#: prouver qu'ils ne ressortent jamais.
CARDIO_VELO = {"duration": 25, "bpm": 130,
               "machine": "velo", "calories": 300}
TILE_LABEL = "État d'entraînement"
LEGACY_WIDGET_LABEL = "État du jour"
HOME_URL = "/"


# ─────────────────── fabriques (base réelle) ───────────────────


def _add_session(db, uid, *, days_ago=1, names=(), global_state=None,
                 concentration=None, cardio=None):
    from app.models.session import SessionExercise, WorkoutSession

    session = WorkoutSession(
        user_id=uid,
        template_slug_snapshot="push-a",
        template_name_snapshot="Push A",
        started_at=NOW.replace(tzinfo=None) - timedelta(days=days_ago),
        status="completed",
        global_state=global_state,
        concentration=concentration,
    )
    if cardio:
        session.cardio_duration_min = cardio.get("duration")
        session.cardio_bpm_avg = cardio.get("bpm")
        session.cardio_machine_type = cardio.get("machine")
        session.cardio_machine_calories = cardio.get("calories")
    for i, name in enumerate(names, start=1):
        session.session_exercises.append(SessionExercise(
            exercise_code_snapshot=f"E{i}",
            exercise_name_snapshot=name,
            position=i,
        ))
    db.add(session)
    db.commit()
    return session


def _add_readiness(db, uid, *, days_ago=0, value=4):
    from app.models.readiness import ReadinessEntry

    entry = ReadinessEntry(
        user_id=uid,
        recorded_on=NOW.date() - timedelta(days=days_ago),
        sleep_quality=value,
        soreness_level=value,
        stress_level=value,
        motivation_level=value,
        fatigue_level=value,
    )
    db.add(entry)
    db.commit()
    return entry


def _tile(uid):
    """La vue-modèle de la tuile, construite depuis la base réelle."""
    from app.database import SessionLocal
    from app.services.home_training_state import build_home_training_state

    with SessionLocal() as db:
        return build_home_training_state(db, uid, now=NOW)


def _page(client) -> str:
    """La Home rendue, entités HTML décodées.

    Jinja échappe l'apostrophe : « État d'entraînement » arrive dans la réponse
    en `État d&#39;entraînement`. Comparer la copie produit brute à la réponse
    échouerait donc pour une raison purement typographique, sans rien dire du
    produit — on compare sur le texte tel qu'un lecteur le voit.
    """
    return html.unescape(client.get(HOME_URL).text)


def _markup() -> str:
    return pathlib.Path(
        "app/templates/_partials/home_coaching_loop.html"
    ).read_text(encoding="utf-8")


TILE_BUILDER = "_build_training_state"
INJECTED_ERROR = "aggregator down"


def _break_the_tile(monkeypatch):
    """Neutralise la tuile par une panne injectée, sans toucher au reste.

    Sert deux fois : prouver le confinement de panne, et reproduire l'état
    « avant branchement » pour la parité de recommandation.
    """
    from app.services import home as home_module

    def boom(*_a, **_k):
        raise RuntimeError(INJECTED_ERROR)

    monkeypatch.setattr(home_module, TILE_BUILDER, boom)


def _count_queries(fn) -> list[str]:
    from app.database import engine

    seen: list[str] = []

    def listener(_conn, _cursor, statement, *_a, **_k):
        seen.append(statement)

    event.listen(engine, "before_cursor_execute", listener)
    try:
        fn()
    finally:
        event.remove(engine, "before_cursor_execute", listener)
    return seen


# ─────────────────── 1. compte réel avec preuves ───────────────────


class TestRendersWithEvidence:
    def test_home_renders_the_tile(self, client):
        uid = get_test_user_id()
        from app.database import SessionLocal

        with SessionLocal() as db:
            _add_session(db, uid, days_ago=1, names=[LEGS],
                         global_state="good", concentration="high")
        page = _page(client)
        assert TILE_LABEL in page

    def test_home_stays_200(self, client):
        uid = get_test_user_id()
        from app.database import SessionLocal

        with SessionLocal() as db:
            _add_session(db, uid, days_ago=1, names=[LEGS])
        assert client.get(HOME_URL).status_code == 200

    def test_the_tile_carries_an_actual_estimate(self, client):
        uid = get_test_user_id()
        from app.database import SessionLocal

        with SessionLocal() as db:
            _add_session(db, uid, days_ago=1, names=[LEGS])
        tile = _tile(uid)
        assert tile["insufficient"] is False

    def test_the_estimate_text_reaches_the_page(self, client):
        uid = get_test_user_id()
        from app.database import SessionLocal

        with SessionLocal() as db:
            _add_session(db, uid, days_ago=1, names=[LEGS])
        tile = _tile(uid)
        page = _page(client)
        assert tile["entries"][0]["message"] in page

    def test_density_is_capped(self, client):
        """Jamais un tableau de bord dans la Home."""
        uid = get_test_user_id()
        from app.database import SessionLocal
        from app.services.home_training_state import HOME_MAX_ITEMS

        with SessionLocal() as db:
            _add_readiness(db, uid)
            _add_session(db, uid, days_ago=1, names=[LEGS, CHEST],
                         global_state="good", concentration="high",
                         cardio=CARDIO_VELO)
            _add_session(db, uid, days_ago=2, names=[CHEST])
        assert len(_tile(uid)["entries"]) <= HOME_MAX_ITEMS

    def test_the_eleven_zones_are_not_dumped_on_home(self, client):
        uid = get_test_user_id()
        from app.database import SessionLocal
        from app.services.home_training_state import HOME_MAX_ZONE_ITEMS
        from app.services.muscle_mapping import ZONE_LABELS

        with SessionLocal() as db:
            _add_session(db, uid, days_ago=1,
                         names=[LEGS, CHEST, "Rowing barre", "Curl biceps",
                                "Mollets debout", "Gainage planche"])
        page = _page(client)
        shown = [
            label for label in ZONE_LABELS.values()
            if f"<b>{label}</b>" in page
        ]
        assert len(shown) <= HOME_MAX_ZONE_ITEMS


# ─────────────────── 2. compte neuf ───────────────────


class TestNewAccount:
    def test_at_most_one_data_state_message(self, client):
        tile = _tile(get_test_user_id())
        assert tile["entries"] == []

    def test_the_tile_is_flagged_insufficient(self, client):
        assert _tile(get_test_user_id())["insufficient"] is True

    def test_the_message_is_the_canonical_one(self, client):
        from app.services.recovery_explainer import GLOBAL_INSUFFICIENT_MESSAGE

        assert _tile(get_test_user_id())["message"] == GLOBAL_INSUFFICIENT_MESSAGE

    def test_the_message_speaks_of_data_not_of_a_body(self, client):
        assert "données" in _tile(get_test_user_id())["message"]

    def test_no_body_interpretation_is_rendered(self, client):
        page = _page(client)
        tile_zone = page.split(TILE_LABEL, 1)[-1][:800]
        assert "probablement disponible" not in tile_zone

    def test_no_fatigue_claim_is_rendered(self, client):
        page = _page(client)
        tile_zone = page.split(TILE_LABEL, 1)[-1][:800]
        assert "encore chargé" not in tile_zone

    def test_the_message_appears_once(self, client):
        from app.services.recovery_explainer import GLOBAL_INSUFFICIENT_MESSAGE

        page = _page(client)
        assert page.count(GLOBAL_INSUFFICIENT_MESSAGE) == 1

    def test_home_still_renders(self, client):
        assert client.get(HOME_URL).status_code == 200


# ─────────────────── 3-5. confiance ───────────────────


class TestConfidenceSurfacing:
    def test_medium_label_is_preserved(self, client):
        """MEDIUM exige une attribution formelle, pas une correspondance floue.

        `CANONICAL` est un nom du référentiel : il résout par la table de
        mapping et atteint donc `Confidence.MEDIUM`. Les noms résolus par
        sous-chaîne restent délibérément en `LOW`.
        """
        uid = get_test_user_id()
        from app.database import SessionLocal

        with SessionLocal() as db:
            _add_session(db, uid, days_ago=1, names=[CANONICAL])
        labels = [i["confidence_label"] for i in _tile(uid)["entries"]]
        assert "Confiance moyenne" in labels

    def test_a_confidence_label_reaches_the_page(self, client):
        uid = get_test_user_id()
        from app.database import SessionLocal

        with SessionLocal() as db:
            _add_session(db, uid, days_ago=1, names=[LEGS])
        assert "Confiance" in _page(client)

    def test_low_is_not_promoted_to_medium(self, client):
        """Une attribution par sous-chaîne reste une confiance faible."""
        uid = get_test_user_id()
        from app.database import SessionLocal

        with SessionLocal() as db:
            _add_session(db, uid, days_ago=1, names=["Exercice maison inconnu"])
        tile = _tile(uid)
        estimates = [i for i in tile["entries"] if i["is_estimate"]]
        for item in estimates:
            assert item["confidence_label"] != "Confiance moyenne"

    def test_no_percentage_is_ever_rendered_in_the_tile(self, client):
        uid = get_test_user_id()
        from app.database import SessionLocal

        with SessionLocal() as db:
            _add_session(db, uid, days_ago=1, names=[LEGS])
        for item in _tile(uid)["entries"]:
            assert "%" not in item["message"]

    def test_high_confidence_wording_never_appears(self, client):
        uid = get_test_user_id()
        from app.database import SessionLocal

        with SessionLocal() as db:
            _add_session(db, uid, days_ago=1, names=[LEGS])
        assert "Confiance élevée" not in _page(client)


# ─────────────────── 6-7. readiness ───────────────────


class TestReadinessOnHome:
    def test_a_stale_declaration_is_not_shown_proactively(self, client):
        uid = get_test_user_id()
        from app.database import SessionLocal

        with SessionLocal() as db:
            _add_readiness(db, uid, days_ago=30, value=5)
            _add_session(db, uid, days_ago=1, names=[LEGS])
        kinds = [i["kind"] for i in _tile(uid)["entries"]]
        assert "readiness" not in kinds

    def test_a_stale_declaration_makes_no_today_claim(self, client):
        uid = get_test_user_id()
        from app.database import SessionLocal

        with SessionLocal() as db:
            _add_readiness(db, uid, days_ago=30, value=5)
            _add_session(db, uid, days_ago=1, names=[LEGS])
        messages = " ".join(i["message"] for i in _tile(uid)["entries"])
        assert "aujourd'hui" not in messages

    def test_a_declaration_today_may_be_shown_as_declared(self, client):
        uid = get_test_user_id()
        from app.database import SessionLocal

        with SessionLocal() as db:
            _add_readiness(db, uid, days_ago=0, value=2)
            _add_session(db, uid, days_ago=1, names=[LEGS])
        messages = " ".join(i["message"] for i in _tile(uid)["entries"])
        assert "déclaré" in messages

    def test_good_readiness_emits_no_escalation(self, client):
        uid = get_test_user_id()
        from app.database import SessionLocal

        with SessionLocal() as db:
            _add_readiness(db, uid, days_ago=0, value=5)
            _add_session(db, uid, days_ago=1, names=[LEGS])
        messages = " ".join(i["message"] for i in _tile(uid)["entries"])
        assert "plus lourd" not in messages

    def test_good_readiness_prescribes_no_session(self, client):
        uid = get_test_user_id()
        from app.database import SessionLocal

        with SessionLocal() as db:
            _add_readiness(db, uid, days_ago=0, value=5)
            _add_session(db, uid, days_ago=1, names=[LEGS])
        messages = " ".join(i["message"] for i in _tile(uid)["entries"])
        assert "grosse séance" not in messages

    def test_the_tile_adds_no_second_data_entry_cta(self, client):
        """Le widget « État du jour · à remplir » porte déjà ce CTA.

        Le dupliquer créerait la double hiérarchie d'action que la mission
        interdit — donc l'invite de saisie de l'explainer n'est pas reprise.
        """
        from app.services.recovery_explainer import DATA_PROMPT_MESSAGE

        assert DATA_PROMPT_MESSAGE not in _page(client)


# ─────────────────── 8. cardio ───────────────────


class TestCardioOnHome:
    def test_cardio_is_worded_as_exposure(self, client):
        uid = get_test_user_id()
        from app.database import SessionLocal

        with SessionLocal() as db:
            _add_session(db, uid, days_ago=1, names=[LEGS],
                         cardio=CARDIO_VELO)
        kinds = [i["kind"] for i in _tile(uid)["entries"]]
        assert "cardio" in kinds

    def test_cardio_context_is_framed_as_exposure(self, client):
        """Formulation prudente imposée : exposition, jamais fatigue mesurée."""
        uid = get_test_user_id()
        from app.database import SessionLocal

        with SessionLocal() as db:
            _add_session(db, uid, days_ago=1, names=[LEGS],
                         cardio=CARDIO_VELO)
        cardio = [i for i in _tile(uid)["entries"] if i["kind"] == "cardio"]
        assert "exposition" in cardio[0]["message"]

    def test_bpm_never_reaches_the_tile(self, client):
        uid = get_test_user_id()
        from app.database import SessionLocal

        with SessionLocal() as db:
            _add_session(db, uid, days_ago=1, names=[LEGS],
                         cardio=CARDIO_VELO)
        messages = " ".join(i["message"] for i in _tile(uid)["entries"])
        assert "130" not in messages

    def test_calories_never_reach_the_tile(self, client):
        uid = get_test_user_id()
        from app.database import SessionLocal

        with SessionLocal() as db:
            _add_session(db, uid, days_ago=1, names=[LEGS],
                         cardio=CARDIO_VELO)
        messages = " ".join(i["message"] for i in _tile(uid)["entries"])
        assert "300" not in messages

    def test_cardio_is_never_a_recovery_penalty_claim(self, client):
        uid = get_test_user_id()
        from app.database import SessionLocal

        with SessionLocal() as db:
            _add_session(db, uid, days_ago=1, names=[LEGS],
                         cardio=CARDIO_VELO)
        messages = " ".join(i["message"] for i in _tile(uid)["entries"])
        assert "réduit" not in messages


# ───── contexte sans estimation : le cas découvert en écrivant les tests ─────


class TestContextWithoutEstimate:
    """Séance à la fois musculation ET cardio → zone dégradée en `NONE`.

    La tranche 4 dégrade la confiance d'une zone dès qu'une exposition cardio
    l'accompagne, donc une telle séance ne produit **aucune** estimation. Le
    contexte cardio, lui, reste un fait enregistré : le taire au prétexte que
    l'estimation manque perdrait une information honnête.
    """

    @staticmethod
    def _mixed(uid):
        from app.database import SessionLocal

        with SessionLocal() as db:
            _add_session(db, uid, days_ago=1, names=[LEGS],
                         cardio=CARDIO_VELO)

    def test_no_zone_estimate_survives(self, client):
        uid = get_test_user_id()
        self._mixed(uid)
        estimates = [e for e in _tile(uid)["entries"] if e["is_estimate"]]
        assert estimates == []

    def test_the_tile_is_marked_insufficient(self, client):
        uid = get_test_user_id()
        self._mixed(uid)
        assert _tile(uid)["insufficient"] is True

    def test_the_data_state_message_is_present(self, client):
        from app.services.recovery_explainer import GLOBAL_INSUFFICIENT_MESSAGE

        uid = get_test_user_id()
        self._mixed(uid)
        assert _tile(uid)["message"] == GLOBAL_INSUFFICIENT_MESSAGE

    def test_the_cardio_context_is_still_shown(self, client):
        uid = get_test_user_id()
        self._mixed(uid)
        kinds = [e["kind"] for e in _tile(uid)["entries"]]
        assert "cardio" in kinds

    def test_no_recovery_claim_accompanies_it(self, client):
        uid = get_test_user_id()
        self._mixed(uid)
        messages = " ".join(e["message"] for e in _tile(uid)["entries"])
        assert "disponible" not in messages

    def test_still_only_one_data_state_message_on_the_page(self, client):
        from app.services.recovery_explainer import GLOBAL_INSUFFICIENT_MESSAGE

        uid = get_test_user_id()
        self._mixed(uid)
        assert _page(client).count(GLOBAL_INSUFFICIENT_MESSAGE) == 1


# ─────────────────── 9. parité de recommandation ───────────────────


class TestRecommendationParity:
    def test_the_recommendation_is_identical_with_and_without_the_tile(
        self, client, monkeypatch
    ):
        """La preuve centrale : brancher P0.4 ne déplace aucune décision.

        La tuile est neutralisée par une panne injectée, ce qui reproduit
        exactement l'état « avant branchement » : `build_home_payload` calcule
        alors `today` sans qu'aucun signal P0.4 n'ait été construit.
        """
        from app.database import SessionLocal
        from app.models.user import User
        from app.services.home import build_home_payload

        uid = get_test_user_id()
        with SessionLocal() as db:
            _add_readiness(db, uid, days_ago=0, value=1)
            _add_session(db, uid, days_ago=2, names=[LEGS, CHEST],
                         global_state="bad", concentration="low")

        with SessionLocal() as db:
            user = db.get(User, uid)
            after = build_home_payload(db, user, now=NOW)

        _break_the_tile(monkeypatch)
        with SessionLocal() as db:
            user = db.get(User, uid)
            before = build_home_payload(db, user, now=NOW)

        assert after["today"] == before["today"]

    def test_the_weekly_signal_is_unchanged_too(self, client, monkeypatch):
        from app.database import SessionLocal
        from app.models.user import User
        from app.services.home import build_home_payload

        uid = get_test_user_id()
        with SessionLocal() as db:
            _add_session(db, uid, days_ago=2, names=[LEGS])

        with SessionLocal() as db:
            after = build_home_payload(db, db.get(User, uid), now=NOW)

        _break_the_tile(monkeypatch)
        with SessionLocal() as db:
            before = build_home_payload(db, db.get(User, uid), now=NOW)

        assert after["week"] == before["week"]

    def test_the_recommendation_engine_does_not_read_the_consumer(self, client):
        from app.services import recommendation

        source = inspect.getsource(recommendation)
        assert "home_training_state" not in source

    def test_the_recommendation_engine_does_not_read_the_explainer(self, client):
        from app.services import recommendation

        source = inspect.getsource(recommendation)
        assert "recovery_explainer" not in source

    def test_the_consumer_never_touches_the_recommendation(self, client):
        from app.services import home_training_state

        source = inspect.getsource(home_training_state)
        assert "recommendation" not in source


# ─────────────────── 10. réutilisation de l'explainer ───────────────────


class TestExplainerReuse:
    def test_the_consumer_holds_no_recovery_copy_table(self, client):
        """Aucune phrase de récupération n'est réécrite dans le consommateur."""
        from app.services import home_training_state
        from app.services.recovery_explainer import BAND_MESSAGES

        source = inspect.getsource(home_training_state)
        for message in BAND_MESSAGES.values():
            assert message not in source

    def test_the_consumer_writes_no_confidence_label(self, client):
        from app.services import home_training_state
        from app.services.recovery_explainer import CONFIDENCE_LABELS

        source = inspect.getsource(home_training_state)
        for label in CONFIDENCE_LABELS.values():
            assert label not in source

    def test_the_consumer_parses_no_basis(self, client):
        from app.services import home_training_state

        source = inspect.getsource(home_training_state)
        assert ".basis" not in source

    def test_the_consumer_recomputes_no_recovery(self, client):
        from app.services import home_training_state

        source = inspect.getsource(home_training_state)
        assert "build_zone_recovery" not in source

    def test_the_consumer_invents_no_readiness_score(self, client):
        """Aucun appel au producteur hérité : la tuile n'a pas de score à elle.

        Le mot « behavioral » apparaît dans la docstring du module, qui explique
        justement pourquoi le KPI hérité reste distinct — c'est l'**appel** qui
        est interdit, pas la mention.
        """
        from app.services import home_training_state

        source = inspect.getsource(home_training_state)
        assert "compute_behavioral_state" not in source

    def test_the_template_hardcodes_no_recovery_sentence(self, client):
        from app.services.recovery_explainer import BAND_MESSAGES

        markup = _markup()
        for message in BAND_MESSAGES.values():
            assert message not in markup


# ─────────────────── 11. requêtes ───────────────────


class TestQueryDiscipline:
    def test_one_training_state_build_per_home_request(self, client, monkeypatch):
        from app.services import home_training_state

        calls: list[int] = []
        original = home_training_state.build_training_state

        def spy(db, user_id, **kwargs):
            calls.append(user_id)
            return original(db, user_id, **kwargs)

        monkeypatch.setattr(home_training_state, "build_training_state", spy)
        client.get(HOME_URL)
        assert len(calls) == 1

    def test_repeated_occurrences_do_not_multiply_queries(self, client):
        """Aucun N+1 : à noms distincts constants, le volume ne coûte rien.

        C'est la propriété que `Sb_TRAINING_STATE_AGGREGATOR_01` garantit —
        mémoïsation **par nom distinct**, par invocation. Le nombre de zones
        n'entre pas dans le coût : les onze sont toujours produites, y compris
        pour un compte vide.

        Le test ne compare **pas** un jeu de noms distincts à un autre : des
        noms nouveaux exigent légitimement de nouvelles résolutions, et
        l'exiger constant reviendrait à interdire la résolution elle-même.
        """
        from app.database import SessionLocal

        uid = get_test_user_id()
        names = [CHEST, LEGS, CANONICAL]
        with SessionLocal() as db:
            _add_session(db, uid, days_ago=1, names=names)
        small = _count_queries(lambda: _tile(uid))

        with SessionLocal() as db:
            for day in range(2, 8):
                _add_session(db, uid, days_ago=day, names=names)
        big = _count_queries(lambda: _tile(uid))
        assert len(big) == len(small)

    def test_the_zone_count_does_not_drive_the_query_count(self, client):
        """Un compte vide produit onze zones — et ne coûte pas onze requêtes."""
        from app.database import SessionLocal

        uid = get_test_user_id()
        empty = _count_queries(lambda: _tile(uid))
        with SessionLocal() as db:
            _add_session(db, uid, days_ago=1, names=[CHEST, LEGS, CANONICAL])
        loaded = _count_queries(lambda: _tile(uid))
        assert len(loaded) - len(empty) <= 4

    def test_the_tile_issues_no_write(self, client):
        from app.database import SessionLocal

        uid = get_test_user_id()
        with SessionLocal() as db:
            _add_session(db, uid, days_ago=1, names=[LEGS])
        statements = _count_queries(lambda: _tile(uid))
        writes = [
            s for s in statements
            if s.strip().split()[0].upper() in {"INSERT", "UPDATE", "DELETE"}
        ]
        assert writes == []

    def test_the_tile_query_cost_is_bounded(self, client):
        """Garde de régression sur le coût : la Home est une route chaude."""
        from app.database import SessionLocal

        uid = get_test_user_id()
        with SessionLocal() as db:
            _add_session(db, uid, days_ago=1, names=[LEGS])
        assert len(_count_queries(lambda: _tile(uid))) <= 20


# ─────────────────── 12. confinement de panne ───────────────────


class TestFailureContainment:
    def test_home_survives_a_failing_tile(self, client, monkeypatch):
        _break_the_tile(monkeypatch)
        assert client.get(HOME_URL).status_code == 200

    def test_the_recommendation_survives_a_failing_tile(self, client, monkeypatch):
        from app.database import SessionLocal
        from app.models.user import User
        from app.services.home import build_home_payload

        _break_the_tile(monkeypatch)
        with SessionLocal() as db:
            payload = build_home_payload(db, db.get(User, get_test_user_id()))
        assert payload["today"].get("available") is not False

    def test_the_failing_tile_is_marked_unavailable(self, client, monkeypatch):
        from app.database import SessionLocal
        from app.models.user import User
        from app.services.home import build_home_payload

        _break_the_tile(monkeypatch)
        with SessionLocal() as db:
            payload = build_home_payload(db, db.get(User, get_test_user_id()))
        assert payload["training_state"]["available"] is False

    def test_a_failure_never_becomes_a_favourable_state(self, client, monkeypatch):
        """Une panne ne doit jamais se lire « récupéré » ni « disponible »."""
        from app.database import SessionLocal
        from app.models.user import User
        from app.services.home import build_home_payload

        _break_the_tile(monkeypatch)
        with SessionLocal() as db:
            payload = build_home_payload(db, db.get(User, get_test_user_id()))
        assert "entries" not in payload["training_state"]

    def test_a_failure_renders_no_tile_at_all(self, client, monkeypatch):
        _break_the_tile(monkeypatch)
        assert TILE_LABEL not in _page(client)

    def test_the_error_type_is_recorded(self, client, monkeypatch):
        from app.database import SessionLocal
        from app.models.user import User
        from app.services.home import build_home_payload

        _break_the_tile(monkeypatch)
        with SessionLocal() as db:
            payload = build_home_payload(db, db.get(User, get_test_user_id()))
        assert payload["training_state"]["error_type"] == "RuntimeError"


# ─────────────────── 13. garde-fou de formulation ───────────────────


class TestRenderedWordingGuardOnHome:
    def test_the_tile_output_passes_the_canonical_guard(self, client):
        """Le garde-fou de P0.4 appliqué aux chaînes réellement mises en Home."""
        from app.database import SessionLocal
        from app.services.recovery_explainer import wording_violations

        uid = get_test_user_id()
        with SessionLocal() as db:
            _add_readiness(db, uid, days_ago=0, value=2)
            _add_session(db, uid, days_ago=1, names=[LEGS],
                         cardio=CARDIO_VELO)
        tile = _tile(uid)
        strings: list[str] = []
        for item in tile["entries"]:
            strings.append(item["message"])
            strings.extend(item["reasons"])
            if item["confidence_label"]:
                strings.append(item["confidence_label"])
        assert wording_violations(tuple(strings)) == ()

    def test_the_insufficient_message_passes_the_guard(self, client):
        from app.services.recovery_explainer import wording_violations

        message = _tile(get_test_user_id())["message"]
        assert wording_violations((message,)) == ()

    def test_the_tile_framing_copy_passes_the_guard(self, client):
        from app.services.home_training_state import (
            HOME_TILE_CAPTION,
            HOME_TILE_LABEL,
        )
        from app.services.recovery_explainer import wording_violations

        assert wording_violations((HOME_TILE_LABEL, HOME_TILE_CAPTION)) == ()


# ─────────────────── 14. nommage, a11y, mobile ───────────────────


class TestNamingAndAccessibility:
    def test_the_tile_does_not_reuse_the_legacy_widget_label(self, client):
        from app.services.home_training_state import HOME_TILE_LABEL

        assert HOME_TILE_LABEL != LEGACY_WIDGET_LABEL

    def test_the_tile_does_not_reuse_the_legacy_kpi_label(self, client):
        """Le KPI hérité s'appelle « disponibilité » — pas de troisième homonyme."""
        from app.services.home_training_state import HOME_TILE_LABEL

        assert "disponibilité" not in HOME_TILE_LABEL.lower()

    def test_the_legacy_widget_still_exists(self, client):
        """Additif d'abord : la tranche ne retire pas la surface héritée."""
        assert LEGACY_WIDGET_LABEL in _page(client)

    def test_the_legacy_kpi_still_exists(self, client):
        assert "disponibilité" in _page(client)

    def test_the_tile_declares_its_provenance(self, client):
        """Ce qui distingue les deux surfaces à la lecture, pas seulement au nom."""
        from app.database import SessionLocal
        from app.services.home_training_state import HOME_TILE_CAPTION

        uid = get_test_user_id()
        with SessionLocal() as db:
            _add_session(db, uid, days_ago=1, names=[LEGS])
        assert HOME_TILE_CAPTION in _page(client)

    def test_the_tile_uses_a_semantic_heading(self, client):
        uid = get_test_user_id()
        from app.database import SessionLocal

        with SessionLocal() as db:
            _add_session(db, uid, days_ago=1, names=[LEGS])
        text = _page(client)
        heading = text.split(TILE_LABEL, 1)[0][-260:]
        assert "<h2" in heading

    def test_confidence_is_not_conveyed_by_colour_alone(self, client):
        uid = get_test_user_id()
        from app.database import SessionLocal

        with SessionLocal() as db:
            _add_session(db, uid, days_ago=1, names=[LEGS])
        labels = [
            i["confidence_label"] for i in _tile(uid)["entries"] if i["is_estimate"]
        ]
        assert all(label for label in labels)

    def test_the_tile_adds_no_horizontal_overflow(self, client):
        markup = _markup()
        block = markup.split("Sb_RECOVERY_HOME_CONSUMER_01", 1)[-1]
        assert "white-space:nowrap" not in block

    def test_the_tile_adds_no_nested_grid(self, client):
        markup = _markup()
        block = markup.split("Sb_RECOVERY_HOME_CONSUMER_01", 1)[-1]
        assert "display:grid" not in block

    def test_the_tile_adds_no_competing_button(self, client):
        markup = _markup()
        block = markup.split("Sb_RECOVERY_HOME_CONSUMER_01", 1)[-1]
        block = block.split("This week", 1)[0]
        assert "btn--primary" not in block


# ─────────────────── frontière : pas de scope creep briefing ───────────────────


class TestBriefingUntouched:
    def test_the_consumer_does_not_import_the_briefing(self, client):
        from app.services import home_training_state

        source = inspect.getsource(home_training_state)
        assert "briefing" not in source

    def test_body_intelligence_is_not_activated(self, client):
        from app.services import home_training_state

        source = inspect.getsource(home_training_state)
        assert "body_intelligence" not in source
