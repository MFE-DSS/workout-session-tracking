# Sprint Sx_NAV_01 — Active Navigation Semantics

**Statut** : 🟢 DELIVERED LOCALEMENT — **NON commité, NON poussé, CI non lancée** (LOCAL BATCH MODE)
**Type** : CODE BUILD — shared shell accessibility / active navigation, SSR/Jinja, no-JS
**Date** : 2026-07-13
**Cycle** : batch local (à la suite de CAT_01 / FB_01 / SUB_01 / CLOSEOUT_01 / 07.3 / 07.4 / 07_CLOSEOUT / TPL_01 / LIB_01 — préservés)
**HEAD de référence** : `b60e749`

---

## 0. But produit

Rendre la navigation globale plus lisible : l'utilisateur **sait sur quelle grande
surface il se trouve** ; le lien courant expose **`aria-current="page"`** ; le shell
reste **SSR / no-JS / mobile-first**. Aucune route/service/donnée/page métier touchée.

---

## 1. Étape 0 — Brainstorming / Options / Choix retenu

### Options

| Option | Description | Verdict |
|---|---|---|
| **A** | Template-only, `request.url.path`, `aria-current` + classe `is-active` | ✅ **RETENU** |
| B | Ajouter `active_nav` dans chaque route | ❌ touche beaucoup de routes |
| C | CSS visible minimal | ⚠️ retenu **minimal** (var existante, pas de nouvelle couleur) |
| D | `aria-current` seul (zéro CSS) | ❌ moins visible ; le style minimal via `var(--fg)` est safe |

### 15 sujets clivants tranchés

