# `Sb_UI_SECTION_RANK_01` — le titre de section cesse d'être plus petit que son contenu

Une ligne de CSS, **onze gabarits**. C'est le point : la tranche existe parce
que la corriger sur une seule surface aurait fabriqué un défaut connu.

## 1. Le constat, mesuré

`AUREN_VISUAL_BACKBONE §3.2` nomme ce défaut depuis sa rédaction :

> body 14 px, section-header 13 px … sur 101 usages

Il est resté ouvert parce qu'il n'appartient à aucun écran. Je l'ai rencontré
en mesurant la bibliothèque :

| Rôle sur `/library` | Taille |
|---|---|
| **titre de section** (`SÉANCES PRINCIPALES`) | **13 px** |
| nom de séance | 16 px |
| accroche de page | 14 px |

Le titre de bloc était plus petit que le contenu qu'il introduit **et** que la
prose qui le précède. Un titre qui ne domine rien ne hiérarchise rien : il
ajoute du texte.

## 2. Brainstorming · options · risques · choix (`CLAUDE.md §3`)

`.section-header` vit sur **onze gabarits** : `science` · `atlas` · `profile` ·
`progress` · `template_detail` · `welcome` · `library` · `dashboard` ·
`user_programs/plan` · `_partials/progression` · `_partials/zone_exposure`.

| Option | Ce qu'elle fait | Pourquoi non / oui |
|---|---|---|
| **A — scoper à la bibliothèque** (`.library .section-header`) | 1 surface corrigée, 10 laissées | **Rejetée.** C'est littéralement le défaut consigné : *une décision appliquée là où c'était commode*. Trois exemplaires en une nuit ont déjà été relevés. Le remède écrit est de **balayer la classe**, jamais l'écran |
| **B — promouvoir la classe** | 11 surfaces d'un coup | **Retenue.** Le rang SECTION est déjà arbitré (échelle E3 : 32 / 22 / 15 / 12) et déjà appliqué à l'accueil et au récap. Ici il n'y a rien à trancher, seulement à propager |
| **C — attendre l'arbitrage écran par écran** | 0 surface corrigée | Rejetée : onze arbitrages pour une décision **déjà prise**. C'est le mode d'échec « livrer d'abord ce qui est facile » du `§5.5`, à l'envers |

**Risque réel, et un seul** : à 22 px en capitales, un titre long passe à deux
lignes et casse le rythme des blocs. Ce n'est pas une hypothèse à débattre,
c'est une mesure à prendre — voir `§4`.

## 3. Ce qui change

```css
.section-header {
  font-size: 22px;      /* était 13px */
  letter-spacing: 0.3px; /* était 0.5px */
}
```

Le crénage descend avec la taille. 0,5 px tenait pour une capitale de 13 px ;
à 22 px il écarterait la ligne au-delà de sa lisibilité. La couleur reste
`--fg-muted` : à ce rang, la sourdine dit « structure », pas « contenu
secondaire ».

## 4. La mesure qui décide (`CLAUDE.md §5.1`)

Rendu réel, avant/après, sur les surfaces atteignables :

| Surface | Titres | Avant | Après | Sur 2 lignes |
|---|---|---|---|---|
| `/library` | 3 | 3,46 écrans | 3,50 | **0** |
| `/profile` | 2 | 1,42 | 1,44 | **0** |
| `/progress` | 4 | 3,05 | 3,10 | **0** |
| `/science` | 8 | 10,17 | 10,43 | **0** |

**17 titres, aucun passage à deux lignes.** Le risque identifié est mesuré à
zéro plutôt que supposé absent. Coût maximal : **+2,5 %** de hauteur sur la
page la plus longue du produit.

`/progress` est la surface qui montre le mieux ce qui était en jeu : trois
écrans de contenu qui n'avaient **aucune colonne vertébrale** en reçoivent une,
et le viseur souverain livré par `Sb_UI_PROGRESSION_LEAD_01` se range enfin
sous un titre de son rang.

Deux routes n'ont pas répondu (`/atlas` 404, `/programs/plan` 422) : ce sont
mes URL qui sont fausses, pas les pages. Elles portent la même classe et
héritent de la même promotion — **non vérifiées au rendu**, dit explicitement.

## 5. La garde épingle la relation, pas le nombre

`guards-that-guard-nothing` relève une forme précise : *une garde qui épingle
une ÉCRITURE au lieu d'une VALEUR interdit le réglage sans protéger
l'invariant*. Figer `font-size: 22px` aurait bloqué tout ajustement futur sans
rien garantir.

