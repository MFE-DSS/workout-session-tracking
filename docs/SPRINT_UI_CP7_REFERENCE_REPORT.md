# UI-CP7 REFERENCE — un document se présente comme un document

**Statut** : `PR GREEN / MERGE PENDING` · **Branche** : `sb/ui-cp7-reference`
**Base** : `114b81d`

> ⚠ **CETTE TRANCHE NE SERA PAS MERGÉE SANS L'OPÉRATEUR.**
>
> `CLAUDE.md §5.1` est un contrat **versionné**, qu'un prompt de session ne peut
> pas désactiver : *« Avant tout commit touchant un template ou une feuille de
> style, l'agent produit un rendu réel et le soumet à l'opérateur. L'opérateur
> tranche. »*
>
> L'autorisation nocturne a pré-tranché **ce qu'il faut construire**
> (`Q1=C`, `Q2=B`, `Q3=A`, `Q4=A scindée`). Elle n'a pas tranché **si le rendu
> est acceptable** — et c'est exactement la question que `§5.1` existe pour
> poser, après qu'une tranche d'UI a livré CI verte, Sonar vert, 4 898 tests
> passants et un objet jugé inacceptable au premier coup d'œil.
>
> Les rendus ont été produits et soumis. Le merge attend.

---

## 1. La règle qui gouverne la tranche

`AUREN_INSTRUMENTS §2bis`, mot pour mot :

> **« Un document ne doit jamais avoir l'air d'un instrument en panne. »**
> « La frontière doit être **perceptible**. »

---

## 2. Mesuré au navigateur, avant de toucher quoi que ce soit

390 × 844 et 1440 × 900, application en marche, session non-prod produite par
`scripts/visual_baseline_runtime.py` — **aucun identifiant inventé**.

| surface | mots | écrans | cartes | `<details>` | titre | section | cibles < 44 |
|---|---|---|---|---|---|---|---|
| `/science` | 1 526 | 12,0 | **18** | 6 | **18 px** | **22 px** | 2 |
| `/science/atlas` | 2 074 | **15,5** | **32** | **0** | **18 px** | **22 px** | **9** |
| `/coach-report` | 499 | 3,9 | 0 | 0 | 22 px | 14 px | 2 |
| `/export` | 100 | 1,5 | 3 | 0 | 18 px | 13 px | 0 |

Ligne de texte en desktop, mesurée avec les **métriques de glyphe réelles**
(8,43 px à 14 px) et non une largeur supposée : **134** caractères sur
`/science`, **156** sur `/export`, **86** sur `/coach-report`. La cible
typographique est ~65.

### Deux défauts que seule la mesure a rendus visibles

1. **Inversion de hiérarchie** sur les deux surfaces `/science` : le titre du
   document (18 px, **centré**) est plus petit que ses propres titres de
   section (22 px). Un document dont le titre chuchote pendant que ses sections
   crient ressemble à un instrument, qui lui aussi ouvre sur des intitulés de
   bloc.
2. **Aucune colonne de lecture** : `main` occupe toute la largeur, sur les
   quatre surfaces.

---

## 3. ⚠ Deux erreurs de mon propre brief d'arbitrage, corrigées

**`F1` affirmait que l'atlas n'a « AUCUNE navigation interne ». C'est faux.**
`atlas.html:6-10` porte un `<nav class="atlas-toc">` avec une ancre par
famille, rendu en pastilles depuis `Sb_07`. Je l'ai découvert en **ouvrant le
gabarit** plutôt qu'en relisant ma note.

`Q3 = A` reste la bonne réponse, mais la moitié du travail était faite : la
tranche ajoute le **repli**, elle ne crée pas le sommaire.

**Et mon arithmétique CSS était fausse aussi.** J'avais calculé ~24 px pour les
pastilles à partir de `font-size: 12px; padding: 4px 10px`. Le rendu en donne
**28**. Je ne l'avais pas affirmé — précisément parce qu'une déclaration CSS
n'est pas une géométrie — et c'était la bonne prudence.

---

## 4. Ce qui a été livré, réponse par réponse

### `Q1 = C` — tête de document **et** colonne de lecture

