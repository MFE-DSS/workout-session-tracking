# SPRINT Sb_UI_PROFILE_PREFERENCES_REDESIGN_01 — un instrument, pas un formulaire (RAPPORT)

**Train :** `AUREN_INTERACTION_REFINEMENT_01`, tranche 2/3 ·
**Base canonique :** `a724605` · **Branche :** `sb/ui-profile-preferences-redesign-01`

---

## 1. Avant / après

| | Avant | Après |
|---|---|---|
| Cadence | `<select>` de 7 valeurs | grille de 7 radios, rien de présélectionné |
| Priorités | **trois `<select>` de navigateur** | six options classées, rang `01/02/03` visible |
| Matériel | cases nues, cible ≈ 16 px | rangées de choix, cible 44 px |
| Style | `style="…"` sur presque chaque bloc | **zéro style en ligne** dans le panneau |

Le contrat POST est **identique** : `sessions_per_week`, `focus_1`, `focus_2`,
`focus_3`, `equipment`, `equipment_declared`.

---

## 2. La décision qui rend le fallback gratuit

L'amélioration progressive est souvent deux chemins à maintenir. Ici il n'y en
a qu'un : **les trois `<select>` natifs restent la source de vérité**. Ils sont
dans le DOM, ils portent les noms attendus, et ce sont eux qui partent dans la
requête. Le bloc classé n'est qu'une **façon d'écrire dedans**.

Conséquence : le corps du POST est rigoureusement le même avec ou sans JS, donc
le fallback n'est pas une branche parallèle à tester — c'est le chemin normal.

Le script est chargé en `defer`, le bloc classé est rendu `hidden` **côté
serveur**, et le fallback n'est masqué qu'une fois l'amélioration réellement
câblée. Si le script ne s'exécute jamais, l'utilisateur voit les trois selects
et peut enregistrer.

Les options classées sont de vrais `<button type="button">` : focusables,
activables à Entrée/Espace, avec `aria-pressed` — aucun ARIA maison, aucun
glisser-déposer.

---

## 3. Ce que le style ne devait pas détruire

**`NULL` ≠ `[]`.** Le marqueur caché `equipment_declared` distingue « section
jamais soumise » de « soumise sans rien cocher ». Il survit à la refonte, et
deux tests le vérifient — l'un sur le balisage, l'autre sur les octets
persistés.

**Aucune cadence présélectionnée.** Un utilisateur qui n'a rien déclaré ne doit
voir aucun radio coché. Planté : présélectionner `3` fait tomber deux gardes.

**Rang visible après sélection.** Le rang est du **texte** dans le libellé, pas
une décoration : il survit à la sélection, et la place est réservée quand il est
vide pour que les libellés ne sautent pas au retrait.

---

## 4. Plantations — quatre, toutes mordent

| # | Plantation | Gardes qui tombent |
|---|---|---|
| 1 | marqueur `equipment_declared` retiré | 2 |
| 2 | cadence `3` présélectionnée | 2 |
| 3 | fallback sans JS masqué côté serveur | 1 |
| 4 | champ POST renommé | 4 |

---

## 5. Un test existant mis à jour, pas affaibli

`test_every_control_has_a_label` cherchait `for="sessions_per_week"` — **un**
label pointant vers **un** `<select>`. La cadence est désormais un groupe de
radios, et le motif accessible correct pour un groupe de radios n'est pas un
label unique mais `<fieldset><legend>` plus un label par option.

Le test vérifie donc la **même intention sous la nouvelle forme**, et il est
plus strict qu'avant : il exige que **chaque** option porte son libellé, et que
les trois selects de repli gardent leurs `for=` explicites.

---

## 6. Preuves

| Preuve | Résultat |
|---|---|
| Tests dédiés | **20** |
| Balayage ciblé (préférences, primitives, profil, morpho, budget) | **253** |
| Style en ligne dans le panneau | **aucun** |
| Empreinte de plan / budget avant-après | **identiques** |
| Modules moteur touchés | **aucun** |

## Verdict

Le panneau se lit maintenant comme un instrument : ce qui est choisi se voit,
et dans quel ordre.

Le point qui méritait le plus d'attention n'était pas le rendu mais le fallback.
En laissant les `<select>` natifs porter la vérité, le mode sans JS cesse d'être
un second chemin à maintenir — et le POST devient impossible à faire diverger.
