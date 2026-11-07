# science/initial-policy-admission Specification

## Purpose
Documenter le diagnostic isolé d’admission négative et ses limites ; aucune admission positive ou activation runtime ne découle de ce scope.

## Requirements

### Requirement: Six-gate assessment of the effective bundle
Le système SHALL évaluer séparément C1 population, C2 dose, C3 protocole, C4 sélection/réalisation, C5 représentation et C6 temps/politique sur le bundle/version/SHA effectifs et le profil de readiness nommé. Un GO BUILD SHALL NOT constituer une admission. Les anciennes évaluations v1/v2 et leurs pins SHALL rester inchangés. Le profil v3 exploratoire SHALL distinguer C6 EXPLORATION_POLICY_ADMITTED d’une preuve de durée SUPPORTED ; aucune gate scientifique non acquise SHALL être masquée par un ack.
#### Scenario: Effective producer remains unadmitted
- WHEN les inputs suffisent mais une condition requise du profil réellement admis manque
- THEN aucun résultat scientifique positif n’est admis et le manque précis est conservé.
#### Scenario: C6 exploration is explicitly admitted for v3
- WHEN C1–C5 et le protocole sont admis sur le bundle exact, et la politique exploratoire v3 est explicitement admise
- THEN la sortie peut porter science positive et BUDGET_UNCERTAIN, sans affirmer durée ou fit positifs et sans droit de démarrage avant ack applicable.

### Requirement: Bounded population and explicit conventions

L'admission SHALL préciser adulte déclaré, non clinique, hypertrophie, cadence 2–3 et limitations explicitement renseignées. Deux séries/intention, 8–12 reps, cible subjective 2 RIR et repos 120/90 SHALL être revus séparément avec leur nature de convention et leurs limites ; ils SHALL NOT être présentés comme optima ou preuve que le bundle entier est conservateur.

#### Scenario: Nonempty limitations
- **WHEN** une limitation est déclarée sans procédure admise applicable
- **THEN** l'admission du périmètre sans limitation ne l'englobe pas et aucune autorisation clinique n'est inférée.

### Requirement: Honest bootstrap and calibration state

Le protocole SHALL séparer réglage observé accepté, précision du RIR et première charge inconnue. Ancien historique seul SHALL NOT signifier calibration en cours. Un épisode préoccupant ou une reprise sans autorité SHALL rester bloquant ; aucun incrément/kg froid ou durée de préparation inventé SHALL combler l'absence de preuve.

#### Scenario: Historical attempt with no current episode activity
- **WHEN** seules des tentatives antérieures à started_at sont présentes, sans événement courant qualifiant ni problème demandant revue
- **THEN** la sortie proposée est NEEDS_CALIBRATION avec charge inconnue et l'historique demeure intact.

#### Scenario: Unknown reported RIR
- **WHEN** le RIR déclaré manque mais une tentative et son acceptation satisfont le protocole opérationnel admis
- **THEN** le réglage peut rester provisoire et effort_sufficiency UNKNOWN sans inventer de vrai RIR.

### Requirement: Exact selection binding with limited realization

L'admission SHALL lier intentions/candidats/curation/pull/réalisation/G17/contexte/exclusions et inconnus à une version et aux digests complets. Les quatre candidats pull retenus inutilisés SHALL NOT être une condition artificielle d'admission du plan qui ne les utilise pas. Disponibilité SHALL NOT prouver réalisation ou calibration.

#### Scenario: Neutral pull without qualified realization
- **WHEN** G17 est seulement AVAILABLE sans réalisation directement qualifiée
- **THEN** le rôle conditionnel nouveau n'est pas appliqué comme fait acquis et la sélection ne devient pas exécutable par ce seul label.

### Requirement: Versioned readiness meaning

Les invariants READY v1 SHALL rester intacts : allocation revue, exposition exacte quinze zones, faisabilité confirmée, durée admise dans budget et prescriptions complètes. Si un successeur retient projection qualitative ou réglage non massique/bootstrap au sens différent, il SHALL définir un contrat versionné et une revue coordonnée des consommateurs avant apply. La complétude d'une déclaration de quinze zones SHALL NOT être confondue avec un crédit exact ou croissance connue.

#### Scenario: Qualitative v2 draft presented as v1 READY
- **WHEN** un draft sans exposition numérique calculée ni prescriptions v1 complètes est présenté au validateur v1
- **THEN** il ne reçoit pas READY et aucune gate v1 n'est assouplie pour l'accepter.

