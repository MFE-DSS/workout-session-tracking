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
templates.env.filters["local"] = to_local
templates.env.filters["local_weekday"] = local_weekday_iso

# `STATIC_ASSET_COHERENCE_01` — L'AUTORITÉ D'URL DES ASSETS MUTABLES.
#
# Les gabarits appellent `asset_url('js/session_focus.js')` et jamais
# `url_for('static', …)` pour une feuille ou un script : l'URL nue est
# dépourvue d'empreinte, donc un client peut conserver un ancien fichier
# pendant que le HTML arrive à jour. Ce couplage rompu a été REPRODUIT — il ne
# reste pas une hypothèse (cf. `SPRINT_STATIC_ASSET_COHERENCE_01_REPORT`).
templates.env.globals["asset_url"] = asset_url
