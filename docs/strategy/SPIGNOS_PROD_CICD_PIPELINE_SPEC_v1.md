# SPIGNOS Production CI/CD Pipeline Spec v1

**Sprint ID :** Sx_16_prod_cicd_pipeline_spec
**Date :** 2026-04-21
**Statut :** SPEC ONLY — aucun code engagé par ce document
**Prérequis :** App V1 déployée manuellement sur OVH VPS, runbook `deploy/README.md` stable
**Successeur :** Sb_16_prod_cicd_pipeline_build (proposé §O)

---

## A. Statut du document

Spec complète de la pipeline cible. Pas d'usine à gaz : une pipeline fiable, simple, traçable, adaptée au contexte réel SPIGNOS (OVH VPS Ubuntu + systemd + Nginx + Alembic + SQLite + FastAPI SSR). Pas de Docker dans ce sprint — le déploiement systemd actuel est stable et documenté, l'ajouter créerait plus de risque qu'il n'en résout.

## B. Contexte déploiement actuel

### B.1 Ce qui existe déjà dans le repo (inventorié)

- [deploy/README.md](../deploy/README.md) — runbook OVH complet (provisioning, git clone, venv, Alembic, seed, systemd, nginx, HTTPS, backups).
- [deploy/DEPLOY_OVH.md](../deploy/DEPLOY_OVH.md), [deploy/CHECKLISTS.md](../deploy/CHECKLISTS.md).
- Unités systemd commitées : `workout.service`, `workout-backup.service`, `workout-backup.timer`, `workout-backup-verify.service`, `workout-backup-verify.timer`.
- [deploy/nginx.conf.example](../deploy/nginx.conf.example) — reverse proxy + static + HTTPS.
- [scripts/deploy_prod.sh](../scripts/deploy_prod.sh) — **script maître sur VPS** : backup SQLite → `git pull` → `pip install` → alembic drift check → `alembic upgrade head` → `python -m scripts.seed_db` → `systemctl restart workout` → vérifie `/healthz` et `/healthz/strict`.
- [scripts/smoke_deploy.sh](../scripts/smoke_deploy.sh) — vérifs post-deploy : routes publiques (200), routes privées (303), backup script, verify script, alembic drift.
- [scripts/backup_sessions.py](../scripts/backup_sessions.py), `verify_backup.py`, `restore_latest_backup.py`, `list_backups.py` — jeu de backup JSON + CSV, rotation `BACKUP_RETENTION_DAYS` (30 j par défaut).
- [scripts/check_alembic_drift.py](../scripts/check_alembic_drift.py) — CLI de détection drift modèle vs migrations.
- `alembic.ini` — DB URL lue depuis `app.config.get_settings()` dans `migrations/env.py`.
- `.env.example` (commité) — template dev uniquement.
- `.env.production.example` **manquant** (test `tests/test_deploy_artifacts.py` l'attend, donc actuellement exclu de la suite).
- `pyproject.toml` Python ≥ 3.11, `requirements.txt` non lockfile.
- **16 migrations** sous `migrations/versions/`, head actuelle `c3d5f1e82a04` (Sb_13).

### B.2 Flow actuel du déploiement

1. Opérateur se connecte en SSH sur le VPS OVH.
2. `cd /srv/workout && sudo bash scripts/deploy_prod.sh`.
3. Le script enchaîne : backup → pull → deps → migration → restart → health check.
4. Opérateur exécute ensuite à la main `sudo -u workout bash scripts/smoke_deploy.sh`.
5. Si quelque chose casse : rollback manuel via `git checkout <previous-sha>` + nouveau `deploy_prod.sh`, et éventuellement `python scripts/restore_latest_backup.py`.

## C. Limites du mode manuel actuel

1. **Aucune traçabilité côté GitHub** — impossible de dire « quel SHA est en prod, déployé par qui, à quelle heure » sans ouvrir un terminal SSH.
2. **Dépend d'une machine d'opérateur** — risque d'oubli, de manipulation incorrecte, de divergence entre dev et prod.
3. **Tests ne sont pas un pré-requis** — rien n'empêche un `git push` contenant une régression d'atterrir sur prod si l'opérateur fait `deploy_prod.sh` sans relancer la suite.
4. **Pas de serialization** — deux déploiements simultanés (rare mais possible) peuvent se marcher sur les pieds.
5. **Pas de gate de review** — aucun moment où un humain dit « je valide ce SHA pour prod ».
6. **Rollback sous-documenté** — le runbook mentionne la stratégie mais ne l'automatise pas.
7. **Test `test_deploy_artifacts.py` désactivé** — `.env.production.example` manquant, donc une partie de la couverture deploy est aveugle.

Ce n'est pas urgent au sens où le système marche. C'est urgent au sens où **à mesure que le produit avance (Sb_11a, Sb_12, Sb_13, catalog v12), la surface qui peut casser grandit**, et le déploiement manuel devient le maillon faible.

## D. Architecture CI/CD cible

### D.1 Deux workflows GitHub Actions séparés

1. **`.github/workflows/ci.yml`** — déclenché sur chaque `pull_request` et chaque `push` vers `main`.
   - Checkout + setup Python 3.11.
   - `pip install -r requirements.txt` + deps dev pytest, httpx.
   - `pytest --ignore=tests/test_v1_acceptance.py` (inclut `test_deploy_artifacts.py` une fois `.env.production.example` ajouté).
   - `python scripts/catalog_qa.py`.
   - `python scripts/machine_atlas_qa.py`.
   - `python scripts/check_alembic_drift.py`.
   - Sortie : statut PR / statut main.

2. **`.github/workflows/deploy-production.yml`** — déclenché **uniquement manuellement** (`workflow_dispatch`) en V1. Optionnellement `push: main` en V1.1 après confiance acquise.
   - Input : `ref` (branche ou SHA, défaut `main`) + `skip_smoke` (bool, défaut `false`).
   - Environment : `production` (avec required reviewer, voir §G).
   - Concurrency group : `production-deploy` sérialisé.
   - Étapes : checkout → setup SSH via secrets → exécute `scripts/deploy_from_github_actions.sh` sur le VPS → exécute `smoke_deploy.sh` → tague le repo → notifie (commentaire commit).

**Pourquoi deux workflows séparés :**
- Le CI doit tourner sur chaque PR **sans** toucher à la prod.
- Le deploy doit être **explicite**, jamais automatique sans validation.
- Permet à l'équipe de pousser sur une branche sans déclencher de déploiement.

### D.2 Deux environnements GitHub

- **`production`** — requiert 1 reviewer (soi-même en mono-dev est acceptable, le point est la friction consciente). Porte les secrets SSH. Protège contre les déploiements accidentels.

Pas de `staging` V1. Le volume (1 utilisateur) et la nature SSR-simple du produit ne justifient pas un second VPS.

### D.3 Modèle de déploiement retenu — SSH + git fetch + checkout SHA exact

**Décision : SSH vers le VPS, fetch, checkout du SHA exact que GitHub Actions a testé.**

#### Options évaluées

| Modèle | Pour | Contre | Verdict |
|--------|------|--------|---------|
| **SSH + git fetch + checkout SHA** | Utilise l'infrastructure déjà en place (`/srv/workout` est déjà un clone git). Minimal changement. Traçabilité parfaite (le SHA en prod = le SHA testé). | Le VPS doit rester clone git. Pas de bundle portable. | **Retenu** |
| Rsync d'un bundle construit par Actions | Pas besoin de git sur le VPS. Portable. | Change la structure VPS, exige réécriture de `deploy_prod.sh`. Plus de risque au refactor. | Rejeté — trop invasif pour le gain |
| Artifact `tar.gz` uploadé sur un object storage puis pull par VPS | Découple encore plus. | Ajoute un object store (dépendance) pour un besoin que git résout. Over-engineering. | Rejeté |
| Docker image + registry + pull + restart | Architecture cloud-native classique. | Pas dans le scope (contrainte sprint). Ajoute docker-build + registry + secrets. Exige revisite systemd → compose/swarm/k8s. | Rejeté V1 |

**Justification retenue :** l'existant est cohérent, `deploy_prod.sh` fonctionne, systemd unit est stable. Le bon niveau d'abstraction est de **orchestrer l'existant**, pas de le remplacer.

## E. Choix du modèle de déploiement recommandé

Voir §D.3. En synthèse :

1. GitHub Actions SSH vers le VPS en tant qu'utilisateur `deploy` dédié (non-root, sudoer restreint).
2. L'action exécute `sudo /srv/workout/scripts/deploy_from_github_actions.sh <SHA>`.
3. Ce wrapper (nouveau) :
   - `cd /srv/workout`
   - `sudo -u workout git fetch --prune origin`
   - `sudo -u workout git reset --hard <SHA>`
   - `sudo -u workout bash scripts/deploy_prod.sh` (existant inchangé)
4. L'action enchaîne avec `sudo -u workout bash scripts/smoke_deploy.sh`.
5. Tag git `deploy/prod/<YYYY-MM-DD-HHMM>-<sha7>` poussé pour traçabilité.

**Le SHA déployé = le SHA testé par CI.** Garantie forte.

## F. Workflows GitHub Actions recommandés

### F.1 `ci.yml` — structure

```yaml
name: CI
on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"
      - run: pip install -r requirements.txt pytest httpx
      - run: pytest --ignore=tests/test_v1_acceptance.py -q
      - run: python scripts/catalog_qa.py
      - run: python scripts/machine_atlas_qa.py
      - run: python scripts/check_alembic_drift.py
```

Notes :
- `test_v1_acceptance.py` reste exclu (checks VSCode local).
- `test_deploy_artifacts.py` rentre dans la suite dès que `.env.production.example` existe — prévu dans Sb_16.
- `concurrency: cancel-in-progress: true` annule la run CI précédente sur la même branche quand on re-pousse → économise les minutes GH.

### F.2 `deploy-production.yml` — structure

```yaml
name: Deploy production
on:
  workflow_dispatch:
    inputs:
      ref:
        description: "Ref to deploy (branch or SHA)"
        required: true
        default: "main"
      skip_smoke:
        description: "Skip smoke_deploy.sh (emergency only)"
        required: false
        type: boolean
        default: false

permissions:
  contents: write   # needed to push the deploy tag

concurrency:
  group: production-deploy
  cancel-in-progress: false   # deploys queue, never collide

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ inputs.ref }}
          fetch-depth: 0

      - name: Resolve full SHA
        id: sha
        run: echo "sha=$(git rev-parse HEAD)" >> "$GITHUB_OUTPUT"

      - name: Setup SSH
        run: |
          mkdir -p ~/.ssh
          echo "${{ secrets.DEPLOY_SSH_KEY }}" > ~/.ssh/id_deploy
          chmod 600 ~/.ssh/id_deploy
          echo "${{ secrets.DEPLOY_SSH_KNOWN_HOSTS }}" > ~/.ssh/known_hosts
          chmod 600 ~/.ssh/known_hosts

      - name: Deploy
        run: |
          ssh -i ~/.ssh/id_deploy \
              -o UserKnownHostsFile=~/.ssh/known_hosts \
              -o StrictHostKeyChecking=yes \
              ${{ secrets.DEPLOY_SSH_USER }}@${{ secrets.DEPLOY_SSH_HOST }} \
              "sudo /srv/workout/scripts/deploy_from_github_actions.sh ${{ steps.sha.outputs.sha }}"

      - name: Smoke
        if: inputs.skip_smoke == false
        run: |
          ssh -i ~/.ssh/id_deploy \
              -o UserKnownHostsFile=~/.ssh/known_hosts \
              ${{ secrets.DEPLOY_SSH_USER }}@${{ secrets.DEPLOY_SSH_HOST }} \
              "sudo -u workout bash /srv/workout/scripts/smoke_deploy.sh"

      - name: Tag deploy
        run: |
          TAG="deploy/prod/$(date -u +%Y-%m-%d-%H%M)-$(echo ${{ steps.sha.outputs.sha }} | cut -c1-7)"
          git tag "$TAG" ${{ steps.sha.outputs.sha }}
          git push origin "$TAG"
```

Notes :
- `skip_smoke` : escape hatch d'urgence, jamais utilisé par défaut.
- Tag `deploy/prod/...` pousse une trace permanente dans le repo.
- `fetch-depth: 0` nécessaire pour push un tag cross-SHA.

## G. Secrets / GitHub Environment / permissions

### G.1 Secrets GitHub (dans l'environment `production`)

| Secret | Contenu | Source |
|--------|---------|--------|
| `DEPLOY_SSH_HOST` | ex. `vps-xxx.ovh.net` ou IP | Config OVH |
| `DEPLOY_SSH_USER` | `deploy` (nouveau user sur le VPS) | À créer lors du build |
| `DEPLOY_SSH_KEY` | Clé privée ed25519 | Générée localement, pubkey ajoutée dans `~deploy/.ssh/authorized_keys` |
| `DEPLOY_SSH_KNOWN_HOSTS` | Ligne `vps-xxx ecdsa-sha2-nistp256 AAAAE...` | `ssh-keyscan <host>` |

Pas besoin de `DEPLOY_APP_DIR` en secret — le chemin `/srv/workout` est publiquement connu (déjà dans le runbook), pas sensible.

### G.2 Environment `production` — protections

- **Required reviewer :** 1 approbation. En mono-dev, on s'auto-approuve ; l'important est le pas conscient « je valide ce SHA ».
- **Wait timer :** 0 min V1 (pas utile).
- **Deployment branches :** `main` uniquement.
- **Secrets scopés :** visibles seulement depuis un run sur l'environment `production`, impossible à lire depuis `ci.yml`.

### G.3 Permissions GitHub du workflow

- `ci.yml` : `contents: read` seul.
- `deploy-production.yml` : `contents: write` (pour pousser le tag). Rien d'autre (pas de `issues`, pas de `pull-requests`).

### G.4 Sudoers sur le VPS

L'utilisateur `deploy` reçoit un sudoers restrictif :

```
# /etc/sudoers.d/spignos-deploy
deploy ALL=(root) NOPASSWD: /srv/workout/scripts/deploy_from_github_actions.sh
deploy ALL=(workout) NOPASSWD: /bin/bash /srv/workout/scripts/smoke_deploy.sh
```

**Aucun autre privilège.** Le wrapper `deploy_from_github_actions.sh` est le seul point d'entrée.

## H. Déroulé exact d'un déploiement

### H.1 Chemin nominal (15 étapes)

1. Dev pousse sur une branche et ouvre une PR.
2. `ci.yml` se déclenche sur la PR → tests + QA scripts verts.
3. PR review + merge vers `main`.
4. `ci.yml` se re-déclenche sur le merge commit dans `main`.
5. Dev va sur GitHub → Actions → « Deploy production » → Run workflow → `ref: main` → Run.
6. GitHub demande l'approbation du reviewer (environment production).
7. Reviewer valide.
8. Le workflow checkout `main`, résout le full SHA.
9. Setup SSH depuis les secrets.
10. SSH vers VPS, exécute `sudo /srv/workout/scripts/deploy_from_github_actions.sh <SHA>`.
11. Sur VPS, le wrapper fait :
   - `git fetch --prune origin`
   - `git reset --hard <SHA>`
   - `bash scripts/deploy_prod.sh` qui enchaîne backup SQLite → pip install → `alembic upgrade head` → `scripts/seed_db.py` → `systemctl restart workout` → vérifie `/healthz` et `/healthz/strict`.
12. SSH re-rentré pour lancer `smoke_deploy.sh` → routes publiques 200, privées 303, backup script OK, verify OK, alembic clean.
13. Si smoke passe : tag `deploy/prod/2026-04-21-2130-<sha7>` poussé vers origin.
14. Workflow termine vert, notification GH standard.
15. Dev vérifie visuellement `/` en prod.

### H.2 Chemin d'échec à l'étape 11 (deploy_prod.sh plante)

- `deploy_prod.sh` exit non-zéro → SSH remonte le code → workflow échoue.
- Pas de tag poussé.
- Backup SQLite a été pris au début → restauration possible via `restore_latest_backup.py` ou `cp var/backups/workout_pre_deploy_*.db var/workout.db`.
- Service systemd reste sur l'ancien code tant que `git reset` n'a pas été effectué avant le restart → voir §H.4.

### H.3 Chemin d'échec à l'étape 12 (smoke fail après deploy_prod OK)

- Le nouveau code est en place et tourne.
- Le smoke détecte une régression (route 500, export cassé, etc.).
- Workflow échoue sans tag.
- Dev doit décider rollback manuel (§I).

### H.4 Ordre des opérations dans `deploy_prod.sh` (rappel, déjà existant)

1. Backup SQLite (snapshot `.backup` atomique).
2. `git pull` (ici devenu sans effet car `git reset --hard` déjà fait par le wrapper).
3. `pip install -r requirements.txt`.
4. Alembic drift check → abort si drift.
5. `alembic upgrade head`.
6. Seed idempotent (catalogue + method_rules).
7. `systemctl restart workout`.
8. Vérif `/healthz` et `/healthz/strict` HTTP 200.

Le script **n'appelle pas** `nginx -t` + `systemctl reload nginx` car la config nginx ne change pas d'un deploy à l'autre (elle vit dans `/etc/nginx/sites-available/workout`, pas dans le repo déployé). Si elle doit changer, c'est un deploy dédié documenté (voir §I.5).

## I. Rollback / failure handling

### I.1 Rollback rapide vers SHA précédent

Le chemin principal : re-déclencher `deploy-production.yml` avec `ref: <previous-sha>`. Le SHA précédent est connu via :
- Le dernier tag `deploy/prod/*` dans le repo.
- `git log` sur `main`.

`deploy_prod.sh` appelé avec un SHA plus ancien refait la boucle complète : backup → checkout → pip install → alembic → restart. Rapide (< 2 min typiquement).

### I.2 Rollback avec restauration de la base

Si la migration a corrompu la base (peu probable, migrations additives, mais possible en cas de bug dans un data migration) :

1. `systemctl stop workout`.
2. `python scripts/restore_latest_backup.py` (restaure le dump JSON le plus récent).
3. Re-deploy SHA précédent via workflow.
4. Investiguer avant de refaire un push.

### I.3 Limite connue — migration additive déjà appliquée

Une migration `a19c4e3b7f21 → c3d5f1e82a04` (Sb_13 `creation_source`) est additive : rollback SHA ne rejoue pas automatiquement un `alembic downgrade`. Comportement attendu : la colonne reste dans la base, le vieux code l'ignore (les champs non utilisés n'importent pas à SQLAlchemy). **Pas un problème en pratique pour des migrations additives.**

