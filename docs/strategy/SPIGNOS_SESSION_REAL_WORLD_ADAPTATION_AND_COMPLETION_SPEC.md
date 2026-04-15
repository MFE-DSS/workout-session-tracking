# SPIGNOS — Session Real-World Adaptation & Completion Spec

**Chantier:** R_T3SX_session_real_world_adaptation
**Date:** 2026-04-15
**Status:** Spec draft — pending validation
**Extends:** Sx_01 (feedback rationalization, built), Sx_02 (mobile exercise entry UX, built), Sx_03 (substitution graph, built)
**Precedes:** Sb_04 (history & analytics alignment), and any body-engineering work that depends on honest volume-per-zone

---

## 1. Contexte

Retour d'usage réel au gym, séance dos, avril 2026.
- Un exercice prévu (tirage unilatéral machine) n'était pas disponible en salle.
- L'utilisateur a noté le manque dans le free_note de la séance.
- Dans d'autres sessions, l'utilisateur a voulu prolonger le travail avec un exercice supplémentaire : aucun mécanisme n'existe, il a écrit une note.
- Après l'enregistrement final de la séance, la page reste identique à l'état en-cours. Pas de clôture visuelle, pas de résumé, pas de CTA de suite.

Ces trois constats touchent trois strates différentes du produit :
1. la **crédibilité du catalogue** en salle commerciale (pas seulement le catalogue idéal),
2. la **liberté de conduire sa séance** sans déformer le template,
3. la **réponse de l'interface** quand l'utilisateur appuie sur "Terminer".

Le chantier R_T3SX adresse les trois ensemble parce qu'ils convergent sur un même terrain : la séance *réelle* (contrainte par l'équipement, les envies du jour, et l'état après-séance), par opposition à la séance *prévue* (idéale, alignée au template).

## 2. Principes produit (non négociables)

- **Template = source de vérité immuable.** Une séance adapte, n'altère jamais, le template.
- **Historique résilient.** Toute évolution du catalogue (substitutes, added) doit préserver les sessions déjà loguées telles qu'elles.
- **Snapshots > FK.** Les noms snapshot dans `SessionExercise` restent la source de vérité d'identité.
- **Classifiabilité obligatoire.** Tout exercice (prescrit, substitué, ajouté) doit être résolvable par `classify_exercise()` sinon il est invisible aux analytics.
- **Mode focus exercice préservé.** Les changements template restent dans la logique `<details>` accordéon livrée par Sb_02.
- **Zéro JS lourd.** Formulaires POST natifs, `<details>`, `<select>`, redirects anchorés. Aucun state client.
- **Pas de pseudo-intelligence.** Aucune recommandation ML, aucune suggestion "tendance". Les graphes de substitution sont curés à la main dans le JSON catalogue, validés par QA.

## 3. Objectifs

| # | Objectif | Mesure de succès |
|---|---|---|
| O1 | Le graphe de substitution couvre les vrais scénarios de salle commerciale (machine guidée occupée, zone câble prise, ne restent que les haltères, etc.) | ≥ 60 % des exos "machine-dependent" du catalogue ont 2+ substituts de familles d'équipement différentes |
| O2 | L'utilisateur peut enrichir une séance sans toucher au template, ni polluer les notes | 0 mention terrain de type "j'ai fait aussi X mais je l'ai mis en note" après livraison |
| O3 | La fin de séance déclenche une vraie réponse visuelle + un résumé utile, lecture seule | Temps perçu entre "je valide" et "j'ai compris que c'est fini" < 1s ; pas de modal ; pas de célébration |
| O4 | Analytics (volume zone, muscle_scoring, physique dashboard) comptent correctement les ajouts et les substitutions | Volume zone calculé = volume réellement exécuté, pas le volume prescrit |

## 4. Portée

**Dans le périmètre :**
- Enrichissement de `data/reference_split.json` avec une structure de substitution par famille d'équipement.
- Nouvelle colonne `SessionExercise.origin` (`template` | `added`).
- Route + template de recap post-clôture (`/sessions/{id}/done` ou mode de rendu dédié).
- Nouveaux endpoints pour ajouter un exercice à une séance en cours.
- Règles analytics explicites pour added/substituted.
- Mise à jour de `catalog_qa.py` avec contrainte de couverture minimale.
- Mise à jour de `muscle_scoring`, `exercise_history`, `export_builder` pour refléter `origin`.

