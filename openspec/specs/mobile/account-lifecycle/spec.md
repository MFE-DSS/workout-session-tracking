# mobile/account-lifecycle Specification

## Purpose
Définit le cycle du compte mobile et les garanties visibles de sécurité et de continuité, depuis l’inscription jusqu’à la révocation ou la suppression autorisée, sans confondre état local et résultat serveur.

## Requirements

### Requirement: Delivered foundation and explicit deferred acceptance
Under approved GOV-MOB03-SPLIT-01 the foundation MUST keep absent producers fail-closed and distinguish its delivery from complete MOB03. It MUST NOT claim deferred body acquisition, deletion execution, scientific session integration or physical release acceptance.

#### Scenario: Foundation archived independently
- **WHEN** the authorized account foundation passes its final tests, reviews and canonical merge checks
- **THEN** its archive does not close DATA01–07, PLAN01–07 or RELEASE01–06, retained in docs/strategy/MOB03_DELIVERY_SPLIT_AUTHORIZATION.md and its reserved proposals; policies, science, physical release and deployment gates remain open.

### Requirement: Inscription conforme au contrat canonique
Le mobile MUST créer un compte au moyen d’une API JSON validant les règles canoniques de nom, mot de passe et email, sans affaiblir les protections d’authentification existantes. Une réponse perdue MUST NOT être présentée comme une création confirmée.

#### Scenario: Déclaration valide
- **WHEN** l’utilisateur soumet des identifiants valides
- **THEN** le résultat serveur détermine la suite du parcours et aucun cookie web n’est pris pour un jeton mobile

#### Scenario: Double appui ou réponse perdue
- **WHEN** une inscription attend sa réponse ou que le réseau coupe
- **THEN** l’état d’attente et le résultat incertain restent explicites et aucune création supplémentaire n’est déclenchée par un double appui

#### Scenario: Identifiant indisponible ou entrée invalide
- **WHEN** le serveur refuse les données selon sa politique canonique
- **THEN** le parcours reste corrigeable et aucun compte ni jeton valide n’est prétendu créé

### Requirement: Authentification et isolation du propriétaire
Les lectures et écritures du compte MUST utiliser l’identité authentifiée côté serveur. Un changement de compte MUST NOT exposer ni envoyer les données ou commandes locales d’un autre propriétaire.

#### Scenario: Identité forgée
- **WHEN** une requête fournit l’identifiant d’un autre utilisateur
- **THEN** elle ne lit, modifie ou supprime aucune donnée de cet utilisateur

#### Scenario: Changement de compte avec journal local
- **WHEN** une personne se déconnecte puis une autre se connecte
- **THEN** les commandes de la première ne sont ni affichées comme celles de la seconde ni envoyées sous ses credentials

### Requirement: Cycle des jetons et changement de mot de passe
Le mobile MUST conserver la restauration et la révocation canoniques des sessions. Un changement de mot de passe MUST appliquer la politique de révocation approuvée, sans stocker de secret en clair dans les journaux ou exports.

#### Scenario: Jeton révoqué
- **WHEN** un credential n’est plus valide
- **THEN** le client demande une authentification et conserve les faits locaux selon leur propriétaire sans les attribuer à un nouveau compte

#### Scenario: Réinitialisation du mot de passe
- **WHEN** l’utilisateur demande le parcours oublié ou réinitialisation existant
- **THEN** le parcours web conservé par MOB-00 reste utilisable et n’est pas remplacé par une sémantique native non approuvée

### Requirement: Suppression de compte explicitement autorisée
La suppression MUST dépendre d’une politique d’effacement/rétention approuvée, d’une authentification du propriétaire et d’une confirmation explicite. Une demande en attente MUST NOT être présentée comme un effacement réalisé. Cette préparation MUST NOT exécuter de suppression.

