# Sprint Sx_21 Spec Report — Dogfooding Generalization

**Date :** 2026-05-09
**Type :** SPEC ONLY — méta-spec + 3 specs aval (Sx_22a, Sx_22b, Sx_23).
**Prérequis :** Cycle Sx_20 clos (CI gate verte).
**Successeurs build :** Sb_22a (substitution gap pack), Sb_22b (profile synthesis v2), Sb_23 (coach report).

---

## 1. Résumé exécutif

Le cycle de dogfooding a généré un signal clair : **les retours répétés (N3 textarea, N4 adduction, N5 pull B) ne sont pas des bugs locaux mais des manifestations d'absence de modèle systémique**. Patch local OK pour Sb_dogfood_fixpack v1 et catalog_v13, mais après 6 sprints de patch, le même type de retour réapparaît parce qu'on n'a jamais fermé la **classe** de problème.

Sx_21 monte d'un cran d'abstraction et produit :
1. Une **méta-spec** pour classifier tout futur retour dogfooding (`SPIGNOS_DOGFOODING_GENERALIZATION_SPEC_v1.md`).
2. Une **spec substitution** qui remplace le graphe ad hoc par une heuristique zone/pattern/équipement avec 3 niveaux N1/N2/N3 (`SPIGNOS_SUBSTITUTION_GAP_PACK_SPEC_v1.md`).
3. Une **spec profile synthesis v2** qui élève leaderboard+profil en synthèse à 3 niveaux (ligne → preview card → page) sans redondance dataviz (`SPIGNOS_PROFILE_SYNTHESIS_SPEC_v2.md`).
4. Une **spec nouvelle feature Coach Report** qui produit un rapport SSR + print imprimable en 2 min de lecture (`SPIGNOS_COACH_REPORT_SPEC_v1.md`).

**Aucune ligne de code applicatif touchée dans Sx_21.** Le ROI vient de l'ouverture du cycle Sb_22+ ciblé.

## 2. Fichiers créés

| Fichier | Type | Cible |
|---------|------|-------|
| `docs/strategy/SPIGNOS_DOGFOODING_GENERALIZATION_SPEC_v1.md` | New | Méta-spec Sx_21 |
| `docs/strategy/SPIGNOS_SUBSTITUTION_GAP_PACK_SPEC_v1.md` | New | Spec Sx_22a |
| `docs/strategy/SPIGNOS_PROFILE_SYNTHESIS_SPEC_v2.md` | New | Spec Sx_22b |
| `docs/strategy/SPIGNOS_COACH_REPORT_SPEC_v1.md` | New | Spec Sx_23 |
| `docs/SPRINT_Sx_21_dogfooding_generalization_REPORT.md` | New | Ce rapport |

5 fichiers documentation, 0 ligne app/ modifiée.

## 3. Trois constats systémiques tirés du dogfooding

### 3.1 — Le graphe de substitution est ad hoc et insuffisant

Audit `reference_split.json` v13 :
- **48 exercices sur 95 (51 %) n'ont aucune alternative** explicite.
- 4 templates entiers (`upper-pecs-delts`, `upper-back-arms`, `lower-quad-bias`, `lower-posterior-bias`) sont à 0 substitution.
- C1/C2 du dogfood corrigent 2 cas spécifiques mais laissent la classe ouverte.

**Décision :** Sx_22a — heuristique zone/pattern/équipement + 12-15 cross-pattern manuels haute valeur.

### 3.2 — Le leaderboard/profil livre des features sans hiérarchie

Sb_19 livre hover radar + page profil mais :
- Score affiché 2-3 fois (badge + au-dessus + au centre du radar).
- Pas de preview card intermédiaire — soit hover éphémère soit clic full-page.
- Mobile = pas de hover, donc seul le clic est disponible.

**Décision :** Sx_22b — 3 niveaux explicites (ligne, preview card 280×320, page synthèse), pattern preview-vs-clic mobile/desktop unifié, score unique par niveau.

### 3.3 — Pas de surface "synthèse coach"

