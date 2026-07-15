# Sprint Sb_UI_10.3 — Public Auth / Welcome Auren Pass (SPIGNOS → Auren) — BUILD

**Statut** : 🟢 **DELIVERED LOCALEMENT — pending GO COMMIT + CI**
**Type** : CODE BUILD — surfaces publiques standalone (welcome/login/register), template-only + tests, SSR/no-JS
**Date** : 2026-07-15
**Spec** : `Sx_UI_10` — migration visible SPIGNOS → Auren (plan §split `10.1` strings → `10.2` PWA+icons → `10.3` auth/welcome → `10.4` docs/labels)
**HEAD de référence** : `dcff052` (review `Sb_UI_10.1` acceptée, poussée, CI skippée docs-only)
**Prérequis** : `Sb_UI_10.1` ✅ HUMAN REVIEW ACCEPTED (commit `e035259`, CI 3/3, 2138 passed)
**Note d'ordre** : `Sb_UI_10.2` (manifest + icons) **BLOCKED BY ASSETS** — décision opérateur 2026-07-15 : ne pas intégrer/copier dans `app/static/` avant gate assets validé. `10.3` passe devant.

---

## 0. Étape 0 — Brainstorming / Options / Risques / Choix retenu

### Décision : **strings-only sur les 3 templates standalone + réalignement des 3 assertions asservies**

### Questions tranchées

