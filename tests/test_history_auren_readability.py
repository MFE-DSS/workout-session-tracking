"""Sx_UI_07.2 — History Surface Auren Readability.

Template-only readability pass on /history: additive lede + clearer aria-label
+ indicative note. All existing behaviour preserved — filters, session cards,
status badges, empty states, <details> management, POST actions (toggle
exclude / delete) and the delete confirm are untouched. No route/service/JS
change, no new score.
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HISTORY_TPL = ROOT / "app" / "templates" / "history.html"
PAGES_ROUTER = ROOT / "app" / "routers" / "pages.py"
SESSIONS_ROUTER = ROOT / "app" / "routers" / "sessions.py"
PROGRESS_TPL = ROOT / "app" / "templates" / "progress.html"
INDEX_TPL = ROOT / "app" / "templates" / "index.html"
# `TRAIN1-C` — `physique.html` a été supprimé avec sa surface. Ces gardes
# de confinement visent la SURFACE VOISINE : c'est Progression qui porte
# désormais l'instrument anatomique, donc c'est elle qu'il faut vérifier.
DASHBOARD_TPL = ROOT / "app" / "templates" / "dashboard.html"
BI_TPL = ROOT / "app" / "templates" / "body_intelligence.html"


def _seed_session(db, user_id, *, status="completed", excluded=False):
    from app.models.catalog import RepTarget, TemplateExercise, WorkoutTemplate
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    t = WorkoutTemplate(slug=f"hist-{user_id}", name="Hist test", kind="strength")
    db.add(t)
    db.flush()
    te = TemplateExercise(
        template_id=t.id, position=1, code="A1", name="Back squat", set_scheme="3×6-10"
    )
    db.add(te)
    db.flush()
    db.add(RepTarget(template_exercise_id=te.id, set_index=1, min_reps=6, max_reps=10))
    db.flush()
    now = datetime.now(UTC)
    s = WorkoutSession(
        user_id=user_id, template_id=t.id, template_slug_snapshot=t.slug,
        template_name_snapshot=t.name, started_at=now - timedelta(days=1),
        ended_at=now - timedelta(days=1) if status == "completed" else None,
        status=status, excluded_from_stats=excluded,
        global_state="good", concentration="high",
    )
    se = SessionExercise(
        template_exercise_id=te.id, exercise_code_snapshot="A1",
        exercise_name_snapshot="Back squat", position=1, success_score=80,
    )
    se.set_logs.append(
        SetLog(kind="work", set_index=1, weight_kg=100.0, reps=8, completed=True)
    )
    s.session_exercises.append(se)
    db.add(s)
    db.commit()


def _uid(db):
    from app.models.user import User

    return db.query(User).first().id


def _render(client, status="all"):
    r = client.get(f"/history?status={status}", follow_redirects=False)
    assert r.status_code == 200, r.text[:300]
    return r.text


# ───────── 1. /history renders title, lede, filters ─────────


def test_history_status_title_and_lede(client):
    html = _render(client)
    assert "Historique" in html
    # ⚠ `UI-CP5 §8` — LE CHAPEAU DIT MAINTENANT CE QUE LA SURFACE EST.
    # « Séances enregistrées, reprises possibles » décrivait une seconde
    # réponse à « qu'est-ce qui a changé ? ». L'historique est le DÉTAIL de
    # FLIGHT_RECORDER : il le dit, et il nomme où la réponse se lit.
    assert "détail temporel" in html.lower()
    assert "Progression" in html


def test_history_keeps_filter_bar_and_choices(client):
    html = _render(client)
    assert "filter-bar" in html
    # existing filter wording preserved (asserted by other tests too)
    assert "Tout" in html
    assert "En cours" in html
    assert "Terminées" in html


def test_history_empty_state_preserved(client):
    """No sessions → empty state + library link kept."""
    html = _render(client, status="completed")
    # completed empty state text preserved
    assert "Aucune séance terminée" in html


# ───────── 2. session cards + badges + management preserved (with data) ─────────


def test_history_session_card_link_and_badges(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        _seed_session(db, _uid(db), status="completed", excluded=False)
    html = _render(client)
    # ⚠ `UI-CP5` — LA CARTE DEVIENT UNE LIGNE. Ce que cette garde protège est
    # que la ligne entière MÈNE quelque part, pas qu'elle soit une carte : 21
    # rectangles identiques donnaient le même poids à la séance d'il y a une
    # heure et à celle d'il y a six semaines.
    assert "hroster__link" in html
    # ⚠ `UI-CP8D` — la ligne OUVRE la séance, elle ne la « sélectionne » plus.
    # `?session=N` rechargeait l'historique pour faire paraître un bloc
    # portant un SECOND lien. Ce que cette garde protège — « la ligne entière
    # mène quelque part » — est plus vrai : elle mène à la séance elle-même.
    assert "/sessions/" in html, "la ligne ne mène à aucune séance"
    assert "session=" not in html, (
        "la sélection en place est revenue : deux gestes pour ouvrir"
    )
    # status badge + exos badge present
    assert "badge" in html
    # `Sb_UI_HISTORIQUE_01` — MIGRÉE : ON MARQUE L'EXCEPTION, PAS LA NORME.
    #
    # Cette garde exigeait le chip « terminée ». Sur un HISTORIQUE, terminée est
    # la norme : le chip était présent sur dix cartes sur dix, seule chose
    # colorée de chacune, et il redisait l'onglet de filtre actif ET le mot
    # « durée » du chip voisin (une séance en cours dit « depuis »).
    #
    # Ce qu'elle protégeait vraiment — « la carte dit dans quel état est la
    # séance » — n'est pas abandonné : il est vérifié dans les DEUX sens juste
    # en dessous, ce que l'assertion d'origine ne faisait pas. Une garde qui ne
    # teste qu'une présence laisse passer un état qui ne se distingue plus.
    assert "en cours" not in html, (
        "une séance terminée est annoncée « en cours »"
    )
    assert "durée" in html, (
        "la carte ne dit plus la durée : sans elle ET sans chip, plus rien ne "
        "distingue une séance terminée d'une séance en cours"
    )


def test_an_unfinished_session_is_the_one_that_gets_marked(client):
    """Le pendant de la garde ci-dessus, et la raison pour laquelle elle tient.

    `Sb_UI_HISTORIQUE_01` retire le chip de la NORME. La distinction ne survit
    que si l'EXCEPTION, elle, reste marquée — deux fois plutôt qu'une : par le
    chip, et par « depuis » au lieu de « durée ».
    """
    from app.database import SessionLocal

    with SessionLocal() as db:
        _seed_session(db, _uid(db), status="in_progress", excluded=False)
    html = _render(client)
    assert "en cours" in html, "une séance en cours n'est plus signalée"
    assert "depuis" in html, (
        "le chip de durée dit « durée » sur une séance en cours : le mot ne "
        "distingue plus les deux états"
    )


def test_history_leads_to_management_without_carrying_it(client):
    """⚠ SCINDÉE ET RETOURNÉE PAR `UI-CP5 §10`.

    Elle exigeait les deux formulaires POST et le `confirm()` DANS
    `history.html`. Or l'instrument de lecture porte un contrat explicite —
    `ACTION : aucune. C'est une lecture.` — et il en portait QUARANTE-DEUX.

    Ce qu'elle protégeait vraiment est la CAPACITÉ, et la capacité est
    intacte : elle vit sur `SESSION_LIFECYCLE`, et l'événement inspecté y mène
    par une entrée discrète. Ce que la garde vérifie maintenant, c'est les
    deux moitiés — le chemin existe, et les contrôles ne sont plus là.
    """
    from app.database import SessionLocal

    with SessionLocal() as db:
        _seed_session(db, _uid(db), status="completed", excluded=True)
    html = _render(client)

    # Le CHEMIN existe.
    assert "/admin/sessions" in html, "plus aucun chemin vers la gestion"
    # Le badge d'exception reste — c'est une lecture, pas une commande.
    assert "exclu des KPI" in html

    # Et les CONTRÔLES ne sont plus sur l'instrument.
    assert 'method="post"' not in html.split("<main", 1)[-1].split("</main", 1)[0], (
        "un formulaire de gestion est revenu sur l'instrument de lecture"
    )
    assert "confirm(" not in html, (
        "le confirm JavaScript est revenu — il ne protégeait que les "
        "navigateurs coopératifs, et la protection est désormais serveur"
    )


def test_history_indicative_note_present_with_data(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        _seed_session(db, _uid(db))
    html = _render(client)
    assert "Lecture indicative" in html
    assert "ne comptent pas dans les KPI" in html


# ───────── 3. non-regression: routes/services/other surfaces untouched ─────────


def test_pages_router_not_modified_by_readability():
    src = PAGES_ROUTER.read_text(encoding="utf-8")
    # sentinel: the readability marker must NOT appear in the router
    assert "Séances enregistrées, reprises possibles" not in src


def test_sessions_router_not_modified_by_readability():
    src = SESSIONS_ROUTER.read_text(encoding="utf-8")
    assert "Séances enregistrées, reprises possibles" not in src


def test_other_surfaces_untouched_by_history_pass():
    for tpl in (PROGRESS_TPL, INDEX_TPL, DASHBOARD_TPL, BI_TPL):
        src = tpl.read_text(encoding="utf-8")
        assert "Séances enregistrées, reprises possibles" not in src


# ───────── 4. non-goals: no JS added, no BI/physique link, no forbidden wording ─────────


def test_no_js_added_to_history_template():
    src = HISTORY_TPL.read_text(encoding="utf-8")
    # the existing inline confirm is kept, but NO <script> / addEventListener
    assert "<script" not in src
    assert "addEventListener" not in src


def test_no_bi_or_physique_link_added_this_sprint():
    src = HISTORY_TPL.read_text(encoding="utf-8")
    assert "/body/intelligence" not in src
    assert "/physique" not in src


def test_the_reading_instrument_carries_no_command():
    """⚠ RETOURNÉE PAR `UI-CP5 §10` — et c'est l'inverse exact de l'ancienne.

    Elle exigeait `toggle_exclude`, `delete_session` et la phrase de `confirm()`
    dans ce gabarit. C'était la garde qui INTERDISAIT le plus directement de
    retirer le fardeau de commande d'un instrument dont le contrat dit
    « aucune action ».

    La capacité est vérifiée ailleurs, contre la surface qui la possède
    désormais (`tests/test_session_management.py`). Ici on garde la propriété
    qui compte pour CETTE surface : elle ne commande rien.
    """
    src = HISTORY_TPL.read_text(encoding="utf-8")
    assert "toggle_exclude" not in src
    assert "delete_session" not in src
    assert "confirm(" not in src
    assert 'method="post"' not in src


def test_no_forbidden_wording_in_history():
    src = HISTORY_TPL.read_text(encoding="utf-8").lower()
    for tok in (
        "diagnostic", "santé", "médical", "vérité corporelle",
        "score de santé", "échec", "mauvaise séance",
    ):
        assert tok not in src, f"forbidden token {tok!r} in history.html"
