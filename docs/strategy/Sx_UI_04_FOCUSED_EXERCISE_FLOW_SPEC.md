# Sx_UI_04 — Focused Exercise Flow Spec (Recadrage)

**Spec ID :** `Sx_UI_04_FOCUSED_EXERCISE_FLOW_SPEC`
**Cycle :** `Sx_UI` — Auren Visual & Product Transformation
**Type :** SPEC ONLY (docs-only) — sprint de **recadrage produit**
**Date d'ouverture :** 2026-07-04
**Auteur :** opérateur (Martin Feldmann) + agent Claude Code
**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`
**Depends on :**
- `Sx_UI_01_BRAND_FOUNDATION_SPEC.md` ✅ accepté
- `Sx_UI_02_DESIGN_TOKENS_SPEC.md` ✅ accepté
- `Sx_UI_03_APP_SHELL_NAVIGATION_SPEC.md` ✅ accepté
- `Sx_UI_04_SESSION_FOCUS_RESKIN_SPEC.md` ✅ accepté (spec-parent conservée, ce document la **recadre**)
- `Sx_UI_11_SCREENSHOT_REGRESSION_BASELINE_SPEC.md` ✅ accepté
- `Sb_UI_04.1` ✅ accepté (CSS Foundation)
- `Sb_UI_04.2` ✅ accepté **avec réserve visuelle** (Header & Jump Bar Structure)

---

## §1. Status

- **SPEC ONLY**
- **BUILD NOT AUTHORIZED** (aucun `Sb_UI_04.k` k≥3 ouvert)
- **Docs-only strict** — aucun `app/`, `tests/`, `migrations/`, `scripts/`, `.github/` touché
- Aucun CSS modifié, aucun template modifié, aucun JS modifié
- Aucun screenshot capturé, aucun asset ajouté
- Aucun renommage `SPIGNOS` → `Auren` dans le code (réservé Sx_UI_10)

**Ce document ne remplace pas `Sx_UI_04_SESSION_FOCUS_RESKIN_SPEC` — il en recadre la suite du build (`Sb_UI_04.3` → `Sb_UI_04.5`).** Les décisions déjà validées par Sb_UI_04.1 et Sb_UI_04.2 restent acquises (tokens Auren scopés, header Focus Mode restructuré, jump bar avec `aria-current="location"` + non-color cues).

> **Amendement 2026-07-04 (brainstorm PO + lead architecte)** — la spec est renforcée par le **Live Exercise Expert Model** (§18) : le cœur de l'écran n'est plus une "single active card" mais un **active exercise cockpit** (orientation · intent pédagogique · worked area · cues · logging console · alternatives · up next). Voir §18–§22. Les OQ sont tranchées par la direction produit en §19. Le build split est renforcé en §20.
>
> **Amendement final 2026-07-04** — la représentation corporelle devient une **couche transverse** (§23 Body Representation System) : visible dans les cartes de séance, le profil, et plus tard l'historique/progression/programme. Taxonomie, rôles biomécaniques, contrat de données futur et stratégie visuelle V1→V3 documentés — **rien implémenté** (aucun modèle, aucune migration, aucun asset).

## §2. Why this recast spec exists

Sb_UI_04.2 a été **accepté avec réserve visuelle explicite** (`docs/SPRINT_Sb_UI_04_2_HUMAN_REVIEW_REPORT.md` §5.2) : la transformation reste **trop proche d'un simple changement de couleur / polish léger**, et le cœur visuel de la séance reste encore trop proche de l'existant. Le verdict opérateur formule que le prochain build **ne doit pas être un simple recolor**.

Au-delà de la profondeur visuelle, une **intention produit nouvelle** émerge et doit être figée avant d'ouvrir `Sb_UI_04.3` :

> Le mode séance ne doit plus être une **liste verticale d'exercices affichés de haut en bas**. Il doit devenir un **flow séquentiel centré sur l'exercice actif du moment** : une seule carte d'exercice active à la fois, aperçu discret du suivant, progression globale lisible en haut, meilleur ancrage sur la zone musculaire travaillée.

Cette intention **modifie la topologie** de l'écran séance. Elle ne se réduit ni à un restyle CSS ni à un ajustement de partial. Elle exige un cadre spec explicite avant tout code — sinon `Sb_UI_04.3` risque de rejouer la même critique que Sb_UI_04.2 ("changement de peinture, pas d'expérience nouvelle").

## §3. Problème actuel (diagnostic)

État post-Sb_UI_04.2 :

- **P1. Liste verticale surchargée.** Tous les exercices sont dépliés / dépliables sur une même page longue. L'utilisateur voit simultanément l'exercice courant + N autres. L'attention se dilue.
- **P2. Focus séance dilué.** L'écran ne dit pas visuellement "voilà l'exercice à faire maintenant". La jump bar aide, mais l'ancre principale reste noyée dans le flux vertical.
- **P3. Hiérarchie visuelle insuffisamment marquée.** Le contraste entre l'exercice actif et les autres reste faible même après Sb_UI_04.2. La carte active n'a pas une présence "instrumentale" nette.
- **P4. Cœur de la séance pas assez centré.** La progression globale ("3 / 8", "N restants") n'est pas mise en avant. L'utilisateur doit reconstituer mentalement où il en est dans la séance.
- **P5. Lien exercice ↔ zone musculaire absent visuellement.** Aucun repère sur le split ou la zone travaillée. Aucune image / silhouette / illustration ne fait ce lien.
- **P6. Densité mobile ambigüe.** Sur 360×640, la liste verticale multiplie les scrolls et rend les CTA "logger" moins prééminents.

## §4. Cible UX

Vision cible en une phrase : **un mode séance qui fait avancer l'utilisateur exercice par exercice, sans surcharge cognitive, avec toujours en vue "où j'en suis, ce que je fais maintenant, ce qui vient ensuite, sur quelle zone".**

Points clés :

- **Une seule carte principale affichée** — l'exercice actif est la surface dominante.
- **Aperçu discret du prochain exercice** — juste ce qu'il faut pour anticiper (nom minimum, éventuellement zone).
- **Indication du nombre restant** — cadran clair : "3 / 8", "5 restants".
- **Progression globale lisible en haut** — barre / stepper / compteur, une seule source de vérité.
- **Meilleur lien exercice / split / zone travaillée** — visuel muscle / silhouette / illustration ou placeholder neutre selon options §7.
- **Ton visuel** — plus focus, plus calmement "instrumentale", plus premium (héritage Clinical Lab / Quiet Instrument déjà posé par Sb_UI_04.1).
- **Toujours mobile-first 360×640, no-JS fallback, WCAG 44×44, focus visible universel.**

## §5. Architecture UI cible (composants)

L'écran séance en mode séquentiel se décompose en **blocs stables**, dans cet ordre vertical par défaut (mobile) :

| # | Bloc | Rôle | Sensitivité |
|---|---|---|---|
| A | **Session header compact** | titre séance + status + retour | déjà stabilisé Sb_UI_04.2 (héritage) |
| B | **Progress rail / stepper / compteur** | "3 / 8 · 5 restants" + barre de progression globale | nouveau, remplace/enrichit la jump bar dense |
| C | **Active exercise hero card** | carte principale de l'exercice courant : nom, code, zone, historique compressé, hint overload, sets à logger | cœur de l'écran |
| D | **Set logging zone** | inputs weight/reps/complete, feedback discret, historique de la série précédente | déjà présent, à réhausser (Sb_UI_04.4) |
| E | **Worked area / muscle focus / visual slot** | slot dédié à un visuel de zone musculaire, silhouette, illustration ou placeholder | nouveau, contrat défini §7 sans pipeline média |
| F | **Rest timer** | timer inter-séries (héritage Sx_29, contrats `data-*` intacts) | invariant |
| G | **Up next** | aperçu compact du prochain exercice (nom, éventuellement zone) | nouveau |
| H | **Primary CTA** | "Valider série" / "Exercice suivant" selon l'état | déjà présent, promotion visuelle |
| I | **Secondary access aux autres exercices** | mini-stepper cliquable OU rien selon OQ-A/OQ-B | conditionnel |

**Ordre desktop (1440×900)** : possibilité de mettre le visuel muscle **à droite** de la hero card (grid 2 colonnes), progress rail toujours en haut. À trancher au build Sb_UI_04.3 selon breakpoints.

**Anti-modèle explicite** : plus de liste verticale de N `<details>` dépliables affichant N exercices simultanément.

## §6. Décisions à prendre sur l'affichage (design decisions)

Ces points nécessitent une position tranchée avant `Sb_UI_04.3`. Ils sont reformulés en OQ dans §11.

1. **Sort des autres exercices** — masqués complètement, réduits à un stepper minimal, ou accessibles via un panneau secondaire.
2. **Navigation secondaire** — la jump bar actuelle (livrée Sb_UI_04.2) devient-elle un mini-stepper compressé horizontal en haut ou est-elle retirée du DOM ?
3. **Réouverture d'un exercice précédent** — autorisée (retour libre) ou interdite (flow strictement séquentiel).
4. **Signalisation skipped / substituted / done** — préservée via les mêmes non-color cues qu'aujourd'hui, mais reportées dans le stepper compact plutôt que dans une liste dépliable.
5. **Préservation des contrats existants** — les anchors `#exercise-N`, le form `<form method="post">` de logging, le contrat JS `data-*` restent invariants. Un exercice non actif n'est pas supprimé du DOM : il est **masqué visuellement** (state hidden ou compact stepper) mais reste addressable.

