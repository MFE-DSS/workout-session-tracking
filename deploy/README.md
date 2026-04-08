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

Avant que l'app n'ait sa propre auth, mettre un mot de passe basic
au niveau nginx.

```bash
sudo apt install -y apache2-utils
sudo htpasswd -c /etc/nginx/workout.htpasswd moi
```

Dans `/etc/nginx/sites-available/workout`, à l'intérieur du bloc
`server { ... }` :

```nginx
auth_basic "Workout";
auth_basic_user_file /etc/nginx/workout.htpasswd;
location = /healthz {
    auth_basic off;          # laisser le probe public
    proxy_pass http://127.0.0.1:8000;
}
```

Recharger nginx : `sudo nginx -t && sudo systemctl reload nginx`.

Alternative : allowlist IP via `allow` / `deny` si IP fixe.
Une auth applicative (cookie session FastAPI) viendra dans un sprint
ultérieur si nécessaire.

## 6. Mise à jour de l'application

```bash
sudo -u workout bash -c '
  cd /srv/workout &&
  git pull &&
  .venv/bin/pip install -r requirements.txt &&
  .venv/bin/alembic upgrade head &&
  .venv/bin/python -m scripts.seed_db
' && sudo systemctl restart workout
```

L'étape `alembic upgrade head` est obligatoire après chaque `git pull`
si une nouvelle migration a été ajoutée. Commandes utiles :

```bash
.venv/bin/alembic current          # révision actuelle
.venv/bin/alembic history          # historique
```

## 7. Sauvegardes

Deux mécanismes complémentaires.

### 7.1 Backup binaire SQLite (snapshot rapide)

Crontab de l'utilisateur `workout` (`crontab -e -u workout`) :

```
0 3 * * * sqlite3 /srv/workout/var/workout.db ".backup '/srv/workout/var/workout-$(date +\%F).db'" && find /srv/workout/var -name 'workout-*.db' -mtime +14 -delete
```

Les 14 derniers snapshots sont conservés. Le `.backup` est atomique
et safe pendant que l'app tourne.

### 7.2 Export JSON logique (Sprint 3)

L'app expose `GET /export/sessions.json` qui renvoie tout le journal
(sessions + exercises + sets) en JSON stable, versionné par
`schema_version`.

Dump local (depuis le VPS) :

```bash
sudo -u workout curl -sfL http://127.0.0.1:8000/export/sessions.json \
  -o /srv/workout/var/workout-journal-$(date +%F).json
```

Derrière nginx+basic_auth, en passant le user:pass :

```bash
curl -sfL -u moi:<pwd> https://workout.example.com/export/sessions.json \
  -o workout-journal-$(date +%F).json
```

Ajouter à la crontab si on veut un export quotidien :

```
15 3 * * * curl -sfL http://127.0.0.1:8000/export/sessions.json -o /srv/workout/var/journal-$(date +\%F).json
```

L'export JSON est plus stable que la copie de fichier SQLite
(indépendant du moteur, relisible sans outil SQL). Préférer le
`.backup` pour la restauration rapide et l'export JSON pour
l'archivage long terme.

## 8. Migration future vers PostgreSQL

Seule `DATABASE_URL` change. Étapes prévues :

1. `sudo apt install postgresql`
2. créer `workout` user + db
3. `DATABASE_URL=postgresql+psycopg://workout:xxx@localhost/workout`
4. `alembic upgrade head` sur la nouvelle base
5. import des données via l'export JSON (écrire un petit script
   de load qui refait les INSERT)
