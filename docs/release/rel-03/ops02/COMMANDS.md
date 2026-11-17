# OPS-02 — commandes et actions bornées à faire approuver

**NON EXÉCUTÉES.** Ce document est destiné à l'agent ; l'opérateur n'a pas à copier ces commandes. Source et références sont remplies depuis DELIVERY_RECEIPT.md et les acquisitions réelles. Aucun `eval`, fichier JSON sourcé comme shell, token dans argv, `--clobber`, prune ou suppression globale.

## 1. Garde, source et préparation d'image

Dans GitHub, après choix des deux acteurs humains : créer/qualifier seulement le dépôt privé de garde et une release dédiée. Créer `qa-release` avec reviewer direct, prevent_self_review=true et sans bypass administrateur. Conserver toutes les protections existantes. Définir la référence publique `docs/release/rel-03/proof-store.json` sur le dépôt effectivement privé et actualiser le contrat opérationnel existant `openspec/changes/rel-03-continuous-android-qa/OVH_EVIDENCE_AND_CONFIG.md` avec l'identité non secrète et le reçu du GO. Livrer ce delta de configuration explicite par PR : ce n'est pas un push100%docs, la CI canonique s'exécute donc réellement. Puis définir les variables `QA_IMAGE_REPOSITORY`, `QA_IMAGE_RELEASE_ID` et les références protégées `QA_IMAGE_WRITE_TOKEN`, `QA_IMAGE_AES256_KEY_HEX`, `QA_RELEASE_AUDIT_TOKEN` ; aucun contenu secret dans Git.

Le token image ne reçoit que Contents:write sur ce seul dépôt privé. Le token d'audit reste en lecture seule avec les droits de lecture de protection nécessaires. Clé image32octets dédiée, distincte des clés d'application, de preuve et de backups personnels. La clé SSH d'audit dédiée et les known_hosts qualifiés deviennent les références protégées `QA_OVH_AUDIT_KEY` / `QA_OVH_KNOWN_HOSTS` avant release ; pas de copie de la clé SSH personnelle.

Figer **le nouveau SHA canonique contenant CONFIGURED**, pas le parent OPS-02 encore UNPROVISIONED. Attendre ses propres quatre check-runs completed/success et sa CI réelle ; les checks du parent ne sont jamais réutilisés comme checks de ce SHA. L'acteur de dispatch choisi exécute alors le workflow sur cette source vérifiée. Une nouvelle ref de tag `qa-ops02-<12premiershex>` peut pointer **ce seul nouveau SHA** après ce GO, sans remplacement de tag. Le garde vérifie encore GITHUB_SHA ; une ref déplacée entraîne un refus. Toute autre modification produit/code entre les deux impose une nouvelle qualification de source, sans extension tacite du paquet.

```bash
gh workflow run qa-release.yml --repo MFE-DSS/workout-session-tracking \
  --ref "$QA_SOURCE_REF" -f operation=PREPARE_IMAGE -f source_sha="$QA_SOURCE_SHA"
```

Le reviewer humain distinct examine le SHA et approuve avec `APPROVE_QA_IMAGE <SHA exact>`. Pas de rerun héritant de l'approbation. Acquérir le résultat et son artifactID depuis GitHub, puis télécharger/déchiffrer les mêmes octets en privé avec les outils existants :

```bash
python -m tools.qa_delivery.image_transport restore \
  --config /chemin/prive/image-store.json --reference /chemin/prive/image-reference.json \
  --output /chemin/prive/nouveau-image.tar
```

Les chemins ci-dessus sont des entrées privées à qualifier, pas des destinations existantes à écraser. Config privée0600/parent0700 : repository,release_id,key_file ; reference privée : run_id,attempt,artifact_id,source_sha. GH_TOKEN sert l'acquisition de provenance ; QA_IMAGE_READ_TOKEN sert seulement la garde. En cas d'intention d'upload sans succès qualifié, `image_transport reconcile --config … --intent … --output <nouveau-reçu>` ne fait que lire. Un job image échoué ne devient pas un build indépendant accepté par cette seule lecture ; nouvelle opération approuvée si nécessaire, aucune répétition automatique d'upload.

## 2. Installation isolée et état synthétique

