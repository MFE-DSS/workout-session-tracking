# `AUREN_UI_NIGHT_PASS` — la passe critique de nuit

> **Nuit du 2026-09-04 au 05, en autonomie.** Mandat opérateur : appliquer à
> tous les objets de l'application la philosophie validée sur le viseur `M3`,
> avec `GO MERGE` explicite et l'autorisation de prendre mes recommandations
> comme décisions.
>
> **À lire dans l'ordre : ce qui a été mergé · ce qui a été trouvé · ce qui
> reste ouvert · ce que je n'ai pas pu faire.**

---

## 1. Ce qui a été mergé

| PR | Tranche | Gate vérifié |
|---|---|---|
| `#183` | socle de **25 rôles** de couleur, aliasés sur les valeurs mesurées | checks verts · Sonar `OK` · 0 fil · `CLEAN` |
| `#184` | **relief** surélevé ↔ creusé, grain par niveau | idem |
| `#185` | la **profondeur de la séance** — l'échelle mesurée y arrive enfin | idem |

Head épinglé à chaque merge, **aucun squash, aucun `--admin`**, aucune branche
ni worktree supprimé — le cleanup reste une décision séparée.

---

## 2. Cinq défauts trouvés **en regardant**, qu'aucune garde ne voyait

Ce sont les plus importants de la nuit, et ils ont un point commun : **aucun
n'est visible en lisant le code.** Il fallait rendre l'écran.

### 2.1 « En cours · depuis 1502 h 16 » — accueil

`format_duration_short` est écrite pour une durée de séance et n'avait **aucune
borne haute**. Une séance laissée ouverte 62 jours rendait « 1502 h 16 » :
format juste, nombre exact, illisible.

Le défaut n'était pas dans l'arithmétique mais dans la **portée**. Un formateur
sans borne finit toujours par sortir de son domaine. Au-delà de 24 h on rend
des **jours**.

### 2.2 Une correction qui n'avait jamais atteint sa cible — accueil

`Sx_UIV3_01 Q5` a retiré le `min-height` du hero. Sa prose cite la mesure :
*« il réservait 44vh… 422 px dont 115 vides »*.

**La règle de base a été corrigée ; la règle mobile, non** — et c'est la seule
qui s'applique au viewport que la prose nomme. À 390 px, `50vh` vaut exactement
422 px. Donc la correction n'a jamais atteint sa cible, **et le vide avait
augmenté** (50vh > 44vh).

| | avant | après |
|---|---|---|
| hero | 422 px | **288 px** |
| vide | 152 px | **18 px** |
| page | 1580 px | **1442 px** |
| écrans | 1,87 | **1,71** |

> **C'est la deuxième fois** que ce dépôt voit un bloc scopé conserver en
> silence ce que la règle universelle a retiré. La garde neuve descend donc
> *dans* les requêtes média, avec une garde-de-garde qui échoue si le parcours
> cesse d'y descendre.

### 2.3 « ANOMALIE None » — progression

`_pick_top_anomaly` lisait **quatre attributs qui n'existent pas** sur
`Anomaly` : `code`, `label`, `session_exercise_id`, et par ricochet le nom de
l'exercice. Les `getattr(..., None)` rendaient l'absence **silencieuse** —
aucune exception, un dict bien formé, et le gabarit imprimait la chaîne
« None ».

**Toute anomalie jamais affichée sur cette surface l'a été sous le nom
« Anomalie None ».** Elle lit désormais :

> *Élévations latérales câble (derrière le dos) — Charge et reps croissent
> simultanément (set 1 : 80 kg × 8 → set 3 : 85 kg × 11). À vérifier.*

### 2.4 « 1 sessions » — progression

Accord manquant **et** anglicisme, dans une carte dont la sous-ligne disait
déjà « séance ». Deux mots pour une chose au même endroit.

⚠ **Le commentaire du test disait le défaut et le gardait** :
*« kept "sessions" so the existing assertions stay valid — see report
§limits »*. Un anglicisme a survécu dans le produit **parce qu'un test
l'épinglait**, et la chose a été consignée comme une limite plutôt que
corrigée.