La garde compare donc **deux tailles lues dans la feuille** : le rang SECTION
doit dominer le corps. Passer à 20 px reste licite ; retomber sous 14 ne l'est
pas.

**Et la sonde a failli ne rien mesurer.** Premier jet : `^body\s*\{`. Il existe
**deux** règles `body` dans `app.css` — la vraie est `html, body { … }` ligne
459, et une seconde, ligne 4676, ne déclare qu'un `font-variant-numeric`. La
sonde lisait la seconde et concluait « pas de taille ». C'est le mode d'échec
« la garde ne regarde qu'un exemplaire d'une famille », attrapé au premier
lancement. Elle collecte désormais **tous** les blocs qui nomment le sélecteur
et retient celui que la cascade applique.

Trois gardes : la relation · aucune redéclaration ne repasse sous le corps ·
la classe est encore portée par au moins dix gabarits. Défaut d'origine planté
**en entier** (13 px sous 14 px) : **2 gardes mordent**, la garde-de-la-garde
reste verte comme prévu.

## 6. Relecture du relevé de décisions (`CLAUDE.md §5.2`)

| Décision | Verdict |
|---|---|
| **Q1** connexion · **Q2** ancre d'accueil · **Q3** état du jour | non concernées |
| **Q4** — « les valeurs deviennent l'objet, le texte recule » | **non concernée** : un titre de section n'est ni une valeur ni de la prose, c'est une charnière de structure |
| **Q4 amendement `DF-C`** | non concernée |
| **Q5** — trois rangs de surface | **respectée** : aucun conteneur ajouté ni retiré, aucun rang de surface déplacé |
| **Échelle E3** (32 / 22 / 15 / 12), arbitrée pour l'accueil | **appliquée, et c'est tout l'objet** — 22 px est son rang SECTION, repris à l'identique |
| Tokens · feu tricolore · une seule aplat ambre | non concernés — la tranche ne touche aucune couleur |
| **`§5.3` jamais une soustraction seule** | respectée : rien n'est retiré |
| **`§5.4` toute couleur est un token** | respectée : `--fg-muted` inchangé |
| **`§5.5` la centralité avant la facilité** | **c'est le motif de la tranche** — le défaut le plus cité du socle, corrigé en classe plutôt que sur la surface commode |

## 7. Vérifications

`check_scope` **SHARED_CODE** · broad sweep ciblé sur les onze surfaces :
**607 tests verts** (283 + 324) · gardes de la tranche **3 vertes**, plantation
du défaut d'origine vérifiée · ruff **OK**.

Rendu exposé (`§5.1`) avant et après sur quatre surfaces, tailles et
passages-à-la-ligne **mesurés**, pas jugés à l'œil.

## Verdict

**LIVRÉ.** Le défaut le plus cité du socle visuel — 101 usages — est fermé en
une ligne, sur les onze gabarits à la fois, avec une garde qui protège
l'invariant sans figer le réglage.

## 8. Ce qui reste ouvert, et qui n'est pas de cette tranche

* **Un second rang de titres de bloc** existe, plus petit, sur d'autres classes
  (`PAR PROGRAMME`, `QUALITÉ DES SÉANCES`, `POIDS CORPOREL` sur `/progress`).
  Il n'a pas été mesuré ; il mérite le même balayage de classe, pas un
  correctif au passage ;
* **`/atlas` et `/programs/plan`** — même classe, promotion héritée, rendu non
  vérifié faute d'URL correcte ;
* **les accents du catalogue** restent bloqués sur une décision opérateur. La
  bibliothèque montre deux cartes cardio voisines dont **une seule est
  accentuée** — « Cardio faible intensite » face à « marche inclinée ». La
  garde de `seed_reference_split` est un **test d'existence de version** :
  corriger le JSON **sans** bumper la version laisserait le fichier juste et
  l'écran faux. Le bump est donc inséparable du correctif, et sa conséquence
  mesurée — une séance cardio historique lue comme une séance de force — est
  décrite dans `SPRINT_Sb_UI_SESSION_DONE_01_REPORT.md §8` ;
* **l'échelle de la bibliothèque elle-même** (noms de carte à 16 px, `FORCE` /
  `CARDIO` à 11 px, treize boutons « Démarrer » identiques) : trois variantes
  rendues, en attente d'arbitrage.
