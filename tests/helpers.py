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


def js_sans_commentaires(js: str) -> str:
    """Un script SANS ses commentaires, avant toute recherche de chaîne.

    Même raison que pour le CSS ci-dessous, et le dépôt s'y est fait prendre
    plusieurs fois : une garde qui lit sa propre prose ne garde rien. Un script
    qui documente « ici on n'utilise SURTOUT PAS `fetch(` » ferait rougir la
    garde qui bannit `fetch(`.

    ⚠ Volontairement naïf sur un point : `//` est retiré jusqu'à la fin de
    ligne, y compris s'il vit dans une chaîne (`"https://…"`). C'est le bon
    sens de l'erreur pour une garde — on retire trop, jamais trop peu.
    """
    js = re.sub(r"/\*[\s\S]*?\*/", " ", js)
    return "\n".join(ligne.split("//", 1)[0] for ligne in js.splitlines())


#: Le répertoire des scripts du produit.
_JS_DIR = (
    __import__("pathlib").Path(__file__).resolve().parent.parent
    / "app" / "static" / "js"
)

#: Une requête qui MUTE — quelle que soit sa forme d'écriture.
_VERBE_MUTANT = re.compile(r"""method\s*:\s*['"](POST|PUT|PATCH|DELETE)['"]""", re.I)

#: Les canaux qui persistent ou poussent sans passer par un formulaire.
_CANAUX_ECRITURE = (
    "navigator.sendBeacon", "axios", "new WebSocket",
    "EventSource(", "XMLHttpRequest",
)

#: Une URL **dans une chaîne**, donc chargée, et non citée dans une phrase.
_URL_CHARGEE = re.compile(r"""['"`]\s*https?://""")

#: Un import de module, quelle que soit sa forme.
_IMPORT_MODULE = re.compile(r"""(^|\s)(import\s|require\s*\()|(\sfrom\s+['"])""", re.M)


def js_sans_blocs(js: str) -> str:
    """Retire les commentaires `/* */` SEULEMENT, jamais les `//`.

    `js_sans_commentaires()` retire aussi les `//`, ce qui **décapite les URL** :
    `"https://cdn/react.js"` y devient `"https:`. Une garde qui interdit
    `https://` et lit cette sortie ne peut jamais se déclencher — mesuré.

    Ici on garde la ligne entière ; c'est `_URL_CHARGEE` qui distingue une URL
    *chargée* (précédée d'un guillemet) d'une URL *citée* dans une phrase.
    """
    return re.sub(r"/\*[\s\S]*?\*/", " ", js)


def assert_aucune_ecriture_parallele() -> None:
    """LE SERVEUR RESTE L'UNIQUE AUTORITÉ D'ÉCRITURE — sur TOUT le répertoire.

    ⚠ CETTE ASSERTION REMPLACE QUATORZE INVENTAIRES DE RÉPERTOIRE.

    Quatorze fichiers de tests portaient, chacun pour sa propre tranche, la
    même garantie historique écrite comme un **inventaire exact** :

        assert js_files == ["prefs_focus_rank.js", "preview.js",
                            "session_focus.js"]
        assert existing <= {"prefs_focus_rank.js", ...}

    Sous les deux formes, un quatrième script faisait échouer la suite. Le
    dépôt le savait : le commentaire de l'une d'elles disait déjà qu'« écrite
    comme un inventaire exact, elle a transformé une garantie historique de
    tranche en **interdiction permanente de toute amélioration progressive
    future** ». Le diagnostic était juste et n'a jamais été suivi d'effet —
    on ajoutait simplement le nouveau nom aux quatorze listes.

    `AUREN_VISUAL_BACKBONE §5bis` fixe la doctrine :
    *SSR is the functional baseline · a critical training write must remain
    recoverable if JS fails.* Ce que le produit garde n'est pas un NOMBRE de
    fichiers, c'est une PROPRIÉTÉ.

    ⚠ CE N'EST PAS « AUCUN `fetch` ». Un premier jet bannissait `fetch(` en
    bloc et faisait rougir `preview.js`, qui LIT un aperçu en GET sans rien
    persister. Bannir la lecture aurait interdit l'enrichissement que la
    doctrine autorise explicitement. **L'invariant est la mutation.**

    Implémentée ICI, une seule fois. Quatorze copies d'une même sonde
    divergent — c'est le mode d'échec qu'elle corrige.
    """
    scripts = sorted(_JS_DIR.glob("*.js"))
    assert scripts, f"aucun script dans {_JS_DIR} — la garde ne mesure rien"

    for p in scripts:
        src = js_sans_commentaires(p.read_text(encoding="utf-8"))
        trouve = _VERBE_MUTANT.search(src)
        assert not trouve, (
            f"{p.name} émet une requête mutante « {trouve.group(0)} » — une "
            "écriture d'entraînement ne doit jamais dépendre du client "
            "(AUREN_VISUAL_BACKBONE §5bis)"
        )
        for interdit in _CANAUX_ECRITURE:
            assert interdit not in src, (
                f"{p.name} ouvre un canal d'écriture parallèle « {interdit} »"
            )


def assert_aucun_framework() -> None:
    """« Zéro framework » est une décision DISTINCTE de la doctrine JS.

    `§5bis` lève « sans JavaScript » ; il ne lève pas celle-ci. Un script du
    produit ne charge rien depuis l'extérieur et n'importe aucun module.

    ⚠ Lit la source privée de ses seuls blocs `/* */` — voir `js_sans_blocs`.
    """
    scripts = sorted(_JS_DIR.glob("*.js"))
    assert scripts, f"aucun script dans {_JS_DIR} — la garde ne mesure rien"

    for p in scripts:
        src = js_sans_blocs(p.read_text(encoding="utf-8"))
        url = _URL_CHARGEE.search(src)
        assert not url, (
            f"{p.name} charge une ressource externe « {url.group(0)} » — "
            "AUREN est sans framework et sans CDN"
        )
        mod = _IMPORT_MODULE.search(src)
        assert not mod, (
            f"{p.name} importe un module « {mod.group(0).strip()} » — les "
            "scripts du produit sont autonomes"
        )


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
