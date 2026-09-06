# Sb_UI_JS_CAPACITY_GUARD_01 — seize inventaires JS deviennent une propriété

**Tier `check_scope`** : `ISOLATED` — sweep remonté d'un cran, `tests/helpers.py`
étant importé par 64 fichiers de tests.
**Fichiers** : 17 fichiers de `tests/`, dont `tests/helpers.py`. **Zéro fichier
d'application.**

---

## 1. Le verrou — et son vrai nombre

La tranche devait retourner **une ligne**. Le plan disait : *« `tests/test_home_
decision_hero.py:344` interdit tout quatrième fichier JS par un inventaire exact
du répertoire. Une ligne, et le chemin de l'étape suivante est ouvert. »*

C'était faux, et de quinze.

```python
assert js_files == ["prefs_focus_rank.js", "preview.js", "session_focus.js"]
assert existing <= {"prefs_focus_rank.js", "preview.js", "session_focus.js"}
assert existing == {"prefs_focus_rank.js", "preview.js", "session_focus.js"}
assert names == ["prefs_focus_rank.js", "preview.js", "session_focus.js"]
```

**Seize gardes, quatre formes d'assertion, seize fichiers.** Sous chacune des
quatre formes, un quatrième script fait échouer la suite. Corriger la première
et livrer aurait laissé **quinze verrous en place** — avec un rapport annonçant
le contraire.

### Comment les quinze autres ont été trouvées

En deux temps, et le second est le seul qui a suffi :

1. **Par NOM** (`grep "def test_no_new_js"`) → **14**. C'est ce que j'aurais
   livré.
2. **Par CLASSE** — une garde AST qui cherche *toute fonction comparant la liste
   du répertoire JS à une constante* → **16**. Les deux manquantes ne portaient
   pas `no_new_js` dans leur nom :
   * `test_session_focus_rest_timer.py::test_no_unexpected_js_file_introduced`
   * `test_ui_profile_preferences.py::test_the_canonical_js_inventory_is_exactly_three_files`

La seconde se présentait comme **l'inventaire canonique**, celui dont les quinze
autres n'étaient que des copies. C'était le meilleur candidat à conserver — et
c'est précisément celui qui montre pourquoi aucun ne tient : *un nombre de
fichiers ne dit rien de ce que ces fichiers font.*

### Le détail qui rend la chose remarquable

**Le même bloc de commentaire était recopié mot pour mot dans quatorze de ces
seize gardes** :

> *écrite comme un inventaire exact du répertoire, elle a transformé une garantie
> historique de tranche en **interdiction permanente de toute amélioration
> progressive future** — ce n'était pas le contrat produit visé*

Le diagnostic était juste, il était écrit, il était **dupliqué quatorze fois**,
et il n'a jamais été suivi d'effet. À chaque nouvelle autorisation, on ajoutait
le nom à quatorze listes.

---

## 2. Brainstorming / Options / Risques / Choix retenu

### Option A — allonger les seize listes, comme les fois précédentes

* ✅ Zéro réflexion.
* ❌ **Ne garde rien** : un `analytics.js` qui poste en douce passerait, du moment
  qu'il figure dans les listes. Aucune ne regarde ce que les scripts FONT.
* ❌ Reconduit exactement le défaut que leur propre commentaire dénonce.

### Option B — supprimer les seize

* ❌ `§5bis` lève l'invariant « sans JS », **pas** l'invariant d'écriture — la
  doctrine dit l'inverse : *a critical training write must remain recoverable if
  JS fails*.
* ❌ `CLAUDE.md §5.3` : une soustraction seule laisse le produit plus pauvre.
* ❌ Consigne opérateur permanente : ne pas supprimer de tests.

### Option C — recopier la nouvelle garde seize fois

* ❌ Reproduit littéralement le défaut de forme. Seize copies d'une sonde
  divergent — le dépôt l'a déjà vécu avec trois copies d'une sonde CSS qui ont
  rougi ensemble sur le même trou.

