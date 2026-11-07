## MODIFIED Requirements

### Requirement: Reviewed authority before implementation
Tout binding, producteur positif ou activation SHALL attendre ses décisions et périmètres approuvés. Le stage1 v3 reste livré inchangé. Le stage2 isolé SHALL être réalisé seulement après revue du cas C1–C6 et GO BUILD explicite ; son admission SHALL être distincte de la réussite des tests et de toute activation PLAN.
#### Scenario: Stage1 approval only
- WHEN seule la décision « Valider v3 et ce build isolé » existe
- THEN elle ne publie pas de registre ou producteur positif et le stage2 reste proposé.
#### Scenario: Stage2 isolated build and policy decisions received
- WHEN le cas limité et son scope de réalisation reçoivent leurs décisions applicables
- THEN registre/producteur/validation positive du profil v3 peuvent être réalisés sans modifier les contrats historiques ni activer API/UI/runtime.

#### Scenario: Preparatory packet contains recommended admission labels
- WHEN un paquet reçu comporte ADMIT et une recommandation RouteB à approuver
- THEN il est conservé comme source de doctrine, sans ajouter automatiquement des bindings dans un registre ni générer une fixture READY.
