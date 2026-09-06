"""Sb_UI_05.1 — Today / Readiness Home : Home IA + Hero Decision Surface.

Verifies the home page became a mobile-first *decision surface* (Sx_UI_05
§7/§8), not a dashboard, WITHOUT removing existing home information.

Asserts:
- .today-home wrapper present
- Hero Decision Surface present with a single primary CTA
- active session dominates when an open session exists (hero--active +
  "Reprendre" + link to /sessions/{id})
- no-active-session branch renders "Démarrer une séance" CTA
- readiness teaser only appears as a qualitative marker (never a medical
  score) — and the copy carries no diagnostic/activation claim
- existing dashboard content preserved but de-prioritized under the hero
  (disponibilité KPI, nav tiles, sparkline block still present/accessible)
- no-JS: hero CTA is a plain <a> to an existing route
- home.css scoped to .today-home (no global leak), no new JS

Invariants (must NOT change):
- route "/" still serves the home
- no new route/service/model/migration
- legacy labels preserved (Historique / Progression / Programmes,
  "Démarrer une séance" | "Nouvelle séance", "disponibilit")

Reads rendered HTML + CSS/template source only — no pixels.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HOME_CSS = ROOT / "app" / "static" / "css" / "home.css"
#: `UIV3_COCKPIT_LADDER_01` (B0) — la palette `--t-*` vit désormais ici.
APP_CSS = ROOT / "app" / "static" / "css" / "app.css"
INDEX = ROOT / "app" / "templates" / "index.html"
JS_DIR = ROOT / "app" / "static" / "js"
#: La suite elle-même — balayée par `Sb_UI_JS_CAPACITY_GUARD_01` pour vérifier
#: qu'aucune garde ne réintroduit un inventaire du répertoire JS.
TESTS_DIR = ROOT / "tests"


def _uncommented(path: Path) -> str:
    """CSS sans ses commentaires.

    `test_amber_accent_present` passait sur `#C8A24B` trouvé dans le
    COMMENTAIRE d'en-tête de `home.css` — donc pour une mauvaise raison. Un
    hex cité en prose ne prouve pas qu'une couleur est déclarée.
    """
    import re as _re
    return _re.sub(r"/\*.*?\*/", "", path.read_text(encoding="utf-8"),
                   flags=_re.DOTALL).lower()


def _start_session(client, slug: str = "push-a") -> int:
    r = client.post("/sessions", data={"template_slug": slug}, follow_redirects=False)
    assert r.status_code == 303, r.text
    m = re.match(r"/sessions/(\d+)", r.headers["location"])
    assert m, r.headers["location"]
    return int(m.group(1))


def _home(client) -> str:
    r = client.get("/")
    assert r.status_code == 200, r.text[:300]
    return r.text


# ───────── IA + hero structure ─────────


class TestHomeIA:
    def test_today_home_wrapper_present(self, client):
        assert "today-home" in _home(client)

    def test_hero_present(self, client):
        assert "today-home__hero" in _home(client)

    def test_eyebrow_today_only_when_a_session_is_active(self, client):
        """Tier **T4** — `Sx_UIV3_01`, décision versionnée.

        « Aujourd'hui » n'est plus rendu sur la branche recommandée : la
        section porte désormais son propre intitulé (« Ce que disent tes
        séances »), et deux eyebrows empilés ne disent qu'une chose — que
        personne n'a relu les deux ensemble.

        Il survit pour la séance active, où il situe réellement l'objet.
        """
        assert "Aujourd'hui" not in _home(client)
        _start_session(client, "push-a")
        active = _home(client)
        assert "today-home__eyebrow" in active
        assert "Aujourd'hui" in active

    def test_single_primary_cta_in_hero(self, client):
        """Exactly one primary hero CTA. Sx_UI_06 Sb_UI_06.3 : the CTA is
        either an <a> (resume / fallback start) or a <button> in a POST form
        (start the recommended session directly). In all cases exactly one
        `today-home__cta` element carries the primary action (the optional
        `today-home__cta-form` wrapper is not counted)."""
        body = _home(client)
        # count the CTA element itself: class token followed by a quote,
        # excluding the form wrapper class `today-home__cta-form`.
        assert body.count('today-home__cta"') == 1

    def test_secondary_zone_present(self, client):
        assert "today-home__secondary-zone" in _home(client)

    def test_terminal_direction_marker(self, client):
        """Sb_UI_02b.1 — the Home carries the Auren Terminal marker class."""
        assert "today-home--terminal" in _home(client)

    def test_status_label_present_only_for_an_active_session(self, client):
        """D4 removed « Aucune séance active » — it stated nothing the CTA did not.

        The status label survives for the ACTIVE-session hero, where « Séance
        active » is real information. The fixture user has no open session, so
        the label is legitimately absent here.
        """
        body = _home(client)
        assert "Aucune séance active" not in body
        assert "today-home__hero--next" in body

    def test_action_block_present(self, client):
        assert "today-home__action" in _home(client)

    def test_the_secondary_zone_is_ranked_below_the_hero(self, client):
        """La zone secondaire reste d'un rang INFÉRIEUR au hero.

        ⚠ `Sb_UI_HOME_COCKPIT_01` — CETTE GARDE ÉPINGLAIT SON VÉHICULE.

        Elle exigeait la chaîne `today-home__summary-eyebrow` et le mot
        « Résumé ». Or l'intertitre « Résumé · indicateurs et navigation »
        décrivait la STRUCTURE du document, pas son contenu, et l'opérateur
        l'a retiré : personne n'ouvre AUREN pour chercher « des indicateurs ».

        Ce que la garde protège vraiment — la hiérarchie entre la décision et
        le reste — n'a pas disparu ; son mécanisme a changé. Il est désormais
        porté par la PROFONDEUR : le hero est le seul objet encadré de l'écran,
        les blocs de rang 2 n'ont plus de conteneur (`Q5`).

        La garde asserte donc la propriété, pas la chaîne qui la portait.
        """
        body = _home(client)
        assert "today-home__secondary-zone" in body, (
            "la zone secondaire a disparu de l'accueil"
        )
        css = HOME_CSS.read_text(encoding="utf-8")
        bloc = re.search(
            r"\.today-home \.coaching-loop \.hl-block,\s*"
            r"\.today-home \.coaching-loop \.home-wk\s*\{([^}]*)\}",
            css,
        )
        assert bloc, "les blocs de rang 2 ne sont plus stylés comme un rang"
        assert "border: none" in bloc.group(1), (
            "un bloc de rang 2 a retrouvé une bordure — il redevient une carte, "
            "et la carte cesse d'être le signal du rang 1"
        )


# ───────── Auren Terminal visual system (graphite / mono / amber) ─────────


class TestAurenTerminal:
    def test_no_teal_in_home_css(self):
        """The teal-light COLOR VALUES must be fully removed from home.css
        (the word 'teal' may still appear in a comment documenting the
        removal — we check hex tokens, i.e. the actual visual leak risk)."""
        css = HOME_CSS.read_text(encoding="utf-8").lower()
        for teal_hex in ("#0f8a85", "#0b7a75", "#095e5a", "#d4edeb"):
            assert teal_hex not in css, f"leftover teal hex {teal_hex!r} in home.css"

    def test_amber_accent_present(self):
        """L'ambre est DÉCLARÉ dans l'autorité et CONSOMMÉ par la Home.

        Tier **T4** — mis à jour par `Sx_UIV3_04 §1bis C8` (décision versionnée).
        `UIV3_COCKPIT_LADDER_01` a déplacé la déclaration de `home.css` vers
        `app.css :root` : la palette était scopée `.today-home` et donc
        inatteignable depuis la Session, ce qui rendait la convergence
        impossible à écrire.

        La garde n'est pas affaiblie, elle est **ouverte en deux** : on vérifie
        désormais la déclaration ET la consommation, là où l'ancienne version
        se contentait d'un hex qu'un commentaire suffisait à satisfaire.
        """
        assert "#c8a24b" in _uncommented(APP_CSS), (
            "amber accent #C8A24B missing from the app.css :root authority"
        )
        assert "var(--t-amber)" in _uncommented(HOME_CSS), (
            "the Home no longer consumes the amber accent"
        )

    def test_graphite_surfaces_present(self):
        """Les surfaces graphite sont déclarées, et la Home s'y pose.

        Tier **T4**, même migration que ci-dessus.
        """
        app_css = _uncommented(APP_CSS)
        assert "#0f1318" in app_css, "L1 --t-base missing from the authority"
        assert "var(--t-base)" in _uncommented(HOME_CSS), (
            "the Home no longer consumes the graphite base"
        )
        # white surface of the teal build must be gone as a hero background
        assert "--home-surface: #ffffff" not in _uncommented(HOME_CSS)

    def test_mono_typography(self):
        """The Home must use a monospace stack (terminal), not a sans stack."""
        css = HOME_CSS.read_text(encoding="utf-8").lower()
        assert "monospace" in css
        assert "ui-monospace" in css

    def test_no_webfont_import(self):
        """No @import / @font-face / external font in home.css (system mono)."""
        css = HOME_CSS.read_text(encoding="utf-8").lower()
        assert "@import" not in css
        assert "@font-face" not in css
        assert "fonts.googleapis" not in css

    def test_no_decorative_box_shadow_on_hero(self):
        """Terminal chrome: the hero uses 1px line, no decorative drop shadow."""
        css = HOME_CSS.read_text(encoding="utf-8")
        m = re.search(r"\.today-home__hero\s*\{[^}]*\}", css, re.DOTALL)
        assert m is not None
        assert "box-shadow" not in m.group(0) or "box-shadow: none" in m.group(0)


# ───────── decision model branches ─────────


class TestDecisionBranches:
    def test_no_active_session_cta_is_start(self, client):
        """Fresh client (no open session) → a start CTA. Sx_UI_06 Sb_UI_06.3 :
        with a recommendation the hero starts it directly (« Démarrer »); the
        cold-start fallback is « Démarrer une séance ». Either way it is a
        start action and the hero is not in the active state."""
        body = _home(client)
        assert "Démarrer" in body
        assert "today-home__hero--active" not in body

    def test_active_session_dominates(self, client):
        """With an open session, the hero switches to active + 'Reprendre'
        and links to /sessions/{id}."""
        sid = _start_session(client, "push-a")
        body = _home(client)
        assert "today-home__hero--active" in body
        assert "Reprendre" in body
        assert f"/sessions/{sid}" in body

    def test_active_session_cta_single(self, client):
        """Even with an active session, exactly one primary hero CTA."""
        _start_session(client, "push-a")
        body = _home(client)
        assert body.count("today-home__cta") == 1


# ───────── readiness teaser (non-medical) ─────────


class TestReadinessTeaser:
    def test_no_medical_score_claim(self, client):
        """Home copy must not present a medical/diagnostic readiness claim."""
        body = _home(client).lower()
        for forbidden in ("diagnostic médical", "activation mesurée",
                          "récupération réelle", "score médical"):
            assert forbidden not in body

    def test_readiness_teaser_removed_from_hero(self, client):
        """Sx_UI_06 Sb_UI_06.3 — the hero readiness teaser (which only said
        « détail plus bas », carrying no data) is removed. Readiness now lives
        in its single widget below the hero; no numeric medical score in the
        hero."""
        src = INDEX.read_text(encoding="utf-8")
        # teaser class gone from the hero
        assert "today-home__readiness" not in src
        # the readiness widget (self-report state) still exists
        assert "readiness-widget" in src
        assert "État du jour" in src


# ───────── dashboard preserved but de-prioritized ─────────


class TestDashboardPreserved:
    def test_disponibilite_left_the_home_but_not_the_product(self, client):
        """Tier **T4** — `Sx_UIV3_01 §7`, BLOCKER-1 tranché : **OUI**.

        Le KPI « disponibilité » quitte la surface de décision. Il n'est pas
        supprimé : `compute_behavioral_state` le calcule toujours et
        `/dashboard` le montre toujours.

        **Ce test passait pour une mauvaise raison.** Après le déplacement, il
        restait vert parce que le libellé du lien vers l'analyse contenait le
        mot « disponibilité ». Le mot suffisait ; le KPI n'était plus là.
        Corriger le libellé — la destination réelle ne porte pas ce KPI — l'a
        fait tomber, ce qui est exactement ce qu'il aurait dû faire d'emblée.

        Il vérifie désormais les deux moitiés de la décision : parti de
        l'accueil, toujours présent dans le produit.
        """
        assert "disponibilit" not in _home(client).lower(), (
            "le KPI appartient à la surface d'analyse, pas à celle de décision"
        )
        # « Déplacé, pas supprimé » se prouve au niveau du SERVICE, pas d'un mot
        # dans une page : le rendu du dashboard dépend de l'historique, et une
        # fixture vierge n'affiche rien. Une assertion sur le HTML serait donc
        # verte ou rouge selon les données — exactement le genre de test qui
        # ment plus tard.
        from app.database import SessionLocal
        from app.models.user import User
        from app.services.behavioral import compute_behavioral_state

        with SessionLocal() as db:
            user = db.query(User).first()
            state = compute_behavioral_state(db, user.id)
        assert state.readiness_score is not None, (
            "déplacé, pas supprimé — le moteur doit toujours le calculer"
        )
        assert client.get("/dashboard").status_code == 200, (
            "la surface d'analyse doit rester atteignable"
        )

    def test_nav_tiles_preserved(self, client):
        body = _home(client)
        for label in ("Historique", "Progression", "Programmes"):
            assert label in body

    def test_dashboard_below_hero(self, client):
        """Hero appears before the secondary zone in the DOM."""
        body = _home(client)
        hero = body.find("today-home__hero")
        zone = body.find("today-home__secondary-zone")
        assert hero != -1, "hero absent"
        assert zone != -1, "zone secondaire absente"
        assert hero < zone, "la décision doit précéder le contexte"

    def test_analysis_is_reachable_from_the_home(self, client):
        """Tier **T4** — `Sx_UIV3_01 §7`, BLOCKER-1 tranché : **OUI**.

        La sparkline et « séances cette sem. » quittent l'accueil pour
        `/progress` ; le score « disponibilité » vit sur `/dashboard`. Trois
        échelles d'état concurrentes vivaient sur la même page — déclarée 1–5,
        inférée en 4
        bandes, calculée 0–100 — dont aucune ne s'accordait avec les autres.

        **Rien n'est supprimé** : `compute_behavioral_state` calcule toujours,
        `/dashboard` montre toujours. C'est la surface de DÉCISION qui s'en
        sépare, pas le produit. Ce que cette garde protège désormais, c'est
        que le chemin vers l'analyse reste **à un tap**.
        """
        body = _home(client)
        assert "today-home__analysis" in body, (
            "l'analyse doit rester accessible depuis l'accueil"
        )
        assert "/progress" in body


# ───────── no-JS / no-framework ─────────


class TestNoFramework:
    def test_hero_cta_is_no_js(self, client):
        """The hero CTA must be no-JS: either a plain <a href> (resume /
        fallback) or a <button> submitting a POST form to /sessions (start
        the recommended session). Both are server-driven, no JS handler.
        Sx_UI_06 Sb_UI_06.3."""
        body = _home(client)
        anchor = re.search(r'<a class="today-home__cta"[^>]*href="[^"]+"', body)
        form_button = (
            'today-home__cta-form' in body
            and 'action="/sessions"' in body
            and re.search(r'<button[^>]*class="today-home__cta"', body) is not None
        )
        assert anchor is not None or form_button

    def test_no_script_writes_in_parallel_of_the_server(self):
        """LE SERVEUR RESTE L'UNIQUE AUTORITÉ D'ÉCRITURE — sur TOUT le répertoire.

        ⚠ CETTE GARDE ÉTAIT UN INVENTAIRE EXACT DU RÉPERTOIRE :

            assert js_files == ["prefs_focus_rank.js", "preview.js",
                                "session_focus.js"]

        Son propre commentaire reconnaissait déjà le défaut — « écrite comme un
        inventaire exact du répertoire, elle a transformé une garantie
        historique de tranche en **interdiction permanente de toute
        amélioration progressive future** » — et le conservait quand même.

        `AUREN_VISUAL_BACKBONE §5bis` a depuis fixé la doctrine :
        *SSR is the functional baseline · a critical training write must remain
        recoverable if JS fails.* Ce que le produit doit garder n'est pas un
        NOMBRE de fichiers, c'est une PROPRIÉTÉ : aucun script n'écrit en
        parallèle du serveur.

        La garde épingle donc la propriété, et sur **tout** le répertoire —
        `test_df_b_session_flow.py:69` fait de même pour un seul fichier. Un
        quatrième script est désormais permis ; un script qui persisterait
        derrière le dos du serveur ne l'est pas, et ne l'a jamais été.

        ⚠ CE N'EST PAS « AUCUN `fetch` ». Mon premier jet bannissait `fetch(`
        en bloc et a fait rougir `preview.js`, qui LIT une carte-aperçu en GET
        — il ne persiste rien. Bannir la lecture aurait interdit
        l'enrichissement que la doctrine autorise explicitement.

        L'invariant est **la mutation**, pas la requête.

        ⚠ L'implémentation vit dans `tests/helpers.py`, pas ici. Elle était
        recopiée dans QUATORZE fichiers sous sa forme d'inventaire ; la
        remplacer par quatorze copies de la nouvelle forme reproduirait
        exactement le défaut — quatorze copies d'une sonde divergent.
        """
        from tests.helpers import assert_aucune_ecriture_parallele

        assert_aucune_ecriture_parallele()

class TestGuardOfTheGuard:
    """Chaque contrôle des deux gardes partagées doit MORDRE sur son défaut.

    Une garde qui n'a jamais vu échouer son propre motif ne prouve rien. Le
    dépôt s'est déjà fait prendre : un contrôle d'URL rendu muet par un filtre
    de commentaires est passé pour une protection pendant tout le temps où il
    n'en était pas une.

    On plante donc le défaut D'ORIGINE, EN ENTIER, et on exige l'échec.

    ⚠ Ces tests exercent les MOTIFS RÉELS de `tests/helpers.py`, importés, et
    non des copies. Une copie ici garderait le souvenir de la garde, pas la
    garde — et c'est précisément le défaut que la tranche corrige.
    """

    def test_le_controle_de_mutation_mord(self):
        from tests.helpers import (
            _CANAUX_ECRITURE,
            _VERBE_MUTANT,
            js_sans_commentaires,
        )

        for defaut in (
            "fetch('/x', {method: 'POST'})",
            'fetch("/x", { method : "delete" })',
            "navigator.sendBeacon('/x', d)",
            "const w = new WebSocket('/ws')",
            "new XMLHttpRequest()",
            "EventSource('/flux')",
        ):
            src = js_sans_commentaires(defaut)
            mord = bool(_VERBE_MUTANT.search(src)) or any(
                c in src for c in _CANAUX_ECRITURE
            )
            assert mord, f"le contrôle de mutation laisse passer : {defaut}"

    def test_le_controle_de_mutation_epargne_une_lecture(self):
        """`preview.js` LIT en GET. Bannir la requête, c'est bannir la doctrine.

        Mon premier jet interdisait `fetch(` en bloc et faisait rougir un
        script qui ne persiste rien. L'invariant est la MUTATION.
        """
        from tests.helpers import _VERBE_MUTANT, js_sans_commentaires

        src = js_sans_commentaires("const r = await fetch(`/preview/${id}`);")
        assert not _VERBE_MUTANT.search(src)

    def test_le_controle_d_url_mord_malgre_le_filtre_de_commentaires(self):
        """Le défaut EXACT qui rendait la garde muette, replanté en entier."""
        from tests.helpers import _URL_CHARGEE, js_sans_blocs, js_sans_commentaires

        defaut = 'const s = "https://cdn.example.com/react.production.min.js";'
        assert "https://" not in js_sans_commentaires(defaut), (
            "le filtre a changé — relire pourquoi cette garde lit la source brute"
        )
        assert _URL_CHARGEE.search(js_sans_blocs(defaut)), (
            "le contrôle d'URL ne mord pas sur un CDN en clair"
        )

    def test_le_controle_d_url_epargne_une_url_en_commentaire(self):
        """Citer une URL dans une phrase n'est pas charger une dépendance."""
        from tests.helpers import _URL_CHARGEE, js_sans_blocs

        cite = "// voir https://developer.mozilla.org/fetch pour le détail"
        assert not _URL_CHARGEE.search(js_sans_blocs(cite))

    def test_le_controle_d_import_mord(self):
        from tests.helpers import _IMPORT_MODULE, js_sans_blocs

        for defaut in (
            "import { h } from 'preact';",
            "const x = require('lodash');",
            "import 'chart.js';",
        ):
            assert _IMPORT_MODULE.search(js_sans_blocs(defaut)), (
                f"import non vu : {defaut}"
            )

    def test_plus_aucune_garde_du_depot_n_epingle_l_inventaire_js(self):
        """LA FAMILLE ENTIÈRE, ou la tranche n'a rien levé.

        Quatorze fichiers portaient la comparaison de liste. En corriger UN
        laissait treize verrous en place et un rapport qui annonçait le
        contraire — le mode d'échec « famille aux deux tiers », dans sa forme
        la plus nette : le commentaire du défaut était lui-même recopié
        quatorze fois.

        La garde balaye par CLASSE (tout `tests/*.py`), jamais par
        énumération : une liste écrite à la main reproduirait l'oubli.
        """
        import ast

        coupables = []
        for f in sorted(TESTS_DIR.rglob("test_*.py")):
            txt = f.read_text(encoding="utf-8")
            if 'glob("*.js")' not in txt:
                continue
            for n in ast.walk(ast.parse(txt)):
                if not isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                seg = ast.get_source_segment(txt, n) or ""
                if 'glob("*.js")' not in seg:
                    continue
                # Un inventaire compare la LISTE ou l'ENSEMBLE des noms de
                # fichiers à une constante. Une garde de propriété, non.
                for a in ast.walk(n):
                    if not isinstance(a, ast.Compare):
                        continue
                    if not any(
                        isinstance(o, (ast.Eq, ast.LtE, ast.Lt)) for o in a.ops
                    ):
                        continue
                    cible = ast.unparse(a)
                    if any(
                        js in cible
                        for js in ("preview.js", "session_focus.js",
                                   "prefs_focus_rank.js")
                    ):
                        coupables.append(f"{f.name}::{n.name} — {cible[:70]}")

        assert not coupables, (
            "des gardes épinglent encore l'INVENTAIRE du répertoire JS au lieu "
            "de la propriété :\n  " + "\n  ".join(coupables)
        )


