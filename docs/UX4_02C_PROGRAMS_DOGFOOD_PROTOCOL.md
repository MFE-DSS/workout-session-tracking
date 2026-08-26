# `UX4_02C_PROGRAMS_REAL_USER_DOGFOOD_01` — protocole d'étude modérée

`OPERATOR_DECISION` · à exécuter sur le produit **tel qu'il est**, après les
deux corrections de cohérence et **avant toute autre tranche**.

---

## 0. Ce que ce document est, et qui fait quoi

Ce document est **l'instrument**, pas l'étude. Il contient le script du
modérateur, les tâches, la grille de mesure et la méthode de regroupement.

**Ce que l'agent a fait** : les deux corrections décidées, la préparation des
comptes, le protocole ci-dessous, les feuilles de relevé.

**Ce que l'agent NE PEUT PAS faire, et qui revient à l'opérateur** : recruter
les participants, modérer les séances, observer les gestes, tenir la montre.
Aucune mesure de ce dépôt ne remplace cinq personnes devant un téléphone —
c'est précisément pourquoi cette étude existe.

> **Règle de fond** : on teste des **tâches**, jamais des opinions d'interface.
> « Est-ce que cette page vous plaît ? » ne produit aucune donnée exploitable.
> « Montrez-moi ce que vous feriez pour… » en produit.

---

## 1. Dispositif

| | |
|---|---|
| Participants | **5**, dont **au moins 3 indépendants** du développement produit |
| Profil visé | pratique de musculation régulière, utilisateur plausible d'AUREN |
| Support | **appareil réel, mobile de préférence** — pas un simulateur de bureau |
| Durée | 25–35 min par personne |
| Modération | une personne pose et observe ; **ne guide jamais** |
| Produit | **figé pendant toute la série** — aucune modification entre participants |

### Pourquoi le produit ne bouge pas entre deux participants

Corriger entre P2 et P3 rend les cinq observations non comparables : on ne sait
plus si P4 réussit parce qu'il a compris ou parce que l'écran a changé. Toute
correction attend la **revue opérateur** finale.

### Préparation des comptes

Chaque participant démarre sur un compte **vierge de déclaration** mais avec un
**historique de séances**, sinon les surfaces sont vides et l'étude ne mesure
que des états vides.

```bash
# Serveur accessible depuis un appareil du réseau local
python scripts/... --host 0.0.0.0        # cf. configuration « Run app (LAN) »
```

Un compte par participant, jamais partagé : la tâche 2 **écrit** une
préférence, et un compte réutilisé donnerait à P3 l'état laissé par P2.

---

## 2. Cadrage dit au participant, mot pour mot

> « Je vais vous demander de faire quelques choses dans une application
> d'entraînement. **Ce n'est pas vous qu'on évalue, c'est l'application.**
> Si vous êtes bloqué, c'est une information utile pour nous, pas un échec pour
> vous.
>
> Dites à voix haute ce que vous cherchez et ce que vous vous attendez à
> trouver. Si vous hésitez, dites-le.
>
> Je ne pourrai pas vous répondre pendant les tâches — pas parce que je ne veux
> pas, mais parce que ma réponse effacerait ce qu'on essaie de voir. »

**Interdits du modérateur pendant une tâche :**

