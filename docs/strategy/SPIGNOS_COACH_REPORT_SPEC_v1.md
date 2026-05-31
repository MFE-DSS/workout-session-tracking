# SPIGNOS — Coach Report Spec v1 (Sx_23)

**Date :** 2026-05-09
**Type :** SPEC ONLY — nouvelle feature "Coach Report".
**Prérequis :** Sx_21 méta-spec, Sx_22b (Profile Synthesis v2) — partage de `profile_metrics`.
**Successeur build :** Sb_23.

---

## A. Pourquoi cette feature

Le user dogfooding réclame "*un rapport de profil orienté coach*" : un document que la personne peut **présenter à un coach externe** (ou se présenter à elle-même via un regard de coach) résumant l'état physique et performatif. Aujourd'hui, un coach qui voit le dashboard SPIGNOS doit naviguer dans 5 pages pour comprendre où en est l'utilisateur.

**Cible utilisateur :**
1. **User → coach humain (60 %)** — partage du rapport en début de séance avec un coach.
2. **User → soi-même (30 %)** — bilan mensuel pour ajuster son programme.
3. **User → expert ponctuel (10 %)** — médecin du sport, kiné, nutritionniste.

**Promesse de la feature :** *"Un coach peut comprendre où en est l'utilisateur en 2 minutes."*

## B. Périmètre fonctionnel V1

Une **page SSR** à l'URL `/coach-report` (vue privée pour l'user lui-même) + un **mode export imprimable** (CSS print).

PDF natif → V2 (cf §G).

## B.bis — Étiquetage obligatoire (verrouillé v1.1, contrat dur)

Chaque ligne/bloc du rapport porte **exactement un** des trois tags suivants, visible dans l'UI :

| Tag | Définition | Couleur / icône suggérée |
|---|---|---|
| **Mesuré** | Donnée saisie par l'user (taille, poids, FC, TA, set log) ou agrégat strict de telles données (sessions/30j, sets/sem). Aucune inférence. | ● vert |
| **Inféré** | Combinaison de données mesurées via une règle déterministe documentée (top zone, ratio strength/cardio, points forts/faibles "probables"). Toujours formulé au conditionnel. | ◐ orange |
| **Non déductible** | Champ que les données SPIGNOS **ne permettent pas** d'inférer (VO2max, masse maigre, qualité d'exécution biomécanique, état hormonal, nutrition). | ◯ gris + label `Données insuffisantes` |

**Interdits stricts v1.1 :**
- ❌ Aucune appréciation esthétique ("bel équilibre", "physique harmonieux", "silhouette équilibrée") — non scientifique, hors périmètre.
- ❌ Aucun pronostic morphologique ("vous prenez de la masse", "vous perdez du gras") — nécessite mesures DXA/impédancemétrie absentes.
- ❌ Aucun verdict performance maximale ("vous êtes fort en", "votre force est inférieure à la moyenne") — pas de 1RM mesuré ni de pop. de référence.
- ❌ Aucune référence comparative à d'autres utilisateurs ("vous êtes dans le top 20 %") — V3 si pertinent.

**Obligations strictes v1.1 :**
- Chaque bloc affiche son tag en en-tête (ex : "Bloc 4 — Zones musculaires `Inféré`").
- Chaque ligne dans un bloc peut sur-étiqueter (ex : Bloc 1 a taille = `Mesuré`, mais "trend poids 90j" = `Inféré`).
- Les blocs 7-9 (points forts/faibles/axes) sont **systématiquement** `Inféré`. Le mot "probable" est obligatoire dans le phrasé.
- Le bloc 10 (garde-fous) reste fixe et inclut explicitement les 4 interdits ci-dessus.

## C. Structure du rapport (1 page écran / 1-2 pages imprimées)

### Bloc 1 — Identité physique

| Champ | Source | Étiquette |
|---|---|---|
| Username | `users.username` | Mesuré |
| Date du rapport | `now()` | Mesuré |
| Taille | `users.height_cm` | Mesuré (si renseigné) |
| Poids actuel | `body_measurements.weight_kg` (dernier) **ou** `WorkoutSession.bodyweight_kg` (dernier, merge Sb_17) | Mesuré |
| Trend poids 90j | dérivé série | Inféré |
| Tour de taille | `users.waist_cm` | Mesuré |
| FC repos | `users.resting_hr` | Mesuré |
| Pression artérielle | `users.bp_systolic`/`bp_diastolic` | Mesuré |
| Âge approx | `users.year_of_birth` (à ajouter ?) | Mesuré |

**Affichage :** ligne dense `178 cm · 78,5 kg (−1,2 kg / 90j) · taille 82 cm · FC 58 · TA 122/76`.

### Bloc 2 — Volume et fréquence

