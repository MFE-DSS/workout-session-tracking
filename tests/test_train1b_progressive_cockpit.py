"""`TRAIN1-B` — instrument PROGRESSIF (A10).

CE QUE CES GARDES PROTÈGENT
----------------------------
Deux contrats opérateur, l'un et l'autre facilement trahis par une
« amélioration » de bonne foi.

**1. Identité analytique = celle d'`A1`, pas `(gabarit, code)`.**
Mesuré sur le catalogue canonique : **106 identités héritées pour 68 exercices
réels**, et `Leg extensions assises` vit dans **4 gabarits sous 3 codes
différents** (`E3`, `E4`, `E5`). Un même mouvement avait donc jusqu'à quatre
historiques séparés. Le gabarit devient une **provenance**.
Aucun rapprochement approximatif : un nom non résolu reste **explicitement**
hors comparaison.

**2. Le cardio n'entre pas dans une identité d'exercice.**
Ses données vivent sur `WorkoutSession` : ni série, ni charge, ni répétition.
Fait primaire = la durée ; contexte = le bpm ; comparaison **à machine
identique uniquement** ; les calories machine ne sont **jamais** une métrique
de progression ; une comparaison chronologique n'implique **aucune**
amélioration.

LE DÉFAUT QUE CETTE TRANCHE A FAILLI INTRODUIRE
------------------------------------------------
Vu au rendu, pas déduit : « Activité récente par exercice » listait les mêmes
faits sur l'identité **héritée**, et y affichait « Chest Press machine »
**deux fois**, une par gabarit. Livrer les deux blocs aurait ajouté une
duplication à l'écran même que `TRAIN1-A` venait d'écrémer.
"""
from __future__ import annotations

import ast
import pathlib
import re
from datetime import UTC, datetime, timedelta

from app.services.cardio_lane import build_cardio_facts
from app.services.progression_facts import (
    ExerciseProgression,
    Performance,
    ProgressionFacts,
    build_progression_facts,
)
from app.services.progression_view import (
    build_cardio_view,
    build_progression_rows,
    build_progression_view,
    format_delta_parts,
    format_performance,
)

ROOT = pathlib.Path(__file__).resolve().parent.parent
PARTIAL = ROOT / "app/templates/_partials/progression.html"
PROGRESS = ROOT / "app/templates/progress.html"
VIEW = ROOT / "app/services/progression_view.py"


def _uncommented(src: str) -> str:
    """Sans les commentaires Jinja — le gabarit EXPLIQUE ce qu'il refuse de
    rendre, donc il cite « progressent » et « Activité récente » dans sa propre
    justification. Une garde qui lit la prose rougirait sur l'explication du
    choix ; le motif s'est présenté **huit fois** dans ce dépôt."""
    return re.sub(r"\{#.*?#\}", " ", src, flags=re.S)


def _perf(w, r, *, sid=1, tpl="Push A", days=0):
    return Performance(
        session_id=sid, at=datetime.now(UTC) - timedelta(days=days),
        weight=w, reps=r, score=None, template=tpl,
    )


def _prog(slug="x", name="X", perfs=()):
    from app.services.progression_facts import _attach_delta

    p = ExerciseProgression(slug=slug, name=name, occurrences=list(perfs))
    _attach_delta(p)
    return p


def _seed(db, uid, *, days, tpl_name, name, weight, reps, code="E1"):
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    s = WorkoutSession(
        user_id=uid, template_slug_snapshot=tpl_name.lower().replace(" ", "-"),
        template_name_snapshot=tpl_name,
        started_at=datetime.now(UTC) - timedelta(days=days),
        status="completed", excluded_from_stats=False,
    )
    db.add(s)
    db.flush()
    se = SessionExercise(
        session_id=s.id, position=0, exercise_code_snapshot=code,
        exercise_name_snapshot=name,
    )
    db.add(se)
    db.flush()
    if weight is not None or reps is not None:
        db.add(SetLog(session_exercise_id=se.id, set_index=1, kind="work",
                      weight_kg=weight, reps=reps, completed=True))
    db.commit()
    return s


# ───────────── aucun score, aucun seuil ─────────────

def test_the_surface_never_states_a_progress_verdict():
    """« 2 progressent · 1 stable » exigerait un seuil qui n'existe nulle
    part. Le gabarit ne peut pas le rendre parce qu'il ne le reçoit pas."""
    src = _uncommented(PARTIAL.read_text(encoding="utf-8"))
    for verdict in ("progressent", "stable", "amélior", "régress", "record"):
        assert verdict not in src.lower(), verdict


