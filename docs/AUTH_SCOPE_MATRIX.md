# Auth Scope Matrix — Sb_26.7

**Audience :** contributeurs SPIGNOS + reviewer sécurité.
**Créé :** 2026-06-14 (sprint Sb_26.7).
**Statut :** matrice des routes ↔ ressources ↔ scope auth. Sert de contrat anti-régression d'isolation user. Doit être mise à jour avec **chaque** ajout / suppression de route privée.

---

## 1. Légende

| Code | Sens |
|---|---|
| `🔒 OWNED` | route privée. Charge la ressource via filtre `user_id == caller.id` ou helper `get_owned_session_or_404`. Test d'isolation requis. |
| `👤 SELF` | route privée mais lit/écrit toujours les données du caller (pas de path-param ressource). Test "anon → redirect login" requis. |
| `🌐 SEMI-PUBLIC` | route privée (auth requise) mais expose intentionnellement des données d'autres users selon un contrat de divulgation documenté (leaderboard). Test : pas de fuite de fingerprints privés. |
| `🆓 PUBLIC` | route ouverte sans auth (welcome, login, register, healthz). Pas de scope auth. |
| `🛂 ADMIN-SCOPED` | route préfixée `/admin/` mais ne donne PAS d'accès cross-user — purement les ressources du caller, juste avec UI admin. |

## 2. Routes recensées (Sb_26.7, état réel du repo)

| Route | Méthode | Ressource accédée | Scope | Helper / Mécanisme | Test d'isolation |
|---|---|---|---|---|---|
| `/healthz` | GET | DB ping | 🆓 PUBLIC | — | n/a |
| `/healthz/strict` | GET | DB + backup + disk + deploy_state | 🆓 PUBLIC | — | tests/test_observability.py |
| `/welcome` | GET | template only | 🆓 PUBLIC | — | n/a |
| `/login` | GET/POST | user lookup (constant-time) | 🆓 PUBLIC | rate limited Sb_26.4 | tests/test_auth.py, test_rate_limiting.py |
| `/register` | POST | user creation | 🆓 PUBLIC | rate limited Sb_26.4 | tests/test_auth.py |
| `/forgot-password` | GET/POST | reset token | 🆓 PUBLIC | rate limited Sb_26.4 | tests/test_password_reset.py |
| `/reset/{token}` | GET/POST | reset token consumption | 🆓 PUBLIC | one-shot DB token | tests/test_password_reset.py |
| `/logout` | POST | clear cookie | 👤 SELF | — | n/a |
| `/` | GET | latest session + reco | 👤 SELF | `CurrentUser` | test_anonymous_cannot_access_private_routes |
| `/history` | GET | list of `WorkoutSession` | 👤 SELF | `WorkoutSession.user_id == user.id` | test_history_does_not_show_other_users_sessions |
| `/progress` | GET | analytics user-scoped | 👤 SELF | `CurrentUser` + service filtre | test_anonymous_cannot_access_private_routes |
| `/dashboard` | GET | KPIs user-scoped | 👤 SELF | `CurrentUser` | idem |
| `/physique` | GET | physique dashboard caller | 👤 SELF | `CurrentUser` | idem |
| `/launcher` | GET | session launcher | 👤 SELF | `CurrentUser` | idem |
| `/library`, `/library/{slug}` | GET | reference docs (catalog) | 👤 SELF (auth) | `CurrentUser` mais ressource non-user | idem |
| `/science`, `/rules`, `/science/atlas` | GET | static catalog | 👤 SELF (auth) | `CurrentUser` | idem |
| `/sessions` | POST | create new session | 👤 SELF | `instantiate_session(..., user_id=user.id)` | tests/test_v1_acceptance.py |
| `/sessions/{id}` | GET | one session | 🔒 OWNED | `_load_session(db, id, user.id)` | **test_user_b_cannot_read_user_a_session_detail** |
| `/sessions/{id}/done` | GET | completed session | 🔒 OWNED | idem | tests/test_user_profile_drilldown.py |
| `/sessions/{id}` | POST | mutate session (complete/skip) | 🔒 OWNED | `_load_session` | **test_user_b_cannot_post_to_user_a_session** |
| `/sessions/{id}/exercises/{seid}` | POST | mutate set logs | 🔒 OWNED | `get_owned_session_or_404` | test_v1_acceptance covers happy path; test_user_b_cannot_post enforces isolation via 404 on parent |
| `/sessions/exercise-history/{slug}/{code}` | GET | history of one exercise | 👤 SELF | `get_exercise_history(..., user_id=user.id)` | n/a (pas de path-param user) |
| `/coach-report` | GET | LLM-augmented synthesis | 👤 SELF | `build_report(db, user)` + `build_inference` | **test_coach_report_is_per_user** |
| `/export` | GET | export landing | 👤 SELF | `WorkoutSession.user_id == user.id` (filter `_uf`) | tests/test_export.py |
| `/export/sessions.json` | GET | full JSON dump | 👤 SELF | `build_json_payload(db, user_id=user.id)` | **test_user_b_export_json_does_not_contain_user_a_data** |
| `/export/sessions.csv` | GET | full CSV dump | 👤 SELF | `build_csv_text(db, user_id=user.id)` | **test_user_b_export_csv_does_not_contain_user_a_data** |
| `/admin/sessions` | GET | list caller's sessions (admin UI) | 🛂 ADMIN-SCOPED | `WorkoutSession.user_id == user.id` | **test_admin_sessions_list_scoped_to_caller** |
| `/admin/sessions/{id}/delete` | POST | delete one session | 🔒 OWNED | `get_owned_session_or_404` | **test_user_b_cannot_delete_user_a_session_via_admin** |
| `/admin/sessions/{id}/exclude` | POST | toggle exclude_from_stats | 🔒 OWNED | `get_owned_session_or_404` | **test_user_b_cannot_toggle_exclude_user_a_session** |
| `/readiness` | POST | save readiness for caller | 👤 SELF | `save_readiness(db, user.id, data)` | tests/test_readiness.py |
| `/readiness/history` | GET | caller's readiness history | 👤 SELF | `CurrentUser` | idem |
| `/leaderboard` | GET | top-N users grade | 🌐 SEMI-PUBLIC | auth required, no per-session data leaked | n/a (no user-specific isolation needed — public-by-design) |
| `/users/{username}` | GET | grade + sessions count + radar 30j | 🌐 SEMI-PUBLIC | spec Sb_19 disclosure contract | **test_leaderboard_user_profile_is_intentionally_semi_public** |
| `/users/{username}/preview` | GET | smaller version idem | 🌐 SEMI-PUBLIC | idem | idem (couvert par même contrat) |
| `/squads` family (10 routes) | GET/POST | squad memberships | 🔒 OWNED via membership | `is_member(db, squad_id, user.id)` + scope par squad | tests/test_squads.py |
| `/profile`, `/profile/body`, `/profile/measurements`, `/profile/password` | GET/POST | caller's profile + body data | 👤 SELF | `CurrentUser` | tests/test_auth.py, test_measurements.py |
| `/contact` | GET/POST | static + form | 👤 SELF | `CurrentUser` | n/a |

