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
En laissant les menus natifs porter la vérité, le mode sans JS cesse d'être un
second chemin à maintenir — et le POST devient impossible à faire diverger.

---

## 7. Trois CI rouges, trois causes de périmètre

Aucune n'était un défaut du code livré. Toutes venaient de ce que je n'avais
**pas cherché** avant d'écrire.

### (a) L'inventaire JS épinglé dans 14 fichiers

`app/static/js/` devait contenir exactement `preview.js` + `session_focus.js`,
assertion dupliquée dans **14** modules de tests issus de tranches sans rapport
entre elles.

Mon balayage local couvrait 6 fichiers ; la suite en compte 245. Un `grep` sur
`static/js` avant d'écrire le script aurait suffi. Pire : l'audit de la tranche 1
lisait déjà ces fichiers pour `.segmented` — je regardais le bon répertoire sans
regarder ce que ses tests affirmaient de son **contenu**.

**Résolu par décision opérateur (Option A)** : invariant supersédé de façon
étroite, 14 gardes amendées avec la correction sémantique, caractère **exact**
conservé — un quatrième fichier JS fait toujours échouer, vérifié par plantation.

### (b) Dérive de périmètre causée par un `--fix` global

`ruff check --fix tests/` a réécrit `tests/test_behavioral.py`, hors périmètre.
L'`E402` était **préexistant**, mais la réécriture en faisait une **ligne neuve
du diff** : Sonar l'a compté comme dette de code neuf, et un seul MAJOR
(poids 15 > seuil 14) casse le gate.

CLAUDE.md §4 nomme la dérive de périmètre comme arrêt dur, et j'y suis entré en
cherchant une commande commode. Fichier intégralement restauré. **Règle retenue :
`--fix` uniquement sur les fichiers du périmètre, jamais sur un répertoire.**

### (c) Deux faux positifs sur mes propres commentaires

`Web:InputWithoutLabelCheck` sur deux lignes situées **dans des commentaires
Jinja** où j'avais écrit une balise `select` en prose : l'analyseur HTML lit le
contenu des commentaires comme du balisage vivant. Classe de faux positif
documentée dans la route de diagnostic du dépôt.

Plutôt qu'une adjudication sur le service externe — écriture délibérément
laissée hors des permissions élargies — les commentaires décrivent désormais les
éléments sans les écrire sous forme de balise.

---

## Closeout (post-merge)

| | |
|---|---|
| PR | **#110** — `--merge --match-head-commit`, **sans** squash / `--admin` / force |
| Commits | `062fa7b` (refonte) · `f0e1765` (inventaire JS) · `8d045f6` (périmètre + faux positifs) |
| Merge | **`a73ecef`** |
| Gate Sonar | **`OK`** — 0 bug, 0 smell, 0 vulnérabilité |
| Threads / Gitar | **0 / 0** |
| Inventaire JS canonique | `prefs_focus_rank.js` · `preview.js` · `session_focus.js` |

**Dette structurelle enregistrée** : `JS_INVENTORY_GUARD_DUPLICATION` — 14
inventaires exacts dupliqués. Candidat futur `Sb_TEST_GUARD_CONSOLIDATION_01`,
**non bloquant**, explicitement hors de cette PR.

### Capacité CI canonique (run `31954805564`) — bande 4–6 Go

| Shard | Fichiers | Tests | min MemAvailable | min SwapFree |
|---|---|---|---|---|
| 1 | 83 | 1 611 | 7 500 Mo | 3 071 — intact |
| 2 | 82 | 1 398 | **5 973 Mo** | 3 071 — intact |
| 3 | 82 | 1 570 | 8 764 Mo | 3 071 — intact |

Le shard 2 passe sous 6 Go pour la première fois depuis le passage à 3 shards
(6 458 → 6 354 → **5 973**). Swap intact, aucun job tué.

Selon la règle de capacité du train : **4–6 Go ⇒ terminer la tranche verte en
cours, puis ne continuer que si la suivante est principalement CSS/gabarit et
que le risque mesuré est faible.** La tranche 2 est terminée et verte. La
tranche 3 est bien de nature CSS/gabarit, donc la règle ne l'interdit pas — mais
la décision d'ouvrir revient à l'opérateur, la marge se réduisant à chaque
tranche.
