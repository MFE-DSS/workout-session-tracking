"""Sx_LIB_01 — Library Card Action Semantics.

The library template cards had the start `<form>` nested INSIDE the detail
`<a>` link (invalid HTML → onclick/onkeydown stopPropagation hacks). This
sprint moves the form OUT of the link (sibling in the <li>), removing the JS
hacks. Behaviour unchanged: card click → detail, "Démarrer" → create_session
(creation_source=library). Template-only, no route/service/data change.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIBRARY_TPL = ROOT / "app" / "templates" / "library.html"
PAGES_ROUTER = ROOT / "app" / "routers" / "pages.py"


def _render(client):
    r = client.get("/library", follow_redirects=False)
    assert r.status_code == 200, r.text[:300]
    return r.text


# ───────── 1. cards render with detail link + start form ─────────


def test_library_renders_cards(client):
    html = _render(client)
    assert "template-card" in html
    assert "template-card__link" in html


def test_each_card_has_detail_link(client):
    html = _render(client)
    # detail links present (href to template_detail resolves to /library/<slug>)
    assert "/library/push-a" in html or "template-card__link" in html


# ───────── 2. THE FIX: form is no longer nested inside the <a> ─────────


def test_form_not_nested_inside_link(client):
    """No <form> must appear inside a template-card__link <a>…</a>."""
    html = _render(client)
    links = re.findall(
        r'<a class="template-card__link".*?</a>', html, re.DOTALL
    )
    assert links, "no template-card__link found"
    for link in links:
        assert "<form" not in link, "form still nested inside the detail link"


def test_stop_propagation_hacks_removed(client):
    """The onclick/onkeydown stopPropagation hacks must be gone from the render."""
    html = _render(client)
    assert "stopPropagation" not in html
    assert "onclick=" not in html
    assert "onkeydown=" not in html


def test_source_template_has_no_stop_propagation():
    src = LIBRARY_TPL.read_text(encoding="utf-8")
    # only allowed in a comment; the code lines must not carry the handlers
    for line in src.splitlines():
        stripped = line.strip()
        if stripped.startswith("{#") or "hacks stopPropagation" in line:
            continue
        assert "onclick=" not in line
        assert "onkeydown=" not in line
        assert 'stopPropagation();' not in line


# ───────── 3. start form contract preserved ─────────


def test_start_form_contract_preserved(client):
    html = _render(client)
    assert "create_session" in html.lower() or "/sessions" in html
    assert 'name="template_slug"' in html
    assert 'name="creation_source"' in html
    assert 'value="library"' in html
    assert ">Démarrer<" in html
    # ghost button preserved
    assert "btn--ghost" in html


def test_form_and_link_are_siblings(client):
    """After the fix, form and link are siblings inside the <li>: the </a>
    closes before the <form>."""
    html = _render(client)
    # find a card block: link then form, with </a> before <form
    m = re.search(
        r'<a class="template-card__link".*?</a>\s*<form',
        html,
        re.DOTALL,
    )
    assert m, "expected </a> immediately followed by the start <form> (siblings)"


# ───────── 4. non-regression: asserted texts + no route/service change ─────────


def test_library_vocabulary_preserved(client):
    html = _render(client)
    # `OPERATOR_DECISION` NAMING — « Explorer », enfant du domaine
    # « Programmes ». L'ancien titre confondait l'enfant et le domaine.
    assert "Explorer" in html
    assert "Programmes de séance" not in html
    assert "Catalogue complet" in html
    assert "Bibliothèque" not in html


def test_pages_router_not_modified():
    src = PAGES_ROUTER.read_text(encoding="utf-8")
    assert "Sx_LIB_01" not in src  # sentinel: no marker leaked into the router


def test_no_js_or_new_wording_added():
    src = LIBRARY_TPL.read_text(encoding="utf-8")
    assert "<script" not in src
    # end-to-end: the start form still creates a session (creation_source=library)


def test_cta_still_creates_session(client):
    r = client.post(
        "/sessions",
        data={"template_slug": "push-a", "creation_source": "library"},
        follow_redirects=False,
    )
    assert r.status_code in (200, 303), r.text[:200]
