# SPRINT Sb_ADAPTIVE_REPLAN_EFFECTIVE_VOLUME_01 — replan et effectif (RAPPORT)

**Train :** `AUREN_EFFECTIVE_VOLUME_COMPLETION_01`, tranche 4/4 — **clôture** ·
**Base canonique :** `214da78` · **Branche :** `sb/adaptive-replan-effective-volume-01`

---

## 1. Le contrat

**La replanification mute des séries PHYSIQUES.** La conséquence effective est
**dérivée** de `SetContributionPolicy`, jamais écrite à la main et jamais mutée
directement.

Concrètement : `effective_impact` est calculé en appliquant la politique
partagée aux occurrences **avant** puis **après** report. Le ricochet sur les
zones secondaires en tombe tout seul — aucune règle « la presse donne du
triceps » n'existe dans ce service, et une garde structurelle interdit toute
arithmétique d'effectif (`* 0.5`, `// 2`, affectation directe).

Mesuré : reporter les **12 séries physiques** de `pecs` retire **12 séries
effectives** de `pecs` **et 6** de `triceps` — dérivées, pas déclarées.

---

## 2. Une exposition secondaire n'est pas une contre-indication

Une récupération estimée limitante ne retire que les occurrences dont la zone
est la **cible principale**. Un composé qui la sollicite en **secondaire** reste
programmé.

`biceps` limitant ⇒ les trois tirages restent au plan. Retirer le travail de dos
pour cela priverait `lats` de son travail primaire à cause d'une exposition que
le modèle n'a jamais mesurée comme telle. L'estimation de récupération est une
**preuve comptable**, pas une prédiction de blessure.

Consigné dans le code : `SECONDARY_EXPOSURE_IS_NOT_A_CONTRAINDICATION`.

### La garde ne prouvait rien — la plantation l'a montré

Mon premier test vérifiait la **liste des deltas** : `lats` n'y figure pas quand
`biceps` est limitant. **Cette liste est correcte par construction** — elle est
filtrée sur `zone_code`. Le test n'éprouvait donc jamais le filtre réellement à
risque, celui des occurrences survivantes.

Plantation : retirer toute occurrence *impliquant* la zone limitante, même en
secondaire ⇒ **17 tests passaient toujours**. Quatrième garde non porteuse de
la session.

Corrigé : le test compare désormais l'**impact effectif** de `lats` avant et
après. Re-plantation ⇒ il tombe (`0 == 24`). La garde est prouvée.

---

## 3. L'asymétrie tient

Preuve favorable ⇒ aucune replanification, `effective_impact` vide.
Aucune zone ne **gagne** jamais d'unités effectives lors d'un replan.
`Confidence.NONE` ne fabrique toujours rien.
La limite plan↔séance sur les séances écourtées est **inchangée**.

---

## 4. Dogfood déterministe — priorité « Bras » déclarée

| Cadence | Statut | Physique | Effectif | Identités | Occurrences | Exercices/séance | ≥ low | ≥ base | Pire | Médiane | INC |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2 | `PARTIAL` | 48 | 54 | 11 | 12 | 6, 6 | 1 | 0 | 0,29 | 0,50 | 0 |
| 3 | `PARTIAL` | 72 | 84 | 11 | 18 | 6×3 | 3 | 1 | 0,50 | 0,57 | 0 |
| 4 | `PARTIAL` | 96 | 114 | 11 | 24 | 6×4 | 5 | 2 | 0,57 | 0,86 | 1 |
| 5 | `PARTIAL` | 120 | 142 | 11 | 30 | 6×5 | **9** | 5 | 0,86 | **1,00** | 1 |

**`PREVENTABLE = 0` partout.** Chaîne complète validée à chaque cadence :
brouillon créé, aperçu qualité calculé, `validate_draft` accepté, **aucun
programme publié**.

