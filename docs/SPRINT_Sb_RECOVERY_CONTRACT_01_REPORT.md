# SPRINT Sb_RECOVERY_CONTRACT_01 — Types purs et normalizers (RAPPORT)

**Base canonique :** `5f66280` · **Branche :** `sb/recovery-contract-01` · **Tier :**
**ISOLATED** (`check_scope`) — traité avec **broad sweep ciblé** en plus des tests ciblés, parce
que ce module crée une **API sémantique partagée future** et lit trois services existants.
**Autorité de spec :** `docs/strategy/Sx_RECOVERY_READINESS_01_SPEC.md`, décisions opérateur
**OQ-1..OQ-7 résolues au §12bis**. **Tranche 1/5 de la file P0.4.**
**0 DB · 0 ORM · 0 routeur · 0 template · 0 UI · 0 moteur de décision · 0 migration.**

## 1. Décisions opérateur enregistrées dans le repo

Les sept arbitrages sont consignés dans la spec canonique en **§12bis**, ajouté **sans réécrire**
le §12 : l'audit d'origine et les défauts proposés restent lisibles tels qu'ils avaient été soumis,
et la nouvelle section déclare explicitement qu'**en cas de contradiction, le §12bis fait foi**.

| OQ | Décision | Effet réel sur le code livré |
|---|---|---|
| **OQ-1** | `behavioral.readiness_score` reste hérité, **hors `TrainingState`** | `normalize_behavioral_readiness` **existe** (la table §3.1 doit rester complète) mais **aucun champ de `TrainingState` ne la consomme** — pinné par un test |
| **OQ-2** | **Pas de `BodyZone.recovery_hours`** ; lecture via adaptateur ; futur = `RecoveryPolicy` versionnée | `recovery_target_hours()` lit la constante par **import différé** ; un test vérifie que `BodyZone` n'a **pas** gagné l'attribut |
| **OQ-3** | **Aucune pondération globale** ; composantes séparément observables | **`overall` et `as_availability` RETIRÉS de `FatigueSignal`** — amendement réel de ma propre spec §2.2 (voir §5) |
| **OQ-4** | Aucun pourcentage cardio ; confiance plafonnée à `medium` ; magnitude déférée | `cardio_load_estimate` **déclarée, non calculée** : rend `(None, Confidence.NONE, basis)` |
| **OQ-5** | Zones détaillées décident ; macro = présentation ; **pire zone**, zone limitante exposée | `worst_zone_rollup()` + `MacroAxisRecovery.limiting_zone_code` |
| **OQ-6** | `0` sufficient · `1..2` partial · `>= 3` stale | `readiness_sufficiency_for_age()` + `READINESS_STALE_AFTER_DAYS = 3` |
| **OQ-7** | Influence **asymétrique**, plus tard, hors `recommendation.py` | `ReadinessSignal.is_decision_relevant` — dit « assez récent pour être *considéré* », jamais « autorise une escalade » |

**Le principe transversal** que ces décisions dessinent est énoncé une fois dans la spec :

> Un signal dégradé, ancien ou incertain **peut rendre le système plus prudent. Il ne peut jamais
> le rendre plus agressif.**

C'est la généralisation de la borne unilatérale de `Sb_FATIGUE_SCALE_FIX_01`.

## 2. Le contrat public créé

Module unique `app/services/recovery_contract.py`, **pur** : pas de DB, d'ORM, de routeur, de
template, de hasard, ni d'horloge propre.

### Vocabulaires fermés (`StrEnum`)

`Sufficiency` (`sufficient`/`partial`/`insufficient`/`stale`) · `Confidence`
(`high`/`medium`/`low`/`none`) · `RecoveryBand`
(`likely_available`/`partially_recovered`/`likely_fatigued`/`unknown`).

Placés **ici** et non dans `app/enums.py` : ce module-là est documenté pour les vocabulaires
**produits par l'utilisateur et persistés**. Rien de ce qui précède n'est persisté ni saisi.

### Types du contrat (tous `@dataclass(frozen=True)`)

