# `Sb_TRAIN_A_ENVIRONMENT_ACTIVATION_01` — la frontière d'activation

**Branche** : `sb/train-a-environment-activation` sur canonique `fb0a66e`
**Nature** : `RUNTIME_FLOW` / décision servie partagée. **Pas** un sprint de
catalogue, **pas** une refonte d'écran.
**Migration** : **aucune**, et c'est démontré au `§3`.

---

## 1. Deux faits mesurés qui gouvernent tout le sprint

Mesurés **avant** d'écrire une ligne, sur la base semée comme le produit la
sème.

### 1.1 — Sur un environnement `NULL`, 2 gabarits sur 18 sont `SERVABLE`

| environnement | `SERVABLE` | `UNKNOWN` | `NOT_FEASIBLE` |
|---|---|---|---|
| **`NULL`** — tous les utilisateurs actuels | **2** (`liss-only`, `no-equipment-full-body`) | 16 | 0 |
| `[]` — vide explicite | 2 | 7 | 9 |

Appliquer le `§1.A` — *« only proven `SERVABLE` templates may win »* — à un
utilisateur `NULL` lui **retirerait 16 gabarits sur 18** et l'enfermerait
dans une séance de cardio ou de poids du corps. Ce serait la régression la
plus brutale de l'histoire du produit.

**La directive porte sa propre levée** : le `§1` s'ouvre sur *« For the
user's **effective declared environment** »*. `NULL` n'est pas une
déclaration — c'est l'absence de déclaration, et le modèle le dit depuis
`TRAIN A` : *« environnement concret non résolu »*. Le `§7` l'exige
d'ailleurs explicitement (*« legacy NULL / unknown environment remains
non-blocking »*), tout comme la porte `G7`.

**Choix retenu, et il n'y en avait pas d'autre de tenable** : la porte
d'environnement ne s'applique **que** lorsque
`available_equipment_items is not None`. Sur `NULL`, le chemin servi est
**identique au bit près** à celui d'aujourd'hui — aucun filtrage, aucune
adaptation, aucune empreinte modifiée.

### 1.2 — Aucune surface n'écrit encore l'environnement concret

Mesuré : `available_equipment_items` n'est écrit par **aucun routeur, aucun
gabarit, aucun service** hors de son propre point d'écriture, qui n'a pas
d'appelant.

**Conséquence dite franchement : cette activation est correctement câblée et
INERTE en production.** Tout utilisateur réel est `NULL`, donc traverse le
chemin hérité. Le `§8` interdit de créer la surface de déclaration
(« DO NOT create Gym Profiles »), et le `§3` demande d'enregistrer la
gestion d'équipement comme suite. C'est donc un fait à consigner, pas un
choix à faire.

Ce que le sprint livre malgré tout, et qui a de la valeur : la frontière
existe, elle est prouvée, et le jour où une surface de déclaration arrive,
**il n'y a rien à concevoir** — seulement à déclarer.

---

## 2. Brainstorming / Options / Risques / Choix retenu (`CLAUDE.md §3`)

### Le graphe d'appel réel, découvert et non supposé

```
GET /            pages._build_reco_context
                      ↓
        advice_memory.recommander(politique="v3", avec_memoire=True)
                      ↓                                  ↑
        recommendation_v3.recommander_v3          empreinte_de_contexte
                      ↓
        recommendation_v3.classer_candidats  →  liste ORDONNÉE complète
                      ↓
                 top + 2 alternatives

POST /sessions   sessions.create_session
                      ↓
        session_builder.instantiate_session(db, tpl, …)
                      ↓
        SessionExercise(exercise_name_snapshot=…)   ← identité PRÉVUE
        SessionExercise.substituted_name            ← identité RÉALISÉE
```

### Où insérer la porte — trois options, une seule tient

