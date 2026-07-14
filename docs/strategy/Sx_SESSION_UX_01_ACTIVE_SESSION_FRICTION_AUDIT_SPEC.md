# Sx_SESSION_UX_01 — Active Session UX Friction Audit — SPEC / AUDIT

**Type** : SPEC / AUDIT ONLY — **NO CODE**
**Statut** : 🟢 AUDIT RÉDIGÉ — **non commité** (attente GO)
**Date** : 2026-07-14
**Origine** : DOGFOOD_DEBRIEF_01 (`c21bd9c`) — « prochain sujet prioritaire = friction carte exercice active »
**Contexte** : batch catalogue/lancement ACCEPTED ; `Sb_BODYMAP_01.1` ACCEPTED ; irritant `Delt_lat` **hors périmètre** (pending capture).

> Audit **lecture seule** du code de la séance active. Aucun fichier code modifié.

---

## 0. Étape 0 — Brainstorming / Options / Risques / Choix retenu

### 0.1 Honnêteté méthodologique (limite de l'audit)

Le dogfood terrain (DOGFOOD_DEBRIEF_01 §4) a **laissé les frictions saisie/scroll/reprise/repères
à compléter par l'opérateur** — elles ne sont **pas encore observées factuellement en salle**.
Cet audit qualifie donc des frictions **probables par lecture du code** (densité, ordre des blocs,
placement de l'action). Il ne peut pas affirmer qu'elles ont été *ressenties*. → Un build issu de
cet audit doit être **validé par un dogfood réel** (Sb_SESSION_UX_01.5).

### 0.2 Sujets clivants (décisions)

| # | Sujet | Décision |
|---|---|---|
| 1 | Saisie charge/reps ou navigation ? | **Ni l'un ni l'autre en premier** : la saisie est déjà solide (44px, 16px anti-zoom, mono) → le vrai enjeu est **où** la saisie tombe dans la carte. |
| 2 | Réduire scroll ou préserver l'info ? | **Réduire le scroll AVANT saisie** (repli/priorisation), sans supprimer l'info. |
| 3 | Charge précédente plus en avant ou discret ? | **Plus lisible au moment de saisir** (« Référence précédente » existe mais loin/haut). |
| 4 | Résumé compact par exercice ou éviter redondance ? | Le recap existe déjà (summary l.50/218) → **éviter d'en rajouter** (anti-re-densification). |
| 5 | Reprise via active-banner ou tel quel ? | **Tel quel** (le banner « Reprendre → » fonctionne ; pas prioritaire). |
| 6 | Progression visuelle intra-séance ou éviter gamification ? | **Éviter la gamification** ; la progression `x/y` séries/exercices existe déjà (sobre). |
| 7 | Simplifier submit ou form par exercice ? | **Form par exercice conservé** (contrat POST stable, no-JS). |
| 8 | Template/CSS seul ou route/services ? | **Template/CSS seul** — toutes les données existent déjà (overload_engine, last_time, descriptor). |
| 9 | JS vanilla ou no-JS ? | **No-JS** (Auren Terminal ; sticky déjà CSS-only). |
| 10 | Mobile 360px ou desktop ? | **Mobile 360px d'abord**. |
| 11 | Carte active seule ou toutes ? | **Carte active seule** (les cartes non-actives sont déjà repliées/compactes). |
| 12 | Sets plus compacts ou plus lisibles ? | **Plus lisibles** (jamais re-densifier) ; réduire le bruit **autour** des sets. |
| 13 | Placeholders de charge autrement ? | Piste : rapprocher « Référence précédente » de la ligne de saisie active. |
| 14 | Reporter à PWA/offline ? | **Non** — indépendant de PWA. |
| 15 | Build minimal suivant ? | Voir §4 shortlist + §5 reco. |

### 0.3 Options comparées

| Option | Description | Verdict |
|---|---|---|
| **A** | Audit → **micro-sprint template/CSS** (ré-ordonner/prioriser la carte active, rapprocher la saisie & la charge de référence) | ✅ **RETENU** — faible risque, ergonomie sans métier |
| B | Audit → sprint saisie set/reps | ❌ la saisie est déjà solide (44px/16px/mono) — faible ROI |
| C | Audit → sprint reprise/navigation | ❌ banner + jump bar + prev/next déjà fonctionnels |
| D | Ne rien faire avant nouveau dogfood | ⚠️ sûr mais lent ; **on garde l'idée** : le build A **doit** être dogfoodé (01.5) |

**Choix : Option A** — micro-sprint template/CSS ciblant la **densité / l'ordre des blocs** de la
carte active, **puis** dogfood de validation.

### 0.4 Risques & parades

| Risque | Parade |
|---|---|
| **Re-densifier** (interdit) | Ne rien ajouter ; **ré-ordonner/replier** seulement. |
| Casser les tests asservis carte active | Auditer AVANT build (`test_session_focus_*`, `test_ui06_dedup`) ; conserver classes/contrat POST. |
| Faux poids / score opaque | Aucune valeur injectée ; silence si donnée absente (règle produit). |
| Régresser Sb_BODYMAP_01.1 | Silhouette conservée telle quelle. |
| Claim médical | Aucun ; microcopy « non médicale » conservée. |

---

## 1. Flow complet de la séance active (audit lecture seule)

| Étape | Surface (fichier) | Constat |
|---|---|---|
| Entrée session | `GET /sessions/{id}` (`sessions.py`) | rendu SSR complet, ancre `#exercise-N`. |
| Active banner | `base.html` (`active-banner`) | « Séance en cours → Reprendre → » — OK. |
| Header + orientation | `session_detail.html` l.17-52 + `session_focus_header.html` | position `x/y exercice`, `n restants` — sticky. |
| Jump bar | `session_detail.html` l.61-83 | stepper sticky par exercice (code + `d/t`) + FB — OK, tap-target. |
| Carte active (hero) | `exercise_card.html` l.84+ | **dense** : Intention → Zone travaillée (silhouette) → Cues → Alternatives → …. |
| Référence précédente | `exercise_card.html` l.520-529 | « Référence précédente : X kg · Y reps » — **au-dessus** de la console, mais après beaucoup de contenu. |
| Console sets (saisie) | `exercise_card.html` l.532-577 | **5ᵉ bloc** de la carte active ; inputs 44px/16px/mono (solides), placeholder overload sur set actif. |
| Overload hints | `overload_hint.html` (via `overload_hints`) | état + cible + 0-3 raisons — données prêtes. |
| Feedback exercice | l.584-600 | Ressenti (details) + Note (details) — repliés, OK. |
| Submit / nav | l.652-673 | **CTA sticky CSS-only** « Enregistrer et passer à N » + prev ; fallback no-JS. |
| Exercice suivant | `sessions.py update_exercise_card` (nav next) | POST → redirect ancre. |
| Fin séance | `session_detail.html` l.140-195 | Bilan + « Enregistrer et terminer ». |

**Ordre réel des blocs sur la carte active** : Intention (l.96) → **Zone travaillée/silhouette** (l.137)
→ Cues techniques (l.188) → Alternatives (l.284) → **Référence + Console sets** (l.520). L'**action
principale** (saisir un set) est le **5ᵉ bloc** — précédée de 4 blocs de contexte.

---

## 2. Frictions probables (par lecture du code)

| Friction | Preuve code | Sévérité |
|---|---|---|
| **F1 — Saisie loin sous le contexte** : l'action principale (set) arrive après Intention+Silhouette+Cues+Alternatives → scroll avant de saisir | ordre l.96→520 | **P1** |
| **F2 — Charge de référence loin du point de saisie** : « Référence précédente » est en tête de console mais après tout le hero ; pas collée à la ligne active | l.520-529 vs set actif l.544 | **P1** |
| **F3 — Densité de la carte active** : intent + silhouette + cues + alternatives + refs + console + ressenti + note + up-next + rest timer sur un même écran mobile | hero l.84-681 | **P1** |
| **F4 — Alternatives (drawer) visible avant la saisie** : action secondaire (« Adapter l'exercice ») placée avant l'action primaire | l.284 avant l.532 | **P2** |
| **F5 — Cues techniques toujours dépliées** au-dessus de la saisie | l.188-201 | **P2** |
| **F6 — Inputs eux-mêmes** : taille/typo | l.226-238 CSS | **Non-friction** (déjà 44px/16px/mono/anti-zoom) |
| **F7 — Reprise séance** | active-banner + jump bar | **Non-friction** (fonctionnel) |
| **F8 — Boutons trop bas** | CTA sticky CSS-only l.652 | **Atténué** (sticky déjà présent) |

> Toutes les frictions P1/P2 identifiées sont **template/CSS** (ordre & repli), **sans métier**.
> Les données (overload, last_time, descriptor) sont déjà calculées côté router.

---

## 3. Classement des irritants

| Prio | Irritant | Nature |
|---|---|---|
| **P0** | *(aucun)* — rien ne **bloque** la saisie en salle ; la carte fonctionne | — |
| **P1** | **F1** saisie sous 4 blocs de contexte · **F2** charge de référence pas collée à la saisie · **F3** densité carte active | template/CSS |
| **P2** | **F4** alternatives avant saisie · **F5** cues toujours dépliées | template/CSS |

**Aucun P0** : l'app est utilisable en séance (confirmé dogfood). Les gains sont des **P1 d'ergonomie**.

---

## 4. Shortlist de builds possibles

| Build | Portée | Valeur | Risque |
|---|---|---|---|
| **Sb_SESSION_UX_01.1** — Compact set input ergonomics | inputs/console | faible (déjà bon) | faible |
| **Sb_SESSION_UX_01.2** — Active card **priorité action** : rapprocher la console de saisie du haut, replier cues/alternatives sous la saisie | template/CSS carte active | **élevée** (F1+F4+F5) | faible |
| **Sb_SESSION_UX_01.3** — **Previous load readability** : « Référence précédente » collée à la ligne active + placeholder cohérent | template/CSS | **élevée** (F2) | faible |
| **Sb_SESSION_UX_01.4** — Mobile scroll reduction : replier/condenser le hero non essentiel (F3) | template/CSS | moyenne | faible |
| **Sb_SESSION_UX_01.5** — Dogfood validation (terrain réel) | docs | **prérequis** | nul |

---

## 5. Recommandation — un seul build suivant

**Recommandation : `Sb_SESSION_UX_01.3` — Previous Load Readability** (F2, P1).

Justification :
- **Impact terrain le plus direct** en salle : au moment de saisir une charge, savoir *ce qu'on a
  fait la dernière fois* est **l'information n°1** — la coller à la ligne active supprime le
  va-et-vient mémoire/scroll.
- **Plus petit périmètre sûr** : « Référence précédente » et les placeholders overload **existent
  déjà** (données prêtes) → simple **repositionnement/lisibilité** template/CSS, zéro métier.
- **Respecte toutes les contraintes produit** : silence si pas de donnée (jamais de faux poids),
  pas de score opaque, non médical, pas de re-densification (on **déplace**, on n'ajoute pas),
  Auren Terminal (un seul accent), SSR/no-JS.
- **Prépare 01.2** : une fois la charge de référence lisible, ré-ordonner la carte (01.2) devient
  le pas suivant naturel.

**Séquence proposée** : `01.3` (charge lisible) → **dogfood 01.5** → si concluant, `01.2` (priorité
action) → `01.4` (scroll). `01.1` (inputs) **écarté** (déjà solide).

---

## 6. Non-goals

Cet audit et le build qui en découlera **n'incluent PAS** :

- **Aucun changement métier** : `sessions.py`, `overload_engine.py`, `overload_inputs.py`,
  `body_map_descriptor.py`, `muscle_mapping.py`, modèles, data, migrations restent **intacts**.
- **Aucune nouvelle donnée / aucun nouveau calcul** : on réutilise overload/last_time/descriptor déjà produits.
- **Pas de re-densification** : on déplace/replie, on n'ajoute pas de surface.
- **Pas de traitement de l'irritant `Delt_lat`** (pending capture, hors périmètre).
- **Pas de JS** (Auren Terminal, SSR/no-JS) ; **pas de React/SPA**.
- **Pas de gamification** / score opaque / faux poids (silence si donnée absente).
- **Pas de claim médical** ; silhouette `Sb_BODYMAP_01.1` conservée telle quelle.
- **Pas d'activation Body Intelligence**, pas de deploy, pas de release, pas de PWA/offline.
- **Aucun commit dans cet audit** (docs-only, sur GO explicite).

---

## Verdict

**Verdict :** 🟢 **Sx_SESSION_UX_01 — AUDIT RÉDIGÉ.**

La séance active est **fonctionnelle et sans P0** (aucun blocage salle). Les frictions **probables**
sont des **P1 d'ergonomie template/CSS** : **F1** saisie reléguée sous 4 blocs de contexte, **F2**
charge de référence pas collée à la saisie, **F3** densité de la carte active — plus deux P2 (F4
alternatives avant saisie, F5 cues dépliées). La **saisie elle-même est solide** (44px/16px/mono/
anti-zoom) → pas prioritaire. **Toutes les corrections sont template/CSS, sans métier** (overload/
last_time/descriptor déjà calculés). **Build recommandé : `Sb_SESSION_UX_01.3` Previous Load
Readability** (F2) — plus petit périmètre sûr, impact salle le plus direct — **suivi d'un dogfood
de validation (01.5)** car les frictions ne sont pas encore confirmées factuellement en salle.

**Recommandation de suite** :
1. **GO COMMIT SPEC** (docs-only) pour verser l'audit ; **ou**
2. **GO build `Sb_SESSION_UX_01.3`** (micro-sprint template/CSS, LOCAL BUILD) ; **ou**
3. **STOP** — attendre un nouveau dogfood terrain (compléter la fiche §4 du dogfood) avant de coder.
