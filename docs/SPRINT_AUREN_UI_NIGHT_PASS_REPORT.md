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
