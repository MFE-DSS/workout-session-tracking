# Sb_BI_01.next — Physique Score Decision (Spec)

**Type** : PRODUCT DECISION / SPEC — docs-only, **aucun code**.
**Date** : 2026-07-11
**Statut** : 🟢 SPEC LIVRÉE — READY FOR HUMAN DECISION
**Rapport d'audit** : [`../SPRINT_Sb_BI_01_NEXT_PHYSIQUE_SCORE_DECISION_REPORT.md`](../SPRINT_Sb_BI_01_NEXT_PHYSIQUE_SCORE_DECISION_REPORT.md)

> **Objet** : trancher la place du **score global A/B/C opaque + radar** de `/physique`
> maintenant que `/body/intelligence` offre une **lecture par zones traçable**
> (Zone Cards + Drill). **Aucun code dans ce sprint** — décision + séquence future.

---

## 0. Étape 0 — Brainstorming / Options / Risques / Choix retenu

### Options

| Option | Description | Verdict |
|---|---|---|
| A | Garder `/physique` live, l'encadrer plus tard | ⚠️ acceptable **seulement si activation BI reste différée** (double lecture sinon) |
| **B** | **`/body/intelligence` = surface principale, déprécier progressivement `/physique`** | ✅ **RETENU (prudent)** |
| C | Fusionner `/physique` dans `/body/intelligence` | ❌ trop large, re-densification |
| D | Supprimer `/physique` | ❌ trop brutal, régression utilisateur/leaderboard |

### 15 sujets clivants tranchés

1. **`/physique` reste live après activation BI ?** → **Oui, temporairement** (dépréciation **progressive**, jamais brutale).
2. **Score A/B/C : gardé / masqué / encadré / déprécié ?** → **Encadré** (microcopy) puis **déprécié progressivement** ; **jamais renforcé**.
3. **Radar : visible ou secondaire ?** → **Secondaire** sur la trajectoire BI ; **conservé sur `/physique`** tant que la surface vit (et **requis par le leaderboard**, cf. §consommateurs).
4. **`/body/intelligence` = nouvelle surface principale ?** → **Oui** — future « lecture corporelle » principale.
5. **Renommer `/physique` ou garder la route ?** → **Garder la route** (compatibilité, liens, leaderboard) ; pas de rename.
6. **Lien `/physique` → BI ou l'inverse ?** → **`/physique` → `/body/intelligence`** (quand le flag BI est actif), pas l'inverse (BI ne doit pas pousser vers le score opaque). Le lien est un **futur build**, pas ce sprint.
7. **Éviter deux lectures concurrentes ?** → une seule surface **principale** (BI) ; `/physique` explicitement présentée comme **lecture synthétique héritée**.
8. **Expliquer que `/physique` est ancienne ?** → microcopy d'encadrement (« lecture synthétique héritée, voir la lecture par zones ») — **futur build** `Sb_BI_01.3`.
9. **Préserver leaderboard couplé ?** → **`compute_physique_dashboard` reste intact** ; le leaderboard utilise `radar_svg`/`radar_axes` — **ne pas toucher le service** ; déprécier la **surface** `/physique`, pas le service.
10. **Tests si on touche `/physique` plus tard ?** → régression `/physique` (rendu inchangé hors microcopy), leaderboard intact, no-nouveau-score, lien conditionnel au flag, wording non médical.
11. **Activer BI d'abord ou encadrer `/physique` d'abord ?** → **encadrer `/physique` d'abord** (`Sb_BI_01.3`), **puis** activation contrôlée du flag (`Sb_BI_01.activation`) — éviter la double lecture au moment de l'activation.
12. **Risque d'un score A/B/C opaque ?** → **fausse intelligence** / note corporelle non traçable ↔ contraire du principe Sx_TRANSFORM_01 « pas de score opaque ».
13. **Risque de retirer trop vite une surface live ?** → régression utilisateur + **casse leaderboard/user_profile/dashboard** (consommateurs de `compute_physique_dashboard`). D'où **dépréciation progressive**.
14. **Rester non médical ?** → toute microcopy d'encadrement reste non médicale ; `FORBIDDEN_WORDING` conservé.
15. **Séquence build minimale ?** → §3.

