# Sprint Sb_20.3 Build Report — Hardening fonctionnel ciblé

**Date :** 2026-05-08
**Type :** Build sécurité fonctionnel — implémente §G + §J Sb_20.3 de `SPIGNOS_SECURITY_HARDENING_AND_SONAR_INTEGRATION_SPEC_v1.md`
**Prérequis :** Sb_20.2 livré (linters CI advisory).
**Successeur :** Sb_20.4 (SonarCloud config + triage 296 issues)

---

## 1. Objectif

Corriger les trois faiblesses d'input validation identifiées par l'audit Sx_20 §G :

1. `/users/{username}` — pas de regex / longueur sur le path param (CWE-20).
2. Plancher mot de passe trop bas (4 caractères).
3. Validation email rudimentaire (`"@" in email and "." in email`).

Objectif : aligner sur OWASP A3:2021 (injection / input validation) et CWE-20 sans introduire de friction utilisateur excessive.

## 2. Fichiers modifiés

| Fichier | Type | Nature |
|---------|------|--------|
| `app/routers/auth_routes.py` | Modify | `MIN_PASSWORD_LENGTH` 4 → 8. Ajout `MAX_USERNAME_LENGTH=64`, `USERNAME_REGEX`, `EMAIL_REGEX`. `register_submit` applique la regex username + length max + regex email stricte. Profile-edit utilise la regex email. |
| `app/routers/leaderboard.py` | Modify | `/users/{username}` : `username: Annotated[str, Path(min_length=2, max_length=64, pattern=r"^[a-zA-Z0-9_-]+$")]`. FastAPI renvoie 422 avant tout DB lookup. |
| `tests/test_security.py` | Modify | +5 tests Sb_20.3 (username regex, password 7 chars, email regex, path-param invalid, path-param too short). Test dup register passé à mdp 8 chars. |
| `tests/test_register_profile.py` | Modify | 3 tests existants ré-alignés sur le nouveau plancher 8 caractères. |
| `docs/SPRINT_Sb_20_3_REPORT.md` | New | Ce rapport. |

## 3. Décisions d'implémentation

### D1 — Username allowlist `^[a-zA-Z0-9_-]+$`

Mêmes caractères que le formulaire d'inscription. Rejette : unicode (`élève`), espaces, `@`, `.`, `/`. Cohérent avec la majorité des conventions (GitHub, Discord, etc.). Length 3-64 à l'inscription, 2-64 sur le path param (deux comptes existants ont 2 caractères en V0 — on ne les casse pas).

### D2 — Password minimum 8 caractères

Cible NIST 800-63B "memorized secrets" minimum 8 sans contrainte de complexité. Pas de règle de classes de caractères (anti-pattern selon NIST). Les utilisateurs existants (mdp ≥ 4 en DB) ne sont pas affectés — seuls les nouveaux comptes / changements de mdp sont contraints.

### D3 — Email regex pragmatique

Pattern `^[^@\s]+@[^@\s]+\.[^@\s]+$` :
- Au moins un caractère avant `@`, sans espace, sans `@` supplémentaire.
- Un domaine avec au moins un `.` séparant TLD.
- Pas la regex RFC 5322 complète (impossible à vérifier en regex propre, et le vrai filtrage se fait par envoi de mail de confirmation — non implémenté en V1).

Suffisant pour bloquer `"plainstring"`, `"two@@at.com"`, `"trailing@dot."`, etc. Volontairement plus strict que `"@"` simple, volontairement plus laxiste que la RFC.

### D4 — Path param validation déclarative FastAPI

`Annotated[str, Path(...)]` plutôt que validation manuelle dans le handler :
- 422 retourné automatiquement par FastAPI avec un payload JSON détaillant l'erreur.
- Aucun appel DB si le pattern échoue → coupe court à toute énumération via 404 timing.
- Le pattern est documenté dans le schéma OpenAPI auto-généré.

Le commentaire dans `leaderboard.py` cite explicitement Sb_20.3 + CWE-20 pour la traçabilité.

### D5 — Test path param "trop court"

`min_length=2` côté Path → `/users/a` renvoie 422. Test ajouté pour empêcher la régression (un dev pourrait baisser à 1 sans s'en rendre compte).

## 4. Tests ajoutés / modifiés

5 nouveaux tests dans `tests/test_security.py` :
- `test_register_rejects_username_with_special_chars` — 5 entrées invalides (espaces, `@`, `.`, `/`, unicode).
- `test_register_rejects_short_password_below_8` — exactement 7 caractères → 400 + "au moins 8".
- `test_register_rejects_malformed_email` — 5 patterns mal formés, vérifie aussi que le message mentionne "email".
- `test_user_profile_path_param_rejects_invalid_chars` — 422 ou 404 sur 3 entrées hors regex.
- `test_user_profile_path_param_rejects_too_short` — `/users/a` → 422.

3 tests existants ajustés à la nouvelle politique de mdp 8 chars (`test_register_profile.py`) : success path, password mismatch (long enough pour atteindre le check de match), password change mismatch.

`test_register_duplicate_returns_400_not_500` (`test_security.py`) passé à `abcdef12` (8 chars) pour atteindre le check d'unicité.

## 5. État des tests

```
739 passed in 251.44s (vs 734 avant — 5 ajoutés, 0 régression)
ruff : non re-mesuré (advisory non-bloquant)
bandit : 0 Medium / 0 High (inchangé)
```

Note : pour la suite Sx_20 §B confirmant 0 vulnérabilité critique réelle, ce sprint ne change pas le verdict — il ferme des trous d'input validation théoriques.

## 6. Limites assumées

1. **Comptes existants non rétro-validés** — les usernames créés avant Sb_20.3 peuvent contenir des caractères hors regex (peu probable, mais possible). Sb_20.4 pourrait ajouter un script `scripts/audit_usernames.py` si SonarCloud le remonte.
2. **Email regex pragmatique, pas RFC 5322** — voir D3.
3. **Pas de blocklist de mots de passe communs** — NIST 800-63B le recommande (top 10k breached passwords). Pourrait être ajouté en Sb_21+ via `pwned-passwords` API (k-anonymity) si nécessaire.
4. **Pas de rate-limit sur `/register`** — toujours absent. Documenté Sx_20 §B.6, à traiter séparément.

## 7. Synthèse

- 2 fichiers app/ modifiés (auth_routes.py, leaderboard.py), 2 fichiers tests modifiés, 1 nouveau rapport.
- 5 tests sécurité ajoutés (739 passed total, 0 régression).
- Plancher mdp 4 → 8 ; username allowlist appliquée ; email regex stricte ; path-param validé déclarativement.
- 3 corrections OWASP A3/CWE-20 livrées en moins de 2 heures comme prévu.
- Sb_20.4 (SonarCloud config + triage) peut commencer.
