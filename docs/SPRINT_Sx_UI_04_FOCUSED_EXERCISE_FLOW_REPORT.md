# Sprint Report — Sx_UI_04 Focused Exercise Flow Spec (Recadrage)

**Sprint ID :** `Sx_UI_04_FOCUSED_EXERCISE_FLOW` (recast)
**Type :** SPEC ONLY (docs-only) — sprint de **recadrage produit**
**Date :** 2026-07-04
**Auteur :** opérateur (Martin Feldmann) + agent Claude Code
**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`
**Verdict :** ✅ **READY FOR HUMAN REVIEW**

---

## 1. Résumé

Sprint spec-only qui **recadre la suite du build Sx_UI_04** (`Sb_UI_04.3` → `Sb_UI_04.5`) suite à la réserve visuelle explicite formulée à l'acceptance de `Sb_UI_04.2` (`docs/SPRINT_Sb_UI_04_2_HUMAN_REVIEW_REPORT.md` §5.2 + §7).

Bascule d'intention produit figée :

> Passer d'une **liste verticale de tous les exercices** à un **flow séquentiel single-active** : une seule carte d'exercice affichée à la fois, aperçu discret du suivant, progression globale en haut ("X / Y · N restants"), meilleur ancrage sur la zone musculaire travaillée, ton "instrumentale" premium.

**Amendement 2026-07-04 (brainstorm PO + lead architecte) — Live Exercise Expert Depth.** La spec a été **renforcée** au-delà du simple layout "une carte à la fois" : le cœur de l'écran devient un **active exercise cockpit** — un instrument live de type coach biomécanique expert. La spec ajoute 5 sections normatives (§18 Live Exercise Expert Model à 7 couches, §19 OQ tranchées par la direction produit, §20 build split renforcé, §21 visual asset strategy, §22 pedagogical interaction principles). **Sb_UI_04.3 doit désormais livrer une vraie rupture perceptible** : un simple recolor ou une simple liste accordéon est **explicitement rejeté**.

**Amendement final 2026-07-04 — Body Representation System (direction transverse).** La spec ajoute §23 : la représentation corporelle n'est plus un visual slot local mais une **couche transverse** de l'app — visible dans les cartes de séance, dans le profil utilisateur, et plus tard dans l'historique / progression / programme. Sont documentés : taxonomie V1 (15 zones), rôles biomécaniques (primary / secondary / stabilizer / systemic / mobility_control), contrat de données futur (`exercise_code → body_map_descriptor`), stratégie visuelle V1→V3, contraintes de prudence (jamais diagnostic médical), et direction Profile Body Intelligence future. **Le Worked Area Panel de Sb_UI_04.3 est le premier jalon** de ce système. Le profil / body intelligence est une **direction future, hors scope immédiat**. Rien implémenté : aucun modèle, aucune migration, aucun service touché, aucun asset.

La spec-parent `Sx_UI_04_SESSION_FOCUS_RESKIN_SPEC.md` est **conservée intacte** ; ce document la **recadre** pour la suite du build, sans invalider les décisions déjà validées par Sb_UI_04.1 et Sb_UI_04.2.

**BUILD BLOQUÉ** tant que cette spec n'est pas acceptée en human review.

## 2. Fichiers créés / modifiés

### Créés

- `docs/strategy/Sx_UI_04_FOCUSED_EXERCISE_FLOW_SPEC.md` — spec de recadrage, 17 sections
- `docs/SPRINT_Sx_UI_04_FOCUSED_EXERCISE_FLOW_REPORT.md` — ce rapport de sprint

### Modifiés

- `docs/strategy/SPEC_REGISTRY.md` — Sx_UI_04 recast pending review, Sb_UI_04.3 / .4 / .5 périmètre redéfini
- `docs/strategy/ROADMAP_AND_NEXT_STEPS.md` — position : prochaine action = human review Sx_UI_04 recast

## 3. Confirmation docs-only

**Scope strict respecté.** Aucun fichier hors `docs/` modifié :

- ❌ `app/` (aucun service, router, template, static, CSS, JS)
- ❌ `tests/`
- ❌ `migrations/`
- ❌ `scripts/`
- ❌ `.github/workflows/`
- ❌ `.env`, config runtime, manifest, favicon
- ❌ `requirements-lock.txt`, `pyproject.toml`, `package.json`
- ❌ Aucun screenshot capturé
- ❌ Aucun asset ajouté
- ❌ Aucun renommage `SPIGNOS` → `Auren` dans le code

## 4. Décisions prises (§ de la spec)

| # | Décision | Section |
|---|---|---|
| 1 | Passage d'une liste verticale à un flow séquentiel single-active | §2, §4 |
| 2 | Une seule hero card visible, aperçu compact "up next", progress rail en haut | §4, §5 |
| 3 | 6 blocs stables : header · progress rail · hero · set logging · worked area · up next (+ CTA + secondary access conditionnel) | §5 |
| 4 | Slot visuel muscle réservé mais **sans pipeline média** (V1 candidate placeholder) | §7, OQ-D |
| 5 | Redécoupage renforcé Sb_UI_04.3 = Active Exercise Cockpit Shell (Worked Area minimal dès V1), .4 = Set Logging Console + Progression Guidance, .5 = Worked Area Visual Slot + Alternatives + hardening | §9, §20 |
| 6 | 10 non-goals explicites (pas React, pas de génération image, pas de GIF, pas de migration, pas de rebrand code…) | §10 |
| 7 | 7 OQ **tranchées par la direction produit** en §19 (mini-stepper cliquable, jump bar compressée, worked area sous titre, panel statique V1, réouverture autorisée, up-next nom+rôle+zone, overview replié) | §11, §19 |
| 8 | Invariants techniques verrouillés : anchors `#exercise-N`, forms POST, contrats JS `data-*`, macros Jinja, no-JS fallback, WCAG 44×44 | §12 |
| 9 | Impact baseline P0 : `session-detail-active/*` modifiés, autres slugs inchangés | §13 |
| 10 | DoR pour Sb_UI_04.3 = cette spec acceptée + OQ tranchées + baseline P0 dispo | §14 |
| 11 | **Live Exercise Expert Model** : 7 couches (orientation · intent · worked area · cues · logging console · alternatives · up next) — cockpit d'exécution, pas conteneur de formulaire | §18 |
| 12 | **Visual asset strategy** : pas de GIF/génération V1, Worked Area Panel textuel + placeholder clinique, contrat futur `exercise_code → primary_zone → asset_key` | §21 |
| 13 | **Pedagogical interaction principles** : 1 décision principale, ≤3 cues, "pourquoi" en 1 phrase, logging < 5 s, progressive disclosure | §22 |
| 14 | **Body Representation System (couche transverse)** : 3 surfaces (session card · program preview · profile body intelligence), taxonomie V1 (15 zones), rôles biomécaniques, contrat futur `exercise_code → body_map_descriptor`, visuel V1→V3, prudence anti-médical | §23 |
| 15 | **Premier jalon** body system = Worked Area Panel de Sb_UI_04.3 ; profil/body intelligence = direction future hors scope | §23.2, §23.9 |

