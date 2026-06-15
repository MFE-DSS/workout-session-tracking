# UX Simplification Notes — Sb_27.6

**Audience :** opérateur SPIGNOS + agent.
**Créé :** 2026-06-15 (sprint Sb_27.6).
**Statut :** documente les décisions UX de simplification de Sx_27 sans refonte UI complète.

---

## 1. Surfaces principales (post-Sx_27)

| Route | Rôle V1 stable | Modifié dans Sx_27 ? |
|---|---|---|
| `/` (Home) | **point d'entrée coaching quotidien** — Today / Last / Week | ✅ Sb_27.1 (composer) + Sb_27.4 (raisons) + Sb_27.5 (narrative) |
| `/progress` | page analytique + suivi tendances + **weekly loop** | ✅ Sb_27.3 (weekly tile en tête) + Sb_27.5 (narrative) |
| `/sessions/{id}/done` | **Session Review V1** post-séance | ✅ Sb_27.2 (5 sub-payloads) + Sb_27.5 (narrative) |
| `/launcher` | démarrer une séance (flux guidé) | non modifié |
| `/history` | recherche / lookup historique | non modifié |
| `/coach-report` | rapport détaillé Sb_23 | non modifié |
| `/physique` | body tracking | non modifié |
| `/library`, `/science`, `/rules` | catalogue méthodologique | non modifié |
| `/leaderboard`, `/users/{username}` | semi-public Sb_19 | non modifié |
| `/squads/*` | groupes (Sx_22) | non modifié |
| `/profile/*` | profil + body + measurements | non modifié |

## 2. Surface dépréciée

| Route | Statut | Comportement | Décision |
|---|---|---|---|
| `GET /dashboard` | **DEPRECATED Sb_27.6** | Retourne `303 → /` pour tout utilisateur authentifié. Auth dependency préservée : un anonyme reçoit toujours `303 → /login`. | OQ-3 tranchée verbatim user : déprécier proprement, pas de suppression brutale |

### 2.1 Pourquoi `/dashboard` plutôt qu'une autre route

- `/` couvre désormais les besoins coaching quotidien (Sb_27.1)
- `/progress` couvre l'analytique de suivi (Sb_27.3)
- `/dashboard` (KPIs body engineering) faisait doublon avec `/physique` et `/progress`
- L'utilisateur arrivait sur 3 surfaces "compte / progression / synthèse" avec une mind map floue

### 2.2 Pas de suppression brutale (verbatim user)

- `app/templates/dashboard.html` : **conservé** dans le repo
- `app/services/dashboard.py:compute_dashboard` : **non touché**
- `app/services/profile_metrics.py`, `app/services/muscle_scoring.py` (consommés par dashboard.py) : **non touchés**

Conséquence : si la décision est révisée en Sx_28+, réintroduire `/dashboard` = changer le handler en `templates.TemplateResponse(...)` puis re-ajouter le lien de nav. Aucun code mort en attendant — la route répond toujours (juste en redirect).

### 2.3 Compatibilité bookmarks externes

Un bookmark `/dashboard?window=60` continue de fonctionner : le paramètre `window` est silencieusement ignoré et l'utilisateur atterrit sur Home. Pas de 404 pour les vieux liens.

## 3. Navigation simplifiée

### 3.1 Avant (base.html nav)
```
Accueil · Programmes · Historique · Physique · Synthèse · Classement · Squads · Profil · Coach · Déconnexion
```
(9 liens + bouton, "Synthèse" pointe vers `/dashboard`)

### 3.2 Après (Sb_27.6)
```
Accueil · Programmes · Historique · Physique · Progression · Classement · Squads · Profil · Coach · Déconnexion
```
(9 liens + bouton, "Progression" pointe vers `/progress`)

### 3.3 Justification

- **Pas de suppression d'entrée** : on garde le même nombre de liens. Une suppression brutale aurait sectionné des chemins d'accès existants (Squads, Coach, Physique, Classement) sans gain immédiat.
- **Renommage 1:1** : "Synthèse" → "Progression", `/dashboard` → `/progress`. L'utilisateur retrouve la même position dans la nav.
- **Le menu reste en `<details>`** (mobile-first 360×640) : pas de scroll horizontal, pas de redesign system.

