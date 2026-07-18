# Sprint Sb_UI_09.2 — Form-Errors ARIA — BUILD REPORT

**Statut** : 🟢 **CODE COMPLETE — CI PENDING — HUMAN REVIEW PENDING**
**Type** : build UI (template only) — 2ᵉ lot de `Sx_UI_09` Accessibility & Motion
**Date** : 2026-07-18
**Baseline** : `ef3b6a1` (revue 09.1 acceptée)
**Worktree** : `work/sb-ui-09-2-form-errors`

---

## 1. Baseline
HEAD local = origin = `ef3b6a1`, working tree clean. Aucun build 09.2 préexistant.

## 2. Brainstorming (Options / Risques / Choix)
**Audit** : **7 templates** rendent `<div class="integrity-errors"><b>{{ error }}</b></div>` (login,
register, reset_password ×2, forgot_password, contact, password_change, export) — **8 conteneurs** au
total, **aucun** `role`/`aria-live`/`aria-invalid`/`aria-describedby`. L'erreur est un **message global**
(`{{ error }}`), pas par-champ ; le backend **n'identifie pas** le champ fautif.

| Question | Options | Choix |
|---|---|---|
| Annonce de l'erreur | `role="alert"` (implique `aria-live="assertive"`) vs `aria-live` explicite | **`role="alert"`** (canonique pour une erreur rendue au chargement, SSR/no-JS) |
| `aria-invalid` par-champ | A: pas d'aria-invalid · B: sur tous les champs · C: minimal | **A** — le backend ne dit pas quel champ est fautif ; marquer les champs = **faux/trompeur** (WCAG : aria-invalid doit refléter l'état réel). **On n'invente pas.** |
| Relier champs↔message | `aria-describedby` par-champ vs sur `<form>` | **`aria-describedby` sur `<form>`** (conditionnel `{% if error %}`, id sur le conteneur) — login/register |
| Portée | login/register seuls vs les 7 | **`role="alert"` sur les 8 conteneurs** (cohérence), `id`+`describedby` sur login/register |

**Choix retenu** : `role="alert"` sur **tous** les conteneurs d'erreur + `id`/`aria-describedby`
(conditionnel) sur login/register. **Pas d'`aria-invalid`** (honnête). SSR/no-JS, tokens Auren, contrat
POST/champs/labels **inchangés**.

## 3. Implémentation
- **login.html** : conteneur `<div class="integrity-errors" role="alert" id="login-error">` +
  `<form … {% if error %} aria-describedby="login-error"{% endif %}>`.
- **register.html** : idem avec `register-error`.
- **reset_password.html** (×2), **forgot_password.html**, **contact.html**, **password_change.html**,
  **export.html** : `role="alert"` ajouté sur chaque conteneur `integrity-errors`.
- **Total : 8/8 conteneurs** portent `role="alert"`. **Pas d'`aria-invalid`**. `aria-describedby`
  **conditionnel** (`{% if error %}`) → aucune référence pendante quand pas d'erreur.

## 4. Tests ajoutés
`tests/test_form_errors_a11y.py` (**11 tests**) : `role="alert"` sur chaque conteneur des 7 templates,
aucun conteneur sans role, login/register `id` + `aria-describedby` conditionnel, **pas d'attribut
`aria-invalid`** (vérifie l'attribut, pas le mot du commentaire), no-JS, contrat POST/champs inchangés
(username/password/email/password_confirm/autocomplete), pas de nouveau style/couleur, garantie source
(les 7 templates livrent role=alert).

## 5. Tests réorientés
**Aucun** — le build est **purement additif** (attributs ARIA ajoutés, aucune structure/champ/contrat
modifié). Aucun test asservi cassé.

## 6. Scope
7 templates (`login`/`register`/`reset_password`/`forgot_password`/`contact`/`password_change`/`export`
`.html`) · `tests/test_form_errors_a11y.py` (neuf) · docs. **Aucun** router/service/model/migration/data/
manifest/icon/asset/JS/contrat POST/couleur/Custom. check_scope = **ISOLATED** ; broad sweep ciblé exécuté.

## 7. Résultats locaux
- `test_form_errors_a11y.py` : **11 passed**.
- Broad sweep ciblé (form_errors/auth/login/register/reset/forgot/contact/password/export/pwa/a11y) :
  **282 passed, 0 failed** (103s).
- ruff clean ; budget **543 ≤ 548** ; spec PASS ; check_scope ISOLATED.

## 8. Accessibilité
Erreurs de formulaire **annoncées** aux lecteurs d'écran via `role="alert"` (WCAG 2.2 — 4.1.3 Status
Messages, niveau AA ; 3.3.1 Error Identification). **SSR-only** : l'annonce se produit au reload de la
page (pas de JS). `aria-describedby` relie le formulaire au message sur login/register. **Pas
d'`aria-invalid`** faute d'information par-champ fiable (choix honnête, non trompeur).

## 9. Non-régressions
Contrat POST (`method`/`action`/`name`/`autocomplete`/`required`/`minlength`) **inchangé** ; labels,
champs, structure des formulaires **intacts** ; no-JS ; aucune couleur/style modifié ; pages auth
standalone toujours fonctionnelles.

## 10. Dettes Sx_UI_09 restantes
`Sb_UI_09.3` Contrast Guard (test de garde ratios tokens) · `Sx_UI_09` closeout.

## 11. Statut
🟢 **CODE COMPLETE — CI PENDING — HUMAN REVIEW PENDING.**

---

## Verdict

**Verdict :** 🟢 **Sb_UI_09.2 CODE COMPLETE (CI + human review pending).** 2ᵉ lot de `Sx_UI_09` : les
erreurs de formulaire sont **annoncées** aux lecteurs d'écran — `role="alert"` sur les **8 conteneurs**
`integrity-errors` des 7 templates (login/register/reset_password/forgot_password/contact/password_change/
export), + `id` et `aria-describedby` **conditionnel** (`{% if error %}`) reliant le formulaire au message
sur login/register. **Pas d'`aria-invalid`** — le backend renvoie un message global sans identifier le
champ fautif, marquer les champs serait faux (choix honnête, WCAG-correct). **SSR/no-JS** ; contrat POST/
champs/labels/couleurs **inchangés**. **Template only** : aucun router/service/model/migration/manifest/
asset/JS/contrat/Custom. 11 tests dédiés, **0 réorienté** (build additif). ruff clean, budget 543 ≤ 548,
check_scope ISOLATED.

**Prochaine étape** (séparée, non commencée) : `GO VALIDATE — Sb_UI_09.2 Form-Errors ARIA`.
