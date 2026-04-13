"""Sprint 5 CSV export + export landing page."""
from __future__ import annotations

import csv
import io
import re


# ---------------------------------------------------------------------------
# /export landing page
# ---------------------------------------------------------------------------


def test_export_landing_page_renders_with_zero_sessions(client):
    r = client.get("/export")
    assert r.status_code == 200
    body = r.text
    assert "Export" in body
    assert "Sessions totales" in body
    # 0 totals + dash for first/last
    assert ">0<" in body
    # Both download buttons must be present
    assert "Télécharger JSON" in body
    assert "Télécharger CSV" in body


def test_export_landing_page_renders_summary_after_sessions(client):
    r = client.post(
        "/sessions", data={"template_slug": "push-a"}, follow_redirects=False
    )
    sid = int(re.match(r"/sessions/(\d+)", r.headers["location"]).group(1))
    client.post(f"/sessions/{sid}", data={"action": "end"}, follow_redirects=False)

    body = client.get("/export").text
    # totals should now show >=1 session
    assert "Sessions totales" in body
    assert "Sessions terminées" in body
    # Schema version must be visible (it's frozen at 1)
    assert "Schema version" in body


# ---------------------------------------------------------------------------
# CSV export
# ---------------------------------------------------------------------------


def test_csv_export_returns_csv_with_headers_and_no_rows_when_empty(client):
    r = client.get("/export/sessions.csv")
    assert r.status_code == 200
    assert "text/csv" in r.headers["content-type"]
    assert "attachment" in r.headers["content-disposition"]
    body = r.text
    reader = list(csv.reader(io.StringIO(body)))
    assert reader[0][0] == "session_id"
    assert "weight_kg" in reader[0]
    assert "set_kind" in reader[0]
    assert "completed" in reader[0]
    # No data rows
    assert len(reader) == 1


def test_csv_export_attachment_filename_uses_timestamp(client):
    r = client.get("/export/sessions.csv")
    cd = r.headers["content-disposition"]
    assert re.search(r'workout-export-\d{8}_\d{4}\.csv', cd)


def test_csv_export_emits_one_row_per_set_for_filled_session(client):
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.session import SessionExercise, SetLog

    r = client.post(
        "/sessions", data={"template_slug": "push-a"}, follow_redirects=False
    )
    sid = int(re.match(r"/sessions/(\d+)", r.headers["location"]).group(1))

    with SessionLocal() as db:
        se = db.execute(
            select(SessionExercise)
            .where(SessionExercise.session_id == sid)
            .where(SessionExercise.exercise_code_snapshot == "E2")
        ).scalar_one()
        se_id = se.id
        work_ids = sorted(
            s.id for s in db.execute(
                select(SetLog).where(SetLog.session_exercise_id == se_id)
            ).scalars().all()
            if s.kind == "work"
        )

    data = {"muscle_sensation": "strong"}
    for i, wid in enumerate(work_ids, start=1):
        data[f"set_{wid}_weight_kg"] = str(60 + i)
        data[f"set_{wid}_reps"] = "10"
        data[f"set_{wid}_completed"] = "1"
    client.post(f"/sessions/{sid}/exercises/{se_id}", data=data, follow_redirects=False)
    client.post(
        f"/sessions/{sid}",
        data={
            "concentration": "high",
            "global_state": "good",
            "bodyweight_kg": "78.5",
            "action": "end",
        },
        follow_redirects=False,
    )

    body = client.get("/export/sessions.csv").text
    rows = list(csv.DictReader(io.StringIO(body)))
    # Push A has 8 exercises x (2 warmup + N work). Total varies but
    # should be exactly the count of set_logs of the session.
    assert len(rows) > 0
    # All rows reference the same session
    sids_in_csv = {int(r["session_id"]) for r in rows}
    assert sids_in_csv == {sid}
    # Session-level columns are denormalised onto every row
    for r in rows:
        assert r["template_slug"] == "push-a"
        assert r["template_name"].startswith("Push A")
        assert r["status"] == "completed"
        assert r["concentration"] == "high"
        assert r["global_state"] == "good"
        assert r["bodyweight_kg"] == "78.5"
    # E2 has 3 work rows that we filled in
    e2_work_rows = [
        r for r in rows
        if r["exercise_code"] == "E2" and r["set_kind"] == "work"
    ]
    assert len(e2_work_rows) == 3
    for w in e2_work_rows:
        assert w["completed"] == "1"
        assert w["execution_quality"] == ""  # no longer sent via form
        assert w["reps_target"] == ""  # no longer sent via form
        assert w["reps"] == "10"


def test_csv_export_emits_rows_for_cardio_session(client):
    """liss-abs is a cardio+core template with exercises. Verify
    that the CSV contains rows for this session."""
    r = client.post(
        "/sessions", data={"template_slug": "liss-abs"}, follow_redirects=False
    )
    sid = int(re.match(r"/sessions/(\d+)", r.headers["location"]).group(1))
    body = client.get("/export/sessions.csv").text
    rows = list(csv.DictReader(io.StringIO(body)))
    cardio_rows = [r for r in rows if int(r["session_id"]) == sid]
    assert len(cardio_rows) > 0
    assert cardio_rows[0]["template_slug"] == "liss-abs"
