# `AUREN_INSTRUMENTS` — l'ontologie du produit

> **Statut : `NORMATIF` sur les dispositions, `PROVISOIRE` sur les formes.**
> Écrit le 2026-09-06 sur arbitrage de l'opérateur, après lecture des vingt-deux
> objets rendus et découpés.
>
> Ce document répond à une question que `AUREN_VISUAL_BACKBONE` ne pose pas :
> **combien d'objets l'utilisateur doit-il comprendre ?** Le socle dit comment
> une surface doit avoir l'air ; celui-ci dit **lesquelles ont le droit
> d'exister**.
>
> Compagnon obligatoire : `AUREN_VISUAL_BACKBONE` — en particulier `§5bis`
> (mode de rendu) et `§3` (le langage).

---

## 1. Le cadre

Le programme UI a passé deux nuits à **améliorer des composants**. Ce travail
n'est pas perdu — il est devenu l'infrastructure. Mais il laissait intacte
l'ontologie : vingt-et-un objets que l'utilisateur devait comprendre un par un,
dans un modèle encore proche du « document web sombre composé de cards ».

**Décision de l'opérateur :**

> Ne plus améliorer 21 composants. Transformer 21 objets hérités en **sept
> instruments cohérents**. Direction : une interface **diégétique** où chaque
> chose ressemble à un instrument qui a une fonction, pas à un composant HTML
> générique. Le viseur intra-séance est la première primitive instrumentale ;
> on en **dérive la grammaire**, on ne le duplique pas.

**L'objectif est de minimiser le nombre d'objets PERÇUS, pas de préserver le
nombre de composants implémentés.** Le composant HTML actuel n'est pas une
contrainte.

---

## 2. Les sept instruments

| Instrument | Question à laquelle il répond |
|---|---|
| **MISSION** | Qu'est-ce que je fais maintenant, et pourquoi ? |
| **EXECUTION** | Qu'est-ce que je fais sur cette série ? |
| **BODY_LEDGER** | Que sait AUREN de mon corps ? |
| **FLIGHT_RECORDER** | Qu'est-ce qui vient réellement de changer ? |
| **LOADOUT_BAY** | Avec quoi vais-je m'entraîner ? |
| **ACCOUNT** | Qui suis-je, comment mon compte fonctionne ? |
| **SQUAD_CHANNEL** | Que se passe-t-il dans mon groupe ? |

### 2bis. La huitième catégorie — `REFERENCE / DOCUMENT`, hors cockpit

Quatre surfaces ne sont **pas** des instruments, et ce n'est pas un oubli :

| Surface | Nature |
|---|---|
| `coach_report` + `coach_body_snapshot` | un **document** destiné à un tiers, imprimable |
| `export` | un **utilitaire** de sauvegarde |
| `science` + `science_diagram` | une **référence explicative** |
| `atlas` | une **référence anatomique** versionnée |

**Elles ne suivent PAS la grammaire d'instrument** — pas de focus frame, pas de
readout, pas de rail. Ce sont des pages servies, sobres.

AUREN a donc **un cockpit et des documents**, et c'est assumé. Le risque — deux
langages visuels — est accepté à une condition, qui est une règle :

> **Un document ne doit jamais avoir l'air d'un instrument en panne.**

La frontière doit être **perceptible** : un document se présente comme un
document, pas comme un cockpit vide de données.

---

## 3. Le test de survie d'un objet autonome

Un objet visuel n'a le droit d'exister séparément que s'il répond **oui à au
moins une** de ces questions :

1. Répond-il à une **question utilisateur unique** ? *(« quelle série
   maintenant ? »)*
2. Possède-t-il un **état propre important** ? *(repos / actif / terminé)*
3. Regroupe-t-il une **famille de données mentalement cohérente** ?
   *(le Body Ledger)*
4. Permet-il une **action que la donnée ne peut pas absorber** ? *(démarrer une
   séance)*
5. Doit-il rester **visible indépendamment** de ses voisins ? *(un minuteur
   actif)*

**Sinon : `MERGE` ou `REMOVE`.**

Deux corollaires opératoires :

* **si deux objets répondent à la même question → proposer une fusion** ;
* **si un objet n'a aucune question propre → proposer sa suppression.**

C'est ce test qui condamne `profil-reference`, et qui condamne la séparation
actuelle entre *Catalogue* et *Mes programmes* — deux destinations pour un seul
espace mental.