### Risques / parades

| Risque | Parade |
|---|---|
| Double lecture du corps (BI + score A/B/C) si flag activé sans encadrement | Encadrer `/physique` **avant** l'activation (`Sb_BI_01.3` avant `Sb_BI_01.activation`) |
| Casser leaderboard / user_profile / dashboard en dépréciant | **Ne pas toucher `compute_physique_dashboard`** ; déprécier la **surface**, pas le service |
| Suppression brutale | Interdite — dépréciation **progressive**, route conservée |
| Renforcer involontairement le score | Aucun nouveau score ; microcopy le **relativise**, ne l'amplifie pas |

---

## 1. Choix retenu — Option B (prudente)

- **`/body/intelligence` devient la future surface principale** « lecture corporelle »
  (Zone Cards traçables + Drill), une fois le flag activé.
- **`/physique` reste live temporairement** — dépréciation **progressive**, **pas de
  suppression**, route **conservée**.
- **Le score A/B/C n'est jamais renforcé** ; il sera **encadré** (microcopy) puis
  **déprioritsé**.
- **`compute_physique_dashboard` reste intact** (consommé par leaderboard,
  user_profile, dashboard.py) — on déprécie la **surface `/physique`**, jamais le
  service.
- **Aucune action code dans ce sprint** (décision + cadrage seulement).

---

## 2. Ce qui reste intact (garde-fous)

- `compute_physique_dashboard` (service) — **inchangé** ;
- leaderboard (radar mini) — **inchangé** ;
- `/physique` route — **conservée** ;
- `/body/intelligence` — **flag OFF prod**, inchangé ;
- aucun nouveau score ; non médical.

---

## 3. Séquence build future recommandée (sur GO séparé, hors de ce sprint)

| Ordre | Sprint | Contenu | Notes |
|---|---|---|---|
| 1 | **`Sb_BI_01.3` Physique Surface Guardrails** | microcopy d'encadrement du score sur `/physique` (« lecture synthétique héritée ») + lien vers `/body/intelligence` **si flag actif** | pas de nouveau score / radar / Home ; `compute_physique_dashboard` intact |
| 2 | **`Sb_BI_01.activation` Controlled BI Flag Activation** | activation contrôlée de `body_intelligence_enabled` (rendre `/body/intelligence` visible) | **uniquement après** `Sb_BI_01.3` (encadrement d'abord) + deploy GO explicite |
| futur | Dépriorisation `/physique` (nav, entrée secondaire) | reléguer `/physique` comme lecture héritée | progressif ; jamais suppression |
| futur | Volume par exercice dans le drill BI | enrichir la lecture par zones | rend BI encore plus complète avant de retirer `/physique` |

**Principe d'ordre** : **encadrer `/physique` AVANT d'activer BI** — éviter que
l'utilisateur voie deux lectures corporelles concurrentes au moment de l'activation.

---

## 4. Non-goals (ce sprint)

Pas de code · pas de template modifié · pas de CSS · pas de tests · pas d'activation
flag · pas de deploy · pas de release · **pas de suppression `/physique`** · pas de
changement leaderboard · **pas de nouveau score**.

---

## 5. Verdict

**Verdict :** 🟢 **Sb_BI_01.next Physique Score Decision — SPEC LIVRÉE, READY FOR HUMAN DECISION.**

**Choix : Option B prudente.** `/body/intelligence` (Zone Cards + Drill) devient la
future surface principale « lecture corporelle » ; `/physique` (score A/B/C opaque +
radar) reste live **temporairement**, déprécié **progressivement** — **route
conservée**, **`compute_physique_dashboard` intact** (leaderboard/user_profile/
dashboard préservés). Le score n'est **jamais renforcé** ; il sera **encadré**
(microcopy) puis déprioritsé. Séquence : **`Sb_BI_01.3` (encadrement) AVANT
`Sb_BI_01.activation` (flag)**. Aucun code, aucune suppression, aucun deploy dans ce
sprint. Non médical préservé.