| option | ce qu'elle coûte | verdict |
|---|---|---|
| **A** — filtrer dans `advice_memory.recommander` | le dictionnaire n'y porte que **top + 2 alternatives** : si les trois sont infaisables, on rend vide alors qu'un 4ᵉ candidat était servable | **écartée** — filtre une liste déjà tronquée |
| **B** — faire entrer l'équipement dans le scoring de `classer_candidats` | l'équipement deviendrait un **signal de classement**. `TRAIN A` l'a explicitement refusé : la faisabilité n'est pas une préférence, et un score la rendrait négociable | **écartée** |
| **C** — porte **après** `classer_candidats`, **avant** le découpage top/alternatives | un seul endroit du graphe réel où la liste **ordonnée complète** existe | **RETENUE** |

L'option **C** ne touche pas au classement : elle **retire** des candidats
prouvés infaisables et **annote** ceux qui s'adaptent. L'ordre relatif
survivant est inchangé, bit pour bit. Ce n'est pas un second moteur — c'est
un filtre de faisabilité posé sur la sortie du seul moteur servi.

### Risques identifiés, et ce qui les tient

| risque | garde |
|---|---|
| tout filtrer et ne rien servir | `§1.B`/`§1.C` : l'incertitude ne vaut pas impossibilité ; repli hérité préservé |
| régresser tous les utilisateurs actuels | porte inactive sur `NULL` — prouvé par test |
| deux exécutions différentes après rechargement | la matérialisation est **persistée** à la création, jamais recalculée |
| fusionner deux historiques d'exercices | la lignée existante `snapshot` + `substituted_name` est **réutilisée telle quelle** |
| une empreinte qui périme un refus sans raison | l'identité matérielle ignore le matériel qui n'a rien changé |

---

## 3. Pourquoi aucune migration n'est nécessaire

Le `§2` demande de préserver **prévu** et **réalisé**. Le dépôt le fait
déjà, et depuis longtemps :

| champ | rôle |
|---|---|
| `SessionExercise.exercise_name_snapshot` | l'identité **prévue**, figée à la création |
| `SessionExercise.substituted_name` | l'identité **réalisée**, `NULL` si aucune substitution |
| `substitution.actual_exercise_name()` | `substituted_name or exercise_name_snapshot` |

La matérialisation d'équipement écrit **exactement le même champ** que la
substitution manuelle, par le même contrat. Historiquement, une adaptation
d'équipement est donc indistinguable d'une substitution manuelle — et c'est
**voulu** : dans les deux cas le fait est « cet exercice-là a été prévu,
celui-ci a été fait ». Aucune colonne neuve, aucune ambiguïté de schéma,
donc **aucun arrêt dur du `§2`**.

---

## 4. Le point d'activation, dans le graphe réel

`recommendation_v3.recommander_v3`, **entre** `classer_candidats` et le
découpage `top + 2 alternatives`. Un appel, une fonction, un module neuf
sans second moteur :

```
verdicts = classer_candidats(db, user_id, now)      # classement V3 intact
environnement = appliquer(db, user_id, verdicts)    # LA PORTE
verdicts = list(environnement.candidats)            # survivants, même ordre
```

`environment_activation` est le **seul** consommateur de
`environment_resolution`. Il ne rend aucun verdict par lui-même, ne cherche
aucun substitut — la liste autorisée lui est fournie dans l'ordre du moteur
de substitution — et ne rend aucun score. Une garde AST vérifie qu'il
n'a redéfini aucune constante d'état.

### Preuve par mutation, **deux** câblages indépendants

| mutation | gardes rouges |
|---|---|
| la porte rendue inerte dans le chemin servi | **2** — activation et empreinte |
| la matérialisation débranchée de `POST /sessions` | **1** — lignée prévu/réalisé |

Les deux chemins sont séparés **à dessein** : démarrer depuis la
Bibliothèque doit matérialiser l'adaptation même si l'écran d'accueil n'a
jamais été rendu. Chacun a donc sa propre preuve.

---

## 5. Matrice de preuve produit (`§7`)

| environnement | état | gagnant | adaptation | doublons | empreinte env. |
|---|---|---|---|---|---|
| **salle équipée** (25) | `servable` | `push-a` | **1** | 0 | oui |
| **salle privée** (8) | `servable` | `push-a` | **3** | 0 | oui |
| **maison** (5) | `servable` | `no-equipment-full-body` | 0 | 0 | oui |
| **`[]`** | `servable` | `no-equipment-full-body` | 0 | 0 | oui |
| **`NULL`** hérité | — | `push-a` | 0 | 0 | **non** |

