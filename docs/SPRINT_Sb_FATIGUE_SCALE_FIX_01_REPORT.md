# SPRINT Sb_FATIGUE_SCALE_FIX_01 — Frontière d'échelle de fatigue (RAPPORT)

**Base canonique :** `d9d78b1` · **Branche :** `sb/fatigue-scale-fix-01` · **Tier :**
**SHARED_CODE** (`check_scope`), traité **avec full sweep local** — voir §5.
**Autorité de spec :** `docs/strategy/Sx_AUREN_ORCHESTRATOR_01_GAP_CONSOLIDATION_SPEC.md` **§P0.2**
(constat d'audit §C.0-B). **P0.2 du train `AUREN_P0_CORRECTNESS`.**
**0 migration · 0 écriture DB · `recommendation.py` NON MODIFIÉ · `behavioral.py` NON MODIFIÉ.**

## 1. Brainstorming / Options / Risques / Choix retenu (`CLAUDE.md §3`)

### Le défaut, vérifié dans le code actif

Le producteur `behavioral.compute_behavioral_state` rend `fatigue_score` sur une échelle
**0–100** (`_GLOBAL_STATE_FATIGUE = {"fatigued": 80, "flat": 50, "good": 20}`).
`recommendation.py:894` le recopie **tel quel** dans `context["fatigue_score"]`.
Le lecteur `recommendation_explainer._fatigue_reason` le comparait à **0.7** et **0.2**, comme
s'il était sur 0–1.

Conséquences, toutes vérifiées par exécution :

| Valeur réelle | Ce que l'utilisateur lisait |
|---|---|
| 20 (« bonne forme ») | « Niveau de fatigue **élevé** » |
| 50 (défaut « plat ») | « Niveau de fatigue **élevé** » |
| 80 (« fatigué ») | « Niveau de fatigue **élevé** » |

La branche haute était **quasi toujours** sélectionnée et la branche basse
(« bon moment pour pousser ») **inatteignable** — `behavioral` ne peut pas produire ≤ 0,2.

### Un troisième défaut, plus grave, découvert au préflight

Une seule valeur pouvait tomber dans la fenêtre basse : **`0.0`**. Or `recommendation.py:400-406`
écrit précisément `fatigue_score = 0.0` **quand `compute_behavioral_state` lève une exception** :

```python
except Exception:
    # Si pour une raison x behavioral échoue (tests limités), on dégrade
    # silencieusement — la reco reste fonctionnelle.
    fatigue_score = 0.0
```

Autrement dit, **le seul cas où l'app disait « fatigue basse — bon moment pour pousser » était
celui où elle avait échoué à calculer la fatigue**. C'est exactement le *fail-open* silencieux
que la spec demande de supprimer. Le vérifier n'a pas été un raisonnement : le test
`test_failure_sentinel_does_not_become_fresh` **échoue** sur l'ancien code (§4).

### La contrainte dure et ce qu'elle impose

`recommendation.py` est **non modifiable** (§P0.2, contrainte permanente de la roadmap). Le
correctif ne peut donc pas se faire à la source, et l'information « ceci est un échec, pas une
mesure » est détruite **à l'intérieur** d'un fichier interdit. Il fallait la **reconstruire** en
aval, sans deviner.

### Options considérées

| # | Option | Verdict |
|---|---|---|
| A | Multiplier les seuils par 100 (`>= 70`, `<= 20`) | **Rejetée.** Corrige le symptôme, laisse l'échelle implicite (rien ne dit *pourquoi* 70), et laisse `0.0` passer en « frais ». La spec exige une conversion **explicite, bornée, nommée, testée**. |
| B | Modifier `behavioral.py` pour produire 0–1 | **Rejetée.** Interdit par la spec, et casserait `recommendation.FATIGUE_HIGH_THRESHOLD = 70`, `profile.html` (`"%.0f"`) et tout l'historique des lectures. |
| C | Modifier `recommendation.py` pour distinguer l'échec | **INTERDIT** — contrainte dure. Aurait été la correction la plus directe ; sa non-disponibilité est précisément ce qui motive l'option D. |
| D | **Helper de normalisation pur, nommé, à la frontière du consommateur** | **Retenue.** |

### Ce qui rend la reconstruction rigoureuse plutôt que devinée

Le point clé : **`0.0` n'est pas une valeur que `behavioral` peut produire**, et c'est
démontrable, pas supposé.

```
compute_session_fatigue = (global_state + concentration) / 2
  global_state  ∈ {80, 50, 20}, défaut 50   → min 20
  concentration ∈ {70, 40, 10}, défaut 40   → min 10
  ⇒ minimum (20 + 10) / 2 = 15
compute_weighted_fatigue = combinaison convexe (poids sommant à 1)
  ⇒ ne peut pas sortir de [15, 75]
historique vide                              ⇒ 50 (le défaut « plat »)
```

Le plancher productible est donc **15,0**. Une valeur strictement inférieure **ne vient pas de
`behavioral`** : c'est la sentinelle d'échec de `recommendation.py`. La distinguer ne demande
aucune modification du fichier interdit — seulement de savoir lire son producteur.

**Ce plancher est *dérivé par un test*, pas codé en dur** : `test_producible_floor_is_derived_from_behavioral_not_guessed`
recalcule `(min(gs) + min(co)) / 2` à partir des dictionnaires réels de `behavioral`. Si
quelqu'un change un ancrage, le test tombe. Le nombre 15 ne peut pas dériver en silence.

### Pourquoi la borne est volontairement asymétrique

Le helper rejette ce qui est **sous** le plancher, mais **pas** ce qui dépasse le plafond
productible (75) tout en restant ≤ 100. Ce n'est pas une inattention :

- Refuser une valeur basse invérifiable évite de dire « tu es frais, pousse » à quelqu'un dont on
  n'a pas su calculer l'état. **On refuse d'inventer une bonne nouvelle.**
- Refuser une valeur haute invérifiable ferait taire un avertissement de prudence. Au pire,
  l'utilisateur est invité à lever le pied sur une lecture qu'on ne peut pas pleinement garantir.
  **On ne supprime pas une mauvaise nouvelle.**

C'est la seule direction où deviner peut nuire. L'asymétrie est documentée dans la docstring.

### Pourquoi 0,7 et 0,2 ne sont pas des nombres inventés

- **`FATIGUE_HIGH = 0.7`** ⟺ 70/100 ⟺ **`recommendation.FATIGUE_HIGH_THRESHOLD`**. Après
  normalisation, l'explainer dit « fatigue élevée » **exactement quand le moteur de
  recommandation lui-même filtre sur la fatigue élevée**. Pinné par un test qui importe les deux.
- **`FATIGUE_LOW = 0.2`** ⟺ 20/100 ⟺ **`_GLOBAL_STATE_FATIGUE["good"]`**. Dire « fatigue basse »
  signifie donc précisément « l'athlète s'est déclaré en bonne forme ». Pinné également.

Aucun seuil nouveau n'est introduit ; les deux sont ancrés dans du code existant.

### Risques et traitement

| Risque | Traitement |
|---|---|
| Le texte visible change pour tous les utilisateurs | **C'est l'objectif.** Avant, « fatigue élevée » s'affichait quel que soit l'état réel. |
| Un vrai 0 de fatigue serait masqué | Impossible : `behavioral` ne descend pas sous 15. Prouvé par test sur **toutes** les combinaisons des vocabulaires fermés, clés inconnues incluses. |
| `True` lu comme 0,01 → « frais » | `bool` est un sous-type de `int` : rejeté explicitement, avec un test qui rappelle pourquoi. |
| NaN traversant les comparaisons | Rejeté (`value != value`). |
| Les tests existants pinnaient la mauvaise échelle | **Corrigés, pas supprimés** — voir §3. |

**Aucune correction n'a exigé de toucher `recommendation.py`** → la condition de STOP de la spec
**n'a pas été atteinte**.

## 2. Ce qui est livré

`app/services/recommendation_explainer.py`, additif :

- `FATIGUE_RAW_SCALE_MAX = 100.0` — l'échelle du producteur, énoncée.
- `FATIGUE_RAW_MIN_PRODUCIBLE = 15.0` — le plancher dérivé, commenté avec sa démonstration.
- `FATIGUE_HIGH = 0.7` / `FATIGUE_LOW = 0.2` — bandes normalisées, ancrées (voir §1).
- `normalize_fatigue_score(raw) -> float | None` — **pure**, explicite, bornée, nommée, testée.
  `None` signifie « pas de lecture exploitable » ; l'appelant **se tait** au lieu d'inventer une
  bande.
- `_fatigue_reason` passe par le helper. C'est le **seul** changement de comportement du module.

**Contrat du wrapper respecté** (docstring du module, lignes 12-20) : `recommendation.py` n'est
ni touché ni ré-exécuté ; la règle est **sautée** quand la donnée manque, ce que le contrat
autorise explicitement (« if a field is missing/None we either skip the rule or surface an
explicit "Non déductible" »). Les phrases restent déterministes.

## 3. Tests existants corrigés — pas affaiblis

`tests/test_recommendation_explainer.py` passait `0.9` / `0.1` / `0.5` / `0.9`, c'est-à-dire
qu'il **verrouillait l'erreur** : il « prouvait » que la lecture 0–1 fonctionnait.

Les **assertions étaient justes** (haute → phrase de fatigue élevée, basse → phrase de fatigue
basse, moyenne → silence) ; seules les **entrées** étaient sur la mauvaise échelle. Elles passent
donc à `90` / `20` / `50` / `90`, l'échelle réelle du producteur. **Aucune assertion n'est
retirée, affaiblie ni marquée `xfail`.** Un commentaire dans le fichier explique la correction et
renvoie vers la table complète.

## 4. Tests — `tests/test_fatigue_scale.py`, 46 tests

**Preuve que les tests mordent.** Le consommateur défectueux a été **temporairement restauré** et
la suite relancée : **10 échecs**, dont
`test_failure_sentinel_does_not_become_fresh` — c'est-à-dire que l'ancien code rendait bien
« bon moment pour pousser » sur la sentinelle d'échec. Correctif rétabli : **69/69** sur les deux
fichiers.

Couverture :

- **Plage réelle du producteur** — plancher **dérivé** des dicts de `behavioral` ; toutes les
  combinaisons de `compute_session_fatigue` (clés fermées + `None` + clé inconnue) restent dans
  la bande ; `compute_weighted_fatigue` (combinaison convexe) n'en sort pas ; historique vide
  → 50 ; **0 non productible**.
- **Alignement des seuils** — `FATIGUE_HIGH × 100 == recommendation.FATIGUE_HIGH_THRESHOLD` ;
  `FATIGUE_LOW × 100 == _GLOBAL_STATE_FATIGUE["good"]`.
- **Table de conversion exigée par la spec** — `0 → None` · `15 → 0.15` · `20 → 0.2` ·
  `50 → 0.5` · `70 → 0.7` · `80 → 0.8` · `100 → 1.0`.
- **Entrées inexploitables** — `None`, `"80"`, `""`, `[]`, `{}`, `()`, `object()`, `True`,
  `False`, `NaN`, `±inf`, `-1`, `-0.1`, `100.1`, `101`, `1000` → toutes `None`.
- **Sortie bornée** à [0, 1].
- **Message rendu** — le défaut 50 **ne devient pas** fatigue élevée · la bande moyenne
  (40/50/60/69.9) n'émet **aucune** phrase extrême · la bande haute (70/75/80/100) émet la phrase
  de séance légère · la bande basse est **atteignable depuis des valeurs réellement productibles**
  (15, 20, et `compute_session_fatigue(good, high)` calculé en direct).
- **Anti-fail-open** — la sentinelle `0.0` est silencieuse et **différente** de la phrase basse ;
  missing/malformé jamais « frais » ; clé absente silencieuse.
- **Bout en bout via `explain_recommendation`** — fatigué → phrase haute · frais → phrase basse ·
  défaut → silence · sentinelle → silence.
- **Non-régression des règles voisines** — cold start, phrase, fallback, confiance, cap à 3
  raisons, dégradation gracieuse sur charge utile cassée.

Conforme à la mémoire Sonar S5863 : aucune assertion de la forme `assert f(x) == f(x)`.

## 5. Vérifications locales

`check_scope` : **SHARED_CODE**. **Full sweep local exécuté** malgré la clause « recommandé si
doute » : le changement modifie un **texte visible par l'utilisateur** sur une surface d'accueil,
et le tier ne mesure pas ce risque-là.

| Contrôle | Résultat |
|---|---|
| Nouveaux tests ciblés | **46 passés** |
| Explainer (tests corrigés) | **24 passés** |
| Broad sweep ciblé — explainer · behavioral (3 fichiers) · reco (5 fichiers) · zone-freshness · calibration · home/hero/payload · launcher · dedup | **221 passés** |
| Full sweep parallélisé | **3108 passés** en 2:20 |
| ruff (fichiers touchés + neuf) | **clean** |
| Budget ruff | **543 ≤ 548** — strictement **neutre** vs la canonique |
| `check_spec_protocol` | **PASS** |

*Précision : le full sweep a tourné sur 3108 tests, soit 45 des 46 du nouveau fichier — le test
d'ancrage de `FATIGUE_LOW` a été ajouté juste après son lancement. Il est pur (aucune DB, aucun
état partagé) et le fichier complet a été rejoué à 46/46 ; la CI de PR rejouera de toute façon
l'intégralité.*

