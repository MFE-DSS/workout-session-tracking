"""Single Jinja2Templates instance shared across routers.

Adds a `local` Jinja filter that converts a UTC-aware datetime to the
application default timezone (DEFAULT_TIMEZONE, Europe/Paris). Storage
stays UTC; only the display layer converts.

The filter tolerates naive datetimes by assuming UTC — SQLite may round-
trip `DateTime(timezone=True)` columns as naive on some drivers.
"""
from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from fastapi.templating import Jinja2Templates

from app.config import BASE_DIR, DEFAULT_TIMEZONE
from app.services.static_assets import asset_url
from app.services.time_format import format_date_short, format_datetime_short

_DEFAULT_TZ = ZoneInfo(DEFAULT_TIMEZONE)


def to_local(dt: datetime | None) -> datetime | None:
    """Convert a datetime to the default timezone (Europe/Paris).

    - None → None (template should guard with `{% if ... %}`)
    - Naive datetime → assume UTC (SQLite roundtrip safety)
    - Aware datetime → astimezone conversion
    """
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(_DEFAULT_TZ)


def local_weekday_iso(dt: datetime | None) -> int | None:
    """ISO weekday (1=Mon..7=Sun) in the user's local timezone."""
    local = to_local(dt)
    if local is None:
        return None
    return local.isoweekday()


templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))
def date_fr(dt: datetime | None) -> str:
    """« Sam 05/09 » — la date d'un coup d'œil, en français.

    `Sb_UI_HISTORIQUE_01` — L'HISTORIQUE RENDAIT SES JOURS EN ANGLAIS.
    Il appelait `strftime('%a %d/%m %H:%M')`, et `%a` rend l'abréviation de la
    locale du PROCESSUS : « Sat 05/09 07:54 », dix fois par écran, dans une
    interface française.

    Les pièces existaient pourtant toutes les deux — le filtre `local_weekday`
    juste au-dessus, et la table `WEEKDAY_LABELS`. Aucune n'était atteignable
    depuis un gabarit sans les connaître. Ce filtre les réunit pour que la
    prochaine surface n'ait plus de raison d'écrire sa propre version.

    Localise avant de formater : formater un UTC brut décalerait le jour de la
    semaine d'un cran une nuit sur deux.
    """
    return format_date_short(to_local(dt))


def datetime_fr(dt: datetime | None) -> str:
    """« Sam 05/09 07:54 » — quand l'heure borne quelque chose.

    Distincte de `date_fr` pour une raison de sens, pas de commodité : sur le
    récap d'une séance, l'heure de début borne la séance avec celle de fin.
    Sur une liste d'historique, elle n'est jamais relue.
    """
    return format_datetime_short(to_local(dt))


templates.env.filters["local"] = to_local
templates.env.filters["local_weekday"] = local_weekday_iso
templates.env.filters["date_fr"] = date_fr
templates.env.filters["datetime_fr"] = datetime_fr

# `STATIC_ASSET_COHERENCE_01` — L'AUTORITÉ D'URL DES ASSETS MUTABLES.
#
# Les gabarits appellent `asset_url('js/session_focus.js')` et jamais
# `url_for('static', …)` pour une feuille ou un script : l'URL nue est
# dépourvue d'empreinte, donc un client peut conserver un ancien fichier
# pendant que le HTML arrive à jour. Ce couplage rompu a été REPRODUIT — il ne
# reste pas une hypothèse (cf. `SPRINT_STATIC_ASSET_COHERENCE_01_REPORT`).
templates.env.globals["asset_url"] = asset_url
