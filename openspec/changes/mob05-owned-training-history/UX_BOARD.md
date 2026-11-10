# MOB-05A — board familial de composition proposé

**G1_ACCEPTED / GO_BUILD_CONTROLLED**, 10novembre2026. Une seule surface Progrès et ses détails, quatre onglets conservés. ASCII = croquis, pas rendu natif. Les noms/chiffres ci-dessous sont des variables contractuelles, pas des faits pilote.

## Croquis validé

**Décision reçue le10novembre : « Autoriser MOB-05A et valider G1 ».** Croquis accepté :

```text
AVANT : Progrès                   APRÈS : Progrès
┌─────────────────────────────┐   ┌─────────────────────────────┐
│ AUREN · Progrès              │   │ Progrès              Aide   │
│ Sur le site, pour l'instant  │   │ [4 sem.] [12 sem.] [Tout]    │
│ description + lien web       │   │ [bornes réelles de période] │
│                             │   │ N séances réalisées         │
│                             │   │ petits comptes par semaine  │
│                             │   │                             │
│                             │   │ Séances récentes            │
│                             │   │ date · nom · terminée     › │
│                             │   │ date · nom · en cours     › │
│                             │   │ [Suite] si page disponible  │
│                             │   │                             │
│                             │   │ Exercice  [choisir ▾]       │
│                             │   │ occurrences datées        › │
│                             │   │ unité/contexte au détail    │
│                             │   │                             │
│                             │   │ Poids                       │
│                             │   │ valeur kg · date            │
│                             │   │ points mesurés RN/SVG       │
│                             │   │ [Voir les mesures]          │
│ Aujourd'hui Prog. Progr. Profil│  │ Aujourd'hui Prog. Progr. Profil│
└─────────────────────────────┘   └─────────────────────────────┘

SÉANCE / EXERCICE sélectionné      POIDS / ERREUR / OFFLINE
┌─────────────────────────────┐   ┌─────────────────────────────┐
│ ‹ Progrès          date      │   │ ‹ Progrès        période    │
│ Nom capturé · statut réel    │   │ Chronologie + liste datée   │
│ contexte / unité réelle      │   │ qualité/source au détail    │
│ Série n · fait · reps        │   │ ou accord requis/indisponible│
│ Série m · non réalisée       │   │ module poids seulement      │
│ Prescrit capturé  [Détails]  │   │                             │
│ Fait daté / heure inconnue   │   │ si offline : lecture passée │
│ [Historique exercice]        │   │ [Actualiser] sans faux zéro │
└─────────────────────────────┘   └─────────────────────────────┘
```

La racine défile, sections courtes, source détaillée à la demande ; fréquence donne des faits enregistrés et pas un score. Pas d'objectif corporel ni courbe de charge reliant contextes inconnus. Empty state par panneau : absence confirmée, couverture partielle, refus et transport inconnu restent distincts. Plan non persisté expliqué dans Aide, pas carte vide « planifié0 ».

## Inventaire — une information, une seule fois

| Élément | Source (contrat de données) | Doublon ? |
|---|---|---|
| Période/bornes | window.from/until/time_zone serveur | non |
| Fréquence | period_counts.completed_with_work + weekly_counts, counts_read_at | non |
| Liste récente | entries snapshots/status/exclusion/entry_ref | non |
| Exercice choisi | exercise_ref exact et occurrence_ref | non |
| Nombre et unité observés | SetLog brut ou V3 observation.setting/context validés | non |
| Prescription repliée | SCI binding capturé ; legacy UNKNOWN_NOT_CAPTURED | non |
| Dernière mesure | WeightHistory entries measured_at/id/quality/value kg | non |
| Graphe poids | mêmes points datés qualityKNOWN, gaps et couverture | non |
| Erreur/lecture précédente | auth revision/outcome/read_id/rows_read_at | non |
| Aide | définition de période/source/absences de contrat, sans règle scientifique | non |

## Comparaison avec la référence validée

Avant réel : PendingSpace canonique de l'onglet ; coque/tabbar MOB01, primitives FrameC/RecessedWindow/NumericReadout et typographie/tokens acceptés. Références compactes UX-CAL-02 reçu accepté ; ce ne sont pas des baselines Progrès qui n'existent pas. Après : vrais composants de production/HTTP synthétique une fois GO obtenu, iOS320/390 et Android360/480, texte agrandi ; avant/après à mêmes dimensions et donnée sourcée. MISSION/exécution/calibrage restent intacts, aucune nouvelle baseline automatique.

## Changement unique de l'itération

Demande : « Use one compact Progress surface inside the existing four-tab navigation ». Introduire la famille Progress Core, ses sous-vues et états, sans dashboard web, nouvelle couleur ou onglet. Chaque retour supplémentaire sera isolé au board. Les points sont aussi une liste textuelle et ne dépendent pas de couleur/motion.

## Preuve future et décision

G1 acquis ; après implémentation, pixels natifs iOS/Android soumis avant commit. Même présentateur monté dans vrai Shell Progrès, pas galerie seule. Retour Android/focus/AX, safeareas/longs libellés/texte agrandi/pagination/offline/A-B requis, limites physiques explicites. Aucun consentement corporel ni déploiement n'est obtenu par cette acceptation visuelle.
