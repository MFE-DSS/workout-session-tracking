# Prod Stabilization Gate — Profile + Body Intelligence + Coach Report + Sx_30 Overload

**Gate ID :** `PROD_STABILIZATION_PROFILE_BODY_COACH_REPORT`
**Type :** OPS / DEPLOY / SMOKE — pas de FEATURE BUILD
**Date :** 2026-07-01
**Branche canonique :** `claude/sprint-reporting-fitness-app-V7Qr6`

---

## 1. SHA à déployer

**Head recommandé :** `1e4cd4c804a96d3e5af32600bbc601158d6a8841`
Message : `Sb Body 02.1 — Capture Quality Shell (#21)` (merge squash 2026-07-01T14:20:08Z)

Ce SHA contient **toutes** les surfaces attendues par le gate :

| Contenu attendu | Commit source | Vérification code (code-side) |
|---|---|---|
| Sx_30 overload bugfix (filtre `template_slug_snapshot` + politique substitution V1 + garde-fou ratio 3×) | `10732e9` | ✅ 3 marqueurs présents dans `app/services/overload_inputs.py` |
| Sx_30 bugfix CI validation | `96d1eff` | ✅ run 28433445051 3/3 |
| Dogfood Sx_30 PASS acté | `0fb5007` | ✅ `docs/dogfood/DOGFOOD_Sx_30_OVERLOAD_ENGINE_REPORT.md` présent |
| Sx_31 Body Intelligence composer | `0016f7f` (`sb_31_1`) | ✅ `body_intelligence.py` avec `BODY_INTELLIGENCE_VERSION = 1` |
| Sx_31 I/O + route `/body/intelligence` | `761cbba` (`sb_31_2`) | ✅ `body_intelligence_inputs.py` + `body_intelligence.html` |
| Sx_31 snapshot dans `/coach-report` | `4b06a5e` (`sb_31_3`) | ✅ `_partials/coach_body_snapshot.html` |
| Sx_31 a11y + responsive + perf | `876101b` (`sb_31_4`) | ✅ marqueurs dans template + CSS |
| Sb_31.next.profile-link (OQ-G) | `290a979` | ✅ classe `profile-body-intel-link` dans `app/templates/profile.html` |
| Sx_31 flag hardening (`BODY_INTELLIGENCE_ENABLED`) | `72f5215` (PR #19) | ✅ 3 flags Body isolés dans `app/config.py` |
| Sb Body 02.1 shell (`/body/capture-quality`, flag OFF par défaut) | `1e4cd4c` (PR #21) | ✅ router + template shell présents |

## 2. CI source

- Bugfix Sx_30 : run [28433445051](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28433445051) — 3/3 ✅
- PR #21 (shell Sb Body 02.1) : run [28454376953](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28454376953) — 3/3 ✅
- HEAD post-merge à valider par un nouveau run CI (automatique au push) — à confirmer dans §11.

## 3. Résultats QA code-side (sur HEAD `1e4cd4c`, local)

| Gate | Résultat |
|---|---|
| `pytest tests/test_overload_history_identity_guard.py` (11 tests bugfix Sx_30) | ✅ passed |
| `pytest tests/test_body_intelligence_route.py` (19 tests) | ✅ passed |
| `pytest tests/test_body_intelligence_gate.py` (23 tests) | ✅ passed |
| `pytest tests/test_body_intelligence_a11y_perf.py` (28 tests) | ✅ passed |
| `pytest tests/test_coach_report_body_snapshot.py` | ✅ passed |
| `pytest tests/test_profile_body_intelligence_link.py` | ✅ passed |
| `pytest tests/test_body_capture_quality_gate.py` (21 tests shell 02.1) | ✅ passed |
| **Total surfaces critiques** | ✅ **122 tests passed** |
| `check_ruff_budget.py` | ✅ 529 ≤ 548 |
| `check_spec_protocol.py` | ✅ OK |
| `check_alembic_drift.py` | ✅ no diff |
| `check_schema_snapshot.py` | ✅ matches head `7i0f5d1e2g43` (Body Manual Profile) |

## 4. Flags prod attendus

| Flag | Valeur cible prod | État code side |
|---|---|---|
| `BODY_INTELLIGENCE_ENABLED` | **`true`** (à activer si absent) | Défaut code `False` — impératif de setter en prod |
| `BODY_ASSESSMENT_ENABLED` | **`false`** (track Manual Body Profile pas encore ouvert) | Défaut code `False` ✅ |
| `BODY_CAPTURE_QUALITY_ENABLED` | **`false`** (shell 02.1 mergé mais flag OFF par design) | Défaut code `False` ✅ |
| `PERF_REQUEST_TIMING_ENABLED` | à ta discrétion | opt-in Sb_26.6 |
| `RATE_LIMIT_ENABLED` | `true` (héritage Sb_26.4) | à confirmer prod |
| `SENTRY_ENABLED` | à ta discrétion | opt-in Sb_26.3 |

## 5. Migration Alembic

- **Head Alembic attendu :** `7i0f5d1e2g43` (Sb_Body_01 — Manual Body Profile MVP)
- **Migration ajoutée par PR #21 ?** ❌ Non (shell docs-only + config)
- **Action prod :** `alembic upgrade head` **si** current prod < `7i0f5d1e2g43`. Sinon no-op.
- **Schema snapshot :** ✅ à jour (`check_schema_snapshot.py` matches)

## 6. Backup pré-déploiement — ACTÉ VIA GITHUB ACTIONS

- [x] Backup SQLite pris automatiquement par `deploy_prod.sh` pendant le workflow deploy GitHub Actions [`28527679621`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28527679621)
- [x] Backup taille cohérente : `116K`
- [x] Backup présent : `/opt/workout-session-tracking/var/backups/workout_pre_deploy_20260701_151059.db`
- [x] `/healthz/strict` post-deploy = 200, confirmant backup + drift OK côté smoke interne

**Note :** la DB prod était initialement vide côté `users`. Ce n'est pas un échec de backup ; c'est l'état fonctionnel initial de la prod avant création du compte smoke.

## 7. Smoke tests prod — EXÉCUTÉS 2026-07-02 (Option A structurel)

Compte smoke créé via `/register` : `martin_prod_smoke_20260702_1037`. Sessions curl externes depuis Mac local (`$BASE=https://spignos.com`). Cf. §9 pour la limitation DB vide.

### 7.1 Auth / navigation

- [x] Register via `POST /register` + auto-login OK (session active, `Se déconnecter` visible)
- [x] `/` home OK
- [x] Nav principale sans 500 dans logs

### 7.2 `/profile`

- [x] 200
- [x] Carte « Lecture corporelle » visible (`profile-body-intel-link`=1, `Lecture corporelle`=1, `Basé sur les séances loggées`=1)
- [x] Lien « Voir Body Intelligence » cliquable
- [x] Lien absolu vers `https://spignos.com/body/intelligence`

### 7.3 `/body/intelligence`

- [x] 200
- [x] 7 blocs distincts rendus (`body_metrics`, `implicit_signal_summary`, `muscle_zone_balance`, `push_pull_legs_balance`, `quality_and_confidence`, `training_consistency`, `unavailable_or_limits`)
- [x] Badges visibles : `Mesuré=2`, `Dérivé=8`, `Inféré=2`, `Hors de portée=3`
- [x] Bloc limites / hors de portée visible
- [x] Aucun wording interdit détecté (seule occurrence `symétrie réelle` = négation transparente conforme Sx_31 : « Posture et symétrie réelle non déductibles sans données dédiées. »)

### 7.4 `/coach-report`

- [x] 200
- [x] `coach-block--body-snapshot=1`
- [x] CTA « Voir le détail » présent (count=2)
- [x] Pas de duplication complète des 7 blocs Body Intelligence (0 `data-block-key` en coach)

### 7.5 Session detail + Sx_30 overload (le test le plus critique)

- [ ] Ouvrir une séance en cours avec un exercice à historique (ex. `push-a E5` élévations latérales câble)
- [ ] Hint overload s'affiche **uniquement** sur la carte active
- [ ] `value=""` reste vide (aucun pré-remplissage)
- [ ] Placeholder `≈ N kg` cohérent avec « Dernière fois »
- [ ] **CRITIQUE :** exercice « élévation latérale câble » (5 kg historique) ne propose PAS 57 kg ni tout autre chiffre incohérent
- [ ] Exercice courant substitué → hint silencieux (aucun chiffre affiché)

> **Différé :** DB prod initialement vide, aucune séance historique disponible. Test reporté au mini-gate `PROD_DOGFOOD_57KG_LIVE_CHECK` après premières séances réelles loggées. Cf. Annexe D.

### 7.6 Non-régression /body/capture-quality

- [x] `GET /body/capture-quality` → **404** strict (flag `BODY_CAPTURE_QUALITY_ENABLED=false` par design)
- [x] Aucune fuite UI détectée dans `/profile`, `/body/intelligence`, `/coach-report` (0/0/0 sur grep `capture-quality`)

### 7.7 Régression générale

- [x] Logs `journalctl -u workout` clean : aucun error / exception / traceback / 500 (fenêtre 20 minutes post-smoke)
- [x] `/healthz` externe 200
- [x] `/healthz/strict` externe 200

## 8. Vérification bug Sx_30 (rappel critique)

**Test prod live-data différé.**

**Raison :** la base prod était initialement vide (`users=0`, aucune séance historique), donc le scénario historique « élévation latérale câble ≠ 57 kg » n'était pas testable honnêtement en production.

**Statut :**

- code-side bugfix (`10732e9` : filtre `template_slug_snapshot` + politique substitution V1 + garde-fou `_IMPLAUSIBLE_WEIGHT_RATIO = 3.0`) présent dans le SHA déployé ✅
- tests critiques Sx_30 verts (11 tests bugfix + suite complète Sb_30) ✅
- dogfood local Sx_30 déjà validé (2026-07-01, `docs/dogfood/DOGFOOD_Sx_30_OVERLOAD_ENGINE_REPORT.md`) ✅
- mini-gate prod requis après données réelles ⏳

**Mini-gate :** `PROD_DOGFOOD_57KG_LIVE_CHECK` (cf. Annexe D).

## 9. Incidents / anomalies

| # | Description | Sévérité | Action |
|---|---|---|---|
| 1 | DB prod initialement vide (`users=0`) : compte smoke `martin_prod_smoke_20260702_1037` créé via `/register`. | Info | Non bloquant pour smoke structurel. Test live-data 57 kg reporté. |
| 2 | Test §7.5 Sx_30 overload non exécutable faute d'historique réel. | Pending | Mini-gate `PROD_DOGFOOD_57KG_LIVE_CHECK` à jouer après premières séances réelles. |

## 10. Verdict final

Trois verdicts possibles :

- [ ] ✅ **PROD STABLE FOR UI RENOVATION** — tous smoke tests verts, bug 57 kg non reproduit, aucun 500 dans logs
- [x] ✅ **PROD STRUCTURALLY STABLE FOR UI RENOVATION** — smoke structurel vert, DB prod initialement vide, Sx_30 57kg live-data mini-gate pending
- [ ] ❌ **PROD NOT READY** — bloqueur(s) identifié(s) ci-dessous

**Justification :**

Deploy SHA `1e4cd4c804a96d3e5af32600bbc601158d6a8841` signé par GitHub Actions run [`28527679621`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28527679621), tag `deploy/prod/2026-07-01-1511-1e4cd4c`.
`BODY_INTELLIGENCE_ENABLED=true` actif en production ; `BODY_ASSESSMENT_ENABLED` et `BODY_CAPTURE_QUALITY_ENABLED` absents donc `false` par défaut.
Smoke structurel externe vert : `/profile`, `/body/intelligence`, `/coach-report`, `/body/capture-quality=404`, `/healthz`, `/healthz/strict`, logs `journalctl` clean.
Le test live-data §7.5 « élévation latérale câble ≠ 57 kg » est différé car la DB prod était initialement vide. Il devient le mini-gate `PROD_DOGFOOD_57KG_LIVE_CHECK`.
UI renovation débloquée avec caveat : le mini-gate 57 kg reste requis pour clôture définitive Sx_30 en prod.

Signature opérateur : **Martin Feldmann** — 2026-07-02

---

## Annexe A — Position agent CLI (transparence)

Cette session CLI a effectué **uniquement** ce qui est faisable sans accès infra :

- ✅ Merge PR #21 via `gh pr merge` (credentials GitHub)
- ✅ Sync branche canonique locale
- ✅ Audit contenu code-side (grep sur les marqueurs attendus)
- ✅ Exécution 122 tests locaux critiques + 4 gates QA
- ✅ Production de ce rapport + mise à jour registry/roadmap

Cette session CLI **NE PEUT PAS** faire, et l'opérateur doit prendre en charge :

- ❌ SSH sur le VPS
- ❌ Déclencher un workflow deploy authentifié (pas de PROD_DEPLOY_TOKEN dans cette session)
- ❌ Setter `BODY_INTELLIGENCE_ENABLED=true` dans l'env prod
- ❌ Exécuter `alembic upgrade head` sur la DB prod
- ❌ Faire un backup SQLite prod
- ❌ Curl authentifié contre l'URL prod
- ❌ Lecture `journalctl` / logs nginx du serveur

Le rapport §6, §7, §8, §9, §10 est un template à remplir par l'opérateur en local, sans committer de secret.

## Annexe B — Rollback si NO-GO

1. Récupérer le SHA prod pré-stabilisation (avant `1e4cd4c`).
2. `git checkout <sha_pre_stabilization>` sur le serveur.
3. Restaurer le backup SQLite si migration a été jouée.
4. Restart service.
5. Vérifier /healthz + smoke §7.5 sur le SHA précédent.
6. Ouvrir un post-mortem docs/OPS_POSTMORTEM_STABILIZATION_YYYYMMDD.md.

## Annexe C — Autorisation

Ce gate autorise **uniquement** :
- ✅ Déploiement du SHA `1e4cd4c` sur prod
- ✅ Activation `BODY_INTELLIGENCE_ENABLED=true`
- ✅ Exécution `alembic upgrade head` si drift

**UI renovation :** avant verdict signé, ce gate n'autorise aucune rénovation UI. Après verdict `PROD STRUCTURALLY STABLE FOR UI RENOVATION`, les sprints UI peuvent démarrer, sous réserve de conserver le mini-gate `PROD_DOGFOOD_57KG_LIVE_CHECK` comme dette prod critique pending.

Ce gate n'autorise toujours **PAS** :
- ❌ Toute ouverture Sx_32 / PWA / Health API
- ❌ Toute ouverture Sb Body 02.2 (caméra locale)
- ❌ Activation de `BODY_ASSESSMENT_ENABLED` ou `BODY_CAPTURE_QUALITY_ENABLED`
- ❌ Aucun rollback partiel (rollback = SHA complet précédent)

## Annexe D — Mini-gate `PROD_DOGFOOD_57KG_LIVE_CHECK` pending

**Statut :** pending — ne bloque pas la rénovation UI, mais reste requis pour clôture définitive Sx_30 en production.

**Prérequis :**

- au moins 3 séances réelles loggées en prod ;
- au moins une occurrence historique de l'exercice « élévation latérale câble » ;
- une nouvelle séance contenant cet exercice.

**Test :**
Ouvrir la séance suivante contenant l'exercice « élévation latérale câble » et vérifier que le hint overload :

- affiche un `≈ N kg` cohérent avec le prior visible « Dernière fois » ;
- ne s'écarte pas de plus de 3× du prior visible ;
- ne propose jamais `57 kg` si le prior visible est autour de `5 kg` ;
- reste silencieux si l'exercice actif est un substitut V1.

**Verdict binaire :**

- ✅ hint cohérent ou silence → Sx_30 confirmé en prod live-data ;
- ❌ hint ≥ 3× prior ou retour du cas `57 kg` → `PROD NOT READY_FOR_OVERLOAD`, rollback SHA ou bugfix ciblé immédiat.

**Interaction avec UI renovation :**
Ce mini-gate ne bloque pas le démarrage des sprints UI, mais doit être suivi comme dette prod critique jusqu'à exécution.
