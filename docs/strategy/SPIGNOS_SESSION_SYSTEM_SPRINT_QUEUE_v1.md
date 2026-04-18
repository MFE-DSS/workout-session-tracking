# SPIGNOS Session System — Sprint Queue v1

**Date:** 2026-04-15
**Statut:** Queue ordonnee, phase spec + phase build
**Anchor:** `SPIGNOS_SESSION_FLOW_AND_INTELLIGENCE_SPEC_v1.md` (Sx_05)
**Principe :** **specs d'abord, builds ensuite.** Chaque build necessite sa spec verrouillee. Aucun build ne demarre avant approbation humaine.

---

## Vue d'ensemble

```
PHASE SPEC (5 sprints — aucun code)
  Sx_05  Session Flow & Intelligence Spec        [CE SPRINT — cadrage global]
  Sx_06  Scoring, Load, Time Semantics           [details charges + temps + score]
  Sx_07  Machine Knowledge & Substitution UX     [atlas machine + drawer substitution]
  Sx_08  Session Review Intelligence             [synthese finale + incoherences]
  Sx_09  Session System Consolidation            [reconciliation, decisions transverses]

PHASE BUILD (5 sprints — code + tests + deploy)
  Sb_05  Session Flow Horizontal Refactor        [carte-par-carte + save-on-next]
  Sb_06  Scoring + Input + Time Semantics        [charges decimales + timezone + scoring cardio]
  Sb_07  Machine Knowledge + Substitution Surface [atlas JSON + panneau i + drawer substitution]
  Sb_08  Session Review + Anomaly Hints          [synthese enrichie + hints V1]
  Sb_09  History Visual & Analytics Alignment    [timeline dispatcher strength/cardio + exports]
```

Dependances et parallelisation documentees par sprint (§par-sprint).

---

## PHASE SPEC

### Sx_05 — Session Flow & Intelligence Spec [CE SPRINT]

**Objectif :** Cadrer la mutation logger vertical → seance guidee carte-par-carte, poser vocabulaire canonique, definir les modeles (flow, prevu/realise, charges, scoring, atlas, intelligence), et mapper les surfaces repo impactees.

**Dependances :** cycle catalogue v10 clos.

**Livrables :**
- `docs/strategy/SPIGNOS_SESSION_FLOW_AND_INTELLIGENCE_SPEC_v1.md`
- `docs/strategy/SPIGNOS_SESSION_SYSTEM_SPRINT_QUEUE_v1.md` (ce doc)
- `docs/SPRINT_Sx_05_session_flow_and_intelligence_spec_REPORT.md`

**Criteres de passage :**
- Vocabulaire normatif figue (§P de la spec)
- 10 problemes produit mappes sur surfaces repo
- 4 couches intelligence preparees sans implementation
- Suite des sprints justifiee (ce document)

**Risques :** reintroduire des decisions deja verrouillees des cycles precedents. Mitigation : §A.3 "ce qui est stabilise" de la spec.

---

### Sx_06 — Scoring, Load, Time Semantics Spec

**Objectif :** Produire la spec technique detaillee des 3 chantiers semantiques :
1. Convention de charge canonique (par cote vs total, application, rappel UI, champ catalogue optionnel `load_semantics`)
2. Separation scoring strength vs cardio (formules, dispatcher, plafonds, impacts consumers)
3. Timezone utilisateur (defaut Europe/Paris, stockage UTC, rendu local, edge cases frontieres jour)

**Dependances :** Sx_05 valide.

**Livrables :**
- `docs/strategy/SPIGNOS_SCORING_LOAD_TIME_SEMANTICS_SPEC_v1.md`
- `docs/SPRINT_Sx_06_REPORT.md`

**Criteres de passage :**
- Regle canonique charge arbitree **une fois pour toutes**
- Formule `compute_session_quality_cardio` documentee avec composants + seuils
- Formule `compute_session_quality_strength` re-documentee (refactor du quality_score actuel)
- Strategie timezone decidee (simple defaut vs pref utilisateur)
- Matrice consumers impactes (leaderboard, kpis, timeline, export, behavioral)
- Liste exhaustive des surfaces a migrer (fichiers + lignes)

