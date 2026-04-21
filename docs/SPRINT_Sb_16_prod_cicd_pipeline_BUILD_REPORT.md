# Sprint Sb_16 Build Report — Prod CI/CD Pipeline

**Date :** 2026-04-21
**Type :** Build infrastructure — implémente §O de `SPIGNOS_PROD_CICD_PIPELINE_SPEC_v1.md`
**Prérequis :** Sx_16 spec figée (commit `03b20f1`), moteur produit stable (Sb_13 commit `77fc78e`)
**Successeur :** activation opérateur (§8) puis premier deploy dry-run (§10)

---

## 1. Objectif

Poser une pipeline CI/CD production **proportionnée à SPIGNOS** :
- `ci.yml` qui lance pytest + QA + drift sur chaque PR et chaque push main.
- `deploy-production.yml` manuel (`workflow_dispatch`) qui SSH sur le VPS, checkout un SHA exact, chaîne sur `deploy_prod.sh` existant puis `smoke_deploy.sh`, pousse un tag `deploy/prod/<date>-<sha7>` à la réussite.
- Zéro Docker, zéro Kubernetes, zéro staging VPS, zéro auto-deploy sur push main.
- Effet de bord bienvenu : débloquer `tests/test_deploy_artifacts.py` en créant le `.env.production.example` manquant.

---

## 2. Fichiers modifiés

| Fichier | Type | Nature |
|---------|------|--------|
| `.env.production.example` | **New** | Template sans secrets, 7 clés minimum attendues par les tests, wording qui oriente vers `docs/CICD_RUNBOOK.md` |
| `scripts/deploy_from_github_actions.sh` | **New** | Wrapper VPS ~55 lignes bash pur, exécutable via sudo par le user `deploy` |
| `.github/workflows/ci.yml` | **New** | Workflow CI read-only, Python 3.11, pytest + catalog_qa + machine_atlas_qa + alembic drift |
| `.github/workflows/deploy-production.yml` | **New** | Workflow deploy `workflow_dispatch`, environment `production`, concurrency sérialisé, tag sur succès |
| `docs/CICD_RUNBOOK.md` | **New** | Runbook opérateur en 8 sections : architecture, activation VPS, activation GitHub, dry-run, flux nominal, rollback, troubleshooting, checklist |
| `docs/SPRINT_Sb_16_prod_cicd_pipeline_BUILD_REPORT.md` | **New** | Ce rapport |

**Aucun fichier existant modifié.** Le build est strictement additif :
- `scripts/deploy_prod.sh` inchangé.
- `scripts/smoke_deploy.sh` inchangé.
- Aucune migration alembic.
- Aucun service / route / modèle touchés.

---

## 3. Décisions d'implémentation

### D1 — Wrapper VPS indépendant, script maître intact

`scripts/deploy_from_github_actions.sh` est un nouveau point d'entrée. Il **n'appelle pas** `deploy_prod.sh` en tant que sous-routine Python/FastAPI — il l'appelle en bash via `sudo -u workout bash`. Résultat : le script maître garde son contrat actuel (peut être exécuté manuellement depuis un SSH opérateur), la pipeline CI/CD devient juste un second appelant.

### D2 — Validation format SHA

Le wrapper refuse un argument qui ne ressemble pas à un SHA hexadécimal (7–40 chars). Garde-fou contre une erreur d'interpolation côté workflow qui aurait pu injecter une chaîne arbitraire via le `ref`.

### D3 — `git reset --hard <SHA>` plutôt que `git checkout <SHA>`

Avec `reset --hard`, aucun fichier en working dir ne peut survivre (par accident ou par malveillance). Le VPS est forcé dans l'état exact du SHA, pas un mix étrange. Le trade-off : si quelqu'un avait édité manuellement un fichier sur le VPS, il serait perdu. **Comportement voulu** — les modifications en prod doivent être commitées, pas éditées en live.

### D4 — Deux jobs SSH séparés (deploy + smoke)