Aucune page ne donne à un coach externe (ou à l'user lui-même en mode bilan) une vue d'ensemble lisible en 2 min. Le dashboard SPIGNOS demande 5 pages à naviguer.

**Décision :** Sx_23 — nouvelle feature `/coach-report` avec 10 blocs structurés (identité physique, volume, ratio, zones, patterns, discipline, points forts/faibles probables, axes), CSS print + garde-fou anti-interprétation médicale.

## 4. Modèle de classification adopté (cf §C de la méta-spec)

Chaque retour dogfooding est désormais étiqueté :

1. Bug réel
2. Lacune UX
3. Lacune de recommandation
4. Lacune de graphe de substitution
5. Lacune de synthèse analytics
6. Lacune de modèle de signal

Un retour n'est pas "fixé" tant que sa **classe** n'a pas été adressée. Cette règle clôt le pattern "le user re-signale N3/N4/N5 après le fix local".

## 5. Critère patch local vs spec système

Si 2+ critères ci-dessous sont remplis → spec système requise :

- ≥ 2 retours similaires
- Coût patch > 1 h ou récurrent
- Risque de récurrence élevé
- Surface ≥ 3 fichiers
- Demande coach/expert externe

## 6. Ordre de sprint build proposé après Sx_21

### Sprint 1 — Sb_22a · Substitution Gap Pack (~16 h sur 2 sem)

| Phase | Sujet | Effort |
|---|---|---|
| Sb_22a.1 | Enrichir catalogue (pattern_motor, chain_type, equipment_family) | 6 h |
| Sb_22a.2 | `cross_pattern_substitutions.json` (12-15 entrées) | 3 h |
| Sb_22a.3 | Trous critiques upper/lower-* manuels (~48 substitutions) | 4 h |
| Sb_22a.4 | Drawer UI 3 niveaux + badges | 3 h |

**Effet :** 100 % des exos strength obtiennent ≥ 1 suggestion (vs 49 % aujourd'hui).

### Sprint 2 — Sb_22b · Profile Synthesis v2 (~12 h sur 1 sem)

| Phase | Sujet | Effort |
|---|---|---|
| Sb_22b.1 | `profile_metrics.py` + tests | 3 h |
| Sb_22b.2 | Refonte page `/users/{username}` niveau 3 | 3 h |
| Sb_22b.3 | Endpoint `/preview` + partial | 2 h |
| Sb_22b.4 | JS `preview.js` mobile/desktop | 3 h |
| Sb_22b.5 | Suppression score centre radar (B3 v2) | 1 h |

**Effet :** synthèse à 3 niveaux, 1 score par niveau, mobile-first.

### Sprint 3 — Sb_23 · Coach Report (~18 h sur 2 sem)

| Phase | Sujet | Effort |
|---|---|---|
| Sb_23.1 | `profile_metrics.py` étendu | 3 h |
| Sb_23.2 | `coach_report.py` orchestration | 3 h |
| Sb_23.3 | `coach_inference.py` règles déterministes points forts/faibles | 4 h |
| Sb_23.4 | Templates 10 blocs + CSS print A4 | 5 h |
| Sb_23.5 | Tests E2E + ownership | 2 h |
| Sb_23.6 | Sprint report | 1 h |

**Effet :** page `/coach-report` imprimable, lisible en 2 min.

### Effort cumulé Sx_22 + Sx_23 build : ~46 h sur 5-6 semaines

À condition de :
- Ne pas mener les 3 sprints en parallèle (Sb_22a et Sb_22b peuvent l'être ; Sb_23 dépend de `profile_metrics` partagé).
- Garder une passe dogfood entre chaque sprint pour valider en vrai.

## 7. Garde-fous reportés depuis la méta-spec

- **Étiquettes obligatoires** `Constaté` / `Calculé` / `Hypothèse` sur toutes les sorties des futurs builds.
- **Historique propre** — aucun chantier ne réécrit les sessions passées.
- **Mobile-first** — toute affordance hover desktop doit avoir un équivalent tap mobile.
- **Re-test obligatoire** — chaque retour clos n'est validé qu'après re-test prod (cf N1-N5 re-signalés faute de re-test).
- **Lotissement** — pas plus d'un chantier de spec par semaine, pas plus d'un build par sprint.

## 8. Limites assumées Sx_21

1. **Pas de chiffrage user research formel** — les retours dogfooding restent issus du seul utilisateur principal. Volume de signal limité.
2. **Pas de roadmap business** — Sx_21 reste produit/technique. Le modèle de monétisation (coach payant ? partage premium ?) n'est pas traité.
3. **Pas de spec UX detailled mocks** — chaque spec aval contient des wireframes ASCII, pas de Figma. Le design fin viendra avec chaque build.
4. **Pas de migration BD planifiée V1** — un seul ajout candidat dans Sx_23 (`users.year_of_birth`), optionnel.
5. **Pas de chantier reco V3 narratif** — listé en backlog Sx_24 mais non spec dans ce cycle (dépend de la télémétrie Sb_18 sur 30j minimum).

## 9. Acceptance criteria Sx_21

- [x] Méta-spec dogfooding generalization livrée (`SPIGNOS_DOGFOODING_GENERALIZATION_SPEC_v1.md`).
- [x] Spec substitution gap pack livrée (`SPIGNOS_SUBSTITUTION_GAP_PACK_SPEC_v1.md`).
- [x] Spec profile synthesis v2 livrée (`SPIGNOS_PROFILE_SYNTHESIS_SPEC_v2.md`).
- [x] Spec coach report v1 livrée (`SPIGNOS_COACH_REPORT_SPEC_v1.md`).
- [x] Sprint report livré (ce fichier).
- [x] Ordre de sprint build proposé §6.

## 10. Synthèse

- **0 ligne app/ touchée.**
- **4 specs livrées + 1 sprint report** = 5 documents.
- **Ouvre 3 chantiers build** (Sb_22a, Sb_22b, Sb_23) pour ~46 h cumulées.
- **Élève les retours dogfooding** de tickets locaux à classes de problèmes système.
- **SPRINT_INDEX.md à mettre à jour** dans le prochain commit qui ouvre Sb_22a (pas dans Sx_21 pour garder le cycle spec pur).

Sx_21 est techniquement clos. Décision produit attendue : **par quel build commencer ?** Recommandation = Sb_22a (substitution) parce que c'est le retour le plus récurrent et qui débloque la confiance utilisateur dans le catalogue.
