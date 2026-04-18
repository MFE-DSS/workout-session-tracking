# Sprint Sx_05 Report — Session Flow & Intelligence Spec

**Date:** 2026-04-15
**Type:** SPEC ONLY — aucun build
**Prerequisite:** cycle catalogue v10 clos
**Suivi par:** Sx_06 (Scoring, Load, Time Semantics Spec)

---

## Objectif

Ouvrir le chantier post-v10 en posant un cadrage discipline : mutation logger vertical → seance guidee carte-par-carte, integration feedback terrain reel (10 problemes produit), preparation de la couche intelligence sans la coder, queue build executable.

---

## Ce que j'ai inspecte reellement dans le repo

### Fichiers consultes

| Fichier | Lignes | Role audite |
|---------|--------|-------------|
| `app/routers/sessions.py` | 511 lignes | Route session_detail GET (155-274), update_session POST (329-360), update_exercise_card POST (363-430) |
| `app/templates/session_detail.html` | 411 lignes | Structure UI actuelle : jump bar, `<details>` par exercice, forme par carte, session feedback en bas |
| `app/models/session.py` | ~210 lignes | WorkoutSession + SessionExercise + SetLog + snapshots immutables |
| `app/services/quality_score.py` | 88 lignes | Formule unique `compute_session_quality` |
| `app/services/feedback.py` | 85 lignes | `compute_success_score` derive |
| `app/services/form_parsing.py` | 70 lignes | `to_float`, `to_int`, enum helpers |
| `app/services/session_recap.py` | ~100 lignes | `build_recap` pour /done |
| `app/services/substitution.py` | 36 lignes | `actual_exercise_name`, `get_substitutes`, `can_substitute` |
| `app/services/timeline.py` | — | Visualisations globales |
| `data/reference_split.json` | v10 | Catalogue actuel |

### Grep/search utilises

- `grep type="number"` dans templates → 4 endroits confirmant B01
- `grep datetime.now\|timezone` dans routers → confirmation B02 (UTC storage correct mais rendu non localise)
- `grep success_score\|quality_score` → confirmation B03 (formule ne distingue pas kind)
- `grep substituted_name\|actual_exercise_name` → confirmation architecture substitution OK

---

## Surfaces concretes reperees

| Surface | Fichier + Lignes | Impact Sx_05+ |
|---------|------------------|---------------|
| Jump bar 4 etats | session_detail.html L29-45 | Garder (Sb_02.1) |
| Cards `<details>` avec active_exercise_id | session_detail.html L52-275 | Refactor layout en Sb_05 (horizontal + save-on-next) |
| Form exercise card (submit manuel) | session_detail.html L66-273 + sessions.py L363-430 | Save-on-next = reutiliser route existante avec CTA "Suivant" |
| Inputs type=number | session_detail.html L177-232, L307-317 | B01 fix vers type=text inputmode=decimal |
| Timezone rendu | sessions.py L95 (storage UTC OK), templates started_at/ended_at | B02 fix conversion locale |
| Scoring | quality_score.py L44-87 | B03 refactor dispatcher strength/cardio |
| Notes libres | session_detail.html textareas | C03 reduction inline |
| Substitution picker | session_detail.html L98-123 | Maintenir garde-fous Sx_02 + refonte visuelle drawer en Sb_07 |
| Timeline / sparkline | timeline.py + index.html + progress.html | B04 fix via dispatcher en Sb_09 |

---

## Hypotheses que j'ai du faire

### H1 — Horizontal via CSS, pas JS

Hypothese : on peut passer a un layout carte-par-carte horizontal uniquement via CSS (scroll-snap horizontal) + `<details open>` serveur, sans JS. A valider dans Sx_09 / Sb_05 avec un prototype.

**Risque si faux :** besoin de JS minimal (progressive enhancement) pour gerer le swipe. Acceptable dans la grammaire SSR existante si fallback sans JS preserve.

### H2 — Save-on-next = bouton "Suivant" explicite, pas swipe auto

Hypothese : le save-on-next V1 passe par un bouton "Suivant" explicite (evolution du CTA actuel "Enregistrer et passer a E2" → juste "Suivant →"). Pas de swipe auto qui save sans clic.

**Justification :** swipe sans clic peut provoquer des saves accidentels. Bouton explicite reste predictible. Le gain UX = suppression du bouton "Enregistrer" separe de la navigation.

### H3 — Convention charge canonique = "comme sur l'equipement"

