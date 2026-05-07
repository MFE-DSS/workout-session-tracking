# SPIGNOS Leaderboard Drilldown Spec v1

**Sprint ID :** Sx_19_leaderboard_drilldown_spec
**Date :** 2026-04-21
**Statut :** SPEC ONLY — aucun code engagé par ce document
**Origine :** dogfooding J+0 §F3
**Successeur :** Sb_19_leaderboard_drilldown_build

---

## A. Statut

Spec courte et pragmatique. Le sujet est avant tout UX (un signal supplémentaire au survol + une page profil publique compacte) sur des briques qui existent déjà : `compute_leaderboard`, `compute_physique_dashboard` (radar), `User.height_cm/weight_kg`, modèle `Squad`. Aucune nouvelle source de données.

## B. Contexte

### B.1 État actuel

- [app/services/leaderboard.py](../app/services/leaderboard.py) calcule un `LeaderboardEntry` (rank, username, total_points, grade, last_session_score) par user actif.
- [app/templates/leaderboard.html](../app/templates/leaderboard.html) affiche la liste, avec un **tooltip** simple sur le grade badge montrant le score de la dernière session + libellé du grade.
- Bandeau « Privacy first · activité agrégée uniquement » en tête de page.
- `compute_physique_dashboard` produit un hexagone radar (6 axes) pour le user courant — disponible sur `/physique` aujourd'hui mais codé avec scope `user.id` du caller.
- `User` a déjà `height_cm`, `weight_kg`, `email`, `created_at`. Pas de champ `bio`/`avatar`.
- Pas de notion d'opt-in privacy explicite. Les `Squad` existent (groupes privés), les `LeaderboardEntry` ne filtrent **pas** par squad — leaderboard mondial.

### B.2 Demande utilisateur (notes dogfooding F3)

Trois éléments :

1. **Hexagone radar 30j au survol** d'une entry du leaderboard, en complément du grade badge actuel.
2. **Click sur le username** → page profil publique : hexagone + métadonnées (taille, poids, …).
3. **Retirer le doublon** du score (au-dessus + au centre du radar) — déjà traité par fixpack v1 commit `59a93ea`.

## C. Décisions produit

### C.1 Privacy V1 — permissif et explicite

- Le leaderboard expose déjà l'username + le grade publiquement. Ajouter un radar 30j et la taille/poids reste **dans le même contrat de partage**.
- Pas d'opt-in V1 — permissif comme l'existant.
- Le bandeau « Privacy first · activité agrégée uniquement » reste vrai au sens où on n'expose **toujours pas** les détails par séance, le tonnage, les exercices, les notes.
- **Donnée ajoutée publique :** taille, poids global, scores radar 6 axes, count de séances 30j.
- **Donnée jamais exposée :** liste de séances, détails d'exercices, notes libres, mesures détaillées (chest_cm, etc.), email, BP, fatigue subjective.

### C.2 Trois surfaces

| Surface | Rôle | Contenu |
|---------|------|---------|
| Tooltip leaderboard (étendu) | Aperçu rapide sans naviguer | Mini radar SVG 30j + grade badge + last_session_score |
| Lien `username` cliquable | Drilldown vers le profil | `<a href="/users/{username}">…</a>` |
| Page `/users/{username}` (nouvelle) | Synthèse publique | Header (username, grade, sessions count 30j) + radar 30j + métadonnées (taille, poids) |

### C.3 Pas de page « historique » publique

L'utilisateur a dit : « ce n'est pas son historique, c'est plus une synthèse ». La page `/users/{username}` est volontairement courte : un bloc résumé, pas de liste de séances. Si tu veux ton propre historique détaillé, ça reste sur `/profile` et `/history` (privé, scope self).

### C.4 Pas d'opt-out V1

Le user actif (`is_active=True`) qui apparaît dans le leaderboard apparaît automatiquement sur `/users/{username}`. Si un utilisateur veut sortir du classement, il peut désactiver son compte — geste cohérent. Un opt-out granulaire (« visible dans le leaderboard mais profil privé ») relève d'une V2.

## D. Architecture

### D.1 Mini-radar dans le tooltip

