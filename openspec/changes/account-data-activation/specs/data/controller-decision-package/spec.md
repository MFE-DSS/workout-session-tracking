## ADDED Requirements

### Requirement: Single explicit controller decision package
Le paquet DATA-ACT-01 SHALL conserver un relevé unique de l'identité/entité et
juridiction du responsable, finalités/fondements/consentements, sort des données
et exceptions, faits locaux non envoyés/non attribués, exports/social, sauvegardes
et restauration, demandes/reçus et URLs publiques privacy/demande web. Chaque
décision SHALL porter réponse, auteur habilité, date et référence avant admission.

#### Scenario: A controller answer is missing
- WHEN une identité, finalité, durée, exception, URL ou décision requise manque
- THEN la ligne reste OPEN, sans valeur déduite du code, d'un défaut ou d'un domaine existant.

### Requirement: Actual copy graph and existing foundations
L'audit SHALL distinguer le snapshot historique des 23 tables des sept tables
PLAN, six propriétaires immuables et une autorité globale, et SHALL inclure copies
locales V3, export, sauvegarde, restauration et workflow de reçu séparé. Il SHALL
nommer les fondations déjà présentes et les seuls manques observés sans affirmer
que le schéma déclaré est déployé ou qu'un export de séance est un export compte complet.

#### Scenario: Existing isolated request and capability service
- WHEN le service isolé de demandes et capacités existe sans politique admise ni exécuteur
- THEN l'audit le réemploie et identifie son intégration manquante, sans proposer un second service ni déclarer DELETED réel.

### Requirement: Preparation does not authorize operation
DATA-ACT-01 SHALL rester documentaire. Une preuve de test ou TIME_ACK SHALL NOT
devenir un consentement DATA ; BodyConsent SHALL NOT autoriser une autre finalité
implicitement. Les critères DATA01–07 SHALL rester ouverts jusqu'à leurs preuves
propres. Admission de politique, exception destructive, GO BUILD et déploiement
SHALL rester explicites et distincts.

#### Scenario: Controlled PLAN tests pass
- WHEN une livraison PLAN ou SCI contrôlée est verte sans décisions DATA applicables
- THEN aucune collecte réelle, migration réelle, suppression ou activation DATA n'en est déduite.
