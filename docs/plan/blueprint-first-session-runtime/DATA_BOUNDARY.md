# PLAN V3 — graphe additif et frontière DATA

8 novembre2026. Six tables propriétaires, une autorité opérationnelle globale,
une table locale. Ceci est un inventaire d'implémentation, sans fondement,
durée de rétention ou consentement de production inventés.

| Source | Copie / lien | Finalité à admettre avant données réelles |
|---|---|---|
| users | blueprint_source_events | déclarations, contexte, observation, préparation, choix et invalidation minimale |
| source events | owned_blueprint_snapshots | capture propriétaire cohérente, faits/provenance/épisodes/pins/assessment |
| snapshot | first_plan_evaluations | requête/résultat SCI et accord TIME_ACK enfant immuables |
| evaluation + owner | first_session_requests | commande, digest, refus/annulation/réconciliation, unique CREATED |
| evaluation + workout_session | first_plan_execution_bindings | prescription/intention/exercice/contexte/version et mapping des séries |
| owner + session + exercise + set | first_plan_set_observations | journal d'opérations typées, CAS, preuve du rejeu et corrections |
| publication test contrôlée | first_plan_runtime_authorities | génération/état/pins du packaging ; pas un second registre scientifique |
| partition native possédée | journal_v3_set_operations + outbox/active_session existants | faits non envoyés/acquittés/refusés/résolus, reprise et historique d'opérations |

Les FK propriétaires sont NO ACTION et composites aux frontières séance/série ;
pas de cascade aveugle ou réattribution. SetLog reste le journal canonique des
répétitions/complétion/date. La sidecar porte le sens du réglage et les versions ;
PER_IMPLEMENT/MACHINE_DISPLAY_KG ne deviennent pas une masse totale.

Aucun traitement corporel global n'est déduit de l'absence de BodyMeasurement.
Les limitations et observations ont leurs propres finalités. Dans le périmètre
synthétique autorisé, consent_assessment reste UNAVAILABLE et la preuve de GO
de test ne devient pas un consentement personnel. APP_ENV réel/default-off
n'acquiert pas ces nouvelles copies.

Le responsable doit intégrer ce graphe, exports JSON, appareils/outbox, copies
et sauvegardes aux décisions D-POL01–05. Aucun DELETE users, purge, worker
d'effacement ou révocation irréversible n'est ajouté. Le retrait scientifique
bloque les nouvelles consignes et préserve les faits autorisés ; le retrait
DATA doit suivre sa politique propre. Une rupture de continuité ne redonne
pas de validité aux anciens faits par une génération ou un GET récent.

Les dérivés legacy ne doivent pas interpréter les masses NULL ou le profil
sans template : score, confiance, implicit labels, records et continuité sont
non évaluables/omis. Les faits et statuts restent visibles ; ceci ne pose pas
excluded_from_stats=True et ne supprime pas la séance. JSON typé conserve les
sources ; CSV/restauration legacy refusent un profil qu'ils ne savent préserver.
