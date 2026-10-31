# Spec Delta — mobile/internal-distribution

## Purpose

Définit comment un build installable hors Store est produit pour un testeur identifié, contre quel backend il travaille, et le parcours pilote qu'il doit permettre de bout en bout.

## ADDED Requirements

### Requirement: Build interne installable
Un build interne Android MUST être installable directement sur un téléphone (APK signé), sans Store, sans serveur de développement et sans câble ; il MUST NOT être un build de publication Store.

#### Scenario: Installation par le testeur
- **WHEN** le testeur ouvre le lien d'installation sur son téléphone Android et autorise l'installation
- **THEN** l'application s'installe et démarre sans Metro ni connexion au poste de l'opérateur

### Requirement: Backend fixé au build
Un build interne MUST viser le backend de production en HTTPS, fixé au moment du build ; il MUST NOT viser une adresse de réseau local ni du HTTP en clair.

#### Scenario: Démarrage hors du réseau de l'opérateur
- **WHEN** le testeur lance l'application sur un réseau mobile
- **THEN** l'écran de connexion s'affiche et la connexion s'établit avec `https://spignos.com`

### Requirement: Parcours pilote de bout en bout
Le build interne MUST permettre : ouvrir l'app, se connecter, charger MISSION, démarrer la séance proposée, enchaîner les exercices, enregistrer séries, répétitions et charge là où c'est supporté, utiliser le repos, terminer, voir le bilan, puis relancer et retrouver l'état.

#### Scenario: Séance complète
- **WHEN** le testeur se connecte, démarre la séance proposée et valide toutes ses séries
- **THEN** le bilan s'affiche et la séance terminée est visible côté serveur pour son compte

#### Scenario: Relance au milieu d'une séance
- **WHEN** le testeur ferme l'application au milieu d'une séance puis la relance
- **THEN** l'écran de reprise s'affiche avec sa position, et les séries déjà validées sont conservées

### Requirement: Mêmes contrats que l'iPhone
Le build interne Android MUST utiliser les mêmes contrats serveur que le client iOS (`/api/mobile/v1`, sessions d'appareil révocables) ; aucune règle d'entraînement n'est décidée sur l'appareil.

#### Scenario: Même compte sur deux plateformes
- **WHEN** un même compte se connecte depuis Android puis depuis l'iPhone
- **THEN** les deux voient la même MISSION et le même historique serveur, et chaque appareil a sa propre session révocable

### Requirement: États d'erreur et hors ligne
Pendant le pilote, une perte de réseau ou un backend indisponible MUST produire un état lisible et une reprise possible ; une série validée hors ligne MUST être gardée sur l'appareil puis envoyée au retour du réseau.

#### Scenario: Série validée sans réseau
- **WHEN** le testeur valide une série alors que le téléphone n'a plus de réseau
- **THEN** la série est gardée sur l'appareil, l'écran le signale, et elle est envoyée au serveur quand le réseau revient

#### Scenario: Backend indisponible au démarrage
- **WHEN** le backend ne répond pas au chargement de MISSION
- **THEN** l'écran « Hors ligne » s'affiche avec une action « Réessayer », et rien d'enregistré n'est perdu

### Requirement: Compte rendu de passe appareil
Chaque build interne remis à un testeur MUST être accompagné d'une passe consignée : référence du build, appareil et version d'Android, flux supportés, captures des écrans critiques, bugs connus, bloquants, divergences de plateforme, checklist réussite/échec.

#### Scenario: Remise au testeur
- **WHEN** un build interne est remis au testeur
- **THEN** le rapport de sprint contient sa référence, la checklist passée sur émulateur, et la checklist à rejouer par le testeur
