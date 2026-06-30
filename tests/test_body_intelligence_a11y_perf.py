"""Sb_31.4 — Body Intelligence v2 a11y consolidation + perf SSR.

Couvre :
- A11y : h1 unique sur /body/intelligence, headings hiérarchisés sur les
  blocs, badges classification textuels, status global lisible hors
  couleur, <details> priorities accessibles, liens explicites,
  aria-label cohérent.
- Perf : N itérations de /body/intelligence et /coach-report avec seed
  léger, p95 sous budget généreux (catch egregious slowness).
- Garde-fous structurels Sx_31 : composer + inputs + coach_report
  service inchangés ; aucune migration ; aucun JS.
"""

from __future__ import annotations

import re
import statistics
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _enable_body_intelligence_v2(monkeypatch):
    """Sb_31.X — Body Intelligence v2 is now flag-gated (default OFF).
    These tests exercise the ON behavior, so enable the flag before the
    `client` fixture builds the app."""
    monkeypatch.setenv("BODY_INTELLIGENCE_ENABLED", "1")


ROOT = Path(__file__).resolve().parent.parent

# Budget perf très généreux pour absorber la variance CI (le but est
# d'attraper les régressions catastrophiques, pas de faire du
# microbenchmark fragile).
P95_BUDGET_MS_BODY_INTEL = 2500
P95_BUDGET_MS_COACH_REPORT = 3000
N_ITERATIONS = 10


# ───────── seed helper ─────────


def _seed_light(db, user_id):
    """Seed minimal : 5 sessions completed sur 30j pour activer la
    plupart des blocs sans saturer."""
    from app.models.catalog import RepTarget, TemplateExercise, WorkoutTemplate
    from app.models.session import SessionExercise, SetLog, WorkoutSession

    t = WorkoutTemplate(
        slug=f"perf-{user_id}",
        name="Perf seed",
        kind="strength",
    )
    db.add(t)
    db.flush()
    te = TemplateExercise(
        template_id=t.id,
        position=1,
        code="A1",
        name="Back squat",
        set_scheme="3×6-10",
    )
    db.add(te)
    db.flush()
    db.add(RepTarget(template_exercise_id=te.id, set_index=1, min_reps=6, max_reps=10))
    db.flush()
    now = datetime.now(UTC)
    for k in range(5):
        s = WorkoutSession(
            user_id=user_id,
            template_id=t.id,
            template_slug_snapshot=t.slug,
            template_name_snapshot=t.name,
            started_at=now - timedelta(days=k * 3 + 1),
            ended_at=now - timedelta(days=k * 3 + 1),
            status="completed",
            global_state="good",
            concentration="high",
        )
        se = SessionExercise(
            template_exercise_id=te.id,
            exercise_code_snapshot="A1",
            exercise_name_snapshot="Back squat",
            position=1,
            success_score=80,
        )
        se.set_logs.append(
            SetLog(kind="work", set_index=1, weight_kg=100.0, reps=8, completed=True)
        )
        s.session_exercises.append(se)
        db.add(s)
    db.commit()


# ───────── a11y : structure HTML ─────────


def test_body_intel_has_exactly_one_h1(client):
    body = client.get("/body/intelligence").text
    h1s = re.findall(r"<h1\b", body, re.IGNORECASE)
    assert len(h1s) == 1, f"expected exactly 1 <h1>, got {len(h1s)}"


def test_body_intel_h1_id_matches_aria_labelledby(client):
    body = client.get("/body/intelligence").text
    m = re.search(r'aria-labelledby="([^"]+)"', body)
    assert m is not None
    target = m.group(1)
    assert f'id="{target}"' in body
    # L'id doit cibler un <h1>.
    assert re.search(
        rf'<h1\b[^>]*id="{re.escape(target)}"',
        body,
    ), f"aria-labelledby target {target!r} must be on an <h1>"


