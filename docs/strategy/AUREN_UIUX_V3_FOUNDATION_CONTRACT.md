# `Sx_UIV3_00` — AUREN UI/UX V3 · Foundation Contract

**Statut : `APPROVED — OPERATOR`** (2026-08-18, avec les amendements A/B/C de `Sx_UIV3_04 §1bis`)
**Portée : UI/UX uniquement.** Aucun algorithme, aucun calcul, aucune donnée
nouvelle, aucun modèle, aucune migration.

Ce document est **transversal aux pages**. Les specs de surface
(`Sx_UIV3_01` Home, `Sx_UIV3_02` Session) l'appliquent ; elles ne le
redéfinissent pas.

---

## 0. Pourquoi ce contrat existe

Trois constats mesurés en août 2026, sur le build réel, dans un navigateur :

| Constat | Mesure |
|---|---|
| L'accueil réserve un hero à hauteur fixe et n'en remplit pas les trois quarts | **422 px dont 115 vides** (27 %) |
| La cause de la recommandation n'est jamais visible sans interaction | **0 px** de récupération au-dessus de 844 px |
| La série courante de la console de séance est sous la ligne de flottaison | y = **843 px** à 390 px de large · **4,3 écrans** de document pour un exercice |
| Les cibles tactiles ne respectent pas le standard du dépôt | **161 occurrences** sous 44 px sur `/sessions/{id}` |

Aucune de ces quatre choses n'était visible dans le code, dans un test, ou
dans un rapport de sprint. **Les quatre ont été trouvées en ouvrant la page
dans un navigateur à la taille d'un téléphone.** Ce contrat existe pour que
la mesure devienne une étape, pas une découverte.

Il complète `CLAUDE.md §5` (contrat de livraison UI), qui reste prioritaire.

---

## 1. Surface hierarchy — trois niveaux, pas quatre

| Niveau | Contenu | Règle |
|---|---|---|
| **L1 — ACTION** | l'objet immédiatement actionnable et l'état courant | **toujours atteignable sans scroll** dans l'état par défaut |
| **L2 — EXPLICATION** | ce qu'il faut pour comprendre L1 | visible par défaut, **jamais replié** |
| **L3 — DÉTAIL** | historique, alternatives, analytique, contexte approfondi | repliable, déplaçable, supprimable |

**Règle bloquante.** Un élément L3 ne pousse jamais un élément L1 sous la
ligne de flottaison. Si c'est le cas, l'un des deux est mal classé.

**Corollaire de vocabulaire.** « Nécessaire à la décision » est un test
opérationnel, pas une opinion : si l'utilisateur ne peut pas juger l'action
sans l'information, elle est L2 ; s'il peut agir puis la consulter, elle est L3.

---

## 2. Action hierarchy — `ONE DOMINANT ACTION PER STATE`

Une action dominante **par état**, pas par écran. L'écran peut porter
plusieurs contrôles ; un seul est dominant à un instant donné.

| État | Action dominante |
|---|---|
| Accueil · recommandation disponible | `DÉMARRER` |
| Accueil · séance ouverte | `REPRENDRE` |
| Session · saisie d'une série | `VALIDER S2` |
| Session · repos | `PASSER LE REPOS` |
| Session · exercice terminé | `CONTINUER → E2` |
| Session · dernier exercice terminé | `TERMINER LA SÉANCE` |

**Ce que cela remplace.** La coexistence permanente de `Valider` et
`Valider · E2` est une **hypothèse de durcissement**, pas une cible. Elle a
été introduite pour réparer un chevauchement de libellés, pas parce que deux
actions simultanées étaient le bon modèle. §9 de ce contrat la tranche.

Les actions secondaires restent visuellement secondaires : pas de fond plein,
pas de casse capitale, pas de largeur pleine.

---

## 3. Target size

**Standard AUREN : 44 × 44 px CSS minimum** pour tout contrôle fréquent ou
séquentiel — c'est-à-dire tout ce qu'on touche plus d'une fois par séance.

