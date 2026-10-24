"""`D9` — l'API versionnée de l'application mobile : `/api/mobile/v1`.

LA PLUS PETITE SURFACE QUI FERME LE PARCOURS
----------------------------------------------
connexion → mission → démarrage → séries confirmées → fin, abandon.

* Authentification : `Bearer` seul (`deps.require_api_user`). Le cookie web
  n'ouvre rien ici, et un jeton d'accès n'ouvre aucune route HTML.
* Le serveur garde le cerveau : la mission est la recommandation servie, le
  démarrage est LA composition du web — ses propres fonctions, appelées par le
  module (`web_sessions._poser_adaptations`, …) pour qu'une garde qui les
  remplace couvre les deux routes à la fois.
* Une série = une commande. Jamais le formulaire d'exercice entier du web, qui
  réécrit note, sensation et substitution absentes (`partial-form-replacement`).
* Le temps de l'appareil ne décide jamais l'authentification ; il ne date une
  série que dans des bornes serveur (`D11`).

Aucune route de cette API ne rend de HTML, et aucune route HTML n'a changé.
"""
from __future__ import annotations

import functools
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.deps import ApiUser, DbSession
from app.enums import SessionStatus
from app.models.catalog import TemplateExercise, WorkoutTemplate
from app.models.session import WorkoutSession
from app.models.user import User
from app.routers import sessions as web_sessions
from app.services import device_auth
from app.services.auth import verify_password
from app.services.environment_activation import ADAPTABLE, REFUSE, preparer_demarrage
from app.services.feedback import compute_success_score
from app.services.mobile_read_models import (
    execution_read_model,
    iso_utc,
    load_owned_session,
    mission_read_model,
)
from app.services.password_policy import is_password_too_long
from app.services.seed import CUSTOM_CATALOG_SECTION
from app.services.session_builder import instantiate_session
from app.services.session_state import latest_open_session
from app.services.user_program_launch import is_owned_published_template


def _no_store(response: Response) -> None:
    """Des jetons et des faits d'entraînement : jamais en cache intermédiaire."""
    response.headers["Cache-Control"] = "no-store"


router = APIRouter(prefix="/api/mobile/v1", tags=["mobile"],
                   dependencies=[Depends(_no_store)])

#: `D11` — marge de l'horloge d'appareil au-delà de la réception serveur.
PERFORMED_AT_TOLERANCE = timedelta(seconds=120)

#: `§10` — une commande reçue est ACQUITTÉE, qu'elle ait écrit ou trouvé le fait déjà là.
ACKNOWLEDGED, APPLIED = "ACKNOWLEDGED", "applied"


def _err(status: int, code: str, **extra: Any) -> HTTPException:
    return HTTPException(status_code=status, detail={"error": code, **extra})


def _aware(dt: datetime) -> datetime:
    """SQLite rend des `datetime` naïfs : ils SONT de l'UTC."""
    return dt.replace(tzinfo=UTC) if dt.tzinfo is None else dt.astimezone(UTC)


# ── AUTHENTIFICATION ─────────────────────────────────────────────────────


class LoginBody(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=256)
    device_label: str | None = Field(default=None, max_length=128)


class RefreshBody(BaseModel):
    refresh_token: str = Field(min_length=1, max_length=256)


@functools.cache
def _dummy_hash() -> str:
    """Un condensat qu'aucun mot de passe ne vérifie, calculé une fois.

    Comme le web : bcrypt tourne aussi quand le compte n'existe pas, pour que le
    temps de réponse ne dise pas lequel des deux a échoué.
    """
    return bcrypt.hashpw(secrets.token_bytes(16), bcrypt.gensalt(12)).decode("utf-8")


def _tokens(issued: device_auth.IssuedTokens) -> dict[str, Any]:
    return {"token_type": "Bearer", "access_token": issued.access_token,
            "access_expires_in": issued.access_expires_in,
            "refresh_token": issued.refresh_token,
            "server_now": datetime.now(UTC).isoformat()}


def _me(user: User) -> dict[str, Any]:
    return {"id": user.id, "username": user.username}


@router.post("/auth/login")
def login(body: LoginBody, db: DbSession) -> dict[str, Any]:
    if is_password_too_long(body.password):
        raise _err(400, "password_too_long")
    user = db.execute(
        select(User).where(User.username == body.username, User.is_active.is_(True))
    ).scalar_one_or_none()
    ok = verify_password(body.password, user.password_hash if user else _dummy_hash())
    if user is None or not ok:
        raise _err(401, "invalid_credentials")
    issued = device_auth.open_device_session(db, user, device_label=body.device_label)
    db.commit()
    return {**_tokens(issued), "user": _me(user)}


