# SPRINT Sx_MORPHO_PROGRAM_01 — Morphology-Aware Programming Architecture (RAPPORT)

**Base canonique :** `092207c` · **Branche :** `sb/sx-morpho-program-01-spec` · **Tier :** DOCS (**spec-only — 0 code applicatif, 0 migration**)
**Spec :** [`Sx_MORPHO_PROGRAM_01_SPEC.md`](strategy/Sx_MORPHO_PROGRAM_01_SPEC.md)
**Livré sous le protocole agentique** (`CLAUDE.md §4`) : `GO BUILD` (spec-only) → préflight → autonome jusqu'à `PR GREEN / MERGE PENDING`.

## 1. Ce qui est livré

L'**architecture** (design uniquement) du pipeline morphologie-aware : faits corporels bruts → descripteurs de morphologie interprétés → priorités d'entraînement → intentions de slots → substitution → programmes custom déterministes. + la **file de build** (5 items). **Aucun code, aucune migration** : la spec définit les 12 décisions imposées et branche le tout sur les briques **existantes** sans les casser.

## 2. Brainstorming / Options / Risques / Choix retenu (CLAUDE.md §3)

**Préflight** : survol des specs corporelles existantes (sous-agent) + lecture directe de la substitution (`Sx_22a`), de l'EKB et du générateur déterministe. **Aucune spec conflictuelle shippée** ; des prédécesseurs **spec-only non construits** (Body Signal Model, roadmap `Sb Body 04/05`) couvrent la moitié amont → à **référencer additivement**, pas à réinventer.

| Option | Verdict |
|---|---|
| **A** — couche **additive** sur les briques existantes (substitution `compute_proximity`, générateur pur, `BodyMeasurement` flag-off, EKB), garde-fou strict, « agent propose / déterministe décide » | ✅ **RETENU** — zéro schéma neuf, zéro rupture, réutilise Sx_22a + Custom_01 §13 (hook body-signal V2 déjà réservé) |
| **B** — nouveau moteur morphologie **from scratch** (descripteurs/priorités/substitution propres) | ✗ duplique Body Signal Model + Sx_22a, risque de **contradiction** (posture), surface énorme |
| **C** — l'agent **génère directement** le programme depuis le rapport | ✗ viole « no silent mutation », non déterministe, black box (contredit Custom_01 §13 + doctrine C2) |

**Risques traités** :
1. **Contradiction posture** — Body Signal Model tolère « posture indicative » ; BI-Activation §13 (human-review-accepté) l'**interdit**. → adoption du **garde-fou strict**, priorité `upper_back_posture` **renommée** `rear_delts_upper_back` (volume, sans posture). *Réconcilié §3.*
2. **Rupture de substitution** — le slot intent pourrait tenter de forcer une substitution cross-pattern. → le slot **biaise la génération initiale** ; la substitution runtime N1/N2/N3 (`compute_suggestions`) reste **inchangée et souveraine**. *§8.*
3. **Pseudo-précision / médical** — ape index, « longiligne », mesures « ≈ ». → traités en **tags/ratios bornés** avec `confidence` ; jamais fémur/insertion/posture/%BF. *§2, §3, §5.*
4. **Données personnelles** — mesures + (pas de) photos. → réutilise `BodyMeasurement`/`body_consents` (flag-off) ; **aucune photo** ; Martin = **fixture dogfood privée**, jamais template global/`/library`. *§4.*
5. **Non-déterminisme agentique** — l'agent pourrait introduire du hasard. → frontière dure : agent **propose** (sortie structurée), services **déterministes décident** ; écriture traçable, aucune mutation silencieuse. *§11.*

## 3. Fichiers touchés (docs only)

| Fichier | Changement |
|---|---|
| `docs/strategy/Sx_MORPHO_PROGRAM_01_SPEC.md` (**neuf**) | l'architecture + 12 décisions + file de build + préflight |
| `docs/SPRINT_Sx_MORPHO_PROGRAM_01_REPORT.md` (**neuf**) | ce rapport |
| `docs/strategy/SPEC_REGISTRY.md` | ligne registry |
| `docs/strategy/ROADMAP_AND_NEXT_STEPS.md` | entrée + file de build |
| **code applicatif** | **aucun** |

## 4. Décisions clés (résumé)

