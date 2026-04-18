# SPIGNOS Session System Consolidation Spec v1

**Sprint:** Sx_09_session_system_consolidation_spec
**Date:** 2026-04-15
**Status:** Spec de consolidation transverse (SPEC ONLY)
**Prerequisites:** Sx_05 + Sx_06 + Sx_07 + Sx_08 valides
**Termine:** la phase spec du cycle post-v10
**Debloque:** phase build complete (Sb_05 → Sb_09)

---

## 0. Objet

Reconcilier les 4 specs fondatrices du cycle post-v10 :
- Sx_05 Session Flow & Intelligence (cadrage global)
- Sx_06 Scoring, Load & Time Semantics (deja built — Sb_06)
- Sx_07 Machine Knowledge + Substitution Surface
- Sx_08 Session Review Intelligence

Produire :
1. Matrice de compatibilite croisee (4 × 4)
2. Resolution des 5 questions ouvertes Sx_07+Sx_08
3. Arbitrage final des ambiguites residuelles
4. Build queue executable avec effort chiffre + ordre + dependances + rollback

---

## 1. Matrice de compatibilite croisee

### 1.1 Decisions structurantes — table maitresse

| # | Decision | Source | Applique dans | Etat |
|---|----------|--------|---------------|------|
| 1 | SSR + zero JS | Sx_05 §D | Sx_06/07/08 | ✓ respecte partout |
| 2 | Mobile-first (une main, 44px+) | Sx_05 §D | Sx_06/07/08 | ✓ |
| 3 | Une seule carte active a la fois | Sx_05 §E | Sx_07 panneau `i` ; Sx_08 hints | ✓ panneau + hints dans carte active |
| 4 | Save-on-next via bouton explicite | Sx_05 §E | Sx_06 storage OK ; impact UI Sb_05 | ✓ pas de conflit |
| 5 | Prevu vs realise (snapshots immutables) | Sx_05 §F + Sx_03 FINAL | Sx_08 zones_touched via `actual_exercise_name` | ✓ reutilise |
| 6 | Convention charge "comme affiche" | Sx_06 §1 (deja built) | Sx_07 `load_semantics` dans atlas | ✓ Q3 resolue |
| 7 | Dispatcher scoring strength/cardio | Sx_06 §2 (deja built) | Sx_08 regles anomalies strength-only | ✓ Q5 resolue |
| 8 | Timezone Europe/Paris (deja built) | Sx_06 §3 | Transparent autres specs | ✓ |
| 9 | Atlas in-memory JSON | Sx_07 §2 | Consume par Sx_08 zones_touched si present | ✓ couplage optionnel |
| 10 | Panneau `i` bloc 6 body | Sx_07 §4.2 | Cohabite avec drawer subst (bloc 4) + hints Sx_08 | ✓ verifie |
| 11 | Drawer substitution affine | Sx_07 §4.3 | Garde-fous Sx_02 FINAL preserves | ✓ |
| 12 | 5 regles anomalies deterministes | Sx_08 §3 | Strength-oriented (OK par design) | ✓ |
| 13 | 2 hints carte active | Sx_08 §4 | Position bloc 6bis (apres delta, avant set lists) | ✓ |
| 14 | Score confiance logging 0-100 | Sx_08 §5 | Affiche dans /done summary | ✓ |
| 15 | Note exercice reduite `<details>` | Sx_08 §6 | Compatible carte horizontal Sb_05 | ✓ |
| 16 | Rapport narratif auto DIFFER | Sx_08 §13.4 | Aucun LLM introduit V1 | ✓ |

### 1.2 Zones de contact entre specs

