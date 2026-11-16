# REL03 — reçu de maintenance du VPS existant

16 novembre 2026 — Europe/Paris. Parent documentaire `bd977f3baa0de7f3ea61cba17f9b6ae6615660ab`. **Maintenance système exécutée ; services revenus après deux redémarrages. MVP-RC-01 reste NOT_READY.** Aucun achat, déploiement QA, DNS/TLS QA, APK ou OTA.

## Autorisation et périmètre

L'opérateur a choisi le réemploi, autorisé les sauvegardes et tests en copie, puis confirmé : « j'autorise la maintenance, maintenant les interruptions possibles ». La console KVM OVH était ouverte. Ces décisions couvrent cette maintenance ; elles ne valent pas autorisation de déployer QA ou de distribuer un candidat.

Le [plan initial](EXISTING_HOST_MAINTENANCE.md) conserve ses constats historiques. Ce reçu actualise son statut ; il ne transforme pas ses propositions anciennes en opérations effectuées. Aucun GO BODY/NUT/MOB06/MOB07 ou contrat scientifique n'est rouvert.

## Options, risques et choix appliqué

Le choix documenté avant exécution est une mise à niveau surveillée sur place, avec copies restaurées avant mutation, conservation des runtimes nécessaires et contrôle de reprise. Une réinstallation et un achat séparé sont écartés. Les risques retenus sont l'interruption des services, le changement de Python système, la migration automatique PostgreSQL, les dépôts tiers et la concurrence d'écoute HTTPS.

L'outil officiel signé, daté du 14 octobre 2026, proposait naturellement Ubuntu 26.04.1 et admettait explicitement `plucky` dans son champ `From`. Cette preuve plus récente précise la note générale du 28 août décrivant une étape intermédiaire. Aucun `-d`, remplacement forcé des sources ou contournement de signature. Archive de l'outil : SHA256 `5693a2405c3972968cee94185b0c537dd417e4f64cd6e8bd092c7b5f0038a6bf`.

## Sauvegarde et restauration en copies

Avant installation, huit conteneurs et les services applicatifs concernés ont été arrêtés pendant la capture finale, puis remis en route. Un premier helper a échoué en essayant de redémarrer l'ancien ID d'un conteneur AutoRemove recréé par son unité systemd ; cet échec est conservé. Le helper corrigé utilise cette unité et les IDs exacts des sept autres conteneurs ; son reçu final est passant.

Capture finale `20261116T191041Z` : archive de 47 874 422 octets, SHA256 `e15894f4acf413b00fa90189540f4a752f3eb8e1b203e2501bef11fbb109a134`. Copie Mac AES-256-GCM : 47 874 466 octets, SHA256 `3dc94fd05716457f32f6754890234d7b6a373e4405071e6267480ff745f3e243`. Le runtime Varro déployé a également sa copie chiffrée distincte ; aucune restauration d'un service externe Supabase n'est revendiquée.

Essais réels : 66 fichiers SQLite restaurés/lus avec intégrité et FK vérifiées ; trois dumps PostgreSQL, incluant les bases standard, restaurés et 13 tables lues dans un conteneur isolé sans réseau, ports ni montage de l'hôte ; 5 746 fichiers réguliers de configuration/sources restaurés et 172 liens inventoriés ; runtime Varro restauré séparément. Le conteneur de test et les copies locales temporaires en clair ont été retirés après vérification. Ce n'est ni un test de restauration complète amorçable de VM ni une garantie sans perte des écritures postérieures.

Conservation privée : `~/auren-private-backups/ovh-vps-491c685f/20261116T191041Z/`, guide `LIRE_AVANT_RESTAURATION.md` et clé dédiée dans le dossier privé `keys` distinct. Aucun secret, contenu de base ou configuration privée n'est publié ici. Plafond de 8 Gio et plancher de 20 Gio libres respectés pendant l'acquisition. Les sauvegardes précédentes restent conservées.

## État système réellement obtenu

| Élément | Résultat observé |
|---|---|
| OS | Ubuntu 25.04 → **Ubuntu 26.04.1 LTS** |
| Noyau chargé après les deux boots | `7.0.0-43-generic` |
| Docker | `29.1.3-0ubuntu4.1` |
| nginx | `1.28.3-2ubuntu1.12` |
| OpenSSH | `1:10.2p1-2ubuntu3.8` ; socket SSH actif |
| Python système | 3.14.3 |
| Runtime web conservé | Python 3.13.3 ; imports natifs et `pip check` passants |
| PostgreSQL | seul cluster `17/main` en ligne ; paquets 18 installés, aucune migration de cluster |
| Node / Tailscale | 24.22.3 / 1.104.7 |
| APT final | index rafraîchis ; simulation : 0 upgrade, ajout, retrait ou paquet différé |
| Espace racine / boot | environ 42 936 Mio / 643 Mio libres au contrôle |