## 5. Points saillants pour la revue

Ce que l'opérateur doit valider en priorité (les OQ sont **déjà tranchées** par la direction produit en §19 — la revue confirme ou ajuste) :

1. **Direction produit** — le passage à un **active exercise cockpit** (Live Exercise Expert Model §18) correspond bien à l'intention ?
2. **Les 7 couches §18** (orientation · intent · worked area · cues · logging console · alternatives · up next) — priorisation correcte ?
3. **OQ tranchées §19** — confirmer : (A) mini-stepper cliquable · (B) jump bar compressée · (C) worked area sous titre avant sets · (D) panel statique V1 · (E) réouverture autorisée · (F) up-next nom+rôle+zone · (G) overview replié.
4. **Redécoupage §20** — Sb_UI_04.3 = Active Exercise Cockpit Shell (avec Worked Area minimal dès V1) · .4 = Set Logging Console · .5 = Visual Slot + Alternatives — bien articulé ?
5. **Worked Area dès 04.3** (pas repoussé en fin) car différenciant produit — d'accord ?
6. **Visual asset strategy §21** — pas de GIF V1, placeholder clinique, contrat futur `exercise_code → primary_zone → asset_key` — validé ?
7. **Principes pédagogiques §22** — logging < 5 s / ≤3 cues / progressive disclosure — validés ?
8. **Body Representation System §23** — direction transverse (session + profil + historique), taxonomie V1 (15 zones), contrat futur `exercise_code → body_map_descriptor`, prudence anti-médical — validée comme direction long terme ?
9. **Premier jalon §23.9** — Worked Area Panel de Sb_UI_04.3 accepté comme point d'entrée du body system, le profil restant hors scope immédiat ?
10. **Non-goals §10 + §23.10** — les listes couvrent-elles tous les périmètres à ne pas ouvrir (dont : pas de body map complète, pas de modèle, pas de diagnostic médical) ?

