# `AUREN_UI_U1_ROLE_TOKENS` — la couche de rôles

> **Tranche 1 de la voie critique UI** (`AUREN_UI_CRITICAL_PATH §2`). Socle :
> `AUREN_VISUAL_BACKBONE §3.1`. Tier `check_scope` : **`SHARED_CODE`**.
>
> Propriété qui définit la tranche : **elle ajoute des noms et ne déplace pas un
> pixel.** Ce n'est pas une intention, c'est vérifié — trois routes rendues
> avant/après sont bit-identiques.

---

## 1. Brainstorming / Options / Risques / Choix retenu (`CLAUDE.md §3`)

**Problème.** La palette cockpit nomme des **valeurs** (`--t-amber`), pas des
**emplois**. `--t-amber` est documenté « action utilisateur · objet actif » :
deux emplois sous un seul nom. Le jour où l'objet actif doit cesser de
ressembler à un bouton, **aucun sélecteur ne permet de les séparer** — le CSS
n'a jamais su lesquels étaient lesquels.

| Option | Description | Risque |
|---|---|---|
| **A** — renommer les `--t-*` en rôles | une seule couche, pas de doublon | **recâble tout le produit d'un coup** ; une tranche invisible devient une tranche à blast radius maximal |
| **B** — couche de rôles **aliasée**, aucun consommateur recâblé | additive, rendu prouvablement inchangé, migration incrémentale ensuite | deux couches cohabitent un temps |
| **C** — attendre `U2` et introduire les rôles avec leur premier usage | pas de couche « morte » | mélange une décision d'ontologie et une décision visuelle ; l'exposition ne saurait plus ce qu'elle juge |

**Retenu : `B`.** La seule option qui sépare *nommer* de *décider*. `A` fait
d'une tranche d'ontologie une refonte. `C` interdit d'exposer l'ontologie seule
— or c'est exactement ce que l'opérateur devait pouvoir juger.

---

## 2. Ce qui est livré

**25 rôles** déclarés dans `app.css :root`, aliasés sur les valeurs en place.

> ⚠ Le socle annonçait **16** rôles. Le CSS en contenait déjà neuf que
> l'ontologie avait oubliés : `action-hover`, `action-dim`, la triade bleue
> (`origin-system` / `-data` / `-line`), `data-unknown`, `glyph-decorative`, et
> un **quatrième** niveau de surface. **Le code avait raison, le socle est
> corrigé.**

Trois points de doctrine matérialisés :

1. **`action-primary` ≠ `state-active` ≠ `focus`** — trois tokens, une seule
   valeur ambre aujourd'hui. Des tokens distincts peuvent diverger ; une valeur
   employée à trois fins ne le peut pas.
2. **`origin-system` ≠ `support-information`** — la provenance n'est pas une
   nature de retour.
3. **Le 4ᵉ niveau produit (« en vol ») n'est pas un 5ᵉ fond** — c'est
   `state-active` posé sur l'un des quatre. Une profondeur de plus aurait été
   inventée pour rien.

`action-terminal` est déclaré et aliasé sur l'ambre **faute de décision** :
`S-09` n'est pas tranché. Le rôle existe pour que la décision ait un endroit où
atterrir, pas parce que sa valeur est arrêtée.

---

## 3. Défauts trouvés — et l'un d'eux était invisible

### 3.1 Trois couleurs de support illisibles sur le fond réel

Héritées, mesurées à l'époque sur `--bg` seul. Sur L3 `--t-raised` :

| token hérité | valeur | L3 | seuil | verdict |
|---|---|---|---|---|
| `--danger` | `#B85C5C` | **3,21:1** | 4,5 | ⛔ un message d'erreur est du **texte** |
| `--info` | `#6E8FA8` | **4,19:1** | 4,5 | ⛔ |
| `--warn` | `#C77B54` | **4,35:1** | 4,5 | ⛔ |
| `--ok` | `#6E9E7A` | 4,65:1 | 4,5 | ✅ repris tel quel |

C'est **exactement** le défaut `--t-blue-line` (`#4A7FB5` : 4,43 sur base,
**3,40 sur L3**) reproduit une génération plus tard. La garde qui l'avait
attrapé ne regarde que les 19 tokens `--t-*` ; ces quatre-là vivent dans la
génération héritée.

Corrections **à teinte et saturation constantes**, seule la luminosité monte —
**approuvées par l'opérateur sur rendu le 2026-09-04** :

    --role-support-warning      #C97F59   4,53   (de #C77B54)
    --role-support-error        #C67D7D   4,51   (de #B85C5C)
    --role-support-information  #7695AD   4,54   (de #6E8FA8)

Les tokens hérités **ne sont pas touchés** : leurs consommateurs actuels gardent
leur rendu (`§5.3`).

### 3.2 La garde de palette ne lisait qu'**un seul** bloc `:root`

`app.css` en déclare **deux** (`:root` ligne 14 ; un second pour les tokens de
rail). `_root_block()` de `test_uiv3_cockpit_ladder` fait un `re.search` : il
s'arrête au premier.

**Preuve, pas hypothèse.** `--t-amber: #FF0000` planté dans le second bloc :

* `test_uiv3_cockpit_ladder` → **17 tests, tous verts.** Il ne l'a pas vu.
* `test_ui_role_tokens` → **5 échecs**, dont la cause nommée.

Aucune valeur n'est aujourd'hui dans ce cas. La garde existe pour que cela reste
vrai.

### 3.3 ⚠ Ouvert — la première marche de profondeur est sous le plancher

