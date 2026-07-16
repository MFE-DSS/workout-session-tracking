# Human Review — Sx_CUSTOM_PROGRAM_03 Program Quality Scoring Spec

**Verdict** : ✅ **HUMAN REVIEW ACCEPTED / SPEC ONLY / BUILD NOT AUTHORIZED**
**Date** : 2026-07-15
**Type** : revue humaine — docs-only (aucun code touché par cette revue ni par la spec)
**Track** : `Sx_CUSTOM_PROGRAM` (01 ✅ ACCEPTED · 02 ✅ ACCEPTED · **03 = ce document**)
**Branche** : `spec/sx-custom-program-01-intelligent-builder` (worktree isolé, synchronisée
origin, spec commit `e082b17`)
**Spec** : [`Sx_CUSTOM_PROGRAM_03_PROGRAM_QUALITY_SCORING_SPEC.md`](strategy/Sx_CUSTOM_PROGRAM_03_PROGRAM_QUALITY_SCORING_SPEC.md)

---

## 1. Verdict

**Sx_CUSTOM_PROGRAM_03 est acceptée.** Le moteur de scoring A/B/C des programmes custom est
défini comme direction. Le statut reste **SPEC ONLY** : aucun build, **aucune migration, aucun
code, aucun seed, aucune donnée modifiée** — `Sb_CUSTOM_PROGRAM_SCORING_*` NOT AUTHORIZED.

## 2. Scope accepté

Moteur de scoring A/B/C · **sous-scores explicables** (8, chacun avec raisons ≤ 3) · alertes
(info/warn) · suggestions actionnables non injonctives · **assumptions / missing data**
exposées (jamais de certitude inventée) · **microcopy non médicale** · future intégration aux
brouillons `UserProgram*` (re-score à chaque édition, figé à la publication).

## 3. Décision moteur

