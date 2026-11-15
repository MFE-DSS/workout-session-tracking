# BODY-01 — checkpoint des ports natifs, sans écran

Parent de branche : `1fd97eba33b8d5bb5682fbe03a58a69d2d30767a` ; parent
canonique : `1462482a4e2bcd1fcde121d6f207a2131616e849`. Suite du même
change et de la Draft PR #407, pas une livraison partielle du produit.

Le checkpoint ajoute le client BODY à négociation exacte, les décodeurs
source-aware fermés, les ressources de lecture et la projection minimale
d'effacement, le stockage des commandes exactes sur un port SQLite et la
reprise explicite vérification/rejeu. Les tests de stockage ferment puis
rouvrent une vraie base fichier, avec partition compte/backend, refus des
reçus divergents et absence d'HTTP si la préparation locale échoue.
Le delta de trainingHistoryResource est uniquement typé ; aucun lecteur de
séances ou contrat poids historique ne change son comportement.

Les helpers serveur d'effacement ne publient que date/identité/version/token,
sans valeurs, spécifications, ratio ou grant. Les routes HTTP nouvelles,
leurs mounts/inventaire, les adaptateurs legacy et les consommateurs visibles
restent non committés jusqu'à leur livraison coordonnée. Aucun attachement
journal, ConnectedApp, template, style, écran ou baseline dans ce checkpoint.

Le reliquat a reçu une revue indépendante puis une relecture corrective :
R01 (valeur héritée hors bornes dans une correction native) et R02 (nouvel
effacement après retrait/redémarrage) sont corrigés dans le worktree.
Les correctifs de composants/SSR et leur preuve ConnectedApp restent hors
commit UI. Les tests Jest de ConnectedApp emploient une vraie base fichier
avec frontières OS et réponses RPC synthétiques ; ils ne sont pas une recette
physique, un rendu approuvé ou la preuve d'un backend servi dans ce commit.

Les campagnes locales et leurs codes de sortie sont conservés dans
`canonical-integration-20261113/BODY_R02_*` hors dépôt. La CI du nouveau HEAD
reste à observer après push ; les CI des checkpoints précédents ne la
remplacent pas. Le master BODY, les pixels SSR/ConnectedApp, la livraison du
reliquat, le parent NUT et les gates release restent ouverts.
Aucun merge/closeout/activation/APK/OTA/déploiement ne découle de ce checkpoint.
