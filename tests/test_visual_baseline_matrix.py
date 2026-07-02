"""Sb_UI_11.1 — tests unitaires de la matrice baseline.

Ces tests ne nécessitent PAS Playwright installé. Ils valident uniquement
la structure de données et les helpers du module `scripts.visual_baseline_matrix`.
"""
from __future__ import annotations

import pytest

from scripts.visual_baseline_matrix import (
    BASELINE_MATRIX,
    OPTIONAL_ENV_VARS,
    REQUIRED_ENV_VARS_FOR_ACTIVE_SESSION,
    REQUIRED_ENV_VARS_FOR_AUTH,
    REQUIRED_ENV_VARS_FOR_DONE_SESSION,
    VIEWPORTS,
    BaselineEntry,
    build_plan,
    entries_for_priority,
    output_path,
    viewport_size,
)

_REQUIRED_P0_SLUGS: frozenset[str] = frozenset(
    {
        "home-authenticated",
        "home-no-active-session",
        "session-detail-active",
        "session-detail-done",
        "progression",
        "profile",
        "login",
        "register",
    }
)


class TestP0Matrix:
    def test_contains_all_required_p0_slugs(self):
        p0_slugs = {e.slug for e in entries_for_priority("P0")}
        missing = _REQUIRED_P0_SLUGS - p0_slugs
        assert not missing, f"Missing required P0 slugs: {sorted(missing)}"

    def test_p0_count_is_at_least_minimum(self):
        # Sx_UI_11 §5 : P0 = 14 screenshots minimum (7 écrans × 2 viewports).
        # Ici on livre 8 écrans P0 × 2 = 16 screenshots (16 ≥ 14).
        p0_entries = entries_for_priority("P0")
        total_screenshots = sum(len(e.viewports) for e in p0_entries)
        assert total_screenshots >= 14, (
            f"P0 baseline must produce ≥14 screenshots, got {total_screenshots}."
        )

    def test_p0_entries_all_have_two_viewports(self):
        for entry in entries_for_priority("P0"):
            assert set(entry.viewports) == {"mobile", "desktop"}, (
                f"P0 entry {entry.slug!r} must target mobile AND desktop."
            )


class TestEntryStructure:
    @pytest.mark.parametrize("entry", BASELINE_MATRIX, ids=lambda e: e.slug)
    def test_entry_has_all_required_fields(self, entry: BaselineEntry):
        assert entry.slug, "slug required"
        assert entry.route, "route required"
        assert entry.priority in {"P0", "P1", "P2"}
        assert isinstance(entry.auth_required, bool)
        assert entry.state, "state required"
        assert entry.data_fixture, "data_fixture required"
        assert entry.viewports, "viewports required"
        for vp in entry.viewports:
            assert vp in VIEWPORTS, f"unknown viewport {vp!r}"

    @pytest.mark.parametrize("entry", BASELINE_MATRIX, ids=lambda e: e.slug)
    def test_slug_is_kebab_case(self, entry: BaselineEntry):
        # kebab-case strict : lowercase, digits allowed, only '-' as separator.
        assert entry.slug == entry.slug.lower(), f"slug not lowercase: {entry.slug!r}"
        assert " " not in entry.slug, f"space in slug: {entry.slug!r}"
        assert "_" not in entry.slug, f"underscore in slug: {entry.slug!r}"

    @pytest.mark.parametrize("entry", BASELINE_MATRIX, ids=lambda e: e.slug)
    def test_route_starts_with_slash(self, entry: BaselineEntry):
        assert entry.route.startswith("/"), (
            f"route must start with '/', got {entry.route!r}"
        )


class TestViewportSize:
    def test_mobile_dimensions(self):
        assert viewport_size("mobile") == (360, 640)

    def test_desktop_dimensions(self):
        assert viewport_size("desktop") == (1440, 900)

    def test_unknown_viewport_raises(self):
        with pytest.raises(ValueError):
            viewport_size("watch")  # type: ignore[arg-type]


class TestOutputPath:
    def test_kebab_case_only(self):
        with pytest.raises(ValueError):
            output_path("out", "Home_Authenticated", "mobile")

    def test_space_in_slug_rejected(self):
        with pytest.raises(ValueError):
            output_path("out", "home authenticated", "mobile")

    def test_unknown_viewport_rejected(self):
        with pytest.raises(ValueError):
            output_path("out", "home-authenticated", "watch")  # type: ignore[arg-type]

    def test_path_shape(self):
        path = output_path("var/visual-baseline", "session-detail-active", "mobile")
        assert path == "var/visual-baseline/session-detail-active/mobile-authenticated.png"

    def test_state_suffix_override(self):
        path = output_path(
            "var/visual-baseline",
            "session-detail-active",
            "desktop",
            state_suffix="active",
        )
        assert path == "var/visual-baseline/session-detail-active/desktop-active.png"

    def test_anonymous_default_suffix(self):
        path = output_path("var/visual-baseline", "login", "mobile")
        assert path.endswith("/login/mobile-anonymous.png")


