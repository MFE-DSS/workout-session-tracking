"""Sb_BODYMAP_FRAME_ATLAS_01 — A5: the frame selector at 360 px, measured.

Reading the CSS cannot answer "does it overflow" or "is the pill tappable" — the
last three real defects on this repo (393 px in a 360 viewport, a CTA covered by
the bottom nav, an anchor parked behind the sticky header) were all found by
measuring a browser and none by reading source. So this measures.

The page is rendered by the real SSR route and laid out with the real
stylesheet; only the transport is short-circuited. That keeps the test hermetic
(no port, no server thread) while still exercising the shipped markup and the
shipped CSS, which is where a filmstrip regression would live.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app.services.bodymap_frames import plate_for_region

playwright_api = pytest.importorskip(
    "playwright.sync_api", reason="Playwright not installed"
)

ROOT = Path(__file__).resolve().parent.parent
CSS = ROOT / "app" / "static" / "css" / "app.css"

MOBILE_WIDTH = 360
MOBILE_HEIGHT = 640
#: Minimum comfortable touch target. The selector is a control, not decoration.
MIN_TARGET_PX = 44


@pytest.fixture(scope="module")
def browser():
    """One Chromium for the module; the page itself is per-test."""
    try:
        driver = playwright_api.sync_playwright().start()
    except Exception as exc:  # pragma: no cover - environment dependent
        pytest.skip(f"Playwright runtime unavailable: {exc}")
    try:
        instance = driver.chromium.launch()
    except Exception as exc:  # pragma: no cover - browser not downloaded
        driver.stop()
        pytest.skip(f"Chromium unavailable: {exc}")
    yield instance
    instance.close()
    driver.stop()


@pytest.fixture
def rendered(client, browser):
    """Lay the real SSR markup out with the real stylesheet at 360 px."""
    response = client.get("/science")
    assert response.status_code == 200

    css = CSS.read_text(encoding="utf-8")
    html = response.text
    if "</head>" in html:
        html = html.replace("</head>", f"<style>{css}</style></head>", 1)
    else:  # defensive: template without a head
        html = f"<style>{css}</style>{html}"

    page = browser.new_page(viewport={"width": MOBILE_WIDTH, "height": MOBILE_HEIGHT})
    page.set_content(html, wait_until="load")
    yield page
    page.close()


def test_a5_page_does_not_scroll_horizontally(rendered):
    overflow = rendered.evaluate(
        "() => document.documentElement.scrollWidth "
        "- document.documentElement.clientWidth"
    )
    assert overflow <= 0, f"horizontal overflow of {overflow}px at {MOBILE_WIDTH}px"


def test_a5_every_frame_pill_is_a_real_touch_target(rendered):
    pills = rendered.locator(".muscle-focus__toggle-btn")
    count = pills.count()
    assert count == plate_for_region("shoulders").frame_count

    for index in range(count):
        box = pills.nth(index).bounding_box()
        assert box is not None, f"pill {index} has no box"
        assert box["height"] >= MIN_TARGET_PX, (
            f"pill {index} is {box['height']}px tall, below the {MIN_TARGET_PX}px target"
        )
        assert box["width"] > 0


def test_a5_pills_stay_inside_the_viewport(rendered):
    pills = rendered.locator(".muscle-focus__toggle-btn")
    for index in range(pills.count()):
        box = pills.nth(index).bounding_box()
        right_edge = box["x"] + box["width"]
        assert right_edge <= MOBILE_WIDTH, (
            f"pill {index} extends to {right_edge}px, past the {MOBILE_WIDTH}px viewport"
        )


def test_a5_frame_viewport_never_widens_the_column(rendered):
    """The strip is N x 100% wide; only its crop may be visible."""
    frame = rendered.locator(".muscle-focus__frame--strip").first
    box = frame.bounding_box()
    assert box is not None
    assert box["width"] <= MOBILE_WIDTH


def test_a5_selecting_a_frame_moves_the_strip_without_javascript(rendered):
    """Proves the filmstrip actually slides — the whole point of the mechanism."""
    shoulders = plate_for_region("shoulders")
    first, second = shoulders.frames[0].code, shoulders.frames[1].code

    strip = rendered.locator(".muscle-focus__frame--strip svg").first

    rendered.locator(f'label[for="mf-shoulders-{first}"]').click()
    before = strip.evaluate("el => getComputedStyle(el).transform")

    rendered.locator(f'label[for="mf-shoulders-{second}"]').click()
    after = strip.evaluate("el => getComputedStyle(el).transform")

    assert before != after, "selecting a different frame must move the strip"
    assert rendered.locator(f"#mf-shoulders-{second}").is_checked()


def test_a5_landmark_follows_the_selected_frame(rendered):
    """Exactly one orientation cue is readable at a time."""
    shoulders = plate_for_region("shoulders")
    for frame in shoulders.frames:
        rendered.locator(f'label[for="mf-shoulders-{frame.code}"]').click()
        shown = rendered.locator(".muscle-focus__landmark:visible")
        assert shown.count() == 1, f"{frame.code}: expected one landmark, saw {shown.count()}"
        assert frame.landmark in shown.first.text_content()
