# Passe critique nocturne AUREN — compte rendu

**Période** : 2026-09-24 · **Canonique de départ** : `2cdac58` ·
**Canonique d'arrivée** : `114b81d` · **Production** : `4b91e6e`

---

## 1. Ce qui a été livré

| Tranche | Merge | CI canonique | Objet |
|---|---|---|---|
| `REC-CP1` | `abb3625` | 7/7 | harnais de rejeu, baseline, diagnostic |
| `REC-CP2` | `242674b` | 7/7 | politique V3 **en ombre**, instrument réparé |
| `REC-CP3` | `4b91e6e` | 7/7 | explication structurée, lue au lieu d'être devinée |
| `UI-CP7` | **non mergée** | en cours | `PR GREEN / MERGE PENDING` — voir `§5` |

**Déploiement unique** : `4b91e6e` → `deploy/prod/2026-09-24-1118-4b91e6e`.
17 smoke PASS, `check_alembic_drift` OK, vérification externe `200` en 195 ms.
Point de retour arrière conservé : `2cdac58`.

---

## 2. La question posée, et sa réponse

Le `§6` demandait de trancher : le blocage de recommandation vient-il du
**départage** (`A`), du **classement primaire** (`B`), ou des **deux** (`C`) ?

**Réponse : `C`, mais empilés — et c'est l'empilement qui dicte l'ordre des
corrections.**

| Mutation, appliquée seule puis annulée | Gagnant | Égalités |
|---|---|---|
| moteur intact | `liss-abs` partout | **0 %** |
| bonus « cardio absent » à 0 | `liss-abs` partout | 0 % |
| `WEIGHT_ALTERNATION` à 0 | `liss-abs` partout | **72 %** |

`A` est réel mais **inactif**, masqué par `B`. Corriger `A` seul ne changerait
rien ; corriger `B` seul découvrirait un moteur épinglé par l'ordre du
catalogue à 72 %.

Et le relevé des consommateurs dit *pourquoi* `B` : le moteur calcule
**trois** horizons d'exposition ; celui à 7 jours **n'a aucun lecteur**, celui à
14 jours n'en a qu'un — un booléen pour la spécialisation. Le classement des six
gabarits du noyau ne voit que les **trois dernières séances**.

> Le moteur mesure la couverture sur deux semaines et ne s'en sert pas pour
> classer.

---

## 3. ⚠ Trois diagnostics réfutés — par la mesure, jamais par un raisonnement

1. **« Le départage épingle »** — réfuté : 0 % d'égalités, marge médiane 20.
2. **« Le bonus cardio domine »** — réfuté par mutation : 90 → 80, toujours en
   tête.
3. **« V2 est bloqué »** — réfuté par la boucle fermée : quand le conseil est
   **suivi**, V2 rend six gabarits différents sur dix décisions.

Le troisième a rétréci et précisé le défaut réel :

| | comportement de V2 |
|---|---|
| conseil **suivi** | tourne correctement |
| conseil **décliné** | répète le même conseil indéfiniment |

> **V2 n'est pas « épinglé ». Il n'a aucune notion d'avoir déjà donné un conseil
> que l'utilisateur a écarté.**

C'est le vrai énoncé de la plainte de dogfood, et il **déborde le scoring** : le
traiter suppose de mémoriser ce qui a été *proposé*, donc une persistance
nouvelle. **Non implémenté** — hors du périmètre autorisé.

---

## 4. ⚠ Six défauts appartenaient à l'instrument, pas au produit

1. Le corpus partait de zéro → les trois premières décisions de chaque
   trajectoire étaient le repli de démarrage à froid, `push-a` partout.
2. Le helper de test rejouait toutes les trajectoires sur **le même
   utilisateur** — le CLI créait déjà un compte par trajectoire pour cette
   raison exacte.
3. Le semis tronquait chaque séance à **deux exercices** sur sept : 7 zones
   servies sur 11, ce qui **fabriquait** le déficit permanent qu'il mesurait.
