# `UX4_02` / TRAIN 2 — tranche B : **Explorer**, le corpus commun contextualisé

`OPERATOR_DECISION` C8 · branche `sb/train2-explore-contextual` · base `c61424f`

---

## 1. Ce que cette tranche fait

Le catalogue montrait treize gabarits et une ligne de texte libre par gabarit.
Rien n'y reliait ce que l'utilisateur a **déclaré** à ce que chaque séance
**travaille**, et rien ne permettait de chercher par zone.

La tranche ajoute deux choses, et deux seulement :

1. **ce qu'un gabarit travaille** — les zones, résolues par l'autorité
   canonique, avec la marque de celles que l'utilisateur a déclarées en
   priorité ;
2. **un filtre par zone**, demandé par l'utilisateur, explicite dans l'URL, et
   dont on sort toujours d'un geste.

**Le corpus reste commun, entier et dans son ordre.** Rien n'est classé, noté,
masqué ni recommandé.

---

## 2. Brainstorming / Options / Risques / Choix retenu (`CLAUDE.md §3`)

### La contrainte, et pourquoi elle est difficile

> C8 : *« découverte CONTEXTUALISÉE sur un corpus commun de 13 gabarits,
> **aucun moteur de recommandation opaque**, contexte de plan explicite
> uniquement »*

Difficile parce que **rien dans le rendu ne signale qu'on a franchi la ligne**.
Un tri par pertinence, un gabarit relégué, un « recommandé pour toi » : la page
reste belle, les tests restent verts, et le produit s'est mis à décider à la
place de l'utilisateur.

### Ce qui a été MESURÉ avant de concevoir

Trois mesures ont décidé la conception, dans cet ordre :

| Mesure | Résultat | Conséquence |
|---|---|---|
| Le corpus est-il annotable de façon déterministe ? | **80 exercices sur 80 résolus en `DB_EXACT`** — 0 repli hérité, 0 non résolu ; **11 zones canoniques sur 11** couvertes | l'annotation est un **fait**, pas une heuristique → faisable |
| Que contient `focus` ? | texte libre : « Adducteurs », « Grand dorsal, largeur du dos », « Haut des pectoraux » — vocabulaire disjoint des zones | il ne peut **pas** servir de clé → l'appariement flou est écarté, comme C8 l'exige |
| Combien de zones sont « sous le volume visé » dans un plan réel ? | **7 des 11**, sur une déclaration de 4 séances | une étiquette « sous la cible » tomberait sur presque chaque carte → **écartée avant d'être écrite** |

La troisième mesure est celle qui a le plus servi : elle a supprimé une
fonctionnalité prévue **parce qu'elle n'aurait rien discriminé**. Un badge sur
douze cartes sur treize n'est pas un signal, c'est du décor.

### Options examinées

**Option A — annoter le corpus commun, filtrer sur demande.** *(retenue)*
Mêmes treize gabarits, même ordre. Chaque carte dit ce qu'elle travaille ; les
zones déclarées sont marquées ; un filtre par zone est offert, jamais appliqué
d'office.
· *Pour* : le corpus reste commun **par construction**, donc la ligne C8 ne
peut pas être franchie par accident. Le seul tri est celui que l'utilisateur
demande.
· *Contre* : la page s'alourdit — mesuré, voir §4.

**Option B — une section « pour toi » en tête du catalogue.**
· *Pour* : lisible immédiatement.
· *Contre* : c'est un **classement**, donc un jugement, donc exactement le
moteur que C8 interdit — même sans score affiché. Rejetée sans hésitation.

**Option C — annoter par les zones du PLAN plutôt que par la déclaration.**
Utiliser `assess_materialization(...).unmet_zones`.
· *Contre* : **mesuré non discriminant** (7 zones sur 11). Et le plan est un
objet dérivé : le rappeler ici demanderait de le reconstruire à chaque
affichage du catalogue (19 ms mesurés) pour un signal quasi constant. Rejetée
sur preuve.

### Risques identifiés avant d'écrire, et ce qui les couvre

| Risque | Couverture |
|---|---|
| Le corpus **rétrécit** silencieusement | garde : mêmes slugs avec et sans déclaration |
| Le corpus se **réordonne** | garde : l'ordre rendu == l'ordre catalogue (`display_order`, `slug`) |
| Une zone est **inventée** | garde : toute étiquette rendue appartient à `ZONE_LABELS` ; le service n'a pas le droit de lire `focus` |
| Une priorité est **devinée** | garde : aucune marque sans déclaration, et les marques ne dépassent pas l'axe déclaré |
| Le filtre devient une **décision du produit** | gardes : rien n'est filtré sans demande · la sortie existe et **ne mène pas à un filtre** · une valeur inconnue est ignorée |
| Le service se met à **noter** | garde structurelle sur le producteur : ni `sort`, ni `score`, ni `rank` dans le code exécutable |

