#!/usr/bin/env python3
"""Sb_UI_11.2 — Visual baseline runtime preparation.

Intègre la capture baseline avec l'app runtime existant :

* lit `app.config.get_settings()` pour DATABASE_URL, app_env, app_secret_key ;
* refuse strictement `app_env=production` ;
* utilise `SessionLocal` (jamais une DB parallèle) ;
* crée ou réutilise un user baseline non-prod ;
* crée ou réutilise 1 session `in_progress` + 1 session `completed`
  via `app.services.session_builder.instantiate_session` ;
* génère un fichier Playwright `storage_state.json` avec un cookie
  `session_token` signé par `URLSafeTimedSerializer(app_secret_key)`
  (contrat identique à `app.services.auth._serializer`) ;
* écrit un fichier `runtime.json` non-secret décrivant les IDs et chemins.

Contrats de sécurité (hard) :

* Aucun password logué en clair.
* Aucun cookie value logué.
* Aucune commande n'accepte `--password` / `--token` / `--secret`.
* Le mot de passe fixture est généré aléatoirement à la volée si un
  nouveau user doit être créé — jamais lu depuis le shell.
* Le storage_state.json et runtime.json sont écrits sous
  `--out-dir` (défaut `var/visual-baseline/`), git-ignoré.
* Refus catégorique de tourner si `app_env == "production"` ou si la
  DB URL ressemble à une DB de production (heuristique).

Usage :

    python scripts/visual_baseline_runtime.py prepare \\
        --base-url http://127.0.0.1:8000 \\
        --out-dir var/visual-baseline

    python scripts/visual_baseline_runtime.py verify \\
        --runtime-file var/visual-baseline/runtime.json

Le mode `--dry-run` sur `prepare` fait tous les checks safety mais
n'écrit rien sur disque et ne touche pas la DB.
"""
from __future__ import annotations

import argparse
import json
import os
import secrets
import string
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

# Repo root on sys.path so we can `from app...` and `from scripts...`.
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))


BASELINE_USERNAME = "baseline_local"
DEFAULT_TEMPLATE_SLUG = "push-a"

# Random password strength for user creation (fixture only, never logged).
_PW_ALPHABET = string.ascii_letters + string.digits
_PW_LENGTH = 32


# ------- Safety checks -------------------------------------------------


def _refuse_production_env(settings) -> None:
    """Hard-refuse if the runtime env looks like production."""
    env = (getattr(settings, "app_env", "") or "").lower()
    if env == "production" or env == "prod":
        print(
            "ERROR: refusing to run baseline runtime against production env "
            f"(app_env={env!r}). Baseline runtime must run against a local "
            "or dev environment only.",
            file=sys.stderr,
        )
        raise SystemExit(11)


def _refuse_non_local_db(settings) -> None:
    """Refuse DB URLs that look like production endpoints."""
    url = getattr(settings, "database_url", "") or ""
    lowered = url.lower()

    # Allow-list : sqlite file, sqlite in-memory.
    if lowered.startswith("sqlite:///"):
        return
    if lowered == "sqlite://" or lowered.startswith("sqlite+"):
        return

    # Explicit local Postgres allowed (127.0.0.1 or localhost).
    if lowered.startswith("postgresql://") or lowered.startswith("postgres://"):
        if "127.0.0.1" in lowered or "localhost" in lowered:
            return

    print(
        "ERROR: refusing to run baseline runtime against a non-local database. "
        f"DATABASE_URL scheme/host not allow-listed (got prefix "
        f"{lowered.split('://', 1)[0]!r}). Local sqlite or local postgres only.",
        file=sys.stderr,
    )
    raise SystemExit(12)


def _short_db_signature(settings) -> str:
    """Return a short, non-secret hint about the DB (never the full URL if it
    contained credentials).

    For sqlite:///./var/workout.db → 'sqlite:./var/workout.db'.
    For postgres URLs → 'postgres://<host>' (never user/password).
    """
    url = getattr(settings, "database_url", "") or ""
    if url.startswith("sqlite:///"):
        return f"sqlite:{url.replace('sqlite:///', '', 1)}"
    if url.startswith("sqlite:"):
        return "sqlite:inline"
    # For postgres, strip credentials.
    if "://" in url:
        scheme, rest = url.split("://", 1)
        host_part = rest.split("@", 1)[-1].split("/", 1)[0]
        return f"{scheme}://{host_part}"
    return "unknown"