#### Scenario: Politique non arbitrée
- **WHEN** l’inventaire de données, les garanties de réauthentification ou la rétention ne sont pas validés
- **THEN** l’implémentation destructive reste bloquée et aucune suppression simulée ou silencieusement partielle n’est livrée

#### Scenario: Demande confirmée et autorisée
- **WHEN** le propriétaire confirme la suppression selon la politique approuvée
- **THEN** le résultat fait état de l’effacement réel et de toute conservation explicitement prévue, avec révocation des accès selon ce contrat

#### Scenario: Coupure avant réponse d’effacement
- **WHEN** la réponse serveur n’est pas connue
- **THEN** le client indique que le résultat doit être vérifié et ne rejoue pas une opération destructive sans le protocole approuvé

### Requirement: Information de confidentialité accessible
Le socle MUST conserver les moyens existants d’accès/export et exposer les destinations de confidentialité lorsqu’une URL réelle est configurée, sans lien fictif ni consentement implicite à des traitements corporels, photos ou fournisseurs externes. La publication du responsable, des URL et des textes définitifs reste DATA01/RELEASE06, explicitement ouverte après GOV-MOB03-SPLIT-01.

#### Scenario: Entrée dans le compte
- **WHEN** l’utilisateur consulte les informations du compte et une destination réelle est configurée
- **THEN** il peut y accéder et conserver les parcours d’export existants sans activer de consentement corporel ; sinon aucun lien fictif ou conformité Store n’est prétendu fourni

### Requirement: Fondations non destructives de demande d'effacement
Sans politique/producteur approuvés, le système MUST NOT servir d'effacement ou prétendre accepter une demande durable côté serveur. Le consommateur MUST conserver une intention propriétaire idempotente, distinguer demande et résultat, et ne jamais nettoyer sur timeout/401/404. Un résultat structuré seul MUST NOT autoriser le nettoyage ; la retraite locale confirmée MUST précéder un nettoyage ciblé.

#### Scenario: Reprise après réponse perdue
- **WHEN** une intention envoyée n'a pas de résultat autoritaire
- **THEN** sa clé persiste et seule la relecture est permise, sans mutation rejouée après relance

#### Scenario: Refus terminal corrigé
- **WHEN** le propriétaire demande explicitement une nouvelle intention après relecture autoritaire du refus terminal
- **THEN** elle est atomiquement liée à la précédente ; les intentions inconnues/en attente ne sont pas rouvertes

#### Scenario: Données anciennes après confirmation
- **WHEN** un nettoyage ciblé est autorisé par le vrai producteur
- **THEN** la marque de retrait persistante et la génération empêchent réouverture et réponses tardives, sans purge globale ni attribution d'un journal incertain

### Requirement: Durable authoritative deletion outcomes do not regress

The request consumer MUST treat unverified terminal refusal as unknown and MUST NOT regress a verified confirmed/rejected terminal request to an older pending/unknown poll. Owner retirement MUST survive metadata restart and deny the removed owner journal while preserving other owners. Server execution remains blocked pending retention policy.

#### Scenario: Older pending poll after confirmed completion
- **WHEN** another consumer has persisted the verified terminal result for the same request
- **THEN** an older response cannot overwrite that terminal state or authorize another account cleanup.

### Requirement: Isolated policy-gated request service
The foundation MUST provide transactional request lifecycle code without registering or creating its proposed workflow table at application startup. No route, worker, irreversible revocation or deletion MUST be activated without the approved controller policy, future migration and adapters. Admission and confirmation authority MUST come from trusted server composition, never request JSON.

#### Scenario: Controller policy absent
- **WHEN** the default service receives an attempted request
- **THEN** no request is accepted or stored, no token is revoked and no deletion is performed.

#### Scenario: Scoped status after irreversible transition
- **WHEN** a future admitted executor has started irreversible processing
- **THEN** active-account identity alone cannot recover that request; only its previously issued, unexpired, scoped capability can read its status, without granting other access.
