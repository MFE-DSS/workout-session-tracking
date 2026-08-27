# `STATIC_ASSET_COHERENCE_01` — le HTML et ses assets évoluent ensemble

`OPERATOR_DECISION` · branche `sb/static-asset-coherence-01` · base `915a3ab`

---

## 1. Ce qui est prouvé, et ce qui ne l'est pas

Le verdict opérateur borne l'attribution, et cette tranche la respecte :

| Énoncé | Statut |
|---|---|
| Un script périmé a causé l'incident de l'iPhone | **NON PROUVÉ** — cache de l'appareil non observé |
| L'architecture de déploiement **permet** un décalage HTML ↔ JS | **PROUVÉ**, reproduit |

Rien dans ce document ne prétend expliquer la soirée du 26 août. Il ferme une
**possibilité structurelle**, et cette possibilité est démontrée.

---

## 2. Le défaut, reproduit avant d'être fermé

Deux versions du même script cherchent deux attributs différents :

| Version | Cherche | En production |
|---|---|---|
| `9b41fa3` | `[data-start-rest]` | du 18 au 26 août |
| `915a3ab` | `[data-rest-started]` | depuis le 26 août |

Le HTML actuel n'émet plus que le second. Un client détenant l'ancien script
trouve **zéro racine** et sort par un `return` silencieux — **avant** la ligne
`btn.hidden = false` qui révèle les `±15 s`.

Banc adverse, ancien script servi contre le HTML actuel :

```
[t0]       1:30   ±15 masqués   « Repos en cours »
[t+2,6 s]  1:30   ±15 masqués   « Repos en cours »
```

**Les deux symptômes du dogfood, d'un seul mécanisme.** Aucune erreur console,
aucun 404 : le défaut est parfaitement silencieux.

Ce qui rendait ce décalage possible :

* URL **sans version** — `/static/js/session_focus.js`, ni hash ni paramètre ;
* **aucun `Cache-Control`**, ni `Expires` — seulement `ETag` et
  `Last-Modified`, donc une fraîcheur *heuristique* laissée au navigateur.

**Le défaut n'appartenait pas au minuteur.** Il appartenait au couplage HTML ↔
asset. Corriger le seul `session_focus.js` aurait laissé la mine en place pour
le prochain changement de contrat — c'est pourquoi l'ordre l'interdisait.

---

## 3. Brainstorming / Options / Risques / Choix retenu (`CLAUDE.md §3`)

### Options examinées

**Option A — empreinte de contenu en chaîne de requête.** *(retenue)*
`/static/js/session_focus.js?v=<sha256 tronqué>`.
· *Pour* : aucune étape de build, aucun fichier dupliqué, le montage
`StaticFiles` existant sert le fichier réel. La chaîne de requête fait partie
de la clé de cache pour tout navigateur.
· *Contre* : quelques CDN anciens ignorent la chaîne de requête. Il n'y a pas
de CDN ici — l'app est servie directement depuis le VPS.

**Option B — nom de fichier haché** (`session_focus.<hash>.js`).
· *Pour* : la forme la plus robuste, insensible aux caches exotiques.
· *Contre* : impose une **étape de génération** que ce dépôt n'a pas. Une étape
de build qu'on oublie de lancer est **le même défaut sous un autre nom** — et
c'est exactement le mode de défaillance qu'on retire. Rejetée.

**Option C — numéro de version manuel** (`?v=7`).
· *Contre* : un humain qui oublie de l'incrémenter reproduit l'incident à
l'identique. L'ordre l'exclut explicitement. Rejetée.

### Risques identifiés avant d'écrire, et ce qui les couvre

| Risque | Couverture |
|---|---|
| Une référence **échappe** à l'autorité | garde qui balaie **tous** les gabarits |
| L'empreinte **cesse de suivre** le contenu | garde comportementale : le fichier est réellement modifié |
| L'empreinte **change sans raison** (cache invalidé à chaque déploiement) | garde : cache vidé, URL identique |
| Le hachage coûte une lecture disque **par balise et par page** | mémorisation invalidée par `(mtime_ns, taille)` |
| Un asset **absent** rend une balise morte | `AssetNotFound` levée, garde d'existence |

### Choix retenu

**Option A**, avec l'empreinte dérivée du contenu et **aucun** incrément
manuel.

---

## 4. Ce qui a changé

