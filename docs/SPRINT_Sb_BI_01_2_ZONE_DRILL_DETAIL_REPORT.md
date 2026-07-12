# Sprint Sb_BI_01.2 — Zone Drill Detail

**Statut** : 🟢 DELIVERED — pending GO commit + CI + human review
**Type** : CODE BUILD — Body Intelligence drill detail, SSR/Jinja, mobile-first, sous flag existant
**Date** : 2026-07-11
**Cycle** : Body Intelligence (reprise Sx_BI_01, Option A)
**Préconditions** : `Sb_BI_01.1` ACCEPTED ✅ · `Sx_TRANSFORM_01` ACCEPTED ✅ · `body_intelligence_enabled` OFF prod ✅ (toutes vérifiées).

---

## 0. But produit

Permettre de comprendre **pourquoi** une zone apparaît dans les cards : un niveau de
détail sobre par zone (exercices principaux) dans `/body/intelligence`, **sans
nouvelle page publique et sans activer le flag prod**. Le drill **explique la card**,
il n'augmente pas l'intelligence apparente.

---

## 1. Étape 0 — Brainstorming / Options / Choix retenu

### Options

| Option | Description | Verdict |
|---|---|---|
| **A** | Drill inline SSR `<details>` dans chaque zone card | ✅ **RETENU** |
| B | Nouvelle route `/body/intelligence/zones/{zone}` | ❌ trop large V1 (routing/test/UX) — différé |
| C | Mini-historique graphique | ❌ trop dense, risque dashboard |
| D | Liste top exercices sans drill | ❌ trop faible pour un « drill » (fallback si données insuffisantes seulement) |

### 15 sujets clivants tranchés

1. **Drill inline** (pas de nouvelle route).
2. **`<details>` SSR natif, no-JS** (disclosure widget natif du navigateur).
3. Réutiliser **`top_exercises`** déjà calculés (noms) — **pas de recalcul** d'historique par zone.
4. Afficher **noms d'exercices seulement** (pas de volume par exercice : recalcul lourd, différé — §limites).
5. Fenêtre **30 j** (cohérent avec la card), pas de 30/90.
6. Éviter le dashboard dense : `<details>` **replié par défaut**, contenu minimal.
7. Contribution reste une **part**, jamais un score ; le drill n'ajoute aucun chiffre synthétique.
8. **Zones primaires uniquement** (comme la card V1) ; secondaires différées.
9. Pas d'exercices « À qualifier » (les unknown sont skippés en amont par `muscle_scoring`).
10. Top exercices vides → **« Détail insuffisant »** sobre.
11. `/physique` **intact** (non touché).
12. Flag `body_intelligence_enabled` **OFF prod** inchangé (activé en test seulement).
13. **Auren Terminal** tokens existants, aucune nouvelle couleur.
14. Tests **no-JS / no-score / no-radar**.
15. Route drill (Option B) **différée**.

**Choix : Option A** — `<details>` inline par card, sous flag existant, no-JS, pas de nouvelle route, `/physique` intact, aucun nouveau score.

### Risques / parades

| Risque | Parade |
|---|---|
| Dashboard dense | `<details>` replié + contenu minimal (noms) |
| JS requis | `<details>`/`<summary>` = disclosure **natif**, zéro JS |
| Contribution → score | drill n'affiche que des noms + un rappel non médical |
| Casser la card `.1` | contrat card conservé ; `top_exercises` étendu 2→3 (non affiché en `.1`) ; test `.1` reste vert |

---

## 2. Pourquoi inline `<details>`

`<details>`/`<summary>` est le **disclosure widget natif** du HTML : il fournit un
repli/dépli **sans une ligne de JS**, respecte le **no-JS fallback** (contenu
accessible même JS désactivé), reste **mobile-first** (tap sur le summary), et
n'introduit **aucune nouvelle route** ni page. C'est l'implémentation minimale qui
« explique la card » sans devenir un dashboard.

---

## 3. Données réutilisées

