# Plafonds candidats à qualifier — aucune valeur mesurée de service

Ces valeurs sont des choix d’ingénierie **proposés pour BUILD01**, pas des conclusions admises ou un runtime activé. Aucun budget S/E/W/R de D4 n’est augmenté. Toute valeur changée exige un diff/une justification et de nouvelles preuves, jamais un fallback silencieux.

| Ressource | Plafond proposé | Garde / verdict attendu |
|---|---|---|
| Candidats | S200/E200/W500, R1000 globaux + sentinelles | raw IDs ASC avant qualification ; overflow ->couverture tronquée |
| Contrôle de graphe V3 | G500 lignes scalaires globales, y compris sets préparatoires/incomplets | garde additionnelle, pas des contributions ; insuffisant ->mapping/provenance UNKNOWN |
| Requêtes SQL |4096 statements maximum, y compris PRAGMA/gardes/alias/sentinelles | compteur de l’adaptateur ; aucun appel ORM eager ou COUNT global ; stop avant statement4097 |
| Instructions VM SQL |2 000 000 globales, progress callback tous1000pas | bornes discrètes ; test d’overshoot<=1000pas ; pas garantie de temps OS |
| SQL/deadline de travail |1500ms monotones depuis ouverture du lecteur, lock timeout100ms | progress handler + deadline entre lectures/blobs/parses ; timeout effectif attesté |
| CPU enfant |RLIMIT_CPU soft2s/hard3s | enfant seulement avant imports lourds ; sortie tuée/échec ->UNAVAILABLE |
| Temps supervisor |3000ms monotones depuis entrée service après auth/validation | aucun waiting queue ; kill+wait de l’enfant avant réponse ; création processus/OS cleanup peuvent dépasser : mesurer et ne pas promettre une deadline réseau absolue |
| Mémoire enfant |RLIMIT_AS soft=hard512MiB d’espace d’adressage ; RLIMIT_CORE=0 | limite OS avant imports/parses ; ne pas présenter AS comme mesure précise de RSS ou du serveur entier ; mesurer pic RSS séparément au build |
| Concurrence |1worker actif par processus HTTP, aucune file d’attente | slot occupé ->503 générique ; qualification déploiement doit consigner nombre de processus HTTP et mémoire cumulée ; pas de changement de serveur ici |
| Entrée commande interne |1KiB | owner authentifié +fenêtre +identité de lecture seulement ; pas de token/secret |
| Corps DB JSON |8KiB observation/reçu ET publication_json,128KiB binding ET évaluation,2MiB cumulés | blobopen TEXT readonly après garde owner et rowid, len avant read ; aucune projection ORM de gros TEXT |
| Autres TEXT DB |512octets par nom/identité,512octets template_slug_snapshot ; mêmes2MiB cumulés | pas de troncature silencieuse des identités ; dépassement ->source inconnue ; marker illisible ne devient pas Legacy |
| JSON non fiable |profondeur16,65536tokens par corps, chaîne4096octets, nombres finis | validation UTF8/structure avant matérialisation ; doublons de clés/NaN/Infinity/forme inattendue refusés ; pas json.loads puis contrôle seulement après allocation |
| Fichiers d’autorité immuables |128fichiers /16MiB cumulés, digest vérifié, chemins de manifeste sûrs | lecture/parse bornés, pas réseau ; bundle V3 absent/différent ->UNKNOWN ; politique fondamentale indisponible ->UNAVAILABLE |
| Sortie JSON |1MiB UTF8, max500facts/15zones, erreur publique<=1KiB | serializer et pipe comptent avant émission ; parent lit par blocs bornés, ne capture jamais stdout/stderr sans plafond ; au-delà ->UNAVAILABLE |

L’objectif n’est pas de maximiser le nombre de faits retournés, mais de servir une part prouvée sans mettre en péril l’app. Un historique volumineux peut rester PARTIAL/UNKNOWN/UNAVAILABLE. Ne pas augmenter les plafonds pour transformer un cas rouge en vert.

## Pourquoi le worker proposé
Les garde-fous SQLite ne bornent pas seuls le parse ni la mémoire du processus HTTP. Le worker jetable permet des limites OS locales sans toucher la VM ou les dépendances. Il ne doit ni servir une requête réseau, ni écrire la DB, ni créer de fichiers de données ; connexions mode=ro/query_only et authorizer à whitelist lectures/transaction/PRAGMA nécessaires. Le parent ne change pas ses propres rlimits ; pas de preexec_fn dans le serveur multithreadé. Les signaux ne ciblent que l’enfant lancé par cette requête.

Le runtime doit prouver la présence et l’efficacité de ces contrôles. Linux/Python3.11.14 est le candidat du Dockerfile canonique ; SQLite exact et AS/CPU restent à mesurer. macOS/Windows/PostgreSQL ou capability absente : qualification HOLD, pas un test mémoire dangereux sur le Mac ni un faux PASS. Tests sémantiques à ports substitués restent séparés des tests Linux réels.

## Profil de qualification et activation
Le futur rapport doit épingler HEAD/image, OS/Python/SQLite, versions/digests catalogue/bundle, caps, limites réelles du conteneur, nombre de processus HTTP, plans SQL, pics RSS/AS, VM/temps, taux de PARTIAL/UNAVAILABLE et cleanup. État initial NON_QUALIFIED. Activer la route dans un banc synthétique sous GO pour produire ces preuves ; usage d’un runtime réel attend la correspondance exacte au profil qualifié et ses permissions DATA/ops. Aucun flag/secret/service distant changé dans cette préparation ou par le simple merge futur.

La première qualification locale pourrait utiliser l’image QA existante reconstruite dans un banc isolé sous le futur GO ; aucun Dockerfile, pipeline, push d’image ou service QA vivant à modifier. Si les caps rendent le cas nominal indisponible, produire HOLD et un amendement borné justifié, pas prétendre un lecteur utilisable.

## Références techniques — portée limitée
Les contrôles sont documentés dans les [API Python resource](https://docs.python.org/3.11/library/resource.html) : disponibilité et ressources varient selon la plateforme, AS/CPU sont des limites distinctes. Le [progress handler sqlite3](https://docs.python.org/3.11/library/sqlite3.html#sqlite3.Connection.set_progress_handler) permet d’interrompre le travail SQL, pas de certifier toute latence système. La [documentation subprocess](https://docs.python.org/3.11/library/subprocess.html#subprocess.Popen.kill) précise que la création du processus peut retarder l’effet d’un timeout ; borner aussi le pipe et prouver kill+wait. Ces références API ne qualifient pas notre déploiement.

Le manifeste de packaging a son cap128KiB compris dans16MiB de sources,128entrées maximum. Les empreintes/paths sont contrôlés avant imports et parsing selon SOURCE_AUTHORITY.md. Tous les petits TEXT DB participent aux2MiB DB ; les fichiers d’autorité au budget séparé16MiB. Une fermeture de l’ensemble de sources qui ne tient pas sous128entrées reste UNKNOWN V3, pas une garantie que le package actuel tiendra. Le plafond CPU inclut imports et attestation ; cas nominal à qualifier avant service.
