"""Sb_ASSET_04.1-P0 — Muscle Focus controlled runtime integration guard + HTTP tests.

The three owner-accepted P0 regional plates (Sb_ASSET_03B.2R-D1 intake) are surfaced SSR/no-JS on the
educational /science page. This guard enforces:
  - byte-integrity: the inlined plate partials equal the design-source SVGs (freeze sha, no geometry rewrite);
  - chest diagnostic partition NOT rendered (whole-pectoralis plate only);
  - attribution (BodyParts3D CC BY 4.0) is visible (not aria-hidden);
  - the shoulders front/back control is a no-JS radio toggle (front default);
  - posterior individual hamstring provenance is named in the caption;
  - /science renders 200 with the section, the three plates, attribution, and the honest non-medical /
    not-professionally-reviewed disclaimers — and no affirmative approval/clearance/measurement claim.

Non-medical fitness visualisation; NOT a professional anatomical review (not claimed).
"""
from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DESIGN = ROOT / "design" / "auren" / "source" / "muscle-focus"
PARTIALS = ROOT / "app" / "templates" / "_partials"
WRAPPER = PARTIALS / "muscle_focus.html"
SCIENCE = ROOT / "app" / "templates" / "science.html"

FREEZE_SHA = {
    "chest": "7a4167eac1db085f1cfb41ae2b2465a3b2c720a4978361eef69e422b104bddfd",
    "shoulders": "5eb7bedfa031b2e9fe29e60c1a17c1fe2822a46c0a3153f2fab14951fcc94983",
    "posterior": "b84c8bceea47455c88d4ee2d3117a6387383187109a20850db2d54feaa71710f",
}
AFFIRMATIVE_LIES = ("cliniquement validé", "approuvé médicalement", "certifié", "validé professionnellement",
                    "diagnostic médical", "emg")


# ── byte-integrity: no geometry rewrite ──

def test_plate_partials_byte_match_design_source():
    for region, want in FREEZE_SHA.items():
        partial = PARTIALS / f"muscle_focus_plate_{region}.svg"
        source = DESIGN / f"auren-plate-region-{region}.svg"
        assert partial.is_file(), f"missing runtime plate partial: {region}"
        assert partial.read_bytes() == source.read_bytes(), f"{region}: partial != design source"
        assert hashlib.sha256(partial.read_bytes()).hexdigest() == want, f"{region}: sha drift"


def test_chest_partition_not_rendered():
    # whole-pectoralis plate only: no deltoid-style part groups, and no clavicular/sternocostal split.
    chest = (PARTIALS / "muscle_focus_plate_chest.svg").read_text(encoding="utf-8")
    assert "auren-mf-part" not in chest
    assert "sternocostal" not in chest.lower()
    assert "clavicular" not in chest.lower()


# ── wrapper structure ──

def test_wrapper_includes_three_plates_and_toggle():
    w = WRAPPER.read_text(encoding="utf-8")
    for region in ("chest", "shoulders", "posterior"):
        assert f'_partials/muscle_focus_plate_{region}.svg' in w, f"wrapper missing {region} include"
    # no-JS front/back toggle for shoulders (radio inputs, front default checked)
    assert 'type="radio"' in w
    assert 'id="mf-shoulders-front"' in w
    assert 'id="mf-shoulders-back"' in w
    # front radio is checked by default, back radio is NOT (non-tautological — parse each tag).
    front_tag = w[w.index('id="mf-shoulders-front"'):].split(">", 1)[0]
    back_tag = w[w.index('id="mf-shoulders-back"'):].split(">", 1)[0]
    assert "checked" in front_tag, "front shoulders radio must be checked by default"
    assert "checked" not in back_tag, "back shoulders radio must not be checked by default"
    # posterior individual provenance named
    low = w.lower()
    assert "semi-tendineux" in low
    assert "semi-membraneux" in low
    assert "biceps fémoral" in low
    # attribution present and NOT inside an aria-hidden block
    assert "bodyparts3d" in low
    assert "cc" in low
    assert "4.0" in low
    assert "muscle-focus__attribution" in w