Plutôt qu'un seul job monoblock, le workflow fait deux appels SSH distincts : un pour `deploy_from_github_actions.sh`, un pour `smoke_deploy.sh`. Pourquoi :
- Si le smoke échoue, le deploy a déjà été fait → on veut une étape nommée « smoke » qui apparaît clairement en erreur dans l'UI GitHub.
- `skip_smoke: true` (emergency) ne saute que le second appel, pas tout.
- Logs plus faciles à lire dans l'UI.

### D5 — Tag `deploy/prod/<date>-<sha7>`

Le tag carry un message `Deployed <full_sha> to production via Actions`. Le `short_sha` dans le nom permet de le scanner visuellement dans `git tag -l`. La date UTC dans le nom garantit l'ordre chronologique dans `--sort=-creatordate`.

### D6 — Permissions minimales par workflow

- `ci.yml` → `contents: read` seul. Pas besoin de push quoi que ce soit.
- `deploy-production.yml` → `contents: write` (uniquement pour pousser le tag). Rien sur `issues`, `pull-requests`, `packages`, `actions`.

### D7 — `BatchMode=yes` sur SSH

Pas de prompt interactif possible. Si une clé n'est pas dispo ou si l'host-key diverge, le SSH échoue immédiatement au lieu d'attendre un input qui n'arrivera jamais.

### D8 — Concurrency `cancel-in-progress: false` pour deploy, `true` pour CI

- CI : une nouvelle run sur le même ref **annule** la précédente (économise des minutes).
- Deploy : une nouvelle run **se met en file** derrière la précédente (deux deploys ne se marchent jamais dessus).

### D9 — `timeout-minutes: 15` partout

Protection contre un job bloqué. Un deploy SSH normal prend 2–4 min, on laisse 15 pour couvrir un cas dégradé.

### D10 — `.env.production.example` plus riche que le strict minimum des tests

Les tests exigent 7 clés. Le fichier en livre 14 (SMTP, port, base URL, etc.) pour qu'un opérateur puisse l'utiliser directement comme base sur le VPS sans retourner chercher les clés ailleurs. Les valeurs sont des placeholders explicites (`REPLACE_ME_WITH_A_LONG_RANDOM_STRING`), pas des faux secrets.

### D11 — Runbook très verbeux, en français, avec checklist finale

Le runbook est la seule documentation autorisée pour passer d'un VPS vierge à une pipeline active. Chaque étape est copier-collable. La checklist §8 permet à l'opérateur de valider l'activation sans relire tout le runbook.

---

## 4. Structure exacte des workflows

### 4.1 `.github/workflows/ci.yml`

```
on: pull_request | push(main)
permissions: contents: read
concurrency: ci-${{ github.ref }}, cancel-in-progress: true
job test:
  steps:
    - checkout
    - setup-python 3.11 + pip cache
    - pip install -r requirements.txt + pytest httpx
    - pytest --ignore=tests/test_v1_acceptance.py -q
    - python scripts/catalog_qa.py
    - python scripts/machine_atlas_qa.py
    - python scripts/check_alembic_drift.py
```