| # | Question | Décision |
|---|---|---|
| 1 | Périmètre exact | **welcome/login/register uniquement** (standalone, n'héritent pas de base.html). |
| 2 | `<title>Connexion · Workout</title>` / `Inscription · Workout` : que faire de « Workout » ? | **Migré vers `· Auren`** — « Workout » est l'ancien nom produit générique visible ; alignement sur le pattern base.html (`{{ page_title }} · Auren`). **Aucun test ne pinne « · Workout »** (vérifié par grep avant décision). |
| 3 | `<h1>SPIGNOS</h1>` du welcome | → **Auren** (brand visible principal de la landing). |
| 4 | Titre SVG a11y « Parcours SPIGNOS — de la série à la synthèse » | → **« Parcours Auren »** — copy visible (lue par lecteurs d'écran) ; la `<desc>` ne contient pas SPIGNOS, inchangée. |
| 5 | Tests asservis pinnant SPIGNOS (`test_pwa_public_auth_heads` ×2, `test_auth:146`) | **Mis à jour dans ce sprint** — leur invariant (« no rebrand *by this sprint* », Sx_UI_08.2) est précisément levé par `10.3`. `test_auth_titles_unchanged_no_rebrand` **renommé** `test_auth_titles_auren_product_name` (l'ancien nom aurait menti). |
| 6 | Lede « Private bodybuilding tracking cockpit. » | **Conservée** (pas de SPIGNOS ; réécriture copy = hors périmètre). |
| 7 | Commentaires de head | Note `Sb_UI_10.3` ajoutée aux 3 heads (précédent `10.1` : documenter SPIGNOS = nom interne). |
| 8 | Manifest / icons / favicon | **Non touchés** — bloqués par le gate assets (`10.2`). |
| 9 | CSS | **0 modification** (nécessité non prouvée ; styles inline existants inchangés). |
| 10 | science/atlas/coach_report | **Non touchés** — réservés `Sb_UI_10.4`. |

### Options écartées
- **B** (batcher avec le manifest/icons) : violé le gate assets — rejeté.
- **C** (réécrire la copy welcome en même temps) : mélange rebrand et rédaction produit — rejeté.
- **D** (garder « · Workout » dans les titles) : laisserait un 3e nom produit visible (Workout ≠ SPIGNOS ≠ Auren) — incohérence pire que le statu quo.

### Risque / parade critique

| Risque | Parade |
|---|---|
| Casser les tests asservis qui exigeaient SPIGNOS sur ces pages | Les 3 assertions identifiées **avant** le build (grep exhaustif `SPIGNOS` dans `tests/`) et réalignées dans le même diff ; `test_science_page` (« Comment SPIGNOS materialise ») et `test_reco_calibration_report` (stdout script) **hors périmètre, non touchés, verts**. |
| Régression formulaire/route auth | Tests sentinelles dédiés (form actions `url_for('login_submit')`/`register_submit`, names `username`/`password`/`password_confirm`/`email`, blocs error/password_reset, labels fonctionnels) + 180 tests sweep auth/pwa verts. |

---

## 1. Chaînes avant / après

| Fichier | Emplacement | AVANT | APRÈS |
|---|---|---|---|
| welcome.html | `apple-mobile-web-app-title` | `content="SPIGNOS"` | `content="Auren"` |
| welcome.html | `<title>` | `SPIGNOS` | `Auren` |
| welcome.html | `<h1 class="page-title">` | `SPIGNOS` | `Auren` |
| welcome.html | SVG `<title id="journey-title">` | `Parcours SPIGNOS — …` | `Parcours Auren — …` |
| login.html | `apple-mobile-web-app-title` | `content="SPIGNOS"` | `content="Auren"` |
| login.html | `<title>` | `Connexion · Workout` | `Connexion · Auren` |
| register.html | `apple-mobile-web-app-title` | `content="SPIGNOS"` | `content="Auren"` |
| register.html | `<title>` | `Inscription · Workout` | `Inscription · Auren` |
| ×3 heads | commentaire Jinja | note Sx_UI_08.2 | + note `Sb_UI_10.3` (SPIGNOS = nom interne) |

**SPIGNOS restant dans ces 3 templates** : uniquement dans les commentaires Jinja
(`{# … #}`, strippés au rendu). **0 SPIGNOS rendu** sur /welcome, /login, /register
(prouvé par tests sur HTML rendu, client anonyme réel).

---

## 2. Fichiers modifiés

| Fichier | Nature |
|---|---|
| `app/templates/welcome.html` | 4 chaînes visibles + commentaire (13 lignes) |
| `app/templates/login.html` | 2 chaînes visibles + commentaire (9 lignes) |
| `app/templates/register.html` | 2 chaînes visibles + commentaire (9 lignes) |
| `tests/test_auren_public_auth_strings.py` | **nouveau** — 14 tests dédiés *(« 15 » initialement annoncé : erreur de comptage, corrigée en review — CI 2138 + 14 = 2152)* |
| `tests/test_pwa_public_auth_heads.py` | 2 assertions réalignées (apple-title Auren ; titles Auren) + renommage honnête du test no-rebrand |
| `tests/test_auth.py` | 1 assertion réalignée (welcome affiche Auren) |

**Non modifiés** : manifest.webmanifest, `app/static/**` (icons/CSS/JS), routers/services/
models/data/migrations, base.html, science/atlas/coach_report, `.github`, deploy,
branche `spec/sx-custom-program-01-intelligent-builder`. **Aucun asset introduit.**

---

## 3. Invariants préservés

- **Routes** : `/welcome`, `/login`, `/register` inchangées ; `url_for('login_submit')`,
  `url_for('register_submit')`, `url_for('login_page')`, `url_for('register_page')`,
  `url_for('public_landing')` **intacts** (`test_form_actions_point_at_same_routes`).
- **Formulaires** : method POST, inputs `username`/`password`/`password_confirm`/`email`
  (names, required, autocomplete, minlength), boutons submit — **byte-identiques**.
- **Messages** : blocs `{% if error %}` et `success == "password_reset"` **intacts**.
- **Labels fonctionnels** : « Connexion », « Se connecter », « Inscription »,
  « Créer le compte », « Créer un compte », « Mot de passe oublié ? » **conservés**.
- **PWA head** : meta d'installabilité (Sx_UI_08.2) conservées ; seul le `content` de
  l'apple-title change (remplacement strict SPIGNOS → Auren) ; manifest ref + favicon.svg
  identiques ; **aucun apple-touch-icon**, aucun `<script>` (SSR/no-JS).
- **Zéro Orion** (test dédié, 3 templates).

---

## 4. Tests & checks locaux

| Suite | Résultat |
|---|---|
| `test_auren_public_auth_strings.py` (dédiés, **nouveau**) | **14/14** |
| Fichiers directement affectés (dédiés + pwa_heads + auth) | **35 passed / 0 échec** (12,6 s) |
| Sweep ciblé `-k "auth or welcome or pwa or login or register or auren or public"` | **180 passed / 0 échec** (66 s) |
| ruff (fichier de tests neuf) | clean |
| `check_ruff_budget` | **543 ≤ 548** |
| `check_spec_protocol` | PASS |

> `check_scope` = **ISOLATED** (6 fichiers : 3 templates standalone non importés + 3 fichiers
> tests leaf) — verdict **honnête et conservé** : contrairement à `10.1` (base.html = shell de
> 37 pages, promu SHARED_CODE), la surface est bornée à **3 pages publiques standalone** dont
> les consommateurs directs (router auth, tests pwa/auth) sont couverts par le sweep ciblé 180.
> Pas de full sweep local (contrat anti-overcheck) ; **CI complète au push = source de vérité**
> (code/template touché ⇒ CI 3 jobs obligatoire, aucun `[skip ci]`).

---

## 5. Risques restants

| Risque | État |
|---|---|
| Incohérence transitoire : pages publiques = Auren, manifest = « Workout Session Tracking » | assumée, **identique à celle du shell depuis `10.1`** → résorbée par `Sb_UI_10.2` (BLOCKED BY ASSETS). |
| science/atlas/coach_report encore « SPIGNOS » | attendu → `Sb_UI_10.4`. |
| Due diligence nom/domaine Auren | **PENDING** (gating public, hors builds). |
| Screenshot/App icon iOS encore générique | dépend des assets (`10.2`). |

---

## 6. Chemins interdits vérifiés

✅ Aucun `manifest.webmanifest`, `app/static/icons/`, CSS, routers/services/models/data/
migrations, renommage repo/modules/routes/env/tables, logique auth, formulaire fonctionnel,
route `/welcome`/`/login`/`/register`. ✅ `Sb_UI_10.4` non ouvert. ✅ Branche Custom Program
non touchée. ✅ Aucun deploy. ✅ Zéro Orion. ✅ Aucun asset.

---

## Verdict

**Verdict :** 🟢 **Sb_UI_10.3 DELIVERED LOCALEMENT — pending GO COMMIT + CI.**

Les 3 surfaces publiques standalone (welcome/login/register) affichent désormais **Auren**
(8 chaînes visibles migrées, dont les 2 titles legacy « · Workout ») ; SPIGNOS reste le nom
interne (commentaires techniques uniquement, 0 rendu). **Strings-only/template-only** :
formulaires, routes, messages d'erreur, meta PWA, manifest, assets, CSS **intacts** —
prouvé par 14 tests dédiés + sentinelles + 180 tests sweep auth/pwa verts. Les 3 assertions
asservies qui pinnaient SPIGNOS (invariant Sx_UI_08.2 « no rebrand by this sprint ») sont
réalignées honnêtement dans le même diff. check_scope ISOLATED (surface bornée, non promue —
justification §4). **Recommandation : GO COMMIT + CI complète** (template + tests touchés).
Suite : `Sb_UI_10.2` dès gate assets validé ; `Sb_UI_10.4` (docs/labels) ensuite.
