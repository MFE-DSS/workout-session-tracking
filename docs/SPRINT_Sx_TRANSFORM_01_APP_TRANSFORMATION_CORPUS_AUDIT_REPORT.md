# Sprint Sx_TRANSFORM_01 — App Transformation Corpus (AUDIT)

**Statut** : 🟢 AUDIT COMPLET — READY FOR HUMAN DECISION
**Type** : AUDIT / STRATEGY ONLY — docs-only, **aucun code**
**Date** : 2026-07-11
**Document maître** : [`strategy/Sx_TRANSFORM_01_APP_TRANSFORMATION_CONSOLIDATION_SPEC.md`](strategy/Sx_TRANSFORM_01_APP_TRANSFORMATION_CONSOLIDATION_SPEC.md)

---

## 0. Méthode

Audit **read-only** du corpus de transformation / stratégie et de son alignement
avec les sprints livrés (Sx_UI_06, Sx_DOGFOOD_01, Sx_BI_01). Objectif : identifier
le vocabulaire dispersé, les contradictions, les passages à figer/interdire, avant
de produire le **document maître** (Option A). Aucun fichier source modifié.

---

## 1. Documents sources audités (cités)

| Document | Rôle | Constat |
|---|---|---|
| `docs/strategy/UI_TRANSFORMATION_ROADMAP.md` | Roadmap UI maître (Sx_UI_01→11) | Priorités + garde-fous **déjà figés** : « SSR FastAPI + Jinja conservé, no-JS fallback préservé, aucun changement de stack (pas de React, pas de SPA, pas de bundler) ». Rebrand `Sx_UI_10` uniquement post-`Sx_UI_04`. Un seul accent. |
| `docs/strategy/Sx_UI_02b_AUREN_TERMINAL_SPEC.md` | Direction visuelle active | **Révise Sx_UI_02** (2026-07-07) : Clinical Lab clair + teal → **Auren Terminal** (graphite `#0A0C0F`→`#1B2029`, tout-mono, accent ambre `#C8A24B` unique). « dark devient l'identité primaire » (pas une option). |
| `docs/strategy/SPIGNOS_CATALOG_BENCHMARK_REVIEW_v1.md` | Benchmark robustesse catalogue | Direction robustesse opérationnelle ; « Pas de code Python à modifier ». Nom **SPIGNOS/Spignos** (jamais « Spinos »). |
| `docs/strategy/SPIGNOS_Sb_R3_TERMINAL_STATE_PLAN.md` | Plan d'état terminal séance | Adaptation séance réel-terrain ; s'articule avec Auren Terminal. |
| `docs/strategy/brainstorm/UI_TRANSFORMATION_BRAINSTORM_V1_normalized.md` | Idées brutes V1 | Direction initiale « Clinical Lab blanc » + finalistes de nom (Teral / Nerva / **Auren**). « la bonne trajectoire n'est pas React Native, ni SPA obligatoire… app web installable d'abord ». |
| `docs/strategy/brainstorm/UI_TRANSFORMATION_BRAINSTORM_V2_normalized.md` | Idées brutes V2 | Séance = meilleur point d'appui. PWA-first ; « pas React Native ni Flutter ». |
| `docs/strategy/SPEC_REGISTRY.md` | Registre des specs | Trace la révision Sx_UI_02 → Sx_UI_02b et les statuts. |
| `docs/strategy/ROADMAP_AND_NEXT_STEPS.md` | Roadmap opérationnelle | Prochaine action + deferred ; réaligné à chaque sprint. |
| Sx_UI_06 (closeout / registry) | Dé-densification | Home + cartes exercice + Worked Area allégées. |
| Sx_DOGFOOD_01 (closeout) | Cohérence charge/substitution | Règle « silence plutôt que faux poids » ; placeholders compacts mobile. |
| Sx_BI_01 (spec/audit) | Reprise Body Intelligence | BI pas greenfield ; `/physique` score opaque LIVE ; **Option A zone cards** ; pas de 2e score opaque. |

---

## 2. Vocabulaire (drift constaté)

| Nom | Où | Statut acté |
|---|---|---|
| **SPIGNOS** | 80+ occurrences (code, benchmarks, gouvernance) | **Nom historique / repo / domaine fonctionnel** — reste dans le code |
| **Spignos** | variante de casse (docs formels) | idem (référence formelle) |
| **Spinos** | **absent du corpus** | variante fantôme — **ne pas introduire** |
| **Auren** | 40+ (roadmap UI, specs, brainstorms) | **Direction produit / UI** — pas encore dans le code (réservé `Sx_UI_10`) |
| **Auren Terminal** | 15+ (Sx_UI_02b, roadmap) | **Codename de l'identité visuelle** (dark/mono/amber) |

