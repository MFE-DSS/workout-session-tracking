"""`D9` — authentification des applications : jeton d'accès court, rafraîchissement tournant.

LE MODÈLE
-----------
* **Jeton d'accès** : signé (`itsdangerous`), sel propre à l'usage, quinze
  minutes. Il porte l'utilisateur, l'époque `A0` du compte et la session
  d'appareil. Il vit en mémoire dans l'application, jamais sur disque.
* **Jeton de rafraîchissement** : `rt1.<session d'appareil>.<secret>`. Le
  secret n'existe en clair que dans la réponse et dans le stockage sécurisé du
  téléphone ; le serveur n'en garde que le condensat. Chaque échange le
  remplace : l'ancien ne rouvre plus rien, et le présenter révoque l'appareil
  (détection de réutilisation).
* **Session d'appareil** (`device_sessions`) : l'identité serveur de
  l'installation. La déconnexion mobile la révoque, elle seule.

CE QUI EST TENU, ET OÙ
------------------------
* Usage : un jeton d'accès ne se vérifie que sous `ACCESS_SALT` et relit
  `purpose` ; un jeton de rafraîchissement n'est pas signé du tout, il ne se
  résout que par condensat. Aucun des deux ne passe pour l'autre, ni pour le
  cookie web (`auth.SESSION_SALT`).
* Expiration : horloge du SERVEUR seule. Aucune valeur transmise par le client
  — ni `performed_at`, ni un en-tête `Date` — n'entre dans une décision
  d'authentification.
* Révocation : par appareil (`revoked_at`) et globale (`session_epoch` recopiée
  à l'émission, comparée à celle du compte à chaque usage).
* Compte inactif : refusé à la connexion, au rafraîchissement et à l'accès.

Aucun secret n'est journalisé : ce module n'écrit aucun log.
"""
from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from itsdangerous import BadData, URLSafeTimedSerializer
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.device_session import DeviceSession
from app.models.user import User

PURPOSE_ACCESS = "access"
ACCESS_SALT = "auren.auth.access.v1"
ACCESS_MAX_AGE = 15 * 60
#: Un appareil inutilisé trente jours se reconnecte — la durée du cookie web.
REFRESH_IDLE_MAX = timedelta(days=30)
REFRESH_PREFIX = "rt1"
DEVICE_LABEL_MAX = 64


@dataclass(frozen=True)
class IssuedTokens:
    access_token: str
    refresh_token: str
    access_expires_in: int
    device_session_id: str


def _now() -> datetime:
    """UTC naïf : le format des colonnes de `device_sessions`."""
    return datetime.now(UTC).replace(tzinfo=None)


def _hash(secret: str) -> str:
    return hashlib.sha256(secret.encode("utf-8")).hexdigest()


def _serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(get_settings().app_secret_key, salt=ACCESS_SALT)


def _access_token(user_id: int, epoch: int, device_session_id: str) -> str:
    return _serializer().dumps({
        "purpose": PURPOSE_ACCESS, "user_id": user_id, "epoch": epoch,
        "dsid": device_session_id,
    })


def _issue(ds: DeviceSession, secret: str) -> IssuedTokens:
    return IssuedTokens(
        access_token=_access_token(ds.user_id, ds.session_epoch, ds.id),
        refresh_token=f"{REFRESH_PREFIX}.{ds.id}.{secret}",
        access_expires_in=ACCESS_MAX_AGE,
        device_session_id=ds.id,
    )


def _clean_label(label: str | None) -> str | None:
    if label is None:
        return None
    propre = " ".join(label.split())[:DEVICE_LABEL_MAX]
    return propre or None


