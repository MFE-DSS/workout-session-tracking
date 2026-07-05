# Sx_UI_04 Focused Exercise Flow — Human Review Report

**Spec :** `Sx_UI_04_FOCUSED_EXERCISE_FLOW_SPEC`
**Spec source :** `docs/strategy/Sx_UI_04_FOCUSED_EXERCISE_FLOW_SPEC.md`
**Sprint report source :** `docs/SPRINT_Sx_UI_04_FOCUSED_EXERCISE_FLOW_REPORT.md`
**Commit :** `996c0c3822a7f342b53db3784fa0907c42589845`
**Type :** Human review docs-only (CI skippée — push docs-only via `paths-ignore: ['docs/**']`)
**Date review :** 2026-07-04
**Reviewer :** opérateur (Martin Feldmann) + direction produit (PO + lead architecte)
**Verdict :** ✅ **SPEC ACCEPTED — Human Review PASS**

---

## 1. Verdict

**Le recast `Sx_UI_04_FOCUSED_EXERCISE_FLOW_SPEC` est accepté en human review.**

La spec recadre proprement la suite de `Sx_UI_04` après la réserve visuelle de `Sb_UI_04.2` : passage d'une **liste verticale d'exercices** à un **Active Exercise Cockpit**, enrichi du **Live Exercise Expert Model** et d'une direction transverse **Body Representation System**. Les 7 OQ sont tranchées, le build split est renforcé (Sb_UI_04.3 → .5), la stratégie visuelle et asset est prudente, et la direction future Profile Body Intelligence est cadrée sans implémentation. Simple recolor / simple accordéon **explicitement rejeté** pour `Sb_UI_04.3`.

## 2. Nature du sprint

Human review **docs-only**. Aucune CI lourde attendue (les 2 commits `190cd32` + `996c0c3` sont docs-only, correctement skippés par `paths-ignore: ['docs/**']` — aucun run CI créé). Aucun code, aucun template, aucun asset touché.

## 3. Décisions validées (human review)

1. ✅ Passage d'une **liste verticale** d'exercices à un **Active Exercise Cockpit**.
2. ✅ Une **carte active dominante** devient le cœur de l'écran séance.
3. ✅ La jump bar devient un **mini-stepper compressé secondaire**.
4. ✅ Le mode séquentiel reste **navigable** : l'utilisateur peut revenir à un exercice précédent.
5. ✅ Le **Live Exercise Expert Model** validé (7 couches) :
   - orientation ;
   - exercise intent ;
   - worked area ;
   - technical cues ;
   - set logging console ;
   - alternatives / substitution ;
   - up next.
6. ✅ Les **principes pédagogiques** validés :
   - une seule décision principale à la fois ;
   - maximum 3 cues techniques visibles ;
   - « pourquoi » en une phrase ;
   - logging possible en moins de 5 secondes ;
   - progressive disclosure pour les détails.
7. ✅ Le **Worked Area Panel** doit apparaître **dès Sb_UI_04.3** en version textuelle minimale.
8. ✅ Le **Body Representation System** validé comme direction transverse long terme :
   - session active card ;
   - program / session preview ;
   - future profile / body intelligence ;
   - historique / progression plus tard.
9. ✅ La **taxonomie V1** des zones corporelles (15 zones) acceptée comme base documentaire.
10. ✅ Le contrat futur `exercise_code → body_map_descriptor` accepté comme cible documentaire, **sans implémentation immédiate**.
11. ✅ La **prudence anti-médicale** validée :
    - jamais diagnostic ;
    - jamais activation mesurée ;
    - parler de zone ciblée / dominante / estimée ;
    - recommandations prudentes.
12. ✅ La **stratégie visuelle V1** validée :
    - Worked Area Panel textuel ;
    - placeholder clinique froid ;
    - pas de GIF ;
    - pas d'image générée ;
    - pas de pipeline média.
13. ✅ La **stratégie V2/V3** acceptée comme direction future :
    - silhouette statique SVG ou image ;
    - fallback texte obligatoire ;
    - assets opérateur possibles plus tard ;
    - reduced-motion obligatoire pour tout média animé.
14. ✅ Le **split suivant** validé :
    - `Sb_UI_04.3` = Active Exercise Cockpit Shell ;
    - `Sb_UI_04.4` = Set Logging Console + Progression Guidance ;
    - `Sb_UI_04.5` = Worked Area Visual Slot + Alternatives Surface + Hardening.
15. ✅ Le **simple recolor / simple accordéon** explicitement **rejeté** pour `Sb_UI_04.3`.

## 4. OQ confirmées

| OQ | Décision confirmée |
|---|---|
| **OQ-A** | Mini-stepper cliquable, **pas** séquentiel strict. |
| **OQ-B** | Jump bar conservée mais **compressée** en stepper secondaire. |
| **OQ-C** | Worked area **dans la carte active, sous le titre, avant les sets**. |
| **OQ-D** | V1 = Worked Area Panel **statique** + contrat asset futur, **pas** placeholder vide. |
| **OQ-E** | **Rouvrir** un exercice passé autorisé. |
| **OQ-F** | Up-next = **nom + rôle court + zone principale**, pas charge complète. |
| **OQ-G** | Overview secondaire **replié**, pas liste dominante. |

Ces confirmations correspondent aux décisions tranchées par la direction produit en §19 de la spec. Aucun écart.

## 5. Cadre de mise en œuvre pour Sb_UI_04.3 (rappel invariants)

L'ouverture de `Sb_UI_04.3` devra respecter les invariants verrouillés par la spec (§8, §12) :

