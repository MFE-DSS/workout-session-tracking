# Sprint Sx_UI_08.1 — PWA Installability Baseline

**Statut** : 🟢 DELIVERED — pending GO commit + CI + human review
**Type** : CODE BUILD — PWA / installability baseline, SSR/Jinja, no-JS safe
**Date** : 2026-07-11
**Cycle** : Sx_UI_08 (Portability / Installability)
**Préconditions** : `Sb_BI_01.activation-readiness` livré (activation deferred) ✅ ; dogfooding terrain prévu demain ✅ ; aucune surface séance/BI touchée ✅.

---

## 0. But produit

Rendre l'application plus proprement **installable** comme web app mobile, **sans**
service worker, sans offline, sans SPA, sans React, **sans changement métier** :
manifest cohérent + meta d'installabilité propres (Auren Terminal, assets existants
seulement).

---

## 1. Étape 0 — Brainstorming / Options / Choix retenu

### Options

| Option | Description | Verdict |
|---|---|---|
| **A** | Manifest/meta baseline seulement | ✅ **RETENU** |
| B | Service worker + cache statique | ❌ trop large, risque de cache stale |
| C | Offline session active | ❌ trop sensible avant dogfood, à spécifier |
| D | Refonte shell mobile | ❌ trop large, risque UI |

### 15 sujets clivants tranchés

1. **Manifest/meta seulement** (pas de service worker).
2. **Pas d'offline** maintenant.
3. **Ne pas toucher la nav.**
4. **Aucune nouvelle icône.**
5. **Assets existants seulement** (`favicon.svg`).
6. **Ne pas changer theme-color** (`#0f1115` déjà cohérent graphite Auren).
7. **Pas de pages session offline.**
8. **Pas d'apple-touch-icon** (aucun PNG asset — seul `favicon.svg` existe).
9. **Pas de maskable PNG** fabriqué (`favicon.svg` a déjà `purpose: any maskable`).
10. **Pas de screenshots PWA** (assets absents).
11. **Ne pas toucher deploy.**
12. **Ne pas toucher nginx.**
13. **Tests** sur le JSON du manifest + présence des meta dans le HTML rendu (pas de navigateur réel).
14. **Conserver** no-JS / viewport / pas de SW.
15. **Suite** : spec service worker / offline séance (futur).

**Choix : Option A** — PWA installability baseline uniquement.

### Risques / parades

| Risque | Parade |
|---|---|
| Régression SSR/no-JS | aucun `<script>`, aucun SW ; ajouts purement déclaratifs |
| Nouvelle palette | theme-color/background **inchangés** (`#0f1115`) |
| Rebrand involontaire | name/short_name du manifest **non modifiés** ; app-title = « SPIGNOS » (nom historique, cohérent avec le `<title>` existant) |
| Toucher une surface qui biaise le dogfooding séance | séance/BI/physique **hors périmètre**, non touchés |

---

## 2. Audit manifest / meta existants

**Constat : la baseline PWA existait déjà partiellement** — ce sprint la **resserre**, il ne part pas de zéro.

