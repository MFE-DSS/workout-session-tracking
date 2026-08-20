# `UIV3_VISUAL_BASELINE_01` — contrats visuels selon la souveraineté

**Phase 3, question 2 sur 2** : *est-ce que ce qu'on vient de valider peut
désormais dériver visuellement sans qu'on le sache ?*

> **B9 n'est pas « prendre des captures partout ».**
> Une capture devient un **contrat de design** uniquement là où la
> souveraineté de la surface le dit.

---

## 1. Brainstorming / Options / Risques / Choix retenu (`CLAUDE.md §3`)

| Option | Ce qu'elle donne | Risque | Retenue |
|---|---|---|---|
| **A** — capturer les 7 surfaces, gate pixel partout | couverture maximale | **fossilise l'architecture de cinq surfaces déjà programmées pour `UX4`** ; la prochaine refonte se battrait contre ses propres captures | **non** |
| **B** — gates différenciés par statut de surface | protège ce qui est conçu, laisse respirer ce qui doit changer | demande un modèle de souveraineté explicite — il existe depuis B8 | **OUI** |
| **C** — pas de baseline du tout, géométrie seule | zéro faux positif de rastérisation | aveugle à une couleur, une ombre, une graisse : la moitié des régressions visuelles | non |

**Choix : B.** Et une conséquence immédiate : `A` aurait été le comportement
par défaut de n'importe quel outil de capture. C'est précisément pourquoi la
décision devait être prise **avant** la première référence.

**Risque accepté** : les gates diffèrent d'une surface à l'autre, donc une
lecture rapide de la CI est moins uniforme. Compensé en rendant le statut
lisible dans le code plutôt que dans une note.

---

## 2. La correction normative, faite avant tout le reste

`24 × 24` est le **seuil WCAG 2.2 niveau AA**, et rien de plus fort. **Le W3C
ne produit pas les lois** : les obligations varient selon la juridiction et
passent par des textes distincts — en UE `EN 301 549` et l'**European
Accessibility Act**.

Le dépôt écrivait « plancher légal » dans **cinq fichiers**. C'est la faute
**symétrique** de celle que B8 évitait : l'une sur-déclarait une conformité
(44 présenté comme obligation AA), l'autre sur-déclarait une obligation.

Les deux formulations autorisées, désormais écrites dans le contrat :

```
WCAG 2.2 AA baseline      24 × 24 px CSS, ou exception SC 2.5.8 valide
AUREN product standard    44 × 44 px CSS minimum sur contrôle tactile désigné
```

**Exécutoire, pas documentaire** : une garde balaie la formulation dans les
cinq fichiers et vérifie que les deux formulations autorisées **et**
`EN 301 549` sont présentes. Une suppression seule aurait laissé la prochaine
plume réinventer la sienne.

### Une leçon d'écriture de garde, payée sur place

La première version cherchait une **négation française** dans les 80
caractères précédents. Elle a rougi sur **quatre fichiers qui disaient tous
l'inverse de ce qu'elle traquait** — la garde punissait sa propre doctrine.

Remplacée par un **token d'échappement mécanique** : une ligne qui doit citer
la formulation porte `VOCAB-INTERDIT`. Plantée en trois cas — affirmation
française nue **rougit**, affirmation anglaise nue **rougit**, citation
échappée reste **verte**.

> Une heuristique de langage naturel dans une garde produit des faux positifs
> pour toujours, et les auteurs finissent par se battre contre elle.

---

## 3. `VISUAL_ENV_V1` — et pourquoi il refuse de promouvoir

Une capture dépend du système, du navigateur, des polices et du matériel.
Comparer une référence macOS à un rendu Chromium Linux **teste la
rastérisation, pas le design**.

L'environnement est déclaré : Playwright, Chromium, plateforme, image du
runner, DPR, locale, fuseau, schéma de couleurs, `reduced-motion`, pile de
polices, largeurs, fixture.

**`may_promote_to_canonical()` renvoie `False`, et dit pourquoi :**