class TestBuildPlan:
    def test_p0_all_viewports_produces_double_entries(self):
        p0_entries = entries_for_priority("P0")
        plans = build_plan(p0_entries, "all", "var/visual-baseline")
        # 8 P0 entries × 2 viewports = 16 plans
        assert len(plans) == len(p0_entries) * 2

    def test_mobile_only_filter(self):
        p0_entries = entries_for_priority("P0")
        plans = build_plan(p0_entries, "mobile", "var/visual-baseline")
        assert all(p.viewport == "mobile" for p in plans)
        assert len(plans) == len(p0_entries)

    def test_desktop_only_filter(self):
        p0_entries = entries_for_priority("P0")
        plans = build_plan(p0_entries, "desktop", "var/visual-baseline")
        assert all(p.viewport == "desktop" for p in plans)
        assert len(plans) == len(p0_entries)

    def test_plan_paths_deterministic(self):
        p0_entries = entries_for_priority("P0")
        plans_a = build_plan(p0_entries, "all", "var/visual-baseline")
        plans_b = build_plan(p0_entries, "all", "var/visual-baseline")
        paths_a = [p.output_path for p in plans_a]
        paths_b = [p.output_path for p in plans_b]
        assert paths_a == paths_b


class TestEnvVarNames:
    def test_auth_env_names_are_declared(self):
        assert "AUREN_BASELINE_USERNAME" in REQUIRED_ENV_VARS_FOR_AUTH
        assert "AUREN_BASELINE_PASSWORD" in REQUIRED_ENV_VARS_FOR_AUTH

    def test_session_env_names_are_declared(self):
        assert "AUREN_BASELINE_ACTIVE_SESSION_ID" in REQUIRED_ENV_VARS_FOR_ACTIVE_SESSION
        assert "AUREN_BASELINE_DONE_SESSION_ID" in REQUIRED_ENV_VARS_FOR_DONE_SESSION

    def test_env_var_names_prefix(self):
        all_names = (
            *REQUIRED_ENV_VARS_FOR_AUTH,
            *REQUIRED_ENV_VARS_FOR_ACTIVE_SESSION,
            *REQUIRED_ENV_VARS_FOR_DONE_SESSION,
            *OPTIONAL_ENV_VARS,
        )
        for name in all_names:
            assert name.startswith("AUREN_BASELINE_"), (
                f"env var must be prefixed AUREN_BASELINE_, got {name!r}"
            )


class TestSecurityInvariants:
    def test_no_matrix_entry_encodes_password_or_token(self):
        # Aucune entrée ne doit exposer une VALEUR de credential.
        # Note : les routes légitimes du produit peuvent inclure le mot
        # "password" (ex : /forgot-password, /profile/password) — ce sont
        # des noms de route publics, jamais des valeurs.
        # On interdit les patterns qui ressemblent à une injection de valeur.
        forbidden_patterns = (
            "password=",
            "password:",
            "token=",
            "token:",
            "secret=",
            "secret:",
            "bearer ",
            "basic ",
            "api-key=",
            "apikey=",
        )
        for entry in BASELINE_MATRIX:
            payload = " ".join(
                (
                    entry.slug,
                    entry.route,
                    entry.state,
                    entry.data_fixture,
                    entry.notes,
                )
            ).lower()
            for pattern in forbidden_patterns:
                assert pattern not in payload, (
                    f"Entry {entry.slug!r} contains forbidden pattern {pattern!r} "
                    "— matrix must never expose credential values."
                )

    def test_no_prod_account_referenced(self):
        # Interdit d'utiliser martin_prod_smoke ou tout compte prod concret.
        for entry in BASELINE_MATRIX:
            payload = " ".join(
                (
                    entry.slug,
                    entry.route,
                    entry.state,
                    entry.data_fixture,
                    entry.notes,
                )
            ).lower()
            assert "martin_prod_smoke" not in payload, (
                f"Entry {entry.slug!r} references a prod account."
            )
            assert "spignos.com" not in payload, (
                f"Entry {entry.slug!r} references a prod URL."
            )
