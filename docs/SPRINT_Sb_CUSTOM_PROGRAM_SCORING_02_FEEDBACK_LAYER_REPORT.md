# Sprint Sb_CUSTOM_PROGRAM_SCORING_02 — Program Quality Feedback Layer — BUILD

**Statut** : 🟢 **PATCH COMPLETE / REVIEW PENDING** (non commité, non poussé, CI non lancée)
**Type** : CODE BUILD — **wrapper pur de présentation** (Option C opérateur), zéro DB/ORM/migration/`data/`
**Date** : 2026-07-22
**Specs** : `Sx_CUSTOM_PROGRAM_03` §8 (microcopy) · §7 (régimes de vérité) · §15 (queue : SCORING_02 = microcopy + alertes + suggestions)
**Branche** : `sb/custom-program-scoring-02-feedback` (worktree dédié, base `65d1381`, head Alembic `n5o0i6j7l98` inchangé)
**Préflight** : ✅ GO PATCH validé — **Option C**, sans modification du moteur SCORING_01

---

## 0. Étape 0 — Brainstorming / Options / Risques / Choix retenu

| Décision | Options | Choix retenu |
|---|---|---|
| Architecture | A microcopy seule · B enrichir le moteur · C wrapper séparé · D différer | **C — wrapper pur** (arbitrage opérateur) : sépare le calcul du langage produit, testable seul, moteur intouché |
| Modification du moteur | oui · non | **non** — aucune nécessité bloquante rencontrée ; les 19 tests moteur restent verts sans changement |
| Niveaux de feedback | 2 (warn/info) · 3 (info/warning/tip) · avec bloquant | **3 niveaux, aucun bloquant** (OQ-SCORE-C : le scoring informe, ne bloque pas) |
| Verbosité | illimitée · plafonnée | **plafonnée à 3 items par niveau** (règle « ≤ 3 » héritée Sx_30) |
| Ton sur les limites de mesure | sujet = utilisateur · sujet = outil | **sujet = l'outil** (« ces dimensions ne sont pas encore mesurables ») — zéro culpabilisation |