Hypothese : la regle la plus intuitive est "saisir comme sur l'equipement" (par cote halteres/independantes, total bilaterales fixes). Valide terrain mais necessite confirmation user pour Sx_06.

### H4 — Atlas machine = fichier JSON separe

Hypothese : `data/machine_atlas.json` independant de `reference_split.json` pour isoler la gouvernance catalogue exercice et la gouvernance atlas machine.

**Alternative :** section `machines` top-level dans reference_split. Decide dans Sx_07.

### H5 — Intelligence layer = pur deterministe V1

Hypothese : aucune ML / LLM dans l'intelligence layer V1. Uniquement des regles deterministes (seuils, compares, comptages). Aligne avec le principe "no AI magic" des sprints precedents.

---

## Decisions de cadrage prises

### D1 — Vocabulaire canonique figue

Spec §P : prevu / realise / vignette / carte active / done / future / substitution / save-on-next / charge canonique / scoring strength vs cardio / machine family knowledge / session review intelligence.

Reutilises obligatoirement dans Sx_06 → Sb_09.

### D2 — Ordre spec avant build

Phase spec complete (Sx_05→Sx_09) avant tout build (Sb_05→Sb_09). Aucune exception.

### D3 — Ordre build : bugs & semantique avant UX

Sb_06 (bugs B01/B02/B03 + charges + scoring cardio) **avant** Sb_05 (refactor UX). Eviter de refaire l'UX sur des donnees semantiquement cassees.

### D4 — Intelligence layer preparee, pas promise

§K de la spec : cadrage des 4 couches (I01 incoherences, I02 rapport auto, I03 hints, I04 confidence) sans engagement de build immediat. Sb_08 minimal V1 avec 3-5 regles.

### D5 — Snapshots immutables restent la regle d'or

Zero migration destructive dans tout le cycle Sx_05→Sb_09. Historique preserve par design.

### D6 — Atlas V1 borne

Maximum 30 machines V1, 5-8 familles. Pas de prose encyclopedique. Visuel possible mais optionnel V1.

### D7 — Save-on-next = bouton explicite

Pas de swipe auto en V1. Bouton "Suivant →" explicite remplace "Enregistrer et passer a E2" mais reste declenche par tap conscient.

### D8 — Scoring LISS : plafond effectif >= 80 pour seance bien faite

Formule cardio §H.3 : 20min dans zone cible + subjective OK = score >= 80.

---

## Conflits ou incertitudes restants

### Q1 — Convention charge bilaterale

La regle "comme sur l'equipement" est simple mais pas universelle. Par exemple, une **machine shoulder press a bras independants** : 30 kg = 30 par bras (total 60). Certains users pourraient saisir 60.

**A arbitrer dans Sx_06 :**
- Confirmation regle canonique
- Gestion edge cases (machines mixtes)
- Besoin ou non d'un champ `load_semantics` dans catalogue (`per_side` / `total`)

### Q2 — Save-on-next sur "Precedent"

Que faire si user tape Precedent apres avoir modifie la carte actuelle ?
- **Option A :** save silencieux + navigation
- **Option B :** warning "Des modifs non sauvegardees..." (mais necessite JS ou `<dialog>` SSR)
- **Option C :** navigation sans save (perte de modif)

**A arbitrer dans Sx_05 ou Sb_05 :** probablement Option A (save silencieux), coherent avec save-on-next.

### Q3 — Timezone : defaut ou preference

V1 peut etre :
- **Simple :** defaut Europe/Paris en dur
- **Intermediaire :** preference user sauvegardee
- **Complet :** detection auto navigateur + override manuel

**A arbitrer dans Sx_06.** Probablement intermediaire (column `users.timezone` nullable, defaut Europe/Paris si null).

### Q4 — Reduction notes inline : jusqu'ou ?

`free_note` par exercice : le retirer completement du body ou le garder collapse ? Impact : users qui utilisaient ce champ perdent visibilite.

**A arbitrer dans Sx_08.** Probablement "collapse dans `<details>` optionnel" pour preserver la donnee existante.

### Q5 — Atlas machine : DB-backed ou in-memory

Charger l'atlas en DB via seed OU le garder en memoire (lecture directe du JSON a chaque request) ?

**A arbitrer dans Sx_07.** Probablement in-memory V1 (simple, suffit, pas de migration).

### Q6 — Parallelisation Sx_07 et Sx_08

Theoriquement parallelisables (domaines disjoints : atlas vs review). En pratique, si un seul developpeur travaille, faire en sequence. OK documente.

---

