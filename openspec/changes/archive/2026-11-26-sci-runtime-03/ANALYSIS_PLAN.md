# SCI-RUNTIME-03 — plan d'expériences autorisées

Parent vérifié :3d4c7577e5ffd39fb59de58d1aab3bded1936edb,26 novembre2026 Europe/Paris.
Mandat OPERATOR_REQUEST.txt, SCI-RUNTIME-03 phases1–6. Analyse/essais synthétiques autorisés ; code produit, CI et budgets non autorisés à modifier. Lecteur disabled/NOT_QUALIFIED.

## Brainstorming / Options / Risques / Choix retenu
- Témoins worker inchangé + sondes légères par frontières : retenu. Mesurer CPUuser/system et monotone, appels imbriqués avec temps exclusif, parsing/digests comptés. Préserver les octets et profils sources ; tout bytecode instrumenté sera explicitement diagnostic.
- Profilage global cProfile/trace : uniquement comparaison d'overhead si utile, jamais assimiler son SIGXCPU à celui d'un nominal sans sondes.
- Hausse CPU ou cache global : rejetés à ce stade. Tout correctif aura son amendement propre, avec source/owner/invalidation/ressources/parité.

## Plan exécutable
1. Inventorier runtime/image/source, préserver témoin SCI02 et checkout opérateur. Monter source Git readonly dans volumes jetables dédiés. Aucun service existant modifié.
2. Répéter nominal intact, imports seuls, puis instrumentation par frontières. Source entière attestée ; ne journaliser ni payload ni credentials. Comparer sorties en excluant seulement les identifiants/instants générés explicitement identifiés ; aucun inconnu promu.
3. Mesurer catalogue/digests, V2/V3 data-only, captation/provenance/P07/DTO et IPC séparément. Mesures détaillées SQL séparées si elles perturbent le nominal. Conserver échecs et limites de mesure.
4. Jeux nominaux, grands valides et adversariaux, snapshots/owner/read-only/concurrence/kill/reap ; limites actuelles. Aucune exécution de code historique non attesté.
5. Cible native et chemins : qualifier uniquement un environnement jetable effectivement autorisé et accessible. DockerDesktop ARM64/amd64 émulé reste distinct. Ancien alias SSH refusé au banner ; VPS connu vérifié séparément. GO du banc natif enregistré dans AUTHORIZATION.json, sans modification de QA.
6. Synthèse bornée ; si code/CI/ressource nécessaire, un amendement précis avant apply. Ne clôturer ni qualifier depuis le seul kill correct d'un enfant.