* nommer une page, un onglet, un bouton, une icône ;
* dire « en haut », « en bas », « dans le menu » ;
* confirmer ou infirmer (« oui c'est ça », « pas tout à fait ») ;
* reformuler la tâche avec les mots de l'interface.

**Autorisé** : « Qu'est-ce que vous cherchez, là ? » · « À quoi vous attendez-
vous ? » · « Qu'est-ce qui vous ferait avancer ? » · le silence.

---

## 3. Les cinq tâches

Elles se suivent dans cet ordre : chacune laisse un état dont la suivante se
sert. **Aucune ne nomme sa destination.**

### T1 — Retrouver la configuration d'entraînement persistante

> « Vous avez indiqué à l'application, il y a quelque temps, **comment vous
> voulez vous entraîner** — à quelle fréquence, sur quoi insister, avec quel
> matériel. Retrouvez ce que l'application a retenu. »

*Ce qui est mesuré* : la déclaration est-elle **trouvable** depuis l'accueil,
sans qu'on ait nommé « Mon plan » ? C'est la tâche qui juge le déménagement de
`TRAIN 2` tranche A.

### T2 — Modifier un paramètre persistant réel

> « Vous voulez maintenant vous entraîner **une fois de plus par semaine**.
> Faites en sorte que l'application le sache. »

*Ce qui est mesuré* : le passage lecture → édition ; la découverte du repli ;
et surtout la **conséquence attendue**. Après enregistrement, demander **avant**
de laisser regarder :

> « Qu'est-ce qui a changé, à votre avis ? »

Puis seulement : « Regardez. C'est ce que vous attendiez ? »

### T3 — Retrouver ses propres programmes

> « Vous aviez créé un programme à vous, il y a quelques semaines. Retrouvez-
> le. »

*Ce qui est mesuré* : « Mes programmes » se distingue-t-il de « Mon plan » et
d'« Explorer » ? La tâche juge directement la décision de nommage.

### T4 — Découvrir un autre programme, sans destination donnée

> « Vous avez envie d'essayer **autre chose** que ce que vous faites
> d'habitude. Voyez ce que l'application propose. »

*Ce qui est mesuré* : « Explorer » est-il atteignable **et reconnaissable** ?
Le filtre par zone est-il découvert **spontanément** ? (Ne pas le mentionner.
S'il n'est jamais ouvert, c'est la donnée.)

### T5 — Expliquer ce qui gouverne, puis revenir

> « À votre avis, **qu'est-ce qui décide** de ce que l'application vous montre
> ici ? »
> puis : « Revenez à ce que vous suivez en ce moment. »

*Ce qui est mesuré* : le modèle mental. `C8` interdit tout moteur opaque — si
le participant croit que l'application « choisit pour lui » ou « apprend de
lui », **la contrainte est violée en perception**, quelle que soit la vérité du
code. La seconde moitié mesure le retour au plan sans le nommer.

### Après chaque surface majeure

Dès que le participant quitte une surface (Mon plan, Mes programmes, Explorer,
Profil), poser **exactement** :

> **« À quoi sert cette page ? »**

Noter la réponse **verbatim**. C'est la mesure la plus dense du protocole :
elle dit si l'architecture d'information tient dans la tête de quelqu'un
d'autre que celle qui l'a conçue.

---

## 4. Grille de relevé — une par participant

### Verdict par tâche

| Verdict | Définition opérationnelle |
|---|---|
| **SUCCESS** | atteint la bonne surface et accomplit la tâche **sans aide**, sans détour majeur |
| **HESITATION** | y arrive seul, mais avec arrêt visible, retour en arrière, ou verbalisation de doute |
| **RESCUE** | n'y arrive pas seul ; le modérateur a dû donner un indice pour poursuivre |
| **FAIL** | n'y arrive pas, même avec indice, ou accomplit **autre chose** en croyant avoir réussi |

Un `RESCUE` est un échec de l'interface, pas du participant. Le noter sans
adoucir, et **noter l'indice donné** — l'indice décrit ce qui manquait.

### Feuille par participant

```
PARTICIPANT ..........  Indépendant du produit : oui / non
Appareil ................................  Date ..............

T1  configuration persistante
    verdict         SUCCESS / HESITATION / RESCUE / FAIL
    première action ..............................................
    destinations erronées ........................................
    retours en arrière (nb) ......
    verbatim .....................................................

T2  modifier un paramètre
    verdict         SUCCESS / HESITATION / RESCUE / FAIL
    première action ..............................................
    conséquence ATTENDUE (avant de regarder) .....................
    conséquence CONSTATÉE ........................................
    écart ? ......................................................

T3  ses propres programmes
    verdict ......  première action ..............................
    destinations erronées ........................................
    confusion Mon plan / Mes programmes / Explorer ? .............

T4  découvrir autre chose
    verdict ......  première action ..............................
    filtre par zone découvert SPONTANÉMENT ?  oui / non
    verbatim .....................................................

T5  ce qui gouverne + retour
    « qu'est-ce qui décide ? » verbatim ..........................
    croit-il à un choix automatique ?  oui / non
    retour au plan : verdict ......

« À QUOI SERT CETTE PAGE ? » — verbatim
    Mon plan .....................................................
    Mes programmes ...............................................
    Explorer .....................................................
    Profil .......................................................

MALENTENDUS SÉMANTIQUES relevés
    ..............................................................
```

---

## 5. Ce qu'on regroupe après, et comment

Le regroupement se fait **une fois les cinq séances terminées**, jamais en
cours de série.

1. **Compter les verdicts** par tâche. Une tâche avec ≥ 2 `RESCUE`/`FAIL` sur 5
   est un défaut d'interface, pas une variation individuelle.
2. **Regrouper les premières actions.** Si trois personnes commencent au même
   mauvais endroit, cet endroit **porte une promesse qu'il ne tient pas** — et
   c'est un résultat plus actionnable que n'importe quel avis.
3. **Regrouper les réponses à « à quoi sert cette page ? »** par surface. Deux
   réponses incompatibles pour la même page = un problème de nommage ou de
   contenu, à trancher.
4. **Isoler les écarts attendu/constaté** de T2 : ce sont des ruptures de
   promesse, la catégorie la plus coûteuse.
5. **Compter combien croient à un moteur automatique** (T5). C'est la mesure de
   conformité perçue à `C8`.

**Ne rien corriger avant la revue.** Un défaut vu chez P1 et jamais revu chez
P2–P5 n'est pas prioritaire ; on ne le saura qu'à la fin.

---

## 6. Ce que l'étude ne peut pas dire

* Elle ne mesure pas la **rétention** ni l'usage réel dans la durée.
* Cinq personnes donnent des **défauts d'interface**, pas des proportions :
  écrire « 3/5 ont échoué », jamais « 60 % des utilisateurs échouent ».
* Elle ne juge pas l'esthétique. Aucune tâche ne demande un avis visuel, et une
  remarque esthétique spontanée se note sans être sollicitée ni relancée.

---

## 7. État de sortie

L'étude s'arrête à **`PROGRAMS REAL-USER DOGFOOD — OPERATOR REVIEW`**.

Aucune tranche de fonctionnalité ne démarre avant cette revue, y compris les
corrections que l'étude aura rendues évidentes.
