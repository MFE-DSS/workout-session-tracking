# SPRINT Sb_CARDIO_FATIGUE_ADAPTER_01 — Adaptateur cardio borné (RAPPORT)

**Base canonique :** `55958de` · **Branche :** `sb/cardio-fatigue-adapter-01` · **Tier :**
**ISOLATED** (`check_scope`), traité **avec broad sweep ciblé** — le module est un contrat
sémantique partagé et l'adaptateur remplace une implémentation déjà publiée.
**Autorité de spec :** `Sx_RECOVERY_READINESS_01_SPEC.md` **§5** et **§11**, décision **OQ-4**.
**Tranche 2/5 de la file P0.4.** **Dépendance :** `Sb_RECOVERY_CONTRACT_01` (mergée, canonique verte).
**0 migration · 0 champ persisté · 0 UI · 0 modif `recommendation.py` · 0 agrégation `TrainingState`
· 0 décision de planification.**

## 1. Phase 0 — l'hypothèse de préflight était fausse, et la correction change la conception

`Sb_RECOVERY_CONTRACT_01` avait justifié le report des coefficients en écrivant que le vocabulaire
`cardio_machine_type` était **inconnu** parce que la colonne est du texte libre. **C'était
imprécis, et vous aviez raison de le corriger.**

| | |
|---|---|
| **Vocabulaire d'UI** | `session_detail.html` expose un `<select>` **fermé** : `""` · `velo` · `marche` · `rameur` · `elliptique` · `autre` |
| **Vocabulaire de stockage** | `String(32)`, et — constat **nouveau de cet audit** — `routers/sessions.py:628` n'applique **aucune allow-list** (`clean_str(max_length=32)`). La permissivité est donc réelle, mais elle vient de l'**endpoint**, pas de la saisie |

La distinction n'est pas cosmétique : elle dit exactement sur quelle garantie l'adaptateur a le
droit de s'appuyer — **la plus faible**. Un `<select>` fermé n'empêche pas un POST forgé, et ne dit
rien des lignes historiques.

### Valeurs réellement observées

| Source | Observé |
|---|---|
| `<select>` `session_detail.html` | `velo`, `marche`, `rameur`, `elliptique`, `autre` (+ option vide) |
| `tests/test_cardio_capture.py:39` | `velo` |
| **`tests/test_session_done.py:183`** | **`stairmaster`** — une valeur **hors liste réellement présente dans ce dépôt** |
| Base de dev locale `var/workout.db` (lecture seule) | **7 séances · `cardio_machine_type` NULL partout · 0 durée · 0 bpm** |
| `var/workout.db.backup_20260413` | antérieure à la colonne (`no such column`) |
| **Production** | **NON AUDITÉE** |

**L'audit production n'a pas pu être fait, et je ne le maquille pas.** Cette session n'a ni
identifiants ni accès DB au VPS — même limite qu'en `Sb_OPS_DEPLOY_SAFETY_01`, où le smoke test a
dû rester non authentifié pour cette raison exacte. **Les fixtures ne valent pas la production.**
Si des lignes historiques portent d'autres valeurs, elles tombent en `UNKNOWN` : dégradation
prévue et testée, pas surprise.

**Aucun alias n'est encodé** — aucun n'est attesté. `velo` est stocké sans accent ; `vélo` n'existe
qu'en libellé d'affichage. Un test échoue si quelqu'un ajoute `vélo`/`bike`/`treadmill` : inventer
des orthographes jamais observées est la fabrication que le §5 interdit.

## 2. Décisions sémantiques — ce que le nombre est, et n'est pas

### 2.1 La durée est la seule entrée quantitative défendable

```
value = clamp_unit(duration_min / CARDIO_DURATION_REFERENCE_MINUTES)
```

Une règle **nommée, monotone, bornée**. Pas de non-linéarité cachée, pas de coefficient
pseudo-scientifique. Un test vérifie l'égalité exacte `duration / référence` sur cinq points.

**La référence vient du catalogue, pas de moi.** Les deux templates cardio de
`reference_split.json` prescrivent **« 20-30 min LISS »** (`liss-only`, `liss-abs`) : 30 est le haut
de la plage prescrite par le produit lui-même. Une séance à la prescription vaut **une unité
complète d'exposition**, et aller plus loin ne peut pas valoir plus d'une. Un test relit le
catalogue et échoue si la prescription change.

> **C'est une constante de normalisation produit, pas un seuil biologique de fatigue.**
> Rien de physiologique ne se produit à 30 minutes.

`coach_inference.CARDIO_LOW_MIN_PER_WEEK` (90) a été examinée puis **écartée** : plancher de volume
**hebdomadaire** issu d'une recommandation de santé publique — mauvaise granularité pour un proxy
**par séance**.

Le nombre est donc explicitement un **proxy opérationnel d'exposition cardio**. Pas un pourcentage
de fatigue physiologique, pas une récupération, pas une mesure de charge interne.

### 2.2 La BPM ne peut pas agrandir la valeur

AUREN n'a **aucun ancrage cardiaque individuel** : ni FCmax mesurée, ni FC de repos, ni réserve,
ni seuil ventilatoire ou lactique. 130 bpm n'est pas comparable entre deux personnes.

