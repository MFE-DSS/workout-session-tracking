# `TRAIN1-C` — Consolidation de Progression

**Canonique de départ** : `d18d1aa` · **Tier `check_scope`** : `SHARED_CODE`
**Contrat** : ordre opérateur *TRAIN1-C — PROGRESSION CONSOLIDATION / BUILD AUTHORIZED*

---

## 1. Brainstorming / Options / Risques / Choix retenu (`CLAUDE.md §3`)

### Le fait qui a orienté toute la tranche

`/physique` n'était pas « une page avec un score en trop ». Son score de zone,
sur 100, **est le substrat** du score global : le global est la moyenne des
agrégats des onze scores de zone. Retirer la somme en gardant les termes aurait
masqué la doctrine sans la retirer.

Et cette doctrine contredit une règle **écrite** du dépôt. Son pilier
d'exposition vaut :

```python
hard_sets / (ZONE_VOLUME_TARGET[zone] * window_days / 7) * 100
```

soit un **pourcentage de cible** — exactement ce que l'en-tête de
`zone_exposure.py` s'interdit de dire, au motif qu'aucune littérature ne
justifie les bornes du dépôt. La barre de la carte de zone le rendait comme une
progression vers un objectif.

Deux autres piliers relèvent du même arbitrage : `_score_performance` range une
variation de tonnage dans cinq paliers codés en dur ; `_score_anthropo` note à
90 un tour de bras qui augmente et à 30 un qui diminue (inversé pour la taille).
Ce sont des jugements de valeur.

### Options examinées

| Option | Ce qu'elle donnait | Verdict |
|---|---|---|
| **A** — retirer score/lettre/radar, garder les cartes de zone avec leur note sur 100 | la doctrine survit intacte, onze fois, sans sa somme | ✗ retrait cosmétique |
| **B** — supprimer `muscle_scoring` | le classement public et les profils publics perdent leur radar | ✗ sort du périmètre de Progression |
| **C** — retirer la surface, **recenser** les consommateurs restants, absorber le seul fait qui manquait à Progression | doctrine hors de Progression, service vivant là où il est inscrit, un fait gagné | ✓ **retenue** |

### Risque principal, et sa mitigation

Absorber « les séries par zone » depuis un module qui utilise **un autre
résolveur** (`resolve_exercise_zones`) que l'instrument d'exposition
(`resolve_zone`) aurait mis **deux attributions contradictoires sur une même
ligne**. Le fait est donc recalculé dans `zone_exposure`, avec **son** résolveur,
**sa** fenêtre, et **aucun** coefficient.

---

## 2. Ce que la tranche livre

### 2.1 Convergence Physique

`/physique` → **redirection 303 vers `/progress`**. `physique.html` supprimé.

**Ce qui a survécu au déménagement** : les **séries de travail validées par
zone**, absorbées dans l'instrument `Exposition · 14 j`, à trois conditions —
même fenêtre (14 j, pas le sélecteur 30/60/90), même résolveur, aucun
coefficient ni cible. Une série compte une fois, sur la zone primaire, rendue
comme un entier.

**Ce qui n'a pas suivi** — et pourquoi, en détail dans
[`docs/LEGACY_SCORE_CONSUMERS.md`](LEGACY_SCORE_CONSUMERS.md) :

| Objet | Décision |
|---|---|
| score, lettre, radar, barres de zone | doctrine — retirée, **non déplacée** |
| `confidence` (« élevée / moyenne / faible ») | un compte de signaux avec des seuils arbitraires |
| `top_exercises` | fait réel, mais l'instrument progressif nomme déjà les exercices ; 33 noms de plus iraient contre la densité visée |
| `measurement_trend` (« +1,5 cm ») | fait réel, autre question, et **aucune surface ne peut le produire** : rien n'écrit de `BodyMeasurement` hors du parcours `/body`, désactivé par défaut |

**Et la provenance**, qui manquait. `MUSCLE_MAPPING_TRUTH_01` comptait déjà les
résolutions venues du référentiel et celles venues du repli — **sans jamais les
rendre nulle part**. C'était un défaut de ma part, signalé dans le CR précédent.
Le quatrième terme de la cible `FAIT → INSTRUMENT → INSPECTION → PROVENANCE`
n'existait pas à l'écran ; il existe.

### 2.2 Navigation

Deux entrées « Physique » retirées (menu topbar, rail desktop). Aucune
`/progress/body` créée. `/body/intelligence` conserve **deux** entrées, toutes
deux derrière son drapeau — vérifié, pas supposé : le retrait de la troisième
aurait pu orpheliner la surface.

### 2.3 Tableau de bord

