"""Tiny time-formatting helpers shared by the session views.

SQLite-safe: handles the "stored-as-naive" quirk by coercing both
operands to the same tz frame before subtraction.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

#: Les jours de la semaine, en français, indexés ISO (1 = lundi).
#:
#: `Sb_UI_HISTORIQUE_01` — PROMUS DEPUIS `routers/sessions.py`. Ils y vivaient,
#: avec un unique consommateur, et un routeur n'est pas un endroit où loger le
#: vocabulaire d'un produit : rien ne signalait leur existence à qui écrivait un
#: autre gabarit. L'historique a donc écrit sa propre version, en appelant
#: `strftime('%a …')` — qui rend la locale du PROCESSUS, c'est-à-dire l'anglais.
#: « Sat 05/09 », dix fois par écran, dans une interface française.
WEEKDAY_LABELS: dict[int, str] = {
    1: "Lundi",
    2: "Mardi",
    3: "Mercredi",
    4: "Jeudi",
    5: "Vendredi",
    6: "Samedi",
    7: "Dimanche",
}

#: Les mêmes, abrégés — DÉRIVÉS, jamais recopiés. Une seconde table à la main
#: divergerait de la première au premier ajout, et c'est exactement la faute que
#: cette tranche corrige ailleurs.
WEEKDAY_SHORT: dict[int, str] = {k: v[:3] for k, v in WEEKDAY_LABELS.items()}


def format_date_short(dt: datetime | None) -> str:
    """« Sam 05/09 » — jour abrégé en français, sans l'heure.

    L'heure de DÉBUT ne survit pas au tri : sur une liste d'historique, personne
    ne relit à quelle minute il a commencé il y a trois semaines. Le jour de la
    semaine, lui, porte l'habitude d'entraînement — c'est la seule chose que la
    date brute ne donne pas d'un coup d'œil.

    ⚠ Attend un datetime DÉJÀ localisé (filtre `| local`). Formater un UTC brut
    décalerait le jour de la semaine d'un cran une nuit sur deux.
    """
    if dt is None:
        return "—"
    return f"{WEEKDAY_SHORT[dt.isoweekday()]} {dt.strftime('%d/%m')}"


def format_datetime_short(dt: datetime | None) -> str:
    """« Sam 05/09 07:54 » — la même, quand l'heure porte du sens.

    Deux formes, et la distinction est un choix, pas une commodité :

    * sur une LISTE d'historique, l'heure de début ne se relit jamais —
      `format_date_short` la retire ;
    * sur le RÉCAP d'une séance, elle borne la séance (« 07:54 → 08:46 ») :
      la retirer effacerait l'information même du bloc.

    Dérivée de l'autre, jamais recopiée : le jour reste écrit à un seul endroit.
    """
    if dt is None:
        return "—"
    return f"{format_date_short(dt)} {dt.strftime('%H:%M')}"


def _coerce(dt: datetime, ref: datetime) -> datetime:
    if dt.tzinfo is None and ref.tzinfo is not None:
        return dt.replace(tzinfo=ref.tzinfo)
    if ref.tzinfo is None and dt.tzinfo is not None:
        return dt  # caller's `ref` will be coerced elsewhere
    return dt


def session_duration(
    start: datetime,
    end: Optional[datetime] = None,
    *,
    now: Optional[datetime] = None,
) -> timedelta:
    """Duration of a session. `end` trumps `now`; `now` is used for
    in-progress sessions."""
    now = now or datetime.now(timezone.utc)
    target = end if end is not None else now
    start_c = _coerce(start, target)
    target_c = _coerce(target, start_c)
    return target_c - start_c


#: Au-delà, on cesse de compter en heures. Une séance ne dure pas un jour ;
#: passé ce seuil, la durée ne décrit plus un effort mais un OUBLI.
_HOURS_CEILING = 24


def format_duration_short(delta: timedelta) -> str:
    """Compact duration for mobile display.

      < 1 h      -> "{m} min" (including 0 min for < 60 s)
      < 24 h     -> "{h} h {mm:02d}"
      otherwise  -> "{d} j"

    ⚠ POURQUOI LE PLAFOND EXISTE. Cette fonction n'en avait pas, et l'accueil
    affichait **« En cours · depuis 1502 h 16 »** sur une séance laissée
    ouverte 62 jours. Le format était juste et le nombre exact ; ce qu'il
    disait ne se lisait pas.

    Le défaut n'était pas dans l'arithmétique mais dans la PORTÉE : la
    fonction est écrite pour une durée de séance — quelques dizaines de
    minutes — et rien ne l'empêchait d'être appelée hors de ce domaine. Un
    formateur sans borne finit toujours par en sortir.

    Passé 24 h on rend des JOURS. C'est moins précis et c'est le but : à ce
    stade la minute n'informe personne, et « 62 j » se lit d'un coup d'œil là
    où « 1502 h 16 » demande un calcul.

    No characters that would be HTML-escaped. Safe to substring-
    match in assertions.
    """
    total_seconds = max(int(delta.total_seconds()), 0)
    minutes = total_seconds // 60
    hours, minutes = divmod(minutes, 60)
    if hours >= _HOURS_CEILING:
        return f"{hours // 24} j"
    if hours == 0:
        return f"{minutes} min"
    return f"{hours} h {minutes:02d}"


def relative_hours_ago(now: datetime, then: datetime) -> str:
    """Compact 'how long ago' label down to the minute.

    Used by /export and /healthz/strict to surface backup file age
    in plain French. Sub-minute deltas show as "à l'instant", to
    avoid noisy sub-second strings on freshly-written files.
    """
    if then.tzinfo is None and now.tzinfo is not None:
        then = then.replace(tzinfo=now.tzinfo)
    elif now.tzinfo is None and then.tzinfo is not None:
        now = now.replace(tzinfo=then.tzinfo)

    delta_sec = max((now - then).total_seconds(), 0.0)
    if delta_sec < 60:
        return "à l'instant"
    if delta_sec < 3600:
        return f"il y a {int(delta_sec // 60)} min"
    if delta_sec < 86400:
        return f"il y a {int(delta_sec // 3600)} h"
    days = int(delta_sec // 86400)
    if days == 1:
        return "hier"
    if days < 30:
        return f"il y a {days} j"
    return f"il y a {days // 30} mois"