**Le catalogue le prouve** : les deux templates LISS prescrivent la **même** cible
« 120-130 bpm » à **tout le monde**. Une lecture dans cette bande **ne distingue personne**. Un
test relit cette prescription.

La BPM est donc de la **preuve que la séance a été enregistrée plus complètement** : elle alimente
la `basis` et peut faire monter la confiance de `LOW` à `MEDIUM` sur une modalité spécifique.
**Elle ne change jamais la magnitude** — pinné en balayant 60→220 bpm à durée constante.

### 2.3 Les calories machine ne sont pas lues

Elles **ne sont même pas un paramètre**. Le produit les étiquette « indicatif » dans le formulaire,
elles viennent d'estimateurs machine de calibration inconnue, et ne sont pas une mesure de charge
interne individualisée. Elles restent affichage et export.

## 3. Vocabulaire et distribution par zone

`CardioModality` : `velo` · `marche` · `rameur` · `elliptique` · `autre` · `unknown`.
Normalisation **trim + casse uniquement**. Valeur non vide non reconnue → `UNKNOWN`, **valeur brute
renvoyée** pour que la `basis` puisse la nommer, confiance réduite — **jamais une contribution nulle
silencieuse**. Champ vide → **aucune modalité fabriquée**.

### La table modalité → zones

**C'est une heuristique produit.** Pas d'EMG, pas d'activation mesurée, pas de fatigue tissulaire,
pas de récupération. Codes `BodyZone` canoniques uniquement, aucune taxonomie nouvelle.

| Modalité | Primaire | Secondaire | Raison |
|---|---|---|---|
| `velo` | `quads`, `posterior` | `calves` | travail cyclique bas du corps assis, aucune charge haute |
| `marche` | `quads`, `posterior` | `calves` | marche inclinée ; mollets sollicités par la pente |
| `rameur` | `quads`, `posterior`, `lats`, `upper_back` | `biceps` | **la seule modalité mixte** : poussée jambes + chaîne de tirage |
| `elliptique` | `quads`, `posterior` | `calves` | **volontairement bas du corps seul** — la machine a des bras mobiles, mais **rien dans les données ne dit s'ils ont été utilisés** ; ajouter des zones hautes serait inventer un fait sur la séance |
| `autre` / `unknown` | — | — | **aucune zone fabriquée** ; estimation générique + confiance réduite |

Les trois modalités bas-du-corps partagent **une** distribution nommée une seule fois : elles
diffèrent réellement dans la façon de charger les jambes, mais **rien dans les données capturées ne
les distingue**, et prétendre le contraire serait une précision que nous n'avons pas.

Poids : `CARDIO_PRIMARY_ZONE_WEIGHT = 1.0`, `CARDIO_SECONDARY_ZONE_WEIGHT = 0.5` — **poids relatifs
internes au signal cardio**, pas des pourcentages de quoi que ce soit, et pas une affirmation sur
l'activation musculaire.

## 4. Matrice de confiance

| Entrées | Confiance | Valeur |
|---|---|---|
| Modalité **spécifique** + durée + BPM utilisable | **`MEDIUM`** | `duration/30` clampée |
| Modalité spécifique + durée, pas de BPM | `LOW` | idem |
| Durée seule (aucune modalité) | `LOW` | idem |
| Durée + BPM, aucune modalité | `LOW` | idem |
| **`autre`** + durée + BPM | `LOW` | idem |
| **Hors liste** (`stairmaster`) + durée + BPM | `LOW` | idem |
| Pas de durée utilisable | **`NONE`** | **`None`** |

**`Confidence.HIGH` est inatteignable** — vérifié par balayage exhaustif de 8 × 5 × 5 combinaisons.
Aucune combinaison des champs actuels n'observe la charge interne.

**Une modalité inconnue ne peut pas être remontée à `MEDIUM` par la BPM** : la BPM prouve un
enregistrement plus complet, pas une calibration. `autre` est une valeur de catalogue légitime mais
ne dit **pas** ce qui a bougé — elle reste donc plafonnée à `LOW` et sans distribution.

## 5. Ce que cette tranche n'implémente pas

**Aucune décroissance temporelle.** Cette tranche décrit l'exposition d'**une** séance. *Quand*
cette exposition cesse de compter appartient à `Sb_ZONE_RECOVERY_ESTIMATE_01`. Un test parcourt le
**corps** de la fonction (docstring exclue par AST) et échoue sur `decay`, `half_life`, `elapsed`,
`hours_since`, `started_at`.

Cardio reste une **composante observable séparée** : pas d'agrégat pondéré sur `FatigueSignal`, pas
de score global sur `TrainingState`, aucune logique de décision. Pinné.

## 6. Tests — `tests/test_cardio_fatigue_adapter.py`, 88 tests

**Cinq garanties centrales, prouvées mordantes par plantation de violations réelles :**

