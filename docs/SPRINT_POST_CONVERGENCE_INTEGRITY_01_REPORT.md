# `POST_CONVERGENCE_INTEGRITY_01`

**Canonique de départ** : `a867699` · **Tier `check_scope`** : `CI_INFRA`
**Points exécutés** : A · B · C · D

> `CI_INFRA` parce que la tranche ajoute `scripts/check_overflow.py`. Le
> contrat du dépôt l'impose alors : full sweep local **obligatoire** (non
> skippable) et **validation sur CI réelle impérative avant merge**.

---

## A — Le débordement de l'Accueil

### Diagnostic, mesuré et non supposé

À 1280 px, l'arbre rendu donne :

```
.today-home__action     958 px   [ 278 → 1236 ]
.today-home__cta        958 px   [ 278 → 1236 ]   ← toute la ligne
.today-home__secondary   73 px   [1246 → 1319 ]   ← +39 px hors cadre
```

La règle de base pose `width: 100%` sur le CTA — correct en colonne, sur
mobile. À partir de 900 px la ligne passe en `row`, et ce bloc réglait `flex`
et `min-width` **sans jamais défaire le `width: 100%`**. Le CTA revendiquait
donc toute la largeur, et `flex-wrap: nowrap` poussait le lien secondaire
dehors.

Le débordement valait **39 px à 1024 comme à 1280** — constant, parce qu'il ne
dépend pas de la fenêtre mais de la largeur du lien moins l'espace nul qui lui
restait.

### Correctif : un mot

`flex-wrap: wrap`. Le lien passe à la ligne au lieu de sortir de l'écran.

**Le défaut ne rendait pas seulement le lien hors cadre — il le rendait
illisible.** Écrasé à 73 px faute de place, il retrouve ses 210 px et son
texte entier. Le CTA garde exactement l'apparence qu'il a aujourd'hui.

### Deux correctifs écartés, et pourquoi

Ajouter `width: auto` ferait enfin agir le `min-width: 300px` — inerte depuis
toujours — et le CTA passerait de pleine largeur à 300 px. C'est peut-être
l'intention d'origine du bloc, mais c'est un **changement visuel de l'action
dominante d'une surface souveraine**, et l'ordre est de corriger sans refondre.
La déclaration reste inerte, et c'est **consigné plutôt que corrigé au
passage**.

### La garde rendue

`scripts/check_overflow.py` — **parcourt** le produit authentifié depuis la
racine, puis rend chaque surface :

| Palier | Surfaces | Largeurs |
|---|---|---|
| toutes les surfaces atteignables | 69 | **390 · 1024** |
| surfaces souveraines (`/`, `/sessions/{id}`) | 2 | **360 · 390 · 430 · 768 · 1024 · 1280** |

**Résultat : 69 surfaces, 174 rendus, zéro débordement.**

> ⚠ **Cette garde ne tourne PAS en CI.** Playwright n'est ni dans
> `requirements.txt` ni dans le workflow ; l'y mettre est une décision
> `ci_infra` distincte. C'est un contrôle de poste, comme
> `run_local_sweep.sh`.
>
> Ce que la CI vérifie, elle : `tests/test_overflow_gate_contract.py` épingle
> les deux paliers de largeurs, le jeu souverain, la raison de chaque
> exclusion, et surtout que la garde **découvre par parcours** et non par une
> liste écrite à la main. Le défaut de `/` a survécu des mois derrière une
> carte de treize surfaces choisies à la main : si le script régresse vers une
> liste, il recommencera à ne pas voir ce qu'on oublie — en restant vert.

---

## B — Science, document de provenance

Audit complet dans [`SCIENCE_REFERENCE_AUDIT.md`](SCIENCE_REFERENCE_AUDIT.md).

### L'audit contredit le brief, et il faut le dire

L'ordre listait six éléments comme périmés. **Cinq sur six décrivaient
fidèlement du code vivant**, vérifiés nombre par nombre contre
`quality_score.py` et `feedback.py` :

| Signalé | Réalité mesurée |
|---|---|
| « cible 20 min LISS » | `if duration_min >= 20: return 50.0` |
| « 115–135 bpm » | `if 115 <= bpm_avg <= 135: return 20.0` |
| « > 85 / 100 » | 50 + 20 + 20 = **90**, avant tout point subjectif |
| « Score dérivé » | `compute_success_score` : reps vs plage + séries complétées |
| « Scoring cardio vs musculation » | les deux branches existent et sont rendues |
| « Synthèse et physique » | **périmé, confirmé** |

Les supprimer aurait retiré de la provenance **exacte** au document dont c'est
la fonction. Ils sont donc classés `CURRENT`.

**Mais l'intuition derrière le signalement était juste, et le défaut réel est
le vocabulaire.** « Cible 20 min » présente un palier de barème comme un
objectif d'entraînement, sur la page de référence d'un produit qui vient de
retirer ce langage de tous ses instruments. Ce n'est pas de la staleness, c'est
une **collision de doctrine**.