## §7. Stratégie "visual slot" muscle / illustration

**Cette spec ne construit aucun pipeline média.** Elle définit uniquement le **contrat cible** pour que `Sb_UI_04.5` puisse construire un slot vide propre, prêt à recevoir des assets fournis plus tard.

Options envisagées pour V1 :

| Option | Description | Coût V1 | Extensibilité |
|---|---|---|---|
| **A. Placeholder neutre** | rectangle sobre avec libellé zone ("Pectoraux", "Ischio") — 0 asset | très faible | facile à substituer plus tard |
| **B. Silhouette / body-zone statique** | 1 seul SVG silhouette générique + surbrillance zone (mapping muscle → zone) | faible-moyen | bonne base, nécessite mapping exercice → zone |
| **C. Image par exercice fournie plus tard** | slot bind à un asset optionnel (`exercise.image_url` ou fichier statique) | faible (slot vide) mais bloqué sur asset | dépend de la fourniture d'images |
| **D. GIF / animation** | vidéo courte ou GIF de démonstration | **hors scope immédiat** | à évaluer post-V1 |

**Recommandation opérateur à confirmer (OQ-D)** : partir **Option A** en V1 (placeholder neutre + libellé zone), avec contrat CSS/template pensé pour basculer vers B ou C sans réécriture. Aucune décision définitive figée par cette spec — voir OQ-D.

**Non-goal explicite** : aucun script de génération d'images, aucun endpoint média, aucun stockage média dans cette spec.

