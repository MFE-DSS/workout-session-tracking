# Security Baseline — Sb_26.4

**Audience :** contributeurs SPIGNOS + opérateur de garde.
**Créé :** 2026-06-14 (sprint Sb_26.4).
**Statut :** verrouille la baseline sécurité minimale avant tout cycle produit ou ouverture publique.

---

## 1. Architecture sécurité actuelle (résumé)

| Couche | Mécanisme | Verrouillé par |
|---|---|---|
| Authentification | session cookie signé (itsdangerous) + bcrypt | tests `test_auth.py` |
| Cookies | `Secure`, `HttpOnly`, `SameSite=lax` (cf. `app/services/auth.py`) | tests `test_security.py` |
| Headers | CSP, X-Frame-Options DENY, Referrer-Policy, Permissions-Policy | `SecurityHeadersMiddleware` |
| Rate limiting | in-process per-IP buckets sur `/login`, `/register`, `/forgot-password` | **Sb_26.4** (cf. §2) |
| Dependency audit | `pip-audit` required en CI | **Sb_26.4** (cf. §3) |
| Dependabot | PRs hebdo pip + actions, pas d'auto-merge | **Sb_26.4** (cf. §4) |
| Lockfile reproducible | `requirements-lock.txt` — **autoritaire** (CI + prod installent depuis lui) | **Sb_DEPENDENCY_LOCK_AUTHORITY_01** (cf. §5) |
| Secrets scan | `gitleaks` required sur PR / push | **Sb_26.4** (cf. §6) |
| Static analysis Python | bandit `-ll` required, ruff budget locked | Sb_26.1 |
| Workflow lint | actionlint required | Sb_26.1 |
| Shell lint | shellcheck `-S warning` required | Sb_26.1 |
| Migration safety | schema snapshot + pattern linter + roundtrip | Sb_26.2 |
| Observabilité | /healthz/strict, Sentry opt-in, Discord opt-in | Sb_26.3 |

## 2. Rate limiting auth (`/login`, `/register`, `/forgot-password`)

### 2.1 Implémentation

In-memory **sliding window per-IP**, single-process. V1 prod tourne sur un seul uvicorn derrière nginx — la granularité est correcte. Pas de Redis, pas de CAPTCHA, pas de 2FA.

Code : `app/main.py` (`RateLimitMiddleware`, `_rate_limit_check`).
Config : `app/config.py` (settings `RATE_LIMIT_*`).

### 2.2 Quotas par défaut

| Route | Max | Fenêtre | Justification |
|---|---|---|---|
| `POST /login` | 10 | 10 min | Login multi-device humain : suffisant. Brute-force : bloque ~6×/h |
| `POST /register` | 5 | 1 h | Création d'utilisateur n'est pas un usage récurrent |
| `POST /forgot-password` | 5 | 1 h | Évite spam de mail de reset |

Configurables via env :
* `RATE_LIMIT_LOGIN_MAX`, `RATE_LIMIT_LOGIN_WINDOW_SECONDS`
* `RATE_LIMIT_REGISTER_MAX`, `RATE_LIMIT_REGISTER_WINDOW_SECONDS`
* `RATE_LIMIT_FORGOT_MAX`, `RATE_LIMIT_FORGOT_WINDOW_SECONDS`
* `RATE_LIMIT_ENABLED=0` désactive entièrement (utile en debug, pas en prod)

### 2.3 Réponse 429

```json
{"detail": "Too many attempts. Please retry later."}
```

Header `Retry-After: <seconds>`.