| Contrat | Décision |
|---|---|
| Moteur **pur** (aucune lecture DB dans le cœur, aucune I/O) | ✅ accepté (pattern `overload_engine` Sx_30) |
| **Déterministe** — même entrée = même `QualityReview`, bit à bit | ✅ accepté (test QA dédié) |
| **Versionné** via `PROGRAM_QUALITY_SCORING_VERSION` + `ekb_version` pinnée sur chaque sortie | ✅ accepté (doctrine d'invariance du repo) |
| **Pas de LLM comme source de vérité** (ni règles, ni textes) | ✅ contrat dur |
| Entrées `(ProgramDefinition, profil déclaré, EKB)` → sortie `QualityReview` | ✅ accepté |

## 4. Sous-scores acceptés (8)

`volume_per_zone` (vs fourchettes prudentes par niveau) · `push_pull_legs_balance` ·
`frequency_per_zone` · `recovery_spacing` (espacement des zones, `fatigue_class` EKB) ·
`redundancy` (`variant_group`/pattern) · `duration_realism` (`estimated_slot_minutes` vs
budget) · `equipment_feasibility` · `overload_compatibility` (ranges exploitables Sx_30).
Seuils = constantes versionnées dans le moteur, sources prudentes (WHO/ODPHP pour les
planchers, jamais pour des promesses).

## 5. Grade A/B/C

- **Règle hybride acceptée comme direction** : moyenne pondérée **plafonnée** par les
  sous-scores critiques (< 40 ⇒ C, < 60 ⇒ B) — énonçable en une phrase, le sous-score
  plafonnant est nommé. **Pas de score opaque** (leçon `/physique`).
- **Sous-scores et alertes visibles avant la lettre** dans toute future UI — la lettre est un
  résumé, jamais l'information principale.
- **Grade C non bloquant par défaut, avec avertissement explicite** — à confirmer dans les
  specs persistence/wizard (OQ-SCORE-C, alignée OQ-CP-J du parent).

## 6. Régimes de vérité

Distinction actée et contraignante : **théorie générale** (constantes sourcées) · **profil
utilisateur déclaré** (base du calcul) · **historique réel = V2 seulement** (aucun signal de
séance en V1) · **données manquantes** (`missing_data_json`, jamais tues) · **inférences
prudentes** (`assumptions_json`, affichées à côté du grade). **Aucune certitude inventée** —
silence ou hypothèse visible, jamais d'optimisme implicite.

## 7. Microcopy

Interdits durs actés : claim médical · promesse hormonale · culpabilisation · **« tu dois »**
(règle Sx_30 reprise verbatim) · « optimal/parfait » en absolu. Formulations indicatives
obligatoires (« peut aider », « semble », « à vérifier », « d'après ton profil déclaré ») +
mention permanente « Grille indicative — pas une vérité médicale ou scientifique absolue ».

## 8. Persistance

- **Scoring sur brouillon** `UserProgram*`, recalculé à chaque édition (affichage).
- **Trace versionnée future `user_program_quality_reviews`** : une row par version publiée
  (grade, subscores, assumptions, `scoring_version`, `ekb_version`), **jamais réécrite**.
- **Scoring figé à la publication.**
- Le **`WorkoutTemplate` matérialisé ne devient jamais source de vérité du score** (au plus
  une copie d'affichage) ; aucune logique de scoring dans les tables catalogue.

## 9. QA future acceptée (10 tests, spec §11)

Déterminisme strict · programme équilibré → A/B · programme redondant → baisse `redundancy` +
alerte · durée irréaliste → baisse `duration_realism` + suggestion · matériel incompatible →
alerte · données manquantes → assumptions non vides · lexique médical interdit absent ·
**aucun « tu dois »** (corpus exhaustif) · grade C publiable (si OQ-SCORE-C confirmée, le
moteur n'émet jamais d'état bloquant) · versions présentes sur toute sortie.

## 10. Open questions (OQ-SCORE-A → OQ-SCORE-H)

Statut : **questions à trancher dans les specs/builds suivants, pas des décisions finales** —
avec leurs positions par défaut : seuils (80/60 + plafonds 40/60) · pondérations uniformes V1 ·
**C publiable avec avertissement** · persistance Option C (à la volée + trace) · **historique
réel V2 strict** · durées en minutes entières ±20 % · cardio neutre, abdos/gainage en volume
`core` hors plafonnement overload · assumptions toujours visibles si non vides (jamais
repliées par défaut).

## 11. Invariants vérifiés

no `app/` · no `tests/` · no `data/` · no migrations · no seed · no templates · no CSS/JS ·
no UI/Auren · no repo principal (vérifié, intact) · no build · no deploy · `quality_score.py`
et `muscle_scoring.py` existants **non touchés** (domaines distincts) · diff de la spec =
3 fichiers docs (+218) · `check_spec_protocol` PASS · `check_scope` DOCS.

## 12. Queue suivante

| Élément | Statut |
|---|---|
| **`Sx_CUSTOM_PROGRAM_04` — User Program Persistence Spec** | 🔵 **NEXT SPEC CANDIDATE** (SPEC ONLY, sur GO explicite) |
| `Sx_CUSTOM_PROGRAM_05` — Session Instantiation Compatibility Spec | ⚪ après 04 |
| `Sb_CUSTOM_PROGRAM_*` (builds parent) | ❌ **NOT AUTHORIZED** |
| `Sb_CUSTOM_PROGRAM_SCORING_01→04` | ❌ **NOT AUTHORIZED** |
| `Sb_CUSTOM_PROGRAM_EKB_01→04` | ❌ NOT AUTHORIZED |
| Migrations / seed | ❌ aucun autorisé |

---

## Verdict

**Verdict :** ✅ **Sx_CUSTOM_PROGRAM_03 Program Quality Scoring Spec — HUMAN REVIEW ACCEPTED /
SPEC ONLY / BUILD NOT AUTHORIZED.**

Le scoring A/B/C est acté comme **moteur pur, déterministe, versionné**, à 8 sous-scores
explicables, grade hybride plafonné jamais opaque, régimes de vérité distingués (historique
réel = V2 strict), microcopy non médicale sans « tu dois », grade C publiable avec
avertissement par défaut, persistance à la volée + trace versionnée figée à la publication.
Les 8 OQ restent ouvertes pour les specs/builds suivants. **Next :
`Sx_CUSTOM_PROGRAM_04 — User Program Persistence Spec` sur GO ; tout build scoring reste
interdit.** Aucun code touché ; repo principal UI non touché.