Pour une migration destructive : **pas de rollback automatique**. Nécessite décision humaine + `alembic downgrade -1` manuel + potentielle restauration depuis backup.

### I.4 Concurrency

`concurrency: group: production-deploy, cancel-in-progress: false` → deux déclenchements simultanés se mettent en file, ne se marchent pas dessus. Important si on combine push main + workflow_dispatch manuel.

### I.5 Changement de la config Nginx

Hors scope du workflow principal. Procédure manuelle :
1. Éditer `/etc/nginx/sites-available/workout` sur le VPS.
2. `sudo nginx -t`.
3. `sudo systemctl reload nginx`.
4. Commiter le diff dans `deploy/nginx.conf.example` à titre documentaire.

Automatiser ça doublerait la complexité du workflow pour un cas très rare. Refusé V1.

## J. Sécurité et garde-fous

| Garde-fou | Mise en œuvre |
|-----------|---------------|
| Clé SSH dédiée au deploy | Nouvelle paire ed25519, pubkey dans `~deploy/.ssh/authorized_keys` avec `from="GH_IP_RANGES"` optionnel |
| Pas d'accès root direct | `deploy` est un user sans sudo général, `NOPASSWD` restreint au seul script de deploy |
| Secrets jamais logués | Workflow utilise `::add-mask::` implicite de GH sur tout secret |
| `StrictHostKeyChecking=yes` | Évite le MITM sur le canal SSH |
| `known_hosts` pinné | Stocké comme secret, mis à jour si la fingerprint VPS change |
| Environment reviewer | Force un clic conscient avant deploy |
| Concurrency group | Serialize les runs, évite collision |
| Tag git post-deploy | Trace immuable dans le repo |
| Backup pré-migration | Pris automatiquement par `deploy_prod.sh` au début |
| Drift alembic bloquant | `deploy_prod.sh` abort si drift détecté |
| Deploy branches limitées | Environment limité à `main` |
| Permissions workflow minimales | `contents: read` CI, `contents: write` deploy (tag only) |
| Pas de secret fuite via PR | Les secrets d'env sont hors de portée d'une PR tierce (scoped environment) |
| Force-push sur main | Protection de branche recommandée (§K.5) |