### Requirement: Positive time authority
Les profils READYv1/v2 et le mode SUPPORTED v3 SHALL conserver leur exigence de borne haute applicable couvrant travail/repos/préparation/calibration/opérations. Sans preuve applicable, cette durée SHALL rester UNKNOWN. Le profil exploratoire v3 séparément approuvé SHALL admettre seulement la gouvernance de cette incertitude : borne négative applicable, reconnaissance du plan exact, arrêt/limite et faits incomplets préservés. Il SHALL NOT déclarer l’ancienne gate de temps positif satisfaite ou utiliser des secondes fictives.
#### Scenario: Complete synthetic timing intervals
- WHEN des intervalles synthétiques donnent un diagnostic conditionnel favorable
- THEN ils ne constituent pas une preuve de temps futur ou une autorité pour SUPPORTED.
#### Scenario: Partial rests below budget
- WHEN la borne de repos sous structure réellement liée au binding est sous le budget mais les autres durées sont inconnues
- THEN BUDGET_UNCERTAIN demeure, et seule une politique exploratoire admise peut autoriser une reconnaissance pour commencer sans promesse d’achèvement.

### Requirement: Integrity and invalidation

Toute autorité future SHALL vérifier policy/engine/bundle/evidence/versions et fingerprints par recomputation canonique sensible aux types, sans label client faisant foi. Retrait/changement d'une source admise ou de son contexte SHALL invalider une décision avant nouveau handoff. Les anciens pins/rejeux SHALL rester reproductibles.

#### Scenario: Numeric boolean substitution
- **WHEN** un booléen de l'enveloppe est remplacé par 0 ou 1
- **THEN** le futur vérificateur refuse l'enveloppe malgré l'égalité permissive Python et conserve le résultat canonique recalculé.

### Requirement: Isolated proposal and PLAN handoff
Le scope historique négatif étape1 SHALL rester livré, piné et rejouable. La présente préparation SHALL rester documentaire ; le change science-initial-policy-v3-producer SHALL être propriétaire unique du prochain apply SCI positif seulement après ses décisions et GO propres. Le parent science-initial-plan-policy SHALL rester ouvert jusqu’à ses critères effectifs. Les autres préparations ARCH ne SHALL NOT être appliquées concurremment sur les mêmes registres. PLAN SHALL recevoir binding/admission réels, sources et limites, sans API/UI/SDK ou séance possédée revendiqués par ce scope.
#### Scenario: No separate stage2 functional GO
- WHEN seule une préparation ou une ancienne autorisation étape1 existe
- THEN aucun registre/binding/producteur positif nouveau n’est implémenté ou publié.

#### Scenario: No separate functional GO BUILD
- WHEN le mandat autorise assessment/design sans GO fonctionnel distinct
- THEN corrections, tests exécutables, schémas et registre d’admission restent des travaux futurs non appliqués.

### Requirement: Isolated negative admission evaluation

L'étape1 autorisée SHALL recomputer le vrai résultat v2 sous comparaison JSON sensible aux types, puis produire ses diagnostics successeurs de calibration et de borne basse sûre avec six gates NOT_ADMITTED depuis un registre vide piné. Elle SHALL conserver le code et les artefacts historiques. Elle SHALL NOT fournir candidat exécutable, READY, nouveau transport mobile ou admission positive.

#### Scenario: Empty registry and sufficient inputs
- **WHEN** une évaluation historique valide est fournie avec inputs suffisants et le registre livré sans binding
- **THEN** le résultat versionné porte NOT_ADMITTED/NOT_SERVED, les empreintes de requête/évaluation/admission et les raisons C1..C6 sans plan.

#### Scenario: Known disjoint lower bound without upper bound
- **WHEN** une composante valide de même source/périmètre est disjointe et possède seulement une borne basse
- **THEN** la borne peut réfuter cette configuration sans raccourcir les repos, sans double compte, ni affirmation de fit ou Duration admise.

## Autorisation et limites conservées

[GO étape1](../../../changes/archive/2026-11-07-science-initial-policy-admission/BUILD_AUTHORIZATION.md). L’archive couvre uniquement les trois durcissements, registre vide, évaluateur et fixtures de refus ; les critères positifs non acquis restent dans le parent et docs/proposals/science-initial-policy-positive-admission.md.
