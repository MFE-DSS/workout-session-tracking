# SCI-RUNTIME-01 — reçu de préparation et d'expériences isolées

26 novembre 2026 — Europe/Paris. Canonique relu/fetché : **`9ef96e39aac400bc53583f62aecafc09f4dda1e3`**. BUILD-01/#446/#447 restent clos. Aucun fichier produit, source scientifique, flag, service ou environnement actif modifié. Nouveau worktree `spec/sci-runtime-01-qualification`, sans commit/PR.

## Verdicts distincts

| Objet | Verdict actuel | Motif |
|---|---|---|
| Catalogue en production | **HOLD** | Le parseur livré refuse toujours4302>4096. L'adaptateur proposé n'est pas appliqué |
| Option sélective jetable | **Parité démontrée sur les sources examinées** | Source entière attestée et JSON entier validé ; omissions éditoriales ciblées ; voir mesures et limites ci-dessous |
| Runtime cible | **HOLD** | Docker local ne répond pas ; aucune campagne Linux3.11.14 exécutée ; SQLite cible et image complète avec le lecteur non qualifiés |
| Sécurité | **Triage borné, conditions de confiance ouvertes** | Pas d'injection de chemin HTTP démontrée ; ancêtres/permissions de la configuration opérationnelle non qualifiés |
| Lecteur complet | **NOT_QUALIFIED**, disabled | Ni l'expérience Mac ni les anciennes CI Linux3.11.18 ne lèvent les deux HOLD |
| Correctif proposé | **GO BUILD PENDING** | Un seul [amendement précis](../../../openspec/changes/archive/2026-11-26-sci-runtime-01/BUILD_AMENDMENT.md), pas une nouvelle architecture |

## A — cause exacte et autorités conservées

Fichier `data/sci/exercise_catalogue.json`, **411788 octets /107 records** ; SHA256 `7d1ae5d3c05c4b76c540789e9e07d0c2c0d96c9a4aa03a28c0b4f964441981fd`. Unique chaîne dépassant4096 : `/records/75/exercise_operational/curation/notes`, **4302 octets UTF-8**, exercice `roulette-abdominale`.

`SourceView.read` borne et atteste les octets complets. `bounded_json` refuse ensuite la chaîne dès l'admission lexicale, avant matérialisation JSON. `load_runtime_profile` appelle cette lecture avant tout job ; le résolveur Legacy, la résolution V3 et la composition effective consomment aussi le catalogue. Traiter le seul premier appel ne suffirait donc pas.

Le catalogue porte les identités/alias et champs scientifiques nécessaires aux rôles et exécutions canoniques. L'expérience conserve **tout sauf** les chaînes au chemin exact `records[i].exercise_operational.curation.notes`, soit107 omissions attestées. Le document projeté n'est jamais présenté comme source complète ; aucune source historique n'est réécrite, aucun Python du bundle historique exécuté. Les références de parité exécutées sont le code courant canonique de confiance.

## Comparaison réellement exécutée

| Vérification | Résultat observé |
|---|---|
| Parseur produit, source inchangée | Refus `json_string_limit`, attendu |
| Parcours incrémental intégral avec la même borne par chaîne | Même refus ; le streaming seul ne résout pas l'incompatibilité |
| Projection spécialisée jetable |107 records,109 résolutions nom/alias et tous rôles bruts identiques |
| Tous champs non éditoriaux | Égalité exacte avec la référence complète moins les seules notes ciblées |
| V2 effective_science_digest | `10e92afb04cd1b14036f5c21e4b3f755a7ac58eddd2cb369be99a355de05b5b9` identique |
| V2 bundle_digest | `091cdfe0758db0d96912a94a47034291624f7939bad7b9e10d177958c877c26a` identique |
| Bundle inventory2 reconstruit en copie privée |95 fichiers attestés + manifeste, chaîne data-only et extension acceptées par le vérificateur canonique avec la seule substitution expérimentale du parseur catalogue |
| V3 binding_digest | `9ef301da08ec3614c7e2a4fbbb95a2384f1c870bca84b6b69eeb4e20a1897389` identique à la référence courante |
| V3 bundle_digest | `78b3e5d99fe05093d6141678fd40f16e744b88d3d87405f14b0f8be357724d94` identique |
| Budget partagé local/bundle | **113/128 fichiers ;3235395/16777216 octets**, sans augmentation. Le futur module changera les pins : remesure obligatoire après build |
| Cas du probe catalogue |17 cas exécutés, incluant nominal/parité et refus digest faux, chaîne SCI trop longue, doublon, escape/surrogate invalides, type note incorrect, JSON tronqué/suffixe, profondeur17, tokens dépassés, non-fini, UTF-8 invalide et dépassement16Mio |
| Régression canonique + worker/API ciblés | **10 PASS,2 SKIP Linux sur Darwin**. Les deux skips ne deviennent pas PASS |

Le benchmark du scanner sur Mac/Python3.11.14 avec tracemalloc relève environ875ms et1614295 octets de pic **Python tracé**. Ce n'est ni un RSS, ni la durée du worker complet, ni une preuve sous CPU/AS Linux. Aucun bilan CPU/SQL/VM/concurrence target n'est revendiqué.

## B — profil runtime et écart exact