## §8. Contraintes hard (invariants)

Rappelées ici en une liste dense car elles conditionnent la faisabilité des builds `Sb_UI_04.3` → `Sb_UI_04.5` :

- **Stack** : FastAPI SSR + Jinja2 conservés. **React prod interdit.**
- **Aucune migration** — modèles inchangés (`WorkoutSession`, `SessionExercise`, `SetLog`, `WorkoutTemplate`, `User`).
- **Aucun nouveau modèle** — pas de table image / asset / muscle_zone dans cette spec.
- **Aucun service métier touché** — `scoring/`, `substitution.py`, `coach_report.py`, `body_intelligence.py`, `overload_engine.py`, `recommendation.py` intacts.
- **No-JS fallback préservé** — la séance doit rester utilisable si JS bloqué (chaque `<form>` POST classique fonctionne, chaque set peut être loggé sans script).
- **Mobile-first 360×640** — cible primaire de conception.
- **WCAG 44×44** — tap targets préservés.
- **Focus visible universel** — outline 2px teal préservé.
- **`prefers-reduced-motion` préservé** — aucune animation lourde derrière cette media query.
- **Aucune réécriture métier du logging** — la logique de progression / substitution / overload reste identique.
- **Aucun renommage SPIGNOS → Auren** dans le code (réservé Sx_UI_10).
- **Anti-secret / anti-PNG committés** invariants (protocoles Sb_UI_11.x).

## §9. Redécoupage des builds (Sb_UI_04.3 → Sb_UI_04.5)

Le plan initial `Sx_UI_04_SESSION_FOCUS_RESKIN_SPEC` §19 découpait `Sb_UI_04.3` en "exercise cards + set logging". Ce redécoupage le remplace :

### `Sb_UI_04.3 — Single Active Exercise Shell`

**But :** basculer la topologie de l'écran d'une liste verticale à un flow séquentiel single-active. Aucun set logging touché.

Portée :
- Modifier `session_detail.html` pour rendre visible **uniquement** l'exercice courant (les autres restent dans le DOM pour préserver anchors `#exercise-N` et no-JS, mais deviennent visuellement compacts / masqués selon OQ-A).
- Introduire le **progress rail / stepper / compteur** en haut ("3 / 8 · 5 restants" + barre).
- Retirer ou compresser la jump bar dense (OQ-B).
- Introduire le bloc **"Up next"** compact (nom du prochain exercice minimum).
- Préserver rigoureusement contrats JS `data-*`, macros Jinja invariantes, tap targets, no-JS.

Zones touchées maximales :
- `app/templates/session_detail.html`
- `app/templates/_partials/session_focus_header.html` (progress rail intégré ou nouveau partial `session_focus_progress.html`)
- `app/static/css/session_focus.css` (styles progress rail, hero card frame, up-next block, hidden state pour exercices non actifs)
- Éventuellement nouveau partial `_partials/session_focus_up_next.html`

Interdit :
- ❌ Aucun changement de logique métier
- ❌ Aucun changement au form de logging
- ❌ Aucune migration
- ❌ Aucun asset

Tests attendus :
- Un seul exercice visible mobile 360×640
- Progress rail présent avec compteur X/Y et restants
- Up next présent avec nom du prochain exercice
- Anchors `#exercise-N` toujours addressables (no-JS fallback)
- Tap targets 44×44 préservés
- `aria-current="location"` reporté sur l'active dans le stepper

Après-screenshots attendus : delta visible sur `session-detail-active/mobile` et `session-detail-active/desktop`.

### `Sb_UI_04.4 — Set Logging Focus + Next Exercise Flow`

**But :** rehausser la zone set logging + fluidifier le passage à l'exercice suivant. Rest timer touché uniquement en styling léger.

Portée :
- Refonte visuelle de la zone set logging à l'intérieur de la hero card (input weight/reps, feedback, historique série précédente compressé, hint overload plus lisible).
- Séparation instrumentale input / feedback / progression au niveau du set.
- Promotion visuelle du CTA principal (validation série / exercice suivant selon état).
- Flow "exercice suivant" : au CTA final d'un exercice, transition claire vers le suivant sans changer la route (peut rester ancre + reload ou form POST classique).
- Éventuellement styling léger rest timer (contrats `data-*` intacts).

Zones touchées maximales :
- `app/static/css/session_focus.css`
- `app/templates/_partials/exercise_card.html` (structure interne set logging)
- `app/templates/_partials/rest_timer.html` (styling léger uniquement, contrats intacts)
- `app/templates/session_detail.html` (marges / wrappers)

Interdit :
- ❌ Aucun changement de logique métier
- ❌ Aucune migration
- ❌ Aucun asset

Tests attendus :
- Set logging visuellement distinct (input / feedback / historique clairement séparés)
- CTA primaire dominant
- Passage exercice suivant fonctionnel avec no-JS
- Rest timer contrats `data-*` intacts

### `Sb_UI_04.5 — Worked Area Visual Slot + Hardening`

**But :** introduire le slot muscle / zone travaillée + polish final Sx_UI_04.

Portée :
- Introduire le **visual slot** (Option A placeholder par défaut, avec CSS/template prêt pour B ou C — voir OQ-D).
- Éventuellement introduire un mapping léger côté template `exercise.zone_label` (attribut snapshot déjà présent : `exercise_name_snapshot`, `exercise_code_snapshot`) — sans nouveau champ modèle.
- Polish mobile / desktop / a11y (contraste, focus, reduced motion).
- Closure Sx_UI_04.

