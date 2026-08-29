# `DF-E` — ouvrir un exercice, c'est l'activer

`OPERATOR_DECISION` — listing consolidé de la console de séance, points **7, 8
et 9** · branche `sb/df-e-exercise-activation` · base `32cf5ee`

---

## 1. Le défaut, tel que la mesure l'a trouvé

Trois notions étaient portées par un seul contrôle :

| Notion | Porteur | Qui pouvait la changer |
|---|---|---|
| carte dépliée | `<details open>` | **n'importe quel toucher**, côté client |
| exercice actif | `?active=<id>` | le serveur seul |
| « je veux travailler ici » | — | **rien ne l'exprimait** |

`?active=` gouverne **tout** : les lignes saisissables, la commande dominante
et `Adapter` sont derrière `{% if is_active and cs %}`. Toucher une carte
repliée satisfaisait la première notion et pas la seconde.

### Ce que j'avais annoncé, et ce qui était vrai

J'ai d'abord dit à l'opérateur qu'une carte non active rendait « un talon,
sans champs ni `Adapter` ». **C'était faux, et dans le mauvais sens.** Elle
rendait une **liste plate complète** — champs `kg`/`reps` pour chaque série,
« Dernière fois », delta, lien d'historique — mais avec les libellés
`Échauf. #1` / `Série #2` que `Q4` puis `DF-C` avaient précisément remplacés,
sans `Adapter`, sans console, sans validation implicite.

Ce n'était pas un talon : c'était une **seconde interface** pour le même
exercice, et laquelle des deux on obtenait dépendait du **chemin d'arrivée**.

Le sélecteur `E1/7` de l'en-tête aggravait le tout : ses liens étaient
`href="#exercise-N"`, des **ancres pures**. « Aller à un exercice » nommait
une action que le lien n'accomplissait pas.

---

## 2. Brainstorming · options · risques · choix (`CLAUDE.md §3`)

| | Approche | Verdict |
|---|---|---|
| **A** | Réparer seulement les liens du sélecteur | **Insuffisant** — le toucher direct sur une carte continue de produire l'ancienne interface. Un chemin sur deux |
| **B** | Rendre la console sur **toutes** les cartes | **Rejeté** — contraire à `Q4` (« un exercice à la fois »), et sept consoles explosent la page |
| **C** ✅ | **La carte repliée devient un lien d'activation** | **Retenu** |
| **D** | Intercepter le `toggle` en JS | **Rejeté** — casse le repli sans JS, propriété vérifiée en `DF-B` ; et l'incident du script périmé a prouvé qu'un JS peut silencieusement ne pas tourner |

### Pourquoi C, et pas A

C est le seul choix où **le défaut ne peut pas revenir**. A répare deux
chemins ; C supprime la possibilité même de divergence : dans une séance en
cours, il n'existe plus qu'un seul `<details>` d'exercice — l'actif. L'état
« ouvert mais pas actif » n'a plus de représentation.

**Ce n'est pas une garde qui surveille le défaut, c'est une structure où il
ne s'écrit plus.** C'est le système anti-drift demandé.

---

## 3. Preuve d'exécution — la séquence de l'opérateur

Séquence réelle jouée par un navigateur, **en suivant les contrôles** et non
en fabriquant des URL : arriver sur E1 → toucher la carte E2 → revenir sur E1
par le sélecteur de l'en-tête.

| Étape | Chromium | WebKit |
|---|---|---|
| arrivée | E1 actif · 6 liens d'activation · 1 `<details>` | idem |
| toucher la carte E2 | `?active=357` · **E2 actif** · `Adapter` présent · champs saisissables | idem |
| retour E1 par le sélecteur | `?active=356` · **E1 actif** · `Adapter` présent · champs saisissables | idem |
| listes plates / codes legacy | **0 / 0** | **0 / 0** |
| erreurs console | aucune | aucune |

> **Playwright WebKit n'est pas Safari iOS** : même famille de moteur, ni le
> même navigateur, ni le même système.

**Points 7, 8 et 9 tenus.**

---

## 4. Le point 8 n'avait besoin d'aucune règle neuve

`can_substitute` est une règle de **données** — « aucune série de travail
complétée » — et elle ne dépend d'aucune navigation. `Adapter` disparaissait
non parce que la règle changeait, mais parce qu'il n'était rendu que sur la
carte active et qu'on ne savait plus la redevenir.

