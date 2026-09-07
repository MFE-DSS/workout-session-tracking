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
>
> ---
>
> ⚠ **RELU CONTRE LE CODE LE 2026-09-06, ET IL AVAIT TORT.**
> `Sb_INSTRUMENTS_FACTS_CORRECTION_01`
>
> Les **60 affirmations factuelles** de la première rédaction ont été revérifiées
> une par une dans le code, chaque réfutation étant elle-même contestée par un
> second lecteur chargé de la démolir. Résultat : **29 corrections, dont 11
> réfutations franches.** Les passages corrigés portent la mention
> *« (corrigé) »*.
>
> Ce que cette passe apprend vaut d'être écrit ici, en tête, plutôt que dans un
> rapport de sprint : **la moitié de ce qu'une exploration de code produit en
> une nuit est inexact ou périmé.** Trois causes, chacune vue plusieurs fois :
>
> * **la dette déjà remboursée.** Le gâchis de `build_weekly_loop` sur
>   `/progress` était corrigé depuis `TRAIN1-C` ; `/physique` et `/dashboard`
>   ne lisent plus rien depuis la même tranche. J'accusais un état passé.
> * **le compte fait de mémoire.** 20 champs au lieu de 18, 14 clés au lieu de
>   15, 4 dataclasses au lieu de 3, 3 échelles de confiance au lieu de 7, une
>   trace « à 6 points » qui en compte de 2 à 6.
> * **le « toutes » et le « aucune ».** *« Les routes `/body/*` vérifient toutes
>   le consentement »* : deux sur huit. *« La Home n'affiche aucune alternative
>   écartée »* : elle les affiche, dans un repli de niveau 3. Un quantificateur
>   universel écrit sans le vérifier est le plus coûteux des raccourcis — et
>   dans le cas du consentement, il **masquait un trou plus grave** que celui
>   que je signalais.
>
> **Règle qui en découle, pour ce document comme pour les suivants : aucun
> nombre, aucun « toutes », aucun « aucune » sans la ligne de code qui le
> prouve.**

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
| 1 | `profil-corps` | ✅ **LIVRÉ** `UI-CP1` | BODY_LEDGER | Réponse primaire (poids + âge) + relevé daté. ⚠ **Les liens « Ajouter » N'ONT PAS disparu** : ils quittent chaque ligne pour le **pied de la bande ABSENT**, où au plus deux destinations réelles existent. Six « Ajouter » empilés étaient exactement les CTA répétés que la doctrine interdit ; zéro affordance aurait rendu l'absence inactionnable |
| 2 | `profil-compte` | ✅ **LIVRÉ** `UI-CP1` | ACCOUNT | ⚠ **Ne déménage PAS vers une autre route** — mesuré : la coque n'a **aucune** destination « compte », `/profile` **est** cette destination (4ᵉ item du rail). Il sort de l'**instrument**, pas de la page : tiroir de bas de page |
| 3 | `profil-mesure` | **REINVENT** — *non fait* | BODY_LEDGER | Les 16 champs **jamais simultanés**. `UI-CP1` l'a **rangé derrière un geste**, pas réinventé : la capture guidée reste bloquée par `update_measurement` (voir `§7.1`) |
| 4 | `profil-morpho` | ✅ **LIVRÉ** `UI-CP1` | BODY_LEDGER | Bande du relevé. Le tableau à 3 colonnes disparaît — il cassait ses cellules à 390 px — et sa capacité d'accessibilité (`scope="row"`) est **remplacée** par `dt`/`dd`, pas perdue. ⚠ **L'énumération des absences n'a lieu que si elle DISCRIMINE** : sur un profil vide, une seule phrase, sans quoi on réintroduit les sept façons de dire la même absence bannies par `UX4_01` |
| 5 | `profil-reference` | ✅ **LIVRÉ** `UI-CP1` | — | Redistribué : Taille/FC repos → relevé BODY_LEDGER, Email → tiroir Compte. Le **formulaire** survit comme tiroir « Données de référence » — la lecture est redistribuée, l'écriture reste atteignable |
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
| `accueil-etat` | ~~DEFER~~ → **RETIRÉ** | **Clos par l'opérateur le 2026-09-06** — voir `§6.2bis` |
| `social-partage` | **DEFER** | Part avec le lien d'invitation / partage système |
| `profil-reference` | **DELETE confirmé** | Rien n'est perdu : le contenu est **redistribué** |
| grade composite | **REMOVE confirmé** | Les diagnostics restent. Seule la **fausse précision** disparaît |

### 6.2bis Quatre questions CLOSES — arbitrage opérateur du 2026-09-06

