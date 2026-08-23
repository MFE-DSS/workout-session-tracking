# `Sb_EKB_ORTHOGRAPHIC_ALIAS_01` — deux écritures, une vérité

**Décision opérateur** : 2026-08-23, hors slices TRAIN 1
**Branche** : `sb/ekb-orthographic-alias-01` · **base** : `a71ac24`
**Tier** : `check_scope` dit `ISOLATED` → **promu `SHARED_CODE`** (§1 : en cas
de doute, remonter d'un cran)

---

## 0. La décision, et ce qu'elle recouvre

> « `Curl marteau câble corde` est un alias orthographique de
> `Curl marteau câble (corde)`. Identité canonique = la forme parenthésée du
> catalogue. Préserver les chaînes historiques. Ne pas créer deux identités
> `Exercise`. Aligner la cartographie EKB contradictoire sur la cartographie
> canonique mesurée si cela ne viole pas le format du snapshot ; l'autorité
> d'identité reste `exercise_aliases`. **Ne pas généraliser aux 17 autres
> candidats.** »

---

## 1. Ce que la mesure a établi avant d'écrire

Le `null` de l'entrée alias n'était justifié par **aucune source amont** :

| Source | `Curl marteau câble (corde)` | `Curl marteau câble corde` |
|---|---|---|
| `exercise_properties.json` | `zone_primary: arms`, `isolation_upper`, `cable`, `isolation` | **identique** |
| `classify_exercise` | `biceps` | **`biceps`** |
| **EKB avant correction** | `biceps` / `arms` / `measured` | **`None` / `None` / `derived`** |

Les deux sources s'accordent sur les deux orthographes. **La divergence
naissait de la construction de l'EKB, pas d'un désaccord de données.**

C'est ce qui rend l'alignement **dérivable** plutôt qu'un copier-coller de
jugement — et c'est pourquoi l'entrée alias porte désormais
`confidence: "measured"` : elle repose sur la même mesure que la canonique, pas
sur elle.

---

## 2. Écriture minimale et préservante

Trois champs alignés (`zone_primary`, `zone_macro`, `confidence`) et
`curation_note` renseigné sur **les deux** entrées — champ existant, jusque-là
`null`, donc **aucune violation du format du snapshot**.

Ce qui n'est **pas** touché :

- **Aucune clé supprimée** — les 103 entrées restent, les chaînes historiques
  sont préservées. Supprimer l'alias casserait toute donnée déjà écrite avec
  cette orthographe.
- **`variant_key` n'est pas aligné** — il est distinct par construction et sert
  de clé de variante, pas d'identité ; le fusionner créerait la collision que
  la décision interdit.
- **`_aliases` n'est pas touché** — cette clé recense les orphelines de
  `exercise_properties`, un concept distinct. L'autorité d'identité est la
  **table `exercise_aliases`**, qui collapse déjà les deux formes : 103 entrées
  → **102 identités**, vérifié en base.

---

## 3. La garde qui manquait

Les 19 gardes existantes vérifiaient l'unicité des `variant_key`, la répartition
`covered`/`gap`, la réconciliation des zones fines vers les macro-zones —
**jamais l'accord entre deux écritures d'un même nom**. Le défaut a donc vécu
sans être vu.

**5 gardes ajoutées**, et la principale a été **plantée sur les données
d'avant** : elle rougit en nommant les trois champs contradictoires.

```
AssertionError: deux écritures d'un même nom portent des cartographies
différentes — l'exercice serait décrit selon l'orthographe rencontrée :
  zone_primary: 'Curl marteau câble (corde)'='biceps' vs '…corde'=None
  zone_macro:   'Curl marteau câble (corde)'='arms'   vs '…corde'=None
  confidence:   'Curl marteau câble (corde)'='measured' vs '…corde'='derived'
```

Puis verte une fois le correctif restauré.

### La portée est bornée, mécaniquement

⚠ **La décision ne se généralise pas aux 17 autres candidats.** La garde ne
compare que des noms **égaux après normalisation stricte** — elle n'attrape que
les écarts de ponctuation, d'accent et de casse, **jamais une différence de
mots**. `Hip thrust Smith` et `Hip thrust Smith machine` ne sont pas groupés, et
ne le seront pas.

Une seconde garde vérifie que cette paire reste **la seule** : un doublon
d'orthographe neuf doit se faire remarquer, pas se fondre dans une garde
d'accord déjà satisfaite.

---

## 4. Vérifications

| Contrôle | Résultat |
|---|---|
| `check_scope` | `ISOLATED` → **promu `SHARED_CODE`** |
| ruff | `All checks passed!` |
| `check_ruff_budget` | 281 ≤ 548 |
| `check_spec_protocol` | PASS |
| Tests EKB | 19 → **24 passed** |
| **Broad sweep** — 17 fichiers consommateurs | **342 passed** |
| `scripts.ekb_coverage_qa` | OK |
| `scripts.ekb_classifiability_qa` | OK, 4 warnings attendues, compteur figé |

Le tier a été **promu manuellement**. `check_scope` classe `ISOLATED` un diff
qui ne touche que `data/**` et `tests/**` — or l'EKB est lu par **18 modules**
(planner, quality engine, programmes utilisateur, morpho, slot intent). Le même
faux classement avait déjà été relevé sur `exercise_properties`.

---

## 5. Non-régressions

- **0 clé supprimée**, 103 entrées avant et après.
- **0 chaîne historique réécrite.**
- **0 identité `Exercise` créée** — toujours 102, vérifié en base.
- **0 généralisation** aux 17 autres candidats — bornée par la normalisation
  stricte, pas par une promesse.
- **0 revendication scientifique** : les valeurs viennent de sources existantes.
