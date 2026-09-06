# CP-1 — le signal historique porte sa lignée

**Tier `check_scope`** : `SHARED_CODE`.
**Fichiers** : `app/services/overload_engine.py` · `app/services/overload_inputs.py` ·
`tests/test_cp1_temporal_lineage.py`
**`BEHAVIOUR CHANGE = NONE`** — aucune prescription ne bouge, et une garde le
tient mécaniquement.

---

## 1. Ce que CP-1 corrige, mesuré avant de l'écrire

`RUNTIME_MEASURED`, en processus isolés, une base jetable par scénario.

Deux historiques dont la **seule** différence est l'existence de séances
substituées produisaient une charge utile **identique champ par champ** :

```
A — l'utilisateur s'est entraîné : 2 substituts, le dernier il y a 7 j
B — l'utilisateur ne s'est pas entraîné depuis 100 jours

{"has_data": true, "relative": "il y a 3 mois", "session_id": 26,
 "started_at": "2026-05-29T12:00:00", "weights_str": "100", ...}   ← LES DEUX
```

**Aucun champ ne les distingue.**

### Les trois histoires, indépendamment

| Cas | Séance courante | Repère | Âge | Entraîné en continu ? | Écart repère / réalité |
|---|---|---|---|---|---|
| **A** prescrit → prescrit | prescrit | 100 kg | il y a 1 sem | oui | **0 j** |
| **B** prescrit → substitut | substitut | **aucun** | — | **oui, il y a 7 j** | — |
| **C** prescrit → substitut(s) → prescrit | prescrit | 100 kg | **il y a 3 mois** | **oui, il y a 7 j** | **93 j** |

**Cause du cas C** : la politique de substitution (`stats.py:157-168`) saute les
occurrences substituées et remonte jusqu'au dernier prescrit. L'utilisateur
s'est entraîné sans interruption — avec un substitut — et reçoit un repère de
mai. **L'âge de la référence est découplé de son absence à lui**, et la
politique est invisible à l'écran.

**Cas B**, `CODE_TRACED` : le silence n'est pas neutre. `exercise_card.html:396`
rend « **Première fois** » à quelqu'un qui a fait ce mouvement prescrit il y a
sept jours. Ce n'est pas une information manquante, c'est une affirmation
fausse. **CP-1 ne la corrige pas** — c'est une décision de politique de
sélection, hors périmètre — mais une garde fige le comportement.

---

## 2. Brainstorming / Options / Risques / Choix retenu

### Option A — dater le repère à l'écran

Afficher « il y a 3 mois » à côté de `Réf. 100 kg`.

* ❌ La suggestion posée juste en dessous **ignore le temps**. On afficherait
  un âge à côté d'un nombre calculé sans lui : deux informations qui se
  contredisent sur la même ligne. La contradiction serait pire que le silence.
* ❌ Et ça ne lève pas le cas C : « il y a 3 mois » ne dit pas *« mais tu t'es
  entraîné il y a 7 jours »*.

### Option B — rendre le moteur conscient du temps

* ❌ **Une métadonnée temporelle est un FAIT ; une règle de décroissance est une
  HYPOTHÈSE DE DOMAINE.** Deux niveaux de maturité différents. Aucune preuve
  dans ce dépôt ne fixe un seuil de désentraînement.
* ❌ Ce serait un changement de recommandation déguisé en transport de donnée.

### Option C — transporter la lignée, sans l'utiliser *(retenu)*

* ✅ Le fait avant la politique. Le moteur **peut** dire sur quoi il s'appuie et
  quand — il ne décide pas encore quoi en faire.
* ✅ `BEHAVIOUR CHANGE = NONE`, prouvable mécaniquement.
* ✅ Aucune migration : tous les champs dérivent de colonnes existantes.

### Risques et leur traitement

| Risque | Traitement |
|---|---|
| Un champ neuf change une prescription | `test_la_prescription_ne_depend_pas_de_la_lignee`, **4 états paramétrés** — même les *raisons* doivent être identiques |
| CP-3 arrive sans décision | `test_le_moteur_reste_aveugle_au_temps` — balayage AST du moteur, docstrings retirées |
| Cette garde lit la prose comme du code | Une garde-de-la-garde vérifie qu'elle **épargne** une docstring parlant de `decay` et `.days`, et **mord** sur un vrai `h.days > 30` |
| Un champ sans consommateur | `computed_at` a été **proposé puis écarté** — voir §4 |
| La garde ne teste que la dataclass | `_signaux()` passe par la **base**, pas par un constructeur à la main |

---

## 3. Ce que la tranche fait

### `HistoricalSetSignal` — trois champs, tous optionnels