@router.post("/auth/refresh")
def refresh(body: RefreshBody, db: DbSession) -> dict[str, Any]:
    issued = device_auth.rotate_refresh(db, body.refresh_token)
    # Committer AUSSI l'échec : une réutilisation détectée a révoqué l'appareil.
    db.commit()
    if issued is None:
        raise _err(401, "invalid_refresh")
    return _tokens(issued)


@router.post("/auth/logout", status_code=204)
def logout(request: Request, user: ApiUser, db: DbSession) -> Response:
    """Cet appareil seul. Le web et les autres appareils restent connectés."""
    device_auth.revoke_device_session(request.state.device_session)
    db.commit()
    return Response(status_code=204, headers={"Cache-Control": "no-store"})


@router.get("/auth/me")
def me(user: ApiUser) -> dict[str, Any]:
    return _me(user)


# ── MISSION ──────────────────────────────────────────────────────────────


@router.get("/mission")
def mission(user: ApiUser, db: DbSession) -> dict[str, Any]:
    return mission_read_model(db, user.id)


# ── DÉMARRAGE ────────────────────────────────────────────────────────────


class DecisionBody(BaseModel):
    fingerprint: str | None = Field(default=None, max_length=128)
    policy: str | None = Field(default=None, max_length=16)
    top: str | None = Field(default=None, max_length=64)
    alternatives: list[str] = Field(default_factory=list, max_length=4)


class StartBody(BaseModel):
    template_slug: str = Field(min_length=1, max_length=64)
    creation_source: str | None = Field(default=None, max_length=16)
    decision: DecisionBody | None = None


def _startable_template(db, user: User, slug: str) -> WorkoutTemplate:
    tpl = db.execute(
        select(WorkoutTemplate).where(WorkoutTemplate.slug == slug)
        .options(selectinload(WorkoutTemplate.exercises)
                 .selectinload(TemplateExercise.rep_targets))
    ).scalar_one_or_none()
    # Un gabarit personnel d'autrui est indistinct d'un gabarit inconnu (aucune fuite).
    if tpl is None or (tpl.catalog_section == CUSTOM_CATALOG_SECTION
                       and not is_owned_published_template(db, user.id, tpl.id)):
        raise _err(404, "unknown_template")
    return tpl


@router.post("/sessions", status_code=201)
def start(body: StartBody, user: ApiUser, db: DbSession) -> dict[str, Any]:
    """`START_SESSION` : la composition du web, plus le refus d'une seconde séance ouverte."""
    ouverte = latest_open_session(db, user.id)
    if ouverte is not None:
        raise _err(409, "session_open", session_id=ouverte.id)
    tpl = _startable_template(db, user, body.template_slug)

    # TRAIN A — le préflight précède l'instanciation (`Sb_TRAIN_A_ENV_EXP_01 §1`).
    preparation = preparer_demarrage(db, user.id, tpl)
    if preparation.etat == REFUSE:
        raise _err(409, "start_blocked", reason="equipment")
    session = instantiate_session(db, tpl, datetime.now(UTC), user_id=user.id)
    # `G6` — l'adaptation se matérialise AVANT le démarrage ; PARTIEL = ÉCHEC.
    if preparation.etat == ADAPTABLE:
        poses = web_sessions._poser_adaptations(session, preparation.plan)
        if poses != preparation.attendu:
            db.rollback()
            raise _err(409, "start_blocked", reason="equipment")
    if body.creation_source in web_sessions._CREATION_SOURCE_ALLOWED:
        session.creation_source = body.creation_source
    db.commit()
    db.refresh(session)

    # `REC-CP4` — après le commit, jamais avant : la séance ne dépend pas de la télémétrie.
    d = body.decision
    if d is not None:
        web_sessions._enregistrer_episode_de_conseil(
            db, user.id, slug_demarre=tpl.slug, session_id=session.id,
            empreinte=d.fingerprint, politique=d.policy, top=d.top,
            alts=",".join(d.alternatives),
        )
        db.commit()
    return execution_read_model(db, load_owned_session(db, session.id, user.id))


def _owned(db, session_id: int, user: User) -> WorkoutSession:
    s = load_owned_session(db, session_id, user.id)
    if s is None:  # celle d'autrui est indistincte d'une séance inexistante
        raise _err(404, "unknown_session")
    return s