Zones touchées maximales :
- `app/static/css/session_focus.css`
- `app/templates/_partials/exercise_card.html` (ou nouveau partial `_partials/session_focus_area_visual.html`)
- Éventuellement libellés zone dans les templates si mapping trivial via données existantes

Interdit :
- ❌ Aucun asset image ajouté (le slot reste vide en Option A)
- ❌ Aucun pipeline média
- ❌ Aucun nouveau modèle
- ❌ Aucune migration

**Post-Sb_UI_04.5 : Sx_UI_04 closable si dogfood OK.**

## §10. Non-goals explicites

- ❌ Aucune **génération automatique d'images** dans l'app
- ❌ Aucun **pipeline GIF / vidéo / animation**
- ❌ Aucune **refonte du moteur métier séance** (scoring, substitution, overload, recommandation)
- ❌ Aucun **changement de modèle** (`WorkoutSession`, `SessionExercise`, `SetLog`, etc.)
- ❌ Aucune **refonte globale hors écran séance** (home, profile, progression, login/register hors scope)
- ❌ Aucun **global app shell** dans ce sprint (bottom nav Sx_UI_03 non touchée)
- ❌ Aucune **intégration React** (SSR + Jinja exclusivement)
- ❌ Aucune **dépendance front lourde** ajoutée
- ❌ Aucun **rebrand SPIGNOS → Auren** dans le code
- ❌ Aucun **release tag** émis par cette spec
- ❌ Aucun **screenshot committé** (baseline + after restent gitignored)

## §11. Open Questions (OQ)

Sept questions à trancher avant l'ouverture de `Sb_UI_04.3`. Les positions "V1 candidate" ci-dessous étaient les propositions initiales de l'agent. **Elles ont été tranchées par la direction produit (PO + lead architecte) — voir §19 pour les décisions faisant foi**, à confirmer en human review. En cas d'écart, **§19 prévaut sur la colonne "V1 candidate"**.

| ID | Question | Options | V1 candidate |
|---|---|---|---|
| **OQ-A** | Mode séquentiel : strict ou avec mini-stepper cliquable ? | (a) strict : seul l'actif visible, non cliquable ; (b) stepper : ronds/segments compacts en haut, cliquables pour rouvrir un exercice passé ; (c) hybride : stepper visible mais navigation cliquable réservée à un mode "overview" | **(b) mini-stepper cliquable** — préserve l'esprit "focus" (une carte active) tout en offrant une porte de sortie sans casser les anchors |
| **OQ-B** | Conserver la jump bar actuelle (livrée Sb_UI_04.2) sous forme compressée ? | (a) la jump bar dense reste, sous forme scrollable horizontale compacte ; (b) elle est remplacée par le stepper `OQ-A` ; (c) elle est retirée du DOM | **(b) remplacée par stepper** — évite deux systèmes de navigation redondants ; les non-color cues des cards actuelles migrent dans le stepper |
| **OQ-C** | Ordre du bloc visuel muscle | (a) au-dessus de la hero card (met la zone en avant) ; (b) au-dessous de la hero card, avant set logging ; (c) latéral desktop uniquement (grid 2 colonnes) | **(c) latéral desktop, (b) sous hero mobile** — respecte la hiérarchie "quoi > où" mobile, exploite la largeur desktop |
| **OQ-D** | Stratégie asset V1 | (A) placeholder neutre ; (B) silhouette SVG statique + surbrillance zone ; (C) image par exercice fournie plus tard ; (D) GIF (hors scope immédiat) | **(A) placeholder V1**, contrat CSS/template prêt pour (B) ou (C) — permet livraison sans dépendance asset externe |
| **OQ-E** | Réouverture libre d'un exercice déjà passé ? | (a) oui, sans restriction ; (b) oui, mais confirmation ; (c) non (flow strict) | **(a) oui sans restriction** — cohérent avec OQ-A (b), no-JS fallback préservé (anchors `#exercise-N` toujours addressables) |
| **OQ-F** | Aperçu "up next" — informations affichées | (a) nom seulement ; (b) nom + zone ; (c) nom + zone + reps/charge cible | **(b) nom + zone** — donne le contexte d'anticipation sans encombrer, aligne avec la stratégie muscle-focus |
| **OQ-G** | Prévoir un mode "overview" secondaire (vue toutes cartes compressées) ? | (a) oui, écran/mode dédié ; (b) non, le stepper suffit ; (c) reporter à Sx_UI_04.next | **(b) non** — le stepper `OQ-A` couvre le besoin d'anticipation, un mode overview séparé duplique la complexité |

## §12. Contraintes de compatibilité (invariants techniques)

Éléments dont la préservation est **non-négociable** pour éviter de casser les contrats déjà validés :

- **Anchors `#exercise-N`** — chaque `SessionExercise` reste addressable par ancre, même masqué visuellement. Un exercice non actif est **hidden**, jamais supprimé du DOM (`hidden` attribute HTML natif ou classe CSS `session-focus__card--collapsed` avec `aria-hidden` selon OQ-A).
- **Form logging** — `<form method="post" action="/sessions/{id}/exercises/{ex_id}/sets/...">` reste identique. Les inputs `weight_kg`, `reps`, `completed` inchangés.
- **Contrats JS `data-*`** — `data-start-rest`, `data-rest-duration`, `data-rest-skip`, `data-rest-display` invariants.
- **Macros Jinja** — `segmented`, `field_group` non modifiées.
- **`aria-current="location"`** — reporté sur l'item actif du stepper (OQ-A/B).
- **`aria-live="polite"`** rest timer — invariant.
- **Tap targets 44×44** — préservés partout, y compris dans le stepper compact.
- **Focus visible universel** — outline 2px teal préservé.
- **`prefers-reduced-motion`** — aucune animation lourde derrière cette media query.
- **No-JS fallback** — si JS bloqué, l'utilisateur peut toujours (a) voir tous les exercices via un fallback `<noscript>` ou classe CSS `.no-js` qui rétablit une liste, (b) logger un set, (c) valider le form. À designer précisément au moment de `Sb_UI_04.3`.
- **Aucun runtime artefact committé** — `runtime.json`, `auth-state.json`, `.env.baseline` restent gitignored.

