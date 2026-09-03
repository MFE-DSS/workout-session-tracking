"""`TRAIN1-C` — CONSOLIDATION DE PROGRESSION.

CE QUE CES GARDES FERMENT
--------------------------
Le dépôt rendait **deux** produits analytiques sur les mêmes séances.
Progression parlait en faits ; Physique rendait un score sur 100, une lettre
et un radar. Cinq tranches ont retiré des scores de Progression pendant que
`/physique` en affichait un, entier, à un clic.

Les gardes ci-dessous portent sur les quatre points où cette tranche peut se
défaire en silence :

  1. LA DOCTRINE REVIENT PAR AILLEURS — le score n'est pas déplacé, il est
     retiré. Une garde vérifie qu'aucune surface de Progression ne le rend, et
     que les consommateurs restants sont ceux qui ont été RECENSÉS, pas ceux
     qui se seront ajoutés.
  2. UNE SURFACE MORTE SE REBRANCHE — `dashboard.html` et `physique` sont
     dépréciés. Un `include`, un lien de navigation ou une nouvelle route
     suffisent à les ramener.
  3. UN DÉNOMINATEUR ABSENT REDEVIENT UN TIRET — la suppression des cartes
     incalculables tient à deux `{% if %}` que n'importe quelle tranche peut
     rouvrir.
  4. LE CHEMIN PROGRESSION RECALCULE CE QU'IL NE REND PAS — il suffit de
     rebrancher `build_weekly_loop` pour que quatre phrases prescriptives
     redeviennent disponibles au gabarit.

MÉTHODE. Chaque garde de cette famille a été vérifiée en PLANTANT son défaut :
une garde qui lit sa propre prose ne garde rien, et ce dépôt en a compté douze.
"""
from __future__ import annotations

import pathlib
import re
from datetime import UTC, datetime, timedelta

from tests.helpers import get_test_user_id

ROOT = pathlib.Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "app/templates"
PROGRESS = TEMPLATES / "progress.html"
BASE = TEMPLATES / "base.html"
PAGES = ROOT / "app/routers/pages.py"

#: ⏰ ANCRAGE FLOTTANT, ET C'EST UNE CORRECTION DE DÉFAUT.
#:
#: Cette constante valait `datetime(2026, 8, 21, 12, 0)`. Les tests de service
#: reçoivent `now=NOW` et restaient donc cohérents — mais ceux qui passent par
#: la VRAIE route `/progress` n'injectent rien : la route lit l'heure réelle.
#:
#: Mesuré le 2026-09-03 : `_session(days_ago=2)` posait la donnée au 08-19, et
#: la fenêtre de `WINDOW_DAYS = 14` commençait au 08-20. **La donnée était
#: dehors, et deux tests sont devenus rouges à minuit UTC** — sans qu'aucun
#: commit n'ait touché ni le produit ni le test. La canonique est tombée
#: (run 33732658392) sur une bombe posée dix-neuf jours plus tôt.
#:
#: Un ancrage flottant garde le déterminisme DANS un run (une seule lecture de
#: l'horloge, réutilisée partout) tout en restant à distance constante de la
#: fenêtre glissante. Les tests de service continuent de recevoir `now=NOW`.
NOW = datetime.now(UTC).replace(hour=12, minute=0, second=0, microsecond=0)

PROGRESS_URL = "/progress"
KPI_VALUE = "kpi-card__value"
# `python:S1192` mord à partir de trois occurrences — y compris dans les tests,
# et c'est le trou qui a laissé passer une MAJEURE sur la PR #82.
BENCH = "Développé couché"
DEAD_DASHBOARD = "dashboard.html"
NO_PRESCRIBED = "aucune série de travail prescrite"


def _uncommented_jinja(src: str) -> str:
    return re.sub(r"\{#.*?#\}", " ", src, flags=re.S)


def _uncommented_py(src: str) -> str:
    """Retire commentaires ET docstrings — une garde satisfaite par sa propre
    explication ne garde rien. Ce dépôt écrit de longs docstrings ; sans cette
    coupe, `"build_weekly_loop" not in source` serait faux à cause du
    paragraphe qui explique précisément qu'on ne l'appelle plus."""
    body = re.sub(r'"""[\s\S]*?"""', " ", src)
    return "\n".join(line.split("#", 1)[0] for line in body.splitlines())


