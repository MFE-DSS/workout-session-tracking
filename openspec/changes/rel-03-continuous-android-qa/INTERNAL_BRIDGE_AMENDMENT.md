# OPS-02 — raccordement hôte vers bridge interne

18 novembre 2026. Base `b8fc63ffadba35028af9e1c92c2e48892f9fe403`.

## Mandat et décision opérateur

Le paquet concret `resume-20261118/NETWORK_AMENDMENT_DECISION.md` a été soumis
après refus réel de la publication Docker 8088. Réponse suivante de l'opérateur :
« ok donc continue sur ton critical path sinon fait le CR final du travail
attendu de maprompt injection ». Cette direction est retenue comme autorisation
de l'amendement borné présenté ; aucun GO APK/OTA/traitement personnel déduit.
Les GO techniques, OPS et GOV-MERGE-01 antérieurs restent acquis.

## Brainstorming / Options / Risques / Choix retenu

Le bridge interne bloque les sorties/hôte et répond depuis l'hôte à l'IP du
conteneur, mais Docker ne matérialise pas le port publié demandé. Désactiver
Internal ouvrirait un autre modèle de sécurité ; ajouter un proxy créerait un
service et une preuve supplémentaires. Choix : conserver Internal, ICC=false,
le filtre et un seul conteneur ; nginx QA cible l'IP privée réellement acquise.
Coût : remplacement/changement d'IP exige nouveau pin et génération de routage.
Une IP n'est jamais une constante produit ni une preuve auto-déclarée par l'app.

## Contrat et fichiers possédés

La politique privée fermée ajoute `container_ip`, IPv4 canonique RFC1918, et
exige `ports=[]`. Requête et observation SSH passent à 2.0.0 ; le format 1.0.0
est refusé. Le collecteur lie cette IP aux deux projections Docker acquises du
même conteneur/réseau et au sous-réseau ; aucune publication, PublishAllPorts,
seconde interface, autre upstream ou preuve nginx périmée n'est admise.
API/app/SCI/schéma/base/SDK et identité du binaire restent inchangés.

Sources : `deploy/qa/observe_ovh.py`,
`tools/qa_delivery/ovh_observation.py` et tests consommateurs QA. Documents :
runbook OVH, paquet/commandes OPS-02 et contrat de preuve du change existant.
Le healthcheck garde son comportement ; une construction d'argv utilise
`shlex.join` pour préserver le code Python, au lieu de retirer ses guillemets.

## Plan d'exécution et critères de sortie

1. Témoins RED : nouvelle politique et vhost sourcé, réseau/point d'accès acquis,
   mauvaise IP/ancien reçu/publication/second réseau ; règles de refus existantes.
2. Implémenter ensemble client et collecteur ; broad QA suivant check_scope,
   Ruff/budget/protocole/OpenSpec/sécurité et revue indépendante entière.
3. PR, CI HEAD exact, merge gardé et CI canonique sous GOV-MERGE-01.
4. Installer uniquement l'outillage hôte qualifié. Recréer QA seul si nécessaire,
   volumes/DB/clefs/ancre conservés. Corriger l'argv healthcheck et vérifier
   maintenance, reprise et health réel. Pas de nouvelle initialisation.
5. Activer après backup/restauration déjà acquis, puis collecteur forcé,
   DNS/TLS/nginx chargé et smokes HTTP. Contrôler services personnels et rollback.
6. Seulement après QA qualifié : paquet candidat Android distinct. Aucun build
   implicite ni clôture anticipée d'acceptation appareil ou DATA.

## Preuves initiales et état

Image b8fc acquise/run44188461111 ; ID de configuration et rootfs concordants.
Base réelle46tables/program_builder_operations_01, deux comptes synthétiques,
106exercices canoniques, zéro fait fabriqué. Trois exports chiffrés restaurés,
digests/ancre identiques. QA arrêté sans marqueur ; services personnels préservés.
Preuves privées persistantes :
`/Users/martinfeldmann/auren-review/rel03-ops02-20261116/resume-20261118/`.
Le paquet contient secrets et données synthétiques : ne pas publier son contenu.

Ledger : préparation autorisée, implémentation et contrôles à acquérir.

## Revue et corrections

Revue indépendante entière : trois Important retenus et corrigés dans une passe :
reçu de routage lié au container_id même si IP réutilisée ; schéma fermé et sortie
allowlistés côté collecteur avant émission ; commandes de reprise distinguant
backend b8fc, collecteur canonique2.0.0 et futur candidat natif/client2.0.0, sans
réinitialiser les ressources existantes. Deux témoins comportementaux ont échoué
DID NOT RAISE avant correctif, puis40tests ciblés passent. Le correctif documentaire
est vérifié par lecture des instructions finales. Aucun second avis indépendant
des correctifs finaux prétendu. Mineur différé : témoins isolés supplémentaires
des trois contrôles de publication Docker ; le contrôle réel reste imposé.

Validation finale locale : check_scope ISOLATED ; broad QA423PASS sousPython3.11.14
(1dépréciation Starlette/httpx connue), ciblés40PASS, Ruff modifiés PASS, budget259≤548,
protocole PASS, OpenSpec strict28/28, Gitleaks diff0. Aucun full sweep local requis.
Bandit outils conserve B108Medium sur la comparaison tmpfs /tmp préexistante,
4Low/0High ; aucun seuil/suppression ajouté et aucune innocuité globale déduite.
La CI PR/canonique et la qualification distante du nouveau raccordement restent
à acquérir ; aucun état final vert anticipé.
