# `Sb_UI_SCIENCE_ACCENTS_01` — la page qui explique le produit, en français

## 1. Le constat

`/science` est la page où AUREN explique sa méthode. Elle comptait **11 blocs
longs sur 20 sans un seul accent** — **345 mots sur 605** :

> La memoire subjective est un mauvais outil de progression. Elle surestime les
> bonnes seances, oublie les stagnations…

> Un carnet la remplace. La surcharge progressive suppose que tu saches ce que
> tu as fait la derniere fois.

> L'auto-illusion — croire qu'on progresse quand on stagne — est la premiere
> cause de stagnation reelle.

Contenu de **gabarit**, donc aucune migration ni re-seed : la correction est
possible sans toucher au catalogue versionné, qui porte le même défaut mais
dont le remède exige un bump de version et un wipe complet (arrêt dur).

## 2. Cinq occurrences ambiguës, pas soixante-trois

Un dépistage large sur les homographes — `la`/`là`, `des`/`dès`, `a`/`à`,
`du`/`dû`, `sur`/`sûr`, `ou`/`où` — en signalait **58**.

**Lues une par une, cinq seulement changeaient.** Les 53 autres sont des
articles, des pronoms ou le verbe *avoir*, qui ne prennent jamais d'accent.

| Phrase | Correction |
|---|---|
| « les jours **ou** tu n'as pas le temps » | `où` — pronom relatif |
| « la capacité **a** enchaîner » | `à` — préposition |
| « calculé automatiquement **a** partir » | `à` |
| « tu n'as pas **a** poser » | `à` |
| « comparer **a** la même séance » | `à` |

Chacune porte un commentaire à son endroit dans le gabarit, pour qu'un futur
passage ne la « corrige » pas à l'envers.

**Le relevé a été soumis à l'opérateur réduit à ces cinq**, pas aux 58 : lui
faire relire 53 non-problèmes aurait été du bruit déguisé en rigueur.

## 3. Ce qu'une garde peut et ne peut pas faire ici

**Elle ne peut pas exiger un accent par bloc.** Il reste un bloc long sans
aucun accent, et il est **correct** :

> Chaque niveau s'ouvre sur le suivant : un fait, l'instrument qui le porte,
> son inspection, et la provenance de l'attribution.

Pas un mot accentué en français. Une garde qui compterait les accents
accuserait cette phrase juste.

La garde tient donc une liste de **graphies fautives observées** — 36 entrées —
et interdit leur retour. Elle n'est pas exhaustive, et ne prétend pas l'être :
elle empêche la régression de ce qui a été corrigé.

**Les homographes en sont exclus.** `calcule` est le verbe (« AUREN calcule »),
`calculé` le participe : l'inclure ferait rougir la garde sur
`progress.html:186`, qui est correct.

## 4. Deux plantations — et la seconde vaut le fichier

| Plantation | Garde qui rougit |
|---|---|
| `mémoire` → `memoire` | `no_template_carries_an_unaccented_french_word`, avec la ligne |
| la sonde ne retire plus les balises | `the_probe_ignores_markup_not_prose` **et** 91 fausses accusations |

**La sonde lisait `<details>` comme le mot « détails ».** Sa première écriture
ne retirait pas les balises HTML : elle rendait **79 fautes dans 19 gabarits
qui n'en contenaient aucune**. Une garde qui lit du balisage comme de la prose
accuse tout le dépôt — et si elle avait été livrée ainsi, la première réaction
aurait été de la désarmer.

C'est le pendant du motif déjà relevé neuf fois ici (« la garde lit sa propre
prose »), pris par l'autre bout. `test_the_probe_ignores_markup_not_prose`
rend la récidive impossible en silence.

## 5. Deux tests épinglaient le défaut

`CLAUDE.md §4` interdit d'affaiblir un test pour verdir la CI. Ici, deux tests
**exigeaient la faute** :

| Test | Ce qu'il imposait |
|---|---|
| `test_science_page_has_materialisation_section` | « Comment Auren **materialise** » et « Ce qui reste **prive** » |
| `test_science_renders_auren_template_strings` | « Comment Auren **materialise** ces concepts » |

Leur **intention est saine** — la section doit apparaître, le nom du produit
doit être visible. Ce qu'ils gelaient, c'est l'orthographe qu'ils croisaient au
passage. Seules les chaînes attendues changent ; aucune assertion n'est retirée,
aucun test n'est affaibli, et chacun porte désormais la note qui explique
pourquoi.

C'est la **cinquième fois** que ce dépôt prend une garde à épingler un défaut
(forme 5 du relevé `guards-that-guard-nothing`).

## 6. Relecture du relevé de décisions (`CLAUDE.md §5.2`)

`docs/DESIGN_DECISIONS_UIV2_SURFACES.md` : **Q1** · **Q2** · **Q3** · **Q4** ·
**Q5** · tokens bleus · interdit du feu tricolore — **aucune n'est concernée**.
La tranche ne touche ni conteneur, ni couleur, ni hiérarchie, ni taille : elle
corrige l'orthographe d'un texte. Le relevé est relu en entier, et il ne dit
rien de ce cas.

## 7. Vérifications

`check_scope` **ISOLATED** · ruff **OK** · gardes de la tranche **4 vertes**,
2 plantations vérifiées · tests ciblés **283 verts** · broad sweep *(voir
appendice)*.

Rendu exposé (`§5.1`) : `/science` capturé sur **deux serveurs vivants**, la
canonique et la tranche.

**Mesuré** : blocs longs sans aucun accent **11 → 1**, et le bloc restant est
du français correct.

## Verdict

**LIVRÉ.** La page qui explique le produit est écrite en français. Les cinq
occurrences réellement ambiguës ont été tranchées une par une et documentées à
leur endroit ; une garde interdit le retour des 36 graphies corrigées, et une
seconde garde empêche cette garde de redevenir aveugle aux balises.

**Ce qui reste ouvert** — le **catalogue** (`data/reference_split.json` :
« Seance cardio sans abdos », « Cardio faible intensite ») porte le même
défaut. Le corriger exige un bump de version, qui déclenche un wipe-and-reseed
annulant `template_id` sur **toute séance historique**. C'est un arrêt dur
(`CLAUDE.md §4`, risque destructif de données) : signalé, non traité.