| Contact | Sx_A | Sx_B | Interaction | Arbitrage |
|---------|------|------|-------------|-----------|
| Block order in body | Sx_05 | Sx_07 | `i` panel = bloc 6 (apres delta/hint) | Bloc 6 confirmee |
| Hints + panel coexistence | Sx_08 (hints) | Sx_07 (panel) | Tous les deux dans body carte active | Hints bloc 6bis (entre delta et set lists) ; panel `i` bloc 6 |
| zones_touched source | Sx_08 | Sx_07 + muscle_scoring | `classify_exercise(actual_exercise_name)` + optionnel `machine_family` | Sb_07 livre d'abord, Sb_08 consomme si present ; fallback zones seules |
| Convention charge + atlas `load_semantics` | Sx_06 | Sx_07 | `load_semantics` dans atlas documente la convention par machine | Sx_07 expose info, Sx_06 regle canonique reste "comme affiche" ; helper C05 deja en place |
| Anomalies cardio | Sx_08 | Sx_06 | 5 regles strength-only, cardio skip | V2 : regles cardio dediees si besoin |

**Conflits detectes : 0.**

### 1.3 Dependances directionnelles finales

```
Sx_01 FINAL ──► Sx_02 FINAL ──► Sx_03 FINAL ──► Sx_04 FINAL
                                                      │
                                                      ▼
                                               Sx_05 (cadrage)
                                                      │
          ┌──────────────────┬──────────────┬────────┴────────┐
          ▼                  ▼              ▼                  ▼
     Sx_06 (bugs +     Sx_07 (atlas +  Sx_08 (review    Sb_06 (deja built
     semantique)       substitution)   + intelligence)   post Sx_06)
          │                  │              │
          └────────────┬─────┴────────┬─────┘
                       ▼              ▼
                  Sx_09 (ce document, consolidation)
                       │
                       ▼
                  Phase build complete
                  Sb_05 → Sb_07 → Sb_08 → Sb_09
```

---

## 2. Resolution des 5 questions ouvertes (Sx_07 + Sx_08)

### Q1 — Aliases machine et matching exercices (Sx_07)

**Arbitrage final :**
- `machine_slug` dans le catalogue exercice = **lien autoritaire**
- `aliases` dans l'atlas = **informatif pour la page /atlas seulement**
- Pas de resolution automatique nom exercice → machine via alias

**Justification :** evite l'ambiguite, la gouvernance catalogue exercice reste explicite.

### Q2 — Evolution atlas et impact history (Sx_07)

**Arbitrage final :**
- **Atlas additif uniquement** V1 (pas de rename, pas de suppression)
- Si un slug doit etre renomme, l'ancien doit rester comme alias avec `deprecated: true`
- `deprecated` machines rendues en bas de la famille dans /atlas
- Les sessions historiques ne pointent **pas** directement vers l'atlas (pointent vers TemplateExercise qui a `machine_slug`), donc impact limite

**Ajout au schema atlas :**
```json
{
  "slug": "old-chest-press-machine",
  "deprecated": true,
  "aliases": [...],
  ...
}
```

### Q3 — Convention charge + atlas `load_semantics` (Sx_06 × Sx_07)

**Arbitrage final :**
- `load_semantics` dans atlas = **documentation par machine** ("total" / "per_side" / "bw_added")
- Convention utilisateur = **"comme affiche sur l'equipement"** (regle unique, Sb_06 deja built)
- Aucun champ ajoute au catalogue exercice pour V1 (pas de `load_semantics` sur TemplateExercise)
- Helper text generic `"kg = comme affiche sur l'equipement"` (deja deploye Sb_06 c0542d9)
- En V2 potentiel : afficher dynamiquement "par cote" / "total" dans le panneau `i` selon la machine liée

**V1 = pas de complexification.** V2 = enrichissement contextualise quand le lien machine est etabli.

### Q4 — Confidence score percu comme punition (Sx_08)

**Arbitrage final :**
- **Wording :** "Confiance du **logging**" (pas "de la seance") → souligne que c'est la qualite des donnees saisies, pas la performance physique
- **Niveaux neutres :** "eleve" / "moyen" / "faible" (pas "excellent" / "mediocre")
- **Explication dans /science :** nouvelle carte brievement expliquant que le score mesure la completude du logging
- **Affichage discret :** badge sobre dans le bloc summary de /done (pas un grand element visuel)
- **Si score faible :** pas de message culpabilisant, juste le badge ; explication en tooltip/details si interesse

### Q5 — Regles anomalies cardio-specific (Sx_08)

