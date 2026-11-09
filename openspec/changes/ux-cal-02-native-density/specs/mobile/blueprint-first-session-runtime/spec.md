## ADDED Requirements

### Requirement: Compact calibration composition preserves scientific meaning
Le consommateur natif SHALL présenter une seule action dominante par étape,
un titre court, un contexte compact et un porteur de réglage/unité. Il SHALL
subordonner les détails sans supprimer les faits nécessaires, UNKNOWN,
conditions d'arrêt, qualification provisoire ou acquittement temporel exact.
Les composants globaux, MISSION et l'exécution LOCKED SHALL rester inchangés.
#### Scenario: Machine and per-implement contexts share one instrument
- WHEN une rencontre machine ou RDL est affichée
- THEN le même présentateur conserve kg affichés ou kg par haltère sans totalisation ni charge recommandée et sans répétition du réglage dans un autre module visible.
#### Scenario: Current instruction is unavailable
- WHEN résultat/autorité est absent, retiré ou bloqué par préoccupation
- THEN aucune compacité ou réouverture de détails ne recrée une permission physique et les faits historiques restent accessibles.

### Requirement: Negotiated calibration tuples are cross-validated by the client
Le client SHALL recouper inventaire demandé/réémis, profils, candidat,
intention, réalisation, policy et sémantique de réglage avec les capacités et
la rencontre courantes du même propriétaire. Il SHALL NOT convertir ou réparer
une incohérence. Ce contrôle SHALL NOT remplacer l'autorité SCI serveur.
#### Scenario: A supported candidate carries another intention or setting semantic
- WHEN le DTO d'un candidat porte une intention/réalisation/policy ou une unité de masse incompatible avec son profil négocié
- THEN le nouveau guidage est refusé côté client, brouillon/faits conservés, sans downgrade ou succès inventé.
#### Scenario: Historical observations differ from the current choice
- WHEN une ancienne observation est valide dans son propre contexte mais son réglage diffère du choix courant
- THEN les faits restent conservés sans promouvoir cet ancien réglage en permission actuelle.

### Requirement: Applicable help is available before encounter mutation
L'aide SHALL être disponible avant ouverture et limitée aux conditions
communes, à la réalisation sélectionnée et aux règles d'arrêt pertinentes du
matériau publié contrôlé. Elle SHALL NOT afficher le protocole d'un autre
exercice, réécrire les règles admises ou prendre la place d'une notice réelle.
#### Scenario: Selected RDL has no opened encounter yet
- WHEN les capacités et le matériau applicables sont présents et RDL est sélectionné
- THEN l'aide du RDL est lisible sans POST d'ouverture, sans source de machine différente ni valeur initiale proposée.
#### Scenario: Material integrity or expected section is absent
- WHEN source/hash/section requis manque ou diverge
- THEN l'aide indique son indisponibilité sans fallback instructif ; aucune nouvelle consigne physique issue de cette projection n'est présentée.

### Requirement: Compact factual forms preserve recovery and accessible actions
La présentation SHALL conserver champs factuels distincts et absence de défaut
positif, occurrence réelle, réglage utilisé séparé du choisi, drafts possédés et
reçus idempotents. Les sous-étapes UI SHALL NOT muter le ledger ou donner une
permission. Les commandes SHALL garder cibles tactiles et accès clavier/grande
fonte/focus/back, sans action obligatoire dissimulée.
#### Scenario: Observation substep is interrupted or its response is lost
- WHEN l'app reprend un brouillon ou retrouve le reçu exact d'un enregistrement
- THEN tous les faits restent récupérables, aucune date/acceptation n'est créée automatiquement et un reçu acquis empêche un ancien formulaire de rouvrir la mutation.
#### Scenario: Large text or visible keyboard consumes screen space
- WHEN fonte agrandie ou clavier décimal est actif
- THEN entrée, unité, consignes nécessaires et action restent lisibles/atteignables par le parcours natif, sans crop ou geste qui confirme implicitement une donnée.