| Fichier | Nature |
|---|---|
| `app/services/static_assets.py` | **neuf** — l'autorité : `asset_url`, `fingerprint`, `is_fingerprinted` |
| `app/templating.py` | `asset_url` exposé comme global Jinja |
| `app/main.py` | `_apply_cache_semantics` — trois régimes explicites |
| 9 gabarits | **12 références** migrées vers l'autorité |
| `tests/test_static_asset_coherence.py` | **neuf** — 14 gardes |

**Aucune migration, aucun changement de schéma, aucune étape de build.**

### Sémantique de cache, telle qu'exigée

| Ce qui est servi | `Cache-Control` |
|---|---|
| Asset **empreint** | `public, max-age=31536000, immutable` |
| Asset **nu** (icône, manifeste, URL tapée à la main) | `no-cache` — donc revalidation |
| **HTML authentifié** | `private, no-cache` |

`immutable` n'a de sens **que** parce que l'URL porte une empreinte : si le
contenu change, l'URL change, et cette entrée cesse d'être demandée. Une route
qui pose déjà son propre `Cache-Control` n'est jamais écrasée.

---

## 5. Gardes plantées

**14 gardes · 7 défauts plantés, 7 rouges** : une référence échappe à
l'autorité · l'empreinte cesse de suivre le contenu · l'empreinte devient non
déterministe · l'asset empreint perd son immutabilité · l'asset nu repart sans
directive · le HTML authentifié perd sa politique · on empreint ce qui n'a pas
de contrat.

### Deux gardes qui passaient pour la mauvaise raison

1. **La garde de la surface d'incident interrogeait `/`** — une page qui ne
   charge même pas le script du minuteur. Elle passait **à vide**, sans jamais
   regarder la page concernée. Elle ouvre désormais une vraie séance et vérifie
   que le script y est référencé **avec** empreinte.
2. **`assert asset_url(x) == asset_url(x)`** est une tautologie : elle ne
   prouvait que la mémoïsation. Signalée par `python:S5863`, et le signalement
   était juste. La garde **vide maintenant le cache interne** entre les deux
   lectures — c'est ainsi qu'un redémarrage de processus se comporte
   réellement.

---

## 6. Exposition exigée

### 6.1 — URL d'assets rendues (page de séance)

```
/static/css/app.css?v=e3b66d7de6f7
/static/css/interaction.css?v=b113212fe089
/static/css/session_focus.css?v=ce20b2a65a4b
/static/css/target_closure.css?v=4cc57565f727
/static/js/session_focus.js?v=26a2d317a192
```

### 6.2 — En-têtes de cache des réponses

```
asset EMPREINT         200  public, max-age=31536000, immutable
asset NU               200  no-cache
icône (hors contrat)   200  no-cache
HTML authentifié       200  private, no-cache
```

Avant la tranche, ces quatre lignes étaient **`— ABSENT —`**.

### 6.3 / 6.4 — Séquence de repos réelle, deux moteurs

Séquence complète : échauffements (`stay_norest`, sans repos) → première série
de travail (`stay`) → `?rest=1`.

| Moteur | t0 | t+2,6 s | `±15 s` |
|---|---|---|---|
| **Chromium** | 1:30 | **1:27** | visibles |
| **Playwright WebKit** | 1:30 | **1:27** | visibles |

> ⚠ **Playwright WebKit n'est pas Safari iOS.** Même famille de moteur, mais ni
> le même navigateur, ni le même système, ni la même politique de cache. Ce
> relevé ne prouve rien sur l'appareil de l'opérateur.

### 6.5 — Reproduction adverse, avant / après

| | t0 | t+2,6 s | `±15 s` |
|---|---|---|---|
| **Avant** (script périmé, URL nue) | 1:30 | **1:30** | masqués |
| **Après** (script courant, URL empreinte) | 1:30 | **1:27** | visibles |
| **Après, ancien script forcé par interception** | 1:30 | **1:30** | masqués |

La troisième ligne mérite d'être lue exactement. Le banc **force** l'ancien
script en interceptant la requête : il montre que le mécanisme est bien
celui-là. Ce qui change après la tranche, c'est qu'un **navigateur ne peut plus
produire cette situation seul** — l'URL demandée porte une empreinte que
l'ancien fichier n'a jamais eue, donc son entrée de cache ne correspond à
aucune requête émise par le HTML à jour.

---

## 7. Attribution historique