def _open_owned(db, session_id: int, user: User) -> WorkoutSession:
    """Une séance à soi ET ouverte : une séance close ne reçoit plus de fait."""
    s = _owned(db, session_id, user)
    if s.status != SessionStatus.IN_PROGRESS.value:
        raise _err(409, "session_closed")
    return s


@router.get("/sessions/{session_id}/execution")
def execution(session_id: int, user: ApiUser, db: DbSession) -> dict[str, Any]:
    return execution_read_model(db, _owned(db, session_id, user))


# ── SÉRIE CONFIRMÉE ──────────────────────────────────────────────────────


class SetCompletionBody(BaseModel):
    op_id: str = Field(min_length=8, max_length=64)
    weight_kg: float | None = Field(default=None, ge=0, le=1000)
    reps: int = Field(ge=1, le=100)
    performed_at: datetime
    performed_at_estimated: bool = False


def _bounded_performed_at(
    body: SetCompletionBody, *, floor: datetime, now: datetime,
) -> tuple[datetime, bool]:
    """`D11` (`§8.8bis`) — rend `(heure retenue, hors bornes ?)`.

    Accepté si `plancher ≤ performed_at ≤ réception + tolérance` — le plancher est
    le début de séance, ou la série précédente du même exercice (ordre). Aucune
    date future n'est écrite : une heure dans la tolérance est ramenée à la
    réception. Hors bornes, ancrée ou estimée, le serveur garde son heure de
    réception et le DIT dans la réponse — un fait réel n'est jamais refusé pour
    une horloge d'appareil, et jamais réordonné en silence.
    """
    at = _aware(body.performed_at)
    if floor <= at <= now + PERFORMED_AT_TOLERANCE:
        return min(at, now), False
    return now, True


@router.put("/sessions/{session_id}/sets/{set_id}")
def complete_set(
    session_id: int, set_id: int, body: SetCompletionBody, user: ApiUser, db: DbSession,
) -> dict[str, Any]:
    """`SET_COMPLETION` — UNE série. Idempotent par nature : rejouer la même
    commande ne crée rien, puisque la série existe déjà (`§8.4`).

    N'écrit que la ligne `set_logs` visée, et le score dérivé de l'exercice.
    Note, sensation, substitution et autres séries ne sont jamais lues ni écrites.
    """
    s = _open_owned(db, session_id, user)
    se, sl = next(((se, x) for se in s.session_exercises for x in se.set_logs
                   if x.id == set_id and x.kind == "work"), (None, None))
    if sl is None:
        raise _err(404, "unknown_set")
    if sl.completed and sl.weight_kg == body.weight_kg and sl.reps == body.reps:
        # Le fait existe déjà : un rejeu de l'outbox, ou un double envoi.
        return _ack(body, sl, applied=False, adjusted=False)

    before = [_aware(x.completed_at) for x in se.set_logs
              if x.kind == "work" and x.set_index < sl.set_index and x.completed
              and x.completed_at is not None]
    floor = max([_aware(s.started_at), *before])
    at, adjusted = _bounded_performed_at(body, floor=floor, now=datetime.now(UTC))
    if not sl.completed:
        # Transition INCOMPLÈTE → COMPLÈTE : elle seule date la série (`UI-CP8R`).
        # Une correction d'une série déjà faite garde sa date.
        sl.completed_at = at
        sl.rest_dismissed_at = None
    else:
        adjusted = False
    sl.weight_kg, sl.reps, sl.completed = body.weight_kg, body.reps, True
    se.success_score = compute_success_score(se, se.template_exercise)
    db.commit()
    return _ack(body, sl, applied=True, adjusted=adjusted)


def _ack(body: SetCompletionBody, sl, *, applied: bool, adjusted: bool) -> dict[str, Any]:
    """`ACKNOWLEDGED` — aussi quand le fait existait déjà pour cette commande (`§10`)."""
    return {"op_id": body.op_id, "set_id": sl.id, "state": ACKNOWLEDGED,
            APPLIED: applied, "performed_at": iso_utc(sl.completed_at),
            "performed_at_adjusted": adjusted}


# ── REMPLACEMENT ─────────────────────────────────────────────────────────


class SubstituteBody(BaseModel):
    op_id: str = Field(min_length=8, max_length=64)
    name: str = Field(min_length=1, max_length=255)