| Violation plantée | Résultat |
|---|---|
| La BPM > 120 multiplie la valeur par 1,3 | **CAUGHT** — 1 failed |
| Une modalité inconnue atteint `MEDIUM` | **CAUGHT** — 3 failed |
| `HIGH` devient atteignable | **CAUGHT** — 4 failed |
| L'elliptique gagne un `lats` fabriqué | **CAUGHT** — 2 failed |
| `autre` reçoit une distribution inventée | **CAUGHT** — 2 failed |

Couverture : vocabulaire (5 valeurs UI + vide + `None` + non-str + `stairmaster` + hors-liste +
anti-alias) · **test qui relit le `<select>` du template** et échoue si une option est ajoutée sans
que l'adaptateur la connaisse · durée (`None`/0/négatif/NaN/inf/bool → inexploitable ; monotonie ;
référence exacte ; saturation ; règle exacte ; bornes) · BPM (seule → rien ; 60→220 à durée
constante → valeur identique ; absente → `LOW` quand même ; présente → `MEDIUM` sur modalité
spécifique) · calories (**pas un paramètre** ; `TypeError` si passées ; absentes du corps ; 5
valeurs de calories → **un seul résultat**) · confiance (matrice de 9 cas + `HIGH` inatteignable
exhaustif) · zones (codes canoniques seuls ; pas de taxonomie ; primaire ≠ secondaire ;
déterminisme ; poids ordonnés) · périmètre (pas de décroissance, pas d'agrégat, pas de score, pas
d'ORM) · formulation (garde canonique des termes interdits).

### Deux tests hérités mis à jour — retraite, pas affaiblissement

`test_recovery_contract.py` pinnait le **placeholder** de la tranche précédente
(`test_cardio_estimate_is_declared_but_computes_nothing_yet`). Ce placeholder était **explicitement
transitoire** : sa docstring disait « aucun coefficient inventé **avant** audit du vocabulaire
stocké ». **L'audit a eu lieu**, donc l'attente est **retirée** et remplacée par le contrat réel —
les garanties durables qu'elle protégeait (plafond de confiance, contenu de la `basis`) sont pinnées
**plus fort**, ici et dans le fichier dédié. Le test de `basis` est réécrit pour le nouveau contenu.

## 7. Vérifications locales

| Contrôle | Résultat |
|---|---|
| Tests dédiés | **88 passés** |
| Broad sweep ciblé (adaptateur · contrat · capture cardio · scoring cardio · recap · session done · coach · profil · fatigue P0.2 · explainer · export ×3 · timeline · zones P0.1 · BodyZone P0.3) | **495 passés** |
| ruff (fichiers touchés + neuf) | **clean** |
| Budget ruff | **543 ≤ 548** — **neutre** |
| `check_spec_protocol` | **PASS** |
| `check_scope` | **ISOLATED** — full sweep local non requis, non lancé |

**Pré-scan Sonar effectué avant le push**, en appliquant la leçon de la PR #79 : un balayage AST
local a trouvé **3 littéraux dupliqués ≥ 3 fois** dans le module (`quads`, `posterior`, `calves` —
`python:S1192`, CRITICAL). Résolus en nommant la distribution bas-du-corps partagée, ce qui rend
aussi le code plus juste. Zéro assertion composite (`S9073`), zéro égalité de flottants (`S1244`).
Le fichier de test conserve des littéraux répétés : la PR #79 a **prouvé empiriquement** que
`S1192` ne se déclenche pas sur les fichiers de test de ce dépôt (son fichier de test en portait
davantage et Sonar n'a rapporté que `S9073`).

## 8. Interdits tenus

**Périmètre** : 0 migration · 0 champ persisté · 0 modèle · 0 template · 0 UI ·
`recommendation.py` **non modifié** · `behavioral.py` **non modifié** · 0 agrégation
`TrainingState` · 0 décision de planification · `Sb_TRAINING_STATE_AGGREGATOR_01` **non ouvert**.

**Consommateurs cardio existants inchangés** : export, recap de séance, minutes cardio du profil,
inférence coach, capture cardio — **aucune modification**, 495 tests le confirment.

**Livraison** : pas de force-push, pas de rebase, pas de squash, pas de merge `--admin`,
`AGENTS.md` non touché.

## Verdict

**Livré.** L'adaptateur cardio existe, il est déterministe et borné, et il ne prétend rien que les
données ne portent : **une** entrée quantitative (la durée), **une** référence prise dans le
catalogue produit, **zéro** influence des calories, **zéro** influence de la BPM sur la magnitude,
et une table de zones assez grossière pour être défendable sans ergomètre.

La correction que vous avez apportée au préflight a **changé la conception** : savoir que l'UI est
déjà fermée mais que l'endpoint ne valide rien m'a dit exactement sur quelle garantie m'appuyer, et
m'a fait chercher — puis trouver — une valeur hors liste réellement présente dans le dépôt
(`stairmaster`) plutôt que d'en imaginer.

Le seul point que je ne peux pas clore : **la base de production n'a pas été auditée**, faute
d'accès. C'est dit, pas contourné.

Statut : `Sb_CARDIO_FATIGUE_ADAPTER_01 PR GREEN / MERGE PENDING` — puis merge permanent autorisé.
**`Sb_TRAINING_STATE_AGGREGATOR_01` n'est pas ouvert.**
