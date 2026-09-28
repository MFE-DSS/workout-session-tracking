# `TRAIN A` — L'autorité canonique de récupération

**Statut** : `MERGÉ` · PR #257 · merge `3476e1a`
**Branche** : `sb/train-a-recovery-authority` sur canonique `bd02c4f`
**Tier `check_scope`** : `SHARED_CODE` — **full sweep exécuté quand même**
**Migration** : aucune. **`recommendation.py` n'est pas touché d'une ligne.**

---

## 1. Le défaut

Le chemin servi calculait sa propre récupération : un ratio 0–1 dérivé de
`RECOVERY_HOURS_TARGET`. Son défaut tenait en une ligne — une zone **jamais
entraînée** y valait `1.0`, donc « pleinement récupérée ». Une affirmation
physiologique que rien n'appuyait.

Le contrat canonique dit `UNKNOWN / confiance NONE` sur ce même cas.

Mesuré, 66 comparaisons zone×corpus : **62 % de désaccord, dont 40 sur 41
de cette seule cause.**

`REC-CP0b` avait pourtant nommé la doctrine et introduit
`AVAILABILITY_INCONNUE = 0.5` — mais il ne l'applique qu'à l'observation
**partielle**. Une zone jamais entraînée n'a jamais été couverte. La
doctrine avait été appliquée à l'une des deux formes d'inconnu.

---

## 2. Ce qui ne change pas, et c'est le cœur

L'arbitrage a tranché : « sans charge observée » est **NON LIMITANT**.

| | rang | preuve positive |
|---|---|---|
| `LIKELY_AVAILABLE` | non limitant | **oui** |
| `NO_OBSERVED_LOAD` | non limitant | **non** |
| `PARTIALLY_RECOVERED` | partiel | — |
| `LIKELY_FATIGUED` | limitant | — |

Le critère de récupération répond à « **ai-je une preuve qui doit LIMITER
ce candidat ?** ». L'absence d'observation n'en est pas une. Elle n'est pas
non plus une preuve de fraîcheur — et l'explication ne doit jamais faire
comme si.

### Mesuré avant d'écrire une ligne

| politique | gagnants changés |
|---|---|
| pénaliser le « sans charge observée » | **9 / 10** |
| migrer en le gardant non limitant | **0 / 60** |

Pénaliser aurait été une **réécriture de politique**, pas une migration
d'autorité. L'opérateur l'a rejetée sur cette base.

---

## 3. Où vit le calcul, et pourquoi pas ailleurs

**Deux gardes de gel ont rougi sur ma première écriture, et elles avaient
raison.**

Cette écriture ajoutait deux champs à `Signals` et faisait importer
`zone_recovery` par `recommendation.py`.

* `test_recommendation_py_is_not_modified` interdit au moteur hérité de
  connaître le contrat canonique : la dépendance va du contrat VERS le
  moteur, jamais l'inverse, sinon les deux modèles se referment l'un sur
  l'autre.
* `test_the_recommendation_engine_may_be_corrected_but_never_grow` épingle
  les champs de `Signals` — le contrat d'ENTRÉE du scoring, **partagé avec
  V2**. Y ajouter des champs que seul V3 lit aurait fait grossir un
  contrat commun pour un besoin qui ne l'est pas.

Les deux pointaient la même chose : **c'est la politique SERVIE qui migre,
pas le socle de signaux.** Le calcul vit donc dans
`recommendation_v3.py`, dans un objet `RecuperationCanonique` à portée de
requête. `recommendation.py` est revenu à l'identique.

C'est une meilleure conception que la mienne, et ce sont les gardes qui
l'ont trouvée.

---

## 4. L'adaptateur est catégoriel, et le type l'interdit d'être autre chose

```
NON_LIMITANT · PARTIEL · LIMITANT        ← trois chaînes, pas trois nombres
```

Traduire la bande canonique en flottant pour réutiliser l'ancienne clé
aurait reconduit le mensonge d'origine sous une couche de respectabilité :
`UNKNOWN → 1.0` est exactement le défaut qu'on corrige. Une garde vérifie
qu'aucune valeur de l'adaptateur n'est un nombre.

**Repli** : carte absente — chaîne d'évidence indisponible — ⇒ `PARTIELLE`,
le neutre. Jamais `RECUPEREE` : une panne ne se lit pas comme une
autorisation.

---

## 5. Parité — contre le code réel, pas contre une simulation

