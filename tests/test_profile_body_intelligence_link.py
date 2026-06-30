"""Sb_31.next.profile-link — Découvrabilité Body Intelligence depuis /profile.

Mini-lot UX. Le but de ces tests est strictement de vérifier qu'un
lien sobre vers /body/intelligence est présent sur /profile, sans
duplication du contenu Body Intelligence ni régression structurelle.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _enable_body_intelligence_v2(monkeypatch):
    """Sb_31.X — Body Intelligence v2 is now flag-gated (default OFF).
    These tests exercise the ON behavior, so enable the flag before the
    `client` fixture builds the app."""
    monkeypatch.setenv("BODY_INTELLIGENCE_ENABLED", "1")


ROOT = Path(__file__).resolve().parent.parent
PROFILE_TEMPLATE = ROOT / "app" / "templates" / "profile.html"
BODY_INTEL_SERVICE = ROOT / "app" / "services" / "body_intelligence.py"
BODY_INTEL_INPUTS = ROOT / "app" / "services" / "body_intelligence_inputs.py"
COACH_SERVICE = ROOT / "app" / "services" / "coach_report.py"
BODY_INTEL_ROUTER = ROOT / "app" / "routers" / "body_intelligence.py"


# ───────── route smoke ─────────


def test_profile_returns_200(client):
    r = client.get("/profile", follow_redirects=False)
    assert r.status_code == 200, r.text[:400]


# ───────── lien visible et explicite ─────────


def test_profile_html_contains_link_to_body_intelligence(client):
    body = client.get("/profile").text
    assert "/body/intelligence" in body


def test_profile_link_has_explicit_visible_text(client):
    """Le lien doit avoir un texte visible explicite ("Voir Body
    Intelligence"), pas juste une flèche ou un mot vide."""
    body = client.get("/profile").text
    m = re.search(
        r'<a\b[^>]*href="[^"]*/body/intelligence[^"]*"[^>]*>(.*?)</a>',
        body,
        re.DOTALL,
    )
    assert m is not None, "missing <a> link to /body/intelligence on /profile"
    visible = re.sub(r"<[^>]+>", "", m.group(1)).strip()
    assert visible, "link visible text must not be empty"
    # Au moins un des wording recommandés
    assert (
        "body intelligence" in visible.lower()
        or "lecture corporelle" in visible.lower()
        or "voir le détail" in visible.lower()
    ), f"link visible text not from recommended set: {visible!r}"


def test_profile_link_section_carries_explicit_title(client):
    """La carte d'entrée Body Intelligence porte un titre lisible
    ("Lecture corporelle")."""
    body = client.get("/profile").text
    assert "Lecture corporelle" in body
    # Et un contexte court ("Basé sur les séances loggées" — wording autorisé)
    assert "Basé sur les séances loggées" in body


def test_profile_link_arrow_is_decorative(client):
    """La flèche → est décorative ; doit être marquée aria-hidden."""
    body = client.get("/profile").text
    m = re.search(
        r'<a\b[^>]*href="[^"]*/body/intelligence[^"]*"[^>]*>(.*?)</a>',
        body,
        re.DOTALL,
    )
    assert m is not None
    link_html = m.group(0)
    # Si une flèche → est présente, elle doit être dans un <span aria-hidden>.
    if "→" in link_html:
        assert 'aria-hidden="true"' in link_html, (
            "decorative arrow must be wrapped in <span aria-hidden=\"true\">"
        )


# ───────── wording interdit ─────────


def test_no_forbidden_wording_on_profile_around_body_intel_card(client):
    """Scan la carte Body Intelligence du profil pour les wordings
    interdits du brief Sb_31.next.profile-link."""
    body = client.get("/profile").text.lower()
    m = re.search(
        r'<div class="card profile-body-intel-link">.*?</div>',
        body,
        re.DOTALL,
    )
    assert m is not None, "profile-body-intel-link card not found"
    block = m.group(0)
    forbidden = (
        "ton physique est",
        "analyse morphologique",
        "taux de gras",
        "diagnostic",
        "posture réelle",
        "symétrie corporelle réelle",
        "tu es gras",
        "tu es sec",
        "tu dois absolument",
    )
    for tok in forbidden:
        assert tok not in block, (
            f"forbidden wording {tok!r} in /profile body intel card"
        )


# ───────── pas de duplication du contenu Body Intelligence ─────────


def test_profile_does_not_duplicate_body_intelligence_blocks(client):
    """Sb_31.next.profile-link doit AJOUTER UN LIEN, pas réimprimer
    les 7 blocs de /body/intelligence."""
    body = client.get("/profile").text
    # Marqueurs spécifiques au rendu /body/intelligence (présents dans
    # body_intelligence.html + partials, jamais sur /profile attendu).
    for marker in (
        'data-block-key="training_consistency"',
        'data-block-key="body_metrics"',
        'data-block-key="muscle_zone_balance"',
        'data-block-key="push_pull_legs_balance"',
        'data-block-key="quality_and_confidence"',
        'data-block-key="implicit_signal_summary"',
        'data-block-key="unavailable_or_limits"',
        "data-overload-state=",  # marqueur Sx_30 propre à exercise card
    ):
        assert marker not in body, (
            f"unexpected duplication marker {marker!r} on /profile"
        )


def test_profile_does_not_pre_compute_body_snapshot(client):
    """Le template /profile ne doit pas exposer de marqueur snapshot
    Body Intelligence (cela appartient à /coach-report)."""
    body = client.get("/profile").text
    # Le snapshot coach_report est marqué par data-body-snapshot-status
    assert "data-body-snapshot-status" not in body


# ───────── garde-fous structurels Sx_31 ─────────


def test_body_intelligence_service_unchanged():
    src = BODY_INTEL_SERVICE.read_text(encoding="utf-8")
    # Sentinelle stable Sb_31.1
    assert "BODY_INTELLIGENCE_VERSION = 1" in src


def test_body_intelligence_inputs_layer_unchanged():
    src = BODY_INTEL_INPUTS.read_text(encoding="utf-8")
    assert "def build_body_intelligence_input(" in src
    assert "db: Session, user: User" in src


def test_coach_report_service_unchanged():
    src = COACH_SERVICE.read_text(encoding="utf-8")
    assert "body_intelligence" not in src


def test_body_intelligence_router_unchanged():
    src = BODY_INTEL_ROUTER.read_text(encoding="utf-8")
    # Pipeline canonique préservée
    assert "compute_body_intelligence" in src
    assert "build_body_intelligence_input" in src
    # Route canonique préservée
    assert '"/body/intelligence"' in src


# ───────── pas de nouvelle route / API JSON / migration / JS ─────────


def test_no_new_route_created_on_profile(client):
    """Pas de /profile.json créé."""
    r = client.get("/profile.json", follow_redirects=False)
    assert r.status_code in (404, 405)


def test_no_new_js_file_introduced():
    js_dir = ROOT / "app" / "static" / "js"
    existing = {p.name for p in js_dir.glob("*.js")}
    assert existing <= {"preview.js", "session_focus.js"}, (
        f"unexpected JS files: {existing}"
    )


def test_no_migration_mentions_profile_link():
    versions = ROOT / "migrations" / "versions"
    for p in versions.glob("*.py"):
        src = p.read_text(encoding="utf-8")
        assert "profile_link" not in src
        assert "body_intelligence_link" not in src


# ───────── non-régression Body Intelligence + coach-report ─────────


def test_body_intelligence_route_still_200(client):
    r = client.get("/body/intelligence", follow_redirects=False)
    assert r.status_code == 200


def test_coach_report_still_200_with_snapshot(client):
    r = client.get("/coach-report", follow_redirects=False)
    assert r.status_code == 200
    body = r.text
    # snapshot Sb_31.3 toujours visible
    assert "coach-block--body-snapshot" in body
    # Note: le coach report a aussi un lien vers /body/intelligence (Sb_31.3),
    # donc 2 occurrences au moins (coach + profile sera disjoint).
