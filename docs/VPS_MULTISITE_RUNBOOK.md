# VPS Multi-Sites Runbook — `vps-491c685f.vps.ovh.net` (51.91.79.44)

**Audience :** Martin (admin VPS) + Claude (assistant ops).
**Créé :** 2026-05-31 après l'incident d'unification.
**Dernière mise à jour :** 2026-05-31.

Ce runbook **fige** l'architecture multi-sites du VPS pour éviter les conflits récurrents sur les ports 80/443 et permettre l'ajout serein d'un futur site.

---

## 1. Architecture

```
                  Internet :80 / :443
                          │
                  ┌───────▼────────┐
                  │   host nginx   │  TLS termination + dispatch par server_name
                  │  (systemd)     │  certbot pour les 3 certs
                  └──┬──┬──┬───┬───┘
                     │  │  │   │
   spignos.com ──────┘  │  │   └────── caracalla.co + www.
                        │  └─────────── varronotes.com + www.
                        ▼
                ┌───────┴───────────────────────────────────┐
                ▼            ▼              ▼               ▼
         127.0.0.1:8000  127.0.0.1:3000  127.0.0.1:3001  127.0.0.1:5000
          SPIGNOS         varronotes      caracalla_ui    caracalla_api
          uvicorn         Next.js         Docker          Docker
          systemd         systemd         compose         compose
          workout.service varro.service   etoro-portfolio-agent-1
```

**Règle d'or unique** : aucune app ne bind `0.0.0.0:80` ni `0.0.0.0:443`. Seul **host nginx** écoute publiquement. Toute app utilisateur écoute sur `127.0.0.1:<port>`.

## 2. Inventaire de chaque service

| Domaine | App | Type | Port localhost | Service systemd / Docker | Vhost nginx |
|---|---|---|---|---|---|
| `spignos.com` | SPIGNOS (FastAPI) | uvicorn | `127.0.0.1:8000` | `workout.service` | `/etc/nginx/sites-enabled/spignos.com` |
| `varronotes.com` | varronotes (Next.js) | Next standalone | `127.0.0.1:3000` | `varro.service` | `/etc/nginx/sites-enabled/varronotes.com` |
| `caracalla.co` | caracalla UI (Next.js) | Docker container | `127.0.0.1:3001` | `caracalla_ui` (compose `frontend`) | `/etc/nginx/sites-enabled/caracalla.co` (location `/`) |
| `caracalla.co/api/` | caracalla API (Flask/gunicorn) | Docker container | `127.0.0.1:5000` | `caracalla_api` (compose `backend`) | idem (location `/api/`) |

**Certificats Let's Encrypt** (auto-renewal via `certbot.timer`) :
- `caracalla.co` + `www.caracalla.co`
- `spignos.com` + `www.spignos.com`
- `varronotes.com` + `www.varronotes.com`

Stockage : `/etc/letsencrypt/live/<domain>/`. Renouvellement automatique 2×/jour.

## 3. Outil de diagnostic — `vps-preflight.sh`

```bash
sudo /usr/local/bin/vps-preflight.sh
```

Affiche en 3 secondes :
- Qui écoute sur 80/443 (doit être nginx host uniquement)
- Qui écoute sur les ports localhost attendus (3000/3001/5000/8000)
- État des services systemd attendus (`nginx`, `workout`, `varro`, `docker`)
- Smoke HTTPS sur les 3 domaines
- Dates d'expiration des certs

À lancer après toute manipulation infra, et à automatiser (cron 5min) si tu veux du monitoring.

## 4. Procédure pour ajouter un 4ᵉ site

Cible : un nouveau site `monsite.com` qui écoute sur `127.0.0.1:9000`.

### Étape 1 — Faire écouter l'app sur localhost uniquement

| App type | Action |
|---|---|
| systemd | `ExecStart=...--host 127.0.0.1 --port 9000` |
| Docker | `ports: ["127.0.0.1:9000:<container_port>"]` |
| Aucun port public, JAMAIS | ❌ pas de `0.0.0.0:80` ni `:443` |

### Étape 2 — Créer le vhost nginx

```bash
sudo tee /etc/nginx/sites-available/monsite.com > /dev/null <<'EOF'
server {
    listen 80;
    listen [::]:80;
    server_name monsite.com www.monsite.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    listen [::]:443 ssl;
    http2 on;
    server_name monsite.com www.monsite.com;

    ssl_certificate /etc/letsencrypt/live/monsite.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/monsite.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    access_log /var/log/nginx/monsite.access.log;
    error_log  /var/log/nginx/monsite.error.log;

    location / {
        proxy_pass http://127.0.0.1:9000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Connection "";
    }
}
EOF
sudo ln -sf /etc/nginx/sites-available/monsite.com /etc/nginx/sites-enabled/monsite.com
```

### Étape 3 — Obtenir le cert Let's Encrypt

```bash
sudo certbot --nginx -d monsite.com -d www.monsite.com --non-interactive --agree-tos -m martin.paul.feldmann@gmail.com
```

certbot patche le vhost lui-même pour pointer vers `live/monsite.com/`.

### Étape 4 — Tester et activer

```bash
sudo nginx -t
sudo systemctl reload nginx
sudo /usr/local/bin/vps-preflight.sh
```

## 5. Procédures courantes

### Redémarrer un service sans tout casser

```bash
# SPIGNOS
sudo systemctl restart workout.service

# varronotes
sudo systemctl restart varro.service

# caracalla (frontend + backend uniquement, JAMAIS le service `nginx` du compose qui est commenté)
cd /home/ubuntu/etoro-portfolio-agent-1
sudo docker compose -f docker-compose.prod.yml restart frontend backend

# host nginx (TLS + dispatch)
sudo systemctl reload nginx       # à privilégier — pas de coupure
sudo systemctl restart nginx      # uniquement si reload ne suffit pas
```

