# Spec Delta — mobile/navigation-shell

## Purpose

Définit la structure de navigation durable de l'app native : les espaces de premier niveau, la place de la séance au-dessus d'eux, la priorité de la reprise et le comportement du retour, pour que chaque espace migré ait une place sans réinventer comment on l'atteint.

## ADDED Requirements

### Requirement: Espaces de premier niveau
Une fois connecté, l'utilisateur MUST atteindre chaque espace de premier niveau approuvé par l'opérateur depuis une barre d'onglets persistante, en un seul geste, depuis n'importe quel autre espace.

#### Scenario: Changer d'espace
- **WHEN** l'utilisateur est dans l'espace PROFIL et touche l'onglet de la MISSION
- **THEN** la MISSION du jour s'affiche, et l'état de l'espace PROFIL est conservé pour y revenir

### Requirement: La séance au-dessus des onglets
Démarrer ou reprendre une séance MUST ouvrir l'exécution en plein écran, sans barre d'onglets ; terminer ou abandonner MUST ramener à la coque ; mettre en pause MUST montrer la reprise, la séance restant ouverte (voir « Priorité de la reprise »).

#### Scenario: Démarrer depuis la MISSION
- **WHEN** l'utilisateur touche « Démarrer » sur la MISSION
- **THEN** l'écran d'exécution occupe tout l'écran et aucune barre d'onglets n'est visible pendant les séries et le repos

#### Scenario: Fin de séance
- **WHEN** l'utilisateur ferme le bilan
- **THEN** la coque réapparaît sur l'espace de la MISSION

#### Scenario: Abandon
- **WHEN** l'utilisateur abandonne la séance
- **THEN** la coque réapparaît sur l'espace de la MISSION

#### Scenario: Pause
- **WHEN** l'utilisateur met la séance en pause
- **THEN** l'écran de reprise s'affiche en plein écran, sans barre d'onglets

### Requirement: Priorité de la reprise
À l'ouverture de l'app, une séance ouverte (locale ou serveur) MUST être proposée en reprise avant tout espace, quel que soit l'onglet actif à la fermeture.

#### Scenario: Relance avec une séance ouverte
- **WHEN** l'app est relancée alors qu'une séance est ouverte et que l'onglet PROGRÈS était actif
- **THEN** l'écran de reprise s'affiche d'abord

### Requirement: Connexion hors de la coque
Sans session valide, l'utilisateur MUST voir la connexion et aucun espace ; après connexion, la coque s'ouvre sur l'espace de la MISSION (ou la reprise).

#### Scenario: Session expirée
- **WHEN** le rafraîchissement du jeton est refusé
- **THEN** l'écran de connexion s'affiche et aucun onglet n'est atteignable

### Requirement: Retour Android dans la coque
Sur Android, le retour matériel MUST dépiler l'écran courant d'un espace ; à la racine d'un espace autre que le premier, il MUST ramener au premier espace ; à la racine du premier espace, il MUST suivre le système. Pendant une séance, les règles de `mobile/android-platform` s'appliquent.

#### Scenario: Retour depuis la racine de PROFIL
- **WHEN** l'utilisateur est à la racine de PROFIL et appuie sur retour
- **THEN** l'espace de la MISSION s'affiche

### Requirement: Espace non migré
Un espace dont les fonctions ne sont pas encore migrées MUST afficher un état qui représente le domaine sans inventer de contenu, et AU PLUS une action (par exemple ouvrir la fonction sur le site) ; il MUST NOT afficher de données fictives.

#### Scenario: PROGRÈS avant migration
- **WHEN** l'utilisateur ouvre PROGRÈS avant MOB-05
- **THEN** l'espace dit ce qu'il contiendra, sans chiffre inventé, avec au plus un lien vers la page web existante

### Requirement: Surfaces verrouillées inchangées
L'introduction de la coque MUST NOT modifier le rendu des écrans verrouillés ; la barre d'onglets est une surface nouvelle soumise à la revue visuelle de l'opérateur avant tout commit.

#### Scenario: Gate visuelle
- **WHEN** la coque est introduite
- **THEN** la gate du contrat visuel reste identique au pixel sur toutes les baselines existantes
