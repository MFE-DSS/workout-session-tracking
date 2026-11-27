## ADDED Requirements

### Requirement: Statut autoritaire après finalisation du worker
Le worker SHALL choisir le succès uniquement après fermeture de la capture readonly, validation du DTO et de son digest, encodage borné et écriture/flush réussis. La terminaison explicite MUST préserver les refus et ne SHALL pas augmenter les budgets.

#### Scenario: Résultat valide puis finalisation échouée
- **WHEN** une fermeture, écriture ou un flush nécessaire échoue
- **THEN** le processus ne termine pas avec succès et le parent refuse toute sortie partielle

#### Scenario: Résultat valide et finalisé
- **WHEN** toutes les obligations sont satisfaites
- **THEN** le worker termine explicitement avec statut0 sans teardown général, et le parent conserve ses validations indépendantes

#### Scenario: Signal ou limites dépassées
- **WHEN** l’enfant reçoit SIGXCPU ou une autre terminaison par signal
- **THEN** le parent refuse la sortie, reap l’enfant et libère son slot sans promotion d’un JSON valide
