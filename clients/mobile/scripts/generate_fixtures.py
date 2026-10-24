"""Sb_VNEXT_NATIVE_N0 — fixtures du labo natif, produites par les services canoniques.

Aucune valeur n'est écrite à la main : le script sème un historique sur une base
SQLite JETABLE, demande à la recommandation servie (V3 + mémoire) ce qu'elle
propose, démarre chaque séance proposable par la vraie route `POST /sessions`,
puis sérialise ce que les services existants rendent. La base de production
n'est jamais ouverte.

Le format est un BROUILLON des read models de
`Sx_AUREN_MOBILE_EXPERIENCE_VNEXT §8` (mission, plan de séance avec table de
transitions, relevé). Il sera remplacé par les schémas réels de la tranche L1.

Usage (depuis n'importe quel répertoire) :
    python clients/mobile/scripts/generate_fixtures.py
"""
from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path

MOBILE = Path(__file__).resolve().parent.parent
ROOT = MOBILE.parent.parent
OUT = MOBILE / "src" / "fixtures" / "lab_fixture.json"

os.chdir(ROOT)
sys.path.insert(0, str(ROOT))
os.environ["DATABASE_URL"] = f"sqlite:///{Path(tempfile.mkdtemp()) / 'n0-lab.db'}"
os.environ["APP_ENV"] = "test"
os.environ["APP_SECRET_KEY"] = "n0-fixture-generator"  # noqa: S105
os.environ["RATE_LIMIT_ENABLED"] = "0"

import app  # noqa: E402

if not Path(app.__file__).resolve().is_relative_to(ROOT):
    raise SystemExit(f"app resolved to {app.__file__}, not {ROOT} — wrong tree")

import httpx  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import select  # noqa: E402
from starlette.responses import Response  # noqa: E402

from app import main as main_mod  # noqa: E402
from app.database import SessionLocal  # noqa: E402
from app.models.session import SessionExercise, SetLog, WorkoutSession  # noqa: E402
from app.models.user import User  # noqa: E402
from app.services import advice_memory  # noqa: E402
from app.services.auth import create_session_cookie  # noqa: E402
from app.services.console_state import REST_FALLBACK_SECONDS  # noqa: E402
from app.services.muscle_mapping import classify_exercise  # noqa: E402
from app.services.overload_engine import compute_overload_hint  # noqa: E402
from app.services.overload_explainer import explain_overload_hint  # noqa: E402
from app.services.overload_inputs import build_overload_input_for_exercise  # noqa: E402
from app.services.recommendation_explainer import explain_recommendation  # noqa: E402
from app.services.recommendation_v3 import classer_candidats, famille_de  # noqa: E402
from app.services.session_recap import _ZONE_LABELS, build_recap  # noqa: E402
from app.services.stats import last_time_by_exercise_code  # noqa: E402
from app.services.substitution import actual_exercise_name, compute_suggestions  # noqa: E402

#: Historique semé : ce qu'un pratiquant réel aurait fait sur deux semaines.
#: `(gabarit, semaine)` — `None` = LISS, qui porte de vraies données cardio.
HISTORY = [
    ("push-a", 0), ("pull-a", 0), ("liss-only", None), ("legs-a", 0),
    ("push-a", 1), ("pull-b", 1), ("liss-abs", None), ("legs-b", 1),
]

#: Charges de départ saisies par le pratiquant semé (DONNÉES D'UTILISATEUR, pas
#: des sorties du moteur), par mot-clé du nom d'exercice. Un labo où toutes les
#: charges sont égales ne décrit aucun utilisateur.
LOADS_KG = (
    ("latérales", 8.0), ("écarté arrière", 10.0), ("rear delt", 30.0), ("face pull", 22.5),
    ("triceps", 25.0), ("curl", 14.0), ("dips", 10.0), ("smith", 50.0), ("chest press", 55.0),
    ("shoulder press", 40.0), ("tirage", 55.0), ("rowing", 60.0), ("row", 60.0),
    ("pull", 50.0), ("squat", 90.0), ("presse", 140.0), ("leg", 50.0), ("mollets", 60.0),
    ("calf", 60.0), ("hip thrust", 80.0), ("soulevé", 80.0), ("crunch", 30.0),
)


