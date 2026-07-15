# Sprint Sb_UI_10.1 — Visible Product Strings (SPIGNOS → Auren) — BUILD

**Statut** : 🟢 **SAFE BUILD — DELIVERED LOCALEMENT** (LOCAL BUILD MODE, non commité)
**Type** : CODE BUILD — shell applicatif (`base.html`), template-only, SSR/no-JS
**Date** : 2026-07-15
**Spec** : `Sx_UI_10` (`49fa7d3`) — migration visible SPIGNOS → Auren
**HEAD de référence** : `49fa7d3` (rien commité par ce sprint)

---

## 0. Étape 0 — Brainstorming / Options / Choix retenu

### Décision : **SAFE BUILD — Option A** (base.html chaînes visibles only)
Migrer le **nom produit visible** SPIGNOS → **Auren** sur les 4 chaînes user-facing de `base.html`.
**Aucun** renommage code/repo/route/model/class ; **aucun** asset ; **aucun** autre fichier.

### Questions tranchées
| # | Question | Décision |
|---|---|---|
| 1 | Remplacer SPIGNOS partout ou chaînes visibles ? | **Chaînes visibles only** (4). |
| 2 | Conserver SPIGNOS dans les commentaires techniques ? | **Oui** — SPIGNOS = nom interne, documenté en commentaire (non visible). |
| 3 | `<title>` : Auren ou Auren Terminal ? | **Auren** (Terminal = identité graphique, pas le nom produit). |
| 4 | apple-title : Auren ou Auren Terminal ? | **Auren**. |
| 5 | Brand topbar : Auren ou Auren Terminal ? | **Auren** seul. |
| 6 | Footer → Auren ? | **Oui**. |
| 7 | Garder SPIGNOS visible quelque part ? | **Non** (0 SPIGNOS visible dans le shell) ; reste interne. |
| 8 | Casser tests nav/shell/PWA ? | **Non** — classes/routes préservées ; 50 tests asservis verts. |
| 9 | Incohérence avec manifest générique ? | assumée & temporaire → **`Sb_UI_10.2`** migrera le manifest. |
| 10 | Auth/welcome maintenant ? | **différé** → `Sb_UI_10.3` (welcome/login/register sont **standalone**, hors base.html). |
| 11 | Manifest maintenant ? | **différé** → `Sb_UI_10.2` (non touché ici). |
| 12 | Favicon/icons maintenant ? | **différé** → `Sb_UI_10.2` (nécessite assets). |
| 13 | Test non-réintroduction Orion ? | **oui** (`test_no_orion_string_introduced`). |
| 14 | Test non-renommage routes ? | **oui** (`test_brand_route_unchanged` : `url_for('home')` préservé). |
| 15 | Build isolé ou batch avec 10.2 ? | **isolé** (10.2 dépend d'assets non prêts). |

### Options écartées
- **B** (base + auth + manifest) : mélange plusieurs surfaces.
- **C** (rebrand code/repo) : rejet formel (non-goal).
- **D** (attendre assets) : inutile pour les chaînes visibles.

### Risque / parade critique
| Risque | Parade |
|---|---|
| Casser un test qui asservit « SPIGNOS » | **Audit** : welcome/login/register sont **standalone** (n'héritent PAS de base.html) → leurs tests (`test_auth:146`, `test_pwa_public_auth_heads` = `content="SPIGNOS"`) **inchangés**. base.html sert 37 pages authentifiées. 50 tests asservis verts. |

---

## 1. Chaînes avant / après (base.html)

| Emplacement | AVANT | APRÈS |
|---|---|---|
| `apple-mobile-web-app-title` | `content="SPIGNOS"` | `content="Auren"` |
| `<title>` | `{{ page_title }} · SPIGNOS` | `{{ page_title }} · Auren` |
| Brand topbar | `<a class="topbar__brand" …>SPIGNOS</a>` | `…>Auren</a>` |
| Footer | `<small>SPIGNOS</small>` | `<small>Auren</small>` |
| Commentaire head | « <title> existant (« · SPIGNOS ») » | mis à jour : « Nom PRODUIT VISIBLE = Auren ; SPIGNOS reste le nom interne » |

**SPIGNOS restant dans base.html** : uniquement dans **un commentaire technique** (`{# … #}`, non
rendu) qui documente que SPIGNOS = nom interne. **0 SPIGNOS visible** dans le HTML rendu.

---

## 2. Fichiers modifiés (périmètre autorisé strict)

| Fichier | Nature |
|---|---|
| `app/templates/base.html` | 4 chaînes visibles SPIGNOS → Auren + commentaire mis à jour |
| `tests/test_auren_visible_product_strings.py` | **nouveau** — 14 tests |

**Non modifiés** : routers, services, models, data, migrations, `app/static/**` (manifest/favicon/CSS/JS),
welcome/login/register, science/atlas/coach_report, `.github`, deploy. **Aucune route/classe/asset touché.**

---

## 3. Invariants préservés

- **Routes** : `url_for('home')` (brand) + toutes les `url_for(...)` de nav **inchangées** (`test_brand_route_unchanged`).
- **Classes** : `topbar__brand`, `topbar__link`, `active-banner`, footer — **inchangées**.
- **Navigation** : 9 liens + labels + état actif `aria-current` (Sx_NAV_01) **préservés** (`test_active_nav_preserved`).
- **Logout** : `<form method="post">` **inchangé**.
- **Manifest** : **non touché** (encore `"Workout Session Tracking"` — `Sb_UI_10.2`).
- **Favicon / static** : **aucun** fichier créé/modifié (`test_no_new_static_file_created` : seul `favicon.svg`).
- **Pages auth standalone** (welcome/login/register) : **non touchées** (SPIGNOS y reste, `Sb_UI_10.3`).
- **Zéro Orion** (`test_no_orion_string_introduced`).

---

## 4. Tests locaux

| Suite | Résultat |
|---|---|
| `test_auren_visible_product_strings.py` (dédiés) | **14/14** |
| Asservis critiques (nav + pwa + pwa_public_auth_heads + auth) | **50 passed / 0 cassé** |
| Sweep large (`base or nav or shell or pwa or auth or visible_product or auren`) | **386 passed / 0 échec** (83 s) |
| ruff (test neuf) | clean |
| `check_ruff_budget` | **543 ≤ 548** |
| `check_spec_protocol` | PASS |

> `check_scope` = **ISOLATED** (2 fichiers) → **promu manuellement SHARED_CODE** : `base.html` est le
> shell de **37 pages authentifiées**. Sweep 386 couvre les consommateurs ; **CI réelle = source de vérité**.

---

## 5. Risques restants

| Risque | État |
|---|---|
| **Incohérence transitoire** : shell = Auren, manifest = « Workout » | assumée → `Sb_UI_10.2` (manifest + icons). Documenté. |
| Pages auth encore « SPIGNOS » | attendu → `Sb_UI_10.3` (standalone). |
| Docs/science/atlas encore « SPIGNOS » | attendu → `Sb_UI_10.4`. |
| Due diligence nom/domaine Auren | **PENDING** (gating public, hors ce build). |

---

## 6. Chemins interdits vérifiés

✅ Aucun `app/routers/**`, `app/services/**`, `app/models/**`, `data/**`, `migrations/**`,
`app/static/**` (manifest/CSS/JS/favicon), `welcome/login/register`, `science/atlas/coach_report`,
`.github/**`, `deploy/**`. ✅ Aucune route/classe/asset touché. ✅ Zéro Orion. ✅ Body Intelligence OFF.
✅ `Delt_lat` non traité. ✅ Non commité / non poussé / CI non lancée.

---

## Verdict

**Verdict :** 🟢 **SAFE BUILD — Sb_UI_10.1 DELIVERED LOCALEMENT (non commité).**

Le nom produit **visible** migre SPIGNOS → **Auren** sur les 4 chaînes de `base.html` (apple-title,
`<title>`, brand topbar, footer) ; SPIGNOS reste le **nom interne** (documenté en commentaire, 0 SPIGNOS
visible dans le shell rendu). **Template-only** : routers / services / models / data / migrations /
static / manifest / CSS / routes / classes **intacts** ; nav + état actif + logout POST **préservés** ;
pages auth standalone (welcome/login/register) et manifest **non touchés** (différés `10.2`/`10.3`).
**Zéro Orion**, aucun asset. 14 tests dédiés + 50 asservis + sweep 386 verts. check_scope ISOLATED →
**promu SHARED_CODE** (base.html shell de 37 pages).

**Recommandation : GO COMMIT + CI complète** (surface partagée → CI réelle = source de vérité). Le shell
est le point le plus visible de la marque ; le migrer d'abord est le bon ordre. **Ne pas batcher avec
`Sb_UI_10.3`** ici (auth standalone = surface distincte, sprint séparé). Suite : `Sb_UI_10.2`
(manifest + icons Auren, **nécessite les assets**) pour résorber l'incohérence transitoire du manifest.
