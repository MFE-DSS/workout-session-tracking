# SPIGNOS Session Flow & Intelligence Spec v1

**Sprint:** Sx_05_session_flow_and_intelligence_spec
**Date:** 2026-04-15
**Status:** Spec de cadrage (SPEC ONLY — aucun build)
**Successeur de:** cycle catalogue v10 clos
**Audit ancrage repo:** effectue sur fichiers reels (voir §14)

---

## A. Statut / Contexte

### A.1 Cycle catalogue v10 — clos

- v10 livre (Push A 25→21 sets, governance volume policy)
- v9 enrichi substitutions (9→43 slots avec substituts, +515%)
- Regle de repos differenciee integree dans `global_notes`
- Zero migration, 519 tests green
- Pret a deployer

### A.2 Pourquoi ouvrir un nouveau chantier

Le cycle catalogue a verrouille **ce qui est programme** (trame + substituts + volumes + repos). Le feedback terrain revele que **comment la seance est jouee** reste friction :

- Logger vertical fatigue (scroll permanent, save manuel a chaque carte)
- Substitution UI pensee comme element dans une longue liste, pas comme action locale
- Scoring LISS/cardio mal calibre
- Bugs de saisie (decimales, timezone)
- Commentaires libres peu utilises
- Aucune ressource "science machine" reliee au programme
- Aucune preparation de la couche d'analyse d'incoherences

Ce sprint ouvre le chantier **comment la seance est vecue, saisie, et interpretee**.

### A.3 Ce qui est stabilise

- Modele catalogue (templates, exercises, sets, rep_targets, substitutes)
- Modele session (snapshots immutables, session_exercises, set_logs)
- Signal feedback (Sx_01 FINAL : weight + reps + completed + muscle_sensation + free_note + success_score derive)
- Composant exercice `<details>` avec jump bar 4 etats + CTA contextuel + footer sticky (Sx_02 FINAL + Sb_02.1)
- Substitution locale par radio dans le body (Sx_03 FINAL + Sb_03)
- Terminal state `/done` + session_recap (Sb_R3)

### A.4 Ce qui change via le feedback terrain

- Passage **vertical → horizontal carte-par-carte** (navigation gestuelle/tactile)
- **Save-on-next** automatique
- **Substitution** doit rester **locale a la vignette active**, via drawer leger (pas un catalogue)
- **Scoring strength vs cardio** doit etre separe
- **Charges bilaterales** : convention canonique a trancher
- **Notes libres → etats structures** pendant la seance, synthese a la fin
- **Atlas machine** : ressource scientifique accessible depuis chaque exercice
- **Couche d'analyse d'incoherences** : preparee, pas implementee

---

## B. Resume executif

**Mutation visee :** passer d'un **logger vertical** (liste de cartes ouvertes, save manuel, flow descendant) a un **systeme de seance guidee horizontal** (vignettes sequentielles, save-on-next, une seule carte active, point d'entree local pour substitution + info machine).

Le produit demande moins a l'utilisateur et infere plus des donnees. La seance devient un flux, pas un formulaire.

---

## C. Problemes produit a resoudre

| # | Probleme | Source feedback | Impact actuel |
|---|----------|-----------------|--------------|
| 1 | Flow vertical fatigant (scroll + remontee/descente) | A | Frictions gym, sessions plus longues que necessaire |
| 2 | Save manuel explicite a chaque carte | E | Clic redondant, casse le rythme |
| 3 | Substitution non contextualisee (liste statique dans carte) | C | Pas explicite comme action "locale", pas invite a l'usage |
| 4 | Scoring LISS/cardio sous-note vs musculation | F | Seance cardio bien faite penalisee visuellement |
| 5 | Saisie decimales refusee (`12.5` ou `12,5`) | G | Bug bloquant pour halteres intermediaires |
| 6 | Timezone incorrecte (creneau arbitraire) | K | Seance enregistree au mauvais jour/heure |
| 7 | Ambiguite charges bilaterales (20+20 vs 40) | H | Historique et comparaisons instables |
| 8 | Commentaires libres peu utilises | I | Champ present mais vide dans 90%+ des cas |
| 9 | Aucune ressource machine reliee au programme | D | User ne sait pas quelle machine, comment l'executer |
| 10 | Aucune detection d'incoherences de saisie | J | Donnees aberrantes (reps+++ et charge+++ en fin d'exercice) non flaggees |

