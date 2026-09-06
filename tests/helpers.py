"""Shared test utilities."""
from __future__ import annotations

import re

# Sb_CI_02_2 — auth fast path contract, shared by conftest and its pinning tests.
#
# TEST-ONLY bcrypt hash of the literal password "testpass" (passlib, $2b$, cost 12 — the
# production default). Precomputed so the generic `client` fixture never pays the bcrypt
# hashing cost, and so the REAL login route still verifies successfully against it.
# Not a secret: it only ever lands in a throwaway per-test SQLite file.
# Pinned by tests/test_auth_fixture_fastpath.py::test_precomputed_hash_really_is_testpass.
TESTPASS_BCRYPT_HASH = "$2b$12$6EEqZ/sTvQI70mZ5iIihGu7IYM4QH/CNFuEFh5dRuhPmQV0TrMnZu"
TESTPASS_PLAIN = "testpass"


def get_test_user_id() -> int:
    """Return the id of the 'testuser' user that conftest creates.

    Call this INSIDE the test function (after the client fixture has
    run) so the DB is populated.
    """
    from sqlalchemy import select

    from app.database import SessionLocal
    from app.models.user import User

    with SessionLocal() as db:
        user = db.execute(
            select(User).where(User.username == "testuser")
        ).scalar_one()
        return user.id


def module_code_only(module) -> str:
    """Source d'un module **sans ses docstrings**.

    Plusieurs suites interdisent la présence de symboles dans le **code** —
    `MEV`, `WeeklyPlanner`, `WorkoutSession`… — tout en ayant besoin de les
    **nommer dans la documentation** pour expliquer précisément ce qui n'est pas
    fait. Un scan brut fait alors échouer un module sur sa propre docstring,
    ce qui pousse à affaiblir la garde plutôt qu'à la respecter.

    Partagé plutôt que réécrit : le motif est apparu dans trois fichiers de
    tests successifs.
    """
    import ast
    import inspect

    tree = ast.parse(inspect.getsource(module))
    for node in ast.walk(tree):
        if not isinstance(
            node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
        ):
            continue
        body = node.body
        if (
            body
            and isinstance(body[0], ast.Expr)
            and isinstance(body[0].value, ast.Constant)
            and isinstance(body[0].value.value, str)
        ):
            body.pop(0)
    return ast.unparse(tree)


#: Un commentaire CSS. Ce qu'il contient ne peint rien.
_COMMENTAIRE_CSS = re.compile(r"/\*.*?\*/", re.DOTALL)


def css_sans_commentaires(css: str) -> str:
    """Retire les commentaires d'une feuille avant de la sonder.

    ⚠ TROIS GARDES PARTAGEAIENT LE MÊME TROU, ET ONT ROUGI ENSEMBLE.

    `test_app_shell_navigation`, `test_app_shell_hardening` et
    `test_app_shell_desktop_rail` cherchent chacune une couleur en dur dans
    `app.css` — et lisaient les COMMENTAIRES comme du code. Un commentaire qui
    documentait le retrait de `#2e7d32` (`Sb_UI_PHANTOM_TOKENS_01`) les a
    toutes les trois fait échouer, dans trois shards différents.

    Un hexadécimal entre `/* */` ne peint rien : la garde condamnait la
    documentation d'un défaut corrigé. C'est la huitième occurrence relevée
    dans ce dépôt d'une sonde qui prend la prose pour du code — la précédente
    lisait la balise `<details>` comme le mot « détails ».

    La sonde est ICI, en un seul endroit, et non recopiée trois fois : trois
    copies d'une même sonde divergent, et c'est exactement le mode d'échec
    qu'elle corrige.
    """
    return _COMMENTAIRE_CSS.sub(" ", css)