## 6. Non-régressions et interdits tenus

**Interdits de la spec, tous tenus** : **`recommendation.py` NON MODIFIÉ** (vérifiable au diff :
il n'apparaît pas) · sémantique de production de `behavioral.py` **non redessinée** (fichier non
modifié) · aucune échelle inconnue devinée · aucune dégradation muette vers « frais » ·
sémantiques de repli existantes préservées hors du bug · aucun test affaibli ou supprimé.

**Interdits du train, tous tenus** : pas de force-push, pas de rebase, pas de squash, pas de
merge `--admin`, `AGENTS.md` non touché, aucun flag Body Intelligence modifié, aucun déploiement,
aucune migration.

### 6bis. Finding Sonar traité in-scope (PR #76)

**Gate externe `SonarCloud Code Analysis` en ÉCHEC** au premier passage :
`new_bugs_severity 15 > 9`, une seule issue — **`python:S1764`**, « Correct one of the identical
sub-expressions on both sides of operator `!=` », sur ma garde NaN `if value != value`.

**Sonar a raison, et la règle est utile ici.** `value != value` est l'idiome NaN classique, mais
il est visuellement indistinguable d'une faute de frappe ; un relecteur ne peut pas dire si c'est
intentionnel. Remplacé par **`math.isnan(value)`** : résultat identique, intention explicite.