Lignée `prévu → réalisé` en salle privée :

```
Chest Press machine                  →  Développé couché haltères
Dips pectoraux (buste penché)        →  Développé incliné haltères 30°
Neutral Grip Shoulder Press machine  →  Shoulder press haltères assis
```

Trois exécutions distinctes, **zéro doublon**, le prescrit conservé partout.

### ⚠ Une conséquence produit que la matrice révèle, et qu'il faut voir

**En salle maison, le gagnant devient `no-equipment-full-body`.** Pas parce
que `push-a` y est impossible — il y est **`UNKNOWN`**. Le `§1.A` exige que
seul le *prouvé* gagne ; le gabarit sans matériel, lui, est
inconditionnellement prouvé. Il gagne donc dès qu'aucun autre ne l'est.

Avec **39 identités encore `UNKNOWN`** dans la clôture, c'est le cas de la
plupart des environnements déclarés modestes. Ce n'est ni un défaut du
résolveur ni une erreur de câblage : c'est l'interaction entre le contenu de
`G4`, la règle du `§1.A` et la **dette de curation restante**. Elle se
résorbe exactement dans la mesure où les 39 inconnues se ferment — et les
7 alias vérifiés de `TRAIN A` en fermeraient 7 d'un mot.

C'est une décision produit, pas une décision de résolveur, et elle vous
revient.

---

## 6. `G8` — un état implémenté et aujourd'hui inatteignable

`NO_SERVABLE_CANDIDATE` est implémenté, testé, rendu. Il est
**structurellement inatteignable** dans le catalogue actuel, pour deux
raisons **cumulées** :

1. `no-equipment-full-body` porte `equipment_requirements = []` et reste
   donc servable dans tout environnement — c'est précisément ce que `G4`
   exigeait ;
2. 39 identités restent `UNKNOWN`, donc les gabarits résolvent en
   `unknown`, et le `§1.B` préserve la liste plutôt que de bloquer.

C'est une **propriété du produit**, pas un défaut : AUREN a toujours quelque
chose à proposer. L'état existera le jour où la curation sera close et où le
catalogue ne portera plus de gabarit inconditionnel.

**Pour l'exposer visuellement**, le labo a réduit le catalogue aux **9
gabarits mesurés `NOT_FEASIBLE`** avec l'environnement de test — il n'a
fabriqué aucun verdict, il a retiré ceux qui n'en étaient pas. Rien de cette
mise en scène n'est livré.

---

## 7. Contrat de livraison UI (`CLAUDE.md §5`)

Un seul gabarit touché — `app/templates/index.html` — et **aucune feuille de
style**.

### 5.1 — exposition préalable

Quatre états rendus en **localhost authentifié**, écran entier, **390 px et
1280 px** : recommandation native sans mention, recommandation adaptée avec
le fait, `NO_SERVABLE_CANDIDATE`, et la Bibliothèque sous environnement
déclaré. **Soumis à l'opérateur avant tout commit ; accepté.**

### 5.2 — relecture du relevé, décision par décision

| décision | verdict |
|---|---|
| **Q5** trois rangs de surface | **RESPECTÉE** — le fait rejoint `cockpit__reasons`, rang 2 informatif ; aucune carte, aucune primitive |
| **Q6** échelle 32/22/15/12 | **RESPECTÉE** — aucun rang typographique introduit |
| **Q7** un seul aplat ambre | **RESPECTÉE** — `DÉMARRER` seul, ou `AJUSTER MON MATÉRIEL` seul |
| **Q8** aucune opacité décorative | **RESPECTÉE** — aucune couleur écrite |
| **Q2** ancre de l'accueil | **NON CONCERNÉE** — les barres de récupération sont intactes |
| **Q4** ligne de série | **NON CONCERNÉE** — la Séance n'est pas touchée |
| **Q1 · Q3** | **NON CONCERNÉES** |
| ordre causal `cause → prescription → action` | **RESPECTÉ**, visible au rendu |

Aucune décision **VIOLÉE**.