L'archive privée existante a été relue sans extraction sur l'hôte et son SHA revérifié : `76f7200d829793a752e33f89a1672eb2b242a12a7a43104c7eaa40e5193b1973`,75357184octets ; config image `sha256:5ee90ab09696c4312cbe2a99654d5d2368d26f2050839858cca0ec801128334e`.

Son contenu déclare Linux/amd64, Debian13.3, Python3.11.14, UID10001 et source `b8fc63ffadba35028af9e1c92c2e48892f9fe403`. Cette image historique ne contient pas le lecteur récent. Sa version SQLite n'a pas été exécutée/établie. Le tag actuel `python:3.11.14-slim` n'est pas une identité de base immuable.

Hôte disponible : Darwin/arm64. `docker version` expire après8s ; une seconde sonde directe en lecture seule `GET /_ping` du socket desktop-linux expire après3s. Aucun redémarrage du daemon, modification de ses limites, du VPS ou du target installé. Aucune image/containeur créé dans cette passe.

**Non exécutés sur cible :** latence HTTP/SQL, nombre/VM SQL, CPU, pic RSS, AS512Mio, plafonds/sortie/timeout, nettoyage sous contrainte, concurrence effective, snapshot et isolation dans l'image. Le protocole de mesure et les contre-exemples sont dans l'amendement. Les anciens témoins CI3.11.18 restent distincts.

## C — sécurité réexaminée

[Alerte GitHub13](https://github.com/MFE-DSS/workout-session-tracking/security/code-scanning/13), Sonar `AaIW9UbPkQr_488ATdJK`, `pythonsecurity:S8707`, relue par API : flux indiqué vers `supervisor.load_runtime_profile` lignes58–60 sur81e5e568. Le reçu historique la donne ouverte ; l'API actuelle renvoie `state:null`, `fixed_at:null`, `dismissed_at:null`. Aucun état de résolution n'est déduit de ces NULL et aucun état/règle/seuil n'est modifié.

Cinq noms de configuration introduits dans la vraie route ASGI renvoient422, sans chemin dans la réponse : profile_path, runtime_profile, muscle_observed_load_profile_path, database_url, bundle_root. Authentification remplacée par un propriétaire synthétique pour ce probe, pas une recette d'authentification réelle. L'owner vient de la dépendance serveur ; le stdin porte owner/from/until/as_of, aucun chemin. L'appel worker est fixe et sans shell.

Sondes de fichiers exclusivement synthétiques : le loader refuse fichier mauvais digest, symlink feuille, FIFO et répertoire ; **un parent symlinké est suivi avant le refus de hash**. Ces sondes du loader contournent explicitement le seul garde de plateforme pour observer l'ouverture sur Darwin : elles ne qualifient pas Linux. Le SourceView refuse séparément parent/feuille symlinkés, chemin absolu et traversal.

Constat résiduel : `O_NOFOLLOW` ne couvre que la feuille du profil ; le loader ne contrôle pas propriétaires/modes/ACL des parents. Le hash attendu doit provenir d'une configuration de confiance, et chaque autorité/ancêtre/monture doit être non remplaçable par les principaux non autorisés. Permissions du profil opérationnel **UNKNOWN** : aucun profil opérationnel n'est fourni/qualifié ici. Les modes700/600 relevés concernent seulement les fixtures jetables. Pas d'exploit distant démontré, pas de certificat de sécurité globale.

## Conservation et suite exécutable

Preuves/scripts jetables privés : `/Users/martinfeldmann/auren-review/sci-runtime-01-evidence-20261126/` : CATALOGUE_SOURCE, CATALOGUE_COMPARISON, BUNDLE_CLOSURE, HISTORICAL_IMAGE_STATIC, DOCKER_READONLY_PROBE, SECURITY_PROBE, SONAR_ALERT_13, logs et empreintes. Aucune de ces vues/probes n'est importée par le produit. La référence de bundle de l'expérience est conservée ; elle ne devient pas un artefact de déploiement.

La prochaine opération produit nécessite l'autorisation du seul amendement proposé. La disponibilité du Docker jetable reste un prérequis technique séparé : un GO code ne rend pas son runtime disponible. Lecteur désactivé, aucune activation QA/OVH/DATA/mobile/release.

PILOT-01 avance séparément par un addendum privé au paquet existant : mode opérateur et faits fictifs conservés ; contact, copies/rétentions/effacement et admission du compte/appareil restent à décider, sans inventer de politique ou assigner un testeur externe. Aucune nouvelle collecte ni distribution dans cette passe. Le G1 artistique DA-READINESS-01 est conservé, sans écran ni nouvel asset produit.

## Relecture et vérification de cette préparation

Relecture indépendante fraîche du paquet par `runtime_amendment_builder_check` : **nothing important left**, aucun élargissement identifié ; lecture de la proposition et des preuves seulement, pas une revue du futur code. Le candidat superposé restera distinct de l'image QA. Aucun fichier ni test modifié par le reviewer.

`check_scope.py` : DOCS,6 fichiers. `check_spec_protocol.py` PASS ; `openspec validate sci-runtime-01 --strict --no-interactive` PASS ; `git diff --check` PASS. Pas de sweep local général ni CI/PR nouvelle pour cette préparation non committée. La référence distante a été relue après les expériences et reste9ef96e39. Diff produit app/data/tools/tests/deploy/clients/CI et gitleaks vide. Les autres worktrees et processus actifs sont préservés.