**`PROBABLE — CACHE APPAREIL NON OBSERVÉ`**, inchangé.

Le test qui trancherait est sur l'appareil : ouvrir une séance en navigation
privée (ou après effacement des données de site) et valider une série de
travail. Si le compteur décompte alors qu'il était figé, l'attribution devient
certaine. Ce test appartient à l'opérateur ; aucune mesure de ce dépôt ne le
remplace.

---

## 8. Vérifications (`CLAUDE.md §1`)

| Vérification | Résultat |
|---|---|
| `check_scope.py` | **`SHARED_CODE`** |
| Sweep ciblé, 12 fichiers consommateurs | **232 passés, 0 échec** |
| `tests/test_static_asset_coherence.py` | **15 passés** |
| **Full sweep local** (arbre stable) | **287/287 fichiers, 85 lots, tous verts** · pic 1967 Mo / 1998 de budget · 1 adaptation automatique, aucun fichier sauté |
| ruff (rapport CI reproduit) | **276 avant / 276 après** — 2 `I001` introduits puis corrigés |

**Aucune surface visible modifiée** : pas de gabarit rendu différemment, pas de
feuille de style changée. Les URL changent, pas les pixels. `CLAUDE.md §5.1`
ne s'applique donc pas — et les deux relevés de runtime ci-dessus valent
davantage qu'une capture, puisque le sujet est un comportement dans le temps.

---

## 9. Fautes de l'agent

### 9.1 — Deux gardes passaient pour la mauvaise raison

* **Une garde interrogeait `/`** — une page qui ne charge même pas le script du
  minuteur. Elle passait **à vide**, sans jamais regarder la surface de
  l'incident. Elle ouvre désormais une vraie séance.
* **`assert asset_url(x) == asset_url(x)`** — tautologie qui ne prouvait que la
  mémoïsation. Signalée par `python:S5863`, et le signalement était juste. La
  garde vide maintenant le cache interne entre les deux lectures.

### 9.2 — J'ai décrit une politique que la production n'applique pas

J'avais rédigé le §4 en présentant la sémantique de cache applicative comme
celle de la production. **Faux** : nginx sert `/static/` depuis le disque, la
requête n'atteint jamais FastAPI. Seul l'examen de la configuration documentée
l'a montré — aucun test applicatif ne pouvait le révéler, puisqu'ils
interrogent l'application.

C'est la même famille d'erreur que le reste de la session : **un instrument
qui mesure autre chose que ce qu'on croit**. Ici, la suite de tests mesurait
fidèlement une politique qui, en production, est court-circuitée.

### 9.3 — J'ai muté l'arbre de travail pendant qu'un sweep le lisait

`git stash` puis `git stash pop` pour relever la ligne de base ruff, **pendant
qu'un full sweep tournait**. Un lot a été exécuté sur un état transitoire et a
rendu un faux `'asset_url' is undefined`. Le fichier passe seul et avec ses
voisins ; le sweep relancé sur arbre stable est **287/287 vert**.

Règle : **ne jamais toucher à l'arbre de travail pendant qu'un sweep le lit.**
Un sweep lit des fichiers, pas un instantané.

---

## 10. Closeout post-merge

| | |
|---|---|
| PR | **#169** |
| Merge | **`faa4208`** — `--merge`, tête épinglée `bb37c84`, **pas de squash, pas de `--admin`, pas de force** |
| CI de PR | 9/9 `pass`, **aucun cycle rouge** |
| CI canonique (`push` sur le merge) | run **33062160377** — **succès** |
| Sonar (gate PR) | **OK** — couverture neuve **95,7 %** · 0 bug · 0 code smell · 0 vulnérabilité |
| Fils de revue non résolus | 0 |

### Reste à l'opérateur

1. **Appliquer le bloc nginx corrigé sur le VPS.** Le dépôt ne fait que le
   documenter ; tant que `expires 7d` vit sur le serveur, les assets **nus**
   (icônes, manifeste) gardent l'ancien régime. Les assets **empreints**, eux,
   sont déjà sûrs : leur URL change avec leur contenu, quelle que soit la durée
   de cache.
2. **Le test appareil** qui trancherait l'attribution : séance en navigation
   privée, valider une série de travail, observer le décompte.

L'attribution de l'incident reste **`PROBABLE — CACHE APPAREIL NON OBSERVÉ`**.
