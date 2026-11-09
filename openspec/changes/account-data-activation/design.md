# Design — DATA-ACT-01 documentaire

## Context

Base fe9f6e9. Faits : matrice MOB03 de 23 tables, service de demandes et capacité
isolés, consentement Body, sept tables PLAN dont six possédées immuables, copies
SQLite et export typé. Le schéma déployé n'a pas été interrogé.

## Decisions

Un seul questionnaire dans docs/data/data-act-01/CONTROLLER_DECISIONS.md ; les
autres documents ne dupliquent pas les réponses. Garder l'ancien inventaire
daté intact et lui joindre le graphe PLAN. Conserver la proposition réservée
DATA01–07 et limiter le delta normatif au paquet de décisions.
La matrice distingue faits statiques, proposition d'ingénierie et admission
humaine ; les valeurs OPEN sont des blocages, pas des réglages par défaut.

## Risks

Conserver des copies immuables n'est pas une justification juridique. Réutiliser
BodyConsent pour tout PLAN, appeler TIME_ACK consentement, adopter 30 jours ou
un domaine existant par commodité créerait une décision fictive. La préparation
évite ces déductions ; les décisions applicables et une revue sourcée restent à
fournir par le responsable. Aucune qualification juridique actuelle affirmée.

## Scope and migration

Docs/OpenSpec seulement ; aucun apply/runtime/migration. Aucune divergence iOS /
Android introduite. Futures routes mobile Bearer et web session-CSRF réemploieront
le même service selon les contrats existants ; ce dossier ne les expose pas.
