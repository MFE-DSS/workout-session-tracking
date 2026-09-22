# `UI-CP6 SHELL` — rapport macro

> **Arbitrage opérateur clos** : réduire le chrome persistant, retirer la
> duplication, formaliser le comportement contextuel de la coque.
> **Ce n'est pas une refonte de navigation.** Les quatre destinations
> primaires sont acceptées et intouchées.

---

## 1. AVANT / APRÈS — mesuré, pas estimé

Sur le compte de labo `pilote` (21 séances), aux cinq viewports du `§11`.

### Chrome persistant

| | AVANT | APRÈS |
|---|---|---|
| topbar mobile | **69 px** | **45 px** (44 + 1 px de filet) |
| pied sur un instrument | **135 px** (mobile) / 79 (desktop) | **0** |
| chrome total, instrument mobile | **126 px** | **102 px** |
| coût vertical desktop | 0 px | **0 px** *(acquis préservé)* |

### Premier viewport utilisable, instrument

| viewport | AVANT | APRÈS | gain |
|---|---|---|---|
| 390 × 844 | 718 px | **742 px** | +24 |
| 390 × 667 | 541 px | **565 px** | +24 |
| **844 × 390** (paysage) | 264 px | **288 px** | +24 |
| 768 × 1024 | 898 px | **922 px** | +24 |
| 1024 × 768 | 768 px | 768 px | — |

### Défilement avant la réponse souveraine — la preuve par la TÂCHE

Le `§11` demandait explicitement des **preuves de tâche** plutôt que des quotas
de pourcentage. Voici la tâche : *le chrome force-t-il à défiler avant la
réponse souveraine ?*

| surface · viewport | AVANT | APRÈS |
|---|---|---|
| `/progress` · 390 × 844 | 0 | **0** |
| `/progress` · 390 × 667 | 0 | **0** |
| **`/progress` · 844 × 390** | **127 px** | **79 px** |
| `/` · 390 × 844 | 0 | **0** |
| **`/` · 390 × 667** | **32 px** | **0** |
| **`/` · 844 × 390** | **172 px** | **124 px** |

⚠ **LE PAYSAGE RESTE IMPARFAIT, ET JE NE LE MASQUE PAS.** À 844 × 390, le
chrome pèse encore 102 px sur 390 — **26 %** — et il reste 79 px de défilement
avant la réponse de `/progress`. C'est la **conséquence directe de
l'arbitrage** : `Q1` a tranché « garder la topbar et la réduire », et la barre
basse porte les destinations primaires. 45 + 57 = 102 px est donc le plancher
que les décisions rendues impliquent. Le corriger davantage exigerait de
masquer une structure en paysage — un comportement que personne n'a arbitré, et
que je n'invente pas.

---

## 2. Les quatre modes de coque

`app/services/shell.py` — module **pur**, ni `sqlalchemy`, ni `datetime`, ni
`request`, garde à l'appui.