def test_no_aggregate_count_of_progressing_exercises():
    view = build_progression_view(ProgressionFacts(exercises=[
        _prog(perfs=[_perf(72.5, 10), _perf(70.0, 10)]),
    ]))
    assert "progressing" not in view
    assert "score" not in view


def test_the_score_trend_is_deliberately_dropped():
    """`Delta.score_trend` vaut `up`/`down` — le seul champ de la primitive qui
    porte un jugement. Le laisser passer réintroduirait l'appréciation que le
    contrat exclut."""
    p = _prog(perfs=[
        Performance(1, datetime.now(UTC), 70.0, 10, 90, "A"),
        Performance(2, datetime.now(UTC), 70.0, 10, 40, "A"),
    ])
    assert p.delta.score_trend == "up"
    assert all("up" not in part for part in format_delta_parts(p))


def test_a_falling_load_is_rendered_without_judgement():
    p = _prog(perfs=[_perf(55.0, 12), _perf(60.0, 10)])
    parts = format_delta_parts(p)
    assert parts == ["−5 kg", "+2 reps"]


def test_an_unchanged_value_names_its_unit():
    """`+2,5 kg =` ne disait pas ce qui était égal. Vu au rendu."""
    p = _prog(perfs=[_perf(72.5, 10), _perf(70.0, 10)])
    assert format_delta_parts(p) == ["+2,5 kg", "= reps"]


def test_a_single_rep_is_singular():
    p = _prog(perfs=[_perf(70.0, 11), _perf(70.0, 10)])
    assert "+1 rep" in format_delta_parts(p)


# ───────────── on n'invente pas la moitié manquante ─────────────

def test_a_set_without_weight_shows_a_dash_not_a_guess():
    assert format_performance(None, 10) == "— × 10"


def test_a_set_with_nothing_shows_nothing():
    assert format_performance(None, None) == "—"


def test_no_comparison_without_two_measured_occurrences():
    assert _prog(perfs=[_perf(70.0, 10)]).comparable is False
    assert _prog(perfs=[_perf(70.0, 10), _perf(None, None)]).comparable is False


def test_a_gap_is_not_skipped_to_find_a_comparable_older_one():
    """« la dernière fois » veut dire la dernière fois. Une séance faite sans
    rien noter est une information, pas un trou à combler."""
    p = _prog(perfs=[_perf(75.0, 10), _perf(None, None), _perf(70.0, 10)])
    assert p.comparable is False


# ───────────── l'identité franchit le gabarit ─────────────

def test_the_same_exercise_in_two_templates_is_one_identity(client):
    """LE CAS QUE `A1` DÉBLOQUE. Sous `(gabarit, code)` ces deux occurrences
    étaient deux exercices distincts et ne se comparaient jamais."""
    from app.database import SessionLocal
    from app.services.seed import seed_reference_split
    from app.services.seed_exercise_identity import seed_exercise_identity

    with SessionLocal() as db:
        seed_reference_split(db)
        seed_exercise_identity(db)
        db.commit()
        _seed(db, 1, days=9, tpl_name="Push A", name="Chest Press machine",
              weight=70.0, reps=10, code="E1")
        _seed(db, 1, days=2, tpl_name="Push B", name="Chest Press machine",
              weight=72.5, reps=10, code="E2")
        facts = build_progression_facts(db, 1)

    assert len(facts.exercises) == 1
    prog = facts.exercises[0]
    assert prog.comparable is True
    assert len(prog.templates) == 2


def test_the_template_is_provenance_counted_not_named(client):
    """Vu au rendu : deux noms de programme complets débordaient sur deux
    lignes à 390 px et prenaient plus de place que le fait qu'ils annotent."""
    rows = build_progression_rows(ProgressionFacts(exercises=[
        _prog(perfs=[_perf(72.5, 10, tpl="Push B"), _perf(70.0, 10, tpl="Push A")]),
    ]))
    assert rows[0]["provenance"] == "2 programmes"
    assert "Push A" not in rows[0]["provenance"]


def test_a_single_template_carries_no_provenance_noise():
    rows = build_progression_rows(ProgressionFacts(exercises=[
        _prog(perfs=[_perf(72.5, 10, tpl="Push A"), _perf(70.0, 10, tpl="Push A")]),
    ]))
    assert rows[0]["provenance"] is None


def test_the_drill_down_targets_the_stable_identity():
    """Décision opérateur : converger le drill-down sur l'identité stable."""
    rows = build_progression_rows(ProgressionFacts(exercises=[
        _prog(slug="chest-press-machine",
              perfs=[_perf(72.5, 10), _perf(70.0, 10)]),
    ]))
    assert rows[0]["href"] == "/exercise-history/chest-press-machine"


