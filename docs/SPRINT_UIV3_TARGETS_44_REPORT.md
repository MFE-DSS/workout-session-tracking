# `UIV3_TARGETS_44_01` — fermeture des cibles tactiles

**Phase 3, question 1 sur 2** : *est-ce que tout ce qu'on touche réellement est
correctement touchable ?*

Ce n'est pas une phase de design. La phase 3 **ferme** l'interface (décision
opérateur du 2026-08-19, `AUREN_UI_BLUEPRINT` §Phase 3). La console de séance
est un **`reference consumer`** : mesurée pour la non-régression, jamais
retouchée.

---

## 1. Brainstorming / Options / Risques / Choix retenu (`CLAUDE.md §3`)

**Le piège annoncé par l'opérateur** : repartir du chiffre « 69 éléments < 44 »
et appliquer `min-height: 44px` partout.

| Option | Ce qu'elle donne | Risque | Retenue |
|---|---|---|---|
| **A** — `min-height: 44px` global sur tout interactif | 0 violation en une règle | gonfle 19 étiquettes de champs texte et 27 radios de 1 × 1 px que personne ne touche ; détruit la densité de la phase 2 | **non** |
| **B** — classifier A–E, puis traiter chaque catégorie selon son exigence | la dette réelle, et rien d'autre | plus lent ; exige un instrument de mesure fiable | **OUI** |
| **C** — ne traiter que les non-conformités WCAG AA | périmètre minimal, défendable juridiquement | il n'y en a **aucune** (voir §3) — l'option se réduit à ne rien faire | non |

**Choix : B.** Le décompte historique est passé de **161 à 69** sur une seule
mesure fraîche, l'écart étant intégralement des `input[type=radio]` clippés.
Une règle générique reproduirait l'erreur en sens inverse : gonfler ce qu'on
ne touche pas, manquer ce qu'on touche.

**Risque accepté et matérialisé** : la fermeture **change la densité** sur
`/library` et `/profile`. C'est la condition d'arrêt posée par l'opérateur, et
elle est honorée — exposition avant/après, puis arrêt.

---

## 2. La taxonomie, avant toute modification

`AUREN_UIUX_V3_FOUNDATION_CONTRACT §3.2`, versionnée dans cette tranche.

| Cat. | Ce que c'est | Exigence |
|---|---|---|
| **A** `FREQUENT_SEQUENTIAL` | bouton, segmented, navigation de séance, action de formulaire | 44 × 44 requis |
| **B** `SECONDARY_STANDALONE` | lien d'historique, disclosure secondaire, action isolée | zone tactile 44, **sans chrome visible inutile** |
| **C** `INLINE` | lien intégré à une phrase | **ne pas gonfler** — exception WCAG 2.5.8 |
| **D** `HIDDEN_IMPLEMENTATION` | `input` de choix clippé derrière son label | mesurer le **label** |
| **E** `USER_AGENT_OR_EDITABLE` | aire éditable | mesurer le vrai rectangle |

### Inventaire mesuré — 7 surfaces × 3 largeurs, `SESSION_RICH`

| Cat. | sélecteurs | occurrences @ 390 px |
|---|---:|---:|
| A | 4 | 20 |
| B | 5 | 17 |
| C | 0 | 0 |
| D | 1 | 6 |
| E | 20 | 20 |
| **total** | **30** | **63** |

**`C = 0` est un fait, pas un détecteur muet** — vérifié en soumettant à la
sonde un lien réellement intégré à une phrase, qu'elle classe bien en `C`.
AUREN n'a aucun lien de ce type sous 44 px sur ces surfaces.

---

## 3. La correction qui compte le plus : **zéro non-conformité WCAG AA**

`44 × 44` **n'est pas** une obligation WCAG AA, et le rapporter comme telle
sur-déclare une conformité — faux dans le sens qui expose.

| Référence | Seuil | Niveau |
|---|---|---|
| WCAG 2.2 **SC 2.5.8** *Target Size (Minimum)* | **24 × 24 px**, avec exceptions | **AA** — plancher légal |
| WCAG 2.2 SC 2.5.5 *Target Size (Enhanced)* | 44 × 44 px | AAA |
| Apple HIG | 44 × 44 pt | recommandation plateforme |
| **AUREN** | **44 × 44 px** | **standard produit** |

