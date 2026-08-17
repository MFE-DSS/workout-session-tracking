"""Sb_FEEDBACK_SIGNAL_AUDIT_01 — gardes de véracité de l'audit.

Un rapport d'audit vieillit en silence : le code bouge, le document reste, et
plus rien ne signale qu'il est devenu faux. Ces gardes rendent périssable la
seule affirmation dont tout le reste dépend — **trois champs de signal de
`SetLog` ne sont jamais écrits par le produit**.

Elles ne figent PAS l'état actuel comme souhaitable. Le jour où l'un de ces
champs reçoit un producteur, la garde tombe : c'est le signal que l'audit doit
être relu, pas qu'une régression a eu lieu. Le message d'échec le dit.
"""
from __future__ import annotations

import pathlib

APP = pathlib.Path(__file__).resolve().parent.parent / "app"
REPORT = (
    pathlib.Path(__file__).resolve().parent.parent
    / "docs/strategy/Sb_FEEDBACK_SIGNAL_AUDIT_01_REPORT.md"
)

#: Champs présents sur le modèle, exportés et restaurables, mais qu'aucune
#: route, aucun service et aucun gabarit ne produit.
NEVER_WRITTEN = ("execution_quality", "reps_target")

#: Fichiers autorisés à mentionner ces champs : la définition du modèle, le
#: contrat d'export, et l'import d'archives.
ALLOWED = {
    "app/models/session.py",
    "app/services/export_builder.py",
    "app/services/restore.py",
}


def _mentions(field: str) -> set[str]:
    """Fichiers Python de `app/` qui mentionnent le champ."""
    hits: set[str] = set()
    for path in APP.rglob("*.py"):
        if field in path.read_text(encoding="utf-8"):
            hits.add(str(path.relative_to(APP.parent)))
    return hits


def test_the_dead_signal_fields_still_have_no_producer():
    """Le constat central de l'audit, rendu exécutable.

    Si cette garde tombe, ce n'est pas forcément un défaut : c'est qu'un
    producteur est apparu. Il faut alors relire l'audit — en particulier la
    décision D1 (« ne jamais collecter `reps_target` », redondant avec
    `success_score`) et la question ouverte OQ-2.
    """
    for field in NEVER_WRITTEN:
        unexpected = _mentions(field) - ALLOWED
        assert not unexpected, (
            f"{field!r} is now referenced in {sorted(unexpected)}. The audit "
            "Sb_FEEDBACK_SIGNAL_AUDIT_01 assumed it had no producer — re-read "
            "its §0, D1 and OQ-2 before relying on the document."
        )


def test_set_logs_are_created_without_any_feedback_signal():
    """`instantiate_session` ne pose que la structure, jamais du signal.

    C'est la raison mécanique pour laquelle les trois champs restent NULL.
    """
    src = (APP / "services/session_builder.py").read_text(encoding="utf-8")
    creation = src[src.find("SetLog("):]
    for field in (*NEVER_WRITTEN, "technique"):
        assert f"{field}=" not in creation[:400], (
            f"session_builder now seeds {field!r} — the audit's §0 is stale"
        )


def test_completed_is_never_a_user_input():
    """`completed` reste DÉRIVÉ (Sx_24 §E) — jamais une case à cocher.

    L'audit classe `completed` comme dérivé et recommande explicitement de ne
    jamais le rendre saisissable ; toute la sémantique de série en dépend.
    """
    # Assertion resserrée : d'autres cases à cocher existent légitimement
    # ailleurs (confirmation de remplacement, matériel du profil). L'invariant
    # porte sur la COMPLÉTION, pas sur les cases en général — une garde large
    # aurait interdit du balisage sans rapport.
    templates = pathlib.Path(APP / "templates")
    for path in templates.rglob("*.html"):
        text = path.read_text(encoding="utf-8")
        assert 'name="completed"' not in text, f"{path} exposes completed"
        assert 'name="set_completed"' not in text, f"{path} exposes set completion"

    card = (APP / "templates/_partials/exercise_card.html").read_text(
        encoding="utf-8")
    start = card.find("work_set_list")
    macro = card[start:card.find("endmacro", start)]
    assert 'type="checkbox"' not in macro, (
        "a checkbox inside the set row would make completion a user input, "
        "contradicting Sx_24 §E where it is derived from weight/reps"
    )


def test_the_audit_report_states_its_own_open_questions():
    """Un audit sans question ouverte est un audit qui a caché ses angles morts."""
    text = REPORT.read_text(encoding="utf-8")
    for marker in ("OQ-1", "OQ-2", "OQ-3", "OQ-4"):
        assert marker in text, f"{marker} missing from the audit report"
    assert "Decision proposal" in text
    assert "Build queue recommended" in text
