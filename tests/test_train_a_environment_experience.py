"""`Sb_TRAIN_A_ENVIRONMENT_EXPERIENCE_01` — la frontière de démarrage.

Trois défauts vivants en canonique se ferment ici, et chacun a sa garde :

1. une **seconde** route de démarrage sans aucun préflight ;
2. `plan_pour_template` incapable d'exprimer un refus — `()` signifiait à la
   fois « rien à adapter » et « infaisable » ;
3. un `except Exception: return 0` autour d'une décision.

Les gardes portent sur le **comportement**, jamais sur une chaîne de code.
"""
from __future__ import annotations

import pytest

from app.services.environment_activation import (
    ADAPTABLE,
    INCERTAIN,
    NATIF,
    NON_APPLICABLE,
    REFUSE,
    PreparationDemarrage,
    environnement_declare,
    preparer_demarrage,
)
from tests.helpers import get_test_user_id

#: Riche mais sans Smith. Mesuré : rend `push-a` SERVABLE avec deux
#: adaptations réelles.
_SANS_SMITH = [
    "adjustable_bench", "dumbbells", "barbell_and_plates", "ez_bar",
    "dual_adjustable_pulley", "cable_rope", "cable_straight_bar",
    "lat_pulldown_station", "low_row_station", "pull_up_bar", "ab_wheel",
    "butterfly_machine", "chest_press_machine", "chest_supported_row",
    "hack_squat_machine", "leg_extension", "leg_press", "lying_leg_curl",
    "pullover_machine", "rear_delt_fly_machine", "seated_calf_raise",
    "seated_leg_curl", "shoulder_press_machine", "standing_calf_raise",
]

#: Mesuré : avec la seule roulette abdominale, ces neuf gabarits sont
#: réellement NOT_FEASIBLE — toutes leurs voies autorisées sont connues
#: incompatibles. Aucun verdict n'est fabriqué ici.
_UN_SEUL_OBJET = ["ab_wheel"]
_REFUSES = ("push-b", "pull-a", "legs-a", "legs-b", "upper-pecs-delts",
            "lower-quad-bias", "lower-posterior-bias", "liss-abs",
            "catch-up-shoulders")


def _declarer(uid, objets):
    from app.database import SessionLocal
    from app.services.training_preferences import save_available_equipment_items

    with SessionLocal() as db:
        save_available_equipment_items(db, uid, objets)


def _gabarit(slug):
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    from app.database import SessionLocal
    from app.models.catalog import TemplateExercise, WorkoutTemplate

    with SessionLocal() as db:
        return db.execute(
            select(WorkoutTemplate).where(WorkoutTemplate.slug == slug)
            .options(selectinload(WorkoutTemplate.exercises)
                     .selectinload(TemplateExercise.rep_targets))
        ).scalar_one()


def _preparer(uid, slug):
    from app.database import SessionLocal

    with SessionLocal() as db:
        return preparer_demarrage(db, uid, _gabarit(slug))


def _compter_seances():
    from sqlalchemy import func, select

    from app.database import SessionLocal
    from app.models.session import WorkoutSession

    with SessionLocal() as db:
        return db.execute(select(func.count(WorkoutSession.id))).scalar_one()


def _lignes(sid):
    from app.database import SessionLocal
    from app.models.session import WorkoutSession

    with SessionLocal() as db:
        s = db.get(WorkoutSession, sid)
        return [(se.position, se.exercise_name_snapshot, se.substituted_name)
                for se in sorted(s.session_exercises, key=lambda x: x.position)]


# ───────── le contrat typé : cinq états, aucun nombre ─────────


def test_the_five_states_are_named_strings():
    for etat in (NON_APPLICABLE, NATIF, ADAPTABLE, INCERTAIN, REFUSE):
        assert isinstance(etat, str)
        with pytest.raises(ValueError):
            float(etat)


def test_the_five_states_are_distinct():
    assert len({NON_APPLICABLE, NATIF, ADAPTABLE, INCERTAIN, REFUSE}) == 5


