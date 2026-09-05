"""`Sb_UI_FORMULAIRES_01` — aucun contrôle de formulaire ne s'en remet au navigateur.

Le produit avait une coque canonique pour le `<select>` — macro `select_shell`,
CSS dans `interaction.css` : 44 px, fond sombre, chevron, `:focus-visible`.
**Un seul gabarit l'employait.** Sept `<select>` étaient écrits à la main, et
ils rendaient le défaut du navigateur : un rectangle BLANC PUR dans une
interface sombre.

Mesuré avant : neuf contrôles à fond clair sur les surfaces d'escouade, et ZÉRO
sur `/plan`, le seul gabarit qui employait la coque. La démonstration se faisait
toute seule.

⚠ POURQUOI PERSONNE NE L'ADOPTAIT — ET POURQUOI CE N'ÉTAIT PAS DE LA NÉGLIGENCE.

En convertissant les sept, QUATRE raisons distinctes sont apparues, chacune
suffisante à elle seule :

  1. `required` n'existait pas. Adopter la coque aurait RETIRÉ une contrainte de
     saisie en silence.
  2. Un `onchange` était impossible à passer — l'un des `<select>` en portait un
     qui alimentait un champ caché.
  3. La macro ne savait pas lire une liste d'OBJETS, or c'est ce que les
     gabarits ont sous la main. Jinja n'a pas de `zip`.
  4. L'option vide était forcée à `value=""`, alors que `squad_compare` lit
     `a: int = Query(0)` et attend `"0"`.

Un composant qui ne couvre pas les attributs de ses appelants et ne consomme pas
la donnée qu'ils ont n'est pas adopté. Les quatre manques sont comblés ; cette
garde empêche le huitième `<select>` nu.

Et pour le champ texte, il n'existait AUCUNE coque : les `<input>` n'étaient
stylés que dans le périmètre de la séance. Ce n'était pas un contournement mais
une absence — elle se voyait dès qu'on corrigeait le `<select>` juste au-dessus,
le champ d'à côté restant blanc.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "app" / "templates"
CSS = (ROOT / "app" / "static" / "css" / "interaction.css").read_text(encoding="utf-8")

_ENC = "utf-8"

#: Les types d'`<input>` qui ne sont PAS des champs de saisie visibles et
#: n'ont donc rien à faire dans une coque : ils sont invisibles, ou bien ils ont
#: leur propre primitive (`choice_row` pour radio et checkbox).
TYPES_HORS_COQUE = {"hidden", "checkbox", "radio", "submit", "button", "file"}

ALL_TEMPLATES = sorted(TEMPLATES.rglob("*.html"))


def _uncommented(src: str) -> str:
    """Les commentaires Jinja EXPLIQUENT le défaut ; ils ne le sont pas.

    Ce fichier a laissé dans les gabarits des commentaires qui citent
    `<select>` pour dire pourquoi il a été retiré. Une garde qui lit sa propre
    justification rougirait sur l'explication du correctif — motif déjà
    rencontré plusieurs fois dans ce dépôt.
    """
    return re.sub(r"\{#.*?#\}", " ", src, flags=re.DOTALL)


def test_the_sweep_actually_reads_templates():
    assert len(ALL_TEMPLATES) > 40, "le balayage ne porte sur rien"


def test_both_shells_share_one_geometry():
    """Deux déclarations divergeraient à la première évolution.

    La coque texte est née en même temps que l'adoption de celle du select. Les
    écrire séparément aurait garanti qu'elles se désynchronisent — c'est la
    faute que cette tranche corrige ailleurs.
    """
    assert re.search(
        r"\.select-shell__control,\s*\n\s*\.input-shell__control\s*\{", CSS
    ), (
        "les deux coques ne partagent plus une seule déclaration de géométrie"
    )


@pytest.mark.parametrize("tpl", ALL_TEMPLATES, ids=lambda p: p.name)
def test_no_template_writes_a_raw_select(tpl: Path):
    """Universel par construction : la liste vient d'un `rglob`.

    `_macros.html` est le seul autorisé — c'est lui qui DÉFINIT la coque.
    """
    src = _uncommented(tpl.read_text(encoding=_ENC))
    if "macro select_shell" in src:
        return
    assert "<select" not in src, (
        f"{tpl.name} écrit un `<select>` à la main. Employer `select_shell` : "
        f"elle couvre `required`, `value_attr`/`label_attr` pour une liste "
        f"d'objets, et `empty_value` pour une sentinelle non vide."
    )


def test_the_text_shell_is_not_dead_code():
    """La coque texte est née dans cette tranche ; on vérifie qu'elle SERT.

    Une macro que personne n'appelle est une intention, pas un composant — c'est
    exactement ce qu'était la coque du `<select>` avant aujourd'hui, employée
    une seule fois dans tout le produit.
    """
    appels = [
        p.name for p in ALL_TEMPLATES
        if "input_shell(" in _uncommented(p.read_text(encoding=_ENC))
        and "macro input_shell" not in p.read_text(encoding=_ENC)
    ]
    assert appels, "`input_shell` n'est appelée nulle part : composant mort-né"


# ═══════════════════════════════════════════════════════════════════════════
# CE QUI N'EST PAS GARDÉ ICI, ET POURQUOI JE L'ÉCRIS PLUTÔT QUE DE FAIRE
# SEMBLANT
# ═══════════════════════════════════════════════════════════════════════════
#
# L'invariant qui compte vraiment pour l'utilisateur est : « aucun contrôle de
# formulaire ne rend le blanc du navigateur sur un fond sombre ». Il n'est PAS
# gardé dans ce fichier, et ce n'est pas un oubli.
#
# J'ai essayé deux fois de l'écrire statiquement, et les deux fois la garde a
# accusé du code sain :
#
#   1. « le contrôle doit porter la classe de coque » → SEIZE gabarits accusés,
#      dont `login`, `register` et `forgot_password`, dont les champs sont
#      pourtant sombres : une RÈGLE de feuille les style, pas une classe ;
#   2. « un contrôle sans aucune classe ne peut être atteint par aucune règle »
#      → FAUX. Les 18 champs de `/profile` n'ont pas de classe et sont
#      pourtant sombres et à 44 px : un sélecteur DESCENDANT les atteint.
#
# Un fichier de gabarit ne dit pas quelle règle s'appliquera. Seul un rendu le
# dit. Le dépôt a d'ailleurs déjà le bon outil pour ça — le contrat visuel de
# `UIV3_VISUAL_BASELINE_01`, avec sa dimension `A11Y` (« contraste, nom
# accessible, focus ») et son harnais navigateur.
#
# C'est là que cette vérification appartient. Ne pas l'y brancher est une dette
# NOMMÉE, pas une garde manquante par distraction — et une garde qui ment vaut
# moins que pas de garde, parce qu'elle apprend à ignorer les rouges.