L'audit teste **l'exception d'espacement** de `2.5.8` : une cible sous 24 px
reste conforme si un cercle de 24 px centré sur elle n'en croise aucun autre.

> **Résultat : 0 non-conformité AA sur les 7 surfaces × 3 largeurs, avant
> comme après.** Chaque cible sous 24 px passait par l'exception.

Sans ce test, l'audit aurait rapporté trois violations légales inexistantes —
la faute symétrique de celle qu'on cherchait à éviter.

---

## 4. Quatre défauts de mon propre instrument, trouvés en le plantant

Aucun n'était visible à la relecture. **Tous les quatre produisaient un
inventaire faux et crédible.**

| # | Défaut | Ce qu'il rendait |
|---|---|---|
| 1 | `elementFromPoint` sondé sans `scrollIntoView` | `hit = 0 %` sur **tout** ce qui vit sous le pli, y compris un lien de 202 px ; et les points sautés comptés comme sondés |
| 2 | `at.contains(el)` dans la condition d'acceptation | le `<body>` contenant tout, **chaque** point comptait : un bouton de 30 px déclaré conforme |
| 3 | l'étiquette d'un champ nombre traitée comme cible opératoire | 44 px exigés sur **19 libellés statiques** de `/profile` — l'erreur du 161 sous une autre forme |
| 4 | une page en **HTTP 500** comptée « 0 cible, tout va bien » | `/profile` entier invisible : la base de lab avait **11 migrations de retard** |

Le défaut 2 a été trouvé par une **plantation** : quatre cas de géométrie
connue soumis à la sonde — bouton 30 nu, bouton 48 nu, lien 14 étendu à 48 par
`::after`, lien 14 nu. La sonde déclarait les quatre conformes.

Le défaut 4 n'était pas un défaut produit : `/profile` fonctionne. C'est la
**fixture** qui était périmée — et le harnais refuse désormais de mesurer une
réponse ≠ 200.

---

## 5. Un défaut produit : `btn--sm` sur l'action principale

`btn--sm` est **la variante des actions rares et denses**. Elle était posée
sur **« Démarrer »** — l'action la plus importante du produit — sur trois
surfaces : `library.html`, `launcher.html`, `template_detail.html`.

Corrigé **au gabarit**, pas en affaiblissant la règle CSS. Ce qui reste en
`--sm` est authentiquement rare : rouvrir un bilan, supprimer, éditer,
imprimer.

**Frontière A/B signalée, non tranchée** : « Rouvrir pour éditer »
(`session_done`) est un `<button>`, donc `A` à la lettre de la taxonomie, mais
ni fréquent ni séquentiel. Traité en `B` — zone tactile 44, chrome inchangé —
parce que grossir une action semi-destructive invite la frappe accidentelle.
**Décision produit, elle appartient à l'opérateur.**

---

## 6. La collision de cascade — et pourquoi une garde textuelle ne l'a pas vue

Écrite `.btn:not(.btn--sm) { min-height: 44px }`, la règle de fermeture a fait
**RÉTRÉCIR `TERMINER LA SÉANCE` de 56 à 44 px**.

`.btn--end` portait déjà un `min-height: 56px` délibéré. Ma règle, **plus
spécifique et chargée après**, l'a **abaissé**. La commande dominante de l'état
`SESSION REVIEW` — acceptée au dogfood de phase 2 — a été rabotée par une passe
d'accessibilité.

**La garde que j'avais écrite est restée verte.** Elle vérifiait qu'aucun
sélecteur de la section ne nomme `.console`, `.dock`, `.setline`. Elle ne
pouvait rien voir : la collision vivait dans la **cascade**, pas dans le texte.

**Correctif** — `:where()`, qui compte pour **zéro** en spécificité. La règle
devient un plancher de dernier recours, que n'importe quelle déclaration
explicite écrase. Elle ne peut plus que **relever**.

**Instrument** — la comparaison de géométrie élément par élément entre deux
serveurs réels, promue dans le dépôt sous `scripts/geometry_manifest.py`.
C'est aussi la **couche B** exigée pour `UIV3_VISUAL_BASELINE_01`.