def test_the_legacy_drill_down_route_is_preserved(client):
    """« entrées héritées conservées en compatibilité seulement » — conservées
    veut dire qu'elles répondent encore."""
    src = (ROOT / "app/routers/sessions.py").read_text(encoding="utf-8")
    assert '"/exercise-history/{template_slug}/{exercise_code}"' in src
    assert '"/exercise-history/{slug}"' in src


def test_both_drill_downs_share_one_comparison_rule():
    """Deux surfaces qui comparent des points différents se contredisent."""
    src = (ROOT / "app/services/exercise_history.py").read_text(encoding="utf-8")
    assert src.count("_attach_row_deltas(") >= 3  # def + 2 appels


# ───────────── aucun rapprochement approximatif ─────────────

def test_an_unresolvable_name_is_never_attached_to_the_closest_match(client):
    from app.database import SessionLocal
    from app.services.seed import seed_reference_split
    from app.services.seed_exercise_identity import seed_exercise_identity

    with SessionLocal() as db:
        seed_reference_split(db)
        seed_exercise_identity(db)
        db.commit()
        _seed(db, 1, days=3, tpl_name="Push A",
              name="Machine bizarre du sous-sol", weight=30.0, reps=10)
        facts = build_progression_facts(db, 1)

    assert facts.exercises == []
    assert facts.unresolved == 1
    assert facts.unresolved_names == ["Machine bizarre du sous-sol"]


def test_unresolved_occurrences_are_rendered_never_silenced():
    """Les taire ferait passer une couverture partielle pour totale — la même
    faute que l'état `PARTIAL` de l'exposition anatomique ferme."""
    view = build_progression_view(ProgressionFacts(unresolved=3))
    assert view["unresolved"] == 3
    assert "unresolved" in _uncommented(PARTIAL.read_text(encoding="utf-8"))


def test_awaiting_says_why_not_that_there_is_no_progress():
    view = build_progression_view(ProgressionFacts(exercises=[
        _prog(name="Curl", perfs=[_perf(14.0, 12)]),
    ]))
    assert view["awaiting"][0]["reason"] == "une seule séance"


# ───────────── cardio : voie séparée, contrats durs ─────────────

def _referenced_names(path: pathlib.Path) -> set[str]:
    """Les noms que le CODE manipule — docstrings et commentaires exclus.

    ⚠ La première écriture de la garde ci-dessous lisait le texte brut du
    module et rougissait sur sa propre docstring, qui EXPLIQUE que le cardio
    ne vit pas dans `SessionExercise`. C'est la huitième fois que ce dépôt
    prend une garde à lire de la prose au lieu du code.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Name):
            names.add(n.id)
        elif isinstance(n, ast.Attribute):
            names.add(n.attr)
        elif isinstance(n, ast.alias):
            names.add(n.name.split(".")[-1])
            if n.asname:
                names.add(n.asname)
    return names


def test_cardio_never_enters_the_exercise_identity():
    names = _referenced_names(ROOT / "app/services/cardio_lane.py")
    assert "SessionExercise" not in names
    assert "SetLog" not in names
    assert "resolve_exercise" not in names


def test_machine_calories_are_never_even_loaded():
    """Ne pas les avoir est plus solide qu'une note disant de ne pas s'en
    servir : on ne peut pas afficher par distraction ce qu'on n'a pas."""
    src = (ROOT / "app/services/cardio_lane.py").read_text(encoding="utf-8")
    code = "\n".join(ln for ln in src.splitlines()
                     if not ln.lstrip().startswith("#"))
    body = code.split('"""', 2)[-1]
    assert "cardio_machine_calories" not in body
    view_src = VIEW.read_text(encoding="utf-8")
    assert "calorie" not in view_src.lower()
    assert "calorie" not in _uncommented(PARTIAL.read_text(encoding="utf-8")).lower()


def test_cardio_compares_only_within_the_same_machine(client):
    from app.database import SessionLocal
    from app.models.session import WorkoutSession

    now = datetime.now(UTC)
    with SessionLocal() as db:
        for days, mins, machine in ((6, 20, "rameur"), (2, 28, "rameur"),
                                    (4, 40, "tapis")):
            db.add(WorkoutSession(
                user_id=1, template_slug_snapshot="s",
                template_name_snapshot="S",
                started_at=now - timedelta(days=days),
                status="completed", excluded_from_stats=False,
                cardio_duration_min=mins, cardio_machine_type=machine,
            ))
        db.commit()
        facts = build_cardio_facts(db, 1)

    lanes = {lane.machine: lane for lane in facts.lanes}
    assert lanes["rameur"].duration_delta == 8
    # Une seule sortie sur tapis : rien à comparer, et surtout PAS une
    # comparaison avec le rameur.
    assert lanes["tapis"].duration_delta is None