`/dashboard` → **`/progress`** (était `/`). `dashboard.html` et
`compute_dashboard` conservés, **marqués dépréciés**, sous garde : aucun
nouveau consommateur de production ne peut apparaître sans faire rougir la CI.
Les huit fichiers de tests dépendants ne sont pas remués.

### 2.4 États vides

« Par programme » ne rend plus une carte pleine pour annoncer qu'elle n'a rien
à dire — **elle est masquée**, et l'implication le justifie : `template_kpis`
vide ⟺ aucune séance terminée non exclue, jamais ⟹ « Aucune séance terminée ·
30 j » est déjà à l'écran, et « Aucune séance · 14 j » aussi.

`cockpit-grid` part avec elle : ce conteneur vaut `3fr 2fr` au-delà de 1024 px
et réservait 40 % de la largeur à une colonne vide depuis que `TRAIN1-B` en a
retiré le second enfant.

### 2.5 KPI sans dénominateur

Les deux cartes dont la mesure n'existe pas **disparaissent** ; leur raison
reste, sur une ligne, nommée par la sémantique du producteur :

> Non calculable · 30 j — aucune série de travail prescrite, aucun exercice noté

Une garde symétrique interdit la sur-suppression : **0 validé sur 2 prescrits
est une mesure**, et son `0 %` reste rendu.

### 2.6 Boucle hebdomadaire

`/progress` appelle désormais `build_progress_week`, qui produit **deux** clés
au lieu de quatorze. Les quatre phrases — `narrative`, `hint`, `volume_signal`,
`data_quality_note` — ne sont plus calculées sur ce chemin. `build_weekly_loop`
et `narrate_week` **restent** en place et testés.

`_partials/weekly_loop.html` est supprimé : orphelin depuis `TRAIN1-A`.
`compute_recent_exercise_activity` n'est plus appelée par la route — mon oubli
de `TRAIN1-B` : la requête tournait encore à chaque affichage pour un résultat
que le gabarit ne lisait plus.

---

## 3. Preuve au rendu (`CLAUDE.md §5.1`) — 3 formats × 4 comptes

Serveur local, comptes de lab, cookies frappés par le helper de production.
Formats **360×800 · 390×844 · 430×932**.

### 3.1 Ce que `/physique` montrait — le chiffre qui justifie la tranche

| compte | avant | après |
|---|---|---|
| **vide** | `/physique` · 162 mots · 2,3 écrans · **score 1 · lettre 1 · radar 1** | `/progress` · 87 mots · 1 écran · 0 · 0 · 0 |
| maigre | idem, **162 mots identiques** | 218 mots · 2,1 écrans · 0 · 0 · 0 |
| plein | idem, **162 mots identiques** | 333 mots · 2,7 écrans · 0 · 0 · 0 |
| cardio | idem, **162 mots identiques** | 208 mots · 2,1 écrans · 0 · 0 · 0 |

**162 mots identiques pour les quatre comptes.** La surface ne variait pas avec
les données. Et un compte **sans une seule séance** y lisait un score global de
**0** avec la lettre **C**, un radar réduit à un point, et onze cartes de zone à
« 0 » portant chacune une flèche de détail. `C` est le plancher de
`compute_grade` : le produit notait quelqu'un qui n'avait jamais rien fait.

### 3.2 `/progress`, état replié

| compte | écrans | mots | boîtes | tirets nus |
|---|---|---|---|---|
| vide | 1,2 → **1** | 112 → **87** | 1 → **0** | 0 → 0 |
| maigre | 2,1 → 2,1 | 215 → 218 | 7 → 7 | 0 → 0 |
| plein | 2,7 → 2,7 | 333 → 333 | 10 → 10 | 0 → 0 |
| cardio | 2,2 → **2,1** | 225 → **208** | 7 → **5** | **2 → 0** |

Les +3 mots du compte `maigre` sont l'**équivalent textuel hors écran** : il
porte désormais les séries. La silhouette est `aria-hidden` et ne peut l'être
que parce que ce paragraphe porte les mêmes faits — ajouter une colonne à
l'écran sans l'ajouter là l'aurait rendue visuelle-seulement.

### 3.3 Le reste des mesures demandées