def _load_for(name: str, week: int) -> float:
    low = name.lower()
    base = next((kg for key, kg in LOADS_KG if key in low), 30.0)
    return round(base * (1 + 0.05 * week) / 2.5) * 2.5

#: Jours écoulés depuis chaque séance semée. Semer tout « maintenant » rend
#: TOUTES les zones non récupérées : V3 choisit alors, à juste titre, le cardio.
#: Un labo représentatif étale l'historique comme le ferait un vrai pratiquant.
DAYS_AGO = [15, 13, 12, 10, 8, 6, 4, 2]

#: D13 — les trois familles du premier lancement, rapportées aux familles que
#: V3 dérive déjà des slugs (`famille_de`). Aucune ontologie nouvelle.
FAMILIES = {
    "upper": ("Haut du corps", ("push", "pull", "catch-up", "short")),
    "lower": ("Bas du corps", ("legs",)),
    "full": ("Corps entier", ("full-body",)),
}


def _login(c: TestClient, username: str = "n0-lab") -> int:
    with SessionLocal() as db:
        # Throwaway DB, cookie minted directly: this account never logs in.
        u = User(username=username, password_hash="!unusable")  # noqa: S106
        db.add(u)
        db.commit()
        uid = u.id
    probe = Response()
    create_session_cookie(probe, uid)
    c.cookies.extract_cookies(httpx.Response(
        200, headers=[("set-cookie", probe.headers["set-cookie"])],
        request=httpx.Request("GET", str(c.base_url))))
    return uid


def _start(c: TestClient, slug: str) -> int:
    r = c.post("/sessions", data={"template_slug": slug}, follow_redirects=False)
    if r.status_code != 303:
        raise SystemExit(f"START {slug} → {r.status_code}")
    return int(re.match(r"/sessions/(\d+)", r.headers["location"]).group(1))


def _ordered_exercises(db, sid: int) -> list[SessionExercise]:
    return db.execute(select(SessionExercise).where(SessionExercise.session_id == sid)
                      .order_by(SessionExercise.position)).scalars().all()


def _work_sets(db, se_id: int) -> list[SetLog]:
    rows = db.execute(select(SetLog).where(
        SetLog.session_exercise_id == se_id, SetLog.kind == "work")).scalars()
    return sorted(rows, key=lambda x: x.set_index)


def _backdate(sid: int, days: int) -> None:
    """Décale une séance semée et ses séries dans le passé (base jetable seulement)."""
    shift = timedelta(days=days)
    with SessionLocal() as db:
        s = db.get(WorkoutSession, sid)
        s.started_at = s.started_at - shift
        if s.ended_at:
            s.ended_at = s.ended_at - shift
        for sl in db.execute(select(SetLog).join(SessionExercise).where(
                SessionExercise.session_id == sid)).scalars():
            if sl.completed_at:
                sl.completed_at = sl.completed_at - shift
        db.commit()


def _complete(c: TestClient, slug: str, week: int | None) -> int:
    sid = _start(c, slug)
    with SessionLocal() as db:
        plan = [(se.id, actual_exercise_name(se), [s.id for s in _work_sets(db, se.id)])
                for se in _ordered_exercises(db, sid)]
    for se_id, name, set_ids in plan:
        data = {"nav": "next"}
        for i, s in enumerate(set_ids):
            if week is not None:  # séries au poids du corps (abdos d'une LISS) : reps seules
                data[f"set_{s}_weight_kg"] = str(_load_for(name, week))
            data[f"set_{s}_reps"] = str(10 - i + (week or 0))
        c.post(f"/sessions/{sid}/exercises/{se_id}", data=data, follow_redirects=False)
    end = {"action": "end"}
    if week is None:
        end |= {"cardio_duration_min": "35", "cardio_bpm_avg": "128", "cardio_machine_type": "bike"}
    c.post(f"/sessions/{sid}", data=end, follow_redirects=False)
    return sid