## 6. Confirmations sécurité et compat

- ✅ Aucun secret / cookie / token affiché ou committé
- ✅ Aucun PNG committé
- ✅ Aucun `runtime.json` / `auth-state.json` committé
- ✅ Aucun compte prod cité ou utilisé
- ✅ Aucune DB locale committée
- ✅ Aucun changement de contrat métier (services, models, migrations intacts)
- ✅ Body Representation System §23 = **documentaire uniquement** — aucun modèle, aucune migration, aucun service (`body_intelligence.py` non touché), aucune donnée runtime créée, aucun asset
- ✅ Aucun claim médical / physiologique fort — formulation prudente imposée (§23.7)
- ✅ Baseline P0 déjà capturée (`docs/BASELINE_P0_CAPTURED_2026_07_04.md`), non touchée par cette spec

## 7. Statut post-livraison de cette spec

| Item | Statut |
|---|---|
| `Sx_UI_04_FOCUSED_EXERCISE_FLOW_SPEC` | 🟢 **SPEC delivered — pending human review** |
| Parent `Sx_UI_04_SESSION_FOCUS_RESKIN_SPEC` | ✅ **conservée** (recadrée par ce document) |
| `Sb_UI_04.3 Active Exercise Cockpit Shell` | ⏸️ **BLOCKED** tant que ce recast n'est pas accepté |
| `Sb_UI_04.4 Set Logging Console + Progression Guidance` | ⏸️ **BLOCKED** |
| `Sb_UI_04.5 Worked Area Visual Slot + Alternatives + Hardening` | ⏸️ **BLOCKED** |
| Baseline P0 | ✅ CAPTURED 2026-07-04 (16/16 PNG) |
| Screenshots | 📁 local only, gitignored |
| Release tag baseline-preauren | ⏸️ deferred |

## 8. Prochaine action recommandée

1. **Human review** de `Sx_UI_04_FOCUSED_EXERCISE_FLOW_SPEC` (opérateur) — notamment le Live Exercise Expert Model §18.
2. **Confirmer OQ-A → OQ-G** (déjà tranchées §19, peuvent être ajustées).
3. **Puis ouvrir Sb_UI_04.3 Active Exercise Cockpit Shell** sur override explicite.

## 9. Références

- Spec principale : `docs/strategy/Sx_UI_04_FOCUSED_EXERCISE_FLOW_SPEC.md`
- Spec parent (conservée) : `docs/strategy/Sx_UI_04_SESSION_FOCUS_RESKIN_SPEC.md`
- Réserve visuelle source : `docs/SPRINT_Sb_UI_04_2_HUMAN_REVIEW_REPORT.md`
- Sb_UI_04.1 acceptance : `docs/SPRINT_Sb_UI_04_1_HUMAN_REVIEW_REPORT.md`
- Baseline P0 : `docs/BASELINE_P0_CAPTURED_2026_07_04.md`
- Registry : `docs/strategy/SPEC_REGISTRY.md`
- Roadmap : `docs/strategy/ROADMAP_AND_NEXT_STEPS.md`

## 10. Verdict final

✅ **READY FOR HUMAN REVIEW.**

**Aucun build ouvert. Sb_UI_04.3 code reste bloqué tant que cette spec n'est pas validée.**