**Risques :**
- Scoring cardio mal calibre au premier coup → mitiger via mode "preview" compare aux anciennes valeurs
- Convention charge mal comprise par les users existants → rappel UI discret (C05) + page `/science`

---

### Sx_07 — Machine Knowledge & Substitution Surface Spec

**Objectif :** Specifier l'atlas machine + l'integration UX :
1. Schema `data/machine_atlas.json` (families, sous-familles, machines, cues, mistakes)
2. Lien exercice → famille/machine (ajout optionnel dans `reference_split.json`)
3. UX panneau `i` (positionnement, contenu, SSR-friendly, zero JS)
4. Refonte drawer substitution locale (actuel `<details>` → pattern drawer compact)
5. Page `/atlas` ou section `/science/atlas`

**Dependances :** Sx_05 valide. Sx_06 recommande (pour lien charge canonique → description machine).

**Livrables :**
- `docs/strategy/SPIGNOS_MACHINE_ATLAS_AND_SUBSTITUTION_UX_SPEC_v1.md`
- `docs/SPRINT_Sx_07_REPORT.md`
- Maquette textuelle de l'atlas (familles + 15-25 machines courantes)

**Criteres de passage :**
- Schema JSON valide et minimaliste
- Ne **pas** depasser ~30 machines au premier catalogue V1
- UX panneau `i` specifie (SSR, compact, fermable, non bloquant)
- Pattern drawer substitution clarifie (difference visuelle vs picker actuel)
- Lien exercice → famille via pattern ajoutable sans rework

**Risques :**
- Catalogue atlas trop ambitieux → s'en tenir a 30 machines V1
- UX panneau `i` trop bavard → wording court, garde-fou explicite

---

### Sx_08 — Session Review Intelligence Spec

**Objectif :** Specifier la synthese finale enrichie + la couche detection d'incoherences minimale :
1. Structure rapport final dans `/done` (Sb_R3 existant a etendre)
2. Regles deterministes I01 (incoherences intra-exercice)
3. Hints contextuels I03 (affichage carte active)
4. Score de confiance logging I04
5. Reduction notes inline (C03) + synthese finale simplifiee (C06)

**Dependances :** Sx_05 + Sx_06 valides. Sx_07 recommande.

**Livrables :**
- `docs/strategy/SPIGNOS_SESSION_REVIEW_INTELLIGENCE_SPEC_v1.md`
- `docs/SPRINT_Sx_08_REPORT.md`

**Criteres de passage :**
- Liste de 5-8 regles deterministes I01 ecrites explicitement
- Structure de rapport final documentee (blocs + wording)
- Mecanique hints V1 (emplacement UI + trigger + wording neutre)
- Score de confiance formule documentee
- Regles reduction notes (quoi retirer du body exercice, quoi garder, ou deplacer)

**Risques :**
- Trop-plein "IA magique" → discipline wording "deterministe, pas predictif"
- Over-engineering regles incoherences → start with 3-5 regles max

---

### Sx_09 — Session System Consolidation Spec

**Objectif :** Reconcilier Sx_05 + Sx_06 + Sx_07 + Sx_08 en un modele transverse unifie, resoudre conflits transverses, figer les arbitrages finaux, produire la build queue definitive Sb_05 → Sb_09.

**Dependances :** Sx_05, Sx_06, Sx_07, Sx_08 valides.

**Livrables :**
- `docs/strategy/SPIGNOS_SESSION_SYSTEM_CONSOLIDATION_SPEC_v1.md`
- `docs/SPRINT_Sx_09_REPORT.md`
- Mise a jour de la queue build avec dependances precises et effort chiffre

**Criteres de passage :**
- Matrice compatibilite croisee 4 specs (Sx_05/06/07/08)
- Zero conflit non resolu documente
- Build queue exhaustive avec estimation d'effort
- Plan de rollback pour chaque build

**Risques :** decouverte tardive d'une contradiction → remettre en boucle une sous-spec.

---

## PHASE BUILD

### Sb_05 — Session Flow Horizontal Refactor

**Objectif :** Transformer la page `/sessions/{id}` en flow carte-par-carte avec **save-on-next** implicite, en preservant le SSR et sans JS lourd.

