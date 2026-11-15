> GO BODY-01/amendement/G1 reçu le 11 novembre 2026 : « Autoriser BODY-01, son amendement et G1 » (call_106057b169a74bc9887b1fea9f527f5d). Apply contrôlé en cours ; pixels non acceptés, aucune activation/release. Les statuts pré-GO ci-dessous gardent leur instant de préparation.

# BODY-01 — delta normatif explicite proposé

11 novembre 2026. **DIRECTION_OPÉRATEUR_ACQUISE / AMENDEMENT_PROPOSÉ / NO_GO_BUILD.** Le mandat MVP demande conservation des originaux et corrections avec provenance. Ancienne option A abandonnée. Le design matérialise cette direction ; aucun contrat canonique édité ici.

## Before au canonique 3cf77e1

| Source | Contrat / comportement |
|---|---|
| Sx_MORPHO_CAPTURE_01_SPEC §2.1,40–56 | Canonique create_measurement, correction par ajout prospectif sans migration des anciennes lignes |
| SPIGNOS_BODY_MANUAL_PROFILE_BUILD_SPEC,62–69/95–98 | Routes propriétaires edit/delete, hard-delete sans lignée |
| SPIGNOS_BODY_PRIVACY_AND_CONSENT_SPEC §3 | Effacement réel individuel/tout profil, dérivés invalidés, distinct de collecte |
| body_profile.py ; body.py ; auth_routes.py profile_measurements_submit | Création INSERT, update en place, DELETE une ligne, lecteurs bruts |
| CLAUDE.md §4/§6 | Pas d'amendement silencieux ni apply sur contradiction non résolue |

## After proposé pour approbation avec le GO BODY

Amender les trois contrats de façon cohérente, avec référence à la décision :

> Nouvelle observation manuelle = INSERT BodyMeasurement ; jour sans upsert. Une correction volontaire d'un relevé ajoute une version dans la même table, liée à la tête sous garde propriétaire/concurrence. Original conservé, provenance héritée inchangée, champs corrigés tracés. Correction distincte d'une observation indépendante. Les lecteurs courants utilisent la tête non effacée ; versions remplacées réservées à l'audit/export, jamais repli d'un champ vidé. Aucune ancienne ligne backfillée, fusionnée, requalifiée ou supprimée par migration.
>
> Suppression volontaire distincte : effacement confirmé du relevé supprime réellement ses nombres et toutes ses versions possédées ; reçu minimal/références réservées restent des copies personnelles DATA. BODY-01 livre cet effacement individuel contrôlé. Suppression tout profil, fermeture/export globaux et politique des copies/backups/local restent gates d'activation ouvertes, sans conformité générale prétendue.

Clarifier aussi la lecture mobile : poids v1 forme/profil limité conservés, versions remplacées exclues ; nouveau DTO BODY complet consommé par Progrès. Aucun changement SCI ou signification de ses résultats.

## Vote et preuve

Un seul vote explicite peut approuver cet amendement nommé, design/scope/G1. Pas de GO normatif puis technique routiniers. Avant décision APPLY_CLOSED. Après : enregistrer auteur/date/référence et amender les sources canoniques dans la même PR avant de revendiquer la réconciliation. La direction opérateur n'est pas redemandée ; forme et coûts sont présentés pour le nouveau GO.

Ce vote ne fournit ni traitement réel, purge globale, nouvelle autorité SCI, provider, activation, hébergement, APK/OTA ou déploiement. Effacement individuel de test expressément inclus, jamais caché dans une migration. Source pinée ou consommateur hors leases incompatible =>revue du delta concerné, pas nouveaux hashes silencieux.