## Pourquoi la queue proposee est la bonne

### Criteres d'ordonnancement

1. **Semantique avant UX** : corriger B01/B02/B03 + scoring cardio avant de refactorer l'UX → Sb_06 avant Sb_05
2. **Donnees avant surface** : atlas machine + substitution avant session review (review utilise les donnees enrichies) → Sb_07 avant Sb_08
3. **Integration avant alignement global** : session review enrichie avant visuels globaux → Sb_08 avant Sb_09
4. **Consolidation avant builds** : Sx_09 consolide toutes les specs avant phase build

### Validation par test

Le scenario user "je suis au gym, je charge des halteres 12,5 kg, je termine ma seance LISS bien faite" doit :
- Fonctionner techniquement (B01 fix) ✓ via Sb_06
- Etre visible avec la bonne date (B02 fix) ✓ via Sb_06
- Etre score correctement (B03 fix) ✓ via Sb_06
- Etre saisi dans un flow fluide (Sb_05) ✓
- Etre accompagne d'info machine si besoin (Sb_07) ✓
- Recevoir une synthese utile a la fin (Sb_08) ✓
- Etre represente fidelement dans les timelines (Sb_09) ✓

Chaque sprint adresse un angle. L'ordre construit progressivement l'experience cible.

---

## Ce qui doit imperativement etre traite avant de passer en build

### Avant Sb_06

1. ✅ Sx_05 valide (ce sprint)
2. Sx_06 valide (detail des 3 chantiers semantiques)
3. Confirmation user sur convention charge canonique (Q1)
4. Confirmation strategie timezone (Q3)

### Avant Sb_05

1. Sb_06 **build termine et deploye**
2. Sx_05 + Sx_06 valides

### Avant Sb_07

1. Sb_05 termine (nouveau flow en place)
2. Sx_07 valide (schema atlas + UX panneau `i`)
3. Catalogue atlas V1 (30 machines) redige

### Avant Sb_08

1. Sb_05 + Sb_06 + Sb_07 termines
2. Sx_08 valide (5 regles anomalies documentees, structure synthese)

### Avant Sb_09

1. Tous les Sb precedents termines
2. Sx_09 valide (matrice compatibilite)

---

## Fichiers crees dans ce sprint

| Fichier | Lignes | Nature |
|---------|--------|--------|
| `docs/strategy/SPIGNOS_SESSION_FLOW_AND_INTELLIGENCE_SPEC_v1.md` | ~600 | Spec principale cadrage |
| `docs/strategy/SPIGNOS_SESSION_SYSTEM_SPRINT_QUEUE_v1.md` | ~400 | Queue 5 spec + 5 build ordonnee |
| `docs/SPRINT_Sx_05_session_flow_and_intelligence_spec_REPORT.md` | ~300 | Ce rapport |

**Zero fichier code modifie.**

---

## Recommandation explicite du prochain sprint

**Apres validation humaine de Sx_05, lancer immediatement Sx_06** — `SPIGNOS_SCORING_LOAD_TIME_SEMANTICS_SPEC_v1.md`.

Pourquoi Sx_06 en priorite :
- Traite les 3 bugs de fond (B01/B02/B03) qui sont les plus douloureux en production
- Produit les decisions semantiques dont Sb_05 aura besoin
- Peut etre produit en 2-3h de spec
- Debloque Sb_06 (premier build du cycle)

Sx_07 et Sx_08 peuvent etre produits en parallele apres Sx_06 valide.

---

## Questions a trancher avec humain avant Sx_06

- [ ] Q1 : convention charge canonique "comme sur l'equipement" acceptee ?
- [ ] Q3 : timezone defaut Europe/Paris + preference user simple ou simple hardcode ?
- [ ] Q8 : scoring cardio plafond 80 pour 20min zone cible — valeur acceptable ?
- [ ] Confirmation : pas de migration DB dans le cycle Sx_05→Sb_09

---

## Synthese executive (5 lignes)

- Cycle catalogue v10 clos. Nouveau chantier Sx_05 ouvre mutation logger vertical → seance guidee carte-par-carte
- Spec principale 15 sections ; couverture exhaustive des 10 problemes produit identifies terrain
- Sprint queue 5 spec + 5 build ordonnees, avec justification d'ordre semantique-avant-UX
- Preparation intelligence layer sans sur-promesse (4 couches cadrees, aucune implementation)
- Prochaine action : Sx_06 Scoring/Load/Time Semantics pour debloquer Sb_06 (bugs prioritaires)