def _split_name(name: str) -> tuple[str, str | None]:
    head, _, tail = name.partition(" — ")
    return head, tail or None


def _mission(db, uid: int) -> dict:
    reco = advice_memory.recommander(db, uid, politique=advice_memory.POLITIQUE_SERVIE,
                                     avec_memoire=advice_memory.MEMOIRE_SERVIE)
    top, tpl = reco["top"], reco["top"]["template"]
    if not tpl.exercises:
        raise SystemExit(f"V3 serves {tpl.slug!r} ({top['phrase']!r}) — no exercise to execute; "
                         "adjust HISTORY, never the engine")
    first = min(tpl.exercises, key=lambda te: te.position)
    name, subtitle = _split_name(tpl.name)
    expl = top["explication"]
    return {
        "state": "READY",
        "template": {"slug": tpl.slug, "name": name, "subtitle": subtitle},
        "reason": {"phrase": top["phrase"], "reasons": explain_recommendation(reco)["reasons"],
                   "winning": list(expl["facteurs_gagnants"]),
                   "limiting": list(expl["facteurs_limitants"]),
                   "horizon": expl["horizon"], "provenance": expl["provenance"]},
        "alternatives": [{"slug": a["template"].slug, "name": _split_name(a["template"].name)[0],
                          "phrase": a["phrase"]} for a in reco["alternatives"]],
        "scope": {"exercise_count": len(tpl.exercises),
                  "work_set_count": sum(len(te.rep_targets) for te in tpl.exercises),
                  "first_exercise": {"name": first.name, "set_scheme": first.set_scheme}},
        "decision_identity": {"fingerprint": reco["context"]["empreinte_contexte"],
                              "policy": reco["context"]["politique"]},
        "duration_estimate": None,
    }


def _rep_range(se: SessionExercise) -> dict | None:
    te = se.template_exercise
    targets = sorted(te.rep_targets, key=lambda t: t.set_index) if te else []
    return {"min": targets[0].min_reps, "max": targets[0].max_reps} if targets else None


def _prefill(hint, first_prev: dict, rng: dict | None) -> dict:
    """D6 (labo) : cible du moteur, sinon dernière série faite, sinon rien."""
    if hint and hint.target_weight_kg is not None:
        # Jamais sous la cible basse du moteur : pré-remplir 11 quand il vise 12
        # ferait contredire la saisie par le guidage affiché juste au-dessus.
        reps = max(first_prev.get("reps") or 0, hint.target_reps_min or 0) or None
        return {"weight_kg": hint.target_weight_kg, "reps": reps, "origin": "OVERLOAD_TARGET"}
    if first_prev.get("weight_kg") is not None:
        return {"weight_kg": first_prev["weight_kg"], "reps": first_prev.get("reps"),
                "origin": "LAST_SET"}
    return {"weight_kg": None, "reps": (rng or {}).get("min"), "origin": "NONE"}


def _best(db, s: WorkoutSession, code: str) -> dict | None:
    """Meilleure série de travail ENREGISTRÉE — charge, puis reps — base des records.

    Même portée que `last_time_by_exercise_code` : même gabarit, même code (les
    codes `E1…` sont locaux au gabarit). Un record ne se compare qu'au même objet.
    """
    rows = db.execute(
        select(SetLog.weight_kg, SetLog.reps)
        .join(SessionExercise, SetLog.session_exercise_id == SessionExercise.id)
        .join(WorkoutSession, SessionExercise.session_id == WorkoutSession.id)
        .where(WorkoutSession.user_id == s.user_id, WorkoutSession.id != s.id,
               WorkoutSession.template_slug_snapshot == s.template_slug_snapshot,
               SessionExercise.exercise_code_snapshot == code, SetLog.kind == "work",
               SetLog.completed.is_(True), SetLog.weight_kg.is_not(None),
               SetLog.reps.is_not(None))).all()
    if not rows:
        return None
    weight, reps = max(rows, key=lambda r: (r[0], r[1]))
    return {"weight_kg": weight, "reps": reps}


