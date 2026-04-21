# SPIGNOS Next-Session Recommendation Spec v1

**Sprint ID :** Sx_12_next_session_recommendation_spec
**Date :** 2026-04-21
**Statut :** SPEC ONLY — aucun code engagé par ce document
**Prérequis :** Session System V1 clos + Sb_11a livré + dogfooding léger OK
**Successeur :** Sb_12_next_session_recommendation_build (proposé §O)

---

## A. Statut du document

Spec produit et technique pour un **premier moteur déterministe** de recommandation de prochaine séance. Pas d'IA, pas de boîte noire, pas de refonte du launcher existant. Approche additive : la recommandation est un **signal** affiché au-dessus du sélecteur actuel, l'utilisateur reste libre de l'ignorer et de choisir manuellement.

## B. Contexte système actuel (V1 + Sb_11a)

L'audit Sx_10 + l'inspection préalable à cette spec confirment :

- Flow séance mature (Sb_05 à Sb_10, carte-par-carte, save-on-next/prev).
- Atlas machine V1 (29 machines, 8 familles) et substitution gérée.
- Dispatcher de scoring strength/cardio séparé (`quality_score.session_kind`).
- Review `/done` avec confidence score + anomalies + top progression + zones touchées.
- Timeline kind-aware + export v2.
- Pre-session briefing (Sb_11a) affichant chip + peek sur la carte active.
- Catalogue v12 équilibré.

Côté analytics préalables à la recommandation :

- `muscle_mapping.classify_exercise(name)` → `(primary_zone, secondary_zones)` sur 11 zones canoniques.
- `muscle_scoring._compute_tonnage_by_zone` agrège tonnage + hard_sets + session_count par zone sur une fenêtre (typiquement 30j), avec pondération 30% pour les zones secondaires.
- `behavioral.compute_behavioral_state` produit `fatigue_score`, `streak_days`, `sessions_30d`, `trend_7d_vs_7d`.
- `kpis.compute_template_kpis` donne par template : `count_completed`, `last_done_at`, `avg_success_score`.
- `readiness` quotidienne : `sleep_quality`, `fatigue_level`, `soreness_level`, `stress_level`, `motivation_level` (1–5 chacun, **global — pas par zone**).
- Launcher actuel (`app/services/launcher.py`) : arbre 3 niveaux figé (`type → variant → template`), aucune logique de recommandation contextuelle.

Le cockpit SPIGNOS a donc **la donnée, pas l'agrégation cible** ni **l'exposition produit**.

## C. Problème produit

> L'utilisateur qui veut démarrer une séance aujourd'hui n'a aucun signal pour décider laquelle choisir. Le launcher actuel est un menu — il ne **suggère rien**, n'explique rien.

Cas d'usage réels, observés ou légitimement inférables :

1. **Deux Push consécutifs** — l'utilisateur prend Push B le lendemain d'un Push A, sans s'apercevoir que pecs/triceps n'ont pas récupéré. Pas de frein produit.
2. **Pull A oublié** — la largeur de dos n'a pas été travaillée depuis 10 jours, le launcher ne le signale pas.
3. **Cardio absent** — l'utilisateur a fait 5 séances strength en 7 jours, aucune séance LISS sur 30 jours, rien ne lui rappelle.
4. **Démarrage à froid** — nouvel utilisateur arrive, le launcher montre 16 templates en arborescence sans aucune aide sur où commencer.
5. **Catch-up non activé** — le template `catch-up-back-width` existe précisément parce que la largeur est souvent sous-travaillée, mais aucun signal produit ne déclenche son usage au bon moment.

**Symptôme commun :** la connaissance de ce qu'il faudrait faire vit dans la tête de l'utilisateur, pas dans le système. Le système a la donnée pour le savoir mieux que lui, mais ne l'expose pas.

## D. Objectifs

**Objectif produit :** poser dans le cockpit une **suggestion claire, explicable et non-bloquante** de la prochaine séance à faire, accompagnée d'une **phrase de justification en une ligne**, et de **2 alternatives** consultables.

**Objectifs techniques :**

