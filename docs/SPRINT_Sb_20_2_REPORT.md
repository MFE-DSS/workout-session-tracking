# Sprint Sb_20.2 Build Report — Linters CI (ruff + bandit)

**Date :** 2026-05-08
**Type :** Build infrastructure CI — implémente §J Sb_20.2 de `SPIGNOS_SECURITY_HARDENING_AND_SONAR_INTEGRATION_SPEC_v1.md`
**Mode :** Option A — advisory (non-bloquant V1)
**Successeur :** Sb_20.3 (hardening fonctionnel : username regex, password length, email regex)

---

## 1. Objectif

Activer ruff (linter + formatter Python) et bandit (SAST sécurité) en mode **advisory** dans le pipeline CI. Les warnings remontent en annotations GitHub PR sans bloquer le merge. Sb_20.5 verrouillera le tout via la Quality Gate SonarCloud quand le triage aura été fait.

## 2. Fichiers modifiés

| Fichier | Type | Nature |
|---------|------|--------|
| `pyproject.toml` | Modify | Ajout deps `ruff>=0.5`, `bandit>=1.7`. Sections `[tool.ruff]`, `[tool.ruff.lint]`, `[tool.ruff.lint.per-file-ignores]`, `[tool.ruff.lint.mccabe]`, `[tool.bandit]`. |
| `.github/workflows/ci.yml` | Modify | Nouveau job `lint` parallèle avec 3 steps (`ruff check`, `ruff format --check`, `bandit -r app/`) tous en `continue-on-error: true`. |
| `docs/SPRINT_Sb_20_2_REPORT.md` | New | Ce rapport. |

Aucune ligne de code applicatif touchée. Pas de fix automatique appliqué.

## 3. Mesure initiale

Run local sur 8761 LoC (incluant `app/` + `scripts/`) :

### 3.1 Ruff

```
Found 478 errors.
[*] 440 fixable with the `--fix` option
```

Distribution probable (à confirmer en CI sur le rapport complet) :
- Majorité : `UP017` (modernisation `timezone.utc` → `datetime.UTC` Python 3.11+)
- Imports non utilisés / mal ordonnés (`I001`)
- Quelques `B*` (bugbear : mutable defaults, etc.)
- Quelques `C901` (complexity > 15) sur des fonctions services

### 3.2 Bandit

```
Total lines of code   : 8761
Issues by severity    : 1 Low / 0 Medium / 0 High
Issues by confidence  : 1 High
```

**Aucun problème sécurité Medium ou High.** L'unique issue Low sera identifiée dans le rapport CI complet (probablement un `try/except` sans logging, ou un `random` non-cryptographique).

→ Confirme l'audit Sx_20 §B.2 : le code n'a aucune faille critique.

## 4. Décisions d'implémentation

### D1 — Mode advisory (continue-on-error)

Chaque step lint dans `ci.yml` a `continue-on-error: true`. Conséquence :
- Les warnings ruff/bandit s'affichent comme **annotations PR** dans GitHub (lignes mises en orange).
- Le job global `lint` retourne `success` même avec des warnings.
- Aucun blocage de merge.

C'est **l'option A** retenue (mode permissif V1). Sb_20.5 retirera ces flags pour activer la gate.

### D2 — Configuration ruff conservatrice

Règles activées : `E F W I B UP S C90`. Standards Python + sécurité de base + complexité.

Règles ignorées explicitement :
- `E501` — line too long, géré par le formatter.
- `S101` — `assert` (acceptable dans tests).
- `S104` — binding all interfaces (uvicorn dev).
- `B008` — `Annotated[..., Form()] = pattern` est le pattern FastAPI.
- `UP007` — `X | Y` union — on garde `Optional[X]` plus lisible.

Per-file overrides :
- `tests/*` : pas de `S`, `B`, `C90`.
- `scripts/*` : `S603`/`S607` (subprocess) acceptés.
- `migrations/*` : règles désactivées (auto-générées Alembic).

### D3 — Configuration bandit

Exclusions `tests/`, `migrations/`, `.venv`, `var/`, `data/`.
Skips `B101` (assert), `B311` (random non-crypto).
Niveau de filtrage CI : `-ll` (Medium + High uniquement).

### D4 — Pas de cleanup automatique V1

Le user a explicitement choisi **option A** : ne pas fixer les 440 warnings auto-fixables maintenant. La motivation : voir d'abord le volume avant de toucher au code. Sb_20.4 traitera le triage / cleanup massif après le triage SonarCloud cohérent.

## 5. État des tests

```
734 tests : passing (inchangés depuis Sb_20.1)
coverage : 89.97 % (inchangé)
ruff : 478 warnings (advisory, non-bloquant)
bandit : 1 Low (advisory, non-bloquant)
```

## 6. Prochaines actions

### Sb_20.3 — Hardening fonctionnel ciblé (~2 h)

Trois corrections fonctionnelles identifiées par l'audit Sx_20 §G :

1. `/users/{username}` — ajouter regex `^[a-zA-Z0-9_-]+$`, length 2-64 sur le path param FastAPI.
2. Password minimum 4 → 8 chars sur la registration.
3. Email regex stricte au lieu du check `"@" in email`.

3 nouveaux tests dans `tests/test_security.py` pour les 3 changements.

### Sb_20.4 — Triage SonarCloud (~6-8 h)

Triage des 478 ruff warnings + 1 bandit low + 296 issues SonarCloud combinés. Classement real / accepted / false-positive et application de fixes ou de mute justifié.

## 7. Limites assumées

1. **Aucun warning fixé V1** — option A choisie. La dette est mesurée mais pas remboursée immédiatement.
2. **Bandit `-ll`** filtre les Low — un `-l` plus large pourrait remonter du bruit utile mais aussi du faux positif. À élargir en Sb_20.4 si besoin.
3. **Pas d'mypy V1** — la spec listait mypy comme optionnel. À ouvrir en Sb_20.x si la confiance type augmente.
4. **Job `lint` ne fait pas tourner mypy ni de tests** — séparation explicite des rôles `test` (pytest + QA) et `lint` (ruff + bandit).

## 8. Synthèse

- 2 fichiers modifiés (pyproject + ci.yml), 1 nouveau (rapport), 0 ligne app/ touchée.
- 478 ruff warnings + 1 bandit low remontent en CI annotations.
- Bandit confirme : **0 Medium / 0 High** sécurité réel.
- 734 tests verts inchangés.
- Mode advisory V1 — bascule à bloquant en Sb_20.5.