### Option D — une implémentation, seize appels *(retenu)*

Deux assertions de propriété dans `tests/helpers.py`, appelées par les seize
gardes :

| Fonction | Ce qu'elle épingle |
|---|---|
| `assert_aucune_ecriture_parallele()` | aucun verbe mutant, aucun canal d'écriture parallèle, **sur tout le répertoire** |
| `assert_aucun_framework()` | aucune ressource externe chargée, aucun import de module |

* ✅ **Zéro test perdu** — les seize points d'entrée subsistent, chacun sous son
  nom et dans le fichier de sa tranche.
* ✅ **Une seule implémentation** — rien à faire diverger.
* ✅ Le verrou se lève vraiment : un quatrième script devient possible.
* ✅ Ce qui doit encore mordre mord toujours.

### Risques et leur traitement

| Risque | Traitement |
|---|---|
| Une dix-septième garde d'inventaire réapparaît plus tard | `test_plus_aucune_garde_du_depot_n_epingle_l_inventaire_js` balaye `tests/**` par AST à chaque exécution |
| Bannir `fetch(` interdirait la lecture que la doctrine autorise | Cf. §3.1 — c'était mon premier jet, il a rougi sur `preview.js` |
| Une garde lit ses propres commentaires | `js_sans_commentaires()`, partagé |
| Le filtre de commentaires décapite les URL et rend un contrôle muet | Cf. §3.2 — trouvé et corrigé **avant** livraison |
| La garde ne mesure pas le bon répertoire | Un vrai fichier fautif planté dans `app/static/js/` |
| Le verrou n'est pas réellement levé | Un vrai fichier **bénin** planté, suite entière rejouée |

---

## 3. Trois défauts trouvés dans mon propre travail, avant livraison

### 3.1 — Bannir `fetch(` interdisait la doctrine elle-même

Mon premier jet interdisait `fetch(` sans distinction. Il a fait rougir
`preview.js`, qui **lit** une carte-aperçu en `GET` et ne persiste rien.
L'invariant est la **mutation**, pas la requête. Bannir la lecture aurait
interdit précisément l'enrichissement que `§5bis` autorise — la garde aurait
défendu le contraire de ce qu'elle prétend défendre.

### 3.2 — Le filtre de commentaires rendait le contrôle d'URL muet

Le contrôle interdisait `https://` dans les scripts. Or `js_sans_commentaires()`
retire `//` jusqu'à la fin de ligne — **y compris à l'intérieur d'une chaîne**.
Mesuré :

```
source brute  : const url = "https://cdn.example.com/react.js";
après filtre  : 'const url = "https:'
la garde voit https:// ?  False
```

**Le contrôle ne pouvait jamais se déclencher.** Il aurait laissé passer un CDN
React en clair tout en ayant l'air d'une protection.