---

## 4. Le contrat d'un objet survivant

Tout objet visible par l'utilisateur porte les sept champs suivants :

`QUESTION` · `DATA` · `SOURCE` · `FRESHNESS` · `STATE` · `ACTION` ·
`DETAIL_LEVEL`

Et une distinction **dure**, jamais confondue :

> **donnée saisie · donnée importée · donnée dérivée.**

Les confondre dégrade la crédibilité analytique du produit, et le projet
l'avait déjà identifié.

### 4.1 Les contrats, avec leur service réel

Chaque `SOURCE` ci-dessous est **un service qui existe déjà**. La colonne dit
d'où vient la donnée, pas ce qu'il faudrait écrire.

#### MISSION

| Champ | Valeur |
|---|---|
| `QUESTION` | Qu'est-ce que je fais maintenant, et pourquoi ? |
| `DATA` | séance proposée · zones ciblées · **raison** · situation de la semaine · séance ouverte |
| `SOURCE` | `recommendation.recommend_next_session` → `top.template`, `top.phrase` *(la raison, ≤ 140 car.)*, `top.primary_zones` · `recommendation_explainer.explain_recommendation` → `primary_reason` + 1..3 `reasons` + `confidence` · `home._build_weekly_plan` · `session_state.latest_open_session` |
| `FRESHNESS` | la reco est calculée à la requête ; la séance ouverte porte `started_at` |
| `STATE` | `in_progress` · `reco` · `no_reco` — **les trois formes existent déjà** dans `home._build_today` |
| `ACTION` | reprendre · démarrer. **Le bloc entier porte l'action** — pas de gros bouton ajouté |
| `DETAIL_LEVEL` | L1 la mission · L2 le rail de situation · `SHEET` les **alternatives écartées avec leur zone limitante**, déjà calculées par `pages._home_causal_context` |

#### EXECUTION

| Champ | Valeur |
|---|---|
| `QUESTION` | Qu'est-ce que je fais sur cette série ? |
| `DATA` | exercice · cible · précédent · saisie courante · delta · repos |
| `SOURCE` | `briefing.build_chip` / `build_peek` · `delta.compute_delta` · l'état de console |
| `FRESHNESS` | temps réel |
| `STATE` | `✓ passé` · `● courant` · `○ futur` · `resting` · `correcting` · `complete` |
| `ACTION` | valider la série *(`Entrée` **ou** bouton — jamais l'un sans l'autre)* · ±15 s · passer le repos |
| `DETAIL_LEVEL` | L1 la série active · L2 la bande · L3 cues et alternatives · L4 méthode |

#### BODY_LEDGER

| Champ | Valeur |
|---|---|
| `QUESTION` | Que sait AUREN de mon corps ? |
| `DATA` | poids · taille · FC repos · mesures morphologiques · ratios · couverture |
| `SOURCE` | `BodyMeasurement` *(saisie)* · `User.height_cm` / `resting_hr` *(profil)* · `WorkoutSession.bodyweight_kg` *(séance)* · `FactProvenance` porte déjà `source` **et** `basis` |
| `FRESHNESS` | `measured_at` **et** `created_at` existent en base. `FactRow.measured_at` est peuplé et **jeté au gabarit** — c'est le geste le moins cher du programme. Échelle à hériter : `recovery_contract.Sufficiency` |
| `STATE` | `measured` · `derived` · `inferred` · `not_deductible` — vocabulaire de `MorphologyDescriptor` |
| `ACTION` | **on touche une valeur pour la modifier.** Plus de lien « Ajouter » qui saute trois blocs plus bas |
| `DETAIL_LEVEL` | L1 le ledger · `SHEET` la capture guidée |

#### FLIGHT_RECORDER

| Champ | Valeur |
|---|---|
| `QUESTION` | Qu'est-ce qui vient réellement de changer ? |
| `DATA` | résultat de la séance · dernier mouvement · exposition corporelle |
| `SOURCE` | `session_recap.build_recap` · `progression_view.build_progression_view` *(`lead` / `rows` / `trace`)* · `zone_exposure.build_zone_exposure` |
| `FRESHNESS` | `ended_at` de la séance · fenêtre d'exposition **fixe à 14 j** |
| `STATE` | `known` · `zero` · `partial` · `unknown` — les **quatre états sémantiques** de `zone_exposure`, où `partial` transforme les zéros en inconnus |
| `ACTION` | **aucune.** C'est une lecture |
| `DETAIL_LEVEL` | L1 le debrief · L2 le dernier mouvement · `SHEET` le détail par exercice |