Deux propriétés vérifiées en base : les `rep_targets` persistés égalent la dose
**physique** (jamais l'effectif), et une identité répétée dans plusieurs séances
**survit** à la matérialisation sans être fusionnée.

**Priorité déclarée matériellement représentée** à toutes les cadences —
`biceps` et `triceps` ont chacun un exercice réel, pas seulement un compteur
rempli par du crédit indirect. C'est la porte de sortie que le défaut de la
tranche 3 avait failli laisser passer.

### Candidat de release

**Cadence 4.** La forme de séance est identique partout (6 exercices / 24
séries) ; ce qui change est l'engagement hebdomadaire. Quatre séances est
l'engagement réaliste le plus courant, pour une couverture médiane de 0,86 et
cinq zones à leur borne basse.

**Cadence 5 reste l'option optimale en couverture** (9 zones sur 11, médiane
1,00) et mérite d'être proposée à qui déclare cette disponibilité — mais la
choisir *par défaut* prescrirait une fréquence que l'utilisateur n'a pas
demandée.

---

## 5. Tests — 17 dédiés + 6 de dogfood

Effectif dérivé et non écrit · concordance exacte avec la politique partagée ·
delta resté physique · garde structurelle contre toute arithmétique d'effectif ·
secondaire non contre-indicant (**plantation vérifiée**) · contre-épreuve
primaire · asymétrie préservée · `Confidence.NONE` stérile · limite séance
écourtée inchangée · déterminisme aux quatre cadences.

## Verdict

La replanification parle enfin la même langue que le reste de la chaîne : elle
mute du **physique**, et l'effet sur les zones — secondaires comprises — est
**déduit** d'une politique unique.

Le point qui compte : une zone limitante ne peut pas faire disparaître le
travail primaire d'une autre. `biceps` fatigués ne suppriment pas le dos.

Et, pour la quatrième fois de cette session, une garde que je croyais solide ne
tenait rien : elle vérifiait une liste correcte par construction plutôt que le
filtre réellement à risque. Seule la plantation l'a révélé.

---

## Closeout (post-merge)

| | |
|---|---|
| PR | **#100** — `--merge --match-head-commit`, **sans** squash / `--admin` / force |
| Build | `514b56b` — aucun correctif de code |
| Merge | **`466a6b0`** |
| Gate Sonar | **`OK`** — couverture du neuf **100 %**, 0 smell, 0 bug, 0 vulnérabilité |
| Threads / Gitar | **0 / 0** |
| Tests | full sweep local **4 296** |

### Capacité CI — **HEALTHY**

| | Shard A | Shard B |
|---|---|---|
| min MemAvailable | **5 168 Mo** | **5 097 Mo** |
| min SwapFree | 3 071 Mo — **jamais entamé** | 3 071 Mo — **jamais entamé** |

Quatrième tranche consécutive au-dessus de 5 Go sur les deux shards.

### Incident CI — un test instable, hors périmètre

Premier passage **rouge** sur `pytest shard 1` :

```
tests/test_ci_runner_stability.py::TestFixtureTempCleanup::test_a_failing_test_still_cleans_up
assert 3 <= 2
```

**Sans rapport avec cette tranche** — qui touche `adaptive_replan.py` et deux
fichiers de tests neufs, rien du nettoyage temporaire. Le test passe en local
(60/60) et passait dans le full sweep de 4 296.

**Cause : le test échantillonne un état GLOBAL sous exécution parallèle.** Il
compte *tous* les répertoires temporaires portant un préfixe partagé, avant puis
après un pytest imbriqué. Sous xdist, le fixture `client` d'un **autre worker**
peut en créer un entre les deux relevés, et `after > before` sans que rien ne
soit cassé.

**Aucun code n'a été touché** : ce test appartient à
`Sb_OPS_CI_RUNNER_STABILITY_01`, et modifier la garde d'un autre sprint pour
verdir sa propre CI est précisément ce que le contrat interdit. Seuls les jobs
échoués ont été relancés — **verts au second passage**, ce qui confirme le
caractère non déterministe.

**Correctif minimal proposé, non appliqué** : relever l'**ensemble** des chemins
plutôt qu'un compte, et vérifier qu'aucun répertoire *imputable au run imbriqué*
ne survit. Remonté comme finding hors périmètre : tant qu'il reste, ce test
produira des rouges aléatoires.