- Moteur **100% déterministe**, testable en unitaire avec des fixtures simples.
- **Zéro IA**, zéro modèle probabiliste, zéro dépendance externe.
- **Zéro migration DB**. Tout se calcule depuis les tables existantes.
- Une **seule phrase d'explication**, composée de slots documentés (§J).
- SSR-first, **zéro JS**.
- Budget perf : ≤ 1 requête SQL supplémentaire par page `/` ou `/launcher` (les données les plus coûteuses — set_logs — sont déjà hydratées pour le dashboard home).
- Pas de nouvelle route. La recommandation s'injecte dans `/` et `/launcher`.

## E. Signaux disponibles dans le système

### E.1 Déjà calculés ou calculables trivialement

| Signal | Source | Cardinalité | Utilisé aujourd'hui par |
|--------|--------|-------------|-------------------------|
| Zone primaire + secondaires par nom d'exercice | `muscle_mapping.classify_exercise` | 11 zones | `muscle_scoring`, `catalog_qa` |
| Tonnage par zone sur fenêtre | `muscle_scoring._compute_tonnage_by_zone` | 11 zones × période | Dashboard radar |
| Hard sets par zone sur fenêtre | idem | 11 zones × période | Dashboard radar |
| Nombre de sessions sur 7j / 14j / 30j | `behavioral.compute_behavioral_state` | scalaire | Home, profile |
| Dernière occurrence d'un template | `kpis.compute_template_kpis` | par template | `/library` |
| Dernière occurrence d'un exercice | `stats.last_time_by_exercise_code` | par code exo | Carte active (delta, last-time chip/peek) |
| Fatigue subjective récente | `behavioral.compute_behavioral_state` → `fatigue_score` | 0–100 | Home, profile |
| Readiness quotidienne | `app/models/readiness.py` | sleep/fatigue/soreness/stress/motivation 1–5 | `/readiness` |
| Session kind (strength/cardio) | `quality_score.session_kind` | 2 valeurs | Scoring, timeline |
| Quality score de séance | `quality_score.compute_session_quality` | 0–100 | Timeline, leaderboard |
| Catalog section du template | `WorkoutTemplate.catalog_section` | core/utility/specialization/archived | `/library` grouping |

### E.2 À calculer (ajouts ciblés)

| Signal manquant | Dérivation proposée | Coût |
|-----------------|---------------------|------|
| **staleness par zone** (0 = fraîche/sursollicitée, 1 = stale/prête) | décroissance exponentielle du nombre de hard sets par zone sur 7j | pur Python sur la sortie de `muscle_scoring` élargie à 7j |
| **map template → zones primaires** | pré-calculée une fois via `classify_exercise` sur les exercices du template, cache applicatif | reseed-dépendant, calcul < 10ms |
| **session_kind_last_k** | dernières K sessions : liste de kinds ordonnée | 1 query (déjà dans pattern behavioral) |
| **time_since_last_kind** | delta jours depuis la dernière `strength` et la dernière `cardio` | dérivé de la même query |

### E.3 Explicitement NON utilisés en V1

- Readiness quotidienne **non consommée** en V1 : signal bruité, 1 réponse quotidienne vs décisions multi-journalières, risque d'incohérence. Envisageable V2.
- Weekday / heure de la journée : pas de storage structurel (Sx_02 garde `weekday_iso` dérivé du timestamp). Pas assez de volume pour un pattern robuste.
- Soreness par zone : **n'existe pas** dans le modèle actuel, créer ce signal obligerait une migration. Rejeté V1.
- `global_state` / `concentration` par session : déjà dans `fatigue_score`, ne pas les recomposer.
- `success_score` de la dernière séance : ne pilote pas le choix du prochain type — c'est un signal de performance, pas de récupération.

## F. Hypothèses produit de recommandation

Hypothèses acceptées comme vraies pour V1 :

1. **La récupération musculaire est dominante** sur 48–96h pour les groupes lourdement sollicités. Donc éviter de resolliciter une zone sursollicitée < 48h est une heuristique de sécurité raisonnable.
2. **L'alternance push/pull/legs est la structure de programme par défaut** du catalogue SPIGNOS. Proposer la suite logique du pattern est rarement faux.
3. **Un utilisateur cardio-absent sur 7+ jours profite d'une suggestion LISS.** Pas de nuance : c'est une bonne nudge produit.
4. **Un cold-start (< 3 séances complétées) doit tomber sur un template de départ prédictible**, pas sur un catch-up ou une specialization.
5. **Une séance spécialisée ne doit être suggérée que si la zone ciblée est manifestement stale.** Exemple : `catch-up-back-width` suggéré seulement si `lats + upper_back` ont un ratio hard_sets / session beaucoup plus bas que les autres zones sur 14j.
6. **La fatigue globale plafonne l'intensité recommandée.** Si `fatigue_score > 70`, le moteur dégrade sa suggestion vers un `short-*` ou un LISS, même si la rotation pointait vers un compound lourd.

