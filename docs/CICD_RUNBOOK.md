# SPIGNOS CI/CD Runbook

**Version :** v1 — 2026-04-21 — Sb_16
**Cycle couvert :** CI (`.github/workflows/ci.yml`) + déploiement production (`.github/workflows/deploy-production.yml`)
**Complément de :** [deploy/README.md](../deploy/README.md), [deploy/CHECKLISTS.md](../deploy/CHECKLISTS.md)

Ce runbook décrit les opérations **à faire une fois** pour activer la pipeline, puis les opérations courantes (deploy, rollback, troubleshooting). Il est volontairement linéaire — à suivre pas à pas.

---

## 1. Architecture rappelée en une page

```
┌─────────────────────────┐       ┌──────────────────────────┐
│  Dev IDE / GitHub web   │──PR──▶│  .github/workflows/      │
│                         │       │    ci.yml  (pytest + QA) │
└─────────────────────────┘       └──────────────────────────┘
                                              │ merge main
                                              ▼
                                   ┌──────────────────────────┐
                                   │  workflow_dispatch       │
                                   │  (reviewer required)     │
                                   └──────────────┬───────────┘
                                                  ▼
                                   ┌──────────────────────────┐
                                   │  deploy-production.yml   │
                                   │  SSH → VPS OVH           │
                                   └──────────────┬───────────┘
                                                  ▼
                            ┌───────────────────────────────────────┐
                            │  VPS /srv/workout                     │
                            │  sudo deploy_from_github_actions.sh   │
                            │    → git fetch + reset --hard <SHA>   │
                            │    → deploy_prod.sh (existant)        │
                            │      → backup SQLite                  │
                            │      → pip install                    │
                            │      → alembic upgrade head           │
                            │      → seed idempotent                │
                            │      → systemctl restart workout      │
                            │      → /healthz, /healthz/strict OK   │
                            │    → smoke_deploy.sh                  │
                            └───────────────────────────────────────┘
                                                  │ success
                                                  ▼
                                   git tag deploy/prod/<date>-<sha7>
```

Deux principes :
1. **Le SHA en prod = le SHA testé par CI.** Garanti par `git reset --hard <SHA>` avec le full SHA résolu côté Actions.
2. **Aucun deploy sans pas conscient humain.** L'environment `production` exige une approbation manuelle.

---

## 2. Activation initiale — côté VPS

À effectuer **une fois**, par l'opérateur, depuis un shell root (ou via `sudo`) sur le VPS OVH.

### 2.1 Créer le user `deploy` dédié

```bash
sudo adduser --system --group --shell /bin/bash --home /home/deploy deploy
sudo install -d -m 700 -o deploy -g deploy /home/deploy/.ssh
```

### 2.2 Générer une clé SSH dédiée (depuis la machine opérateur locale)

```bash
# Sur la machine opérateur (pas sur le VPS)
ssh-keygen -t ed25519 -C "github-actions-deploy-spignos" \
  -f ~/.ssh/spignos_deploy_ed25519 -N ""
```

Deux fichiers produits :
- `spignos_deploy_ed25519` — clé privée, à mettre dans le secret GitHub `DEPLOY_SSH_KEY`.
- `spignos_deploy_ed25519.pub` — clé publique, à copier sur le VPS.

### 2.3 Autoriser la clé publique côté VPS

```bash
# Sur le VPS, en root :
sudo -u deploy tee /home/deploy/.ssh/authorized_keys <<'EOF'
<coller ici le contenu de spignos_deploy_ed25519.pub>
EOF
sudo chmod 600 /home/deploy/.ssh/authorized_keys
sudo chown deploy:deploy /home/deploy/.ssh/authorized_keys
```

**Option durcissement** (recommandée) : préfixer la ligne par une contrainte de commande ou de source :

```
from="140.82.112.0/20,143.55.64.0/20" ssh-ed25519 AAAA... github-actions-deploy-spignos
```

