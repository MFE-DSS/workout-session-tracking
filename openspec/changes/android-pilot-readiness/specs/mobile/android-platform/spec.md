# Spec Delta — mobile/android-platform

## Purpose

Définit ce que le client mobile AUREN fait de propre à Android — retour matériel, clavier, identité d'appareil, barres système, notification de repos — pour que le même parcours que sur iPhone reste sûr et lisible sur Android.

## ADDED Requirements

### Requirement: Retour matériel pendant une séance
Pendant une séance en cours (série ou repos, hors écran de reprise), le retour matériel Android MUST ouvrir la feuille « Quitter la séance » existante, avec les mêmes choix que le bouton ✕, et MUST NOT quitter l'application ni perdre une série.

#### Scenario: Retour pendant une série
- **WHEN** l'utilisateur appuie sur retour pendant qu'une série est affichée
- **THEN** la feuille « Quitter la séance » s'ouvre et l'application reste au premier plan

#### Scenario: Retour pendant le repos
- **WHEN** l'utilisateur appuie sur retour pendant un repos
- **THEN** la feuille « Quitter la séance » s'ouvre et le compte à rebours continue

### Requirement: Retour matériel sur une feuille ouverte
Quand une feuille est ouverte, le retour matériel SHALL fermer la feuille et rien d'autre, comme son geste de fermeture.

#### Scenario: Fermer la feuille de sortie
- **WHEN** la feuille « Quitter la séance » est ouverte et l'utilisateur appuie sur retour
- **THEN** la feuille se ferme, la séance reprend là où elle était, et aucune commande n'est envoyée

### Requirement: Retour matériel hors séance
Hors séance (connexion, MISSION, reprise, fin de séance, écrans d'attente), le retour matériel SHALL suivre le comportement du système ; l'état enregistré MUST survivre à la sortie et être restauré à la relance.

#### Scenario: Retour sur la reprise puis relance
- **WHEN** l'utilisateur est sur l'écran de reprise, appuie sur retour, puis relance l'application
- **THEN** l'application rouvre sur la reprise avec la même position dans la séance

### Requirement: Saisie visible au-dessus du clavier
Quand le clavier logiciel est ouvert, le champ en cours de saisie et son action de validation MUST rester visibles et atteignables, sur l'écran de connexion comme dans la saisie numérique d'une valeur.

#### Scenario: Connexion au clavier
- **WHEN** l'utilisateur tape son mot de passe sur l'écran de connexion
- **THEN** le champ et le bouton de connexion restent visibles au-dessus du clavier

#### Scenario: Saisie numérique d'une charge
- **WHEN** l'utilisateur ouvre la saisie numérique d'une charge et le clavier apparaît
- **THEN** la valeur saisie et sa validation restent visibles

### Requirement: Identité de la session d'appareil
La session d'appareil créée à la connexion MUST porter une étiquette tirée de la plateforme et du modèle réels ; elle MUST NOT annoncer une autre plateforme.

#### Scenario: Connexion depuis Android
- **WHEN** un utilisateur se connecte depuis un téléphone Android
- **THEN** la session d'appareil enregistrée côté serveur est étiquetée Android avec le modèle de l'appareil, jamais « iPhone »

### Requirement: Aucun écran ne déborde
Sur Android, chaque écran du parcours pilote MUST tenir dans la zone sûre (barre d'état, barre de navigation gestuelle ou à trois boutons) sans contenu coupé ni recouvert, et MUST conserver les cibles tactiles du produit (44 dp au minimum).

#### Scenario: Barre de navigation à trois boutons
- **WHEN** l'écran d'exécution est affiché avec une barre de navigation à trois boutons
- **THEN** les actions du bas restent entièrement au-dessus de la barre et aucun élément n'est coupé

### Requirement: Notification de fin de repos sur Android
La notification locale de fin de repos SHALL être programmée sur Android sans permission d'alarme exacte ; son retard possible MUST être mesuré et consigné ; l'écran reste la vérité du temps de repos.

#### Scenario: Application en arrière-plan pendant le repos
- **WHEN** l'application passe en arrière-plan pendant un repos
- **THEN** une notification locale est programmée pour la fin du repos, et à la reprise l'écran affiche le temps réel restant ou la série suivante

### Requirement: Consignation des divergences de plateforme
Toute différence de comportement ou de rendu entre iOS et Android MUST être consignée explicitement (quoi, pourquoi, mesure) ; aucune refonte visuelle propre à Android n'est permise sans revue de l'opérateur.

#### Scenario: Divergence de rendu constatée
- **WHEN** un écran verrouillé s'affiche différemment sur Android (police, métrique, rendu SVG)
- **THEN** l'écart est mesuré, documenté et montré à l'opérateur avant tout correctif, et aucune baseline n'est modifiée sans son approbation
