# SPRINT Sb_ZONE_RECOVERY_ESTIMATE_01 — Estimation de récupération par zone (RAPPORT)

**Base canonique :** `79a993b` · **Branche :** `sb/zone-recovery-estimate-01` · **Tier :**
**SHARED_CODE** (`check_scope`) — l'agrégateur existant est modifié. **Full sweep exécuté**.
**Autorité de spec :** `Sx_RECOVERY_READINESS_01_SPEC.md` §2.3, §5.3, §11, §12bis.
**Tranche 4/5 de la file P0.4.** **Dépend de** `Sb_TRAINING_STATE_AGGREGATOR_01`.
**0 migration · 0 table · 0 colonne · 0 UI · 0 modif `recommendation.py`/`behavioral.py` ·
0 décision · 0 texte utilisateur.**

## 1. OQ-2 appliquée — la règle temporelle vit dans le code, versionnée

La décision opérateur du §12bis est appliquée à la lettre : **pas de colonne
`BodyZone.recovery_hours`, aucune migration**. Une durée de récupération n'est pas une propriété
anatomique intrinsèque — elle dépend de la charge appliquée, de l'historique et de l'individu — donc
elle appartient à une **politique versionnable et remplaçable**, pas au schéma.

`RecoveryPolicy` est délibérément mince : `version`, `target_hours()`, `estimate()`. **Elle ne
possède aucune arithmétique** — un test lit le corps des deux méthodes et échoue si un opérateur
arithmétique y apparaît. Les deux délèguent au contrat canonique. C'est une **couture nommée**, pas
une formule.

La constante héritée est **lue** via `recovery_target_hours` (import différé vers
`recommendation.py`). Lire est autorisé ; modifier ne l'est pas — un test vérifie que
`recommendation.py` ne mentionne pas ce module.

**Preuve que la couture fonctionne** : un test définit une `FlatPolicy(version=2)` qui change le
résultat (1.0 → 0.0 sur la même entrée) **sans toucher au module ni au schéma**. C'est exactement le
chemin de remplacement que la spec décrit.

## 2. Aucune physiologie nouvelle

L'estimation est `hours_since_last_load / target_hours`, clampée — **la formule héritée**, atteinte
via `recovery_contract.normalize_training_suitability`. Un test compare l'égalité exacte avec le
normaliseur canonique sur quatre zones.

**Ce que cette tranche ajoute n'est pas une courbe, c'est le traitement correct de l'absence.**
Un test interdit dans le code : `decay`, `half_life`, `exp(`, `math.e`, et les constantes
`0.72`/`72 *`/`48 *`. Planter une courbe exponentielle fait échouer **6 tests**.

## 3. Le fail-open que cette tranche ferme

Le chemin hérité rend une zone jamais vue comme `availability = 1.0` — **parfaitement disponible**.
C'est l'absence de donnée rendue comme la meilleure donnée possible.

Ici : `estimate=None`, `band=UNKNOWN`, `confidence=NONE`, `hours_since_last_load=None`,
`staleness=INSUFFICIENT`, `is_informative=False`. Un utilisateur neuf reçoit **11 zones
explicitement inconnues**, jamais un tuple vide — car une entrée absente serait indiscernable de
« pas calculé », et un consommateur doit pouvoir distinguer « on ne sait pas » de « on n'a pas
regardé ».

**Les divergences avec l'hérité sont énumérées, pas découvertes** (`LEGACY_DIVERGENCES`, 3 entrées,
pinnées par test) :

| Cas | Hérité | Ici |
|---|---|---|
| Zone jamais entraînée | `availability = 1.0` | `None` / `UNKNOWN` / `NONE` |
| Idem, heures | sentinelle `24×365` | `None` — la sentinelle est démasquée |
| Zone avec cardio seul | n'existe pas dans ce chemin | signal contributeur, toujours `UNKNOWN` |

