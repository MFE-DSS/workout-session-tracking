"""`Sb_TRAIN_A_ENV_ACT_01` — l'activation sur le chemin RÉEL.

Pas de mime : on passe par `POST /sessions`, par `advice_memory.recommander`
et par la vraie base semée. Les gardes du module voisin prouvent la logique ;
celles-ci prouvent qu'elle est **branchée**.
"""
from __future__ import annotations

from datetime import UTC, datetime

from app.services.advice_memory import MEMOIRE_SERVIE, POLITIQUE_SERVIE
from tests.helpers import get_test_user_id

#: Un environnement RICHE MAIS SANS SMITH. Mesuré : il rend `push-a`
#: SERVABLE avec deux adaptations réelles —
#: `Incline Smith Press → Développé incliné haltères 30°` et
#: `Dips pectoraux → Développé couché haltères`.
#:
#: ⚠ Ma première version testait une salle maison. Mesuré : `push-a` y est
#: `UNKNOWN`, pas `SERVABLE`, donc rien ne s'y matérialise — et c'est le
#: comportement CORRECT du §1.B. La prémisse du test était fausse, pas le
#: service. Un labo non représentatif fait conclure faux.
_SANS_SMITH = [
    "adjustable_bench", "dumbbells", "barbell_and_plates", "ez_bar",
    "dual_adjustable_pulley", "cable_rope", "cable_straight_bar",
    "lat_pulldown_station", "low_row_station", "pull_up_bar", "ab_wheel",
    "butterfly_machine", "chest_press_machine", "chest_supported_row",
    "hack_squat_machine", "leg_extension", "leg_press", "lying_leg_curl",
    "pullover_machine", "rear_delt_fly_machine", "seated_calf_raise",
    "seated_leg_curl", "shoulder_press_machine", "standing_calf_raise",
]

#: Une salle maison : elle laisse le catalogue INCERTAIN, ce qui est le cas
#: du §1.B et mérite sa propre garde.
_MAISON = ["adjustable_bench", "dumbbells", "ez_bar", "ab_wheel",
           "pull_up_bar"]


def _declarer(uid, objets):
    from app.database import SessionLocal
    from app.services.training_preferences import save_available_equipment_items

    with SessionLocal() as db:
        save_available_equipment_items(db, uid, objets)


def _recommander(uid):
    from app.database import SessionLocal
    from app.services import advice_memory

    with SessionLocal() as db:
        return advice_memory.recommander(
            db, uid, datetime.now(UTC),
            politique=POLITIQUE_SERVIE, avec_memoire=MEMOIRE_SERVIE)


def _session(sid):
    from app.database import SessionLocal
    from app.models.session import WorkoutSession

    with SessionLocal() as db:
        s = db.get(WorkoutSession, sid)
        return [(se.position, se.exercise_name_snapshot, se.substituted_name)
                for se in sorted(s.session_exercises, key=lambda x: x.position)]


# ───────── G7 — l'utilisateur hérité ne voit RIEN changer ─────────


def test_a_legacy_user_gets_the_untouched_served_path(client):
    """`available_equipment_items` vaut `NULL` pour tout le parc. Mesuré :
    filtrer y retirerait 16 gabarits sur 18."""
    reco = _recommander(get_test_user_id())
    assert reco is not None
    assert reco["top"] is not None
    ctx = reco["context"]
    assert ctx["environnement_actif"] is False
    assert ctx["environnement_etat"] is None
    assert ctx["environnement_adapte"] is False


def test_a_legacy_user_fingerprint_carries_no_environment(client):
    """`G9` — sans quoi activer le module périmerait d'un coup tous les
    refus déjà enregistrés."""
    reco = _recommander(get_test_user_id())
    assert "|env:" not in reco["context"]["empreinte_contexte"]


def test_a_legacy_start_materializes_no_adaptation(client):
    r = client.post("/sessions", data={"template_slug": "push-a"},
                    follow_redirects=False)
    assert r.status_code == 303
    sid = int(r.headers["location"].rsplit("/", 1)[1])
    assert all(sub is None for _, _, sub in _session(sid))


# ───────── §1.A — un environnement déclaré filtre ─────────


def test_a_declared_environment_activates_the_gate(client):
    _declarer(get_test_user_id(), _SANS_SMITH)
    ctx = _recommander(get_test_user_id())["context"]
    assert ctx["environnement_actif"] is True
    assert ctx["environnement_identite"]


def test_a_declared_environment_makes_the_fingerprint_environmental(client):
    uid = get_test_user_id()
    avant = _recommander(uid)["context"]["empreinte_contexte"]
    _declarer(uid, _SANS_SMITH)
    apres = _recommander(uid)["context"]["empreinte_contexte"]
    assert "|env:" not in avant
    assert "|env:" in apres
    assert apres != avant