def _exercise(db, s: WorkoutSession, se: SessionExercise, last: dict) -> dict:
    inp = build_overload_input_for_exercise(db, s, se)
    hint = compute_overload_hint(inp) if inp else None
    guidance = explain_overload_hint(hint) if hint else None
    prev = last.get(se.exercise_code_snapshot) or {}
    rng = _rep_range(se)
    te = se.template_exercise
    suggestions = compute_suggestions(te) if te else {}
    # même règle que le relevé serveur (`session_recap._zones_touched`)
    primary, _ = classify_exercise(actual_exercise_name(se))
    return {
        "se_id": se.id, "code": se.exercise_code_snapshot,
        "prescribed_name": se.exercise_name_snapshot, "executed_name": actual_exercise_name(se),
        "set_scheme": te.set_scheme if te else None, "rep_range": rng,
        "guidance": guidance and {k: guidance[k] for k in
                                  ("state", "intent_label", "target_summary", "reasons", "is_silent")},
        "previous": ({"relative": prev.get("relative"), "weights": prev.get("weights_str"),
                      "reps": prev.get("reps_str")} if prev.get("has_data") else None),
        "prefill": _prefill(hint, prev.get("first_set") or {}, rng),
        "substitutes": [sg.name for lvl in ("N1", "N2") for sg in suggestions.get(lvl, [])][:4],
        "zone": None if primary == "unknown" else {"zone": primary,
                                                    "label": _ZONE_LABELS.get(primary, primary)},
        "best": _best(db, s, se.exercise_code_snapshot),
    }


def _transitions(sets: list[dict]) -> dict:
    """Table du chemin nominal (§8.8), calculée côté serveur ; le client la suit."""
    table = {}
    for i, st in enumerate(sets):
        nxt = sets[i + 1] if i + 1 < len(sets) else None
        if nxt is None:
            table[str(st["set_id"])] = {"kind": "BILAN"}
        elif nxt["se_id"] == st["se_id"]:
            table[str(st["set_id"])] = {"kind": "REST_THEN_SET", "set_id": nxt["set_id"]}
        else:
            table[str(st["set_id"])] = {"kind": "REST_THEN_EXERCISE", "se_id": nxt["se_id"],
                                        "set_id": nxt["set_id"]}
    return table


def _plan(c: TestClient, slug: str) -> dict:
    sid = _start(c, slug)
    with SessionLocal() as db:
        s = db.get(WorkoutSession, sid)
        now = datetime.now(UTC)
        last = last_time_by_exercise_code(db, s, now)
        ses = _ordered_exercises(db, sid)
        sets = [{"set_id": x.id, "se_id": se.id, "index": x.set_index}
                for se in ses for x in _work_sets(db, se.id)]
        plan = {
            "session_id": sid, "template_slug": slug, "template_name": s.template_name_snapshot,
            "server_now": now.isoformat(), "rest_default_seconds": REST_FALLBACK_SECONDS,
            "exercises": [_exercise(db, s, se, last) for se in ses],
            "sets": sets, "on_complete": _transitions(sets),
        }
    c.post(f"/sessions/{sid}", data={"action": "end"}, follow_redirects=False)
    return plan