**Perimetre :**
- Refactor `app/templates/session_detail.html` vers structure "une carte active visible, autres compactees"
- Mecanisme save-on-next (bouton "Suivant" → POST save + redirect 303 `?active={next_id}`)
- Navigation precedent/suivant explicite
- Auto-compactage carte done via CSS + attribute `open`
- Preserver jump bar (Sb_02.1) et CTA contextuel

**Fichiers cibles :**
- `app/templates/session_detail.html` (refactor UX majeur)
- `app/routers/sessions.py` (simplification mecanismes save)
- `app/static/css/app.css` (nouveau pattern carte active/compact/horizontal)

**Dependances :** Sx_05 + Sx_06 valides (au moins B02 timezone et B01 decimales corriges en pre-requis pour eviter de tester sur data cassee).

**Criteres d'acceptation :**
- Une seule carte ouverte a la fois par defaut
- Bouton "Suivant" enregistre + ouvre la suivante (pas de bouton "Enregistrer" separe sur carte intermediaire)
- Bouton "Precedent" ouvre la precedente (avec save si modifs)
- Jump bar inchangee (4 etats preserves)
- Aucun JS ajoute (ou extreme minimal, progressive enhancement)
- Zero regression tests
- Mobile 320px-430px fluides

**Risques :**
- Save-on-next sur Precedent peut perdre des modifs si user clique Precedent par erreur → confirmer save implicite + warning si data modifiee (simple `<dialog>` SSR ou pas de warning V1)
- Refacto UX sur page deja mature → faire en plusieurs PRs idempotentes

**Effort estime :** 4-6h (UI + tests update + recette).

---

### Sb_06 — Scoring + Input + Time Semantics Build

**Objectif :** Corriger B01, B02, B03 + implementer la convention de charge canonique + scoring cardio separe.

**Perimetre :**

**B01 decimales :**
- Changer inputs `type="number"` en `type="text" inputmode="decimal" pattern="[0-9]*[.,]?[0-9]*"` pour weight_kg + cardio fields numeriques avec decimales
- Backend `to_float` deja tolere virgule : tests unit confirmation

**B02 timezone :**
- Decider storage UTC (conserve) + rendu local Europe/Paris par defaut (via `ZoneInfo` ou equivalent)
- Fix : `WEEKDAY_LABELS[session.weekday_iso]` + templates rendu started_at/ended_at en local
- Possibilite user preference `tz` (optionnel V1)
- `session_recap._duration_label` deja tolere tz

**B03 + scoring cardio :**
- Refactor `app/services/quality_score.py` en dispatcher :
  - `compute_session_quality(session)` → dispatch par `session.template.kind`
  - Nouveau `compute_session_quality_strength(session)` — formule actuelle renommee
  - Nouveau `compute_session_quality_cardio(session)` — formule §H.3 de Sx_05
- Tests unitaires complets pour les deux regimes
- Impact consumers : leaderboard, kpis.avg_success_score_30d (exclure cardio), timeline sparkline (dispatcher ou rendu separe — voir Sb_09)

**Convention charge (C02 + C05) :**
- Documenter dans `docs/PRODUCT_SPEC.md` + page `/science`
- Ajouter helper text discret sous input weight_kg dans template
- Optionnel : ajouter `load_semantics` dans `reference_split.json` pour exercices ambigus (v11) — peut etre differe

**Fichiers cibles :**
- `app/templates/session_detail.html` (input types + helper text)
- `app/templates/index.html`, `app/templates/progress.html` (dispatcher rendu si besoin)
- `app/services/quality_score.py` (refactor dispatcher)
- `app/services/kpis.py` (filtrer par kind pour agregats strength)
- `app/routers/sessions.py` (timezone rendu)
- `app/services/session_recap.py` (timezone rendu)
- `data/reference_split.json` (si `load_semantics` decide)
- Tests : new `tests/test_scoring_cardio.py`, maj `tests/test_quality_score.py`

**Criteres d'acceptation :**
- Saisie `12.5` et `12,5` acceptees et stockees identiquement
- Date affichee coherente avec fuseau user (Europe/Paris defaut)
- LISS bien execute (20min zone) score >= 80
- `compute_session_quality_strength` renvoie les valeurs identiques a l'actuel sur cas strength
- Tests existants verts
- Export CSV/JSON inclut `session_kind` ou equivalent