## K. Structure de fichiers recommandée

### K.1 Nouveaux fichiers (Sb_16 va les créer)

```
.github/
  workflows/
    ci.yml
    deploy-production.yml
scripts/
  deploy_from_github_actions.sh   # wrapper minimal exécuté via SSH
.env.production.example           # débloque test_deploy_artifacts.py
docs/
  CICD_RUNBOOK.md                 # nouveau, pour compléter deploy/README.md
```

### K.2 Fichiers modifiés (Sb_16)

- `deploy/README.md` — section « CI/CD pipeline » pointant vers le runbook.
- `deploy/CHECKLISTS.md` — ajouter la checklist « avant d'activer le workflow deploy ».

### K.3 `scripts/deploy_from_github_actions.sh` — contenu attendu

Petit wrapper (~30 lignes) qui :

```bash
#!/usr/bin/env bash
set -euo pipefail

SHA="${1:-}"
if [[ -z "$SHA" ]]; then
  echo "FATAL: SHA required as first argument" >&2
  exit 2
fi

APP_DIR="/srv/workout"
APP_USER="workout"

cd "$APP_DIR"
echo "[deploy] fetching origin…"
sudo -u "$APP_USER" git fetch --prune origin

echo "[deploy] checking out $SHA…"
sudo -u "$APP_USER" git reset --hard "$SHA"

echo "[deploy] running deploy_prod.sh…"
sudo -u "$APP_USER" bash "$APP_DIR/scripts/deploy_prod.sh"

echo "[deploy] OK — $SHA is live"
```