#### LOADOUT_BAY

| Champ | Valeur |
|---|---|
| `QUESTION` | Avec quoi vais-je m'entraîner ? |
| `DATA` | manifest de séances : nom · durée · zones · provenance · statut |
| `SOURCE` | `pages._load_templates` + `template_zone_context.annotate_templates` *(catalogue)* · `user_program_drafts.list_drafts` *(personnels)* · `program_quality_engine` *(4 diagnostics calculables)* |
| `FRESHNESS` | sans objet |
| `STATE` | `ACTIF` · `MIENS` · `CATALOGUE` — ⚠ **`ACTIF` n'existe pas** (voir `§7`) |
| `ACTION` | **la ligne EST la commande.** Pas treize boutons identiques |
| `DETAIL_LEVEL` | L1 le manifest · `SCOPE STRIP` le filtre de zone, permanent · `SHEET` les diagnostics |

#### ACCOUNT

| Champ | Valeur |
|---|---|
| `QUESTION` | Qui suis-je, comment mon compte fonctionne ? |
| `DATA` | identifiant · email · statut · date d'inscription · mot de passe |
| `SOURCE` | `User` |
| `FRESHNESS` | `created_at` |
| `STATE` | actif |
| `ACTION` | modifier email · changer le mot de passe |
| `DETAIL_LEVEL` | L1 |

#### SQUAD_CHANNEL

| Champ | Valeur |
|---|---|
| `QUESTION` | Que se passe-t-il dans mon groupe ? |
| `DATA` | classement réduit *(rang · personne · **une** métrique)* · pulse d'activité |
| `SOURCE` | services `squads` · `SQUAD_ROLE_LABELS` pour les rôles |
| `FRESHNESS` | horodatage des activités |
| `STATE` | propriétaire · membre |
| `ACTION` | drill-down |
| `DETAIL_LEVEL` | L1 le pulse · `SHEET` le classement complet |

---

## 5. Les six primitives visuelles

**`card` cesse d'être une primitive souveraine.** Elle survit techniquement ;
visuellement, elle devient l'exception.

| Primitive | Rôle | Implémentation de référence |
|---|---|---|
| **`FOCUS FRAME`** | c'est ici que se passe l'action | `session_focus.css` `.setline--current` — **trois signaux simultanés** |
| **`READOUT`** | valeur + unité + delta + microtendance | `.console__delta*`, `.rest-readout__*` |
| **`RAIL`** | temps · semaine · séries · position | un `border-left: 2px`, jamais un contour |
| **`LEDGER`** | données stables + fraîcheur + provenance | *à construire* — `FactProvenance` en est la ligne |
| **`SCOPE STRIP`** | choix de contexte : 7/14/28 j, zone, programme | *à construire* |
| **`SHEET`** | **seule** couche d'édition complexe, de paramètres et d'explication | `<details>` natifs L3/L4 |

### 5.1 `FOCUS FRAME` — trois signaux, jamais un seul

`session_focus.css:2212-2222` :

1. **profondeur** — `background: var(--t-raised)`, une marche L3 au-dessus du
   fond ;
2. **halo** — `box-shadow: inset 0 0 0 1px` : un liseré **intérieur**, pas une
   ombre portée *(les ombres sont neutralisées)* ;
3. **marqueur** — `var(--t-amber)` avec la **seule lueur de tout le fichier**.

Plus la géométrie : `min-height` 34 → 56 px, la grille passe de 4 à 3 colonnes.

Variantes existantes : `--correcting` *(liseré **bleu** = rectification
système)* · `--resting` *(cadre **retiré** — la ligne redevient un rappel)*.

### 5.2 La discipline chromatique — déjà écrite, à généraliser

`session_focus.css:2534-2539` :

```
ambre plein     CommandDock, et rien d'autre
ambre ponctuel  marqueur de la série COURANTE
graphite        toute la structure
bleu            système : référence, analyse, aperçu produit par AUREN
```

**C'est la règle qui explique « pas de viseur partout ».** Deux ambres pleins
sur un écran, et l'ambre cesse de vouloir dire *c'est à toi de jouer*.

