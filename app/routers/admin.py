"""`SESSION_LIFECYCLE` — le cycle de vie d'une séance enregistrée.

CE QUE CETTE RESPONSABILITÉ POSSÈDE, ET POURQUOI ELLE EST NOMMÉE
------------------------------------------------------------------
`UI-CP5 FLIGHT_RECORDER` a nommé une frontière qui existait déjà sans nom.
L'instrument de lecture répond à « qu'est-ce qui vient de changer ? » et son
contrat dit `ACTION : aucune. C'est une lecture.` — alors que `/history`
portait **42 formulaires**, deux par séance, pour exclure des KPI et supprimer.

Ce ne sont pas des lectures : c'est le **cycle de vie de la donnée**. Il vit
ici, sur une surface unique, et la capacité n'a pas bougé d'un cran — seul le
fardeau de commande a quitté l'instrument.

    GET  /admin/sessions                  la liste de gestion
    GET  /admin/sessions/{id}/delete      la CONFIRMATION, nommée et chiffrée
    POST /admin/sessions/{id}/delete      suppression dure, en cascade
    POST /admin/sessions/{id}/exclude     bascule `excluded_from_stats`

⚠ LA ROUTE GARDE SON PRÉFIXE `/admin`. Le renommer toucherait
`docs/AUTH_SCOPE_MATRIX.md` et son script de vérification : c'est une dérive
hors périmètre. La responsabilité est nommée ici ; l'URL suivra une autre fois.

LA DESTINATION EST DÉCLARÉE, PLUS RENIFLÉE
--------------------------------------------
Ces deux routes choisissaient leur redirection en cherchant `"/history"` dans
l'en-tête `Referer`. C'était porteur : le jour où les formulaires quittent
`/history`, toute action rebondit silencieusement vers `/admin/sessions`. Et
`Referer` est absent sous `Referrer-Policy: no-referrer`, retiré par les outils
de confidentialité, et contrôlé par l'appelant.

La destination est désormais un champ `next` **validé contre une liste close**.
Un en-tête devinable est remplacé par une valeur déclarée et vérifiée.

⚠ AUCUNE MACHINERIE CSRF N'EXISTE DANS CETTE APPLICATION, et la confirmation en
deux temps ci-dessous **n'en est pas une**. Elle protège d'un geste accidentel,
pas d'une requête forgée. L'écrire ici pour que personne ne la lise autrement.
"""
from __future__ import annotations

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.deps import CurrentUser, DbSession
from app.models.session import SessionExercise, WorkoutSession
from app.services.ownership import get_owned_session_or_404
from app.services.quality_score import compute_session_quality
from app.services.session_state import latest_open_session
from app.services.time_format import format_duration_short, session_duration
from app.templating import templates

router = APIRouter(tags=["admin"])

#: La liste CLOSE des destinations de retour. Une valeur hors de cette liste
#: est ignorée, jamais suivie : c'est ce qui distingue une destination déclarée
#: d'un en-tête `Referer`, que l'appelant contrôle.
#:
#: ⚠ Pas de préfixe libre, pas de « commence par `/` » : une allowlist de
#: chemins EXACTS. `//evil.example` commence bien par `/` et part ailleurs.
DESTINATIONS_DE_RETOUR = frozenset({"/admin/sessions", "/history", "/progress"})
DESTINATION_PAR_DEFAUT = "/admin/sessions"

#: Le champ que seule la vue de confirmation produit. Sans lui, aucune
#: suppression — la protection devient une propriété du SERVEUR, là où le
#: `confirm()` JavaScript d'avant ne protégeait que les navigateurs coopératifs.
CONFIRMATION_ATTENDUE = "oui"


def _destination(valeur: str | None) -> str:
    """La destination de retour, si elle est dans la liste close."""
    return valeur if valeur in DESTINATIONS_DE_RETOUR else DESTINATION_PAR_DEFAUT


