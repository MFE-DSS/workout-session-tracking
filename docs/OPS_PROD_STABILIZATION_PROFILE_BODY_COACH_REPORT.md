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

## 6. Backup pré-déploiement — À ACTER PAR L'OPÉRATEUR

⚠️ **Cette session CLI n'a pas d'accès VPS.** Le backup SQLite pré-déploiement doit être joué manuellement sur le serveur cible avant le rollout. Cocher ci-dessous après exécution :

- [ ] `sqlite3 spignos.db ".backup /var/backups/spignos_pre_stabilization_$(date +%Y%m%d_%H%M%S).db"` (ou équivalent selon setup)
- [ ] Backup taille cohérente (> 0 octets, > 90% de la taille de `spignos.db`)
- [ ] Backup lisible : `sqlite3 <backup> "SELECT count(*) FROM users;"` retourne > 0

## 7. Smoke tests prod — À ACTER PAR L'OPÉRATEUR

⚠️ **Cette session CLI ne peut pas jouer de smoke tests contre la prod.** Les URLs, credentials et logs systemd/nginx sont hors de portée. Case à cocher après exécution manuelle depuis un navigateur mobile ou curl externe :

### 7.1 Auth / navigation

- [ ] Login OK
- [ ] `/` (home) OK
- [ ] Nav principale sans 500 dans logs

### 7.2 `/profile`

- [ ] 200
- [ ] Carte « Lecture corporelle » visible (uniquement si `BODY_INTELLIGENCE_ENABLED=true`)
- [ ] Lien « Voir Body Intelligence » cliquable
- [ ] Redirige vers `/body/intelligence`

### 7.3 `/body/intelligence`

- [ ] 200 (200 si flag ON, 404 si flag OFF — flag OFF = FAIL du gate)
- [ ] Headline visible
- [ ] 7 blocs visibles OU empty states propres
- [ ] Badges Mesuré / Dérivé / Inféré / Hors de portée visibles
- [ ] Bloc « Hors de portée » always-on visible avec limites
- [ ] Aucun wording interdit (tu es gras / diagnostic / etc.)

### 7.4 `/coach-report`

- [ ] 200
- [ ] Bloc `1bis. Snapshot Body Intelligence` visible entre section 1 et 2
- [ ] CTA « Voir le détail » présent + fonctionnel
- [ ] Pas de duplication des 7 blocs (juste snapshot compact)

### 7.5 Session detail + Sx_30 overload (le test le plus critique)

- [ ] Ouvrir une séance en cours avec un exercice à historique (ex. `push-a E5` élévations latérales câble)
- [ ] Hint overload s'affiche **uniquement** sur la carte active
- [ ] `value=""` reste vide (aucun pré-remplissage)
- [ ] Placeholder `≈ N kg` cohérent avec « Dernière fois »
- [ ] **CRITIQUE :** exercice « élévation latérale câble » (5 kg historique) ne propose PAS 57 kg ni tout autre chiffre incohérent
- [ ] Exercice courant substitué → hint silencieux (aucun chiffre affiché)

### 7.6 Non-régression /body/capture-quality

- [ ] `GET /body/capture-quality` → **404** (flag `BODY_CAPTURE_QUALITY_ENABLED=false` par design)
- [ ] Aucun lien vers `/body/capture-quality` visible dans le HTML de `/profile` ni `/body/intelligence` ni `/coach-report`

### 7.7 Régression générale

- [ ] `/sessions/{id}/done` OK
- [ ] `/progress` OK
- [ ] `journalctl -u spignos-web --since "1 hour ago" | grep -i error` : aucun 500 non-attendu

## 8. Vérification bug Sx_30 (rappel critique)

Le bugfix `10732e9` corrige la contamination inter-template. Le smoke test §7.5 ci-dessus est **le** test à valider. Si le hint chiffré s'écarte de plus de 3× du prior visible (« Dernière fois »), c'est un **NO-GO immédiat** et rollback SHA précédent.

## 9. Incidents / anomalies (à remplir opérateur)

| # | Description | Sévérité | Action |
|---|---|---|---|
| 1 | | | |
| 2 | | | |

## 10. Verdict final

⚠️ **Ce verdict ne peut être posé que par l'opérateur après exécution des §6, §7, §8 ci-dessus.**

Deux verdicts possibles :

- [ ] ✅ **PROD STABLE FOR UI RENOVATION** — tous smoke tests verts, bug 57 kg non reproduit, aucun 500 dans logs
- [ ] ❌ **PROD NOT READY** — bloqueur(s) identifié(s) ci-dessous :

**Justification (3-5 lignes) :**

> _à remplir_

Signature opérateur : ______________________  Date/heure : ______________________

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

Ce gate n'autorise **PAS** :
- ❌ Toute rénovation UI
- ❌ Toute ouverture Sx_32 / PWA / Health API
- ❌ Toute ouverture Sb Body 02.2 (caméra locale)
- ❌ Activation de `BODY_ASSESSMENT_ENABLED` ou `BODY_CAPTURE_QUALITY_ENABLED`
- ❌ Aucun rollback partiel (rollback = SHA complet précédent)