## G. Plusieurs modèles possibles de recommandation

Trois variantes évaluées. Toutes déterministes.

### Modèle G1 — Chronologie stricte du programme

Rotation fixe `Push A → Pull A → Legs A → Push B → Pull B → Legs B → LISS`, itérée sur la position de la dernière séance dans ce cycle.

- **Pour :** trivial à implémenter, 100 % prédictible.
- **Contre :** ignore les signaux (irrégularité, substitutions, skipping). Si l'utilisateur saute une semaine, la rotation propose quand même la suite mécanique.

**Rejeté V1.** Trop naïf pour justifier un chantier — autant garder le launcher actuel.

### Modèle G2 — Scoring multi-critères sur templates candidats

Chaque template éligible reçoit un **score 0–100** calculé comme somme pondérée de 4 composants :

1. **+40 points × staleness moyenne des zones ciblées** (0 si zones fraîchement sursollicitées, 1 si largement au-dessus de 96h sans stimulation).
2. **+20 points × alternation_bonus** (si le kind complète la récente séquence : ex. 2 strength de suite → +20 pour cardio).
3. **−15 points × redundancy_penalty** (si une zone primaire du template a été lourdement sollicitée dans les dernières 48h).
4. **+15 points × catalog_affinity** (core = +15, utility = +10, specialization = +0 base, bonus +15 si la spec cible une zone stale extrême).

Top-1 présenté avec la phrase d'explication, top-2 et top-3 en alternatives.

- **Pour :** lisible, testable, cap par composant documenté.
- **Contre :** les pondérations sont a priori. Si mal calibrées, les suggestions paraîtront arbitraires.

**Retenu V1.**

### Modèle G3 — Contexte + filtre

Trois filtres successifs :
- Filtre A : si `fatigue_score > 70` ou `global_state == "fatigued"` sur la dernière, ne proposer que `short-*` ou LISS.
- Filtre B : exclure les templates dont les zones primaires ont été travaillées < 48h.
- Filtre C : parmi les restants, picker par ordre de staleness décroissante.

- **Pour :** pas de pondération, logique de règles pures.
- **Contre :** risque de renvoyer **aucun** candidat si filtres conjoints sont trop stricts. Moins flexible que G2 pour donner 2 alternatives justifiées.

**Rejeté V1** (mais les filtres A et B sont intégrés à G2 comme règles de sécurité).

## H. Arbitrage recommandé

**Modèle G2 retenu**, avec **garde-fous G3** (filtres A et B appliqués avant le scoring).

### H.1 Algorithme en 4 étapes

1. **Collecte** : récupérer les 5 dernières sessions complétées + `muscle_scoring` sur 7j + `behavioral.compute_behavioral_state`.
2. **Derive** : calculer `staleness_by_zone`, `last_kind_sequence`, `time_since_last_kind`, `fatigue_global`.
3. **Filter** : exclure du pool initial :
   - tous les templates `archived`
   - si `fatigue_global > 70` → garder uniquement `short-*` + `liss-*`
   - tout template dont la zone primaire a > seuil de hard sets dans les 48h
4. **Score + rank** : appliquer G2 aux templates restants, retourner top-1 + top-2 + top-3 avec leurs phrases d'explication respectives.

### H.2 Paramètres numériques V1 (calibrables)

| Paramètre | Valeur V1 | Justification |
|-----------|-----------|---------------|
| Fenêtre staleness | 7 jours | Cohérent avec la structure hebdo des programmes core |
| Seuil fatigue dégradé | `fatigue_score > 70` | `behavioral` rend déjà 0–100 ; 70 = « franchement fatigué » |
| Fenêtre redundancy | 48 heures | 2 jours = plancher classique de récupération locale |
| Seuil hard sets redundancy | > 8 sets sur la zone primaire dans la fenêtre redundancy | calibrable, peut être affiné après dogfooding |
| Seuil cardio stale → bonus LISS | 0 séance cardio sur 7j | simple binaire |
| Seuil spécialisation → valide | zone cible du template `catch-*` avec ratio hard_sets zone / median des autres zones < 0.5 sur 14j | déclenche l'inclusion d'une specialization dans le pool scoré |
| Cold start | < 3 séances complétées lifetime | retomber sur `display_order` catalogue core |

