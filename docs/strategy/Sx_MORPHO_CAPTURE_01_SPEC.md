# Sx_MORPHO_CAPTURE_01 — Contrat de capture morphologique (SPEC)

> **SPEC ONLY.** Aucun code runtime, aucune migration, aucun modèle n'est livré par ce
> document. Il tranche ce que le runtime devra faire, sur la base d'un **audit du code
> actif** au SHA canonique `62ff4bd`.

**Autorité amont :** moteur pur `app/services/morphology_profile.py` (livré, fermé).
**Consommateur aval :** `Sb_MORPHO_PROFILE_RUNTIME_01` (non ouvert).

---

## 1. Pourquoi cette spec existe

Le moteur de morphologie est **livré et pur** : il transforme des `MorphologyFacts` en
descripteurs bornés et traçables. Personne ne l'alimente. L'audit ci-dessous montre que
le chemin de capture existant ne peut pas, en l'état, produire l'entrée que le moteur
déclare attendre — et qu'il existe **deux écrivains concurrents** sur la même table, avec
des sémantiques temporelles différentes.

Ce n'est pas une question de câblage. C'est une question de contrat.

---

## 2. Audit — deux écrivains, une table

| | **Écrivain A** | **Écrivain B** |
|---|---|---|
| Emplacement | `routers/auth_routes.py` — `profile_measurements_submit` | `services/body_profile.py` — `create_measurement` |
| Déclenchement | formulaire `POST /profile/measurements` | fonction de service |
| Temporalité | **upsert par date** — met à jour la ligne du jour | **insertion systématique** à `now()` |
| Écrasement | met à jour **uniquement les champs non nuls** soumis | écrit les clés fournies |
| Validation | analyse **en ligne**, locale à la route | `parse_and_validate` + liste blanche `_FIELD_BY_KEY` |
| Propriété | `CurrentUser` (session) | `user_id` en paramètre ; `get_owned_measurement` pour la lecture |

**Le conflit n'est pas stylistique.** A traite `BodyMeasurement` comme un **état courant
révisable** ; B la traite comme une **série temporelle append-only**. Les deux coexistent
sur la même table. Une mesure saisie deux fois le même jour produit une ligne mise à jour
par un chemin, et deux lignes par l'autre.

### 2.1 Décision — écrivain canonique

**`body_profile.create_measurement` est l'écrivain canonique**, pour trois raisons tirées
du code et non de la préférence :

1. il porte déjà la **validation bornée** (`BODY_MEASUREMENT_FIELDS`, min/max par champ) ;
2. il porte déjà la **liste blanche** de champs, donc un champ inconnu ne peut pas y entrer ;
3. il porte déjà le **garde-fou de formulation** non médical (`FORBIDDEN_WORDING`).

L'écrivain A devra **déléguer** à B. Sa sémantique d'upsert-par-jour n'est pas conservée :
une mesure est un **fait daté**, et corriger une saisie n'est pas la même chose que
réécrire l'histoire. La correction reste possible en ajoutant une mesure ultérieure.

> **Compatibilité historique.** Les lignes déjà écrites par A restent valides et ne sont
> **pas** migrées. Le passage à une sémantique append-only est **prospectif** : aucune
> ligne existante n'est dupliquée, fusionnée ni supprimée. Une base qui contient
> aujourd'hui des lignes upsertées reste lisible sans transformation.

---

## 3. Audit — ce que le moteur attend vs ce qui existe

`MorphologyFacts` déclare onze entrées. Voici ce qu'une base réelle peut fournir
**aujourd'hui**.

| Champ attendu | Source persistée | État |
|---|---|---|
| `height_cm` | `User.height_cm` | ✅ mais **hors** `BodyMeasurement` |
| `wingspan_cm` | — | ❌ **aucune colonne** |
| `ape_index_cm` | dérivé `wingspan − height` | ❌ inatteignable |
| `waist_cm` | `BodyMeasurement.waist_cm` | ✅ |
| `chest_cm` | `BodyMeasurement.chest_cm` | ✅ |
| `thigh_cm` | `thigh_cm_left` / `thigh_cm_right` | ⚠️ **latéralisé**, le moteur veut une valeur |
| `calf_cm` | `calf_cm` **et** `calf_cm_left/right` | ⚠️ **trois colonnes**, dont une héritée |
| `observations` | — | ❌ aucune surface de saisie |
| `focus_candidates` | — | sortie du moteur, pas une entrée |
| `source`, `notes` | — | métadonnées |

Trois constats méritent d'être nommés :

**(a) `wingspan_cm` est absent, et c'est bloquant pour l'ape index.** Le moteur dérive
l'ape index de `wingspan − height` et refuse explicitement toute longueur de segment
osseux. Sans envergure persistée, cette branche entière du moteur est morte.

