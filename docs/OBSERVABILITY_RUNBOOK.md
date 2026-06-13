# Observability Runbook — Sb_26.3

**Audience :** opérateur SPIGNOS (humain de garde).
**Créé :** 2026-06-13 (sprint Sb_26.3).
**Statut :** verrouille la base d'observabilité minimale. Aucune stack Prometheus/Grafana — juste les signaux nécessaires pour répondre vite.

---

## 1. Vue d'ensemble — quel signal pour quoi

| Signal | Surface | Qui le consomme | Latence cible |
|---|---|---|---|
| `/healthz` | HTTP GET (public, non auth) | UptimeRobot (cf. §3) | < 1s |
| `/healthz/strict` | HTTP GET (public — leak surface minime) | Opérateur, cron VPS | < 2s |
| `var/deploy_state.json` | Fichier local | `/healthz/strict`, `prod_state_report.py` | instant |
| `scripts/prod_state_report.py` | CLI sur VPS | Opérateur en cas d'alerte | < 5s |
| Sentry (opt-in) | SDK in-app via `SENTRY_DSN` | Sentry.io UI | temps réel |
| Discord webhook (opt-in) | CLI manuel ou hook deploy | Discord channel | temps réel |

## 2. Sentry — opt-in via env

### 2.1 Activation

Sentry est **strictement opt-in**. Si `SENTRY_DSN` est vide ou absent, aucun appel sortant n'est fait, aucun `sentry-sdk` requis.

Sur le VPS, ajouter à `/opt/workout-session-tracking/.env` :

```bash
SENTRY_DSN=https://<public_key>@oXXXXX.ingest.sentry.io/<project_id>
SENTRY_ENVIRONMENT=prod
SENTRY_TRACES_SAMPLE_RATE=0.0   # 0 = errors only, no perf data
```

Puis :

```bash
sudo -u ubuntu /opt/workout-session-tracking/.venv/bin/pip install sentry-sdk
sudo systemctl restart workout
```

### 2.2 Sécurité

* Le DSN n'est **pas** un secret au sens strict (il identifie le projet, pas une auth), mais ne pas le commiter par hygiène — il vit dans `.env` qui est dans `.gitignore`.
* `send_default_pii=False` est forcé (`app/main.py:_init_sentry_if_enabled`). Sentry ne reçoit jamais user-agent + IP par défaut.
* `traces_sample_rate=0.0` par défaut. Les traces de perf ne sont **pas** envoyées tant qu'on ne le décide pas explicitement.

### 2.3 Désactiver

```bash
# Sur le VPS :
sed -i 's/^SENTRY_DSN=.*/SENTRY_DSN=/' /opt/workout-session-tracking/.env
sudo systemctl restart workout
```

Vérif : `/healthz` renvoie 200 (Sentry off n'impacte pas l'app).

## 3. Uptime externe — UptimeRobot (gratuit)

### 3.1 Configuration recommandée

| Monitor | URL | Type | Fréquence | Seuil | Notif |
|---|---|---|---|---|---|
| Liveness | `https://<your-host>/healthz` | HTTP(s) Keyword | 5 min | `"status":"ok"` absent → DOWN | email + Discord (cf. §4) |
| Strict | `https://<your-host>/healthz/strict` | HTTP(s) Status | 15 min | code ≠ 200 → DOWN | email |

UptimeRobot gratuit accepte ~50 monitors en 5 min. La paire liveness/strict suffit pour V1.

### 3.2 Réaction en cas de DOWN

```bash
# 1. SSH sur le VPS
ssh ubuntu@<vps>

# 2. Snapshot état complet (1 commande, JSON sans secrets)
python3 /opt/workout-session-tracking/scripts/prod_state_report.py \
    --healthz http://127.0.0.1:8000/healthz/strict \
    --pretty

# 3. Si /healthz local renvoie aussi un erreur :
sudo systemctl status workout
sudo journalctl -u workout -n 50 --no-pager

# 4. Si le service est down :
sudo systemctl restart workout
# Attendre 5s, retest :
curl -s http://127.0.0.1:8000/healthz

# 5. Si le service tourne mais /healthz renvoie 5xx :
#    → la DB est probablement le problème (cf. §6)

# 6. Si nginx est cassé (502 côté UptimeRobot mais service tourne) :
sudo nginx -t
sudo systemctl status nginx
sudo systemctl restart nginx
```

### 3.3 Quand escalader

* `/healthz` down > 10 min ET restart service ne corrige pas → rollback (cf. `docs/MIGRATION_HARDENING.md §5`)
* Disque < 5% libre (visible dans `/healthz/strict` payload `disk.free_percent`) → free up immédiatement, sinon SQLite WAL va corrompre
* Backup absent > 48h (visible dans `prod_state_report.py` `backup.age_seconds`) → cron de backup cassé, investiguer

## 4. Alerting Discord — opt-in

### 4.1 Activation

Créer un webhook Discord (Server Settings → Integrations → Webhooks → New). Stocker l'URL dans `/opt/workout-session-tracking/.env` du VPS :

```bash
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/<id>/<token>
```

### 4.2 Usage manuel

```bash
DISCORD_WEBHOOK_URL=$(grep DISCORD_WEBHOOK_URL /opt/workout-session-tracking/.env | cut -d= -f2-) \
  python3 /opt/workout-session-tracking/scripts/alert_discord.py \
    --severity error \
    --title "Prod /healthz DOWN" \
    --message "$(curl -sS http://127.0.0.1:8000/healthz/strict | head -c 500)"
```