- **Anchors `#exercise-N`** préservés (exercice non actif masqué, jamais supprimé du DOM).
- **Form logging** POST inchangé, inputs `weight_kg` / `reps` / `completed` invariants.
- **Contrats JS `data-*`** (`data-start-rest`, `data-rest-duration`, `data-rest-skip`, `data-rest-display`) invariants.
- **Macros Jinja** (`segmented`, `field_group`) non modifiées.
- **No-JS fallback** préservé.
- **WCAG 44×44**, focus visible universel, `prefers-reduced-motion` préservés.
- **Aucune logique métier touchée** (`scoring/`, `substitution.py`, `coach_report.py`, `body_intelligence.py`, `overload_engine.py`, `recommendation.py`).
- **Aucune migration, aucun nouveau modèle, aucun asset.**
- Baseline P0 doit rester capturable (`ok=16`) après build.

## 6. Confirmations sécurité et compat

- ✅ Aucun secret / cookie / token affiché ou committé
- ✅ Aucun PNG committé
- ✅ Aucun `runtime.json` / `auth-state.json` committé
- ✅ Aucun compte prod cité ou utilisé
- ✅ Aucune DB locale committée
- ✅ Body Representation System = **documentaire uniquement** (aucun modèle, migration, service, asset, donnée runtime)
- ✅ Aucun claim médical / physiologique fort
- ✅ Baseline P0 déjà capturée (`docs/BASELINE_P0_CAPTURED_2026_07_04.md`), non touchée

## 7. Confirmation docs-only (ce commit d'acceptance)

Fichiers touchés dans ce commit d'acceptance :

- `docs/SPRINT_Sx_UI_04_FOCUSED_EXERCISE_FLOW_HUMAN_REVIEW_REPORT.md` — ce rapport
- `docs/strategy/SPEC_REGISTRY.md` — Sx_UI_04 recast ✅ HUMAN REVIEW ACCEPTED
- `docs/strategy/ROADMAP_AND_NEXT_STEPS.md` — recast accepté + Sb_UI_04.3 ready to be proposed

Aucun périmètre applicatif touché :

- ❌ `app/` (aucun template, CSS, JS, static, service, router, model)
- ❌ `tests/`
- ❌ `scripts/`
- ❌ `migrations/`
- ❌ `.github/workflows/`
- ❌ `requirements-lock.txt`, `pyproject.toml`, `package.json`
- ❌ Aucun PNG / runtime artefact / DB / secret

## 8. Statut post-acceptance

| Item | Statut |
|---|---|
| `Sx_UI_04_FOCUSED_EXERCISE_FLOW_SPEC` | ✅ **HUMAN REVIEW ACCEPTED** |
| Parent `Sx_UI_04_SESSION_FOCUS_RESKIN_SPEC` | ✅ conservée (recadrée) |
| `Sb_UI_04.3 Active Exercise Cockpit Shell` | 🟡 **READY TO BE PROPOSED, not opened** |
| `Sb_UI_04.4 Set Logging Console + Progression Guidance` | ⏸️ **BLOCKED until .3 delivered and reviewed** |
| `Sb_UI_04.5 Worked Area Visual Slot + Alternatives + Hardening` | ⏸️ **BLOCKED until .4 delivered and reviewed** |
| Baseline P0 | ✅ CAPTURED 2026-07-04 (16/16 PNG) |
| Screenshots | 📁 local only, gitignored |
| Release tag baseline-preauren | ⏸️ deferred |

## 9. Prochaine action recommandée

**Ouvrir `Sb_UI_04.3 Active Exercise Cockpit Shell`** sur override explicite opérateur.

Contenu attendu (aperçu, à finaliser à l'ouverture, cf. spec §20 + §23.9) :

- Bascule topologique : liste verticale → **carte active dominante** (cockpit).
- **Orientation** en haut : X/Y, N restants, progression, set courant.
- **Exercise intent** : pourquoi cet exercice maintenant, rôle dans le split.
- **Worked Area Panel textuel minimal** (zone principale / assistants / stabilisation) — **premier jalon** du Body Representation System.
- **Up next** compact (nom + rôle + zone).
- Jump bar → **mini-stepper compressé** cliquable (OQ-A / OQ-B).
- Invariants préservés (anchors, forms, JS `data-*`, no-JS, a11y).
- **Rupture perceptible exigée** — simple recolor / accordéon rejeté.
- Baseline P0 capturable après build (`ok=16`).

## 10. Verdict final

✅ **Sx_UI_04 Focused Exercise Flow recast ACCEPTED — Human Review PASS.**

**Sb_UI_04.3 Active Exercise Cockpit Shell : READY TO BE PROPOSED, not opened.**
**Sb_UI_04.4 / .5 : blocked until .3 delivered and reviewed.**
**No code touched. No screenshots. No release tag.**

## 11. Références

- Spec acceptée : `docs/strategy/Sx_UI_04_FOCUSED_EXERCISE_FLOW_SPEC.md`
- Sprint report source : `docs/SPRINT_Sx_UI_04_FOCUSED_EXERCISE_FLOW_REPORT.md`
- Spec parent (conservée) : `docs/strategy/Sx_UI_04_SESSION_FOCUS_RESKIN_SPEC.md`
- Réserve visuelle source : `docs/SPRINT_Sb_UI_04_2_HUMAN_REVIEW_REPORT.md`
- Baseline P0 : `docs/BASELINE_P0_CAPTURED_2026_07_04.md`
- Registry : `docs/strategy/SPEC_REGISTRY.md`
- Roadmap : `docs/strategy/ROADMAP_AND_NEXT_STEPS.md`
