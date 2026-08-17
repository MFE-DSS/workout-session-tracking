# DOGFOOD — Accueil / Aujourd'hui, 2026-08-17 (Martin, production `e51e4cb`)

Retour opérateur sur la page d'accueil, après le déploiement des 47 commits.
**Constats vérifiés dans le code** — chaque point porte son ancre. Deux
passages du retour vocal n'étaient pas exploitables et ne sont pas interprétés
ici.

**Statut : CAPTURE. Aucune ligne de code écrite.**

---

## 1. Le défaut structurel — le plus grave

> « c'est presque la même typo que l'autre […] il y a une incohérence
> structurelle dans la façon de rédiger le contrat UI/UX »

| élément | ancre | interactif ? | traitement visuel |
|---|---|---|---|
| « Choisir une séance » | hero d'accueil | **oui** | texte gris |
| « Résumé · indicateurs et navigation » | `index.html:86`, `today-home__summary-hint` | **non** | texte gris, typo quasi identique |

**Le même traitement visuel sert à un contrôle et à une étiquette.** Ce n'est
pas une question de goût : c'est un contrat d'interface rompu. L'utilisateur
ne peut pas déduire ce qui est cliquable.

`Sb_UI_INTERACTION_PRIMITIVES_01` avait posé la règle « la sélection doit être
lisible sans couleur » ; il manque son symétrique : **l'interactivité doit être
lisible sans essayer de cliquer.**

---

## 2. Étiquettes qui ne disent rien

| constat | ancre |
|---|---|
| « Aucune séance active » sous « Aujourd'hui » — *« qu'est-ce que ça veut dire ? »* | `index.html:48`, `today-home__status` |
| « Aujourd'hui » apparaît **deux fois** (bandeau + sous le résumé) | `index.html:26`, `today-home__eyebrow` |
| Cadre orange + flèche : l'action attendue n'est pas lisible | hero |

---

## 3. Vignettes jugées inutiles ou mal formatées

| vignette | verdict opérateur |
|---|---|
| **« Cette semaine — pas encore de séances »** | *« ne sert strictement à rien »* (`index.html:184`) |
| Première carte sous Résumé | *« on ne comprend pas »* — mais contient une info utile |
| « Se mettre / planifier » | utile, mais **texte brut** |
| « Prochaines séances proposées » | utile, mais **devrait être visuel** |
| « Dernière séance » | ✅ utilité comprise |
| « État du jour » · « Disponibilité » | ✅ à garder |

**« Niveau de fatigue bas, bon moment pour pousser »** est jugée *bonne
information, mauvais format* : elle mérite un affordance informationnel (un
« i ») expliquant qu'elle dérive d'une **tendance remplie régulièrement** — et
non un paragraphe.

---

## 4. L'idée à plus forte valeur — et elle est réalisable par assemblage

> « sur cette vignette état d'entraînement […] intégrer les assiettes visuelles
> qu'on a commencé à faire pour la science, où on a un corps humain complet
> avec des zones en récupération intermédiaire estimée ou en pleine forme. On
> comprend notre body à l'instant t […] sur quoi on peut aller forcer ou encore
> se reposer. Ça, c'est très important. »

**Vérifié : la donnée ET les assets existent déjà.**

| brique | où |
|---|---|
| Estimation de récupération **par zone** | `ZoneRecoveryEstimate` (`recovery_contract.py:1048`) |
| Vocabulaire d'état | `RecoveryBand` : `LIKELY_AVAILABLE` · `PARTIALLY_RECOVERED` · `LIKELY_FATIGUED` · `UNKNOWN` |
| Silhouette corps | `_partials/worked_area_body_map.html` |
| Plaques par région | `muscle_focus_plate_chest.svg`, `_shoulders.svg`, `_posterior.svg` |
| Carte de zone | `_partials/body_intelligence_zone_card.html` |

Les trois états que Martin décrit — *pleine forme*, *récupération intermédiaire
estimée*, *fatiguée* — **sont exactement** `LIKELY_AVAILABLE`,
`PARTIALLY_RECOVERED`, `LIKELY_FATIGUED`.

**C'est donc de l'assemblage, pas de l'invention.** Aucun moteur nouveau,
aucune donnée nouvelle, aucune migration.

⚠️ **Garde-fou obligatoire** : ces bandes sont des **estimations**. Le dépôt
interdit déjà toute revendication d'activation réelle ou de diagnostic
(`Sb_UI_04.3` : « zone estimée, jamais diagnostic »). Le rendu devra dire
*estimé*, et `UNKNOWN` devra rester visiblement inconnu — jamais colorié comme
« en forme ».

---

## 5. La thèse d'ensemble

> « il faut faire un travail de substitution d'objets descriptifs, manuscrits,
> vers des objets visuels du cockpit […] essentiellement dérivé des données
> qu'on a déjà et des assets qu'on a déjà »

Direction artistique **proche de Gravl, spécifiquement Auren**, cohérente avec
le design system existant. **Contrainte forte et bienvenue : dérivé de
l'existant.** Pas de nouveau moteur, pas de nouvelle collecte.

---

## 6. Découpage proposé

| # | tranche | nature | pourquoi cet ordre |
|---|---|---|---|
| 1 | **Contrat d'interactivité** | primitives + audit | Le défaut §1 est **systémique** : le corriger d'abord évite de reproduire l'ambiguïté dans chaque nouvelle vignette. |
| 2 | **État d'entraînement corporel** | assemblage | Plus forte valeur perçue, données et assets déjà là. |
| 3 | **Dégraissage d'accueil** | suppression | « Cette semaine » vide, doublon « Aujourd'hui », « Aucune séance active ». Retirer avant d'embellir. |
| 4 | **Prochaines séances en visuel** | rendu | Dépend de 1 et 3. |

**Le préflight `Sb_UIV2_HOME_COMMAND_CENTER_01` (tranche 1/8, écrit et jamais
implémenté) reste valide** : il avait déjà identifié la concurrence d'actions
au-dessus de la ligne de flottaison et le cadre imbriqué. Ce dogfood le
**complète** — il ne le remplace pas.

---

## 7. Ce qui n'est pas tranché

- **Traduction des bandes de récupération** en libellés produit : même piège
  que le ressenti musculaire (`Sb_SESSION_REVIEW_SIGNAL_01`) — une table de
  libellés créerait une seconde source de vérité. À décider explicitement.
- **Deux passages du retour vocal** non exploitables, non interprétés.
- **Le dogfood planner reste à faire** et n'est pas couvert ici.