class TestNoFrameworkVendored:
    def test_no_framework_is_vendored(self):
        """« Zéro framework » est une décision DISTINCTE de la doctrine JS.

        `§5bis` lève « sans JavaScript » ; il ne lève pas celle-ci.
        Implémentation partagée — voir `tests/helpers.py`.
        """
        from tests.helpers import assert_aucun_framework

        assert_aucun_framework()

    def test_no_react_marker(self, client):
        body = _home(client)
        for marker in ("data-reactroot", "__NEXT_DATA__", "ReactDOM", "/_next/"):
            assert marker not in body


# ───────── CSS presence (scoped) ─────────


class TestHomeCss:
    def test_css_defines_today_home(self):
        assert ".today-home" in HOME_CSS.read_text(encoding="utf-8")

    def test_css_defines_hero(self):
        assert ".today-home__hero" in HOME_CSS.read_text(encoding="utf-8")

    def test_css_defines_cta(self):
        assert ".today-home__cta" in HOME_CSS.read_text(encoding="utf-8")

    def test_css_cta_meets_tap_target(self):
        """Primary CTA must reserve a ≥44px tap target."""
        css = HOME_CSS.read_text(encoding="utf-8")
        m = re.search(r"\.today-home__cta\s*\{[^}]*\}", css, re.DOTALL)
        assert m is not None
        assert re.search(r"min-height:\s*(4[4-9]|[5-9]\d)px", m.group(0))

    def test_css_scoped_to_today_home(self):
        """Every rule must be scoped under .today-home (no bare global
        element selectors introduced for home)."""
        css = HOME_CSS.read_text(encoding="utf-8")
        # crude scope check: every selector block references today-home,
        # a media query, or a comment — no bare "body {" / "a {" leak.
        for bad in ("\nbody {", "\nhtml {", "\na {", "\np {", "\ndiv {"):
            assert bad not in css, f"unscoped global selector {bad!r} in home.css"

    def test_home_loads_home_css(self):
        """index.html must load home.css via extra_head."""
        src = INDEX.read_text(encoding="utf-8")
        assert "css/home.css" in src