### 5.3 — jamais une soustraction seule

Aucune soustraction : le repli générique existant est **conservé** ; l'état
bloqué s'ajoute **avant** lui, sur une condition plus précise.

### 5.4 — toute couleur est un token

Aucune couleur introduite. Les deux états réutilisent `today-home__cta` et
`cockpit__reasons` tels quels.

---

## 8. Non-buts tenus (`§8`)

| interdit | tenu |
|---|---|
| appliquer les 7 alias d'atlas | aucun touché |
| rapprochement approximatif | aucun |
| rendre le contenu poids du corps globalement substituable | `exercise_properties` **intouché**, 69 entrées |
| changer l'équivalence `N1`/`N2`/`N3` | inchangée |
| étendre `pattern_motor` | inchangé |
| dose en temps / planche frontale | aucune |
| refonte Bibliothèque · Accueil · Séance | aucune — un seul bloc de `index.html` |
| Gym Profiles | aucun — l'état bloqué mène à `/plan#declaration`, **qui existe déjà** |
| migration | **aucune** — voir `§3` |
| framework front | aucun |
| seconde politique de recommandation | aucune — un filtre, pas un moteur |

---

## 9. Vérifications

* `check_scope` : `SHARED_CODE`. **Full sweep exécuté quand même** — le `§9`
  de la directive l'exige pour une décision servie, et ce dépôt a déjà payé
  l'excès de confiance dans le classifieur. Verdict sur arbre gelé :
  **`tous les lots sont verts.`** (356 fichiers, aucun sauté)
* `check_spec_protocol` : `OK` — après l'avoir oublié une première fois,
  voir `§10.4`
* **CI de PR : 9/9 verte** · Sonar `OK` — 0 bug, 0 code smell,
  0 vulnérabilité, duplication 0 %, couverture nouveau code **90,3 %**
* `ruff` sur **tous** les fichiers Python du diff : propre. Deux `I001` de ma
  main corrigés — la classe exacte qui a rougi Sonar deux fois. Le `C901` de
  `session_detail` est **préexistant**, vérifié en remisant la tranche
* scan `S9073` par AST : aucun
* **33 gardes neuves**, deux mutations jouées et attrapées
* 118 tests verts sur accueil, recommandation, mémoire et activation

---

## 10. Quatre gardes rouges, et ce qu'elles disaient vraiment

La CI et le sweep local ont trouvé **exactement les mêmes quatre**. Aucune
n'a été affaiblie.

### 10.1 — Une garde qui accusait une COMPARAISON

`test_the_planned_identity_is_never_overwritten` interdisait la sous-chaîne
`"se.exercise_name_snapshot ="` dans le routeur. Or une **comparaison** —
`se.exercise_name_snapshot == prescrit` — la contient.

La matérialisation compare le nom prévu avant d'écrire, précisément **pour
ne pas écrire au mauvais créneau**. Elle s'est donc fait accuser d'écraser
l'identité qu'elle protège.

Réécrite **par AST** : affectation, affectation augmentée, affectation
annotée. Strictement plus précise, jamais plus permissive. Et deux gardes
neuves l'encadrent : l'une plante une vraie réaffectation (elle doit être
vue), l'autre plante la comparaison (elle ne doit pas l'être). C'est la
classe « garde statique qui accuse du code sain », sixième instance
recensée.

### 10.2 — Le cliquet ambre, et pourquoi la ligne monte légitimement

`index.html` passe de **3 à 4** occurrences. Les quatre vivent dans des
**branches Jinja mutuellement exclusives** : recommandation servie, état
bloqué, repli générique. `Q7` prévoit exactement ce cas — *« un gabarit peut
légitimement écrire plusieurs aplats dans des branches mutuellement
exclusives »* — et désigne le **harnais de rendu** comme garde de vérité.

Ce harnais a tranché : **un seul aplat ambre mesuré sur chacun des trois
écrans rendus**. La ligne de base suit la mesure, pas l'inverse.

### 10.3 — Ma propre garde de non-consommation

`test_the_resolution_layer_itself_has_no_consumer` était juste : le
résolveur a désormais **un** consommateur. C'était l'objet de la tranche.
Renommée, et l'égalité reste **stricte** — un second consommateur
échouerait.

