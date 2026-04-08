# OVH VPS deployment (V1)

Cible : VPS OVH existant, Ubuntu/Debian récent, accès HTTPS depuis le
téléphone. Le service tourne comme un process `uvicorn` unique derrière
nginx.

## 1. Provisioning (une fois)

```bash
sudo adduser --system --group --home /srv/workout workout
sudo apt update && sudo apt install -y python3.11 python3.11-venv nginx certbot python3-certbot-nginx
sudo mkdir -p /srv/workout && sudo chown workout:workout /srv/workout
```

## 2. Déploiement applicatif

```bash
sudo -u workout bash
cd /srv/workout
git clone https://github.com/mfe-dss/workout-session-tracking.git .
python3.11 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env
# éditer .env (APP_SECRET_KEY, APP_BASE_URL, DATABASE_URL)
mkdir -p var
# Schema : Alembic est la source de vérité depuis Sprint 2.
.venv/bin/alembic upgrade head
.venv/bin/python -m scripts.seed_db
exit
```

## 3. systemd

```bash
sudo cp /srv/workout/deploy/workout.service /etc/systemd/system/workout.service
sudo systemctl daemon-reload
sudo systemctl enable --now workout
sudo systemctl status workout
```

## 4. nginx + HTTPS

```bash
sudo cp /srv/workout/deploy/nginx.conf.example /etc/nginx/sites-available/workout
# remplacer workout.example.com par votre domaine
sudo ln -s /etc/nginx/sites-available/workout /etc/nginx/sites-enabled/workout
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d workout.example.com
```

## 5. Protection minimale V1 (nginx basic_auth)

L'application n'a **pas** d'auth interne en V1 par choix
explicite. Toute la protection se fait au niveau du reverse
proxy nginx, dont la configuration recommandée et opérationnelle
est ici.

### 5.1 Créer le fichier de credentials

```bash
sudo apt install -y apache2-utils
sudo htpasswd -c /etc/nginx/workout.htpasswd moi
# Ajouter d'autres utilisateurs : sudo htpasswd /etc/nginx/workout.htpasswd autre
```

### 5.2 vhost nginx complet (recommandé)

`/etc/nginx/sites-available/workout` :

```nginx
server {
    listen 443 ssl http2;
    server_name workout.example.com;

    ssl_certificate     /etc/letsencrypt/live/workout.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/workout.example.com/privkey.pem;

    # Auth par défaut sur tout le vhost.
    auth_basic           "Workout";
    auth_basic_user_file /etc/nginx/workout.htpasswd;

    # Sondes d'uptime publiques (Pingdom, UptimeRobot, etc.)
    location = /healthz {
        auth_basic off;
        proxy_pass http://127.0.0.1:8000;
    }

    # Statics : pas de secrets, on les rend publics pour économiser
    # un round-trip d'auth sur chaque image / CSS.
    location /static/ {
        auth_basic off;
        alias /srv/workout/app/static/;
        expires 7d;
        access_log off;
    }

    # Tout le reste passe par auth_basic.
    location / {
        proxy_pass         http://127.0.0.1:8000;
        proxy_set_header   Host              $host;
        proxy_set_header   X-Real-IP         $remote_addr;
        proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo nginx -t && sudo systemctl reload nginx
```

### 5.3 Que voit le monde public ?

| Route                             | Auth basic | Pourquoi                                         |
|-----------------------------------|------------|--------------------------------------------------|
| `/healthz`                        | NON        | Sondes d'uptime, contenu inoffensif.             |
| `/static/*`                       | NON        | CSS, manifest, icône, aucun secret.              |
| `/`                               | OUI        | Page d'accueil, expose le statut de la session.  |
| `/library`, `/library/{slug}`     | OUI        | Catalogue privé.                                 |
| `/sessions`, `/sessions/{id}`     | OUI        | Données de séance.                               |
| `/history`, `/progress`           | OUI        | KPI personnels.                                  |
| `/exercise-history/...`           | OUI        | Données historiques.                             |
| `/rules`                          | OUI        | Mineur, gardé sous auth pour la cohérence.       |
| `/export`                         | OUI        | **Sensible : page de téléchargement du journal.**|
| `/export/sessions.json`           | OUI        | **Sensible : journal complet.**                  |
| `/export/sessions.csv`            | OUI        | **Sensible : journal complet.**                  |