### 2.5 Un second lien traversant une redirection héritée

La séance lie « Voir toutes les règles » vers `/rules`, qui répond **301** vers
`/science`. C'est `R-03` — le CTA de fin de séance vers `/dashboard` — à un
second endroit. **Deux occurrences font un motif**, pas un accident.

---

## 3. Ce que la revue complète a mesuré

18 surfaces capturées en écrans entiers, 390×844, routes énumérées **depuis les
routeurs** et non depuis une liste écrite à la main.

| surface | écrans | contrôles |
|---|---|---|
| `science` | **11,5** | 52 |
| `explorer` | 4,05 | **99** |
| séance | 3,16 | 82 |
| accueil | 1,71 | 72 |
| progression | 2,2 | 35 |

`science` est de loin la plus longue ; `explorer` la plus dense — treize cartes
identiques portant treize commandes « Démarrer », ce qui est le motif `X-01` à
pleine échelle, et exactement ce que `O-04` demande de trancher.

---

## 4. Deux fausses alertes, écartées après vérification

`/profile` renvoie 500 et `/body` 404 sur mon poste. **Ni l'un ni l'autre n'est
un défaut produit** : le 500 vient de ma copie de base, antérieure à une
migration (`body_measurements.shoulder_width_cm`) ; le 404 est le comportement
correct d'une surface derrière un drapeau éteint.

> ⚠ **Conséquence à dire : le profil n'a pas pu être revu.** C'est le seul trou
> de cette revue, et le dire vaut mieux que de laisser croire que tout est
> passé.

---

## 5. Trois leçons de méthode, payées cette nuit

**Un filtre `-k` est une hypothèse sur le rayon d'impact.** La mienne était
fausse : six gardes sont tombées en CI, dans des fichiers que le filtre ne
couvrait pas. Sur du `shared_code`, c'est le sweep complet qui tranche.

**Un laboratoire non représentatif fait juger un écran que la donnée rend
absurde.** Progression semblait n'être que « cinq blocs qui disent rien » —
c'était ma base, vieille de 62 jours. Avec des données récentes : plus une
seule ligne vide, et deux vrais défauts à la place.

**Ne pas muter l'arbre pendant qu'un sweep le lit.** Je l'ai fait ; le verdict
devenait ininterprétable. J'ai arrêté le sweep plutôt que d'en garder le
résultat.

---

## 6. Ce qui reste ouvert, et pour vous

* **`O-01`** — les trois rendus `U-01` à réexposer.
* **`O-02`…`O-05`**, **`T-01`…`T-06`**, **`N-01`…`N-04`**, **`X-01`…`X-05`** —
  arbitrés par mes recommandations, non encore implémentés.
* **`R-03`** — la destination après une séance ; le CTA traverse toujours
  `/dashboard`.
* **Deux anglicismes en DONNÉE**, pas en affichage : le gabarit nommé
  « Session courte — Full upper 45 min », et `kind = strength` rendu
  `STRENGTH`. Le second est un correctif d'affichage ; le premier est une
  décision de contenu, donc la vôtre.
* **Le profil**, non revu.

---

## 7. Addendum — seconde moitié de la nuit

Cette section couvre ce qui s'est passé **après** l'écriture des six premières.
Le rapport ci-dessus a été mergé avec `#187` ; il ne mentionnait donc ni `#186`,
ni les deux trouvailles obtenues en changeant de méthode.

### 7.1 J'ai arrêté de regarder les écrans un par un

Les cinq défauts de la §2 ont été trouvés en **regardant** des rendus. C'est
lent, et surtout ça ne dit rien sur ce que je n'ai pas ouvert. À partir du
milieu de la nuit j'ai balayé les **classes** de défaut sur tout le dépôt.
Trois balayages, trois verdicts nets :

