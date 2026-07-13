# Dogfood terrain — Session Active — 2026-07-13

**Type** : DOGFOOD REPORT — terrain réel, docs-only (aucun code touché)
**Statut** : 🟢 DÉBRIEF RÉDIGÉ — **non commité** (attente GO)
**Date** : 2026-07-13
**Sprint** : DOGFOOD_DEBRIEF_01 — Terrain Debrief Session Active

> Test terrain réel en situation de salle. NO CODE / NO COMMIT / NO DEPLOY.
> Saisie vocale Apple (FR) utilisée pour la prise de notes → certaines
> transcriptions à re-vérifier via capture d'écran (voir Irritant #1).

---

## 1. Contexte séance

| Champ | Valeur |
|---|---|
| Programme | _(à compléter par l'opérateur)_ |
| Chemin d'entrée | _(à compléter — candidats : reco_top / reco_alt / library carte / library CTA fiche / launcher / reprise)_ |
| Appareil utilisé | Mobile (iOS — dictée vocale Apple pour les notes) |
| Durée | _(à compléter)_ |
| Conditions réelles | Séance d'entraînement réelle en salle, app utilisée sans interruption de l'entraînement |

> Le contexte détaillé (programme exact, chemin, durée, fluidité set/reps) reste
> à renseigner par l'opérateur : l'observation terrain est celle de l'utilisateur
> en salle, non reproductible côté agent.

---

## 2. Irritant #1 — libellé de zone « Delt_lat »

- **Observé (terrain)** : sur la carte d'exercice, ligne « Principal » de « Zone
  travaillée », un libellé perçu comme technique (« Delt_lat » / « Dell latte »
  en dictée vocale) au lieu d'un texte humain.

- **Statut** : ⚠️ **NON REPRODUIT** (dans le code).

- **Preuve code (lecture seule)** :
  - Texte « Principal » = `_bmd.primary_label` si `status == "mapped"`, sinon
    `_family.name`, sinon « À qualifier »
    (`app/templates/_partials/exercise_card.html:153-157`).
  - `primary_label = _label_for(code, db)` →
    `ZONE_LABELS.get(code, code)` (`app/services/body_map_descriptor.py:81`,
    `app/services/muscle_mapping.py:24`).
  - **`ZONE_LABELS["delt_lat"] = "Deltoïdes latéraux"`** existe → le chemin
    nominal produit un **libellé humain**.
  - Fallback code brut = `delt_lat` (**minuscule / underscore**) ;
    `_family.name` (atlas) = **toujours humain** (« Épaules — Latéral /
    Postérieur »). Aucun chemin ne produit « Delt_lat » avec la casse Title
    observée.

- **Décision** : **attendre une capture d'écran** de la carte exercice. Le
  « Delt_lat » (casse Title) ne correspond à aucune sortie du code → **probable
  artefact de dictée vocale** (l'opérateur a signalé les fautes d'interprétation
  FR de la dictée). **Aucun fix sans preuve** : reproduction requise avant tout
  changement.

- **Si la capture confirme le bug** : chercher un point d'affichage hors ligne
  « Principal », ou un cas `status == "unknown"` particulier ; le correctif
  serait un **micro-fix isolé** (template/service), tier `isolated`.

---

## 3. Irritant #2 — visuel « Zone travaillée »

- **Observé (terrain)** : le visuel de zone (forme arrondie sous la carte)
  semble « sans fond », comme non configuré pour tous les exercices ; l'attente
  utilisateur est un **gabarit standard** commun à tous les exercices.

- **Statut** : ✅ **CONFIRMÉ.**

- **Preuve code (lecture seule)** :
  - CSS réel : `app/static/css/session_focus.css:1550-1584` — conteneur
    `.session-focus__body-map` (fond dégradé rayé + bordure) + forme
    `.session-focus__body-map-shape` (blob accent) + 6 variantes de zone
    (`pecs`, `upper_back`, `lats`, `delt_lat`, `quads`, `posterior`).
  - Le visuel est **volontairement un blob abstrait non-anatomique**
    (`session_focus.css:1547-1549` : « un simple bloc de zones abstraites en
    dégradé sobre — repère visuel, jamais anatomiquement précis (donc jamais un
    claim) »). `aria-hidden="true"`.

- **Analyse** : ce n'est **pas** un bug d'asset manquant — c'est un **repère
  décoratif anti-claim-médical** qui ne porte aucune information exploitable en
  salle → occupe de l'espace visuel sans aider. Le diagnostic terrain est juste.

- **Décision produit** : **futur sprint dédié `Sx_BODYMAP_01`**. Direction
  retenue (opérateur) : **vraie silhouette + zone surlignée** (gabarit SVG
  anatomique standard commun à tous les exercices, zone en surbrillance).
  **Aucun patch pendant le dogfood.** Enjeu à trancher en étape Brainstorming
  (CLAUDE.md §3) : **précision anatomique vs prudence claim médical** (le design
  actuel évite volontairement le claim), asset SVG, fallback pour les zones non
  couvertes, accessibilité (`aria-hidden` vs description).

---

## 4. Frictions restantes (fiche terrain — à compléter par l'opérateur)

Ces axes relèvent de l'usage réel en salle et ne sont pas reproductibles côté
agent ; ils sont laissés à renseigner :

| Axe | Observation terrain |
|---|---|
| Saisie charge / reps | _(trop lourde ? nombre de taps ? clavier ?)_ |
| Scroll | _(trop de scroll par exercice / série ?)_ |
| Reprise séance | _(bandeau « Séance en cours → Reprendre → » évident ?)_ |
| Repères de charge | _(charges précédentes utiles / intrusives / absentes ?)_ |
| Lisibilité mobile | _(tailles, contrastes, cibles tactiles ?)_ |
| Abandon éventuel vers Notes | _(y a-t-il eu un moment de bascule vers l'app Notes ? quand ?)_ |

> À ce stade, seuls #1 et #2 ont été remontés explicitement par l'opérateur. Les
> autres axes restent ouverts pour un prochain passage terrain.

---

## 5. Décision

- **Pas de code immédiat.** Le dogfood ne déclenche aucun commit de fix.
- **Priorité proposée** : **#1 Session active UX** — les deux irritants sont sur
  la carte d'exercice de la séance active (surface la plus utilisée en salle).
- **Prérequis pour #1** : **capture d'écran** de la carte exercice pour
  confirmer/infirmer avant tout micro-fix.
- **Pour #2** : **spec dédiée `Sx_BODYMAP_01`** (silhouette anatomique standard)
  — à ouvrir sur GO, avec étape Brainstorming obligatoire (précision vs claim
  médical).

---

## Verdict

**Verdict terrain :** 🟢 **GO corriger friction mineure** (sous conditions) —
l'app est utilisable en séance réelle ; deux irritants de la carte d'exercice
active sont remontés. **#1** (libellé zone) est **non reproduit** → **attendre
capture** avant tout fix. **#2** (visuel zone décoratif non-anatomique) est
**confirmé** → **spec dédiée `Sx_BODYMAP_01`** (direction : vraie silhouette +
zone surlignée), pas de patch pendant le dogfood. **Aucun code touché, aucun
commit de fix, aucun deploy.** Body Intelligence reste OFF.

**Suites** :
1. **Attendre la capture** de la carte exercice (débloque #1).
2. Si capture prouve le bug → **micro-fix label** isolé (tier `isolated`).
3. **Ouvrir `Sx_BODYMAP_01` spec** (silhouette) — étape Brainstorming d'abord.
4. Compléter le reste de la fiche terrain (saisie, scroll, reprise, repères,
   lisibilité) au prochain passage.
