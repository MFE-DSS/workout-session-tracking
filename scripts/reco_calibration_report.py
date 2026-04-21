"""Recommendation calibration report — Sb_13.

Reads the last N days of completed WorkoutSession rows and produces a
short textual report with:

  1. reco_acceptance_rate   — share of sessions started via the reco top CTA
  2. alt_click_rate         — share started via a reco alternative
  3. bypass_rate            — share started via launcher / library
  4. phrase_repetition_rate — counts of the most recurrent top-phrases
                              (re-computed against the engine at the time
                              of each reco_top session)

Run offline, stdout only. Usage::

    python scripts/reco_calibration_report.py               # default 7j
    python scripts/reco_calibration_report.py --days 14     # wider window

Exit code: 0 always — the script is observational, not pass/fail.
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import select

from app.database import SessionLocal
from app.models.session import WorkoutSession
from app.services.recommendation import (  # noqa: E402
    recommend_next_session,
    reset_template_zones_cache,
)


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Recommendation calibration report")
    p.add_argument(
        "--days", type=int, default=7,
        help="Window in days (default 7)",
    )
    p.add_argument(
        "--user-id", type=int, default=None,
        help="Restrict to a single user_id (default: all)",
    )
    p.add_argument(
        "--phrase-top", type=int, default=10,
        help="How many recent reco_top phrases to sample (default 10)",
    )
    return p.parse_args()


def _rate(numerator: int, denom: int) -> str:
    if denom == 0:
        return "n/a"
    pct = numerator / denom * 100
    return f"{pct:.1f}%"


def _sessions_in_window(days: int, user_id: int | None):
    window_start = datetime.now(timezone.utc) - timedelta(days=days)
    with SessionLocal() as db:
        stmt = (
            select(WorkoutSession)
            .where(
                WorkoutSession.status == "completed",
                WorkoutSession.excluded_from_stats.is_(False),
                WorkoutSession.started_at >= window_start,
            )
            .order_by(WorkoutSession.started_at.asc())
        )
        if user_id is not None:
            stmt = stmt.where(WorkoutSession.user_id == user_id)
        return list(db.execute(stmt).scalars().all())


def _sample_top_phrases(
    user_id: int, reco_top_sessions: list[WorkoutSession], limit: int
) -> list[tuple[str, int]]:
    """Re-invoke the engine at the time of each recent reco_top session
    to approximate the phrase that was served."""
    reset_template_zones_cache()
    phrases: list[str] = []
    with SessionLocal() as db:
        for s in reco_top_sessions[-limit:]:
            started = s.started_at
            if started and started.tzinfo is None:
                started = started.replace(tzinfo=timezone.utc)
            result = recommend_next_session(
                db, s.user_id, now=started or datetime.now(timezone.utc)
            )
            if result and result.get("top"):
                phrases.append(result["top"]["phrase"])
    return Counter(phrases).most_common()


def main() -> int:
    args = _parse_args()
    sessions = _sessions_in_window(args.days, args.user_id)
    total = len(sessions)

    by_source = Counter(s.creation_source for s in sessions)
    reco_top = by_source.get("reco_top", 0)
    reco_alt = by_source.get("reco_alt", 0)
    launcher = by_source.get("launcher", 0)
    library = by_source.get("library", 0)
    replay = by_source.get("replay", 0)
    unknown = by_source.get(None, 0) + by_source.get("", 0)

    bypass = launcher + library
    known = total - unknown

    print("SPIGNOS — Reco calibration report")
    print("=" * 48)
    print(f"Window                : {args.days} day(s)")
    if args.user_id is not None:
        print(f"User filter           : user_id={args.user_id}")
    print(f"Sessions (window)     : {total}")
    print(f"  with known source   : {known}")
    print(f"  with unknown source : {unknown}  (pre-Sb_13 or invalid)")
    print()
    print("Creation source breakdown")
    print("-" * 48)
    print(f"  reco_top  : {reco_top:>4}  ({_rate(reco_top, known)} of known)")
    print(f"  reco_alt  : {reco_alt:>4}  ({_rate(reco_alt, known)} of known)")
    print(f"  launcher  : {launcher:>4}  ({_rate(launcher, known)} of known)")
    print(f"  library   : {library:>4}  ({_rate(library, known)} of known)")
    if replay:
        print(f"  replay    : {replay:>4}  ({_rate(replay, known)} of known)")
    print()
    print("Key indicators (vs known-source sessions)")
    print("-" * 48)
    print(f"  reco_acceptance_rate : {_rate(reco_top, known)}  (target > 40%)")
    print(f"  alt_click_rate       : {_rate(reco_alt, known)}  (target 10-25%)")
    print(f"  bypass_rate          : {_rate(bypass, known)}  (target < 30%)")
    print()

    # Top phrases — restricted to the single user filter, otherwise the
    # phrase makes no sense (it depends on one user's history).
    if args.user_id is not None:
        top_sessions = [
            s for s in sessions if s.creation_source == "reco_top"
        ]
        top_phrases = _sample_top_phrases(
            args.user_id, top_sessions, args.phrase_top,
        )
        print(f"Top phrases (last {min(args.phrase_top, len(top_sessions))} reco_top)")
        print("-" * 48)
        if not top_phrases:
            print("  (no reco_top sessions in window)")
        else:
            for phrase, count in top_phrases:
                marker = " ⚠" if count >= 3 else ""
                print(f"  [{count}x{marker}] {phrase}")
            repetitive = sum(1 for _, c in top_phrases if c >= 3)
            print(f"\n  phrase_repetition_rate: {repetitive} distinct phrase(s) >= 3 occurrences")
            print(f"  (target <= 3 repetitions for any given phrase)")
    else:
        print("Top phrases sampling skipped (requires --user-id to be meaningful)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