VPS exact : ubuntu@vps-491c685f.vps.ovh.net, IP51.91.79.44, contrôle strict de clé existante. Transférer uniquement image/outil acquis et références privées dédiées, jamais DB/secret personnel. Installer un checkout/outillage immuable de ce SHA sous `/opt/auren-qa-ops/<SHA>` ; pas de modification du site `/opt/workout-session-tracking`. L'outillage Python privé est séparé du venv web, avec httpx0.28.1 et Node existant pour les codecs ; aucun upgrade Python/FastAPI du site.

Avant chaque création : refuser les noms préexistants, les drivers/Options non attendus, UID/propriétaire/mode non conformes et collisions de comptes. Le helper d'isolation vérifie aussi le label du réseau et refuse des règles étrangères ; il ne les flush/reconstruit pas.

```bash
sudo docker load --input /chemin/prive/nouveau-image.tar
sudo docker image inspect "$QA_IMAGE_ID"
sudo docker volume create --label org.auren.qa=rel03 auren-qa-rel03-data
sudo docker volume create --label org.auren.qa=rel03 auren-qa-rel03-config
sudo install -o root -g root -m 0755 deploy/qa/isolate_network.py /usr/local/libexec/auren-qa-isolation-v1
sudo install -o root -g root -m 0644 deploy/qa/auren-qa-isolation.service /etc/systemd/system/auren-qa-isolation.service
sudo install -o root -g root -m 0644 deploy/qa/auren-qa-rel03.service /etc/systemd/system/auren-qa-rel03.service
sudo systemctl daemon-reload
sudo systemctl start auren-qa-isolation.service
```

Les sources relatives `deploy/qa/*` sont prises exclusivement dans le checkout vérifié du SHA livré, avec empreintes. Aucun install sur un fichier préexistant sans comparaison et décision d'incident. Le helper ajoute un réseau nommé interne et le seul hook INPUT `-i br-auren-qa -j AUREN-QA-IN` ; chaîne : ACCEPT retours RELATED,ESTABLISHED puis DROP. Aucun flush/policy globale ou changement Tailscale.

Préparer les racines des **deux seuls volumes neufs data et config** en UID10001/GID10001 et mode0700, avant la première écriture. Pas de chown/chmod récursif ni de volume préexistant. Matérialiser les fichiers privés dans config en UID10001/mode0600, par opérations exclusives depuis le canal privé. Les mountpoints Docker ne sont utilisés qu'après vérification driverlocal, Options vides, noms/labels exacts et lien avec les volumes créés par cette opération. Ne jamais utiliser un chemin fourni librement par une preuve comme destination système.

Entrée `initialize.json` privée : schema_version=`qa-initialization/1.0.0`, source_sha exact, environment_id=`qa-rel03-rc01-20261117`, approval_ref de cette décision, accounts_file, auth_secret_file, data_dir=`/var/lib/qa`, bundle_root=`/opt/science`, science_mode=`ACTIVE_PUBLISHED`. Le fichier accounts est uniquement les deux nouveaux usernames qa02-rel03-rc01-a/b et leurs nouveaux mots de passe ; pas d'email. Le secret auth est neuf et distinct. Aucune valeur secrète dans ces exemples.

```bash
sudo docker run --rm --network none --read-only --cap-drop ALL --security-opt no-new-privileges \
  --user 10001 --memory 1g --cpus 1 --pids-limit 128 \
  --tmpfs /tmp:rw,noexec,nosuid,size=67108864,mode=1777 \
  --mount type=volume,source=auren-qa-rel03-data,target=/var/lib/qa \
  --mount type=volume,source=auren-qa-rel03-config,target=/etc/secrets,readonly \
  --entrypoint python "$QA_IMAGE_ID" -m tools.qa_delivery.initialization \
  --config /etc/secrets/initialize.json
```

Cette surcharge d'entrypoint concerne le seul conteneur d'initialisation jetable sans réseau ; le service est créé ensuite avec les Entrypoint/Cmd originaux. Initialisation depuis vide par migrations, seeds de **références canoniques** (catalogue/méthodes/identités), register/device canoniques, autorité existante et ancre. Aucun lifespan/create_all ni fixture de base. Un état `state` existant ou partiel refuse toute reprise ; aucun reset automatique. Relever tables/FK/versions et catalogue builder réellement non vide, zéro mesure/nutrition/fait d'entraînement créé.