**Constat qui justifie le build (mesuré au préflight)** : les champs `alerts`/`suggestions` de
SCORING_01 étaient **déjà peuplés**, mais **quatre informations restaient invisibles** pour
l'utilisateur — le plafond de grade, les 4 dimensions non mesurables, la fiabilité, et tout
retour sur un programme sain (un PPL équilibré ne produisait qu'**1 alerte**).

## 1. Patch appliqué

| Fichier | Nature |
|---|---|
| `app/services/program_quality_feedback.py` | **nouveau** (~290 l.) — `build_program_quality_feedback(result)`, dataclasses `ProgramQualityFeedback`/`FeedbackItem`, 3 niveaux, ordre stable, plafonnement, microcopy |
| `tests/test_program_quality_feedback.py` | **nouveau** — **20 tests** |

**Zéro modification de `program_quality_engine.py` et de ses tests** · zéro `data/` · zéro
`app/models/` · zéro migration · zéro API/UI · zéro persistance `quality_reviews`.

## 2. Contrat final du wrapper

```
build_program_quality_feedback(result: QualityReviewResult) -> ProgramQualityFeedback
```

```
ProgramQualityFeedback
  headline          str            # phrase d'accroche dérivée du grade
  grade             str            # A | B | C (repris tel quel du moteur)
  grade_note        str | None     # explication du plafond, si applicable
  confidence_note   str            # fiabilité verbalisée (% de couverture)
  items             tuple[FeedbackItem, ...]
  limitations       tuple[str, ...]  # dimensions non mesurables + raison
  disclaimer        str            # repris du moteur
  scoring_version   int
  ekb_version       str | None
  to_dict()                        # sérialisable JSON

FeedbackItem
  level: info | warning | tip · category · title · message · action · subscore
```

**Pureté** : aucune I/O, aucune DB, aucun ORM, aucun LLM, aucun recalcul de score
(pinné par un test qui grep le source du module).

## 3. Niveaux livrés

| Niveau | Usage | Exemple produit |
|---|---|---|
| `warning` | déséquilibre **réel** constaté | « Le programme ne couvre que : poussée. » |
| `tip` | option d'amélioration actionnable | « Répartir quelques séries vers les zones les moins vues peut aider. » |
| `info` | contexte, limites de l'outil, grade cap, fiabilité, point solide, hypothèses | « Ces dimensions ne sont pas encore mesurables par l'outil : … » |

**Aucun niveau bloquant n'existe** — un grade C reste publiable (testé).

## 4. Doctrine de microcopy appliquée

- **Interdits testés par grep** : lexique médical/hormonal · « tu dois » · « optimal » ·
  « parfait » · formulations culpabilisantes (« tu manques », « insuffisant »…).
- **Sujet grammatical côté outil** pour toute limite de mesure — testé explicitement.
- **Formulations indicatives** : « peut aider », « souvent utile », « à vérifier ».
- **Disclaimer** repris du moteur et toujours présent.
- Le plafond de grade est présenté comme une **limite de l'outil**, jamais comme un défaut
  du programme : « Ce n'est pas un défaut de ton programme. »

## 5. Effet mesuré (avant / après)

Sur un **PPL équilibré** (grade B) :

| | SCORING_01 seul | Avec SCORING_02 |
|---|---|---|
| Retours utiles | 1 alerte | **4 items** |
| Plafond de grade expliqué | ❌ | ✅ `grade_note` + item dédié |
| Dimensions non mesurables restituées | ❌ | ✅ 4/4 en `limitations` + item |
| Fiabilité verbalisée | ❌ | ✅ « Lecture indicative : 100 % … » |
| Point solide signalé | ❌ | ✅ |

## 6. Tests et checks exécutés

| Suite / check | Résultat |
|---|---|
| Dédiés (`test_program_quality_feedback.py`) | **20/20 premier coup** |
| **Non-régression moteur** (`test_program_quality_engine.py`) | **19/19** — moteur intouché |
| ruff (2 fichiers neufs) | clean |
| `check_ruff_budget` | **543 ≤ 548** (inchangé) |
| `check_spec_protocol` | PASS |
| **`check_scope`** | **ISOLATED** — full sweep local skippé par le garde-fou (contrat CLAUDE.md §1) ; CI PR = source de vérité |

Couverture des 20 tests : pureté (aucun import ORM) · déterminisme · sérialisabilité ·
versions reportées · **feedback non vide sur programme équilibré** · **grade cap expliqué** ·
**4 `missing_data` restitués** · **confiance + coverage verbalisés** · contexte nommé ·
**aucun niveau bloquant** · ordre priorisé stable · **plafonnement par niveau** · grade C
publiable · lexique médical absent · aucune injonction · **aucune culpabilisation** ·
limites formulées côté outil · disclaimer reporté · programme vide et exercices inconnus
sans crash.

## 7. Risques résiduels

Couche **non branchée** (consommateur = wizard futur — pattern fondation du track) · la
microcopy existe en deux endroits (raisons factuelles du moteur, langage produit du wrapper) :
assumé et cohérent, les deux corpus étant soumis aux **mêmes tests de lexique** · les libellés
resteront à ajuster au dogfood réel.

## 8. Confirmations de périmètre

✅ Wrapper pur (zéro DB/ORM/I-O) · ✅ **moteur SCORING_01 non modifié** · ✅ zéro `data/` ·
✅ zéro `app/models/`, zéro migration (head `n5o0i6j7l98`), zéro seed · ✅ zéro écriture
`UserProgramQualityReview` · ✅ zéro API/UI/wizard · ✅ pas de LLM · ✅ pas de claim médical.

---

## Verdict

**Verdict :** 🟢 **Sb_CUSTOM_PROGRAM_SCORING_02 — PATCH COMPLETE / REVIEW PENDING.**

La couche de feedback traduit le score brut en langage produit sans jamais recalculer :
le plafond de grade, les 4 dimensions non mesurables et la fiabilité sont désormais
**expliqués à l'utilisateur**, un programme sain reçoit un retour utile, la hiérarchie
info/warning/tip **n'émet aucun blocage**, et la microcopy est verrouillée par grep
(médical, injonctions, culpabilisation). 20 dédiés + 19 non-régression verts ;
check_scope ISOLATED. **`SCORING_03` (persistance `quality_reviews`), `EKB_04`,
`WIZARD_*` restent NOT OPENED.**