def test_a_refusal_is_no_longer_confused_with_nothing_to_adapt(client):
    """LE DÉFAUT 2. `plan_pour_template` rendait `()` dans les deux cas ; le
    signal de refus était jeté à la frontière que `create_session` utilise."""
    uid = get_test_user_id()
    _declarer(uid, _UN_SEUL_OBJET)
    refuse = _preparer(uid, _REFUSES[0])
    assert refuse.etat == REFUSE
    assert refuse.plan == ()

    _declarer(uid, _SANS_SMITH)
    natif = _preparer(uid, "no-equipment-full-body")
    assert natif.etat == NATIF
    assert natif.plan == ()

    # Les deux ont un plan vide, et pourtant ils ne disent pas la même chose.
    assert refuse.etat != natif.etat


# ───────── G7 — l'environnement non déclaré ne change RIEN ─────────


def test_an_undeclared_environment_is_not_applicable(client):
    p = _preparer(get_test_user_id(), "push-a")
    assert p.etat == NON_APPLICABLE
    assert p.plan == ()
    assert p.attendu == 0


def test_a_legacy_start_still_creates_a_session_untouched(client):
    avant = _compter_seances()
    r = client.post("/sessions", data={"template_slug": "push-a"},
                    follow_redirects=False)
    assert r.status_code == 303
    assert _compter_seances() == avant + 1
    sid = int(r.headers["location"].rsplit("/", 1)[1])
    assert all(sub is None for _, _, sub in _lignes(sid))


# ───────── §1 — les quatre autres états, sur le chemin réel ─────────


def test_an_adaptable_template_announces_its_expected_count(client):
    uid = get_test_user_id()
    _declarer(uid, _SANS_SMITH)
    p = _preparer(uid, "push-a")
    assert p.etat == ADAPTABLE
    assert p.attendu == len(p.plan) > 0


def test_an_uncertain_template_stays_non_blocking(client):
    """§1.B — l'incertitude n'est pas une impossibilité."""
    uid = get_test_user_id()
    _declarer(uid, ["adjustable_bench", "dumbbells"])
    p = _preparer(uid, "push-a")
    assert p.etat == INCERTAIN
    assert p.plan == ()


def test_a_proven_incompatible_template_is_refused(client):
    uid = get_test_user_id()
    _declarer(uid, _UN_SEUL_OBJET)
    assert _preparer(uid, _REFUSES[0]).etat == REFUSE


# ───────── le refus ne crée AUCUNE séance ─────────


def test_a_refused_start_creates_no_session_at_all(client):
    uid = get_test_user_id()
    _declarer(uid, _UN_SEUL_OBJET)
    avant = _compter_seances()
    r = client.post("/sessions", data={"template_slug": _REFUSES[0]},
                    follow_redirects=False)
    assert r.status_code == 303
    assert _compter_seances() == avant, "séance orpheline après un refus"


def test_a_refused_start_returns_to_the_equipment_declaration(client):
    """§6 — vers l'environnement CONCRET, jamais vers le questionnaire de
    familles : celui-ci ne répare pas le problème."""
    _declarer(get_test_user_id(), _UN_SEUL_OBJET)
    r = client.post("/sessions", data={"template_slug": _REFUSES[0]},
                    follow_redirects=False)
    destination = r.headers["location"]
    assert destination.startswith("/plan")
    assert "#equipement" in destination
    assert "#declaration" not in destination


def test_the_refusal_page_says_it_calmly(client):
    _declarer(get_test_user_id(), _UN_SEUL_OBJET)
    r = client.post("/sessions", data={"template_slug": _REFUSES[0]},
                    follow_redirects=False)
    corps = client.get(r.headers["location"].split("#")[0]).text
    assert "matériel" in corps.lower()
    for interdit in ("erreur", "impossible de t'entraîner", "blessure",
                     "danger", "échec"):
        assert interdit not in corps.lower(), interdit


# ───────── l'invariant critique : partiel = échec ─────────


