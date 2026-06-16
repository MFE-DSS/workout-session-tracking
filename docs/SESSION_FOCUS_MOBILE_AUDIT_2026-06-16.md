# Session Focus Mobile Audit — V1

**Date :** 2026-06-16
**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`
**Niveau d'audit :** **manuel statique** (lecture code + tests structurels).
**Pas de Lighthouse CI dans Sb_29.5 (OQ-D).**
**Pas de navigateur réel exécuté.**

---

## 1. Périmètre audité

Sb_29.1 → Sb_29.5 sur la page session detail (`/sessions/{id}`).
Cibles : 360×640, no-JS fallback, accessibilité statique.

## 2. Checklist

### Mobile 360×640
- [x] Aucun `overflow-x: scroll` introduit dans `session_focus.css` (test `test_no_overflow_x_scroll_introduced_in_session_focus_css`).
- [x] Rest timer wrapper utilise `flex-wrap: wrap` (test `test_rest_timer_uses_flex_wrap`).
- [x] Media query `@media (max-width: 380px)` présente sur sticky-jump, sticky-cta et rest-timer.
- [x] Aucune largeur fixe en pixels > 360 introduite par les blocs Sx_29.
- [ ] **Non testé** : vrai défilement vertical sur device réel — voir dogfood template.

### Tap targets (WCAG 2.5.5)
- [x] `.session-focus__tap-target` impose `min-height: 44px` + `min-width: 44px`.
- [x] Classes appliquées sur boutons jump bar, prev/next, CTA primaire, skip rest.

### Sticky comportements
- [x] `session-focus__sticky-header` : `position: sticky; top: 0; z-index: 4`.
- [x] `session-focus__sticky-jump` : `position: sticky; top: 56px; z-index: 3` (48px en mobile <380px).
- [x] `session-focus__card--active .session-focus__sticky-cta` : `position: sticky; bottom: 0; z-index: 2` (scope strict actif).
- [x] iOS safe-area : `env(safe-area-inset-bottom, 0px)` sur sticky CTA + media query mobile.

### Rest timer (Sb_29.4)
- [x] Fallback statique no-JS : "Repos suggéré : 90s" rendu en SSR.
- [x] `aria-live="polite"` + `role="status"` (test `test_rest_timer_has_aria_live_polite`).
- [x] Skip button `type="button"` (test `test_skip_rest_is_type_button`).
- [x] Timer hors `<form action=update_exercise_card>` (test `test_rest_timer_is_outside_post_form`).
- [x] Aucune action critique ne dépend de `session_focus.js`.

### Accessibilité non-color (WCAG 1.4.1)
- [x] Active : bullet `•` via `::before` sur `.exercise-card__code`.
- [x] Done : check `✓` via `::after` + `border-left: 3px solid`.
- [x] Partial : `border-left: 3px solid var(--warn)`.
- [x] Skipped : `border-left: 3px dashed` + `text-decoration: line-through`.
- [x] Substituted : `border-left: 3px dotted` + flèche `↔` via `::after`.
- [x] Jump bar active : bullet `•` via `::before`.

### Cascade CSS post-extraction
- [x] `session_focus.css` chargé APRES `app.css` dans `<head>` (test `test_session_focus_css_link_in_rendered_page`).
- [x] Blocs Sx_29 retirés de `app.css` (test `test_app_css_no_longer_contains_sx29_blocks`).
- [x] Tous les marqueurs Sb_29.1 → Sb_29.4 présents dans `session_focus.css` (test `test_session_focus_css_exists_and_nonempty`).

### No-JS hardening
- [x] `<details>` natif HTML pour collapse cards et notes.
- [x] Ancres `#exercise-{id}` préservées.
- [x] Tous les boutons prev/next/primary CTA sont `type="submit"` à l'intérieur des `<form action="…/update_exercise_card">`.
- [x] Skip rest hors form.
- [x] Aucune réécriture client-side.

### JS hardening
- [x] `session_focus.js` IIFE strict mode.
- [x] Aucun `import`, `require`, `fetch`, `XMLHttpRequest`, `Promise.then` réseau.
- [x] `clearInterval` présent (cleanup).
- [x] Short-circuit `length === 0` (test `test_session_focus_js_handles_empty_dom`).
- [x] Aucun token React / Vue / Angular (tests `test_no_react_or_bundle_introduced` + `test_session_focus_js_is_vanilla`).
- [x] Aucun nouveau fichier JS au-delà de `preview.js` + `session_focus.js`.

## 3. Limites de cet audit (V1)

- Pas de Lighthouse CI (OQ-D respecté).
- Pas de test sur un vrai navigateur (Chrome / Safari / Firefox mobile).
- Pas de mesure CLS / LCP / INP réelle.
- Pas de test screen reader (VoiceOver / TalkBack) sur device.
- Pas de test prefers-reduced-motion en condition réelle (déclaratif uniquement).
- Pas de test de scroll horizontal sur un vrai viewport 360×640.

Ces limites sont **assumées** pour Sb_29.5. Elles seront levées par le
dogfood Sx_29 sur device réel (cf. `docs/dogfood/DOGFOOD_Sx_29_FOCUS_MODE_TEMPLATE.md`).

## 4. Recommandation

**✅ V1 mobile audit PASS** sur la base des assertions structurelles
disponibles. **Dogfood device réel REQUIS** avant toute conclusion sur
l'expérience utilisateur. Sx_30 ne s'ouvre pas tant que le dogfood
n'est pas exécuté.

## 5. Pointeurs

- `tests/test_session_focus_layout.py` — squelette Sb_29.1
- `tests/test_session_focus_navigation.py` — navigation active Sb_29.2
- `tests/test_session_focus_sticky_cta.py` — CTA Sb_29.3
- `tests/test_session_focus_rest_timer.py` — timer Sb_29.4
- `tests/test_session_focus_mobile_smoke.py` — smoke Sb_29.5
- `tests/test_session_focus_accessibility.py` — a11y Sb_29.5
- `app/static/css/session_focus.css` — surface CSS Sx_29 extraite
- `app/static/js/session_focus.js` — progressive enhancement vanilla
- `docs/strategy/Sx_29_MOBILE_SESSION_FOCUS_MODE_SPEC.md` — spec source
- `docs/strategy/Sx_29_CLOSURE_REPORT.md` — bilan technique Sx_29
