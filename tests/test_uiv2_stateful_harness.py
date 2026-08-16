"""Sb_UIV2_STATEFUL_VISUAL_HARNESS_01 — la revue visuelle devient un vrai gate.

Le harnais ne savait capturer que des **routes**. Les défauts rapportés par le
dogfood réel vivent dans des **états d'interaction** qu'aucune URL n'atteint :
« alternatives ouvertes », « une alternative retenue », « disclosure machine
ouverte ». C'est pour cela que le train précédent n'a produit aucune capture.

Le risque de cette tranche n'est pas de mal dessiner : c'est de produire une
**preuve vide** — une capture de l'écran fermé présentée comme l'écran ouvert.
`expect_visible` existe pour rendre ce cas impossible, et ces tests le pinnent.
"""
from __future__ import annotations

import importlib.util
import pathlib

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent


def _mod(name: str):
    """Import normal : `visual_baseline_capture` importe `scripts.*`, donc un
    chargement par chemin isolé casse ses propres imports."""
    return importlib.import_module(f"scripts.{name}")


@pytest.fixture(scope="module")
def matrix():
    return _mod("visual_baseline_matrix")


@pytest.fixture(scope="module")
def capture():
    return _mod("visual_baseline_capture")


# ── Le vocabulaire d'actions est fermé ───────────────────────────────────────


def test_the_action_vocabulary_is_small_and_closed(matrix):
    assert matrix.ACTION_KINDS == frozenset(
        {"click", "check", "open_details", "press", "wait_for"})


def test_arbitrary_javascript_is_not_an_action_kind(matrix):
    """Forcer un état par JS montrerait un écran inatteignable."""
    for banned in ("evaluate", "eval", "script", "set_attribute", "inject"):
        assert banned not in matrix.ACTION_KINDS


@pytest.mark.parametrize("kind", ["click", "check", "open_details", "wait_for"])
def test_a_selector_action_refuses_an_empty_selector(matrix, kind):
    with pytest.raises(ValueError):
        matrix.Action(kind)


def test_press_requires_a_key(matrix):
    with pytest.raises(ValueError):
        matrix.Action("press")
    assert matrix.Action("press", key="Tab").key == "Tab"


def test_an_unknown_action_kind_is_refused(matrix):
    with pytest.raises(ValueError):
        matrix.Action("evaluate", "body")


# ── L'entrée porte le scénario ───────────────────────────────────────────────


def test_an_entry_can_carry_actions_and_an_expected_state(matrix):
    entry = matrix.BaselineEntry(
        slug="session-alternatives-open", route="/", priority="P0",
        auth_required=True, state="s", data_fixture="f",
        actions=(matrix.Action("open_details", ".substitute-picker"),),
        expect_visible=".segmented--stacked",
    )
    assert entry.actions[0].kind == "open_details"
    assert entry.expect_visible == ".segmented--stacked"


def test_entries_without_actions_still_work(matrix):
    """Les entrées route-seule existantes ne changent pas de comportement."""
    entry = matrix.BaselineEntry(
        slug="home", route="/", priority="P0", auth_required=True,
        state="s", data_fixture="f")
    assert entry.actions == ()
    assert entry.expect_visible == ""


def test_the_existing_p0_matrix_is_unchanged_by_the_extension(matrix):
    slugs = {e.slug for e in matrix.P0_ENTRIES} if hasattr(matrix, "P0_ENTRIES") \
        else {e.slug for e in matrix._P0_ENTRIES}
    assert "home-authenticated" in slugs
    assert "profile" in slugs
    # Aucune entrée historique n'a gagné d'actions par accident.
    entries = getattr(matrix, "P0_ENTRIES", None) or matrix._P0_ENTRIES
    assert all(e.actions == () for e in entries)


# ── L'exécuteur ──────────────────────────────────────────────────────────────


