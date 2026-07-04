# Baseline P0 Captured — 2026-07-04

**Type :** Capture report — docs-only, no PNG committed
**Date :** 2026-07-04
**Operator :** Martin Feldmann
**Branch :** `claude/sprint-reporting-fitness-app-V7Qr6`
**Verdict :** ✅ **P0 BASELINE CAPTURED LOCALLY — Sb_UI_04.1 READY TO BE PROPOSED**

---

## 1. Runtime CLI utilisé

- **Sprint runtime :** `Sb_UI_11.2 Baseline Runtime Integration Patch`
- **Runtime commit (code) :** `a2846a253612409d00284c7ce3946506a8577e04`
- **Acceptance commit (review) :** `29b756efa7416d47fb519fc00ee32f0094178cfe`
- **HEAD au moment de la capture :** `29b756efa7416d47fb519fc00ee32f0094178cfe` (inchangé)

## 2. Résultat capture

| Métrique | Valeur |
|---|---|
| Priorité capturée | **P0** |
| Écrans P0 dans matrice | 8 |
| Viewports (mobile + desktop) | 2 |
| PNG attendus | 16 |
| **PNG capturés** | **16** |
| **Status** | **ok=16 / failed=0** |
| Base URL | `http://127.0.0.1:8000` (uvicorn local) |
| DB signature | `sqlite:./var/workout.db` (DB locale, `.env` par défaut) |
| App env | `dev` |

## 3. Seuils réglementaires

| Contrainte | Seuil | État |
|---|---|---|
| Sx_UI_11 §5 — P0 minimum | ≥ 14 screenshots | ✅ **16 ≥ 14** |
| Sx_UI_04 §18 — unblock minimum | ≥ 14 screenshots P0 | ✅ **16 ≥ 14** |
| Sx_UI_11 §12 — human review primary | revue humaine possible | ✅ 16 PNG disponibles localement |

## 4. IDs non-secrets utilisés

Ces IDs sont des identifiants de fixture locale, pas des secrets. Ils sont créés par `visual_baseline_runtime.py prepare` et existent uniquement dans la DB locale de l'opérateur.

- `user.id` = **3** (compte fixture `baseline_local`)
- `active_session_id` = **4** (session `in_progress`)
- `done_session_id` = **5** (session `completed`)

Les 3 entités ont été **créées** lors du `prepare` (flag `created=True` sur les 3).

## 5. Liste des chemins PNG capturés (paths only, pas de contenu)

Convention Sx_UI_11 §11 respectée : `{page-slug}/{viewport}-{state}.png`, kebab-case strict.

```
var/visual-baseline/home-authenticated/desktop-authenticated.png
var/visual-baseline/home-authenticated/mobile-authenticated.png
var/visual-baseline/home-no-active-session/desktop-authenticated.png
var/visual-baseline/home-no-active-session/mobile-authenticated.png
var/visual-baseline/login/desktop-anonymous.png
var/visual-baseline/login/mobile-anonymous.png
var/visual-baseline/profile/desktop-authenticated.png
var/visual-baseline/profile/mobile-authenticated.png
var/visual-baseline/progression/desktop-authenticated.png
var/visual-baseline/progression/mobile-authenticated.png
var/visual-baseline/register/desktop-anonymous.png
var/visual-baseline/register/mobile-anonymous.png
var/visual-baseline/session-detail-active/desktop-authenticated.png
var/visual-baseline/session-detail-active/mobile-authenticated.png
var/visual-baseline/session-detail-done/desktop-authenticated.png
var/visual-baseline/session-detail-done/mobile-authenticated.png
```

**Total : 16 chemins.**

**Le contenu des images n'est ni committé ni référencé.** Ce report documente uniquement que la capture a eu lieu.

## 6. Confirmations sécurité

- ✅ **Aucun PNG committé** — `git ls-files | grep .png` = vide, `.gitignore` sur `/var/` couvre déjà `var/visual-baseline/`
- ✅ **Aucun `runtime.json` committé** — reste local dans `var/visual-baseline/runtime.json`, gitignored
- ✅ **Aucun `auth-state.json` committé** — reste local dans `var/visual-baseline/auth-state.json`, gitignored, `chmod 600`
- ✅ **Aucune DB locale committée** — `.gitignore` sur `*.db` et `/var/` couvre `var/workout.db`
- ✅ **Aucun secret / cookie / token affiché ou committé** — anti-secret rules Sb_UI_11.1 + Sb_UI_11.2 respectées
- ✅ **`git status` clean après capture** — aucun fichier tracké modifié, aucun untracked apparu
- ✅ **`HEAD` inchangé** — `29b756e` (aucun commit inattendu par la capture)

## 7. Décision

- ✅ **P0 baseline captured locally.**
- ⏸️ **Release tag / artifact upload deferred** — les 16 PNG restent sur la machine opérateur pour l'instant. Aucun besoin immédiat de partage cross-machine.
- 🟢 **`Sb_UI_04.1 CSS Foundation Build` may now be proposed** au GO opérateur explicite.
- ❌ **No baseline derogation needed anymore** — la précondition dure de `Sx_UI_04 §18` et `Sx_UI_04_HUMAN_REVIEW_REPORT §5` (baseline P0 réellement capturée) est satisfaite.

## 8. Limitations et étapes futures optionnelles

- **Les PNG restent locaux sur la machine opérateur.** Impossible de comparer avant/après entre machines sans upload artefact ou release tag.
- **Pour partage cross-machine ou conservation long terme :** créer plus tard un **release tag** `baseline-preauren-2026-07-04` avec les 16 PNG uploadés comme assets, ou un artefact CI contrôlé. Non urgent V1.
- **Session `home-no-active-session` :** la fixture actuelle crée le même user pour la session `active` et la session `done`. La route `/` avec cet user peut donc afficher la même active session que sur `home-authenticated`. Non-bloquant pour V1 baseline pixel-fair, mais un futur `Sb_UI_11.3` pourrait affiner en créant un 2ᵉ user sans session active.
- **Warning `bcrypt.__about__`** observé lors de `prepare` (bug connu passlib+bcrypt 4.x, non-bloquant, hash valide produit). À nettoyer dans un futur `Sb_OPS.passlib-bcrypt-compat` si souhaité — indépendant du cycle Sx_UI.

## 9. Références

- Runtime CLI source : `scripts/visual_baseline_runtime.py` (commit `a2846a2`)
- Capture CLI source : `scripts/visual_baseline_capture.py` (commits `e8ba190` + `a2846a2`)
- Sprint report runtime : `docs/SPRINT_Sb_UI_11_2_BASELINE_RUNTIME_PATCH_REPORT.md`
- Human review runtime : `docs/SPRINT_Sb_UI_11_2_HUMAN_REVIEW_REPORT.md`
- Spec source : `docs/strategy/Sx_UI_11_SCREENSHOT_REGRESSION_BASELINE_SPEC.md`
- Spec cible reskin : `docs/strategy/Sx_UI_04_SESSION_FOCUS_RESKIN_SPEC.md`
- Registry : `docs/strategy/SPEC_REGISTRY.md` §1sexies
- Roadmap : `docs/strategy/ROADMAP_AND_NEXT_STEPS.md`

## 10. Verdict final

✅ **P0 BASELINE CAPTURED — Sb_UI_04.1 READY TO BE PROPOSED.**

**Baseline P0 précondition satisfaite.**
**Aucune dérogation baseline nécessaire.**
**`Sb_UI_04.1 CSS Foundation Build` peut être ouvert au prochain override opérateur explicite.**
