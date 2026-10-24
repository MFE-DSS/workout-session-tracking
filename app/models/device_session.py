"""`D9` — la session d'appareil : l'identité serveur d'une application installée.

POURQUOI UNE TABLE, ET PAS SEULEMENT L'ÉPOQUE DE `A0`
--------------------------------------------------------
`users.session_epoch` révoque TOUT d'un coup : c'est la bonne réponse à un
changement de mot de passe, et la mauvaise à « je me déconnecte de ce
téléphone ». Deux exigences de `D9` n'ont aucune expression sans état serveur
par appareil :

* la déconnexion mobile révoque **sa** session d'appareil, et elle seule ;
* un jeton de rafraîchissement **déjà échangé** ne doit plus rien ouvrir.
  Un jeton signé sans état reste valide jusqu'à son expiration ; seul un
  condensat courant, remplacé à chaque rotation, rend l'ancien inerte.

CE QUE LA LIGNE PORTE
-----------------------
Une ligne par connexion d'un appareil. La rotation REMPLACE le condensat en
place : la ligne est la famille de jetons, il n'y a donc pas de colonne
`family_id` (`§8.9` en prévoyait une ; une ligne par rotation n'apportait que
de la croissance). Présenter un secret qui n'est pas le courant révoque la
ligne : c'est la détection de réutilisation.

Le secret n'est JAMAIS stocké, seulement son condensat SHA-256. Il est tiré de
`secrets` (256 bits) : un condensat lent n'ajouterait rien contre une recherche
exhaustive impossible, et coûterait à chaque rafraîchissement.

`session_epoch` recopie l'époque `A0` du compte à l'émission. Toute révocation
globale — changement ou réinitialisation du mot de passe, déconnexion web —
rend donc la ligne inutilisable sans qu'aucun appelant de `revoke_sessions`
ait à la connaître.

Horodatages en UTC naïf, comme `recommendation_episodes` : SQLite rend des
`datetime` naïfs, et un mélange naïf/conscient lève à la comparaison.
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class DeviceSession(Base):
    """Une application connectée. Révocable seule, ou avec tout le compte."""

    __tablename__ = "device_sessions"

    #: Identifiant public, aléatoire, porté par les jetons. Ce n'est pas un
    #: secret : seul le condensat du secret de rafraîchissement en est un.
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    refresh_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    session_epoch: Mapped[int] = mapped_column(Integer, nullable=False)
    device_label: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.current_timestamp())
    last_used_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
