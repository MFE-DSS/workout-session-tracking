"""`Sb_UI_DISCLOSURE_01` — aucun dépliant ne s'en remet au navigateur.

Un `<summary>` non stylé rend le triangle natif, à la taille que le navigateur
décide. Mesuré avant cette tranche : **20 px** sur les six dépliants de
`muscle_focus`, **21 px** sur `/plan` et `/profil`. Le standard du produit est
**44 px** (`UIV3_TARGETS_44_01`), et `interaction.css` définit `.disclosure`
depuis longtemps — avec sa géométrie, son chevron, son état de focus.

Le composant existait. Neuf dépliants ne s'en servaient pas. C'est le motif
« une décision appliquée là où c'était commode », appliqué à un composant.

⚠ POURQUOI CETTE GARDE N'EST PAS UNE LISTE. Ma première version énumérait les
gabarits à corriger — donc elle n'aurait jamais vu le dixième. Elle part d'un
`rglob` et n'admet aucune exception nommée : un dépliant est conforme s'il
adopte le composant OU s'il désarme lui-même le marqueur, jamais parce qu'il
figure sur une liste.

⚠ ET POURQUOI ELLE N'EST PAS UN DOUBLON DE `test_ui_surface_guards`.

J'ai écrit ce fichier sans voir que le dépôt avait DÉJÀ un cliquet sur les
`<summary>` — `test_no_new_summary_loses_its_native_marker`, avec un inventaire
de décisions dans `ui_surface_inventory.json`. C'est la CI qui me l'a appris, en
rougissant sur une entrée devenue périmée. Neuvième fois de cette session qu'un
outil existait et que je ne l'ai pas cherché : le motif que je traque, commis
par moi.

Les deux gardes tirent en sens OPPOSÉS, et c'est ce qui les rend
complémentaires :

* le CLIQUET interdit de **retirer** le marqueur natif sans l'inscrire comme
  décision. Il regarde le CSS. Il n'a jamais pu voir les onze `<summary>` nus,
  puisqu'aucune règle ne les visait ;
* CE FICHIER interdit de **laisser** le marqueur natif. Il regarde les gabarits.
  Il ne verra jamais un retrait silencieux, puisque le retrait le satisfait.

Ensemble, ils forcent un choix EXPLICITE dans les deux sens. Séparément, chacun
laisse passer exactement ce que l'autre attrape.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "app" / "templates"
CSS_DIR = ROOT / "app" / "static" / "css"

_ENC = "utf-8"


def _css() -> str:
    return "\n".join(
        re.sub(r"/\*.*?\*/", "", p.read_text(encoding=_ENC), flags=re.DOTALL)
        for p in sorted(CSS_DIR.glob("*.css"))
    )


CSS = _css()


def _classes_that_disarm() -> tuple[frozenset[str], frozenset[str]]:
    """Les classes dont une règle CSS retire le marqueur natif du `<summary>`.

    ⚠ CETTE FONCTION A REMPLACÉ UNE REGEX SUR LE SÉLECTEUR, ET C'EST UNE
    CORRECTION, PAS UN RAFFINEMENT. La première version composait le sélecteur
    attendu (`.maclasse > summary`) et le cherchait tel quel. Elle ne voyait ni
    `:where(.session-feedback__note, .rule) > summary`, ni
    `.exercise-card__compact::marker`, ni aucune règle groupée par virgule —
    trois formes bien réelles dans ce dépôt. Elle produisait donc **trois faux
    positifs**, et une garde qui accuse du code sain est pire qu'une garde
    absente : elle apprend à ignorer les gardes.

    On lit maintenant les RÈGLES : pour chaque bloc qui désarme le marqueur, on
    récolte toutes les classes citées dans son sélecteur. La forme du sélecteur
    n'a plus d'importance.

    Trois façons valides de désarmer, toutes présentes ici : `list-style: none`,
    un pseudo-élément de marqueur mis à `display: none`, ou un `display` qui
    n'est pas `list-item` — un `<summary>` en `flex` ne génère pas de boîte de
    marqueur.

    ⚠ DEUX ENSEMBLES, ET LA DISTINCTION EST NÉCESSAIRE — une version qui les
    confondait accusait `history.html`, dont le `<summary>` porte pourtant
    `.history-item__toggle { display: flex; min-height: 44px }` :

    * `SOI` — une classe posée SUR le `<summary>`. Sa règle n'a aucune raison de
      mentionner `summary` : `.history-item__toggle { display: flex }` suffit.
    * `ENFANT` — une classe posée sur le `<details>`. Là, seule une règle qui
      vise explicitement le descendant (`.X summary`, `:where(.X, .Y) > summary`)
      atteint le `<summary>`.

    Exiger « summary dans le sélecteur » partout ratait le premier cas ; ne
    l'exiger nulle part ferait entrer dans l'ensemble toutes les classes en
    `display:flex` du dépôt, et la garde passerait tout.
    """
    soi: set[str] = set()
    enfant: set[str] = set()
    for sel, bloc in re.findall(r"([^{}]+)\{([^{}]*)\}", CSS):
        vise_marqueur = "::-webkit-details-marker" in sel or "::marker" in sel
        desarme = (
            (vise_marqueur and re.search(r"display:\s*none", bloc))
            or re.search(r"list-style(-type)?:\s*[^;]*none", bloc)
            or re.search(r"display:\s*(flex|block|inline-flex|grid)", bloc)
        )
        if not desarme:
            continue
        classes = re.findall(r"\.([A-Za-z0-9_-]+)", sel)
        soi.update(classes)
        if "summary" in sel or vise_marqueur:
            enfant.update(classes)
    return frozenset(soi), frozenset(enfant)


DISARMED_SELF, DISARMED_CHILD = _classes_that_disarm()


def _class_tokens(attrs: str) -> list[str]:
    """Les classes d'un attribut, Jinja neutralisé.

    ⚠ TROISIÈME FOIS QUE CE MOTIF ME PIÈGE DANS CETTE SESSION. Un attribut de
    classe peut porter du Jinja :

        class="exercise-card__compact{% if is_active %} …--active{% endif %}"

    Un `split()` naïf en tire le jeton `exercise-card__compact{%`, qui ne
    correspond à aucune classe CSS — et la garde accuse un gabarit parfaitement
    sain, dont la classe est pourtant désarmée trois fois dans `app.css`.

    On retire donc les blocs et les expressions AVANT de découper. Un `{% %}`
    devient une espace : il sépare réellement deux classes.
    """
    m = re.search(r'class="([^"]*)"', attrs)
    if not m:
        return []
    brut = re.sub(r"\{%.*?%\}|\{\{.*?\}\}", " ", m.group(1), flags=re.DOTALL)
    return brut.split()


def _pairs() -> list[tuple[str, int, str, str]]:
    """(fichier, ligne, classes du <details>, classes du <summary>)."""
    out: list[tuple[str, int, str, str]] = []
    for p in sorted(TEMPLATES.rglob("*.html")):
        src = re.sub(r"\{#.*?#\}", "", p.read_text(encoding=_ENC), flags=re.DOTALL)
        for m in re.finditer(
            r"<details([^>]*)>((?:(?!<details)[\s\S])*?)<summary([^>]*)>", src
        ):
            d_attrs, _, s_attrs = m.groups()
            ligne = src[: m.start()].count("\n") + 1
            out.append((
                p.relative_to(TEMPLATES).as_posix(), ligne,
                " ".join(_class_tokens(d_attrs)),
                " ".join(_class_tokens(s_attrs)),
            ))
    return out


PAIRS = _pairs()


def test_the_sweep_actually_finds_disclosures():
    """Une garde qui ne trouve aucun dépliant serait verte pour rien."""
    assert len(PAIRS) > 15, f"{len(PAIRS)} dépliants trouvés — le balayage ne porte sur rien"


def test_the_component_can_be_adopted_without_rewriting_the_summary():
    """Adopter le composant doit coûter UNE classe, pas une réécriture.

    Le sélecteur ne visait que `.disclosure__summary` : adopter imposait
    d'ajouter une classe, d'envelopper le texte et de poser un `<span>` de
    chevron. Sur six dépliants identiques, ce coût a suffi pour que personne
    n'adopte. Un composant trop cher à adopter n'est pas un composant.
    """
    assert re.search(r"\.disclosure\s*>\s*summary", CSS), (
        "le composant n'accepte plus un `<summary>` nu : son adoption redevient "
        "une réécriture, et les surfaces recommenceront à s'en passer"
    )


@pytest.mark.parametrize(
    "fichier,ligne,d_cls,s_cls",
    PAIRS,
    ids=[f"{f}:{n}" for f, n, _, _ in PAIRS],
)
def test_no_disclosure_relies_on_the_browser_default(fichier, ligne, d_cls, s_cls):
    """Conforme par ADOPTION du composant, ou par désarmement explicite."""
    if "disclosure" in d_cls.split():
        return                                    # adopte le composant
    if DISARMED_SELF.intersection(s_cls.split()):
        return                                    # le <summary> se style lui-même
    if DISARMED_CHILD.intersection(d_cls.split()):
        return                                    # stylé depuis le <details>
    pytest.fail(
        f"{fichier}:{ligne} — dépliant livré au marqueur natif du navigateur.\n"
        f"  <details class=\"{d_cls or '—'}\"> / <summary class=\"{s_cls or '—'}\">\n"
        f"  Ajouter `disclosure` sur le <details> suffit : le composant accepte "
        f"un <summary> nu."
    )