## 3. Helpers d'ownership

### 3.1 `app/deps.py`

| Helper | Rôle | Tests |
|---|---|---|
| `require_user` | Récupère `User` via cookie session, raise `_redirect_to_login` si absent | tests/test_auth.py |
| `CurrentUser` alias | `Annotated[User, Depends(require_user)]` — import dans tout router privé | usage massif |
| `DbSession` alias | `Annotated[Session, Depends(get_db)]` | idem |
| `_redirect_to_login` | sentinel exception catchée par handler global → 303 vers `/login` | n/a |

### 3.2 `app/services/ownership.py`

| Helper | Rôle | Tests |
|---|---|---|
| `get_owned_session_or_404(db, session_id, user_id)` | Charge `WorkoutSession` filtré par owner, 404 sinon | **test_get_owned_session_or_404_*** (3 cas) |
| `user_sessions_filter(user_id)` | Clause WHERE réutilisable `WorkoutSession.user_id == uid` | usage indirect dans services |

## 4. Gaps identifiés (audit Sb_26.7)

| Gap | Sévérité | Décision |
|---|---|---|
| Aucun gap fonctionnel détecté | — | toutes les routes auditées sont correctement scopées |
| Pas de helper `get_owned_squad_or_404` (la logique est dans `app/routers/squads.py` via `is_member`) | mineur | acceptable V1 — le pattern est inlined par souci de lisibilité, couvert par tests/test_squads.py |
| Pas de helper `get_owned_measurement_or_404` | mineur | les routes mesures sont 👤 SELF, pas de path-param ressource → pas nécessaire |
| Sessions V1 legacy avec `user_id IS NULL` | non régression | filtre `user_id == uid` les exclut naturellement (`app/services/ownership.py` §8) |

**Aucune modification de code métier n'a été nécessaire dans Sb_26.7.** L'audit confirme que l'hygiène d'ownership a été tenue lot par lot depuis Sb_09/Sb_20.

## 5. Procédure pour ajouter une nouvelle route privée

1. Choisir le scope (`OWNED` / `SELF` / `ADMIN-SCOPED`).
2. Si `OWNED` : utiliser `get_owned_session_or_404` (ou créer un nouvel helper si une autre ressource path-paramée).
3. Si `SELF` : filtrer toute requête DB par `WorkoutSession.user_id == user.id` (ou équivalent pour le modèle concerné).
4. **Mettre à jour cette matrice** dans le même commit que la route.
5. Ajouter un cas de test d'isolation dans `tests/test_auth_scope_isolation.py`.
6. CI : `scripts/check_auth_scope_matrix.py` vérifie l'existence du fichier (pas de NLP).

## 6. Limites V1

- Pas d'audit log persistant des accès cross-user (Sb_27+)
- Pas d'attribute-level scope (champ `free_note` lu/écrit en entier) — acceptable V1
- Pas de RBAC : un user a accès intégral à ses propres données, pas de rôle "lecteur"
- Pas de scope par tenant_id — V1 n'a pas de notion de tenant ; cf. `docs/MULTI_TENANT_READINESS.md`