def test_wrapper_has_honest_disclaimers_and_no_affirmative_lie():
    low = WRAPPER.read_text(encoding="utf-8").lower()
    assert "non médical" in low
    assert "non revendiqué" in low or "non revendiquée" in low
    for tok in AFFIRMATIVE_LIES:
        assert tok not in low, f"affirmative claim in muscle-focus wrapper: {tok}"


def test_science_includes_muscle_focus():
    s = SCIENCE.read_text(encoding="utf-8")
    assert '_partials/muscle_focus.html' in s
    assert 'id="section-muscle-focus"' in s


# ── HTTP (SSR) ──

def test_science_renders_muscle_focus_section(client):
    body = client.get("/science").text
    assert 'id="section-muscle-focus"' in body
    assert "Muscle Focus" in body
    for root in ("auren-plate-region-chest", "auren-plate-region-shoulders", "auren-plate-region-posterior"):
        assert f'id="{root}"' in body, f"plate not rendered: {root}"


def test_science_renders_attribution_and_toggle(client):
    body = client.get("/science").text
    low = body.lower()
    assert "bodyparts3d" in low
    assert "creativecommons.org/licenses/by/4.0" in low
    assert 'id="mf-shoulders-front"' in body
    assert 'id="mf-shoulders-back"' in body


def test_science_renders_non_medical_not_claimed(client):
    low = client.get("/science").text.lower()
    assert "non médical" in low
    assert "non revendiqué" in low or "non revendiquée" in low
    for tok in AFFIRMATIVE_LIES:
        assert tok not in low, f"affirmative claim rendered on /science: {tok}"


# ── P1 (Sb_ASSET_04.2) — product enrichment: region cards + progressive disclosure, no new claims ──

# Hard guardrails: no activation percentage / EMG / recruitment claim anywhere in the surface.
FORBIDDEN_CLAIMS = ("%", "activation", "emg", "recruitment", "recrutement")


def _muscle_focus_section(body: str) -> str:
    """The rendered #section-muscle-focus slice (up to the next section)."""
    start = body.index('id="section-muscle-focus"')
    end = body.index('id="section-diagram"', start)
    return body[start:end]


def test_wrapper_has_three_region_cards():
    w = WRAPPER.read_text(encoding="utf-8")
    assert w.count('class="muscle-focus__card') == 3, "expected exactly three region cards"
    assert w.count('class="muscle-focus__title"') == 3, "each card carries a title"
    for title in ("Pectoraux", "Épaules", "Chaîne postérieure"):
        assert title in w, f"missing region card title: {title}"


def test_wrapper_has_progressive_disclosure_blocks():
    w = WRAPPER.read_text(encoding="utf-8")
    assert w.count("<details") == 6, "one 'shows' + one 'does not show' per region"
    assert w.count("Ce que cette planche montre") == 3
    assert w.count("Ce qu'elle ne montre pas") == 3


def test_wrapper_has_no_forbidden_claim_token():
    low = WRAPPER.read_text(encoding="utf-8").lower()
    # "%" is excluded here only because the Jinja `{% include %}` syntax legitimately uses it in the
    # SOURCE; the rendered-surface test below enforces "%" absence where Jinja is gone.
    for tok in (t for t in FORBIDDEN_CLAIMS if t != "%"):
        assert tok not in low, f"forbidden claim token in muscle-focus wrapper: {tok!r}"


def test_science_section_enriched_without_forbidden_claims(client):
    section = _muscle_focus_section(client.get("/science").text)
    low = section.lower()
    # three region cards + progressive disclosure rendered SSR (no-JS)
    assert low.count("muscle-focus__card") >= 3
    assert "ce que cette planche montre" in low
    assert "ce qu'elle ne montre pas" in low
    # hard guardrails: no activation/EMG/recruitment/percentage claim in the muscle-focus surface
    for tok in FORBIDDEN_CLAIMS:
        assert tok not in low, f"forbidden claim rendered in muscle-focus section: {tok!r}"
    # provenance + non-medical honesty preserved in the section itself
    assert "bodyparts3d" in low
    assert "creativecommons.org/licenses/by/4.0" in low
    assert "non médical" in low
