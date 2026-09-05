# `Sb_UI_PROGRESSION_SOVEREIGN_READOUT_01` — le relevé souverain de Progression

> Tranche du programme d'arbitrage UI mené par l'opérateur. Elle applique à
> `/progress` le patron d'instrument validé sur rendu le 2026-09-04
> (`AUREN_VISUAL_BACKBONE §4`), déjà transposé sur `Mon plan` (PR #198).

---

## 1. Le constat, mesuré

L'écran s'appelle **Progression**. Voici ses cinq plus grosses typographies,
relevées au rendu à 430 px :

| Ce que l'écran écrit | Taille | Ce que c'est |
|---|---|---|
| « 3 » (zones touchées) | **34 px** | un comptage |
| « 3 » (séances cette semaine) | 28 px | un comptage |
| « 10 » (séances terminées) | 28 px | un comptage |
| « 100 % » (work sets validés) | 28 px | un comptage |
| « 4 » | 28 px | un comptage |
| `Tirage front câble · 66 → 72` | **13 px** | **la progression** |
| `+6 kg` | **11 px** | **l'écart** — le plus petit texte de la page |

**Un rapport de 1 à 3, à l'envers.** Un écran nommé Progression écrivait la
progression dans son plus petit corps et les comptages dans son plus grand.

Aucune garde du dépôt ne pouvait le voir : ce n'est pas un défaut de valeur, ni
de contraste, ni de cible tactile. C'est un fait de **hiérarchie**, et la
hiérarchie ne se lit que dans les tailles comparées entre elles.

## 2. Ce que le produit avait déjà, et jetait

C'est la troisième fois dans ce programme, et le motif est stable : *le produit
ne manque presque jamais d'une décision — il manque du moyen de l'appliquer.*

**La décision d'ordre existait**, écrite dans le service :

> **Aucun tri par ampleur d'écart.** Classer par « plus gros progrès »
> reviendrait à décider que l'écart est un mérite ; l'ordre est celui de la
> pratique, qui n'affirme rien.
> — `build_progression_rows`

Donc `rows[0]` **est déjà** le mouvement le plus récent. L'écran avait l'ordre ;
il ne rendait simplement pas la position 1 autrement que la position 6.

**Les occurrences existaient aussi.** `KEEP_OCCURRENCES = 6` en retient six par
exercice ; `latest` et `previous` ne lisent que les index **0 et 1**. **Quatre
occurrences sur six étaient calculées, puis jetées avant la vue** — exactement
ce que `MaterializationReadiness` infligeait aux séances du plan hebdomadaire
la tranche précédente.

## 3. Brainstorming · options · risques · choix retenu

### Le point de départ imposé : le viseur intra-séance

| Viseur (une série) | Progression (ce que je suis devenu) |
|---|---|
| les puits `kg` / `reps` à 32 px | `23` et `10`, chacun son puits |
| la référence « la dernière fois » | `avant 24` / `avant 10`, en bleu système |
| la bande d'étapes `⁄2 —1 —2 —3` | la trace `30 · 29 · 26 · 25 · 24 · 23` |
| `3x 6-10` en support | `−1 kg` / `= reps` |
| le nom de l'objet + affordance de rang 2 | le nom de l'exercice, **qui est le lien** |

### Options soumises à l'opérateur, sur rendu réel

| | Forme | Verdict |
|---|---|---|
| **A** | un seul puits : `24 → 23` | écarté — les répétitions quittent le relevé |
| **B** | deux puits, sans trace | écarté — les 4 occurrences restent jetées |
| **C** | deux puits **+ la trace** | ✅ **retenu par l'opérateur** |

Et, séparément : les comptages sont **redescendus sous le relevé, taille
réduite** — ✅ retenu.

### Le risque principal, et pourquoi il ne se réalise pas

**Promouvoir un exercice, est-ce un jugement ?** Ce serait le cas si l'on
promouvait le « plus gros progrès ». Deux raisons de ne pas le faire, et la
seconde est dirimante :

1. le service l'interdit explicitement (cité au §2) ;
2. cela exigerait de comparer des **kilos entre exercices** — 6 kg au tirage
   vertical contre 1 kg au développé haltères — c'est-à-dire l'addition sans
   référent que la voie cardio refuse déjà entre deux machines.

`lead` est donc `rows[0]` : **le plus récent**. La chronologie n'affirme rien.

### Ce que la trace ajoute, énoncé comme un fait vérifiable

`−1 kg` décrit les deux dernières séances. Il est **identique** pour une décrue
régulière et pour un accident isolé. La trace les sépare. C'est une assertion,
pas une opinion — `test_the_trace_says_something_the_delta_cannot` la tient.

## 4. Le socle a corrigé ma maquette sur deux points

Lues **avant** d'écrire, comme la mémoire de projet l'exige, les règles
`§4.1`/`§4.2` du socle ont invalidé deux choix de mes maquettes :

* **la référence est en bleu système**, pas en gris. Le bleu dit la
  **provenance** ; distinguer « avant » de « maintenant » par une teinte de
  jugement aurait fait lire une charge allégée comme un échec ;
* **le rang 2 vit sur le titre** (règle 5), pas dans un bouton concurrent. Ma
  maquette posait « Les 6 occurrences → » sous les puits. Le titre **est** le
  lien.

Deux gardes fixent ces deux points, pour qu'ils ne se reperdent pas.

## 5. Relecture du relevé de décisions (`CLAUDE.md §5.2`)

`docs/DESIGN_DECISIONS_UIV2_SURFACES.md`, décision par décision :

| Décision | Verdict |
|---|---|
| **Q1** — la connexion porte l'identité | non concernée |
| **Q2** — ancre visuelle de l'accueil | non concernée |
| **Q3** — « État du jour » replié | non concernée |
| **Q4** — « les valeurs deviennent l'objet, le texte recule » | **respectée**, et c'est littéralement l'objet de la tranche |
| **Q4 amendement `DF-C`** — glyphes sur les lignes de série | non concernée (surface de séance) |
| **Q5** — trois rangs de surface | **respectée** : les puits sont des **plaques de niveau 3**, pas des cartes bordées. La carte reste au rang **actionnable** ; lire sa progression n'est pas agir |
| **Tokens bleus** — « origine système / information calculée » | **respectée**, avec une nuance assumée : `avant 24` est une performance enregistrée, pas une production du moteur. Le socle `§4.1`, plus récent et plus spécifique, assigne explicitement « la référence — la dernière fois » au bleu système, et il a été validé sur rendu. Je suis le document le plus spécifique, et je le signale |
| Interdiction du feu tricolore sur la récupération | **respectée** — aucune couleur de verdict n'est introduite |

Contrat de séance (`_partials/progression.html`) : aucun seuil, aucune tendance
nommée, aucune couleur de jugement. Les trois interdits tiennent.

## 6. Ce qui n'est PAS fait, et pourquoi

**Les sections ne sont pas réordonnées.** `EXPOSITION · 14 J` reste au-dessus de
`PROGRESSION PAR EXERCICE`. L'arbitrage portait sur la **taille** — « cessent
d'être les plus gros objets de l'écran », « le relevé devient le seul objet à
32 px » — et c'est ce qui est livré. Déplacer une section entière a ses propres
conséquences de lecture et mérite son propre arbitrage. **Signalé, pas fait.**

## 7. Une garde qui ne mordait pas

La première écriture de `test_no_count_reaches_the_rank_below_the_sovereign_readout`
demandait seulement `readout > comptage`. Le défaut d'origine replanté —
`.kpi-card__value` remis à 28 px — l'a laissée **verte** : 28 est bien inférieur
à 32.

Mais 28 contre 32 n'est pas une hiérarchie, c'est une égalité de fait à l'œil,
et c'est très exactement l'écran que la tranche corrige. Une garde qui
n'interdit que l'**inversion stricte** laisse revenir l'**écrasement**, qui
produit le même défaut.

Le seuil est désormais accroché au rang `SECTION` (22 px) de l'échelle
documentée, donc non négociable par un pixel.

**Six plantations, six morsures** — après réécriture :

| Plantation | Garde qui rougit |
|---|---|
| `.kpi-card__value` 20 → 28 px | rang du comptage |
| `.ze__n` 22 → 34 px | rang du comptage |
| `rows[1:]` → `rows[:]` | la ligne promue quitte la liste |
| `occurrences[:2]` dans la trace | trace complète · trace ≠ écart (2 gardes) |
| référence en gris | référence en bleu système |
| titre non cliquable | rang 2 sur le titre |

## 8. Vérifications

| Contrôle | Résultat |
|---|---|
| `check_scope.py` | **SHARED_CODE** |
| ruff (fichier touché) | `All checks passed` |
| budget ruff | **267 / 548** |
| `check_spec_protocol.py` | **OK** |
| gardes de surface + primitives | **35 vertes** |
| contrat `TRAIN1-B` existant | **30 vertes** |
| gardes neuves | **11 vertes**, 6 plantations vérifiées |
| broad sweep ciblé | *(voir appendice)* |

**Contraste mesuré au pixel sur le fond réel du puits `rgb(35,43,54)`** — pas
sur la valeur calculée d'un token, « calculé ≠ peint » ayant déjà trompé trois
fois dans ce programme :

| Couple | Mesure |
|---|---|
| valeur souveraine | **12,02:1** |
| référence bleue | **5,46:1** |
| unité · écart · trace | **4,64:1** |
| dernier segment de trace | **12,02:1** |

Aucune couleur neuve : uniquement des rôles déjà promus et mesurés.

## 9. Le labo était faux, et il l'était sur trois points

Le premier rendu de `/progress` montrait une section `PROGRESSION PAR EXERCICE`
**vide**, avec « 40 non rattachés », et deux graphiques parfaitement plats.
Aucun des trois n'était un défaut du produit :

1. `exercise_name_snapshot = code.replace("_", " ").title()` — un nom fabriqué,
   qu'aucun alias du catalogue ne rattache. Les 102 exercices du catalogue
   étaient là ; le labo ne s'en servait pas ;
2. `weight_kg = 40 + 5k + 2i` — **indépendant de la séance**. Toute progression
   valait zéro par construction ;
3. poids corporel et qualité constants → deux courbes plates.

C'eût été la **troisième fois** qu'un labo non représentatif me fait conclure
faux. Le labo a été resemé avec des noms réels et des charges qui bougent
**avant** de regarder l'écran.

## Verdict

**LIVRÉ.** Sur `/progress`, le relevé souverain (32 px) est désormais le seul
objet de son rang ; les comptages sont redescendus à 22 et 20 px, et la
progression — ce que l'écran nomme — a cessé d'être son plus petit texte.

Six occurrences sur six atteignent l'écran, contre deux auparavant. Aucun
seuil, aucune comparaison entre exercices, aucune couleur de jugement : les
trois interdits du contrat `TRAIN1-B` tiennent, et la promotion repose sur la
seule chronologie.

**Ce qui reste ouvert** — l'ordre des sections. `EXPOSITION · 14 J` précède
toujours `PROGRESSION PAR EXERCICE`. L'arbitrage opérateur portait sur la
taille ; déplacer une section a ses propres conséquences de lecture et attend
son propre arbitrage.
