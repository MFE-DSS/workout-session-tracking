"""`TRAIN1-A` — fermeture de la couche temporelle (A4 + A5 + A11).

CE QUE CES GARDES PROTÈGENT
----------------------------
Trois défauts **mesurés** sur la surface avant cette tranche, pas supposés :

1. **A11 — la cadence survivait au bloc qui devait l'absorber.**
   `UX4_03D` déclarait la cadence « absorbée par le rail » et retirait l'objet
   `cadence 7 j`. Mesuré ensuite sur un compte peuplé : `weekly_loop` rendait
   toujours « 3 séances cette semaine » et « Semaine précédente : 2 (+1) ».
   Cinq comptages de séances coexistaient sur un même écran, et douze mentions
   de fenêtre temporelle sur **cinq fenêtres différentes**.

2. **A4 — l'état vide était l'instrument avec des blancs.**
   Sans aucune séance : deux cartes `weekly_loop` dont l'une répétait la MÊME
   phrase deux fois, deux lignes de signaux, quatorze cellules identiques.

3. **A5 — le détail jour par jour n'existait pour personne.**
   Le rail est `aria-hidden` ; ses `title` ne s'annoncent pas de façon fiable.
   Ni l'œil ni le lecteur d'écran n'atteignaient la ligne.

Et un quatrième, trouvé en construisant :

4. **L'état ``none`` du rail était mort.** `DayTrace` le documente depuis le
   premier jour — « hors historique : le compte n'existait pas encore » — la
   vue-modèle sait le rendre, l'équivalent textuel a sa phrase. **Le producteur
   ne l'émettait jamais.** Un compte créé la veille rendait quatorze traces
   ``rest`` : treize affirmations « il pouvait s'entraîner, il ne l'a pas fait »
   sur des jours sans compte. Les gardes existantes éprouvaient ``none`` via
   une fabrique de test, jamais via le producteur réel.
"""
from __future__ import annotations

import pathlib
import re
from datetime import UTC, datetime, timedelta

import pytest

from app.services.progress_facts import (
    WINDOW_DAYS,
    DayTrace,
    ProgressFacts,
    build_progress_facts,
)
from app.services.progress_signals import (
    build_progress_rail,
    build_rail_days,
    build_rail_summary,
    has_any_trace,
)

ROOT = pathlib.Path(__file__).resolve().parent.parent
PROGRESS = ROOT / "app/templates/progress.html"
PAGES = ROOT / "app/routers/pages.py"


def _uncommented(src: str) -> str:
    """Sans les commentaires Jinja.

    Ce gabarit EXPLIQUE ce qu'il retire, donc il cite `weekly_loop` et
    « Séances dominantes » dans sa propre justification. Une garde qui lit la
    prose rougirait sur l'explication du choix — le motif s'est présenté
    **sept fois** dans ce dépôt.
    """
    return re.sub(r"\{#.*?#\}", " ", src, flags=re.S)


def _age_account(days: int, uid: int = 1) -> None:
    """Vieillit le compte du harnais.

    Le `conftest` crée son utilisateur à l'instant : quatorze traces « hors
    historique » y sont donc le rendu CORRECT depuis cette tranche. Pour
    éprouver un état peuplé il faut un compte de l'âge de ses séances.
    """
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        u = db.get(User, uid)
        u.created_at = datetime.now(UTC) - timedelta(days=days)
        db.commit()


def _add_session(uid: int, days_ago: int, status: str = "completed") -> None:
    from app.database import SessionLocal
    from app.models.session import WorkoutSession

    with SessionLocal() as db:
        db.add(WorkoutSession(
            user_id=uid, template_slug_snapshot="s", template_name_snapshot="S",
            started_at=datetime.now(UTC) - timedelta(days=days_ago),
            status=status, excluded_from_stats=False,
        ))
        db.commit()


def _days(*, first_known=0, done=(), active=(), sids=None):
    sids = sids or {}
    out = []
    for i in range(WINDOW_DAYS):
        if i < first_known:
            state = "none"
        elif i in done:
            state = "done"
        elif i in active:
            state = "active"
        else:
            state = "rest"
        out.append(DayTrace(
            offset=i, label=f"{i:02d}/01", state=state,
            kind="strength" if state == "done" else None,
            name="Push A" if state == "done" else None,
            session_id=sids.get(i),
        ))
    return ProgressFacts(days=tuple(out))


# ───────────── A11 — le conteneur part, ses faits uniques restent ─────────────