### 5.3 La bande d'état — trois porteurs distincts

`✓ passé` · `● courant` · `○ futur`, et une séparation stricte :

> le **glyphe** porte le TYPE · l'**ordinal** est du texte · le **marqueur**
> porte l'ÉTAT.

### 5.4 ⚠ Ce sur quoi le viseur ne doit PAS servir d'étalon

Le viseur est l'étalon de **grammaire de composition**, pas de typographie :

1. **Deux familles de tokens coexistent dans son fichier.** `--color-*`
   (déclarées localement) et `--t-*` (depuis `:root`). Elles **divergent** sur
   surface, surélevé, creusé et filet — l'ancienne échelle est celle
   qu'`app.css` qualifie de « trois marches sous le seuil de perception ».
2. **23 tailles de police distinctes**, dont 4 seulement passent par un token,
   avec des demi-pixels (10,5 · 11,5 · 12,5). C'est l'échelle la plus dispersée
   du dépôt.

---

## 6. Les dispositions

Six verdicts possibles : `PRESERVE` · `REINVENT` · `MERGE` · `MOVE` ·
`DELETE` · `DEFER`.

### 6.1 Les vingt-deux objets

| # | Objet | Verdict | Vers | Transformation |
|---|---|---|---|---|
| 1 | `profil-corps` | **MERGE + REINVENT** | BODY_LEDGER | Tête du ledger : poids · taille · FC repos · couverture morpho · **fraîcheur**. Plus de liens « Ajouter » |
| 2 | `profil-compte` | **MOVE** | ACCOUNT | Sort du corps. Email, statut et mot de passe n'ont aucune raison de couper l'instrument corporel |
| 3 | `profil-mesure` | **REINVENT** | BODY_LEDGER | Les 16 champs **jamais simultanés** : capture guidée, une valeur à la fois, protocole contextuel |
| 4 | `profil-morpho` | **MERGE** | BODY_LEDGER | Disparaît comme bloc → couche du ledger : représentation + disponible + manquant. Aucun grand état vide autonome |
| 5 | `profil-reference` | **DELETE** | — | Mélange Email + Taille + FC repos. Email → ACCOUNT, Taille/FC → BODY_LEDGER. **Redistribution, pas trou** |
| 6 | `seance-viseur` | **PRESERVE** | EXECUTION | Première primitive instrumentale. **Interdiction de micropatch maintenue** |
| 7 | `seance-exercice` | **REINVENT** | EXECUTION | Cesse d'être une card → **Set Instrument**. L'actif s'ouvre ; passé et futur deviennent des rails compacts |
| 8 | `seance-bilan` | **REDUCE + REINVENT** | EXECUTION | Seulement les signaux **non dérivables**. 2–3 entrées tactiles + note facultative |
| 9 | `seance-recap` | **REPLACE** | EXECUTION → FLIGHT_RECORDER | → **Debrief** : résultat · changement remarquable · prochaine conséquence. **Le détail rejoint FLIGHT_RECORDER** |
| 10 | `accueil-hero` | **REINVENT** | MISSION | → **Mission Briefing** : séance, durée, cible, raison. Le bloc entier porte l'action |
| 11 | `accueil-boucle` | **MERGE + REDUCE** | MISSION | → rail de situation sous Mission, pas une seconde longue card narrative |
| 12 | `accueil-etat` | **DEFER** ⚠ | — | Décommissionné, mais **ne part qu'avec la lecture d'état dérivée** — voir `§6.2` |
| 13 | `prog-releve` | **REINVENT** | FLIGHT_RECORDER | → readout de performance : charge · reps · delta · tendance courte. Plus trois puits indépendants |
| 14 | `prog-exposition` | **REPLACE VISUALLY** | FLIGHT_RECORDER | → BodyMap AUREN, 11 zones. **Jamais** de revendication d'activation musculaire |
| 15 | `biblio-carte` | **REPLACE** | LOADOUT_BAY | → **manifest** : nom · durée · zones · provenance · statut. **La ligne est la commande** |
| 16 | `biblio-filtre` | **REINVENT** | LOADOUT_BAY | Un `<details>` cache précisément l'information discriminante → `SCOPE STRIP` permanent, ou sélection sur le BodyMap |
| 17 | `social-classement` | **REDUCE** | SQUAD_CHANNEL | Six colonnes sur mobile n'ont aucune chance. Rang · personne · **une** métrique |
| 18 | `social-activite` | **MERGE** | SQUAD_CHANNEL | → **Squad Pulse**, flux temporel léger. Pas un instrument primaire |
| 19 | `social-partage` | **DEFER** ⚠ | — | Formulaire trop lourd pour sa valeur, mais **ne part qu'avec le lien d'invitation** — voir `§6.2` |
| 20 | `prog-liste` | **MERGE** | LOADOUT_BAY | « Mes programmes » et « catalogue » sont **le même espace mental** |
| 21 | `prog-qualite` | **REMOVE COMPOSITE** | LOADOUT_BAY | Le grade global donne une **précision artificielle**. Les 4 diagnostics explicables restent |
| 22 | `prog-rythme` | **MERGE** *(proposé)* | FLIGHT_RECORDER | Le rail de rythme 14 j. ⚠ **Jamais arbitré** — récupéré après la lecture du catalogue |