# ------- Fixture user + sessions --------------------------------------


def _generate_random_password() -> str:
    """Generate a strong fixture password. Never logged."""
    return "".join(secrets.choice(_PW_ALPHABET) for _ in range(_PW_LENGTH))


def _ensure_user(db, username: str) -> tuple[int, bool]:
    """Ensure a baseline user exists locally.

    Returns (user_id, created). Password is generated on the fly if the
    user doesn't exist. It is NEVER logged and NEVER returned.
    """
    from app.models.user import User  # local import to avoid app boot cost
    from app.services.auth import hash_password

    existing = db.execute(
        _select_one_by_username(User, username)
    ).scalar_one_or_none()
    if existing is not None:
        return int(existing.id), False

    pw = _generate_random_password()
    try:
        user = User(username=username, password_hash=hash_password(pw))
    finally:
        # Best-effort scrub. Python strings are immutable; we just drop the ref.
        del pw
    db.add(user)
    db.flush()
    return int(user.id), True


def _select_one_by_username(user_cls, username: str):
    from sqlalchemy import select

    return select(user_cls).where(user_cls.username == username).limit(1)


def _pick_template(db, preferred_slug: str = DEFAULT_TEMPLATE_SLUG):
    """Prefer `push-a`, else the first strength template available."""
    from sqlalchemy import select

    from app.models.catalog import WorkoutTemplate

    preferred = db.execute(
        select(WorkoutTemplate).where(WorkoutTemplate.slug == preferred_slug).limit(1)
    ).scalar_one_or_none()
    if preferred is not None:
        return preferred

    # Fallback: any template with kind starting with 'strength' or first row.
    any_tpl = db.execute(select(WorkoutTemplate).limit(1)).scalar_one_or_none()
    if any_tpl is None:
        print(
            "ERROR: no WorkoutTemplate in DB. Run seeding first (`app.seed`) "
            "or import the reference catalog.",
            file=sys.stderr,
        )
        raise SystemExit(13)
    return any_tpl


def _has_logged_work(db, session_id: int) -> bool:
    """True si une série de travail est déjà validée dans cette séance."""
    from sqlalchemy import select

    from app.models.session import SessionExercise, SetLog

    row = db.execute(
        select(SetLog.id)
        .join(SessionExercise, SetLog.session_exercise_id == SessionExercise.id)
        .where(SessionExercise.session_id == session_id)
        .where(SetLog.kind == "work")
        .where(SetLog.completed.is_(True))
        .limit(1)
    ).scalar_one_or_none()
    return row is not None


def _ensure_active_session(db, user_id: int) -> tuple[int, bool]:
    """Séance `in_progress` SANS aucune série de travail validée.

    Sb_UIV2_SESSION_FOCUS_02 — deux états authentiques valent mieux qu'un
    seul état impossible. `can_substitute()` renvoie False dès qu'une série
    de travail est validée : une séance déjà entamée ne peut donc PAS servir
    à photographier les alternatives. Cette séance-ci reste vierge et sert
    aux scénarios de substitution ; la séance `focus` porte l'état
    « série de travail courante ». On ne touche pas à `can_substitute()`.

    Returns (session_id, created).
    """
    from sqlalchemy import select

    from app.models.session import WorkoutSession

    candidates = db.execute(
        select(WorkoutSession)
        .where(WorkoutSession.user_id == user_id)
        .where(WorkoutSession.status == "in_progress")
        .order_by(WorkoutSession.id.asc())
    ).scalars().all()
    for candidate in candidates:
        if not _has_logged_work(db, int(candidate.id)):
            return int(candidate.id), False

    from app.services.session_builder import instantiate_session

    template = _pick_template(db)
    session = instantiate_session(
        db,
        template=template,
        started_at=datetime.now(timezone.utc),
        user_id=user_id,
    )
    db.add(session)
    db.flush()
    return int(session.id), True