# ───────── G6 — la matérialisation précède le démarrage ─────────


def test_an_adapted_start_persists_planned_and_executed(client):
    """Le prescrit n'est jamais effacé : les deux identités coexistent."""
    _declarer(get_test_user_id(), _SANS_SMITH)
    r = client.post("/sessions", data={"template_slug": "push-a"},
                    follow_redirects=False)
    assert r.status_code == 303
    sid = int(r.headers["location"].rsplit("/", 1)[1])
    lignes = _session(sid)
    adaptes = [(p, prev, exe) for p, prev, exe in lignes if exe]
    assert adaptes, "aucune adaptation matérialisée sur un environnement pauvre"
    for _, prevu, execute in adaptes:
        assert prevu
        assert execute != prevu


def test_the_source_template_is_never_rewritten(client):
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.catalog import TemplateExercise, WorkoutTemplate

    def _noms():
        with SessionLocal() as db:
            t = db.execute(select(WorkoutTemplate).where(
                WorkoutTemplate.slug == "push-a")).scalar_one()
            return [te.name for te in db.execute(
                select(TemplateExercise).where(
                    TemplateExercise.template_id == t.id).order_by(
                        TemplateExercise.position)).scalars().all()]

    avant = _noms()
    _declarer(get_test_user_id(), _SANS_SMITH)
    client.post("/sessions", data={"template_slug": "push-a"},
                follow_redirects=False)
    assert _noms() == avant


def test_the_materialized_execution_is_stable_across_reloads(client):
    """`§2` — un rechargement relit la séance, il ne rejoue pas la
    résolution. On change même l'environnement entre les deux lectures."""
    uid = get_test_user_id()
    _declarer(uid, _SANS_SMITH)
    r = client.post("/sessions", data={"template_slug": "push-a"},
                    follow_redirects=False)
    sid = int(r.headers["location"].rsplit("/", 1)[1])
    premier = _session(sid)
    _declarer(uid, None)
    client.get(f"/sessions/{sid}")
    assert _session(sid) == premier


def test_the_user_never_enters_the_console_with_a_pending_rewrite(client):
    """La console doit déjà montrer l'exécution réelle."""
    _declarer(get_test_user_id(), _SANS_SMITH)
    r = client.post("/sessions", data={"template_slug": "push-a"},
                    follow_redirects=False)
    sid = int(r.headers["location"].rsplit("/", 1)[1])
    corps = client.get(f"/sessions/{sid}").text
    for _, prevu, execute in _session(sid):
        if execute:
            assert execute in corps, execute


# ───────── régression — la substitution manuelle survit ─────────


def test_manual_substitution_still_works_after_an_equipment_adaptation(client):
    from app.database import SessionLocal
    from app.models.session import WorkoutSession

    _declarer(get_test_user_id(), _SANS_SMITH)
    r = client.post("/sessions", data={"template_slug": "push-a"},
                    follow_redirects=False)
    sid = int(r.headers["location"].rsplit("/", 1)[1])
    with SessionLocal() as db:
        s = db.get(WorkoutSession, sid)
        se = sorted(s.session_exercises, key=lambda x: x.position)[0]
        seid, prevu = se.id, se.exercise_name_snapshot

    # La substitution manuelle passe par la route GÉNÉRIQUE de mise à jour
    # d'exercice, pas par un point dédié — vérifié dans le routeur.
    client.post(f"/sessions/{sid}/exercises/{seid}",
                data={"substituted_name": "Pompes"}, follow_redirects=False)
    lignes = {p: (prev, exe) for p, prev, exe in _session(sid)}
    assert lignes[1] == (prevu, "Pompes")


def test_an_equipment_adaptation_is_written_where_manual_substitution_writes(
    client,
):
    """Même champ, même contrat : l'historique reste interprétable sans
    savoir laquelle des deux a eu lieu."""
    from app.models.session import SessionExercise

    assert hasattr(SessionExercise, "substituted_name")
    _declarer(get_test_user_id(), _SANS_SMITH)
    r = client.post("/sessions", data={"template_slug": "push-a"},
                    follow_redirects=False)
    sid = int(r.headers["location"].rsplit("/", 1)[1])
    from app.database import SessionLocal
    from app.models.session import WorkoutSession
    from app.services.substitution import actual_exercise_name

    with SessionLocal() as db:
        s = db.get(WorkoutSession, sid)
        for se in s.session_exercises:
            attendu = se.substituted_name or se.exercise_name_snapshot
            assert actual_exercise_name(se) == attendu