### Voir les logs en direct

```bash
# SPIGNOS
sudo journalctl -u workout -f

# varronotes
sudo journalctl -u varro -f

# caracalla (UI + API)
sudo docker logs -f caracalla_ui
sudo docker logs -f caracalla_api

# host nginx access + erreur
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/spignos.access.log
sudo tail -f /var/log/nginx/varronotes.access.log
sudo tail -f /var/log/nginx/caracalla.access.log
```

### Forcer le renouvellement d'un cert

```bash
sudo certbot renew --force-renewal --cert-name spignos.com
sudo systemctl reload nginx
```

## 6. Signes qu'un conflit 80/443 est en train de se reproduire

Symptômes typiques :
- `https://<domain>` répond `connection refused` mais le ping et SSH (port 22) fonctionnent
- `sudo systemctl status nginx` montre `Active: inactive (dead)` ou `Active: failed`
- Le `journalctl -u nginx` contient `nginx: [emerg] bind() to 0.0.0.0:80 failed (98: Address already in use)`

Diagnostic en 1 commande :

```bash
sudo /usr/local/bin/vps-preflight.sh
```

Si "Processus écoutant sur 80/443" montre **autre chose que `nginx` host** (docker-proxy, node, etc.), tu as identifié le coupable. Souvent un `docker compose up` qui a réintroduit un container avec `-p 80:80` ou `-p 443:443`.

**Remédiation** :
1. Identifier le container fautif : `sudo docker ps`
2. Le stopper : `sudo docker stop <container>`
3. Corriger son docker-compose (ports `127.0.0.1:<X>:<port_interne>` au lieu de `0.0.0.0:<X>:<port_interne>`)
4. Le recréer : `sudo docker compose up -d --force-recreate <service>`
5. Démarrer host nginx : `sudo systemctl start nginx`
6. Re-pre-flight : `sudo /usr/local/bin/vps-preflight.sh`

## 7. Incident du 2026-05-31 — leçons retenues

**Cause racine** : caracalla utilisait un nginx-en-Docker (`caracalla_proxy`) qui bind publiquement 80/443 dans son `docker-compose.prod.yml`. Quand SPIGNOS et varronotes ont été ajoutés sur le VPS avec leurs propres vhosts nginx host-level, le host nginx n'a jamais pu démarrer car les ports étaient déjà pris par le container Docker. Les 2 nouveaux sites ne fonctionnaient probablement pas en HTTPS depuis leur installation.

**Résolution** :
1. `caracalla_proxy` Docker éliminé (bloc nginx commenté dans `docker-compose.prod.yml`)
2. `caracalla_ui` et `caracalla_api` exposés sur `127.0.0.1:3001` et `127.0.0.1:5000`
3. Host nginx réutilisé comme single gateway pour les 3 domaines
4. `caracalla_scheduler` désactivé (script `scheduler_daemon.py` absent — relic d'une ancienne version)

**Prévention future** :
- Ce runbook documenté
- `vps-preflight.sh` installé pour diagnostic 3-sec
- Convention strictement appliquée : aucune app ne bind 0.0.0.0:80 ou :443

## 8. Backlog (non urgent)

### Monitoring — état actuel et compléments

| Site | Couverture existante | Manque |
|---|---|---|
| `varronotes.com` | Sentry (SDK Next.js → events vers sentry.io). Couvre erreurs runtime client + serveur Next | uptime externe pas couvert par Sentry — si le site est totalement down (nginx HS, app crashée), Sentry ne le voit pas |
| `spignos.com` | bandit/SonarCloud côté CI uniquement | aucun monitoring runtime ni uptime externe |
| `caracalla.co` | aucun connu | aucun monitoring runtime ni uptime externe |

**Recommandation** : ajouter un **monitoring uptime externe** (ping HTTPS toutes les 5 min depuis l'extérieur) pour les 3 sites. Sentry ne le remplace pas — Sentry capture les erreurs **du runtime de l'app**, donc si l'app ne tourne plus du tout, Sentry est silencieux. L'incident du 2026-05-31 n'aurait pas été détecté par Sentry.

Options pertinentes :
- **uptimerobot.com** — gratuit jusqu'à 50 monitors, ping 5 min, notif email/Slack/Telegram. Setup 10 min total pour les 3 sites.
- **cron + curl + ntfy.sh** — entièrement self-hosted, notif push. Plus de boulot mais zéro dépendance externe.

Sentry continue à servir son rôle (capture des exceptions runtime côté varronotes) — ils sont **complémentaires**, pas alternatifs.

### Autres items

- Ajouter une dépendance systemd `After=docker.service` sur nginx, ou inversement, pour éviter les courses au démarrage
- Migrer la base de configs hors `/home/ubuntu` vers `/opt` ou `/srv` (perméable aux suppressions accidentelles du compte ubuntu)
- Documenter les rotations de logs nginx (logrotate config probablement OK par défaut, mais à vérifier)
- Étendre Sentry à SPIGNOS (FastAPI SDK) et caracalla API si l'instrumentation runtime devient utile

## 9. Contacts / accès

- DNS : OVH (gestion des 3 zones)
- VPS : OVH, `ssh ubuntu@51.91.79.44`
- Repos sources :
  - SPIGNOS : `/opt/workout-session-tracking` (git)
  - varronotes : ??? (à compléter)
  - caracalla : `/home/ubuntu/etoro-portfolio-agent-1` (git)
- Certbot mail : martin.paul.feldmann@gmail.com