### 6.2 ⚠ `CLAUDE.md §5.3` — chaque suppression attend son remplaçant

> *« Une suppression part dans la même livraison que ce qui la remplace. »*

C'est un contrat versionné qu'un prompt ne peut pas désactiver. **Deux
suppressions sur quatre laissaient un trou et deviennent `DEFER` :**

| Suppression | Verdict | Pourquoi |
|---|---|---|
| `accueil-etat` | **DEFER** | Une **lecture d'état dérivée** a été annoncée — des performances et des déclarations de fin de séance. Le produit perdrait quelque chose de **promis** |
| `social-partage` | **DEFER** | Part avec le lien d'invitation / partage système |
| `profil-reference` | **DELETE confirmé** | Rien n'est perdu : le contenu est **redistribué** |
| grade composite | **REMOVE confirmé** | Les diagnostics restent. Seule la **fausse précision** disparaît |

**Conséquence de séquencement, à connaître avant de planifier MISSION :** la
**règle de dérivation de l'état** n'est pas décidée, et elle est désormais un
**prérequis** du retrait de `accueil-etat`.

### 6.3 Les cinquante gabarits qui n'étaient pas dans l'inventaire

L'arbitrage portait sur les objets **rendus et montrés**. Le produit compte
**63 gabarits rendables** (17 partiels · 36 pages · 10 sous-pages), dont 13
couverts. Voici les autres.

| Vers | Gabarits |
|---|---|
| **ACCOUNT** | `login` `register` `welcome` `forgot_password` `reset_password` `password_change` `contact` |
| **SQUAD_CHANNEL** | `squads_list` `squad_create` `squad_join` `squad_challenges` `squad_challenge_create` `squad_challenge_detail` `squad_compare` `user_profile` `profile_preview` `leaderboard` |
| **LOADOUT_BAY** | `user_programs/{list,new,detail,generate,publish,quality,plan,_status}` · `template_detail` · `launcher` |
| **BODY_LEDGER** | `body_assessment/{body_overview,measurement_form}` · `body_intelligence` + ses 3 partiels · `body_capture_quality` · `worked_area_body_map` · `muscle_focus` · `bodymap_frame_selector` |
| **FLIGHT_RECORDER** | `history` · `exercise_history` |
| **EXECUTION** | `rest_timer` · `overload_hint` |
| **MISSION** | `next_session_reco` |
| **`REFERENCE / DOCUMENT`** | `coach_report` · `coach_body_snapshot` · `export` · `science` · `science_diagram` · `atlas` |
| **meurt avec `accueil-etat`** | `readiness_history` |
| **déjà mort** | `dashboard` — aucune route ne le rend depuis `Sb_27.6` |
| **hors produit** | `admin_sessions` |

---

## 7. Ce que la donnée ne sait pas encore faire

Les instruments cibles décrivent des choses que le produit **ne calcule pas**.
Ce tableau existe pour qu'aucune maquette n'affiche un nombre qui n'existe pas.