> **Ces quatre décisions ne se rouvrent pas.** Elles étaient présentées comme
> des blocages dans les versions précédentes de ce document ; elles ont été
> tranchées. Un document qui les dit encore ouvertes invite à les re-litiger.

#### 1 · État global de l'utilisateur — **CLOS**

`accueil-etat` **sort de l'ontologie cible de MISSION**, et il n'y a **pas** de
score de préparation de remplacement à inventer.

MISSION expose d'abord : **les faits pertinents · l'action suivante · la raison
de la recommandation · l'incertitude quand elle est matérielle.**

Un état global synthétique ne pourra revenir **que si un modèle validé est
explicitement conçu**. *« Ne pas remplacer une abstraction faible par une
autre. »* La « règle de dérivation de l'état » cesse donc d'être un prérequis :
elle n'a plus d'objet.

#### 2 · Consentement corporel — **CLOS, POLITIQUE PRODUIT**

| Consentement actif **exigé** | Consentement actif **non exigé** |
|---|---|
| collecte · import · modification · traitement dérivé · usage dans les recommandations | **accès de l'utilisateur à ses données déjà détenues** · **export** · **suppression** |

Le retrait du consentement **arrête les traitements et usages nouveaux ; il ne
séquestre pas les données existantes de l'utilisateur.**

⚠ La validation **juridique / vie privée** est signalée **séparément** et reste
ouverte. La sémantique produit, elle, est tranchée.