1. **État actif global** (via `request.url.path`).
2. **`request.url.path` en Jinja** (pas de `active_nav` dans les routes).
3. **`pages.py` non modifié** (template-only).
4. **`aria-current="page"` + classe `is-active`**.
5. **CSS minimal** `.topbar__link.is-active` réutilisant `var(--fg)` (pas de nouvelle couleur).
6. **`/library/{slug}` → Programmes actif** (`startswith('/library')`).
7. **`/sessions/{id}` → aucun actif** (pas dans la topbar).
8. **`/body/intelligence` → Physique actif** (regroupé avec `/physique`).
9. **`/progress` → Progression actif.**
10. **`/coach…` → Coach actif** (`startswith('/coach')` matche `/coach-report`).
11. **Pages auth standalone non touchées** (n'étendent pas `base.html`).
12. Tests asservis topbar **préservés** (labels).
13. **Mobile details menu** inchangé (`<details class="topbar__menu">`).
14. **Pas de JS.**
15. **Suite** : recommandation §9.

**Choix : Option A** + CSS minimal `var(--fg)`.

### Risque / parade critique

| Risque | Parade |
|---|---|
| Conflit avec `aria-current="location"` du header de séance (`test_session_focus_header_structure` interdit `="false"`/`="step"`) | approche **conditionnelle** : liens non actifs = **aucun** `aria-current` (jamais `"false"`) ; valeur `"page"` distincte de `"location"`/`"step"`. **65 tests aria-current re-joués verts.** |

---

## 2. Mapping route → nav actif

Bloc `{% set %}` en tête (SSR, `request.url.path`) :

| Variable | Condition | Lien topbar |
|---|---|---|
| `is_home` | `== '/'` ou `startswith('/home')` | Accueil |
| `is_programs` | `startswith('/library')` ou `startswith('/launcher')` | Programmes |
| `is_history` | `startswith('/history')` | Historique |
| `is_physique` | `startswith('/physique')` ou `startswith('/body/intelligence')` | Physique |
| `is_progress` | `startswith('/progress')` | Progression |
| `is_leaderboard` | `startswith('/leaderboard')` | Classement |
| `is_squads` | `startswith('/squads')` | Squads |
| `is_profile` | `startswith('/profile')` | Profil |
| `is_coach` | `startswith('/coach')` | Coach |

Chaque lien : `class="topbar__link {% if is_x %}is-active{% endif %}"` +
`{% if is_x %}aria-current="page"{% endif %}`.

**Rendu vérifié** (9 routes) : exactement **1** `aria-current="page"` par route, sur le
bon lien ; `is-active` sur le bon label ; **jamais** `aria-current="false"`.
`/library/push-a` + `/launcher` → Programmes.

---

## 3. Fichiers modifiés

| Fichier | Nature |
|---|---|
| `app/templates/base.html` | + bloc `{% set %}` mapping + `is-active`/`aria-current` conditionnels sur les 9 liens topbar |
| `app/static/css/app.css` | + `.topbar__link.is-active { color: var(--fg); font-weight: 600; }` (1 règle, var existante) |
| `tests/test_active_navigation_semantics.py` | **nouveau** — 15 tests |

**Non modifiés** : routers, services, data (`reference_split.json` = CAT_01), library/
launcher/template_detail (07.3/07.4/TPL_01/LIB_01), session/progress/history/index/BI/
physique templates, models, migrations. **Pages auth standalone non touchées** (head
standalone, n'étendent pas base.html).

---

## 4. Preuve — routes/services/data inchangés

- **Diff** : `base.html` (mapping + attributs conditionnels) + `app.css` (1 règle) uniquement.
- **`pages.py` non ouvert** (test sentinelle : `is_programs`/`active_nav` absents du routeur).
- Aucune route/service/data touché ; l'état actif est **dérivé du path côté template**.

---

## 5. Preuve — topbar/logout/banner préservés

- **9 liens** (Accueil/Programmes/Historique/Physique/Progression/Classement/Squads/Profil/Coach) + labels **conservés** (test `test_all_nav_links_and_logout_preserved`).
- **Logout** reste un `<form method="post">` (bouton `topbar__link--btn`).
- **`active-banner`** (session en cours) **inchangée** (hors du bloc modifié).
- **Brand** `topbar__brand` SPIGNOS conservé · manifest/head/PWA (Sx_UI_08.1) intacts · footer intact.

---

## 6. CSS ajouté (minimal, scopé)

```css
.topbar__link.is-active { color: var(--fg); font-weight: 600; }
```

- Réutilise **`var(--fg)`** (la couleur pleine, comme `:hover`) → **aucune nouvelle
  couleur**, aucune ombre, aucun rebrand. `font-weight: 600` pour la lisibilité de
  l'état actif. Test `test_active_css_reuses_existing_variable` (var(--fg), pas de hex).

---

## 7. Tests locaux

### `tests/test_active_navigation_semantics.py` (NOUVEAU, 15 tests)
- **surface → lien actif** : `/`→Accueil, `/library`→Programmes, `/library/{slug}`→Programmes, `/launcher`→Programmes, `/history`→Historique, `/progress`→Progression, `/physique`→Physique, `/leaderboard`→Classement.
- **exactement 1** `aria-current="page"` par route · **jamais** `="false"`/`="step"`.
- **shell préservé** : 9 liens + logout POST + brand.
- **non-goals** : `request.url.path` (pas de router), pas de JS, CSS réutilise `var(--fg)`, `pages.py` non modifié.

### Résultats locaux
- Dédiés : **15/15 verts**.
- **Tests asservis aria-current** (`test_session_focus_header_structure`, `_accessibility`, `_cockpit`, `test_squad_routes`) : **65 passed** — 0 cassé (pas de conflit avec `aria-current="location"`).
- **Broad sweep** (home/library/launcher/template_detail/history/progress/physique/profile/coach/auth) : **532 passed, 0 échec** (196 s) — le shell partagé `base.html` ne régresse aucune surface consommatrice.
- `check_scope` = **ISOLATED** → **promu manuellement SHARED_CODE** (`base.html` est le layout partagé par ~toutes les pages). CI complète = source de vérité.
- ruff clean sur fichiers touchés, budget **543 ≤ 548** ; spec vert.

> **LOCAL BATCH MODE** : rapide, pas de full suite, pas de CI. Aucun commit/push.

---

## 8. Limites

- **`/sessions/{id}`** ne marque aucun lien topbar actif (la séance n'est pas une
  entrée de nav — c'est cohérent, la topbar est masquée/secondaire en focus séance).
- **Style minimal** : l'état actif = couleur pleine + gras. Un design plus marqué
  (soulignement, accent ambre) serait un choix esthétique dédié — évité ici.
- **Pages auth publiques** : head standalone, pas de topbar → pas concernées.

---

## 9. Impact batch & recommandation

Ce sprint ajoute **base.html + 1 règle CSS + 1 test** au batch. Le batch touche
maintenant aussi le **shell partagé** (base.html) → au commit, ce changement sera
**SHARED_CODE** et la CI complète sera la source de vérité. Le **plan de commit**
(closeout) doit inclure `base.html`, `app.css`, `test_active_navigation_semantics.py` +
ce rapport dans le **commit code**.

**Recommandation finale : GO BATCH COMMIT + CI complète.** Le batch touche désormais le
shell global (base.html) — c'est un argument **de plus** pour le sécuriser via la CI
réelle sans tarder.

---

## Verdict

**Verdict :** 🟢 **Sx_NAV_01 Active Navigation Semantics — DELIVERED LOCALEMENT (batch, non commité).**

La topbar partagée (`base.html`) expose désormais un **état actif** dérivé de
`request.url.path` : le lien de la surface courante porte `is-active` +
`aria-current="page"` (exactement un par route, jamais `"false"`) — SSR, no-JS,
mobile-first. **Template-only** : routers/services/data **inchangés** ; 9 liens + logout
POST + active-banner + brand + PWA **préservés** ; CSS minimal réutilisant `var(--fg)`
(aucune nouvelle couleur). Pas de conflit avec l'`aria-current="location"` du header de
séance (65 tests verts). 15 tests dédiés ; broad sweep vert. `check_scope` isolated →
**promu SHARED_CODE** (base.html partagé). ruff clean ; spec vert. Batch préservé.
Recommandation : **GO BATCH COMMIT + CI**.
