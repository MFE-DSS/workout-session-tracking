"""Sx_UI_07.1 — Progress Surface Auren Readability.

Template-only readability pass on /progress: clearer hierarchy + microcopy,
no business logic change. All existing blocks (weekly loop, KPIs, per-program,
recent activity, timelines, technical note) stay available. No new score, no
JS, no service touched.
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROGRESS_TPL = ROOT / "app" / "templates" / "progress.html"
KPIS_SVC = ROOT / "app" / "services" / "kpis.py"
TIMELINE_SVC = ROOT / "app" / "services" / "timeline.py"
WEEKLY_SVC = ROOT / "app" / "services" / "weekly_loop.py"
PAGES_ROUTER = ROOT / "app" / "routers" / "pages.py"
SESSION_TPL = ROOT / "app" / "templates" / "session_focus.html"
# `TRAIN1-C` — `physique.html` a été supprimé avec sa surface. La garde qui le
# citait vérifiait que la passe de lisibilité de Progression ne débordait pas
# sur les pages voisines ; elle porte désormais sur celles qui existent.
DASHBOARD_TPL = ROOT / "app" / "templates" / "dashboard.html"
INDEX_TPL = ROOT / "app" / "templates" / "index.html"
BI_TPL = ROOT / "app" / "templates" / "body_intelligence.html"


# ───────── seed a couple of completed sessions so /progress renders content ─────────


def _seed(db, user_id):
    from app.models.catalog import RepTarget, TemplateExercise, WorkoutTemplate
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    t = WorkoutTemplate(slug=f"prog-{user_id}", name="Prog test", kind="strength")
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
    for k in range(3):
        s = WorkoutSession(
            user_id=user_id, template_id=t.id, template_slug_snapshot=t.slug,
            template_name_snapshot=t.name, started_at=now - timedelta(days=k * 4 + 1),
            ended_at=now - timedelta(days=k * 4 + 1), status="completed",
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


def _render(client):
    r = client.get("/progress", follow_redirects=False)
    assert r.status_code == 200, r.text[:300]
    return r.text


# ───────── 1. /progress renders title, lede, and all existing blocks ─────────


def test_progress_status_title_and_lede(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        _seed(db, _uid(db))
    html = _render(client)
    assert "Progression" in html
    # ⚠ `UI-CP5` — LE CHAPEAU EST RETIRÉ, ET C'EST LE SUJET DE LA TRANCHE.
    # Il annonçait ce que la page montre — une quatrième ligne de prose entre
    # le titre et la seule chose qui RÉPOND, au prix de ~40 px de défilement
    # avant la réponse. Ce que cette garde protégeait est que la page NOMME
    # ce qu'elle est ; le titre le fait, et le périmètre vit dans la note de
    # pied et la divulgation.
    assert "Lecture indicative" in html
    assert "séances terminées" in html


def test_progress_counts_name_their_window(client):
    """⚠ REPOINTÉE PAR `UI-CP5 §7` — « Rythme récent » est RETIRÉ COMME OBJET.

    La garde épinglait `kpi-grid`, `kpi-card` et le littéral « Rythme récent ».
    Ce qu'elle protégeait vraiment — établi par `UX4_03D` /
    `OPERATOR_DECISION 3` — est que **tout compte nomme sa fenêtre** : deux
    nombres de la même entité sur deux fenêtres muettes étaient le défaut
    d'origine.

    Elle lit donc désormais la page RENDUE et exige qu'aucun compte ne flotte
    sans sa fenêtre, quel que soit le conteneur qui le porte. Le conteneur
    pouvait changer ; la règle, non.
    """
    from app.database import SessionLocal

    with SessionLocal() as db:
        _seed(db, _uid(db))
    html = _render(client)
    assert "Rythme récent" not in html, "l'objet retiré est revenu"
    assert "kpi-grid" not in html, "la grille de tuiles est revenue"
    # Les fenêtres restent nommées, partout où un compte est affirmé.
    assert "30 j" in html
    assert "14 j" in html
    assert "historique" in html
    # ⚠ CE COMMENTAIRE DISAIT LE DÉFAUT ET LE GARDAIT.
    #
    # Il lisait : « the KPI labels are preserved (kept "sessions" so the
    # existing test_kpis textual assertions stay valid — see report §limits) ».
    # Autrement dit : un ANGLICISME a survécu dans le produit PARCE QU'UN TEST
    # L'ÉPINGLAIT, et la chose a été consignée comme une limite plutôt que
    # corrigée. La coque dit « Séance », la commande dit « TERMINER LA
    # SÉANCE », et la sous-ligne de la carte voisine disait déjà « séance » :
    # deux mots pour une chose dans la même carte.
    #
    # S'y ajoutait un défaut d'accord — « 1 sessions » était à l'écran.
    #
    # Ce qui est gardé — la grille de KPI existe, nomme sa fenêtre et son
    # objet — est inchangé.
    # L'anglicisme reste interdit — sur la page entière plutôt que dans un
    # bloc qui n'existe plus. C'est plus strict, pas moins.
    #
    # ⚠ `session` apparaît légitimement dans les URL (`?session=`) et les noms
    # de classe : on interdit le MOT rendu, pas la sous-chaîne.
    import re

    visible = re.sub(r"<[^>]+>", " ", html)
    assert not re.search(r"\bsessions?\b", visible, re.I), (
        "l'anglicisme « session » est revenu dans le texte rendu"
    )


def test_progress_keeps_per_program_and_replaces_recent_activity(client):
    """`TRAIN1-B` / A10 — RÉORIENTÉ VERS LA NOUVELLE VÉRITÉ, PAS AFFAIBLI.

    Ce test assertait la présence de « Activité récente par exercice ». Ce
    bloc listait, par exercice, la dernière charge et les dernières reps —
    exactement ce que l'instrument progressif rend désormais, en le COMPARANT
    à l'occurrence précédente.

    Il était clavé sur l'identité HÉRITÉE `(gabarit, code)`. Vu au rendu :
    « Chest Press machine » y apparaissait DEUX FOIS, une par gabarit — la
    fragmentation qu'`A1` corrige, affichée comme deux exercices distincts.

    L'invariant utile n'était pas « ce bloc existe » mais **« la surface rend
    l'activité par exercice »**. C'est ce qui est asserté ici, et c'est plus
    strict : le bloc dupliqué doit être ABSENT, et son remplaçant présent.
    """
    from app.database import SessionLocal

    with SessionLocal() as db:
        _seed(db, _uid(db))
    html = _render(client)
    assert "Par programme" in html
    assert "Activité récente par exercice" not in html
    # « Back squat » n'appartient pas au catalogue : il ne se résout vers
    # aucune identité, donc il n'est PAS comparé. La section se rend quand
    # même — pour DIRE qu'une occurrence n'a pas été rattachée. La taire
    # ferait passer une couverture nulle pour une absence de pratique.
    assert "Progression par exercice" in html
    # ⚠ Fragment qui ne traverse AUCUN retour à la ligne du gabarit : la
    # première écriture cherchait « hors comparaison », coupé en deux par le
    # rendu. Un test d'affichage qui échoue sur un pli est un faux échec.
    assert "ne rattache à aucun exercice connu" in html


def test_progress_keeps_technical_note(client):
    from app.database import SessionLocal

    with SessionLocal() as db:
        _seed(db, _uid(db))
    html = _render(client)
    # note preserved, now prefixed « Lecture indicative »
    assert "Lecture indicative" in html
    assert "séances terminées uniquement" in html
    assert "warmup exclus" in html


def test_progress_timeline_titles_present_when_svg(client):
    """When timelines render, their calmer titles appear (data untouched)."""
    from app.database import SessionLocal

    with SessionLocal() as db:
        _seed(db, _uid(db))
    html = _render(client)
    # timelines are conditional (only if svg present); if present, calmer titles
    if "timeline-chart" in html:
        assert ("Qualité des séances" in html) or ("Poids corporel" in html)


# ───────── 2. non-regression: services + other surfaces untouched ─────────


def test_kpi_and_timeline_services_not_modified():
    """The readability pass must not touch the KPI / timeline / weekly services."""
    for svc in (KPIS_SVC, TIMELINE_SVC, WEEKLY_SVC):
        src = svc.read_text(encoding="utf-8")
        # sentinel: the readability marker must NOT appear in a service
        assert "Rythme récent" not in src
        assert "Lecture des séances terminées" not in src


def test_router_not_required_for_readability():
    """Option A is template-only: pages.py must not carry the readability
    microcopy (no router change needed)."""
    src = PAGES_ROUTER.read_text(encoding="utf-8")
    assert "Rythme récent" not in src
    assert "Lecture des séances terminées" not in src


def test_other_surfaces_untouched_by_progress_pass():
    for tpl in (DASHBOARD_TPL, INDEX_TPL, BI_TPL):
        src = tpl.read_text(encoding="utf-8")
        assert "Rythme récent" not in src


# ───────── 3. non-goals: no JS, no new score, no BI/physique link ─────────


def test_no_js_in_progress_template():
    src = PROGRESS_TPL.read_text(encoding="utf-8")
    assert "<script" not in src
    assert "onclick" not in src
    assert "addEventListener" not in src


def test_no_bi_or_physique_link_added_this_sprint():
    src = PROGRESS_TPL.read_text(encoding="utf-8")
    assert "/body/intelligence" not in src
    assert "/physique" not in src


def test_no_forbidden_wording_in_progress():
    src = PROGRESS_TPL.read_text(encoding="utf-8").lower()
    for tok in (
        "diagnostic", "santé", "vérité corporelle", "score de santé",
        "body fat", "morphotype", "attractivité", "médical",
    ):
        assert tok not in src, f"forbidden token {tok!r} in progress.html"