`.doc` borne la colonne en **`ch`**, l'unité qui suit la police : elle reste à
~68 caractères quelle que soit la taille choisie, là où un `max-width` en px
dériverait au premier changement d'échelle.

`.doc-head__title` prend le rang **DISPLAY (32 px)**, aligné au début. C'est la
moitié de `Q6` — « relevé souverain **ou titre d'écran** » — que rien
n'utilisait sur ces surfaces. Un document n'ayant pas de relevé souverain, ce
titre est le seul DISPLAY de l'écran, comme `Q6` l'exige.

### `Q2 = B` — remplacer la carte, pas la retirer

`.card` est le conteneur de **rang 1** du socle. Cinquante cartes autour de
prose faisaient lire un tableau de bord. Elles deviennent `.doc-prose` (aucun
conteneur) et `.doc-entry` (un filet, pas un cadre).

⚠ **`/export` garde ses trois cartes, et c'est une décision consignée par une
garde.** Elles ne contiennent pas de prose : ce sont un menu d'actions, un
relevé chiffré et deux boutons. `Q5` réserve la carte à ce rang. Appliquer la
règle là aurait été l'appliquer où elle ne dit rien.

### `Q3 = A` — le repli, en adoptant le composant existant

`.disclosure` porte **déjà** la géométrie 44 px, le chevron et le focus. Son
propre commentaire dit qu'il s'adopte « pour UNE classe sur le `<details>` » et
qu'« un composant qu'on n'adopte pas parce qu'il coûte trop cher à adopter
n'est pas un composant : c'est une intention ». On l'adopte.

Deux décisions de rendu, toutes deux adossées à `§2bis` :

- **La première famille reste ouverte.** Neuf lignes repliées et rien d'autre
  donneraient exactement ce que `§2bis` interdit : un document qui a l'air d'un
  instrument vide.
- **Les ancres publiques `#family-<slug>` restent sur le `<details>`
  lui-même.** À l'intérieur du repli, un navigateur qui n'ouvre pas
  automatiquement un `<details>` ciblé par un fragment ferait atterrir le
  lecteur sur du contenu masqué.

### `Q4 = A, scindée` — la signature, et l'impression

Le pied générique **disparaît de partout** (`MODES_AVEC_PIED = ()`). Ce n'est
pas une soustraction seule (`§5.3`) : chaque document gagne une **signature**
— provenance, nom du document, version ou date réelle.

La signature **nomme le produit en premier**, et ce n'est pas cosmétique : les
règles d'impression masquent la topbar, donc sur une feuille remise à un coach
externe la signature est le seul porteur du nom.

L'**affordance** d'impression reste sur `coach-report` seul. Le dépôt le décrit
comme « un document à présenter à un coach externe » : son intention est
établie. Celle d'un atlas de machines ne l'est pas.

---

## 5. Résultat mesuré

| surface | écrans | cartes | `<details>` | max police | cibles < 44 | pied |
|---|---|---|---|---|---|---|
| `/science` | 12,0 → **11,1** | 18 → **0** | 6 | 22 → **32** | 2 | oui → **non** |
| `/science/atlas` | **15,5 → 3,9** | **32 → 0** | 0 → **9** | 22 → **32** | **9 → 0** | oui → **non** |
| `/coach-report` | 3,9 → 3,8 | 0 | 0 | 22 → **32** | 2 | oui → **non** |
| `/export` | 1,5 | 3 *(voulu)* | 0 | 18 → **32** | 0 | oui → **non** |

Colonne de lecture en desktop : **134 → 68**, **86 → 64**, **156 → 75**
caractères par ligne.

Les deux cibles restantes sous 44 px sur `/science` et `/coach-report` sont des
**liens en ligne dans la prose** (« CC BY 4.0 ») et des libellés de légende —
une autre catégorie de la taxonomie que le plancher produit, qui vise les
contrôles autonomes. Elles ne sont pas touchées ici, et ne l'étaient pas avant.

---

## 6. ⚠ Une limite mesurée, pas contournée

**Un `<details>` fermé s'imprime amputé.** J'ai essayé
`display: block !important` puis `content-visibility: visible` sur le panneau.
**Les deux échouent** — mesuré sous `emulate_media(print)` : 2 771 px contre
3 293 à l'écran, 356 mots contre 441.

