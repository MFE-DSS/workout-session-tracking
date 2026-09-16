"""Sx_LIB_01 → `UI-CP4 LOADOUT` — la sémantique d'action du registre.

CE QUE CE FICHIER GARDAIT, ET CE QU'IL GARDE ENCORE
----------------------------------------------------
`Sx_LIB_01` avait sorti le formulaire de démarrage de l'intérieur du lien de
détail : imbriquer l'un dans l'autre est du HTML invalide, et les hacks
`stopPropagation` qui en découlaient étaient la rançon de cette faute.

`UI-CP4` supprime les cartes de cette surface. **La propriété protégée, elle,
ne change pas** — elle se renforce : sur un registre, aucun formulaire n'est
imbriqué dans un lien parce qu'aucun formulaire ne partage sa ligne avec un
lien de navigation. Les gardes sont donc REPOINTÉES sur la propriété, pas
supprimées avec l'écriture qu'elles épinglaient.

⚠ LE CONTRAT DE DÉMARRAGE NE VIT PLUS SUR LA PAGE FERMÉE. Une ligne sélectionne
et ne démarre pas ; la commande n'apparaît que dans le dépli. Les gardes du
contrat déplient donc explicitement une ligne — les écrire sur la page fermée
les rendrait vertes sur un écran qui ne contient plus rien à vérifier.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIBRARY_TPL = ROOT / "app" / "templates" / "library.html"
PAGES_ROUTER = ROOT / "app" / "routers" / "pages.py"

#: La clé de dépli d'un gabarit de catalogue — `app.services.loadout.session_key`.
PUSH_A = "t-push-a"


def _render(client, query: str = ""):
    r = client.get("/library" + query, follow_redirects=False)
    assert r.status_code == 200, r.text[:300]
    return r.text


# ───────── 1. le registre rend des lignes, et AUCUNE carte ─────────


def test_loadout_renders_rows(client):
    html = _render(client)
    assert "loadout__row" in html
    assert "loadout__handle" in html


def test_no_card_survives_on_loadout(client):
    """La carte n'est pas allégée : elle n'existe plus sur cette surface.

    Elle reste vivante ailleurs (`launcher`, `template_detail`) — c'est bien
    une tranche de surface, pas une migration globale de composants.
    """
    html = _render(client)
    assert "template-card" not in html
    assert "card-stack" not in html


def test_each_row_reaches_its_detail(client):
    """Voir le détail reste atteignable — depuis le dépli, pas depuis la ligne."""
    html = _render(client, f"?loadout={PUSH_A}")
    assert "/library/push-a" in html


# ───────── 2. LA PROPRIÉTÉ HISTORIQUE : aucun formulaire dans un lien ─────────


def test_no_form_nested_inside_any_link(client):
    """Élargie : plus seulement « pas dans une carte », mais dans AUCUN lien.

    L'ancienne garde ne regardait que `template-card__link`. Sur une surface
    qui n'a plus de carte, elle serait passée au vert sans rien observer — la
    forme exacte d'une garde qui ne garde plus rien.
    """
    html = _render(client, f"?loadout={PUSH_A}")
    links = re.findall(r"<a\b.*?</a>", html, re.DOTALL)
    assert links, "aucun lien rendu — la garde n'observerait rien"
    for link in links:
        assert "<form" not in link, "un formulaire est imbriqué dans un lien"


def test_stop_propagation_hacks_removed(client):
    """Les hacks `stopPropagation` restent absents du rendu."""
    html = _render(client, f"?loadout={PUSH_A}")
    assert "stopPropagation" not in html
    assert "onclick=" not in html
    assert "onkeydown=" not in html


def test_source_template_has_no_inline_handlers():
    src = LIBRARY_TPL.read_text(encoding="utf-8")
    for line in src.splitlines():
        if line.strip().startswith("{#"):
            continue
        assert "onclick=" not in line
        assert "onkeydown=" not in line
        assert "stopPropagation();" not in line


# ───────── 3. le contrat de démarrage est préservé ─────────


def test_start_form_contract_preserved(client):
    """`template_slug` + `creation_source=library` — un contrat, pas un détail."""
    html = _render(client, f"?loadout={PUSH_A}")
    assert 'name="template_slug"' in html
    assert 'name="creation_source"' in html
    assert 'value="library"' in html
    assert ">Démarrer<" in html


def test_the_closed_register_offers_no_start_at_all(client):
    """LE DÉMARRAGE ACCIDENTEL EST STRUCTURELLEMENT IMPOSSIBLE.

    Treize boutons « Démarrer » étaient visibles d'un coup ; un pouce qui
    glissait lançait une séance. Le registre fermé n'en expose aucun.
    """
    html = _render(client)
    assert ">Démarrer<" not in html
    assert 'name="template_slug"' not in html


def test_exactly_one_start_command_when_one_row_is_open(client):
    """Un seul propriétaire d'action sur l'écran, jamais deux."""
    html = _render(client, f"?loadout={PUSH_A}")
    assert html.count('name="template_slug"') == 1


def test_no_js_added():
    src = LIBRARY_TPL.read_text(encoding="utf-8")
    assert "<script" not in src


def test_cta_still_creates_session(client):
    r = client.post(
        "/sessions",
        data={"template_slug": "push-a", "creation_source": "library"},
        follow_redirects=False,
    )
    assert r.status_code in (200, 303), r.text[:200]


# ───────── 4. vocabulaire ─────────


def test_loadout_vocabulary(client):
    html = _render(client)
    # La page absorbe « Mes programmes » ; elle EST le domaine et porte son nom.
    assert "Programmes" in html
    assert "Programmes de séance" not in html
    assert "Bibliothèque" not in html


def test_pages_router_carries_no_sprint_marker():
    src = PAGES_ROUTER.read_text(encoding="utf-8")
    assert "Sx_LIB_01" not in src
