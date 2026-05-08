# SPIGNOS Security Hardening & SonarQube Integration Spec v1

**Sprint ID :** Sx_20_security_hardening_and_sonar_integration_spec
**Date :** 2026-05-08
**Statut :** SPEC ONLY — aucun code engagé par ce document
**Origine :** retour SonarCloud côté GitHub (52 security / 97 reliability / 147 maintainability / 0 % coverage)
**Standards visés :** OWASP A1+A3 (2021), OWASP A1+A5 (2017), CWE-20, CWE-22, STIG V-222609
**Successeurs :** Sb_20.1 → Sb_20.5 (chaîne de sprints courts, voir §J)

---

## A. Statut

Spec d'intégration qualité/sécurité. Cadre les chantiers nécessaires pour passer le code SPIGNOS aux exigences SonarQube et formaliser une gate continue. Le but n'est pas de refondre le code (l'audit factuel §C montre qu'il est globalement sain), mais de :

1. **Mesurer** ce qui n'est pas mesuré (coverage, complexité cyclomatique).
2. **Formaliser** ce qui est implicite (validation d'inputs, scope d'accès) via des linters CI.
3. **Trier** les 296 issues SonarQube remontées (real / won't fix / false positive).
4. **Bloquer** les régressions futures via une gate CI.

## B. Contexte

### B.1 Rapport SonarCloud actuel

| Catégorie | Issues | Grade | Cible |
|-----------|--------|-------|-------|
| Security | 52 open | E | A |
| Reliability | 97 open | — | B+ |
| Maintainability | 147 open | D | B+ |
| Coverage | non configuré | — | ≥ 70 % |
| Duplications | 1.0 % sur 33k LoC | — | < 3 % |
| Security Hotspots | 13 | — | reviewed |

### B.2 Audit factuel du code (8 mai 2026)

Inspection ciblée des risques OWASP / CWE par grep + lecture de routers, services, templates. Résumé :

| Risque OWASP/CWE | Statut audit code | Évidence |
|------------------|-------------------|----------|
| **A1 Broken Access Control (OWASP 2021)** | ✅ aucun trou | Toutes les routes scopent `user_id` ; `_load_session` filtre `user_id == user.id` ; `/users/{username}` n'expose que les champs publics |
| **A3/A1 Injection (OWASP 2021/2017)** | ✅ aucun raw SQL | SQLAlchemy paramétré partout, `text("SELECT 1")` uniquement pour healthz |
| **XSS / Template injection** | ✅ Jinja autoescape on | `\|safe` réservé aux SVG serveur (`radar_svg`, `quality_svg`, `sparkline_svg`) — jamais sur free_note ou autre input user |
| **CWE-20 Improper Input Validation** | ⚠️ partiel | `form_parsing.to_float/to_int/enum_str` solides ; **gap** : `/users/{username}` path param sans regex de validation |
| **CWE-22 Path Traversal** | ✅ aucun | Aucun `open()` avec input utilisateur ; chemins tirés de constantes ou de `BACKUP_DIR` env |
| **STIG V-222609 Input Handling** | ⚠️ partiel | Validation présente sur la plupart des routes, mais pas systématiquement déclarée via Pydantic |
| **Secrets** | ✅ aucun | `pydantic-settings` avec `.env`, bcrypt, `itsdangerous` ; pas de credentials commités |

**Conclusion d'audit** : le code n'a **aucune faille critique exploitable**. Les 52 issues sécurité SonarQube sont presque certainement des **warnings de style** (mots-clés "password" dans des noms de variables, recommandations PEP, etc.) — à confirmer par triage manuel (§ Sb_20.4).

### B.3 Outillage qualité actuel

| Outil | État | Couverture |
|-------|------|-----------|
| pytest | ✅ 734 tests verts | logique métier complète |
| pytest-cov | ❌ absent | aucune mesure |
| ruff | ❌ absent | linter Python rapide manquant |
| mypy | ❌ absent | type hints non vérifiés statiquement |
| bandit | ❌ absent | scan sécurité Python manquant |
| SonarCloud | ⚠️ scan actif sans gate CI | issues remontées mais pas bloquantes |
| pre-commit | ❌ absent | rien ne valide avant commit |
| `tests/test_security.py` | ✅ 9 tests | headers, cookies, timing |
| `tests/test_ownership.py` | ✅ 11 tests | cross-user isolation |

## C. Problème produit / qualité

> Le code SPIGNOS est sain mais ses **garanties qualité** sont implicites. SonarCloud ne sait pas le mesurer, GitHub ne peut pas bloquer une PR qui dégrade la qualité, et un futur contributeur n'a pas de garde-fou automatique.

Symptômes :
- Grade Security E sur SonarCloud → mauvaise carte de visite publique du repo.
- Coverage 0 % rapporté → les 734 tests existants ne sont pas crédités.
- Aucun blocage CI sur régression sécurité ou complexité.
- Aucun rapport périodique sur la dette qualité (que reste-t-il à corriger ?).

## D. Objectifs

1. **Lever le grade Security à A** (≤ 5 issues, 0 hotspot non-reviewé).
2. **Maintainability ≥ B+** (≤ 50 issues acceptées).
3. **Coverage ≥ 70 %** rapporté à SonarCloud.
4. **Gate CI** : bloquer toute PR qui :
   - introduit une issue Security/Reliability **non acceptée**,
   - fait chuter le coverage de plus de 1 point,
   - introduit une duplication > 3 %.
5. **Triage** des 296 issues actuelles : `real` (à corriger) / `accepted` (won't fix avec justification) / `false-positive` (rule mute).
6. **Hardening ciblé** sur les 2 vrais gaps (§B.2) : username regex + password longueur min.

## E. Outillage cible

| Outil | Rôle | Intégration |
|-------|------|-------------|
| **pytest-cov** | Mesure coverage Python | `pyproject.toml` + `.coveragerc` |
| **coverage.xml** | Format consommable par SonarCloud | généré par `pytest --cov` |
| **ruff** | Linter formatter Python ultra-rapide | `pyproject.toml` `[tool.ruff]`, exécuté en CI |
| **mypy** (optionnel V1) | Type checking | `pyproject.toml` `[tool.mypy]`, mode strict progressif |
| **bandit** | Scan sécurité Python (SAST) | `pyproject.toml` `[tool.bandit]`, exécuté en CI |
| **sonar-project.properties** | Config SonarCloud | racine repo, déclare coverage path + exclusions |
| **SonarCloud GitHub Action** | Push des rapports + gate | `.github/workflows/sonar.yml` |
| **pre-commit** (optionnel) | Hooks locaux | `.pre-commit-config.yaml` |

## F. Architecture cible CI

Workflow `.github/workflows/ci.yml` étendu avec **3 jobs parallèles** :

```yaml
jobs:
  test:
    # Existant : pytest + catalog_qa + machine_atlas_qa + alembic_drift
    # Ajout : pytest --cov=app --cov-report=xml + upload coverage.xml artifact
  lint:
    # ruff check . && ruff format --check .
    # bandit -r app/ -ll
  sonar:
    # needs: [test, lint]
    # download coverage.xml artifact
    # SonarSource/sonarcloud-github-action@v2 avec sonar-project.properties
    # gate échoue si Quality Gate SonarCloud "Failed"
```

Quality Gate SonarCloud paramétrée :
- New Security Issues : 0
- New Reliability Issues : 0
- New Maintainability Issues : ≤ 5
- Coverage on New Code : ≥ 70 %
- Duplication on New Code : ≤ 3 %

(Gate s'applique aux **lignes nouvelles** uniquement → ne pénalise pas la dette historique pendant la phase de triage.)

## G. Hardening fonctionnel — corrections ciblées

### G.1 Username path validation (`/users/{username}` — Sb_19)

Le path param est aujourd'hui un `str` libre. Aucune injection (la query SQLAlchemy est paramétrée), mais CWE-20 demande une validation explicite d'allowlist.

```python
@router.get("/users/{username:str}", ...)
def user_profile(
    username: Annotated[str, Path(min_length=2, max_length=64, regex=r"^[a-zA-Z0-9_-]+$")],
    ...
):
```

Effort : 5 min + 1 test.

### G.2 Password length minimum

`auth_routes.py` accepte `password >= 4` chars. Reposer à `>= 8` (best practice OWASP).

Migration utilisateur : ne **pas** invalider les comptes existants, mais imposer le nouveau seuil aux registrations / changements futurs. Effort : 5 min + 1 test.

### G.3 Email regex stricte

Validation actuelle : `"@" not in email` + un point dans le domaine. Remplacer par un regex `r"^[^@\s]+@[^@\s]+\.[^@\s]+$"` (basique mais suffisant pour V1, RFC 5322 complet hors scope).

Effort : 5 min + 1 test.

### G.4 Aucune autre correction sécurité fonctionnelle

L'audit n'a rien trouvé d'autre. Toutes les autres "issues" SonarCloud sont à traiter via §H triage, pas via patch fonctionnel.

## H. Triage des 296 issues SonarCloud

Stratégie : **pas de bulk fix**. Chaque issue passe par 3 catégories :

| Catégorie | Action |
|-----------|--------|
| **real** | Fix dans Sb_20.x dédié. Documenté dans le sprint report. |
| **accepted** | Marqué `won't fix` dans SonarCloud avec justification 1-2 lignes. Reportés cumulés ≤ 30. |
| **false-positive** | Rule muted dans `sonar-project.properties` ou `# nosec` / `# type: ignore` ciblé. Justification dans le commit. |

Heuristique probable d'après l'audit :
- ~70 % des issues = **false-positive** (variables nommées "password", urls externes documentaires, conventions de style FR).
- ~25 % = **accepted** (code legacy bootstrap S0–S4 conservé pour compat, fonctions courtes "complexes" mais lisibles).
- ~5 % = **real** (probablement de la complexité cyclomatique sur 2-3 fonctions, ou des unused imports).

Validation : exporter les issues SonarCloud en CSV (interface UI), trier par catégorie, traiter par lots de 30.

## I. Risques

| Risque | Mitigation |
|--------|------------|
| Triage long (296 issues) | Lots de 30, priorité Security d'abord |
| Coverage 70 % difficile à atteindre sans mock-heavy | Accepter coverage 60 % V1, monter à 70 % en V2 |
| Bandit / mypy generent leur propre flot d'issues | Démarrer en mode `warning`, durcir progressivement |
| Gate CI bloque le merge en plein dogfooding | Gate sur **new code** uniquement, dette historique exemptée |
| SonarCloud GitHub Action requiert un secret `SONAR_TOKEN` | Documenter procédure d'activation dans `docs/CICD_RUNBOOK.md` §3.4 |
| Faux-positifs durables après mute | Auto-revue par sprint : un audit tous les 6 mois |

## J. Plan de sprints — Sb_20.1 → Sb_20.5

Cycle court, sprints courts, livrables atomiques.

### Sb_20.1 — Coverage infrastructure (~3 h)

- Ajouter `pytest-cov`, `coverage` aux dev deps.
- `pyproject.toml [tool.pytest.ini_options]` + `[tool.coverage.run]` + `[tool.coverage.report]`.
- `.coveragerc` (alternativement).
- Modifier `.github/workflows/ci.yml` job `test` : `pytest --cov=app --cov-report=xml --cov-report=term`.
- Upload `coverage.xml` comme artifact.
- Sprint report `SPRINT_Sb_20_1_REPORT.md`.

### Sb_20.2 — Linters & SAST (~3 h)

- Ajouter `ruff`, `bandit` aux dev deps.
- `[tool.ruff]` + `[tool.bandit]` dans `pyproject.toml`.
- Job `lint` dans `ci.yml` : `ruff check`, `ruff format --check`, `bandit -r app/ -ll`.
- Premier passage local : fixer les ruff warnings triviaux (imports, espacement).
- Tolérer les warnings bandit sur secrets faux-positifs via `# nosec B105` ciblé.
- Sprint report.

### Sb_20.3 — Hardening fonctionnel (~2 h)

- §G.1 username regex.
- §G.2 password ≥ 8.
- §G.3 email regex.
- 3 nouveaux tests dans `tests/test_security.py`.
- Sprint report.

### Sb_20.4 — Intégration SonarCloud + triage (~6-8 h)

- Créer `sonar-project.properties` à la racine.
- Workflow `.github/workflows/sonar.yml` (job indépendant ou intégré dans `ci.yml`).
- Configurer le secret `SONAR_TOKEN` (procédure runbook).
- Définir la **Quality Gate** côté SonarCloud (UI).
- Triage des 296 issues : exporter CSV, classer real/accepted/false-positive.
- Mute global des rules false-positive avec justification.
- Sprint report **avec un tableau** issue par issue traitée.

### Sb_20.5 — Verrouillage CI gate (~2 h)

- Activer le **required status check** SonarCloud sur la branche `main` (et `claude/sprint-reporting-fitness-app-V7Qr6` pendant la phase active).
- Mettre à jour `docs/CICD_RUNBOOK.md` avec la procédure SonarCloud (§3.4 nouvelle).
- Mettre à jour `docs/SPRINT_INDEX.md` avec le cycle Sb_20.x complet.
- Sprint report final + bilan Coverage / Grade Security / Maintainability **avant/après**.

**Effort cumulé Sb_20.1 → Sb_20.5 :** 16-20 h. Étalable sur 2 semaines en parallèle du dogfooding.

## K. Acceptance criteria Sx_20

| Critère | Statut |
|---------|--------|
| Audit factuel du code (5 axes OWASP/CWE) documenté §B.2 | ✓ |
| Outillage cible cartographié §E | ✓ |
| Architecture CI cible §F (3 jobs parallèles + Quality Gate) | ✓ |
| Hardening ciblé §G : 3 corrections fonctionnelles chiffrées | ✓ |
| Stratégie de triage §H : 3 catégories real/accepted/false-positive | ✓ |
| Plan de 5 sprints courts §J avec effort | ✓ |
| Risques §I listés | ✓ |
| Aucun gros refactor du code applicatif requis | ✓ (audit montre code sain) |
| Coverage cible ≥ 70 %, security A, maintainability ≥ B+ | ✓ |

## L. Recommandation build suivant

**Sb_20.1 — Coverage infrastructure** en premier. Effort 3h. Effet immédiat sur le grade SonarCloud (le 0 % coverage est probablement responsable d'un quart du grade Security E).

Séquence recommandée : Sb_20.1 → Sb_20.2 → Sb_20.3 → Sb_20.4 → Sb_20.5, en commitant chaque sprint séparément pour traçabilité.

Pré-requis avant Sb_20.4 :
- Compte SonarCloud lié au repo GitHub (probablement déjà fait vu que le scan tourne).
- Token `SONAR_TOKEN` généré et stocké comme secret GitHub.
- Quality Gate SonarCloud configurée (5 minutes UI).

Tout le reste est code-only.

---

## Annexe — Mapping Standards → Sprints

| Standard | Sprint principal | Note |
|----------|------------------|------|
| OWASP A1 Broken Access Control (2021/2017) | déjà respecté (audit §B.2) — Sb_20.4 confirme via SonarCloud | rules `python:S5145`, `S2755` |
| OWASP A3/A1 Injection (2021/2017) | déjà respecté (audit §B.2) | rules `python:S2078`, `S2076` |
| CWE-20 Improper Input Validation | Sb_20.3 (username + password + email) | + bandit en CI |
| CWE-22 Path Traversal | déjà respecté — Sb_20.4 confirme | rules `python:S2083`, `S2076` |
| STIG V-222609 Input Handling | Sb_20.3 + bandit V1 | rules `python:S5527` |
| Coverage 70 % | Sb_20.1 + Sb_20.4 (rapport Sonar) | — |
| Maintainability B+ | Sb_20.4 (triage) + Sb_20.2 (ruff cleanup) | — |

## Annexe — Coût d'opportunité

| Alternative | Coût | Avantage | Inconvénient |
|-------------|------|----------|--------------|
| Refonte complète "OWASP-by-the-book" | 40-60 h | grade A garanti | code déjà sain → effort sans ROI |
| Ne rien faire (laisser SonarCloud crier) | 0 h | aucun | perte de signal qualité, aucune gate |
| **Plan Sx_20 (retenu)** | **16-20 h** | gates CI permanentes, audit visible, calibrage post-ROI | effort modéré sur 2 semaines |
| Migrer SonarCloud → Snyk + CodeClimate | 10 h | autre fournisseur | pas de gain net, pas la demande user |

Plan Sx_20 retenu.
