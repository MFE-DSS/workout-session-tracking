# Sb_DA_04_4_MOTION_ZOOM_DEFERRED — le zoom biomécanique, mis de côté et consigné

**Date :** 2026-10-31
**Branche :** `sb/da-04-4-motion-deferred` (base canonique `5fe7855`, après DA-04.3)
**Verdict :** voir la fin du rapport.

## 0. Commande et décisions de l'opérateur

- Demande initiale : « un zoom biomécanique de la zone […] où on voit la fibre contractée, se décontracter,
  comprendre les zones de risque […] un zoom technico-fonctionnel ».
- Sur le prototype : « Très intéressant les deux variants […] tu as quelque chose de mécanique qui est
  pertinent » ; puis : chercher « des frameworks, des planches, des travails biomécaniques déjà disponibles […]
  avec une licence […] qui fait qu'on peut les prendre et les refactoriser ».
- Décision finale : « le prototype, globalement, est moche. Donc, le cadran et tout, j'aime pas trop […] mets
  tout ça de côté […] à faire plus tard dans l'amélioration continue du software, de fournir une représentation
  3D pertinente des faisceaux […] J'utiliserai Midjourney […] mets-le de côté dans le data contract, c'est à
  faire. Et avance sur ton critical path des autres assets UX UI […] il faut plutôt qu'on converge vers la fin
  de la préparation de l'application ».

## 1. Brainstorming · Options · Risques · Choix retenu (`CLAUDE.md §3`)

| Option | Pour | Contre |
|---|---|---|
| A — livrer le prototype dessiné | prêt, testé | rejeté par l'opérateur (« moche ») |
| B — construire tout de suite le générateur sur le modèle thoraco-scapulaire | mécanique juste | 3 à 5 jours hors chemin critique ; rendu pas encore conçu |
| C — **différer et consigner** : rien de livré, tout ce qui a été appris versionné, le chemin critique reprend | suit la décision ; la reprise ne refait pas la recherche | aucun |

**Choix : C.** **Risques** : perdre la recherche (→ `AUREN_VISUAL_CONTRACT §23`, sources, licences, pièges,
mesures) ; laisser croire qu'un rendu a été accepté (→ statut DIFFÉRÉ, aucune baseline) ; laisser le mannequin
bloquer le chemin critique (→ DA-05.0 en sort, DA-05.1 redéfinie).

## 2. Ce qui a été fait (hors dépôt, rien n'est livré)

- **Prototype** : fibres en éventail dans le pectoral du corps MIT, stries pilotées par le tempo, cadran de
  l'épaule, piste de tempo, animations réduites respectées ; 82 captures dans l'image épinglée ; deux variantes
  revues. Non committé ; patch conservé hors dépôt.
- **Recherche** : trois axes (simulation et anatomie 3D, illustrations et animations, données de mouvement),
  chaque licence lue à la source ; les deux licences portantes revérifiées à la main.
- **Essai** : OpenSim (Apache-2.0) dans un environnement isolé, sur canaux ouverts seulement (les conditions
  d'Anaconda n'ont pas été acceptées au nom de l'opérateur) ; modèle thoraco-scapulaire (CC BY 4.0) mené sur une
  répétition de développé incliné ; contour du pectoral MIT déformé par l'insertion calculée.

## 3. Ce qu'on garde (consigné au contrat §23)

- Aucune ressource ouverte ne montre déjà un muscle en mouvement : le mouvement est à produire.
- La mécanique a une source ouverte et vérifiée : le modèle thoraco-scapulaire. Faisceaux du grand pectoral sur
  l'incliné (longueur de fibre normalisée, bas → haut) : claviculaire 1,01 → 0,49 ; moyen 0,95 → 0,73 ; inférieur
  0,85 → 0,74.
- Deux pièges du modèle, prouvés : coude verrouillé par défaut (un déverrouillage après construction est ignoré
  sans erreur — d'où le contrôle de chaque valeur tenue) ; longue portion du triceps fausse au coude.
- Exclus, et pourquoi (non commercial, origine inconnue, non redistribuable).

## 4. Conséquences sur le chemin critique (`AUREN_VISUAL_BACKBONE §8.4`)

- `DA-04.4` : DIFFÉRÉ ; backlog `MOTION-V2`.
- `DA-05.0` (mannequin) : sort du chemin critique ; l'opérateur produira les représentations.
- `DA-05.1` : redéfinie — l'écran d'exercice réel composé des pièces verrouillées ; prochaine étape.
- Puis gate `DA-01` final, puis montage des pièces verrouillées dans les écrans réels (l'instrument de charge
  attend E7).

## 5. Réalisation (docs seulement)

| Fichier | Rôle |
|---|---|
| `docs/strategy/AUREN_VISUAL_CONTRACT.md` | registre (`MOTION-ZOOM` DIFFÉRÉ), §23 |
| `docs/strategy/AUREN_VISUAL_BACKBONE.md` | §8.4 : `DA-04.4`, `DA-05.0`, `DA-05.1`, backlog `MOTION-V2`, convergence |
| `docs/strategy/SPEC_REGISTRY.md` | ligne de la tranche |

## Annexe de clôture (2026-10-31)

- Gate vérifié avant fusion : tête `91943b1`, 11 / 11 checks verts, Sonar PR `OK`, 0 fil ouvert, `CLEAN`.
- PR #328 fusionnée en `--merge --match-head-commit` : **`fec77bb`**. Docs seulement : la CI de push est
  légitimement sautée par `paths-ignore: docs/**` (`CLAUDE.md §2`) ; la CI de la PR fait foi.

**Verdict :** `MOTION-ZOOM` **DIFFÉRÉ** — rien de livré, tout ce qui a été appris est versionné ; le chemin critique
reprend par `DA-05.1`.
