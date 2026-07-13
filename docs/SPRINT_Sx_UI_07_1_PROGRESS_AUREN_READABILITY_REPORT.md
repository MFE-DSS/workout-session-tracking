# Sprint Sx_UI_07.1 — Progress Surface Auren Readability

**Statut** : 🟢 DELIVERED — pending GO commit + CI + human review
**Type** : CODE BUILD — visual/product readability pass on `/progress`, SSR/Jinja, no-JS safe
**Date** : 2026-07-11
**Cycle** : Sx_UI_07 (History & Progress)
**Préconditions** : `Sx_UI_08.2` HUMAN REVIEW ACCEPTED ✅ ; BI activation deferred ✅ ; dogfooding peut être différé ✅ ; aucune surface session/BI/physique/service touchée ✅.

---

## 0. But produit

Faire évoluer `/progress` vers une lecture **Auren plus calme, hiérarchisée,
actionnable**, **sans toucher au calcul métier** : mieux représenter ce qui existe
déjà (hiérarchie plus claire, microcopy non opaque, moins cockpit KPI, plus
instrument calme, mobile-first). **Aucune nouvelle intelligence.**

---

## 1. Étape 0 — Brainstorming / Options / Choix retenu

### Options

| Option | Description | Verdict |
|---|---|---|
| **A** | Template-only readability pass | ✅ **RETENU** |
| B | Template + CSS dédié minimal | ❌ non nécessaire (classes existantes suffisent) |
| C | Changer les calculs KPIs | ❌ hors périmètre |
| D | Nouvelle route Progress v2 | ❌ trop large |

### 15 sujets clivants tranchés

1. **`/progress` conservé** (pas de nouvelle route).
2. **Template-only** (pas de routeur, pas de service).
3. **Weekly loop conservé en haut** (« ce qui compte maintenant »).
4. **KPI cards conservés** mais regroupés sous un header « Rythme récent » (moins cockpit).
5. **Labels clarifiés** + note d'encadrement ; **valeurs inchangées**.
6. **Lede plus utile** (microcopy recommandée).
7. **Ordre conservé** (Par programme / Activité récente / timelines) — timelines **non déplacées**.
8. **Ne pas toucher `kpis.py`.**
9. **Ne pas toucher `timeline.py`.**
10. **Pas de lien BI.**
11. **Pas de lien `/physique`.**
12. **Pas de JS.**
13. **Pas de CSS dédié** (classes `page-title`/`lede`/`kpi-grid`/`card`/`section-header`/`kpi-note` déjà dans app.css) → **Option A pure**.
14. **Mobile-first préservé** (classes responsive existantes) ; pas de re-densification.
15. **Suite** : History Surface Auren Readability.

**Choix : Option A pure** — template-only, aucun service/routeur/CSS touché.

### Risques / parades

| Risque | Parade |
|---|---|
| Changer une valeur métier par inadvertance | diff prouve : **aucune expression `{{ kpis.* }}`/`{{ tk.* }}`/`svg` modifiée**, seuls libellés statiques |
| Toucher un service | `kpis.py`/`timeline.py`/`weekly_loop.py` **non ouverts** ; tests sentinelles |
| Re-densifier | +10/-6 lignes, header de section léger, aucune donnée ajoutée |
| Introduire une classe CSS manquante | `section-header` **existe déjà** dans app.css (réutilisée) |

---

## 2. Audit de la page existante

`progress.html` (123 lignes, étend `base.html`) contenait déjà, dans l'ordre :
titre + lede · weekly_loop (partial) · kpi-grid (4 cards) · cockpit-grid (Par
programme / Activité récente par exercice) · timeline Qualité (conditionnelle) ·
timeline Poids corporel (conditionnelle) · note technique. **Tous les blocs sont
conservés.**

---

## 3. Fichiers modifiés

| Fichier | Nature |
|---|---|
| `app/templates/progress.html` | re-hiérarchie + microcopy (10 insertions / 6 suppressions) — **libellés statiques uniquement** |
| `tests/test_progress_auren_readability.py` | **nouveau** — 11 tests |

**Non modifiés** : `kpis.py`, `timeline.py`, `weekly_loop.py`, `performance.py`,
`muscle_scoring.py`, `pages.py` (**Option A pure, aucun routeur touché**), session,
exercise, body_intelligence, physique, index.html, models, migrations, static/js,
app.css (aucune nouvelle règle). Aucune nouvelle couleur.

---

## 4. Changements de hiérarchie / microcopy