| mesure | avant | après |
|---|---|---|
| modules vides pleine taille (compte vide) | 1 — « PAR PROGRAMME · Aucune session terminée pour l'instant. » | **0** |
| scores globaux / lettres / radars sur le parcours | 1 / 1 / 1 (sur `/physique`) | **0 / 0 / 0** |
| destinations mortes (19 liens réellement suivis) | 0 | **0** (18 liens) |
| liens menteurs (rebond vers la page d'origine) | 0 | **0** |
| débordement horizontal | aucun | **aucun** |
| colonnes « séries » au niveau d'inspection | 0 | **11** (compte maigre), 5 (partiel) |
| ligne de provenance | absente | « Attribution : 8 depuis le référentiel » |

---

## 4. Relecture des décisions UI (`CLAUDE.md §5.2`)

| Règle | Verdict |
|---|---|
| **5.1** exposition visuelle préalable | **respectée** — 24 captures pleine page, 3 formats × 4 comptes, avant/après ; deux défauts trouvés à l'œil seul (voir §5) |
| **5.2** relecture consignée | **respectée** — ce tableau |
| **5.3** jamais une soustraction seule | **respectée** — la surface Physique part avec son fait absorbé dans la même livraison ; le partiel `weekly_loop` part avec ses deux faits déjà absorbés par `TRAIN1-A` ; le lien BI retiré est remplacé par la vérification que deux entrées subsistent |
| **5.4** toute couleur est un token mesuré | **non concernée** — aucune couleur introduite. `.ze-row__s`, `.ze-prov` et `.kpi-absent` réutilisent `--fg-muted` / `--fg-dim`, déjà mesurés |
| **5.5** centralité avant facilité | **respectée** — la convergence Physique (point 1, la plus centrale et la plus difficile) a été traitée en premier ; les états vides et la boucle hebdomadaire, plus commodes, ensuite |

---

## 5. Défauts trouvés — et ce qui les a trouvés

### 5.1 Dans le produit

1. **Un compte vide notait C.** `/physique` rendait score, lettre et radar
   identiques quelles que soient les données. *Trouvé en regardant la capture.*
2. **Deux tirets géants comme résultats.** Le compte cardio lisait `—` dans deux
   cartes de la taille des mesures réelles. *Trouvé par la mesure, confirmé au
   rendu.*
3. **Une carte pleine pour dire qu'il n'y a rien.** *Mesuré : 1 module vide
   pleine taille sur le compte vide.*
4. **Une note de bas de page qui définit un mot absent de l'écran.** Sur le
   compte vide, elle expliquait « prescrits = … » sous un écran où la carte qui
   emploie ce mot venait d'être supprimée. **La promesse sans réponse,
   retournée.** *Invisible autrement qu'en regardant l'écran.*
5. **Une colonne morte de 40 % sur desktop** (`cockpit-grid` à un seul enfant).
6. **`compute_recent_exercise_activity` tournait pour rien** à chaque affichage.
7. **« 1 zones touchées »** dans l'équivalent lecteur d'écran — sur la ligne même
   que cette tranche réécrit, et donc là où la faute s'entend.

### 5.2 De ma part, dans cette tranche

1. **Trois gardes fausses au premier jet** — un glob sur `_partials/` qui
   accusait le profil public, le module qui définit `compute_physique_dashboard`
   compté comme son propre consommateur, et `narrate_week` supposé rendre une
   chaîne alors qu'il rend un dict.
2. **Une garde qui passait pour la mauvaise raison.** `assert "0%" in r.text`
   restait verte alors que la carte était supprimée : la page contient
   `width:100%` et `offset="0%"` dans les dégradés du graphique SVG. **Trouvée en
   plantant le défaut, pas en relisant.**
3. **Deux mesures qui ne mesuraient rien.** L'audit des liens écartait tout href
   commençant par `http` — or `url_for` rend des URL absolues, donc il écartait
   **toute la navigation**, c'est-à-dire précisément ce que le point 7 demande de
   mesurer ; il rendait « 0 problème » sans avoir regardé. Et le détecteur de
   modules vides normalisait les sauts de ligne **avant** de découper dessus,
   donc il rendait 0 partout, y compris là où la carte vide existait.
4. **Une occurrence ruff neuve, passée sous le budget.** Mon insertion d'une
   constante dans `test_dashboard_routes.py` a produit un `I001` ; la CI l'a
   ingéré dans Sonar, où il vaut **MAJOR = 15** et a fait rougir le gate à
   15 pour un seuil de 14. **`check_ruff_budget.py` ne pouvait pas l'attraper** :
   c'est un cliquet sur le TOTAL (282 ≤ 548), pas une garde de code neuf. Une
   régression locale reste donc invisible tant que le total baisse par ailleurs.
   Mon pré-scan local, lui, ne portait que sur les fichiers que je croyais avoir
   touchés — celui-ci avait été modifié par un script, pas à la main. *La CI a
   rattrapé ce que mes deux gardes locales laissaient passer.*
5. **Une collision de cascade, évitée de justesse.** J'ai d'abord écrit la
   grille de `.ze-row` dans un bloc groupé placé **au-dessus** du bloc d'origine,
   qui garde `display: flex` — à spécificité égale, le dernier gagne. C'est
   exactement le défaut de la tranche précédente ; il a été vu avant tout rendu
   parce que je relisais la région, et la règle vit maintenant dans le bloc
   d'origine avec la raison écrite à côté.

### 5.3 Une garde qui ne gardait rien — la treizième

`test_the_unique_weekly_objects_survive` et
`test_coexisting_counts_of_the_same_entity_state_their_window` lisaient
`_partials/weekly_loop.html` — **un gabarit qu'aucune route ne rendait depuis
`TRAIN1-A`**. Elles étaient vertes quoi qu'il arrive à la vraie page. Les deux
lisent désormais la surface.

---

## 6. Vérifications

| Contrôle | Résultat |
|---|---|
| `check_scope.py` | `SHARED_CODE` |
| ruff (fichiers touchés) | **0 nouvelle** occurrence (9 pré-existantes dans `kpis.py`) |
| `check_ruff_budget.py` | 281 ≤ 548 |
| `check_spec_protocol.py` | OK |
| pré-scan AST `S9073` / `S5863` / `S1192` | 3 littéraux répétés **dans mon code neuf** hissés en constantes ; le reste pré-existant |
| gardes plantées | **10 / 10 rougissent** avec leur défaut en place |
| suite complète en local | **verte** — 230 fichiers au sweep + 48 en queue (détail ci-dessous) |
| gardes existantes migrées | **15**, aucune supprimée ni affaiblie |

### Le sweep s'est arrêté lui-même — deux fois, et c'était le bon comportement

| passage | lots verts | arrêt | pic / budget |
|---|---|---|---|
| 1 (`SWEEP_BATCH=4`) | 57 | lot 58 | 2306 Mo / **2012 Mo** |
| 2 (`SWEEP_BATCH=4`, serveurs de lab arrêtés) | 57 | lot 58 | 2062 Mo / **1860 Mo** |
| 3 (`SWEEP_BATCH=2`) | **115** — fichiers 1 à 230 | lot 116 | 1866 Mo / **1852 Mo** |
| queue (49 fichiers restants, lots de 3, processus neufs) | **17 / 17** | — | — |

**La suite entière est passée au vert**, en deux exécutions : les 230 premiers
fichiers au troisième passage du sweep, les 48 derniers par un runner de queue
qui fait le même travail (processus neuf par lot, série, sans couverture) sans
retester les 230 déjà couverts. Aucun échec dans l'un ni dans l'autre. Je le dis
ainsi plutôt que « sweep complet vert » : ce ne fut pas une seule commande.

La garde livrée en `Sb_OPS_LOCAL_SWEEP_MEMORY_01` a fait exactement ce pour quoi
elle existe : **s'arrêter elle-même plutôt que laisser l'OS choisir quel
programme tuer**. Elle a nommé les fichiers du lot fautif et proposé la sortie.

**Et elle apprend quelque chose sur elle-même.** Le budget vaut 60 % de la
mémoire **disponible**, mesurée au démarrage ; il a valu 2397 Mo la tranche
dernière, 2012 puis 1860 ici. Le pic d'un lot de quatre fichiers lourds
(`test_train1b_progressive_cockpit` + `test_train1c_progression_consolidation` +
deux autres) vaut ~2,1 Go et **ne dépend pas** de ce budget. Sur une machine
chargée, `SWEEP_BATCH=4` peut donc devenir inatteignable quoi que fasse le code
testé. L'échappatoire est prévue et imprimée par le script lui-même
(`SWEEP_BATCH=2`) ; ce qui manque est qu'elle soit **choisie automatiquement**
quand le budget descend sous ce qu'un lot de quatre demande. Noté pour
`Sb_OPS`, hors périmètre de cette tranche.

---

## 7. Ce que je n'ai pas fait, et pourquoi

- **`muscle_scoring.py` n'est pas supprimé.** Quatre consommateurs recensés
  `LEGACY_SCORE_CONSUMER`. Sa disparition suppose deux décisions hors
  Progression : ce que le classement public montre à la place du radar, et ce
  que devient Body Intelligence.
- **`dashboard.html` / `compute_dashboard` ne sont pas supprimés** — ordre
  opérateur explicite, huit fichiers de tests dépendants.
- **Le graphique « Qualité des séances » n'est pas touché.** Observé à plat sur
  le compte cardio de lab — mais c'est un artefact de ma graine (champs cardio
  sur un gabarit de force), pas un défaut produit : `compute_session_quality`
  dispatche vers un calcul cardio dédié. *Vérifié avant de le signaler.*
  Reste vrai qu'une séance de force **terminée sans une série cochée** vaut 0 et
  se trace comme un score — même famille que le point 5, hors du périmètre nommé.
- **L'état de la production reste NON MESURÉ** (registre II, B11) : aucun accès
  VPS. En particulier, `body_assessment_enabled` n'y est pas vérifiable, et
  l'argument « `measurement_trend` est inatteignable » repose sur la valeur par
  défaut du drapeau, pas sur une mesure en production.