| Blocage | Conséquence |
|---|---|
| `pyproject.toml` déclare **`playwright>=1.40`** — plage ouverte | un bump mineur change Chromium, donc la rastérisation, donc **toutes les références d'un coup** |
| `runner_image: ubuntu-latest` est un **alias mouvant** | l'image change sous le même nom, avec les polices système dont dépend un rendu tout-mono sans webfont |

Ce n'est pas un défaut de configuration à corriger ici : **épingler une
dépendance est du `ci_infra`**. La tranche le **nomme et le bloque** plutôt que
de produire des références qui se périmeraient au premier `pip install`.

Un `False` n'interdit pas de **capturer** — il interdit de **promouvoir**.

---

## 4. Trois types de gate, encodés

| Statut | Surfaces | Bloquant | Preuve seule |
|---|---|---|---|
| **SOVEREIGN** | Home · Session | pixel · géométrie · cibles · a11y · fonctionnel · non-rétrécissement | — |
| **TRANSITIONAL** | Profile · Library · Progress · Dashboard · History | géométrie · cibles · a11y · fonctionnel · non-rétrécissement | **pixel** |
| **UTILITY** | login · mot de passe · admin · exports | idem transitionnel | pixel |

Une surface non inscrite est `TRANSITIONAL` — donc **jamais** un gate pixel
bloquant par défaut d'inscription.

**Gouvernance des références** : remplacer un golden souverain exige cinq
preuves — `decision_ref`, `before`, `after`, `geometry_delta`,
`human_verdict` — et `promotion_blockers()` **nomme celles qui manquent**
plutôt que de résumer en « refusé ». Sur une surface transitionnelle, la
capture **documente** l'état sans le gouverner : la rafraîchir pendant une
refonte est normal.

**Planchers dominants protégés** : `TERMINER LA SÉANCE ≥ 56 px`, **avec son
histoire**. Un plancher qu'on ne mesure plus est signalé `NON MESURÉ` — le
silence ressemble trop au succès.

---

## 5. Le trou que B8 ne pouvait pas voir, maintenant mesuré

Chromium verrouille la mise en page dans un `<details>` fermé : y mesurer rend
des faux positifs — 23 en phase 2. B8 les excluait, et son inventaire était un
**plancher assumé**.

B9 ouvre chaque disclosure et fait l'**union** avec l'état par défaut.

| | |
|---|---:|
| cibles révélées | **558** |
| sous le standard produit | **214** |
| **sélecteurs distincts** | **7** |

**L'essentiel n'est pas périphérique : c'est la navigation globale.**
`a.topbar__link` à 37 px sur **les sept surfaces**, le déclencheur `☰` à
39,4 × 41, « Déconnexion » à 37. Le menu principal du produit n'avait jamais
été mesuré.

**214 → 21.** Et la géométrie de l'état par défaut est **strictement
inchangée** : `195 inchangés, 0 grandi, 0 rétréci`. Ces changements ne vivent
que derrière les disclosures.

### Un piège de mesure, et l'inventaire qu'il gonflait

Identifier une cible par `chemin|texte|y` fait passer pour « révélé » tout ce
qu'une disclosure ouverte **décale**. Le premier total disait **688** ; avec
une identité sans `y`, il dit **558**. `topbar__brand`, déjà réparé en B8,
réapparaissait parmi les cibles cachées.

Un inventaire qui compte du décalage pour de la découverte fait exactement ce
que le décompte 161 faisait : mesurer le mauvais objet, avec assurance.

---

## 6. Six cibles que je ne ferme pas, nommées et chiffrées (`§3.4`)

**Trois `<summary>` empilés à 19,5 px d'intervalle ne peuvent pas recevoir
chacun 44 px de zone tactile : les zones se chevaucheraient**, et un appui
atterrirait sur le contrôle voisin. Une extension qui se recouvre est **pire**
que pas d'extension — elle déplace le défaut et le rend invisible à la mesure.