**Arbitrage final :**
- V1 = **strength-only** par design (5 regles concernent reps/weight/rep_targets, inapplicables cardio)
- `compute_anomalies` retourne liste vide pour les seances `kind=cardio`
- **V2 potentiel** : 2-3 regles cardio si besoin ("duration declare sans bpm", "calories > seuil plausible", etc.)
- **Non bloquant V1** : les seances cardio ont leur propre scoring (Sb_06), les anomalies ajoutent peu de valeur immediate

---

## 3. Arbitrages additionnels Sx_09

### 3.1 Ordre des blocs dans le body de la carte exercice (consolidation finale)

Ordre vertical fige **revise Sx_09** (extension Sx_02 FINAL §4.2) :

| Bloc | Contenu | Provenance | Statut |
|------|---------|------------|--------|
| 1 | Lien historique discret | Sx_02 | Existant |
| 2 | Set scheme du catalogue | Sx_02 | Existant |
| 3 | Done-summary (si completed) | Sx_02 | Existant |
| 4 | **Substitute picker** (drawer affine Sx_07) | Sx_02 + Sx_07 | Refactor visuel Sb_07 |
| 5 | Last-time | Sx_02 | Existant |
| 6 | Delta | Sx_02 | Existant |
| 6bis | **Hints I03** (Sx_08) | Sx_08 | Nouveau Sb_08 |
| 7 | Hint progression (legacy) | Sx_02 | Existant |
| 8 | **Panel `i` machine** (Sx_07) | Sx_07 | Nouveau Sb_07 |
| 9 | Set list warmup | Sx_02 | Existant |
| 10 | Set list work | Sx_02 | Existant |
| 11 | Muscle_sensation | Sx_01 | Existant |
| 12 | Note (`<details>` optionnel Sx_08) | Sx_08 | Reduction Sb_08 |
| 13 | Footer CTA (sticky Sb_02.1) | Sb_02.1 | Existant |

**Justification de l'ordre :**
- Les blocs "contexte" (historique, scheme, done, substitute) avant le "recap performance" (last-time, delta, hints)
- Le panneau `i` vient apres les hints car c'est une info plus statique (education) alors que les hints sont dynamiques (adapte a la saisie en cours)
- Notes en toute fin car secondaires
- Ensemble coherent avec la grammaire SSR existante

### 3.2 Interaction hints (Sx_08) + carte horizontale (Sb_05)

Sb_05 (session flow horizontal refactor) doit preserver :
- Les 13 blocs du body carte active
- L'affichage conditionnel des hints (bloc 6bis)
- Le panneau `i` comme `<details>` (pas de popover complexe en UI horizontale)

**Conclusion :** Sb_05 ne reecrit pas le body, il reorganise la **navigation entre cartes**. Les 13 blocs restent intacts par design.

### 3.3 Template kind snapshot — pas necessaire V1

Decision Sx_06 §2.8 : fallback safe `session.template.kind if session.template else "strength"`.

**Sx_09 confirme :** aucune migration `template_kind_snapshot` V1. Le fallback tolere les sessions orphelines (template detache post-reseed). Migration additive possible V2 si besoin remonte.

### 3.4 Convention save-on-next — "Precedent" comportement

Decision Q2 Sx_05 : save silencieux au click Precedent.

**Sx_09 confirme :** si l'user modifie la carte courante puis tape Precedent, le save se declenche automatiquement avant la navigation. Zero warning. Coherent avec save-on-next.

**Edge case :** si le user clique sur un item de la jump bar (non adjacent), meme comportement : save puis navigation.

---

## 4. Build queue definitive

### 4.1 Etat phase spec — CLOSE

| Sprint | Statut |
|--------|--------|
| Sx_05 Session Flow & Intelligence | ✓ VALIDE |
| Sx_06 Scoring, Load & Time Semantics | ✓ VALIDE + **BUILD Sb_06 LIVRE** |
| Sx_07 Machine Knowledge + Substitution | ✓ VALIDE |
| Sx_08 Session Review Intelligence | ✓ VALIDE |
| Sx_09 Consolidation (ce document) | ✓ VALIDE |

### 4.2 Phase build — ordre executable