### 4.3 Comportement si env absent

```bash
python3 scripts/alert_discord.py --title x --message y
# → [alert_discord] DISCORD_WEBHOOK_URL unset — alerter disabled, no-op
# → exit 0
```

Pas de network call, pas d'erreur. C'est le contrat "opt-in" : zero side effect si non configuré.

### 4.4 Dry-run (test du payload sans POST)

```bash
python3 scripts/alert_discord.py --dry-run \
  --severity warning --title "test" --message "preview the embed"
```

Affiche le JSON envoyé à Discord sans l'envoyer.

## 5. Deploy state — `var/deploy_state.json`

### 5.1 Génération automatique

À la fin de chaque deploy réussi (`scripts/deploy_prod.sh` §"Recording deploy state"), un fichier `<APP_DIR>/var/deploy_state.json` est écrit :

```json
{
  "sha": "0123456789abcdef0123456789abcdef01234567",
  "deployed_at": "2026-06-13T10:24:53.123456+00:00",
  "service": "workout",
  "app_dir": "/opt/workout-session-tracking",
  "health_at_deploy": "200"
}
```

### 5.2 Lecture

Le fichier est lu par :
* `/healthz/strict` → champ `deploy` du JSON renvoyé
* `scripts/prod_state_report.py` → champ `deploy` du rapport

Schéma stable : un nouveau champ peut être ajouté, jamais retiré ni renommé sans amendment Sx_26.

### 5.3 Tolérance aux erreurs

Le fichier absent, mal formé, ou avec des champs inattendus ne casse **jamais** `/healthz/strict` — il dégrade simplement à `deploy.present = false`. C'est le pattern "best-effort observability" : l'app continue de servir même si la couche meta est cassée.

## 6. Healthcheck strict — sous-payloads

`/healthz/strict` renvoie un JSON avec :

| Champ | Type | Sens | Impact sur le code HTTP |
|---|---|---|---|
| `db.ok` | bool | `SELECT 1` réussi ? | **503 si false** |
| `backup_dir.exists` | bool | `var/backups` existe ? | informatif |
| `backup.present` | bool | au moins 1 backup JSON ? | informatif |
| `backup.valid` | bool/null | dernier backup intègre ? | **503 si present + invalid** |
| `backup.age_seconds` | int | âge du dernier backup | informatif |
| `deploy.present` | bool | `deploy_state.json` lisible ? | informatif |
| `deploy.sha` / `short_sha` | str | SHA déployé | informatif |
| `deploy.age_seconds` | int | secondes depuis le deploy | informatif |
| `disk.free_percent` | float | espace libre % | informatif |

**Règle** : seuls `db.ok` et `backup.valid` peuvent rendre le code HTTP 503. Tout le reste est informationnel — `/healthz/strict` ne flap pas pour un fichier non lu.

## 7. Procédure incident-type

### 7.1 « UptimeRobot dit que `/healthz` est DOWN »

1. `prod_state_report.py --pretty --healthz http://127.0.0.1:8000/healthz/strict`
2. Si `deploy.age_seconds < 300` → un deploy vient d'être fait, probablement service en cours de boot, attendre 1 min puis retest
3. Si `disk.free_percent < 5` → libérer (logs, anciens backups au-delà retention) puis retest
4. Sinon `systemctl status workout && journalctl -u workout -n 50`
5. Si toujours down → rollback (`docs/MIGRATION_HARDENING.md §5`)

### 7.2 « Erreur 500 reportée par utilisateur »

1. Sentry activé ? → ouvrir l'event dans Sentry, reproduire avec le contexte fourni
2. Sentry désactivé ? → `journalctl -u workout -n 200 | grep -i error` sur le VPS, isoler la trace
3. Pour activer Sentry ad hoc : cf. §2.1

### 7.3 « Backup ne se fait plus »

1. `prod_state_report.py` → `backup.age_seconds`
2. Si > 48h : `crontab -u ubuntu -l` pour confirmer la cron de backup
3. Logs : `journalctl --since="48 hours ago" | grep -i backup`

## 8. Ce qui n'est PAS dans Sb_26.3

| Item | Reporté à |
|---|---|
| Métriques temps réel (Prometheus / Grafana) | hors scope, peut-être post-Sx_26 |
| Logs structurés JSON | Sb_27+ |
| Distributed tracing | hors scope produit V1 |
| Auto-rollback sur /healthz down | Sb_26.next (risque > bénéfice en V1) |
| Sentry release tracking automatique | Sb_26.next (lier release à deploy_state SHA) |
| Status page publique | hors scope |

## 9. Contrats durs (verrouillés par Sb_26.3)

| Contrat | Mécanisme |
|---|---|
| Sentry doit pouvoir être désactivé sans redéploiement (juste `.env` + restart) | `_init_sentry_if_enabled` ne s'exécute que si `SENTRY_DSN` non vide |
| Aucun token / webhook / secret dans le code ou les JSON exposés | review humaine + test `test_healthz_strict_does_not_expose_secrets` + `test_prod_state_report_emits_json_no_secrets` |
| `/healthz/strict` ne flap pas pour un fichier manquant | `_read_deploy_state` + `_disk_usage` retournent toujours un dict, jamais raise |
| Discord webhook opt-in : pas de POST sans env var | test `test_alert_discord_disabled_when_env_unset` |
| Le deploy ne se déclenche jamais automatiquement | `.github/workflows/deploy-production.yml` reste sur `workflow_dispatch` |
