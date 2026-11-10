# MOB04 — board unique proposé, G1_PENDING

**État courant : GO_BUILD_CONTROLLED / G1_ACCEPTED / PIXELS_PENDING**, décision opérateur « Autoriser MOB-04 et valider G1 », [reçu](BUILD_AUTHORIZATION.md). Les paragraphes de proposition ci-dessous conservent leur instant historique ; la navigation B est retenue. Base de réalisation réconciliée d67f12a (REL03 livré et réservation MOB06 préservée).
## Croquis validé
**Pas encore validé.** Proposition à comparer au MISSION-SCREEN-V1 accepté31octobre et aux entrées UX-CAL-02 acceptées9novembre. Aucun nouveau pixel produit.

```text
Aujourd'hui — HISTORICAL       Premier parcours — FIRST_USE
┌────────────────────────┐    ┌────────────────────────┐
│ [mark existant]        │    │ [mark existant]        │
│ [titre/raison serveur] │    │ Première séance       │
│ [BodyMap LOCKED]       │    │ [état propriétaire]   │
│ [scope factuel]        │    │ [prochaine étape utile]│
│ [ Démarrer ]           │    │ [ Continuer ]          │
│ Autres parcours ›      │    │ Autres parcours ›      │
└────────────────────────┘    └────────────────────────┘

Reprise (priorité commune)    Source indisponible / inconnu
┌────────────────────────┐   ┌─────────────────────────┐
│ [séance possédée]      │   │ Première séance         │
│ [position factuelle]   │   │ [motif bref applicable] │
│ [ Reprendre ]          │   │ [ Actualiser ]          │
│ Détails ›              │   │ Aide ›                  │
└────────────────────────┘   └─────────────────────────┘
```

La colonne historique reprend exactement la composition LOCKED, sans rajouter un badge dans sa carte. « Autres parcours » est une commande subordonnée extérieure à cette composition, uniquement si G1 l'accepte ; elle ne sélectionne aucune source scientifique automatiquement. Le host de calibrage/proposition/ack/exécution existant s'ouvre après action et garde ses pixels/contrats. Séance close : lecture historique, sans CTA nouvelle première séance.

**Deux variantes G1, à trancher avec le scope :** A conserve Aujourd'hui→HISTORICAL et une entrée premier parcours distincte ; B fait de FIRST_USE l'entrée Aujourd'hui du nouveau consommateur, puis HISTORICAL seulement par bascule volontaire. B est proposé pour le nouveau parcours AUREN, avec indisponibilité honnête si son runtime est absent. Aucun changement des anciens clients ni fallback SCI automatique dans l'une ou l'autre. Une séance possédée ouverte prime toujours. Les titres des deux colonnes sont intervertis pour B ; leurs compositions ne changent pas. La décision n'est pas encore acquise.

## Inventaire — une information, une seule fois
| Élément | Source (contrat de données) | Doublon ? |
|---|---|---|
| Titre/raison/BodyMap/scope historiques | mission_read_model existant, zones serveur | non |
| Chemin demandé | Navigation explicite echoed requested_path, pas donnée de santé | non |
| Position reprise | Séance possédée et open_session_position, profil du domaine | non |
| Prochaine étape premier parcours | Projection de références/disponibilité PLAN puis host existant ; aucune dose créée par MISSION | non |
| Bouton principal | primary_action typé recoupé au owner/profil/path | non |
| Absence ou motif indisponible | state/reason serveur ; transport inconnu distingué | non |
| Détails/aide | Données/texte applicables du contrat existant, à la demande | non |

## Comparaison avec la référence validée
Quatre baselines mission-390x844-* read-only ; croquis ne remplace pas la comparaison de vrais pixels. Le nouveau board réel couvrira sources, reprise, vide/inconnu, petites/grandes largeurs iOS/Android, grandes fontes, AX et safe areas. Pas d'icône anatomique nouvelle, vert, seuil E7 ou cinquième onglet. Les captures de l'app pilote seront des preuves fonctionnelles si reçues, jamais une DA à copier.

## Changement unique de l'itération
Demande : « real Mission ». Changement proposé : source/action propriétaire explicite autour des consommateurs déjà livrés. Avant : Today historique + entrée PLAN contrôlée séparée. Après proposé : projection typée et orientation délibérée, reprise prioritaire et un seul CTA ; aucune refonte de MISSION.


Réconciliation du mandat PILOT VALUE DELIVERY du10novembre : [PILOT_VALUE_SCOPE](PILOT_VALUE_SCOPE.md) précise base canonique, option de navigation B, commandes locales et leases séquencés. Statut toujours NO_GO_BUILD/G1_PENDING.


## Croquis consolidé proposé — PILOT VALUE DELIVERY du10novembre

Option B proposée dans PILOT_VALUE_SCOPE, G1 toujours pending. Les quatre onglets restent visibles hors exécution/flow actif. Les nouvelles orientations sont une famille compacte ; la carte historique reste sa baseline intacte.

```text
Aujourd'hui                         Aujourd'hui
Première séance                     Séance en cours · nom possédé
[étape confirmée du contrôleur]      [position confirmée ou historique]
[ Continuer ]                       [ Reprendre ]
Détails                             Journal / détail à la demande
Autres parcours (secondaire)         (jamais nouveau start concurrent)

Aujourd'hui                         Aujourd'hui
Réception à vérifier                Proposition indisponible
[commande conservée sur appareil]    [motif confirmé ou inconnu]
[ Vérifier ]                        [ Actualiser ]
Journal                             Aide

Historique explicitement demandé    Première séance déjà terminée
[MISSION-SCREEN-V1 INTACT]           [fait possédé, date/statut]
raison exacte · zones serveur       [ Lire la séance ]
[Démarrer] sous vrai start gate      (pas deuxième séance SCI inventée)
```

Source dominante unique : projection serveur pour ownership/action, contrôleur/journal pour commandes locales, read-model historique pour raison/zones. La raison LOCKED n'est pas déplacée dans un repli. Compte A/B et état réseau sont des sources distinctes, pas du texte de prescription. Aucun élément sans champ réel, unknown jamais zéro. Avant/après réels après GO : QA02 native-main/native-fresh-entry et baselines MISSION/UXCAL acceptées datées, pas un nouveau rendu prétendu produit ici. Les captures officielles de recette physique restent à obtenir.