**Risques :**
- Migration implicite : les scores historiques vont etre recalcules a la volee → jauger si l'impact est acceptable ou ajouter une colonne figee
- Convention charge documentee mais mal comprise → C05 discret + aide contextuelle

**Effort estime :** 5-7h.

---

### Sb_07 — Machine Knowledge + Substitution Surface Build

**Objectif :** Implementer atlas machine + drawer substitution + point d'entree `i` depuis chaque vignette.

**Perimetre :**
- Creer `data/machine_atlas.json` (30 machines V1)
- Ajouter champs optionnels `machine_family`, `machine_slug` a ~30 exercices du catalogue (version bump v11)
- Nouveau service `app/services/machine_atlas.py` (loader + lookup)
- Nouveau template partial `app/templates/_machine_panel.html`
- Template session_detail : icone `i` dans header carte → ouvre panneau contextuel
- Refonte drawer substitution : pattern visuel plus clair (vs `<details>` actuel)
- Page `/atlas` ou `/science/atlas` pour exploration complete
- Nav : ajouter lien "Atlas" (ou sous-section de `/science`)

**Fichiers cibles :**
- `data/machine_atlas.json` (nouveau)
- `data/reference_split.json` (version v11 avec liens machine)
- `app/services/machine_atlas.py` (nouveau)
- `app/services/seed.py` (charger atlas si strategie DB-backed, ou loader en memoire V1)
- `app/routers/pages.py` ou nouveau `app/routers/atlas.py`
- `app/templates/session_detail.html` (icone i + drawer substitution refait)
- `app/templates/_machine_panel.html` (nouveau)
- `app/templates/atlas.html` (nouveau)
- `app/templates/base.html` (nav)
- Tests integration atlas

**Dependances :** Sx_07 valide. Sb_05 recommande (pour integrer drawer dans nouveau layout).

**Criteres d'acceptation :**
- Icone `i` visible dans header carte sans surcharger l'UI
- Panneau s'ouvre sans JS (natif `<details>` ou navigation fragment)
- Atlas navigable (30 machines, 5-8 familles)
- Drawer substitution visuellement distinct d'un `<details>` generique
- Aucun exercice sans `i` ne casse (degradation gracieuse)
- Tests QA catalog verts

**Risques :**
- Premiere version atlas trop pauvre → OK, iterer
- Drawer substitution "too clever" → rester dans grammaire SSR stricte

**Effort estime :** 6-8h.

---

### Sb_08 — Session Review + Anomaly Hints Build

**Objectif :** Enrichir la page `/done` avec synthese structuree + detecter 3-5 incoherences simples + afficher hints contextuels V1.

**Perimetre :**
- Refactor `app/services/session_recap.py` :
  - Ajouter `compute_anomalies(session)` → liste de flags deterministes
  - Ajouter `compute_top_progression(session)` → delta notable vs derniere fois
  - Ajouter `compute_confidence_score(session)` → 0-100 qualite logging
- Etendre `app/templates/session_done.html` :
  - Nouveau bloc "Synthese" (top progression, zones touchees, substitutions)
  - Nouveau bloc "A verifier" si anomalies detectees
  - Confidence badge discret
- Reduction notes inline (C03) dans session_detail :
  - Retirer textarea exercice du body par defaut (deplacer dans `<details>` optionnel)
  - Garder note session dans feedback
- Nouveau `app/services/hints.py` — compute_hints pour carte active (optionnel V1, peut etre differe)

**Fichiers cibles :**
- `app/services/session_recap.py` (extensions)
- `app/services/hints.py` (nouveau, si decide)
- `app/templates/session_done.html` (nouveaux blocs)
- `app/templates/session_detail.html` (reduction notes + hints slot)
- Tests : `tests/test_anomalies.py`, `tests/test_session_review.py`