→ Décision (doc maître §1) : **SPIGNOS** (repo) vs **Auren** (produit) vs **Auren
Terminal** (identité), séparés une fois pour toutes.

---

## 3. Contradictions identifiées → statut

| Contradiction | Statut réel | Traitement dans le maître |
|---|---|---|
| White clinical vs Auren Terminal dark | **Déjà résolue** (Sx_UI_02 → Sx_UI_02b, 2026-07-07, **livré**) | Actée comme **amendement daté** (§7), pas re-débattue |
| React Native future vs React interdit | Gouvernance : **React interdit repo** ; mentions React = **rejets** | Encadré « hors repo », PWA-first (§4, §8) |
| Dashboard riche vs app minimaliste | App minimaliste ; Home dé-densifiée (Sx_UI_06) | Principe actif « ne pas re-densifier » (§5) |
| Score global opaque vs zone cards | `/physique` score A/B/C **LIVE** ; BI = zone cards (Sx_BI_01) | « Pas de 2e score opaque » (§5, §7) |
| BI flag-off vs `/physique` live | Composer `/body/intelligence` flag-off ; `/physique` live | Acté (§7) ; reprise = zone cards sur `/body/intelligence` |

---

## 4. Passages à figer (principes actifs) vs interdire

**À figer (principes actifs — doc maître §5)** : SSR/Jinja · mobile-first · no-JS
fallback · une décision par écran · silence plutôt que faux poids · pas de score
opaque · confidence visible · non-médical explicite · ne pas re-densifier la home ·
un seul accent · placeholder = indication légère.

**À interdire (doc maître §8)** : React / SPA / bundler · big-bang redesign · claims
médicaux / diagnostic corporel · dashboard trop dense · 2e accent · mutation métier
en sprint UI · nouveau score opaque.

---

## 5. Alignement avec les sprints livrés

| Sprint livré | Ce que le maître en tire |
|---|---|
| **Sx_UI_02b** (Auren Terminal) | Direction visuelle active (§2) ; contradiction white clinical tranchée (§7) |
| **Sx_UI_06** (dé-densification) | Principe « ne pas re-densifier la home » (§5) ; Home décisionnelle légère (§4) |
| **Sx_DOGFOOD_01** (cohérence charge) | « Silence plutôt que faux poids » + placeholder = indication légère (§5) |
| **Sx_BI_01** (reprise BI) | BI zones traçables ; pas de 2e score opaque ; hérite Auren Terminal (§4, §5, §14) |

---

## 6. Priorités réalignées (proposées)

**Mode séance souverain › Home décisionnelle légère › cohérence charge/substitution
› Body Intelligence par zones › Progress/Physique › PWA (`Sx_UI_08`) › Rebrand
(`Sx_UI_10`).** Détail + séquence build exploitable dans le doc maître §4 et §6.

---

## 7. Note corpus (dépendance Sb_BI_01.1)

Un audit read-only du mapping exercice→zone (pour cadrer un éventuel « corpus
improvement ») montre : **11/11 zones couvertes en primaire, 0 exercice
« unknown »** (65 noms distincts, 87 lignes `ExerciseMuscleMapping` backfillées ;
11 patterns substring). Gaps réels : **zones secondaires** (seules biceps/triceps
peuplées comme secondaires) et **stabilisateurs / muscles fins** (vides par design,
OQ-32). **Conséquence** : le corpus improvement **n'est pas un préalable bloquant**
aux zone cards V1 — le socle primaire suffit ; il reste une amélioration possible
**après**, sur GO séparé. (Consigné dans le doc maître §6.)

---

## 8. Non-goals

Pas de code / UI build / rebrand complet / deploy / release tag / React / claims
médicaux / nouveau score. Les documents sources ne sont **ni réécrits ni archivés** —
ils restent références actives ; le doc maître est la porte d'entrée.

---

## Verdict

**Verdict :** 🟢 **Sx_TRANSFORM_01 App Transformation Corpus — AUDIT COMPLET, READY FOR HUMAN DECISION.**

Le corpus de transformation est riche mais dispersé (vocabulaire SPIGNOS/Auren,
directions visuelles successives, mentions React désormais interdites). L'audit
établit que les principales contradictions sont **déjà résolues** dans les faits
(Sx_UI_02b livré ; React interdit en gouvernance) et que le travail utile est une
**consolidation** — pas un nouveau débat. Le **document maître**
`Sx_TRANSFORM_01_APP_TRANSFORMATION_CONSOLIDATION_SPEC.md` (Option A) fixe le
vocabulaire, l'identité Auren Terminal, les garde-fous architecture, les priorités
réalignées, les principes informationnels actionnables, les contradictions résolues
et les interdits — sans réécrire les sources. Aucun code touché par ce sprint.