def test_body_intel_blocks_use_h2(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        _seed_light(db, user.id)

    body = client.get("/body/intelligence").text
    h2_count = len(re.findall(r"<h2\b", body, re.IGNORECASE))
    assert h2_count >= 5, f"expected ≥ 5 <h2> for blocks, got {h2_count}"


def test_body_intel_blocks_carry_classification_label(client):
    """Chaque bloc visible expose un badge classification compréhensible
    hors couleur (texte explicite)."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        _seed_light(db, user.id)

    body = client.get("/body/intelligence").text
    for label in ("Mesuré", "Dérivé", "Inféré", "Hors de portée"):
        assert label in body, f"classification label {label!r} not rendered"


def test_body_intel_status_visible_hors_couleur(client):
    """Le status global doit être lisible hors couleur : data attribute
    + headline textuel + bullet annonçant les séances."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        _seed_light(db, user.id)

    body = client.get("/body/intelligence").text
    assert re.search(
        r'data-status="(ok|partial_data|insufficient_data)"', body
    )
    # Au moins un texte explicite annonçant le sens
    assert (
        "séances loggées" in body
        or "Lecture corporelle" in body
        or "Données insuffisantes" in body
    )


def test_body_intel_priorities_use_native_details(client):
    body = client.get("/body/intelligence").text
    # Pas d'erreur si pas de priorités, mais quand présentes, doivent
    # être en <details>/<summary>
    if "bi-priority__why" in body:
        assert "<details" in body
        assert "<summary" in body


def test_body_intel_links_have_explicit_text(client):
    """Aucun lien <a> avec un texte vide ou uniquement décoratif."""
    body = client.get("/body/intelligence").text
    # Trouver toutes les <a href=...>...</a> dans le bloc body-intelligence
    m = re.search(
        r'<section[^>]*class="body-intelligence[^"]*".*?</section>',
        body,
        re.DOTALL,
    )
    if m is None:
        return  # section absente (cas dégradé)
    block = m.group(0)
    for link_m in re.finditer(r"<a\b[^>]*>(.*?)</a>", block, re.DOTALL):
        text = re.sub(r"<[^>]+>", "", link_m.group(1)).strip()
        # Soit le texte est non-vide, soit le lien a un aria-label.
        if not text:
            assert "aria-label=" in link_m.group(0), (
                f"empty link without aria-label: {link_m.group(0)!r}"
            )


def test_coach_snapshot_cta_has_aria_label_or_explicit_text(client):
    body = client.get("/coach-report").text
    m = re.search(
        r'<section[^>]*coach-block--body-snapshot[^>]*>(.*?)</section>',
        body,
        re.DOTALL,
    )
    assert m is not None
    block = m.group(1)
    cta = re.search(
        r'<a\b[^>]*href="[^"]*body/intelligence[^"]*"[^>]*>(.*?)</a>',
        block,
        re.DOTALL,
    )
    assert cta is not None, "CTA vers /body/intelligence absent"
    cta_html = cta.group(0)
    # Sb_31.4 : aria-label explicite ajouté
    assert "aria-label=" in cta_html, "CTA must carry an explicit aria-label"
    # Texte visible non-vide
    visible = re.sub(r"<[^>]+>", "", cta.group(1)).strip()
    assert visible, "CTA visible text must not be empty"


def test_coach_snapshot_decorative_arrow_is_hidden(client):
    """Flèche → est décorative et doit être marquée aria-hidden."""
    body = client.get("/coach-report").text
    m = re.search(
        r'<a\b[^>]*href="[^"]*body/intelligence[^"]*"[^>]*>(.*?)</a>',
        body,
        re.DOTALL,
    )
    assert m is not None
    cta = m.group(0)
    # La flèche est dans un <span aria-hidden="true">
    assert 'aria-hidden="true"' in cta, (
        "decorative → must be wrapped in <span aria-hidden=\"true\">"
    )


# ───────── a11y : wording interdit (rappel) ─────────


def test_no_forbidden_wording_on_body_intel(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        _seed_light(db, user.id)

    body = client.get("/body/intelligence").text.lower()
    for tok in (
        "tu es gras",
        "tu es sec",
        "ton taux de gras",
        "ton physique est",
        "diagnostic",
        "problème médical",
        "tu dois absolument",
    ):
        assert tok not in body, f"forbidden wording {tok!r} on /body/intelligence"


# ───────── perf : p95 sur N itérations ─────────


def _measure_p95(client, route: str) -> float:
    """Retourne le p95 en ms sur N_ITERATIONS appels. Échoue dur si
    la route ne renvoie pas 200 sur la 1re itération (sanity)."""
    first = client.get(route)
    assert first.status_code == 200, f"{route} did not return 200"
    durations: list[float] = []
    for _ in range(N_ITERATIONS):
        start = time.perf_counter()
        r = client.get(route)
        elapsed_ms = (time.perf_counter() - start) * 1000
        assert r.status_code == 200
        durations.append(elapsed_ms)
    # statistics.quantiles avec n=20 → percentiles ; index 18 ≈ p95.
    if len(durations) < 2:
        return durations[0]
    return statistics.quantiles(durations, n=20)[18]


def test_perf_body_intelligence_route_p95(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        _seed_light(db, user.id)

    p95 = _measure_p95(client, "/body/intelligence")
    # Budget intentionnellement très large : on attrape les régressions
    # > 2.5s, pas les variations < 100ms (variance CI).
    assert p95 < P95_BUDGET_MS_BODY_INTEL, (
        f"/body/intelligence p95 = {p95:.0f}ms > {P95_BUDGET_MS_BODY_INTEL}ms budget"
    )


def test_perf_coach_report_route_p95(client):
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        _seed_light(db, user.id)

    p95 = _measure_p95(client, "/coach-report")
    assert p95 < P95_BUDGET_MS_COACH_REPORT, (
        f"/coach-report p95 = {p95:.0f}ms > {P95_BUDGET_MS_COACH_REPORT}ms budget"
    )


def test_perf_routes_stay_200_under_repeated_load(client):
    """Garde simple : 20 appels successifs ne dégradent pas le 200."""
    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.query(User).first()
        _seed_light(db, user.id)

    for _ in range(20):
        r1 = client.get("/body/intelligence")
        r2 = client.get("/coach-report")
        assert r1.status_code == 200
        assert r2.status_code == 200


# ───────── garde-fous structurels Sx_31 (rappel non-régression) ─────────


def test_composer_signature_unchanged_by_sb_31_4():
    from app.services.body_intelligence import (
        BODY_INTELLIGENCE_VERSION,
        compute_body_intelligence,
    )

    assert BODY_INTELLIGENCE_VERSION == 1
    assert callable(compute_body_intelligence)


def test_inputs_layer_signature_unchanged_by_sb_31_4():
    src = (ROOT / "app" / "services" / "body_intelligence_inputs.py").read_text()
    assert "def build_body_intelligence_input(" in src
    assert "db: Session, user: User" in src


def test_coach_report_service_still_unchanged_by_sb_31_4():
    src = (ROOT / "app" / "services" / "coach_report.py").read_text()
    assert "body_intelligence" not in src


# ───────── no migration / no JS / no JSON API ─────────


def test_no_new_js_file_by_sb_31_4():
    existing = {p.name for p in (ROOT / "app" / "static" / "js").glob("*.js")}
    assert existing <= {"preview.js", "session_focus.js"}


def test_no_new_migration_mentions_a11y_perf():
    versions = ROOT / "migrations" / "versions"
    for p in versions.glob("*.py"):
        s = p.read_text()
        for tok in ("a11y", "p95_body", "body_intelligence_perf"):
            assert tok not in s, f"unexpected migration mentioning {tok}"


@pytest.mark.parametrize(
    "route",
    ["/body/intelligence.json", "/coach-report.json"],
)
def test_no_json_api_introduced_sb_31_4(client, route):
    r = client.get(route, follow_redirects=False)
    assert r.status_code in (404, 405)