### H.3 Pseudocode du scoring par template

```
score = 0
primary_zones = template_primary_zones(template)  # via classify_exercise cache
staleness = mean(staleness_by_zone[z] for z in primary_zones)
score += 40 * staleness

# Alternation
if kind_last_sequence == ["strength", "strength"] and template.kind == "cardio":
    score += 20
elif kind_last_sequence[-1] == "cardio" and template.kind == "strength":
    score += 10

# Redundancy penalty (déjà filtré avant mais fait office de tie-break)
recent_hard_sets = max(hard_sets_by_zone_48h[z] for z in primary_zones)
if recent_hard_sets > 4:
    score -= 5 * (recent_hard_sets / 4)

# Catalog affinity
if template.catalog_section == "core":
    score += 15
elif template.catalog_section == "utility":
    score += 10
elif template.catalog_section == "specialization":
    if is_specialization_justified(template, staleness_by_zone):
        score += 20  # inclut une spec seulement si très justifiée
    else:
        score = -1   # l'exclut du top

return clamp(score, 0, 100)
```

### H.4 Garantie « jamais zéro candidat »

Si après le filtre (H.1 étape 3) la liste est vide, fallback déterministe :
- cold start → premier template core par `display_order`.
- autre → `liss-only` (toujours valide).

## I. UX recommandée

### I.1 Surface principale — Home (`/`)

Nouveau bloc **« Prochaine séance suggérée »** placé **au-dessus** des KPIs / sparkline / CTA séance actuelle. Visible uniquement si **aucune séance n'est en cours** (`open_session is None`).

```
╔═══════════════════════════════════════════════════════════════╗
║ ✦ Prochaine séance suggérée                                   ║
║                                                                ║
║   Pull A — Dos largeur + Delts postérieurs                    ║
║   Dernière Push il y a 2 j, jambes reposées, largeur du dos   ║
║   pas travaillée depuis 6 j.                                  ║
║                                                                ║
║   [Démarrer Pull A →]   [Voir 2 alternatives]                 ║
╚═══════════════════════════════════════════════════════════════╝
```

- **Titre prominent** : nom du template + focus dérivé.
- **Une seule phrase** d'explication (§J).
- **CTA principal** lance directement la séance (POST `/sessions` avec le slug suggéré).
- **CTA secondaire** ouvre un `<details>` déroulant avec les 2 alternatives et leurs phrases courtes respectives.

### I.2 Surface secondaire — Launcher (`/launcher`)

Même bloc injecté **au-dessus** du 3-step picker existant. Le picker reste disponible sans modification. L'utilisateur peut l'ignorer et choisir manuellement.

### I.3 Comportement `<details>` alternatives

```
<details class="reco-alternatives">
  <summary>Voir 2 alternatives</summary>
  <ul>
    <li>
      <a href="/sessions?preselect=liss-abs">LISS + abs</a>
      <small>Pas de cardio depuis 9 j.</small>
    </li>
    <li>
      <a href="/sessions?preselect=legs-b">Legs B</a>
      <small>Chaîne postérieure relativement stale.</small>
    </li>
  </ul>
</details>
```

### I.4 Règles UX « anti-magie »

- Pas de badge « IA », pas d'icône cerveau, pas de vocabulaire prédictif.
- Pas d'auto-démarrage — toujours un clic explicite.
- Pas de recommandation **négative** (« ne faites pas X ») — uniquement positive.
- Phrase d'explication **toujours affichée** avec la suggestion. Si pas de phrase, pas de suggestion.
- Si cold start, wording dédié : « Bon premier template pour démarrer : Push A. »

## J. Explicabilité — phrase de justification

### J.1 Structure en slots

Chaque recommandation produit une `phrase` de **1–2 clauses**, max 140 caractères. Structure :

```
{signal_primaire} → {pourquoi_ce_template}
```

### J.2 Slots types

