# SPRINT Sb_MORPHO_PROFILE_RUNTIME_01 — de vraies mesures dans le moteur (RAPPORT)

**Train :** `AUREN_MORPHO_RUNTIME_FOUNDATION_01`, tranche 1/3 ·
**Base canonique :** `64a6e75` · **Branche :** `sb/morpho-profile-runtime-01`

---

## 1. Brainstorming / Options / Risques / Choix retenu

L'audit de `Sx_MORPHO_CAPTURE_01_SPEC` annonçait deux écrivains concurrents. Le
code en a révélé **un troisième désaccord que la spec n'avait pas vu**, et c'est
lui qui a dicté la forme du sprint.

### Ce que la spec disait, et ce que le code dit

La spec §4.4 écrit que la colonne héritée `calf_cm` « vieillit sans être
écrite ». **C'est faux au SHA de départ.** Les deux surfaces n'écrivent pas les
mêmes colonnes :

| | `/profile` (écrivain A) | `/body` (écrivain B, canonique) |
|---|---|---|
| Liste de champs | `MEASUREMENT_FIELDS` (10) | `BODY_MEASUREMENT_FIELDS` (12) |
| Mollet | **`calf_cm` hérité** | `calf_cm_left` / `calf_cm_right` |
| Épaules | absent | `shoulder_width_cm` |
| Date | **choisie par l'utilisateur** | `now()` imposé |
| Hors bornes | **silencieusement mis à `NULL`** | `ValueError` explicite |
| Consentement | aucun | `has_active_consent` obligatoire |

Le formulaire `/profile` est donc **la raison pour laquelle la colonne héritée
est encore alimentée aujourd'hui**. Le rapport prime sur la spec quand les deux
divergent : c'est le code qui a tranché.

### Options examinées

**A — déléguer tel quel.** `parse_and_validate` ignore les clés inconnues :
`calf_cm` posté serait **silencieusement perdu**. Une perte de donnée déguisée
en refactor. **Rejetée.**

**B — ajouter `calf_cm` à la liste blanche canonique.** Contredit frontalement
la consigne « ne pas écrire la colonne héritée depuis l'écrivain canonique », et
fige une colonne que le modèle documente comme dépréciée depuis Sb_Body_01.
**Rejetée.**

**C — mapper le champ unique vers les deux côtés.** Fabriquerait deux mesures à
partir d'une seule. **Rejetée** — c'est l'invention que le train interdit.

**D — rendre le formulaire depuis la liste blanche canonique.** *(retenue)* Le
formulaire devient la projection du contrat de l'unique écrivain. Le mollet
passe en gauche/droite, cohérent avec le bras et la cuisse **déjà latéralisés
dans ce même formulaire** — le mollet en était la seule anomalie.

### Risques acceptés, et ce qui les compense