Trouvé **en exposant la planche**, pas en lisant le code : **L0→L1 vaut 1,065**,
contre le plancher de **1,12** que le projet s'est fixé. La garde ne la vérifie
pas — `test_adjacent_depth_steps_are_perceptible` boucle sur `for i in (1, 2)`.

**Arbitrage opérateur du 2026-09-04 : les quatre niveaux restent quatre, et la
superposition doit devenir plus distincte** — par délimiteur, par contraste
accru, ou les deux ; et la distinction doit porter **au-delà de la couleur**.
C'est l'objet de `U2`, pas de cette tranche : `U1` ne touche aucune valeur
existante.

---

## 4. Relecture des relevés de décisions (`CLAUDE.md §5.2`)

Décision par décision, contre ce qui vient d'être écrit.

### `DESIGN_DECISIONS_UIV2_SURFACES.md`

| Décision | Verdict |
|---|---|
| `Q1` connexion porte l'identité | **non concernée** — aucun template touché |
| `Q2` ancre visuelle de l'accueil | **non concernée** |
| `Q3` « état du jour » replié | **non concernée** |
| `Q4` la ligne de série devient un instrument | **non concernée** |
| `Q5` trois rangs de surfaces | **respectée** — les rôles de surface nomment la profondeur ; aucun conteneur universel n'est réintroduit |
| Tokens bleus (origine système) | **respectée et renforcée** — la triade devient `origin-system*`, et `U1` rend impossible de la confondre avec `support-information` ⚠ *voir dérive ci-dessous* |
| Convergence Gravl → Auren | **non concernée** |

> ⚠ **DÉRIVE DE RELEVÉ, signalée et NON corrigée d'office.** La table des tokens
> bleus documente encore `--t-blue-line: #4A7FB5` à **4,43:1**. Cette valeur a
> été **corrigée en `#5A93C9`** parce qu'elle tombait à 3,40 sur L3. Le relevé
> versionné contredit donc le code livré. **Amender silencieusement une spec
> versionnée est un arrêt dur (`CLAUDE.md §4`)** — la correction du relevé est
> signalée à l'opérateur, pas commise ici.

### `DESIGN_DECISIONS_HOME_UIV2.md`

| Décision | Verdict |
|---|---|
| `D1` contrat d'interactivité hybride | **non concernée** |
| `D2` badge d'origine | **respectée** — `origin-system` porte le sens, sans le diluer |
| `D3` sémantique des couleurs | **respectée aujourd'hui, à surveiller.** `D3` écrit « ambre = action / actif / focus » : la même conflation que `U1` nomme. Les valeurs sont **inchangées**, donc `D3` tient. Mais toute divergence future de `state-active` ou `focus` **amende `D3`** et exige une décision opérateur, jamais un commit silencieux |
| `D4` suppressions | **non concernée** |
| `D5` substitution descriptif → visuel | **non concernée** |
| `D6`–`D9` cycle, régularité, progression, anticipation | **non concernées** |

**Aucune décision violée.**

---

## 5. Vérifications

| Check | Résultat |
|---|---|
| `check_scope.py` | **`SHARED_CODE`** — 5 checks locaux exigés |
| `ruff` (fichier neuf) | All checks passed |
| `check_ruff_budget.py` | 275 / 548 — respecté |
| `check_spec_protocol.py` | OK |
| Tests ciblés | **31 verts** (`test_ui_role_tokens`) |
| Broad sweep ciblé | **528 verts** — les 48 suites qui lisent les feuilles, plus coque, navigation, a11y — **en série**, jamais `-n auto` |
| Full sweep local | **skippé**, conformément au tier (`CLAUDE.md §1`) |

**Gardes plantées avant d'être crues.** Une garde verte du premier coup ne
prouve rien. Les trois défauts d'origine ont été plantés **en entier** puis
retirés : contraste sous seuil → 2 échecs ; seconde autorité `:root` → 5
échecs ; consommateur prématuré → 1 échec. Diff final : **0 suppression**.

---

## 6. Exposition (`CLAUDE.md §5.1`)

**Méthode.** Un seul serveur, une seule base (copie locale en scratchpad,
**jamais la prod**), le même HTML. Playwright intercepte `app.css` et sert la
feuille canonique pour la passe « avant ». **Seuls les octets de CSS diffèrent** —
pas le HTML, pas les données. Plus strict que deux serveurs, qui auraient pu
diverger par la donnée.

| Route | Verdict |
|---|---|
| `/` | **pixel-identique** |
| `/login` | **pixel-identique** |
| `/science` | **pixel-identique** |

25 rôles **résolus par le navigateur** — un token déclaré mais non résolu
rendrait la couche décorative. `action-primary`, `state-active` et `focus`
résolvent tous trois `#C8A24B` : la démonstration de l'ontologie.

**Preuve mécanique complémentaire** — le diff est **108 insertions, 0
suppression**, et la seule ligne ajoutée contenant un `;` hors `--role-` est une
phrase de commentaire. Aucune déclaration existante n'est touchée ; aucun
consommateur n'existe (garde `test_the_role_layer_rewires_no_consumer`). Le
style calculé est donc inchangé **par construction**, pas seulement sur les
routes échantillonnées.

---

## 7. Ce que cette tranche laisse ouvert

* **`U2`** — rendre la superposition des quatre niveaux **distincte**, y compris
  **au-delà de la couleur** (arbitrage opérateur du 2026-09-04).
* **`S-09`** — la valeur de `action-terminal`.
* **La dérive du relevé** sur `--t-blue-line` (§4).
* La migration des consommateurs vers les rôles : elle fera **expirer**
  `test_the_role_layer_rewires_no_consumer`, tier T5, par la spec et pas par
  commodité.