| Classe balayée | Verdict |
|---|---|
| **Absence rendue silencieuse** (`getattr(o,"x",None)` sur un attribut inexistant) — la cause d'« ANOMALIE None » | 64 occurrences, **aucune** ne lit un nom absent du dépôt. Classe **close**. ⚠ Le contrôle attrape les noms absents *partout* ; il ne verrait pas un nom qui existe sur une *autre* classe. |
| **Décision opérateur appliquée partiellement** | **1 trouvée** — `D7`, ci-dessous. La plus grave de la nuit. |
| **§5.4, couleur hors token** | **88 occurrences, 30 couleurs** — la plus lourde en volume. |

### 7.2 `D7` — une décision à vous, appliquée sur 2 surfaces et oubliée sur 4

`OPERATOR_DECISION D7` a retiré « Streak ». Le motif écrit dans le dépôt est un
motif **produit** : *« le compteur de jours consécutifs punissait un jour de
repos correctement pris »*.

Elle a été appliquée au rapport coach et à Progression. **Quatre surfaces le
rendent encore** : `squad_detail`, `squad_compare`, `profile_preview`,
`user_profile` — **les quatre surfaces sociales**, celles que les autres voient
de vous. Sur un classement d'escouade, un compteur qui punit un repos bien pris
fait du repos un désavantage compétitif **public**. La décision a été appliquée
aux surfaces intimes et oubliée sur les sociales : l'inverse de l'ordre de
priorité.

Les deux gardes de `D7` existent — **et chacune ne regarde qu'un gabarit.** La
garde existe, elle ne regarde pas où est le défaut.

La décision soupçonnait « un second producteur » ; il y en a **trois**.
Vérifié : `streak` ne pèse pas sur le classement, qui se calcule sur les points.

### 7.3 Une seconde palette, non mesurée, vit à côté de la vôtre

**30 couleurs littérales, 88 occurrences**, hors du système de tokens. Ce n'est
pas une dispersion : c'est la **palette par défaut de Tailwind**, nuance par
nuance (`gray-500`, `blue-600`, `amber-500/600/800`, `green-400/600/800`).

La mesure qui tranche : votre palette validée vit entre **20 % et 51 % de
saturation**. Onze des clandestines sont à **S ≥ 56 %, jusqu'à 100 %**.

**Cinq tokens n'existent nulle part** — leur repli est donc littéralement ce qui
est rendu, exactement le piège que §5.4 nomme. Dont
`--bg-elev → rgba(0,0,0,0.02)` : un film **noir** posé pour créer une élévation,
sur un produit **sombre**. Invisible par construction — il a été écrit pour un
thème clair.

**Je ne les ai pas remplacées**, et c'est délibéré : elles vivent sur des
surfaces que vous n'avez pas vues et que je n'ai pas revues. §5.1 exige une
exposition avant tout commit UI, et §5.5 dit que la centralité prime. Le
recensement est le livrable ; l'arbitrage est le vôtre.

### 7.4 Une garde à moi, tombée pour la bonne raison

`python:S1192` a signalé cinq copies de `"var(--accent)"` dans `timeline.py`. La
règle avait raison **ici plus qu'ailleurs** : le défaut que ce module venait de
corriger — la légende qui ne décrivait pas son graphique — était né exactement
de ça, d'une valeur recopiée à un endroit et changée à l'autre.

Extraire la constante a fait tomber `test_the_chart_consumes_the_tokens_of_its_own_legend`
— **une garde que j'avais écrite quelques heures plus tôt**. Elle lisait le
*texte source* du dictionnaire, pas sa *valeur*. La valeur rendue n'avait pas
bougé d'un caractère.

C'est la faute que je documentais depuis la veille dans le code des autres,
commise par moi, dans le même fichier, la même nuit. Elle lit désormais le
dictionnaire résolu. Plantation vérifiée : trois gardes mordent.

### 7.5 Le balayage local, cette fois, a mesuré la bonne chose

`77/77` lots · `307/307` fichiers · **5 720 tests, 0 échec** · pics 0,2 à 1,3 Go.

Lancé **depuis le worktree** — la correction du défaut de §5 : depuis le
répertoire canonique, `app` se résout sur le dépôt canonique et le sweep mesure
un autre code que celui de la branche.
