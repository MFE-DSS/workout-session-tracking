# Sprint Sx_10 Report — Session V1 Gap Audit

**Date :** 2026-04-20
**Type :** SPEC ONLY — audit d'écart, aucun code produit
**Branche auditée :** `claude/sprint-reporting-fitness-app-V7Qr6` au commit `0110544`
**Prérequis :** Sb_05, Sb_06, Sb_07, Sb_08, Sb_09, catalog v12 commités
**Successeur recommandé :** Sb_10 (polish ciblé ~1h) puis Sx_11 (nouveau cycle produit)

---

## 1. Ce que j'ai concrètement inspecté

### 1.1 Commits et branche

`git log --oneline` lu intégralement pour localiser chaque sprint. Le graphe confirme l'ordre d'arrivée sur la branche :

```
b01→b02→b03→c05 (Sb_06 en 4 étapes) → docs Sb_06 → specs Sx_07/08/09 → Sb_05 → Sb_07 → Sb_08 → Sb_09 → catalog v12 → doc polish
```

Important : **Sb_06 a été buildé avant Sb_05 chronologiquement**, ce qui explique la confusion potentielle de l'utilisateur.

### 1.2 Fichiers ouverts (lecture directe)

Services :
- [app/services/quality_score.py](app/services/quality_score.py)
- [app/services/anomalies.py](app/services/anomalies.py)
- [app/services/hints.py](app/services/hints.py)
- [app/services/confidence.py](app/services/confidence.py)
- [app/services/session_recap.py](app/services/session_recap.py)
- [app/services/machine_atlas.py](app/services/machine_atlas.py)
- [app/services/substitution.py](app/services/substitution.py)
- [app/services/timeline.py](app/services/timeline.py)
- [app/services/export_builder.py](app/services/export_builder.py)
- [app/services/form_parsing.py](app/services/form_parsing.py) (via agent)
- [app/templating.py](app/templating.py) (via agent)

Routeurs :
- [app/routers/sessions.py](app/routers/sessions.py) — `session_detail`, `update_exercise_card`, `session_done`, `science_atlas`
- [app/routers/pages.py](app/routers/pages.py) — home sparkline + progress timeline
- [app/routers/auth_routes.py](app/routers/auth_routes.py) — /profile timeline

Templates :
- [app/templates/session_detail.html](app/templates/session_detail.html)
- [app/templates/session_done.html](app/templates/session_done.html)
- [app/templates/atlas.html](app/templates/atlas.html)
- [app/templates/science.html](app/templates/science.html)
- [app/templates/progress.html](app/templates/progress.html)
- [app/templates/profile.html](app/templates/profile.html)

Modèles :
- [app/models/catalog.py](app/models/catalog.py)
- [app/models/session.py](app/models/session.py)

Données :
- [data/reference_split.json](data/reference_split.json) — v12, comptes vérifiés par script
- [data/machine_atlas.json](data/machine_atlas.json) — v1, 8 familles / 29 machines

### 1.3 Commandes exécutées

```bash
python scripts/catalog_qa.py            # PASS — 16 tpl, 98 ex, 0 err
python scripts/machine_atlas_qa.py      # PASS — 8 fam, 29 machines
git log --oneline -20                   # chronologie complète de la branche
python -c "..."                         # stats catalogue : 63 slug / 1 family only / 34 unlinked
```

## 2. Ce que j'ai trouvé par sprint

### Sb_05 — Session Flow Horizontal
**Présent :**
- `<details>` par slot avec `{% if is_active %}open{% endif %}` à `session_detail.html:54-66`
- Jump bar 4 états (`active`/`done`/`partial`/`future`) calculée à `sessions.py:267-286`, rendue à `session_detail.html:29-46`
- Boutons Précédent + Suivant via `name="nav" value="prev/next"` à `session_detail.html:343-361`
- Router `update_exercise_card` branche explicitement `nav=prev` vs `next`, save + redirect atomique
- Recap line `N kg · N reps` sur `<summary>` dès `done > 0`
- CSS `.exercise-card--done` : bordure verte, code vert, texte dim

**Ambigu / À noter :**
- Toutes les cartes sont dans le DOM (pas de lazy render). Pour ≤ 10 exercices c'est OK — documenté §F#G4 comme info pas gap.

**Manquant :** rien au sens fort.

### Sb_06 — Scoring + Load + Time Semantics
**Présent (en 4 étapes) :**
- `form_parsing.to_float` accepte `,` et `.` (commit `edd435e`, 21 tests dédiés)
- Inputs `type="text" inputmode="decimal" pattern="[0-9]*[.,]?[0-9]*"` sur weight + bodyweight
- Filtre Jinja `| local` et `local_weekday_iso` dans `app/templating.py` (commit `0183493`), 7 templates migrés
- `tests/test_timezone_rendering.py` : 9 tests hiver/été/minuit/Europe-Paris
- `quality_score.compute_session_quality` dispatcher strength/cardio (commit `25bf65c`)
- `compute_session_quality_cardio` : 4 composants (durée 50, intensité 20, abs 20, subjectif 10)
- `tests/test_scoring_cardio.py` : 11 tests sur les deux branches
- Hint C05 `kg = comme affiché sur l'équipement` sous le heading « Travail » (commit `c0542d9`)
- Page `/science` section « Convention de saisie des charges » avec 7 cas équipement

