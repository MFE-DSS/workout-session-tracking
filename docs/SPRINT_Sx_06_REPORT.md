# Sprint Sx_06 Report — Scoring, Load & Time Semantics Spec

**Date:** 2026-04-15
**Type:** SPEC ONLY — aucun build
**Prerequisite:** Sx_05 valide
**Debloque:** Sb_06 (premier build du cycle post-v10)

---

## Objectif

Specifier les 3 chantiers semantiques que Sb_06 implementera avant la refacto UX :
1. Convention canonique charges (C02 + C05) + fix B01 decimales
2. Dispatcher scoring strength vs cardio (B03)
3. Rendu timezone utilisateur (B02)

---

## Travail effectue

### Audit repo complementaire

| Surface | Fichier + Lignes | Constat |
|---------|------------------|---------|
| Storage timezone | `app/routers/sessions.py:95, 173, 363` | `datetime.now(timezone.utc)` → stockage UTC correct |
| Rendu dates | `session_detail.html:13`, `session_done.html:10, 12`, `history.html:37` | `strftime` direct sans conversion locale → bug B02 |
| Cardio fields | `app/models/session.py:103-106` | `cardio_duration_min`, `cardio_bpm_avg`, `cardio_machine_calories`, `cardio_machine_type` → signaux disponibles |
| Form parsing | `app/services/form_parsing.py:28-34` | `to_float` tolere deja virgule (`.replace(",", ".")`) |
| Input types | `session_detail.html:177-232, 307-317, 348-353` | 4 zones avec `type="number"` → bloque virgule cote navigateur |
| Quality score | `app/services/quality_score.py:44-87` | Formule unique melangee, success_score NULL pour cardio → plafond ~60 |

### Decisions prises

**D1 — Convention charge canonique** : "saisir comme affiche sur l'equipement"
- Halteres : un seul haltere
- Machines a bras independants : par cote
- Machines bilaterales fixes : total
- Cable : poids pile
- Poids corps : externe ajoute

**D2 — B01 fix technique** : migration `type="number"` → `type="text" inputmode="decimal" pattern="[0-9]*[.,]?[0-9]*"` dans 4 endroits UI. Backend deja robuste.

**D3 — Scoring dispatcher** : `compute_session_quality(session)` dispatch via `template.kind` ; formule strength inchangee, nouvelle formule cardio.

**D4 — Formule cardio V1** : 50 duration + 20 intensity + 20 completion + 10 subjective = 100 max. Plafond effectif LISS 20min zone cible : >= 85.

**D5 — Timezone V1** : stockage UTC conserve. Helper Jinja `local` filter avec defaut Europe/Paris. Preference user differee V2.

**D6 — `template_kind_snapshot` differe** : V1 alternative sans migration (`session.template.kind if session.template else "strength"`). Acceptable. Migration additive possible V2.

**D7 — `load_semantics` catalogue differe** : V1 sans champ. V2 potentiel couple avec Sx_07 (machine atlas) si souhaite.

### Contenu spec produit

Spec principale `SPIGNOS_SCORING_LOAD_TIME_SEMANTICS_SPEC_v1.md` — 10 sections :

1. Objet et scope
2. Chantier A — Convention charge canonique (6 sous-sections + fix B01)
3. Chantier B — Dispatcher scoring (8 sous-sections avec formules, impacts consumers)
4. Chantier C — Timezone (6 sous-sections)
5. Ordre de fix Sb_06 (6 etapes committables)
6. Tests prevus (unit + regression + recette)
7. Risques et mitigation
8. Impacts consumers non listes dans Sx_05
9. Ouvertures Sx_07 + Sx_08
10. Acceptance criteria + synthese

---

## Hypotheses validees / a confirmer

### Validees via audit

- ✅ Backend `to_float` deja tolere virgule (confirme par grep ligne 32 de form_parsing.py)
- ✅ Storage UTC correct (confirme 3 emplacements dans sessions.py)
- ✅ Rendu templates sans conversion locale (confirme 4 templates)
- ✅ Cardio fields existants et suffisants pour scoring V1

