# `MUSCLE_MAPPING_TRUTH_01` — l'exposition anatomique cesse de compter l'ignorance pour zéro

**Tranche** : `MUSCLE_MAPPING_TRUTH_01` (A1 du registre d'arbitrage — décision opérateur `A3 = B`)
**Branche** : `sb/muscle-mapping-truth-01` · **base canonique** : `a29a104`
**Tier `check_scope`** : `SHARED_CODE`
**Surface** : `/progress` — instrument d'exposition anatomique (14 jours)

---

## 0. Brainstorming / Options / Risques / Choix retenu

*(CLAUDE.md §3 — obligatoire avant code)*

### Le défaut, mesuré avant d'être corrigé

`build_zone_exposure` classait chaque exercice avec `classify_exercise(nom)`. Un
exercice non reconnu **ne comptait pas** — il disparaissait silencieusement du
numérateur sans jamais empêcher l'état `known`. Conséquence en fenêtre
contrôlée : une séance de deux exercices dont **un seul** est attribuable rendait

> « 2 zones touchées » + **9 lignes à `0`**

Les neuf zéros étaient **fabriqués**. On ignorait ce que l'exercice non reconnu
avait sollicité ; n'importe laquelle de ces neuf zones avait pu l'être. Le
produit affirmait donc neuf faits qu'il ne possédait pas, avec l'autorité
visuelle d'un instrument.

### Deux mesures qui cadrent la correction

| Mesure | Résultat | Statut |
|---|---|---|
| Catalogue canonique vs `ExerciseMuscleMapping` | **68/68 attribués, 0 conflit** | MESURÉ |
| Usage réel en production | — | **NON MESURÉ** (pas d'accès prod, et on n'en invente pas) |

La deuxième ligne est la raison d'être de la tranche : la couverture parfaite du
catalogue **ne garantit rien** sur les noms libres saisis en substitution
([sessions.py:866](../app/routers/sessions.py#L866), texte libre à 255
caractères). Un produit honnête doit donc savoir dire « partiellement ».

### Options

| # | Option | Verdict |
|---|---|---|
| A | Ne rien changer — la couverture catalogue est parfaite | **Rejetée.** Elle mesure le catalogue, pas l'usage. La substitution libre reste une source vivante de noms inconnus. |
| B | Compter l'inconnu comme zéro, mais afficher un avertissement | **Rejetée.** Une note ne désarme pas neuf chiffres. Le lecteur croit les chiffres. |
| C | Basculer en `unknown` global dès un seul exercice non attribué | **Rejetée.** Jette des faits vrais : les zones observées **ont** été travaillées. C'est une soustraction (§5.3). |
| **D** | **Quatrième état `PARTIAL`** — les comptages positifs survivent comme **minima observés**, les zones non observées deviennent **inconnues, pas nulles** | **Retenue.** Seule option qui ne perd aucun fait vrai et n'en fabrique aucun faux. |

### Risques et parades

| Risque | Parade | Garde |
|---|---|---|
| `PARTIAL` réintroduit une ligne à `0` par régression | Filtre `if exp.counts.get(z)` dans la vue-modèle | `test_partial_never_renders_a_zero_row` |
| Le résolveur contamine les moteurs de décision gelés | Le résolveur n'est importé que par l'analytique | `test_the_decision_engines_never_import_the_resolver` (AST) |
| Les quatre états deviennent indistinguables | — | `test_the_four_states_are_reachable_and_distinct` |
| Silhouette : le fond neutre reste lu comme « zéro » | Fond `unknown` **hachuré** (`<pattern>` déclaré en CSS, pas en attribut de présentation) | rendu vérifié en navigateur |

---

## 1. Ce que la tranche livre

### 1.1 `app/services/exercise_zone_resolver.py` — neuf (autorité + provenance)

Point de résolution unique `nom → zone`, qui **rend aussi d'où vient la
réponse** :

| Source | Sens |
|---|---|
| `DB_EXACT` | une ligne `ExerciseMuscleMapping` active porte ce nom |
| `LEGACY_FALLBACK` | seul le matcher hérité a su répondre |
| `UNMAPPED` | ni l'un ni l'autre |

`resolved_db` / `resolved_legacy` ne sont **pas rendus** : ce sont les
instruments qui mesureront la bascule de A3 vers son option `c` (retrait du
matcher hérité). Sans eux, cette décision se prendrait à l'aveugle.

### 1.2 `app/services/zone_exposure.py` — le quatrième état

`STATE_PARTIAL` s'insère **avant** l'arbitrage `known`/`zero` :

```python
if classified and unmapped:
    return ZoneExposure(state=STATE_PARTIAL, counts=counts, **common)
```

Et la vue-modèle en tire deux conséquences, pas une :

- `base = "unknown" if exp.state == STATE_PARTIAL else "zero"` — sur la
  silhouette, une région non observée ne peut plus être affirmée vide ;
- `rows = [… for z in ZONE_LABELS if exp.counts.get(z)]` — au niveau 2,
  **aucune ligne à zéro n'est rendue**.

### 1.3 Surface

`_partials/zone_exposure.html` gagne une branche `partial` : en-tête « *N zones
identifiées · minimum observé* » + le compte d'exercices non attribués, rendu et
non tu. `app.css` déclare `.ze-r--unknown { fill: url(#auren-hatch) }` — la
hachure vit **dans la feuille de style**, parce qu'une règle CSS bat un attribut
de présentation SVG (défaut vécu dans cette même session).

---

## 2. Relecture du relevé de décisions (CLAUDE.md §5.2)

| Décision | Verdict |
|---|---|
| §5.1 exposition visuelle préalable | **Respectée** — quatre fixtures (`known`, `zero`, `unknown`, `partial`) rendues en navigateur et soumises à l'opérateur avant tout commit |
| §5.2 relecture consignée | **Respectée** — ce tableau |
| §5.3 jamais une soustraction seule | **Respectée** — `PARTIAL` **ajoute** un état ; aucun fait vrai n'est retiré, les comptages observés survivent |
| §5.4 toute couleur est un token | **Respectée** — aucune couleur neuve ; `.ze-r--unknown` réutilise `var(--fg-dim)` et une hachure construite depuis `currentColor` |
| §5.5 centralité avant facilité | **Respectée** — c'est la décision de vérité sémantique, priorisée n°1 par l'opérateur devant le rail L2 et l'instrument progressif |
| AMBRE = action utilisateur / BLEU = produit système | **Respectée** — l'exposition anatomique reste bleue (produite par le système) |
| Ne pas dessiner d'anatomie / inventer de géométrie | **Respectée** — aucune géométrie neuve, la silhouette existante est réutilisée |

---

## 3. Vérifications (tier `SHARED_CODE`)

| Contrôle | Résultat |
|---|---|
| `check_scope` | `SHARED_CODE` — full sweep local **non requis** |
| ruff (fichier neuf) | `All checks passed!` |
| `check_ruff_budget` | 281 ≤ 548 |
| `check_spec_protocol` | PASS |
| Tests ciblés | `test_ux4_zone_exposure.py` — **23 passed** |
| Broad sweep ciblé (12 fichiers consommateurs du mapping) | **339 passed** |
| Sweep surface Progression | **58 passed** |

**397 tests verts** sur le rayon d'impact. Le sweep a été lancé avec `env -C`
depuis le worktree — le compte de 23 (contre 17 sur la canonique) **prouve** que
c'est bien l'arbre modifié qui a été mesuré.

---

## 4. Ce que la tranche ne fait pas

- **Aucune migration de schéma.** L'identité d'exercice stable (A1) est une
  tranche séparée, ordonnée par l'opérateur en TRAIN 1.
- **Aucun changement de moteur de décision.** `recommendation.py` et
  `substitution.py` restent sur le matcher hérité et sur leur gel (A3 = B).
- **Aucun retrait du matcher hérité.** Différé jusqu'à identité stable +
  preuve d'usage suffisante (A3 option `c`).
- **Aucune revendication d'activation musculaire, EMG ou pourcentage.**

---

## 5. Erratum porté par cette tranche

Un rapport antérieur affirmait que « Développé militaire » et « Soulevé de terre
roumain » étaient des exercices du catalogue non attribués. **C'était faux** :
ces deux noms étaient des fixtures que j'avais écrites moi-même, pas des entrées
du catalogue. L'affirmation avait été inscrite dans `c2a5c43`, `a29a104`, le
blueprint et le compte rendu final.

L'historique n'est **pas réécrit** (décision opérateur). L'erratum est posé en
§10 du rapport `UX4_03B` et dans `AUREN_UI_BLUEPRINT`, citant les deux SHAs
concernés. La mesure correcte est celle du §0 : **68/68, 0 conflit**.