**Hors périmètre :**
- Création d'entités `Exercise` canoniques en base (reporté, décision Sx_03 toujours valide).
- Exercices personnalisés par l'utilisateur (doit venir du canon catalogue).
- Substitution bidirectionnelle (A→B n'implique pas B→A).
- Suggestions ML de substitution ou d'ajout.
- Analytics "fréquence de substitution par exo" (collectable en post-hoc si besoin).
- Réorganisation du template pendant la séance.

---

## 5. Section I — Substitutions réalistes (Axe 1)

### 5.1 Problème

Le graphe actuel (Sx_03/Sb_03 livré) couvre 9 exercices sur 113, avec 1-2 substituts quasi-tous haltères. En salle Fitness Park / Basic-Fit / club généraliste, plusieurs scénarios cassent le rail :

- machine guidée occupée **ET** haltères équivalents occupés → aucun recours dans l'app
- exercice câble (poulie basse/haute) prescrit → l'utilisateur n'a jamais de fallback câble dans la liste actuelle
- exercice avec posture spécifique (hack squat, hip thrust smith) → fallback haltère parfois absurde mécaniquement

L'utilisateur sort du rail et note l'absence dans `free_note`. Ces notes ne sont pas consommées par les analytics : volume zone compté faux, body engineering aveugle, crédibilité produit dégradée.

### 5.2 Modèle de substitution proposé

**Principe** — pour chaque exercice "machine-dependent" du catalogue, on pré-définit les alternatives par **famille d'équipement**, et on garantit qu'au moins deux familles distinctes sont couvertes.

**Familles d'équipement (taxonomie introduite) :**

| Clé | Libellé | Exemple |
|---|---|---|
| `machine_guidee` | Machine guidée / plate-loaded | Chest Press, Hack Squat, Rowing chest-supported |
| `cable` | Câble / poulie | Écarté câble, Face pull, Tirage poulie |
| `free_weight` | Haltères / barre libre | Développé haltères, Rowing haltère |
| `bodyweight` | Poids de corps | Dips, Tractions, Pompes lestées |
| `smith` | Smith machine | Incline Smith, Hip thrust Smith |

**Classes de dépendance** (attribuées par exercice dans le JSON) :

| Classe | Définition | Couverture minimale requise |
|---|---|---|
| `machine_dependent` | L'exercice prescrit ne peut être réalisé qu'avec une pièce d'équipement spécifique (machine, câble, Smith) | 2 substituts minimum, au moins **2 familles différentes** |
| `equipment_portable` | L'exercice peut être fait avec plusieurs équipements de base sans perte majeure (ex. curl haltères ↔ curl barre) | 1 substitut recommandé, pas obligatoire |
| `bodyweight_universal` | Pompes, abdos, étirements | 0 substitut requis |

### 5.3 Extension de schéma JSON

```json
{
  "code": "E2",
  "name": "Chest Press machine",
  "set_scheme": "3x 8-12",
  "dependency_class": "machine_dependent",
  "equipment_family": "machine_guidee",
  "substitutes": [
    {"name": "Développé couché haltères", "family": "free_weight"},
    {"name": "Dips pectoraux (buste penché)", "family": "bodyweight"},
    {"name": "Écarté câble poulie basse convergent", "family": "cable"}
  ],
  "rep_targets": [...]
}
```

**Compatibilité descendante** — `substitutes` peut rester une liste de strings pour les exos déjà peuplés, lus comme `{name: <string>, family: null}`. Le champ `dependency_class` est optionnel (défaut `equipment_portable`). Pas de migration destructive.

### 5.4 Gouvernance catalogue

`catalog_qa.py` doit vérifier :

1. Tout exercice `dependency_class=machine_dependent` a ≥ 2 substituts couvrant ≥ 2 familles différentes.
2. Tout `substitutes[].name` reste classifiable par `classify_exercise()` (règle Sx_03 préservée).
3. Aucune famille référencée hors de la taxonomie close (§5.2).
4. Avertissement (pas erreur) si un exercice `machine_dependent` n'a pas de substitut `family=free_weight` (fallback universel recommandé mais pas requis).

Ces checks sont bloquants pour le versionnage du catalogue (bump de version JSON = pass QA obligatoire).

### 5.5 Exposition UX

Le `<select>` existant reste la brique principale, enrichi :

```
Exercice prévu : Chest Press machine
[ Chest Press machine (prévu) ▾ ]
  ├─ Développé couché haltères — haltères
  ├─ Dips pectoraux (buste penché) — poids de corps
  └─ Écarté câble poulie basse convergent — câble
```

- Les substituts sont groupés par famille (optgroup) quand il y en a 3+.
- Le nom de la famille est visible en suffixe → l'utilisateur choisit en fonction de ce qui est libre dans sa salle.
- Le lock après premier set complété (Sx_03) est conservé.
- **Aucun champ de saisie libre** — la discipline catalogue reste ferme. Si l'utilisateur n'a rien, il fait l'Axe 2 (ajout) ou bascule sur l'exercice suivant.

### 5.6 Liste initiale des exos à enrichir

Scan rapide du catalogue réel, exercices `machine_dependent` dont la couverture actuelle est insuffisante :

| Template | Code | Exercice | Substituts manquants (familles) |
|---|---|---|---|
| push-a | E1 | Incline Smith Press | câble, bodyweight |
| push-a | E2 | Chest Press machine | câble |
| push-a | E4 | Neutral Grip Shoulder Press machine | câble, bodyweight |
| pull-a | E1 | Pull-down machine / lat-pulldown | free_weight (rowing haltère biais largeur), câble (tirage poulie) |
| pull-a | E4 | Rear delt fly machine | free_weight (oiseau haltères) |
| pull-b | E1 | Rowing machine chest-supported | câble |
| legs-a | E1 | Hack Squat machine | smith, free_weight |
| legs-a | E2 | Leg Press | free_weight (goblet squat lourd) |
| legs-b | E4 | Hip thrust Smith machine | free_weight |

Liste indicative — la curation exacte est faite dans le sprint de build et validée par QA.

### 5.7 Implications historique & analytics

- **Pas d'impact rétroactif.** Les sessions loguées avant le build conservent leur `substituted_name` tel quel (Sx_03 a déjà le contrat).
- **Volume zone (muscle_scoring).** Déjà classifié via `actual_exercise_name(se)` (Sb_03). Aucun changement requis.
- **Exercise history.** Le nom affiché reste `actual_exercise_name()`. Ajouter une pastille famille d'équipement en micro-texte est un nice-to-have, non requis.
- **Compare mode futur.** Permet à terme de comparer "même exercice, familles différentes" (hack squat vs leg press sur quads). Spec ultérieure.

### 5.8 Décisions tranchées

| Question | Décision | Raison |
|---|---|---|
| Faut-il un champ libre "autre" en dernier recours ? | **Non** | Casse classifiabilité, pollue muscle_scoring. Si rien ne convient, passer à l'Axe 2 (ajout) ou skip. |
| Faut-il stocker `family` dans `SessionExercise` à la substitution ? | **Non** | Derivable depuis le nom + classifier. Gardons le schéma mince. |
| Faut-il exposer le graphe dans la page `/library/{slug}` ? | **Oui, en phase 2** | Améliore la lecture produit. Pas bloquant pour R_T3SX. |
| Bidirectionnalité (A→B ⇒ B→A) ? | **Non** | Déjà tranché Sx_03, maintenu. |

---

## 6. Section II — Exercice ajouté à la séance (Axe 2)

### 6.1 Problème

L'utilisateur veut parfois :
- prolonger le travail sur une zone sous-sollicitée par son template du jour,
- profiter d'une machine libre qu'il aime,
- rattraper un retard identifié (ex. deltoïdes postérieurs faibles),
- ajouter un finisher.

Aujourd'hui, aucun mécanisme. Le contournement (note libre) n'alimente aucune analytics. Le volume zone calculé par muscle_scoring est faux à la baisse.

### 6.2 Distinction fondamentale (à documenter dans le code)

| Notion | Colonne | Sens |
|---|---|---|
| Template exercise | `origin='template'`, `substituted_name=NULL` | Exercice prescrit par le template, exécuté tel quel |
| Substituted exercise | `origin='template'`, `substituted_name!=NULL` | Exercice prescrit par le template, remplacé par une alternative du graphe — même slot, même rep_targets |
| **Added exercise** | `origin='added'`, `substituted_name=NULL` | **Exercice hors template, ajouté pendant la séance, sans rep_targets prescrits** |

**Invariant clé** — un added exercise n'a pas de `template_exercise_id` (FK nullable, mise à NULL). Il porte un `exercise_name_snapshot` (nom canon choisi) et un `exercise_code_snapshot` artificiel (ex. `A1`, `A2`, `A3`…) pour préserver l'unicité (session_id, position) et permettre l'affichage.

### 6.3 Modèle de données

Nouvelle colonne :
```
SessionExercise.origin   VARCHAR(16) NOT NULL DEFAULT 'template'
```

Valeurs : `template` | `added`. Default `template` pour rétro-compat (toutes les sessions existantes ont origin=template implicite).

Alembic migration :
1. Ajout colonne `origin` avec default `'template'` + backfill immédiat `UPDATE session_exercises SET origin='template'`.
2. Rendre la colonne NOT NULL après backfill.

Aucune autre structure ne change. `template_exercise_id` reste nullable (déjà le cas, pour résilience reseed).

### 6.4 UX de l'ajout

**Point d'entrée unique et discret** — une zone `+ Ajouter un exercice` sous la liste des exos, visible **uniquement tant que la séance est `in_progress`**.

```
[ carte exercice E1  •••  ]
[ carte exercice E2  •••  ]
...
[ carte exercice E7  •••  ]

┌──────────────────────────────────────┐
│  + Ajouter un exercice (optionnel)  │
│    depuis le canon catalogue         │
└──────────────────────────────────────┘

[ section-feedback ]
[ Terminer la séance ]
```

**Flux de l'ajout (aucun JS) :**

1. Clic sur la zone → expansion `<details>` vers un formulaire d'ajout.
2. Formulaire contenu :
   - `<select>` des exercices canon du catalogue, groupés par zone musculaire principale (pecs, dos, épaules…). Uniquement des noms classifiables.
   - Un `<select>` minimal de schéma de sets (presets : `3x 8-12`, `3x 10-15`, `4x 6-10`, `2x AMRAP`). Réutilise les presets déjà employés dans le catalogue — pas de création libre.
   - Bouton POST `Ajouter`.
3. POST → création d'un `SessionExercise` avec :
   - `origin='added'`
   - `position = max(positions) + 1` (toujours en fin de séance, voir §6.5)
   - `exercise_code_snapshot = 'A' + rang d'ajout` (A1, A2, A3)
   - `exercise_name_snapshot = nom choisi`
   - `template_exercise_id = NULL`
   - `set_logs` créés depuis le preset choisi, tous `kind='work'`, `completed=False`
4. Redirect `?active={new_se.id}#exercise-{new_se.id}` → la carte ajoutée est ouverte, prête à saisie.

### 6.5 Position des added (question tranchée)

**Décision : les added exercises sont toujours appendés en fin de séance (`position > max(template_positions)`).**

Raisons :
- Le template reste lisible d'un coup d'œil (les positions 1..N sont prescrites).
- Le bandeau jump bar garde son sens : `E1 E2 ... E7 | A1 A2 | FB`.
- Un ajout en milieu de séance réordonnerait les positions → casse `uq_session_exercise_position` ou force un recalcul.
- Simplicité du POST (pas d'UI pour "insérer avant/après").

**Conséquence UX acceptée** — si l'utilisateur veut faire son ajout entre E3 et E4, il le loggue après E7 quand même. L'historique reflétera l'ordre de logging, pas l'ordre d'exécution réel. Ce compromis est jugé acceptable : la valeur analytique (volume zone correct) prime sur la fidélité chronologique intra-session.

### 6.6 Limites

- **Cap soft : 5 added exercises par session.** Au-delà, la zone d'ajout se grise avec message `Maximum d'ajouts atteint. Si ta séance est devenue un programme, crée-en un.`. Le cap est un garde-fou, pas une restriction métier rigide.
- **Pas de suppression via l'UI.** Un added exercise peut être vidé (laisser les sets à completed=false) mais pas détruit depuis la séance. Suppression via la page `admin_sessions` existante (réutilise `delete_session` au niveau session entière ; per-exercise delete hors périmètre).
- **Pas de drag-and-drop, pas de réordonnancement.** YAGNI.

### 6.7 Source des exercices ajoutables

**Le `<select>` d'ajout ne liste QUE les noms classifiables par `classify_exercise()`.**

Construction du select à la volée côté serveur :
1. Collecte : set de tous les noms d'exercices présents dans `reference_split.json` (tous templates confondus) + tous les `substitutes[].name`.
2. Filtre : classifiable par `classify_exercise()` (garantit zone attribuable).
3. Groupage par zone primaire (définie dans `muscle_mapping.py`).
4. Dé-duplication par nom exact.

Estimation : ~130-150 noms uniques (113 exos + ~40 substitutes non-dupliqués). Select groupé reste utilisable en mobile.

**Pas de saisie libre. Pas d'import utilisateur. Pas de création in-session.**

### 6.8 Impacts analytics — règles explicites

| Mesure | Comportement sur added | Raison |
|---|---|---|
| `completion_rate_30d` (progress page) | **Exclus** du numérateur et du dénominateur | Les added n'étaient pas prescrits → les compter biaise la lecture "conformité au plan" |
| `work_sets_done_30d` / `work_sets_total_30d` | **Exclus** | Idem |
| `avg_success_score_30d` | **Inclus** | Le score dérivé (Sb_01) reste valide : l'utilisateur s'est fixé une plage de reps |
| `muscle_scoring` / volume zone | **Inclus** | C'est le vrai volume exécuté — la raison d'être de la feature |
| Physique dashboard (Body Engineering) | **Inclus** | Idem |
| `quality_score` de la séance | **Inclus partiellement** — les work sets added comptent dans le `completion_pct_work_sets` de la séance courante, mais pas dans le rolling 30j | Cohérence intra-séance |
| Exercise history | **Séparé** — les added apparaissent sous la bannière "Ajouts" par session, pas dans la timeline par slot | Pas de slot code stable → pas de comparaison longitudinale (hors périmètre) |
| Leaderboard squad | **Inclus via quality_score** | Transitif |
| Export JSON/CSV | **Inclus avec `origin='added'`** | Données complètes |

Ces règles doivent être **documentées dans `SPIGNOS_SCORING_RULES_V1.md`** après build.

### 6.9 Décisions tranchées

| Question posée par le cadrage | Décision | Raison |
|---|---|---|
| Ajout seulement en fin ou aussi entre deux exos ? | **En fin seulement** (§6.5) | Invariant template, simplicité modèle |
| Limite au nombre d'added ? | **Cap soft à 5** | Garde-fou UX, pas métier |
| Mêmes exercices que le catalogue ? | **Oui, canon strict** | Classifiabilité obligatoire pour analytics |
| Lisibilité séance suivie/adaptée/enrichie ? | **Badge `origin` visible dans l'historique** : `Ajout`, `Substitué`, ou rien par défaut (template suivi) | Lecture évidente sans surcharger |

---

## 7. Section III — Terminal state de fin de séance (Axe 3)

### 7.1 Problème

Chemin actuel après clic "Terminer la séance" :
1. POST `/sessions/{id}/feedback` avec `action=end`.
2. DB : `status=completed`, `ended_at=now()`.
3. Redirect 303 → `/sessions/{id}#session-feedback` (même page, même template).
4. Render : identique à l'état en cours + badge `Terminée` + note `Séance terminée — éditable via Rouvrir.`.

Défaut produit : **la transition d'état n'est pas perçue**. Tous les champs restent éditables (désactivation purement visuelle minimale), le jump bar est toujours là, l'utilisateur ne sait pas ce qui s'est passé. Il scrolle pour vérifier que ses sets sont bien enregistrés.

### 7.2 Cible produit

- Clôture **sobre** (pas de modal, pas de célébration, pas de confetti).
- Changement d'état **visible au premier regard**.
- Résumé **utile** (pas de vanity metrics).
- CTA **cohérents** (où va l'utilisateur après une séance ?).
- Lecture seule **par défaut**, ré-ouvrable explicitement.
- Aucun JS nouveau. Redirect serveur + template dédié.

### 7.3 Décision d'architecture

**Option retenue : nouvelle route `GET /sessions/{id}/done` + template `session_done.html` dédié.**

Flux :
1. POST `action=end` → DB status=completed → redirect 303 → `GET /sessions/{id}/done`.
2. `/sessions/{id}/done` :
   - Si `status != completed` → redirect vers `/sessions/{id}` (ne jamais pouvoir atteindre le recap d'une séance pas finie).
   - Sinon render `session_done.html` (lecture seule, résumé, CTA).
3. L'ancien `/sessions/{id}` continue d'afficher la séance en mode éditable **pour `status=in_progress` uniquement**. Pour une séance completed, il redirige vers `/done` **ou** affiche une version éditable quand arrivé depuis `Rouvrir`. Cf. §7.5.

**Options écartées et pourquoi :**

| Option | Raison de l'écarter |
|---|---|
| Modal de confirmation | Casse le zéro-JS, casse le flow mobile, cheap visuellement |
| Bannière + lecture seule sur la même page | La page reste mentalement "la séance en cours" — pas de rupture perçue |
| Célébration / score final / comparaison leaderboard | Gamification contraire à la discipline produit (cf. PRODUCT_SPEC.md) |
| Redirect direct vers `/dashboard` | Perd le contexte de la séance qui vient de se terminer |
| Redirect vers `/history` | Dilue : l'utilisateur n'a pas demandé à voir l'historique |

### 7.4 Contenu du template recap (`session_done.html`)

Structure mobile-first, densité élevée, rien de cosmétique :

```
┌──────────────────────────────────────────────┐
│  ✓ Séance terminée                           │
│  Push A — Pecs épaisseur + Delts + Triceps  │
│  Lun 13/04 · 18h45 → 20h02 · 1h17           │
└──────────────────────────────────────────────┘

┌─ Résumé ────────────────────────────────────┐
│  Work sets : 18 / 21 cochés (86 %)           │
│  Score moyen : 82                             │
│  Score de séance : 78                         │
│  Ajouts : 1 exercice (A1 · Curl pupitre)     │
│  Substitutions : 1 (E2 → Développé haltères) │
│  Bodyweight : 79,4 kg                         │
│  Concentration : haute · État : bon           │
└──────────────────────────────────────────────┘

┌─ Par exercice ──────────────────────────────┐
│  E1  Incline Smith Press     3/3  ✓  100    │
│  E2  → Développé haltères    3/3  ✓   80    │
│  E3  ...                                      │
│  A1  Curl pupitre (ajout)    2/3      80    │
└──────────────────────────────────────────────┘

[ Voir la synthèse → ]     [ Historique → ]

  ─────────────────────────
  Rouvrir pour éditer
```

**Points de design :**
- Header : badge `✓ Séance terminée` + nom template + durée calculée.
- Résumé : chiffres bruts, pas de grade, pas de note émotionnelle.
- Par exercice : ligne par ligne, code + nom + sets + score. Les substitutions affichent `→ nom_substitué`. Les added affichent `(ajout)`.
- Deux CTA primaires côte à côte : `Voir la synthèse` (dashboard) et `Historique`.
- CTA tertiaire discret en bas : `Rouvrir pour éditer` → POST `action=reopen` → redirect `/sessions/{id}`.
- Aucun formulaire de saisie sur cette page. Pure lecture.

### 7.5 Gestion de `/sessions/{id}` pour une séance completed

Deux sous-cas :

| Cas | Comportement |
|---|---|
| Arrivée directe sur `/sessions/{id}` (status=completed) via historique ou bookmark | **Redirect 303 → `/sessions/{id}/done`** |
| Arrivée sur `/sessions/{id}` après clic `Rouvrir` (status bascule à in_progress) | Render normal éditable (pas de redirect, status est déjà `in_progress`) |

Cela implique : `Rouvrir` change **d'abord** le status en DB puis redirige. `/sessions/{id}/done` n'est jamais atteint pour une séance in_progress.

### 7.6 Interactions avec les autres axes

- **Added exercises (Axe 2)** : apparaissent dans le recap avec badge `(ajout)`. Zone d'ajout **masquée** sur la page recap (l'utilisateur doit `Rouvrir` pour en ajouter un a posteriori).
- **Substitutions (Axe 1)** : affichées dans le recap avec `→ nom`. Toujours lues via `actual_exercise_name(se)`.
- **Cardio sessions (Sb_cardio_capture)** : le recap affiche durée / BPM / calories machine au lieu de la table exercices (dispatch sur `template.kind`).
- **Mode focus exercice (Sx_02)** : inopérant sur le recap (lecture seule).

### 7.7 Implications analytics

- `/dashboard` et `/progress` voient la séance comme `completed` dès le POST `action=end`. Le recap ne change rien aux agrégats — il change uniquement la surface d'affichage.
- Les axes `score de séance` affichés dans le recap sont les mêmes que ceux affichés ailleurs (reuse `quality_score.py`).

---

## 8. Implications transverses

### 8.1 Modèle (Alembic)

Une seule migration couvre les trois axes :

1. Add `SessionExercise.origin` VARCHAR(16) NOT NULL DEFAULT 'template', avec backfill.
2. (Substitution structure JSON — pas de migration schema, c'est dans le catalogue.)
3. Aucune nouvelle table.

### 8.2 Services impactés

| Service | Changement |
|---|---|
| `substitution.py` | Étendre `get_substitutes()` pour retourner `{name, family}` quand disponible ; rester rétro-compatible sur les listes plates. |
| `session_builder.py` | Nouvelle fonction `add_exercise_to_session(session, name, scheme_preset) -> SessionExercise` avec `origin='added'`. |
| `muscle_scoring.py` | Aucun changement (déjà via `actual_exercise_name`). Vérifier que les added sont bien itérés (c'est le cas, on itère `session_exercises` entier). |
| `kpis.py` | Exclure `origin='added'` du calcul `work_sets_total/done_30d` et `completion_rate_30d`. Inclure dans `avg_success_score_30d`. |
| `quality_score.py` | Inclut tous les sets de la séance en cours — comportement inchangé. Règle `completion_pct_work_sets` calcule sur la séance entière. À documenter explicitement. |
| `exercise_history.py` | Séparer `added` dans un bucket "Ajouts" par session. Ne pas les mélanger dans la timeline par slot code. |
| `export_builder.py` | Ajouter colonne `origin` aux exports JSON/CSV. |
| `feedback.py` | `compute_success_score()` — pour un added, pas de `template_exercise` → fallback 80/set existant. OK tel quel. |

### 8.3 Templates impactés

| Template | Changement |
|---|---|
| `session_detail.html` | Zone `+ Ajouter un exercice` après la boucle exercises, visible si `status=in_progress`. Substitution select enrichi (groupage par famille, suffixe). |
| `session_done.html` | **Nouveau.** Template recap (§7.4). |
| `exercise_history.html` | Bannière "Ajouts" par session, pas dans la timeline slot. |
| `admin_sessions.html` | Badge nouveau : `origin=added` count si > 0. Nice-to-have. |

### 8.4 Gouvernance catalogue

`scripts/catalog_qa.py` — nouvelle règle §5.4. Bump `reference_split.json` version à la prochaine mouture enrichie (v8 → v9).

### 8.5 Tests impactés / nouveaux

| Test | Nature |
|---|---|
| `tests/test_substitution.py` | Étendre : parsing structure `{name, family}`, groupage select. |
| `tests/test_catalog_integrity.py` | Nouveau check §5.4. |
| `tests/test_session_added.py` | **Nouveau.** Ajout exo en cours, cap à 5, impossible sur session completed, classifiabilité obligatoire. |
| `tests/test_session_done.py` | **Nouveau.** Redirect POST→/done, lecture seule, Rouvrir fonctionnel, dispatch cardio. |
| `tests/test_kpis.py` | Vérifier exclusion added du completion_rate, inclusion dans success_score avg. |
| `tests/test_exercise_history.py` | Bucket added séparé. |

### 8.6 Dépendances inter-axes

```
Axe 1 (substitution) —— indépendant du reste
    │
    └─ peut être livré seul, améliore Sb_03 déjà en place

Axe 2 (added)    ┬── dépend faiblement d'Axe 1 (le select d'ajout réutilise la même classification)
                 │
                 └── doit livrer avant Axe 3 pour que le recap affiche added correctement

Axe 3 (terminal state) —— dépend d'Axe 2 pour le contenu du recap
                      └── sinon livrable seul, avec recap minimal (sans section added)
```

---

## 9. Collisions avec les docs verrouillées — vérification

| Doc | Collision ? | Détail |
|---|---|---|
| `SPIGNOS_EXERCISE_FEEDBACK_RATIONALIZATION.md` (Sx_01) | **Aucune** | Les added utilisent le même algo `compute_success_score()` avec le fallback "pas de rep_targets → 80/set". Cohérent. |
| `SPIGNOS_MOBILE_EXERCISE_ENTRY_UX.md` (Sx_02) | **Aucune** | Le `<details>` pattern est préservé pour toutes les cartes (template et added). La zone `+ Ajouter` est un `<details>` sœur, pas une surcharge du pattern. |
| `SPIGNOS_EXERCISE_SUBSTITUTION_GRAPH_SPEC.md` (Sx_03) | **Extension rétrocompatible** | La structure `substitutes: [{name, family}]` étend, ne casse pas, la forme `substitutes: [string]`. Le lock après premier set (§4 Sx_03) est conservé. |
| `SPIGNOS_EXERCISE_SYSTEM_ROADMAP.md` | **Insérer R_T3SX entre Sb_03 et Sb_04** | Logique : Sb_03 livre la graine, R_T3SX élargit la graine + ajoute added + recap. Sb_04 (history alignment) consomme les deux. |
| `SPIGNOS_EXERCISE_SYSTEM_CONSOLIDATION_SPEC.md` | **À actualiser** | Ajouter une ligne R_T3SX dans la matrice Spec×Build. |
| `SPIGNOS_SCORING_RULES_V1.md` | **À amender** | Documenter les règles §6.8 sur inclusion/exclusion des added. |
| `SPIGNOS_CATALOG_GOVERNANCE.md` | **À amender** | Documenter la taxonomie familles d'équipement §5.2 et la règle de couverture §5.4. |

Aucune rupture sémantique, aucune contradiction frontale.

---

## 10. Risques

| Risque | Sévérité | Mitigation |
|---|---|---|
| Le cap de 5 added / session frustre un utilisateur qui enchaîne les finishers | Basse | Cap soft, message explicite. Si remonté en usage réel, lever à 8. |
| Les noms canon dans le select d'ajout explosent (150+) et rendent le select illisible en mobile | Moyenne | Groupage par zone musculaire. Si insuffisant, phase 2 : champ de recherche (sans JS : `<datalist>`). |
| Un added mal classé compte faux dans muscle_scoring | Basse | Contrainte classifiabilité en aval + QA catalog. |
| La nouvelle colonne `origin` crée un mismatch historique | Basse | Backfill `'template'` à la migration — invariant respecté. |
| Le recap `/done` introduit un état indésirable si l'utilisateur clique `Rouvrir` puis revient en arrière | Basse | `Rouvrir` bascule DB puis redirect — pas d'état client. |
| La structure JSON substitutes {name, family} casse les tests qui parsent la liste plate | Basse | Coder le parser tolérant les deux formes. |
| User interprète "Ajouter un exercice" comme "modifier mon programme pour les prochaines fois" | Moyenne | Libellé produit explicite : `+ Ajouter un exercice (cette séance uniquement)`. |

---

## 11. Acceptance Criteria — Spec

- [x] Graphe de substitution : taxonomie familles définie, classes de dépendance définies, règle de couverture minimale définie.
- [x] Liste initiale d'exos à enrichir identifiée (§5.6).
- [x] Distinction tripartite template / substituted / added formalisée au niveau modèle (§6.2).
- [x] Décisions tranchées sur position des added (fin uniquement), cap (5 soft), source (canon strict).
- [x] Règles analytics par mesure documentées en table (§6.8).
- [x] Architecture terminal state tranchée (nouvelle route `/done`, template dédié, reopen explicite).
- [x] Contenu minimal du recap spécifié (§7.4).
- [x] Migration unique Alembic décrite (§8.1).
- [x] Impact fichier par fichier audité (§8.2-8.5).
- [x] Collisions avec les 6 docs verrouillées vérifiées, aucune rupture (§9).
- [x] Risques listés (§10).

## 12. Acceptance Criteria — Build (à instancier dans un plan ultérieur)

**Axe 1 :**
- [ ] Structure JSON `{name, family}` parsée avec rétro-compat.
- [ ] Champ `dependency_class` et `equipment_family` lus par le seed.
- [ ] QA script bloquant sur couverture insuffisante (machine_dependent < 2 familles).
- [ ] Select `<select>` regroupe les substituts par famille quand ≥ 3.
- [ ] 9 exos actuels migrés vers la nouvelle structure + 15 exos supplémentaires enrichis pour atteindre ≥ 60 % de couverture.

**Axe 2 :**
- [ ] Migration `origin` NOT NULL default `'template'` avec backfill.
- [ ] Zone `+ Ajouter un exercice` rendue sous les cartes exo si `status=in_progress`.
- [ ] POST d'ajout crée un SessionExercise `origin='added'`, `position=max+1`, code `A{N}`.
- [ ] Cap à 5 appliqué server-side.
- [ ] Select d'ajout : noms canon, classifiables, groupés par zone musculaire.
- [ ] muscle_scoring inclut added (volume zone).
- [ ] kpis exclut added de completion_rate / work_sets totaux 30j.
- [ ] Exercise history : bucket "Ajouts" par session.
- [ ] Export : colonne `origin` présente.

**Axe 3 :**
- [ ] Route `GET /sessions/{id}/done` + template `session_done.html`.
- [ ] POST `action=end` redirige vers `/done`.
- [ ] `GET /sessions/{id}` pour completed redirige vers `/done`.
- [ ] Recap affiche header, résumé, liste par exo (avec substitutions et added), CTA Synthèse / Historique / Rouvrir.
- [ ] `Rouvrir` bascule DB puis redirect `/sessions/{id}` (éditable).
- [ ] Dispatch cardio : pour `template.kind='cardio'`, recap affiche durée/BPM/calories au lieu de la table exo.
- [ ] Aucun JS ajouté.

---

## 13. Lotissement recommandé

### Option A — Monolithique (un seul build)
Livre les trois axes en une fois. Durée estimée : 3-4 jours de build dense. Risque de régression plus élevé, tests plus lourds à écrire.

### Option B — Trois builds séquentiels (recommandé)
- **Sb_R1 — Substitution graph enrichment** (2 jours). Livre l'Axe 1. Rétro-compatible, aucun risque sur le flow séance. Pas de migration Alembic nécessaire (enrichissement JSON catalogue + rules QA uniquement).
- **Sb_R2 — Added exercise** (2 jours). Livre l'Axe 2. **Nécessite 1 migration Alembic** (colonne `SessionExercise.origin`). UX + analytics.
- **Sb_R3 — Session terminal state** (1-1,5 jour). Livre l'Axe 3. Consomme Sb_R2 pour afficher added dans le recap. Aucune migration Alembic (ajout de route + template uniquement).

**Budget migrations** — le chantier R_T3SX génère **une seule migration Alembic au total** (Sb_R2), **conditionnelle** au périmètre livré : si Sb_R2 est reporté ou retiré, le chantier passe sans aucune migration. Cette propriété vaut confirmation au moment du plan de build, pas avant.

**Recommandation : Option B.** Chaque sous-livrable est déployable et validable indépendamment. Le feedback terrain après Sb_R1 peut ajuster Sb_R2 (ex. si la couverture atteinte suffit au terrain, on peut temporiser Sb_R2). Sb_R3 bouclerait l'expérience utilisateur.

### Ordre recommandé et dépendances explicites

**Priorité 1** — **Sb_R3** (terminal state). Standalone, ROI perçu immédiat, aucune dépendance aux autres axes.
**Priorité 2** — **Sb_R1** (substitution enrichment). Attaque directe du pain-point terrain, rétro-compatible.
**Priorité 3** — **Sb_R2** (added). Structurant, mais **dépend de Sb_R1 par cohérence taxonomique forte**.

| Build | Dépend de | Bloque |
|---|---|---|
| **Sb_R3** (terminal state) | Rien de nouveau (consomme schéma existant) | Rien — standalone. Peut enrichir son recap a posteriori quand Sb_R2 livre. |
| **Sb_R1** (subst enrichment) | QA catalog infra (existe) | **Sb_R2 (dépendance de cohérence taxonomique forte)** — le select d'ajout de Sb_R2 s'appuie sur la classification canon + taxonomie familles d'équipement (§5.2) introduite par Sb_R1. Livrer Sb_R2 sans Sb_R1 obligerait à dupliquer ou ré-inventer cette taxonomie, créant une divergence entre "noms substituables" et "noms ajoutables". **Sb_R1 doit précéder Sb_R2.** |
| **Sb_R2** (added) | Sb_R1 (classification canon + taxonomie familles partagée) | Sb_04 (analytics alignment a besoin de `origin` pour distinguer les timelines). |
| **Sb_04** (history & analytics alignment) | Sb_R1 + Sb_R2 + Sb_R3 | Déblocage de la phase S4+. |

### Arbitrage si une seule fenêtre de build est disponible

- **Sb_R3** → effet produit le plus immédiat (clôture perçue).
- **Sb_R1** → le graphe devient utile en salle (plus de retour en note libre).
- **Sb_R2** seul **n'est pas recommandé** — voir la dépendance taxonomique ci-dessus.

---

## 14. DO NOT BUILD

- Reordonnancement drag-and-drop d'exercices en séance.
- Insertion d'added en milieu de séance (position arbitraire).
- Suppression d'un added depuis l'UI séance (via admin seulement).
- Création d'exercice libre (hors canon catalogue).
- Célébration / confetti / son / animation en fin de séance.
- Recommandation ML de substitution ou d'ajout.
- Analytics "fréquence des added" ou "ratio de substitution" en V1.
- Notion d'exercice personnel / favori à ajouter en un clic (cf. phase 3 catalog governance).
- Entité `Exercise` canonique en DB (toujours reporté, cohérent avec Sx_03).

---

## 15. Questions ouvertes (à trancher avant ou en début de build)

1. **Preset de schéma de sets pour added** — 4 presets suffisent-ils (3x 8-12, 3x 10-15, 4x 6-10, 2x AMRAP) ou faut-il un 5e ? À valider lors de la maquette Sb_R2.
2. **Badge famille d'équipement visible dans l'exercise card** pendant la séance (pas seulement dans le select) — utile ou bruit ? Recommandation : pas en V1, évaluer au retour terrain.
3. **Cardio + added** — peut-on ajouter un exo strength à une séance cardio ? Recommandation : non, bloquer côté server (`template.kind=strength` requis pour afficher la zone d'ajout). Simple, explicite, cohérent.
4. **Persistance du choix d'ajout favori** — si un utilisateur ajoute toujours le même finisher, peut-on lui proposer en premier ? Hors périmètre R_T3SX, candidat à phase 2 du catalog governance.

---

## 16. Références

- `docs/strategy/SPIGNOS_EXERCISE_SUBSTITUTION_GRAPH_SPEC.md`
- `docs/strategy/SPIGNOS_EXERCISE_FEEDBACK_RATIONALIZATION.md`
- `docs/strategy/SPIGNOS_MOBILE_EXERCISE_ENTRY_UX.md`
- `docs/strategy/SPIGNOS_EXERCISE_SYSTEM_ROADMAP.md`
- `docs/strategy/SPIGNOS_EXERCISE_SYSTEM_CONSOLIDATION_SPEC.md`
- `docs/strategy/SPIGNOS_SCORING_RULES_V1.md`
- `docs/strategy/SPIGNOS_CATALOG_GOVERNANCE.md`
- `data/reference_split.json` (v2026-04-14.v8)
- `app/models/session.py`, `app/services/substitution.py`, `app/routers/sessions.py`
- `app/templates/session_detail.html`

---

**Fin de spec.**
