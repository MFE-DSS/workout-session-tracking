## ADDED Requirements

### Requirement: Blueprint progressif et traçable
Le contrat MUST distinguer les faits connus, inconnus, conflictuels et non utilisés par consentement. Chaque valeur MUST porter sa provenance et les champs hérités sans date MUST rester sans date. Une priorité déclarée MUST NOT devenir une faiblesse analysée. Le contrat MUST NOT imposer un inventaire matériel.

#### Scenario: Mesures absentes
- **WHEN** taille et poids ne sont pas disponibles
- **THEN** leur valeur reste inconnue et la suffisance dépend uniquement des inputs effectivement requis par la politique applicable

#### Scenario: Salle non caractérisée
- **WHEN** le contexte matériel est inconnu
- **THEN** aucune salle complète ou compatibilité certaine n'est déduite

### Requirement: Décision déterministe et disponibilité honnête
Le contrat de premier plan MUST distinguer insuffisance de données, conflit, absence de politique validée, plan à confirmer et plan prêt. Une prescription MUST porter les versions et origines de dose, répartition, effort, temps et exercices. Un chiffre non soutenu MUST NOT être inventé pour remplir le contrat.

#### Scenario: Blueprint complet mais politique non validée
- **WHEN** les données utilisateur suffisent mais la politique de dose ou de temps manque
- **THEN** la réponse indique POLICY_UNAVAILABLE et ne réclame pas de nouvelles mensurations pour masquer ce manque

#### Scenario: Compatibilité incertaine
- **WHEN** un candidat de plan a un matériel non confirmé
- **THEN** la sortie reste REVIEW_REQUIRED avec confirmation/substitution contextuelle, sans inventaire obligatoire

### Requirement: Non-activation et handoff versionné
Les artefacts de cette tranche MUST rester isolés et non servis. Le handoff MUST distinguer schémas proposés, producteurs actuels, fixtures illustratives et disponibilité réelle. La tranche MUST NOT modifier un modèle partagé ou un contrat visuel.

#### Scenario: Consommateur mobile
- **WHEN** le mobile reçoit le paquet de contrats proposé
- **THEN** il peut vérifier ses fixtures mais ne présente aucun nouvel endpoint ou moteur comme livré