| Trou | Bloque | État réel |
|---|---|---|
| **durée d'une séance** | MISSION · LOADOUT_BAY | **Aucune colonne** sur `WorkoutTemplate`, et rien ne l'estime. `UserProgramSession.duration_target_minutes` est une **cible déclarée**, jamais calculée ni vérifiée |
| **fenêtre 28 j** | BodyMap de FLIGHT_RECORDER | `zone_exposure.WINDOW_DAYS` est **fixe à 14**. Les fenêtres 24 h / 7 j / 14 j **par zone** sont calculées dans `recommendation._compute_signals` et **jamais rendues** |
| **programme ACTIF** | LOADOUT_BAY | Notion **inexistante**. `MAX_ACTIVE_PROGRAMS` veut dire « non archivé ». Un index DB la **prévoit en commentaire**, rien ne l'implémente |
| **progression intra-séance** | MISSION à l'état `LIVE` | `latest_open_session` rend l'entité ORM entière ; « X/Y séries » exige de charger `session_exercises → set_logs` |
| **fraîcheur d'une donnée corporelle** | BODY_LEDGER | N'existe pas pour le corps. Patron réutilisable : `recovery_contract.Sufficiency` + `readiness_sufficiency_for_age` |
| **règle de dérivation de l'état** | le retrait de `accueil-etat`, donc MISSION | ⚠ **décision produit non prise** |

### 7.1 Deux contraintes dures sur BODY_LEDGER

**`update_measurement` remet à NULL les champs absents**
(`body_profile.py:400-409`). Le formulaire actuel soumet l'ensemble, donc ça
marche. **Une capture guidée « une valeur à la fois » casserait ce contrat** :
chaque étape effacerait les autres mesures.

**`/profile` écrit des mesures sans consentement ni drapeau.** Les routes
`/body/*` vérifient toutes `has_active_consent` ; `POST /profile/measurements`
ne le vérifie pas. Cinq autres surfaces lisent aussi les mesures sans vérifier.
Ce n'est pas une question de cockpit — c'est une **décision produit sur le
périmètre du consentement**.

---

## 8. Ce qui est déjà calculé et qu'il suffit de brancher

Le diagnostic du programme — *le produit a la décision, pas le moyen de
l'appliquer* — se vérifie une dernière fois ici, et à son avantage : **une part
substantielle des instruments peut être bâtie en branchant l'existant.**

| Déjà calculé | Où | Aujourd'hui |
|---|---|---|
| la **raison** de la recommandation, ≤ 140 car. | `recommendation.py:642-751` | rendue |
| les **alternatives écartées avec leur zone limitante** | `pages._home_causal_context` | rendues |
| l'exposition 14 j, **4 états sémantiques** + provenance | `zone_exposure.py:209` | rendue |
| `lead` / `rows` / `trace`, ordre de **pratique** | `progression_view.py:197` | rendu |
| 4 diagnostics + **4 manquants nommés**, jamais notés 0 | `program_quality_engine.py:394` | rendus |
| la **provenance** d'une donnée corporelle | `FactProvenance` | calculée, **non rendue** |
| l'**horodatage** d'une mesure | `FactRow.measured_at` | calculé, transporté, **jeté au gabarit** |

Et le cas extrême, à connaître : **`app/services/adaptive_replan.py` — 387
lignes, `replan()` complet, 5 déclencheurs nommés — n'est importé par aucun
routeur et aucun service.** La décision existe en entier ; le moyen de
l'appliquer n'existe pas du tout.

Même famille : `WeeklyPlan.zone_coverage` porte 20 champs par zone dont la Home
lit deux clés · `build_weekly_loop` produit 14 clés, `/progress` en lit 2.

---

## 9. Ce qui n'est pas décidé

* la **règle de dérivation de l'état** — prérequis du retrait de
  `accueil-etat` ;
* le **périmètre du consentement** corporel ;
* la disposition de **`prog-rythme`** *(proposition : `RAIL` dans
  FLIGHT_RECORDER)* ;
* l'**ordre de bascule** des surfaces après BODY_LEDGER ;
* la **forme** des sept instruments — ce document fixe l'ontologie, pas le
  dessin. Les maquettes viennent après, et l'opérateur tranche sur rendu
  (`CLAUDE.md §5.1`).

---

## 10. Ce que ce document ne fait pas

Il **ne supersède pas** `AUREN_VISUAL_BACKBONE` : le socle reste l'autorité sur
la couleur, la profondeur, la typographie et les invariants. Ce document dit
**quels objets existent** ; le socle dit **de quoi ils ont l'air**.

Il ne fixe **aucune valeur** de taille, d'espacement ni de couleur.
