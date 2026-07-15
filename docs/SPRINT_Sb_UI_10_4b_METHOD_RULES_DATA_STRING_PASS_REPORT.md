# Sprint Sb_UI_10.4b — Method Rules User-Facing Data String Pass (SPIGNOS → Auren) — BUILD

**Statut** : 🟢 **CODE COMPLETE — CI PENDING — HUMAN REVIEW PENDING**
**Type** : CODE BUILD — **data-string pass** (une chaîne produit visible seedée en base), pas de migration
**Date** : 2026-07-15
**Branche de travail** : `work/auren-migration-continuation` (isolée, mergée vers canonique après CI verte)
**Spec** : `Sx_UI_10` — ferme l'occurrence OPEN laissée par `Sb_UI_10.4`

> Ne prétend **pas** ACCEPTED. CI et human review = étapes séparées.

---

## 1. Contexte
`Sb_UI_10.4` (labels docs) a migré 8 chaînes template SPIGNOS → Auren mais a **laissé OPEN** une occurrence
**hors de son périmètre** (`data/**` interdit dans 10.4) : le body de la règle de méthode
`plages-repetitions` (`data/method_rules.json`), seedé en table `method_rules` et **rendu sur /science**
(« Le score d'un exercice dans **SPIGNOS** est dérivé… »). Le test sentinelle de 10.4 pinnait /science à
**exactement 1** SPIGNOS rendu, avec instruction : *« When that pass lands, flip this test to assert 0 »*.
Ce sprint `10.4b` est ce pass.

## 2. Étape 0 — Brainstorming / Options / Choix
Occurrence = **catégorie A (marque produit visible)**, rendue à l'utilisateur sur /science.
| Option | Verdict |
|---|---|
| **A** — remplacer « SPIGNOS » → « Auren » dans le body JSON | ✅ **RETENU** |
| B — reformuler sans marque | ❌ incohérent avec les autres textes Auren |
| C — laisser OPEN | ❌ c'est justement la dette à fermer |

**Faisabilité confirmée par audit** : `method_rules.json` est **seedé par wipe + reinsert à CHAQUE
startup** (`app/main.py` lifespan → `seed_method_rules`, `delete(MethodRule)` + réinsertion). Donc
**modifier le JSON suffit** : au prochain boot (et dans les tests via fixture DB fraîche), la table est
re-seedée avec « Auren ». **Aucune migration, aucun schéma, aucune FK entrante.**

## 3. Fichiers modifiés
| Fichier | Nature |
|---|---|
| `data/method_rules.json` | 1 chaîne body : « …dans SPIGNOS est dérivé… » → « …dans Auren est dérivé… » (marque seule ; texte scientifique intact) |
| `tests/test_auren_user_facing_labels.py` | test sentinelle **ré-orienté** : `test_science_remaining_spignos...` (== 1) → `test_science_no_visible_spignos_after_method_rule_migration` (**== 0** + « dans Auren est dérivé ») |

**Non modifiés** : templates, routes, services (`seed_method_rules` inchangé), modèles, migrations,
`schema_snapshot.sql`, manifest, assets, CSS, JS, base.html, autres data. Aucun renommage interne
(logger `spignos.request_timing`, table `method_rules`, slug `plages-repetitions` = techniques, conservés).

## 4. Preuves
- **JSON valide** ; 0 SPIGNOS / 1 Auren dans le fichier ; diff = mot marque uniquement.
- **Re-seed vérifié** (manuel) : après `seed_method_rules`, en base **SPIGNOS=0, Auren=1**.
- **Rendu /science** (fixture test, DB re-seedée) : **0 SPIGNOS**, « dans Auren est dérivé » présent.
- Sens scientifique du body (échec mécanique, plage 8-12, progression de charge) **inchangé**.
- Aucun QA ne valide le contenu de `method_rules.json` (pas de drift) ; catalog_qa PASS ;
  `schema_snapshot.sql` non impacté (donnée, pas schéma) ; rapport QA auto-régénéré restauré.

## 5. Tests locaux
- `test_auren_user_facing_labels.py` + `test_science_page.py` = **20 passed** (dont le test sentinelle ré-orienté → 0 SPIGNOS).
- Sweep ciblé (science/method/seed/auren_user_facing) = **25 passed**.
- ruff **543 ≤ 548** ; spec protocol **PASS** ; check_scope = **ISOLATED** (2 fichiers ; pas migration :
  ni `migrations/`/`app/models/`/`schema_snapshot.sql`).

## 6. Statut CI
**PENDING** — au push de la branche / à la PR. Le body étant seedé et rendu, la CI (suite complète)
est la source de vérité.

## 7. Éléments différés (inchangés)
`Sb_UI_10.2` (BLOCKED BY ASSETS) · `Sx_UI_10` Closeout (BLOCKED BY 10.2) · Dogfood F1/F2/F3 (séparé).

## 8. Human review
**PENDING** — session séparée. Ce commit ne contient pas de revue.

---

## Verdict

**Verdict :** 🟢 **Sb_UI_10.4b — CODE COMPLETE (data-string pass).** La dernière occurrence SPIGNOS
visible côté utilisateur (règle de méthode `plages-repetitions`, seedée et rendue sur /science) migre
SPIGNOS → **Auren**. **Data-only, aucune migration** (table re-seedée wipe+reinsert au boot) ; texte
scientifique intact ; identifiants internes (table/slug/logger) conservés ; zéro Orion. Test sentinelle
ré-orienté (/science == 0 SPIGNOS). **Après ce pass, plus aucune surface utilisateur ne rend « SPIGNOS »**
(shell 10.1 + auth 10.3 + docs 10.4 + cette donnée). 20 + 25 tests verts local.

**Recommandation** : commit sur `work/auren-migration-continuation`, CI verte, puis **merge** dans
`claude/sprint-reporting-fitness-app-V7Qr6`. `10.2` reste bloqué (assets) ; closeout après 10.2.
