# La nuit du 5 au 6 septembre — neuf tranches, et deux leçons sur mes propres gardes

Passe autonome sur mandat opérateur : `GO BUILD` + `GO MERGE` + nettoyage.
Neuf tranches livrées avec la porte complète, la **CI canonique de push
vérifiée verte** à chaque fois.

## 1. Ce qui est parti

| PR | Objet | Le défaut central | Merge |
|---|---|---|---|
| `#207` | Récap de séance | trois valeurs d'énumération **anglaises** à l'écran ; 50 blocs de texte sur 57 dans deux corps voisins — un plateau | `741833f` |
| `#208` | Rang SECTION | le titre de bloc **plus petit que le contenu qu'il introduit**, sur **onze gabarits** | `21f022b` |
| `#209` | Relevé de décisions | quatre arbitrages gouvernaient le code **sans exister dans un fichier** | `b62757a` |
| `#210` | Tokens fantômes | deux couleurs jamais choisies, une **jamais peinte du tout** | `b5109f1` |
| `#197` | Closeout de la veille | ouvert depuis 16 h, vert, propre, jamais mergé | `cae3c72` |
| `#211` | Éditeur de programmes | cinquante attributs `style` alors que le vocabulaire existait | `61d7393` |
| `#212` | Surface sociale | un fil d'activité **rendu en colonnes sans espaces** | `1009001` |
| `#213` | Seuil de pluriel | « 0 séance**s** » sept fois, et trois clés de programme sur un **profil public** | *(en vol)* |

Plus les tranches de la première moitié de nuit (`#198`–`#206`), couvertes par
leurs rapports respectifs.

**Smoke test final** : 21 routes rendues, **21 en 200**, zéro erreur
JavaScript.

## 2. Le diagnostic, seizième à vingtième occurrence

*Le produit ne manque presque jamais de la décision. Il manque du moyen de
l'appliquer.*

| Ce qui manquait à l'écran | Ce qui existait déjà |
|---|---|
| `Concentration → low` | `DECLARED_STATE_LABELS` traduisait l'énergie ; la concentration n'avait jamais eu sa table |
| `var(--success, #2e7d32)` à **3,41 : 1** | **`--ok: #6E9E7A`**, à **5,69 : 1**, dans le même bloc « États sémantiques » |
| `max-width: 40rem` écrit en dur ×4 | `.pd-page` le portait depuis `Sb_UI_PROGRAM_DETAIL_01` |
| « 586.0 pts » | la décision existait, appliquée en **trois orthographes** et oubliée sur la quatrième surface |
| `owner` / `member` bruts | le patron `LEVEL_LABELS` venait d'être posé — **là où je regardais** |
| `color:#fff` sur un aplat vert, **3,07 : 1** | `--on-accent`, **6,37 : 1** sur le même fond |
| « 0 séance**s** », sept fois | le filtre `pluriel` **documente ce défaut dans sa propre docstring** |
| `pecs` / `back_width` sur un profil **public** | `RADAR_AXES` porte les libellés, dans le module que le service **importe déjà** |

### Deux formes plus vicieuses que l'absence

**Le moyen existe et il est MAL PRIS.** `.stats-list li` est une ligne
clé/valeur (`display:flex; space-between`). Le fil d'activité squad
l'empruntait pour de la **prose** : flex a fait de « marin », « recommande » et
du nom du modèle trois colonnes, **sans espaces entre eux**. Ce n'est pas une
pièce manquante, c'est une pièce prise pour une autre — et j'avais commis
exactement la même erreur deux tranches plus tôt avec `.pd-sessions`, en
l'écrivant dans la feuille pour ne pas la refaire.

**Le moyen manque, donc chacun l'improvise — et j'en deviens l'auteur.** Sur
les trois orthographes de la virgule décimale, **deux étaient de moi**, écrites
la même nuit. Poser le filtre a révélé **six** occurrences, pas trois : mon
propre balayage en avait manqué la moitié.

## 3. Mes gardes, deux fois prises en défaut

### Une sonde qui lit la prose comme du code — en fratrie de trois

