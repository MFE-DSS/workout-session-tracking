# SPRINT Sb_ATLAS_TECHNICAL_GUARDS_01 — restituer, pas collecter (RAPPORT)

**Base canonique :** `b8e885f` · **Branche :** `sb/atlas-technical-guards-01`

---

## 1. Capacités vérifiées avant de coder

Les sept vérifications exigées par le brief. Toutes présentes — aucun HARD STOP.

| # | Capacité | Constat |
|---|---|---|
| 1 | Chargement de l'atlas | `app/services/machine_atlas.py`, index en mémoire, **aucun nouveau moteur nécessaire** |
| 2 | `execution_cues` | liste de chaînes courtes — **29/29 machines en ont exactement 3** |
| 3 | `common_mistakes` | liste de chaînes — **29/29 machines en ont exactement 2** |
| 4 | Mapping exercice → atlas | `get_for_session_exercise()`, **conscient de la substitution** (suit le réalisé, pas le prescrit) |
| 5 | Rendu de la carte active | `atlas_data[se.id]` **déjà** passé au gabarit par le routeur |
| 6 | Contraintes 360×640 | série courante 488 → 556 ; barre d'action collante ; champs à 497 |
| 7 | Tests existants | `test_machine_atlas_surface` épingle `class="machine-panel"` **exact** et l'absence de panneau pour les exercices non mappés |

**Aucun enrichissement de l'atlas n'a été nécessaire.** Le brief l'autorisait
« si nécessaire » ; il ne l'était pas. Ajouter `setup_checklist` ou
`correction_hints` aurait produit de la donnée que rien n'affiche — exactement
le défaut que `Sb_FEEDBACK_SIGNAL_AUDIT_01` venait de documenter (trois
colonnes jamais écrites). **Zéro octet ajouté à `machine_atlas.json`.**

---

## 2. Ce qui change

Le résumé de la disclosure machine ne portait qu'une **étiquette** :
« Comment bien exécuter <machine> ». Il annonçait du contenu sans en montrer.

Il porte désormais **le premier cue d'exécution de l'atlas**, donc une
consigne réellement actionnable **lisible sans ouvrir la disclosure et sans
JS** :

```
Comment bien exécuter Incline Smith Press
Banc à 30° pour cibler le haut des pecs
```

Les deux autres cues et les deux erreurs fréquentes restent dans le corps de
la disclosure, inchangés.

---

## 3. L'écart au brief, énoncé franchement

**Le brief demandait le cue principal « visible immédiatement » dans la carte
active. Il n'est pas dans le premier écran : il est sous la console.**

Ce n'est pas un renoncement, c'est une mesure. Placé au-dessus de la console,
le cue a été essayé et mesuré deux fois à 360×640 :

| placement essayé | hauteur | série courante | champs `elementFromPoint` |
|---|---|---|---|
| deux lignes (label + texte) | 39 px | 488 → **531** | occultés |
| **une ligne** (tronquée) | 20 px | 488 → **511** | **occultés** (`owned=false`) |
| **dans le résumé, sous la console** | 0 px au-dessus | 488 → 556 | **`owned=true`** |

Même réduit à une seule ligne de 20 px, le cue poussait les champs de la série
courante de 497 à 520 px, et `elementFromPoint()` cessait de les retourner :
ils passaient **derrière la barre d'action collante**. La saisie devenait
impossible.

Les priorités du brief tranchent explicitement — **P2 préserver l'action de
série**, **P3 préserver la géométrie mobile**, avant **P4 utiliser l'atlas
comme source**. L'atlas est la **source**, pas la **position**. Le cue est
donc placé là où il ne coûte rien.

Il reste **lisible sans ouvrir et sans JS**, ce qui était l'objectif de fond :
que l'utilisateur ne loggue pas proprement un mouvement mal exécuté.

---

## 4. Une mesure qui a corrigé une conclusion précédente

En comparant contre canonical, j'ai constaté que **l'écart de boîte entre la
série courante et la barre d'action est déjà de −22 px sans mon changement**,
alors que `Sb_SESSION_SET_ACTION_01` avait rapporté « +15 px ».