Le lien Python du seul venv web est fixé vers le binaire 3.13 déjà présent, après contrôle d'identité de l'ancien binaire. Aucun remplacement du Python système ou upgrade des dépendances applicatives. Les invites de migration automatique PostgreSQL 17→18 sont refusées ; `auto_upgrade=false`. Zéro divergence de version de collation rapportée par la requête de contrôle. La purge proposée de 42 paquets obsolètes est refusée, notamment pour conserver Python 3.13 et ses bibliothèques. Ces anciennes versions conservées ne bénéficient pas, de ce seul fait, de la maintenance des dépôts Ubuntu 26.

NodeSource et Tailscale sont réactivés avec leurs sources signées compatibles et leurs clés existantes. Aucun script d'installation tiers ou nouvelle clé de confiance. Le code web demeure `90da8461803e87897c3d8f48627c4b704b3cfcd6`, avec son fichier non suivi préexistant ; aucun backend MVP ne remplace le site.

## Incidents et corrections bornées

1. **SSH pendant l'installation :** l'opérateur exécute via KVM `sudo systemctl daemon-reload && sudo systemctl restart ssh.socket`, sans erreur. La connexion reprend avec vérification stricte de la clé d'hôte.
2. **nginx au premier boot :** Tailscale occupe son adresse privée sur 443 avant les écoutes wildcard nginx. Quatorze directives TLS de huit configurations actives sont remplacées par des écoutes explicites sur les adresses publiques attribuées et loopback IPv4/IPv6. Options TLS, certificats, noms, upstreams et HTTP 80 conservés ; aucune configuration Tailscale ou ACL changée. Originaux et empreintes sauvegardés, remplacement atomique et `nginx -t` passants. Revue indépendante du diff réel : aucun Critical/Important. Le second boot vérifie leur reprise automatique conjointe.
3. **GRUB au second boot :** le service de comptabilisation `grub2-common` échoue une fois avec `invalid environment block`. Après passage du service fournisseur `grub-initrd-fallback`, le bloc courant est valide ; copie conservée puis relance de `grub2-common` réussie, statut 0. Aucune recréation manuelle de grubenv, modification du choix de boot ou troisième reboot. La non-récurrence de cet incident sur d'autres boots n'est pas prouvée.

Les avertissements nginx de syntaxe HTTP/2 obsolète restent non bloquants. Aucun refactoring général des vhosts.

## Contrôles après redémarrage

Deux redémarrages réels : premier boot vers 21:30 UTC, puis second boot vers 21:50 UTC. Identités de boot conservées dans les reçus privés. Après le second boot :

- Les huit conteneurs initiaux tournent, sept avec healthcheck healthy et un sans healthcheck. Images, environnement, montages et publications de ports comparés à la capture antérieure : identiques ; aucun conteneur supplémentaire.
- workout, Varro, service de revue Caracalla, nginx, Docker, PostgreSQL 17 et socket SSH actifs ; Tailscale actif séparément. Audit dpkg vide. Après la relance GRUB, zéro unité en échec au relevé final.
- **Sept racines HTTPS répondent 200 avec TLS vérifié**, au 16 novembre à 21:52:59 UTC : spignos.com, varronotes.com, maltin.io (redirection app), app.maltin.io, preview.maltin.io, caracalla.co et review.caracalla.co. Les deux timeouts Maltin antérieurs à la correction sont conservés. Ces GET ne prouvent pas les parcours authentifiés complets.
- Serve Tailscale privé : 443 répond 200, 8443 répond 404 avec TLS vérifié ; le 404 prouve ici le transport de la racine API, pas un parcours métier.
- SQLite web : intégrité OK, zéro erreur FK, 35 tables ; lecture seule, aucune migration applicative. Unités workout et trois unités de backup comparées par empreinte : inchangées.

**Défaut historique non corrigé :** `workout-backup.service` pointe toujours sur `/srv/workout`, absent. L'absence d'unité failed après reboot ne prouve pas que son prochain timer réussira. Les copies complètes de maintenance ne remplacent pas sa réparation future. Aucun backup automatique récurrent sain n'est déclaré.

## Preuves et suite REL03

Dossier privé : `~/auren-review/rel03-ops-mvp-rc01-20261116/maintenance-20261116T185539Z/`. Il conserve autorisations, préflight, copies/restaurations, logs d'installation, incidents, deltas nginx, dépôts, deux boots, postflight et HTTPS. Les fichiers bruts `*.private.json` peuvent contenir de la configuration sensible : ne pas les joindre à une PR. Logs fournisseur conservés sur le VPS sous `/var/log/dist-upgrade` et copies/configurations root privées sous `/var/backups/auren-host-maintenance`.

**Le blocage OS de la qualification est levé ; le banc QA n'est pas déployé.** Restent : réparation bornée du backup récurrent, observateur/compte QA, garde d'image et environnement GitHub protégé, secrets/base synthétiques isolés, API/SCI/schema réellement qualifiés, autorisation du diff opérationnel puis DNS/TLS QA, manifeste binaire/runtime/signature, build consolidé et smokes installés. `qa.spignos.com` n'est pas présenté comme endpoint disponible. Les gates DATA et d'acceptation physique ne sont pas fermées par cette maintenance.

Ce changement du dépôt est documentaire uniquement. Ses checks/PR/CI et reçu de merge sont consignés dans la passation de livraison ; aucun ancien test produit n'est renommé test du système maintenu.