def open_device_session(
    db: Session, user: User, *, device_label: str | None = None,
) -> IssuedTokens:
    """Crée la session d'un appareil qui vient de s'authentifier. L'appelant commite."""
    secret = secrets.token_urlsafe(32)
    now = _now()
    ds = DeviceSession(
        id=secrets.token_hex(16),
        user_id=user.id,
        refresh_hash=_hash(secret),
        session_epoch=user.session_epoch or 0,
        device_label=_clean_label(device_label),
        created_at=now,
        last_used_at=now,
    )
    db.add(ds)
    db.flush()
    return _issue(ds, secret)


def _parse_refresh(token: str) -> tuple[str, str] | None:
    parts = token.split(".", 2) if isinstance(token, str) else []
    if len(parts) != 3 or parts[0] != REFRESH_PREFIX or not parts[1] or not parts[2]:
        return None
    return parts[1], parts[2]


def _active_user(db: Session, user_id: int) -> User | None:
    return db.execute(
        select(User).where(User.id == user_id, User.is_active.is_(True))
    ).scalar_one_or_none()


def rotate_refresh(db: Session, refresh_token: str) -> IssuedTokens | None:
    """Échange un jeton de rafraîchissement contre une paire neuve, ou None.

    Un secret qui n'est pas le courant RÉVOQUE l'appareil : c'est soit un jeton
    déjà échangé — donc copié —, soit une forgerie. L'appelant commite dans les
    deux cas, sinon la révocation serait perdue.
    """
    parsed = _parse_refresh(refresh_token)
    if parsed is None:
        return None
    dsid, secret = parsed
    ds = db.get(DeviceSession, dsid)
    if ds is None or ds.revoked_at is not None:
        return None
    now = _now()
    user = _active_user(db, ds.user_id)
    if (
        user is None
        or (user.session_epoch or 0) != ds.session_epoch
        or now - ds.last_used_at > REFRESH_IDLE_MAX
    ):
        ds.revoked_at = now
        return None
    presented = _hash(secret)
    if not hmac.compare_digest(presented, ds.refresh_hash):
        ds.revoked_at = now
        return None
    # Rotation conditionnelle : deux échanges concurrents du même jeton ne
    # peuvent pas réussir tous les deux. Le perdant voit 0 ligne et révoque.
    nouveau = secrets.token_urlsafe(32)
    res = db.execute(
        update(DeviceSession)
        .where(DeviceSession.id == dsid, DeviceSession.refresh_hash == presented,
               DeviceSession.revoked_at.is_(None))
        .values(refresh_hash=_hash(nouveau), last_used_at=now)
        .execution_options(synchronize_session=False)
    )
    if res.rowcount != 1:
        db.execute(
            update(DeviceSession).where(DeviceSession.id == dsid)
            .values(revoked_at=now).execution_options(synchronize_session=False)
        )
        return None
    db.refresh(ds)
    return _issue(ds, nouveau)


def resolve_access(db: Session, token: str) -> tuple[User, DeviceSession] | None:
    """L'utilisateur et l'appareil qu'un jeton d'ACCÈS authentifie, ou None."""
    try:
        payload = _serializer().loads(token, max_age=ACCESS_MAX_AGE)
    except BadData:
        return None
    if not isinstance(payload, dict) or payload.get("purpose") != PURPOSE_ACCESS:
        return None
    user_id, epoch, dsid = payload.get("user_id"), payload.get("epoch"), payload.get("dsid")
    if not isinstance(user_id, int) or isinstance(user_id, bool):
        return None
    if not isinstance(epoch, int) or isinstance(epoch, bool):
        return None
    if not isinstance(dsid, str):
        return None
    user = _active_user(db, user_id)
    if user is None or (user.session_epoch or 0) != epoch:
        return None
    ds = db.get(DeviceSession, dsid)
    if (
        ds is None or ds.user_id != user.id or ds.revoked_at is not None
        or ds.session_epoch != epoch
    ):
        return None
    return user, ds


def revoke_device_session(ds: DeviceSession) -> None:
    """Déconnexion mobile : cet appareil seul. L'appelant commite."""
    if ds.revoked_at is None:
        ds.revoked_at = _now()