class _FakePage:
    """Enregistre les appels au lieu de piloter un navigateur."""

    def __init__(self, *, fail_on_wait: str | None = None):
        self.calls: list[tuple[str, str]] = []
        self._fail_on_wait = fail_on_wait

    def click(self, selector, timeout=None):
        self.calls.append(("click", selector))

    def check(self, selector, timeout=None):
        self.calls.append(("check", selector))

    def wait_for_selector(self, selector, state=None, timeout=None):
        self.calls.append(("wait_for_selector", selector))
        if self._fail_on_wait and selector == self._fail_on_wait:
            raise TimeoutError(f"not visible: {selector}")

    class _Keyboard:
        def __init__(self, outer):
            self.outer = outer

        def press(self, key):
            self.outer.calls.append(("press", key))

    @property
    def keyboard(self):
        return _FakePage._Keyboard(self)


def _entry(matrix, **kw):
    base = dict(slug="s", route="/", priority="P0", auth_required=True,
                state="s", data_fixture="f")
    base.update(kw)
    return matrix.BaselineEntry(**base)


def test_open_details_clicks_the_summary_not_the_attribute(matrix, capture):
    """Le geste réel exerce la sémantique native de `<details>`."""
    page = _FakePage()
    capture.apply_actions(
        page, _entry(matrix, actions=(matrix.Action("open_details", ".panel"),)))
    assert ("click", ".panel > summary") in page.calls


def test_actions_run_in_declared_order(matrix, capture):
    page = _FakePage()
    capture.apply_actions(page, _entry(matrix, actions=(
        matrix.Action("wait_for", ".card"),
        matrix.Action("open_details", ".panel"),
        matrix.Action("check", "#opt-2"),
        matrix.Action("press", key="Tab"),
    )))
    assert page.calls == [
        ("wait_for_selector", ".card"),
        ("click", ".panel > summary"),
        ("check", "#opt-2"),
        ("press", "Tab"),
    ]


def test_the_expected_state_is_verified_after_the_actions(matrix, capture):
    page = _FakePage()
    capture.apply_actions(page, _entry(
        matrix,
        actions=(matrix.Action("open_details", ".panel"),),
        expect_visible=".choices"))
    assert page.calls[-1] == ("wait_for_selector", ".choices")


def test_a_scenario_whose_state_was_not_reached_fails_loudly(matrix, capture):
    """La preuve vide que ce harnais existe pour empêcher.

    Si le geste échoue silencieusement, la capture montrerait l'écran fermé en
    le faisant passer pour l'écran ouvert. `expect_visible` transforme ce cas en
    échec au lieu d'une image trompeuse.
    """
    page = _FakePage(fail_on_wait=".choices")
    entry = _entry(
        matrix,
        actions=(matrix.Action("open_details", ".panel"),),
        expect_visible=".choices")
    with pytest.raises(TimeoutError):
        capture.apply_actions(page, entry)


def test_an_entry_without_expectation_skips_the_verification(matrix, capture):
    page = _FakePage()
    capture.apply_actions(page, _entry(matrix))
    assert page.calls == []


def test_the_executor_never_evaluates_javascript(capture):
    import inspect

    src = inspect.getsource(capture.apply_actions)
    for banned in ("evaluate", "eval(", "add_script_tag", "set_content"):
        assert banned not in src


def test_the_executor_is_wired_before_the_screenshot(capture):
    import inspect

    src = inspect.getsource(capture._capture_real)
    assert "apply_actions(page, plan.entry)" in src
    assert src.index("apply_actions") < src.index("page.screenshot")


# ── Pas de nouveau framework ─────────────────────────────────────────────────


def test_no_new_browser_framework_was_introduced():
    req = (REPO_ROOT / "requirements.txt").read_text(encoding="utf-8").lower()
    for banned in ("selenium", "puppeteer", "cypress", "webdriver"):
        assert banned not in req


def test_the_harness_still_uses_playwright(capture):
    import inspect

    assert "playwright" in inspect.getsource(capture).lower()
