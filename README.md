# Workout Session Tracking

Mobile-first web app pour consigner les séances du split hypertrophie et
suivre la surcharge progressive.

- **V1** : FastAPI SSR + SQLite, déployé sur VPS OVH derrière nginx/HTTPS.
- **Cible** : téléphone, utilisation au gym, UI pouce.
- **Évolution** : PWA, puis migration PostgreSQL.

## Démarrage rapide (local)

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m scripts.seed_db          # seed du catalogue de référence
uvicorn app.main:app --reload
# -> http://localhost:8000
```

## Tests

```bash
pip install pytest httpx
pytest -q
```

## Structure

```
app/
  main.py            FastAPI entrypoint + lifespan seed
  config.py          Settings (env driven)
  database.py        SQLAlchemy engine + Base + session
  models/
    catalog.py       Split, Exercise, RepRange, ReferenceDoc
    session.py       WorkoutSession, SetLog (skeleton Sprint 1)
  routers/
    pages.py         SSR (/, /jours/{1..7})
    health.py        /healthz
  services/seed.py   Idempotent seed du catalogue
  schemas/catalog.py Pydantic DTOs
  templates/         Jinja2 mobile-first
  static/            CSS + manifest PWA
data/
  reference_split.json  Source de vérité du split
scripts/seed_db.py   CLI de (re)seed
deploy/              systemd unit, nginx sample, guide OVH
tests/               pytest + httpx
```

## Décision d'hébergement V1

- mobile-first, rendu serveur (Jinja2)
- SQLite file persisté dans `./var/` ou `/srv/workout/var/` en prod
- dialect-agnostic (prêt PostgreSQL en changeant `DATABASE_URL`)
- pas d'app native → PWA-ready dès la V1 (manifest + viewport)
- déploiement : cf. `deploy/README.md`
