# Sx_SCI_V2_CATALOGUE_INTEGRATION_01 — Intégrer le catalogue scientifique V2 sans changer ce qui est servi (SPEC ONLY)

> **Statut :** SPEC **ACCEPTÉE** par l'opérateur (GO BUILD `Sb_SCI_V2_01`, 2026-10-23). Les
> questions du §17 sont tranchées au §19. Aucune migration, aucune activation. · **Date :**
> 2026-10-23 · **Version :** v3 (v1 + rulings du §19 + corrections déclarées de
> `Sb_SCI_V2_02` : règle d'éligibilité §7.1, collisions et relevé des noms §6.2, exécution
> incertaine §7.3) ·
> **Dépend de :** `Sx_AUREN_SCIENTIFIC_ENGINE_V2_SPEC.md` (doctrine E0–E8, §4 bis) ·
> **Code de référence :** `0c9e14b` (merge PR #272, recommandeur V3 servi, D14 en vigueur).

## 0. En une phrase

Le catalogue scientifique V2 entre dans le dépôt comme **donnée versionnée** avec un résolveur
d'identité, un registre d'exposition dérivé et une jointure TRAIN A, puis tourne **en ombre** à
côté du recommandeur V3. Il ne change rien de ce que l'utilisateur voit ou de ce que la base
contient, tant qu'une décision opérateur distincte ne l'a pas promu.

## 1. Ce qui entre : le catalogue clos

Le catalogue clos est un artefact généré par outil, aujourd'hui hors dépôt sous
`reports/curation_v2/`. Tous les chiffres sont régénérés par `validate_closure.py`.

| Mesure | Valeur |
|---|---|
| Fiches source (une par `variant_key` de l'EKB) | 107/107, 0 erreur de format, 107 `reviewed` |
| Identités scientifiques canoniques = candidats du compilateur | **84** |
| Alias historiques | **23** (11 par faits sources, 12 par définition opérateur) |
| Canoniques UNIQUE / doublon exact / variante légitime / UNRESOLVED | 48 / 18 / 18 / **0** |
| Vecteurs d'exposition incomplets (≥ 1 contribution UNKNOWN) | 28 |
| Exigences d'équipement UNKNOWN | 1 (`adduction-couchee-machine`) |
| `machine_unspecified` | 29 |
| Exigences `any_of` réelles | 1 (pullover câble : corde **ou** barre) |
| Défauts plantés rejetés par le validateur, chacun pour sa raison nommée | 29/29 (26 fiches + 3 delta) |
| Contenus servis en écart connu (`CONTENT_EXECUTION_MISMATCH`, §19) | 2 |

Le delta proposé du registre TRAIN A (`Sb_SCI_V2_01`, versionné dans
`data/sci/train_a_delta_proposal.json`) n'est pas appliqué au registre servi. Il ajoute
**12 capacités et 13 objets**, dont la poignée prise neutre et, depuis le §19, la poignée de rowing
prise neutre serrée. Il n'accorde **aucun** accessoire à une station : la poignée simple n'est pas
donnée à `dual_adjustable_pulley`, et la poignée de rowing ne l'est pas à `low_row_station`. Une
provenance en prose n'est pas une définition de capacité.

## 2. Faits mesurés du dépôt qui contraignent l'intégration

Tous les faits ci-dessous sont lus dans le code à `0c9e14b`. Les points décisifs ont été
re-vérifiés à la main.

| # | Fait | Où |
|---|---|---|
| F1 | L'identifiant des 107 fiches est le `variant_key` de l'EKB, qui **n'est pas** le slug de la base : `slugify(nom)` diffère pour **21/107** (ex. `cable-cross-over-paren-bashaut` ≠ `cable-cross-over-bas-haut`). | `app/services/exercise_identity.py:42` ; mesure scriptée |
| F2 | Sous `normalize`, deux noms EKB fusionnent (`Curl marteau câble (corde)` / `Curl marteau câble corde`). Le catalogue en fait déjà une seule identité. | `exercise_identity.py:29` |
| F3 | L'historique est **adressé par nom** : `session_exercises.exercise_name_snapshot` (prescrit) et `substituted_name` (exécuté, texte libre). `set_logs` ne porte aucune référence d'exercice. Les instantanés font foi. | `app/models/session.py:164-192` |
| F4 | Il existe déjà une identité d'exercice (`exercises.slug` + `exercise_aliases.normalized`), sans clé étrangère vers les séances, résolue par `resolve_exercise` en lecture seule. | `exercise_identity.py:60-75`, migration `20260822_add_exercise_identity` |
| F5 | `identity_key` décide quelles séances **partagent un historique de charges** (surcharge, « dernière fois »). | `exercise_identity.py:132-167` ; `stats.py`, `overload_inputs.py` |
| F6 | L'exposition servie lit `ExerciseMuscleMapping` et un classifieur par sous-chaîne, pas l'EKB. Deux coefficients coexistent : 0,3 dans `muscle_scoring`, demi-séries 2/1/0 dans `set_contribution`. | `muscle_scoring.py:163-169`, `set_contribution.py:69-147` |
| F7 | Faisabilité : `equipment_model.feasibility` → FEASIBLE / NOT_FEASIBLE / UNKNOWN, en **conjonction pure**, sans aucun `OU`. `None` (inconnu) ≠ `()` (rien de requis). Environnement NULL ⇒ porte inactive, candidats inchangés. | `equipment_model.py:191-247`, `environment_activation.py:87-89` |
| F8 | Le résolveur de créneau a quatre états (`native_feasible`, `adaptable`, `unknown`, `not_feasible`) et **un seul consommateur** autorisé, gardé par test. | `environment_resolution.py:40-43` ; `test_the_resolution_layer_has_exactly_one_consumer` |
| F9 | Servi = V3 via `advice_memory.recommander`. Le choix tient à deux constantes, `POLITIQUES = ("v2", "v3")` et `POLITIQUE_SERVIE = "v3"`. **« v2 » désigne déjà l'ancien recommandeur à somme pondérée.** | `advice_memory.py:49,77-78` |
| F10 | `_build_reco_context` avale toute exception et rend `None`. Une erreur de l'ombre dans ce chemin **éteindrait la recommandation servie**. | `pages.py:90-112` |
| F11 | `recommendation_episodes` est écrit au seul POST de démarrage ; aucun GET n'écrit (garde). `provenance_de` lit **une** ligne par séance (`scalar_one_or_none`, sans filtre de politique) : une seconde ligne d'épisode casserait la page d'une ancienne séance. | `sessions.py:105-147` ; `session_provenance.py:71-74` ; `test_rec_cp4_memoire_conseil.py:601` |
| F12 | Une garde refuse tout fichier qui nomme `recommendation_v3` hors d'une liste de 10 fichiers. | `test_rec_cp2_policy.py:93-148` |
| F13 | Un banc de rejeu existe : 17 trajectoires, 78 décisions, origine fixe, boucle ouverte et fermée. Il n'y a aucun fichier de décisions de référence, tout est recalculé sous pytest. | `scripts/reco_replay.py` |
| F14 | Aucune capture HTML d'ancienne séance n'est versionnée. Les gardes de rendu sont structurelles. | `tests/test_ui_cp8d_releve_durable.py` |
| F15 | Couverture des noms : les 107 noms des gabarits et de leurs substituts, les 69 noms de `exercise_properties` et les 109 lignes de `equipment_curation` se résolvent **tous** vers une fiche V2 (`normalize` + `_aliases` de l'EKB). Restent inconnus possibles : les noms libres saisis par un utilisateur. | mesure scriptée |

## 3. Invariants préservés (contrat)

1. **Toute identité historique d'exercice** reste lisible pour toujours : aucun `variant_key`,
   slug, alias ni instantané n'est supprimé ou réécrit.
2. **Lignée prescrit → exécuté** : l'ombre lit `exercise_name_snapshot` et `substituted_name`
   comme aujourd'hui (`actual_exercise_name`) et ne les modifie jamais.
3. **Sémantique TRAIN A** : objet → capacité → exigence. `None` ≠ `()` ; NULL ⇒ porte inactive ;
   le résolveur à quatre états n'est ni affaibli ni dupliqué.
4. **Service V3** : sorties identiques (décision et octets), ombre active ou non.
5. **Rejeu des anciennes séances** : leur rendu ne lit aucune donnée V2.
6. **Base de données** : aucune colonne, table ni écriture nouvelle dans cette intégration.

## 4. Nommage : pas de second « v2 »

« v2 » est déjà pris par l'ancien recommandeur (F9). Le moteur scientifique s'appelle **`sci`**
dans le code : répertoire `data/sci/`, modules `app/services/sci_*.py`, étiquette d'ombre
`"sci-shadow"`. Le littéral `"v2"` n'est **jamais** employé pour lui, et la valeur `"sci-shadow"`
n'entre jamais dans `POLITIQUES` ni dans `policy_version`. Une garde vérifie les deux.

## 5. Autorités canoniques (une notion → une autorité)

| Notion | Autorité | Emplacement cible | Remarque |
|---|---|---|---|
| Fiche scientifique d'exercice (rôles bruts, base de rôle, actions chargées, pattern, exécution canonique, références de preuve) | catalogue SCI | `data/sci/exercise_catalogue.json` | 107 fiches, en-tête versionné (`catalogue_version`, `schema_id`, versions zone / crédit / registre de preuve) |
| Identité scientifique et alias historiques | **le bloc `identity` de chaque fiche** | même fichier | pas de fichier d'alias séparé : il dupliquerait la relation. `merge_basis` dit si la fusion vient des faits sources ou d'une définition opérateur |
| Vocabulaires (zones, rôles, patterns, actions, modes d'équipement) | schéma JSON | `data/sci/exercise_catalogue.schema.json` | enums fermés ; ajouter un terme = un commit sur le schéma |
| Politique de crédit d'exposition | fichier de politique versionné | `data/sci/exposure_credit_policy.json` (`sci-exposure-credit-v1`) | appliquée **à la lecture** (§7). L'étiquette d'en-tête actuelle `credit_policy_v2` est renommée à l'adoption |
| Registre de preuves / provenance (E0) | registre de preuves | `data/sci/evidence_registry.json` | 96 entrées ; les fiches ne citent que des `EV-*` de ce registre |
| Objets et capacités d'équipement | **registre TRAIN A existant** | `data/equipment_registry.json` | le delta y est **appliqué**, jamais doublé (§8.2). Aucun second registre |
| Exigences d'équipement d'un exercice | catalogue SCI pour le moteur SCI ; **EKB pour V3 tant que V3 est servi** | `exercise_catalogue.json` / `exercise_knowledge_base.json` | deux autorités **datées et bornées** (§8.3) : l'EKB est gelé pour ce champ, et le champ disparaît à la promotion |
| Arêtes de substitution | inchangées | `app/services/substitution.py`, `exercise_properties.json`, `cross_pattern_substitutions.json` | **jamais copiées** dans une fiche. Le moteur SCI les lit au même endroit |
| Pont nom historique → fiche | dérivé, pas stocké | calculé au chargement depuis les noms EKB et `_aliases` | on préfère la dérivation à un fichier de correspondance (§6) |
| Génération | générateur du catalogue | `scripts/generate_sci_catalogue.py` depuis `data/sci/sources/` | rejoue les rulings ; reproductible à l'octet (`--check`) |
| Outil de validation | validateur du catalogue | `scripts/validate_sci_catalogue.py`, exercé en CI par la suite pytest | régénère le rapport (`exercise_catalogue.validation_report.json`), rejette les défauts plantés |

Le contenu servi aux utilisateurs par V3 n'est pas modifié par l'adoption : consignes de l'atlas,
notes de gabarit, noms affichés. Deux contradictions sont **connues**. Chacune est consignée
dans la fiche concernée par un bloc `content_alignment` au statut `CONTENT_EXECUTION_MISMATCH`
(§19) :
- la note de « Relevé de jambes suspendu » (« monter les genoux au-dessus des hanches ») contredit
  l'exécution jambes tendues que l'opérateur a définie ;
- la consigne d'atlas « coudes vers les hanches » de « Rowing machine chest-supported » contredit
  l'exécution générique à 30–45°.

**Porte d'alignement du contenu.** Tant que l'un de ces deux écarts subsiste, une preuve d'ombre
tirée du dogfood réel (`Sb_SCI_V2_04`) ne peut pas être lue comme une exposition **exacte** pour
la fiche concernée. Sa sémantique d'exécution est incertaine : on ne sait pas laquelle des deux
exécutions l'utilisateur a faite. Cette porte ne bloque pas `Sb_SCI_V2_01` à `03`. Le contenu
servi n'est corrigé dans aucune de ces tranches.

## 6. Résolveur d'identité unique

### 6.1 Deux couches, jamais confondues

- **Identité d'exercice** (`exercises` / `exercise_aliases`, F4–F5). C'est elle qui décide de la
  continuité des **charges et de la progression**. Elle reste l'autorité de V3 et **n'est pas
  modifiée**.
- **Identité scientifique** (bloc `identity` SCI). Elle décide de la **comptabilité d'exposition**
  et des **candidats du compilateur**.

Les fusions SCI ne fusionnent **pas** l'historique de charges. G12 range un ancien « Curl poulie
basse » éventuellement fait à la corde sous le curl à la barre. C'est juste pour compter des
séries de biceps, pas pour comparer des kilos. Étendre une fusion SCI à la continuité des charges
est une **décision opérateur distincte**, hors de cette spec.

### 6.2 Algorithme

```
résoudre(entrée) -> Résolution
  entrée = variant_key connu (user_program_exercises.variant_key)  → fiche
         | nom historique (substituted_name sinon exercise_name_snapshot)
  1. variant_key présent et connu du catalogue           → fiche
  2. normalize(nom) ∈ index(noms canoniques EKB ∪ _aliases EKB) → variant_key → fiche
  3. sinon resolve_exercise(db, nom) → Exercise ; normalize(Exercise.name) ∈ index → fiche
  4. sinon                                               → UNKNOWN_IDENTITY (raison explicite)
  fiche → identity.alias_of (au plus un saut : la clôture interdit les chaînes) → fiche canonique
Résolution = {statut: RESOLVED | UNKNOWN_IDENTITY, étape: 1|2|3, entrée, variant_key,
              scientific_identity_id, fiche_canonique, catalogue_version}
```

- **Déterministe** : `normalize` est une forme canonique exacte, pas une ressemblance. Aucune
  correspondance floue, aucune distance d'édition, aucun « meilleur candidat » au moment de
  l'exécution.
- **Lecture seule** : l'étape 3 n'appelle jamais `ensure_exercise` ni `add_alias`, qui écrivent.
- **Un alias n'est jamais un candidat** : le compilateur ne reçoit que des fiches CANONICAL, dédupliquées
  par `scientific_identity_id`.
- **Inconnu explicite** : `UNKNOWN_IDENTITY` est une valeur, pas `None`. Ses séries entrent dans
  le registre comme exposition inconnue (§7.3), jamais comme zéro.
- **Renommer sans couper l'historique** : un nom changé dans les données de référence garde son
  `variant_key`. L'ancien nom passe d'abord dans `_aliases` de l'EKB, ce qui le propage à
  `exercise_aliases` par la graine insert-only existante. Une garde refuse un changement de nom
  sans alias préalable, car `ensure_exercise` créerait sinon une identité neuve et couperait
  l'historique.
- **Concordance** : quand les étapes 2 et 3 résolvent toutes deux, elles doivent rendre la même
  fiche. Une garde le vérifie sur tout le corpus.
- **Collision sous `normalize`** (v3) : deux noms EKB qui se normalisent à l'identique ne sont
  admis que s'ils désignent la **même identité scientifique**. Ils se résolvent alors vers la fiche
  canonique : c'est le cas, mesuré, de « Curl marteau câble (corde) » et « Curl marteau câble
  corde ». Deux identités distinctes sous une même forme normalisée sont une erreur de donnée,
  refusée au chargement.
- **Relevé des noms** (v3) : la garde de renommage a besoin de se souvenir des noms passés, ce
  qu'aucun index dérivé ne peut faire. `data/sci/legacy_name_ledger.json` relève, une fois pour
  toutes, les noms EKB (canoniques et `_aliases`) sous lesquels chaque fiche a été curée. C'est un
  **outil de test, jamais lu à l'exécution** : le résolveur reste dérivé de l'EKB (§15). La garde
  exige que chaque nom relevé se résolve toujours vers sa fiche, et que tout nom EKB nouveau soit
  ajouté au relevé.

## 7. Entrée au registre d'exposition

### 7.1 Ligne de registre (dérivée, recalculable, non persistée)

Une ligne par **série de travail réalisée**, et par zone contributrice.

**Correction déclarée (v3, `Sb_SCI_V2_02`).** La v1 attribuait la règle d'éligibilité à
`set_contribution`. C'était faux : ce module ne compte que des séries **planifiées**
(`planned_sets`) et n'a aucune règle pour les séries exécutées. La règle qui fait foi dans le
dépôt est celle de l'exposition existante :
- **série** : `kind == "work"` et `completed`, définition de `zone_exposure._work_sets`, « même
  définition que `kpis.work_sets_done_30d` — le dépôt n'a besoin que d'une seule notion de série
  faite » ;
- **séance** : `status == "completed"`, `excluded_from_stats` faux, `started_at` dans
  `[début, fin)`, borne de fin exclusive comme `muscle_scoring` et `weekly_loop`.

L'horodatage d'une ligne est le `started_at` de la séance, comme dans les comptes existants. Le
nom exécuté est `actual_exercise_name`. Une garde de parité épingle la règle contre
`zone_exposure._work_sets`.

```
{ session_id, session_exercise_id, set_log_id, performed_at,
  nom_prescrit, nom_executé, résolution (§6.2),
  catalogue_version, scientific_identity_id,
  zone, raw_role ∈ {PRIMARY, SECONDARY, MINOR, UNKNOWN}, role_basis, evidence_refs }
```

Le **rôle brut** est conservé. Le crédit (1,0 / 0,5 / 0) n'est **jamais** stocké à sa place : il
se recalcule.

### 7.2 Politique `sci-exposure-credit-v1`

| Rôle brut | Crédit |
|---|---|
| PRIMARY | 1,0 |
| SECONDARY | 0,5 |
| MINOR | 0 |
| UNKNOWN | **UNKNOWN** — jamais 0, jamais 0,5 |

### 7.3 Agrégat par zone et vecteurs incomplets

```
exposition(zone, fenêtre) = { crédit_résolu: Σ crédits des rôles résolus,
                              séries_inconnues: nb de séries où la zone est UNKNOWN,
                              séries_identité_inconnue: nb de séries UNKNOWN_IDENTITY,
                              borne: EXACT si séries_inconnues = séries_identité_inconnue = 0,
                                     sinon MINIMUM }
```

- Une zone `MINIMUM` signifie « au moins ce crédit ». Elle n'est jamais lue comme « exactement ce
  crédit ».
- Couverture et départages n'utilisent que `crédit_résolu` (ruling 9). Une zone dont la seule
  information est UNKNOWN n'est pas déclarée « non travaillée ».
- Une série `UNKNOWN_IDENTITY` rend **toutes** les zones `MINIMUM` sur la fenêtre, puisqu'on ne
  sait pas ce qu'elle a travaillé.
- Les 28 vecteurs incomplets produisent ces bornes ; aucun n'est complété par défaut.
- **Exécution incertaine** (v3, §19.5). Une série faite sur une fiche en
  `CONTENT_EXECUTION_MISMATCH` est comptée normalement. Elle est aussi décomptée en
  `séries_exécution_incertaine`. Une zone n'est une preuve **exacte** que si sa borne est `EXACT`
  **et** si ce décompte est nul : c'est ce que lira `Sb_SCI_V2_04`.
- Le registre SCI ne remplace **ni** `muscle_scoring` **ni** `set_contribution` pendant l'ombre.
  Il est calculé à côté.

## 8. Jointure environnement

### 8.1 Preuve de la chaîne

```
objet déclaré (training_preferences.available_equipment_items)
  → capacités (equipment_registry.json, après application du delta)
  → exigence de la fiche canonique (ET de capacités ; {any_of} = au moins une)
  → verdict FEASIBLE | NOT_FEASIBLE | UNKNOWN
```

- `equipment_requirement_status = UNKNOWN` ⇒ verdict `UNKNOWN`, quel que soit l'environnement.
  Ce n'est **jamais** `[]`. Le validateur rejette une liste vide RESOLVED hors poids du corps.
- Une capacité citée par une fiche mais absente du registre servi ⇒ `UNKNOWN`. Elle n'est jamais
  « faisable ».
- Environnement NULL ⇒ porte inactive, exactement comme F7.
- `any_of` : `feasibility` est étendue **dans `equipment_model.py`**, sa seule maison. Aucune
  entrée EKB ne porte de `any_of`, donc V3 est inchangé par construction. Une garde l'épingle.
- **Grammaire V1 des exigences** (§19), volontairement petite :
  - une exigence est une conjonction de membres ;
  - un membre est soit une capacité atomique, soit un groupe `{any_of: [capacité, …]}` d'au moins
    deux capacités atomiques ;
  - aucun groupe n'en contient un autre.
  Exemple valide : `ancrage_haut ET any_of(corde, barre_droite)`. Les arbres booléens imbriqués
  sont hors périmètre, et le schéma les rejette.
- Les créneaux passent par le résolveur à quatre états existant, via son unique consommateur
  (`environment_activation`). Aucun second résolveur n'est créé (F8).

### 8.2 Application du delta TRAIN A

Ajouter des objets au registre les rend **déclarables** dans l'interface : c'est un changement
de surface visible. Le delta part donc dans une tranche à lui (§12, `Sb_SCI_V2_03`), avec
exposition d'un rendu à l'opérateur (CLAUDE.md §5.1). Jusque-là, l'ombre traite les capacités
neuves comme absentes du registre, donc `UNKNOWN`, sans couche de surcharge.

### 8.3 Divergences d'exigence entre V3 servi et SCI (mesurées)

Sur 107 fiches : 59 identiques, 38 inconnues côté servi et résolues côté SCI, **10 différentes**,
et **aucune** résolue côté servi qui deviendrait inconnue côté SCI. Les 10 (dont les deux rowings
assis ajoutés par le §19) :

| Exercice | V3 (EKB) | SCI | Décision qui l'emporte |
|---|---|---|---|
| Curl poulie basse | ancrage bas | + barre droite | G12 |
| Face pull câble / (corde) | ancrage haut (± corde) | ancrage réglable + corde | face pull délégué ; **remplace** `test_face_pull_does_not_require_an_attachment` |
| Pullover câble (bras tendus) ×2 | `machine_pullover` | ancrage haut + {corde ∣ barre} | R11 + G21/G22 |
| Rowing haltère un bras | haltères | + banc plat | G31 ; **remplace** la décision TRAIN A « rowing un bras sans banc » |
| Tirage poulie haute prise neutre | station | + poignée prise neutre | G17 |
| Tirage vertical unilatéral câble | station | + poignée simple | délégué |
| Rowing câble assis prise neutre / prise serrée | station | + poignée de rowing prise neutre serrée | §19.4 |

Pendant l'ombre, ces écarts sont une **preuve** : l'ombre dit quand un V3 servi aurait été jugé
infaisable par SCI. Ils ne modifient pas l'EKB. Leur adoption dans le service se fait à la
promotion, avec amendement **explicite** des gardes TRAIN A concernées, jamais en silence.

## 9. Ombre : SCI ne sert rien

### 9.1 Étape S1 — ombre hors ligne (recommandée en premier)

Un comparateur déterministe (`scripts/sci_shadow.py`) rejoue, pour le même utilisateur, le même
jour et le même historique :

- le banc existant (F13, 17 trajectoires et 78 décisions) en boucle ouverte et fermée ;
- une copie en lecture seule d'une base de dogfood.

Pour chaque décision, il calcule V3 servi (appel inchangé) et SCI, puis écrit un rapport
JSON + Markdown **hors base**. Il ne touche à aucune route ni table.

### 9.2 Étape S2 — ombre en processus (optionnelle, GO séparé)

Elle ne se justifie que si S1 laisse une question que seul le trafic réel peut trancher. Ses
conditions sont non négociables :

1. elle est calculée **après** la construction de la réponse servie, hors de
   `_build_reco_context`, dans son propre `try`. Une exception de l'ombre est journalisée et
   n'atteint jamais le service (F10) ;
2. **aucune écriture en base**, en GET comme en POST : pas de `recommendation_episodes`, pas de
   `decision_traces` (F11) ;
3. sa sortie va dans un journal structuré borné, désactivé par défaut par une constante ;
4. elle n'est pas importée par `recommendation_v3`. Si elle doit nommer ce module, elle entre
   dans la liste de la garde F12 par un amendement **déclaré**.

### 9.3 Ce que SCI calcule en ombre

- registre d'exposition (§7) ;
- entrées de charge résiduelle ;
- écarts au plan (`PRESCRIPTION_GAP`) ;
- besoin d'entraînement ;
- candidats (canoniques seulement) ;
- faisabilité (§8) ;
- séance proposée ;
- trace de décision.

Une couche E0–E8 qui n'est pas encore construite rend `NOT_IMPLEMENTED` explicitement. Elle n'est
jamais simulée.

## 10. Preuve d'ombre : répondre à « pourquoi SCI aurait entraîné autre chose ? »

Un enregistrement par décision, sans score agrégé :

```
{ décision: {utilisateur, maintenant, empreinte_historique},
  v3: {gabarit, rang, critère_décisif, phrase},
  sci: {séance_proposée: [exercices canoniques + séries], statut_par_couche},
  zones_décisives: [{zone, crédit_résolu, borne, plan, écart}],
  exercices: {conservés, changés: [{v3, sci, raison}]},
  environnement: {adaptations, verdicts_UNKNOWN, divergences_exigence (§8.3)},
  inconnus_décisifs: [{fait, effet_sur_le_choix}],
  divergence: {même_séance: bool, raison ∈ {ZONE_PRIORITY, PLAN_GAP, RECOVERY,
               ENVIRONMENT, UNKNOWN_FACT, IDENTITY_MERGE, CANDIDATE_POOL, NOT_IMPLEMENTED}} }
```

Le rapport Markdown dérivé groupe les décisions par raison de divergence. Chaque ligne se lit
sans outil : zone, écart, fait inconnu.

## 11. Base de données

Aucune migration n'est prévue. Le catalogue est statique et versionné, le registre d'exposition
est dérivé de l'historique, et la preuve d'ombre vit dans des fichiers. Une colonne n'est pas
ajoutée parce qu'un champ JSON existe. Toute persistance future demande un besoin d'exécution
**démontré** dans sa propre spec. Les données d'utilisateur et de séance ne sont pas touchées.

## 12. Découpage en tranches (chacune sur GO BUILD, check_scope §1)

| Tranche | Contenu | Surface | Tier attendu |
|---|---|---|---|
| `Sb_SCI_V2_01` | `data/sci/*` (catalogue, schéma, preuves, politique de crédit), chargeur, validateur en CI, rapport régénéré | aucune | isolated |
| `Sb_SCI_V2_02` | résolveur d'identité (§6) + registre d'exposition dérivé (§7), sans consommateur servi | aucune | shared_code (lit `exercise_identity`) |
| `Sb_SCI_V2_03` | delta TRAIN A appliqué + `any_of` dans `equipment_model` + déclaration des nouveaux objets | **UI** : §5.1 obligatoire | shared_code |
| `Sb_SCI_V2_04` | comparateur d'ombre hors ligne (S1) et rapport de preuve (§10) | aucune | isolated |
| `Sb_SCI_V2_05` | ombre en processus (S2) | aucune | shared_code ; GO séparé, seulement si S1 le réclame |

La promotion de SCI au service n'est **dans aucune** de ces tranches.

## 13. Gates de validation de l'intégration

Chaque gate est une garde exécutée en CI, sauf mention contraire.

1. Le chargeur accepte les **107** fiches source. Le validateur rend 0 erreur de format et
   rejette ses défauts plantés.
2. **Chaque** nom d'exercice historique connu du produit se résout de façon déterministe, ou
   rend explicitement `UNKNOWN_IDENTITY`. Le corpus de noms est : gabarits, substituts,
   propriétés, curation, programmes utilisateur, et les noms distincts d'une base de dogfood au
   build. Les étapes 2 et 3 concordent.
3. Un alias n'apparaît jamais comme candidat du compilateur : 84 candidats au plus pour 107
   fiches.
4. Les anciennes séances se rendent à l'identique : le HTML de `/sessions/{id}` et du récapitulatif
   est capturé avant et après, sur un corpus semé, puis comparé.
5. La sortie de V3 est équivalente, en décision et en octets, ombre activée ou non. Le contrôle
   porte sur les 78 décisions du banc et sur l'empreinte de `test_rec_cp0_causal`.
6. Le comportement NULL de TRAIN A est inchangé : les gardes existantes restent vertes **sans
   amendement**.
7. Aucune contribution UNKNOWN ne devient 0 : sur une fiche plantée UNKNOWN, le registre rend
   `MINIMUM`, jamais un crédit nul.
8. Aucune exigence UNKNOWN ne devient « sans matériel » : le verdict reste `UNKNOWN` dans un
   environnement vide comme dans un environnement plein.
9. Recharger le catalogue est déterministe : deux chargements donnent le même condensat, et
   l'ordre est stable.
10. Preuve et provenance sont conservées : chaque ligne de registre cite `catalogue_version`,
    `role_basis` et `evidence_refs`.
11. Aucun GET n'écrit, aucune ligne d'épisode n'est ajoutée, `"sci-shadow"` ∉ `POLITIQUES`.
12. Un changement de nom sans alias préalable est refusé (§6.2).

## 14. Laboratoire mobile N0

Il n'est pas modifié. SCI est un travail backend et données, indépendant de la porte
d'expérience mobile. Plus tard, le modèle de lecture mobile consommera des prescriptions SCI déjà
calculées (séance, séries, raison), sans connaître la logique du domaine.

## 15. Options, risques, choix

| Sujet | Options | Choix | Raison |
|---|---|---|---|
| Lieu du catalogue | (a) colonnes en base ; (b) JSON versionné | **b** | statique, relisible, diffable ; aucune migration |
| Alias | (a) fichier d'alias ; (b) bloc `identity` dans la fiche | **b** | une seule autorité pour la relation |
| Pont d'identité | (a) table de correspondance stockée ; (b) dérivé au chargement | **b** | 21 divergences slug/`variant_key` absorbées sans fichier de plus |
| Fusions SCI et charges | (a) étendre à `identity_key` ; (b) séparer | **b** | (a) changerait la progression servie |
| Exigences pendant l'ombre | (a) amender l'EKB ; (b) deux autorités bornées | **b** | (a) change V3 (8 écarts) |
| Ombre | (a) en processus d'emblée ; (b) hors ligne d'abord | **b** | F10 et F11 : l'ombre en processus peut éteindre le service ou casser une page |

**Risques résiduels :**
- la règle d'éligibilité des séries doit être citée exactement, pas réinventée ;
- des noms libres utilisateur produiront des `UNKNOWN_IDENTITY`, à mesurer en dogfood avant
  toute conclusion ;
- les deux contradictions de contenu du §5.

## 16. Périmètre interdit (Non-goals)

- Aucun code, aucune migration et aucune constante modifiée par cette spec.
- Aucune activation de SCI au service, aucun changement de `POLITIQUE_SERVIE`.
- Aucune réécriture de la curation des 107 fiches, aucune revue de littérature nouvelle.
- Aucune fusion de l'historique de charges.
- Aucune modification du laboratoire N0.
- Aucun score agrégé opaque dans la preuve d'ombre.

## 17. Questions pour l'opérateur

1. **G30.** « Hanging knee raise » est nommé genoux fléchis. Je l'ai gardé en **variante
   distincte** (`hanging_bent_knee_raise`) au lieu de le fusionner dans la version jambes tendues,
   puisque ta règle fait de la version genoux fléchis une identité distincte. Le fusionner
   reviendrait à une ligne de `closure.py`.
2. **G24.** « Rowing machine chest-supported » est fusionné dans le rowing générique : son nom ne
   déclare aucun biais. Le biais ne venait que d'une consigne d'atlas.
3. **Face pull.** « Hauteur du visage » est traduit en `cable_anchor_adjustable` plutôt qu'en
   ancrage haut. Mesuré, cela ne change aucune faisabilité aujourd'hui : les deux poulies qui
   accordent l'ancrage haut accordent aussi le réglable.
4. **Même trou côté rowing assis.** Les prises neutre et serrée du rowing câble assis exigent
   probablement un accessoire, comme G17. Rien n'a été changé sans ta décision.

## 18. Verdict de la spec

**Verdict :** `V2 CATALOGUE INTEGRATION SPEC — READY FOR OPERATOR REVIEW` (v1), puis **acceptée**
par le GO BUILD `Sb_SCI_V2_01` (v2, §19). Aucune migration, aucune activation du service SCI.

## 19. Rulings opérateur du GO BUILD `Sb_SCI_V2_01` (2026-10-23)

Ces rulings ferment les questions du §17 et font désormais contrat.

1. **G30.** `hanging_bent_knee_raise` reste une **variante légitime**, distincte de
   `hanging_straight_leg_raise`. Ni alias, ni fusion.
2. **G24.** « Rowing machine chest-supported » relève de l'identité générique
   `chest_supported_row`. Aucune identité biaisée dorsaux n'est créée sur la seule foi de la
   consigne d'atlas. L'écart avec le contenu servi est consigné en `CONTENT_EXECUTION_MISMATCH`.
   Une comparaison d'ombre sur dogfood réel ne peut revendiquer une sémantique d'exécution exacte
   pour cet exercice tant que l'écart subsiste.
3. **Face pull.** L'exigence SCI est `cable_anchor_adjustable` + `cable_attachment_rope`. Elle
   n'est pas ramenée à l'ancrage haut générique pour la parité avec V3.
4. **Rowing câble assis, prises neutre et serrée.** Le delta TRAIN A futur gagne la capacité
   `cable_attachment_close_neutral_row_handle` et l'objet physique `close_neutral_row_handle`.
   Ils ne sont **pas** accordés à `low_row_station` : une station et son accessoire amovible sont
   deux faits physiques distincts, sauf si l'autorité du registre prouve ce lot exact. Ce delta
   n'est pas appliqué dans `Sb_SCI_V2_01`, qui ne met à jour que le catalogue versionné et
   l'autorité d'intégration.
5. **Porte d'alignement du contenu** (§5). Elle ne bloque pas `Sb_SCI_V2_01` à `03`. Elle bloque
   la lecture « exposition exacte » des conclusions de dogfood de `Sb_SCI_V2_04` pour les deux
   fiches concernées.
6. **Grammaire `any_of` V1** (§8.1) : conjonction de capacités et de groupes `any_of` de capacités
   atomiques. Aucune expression booléenne récursive.