```
+ performed_at: datetime | None = None       quand la série a été exécutée
+ source_session_id: int | None = None       d'où elle vient — vérifiable
+ substituted_name: str | None = None        None = prescrit
```

### `OverloadHint` — un champ

```
+ reference_signal: HistoricalSetSignal | None = None
```

`None` pour l'état `unknown`, qui n'a par définition aucun historique. Pour les
quatre autres, c'est l'occurrence dont `target_weight_kg` dérive.
`engine_version` disait déjà **comment** le calcul est fait ; ce champ dit **sur
quoi**.

---

## 4. Ce qui n'entre PAS dans le contrat, et pourquoi

| Écarté | Raison |
|---|---|
| `computed_at` | **Aucun consommateur avant CP-2.** La directive interdit un champ sans besoin démontré |
| `actual_exercise_id` | **N'existe pas.** `substituted_name` est une chaîne libre, normalisée seulement à la comparaison (`exercise_identity.identity_key`). Le contrat transporte la chaîne, il ne prétend pas à un identifiant |
| `has_more_recent_skipped` | Lèverait complètement l'ambiguïté du cas C — mais **pas de consommateur avant CP-2**. Nommé, pas ajouté |
| tout seuil, score, décroissance | `CP-3`. Une hypothèse de domaine sans preuve |

---

## 5. Compatibilité — migration : **NON**

`CODE_TRACED`.

* Les trois champs **dérivent de colonnes existantes** : `WorkoutSession.started_at`,
  `.id`, `SessionExercise.substituted_name`. Rien à écrire, rien à rétro-remplir.
* `HistoricalSetSignal` est une dataclass `frozen` **sans consommateur hors du
  moteur** : des champs à valeur par défaut ne cassent aucun appelant.
* Les séances anciennes portent déjà ces colonnes — la lignée est disponible
  rétroactivement, sans traitement.
* Les snapshots (`template_slug_snapshot`, `exercise_code_snapshot`) protègent
  l'historique des renames.

---

## 6. Preuve que le comportement numérique est identique

**Deux preuves indépendantes.**

**Structurelle**, `CODE_TRACED` : le moteur ne lit que **quatre attributs** du
signal — `weight_kg` (l. 174, 195, 220, 240), `reps` (126, 294, 302),
`quality_score` (133), `fatigue_signal` (295). Aucun chemin n'en lit un
cinquième.

**Mécanique**, `TEST_PROVEN` : `test_la_prescription_ne_depend_pas_de_la_lignee`
compare, sur **quatre états** (`progress`, `consolidate`, `top-range`,
`deload`), un historique **nu** et le même **portant une lignée très ancienne**.
`state`, `target_weight_kg`, `target_reps_min/max` **et les raisons** doivent
coïncider.

**Et la garde de frontière** : injecter dans le moteur une lecture de
`performed_at` fait rougir `test_le_moteur_reste_aveugle_au_temps` —
`RUNTIME_MEASURED` par plantation.

---

## 7. Vérifications

| Contrôle | Résultat |
|---|---|
| `check_scope` | `SHARED_CODE` |
| `ruff` (fichiers touchés) | `All checks passed!` |
| `check_ruff_budget` | *(voir appendice)* |
| `check_spec_protocol` | *(voir appendice)* |
| `tests/test_cp1_temporal_lineage.py` | **15 passés** |
| Tests de surcharge existants | **146 passés** |
| **Broad sweep ciblé** — 39 fichiers | **754 passés · 0 échec** |
| **Défaut d'origine replanté** — lignée non peuplée | **3 gardes rouges** |
| **Défaut CP-3 injecté** — le moteur lit le temps | **1 garde rouge** |
| Fichiers restaurés après plantation | à l'identique |

---

## Verdict

**LIVRÉ.** Le signal historique porte désormais **quand** il a été exécuté,
**d'où** il vient, et **s'il était prescrit ou substitué**. La recommandation
peut désigner l'occurrence dont elle dérive.

Aucune prescription ne change, et ce n'est pas une intention : c'est une
impossibilité structurelle, doublée d'une garde sur quatre états.

**Ce que CP-1 ne résout pas, nommément :**

* le **« Première fois » faux** du cas B — politique de sélection, hors périmètre ;
* l'ambiguïté **résiduelle** du cas C : `substituted_name` sur le repère retenu
  dit *« ce repère est un prescrit »*, pas *« et deux substituts existent
  depuis »*. Lever cela demande un champ de plus, qui n'aura de consommateur
  qu'en CP-2.

**Le temps est désormais un CONTEXTE transporté. Il n'est pas encore une
POLITIQUE** — et la garde de frontière l'y maintient jusqu'à ce que CP-3 soit
ouvert avec des preuves.
