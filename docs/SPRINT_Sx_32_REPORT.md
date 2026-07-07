# Sprint Report — Sx_32 Muscle & BodyZone Model (Deep Feature Refactor Scoping)

**Sprint ID :** `Sx_32_MUSCLE_BODYZONE_MODEL`
**Type :** SPEC ONLY (docs-only) — cadrage de refonte métier
**Date :** 2026-07-07
**Auteur :** opérateur (Martin Feldmann) + agent Claude Code
**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`
**Verdict :** ✅ **READY FOR HUMAN REVIEW**

---

## 1. Résumé

Sprint spec-only qui **ouvre le premier axe de refonte profonde du métier** (features/objets), demandée par l'opérateur après le constat que les cycles UI ont transformé l'interface mais laissé le backend sur des heuristiques. Choix opérateur : **modèle Muscle / BodyZone formel** comme fondation.

La spec s'appuie sur un **audit backend read-only** (10 modèles, ~60 services, 20 migrations) qui a confirmé la dette : la classification muscle/zone est du **substring-matching en dur** (`muscle_mapping.py`, 11 zones + `_EXERCISE_PATTERNS`), sans objet en base. Le Worked Area UI affiche « à qualifier » précisément faute de ce modèle.

**BUILD BLOQUÉ** : aucun code/migration ; override cycle métier requise.

## 2. Fichiers créés / modifiés

### Créés
- `docs/strategy/Sx_32_MUSCLE_BODYZONE_MODEL_SPEC.md` — spec de cadrage, 15 sections
- `docs/SPRINT_Sx_32_REPORT.md` — ce rapport

### Modifiés
- `docs/strategy/SPEC_REGISTRY.md` — Sx_32 🟢 SPEC delivered pending review (nouveau cycle métier)
- `docs/strategy/ROADMAP_AND_NEXT_STEPS.md` — ouverture cycle refonte, backlog des autres axes

## 3. Confirmation docs-only

Scope strict. Aucun fichier hors `docs/` modifié par CE sprint :
- ❌ `app/`, `tests/`, `migrations/`, `scripts/`, `.github/`, deps, PNG, runtime, DB, secret
- ❌ Aucun modèle / migration écrit
- Lectures read-only autorisées (audit) : `app/models/*`, `app/services/*` — aucune modification.

> **Note working tree** : le sprint `Sb_UI_02b.3` (shell Auren Terminal) est présent en working tree, **non commité** (CR livré, GO commit non encore donné). Il est **indépendant** de cette spec. Les fichiers Sx_32 (docs) sont à committer **séparément** du shell Sb_UI_02b.3.

## 4. Constat d'audit (dette confirmée sur code réel)

- `muscle_mapping.py` : **11 zones hardcodées** (`ZONE_LABELS`) + `ZONE_MEASUREMENT` + `ZONE_VOLUME_TARGET` + `RADAR_AXIS_ORDER` + `_EXERCISE_PATTERNS` (liste de mots-clés) → `classify_exercise(name)` par substring match.
- **Aucun objet Muscle/BodyZone en base.** `machine_atlas.json` (zone par famille) et `exercise_properties.json` (zone_primary/muscle_group) existent mais **non reliés** au modèle.
- 3+ sources de vérité zone non réconciliées.
- Conséquence directe : Worked Area UI (Sx_UI_04 §23) bloqué sur « à qualifier » ; `body_map_descriptor` (§23.5) resté documentaire.

## 5. Décisions produit (§ de la spec)

| # | Décision | Section |
|---|---|---|
| 1 | Formaliser Muscle / BodyZone / ExerciseMuscleMapping en base | §5 |
| 2 | **Invariance historique = contrainte #1** (mêmes classifications/scores/leaderboards) | §4, §8 |
| 3 | Backfill des 11 zones actuelles → point de départ, pas remplacement | §5.2, §6 |
| 4 | `classify_exercise` bascule sur lookup + **fallback substring** (zéro régression) | §6 |
| 5 | Contrat `body_map_descriptor` implémentable → débloque Worked Area | §5.4 |
| 6 | Découpage 4 sous-sprints review-gated + migrations additive-only | §7 |
| 7 | Périmètre borné : autres axes Tier 1 en **backlog** (pas de scope creep) | §10 |
| 8 | 7 OQ avec recommandation | §9 |

## 6. Découpage proposé

- **Sb_32.1** : `BodyZone` + `Muscle` + backfill des dicts hardcodés → base.
- **Sb_32.2** : `ExerciseMuscleMapping` + backfill `_EXERCISE_PATTERNS` ; `classify_exercise` → lookup + fallback.
- **Sb_32.3** : contrat `body_map_descriptor` (service) + branchement Worked Area (sprint UI séparé).
- **Sb_32.4** : migration consommateurs (coach/body_intel/scoring) + closeout.

## 7. OQ (7, avec recommandation)

| OQ | Recommandation V1 |
|---|---|
| A clé mapping | `exercise_code` |
| B granularité | **Zone V1** (Muscle préparé, peuplé minimal) |
| C arbitrage sources | muscle_mapping primaire, atlas/properties enrichissement |
| D substitution | reste indépendante V1 (autre axe) |
| E fallback substring | conservé V1, déprécié en .4 après invariance |
| F stabilizers | fallback « à qualifier » V1 (pas d'invention) |
| G Worked Area UI | sprint UI séparé (Sx_32 fournit le service) |

## 8. Backlog documenté (hors ce cycle)

Différés sous override dédiée : agrégation Readiness/Recovery · unification identité exercice · substitution first-class · overload compliance · Tier 2/3.

## 9. Limites

- La spec **cadre**, ne construit rien.
- L'invariance historique impose des tests de non-régression lourds (comparer classify old/new sur tout le catalogue) — coût réel du build, pas de la spec.
- La granularité muscle fine est repoussée V2 (zone V1) pour borner le risque.

## 10. Confirmations sécurité et compat

- ✅ Aucun secret / PNG / runtime / DB committé
- ✅ Aucun code métier touché (audit read-only)
- ✅ Aucun claim médical dans la spec
- ✅ Contrat additive-only migrations rappelé (§4)

## 11. Statut post-livraison

| Item | Statut |
|---|---|
| `Sx_32_MUSCLE_BODYZONE_MODEL_SPEC` | 🟢 **SPEC delivered — pending human review** |
| `Sb_32.1` → `.4` | ⏸️ BLOCKED (spec + OQ + override cycle métier) |
| Autres axes refonte (readiness agg, identité, substitution) | 📋 backlog documenté, not opened |
| `Sb_UI_02b.3` shell | ⚠️ working tree, non commité (indépendant) |
| Release tag | ⏸️ deferred |

## 12. Prochaine action recommandée

1. **Human review** de `Sx_32_MUSCLE_BODYZONE_MODEL_SPEC` + trancher OQ-32-A→G.
2. **Override explicite d'ouverture du cycle Sx_32** (métier).
3. Puis **ouvrir `Sb_32.1`** (BodyZone + Muscle + backfill) sous override.

En parallèle non bloquant : décider du sort de `Sb_UI_02b.3` (commit + push le shell terminal, CI verte attendue).

## 13. Verdict

✅ **READY FOR HUMAN REVIEW.**

**Aucun build ouvert. Aucun code/migration. Backlog des autres axes documenté. Aucun release tag.**