Verdict final : **146 inchangés · 49 grandis · 0 rétréci.**

---

## 7. Un défaut de ma main, attrapé par la mesure

Un bloc de commentaire CSS **ouvert sans `/*`** a fait disparaître
`.topbar__brand { position: relative }`. Conséquence : le pseudo-élément
d'extension prenait le viewport pour bloc conteneur — **844 px de haut** — et
**24 cibles réparées redevenaient fautives d'un coup**.

Rien dans le fichier ne le montrait à la lecture. Une garde de parité
`/*` / `*/` sur toutes les feuilles couvre désormais ce cas en une seconde.

---

## 7bis. La CI a refusé mon domicile, et elle avait raison

Premier push, `pytest shard 3` rouge sur une garde **préexistante** :
`test_ui_interaction_primitives.py::test_the_family_stays_small`.

`interaction.css` est tenu à **six primitives réutilisables**. J'y avais écrit
la fermeture parce que son en-tête porte déjà la doctrine « cible tactile
44px » — et j'y ai fait apparaître quatre racines neuves : `btn`, `topbar`,
`foot`, `method-reminder`.

**La garde ne s'est pas trompée de cible.** `interaction.css` **crée** des
primitives ; la fermeture **ferme** des surfaces héritées. Deux métiers. Les
mélanger aurait transformé le fichier des primitives en dépotoir transversal —
lentement, et sans que personne ne le décide.

Réponse : **déménager**, pas élargir la liste autorisée. La fermeture vit
désormais dans `app/static/css/target_closure.css`, chargée après
`interaction.css`. **Aucune garde affaiblie.** Mesure refaite après le
déménagement : 0 violation, 0 rétrécissement, rendu identique.

---

## 8. Résultat

| | avant | après |
|---|---:|---:|
| cibles sous le standard produit (390 px) | **63** | **0** |
| non-conformités WCAG 2.2 AA | 0 | **0** |
| éléments rétrécis | — | **0** |
| console de séance — dogfood 49 étapes × 3 largeurs | vert | **vert** |

Le dogfood complet de phase 2 a été **rejoué intégralement** : bilan atteint,
0 champ sous le clavier, 0 cible < 44 dans la console, 0 débordement dur,
aucun défilement horizontal, aux trois largeurs. **La console n'a pas bougé.**

---

## 9. Gardes

**36 gardes neuves**, réparties en deux modules :

- `tests/test_target_size_taxonomy.py` — 21 gardes : la taxonomie, les deux
  prédicats (violation produit / non-conformité AA), les quatre défauts de la
  sonde, la parité des commentaires CSS, et l'interdiction d'atteindre la
  console.
- `tests/test_geometry_manifest.py` — 15 gardes : complétude du manifeste,
  détection directionnelle du rétrécissement, dérive structurelle.

**Sept plantations vérifiées.** Chaque garde a été mise en défaut en
replantant le défaut réel qu'elle protège, et exigée **rouge** :

| Défaut replanté | Garde | Verdict |
|---|---|---|
| `at.contains(el)` réintroduit | `..._never_accepts_an_ancestor_as_a_hit` | rougit |
| `scrollIntoView` retiré | `..._scrolls_before_hit_testing` | rougit |
| étiquette de champ texte comptée en `D` | `..._only_treats_choice_inputs_as_label_owned` | rougit |
| zone tactile étendue redevient violation | `..._extended_hit_area_satisfies_the_threshold` | rougit |
| exception d'espacement ignorée | `..._passes_aa_by_the_spacing_exception` | rougit |
| commentaire CSS ouvert sans `/*` | `..._comment_delimiters_are_balanced` | rougit |
| la fermeture atteint `.console__band` | `..._never_reaches_the_session_console` | rougit |

---

## 10. Relecture du relevé de décisions (`CLAUDE.md §5.2`)

`DESIGN_DECISIONS_UIV2_SURFACES.md`, décision par décision :

