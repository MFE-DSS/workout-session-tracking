# Sx_32 Muscle / BodyZone Model — Human Review Report

**Spec :** `Sx_32_MUSCLE_BODYZONE_MODEL_SPEC`
**Spec source :** `docs/strategy/Sx_32_MUSCLE_BODYZONE_MODEL_SPEC.md`
**Sprint report source :** `docs/SPRINT_Sx_32_REPORT.md`
**Commit spec :** `47f3fac`
**Type :** Human review docs-only (CI skippée — push docs-only via `paths-ignore: ['docs/**']`)
**Date review :** 2026-07-07
**Reviewer :** opérateur (Martin Feldmann)
**Verdict :** ✅ **SPEC ACCEPTED — Human Review PASS + CYCLE MÉTIER AUTORISÉ**

---

## 1. Verdict

**La spec `Sx_32_MUSCLE_BODYZONE_MODEL_SPEC` est acceptée en human review, et le cycle métier `Sx_32` est autorisé.**

C'est le **premier chantier de refonte profonde du backend** — au-delà de la transformation UI. Il formalise un **modèle Muscle / BodyZone relationnel** pour remplacer le substring-matching heuristique actuel, et débloque le Worked Area UI + coach report + body intelligence. La contrainte #1 est l'**invariance historique** : formaliser sans casser les classifications, scores et leaderboards existants.

**`Sb_32.1` reste READY TO BE PROPOSED, not opened** — le build backend s'ouvre sur override séparé, pas dans cette validation.

## 2. Nature du sprint

Human review **docs-only**. Aucune CI lourde (commit spec `47f3fac` docs-only, skippé par `paths-ignore: ['docs/**']`). Aucun code / modèle / migration / service touché.

## 3. OQ confirmées

