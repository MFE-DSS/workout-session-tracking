# SCI-RUNTIME-01 — amendement unique proposé

26 novembre 2026, Europe/Paris. Parent `9ef96e39aac400bc53583f62aecafc09f4dda1e3`.
**PROPOSED — GO BUILD NON REÇU — lecteur toujours désactivé.**

## Why

Le refus vient d'une note éditoriale, non d'un rôle SCI. Le lecteur actuel refuse correctement cette source sous son contrat JSON générique. Une expérience jetable démontre une projection sans les seules notes de curation, avec intégrité du document entier et parité des autorités. Cette expérience n'est ni l'adaptateur produit ni une qualification Linux.

## Choix proposé et alternatives

| Option | Résultat / coût | Décision proposée |
|---|---|---|
| Projection sélective, digest des octets complets | Parité des 107 identités/rôles, 109 résolutions nom/alias, composition v2 et admission data-only du bundle V3 ; vérifie toute la grammaire, omet seulement les notes éditoriales avant matérialisation | Retenir ; exception de lecture explicite et localisée |
| Lecture incrémentale intégrale | Le maintien de la limite par chaîne refuse toujours les 4 302 octets. Réduire le tampon ne change pas cette règle. Une lecture réellement streamée exige également la vérification du document entier et de son digest | Ne résout pas seule le HOLD ; le parcours sélectif peut utiliser un scanner incrémental |
| Hausse du plafond générique | Peut accepter la note, mais élargit tous les champs/payloads concernés et la surface de ressources | Non retenue ; aucune preuve actuelle ne justifie cette hausse |

## Contrat exact de l'exception

1. Lire les octets complets avec `SourceView.read`, mêmes protections fichier régulier, taille, hash, cohérence avant/après et budget partagé. Le SHA-256 complet reste l'autorité et la source canonique reste inchangée.
2. Valider le JSON entier : UTF-8 strict, grammaire, fin exacte, absence de clés dupliquées, nombres finis, escapes valides, profondeur16 et plafond lexical65 536 selon la sémantique actuelle. Un préfixe valide n'est jamais un document complet.
3. Seul le chemin `records[entier].exercise_operational.curation.notes`, de type chaîne, peut être parcouru sans matérialiser son texte. Ses caractères/escapes sont validés jusqu'à sa fin et restent bornés par les octets de source admis. C'est une **exception au plafond scalaire pour ce seul champ opaque**, pas un relèvement général de4096. Aucun autre champ nommé notes n'est exempté.
4. Tous les autres champs, y compris l'intégralité du header, identités/alias, rôles, exécutions canoniques, content_alignment, équipement et métadonnées non éditoriales, sont conservés. Leurs chaînes brutes/encodées et décodées gardent4096. Ce choix plus conservateur qu'une petite whitelist évite une perte d'autorité future non examinée.
5. Retourner une vue explicitement projetée, jamais présentée comme le catalogue complet ; aucune sérialisation de cette vue ne remplace la source ou son digest. La liste des chemins omis est une preuve de qualification, pas un DTO métier nouveau.
6. Utiliser ce même adaptateur pour la préadmission locale, le résolveur Legacy, la résolution V3 et `compose_effective`, y compris dans le bundle attesté. Aucun parsing permissif parallèle ne subsiste.
7. Le parseur générique `bounded_json`, ses utilisateurs DB/manifeste/politiques et tous les plafonds restent inchangés. Ne jamais exécuter/importer du Python du bundle historique.

## Fichiers proposés et ownership