def _advance_to_work_set(db, session_id: int, *, work_done: int = 1) -> int:
    """Amène la 1re carte d'exercice à « série de travail courante ».

    Sb_UIV2_SESSION_FOCUS_02 — une capture qui prétend montrer une **série de
    travail courante** alors que l'échauffement n'est pas fait photographie un
    état que le produit ne considère pas courant. Le fixture doit donc être
    cohérent avec ce que l'image affirme, sinon la preuve de hiérarchie porte
    sur un écran impossible.

    Marque donc l'échauffement comme fait, puis `work_done` série(s) de
    travail. La suivante devient la série courante, et celles d'après restent
    à venir — ce qui donne d'un seul état honnête « terminée / courante /
    à venir ».

    Écrit uniquement `completed`/`weight_kg`/`reps` sur des lignes **déjà
    créées** par le session builder : aucune sémantique métier n'est
    contournée, aucune ligne n'est inventée.
    """
    from sqlalchemy import select

    from app.models.session import SessionExercise, SetLog

    first = db.execute(
        select(SessionExercise)
        .where(SessionExercise.session_id == session_id)
        .order_by(SessionExercise.position.asc(), SessionExercise.id.asc())
        .limit(1)
    ).scalar_one_or_none()
    if first is None:
        return 0

    rows = db.execute(
        select(SetLog)
        .where(SetLog.session_exercise_id == first.id)
        .order_by(SetLog.kind.asc(), SetLog.set_index.asc())
    ).scalars().all()

    touched = 0
    work_marked = 0
    for row in rows:
        if row.kind == "warmup":
            row.completed = True
            row.weight_kg = row.weight_kg or 20.0
            row.reps = row.reps or 12
            touched += 1
        elif row.kind == "work" and work_marked < work_done:
            row.completed = True
            row.weight_kg = row.weight_kg or 40.0
            row.reps = row.reps or 10
            work_marked += 1
            touched += 1
    return touched


def _ensure_focus_session(db, user_id: int) -> tuple[int, bool]:
    """Séance `in_progress` AVEC échauffement fait et une série de travail.

    C'est l'état « série de travail courante » : la suivante est la série
    active, celles d'après sont à venir. Un seul état honnête couvre donc
    « terminée / courante / à venir » sans rien simuler.
    """
    from sqlalchemy import select

    from app.models.session import WorkoutSession

    candidates = db.execute(
        select(WorkoutSession)
        .where(WorkoutSession.user_id == user_id)
        .where(WorkoutSession.status == "in_progress")
        .order_by(WorkoutSession.id.asc())
    ).scalars().all()
    for candidate in candidates:
        if _has_logged_work(db, int(candidate.id)):
            return int(candidate.id), False

    from app.services.session_builder import instantiate_session

    template = _pick_template(db)
    session = instantiate_session(
        db,
        template=template,
        started_at=datetime.now(timezone.utc),
        user_id=user_id,
    )
    db.add(session)
    db.flush()
    _advance_to_work_set(db, int(session.id))
    return int(session.id), True


def _ensure_done_session(db, user_id: int) -> tuple[int, bool]:
    """Ensure the user has ≥ 1 session with status='completed'.

    If none exists, we instantiate a new session and flip its status to
    'completed' directly (no set logs; the goal is a captured static
    baseline of the done view, not a metric-valid session).
    """
    from sqlalchemy import select

    from app.models.session import WorkoutSession

    existing = db.execute(
        select(WorkoutSession)
        .where(WorkoutSession.user_id == user_id)
        .where(WorkoutSession.status == "completed")
        .order_by(WorkoutSession.id.desc())
        .limit(1)
    ).scalar_one_or_none()
    if existing is not None:
        return int(existing.id), False

    from app.services.session_builder import instantiate_session

    template = _pick_template(db)
    session = instantiate_session(
        db,
        template=template,
        started_at=datetime.now(timezone.utc),
        user_id=user_id,
    )
    session.status = "completed"
    db.add(session)
    db.flush()
    return int(session.id), True


# ------- Playwright storage_state --------------------------------------


