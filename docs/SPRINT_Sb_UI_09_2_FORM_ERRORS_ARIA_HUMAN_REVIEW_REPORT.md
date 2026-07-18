# Human Review — Sb_UI_09.2 — Form-Errors ARIA

**Verdict** : ✅ **HUMAN REVIEW: ACCEPTED**
**Type** : HUMAN REVIEW — docs-only (aucun code/template/test touché)
**Date** : 2026-07-18
**Baseline canonique** : `ac6cf20` (origin == build, aucun merge parallèle)
**Worktree** : `work/sb-ui-09-2-review` (isolé sur `ac6cf20`)

> Distinction d'état : **CODE COMPLETE** `ac6cf20` · **CI GREEN** run `29655710750` 3/3 (premier coup) ·
> **HUMAN REVIEW ACCEPTED** = le présent commit `docs(review)` séparé. 2ᵉ lot de `Sx_UI_09`.

## 1. Baseline Git
HEAD canonique = origin = `ac6cf20`, working tree clean. Aucun merge parallèle depuis le build (origin ==
build) → aucun drift possible. Aucune revue 09.2 préexistante.

## 2. Commit build audité (`ac6cf20`)
`feat(ui): announce form errors to screen readers` : **7 templates** (login/register/reset_password/
forgot_password/contact/password_change/export `.html`) + `tests/test_form_errors_a11y.py` (neuf) + 3
docs. **Template only** — aucun router/service/model/migration/data/manifest/icon/asset/JS/contrat POST/
couleur/Custom (vérifié `git diff --name-only ef3b6a1..ac6cf20`).

## 3. role="alert" sur tous les conteneurs d'erreur
**8/8 conteneurs** `.integrity-errors` portent `role="alert"` (audit markup réel) : login, register,
reset_password (×2), forgot_password, contact, password_change, export. `role="alert"` implique
`aria-live="assertive"` → l'erreur est **annoncée** au lecteur d'écran (SSR, au reload — no-JS).
(`test_every_integrity_errors_container_has_role_alert`, `test_no_integrity_errors_container_without_role`.)

## 4. login/register : id + aria-describedby conditionnel
- `login.html` : `<div class="integrity-errors" role="alert" id="login-error">` + `<form … {% if error %}
  aria-describedby="login-error"{% endif %}>`.
- `register.html` : idem `register-error`.
- **Conditionnel** (`{% if error %}`) → **aucune référence pendante** quand pas d'erreur
  (`test_describedby_is_conditional_on_error`).