| Slot `signal_primaire` | Déclenché quand | Exemple wording |
|------------------------|-----------------|-----------------|
| `push_recent` | dernière séance a une zone primaire pecs/shoulders/triceps < 48h | « Dernière push il y a {N} j » |
| `pull_recent` | idem avec lats/upper_back/biceps | « Dernière pull il y a {N} j » |
| `legs_recent` | idem avec quads/posterior/calves | « Dernières jambes il y a {N} j » |
| `no_cardio_recent` | aucune cardio sur 7j | « Pas de cardio depuis {N} j » |
| `fatigue_high` | fatigue_score > 70 | « Charge récente élevée » |
| `cold_start` | < 3 séances lifetime | « Bon premier template pour démarrer » |
| `zone_stale` | une zone spécifique clairement stale | « {Zone} pas travaillée depuis {N} j » |
| `rotation_cycle` | alternance simple cohérente avec le pattern | « Suite naturelle après {dernier_focus} » |

| Slot `pourquoi_ce_template` | Exemple wording |
|-----------------------------|-----------------|
| Template cible une zone stale | « {Focus} recommandé » |
| Template complète l'alternance kind | « LISS suggéré pour équilibrer » |
| Fallback cold start | — (slot vide, déjà porté par `signal_primaire`) |
| Catch-up justifié | « Largeur du dos sous-travaillée depuis 2 semaines » |

### J.3 Exemples de rendus complets

1. « Dernière push il y a 2 j, jambes reposées → Legs A recommandé. »
2. « Pas de cardio depuis 9 j → LISS suggéré pour équilibrer. »
3. « Charge récente élevée → séance courte recommandée. »
4. « Bon premier template pour démarrer : Push A. »
5. « Largeur du dos sous-travaillée depuis 12 j → catch-up-back-width recommandé. »

### J.4 Garde-fous éditoriaux

- Pas de superlatifs (« parfait », « idéal »).
- Pas de conditionnel (« devrait », « pourrait »).
- Ton neutre et factuel.
- Chiffres arrondis au jour.

## K. Cas particuliers

