# Multi-Tenant Readiness — Sb_26.7

**Audience :** opérateur SPIGNOS + architecte d'évolution.
**Créé :** 2026-06-14 (sprint Sb_26.7).
**Statut :** documente l'écart entre l'état actuel ("user-scope isolation V1") et une vraie multi-tenancy SaaS.

---

## 1. Pourquoi distinguer "user-scope isolation" vs "multi-tenancy"

SPIGNOS V1 est **multi-utilisateur, pas multi-tenant** :

- **Multi-utilisateur** : N comptes individuels distincts, chacun voit uniquement ses données. Sb_26.7 verrouille cette isolation par la matrice `AUTH_SCOPE_MATRIX.md` + les tests `tests/test_auth_scope_isolation.py`.
- **Multi-tenant** : N **organisations** distinctes, chacune contenant M utilisateurs, avec rôles, quotas, billing, possibilité d'admin org, audit logs, et — souvent — isolation infra par tenant (DB, namespace, certificats).

Le V1 actuel n'a aucun concept d'organisation. Tous les users vivent dans la même DB SQLite, isolés uniquement par `user_id` foreign key.

## 2. Ce qui est déjà prêt (Sb_26.7 confirme)

| Item | Mécanisme V1 | Référence |
|---|---|---|
| Identité utilisateur stable | `users` table, `username` unique, bcrypt hash | `app/models/user.py` |
| Session auth | cookie signé itsdangerous, `Secure`+`HttpOnly`+`SameSite=lax` | `app/services/auth.py` |
| Scope par ressource | `WorkoutSession.user_id` FK + helper `get_owned_session_or_404` | `app/services/ownership.py` |
| Tests d'isolation cross-user | 16 cas (sessions, exports, coach report, history, admin) | `tests/test_auth_scope_isolation.py` |
| Rate limiting auth | per-IP `/login`, `/register`, `/forgot-password` | Sb_26.4, `docs/SECURITY_BASELINE.md §2` |
| Headers sécurité | CSP, X-Frame DENY, Referrer, Permissions-Policy | `app/main.py:SecurityHeadersMiddleware` |
| Audit baseline | matrice route → scope dans `AUTH_SCOPE_MATRIX.md` | livré Sb_26.7 |
| Sessions legacy `user_id IS NULL` filtrées | filtre `user_id == uid` les exclut naturellement | `app/services/ownership.py` §8 |
| Routes semi-publiques explicitées | contrat de divulgation Sb_19 (leaderboard, /users/{username}) | matrice §2 |

## 3. Ce qui n'est PAS prêt pour une vraie multi-tenancy

| Item manquant | Pourquoi nécessaire en multi-tenant | Effort estimé |
|---|---|---|
| `tenant_id` sur toutes les tables | scoping de niveau supérieur à user_id | M (migration + audit + tests) |
| Table `organizations` | unité de facturation/configuration | S |
| Table `organization_memberships` (user_id, org_id, role) | un user peut être dans plusieurs orgs | S |
| RBAC complet (owner/admin/member/viewer) | permissions par rôle dans une org | M-L |
| Data partitioning | éviter qu'une org A puisse même accidentellement requêter org B | L (couches DB ou query layer) |
| Admin org panel | gérer membres, invitations, settings | M |
| Audit logs | obligatoire pour compliance (GDPR, SOC2) | M |
| Tenant export/delete | obligation légale GDPR (droit à l'effacement) | M |
| Quotas (storage, sessions/mois, etc.) | différencier les tiers de facturation | S |
| Billing intégré | Stripe Customer + Subscription per org | L |
| Infra isolation (optionnel) | DB par tenant, ou schema PG par tenant, ou logique | L-XL |
| Vrai backup per-tenant | restauration ciblée | M |
| API tokens scopés org | accès machine-to-machine | M |
| Monitoring per-tenant (Sentry tags, Discord channels) | troubleshooting ciblé | S |
| Limites de débit per-tenant | rate limiting au-delà du per-IP | M |

**Tout ce qui précède est explicitement HORS SCOPE de Sb_26.7 et hors Sx_26.**

## 4. Pourquoi on n'implémente pas la multi-tenancy maintenant

| Raison | Détail |
|---|---|
| **Pas de besoin métier** | SPIGNOS V1 vise un usage individuel + petits groupes (squads), pas un produit B2B SaaS |
| **Coût massif** | Migration + refonte models + UI admin = sprint dédié de plusieurs semaines |
| **Risque de drift** | Introduire `tenant_id` sans usage clair = code mort, compliance overhead inutile |
| **Inversion de la complexité** | Le bon temps pour multi-tenant = quand le 1er client B2B signe, pas avant |
| **Verbatim user constraint** | "Ne crée pas de table tenant. Ne crée pas de table organization. Ne crée pas de billing." (Sb_26.7 prompt) |

## 5. Trajectoire si on devait y aller (esquisse roadmap)

Si SPIGNOS prend la direction SaaS multi-tenant, ouvrir un cycle **Sx_30** (nouveau cycle complet, hors Sx_26) avec ces lots prévisionnels :

| Sb_30.k | Objet | Effort |
|---|---|---|
| Sb_30.1 | Spec multi-tenant : modèle data, routes, RBAC | spec only |
| Sb_30.2 | Migration `organizations` + `organization_memberships` + backfill mono-org | M |
| Sb_30.3 | `tenant_id` sur toutes les tables data + filter middleware DB | L |
| Sb_30.4 | RBAC : décorateurs `@requires_role("owner")` etc. + UI admin | M |
| Sb_30.5 | Audit logs persistants + endpoints d'audit | M |
| Sb_30.6 | Quotas + billing Stripe | L |
| Sb_30.7 | Tenant export / delete GDPR | M |
| Sb_30.8 | Migration prod : assigner tous les users existants à une org "default" | S |

Estimation totale brute : 6-10 semaines de build. À évaluer.

## 6. Décision Sb_26.7

✅ **Confirmer la posture V1 "user-scope isolation"** : isolation cross-user fiable via matrice + tests, **sans** introduire le poids architectural d'une vraie multi-tenancy.

Le jour où le besoin business apparaît, le cycle Sx_30 sera ouvert. Pas avant.

## 7. Limites assumées (verbatim contraintes user)

| Item | Statut |
|---|---|
| Pas de table tenant | ✅ |
| Pas de table organization | ✅ |
| Pas de billing | ✅ |
| Pas de RBAC complet | ✅ |
| Pas d'admin panel multi-tenant | ✅ |
| Pas de refonte auth | ✅ |
| Single-user experience préservée | ✅ |
