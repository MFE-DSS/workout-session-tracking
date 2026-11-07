## MODIFIED Requirements

### Requirement: Six-gate assessment of the effective bundle
Le système SHALL évaluer séparément C1 population, C2 dose, C3 protocole, C4 sélection/réalisation, C5 représentation et C6 temps/politique sur le bundle/version/SHA effectifs et le profil de readiness nommé. Un GO BUILD SHALL NOT constituer une admission. Les anciennes évaluations v1/v2 et leurs pins SHALL rester inchangés. Le profil v3 exploratoire SHALL distinguer C6 EXPLORATION_POLICY_ADMITTED d’une preuve de durée SUPPORTED ; aucune gate scientifique non acquise SHALL être masquée par un ack.
#### Scenario: Effective producer remains unadmitted
- WHEN les inputs suffisent mais une condition requise du profil réellement admis manque
- THEN aucun résultat scientifique positif n’est admis et le manque précis est conservé.
#### Scenario: C6 exploration is explicitly admitted for v3
- WHEN C1–C5 et le protocole sont admis sur le bundle exact, et la politique exploratoire v3 est explicitement admise
- THEN la sortie peut porter science positive et BUDGET_UNCERTAIN, sans affirmer durée ou fit positifs et sans droit de démarrage avant ack applicable.

### Requirement: Positive time authority
Les profils READYv1/v2 et le mode SUPPORTED v3 SHALL conserver leur exigence de borne haute applicable couvrant travail/repos/préparation/calibration/opérations. Sans preuve applicable, cette durée SHALL rester UNKNOWN. Le profil exploratoire v3 séparément approuvé SHALL admettre seulement la gouvernance de cette incertitude : borne négative applicable, reconnaissance du plan exact, arrêt/limite et faits incomplets préservés. Il SHALL NOT déclarer l’ancienne gate de temps positif satisfaite ou utiliser des secondes fictives.
#### Scenario: Complete synthetic timing intervals
- WHEN des intervalles synthétiques donnent un diagnostic conditionnel favorable
- THEN ils ne constituent pas une preuve de temps futur ou une autorité pour SUPPORTED.
#### Scenario: Partial rests below budget
- WHEN la borne de repos sous structure réellement liée au binding est sous le budget mais les autres durées sont inconnues
- THEN BUDGET_UNCERTAIN demeure, et seule une politique exploratoire admise peut autoriser une reconnaissance pour commencer sans promesse d’achèvement.

### Requirement: Isolated proposal and PLAN handoff
Le scope historique négatif étape1 SHALL rester livré, piné et rejouable. La présente préparation SHALL rester documentaire ; le change science-initial-policy-v3-producer SHALL être propriétaire unique du prochain apply SCI positif seulement après ses décisions et GO propres. Le parent science-initial-plan-policy SHALL rester ouvert jusqu’à ses critères effectifs. Les autres préparations ARCH ne SHALL NOT être appliquées concurremment sur les mêmes registres. PLAN SHALL recevoir binding/admission réels, sources et limites, sans API/UI/SDK ou séance possédée revendiqués par ce scope.
#### Scenario: No separate stage2 functional GO
- WHEN seule une préparation ou une ancienne autorisation étape1 existe
- THEN aucun registre/binding/producteur positif nouveau n’est implémenté ou publié.

#### Scenario: No separate functional GO BUILD
- WHEN le mandat autorise assessment/design sans GO fonctionnel distinct
- THEN corrections, tests exécutables, schémas et registre d’admission restent des travaux futurs non appliqués.
