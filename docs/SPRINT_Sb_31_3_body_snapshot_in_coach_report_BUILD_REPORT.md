# Sb_31.3 — Body Intelligence Snapshot dans /coach-report (Build Report)

**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`
**Date :** 2026-06-28
**Spec parent :** `docs/strategy/SPIGNOS_BODY_INTELLIGENCE_V2_SPEC.md`
**Lot Sx_31 :** §N.2 — Sb_31.3 (snapshot dans coach-report, 3/5 du cycle)
**Build authorization :** ✅ `BUILD AUTHORIZED FOR Sx_31` (override #4)
**Pré-requis :** Sb_31.1 ✅ + Sb_31.2 ✅ (CI 28317125588).

---

## 1. Résumé exécutif

Bloc « Snapshot Body Intelligence » ajouté dans `/coach-report` via la pipeline canonique Sx_31. Le router orchestre uniquement `build_body_intelligence_input → compute_body_intelligence → contexte template`. Le partial affiche un résumé compact (headline + ≤3 bullets + ≤3 priorités + lien vers `/body/intelligence`). Aucun seuil dupliqué hors composer, aucune logique métier dans le router ou le template, aucun service métier core muté, aucune migration, aucun JS, aucune API JSON.

`app/services/coach_report.py` n'est **pas** modifié — test garde structurel explicite.

## 2. Fichiers créés / modifiés

| Fichier | Type | Description |
|---|---|---|
| `app/routers/coach_report.py` | MODIFIED | +3 imports (composer + I/O layer) + +4 lignes : construction `body_snapshot` via pipeline canonique + injection contexte. Aucune autre mutation. |
| `app/templates/_partials/coach_body_snapshot.html` | **NEW** | 67 lignes. Partial compact qui lit uniquement `body_snapshot.{status, headline, bullets, priorities, engine_version}`. Réutilise classes existantes (`coach-block`, `coach-tag`, `text-dim`, `link`). |
| `app/templates/coach_report.html` | MODIFIED | +6 lignes : commentaire `1bis. Sb_31.3` + `{% include "_partials/coach_body_snapshot.html" %}` inséré entre la section 1 (Identité) et la section 2 (Volume). |
| `tests/test_coach_report_body_snapshot.py` | **NEW** | 23 tests : structure (4) + smoke route (2) + HTML rendu (7) + wording (1) + garde-fous structurels (5) + non-régression (4). |
| `docs/SPRINT_Sb_31_3_body_snapshot_in_coach_report_BUILD_REPORT.md` | **NEW** | Ce rapport. |
| `docs/strategy/SPEC_REGISTRY.md` | MODIFIED | Sb_31.3 livré ✅. |

### Non touché (vérification explicite)

- `app/services/coach_report.py` — **strictement intact** (test garde dédié)
- `app/services/body_intelligence.py` (Sb_31.1, composer pur)
- `app/services/body_intelligence_inputs.py` (Sb_31.2)
- `app/services/coach_inference.py` / `profile_metrics.py` / `muscle_scoring.py` / `quality_score.py` / `implicit_signal.py` / `confidence.py` / `radar.py` / `overload_*` / `substitution.py` / `recommendation.py` / `body_tracking.py`
- `app/models/*` / `migrations/*`
- `app/routers/body.py` / `app/routers/body_intelligence.py` (Sb_31.2 intact)
- `app/templates/body_intelligence.html` + partials Sb_31.2 (inchangés)
- `app/static/css/body_intelligence.css` (Sb_31.2, inchangée)
- `app/static/js/*` — aucun nouveau JS

## 3. Emplacement du bloc dans /coach-report

```
1. Identité physique          [Mesuré]
1bis. Snapshot Body Intelligence  ←── Sb_31.3 inséré ici
2. Volume et fréquence        [Mesuré]
3. Ratio strength / cardio    [Mesuré]
4. Répartition par zone musculaire
5. Patterns moteurs dominants
6. Discipline de logging
6bis. Signaux implicites 30j
7. Points forts probables
8. Points faibles probables
9. Axes de travail suggérés
```

Position justifiée :
- **après l'identité** : le snapshot consomme les mêmes data familières (taille/poids/IMC implicite dans l'engine), donc s'enchaîne naturellement après Section 1.
- **avant les analyses détaillées** : le snapshot offre la vue synthèse globale ; les sections 2-9 entrent dans le détail. Le bloc joue le rôle de "résumé exécutif body" pour le coach lecteur.
- **format d'impression préservé** : utilise les mêmes classes `coach-block` que les autres sections → s'imprime de la même façon, aucun risque sur `window.print()`.

## 4. Données affichées

Strictement depuis `BodyIntelligenceSnapshot` :

| Champ snapshot | Rendu UI |
|---|---|
| `status` | Badge `coach-tag` ("Sur les séances loggées" / "Partiel" / "Données partielles") + classe modifier `body-snapshot--{status}` + `data-body-snapshot-status` |
| `headline` | `<p class="coach-block__line body-snapshot__headline">` |
| `bullets[:3]` | `<ul>` avec cap 3 explicite (`body_snapshot.bullets[:3]`) |
| `priorities[:3]` | `<ul>` avec cap 3 + classes severity et priority key + `data-priority-key` |
| `engine_version` | Footer discret "Moteur Body Intelligence v{N}" |
| `limits` (si `insufficient_data`) | Note brève "À confirmer avec plus de séances." |

**Aucun accès direct** dans le template à : `sessions`, `body_measurements`, `quality_score`, `confidence_score`, `implicit_labels`.

**Lien** : `<a href="{{ url_for('body_intelligence') }}">Voir le détail →</a>` (route nommée Sb_31.2).

## 5. UX / wording

| Autorisé (utilisé dans le partial) | Statut |
|---|---|
| « Snapshot Body Intelligence » | ✅ titre |
| « Sur les séances loggées » | ✅ badge status `ok` |
| « Données partielles » | ✅ badge status `insufficient_data` |
| « Partiel » | ✅ badge status `partial_data` |
| « À confirmer avec plus de séances » | ✅ note si `insufficient_data` |
| « Voir le détail » | ✅ CTA lien |

| Interdit (scanné par test) | Statut |
|---|---|
| « ton physique est » / « tu es gras/sec » / « ton taux de gras » | ✅ absent |
| « diagnostic » / « problème médical » | ✅ absent |
| « posture réelle » / « symétrie corporelle réelle » | ✅ absent |
| « tu dois absolument » / « il faut absolument » / « obligatoire » | ✅ absent |

## 6. Statut des tests

| Suite | Tests | Résultat |
|---|---|---|
| `tests/test_coach_report_body_snapshot.py` (Sb_31.3) | 23 | ✅ |
| `tests/test_body_intelligence.py` (Sb_31.1) | 38 | ✅ non régressé |
| `tests/test_body_intelligence_inputs.py` (Sb_31.2) | 11 | ✅ non régressé |
| `tests/test_body_intelligence_route.py` (Sb_31.2) | 19 | ✅ non régressé |
| **Sous-suite Sx_31** | **91** | ✅ |
| Suite complète | ⏳ background run | (CI confirmera) |
| Ruff | ✅ 529 ≤ 548 (inchangé) |
| Spec protocol | ✅ |
| Alembic drift | ✅ no diff (aucune migration) |

### Garde-fous structurels Sb_31.3 (extraits)

- `test_coach_report_service_unchanged_no_body_imports` — `coach_report.py` ne mentionne pas `body_intelligence`
- `test_composer_unchanged` — sentinelle `BODY_INTELLIGENCE_VERSION = 1` toujours dans le composer
- `test_inputs_layer_unchanged_by_sb_31_3` — signature publique du builder préservée
- `test_partial_does_not_reference_engine_constants` — 8 tokens interdits scannés dans le partial
- `test_rendered_html_caps_bullets_at_3` + `test_rendered_html_caps_priorities_at_3` — cap explicite
- `test_no_json_api_for_coach_body_snapshot` — `/coach-report.json` et `/coach-report/body-snapshot.json` → 404/405
- `test_body_intelligence_route_still_200` — non-régression Sb_31.2

## 7. Limites produit (rappel)

- Le snapshot dans `/coach-report` est volontairement **compact** et différent de `/body/intelligence`.
- Bullets et priorités sont strictement cap 3 (composer impose `MAX_PRIORITIES=3` ; template applique `[:3]` défensif sur bullets).
- Si `insufficient_data` → message explicite "À confirmer avec plus de séances", aucun verdict.
- Aucune classification Mesuré/Dérivé/Inféré rendue ici (déjà couverte par `/body/intelligence`) — sauf le badge de niveau du bloc ("Sur les séances loggées" = Mesuré ; "Partiel" = Inféré).
- Aucun rendu des 7 blocs ; pour le détail, l'utilisateur clique "Voir le détail" → `/body/intelligence`.

## 8. Contraintes respectées (verbatim user)

| Contrainte | OK |
|---|---|
| Modifier le router /coach-report ou son contexte | ✅ +3 imports + +4 lignes |
| Ajouter un partial template dédié | ✅ `coach_body_snapshot.html` |
| Modifier `coach_report.html` pour inclure ce partial | ✅ +6 lignes après section 1 |
| Modifier `app/services/coach_report.py` | ❌ **NE PAS** — test garde |
| Modifier `app/services/body_intelligence.py` | ❌ **NE PAS** — test garde |
| Recalculer une priorité dans le router | ❌ **NE PAS** — router orchestre uniquement |
| Interpréter des métriques body dans le template | ❌ **NE PAS** — partial lit uniquement le snapshot |
| Dupliquer les seuils de `body_intelligence.py` | ❌ **NE PAS** — test garde sur 8 tokens |
| Ajouter migration / modèle / JS / API JSON / LLM | ❌ **NE PAS** — tests garde |
| Réutiliser les classes existantes au maximum | ✅ `coach-block`, `coach-tag`, `text-dim`, `link` |
| CSS minimal seulement si nécessaire | ✅ 0 CSS ajoutée |
| Mobile-first, sobre, non médical, non esthétique | ✅ + test wording |
| Format A4 / print préservé | ✅ même classe `coach-block` que les autres sections |

## 9. CI réelle (post-push)

**Run GitHub Actions : [28319392397](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28319392397) — ✅ success (3/3 jobs verts)**

Note : un premier run [28319244872](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/28319244872) sur `4b06a5e` (Sb_31.3 strict) a été cancelled par un push concurrent `78ee3d4` (merge PR #16 — CI hardening gitleaks). Le run final couvre `78ee3d4` qui contient `4b06a5e` + le merge — Sb_31.3 validé en CI dans son contexte de branche canonique.

- [x] Job `pytest + QA scripts` — ✅ success
- [x] Job `lint (ruff budget + bandit + actionlint + shellcheck)` — ✅ success
- [x] Job `SonarCloud` — ✅ success

## 10. Métriques

| Item | Valeur |
|---|---|
| Lignes router modifiées | +6 (3 imports + 3 logique injection) |
| Lignes partial créées | +67 |
| Lignes template modifiées | +6 |
| Lignes CSS ajoutées | 0 |
| Tests ajoutés | +23 |
| Migrations | 0 |
| Modèles SQLAlchemy | 0 |
| JS ajouté | 0 |
| Services métier core mutés | **0** (test garde sur `coach_report.py` explicite) |
| API JSON publiques | 0 |
| Ruff total | 529 ≤ 548 (inchangé vs Sb_31.2) |

## 11. Verdict

**✅ Sb_31.4 prêt.**

Prochaine étape : `Sb_31.4` traitera la consolidation a11y + perf p95 + non-color cues + responsive 360×640, sans toucher au composer ni à la pipeline. Aucun blocage anticipé.

Pipeline d'orchestration Sx_31 désormais réutilisée par 2 surfaces (`/body/intelligence` et `/coach-report`), validant la séparation router-orchestrateur / composer-décideur / template-affichage de la spec §K. Le composer reste la seule source de vérité métier ; les deux surfaces UI consomment le même snapshot via la même pipeline.