| Ordre | Sprint | Duree | Dependances | Peut etre parallelise |
|-------|--------|-------|-------------|-----------------------|
| ✓ FAIT | **Sb_06** | 5-6h | Sx_06 | — |
| 1 | **Sb_05** | 4-6h | Sb_06 (bugs fixes) | Non (touche template session_detail en profondeur) |
| 2 | **Sb_07** | 6-8h | Sb_05 (nouveau template stable) | Non |
| 3 | **Sb_08** | 4-6h | Sb_07 (pour zones_touched + machine_family optionnel) | Non |
| 4 | **Sb_09** | 3-5h | Sb_08 (confidence + anomalies influencent visuels globaux) | Non |

**Total phase build restante : 17-25h.**

### 4.3 Pourquoi cet ordre strict

- **Sb_05 avant Sb_07** : le template session_detail est refactore sur donnees saines (post-Sb_06) ; Sb_07 s'inscrit dans le nouveau layout
- **Sb_07 avant Sb_08** : atlas livre avant session review permet zones_touched enrichies ; degradation gracieuse si ordre inverse
- **Sb_08 avant Sb_09** : visuels globaux (timeline, sparkline) doivent refleter la confidence + anomalies apres leur introduction
- **Aucune parallelisation** : tous touchent au template session_detail ou /done, risque de merge conflicts

---

## 5. Details execution par sprint build

### 5.1 Sb_05 — Session Flow Horizontal Refactor

**Scope execution :**

1. Template `session_detail.html` : refactor layout
   - Une seule carte `<details open>` a la fois (mecanisme existant via `active_exercise_id`)
   - Autres cartes collapsed (existant) — verifier hauteur compacte
   - Ajouter `scroll-snap-type: y mandatory` sur le container + `scroll-snap-align: start` sur chaque carte pour scroll vertical saccade naturel (optionnel, progressive enhancement)
   - **Pas de swipe horizontal V1.** La "navigation horizontale" Sx_05 = metaphore conceptuelle, implementee par ergonomie verticale saccadee
2. Save-on-next via bouton explicite
   - Libelle "Suivant →" ou "Enregistrer et passer a E2" (deja Sb_02.1)
   - Zero bouton "Enregistrer" separe sur les cartes intermediaires — ce qui est deja le cas depuis Sb_02.1
3. Bouton "Precedent" explicite (nouveau)
   - Position : a cote du "Suivant →" dans le footer CTA
   - Comportement : POST save + 303 `?active={prev_id}#exercise-{prev_id}`
   - Lock : si aucun exercice precedent, bouton absent ou disabled
4. Auto-compactage done via CSS + attribute `open` sur `<details>` cible (deja en place Sb_02)
5. Tests integration :
   - Save-on-next sur "Precedent" declenche bien le save
   - Navigation directe via jump bar preserve les donnees en cours
   - Aucune regression Sb_02.1 (jump bar 4 etats, footer sticky, CTA contextuel)

**Fichiers :**
- `app/templates/session_detail.html` (refactor layout + bouton Precedent)
- `app/routers/sessions.py` (nouveau endpoint ou parametre pour Precedent)
- `app/static/css/app.css` (optionnel scroll-snap)
- `tests/test_session_flow.py` (extend nouveaux scenarios)

**Criteres d'acceptation :**
- Une seule carte ouverte visible par defaut
- "Precedent" et "Suivant" enregistrent avant navigation
- Zero JS ajoute (sauf optionnel progressive)
- Jump bar 4 etats preservee
- Tests existants verts + 3-5 nouveaux

**Rollback :** revert commit template + route. Zero migration.

### 5.2 Sb_07 — Machine Knowledge + Substitution Surface

**Scope execution (6-8h decoupe) :**

Phase A (2h) — Atlas fondation :
- Creer `data/machine_atlas.json` V1 (30 machines, 8 familles)
- Creer `app/services/machine_atlas.py` (loader + lookup)
- Creer `scripts/machine_atlas_qa.py`
- Tests `tests/test_machine_atlas.py`