Seule nouveauté par rapport à `deploy_prod.sh` : le `git fetch + reset --hard <SHA>` explicite **avant** le script maître, pour garantir que la prod est sur le SHA exact testé par CI.

### K.4 `.env.production.example` — contenu attendu

Template sans secrets réels. Exemple :

```
APP_ENV=production
APP_SECRET_KEY=<generate-via-python-secrets>
APP_BASE_URL=https://spignos.example.com
APP_HOST=127.0.0.1
APP_PORT=8000
DATABASE_URL=sqlite:////srv/workout/var/workout.db
BACKUP_DIR=/srv/workout/var/backups
BACKUP_RETENTION_DAYS=30
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM=
SMTP_USE_TLS=true
```

Commit sans les vraies valeurs. Le vrai `.env` reste sur le VPS, jamais commité.

### K.5 Protections branche `main` (GH UI, pas dans le repo)

- Require pull request review avant merge (recommandé, pas obligatoire V1 mono-dev).
- Require status checks → `CI` doit être vert.
- Require branches up to date.
- Include administrators.
- Prevent force pushes.

À activer lors du Sb_16 build, documenté dans `CICD_RUNBOOK.md`.

## L. Plan de build suivant

Voir §O.

## M. Risques

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|-----------|
| Clé SSH fuitée | Faible | **Critique** | Clé scopée au user `deploy`, sudoers restreints, rotation possible par régénération + remplacement du secret |
| Deploy en pleine séance utilisateur | Moyenne | Moyen | Opérer en début de journée ou sur fenêtre connue. Accepter l'interruption courte (restart uvicorn ~2s). V2 : deploy blue/green si volume le justifie |
| Migration cassée découverte en smoke | Faible | Élevé | Backup pré-deploy obligatoire, rollback SHA + `restore_latest_backup.py` |
| GitHub Actions down | Rare | Faible | Fallback possible : SSH manuel + `deploy_from_github_actions.sh` **directement sur VPS** — le wrapper reste exécutable manuellement |
| Secret `DEPLOY_SSH_KNOWN_HOSTS` devenu obsolète (IP changée OVH) | Moyen (après redémarrage VPS) | Moyen | Regénérer via `ssh-keyscan` + mise à jour du secret. Documenté |
| Tag `deploy/prod/*` qui pollue `git tag` | Faible | Faible | Accepté — 1 tag/deploy lisible. Cleanup possible via `git tag -d` si nécessaire |
| Concurrency bug (deux run deploy superposés) | Rare | Élevé | `concurrency: cancel-in-progress: false` — ils se mettent en file |
| Deploy force malgré CI rouge | Faible | Élevé | Protection branche main + required CI status checks |
| Utilisateur `deploy` compromis localement | Très faible | Critique | Sudoers strict : ne peut que lancer le script de deploy, pas shell libre |
| Alembic drift non détecté en CI car `.env` dev | Faible | Moyen | `check_alembic_drift.py` utilise une DB SQLite temporaire, indépendant du `.env` |