def test_a_partial_materialization_commits_nothing(client, monkeypatch):
    """Si TRAIN A dit qu'une adaptation est REQUISE, en poser N−1 est un
    ÉCHEC. Committer la séance comme si l'adaptation avait réussi la
    rendrait inexécutable sans que rien ne le dise."""
    import app.routers.sessions as routeur

    uid = get_test_user_id()
    _declarer(uid, _SANS_SMITH)
    attendu = _preparer(uid, "push-a")
    assert attendu.attendu >= 2, "prémisse : il faut au moins deux adaptations"

    vrai = routeur._poser_adaptations

    def _mutile(session, plan):
        return vrai(session, plan[:-1])

    monkeypatch.setattr(routeur, "_poser_adaptations", _mutile)
    avant = _compter_seances()
    r = client.post("/sessions", data={"template_slug": "push-a"},
                    follow_redirects=False)
    assert _compter_seances() == avant, "séance committée malgré un plan partiel"
    assert r.status_code == 303


def test_a_complete_materialization_commits_every_adaptation(client):
    uid = get_test_user_id()
    _declarer(uid, _SANS_SMITH)
    attendu = _preparer(uid, "push-a")
    r = client.post("/sessions", data={"template_slug": "push-a"},
                    follow_redirects=False)
    sid = int(r.headers["location"].rsplit("/", 1)[1])
    poses = [(p, prev, exe) for p, prev, exe in _lignes(sid) if exe]
    assert len(poses) == attendu.attendu
    for _, prevu, execute in poses:
        assert execute != prevu


# ───────── le fail-open est BORNÉ ─────────


def test_reading_the_environment_to_rank_may_fail_open(client):
    """Une recommandation dégradée vaut mieux qu'un écran cassé."""
    from app.database import SessionLocal

    with SessionLocal() as db:
        assert environnement_declare(db, get_test_user_id()) is None


def test_reading_the_environment_to_decide_must_not_fail_open(monkeypatch):
    """Décider de CRÉER une séance ne tolère pas la même indulgence : une
    lecture qui échoue doit remonter, jamais se déguiser en « non déclaré »."""
    import app.services.training_preferences as prefs
    from app.database import SessionLocal

    def _casse(*a, **k):
        raise RuntimeError("base indisponible")

    monkeypatch.setattr(prefs, "get_training_preferences", _casse)
    with SessionLocal() as db:
        assert environnement_declare(db, 1) is None          # tolérant
        with pytest.raises(RuntimeError):
            environnement_declare(db, 1, strict=True)         # strict


# ───────── LE DÉFAUT 1 : la seconde route de démarrage ─────────


def test_every_session_creating_route_preflights_the_environment():
    """`POST /sessions` était câblé, `POST /programs/.../start` ne l'était
    pas. Recherché par CLASSE — tout appelant d'`instantiate_session` — et
    non par nom de route."""
    import ast
    import pathlib

    racine = pathlib.Path(__file__).resolve().parents[1] / "app"
    sans_preflight = []
    for chemin in sorted(racine.rglob("*.py")):
        arbre = ast.parse(chemin.read_text(encoding="utf-8"))
        for fn in [n for n in ast.walk(arbre)
                   if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
            appels = {
                n.func.id for n in ast.walk(fn)
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
            }
            if "instantiate_session" not in appels:
                continue
            if not appels & {"preparer_demarrage", "_demarrage_autorise"}:
                sans_preflight.append(f"{chemin.name}:{fn.name}")
    assert sans_preflight == []


def test_the_program_start_route_also_materializes(client):
    """La route programme doit adapter comme l'autre — sinon un
    propriétaire de programme démarre une séance qu'il ne peut pas faire."""
    import ast
    import pathlib

    src = (pathlib.Path(__file__).resolve().parents[1]
           / "app" / "routers" / "user_programs.py").read_text(encoding="utf-8")
    fn = next(n for n in ast.walk(ast.parse(src))
              if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
              and n.name == "user_program_start_session")
    appels = {n.func.id for n in ast.walk(fn)
              if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    assert "preparer_demarrage" in appels


# ───────── forme du résultat ─────────


def test_the_preparation_carries_its_own_expected_count():
    p = PreparationDemarrage(etat=NON_APPLICABLE)
    assert p.plan == ()
    assert p.attendu == 0
    assert p.slug is None