**Sober message** : ne révèle ni l'existence d'un compte/email, ni l'utilisateur ciblé, ni l'IP. Test : `tests/test_rate_limiting.py::test_login_returns_429_after_max_attempts` (vérifie qu'aucun mot de la liste `["user", "exist", "registered", "account", "email"]` ne fuit dans la réponse 429).

### 2.4 Limites V1 (documentées)

| Limitation | Conséquence | Reporté à |
|---|---|---|
| Single-process : bucket réinitialisé sur restart | Restart fréquent ⇒ rate limit perd l'historique | acceptable V1 |
| Single-process : pas de partage entre workers | Si on passe à N workers uvicorn, quotas effectifs ×N | Sb_27+ (passer à Redis si besoin) |
| Pas de protection nginx en amont | nginx pourrait absorber le burst avant FastAPI | optionnel post-V1 |
| Pas de blacklist permanente IP | Une IP malveillante peut juste attendre la fenêtre | Sb_27+ si abus constatés |
| Bucket en RAM : pas de persistance audit | Logs nginx restent disponibles | acceptable V1 |

## 3. Dependency audit — pip-audit

### 3.1 État baseline (2026-06-14)

```bash
pip-audit -r requirements.txt --strict
# → No known vulnerabilities found
```

Cette baseline est **figée par la gate CI** : tout commit qui introduit une dep vulnérable casse la CI.

### 3.2 Procédure si pip-audit trouve une vuln

1. Identifier le package + CVE (sortie de pip-audit pointe vers le PyPA advisory)
2. Vérifier si une version corrige : `pip-audit -r requirements.txt --fix` (dry-run)
3. **Si oui** : update `requirements.txt`, régénère lockfile (`bash scripts/regen_lockfile.sh`), commit
4. **Si non** (pas encore de patch publié) :
   - Évaluer l'impact : la fonction vulnérable est-elle utilisée par SPIGNOS ?
   - Documenter dans `docs/SECURITY_BASELINE.md §9` (backlog)
   - Si exploitable et non patchable : envisager downgrade vers version pré-vuln ou retrait
   - Si non exploitable : créer une baseline temporaire dans `.pip-audit-baseline.json` (à introduire au moment où une exception sera nécessaire), justifier le commit

**Interdit** : `--ignore-vuln <GHSA-...>` silencieux sans entrée écrite dans ce doc.

### 3.3 Étendre l'audit

* `pip-audit` ne scanne pas les optional dev deps (pytest, ruff, etc.) par défaut. Ces deps ne tournent pas en prod — risque acceptable V1.
* `pip-audit --strict` scanne **`requirements-lock.txt`** — c'est le fichier réellement installé en CI comme en production.

## 4. Dependabot

### 4.1 Configuration

`.github/dependabot.yml` — PR hebdo lundi 06:00 Europe/Paris :
* écosystème `pip` (racine, `requirements.txt`) — patches groupés
* écosystème `github-actions` (racine, tous workflows)

Pas d'auto-merge. Tous les PRs Dependabot doivent passer :
* CI complète (tous jobs Sb_26.1 → 26.4)
* Review humaine du diff
* Vérification que pip-audit reste vert

### 4.2 Workflow recommandé

1. Lundi matin : ouvrir les PRs Dependabot par ordre de date d'ouverture
2. Pour chaque PR :
   * lire le changelog amont (lien dans le PR body)
   * lancer la CI
   * si CI verte ET pas de changement de comportement signalé → merge
   * sinon : commenter, attendre Sb_xx.x dédié si refactor nécessaire
3. Si patch sécu critique : merge dans la journée même si autres PRs en attente

### 4.3 Que NE PAS faire

* `auto-merge` Dependabot : non. Une review humaine reste obligatoire (V1).
* Ignorer 3+ PRs Dependabot accumulées : la dette se compose. Capper à 5 ouvertes simultanées (`open-pull-requests-limit: 5`).
* Bump majeur sans tester localement (FastAPI, SQLAlchemy, Pydantic en particulier).

## 5. Lockfile reproducible — `requirements-lock.txt`

### 5.1 Génération

```bash
bash scripts/regen_lockfile.sh
git add requirements-lock.txt
```

Résolu **pour Python 3.11**, la version de la CI, via `uv pip compile --python-version 3.11 --strip-extras`. Le fichier liste toutes les transitives avec versions exactes.

Le script **refuse** de régénérer avec `pip-compile` sous un interpréteur différent de la cible : `pip-compile` résout pour l'interpréteur courant, et le lock ne porte aucun marqueur d'environnement — il n'est donc valide que pour la version qui l'a produit.

### 5.2 Statut : AUTORITAIRE

Depuis `Sb_DEPENDENCY_LOCK_AUTHORITY_01`, le lockfile est **le fichier d'installation** :

* CI — `pip install -r requirements-lock.txt` (les deux jobs runtime)
* `scripts/deploy_prod.sh` — idem, avec échec explicite si le fichier est absent
* `pip-audit` scanne le lock, puisque c'est lui qui s'installe

`requirements.txt` reste la **spécification source** : plages ouvertes, éditée à la main. On ne modifie jamais le lock à la main.

**Pourquoi ce basculement.** Les plages ouvertes (`fastapi>=0.110`, `sqlalchemy>=2.0`…) faisaient résoudre les dernières versions compatibles **à chaque installation**. Mesuré le 2026-08-18 : **13 paquets sur 29** divergeaient entre le lock déclaré et un environnement installé ainsi. La pipeline épinglait le code à un SHA exact tout en laissant l'arbre de dépendances flotter — deux déploiements du même SHA pouvaient livrer des bibliothèques différentes.

### 5.3 Les pré-requis de bascule, et comment ils ont été tenus

Les trois conditions posées en `Sb_26.4` :

1. **Toutes les versions tiennent en Python 3.11** — vérifié : les 29 paquets se résolvent pour 3.11, et la CI réelle installe désormais le lock.
2. **Le lockfile est régénéré correctement** — `scripts/check_lock_drift.py` est **bloquant** en CI : toute dépendance ajoutée à `requirements.txt` sans régénération fait échouer le build.
3. **Plan de rollback** — `deploy_prod.sh` échoue explicitement si le lock est absent ou non installable, et le message indique la manœuvre : relancer le workflow de déploiement avec le SHA précédent.

### 5.4 Ce que la garde de dérive ne vérifie pas

Elle compare les épingles aux specs déclarées, **hors ligne**. Elle ne vérifie pas que le lock est la résolution la plus fraîche possible : qu'une version plus récente existe sur PyPI n'est pas une dérive, c'est du temps qui passe. Proposer ces montées est le travail de Dependabot.

## 6. Secrets scanning — gitleaks

### 6.1 Gate CI

`.github/workflows/ci.yml` job `lint` : `gitleaks/gitleaks-action@v2` required sur PR + push. Scan le diff + working tree.

### 6.2 Full-history scan one-shot

Au moins une fois par cycle de sécurité (et après tout secret rotation) :

```bash
# Local, sur la branche main à jour :
docker run --rm -v "$(pwd):/repo" zricethezav/gitleaks:latest \
    detect --source /repo --no-banner --redact

# OU sans docker (binary) :
gitleaks detect --source . --no-banner --redact
```

Si la sortie est non-vide :
1. Inspecter chaque finding — peut-il être un faux positif (un format qui ressemble à un secret mais ne l'est pas) ?
2. Si vrai secret :
   * **Rotater le secret immédiatement** côté provider (Sentry DSN, Discord webhook, GitHub token, etc.)
   * Purger l'historique avec `git filter-repo` (sprint dédié, pas en feature sprint)
   * Documenter dans §9 (incident log)

### 6.3 Allowlist

Si un faux positif persistent (clé publique de test, exemple .env.example), ajouter un `.gitleaksignore` ou un commentaire `gitleaks:allow` SUR LA LIGNE MÊME, avec justification dans le commit.

**Pas de fichier `.gitleaksignore` ouvert pour V1** — toute exception doit être proposée dans un PR + review humaine.

### 6.4 Procédure incident "secret leak" (critical)

| Étape | Action | Délai |
|---|---|---|
| T+0 | Identifier le secret (sortie gitleaks ou alerte GitHub) | immédiat |
| T+5min | Rotater le secret côté provider | < 15min |
| T+15min | Forcer reload des consommateurs (restart services, refresh `.env`) | < 30min |
| T+30min | Vérifier qu'aucun usage non-autorisé n'a eu lieu (logs provider) | < 1h |
| T+1h | Décision purge historique : `git filter-repo` ou laisser (dépend exposition + sensibilité) | < 24h |
| T+24h | Postmortem dans `docs/incidents/<date>_secret_leak.md` (à créer le jour J) | < 7 jours |

## 7. Procédure upgrade dépendance (manuelle)

```bash
# 1. Bump version dans requirements.txt
vim requirements.txt

# 2. Régénérer le lockfile
bash scripts/regen_lockfile.sh

# 3. Audit + tests locaux — sur le LOCK, qui est ce qui sera déployé.
#    Auditer requirements.txt auditerait des plages, pas des versions.
pip install -r requirements-lock.txt
pip-audit -r requirements-lock.txt --strict
PYTHONPATH=. pytest --ignore=tests/test_v1_acceptance.py -q

# 4. Si tests verts → commit + PR
git add requirements.txt requirements-lock.txt
git commit -m "chore(deps): bump <package> X → Y (CVE-... / security / minor)"
```

## 8. Limites assumées V1 (par contrat)

| Item | Pourquoi pas dans Sb_26.4 | Reporté à |
|---|---|---|
| 2FA / TOTP | Hors scope V1 (interdiction "pas de refonte auth") | Sb_27+ |
| CAPTCHA sur /login | Hors scope V1 (interdiction explicite user) | Sb_27+ |
| Rate limiting multi-process Redis-backed | Single-process suffit pour V1 | Sb_27+ |
| CSP report-uri / report-to | Non utile sans collecteur | Sb_27+ |
| HSTS preload | Doit être posé côté nginx, pas FastAPI | OPS hors scope |
| SBOM (Software Bill of Materials) | Hors scope V1 ; lockfile suffit pour traçabilité | Sb_27+ |
| Audit dev/test deps | Risque acceptable V1 (pas en prod) | Sb_27+ |
| Résolution la plus fraîche imposée en CI | Une version plus récente sur PyPI n'est pas une dérive ; c'est le rôle de Dependabot | — |
| Auto-bascule deploy sur lockfile-install | ✅ **fait** — `Sb_DEPENDENCY_LOCK_AUTHORITY_01` | livré 2026-08-18 |
| Cleanup ruff baseline 548 → < | Contrat sprint dédié | `Sb_26.next.ruff-cleanup-N` |

## 9. Backlog sécurité (incident log + TODOs)

| Date | Item | Statut |
|---|---|---|
| 2026-06-14 | Baseline Sb_26.4 établie | ✅ livrée |

(Ce tableau s'enrichira au fil des incidents et upgrades.)

## 10. FAQ

> Pourquoi pas Redis pour le rate limiter ?

V1 prod = 1 process uvicorn. La portée du bucket en RAM est correcte. Redis = stack à opérer, secret à gérer, latence réseau. Bénéfice nul tant qu'on est monolithe single-instance.

> Pourquoi le rate limiter ne bloque pas /reset/{token} ?

Le token de reset est déjà à usage unique côté DB. Le brute-force du token est computationnellement impraticable (32+ bytes signés). Le rate limit n'apporterait rien. /forgot-password en amont (qui génère le token) est rate-limité, donc le flow est protégé.

> Et si Dependabot ouvre 5 PRs simultanément ?

Cap volontaire (`open-pull-requests-limit: 5`). Au-delà, Dependabot attend qu'on en merge avant d'ouvrir de nouveaux. Force la discipline de revue.

> Pourquoi pip-audit en CI et pas en pre-commit ?

Pre-commit nécessite que chaque dev ait l'outil installé + la base CVE à jour. CI : 1 install, base toujours fresh, ratchet uniforme. Pre-commit en V2 si la friction CI gêne (peu probable, pip-audit est rapide).

> gitleaks va-t-il bloquer un PR avec un faux positif ?

Oui — c'est le principe. La gate est required. Procédure documentée §6.3 : allowlist par-ligne uniquement, jamais de fichier ouvert.