def _session(db, uid, *, days_ago, exercises=(), status="completed",
             excluded=False):
    from app.models.session import SessionExercise, WorkoutSession

    s = WorkoutSession(
        user_id=uid, template_slug_snapshot="push-a",
        template_name_snapshot="Push A", status=status,
        excluded_from_stats=excluded,
        started_at=NOW - timedelta(days=days_ago),
    )
    for i, (name, sets) in enumerate(exercises, start=1):
        se = SessionExercise(
            exercise_code_snapshot=f"E{i}", exercise_name_snapshot=name,
            position=i)
        for j, (kind, done) in enumerate(sets, start=1):
            se.set_logs.append(_set_log(j, kind, done))
        s.session_exercises.append(se)
    db.add(s)
    db.commit()
    return s


def _set_log(index, kind, done):
    from app.models.session import SetLog

    return SetLog(set_index=index, kind=kind, completed=done,
                  weight_kg=40.0, reps=10)


# ═════════════ 1 — CONVERGENCE PHYSIQUE ═════════════


def test_physique_redirects_to_progression(client):
    """La route survit pour les liens existants ; la surface, non."""
    r = client.get("/physique", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == PROGRESS_URL


def test_the_physique_template_no_longer_exists():
    """Un gabarit qu'aucune route ne rend, mais qui contient encore le score,
    la lettre et le radar, est une doctrine en sommeil : il suffit d'une ligne
    de route pour la réveiller. Il part, contrairement à `dashboard.html` dont
    huit fichiers de tests dépendent."""
    assert not (TEMPLATES / "physique.html").exists()


def test_the_global_scoring_doctrine_is_absent_from_progression():
    """Le score n'est pas DÉPLACÉ vers Progression — il est retiré.

    Les trois objets sont cherchés sur la page ET les partiels QU'ELLE INCLUT —
    un score réintroduit dans `_partials/progression.html` serait tout aussi
    visible. La liste est DÉRIVÉE du gabarit, pas écrite à la main : un include
    ajouté demain est couvert sans que personne y pense.

    ⚠ Elle n'est pas un glob sur `_partials/` non plus. `profile_preview.html`
    y vit et rend légitimement une lettre : c'est la carte de profil PUBLIC,
    une surface `LEGACY_SCORE_CONSUMER`, pas une surface de Progression. La
    première version de cette garde a rougi là-dessus — elle avait tort.
    """
    body = _uncommented_jinja(PROGRESS.read_text(encoding="utf-8"))
    surfaces = [PROGRESS] + [
        TEMPLATES / name
        for name in re.findall(r'include\s+"([^"]+)"', body)
    ]
    assert len(surfaces) > 1, "aucun include détecté — la garde ne couvre rien"

    forbidden = ("global_score", "global_grade", "grade-badge", "radar_svg")
    for path in surfaces:
        src = _uncommented_jinja(path.read_text(encoding="utf-8"))
        for token in forbidden:
            assert token not in src, f"{path.name} rend « {token} »"


def test_the_remaining_score_consumers_are_the_recorded_ones():
    """`LEGACY_SCORE_CONSUMER` — tolérés, pas validés.

    Le classement public et les profils publics consomment le radar ; les
    retirer sortirait du périmètre de Progression. Ils sont donc RECENSÉS. La
    garde rougit dans les deux sens : un consommateur qui s'ajoute sans être
    inscrit, et un inscrit qui disparaît sans que le registre soit mis à jour.
    """
    # `TRAIN1-E` / C4 — DEUX CONSOMMATEURS SONT SORTIS, et cette garde l'a
    # signalé d'elle-même : elle rougit dans les deux sens, y compris quand un
    # inscrit disparaît sans que le registre soit mis à jour. C'est
    # exactement ce pour quoi elle a été écrite.
    #
    #   app/routers/leaderboard.py   ← radar retiré du profil public
    #   app/services/leaderboard.py  ← mini-radar retiré du classement
    #
    # Il ne reste que deux appelants, et AUCUN n'est atteignable par un
    # utilisateur : Body Intelligence est derrière un drapeau éteint
    # (`DO_NOT_ACTIVATE_AS_STANDALONE`), le tableau de bord n'est rendu par
    # aucune route depuis Sb_27.6.
    recorded = {
        "app/routers/body_intelligence.py",
        "app/services/dashboard.py",
    }
    # Le module qui DÉFINIT la fonction n'en est pas un consommateur.
    definer = "app/services/muscle_scoring.py"
    found = set()
    for path in (ROOT / "app").rglob("*.py"):
        rel = str(path.relative_to(ROOT))
        if rel == definer:
            continue
        src = _uncommented_py(path.read_text(encoding="utf-8"))
        if "compute_physique_dashboard" in src:
            found.add(rel)
    assert found == recorded


def test_the_legacy_score_consumers_are_documented():
    """Un recensement qui ne vit que dans un test n'est pas un recensement :
    personne ne le lit avant d'ajouter un appel."""
    doc = (ROOT / "docs/LEGACY_SCORE_CONSUMERS.md").read_text(encoding="utf-8")
    assert "LEGACY_SCORE_CONSUMER" in doc
    for module in ("leaderboard", "body_intelligence", "dashboard"):
        assert module in doc


# ═════════════ 2 — NAVIGATION ═════════════


def test_physique_left_the_global_navigation():
    body = _uncommented_jinja(BASE.read_text(encoding="utf-8"))
    assert "Physique" not in body
    assert "url_for('physique')" not in body


def test_no_child_body_destination_was_created():
    """Une destination enfant se mérite par une profondeur mesurée, pas par
    l'existence historique d'une route."""
    from app.main import app

    paths = {getattr(r, "path", "") for r in app.routes}
    assert "/progress/body" not in paths


def test_the_compatibility_redirect_lands_on_a_real_surface(client):
    """Une redirection vers une route inexistante est un lien menteur avec un
    saut de plus."""
    r = client.get("/physique", follow_redirects=True)
    assert r.status_code == 200
    assert "Progression" in r.text


# ═════════════ 3 — TABLEAU DE BORD ═════════════


def test_dashboard_redirects_to_progression(client):
    r = client.get("/dashboard", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == PROGRESS_URL


def test_the_dead_dashboard_is_marked_deprecated():
    """Conservé — huit fichiers de tests en dépendent — mais jamais
    silencieusement : le gabarit dit qu'il est mort et pourquoi."""
    head = (TEMPLATES / DEAD_DASHBOARD).read_text(encoding="utf-8")[:1200]
    assert "DÉPRÉCIÉ" in head


def test_no_production_surface_renders_the_dead_dashboard():
    """La garde qui empêche un nouveau consommateur d'apparaître.

    Deux façons de le rebrancher : un gabarit qui l'inclut ou l'étend, ou une
    route qui le rend. Les deux sont fermées ici.
    """
    for path in TEMPLATES.rglob("*.html"):
        if path.name == DEAD_DASHBOARD:
            continue
        body = _uncommented_jinja(path.read_text(encoding="utf-8"))
        assert DEAD_DASHBOARD not in body, f"{path.name} rebranche la surface"

    routers = _uncommented_py(
        "\n".join(p.read_text(encoding="utf-8")
                  for p in (ROOT / "app/routers").rglob("*.py")))
    assert DEAD_DASHBOARD not in routers


def test_no_navigation_link_points_at_the_dead_dashboard():
    body = _uncommented_jinja(BASE.read_text(encoding="utf-8"))
    assert "url_for('dashboard')" not in body


# ═════════════ 4 — ÉTATS VIDES ═════════════


def test_par_programme_does_not_instantiate_an_empty_card(client):
    """Sans séance terminée, le module ne rend pas une carte pleine pour
    annoncer qu'il n'a rien à dire — il ne se rend pas.

    L'absence est déjà à l'écran deux fois (« Aucune séance · 14 j » et
    « Aucune séance terminée · 30 j ») : `template_kpis` vide ⟺ aucune séance
    terminée non exclue, jamais.
    """
    r = client.get(PROGRESS_URL)
    assert "Par programme" not in r.text
    assert "Aucune session terminée pour l'instant" not in r.text


def test_the_empty_progression_carries_no_motivation_and_no_duplicate_cta(
        client):
    """Ni encouragement générique, ni second appel à démarrer une séance :
    l'Accueil porte déjà celui-là."""
    r = client.get(PROGRESS_URL)
    for phrase in ("Bon départ", "Bon démarrage", "garde le rythme",
                   "Continue sur cette base", "pense à la récupération"):
        assert phrase not in r.text
    assert "Démarrer une séance" not in r.text


def test_the_footnote_only_defines_words_that_are_on_the_screen(client):
    """VU AU RENDU, PAS DÉDUIT. Sur le compte vide, la note de bas de page
    définissait « prescrits = nombre de work sets… » sous un écran où le mot
    « prescrits » n'apparaît nulle part : la carte qui l'emploie venait d'être
    supprimée faute de dénominateur.

    Une réponse sans question — la promesse sans réponse, retournée.
    """
    r = client.get(PROGRESS_URL)
    assert "prescrits" not in r.text
    assert "Lecture indicative" in r.text


def test_the_footnote_defines_prescrits_when_the_word_is_used(client):
    """Le symétrique : dès que la carte revient, sa définition revient."""
    from app.database import SessionLocal

    uid = get_test_user_id()
    with SessionLocal() as db:
        _session(db, uid, days_ago=2, exercises=[
            (BENCH, [("work", True)])])

    r = client.get(PROGRESS_URL)
    assert "prescrits =" in r.text


def test_par_programme_reappears_as_soon_as_it_has_something_to_say(client):
    """Le symétrique — masquer un module qui a du contenu serait la faute
    inverse, et une garde qui ne teste qu'un sens ne prouve rien."""
    from app.database import SessionLocal

    uid = get_test_user_id()
    with SessionLocal() as db:
        _session(db, uid, days_ago=3,
                 exercises=[(BENCH, [("work", True)])])

    r = client.get(PROGRESS_URL)
    assert "Par programme" in r.text


# ═════════════ 5 — KPI SANS DÉNOMINATEUR ═════════════


def test_absent_measures_names_each_missing_denominator():
    from app.services.kpis import GlobalKPIs, absent_measures

    empty = GlobalKPIs(
        total_sessions=1, completed_total=1, sessions_this_week=1,
        sessions_last_30=1, completed_last_30=1,
        avg_success_score_30d=None, completion_rate_30d=None,
        work_sets_done_30d=0, work_sets_total_30d=0)
    assert absent_measures(empty) == [
        NO_PRESCRIBED, "aucun exercice noté"]


def test_absent_measures_is_empty_when_both_denominators_exist():
    from app.services.kpis import GlobalKPIs, absent_measures

    full = GlobalKPIs(
        total_sessions=1, completed_total=1, sessions_this_week=1,
        sessions_last_30=1, completed_last_30=1,
        avg_success_score_30d=72.0, completion_rate_30d=0.5,
        work_sets_done_30d=6, work_sets_total_30d=12)
    assert absent_measures(full) == []


def test_a_cardio_only_account_reads_no_naked_dash(client):
    """LE CAS RÉEL. Des séances terminées, aucune série de travail prescrite,
    aucun exercice noté : la page rendait DEUX `—` de 26 px, dans des cartes de
    la même taille que les mesures réelles d'à côté.
    """
    from app.database import SessionLocal

    uid = get_test_user_id()
    with SessionLocal() as db:
        _session(db, uid, days_ago=2)
        _session(db, uid, days_ago=4)

    r = client.get(PROGRESS_URL)
    values = re.findall(rf'{KPI_VALUE}">\s*([^<]*?)\s*<', r.text)
    assert values, "aucune carte de KPI rendue — la garde ne mesure rien"
    assert "—" not in "".join(values)


def test_a_cardio_only_account_is_told_why_the_measures_are_absent(client):
    """La carte disparaît, la RAISON reste. Sans cette ligne, la page
    laisserait croire qu'elle n'a jamais eu ces mesures."""
    from app.database import SessionLocal

    uid = get_test_user_id()
    with SessionLocal() as db:
        _session(db, uid, days_ago=2)

    r = client.get(PROGRESS_URL)
    assert "Non calculable" in r.text
    assert NO_PRESCRIBED in r.text
    assert "aucun exercice noté" in r.text


def test_a_real_zero_percent_is_still_rendered(client):
    """LA GARDE CONTRE LA SUR-SUPPRESSION. 0 validé sur 2 prescrits **est** une
    mesure — 0 %, un fait. Seul le dénominateur absent fait disparaître la
    carte ; confondre les deux effacerait un résultat réel.

    ⚠ `"0%" in r.text` NE MARCHE PAS ICI, et la première version de cette garde
    le faisait. La page contient un graphique SVG dont les dégradés portent
    `offset="0%"` et `width:100%` : l'assertion passait en supprimant la carte,
    satisfaite par trois occurrences qui n'ont rien à voir. Elle lit donc la
    valeur DE LA CARTE, comme sa jumelle du tiret nu.
    """
    from app.database import SessionLocal

    uid = get_test_user_id()
    with SessionLocal() as db:
        _session(db, uid, days_ago=2, exercises=[
            (BENCH, [("work", False), ("work", False)])])

    r = client.get(PROGRESS_URL)
    values = re.findall(rf'{KPI_VALUE}">\s*([^<]*?)\s*<', r.text)
    assert "0%" in values
    assert NO_PRESCRIBED not in r.text


# ═════════════ 6 — BOUCLE HEBDOMADAIRE ═════════════


def test_the_progression_path_no_longer_calls_the_full_weekly_composer():
    """Quatre des douze clés jetées sont des PHRASES — `narrative`, `hint`,
    `volume_signal`, `data_quality_note`. Les produire pour une surface qui a
    retiré son conteneur garde vivante une voix qu'elle a congédiée : un seul
    `{{ weekly.hint }}` suffit à la faire revenir.
    """
    src = _uncommented_py(PAGES.read_text(encoding="utf-8"))
    assert "build_weekly_loop" not in src
    assert "build_progress_week" in src


def test_the_narrow_producer_returns_only_what_the_surface_reads(client):
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.weekly_loop import build_progress_week

    uid = get_test_user_id()
    with SessionLocal() as db:
        user = db.get(User, uid)
        payload = build_progress_week(db, user, now=NOW)

    assert set(payload) == {"dominant_templates", "top_anomaly"}


def test_the_reusable_weekly_services_are_not_deleted(client):
    """La décision porte sur CE QUE LE CHEMIN PROGRESSION CALCULE, pas sur
    l'existence de services réutilisables. `narrate_week` reste appelable."""
    from app.database import SessionLocal
    from app.models.user import User
    from app.services.narrative import narrate_week
    from app.services.weekly_loop import build_weekly_loop

    uid = get_test_user_id()
    with SessionLocal() as db:
        payload = build_weekly_loop(db, db.get(User, uid), now=NOW)

    assert "volume_signal" in payload
    # `narrate_week` rend un dict, pas une chaîne — vérifié, pas supposé.
    assert "phrase" in narrate_week(payload)


def test_the_progression_path_no_longer_computes_recent_exercise_activity():
    """`TRAIN1-B` a retiré « Activité récente par exercice » du gabarit et a
    laissé son producteur tourner à chaque affichage. Mon oubli."""
    src = _uncommented_py(PAGES.read_text(encoding="utf-8"))
    assert "compute_recent_exercise_activity" not in src


# ═════════════ 7 — LE FAIT ABSORBÉ ═════════════


def test_sets_per_zone_count_validated_work_sets_only(client):
    """Ni échauffement, ni série prescrite non cochée. Même définition que
    `work_sets_done_30d` — le dépôt n'a besoin que d'une notion de série
    faite."""
    from app.database import SessionLocal
    from app.services.zone_exposure import build_zone_exposure

    uid = get_test_user_id()
    with SessionLocal() as db:
        _session(db, uid, days_ago=2, exercises=[
            (BENCH, [
                ("warmup", True), ("work", True), ("work", True),
                ("work", False)])])
        exp = build_zone_exposure(db, uid, now=NOW)

    assert exp.sets["pecs"] == 2


def test_sets_per_zone_carry_no_coefficient_and_no_target(client):
    """Physique attribuait 30 % d'une série aux zones secondaires, puis
    divisait par un objectif hebdomadaire — le « % de cible » que cet
    instrument s'interdit. Ici, un entier, sur la zone primaire, rendu tel
    quel."""
    from app.database import SessionLocal
    from app.services.zone_exposure import build_zone_exposure

    uid = get_test_user_id()
    with SessionLocal() as db:
        _session(db, uid, days_ago=1, exercises=[
            (BENCH, [("work", True)] * 3)])
        exp = build_zone_exposure(db, uid, now=NOW)

    assert exp.sets["pecs"] == 3
    assert all(isinstance(n, int) for n in exp.sets.values())
    assert sum(n for z, n in exp.sets.items() if z != "pecs") == 0


def test_sets_use_the_same_window_as_the_exposure_instrument(client):
    """Deux instruments côte à côte sur des fenêtres différentes rouvriraient
    la contradiction que l'écrémage a fermée. La séance est hors des quatorze
    jours : elle ne compte ni en séances, ni en séries."""
    from app.database import SessionLocal
    from app.services.zone_exposure import WINDOW_DAYS, build_zone_exposure

    uid = get_test_user_id()
    with SessionLocal() as db:
        _session(db, uid, days_ago=WINDOW_DAYS + 3, exercises=[
            (BENCH, [("work", True)] * 5)])
        exp = build_zone_exposure(db, uid, now=NOW)

    assert exp.sets.get("pecs", 0) == 0


def test_the_inspection_level_renders_both_counts(client):
    from app.database import SessionLocal

    uid = get_test_user_id()
    with SessionLocal() as db:
        _session(db, uid, days_ago=2, exercises=[
            (BENCH, [("work", True), ("work", True)])])

    r = client.get(PROGRESS_URL)
    assert "séries" in r.text
    assert "ze-row__s" in r.text


def test_provenance_is_rendered_the_fourth_term_of_the_target(client):
    """`MUSCLE_MAPPING_TRUTH_01` comptait déjà les résolutions venues du
    référentiel et celles venues du repli — sans jamais les rendre. Un
    instrument qu'aucune surface n'expose ne mesure rien."""
    from app.database import SessionLocal

    uid = get_test_user_id()
    with SessionLocal() as db:
        _session(db, uid, days_ago=2, exercises=[
            (BENCH, [("work", True)])])

    r = client.get(PROGRESS_URL)
    assert "Attribution :" in r.text


def test_the_screen_reader_equivalent_carries_the_absorbed_fact(client):
    """La silhouette est `aria-hidden`, et elle ne peut l'être QUE parce que ce
    paragraphe porte les mêmes faits. Ajouter une colonne à l'écran sans
    l'ajouter ici rendrait le nouveau comptage visuel-seulement — et
    dés-armerait la raison pour laquelle la silhouette est masquée.
    """
    from app.database import SessionLocal
    from app.services.zone_exposure import (
        build_zone_exposure,
        build_zone_exposure_view,
    )

    uid = get_test_user_id()
    with SessionLocal() as db:
        _session(db, uid, days_ago=2, exercises=[
            (BENCH, [("work", True), ("work", True)])])
        view = build_zone_exposure_view(
            build_zone_exposure(db, uid, now=NOW))

    assert "2 séries" in view["sr"]
    # accord vu au rendu : « 1 zones touchées » s'entendait au lecteur d'écran
    assert "1 zone touchée" in view["sr"]


def test_provenance_is_silent_when_nothing_was_resolved(client):
    """« 0 attribution » ferait passer un écran vide pour une mesure."""
    from app.services.zone_exposure import (
        ZoneExposure,
        build_zone_exposure_view,
    )

    view = build_zone_exposure_view(ZoneExposure())
    assert view.get("provenance") is None
