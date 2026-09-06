# `Sb_UI_PROGRAM_EDITOR_STYLES_01` — l'éditeur de programmes rejoint sa propre feuille

Cinquante styles inline sur trois gabarits. Le vocabulaire qui les remplace
**existait déjà**, à quelques classes près.

## 1. Le constat

| | |
|---|---|
| dette d'attributs `style` du dépôt | **249** sur 35 gabarits |
| part de la famille `user_programs/` | **59** sur 4 gabarits |
| dont de pur espacement | **27** |
| valeurs dynamiques légitimes dans le lot | **0** |

Ces quatre gabarits écrivaient en dur `max-width: 40rem` — que `.pd-page`
porte depuis `Sb_UI_PROGRAM_DETAIL_01` —, des `display:flex` identiques à
`.pd-head__row`, et des `margin-top` que `--space-sm/md/lg` nomment déjà.

**Quinzième occurrence du diagnostic** : *le produit ne manque pas de la
décision, il manque du moyen de l'appliquer.* Ici, le moyen était écrit dans
la feuille, à deux mille lignes de là.

## 2. Brainstorming · options · risques · choix (`CLAUDE.md §3`)

| Option | Pourquoi non / oui |
|---|---|
| **A — des utilitaires d'espacement** (`.mt-1`, `.mt-2`…) | Rejetée. Ce sont les mêmes attributs `style`, déguisés en classes. La dette changerait de forme, pas de nature |
| **B — un nouveau préfixe `.up-*`** pour l'éditeur | Rejetée. Elle dupliquerait `.pd-page`, `.pd-note`, `.pd-section` à l'identique, sous un autre nom |
| **C — étendre la famille `.pd-*`** | **Retenue.** Le préfixe dit « program detail » et couvrira l'éditeur entier : un renommage coûterait un diff sur cinq gabarits pour ne rien dire de plus. Douze classes ajoutées, quinze réutilisées |

**Risque réel** : un refactoring « visuellement neutre » qui ne l'est pas.
C'est mesurable, donc mesuré — voir `§4`.

## 3. Ce qui change de valeur, et pourquoi

Trois écarts délibérés, tous sur des valeurs qui n'étaient sur **aucune
grille** :

| Écriture | Devient | Motif |
|---|---|---|
| `margin:.75rem` (12 px) | `--space-sm` (8 px) | arbitrage « les espacements de 12 px s'alignent sur 8 » |
| `margin:.35rem` (5,6 px) | `--space-xs` (4 px) | même arbitrage |
| `font-size:1.5rem` (24 px) sur le grade | **22 px** | le grade est le relevé souverain de sa page ; il rejoint le rang SECTION (`Q6`) |
| `font-size:.85em` sur le slug | **12 px** | rang META. Une taille relative ne se lit pas dans la feuille |

Et un titre de bloc, `<h2 style="font-size:1rem">`, devient un vrai
`.section-header` — donc 22 px depuis `Sb_UI_SECTION_RANK_01`.

## 4. La mesure qui décide (`CLAUDE.md §5.1`)

Rendu **depuis deux serveurs**, pas une injection : la tranche change des
gabarits, pas seulement une feuille. Le port 8103 sert l'arbre canonique, le
8104 l'arbre de la tranche.

| Page | Hauteur avant → après | Styles inline dans `main` |
|---|---|---|
| `/programs/1/quality` | 2465 → 2459 px (**−0,2 %**) | **30 → 0** |
| `/programs/1/publish` | 932 → 932 px (**0 %**) | **13 → 0** |
| `/programs/1/generate` | 1139 → 1139 px (**0 %**) | **10 → 0** |

Les six pixels de la page qualité sont **comptés** : deux espacements à −4 px
et le grade à −2. Rien d'autre ne bouge.

## 5. Une paire de tests migrée, et devenue plus forte

Deux tests gardaient un invariant réel et subtil : **seule une vraie erreur de
saisie porte la couleur de danger**, jamais une étape que l'utilisateur n'a pas
encore franchie. Ils l'épinglaient ainsi :

```python
assert "color:var(--danger)" in r.text
```

C'est **l'écriture**, pas la propriété — le mode d'échec relevé dans
`guards-that-guard-nothing` : *interdit le refactoring sans protéger
l'invariant*. Pire, cette forme est **contournable** : remplacer l'attribut par
une classe grise l'aurait laissée verte.

Ils vérifient désormais que la bonne classe est posée **et** que cette classe
porte — ou ne porte pas — `--danger` dans la feuille.

**Plantation du défaut que l'ancienne écriture ne pouvait pas voir** : donner
`color: var(--danger)` à `.pd-notice`. L'ancienne garde serait restée verte ;
la nouvelle **mord**.

## 5bis. Trois gardes, un seul trou, trois shards rouges

La CI de cette PR est passée au rouge sur **les trois shards à la fois**. Ce
n'était pas le bruit de runner de la veille : une vraie panne, systématique.

