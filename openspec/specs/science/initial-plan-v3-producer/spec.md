# science/initial-plan-v3-producer Specification

## Purpose
Produire et valider un premier plan V3 scientifiquement admis pour le profil observé limité, en distinguant applicabilité, incertitude temporelle, reconnaissance du plan et permission scientifique. Aucun runtime ni bootstrap positif n’est activé par cette capacité.

## Requirements

### Requirement: Actual limited authority before positive output
Le producteur v3 SHALL accepter uniquement un registre successeur réellement revu et admis pour le bundle exact. La forme du schéma, un GO BUILD ou un label fourni dans la requête SHALL NOT constituer une admission.
#### Scenario: Synthetic user through the real producer
- WHEN un utilisateur synthétique satisfait toutes préconditions du binding réellement admis
- THEN la sortie générée est vérifiée par les modèles v3 et le validateur canonique du profil admis, sans autorité de test ni activation runtime.

### Requirement: Bounded applicability and unchanged historical sources
Le scope initial SHALL être adulte déclaré non clinique, hypertrophie, deux séances/semaine et limitations explicitement vides. V1/v2/v3 et leurs validateurs/artefacts historiques SHALL rester inchangés ; un nouveau profil d’autorité SHALL être distingué d’un nouveau contrat.
#### Scenario: Unsupported third session or unresolved limitation
- WHEN cadence3 ou limitation non résolue est présente
- THEN le binding limité ne l’admet pas depuis l’ancien périmètre2–3 ou un souhait utilisateur.

### Requirement: Observed feasibility before positive output
Chaque slot positif SHALL référencer contexte/réalisation/appareil/côté et source actuels. Un réglage observé SHALL être une référence provisoire effectivement qualifiée et acceptée au présent. Le premier binding positif SHALL accepter uniquement ce mode ; charge inconnue/bootstrap SHALL rester hors résultat positif plutôt que prétendre CONFIRMED depuis la seule disponibilité. Préoccupation/interruption SHALL NOT engendrer une charge automatique.
#### Scenario: Unknown gym inventory with known selected contexts
- WHEN l’inventaire global est inconnu et les sept réalisations consommées sont confirmées dans leur contexte propre
- THEN l’inconnu global est conservé et aucune liste obligatoire d’inventaire ou salle complète n’est inférée.
#### Scenario: Concern without an admitted restart rule
- WHEN une préoccupation ou un prédécesseur bloqué reste non résolu
- THEN le chemin positif et le retry automatique sont refusés.

### Requirement: Independent validation and exact fingerprints
Le validateur canonique du profil admis SHALL vérifier les invariants d’allocation/dose/candidats/protocole/projection/temps/autorité indépendamment de la construction du producteur, puis recomputer sa sortie strictement. Les empreintes existantes SHALL lier sujet/snapshot/révision/observations et ack exact.
#### Scenario: Permissive schema or copied boolean substitution
- WHEN une enveloppe syntaxiquement valide diffère de la décision canonique, d’une source ou d’un type numérique attendu
- THEN elle est refusée malgré les labels positifs ou l’égalité booléenne permissive.

### Requirement: Permission and runtime remain separate
SCIENTIFICALLY_READY avec BUDGET_UNCERTAIN SHALL rendre REQUIRES_TIME_ACK sans reconnaissance explicite applicable. ELIGIBLE SHALL exiger l’ack du plan/temps/politique exacts et une autorité toujours applicable ; cela SHALL NOT créer une commande de séance ou un déploiement.
#### Scenario: Policy or plan changes after acknowledgment
- WHEN le binding, le contexte ou le plan reconnu change ou est retiré
- THEN l’ancienne sortie/ack ne permet plus le handoff, sans replay automatique ou succès déduit.

### Requirement: No inferred bootstrap feasibility
Le protocole C3 SHALL préparer les observations sans autoriser une série de travail à charge inconnue. Le contrat v3 et son champ CONFIRMED SHALL rester inchangés ; l’extension positive aux slots non calibrés SHALL demander sa propre résolution/admission, pas un statut plus optimiste.
#### Scenario: Available equipment without an observed achievable prescription
- WHEN un dispositif est identifié mais la plage/réalisation n’a pas été qualifiée par une tentative courante acceptée
- THEN le premier binding conserve un draft/revue et DENIED, sans SCIENTIFICALLY_READY ou réglage fabriqué.
