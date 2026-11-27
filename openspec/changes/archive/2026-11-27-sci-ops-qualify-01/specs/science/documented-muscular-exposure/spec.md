## ADDED Requirements

### Requirement: Qualification liée au paquet exact
Le système SHALL distinguer la qualification d'un candidat contrôlé de celle de l'image effectivement destinée à QA. Le reçu MUST identifier source, image/config/archive, dépendances effectives, profil, chemins, montages et budgets sans réemployer implicitement un PASS d'image historique.

#### Scenario: Source montée sur une ancienne image
- **WHEN** la qualification antérieure utilise un montage du source corrigé sur une image historique
- **THEN** l'image reconstruite et ses chemins opérationnels restent HOLD jusqu'à preuve sur leurs propres octets

#### Scenario: Opération externe en attente
- **WHEN** build cloud, transfert ou qualification distante nécessitent un GO distinct qui n'est pas reçu
- **THEN** la préparation locale continue et l'opération dépendante n'est pas exécutée

#### Scenario: Lecteur qualifié mais lanceur sans configuration SCI
- **WHEN** le lecteur passe sa campagne isolée mais le lanceur QA ne transmet pas flag et références du profil
- **THEN** readiness d'activation reste NO et le raccordement est soumis comme delta ultérieur sans activation implicite

### Requirement: Frontière explicite du contexte V3 public
Le lecteur SHALL conserver le contexte interne intégral pour les digests, reçus, prescriptions et vérifications d’identité admise. Il SHALL émettre uniquement context_ref, equipment_ref, realization_ref, side et load_semantics dans facts[].context ; l’identité reste dans resolution.canonical_exercise_id. Aucun champ inconnu ne SHALL être filtré silencieusement.

#### Scenario: Contexte interne réel à six propriétés
- **WHEN** les services inventory2, évaluation, START, SET et FINISH produisent un contexte contenant une identité canonique conforme au mapping attesté
- **THEN** les quatorze faits conservés sont lisibles dans le DTO strict, sans réécriture des observations, conversion des réglages machine/PER_IMPLEMENT ni perte de provenance

#### Scenario: Contexte historique ou contradictoire
- **WHEN** un contexte historique admis contient les cinq propriétés publiques
- **THEN** sa qualification existante est conservée
- **WHEN** l’identité supplémentaire diverge ou une propriété non admise apparaît
- **THEN** le fait reste conservateur, sans contribution qualifiée ni promotion artificielle