`test_app_shell_navigation`, `_hardening` et `_desktop_rail` cherchent une
couleur en dur par `css[css.index(MARQUEUR):]` + regex, **sans retirer les
commentaires**. Elles ont fait tomber **deux tranches indépendantes à deux
heures d'intervalle**, sur des hexadécimaux cités dans une prose qui
documentait précisément leur retrait.

Trois copies du même idiome ⇒ trois shards rouges. La sonde vit désormais **en
un seul exemplaire** dans `tests/helpers.py` : *trois copies d'une sonde
divergent, c'est le défaut qu'elle corrige.*

**Ce que je n'ai pas fait** : réduire leur portée. `css[index:]` va jusqu'à la
fin du fichier, pas jusqu'au bloc suivant — leur nom ment, mais la largeur est
**utile** et garde chaque bloc ajouté depuis. Conservée ; ce sont les messages
qui cessent de mentir.

### Ma propre garde des tokens fantômes est partie avec trois trous

Écrite le soir, corrigée avant merge, après l'avoir promenée sur des fichiers
qu'elle n'avait pas servi à écrire :

1. **elle ne voyait pas la forme grave** — `var(--fantome)` **sans repli** rend
   la déclaration invalide au calcul : rien n'est peint. Vu en vrai,
   « Préférences enregistrées » restait **grise** ;
2. **elle accusait un token sain** — sa détection exigeait un début de ligne, et
   manquait les quatre `--mf-frames` déclarés sur la ligne de leur sélecteur ;
3. **elle s'accusait elle-même** — son propre fichier cite `--success` en le
   documentant.

*Une garde se teste contre le dépôt, pas contre l'intention de qui l'écrit.*

### Un cliquet n'est pas un jugement

Le cliquet ambre enregistrait `squad_detail.html: 4`. Quatre aplats ambre —
exactement ceux qui s'affichent **ensemble** sur cet écran, en violation
directe de « un seul par écran, strictement ». **Il avait gelé la dette sans la
juger**, et son propre commentaire le dit : « ce n'est PAS un compte d'écran ».

Personne n'avait regardé le rendu. C'est précisément ce que `CLAUDE.md §5.1`
exige, et aucune garde automatisée ne le remplacera.

## 4. Un rouge canonique qui n'en était pas un

La canonique de `#208` est tombée sur un test de performance —
`/body/intelligence p95 = 4269 ms` contre un budget de 2500. Le même commit
avait passé **ce même test** sur sa PR quelques minutes plus tôt, et une taille
de police ne ralentit pas une route.

**Rejeu des jobs échoués, sans nouveau commit → vert.** Bruit de runner,
diagnostiqué plutôt que « corrigé ». `CLAUDE.md §2` demande de distinguer un
échec de test d'un incident d'infrastructure ; le critère décisif était ici
« le même code, vert ailleurs, minutes avant ».

## 5. Mesures

| | début | fin |
|---|---|---|
| attributs `style` statiques | **328** | **174** sur 30 gabarits |
| pluriels au seuil anglais | 7 | **0**, gardés |
| clés de programme rendues à l'écran | 6 relevées | **1** — `push_horizontal`, qui demande une taxonomie |
| tokens fantômes peignant un repli | 16 sur 9 tokens | **0 hors viseur**, 5 exemptés avec leur raison |
| titres de bloc sous leur propre corps | 101 usages documentés | **0** — `.section-header` promu au rang SECTION sur 11 gabarits |
| orthographes de la virgule décimale | 3, plus une surface sans rien | **1 filtre** |

## 6. Nettoyage

**Trente arbres de travail → neuf.** Vingt-et-un retirés, tous avec PR mergée
et arbre propre. **Les branches ne sont pas supprimées** : c'est la moitié
réversible du nettoyage — le répertoire part, chaque commit reste.

