"""Quand un moyen existe, un gabarit ne le réinvente pas à côté.

Ce dépôt a un diagnostic qui revient : *le produit ne manque presque jamais de
la décision, il manque du moyen de l'appliquer.* Quand le moyen finit par
exister — un filtre, une table de libellés —, rien n'empêche la surface
suivante de le contourner. C'est ce que gardent ces tests.

Deux contrats, tous deux nés d'un défaut vu à l'écran :

* **les nombres** — le produit écrivait les décimales en français avec TROIS
  orthographes différentes, et une quatrième surface, le classement de squad,
  n'avait rien du tout : « 586.0 pts » à côté d'un « 75,6 kg » correct. Deux
  des trois orthographes venaient de moi ;
* **les rôles** — `owner` et `member` atteignaient l'écran bruts, sur deux
  gabarits. Le récap de séance avait fermé exactement ce défaut pour trois
  autres énumérations, et la surface SOCIALE avait été oubliée. C'est le mode
  d'échec consigné sous *une décision appliquée là où c'était commode* : elle
  tombe sur les surfaces sociales.
"""
from __future__ import annotations

import re
from pathlib import Path

GABARITS = Path(__file__).resolve().parents[1] / "app" / "templates"

#: Les écritures artisanales de la virgule décimale, telles qu'elles existaient.
_VIRGULE_ARTISANALE = re.compile(r"""replace\(\s*["']\.["']\s*,\s*["'],["']\s*\)""")

#: Un rendu de `.role` — `{{ item.role }}`, `{{ m.role }}` — hors comparaison.
_ROLE_RENDU = re.compile(r"\{\{[^}]*\.role\b[^}]*\}\}")


def _gabarits() -> list[Path]:
    return sorted(GABARITS.rglob("*.html"))


def test_aucun_gabarit_ne_refait_la_virgule_decimale_a_la_main():
    """`nombre_fr` existe : personne ne réécrit `replace(".", ",")`.

    Trois orthographes coexistaient pour la même conversion. Une quatrième
    surface l'avait simplement oubliée. Un filtre nommé est atteignable ; une
    incantation recopiée ne l'est pas — et la surface suivante l'oubliera.
    """
    fautifs = {
        p.relative_to(GABARITS).as_posix(): len(m)
        for p in _gabarits()
        if (m := _VIRGULE_ARTISANALE.findall(p.read_text(encoding="utf-8")))
    }
    assert not fautifs, (
        "des gabarits refont la virgule décimale à la main au lieu d'utiliser "
        f"le filtre `nombre_fr` : {fautifs}"
    )


def test_aucun_role_de_squad_natteint_lecran_brut():
    """`owner` est un identifiant. L'utilisateur lit « Propriétaire ».

    La clé reste la clé : trois gabarits comparent dessus
    (`membership.role == 'owner'`), et la renommer casserait l'autorisation.
    Seul l'AFFICHAGE est traduit, par le filtre `role_squad`.
    """
    fautifs: dict[str, list[str]] = {}
    for p in _gabarits():
        rendus = [
            r for r in _ROLE_RENDU.findall(p.read_text(encoding="utf-8"))
            if "role_squad" not in r
        ]
        if rendus:
            fautifs[p.relative_to(GABARITS).as_posix()] = rendus
    assert not fautifs, (
        "des gabarits rendent une valeur de rôle brute — c'est une clé de "
        f"programme, pas un mot français. Passer par `| role_squad` : {fautifs}"
    )


def test_la_sonde_reconnait_les_deux_defauts():
    """Garde de la garde : les deux sondes mordent-elles encore ?

    Les défauts d'ORIGINE, dans leurs écritures réelles — les trois variantes
    de la virgule telles qu'elles vivaient dans le dépôt, et le rendu de rôle
    tel qu'il vivait sur deux surfaces.
    """
    for original in (
        '{{ x | string | replace(".", ",") }}',
        """{{ "%.1f" | format(x) | replace('.', ',') }}""",
        '{{ x | round(1) | string | replace(".", ",") }}',
    ):
        assert _VIRGULE_ARTISANALE.search(original), (
            f"la sonde ne reconnaît plus cette écriture : {original}"
        )
    assert _ROLE_RENDU.findall("<span>{{ m.role }}</span>") == ["{{ m.role }}"]
    # Une COMPARAISON n'est pas un rendu : elle ne doit pas être accusée.
    assert not _ROLE_RENDU.findall("{% if membership.role == 'owner' %}")


def test_le_filtre_rend_ce_quil_promet():
    """Le zéro décimal disparaît par défaut, et se force quand il est mesuré."""
    from app.templating import nombre_fr

    assert nombre_fr(586.0) == "586"
    assert nombre_fr(75.63) == "75,6"
    assert nombre_fr(75.0, 1) == "75,0"
    assert nombre_fr(None) == "—"


def test_le_libelle_de_role_couvre_toutes_les_cles():
    """Une clé sans libellé s'afficherait telle quelle — donc visible.

    Le repli rend la clé plutôt que d'escamoter la ligne : c'est ce
    comportement qui a révélé, sur le récap, qu'une valeur semée par mon labo
    n'existait pas dans le produit.
    """
    from app.models.squad import SQUAD_ROLE_LABELS
    from app.templating import role_squad

    assert set(SQUAD_ROLE_LABELS) == {"owner", "member"}
    assert role_squad("owner") == "Propriétaire"
    assert role_squad("inconnu") == "inconnu"
    assert role_squad(None) == ""