@router.get("/admin/sessions", response_class=HTMLResponse)
def admin_sessions(request: Request, db: DbSession, user: CurrentUser) -> HTMLResponse:
    stmt = (
        select(WorkoutSession)
        .where(WorkoutSession.user_id == user.id)
        .order_by(WorkoutSession.started_at.desc())
        .options(
            selectinload(WorkoutSession.session_exercises)
            .selectinload(SessionExercise.set_logs)
        )
    )
    sessions = list(db.execute(stmt).scalars().all())

    rows: list[dict] = []
    for s in sessions:
        quality = compute_session_quality(s) if s.status == "completed" else None
        total_ex = len(s.session_exercises)
        done_ex = 0
        for se in s.session_exercises:
            work = [sl for sl in se.set_logs if sl.kind == "work"]
            if work and all(sl.completed for sl in work):
                done_ex += 1
        rows.append({
            "session": s,
            "quality": quality,
            "total_exercises": total_ex,
            "done_exercises": done_ex,
            "duration": format_duration_short(session_duration(s.started_at, end=s.ended_at)),
        })

    return templates.TemplateResponse(
        request,
        "admin_sessions.html",
        {
            "page_title": "Gestion des séances",
            "rows": rows,
            "active_session": latest_open_session(db, user.id),
        },
    )


@router.get("/admin/sessions/{session_id}/delete", response_class=HTMLResponse,
            name="confirm_delete_session")
def confirm_delete_session(
    session_id: int, request: Request, db: DbSession, user: CurrentUser,
    next: str | None = None,
) -> HTMLResponse:
    """La confirmation — nommée, chiffrée, et appliquée par le SERVEUR.

    ⚠ ELLE REMPLACE UN `confirm()` JAVASCRIPT, et c'est strictement plus fort.
    L'ancien vivait dans `onsubmit` : côté client uniquement, donc contournable
    par n'importe quelle requête directe, et c'était du JavaScript sur une
    surface que le dépôt garde contre le JavaScript.

    Elle dit ce qui disparaît — la séance, ses exercices, ses séries — parce
    qu'une suppression en cascade qu'on n'a pas chiffrée n'est pas un
    consentement éclairé.

    Elle offre l'alternative RÉVERSIBLE dans le même écran. « Preserve
    capability. Remove command burden. » se lit aussi ainsi : la commande la
    plus destructive ne doit pas être la seule offerte.
    """
    session = get_owned_session_or_404(db, session_id, user.id)
    exercices = len(session.session_exercises)
    series = sum(len(se.set_logs) for se in session.session_exercises)
    return templates.TemplateResponse(
        request,
        "admin_session_delete.html",
        {
            "page_title": "Supprimer cette séance",
            "session": session,
            "exercices": exercices,
            "series": series,
            "retour": _destination(next),
            "active_session": latest_open_session(db, user.id),
        },
    )


@router.post("/admin/sessions/{session_id}/delete")
def delete_session(
    session_id: int, request: Request, db: DbSession, user: CurrentUser,
    confirmation: str | None = Form(default=None),
    next: str | None = Form(default=None),
) -> RedirectResponse:
    session = get_owned_session_or_404(db, session_id, user.id)

    # ⚠ SANS LE CHAMP, AUCUNE SUPPRESSION. On renvoie vers la confirmation
    # plutôt que d'échouer : l'utilisateur voulait bien supprimer, il lui
    # manque l'étape qui le lui fait dire.
    if confirmation != CONFIRMATION_ATTENDUE:
        return RedirectResponse(
            url=f"/admin/sessions/{session_id}/delete", status_code=303,
        )

    db.delete(session)
    db.commit()
    # ⚠ LA SUPPRESSION N'HONORE JAMAIS UNE DESTINATION SCOPÉE SUR LA SÉANCE :
    # elle vient d'être détruite en cascade, et y revenir rendrait un 404 juste
    # après une action réussie.
    return RedirectResponse(url=_destination(next), status_code=303)


@router.post("/admin/sessions/{session_id}/exclude")
def toggle_exclude(
    session_id: int, request: Request, db: DbSession, user: CurrentUser,
    next: str | None = Form(default=None),
) -> RedirectResponse:
    session = get_owned_session_or_404(db, session_id, user.id)
    session.excluded_from_stats = not session.excluded_from_stats
    db.commit()
    return RedirectResponse(url=_destination(next), status_code=303)