def test_the_weekly_loop_container_is_no_longer_included():
    assert 'include "_partials/weekly_loop.html"' not in _uncommented(
        PROGRESS.read_text(encoding="utf-8"))


def test_the_duplicated_cadence_wording_is_gone_from_the_surface():
    """« Semaine précédente : N » disait ce que le rail montre déjà."""
    src = _uncommented(PROGRESS.read_text(encoding="utf-8"))
    assert "previous_week_sessions_count" not in src
    assert "delta_sessions_count" not in src
    assert "volume_signal" not in src


def test_the_anomaly_survives_the_container():
    """§5.3 — une soustraction ne part jamais seule. L'anomalie est le fait
    UNIQUE de `weekly_loop` : aucun autre bloc ne la porte."""
    assert "top_anomaly" in _uncommented(PROGRESS.read_text(encoding="utf-8"))


def test_the_weekly_dominance_survives_inside_per_programme():
    src = _uncommented(PROGRESS.read_text(encoding="utf-8"))
    assert "tk.week_count" in src
    assert "cette sem." in src


def test_the_producers_are_not_deleted_only_the_container():
    """La décision porte sur ce que la surface rend, pas sur la capacité."""
    assert "build_weekly_loop" in PAGES.read_text(encoding="utf-8")


# ───────────── A4 — l'état vide est une ligne, pas un instrument ─────────────

def test_a_window_with_no_trace_at_all_is_not_instrumented():
    assert has_any_trace(_days()) is False


@pytest.mark.parametrize("kw", [{"done": (3,)}, {"active": (13,)}])
def test_a_single_trace_is_enough_to_instrument(kw):
    """« Aucune séance terminée » n'est pas « rien à montrer » : une séance
    ouverte est une trace."""
    assert has_any_trace(_days(**kw)) is True


def test_the_empty_state_renders_one_line_and_no_rail(client):
    html = client.get("/progress").text
    assert 'class="empty-line"' in html
    assert "Aucune séance" in html
    assert 'class="rail-l2"' not in html


def test_the_empty_state_carries_no_cta_competing_with_home(client):
    """L'Accueil porte déjà l'appel à démarrer ; `home_training_state` a
    refusé de le dupliquer. Le rouvrir ici rejouerait la duplication."""
    html = client.get("/progress").text
    line = html[html.index('class="empty-line"'):]
    line = line[:line.index("</p>")]
    for lure in ("Démarrer", "Commencer", "/launcher", "<a "):
        assert lure not in line, lure


def test_the_empty_state_shows_no_em_dash_counters(client):
    """Décision opérateur : « sans compteurs — »."""
    html = client.get("/progress").text
    assert 'class="signal__value">—' not in html


# ───────────── A5 — le rail devient inspectable, sans nouvelle route ─────────

def test_the_level_two_lists_every_day_of_the_window():
    rows = build_rail_days(_days(done=(2, 5), sids={2: 11, 5: 22}))
    assert len(rows) == WINDOW_DAYS


def test_the_level_two_reads_most_recent_first():
    """Le rail est une frise ; une liste se lit du plus pertinent au moins."""
    facts = _days()
    rows = build_rail_days(facts)
    assert rows[0]["label"] == facts.days[-1].label
    assert rows[-1]["label"] == facts.days[0].label


def test_only_a_completed_day_carries_a_link():
    rows = build_rail_days(_days(done=(2,), active=(13,), sids={2: 11}))
    linked = [r for r in rows if r["href"]]
    assert len(linked) == 1
    assert linked[0]["href"] == "/sessions/11/done"


def test_no_link_on_a_rest_day():
    """Un lien qui n'ouvre rien est une promesse."""
    rows = build_rail_days(_days())
    assert [r for r in rows if r["href"]] == []


def test_a_completed_day_without_an_id_stays_readable_but_not_openable():
    """On ne fabrique pas de cible pour rendre une ligne cliquable."""
    rows = build_rail_days(_days(done=(4,)))
    day = next(r for r in rows if r["state"] == "done")
    assert day["href"] is None
    assert day["detail"] == "Push A"


def test_the_level_two_points_at_the_existing_session_surface_not_a_new_route():
    """Décision opérateur : **pas de route jour.**"""
    rows = build_rail_days(_days(done=(1,), sids={1: 7}))
    href = next(r["href"] for r in rows if r["href"])
    assert href.startswith("/sessions/")
    src = _uncommented(PROGRESS.read_text(encoding="utf-8"))
    assert "/progress/day" not in src
    assert "/progress/jour" not in src