| Métrique | Fenêtre | Source |
|---|---|---|
| Sessions / 30j | 30j | `sessions WHERE status=completed AND excluded_from_stats=false` |
| Sessions / 90j | 90j | idem |
| Streak actuel (jours consécutifs avec ≥ 1 session) | depuis dernière séance | dérivé |
| Min cardio / sem | 30j | `sessions WHERE kind=cardio` aggregate |
| Sets strength / sem | 30j | `set_logs WHERE kind=work AND completed` aggregate |

### Bloc 3 — Ratio strength / cardio

```
Strength : ████████░░  78 %
Cardio   : ██░░░░░░░░  22 %
```

Calculé sur **temps** (minutes session) ou **fréquence** (séances). V1 = sur fréquence (plus stable).

**Tag d'interprétation (`Inféré`) :**
- `> 80 %` strength → "Profil orienté hypertrophie/force"
- `40-80 %` mixte → "Équilibre strength/cardio"
- `< 40 %` strength → "Profil endurance dominante"

### Bloc 4 — Répartition par zone musculaire

Réutilisation du radar 30j (silhouette uniquement, sans score au centre) + ligne légende :

```
Top zones :       Pecs (8), Back-width (6), Shoulders (5)
Zones négligées : Lower (1), Arms (2)
```

Comptage = **séances visant la zone** (pas sets, trop bruité).

### Bloc 5 — Patterns moteurs dominants

(Dépend de `pattern_motor` à ajouter au catalogue — cf Sx_22a §C.2)

```
Push horizontal :  ████████  35 %
Pull horizontal :  ██████    25 %
Squat           :  ████      18 %
Hinge           :  ██        10 %
Isolation       :  ██         8 %
Cardio          :  █          4 %
```

Permet de détecter rapidement les déséquilibres push/pull et lower/upper.

### Bloc 6 — Discipline de logging

| Indicateur | Mesure |
|---|---|
| Taux de séances complétées (non-abandonnées) | % |
| Taux de séances avec note libre | % |
| Taux de séances avec bodyweight saisie | % |
| Taux de séances avec sensation musculaire | % |
| Score qualité moyen `quality_score` (Sx_06) | sur 100 |

Affichage : pastilles vert/orange/rouge :
- ≥ 80 % → vert
- 50-79 % → orange
- < 50 % → rouge

### Bloc 7 — Points forts probables (`Inféré`)

Inférence à partir de :
- Zone(s) la plus travaillée + score radar le plus haut.
- Pattern dominant cohérent (ex : push horizontal élevé + pecs élevé = "Pecs probables comme point fort").

Phrasé :
> *"Points forts probables : pecs et back-width (zones les plus travaillées + scores radar > 70)."*

Toujours formulé avec `probables` ou `hypothèse`. Jamais "vous avez X".

### Bloc 8 — Points faibles probables (`Inféré`)

Inverse du bloc 7 :
- Zone(s) la moins travaillée + score radar le plus bas.

Phrasé :
> *"Points faibles probables : lower body (< 2 séances/30j, score radar 18/100)."*

### Bloc 9 — Axes de travail suggérés (`Inféré`)

Génère 2-3 recommandations à partir des blocs 7-8 :

```
1. Rééquilibrer lower body : viser 2 séances Legs/sem sur 4 semaines.
2. Augmenter volume cardio : 90 min/sem actuellement, cible 150 min OMS.
3. Réduire fréquence push horizontal (35 % sets) : intégrer Pull B vertical.
```

V1 = règles déterministes simples, pas d'IA. Liste close de 10-15 règles candidates, on en retient 2-3.

### Bloc 10 — Garde-fous d'interprétation

Bloc fixe en bas, **toujours présent** :

> ⚠️ Ce rapport synthétise les données saisies par l'utilisateur. Il **ne remplace pas** un avis médical, kinésithérapique ou diététique. Les "points forts/faibles probables" sont des hypothèses basées sur le volume d'entraînement et non sur des mesures de performance maximale.

## D. Hiérarchie visuelle

Le rapport doit être lisible en 2 min. Hiérarchie :

1. **30 sec** : Bloc 1 (identité) + Bloc 2 (volume) + Bloc 3 (ratio) → on sait qui c'est et combien il/elle s'entraîne.
2. **60 sec** : Bloc 4 (zones) + Bloc 5 (patterns) → on voit les déséquilibres.
3. **30 sec** : Blocs 7-9 (points forts / faibles / axes) → on sait quoi proposer.

Bloc 6 (discipline) et Bloc 10 (garde-fous) lus à la marge.

## E. Format produit

