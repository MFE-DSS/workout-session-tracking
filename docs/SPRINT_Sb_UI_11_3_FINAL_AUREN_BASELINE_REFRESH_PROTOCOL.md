# Sb_UI_11.3 — Final Auren Baseline Refresh — PROTOCOLE

**Statut** : 🟡 **BASELINE REFRESH READY / OPERATOR CAPTURE PENDING**
**Type** : protocole de capture — docs-only (aucun PNG committé, aucun code touché)
**Date** : 2026-07-19
**Baseline auditée** : `a7b1acc`
**Nature** : capture **locale, opérateur** (Playwright + compte fixture) — l'agent **ne peut pas** la
réaliser (pas de navigateur/AT en environnement ; les PNG ne sont **jamais** committés, `.gitignore`).

> Ce protocole prépare le **refresh de la baseline visuelle** après le rebrand **Auren** et le nouveau
> shell. La baseline P0 existante (`BASELINE_P0_CAPTURED_2026_07_04.md`) date d'**avant** ces changements
> et est **obsolète visuellement**. Le refresh est une **action opérateur** ; ce document en fournit la
> fiche exécutable.

---

## 1. Pourquoi un refresh (delta depuis la baseline du 2026-07-04)
La baseline P0 du 4 juillet a été capturée **avant** :
- **Rebrand Auren visible** (`Sx_UI_10`) : `<title>`/brand/footer/manifest « Auren », pack d'icônes PWA,
  strings science/atlas/coach, welcome/login/register.
- **Nouveau shell app-like** (`Sx_UI_03`, CLOSED) : **bottom navigation mobile** (4 destinations), **rail
  desktop** (≥1024px), **topbar rétrogradée** en nav secondaire, **skip link**, indicateur session active
  (fin de l'active-banner overlay).
- **Densité / lisibilité** (`Sx_UI_06`/`07`) et **a11y** (`Sx_UI_09`, CLOSED) : reduced-motion global,
  form-errors `role="alert"`.
→ Les captures existantes ne reflètent plus l'UI réelle. **Refresh nécessaire** avant tout closeout
visuel global.

## 2. Outillage (existant, Sx_UI_11 — ne rien réinstaller)
- **Matrice** : `scripts/visual_baseline_matrix.py` (8 slugs P0 × 2 viewports = 16 screenshots).
- **Runtime** : `scripts/visual_baseline_runtime.py` (auth cookie + session fixture + storage_state ;
  refuse prod / DB non-locale).
- **Capture** : `scripts/visual_baseline_capture.py`.
- **Viewports** : mobile **360×640**, desktop **1440×900**.
- **Prérequis local** : Playwright installé (hors CI), compte fixture local (`baseline_user_local`),
  `.env.baseline` **non versionné**.

## 3. Matrice à recapturer

### 3.A — P0 obligatoire (8 slugs × 2 viewports = 16)
`home-authenticated` · `home-no-active-session` · `session-detail-active` · `session-detail-done` ·
`progression` · `profile` · `login` · `register`.

### 3.B — Surfaces shell nouvelles (à vérifier explicitement dans les captures P0)
Ces surfaces **n'existaient pas** dans la baseline du 4 juillet ; elles doivent apparaître correctement :
| Surface | Où l'observer | Viewport |
|---|---|---|
| **Bottom navigation** (4 destinations) | toute page authentifiée | **mobile** (<1024px) |
| **Rail desktop** (4 destinations + Plus + logout) | toute page authentifiée | **desktop** (≥1024px) |
| **Topbar secondaire** (`<details>` Plus, 0 primaire) | mobile | mobile |
| **Skip link** (visible au focus) | 1er tab de n'importe quelle page | les 2 |
| **Indicateur session active** (dot Séance, plus de banner) | `home-authenticated` / `session-detail-active` | les 2 |
| **Marque/strings Auren** | login/register/home/footer | les 2 |
| **Form-errors `role="alert"`** | login avec erreur (POST invalide) | mobile |

### 3.C — P1/P2 recommandés (si temps)
`library` · `library-detail` · `progression-empty` · `history`.

## 4. Commande de capture (opérateur, local)
```bash
# dry-run d'abord (vérifie la matrice sans capturer)
python scripts/visual_baseline_capture.py --dry-run --priority P0 --strict-p0

# capture réelle P0 (les 2 viewports), compte fixture local
python scripts/visual_baseline_capture.py \
    --priority P0 \
    --viewport all \
    --out baseline/auren_final_2026_07_19/
```
- **Compte** : fixture local `baseline_user_local` — **JAMAIS** un compte prod. Identifiants via
  `.env.baseline` (non versionné).
- **Storage** : `baseline/` (ou `tests/visual/baseline/`) — **`.gitignore`**, aucun PNG committé.

## 5. Inspection humaine attendue (checklist par capture)
Sur chaque écran, vérifier :
- [ ] **Identité Auren** : marque « Auren » (pas SPIGNOS visible), palette graphite/mono/ambre `#C8A24B`,
      **0 orange legacy `#f25f3a`** dans les surfaces PWA, 0 « Orion ».
- [ ] **Mobile** : bottom nav 4 destinations lisible, non tronquée, safe-area OK, pas de scroll horizontal,
      topbar réduite au menu secondaire, pas de destination primaire dupliquée.
- [ ] **Desktop** : rail gauche visible (bottom nav + topbar masquées), contenu décalé + centré (≤960px),
      pas d'espace vide inutile.
- [ ] **Session active** : indicateur discret sur l'onglet Séance (dot ambre), **aucune bannière globale**
      ; le hero Home reste l'unique surface « Reprendre ».
- [ ] **Skip link** : invisible au repos, visible et net au focus clavier.
- [ ] **Cohérence** : Auren Terminal homogène, contraste confortable (tokens ≥ AA, verrouillés par
      `Sb_UI_09.3`), pas de motion parasite (reduced-motion respecté).

## 6. Livrable de la capture (opérateur → docs)
Après capture locale, l'opérateur produit un **rapport de capture** (comme
`BASELINE_P0_CAPTURED_2026_07_04.md`) — docs-only, **sans PNG** : liste des slugs capturés, viewports,
runtime/commit utilisés, verdict d'inspection, anomalies éventuelles. Ce rapport **remplace** la baseline
du 4 juillet comme référence visuelle courante (« Final Auren Baseline »).