### 3.4 Non-goals (verbatim user)

- ❌ Pas de refonte UI complète
- ❌ Pas de redesign system
- ❌ Pas de changement de palette
- ❌ Pas de nouvelle route
- ❌ Pas de refonte du flow de capture de séance
- ❌ Pas de suppression massive de templates
- ❌ Pas de changement fonctionnel sur `/progress` hors libellé/navigation

## 4. Impact tests

### 4.1 Tests modifiés

| Fichier | Changement |
|---|---|
| `tests/test_dashboard_routes.py` | Réécrit : les 5 tests 200/rendering historiques deviennent 4 tests "deprecated redirect" (303 → /, auth still redirects to /login, follow redirect lands on Home, window param tolerated) |
| `tests/test_session_done.py` | 1 assertion mise à jour : la page `/done` ne référence plus `/dashboard` (la session review Sb_27.2 expose ses propres CTAs Retour Accueil + Nouvelle séance) |

### 4.2 Tests ajoutés (`tests/test_ux_navigation.py`)

- `test_dashboard_redirects_to_home` : doublon explicite du contrat OQ-3
- `test_home_still_200`
- `test_progress_still_200`
- `test_navigation_has_primary_entries` : nav contient Accueil + Progression + Historique
- `test_navigation_reaches_launcher` : un CTA atteint `/launcher`
- `test_navigation_does_not_promote_dashboard` : pas de `topbar__link" href="/dashboard"`, pas de `Synthèse</a>`
- `test_session_done_does_not_promote_dashboard` : même contrat sur la page de fin de séance

### 4.3 Tests existants non régressés

- `tests/test_auth_scope_isolation.py::test_anonymous_cannot_access_private_routes` continue de vérifier que GET `/dashboard` sans auth → 303 (l'auth dependency reste devant le handler)
- Tous les autres tests Sx_27 (Sb_27.1 à Sb_27.5) restent verts

## 5. Mind map utilisateur (post-Sx_27)

```
┌────────────────┐
│   /  (Home)    │  ← point d'entrée
│   Aujourd'hui  │
│   Dernière     │
│   Cette sem.   │
└───────┬────────┘
        │
        ├── /launcher       (démarrer)
        ├── /progress       (analytique + weekly loop)
        ├── /history        (recherche)
        ├── /coach-report   (synthèse détaillée)
        ├── /sessions/{id}/done  (review post-séance)
        └── nav secondaires (Programmes, Physique, Classement, Squads, Profil)
```

## 6. Backlog futur

| Item | Pourquoi pas dans Sb_27.6 | Reporté à |
|---|---|---|
| Suppression effective de `dashboard.html` + `compute_dashboard` | Verbatim user "pas de suppression brutale" | Sb_27.next.cleanup-dashboard si dogfood confirme la dépréciation |
| Réorganisation de la nav (moins de 9 liens) | Hors scope V1, demande dogfood + retours | post-Sx_27 |
| Footer / breadcrumbs / homerun layout | Hors scope V1 | post-Sx_27 |
| Theme dark/light user-choice | Hors scope V1 | post-Sx_27 |

## 7. Contrats verrouillés par Sb_27.6

| Contrat | Mécanisme |
|---|---|
| `/dashboard` est un redirect, pas une surface | `test_dashboard_redirects_to_home`, `test_navigation_does_not_promote_dashboard` |
| `/` reste la Home coaching | `test_home_still_200` + tests Sb_27.1 |
| `/progress` reste la page analytique | `test_progress_still_200` + tests Sb_27.3 |
| Nav contient Accueil + Progression + Historique | `test_navigation_has_primary_entries` |
| Un CTA atteint `/launcher` | `test_navigation_reaches_launcher` |
| Aucun service métier core touché | review humaine — `app/services/scoring/`, `recommendation.py`, etc. non modifiés |
