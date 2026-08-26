# `UX4_02C` — deux corrections de cohérence avant l'étude utilisateur

`OPERATOR_DECISION` · branche `sb/ux4-02c-coherence` · base `26ace24`

---

## 1. Ce que cette tranche fait, et ce qu'elle s'interdit

L'ordre est explicite : **deux corrections déjà décidées, et rien d'autre**,
avant `UX4_02C_PROGRAMS_REAL_USER_DOGFOOD_01`.

| | Décision | Fait |
|---|---|---|
| **Q5** | « Pourquoi ce plan ? » est du contenu informationnel de niveau 2 : retirer le traitement en carte bordée autonome, conserver en divulgation progressive **dans le flux**, **aucune refonte de contenu** | ✅ |
| **NAMING** | Domaine **PROGRAMMES** ; enfants **MON PLAN**, **MES PROGRAMMES**, **EXPLORER**. Pas d'« Explore » anglais dans l'interface française | ✅ |

**Atlas : non rouvert.** Sa condition de réouverture — que `TRAIN 3` démontre
une entrée dans l'atlas sans contexte machine connu — n'a pas été remplie par
l'étape B, qui est une tranche de correctness sans surface. Rien n'a été touché
de ce côté.

Aucune fonctionnalité, aucune migration, aucun changement de moteur.

---

## 2. Q5 — de la carte au flux

Le bloc était une `<section class="card">` avec titre : le traitement de rang 1
du relevé de décisions, pour un objet de rang 2. Il devient un `<details>` dans
le flux, séparé par un simple filet.

**Le contenu n'a pas bougé** — mêmes éléments, mêmes sources citées une par
une, même avis final, même ordre. Une garde le vérifie **élément par élément**
contre ce que `build_plan_explanation` produit, plutôt que sur une chaîne
témoin.

Effet mesuré sur `/plan` à 390 px, compte déclaré :

| | Écrans | Mots | Cartes |
|---|---|---|---|
| Avant | 2,1 | 243 | 3 |
| Après | **1,3** | **103** | **2** |

La surface passe sous les deux écrans. Ce n'est pas l'objectif de Q5 — c'en est
la conséquence, et elle confirme le diagnostic : trois cartes bordées sur une
surface courte, c'est ce que le relevé nomme « une carte qui entoure tout
n'entoure plus rien ».

---

## 3. Le défaut que le rendu a révélé — et qui existait déjà

Le premier rendu de Q5 montrait « Pourquoi ce plan ? » comme **du texte inerte** :
aucun triangle, rien qui indique que ça s'ouvre.

Diagnostic **mesuré sur les styles calculés**, pas supposé — trois déclencheurs
de la même page comparés :

| Déclencheur | `display` | marqueur visible |
|---|---|---|
| « Modifier mes préférences » (témoin qui marche) | `list-item` | ✅ natif |
| « Pourquoi ce plan ? » (neuf, Q5) | `flex` | ❌ **aucun** |
| « Filtrer par zone » (livré en `TRAIN 2` tranche B) | `flex` | ❌ **aucun** |

**Un `<summary>` en `display: flex` perd son marqueur natif.** Le second n'est
pas neuf : **je l'ai livré ainsi deux tranches plus tôt**, et personne ne
pouvait le voir dans le gabarit.

### Pourquoi j'ai corrigé le second, alors que l'ordre disait « deux corrections »

Le filtre par zone est **l'objet même de la tâche T4** de l'étude à venir :
« le participant découvre-t-il spontanément le filtre ? ». Mesurer la
découverte d'un contrôle dont **rien n'indique qu'il s'ouvre** n'aurait pas
mesuré la découverte, mais un défaut d'affordance déjà connu et déjà
diagnostiqué. Laisser le défaut aurait corrompu la donnée que l'étude existe
pour produire.

C'est une **troisième modification, assumée et signalée**, pas un élargissement
discret. Elle est d'une ligne de sélecteur, ne touche aucun contenu et aucune
couleur.

### Et un troisième cas, mesuré et NON corrigé

La recherche générale a trouvé deux autres `<summary>` en `flex` :

* `.machine-panel__summary` — **CSS mort** : plus aucun `<summary>` ne porte
  cette classe. Rien à corriger.
* `.substitute-picker__summary` — **défaut réel, laissé intact**. Il vit sur
  l'écran de séance, surface **SOUVERAINE**, et porte un badge de compte en
  `space-between` : y ajouter un chevron changerait l'apparence d'un contrôle
  protégé. Hors des deux corrections ordonnées → **mesuré, consigné, soumis à
  arbitrage**.

---

## 4. NAMING — un domaine, trois enfants nommés

Le défaut n'était pas seulement un mot anglais : **l'enfant portait le nom du
domaine**. L'onglet « Programmes » menait à une page intitulée « Programmes de
séance », et le mot **« Explorer » n'existait nulle part** dans l'interface —
aucun des trois enfants n'était donc désignable par son nom.

| | Avant | Après |
|---|---|---|
| Onglet du domaine | Programmes | Programmes *(inchangé)* |
| `/plan` | Mon plan | Mon plan *(inchangé)* |
| `/programs` | Mes programmes | Mes programmes *(inchangé)* |
| `/library` | **Programmes de séance** | **Explorer** |
| Menus de la coque | 2 enfants nommés | **3 enfants nommés, chacun menant à sa surface** |