- Le `compute_leaderboard` actuel produit `LeaderboardEntry` par user. On l'étend avec un nouveau champ `radar_svg_mini: str | None`.
- Pour chaque entry, on calcule via `compute_physique_dashboard(db, user_id, window_days=30)`. Coût : 1 call SQLAlchemy déjà optimisé. Sur N users, on fait N appels — si la liste devient longue (> 100 users) on optimisera. V1 : volume utilisateur faible.
- `build_radar_svg` est généralisé pour accepter une taille compacte (par défaut une cartouche large, on ajoute un paramètre `compact: bool` pour produire un SVG ~120×120px).
- Le tooltip CSS existant est étendu pour accueillir le SVG.

### D.2 Lien username → page profil

- Dans `leaderboard.html`, transformer le `<span class="lb-row__name">` en `<a href="{{ url_for('user_profile', username=e.username) }}">`.
- Conserver le tooltip wrapper qui reste accessible au clavier.

### D.3 Nouvelle route `/users/{username}`

- `GET /users/{username}` → `name="user_profile"`.
- Auth required (cohérent avec le reste).
- Lookup user par username, 404 si inactif ou inexistant.
- Build le dashboard via `compute_physique_dashboard(db, target_user.id, window_days=30)`.
- Compte les séances 30j, last_session_score 30j.
- Render `templates/user_profile.html` avec :
  - Header : username, grade badge, count séances 30j.
  - Radar SVG 30j taille pleine.
  - Métadonnées : `height_cm`, `weight_kg` si présents (formatés `1m72`, `78 kg`). Sinon ne pas afficher la ligne.
  - Footer : « Profil public · activité agrégée uniquement ».

Page **statique** (pas de chart history, pas de filtres). Charge < 200ms attendue.

### D.4 Effort

- `app/services/leaderboard.py` : extend `LeaderboardEntry` + appel `compute_physique_dashboard`. ~30 min.
- `app/services/radar.py` : ajouter mode `compact` à `build_radar_svg`. ~30 min.
- `app/templates/leaderboard.html` : ajouter mini-svg dans tooltip + lien username. ~30 min.
- `app/static/css/app.css` : élargir le tooltip pour le svg mini. ~15 min.
- Nouvelle route `user_profile` + template. ~1 h.
- Tests : `test_leaderboard_ui.py` (tooltip svg), `test_user_profile_route.py` (200, 404, contenu). ~1 h.
- Sprint report. ~30 min.

**Build estimé Sb_19 : ~4-5 h.**

## E. Risques

| Risque | Mitigation |
|--------|------------|
| Coût compute leaderboard explose si > 50 users | V1 OK (mono-user effectif), monitorer ; si nécessaire cache 5 min |
| Radar mini illisible sur mobile (tooltip trop petit) | Sur mobile, le tooltip devient un panneau compact en dessous de la row plutôt qu'un overlay |
| User désactive son compte mais URL `/users/{username}` reste indexée | 404 si `is_active=False` — pas de redirection ni de note publique |
| Métadonnées `height_cm` non renseignées affichent un vide bizarre | Skip silencieusement la ligne |

## F. Acceptance criteria

| Critère | Statut |
|---------|--------|
| Mini radar SVG visible dans le tooltip leaderboard | À builder |
| Username cliquable vers `/users/{username}` | À builder |
| Page `/users/{username}` 200 pour user actif | À builder |
| Page 404 pour username inactif ou inexistant | À builder |
| Métadonnées exposées limitées à : username, grade, sessions 30j, radar 6 axes, height_cm, weight_kg | À builder |
| Aucune donnée par séance, par exercice ou note libre exposée | À garantir |
| Aucune migration, zéro JS | À garantir |
| 4-6 nouveaux tests | À builder |

## G. Recommandation build suivant

**Sb_19 build** dans la foulée de cette spec. Effort 4-5 h. Aucun bloqueur — tout est buildable depuis l'existant.

Ouvertures V2 explicitement différées :
- Opt-out granulaire visibilité profil.
- Filter leaderboard par squad.
- Avatar / bio user.
- Page `/users/{username}/history` (si jamais voulu — privacy trade-off à ré-arbitrer).