**Dependances :** Sx_08 valide. Sb_05 + Sb_06 + Sb_07 termines (l'enrichissement de /done consolide tout).

**Criteres d'acceptation :**
- 3-5 regles anomalie implementees avec tests
- Synthese `/done` lisible et non-verbeuse
- Notes libres reduites mais pas supprimees (accessibles en mode optionnel)
- Confidence score entre 0-100, formule deterministe documentee
- Aucune alerte bloquante, wording neutre

**Risques :**
- Regles anomalie trop bruyantes → seuils conservateurs V1
- Confidence score mal comprit → documenter dans `/science`

**Effort estime :** 4-6h.

---

### Sb_09 — History Visual & Analytics Alignment

**Objectif :** Aligner les visualisations globales (timeline, sparkline, progress, dashboard) avec le dispatch strength/cardio et l'enrichissement post-Sb_08.

**Perimetre :**
- Timeline quality (`app/services/timeline.py`) : separer strength/cardio ou normaliser plafond
- Sparkline home (`app/templates/index.html`) : idem
- `/progress` page : possiblement 2 graphes (strength vs cardio) ou un indicateur unifie equitable
- Body engineering dashboard : verifier si axes impactes
- Exports : inclure `session_kind` + nouveau confidence score si pertinent
- Eventuel fix B04 (representation visuelle cardio)

**Fichiers cibles :**
- `app/services/timeline.py`
- `app/templates/index.html`, `app/templates/progress.html`, `app/templates/dashboard.html`
- `app/services/export_builder.py`
- Tests visuels (non-regression + nouvelle coherence)

**Dependances :** Sb_06 (dispatcher score) + Sb_08 (confidence) termines.

**Criteres d'acceptation :**
- Seances cardio n'apparaissent plus comme "faibles" dans les timelines globales
- Distinction visuelle claire strength vs cardio si les deux coexistent
- Aucune regression sur les dashboards existants
- Export schema documente

**Risques :**
- Rupture visuelle abrupte pour users existants → option de vue unifiee preservee si besoin

**Effort estime :** 3-5h.

---

## Ordre recommande d'execution

```
Maintenant (SPEC)
  1. Sx_05 VALIDE (ce sprint)
  2. Sx_06  Scoring/Load/Time Semantics
  3. Sx_07  Machine Atlas + Substitution UX     [parallelisable avec Sx_08]
  4. Sx_08  Session Review Intelligence          [parallelisable avec Sx_07]
  5. Sx_09  Consolidation

Ensuite (BUILD — ordre strict)
  6. Sb_06  Scoring/Load/Time                    [BUGS PRIORITAIRES + SCORING SEPARATION]
  7. Sb_05  Session Flow Horizontal              [refactor UX sur base data saine]
  8. Sb_07  Machine Knowledge                    [integration dans nouveau flow]
  9. Sb_08  Session Review                       [enrichissement terminal]
  10. Sb_09 History Visual                       [alignement transverse final]
```

**Justification de l'ordre build :**
- **Sb_06 avant Sb_05** : corriger B01/B02/B03 d'abord pour ne pas refaire UX sur data cassee
- **Sb_07 apres Sb_05** : atlas s'integre proprement dans nouveau flow carte-par-carte
- **Sb_08 apres Sb_07** : session review enrichie utilise les donnees machine (via `actual_exercise_name` + machine_family)
- **Sb_09 dernier** : aligne visuels globaux avec toutes les nouvelles semantiques

---

## Recapitulatif effort total

| Phase | Sprint | Effort estime |
|-------|--------|---------------|
| Spec | Sx_05 | Fait (ce sprint) |
| Spec | Sx_06 | 2-3h |
| Spec | Sx_07 | 3-4h |
| Spec | Sx_08 | 2-3h |
| Spec | Sx_09 | 1-2h |
| Build | Sb_06 | 5-7h |
| Build | Sb_05 | 4-6h |
| Build | Sb_07 | 6-8h |
| Build | Sb_08 | 4-6h |
| Build | Sb_09 | 3-5h |
| **TOTAL** | | **~30-44h** |

Cycle complet (spec + build) realiste en 2-3 semaines d'effort produit concentre.

---

## Regle de stop

Si un sprint de spec revele une contradiction avec un sprint precedent verrouille :
1. **Ne pas coder**
2. Produire un **spec de reconciliation** explicite
3. Revalider avec humain avant de continuer

Aucun build ne demarre sans **OK explicite** humain sur sa spec.