| Élément | Avant | Constat |
|---|---|---|
| `app/static/manifest.webmanifest` | name/short_name/start_url/scope/display(standalone)/orientation/bg/theme_color/icons | correct ; manquait `id`/`lang`/`dir` (recommandés PWA moderne) |
| `base.html` head | viewport (viewport-fit=cover), theme-color `#0f1115`, mobile-web-app-capable, apple-mobile-web-app-capable, status-bar-style, `<link rel="manifest">`, favicon.svg | correct ; manquait `apple-mobile-web-app-title` |
| Assets icons | `favicon.svg` uniquement (aucun PNG) | → pas d'apple-touch-icon PNG possible ; pas de nouvelle icône fabriquée |
| Pages auth publiques | `welcome/login/register` ont leur **propre `<head>` standalone** (n'étendent pas `base.html`) | **hors périmètre** ce sprint → limite documentée (§limites) |

---

## 3. Fichiers modifiés

| Fichier | Nature |
|---|---|
| `app/static/manifest.webmanifest` | + `id: "/"`, `lang: "fr"`, `dir: "ltr"` (recommandés PWA) ; **name/short_name/couleurs inchangés** |
| `app/templates/base.html` | + `<meta name="apple-mobile-web-app-title" content="SPIGNOS">` (titre écran d'accueil iOS, cohérent avec le `<title>` existant) |
| `tests/test_pwa_installability.py` | **nouveau** — 14 tests |

**Non modifiés** : session, exercise, body_intelligence, physique, pages.py,
services, models, migrations, static/js, service worker (aucun), deploy, nginx,
theme-color, name/short_name.

---

## 4. Ce qui a été volontairement exclu

- **service worker** / cache / offline (Option B/C — futur) ;
- **apple-touch-icon** (aucun PNG asset ; ne pas référencer un SVG non fiable) ;
- **maskable PNG** dédié (le SVG couvre `any maskable`) ;
- **screenshots PWA** (assets absents) ;
- **rename** name/short_name (« Workout Session Tracking »/« Workout ») — pas de rebrand ;
- **alignement des pages auth publiques** (welcome/login/register, head standalone) — hors périmètre, limite documentée ;
- **theme-color** changé (palette Auren validée conservée) ;
- deploy / nginx / config prod / flag.

---

## 5. Tests

### `tests/test_pwa_installability.py` (NOUVEAU, 14 tests)
1. **Manifest** : JSON valide · clés d'installabilité requises présentes et non vides · `display` installable (standalone) · start_url/scope = `/` · theme/background = graphite `#0f1115` (pas de nouvelle couleur) · icons référencent un **asset existant sur disque** · start_url résout (200/303, jamais 404).
2. **Base HTML** : référence le manifest · theme-color + viewport · mobile-web-app-capable + apple-mobile-web-app-capable + apple-mobile-web-app-title · rendu réel sur une page qui étend `base.html` (`/library` via auto-login).
3. **Non-goals** : aucun service worker référencé dans base · aucun `<script>`/registration PWA · aucun fichier service worker sous `static/`.

### Résultats
- Dédiés : **14/14 verts**.
- **Broad sweep** (pwa/template/auth/welcome/health/session/body_intelligence/physique) : **733 passed, 0 failed** — aucune régression (le layout partagé `base.html` couvert largement).
- `check_scope` = **ISOLATED** → **promu manuellement SHARED_CODE** (`base.html` est le layout partagé par ~toutes les pages). CI complète = source de vérité.
- ruff clean sur fichiers touchés, budget **543 ≤ 548** ; spec protocol vert.

---

## 6. Limites

- **Baseline seulement** : pas d'offline, pas de SW, pas de cache — l'app est
  **installable** mais pas **offline-capable** (V1 assumée).
- **Pages auth publiques** (welcome/login/register) ont un `<head>` **standalone**
  qui n'hérite pas de `base.html` → elles ne portent pas encore
  `apple-mobile-web-app-title` ni `id` de manifest resserré. **Hors périmètre** ce
  sprint (le brief cible `base.html`) — futur alignement possible.
- **Pas d'apple-touch-icon** raster (aucun PNG) — l'icône d'écran d'accueil iOS
  s'appuiera sur le `favicon.svg` / fallback système.

---

## 7. Next

- **Human review** attendue (docs-only).
- Futur (sur GO séparé) : **`Sx_UI_08.2`** spec service worker / **offline ciblé
  séance active** (Option C) — à spécifier **après** dogfooding ; alignement des
  pages auth publiques sur `base.html` (ou head partagé).

---

## Verdict

**Verdict :** 🟢 **Sx_UI_08.1 PWA Installability Baseline — DELIVERED, pending GO commit + CI + human review.**

Le manifest est **resserré** (`id`/`lang`/`dir` ajoutés, couleurs et noms
**inchangés**) et `base.html` gagne `apple-mobile-web-app-title` (« SPIGNOS », cohérent
avec le `<title>` existant, pas un rebrand). **Aucun** service worker / offline / cache
/ JS / nouvelle icône / nouvelle couleur / changement métier ; session, BI, physique,
pages.py, services, modèles, migrations, deploy, nginx **intacts** ; no-JS fallback
préservé. 14 tests dédiés verts ; ruff clean, budget 543 ≤ 548 ; spec vert. Compatible
avec le dogfooding séance de demain (aucune surface séance touchée).