## §13. Impact sur baseline visuelle P0

La baseline P0 capture les 8 slugs × 2 viewports = 16 PNG (cf. `docs/BASELINE_P0_CAPTURED_2026_07_04.md`).

`Sb_UI_04.3` **modifie substantiellement** :
- `session-detail-active/mobile` et `session-detail-active/desktop` — refonte topologique
- éventuellement `session-detail-done/mobile` et `session-detail-done/desktop` selon rendu terminé du flow

**N'affecte pas** :
- `home-authenticated`, `home-no-active-session`, `progression`, `profile`, `login`, `register`

Chaque build `Sb_UI_04.k` (k≥3) doit :
1. Rester capturable en P0 après build (`ok=16 failed=0` via `visual_baseline_capture.py`)
2. Produire un rapport `after-screenshots` locaux + comparaison humaine
3. Ne rien committer côté PNG / runtime

## §14. Definition of Ready (DoR) pour Sb_UI_04.3

Avant d'ouvrir `Sb_UI_04.3`, il faut :

- ✅ Cette spec (`Sx_UI_04_FOCUSED_EXERCISE_FLOW_SPEC.md`) acceptée en human review
- ✅ OQ-A → OQ-G tranchées V1 (positions confirmées ou modifiées par l'opérateur)
- ✅ Baseline P0 disponible (déjà OK, capturée 2026-07-04)
- ✅ HEAD sur origin propre, working tree clean

## §15. Definition of Done (DoD) pour cette spec (Sx_UI_04 recast)

- ✅ Fichier `docs/strategy/Sx_UI_04_FOCUSED_EXERCISE_FLOW_SPEC.md` créé (ce document)
- ✅ Fichier `docs/SPRINT_Sx_UI_04_FOCUSED_EXERCISE_FLOW_REPORT.md` créé
- ✅ `docs/strategy/SPEC_REGISTRY.md` mis à jour (référence recast + statut Sb_UI_04.3/.4/.5 recadré)
- ✅ `docs/strategy/ROADMAP_AND_NEXT_STEPS.md` mis à jour (position claire : spec recast pending human review, aucun build ouvert)
- ✅ Diff `git diff --name-only` = uniquement sous `docs/`
- ✅ Aucun fichier hors `docs/` touché
- ✅ `check_spec_protocol` OK (référence croisée valide)
- ✅ `check_ruff_budget` non impacté (aucun code Python touché)

## §18. Live Exercise Expert Model

> **Recadrage produit majeur (amendement 2026-07-04).** Le cœur de l'écran séance n'est **plus** une "exercise list", ni même une "single active card". C'est un **active exercise cockpit** : un instrument live qui accompagne l'utilisateur exercice par exercice comme le ferait un coach biomécanique expert.

L'écran séance doit répondre, au bon moment et sans surcharge, à trois questions :

1. **Qu'est-ce que je fais maintenant ?**
2. **Pourquoi je le fais dans cette séance ?**
3. **Comment je l'exécute proprement — et que faire si ce n'est pas adapté ?**

Positionnement produit différenciant (issu du benchmark Strong / Fitbod / Jefit / Freeletics) :

> **Strong** pour la rigueur de logging · **Fitbod** pour le "quoi faire ensuite" · **Jefit** pour l'instruction et les métriques · **Freeletics** pour la sensation de coach adaptatif — **+ une couche biomécanique plus froide, plus instrumentale, plus experte** (Clinical Lab / Quiet Instrument déjà posé par Sb_UI_04.1). Le produit visé n'est **pas** "Strong en plus joli", c'est un **Live Exercise Expert**.

Ce n'est **ni** un coach motivationnel, **ni** un chatbot, **ni** une liste d'exercices. C'est un cockpit d'exécution.

La carte active se structure en **7 couches normatives** :

### §18.A — Orientation

L'utilisateur sait immédiatement où il en est, sans réflexion. Dans le header (ou juste sous) :

- exercice courant / total (`3 / 8`)
- exercices restants (`5 restants`)
- progression de séance (barre + %)
- set courant / total (`Set 2 / 4`)
- repos conseillé si pertinent (`90 s`)

Cible : lisible en < 1 s, aucun calcul mental.

### §18.B — Exercise Intent (intention pédagogique)

Chaque exercice dit **pourquoi il existe dans cette séance**. Format court, jamais un article :

- **But du bloc** : 1 phrase (ex. "Renforcer la poussée horizontale lourde.")
- **Rôle dans le split** : 1 phrase (ex. "Stimulus principal pectoraux / triceps, avant isolation.")
- **Pourquoi maintenant** : 1 phrase (ex. "Placé tôt car demande le plus de fraîcheur technique.")

Maximum ~3 phrases. Le "pourquoi" en 1 phrase par item.

### §18.C — Worked Area (zone travaillée)

Le visuel n'est **pas un gadget décoratif** — c'est un **Worked Area Panel** qui répond à : quelle zone est principalement attaquée, quelle zone assiste, quelle zone doit rester stable.

- **Zone principale** (ex. Pectoraux)
- **Assistants** (ex. Triceps · Deltoïde antérieur)
- **Stabilisation** (ex. Scapula · Gainage)
- **Visual slot froid / clinique** : silhouette statique / schéma simple / placeholder anatomique

Philosophie bodybuilding en split : mettre en avant les muscles sous-jacents travaillés dans le groupe musculaire de la séance. **V1 = panneau textuel + placeholder clinique** (pas de GIF, voir §21).

### §18.D — Technical Cues (exécution)

Cues courts, actionnables. **Maximum 3 cues visibles par défaut**, le reste en détail replié (progressive disclosure) :

- ex. `1. Omoplates fixées · 2. Descente contrôlée · 3. Trajectoire stable`

### §18.E — Set Logging Console

La saisie des sets n'est plus un formulaire brut mais une **console instrumentale** :

- sets réalisés (avec cue ✓ non-color)
- set actif (inputs charge / reps mis en avant)
- target reps / charge (fourchette cible)
- previous performance si disponible (perf précédente de l'exercice)
- hint surcharge lisible (issu `overload_engine` — **présentation uniquement, aucune logique métier touchée**)

### §18.F — Alternatives / Substitution affordance

Pendant une séance, l'utilisateur doit pouvoir répondre à : *je n'ai pas la machine · j'ai une gêne · c'est trop dur · trop facile · je veux une alternative équivalente.*

- accessible mais **non dominante** (pas anxiogène)
- alternative **expliquée** par pattern / zone / contrainte (ex. "Même pattern : poussée horizontale · même zone : pectoraux dominant · moins contraignant épaules : dumbbell press")

C'est ici que le **graphe de substitutions** (`substitution.py`) devient produit, pas seulement backend. **Aucune modification de la logique de substitution** — surface d'affichage uniquement.

### §18.G — Up Next

Aperçu du prochain exercice, **sans surcharge cognitive** :

- nom du prochain exercice
- rôle court (1 phrase)
- zone principale
- **pas** de charge / reps complets (voir OQ-F §19)

### §18.H — Topologie de carte active (schéma cible)

```
┌────────────────────────────────────┐
│ Header séance                       │
│ Push A · Exercice 3/8 · 5 restants  │
│ ███████░░░ 38%                      │
└────────────────────────────────────┘
┌────────────────────────────────────┐
│ ACTIVE EXERCISE                     │
│ Développé couché haltères           │
│ Pectoraux dominant · Push horizontal│
│                                     │
│ [Worked Area Panel]                 │
│ Principal: Pectoraux                │
│ Assistants: Triceps · Delto ant.    │
│ Stabilise: Scapula                  │
│                                     │
│ Pourquoi cet exercice ?             │
│ Stimulus principal du bloc push.    │
│ Placé tôt car technique + charge.   │
│                                     │
│ Cues techniques                     │
│ 1. Omoplates fixées                 │
│ 2. Descente contrôlée               │
│ 3. Trajectoire stable               │
│                                     │
│ Sets                                │
│ 1  22kg × 10  ✓                     │
│ 2  [ kg ] [ reps ]  CTA             │
│ 3  prévu                            │
│                                     │
│ Hint surcharge                      │
│ Reste dans la fourchette haute.     │
│                                     │
│ [Valider set] [Alternative]         │
└────────────────────────────────────┘
┌────────────────────────────────────┐
│ Up next                             │
│ Écarté incliné — isolation pec haut │
└────────────────────────────────────┘
```

**La carte active est un cockpit d'exécution, pas un conteneur de formulaire.**

## §19. OQ Decisions Recommended by Product Direction

Tranchées par la direction produit (PO + lead architecte, brainstorm 2026-07-04). Ces positions **remplacent** les "V1 candidate" du tableau §11 et sont à confirmer en human review :

| ID | Décision produit tranchée |
|---|---|
| **OQ-A** | **Mini-stepper cliquable**, pas séquentiel strict. L'utilisateur doit pouvoir revenir à un exercice précédent. |
| **OQ-B** | Jump bar **conservée mais compressée** en stepper secondaire (pas la navigation principale). |
| **OQ-C** | Worked Area **dans la carte active, sous le titre, avant les sets** — il explique l'exercice avant l'action. |
| **OQ-D** | **V1 = Worked Area Panel statique** (textuel + placeholder clinique) + contrat asset futur — **pas** placeholder vide. |
| **OQ-E** | **Rouvrir un exercice passé autorisé** (en muscu réelle on revient corriger / compléter). |
| **OQ-F** | Up-next = **nom + rôle court + zone principale** — pas charge complète. |
| **OQ-G** | **Overview secondaire replié** ("Vue séance" / stepper compact) — pas de liste dominante. |

## §20. Revised Build Split

Le découpage §9 est **renforcé** : Sb_UI_04.3 ne fait plus seulement "shell topologique", il livre une **rupture perceptible** dès V1, incluant un Worked Area Panel minimal textuel.

### `Sb_UI_04.3 — Active Exercise Cockpit Shell`

- **Objectif** : casser la perception de liste verticale, introduire la **carte active dominante** comme cockpit.
- **Inclure dès V1** un **Worked Area Panel minimal textuel** (zone principale / assistants / stabilisation) + Exercise Intent (pourquoi maintenant) + orientation (X/Y, restants, progression).
- Touches : `session_detail.html` + `exercise_card.html` + `session_focus.css` + tests.
- **Livrable visible** : une seule expérience centrée sur l'exercice actif, avec pédagogie textuelle immédiate. **Simple recolor / simple accordéon explicitement rejeté.**

### `Sb_UI_04.4 — Set Logging Console + Progression Guidance`

- **Objectif** : rendre la saisie des sets **instrumentale et pédagogique**, moins formulaire.
- Touches : `exercise_card.html` + `session_focus.css` + présentation du hint overload.
- **Livrable visible** : logging console, previous performance, target range, feedback.

### `Sb_UI_04.5 — Worked Area Visual Slot + Alternatives Surface + Hardening`

- **Objectif** : enrichir le visuel muscle / zone + rendre les alternatives visibles, sans pipeline média lourd.
- Touches : `exercise_card.html` + substitution affordance (surface) + `session_focus.css`.
- **Livrable visible** : zone travaillée enrichie visuellement, rôle musculaire, alternative équivalente expliquée.

> **Note** : le Worked Area apparaît **dès 04.3** en version simple (textuelle), puis est **enrichi en 04.5** (visuel). Il n'est pas repoussé en fin de cycle car c'est un différenciant produit.

## §21. Visual Asset Strategy

Décisions figées :

- **Pas de GIF pipeline en V1** (distraction, perf, a11y, copyright, maintenance).
- **Pas d'image générée automatiquement** dans l'app.
- **Pas d'asset externe obligatoire** pour Sb_UI_04.3.
- **V1 doit fonctionner** avec un Worked Area Panel textuel + placeholder clinique (schéma statique froid, très simple, remplaçable).
- **V2 pourra accepter** des assets fournis par l'opérateur.
- **Contrat futur recommandé** :
  ```
  exercise_code → primary_zone → asset_key
  asset_key → static image / SVG / GIF later
  ```
- Tous les médias futurs devront respecter **`prefers-reduced-motion`** et un **fallback statique**.

À terme (hors ce cycle) : feature visuelle sur chaque carte mettant en avant les **muscles sous-jacents** travaillés dans le groupe musculaire de la séance, dans la philosophie du **bodybuilding en split**.

## §22. Pedagogical Interaction Principles

Principes normatifs pour tout build `Sb_UI_04.k` (k≥3) :

- **Une seule décision principale à la fois.**
- **Maximum 3 cues techniques visibles** (reste replié).
- **Expliquer le "pourquoi" en 1 phrase.**
- **Ne pas transformer l'écran en article.**
- **Progressive disclosure** : le détail est disponible, pas imposé.
- **Alternatives disponibles mais pas anxiogènes.**
- **L'utilisateur fatigué doit pouvoir logger en < 5 secondes.**
- **L'utilisateur curieux doit pouvoir ouvrir les détails.**

Ces principes arbitrent tout conflit densité vs pédagogie : le logging rapide prime pour l'utilisateur pressé, la profondeur reste accessible pour l'utilisateur curieux.

## §23. Body Representation System, Session + Profile Direction

> **Amendement final 2026-07-04.** La représentation corporelle ne doit **pas** rester un visual slot local dans une carte d'exercice. Elle devient à terme une **couche transverse** de l'app, visible pendant la séance (cartes), dans le profil utilisateur, et plus tard dans l'historique / progression / programme. Cette section pose la **direction long terme** sans rien implémenter.

### §23.1 — Principe produit

La représentation corporelle **n'est pas décorative**. Elle sert à rendre visible :

- la **zone principale** travaillée ;
- les **muscles assistants** ;
- les **stabilisateurs** ;
- le **pattern moteur** ;
- le **rôle de l'exercice dans le split** ;
- la **distribution de charge** du programme ;
- l'**historique des zones** entraînées dans le profil.

### §23.2 — Surfaces cibles

Trois surfaces réutilisent la même couche body :

**A. Session Active Exercise Card** (jalon Sb_UI_04.3)
- affiche la zone travaillée **maintenant** ;
- explique primary / secondary / stabilizers ;
- reste **compact** ;
- aide à comprendre l'**intention biomécanique** de l'exercice.

**B. Program / Session Preview** (futur, Sx_UI_05 / programme)
- affiche le **split prévu** ;
- montre les **zones dominantes** de la séance ;
- aide à comprendre **pourquoi** ces exercices sont groupés.

**C. Profile / Body Intelligence** (futur, profil / Sx_UI_07)
- affiche la **distribution des zones** travaillées dans le temps ;
- met en évidence zones **dominantes**, **sous-stimulées**, **déséquilibres potentiels** ;
- relie séances, historique et progression ;
- **ne prétend pas** à une vérité médicale.

### §23.3 — Taxonomie V1

Taxonomie simple des zones (labels V1) :

`chest / pectoraux` · `back / dos` · `lats` · `traps` · `shoulders / deltoids` · `biceps` · `triceps` · `forearms` · `core / gainage` · `glutes` · `quads` · `hamstrings` · `calves` · `cardio / systemic` · `mobility / control`

Chaque exercice pourra être associé à :

- `primary_zone`
- `secondary_zones`
- `stabilizer_zones`
- `movement_pattern`
- `split_role`
- `optional_asset_key`

### §23.4 — Rôles biomécaniques

- **primary** : zone cible principale ;
- **secondary** : muscles assistants significatifs ;
- **stabilizer** : zones qui maintiennent la posture / trajectoire ;
- **systemic** : fatigue générale / cardio / conditioning ;
- **mobility_control** : contrôle, amplitude, technique.

### §23.5 — Contrat futur de données (documentaire uniquement)

Sans implémenter de modèle maintenant, contrat cible :

```
exercise_code → body_map_descriptor

body_map_descriptor:
  primary_zone         # une zone de la taxonomie §23.3
  secondary_zones[]    # 0..n zones assistantes
  stabilizer_zones[]   # 0..n zones de stabilisation
  movement_pattern     # ex. push horizontal, hinge, squat, pull vertical...
  split_role           # rôle dans le split (stimulus principal, isolation, finisher...)
  asset_key            # optional — clé vers un futur visuel
  confidence / source  # optional — origine de l'association, niveau de confiance
```

**Important :**
- Ce contrat est **documentaire** pour l'instant.
- **Aucune migration.**
- **Aucun nouveau modèle.**
- **Aucun service modifié.**
- **Aucune donnée runtime créée** dans cette spec.

### §23.6 — Stratégie visuelle (V1 → V3)

**V1** (Sb_UI_04.3 → 04.5) :
- Worked Area Panel **textuel** dans la carte active ;
- placeholder clinique froid ;
- **pas** d'image obligatoire · **pas** de GIF · **pas** d'asset externe requis.

**V2** (futur) :
- silhouette statique SVG / image simple ;
- zones colorées avec mono-accent ou intensité neutre ;
- **fallback texte obligatoire**.

**V3** (futur, hors cycle) :
- asset par zone ou par exercice ;
- éventuellement image fournie par l'opérateur ;
- éventuellement GIF / animation, **mais seulement** avec fallback statique et respect **`prefers-reduced-motion`**.

### §23.7 — Contraintes de prudence

- **Ne jamais** présenter la body map comme **diagnostic médical**.
- **Ne pas** prétendre mesurer une **activation réelle**.
- Parler de **"zone ciblée"**, **"zone dominante"**, **"rôle biomécanique estimé"**.
- Toujours une formulation **sobre et conservatrice**.
- **Pas de claims physiologiques forts** sans source.
- **Pas de surcharge visuelle** pendant le logging.

### §23.8 — Profile Body Intelligence Direction (futur)

À terme, le profil pourra montrer (hors scope immédiat, **direction future**) :

- répartition **hebdomadaire / mensuelle** par zones ;
- **heatmap corporelle cumulative** ;
- **split balance** ;
- zones **rarement travaillées** ;
- zones **très sollicitées** ;
- lien avec **fatigue / douleurs déclarées** si cette donnée existe plus tard ;
- **recommandations prudentes, jamais médicales**.

Cette direction s'articule avec le module Body Intelligence existant (`body_intelligence.py`) **sans le modifier** dans ce cycle — surface d'affichage uniquement, le jour venu.

### §23.9 — Impact sur les prochains sprints

- **Sb_UI_04.3** introduit le **Worked Area Panel minimal** (textuel) dans la carte active — **premier jalon** du Body Representation System.
- **Sb_UI_04.4** relie ce panel au **logging** et à la **progression**.
- **Sb_UI_04.5** formalise le **visual slot** et prépare le futur **Body Map System** (contrat §23.5 prêt à être branché).
- **Sx_UI_05 / Sx_UI_07 / profil** pourront **réutiliser cette couche** plus tard (surfaces B et C §23.2).

### §23.10 — Non-goals (body representation)

- ❌ Pas de **Body Map complète** maintenant.
- ❌ Pas de **profil modifié** maintenant.
- ❌ Pas de **modèle de données** maintenant.
- ❌ Pas de **calcul biomécanique réel** maintenant.
- ❌ Pas d'**asset pipeline** maintenant.
- ❌ Pas de **génération d'image** dans l'app maintenant.
- ❌ Pas de **GIF** maintenant.
- ❌ Pas de **diagnostic médical**.

## §24. Verdict final attendu

- **READY FOR HUMAN REVIEW**
- **Aucun build ouvert** (Sb_UI_04.3 reste bloqué tant que cette spec n'est pas validée)
- **Aucune capture screenshot** dans ce sprint
- **Aucune release tag** dans ce sprint

## §25. Références croisées

- Parent spec (conservée, recadrée) : `docs/strategy/Sx_UI_04_SESSION_FOCUS_RESKIN_SPEC.md`
- Réserve visuelle source : `docs/SPRINT_Sb_UI_04_2_HUMAN_REVIEW_REPORT.md` §5.2 + §7
- Sprints Sb_UI_04.1 / Sb_UI_04.2 acceptés : `docs/SPRINT_Sb_UI_04_1_HUMAN_REVIEW_REPORT.md`, `docs/SPRINT_Sb_UI_04_2_HUMAN_REVIEW_REPORT.md`
- Baseline P0 : `docs/BASELINE_P0_CAPTURED_2026_07_04.md`
- Tokens : `docs/strategy/Sx_UI_02_DESIGN_TOKENS_SPEC.md`
- App Shell : `docs/strategy/Sx_UI_03_APP_SHELL_NAVIGATION_SPEC.md`
- Screenshot regression : `docs/strategy/Sx_UI_11_SCREENSHOT_REGRESSION_BASELINE_SPEC.md`
- Focus mode précurseur : `docs/strategy/Sx_29_CLOSURE_REPORT.md`
- Body Intelligence existant (non modifié, réutilisé plus tard par §23.8) : `app/services/body_intelligence.py` + `docs/strategy/Sx_31*` (cycle Body Intelligence v2)
- Registry : `docs/strategy/SPEC_REGISTRY.md`
- Roadmap : `docs/strategy/ROADMAP_AND_NEXT_STEPS.md`