*(Le relevé de `§7.1` reste valide comme **constat d'écart** entre cette
politique et le code : quatre routes modifient, suppriment ou exportent des
mesures sans contrôle. L'écart est désormais mesurable contre une règle.)*

#### 3 · Durée d'une séance — **CLOS**

**Ne pas inventer de durée planifiée.** La durée **écoulée réelle** peut être
exposée **uniquement** si de vrais horodatages de début et de fin la portent.

Pour une séance **future** : **AUCUNE ESTIMATION**, tant qu'un estimateur validé
n'existe pas. MISSION peut à la place utiliser le **nombre d'exercices**, le
**nombre de séries de travail**, la **structure de charge**.

> **La précision ne doit pas dépasser le modèle.**

#### 4 · Programme actif — **CLOS**

**« non archivé » n'est PAS « actif ».** Le triptyque `ACTIF / MIENS /
CATALOGUE` **ne s'expose pas** avec la sémantique actuelle.

Pour l'instant : **`MIENS` · `CATALOGUE`.**

Si l'orchestration produit exige plus tard **un** programme gouvernant, il
faudra introduire un `CURRENT_PROGRAM` / `SELECTED_PROGRAM` **explicite**, avec
sa persistance et sa sémantique de propriété. **Ne pas aliaser un champ ancien
dans le concept neuf.**

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
| **durée d'une séance** *(clos — `§6.2bis`)* | MISSION · LOADOUT_BAY | **Aucune colonne** sur `WorkoutTemplate`, et rien ne l'estime. **Décision : aucune estimation** pour une séance future ; la durée écoulée réelle seulement si de vrais horodatages la portent. MISSION utilise le nombre d'exercices, de séries de travail, la structure de charge. *La précision ne doit pas dépasser le modèle.* |
| **fenêtre 28 j** | BodyMap de FLIGHT_RECORDER | `zone_exposure.WINDOW_DAYS` est **fixe à 14** (`zone_exposure.py:50`). Les agrégats **par zone** sont bien calculés dans `recommendation._compute_signals` — 7 j (`hard_sets_by_zone_recent`, l. 288-294), 24 h (`hard_sets_by_zone_24h`, l. 296-302), 14 j (`hard_sets_14d_by_zone`, l. 304-314) — et **aucun ne sort du module** : le payload de `recommend_next_session` ne porte que `template` / `score` / `phrase` / `primary_zones` et un `context` de 4 clés. *(Noms corrigés : ni `hard_sets_by_zone_7j` ni `hard_sets_by_zone_14j` n'existent.)* |
| **programme ACTIF** *(clos — `§6.2bis`)* | LOADOUT_BAY | Ce qui manque n'est pas la liste, c'est la **distinction**. `GET /programs` existe et `list_drafts` rend les programmes **non archivés** — ce que `MAX_ACTIVE_PROGRAMS` appelle « actifs ». **Décision : « non archivé » n'est PAS « actif ».** Le triptyque ne s'expose pas ; on rend **`MIENS` · `CATALOGUE`**. Un `CURRENT_PROGRAM` explicite, persisté, viendra si l'orchestration l'exige — **sans aliaser un champ ancien** |
| **progression intra-séance** | MISSION à l'état `LIVE` | `latest_open_session` rend l'entité ORM entière ; « X/Y séries » exige de charger `session_exercises → set_logs` |
| ~~**fraîcheur d'une donnée corporelle**~~ | ~~BODY_LEDGER~~ | ✅ **CLOS le 2026-09-07 par `UI-CP1` (PR #226).** ⚠ **Le patron pressenti a été ÉCARTÉ** : `recovery_contract.Sufficiency` et `readiness_sufficiency_for_age` portent sur la **récupération d'entraînement**, pas sur le corps — les reprendre par commodité aurait été inventer un seuil de péremption corporelle en le déguisant en réemploi, et **aucun tel seuil n'existe dans ce dépôt**. Ce qui est livré est un **FAIT, pas un verdict** : `FactRow.age_label`, formaté par `time_format.relative_hours_ago` (déjà en service sur `/export` et `/healthz`), plus `weight_age_label` sur la route. Aucune couleur d'alerte sur l'ancienneté. **Trois régimes distingués** : OBSERVATION porte son âge · RÉFÉRENCE STABLE (la taille) n'en porte pas · INCONNU se dit (`users.resting_hr` est un `Integer` nu — le schéma **n'a pas** de colonne de date) |
| ~~**règle de dérivation de l'état**~~ | ~~le retrait de `accueil-etat`~~ | ✅ **SANS OBJET — clos le 2026-09-06.** `accueil-etat` sort de l'ontologie cible et **aucun score de remplacement n'est à inventer**. Ce n'est plus un prérequis. Voir `§6.2bis` |

### 7.1 Deux contraintes dures sur BODY_LEDGER

**`update_measurement` remet à NULL les champs absents**
(`body_profile.py:400-409`). Le formulaire actuel soumet l'ensemble, donc ça
marche. **Une capture guidée « une valeur à la fois » casserait ce contrat** :
chaque étape effacerait les autres mesures.

**Sept échelles de confiance concurrentes, sans une seule constante partagée.**
Un `BODY_LEDGER` qui affiche une confiance doit d'abord en choisir une :

| Échelle | Niveaux | Où |
|---|---|---|
| `MorphologyDescriptor.confidence` | 4 — `measured` / `derived` / `inferred` / `not_deductible` | `morphology_profile.py:36-39` |
| `RatioResult.confidence` | 3 — `ok` / `proxy` / `none` | `body_profile.py:165` |
| `ZoneScore.confidence` | 3, **en français** — élevée / moyenne / faible | `muscle_scoring.py:39` |
| `AxisScore.confidence` | 4, en français **aussi, mais pas les mêmes** — + insuffisante | `dashboard.py:43` |
| `recovery_contract.Confidence` | 4 — `high` / `medium` / `low` / `none` | `recovery_contract.py:62-68` |
| `confidence.py` | 3 — ⚠ **homonyme** : mesure la qualité du *logging d'une séance*, pas la confiance dans une donnée corporelle | `services/confidence.py` |
| `recommendation_explainer` | son propre `confidence` | — |

Deux d'entre elles sont en français et ne partagent pas leurs niveaux ; une
septième porte le mot sans parler de la même chose. **Le ledger doit en élire
une et absorber les autres** — c'est une décision, pas un refactor.

**Le consentement corporel ne garde presque rien** *(corrigé — la première
rédaction disait que `/body/*` vérifiait « toutes », et sous-estimait de
beaucoup le trou réel).*

`has_active_consent` n'est appelé qu'en **trois points de tout le dépôt**, tous
dans `app/routers/body.py` — et l'un des trois ne garde rien : l. 43 conditionne
seulement un affichage, la route rend 200 avec ou sans consentement. Sur les
**8 routes** du fichier, **deux** sont réellement gardées : `GET /body/measurements/new`
(l. 81) et `POST /body/measurements` (l. 90).

**Quatre routes modifient, suppriment ou exportent des mesures sans aucun
contrôle de consentement** :

| Route | Ce qu'elle fait | Ce qu'elle vérifie |
|---|---|---|
| `GET /body/measurements/{id}/edit` (l. 105) | affiche | propriété seule |
| `POST /body/measurements/{id}/edit` (l. 128) | **écrit** | propriété seule |
| `POST /body/measurements/{id}/delete` (l. 155) | **supprime** | propriété seule |
| `GET /body/export.json` (l. 172) | **exporte tout** | rien |

Vérifié au runtime, consentement retiré : le POST d'édition écrit bien la
nouvelle valeur, la suppression supprime.

Côté lecture, **quatre** surfaces lisent les mesures sans vérifier —
`/profile` (`auth_routes.py:462, 464, 474`), `/body/export.json`,
`/body/intelligence` et `/coach-report`. Deux d'entre elles sont au moins
derrière un drapeau de fonctionnalité ; `/profile` n'a **ni consentement ni
drapeau**, et c'est la surface corporelle la plus exposée du produit.

⚠ **`/physique` et `/dashboard` sortent de cette liste** : depuis `TRAIN1-C` ce
sont de simples redirections 303 vers `/progress` (`pages.py:966`, `:997`) et
elles ne lisent plus aucune mesure. Le compte est de **quatre**, pas cinq.

Ce n'est pas une question de cockpit — c'est une **décision produit sur le
périmètre du consentement**, et l'état actuel (gardé sur la création, ouvert sur
l'édition, la suppression et l'export) est le seul qui ne se défende pas.

---

## 8. Ce qui est déjà calculé et qu'il suffit de brancher

Le diagnostic du programme — *le produit a la décision, pas le moyen de
l'appliquer* — se vérifie une dernière fois ici, et à son avantage : **une part
substantielle des instruments peut être bâtie en branchant l'existant.**

| Déjà calculé | Où | Aujourd'hui |
|---|---|---|
| la **raison** de la recommandation, ≤ 140 car. | `recommendation.py:642-751` | rendue |
| les **alternatives écartées avec leur zone limitante** | `pages._home_causal_context` | rendues |
| l'exposition 14 j — **4 états d'instrument** (`known` · `zero` · `partial` · `unknown`, **un seul scalaire pour toute la fenêtre**) et **3 états par macro-région** sur la silhouette (`on` · `zero` · `unknown`, 6 régions pour 11 zones), + provenance | `zone_exposure.py:52-68` · `:265-282` · `:322-326` | rendue |
| `lead` / `rows` / `trace`, ordre de **pratique** — 7 clés en tout ; `TOP_N = 5` donc `rows` en porte 4 au plus, le `lead` en étant extrait | `progression_view.py:197` | rendu |
| la **trace** — de **2 à 6 points**, jamais une longueur fixe : 6 est un plafond (`KEEP_OCCURRENCES`), 2 un plancher (le `delta` exige deux occurrences) | `progression_view.py:120` | rendue **pour le `lead` seul**, sous `L.trace \| length > 1` |
| 4 diagnostics + **4 manquants nommés**, jamais notés 0 | `program_quality_engine.py:394` | rendus |
| la **provenance** d'une donnée corporelle | `FactProvenance` | calculée, **non rendue** |
| l'**horodatage** d'une mesure | `FactRow.measured_at` | calculé, transporté, **jeté au gabarit** |

Et le cas extrême, à connaître : **`app/services/adaptive_replan.py` — 387
lignes, trois dataclasses, `replan()` complet (l. 286-373) — n'est importé par
aucun routeur et aucun service, et il est pourtant couvert par trois fichiers de
tests.** La décision existe en entier, elle est testée, et le moyen de
l'appliquer n'existe pas du tout.

Son `DivergenceKind` déclare 5 déclencheurs, **dont 4 seulement sont émis** :
`detect_divergences` (l. 183-222) construit `MISSED_SESSION`,
`SHORTENED_SESSION`, `CONSTRAINT_CHANGE` et `LIMITING_RECOVERY`.
`INCOMPLETE_SESSION` (l. 100) n'est construit nulle part — ni par son nom, ni
par sa valeur `"materially_incomplete_session"` — dans `app/` comme dans
`tests/`. Du code mort **à l'intérieur** du code mort.

Même famille, deux cas voisins et un démenti :

* **`WeeklyPlan.zone_coverage` porte 18 champs par zone** (`weekly_planner.py:173-202`,
  plus 4 propriétés dérivées) — et la Home n'en lit **aucun**.
  `_build_weekly_plan` (`home.py:76-113`) ne touche jamais `plan.zone_coverage` :
  ses deux clés viennent des `zone_label` des créneaux (donc de `PlannedSlot`) et
  de `unmet_constraints[0]`. Le seul lecteur de `zone_coverage` est
  `decision_analytics.py`, plus `adaptive_replan.py` — qui est mort.
* **`build_weekly_loop` produit 15 clés**, pas 14 : les 14 de `_compose` plus
  `narrative` (16 sur le chemin dégradé).
* ⚠ **Le gâchis de `/progress` est déjà corrigé** *(mon affirmation était
  périmée).* Depuis `TRAIN1-C`, `/progress` n'appelle plus `build_weekly_loop` :
  il appelle `build_progress_week` (`pages.py:795-797`), un producteur étroit qui
  ne calcule que les deux clés réellement rendues. `build_weekly_loop` n'est plus
  appelé par aucun routeur — seulement par des tests. La docstring de
  `build_progress_week` documente le gâchis **au passé**, comme sa raison d'être.

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