Je ne livre donc pas une règle qui prétend le déplier.

La portée réelle est étroite et **vérifiée** : `coach-report`, le seul document
porteur d'une affordance d'impression, ne contient **aucun** `<details>`
(mesuré à zéro). Reste ouvert : un lecteur qui fait `Ctrl+P` sur l'atlas
obtient les familles ouvertes seulement. `BLOCKED` sans arbitrage — le corriger
supposerait soit de tout déplier par défaut (et de rendre les 15,5 écrans que
cette tranche vient de ramener à 3,9), soit du JavaScript, que le périmètre
exclut.

---

## 7. Les gardes

**15 neuves** (`tests/test_ui_cp7_reference.py`), **4 repointées**, aucune
affaiblie.

| Garde repointée | Propriété protégée, inchangée |
|---|---|
| `test_le_document_garde_son_pied…` | `§5.3` : pas de soustraction nue → on exige la **signature** là où on exigeait le pied |
| `test_les_modes_qui_rendent_quoi…` | la table reste déclarée et vérifiée, simplement **vide** |
| `test_footer_shows_auren` | le nom produit reste visible → porté par la signature |
| `test_atlas_page_renders` | l'atlas déclare sa **version** → on épingle la valeur, plus son libellé |

### ⚠ Trois de mes propres gardes étaient fausses

Écrites, rouges, diagnostiquées :

1. **Elle lisait la prose comme du code.** La garde « aucune couleur en dur »
   trouvait le `#999` cité dans le **commentaire qui raconte** qu'une couleur
   en dur avait été refusée. Correction : retirer les commentaires avant de
   scanner. Vérifiée par mutation — un `#abc` planté dans le code est attrapé.
2. **Une sous-chaîne n'est pas un objet.** `\bcard\b` attrapait `rule-card`,
   le tiret étant une frontière de mot. Correction : extraire les listes de
   classes et chercher le **jeton** exact.
3. **Elle mesurait la mauvaise règle.** `re.search(".doc-head__title")` sur
   toute la feuille trouvait la déclaration du bloc d'**impression**, plus
   haut. Correction : borner la lecture au bloc de la tranche.

### ⚠ Deux régressions que j'ai introduites et que le rendu a montrées

- **Le sommaire à 44 px occupait plus d'un demi-écran.** Invisible dans les
  chiffres, qui ne comptent que les cibles **non** conformes. Corrigé par une
  mise en grille : les 44 px sont conservés et le sommaire est plus court
  qu'avant la tranche.
- **J'avais ouvert un second bloc `@media print`.** Trois gardes l'ont refusé
  pour une couleur en dur — et elles avaient raison sur un point que je n'avais
  pas vu : la feuille en a déjà un. Deux blocs du même sujet divergent. Fondu
  dans l'existant, sans introduire aucune couleur.

---

## 8. Relecture du relevé de décisions (`CLAUDE.md §5.2`)

| Décision | Verdict |
|---|---|
| `§2bis` — un document ne ressemble pas à un instrument | **respectée** — c'est l'objet de la tranche |
| `Q5` — la carte est le conteneur de rang 1 | **respectée** — retirée de la prose, gardée sur le fonctionnel |
| `Q6` — un seul DISPLAY par écran | **respectée**, garde dédiée |
| `§5.3` — jamais une soustraction seule | **respectée** — signature et colonne partent avec le retrait |
| `§5.4` — toute couleur est un token | **respectée** — la grammaire n'introduit **aucune** couleur |
| Deux dialectes visuels, pas trois | **respectée** — la frontière se lit à la forme, pas à un ornement |
| `IDENTITY_HOME_EXCEPTION` | non concernée |
| Zéro framework, zéro JS | **respectée** — `<details>` natif |

---

## 9. Ce que ce rapport ne prétend pas

- Le rendu **sur papier** n'a pas été vérifié sur une sortie réelle, seulement
  sous média émulé.
- L'atlas n'a pas été mesuré en **paysage** ni sur viewport court.
- La lisibilité des 2 074 mots est une question **éditoriale**, hors tranche.
- Playwright Chromium **n'est pas Safari iOS**.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