La cause : un commentaire CSS que j'ai écrit dans cette tranche cite `#2e7d32`
— le hexadécimal fantôme retiré par `Sb_UI_PHANTOM_TOKENS_01` — pour expliquer
ce que `.pd-success` remplace. **Trois gardes ont lu cette prose comme du
code** :

```python
block = css[css.index("Sb_UI_03.1 — Mobile Bottom Navigation"):]
assert not re.search(r"#[0-9a-fA-F]{3,6}", block)   # ← lit aussi les commentaires
```

`test_app_shell_navigation` · `test_app_shell_hardening` ·
`test_app_shell_desktop_rail`. Trois copies du même idiome, dans trois shards
différents. **Huitième occurrence relevée dans ce dépôt d'une sonde qui prend
la prose pour du code** — la précédente lisait la balise `<details>` comme le
mot « détails ».

Un hexadécimal entre `/* */` ne peint rien : la garde condamnait la
documentation d'un défaut corrigé. La sonde retire désormais les commentaires,
et elle vit **en un seul exemplaire** dans `tests/helpers.py` — trois copies
d'une même sonde divergent, ce qui est exactement le mode d'échec qu'elle
corrige.

**Ce que je n'ai PAS fait** : réduire leur portée. `css[index:]` prend tout ce
qui suit le marqueur, jusqu'à la fin du fichier — plusieurs milliers de lignes.
Le nom dit « rail CSS », la réalité dit « tout ce qui a été écrit depuis ».
C'est accidentel, et c'est **utile** : cette largeur garde chaque bloc ajouté
depuis. Elle est conservée telle quelle ; ce sont les **messages** qui cessent
de mentir sur la portée.

**Vérifié de bout en bout** : un `#ff0000` planté dans le CODE fait tomber les
trois ; le même hexadécimal dans un commentaire les laisse vertes.

## 6. Relecture du relevé de décisions (`CLAUDE.md §5.2`)

| Décision | Verdict |
|---|---|
| **Q1** · **Q2** · **Q3** · **Q4** · **Q4/DF-C** | non concernées |
| **Q5** — trois rangs de surface | **respectée** : aucune carte ajoutée ni retirée ; les conteneurs existants gardent leur rang |
| **Q6** — échelle E3 | **appliquée** : le grade rejoint SECTION (22), le slug META (12), le `<h2>` devient un vrai `.section-header` |
| **Q7** — un seul aplat ambre par écran | **respectée** : aucun aplat touché |
| **Q8** — aucune opacité décorative | non concernée : la tranche ne touche aucune opacité |
| **`§5.3`** jamais une soustraction seule | **respectée** : rien ne disparaît de l'écran — les styles changent de lieu, pas d'effet, et c'est mesuré à 0 % de hauteur sur deux pages sur trois |
| **`§5.4`** toute couleur est un token | **respectée** : les deux seules couleurs du lot passent par `.pd-error` / `.pd-success`, qui pointent sur `--danger` et `--ok` |
| **`§5.5`** la centralité avant la facilité | tranche de dette assumée comme telle — elle ne prétend pas être un arbitrage de forme |

## 7. Vérifications

`check_scope` **SHARED_CODE** · broad sweep ciblé sur la famille
`user_programs` + les gardes UI · **164 tests** · cliquet des styles inline
resserré **249 → 199** (32 gabarits) · ruff OK.

Rendu exposé (`§5.1`) avant et après, sur trois pages réelles servies par deux
serveurs distincts.

## Verdict

**LIVRÉ.** Cinquante attributs `style` disparaissent sans qu'un pixel bouge sur
deux pages et six sur la troisième, tous comptés. Douze classes ajoutées à une
famille qui en portait déjà quinze utilisables. Une paire de tests migrée d'une
écriture vers une propriété, et vérifiée sur le défaut qu'elle ne voyait pas.

## 8. Ce qui reste ouvert

* **`user_programs/plan.html`** — 9 styles inline, non traités : le gabarit est
  touché par `Sb_UI_PHANTOM_TOKENS_01` (PR #210) sur la même ligne. Deux
  tranches sur une ligne se conflictent pour rien ;
* **199 styles inline** sur 32 gabarits. Les cinq plus gros restants :
  `body_overview` (21), `squad_detail` (20), `profile` (17), `dashboard` (13),
  `index` (13) ;
* **une duplication de contenu, vue au rendu** : sur `/programs/1/quality`,
  « Dimensions pas encore mesurables » est rendu **deux fois** — une carte
  d'item `Info`, puis une carte de limitations. Défaut préexistant, hors
  périmètre de cette tranche, signalé plutôt que corrigé au passage ;
* **`.pd-*` porte un nom qui ne dit plus ce qu'il couvre.** Assumé et écrit
  dans la feuille, plutôt que corrigé par un renommage qui toucherait cinq
  gabarits sans rien changer au rendu.
