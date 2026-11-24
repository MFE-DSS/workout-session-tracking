# UX11 — contrat proposé de référence située

Statut : convention d’affichage autorisée pour le build contrôlé le24novembre2026 ; pixels PENDING. Nom de la convention proposée : SAME_RECORDED_CONTEXT_V1. Il s’agit d’une égalité de contexte enregistré pour afficher un fait, pas de comparabilité physiologique, de permission ou de recommandation.

## Ensemble éligible initial
- Profil SCI_V3, un seul canonical_exercise_id `leg-extensions-assises`, sideBILATERAL, load_semanticsMACHINE_DISPLAY_KG. Tous les autres cas restent sur leur consommateur existant ou sans référence. Aucune déclaration que TOTAL_EXTERNAL/PER_IMPLEMENT/unilatéral sont intégrés par cette tranche.
- Même propriétaire/backend, même occurrence/session_id, started_at, binding_digest, se_id, slot_id et intent_id. Réponse strictement validée et toujours liée à l’auth-révision et à la sélection.
- Série source exactement d’indice courant−1 dans ce même exercice ; distincte du set courant. Pas de recherche d’une meilleure ou plus récente performance, pas de repli silencieux vers une série plus ancienne.
- Tous les champs ContextKey connus/non nuls, identiques au contexte capturé courant et cohérents avec binding/exercice : canonical_exercise_id,context_ref,equipment_ref,realization_ref,load_semantics,side. DeuxUNKNOWN égaux ne qualifient rien.
- Observation effective issue d’une lecture serveur : completed=true, reps entier connu≥0, setting.kindMASS_KG/unitkg/valeur finie≥0, revision≥1 et cohérence avec la ligne. Dernière applied_revision exposée à cette lecture ; une correction rendant completedfalse ou settingnull invalide l’éligibilité. Pas d’ancienne version retenue par commodité.
- Source exclusivement observation.setting/reps. Jamais prescription.setting, prefillLegacy, currentSetFactV3 à priorité locale, outbox, brouillon, seul ACK ou export historique. Une commande locale en attente/refusée/modifiée sur cette source invalide la référence jusqu’à relecture/résolution.

## Sens de la comparaison
La valeur peut être différente du réglage actuel : on compare le CONTEXTE et l’unité, pas l’égalité des nombres. Aucun multiplicateur machine, total d’une paire, conversion ou ordre de difficulté déduit. Le libellé est « Série précédente enregistrée » / « même contexte enregistré ». Pas « vous pouvez », « recommandé », « plus fort » ou « mieux récupéré ».

Le contexte enregistré n’atteste pas physiquement la persistance d’une installation entre deux manipulations. Aucune conclusion de sécurité/capacité ne résulte de cette présentation. Un fait antérieur ne devient pas une prescription et ne réadmet pas une autorité retirée.

## Temps et version
Sélection par ordre de série, jamais par tri de performed_at ou promesse de dernière performance globale. Conserver heure déclarée, flag estimated et completed_at selon leurs contrats séparés ; le flag d’ajustement n’est pas fourni par le readModel et n’est pas inventé. Aucun âge/temps écoulé précis, TTL ou seuil de fraîcheur scientifique créé. read_id/rows_read_at qualifient seulement la lecture de l’index. Le détail SCI n’a pas ces champs : conserver son server_now comme date serveur de détail, avec binding/révision. Aucun de ces temps ne devient l’heure de réalisation.

## Absence et incertitude
Source absente/incomplète/inconnue ou réseau défaillant → pas de valeur comparable. Libellé compact « Référence indisponible », raison sur demande ; ne pas dire « aucun historique » si lecture inconnue. Après background/coldrestore, aucune réutilisation de source persistée : lecture courante à obtenir. L’UI de travail conserve ses propres restrictions, sans dépendre d’une réussite de la référence.

## Contrat historique préservé
Les listes inter-occurrences restent comparisonNON_COMPARABLE. Le helper comparisonKey de trainingHistory vérifie seulement une partie du contexte et ne suffit pas. Cette proposition ne l’étend pas en autorité scientifique ni en sélecteur de faits.