---

## D. Principes directeurs

Verrouilles pour tout Sx_05 → Sb_09 :

1. **Mobile-first reel** — chaque decision passe par le test "au gym, une main, 5 sec"
2. **SSR prioritaire** — zero JS lourd, HTML natif + `<details>` + flexbox/grid + progressive enhancement uniquement
3. **Une seule carte active a la fois** — la carte courante domine l'ecran, les autres sont compactees
4. **La navigation enregistre** — save-on-next implicite, zero bouton "Enregistrer" primaire sur carte intermediaire
5. **Le programme reste la source planifiee** — la vignette d'origine n'est jamais reecrite par la substitution
6. **La seance trace le realise** — snapshots immutables + `substituted_name` portent la verite d'execution
7. **Demander moins, inferer plus** — preferer des etats structures a du texte libre
8. **Aucune sophistication ne doit degrader la lisibilite** — pas d'animation, pas de gadget, pas de simulation d'app native
9. **Historique propre et interpretable** — aucune migration destructive, snapshots preserves
10. **Intelligence layer preparee, pas promise** — cadrer la couche d'analyse sans sur-promettre

---

## E. Modele cible de la seance

### E.1 Vocabulaire canonique

| Terme | Definition |
|-------|-----------|
| **Programme** | Trame de vignettes d'exercices (TemplateExercise ordonnees) |
| **Vignette** | Element du programme — porte l'exercice prevu, les substituts autorises, et l'acces info machine |
| **Carte active** | Vignette actuellement editable, domine l'ecran |
| **Carte done** | Vignette dont tous les work sets prevus sont marques `completed` |
| **Carte future** | Vignette pas encore entamee, non active |
| **Carte partial** | Vignette partiellement remplie, non active |
| **Substitution** | Choix ponctuel d'un exercice realise different du prevu, **local** a la vignette |
| **Save-on-next** | Enregistrement automatique declenche par la navigation vers la vignette suivante |
| **Synthese finale** | Surface terminale `/done` consolidant le realise (Sb_R3 deja en place) |

### E.2 Flow cible

```
Entree session
  ↓
Vignette 1 (ACTIVE)
  - Exercice prevu visible
  - Substitution locale accessible (drawer)
  - Info machine accessible (i icon)
  - Sets a saisir inline
  ↓
[User saisit, coche, puis tape "Suivant" ou swipe]
  ↓
Save-on-next declenche automatiquement
  ↓
Vignette 1 se compacte (done ou partial)
Vignette 2 devient ACTIVE
  ↓
... repete jusqu'a derniere vignette ...
  ↓
Synthese finale /done (Sb_R3 existant)
```

### E.3 Navigation

| Action | Effet | Implementation SSR |
|--------|-------|-------------------|
| Tap "Suivant" | Save + ouvre carte suivante | POST vers endpoint qui redirige `?active={next_id}` |
| Tap "Precedent" | Ouvre carte precedente (sans save prealable necessaire si rien modifie) | GET ou POST selon modifications locales |
| Tap vignette dans jump bar | Navigation libre | GET avec `?active={id}` |
| Swipe horizontal (V2+) | Navigation gestuelle optionnelle | Progressive enhancement CSS seul |

### E.4 Etats visuels

| Etat | Visuel | Rendu |
|------|--------|-------|
| `future` | Compact, dim neutre | `<details>` ferme, accent `--fg-dim` |
| `partial` | Compact, warn | `<details>` ferme, bordure `--warn`, recap des sets faits |
| `done` | Compact, ok | `<details>` ferme, bordure `--ok`, recap complet |
| `active` | Expanded, accent | `<details open>`, bordure `--accent`, box-shadow |

---

## F. Prevu vs Realise

### F.1 Principe canonique (reaffirmation Sx_03)