### A confirmer par le user

Questions de Sx_05 restees ouvertes :

- [ ] **Q1** Convention charge "comme affiche" acceptee ? → **defaut pris dans Sx_06 §1.2**
- [ ] **Q3** Timezone defaut Europe/Paris V1, preference user V2 ? → **defaut pris dans Sx_06 §3.3**
- [ ] **Q8** Plafond LISS bien fait >= 85 (vs 80 initial) ? → **defaut pris dans Sx_06 §2.4 avec exemple chiffre**
- [ ] Confirmation : aucune migration DB V1 ? → **defaut pris, migration additive possible V2**

---

## Decisions restees ouvertes (pour Sx_07/Sx_08)

- `load_semantics` champ catalogue : a arbitrer dans Sx_07 si Machine Atlas introduit un schema catalogue riche
- `template_kind_snapshot` migration : a arbitrer dans Sx_09 consolidation si besoin remonte
- Wording helper text exact ("comme affiche", "sur l'equipement", autre) : a ajuster a Sb_06 via recette terrain

---

## Fichiers crees

| Fichier | Lignes | Nature |
|---------|--------|--------|
| `docs/strategy/SPIGNOS_SCORING_LOAD_TIME_SEMANTICS_SPEC_v1.md` | ~550 | Spec detaillee |
| `docs/SPRINT_Sx_06_REPORT.md` | ~200 | Ce rapport |

**Zero fichier code modifie.** SPEC ONLY.

---

## Pourquoi cette spec debloque Sb_06

Sb_06 est le **premier build du cycle** parce que :

1. **B01/B02/B03 sont les bugs les plus douloureux** en production (decimales, date fausse, LISS sous-note)
2. Aucune de ces corrections ne touche a la structure UX → peut preceder Sb_05
3. Refacto UX Sb_05 ensuite partira de donnees semantiquement saines
4. Les decisions `load_semantics` / `template_kind_snapshot` sont defered → Sb_06 reste petit et executable en ~5-7h

---

## Plan d'execution Sb_06 (apres OK humain)

1. Etape 1 — B01 decimales (commit isole, ~30 min)
2. Etape 2 — B02 timezone (commit isole, ~1h30)
3. Etape 3 — B03 scoring dispatcher (commit isole, ~2h)
4. Etape 4 — C05 helper text (commit isole, ~30 min)
5. Etape 5 — Documentation (commit isole, ~30 min)
6. Etape 6 — Sprint report + merge (~30 min)

**Total estime : 5-6h.**

---

## Recommandation explicite du prochain sprint

**Apres validation humaine Sx_06 + reponses aux 4 questions ouvertes :**

- Option A — Lancer **Sb_06 directement** (execute 3 bugs prioritaires avant de continuer la phase spec)
- Option B — Continuer phase spec avec **Sx_07 (Machine Atlas)** et **Sx_08 (Session Review)** en parallele, puis revenir a la phase build en une passe

**Ma recommandation : Option A.**

Raisons :
- Sb_06 traite des bugs critiques terrain (decimales/timezone/scoring) → gain produit immediat
- Sb_06 est petit, bien borne, zero migration
- Feedback utilisateur Sb_06 peut eclairer Sx_07/Sx_08 (notamment si helper text + convention charge necessitent ajustement)
- La discipline "spec before build" n'est pas violee : Sx_06 est complet, Sb_06 est executable

Option B reste valide si tu preferes finir toute la phase spec avant tout code (discipline stricte Sx_05 → Sx_09 puis Sb_05 → Sb_09).

---

## Synthese executive (5 lignes)

- Sx_06 specifie 3 chantiers semantiques : charges canoniques, scoring cardio separe, timezone
- B01 fix simple (HTML input type) ; B02 fix via helper Jinja ; B03 refactor dispatcher
- Convention "comme affiche sur l'equipement" tranchee, rappel UI discret
- Formule cardio V1 (4 composants) plafonne LISS 20min zone cible a >= 85/100
- Zero migration V1, Sb_06 executable en 5-6h, debloque le premier build du cycle