def _signed_cookie_value(user_id: int, settings) -> str:
    """Produce a cookie value compatible with `app.services.auth`.

    We import the app's `_serializer` behavior — same secret, same
    serializer class — so the cookie will be accepted verbatim by
    `get_user_id_from_cookie`.

    NEVER log the return value.
    """
    from itsdangerous import URLSafeTimedSerializer

    ser = URLSafeTimedSerializer(settings.app_secret_key)
    return ser.dumps({"user_id": int(user_id)})


def _build_storage_state(base_url: str, cookie_value: str) -> dict:
    """Build the Playwright storage_state JSON structure.

    Cookie name `session_token` matches `app.services.auth.SESSION_COOKIE`.
    """
    from urllib.parse import urlparse

    host = urlparse(base_url).hostname or "127.0.0.1"

    # ~7 days from now, in POSIX seconds. Well within SESSION_MAX_AGE
    # (30 days) so the cookie will be accepted throughout the baseline
    # window.
    expires_ts = int(datetime.now(timezone.utc).timestamp()) + 7 * 86400

    return {
        "cookies": [
            {
                "name": "session_token",
                "value": cookie_value,
                "domain": host,
                "path": "/",
                "expires": expires_ts,
                "httpOnly": True,
                "secure": False,
                "sameSite": "Strict",
            }
        ],
        "origins": [],
    }


def _write_storage_state(
    out_dir: Path,
    user_id: int,
    base_url: str,
    settings,
) -> Path:
    """Write a Playwright-compatible storage_state.json for `user_id`.

    Path returned. Content NEVER printed.
    """
    cookie_value = _signed_cookie_value(user_id, settings)
    state = _build_storage_state(base_url, cookie_value)
    path = out_dir / "auth-state.json"
    out_dir.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2))
    try:
        path.chmod(0o600)
    except OSError:
        # Best-effort permissions; on some FS (Windows over network) chmod
        # is a no-op. Not fatal — file remains git-ignored.
        pass
    # scrub reference
    del cookie_value
    return path


# ------- Prepare / verify commands ------------------------------------