| mode | topbar | nav primaire | pied |
|---|---|---|---|
| `INSTRUMENT` | 44 px | oui | **non** |
| `FOCUS` | **non** | **non** | **non** |
| `DOCUMENT` | 44 px | oui | oui *(temporaire, jusqu'à `UI-CP7`)* |
| `GUEST` | **non** | **non** | **non** |

### La précédence est une décision, et elle est épinglée

```
GUEST  >  FOCUS  >  DOCUMENT  >  INSTRUMENT
```

Elle est vérifiée **dans une seule assertion** qui énumère aussi les modes :
réordonner force à toucher la ligne qui l'énonce, au lieu de la changer en
déplaçant un `if`. C'est le dispositif de `PRECEDENCE_VERSION` de
`flight_recorder`, réemployé.

`GUEST` prime sur tout : une surface de seuil ne reçoit jamais le cockpit, quel
que soit l'état par ailleurs. `INSTRUMENT` est le défaut parce que se tromper
dans ce sens rend une coque **complète**, jamais une coque vide.

### Ce que les deux drapeaux précédents ne tenaient pas

Ils sont remplacés par un seul mode, et **aucun des deux ne couvrait son
intention** :

* `shell_focus_mode` masquait la barre basse pendant une séance active, et
  laissait la topbar (69 px) **et** le pied (79 px) ;
* `shell_bare` disait « seuil » et ne retirait que le pied et la barre basse.

Un drapeau qui ne couvre pas son intention n'est pas un drapeau : c'est une
coïncidence qui tient tant que personne ne regarde.

`shell_focus_mode` **survit**, dérivé du mode : la classe
`is-session-focus-mode` du `<body>` est une garantie de style épinglée par une
garde existante, et elle n'avait aucune raison de bouger. Ce qui change est ce
qui la produit.

---

## 3. `FOCUS` — l'exécution possède l'écran

La décision produit majeure de la tranche.

| viewport | chrome global AVANT | chrome global APRÈS | viewport utilisable |
|---|---|---|---|
| 390 × 844 | topbar 69 + pied 79 | **0** | **844 px** |
| 390 × 667 | topbar 69 + pied 79 | **0** | **667 px** |
| 844 × 390 | topbar 69 + pied 79 | **0** | **390 px** |
| 1024 × 768 | rail + pied 79 | **0** | **768 px** |

Le rail desktop disparaît lui aussi : l'exécution possède l'écran **aux deux
ruptures**, pas seulement sur mobile.

### La sortie — explicite, découvrable, réversible

`§7` : *« do not trap the user »*. Mesuré au rendu, aux quatre viewports :

```
← (retour à l'accueil)   y = 26 px   hauteur 44 px   visible sans défiler
```

Elle vit dans l'en-tête collant de la séance
(`_partials/session_focus_header.html`), **existait déjà**, et porte
`aria-label="Retour à l'accueil"`.

⚠ **SON LIBELLÉ VISIBLE RESTE UNE FLÈCHE, ET C'EST UN ARBITRAGE QUE JE SIGNALE
PLUTÔT QUE DE LE TRANCHER SEUL.** J'ai envisagé d'ajouter le mot « Accueil ».
L'en-tête est une grille de quatre colonnes — `44px | 199px | 47px | 44px` sur
un viewport de 390 — et la sortie occupe la colonne fixe de 44. Ajouter un mot
prendrait de la largeur au **nom de la séance**, sur l'instrument dont la
question souveraine est « que fais-je maintenant ». J'ai donc gardé la flèche :
elle est conventionnelle, conforme au plancher tactile, au-dessus de la ligne
de flottaison partout, et nommée pour les aides techniques.

---

## 4. `GUEST` — la fuite mesurée, et fermée

**AVANT**, `/forgot-password` exposait la coque authentifiée :

| viewport | destinations authentifiées visibles |
|---|---|
| 390 × 844 | **8** — `/`, `/plan`, `/history`, `/coach-report`, `/export`, `/squads`, `/leaderboard`, `/contact` |
| 1024 × 768 | **11** — les précédentes **plus** `/library`, `/progress`, `/profile` |

Et c'était **le seul gabarit du dépôt qui posait `shell_bare`** — ce qui rendait
le défaut invisible à la relecture : le drapeau avait l'air posé, donc le
travail avait l'air fait.

**APRÈS** : `0` destination authentifiée, sur `/login` **et**
`/forgot-password`, aux deux ruptures.

`login` et `register` échappaient au défaut **par accident** : ce sont des
gabarits autonomes qui n'étendent pas `base.html`. Ils figurent quand même dans
`CHEMINS_INVITE` — le jour où l'un rejoindra la coque, il sera déjà classé.

---

## 5. `DOCUMENT` — classé, pas redessiné

`/science`, `/atlas`, `/coach-report`, `/coach-body-snapshot`, `/export` sont
désormais **classés** `DOCUMENT`, conformément à `AUREN_INSTRUMENTS §2bis`.

`UI-CP6` ne fait que les classer. Leur pied de page est **conservé
temporairement**, sur instruction explicite : leur transformation appartient à
`UI-CP7 REFERENCE`.

⚠ La borne de préfixe est le `/`, pas un `startswith` nu : `/exportateur` n'est
pas sous `/export`. Une garde le vérifie — sans elle, une surface voisine
perdrait sa navigation primaire en silence.

---

## 6. `SECONDARY_NAV` — un contrat, deux rendus

L'arbitrage `Q4` interdisait de supposer qu'un partiel HTML partagé est la
bonne abstraction. Architecture livrée :

```
NAVIGATION_SECONDAIRE  (contrat sémantique, app/services/shell.py)
        ├─▶  rendu MOBILE   (.topbar__nav,  classes topbar__link)
        └─▶  rendu DESKTOP  (.app-rail__secondary-nav, classes app-rail__sublink)
```

Le balisage diffère ; la **sémantique** ne peut pas diverger.

Chaque destination est décrite par un `id` stable, une `route`, un `libelle` et
le **nom** du drapeau qui la souligne. Aucun champ ne porte de classe CSS ni de
position — c'est ce qui permet aux deux rendus de différer.

### La garde qui n'existait pas

Les six liens étaient **écrits deux fois** dans `base.html`, et les deux blocs
ne sont **jamais rendus en même temps** : l'un est masqué par media query.
**Aucun test de page ne pouvait les comparer**, et `UI-CP4` a dû éditer les
deux à la main. C'était le mode d'échec « famille aux deux tiers », déjà armé.

Le HTML **servi** contient pourtant les deux. La garde les compare là, sans
navigateur — donc insensible à la rupture de 1024 px. Elle vérifie **l'ordre**,
pas seulement l'ensemble : deux rendus proposant les mêmes destinations dans
deux ordres différents apprendraient deux produits à la même personne.

Vérifié au rendu : ensembles identiques, ordre identique.

### L'exception de placement, encodée

`CONTACT` vit dans le menu sur mobile et en pied de rail sur desktop. `Q4`
autorise ces exceptions **« à condition qu'elles soient encodées et testées »** :
elle l'est — `CONTACT` est hors de la liste ordonnée mais dans
`DESTINATIONS_ATTENDUES`, et une garde vérifie exactement cela. Une exception
qui ne vivrait que dans un commentaire ne serait pas encodée.

### Le risque résiduel, nommé et gardé

Le contrat porte le **nom** du drapeau, `base.html` porte sa **valeur** — parce
que remonter le mapping `is_*` en Python aurait reconstruit toute l'IA, ce que
le `§12` interdit. Le risque est qu'une clé manque dans la table du gabarit :
la destination serait rendue mais **jamais soulignée**, un défaut silencieux
invisible à toute garde statique. Une garde de **rendu** visite chaque route du
contrat et exige le soulignement.

---

## 7. `Q2` — `IDENTITY_HOME_EXCEPTION`

Le mot-marque « Auren » reste un lien vers `/`, alors que l'onglet « Séance » y
mène aussi. L'exception est **inscrite dans le gabarit**, aux deux endroits qui
la portent, avec sa raison : l'identité de produit sert l'**orientation** et
l'échappée vers l'accueil, elle n'est pas une tuile de navigation concurrente.

⚠ **Elle nomme explicitement l'instruction de ne pas retirer ce lien dans une
passe de déduplication future.** Sans cette phrase, la règle « pas deux chemins
vers la même destination » — vraie et appliquée par `UI-CP3` et `UI-CP4` —
reviendrait le supprimer, et personne ne saurait pourquoi il était là.

---

## 8. `§10` — la rupture 1024, testée et conservée

L'arbitrage interdisait de la changer à l'intuition et demandait de la
**tester**. Mesuré sur neuf largeurs :

```
390 · 600 · 768 · 900 · 1000 · 1023  →  topbar 45 + barre basse 57, rail absent
1024 · 1025 · 1280                   →  rail seul, chrome vertical 0
```

**Exactement une structure à chaque largeur** : jamais les deux, jamais aucune.
Aucun débordement horizontal. Bascule nette à 1024.

**Aucun défaut de tâche ni de mise en page prouvé → la rupture est CONSERVÉE.**

---

## 9. `§12` — les acquis, préservés et gardés

| Acquis | Vérifié |
|---|---|
| Quatre destinations primaires, exposées une seule fois | garde de compte + unicité |
| Un seul `aria-current` par structure | garde, barre basse **et** rail |
| Rail desktop, zéro coût vertical | garde de présence + mesure |
| SSR, aucune dépendance JS | garde : ni `<script>` ni gestionnaire en ligne dans la coque |
| Divulgation native | `<details>` conservé |

⚠ **MA PREMIÈRE GARDE `aria-current` COMPTAIT LE DOCUMENT ET RENDAIT 2.** La
barre basse et le rail le portent chacun ; ils coexistent dans le HTML et
s'excluent par media query, donc un utilisateur n'en voit jamais qu'un. Elle
accusait le produit d'un défaut d'accessibilité **qui n'existe pas**. Corrigée :
un `aria-current` **par structure**.

---

## 10. Les gardes — 19, dont quatre vérifiées par mutation

Le défaut replanté est celui d'**origine**, pas une caricature : une coque qui
ignore le mode `GUEST` et dont `FOCUS` ne retire que la barre basse.

| Garde | Rouge sous mutation |
|---|---|
| aucune destination authentifiée ne fuit sur un seuil | ✔ |
| la séance active retire **tout** le chrome global | ✔ |
| aucun pied générique sur une surface d'instrument | ✔ |
| les deux rendus proposent les mêmes destinations dans le même ordre | ✔ *(divergence plantée dans le gabarit, annulée aussitôt)* |

### Deux gardes existantes repointées — de l'ÉCRITURE vers la PROPRIÉTÉ

| Garde | Ce qu'elle épinglait | Ce qu'elle vérifie désormais |
|---|---|---|
| `test_footer_shows_auren` | `<small>Auren</small>` dans le pied de **l'accueil** | le pied nomme le produit **là où il subsiste** (document), et le mot-marque le nomme sur un instrument |
| `test_the_shell_names_the_children_without_duplicating_them` | des libellés **littéraux** dans la SOURCE de `base.html` | les mêmes libellés dans le HTML **servi**, qui contient les deux rendus |

⚠ **LA SECONDE SERAIT DEVENUE PIRE QUE FAUSSE SI ELLE ÉTAIT PASSÉE PAR
ACCIDENT.** Elle compte des libellés dans la source ; `UI-CP6` les remplace par
`{{ d.libelle }}`. Son `count(...) == 1` est tombé — tant mieux. Mais ses
`count(...) == 0`, eux, seraient passés tout seuls sur une source qui ne
contient plus aucun libellé : la moitié de la garde se serait désarmée en
silence. Repointée sur le rendu, elle est **plus stricte qu'avant** — elle voit
ce que le gabarit produit, pas ce qu'il a l'air de produire.

### Deux de mes propres gardes étaient fausses, et le produit avait raison

1. **`/login` « fuyait » une topbar.** La fixture `client` est authentifiée :
   `/login` renvoie alors une redirection, et `follow_redirects=True` rendait
   le HTML de **l'accueil**. La garde mesurait une autre page que celle
   qu'elle nommait. Corrigée : déconnexion d'abord, et vérification que le
   statut est bien `200`.
2. **`aria-current` compté sur le document** — voir `§9`.

*Les deux relèvent de la même classe : mesurer le mauvais objet. C'est la
raison pour laquelle aucune accusation n'est publiée ici sans avoir été
vérifiée à la main d'abord.*

---

## 11. Portail visuel `§15`

Six rendus produits et soumis à l'opérateur **avant** ce commit, au **premier
écran** plutôt qu'en pleine page — ce que la tranche change est le budget de
chrome, et il ne se juge qu'au premier regard :

`instrument mobile` · `instrument court 390×667` · `FOCUS séance active` ·
`instrument desktop` · `document` · `invité`.

---

## 12. Périmètre — ce qui n'a PAS été touché

Conformément aux `§12` et `§13` :

* les quatre destinations primaires — noms, ordre, routes, iconographie ;
* la rupture 1024 px (testée, conservée) ;
* l'information architecture ;
* les surfaces de document elles-mêmes (`UI-CP7`) ;
* aucune route supprimée ni renommée ;
* aucun JavaScript introduit.

---

## 13. Contrôles

| Contrôle | Résultat |
|---|---|
| `check_scope.py` | **`SHARED_CODE`** |
| `ruff` (fichiers neufs) | **vert** |
| `check_ruff_budget.py` | **266 / 548** |
| `check_spec_protocol.py` | **vert** |
| pré-scan `S9073` | une assertion composite de ma main, **corrigée** |
| sweep local complet, arbre **gelé** | *(voir l'avenant)* |

⚠ Une finding `external_ruff:UP017` subsiste dans `app/templating.py` sur une
ligne **pré-existante** que mon diff n'a pas touchée — vérifié au `git diff`.
Je ne l'ai pas corrigée : élargir le diff pour une coquetterie de lint hors
périmètre est de la dérive, et le budget confirme l'absence de régression.

---

## 14. Suite de la voie critique

`UI-CP7 REFERENCE`, puis `UI-CP8 UTILITY + LIFECYCLE`, puis
`UI-CP9 SQUAD / SOCIAL ARBITRATION`.

**Ne pas avancer automatiquement.**

---

## AVENANT POST-MERGE — closeout

**Mergée le 2026-09-22.** PR **#241**, méthode `--merge` avec SHA de tête
épinglé (`15c9329`), commit de merge **`81f9c01`**. Aucun squash, aucun
`--admin`, aucun force.

### Les six portes, revérifiées juste avant le merge

| Porte | État |
|---|---|
| SHA de tête connu et inchangé | `15c93290f2d7933acbc5e9d7622c88de09bc6199` |
| Tous les contrôles requis | **10/10 pass**, dont le gate **externe** `SonarCloud Code Analysis` |
| Gate Sonar, par API | **`status: OK`**, 5/5 conditions |
| Threads de revue non résolus | **0** |
| `mergeable` / `mergeStateStatus` | `MERGEABLE` / `CLEAN` |
| Dérive de périmètre | aucune |

### CI canonique sur le commit de merge — la source de vérité

Run **35738241348**, `conclusion: success`, **7/7** :
`canonical attestation` · `lint` · `pytest shard 1/2/3` · `pytest + QA scripts`
· `SonarCloud`.

### Qualité du nouveau code

| Condition | Valeur | Seuil |
|---|---|---|
| `new_coverage` | **100,0 %** | ≥ 80 |
| `new_duplicated_lines_density` | **0,0 %** | ≤ 3 |
| `new_bugs_severity` | **0** | ≤ 9 |
| `new_code_smells_severity` | **0** | ≤ 14 |
| `new_vulnerabilities_severity` | **0** | ≤ 9 |

**Aucune finding Sonar au premier passage**, contrairement à `UI-CP5`. La
différence tient à une seule chose : la liste ruff a été **dérivée de
`git diff --name-only`** au lieu d'être écrite à la main. C'est exactement la
faute qui avait coûté un cycle sur la tranche précédente.

### ⚠ Un défaut de cette tranche, trouvé en ouvrant la suivante

`PREFIXES_DOCUMENT` contenait **deux préfixes qui ne désignent aucune route** :
`/atlas` (l'atlas vit à `/science/atlas`) et `/coach-body-snapshot` (c'est un
**partiel** inclus dans `coach_report.html`, pas une page).

**Cause** : `AUREN_INSTRUMENTS §2bis` nomme des **surfaces** — « coach_report +
coach_body_snapshot », « atlas » — et j'en avais fait des **chemins d'URL**.

Inoffensif à l'exécution — un préfixe qui ne matche rien ne classe rien — mais
**ma propre garde l'assertait à vide** : « `/atlas` est un DOCUMENT » passait
sans que `/atlas` existe. C'est la forme la plus coûteuse d'un faux vert :
celle qui *a l'air* de protéger.

Trouvé en interrogeant `app.routes` plutôt qu'en relisant mon propre code.
Corrigé en **PR #242**, avec une garde qui ferme la classe.

⚠ **Et cette garde a échoué sur la CI à son premier passage**, en annonçant que
`/coach-report` ne désignait aucune route — ce qui est faux. La cause est le
harnais, pas le produit : le `conftest` retire tous les modules `app.*` de
`sys.modules` à chaque fixture `client`, et la CI exécute sous `xdist`. Un
`from app.main import app` écrit à nu récupère ce que le worker a laissé
derrière lui. **Je n'ai pas prouvé l'état exact du module sur ce worker et je
ne le prétends pas** — ce que je sais suffit : une garde ne doit pas dépendre
d'un état d'import que le harnais manipule. Elle prend désormais l'application
de la fixture, ce qui supprime la dépendance au lieu de la contourner.

*Troisième garde de ma main, en deux tranches, à mesurer le mauvais objet. Ici
l'objet mesuré était une application à moitié assemblée.*

### Ce que cette tranche laisse derrière elle

* le **paysage** reste à 79 px de défilement avant la réponse souveraine —
  conséquence assumée de l'arbitrage `Q1`, pas un oubli ;
* la **sortie de `FOCUS`** reste une flèche nue, avec sa raison mesurée ;
* une finding `external_ruff:UP017` **pré-existante** dans `app/templating.py`,
  hors du nouveau code.

**Déploiement en production : non fait dans ce closeout.** Décision séparée.
