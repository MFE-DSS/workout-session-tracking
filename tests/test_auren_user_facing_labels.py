"""Sb_UI_10.4 — User-Facing Docs / Labels Auren Pass (SPIGNOS → Auren).

Last user-facing surfaces migrate their visible product name to « Auren » :
/science (lede, cardio capture, materialisation header, architecture header),
the science diagram SVG accessible title, /science/atlas (lede) and the
/coach-report guardrails block (« données saisies … dans Auren »).

SPIGNOS stays the INTERNAL name (repo/code). No route, metric, calculation,
coach-report logic, CSS, JS, manifest or asset change. After this pass, no
TEMPLATE renders « SPIGNOS » to the user anywhere in the app. One known
residual remains OUT of template scope: the seeded method rule
'plages-repetitions' (data/method_rules.json — data/ forbidden in 10.4),
pinned by a dedicated sentinel test below.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "app" / "templates"
SCIENCE = TEMPLATES / "science.html"
ATLAS = TEMPLATES / "atlas.html"
COACH = TEMPLATES / "coach_report.html"
DIAGRAM = TEMPLATES / "_partials" / "science_diagram.svg"
TARGETS = (SCIENCE, ATLAS, COACH, DIAGRAM)


def _get(client, path):
    r = client.get(path, follow_redirects=False)
    assert r.status_code == 200, f"{path} -> {r.status_code}: {r.text[:200]}"
    return r.text


# ───────── rendered surfaces: Auren visible, SPIGNOS gone ─────────


def test_science_renders_auren_template_strings(client):
    body = _get(client, "/science")
    assert "Comment Auren transforme une série loguée" in body
    assert "Auren capture : durée, BPM moyen" in body
    assert "Comment Auren materialise ces concepts" in body
    assert "Architecture du cockpit Auren" in body


def test_science_remaining_spignos_is_only_the_seeded_method_rule(client):
    """KNOWN RESIDUAL, pinned so it cannot silently grow. The seeded method
    rule 'plages-repetitions' (data/method_rules.json → method_rules table)
    still reads « …dans SPIGNOS est dérivé… » on /science. data/** is
    FORBIDDEN in Sb_UI_10.4 → the fix is a dedicated data micro-pass on
    explicit operator GO. When that pass lands, flip this test to assert 0."""
    body = _get(client, "/science")
    assert body.count("SPIGNOS") == 1, (
        f"expected exactly the 1 known seeded residual, got {body.count('SPIGNOS')}"
    )
    assert "dans SPIGNOS est dérivé" in body


def test_science_diagram_svg_title_is_auren(client):
    body = _get(client, "/science")
    assert "Architecture des modules Auren" in body
    # a11y wiring of the inline SVG stays intact
    assert 'aria-labelledby="diagram-title diagram-desc"' in body


def test_atlas_renders_auren_no_spignos(client):
    body = _get(client, "/science/atlas")
    assert "SPIGNOS" not in body
    assert "les machines qui reviennent dans Auren" in body


def test_coach_report_guardrails_auren_no_spignos(client):
    body = _get(client, "/coach-report")
    assert "SPIGNOS" not in body
    assert "données saisies par l'utilisateur dans Auren" in body


def test_coach_report_non_medical_guardrail_preserved(client):
    """The rebrand must not weaken the non-medical disclaimer."""
    body = _get(client, "/coach-report")
    assert "ne remplace pas" in body
    assert "avis médical" in body


def test_science_diagram_desc_unchanged(client):
    """Only the SVG <title> was rebranded; the <desc> flow text is intact."""
    body = _get(client, "/science")
    assert "Programmes alimente Seance" in body


# ───────── source-level guards ─────────


def test_no_spignos_in_104_template_sources():
    for f in TARGETS:
        assert "SPIGNOS" not in f.read_text(encoding="utf-8"), f.name


def test_no_orion_string_introduced():
    for f in TARGETS:
        src = f.read_text(encoding="utf-8")
        assert "Orion" not in src
        assert "ORION" not in src


def test_no_template_renders_spignos_anywhere():
    """Milestone guard: after 10.1 + 10.3 + 10.4, every remaining SPIGNOS
    occurrence in ANY template lives inside a Jinja comment ({# … #},
    stripped at render). No template ships SPIGNOS to the user."""
    for f in TEMPLATES.rglob("*.html"):
        src = f.read_text(encoding="utf-8")
        rendered_side = re.sub(r"\{#.*?#\}", "", src, flags=re.DOTALL)
        assert "SPIGNOS" not in rendered_side, f"visible SPIGNOS in {f}"


# ───────── non-regression: 10.1 / 10.3 surfaces stay stable ─────────


def test_shell_still_auren_after_104(client):
    html = _get(client, "/")
    assert "· Auren</title>" in html
    assert "SPIGNOS" not in html


def test_public_auth_sources_untouched_by_104():
    for name in ("welcome.html", "login.html", "register.html"):
        src = (TEMPLATES / name).read_text(encoding="utf-8")
        assert re.search(
            r'<meta name="apple-mobile-web-app-title" content="Auren"\s*/?>', src
        ), f"10.3 state altered in {name}"
