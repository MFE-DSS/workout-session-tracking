#!/usr/bin/env python3
"""Sb_UI_11.1 — Visual baseline capture CLI (Playwright).

Capture des screenshots baseline pré-Auren, alignés avec la matrice
`scripts/visual_baseline_matrix.py` et la spec
`docs/strategy/Sx_UI_11_SCREENSHOT_REGRESSION_BASELINE_SPEC.md`.

Contrats (hard) :
* Aucun argument CLI ne peut recevoir un mot de passe, token ou secret.
  Les valeurs sont lues uniquement depuis les variables d'environnement
  `AUREN_BASELINE_*` — jamais loggées, jamais affichées.
* Le CLI en `--dry-run` n'importe pas Playwright et ne fait aucun réseau.
* Aucun compte prod n'est utilisé.
* Aucun PNG n'est commit — voir `.gitignore` sur `var/visual-baseline/`.

Usage :
    # Dry-run (recommandé pour vérifier la matrice, sans navigateur)
    python scripts/visual_baseline_capture.py --dry-run --priority P0

    # Capture réelle locale (requiert `python -m playwright install chromium`)
    python scripts/visual_baseline_capture.py \\
        --base-url http://127.0.0.1:8000 \\
        --priority P0 \\
        --viewport all \\
        --out-dir var/visual-baseline

    # Strict mode : fail si env vars requises manquent
    python scripts/visual_baseline_capture.py --dry-run --priority P0 --strict-p0

Prérequis navigateur (à exécuter localement, jamais en CI V1) :
    python -m playwright install chromium
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Sequence
from pathlib import Path

# Add repo root to sys.path so we can import scripts.visual_baseline_matrix.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.visual_baseline_matrix import (  # noqa: E402
    OPTIONAL_ENV_VARS,
    REQUIRED_ENV_VARS_FOR_ACTIVE_SESSION,
    REQUIRED_ENV_VARS_FOR_AUTH,
    REQUIRED_ENV_VARS_FOR_DONE_SESSION,
    CapturePlan,
    build_plan,
    entries_for_priority,
)

# Substring tokens forbidden in CLI argument names (hard anti-secret rule).
_FORBIDDEN_ARG_SUBSTRINGS: tuple[str, ...] = (
    "password",
    "token",
    "secret",
    "basic-auth-password",
    "api-key",
    "apikey",
)


def _reject_secret_args(argv: Sequence[str]) -> None:
    """Refuse hard tout argument nommé contenant password/token/secret.

    Levée avant argparse pour empêcher tout `--password=xxx` d'atteindre
    les logs argparse. Le message d'erreur ne contient JAMAIS de valeur.
    """
    for arg in argv:
        # Match on the flag name only, up to '='.
        flag = arg.split("=", 1)[0].lower().lstrip("-")
        for forbidden in _FORBIDDEN_ARG_SUBSTRINGS:
            if forbidden in flag:
                # Ne pas logger la valeur, jamais.
                print(
                    "ERROR: refusing CLI argument with forbidden name segment "
                    f"'{forbidden}'. Credentials must be passed via "
                    "AUREN_BASELINE_* environment variables. "
                    "See docs/strategy/Sx_UI_11_SCREENSHOT_REGRESSION_BASELINE_SPEC.md §6.",
                    file=sys.stderr,
                )
                raise SystemExit(2)


def _env_status(name: str) -> str:
    """Retourne 'set' ou 'missing' — jamais la valeur."""
    value = os.environ.get(name, "")
    return "set" if value else "missing"


def _print_env_status(strict_p0: bool) -> bool:
    """Affiche l'état des variables d'environnement critiques (set|missing).

    Ne logge jamais les valeurs. Retourne True si toutes les vars requises
    par le mode strict sont set.
    """
    all_required = REQUIRED_ENV_VARS_FOR_AUTH + REQUIRED_ENV_VARS_FOR_ACTIVE_SESSION + REQUIRED_ENV_VARS_FOR_DONE_SESSION
    print("Environment status (values redacted):")
    all_set = True
    for name in all_required:
        status = _env_status(name)
        print(f"  {name}=<{status}>")
        if strict_p0 and status == "missing":
            all_set = False
    for name in OPTIONAL_ENV_VARS:
        status = _env_status(name)
        print(f"  {name}=<{status}> (optional)")
    return all_set


def _load_runtime_file(path: str | None) -> dict | None:
    """Load runtime.json produced by scripts/visual_baseline_runtime.py.

    Returns None if `path` is falsy. Raises SystemExit(5) with a clear
    error if the file is missing or unreadable. The runtime file must
    NEVER contain credentials — we assert that here as a defense-in-depth.
    """
    if not path:
        return None
    p = Path(path)
    if not p.is_file():
        print(
            f"ERROR: --runtime-file not found: {p}. Run "
            "`python scripts/visual_baseline_runtime.py prepare` first.",
            file=sys.stderr,
        )
        raise SystemExit(5)
    try:
        data = json.loads(p.read_text())
    except json.JSONDecodeError as exc:
        print(f"ERROR: --runtime-file is not valid JSON: {exc}", file=sys.stderr)
        raise SystemExit(6) from exc
    for banned in ("password", "cookie", "session_token", "secret", "token"):
        if banned in data:
            print(
                f"ERROR: --runtime-file contains banned key {banned!r} — "
                "this file must never carry secrets.",
                file=sys.stderr,
            )
            raise SystemExit(7)
    return data


def _resolve_route(
    route_template: str, runtime: dict | None = None
) -> str:
    """Remplace les placeholders `${AUREN_BASELINE_*}` par leur valeur.

    Résolution :
    1. Si un `runtime` est fourni, ses IDs `sessions.active.id` et
       `sessions.done.id` sont utilisés en priorité.
    2. Sinon fallback sur les variables d'environnement `AUREN_BASELINE_*`
       (compatibilité Sb_UI_11.1).

    Les valeurs ne sont jamais loggées.
    """
    resolved = route_template

    # Runtime file has priority (Sb_UI_11.2).
    if runtime is not None:
        sessions = runtime.get("sessions", {})
        runtime_map = {
            "AUREN_BASELINE_ACTIVE_SESSION_ID": (
                sessions.get("active", {}).get("id")
            ),
            "AUREN_BASELINE_DONE_SESSION_ID": (
                sessions.get("done", {}).get("id")
            ),
        }
        for name, value in runtime_map.items():
            placeholder = f"${{{name}}}"
            if placeholder in resolved and value is not None:
                resolved = resolved.replace(placeholder, str(value))

    # Env-var fallback (Sb_UI_11.1 compat).
    for name in (
        *REQUIRED_ENV_VARS_FOR_ACTIVE_SESSION,
        *REQUIRED_ENV_VARS_FOR_DONE_SESSION,
        *OPTIONAL_ENV_VARS,
    ):
        placeholder = f"${{{name}}}"
        if placeholder in resolved:
            value = os.environ.get(name, "")
            if value:
                resolved = resolved.replace(placeholder, value)
    return resolved


def _resolve_state_file(
    cli_state_file: str | None, runtime: dict | None
) -> str | None:
    """Prefer explicit --state-file. Fallback to runtime.state_file."""
    if cli_state_file:
        return cli_state_file
    if runtime is not None:
        val = runtime.get("state_file")
        if val:
            return str(val)
    return None


def _plan_summary(plan: CapturePlan, runtime: dict | None = None) -> str:
    """Résumé texte pour dry-run — jamais de secret ni valeur env."""
    entry = plan.entry
    resolved = _resolve_route(entry.route, runtime=runtime)
    return (
        f"  [{entry.priority}] {entry.slug}/{plan.viewport} "
        f"({plan.width}×{plan.height}) → {plan.output_path} "
        f"| auth={entry.auth_required} | fixture={entry.data_fixture} "
        f"| route={resolved}"
    )


def _dry_run(plans: list[CapturePlan], runtime: dict | None = None) -> int:
    """Liste les captures sans lancer de navigateur ni écrire aucun fichier."""
    print(f"Dry-run: {len(plans)} capture(s) planned.")
    if runtime is not None:
        print("Runtime source: runtime.json")
    for plan in plans:
        print(_plan_summary(plan, runtime=runtime))
    return 0


def apply_actions(page, entry, *, timeout: int = 5000) -> None:
    """Rejoue les gestes du scénario, puis vérifie l'état attendu.

    Sb_UIV2_STATEFUL_VISUAL_HARNESS_01 — chaque geste passe par l'API Playwright
    correspondante, jamais par une évaluation JavaScript : une capture doit
    montrer un état que l'utilisateur peut réellement atteindre.

    `expect_visible` n'est pas décoratif. Sans lui, un sélecteur devenu obsolète
    ferait échouer silencieusement un geste et la capture montrerait l'écran
    fermé en le faisant passer pour l'écran ouvert — exactement le genre de
    preuve vide que ce harnais existe pour empêcher.
    """
    for action in getattr(entry, "actions", ()):
        if action.kind == "wait_for":
            page.wait_for_selector(action.selector, timeout=timeout)
        elif action.kind == "click":
            page.click(action.selector, timeout=timeout)
        elif action.kind == "check":
            page.check(action.selector, timeout=timeout)
        elif action.kind == "open_details":
            # Cliquer le <summary> : c'est le geste réel, et il exerce la
            # sémantique native au lieu de forcer l'attribut `open`.
            page.click(f"{action.selector} > summary", timeout=timeout)
        elif action.kind == "press":
            page.keyboard.press(action.key)
        else:  # pragma: no cover - `Action` valide déjà le vocabulaire
            raise ValueError(f"unhandled action kind: {action.kind}")

    expected = getattr(entry, "expect_visible", "")
    if expected:
        page.wait_for_selector(expected, state="visible", timeout=timeout)


def _capture_real(
    plans: list[CapturePlan],
    base_url: str,
    state_file: str | None,
    runtime: dict | None = None,
) -> int:
    """Lance Playwright et capture les screenshots.

    Import Playwright uniquement ici — jamais au chargement du module.

    Auth : `state_file` (Playwright storage_state) est utilisé pour les
    entrées `auth_required=True`. Les entrées anonymes (`login`,
    `register`) sont capturées SANS state_file pour capturer le vrai
    empty state public.
    """
    try:
        from playwright.sync_api import sync_playwright  # type: ignore[import-not-found]
    except ImportError:
        print(
            "ERROR: playwright not installed. Run `pip install -e '.[baseline]'` "
            "and `python -m playwright install chromium`.",
            file=sys.stderr,
        )
        return 3

    print(f"Capturing {len(plans)} screenshot(s) against {base_url} ...")
    if runtime is not None:
        print("Runtime source: runtime.json")
    ok = 0
    failed = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            for plan in plans:
                context_kwargs: dict[str, object] = {
                    "viewport": {"width": plan.width, "height": plan.height},
                }
                # Auth state only for authenticated entries.
                if plan.entry.auth_required and state_file:
                    context_kwargs["storage_state"] = state_file
                context = browser.new_context(**context_kwargs)
                page = context.new_page()
                try:
                    route = _resolve_route(plan.entry.route, runtime=runtime)
                    url = base_url.rstrip("/") + route
                    page.goto(url, wait_until="networkidle", timeout=15000)
                    apply_actions(page, plan.entry)
                    output_dir = Path(plan.output_path).parent
                    output_dir.mkdir(parents=True, exist_ok=True)
                    page.screenshot(path=plan.output_path, full_page=True)
                    print(f"  ✓ {plan.entry.slug}/{plan.viewport}")
                    ok += 1
                except Exception as exc:  # noqa: BLE001 — CLI wants to keep going
                    # Do NOT include env values in errors.
                    print(
                        f"  ✗ {plan.entry.slug}/{plan.viewport}: "
                        f"{type(exc).__name__}",
                        file=sys.stderr,
                    )
                    failed += 1
                finally:
                    context.close()
        finally:
            browser.close()
    print(f"Done. ok={ok} failed={failed}")
    return 0 if failed == 0 else 1


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    """Parse arguments. Never accepts credentials in flags."""
    _reject_secret_args(argv)
    parser = argparse.ArgumentParser(
        description="Sb_UI_11.1 — Visual baseline screenshot capture (Playwright).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List captures without opening a browser or writing PNGs.",
    )
    parser.add_argument(
        "--priority",
        choices=("P0", "P1", "P2", "all"),
        default="P0",
        help="Which priority tier to capture (default: P0).",
    )
    parser.add_argument(
        "--viewport",
        choices=("mobile", "desktop", "all"),
        default="all",
        help="Which viewport(s) to capture (default: all).",
    )
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8000",
        help="Base URL for the app under test (default: http://127.0.0.1:8000).",
    )
    parser.add_argument(
        "--out-dir",
        default="var/visual-baseline",
        help="Output directory for PNGs (default: var/visual-baseline).",
    )
    parser.add_argument(
        "--state-file",
        default=None,
        help="Optional Playwright storage_state JSON path (auth cookies). "
        "Never contains raw password. See Sx_UI_11 §6. "
        "If omitted, --runtime-file's state_file is used.",
    )
    parser.add_argument(
        "--runtime-file",
        default=None,
        help="Path to runtime.json produced by "
        "scripts/visual_baseline_runtime.py. Resolves session IDs and "
        "state_file. Preferred over env vars (Sb_UI_11.2).",
    )
    parser.add_argument(
        "--strict-p0",
        action="store_true",
        help="Fail if required env vars for session active/done are missing. "
        "Ignored when --runtime-file is provided (runtime file supplies "
        "the IDs).",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])

    runtime = _load_runtime_file(args.runtime_file)

    # env status is still printed for transparency, but strict_p0 is
    # relaxed when runtime supplies the IDs.
    all_env_ok = _print_env_status(strict_p0=args.strict_p0)
    if args.strict_p0 and runtime is None and not all_env_ok:
        print(
            "\nERROR: --strict-p0 requires either --runtime-file "
            "or all AUREN_BASELINE_* env vars to be set.",
            file=sys.stderr,
        )
        return 4

    entries = entries_for_priority(args.priority)
    plans = build_plan(entries, args.viewport, args.out_dir)

    if not plans:
        print(
            f"WARNING: no plans generated for priority={args.priority}, "
            f"viewport={args.viewport}.",
            file=sys.stderr,
        )
        return 0

    if args.dry_run:
        return _dry_run(plans, runtime=runtime)

    state_file = _resolve_state_file(args.state_file, runtime)
    return _capture_real(
        plans,
        base_url=args.base_url,
        state_file=state_file,
        runtime=runtime,
    )


if __name__ == "__main__":
    raise SystemExit(main())
