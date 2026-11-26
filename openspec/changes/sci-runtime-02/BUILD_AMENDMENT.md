# SCI-RUNTIME-02 — amendement technique minimal à autoriser

26 novembre2026 — Europe/Paris. **GO BUILD REÇU le 26 novembre2026**, `call_12d65838fae34f55aee3aee31ea82f69` : « Autoriser ce correctif SCI-RUNTIME-02 ». Parent frais c454af863278b0801a568437038eb4efb94db588. [Reçu des essais](../../../docs/science/sci-runtime-02/QUALIFICATION_RECEIPT.md).

## Défaut prouvé
Worker → projection → exercise_identity.normalize → models.exercise → app.database → get_settings. L'environnement enfant supprime DATABASE_URL ; le défaut tente mkdir('/opt/auren/var') sur source readonly. Trace réelle EROFS ; retour1 avant la captation. La suite Linux pure donne126PASS/1FAIL, sans skip. Aucun dépassement du catalogue, de CPU ou d'AS n'est démontré par cet échec.

## Delta proposé — deux fichiers produit/test
- `app/services/muscle_observed_load/worker.py` : immédiatement après install_limits() et avant tout import applicatif, importer os et affecter **fixement** `os.environ["DATABASE_URL"] = "sqlite:///:memory:"`, avec commentaire expliquant l'ORM incident.
- `tests/test_muscle_observed_load_worker.py` : régression subprocess prouvant l'absence de création du répertoire par défaut dans une source non inscriptible, environnement parent exclu, vraie capture propriétaire sur son URI séparé et absence de mutation. Conserver tous les tests existants.
- Documents du seul change et reçu de qualification, sans autre modification produit.

L'URL réelle de captation reste `sys.argv` → `open_owned_capture`, mode=ro/query_only/authorizer/snapshot. Ne pas utiliser cette URL comme configuration ORM, ne pas hériter du parent, ne pas employer setdefault. Aucun writer, algorithme, SCI, TIME-01 ou contrat DTO modifié.

## Gates après GO distinct
RED→GREEN, vraie campagne Linux readonly et HTTP/SQL/ressources/owner/snapshot ; régénérer uniquement le profil de test depuis le HEAD réel. check_scope/broad/ruff/budget/Bandit/Gitleaks/protocole/OpenSpec ; revue indépendante ; CI protégée HEAD exact ; merge/closeout sous GOV-MERGE-01 sans nouveau GO routinier. Toute limite non qualifiée garde HOLD ; aucune hausse de budget.

## Exclusions
Aucun `.github/workflows`, Dockerfile, supervisor.py, config.py, SOURCE_PINS historique, .gitleaksignore, source SCI, migration, VPS, secret, activation QA, donnée réelle, APK/OTA ou UI. Si un runner/config d'infrastructure distinct devient nécessaire, son delta gardera une décision séparée. La qualification du candidat émulé ne se transfère pas automatiquement à l'hôte QA amd64 natif.

## Décision reçue
**Autoriser le correctif de bootstrap SCI-RUNTIME-02 dans ces deux fichiers et sa vérification complète.** La phase6 exigeait un GO propre avant tout changement de code/CI. Le GO cité en tête autorise désormais ce delta ; les résultats avant/après sont conservés séparément.