- **3 couches** FACT / INFERENCE / RECOMMENDATION, flux unidirectionnel, versions d'engine (§1).
- **Confidence** `measured/derived/inferred/not_deductible` ; `inferred`-seul ne crée jamais une priorité (§2).
- **Garde-fou strict** (BI-Activation §13) : 0 posture / composition / diagnostic / pseudo-précision (§3).
- **Confidentialité** : 0 photo, réutilise `BodyMeasurement`+`body_consents`, Martin = fixture privée (§4).
- **Schémas** descripteur (§5), priorité (§6), slot intent (§7) — tous sur des champs **existants**.
- **Substitution réutilisée** (`compute_proximity`), N1/N2/N3 **inchangé** (§8).
- **Fitness Park** : manifeste d'availability filtrant la génération, jamais la substitution runtime (§9).
- **Générateur** : couche pure **additive** qui compose le générateur existant, déterminisme préservé (§10).
- **Frontière agentique** : propose vs décide, 0 mutation silencieuse (§11).
- **Dogfood** : mise à jour = nouvelle version via cycle existant, jamais mutation en place (§12).

## 5. File de build définie

`Sb_MORPHO_PROFILE_01` → `Sb_PROGRAM_SLOT_INTENT_01` → `Sb_MORPHO_PROGRAM_GENERATOR_01` → `Sb_MARTIN_PROGRAM_01` → `Sb_MORPHO_DOGFOOD_01` (dépendances ordonnées, cf. spec §14). Chacun sur GO explicite.

## 6. Interdits tenus

0 code applicatif · 0 migration · 0 implémentation de modèle/schéma · 0 photo · 0 asset image · 0 médical/posture/pseudo-précision · 0 donnée Martin en template global · substitution (Sx_22a) **inchangée** · cycle publication (PUBLICATION_01→04) **inchangé** · EKB_04 non ouvert · runtime ASSET non touché · `/library` non exposé · `session_builder` non réécrit.

## 7. Validation

check_scope **DOCS** · `check_spec_protocol` PASS · `check_ruff_budget` inchangé (543 ≤ 548). Commit **100 % docs** → CI push canonique légitimement skippée (`paths-ignore: docs/**`) ; la PR (`pull_request`) déclenche la CI complète comme filet.

## Verdict

**Verdict :** ✅ **Sx_MORPHO_PROGRAM_01_SPEC — MERGED + VERIFIED (spec-only).** Architecture morphologie-aware **spec-only** : 12 décisions tranchées, garde-fou **strict** (0 posture/médical), substitution **réutilisée sans changement**, générateur étendu **additivement**, frontière **agent propose / déterministe décide**, confidentialité **0 photo + fixture privée Martin**, file de build en 5 items. **Zéro code, zéro migration, zéro rupture.**

---

## Appendice post-merge (closeout)

- **Merge** : PR **#60 MERGED** 2026-08-09, build `26c4bf2`, merge commit **`8d1ce98`** sur `claude/sprint-reporting-fitness-app-V7Qr6` via `--merge --match-head-commit 26c4bf2` — **sans squash, sans `--admin`** (gate `CLEAN`, 0 thread). `GO BUILD` → `GO MERGE` (protocole `CLAUDE.md §4`).
- **CI** : **CI de vérité = PR #60 run `31313414699` (`pull_request`) success** — 5 checks verts (lint · pytest+QA · Gitar · SonarCloud · SonarCloud Code Analysis), Sonar gate PR **OK** (0 issue neuve). Le merge est **100 % docs** → la CI push canonique est **légitimement skippée** (`paths-ignore: docs/**`, CLAUDE.md §2) : aucun run canonique pour `8d1ce98`.
- **Closeout** : docs-only (report + SPEC_REGISTRY + ROADMAP → MERGED). **Aucun code / migration / schéma / fixture personnelle** committé.
- **File de build ouverte sur GO** : `Sb_MORPHO_PROFILE_01` → `Sb_PROGRAM_SLOT_INTENT_01` → `Sb_MORPHO_PROGRAM_GENERATOR_01` → `Sb_MARTIN_PROGRAM_01` → `Sb_MORPHO_DOGFOOD_01`.
- **Cleanup** : branche `sb/sx-morpho-program-01-spec` + worktree `workout-session-tracking-morpho-spec` **conservés** — suppression = GO humain séparé.
