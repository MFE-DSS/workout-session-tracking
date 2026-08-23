# TRAIN 1-A — closeout, et ce que le rendu a appris que la mesure taisait

**Date** : 2026-08-23
**Canonique finale** : `4c81ba3`
**Base d'entrée** : `a71ac24`

---

## 1. Ce qui est livré

| PR | Contenu | Merge | Méthode |
|---|---|---|---|
| #144 | `Sb_EKB_ORTHOGRAPHIC_ALIAS_01` — décision EKB | `d7417f3` | `--merge`, tête `92363b0` |
| #145 | `TRAIN1-A` — A4 + A5 + A11 | `4c81ba3` | `--merge`, tête `c394f26` |

**Aucun squash, aucun `--admin`, aucun force.** Tête épinglée à chaque merge.

**CI canonique — source de vérité** : run
[`32650666473`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/32650666473)
sur `4c81ba3` — **`success`, 6/6 jobs verts** (lint · 3 shards pytest · QA
scripts · SonarCloud). Elle couvre les deux merges cumulativement.

**Cleanup de TRAIN 0** exécuté avant : cinq worktrees, cinq branches locales et
cinq branches distantes supprimées après vérification — arbre propre et zéro
commit non mergé sur chacune.

---

## 2. La décision EKB, et pourquoi elle était plus simple que prévu

L'ordre disait : « aligner la cartographie contradictoire sur la canonique
mesurée ». La mesure a montré que ce n'était **pas un arbitrage entre deux
sources** :

| Source | `…(corde)` | `…corde` |
|---|---|---|
| `exercise_properties.json` | `arms` · `isolation_upper` · `cable` | **identique** |
| `classify_exercise` | `biceps` | **`biceps`** |
| **EKB avant** | `biceps` / `arms` / `measured` | **`None` / `None` / `derived`** |

Les deux sources amont s'accordent **sur les deux orthographes**. Le `null`
n'était justifié par aucune d'elles : défaut de **construction** de l'EKB. C'est
ce qui autorise `confidence: measured` sur l'entrée alignée — elle repose sur la
même mesure que la canonique, pas **sur elle**.

**Portée bornée mécaniquement, pas par une promesse.** La garde ne groupe que
des noms égaux après **normalisation stricte** — ponctuation, accents, casse.
Jamais une différence de mots. Les 17 autres quasi-doublons ne peuvent pas y
tomber, et une seconde garde vérifie que cette paire reste la seule.

---

## 3. TRAIN 1-A — ce qui a été mesuré avant d'écrire

| Fait | Occurrences sur un même écran, avant |
|---|---|
| comptage de séances | **5** |
| fenêtre temporelle nommée | **12**, sur **5 fenêtres différentes** |
| blocs de dominance par programme | **2** |

`UX4_03D` déclarait la cadence « absorbée par le rail » et retirait l'objet
`Cadence 7 j`. **Elle survivait dans `weekly_loop`.** Sur un compte vide, la
même phrase — « Pas encore assez de données cette semaine » — était rendue
**deux fois dans la même carte**.

### Résultat, mesuré au rendu réel

Densité **visible** — le contenu d'un `<details>` fermé est compté à part.

| | avant | après |
|---|---|---|
| compte vide · mots | 166 | **123** |
| compte vide · cartes | 6 | **2** |
| compte peuplé · mots | 268 | **228** |
| compte peuplé · cartes | 9 | **3** |
| comptages de séances | 5 | **3** |
| blocs de dominance | 2 | **1** |

`<summary>` à **44 px** aux trois largeurs, aucun défilement horizontal.

---

## 4. Le défaut que personne n'avait demandé de chercher

`DayTrace` documente **quatre** natures de jour depuis le premier jour, dont
`none` — « hors historique : le compte n'existait pas encore ». La vue-modèle
sait la rendre : classe dédiée, titre, phrase dans l'équivalent textuel.

**Le producteur ne l'a jamais émise.** Un compte créé la veille rendait
**quatorze traces `rest`** — treize affirmations « il pouvait s'entraîner, il ne
l'a pas fait » sur des jours où il n'avait pas de compte.

Trois chemins de code et une phrase de lecteur d'écran étaient morts. Aucune
garde ne l'avait vu : elles éprouvaient `none` via une **fabrique de test**,
jamais via le producteur réel. C'est la signature exacte du motif catalogué
« une garde qui ne garde rien » — et cette fois il protégeait un état
inatteignable.

⚠ **La donnée passe avant la borne.** Une séance enregistrée ce jour-là
**prouve** que le compte existait, quoi qu'en dise `created_at`. La première
écriture testait la borne en premier et **faisait disparaître des séances** ;
une garde tient désormais l'ordre.

---

## 5. Trois défauts vus seulement en REGARDANT

Neuf écrans entiers, deux comptes × trois largeurs, plus le niveau 2 ouvert
(§5.1). **Aucune mesure automatisée n'aurait signalé ces trois-là :**

1. **« Par programme » se cassait à 390 px** — « 1× cette sem. » s'écrasait
   contre le nom du programme et contre « 2 sessions ».
2. **La divulgation « Comment AUREN calcule ces signaux » se rendait sur
   l'écran vide** — elle proposait d'expliquer des signaux absents.
3. **Son texte décrivait encore « Cadence 7 j »** — objet retiré par `UX4_03D`,
   donc une explication d'un signal disparu depuis deux tranches.