| Champ drill | Source |
|---|---|
| Exercices principaux (≤ 3 noms) | `ZoneScore.top_exercises` (déjà calculé par `_top_exercises(n=3)` dans `muscle_scoring`, **fréquence d'apparition**) |

Le router expose désormais `top_exercises[:3]` (au lieu de `[:2]`, non affiché en
`.1`). **Aucun recalcul**, aucun nouveau champ métier.

---

## 4. Ce qui reste non affiché (limites V1)

- **Volume par exercice** : `top_exercises` ne porte que des **noms** (fréquence), pas
  le tonnage par exercice. L'afficher exigerait un **recalcul** de l'historique par
  exercice → différé (Option B / `Sb_BI_01.next`).
- **Zones secondaires** : non affichées (primaire V1).
- **Historique 90 j** : hors périmètre (30 j seulement).
- **Score / grade / radar** : jamais surfacés (invariant du cycle).

---

## 5. Flag toujours off

`body_intelligence_enabled` reste **OFF en prod** (défaut inchangé) — le drill (comme
toute la surface `/body/intelligence`) reste **invisible** en production. Activation
en test uniquement (`BODY_INTELLIGENCE_ENABLED=1`). Aucune config prod modifiée.

---

## 6. Fichiers modifiés

| Fichier | Nature |
|---|---|
| `app/routers/body_intelligence.py` | `top_exercises[:2]` → `[:3]` pour alimenter le drill (commentaire) |
| `app/templates/_partials/body_intelligence_zone_card.html` | + `<details class="zone-card__drill">` (summary « Détail zone », liste top exercices, note, état vide « Détail insuffisant ») |
| `app/static/css/body_intelligence.css` | + styles `.zone-card__drill*` Auren Terminal (tokens existants), tap target summary |
| `tests/test_bi01_zone_drill_detail.py` | **nouveau** — 10 tests |

**Non modifiés** : `muscle_scoring.py`, `physique.html`, `index.html` (Home), `body_intelligence.html`, modèles, migrations, JS.

---

## 7. Tests

### `tests/test_bi01_zone_drill_detail.py` (NOUVEAU, 10 tests)
1. **Flag** : 404 si off (client dédié) · drill rendu si on.
2. **Drill** : un `<details>` par card active · `<summary>` natif · top exercices affichés · **aucun JS** (`<script>`/`onclick`/`addEventListener`).
3. **Non-score** : section drill sans `/100`, sans radar, sans « score global »/« note globale »/grade.
4. **État vide** : partial porte « Détail insuffisant ».
5. **Architecture** : pas de JS dans partial/template · router réutilise `top_exercises` sans `.score`/grade · `/physique` et Home non touchés.
6. **Wording interdit** : ni diagnostic, body fat, morphotype, attractivité, pathologie, « score physique », « note corporelle ».

### Résultats
- Dédiés : **10/10 verts**.
- Test `.1` (`test_bi01_zone_intelligence_cards.py`) : **12/12 toujours verts** (pas de régression du contrat card).
- **Broad sweep** (body_intelligence/bi01/muscle_scoring/physique/progress/body_map/body_profile/leaderboard) : **305 passed, 0 failed**.
- `check_scope` = **ISOLATED** → **promu manuellement SHARED_CODE** (router monté main.py, angle mort classifier). CI complète = source de vérité.
- ruff clean sur fichiers touchés, budget **543 ≤ 548** ; spec protocol vert.

---

## 8. Limites

- **Pas de volume par exercice** dans le drill (noms seulement) — recalcul lourd différé.
- **Zones secondaires / stabilisateurs** non représentés (corpus improvement non bloquant, différé).
- **`<details>` non persistant** : l'état ouvert/fermé n'est pas mémorisé (no-JS assumé).
- **Flag off prod** : surface invisible jusqu'à décision d'activation.

---

## 9. Next

- **Human review** attendue (docs-only).
- Ensuite (sur GO séparé) : **décision d'activation du flag** `body_intelligence_enabled` (rendre `/body/intelligence` visible en prod) · **`Sb_BI_01.next`** décision score `/physique` · volume par exercice dans le drill (recalcul, à cadrer) · dogfooding terrain.

---

## Verdict

**Verdict :** 🟢 **Sb_BI_01.2 Zone Drill Detail — DELIVERED, pending GO commit + CI + human review.**

Chaque Zone Intelligence Card gagne un **drill inline `<details>` no-JS** qui montre
les **exercices principaux** de la zone (noms, réutilisés de `ZoneScore.top_exercises`),
avec un état vide sobre « Détail insuffisant ». Disclosure natif SSR — **zéro JS**,
no-JS fallback préservé, mobile-first. **Aucun nouveau score, aucun radar, aucun
volume par exercice** (différé) ; `/physique`, Home, modèles et flag **inchangés**
(OFF prod → surface invisible) ; Auren Terminal sans nouvelle couleur. 10 tests
dédiés verts ; test `.1` intact (12/12) ; broad sweep 305 passed (0 régression) ;
ruff clean, budget 543 ≤ 548 ; spec vert.