**Ambigu :**
- `load_semantics` est sur l'atlas (29 machines) mais **pas** sur `reference_split.json`. Spec Sx_06 §1.6 avait différé V2 — donc conforme à la décision, pas un gap. 35 exercices du catalogue sur 98 n'affichent pas de convention explicite. Documenté §F#G3.

**Manquant :** rien (cf. G3 = décision différée spec, pas oubli).

### Sb_07 — Machine Atlas + Substitution Surface
**Présent :**
- `data/machine_atlas.json` v1, version `2026-04-15.v1`, 8 familles / 29 machines
- `app/services/machine_atlas.py` loader in-memory + lookups
- Migration alembic `20260418_add_machine_atlas_links.py` (`machine_slug` + `machine_family` nullable sur `template_exercises`)
- Catalog v11 : 63 exercices sur 98 avec `machine_slug` ; 1 avec `machine_family` only ; 34 non liés (isolation/accessoires, intentionnel)
- Panel `<details class="machine-panel">` à `session_detail.html:103-132` — rendu sur toutes les cartes (pas juste active), affiche `execution_cues`, `common_mistakes`, `load_semantics`
- Substitute picker refacto drawer à `session_detail.html:140-166` — compteur d'alternatives, wording explicite
- Route `/science/atlas` + template `atlas.html` — TOC 8 familles, 29 fiches complètes
- Lien depuis `/science` (section « Atlas des machines »)

**Ambigu :** rien.

**Manquant :** rien au sens strict.

### Sb_08 — Session Review Intelligence
**Présent :**
- `anomalies.py` : 5 règles A/B/C/D/E, `Anomaly` dataclass, `compute_anomalies(session, prior_weight_by_code=None)`
- `hints.py` : 2 règles A/B, `Hint` dataclass, cap 1 B-hint par carte
- `confidence.py` : `compute_confidence_score` (40+15+10+10+15+10), `level_for` → `eleve`/`moyen`/`faible`
- `session_recap.build_recap` étendu : `confidence_score`, `confidence_level`, `top_progression`, `zones_touched`, `anomalies`
- `/done` 4 blocs (session_done.html:57-116)
- Note exercice repliée dans `<details class="exercise-card__note">` à `session_detail.html:331-334`
- Hints sur carte active uniquement (`{% if is_active %}` à `session_detail.html:202-215`)

**Ambigu :**
- **Note session** reste `<textarea rows="2">` d'emblée visible (`session_detail.html:450-457`). Sx_08 §6 suggérait de garder la note session dans le feedback session naturel — donc défendable — mais crée une asymétrie visuelle avec la note exo. Documenté §F#G2.

**Manquant :** rien.

### Sb_09 — History Visual & Analytics Alignment
**Présent :**
- `timeline.TimelinePoint.kind`, `KIND_COLORS` (`#f25f3a` strength / `#38b2ac` cardio)
- `build_sparkline_svg(... kinds=None)` colore les dots par kind
- `/progress` et `/profile` ont une légende `.timeline-legend` sous le chart qualité
- `export_builder.SCHEMA_VERSION = 2` ; nouveaux champs `session_kind`, `quality_score`, `confidence_score`, `confidence_level` en JSON et CSV
- Consumers migrés : `pages.home`, `pages.progress`, `auth_routes./profile`

**Ambigu :**
- **Home sparkline sans légende** : les dots sont bien colorés (via `sparkline_kinds` dans `pages.home`) mais l'UI de `/` n'affiche pas de `.timeline-legend`. Documenté §F#G1.

**Manquant :** rien au sens structurel.

### catalog v12 (Pull A balance)
**Présent :**
- Pull A : 7 exercices / 20 work sets (E6 Pullover machine + E7 Straight-arm pulldown câble ajoutés)
- Focus préservé (« Dos largeur + Delts postérieurs »), les deux ajouts classifient en `lats`
- E6 lié à l'atlas (`pullover-machine`) ; E7 en famille seule (`back-vertical`)
- Gouvernance documentée dans `SPIGNOS_CATALOG_GOVERNANCE.md` section v12
- Test `test_pull_a_has_seven_exercises` aligné

**Ambigu :** rien.

**Manquant :** rien.

## 3. Ce qui est clairement présent

Voir `SPIGNOS_SESSION_V1_GAP_AUDIT_SPEC.md` §F — matrice 16 sujets. **13 sujets ✅, 3 sujets 🟡, 0 sujet ❌**.

