# Sprint Sx_UI_08.2 — Public Auth Heads Alignment

**Statut** : 🟢 DELIVERED — pending GO commit + CI + human review
**Type** : CODE BUILD — PWA / public auth head alignment, SSR/Jinja, no-JS safe
**Date** : 2026-07-11
**Cycle** : Sx_UI_08 (Portability / Installability)
**Préconditions** : `Sx_UI_08.1` HUMAN REVIEW ACCEPTED ✅ (validé `af6e620`) ; dogfooding terrain prévu demain ✅ ; aucune surface séance/BI/physique/service touchée ✅.

---

## 0. But produit

Aligner les pages publiques d'authentification (`/welcome`, `/login`, `/register`)
qui ont encore un `<head>` **standalone** (elles n'étendent pas `base.html`) sur la
**baseline PWA** de `Sx_UI_08.1`, pour que l'expérience installable soit cohérente
partout — **sans refactor lourd**, sans toucher formulaires/routes/wording/couleurs.

---

## 1. Étape 0 — Brainstorming / Options / Choix retenu

### Options

| Option | Description | Verdict |
|---|---|---|
| **A** | Patch minimal des heads publics (3 templates) | ✅ **RETENU** |
| B | Créer un partial head partagé | ❌ différé (plus propre à terme mais plus invasif) |
| C | Faire hériter welcome/login/register de `base.html` | ❌ trop large, risque layout/UX auth |
| D | Ajouter service worker / offline | ❌ hors périmètre |

### 15 sujets clivants tranchés

1. **Patcher les 3 templates** (pas de partial partagé — Option B différée).
2. **Conserver les templates standalone** (pas d'héritage base.html — Option C rejeté).
3. **Minimum cohérent** avec base.html (manifest + meta installabilité).
4. **Titre visible inchangé** (les `<title>` restent tels quels).
5. **Pas de rebrand** SPIGNOS → Auren.
6. **Pas d'apple-touch-icon** (aucun PNG asset).
7. **Pas de service worker.**
8. **Pas d'offline/cache.**
9. **Ne pas toucher les formulaires.**
10. **Ne pas toucher les routes.**
11. **Ne pas toucher les CSS.**
12. **Tests sur rendu réel HTTP** (200 + meta) — pages publiques via client non-authentifié.
13. **Vérifier le link manifest** (pas de lien cassé).
14. **Vérifier aucune régression** login/register/welcome (form intact).
15. **Suite** : `Sx_UI_08.3` service worker / offline spec (pas build).

**Choix : Option A** — alignement minimal des heads standalone auth publics.

### Risques / parades

| Risque | Parade |
|---|---|
| Casser un formulaire auth | ne toucher que le `<head>` ; tests « form intact » |
| Rebrand involontaire | `<title>` visibles **inchangés** ; app-title = « SPIGNOS » (nom historique) |
| Lien manifest cassé | même chemin que base.html (`manifest.webmanifest`) ; test de présence |
| Toucher base.html/manifest | **hors périmètre** — non modifiés (tests sentinelles) |

---

## 2. Audit des heads auth existants

**Constat** : les 3 pages ont **déjà** `viewport` + `theme-color` `#0f1115`, mais
**manquent** : manifest, mobile-web-app-capable, apple-mobile-web-app-capable,
status-bar-style, apple-mobile-web-app-title, favicon.

| Page | Avant | Manque comblé |
|---|---|---|
| `welcome.html` | viewport, theme-color, `<title>SPIGNOS</title>` | manifest + 4 meta apple/mobile + favicon |
| `login.html` | viewport, theme-color, `<title>Connexion · Workout</title>` | idem |
| `register.html` | viewport, theme-color, `<title>Inscription · Workout</title>` | idem |

---

## 3. Fichiers modifiés

| Fichier | Nature |
|---|---|
| `app/templates/welcome.html` | + bloc meta PWA (mobile-web-app-capable, apple-mobile-web-app-capable, status-bar-style, apple-mobile-web-app-title="SPIGNOS", `<link rel="manifest">`, favicon.svg) |
| `app/templates/login.html` | idem (bloc identique) |
| `app/templates/register.html` | idem (bloc identique) |
| `tests/test_pwa_public_auth_heads.py` | **nouveau** — 9 tests |

**Non modifiés** : `base.html`, `manifest.webmanifest`, routers, services, models,
migrations, static/js, session, exercise, body_intelligence, physique, deploy,
nginx. **Formulaires / routes / wording visible / couleurs inchangés.**

---

## 4. Meta ajoutées (par page)

```
<meta name="mobile-web-app-capable" content="yes" />
<meta name="apple-mobile-web-app-capable" content="yes" />
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
<meta name="apple-mobile-web-app-title" content="SPIGNOS" />
<link rel="manifest" href="{{ url_for('static', path='manifest.webmanifest') }}" />
<link rel="icon" href="{{ url_for('static', path='icons/favicon.svg') }}" type="image/svg+xml" />
```

Bloc **identique** à `base.html` (Sx_UI_08.1). viewport + theme-color déjà présents,
non dupliqués. Aucun apple-touch-icon (pas de PNG).

---

## 5. Non-goals respectés

Pas de : changement de formulaire · de route · de wording visible · de couleur ·
apple-touch-icon · service worker · JS · offline/cache · rebrand · modification
`base.html`/manifest · surface séance/BI/physique · service/modèle/migration ·
deploy/nginx/config prod.

---

## 6. Tests

### `tests/test_pwa_public_auth_heads.py` (NOUVEAU, 9 tests)
- **rendu réel HTTP** (client **non-authentifié** — ces pages redirigent 303 si loggé) :
  `/welcome`, `/login`, `/register` → **200** + toutes les meta d'installabilité + manifest ;
- **formulaires intacts** : login/register conservent `<form method="post">` + `username`/`password`/submit ;
- **non-goals** : aucun `<script>`/service worker dans les templates · pas d'apple-touch-icon ·
  les 3 pointent le **même** manifest · `<title>` **non rebrandés** · manifest **non modifié** (JSON valide, `#0f1115`, standalone).

### Résultats
- Dédiés : **9/9 verts**.
- **Broad sweep** (pwa/auth/welcome/login/register/template/session/body_intelligence/physique) : **760 passed, 0 failed** — aucune régression (+ sweep ciblé auth/pwa **118 passed**).
- `check_scope` = **ISOLATED** — **correct ici** (les 3 templates sont réellement standalone, aucun layout partagé) ; pas de promotion SHARED_CODE. Broad sweep exécuté par prudence (pages publiques).
- ruff clean sur fichiers touchés, budget **543 ≤ 548** ; spec protocol vert.

---

## 7. Limites

- **Duplication assumée** : le bloc meta est répété dans 3 templates standalone. Un
  **partial head partagé** (Option B) serait plus DRY — différé pour éviter un
  refactor de `base.html`/auth plus large.
- **Pas d'offline / SW** : cohérence d'installabilité seulement, pas de capacité
  offline (V1 assumée, comme `.1`).
- **Pas d'apple-touch-icon** (aucun PNG asset).

---

## 8. Next

- **Human review** attendue (docs-only).
- Futur (sur GO séparé) : **`Sx_UI_08.3`** — **spec** service worker / offline ciblé
  séance active (spec, **pas build**), à cadrer **après** dogfooding. Éventuel
  refactor partial head partagé (Option B) si la duplication devient gênante.

---

## Verdict

**Verdict :** 🟢 **Sx_UI_08.2 Public Auth Heads Alignment — DELIVERED, pending GO commit + CI + human review.**

Les 3 pages publiques d'authentification (`welcome`/`login`/`register`, heads
standalone) sont **alignées** sur la baseline PWA de `.1` : manifest + meta
d'installabilité + favicon, bloc **identique** à `base.html`. **Aucun** changement de
formulaire / route / wording visible / couleur ; **pas** de service worker / offline /
JS / apple-touch-icon / rebrand ; `base.html` et `manifest.webmanifest`
**non modifiés** ; no-JS fallback préservé. 9 tests dédiés verts (rendu réel HTTP
non-authentifié) ; ruff clean, budget 543 ≤ 548 ; spec vert. Compatible avec le
dogfooding séance de demain (aucune surface séance/BI/physique touchée).
