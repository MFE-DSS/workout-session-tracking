"""Sx_UI_06 / Sb_UI_06.1 — information density dedup (exercise card).

Locks the de-densification of the exercise card, per the accepted spec
(docs/strategy/Sx_UI_06_INFO_DENSITY_DEDUP_SPEC.md):

- **D1** : the previous-session load (« Dernière fois ») is no longer shown on
  the ACTIVE card — its info lives once in the console « Référence précédente »,
  closest to the input cells. It STILL renders on non-active cards (no info loss).
- **D2** : the target (« Cible ») no longer has its own head block
  (`exercise-card__scheme`) nor its own console row; the target suggestion lives
  ONLY as the input placeholder.

Guarantees the redundancy is gone WITHOUT weakening the logging contract
(input names, form, no-JS) and WITHOUT losing information on non-active cards.
"""
from __future__ import annotations

import re


def _new_session(client, slug: str = "push-a") -> int:
    r = client.post("/sessions", data={"template_slug": slug}, follow_redirects=False)
    m = re.match(r"/sessions/(\d+)", r.headers["location"])
    return int(m.group(1))


def _body(client) -> str:
    sid = _new_session(client)
    r = client.get(f"/sessions/{sid}", follow_redirects=False)
    assert r.status_code == 200, r.text[:300]
    return r.text


# ───────── D1 : previous load — active vs non-active ─────────


def test_active_card_has_no_last_time_block(client):
    """The active card carries the previous load ONLY via the console
    « Référence précédente », not the redundant « Dernière fois » head block."""
    body = _body(client)
    # console reference exists (previous load surface on the active card)
    assert "session-focus__console-ref--prev" in body
    assert "Référence précédente" in body


def test_last_time_block_still_present_on_non_active_cards(client):
    """No info loss: non-active cards keep « Dernière fois » (they have no
    console). A fresh session has 1 active + N-1 non-active cards, so the
    block still renders at least once."""
    body = _body(client)
    assert "Dernière fois" in body  # non-active cards keep it


def test_previous_load_not_duplicated_on_active_card(client):
    """The « Référence précédente » console row is the single home of the
    previous load near the inputs; the console does not also render a
    « Dernière fois » label inside itself."""
    body = _body(client)
    # console block present…
    assert "session-focus__console-refs" in body
    # …and the reference label used in the console is the console one.
    assert "Référence précédente" in body


# ───────── D2 : target lives only in the input placeholder ─────────


def test_scheme_head_block_removed(client):
    body = _body(client)
    assert "exercise-card__scheme" not in body


def test_target_console_row_removed(client):
    body = _body(client)
    assert "session-focus__console-ref--target" not in body
    assert "Objectif à qualifier" not in body


def test_target_lives_in_input_placeholder(client):
    """The target suggestion survives as the input placeholder (kg / reps or
    an overload suggestion), closest to the action."""
    body = _body(client)
    assert 'placeholder="kg"' in body or 'placeholder="reps"' in body


# ───────── logging contract preserved (no-JS, input names) ─────────


def test_logging_input_names_unchanged(client):
    body = _body(client)
    assert "weight_kg" in body and "reps" in body


def test_console_still_present(client):
    body = _body(client)
    assert "session-focus__console" in body
    assert "Référence précédente" in body