def _cmd_prepare(args: argparse.Namespace) -> int:
    from app.config import get_settings
    from app.database import SessionLocal, init_db

    settings = get_settings()
    _refuse_production_env(settings)
    _refuse_non_local_db(settings)

    print("Baseline runtime prepare")
    print(f"  base_url         : {args.base_url}")
    print(f"  app_env          : {settings.app_env}")
    print(f"  db               : {_short_db_signature(settings)}")
    print(f"  out_dir          : {args.out_dir}")

    if args.dry_run:
        print("\nDry-run: safety checks passed. No DB write, no state file.")
        return 0

    # Ensure schema exists (idempotent).
    init_db()

    with SessionLocal() as db:
        try:
            user_id, user_created = _ensure_user(db, BASELINE_USERNAME)
            active_id, active_created = _ensure_active_session(db, user_id)
            done_id, done_created = _ensure_done_session(db, user_id)
            focus_id, focus_created = _ensure_focus_session(db, user_id)
            db.commit()
        except Exception:
            db.rollback()
            raise

    out_dir = Path(args.out_dir)
    state_path = _write_storage_state(out_dir, user_id, args.base_url, settings)

    runtime_data = {
        "spec": "Sb_UI_11.2",
        "base_url": args.base_url,
        "user": {
            "username": BASELINE_USERNAME,
            "id": user_id,
            "created": user_created,
        },
        "sessions": {
            "active": {"id": active_id, "created": active_created},
            "done": {"id": done_id, "created": done_created},
            # État « série de travail courante ». Distinct de `active`, qui
            # reste vierge pour que la substitution existe réellement.
            "focus": {"id": focus_id, "created": focus_created},
        },
        "state_file": str(state_path),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    runtime_path = out_dir / "runtime.json"
    runtime_path.write_text(json.dumps(runtime_data, indent=2))
    try:
        runtime_path.chmod(0o600)
    except OSError:
        pass

    print("\nRuntime prepared (no secrets logged):")
    print(f"  user             : id={user_id} (created={user_created})")
    print(f"  active_session_id: {active_id} (created={active_created})")
    print(f"  focus_session_id : {focus_id} (created={focus_created}) "
          "— warm-ups done + 1 work set, current-set state")
    print(f"  done_session_id  : {done_id} (created={done_created})")
    print(f"  state_file       : {state_path}")
    print(f"  runtime_file     : {runtime_path}")
    print(
        "\nNext:\n"
        "  python scripts/visual_baseline_capture.py \\\n"
        f"      --base-url {args.base_url} \\\n"
        "      --priority P0 --viewport all \\\n"
        f"      --out-dir {args.out_dir} \\\n"
        f"      --runtime-file {runtime_path}"
    )
    return 0


def _cmd_verify(args: argparse.Namespace) -> int:
    runtime_path = Path(args.runtime_file)
    if not runtime_path.is_file():
        print(f"ERROR: runtime file not found: {runtime_path}", file=sys.stderr)
        return 14
    try:
        data = json.loads(runtime_path.read_text())
    except json.JSONDecodeError as exc:
        print(f"ERROR: runtime file is not valid JSON: {exc}", file=sys.stderr)
        return 15

    # Required keys.
    required = ("base_url", "user", "sessions", "state_file")
    missing = [k for k in required if k not in data]
    if missing:
        print(
            f"ERROR: runtime file missing required keys: {missing}",
            file=sys.stderr,
        )
        return 16

    # Security invariant: no secret-looking key.
    for banned in ("password", "cookie", "session_token", "secret", "token"):
        if banned in data:
            print(
                f"ERROR: runtime file contains banned key {banned!r} — "
                "this file must never carry secrets.",
                file=sys.stderr,
            )
            return 17

    # State file must exist locally.
    state_path = Path(data["state_file"])
    if not state_path.is_file():
        print(
            f"ERROR: state file referenced by runtime not found: {state_path}",
            file=sys.stderr,
        )
        return 18

    print("Runtime file verified (safe):")
    print(f"  base_url         : {data['base_url']}")
    print(f"  user_id          : {data['user']['id']}")
    print(f"  active_session_id: {data['sessions']['active']['id']}")
    print(f"  done_session_id  : {data['sessions']['done']['id']}")
    print(f"  state_file       : {state_path}")
    return 0


# ------- CLI ----------------------------------------------------------


# Substring tokens forbidden in CLI argument names (mirrors capture CLI).
_FORBIDDEN_ARG_SUBSTRINGS: tuple[str, ...] = (
    "password",
    "token",
    "secret",
    "basic-auth-password",
    "api-key",
    "apikey",
    "cookie",
)


def _reject_secret_args(argv: Sequence[str]) -> None:
    for arg in argv:
        flag = arg.split("=", 1)[0].lower().lstrip("-")
        for forbidden in _FORBIDDEN_ARG_SUBSTRINGS:
            if forbidden in flag:
                print(
                    "ERROR: refusing CLI argument with forbidden name segment "
                    f"'{forbidden}'. Credentials/state must never pass via CLI. "
                    "See docs/strategy/Sx_UI_11_SCREENSHOT_REGRESSION_BASELINE_SPEC.md §6.",
                    file=sys.stderr,
                )
                raise SystemExit(2)


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    _reject_secret_args(argv)
    parser = argparse.ArgumentParser(
        description=(
            "Sb_UI_11.2 — Visual baseline runtime preparation "
            "(local app fixtures + Playwright storage_state)."
        ),
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    prep = sub.add_parser("prepare", help="Create/reuse fixtures and write runtime.json.")
    prep.add_argument(
        "--base-url",
        default="http://127.0.0.1:8000",
        help="Local app base URL (default: http://127.0.0.1:8000).",
    )
    prep.add_argument(
        "--out-dir",
        default="var/visual-baseline",
        help="Output directory (default: var/visual-baseline).",
    )
    prep.add_argument(
        "--dry-run",
        action="store_true",
        help="Run safety checks only; no DB write, no state file.",
    )
    prep.set_defaults(func=_cmd_prepare)

    verify = sub.add_parser("verify", help="Verify an existing runtime.json (no writes).")
    verify.add_argument(
        "--runtime-file",
        default="var/visual-baseline/runtime.json",
        help="Path to runtime.json (default: var/visual-baseline/runtime.json).",
    )
    verify.set_defaults(func=_cmd_verify)

    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