### 10.4 — Le protocole de spec

Rapport sans section `Verdict`. **Je n'avais pas lancé
`check_spec_protocol`**, que `check_scope` exigeait pourtant. Faute de
méthode, pas de conception.

---

## 11. Verdict

**Livré.** La frontière d'activation est en place et prouvée : point unique
dans le chemin servi, matérialisation avant `START`, état bloqué nommé,
empreinte environnementale à l'activation causale. **Aucune migration,
aucun second moteur, aucun non-but franchi.**

**Deux réserves, dites franchement.**

L'activation est **inerte en production** tant qu'aucune surface n'écrit
`available_equipment_items` — le `§8` interdisait de la créer ici. La
gestion d'équipement est la suite naturelle, et elle est nommée.

Et le `§1.A`, appliqué à une curation incomplète, **fait gagner le gabarit
sans matériel** dès qu'aucun autre n'est *prouvé* — cas de la plupart des
environnements modestes tant que 39 identités restent `UNKNOWN`. Ce n'est
pas un défaut du résolveur ; c'est une décision produit qui revient à
l'opérateur.

---

## 12. Closeout

| | |
|---|---|
| **PR** | [#264](https://github.com/MFE-DSS/workout-session-tracking/pull/264) |
| **Merge** | `be19736881f367e75f58b5a7e4d6fd456e46f988` |
| **Méthode** | `--merge` avec `--match-head-commit e866476` — pas de squash, pas d'`--admin`, pas de force |
| **CI canonique** | run [`36480604452`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/36480604452) — **7/7 verts** |
| **Sonar (gate de PR, autorité de merge)** | `OK` — 0 bug, 0 code smell, 0 vulnérabilité, duplication 0 %, couverture nouveau code **90,3 %** · **0 issue ouverte sur la PR** |
| **Threads de revue** | 0 |
| **Migration** | aucune |

Les totaux projet (6 bugs, 6 vulnérabilités, 431 code smells, couverture
93,6 %) sont la dette préexistante consignée sous `SONAR-AUDIT-01`. Le zéro
**cadré sur la PR** prouve que cette tranche n'y a rien ajouté ; je ne
confonds pas les deux mesures.

### Gate visuel — accepté par l'opérateur

Quatre états rendus en localhost authentifié, écran entier, 390 et 1280 px,
**soumis avant tout commit** conformément au `CLAUDE.md §5.1`, puis
acceptés. Un seul gabarit touché, **aucune feuille de style**.

### Ce que ce merge ne fait PAS

| | vérifié |
|---|---|
| filtre servi sur environnement **non déclaré** | **inerte** — garde dédiée |
| 7 alias d'atlas en attente | non appliqués |
| graphe de substitution | non élargi — `exercise_properties` à **69** |
| `pattern_motor` | inchangé |
| Bibliothèque · Accueil · Séance | non redessinés |
| Gym Profiles | aucun — l'état bloqué mène à `/plan#declaration`, existant |
| migration | **aucune** |
| seconde politique de recommandation | **aucune** |

### Registre et roadmap

**Aucune mise à jour requise.** Le protocole appliqué à ce train fait le
closeout en annexe du rapport de sprint : les closeouts `456519c` (#259),
`337a4a0` (#261) et `fb0a66e` (#263) n'ont touché que leur propre rapport,
vérifié sur leur diff.

### Ce qui reste ouvert, et qui n'est pas de mon ressort

1. **Aucune surface n'écrit `available_equipment_items`** — l'activation est
   inerte en production tant que la gestion d'équipement n'existe pas. Le
   `§8` interdisait de la créer dans cette tranche.
2. **Les 39 identités `UNKNOWN`** font gagner le gabarit sans matériel dès
   qu'aucun autre n'est *prouvé*. Les 7 alias vérifiés de `TRAIN A` en
   fermeraient 7 d'un mot.
3. **`NO_SERVABLE_CANDIDATE` restera inatteignable** tant qu'un gabarit
   inconditionnellement servable existe — c'est une propriété voulue.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