def _recap(c: TestClient, slug: str) -> dict:
    """Relevé serveur d'une séance de ce gabarit réellement finie (zones par série)."""
    sid = _complete(c, slug, 2)
    with SessionLocal() as db:
        summ = build_recap(db.get(WorkoutSession, sid))["summary"]
    return {"work_sets_total": summ["work_sets_total"],
            "substitution_count": summ["substitution_count"],
            "top_progression": summ["top_progression"], "zones_touched": summ["zones_touched"]}


def _family_slugs(c: TestClient, prefixes: tuple[str, ...]) -> list[str]:
    """Les gabarits proposables d'une famille, DANS L'ORDRE DE V3 pour un
    utilisateur sans historique (hors utilitaires et archivés).

    D13 : l'utilisateur choisit sa première séance parmi les gabarits EXISTANTS.
    LABO : le vrai choix à froid (objectif × famille × matériel) est une tranche
    métier ; ceci n'invente aucun ordre, il lit celui du moteur servi.
    """
    uid = _login(c, f"n0-order-{prefixes[0]}")
    with SessionLocal() as db:
        return [v.slug for v in classer_candidats(db, uid, datetime.now(UTC))
                if famille_de(v.slug) in prefixes and v.template.catalog_section != "utility"
                and v.template.exercises]


def _newcomer(c: TestClient, slug: str) -> dict:
    """Un nouvel utilisateur réel qui choisit ce gabarit : sa première séance,
    puis ce que le moteur propose une fois qu'il l'a faite (charges de semaine 0)."""
    uid = _login(c, f"n0-new-{slug}")
    first = _plan(c, slug)
    _complete(c, slug, 0)
    with SessionLocal() as db:
        nxt = _mission(db, uid)
    name, subtitle = _split_name(first["template_name"])
    return {"slug": slug, "name": name, "subtitle": subtitle, "plan": first,
            "next_mission": nxt, "next_plan": _plan(c, nxt["template"]["slug"])}


def _family(c: TestClient, key: str) -> dict:
    label, prefixes = FAMILIES[key]
    return {"label": label, "sessions": [_newcomer(c, s) for s in _family_slugs(c, prefixes)]}


def main() -> None:
    fixture: dict = {"generated_at": datetime.now(UTC).isoformat(timespec="seconds"),
                     "source": "canonical services on a throwaway SQLite (generate_fixtures.py)",
                     "history_seeded": [f"{s} (J-{d})" for (s, _), d in zip(HISTORY, DAYS_AGO,
                                                                           strict=True)]}
    with TestClient(main_mod.app) as c:
        uid = _login(c)
        for (slug, week), days in zip(HISTORY, DAYS_AGO, strict=True):
            _backdate(_complete(c, slug, week), days)
        with SessionLocal() as db:
            fixture["mission"] = _mission(db, uid)
        slugs = [fixture["mission"]["template"]["slug"]] + \
            [a["slug"] for a in fixture["mission"]["alternatives"]]
        # Plans d'abord (tous sur le même historique), relevés ensuite.
        fixture["plans"] = {slug: _plan(c, slug) for slug in slugs}
        fixture["recaps"] = {slug: _recap(c, slug) for slug in slugs}
        # D13 — un nouvel utilisateur par gabarit proposable, chacun sur sa propre histoire vide
        fixture["onboarding"] = {"families": {k: _family(c, k) for k in FAMILIES}}

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(fixture, ensure_ascii=False, indent=2, default=str) + "\n",
                   encoding="utf-8")
    m = fixture["mission"]
    with_history = [s for s, p in fixture["plans"].items()
                    if any(e["previous"] for e in p["exercises"])]
    print(f"wrote {OUT.relative_to(ROOT)} — top={m['template']['slug']} "
          f"phrase={m['reason']['phrase']!r} plans={list(fixture['plans'])} "
          f"with_history={with_history}")
    for k, f in fixture["onboarding"]["families"].items():
        for s in f["sessions"]:
            print(f"  {k}: {s['slug']} → next={s['next_mission']['template']['slug']}")


if __name__ == "__main__":
    main()