- Le plancher WCAG 2.2 AA (24 × 24 px) est un **minimum absolu**, jamais une
  cible.
- Un contrôle sous 44 px doit être **nommé et justifié** dans la spec de sa
  surface. L'absence de justification vaut violation.
- **La mesure est faite dans le navigateur**, pas déduite du CSS : `padding`,
  `line-height` et `display` produisent des hauteurs que la feuille de style
  ne dit pas.

**Dette connue à la signature de ce contrat** : 161 occurrences sous 44 px sur
`/sessions/{id}`, dont 27 `label.segmented__option` à 32 px et le CTA de séance
à 38 px. Elle est inscrite dans la BUILD QUEUE, pas amnistiée.

---

## 4. Color semantics

| Rôle | Couleur | Usage |
|---|---|---|
| **Action / actif / focus** | ambre `#C8A24B` | CTA dominant, série courante, focus |
| **Origine système** | bleu `--t-blue-*` | ce que le moteur produit : phrase, score, proposition |
| **Structure** | graphite `#0F1318` / `#151A21` / `#1B2029` | fonds, filets |
| **Neutre / secondaire** | gris `--t-fg-2` → `--t-fg-faint` | readouts, indisponibilité structurelle |

Tokens bleus validés le 2026-08-18, **contraste mesuré sur `#0F1318`** :

| Token | Valeur | Ratio | Seuil |
|---|---|---|---|
| `--t-blue-fg` | `#7DD3FC` | **11,18:1** | ≥ 4,5 ✓ |
| `--t-blue-line` | `#4A7FB5` | **4,43:1** | ≥ 3,0 ✓ |
| `--t-blue-mid` | `#5FA8D3` | **7,13:1** | ≥ 3,0 ✓ |

**La récupération ne reçoit pas de palette.** Vert / orange / rouge est
**interdit** : c'est le vocabulaire de tout le marché, il ne survit pas au
daltonisme sans redondance, et il suggère un jugement médical que le produit
refuse. La forme porte le sens ; la couleur ne fait que le renforcer.

Toute couleur nouvelle est **promue en token avec sa mesure** avant usage
(`CLAUDE.md §5.4`). `var(--token-inexistant, #hex)` est interdit.

---

## 5. Recovery encoding

**Verrou métier, pas esthétique.** `zone_recovery` produit un `estimate` 0–1
dont la docstring dit qu'il n'est « pas une mesure, pas un pourcentage de
récupération physiologique ». Une barre remplie à 32 % **est** une affirmation
de pourcentage. Elle est donc interdite — ce qui élimine la solution retenue
par Gravl et Fitbod.

**La donnée publique est la bande qualitative**, pas l'estimate.

| Bande `RecoveryBand` | Segments | Libellé public |
|---|---|---|
| `LIKELY_AVAILABLE` | ▮▮▮ 3 | disponible |
| `PARTIALLY_RECOVERED` | ▮▮ 2 | récupération partielle |
| `LIKELY_FATIGUED` | ▮ 1 | encore chargée |
| `UNKNOWN` | ░░░ contour pointillé + hachure, **jamais rempli** | non mesurée |

**Interdits explicites :**

- `% recovered` sous toute forme
- barre continue proportionnelle à l'`estimate` brut
- feu tricolore vert / orange / rouge
- `unknown` rendu comme 0, comme vide, ou comme « disponible »

**`unknown` n'est pas une valeur basse : c'est une autre nature de chose.**
Il reçoit donc une **forme** différente, pas une intensité différente. Un
contour pointillé hachuré ne peut pas être confondu avec une zone chargée,
qui est pleine à un segment.

Le nombre de segments peut être affiné visuellement, **jamais augmenté au
point de suggérer une mesure plus fine que le domaine**. Quatre bandes → au
plus quatre états lisibles.

---

## 6. Progressive disclosure

`<details>/<summary>` est **autorisé** pour : alternatives · historique ·
justification étendue · données secondaires · réglages.

`<details>` est **interdit** pour : la cause centrale d'une décision affichée
sur la même surface.

