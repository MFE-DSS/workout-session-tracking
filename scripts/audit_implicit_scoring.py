#!/usr/bin/env python3
"""Sb_24.8 — audit empirique V1 vs V2 sur la BD locale ou prod.

Usage :
    sudo -u ubuntu /opt/workout-session-tracking/.venv/bin/python3 \\
        -m scripts.audit_implicit_scoring [--days 30] [--user-id N]

Sort un récapitulatif :
- Nombre de sessions par scoring_version
- Distribution des implicit_label par fréquence
- Pour chaque session V2 avec labels : delta V2 - V1 (donne la magnitude
  d'effet de la formule V2)
- Verdict : la formule semble-t-elle cohérente ou faut-il ajuster
  w_implicit ?

Le script est read-only — aucune écriture en BD.
"""
from __future__ import annotations

import argparse
import statistics
from collections import Counter
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import SessionLocal
from app.models.session import SessionExercise, WorkoutSession
from app.services.implicit_signal import LABEL_SCORE_CONTRIBUTION, ImplicitLabel
from app.services.quality_score import (
    W_IMPLICIT,
    W_V1,
    _implicit_signal_avg,
    compute_session_quality,
    compute_session_quality_strength,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--user-id", type=int, default=None)
    args = parser.parse_args()

    window_start = datetime.now(timezone.utc) - timedelta(days=args.days)

    with SessionLocal() as db:
        stmt = (
            select(WorkoutSession)
            .where(
                WorkoutSession.status == "completed",
                WorkoutSession.started_at >= window_start,
            )
            .options(
                selectinload(WorkoutSession.session_exercises)
                .selectinload(SessionExercise.set_logs),
                selectinload(WorkoutSession.template),
            )
            .order_by(WorkoutSession.started_at.desc())
        )
        if args.user_id is not None:
            stmt = stmt.where(WorkoutSession.user_id == args.user_id)
        sessions = db.execute(stmt).scalars().all()

        print(f"=== Audit Sb_24.8 — fenêtre {args.days}j, "
              f"{len(sessions)} sessions completed ===")

        # 1. scoring_version distribution
        sv_counter: Counter[int] = Counter(s.scoring_version for s in sessions)
        print("\n--- scoring_version ---")
        for sv, n in sorted(sv_counter.items()):
            print(f"  v{sv}: {n} sessions")

        # 2. label distribution across labeled exercises
        all_labels: list[str] = []
        for s in sessions:
            for se in s.session_exercises:
                if se.implicit_label:
                    all_labels.append(se.implicit_label)
        label_counter: Counter[str] = Counter(all_labels)
        print(f"\n--- Labels implicites (total {len(all_labels)} exos) ---")
        for label, n in label_counter.most_common():
            pct = round(100 * n / len(all_labels)) if all_labels else 0
            print(f"  {label:30} {n:4d}  ({pct}%)")

        # 3. delta V2 - V1 per session with labels (strength only)
        deltas: list[int] = []
        examples: list[str] = []
        for s in sessions:
            try:
                kind = s.template.kind if s.template else None
            except Exception:
                kind = None
            if kind == "cardio":
                continue
            avg = _implicit_signal_avg(s)
            if avg is None:
                continue
            v1 = compute_session_quality_strength(s)
            v2 = compute_session_quality(s)
            delta = v2 - v1
            deltas.append(delta)
            if len(examples) < 5:
                examples.append(
                    f"  session #{s.id} {s.template_name_snapshot[:25]:25} "
                    f"V1={v1} avg={avg:.1f} V2={v2} delta={delta:+d}"
                )

        print(f"\n--- Delta V2 - V1 (sessions strength avec labels, "
              f"n={len(deltas)}) ---")
        if deltas:
            print(f"  min   : {min(deltas):+d}")
            print(f"  median: {round(statistics.median(deltas)):+d}")
            print(f"  mean  : {statistics.mean(deltas):+.1f}")
            print(f"  max   : {max(deltas):+d}")
            print(f"  stdev : {statistics.stdev(deltas):.1f}" if len(deltas) >= 2 else "")
            print("\n  Exemples :")
            for ex in examples:
                print(ex)
        else:
            print("  Pas de session strength labellée dans la fenêtre.")

        # 4. Verdict
        print("\n--- Verdict ---")
        if not deltas:
            print("  Pas de signal — attendre quelques séances réelles.")
        else:
            mean_delta = statistics.mean(deltas)
            if abs(mean_delta) < 3:
                print(f"  Pondération w_implicit={W_IMPLICIT} équilibrée "
                      f"(mean delta {mean_delta:+.1f}).")
            elif mean_delta > 6:
                print(f"  Mean delta {mean_delta:+.1f} > 6 — V2 boost trop "
                      f"généreux. Envisager w_implicit plus bas (~0.20).")
            elif mean_delta < -6:
                print(f"  Mean delta {mean_delta:+.1f} < -6 — V2 pénalise "
                      f"trop. Envisager w_implicit plus bas (~0.20) ou "
                      f"revoir les contributions par label.")
            else:
                print(f"  Pondération acceptable (mean delta {mean_delta:+.1f}).")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
