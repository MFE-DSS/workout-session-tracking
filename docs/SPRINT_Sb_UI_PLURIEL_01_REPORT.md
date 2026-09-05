# `Sb_UI_PLURIEL_01` — la règle que le produit connaissait sans l'avoir écrite

## 1. Le constat

Dix-huit endroits écrivaient `séance{% if n > 1 %}s{% endif %}` **correctement**.
Neuf autres, dans trois gabarits, écrivaient `séance(s)` — la parenthèse qui
économise la condition en abîmant la phrase.

| Gabarit | Occurrences |
|---|---|
| `user_programs/publish.html` | 4 (`séance(s)`, `modèle(s)`, `lançable(s)`, `exercice(s)`) |
| `_partials/body_intelligence_block.html` | 3 |
| `_partials/home_coaching_loop.html` | 2 (`séance(s) proposée(s)`) |

La règle était **connue** du produit — dix-huit fois — mais **écrite nulle
part** : seulement répétée. Une règle répétée et jamais nommée dérive, et elle
a dérivé neuf fois.

C'est mot pour mot le constat que `date_fr` a inscrit dans `templating.py` ce
matin : *les pièces existaient, aucune n'était **atteignable** depuis un
gabarit sans les connaître.*

## 2. Brainstorming · options · risques · choix retenu

### Option 1 — convertir les 9 vers la forme Jinja en ligne

**Écartée.** Vingt-sept répétitions d'un motif verbeux au lieu de dix-huit, et
la vingt-huitième dérivera pour la même raison que les neuf premières.

### Option 2 — un filtre `pluriel`, pour les 9 seulement

**Écartée.** Deux conventions coexistantes, c'est précisément ce qui a produit
la dérive.

### Option 3 — un filtre, les 9 corrigés, une garde qui interdit la parenthèse

**✅ Retenue.** Les 18 endroits corrects ne sont **pas** touchés : ce serait un
refactor sans gain, et un diff plus large pour zéro défaut réparé. La garde,
elle, empêche la parenthèse de revenir — c'est ce qui rend le choix durable
sans toucher l'existant.

### Le risque, et comment il est traité

**Un filtre qui devine.** Ajouter un `s` est faux pour « cheval », « travail »,
« bijou ». Un filtre qui se trompe est **pire** qu'une condition en ligne : il
a l'air d'avoir décidé, et personne ne relit un pluriel.

Le filtre **lève** donc sur une terminaison ambiguë. Il refuse la **classe de
terminaison** plutôt que de maintenir la liste exacte des exceptions
françaises — celle-ci serait une dette pour un gain nul, le produit pluralisant
onze mots, tous réguliers.

## 3. Ce qu'une phrase entière impose, et que le filtre ne fait pas

La première écriture de `publish.html:21` a produit **huit appels de filtre**
pour une seule phrase :

```jinja
Ses {{ n }} {{ "séance"|pluriel(n) }} {{ "est" if n <= 1 else "sont" }}
{{ "disponible"|pluriel(n) }} comme {{ "modèle"|pluriel(n) }} …
```

Illisible, et pire que l'original. **En français l'accord touche le verbe et
les participes autant que le nom.** Le filtre sert un **nom isolé** ; une phrase
qui s'accorde en entier s'écrit **deux fois**, sous un `{% if %}`. C'est ce qui
est livré.

## 4. Trois trouvailles, trois mécanismes différents

### `travail` — trouvé par une PLANTATION

Ma liste de terminaisons contenait `al` mais pas `ail`. `travail` ne finit pas
par « al » : le filtre rendait **« travails »** en silence.

**La garde censée l'attraper était verte.** `test_every_word_the_product_pluralises_is_regular`
scanne les mots passés au filtre dans les gabarits et vérifie qu'aucun ne lève
— mais elle interroge le filtre, et le filtre se trompait. Une garde qui
délègue son jugement à ce qu'elle teste ne teste rien. C'est une variante de
plus du relevé `guards-that-guard-nothing`.

### `pneu` — trouvé en corrigeant la précédente

Mon propre test rangeait `pneu` parmi les mots « impossibles à former ».
`pneu` → `pneus` est **régulier**. Le filtre le refuse quand même, et c'est le
bon côté pour se tromper : sur-refuser coûte un pluriel écrit à la main ;
sous-refuser coûte « travails » en production. Le test dit désormais cela, au
lieu de prétendre que le mot est irrégulier.

### `2\n      modèles` — trouvé par le SWEEP

J'avais replié les expressions Jinja sur plusieurs lignes. Le rendu visuel est
identique — l'espace HTML se réduit — mais le texte **servi** contenait
`2\n      modèles`, et `test_get_publish_validated_shows_summary`, qui vérifie
`"2 modèle" in r.text`, a rougi.

Un défaut **invisible à l'écran et visible dans la réponse**. Le test est sain ;
c'est ma mise en forme qui cassait. Les expressions sont désormais sur une
ligne, avec la raison en commentaire dans le gabarit.

## 5. Relecture du relevé de décisions (`CLAUDE.md §5.2`)

`docs/DESIGN_DECISIONS_UIV2_SURFACES.md` :

| Décision | Verdict |
|---|---|
| **Q1** connexion · **Q2** ancre d'accueil · **Q3** état du jour | non concernées |
| **Q4** « les valeurs deviennent l'objet, le texte recule » | **respectée** — `4 séance(s) proposée(s)` portait deux parenthèses de bruit autour d'un nombre |
| **Q5** trois rangs de surface | non concernée — aucun conteneur n'est touché |
| Tokens bleus · interdit du feu tricolore | non concernés |

## 6. Vérifications

`check_scope` **SHARED_CODE** · budget ruff **267 / 548** ·
`check_spec_protocol` **OK** · gardes de la tranche **7 vertes**,
3 plantations vérifiées · sweep ciblé **1 064 tests verts**.

Rendu exposé (`CLAUDE.md §5.1`) sur `/` et `/body/intelligence`, avec le cas
qui prouve le seuil français : **« 0 séance »** au singulier. Un seuil anglais
(`!= 1`) aurait rendu « 0 séances ».

⚠ `app/templating.py:34` porte un `UP017` **préexistant** (`timezone.utc` →
`datetime.UTC`), dans `to_local`, hors du diff. Il n'entre donc pas dans le code
neuf de Sonar. Non corrigé ici : ce serait une dérive de périmètre.

## 7. Trouvaille hors périmètre

Sur `/body/intelligence`, les zones sont rendues avec leurs **clés anglaises
brutes** — `pecs`, `shoulders`, `arms`, `lower`, `back_thickness`,
`back_width` — dans une interface française. Même famille que les jours de la
semaine en anglais corrigés par `Sb_UI_HISTORIQUE_01`.

Surface derrière `body_intelligence_enabled`, **éteint par défaut**. Signalée,
non traitée.

## Verdict

**LIVRÉ.** Les neuf pluriels entre parenthèses ont disparu, la règle est portée
par un filtre nommé et atteignable, et une garde interdit à la parenthèse de
revenir. Le filtre refuse ce dont il n'est pas sûr plutôt que de rendre une
faute que personne ne relit.

**Ce qui reste ouvert** — les dix-huit endroits qui pluralisent correctement en
Jinja en ligne. Ils ne sont pas touchés : les convertir serait un refactor sans
défaut réparé. Ils pourront migrer au fil des tranches qui les rencontrent.