Deux arbres, même base, **horloge figée et partagée** (sans quoi l'écart
serait imputé à la migration alors qu'il viendrait du temps qui passe).
60 historiques : neuf, un passage à 1/3/8/30 jours pour dix gabarits,
quinze couples, semaine dense, tout ancien, répétition pure, cardio seul.

| mesure | résultat |
|---|---|
| **gagnant changé** | **0 / 60** |
| ordre complet identique | 38 / 60 |
| premier rang divergent | min 3 · max 11 |
| **divergence dans les 3 rangs SERVIS** | **1 / 60** |

La seule divergence visible : « semaine dense », rang 3,
`pull-b` → `legs-b`. Le produit sert le gagnant plus deux alternatives ;
les 21 autres divergences sont au rang 5 ou plus bas et n'atteignent
jamais l'écran.

⚠ J'ai d'abord rapporté « 22 ordres changés » sans le rang de divergence.
Ce chiffre ne disait pas si la politique avait bougé pour l'utilisateur ou
seulement dans la queue du classement. Instrumenter la profondeur a
transformé un chiffre alarmant en un fait précis.

---

## 6. L'explication ne ment plus par omission de preuve

`FACTEUR_RECUPERATION` (« zones récupérées ») exige désormais une **preuve
positive**, pas seulement un bon rang. Sur une zone jamais chargée, le rang
est bon et le produit ne sait rien : le silence est la seule sortie
honnête, et il est explicitement autorisé.

Une garde bout-en-bout vérifie qu'un **utilisateur neuf** ne s'entend pas
dire qu'il est récupéré.

---

## 7. Gardes — 12 neuves, toutes vues rouges

`tests/test_train_a_autorite_recuperation.py`

| mutation | attrapée par |
|---|---|
| la phrase ne vérifie plus la preuve | `sans_charge_observee_ne_dit_jamais_zones_recuperees` |
| l'inconnu devient limitant | `sans_charge_observee_est_non_limitant` · `n_est_pas_une_preuve` |

Une garde vérifie aussi que la carte est **réellement peuplée** : sans
elle, un `RecuperationCanonique` vide laisserait toutes les autres passer
sur le repli neutre.

---

## 8. Trois gardes existantes migrées, aucune affaiblie

| garde | traitement |
|---|---|
| `test_v3_n_est_reference_que_par_le_banc_et_la_composition` | **le dispositif a fonctionné** — un nouveau lecteur de V3 doit se déclarer, la garde a rougi, je m'y suis inscrit avec le motif |
| `test_une_zone_a_plat_n_est_pas_compensee_par_une_zone_fraiche` | construisait un `Signals` avec des ratios que la politique ne lit plus. Laissée telle quelle, elle serait passée **sur le repli neutre sans jamais exercer sa règle** — verte et muette. Migrée sur la nouvelle entrée, règle identique au mot près |
| `test_la_nouveaute_parle_quand_elle_a_reellement_departage` | son double supposait que la récupération parle toujours. Sans preuve, le double n'avait plus aucun facteur gagnant et « jamais fait » s'énonçait légitimement par la clause de dernier recours. Une preuve positive lui rend le cas qu'il voulait tester |

---

## 9. Vérifications

* **Sweep local complet : `tous les lots sont verts.`** — tier
  `SHARED_CODE`, full sweep non requis, exécuté quand même : la tranche
  touche le moteur de décision servi
* 739 tests ciblés verts sur le périmètre recommandation / récupération
* ruff propre sur les trois fichiers touchés
* parité rejouée **après** chaque correction, y compris la dernière

---

## 10. Ce que cette tranche n'ouvre pas

Aucun filtre d'équipement, aucun vocabulaire de capacités, aucun contenu
poids du corps. La piste ENVIRONNEMENT reste bloquée en amont : le `§10`
exige un vocabulaire **dérivé d'un audit sourcé**, et le `§12` interdit
l'inférence par le nom. Trois items sont déjà hors d'atteinte du
vocabulaire actuel — roulette abdominale, relevé suspendu, barre EZ.

`sessions_per_week`, `focus_priorities`, morphologie et retours par
exercice restent hors du classement.

---

## 11. Closeout

| | |
|---|---|
| **PR** | [#257](https://github.com/MFE-DSS/workout-session-tracking/pull/257) |
| **Merge** | `3476e1ac9d69692c1a23b6b90c89da1bec02c59f` |
| **Méthode** | `--merge` avec `--match-head-commit 2659d6e` — pas de squash, pas de `--admin`, pas de force |
| **CI canonique** | run [`36399789712`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/36399789712) — **7/7 verts** |
| **Sonar** | `OK` — 0 code smell, 0 bug, couverture nouveau code **94,4 %** |
| **Threads de revue** | 0 non résolu |
| **Migration** | aucune |

### Les neuf findings Sonar, et la cause qui s'est répétée

Premier passage : `new_code_smells_severity = 15` pour un seuil de 14.
Neuf MAJOR, **tous dans le fichier de gardes neuf** — huit
`external_ruff:I001` et un `python:S9073`.

**La cause racine est celle de `UI-CP7.5`, à l'identique** : `ruff` lancé
sur les fichiers applicatifs que je venais de modifier, pas sur le
**diff**. Le fichier de tests neuf n'a jamais été scanné en local. Le
commit `4fc3535` avait déjà consigné la commande correcte plusieurs
tranches plus tôt.

Elle est désormais appliquée, avec en plus un scan `S9073` par AST :

```bash
ruff check $(git diff --name-only <base>...HEAD -- '*.py')
```

### Ce que la tranche laisse derrière elle

| résidu | destination |
|---|---|
| granularité des capacités câble — une ou cinq | **arbitrage opérateur** |
| 35 exercices sans source de prérequis | curation sourcée (`E2`) |
| dimension `equipment_requirements` | `E3`, après gel du vocabulaire |
| contenu de force sans matériel | `E4`, 5 mouvements ACE sourcés, 0 intégré |
| activation du filtre dur | `G1`…`G8`, dernière porte |

La piste RÉCUPÉRATION est **close**. La piste ENVIRONNEMENT continue.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