**(b) La latéralité est capturée mais pas consommée.** La table est latéralisée
(gauche/droite) depuis une migration antérieure ; le moteur veut une valeur unique par
membre. Il faut une **convention de réduction explicite**, pas un choix implicite.

**(c) `shoulder_width_cm` est capturé et n'est lu par personne.** Le champ existe, il est
borné (30–60 cm), il est saisi — et `MorphologyFacts` ne le déclare pas, alors que
`OBSERVATION_VOCAB` contient `clavicular_width`. Une observation qualitative est attendue
là où une mesure quantitative existe déjà.

---

## 4. Décisions

### 4.1 `wingspan_cm` — colonne persistée requise : **OUI**

L'envergure est un **fait directement mesurable** au mètre ruban, comme le tour de taille.
Elle n'est ni inférée, ni photographique, ni osseuse. Elle entre donc pleinement dans le
périmètre autorisé.

- colonne `wingspan_cm` sur `BodyMeasurement`, `Float`, **nullable**, migration **additive** ;
- bornes de validation à ajouter à `BODY_MEASUREMENT_FIELDS`, cohérentes avec
  `HEIGHT_BOUNDS` (120–230 cm) puisque l'envergure est du même ordre que la taille ;
- **aucun backfill.** Une envergure non mesurée reste `NULL` ; elle n'est jamais estimée
  depuis la taille, ce qui reviendrait à fabriquer l'ape index qu'on cherche à mesurer.

`ape_index_cm` reste **dérivé**, jamais stocké : c'est une soustraction de deux faits, pas
un fait.

### 4.2 `height_cm` — source unique, sans duplication

La taille reste sur `User`. Elle n'est **pas** recopiée dans `BodyMeasurement` : une
seconde copie divergerait, et la taille adulte ne varie pas à l'échelle d'une série de
mesures. L'adaptateur lit `User.height_cm` et l'associe à la mesure la plus récente.

**Conséquence assumée** : une taille modifiée rétroactivement change l'ape index calculé
pour des mesures anciennes. C'est acceptable pour une donnée quasi constante, et
préférable à une duplication qui mentirait silencieusement.

### 4.3 Latéralité — convention de réduction explicite et versionnée

Le moteur reçoit une valeur par membre. La réduction retenue est la **moyenne des deux
côtés lorsque les deux existent**, sinon le côté disponible seul.

Ce n'est pas une vérité physiologique, c'est une **convention d'agrégation**, et elle doit
être nommée comme telle dans le code, versionnée, et exposée dans le `basis`. Le maximum
et le minimum ont été écartés : le premier flatte, le second pénalise, et aucun des deux
ne décrit « la cuisse » mieux que la moyenne.

**Asymétrie non exploitée.** L'écart gauche/droite est une donnée réelle et potentiellement
intéressante, mais l'interpréter relève du diagnostic postural — **interdit**. Il est
conservé en base, il n'entre pas dans `MorphologyFacts`.

### 4.4 `calf_cm` hérité — lecture, pas migration

Trois colonnes coexistent (`calf_cm`, `calf_cm_left`, `calf_cm_right`). L'adaptateur
applique une **précédence de lecture** : les colonnes latéralisées d'abord, la colonne
héritée en repli si elles sont vides.

**Aucune migration de données.** Fusionner ou supprimer la colonne héritée toucherait des
données historiques, ce que le contrat du dépôt interdit. Elle vieillit sans être écrite.

### 4.5 `shoulder_width_cm` — hors périmètre de cette spec

Le champ est capturé, borné, et inutilisé. Le relier à `clavicular_width` exigerait de
définir à partir de quelle largeur une clavicule est « favorable » — c'est un seuil
morphologique, il n'est adossé à aucune source dans le dépôt, et l'inventer serait
exactement l'inférence que le §5 interdit.

**Consigné comme question ouverte**, pas résolu ici. La mesure continue d'être capturée.

### 4.6 `observations` — capture opérateur, pas utilisateur

`OBSERVATION_VOCAB` est un vocabulaire fermé de constats qualitatifs. Aucune surface ne les
saisit. Cette spec **n'ouvre pas** de surface utilisateur pour eux : demander à un
utilisateur de qualifier ses propres « quadriceps relativement forts » produirait une
donnée déclarative présentée comme une observation.

Le runtime devra donc fonctionner avec `observations = ()` et une confiance réduite en
conséquence. C'est une limite énoncée, pas un oubli.

---

## 5. Garde-fous durs — périmètre de capture

Sont **interdits**, sans exception et sans dérogation par prompt :

- **aucune photo**, aucune estimation visuelle, aucun upload d'image corporelle ;
- **aucune longueur osseuse inférée** — ni fémur, ni humérus, ni segment ;
- **aucune inférence de masse grasse** — ni Navy, ni plis, ni ratio présenté comme tel ;
- **aucun diagnostic postural**, y compris depuis l'asymétrie gauche/droite ;
- **aucune inférence d'insertion musculaire.**

