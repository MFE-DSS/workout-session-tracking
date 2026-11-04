# Spec Delta — mobile/session-integration

## Purpose

Définit ce que la séance native garantit en dehors du chemin heureux : ce que l'utilisateur voit de la synchronisation
de chaque série, l'envoi unique d'un démarrage, la reprise, le démarrage de l'app, la substitution refusée ou en
attente, et l'origine de chaque valeur du bilan.

## ADDED Requirements

### Requirement: Vérité de synchronisation par série
L'état affiché de chaque série validée MUST refléter ce que le serveur en a dit (acceptée, refusée, en attente ou inconnue),
y compris après une relance de l'app ; une série acceptée MUST NOT s'afficher comme gardée seulement sur l'appareil.

#### Scenario: Relance après une série acceptée
- **WHEN** une série a été acceptée par le serveur et que l'app est relancée pendant la séance
- **THEN** l'exécution et le bilan la montrent comme reçue par AUREN

#### Scenario: Série refusée
- **WHEN** le serveur refuse une série
- **THEN** la série est montrée comme à vérifier, gardée sur l'appareil, et le compteur d'attention l'inclut

#### Scenario: Détail des séries depuis le bilan
- **WHEN** l’utilisateur ouvre le bouton de détail existant du bilan
- **THEN** les séries réalisées de cette séance sont accessibles par exercice avec leur dernier état persisté : reçue, en attente, refusée-à vérifier ou inconnu
- **AND** une commande locale ou en file n’est jamais présentée comme confirmée

#### Scenario: Retry, doublon ou source devenue indisponible
- **WHEN** une nouvelle commande remplace un ancien accusé ou que le dernier journal n’est plus vérifiable
- **THEN** le bilan reflète le dernier envoi, une seule fois par série, ou indique un état inconnu
- **AND** une réponse tardive ne restaure pas une ancienne confirmation

### Requirement: Envoi unique d'un démarrage
Toucher « Démarrer » ou « Reprendre » MUST montrer un état d'attente jusqu'à la réponse et MUST NOT envoyer une seconde
demande tant que la première n'a pas répondu.

#### Scenario: Double appui
- **WHEN** l'utilisateur touche deux fois « Démarrer » avant la réponse
- **THEN** une seule séance est créée côté serveur

### Requirement: Démarrage sans écran vide
Pendant la restauration ou le rafraîchissement du jeton au lancement, l'app MUST afficher un écran de démarrage
identifiable, jamais un écran vide.

#### Scenario: Lancement lent
- **WHEN** la restauration du jeton prend plus d'un instant
- **THEN** l'écran de démarrage est visible jusqu'à la connexion, la reprise ou la MISSION

### Requirement: Substitution hors chemin heureux
Une demande de substitution MUST avoir un état explicite tant qu'elle n'est pas confirmée ; un refus du serveur MUST
rendre l'exercice d'origine, avec une explication, sans bloquer la suite de la séance.

#### Scenario: Substitution refusée
- **WHEN** le serveur refuse le remplacement demandé
- **THEN** l'exercice d'origine reste à l'écran, une phrase dit que le remplacement n'a pas été accepté, et la série peut être validée

#### Scenario: Substitution hors ligne
- **WHEN** la demande est faite sans réseau
- **THEN** l'écran dit qu'elle part au retour du réseau, et rien n'est présenté comme déjà remplacé

### Requirement: Valeurs du bilan
Chaque valeur du bilan MUST venir d'une source déclarée (la séance, l'historique serveur, une préférence déclarée) ;
une valeur sans source MUST être omise, jamais remplacée par une valeur par défaut présentée comme celle de l'utilisateur.

#### Scenario: Fréquence non déclarée
- **WHEN** l'utilisateur n'a déclaré aucune fréquence hebdomadaire
- **THEN** le bilan n'affiche pas de fréquence

### Requirement: Textes de reprise
Les textes de reprise MUST accorder les nombres (« 1 série faite », « 2 séries faites ») et MUST dire, pour la reprise
serveur comme pour la reprise locale, ce qui se passe hors ligne.

#### Scenario: Une seule série
- **WHEN** une seule série a été faite avant la pause
- **THEN** la reprise affiche « 1 série faite »

### Requirement: Contexte factuel optionnel du bilan (D-MOB02-3)
Le bilan MAY afficher une seule ligne factuelle sous le bloc conservé, sans carte ni compteur empilé.
Elle MUST utiliser uniquement les données serveur complètes et expliciter la période.
Elle MUST NOT confondre fréquence déclarée et activité observée, ajouter une séance locale non attestée,
inventer un défaut, une comparaison ou un jugement. Les détails restent réservés à MOB-05.

#### Scenario: Historique complet attestant la séance courante
- **WHEN** le GET authentifié renvoie un historique complet, des identifiants uniques, des dates valides et la séance courante terminée
- **THEN** une ligne facultative compte les séances terminées de la semaine UTC jusqu’à cette fin attestée et indique les bornes
- **AND** la préférence de fréquence ne modifie jamais ce nombre observé

#### Scenario: Données manquantes ou incomplètes
- **WHEN** la lecture échoue, la page est tronquée, la séance courante manque ou les données sont invalides
- **THEN** cette ligne est omise et aucune activité par défaut n’est affichée
