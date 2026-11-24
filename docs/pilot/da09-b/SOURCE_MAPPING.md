# B — données vers éléments visibles

| Élément | Source | Limite conservée |
|---|---|---|
| Type/statut/nom | LibraryEntry.kind/source_status/name | Catalogue distinct ; VALIDATED non PUBLISHED |
| Marques de l’index | counts.sessions/exercise_slots/prescribed_sets/count_state | Comptes agrégés uniquement ; aucun zéro depuis NULL |
| Séances ordonnées | LibraryDetail.composition[] | Source_ref exact, aucune allocation par jour |
| Mouvements | exercises[].position/id/name | Ordre reçu par position, pas par nom ou zones supposées |
| Unités | rep_targets[].set_index/min_reps/max_reps/is_warmup | Préparation/travail et reliquats exacts, bornes graphiques non physiologiques |
| Sélection/action | selection_ref/domain_launchable/native_support et état courant | Sélection ne crée rien, même callback/start/verify/adopt |
| UNKNOWN/occurrence | LibraryOpeningState.pending et owned.session_id/session_profile | Lecture propriétaire distincte du reçu de création initiale |
| Zones éventuelles | LibraryEntry.zones MAPPED et source_ref exact | Aucun mapping depuis nom ou compte d’exercices |

Primitives/tokens/BodyMap/contrôleurs/SQLite/TIME01 inchangés. Les captions TalkBack et gestes qualifiés pour C ne sont pas transférés à B.