def test_a_cardio_session_without_a_machine_is_counted_not_filed(client):
    from app.database import SessionLocal
    from app.models.session import WorkoutSession

    with SessionLocal() as db:
        db.add(WorkoutSession(
            user_id=1, template_slug_snapshot="s", template_name_snapshot="S",
            started_at=datetime.now(UTC), status="completed",
            excluded_from_stats=False, cardio_duration_min=15,
        ))
        db.commit()
        facts = build_cardio_facts(db, 1)

    assert facts.lanes == []
    assert facts.untyped == 1


def test_bpm_is_context_never_compared():
    from app.services.cardio_lane import CardioBout, CardioFacts, CardioMachineLane

    now = datetime.now(UTC)
    lane = CardioMachineLane(machine="rameur", bouts=[
        CardioBout(1, now, "rameur", 30, 150),
        CardioBout(2, now, "rameur", 30, 120),
    ])
    view = build_cardio_view(CardioFacts(lanes=[lane]))
    row = view["lanes"][0]
    assert row["bpm"] == "150 bpm"
    # La durée est égale : l'écart porte sur ELLE, jamais sur le bpm.
    assert row["delta"] == "= min"


def test_no_cardio_score_and_no_cross_machine_total():
    src = _uncommented(PARTIAL.read_text(encoding="utf-8"))
    assert "score" not in src.lower()
    view_src = VIEW.read_text(encoding="utf-8")
    tree = ast.parse(view_src)
    fn = next(n for n in ast.walk(tree)
              if isinstance(n, ast.FunctionDef) and n.name == "build_cardio_view")
    assert not [n for n in ast.walk(fn) if isinstance(n, ast.BinOp)], (
        "la vue cardio calcule au lieu de projeter"
    )


# ───────────── périmètre ─────────────

def test_the_duplicated_activity_block_is_gone():
    """Vu au rendu : il affichait « Chest Press machine » deux fois, une par
    gabarit — la fragmentation que `A1` corrige, rendue comme deux exercices."""
    src = _uncommented(PROGRESS.read_text(encoding="utf-8"))
    assert "Activité récente par exercice" not in src
    assert "activity-row" not in src


def test_the_view_model_stays_free_of_database_and_clock():
    imported = {
        (n.module or "").split(".")[0]
        for n in ast.walk(ast.parse(VIEW.read_text(encoding="utf-8")))
        if isinstance(n, ast.ImportFrom)
    }
    assert "sqlalchemy" not in imported
    assert "datetime" not in imported


def test_the_decision_engines_never_import_the_progression_services():
    offenders = []
    for name in ("recommendation", "substitution", "behavioral"):
        path = ROOT / "app" / "services" / f"{name}.py"
        if not path.exists():
            continue
        src = path.read_text(encoding="utf-8")
        for mod in ("progression_facts", "progression_view", "cardio_lane"):
            if mod in src:
                offenders.append(f"{name} → {mod}")
    assert offenders == []


def test_the_identity_table_is_populated_at_startup(client):
    """LA GARDE QUI MANQUAIT, ET LE DÉFAUT QU'ELLE FERME.

    `A1` branchait le peuplement de `exercises` sur `scripts/seed_db`. Le
    démarrage de l'application ne semait que le catalogue et les règles de
    méthode. Sur tout déploiement où `seed_db` n'avait pas été rejoué, la
    table restait VIDE : `resolve_exercise` ne rendait jamais rien et
    l'instrument progressif n'affichait aucun exercice — **sans erreur, sans
    message**. Une surface qui marche sur le poste du développeur et nulle
    part ailleurs.
    """
    from sqlalchemy import func, select

    from app.database import SessionLocal
    from app.models.exercise import Exercise

    with SessionLocal() as db:
        n = db.execute(select(func.count()).select_from(Exercise)).scalar_one()
    assert n > 0, "la table d'identité est vide au démarrage"


def test_only_completed_stat_eligible_sessions_are_aggregated():
    src = (ROOT / "app/services/progression_facts.py").read_text(encoding="utf-8")
    assert 'status == "completed"' in src
    assert "excluded_from_stats.is_(False)" in src
    cardio = (ROOT / "app/services/cardio_lane.py").read_text(encoding="utf-8")
    assert 'status == "completed"' in cardio
    assert "excluded_from_stats.is_(False)" in cardio