> **Origine de la règle.** D2 rangeait l'origine et la raison de la
> recommandation derrière un `<details>`. D6, décidée après, a fait de la
> récupération **l'explication** de la recommandation. Une explication repliée
> ne peut pas être la cause visible d'une décision. Mesuré : 0 px de cause
> au-dessus du pli, et l'ouverture du pli **déplace la décision vers le bas**.

---

## 7. No-color-only state

Toute distinction porteuse de sens repose sur **au moins deux** signaux parmi :
forme · texte · remplissage · contour · position · motif · couleur.

La couleur ne compte jamais pour deux. Un état distingué par « ambre vs gris »
et rien d'autre est une violation.

---

## 8. Typography

Quatre rôles, pas davantage :

| Rôle | Usage | Indication |
|---|---|---|
| **display / action title** | la décision, le nom de l'exercice | 25–30 px, 700 |
| **body / readout** | valeurs, phrases | 14–15 px, 400–600 |
| **micro-label** | eyebrows, codes de zone, clés de section | 10–11 px, 0,14–0,2 em, capitales |
| **numeric / mono** | toute donnée comparable | `tabular-nums` **obligatoire** |

`tabular-nums` est obligatoire dès que des chiffres s'alignent verticalement
ou se comparent d'un coup d'œil : charges, répétitions, scores, compteurs.

Pile mono système, **zéro webfont** (règle existante `AUREN_STYLE_RULES §2`).

---

## 9. Density budget

Une surface mobile n'est pas réussie parce qu'elle « rentre ». Quatre mesures
sont **obligatoires** dans tout rapport de tranche UI :

1. **px utilisés avant le CTA dominant**
2. **px vides inutiles** (espace réservé et non rempli)
3. **nombre d'objets interactifs** dans la zone active
4. **scroll nécessaire avant l'action principale** — cible : **0 px**

Viewport de référence : **390 × 844**. Secondaires : **360 × 800** et
**430 × 932**. Les trois sont mesurés ; le plus étroit fait foi en cas de
conflit.

**Seuils d'échec.** Scroll > 0 px avant l'action dominante · px vides > 15 %
de la hauteur d'un bloc à hauteur réservée · débordement horizontal quelconque.

---

## 10. No-JS baseline

Toute opération critique fonctionne **sans JavaScript** : démarrer une séance,
saisir une série, l'enregistrer, naviguer entre exercices, terminer la séance.

JS autorisé **uniquement** en amélioration progressive : minuteur de repos,
confort de saisie, animations. Jamais comme condition de compréhension, jamais
comme condition de sauvegarde.

Inventaire JS versionné : `prefs_focus_rank.js`, `preview.js`,
`session_focus.js`. Tout quatrième fichier fait échouer une garde existante.

---

## 11. Guard taxonomy

**656 gardes UI réparties sur 39 modules** existent à la signature de ce
contrat. Une refonte ne peut pas les traiter comme un bloc.

| Tier | Nature | Règle de modification |
|---|---|---|
| **T1 — BUSINESS / DATA** | vérité métier, honnêteté des données, `unknown` reste `unknown`, aucun calcul inventé | **jamais affaiblie** par un redesign |
| **T2 — ACCESSIBILITY** | no-JS, cible tactile, contraste, nom accessible, pas de couleur seule, `prefers-reduced-motion` | **jamais supprimée** sans preuve équivalente ou supérieure |
| **T3 — INTERACTION CONTRACT** | ce qu'un contrôle fait et ce que son libellé revendique | modifiable **uniquement par une spec explicite** |
| **T4 — VISUAL CONTRACT** | classes, positions, tokens, snapshots | évolutif, **avec décision versionnée + baseline** |
| **T5 — LEGACY IMPLEMENTATION** | garde qui pinne une implémentation remplacée | **supprimable** quand la nouvelle spec la remplace |

**Règle absolue.** Tout test modifié pendant un build V3 déclare son tier dans
le diff. Un test T1 ou T2 modifié sans justification explicite **bloque la
tranche**.