Trois tests existants épinglaient « Programmes de séance ». Ils **suivent la
décision** — aucun affaibli, aucun supprimé — et gagnent l'assertion inverse :
l'ancienne appellation ne doit pas subsister, car deux noms pour une surface
sont exactement le défaut qu'on retire.

---

## 5. Gardes plantées

**14 gardes · 11 défauts plantés, 11 rouges** : la carte revient · le titre
disparaît du déclencheur · le repli est déplié par défaut · l'avis final est
retiré · les sources cessent d'être citées · le marqueur n'est plus dessiné ·
le marqueur perd sa largeur · l'enfant reprend le nom du domaine · un nom
anglais entre dans l'interface · un enfant cesse d'être nommé · le déclencheur
passe sous 44 px.

### Trois fautes d'instrument, toutes trouvées, toutes corrigées

1. **Compter les `<span>` ne prouve pas que les sources sont citées.** En
   retirant `item.source_label`, le span **reste** — vide — et la garde restait
   verte pendant que plus aucune source n'était nommée. Elle compare désormais
   aux libellés **produits**.
2. **Chercher la chaîne `::before` ne prouve pas qu'un marqueur est dessiné.**
   Le sélecteur réapparaît dans la règle `[open]` et dans le bloc
   `reduced-motion` : supprimer la règle qui dessine laissait la garde verte.
   Elle exige maintenant une déclaration qui **produit** quelque chose.
3. **La plus instructive : mes deux plantations du marqueur étaient rouges POUR
   LA MAUVAISE RAISON.** Mon extracteur CSS n'acceptait pas les sélecteurs sur
   plusieurs lignes, or la règle groupe les deux replis ; il ne voyait que le
   second et déclarait le premier sans marqueur — donc la garde échouait déjà
   sur du code sain. **Ce n'est pas la plantation qui l'a montré, c'est le
   sweep élargi.** Une plantation qui rougit ne prouve rien si la garde rougit
   aussi à vide.

---

## 6. Exposition §5.1

360×800 · 390×844 · 430×932, comptes déclaré et vierge, sur les trois surfaces
du domaine. Chevron vérifié **au rendu** après correction (largeur mesurée :
5 px, absent avant).

* `/plan` déclaré : **1,3 écran · 103 mots · 2 cartes**, les trois objets
  présents, l'explication repliée avec son titre et son marqueur visibles ;
* `/plan` vierge : 1,0 écran · 54 mots, inchangé ;
* **0 débordement horizontal**, **0 cible < 44 px dans `<main>`** sur les
  18 rendus.

---

## 7. Relecture du relevé de décisions (`CLAUDE.md §5.2`)

| Décision | Verdict |
|---|---|
| Q1 connexion / identité | non concernée |
| Q2 ancre visuelle de l'accueil | non concernée |
| Q3 « État du jour » replié | non concernée |
| Q4 ligne de série instrument | non concernée |
| **Q5 surfaces, trois rangs** | **VIOLATION RÉPARÉE** — c'est l'objet de la tranche. Le manquement consigné en `TRAIN 2` tranche A est fermé : plus aucune carte bordée pour un objet de rang 2 sur `/plan` |
| Tokens | respectée — **aucune couleur introduite** ; le chevron est `currentColor` |
| Ordre de livraison | respectée — corrections décidées avant l'étude ordonnée |

`§5.1` rendus exposés ✅ · `§5.3` aucune soustraction seule — le contenu de
l'explication est intégralement conservé, seul son conteneur change ✅ ·
`§5.4` aucune couleur ✅ · `§5.5` les deux corrections sont ordonnées par
l'opérateur, pas choisies pour leur facilité ✅

---

## 8. Vérifications

| Vérification | Résultat |
|---|---|
| `check_scope.py` | `ISOLATED` → **remonté à la main en `shared_code`** (`base.html` est la coque de toutes les pages) |
| Sweep ciblé, 14 fichiers | **288 passés, 0 échec** |
| `tests/test_ux4_02c_coherence.py` | **14 passés** |
| ruff (rapport CI reproduit) | **276 / 276** — 0 sur les fichiers touchés |

---

## 9. L'étude, et la frontière de ce que je peux faire

Le protocole complet est dans
[`UX4_02C_PROGRAMS_DOGFOOD_PROTOCOL.md`](UX4_02C_PROGRAMS_DOGFOOD_PROTOCOL.md) :
cadrage mot pour mot, cinq tâches qui ne nomment jamais leur destination,
définitions opérationnelles de `SUCCESS` / `HESITATION` / `RESCUE` / `FAIL`,
feuille de relevé par participant, méthode de regroupement.

**Ce que je ne peux pas faire, et qui revient à l'opérateur** : recruter les
cinq participants, modérer, observer les gestes sur un appareil réel. Aucune
mesure automatisée de ce dépôt ne remplace cinq personnes devant un téléphone —
c'est exactement pourquoi cette étude a été ordonnée, et pourquoi la tranche
s'arrête ici.

Prochain état : **`PROGRAMS REAL-USER DOGFOOD — OPERATOR REVIEW`**.