Copier l'ancre privée produite dans le nouveau volume config et écrire le `qa-config.json` exact avec digest acquis, auth/access/features/signing refs distinctes (voir OVH_TECHNICAL_RUNBOOK.md). DB=`/var/lib/qa/state/qa.db`. Config/accords BODY/NUT ne sont pas interchangeables. Conserver le kit privé hors runtime puis retirer de ce nouveau montage uniquement les entrées d'initialisation contenant les mots de passe ; garder les clés nécessaires au runtime. Aucune suppression de données historiques.

## 3. Service exact, d'abord en maintenance

```bash
sudo docker create --name auren-qa-rel03 --restart no --read-only --cap-drop ALL \
  --security-opt no-new-privileges --network auren-qa-rel03-internal --ipc private \
  --cpus 1 --memory 2147483648 --pids-limit 128 \
  --tmpfs /tmp:rw,noexec,nosuid,size=67108864,mode=1777 \
  --publish 127.0.0.1:8088:8080 \
  --mount type=volume,source=auren-qa-rel03-data,target=/var/lib/qa \
  --mount type=volume,source=auren-qa-rel03-config,target=/etc/secrets,readonly \
  --log-driver local --log-opt max-size=10m --log-opt max-file=3 \
  --health-cmd 'python -c "import http.client as h;c=h.HTTPConnection(\"127.0.0.1\",8080,timeout=3);c.request(\"GET\",\"/__qa_liveness\");assert c.getresponse().status==200"' \
  --health-interval 30s --health-timeout 5s --health-retries 3 --health-start-period 30s \
  "$QA_IMAGE_ID"
sudo systemctl start auren-qa-rel03.service
```

Sans marqueur : liveness200/data_readyfalse, toutes routes métier503. Valider image/argv/source/UID/config/ancre, puis effectuer la sauvegarde/restauration initiale du §5 **avant** toute activation. Seulement après cette preuve, écrire le seul marqueur privé `qa-activation/1.0.0` avec source_sha et config_sha256 réels dans `/var/lib/qa/activation.json`. Redémarrer **QA seul**, puis version/health/API/SCI concordants. `systemctl enable` des deux unités propres seulement après tests de reprise du service et persistance. Aucun reboot du VPS inclus.

Installer le collecteur root-owned et le compte à mot de passe verrouillé `qa-audit`, shell d'exécution `/bin/sh` (OpenSSH l'utilise pour la forced-command), sans accès interactif/PTY/forwarding. Sa seule clé dédiée porte `restrict,command="sudo -n /usr/local/libexec/auren-qa-observe-v1"`. Aucun droit Docker, aucune modification globale de sshd. Le sudoers exact est `qa-audit ALL=(root) NOPASSWD: /usr/local/libexec/auren-qa-observe-v1 ""` : aucun argument admis. Le wrapper root-owned emploie l'interpréteur qualifié et le seul collecteur immuable ; jamais sudo python arbitraire. Valider sudoers avec visudo avant installation, clé publique exacte et parents non modifiables par l'auditeur. Les trois reçus root `/etc/auren-qa/{observer-policy,activation-proof,routing-loaded}.json` sont enregistrés depuis l'état acquis réel, pas depuis l'application. `network=auren-qa-rel03-internal`, restart_policy=no ; limites exactes du conteneur ci-dessus.

## 4. DNS/TLS et routage chargé

Dans OVH DNS de spignos.com : créer uniquement A `qa`→51.91.79.44 si absent. Pas d'AAAA, racine/www/anciens RR modifiés. Relever la valeur/TTL et son reçu. Créer le webroot vide `/var/lib/auren-qa-acme`, sans lien vers fichiers applicatifs.

Générer d'abord `qa_http_vhost()` du collecteur dans un nouveau `/etc/nginx/conf.d/auren-qa-rel03.conf`, root-owned. HTTP80 garde les écoutes wildcard déjà utilisées par les sites : ne pas introduire une écoute IP80 plus spécifique qui détournerait leurs requêtes. `nginx -t`, reload explicite et contrôle des huit domaines préexistants avant/après. Puis avec le compte ACME existant seulement :

```bash
sudo certbot certonly --webroot --webroot-path /var/lib/auren-qa-acme \
  --cert-name qa.spignos.com -d qa.spignos.com --non-interactive
```

