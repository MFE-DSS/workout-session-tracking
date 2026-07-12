# Sprint Sb_BI_01.activation-readiness — Audit

**Statut** : 🟢 AUDIT COMPLET — activation **deferred until after dogfood + explicit GO**
**Type** : ACTIVATION READINESS / AUDIT — docs-only, **aucun code, aucune activation**
**Date** : 2026-07-11
**Plan** : [`strategy/Sb_BI_01_ACTIVATION_READINESS_PLAN.md`](strategy/Sb_BI_01_ACTIVATION_READINESS_PLAN.md)

---

## 0. Méthode

Audit **read-only** de la mécanique du flag, du workflow deploy et des scripts smoke,
pour produire un **plan d'activation contrôlée** sans rien activer. Aucun fichier
modifié.

---

## 1. Mécanique du flag (audit `config.py`)

| Aspect | Constat |
|---|---|
| Déclaration | `body_intelligence_enabled: bool = Field(default=False)` (`config.py:95`) |
| Classe | `Settings(BaseSettings)` (pydantic-settings) ; `model_config = SettingsConfigDict(env_file=".env", ...)` |
| Lecture env | variable d'env `BODY_INTELLIGENCE_ENABLED` (pydantic mappe le champ ↔ l'env, majuscules) |
| Gate route | `body_intelligence.py` : `require_body_intelligence_enabled()` → **404** si flag OFF (dépendance router-level, avant auth) |
| Défaut | **False** — toute install/CI est OFF par défaut (sécurité) |

**Conséquence** : activer = poser `BODY_INTELLIGENCE_ENABLED=1` dans le `.env` prod +
restart systemd. **Aucun fichier repo modifié** ; le défaut `False` reste.

---

## 2. Workflow deploy (audit `deploy-production.yml`)

| Aspect | Constat |
|---|---|
| Déclencheur | `workflow_dispatch` (manuel) |
| Input `ref` | « Ref to deploy (branch or full SHA). **Default: main** » — ⚠️ `main` est **invalide** dans ce repo (cf. Sx_32) → passer un **SHA/branche réel** |
| Input `skip_smoke` | défaut `false` (smoke joué automatiquement) |
| Environnement | `environment: production` |
| Étape smoke | `Run smoke_deploy.sh on VPS` si `skip_smoke == false` |

---

## 3. Scripts ops disponibles

| Script | Rôle |
|---|---|
| `scripts/deploy_prod.sh` | déploiement VPS (vérifie `.env`, restart systemd, rollback manuel documenté) |
| `scripts/deploy_from_github_actions.sh` | pont CI → VPS |
| `scripts/smoke_deploy.sh` | smoke post-deploy (public + auth-redirect) |
| `scripts/write_deploy_state.py` | état de deploy (deploy.sha pour `/healthz/strict`) |

---

## 4. Smoke actuel (audit `smoke_deploy.sh`)

**Endpoints publics vérifiés** : `/healthz` (200), `/healthz/strict` (200),
`/welcome` `/login` `/register` (200).
**Routes privées** (attendu **303** redirect login) : `/`, `/library`, `/science`,
`/history`, `/progress`, `/export`, `/export/sessions.json`, `/export/sessions.csv`.
**Autres** : backup refresh offline, `check_alembic_drift`.

**Manque identifié** : `/body/intelligence` **n'est pas** dans le smoke (normal, flag
off aujourd'hui). Le futur build d'activation devra **ajouter** un
`check_auth_redirect "GET /body/intelligence" "/body/intelligence"` (attendu **303**
flag ON). **Non fait ici** (docs-only).

---

## 5. Comportement `/body/intelligence` selon le flag

| Flag | Anonyme | Authentifié |
|---|---|---|
| **OFF** (prod aujourd'hui) | **404** (gate router-level avant auth) | **404** |
| **ON** (après activation) | **303** (redirect login) | **200** (Zone Cards + Drill) |

→ **Preuve d'activation sans compte prod** : `/body/intelligence` passant de **404 →
303** suffit à valider l'activation, **sans se connecter**.

---

## 6. `/healthz/strict` (monitoring)

Expose (audit `health.py`) : `db.ok`, `backup_dir` présence, dernier backup
présence + intégrité, `deploy.sha`. → utilisable comme check GO/NO-GO post-deploy.

---

## 7. Consommateurs partagés à surveiller

`compute_physique_dashboard` (réutilisé en lecture par les Zone Cards) alimente aussi
**leaderboard** et **user_profile**. Après activation, surveiller qu'ils rendent
toujours (pas de 500) — l'activation ne change pas le service, mais le monitoring le
confirme.

---

## 8. Plan produit (résumé — détail dans le plan)

**Option A** : readiness docs-only maintenant, activation après dogfood. Activation
par **variable d'env prod** (`BODY_INTELLIGENCE_ENABLED=1`), deploy via
`deploy-production.yml` (`ref=<SHA réel>`, jamais `main`), smoke **sans compte prod**
(303), rollback flag en secondes, critères GO/NO-GO explicites.

---

## 9. Non-goals

Pas de code / test / config prod / modification flag / deploy / release tag / smoke
prod réel / compte prod personnel / modification `/physique` / modification
`/body/intelligence`.

---

## Verdict

**Verdict :** 🟢 **Sb_BI_01.activation-readiness — AUDIT COMPLET, activation deferred.**

La mécanique est claire : flag pydantic lu depuis le `.env` prod (défaut `False`),
deploy `workflow_dispatch` (`ref` réel, jamais `main`), smoke public + auth-redirect.
Le plan d'activation contrôlée est **entièrement cadré** (préconditions dont dogfood +
GO, activation par env, deploy, smoke sans compte prod via le 404→303, rollback flag,
monitoring, GO/NO-GO). Manque identifié pour le futur build : ajouter
`/body/intelligence` au smoke. **Rien activé/déployé/modifié dans ce sprint.**
Aucun code touché.