Notes :
- `test_v1_acceptance.py` reste exclu (c'est un check VSCode local, inutile en CI).
- `test_deploy_artifacts.py` **tourne maintenant** grâce au `.env.production.example`.

### 4.2 `.github/workflows/deploy-production.yml`

```
on: workflow_dispatch
  inputs:
    ref         (default "main")
    skip_smoke  (default false)
permissions: contents: write
concurrency: production-deploy, cancel-in-progress: false
job deploy:
  environment: production
  steps:
    1. checkout ref with fetch-depth: 0
    2. resolve full SHA + short SHA → GITHUB_OUTPUT
    3. configure SSH (key + known_hosts from secrets)
    4. SSH: sudo /srv/workout/scripts/deploy_from_github_actions.sh <FULL_SHA>
    5. SSH (if !skip_smoke): sudo -u workout bash /srv/workout/scripts/smoke_deploy.sh
    6. on success: git tag deploy/prod/<date>-<short7> + git push origin <tag>
    7. on failure: ::error:: annotation + exit 1
```

---

## 5. Comportement du script VPS

`scripts/deploy_from_github_actions.sh` en 3 phases logiques :

### Phase 1 — Argument validation

```
- SHA required (exit 2 if missing)
- SHA must match ^[0-9a-f]{7,40}$ (exit 2 if not)
- /srv/workout/.git must exist (exit 1 if missing)
```

### Phase 2 — Checkout du SHA exact

```
sudo -u workout git fetch --prune --tags origin
sudo -u workout git reset --hard <SHA>
```

Résultat : le working tree du user `workout` est **exactement** dans l'état du SHA demandé.

### Phase 3 — Délégation à `deploy_prod.sh`

```
sudo -u workout bash /srv/workout/scripts/deploy_prod.sh
```

Le script maître enchaîne (inchangé depuis sa dernière version) :
1. Backup SQLite `sqlite3 .backup` atomique → `var/backups/workout_pre_deploy_<ts>.db`.
2. `pip install -r requirements.txt` dans le venv.
3. `python scripts/check_alembic_drift.py` — abort si drift.
4. `alembic upgrade head`.
5. `python -m scripts.seed_db` — seed idempotent.
6. `systemctl restart workout`.
7. `curl /healthz` + `/healthz/strict` → 200 attendu.

Le wrapper sort en 0 si et seulement si toutes les phases réussissent.

---

## 6. Secrets attendus

Configurés dans l'environment GitHub `production` (§3.2 du runbook) :

| Secret | Exemple |
|--------|---------|
| `DEPLOY_SSH_HOST` | `vps-xxxx.ovh.net` |
| `DEPLOY_SSH_USER` | `deploy` |
| `DEPLOY_SSH_KEY` | Contenu PEM complet de `spignos_deploy_ed25519` (lignes BEGIN/END incluses) |
| `DEPLOY_SSH_KNOWN_HOSTS` | Sortie complète de `ssh-keyscan -t ed25519,rsa,ecdsa <host>` |

**4 secrets, pas un de plus.** Path `/srv/workout` codé en dur dans le wrapper — pas un secret (public dans `deploy/README.md`).

---

## 7. Procédure opérateur résumée

Copier le runbook `docs/CICD_RUNBOOK.md` pour la version complète. Synthèse :

**Côté VPS (une fois, en root) :**
1. `adduser --system --group --shell /bin/bash deploy`.
2. Générer clé SSH locale dédiée (sur machine opérateur).
3. Installer la pubkey dans `~deploy/.ssh/authorized_keys`.
4. Installer `/etc/sudoers.d/spignos-deploy` restrictif.
5. Vérifier que `scripts/deploy_from_github_actions.sh` est exécutable.
6. `ssh-keyscan` pour capturer la fingerprint.

**Côté GitHub (une fois, UI web) :**
1. Créer environment `production` avec required reviewer.
2. Ajouter les 4 secrets dans l'environment.
3. Protéger la branche `main` (require CI green).

**Validation (une fois) :**
1. Premier `workflow_dispatch` avec `ref: <SHA actuellement en prod>` — dry-run safe.
2. Approuver, observer les logs, vérifier le tag.

**Deploys courants :**
- Merger sur `main` → CI tourne.
- `workflow_dispatch` → approuver → déploiement automatique.

**Rollback :**
- `workflow_dispatch` avec `ref: <SHA précédent>`.

---

## 8. État des tests

### 8.1 Tests réactivés par Sb_16

`tests/test_deploy_artifacts.py` — 16 tests qui étaient silenced parce que `.env.production.example` était manquant. Le fichier ajouté dans ce sprint débloque les assertions et les 16 tests passent sans autre modification.

### 8.2 Full suite

```
tests  : 712 passed in 3m46s
(vs 696 avant Sb_16, +16 réactivés)
```

Commande utilisée :
```bash
pytest --ignore=tests/test_v1_acceptance.py -q
```

`test_v1_acceptance.py` reste exclu — c'est un check VSCode local, pas CI.

### 8.3 Pas de nouveau test écrit

Sb_16 ne pose pas de nouveau test unitaire — les workflows YAML ne se testent pas en pytest, et les tests `test_deploy_artifacts.py` existants couvrent exactement les invariants pertinents (présence des fichiers, syntaxe des systemd units, cohérence du runbook).

Un test supplémentaire pourrait vérifier que `scripts/deploy_from_github_actions.sh` est **exécutable** dans le repo (bit `x`), mais c'est déjà validé par `test_smoke_deploy_script_exists_and_executable` pour le pattern voisin. Si utile, ajouter dans un micro-commit ultérieur.

### 8.4 QA scripts inchangés

- `catalog_qa.py` : PASS (16 templates, 98 exercises).
- `machine_atlas_qa.py` : PASS (8 familles, 29 machines).
- `check_alembic_drift.py` : PASS (head `c3d5f1e82a04`).

---

## 9. Limites assumées

1. **Aucun test du workflow GitHub Actions en local.** Possible via `act` mais pas intégré V1. Le workflow est suffisamment simple pour être validé par le premier run réel.
2. **Pas d'auto-deploy sur push main.** Décision consciente §F.2 de la spec. Si un jour on bascule, c'est un petit PR qui ajoute `push: branches: [main]` au trigger.
3. **Mono-reviewer = soi-même.** Le pas conscient est là, mais pas la vraie 4-eyes review. Acceptable mono-dev ; si équipe grandit, ajouter un 2ᵉ reviewer.
4. **Pas de rollback automatique si smoke fail.** Le workflow tag seulement à la réussite ; en cas d'échec, la prod reste sur le nouveau code. Décision produit : préférer laisser l'opérateur décider (re-deploy SHA précédent vs patch hotfix).
5. **Pas de notification externe (Slack, email).** GitHub Actions UI suffit en V1. Ajouter un webhook Slack est un petit ajout ultérieur si besoin.
6. **Path `/srv/workout` codé en dur** dans le wrapper. Si le VPS change de layout un jour, il faut éditer le script. Acceptable vu la stabilité du layout.
7. **Le runbook décrit l'activation mais ne la teste pas.** C'est l'opérateur qui active, pas la CI. Si l'opérateur oublie une étape, le premier deploy échouera — c'est le filet de sécurité attendu.
8. **Aucun monitoring post-deploy structuré** (latency p95, error rate). Juste smoke. Suffisant V1, à enrichir quand le volume le justifiera.
9. **Les GitHub Actions runners utilisent une IP variable** — le durcissement par `from="..."` dans `authorized_keys` est optionnel et tombe si les plages changent. Documenté comme bonus, pas comme garde-fou.
10. **Rotation de secrets non automatisée.** Si `DEPLOY_SSH_KEY` est compromise, l'opérateur doit regénérer à la main et mettre à jour le secret GH + authorized_keys. Documenté §7.1 du runbook.

---

## 10. Instructions du premier dry-run sûr

**Objectif :** valider que la pipeline fonctionne **sans changer ce qui tourne en prod**.

### Prérequis
- Runbook §2 (VPS) fait intégralement.
- Runbook §3 (GitHub) fait intégralement.
- Branche `main` à jour avec le commit Sb_16 mergé.

### Dry-run
1. Sur la machine opérateur :
   ```bash
   ssh deploy@<VPS> "cd /srv/workout && git rev-parse HEAD"
   ```
   Ça donne le SHA **actuellement en prod** — disons `abcdef1234567...`.

2. Sur GitHub web : `Actions` → `Deploy production` → `Run workflow`.

3. Inputs :
   - `ref` : coller `abcdef1234567...` (exactement le SHA déjà en prod).
   - `skip_smoke` : décocher (false).

4. `Run workflow`.

5. Approuver le deployment dans l'environment `production` (clic sur `Review deployments` → cocher → `Approve and deploy`).

6. Observer les logs des 7 steps. Comportement attendu :
   - **step 3/3** : `deploy_prod.sh` fait le backup, re-run pip (no-op si rien à installer), alembic upgrade (no-op car DB déjà à jour), seed idempotent, restart (downtime de ~2s), health check OK.
   - **smoke** : toutes routes OK.
   - **tag** : `deploy/prod/<YYYY-MM-DD-HHMM>-<sha7>` poussé vers origin.

7. Aller sur `Code → tags` : le nouveau tag doit apparaître.

8. Vérifier `/` en prod — le service est revenu up après le restart.

Résultat attendu : **aucun changement fonctionnel**, juste un restart de service court et un tag de plus dans le repo. Si tout passe, la pipeline est active.

### Si le dry-run échoue
- Lire les logs GitHub Actions.
- Relire le runbook §7 (troubleshooting).
- Les 90 % des échecs V1 viennent d'un secret mal copié (clé privée tronquée, known_hosts mal échappé).

### Après le dry-run réussi
- Faire un vrai deploy sur un petit PR (par exemple un ajout de commentaire docs) pour confirmer le flux merge → CI → deploy → smoke → tag en conditions réelles.

---

## 11. Recommandation de la suite

### 11.1 Séquence immédiate (court terme, quelques jours)

1. **Opérateur active** le runbook §2 et §3 sur VPS + GitHub. ~30 min.
2. **Premier dry-run** §10. ~10 min.
3. **Premier vrai deploy** sur un commit mineur. ~5 min.
4. Si les 3 étapes sont OK → la pipeline est **production-ready**.

### 11.2 Retours probables à observer

- Temps total de run (Actions + smoke) doit rester < 5 min — sinon investiguer.
- Le restart `systemctl restart workout` coupe l'accès ~2 s. Acceptable. Si dérange : bascule future vers blue/green avec deux services et nginx upstream switch.
- Si un smoke échoue régulièrement sur une route privée → faux positif du session cookie, ajuster dans `smoke_deploy.sh` plutôt que dans le workflow.

### 11.3 Prochains sprints candidats (aucun urgent)

- **V1.1 auto-deploy** : ajouter `push: branches: [main]` à `deploy-production.yml` après ~2 mois de confiance acquise. 15 min.
- **Notification Slack / email** : webhook ajouté en `on: workflow_run` si besoin de push notifications. ~30 min.
- **Staging VPS** : seulement si le produit passe en multi-utilisateur.
- **Docker** : seulement si architecture multi-services ou multi-environnements émerge.
- **Retour sur le rail produit** : passe dogfooding Sb_13 (la reco telemetry a besoin de vrai usage), puis arbitrage Sx_11b programme-builder / Sx_11c squad v2 / Sx_13.1 calibration 2.

Ordre recommandé : finir l'activation Sb_16 opérateur → passer une semaine en dogfooding Sb_13 avec deploys via la nouvelle pipeline → ouvrir le prochain chantier produit.

---

## 12. Synthèse exécutive

- **6 nouveaux fichiers**, aucun fichier existant modifié. `deploy_prod.sh` et `smoke_deploy.sh` intacts.
- **Deux workflows GitHub Actions** : CI read-only sur PR/push, deploy manuel via `workflow_dispatch` avec environment `production` + reviewer + concurrency sérialisé.
- **Wrapper VPS ~55 lignes** qui valide le SHA, fait `git fetch → reset --hard`, appelle `deploy_prod.sh`.
- **Tag git permanent** sur chaque deploy réussi.
- **4 secrets scopés** à l'environment production.
- **Runbook `docs/CICD_RUNBOOK.md`** de 8 sections + checklist, entièrement copier-collable.
- **Full suite : 712 passed** (vs 696, +16 réactivés via `.env.production.example`).
- **Zéro Docker, zéro K8s, zéro staging, zéro auto-push-deploy.** V1 proportionnée.
- Prête à activation opérateur puis dry-run §10.