### Choix retenu

**Option A**, avec la troisième étiquette supprimée sur preuve.

---

## 3. Ce qui a changé

| Fichier | Nature |
|---|---|
| `app/services/template_zone_context.py` | **neuf** — annotation zones + marque des priorités. N'ordonne pas, ne filtre pas, ne note pas |
| `app/routers/pages.py` | `/library` : annotation, filtre `?zone=`, axes déclarés |
| `app/templates/library.html` | repli de filtre, ligne d'état, légende, zones par carte |
| `app/static/css/app.css` | bloc `zone-filter` / `template-card__zone` — **aucune couleur neuve** |
| `tests/test_train2_explore_context.py` | **neuf** — 21 gardes |

---

## 4. Densité : le coût, mesuré et réduit

Le catalogue à 390 px, compte **vierge** / compte **déclaré** :

| État | Écrans | Mots |
|---|---|---|
| Avant la tranche (base `c61424f`) | 3,9 | 305 |
| Premier jet | 4,8 / **4,9** | 394 / **474** |
| Livré | 4,0 / **4,1** | 325 / **405** |
| Livré, filtré sur une zone | 1,9 / **2,0** | 114 / **164** |

Le premier jet coûtait **+1,0 écran**. Deux défauts vus **au rendu**, pas dans
les chiffres, expliquent la moitié de l'écart — et leur correction ramène le
coût à **+0,2 / +0,3 écran** pour l'information ajoutée.

### 4.1 — La ligne de zones DOUBLONNAIT le texte libre

Push A affichait `focus` = « Pectoraux, Deltoïdes, Triceps », puis, deux lignes
plus bas, « Pectoraux · Deltoïdes latéraux · Deltoïdes postérieurs · Triceps ».
La même chose deux fois, en deux vocabulaires, sur treize cartes.