Le point 8 découle donc entièrement du point 7. Une garde vérifie **l'inverse
aussi** : `Adapter` doit toujours disparaître une fois une série de travail
faite. Rendre une capacité plus durable ne doit pas la rendre permanente.

---

## 5. Exposition `§5.1` — densité mesurée, et ce qu'elle coûte

360 / 390 / 430 px, `device_scale_factor=3`.

| | mesure | avant |
|---|---|---|
| liens d'activation | 6 | — |
| CTA de la page (DOM) | 4 | 16 |
| densité | **4,4 / 4,1 / 3,6 écr** | 3,5 / 3,3 / 2,8 |
| débordement horizontal | **aucun** | aucun |
| cibles < 44 px | **aucune** | 5, puis 0 après `DF-C` |
| cible d'activation, la plus petite | **109 px** | — |

### ⚠ Un chiffre que j'ai d'abord annoncé faux

J'ai écrit à l'opérateur « **les CTA passent de 16 à 4** ». **C'est trompeur.**
Mon compteur balayait le **DOM** (`main button, main a.btn, main .dock__cmd`),
pas les contrôles **visibles** : les douze boutons des cartes repliées vivaient
dans des `<details>` **fermés**. L'utilisateur n'en a jamais vu seize.

Douze éléments interactifs quittent bien le DOM — ce qui compte pour la
navigation au clavier et les technologies d'assistance — mais **le nombre de
CTA visibles ne change pas**. Le gain de cette tranche est l'activation, pas
une simplification du dock.

### La densité, elle, augmente vraiment

**3,5 / 3,3 / 2,8 → 4,4 / 4,1 / 3,6 écrans.** C'est le prix de trois
informations qui étaient **enfermées dans un repli** et deviennent visibles :
« Dernière fois », le delta, le lien d'historique. Elles n'ont pas été ajoutées
— elles ont cessé d'être cachées derrière un geste qui produisait par ailleurs
la mauvaise interface. **Arbitrage soumis** (§9).

---

## 6. Trois soustractions, et comment elles ont été trouvées

En faisant de la carte non active un lien, j'ai supprimé son corps — donc trois
choses qui y vivaient : **« Dernière fois »**, le **delta**, et le **lien
d'historique**.

**Aucune n'a été trouvée par moi.** Ce sont les gardes du dépôt qui les ont
dites, et en deux temps :

| Trouvée par | Ce que j'avais perdu | Pourquoi je l'avais manqué |
|---|---|---|
| `test_last_time.py` — 5 gardes | « Dernière fois » | je cherchais `last-time`, la **classe CSS** ; elles assertent le **texte** français |
| `test_exercise_history.py` — 2 gardes | delta + lien d'historique | **le sweep ciblé ne couvrait pas ce fichier** ; seul le sweep complet l'a vu |

Les deux avaient été **explicitement protégées** par des tranches précédentes,
commentaires à l'appui dans la branche que je supprimais : « le delta existait
sur TOUTES les cartes, le restreindre à la console active l'aurait retiré des
exercices déjà faits, où il est précisément la lecture utile » · « l'accès à
l'historique existait sur toutes les cartes ».

**Toutes trois sont restituées.** La carte repliée est devenue un **conteneur** :
le lien d'activation, puis le delta et l'historique en **frères** — un `<a>` ne
peut pas en contenir un autre, et le navigateur en ferait n'importe quoi.

> La puce porte le **schéma** et la **date** ; « Dernière fois » porte les
> **valeurs** (`60 / 62.5 kg`). Ce ne sont pas les mêmes informations.

Elles y sont **plus utiles qu'avant** : elles vivaient dans un corps replié
qu'il fallait ouvrir — donc quitter la console — pour les lire. Elles sont
maintenant lisibles sans rien ouvrir. **Coût : ~0,9 écran** (§5), soumis à
arbitrage.

### La leçon d'opération

Mon sweep ciblé couvrait quinze fichiers de l'écran de séance et il était
**vert**. Le sweep complet a fait tomber **dix gardes dans cinq fichiers** que
je n'avais pas pensé à inclure — dont deux capacités réelles. `check_scope`
annonçait `ISOLATED` ; le blast radius réel touchait `test_exercise_history`,
`test_overload_placeholder`, `test_session_focus_accessibility`,
`test_session_focus_sticky_cta` et `test_uiv2_session_focus_contract`.

**Un sweep ciblé ne borne pas un rayon d'impact : il borne ce qu'on a pensé à
regarder.**

---

