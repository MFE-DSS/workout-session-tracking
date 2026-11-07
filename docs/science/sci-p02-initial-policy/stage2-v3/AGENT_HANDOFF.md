# SCI stage2 — handoff PLAN du producteur V3 isolé

7 novembre2026. Cette passe porte uniquement sur le cas limité approuvé, pas sur une API, SDK, acquisition, séance ou activation. Les versions sont first-plan-request/recommendation3.0.0, engine initial-policy-producer/3.0.0, policy initial-hypertrophy-policy/1.0.0-limited, binding initial-plan-v3-binding/1.0.0. L'admission et les pins effectifs se lisent dans authority/registry.v1.json et producer-artifact-manifest.v1.json, jamais dans un label client.

## Appels réutilisables

`load_v3_registry()` vérifie publication et sources réelles ; `produce_v3(request, registry)` compose et qualifie ; `validate_admitted_exchange_v3(request, response, registry)` vérifie indépendamment sélection/dose/qualification/quinze zones/temps/ack, puis rejoue strictement le producteur. L'ancien validate_exchange V3 reste historiquement négatif ; ne pas le remplacer ni modifier ses anciennes références pour admettre cette publication. Le SDK FirstPlanClient V1 reste V1 et refuse V3 sans négociation PLAN explicite.

## Applicabilité et facts

Objectif hypertrophie, population adulte déclarée non clinique, cadence exactement2, deux budgets explicites et limitations connues vides. Sept contextes bilatéraux exacts du binding : contexte/dispositif/réalisation/sémantique du réglage sourcés, familiarisation avant essai, essai comparable observé8–12répétitions sans préoccupation/échec, qualité/gêne connues acceptables, acceptation explicite courante. Le réglage est provisoire à réessayer ; ni optimum ni vrai2RIR mesuré. Aucun bootstrap positif ou charge universelle, transfert entre appareils, progression ou reprise après préoccupation admis.

Poids, taille, expérience et priorités facultatives ; priorité ≠ faiblesse analysée. Inventaire global UNKNOWN conservé si les sept contextes consommés sont connus ; pas de salle complète supposée. Exclusion/indisponibilité/contexte ambigu ou absent bloque sans substitution hors binding. Quinze zones sont quinze états de connaissance, avec rôles qualitatifs et slots unresolved ; aucune quantité de croissance ni crédit numérique.

## Identité, temps, permission

PLAN doit construire le snapshot serveur propriétaire, révision/as_of et provenances depuis des acquisitions réelles ; owner_id n'est jamais choisi par le body. Le moteur pur ne peut authentifier ni prouver un consentement, une révocation réseau ou une déclaration humaine. Métadonnées et empreintes seules ne font pas autorité.

Conserver séparément request_fingerprint (faits), observation_fingerprint (faits/observations), full_evaluation_fingerprint (avec ack), plan_time_fingerprint et identité persistée de séance. Plan+temps ne changent pas par le seul ajout d'ack ; la décision complète change. generated_at=max(as_of,acktime), déterministe sans horloge cachée. Relever les digests dans le manifeste, pas les recopier depuis une ancienne préparation.

Le profil admis ne donne aucune borne supérieure temporelle : BUDGET_UNCERTAIN/Duration UNKNOWN. Structure TRADITIONAL_SEQUENTIAL ;750s de repos sont l'addition120×4+90×3 entre les deux séries de chaque slot. Aucun repos inter-exercice, travail, installation ou préparation inconnu converti en zéro. Borne consommant le budget => refus ; sinon aucun fit garanti. C6 est EXPLORATION_POLICY_ADMITTED, pas preuve SUPPORTED ni réussite des anciennes gates v1/v2.

SCIENTIFICALLY_READY sans ack => REQUIRES_TIME_ACK. Ack explicite lié au sujet/snapshot/révision/faits/observations/plan+temps/politique => ELIGIBLE scientifique. Cela n'est pas une commande serveur de début. PLAN vérifie l'identité, l'applicabilité et l'autorité courantes, la règle produit et le consentement pertinent, puis crée idempotemment une séance possédée. Aucune auto-acceptation d'ack depuis navigation ou simple série journalisée.

## Erreurs, retrait et reprise

Manques utiles => INSUFFICIENT_DATA ; conflits consommés => CONFLICTING_DATA ; hors population/cadence/limitations ou borne de repos incompatible => CONSTRAINT_UNSATISFIABLE ; qualification/contexte absent => REVIEW_REQUIRED. Pas de producteur dans un runtime => NOT_SERVED transport, jamais MISSION scientifique de repli. Versions/pins/binding/owner incompatibles et ack périmé sont refusés, pas réparés par resérialisation. Aucun ordre non déterministe ou retry de mutation n'est introduit.

Retrait ou changement d'une référence requiert une nouvelle évaluation, aucune réactivation automatique après préoccupation. Le registre isolé est une publication figée ; PLAN doit obtenir un état courant de retrait/admission depuis son autorité serveur avant nouvelle consigne. Reprise de lecture/journal factuel distincte de permission pour nouveau travail. Le producteur ne purge aucune séance ni ancienne observation.

## Fixtures et dépendances

Les quatre exports sont générés par le vrai producteur et son vrai registre depuis SYNTHETIC_INPUT.json : positif sans ack, positif avec ack, fait requis absent et dispositif indisponible. **REAL_PRODUCER_SYNTHETIC_INPUT_NOT_SERVED** : aucune donnée de personne réelle, aucune autorité de test positive ni import produit. Les40kg observés/75min déclarées et dates des exemples ne sont pas des prescriptions ou seuils par défaut.

PLAN reste proposé sans GO BUILD : snapshot/acquisitions, négociation et adaptateur, réglage typé/journal canonique, commande concurrente/idempotente, réponse perdue/reprise, lecture native, contraintes des dérivés historiques, visuel et appareils. DATA doit encadrer les nouvelles copies/observations/consentements ; RELEASE nécessite cible, compatibilité/rollback, GO déploiement distinct et recettes. MISSION LOCKED ; socle #353 accepté conservé ; MOB03 complet reste ouvert.
