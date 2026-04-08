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

## 5. Mise à jour

```bash
sudo -u workout bash -c '
  cd /srv/workout &&
  git pull &&
  .venv/bin/pip install -r requirements.txt &&
  .venv/bin/python -m scripts.seed_db
' && sudo systemctl restart workout
```

## 6. Sauvegardes SQLite

Ajouter à la crontab de `workout` :

```
0 3 * * * sqlite3 /srv/workout/var/workout.db ".backup '/srv/workout/var/workout-$(date +\%F).db'"
```

## 7. Migration future vers PostgreSQL

Seule `DATABASE_URL` change. Étapes prévues (Sprint ultérieur) :

1. `sudo apt install postgresql`
2. créer `workout` user + db
3. `DATABASE_URL=postgresql+psycopg://workout:xxx@localhost/workout`
4. `alembic upgrade head` (quand Alembic sera branché)
5. migration des données via script ad hoc