| Format | V1 | V2 | V3 |
|---|---|---|---|
| Page SSR `/coach-report` | ✅ | ✅ | ✅ |
| Print CSS (`@media print`) | ✅ — A4 1-2 pages | ✅ | ✅ |
| Export PDF natif | ❌ | ✅ via `weasyprint` ou navigateur "Imprimer en PDF" | ✅ |
| Partage URL signée temporaire | ❌ | ❌ | ✅ (lien expirant 24h pour coach externe) |
| Export JSON pour API tierce | ❌ | ❌ | ✅ (option) |

V1 = SSR + print. Suffisant pour 95 % des cas (l'user imprime en PDF via navigateur).

## F. Implémentation technique

### F.1 — Services

- `services/coach_report.py` :
  - `build_report(user_id, ref_date=None) -> CoachReport` — orchestration.
  - Réutilise `services/profile_metrics.py` (Sx_22b), `muscle_scoring.py`, `quality_score.py`.

- `services/coach_inference.py` :
  - `strong_points(report) -> list[str]`
  - `weak_points(report) -> list[str]`
  - `suggested_axes(report) -> list[str]` (2-3 sorties parmi 10-15 règles déterministes)

### F.2 — Router

- `app/routers/coach_report.py` :
  - `GET /coach-report` — page SSR pour l'user courant.
  - `GET /coach-report.print` — version print-optimisée (toggle CSS via media query).

### F.3 — Templates

- `templates/coach_report.html` — vue principale.
- `templates/_partials/coach_report_block_*.html` — 10 partials (un par bloc).

### F.4 — Modèle de données

**Aucune nouvelle table BD.** Toutes les données existent déjà :
- `users` (identité, métadonnées)
- `body_measurements` + `workout_sessions.bodyweight_kg` (poids)
- `workout_sessions` (volume, dates)
- `set_logs` (volume strength)
- `template_exercises.pattern_motor` (si Sx_22a livré, sinon dérivation lexicale fallback)

**Possible ajout (V1.1) :**
- `users.year_of_birth INTEGER NULL` — pour Bloc 1 âge.
- `users.experience_level VARCHAR(16) NULL` — débutant/intermédiaire/avancé (optionnel, déclaratif).

### F.5 — Performance

- Build report = ~10 requêtes BD (agrégats 30j et 90j sur `set_logs` essentiellement).
- Cible : < 800 ms pour 200 sessions historiques.
- Cache léger 1h (TTL clé `coach_report:{user_id}:{date}`).

## G. Acceptance criteria Sx_23

| Critère | Mesure |
|---|---|
| Page `/coach-report` accessible authentifié | Test E2E |
| 10 blocs présents | Audit visuel |
| Tag `Mesuré` / `Inféré` / `Inféré` sur chaque bloc | Audit |
| Print A4 1-2 pages, lisible | Test impression |
| Garde-fou §C.10 toujours visible | Test |
| Rapport généré en < 800 ms | Mesure |
| Pas de fuite de données d'autres users | Test d'ownership |

## H. Risques d'interprétation abusive

| Risque | Mitigation |
|---|---|
| User prend "points faibles probables" comme diagnostic | Bloc 10 garde-fou + langage "probables" partout |
| Coach externe utilise le rapport sans contexte | Bloc 10 explicite + rappel "ce n'est pas un avis médical" |
| Métriques poids/IMC stigmatisantes | Pas d'IMC affiché V1 — juste poids brut. Pas de jugement valeur. |
| Recommandation cardio devient injonction | Phrasé "axes de travail suggérés" pas "vous devez" |
| User cache des données → rapport biaisé | Mention "Données saisies par l'utilisateur" en bloc 10 |

## I. Hors V1

- IA générative pour rédiger axes (V2 si pertinent).
- Comparaison vs population (médiane SPIGNOS, vs OMS, etc.) — V3.
- Calcul VO2max estimé — V3 (nécessite test sous-maximal protocolé).
- Tracking nutrition — out of scope.
- Lien direct vers coach humain depuis l'app — out of scope V1 (modèle business non défini).

## J. Lotissement build (Sb_23)

| Lot | Sujet | Effort |
|---|---|---|
| Sb_23.1 | `profile_metrics.py` étendu + tests | 3 h |
| Sb_23.2 | `coach_report.py` orchestration | 3 h |
| Sb_23.3 | `coach_inference.py` règles déterministes | 4 h |
| Sb_23.4 | Templates 10 blocs + CSS print | 5 h |
| Sb_23.5 | Tests E2E + ownership | 2 h |
| Sb_23.6 | Sprint report | 1 h |
| **Total** | | **18 h** |

## K. Sortie attendue

Une page `/coach-report` qu'un user peut afficher en salle de sport sur tablette et tendre à un coach. Le coach lit 2 min, comprend, propose. La page tient sur un format A4 si imprimée.
