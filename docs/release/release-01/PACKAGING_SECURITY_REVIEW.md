# RELEASE-01 — contexte des alertes packaging B404 / B603

9 novembre 2026. Source relue : fe9f6e9, `app/services/plan_v3/packaging.py`,
workers historiques/v2 et builder. **Analyse de frontière ciblée ; pas audit
global, pentest ou qualification juridique de sécurité.** Les issues Sonar
restent inchangées sous GOV-SONAR-01. Ce document ne les ferme pas.

## Appel effectif et données contrôlées

`execute_science` obtient le chemin du bundle de la configuration serveur.
Son argument `expected_digest` est **optionnel** : les appels d'autorisation et
d'évaluation pinés le reçoivent de l'autorité opérationnelle en base, mais
certains validateurs de contexte/blueprint, validations des faits du journal et captures
utilisent le manifeste configuré sans ce pin DB. Il serait faux de présenter
tous les sous-processus comme liés au digest de l'autorité en base. Les routes
publiques de rencontre ne prennent pas un chemin worker, une commande shell
ou un manifeste d'autorité arbitraire comme instruction d'exécution.
Le manifeste doit avoir le format connu et chaque source hashée doit se
résoudre dans le bundle. L'inventaire est borné à absent ou inventaire2 ; il
sélectionne seulement `science_worker.py` ou `science_worker_v2.py`, qui doit
être inclus dans la fermeture attestée.

L'argv est `[sys.executable, '-I', worker_fixe, chemin_bundle, digest_calculé]`.
Ce digest calculé a été comparé au pin attendu seulement quand celui-ci est
fourni ; le passage de l'argument ne prouve donc pas à lui seul une autorité DB.
`subprocess.run` ne reçoit pas shell=True, ne concatène pas les déclarations
utilisateur en commande et transmet opération/valeurs sous JSON stdin
(`allow_nan=False`). Le subprocess a un cwd privé, timeout20, stdout/stderr
capturés et returncode contrôlé. Les erreurs exposées par la frontière ne
recopient ni observations, ni stderr, ni chemins privés. Les validateurs SCI
réels vérifient les entrées et le résultat ; une forme JSON seule ne suffit pas.

Le worker v2 vérifie les imports réels `tools.*` avant/après l'opération, y
compris ceux chargés tardivement. Cette vérification intervient après leur
chargement : ce n'est ni une prévention de toute exécution ni un confinement
général. V2 ajoute le scan de fermeture/caches/liens symboliques et le contrôle
final ; ne pas attribuer ces propriétés indistinctement au worker historique.
Il désactive l'écriture de pyc. Le packaging historique est conservé ; aucun
contenu synthétique d'artefact n'est appelé comme factory de résultat.

## Exploitabilité examinée

| Entrée / menace | Garde existante et constat | Limite conservée |
|---|---|---|
| Chaîne de shell dans les faits | Faits JSON sur stdin, argv fixe, aucun shell | Cela ne prouve pas l'absence de bug dans chaque parseur/consommateur scientifique |
| Choisir un exécutable ou worker depuis le body | Interpréteur du processus, deux noms fixes selon inventaire et sources attestées | Configuration, code appelant et autorité en base sont des entrées administratives de confiance |
| Source absente, modifiée ou hors root | Hash/source closure, chemin résolu interne et import attesté ; digest DB seulement sur les appels qui le transmettent | Sans expected_digest, manifeste auto-déclaré de configuration ; un hash seul ne prouve ni auteur ni autorisation. Couverture des pins à revoir sur les revalidations/captures/journal avant exposition |
| Écriture locale concurrente après vérification | Le nouveau banc a parent0700 et fichiers0444 ; aucune mutation du bundle après publication | Ce n'est pas une immutabilité OS : même uid/administrateur peut rechmod/écrire. La fenêtre check→exec et les permissions du parent/interpréteur/dépendances restent un risque d'hôte à traiter avant exposition |
| Injection par PYTHONPATH / cwd | Interpréteur `-I`, chemins/imports attestés | L'environnement OS est hérité, et les dépendances/interpréteur installés restent de confiance ; `-I` n'est pas une sandbox ou restriction réseau/filesystem |
| Worker bloquant ou sortie excessive | Timeout20 et validation des échanges | Le timeout ne couvre pas le hash et la sérialisation avant subprocess ; capture_output n'est pas un plafond de mémoire ; quota d'entrée/sortie/concurrence et supervision à vérifier sur la vraie cible |
| Fuite par exception du worker | Erreur neutre, stderr privé non exposé | Les autres logs, traceurs ou exporteurs du déploiement réel n'ont pas été audités ici |

B404 signale l'import d'un mécanisme d'exécution ; B603 demande la revue de ses
arguments et entrées. **Aucune injection de commande distante n'a été démontrée
par la frontière examinée sous ces hypothèses.** Cette conclusion ciblée n'est
pas « toutes les alertes historiques sont des faux positifs », ni une garantie
de sûreté de l'hôte. Le fichier packaging a été modifié dans PLAN-CAL-01 : il
ne faut pas présenter toutes les entrées Bandit comme fichiers inchangés.

## Preuve du banc et décisions avant exposition

Le banc RELEASE-01 possède son nouveau bundle attesté, ses fichiers read-only,
une DB synthétique et APP_ENV=test ; identité exacte et hash dans
`QA_ENVIRONMENT.json` hors dépôt. Son résultat live HTTP passe par les vrais
workers. Ce résultat n'est pas un test d'exploitation ou d'effacement réel.

Avant cible sensible/externe : propriétaire et permissions du bundle et de ses
parents, publication atomique/immuable, interpréteur/dépendances, intégrité et
révocation d'autorité, environnement minimal et privilèges, quotas/supervision,
journaux/exports et rollback à évaluer sur la cible effective. Responsable et
preuves d'acceptation à nommer ; pas de configuration production inventée.

Les six autres entrées Bandit historiques de juin gardent leur propre revue ;
leur seul libellé ne permet pas une clôture globale. Les quatre checks GitHub
obligatoires restent en place, Sonar réel consigné, faille confirmée = arrêt.
Le gate de revue privacy/sécurité avant bêta externe élargie reste OPEN.