La ligne de zones **remplace** désormais le texte libre quand elle existe. Ce
n'est pas une soustraction (`§5.3`) mais une **substitution dans la même
livraison** : la version résolue est plus précise, porte la marque des
priorités, et partage le vocabulaire du filtre — le texte libre ne peut rien de
tout cela. Il reste la seule source pour les gabarits **sans zone résolue** (le
LISS pur n'a aucun exercice) et **reste intact sur la page de détail**, où il
est éditorial et non redondant.

### 4.2 — Douze puces de filtre occupaient un écran entier

Déployées, elles poussaient le premier gabarit hors de vue. Un outil de tri qui
repousse ce qu'il sert à trier coûte plus qu'il ne rend. Elles sont repliées
derrière un `<details>` — et **le repli s'ouvre de lui-même quand un filtre est
actif**, sans quoi l'utilisateur verrait un catalogue amputé sans savoir
pourquoi.

### 4.3 — Deux défauts de rendu invisibles dans le gabarit

* **Le séparateur `·` devenait une puce.** Posé en `::before`, il partait en
  tête de ligne dès qu'une zone passait à la ligne suivante — en `flex-wrap`,
  l'élément emporte son pseudo-élément. Retiré : l'écart de grille sépare, et
  il ne se casse pas au retour à la ligne.
* **`display: flex` mangeait une espace.** Le résumé du repli rendait
  « Filtrer par zone**·** Dos largeur » : le nœud de texte et le `<b>` sont deux
  éléments flex, et l'espace du gabarit disparaît entre eux. Le HTML, lui,
  contenait bien l'espace — invisible à la relecture, évident à l'écran.

---

## 5. Gardes plantées

**14 défauts plantés, 14 gardes rouges.** Une garde qu'on n'a jamais vue rouge
ne garde rien.

| Défaut planté | Garde | Verdict |
|---|---|---|
| le corpus se réduit aux gabarits « pertinents » | corpus identique avec/sans déclaration | 🔴 |
| le corpus est classé par pertinence | ordre == ordre catalogue | 🔴 |
| le service se met à trier | garde structurelle sur le producteur | 🔴 |
| l'annotation vient du texte libre | zones canoniques / résolveur | 🔴 |
| les priorités sont supposées faute de déclaration | rien n'est marqué sans déclaration | 🔴 |
| la marque renvoie le mot de la ZONE | texte de rechange = l'axe déclaré | 🔴 |
| une zone bidon est acceptée | valeur inconnue ignorée | 🔴 |
| « Toutes » mène à un filtre | la sortie existe **et** ne filtre pas | 🔴 |
| le filtre actif est replié | le repli s'ouvre | 🔴 |
| le total disparaît de la ligne d'état | « N sur 13 » | 🔴 |
| les puces passent sous 44 px | standard tactile produit | 🔴 |

### Trois fautes d'instrument, toutes dans MES gardes

1. **Un préfixe de classe n'est pas un sélecteur.** Mon extracteur de cartes
   découpait sur `<li class="template-card`, qui attrape **aussi** les
   `template-card__zone` ajoutés par cette tranche même. Il rendait des
   fragments qui n'étaient pas des cartes.
2. **Une expression jusqu'au premier `</li>`** coupait la carte avant ses
   zones, puisque la liste de zones est **imbriquée**. Deux gardes passaient
   alors pour la mauvaise raison — l'une constatait l'absence du texte libre
   dans un fragment tronqué **avant** lui. Trouvé parce qu'une troisième garde,
   elle, a échoué.
3. **Mon harnais de plantation a rendu un faux « ROUGE ».** `pytest` sort avec
   le code 5 quand il ne collecte **rien** ; mon sélecteur `-k` était invalide,
   aucun test n'a tourné, et le harnais a compté ça comme une garde qui mord.
   Il détecte désormais explicitement le cas et l'affiche comme tel.

Et une garde trop faible, corrigée : la sortie du filtre cherchait la chaîne
« Toutes ». En pointant cette puce vers une zone, elle restait verte tout en
enfermant l'utilisateur dans le filtre. Elle vérifie maintenant la
**destination**.

---

## 6. Exposition §5.1 — rendus réels

360×800 · 390×844 · 430×932, comptes **déclaré** et **vierge**, et **trois
états** : catalogue entier, filtré sur une zone, et **URL bricolée**
(`?zone=pas_une_zone`) — un filtre dont on n'a pas regardé le cas dégradé n'est
pas exposé.

Sur les 18 rendus :

* **0 débordement horizontal** ;
* **0 cible tactile < 44 px** ;
* **0 liste de zones vide** ;
* **exactement une puce active** partout ;
* 13 cartes au catalogue, **3** sous `?zone=lats`, **13** sous une zone
  inconnue (valeur ignorée, jamais rendue) ;
* 40 zones affichées ; **10 marquées** sur le compte déclaré, **0** sur le
  compte vierge ; légende présente uniquement avec déclaration.

---

## 7. Relecture du relevé de décisions (`CLAUDE.md §5.2`)

`docs/DESIGN_DECISIONS_UIV2_SURFACES.md` :

| Décision | Verdict |
|---|---|
| **Q1** connexion / identité | non concernée |
| **Q2** ancre visuelle de l'accueil | non concernée |
| **Q3** « État du jour » replié | non concernée |
| **Q4** ligne de série instrument | non concernée |
| **Q5** surfaces, trois rangs | **respectée** — voir ci-dessous |
| **Tokens bleus** | respectée — **aucune couleur introduite** |
| Convergence Gravl → Auren | non concernée |
| Ordre de livraison | respectée — tranche B de C8, après la tranche A |

**Q5.** Le filtre est un objet **ambiant** : pas de conteneur, typographie et
espace seuls. La ligne d'état et la légende de même. Les zones vivent **dans**
la carte existante, sans en créer une nouvelle. Aucun conteneur n'a été ajouté
à cette surface.

**§5.4 — toute couleur est un token.** Aucune couleur n'est introduite. Les
quatre tokens réutilisés ont été **recalculés sur les fonds réels de cette
surface** plutôt que supposés :

| Paire | Ratio | Verdict |
|---|---|---|
| `--fg-muted` sur `--surface` | 7,96:1 | AA |
| `--fg-dim` sur `--surface` | 5,68:1 | AA |
| `--accent` sur `--surface` | 7,26:1 | AA |
| `--accent` sur `--bg` | 7,74:1 | AA |

La marque d'une priorité déclarée ne repose **pas sur la seule teinte** :
couleur **+** graisse **+** soulignement, plus un texte de rechange qui nomme
l'axe. Une marque perceptible d'une seule façon n'est pas perceptible.

**§5.3 — jamais une soustraction seule.** La seule chose retirée est la ligne
de texte libre, **remplacée dans la même livraison** par la ligne de zones, et
conservée là où elle n'est pas un doublon.

**§5.5 — centralité avant facilité.** L'annotation du corpus est le cœur de
C8 ; le filtre en découle. Aucune des deux n'a été choisie pour sa facilité.

---

## 8. Vérifications (`CLAUDE.md §1`)

| Vérification | Résultat |
|---|---|
| `check_scope.py` | **`SHARED_CODE`** |
| Sweep ciblé, 13 fichiers consommateurs | **223 passés, 0 échec** |
| `tests/test_train2_explore_context.py` | **21 passés** |
| ruff (rapport CI reproduit) | **276 avant / 276 après** — 0 sur les fichiers touchés |
| `check_ruff_budget.py` | OK (276 ≤ 548) |
| `check_spec_protocol.py` | OK |
| Pré-scan AST S9073 / S5863 / S1192 | 0 nouveau |
| Doublons de sélecteurs CSS (`css:S4666`) | **0 introduit** (6 préexistants, hors périmètre) |

Coût serveur mesuré : l'annotation du corpus complet vaut **~20 ms / 160
requêtes** sans mémoïsation. Le service mémoïse **par appel** sur le nom
d'exercice — un cache qui ne survit pas à la requête ne peut pas devenir
périmé quand le référentiel change. Si le catalogue grossit, le groupage des
lectures est la prochaine étape ; à treize gabarits il serait prématuré, et le
chiffre est consigné pour que la décision soit prise sur mesure.

---

## 9. Ce que cette tranche ne fait pas

* **Aucun renommage de surface.** C8 nomme la destination « Explore » ; le
  produit l'appelle « Programmes de séance » et l'onglet « Programmes ».
  Renommer est une décision d'appellation, pas une conséquence technique de
  cette tranche — **laissé à l'arbitrage**.
* Aucun changement de moteur : `weekly_planner`, `exercise_zone_resolver`,
  `muscle_mapping` sont **lus**, jamais modifiés.
* Aucune migration, aucune écriture de schéma, aucun gabarit ajouté ou retiré
  du catalogue.

---

## 10. Closeout post-merge

| | |
|---|---|
| PR | **#163** |
| Merge | **`ea5880d`** — `--merge`, tête épinglée `4fbcc1b`, **pas de squash, pas de `--admin`, pas de force** |
| CI de PR | 9/9 `pass`, **aucun cycle rouge** |
| CI canonique (`push` sur le merge) | run **32902173485** — **succès** |
| Sonar (gate PR) | **OK** — couverture neuve **96,7 %** · 0 bug · 0 code smell · 0 vulnérabilité · duplication 0,0 % |
| Fils de revue non résolus | 0 |

### Ce que cette tranche laisse au dépôt, au-delà du code

**Une mesure peut supprimer une fonctionnalité, et c'est le meilleur usage
qu'on puisse en faire.** L'étiquette « zone sous le volume visé » était prévue,
justifiée, facile à écrire. Mesurée avant d'être écrite : 7 zones sur 11 sous la
cible pour une déclaration de 4 séances. Elle serait tombée sur presque chaque
carte. Livrée, elle aurait été indiscernable d'une fonctionnalité utile — c'est
précisément ce qui la rendait dangereuse.

**Trois fautes d'instrument, toutes dans les gardes, dont une qui aurait pu
créditer une garde jamais exécutée.** `pytest` sort avec le code 5 quand il ne
collecte **rien** ; un harnais de plantation qui teste `returncode != 0` compte
alors un sélecteur `-k` invalide comme une garde qui mord. Le harnais nomme
désormais ce cas explicitement.

Même famille, corrigée dans la foulée sur l'outil qui surveille la CI
canonique : un appel `gh` en échec n'est **pas** « aucun run ». La première
version laissait remonter l'erreur et s'arrêtait sur ce qui ressemblait à un
verdict. Un hoquet d'API doit faire réessayer, jamais conclure.

### Reste ouvert — deux arbitrages, aucun bloquant

1. **Q5 (tranche A)** — « Pourquoi ce plan ? » est rendue en carte bordée alors
   que c'est un objet informatif de rang 2. Manquement **antérieur** au
   déménagement ; corriger l'apparence dépasse une tranche de déplacement.
2. **Appellation « Explore »** — C8 nomme ainsi la destination ; le produit
   l'appelle « Programmes de séance », onglet « Programmes ». Décision
   d'appellation, pas conséquence technique. **Non fait.**