**Règle anti-prison.** Une garde T4 ou T5 qui protège un choix officiellement
abandonné n'est pas un argument contre le redesign : elle est un élément à
migrer. Une docstring historique ne définit jamais le produit contre le
runtime actuel.

Registre détaillé : `AUREN_UIUX_V3_GUARD_MIGRATION_REGISTER.md`.

---

## 12. SPEC QUEUE

| # | Spec | Statut |
|---|---|---|
| 00 | `AUREN_UIUX_V3_FOUNDATION_CONTRACT` (ce document) — vérité, géométrie, budgets | **rédigé** |
| **00A** | `Sx_UIV3_00A_COCKPIT_CAPABILITY_CONTRACT` — grammaire instrumentale : escalier de contraste, profondeur, primitives, illumination d'état, retour au toucher, sémantique du mouvement, popover, view transitions, porte d'admission framework, glanceability | **rédigé** |
| 01 | `Sx_UIV3_01_HOME_CAUSAL_COCKPIT_SPEC` | **rédigé** |
| 02 | `Sx_UIV3_02_ACTIVE_EXERCISE_CONSOLE_SPEC` | **rédigé** |
| 03 | `Sx_UIV3_03_VISUAL_REGRESSION_A11Y_SPEC` | **rédigé** |
| 04 | `Sx_UIV3_04_HOME_SESSION_CONVERGENCE_SPEC` | **rédigé** — résout **7 conflits** entre 00/00A/01/02 et porte la Convergence Matrix + le Build Readiness Gate |

> **`04` amende `00` et `00A`.** Sept conflits ont été trouvés en confrontant
> les specs : profondeur mélangée à la sémantique (`00A §1.2` → **L0–L3
> seulement**) · rail virant ambre à la prescription (`01 §3` → **bleu jusqu'à
> la prescription, ambre au seul CommandDock**) · `rest` et `unknown`
> distingués par la couleur seule (`00A §4`) · `:active` mal classé
> accessibilité (**T3**, `focus-visible` = **T2**) · `loading` spécifié comme
> un `…` destructeur d'information · **`--t-blue-line` sous la cible 4:1 sur
> L2 et L3** · absence de token conforme pour l'inconnu.
> **En cas de divergence, `04` prévaut sur `00` et `00A`.**

**`00A` s'intercale volontairement entre le socle et les surfaces.** `00`
gouverne ce qu'on a le droit d'affirmer et où les choses se posent ; il est
muet sur la profondeur, l'illumination d'état et le mouvement. Une surface peut
satisfaire `00` entièrement et rester un document bien composé plutôt qu'un
instrument. `00A` ferme cet écart **avant** que 01 et 02 ne soient construites,
pas après.

### Décisions opérateur du 2026-08-18 — figées

| Blocker | Décision |
|---|---|
| **BLOCKER-1** — « Disponibilité » quitte la Home | **OUI.** Quatrième lecture d'état concurrente ; appartient à Progression / Analyse. |
| **BLOCKER-2** — Q2 `SUPERSEDE` | **OUI.** Les « 11 barres comme ancre Home » sont officiellement remplacées par **zones causales + tally compact**. Le relevé 11 zones reste une surface N2 future, jamais au-dessus du CTA. |
| **BLOCKER-3** — suppression des deux CTA permanents | **OUI.** L'état devient le contrôleur de la commande. |
| **BLOCKER-4** — dogfood complet du concept D | **OUI.** Aucune Future Console figée avant une séance complète sur 360 / 390 / 430. |

### Plateforme — figée

`FastAPI + Jinja SSR` **KEEP** · HTML/CSS natif **PRIMARY** ·
View Transitions / Popover / Anchor Positioning **ADOPT en enhancement** ·
HTMX **EVALUATE** · React / Vue / Next / React Native **REJECT** ·
Capacitor **FUTURE GATE V4**. Porte d'admission détaillée : `00A §9`.

---

## 13. BUILD QUEUE — **non exécutée**

Chaque tranche déclare : objectif visible · dépendances · fichiers possibles ·
fichiers interdits · tests · golden states · rollback · porte de revue humaine.