Vérification faite : ce n'est **pas** une régression. La boîte de la barre
collante inclut une zone de padding vide ; les contrôles réels sont peints
plus bas. Les champs à 497 → 547 sont **intégralement possédés** par
eux-mêmes (`elementFromPoint` renvoie l'input).

**Conclusion de méthode : l'écart de boîte est une métrique trompeuse ; seule
l'occultation réelle des contrôles compte.** La conclusion opérationnelle de
la tranche précédente (contrôles cliquables) reste juste ; c'est le chiffre
d'écart que j'avais rapporté qui mesurait la mauvaise chose. Les gardes de
cette tranche mesurent désormais l'occultation, pas la boîte.

---

## 5. Preuves (360×640, `scrollY = 0`)

| | canonical `b8e885f` | avec le cue |
|---|---|---|
| champs série courante | 497, **owned** | 497, **owned** |
| série courante | 488 → 556 | **488 → 556** |
| `scrollWidth` | 360 | **360** |
| action de série | 5/5 CTA | **5/5 CTA** |
| CTA d'exercice | 5/5 CTA | **5/5 CTA** |
| inputs / selects / textareas / checkboxes | 137 / 0 / 8 / 0 | **137 / 0 / 8 / 0** |

**Géométrie strictement identique à canonical**, et **zéro contrôle de
collecte ajouté** — c'est la mesure directe de A3.

---

## 6. Couverture réelle, dite sans arrondi

Sur une séance type de 7 exercices, **4 sont mappés** à une machine de
l'atlas :

```
E1 Incline Smith Press            → incline-smith-press
E2 Chest Press machine            → chest-press-machine
E3 Dips pectoraux (buste penché)  → AUCUNE
E4 Neutral Grip Shoulder Press    → shoulder-press-machine
E5 Élévations latérales câble     → cable-lateral-raise
E6 Écarté arrière d'épaule câble  → AUCUNE
E7 Triceps extension poulie haute → AUCUNE
```

**Le cue est donc absent sur 3 des 7 exercices.** Aucun texte générique ne
vient combler le trou : une consigne qui ne correspond pas à la machine serait
pire que le silence. L'invariant est déjà tenu par
`test_machine_panel_absent_for_unlinked_exercises`.

Étendre la couverture demanderait de nouvelles entrées d'atlas — un travail de
contenu, pas de code, et hors du périmètre de cette tranche.

---

## 7. Gardes et plantations

**10 tests dédiés** : la source est l'atlas et non le gabarit · toutes les
machines peuvent fournir un cue · atlas versionné · aucun champ
`execution_quality` / `reps_target` · aucun contrôle autour du cue · aucun
wording pseudo-médical dans l'atlas **ni** dans le gabarit · cue dans le
`<summary>` donc lisible sans JS · `<details class="machine-panel">` exact
préservé · cue rendu **après** la console.

| plantation | garde qui tombe |
|---|---|
| cue codé en dur (« Garde le dos droit ») au lieu de `execution_cues[0]` | source atlas |

**Ma garde anti-médicale mesurait faux au premier jet** : elle lisait le
fichier entier et tombait sur un commentaire du gabarit disant précisément
« jamais diagnostic ». Une consigne *interdisant* les revendications médicales
était comptée comme revendication médicale — la classe de faux positif déjà
documentée ici (les commentaires Jinja lus comme du balisage). Les
commentaires sont désormais retirés avant examen.

---

## 8. Parité

| | |
|---|---|
| `app/models` · `migrations` · `app/services` · `app/routers` | **diff vide** |
| `data/machine_atlas.json` | **inchangé** |
| Fichiers touchés | 1 gabarit, 1 CSS, 1 test, 1 doc |
| Sweep complet | **4676 tests, 0 échec**, lancé **depuis le worktree** |

---

## 9. Ce que cette tranche NE livre PAS

- **Pas de `setup_checklist`, pas de `correction_hints`.** Non nécessaires, et
  les ajouter aurait créé de la donnée que rien n'affiche.
- **Pas de couverture pour les 3 exercices non mappés** — travail de contenu.
- **Pas de cue dans le premier écran** — mesuré impossible sans occulter la
  saisie (§3).
- **Aucune collecte**, conformément à la décision de l'audit précédent.

## Verdict

Le résumé de la disclosure annonçait du contenu sans en montrer ; il porte
maintenant une consigne réelle, lisible sans ouvrir et sans JS, tirée de
l'atlas versionné.

Le travail utile a été de mesurer que le placement demandé était incompatible
avec la saisie — et de le dire, plutôt que de livrer un cue joliment placé
au-dessus de champs devenus inutilisables.

---

## Closeout (post-merge)

| | |
|---|---|
| PR | **#117** — `--merge --match-head-commit f129df6`, **sans** squash / `--admin` / force |
| Merge | **`9177724`** |
| CI canonique | run `32013286672` — **succès 6/6** |
| Gate Sonar | **`OK`** — 0 bug, 0 smell, 0 vulnérabilité, 0 % duplication |
| Threads / Gitar | **0 / 0** |
| Parité métier | diff **vide** sur `app/models`, `migrations`, `app/services`, `app/routers` |
| Atlas | **inchangé** — zéro octet ajouté |

### Un aller-retour Sonar, et c'était ma leçon non appliquée

Gate rouge à **15** pour un seuil de 14 — un MAJOR. Localisé par la route
documentée avant toute modification : **`python:S9073`**, assertion composée,
sur **deux lignes que j'avais écrites** dans ce sprint.

Le sprint précédent s'était conclu en notant que le **pré-scan AST avant
commit** évitait exactement cet aller-retour. Je ne l'ai pas fait ici. C'est
la seule cause du cycle CI supplémentaire, et elle était entièrement évitable.

### Capacité CI — `HEALTHY`

| Shard | Fichiers | min MemAvailable | min SwapFree |
|---|---|---|---|
| 1 | 85 | 6 797 Mo | 3 071 — intact |
| 2 | 84 | 7 033 Mo | 3 071 — intact |
| 3 | 84 | 8 131 Mo | 3 071 — intact |

`workers=2`, manifeste respecté, jamais `-n auto`. Le shard le plus bas est à
**6 797 Mo**, très au-dessus du plancher de 4 Go. Quatre tranches successives
confirment que l'équilibre suit la **partition**, pas la machine.

### Ce que la tranche laisse ouvert

- **3 exercices sur 7 n'ont pas de cue** faute d'entrée d'atlas. Travail de
  **contenu**, pas de code — candidat `Sb_ATLAS_COVERAGE_01`.
- **Le cue n'est pas dans le premier écran** : mesuré impossible sans occulter
  la saisie. Le rouvrir supposerait de libérer de la place ailleurs, donc une
  décision produit sur ce que Home ou l'en-tête de séance peuvent perdre.