Jamais touché : les trois arbres **sales**, les deux sur PR ouvertes, et
`-custom` (branche de spec de l'opérateur).

### Un hasard du nettoyage : l'arbre principal est périmé

`/Users/martinfeldmann/workout-session-tracking` est resté sur `4549d8f`,
**plus de vingt commits en retard**. J'y ai compté 368 styles inline là où il y
en avait 250 — dont 31 sur un gabarit ramené à zéro trois PR plus tôt.

**Cause** : sept fichiers y sont *non suivis* alors que la canonique les a
committés depuis, ce qui fait échouer tout `merge --ff-only` en silence.
Vérifié : cinq sont **identiques** au committé, les deux autres sont des
brouillons **strictement antérieurs** (diff en pure suppression, zéro
insertion). Les retirer serait donc **sans perte** — mais supprimer des
fichiers du répertoire de travail principal n'est pas une action d'agent.

**Non fait, signalé.** En attendant, toute mesure passe par un worktree créé
sur le SHA canonique.

## 7. Quatre décisions attendent l'opérateur

Rassemblées, rendues et mesurées dans un tableau privé ouvrable depuis un
téléphone — avec un commutateur qui échange les variantes **au même endroit de
la page**, seule façon de juger une échelle sur trois écrans et demi :

**https://claude.ai/code/artifact/76e226fe-7cb1-471a-83bc-8ead6246b627**

1. **`/library`** — l'échelle du catalogue. Trois variantes rendues ; ma
   recommandation est `L` (maison stricte), coût mesuré **+0,04 écran**, aucun
   titre à deux lignes sur 17 vérifiés.
2. **`/profile`** — la refaire maintenant, ou attendre la **règle de
   dérivation** de l'état (amendement `Q3`) ? La refaire avant que la règle
   existe revient à la refaire deux fois.
3. **La palette** — `--warn` et `--danger` sous AA sur leurs propres badges
   (4,41 et 3,42). Remède calculé à teinte et saturation constantes :
   `#CF8D6B` et `#C78080`. **Non livré** parce que ces tokens servent aussi de
   **fond** dans quatre règles : réparer un couple en dégradant quatre autres
   est le mode d'échec que cette passe combat.
4. **`/squads/1`** — quatre aplats ambre simultanés contre `Q7`.

## 8. Ce qui reste ouvert, sans arbitrage requis

* **174 attributs `style`** sur 30 gabarits. Les plus gros :
  `body_overview` (21), `profile` (17), `dashboard` (13), `index` (13) ;
* **`dashboard.html` n'est rendu par aucune route** — `/dashboard` redirige
  vers `/progress` depuis `Sb_27.6`. Ses 13 attributs `style` sont de la dette
  **morte** : les nettoyer déplacerait un cliquet sans améliorer un pixel, et
  `§5.1` serait insatisfiable faute de rendu. La vraie question est s'il doit
  être supprimé ;
* **150 replis de tokens décoratifs** — le token existe, le repli ne part
  jamais. Dette de style, pas défaut visuel : à résorber au fil des tranches ;
* **les accents du catalogue** — `templates[10]`, trois chaînes. La garde de
  `seed_reference_split` est un **test d'existence de version** : corriger le
  JSON sans bumper laisserait le fichier juste et l'écran faux. Décision
  opérateur, faits dans `SPRINT_Sb_UI_SESSION_DONE_01_REPORT.md §8` ;
* **`/body/intelligence` répond 404** derrière son drapeau : le correctif
  `--bg-elev` y est écrit et mesuré mais **non vérifié au rendu** ;
* **le tableau de classement squad** — six colonnes sur un téléphone ;
* **`.btn` à 14 px** — primitive partagée, à trancher globalement ;
* **`push_horizontal` sur un profil public** — pas de table de libellés, et
  l'espace de clés mélange patterns, familles d'exercices et variantes
  d'isolation sur **dix-neuf chaînes**. En créer une demande de trancher une
  taxonomie, pas de traduire un mot ;
* **aucune garde ne surveille les anglicismes en général**, et c'est
  volontaire : la liste étroite de `#213` est extensible, une garde large
  accuserait « squad », « template » et « Challenges » — des noms de produit
  que l'opérateur a choisi de garder.

## Verdict

**LIVRÉ.** Huit tranches mergées cette nuit avec la porte complète, une en vol.
La dette d'attributs `style` a perdu **47 %**. Le défaut le plus cité du socle
visuel est fermé **en classe**, sur onze gabarits à la fois plutôt que sur la
surface commode.

Et deux leçons qui valent les tranches : **une garde se teste contre le dépôt**,
et **un cliquet ne prononce jamais la conformité**.