**La garde reste nécessaire** et n'a pas été simplement supprimée pour verdir la CI : toute
comparaison avec NaN vaut `False`, donc `NaN < 15` et `NaN > 100` sont **tous deux faux** et le
contrôle de plage laisserait NaN passer jusqu'à la division. Vérifié après correction :
`nan → None`, `inf → None`, `-inf → None`, `50 → 0.5`.

*À noter — même famille que la règle `python:S5863` déjà rencontrée sur ce repo (auto-comparaison
dans les tests de déterminisme) : Sonar refuse les expressions dont les deux côtés sont
identiques, en code de production comme en test.*

## Verdict

**Livré.** La frontière d'échelle est désormais **explicite, bornée, nommée et testée**, du côté
consommateur, sans toucher au fichier interdit. Le message de fatigue reflète l'état réel : la
branche « bon moment pour pousser » est **atteignable** depuis de vraies valeurs, le défaut
« plat » **cesse** d'être annoncé comme une fatigue élevée, et un **échec de calcul** ne se
déguise plus en bonne forme.

**Critère d'acceptation de la spec — atteint** : « le message de fatigue reflète l'état réel ;
plus de dégradation muette vers "frais" ».

**Preuve exécutée, pas affirmée** : le consommateur défectueux restauré fait échouer **10** tests,
dont celui de la sentinelle d'échec ; rétabli, **69/69**.

Statut : `Sb_FATIGUE_SCALE_FIX_01 PR GREEN / MERGE PENDING` — puis merge permanent autorisé par
le `GO TRAIN`.
