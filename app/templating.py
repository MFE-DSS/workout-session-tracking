"""Single Jinja2Templates instance shared across routers."""
from __future__ import annotations

from fastapi.templating import Jinja2Templates

from app.config import BASE_DIR

templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))