(Les plages IP de GitHub Actions bougent — consulter <https://api.github.com/meta> pour la liste à jour. Durcir est bonus, pas strictement nécessaire.)

### 2.4 Installer le sudoers restreint

Le contenu exact dépend du couple `(APP_DIR, APP_USER)` de ton install. Voir §2.4.1 ci-dessous pour les valeurs non-défaut.

**Install par défaut (user système `workout`, repo `/srv/workout`) :**

```bash
# Sur le VPS, en root :
sudo tee /etc/sudoers.d/spignos-deploy <<'EOF'
# Allow the github-actions deploy user to run ONLY the deploy wrapper
# as root, and smoke_deploy.sh as the `workout` user. Nothing else.
deploy ALL=(root)    NOPASSWD: /srv/workout/scripts/deploy_from_github_actions.sh
deploy ALL=(workout) NOPASSWD: /bin/bash /srv/workout/scripts/smoke_deploy.sh
EOF
sudo chmod 440 /etc/sudoers.d/spignos-deploy
sudo visudo -c -f /etc/sudoers.d/spignos-deploy   # vérifie la syntaxe
```

Effet : `deploy` ne peut **que** lancer ces deux scripts. Pas de shell root, pas de modification arbitraire du système.

### 2.4.1 Layout non-défaut — `APP_DIR` / `APP_USER`

Si ton install SPIGNOS n'utilise pas le chemin `/srv/workout` ni le user `workout` (par exemple une install historique sous `/opt/workout-session-tracking` avec `ubuntu` comme user de service), deux ajustements :

1. **Sudoers** avec les vrais chemins et user cible :

   ```bash
   # Exemple : APP_DIR=/opt/workout-session-tracking, APP_USER=ubuntu
   sudo tee /etc/sudoers.d/spignos-deploy <<'EOF'
   deploy ALL=(root)   NOPASSWD: /opt/workout-session-tracking/scripts/deploy_from_github_actions.sh
   deploy ALL=(ubuntu) NOPASSWD: /bin/bash /opt/workout-session-tracking/scripts/smoke_deploy.sh
   EOF
   sudo chmod 440 /etc/sudoers.d/spignos-deploy
   sudo visudo -c -f /etc/sudoers.d/spignos-deploy
   ```

2. **Wrapper `deploy_from_github_actions.sh`** reconnaît les env vars `APP_DIR` et `APP_USER` depuis Sb_16.1. Les valeurs par défaut hardcodées au début du fichier sont `/opt/workout-session-tracking` et `ubuntu` — cohérentes avec l'install historique du projet. Si ton layout est encore autre chose, édite les 2 lignes en tête du script ou passe les vars via sudoers (non recommandé, plus opaque).

`deploy_prod.sh` consomme aussi `APP_DIR` et `APP_USER` depuis Sb_16.1 via ses variables d'env. Le wrapper les propage avec `sudo --preserve-env=APP_DIR,APP_USER`.

### 2.5 Vérifier que `/srv/workout/scripts/deploy_from_github_actions.sh` est exécutable

```bash
ls -la /srv/workout/scripts/deploy_from_github_actions.sh
# attendu : -rwxr-xr-x ... workout workout ... deploy_from_github_actions.sh
```

Si le script n'est pas encore présent (le VPS n'a pas encore tiré le commit Sb_16), faire un `git pull` manuel une dernière fois :

```bash
sudo -u workout bash -c 'cd /srv/workout && git pull && chmod +x scripts/deploy_from_github_actions.sh'
```

### 2.6 Capturer la fingerprint du VPS

Depuis la machine opérateur :

```bash
ssh-keyscan -t ed25519,rsa,ecdsa <VPS_HOST>
```

Copier la sortie complète, elle devient la valeur du secret `DEPLOY_SSH_KNOWN_HOSTS`.

### 2.7 Test SSH end-to-end depuis la machine opérateur

```bash
ssh -i ~/.ssh/spignos_deploy_ed25519 deploy@<VPS_HOST> \
    "sudo /srv/workout/scripts/deploy_from_github_actions.sh --help" 2>&1 | head -5
```

Attendu : le script doit exit 2 avec `FATAL: SHA required as first argument` (pas de SHA fourni). Ça prouve que :
- le SSH passe,
- le sudoers accepte,
- le script est exécutable.

---

## 3. Activation initiale — côté GitHub

### 3.1 Créer l'environment `production`

