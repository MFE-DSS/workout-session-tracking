# Sprint Sb_catalog_v13 Report — Adductions + Pulldown Pull B

**Date :** 2026-04-21
**Type :** Catalogue uniquement — édition JSON, zéro code, zéro migration
**Issu de :** dogfooding J+0 (notes utilisateur §C1 + §C2)

---

## 1. Objectif

Corriger deux trous de couverture identifiés en dogfooding :

- **C1** — `legs-a/E5 Adduction assise` était sans substitut alors que des alternatives évidentes existent (debout, couchée).
- **C2** — Pull B n'offrait aucune alternative `tirage vertical` aux 3 rowings principaux. Si la machine est occupée et que l'utilisateur veut basculer sur un pulldown, le drawer substitution ne le proposait pas.

## 2. Modifications

### `data/reference_split.json` — version `2026-04-18.v12` → `2026-04-21.v13`

| Slot | Avant | Après |
|------|-------|-------|
| `legs-a/E5 "Adduction assise"` | `substitutes: null` | `["Adduction debout câble", "Adduction couchée machine"]` |
| `pull-b/E1 "Rowing machine chest-supported"` | 2 substituts existants | + `Tirage poulie haute prise neutre` |
| `pull-b/E2 "Rowing câble assis prise neutre"` | 2 substituts existants | + `Tirage poulie haute prise neutre` |
| `pull-b/E3 "Rowing haltère un bras (banc)"` | `substitutes: null` | `["Tirage poulie haute prise neutre"]` |

## 3. Décisions

- **Pas de nouvelle position d'exercice** sur Pull B. Le user disait « comme exercice principal **ou** comme substitut » — j'ai choisi substitut pour ne pas alourdir la séance (Pull B est déjà à 7 ex / 20 sets). L'utilisateur peut basculer via le drawer pendant la séance si la machine est occupée.

- **Le tirage vertical proposé** : « Tirage poulie haute prise neutre » (alias `lat-pulldown` dans l'atlas via `apply_machine_atlas_links.py`). Choix par défaut du catalogue sur les autres templates. Cohérent.

- **Adductions** : choix de wording aligné avec la convention du catalogue (verbe + adverbe + équipement). « Adduction debout câble » et « Adduction couchée machine » classifient en `posterior` (zone primaire ischios/fessiers/adducteurs) via `classify_exercise`.

## 4. Vérifications

```
catalog_qa.py        : PASS (16 templates, 98 exercises, 0 err, 0 warn)
test_catalog_integrity.py : 10/10 passed
test_library.py      : 11/11 passed
```

Pas de migration. Pas de code Python touché. Pas de full suite relancée — le changement est strictement déclaratif (JSON + version bump).

## 5. Prochain cycle catalogue

Pas d'autres trous identifiés en dogfooding J+0. Si la passe complète à J+7 fait remonter d'autres alternatives manquantes, prévoir un Sb_catalog_v14 ciblé.

---

## Synthèse

- v12 → **v13** (4 substituts ajoutés sur 3 templates différents)
- 0 nouvelle migration
- 0 code touché
- catalog_qa + test_catalog_integrity + test_library tous verts