## N. Acceptance criteria Sx_16

| Critère | Statut |
|---------|--------|
| Contexte deploy actuel audité (§B) | ✓ |
| Limites mode manuel listées (§C) | ✓ |
| Architecture 2 workflows + 1 environment documentée (§D) | ✓ |
| Modèle SSH + SHA justifié contre 3 alternatives (§D.3) | ✓ |
| Workflow CI et deploy avec structure YAML (§F) | ✓ |
| Secrets, environment et permissions cartographiés (§G) | ✓ |
| Déroulé exact d'un deploy (chemin nominal + 2 chemins d'échec) (§H) | ✓ |
| Rollback + failure handling (§I) | ✓ |
| Garde-fous sécurité tabulés (§J) | ✓ |
| Structure de fichiers cible (§K) | ✓ |
| Risques listés (§M) | ✓ |
| Build Sb_16 chiffré et scopé (§O) | ✓ |
| Zéro Docker/K8s imposé, priorité simplicité / fiabilité / traçabilité | ✓ |

## O. Recommandation explicite du sprint build suivant

### Sb_16 — Prod CI/CD Pipeline build

**Scope strict (≤ 6 h) :**

1. **Créer `.env.production.example`** au root — débloque `test_deploy_artifacts.py`. 10 min.
2. **Créer `scripts/deploy_from_github_actions.sh`** — wrapper minimal §K.3. 20 min.
3. **Créer `.github/workflows/ci.yml`** — structure §F.1. 30 min.
4. **Créer `.github/workflows/deploy-production.yml`** — structure §F.2. 45 min.
5. **Créer `docs/CICD_RUNBOOK.md`** — procédure d'activation côté VPS (création user `deploy`, sudoers, secrets) et côté GitHub (environment, secrets, protection branche). 30 min.
6. **Vérification locale** :
   - `pytest` inclut désormais `test_deploy_artifacts.py` → full suite doit rester verte.
   - Sprint report Sb_16 compose un dry-run mental du workflow.
