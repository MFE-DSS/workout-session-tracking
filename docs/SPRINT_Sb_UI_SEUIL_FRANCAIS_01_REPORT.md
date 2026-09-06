# `Sb_UI_SEUIL_FRANCAIS_01` — « 0 séances », et trois clés de programme sur un profil public

Le filtre `pluriel` documente ce défaut **dans sa propre docstring**, depuis
`Sb_UI_PLURIEL_01` :

> Le seuil est `> 1`, et c'est le français : « 0 séance », « 1 séance »,
> « 2 séances ». Le seuil anglais (`!= 1`) rendrait « 0 séances ».

Il vivait **sept fois**, dans deux gabarits.

## 1. `!= 1` n'est pas un détail d'orthographe

`!= 1` et `> 1` ne diffèrent que sur **zéro** — et zéro est le compte que le
produit rend le plus souvent, sur chaque état vide. Servi à l'écran avant cette
tranche, sur `/coach-report` :

```
11 séances strength · 0 séances cardio
```

et sur un profil public :

```
Zone négligée back_width (0 séances)
```

Sept occurrences : `coach_report.html` (×5, deux d'entre elles sur une seule
ligne qui accorde le nom **et** le participe) et `user_profile.html` (×2).

## 2. Deux mots anglais sur des écrans français

* `Strength {{ … }}%` sur la barre de ratio du rapport coach — le produit dit
  **« Musculation »** partout ailleurs, jusque dans la légende de `/progress` ;
* `séance{…}s **strength**` sur la ligne suivante, en minuscule ;
* `Top zone` comme intitulé sur le profil public.

Le sweep qui les a trouvés porte sur une **liste étroite** de mots sans
ambiguïté. Il ne cherche pas « squad », « template » ni « Challenges » : ce
sont des **noms de produit tranchés par l'opérateur**, pas des fautes. Une
garde anti-anglicisme brutale accuserait exactement ce qu'il a choisi de
garder.

## 3. Trois clés de programme sur un profil PUBLIC

Le bloc « Activité 30j » d'un profil visible par les autres membres d'une
squad rendait :

```
Top zone pecs (8 séances)
Zone négligée back_width (0 séances)
Pattern dominant push_horizontal (62%)
```

**Le moyen existait**, et pas loin : `ZoneRanking.zone` porte une clé d'**axe
radar** — `profile_metrics` projette chaque zone fine sur son axe avant de
compter, et sa docstring le dit. La table `RADAR_AXES` vit dans
`muscle_mapping`, que ce même service **importe déjà**, et elle porte le
libellé : `pecs` → « Pectoraux », `back_width` → « Dos largeur ».

### Le piège que j'ai failli prendre

Ma première intuition a été `ZONE_LABELS`. **`back_width` n'y est pas** : cette
table est indexée par zone fine, où le dos large s'appelle `lats`. Deux espaces
de clés différents, dont **un seul mot commun** — `pecs`, que la docstring de
`profile_metrics` signale nommément comme « le seul libellé qui existe aux deux
niveaux taxonomiques ».

Traduire avec la mauvaise table aurait rendu « Dos largeur » pour un axe et la
clé brute pour l'autre, en ayant l'air de fonctionner sur l'exemple testé.

## 4. Ce que je n'ai PAS traduit

**`push_horizontal` reste tel quel.** Il n'existe aucune table de libellés pour
les patterns de mouvement, et l'espace de clés est **hétérogène** : le dépôt
mélange des patterns (`push_horizontal`, `pull_vertical`), des familles
d'exercices (`pulldown`, `pullup`, `pullover`) et des variantes d'isolation
(`isolation_free`, `isolation_machine`) — dix-neuf chaînes dont les frontières
ne m'appartiennent pas.

En créer une demanderait de **trancher une taxonomie**, pas de traduire un mot.
Signalé plutôt que deviné.

Même raison pour `_partials/body_intelligence_block.html`, qui rend
`Overload compliance : not_available_v1` — un anglicisme **et** une clé brute,
sur une deuxième ligne. La surface répond **404 derrière son drapeau de
fonctionnalité** : `CLAUDE.md §5.1` interdit de livrer ce qu'on ne peut pas
montrer.

## 5. La garde

Elle interdit le seuil anglais dans les gabarits, et vit dans le fichier qui
garde déjà la pluralisation — pas dans un dixième fichier de gardes
linguistiques.

Trois tests : aucun gabarit n'utilise `!= 1` · la sonde reconnaît ses deux
écritures réelles **et n'accuse pas le seuil français** · le filtre porte bien
le seuil français (`pluriel("séance", 0) == "séance"`).

Défaut d'origine replanté dans sa forme exacte : **la garde mord**.

## 6. Relecture du relevé de décisions (`CLAUDE.md §5.2`)

| Décision | Verdict |
|---|---|
| **Q1** · **Q2** · **Q3** · **Q5** · **Q6** · **Q7** · **Q8** | non concernées — la tranche ne touche ni surface, ni échelle, ni couleur |
| **Q4** — « les valeurs deviennent l'objet, le texte recule » | **respectée** : une clé d'axe n'est pas une valeur, c'est du chrome technique ; elle recule derrière son libellé |
| **Q4 amendement `DF-C`** — « les codes techniques ne sont pas la sémantique visuelle d'AUREN » | **respectée, et c'est le motif** |
| **`§5.3`** jamais une soustraction seule | respectée : rien ne disparaît ; un filtre et quatre libellés sont ajoutés |
| **`§5.4`** toute couleur est un token | non concernée |
| **`§5.5`** la centralité avant la facilité | respectée : le profil **public** — la surface la plus exposée du lot — est traité, et la taxonomie difficile est signalée plutôt que bâclée |

## 7. Vérifications

`check_scope` **SHARED_CODE** · broad sweep ciblé : **77 tests** · gardes de la
tranche **3 vertes**, plantation vérifiée · ruff OK.

Rendu exposé (`§5.1`) depuis deux serveurs, sur les deux surfaces atteignables :

| | avant | après |
|---|---|---|
| `/coach-report` | `Strength 100%` | `Musculation 100%` |
| | `11 séances strength · 0 séances cardio` | `11 séances de musculation · 0 séance de cardio` |
| `/users/nadia` | `Top zone pecs (8 séances)` | `Zone la plus travaillée Pectoraux (8 séances)` |
| | `Zone négligée back_width (0 séances)` | `Zone négligée Dos largeur (0 séance)` |

Hauteur inchangée sur les deux (**3,25** et **1,00** écrans).

## Verdict

**LIVRÉ.** Sept pluriels au seuil anglais corrigés par le filtre qui portait
déjà la règle, deux mots anglais remplacés par le mot que le produit emploie
ailleurs, et deux clés de programme retirées d'un **profil public** grâce à une
table que le service importait déjà.

## 8. Ce qui reste ouvert

* **`push_horizontal`** sur le profil public — demande une table de libellés,
  donc une décision de taxonomie ;
* **`Overload compliance : not_available_v1`** — même famille, sur une surface
  404 derrière son drapeau : non vérifiable au rendu, donc non livré ;
* **aucune garde ne surveille les anglicismes en général**, et c'est
  volontaire : la liste étroite de cette tranche est extensible, une garde
  large accuserait les noms de produit tranchés par l'opérateur.