| Élément | Avant | Après |
|---|---|---|
| Lede | « KPI · sessions terminées. » | « **Lecture des séances terminées, de la régularité et des signaux récents.** » |
| Section KPI | (grille sans header) | + header **« Rythme récent »** (lecture d'entraînement, pas cockpit) |
| Labels KPI « sessions cette semaine » / « sessions terminées (30 j) » | inchangés | **conservés** (voir §limites — évite de casser des assertions textuelles de `test_kpis.py`, hors périmètre) |
| Timeline qualité | « Qualité de séance dans le temps » | « **Qualité des séances** » |
| Timeline poids | « Poids corporel dans le temps » | « **Poids corporel** » |
| Note technique | « Sessions terminées uniquement · warmup sets exclus · prescrits = … » | « **Lecture indicative** · séances terminées uniquement · warmup exclus · prescrits = … » |

Weekly loop, KPI values, « Par programme », « Activité récente par exercice »,
timelines (SVG), liens exercice : **inchangés**.

---

## 5. Preuves que les calculs ne changent pas

- **Diff** : aucune expression Jinja de données (`{{ kpis.* }}`, `{{ tk.* }}`,
  `{{ a.* }}`, `quality_svg`, `bodyweight_svg`) ajoutée/modifiée — vérifié par grep sur
  le diff (seuls libellés statiques + un `<h2 class="section-header">`).
- **Services intacts** : `kpis.py`/`timeline.py`/`weekly_loop.py` **non ouverts** ;
  tests sentinelles (`test_kpi_and_timeline_services_not_modified`).
- **Routeur intact** : `pages.py` **non touché** (`test_router_not_required_for_readability`).

---

## 6. Tests

### `tests/test_progress_auren_readability.py` (NOUVEAU, 11 tests)
1. **Rendu** (client auth) : `/progress` → 200 · titre « Progression » · nouveau lede ·
   weekly loop + kpi-grid + « Rythme récent » · labels « séances » · « Par programme » +
   « Activité récente » · note « Lecture indicative » · titres timelines calmes (si SVG).
2. **Non-régression** : services KPI/timeline/weekly **non modifiés** · `pages.py` non
   requis · physique/index/BI templates non touchés.
3. **Non-goals** : pas de JS · pas de lien BI/physique ajouté · wording interdit absent.

### Résultats
- Dédiés : **11/11 verts**.
- **Broad sweep** (progress/kpis/timeline/weekly/history/pwa/auth) : **232 passed, 0 failed** — aucune régression (dont `test_kpis.py` 7/7 après conservation des labels « sessions »). Sweep large initial (`+template`) : 828 passed après le fix des 2 assertions textuelles.
- `check_scope` = **ISOLATED** — **correct** (`progress.html` est une page unique, pas un layout partagé ; `pages.py` non touché). Broad sweep exécuté par prudence.
- ruff clean sur fichiers touchés, budget **543 ≤ 548** ; spec protocol vert.

---

## 7. Limites

- **Labels KPI « sessions » conservés** : un premier essai renommait « sessions » →
  « séances » (cohérence FR), mais 2 assertions textuelles préexistantes de
  `test_kpis.py` (hors périmètre autorisé) y sont asservies. **Décision opérateur** :
  garder « sessions » sur ces 2 labels pour rester **strictement dans le périmètre**
  (`progress.html` seul, `test_kpis.py` non modifié). Le reste de la microcopy
  (lede, « Rythme récent », titres timelines, note « Lecture indicative ») est
  appliqué. Un alignement FR complet serait un futur sprint touchant aussi ces tests.
- **Readability pass seulement** : aucune nouvelle métrique, aucun tri/filtre
  interactif (pas de JS) ; la structure des sections reste proche de l'existant.
- **Timelines non déplacées** (l'ordre est conservé pour éviter tout risque de
  régression visuelle) — un re-agencement plus profond serait un sprint dédié.
- **Pas de lien BI / `/physique`** (interdit ce sprint) — la mise en relation des
  surfaces reste future.

---

## 8. Next

- **Human review** attendue (docs-only).
- Futur (sur GO séparé) : **`Sx_UI_07.2`** History Surface Auren Readability (même
  approche template-only sur `/history`), ou **Progress advanced metrics spec** (si
  de nouvelles métriques sont voulues — nécessiterait de toucher les services, donc
  une spec dédiée d'abord).

---

## Verdict

**Verdict :** 🟢 **Sx_UI_07.1 Progress Surface Auren Readability — DELIVERED, pending GO commit + CI + human review.**

`/progress` gagne une **lecture plus calme et hiérarchisée** (lede utile, section
« Rythme récent », labels clarifiés, titres timelines sobres, note « Lecture
indicative ») **sans changer une seule valeur ni un service** : `kpis.py`,
`timeline.py`, `weekly_loop.py`, `pages.py` **non touchés** (Option A pure) ; tous les
blocs (weekly loop, KPI, Par programme, Activité récente, timelines, note) conservés ;
aucun JS / nouveau score / lien BI-physique / nouvelle couleur / rebrand ; session, BI,
physique, Home, modèles, migrations **intacts**. 11 tests dédiés verts ; ruff clean,
budget 543 ≤ 548 ; spec vert.