Phase B (2h) — Catalogue enrichi :
- Alembic migration `20260416_add_machine_fields.py` (2 colonnes nullable sur `template_exercises`)
- Modifier `app/models/catalog.py` (ajout `machine_slug`, `machine_family`)
- Modifier `reference_split.json` → v11, lier ~30 exercices aux machines
- Modifier `app/services/seed.py` pour persister les nouveaux champs
- Extend `scripts/catalog_qa.py` et `tests/test_catalog_integrity.py`

Phase C (2h) — UX carte exercice :
- Icone `ⓘ` dans `<summary>` de la carte si `machine_info` present
- Panneau `<details class="machine-panel">` bloc 8 du body (post Sx_09 §3.1)
- Drawer substitution affine (wording + count + style CSS `.substitute-picker--drawer`)
- CSS `app/static/css/app.css` nouveaux selecteurs

Phase D (2h) — Page /science/atlas :
- Route `GET /science/atlas` dans `app/routers/pages.py` (ou nouveau `atlas.py`)
- Template `app/templates/atlas.html`
- Lien depuis `science.html`
- Nav optionnel depuis carte exercice ("Voir fiche complete →")
- Tests `tests/test_atlas_routes.py`

**Criteres d'acceptation :**
- QA atlas passe
- 30 machines visibles sur /science/atlas
- Panneau `ⓘ` fonctionne sur cartes exercice ayant un lien
- Cartes sans lien fonctionnent normalement (degradation gracieuse)
- Drawer substitution visuellement affine
- Tests integration verts

**Rollback :** revert commits + migration downgrade. Sessions historiques non impactees (snapshots).

### 5.3 Sb_08 — Session Review + Anomaly Hints

**Scope execution (4-6h decoupe) :**

Phase A (1.5h) — Services :
- Creer `app/services/anomalies.py` (5 regles + `compute_anomalies`)
- Creer `app/services/hints.py` (2 regles + `compute_hints`)
- Creer `app/services/confidence.py` (formule 5 composants)
- Tests unit : `test_anomalies.py`, `test_hints.py`, `test_confidence.py`

Phase B (1.5h) — Extension session_recap :
- Modifier `app/services/session_recap.py` pour enrichir `summary` avec :
  - `confidence_score`, `confidence_level`
  - `top_progression` (via reutilisation `delta.compute_delta`)
  - `zones_touched` (via `muscle_scoring.classify_exercise` + optionnel `machine_family` de Sb_07)
  - `anomalies` (via `compute_anomalies`)
- Tests extend `test_session_recap.py`

Phase C (1.5h) — UI /done :
- Modifier `app/templates/session_done.html` :
  - Bloc "Top progression" (conditionnel)
  - Bloc "Zones sollicitees" (conditionnel)
  - Bloc "A verifier" (conditionnel, si anomalies)
  - Badge confidence dans le summary
- CSS styles `.done-top-progression`, `.done-zones`, `.done-anomalies`, `.confidence-badge`

Phase D (1h) — UI carte exercice :
- Modifier `app/templates/session_detail.html` :
  - Bloc hints 6bis (rendus conditionnels si hints present)
  - Note exercice reduite en `<details>` optionnel (bloc 12)
- Modifier `app/routers/sessions.py` pour charger `hints_by_exercise`
- Tests integration

**Criteres d'acceptation :**
- 5 regles anomalies testees isolement
- Confidence score calibre (LISS parfait ~95, seance incomplete ~50)
- Top progression affiche quand delta existe
- Hints visibles sur carte active si declenches
- Note exercice accessible mais collapsed par defaut
- Wording neutre verifie
- Zero JS

**Rollback :** revert commits. Aucune migration.

### 5.4 Sb_09 — History Visual & Analytics Alignment

**Scope execution (3-5h decoupe) :**

Phase A (1.5h) — Timelines separees ou annotees :
- Modifier `app/services/timeline.py` : option de rendu avec dispatcher strength/cardio
  - Option 1 : deux series distinctes (couleurs differentes)
  - Option 2 : serie unifiee avec normalisation (deja effective post-Sb_06)
- Decision a prendre a Sb_09 selon rendu visuel

