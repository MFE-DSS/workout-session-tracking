"""Un lien du produit vise une route actuelle, jamais une route héritée.

POURQUOI CETTE GARDE EXISTE
---------------------------
Deux occurrences, trouvées à trois semaines d'écart et sur deux surfaces :

* `session_done.html` — le CTA primaire de fin de séance pointe vers
  `/dashboard`, **route dépréciée** qui répond `303` vers `/progress` ;
* `session_detail.html` — « Voir toutes les règles » pointait vers `/rules`,
  qui répond **301** vers `/science`.

**Deux occurrences font un motif, pas un accident.** Une route héritée survit
pour les signets externes — c'est légitime, et aucune n'est supprimée ici. Ce
qui ne l'est pas, c'est qu'un lien du produit la traverse : l'utilisateur paie
un aller-retour réseau, et le code laisse croire que la destination est encore
là où elle n'est plus.

⚠ `R-03` n'est PAS corrigé par cette tranche : la destination après une séance
est un arbitrage ouvert (accueil ? progression ? rien ?), pas un correctif.
Son entrée est donc INSCRITE avec sa raison plutôt que la garde affaiblie —
et c'est elle qui rendra le jour où l'arbitrage tombe.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = ROOT / "app" / "templates"

#: Routes qui existent UNIQUEMENT pour les signets externes. Elles répondent
#: par une redirection ; aucun lien interne ne doit y mener.
LEGACY_ROUTE_NAMES = {
    "dashboard": "301/303 → /progress (déprécié par `Sb_27.6`)",
    "rules_page": "301 → /science (fusionné avec Science)",
}

#: Dérogations, chacune avec sa raison et sa condition de sortie.
#: Une dérogation sans date de péremption est une permission permanente.
KNOWN_TRAVERSALS = {
    ("session_done.html", "dashboard"): (
        "`R-03` — la destination après une séance est un ARBITRAGE ouvert "
        "(accueil ? progression ? aucune ?), pas un correctif. Sortir de "
        "cette liste le jour où l'opérateur tranche."
    ),
    ("dashboard.html", "dashboard"): (
        "TROISIÈME OCCURRENCE, trouvée par cette garde même. C'est un "
        "auto-lien DANS le gabarit déprécié : `/dashboard` redirige, donc "
        "`dashboard.html` n'est jamais rendu en production. Le gabarit et "
        "`compute_dashboard` sont conservés sous garde (huit fichiers de "
        "tests en dépendent) ; les remuer pour effacer du code mort "
        "n'apporterait rien. Sortir de cette liste le jour où le gabarit "
        "part."
    ),
}


def _templates() -> list[Path]:
    return sorted(TEMPLATES.rglob("*.html"))


def _traversals() -> set[tuple[str, str]]:
    found = set()
    for tpl in _templates():
        src = re.sub(r"\{#.*?#\}", "", tpl.read_text(encoding="utf-8"), flags=re.DOTALL)
        for name in LEGACY_ROUTE_NAMES:
            if re.search(rf"url_for\(\s*['\"]{re.escape(name)}['\"]", src):
                found.add((tpl.name, name))
    return found


def test_the_probe_reads_actual_templates():
    """Garde de la garde : sans gabarits lus, tout passerait à vide."""
    tpls = _templates()
    assert len(tpls) > 20, f"seulement {len(tpls)} gabarits lus — chemin suspect"
    joined = "".join(t.read_text(encoding="utf-8") for t in tpls)
    assert "url_for(" in joined, "aucun `url_for` trouvé — le parcours a dérivé"


def test_no_new_internal_link_traverses_a_legacy_redirect():
    """Le CLIQUET. Toute traversée neuve échoue ici.

    Se contenter d'interdire `rules_page` aurait protégé un cas ; ce qui est
    gardé est le MOTIF — aucun lien interne vers une route qui redirige.
    """
    new = sorted(_traversals() - set(KNOWN_TRAVERSALS))
    assert not new, (
        "des liens internes traversent une redirection héritée : "
        + " · ".join(
            f"{tpl} → {name} ({LEGACY_ROUTE_NAMES[name]})" for tpl, name in new
        )
        + ". Viser la route actuelle, ou inscrire la dérogation avec sa raison."
    )


def test_the_traversal_exemptions_do_not_rot():
    """Une dérogation pour un cas disparu autorise d'avance un cas futur."""
    stale = sorted(set(KNOWN_TRAVERSALS) - _traversals())
    assert not stale, (
        f"dérogations périmées : {stale} — les retirer."
    )


@pytest.mark.parametrize("name", sorted(LEGACY_ROUTE_NAMES))
def test_the_legacy_routes_still_exist(name):
    """Elles ne sont PAS supprimées, et c'est délibéré.

    Un signet externe vers `/rules` doit continuer d'atterrir. Cette garde
    empêche qu'on « nettoie » la route en croyant bien faire — ce qui
    casserait des liens que le produit ne contrôle pas.
    """
    from app.main import app

    routes = {getattr(r, "name", None) for r in app.routes}
    assert name in routes, (
        f"la route héritée `{name}` a disparu — les signets externes qui la "
        "visent tombent désormais en 404"
    )
