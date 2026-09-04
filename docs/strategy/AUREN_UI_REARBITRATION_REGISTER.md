# `AUREN_UI_REARBITRATION_REGISTER` — inventaire des contrats UI

---

# ⭐ CURRENT AUTHORITATIVE STATE — 2026-09-04

> ## 🔀 CHANGEMENT DE MODE — `PHILOSOPHICAL UI RE-DESIGN PASS`
>
> **Décision opérateur du 2026-09-04.** Le déroulé macro par familles s'arrête
> après la calibration `F9`. `F2` / `F3` / `F9` restent **valides comme
> ENTRÉES et CONTRAINTES**, mais **n'ont pas le droit de figer l'ontologie UI
> actuelle**.
>
> `F9` est marquée **`FOUNDATION_CALIBRATED` · `VISUAL_VALUES_PROVISIONAL`**.
> Aucune direction visuelle finale n'est superseded à ce stade.
>
> **Nouvelle question centrale, avant tout style :**
> *si nous concevions AUREN aujourd'hui, représenterions-nous cette
> responsabilité de cette façon ?*
>
> **Trois arbitrages indépendants par objet** — `RESPONSABILITÉ` →
> `MÉTAPHORE D'INTERACTION` → `EXPRESSION`. On ne saute jamais directement du
> composant actuel au niveau 3.
>
> **`79 / 79` doivent être revus — mais plus « survivre ».** Supprimer,
> fusionner ou transformer sont des améliorations valides.
>
> Champs ajoutés : `PHILOSOPHICAL_STATUS` (`UNREVIEWED` → `RESPONSIBILITY_DECIDED`
> → `METAPHOR_DECIDED` → `VISUAL_DECIDED`) · `CURRENT_METAPHOR` ·
> `ALTERNATIVE_METAPHORS` · `OPERATOR_DIRECTION` · `REINVENTION_DEPTH`
> (`D0` préserver · `D1` polir · `D2` refonte structurelle · `D3` nouvelle
> métaphore d'interaction · `D4` retirer / fusionner / remplacer).
>
> **Une décision antérieure est une preuve, pas une protection d'investissement.**

> **Seule cette section fait autorité.** Tout ce qui suit le séparateur
> `HISTORIQUE` est un instantané conservé pour la traçabilité et **ne doit
> jamais être lu comme l'état courant**.

## Dénominateur

**79 objets** · `CAP` 4 · `INT` 13 · `VIS` 47 · `SYS` 15.
`F1` 7 · `F2` 14 · `F3` 14 · `F4` 9 · `F5` 9 · `F6` 6 · `F7` 5 · `F8` 8 · `F9` 7 ·
`F10` 0 *(vue transverse, aucun objet propre)* — **somme 79**.

## Avancement

| | `CONTRACT` | `EVOLUTION` | `BUILD` | `VALIDATION` |
|---|---|---|---|---|
| **28 / 79** | `DECIDED` (`F2`, `F3`) | **27 / 79** `APPROVED` | **0 / 79** | **0 / 79** |

## Dispositions courantes — `A` ⟂ `B`

`A` ∈ {`KEEP`, `REMOVE`, `MOVE`, `MERGE`, `REPLACE`, `ADD`}
`B` ∈ {`POLISH`, `SIMPLIFY`, `REDUCE`, `STRENGTHEN`, `STANDARDIZE`, `RECOMPOSE`,
`REWRITE`, `CONSOLIDATE`, `SYSTEMATIZE`, `ACCESSIBILITY`, `RESPONSIVE`,
`CLEANUP`, `VERIFY`}

| `F2` | `A` | `B` | | `F3` | `A` | `B` |
|---|---|---|---|---|---|---|
| `INT-001` | KEEP | STANDARDIZE + CONSOLIDATE | | `VIS-015` | KEEP | SIMPLIFY + STANDARDIZE |
| `VIS-002` | KEEP | RECOMPOSE | | `VIS-016` | KEEP | STANDARDIZE |
| `VIS-003` | KEEP | STANDARDIZE | | `VIS-017` | **MERGE** → `VIS-018` | CONSOLIDATE |
| `VIS-004` | **MOVE** | CLEANUP | | `VIS-018` | KEEP | STRENGTHEN |
| `VIS-005` | KEEP | REDUCE + SYSTEMATIZE | | `VIS-019` | KEEP | STANDARDIZE |
| `VIS-006` | KEEP | CONSOLIDATE | | `VIS-020` | KEEP | SIMPLIFY + STANDARDIZE |
| `VIS-007` | KEEP | STANDARDIZE + POLISH | | `VIS-021` | KEEP | SIMPLIFY |
| `VIS-008` | KEEP | RECOMPOSE | | `SYS-022` | KEEP | CLEANUP |
| `CAP-009` | KEEP | STRENGTHEN | | `SYS-023` | KEEP | VERIFY + POLISH |
| `CAP-010` | KEEP | *→ `F5`* | | `SYS-024` | **REPLACE** | REDUCE + SYSTEMATIZE |
| `INT-011` | KEEP | ACCESSIBILITY + VERIFY | | `SYS-025` | **MERGE** | CONSOLIDATE + SYSTEMATIZE |
| `VIS-012` | KEEP | RECOMPOSE | | `SYS-026` | **REPLACE** | CLEANUP + SYSTEMATIZE |
| `VIS-013` | KEEP | RECOMPOSE | | `VIS-027` | **REPLACE** | SYSTEMATIZE |
| `SYS-014` | **REPLACE** | SYSTEMATIZE | | `VIS-028` | KEEP | STANDARDIZE + CONSOLIDATE |

## Contradictions

| # | État | Résolution |
|---|---|---|
| `C-01` | **OUVERTE** | véhicule canonique de l'alternative démotée — `F2`/`F5` |
| `C-02` | **OUVERTE** | 2 `btn--primary` sur surface souveraine : conversion ou exception nommée |
| `C-03` | **OUVERTE** | marqueurs `--past` / `--complete` ambre — déférée à `F5` |
| `C-04` | **OUVERTE** | emphase dépendante de l'état — déférée à `F8` |
| `C-05` | ✅ **FERMÉE** | trois rôles distincts : `ACTION_PRIMARY` · `ACTION_TERMINAL` · `SUPPORT_SUCCESS`. « Terminer la séance » est une **action** tant qu'elle n'est pas déclenchée ; elle ne consomme donc pas `SUPPORT_SUCCESS`. L'état accompli, lui, le peut. **Contrat sémantique fermé, valeur visuelle ouverte** → `PREVIEW ACTION/CONTAINER`. |
| `C-06` | ✅ **FERMÉE** *(gate de migration)* | `section-header` est une **primitive visuelle** ; `h1..h6` expriment la **structure sémantique**. `section-header ≠ h2`. Le merge unifie le **vocabulaire visuel**, pas la balise. `F3-A` devient `READY_WITH_GATE` : mapping des 11 occurrences non-`h2` requis avant build. **Le CSS ne décide jamais du niveau HTML.** |
| `C-08` | ✅ **FERMÉE** | `border-subtle` est un rôle valide. **`border-strong` n'est PAS créé d'office.** Le `VERIFY` de `SYS-023` décide si un second rôle de bordure existe réellement ; si oui il s'appellera `border-emphasis` et sera **justifié par sa fonction**, sinon un seul rôle survit. |
| `C-09` | ✅ **FERMÉE** | **Propriété séparée, sans recouvrement.** `SYS-074` possède les **noms de rôles** de bordure · `SYS-023` possède la **mécanique et la valeur** visuelles · `SYS-078` possède **quand** la profondeur exige une séparation visuelle. |
| `C-10` | ✅ **FERMÉE / BUILD DIFFÉRÉ** | Le **contrat** `SYS-076` peut être approuvé maintenant ; la **migration visible des 8 icônes de coque est différée à `F1`**. Les deux `OTHER` (sans `viewBox`, `width=0`) sont inspectés **séparément** : ils ne doivent pas être normalisés en silence. |
| `C-11` | ✅ **FERMÉE** | L'interdiction de `§4` porte sur l'**encodage de récupération**, pas sur les rôles UI généraux. `support-success` / `-warning` / `-error` restent valides pour le feedback de formulaire, l'erreur, le succès d'opération, l'avertissement système. **Mais `RECOVERY BAND`, `RECOVERY ZONE` et `RECOVERY ESTIMATE` ne peuvent jamais consommer une sémantique « feu tricolore ».** La récupération continue de porter son sens par la **forme, les segments, le texte, le motif, le remplissage** ; la couleur ne fait que renforcer. *(Ouverte puis fermée le 2026-09-04.)* ⚠ **Trouvée en vérifiant `§4`.** Le contrat interdit explicitement le vocabulaire **vert / orange / rouge** — *« La récupération ne reçoit pas de palette … il ne survit pas au daltonisme sans redondance, et il suggère un jugement médical que le produit refuse. »* Or `SYS-074` crée `support-success` · `support-warning` · `support-error`, exactement ce vocabulaire. **L'interdiction est-elle limitée à l'encodage de récupération, ou vaut-elle pour tout feedback de support ?** Les rôles peuvent exister sans que leurs valeurs violent `§4` — mais la frontière doit être écrite. |
| `C-07` | ✅ **FERMÉE** | `class="card pstate"` n'est **pas** une carte imbriquée : c'est **un seul élément composant deux responsabilités**. `pstate` = bloc d'état et structure interne · `card` = chrome de groupe autonome · `pstate--flat` = état ne justifiant aucun conteneur. **Composition conservée**, aucune fusion, aucune primitive nouvelle. |

## Contrats superseded — **préparés, non appliqués**

| Contrat ancien | Remplacé par | Condition d'application |
|---|---|---|
| `SYS-014` « ambre = action utilisateur » | **`SYS-074`** (ontologie des rôles) | `SYS-CTA-AMBER-01` **rétrogradé** en contrainte de thème/mapping |
| `FOUNDATION_CONTRACT §8` Typography | **`SYS-075`** | `SUPERSEDES` explicite **après approbation + `PREVIEW TYPOGRAPHY`** |
| Système d'ombres (`--shadow-sm/md`) | **`SYS-078`** | après `PREVIEW CHROME` |
| Générations `--t-*` et `--color-*` | **`SYS-073`** | après table de migration complète ; deviennent des **alias de transition** |
| `FOUNDATION_CONTRACT §9` Density budget | **AUCUN** | ✅ **conservé intégralement** — il mesure des outcomes, pas des tokens |

## `READY` / `HOLD`

| Slice | État | Condition |
|---|---|---|
| `F3-A` titres | **`READY_WITH_GATE`** | mapping sémantique des 11 `card__title` non-`h2` |
| `F3-C1` rayons | **`READY`** | remplacements **strictement isométriques** seulement |
| `F3-G1` inline | **`READY`** | inventaire + allowlist uniquement, aucun code produit |
| `F9-M1` table de migration des tokens | **`READY`** | `SYS-073` — inventaire seul, aucun code |
| `F9-M2` matrice de couples de contraste | **`READY`** | `SYS-077` — mesure seule, aucun code |
| `F9-M3` mapping des 25 `font-size` | **`READY`** | `SYS-075` — mapping seul ; **tailles finales après `PREVIEW TYPOGRAPHY`** |
| `F3-C2` rayons à géométrie contractée | **`READY`** *(débloqué)* | `SYS-078` **ne possède plus le rayon** → `SYS-022` peut nommer ses exceptions |
| `F3-B` espacement | `HOLD` | `PREVIEW DENSITY` |
| `F3-G2` migration inline | `HOLD` | `PREVIEW TYPOGRAPHY` (127 typo) · `PREVIEW DENSITY` (261 espacement) · `SYS-074` mappé (44 couleur) |
| `F3-D2` · `F3-E` ambre | `HOLD` | rôles créés, **valeurs non arbitrées** |
| `F3-D1` · `F3-H` | `HOLD` | `PREVIEW CHROME` |
| `F3-F` | `HOLD` | `PREVIEW ACTION/CONTAINER` + `F2` non construite |
| `F3-I` `border-strong` | `HOLD` | **`C-08`** — le `VERIFY` est désormais contraint par le rôle |
| `F9-E1` mise en conformité des 8 icônes | `HOLD` | **`C-10`** — préempterait `F1` |

**Aucun build lancé.** La prochaine étape est la **convergence visuelle**.


## `F9` — VISUAL LANGUAGE · **ARBITRÉE 2026-09-04**

### Corrections de doctrine imposées par l'opérateur

| Point | Ce que j'avais proposé | Doctrine retenue |
|---|---|---|
| `SYS-073` | trois couches systématiques | **`COMPONENT` seulement si nécessaire.** Un composant sans sémantique propre consomme directement les tokens sémantiques. Les anciens namespaces deviennent des **alias de transition**. **Règle dure : aucun code neuf ne consomme un nom hérité.** |
| `SYS-074` | « `ADD` — aucun rôle nommé n'existe » | ⚠ **FAUX, corrigé par l'opérateur et vérifié à la source.** `FOUNDATION_CONTRACT §4` nomme déjà quatre rôles : *Action / actif / focus* · *Origine système* · *Structure* · *Neutre / secondaire*. C'est donc un **`REPLACE` + `EXPAND`** d'une ontologie existante, pas une création. **Incomplet aussi :** 17 rôles minimum, en 6 groupes. **`origin-system ≠ support-information`** — la provenance n'est pas une nature de feedback. **`action-primary ≠ state-active`** même s'ils aliasent aujourd'hui la même valeur. `SYS-CTA-AMBER-01` **rétrogradé** : contrainte de thème/mapping, **pas** l'ontologie. |
| `SYS-075` | dériver l'échelle des valeurs fréquentes | **Non.** *« 12px utilisé 105 fois ne prouve pas que 12px est une bonne décision. »* Rôles (`DISPLAY/ACTION` · `SECTION` · `BODY/READOUT` · `META/MICRO`) + modificateurs (`NUMERIC` avec `tabular-nums` obligatoire, `EMPHASIS`). **Le numérique n'est plus un niveau concurrent.** |
| `SYS-076` | « une graisse, deux tailles » | **Rejeté** — le projet a déjà un contrat plus précis : `viewBox 0 0 24 24`, `stroke-width 2`, cap/join ronds, `fill none`, `currentColor`, Tabler source primaire ; tailles **16 · 20 · 24 · 32 · 48** par rôle. **Classification obligatoire avant migration** ; le contrat ne vaut que pour `FUNCTIONAL_ICON`. |
| `SYS-077` | ratio par token | **Le contraste est un contrat de COUPLE, pas une propriété intrinsèque.** Matrice de couples autorisés, mesurée sur les compositions **réellement rendues**, pas sur les variables de `:root`. `no-color-only-state` préservé. |
| `SYS-078` | « le rayon est une propriété de la couche » | **Rejeté.** **Forme et élévation sont deux dimensions indépendantes.** `SYS-022` possède la forme/rayon ; `SYS-078` possède profondeur de surface, relation bordure/élévation, traitement d'ombre. Un composant peut avoir un rayon contracté sans être élevé. |
| `SYS-079` | remplacer par un système de tokens | **Non.** Le **density budget** de `FOUNDATION_CONTRACT §9` est **conservé** — il mesure des *outcomes* : px avant le CTA dominant, px vides, objets interactifs, scroll avant action (cible 0). La densité **compose** espacement + typographie + géométrie de contrôle. **Ne pas graver deux modes avant `PREVIEW DENSITY`.** |

### Décisions

| ID | `A` | `B` | Conséquence normalisée |
|---|---|---|---|
| `SYS-073` | **MERGE** | `CONSOLIDATE` + `SYSTEMATIZE` | `PRIMITIVE → SEMANTIC → COMPONENT (si nécessaire)`. Table de migration obligatoire : *token hérité → cible → consommateurs → statut*. **101 tokens, 3 générations, 2527 réf.** dont **79 % sur la génération héritée**. |
| `SYS-074` | **REPLACE** | `SYSTEMATIZE` + `EXPAND` | **Remplace les 4 rôles grossiers de `§4`.** 16 rôles en 6 groupes : surface (3) · texte (4) · **structure (1, + `border-emphasis` SEULEMENT si `SYS-023` prouve un besoin distinct)** · action/interaction (4) · provenance (1) · support (4). **Aucune valeur couleur arbitrée.** |
| `SYS-075` | **REPLACE** | `CONSOLIDATE` + `SYSTEMATIZE` + `POLISH` | 4 rôles + 2 modificateurs. Les **25 valeurs** sont mappées une par une (`CURRENT VALUE / CONSUMERS / TARGET ROLE / KEEP-ABSORB-EXCEPTION / WHY`). Tailles finales **seulement après `PREVIEW TYPOGRAPHY`** sur Home · Séance · Progression · Profil, 390×844 + desktop. |
| `SYS-076` | **KEEP** | `STANDARDIZE` + `ENFORCE` | Contrat Tabler appliqué aux seules `FUNCTIONAL_ICON`. **Classification faite : 8 / 16.** |
| `SYS-077` | **KEEP** | `STRENGTHEN` + `ACCESSIBILITY` | **Matrice de couples autorisés** : `FG · BG · contexte · texte/non-texte · minimum · mesuré · verdict`. Mesure sur compositions rendues. |
| `SYS-078` | **REPLACE** | `REDUCE` + `SYSTEMATIZE` | Surface par défaut **sans ombre** ; **un seul** traitement d'élévation sémantique pour le flottant/overlay. **Ne possède pas le rayon.** `PREVIEW CHROME` obligatoire. |
| `SYS-079` | **KEEP** | `SYSTEMATIZE` + `RESPONSIVE` | `§9` conservé. Espacement en trois couches ; `line-height` **transféré à `SYS-075`**. Densité **par contexte d'usage**, pas par page. `PREVIEW DENSITY` obligatoire à 390×844 avec les 4 métriques du contrat. |


### `F9-M3` — mapping des 25 valeurs de `font-size` · **mesuré, 407 usages**

> Le mapping n'est **pas** dérivé de la fréquence. La fréquence dit ce que
> l'implémentation fait ; elle ne dit pas ce qui est juste.

| Valeur | Usages | Consommateurs représentatifs | Rôle cible | Verdict | Pourquoi |
|---|---|---|---|---|---|
| `46px` | 1 | `.console[data-state=rest] .rest-readout` | **`DISPLAY / INSTRUMENT` + `NUMERIC`** | à évaluer **avant** de conclure à l'exception | ⚠ **Correction opérateur.** Le minuteur doit d'abord être évalué comme un rôle plein — grande valeur d'instrument lue pendant l'effort — et non classé exception par défaut. |
| `34px` · `32px` · `28px` · `24px` | 9 | `.ze__n`, `.kpi__value`, `.global-score`, `.kpi-card__value` | **remappés un par un** | **ABSORB** | ⚠ **Correction opérateur : `NUMERIC` est un MODIFICATEUR, pas un rang de taille.** Chaque consommateur reçoit son rôle propre — `DISPLAY + NUMERIC` pour une valeur de décision, `BODY/READOUT + NUMERIC` pour une valeur comparable, `META/MICRO + NUMERIC` pour une métadonnée chiffrée. |
| `26px` · `24px` · `22px` | 3 | `.today-home__title` aux trois points de rupture | `DISPLAY/ACTION` | **ABSORB** | Un seul élément, trois valeurs : c'est une **échelle responsive**, pas trois rôles. |
| `18px` | 8 | `.page-title`, `.user-profile__score b` | `DISPLAY/ACTION` | KEEP *(candidat)* | Titre de page. |
| `17px` · `16px` · `15px` | 26 | `.body-intelligence__headline`, `.tile__label`, `.exercise-card__name` | `SECTION` | **ABSORB** | Trois pas pour un même rang de titre de bloc. |
| `14px` | 52 | **`html, body`**, `.topbar__brand` | `BODY/READOUT` | KEEP *(base)* | Base du document. |
| `13px` | **101** | **`.section-header`**, `.card__title`, `.topbar__link` | `SECTION` | **⚠ voir ci-dessous** | — |
| `13.5px` · `12.5px` · `11.5px` · `10.5px` | 15 | `.ze-row__n`, `.cockpit__reasons`, `.dock__sub`, `.console__delta-label` | `META/MICRO` | **ABSORB** | Demi-pixels : dérive d'ajustement, pas décision. |
| `12px` | **105** | `.tooltip-content`, `.user-profile__data li` | `META/MICRO` | KEEP *(candidat)* | Métadonnée. |
| `11px` | 55 | `.kpi__label`, `.badge`, `.chip` | `META/MICRO` | **ABSORB** | Se distingue mal de 12 px. |
| `10px` | 20 | `.coach-tag`, `.implicit-pill` | `META/MICRO` | **ABSORB** ou EXCEPTION | À trancher au rendu : lisibilité en dessous de 11 px. |
| `9px` | 2 | `.ze-cap` · ~~`.setline--future .setline__marker`~~ | `META/MICRO` pour `.ze-cap` | **hors périmètre** pour le marqueur | ⚠ **Le marqueur `DF-C` est un CONTRAT DE GLYPHE, pas une taille de texte.** Il **sort de l'analyse typographique** et reste possédé par `SYS-076` / le contrat de glyphe. |
| `0.9em` · `0.85em` · `0.8125rem` | 3 | `.session-focus__card--active > summary`, requête `max-width: 380px` | à mapper vers un **rôle** | **MAP, ne pas convertir** | ⚠ **Correction opérateur : `em`/`rem` ne sont pas une dette en soi.** La dette est la **valeur non contractée**. Cible : `TYPE TOKEN → valeur primitive relative là où c'est pertinent` — pas une doctrine « tout en px ». |

#### Petit texte — règle candidate, **pas une interdiction**

> ⚠ **Ne grave pas « < 11 px interdit ».**
>
> `TEXTE INFORMATIF < 11 px` → **`EXCEPTION_REQUIRES_EVIDENCE`**
> `GLYPHE FONCTIONNEL` → possédé par `SYS-076` / le contrat de glyphe
>
> Chaque texte ≤ 10 px est revu individuellement : contenu · rôle · viewport ·
> contraste · importance · lisibilité · `keep / increase / glyph`.
> La recommandation Apple 11 pt sert de **preuve d'appoint**, jamais de seuil
> de conformité web.

#### ⚠ Inversion de hiérarchie mesurée

`html, body` est à **14 px**, tandis que **`.section-header` et `.card__title`
sont à 13 px**. **Le titre de bloc est plus petit que le corps de texte qu'il
introduit.** Ce n'est pas un choix consigné ; c'est le résultat de 25 valeurs
sans échelle. Toute échelle candidate doit le résoudre explicitement.

---

### `SYS-076` — classification des 16 `<svg>` inline · **mesurée**

| Classe | N | Détail |
|---|---|---|
| **`FUNCTIONAL_ICON`** | **8** | `app-rail__icon` ×4 · `app-bottom-nav__icon` ×4 — `viewBox 24` ✓, mais **`stroke-width` 1.7 au lieu de 2**, et **22 px au rail** (taille non autorisée) |
| `CUSTOM_AUREN_GLYPH` | 2 | `setline__glyph--warmup` / `--work` — **contrat `DF-C`, hors périmètre Tabler** |
| `BODYMAP / ILLUSTRATION` | 4 | `wa-silhouette` ×2, `ze-sil`, bannière `welcome` (`viewBox 0 0 780 340`) |
| `OTHER` | 2 | `zone_exposure` (sans `viewBox`, `width=0`) · `index.html` (sans `viewBox`) — **à inspecter** |

---

---
---

# 📁 HISTORIQUE — `HISTORICAL SNAPSHOT — NON AUTHORITATIVE`

> ⚠️ **Tout ce qui suit est conservé pour la traçabilité des décisions.**
> Les dénominateurs, dispositions et statuts qui y figurent ont été **dépassés**.
> Aucun agent ne doit en extraire un état courant : voir
> ⭐ `CURRENT AUTHORITATIVE STATE` ci-dessus.


> ⚠️ **MODE : AMÉLIORATION EXHAUSTIVE** — décision opérateur du 2026-09-04.
>
> **Les 78 objets sont dans le périmètre.** La priorité dit *quand*, jamais *si*.
> `KEEP` signifie désormais **« conserver la responsabilité / le contrat »**, et
> **jamais** « laisser l'implémentation en l'état ». Chaque objet reçoit au
> moins une disposition d'évolution.
>
> Fin de chantier : `0 UNREVIEWED · 0 UNPROPOSED · 0 APPROVED non planifié ·
> 0 BUILT non validé`.
>
> ⚠️ **CE DOCUMENT EST UN INVENTAIRE, PAS UN DESIGN APPROUVÉ.**
>
> Toute ligne porte `UNREVIEWED` tant que l'opérateur n'a pas rendu sa décision.
> Aucune opinion opérateur n'est inférée d'une décision antérieure. Une
> recommandation d'agent n'est pas une décision.
>
> Recensé le **2026-09-03** sur la canonique `4549d8f` (= production).

---

## 0. Trois niveaux de vérité, résolus explicitement

| Niveau | Ce que c'est | Autorité |
|---|---|---|
| **CURRENT RUNTIME** | ce que le produit rend aujourd'hui | les gabarits, le CSS, le JS servis |
| **CURRENT NORMATIVE CONTRACT** | ce qu'une spec vivante exige | `AUREN_UI_BLUEPRINT §2.5`, specs `UIV3`/`UX4` actives |
| **HISTORICAL CONTRACT** | ce qu'une spec disait avant d'être dépassée | rapports de sprint, `§2.4` du blueprint |

**`AUREN_UI_BLUEPRINT §2.4` est HISTORIQUE** : il décrit encore la Séance comme
« spécifiée, non construite » et l'Accueil en `MERGE PENDING`. Les deux sont
mergées et **en production**. `§2.5` — *quatre instruments, quatre questions* —
reste **normatif**.

---

## 1. Recensement initial · `HISTORICAL SNAPSHOT — NON AUTHORITATIVE`

> ⚠️ **CORRECTION DU DÉNOMINATEUR — 2026-09-04.** Le « 78 · CAP 12 / INT 18 /
> VIS 30 / SYS 18 » annoncé le 2026-09-03 était une **estimation non énumérée**.
> Les objets ont maintenant été énumérés un par un, avec un `PRIMARY_FAMILY`
> unique chacun. **Le total réel est 79.** Les identifiants `X-*`, `D-*` et
> `C-*` sont des *findings*, des doublons et des contradictions : ils ne
> deviennent pas des objets du dénominateur.

| | |
|---|---|
| **Objets décidables énumérés** | **79** |
| `CAP` — capacités produit | **4** |
| `INT` — contrats d'interaction | **13** |
| `VIS` — composants visuels | **47** |
| `SYS` — règles transverses | **15** |
| Familles de revue | 10 · dont **`F10` = 0 objet propre** |
| Contrat ≠ runtime | 7 (`X-*`) |
| Contrats doublons ou chevauchants | 9 (`D-*`) |
| Contradictions ouvertes | 4 (`C-*`) |

**`F10` n'a aucun objet propre.** C'est une **vue** sur les objets dont les
`RELATED_FAMILIES` incluent « transverse » — `btn` appartient déjà à `F2`,
`card` à `F3`. Le compter comme famille aurait doublé cinq objets.

### Mesures brutes, non interprétées

| Mesure | Valeur |
|---|---|
| Routes `GET` | 58 · dont **4 primaires**, 9 secondaires |
| Classes d'action distinctes | **19** · 93 occurrences de `btn` |
| Occurrences de `card` | **88** |
| `<details>` dans les gabarits | **52** |
| Règles CSS visant un `<summary>` | 27 |
| Tokens de couleur distincts référencés | **100** |
| **Styles `inline` dans les gabarits** | **373** |
| Planchers tactiles sous 44 px | 9 (inventoriés, gelés) |

---

## 2. Objets où le CONTRAT et le RUNTIME divergent

| ID | Objet | Contrat | Runtime | Nature |
|---|---|---|---|---|
| `X-01` | `CausalRail` | primitive nommée (`Sx_UIV3_01`) | n'existe pas ; la responsabilité vit sous `cockpit__zones` | **nom** |
| `X-02` | `ZoneTally` | primitive nommée (`Sx_UIV3_01 §5`) | n'existe pas ; vit sous `cockpit__tally-item` | **nom** |
| `X-03` | Slot primaire « Programmes » | — | ouvre `/library`, dont le titre est « Explorer » | **promesse** |
| `X-04` | `/progress/body` — État des zones | instrument nommé par `§2.5` | **404** | **capacité absente** |
| `X-05` | Statut des surfaces | `§2.4` : Séance « non construite » | mergée, 4 tranches, en production | **doc périmée** |
| `X-06` | `.session-focus__card--skipped` | état de carte | **0 occurrence** dans les gabarits | **CSS mort** |
| `X-07` | `btn--primary` sur surface souveraine | `VIS-003` : le CommandDock possède l'action dominante | 2 occurrences — `index.html`, `session_detail.html` | **propriété disputée** |

### ⚠ Corrections de census, vérifiées à la source le 2026-09-04

| Ce que j'avais écrit | Ce que la source dit | Vérifié par |
|---|---|---|
| `btn--wide` = « emphase », rang CTA | `width: 100%` **et rien d'autre** | lecture CSS |
| `btn--end` « ne termine pas lui-même » | `class="btn btn--end dock__cmd"`, `action=end` **clôt la séance** ; c'est une **variante du CommandDock**. Le commentaire que j'avais cité parle de l'ÉTAT de console qui y conduit, pas du bouton | lecture gabarit + routeur |
| `btn--ghost` « même hauteur » = défaut | il hérite du `padding` de `.btn` : **même cible tactile, masse visuelle différente**. Cible ≠ masse | lecture CSS |
| `SYS-014` « ambre = action utilisateur » | contrat élargi par l'opérateur : **action dominante OU objet/état actif** | décision `SYS-014` |

---

## 3. Contrats doublons ou chevauchants

| ID | Doublon | Détail |
|---|---|---|
| `D-01` | `btn--sm` / `btn--small` | deux noms, une intention |
| `D-02` | `btn--secondary` | 3 occurrences, **uniquement dans `dashboard.html`** — surface dépréciée qui redirige |
| `D-03` | Trois générations de tokens | `--fg-*` (310 réf.) · `--t-fg-*` (80) · `--color-fg-*` (45) coexistent |
| `D-04` | Navigation secondaire | rendue **trois fois** : `☰` topbar, « Plus » du rail, et le `☰` sur mobile |
| `D-05` | `/library` | atteignable en primaire (« Programmes ») **et** en secondaire (« Explorer ») |
| `D-06` | `card__title` / `section-header` | deux primitives de titre de bloc, usage non séparé |
| `D-07` | `dock__cmd` / `btn--primary` | deux véhicules pour « action dominante ». **`btn--wide` en est retiré** : mesuré, il ne porte que `width: 100%` — utilitaire de mise en page, aucun rang |
| `D-08` | `dock__alt` | rendu **six fois de deux façons incompatibles** : `<button class="dock__alt">`, `<a class="dock__alt">`, et une fois `<button class="btn btn--ghost dock__alt">` |
| `D-09` | Deux échelles d'espacement | `--space-1..5` **et** `--space-sm/md/lg/2xl` coexistent |

---

## 4. Familles · `HISTORICAL SNAPSHOT — NON AUTHORITATIVE`

| # | Famille | Objets | `CONTRACT` | `EVOLUTION` |
|---|---|---|---|---|
| `F1` | Navigation / shell | 7 | `UNREVIEWED` | `UNPROPOSED` |
| **`F2`** | **Action hierarchy / CTA** | **14** | **`DECIDED`** | **`PROPOSED`** |
| **`F3`** | **Chrome / containers** | **14** | `UNREVIEWED` | **`PROPOSED`** |
| `F4` | Data readouts | 9 | `UNREVIEWED` | `UNPROPOSED` |
| `F5` | Session input | 9 | `UNREVIEWED` | `UNPROPOSED` |
| `F6` | Information hierarchy | 6 | `UNREVIEWED` | `UNPROPOSED` |
| `F7` | Disclosure / density | 5 | `UNREVIEWED` | `UNPROPOSED` |
| `F8` | Feedback / state | 8 | `UNREVIEWED` | `UNPROPOSED` |
| `F9` | Visual language | 7 | `UNREVIEWED` | `UNPROPOSED` |
| `F10` | *(vue transverse, 0 objet propre)* | 0 | — | — |
| | **SOMME** | **79** | **14 / 79** | **28 / 79** |

---

## 5. `F2` — tableau d'inventaire · `HISTORICAL SNAPSHOT — NON AUTHORITATIVE`

> ⚠️ La colonne « Statut » emploie l'ancien vocabulaire pré-normalisation (`IMPROVE`, `REDUCE`). **Voir `A`/`B` dans l'état courant.**

`SOURCE OF CONTRACT` : `B` = blueprint/spec versionnée · `R` = runtime seul ·
`O` = décision opérateur antérieure.

| ID | Objet | Surfaces | Runtime aujourd'hui | Contrat | Source | Statut |
|---|---|---|---|---|---|---|
| `INT-001` | Action dominante unique par état | Séance | une commande pleine largeur par état | « une commande par état » | `B` `O` | **KEEP** |
| `VIS-002` | `dock__cmd` — commande dominante | Séance | bouton ambre pleine largeur | véhicule de `INT-001` | `B` | **IMPROVE** |
| `VIS-003` | `btn--primary` | 43 occurrences, transverse | ambre plein | action primaire de page | `R` | **IMPROVE** |
| `VIS-004` | `btn--wide` | 17 occurrences | `width: 100%` **seulement** | utilitaire de mise en page | `R` | **MOVE** |
| `VIS-005` | `btn--ghost` — action secondaire | 39 occ. · 23 gabarits | contour ; **même cible tactile**, masse moindre | action secondaire | `R` | **REDUCE** |
| `VIS-006` | `dock__alt` — alternative démotée | Séance | lien texte discret | sortie manuelle, démotée par `DF-B` | `O` | **KEEP** |
| `VIS-007` | `btn--danger` | 4 occurrences | rouge | action destructive | `R` | **KEEP** |
| `VIS-008` | `btn--end` — terminer la séance | Séance | `btn btn--end dock__cmd`, fond `--ok` | **variante terminale du CommandDock ; clôt réellement la séance** | `O` | **IMPROVE** |
| `CAP-009` | « Choisir une autre séance » | Accueil | lien texte sous le CTA | capacité de contournement de la reco | `O` | **IMPROVE** |
| `CAP-010` | « Adapter » — substitution | Séance | bouton sur la carte active | règle de données : aucune série de travail faite | `B` `O` | **KEEP** |
| `INT-011` | Validation implicite | Séance | `Entrée`/`Done`, jamais au `blur` | `DF-B`, `D9`/`D10` préservés | `O` | **KEEP** |
| `VIS-012` | `DÉMARRER` de l'accueil | Accueil | ambre pleine largeur + flèche | CTA unique du héros | `O` | **IMPROVE** |
| `VIS-013` | `Créer un programme` | Mes programmes | ambre plein, au-dessus de la liste | action primaire de la surface | `R` | **IMPROVE** |
| `SYS-014` | Rôle de l'ambre | transverse | **19 réf. `--t-amber`, 114 `--accent`** | « ambre = action utilisateur » | `B` | **IMPROVE** |

---

## 6. Journal des décisions

### `F2` — ACTION HIERARCHY / CTA · **arbitrée le 2026-09-04**

| ID | Décision | Note brute opérateur | Conséquence normalisée | Conséquence transverse |
|---|---|---|---|---|
| `INT-001` | **KEEP** | — | Une action dominante par état reste le contrat. | — |
| `VIS-002` | **IMPROVE** | *« Garder CommandDock comme propriétaire de la commande dominante. Je veux cependant explorer une matérialisation plus instrumentale, plus précise et moins "gros bouton web". »* | Le CommandDock **conserve la propriété** de l'action dominante sur les surfaces souveraines. Sa **matérialisation** est ouverte : cible ≥ 44 px préservée, masse et chrome à réinventer vers un registre d'instrument. | `PREVIEW_REQUIRED` |
| `VIS-003` | **IMPROVE** | *« primaire générique de page/formulaire »* | `btn--primary` reste le primaire des pages et formulaires. **Sur une surface souveraine à état dérivé, il ne peut pas porter l'action dominante** — le CommandDock la possède. | 2 occurrences en conflit (`X-07`) |
| `VIS-004` | **MOVE** | *« Full-width ne porte aucune sémantique d'importance. »* | `btn--wide` est reclassé **utilitaire de mise en page**. Il sort de la famille CTA et ne peut plus être lu comme un rang. | 17 occurrences reclassées ; retiré de `D-07` |
| `VIS-005` | **REDUCE** | *« Conserver une hit target confortable. Réduire fortement la masse/chrome visible des secondaires. Créer si nécessaire un niveau tertiaire encore plus discret. »* | **Cible tactile préservée** (≥ 44 px, plancher produit). **Masse visible fortement réduite.** Un **niveau tertiaire** est autorisé s'il est nécessaire — il devra être une primitive nommée, pas un cas particulier. | **39 occurrences · 23 gabarits** |
| `VIS-006` | **KEEP** | — | L'alternative démotée reste démotée. | contredit par `D-08` |
| `VIS-007` | **KEEP** | — | Le destructif garde son traitement. | — |
| `VIS-008` | **IMPROVE** | *« Conserver TERMINER LA SÉANCE comme action dominante réelle. Ne pas supprimer encore sa variante terminale. »* | Action dominante **réelle** et reconnue comme telle. La variante terminale (`--ok`, verte) **est conservée en l'état** jusqu'à comparaison. | `PREVIEW_REQUIRED` — A terminal vert actuel · B CommandDock standard · C terminale plus discrète |
| `CAP-009` | **IMPROVE** | *« Plus découvrable, mais toujours tertiaire face à la recommandation. »* | La capacité est **préservée**. Découvrabilité augmentée, **rang tertiaire maintenu** : elle ne doit jamais concurrencer la recommandation. | consommateur du niveau tertiaire de `VIS-005` |
| `CAP-010` | **KEEP** | *« Capacité non négociable. Apparence à arbitrer en F5. »* | Capacité intouchable. **Apparence explicitement déférée à `F5`.** | ouvre un point `F5` |
| `INT-011` | **KEEP** | — | Validation implicite inchangée : `Entrée`/`Done`, jamais au `blur`. `D9`/`D10` préservés. | — |
| `VIS-012` | **IMPROVE** | *« Conserver exactement UNE action dominante Home. Réduire / réinventer sa masse visuelle. »* | **Exactement une** action dominante sur l'accueil — invariant. Masse visuelle à réduire ou réinventer. | `PREVIEW_REQUIRED` · lié à `VIS-002` |
| `VIS-013` | **IMPROVE** | *« aucun programme → création primaire ; programmes existants → création compacte, contenu dominant. »* | **Emphase contextuelle** : le rang de l'action dépend de l'état de la surface. Nouveau contrat d'interaction — l'emphase n'est plus statique. | ouvre un point `F8` (états) |
| `SYS-014` | **IMPROVE** | contrat candidat fourni | voir `SYS-CTA-AMBER-01` ci-dessous | **65 violations mesurées** |

---

## 6bis. `F2` — NORMALISATION `A` ⟂ `B` · 2026-09-04

`A` ne contient plus que `KEEP · REMOVE · MOVE · MERGE · REPLACE · ADD`.
`IMPROVE`, `REDUCE` et `KEEP+IMPROVE` en sont **bannis** — ils mélangeaient les
deux axes.

| ID | `A` contrat | `B` évolution |
|---|---|---|
| `INT-001` | **KEEP** | `STANDARDIZE` + `CONSOLIDATE` |
| `VIS-002` | **KEEP** | `RECOMPOSE` |
| `VIS-003` | **KEEP** | `STANDARDIZE` |
| `VIS-004` | **MOVE** | `CLEANUP` |
| `VIS-005` | **KEEP** | `REDUCE` + `SYSTEMATIZE` |
| `VIS-006` | **KEEP** | `CONSOLIDATE` |
| `VIS-007` | **KEEP** | `STANDARDIZE` + `POLISH` |
| `VIS-008` | **KEEP** | `RECOMPOSE` |
| `CAP-009` | **KEEP** | `STRENGTHEN` |
| `CAP-010` | **KEEP** | `UNPROPOSED` → `F5` |
| `INT-011` | **KEEP** | `ACCESSIBILITY` + `VERIFY` |
| `VIS-012` | **KEEP** | `RECOMPOSE` |
| `VIS-013` | **KEEP** | `RECOMPOSE` |
| `SYS-014` | **REPLACE** | `SYSTEMATIZE` |

**`SYS-014` = `REPLACE`** : l'ancien contrat « ambre = action utilisateur » est
**remplacé** par `SYS-CTA-AMBER-01`. Un `SUPERSEDES` est **préparé, non
appliqué** — aucune spec normative n'est modifiée à ce stade.

### Détail des cibles d'évolution `F2` · `HISTORICAL SNAPSHOT` — colonne `A` pré-normalisation

`A` = disposition de contrat (arbitrée) · `B` = disposition d'évolution (ma proposition).

| ID | `A` contrat | `B` évolution | Cible concrète | Type | Priorité |
|---|---|---|---|---|---|
| `INT-001` | KEEP | `STANDARDIZE` `CONSOLIDATE` | supprimer les **2 exceptions** où `btn--primary` porte l'action dominante sur une surface souveraine (`C-02`) | B | **P0** |
| `VIS-002` | KEEP+IMPROVE | `RECOMPOSE` | matérialisation instrumentale : cible ≥ 44 px conservée, chrome et masse repensés | B | **P0** · `PREVIEW` |
| `VIS-003` | KEEP | `STANDARDIZE` | cantonner explicitement à page/formulaire ; interdit comme dominante sur surface souveraine | B | **P0** |
| `VIS-004` | MOVE | `CLEANUP` | sortir de la famille CTA ; documenter comme utilitaire ; 17 occurrences relues sans changement de rendu | A | P1 |
| `VIS-005` | REDUCE | `REDUCE` `SYSTEMATIZE` | masse réduite sur **39 occ. / 23 gabarits** ; niveau **tertiaire nommé** créé comme primitive, pas comme cas particulier | B | **P0** |
| `VIS-006` | KEEP | `CONSOLIDATE` | **un seul véhicule canonique** pour l'alternative démotée — résout `C-01` | B | **P0** |
| `VIS-007` | KEEP | `STANDARDIZE` `POLISH` | même langage destructif partout : aucun style inline, même densité, même cible, même interaction | B | P2 |
| `VIS-008` | IMPROVE | `RECOMPOSE` | variante terminale conservée jusqu'à comparaison A/B/C | B | P1 · `PREVIEW` |
| `CAP-009` | IMPROVE | `STRENGTHEN` | découvrabilité accrue **au rang tertiaire** — premier consommateur du niveau créé par `VIS-005` | A | P1 |
| `CAP-010` | KEEP | *déféré* | apparence arbitrée en `F5` ; capacité intouchable | — | `F5` |
| `INT-011` | KEEP | `ACCESSIBILITY` | vérifier la parité clavier / sans-JS du contrat `Entrée`/`Done` ; aucun changement de comportement | A | P2 |
| `VIS-012` | IMPROVE | `RECOMPOSE` | exactement une dominante sur l'accueil ; masse réduite ou réinventée | B | **P0** · `PREVIEW` |
| `VIS-013` | IMPROVE | `RECOMPOSE` | emphase **dépendante de l'état** — nouvelle primitive, dépend de `F8` (`C-04`) | B | P1 |
| `SYS-014` | IMPROVE | `SYSTEMATIZE` | **65 violations** à résorber par catégorie | B | **P0** |

---

## 6bis-2. Règles transverses candidates, issues de `F2`

### `SYS-CTA-AMBER-01` — rôle de l'ambre · *candidat, non approuvé*

```
AMBRE  =  action utilisateur DOMINANTE
       ou OBJET / ÉTAT ACTIF

AMBRE ≠  décoration générique
       ≠ succès
       ≠ métrique neutre
       ≠ origine système non active
```

**Mesuré sur les cinq feuilles** : 134 règles emploient l'ambre.

| | Règles | Exemples |
|---|---|---|
| **Légitime — action dominante** | 11 | `.btn--primary`, `.today-home__cta`, `.profile-preview__cta` |
| **Légitime — objet/état actif** | 58 | `:checked`, `aria-pressed="true"`, `--in-progress`, `:focus` |
| **VIOLATION — décoration / structure** | **44** | `.card--signal`, `.tile--primary`, `.template-card`, `.exercise__code` |
| **VIOLATION — origine système non active** | **11** | `.insight`, `.machine-panel__tag`, `.substitute-badge`, `.bi-priority--info` |
| **VIOLATION — métrique neutre** | **8** | `.kpi__value`, `.grade-badge--b`, `.coach-ratio__strength`, `.rest-readout__value` |
| **VIOLATION — succès / passé** | **2** | `.setline--past .setline__marker`, `.setline--complete .setline__marker` |
| | **65 violations** | |

### `SYS-CTA-MASS-01` — masse des secondaires · *candidat, issu de `VIS-005`*

> **La cible tactile et la masse visuelle sont deux contrats distincts.**
> Un secondaire garde une cible ≥ 44 px et perd son chrome.

Consommateurs mesurés : **39 occurrences de `btn--ghost` dans 23 gabarits** —
`body_overview` (5), `squad_detail` (5), `detail` (5), `admin_sessions` (2),
`history` (2), `profile` (2), `session_detail` (2), et 16 autres à une occurrence.

---

## 6quater. `F3` — CHROME / CONTAINERS · **ARBITRÉE 2026-09-04**

### Corrections de doctrine imposées par l'opérateur

| Point | Ce que j'avais proposé | Doctrine retenue |
|---|---|---|
| `VIS-028` | « `tile` devient une présentation de `btn` » | **Faux.** Une tile est un **objet composite distinct**. Elle partage tokens d'action, focus, pressed, disabled, règles de hiérarchie et de cible — **sa géométrie et sa composition lui restent propres.** |
| `SYS-025` | « migrer vers l'échelle nommée, majoritaire à 73 % » | **La majorité n'est pas un argument.** Cible : `primitive spacing values → semantic aliases → component usage`. Migration mécanique **seulement après mapping exhaustif**. |
| `SYS-026` | `A = KEEP` | **`A = REPLACE`.** Nouveau contrat : *no uncontracted static inline visual style*. L'inline ne survit que pour une valeur réellement dynamique, **explicitement allowlistée**. |
| `SYS-022` | « 0 rayon en dur » | **Cible : 0 valeur INEXPLIQUÉE hors système.** Une géométrie spéciale **contractée et nommée** reste légitime. |

### Décisions

| ID | `A` | `B` | Note brute opérateur | Conséquence normalisée |
|---|---|---|---|---|
| `VIS-015` | **KEEP** | `SIMPLIFY` + `STANDARDIZE` | *« Une card signifie un GROUPE AUTONOME. Une information simple ne reçoit pas automatiquement fond + bordure + radius. Interdire les nested cards sans responsabilité autonome. »* | Le conteneur explicite devient un **signal de groupe autonome**. Imbrication interdite sauf responsabilité autonome propre. |
| `VIS-016` | **KEEP** | `STANDARDIZE` | *« Aucune cinquième variante sans nouvelle sémantique. `signal` ne dépend plus de l'ambre. »* | Les 4 variantes reçoivent une définition écrite. Création d'une variante = création d'une sémantique. `--signal` sort de l'ambre. |
| `VIS-017` | **MERGE** → `VIS-018` | `CONSOLIDATE` | *« Supprimer le vocabulaire parallèle. »* | `card__title` disparaît. |
| `VIS-018` | **KEEP** | `STRENGTHEN` | *« vocabulaire canonique … rangs explicites … respecter parallèlement la hiérarchie HTML réelle, pas seulement le style. »* | Primitive unique, **rangs section / sous-section**, et **le niveau de titre HTML doit être juste**, pas seulement l'apparence. |
| `VIS-019` | **KEEP** | `STANDARDIZE` | *« dominante d'abord dans le DOM ; secondaires ensuite ; masse réduite ; responsive sans changer la hiérarchie logique. »* | Ordre **DOM** canonique, indépendant du rendu responsive. |
| `VIS-020` | **KEEP** | `SIMPLIFY` + `STANDARDIZE` | *« NE PAS fusionner automatiquement pstate dans card … son implémentation doit partager les fondations visuelles. »* | `pstate` **garde son identité** ; il partage surface / bordure / rayon / espacement avec le socle commun. |
| `VIS-021` | **KEEP** | `SIMPLIFY` | *« La liste porte le rythme … les enfants ne reçoivent un cadre que lorsqu'ils sont eux-mêmes des groupes autonomes. »* | Fin des bordures concentriques. |
| `SYS-022` | **KEEP** | `CLEANUP` | *« 0 unexplained hardcoded radius … exceptions géométriques permises si nommées et contractées. »* | Une échelle gouvernante + un registre d'exceptions **nommées**. |
| `SYS-023` | **KEEP** | `VERIFY` + `POLISH` | *« Vérifier si border-strong encode réellement une différence … sinon proposer plus tard sa fusion, sans changement arbitraire maintenant. »* | **Mesure d'abord, décision ensuite.** Aucun changement immédiat. |
| `SYS-024` | **REPLACE** | `REDUCE` + `SYSTEMATIZE` | *« DEFAULT SURFACE no shadow ; TRUE ELEVATED one semantic elevation treatment. »* | Deux états seulement. Les surfaces ordinaires portent la profondeur par **surface + bordure**. |
| `SYS-025` | **MERGE** | `CONSOLIDATE` + `SYSTEMATIZE` | *« Ne pas migrer simplement `--space-1` vers `--space-sm` par préférence nominale. »* | Modèle à trois niveaux. **Mapping exhaustif obligatoire avant toute migration.** |
| `SYS-026` | **REPLACE** | `CLEANUP` + `SYSTEMATIZE` | *« STATIC VISUAL RULE → class/token/primitive ; INLINE → uniquement dynamique et autorisé. »* | **703 des 708 déclarations sont statiques (99,3 %)** ; **5 seulement sont dynamiques**, toutes des `width`. L'allowlist a donc une taille mesurée : **5**. Garde de non-remontée obligatoire. |
| `VIS-027` | **REPLACE** | `SYSTEMATIZE` | *« Le signal doit recevoir une sémantique … Ne pas remplacer l'ambre par une nouvelle couleur décorative universelle. »* | La responsabilité « signaler un bloc » reste ; la couleur devient **sémantique** (information / warning / error / success), jamais décorative. |
| `VIS-028` | **KEEP** | `STANDARDIZE` + `CONSOLIDATE` | *« Conserver tile comme composant composite/actionnable distinct. NE PAS transformer tile en btn. »* | La tile **partage** accent sémantique, focus, pressed, disabled, hiérarchie d'action, règles de cible — et **garde sa géométrie**. |

---

## 6ter. Contradictions détectées — **à arbitrer, non résolues**

| # | Contradiction | Détail |
|---|---|---|
| **C-01** | `VIS-005 REDUCE` × `VIS-006 KEEP` | `dock__alt` est rendu **de deux façons incompatibles** : lien texte nu dans `exercise_card.html`, et `btn btn--ghost dock__alt` dans `session_detail.html`. Réduire la masse des ghosts change l'un et pas l'autre. **Quel est le véhicule canonique de l'alternative démotée ?** |
| **C-02** | `VIS-003 IMPROVE` × runtime | `btn--primary` apparaît sur **les deux surfaces souveraines** — `index.html` et `session_detail.html` — où votre décision donne la propriété au CommandDock. Deux occurrences à trancher : conversion, ou exception nommée. |
| **C-03** | `SYS-CTA-AMBER-01` × `DF-C` | `.setline--past` et `.setline--complete` colorent leur marqueur en ambre. Sous le nouveau contrat, l'ambre signifie « actif » — or une série passée ne l'est pas. Mais `DF-C` a délibérément fait porter l'ÉTAT par la couleur du marqueur. **Arbitrage `F5`, pas ici.** |
| **C-04** | `VIS-013` × `F8` | L'emphase contextuelle introduit un contrat dépendant de l'état (vide / peuplé) qui n'existe dans aucune primitive actuelle. À reprendre en `F8`. |
| **C-05** | `VIS-027 REPLACE` × `VIS-008 KEEP` | `VIS-027` donne au signal une sémantique incluant **succès**. Or `btn--end` emploie déjà `--ok` comme couleur d'**action dominante terminale**. Un même token porterait alors deux sens — *succès* et *action*. **Quel token porte le succès, et lequel porte l'action terminale ?** |
| **C-06** | `VIS-017 MERGE` × `VIS-018` « hiérarchie HTML réelle » | Mesuré : `section-header` est **toujours** un `<h2>` (23/23). `card__title` est **incohérent** — `h2`×24, `h3`×8, `span`×2, `h1`×1. La fusion force donc une décision de **niveau de titre sur 11 cas non-`h2`** : c'est une décision sémantique, pas de style. |
| **C-07** | `VIS-020 KEEP` × `VIS-015` imbrication | ⚠ **Correction de mon census** : `pstate` n'est pas confiné au Profil — il vit aussi dans `plan.html`. Et il apparaît **composé avec `card`** (`class="card pstate"`). Ce n'est donc pas « `pstate` ou `card` » : les deux **s'empilent déjà**. Sous `VIS-015`, cette composition est-elle une responsabilité autonome légitime, ou une imbrication à supprimer ? |

---

## 6quinquies. Tranches `F3` — `READY` / `HOLD`

| Slice | Décisions | `READY_TO_BUILD` | Bloqueur exact |
|---|---|---|---|
| **`F3-A`** convergence des titres | `VIS-017` `VIS-018` | **YES** | — · *décide aussi les 11 niveaux de titre non-`h2` (`C-06`)* |
| **`F3-C1`** rayons **isométriques** | `SYS-022` (sous-ensemble) | **YES** | — · **uniquement les remplacements à valeur identique, 0 changement visuel** |
| `F3-C2` rayons à géométrie contractée | `SYS-022` (reste) | HOLD | exceptions à nommer et contracter d'abord |
| `F3-D1` cœur carte · imbrication · titre | `VIS-015` `VIS-021` `VIS-020` | HOLD | `PREVIEW CHROME` |
| `F3-D2` variante `signal` | `VIS-016` (part) `VIS-027` | HOLD | **`SYS-CTA-AMBER-01` non approuvé** |
| `F3-B` espacement | `SYS-025` | **HOLD** | **`F9`** — architecture primitive / semantic token non validée |
| `F3-E` l'ambre quitte le chrome | `VIS-027` + 44 violations | HOLD | **`SYS-CTA-AMBER-01` non approuvé** |
| `F3-F` vocabulaire d'action | `VIS-028` `VIS-019` | HOLD | `PREVIEW ACTION/CONTAINER` + `F2` non construite |
| `F3-G1` **inventaire + allowlist** inline | `SYS-026` (préparation) | **YES** | — · aucun code produit, **5 déclarations dynamiques** identifiées |
| `F3-G2` migration inline | `SYS-026` (exécution) | HOLD | **`F9`** |
| `F3-H` ombres | `SYS-024` | HOLD | `PREVIEW CHROME` |
| `F3-I` `border-strong` | `SYS-023` | HOLD | mesure `VERIFY` à produire d'abord |

### Previews regroupées — jamais une par objet

| Preview | Objets |
|---|---|
| **`PREVIEW CHROME`** | `VIS-015` + `VIS-021` + `SYS-024` |
| **`PREVIEW ACTION/CONTAINER`** | `VIS-028` + `VIS-002` + `VIS-012` + `VIS-008` |

---

## 7. Modèle d'état du registre *(définitions — toujours valides)*

| Champ | Valeurs |
|---|---|
| `CONTRACT_STATUS` | `UNREVIEWED` → `DECIDED` |
| `EVOLUTION_STATUS` | `UNPROPOSED` → `PROPOSED` → `APPROVED` |
| `BUILD_STATUS` | `NOT_STARTED` → `IN_PROGRESS` → `BUILT` |
| `VALIDATION_STATUS` | `UNVALIDATED` → `VALIDATED_RUNTIME` → `VALIDATED_VISUAL` |

### Avancement · `HISTORICAL SNAPSHOT`

*(voir l'état courant en tête)*

---

## 7bis. ADN UI émergent — **hypothèses, non approuvées**

Dérivé uniquement des décisions `F2`. À valider ou rejeter en bloc plus tard.

1. **La cible tactile et la masse visuelle sont deux contrats distincts.**
2. **Une surface souveraine a un propriétaire d'action dominante ; les autres primitives s'y effacent.**
3. **Le rang ne se lit pas dans la largeur** — `width: 100%` ne dit rien de l'importance.
4. **L'ambre est un signal d'action ou d'activité, pas une couleur de marque.**
5. **L'emphase peut dépendre de l'état de la surface** (vide / peuplé).

---

## 8. Ce que ce document n'est pas

* Il **ne remplace aucune autorité**. Il les inventorie.
* Il **ne supersède rien** tant qu'une décision opérateur ne le dit pas
  explicitement, avec un `SUPERSEDES <autorité>`.
* Il ne contient **aucune proposition visuelle**. Les rendus viennent après
  l'arbitrage, consolidés, jamais un par décision.