| Risque | Décision |
|---|---|
| La rétro-datation aurait disparu (`create_measurement` imposait `now()`) | paramètre `measured_at` **ajouté** à l'écrivain canonique. Sans lui, la délégation aurait effacé une capacité produit sans le dire. |
| Les valeurs hors bornes deviennent des **erreurs** au lieu de disparaître | assumé, c'est la règle §6 contre la troncature silencieuse. Un état d'erreur a été ajouté au formulaire. |
| Les graphiques du mollet hérité pourraient disparaître | **capture et affichage séparés** : `capture_fields` (canonique) pilote le formulaire, `MEASUREMENT_FIELDS` (avec l'hérité) pilote les courbes. L'historique reste lisible. |

### Question ouverte, délibérément non tranchée

`/body` exige un consentement actif pour écrire ; `/profile` non. La délégation
unifie **les sémantiques d'écriture**, pas la politique d'autorisation :
importer la barrière de consentement sur `/profile` bloquerait des utilisateurs
qui saisissent des mesures aujourd'hui, et la retirer de `/body` affaiblirait
une garantie. Le statu quo est conservé et la question est **signalée**, pas
résolue en passant — elle relève du produit.

---

## 2. Ce qui est livré

**Migration `r9s4m0n1p12`** (`q8r3l9m0o11 → r9s4m0n1p12`) : `ADD COLUMN
wingspan_cm FLOAT NULL`. Pas de `server_default` — un défaut matérialiserait une
valeur sur **chaque ligne existante**, c'est-à-dire exactement le backfill
interdit. Idempotente, downgrade symétrique.

**Écrivain unique.** `POST /profile/measurements` délègue à
`body_profile.create_measurement`. Trois comportements changent volontairement :
append-only, bornes appliquées, colonne héritée non écrite.

**Adaptateur `build_morphology_facts(db, user_id, *, as_of=None)`.** Chaque fait
est résolu **indépendamment**, du plus récent au plus ancien, et porte sa
provenance : `field`, `value`, `source`, `basis`, `measurement_id`,
`measured_at`.

---

## 3. Les trois décisions qui portent le reste

**L'ape index n'est ni stocké ni pré-calculé.** L'adaptateur transmet
`wingspan_cm` et `height_cm` bruts, avec `ape_index_cm=None` ; c'est le moteur
qui soustrait. Sans envergure : pas d'ape index, pas de valeur de repli, pas de
zéro. Une envergure estimée depuis la taille produirait un ape index nul **par
construction pour tout le monde** — une invention présentée comme une mesure.

**Un profil multi-dates est nommé comme tel.** `profile_kind` vaut `empty`,
`single_measurement` ou `latest_known_facts`. Le troisième cas interdit à un
consommateur de présenter l'assemblage comme « mesures du 12 avril » alors que
le tour de taille vient de mardi et la poitrine du mois dernier.

**Les deux côtés viennent de la même ligne.** Moyenner une cuisse gauche de
mardi avec une droite de janvier fabriquerait une valeur jamais mesurée.
L'adaptateur prend la **ligne la plus récente portant un côté** et réduit à
l'intérieur de celle-ci. Convention versionnée `lateral-mean-v1`, exposée dans
le `basis`.

---

## 4. Preuves

| Preuve | Résultat |
|---|---|
| Tests dédiés | **64** |
| Balayage ciblé (mesures / body / profil / moteur / drift) | **128** |
| Full sweep local | **4 378** |
| Drift Alembic | OK |
| Roundtrip migration (upgrade → downgrade → upgrade) | 44 objets, schéma identique |
| Patterns de migration | aucun motif dangereux |
| Snapshot de schéma | régénéré, diff **d'une seule ligne** |
| Budget ruff | 536 ≤ 548 |

### Plantations — deux gardes testées, **une était morte**

**(a) Moyenne inter-dates.** En reconnectant `_lateral` pour prendre le dernier
gauche et le dernier droit indépendamment, le test tombe sur la valeur
fabriquée exacte (`55.0` au lieu de `60.0`). Garde vivante.

**(b) Colonne héritée — garde morte, corrigée.** En remettant `calf_cm` dans la
liste blanche canonique, **le fichier restait entièrement vert**. La cause : le
test ne postait que `calf_cm_left/right`, donc la colonne héritée n'était jamais
candidate à l'écriture et l'assertion tenait quel que soit le contenu de la
liste. Le test **poste désormais `calf_cm`** et vérifie qu'il n'est pas
persisté ; une garde structurelle sur la liste blanche a été ajoutée à côté.
Replantée : les deux tombent.

> Note honnête : deux faux signaux m'ont coûté du temps et méritent d'être
> consignés. `python scripts/check_alembic_drift.py` place `scripts/` sur
> `sys.path` et **résout `app` vers l'autre worktree** — il annonçait une dérive
> inexistante. La forme documentée `python -m scripts.check_alembic_drift` dit
> `OK`. Et mes tests importaient `app.*` au niveau module, alors que la fixture
> `client` purge `sys.modules` : le symptôme (`no such table`) ressemble à une
> migration cassée et n'en est pas.

---

## 5. Isolation du planificateur

Le train gèle la sortie du planificateur. La preuve est d'abord **structurelle** :
`build_weekly_plan(preferences, budget, pool)` ne prend **ni `db` ni `user_id`**
— il ne peut pas atteindre une mesure. Un test vérifie cette signature.

S'y ajoutent : un scan des **8 modules gelés** (aucun ne mentionne
`morphology_runtime` ni `morphology_profile`), et une vérification
comportementale — mêmes préférences, empreinte de plan et budget identiques
avant et après l'insertion d'un jeu complet de faits morphologiques. Cette
dernière est une ceinture par-dessus les bretelles : la pureté du planificateur
la rend structurellement acquise, elle attrapera surtout une régression future.

`recommendation.py` n'est pas modifié. Aucun fichier gelé n'apparaît au diff.

---

## 6. Limites énoncées

- **`observations = ()`** — aucune surface ne capture le vocabulaire
  d'observations, et en inventer depuis des nombres serait l'inférence
  interdite. Le moteur produit donc des descripteurs à **confiance
  structurellement réduite**. À savoir avant de brancher un planificateur
  dessus, pas après.
- **`shoulder_width_cm`** reste capturé et non consommé (OQ-1 de la spec).
- **Consentement `/profile` vs `/body`** — divergence conservée, signalée.
- La taille reste sur `User` : la modifier rétroactivement change l'ape index
  calculé pour des mesures anciennes (conséquence assumée, spec §4.2).

## Verdict

Le moteur pur reçoit enfin de vraies mesures, **sans qu'une ligne de sa science
ait bougé**. La capture porte une seule autorité d'écriture, l'envergure est
mesurée ou absente, et un profil assemblé sur plusieurs dates le dit.

Le vrai risque du sprint n'était pas l'ajout de colonne : c'était la délégation,
qui pouvait faire disparaître silencieusement la rétro-datation et la saisie du
mollet. Les deux ont été vues avant d'écrire, et traitées explicitement.

**La morphologie n'influence pas le programme** — et c'est vérifié, pas promis.