7. **Activation VPS + GitHub** (étape opérateur manuelle, documentée dans le runbook) :
   - Créer user `deploy` sur VPS + authorized_keys.
   - Installer sudoers `/etc/sudoers.d/spignos-deploy`.
   - Générer `DEPLOY_SSH_KEY` + `DEPLOY_SSH_KNOWN_HOSTS`.
   - Créer l'environment `production` dans GH UI avec required reviewer.
   - Configurer les secrets dans cet environment.
   - Activer les protections de branche main.
8. **Test en conditions réelles** : déclencher un premier `workflow_dispatch` sur un SHA de `main` identique à celui déjà en prod → pas de diff fonctionnel, valide le plumbing.
9. **Sprint report** `docs/SPRINT_Sb_16_prod_cicd_pipeline_BUILD_REPORT.md`. 30 min.

**Hors scope Sb_16 :**

- Pas de Docker / registry / image build.
- Pas de staging VPS.
- Pas de rollback automatique (trigger manuel uniquement — volontaire, protection).
- Pas de pipeline pour nginx conf (changement rare, manuel).
- Pas de monitoring/alerting externe (Sentry, Grafana) — séparé.
- Pas d'automatisation des backups offsite (déjà géré localement, extension plus tard).
- Pas de `push: main → deploy` automatique — V1.1 si confiance acquise après 2 mois.