| Sélecteur | Mesure | Surface |
|---|---|---|
| `.method-reminder details > summary` | 19,5–39 px × 3 | `session-active`, **hors console** |
| `.session-feedback__note > summary` | 27,5 px | `session-active`, **hors console** |
| `.history-item__actions > summary` | 26 px | `history` |
| `.history-item__actions .btn--ghost` | 26,8 px, voisins adjacents | `history` |

Ce sont des **densités de mise en page**, pas des défauts de feuille de style.
Les fermer demande de l'**espace** entre les contrôles, donc un changement
structurel :

- `method-reminder` et `session-feedback` vivent sur `session-active` mais
  **hors console** — la console est à 0. Les retoucher violerait son statut de
  `reference consumer`.
- `history` est **`TRANSITIONAL`** : sa mise en page est programmée pour
  `UX4_03`, et lui imposer un espacement maintenant reviendrait à
  contractualiser une architecture qu'on prévoit de refaire.

**Reportées à `UX4`, avec leur mesure.** Une exception nommée et chiffrée
n'est pas une dette cachée.

### Une règle morte, laissée deux versions

J'ai écrit une extension par pseudo-élément pour ces `<summary>`, l'ai crue
active, l'ai réduite, puis mesurée sans effet. Elle a survécu **deux versions
successives** avant d'être correctement mesurée. Du CSS mort accompagné d'un
commentaire assuré se lit exactement comme du CSS qui marche.

---

## 7. Ce que la mesure a corrigé chez elle-même

| Instrument | Ce qu'il rendait | Correction |
|---|---|---|
| identité de cible avec `y` | 688 « révélations » dont du simple décalage | identité `chemin|texte` |
| capture cadrée sur `header.topbar` | **la barre seule** — le panneau déroulant est en position absolue et déborde | capture de fenêtre |
| extension sur `<summary>` voisins | rien, et un chevauchement si elle avait marché | retirée, exception documentée |

La capture cadrée est la plus instructive : elle prouvait l'**inverse** de ce
qu'elle prétendait montrer, et deux images identiques auraient été lues comme
« aucun changement ».

---

## 8. Gardes

**28 + 23 = 51 gardes** sur cette tranche (`test_target_size_taxonomy`
étendu, `test_visual_contract` neuf), et **3 plantations** sur la garde de
vocabulaire.

Ce qu'elles protègent : la souveraineté des surfaces · le refus de promotion
hors environnement canonique · les cinq preuves de remplacement d'un golden ·
le plancher de `TERMINER LA SÉANCE` · l'identité de cible sans `y` ·
l'ouverture exhaustive des disclosures · le vocabulaire juridique.

---

## 9. Relecture du relevé de décisions (`CLAUDE.md §5.2`)

`DESIGN_DECISIONS_UIV2_SURFACES.md` :

| Décision | Verdict |
|---|---|
| **Q1** — la connexion porte l'identité | **non concernée** |
| **Q2** — ancre visuelle de l'accueil | **respectée** — l'accueil ne change qu'à l'intérieur du menu déroulant |
| **Q3** — « État du jour » replié | **respectée** — `open_disclosure_count` inchangé à l'état par défaut |
| **Q4** — la ligne de série est un instrument | **respectée** — console à 0, dogfood intact, aucun sélecteur ne l'atteint |
| **Q5** — trois rangs de surface | **respectée** — aucun conteneur ajouté, aucun rang changé |
| **Tokens bleus** mesurés | **non concernée** — aucune couleur touchée |

`§5.3` — rien n'est retiré. `§5.4` — **aucune couleur** : la tranche est
entièrement géométrique et documentaire.

---

## 10. Ce qui reste

- **Génération des références : bloquée, volontairement.** Elle attend
  l'épinglage de Playwright et du runner (`ci_infra`). Produire des goldens
  maintenant les périmerait au premier `pip install`.
- **Six cibles sous disclosure** reportées à `UX4` avec leur mesure.
- **`Sb_OPS_CI_LINT_TIMEOUT_01`** reste indépendante. B9 ne l'attend pas, et
  la gate visuelle ne doit pas hériter d'un job lint instable comme
  prérequis.
