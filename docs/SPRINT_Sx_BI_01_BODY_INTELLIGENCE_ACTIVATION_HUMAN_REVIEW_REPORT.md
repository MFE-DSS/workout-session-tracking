# Human Review — Sx_BI_01 Body Intelligence Activation (Spec + Audit)

**Verdict** : ✅ **HUMAN REVIEW ACCEPTED**
**Date** : 2026-07-11
**Type** : revue humaine — docs-only (aucun code touché par cette revue)
**Spec** : [`strategy/Sx_BI_01_BODY_INTELLIGENCE_ACTIVATION_SPEC.md`](strategy/Sx_BI_01_BODY_INTELLIGENCE_ACTIVATION_SPEC.md)
**Audit** : [`SPRINT_Sx_BI_01_BODY_INTELLIGENCE_ACTIVATION_AUDIT_REPORT.md`](SPRINT_Sx_BI_01_BODY_INTELLIGENCE_ACTIVATION_AUDIT_REPORT.md)

---

## 1. Décision

**Sx_BI_01 est accepté.** Ce sprint **spec/audit docs-only** établit que Body
Intelligence n'est **pas un greenfield** : le socle Sx_31 (composer
`/body/intelligence`, flag-off) + Sx_32 (zones, mapping, `body_map_descriptor`)
existe déjà, et coexiste avec un **score global opaque LIVE** (`/physique` A/B/C +
radar). L'angle de reprise retenu — **Option A, Zone Intelligence Cards** — offre
une lecture **par zones traçable, confidence-aware et non médicale**, **sans
ajouter de second score opaque**, en réutilisant les signaux déjà calculés
(`muscle_scoring ZoneScore`). Aucun build n'est ouvert ; `Sb_BI_01.1` reste
**READY TO BE PROPOSED**.

---

## 2. Preuve (commit docs-only)

| Item | Valeur |
|---|---|
| **Commit spec/audit** | `d081f41d6ae4c79db4d72a709345f5ad45138af1` |
| **Type** | docs-only (4 fichiers) |
| **CI** | ⏭️ **skipped** (`paths-ignore: docs/**`) |
| **DoD** | check_scope=DOCS · spec_protocol ✅ · ruff 543 ≤ 548 ✅ · docs-only ✅ |

Aucun run CI pour `d081f41` (commit 100 % docs). `app/` et `tests/` intacts.

---

## 3. Éléments acceptés (checklist)

| Élément | Statut |
|---|---|
| Body Intelligence **n'est pas greenfield** | ✅ |
| Socle **Sx_31 + Sx_32** déjà présent | ✅ |
| `/body/intelligence` existe mais **flag-off / 404 prod** | ✅ |
| `/physique` **LIVE** avec **score global opaque A/B/C + radar** | ✅ |
| **Ne pas ajouter de second score global opaque** | ✅ |
| **Option A — Zone Intelligence Cards** retenue | ✅ |
| Réutiliser **`muscle_scoring ZoneScore`** | ✅ |
| **Aucun nouveau score** | ✅ |
| `Sb_BI_01.1` seulement **READY TO BE PROPOSED** | ✅ |
| Body Intelligence build **deferred until explicit GO** | ✅ |
| Dogfooding terrain Sx_DOGFOOD_01 **toujours à faire** | ✅ |
| Aucun code / modèle / migration / JS / home / session / deploy / release / claim médical | ✅ |

---

## 4. Angle validé — Zone Intelligence Cards (Option A)

Cards par zone (parmi les 11 zones seedées Sx_32), chacune : **volume récent**
(hard sets/semaine 30 j) · **tendance** (↑/→/↓) · **contribution** (part du volume
total) · **confidence** (badge élevée/moyenne/faible) · **mention non-médicale** ·
**drill** vers le détail. **Pas de radar opaque** (niveau 2, déjà sur `/physique`) ;
**pas de score global en tête** ; **mobile-first SSR** ; **silence** si données
insuffisantes. Réutilise les signaux déjà calculés — aucun score composite nouveau.

Positionnement face à l'existant :
- **vs `/physique`** (score A/B/C opaque LIVE) : ne pas dupliquer ; la décision
  produit sur ce score (garder / encadrer / déprécier) est reportée à `Sb_BI_01.next` ;
- **vs `/body/intelligence`** (composer flag-off) : reprise de cette page, section
  « Zones » en tête des blocs existants ;
- **Muscle table reste vide** (aucune anatomie fine inventée) ; zones inconnues → « À qualifier ».

---

## 5. Séparation signal / estimation / absence (acceptée)

Trois classes explicites conservées : `measured` (mensuration saisie), `derived`
(calculé depuis du réel : volume, ratios), `inferred` (heuristique : patterns), +
`not_deductible` (composition / esthétique / posture / médical). Les mensurations
restent une **classe séparée**, jamais fusionnées au volume. Les `DEFAULT_LIMITS`
non-médicaux et `FORBIDDEN_WORDING` du socle sont réutilisés tels quels.

---

## 6. Build split (validé)

| Sprint | Contenu | Statut |
|---|---|---|
| **Sb_BI_01.1** | Zone Intelligence Cards (reprise `/body/intelligence`) | 🟡 **READY TO BE PROPOSED, not opened** |
| Sb_BI_01.2 | Drill zone → détail (top exercices, historique volume) | futur |
| Sb_BI_01.3 | Radar niveau 2 (encadrer le score `/physique`) | futur |
| Sb_BI_01.next | Décision produit sur le score A/B/C de `/physique` | à cadrer |
| **Transformation corpus improvement** | Amélioration du corpus / mapping exercice→zone (couverture, qualité classification) | 🟡 **READY TO BE PROPOSED** |
| Différé | Home widget, insight post-séance, readiness/reco, carte graphique, activation `/body` | deferred |

---

## 7. Suite

| Piste | État |
|---|---|
| **Sb_BI_01.1** Zone Intelligence Cards | 🟡 READY TO BE PROPOSED, not opened |
| **Transformation corpus improvement sprint** | 🟡 READY TO BE PROPOSED |
| Dogfooding terrain Sx_DOGFOOD_01 | 🗓️ **pending** |
| Body Intelligence build | ⏸️ deferred until explicit GO |
| Deploy | ⏸️ deferred |
| Release tag | ⏸️ deferred |

---

## 8. Verdict

**Verdict :** ✅ **Sx_BI_01 Body Intelligence Activation — HUMAN REVIEW ACCEPTED.**

La reprise Body Intelligence est cadrée sur un socle **déjà implémenté mais
flag-off** (`/body/intelligence`) coexistant avec un **score global opaque LIVE**
(`/physique`). L'angle validé — **Option A, Zone Intelligence Cards** — offre une
lecture par zones **traçable, confidence-aware et non médicale**, sans second score
opaque, sans toucher home ni séance, en réutilisant `muscle_scoring ZoneScore` et
les fondations Sx_32 (Muscle vide). Aucun build ouvert : `Sb_BI_01.1` prêt à être
proposé, build deferred until explicit GO. Le dogfooding terrain Sx_DOGFOOD_01
reste à faire. Aucun code touché par cette revue.
