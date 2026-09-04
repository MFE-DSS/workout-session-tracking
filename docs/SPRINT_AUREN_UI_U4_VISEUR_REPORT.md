# `AUREN_UI_U4_VISEUR` — l'instrument de séance

> **Tranche 4 de la voie critique UI.** Empilée sur `U3` (PR #185).
> La métaphore validée par l'opérateur sur maquette (`P-03`), posée sur le
> **produit réel**, en trois états.
>
> **Aucun gabarit touché. Aucun JavaScript ajouté.**

---

## 1. Brainstorming / Options / Risques / Choix retenu (`CLAUDE.md §3`)

| Option | Description | Verdict |
|---|---|---|
| **A** — réécrire `exercise_card.html` | le viseur en DOM neuf, fidèle à la maquette | ⛔ **risque de perte de données** — voir §2 — et 330 lignes de contrats documentés à rejouer |
| **B** — nouveau partial pour l'exercice actif | rayon d'impact borné | mieux, mais duplique les macros de sérialisation : deux endroits où oublier un champ |
| **C** — poser le viseur sur la structure existante, en CSS | zéro DOM déplacé, zéro champ perdu | **retenu** |

**Retenu : `C`.** Les trois éléments que l'opérateur a retenus — readout
souverain, jauge à verdict, commande en trait — **ne demandaient pas de
nouveau DOM**. Le constater a évité une refonte à risque.

---

## 2. ⚠ Pourquoi aucun gabarit n'est touché

`_persist_set_values` (`app/routers/sessions.py`) boucle sur **toutes** les
`set_logs` de l'exercice et écrit sans condition :

    sl.weight_kg = to_float(form.get(f"set_{sl.id}_weight_kg"))
    sl.reps      = to_int(form.get(f"set_{sl.id}_reps"))
    sl.completed = (new_weight is not None) or (new_reps is not None)

**Un champ absent du POST vaut `None` : la série est effacée et
dé-complétée.** Silencieusement, au prochain enregistrement.

Déplacer un `input` hors du formulaire, ou en oublier un dans une
recomposition, **détruit des données d'entraînement**. Vérifié au code, pas au
commentaire.

### La garde qui rend la suite sûre

Le dépôt gardait déjà cet invariant — mais en lisant le **source du gabarit** :
présence de la macro `set_values`, appelée par `past_line` et `future_line`.
Cette forme protège **une composition donnée**, pas l'invariant. Or c'est
précisément cette composition que le programme UI remplace.

`tests/test_session_set_preservation.py` vérifie le **comportement** : il rend
une vraie séance, découpe **chaque formulaire d'exercice**, le rejoue
exactement comme le navigateur l'enverrait, et vérifie qu'aucune série n'a
perdu ses valeurs. Il survit à n'importe quelle composition.

**Preuve par plantation** : en retirant le champ `reps` caché,
`test_replaying_a_form_unchanged_loses_nothing` échoue — une **perte de données
réelle**, pas seulement une chaîne absente. C'est ce que la garde de source ne
pouvait pas dire.

> ⚠ Ma première version de cette garde était **fausse** : elle exigeait que
> toute la page porte toutes les séries de la séance. Or chaque exercice a son
> propre formulaire et un POST ne touche que **ses** séries — 48 faux positifs
> sur le code canonique. Resserrée sur le bon périmètre.

Tier **T1**. Ne se retire pas, ne s'assouplit pas.

---

## 3. Ce que la tranche change

| | |
|---|---|
| **La bande devient une jauge horizontale** | on lit l'avancement d'un coup d'œil au lieu de parcourir une liste. Les marqueurs `✓ ● ○` restent : la **forme** porte l'état (`§7`) |
| **La série courante devient le readout souverain** | 40 px, phosphore, creusé dans un puits. **Le champ de saisie EST le readout** — sans JS, un champ texte est déjà de la manipulation directe ; en faire un affichage séparé aurait créé deux porteurs de la même valeur |
| **La commande dominante devient un trait** | `P-03` : l'aplat n'est pas nécessaire à la domination. La cible tactile, si — elle reste à **56 px** |
| **Le repos change de phosphore** | le minuteur devient le readout, et il passe au **bleu système** : un décompte est produit par le moteur, pas par l'utilisateur |
| **`S-11` correction** | variante de la série en cours, distinguée par un **liseré** — corriger, c'est ressaisir ; un quatrième phosphore diluerait les trois états validés |

### Un effet de bord qui sert une décision antérieure

Il n'y a plus **deux ambres pleins** sur l'écran de séance. C'était exactement
le motif qui avait fait retirer la surface de la carte active (*« deux ambres
pleins et l'ambre cesse de vouloir dire c'est à toi de jouer »*). **Le motif
est servi sans retirer la surface** — et « TERMINER LA SÉANCE » devient le seul
aplat ambre du produit, ce qui va dans le sens de `S-09` : une action
irréversible ne ressemble pas à « série suivante ».

---

## 4. `css:S4666` — fusionné, pas dupliqué

Le passage de la bande en `row` a d'abord été écrit en **seconde règle** sur
`.console__band`. Sonar l'a signalé, et ce fichier documente lui-même pourquoi
il a raison : *« deux règles pour un même sélecteur laissent croire à deux
composants, et la seconde gagne en silence sur toute propriété commune »*.
Fusionné dans la règle d'origine.

---

## 5. Relecture des relevés de décisions (`CLAUDE.md §5.2`)

| Décision | Verdict |
|---|---|
| `Q4` (UIV2) — la ligne de série devient un instrument | **respectée et enfin servie** — la ligne courante devient le readout souverain, la bande devient une jauge |
| `Q5` (UIV2) — trois rangs de surfaces | **respectée** — la jauge est du rang 2 (informatif), le readout du rang 1 |
| Tokens bleus — origine système | **respectée et étendue** — le minuteur de repos est une production du moteur, il prend le bleu |
| `D1` (HOME) — interactivité hybride | **respectée** — aucun JS ajouté ; tout fonctionne sans |
| `D3` (HOME) — ambre = action | **respectée et renforcée** — l'ambre plein devient exclusif à l'action terminale |
| `Sx_UIV3_02` — ordre `SystemOrigin → DeltaReadout → SetInstrument → CommandDock` | **respecté** — aucun bloc déplacé dans le DOM |
| `§7 no-color-only-state` | **respectée** — les trois marqueurs de forme restent ; le repos change aussi de FORME (deux champs → un cadran) |
| `Sx_UIV3_02 §7.4` — la correction est visible | **respectée** — `corriger` reste dans le segment, cible ≥ 44 px |

**Aucune décision violée.**

---

## 6. Vérifications

| Check | Résultat |
|---|---|
| `check_scope.py` | à relancer avant commit — traité comme **`SHARED_CODE`** (cf. rapport `U3` §4) |
| `ruff` (fichier neuf) | All checks passed |
| Tests ciblés + a11y + cible tactile | **166 verts** |
| Contrats, flux, tokens | **136 verts** |
| **Total en série** | **302 verts** |

Cibles tactiles mesurées **dans le navigateur** : commande 56 px, segments de
jauge 44 px, readout 68 px.

---

## 7. Exposition (`CLAUDE.md §5.1`)

Trois états **joués comme un utilisateur** — on remplit les champs, on appuie
sur la commande. Un état atteint en fabriquant un POST n'est pas un état
vérifié. Écrans **entiers**, 390×844, séance réelle à sept exercices, sur une
**copie** de la base locale.

**Deux artefacts de sonde corrigés avant publication**, tous deux lisibles
comme des défauts du produit :

* le lien d'évitement, visible parce que le clic le laissait focalisé ;
* l'en-tête **collant** recollé au milieu d'une capture pleine page, après une
  redirection ancrée qui avait défilé la page.

Une exposition trompeuse vaut moins que pas d'exposition.

---

## 8. Ce qui reste ouvert

* **`S-08` · `S-09` · `S-10`** — pris comme **hypothèses déclarées**, aucune
  n'est implémentée : elles portent sur la **composition**, pas sur
  l'instrument.
* **Le readout vide.** Sur une première série sans valeur, deux grands puits
  affichent « kg » et « reps ». C'est honnête — il n'y a rien à montrer — mais
  ça n'a pas la présence du `82` de la maquette. Question posée par le rendu,
  que la maquette ne posait pas.
* **L'illustration biomécanique** — chantier toujours parqué.
