# SPRINT Sb_UI_INTERACTION_PRIMITIVES_01 — une grammaire, pas un rebrand (RAPPORT)

**Train :** `AUREN_INTERACTION_REFINEMENT_01`, tranche 1/3 ·
**Base canonique :** `832abda` · **Branche :** `sb/ui-interaction-primitives-01`

Déclencheur : **dogfood réel**, `UX_INTERACTION = FAIL`. Ce n'est pas un défaut
de planification et n'est pas traité comme tel.

---

## 1. Audit de l'existant

| Surface | Constat |
|---|---|
| `.segmented` | `input { display: none }` — **le seul contrôle opérable est retiré du clavier** |
| Priorités du profil | trois `<select>` de navigateur, la sélection disparaît dans le chrome |
| Matériel | liste verticale de cases nues, cible tactile ≈ 16 px |
| Cadence | `<select>` pour un domaine fini de 7 valeurs |
| Formulaire profil | `style="..."` en ligne sur presque chaque bloc |
| `details/summary` | stylés au cas par cas, pas de grammaire commune |

Le défaut rapporté — « boîtes dans des boîtes », « la sélection ne se voit
pas » — est une **grammaire d'interaction**, pas une palette. La palette
graphite, l'accent ambre, la typographie mono et la coque ne sont pas rouverts.

---

## 2. Ce qui est livré

`app/static/css/interaction.css` — **six primitives**, chargé après `app.css`
pour s'appuyer sur ses tokens :

| Primitive | Rôle |
|---|---|
| `.choice-group` | encadre le groupe **une fois** ; les enfants sont des rangées |
| `.choice-row` | option finie : `[marqueur] libellé / métadonnée` |
| `.choice-row__rank` | rang `01/02/03` visible **après** sélection |
| `.disclosure` | `details/summary` : résumé + filet + contenu, **sans** carte imbriquée |
| `.select-shell` | coque canonique unique du `<select>` natif |
| `.choice-grid` | domaine fini très court (cadence 1..7) |

Plus `.a11y-input` : masquage **visuel** qui conserve le focus clavier.

Macros Jinja correspondantes dans `_macros.html`. **Aucun style en ligne**,
aucun ARIA maison, aucun JS.

Les primitives ne sont **pas encore appliquées** à l'application — c'est le
périmètre des tranches 2 et 3.

---

## 3. Les quatre règles, rendues exécutables

**Un cadre par groupe.** `.choice-row` n'a ni `border`, ni `border-radius`, ni
`box-shadow` — un test le vérifie champ par champ. La séparation est un filet
`+ .choice-row`.

**Sélection lisible sans couleur.** Trois signaux non chromatiques : le marqueur
se remplit d'un glyphe **texte** (`●` / `✓`), le libellé passe en `600`, une
arête `inset 2px` apparaît. L'ambre est un quatrième signal, jamais un
remplissage plein.

**44 px et rangée entière cliquable.** Le `<label>` **enveloppe** l'input : le
test l'affirme sur le **HTML rendu**, pas sur le gabarit.

**Sémantique native.** `radio` / `checkbox` / `details`. Zéro `role="combobox"`.
`display:none` interdit sur l'input opérable.

---

## 4. Plantations — cinq, dont une a démasqué une garde trouée

| # | Plantation | Résultat |
|---|---|---|
| 1 | `display:none` sur l'input opérable | **mord** |
| 2 | sélection lisible en couleur seulement | **mord** |
| 3 | cible tactile à 28 px | **mord** |
| 4 | bordure + rayon + ombre sur chaque enfant | **mord** (2 gardes) |
| 5 | sélecteur global non scopé | **passait au vert** → corrigé |

**(5)** Ma garde anti-sélecteur-global n'inspectait que les lignes **finissant**
par `{`. Une règle sur une seule ligne — `select { border: 1px solid red; }` —
passait sans être vue. Les sélecteurs sont désormais extraits
**structurellement** ; replantée en trois formatages (une ligne, multi-lignes,
sélecteur groupé), la garde tombe à chaque fois.

> Note honnête : trois de mes tests lisaient le mauvais bloc CSS. `_rule()`
> faisait une recherche de sous-chaîne, donc demander `.choice-row {` renvoyait
> le bloc de `.choice-group .choice-row + .choice-row {`. Et
> `test_the_family_stays_small` comptait chaque `__part` BEM comme une
> primitive — il mesurait la verbosité, pas la taille de la famille. Les deux
> mesures ont été corrigées avant de servir de preuve.

Un quatrième test lisait le gabarit et découpait jusqu'au **premier**
`</label>` du fichier — celui de la macro `segmented` préexistante — donc il
comparait une chaîne vide et serait passé sur n'importe quoi. Il opère
maintenant sur le HTML rendu.

---

## 5. Preuves

| Preuve | Résultat |
|---|---|
| Tests dédiés | **29** |
| Balayage ciblé (a11y, focus session, profil, dedup UI) | **73** |
| Style en ligne dans les primitives | **aucun** |
| Couleurs brutes hors tokens | **aucune** |
| Sélecteurs globaux | **aucun** (vérifié structurellement) |

## 6. Faux positif consigné

Le linter signale un `id="main-content"` dupliqué dans `base.html`. Les deux
occurrences sont la ligne 33 (le `href` du lien d'évitement) et la ligne 136
(le `<main>` réel) — la « première occurrence » qu'il compte est dans un
commentaire Jinja `{# … #}` qui *décrit* le balisage. Faux positif d'analyse,
pas un défaut ; aucune correction appliquée.

## Verdict

Six primitives, une seule règle de construction : l'élément natif reste
opérable, le label rend la rangée entière cliquable, et le groupe est encadré
une fois.

Le vrai travail n'était pas d'écrire le CSS — c'était de rendre les quatre
règles **exécutables**, puis de découvrir que ma propre garde contre les
sélecteurs globaux ne regardait qu'un formatage sur trois.
