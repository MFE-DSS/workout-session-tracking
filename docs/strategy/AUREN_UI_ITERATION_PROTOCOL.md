# `AUREN_UI_ITERATION_PROTOCOL` — quatre garde-fous pour toute itération d'interface

**Statut** : actif · **Décision opérateur** : 2026-10-25 · **Autorité** : `CLAUDE.md §5.6–5.9` (versionné, prioritaire).
**Garde mécanique** : `tests/test_ui_iteration_protocol.py`. Tout nouveau rapport de tranche UI qui ne contient pas
les quatre sections ci-dessous fait rougir la CI.

---

## Pourquoi ce document existe

Le 2026-10-25, deux défauts ont été constatés en une journée, et l'opérateur les a jugés systématiques.

**1. DA-02.4 rejeté.**
- Une composition a été réinterprétée à partir d'un brief, au lieu de partir du rendu validé.
- Le rail en ligne (DA-02.2), qui porte l'ADN (pleine largeur, barres horizontales, profondeur), a été remplacé par une autre forme.
- Verdict de l'opérateur : « on ne comprend plus l'ADN de la chose ».

**2. Doublons verbaux-visuels.** Trois exemples :
- « PRESCRIT 70 KG » à côté du repère qui EST la cible ;
- la valeur répétée sous le rail alors qu'un module la porte déjà ;
- « · PUSH » écrit alors que le nom de zone PUSH est allumé.

Question de l'opérateur : *« comment développer avec toi quelque chose où tu arrêtes de produire de la connerie ? »*

Réponse : quatre garde-fous, à appliquer avant de montrer quoi que ce soit, et consignés dans chaque rapport.

---

## G1 — Croquis validé avant le code

Dès qu'une itération **change la composition** d'un écran (placement, hiérarchie, ajout ou retrait d'un bloc), un croquis est **validé par l'opérateur avant la première ligne de code**.
- Le croquis : ASCII d'une page, ou croquis de l'opérateur (photo de papier acceptée).
- Le code **reproduit le croquis**. Toute proposition de l'exécutant en plus est **séparée et marquée** « proposition », jamais fondue dans le rendu.
- Une demande ponctuelle et précise de l'opérateur (« les images plus grosses, alignées ») vaut croquis pour ce seul changement. Le rapport la cite mot pour mot.

**Gabarit** (section obligatoire du rapport) :

```
## Croquis validé

Source : <croquis ASCII ci-dessous | croquis de l'opérateur, date | demande de l'opérateur citée>

┌──────────────────────────────┐
│ ...                          │
└──────────────────────────────┘
```

## G2 — Une information, une seule fois (inventaire et contrat de données)

Avant tout rendu soumis, l'écran est **inventorié élément par élément**. Pour chaque élément : l'information qu'il porte, et le **champ du contrat de données** qui la fournit.

**Règles** :
- **Une information = un seul porteur.** C'est la marque ou le mot, jamais les deux.
- **Un mot ne nomme jamais ce que sa marque est déjà.** On écrit « 70 kg » au-dessus du repère de cible, pas « PRESCRIT 70 KG ».
- **Une valeur vit dans un seul module.**
- **Un élément sans source** dans le contrat de données n'est pas affiché, ou il est déclaré comme démonstration.

**Gabarit** (section obligatoire) :

```
## Inventaire — une information, une seule fois

| Élément | Information | Source (contrat de données) | Doublon ? |
|---|---|---|---|
| repère bleu + « 70 kg » | la cible | `calibration.reference.weight_kg` (VNEXT §8.11) | non |
| ... | ... | ... | ... |
```

La colonne **Doublon ?** ne contient que « non ». Un « oui » se corrige avant de montrer.

## G3 — Comparaison avec la référence validée

Chaque rendu soumis est montré **à côté du dernier rendu validé** de la même surface : même taille, même scénario.
- Si l'ADN validé a disparu (forme, largeur, profondeur, motif), **le rendu n'est pas montré**. Il est corrigé d'abord.
- Les références validées sont listées dans le rapport, avec leur date et la tranche qui les a validées.

**Gabarit** (section obligatoire) :

```
## Comparaison avec la référence validée

| Référence validée | Tranche / date | Ce qui doit survivre | Survit ? |
|---|---|---|---|
| rail en ligne pleine largeur | DA-02.2, 2026-10-25 | ligne horizontale, bande de zones, curseur dessus / repère dessous | oui |
```

## G4 — Un changement par itération

Une itération soumise à l'opérateur porte **un seul changement**, montré en **avant / après**.
- Plusieurs demandes de l'opérateur dans un même message peuvent être traitées ensemble **si et seulement si** chacune est citée et montrée séparément dans l'avant / après.
- Une recomposition complète n'est **jamais** une itération : elle passe par G1.

**Gabarit** (section obligatoire) :

```
## Changement unique de l'itération

- Demande : « <citation exacte de l'opérateur> »
- Changement : <une phrase>
- Avant : <capture / chemin>   ·   Après : <capture / chemin>
```

---

## Ce que la garde mécanique vérifie, et ce qu'elle ne peut pas vérifier

**Elle vérifie** que tout **nouveau** rapport de tranche UI contient les quatre sections, et que l'inventaire a la colonne « Source (contrat de données) ». Un rapport est une tranche UI s'il cite `clients/mobile` ou le contrat UI (`§5.1`). Les rapports existants sont figés dans une liste d'exemption.

**Elle ne peut pas vérifier** que le croquis a été respecté, que l'inventaire est juste, ou que la comparaison est honnête. Comme pour le `§5.1`, **aucune garde automatisée ne regarde un pixel** : le jugement de l'opérateur reste la garde finale. Ces quatre sections la rendent possible et rapide.
