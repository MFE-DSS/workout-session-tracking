## ADDED Requirements

### Requirement: Reuse of admitted current catalogue is confined to one read job
Le worker SHALL confiner la réutilisation du parsing au même job, aux mêmes octets pleinement attestés et aux mêmes limites, avec des vues indépendantes. Chaque bundle SHALL conserver son autorité propre. Aucun cache inter-jobs ou inter-propriétaires n'est introduit.

#### Scenario: Current catalogue was completely attested for this job
- **WHEN** la projection reçoit la vue du catalogue courant déjà vérifiée dans ce même enfant
- **THEN** elle évite le second parsing de ces mêmes octets
- **AND** tous les faits, sources, états, limites et politiques restent identiques

#### Scenario: Valid historical catalogue differs from the current catalogue
- **WHEN** le catalogueB est valide selon son propre pin mais diffère du catalogueA
- **THEN** le lecteur utilise un cache miss et le parsing ordinaire deB
- **AND** il conserve son résultat historique et toutes les vérifications finales du bundle

#### Scenario: Source mismatches its own pin or output exceeds parent admission
- **WHEN** les octets divergent de leur propre pin ou la sortie dépasse un plafond du parent
- **THEN** aucune réutilisation divergente ni réponse faussement admise n'est retournée
- **AND** les plafonds restent inchangés, même si l'enfant a écrit un JSON avant un refus ou une terminaison

### Requirement: Result digest describes the normalized returned response
Le lecteur SHALL calculer le digest de résultat sur le DTO normalisé qu'il retourne, sans modifier les observations, leurs identités ou leurs politiques.

#### Scenario: Admissible integer is normalized to a floating representation
- **WHEN** une valeur numérique admissible change de représentation dans la validation stricte
- **THEN** le digest correspond au DTO final avec le placeholder canonique de digest
- **AND** les faits, droits et données historiques restent inchangés