Phase B (1h) — Sparkline home et progress :
- Adapter `app/templates/index.html` et `app/templates/progress.html`
- Eventuel dispatch visuel strength vs cardio

Phase C (1h) — Confidence dans visuels :
- Ajouter marker/opacity sur sessions a faible confidence dans les timelines
- Bloc "sessions a faible confiance" dans /progress si plusieurs cas

Phase D (1h) — Export enrichi :
- Modifier `app/services/export_builder.py` pour inclure :
  - `session_kind`
  - `confidence_score`
  - `anomaly_count`
- Tests regression export

**Criteres d'acceptation :**
- Seances cardio n'apparaissent plus comme "faibles" dans timelines
- Distinction visuelle claire si pertinent
- Confidence apparait dans exports
- Aucune regression sur dashboards existants

**Rollback :** revert commits. Aucune migration.

---

## 6. Strategie de rollback globale

Chaque sprint build peut etre rollback independamment :

| Sprint | Strategie | Impact rollback |
|--------|-----------|-----------------|
| Sb_05 | `git revert` commits template + route | Retour au flow Sb_02.1, aucune donnee perdue |
| Sb_07 | `git revert` + `alembic downgrade` 1 revision | 2 colonnes retirees de template_exercises (snapshots preserves, sessions historiques intactes) |
| Sb_08 | `git revert` commits services + templates | Aucun modele touche |
| Sb_09 | `git revert` commits timeline + templates | Aucun modele touche |

**Ordre de rollback si besoin :** inverse de l'ordre de build (Sb_09 → Sb_08 → Sb_07 → Sb_05).

---

## 7. Risques transverses

| Risque | Probabilite | Mitigation |
|--------|------------|------------|
| Ordre build strict bloque en cas d'incident sur Sb_05 | Faible | Sb_06 deja en prod offre une base saine ; Sb_05 peut etre partitionne (layout refactor puis bouton Precedent) |
| Sb_07 migration Alembic echoue sur prod | Faible | Migration additive pure (colonnes nullable), testable en dry-run local |
| Sb_08 wording confidence mal percu | Moyen | Iterer si feedback negatif ; fallback = cacher le badge si user veut |
| Sb_09 change rendu timeline trop brusquement | Faible | Option unifiee (non-disruption) par defaut ; dispatch visuel en mode opt-in si besoin |
| Tests casses en cascade | Moyen | Chaque sprint a ses tests dedies ; full suite apres chaque sprint |

---

## 8. Definition of Done Sx_09

| Critere | Statut |
|---------|--------|
| Matrice compatibilite 4 specs produite (0 conflit) | ✓ §1 |
| 5 questions ouvertes Sx_07+Sx_08 resolues | ✓ §2 (Q1-Q5) |
| Arbitrages additionnels Sx_09 documentes | ✓ §3 |
| Build queue executable avec effort chiffre | ✓ §4 |
| Details execution par sprint (fichiers, criteres, rollback) | ✓ §5 |
| Strategie rollback globale | ✓ §6 |
| Risques transverses + mitigation | ✓ §7 |
| Ordre de lancement confirme | ✓ Sb_05 → Sb_07 → Sb_08 → Sb_09 |

---

## 9. Recommandation de lancement

**Phase build autorisee a demarrer immediatement post-validation Sx_09.**

Premier sprint : **Sb_05 — Session Flow Horizontal Refactor** (4-6h).

**Prochain commit attendu apres validation :**
- Sb_05 implementation
- Sb_05 sprint report
- Full suite verte

---

## 10. Synthese executive

- Phase spec close : 5 specs FINAL validees, 0 conflit transverse detecte
- 5 questions ouvertes resolues (atlas additive only, load semantics informatif, wording confidence neutre, anomalies strength-only V1, aliases informatifs)
- Ordre body carte exercice fige en 13 blocs (refined Sx_09 §3.1)
- Build queue definitive : Sb_05 → Sb_07 → Sb_08 → Sb_09 (ordre strict, 17-25h au total)
- Chaque sprint rollback independamment, zero migration destructive
- Phase build autorisee a demarrer par Sb_05
