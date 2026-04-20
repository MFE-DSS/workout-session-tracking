# SPIGNOS Session V1 — Gap Matrix (compagnon Sx_10)

Matrice exploitable extraite de `SPIGNOS_SESSION_V1_GAP_AUDIT_SPEC.md` §F. Une ligne par sujet, classement par statut puis par surface.

| # | Sujet | Sprint source | Statut | Fichiers principaux | Surface UI |
|---|-------|---------------|--------|---------------------|------------|
| 1 | Flow horizontal carte-par-carte | Sb_05 | couvert | `app/templates/session_detail.html` | `/sessions/{id}` |
| 2 | Carte active unique | Sb_05 | couvert | `app/routers/sessions.py` (`session_detail`) | `/sessions/{id}` |
| 3 | Précédent / Suivant | Sb_05 | couvert | `session_detail.html` footer, router `update_exercise_card` branche `nav` | carte active |
| 4 | Save on next + save on prev | Sb_05 | couvert | `app/routers/sessions.py:~474-507` | implicite (submit form) |
| 5 | Compactage done + recap line | Sb_05 | couvert | `session_detail.html` `<summary>`, `app/static/css/app.css:940` | carte pliée |
| 6 | Substitution drawer + lock | Sb_07 | couvert | `app/services/substitution.py`, `session_detail.html:140-166` | carte active |
| 7 | Prévu vs réalisé préservé | Sb_07 | couvert | `app/models/session.py` (`substituted_name` + `exercise_name_snapshot`), `export_builder.py` | export + `/done` |
| 8 | Panel info machine sur carte | Sb_07 | couvert | `session_detail.html:103-132`, `app/services/machine_atlas.py` | carte (toutes cartes, pas juste active) |
| 9 | Atlas JSON + page `/science/atlas` | Sb_07 | couvert | `data/machine_atlas.json`, `app/templates/atlas.html`, route `science_atlas` | `/science/atlas` |
| 10 | Scoring dispatcher strength / cardio | Sb_06 | couvert | `app/services/quality_score.py`, `tests/test_scoring_cardio.py` | timeline + `/done` |
| 11 | Timeline / sparkline kind-aware | Sb_09 | **partiel (G1)** | `app/services/timeline.py`, `progress.html`, `profile.html` | `/progress` et `/profile` ont une légende ; `/` home sparkline **non** |
| 12 | Review `/done` 4 blocs | Sb_08 | couvert | `session_done.html`, `app/services/session_recap.py`, `confidence.py`, `anomalies.py` | `/sessions/{id}/done` |
| 13 | Anomalies (5 règles) + hints (2 règles) | Sb_08 | couvert | `app/services/anomalies.py`, `app/services/hints.py`, `session_detail.html:202-215` | carte active + `/done` |
| 14 | Notes réduites (C03) | Sb_08 | **partiel (G2)** | `session_detail.html:331-334` (note exo en `<details>`) ; `session_detail.html:450-457` (note session encore `<textarea>`) | bloc feedback session |
| 15 | Inputs virgule + point, convention charge C05 | Sb_06 | **partiel (G3)** | `app/services/form_parsing.py`, inputs `type="text"`, hint C05, atlas `load_semantics` | carte active + `/science` ; `load_semantics` absent du catalogue pour 35 exos |
| 16 | Timezone Europe/Paris | Sb_06 | couvert | `app/templating.py` (filtre `\| local`), `tests/test_timezone_rendering.py` | header séance, liste historique, admin |

## Résumé statut

| Statut | Count |
|--------|-------|
| Couvert | 13 |
| Partiel | 3 |
| Manquant | 0 |

## Gaps cumulés

| ID | Ligne matrice | Gravité | Effort | Action |
|----|---------------|---------|--------|--------|
| G1 | 11 | faible | 10 min | Sb_10 — ajouter `.timeline-legend` sous sparkline home |
| G2 | 14 | faible | 10 min | Sb_10 — replier note session en `<details>` (option B) |
| G3 | 15 | info | — | Conforme Sx_06 §1.6 — différé V2, ne pas rouvrir |
| G4 | — | info | — | Note architecture : toutes cartes rendues en DOM, OK ≤ 10 exos |