| Fichier | Delta autorisable proposé |
|---|---|
| `app/services/muscle_observed_load/catalogue_source.py` nouveau | Scanner/projection strict spécialisé, aucune dépendance nouvelle |
| `app/services/muscle_observed_load/provenance.py` | Méthode de vue catalogue et appel de compose_effective ; lecture/hash/budget existants conservés |
| `app/services/muscle_observed_load/projection.py` | Deux consommateurs de catalogue, calculs/états/roles inchangés ; reste l'unique exception d'import SCI existante |
| `app/services/muscle_observed_load/supervisor.py` | Préadmission catalogue utilisant la vue spécialisée, lifecycle/commande/rlimits inchangés |
| `tests/test_muscle_observed_load_catalogue_source.py` nouveau | Cas nominaux, frontières et contre-exemples du scanner |
| `tests/test_muscle_observed_load_provenance.py` | Refus générique conservé + parité de l'adaptateur et budget local/bundle |
| `tests/test_muscle_observed_load_worker.py` | Admission réelle par worker sur fixture source attestée ; limites conservées |
| `tests/test_mobile_muscle_observed_load.py` | Même contrat et refus des paramètres de configuration HTTP |
| `tools/muscle_observed_load_qualification.py` nouveau | Harness isolé d'inventaire/campagne Linux, sans activation/déploiement et sans modification du worker produit |
| OpenSpec et `docs/science/sci-runtime-01/` | Acte, plan, résultats et closeout du seul scope |

Relire les leases et le canonique au GO ; aucun fichier partagé mobile, writer, TIME-01, SCI allocation, mapping, catalogue, Dockerfile, workflow, secret ou configuration OVH n'entre dans ce delta. `SOURCE_PINS.json` historique112 empreintes et `.gitleaksignore` sont hors scope. `_REQUIRED` découvre le nouveau module : recalculer le futur profil et remesurer le budget, sans recopier les pins de l'expérience.

## Profil Linux à qualifier — pas de cible inventée

L'archive historique revérifiée est Linux/amd64, Debian13.3, Python3.11.14 déclaré, UID10001 ; imageconfig `sha256:5ee90ab09696c4312cbe2a99654d5d2368d26f2050839858cca0ec801128334e`, source b8fc63f, sans lecteur récent. Son SQLite exact n'est pas exécuté/établi ici. Le Dockerfile actuel emploie un tag `python:3.11.14-slim`, donc ne suffit pas à attester un digest de base.

Le harness devra travailler dans une copie jetable, sans réseau externe ni compte réel. Un conteneur peut être lancé depuis l'archive vérifiée avec les seuls fichiers candidats montés read-only dans `/opt/auren`, plus un bundle neuf attesté dans `/opt/science`, une DB synthétique et un profil test privés. **Ce profil de source superposé est un candidat distinct de l'image QA inchangée.** Ne pas modifier/copier de fichier dans l'image/les conteneurs actifs ; aucun tag, push ou déploiement. Une qualification sans superposition exigera ultérieurement une image complète correspondante et les gates de release propres ; elle n'est pas acquise par ce mandat.

Conditions proposées à reproduire : architectureamd64, Python3.11.14 exact, SQLite capturé réellement, FastAPI/Starlette/imports et entrypoint HTTP réels ; un seul processus HTTP, un worker simultané sans file ; 1CPU/2Gio/pids128, rootfs read-only, cap-drop/no-new-privileges, tmpfs64Mio, pas d'accès aux secrets/volumes existants. Capturer les limites effectives, pas seulement les options demandées. Toute divergence d'OS/ABI/librairie/native ou de source garde HOLD jusqu'à qualification explicite du nouveau profil. La simple égalité Python est insuffisante.

## Campagne et plafonds conservés

