# Sprint Sx_16 Report — Prod CI/CD Pipeline Spec

**Date :** 2026-04-21
**Type :** SPEC ONLY — aucun code produit
**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6` @ commit `77fc78e`
**Livraison :** 2 documents (spec principale + ce rapport)
**Successeur :** Sb_16_prod_cicd_pipeline_build

---

## 1. Surfaces inspectées

### 1.1 Scripts et infrastructure de déploiement

- [scripts/deploy_prod.sh](../scripts/deploy_prod.sh) — script maître exécuté **sur le VPS** par l'opérateur. Backup SQLite → git pull → pip install → alembic drift → migrate → seed → systemctl restart → health checks. Robuste, testé par l'usage réel.
- [scripts/smoke_deploy.sh](../scripts/smoke_deploy.sh) — post-deploy : 6 routes publiques (attendu 200), 8 routes privées (attendu 303), backup script, verify script, alembic drift. Exit 0 seulement si tout passe.
- [scripts/backup_sessions.py](../scripts/backup_sessions.py) — dump JSON + CSV, rotation `BACKUP_RETENTION_DAYS`.
- [scripts/restore_latest_backup.py](../scripts/restore_latest_backup.py) — restauration avec safety (refuse si DB non vide).
- [scripts/verify_backup.py](../scripts/verify_backup.py) — validation du dernier dump.
- [scripts/list_backups.py](../scripts/list_backups.py) — listing.
- [scripts/check_alembic_drift.py](../scripts/check_alembic_drift.py) — drift metadata vs migrations, SQLite temporaire.
- [scripts/catalog_qa.py](../scripts/catalog_qa.py), [scripts/machine_atlas_qa.py](../scripts/machine_atlas_qa.py), [scripts/reco_calibration_report.py](../scripts/reco_calibration_report.py) — QA + observabilité business.

### 1.2 Artéfacts systemd et nginx

- [deploy/workout.service](../deploy/workout.service) — unit principale uvicorn, User=workout, `EnvironmentFile=/srv/workout/.env`, hardening (`NoNewPrivileges`, `ProtectSystem=strict`, `ReadWritePaths=/srv/workout/var`).
- `deploy/workout-backup.service` + `.timer` — dump nightly 03:30 UTC.
- `deploy/workout-backup-verify.service` + `.timer` — vérification à 04:00 UTC.
- [deploy/nginx.conf.example](../deploy/nginx.conf.example) — HTTPS → uvicorn 127.0.0.1:8000, static cache 7j, proxy headers corrects.

### 1.3 Config et Alembic

- [app/config.py](../app/config.py) — `pydantic-settings`, lit `.env`. 14 clés env identifiées (`APP_*`, `DATABASE_URL`, `BACKUP_*`, `SMTP_*`).
- [.env.example](../.env.example) — template dev présent.
- `.env.production.example` — **manquant**, attendu par `tests/test_deploy_artifacts.py`.
- `alembic.ini` — DB URL lue via `get_settings()`.
- `migrations/versions/` — 16 migrations, head `c3d5f1e82a04` (Sb_13).

### 1.4 Runbook et docs

- [deploy/README.md](../deploy/README.md) — guide OVH complet en français (provisioning, systemd, nginx, HTTPS, backups, PostgreSQL future).
- [deploy/DEPLOY_OVH.md](../deploy/DEPLOY_OVH.md) + [deploy/CHECKLISTS.md](../deploy/CHECKLISTS.md).
- [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md), [docs/PRODUCT_SPEC.md](../docs/PRODUCT_SPEC.md).

### 1.5 Tests infrastructure

- `pyproject.toml` — `requires-python = ">=3.11"`. Deps alignées avec `requirements.txt`.
- Pas de marker pytest (`ci`, `slow`). Full suite typiquement invoquée `pytest --ignore=tests/test_deploy_artifacts.py --ignore=tests/test_v1_acceptance.py -q` côté dev parce que ces deux fichiers testent l'environnement local.
- [tests/test_deploy_artifacts.py](../tests/test_deploy_artifacts.py) — 16 tests sur présence/cohérence des fichiers deploy (systemd, nginx, `.env.production.example`). **Actuellement exclu** car `.env.production.example` absent.
- [tests/test_v1_acceptance.py](../tests/test_v1_acceptance.py) — valide la config VSCode locale. Exclu en CI, restera exclu.

### 1.6 CI/CD existant

**Aucun.** Pas de `.github/workflows/`, pas de `.gitlab-ci.yml`, pas de `.pre-commit-config.yaml`.

## 2. Scripts / workflows existants repérés

Le repo est **très bien outillé** pour le déploiement manuel. Tout le paquet scripts + systemd + runbook existe et fonctionne. Ce qu'il manque n'est pas du code métier, c'est l'**orchestration CI/CD** autour de ces briques.

| Brique | Existant | Utilisable directement ? |
|--------|----------|--------------------------|
| `deploy_prod.sh` (backup + migrate + restart) | ✓ | Oui, appelé tel quel par le nouveau wrapper |
| `smoke_deploy.sh` | ✓ | Oui, exécuté via SSH depuis l'action |
| `backup_sessions.py` | ✓ | Non utilisé directement par l'action — tourne déjà en timer systemd 03:30 UTC |
| `check_alembic_drift.py` | ✓ | Utilisé en CI **et** au sein de `deploy_prod.sh` |
| `catalog_qa.py` / `machine_atlas_qa.py` | ✓ | Utilisés en CI |
| Systemd units | ✓ | Déploiement les utilise tels quels (pas d'overlay CI) |
| Nginx conf | ✓ (exemple) | Hors workflow, changements manuels |
| `.env.production.example` | ✗ | **À créer** dans Sb_16 |

## 3. Points de friction actuels (et leurs causes)

1. **Zéro traçabilité GitHub-side.** Un `git log` sur le VPS montre le SHA déployé, mais aucun tag, aucune entrée dans Actions. Si la machine opérateur change, l'historique des deploys devient opaque.
2. **Deploy et tests découplés mentalement.** Rien ne force l'opérateur à relancer la suite avant `deploy_prod.sh`. Le drift alembic est détecté (filet de sécurité du script), mais une régression métier non.
3. **Review de ce qu'on pousse inexistante.** Mono-dev ≠ pas besoin de gate. Une seconde paire d'yeux manuelle (même soi-même avec un pas conscient) élimine 80 % des erreurs stupides (config oubliée, debug print resté).
4. **`test_deploy_artifacts.py` désactivé depuis des sprints** parce qu'il manque un seul fichier (`.env.production.example`). Le créer débloque 16 tests deploy.
5. **Rollback non-automatisé.** Le runbook décrit la procédure, mais elle exige de se rappeler des commandes `git log → checkout → deploy_prod.sh` en pleine crise. Une CI/CD qui prend `ref: <previous-sha>` supprime cette friction.
6. **Concurrency informelle.** Si l'opérateur lance `deploy_prod.sh` deux fois (oubli de la première instance), les deux exécutions se marchent potentiellement dessus (sur le backup, sur `git pull`). Unlikely en pratique, mais le workflow élimine cette classe d'erreur.

## 4. Arbitrages clés

### 4.1 Modèle de déploiement : SSH + fetch + checkout SHA

Les 4 modèles ont été évalués §D.3. **SSH + checkout SHA retenu** parce qu'il minimise le changement structurel (le VPS est déjà un clone git) tout en apportant la garantie critique : **le SHA en prod = le SHA testé par CI**. Rsync et artifact bundle demanderaient une refonte de `deploy_prod.sh` — non justifiée.

### 4.2 Docker hors scope

Contrainte explicite du sprint. Même sans contrainte, l'argument tient : `deploy_prod.sh` + systemd sont mûrs, et empiler Docker par-dessus un VPS mono-instance ajoute une couche (image build, registry, docker-compose ou systemd unit docker, networking) pour un bénéfice marginal. Si on grandissait vers plusieurs instances ou un multi-service, Docker ferait sens — **pas V1**.

### 4.3 Deux workflows, pas un seul

Certains pipelines monoblocs déclenchent tests → deploy d'un coup sur push main. **Rejeté** pour SPIGNOS : on veut un pas conscient entre « le code est testé » et « le code est en prod ». La séparation CI / deploy + l'environment `production` avec reviewer incarnent ce pas conscient sans ajouter de friction démesurée.

### 4.4 Trigger manuel, pas push automatique

`workflow_dispatch` only en V1. Pas de `push: main → deploy` automatique. Raison : le reviewer et le clic conscient sont la vraie valeur de la pipeline en mono-dev. L'automatisation auto-push arrivera en V1.1 après 2 mois de confiance acquise, documentée dans le runbook.

### 4.5 Tag git au lieu de release GitHub

Un tag `deploy/prod/<date>-<sha7>` est suffisant pour la traçabilité. GitHub Release ajouterait du formalisme (changelog, artifacts) sans ROI tangible pour un mono-dev. Si des releases deviennent utiles plus tard, on pourra générer à partir des tags.

### 4.6 Restaurer la suite `test_deploy_artifacts.py`

C'est le signal le plus visible que le build Sb_16 a touché à la partie CI/CD du repo : 16 tests réactivés d'un coup, full suite passe de ~696 à ~712. Effet collatéral souhaité.

### 4.7 Un seul environment `production`, pas de staging

Mono-dev + SSR + volume = 1 utilisateur ne justifient pas un second VPS. Les tests + le smoke couvrent le besoin « vérifier avant public ». Staging en V2 si le volume passe à un multi-utilisateur non-test.

## 5. Pourquoi cette architecture est la bonne pour SPIGNOS

1. **Elle respecte l'existant.** Les briques `deploy_prod.sh`, systemd, nginx, backup/verify ne sont pas recodées. Elles sont **orchestrées**.
2. **Elle est proportionnée au produit.** Un mono-utilisateur + un VPS + un fichier SQLite + zéro JS = pas besoin de container registry, blue-green, canary, k8s.
3. **Elle tient dans la tête.** Deux workflows YAML de ~40 lignes chacun, un wrapper bash de 30 lignes, un environment GitHub, 4 secrets. Tout inspectable en une heure.
4. **Elle rend le rollback trivial.** Un SHA plus ancien = un nouveau `workflow_dispatch`.
5. **Elle rend la traçabilité permanente.** Tag git par deploy, logs GitHub Actions, SHA explicite.
6. **Elle respecte les garde-fous sécurité** mentionnés dans la review `SECURITY_REVIEW_01_REPORT.md` : principe du moindre privilège via sudoers restreint, clé SSH scopée, StrictHostKeyChecking yes.
7. **Elle est testable localement partiellement.** CI peut être simulé via `act` si besoin. Deploy workflow ne peut pas être simulé intégralement (dépend du VPS), mais le wrapper `deploy_from_github_actions.sh` est du bash pur, simple à lire et à fail-fast.
8. **Elle ferme une dette observable** — le test `test_deploy_artifacts.py` est réactivé, le commit `test_v1_acceptance.py` reste volontairement exclu (c'est un check VSCode local, pas CI).

## 6. Ambiguïtés restantes à résoudre en phase build

1. **Le user `deploy` existe-t-il déjà sur le VPS ?** Probablement non. Le runbook Sb_16 devra inclure `adduser --system --group --shell /bin/bash deploy`.
2. **OVH rotate-t-il les IPs après un redémarrage majeur ?** Si oui, le secret `DEPLOY_SSH_KNOWN_HOSTS` deviendra obsolète. Documenter la procédure de refresh dans le runbook.
3. **Le reviewer en mono-dev reste-t-il crédible ?** Auto-approbation est un pas conscient mais pas une vraie review. Accepter la limite V1 ; un `wait_timer: 5 minutes` dans l'environment peut être ajouté plus tard pour forcer un temps de réflexion si besoin.
4. **Si CI échoue sur main après un merge "no-op" (ex. flakiness)**, faut-il bloquer les deploys ? V1 : non (le reviewer est la gate finale). V1.1 : oui, si on bascule en `push: main → deploy` auto.
5. **La protection de branche main** doit-elle inclure `require signed commits` ? Probablement pas V1 — friction élevée, bénéfice marginal mono-dev.

## 7. Pourquoi c'est le bon prochain sprint

- **Dette opérationnelle critique.** Tout le produit marche, mais son déploiement reste manuel. Un accident (perte de machine opérateur, erreur de frappe sous stress) peut sérieusement dégrader l'usage.
- **ROI élevé.** 4–6 h de build contre : traçabilité permanente, rollback 2-clics, review gate, zéro drift oubliée, backup pré-migration garanti, réactivation d'une suite de tests deploy.
- **Pas de blocage produit concurrent.** Sb_13 attend un dogfooding 7 jours avant toute décision. Sx_16 ne touche ni le moteur de reco, ni le catalogue, ni aucune surface utilisateur — il renforce l'infrastructure.
- **Débloque les sprints suivants.** Programme-builder (Sx_11b), calibration (Sx_13.1), squad v2 (Sx_11c) — tous bénéficient d'un pipeline de deploy fiable avant d'être buildés.
- **Sécurité.** `SECURITY_REVIEW_01_REPORT.md` a validé l'app, mais la chaîne de deploy n'a pas été auditée. Automatiser et formaliser = réduire l'attack surface humaine.

## 8. Recommandation explicite du build suivant

**Sb_16 — Prod CI/CD Pipeline build**, scope §O de la spec principale.

Livrables principaux :
- `.github/workflows/ci.yml`
- `.github/workflows/deploy-production.yml`
- `scripts/deploy_from_github_actions.sh`
- `.env.production.example`
- `docs/CICD_RUNBOOK.md`
- Sprint report.

Effort estimé : **4–6 h** code/docs + ~30 min d'activation opérateur sur VPS + GitHub UI.

**Préconditions avant Sb_16 :**
- Accès OVH confirmé (SSH fonctionnel avec le user actuel).
- Accès GitHub confirmé avec droits settings (pour créer secrets + environment + protection branche).
- Fenêtre opérationnelle réservée (≈ 1 h) pour tester le premier `workflow_dispatch` sans risque.

**Séquence post-Sb_16 :**
1. Faire 2-3 deploys via le workflow.
2. Si OK, basculer sur `push: main → deploy` automatique en V1.1 (édition mineure du YAML).
3. Reprendre le rail produit : passe dogfooding Sb_13, puis arbitrage Sx_11b / Sx_11c / Sx_13.1.

## 9. Livrables produits par ce sprint

| Fichier | Action |
|---------|--------|
| `docs/strategy/SPIGNOS_PROD_CICD_PIPELINE_SPEC_v1.md` | New |
| `docs/SPRINT_Sx_16_prod_cicd_pipeline_spec_REPORT.md` | New (ce rapport) |

Aucun code, aucune migration, aucun test.

## 10. Synthèse exécutive

- État actuel : **zéro CI/CD automatisée**, déploiement manuel via `deploy_prod.sh` sur VPS. Les briques (scripts, systemd, nginx, runbook) sont toutes là et solides.
- Architecture cible : **deux workflows GitHub Actions** (`ci.yml` indépendant, `deploy-production.yml` manuel), **SSH + fetch + checkout SHA exact** comme modèle de déploiement, **environment `production` avec reviewer**, **concurrency group sérialisé**, **tag git par deploy** pour la traçabilité.
- Nouveau wrapper VPS **minimal** (~30 lignes bash) qui enchaîne `git fetch → reset --hard <SHA> → deploy_prod.sh → smoke_deploy.sh`.
- Sécurité : clé SSH scopée à un user `deploy` dédié, sudoers `NOPASSWD` restreint au seul script, `StrictHostKeyChecking=yes`, secrets scopés à l'environment.
- Rollback par re-déclenchement du workflow sur SHA précédent. Backup SQLite pré-migration déjà géré par `deploy_prod.sh`.
- **Zéro Docker, zéro K8s**, cohérent avec le produit mono-VPS SSR + SQLite.
- Build Sb_16 estimé **4–6 h**, débloque `test_deploy_artifacts.py` au passage (~16 tests réactivés), full suite cible **~710 tests**.