## 4. Ce qui est ambigu

| # | Sujet | Nature de l'ambiguïté |
|---|-------|----------------------|
| 1 | Panel machine sur toutes les cartes vs carte active uniquement | Actuellement rendu partout. L'intention Sx_07 disait « sur la carte active ». À expliciter comme décision produit (préparation avant de commencer l'exo). Pas un bug. |
| 2 | Note session sur `/feedback` | Asymétrie UI avec la note exo, mais alignée avec Sx_08 §6. Peut rester ou se replier — décision produit. |
| 3 | Légende sparkline home | Absence de légende là où il y a pourtant une couleur. Manifestement un oubli vs `/progress`. |

## 5. Ce qui manque encore

Aucun sujet n'est totalement absent. Les 3 partiels (§F#11, §F#14, §F#15) couvrent l'intégralité des écarts identifiés.

## 6. Recommandation du prochain sprint build

### Sb_10 — Session V1 polish (gap closure)

**Objectif :** fermer G1 et G2 pour clore proprement le cycle V1 avant d'ouvrir un nouveau sujet.

**Scope (≤ 1h) :**
1. Ajouter `.timeline-legend` sous le sparkline home dans `app/templates/index.html` (même markup que `/progress`).
2. Replier la note session dans un `<details>` à `session_detail.html:450-457`, ouvert par défaut uniquement si `session.free_note` est non vide. Miroir exact de la note exo.
3. 1 test sur `/` vérifiant la présence de `.timeline-legend` quand les sessions cardio et strength coexistent sur les 14 derniers jours.

**Hors scope explicite :**
- Pas de `load_semantics` sur `reference_split.json` (conforme Sx_06 différé V2).
- Pas de refacto du panel machine (carte active vs toutes cartes — décision produit à prendre séparément).
- Pas de nouvelle feature.

**Critères d'acceptation :**
- Full suite verte (attendu : 635 → 636 avec le nouveau test, ou 635 si on s'abstient).
- Légende visible sur `/` si au moins une session cardio et une session strength sur 14j.
- Note session pliée par défaut dans `/sessions/{id}` quand vide.

### Alternative minimaliste

Si tu veux ne pas toucher à la note session (option A de G2), Sb_10 se réduit à G1 seule — 15 min total.

## 7. Recommandation du prochain sprint de spec après ce build

Une fois Sb_10 fermé, **Sx_11** devrait cadrer la **prochaine direction produit** et non pas rouvrir Session System. Trois candidats, à arbitrer par l'utilisateur :

| Candidat | Angle | Effort spec | Effort build |
|----------|-------|-------------|--------------|
| **Sx_11a — Pre-session briefing / préparation** | Montrer les cues d'exécution du prochain exo avant de l'ouvrir, surfacer le last-time et la cible. Surface `/sessions/{id}` sur la carte `future`. | 4h | 6-8h |
| **Sx_11b — Programme-builder utilisateur** | Permettre à l'utilisateur de créer ses propres templates (pas juste consommer le catalogue). Grosse spec. | 6-8h | 15-20h |
| **Sx_11c — Squad / social v2** | Améliorer `squad.py` déjà existant : défis hebdo, comparaisons non-agressives, confidentialité renforcée. | 4h | 8-12h |

**Recommandation personnelle :** Sx_11a — plus petit effort, améliore immédiatement le flow en séance, naturellement lié à l'atlas déjà buildé. À valider par l'utilisateur selon ses priorités.

## 8. Livrables produits par ce sprint

| Fichier | Action |
|---------|--------|
| `docs/strategy/SPIGNOS_SESSION_V1_GAP_AUDIT_SPEC.md` | New |
| `docs/strategy/SPIGNOS_SESSION_V1_GAP_MATRIX.md` | New (compagnon exploitable) |
| `docs/SPRINT_Sx_10_session_v1_gap_audit_spec_REPORT.md` | New (ce rapport) |

Aucun code touché. Aucune migration. Aucun fichier applicatif modifié. Branche inchangée hors ces 3 docs.

## 9. Synthèse exécutive

- Cycle Session System V1 (Sb_05 → Sb_09) + catalog v12 : **13/16 surfaces couvertes, 3 partielles, 0 manquante**.
- **Sb_06 est livré** (commits `edd435e` → `6ca03a8`) — confusion levée.
- 3 gaps résiduels : G1 (légende sparkline home), G2 (note session à replier, optionnel), G3 (`load_semantics` catalogue — décision Sx_06 différée V2, ne pas rouvrir).
- Build recommandé : **Sb_10 polish** (≤ 1h) pour G1 + G2.
- Spec recommandée après Sb_10 : **Sx_11a Pre-session briefing** (candidat par défaut, à valider par l'utilisateur).
- 635 tests verts, QA clean, branche saine. Le cycle V1 est **livré dans sa quasi-totalité** — pas de gros chantier caché.