def test_the_rail_stays_one_object_the_summary_is_the_target():
    """Quatorze cibles de 25 px violeraient quatorze fois le standard de 44 px."""
    src = _uncommented(PROGRESS.read_text(encoding="utf-8"))
    rail = src[src.index('<div class="rail"'):src.index("</div>", src.index('<div class="rail"'))]
    assert "<a " not in rail
    assert "rail-l2__summary" in src


def test_the_disclosure_works_without_a_line_of_script():
    src = _uncommented(PROGRESS.read_text(encoding="utf-8"))
    assert "<details class=\"rail-l2\">" in src
    assert "<script" not in src


def test_the_screen_reader_is_told_the_detail_can_be_opened(client):
    _age_account(90)
    _add_session(1, 2)
    html = client.get("/progress").text
    assert "Ouvrir le détail jour par jour" in html


# ───────────── le quatrième défaut : `none` était mort ─────────────

def test_a_brand_new_account_is_not_told_it_rested_for_two_weeks(client):
    """LA GARDE QUI MANQUAIT. Le compte du harnais vient d'être créé."""
    from app.database import SessionLocal
    with SessionLocal() as db:
        facts = build_progress_facts(db, 1)
    states = {d.state for d in facts.days}
    assert "none" in states, (
        "un compte créé aujourd'hui rend quatorze jours de « repos » — "
        "treize affirmations sur des jours où il n'existait pas"
    )
    assert states != {"rest"}


def test_the_producer_can_emit_every_documented_state(client):
    """`DayTrace` en documente quatre. Trois chemins de la vue-modèle étaient
    inatteignables depuis le producteur réel."""
    from app.database import SessionLocal

    # Compte de 8 jours : la fenêtre en couvre 14, donc six jours précèdent la
    # création — c'est ce qui rend ``none`` atteignable en même temps que les
    # trois autres.
    _age_account(8)
    _add_session(1, 2)
    _add_session(1, 0, status="in_progress")
    with SessionLocal() as db:
        facts = build_progress_facts(db, 1)
    assert {d.state for d in facts.days} == {"none", "rest", "done", "active"}


def test_a_session_older_than_the_account_still_shows(client):
    """LA DONNÉE PASSE AVANT LA BORNE. Un import ou une horloge de travers ne
    doit pas effacer une séance réelle — la première version testait la borne
    en premier et les faisait disparaître."""
    from app.database import SessionLocal
    from app.models.session import WorkoutSession

    now = datetime.now(UTC)
    with SessionLocal() as db:
        db.add(WorkoutSession(
            user_id=1, template_slug_snapshot="s", template_name_snapshot="S",
            started_at=now - timedelta(days=10), status="completed",
            excluded_from_stats=False,
        ))
        db.commit()
        facts = build_progress_facts(db, 1)
    done = [d for d in facts.days if d.state == "done"]
    assert len(done) == 1


def test_the_textual_equivalent_reports_days_outside_the_history():
    """La phrase existait et n'avait jamais pu se rendre."""
    summary = build_rail_summary(_days(first_known=5))
    assert "hors historique" in summary


def test_the_out_of_history_days_read_differently_from_rest():
    rows = build_rail_days(_days(first_known=3))
    assert rows[-1]["word"] == "hors historique"
    assert rows[0]["word"] == "repos"


def test_the_rail_marks_out_of_history_with_its_own_class():
    cells = build_progress_rail(_days(first_known=3))
    assert "rail__c--void" in cells[0]["cls"]
    assert "rail__c--rest" in cells[-1]["cls"]


# ───────────── périmètre ─────────────

def test_no_new_metric_was_introduced():
    """Décision opérateur : **No new metric.** Le niveau 2 projette les mêmes
    `facts.days` ; il ne compte ni ne seuille rien."""
    src = (ROOT / "app/services/progress_signals.py").read_text(encoding="utf-8")
    import ast
    tree = ast.parse(src)
    fn = next(n for n in ast.walk(tree)
              if isinstance(n, ast.FunctionDef) and n.name == "build_rail_days")
    ops = [n for n in ast.walk(fn) if isinstance(n, ast.BinOp)]
    assert ops == [], "le niveau 2 calcule au lieu de projeter"


def test_the_view_model_stays_free_of_database_and_clock():
    import ast
    src = (ROOT / "app/services/progress_signals.py").read_text(encoding="utf-8")
    imported = {
        (n.module or "").split(".")[0]
        for n in ast.walk(ast.parse(src)) if isinstance(n, ast.ImportFrom)
    }
    assert "sqlalchemy" not in imported
    assert "datetime" not in imported