Le bloc est reformulé : **aucun nombre déplacé, aucune règle inventée**, et la
distinction est écrite en toutes lettres — *« Ce sont des paliers de barème,
pas des objectifs d'entraînement. »*

### Les deux blocs réellement périmés

**« Synthèse et physique »** décrivait deux surfaces qui n'existent plus. Une
phrase a été sauvée — « tu ne vois jamais un score qu'on ne peut pas calculer
honnêtement » — parce qu'elle était une promesse à l'écriture et est devenue
**littéralement vraie** avec `TRAIN1-C`.

**Le diagramme d'architecture** — trouvé parce que l'ordre disait « chaque
section **visible** », pas « chaque section du gabarit ». Le SVG rendait
`Synthese` et `Physique` en boîtes de sortie **et dans sa `<desc>`** : un
lecteur d'écran recevait l'architecture d'avril. Un `grep` sur `science.html`
ne l'aurait jamais vu.

Les sept ancres de règle sont préservées et vérifiées au rendu.

---

## C — Le gabarit mort

`rules.html` : **zéro référence** dans `app/`, `tests/`, `scripts/`. La route
`/rules` est une redirection 301 indépendante du gabarit. Supprimé ; la
redirection est vérifiée **au rendu**, pas déduite.

---

## D — L'atlas

**`SCIENCE_ATLAS = REFERENCE_SECONDARY`**, consigné. Sa longueur — 15,3
écrans, 2 074 mots — **n'est pas un défaut** : c'est un référentiel consulté
par entrée ponctuelle. Sommaire par famille et ancres machine suffisent.

**Condition de réouverture, unique et écrite** : que `TRAIN 3` démontre une
entrée dans l'atlas **sans contexte machine connu**. Une longueur déclarée
non-défaut sans condition de réouverture serait une dette qui ne se rouvre
jamais — une garde vérifie que la condition reste écrite.

---

## Relecture des décisions UI (`CLAUDE.md §5.2`)

| Règle | Verdict |
|---|---|
| **5.1** exposition préalable | **respectée** — arbre rendu mesuré avant/après, captures 1024 et 1280 |
| **5.2** relecture consignée | **respectée** |
| **5.3** jamais une soustraction seule | **respectée** — le bloc « Synthèse et physique » est remplacé par la description de Progression ; le diagramme garde deux sorties au lieu d'en perdre deux ; `rules.html` part mais sa route survit |
| **5.4** toute couleur est un token mesuré | **non concernée** — aucune couleur touchée |
| **5.5** centralité avant facilité | **respectée** — A (défaut sur surface souveraine) avant B, C, D |

---

## Mes fautes

1. **Trois gardes passaient pour la mauvaise raison**, toutes trouvées en
   plantant leur défaut :
   - « le diagnostic est consigné » cherchait `width: 100%` dans **tout le
     fichier** — satisfaite par la déclaration réelle de `.today-home__cta`,
     pas par le commentaire qu'elle prétendait vérifier. Elle serait restée
     verte avec le diagnostic entièrement effacé ;
   - « la ligne d'action peut passer à la ligne » cherchait
     `.today-home__action` dans toute la feuille et tombait sur la règle
     **mobile** (une colonne, qui n'a jamais eu besoin de `wrap`) ;
   - « la description accessible correspond au dessin » vérifiait la
     **présence** de deux mots : elle ne pouvait pas voir une description qui
     nomme les bonnes surfaces dans de mauvaises relations. Elle extrait
     désormais les libellés réellement dessinés et exige la correspondance.
2. **Deux de mes mutations étaient trop faibles** pour éprouver leur garde —
   corrigées jusqu'à reproduire le vrai mode d'échec, pas une variante
   commode.

---

## Vérifications

| Contrôle | Résultat |
|---|---|
| `check_scope.py` | **`CI_INFRA`** |
| ruff, reproduction exacte du rapport CI | **0** occurrence dans la tranche |
| `check_ruff_budget.py` | 276 ≤ 548 |
| `check_spec_protocol.py` | OK |
| garde rendue de débordement | **69 surfaces · 174 rendus · 0 débordement** |
| gardes plantées | **14 / 14 rougissent** |
| full sweep local | **obligatoire à ce tier** |
| CI réelle | **impérative avant merge à ce tier** |

---

## Closeout post-merge

| | |
|---|---|
| PR | [#158](https://github.com/MFE-DSS/workout-session-tracking/pull/158) |
| Méthode | `--merge`, tête épinglée `d7e31de` — pas de squash, pas de `--admin`, pas de force |
| Commit de merge | **`0ccab96`** |
| CI de PR | **9 / 9** verts · gate Sonar `OK` · 0 code smell neuf |
| CI canonique au push | run `32846681960` — **succès** |
| Fils de revue · migration | 0 · aucune |

**Validation CI réelle : satisfaite.** Le tier `CI_INFRA` l'exige avant merge,
et c'est la première tranche de cette série où l'exigence porte réellement —
elle ajoute un script à `scripts/`.

**Aucun cycle rouge.** Troisième tranche consécutive.

### État

**`CLOSED`** — nettoyage exécuté sur ordre opérateur.