**Fichiers interdits pour toute la queue V3** (sans exception, sans dérogation
de prompt) : `app/services/recommendation.py` · `app/services/zone_recovery.py`
· `app/services/recovery_contract.py` · `app/models/**` · `migrations/**` ·
tout service métier. Une tranche UI qui a besoin d'y toucher est **bloquée** et
documente un `UI_DATA_GAP`.

| # | Tranche | Objectif visible | Dépend de | Fichiers possibles | Tests / golden | Rollback |
|---|---|---|---|---|---|---|
| **B0** | `UIV3_COCKPIT_LADDER_01` | l'escalier de surfaces devient perceptible (≥ 1,12:1 par marche) ; `--t-fg-faint` et `--t-amber-dim` réparés | **00A** | `home.css`, `app.css` | garde de contraste **sur le fond réel** | revert CSS |
| B1 | `UIV3_TOKENS_01` | les 3 tokens bleus existent et sont mesurés | 00, **B0** | `home.css`, `app.css` | garde de contraste sur token | revert CSS |
| B2 | `UIV3_HOME_CAUSE_01` | la cause est visible sans tap | 01 | `index.html`, `home.css`, `pages.py` (contexte seul) | HOME/reco, HOME/unknown | revert template |
| B3 | `UIV3_HOME_TALLY_01` | la ligne de bilan 11 zones | 01, B2 | `index.html`, `home.css` | HOME/partial | revert bloc |
| B4 | `UIV3_HOME_REJECTED_01` | « écarté — et pourquoi » | 01, B2, **G1** | `index.html`, `home.css`, `pages.py` | HOME/reco | revert bloc |
| B5 | `UIV3_HOME_DEPRIORITISE_01` | Disponibilité quitte l'accueil · État du jour replié | 01, D8 | `index.html`, partials | HOME/active | revert |
| **B6+B7** | **`UIV3_SESSION_EXECUTION_CONSOLE_01`** — **une seule vertical slice utilisateur** (décision opérateur 2026-08-18) : commande contextuelle · série courante **réellement** au-dessus du pli · états `set` / `rest` / `complete` · **suppression de l'architecture sticky remplacée**. Les quatre livrent **ensemble** ou la tranche n'existe pas. | 02, 04 | `exercise_card.html`, `session_detail.html`, `session_focus.css`, `app.css` | tous les golden SESSION, `S7` et `S8` inclus | revert vers `nav=stay`+`next` et la sticky |
| B8 | `UIV3_TARGETS_44_01` | 0 cible sous 44 px sur les surfaces V3 | 00 | CSS uniquement | garde de cible mesurée | revert CSS |
| B9 | `UIV3_VISUAL_BASELINE_01` | baselines capturées et versionnées | 03 | `scripts/`, `var/` | — | supprimer baselines |

**Porte de revue humaine** : chaque tranche s'arrête à `PR GREEN / MERGE
PENDING` avec un **rendu exposé** (`CLAUDE.md §5.1`). Aucune ne merge sans
`GO MERGE`.

**Porte de sortie spécifique à `UIV3_SESSION_EXECUTION_CONSOLE_01`.**
La tranche **ne passe pas en `ACCEPTED`** tant qu'une **séance complète réelle**
n'a pas été exécutée et **validée humainement** aux trois viewports
(360 / 390 / 430). Décision opérateur : `BLOCKER-4` est **recadré** — il n'est
plus une précondition de `B0`, il devient cette porte de sortie. Motif : les
prototypes sont statiques, on ne peut pas y enregistrer une série ; le dogfood
ne peut donc pas précéder la construction de la console.

---

## 14. Ce que ce contrat ne fait pas

- Il ne construit rien. Aucun fichier de `app/` n'est modifié par sa rédaction.
- Il ne remplace pas `CLAUDE.md §5`, qui reste prioritaire et versionné.
- Il ne tranche pas les **décisions produit** listées comme
  `BLOCKER` dans les specs 01 et 02 — celles-là appartiennent à l'opérateur.
