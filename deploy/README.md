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

Deux mécanismes complémentaires.

### 7.1 Backup binaire SQLite (snapshot rapide)

Crontab de l'utilisateur `workout` (`crontab -e -u workout`) :

```
0 3 * * * sqlite3 /srv/workout/var/workout.db ".backup '/srv/workout/var/workout-$(date +\%F).db'" && find /srv/workout/var -name 'workout-*.db' -mtime +14 -delete
```

Les 14 derniers snapshots sont conservés. Le `.backup` est atomique
et safe pendant que l'app tourne.

### 7.2 Export logique (Sprint 3 + Sprint 5)

Trois URLs disponibles :

| URL                          | Format     | Usage                                         |
|------------------------------|------------|-----------------------------------------------|
| `GET /export`                | HTML       | Page de résumé + boutons de téléchargement.   |
| `GET /export/sessions.json`  | JSON       | Payload complet versionné (`schema_version`). |
| `GET /export/sessions.csv`   | CSV        | Une ligne par set, prêt à ouvrir dans Excel.  |

Dump local (depuis le VPS, loopback) :

```bash
# JSON
sudo -u workout curl -sfL http://127.0.0.1:8000/export/sessions.json \
  -o /srv/workout/var/journal-$(date +%F).json

# CSV
sudo -u workout curl -sfL http://127.0.0.1:8000/export/sessions.csv \
  -o /srv/workout/var/journal-$(date +%F).csv
```

Derrière nginx+basic_auth, en passant le user:pass :

```bash
curl -sfL -u moi:<pwd> https://workout.example.com/export/sessions.json \
  -o workout-journal-$(date +%F).json
```

Crontab quotidienne (utilisateur `workout`) :

```
15 3 * * * curl -sfL http://127.0.0.1:8000/export/sessions.json -o /srv/workout/var/journal-$(date +\%F).json
20 3 * * * curl -sfL http://127.0.0.1:8000/export/sessions.csv -o /srv/workout/var/journal-$(date +\%F).csv
```

L'export JSON est plus stable que la copie de fichier SQLite
(indépendant du moteur, relisible sans outil SQL). Le CSV est
meilleur pour les outils tiers (Excel, Numbers, Pandas).

Choix recommandé :
- **`.backup` SQLite** pour la restauration rapide en place.
- **JSON** pour l'archivage long terme (round-trip futur).
- **CSV** pour l'analyse ad hoc dans un tableur.

## 8. Migration future vers PostgreSQL

Seule `DATABASE_URL` change. Étapes prévues :

1. `sudo apt install postgresql`
2. créer `workout` user + db
3. `DATABASE_URL=postgresql+psycopg://workout:xxx@localhost/workout`
4. `alembic upgrade head` sur la nouvelle base
5. import des données via l'export JSON (écrire un petit script
   de load qui refait les INSERT)