| Décision | Verdict |
|---|---|
| **Q1** — la connexion porte l'identité | **non concernée** — `/login` hors périmètre mesuré |
| **Q2** — ancre visuelle de l'accueil (barres de récupération) | **respectée** — 0 modification de `/`, seul le pied de page gagne une zone tactile invisible |
| **Q3** — « État du jour » replié | **respectée** — `open_disclosure_count` inchangé, aucun `<details>` ouvert |
| **Q4** — la ligne de série est un instrument | **respectée** — console `reference consumer`, dogfood rejoué vert, 0 sélecteur l'atteignant |
| **Q5** — trois rangs de surface | **respectée** — aucun conteneur ajouté, aucun rang changé ; les extensions `B` sont des pseudo-éléments **sans peinture** |
| **Tokens bleus** mesurés | **non concernée** — aucune couleur touchée par cette tranche |

`CLAUDE.md §5.3` — **jamais une soustraction seule** : rien n'est retiré.
`btn--sm` disparaît de trois boutons, remplacé **dans la même livraison** par
la taille pleine.

`CLAUDE.md §5.4` — **aucune couleur** introduite ni modifiée. La tranche est
entièrement géométrique.

---

## 11. Le carve-out architectural — verdict opérateur du 2026-08-20

L'exposition est **ACCEPTÉE**, et « Rouvrir pour éditer » est confirmé en **B**
(zone tactile ≥ 44, chrome discret) : une action rare et potentiellement
disruptive ne doit pas recevoir le poids visuel de l'action principale.

**Mais l'exposition a révélé une limite de la phase elle-même.** Cette tranche
améliore la qualité **mécanique** de surfaces dont le **modèle d'interaction
est hérité**. Agrandir proprement les zones tactiles d'un formulaire Profil qui
restera pénible à remplir ne transforme pas ce formulaire en bonne UX.

**Conséquence directe, versionnée ici** — `UIV3_VISUAL_BASELINE_01` ne peut
plus capturer toutes les surfaces de la même façon :

| Statut | Surfaces | Ce que la baseline peut faire échouer |
|---|---|---|
| **SOVEREIGN** | Home · Session | pixel · architecture · mécanique |
| **TRANSITIONAL** | Profile · Library · Progress · Dashboard · History | **mécanique seulement** |
| **UTILITY** | login · mot de passe · admin · exports | mécanique seulement |

Une baseline transforme ce qu'elle capture en **contrat**. Sans ce découpage,
`B9` **gèlerait la dette en la rendant contractuelle**.

Le découpage n'est pas seulement écrit : `scripts/geometry_manifest.py` porte
`SURFACE_STATUS` et `gate_is_allowed()`, et **une surface non inscrite est
traitée en `TRANSITIONAL`** — promouvoir une surface en `SOVEREIGN` doit être
un geste délibéré, jamais un défaut d'inscription. Six gardes le vérifient.

**Programme ouvert** : `AUREN_EXPERIENCE_ARCHITECTURE_V4` — `UX4_01`
PROFILE_DATA_ACQUISITION · `UX4_02` LIBRARY_WORKOUT_DISCOVERY · `UX4_03`
PROGRESSION_BODY_LEDGER (absorbe l'ancienne « Phase 4 ») · `UX4_04`
SHELL_MOTION_POLISH. Doctrines détaillées : `AUREN_UI_BLUEPRINT §5bis`.
**Aucune implémentation V4 dans cette tranche.**

---

## 12. Ce qui reste, et ce qui n'est pas fait

- **Cibles dans les `<details>` fermés : non mesurées, par construction.**
  Chromium y verrouille la mise en page (`content-visibility`), et les
  mesurer produirait 23 faux positifs — c'est arrivé en phase 2. L'inventaire
  est donc un **plancher**, pas un total. Les atteindre demande un harnais qui
  ouvre chaque disclosure — c'est le travail de `UIV3_VISUAL_BASELINE_01`, qui
  dispose déjà du vocabulaire d'actions `open_details`.
- **La frontière A/B de « Rouvrir pour éditer »** attend un verdict opérateur.
- **`Sb_OPS_CI_LINT_TIMEOUT_01`** reste ouverte et **hors queue UI**.
- `UI_DATA_GAP` **G6** et **G7** : inchangés, hors périmètre, confirmés par
  l'opérateur.