À ne JAMAIS exposer publiquement sans auth :
- toutes les routes `/export/*`
- toutes les routes `/sessions/*`
- `/history`, `/progress`, `/exercise-history/*`

### 5.4 Alternative : IP allowlist

Si vous avez une IP fixe (VPN, box ADSL static), vous pouvez
remplacer `auth_basic` par :

```nginx
allow 203.0.113.42;     # votre IP
deny all;
```

ou les combiner (`satisfy any`) pour autoriser soit l'IP soit
l'auth basic.

### 5.5 Pas d'auth applicative en V1

Aucun cookie de session, aucune table `users`, aucun mot de
passe stocké côté app. La trajectoire reste : nginx fait
l'auth, l'app est mono-utilisateur. Si un jour le besoin
d'utilisateurs multiples apparaît, on introduit une couche
auth applicative dans un sprint dédié.

## 6. Mise à jour de l'application

Workflow recommandé après un `git pull` :

```bash
sudo -u workout bash -c '
  cd /srv/workout &&
  git pull &&
  .venv/bin/pip install -r requirements.txt &&
  .venv/bin/python -m scripts.check_alembic_drift &&
  .venv/bin/alembic upgrade head &&
  .venv/bin/python -m scripts.seed_db
' && sudo systemctl restart workout
```

Étapes en détail :

1. `git pull` : récupère le code.
2. `pip install -r requirements.txt` : aligne les dépendances.
3. `scripts.check_alembic_drift` (Sprint 4) : vérifie qu'aucun
   modèle ORM n'a divergé du dernier `alembic head` sans qu'une
   migration ait été générée. Sort en code 1 si drift, dans ce
   cas STOP : il manque une révision Alembic à committer.
4. `alembic upgrade head` : applique les migrations en attente.
   C'est l'étape officielle de migration depuis Sprint 2.
5. `scripts.seed_db` : reseed idempotent du catalogue + règles.
6. `systemctl restart workout` : recharge l'app.

Commandes utiles :

```bash
.venv/bin/alembic current               # révision actuelle
.venv/bin/alembic history                # historique
.venv/bin/python -m scripts.check_alembic_drift   # garde-fou drift
```

## 7. Sauvegardes

Trois formats complémentaires, chacun avec un usage clair :

| Format               | Source             | Usage                                |
|----------------------|--------------------|--------------------------------------|
| `.backup` SQLite     | sqlite3 .backup    | Restauration en place, la plus rapide|
| Dump JSON            | export_builder     | Archivage long terme, format stable  |
| Dump CSV             | export_builder     | Analyse ad hoc dans un tableur       |

### 7.1 Snapshot SQLite (la base)

Crontab de l'utilisateur `workout` (`crontab -e -u workout`) :

```
0 3 * * * sqlite3 /srv/workout/var/workout.db ".backup '/srv/workout/var/workout-$(date +\%F).db'" && find /srv/workout/var -maxdepth 1 -name 'workout-*.db' -mtime +14 -delete
```

Les 14 derniers snapshots sont conservés. Le `.backup` SQLite est
atomique et safe pendant que l'app tourne.

### 7.2 Sauvegardes planifiées JSON + CSV (Sprint 6)

Le script `scripts/backup_sessions.py` produit un dump JSON et un
dump CSV en lisant directement la base via SQLAlchemy (aucun
appel HTTP requis). Il prune ensuite les fichiers plus anciens
que la rétention configurée.

**Variables d'environnement :**

| Var                       | Défaut                          | Rôle                            |
|---------------------------|---------------------------------|---------------------------------|
| `BACKUP_DIR`              | `<repo>/var/backups`            | Dossier de sortie               |
| `BACKUP_RETENTION_DAYS`   | `30`                            | 0 = garder indéfiniment         |

**Test manuel :**