| Mesure / frontière | Preuve requise sur le candidat Linux exact |
|---|---|
| Identité | Imageconfig/archive/montages/source/bundle/profil SHA, `/etc/os-release`, architecture, Python et SQLite exécutés, versions HTTP, UID/GID, commande et processus effectifs |
| Temps | Latence monotone bout en bout, CPU enfant, SQL≤1,5s, CPU enfant2s soft/3s hard, parent3s ; conserver durées observées y compris démarrage/kill/reap, sans promettre temps réel absolu |
| Mémoire | Pic RSS réel et méthode d'échantillonnage, `RLIMIT_AS`512Mio et CORE0 dans l'enfant, état cgroup2Gio ; distinguer MemoryError/AS, SIGXCPU, timeout et OOM attesté |
| SQL | Nombre de statements incluant setup≤4096, VM≤2 000 000 par callback1000, plans et temps des requêtes ; lock100ms ; aucun DDL/DML via la connexion read-only |
| Entrées/sorties | S200/E200/W500/R1000/G500 ; DBJSON8192, binding/evaluation131072, total2Mio ; texteDB512 ; source128fichiers/16Mio ; manifeste131072 ; stdin1024 ; stdout1Mio |
| Frontières | Cas à la borne et juste au-delà, profondeur/tokens/chaîne, JSON tronqué/dupliqué/malformé, digest changé, mutation de source, sortie excessive, worker bloqué et concurrence |
| Cohérence | Deux propriétaires, transaction/snapshot et révision concurrente, préfixe ancien masquant le récent, estimé/NULL/futur, V3 sans chaîne/catalogue, substitution et corrections ; états conservateurs sans promotion EXACT |
| Nettoyage | PID enfant observé, terminaison ET wait/reap, slot rendu, descripteurs refermés, aucun descendant restant ; aucun writer/SET/FINISH déclenché |
| Fidélité HTTP | Vrai endpoint isolé et même profil source, réponses strictes, aucune route QA activée ; comparaison avec les captures directes instrumentées |

Le harness collecte les métriques hors payload métier et sans credentials. Les fixtures peuvent tester le schéma d'un profil admis, mais restent nommées TEST_ONLY et ne constituent pas une qualification. Aucun profil opérationnel exporté QUALIFIED avant succès réel de l'ensemble et scellement de la preuve du profil exact. Le service QA reste disabled même en cas de succès. Tout dépassement laisse HOLD/UNAVAILABLE ; aucune augmentation automatique de budget ni fallback moins sûr.

## Sécurité / confiance à établir

L'alerte13/S8707 reste à relever ; aucune suppression/dismissal. Les chemins proviennent des Settings serveur. Les cinq paramètres de configuration HTTP testés répondent422 ; le job transporte owner/from/until/as_of, aucun chemin. `O_NOFOLLOW` protège la feuille du profil mais pas ses ancêtres, et le loader ne vérifie pas UID/modes. Le harness doit refuser une qualification si profil, DB, bundle, sources ou ancêtres sont symlinkés, modifiables par un principal non autorisé, ou si une ACL/monture le permet ; relever UID/GID/modes/mounts et stratégie immuable. Le worker lit en tant qu'UID10001, qui ne doit pas pouvoir remplacer ces autorités.

Aucun exploit distant n'est démontré par cette passe. Un changement de loader pour une vulnérabilité réellement démontrée exigerait le delta exact avant apply ; aucune correction sécurité opportuniste dans cet amendement.

## RED → GREEN et gates de livraison après GO seulement

1. Ajouter les tests qui exposent le refus canonique du futur adaptateur et les contre-exemples. Le parseur générique doit continuer à refuser la note.
2. Implémenter le seul adaptateur, prouver parité Legacy/V2/V3/extension, lecture entière et budgets inchangés, puis les consommateurs backend concernés.
3. Exécuter la campagne Linux dans la cible jetable fidèle. Si Docker indisponible ou profil différent, publier les écarts exacts et garder RUNTIME HOLD ; ne pas fabriquer de mesures CPU/RSS ou profil.
4. Exécuter `check_scope.py` sur le vrai diff et ses tests ciblés/broad/sécurité/protocole/OpenSpec ; aucune réduction des checks ou des budgets. Revue indépendante entière et corrections en scope.
5. Publier le HEAD autorisé, CI protégée exacte, merge commit gardé et closeout sous GOV-MERGE-01. Aucun GO MERGE routinier à redemander. Aucun scope mobile, activation, OVH ou release inclus.

**Décision demandée : autoriser ce seul adaptateur catalogue et son harness de qualification isolée.** Cette proposition n'est pas un GO reçu. Les budgets, l'admission descriptive SCI et l'état disabled ne changent pas ; l'activation restera une décision opérationnelle séparée.