@router.post("/sessions/{session_id}/exercises/{se_id}/substitute")
def substitute(
    session_id: int, se_id: int, body: SubstituteBody, user: ApiUser, db: DbSession,
) -> dict[str, Any]:
    """`SUBSTITUTE` — la commande `REQUIRES_SYNC` du labo, enfin appliquée par le serveur.

    Sans elle, les séries faites sur le remplaçant seraient enregistrées sous le
    nom prescrit : un faux fait. Le serveur n'accepte qu'un remplaçant qu'il a
    lui-même proposé, et seulement avant la première série de travail — la règle
    du web (`can_substitute`). Il n'écrit que `substituted_name`.
    """
    from app.services.substitution import can_substitute, compute_suggestions

    s = _open_owned(db, session_id, user)
    se = next((x for x in s.session_exercises if x.id == se_id), None)
    if se is None:
        raise _err(404, "unknown_exercise")
    te = se.template_exercise
    proposes = {sg.name for lvl in compute_suggestions(te).values() for sg in lvl} if te else set()
    if body.name not in proposes:
        raise _err(422, "unknown_substitute")
    applied = se.substituted_name != body.name
    if applied:
        if not can_substitute(se):
            raise _err(409, "substitution_locked")
        se.substituted_name = body.name
        db.commit()
    return {"op_id": body.op_id, "se_id": se.id, "state": ACKNOWLEDGED,
            APPLIED: applied, "executed_name": se.substituted_name}


# ── FIN DE SÉANCE (R16) ──────────────────────────────────────────────────


class CloseBody(BaseModel):
    op_id: str | None = Field(default=None, max_length=64)
    #: Quand l'utilisateur a décidé, sur l'appareil. Toujours borné, jamais refusé :
    #: une clôture hors ligne synchronisée plus tard ne doit pas dater de la synchro.
    at: datetime | None = None


def _ended_at(s: WorkoutSession, body: CloseBody, now: datetime) -> datetime:
    faits = [_aware(x.completed_at) for se in s.session_exercises for x in se.set_logs
             if x.completed and x.completed_at is not None]
    floor = max([_aware(s.started_at), *faits])
    at = _aware(body.at) if body.at is not None else now
    return min(max(at, floor), now)


def _close(db, s: WorkoutSession, body: CloseBody, *, exclude: bool) -> None:
    s.ended_at = _ended_at(s, body, datetime.now(UTC))
    s.status = SessionStatus.COMPLETED.value
    if exclude:
        s.excluded_from_stats = True
    web_sessions._persist_implicit_labels_on_completion(s)
    db.commit()


def _closure(s: WorkoutSession, *, applied: bool) -> dict[str, Any]:
    from app.services.session_completion import completion_of

    etat = completion_of(s)
    return {"session_id": s.id, "status": s.status,
            "excluded_from_stats": bool(s.excluded_from_stats),
            "ended_at": iso_utc(s.ended_at), APPLIED: applied,
            "work_sets_done": etat.done, "work_sets_total": etat.total}


@router.post("/sessions/{session_id}/finish")
def finish(session_id: int, body: CloseBody, user: ApiUser, db: DbSession) -> dict[str, Any]:
    """TERMINER MAINTENANT — ce qui est fait reste fait, rien n'est fabriqué.

    C'est la clôture du web (`action=end`). Une fin anticipée n'a pas de motif
    stocké : `completion_of` la dérive des séries, et la continuité l'enregistre
    comme le web (« séance terminée à N séries sur M — travail reporté »).
    """
    s = _owned(db, session_id, user)
    if s.status == SessionStatus.COMPLETED.value:
        if s.excluded_from_stats:
            raise _err(409, "session_abandoned")
        return _closure(s, applied=False)
    _close(db, s, body, exclude=False)
    web_sessions._record_continuity_on_completion(db, s, user.id)
    db.refresh(s)
    return _closure(s, applied=True)


@router.post("/sessions/{session_id}/abandon")
def abandon(session_id: int, body: CloseBody, user: ApiUser, db: DbSession) -> dict[str, Any]:
    """ABANDONNER LA SÉANCE — close et EXCLUE des statistiques, jamais effacée.

    L'état existe déjà : `excluded_from_stats`, que l'historique web affiche
    « exclue » et que l'administration sait rebasculer. Les séries enregistrées
    restent en base ; elles ne comptent simplement plus. Aucune continuité n'est
    enregistrée : on ne reporte pas le travail d'une séance qu'on a renoncé à compter.
    """
    s = _owned(db, session_id, user)
    if s.status == SessionStatus.COMPLETED.value:
        if not s.excluded_from_stats:
            raise _err(409, "session_finished")
        return _closure(s, applied=False)
    _close(db, s, body, exclude=True)
    db.refresh(s)
    return _closure(s, applied=True)