```bash
sudo -u workout BACKUP_DIR=/srv/workout/var/backups \
  /srv/workout/.venv/bin/python -m scripts.backup_sessions
# -> backup_sessions: wrote sessions-YYYYMMDD_HHMM.json (1234 B) and ...

sudo -u workout BACKUP_DIR=/srv/workout/var/backups \
  /srv/workout/.venv/bin/python -m scripts.list_backups
```

**Option A : systemd timer (recommandé)**

```bash
sudo cp /srv/workout/deploy/workout-backup.service /etc/systemd/system/
sudo cp /srv/workout/deploy/workout-backup.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now workout-backup.timer
sudo systemctl list-timers | grep workout-backup
```

Le timer tire le service tous les jours à 03:30 UTC. Si la
machine était éteinte (`Persistent=true`), le backup s'exécute
au démarrage suivant.

**Option B : cron**

```
30 3 * * * BACKUP_DIR=/srv/workout/var/backups BACKUP_RETENTION_DAYS=30 /srv/workout/.venv/bin/python -m scripts.backup_sessions >> /srv/workout/var/backup.log 2>&1
```

### 7.3 Vérification à la volée

L'utilisateur dispose de deux signaux :

1. La page `/export` montre le **dernier fichier de backup
   détecté** dans `BACKUP_DIR` (nom, taille, modifié-le). Si
   aucun fichier n'est trouvé, un message explicite invite à
   activer le timer.
2. La commande `python -m scripts.list_backups` liste tous
   les fichiers du dossier, du plus ancien au plus récent.

## 8. Restauration

Trois scénarios. Choisissez selon le contexte.

### 8.1 Scénario A : rollback d'urgence (recommandé V1)

Vous avez accidentellement écrasé une session, ou la base est
corrompue. Le snapshot SQLite est la voie la plus rapide.

```bash
sudo systemctl stop workout
sudo cp /srv/workout/var/workout-2026-04-08.db /srv/workout/var/workout.db
sudo chown workout:workout /srv/workout/var/workout.db
sudo systemctl start workout
```

Vérifier : `curl http://127.0.0.1:8000/healthz`.

### 8.2 Scénario B : machine vide / migration de VPS

Vous repartez de zéro sur une nouvelle machine.

```bash
# 1. Provisionner comme aux sections 1..4
# 2. Schéma vide via Alembic
sudo -u workout /srv/workout/.venv/bin/alembic upgrade head
# 3. Restaurer le snapshot SQLite si vous l'avez recopié
sudo cp workout-2026-04-08.db /srv/workout/var/workout.db
sudo chown workout:workout /srv/workout/var/workout.db
sudo systemctl start workout
```

Si vous n'avez QUE le dump JSON (pas le SQLite), V1 ne fournit
pas encore d'endpoint d'import. Le JSON reste la **source de
vérité d'archivage** : un script de chargement ad hoc peut être
écrit en quelques lignes (futur Sprint).

### 8.3 Scénario C : analyse ad hoc dans un tableur

Le dump CSV est plat, une ligne par set, prêt à être ouvert dans
Excel / Numbers / Pandas. Aucune restauration nécessaire — c'est
une **vue analytique**, pas une sauvegarde restorable.

### 8.4 Recommandation V1

- **Quotidien** : timer `workout-backup.timer` (JSON + CSV) +
  cron snapshot SQLite. 30 jours de rétention.
- **Restauration** : snapshot SQLite (Scénario A) en priorité.
- **Archivage long terme** : commiter les dumps JSON dans un
  petit repo git privé (un dump par jour, taille ~ quelques
  centaines de Ko).
- **Analyse** : ouvrir le dernier CSV dans un tableur.

## 8. Migration future vers PostgreSQL

Seule `DATABASE_URL` change. Étapes prévues :

1. `sudo apt install postgresql`
2. créer `workout` user + db
3. `DATABASE_URL=postgresql+psycopg://workout:xxx@localhost/workout`
4. `alembic upgrade head` sur la nouvelle base
5. import des données via l'export JSON (écrire un petit script
   de load qui refait les INSERT)