**Critères d'acceptation Sb_16 :**

1. `ci.yml` passe sur une PR test sans toucher à la prod.
2. `.env.production.example` présent, `test_deploy_artifacts.py` vert en CI et localement.
3. `deploy-production.yml` exécute un deploy réel réussi en conditions contrôlées (même SHA que prod actuelle).
4. Tag `deploy/prod/<date>-<sha7>` visible dans le repo.
5. Full suite verte avec `test_deploy_artifacts.py` inclus (attendu ~ 696 → 710+).
6. `CICD_RUNBOOK.md` complet, pas-à-pas, testé par l'opérateur.
7. Workflow `deploy-production.yml` exige 1 reviewer avant d'exécuter.
8. Rollback testé une fois : re-déclencher `workflow_dispatch` sur un SHA plus ancien, vérifier que le VPS revient à cet état.

**Effort estimé Sb_16 :** 4–6 h (+ ~30 min d'activation VPS par l'opérateur).

---

## Annexe — Terminologie stricte

| Terme | Sens |
|-------|------|
| **CI** | Workflow `.github/workflows/ci.yml` — tests + QA, pas de deploy |
| **Deploy workflow** | `.github/workflows/deploy-production.yml` — SSH + exécution sur VPS |
| **Environment** | GitHub Environment `production`, porte les secrets scopés + le reviewer |
| **Wrapper** | `scripts/deploy_from_github_actions.sh`, petit script sur le VPS qui enchaîne `git fetch` + `deploy_prod.sh` |
| **SHA exact** | Le commit identifiant précisément la version déployée, tracé par un tag `deploy/prod/*` |
| **Smoke** | `scripts/smoke_deploy.sh` — vérifications post-deploy |
| **Concurrency group** | Mécanisme GitHub Actions qui sérialise les runs partageant la même étiquette |
| **Rollback SHA** | Redeploy d'un SHA plus ancien via le même workflow, avec `workflow_dispatch` |