C'est le fondement de `CLAUDE.md §5.1` : aucune garde automatisée du dépôt ne
regarde un pixel.

---

## 6. Deux erreurs de méthode, consignées

### 6.1 — Un correctif CSS écrit 300 lignes trop haut

Le correctif de « Par programme » a d'abord été posé près du bloc du rail
(ligne ~1950). Les définitions d'origine de `.template-kpi__count` et
`.template-kpi__name` suivent dans le fichier (~2270) : **même spécificité, la
dernière gagne**. Le correctif n'avait aucun effet, et **rien ne l'aurait
signalé** — ni test, ni lint. Vu au re-rendu.

### 6.2 — Un broad sweep bâti sur le mauvais rayon d'impact

`test_reduced_motion_targets_universal_selector` est sorti **en CI**, pas en
local. J'avais ajouté un bloc `@media (prefers-reduced-motion: reduce)` scopé au
chevron : **redondant** — le bloc universel du fichier se décrit lui-même comme
« robuste aux transitions ajoutées ultérieurement » — et **nuisible**, car placé
ligne 1999 il devenait le premier bloc que la garde inspecte, désarmant la
contrainte universelle.

**Cause de l'échappement** : mon broad sweep local était construit sur le rayon
d'impact **Python** (consommateurs de `/progress` et des KPI) alors que la
tranche touche aussi `app.css`. Les **20 fichiers de test qui lisent la feuille
de style** n'y figuraient pas. Relancés après correction : **374 verts**.

**Règle qui en découle** : un diff qui touche du CSS tire les contrats CSS. La
sélection du broad sweep se fait par **fichier modifié**, pas par intuition du
domaine.

---

## 7. Quatre tests migrés, aucun affaibli, un renforcé

| Test | Ancien invariant | Nouveau |
|---|---|---|
| `test_progress_route_renders_weekly_section` | « le conteneur existe » | conteneur **absent** + ses deux faits présents ailleurs |
| `test_progress_renders_with_empty_db` | « la grille de KPI existe » | ligne compacte + **aucun `—`** en valeur |
| `test_progress_kpis_are_scoped` | « un `0` apparaît quelque part » | **rien de l'autre compte** + la page dit qu'elle n'a rien |
| 7 gardes HTTP d'`UX4_03B` | supposaient l'instrument toujours rendu | reçoivent des traces via `_with_traces` |

Le troisième était un proxy faible de l'étanchéité entre comptes : n'importe
quel zéro le satisfaisait.

---

## 8. Vérifications

| Contrôle | #144 | #145 |
|---|---|---|
| `check_scope` | `ISOLATED` → **promu SHARED_CODE** | `SHARED_CODE` |
| Gardes dédiées | 19 → **24** | **28** |
| Broad sweep | **342** (17 consommateurs EKB) | **476** (Python) + **374** (contrats CSS) |
| CI PR | 8/8 · Sonar OK | 8/8 · Sonar OK · couverture neuve 97,0 % |
| Exposition §5.1 | — (aucune surface) | **9 écrans entiers**, 360/390/430 |

**Incidents Sonar, tous in-scope et corrigés à la source** : `python:S9073` sur
#144 (assertion composite dans ma propre garde). Le pré-scan AST prescrit par le
skill Sonar avait été omis ; relancé depuis sur chaque fichier de test.

---

## 9. Constaté, non traité, et pourquoi

- **« Par programme » et « Activité récente » rendent chacune une carte pleine
  pour dire « aucune session »** sur un compte vide — le même défaut qu'A4
  ferme, dans des blocs qui relèvent de **TRAIN 1-C**.
- **Deux `—` subsistent dans « Rythme récent » sur un compte peuplé sans
  `SetLog`.** Ici le tiret est **exact** : il n'y a rien à diviser. Le changer
  demanderait une décision produit sur ce que rend un KPI sans dénominateur.
- **Trois cibles sous 44 px** sur Progression : `topbar__brand`,
  `foot__contact`, lien « Comment c'est calculé → ». **Toutes préexistantes**,
  présentes sur chaque page.

---

## 10. Ce que TRAIN 1-B devra trancher

L'audit préalable d'A10 est fait, et il change la question.

**La primitive de comparaison existe déjà.** `app/services/delta.py` :

> « The function NEVER infers a "delta" from partial data. »

Zéro seuil, zéro agrégat, `=` pour une égalité, `None` quand le côté précédent
n'a pas de série complétée. L'exigence « pas de score global inventé » est
**déjà le contrat écrit du dépôt**, et `exercise_history` la consomme.

Ce qu'A10 ajoute n'est donc pas une règle de comparaison mais une **vue agrégée
par exercice**. Deux points restent à trancher, et ils sont produits :

1. **L'identité de comparaison est `(gabarit, code d'exercice)`**, et
   `exercise_history` documente explicitement : *« Deliberately does not merge
   exercises across templates »*. A1 existe pour permettre cette fusion.
   **La franchir change une décision produit écrite.**
2. **Le cardio n'a pas de série.** `cardio_duration_min`, `cardio_bpm_avg`,
   `cardio_machine_calories` vivent sur `WorkoutSession`, pas sur
   `SessionExercise`. La « métrique adaptée au type » existe, mais à un autre
   niveau du modèle.

Risque de duplication à surveiller : la page d'historique par exercice existe
déjà. A10 doit en devenir le niveau amont, pas un objet parallèle.