4. Le corpus était en **boucle ouverte** — le conseil n'y est jamais suivi.
5. Une garde comparait des **gagnants** là où le gagnant ne bouge jamais : elle
   ne pouvait rien détecter.
6. Une garde que j'avais écrite **avait tort, pas le code** : exiger que V3 ne
   répète jamais revenait à traiter la variété comme une preuve de justesse, ce
   que le `§11` proscrit.

---

## 5. `UI-CP7` — livrée, non mergée, et c'est délibéré

`CLAUDE.md §5.1` est **versionné** et ne se désactive pas par un prompt de
session. La directive nocturne a pré-tranché **quoi** construire
(`Q1=C`, `Q2=B`, `Q3=A`, `Q4=A scindée`) ; elle n'a pas tranché **si le rendu
est acceptable** — la question même que `§5.1` existe pour poser.

Les rendus avant/après ont été produits et soumis. **Le merge appartient à
l'opérateur.**

Résultat mesuré au navigateur :

| surface | écrans | cartes | `<details>` | max police | cibles < 44 |
|---|---|---|---|---|---|
| `/science/atlas` | **15,5 → 3,9** | **32 → 0** | **0 → 9** | 22 → **32** | **9 → 0** |
| `/science` | 12,0 → 11,1 | **18 → 0** | 6 | 22 → **32** | 2 |
| `/coach-report` | 3,9 → 3,8 | 0 | 0 | 22 → **32** | 2 |
| `/export` | 1,5 | 3 *(voulu)* | 0 | 18 → **32** | 0 |

Colonne de lecture : **134 → 68**, **86 → 64**, **156 → 75** caractères/ligne.

### Corrections de ma propre main dans cette tranche

- Mon brief affirmait que l'atlas n'a **aucune navigation interne** : il en a
  une depuis `Sb_07`.
- Mon arithmétique CSS donnait ~24 px là où le rendu donne **28**.
- **Trois gardes neuves étaient fausses** — l'une accusait son propre
  commentaire, l'une prenait `rule-card` pour une carte, l'une mesurait la règle
  du bloc d'impression.
- **Deux régressions** invisibles dans les chiffres et évidentes au rendu : un
  sommaire à 44 px mangeant un demi-écran, et un second bloc `@media print`.

### Une limite mesurée, pas contournée

Aucun CSS ne déplie un `<details>` fermé à l'impression :
`display: block !important` et `content-visibility: visible` échouent tous deux
(2 771 px contre 3 293, 356 mots contre 441). Je ne livre pas une règle
décorative. Portée vérifiée : `coach-report`, seul document imprimable, ne
contient aucun `<details>`.

---

## 6. Ce qui reste ouvert

| Sujet | Statut |
|---|---|
| Promotion de V3 | **techniquement possible** depuis `REC-CP3` — mais le cas « conseil décliné » n'est traité par aucune politique |
| « Conseil décliné » | `DESIGN_PROPOSAL` — suppose une persistance nouvelle, **non inventée** |
| Merge d'`UI-CP7` | **attend l'arbitrage visuel** (`§5.1`) |
| Impression d'un atlas replié | `BLOCKED` — déplier par défaut annulerait la tranche, et le JS est hors périmètre |
| `UI-CP8`, `UI-CP9`, `CP10`, `CP11` | non ouvertes |

---

## 7. Discipline

**Aucun** force-push, **aucun** rebase de branche publiée, **aucun** squash,
**aucun** `--admin`. Chaque merge a franchi la porte complète : CI verte, Sonar
`OK`, `CLEAN/MERGEABLE`, zéro thread, sweep local `tous les lots sont verts.`

**Trois worktrees** créés puis retirés après vérification (propre, zéro commit
unique). Les onze préexistants sont intacts, dont les trois protégés
(`-sb-asset-03b-1`, `-custom`, `-fresh`).

Aucun identifiant de production inventé : la session de mesure visuelle vient
de `scripts/visual_baseline_runtime.py`, qui crée un compte non-prod.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