| ID | Décision confirmée |
|---|---|
| **OQ-32-A** | Clé de mapping : **`exercise_code`** (cohérent avec l'identité snapshot, robuste aux reseeds). |
| **OQ-32-B** | Granularité : **Zone V1** (backfill des 11 zones), `Muscle` table préparée mais peuplée au minimum ; granularité fine en V2. |
| **OQ-32-C** | Arbitrage des sources : **`muscle_mapping.py` primaire** (ground truth actuel des scores) ; `machine_atlas.json` + `exercise_properties.json` = **enrichissement** (stabilizers/pattern), jamais override du primary. |
| **OQ-32-D** | Substitution : **indépendante V1**, non couplée au build Muscle/BodyZone (autre axe Tier 1, backlog). |
| **OQ-32-E** | Fallback substring : **conservé V1**, dépréciable en `Sb_32.4` seulement après invariance prouvée sur 100% du catalogue. |
| **OQ-32-F** | Stabilizers : **fallback « à qualifier » V1**, pas d'invention (peuplement progressif depuis données fiables). |
| **OQ-32-G** | Worked Area UI : **sprint UI séparé** ; `Sx_32` fournit le service / contrat `body_map_descriptor`, l'UI le consomme après. |

Ces confirmations correspondent aux recommandations produit de la spec (§9). Aucun écart.

## 4. Décisions actées

1. **Sx_32 est human reviewed and accepted.**
2. Le **cycle métier `Sx_32` est autorisé** (override d'ouverture accordée).
3. **`Sb_32.1` est READY TO BE PROPOSED, not opened.**
4. Les **migrations futures doivent rester additive-only** (contrat Sx_26 : ADD COLUMN / ADD TABLE only, jamais DROP/RENAME/UPDATE destructif).
5. L'**invariance historique est contrainte #1** : aucune divergence de classification tolérée.
6. Les **classifications historiques, leaderboards, scores, body intelligence et coach consumers** doivent être protégés par **tests de non-régression** (comparer `classify_exercise` old vs new sur tout le catalogue avant chaque bascule).
7. Le **fallback substring reste actif en V1** (filet de sécurité anti-régression « unknown »).
8. **Aucune refonte substitution / readiness aggregation / exercise identity** n'est incluse dans `Sb_32.1` (autres axes Tier 1, backlog).
9. Les **autres axes Tier 1 restent backlog** documenté.
10. **Aucun code n'est touché dans cette validation** (docs-only).

## 5. Cadre pour l'ouverture de Sb_32.1 (invariants métier)

Le futur build `Sb_32.1` (BodyZone + Muscle + backfill) devra respecter (§4/§7/§8 de la spec) :
- **Invariance** : les 11 zones/labels/measurement/radar/volume actuels sont **backfillés** — mêmes valeurs exposées, prouvé par test.
- **Migrations additive-only** : ADD TABLE `bodyzone`, `muscle` ; downgrades idempotents.
- **Contrat DoR (§12)** : baseline de non-régression définie (snapshot `classify_exercise` sur tout le catalogue = référence à égaler) avant toute bascule.
- **Aucun consommateur muté dans .1** : `muscle_scoring`, `coach_report`, `body_intelligence` migrent progressivement (`.2`→`.4`), à sortie identique.
- **Aucun claim médical nouveau** (garde-fous coach/body préservés).
- **Aucun rebrand SPIGNOS → Auren dans le code** (réservé Sx_UI_10).

## 6. Confirmations sécurité et compat

- ✅ Aucun secret / PNG / runtime / DB committé
- ✅ Aucun code métier touché (validation docs-only)
- ✅ Aucun claim médical dans la spec ni cette validation
- ✅ Contrat migrations additive-only rappelé
- ✅ Invariance historique posée comme contrainte bloquante

## 7. Confirmation docs-only (ce commit d'acceptance)

Fichiers touchés dans ce commit d'acceptance :

- `docs/SPRINT_Sx_32_HUMAN_REVIEW_REPORT.md` — ce rapport
- `docs/strategy/SPEC_REGISTRY.md` — Sx_32 ✅ SPEC HUMAN REVIEW ACCEPTED + cycle autorisé
- `docs/strategy/ROADMAP_AND_NEXT_STEPS.md` — Sx_32 accepté + Sb_32.1 ready

Aucun périmètre applicatif touché : ❌ `app/`, `tests/`, `migrations/`, `scripts/`, `.github/`, deps, PNG, runtime, DB, secret.

## 8. Statut post-acceptance

| Item | Statut |
|---|---|
| `Sx_32_MUSCLE_BODYZONE_MODEL_SPEC` | ✅ **SPEC HUMAN REVIEW ACCEPTED** |
| Cycle métier `Sx_32` | ✅ **AUTORISÉ** (override d'ouverture accordée) |
| `Sb_32.1 BodyZone + Muscle foundation` | 🟡 **READY TO BE PROPOSED, not opened** |
| `Sb_32.2` → `.4` | ⏸️ **BLOCKED** (séquentiels, review-gated, non-régression prouvée) |
| Autres axes Tier 1 (readiness agg, identité exercice, substitution first-class) | 📋 backlog documenté, not opened |
| Release tag | ⏸️ deferred |

## 9. Prochaine action recommandée

**Ouvrir `Sb_32.1 BodyZone + Muscle Foundation + Backfill`** sur override explicite opérateur.

Contenu attendu (aperçu, cf. spec §7) :
- Modèles `BodyZone` + `Muscle` (migrations additive-only).
- **Backfill** des 11 zones actuelles (labels, measurement_field, radar_axis, volume_target) depuis les dicts hardcodés `muscle_mapping.py` → base.
- **Test d'invariance** : les zones/labels/targets exposés sont identiques avant/après.
- Aucun consommateur muté (bascule `classify_exercise` en `.2`).
- Baseline de non-régression capturée en préalable (DoR §12).

## 10. Références

- Spec acceptée : `docs/strategy/Sx_32_MUSCLE_BODYZONE_MODEL_SPEC.md`
- Sprint report source : `docs/SPRINT_Sx_32_REPORT.md`
- Code ancré : `app/services/muscle_mapping.py` (11 zones + `_EXERCISE_PATTERNS` + `classify_exercise`)
- Contrat UI en attente : `docs/strategy/Sx_UI_04_FOCUSED_EXERCISE_FLOW_SPEC.md` §23 (`body_map_descriptor`)
- Contrat migrations : `Sx_26` (additive-only)
- Registry : `docs/strategy/SPEC_REGISTRY.md`
- Roadmap : `docs/strategy/ROADMAP_AND_NEXT_STEPS.md`

## 11. Verdict final

✅ **Sx_32 Muscle / BodyZone Model SPEC ACCEPTED — Human Review PASS. Cycle métier autorisé.**

**Sb_32.1 BodyZone + Muscle Foundation : READY TO BE PROPOSED, not opened.**
**Invariance historique = contrainte #1. Fallback substring conservé V1. Autres axes Tier 1 en backlog.**
**Aucun code touché. Release tag deferred.**