Un test **recalcule la formule héritée** avec la sentinelle et vérifie qu'elle rend bien `1.0` : la
divergence est prouvée, pas affirmée. Le chemin hérité reste en place — `recommendation.py` n'est pas
modifiable et n'est pas modifié — donc les deux coexistent et divergent **exactement** ainsi.

## 4. Cardio : peut baisser la confiance, jamais lever la disponibilité

Une exposition cardio est enregistrée comme `contributing_signal` et **dégrade la confiance d'un
cran**, parce que c'est une preuve que la zone a été chargée d'une manière que ce contrat ne sait pas
situer dans le temps. Elle **n'augmente jamais** l'estimation — un test compare avec et sans cardio à
entrée identique.

Une zone **exposée au cardio mais sans charge de musculation** reste `UNKNOWN` : rien ne place cette
exposition sur une horloge de récupération dans cette tranche, et inventer une décroissance cardio
était explicitement différé en `Sb_CARDIO_FATIGUE_ADAPTER_01`. La `basis` le dit.

C'est l'asymétrie du train : **un signal incertain peut rendre le système plus prudent, jamais plus
agressif.**

## 5. Confiance

| Situation | Confiance |
|---|---|
| Attribution formelle (`db_lookup` / `reviewed_correction`) | **`MEDIUM`** |
| Repli substring pour au moins un exercice | `LOW` |
| Idem + exposition cardio | dégradée d'un cran |
| Zone inconnue / jamais chargée / charge non situable | **`NONE`** |

**`HIGH` est inatteignable** — balayage exhaustif sur 4 durées × 4 combinaisons de chemins × 2 états
cardio. Planter `HIGH` fait échouer **4 tests**.

## 6. OQ-5 — le roll-up macro est de présentation

`build_macro_recovery` groupe par `radar_axis_for_zone` — **la projection canonique de P0.1**, pas
une recopie : un test échoue si `ZONE_TO_RADAR_AXIS` ou `RADAR_AXES` réapparaît ici. Il prend la
**pire zone** via `worst_zone_rollup`, expose la zone limitante, et **dégrade la confiance** si une
zone de l'axe est inconnue.

**`core` n'a pas d'axe radar** : il est **absent du roll-up** tout en restant pleinement présent au
niveau détaillé. Planter un rattachement de `core` à un axe fait échouer un test.

Les décisions d'entraînement utilisent les **zones détaillées** ; la valeur macro ne doit pas devenir
source de vérité d'un planificateur. La docstring le dit et un test le pinne.

## 7. Intégration dans `TrainingState` — la frontière laissée par la tranche 3

`build_training_state` peuple désormais `zone_recovery`, **à partir des preuves déjà rassemblées** :
**zéro requête supplémentaire**, prouvé par un test qui compare le nombre de requêtes avec et sans la
délégation.

**Un piège d'import corrigé, qui aurait été vicieux.** J'avais d'abord écrit la délégation en
**import différé**, en croyant casser un cycle. Il n'y avait pas de cycle : l'estimateur n'a besoin du
type de preuve que sous `TYPE_CHECKING`. Et l'import différé provoquait un vrai défaut sous le
conftest, qui purge `app.*` entre les tests : il résolvait une **seconde génération** de
`recovery_contract`, mettant **deux enums `Confidence` distincts dans un même graphe d'objets**. Les
comparaisons `is` échouaient sur des valeurs pourtant identiques. Diagnostiqué en imprimant les
`id()` des classes plutôt qu'en changeant l'assertion en `==`, ce qui aurait masqué la cause.

Trois tests de la tranche 3 pinnaient la frontière vide. **Retirés, pas affaiblis** — remplacés par
des assertions **plus fortes** : les 11 zones sont toujours présentes, l'agrégateur ne calcule
toujours aucune estimation lui-même (liste d'interdits élargie à `normalize_training_suitability`,
`recovery_target_hours`, `radar_axis_for_zone`), et un utilisateur neuf obtient 11 zones
explicitement inconnues au lieu d'un tuple vide.

## 8. Robustesse temporelle

