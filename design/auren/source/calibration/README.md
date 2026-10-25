# Calibration System — design source (`DA-02.2`)

Autorité de design : `docs/strategy/AUREN_CALIBRATION_SYSTEM.md` (🔒 LOCKED v1).

## `reference/` — références visuelles, PAS des assets d'exécution

| Fichier | Rôle | Statut |
|---|---|---|
| `finallockedcursor.svg` | référence visuelle du `ReferenceMarker` | fourni par l'opérateur le 2026-10-25, conservé à l'octet près |
| `finlactivecursor.svg` | référence visuelle de l'`ActiveCursor` | idem |

Ces deux fichiers sont des **tracés** (fond blanc 1024 × 1024, coordonnées non entières, une encoche
en courbe). Ils fixent la **direction**, pas la géométrie : ils ne sont **jamais** chargés à
l'exécution et ne doivent pas être recopiés tels quels.

## La géométrie d'exécution — normalisée, ailleurs

`clients/mobile/src/ui/calibration/geometry.ts` reconstruit les deux objets sur **une grille commune**
d'unité `u`. **`u` est la largeur d'un index du rail** : la fente fait un index de large, et l'index
qu'elle encadre la remplit exactement (revue opérateur du 2026-10-25).

| Invariant partagé | Valeur |
|---|---|
| largeur de la fente de visée | `1u` = un index |
| épaisseur de paroi | `2,5u` (le curseur « plus massif ») |
| largeur hors tout | `6u`, **identique** pour les deux |
| encoche basse | `1u × 0,6u` |
| axe | `x = 0`, la fente centrée dessus |
| angles | droits, aucun arrondi |

| Objet | Silhouette | Lecture |
|---|---|---|
| `ActiveCursor` | `6u × 10u` : fente ouverte en haut sur `4u`, corps plein | tenu par l'utilisateur, massif, en vol |
| `ReferenceMarker` | `6u × 4u` : même largeur, bas et plat, fente sur `2u` | posé par l'instrument ; seule la hauteur le distingue |

Lus contre les tracés : la fente du marqueur tracé fait ~0,73 fois sa paroi, celle du curseur ~1,0 ; la
norme les unifie (exigence : *même fente, même paroi*). La géométrie est vérifiée par
`clients/mobile/src/ui/calibration/calibration.test.ts`.

Aucune couleur n'est inscrite dans la géométrie : `system` et `signal` sont injectés à l'exécution.