## 5. Pas d'aria-invalid (choix honnête vérifié)
**0 attribut `aria-invalid="`** dans les templates (audit + `test_no_aria_invalid_added` vérifie
l'attribut, pas le mot du commentaire explicatif). Justification confirmée : l'erreur est un **message
global** (`{{ error }}`), le backend n'identifie pas le champ fautif → marquer les champs serait **faux**
(WCAG : `aria-invalid` doit refléter l'état réel). **On n'invente pas d'état par-champ.** Correct.

## 6. Preuve de rendu HTTP réel
POST login invalide (`nobody_xyz`/`wrong`) → **status 401**, HTML rendu contenant `<div
class="integrity-errors" role="alert" id="login-error">` (vérifié en conditions réelles via TestClient).
L'annonce d'accessibilité **fonctionne réellement**, pas seulement au niveau source.

## 7. Non-régression : contrat POST / champs
Contrat POST **inchangé** (`method`/`action` intacts) ; champs login (`username`/`password`/
`autocomplete="current-password"`) et register (`username`/`email`/`password`/`password_confirm`)
**intacts** (`test_login_form_contract_unchanged`, `test_register_form_contract_unchanged`) ; no-JS
(`test_no_js_added`) ; aucune couleur/style modifié (attributs ARIA uniquement).

## 8. Tests
`test_form_errors_a11y.py` (**11 tests, tous verts**) : role=alert sur chaque conteneur des 7 templates,
aucun sans role, login/register id + describedby conditionnel, **pas d'attribut aria-invalid**, no-JS,
contrats POST/champs inchangés, pas de nouvelle couleur, garantie source (7 templates livrent role=alert).
**0 test réorienté** (build purement additif → aucun test asservi cassé).

## 9. Tests locaux de revue
- Dédiés : **11 passed** (verbose vérifié critère par critère).
- Rendu HTTP réel : login échoué (401) rend `role="alert"` + `id="login-error"` (vérifié).
- Suites adjacentes (form_errors/auth/login/register/reset/forgot/contact/password/export/pwa/a11y/
  integrity/auren) : **327 passed, 0 failed** (109s).
- Garde-fous : ruff budget **543 ≤ 548** ✅ · spec_protocol ✅. Aucun test modifié durant la revue.

## 10. CI finale (run `29655710750`, SHA `ac6cf20`)
| Job | Résultat |
|---|---|
| pytest + QA scripts | ✅ success (dont Alembic drift · schema snapshot · migration patterns · migration roundtrip · perf baseline — tous **success**) |
| lint (ruff budget + bandit + actionlint + shellcheck) | ✅ success |
| SonarCloud | ✅ success |
**3/3 verte du premier coup** (aucun incident CI).

## 11. Accessibilité (WCAG)
- **4.1.3 Status Messages (AA)** : erreurs annoncées via `role="alert"`.
- **3.3.1 Error Identification** : le message d'erreur est visible + programmatiquement associé
  (`aria-describedby`) au formulaire sur login/register.
- **SSR/no-JS** : annonce au reload, pas de dépendance client.
- Choix conservateur et honnête sur `aria-invalid` (non ajouté faute d'info par-champ).

## 12. Critères d'acceptation — satisfaits
7 templates couverts ✅ · 8 conteneurs role=alert ✅ · aucun conteneur sans role ✅ · login/register id +
describedby conditionnel ✅ · 0 aria-invalid ✅ · rendu HTTP réel annonce role=alert ✅ · contrat POST/
champs/labels/couleurs inchangés ✅ · no-JS ✅ · template only, 0 backend/Custom ✅ · 11 tests dédiés verts,
0 réorienté ✅ · CI 3/3 ✅.

---

## Verdict

**Verdict :** ✅ **Sb_UI_09.2 — HUMAN REVIEW: ACCEPTED.** Les erreurs de formulaire sont **annoncées** aux
lecteurs d'écran : `role="alert"` sur les **8 conteneurs** `.integrity-errors` des **7 templates**
(login/register/reset_password/forgot_password/contact/password_change/export), + `id` et
`aria-describedby` **conditionnel** reliant le `<form>` au message sur login/register. **Pas
d'`aria-invalid`** (0 attribut vérifié) — le message est global, le backend n'identifie pas le champ
fautif ; le marquer serait faux (choix honnête, WCAG-correct). **Rendu HTTP réel prouvé** : un login
échoué (401) sert bien `role="alert"` dans le HTML. **SSR/no-JS** ; contrat POST/champs/labels/couleurs
**inchangés**. **Template only** : aucun router/service/model/migration/manifest/asset/JS/contrat/Custom.
11 tests dédiés verts, **0 réorienté**. **CI 3/3 verte** sur `ac6cf20` (premier coup). WCAG 2.2 — 4.1.3
(AA) + 3.3.1. Inspection lecteur d'écran réel = action opérateur.

**Statut** : `Sb_UI_09.2` — **CODE COMPLETE · CI GREEN · HUMAN REVIEW ACCEPTED**. Conservés :
`Sb_UI_09.3` (contrast guard) NOT OPENED · `Sx_UI_09` closeout après le dernier lot.

**Prochaine action** (non commencée) : **`GO BUILD — Sb_UI_09.3 Contrast Guard`** (test de garde des
ratios de contraste des tokens — déjà AA, à verrouiller contre régression).
