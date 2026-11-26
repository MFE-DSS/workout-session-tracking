# Réconciliation proposée — gate distinct, aucune permission actuelle

Le canonique interdit encore tout consommateur produit direct des modules SCI (`test_sci_exposure::test_no_product_module_consumes_the_scientific_layer`, spec SCI V2 §§7/9/16 et tableau des tranches). L’admission d’un contrat descriptif et le GO BUILD doivent porter explicitement sur **l’exception de ce seul lecteur** ; ce brouillon ne modifie pas le contrat canonique à lui seul.

Proposition d’amendement futur : autoriser uniquement `app/services/muscle_observed_load/projection.py` à importer les folds/résolveurs SCI ; garder la garde pour tous les autres modules et les moteurs, interdire tout retour de la projection dans MISSION/allocation, conserver les anciens modules et leur fenêtre started_at. Le nouveau contrat est distinct et annonce completed_at +couverture. Ne pas contourner la garde via import dynamique ou copie de politique.

Le mapping P07 est une source de projection versionnée ; aucune géométrie BodyMap modifiée, P09 non admis, aucune activation/récupération. Legacy garde sa résolution canonique ; charges historiques et identité de progression ne fusionnent pas avec identité SCI. V3 exige son bundle effectif applicable et ses sources, pas une qualification par seul identifiant.

TIME-01 et les findings de recompletion/provenance restent sources lues, jamais corrigées. La lecture déclare UNKNOWN si leur provenance manque ; aucun nouveau timestamp, UUID, writer ou replay mutation.

Le choix worker/OSlimits et la restriction initiale Linux/SQLite sont techniques à approuver dans le GO distinct, pas inclus dans la seule admission SCI. Aucun nouveau secret/dépendance ni maintenance VM. Les qualifications AS/CPU/temps/sortie, API et source restent à exécuter. DATA/release sont indépendants ; feature non activée par défaut.
