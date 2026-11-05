# MOB-03 — lecture canonique de poids v1

5 novembre 2026. Delta GET accepté : « Valider le GET de poids proposé ». PR #353 ; aucun écran ni writer nouveau.

`GET /api/mobile/v1/me/body/weight-history?limit=50&cursor=…` réutilise body_profile.list_weight_measurements / weight_history_page et la table BodyMeasurement. Limite 1–100, filtre propriétaire résolu par Bearer, ordre décroissant (measured_at,id), clé de continuation base64url de date UTC + identifiant. Un curseur ne choisit jamais le propriétaire. Cookie web seul refusé. Flag BODY_ASSESSMENT_ENABLED conservé (OFF →404), consentement actif requis (sinon403), erreurs de query/cursor privées 422/400 ; toutes les réponses du GET pris en charge portent no-store.

Sortie weight-history/1.0.0 : owner_id, unit=kg, legacy_profile_included=false, timezone_basis=DATABASE_UTC_CONVENTION, state AVAILABLE/EMPTY, entries et next_cursor opaque/null. Chaque entrée garde measurement_id, measured_at, recorded_at distinct, value, quality, raw_value_repr et provenance. Les datetimes naïfs SQLite suivent la convention UTC existante ; aucune acquisition timezone originale non stockée n'est inventée.

Provenance historique origin/acquisition UNKNOWN et source_ref body_measurements/ID/weight_kg. Une ligne partielle sans poids ne produit pas de point. Un poids User sans date n'est jamais lu comme point de chronologie. Une valeur atypique finie reste inchangée et marquée LEGACY_OUTSIDE_CURRENT_BOUNDS, selon les bornes existantes du service ; non finie : value=null + représentation textuelle étiquetée INVALID_NONFINITE, sans mutation de la source. Cette projection ne crée pas un diagnostic.

WeightHistoryClient passe par le vrai AuthSession, vérifie owner/version/unité/dates/provenance et annule les réponses après changement de compte. Le GET a été vérifié avec API réelle et avec un client HTTP réel sur backend jetable synthétique : pagination, no-store, changement de propriétaire et création réelle de compte → consent_required, sans consentement créé par lecture. Aucun déploiement ou état appareil déduit de ce smoke.

Consentement/retrait natifs, saisie corporelle/impérial et surface de consultation restent hors de ce delta. La lecture respecte le service de consentement existant sans réinterpréter son retrait comme un effacement. Revue indépendante de cette frontière : aucun Critical/Important ; deux mineurs connus (curseur à extrême du calendrier →503 privé ; validation calendaire client permissive si un serveur futur sérialisait un jour impossible), conservés dans le rapport.
