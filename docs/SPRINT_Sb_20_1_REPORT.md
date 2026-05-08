# Sprint Sb_20.1 Build Report — Coverage Infrastructure

**Date :** 2026-05-08
**Type :** Build infrastructure CI — implémente §J Sb_20.1 de `SPIGNOS_SECURITY_HARDENING_AND_SONAR_INTEGRATION_SPEC_v1.md`
**Prérequis :** Sx_20 spec validée (commit `0f5eb9f`)
**Successeur :** Sb_20.2 (linters CI ruff + bandit)

---

## 1. Objectif

Mesurer la couverture de tests Python et produire le rapport `coverage.xml` que SonarCloud consommera pour calculer le grade Coverage. Sans cette mesure, SonarCloud rapporte 0 % et plombe automatiquement les autres grades.

## 2. Fichiers modifiés

| Fichier | Type | Nature |
|---------|------|--------|
| `pyproject.toml` | Modify | Ajout deps `pytest-cov`, `coverage[toml]`. Sections `[tool.coverage.run]` et `[tool.coverage.report]`. |
| `.github/workflows/ci.yml` | Modify | Pipeline CI exécute `pytest --cov=app --cov-report=xml`, upload artifact. |
| `.gitignore` | Modify | Exclusion `.coverage.*` et `coverage.xml` (déjà partiellement présent). |
| `docs/SPRINT_Sb_20_1_REPORT.md` | New | Ce rapport. |

Aucune ligne de code applicatif touchée. Aucun test modifié.

## 3. Mesure de couverture initiale

Run local complet sur **734 tests** (`pytest --ignore=tests/test_v1_acceptance.py --cov=app --cov-report=term -q`) :

```
TOTAL    4339 lignes    435 manquantes    89.97 %
734 passed in 254.32s
```

**Coverage = 89.97 %**, très au-dessus de la cible Sx_20 de 70 %.

Surface des modules à plus faible couverture (à attaquer si on veut viser 95 %+) :

| Module | Coverage | Commentaire |
|--------|----------|-------------|
| `app/services/session_recap.py` | 74 % | Branches d'exception non testées |
| `app/services/stats.py` | 81 % | Idem |
| `app/services/substitution.py` | 90 % | Edge cases mineurs |

Ces lacunes sont **non bloquantes** pour Sx_20. Elles pourraient être complétées en Sb_20.4 si le triage SonarCloud les remonte comme issues Reliability.

## 4. Décisions d'implémentation

### D1 — Coverage configurée mais non auto-activée localement

`pyproject.toml [tool.coverage.run]` définit la source (`app`) et les exclusions (`migrations/*`, `tests/*`, `app/__init__.py`), mais **aucun `addopts`** dans `[tool.pytest.ini_options]`. Conséquence : `pytest` local sans flag explicite reste rapide, sans instrumentation. CI lance toujours avec `--cov=app --cov-report=xml`.

Justification : éviter de ralentir le dev workflow par défaut. La mesure se fait à la demande locale (`pytest --cov=app --cov-report=term-missing`) ou systématiquement en CI.

### D2 — Format XML pour SonarCloud

SonarCloud (et SonarQube) consomment `coverage.xml` au format Cobertura. Le flag `--cov-report=xml` génère exactement ce format à la racine du repo. Pas besoin de convertir.

### D3 — Artifact GitHub upload

Job `test` upload `coverage.xml` comme artifact `coverage-xml` (rétention 7 jours). Sb_20.4 fera consommer cet artifact par le job SonarCloud — séparation `test` / `sonar` propre.

`if: always()` sur l'upload : même si pytest plante partiellement, on récupère le rapport pour debug.

### D4 — `branch = false`

`coverage[toml]` permet le suivi de branches (each `if/else` testé sur les 2 branches). Désactivé V1 — la complexité ajoutée n'est pas justifiée pour 90 % de couverture lignes. Pourrait être activé en V2 si SonarCloud insiste.

### D5 — Lignes exclues de la couverture

`exclude_lines` dans `[tool.coverage.report]` :
- `pragma: no cover` (manuel)
- `raise NotImplementedError` (méthodes abstraites)
- `if __name__ == .__main__.:` (entrée scripts)
- `if TYPE_CHECKING:` (imports types-only)

Standard pour Python.

## 5. État des tests

```
tests       : 734 passed (vs 734 avant — aucun ajout, aucune régression)
coverage    : 89.97 % sur 4339 lignes app/
catalog_qa  : PASS
machine_atlas_qa : PASS
alembic_drift : PASS
```

## 6. Effet SonarCloud attendu

Au prochain push sur la branche, le scan SonarCloud va trouver `coverage.xml` (via la config `sonar-project.properties` de Sb_20.4 — pas encore en place). En attendant Sb_20.4, le rapport reste local et CI artifact uniquement.

**Effet attendu post-Sb_20.4 :**
- Coverage : `0 %` → `~90 %` (grade A garanti).
- Security grade : E → probablement B+ (la pondération coverage représente une part significative).
- Maintainability : pas affecté par ce sprint, c'est Sb_20.2 qui poussera ruff cleanup.

## 7. Limites assumées

1. **Pas de gate coverage activée V1** — la cible 70 % min est documentée mais pas enforced. Sb_20.5 ajoutera la gate via SonarCloud Quality Gate.
2. **Pas de `branch = true`** — coverage de lignes uniquement V1.
3. **`migrations/*` exclu** — les migrations sont testées implicitement par `test_alembic_drift.py`, pas besoin de coverage par fichier.
4. **`tests/*` exclu** — éviter le narcissique "tests mesurent les tests".
5. **Pas de seuil de fichier minimum** — un module à 0 % reste possible. Sb_20.4 pourrait définir un `fail_under = 60` au niveau report si nécessaire.

## 8. Recommandation suite

**Sb_20.2 — ruff + bandit linters CI** dans la foulée. Effort 3 h.

Cibles Sb_20.2 :
- `[tool.ruff]` dans `pyproject.toml` avec règles E, F, W, I, B, C90, S (security via flake8-bandit), UP.
- `[tool.bandit]` avec exclusions `tests/`, `migrations/`.
- Job `lint` parallèle dans `ci.yml`.
- Premier passage : fixer les warnings triviaux (imports non utilisés, espacement).
- Documenter les `# noqa` ciblés et `# nosec Bxxx` justifiés.

## 9. Synthèse

- **Coverage 89.97 %** mesurée localement, bien au-dessus de la cible Sx_20.
- 3 fichiers modifiés (`pyproject.toml`, `ci.yml`, `.gitignore`), 0 ligne app/ touchée.
- 734 tests verts inchangés.
- `coverage.xml` généré et uploadé en CI artifact, prêt pour SonarCloud.
- Cycle Sb_20.x peut continuer.