| Cas | Traitement V1 |
|-----|---------------|
| **Utilisateur lifetime = 0 séance** | Aucune suggestion personnalisée → afficher « Bon premier template pour démarrer : Push A. » |
| **< 3 séances lifetime** | Cold start — utiliser `display_order` core, ignorer les signaux (données insuffisantes) |
| **Séances irrégulières (gap > 14j)** | Si le gap dépasse 14j, traiter comme un re-démarrage soft : tomber sur `short-*` ou `liss-*` au lieu d'un compound lourd |
| **Pas de cardio sur 30j+** | Force-boost LISS dans le top-3 même s'il n'atteint pas le top-1 par scoring |
| **Programme spécialisé actif** | Aucun champ "user programme" n'existe V1. La notion de programme n'est pas structurelle. Pas de traitement spécifique — la logique générique s'applique |
| **Conflit rotation vs récupération** | La récupération gagne toujours. Le filtre redundancy (H.1 étape 3) exclut explicitement les templates qui cassent la récup |
| **Utilisateur ignore la reco 3 fois de suite** | Pas de signal pour le détecter V1 (pas de tracking UI). Si l'utilisateur choisit manuellement, le moteur s'adapte au tour suivant via l'historique. Pas de logique d'« apprentissage » explicite |
| **Catalogue custom futur (Sx_11b)** | La recommandation doit opérer sur `WorkoutTemplate` peu importe sa source. Si un jour un `UserTemplate` existe, tant qu'il a un `kind` + des exercices classifiables, il rentre dans le pool. Point de contact documenté mais pas implémenté V1 |
| **Template ayant des exos non classifiables** | Fallback : zone primaire = `unknown`. Le scoring le dégrade naturellement (staleness 0) → ne sera pas top-1 sauf si tout le reste est filtré |
| **Tie entre 2 templates** | Départagés par (1) `display_order` du catalog_section, (2) `last_done_at` (plus ancien d'abord) |

## L. Impacts techniques

### L.1 Nouveau service

`app/services/recommendation.py` — fonctions pures :

```python
def build_staleness_by_zone(session, user_id, now) -> dict[str, float]:
    """Retourne staleness 0..1 par zone sur fenêtre 7j."""

def build_template_zones_map(templates) -> dict[str, list[str]]:
    """Pré-calcule {template_slug: [primary_zones]} depuis classify_exercise."""

def score_template(template, signals) -> tuple[int, str]:
    """Retourne (score_0_100, phrase_explication)."""

def recommend_next_session(db, user_id, now) -> dict | None:
    """Point d'entrée principal. Retourne
    {top: {template, score, phrase}, alternatives: [...]} ou None."""
```

### L.2 Nouveau helper muscle_scoring (fenêtre 7j)

Actuel : `_compute_tonnage_by_zone` sur 30j par défaut.
Ajout : signature acceptant une fenêtre en jours. Pas de nouvelle logique.

### L.3 Cache applicatif de la map template → zones

La map est invariante tant que `reference_split.json` ne change pas. Calcul une fois au démarrage ou via un module-level lru_cache sur le slug.

### L.4 Routeurs touchés

- `app/routers/pages.py::home` — appel `recommend_next_session` quand `open_session is None`, passage du dict au template.
- `app/routers/pages.py::launcher` — même injection au-dessus du picker actuel.

### L.5 Templates touchés

- `app/templates/index.html` — nouveau bloc en haut.
- `app/templates/launcher.html` — même bloc en haut.
- Partial commun recommandé : `app/templates/_partials/next_session_reco.html`.

### L.6 CSS

Nouveau bloc BEM `.reco-next*` — réutilise la palette existante (pas de couleur nouvelle). Visuellement : card neutre avec accent subtil, pas un cartouche criard.

### L.7 Tests

- `tests/test_recommendation_service.py` — fixtures de sessions historiques contrôlées :
  - cold start → Push A / phrase cold-start
  - 2 pushs consécutifs → Pull ou Legs en top-1
  - pas de cardio 9j → LISS dans top-3
  - fatigue_score fabriqué > 70 → short-* ou LISS en top-1
  - zone largeur stale → catch-up-back-width dans top-3
  - tie-break → le plus ancien gagne
  - jamais zéro candidat (fallback toujours présent)

- `tests/test_recommendation_surface.py` — intégration :
  - home affiche bloc reco si `open_session is None`
  - bloc masqué si session en cours
  - alternatives dans `<details>` replié par défaut
  - CTA démarre la session attendue

### L.8 Migrations

**Aucune.** Tout se calcule.

### L.9 Impact perf

- Home charge déjà 14j de sessions pour le sparkline (hydraté avec set_logs). La query recommandation ajoute au maximum 1 query session supplémentaire (les 5 dernières) si la fenêtre 7j n'est pas couverte par la sparkline 14j — la plupart du temps zéro query additionnelle (réutilisation).
- Calcul de score : O(N_templates × N_zones × 1) ≈ constant pour 16 templates × 11 zones. Négligeable.

## M. Risques

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|-----------|
| Calibrage V1 mal ajusté → reco perçue arbitraire | Élevée | Moyen | Paramètres numériques centralisés en haut du service (constantes nommées) pour ajustement rapide post-dogfooding |
| Phrase d'explication trop longue ou répétitive | Moyen | Faible | Hard cap 140 chars ; tests snapshot sur 5 scénarios types |
| Sur-sollicitation d'une zone restée invisible au moteur | Moyen | Moyen | Le filtre redundancy empêche ce cas ; si vraiment pas de couverture, fallback LISS |
| Utilisateur veut ignorer la reco → friction CTA | Faible | Faible | Le picker actuel reste accessible, la reco n'est **jamais** le seul CTA |
| Cold start ambigu si 1–2 sessions | Moyen | Faible | Seuil fixé à 3 ; documenté |
| Fatigue_score passe au-dessus de 70 à cause d'une seule mauvaise séance → reco dégrade toujours | Moyen | Moyen | `fatigue_score` utilise déjà un moyen pondéré sur 3 sessions ; acceptable comme heuristique V1 |
| Specialization templates toujours exclus | Faible | Moyen | Condition explicite d'inclusion (ratio < 0.5 sur 14j) documentée et testée |
| Dépendance à la qualité de `classify_exercise` | Moyen | Moyen | Déjà testé via `catalog_qa` (100% classifiables). Si un exo devient `unknown`, `catalog_qa` le signalera en CI |
| Reco change chaque heure (utilisateur rassuré peu) | Faible | Faible | La donnée évolue seulement à la fin d'une nouvelle session. Stabilité naturelle |

## N. Acceptance criteria Sx_12

| Critère | Statut |
|---------|--------|
| Contexte repo audité avec briques existantes (§B, §E) | ✓ |
| Problème produit articulé avec 5 cas d'usage (§C) | ✓ |
| 3 modèles G1/G2/G3 comparés (§G) | ✓ |
| Arbitrage G2 + garde-fous G3 retenu et justifié (§H) | ✓ |
| Paramètres numériques V1 explicites et calibrables (§H.2) | ✓ |
| UX définie avec wireframe ASCII (§I) | ✓ |
| Phrase d'explication modélisée en slots (§J) | ✓ |
| 10 cas particuliers traités (§K) | ✓ |
| Impacts techniques cadrés — 1 service, 0 migration, 0 route (§L) | ✓ |
| Risques listés et mitigés (§M) | ✓ |
| Tests prévus (unit + intégration) documentés (§L.7) | ✓ |
| Zéro IA, zéro boîte noire, SSR-first, mobile-first | ✓ |
| Pas de fuite vers programme-builder | ✓ |

## O. Recommandation du build suivant

### Sb_12 — Next-Session Recommendation build

**Objectif :** implémenter §L intégralement. Scope strict G2 + garde-fous G3, pas de réglage fin.

**Périmètre proposé :**
- **New** : `app/services/recommendation.py` (~250 lignes, 4 fonctions publiques + helpers).
- **Modify** : `app/services/muscle_scoring.py` — signature window en jours (paramétrable, backward-compatible).
- **Modify** : `app/routers/pages.py` — injection dans `home` + `launcher`.
- **New** : `app/templates/_partials/next_session_reco.html` — partial commun.
- **Modify** : `app/templates/index.html`, `app/templates/launcher.html` — inclusion du partial.
- **Modify** : `app/static/css/app.css` — `.reco-next*` BEM (~30 lignes).
- **New** : `tests/test_recommendation_service.py` (~10 tests).
- **New** : `tests/test_recommendation_surface.py` (~5 tests).
- **New** : `docs/SPRINT_Sb_12_next_session_recommendation_BUILD_REPORT.md`.

**Hors scope explicite :**
- Pas d'historique personnalisé des recommandations refusées.
- Pas d'apprentissage.
- Pas d'intégration readiness quotidienne (reportée V2).
- Pas de UI pour modifier les paramètres.

**Effort estimé :** 8–12h (service 3h, router 1h, templates + CSS 2h, tests 3h, report 1h, polish 1–2h).

**Critères d'acceptation Sb_12 :**
1. `recommend_next_session(db, user_id, now)` retourne `None` pour session en cours, sinon un dict avec top + alternatives.
2. Phrase d'explication ≤ 140 chars, non vide, non générique.
3. Home + Launcher affichent le bloc quand reco disponible.
4. 3 scénarios snapshots testés : cold start, 2 pushs consécutifs, absence cardio.
5. Full suite verte (attendu : 666 → ≈ 680+ avec les ~15 tests reco).
6. Dogfooding visuel validé 375px + desktop avant merge du build.

---

## Annexe — Terminologie stricte (spec)

| Terme | Sens |
|-------|------|
| **staleness** | Score 0–1 par zone musculaire, 0 = zone récemment saturée, 1 = zone longtemps sans stimulus. Fenêtre V1 = 7 jours. |
| **redundancy_penalty** | Pénalité appliquée à un template dont la zone primaire a été sur-sollicitée dans les 48h |
| **alternation_bonus** | Bonus si le `kind` du candidat complète la séquence récente (ex. cardio après 2 strength) |
| **cold start** | Utilisateur avec < 3 séances complétées lifetime, traitement par défaut dédié |
| **phrase d'explication** | Chaîne 1–2 clauses, max 140 chars, composée de slots, accompagnant chaque recommandation |
| **template candidat** | `WorkoutTemplate` non archivé, non filtré par la phase G3 |
| **top-1 / alternatives** | Résultat du moteur : 1 suggestion principale + 2 alternatives consultables |
| **fallback** | Réponse garantie si le pool de candidats filtrés est vide (cold start → Push A, sinon → LISS) |