## 7. Ce qui a été supprimé, et pourquoi ce n'en est pas une

La branche « carte non active » du gabarit (84 lignes) est supprimée. Elle
était devenue **inatteignable** : le `<details>` ne s'écrit plus que pour
l'exercice actif, et `console_states` est construit pour tous les exercices —
donc `cs` n'est jamais nul.

Elle n'est pas laissée morte, et c'est délibéré : **un second écran
inatteignable dans le même fichier est exactement ce qui fait revenir le
défaut.** Il suffirait de rétablir un `<details>` pour les cartes non actives
et le vieil écran ressusciterait. Une garde le verrait ; mieux vaut qu'il n'y
ait rien à ressusciter.

**Reste dans les feuilles de style** : `.set-list--compact`, `.last-time`
(partiellement réemployée), `.set-row__kind`. Nettoyage CSS **hors périmètre**,
consigné.

---

## 8. Fautes de l'agent

1. **J'ai décrit le défaut à l'envers.** « Un talon sans champs » — c'était une
   interface complète et concurrente. Le diagnostic s'en trouvait affaibli, pas
   renforcé.
2. **Deux gardes ne gardaient rien, et je l'ai vu en plantant.**
   `test_coming_back_…` et `test_adapter_…` fabriquaient l'URL `?active=N`
   elles-mêmes. Or **le routeur l'a toujours honorée** : le défaut n'a jamais
   été là. Avec l'activation intégralement rétablie à l'ancien comportement,
   ces deux gardes restaient **VERTES**. Elles passent désormais par les
   **contrôles réellement rendus** — 9 gardes sur 12 rougissent au défaut
   d'origine.
3. **Une condition défensive sur un cas qui n'arrive pas.** J'avais écrit
   `status != 'completed'` « au cas où ». Mesuré : une séance terminée
   **redirige** (303) vers `/sessions/{id}/done`, qui n'inclut pas ce gabarit.
   La condition n'était jamais évaluée — le motif exact qui a produit onze
   gardes vertes sans comportement dans ce dépôt.
4. **Une recherche trop étroite** m'a fait croire que rien ne dépendait de
   « Dernière fois » (§6).
5. **Un découpage de gabarit faux**, qui coupait au premier `</details>`
   imbriqué et me faisait conclure que la carte active n'avait pas
   d'historique. Elle en a un.
6. **Une factorisation mécanique qui a introduit un vrai bug** : en hoistant
   `"/sessions"` j'ai écrit `"/sessions/"`, et le POST de création a cessé de
   fonctionner. Les tests l'ont attrapé immédiatement.
7. **Un chiffre trompeur donné à l'opérateur** : « les CTA passent de 16 à 4 ».
   Comptage du **DOM**, pas des contrôles **visibles** — les douze boutons des
   cartes repliées étaient dans des `<details>` fermés. Corrigé au §5.
8. **Un sweep ciblé pris pour une couverture** : quinze fichiers, tous verts, et
   le sweep complet a trouvé dix gardes rouges dans cinq fichiers absents de ma
   liste — dont deux capacités réelles supprimées (§6).

**L'enseignement dominant est le n°2**, et il prolonge `DF-C` : une garde qui
construit elle-même l'état qu'elle observe ne teste que le serveur. Le défaut
vivait dans ce que l'écran **propose** — il fallait partir du HTML rendu et
suivre les liens.

---

## 9. Arbitrages soumis — non tranchés

1. **Densité** : « Dernière fois » + delta + historique, rendus visibles sur
   six cartes, coûtent **~0,9 écran** (3,5 → 4,4 à 360 px). Les garder visibles,
   ou les remettre derrière un repli — sachant que le repli était précisément le
   geste qui produisait la mauvaise interface ?
2. **Redondance** : la puce dit « première fois » et la ligne dit « aujourd'hui
   · aucune donnée saisie ». Les deux existaient avant, jamais **côte à côte**.
3. **`VALIDER É1`** — arbitrage de `DF-C`, toujours ouvert.

---

## 10. Hors périmètre

* **Point 6, réserve** : `PASSER À E{n}` reste absent du dock **pendant** le
  repos (les secondaires y sont `−15 s` / `+15 s`). Mais les autres exercices
  sont désormais atteignables pendant le repos par leur carte — une garde le
  vérifie. La réserve est **close par effet de bord**, pas par une commande.
* **Nettoyage CSS** des classes de l'ancienne interface.
* **`DF-D`** — repos adaptatif : tranche suivante.