1. GitHub → Settings → Environments → **New environment**.
2. Nom : `production`.
3. **Required reviewers** : cocher, ajouter soi-même (ou l'ops).
4. **Deployment branches** : « Selected branches » → `main`.
5. Wait timer : 0 min V1 (peut être relevé à 5 min plus tard pour forcer un pas de réflexion).
6. Sauvegarder.

### 3.2 Ajouter les 4 secrets dans l'environment `production`

Toujours dans `Settings → Environments → production → Environment secrets → Add secret` :

| Secret | Contenu |
|--------|---------|
| `DEPLOY_SSH_HOST` | Hostname ou IP du VPS OVH (ex. `vps-xxxx.ovh.net`). |
| `DEPLOY_SSH_USER` | `deploy` |
| `DEPLOY_SSH_KEY` | Contenu complet de `spignos_deploy_ed25519` (clé privée, lignes `-----BEGIN OPENSSH PRIVATE KEY-----` jusqu'à `-----END OPENSSH PRIVATE KEY-----`). |
| `DEPLOY_SSH_KNOWN_HOSTS` | Sortie complète de `ssh-keyscan` (§2.6). |

### 3.3 Protéger la branche `main`

`Settings → Branches → Branch protection rules → Add rule` :

- Branch name pattern : `main`.
- ✅ Require a pull request before merging (cocher si travail en PR).
- ✅ Require status checks to pass before merging → sélectionner `CI / pytest + QA scripts`.
- ✅ Require branches to be up to date before merging.
- ✅ Include administrators.
- ✅ Restrict who can push to matching branches (soi-même).
- ❌ Allow force pushes (désactivé).
- ❌ Allow deletions (désactivé).

### 3.4 SonarCloud — secret + Quality Gate (Sb_20.4)

**Pré-requis :** projet déjà créé côté SonarCloud (`https://sonarcloud.io/organizations/mfe-dss/`).

1. **Générer un token SonarCloud**
   - SonarCloud → avatar → *My Account* → *Security* → *Generate Tokens*.
   - Type : `User Token`. Nom : `github-actions-spignos`. Expiration : 1 an.
   - Copier le token (visible une seule fois).

2. **Stocker le token dans GitHub**
   - Repo GitHub → *Settings* → *Secrets and variables* → *Actions* → *New repository secret*.
   - Nom : `SONAR_TOKEN`. Valeur : le token de l'étape 1.
   - **Pas** dans l'environment `production` — le scan tourne sur PR/push avant tout déploiement.

3. **Activer l'analyse automatique côté SonarCloud**
   - SonarCloud → projet → *Administration* → *Analysis Method* → désactiver *Automatic Analysis*.
   - Choisir *CI-based analysis* (le scan vient de notre `ci.yml`).
   - Sans ça, SonarCloud refusera le scan GitHub Actions avec l'erreur `automatic analysis enabled`.

4. **Quality Gate (V1 advisory)**
   - SonarCloud → *Quality Gates* → cloner *Sonar way* en `Spignos Way`.
   - Conditions sur **New Code** uniquement (V1) :
     - Coverage on New Code ≥ 70 %
     - Maintainability Rating on New Code = A
     - Reliability Rating on New Code = A
     - Security Rating on New Code = A
     - Security Hotspots Reviewed = 100 %
   - Pas de seuil sur le code existant V1 — Sb_20.4 triage les 296 issues legacy avant de durcir.

5. **Vérification**
   - Pousser un commit, ouvrir l'onglet *Actions* → job `SonarCloud` doit être vert (advisory).
   - Lien direct : `https://sonarcloud.io/project/overview?id=workout-session-tracking`.

6. **Bascule en required (Sb_20.5)**
   - Une fois le triage Sb_20.4 fini, retirer `continue-on-error: true` du step *SonarCloud scan* dans `ci.yml`.
   - Branch protection `main` → *Require status checks* → ajouter `CI / SonarCloud`.

---

## 4. Premier déploiement — dry-run sûr

**Objectif :** valider tout le plumbing sans changer l'état de la prod.

1. Identifier le SHA actuellement en prod :
   ```bash
   ssh deploy@<VPS_HOST> "cd /srv/workout && git rev-parse HEAD"
   ```
2. GitHub → Actions → **Deploy production** → **Run workflow**.
3. Input `ref` : coller le SHA récupéré à l'étape 1 (ou le nom de la branche `main` si elle pointe déjà dessus).
4. Input `skip_smoke` : décoché (false).
5. Click **Run workflow**.
6. Une notification d'approbation apparaît dans l'environment `production`. Cliquer **Review deployments** → cocher `production` → **Approve and deploy**.
7. Observer les logs :
   - Checkout OK.
   - SHA résolu.
   - SSH configuré.
   - `deploy_from_github_actions.sh` log `step 1/3`, `step 2/3`, `step 3/3` puis `OK — $SHA is live`.
   - `smoke_deploy.sh` log toutes les routes OK.
   - Tag poussé : `deploy/prod/<date>-<sha7>`.
8. Vérifier le tag : GitHub → Code → **tags** → le tag doit apparaître et pointer sur le bon SHA.
9. Vérifier visuellement que `/` en prod répond toujours.

Si tout passe → la pipeline est **active**.

---

## 5. Déploiement d'une nouvelle version (flux nominal)

1. Ouvrir une PR sur le code → `ci.yml` tourne automatiquement.
2. Merger la PR sur `main` → `ci.yml` tourne une seconde fois sur le merge commit.
3. GitHub → Actions → **Deploy production** → **Run workflow** → `ref: main` → **Run**.
4. Approuver le deployment dans l'environment `production`.
5. Attendre la fin (≈ 2 à 4 min).
6. Le tag `deploy/prod/<date>-<sha7>` trace ce deploy.

Durée attendue : ≈ 1 min de préparation côté GitHub + ≈ 2 min de déploiement effectif + smoke.

---

## 6. Rollback — ramener la prod à un SHA précédent

1. Trouver le SHA précédent :
   - `git log origin/main --oneline`
   - ou `git tag -l 'deploy/prod/*' --sort=-creatordate | head -5` (le tag juste avant le courant).
2. GitHub → Actions → **Deploy production** → **Run workflow** → `ref: <previous-sha>` → **Run**.
3. Approuver.
4. Le workflow fait exactement le même boulot en checkoutant le SHA ancien. Un nouveau tag `deploy/prod/<date>-<sha7>` est poussé.

**Limites connues :**
- Les migrations Alembic déjà appliquées **ne sont pas annulées** automatiquement. Le vieux code ignore les nouvelles colonnes nullable → comportement normal pour une migration additive.
- Si le problème vient d'une **migration destructive** (très rare, jamais dans le catalogue SPIGNOS à ce jour), il faut aussi :
  1. `ssh workout@<VPS>` pour ouvrir un shell applicatif.
  2. `cd /srv/workout && source .venv/bin/activate`.
  3. `alembic downgrade -1` si pertinent.
  4. Éventuellement restaurer la DB : `python scripts/restore_latest_backup.py`.
  5. Redémarrer le service : `sudo systemctl restart workout`.

---

## 7. Troubleshooting

### 7.1 « Permission denied (publickey) » au step SSH

- Vérifier que `DEPLOY_SSH_KEY` dans GH est bien la **clé privée entière**, y compris les lignes `BEGIN/END`, avec newlines LF.
- Vérifier côté VPS : `sudo -u deploy cat ~/.ssh/authorized_keys` doit contenir la pubkey correspondante.
- Vérifier les permissions : `~/.ssh` en 700, `authorized_keys` en 600.

### 7.2 « Host key verification failed »

- `DEPLOY_SSH_KNOWN_HOSTS` obsolète (typique après un reboot majeur du VPS qui a régénéré ses hostkeys). Re-exécuter `ssh-keyscan` (§2.6) et mettre à jour le secret.

### 7.3 Script exit 2 « does not look like a git SHA »

- Le workflow n'a pas réussi à résoudre le `ref` en un SHA. Vérifier que le ref existe sur `origin/main` et qu'on n'essaie pas de déployer une branche locale.

### 7.4 `deploy_prod.sh` échoue sur alembic drift

- Un dev a oublié de générer la migration pour un changement de modèle. Soit corriger, soit downgrade le ref.
- Le script abort **avant** toute modification — la prod reste sur l'ancien code.

### 7.5 `smoke_deploy.sh` échoue sur une route privée

- Probablement un cookie de session expiré dans le contexte non-auth du test. Lire les logs, vérifier que c'est bien un faux positif avant de rollback.

### 7.6 Deux déploiements tentés en même temps

- `concurrency: group: production-deploy, cancel-in-progress: false` → ils se mettent en file, le second attend. Comportement normal.

---

## 8. Checklist d'activation (à cocher une fois tout fait)

### Côté VPS
- [ ] User `deploy` créé (§2.1)
- [ ] Pubkey installée dans `~deploy/.ssh/authorized_keys` (§2.3)
- [ ] Sudoers `/etc/sudoers.d/spignos-deploy` installé + `visudo -c` OK (§2.4)
- [ ] `scripts/deploy_from_github_actions.sh` exécutable sur le VPS (§2.5)
- [ ] Test SSH end-to-end → exit 2 attendu (§2.7)

### Côté GitHub
- [ ] Environment `production` créé (§3.1)
- [ ] Required reviewer configuré
- [ ] 4 secrets ajoutés dans l'environment (§3.2)
- [ ] Protection de branche `main` activée (§3.3)

### Validation
- [ ] CI passe sur une PR test
- [ ] Premier déploiement dry-run OK (§4)
- [ ] Tag `deploy/prod/*` visible dans le repo
- [ ] Smoke vert

### Post-activation
- [ ] Runbook relu et marqué comme en vigueur
- [ ] Documenter la date de la première activation réussie ici : **__/__/__**