La docstring du filtre affirme que « on retire trop, jamais trop peu » est *le bon
sens de l'erreur pour une garde*. C'est vrai d'une garde qui exige une
**présence**, et **faux** d'une garde qui prononce une **interdiction** : y
retirer trop fabrique un silence, pas une alerte. `js_sans_blocs()` ne retire
désormais que les blocs `/* */`, et `_URL_CHARGEE` distingue une URL *chargée*
(précédée d'un guillemet) d'une URL *citée* dans une phrase.

C'est la première fois qu'on relève ici **un outil partagé qui désarme la garde
de son appelant**.

### 3.3 — J'allais livrer une garde sur seize

Le plan annonçait une ligne. Le relevé par nom en donnait quatorze. Seul le
balayage par **classe** a rendu les seize. Sans lui, la tranche aurait livré une
PR verte, un rapport affirmant « le verrou est levé », et **quinze verrous
intacts**.

C'est la forme la plus nette du défaut « famille aux deux tiers » relevée à ce
jour — avec cette aggravation que le commentaire décrivant le défaut était
lui-même l'objet dupliqué quatorze fois.

---

## 4. Vérifications

| Contrôle | Résultat |
|---|---|
| `check_scope` | `ISOLATED` (sweep remonté d'un cran) |
| `ruff` (17 fichiers touchés) | `All checks passed!` |
| `check_ruff_budget` | `267 ≤ 548` |
| `check_spec_protocol` | `OK` |
| Les 17 fichiers modifiés | **391 passés** |
| Balayage AST du dépôt | **0 garde d'inventaire restante** |
| Défaut planté dans le vrai répertoire | 3/3 détectés, témoin retiré |
| **Quatrième script BÉNIN planté** | **391 passés** — le verrou est réellement levé |
| **Quatrième script FAUTIF planté** | **16 échecs** — les seize gardes mordent, une par une |
| Sweep large — 64 consommateurs de `tests/helpers.py` | *(voir appendice)* |

Les deux plantations sont la seule preuve qui compte, et elles se répondent : un
quatrième script d'enrichissement passe désormais, un quatrième script qui écrit
derrière le dos du serveur échoue **seize fois**. Le nombre seize n'est pas
recopié d'un relevé — c'est le nombre de gardes que l'expérience a fait rougir.

### La garde-de-la-garde

`TestGuardOfTheGuard` exige que **chaque contrôle morde sur son propre défaut** et
**épargne** ce qu'il ne doit pas mordre. Elle importe les motifs **réels** de
`tests/helpers.py` — une copie ici garderait le souvenir de la garde, pas la garde.

* six formes d'écriture mutante détectées ;
* une lecture `GET` épargnée ;
* le défaut d'URL **exact** de `§3.2` replanté, avec l'assertion que le filtre
  partagé le décapite toujours — si ce filtre change, la garde le dira au lieu de
  se taire ;
* une URL citée dans un commentaire épargnée ;
* trois formes d'import détectées ;
* **le dépôt entier balayé** : aucune fonction de `tests/**` ne compare la liste
  du répertoire JS à une constante.

### Ce que cette tranche ne fait PAS

* Elle **n'ajoute aucun fichier JS**, et ne touche à **aucun fichier
  d'application**. Elle retire l'interdiction, elle n'en profite pas.
* Elle ne trie pas les **41 autres gardes de MOYEN** « sans JS » (relevé
  contradictoire : 51 gardes nommées sur 47 fichiers, dont 41 de moyen, 9 de
  capacité, 1 mixte). Leur tri se fera tranche par tranche, quand une surface
  changera de mode de rendu.
* Elle ne corrige pas les **5 attributs `on*=`** qui subsistent dans 4 gabarits
  (`onsubmit="return confirm(...)"` ×4, `onclick="window.print()"`) — voir le
  verdict.

---

## Verdict

**LIVRÉ.** Seize inventaires du répertoire `app/static/js/` deviennent deux
assertions de propriété, implémentées une seule fois et appelées seize fois.
Aucun test n'est perdu, aucun fichier d'application n'est touché, et le verrou
est levé pour de bon — prouvé par plantation, pas par raisonnement.

Ce que cette tranche apprend dépasse son objet.

**Le plan disait « une ligne ».** Le relevé par nom en donnait quatorze. Seul un
balayage par CLASSE a rendu les seize — et les deux manquantes étaient les plus
intéressantes, dont celle qui se présentait comme l'inventaire *canonique*.
Livrer la première version aurait produit une PR verte, un rapport affirmant
« le verrou est levé », et quinze verrous intacts.

**Le défaut était écrit, quatorze fois, et jamais corrigé.** Le même paragraphe
— « une interdiction permanente de toute amélioration progressive future » —
était recopié dans quatorze gardes. Chaque nouvelle autorisation ajoutait le nom
à quatorze listes plutôt que de retirer le mécanisme que quatorze commentaires
dénonçaient. C'est le diagnostic central du programme dans sa forme la plus
littérale : *le produit avait la décision, il n'avait pas le moyen de
l'appliquer.*

**Un outil partagé peut désarmer la garde de son appelant.**
`js_sans_commentaires()` décapitait les URL avant que le contrôle ne les
cherche, et sa propre docstring affirmait que son excès était sans danger. Il
l'est pour une garde qui exige une présence ; il fabrique un silence pour une
garde qui prononce une interdiction.

Reste ouvert, et nommé : **les 5 attributs `on*=` dans 4 gabarits**
(`onsubmit="return confirm(...)"` ×4, `onclick="window.print()"`). Sans JS, une
suppression part sans confirmation et le bouton « Imprimer » est un contrôle
mort — pas dégradé, mort. Aucun n'est une garde de sécurité : la propriété est
vérifiée côté serveur. C'est une tranche à part, et elle demande de trancher ce
qu'on fait d'un bouton d'impression sans script.

---

## Appendice de clôture — post-merge

| | |
|---|---|
| **PR** | [#219](https://github.com/MFE-DSS/workout-session-tracking/pull/219) |
| **Méthode** | `--merge`, `--match-head-commit 837eb2d` — pas de squash, pas de `--admin`, pas de force |
| **Commit de merge** | `7a37092` |
| **CI de PR** | 7/7 verts — shards à 8 min 22, 9 min 42 et 8 min 28 |
| **Gate Sonar** | `OK` — 0 bug, 0 code smell, 0 vulnérabilité, **duplication 0,0 %** sur le code neuf |
| **Fils de revue non résolus** | 0 |
| **Sweep large** — les 64 consommateurs de `tests/helpers.py` | couvert par la CI de PR (3 shards sur la suite entière) |

### ⚠ La CI canonique de ce merge a été ANNULÉE — et c'est normal

Le run sur `7a37092` porte la conclusion **`cancelled`**, pas `success`. Ce n'est
pas un échec : le merge de la PR #218 est arrivé quelques secondes plus tard, et le
groupe de concurrence du workflow annule le run en cours au profit du plus récent.

**La source de vérité est le run sur `793be86`** —
[`run 34029186636`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/34029186636),
**success**, et ce commit **contient** `7a37092`. Vérifié, pas supposé.

C'est exactement la distinction que `CLAUDE.md §2` demande de faire : *une annulation
d'infrastructure n'est pas un échec de test*. Un `cancelled` lu trop vite aurait
déclenché une cascade de fixes sur une tranche saine.

### Ce que la tranche a réellement livré

| | |
|---|---|
| Gardes converties | **16**, dans 16 fichiers, sous 4 formes d'assertion |
| Implémentations | **1** — `tests/helpers.py` |
| Tests perdus | **0** |
| Fichiers d'application touchés | **0** |
| Quatrième script bénin planté | **391 passés** — le verrou est levé |
| Quatrième script fautif planté | **16 échecs** — les seize mordent |

### Ce qui reste ouvert, et qui appelle une décision

**Les 5 attributs `on*=`, recomptés à la main :**

| Gabarit | Handler | Sans JS |
|---|---|---|
| `squad_detail.html:162` | `onsubmit="return confirm('Supprimer cette squad ?…')"` | **supprime sans confirmer** |
| `squad_detail.html:167` | `onsubmit="return confirm('Quitter cette squad ?')"` | **quitte sans confirmer** |
| `history.html:113` | `onsubmit="return confirm('Supprimer définitivement…')"` | **supprime sans confirmer** |
| `admin_sessions.html:42` | idem — hors produit utilisateur | idem |
| `coach_report.html:17` | `onclick="window.print()"` | **bouton mort**, pas dégradé |

Trois **actions destructives** perdent leur confirmation, et un bouton devient inerte.
Aucun n'est une garde de sécurité — la propriété est vérifiée côté serveur. Mais
`AUREN_VISUAL_BACKBONE §5bis` dit que le SSR est la ligne de base fonctionnelle : un
bouton qui ne fait rien sans script n'est pas une amélioration progressive, c'est un
contrôle cassé. **Tranche à part, décision à prendre.**

**Branche `sb/js-capacity-guard` : NON supprimée.** `CLAUDE.md §2` réserve la
suppression de branche/worktree à une action humaine.