- **Prevu** : `TemplateExercise.name` (catalogue) + `SessionExercise.exercise_name_snapshot` (fige au create)
- **Realise** : `SessionExercise.substituted_name` (nullable — NULL si execute tel quel, sinon nom de l'exercice reellement fait)
- **Resolution** : `actual_exercise_name(se) = substituted_name or exercise_name_snapshot`

### F.2 Pourquoi la vignette d'origine ne doit pas etre reecrite

- L'utilisateur veut **savoir ce que le programme demandait** meme apres substitution
- L'historique slot-based (`(template_slug_snapshot, exercise_code_snapshot)`) compare les occurrences du MEME slot, quelle que soit la substitution
- Les analytics slot-based (delta, progression_hint, last_time) continuent de fonctionner
- Les analytics realise-based (muscle_scoring, physique dashboard) utilisent `actual_exercise_name`

### F.3 Enregistrement de la substitution

Deja en place (Sb_03). La substitution :
- S'ecrit dans `session_exercises.substituted_name`
- Est **locked** apres le premier work set completed (via `can_substitute()`)
- Conserve le `exercise_name_snapshot` intact
- Apparait dans le summary de la carte et dans le recap `/done` avec prefixe `→`

### F.4 Impacts

| Surface | Lecture | Comportement |
|---------|---------|--------------|
| Vignette du programme (pre-session) | Prevu | Jamais modifiee |
| Carte active | Prevu + realise | Affiche prevu + picker substitution + badge si choisi |
| Summary carte done | Realise | `substituted_name or exercise_name_snapshot` |
| Historique exercice-par-exercice | Slot + realise | Liste les occurrences du slot avec prefixe `→` si substitue |
| Muscle scoring / physique | Realise | Classifie via `actual_exercise_name` |
| Export CSV/JSON | Les deux | Preserve `exercise_name_snapshot` + `substituted_name` |
| Future lecture pattern-aware | Realise + taxonomie | Agrege par motor_pattern via canonical (defer) |

---

## G. Charges : semantique canonique

### G.1 Probleme

Cas ambigus :
- Halteres : `20 kg + 20 kg` = "20" (par cote) ou "40" (total) ?
- Machines unilaterales : `20 kg` = par cote ou total ?
- Presses bilaterales : `60 kg` = charge totale sur la machine
- Shoulder press machine : `30` = souvent par cote sur machines a bras independants

### G.2 Convention canonique proposee

**Regle unique : saisir la charge par cote** pour les exercices **unilateraux par nature** (halteres, cable unilateral, machines a bras independants). **Saisir la charge totale** pour les exercices bilateraux fixes (Smith, hack squat, leg press, butterfly machine).

**Formulation claire :**

> Pour chaque exercice, saisir la charge **telle qu'elle apparait sur l'equipement**.
> - Halteres : poids d'un seul haltere (ex: 20 kg)
> - Machines a bras independants : poids d'un cote (ex: 30 kg)
> - Machines bilaterales fixes : poids total (ex: 60 kg)
> - Cable unilateral : poids de la pile (ex: 15 kg)

### G.3 Compromis arbitres

- **Pas de champ "par cote"/"total"** — trop de friction UI, trop de decisions par carte
- **Le catalogue porte la reference** : via taxonomie equipment (cf. P04/P05) on peut annoter chaque exercice avec `load_semantics: per_side | total`
- **Affichage historique** normalise : la comparaison delta se fait sur **la valeur saisie**, pas sur une grandeur reconstruite

### G.4 Rappel discret de la convention (C05)

- **Pas de modale** ni d'alerte
- Un petit texte d'aide sous le champ `kg` : "Saisir comme sur la machine/haltere"
- Optionnel : lien vers la ressource atlas machine pour l'exercice courant
- Une fois lu, le user n'a pas besoin de le revoir — mais il reste accessible sans casser le flow

### G.5 Impacts

- Zero migration historique (les donnees passees sont ce qu'elles sont, meme convention probable)
- Documenter dans `docs/PRODUCT_SPEC.md` + page `/science`
- Ajout optionnel dans le catalogue : `"load_semantics": "per_side"` par exercice concerne (traite dans Sx_06 ou Sx_07)

### G.6 Bug B01 a corriger conjointement

Les inputs `type="number"` HTML5 rejettent la virgule au niveau du navigateur avant submit. Backend (`to_float`) accepte deja la virgule. **Fix : passer a `type="text" inputmode="decimal" pattern="[0-9]*[.,]?[0-9]*"`** dans les champs weight_kg. Zero regression attendue — la validation backend reste robuste.

---

## H. Score / Logique d'evaluation

### H.1 Probleme actuel

`quality_score` unique pour tous les types de seance :
- 40 pts work set completion (depend de total_work_sets)
- 40 pts success_score (derive reps vs rep_targets)
- 10 pts concentration
- 10 pts global_state

Pour une seance LISS cardio :
- `rep_targets` non pertinents → success_score souvent None ou bas
- Work set completion OK mais sur 3-4 sets (abs) → petite base
- Concentration + global_state OK
- **Score max effectif : ~20-60 / 100 meme pour une seance bien faite**

### H.2 Separation minimale viable

Introduire un **dispatcher de scoring** base sur `template.kind` :

```
session.template.kind == "strength"  → compute_session_quality_strength(session)
session.template.kind == "cardio"    → compute_session_quality_cardio(session)
```

### H.3 Scoring cardio/LISS propose

Signaux d'entree (deja captures) :
- `cardio_duration_min` (champ existant)
- `cardio_bpm_avg` (champ existant)
- `cardio_machine_calories` (indicatif)
- `cardio_machine_type`
- `concentration`, `global_state`
- Eventuel exercice abs attache (`liss-abs` template)

Formule proposee V1 :

```
cardio_score = (
    duration_component      # 0..50 (60 pts si >= 20min LISS, degrade en dessous)
  + intensity_component     # 0..20 (bpm dans zone cible = 20, sinon degrade)
  + completion_component    # 0..20 (abs complets si template liss-abs, sinon 20 par defaut)
  + subjective_component    # 0..10 (concentration + global_state combines)
)
```

Plafonne a 100. Cardio bien fait (>= 20 min dans zone cible) → score >= 80.

### H.4 Cadrage Sx_06

Sx_06 traite le detail. Ici on pose :
- **separation des regimes**
- **plafond effectif** (eviter qu'une seance cardio saine reste plombee)
- **coherence des surfaces visuelles** (timeline quality, sparkline) qui doivent dispatcher selon le kind

### H.5 Impacts

| Surface | Impact | Action |
|---------|--------|--------|
| `quality_score.compute_session_quality` | Refactor vers dispatcher | Sb_06 |
| `kpis.avg_success_score_30d` | Doit rester coherent (skip cardio dans agregats musculation) | Sb_06 |
| Timeline quality, sparkline home | Doit visualiser les deux regimes sans melange naif | Sb_06 + Sb_09 |
| `behavioral.compute_session_fatigue` | Inchange (consomme concentration+global_state) | Neutre |
| Leaderboard | Via quality_score → dispatch transparent | Neutre |
| Export JSON/CSV | Ajouter champ `session_kind` ou equivalent | Sb_06 |

---

## I. Notes / Etats structures / Synthese finale

### I.1 Diagnostic

`free_note` (exercice 140 chars, session 280 chars) est present mais **tres peu utilise** en pratique gym (pas le moment de taper un texte). Il reste utile en post-session pour consigner un ressenti particulier.

### I.2 Arbitrage

| Champ | Pendant la seance | Post-seance |
|-------|-------------------|-------------|
| `free_note` exercice | **Reduit** : collapsed dans `<details>` optionnel, non prioritaire | Accessible en edition via `/done` + Rouvrir |
| `free_note` session | **Pas montre pendant la saisie exercice** | Affiche dans bloc feedback session en fin |
| `muscle_sensation` | Bouton rapide (deja un `<details>` optionnel) | — |
| `concentration`, `global_state` | Bloc feedback session a la fin, segmented controls | — |
| `bodyweight_kg` | Bloc feedback session | — |
| **Nouveaux etats structures possibles** | Voir §I.3 | — |

### I.3 Etats structures nouveaux potentiels (Sx_07 ou Sx_08)

Propositions a arbitrer **plus tard** — pas dans Sx_05 :

- `session_fatigue_level` (1-5) — post-seance, remplace le global_state si jugee insuffisante
- `session_quality_self` (1-5) — auto-evaluation subjective globale
- `session_tags` — enum mots-cles post-seance ("PR", "deload", "maladie", "blessure mineure")

Ces champs sont **optionnels** et ne remplacent pas la synthese generee par les donnees.

### I.4 Preparation rapport final

Cadrage Sx_08 :
- Synthese auto-generee dans `/done` a partir des donnees
- Basee sur : duration, completion rate, deltas vs derniere fois, zones touchees, substitutions, etc.
- Ne doit jamais etre une "lettre generee par IA" — doit etre une **structure de donnees** rendue en SSR avec wording neutre

---

## J. Ressource machine / Familles de machines

### J.1 Structure minimale viable de l'atlas

Taxonomie en 3 niveaux :

```
Famille (haut niveau)
  ├── Sous-famille
  │   └── Machine specifique (ou classe generique)
```

Exemples :

```
Pectoraux
  ├── Developpe
  │   ├── Chest Press machine (convergente / independante / bras fixes)
  │   ├── Smith Press (vertical, incline, couche)
  │   └── Developpe haltere (banc plat, incline 30°, incline 45°)
  ├── Fly / Ecarte
  │   ├── Butterfly machine (pec deck)
  │   ├── Cable cross (bas-haut, haut-bas, convergent)
  │   └── Ecarte haltere (plat, incline)
  └── Dips
      ├── Dips machine assistee
      └── Dips poids corps

Dos
  ├── Verticaux
  │   ├── Lat pulldown (prise large, neutre, serree)
  │   ├── Traction (pull-up, assistee, lesté)
  │   └── Pullover cable/machine
  ├── Horizontaux
  │   ├── Rowing chest-supported (machine convergente)
  │   ├── Rowing assis cable (prise neutre, large, serree)
  │   ├── Rowing haltere un bras
  │   └── T-bar row
  └── Shrugs / Traps (barre, haltere, cable)
```

### J.2 Stockage propose

**Option A — Fichier JSON dedie** `data/machine_atlas.json` :

```json
{
  "version": "2026-04-15.v1",
  "families": [
    {
      "slug": "pecs-press",
      "name": "Pectoraux — Developpe",
      "parent": "pecs",
      "machines": [
        {
          "slug": "chest-press-machine",
          "name": "Chest Press machine",
          "description": "...",
          "execution_cues": ["...", "..."],
          "common_mistakes": ["...", "..."]
        }
      ]
    }
  ]
}
```

**Option B — Section etendue de `reference_split.json`** :
- Ajouter `machines` et `families` en top-level

**Recommandation :** Option A (fichier dedie, gouvernance separee, pas de pollution du catalogue exercice).

### J.3 Lien exercice → famille / machine

Ajouter a chaque exercice du catalogue un champ optionnel :

```json
{
  "code": "E1",
  "name": "Chest Press machine",
  "set_scheme": "3x 8-12",
  "machine_family": "pecs-press",
  "machine_slug": "chest-press-machine"
}
```

`machine_slug` pointe vers l'atlas si besoin de precision, sinon `machine_family` suffit.

### J.4 UX d'acces (UX05 + C04)

- Icone `i` discrete dans le header de la carte exercice, a cote du nom
- Tap → ouvre un **petit panneau contextuel** (Bottom-Sheet SSR via `<details>` ou nouveau fragment)
- Panneau contient : famille + machine + cues d'execution + lien vers atlas complet
- **Pas de modale bloquante** — fermable d'un tap

### J.5 Garde-fous

- Atlas reste **court et visuel** (pas de paragraphes encyclopediques)
- Mise a jour versione (comme catalogue)
- Aucune dependance dure : si `machine_slug` est null, la carte fonctionne normalement sans `i`
- Pas d'images lourdes (SVG sobres ou pictogrammes text-only V1)

### J.6 Page `/science` / `/atlas`

Route dediee qui affiche l'atlas complet navigable. Deja pre-positionnee via la page `/science` existante. Sx_07 detaille la maquette.

---

## K. Future Intelligence Layer

### K.1 Scope preparatoire

Aucune implementation dans Sx_05. Preparation explicite pour eviter sur-promesse.

### K.2 Couche I01 — Detection incoherences de series

Exemples de regles simples deterministes :

| Regle | Detection |
|-------|-----------|
| Charge + reps croissent simultanement en fin d'exercice | Probable erreur saisie ou surestimation |
| Execution "clean" maintenue sur tous les sets alors que succes_score derive = 50 | Incoherence subjective vs objective |
| Delta weight > 30% vs derniere fois sans contexte | A flagger |
| Dernier set complete 0 reps ou NULL mais marque "done" | Incoherence structurelle |

### K.3 Couche I02 — Rapport final auto-genere

Structure a rendre en SSR dans `/done` :

- Duration effective (deja dans session_recap)
- Completion rate (deja)
- **Top progression** vs derniere fois (delta le plus grand) — nouveau
- **Zones touchees** avec volume par zone — nouveau
- **Substitutions** effectuees — deja
- **Alertes** eventuelles (I01) — nouveau
- **Status final** : "seance complete", "seance partielle", "seance interrompue"

### K.4 Couche I03 — Hints automatiques

Affichage contextuel dans la carte exercice active :
- "Charge augmente de 10% vs derniere fois — prudence sur la technique"
- "Tu as reduit les reps sur ce set, la fatigue est probable"
- **Pas d'alerte bloquante** — suggestions a coter de la carte

### K.5 Couche I04 — Score de confiance

Meta-score 0-100 qui jauge la **qualite du logging** (pas de la seance) :
- 100 = tous les sets renseignes + concentration + global_state + bodyweight + pas d'incoherence flaggee
- 0 = session abandonnee apres 2 sets sans feedback

A utiliser pour ponderer les analytics (degrade les cas "donnees douteuses").

### K.6 Couche I05 — Lecture pattern-aware

Voir §3 Sx_03 FINAL. Necessite taxonomie de mouvement (defer jusqu'a Option 2 canonical entity).

### K.7 Preparation sans coder

Ce que Sx_05 pose :
- **Vocabulaire** : "hint", "alert", "incoherence", "session review intelligence"
- **Surface cible** : `/done` enrichi + petit hint zone dans la carte active
- **Ne jamais ajouter** une couche predictive bloquante
- **Signal de confiance** documente comme prochaine etape quand les donnees Sb_R3 (/done) sont stabilisees

---

## L. Bugs et Core a fixer avant / pendant la refacto

### L.1 Bugs prioritaires

| ID | Titre | Surface repo | Gravite | Lot recommande |
|----|-------|--------------|---------|----------------|
| **B01** | Saisie decimales/virgules | `app/templates/session_detail.html` (inputs type=number lignes 177-232 + cardio lignes 307-317) + `app/services/form_parsing.to_float` (deja tolere virgule) | Haute | **Sb_06** (input canonicalization) |
| **B02** | Timezone session incorrecte | `app/routers/sessions.py:95` (`datetime.now(timezone.utc)` au create), `session.started_at` / `ended_at` stockes UTC mais rendu a verifier dans templates + `session_recap._duration_label` | Haute | **Sb_06** |
| **B03** | Score LISS/cardio incoherent | `app/services/quality_score.py` (formule unique), template `liss-abs` / `liss-only` | Haute | **Sb_06** |
| **B04** | Visualisation cardio penalisante | `app/services/timeline.py`, `app/templates/index.html` sparkline, `app/templates/progress.html` | Moyenne | **Sb_09** |
| **B05** | Friction residuelle saisie | A capturer via recette terrain | Basse | **Lot 3** |

### L.2 Core items

| ID | Titre | Surface | Lot |
|----|-------|---------|-----|
| **C01** | Save-on-next | `app/routers/sessions.py:363-430` (update_exercise_card), `app/templates/session_detail.html` footer CTA | **Sb_05** |
| **C02** | Convention charge bilaterale | `docs/PRODUCT_SPEC.md`, page `/science`, optionnel catalogue `load_semantics` | **Sb_06** |
| **C03** | Reduire notes inline | `app/templates/session_detail.html` (textareas exercice + session), `app/routers/sessions.py` parsing | **Sb_08** |
| **C04** | Entree info machine | Nouveau panneau, lien template, atlas JSON | **Sb_07** |
| **C05** | Rappel discret convention charge | Helper text sous input weight | **Sb_06** |
| **C06** | Synthese finale simplifiee | Evolution `session_recap` + `session_done.html` | **Sb_08** |

### L.3 Tableau croise ordre de fix

Bugs avant refactor UX majeure :
- B02 (timezone) avant Sb_05 : evite de refaire UI sur data non alignee temporellement
- B01 (decimales) avant Sb_05 : UX cle, bloquant terrain
- B03 (score cardio) peut etre en parallele de Sb_06

---

## M. Impacts techniques et fonctionnels

### M.1 Consommateurs impactes

| Surface | Fichier repo | Impact Sx_05+ |
|---------|--------------|---------------|
| UI session editable | `app/templates/session_detail.html` | Refactor majeur → Sb_05 |
| Route session_detail GET | `app/routers/sessions.py:155-274` | Adaptation active_exercise_id + save-on-next → Sb_05 |
| Route update_exercise_card POST | `app/routers/sessions.py:363-430` | Mecanisme save-on-next transparent → Sb_05 |
| Route update_session POST | `app/routers/sessions.py:329-360` | Inchange |
| Score session | `app/services/quality_score.py` | Dispatcher strength/cardio → Sb_06 |
| Parse inputs | `app/services/form_parsing.py` | Tolere deja virgule, OK |
| Time / dates | `app/routers/sessions.py` (UTC now), rendu templates | B02 fix → Sb_06 |
| Historique par slot | `app/services/exercise_history.py` | Neutre |
| Delta / progression hint | `app/services/delta.py`, `progression_hint.py` | Neutre |
| Zones / physique | `app/services/muscle_scoring.py` | Neutre (consume actual_exercise_name) |
| Export JSON/CSV | `app/services/export_builder.py` | Ajout `session_kind` → Sb_06 ; champ `load_semantics` optionnel |
| Session recap / done | `app/services/session_recap.py`, `app/templates/session_done.html` | Enrichissement progressif → Sb_08 |
| Timeline / sparkline | `app/services/timeline.py`, `app/templates/index.html`, `app/templates/progress.html` | Dispatcher strength/cardio → Sb_09 |
| Leaderboard + squad | `app/services/leaderboard.py`, `app/services/squad.py` | Transparent (lit quality_score) |
| Behavioral engine | `app/services/behavioral.py` | Neutre |

### M.2 Nouvelles surfaces

- `data/machine_atlas.json` (nouveau, Sx_07/Sb_07)
- Panneau contextuel machine (fragment HTML dedie ou `<details>` dans carte, Sb_07)
- Eventuel `app/services/scoring.py` refactor ou split (Sb_06)

---

## N. Risques

| Risque | Probabilite | Mitigation |
|--------|------------|------------|
| Refaire UX avant de figer la semantique | Moyen | **Ce spec** ; plus Sx_06 pour charges/time/score avant Sb_05 final |
| Complexifier trop tot l'intelligence layer | Moyen | K explicite : preparation, pas implementation ; Sb_08 minimal |
| Convention charge mal comprise | Moyen | C05 rappel discret + page science ; pas de migration |
| Casser historique / analytics existantes | Faible | Snapshots immutables + slot-based reste stable |
| Atlas machine trop lourd | Moyen | Regle : compact, visuel, optionnel ; pas de prose longue |
| Save-on-next trop intrusif | Faible | Bouton "Suivant" explicite + navigation reste tolerante ; pas de swipe force V1 |
| Scoring cardio V1 encore imparfait | Moyen | Iterer via feedback terrain ; valider avec plusieurs templates cardio |
| Mauvaise detection timezone user | Moyen | Defaut Europe/Paris (Sb_06), evolution vers user preference plus tard |

---

## O. Acceptance criteria de la spec Sx_05

| Critere | Statut |
|---------|--------|
| Modele flow carte-par-carte clair (vocabulaire, etats, navigation) | ✓ §E |
| Save-on-next documente (principe + redirect + edge cases) | ✓ §E + §L.1 C01 |
| Prevu vs realise clarifie (reaffirmation + regles) | ✓ §F |
| Scoring musculation vs cardio distingue (separation + formule V1) | ✓ §H |
| Convention charge bilaterale traitee serieusement (regle + compromis + rappel UI) | ✓ §G |
| Notes vs etats structures arbitres (reduction inline + synthese finale) | ✓ §I |
| Atlas machine cadre (structure, liens, UX, stockage) | ✓ §J |
| Future intelligence layer preparee sans sur-ingenierie (4 couches, surfaces, vocabulaire) | ✓ §K |
| Bugs prioritaires mappes sur surfaces repo | ✓ §L |
| Impacts techniques identifies par fichier | ✓ §M |
| Risques enumeres et mitiges | ✓ §N |
| Suite des sprints ordonnee et justifiee | ✓ voir `SPIGNOS_SESSION_SYSTEM_SPRINT_QUEUE_v1.md` |

---

## P. Terminologie normative

A utiliser dans tous les sprints suivants :

| Terme | Usage |
|-------|-------|
| **prevu** | Ce que le programme prescrit (TemplateExercise.name, rep_targets) |
| **realise** | Ce que l'utilisateur a fait (SetLog + substituted_name) |
| **vignette** | Element du programme dans la trame sequentielle |
| **carte active** | Vignette editable courante |
| **done** / **future** / **partial** | Etats des vignettes non-actives |
| **substitution** | Choix d'un exercice realise different du prevu, local a la vignette |
| **save-on-next** | Save automatique declenche par la navigation vers la vignette suivante |
| **charge canonique** | Regle de saisie = comme sur l'equipement (par cote halteres/machines independantes, total bilaterales fixes) |
| **scoring strength** | Formule `compute_session_quality_strength` pour templates `kind=strength` |
| **scoring cardio** | Formule `compute_session_quality_cardio` pour templates `kind=cardio` |
| **machine family knowledge** | Taxonomie atlas machine (famille → sous-famille → machine) |
| **session review intelligence** | Couche d'analyse post-seance (incoherences, hints, confidence score, pattern-aware) |

---

## Q. Audit repo effectue

Fichiers et surfaces inspectes pour ancrer le spec :

| Fichier | Lignes cles | Role |
|---------|-------------|------|
| `app/routers/sessions.py` | 155-274 (GET), 311-360 (POST session), 363-430 (POST exercise card) | Flow actuel + redirect logic |
| `app/templates/session_detail.html` | 29-45 (jump bar), 52-275 (cards + form), 278-378 (session feedback) | Structure UI + inputs type=number |
| `app/models/session.py` | 46-119 (WorkoutSession), 117-163 (SessionExercise), 166-210 (SetLog) | Modele + snapshots |
| `app/services/quality_score.py` | 44-87 | Formule unique strength+cardio melange |
| `app/services/feedback.py` | 28-84 | compute_success_score derive |
| `app/services/form_parsing.py` | 28-34 | to_float tolere virgule (backend OK, browser bloque) |
| `app/services/session_recap.py` | 17-46 | _duration_label, cardio block |
| `app/services/timeline.py` | — | Visualisations globales |
| `app/services/substitution.py` | 12-36 | actual_exercise_name, get_substitutes, can_substitute |
| `data/reference_split.json` | v10 | Catalogue + templates kind=strength/cardio |

**Constats :**

1. **B01** effectivement cause cote navigateur : `type="number"` rejette virgule. `to_float` backend tolere deja.
2. **B02** : `started_at` stocke en UTC (correct), mais rendu template sans conversion locale → heure affichee decalee pour user Europe.
3. **B03** : `quality_score` consume success_score (None pour cardio sans rep_targets) → plafond ~60/100 pour LISS.
4. **save-on-next** : logique actuelle = bouton submit explicite par carte. Pour V1 du refactor, on peut garder un bouton "Suivant" explicite (pas de swipe auto) mais rendre son libelle evident et eviter tout autre bouton "Enregistrer" sur la carte.
5. **Architecture SSR** : tout le flow session passe par `<details>` + `<form>` → compatible avec une evolution horizontale via CSS seul (scroll-snap horizontal).
6. **Substitution** : `<details class="substitute-picker">` deja dans le body. Transformation en drawer = CSS uniquement, structure inchangee.
7. **Notes libres** : present dans 2 endroits (exercice + session). Reduire inline = cacher plus profondement dans `<details>` ou retirer du body exercice. Session feedback garde.