| Type | Rôle |
|---|---|
| `ReadinessSignal` | Déclaratif du jour, daté, périmable. `fatigue_level` exposé **`self_reported_freshness`** |
| `FatigueSignal` | 3 composantes **séparées**, **aucun agrégat** |
| `ZoneRecoveryEstimate` | **Estimation** par zone : `band` · `confidence` · `basis` · `staleness` · `is_informative` |
| `MacroAxisRecovery` | Roll-up macro **de présentation**, avec `limiting_zone_code` |
| `TrainingSuitability` | L'ex-`availability_by_zone`, renommée |
| `EquipmentAvailability` | Contrainte externe : matériel |
| `ScheduleAvailability` | **Déclarée, non implémentée** (aucune donnée n'existe) |
| `TrainingState` | L'agrégat — **primitives uniquement, aucun score** |

### Helpers purs

`clamp_unit` · `mean_of_present` · `readiness_sufficiency_for_age` · `band_for_estimate` ·
`never_trained_estimate` · `worst_zone_rollup` · `fatigue_to_availability`.

### Constantes nommées

`NEUTRAL_ESTIMATE = 0.5` (le neutre est **nommé**, jamais un `0.5` perdu dans une formule —
spec §4.3 condition 1) · `READINESS_STALE_AFTER_DAYS = 3` · `NEVER_TRAINED_HOURS_SENTINEL` ·
`CARDIO_MAX_CONFIDENCE = Confidence.MEDIUM` · `ALLOWED_CONTRACT_WORDING` ·
`FORBIDDEN_CONTRACT_WORDING` · `RECOVERY_CONTRACT_VERSION = 1`.

## 3. Les 13 conversions

Chacune est **nommée, pure, déterministe, bornée**, explicite sur sa **direction** et sur son
**entrée manquante**. Elles sont en plus enregistrées dans **`LEGACY_SCALE_CONVERSIONS`**, un tuple
de 13 `ScaleConversion` liant chaque ligne du §3.1 de la spec à son implémentation — pour que la
table et le code **ne puissent pas diverger** ; trois tests le vérifient.

| # | Source héritée | Conversion | Point notable |
|---|---|---|---|
| 1 | `ReadinessEntry` × 4 dimensions | `normalize_readiness_scale` | `(v−1)/4` ; hors 1–5 entier ⇒ `None` |
| 2 | `ReadinessEntry.fatigue_level` | `normalize_readiness_scale` | Exposé **`self_reported_freshness`** — 5 = « Très frais » |
| 3 | `behavioral.fatigue_score` | `normalize_legacy_fatigue` | **Délègue** (§4) |
| 4 | `behavioral.readiness_score` | `normalize_behavioral_readiness` | Nommée, **non consommée** (OQ-1) |
| 5 | Axe recovery du dashboard | `normalize_percent_scale` | Ne porte **pas** `active=False` : un axe inactif reste `INSUFFICIENT`, pas `0.0` |
| 6 | `availability_by_zone` | `normalize_training_suitability` | **Corrige le fail-open** : jamais entraînée ⇒ `None`, plus `1.0` |
| 7 | `hours_since_last_by_zone` | `hours_since_last_or_none` | La sentinelle `24×365` devient `None` |
| 8 | `days_since_last_*` | `days_since_last_or_none` | Producteur déjà honnête ; rejette négatifs/non-entiers |
| 9 | `RECOVERY_HOURS_TARGET` | `recovery_target_hours` | **Lue** par import différé (OQ-2) |
| 10 | `global_state`/`concentration` | `normalize_session_feedback` | Réutilise `compute_session_fatigue` **puis** la conversion #3 ; les deux `None` ⇒ `None` |
| 11 | Champs cardio | `cardio_load_estimate` | **Déclarée, non calculée** (OQ-4) |
| 12 | `ZONE_FRESHNESS_BONUS_*` | **aucune** — `zone_freshness_bonus_conversion` documente pourquoi | Poids de ranking en points, pas une grandeur mesurée |
| 13 | Libellés FR de confiance | `confidence_from_legacy_label` | Libellé inconnu ⇒ `None`, jamais un défaut |

## 4. Preuve que `normalize_fatigue_score` est réutilisé

Trois preuves indépendantes, dont deux **exécutées** :

1. **Espion comportemental** — `test_legacy_fatigue_normalisation_delegates_to_the_existing_helper`
   monkeypatche `recommendation_explainer.normalize_fatigue_score` et vérifie qu'il est **appelé**
   avec l'argument brut. Si quelqu'un réimplémente la conversion ici, l'espion cesse de se
   déclencher.
2. **Garde AST anti-duplication** —
   `test_there_is_exactly_one_legacy_fatigue_formula_in_the_codebase` parcourt **tout `app/`**,
   collecte les `def` dont le nom contient `fatigue` **et** `normal`/`scale`, et exige exactement
   **deux** : l'implémentation canonique et le délégateur. Un troisième fait échouer le test. Elle
   vérifie en plus que le délégateur **ne fait aucune arithmétique**.
3. **Preuve exécutée que la garde mord** — j'ai planté
   `def normalize_fatigue_scale(v): return float(v) / 100.0` dans le module : **1 failed**. Retiré :
   vert. Ce n'est pas une garde décorative.

Conséquence sémantique : le plancher productible **15.0** et la borne unilatérale de
`Sb_FATIGUE_SCALE_FIX_01` s'appliquent **automatiquement** ici. La sentinelle d'échec `0.0` reste
inexploitable — pinné, y compris à travers `fatigue_to_availability`.

## 5. Tension avec ma propre spec, et comment elle est tranchée

**OQ-3 amende le §2.2 que j'avais écrit.** Ma spec donnait à `FatigueSignal` un champ `overall` et
un `as_availability` dérivé. L'opérateur a tranché : **aucun agrégat pondéré**.

Les deux champs sont donc **retirés**, et le complément de direction devient une **fonction pure
nommée** — `fatigue_to_availability(value)` — appliquée par l'appelant à **une composante de son
choix**. C'est plus honnête : l'agrégat supposait des poids que rien dans ce dépôt ne justifie,
et le complément d'un agrégat inventé aurait propagé l'invention.

L'amendement est **inscrit dans la spec** (§12bis, ligne OQ-3) et pinné par
`test_fatigue_signal_has_no_weighted_aggregate`.

**Deuxième tension, mineure : « implémenter les 13 conversions » vs « ne pas inventer de
coefficient cardio » (OQ-4).** Résolu en livrant la **signature, la forme de retour et le plafond
de confiance** de `cardio_load_estimate`, sans les nombres : elle rend `(None, Confidence.NONE,
basis)` et sa `basis` enregistre quels champs étaient présents, pour que l'adaptateur suivant — et
une surface d'explication — puissent dire **pourquoi** il n'y a pas d'estimation. Un contrat
déclaré vaut mieux qu'un coefficient inventé ou qu'un trou dans la table.

**Troisième point : `TrainingState.sufficiency` / `.confidence`.** Ma spec les nommait
`overall_sufficiency` / `overall_confidence`. Renommés sans le préfixe pour lever toute ambiguïté
avec l'interdit « pas de champ `overall_*` ». Ce sont des **qualificatifs catégoriels**, pas des
scores, et un test vérifie qu'aucune propriété de `TrainingState` ne rend un `float`.

## 6. Tests — `tests/test_recovery_contract.py`, 186 tests

**Quatre gardes critiques, prouvées mordantes par plantation de violations réelles :**

| Violation plantée | Résultat |
|---|---|
| Seconde formule `normalize_fatigue_scale(v) = v/100` | **CAUGHT** — 1 failed |
| `overall_score` ajouté à `TrainingState` | **CAUGHT** — 1 failed |
| Propriété `overall` ajoutée à `FatigueSignal` | **CAUGHT** — 1 failed |
| Docstring « measured muscle recovery » / « physiologically recovered » · fonction publique `diagnosis_for_zone` | **CAUGHT** ×3 — 1 failed chacune |

**La garde de vocabulaire a d'abord échoué à mordre**, et je l'ai corrigée : ma tolérance
`occurrences <= 1` (censée autoriser la deny-list à se nommer elle-même) laissait passer une vraie
occurrence. Remplacée par une exclusion explicite de `FORBIDDEN_CONTRACT_WORDING` du périmètre
scanné + une assertion **stricte à zéro**, et le scan couvre désormais aussi les docstrings de
membres. Re-vérifiée par plantation : elle mord sur les trois formes.

Couverture par thème :

- **Readiness** — 1→0.0 · 3→0.5 · 5→1.0 · rejet hors 1–5 entier · `fatigue_level` **absent** de la
  signature et `self_reported_freshness` **présent** · seuils 0/1-2/≥3 · âge inutilisable ⇒
  `INSUFFICIENT` · `stale` jamais promu · **dimension manquante exclue, jamais lue comme 0.0** ·
  défauts pessimistes.
- **Fatigue** — délégation (espion) · unicité de la formule (AST) · direction · **sentinelle `0.0`
  inexploitable, y compris via le complément** · complément explicite et borné · **aucun agrégat**
  (jeu de noms interdits) · composantes adressables · feedback de séance réutilisant le producteur
  de production (`good`+`high` ⇒ 0.15, le plancher productible) · **deux `None` ⇒ `None`**, pas les
  défauts 50/40.
- **Disponibilité** — les 3 types sont **distincts** et ne partagent aucun champ · **aucun type du
  contrat n'a de champ `available`** (le 4ᵉ sens, UI, reste dehors) · `None` = non contraint ·
  agenda vide en V1.
- **Zone** — **jamais entraînée ⇒ jamais `1.0`** · une estimation informative exige valeur **+**
  confiance **+** basis · défauts `UNKNOWN`/`NONE` · bandes et bornes.
- **Roll-up macro (OQ-5)** — pire zone, **zone limitante nommée** · confiance **dégradée** si une
  zone manque · rien de connu ⇒ `UNKNOWN` · **déterministe à égalité** · documenté « présentation ».
- **`TrainingState`** — **aucun score** (jeu de noms interdits) · **aucune propriété ne rend un
  `float`** · primitives préservées · défauts pessimistes · `schedule is None`.
- **Immuabilité** — les 8 types lèvent `FrozenInstanceError`.
- **Pureté / frontières** — le module ne contient ni `sqlalchemy`, ni `SessionLocal`, ni `select(`,
  ni `APIRouter` · **aucun import lourd au niveau module** · `recommendation.py` et
  `behavioral.py` **ne référencent pas** le contrat · **aucun vocabulaire de zone nouveau**.
- **Table §3.1** — 13 lignes · chaque ligne a une callable **ou** dit pourquoi elle n'en a pas ·
  chaque callable est une fonction publique du module · **aucune conversion ne mappe une entrée
  inutilisable vers une valeur favorable** (balayage croisé de 12 entrées inutilisables × 5
  conversions unitaires).

## 7. Vérifications locales

| Contrôle | Résultat |
|---|---|
| Tests ciblés | **186 passés** |
| Broad sweep ciblé (contrat · fatigue P0.2 · explainer · behavioral · reco · zones P0.1 · BodyZone P0.3 · mapping) | **371 passés** |
| ruff (fichiers neufs) | **clean** |
| Budget ruff | **543 ≤ 548** — **neutre** vs la canonique |
| `check_spec_protocol` | **PASS** |
| `check_scope` | **ISOLATED** — full sweep local **explicitement non requis**, et non lancé |

Le full sweep local n'a pas été lancé : `check_scope` ne l'exige pas à ce tier, la mission demande
de ne pas le faire sans nécessité, et le module est **neuf et importé par personne** — son blast
radius réel est nul. La CI de PR reste le filet de vérité.

## 8. Interdits tenus

**Périmètre d'implémentation** : 0 DB · 0 ORM · 0 routeur · 0 template · 0 UI · 0 moteur de
décision de recommandation · 0 migration · 0 modèle persisté modifié.

**Fichiers protégés** : `recommendation.py` **lu, jamais modifié** · `behavioral.py` **lu, jamais
modifié** — les deux vérifiés par test (aucun n'importe le contrat).

**Contrat** : `TrainingState` sans `overall_score`/`readiness_score`/`recovery_percentage`/composite
opaque · `FatigueSignal` sans agrégat · aucun `None` promu en valeur favorable · aucune sentinelle
lue comme « frais » · aucun `stale` promu en `sufficient`.

**Livraison** : pas de force-push, pas de rebase, pas de squash, pas de merge `--admin`,
`AGENTS.md` non touché, **`Sb_CARDIO_FATIGUE_ADAPTER_01` non ouvert**.

## Verdict

**Livré.** Le vocabulaire canonique existe et il est exécutable : quatre mots qui désignaient
chacun plusieurs choses ont un type, une échelle, une direction et une politique de données
manquantes, et les 13 conversions d'échelle héritées sont nommées, bornées et testées.

Trois propriétés structurantes sont **verrouillées par des gardes dont la morsure a été prouvée
par plantation** : il n'existe qu'**une** formule de fatigue héritée, `TrainingState` **ne peut pas**
gagner un score global, et le contrat **ne peut pas** se mettre à parler de récupération mesurée.

Le fail-open le plus vicieux de l'audit — une zone jamais entraînée rendue « parfaitement
disponible » — est corrigé **dans le vocabulaire lui-même** : il n'existe aucun chemin, dans ce
contrat, permettant à une absence de donnée de produire une bonne nouvelle.

Statut : `Sb_RECOVERY_CONTRACT_01 PR GREEN / MERGE PENDING` — puis merge permanent autorisé par la
mission. **`Sb_CARDIO_FATIGUE_ADAPTER_01` n'est pas ouvert.**