`_hours_between` aligne le `started_at` **naïf** que SQLite rend sur le fuseau de `now` — la
convention réelle du dépôt, dont les colonnes sont des `DateTime` sans fuseau. Un test vérifie que
les chemins naïf et aware donnent le même résultat.

**Une charge dans le futur rend `None`**, pas un écart négatif : un décalage d'horloge ne doit pas
devenir le signal de fatigue le plus fort possible. Planter `abs(delta)` fait échouer un test.

## 9. Vérifications locales

| Contrôle | Résultat |
|---|---|
| Tests dédiés `test_zone_recovery.py` | **44 passés** |
| Agrégateur (tranche 3, dont 3 tests retirés en assertions plus fortes) | **62 passés** |
| Broad sweep ciblé (16 fichiers : contrat · cardio · readiness · behavioral · reco ×2 · fatigue P0.2 · BodyZone P0.3 · zones P0.1 · scoring · dashboard · profil · substitution · contrat taxonomie) | **665 passés** |
| **Full sweep parallélisé** | **3528 passés, 0 échec** en 3:44 |
| ruff | **clean** |
| Budget ruff | **543 ≤ 548** — **neutre** |
| `check_spec_protocol` | **PASS** |

**Sur le tier.** `check_scope` dit **SHARED_CODE** parce que `training_state.py` est modifié. Aucun
autre module d'`app/` n'importe `training_state` ni `zone_recovery` — vérifié — donc le rayon reste
confiné à la paire ; **le full sweep est néanmoins exécuté**, la tranche précédente ayant montré
qu'un défaut peut se cacher dans l'interaction plutôt que dans le module.

**Pré-scan Sonar avant push** : `S1192`, `S9073`, `S1244` → **NONE** sur les deux modules.

## 10. Six garanties prouvées mordantes par plantation

| Violation plantée | Résultat |
|---|---|
| Zone jamais entraînée rendue « parfaitement disponible » | **CAUGHT** — 7 failed |
| Le cardio multiplie l'estimation par 1,2 | **CAUGHT** — 1 failed |
| Une courbe exponentielle s'installe dans la politique | **CAUGHT** — 6 failed |
| `core` rattaché à l'axe `lower` | **CAUGHT** — 1 failed |
| Une charge future lue comme « vient de s'entraîner » | **CAUGHT** — 1 failed |
| `Confidence.HIGH` devient atteignable | **CAUGHT** — 4 failed |

## 11. Interdits tenus

`recommendation.py` **lu, jamais modifié** (pinné) · `behavioral.py` non touché · modèles ·
migrations · UI · templates : aucun touché. **0 nouvelle taxonomie de zone** (`canonical_zone_codes`
lit `ZONE_LABELS`) · **0 recopie de la projection P0.1** · **0 décision, 0 ranking, 0 texte
utilisateur** · `TrainingState` toujours **sans score global** · `FatigueSignal` toujours **sans
agrégat**. Pas de force-push, pas de rebase, pas de squash, pas de merge `--admin`, `AGENTS.md` non
touché. **`Sb_RECOVERY_EXPLAINER_01` n'est pas ouvert.**

## Verdict

**Livré.** Les 11 zones canoniques portent désormais une **estimation** — bande, confiance, base,
signaux contributeurs, dernière charge datée — construite sur la formule héritée, sans une seule
courbe inventée, et branchée dans `TrainingState` pour **zéro requête de plus**.

Le fail-open que la spec désignait depuis le début est fermé : une zone jamais vue n'est plus
« parfaitement disponible », elle est **inconnue**, et l'écart avec le chemin hérité est énuméré et
prouvé plutôt que découvert plus tard.

Le piège qui aurait coûté le plus cher n'était pas dans la physiologie mais dans les imports : un
import différé inutile mettait deux générations du même enum dans un seul graphe d'objets. Il est
retiré, et la raison est écrite dans le code pour que personne ne le réintroduise « pour casser un
cycle » qui n'existe pas.

Statut : `Sb_ZONE_RECOVERY_ESTIMATE_01 PR GREEN / MERGE PENDING` — puis merge permanent autorisé.