## 7. Non-goals
- ❌ Aucun PNG committé (baselines `.gitignore`, spec `Sx_UI_11`).
- ❌ Aucune installation Playwright/tooling dans ce protocole (déjà livré `Sb_UI_11.1`/`.2`).
- ❌ Aucun compte prod (fixture local uniquement).
- ❌ Aucun code/template/CSS/route/service touché.
- ❌ Aucune capture par l'agent (hors capacité : pas de navigateur ; action opérateur).

## 8. Gating / point d'arrêt
- La **capture** est une action **opérateur locale** — non réalisable par l'agent, non committée.
- Ce protocole (docs-only) est committé ; la CI est légitimement skippée (`paths-ignore: docs/**`).
- **Prochaine action** dépend de l'opérateur : exécuter la capture locale → produire le rapport de capture
  → puis `Sx_UI` Global Final Closeout (dernier élément de la queue `Sx_UI_12`).

---

## Verdict

**Verdict :** 🟡 **Sb_UI_11.3 — BASELINE REFRESH READY / OPERATOR CAPTURE PENDING.** Le protocole de
refresh de la baseline visuelle **post-Auren / post-shell** est prêt : la baseline P0 du 2026-07-04 est
**obsolète** (antérieure au rebrand Auren et au nouveau shell bottom-nav/rail/hardening). Matrice à
recapturer = **8 slugs P0 × 2 viewports** (+ surfaces shell nouvelles : bottom nav, rail, topbar
secondaire, skip link, indicateur session active, form-errors) via le tooling `Sx_UI_11` existant
(`visual_baseline_capture.py --priority P0 --viewport all`), compte fixture **local** (`baseline_user_
local`), storage **`.gitignore`** (aucun PNG committé). La **capture elle-même est une action opérateur
locale** — l'agent ne peut pas la réaliser (pas de navigateur/Playwright ; PNG non versionnés). Aucun
code/CSS/template touché par ce protocole (docs-only).

**Prochaine action** (opérateur, non commencée par l'agent) : exécuter la capture locale puis produire le
**rapport de capture** (docs, sans PNG), après quoi la queue `Sx_UI_12` ne comptera plus que le **`Sx_UI`
Global Final Closeout**.