Ces cinq interdits sont déjà portés par `GUARDED_NOT_DEDUCTIBLE` dans le moteur. Cette spec
les étend à la **capture** : ce qui n'est pas déductible ne doit pas non plus être demandé
sous une forme qui suggère qu'il le deviendrait.

**Seuls des faits directement mesurés** — au mètre ruban, à la balance — sont capturés.

---

## 6. Sémantique NULL / manquant

| État | Signification | Interdit |
|---|---|---|
| colonne `NULL` | non mesuré | l'estimer depuis une autre mesure |
| aucune ligne | jamais mesuré | fabriquer une ligne par défaut |
| champ hors bornes | rejeté à la saisie | le tronquer silencieusement |
| `MorphologyFacts` partiel | entrée légitime | compléter les trous |

**Un fait absent réduit la confiance du descripteur ; il ne déclenche jamais une valeur de
remplacement.** C'est la même règle que la chaîne P0.4 applique à la récupération, et pour
la même raison : un consommateur doit pouvoir distinguer « mesuré » de « supposé ».

---

## 7. Propriété et autorisation

- toute lecture et toute écriture sont **scopées au propriétaire** ;
- le propriétaire vient de la **session authentifiée**, jamais d'un champ de formulaire ;
- `get_owned_measurement` est le point de lecture unitaire canonique ;
- une mesure appartenant à un autre utilisateur est **introuvable**, pas « refusée » —
  l'existence même ne doit pas fuir.

---

## 8. Ce que le runtime devra prouver

`Sb_MORPHO_PROFILE_RUNTIME_01` sera accepté s'il démontre :

1. un seul écrivain canonique, l'autre chemin y déléguant ;
2. `wingspan_cm` persisté, nullable, migration additive, **zéro backfill** ;
3. la convention de réduction latérale nommée, versionnée, présente dans le `basis` ;
4. la précédence de lecture `calf_cm` sans aucune écriture sur la colonne héritée ;
5. un fait manquant qui **réduit la confiance** au lieu d'être comblé ;
6. les cinq interdits du §5 absents de la surface de capture comme du moteur ;
7. **priorité déclarée ≠ candidat morphologique** — les deux sources restent distinctes et
   distinguables par le consommateur, conformément à `Sb_TRAINING_PREFERENCES_01` ;
8. la sémantique scientifique du moteur pur **inchangée** — le runtime s'adapte au moteur,
   jamais l'inverse.

---

## 9. Questions ouvertes

| # | Question | Pourquoi elle n'est pas tranchée ici |
|---|---|---|
| OQ-1 | `shoulder_width_cm` → `clavicular_width` : quel seuil ? | Aucune source dans le dépôt ; l'inventer serait une inférence morphologique. |
| OQ-2 | L'asymétrie gauche/droite doit-elle être exposée, et sous quelle formulation non diagnostique ? | Frôle le §5 ; mérite une décision produit explicite. |
| OQ-3 | Les `observations` opérateur méritent-elles une surface, et pour qui ? | Une surface utilisateur transformerait un constat en déclaration. |
| OQ-4 | L'ape index doit-il être affiché à l'utilisateur, ou rester une entrée interne du moteur ? | Question de produit, pas de capture. |

Aucune ne bloque le runtime : toutes portent sur des extensions, pas sur le chemin
principal.

---

## 10. Non-goals

Ce document **n'autorise pas** et le runtime associé **ne livrera pas** :

- de capture photo ou d'estimation visuelle ;
- d'inférence de masse grasse, de longueur osseuse, d'insertion ou de posture ;
- de migration destructive, de fusion ou de suppression de colonne héritée ;
- de backfill, y compris « raisonnable », d'une envergure non mesurée ;
- de modification de la sémantique scientifique de `morphology_profile` ;
- d'écrasement d'une priorité **déclarée** par un candidat **inféré** ;
- de nouvelle taxonomie anatomique — la taxonomie `BodyZone` canonique reste seule ;
- de vocabulaire médical dans une chaîne rendue ;
- de surface `/morphologie` dédiée ni de refonte du profil ;
- de déploiement.

---

## Verdict

**Spec livrable, runtime non ouvert.**

L'audit a produit un résultat plus net qu'attendu : le blocage n'est pas le câblage mais
**l'absence d'une colonne** (`wingspan_cm`) sans laquelle une branche entière du moteur est
inatteignable, **plus** un conflit d'écrivains que personne n'avait tranché. Les deux se
règlent par une migration additive et une délégation — aucune réécriture du moteur, aucune
donnée historique touchée.

La limite la plus honnête de ce document : sans `observations`, le runtime produira des
descripteurs à **confiance structurellement réduite**. C'est correct — mais il faut le
savoir avant de brancher un planificateur dessus, pas après.