Si aucun compte utilisable, conflit de certificat, challenge ou signature incorrect : arrêt, pas d'acceptation automatique de conditions ni remplacement des certificats personnels. Générer ensuite `qa_vhost(policy)` complet (ACME + TLS IPpublique, aucun logging de requête QA), nginx-t, reload et huit domaines préexistants vérifiés. Qualifier réellement la nouvelle génération master/workers/config dans routing-loaded.json. Certbot renew QA en dry-run, puis requalifier tout reload ; le remplacement de workers impose aussi une nouvelle attestation, pas un auto-stamp depuis fichiers.

## 5. Backup, copie jetable et rollback

Créer un nouveau dossier privé horodaté de backup dans le volume QA. `tools.qa_delivery.database backup /var/lib/qa/state/qa.db <nouveau-fichier>` conserve et vérifie toutes les tables ; si la source change pendant l'acquisition, il refuse. Le manifeste ne peut pas être remplacé. Aucune utilisation du backup workout défectueux.

L'export initial n'est **pas** `proofs pack` : ce dernier exige les onze preuves d'une release, dont ancien natif et cutover, qui n'existent pas encore. Exporter seulement la DB snapshot, son manifeste et l'ancre dans un nouveau dossier privé, sans secret runtime. Pour chacun de ces trois fichiers, vérifier taille≤128Mio et somme≤256Mio, chiffrer séparément via le codec AES-GCM existant `proofs.crypto`, puis écrire exclusivement avec `proofs.exclusive_write`. Exemple d'appel Python (chemins déjà qualifiés et clé privée32octets) :

```python
from tools.qa_delivery import proofs

payload = source.read_bytes()  # fichier privé du snapshot vérifié, jamais DB writer
proofs.require(len(payload) <= proofs.MAX_FILE, "initial_backup_file_size")
cipher = proofs.crypto("encrypt", key_file, payload)
proofs.exclusive_write(new_encrypted_path, cipher)
plain = proofs.crypto("decrypt", key_file, new_encrypted_path.read_bytes())
proofs.require(proofs.sha(plain) == proofs.sha(payload), "initial_backup_readback")
proofs.exclusive_write(new_restoration_input, plain)
```

Conserver noms, tailles et SHA256 plaintext/ciphertext dans le reçu privé d'export initial ; aucun artifact de release fabriqué. Copier les trois ciphertexts sur le Mac privé, déchiffrer avec le même codec dans des fichiers neufs et revérifier ces digests. `database restore <backup> <nouvelle-destination>` vérifie le manifeste associé ; `database verify` contrôle la copie jetable sans réseau, jamais le volume writer. Préserver l'ancre et comparer tables/digests sans divulguer les lignes. Le futur paquet de release complet utilisera `proofs pack` seulement lorsque toutes ses véritables preuves existent.

Sauvegarde constatée avant activation et avant chaque release ; **aucun timer quotidien automatiquement sain n'est déclaré**. Le fonctionnement périodique peut être cadré séparément ; les tests de ce paquet prouvent la récupération effectuée, pas une supervision de production.

Rollback de service : fermer QA, `systemctl stop auren-qa-rel03`, vérifier absence8088 et services personnels actifs ; conserver état/image/volumes/preuves. Restaurer uniquement le vhost et le RR QA propres si créés, nginx-t/reload puis sites/Tailscale. Ne retirer le réseau/filtre propre qu'après arrêt de tous ses raccordements et vérification des seules références créées. Après écritures : sauvegarder l'état courant ; aucune ancienne copie promue comme writer ni downgrade de schéma.

## 6. Acceptation et arrêt

Vérifier l'origine publique réellement reliée au conteneur par les outils OVH/GitHub, nonce frais, DNS/TLS sans contournement, API/SCI/schéma et comptes A/B réels. Prove non-egress, blocage vers services hôte/autres réseaux, unique writer et restart QA ; vérifier Tailscale avant/après reload. Chaque ligne FAILED/UNAVAILABLE conservée distinctement.

Aucun EAS Build/Update, APK, OTA, transfert à un appareil externe ou réinterprétation de la DATA policy dans ces commandes. Le candidat vient ensuite, sous ses gates distinctes.
