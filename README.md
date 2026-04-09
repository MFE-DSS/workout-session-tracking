# Workout Session Tracking

Mobile-first web app pour consigner les séances du programme
d'hypertrophie et suivre la surcharge progressive. Feedback normalisé
prêt pour analytics.

- **V1** : FastAPI SSR + SQLite, VPS OVH derrière nginx/HTTPS.
- **Cible** : téléphone, utilisation au gym, interaction pouce.
- **Évolution** : PWA complète, migration PostgreSQL.

## Docs

- [`docs/PRODUCT_SPEC.md`](docs/PRODUCT_SPEC.md) — product rules
- [`docs/DOMAIN_MODEL.md`](docs/DOMAIN_MODEL.md) — data model
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — tech overview + Alembic workflow
- [`docs/SPRINT_01_REPORT.md`](docs/SPRINT_01_REPORT.md) — Sprint 1 report
- [`docs/SPRINT_02_REPORT.md`](docs/SPRINT_02_REPORT.md) — Sprint 2 report
- [`docs/SPRINT_03_REPORT.md`](docs/SPRINT_03_REPORT.md) — Sprint 3 report
- [`docs/SPRINT_04_REPORT.md`](docs/SPRINT_04_REPORT.md) — Sprint 4 report
- [`docs/SPRINT_05_REPORT.md`](docs/SPRINT_05_REPORT.md) — Sprint 5 report
- [`docs/SPRINT_06_REPORT.md`](docs/SPRINT_06_REPORT.md) — Sprint 6 report
- [`docs/SPRINT_07_REPORT.md`](docs/SPRINT_07_REPORT.md) — Sprint 7 report
- [`deploy/README.md`](deploy/README.md) — OVH deployment + backup + restore guide
- [`deploy/CHECKLISTS.md`](deploy/CHECKLISTS.md) — tickable first-deploy / update / verify / restore checklists

## Règles produit (non négociables)

1. **L'utilisateur choisit librement un template de séance** dans la
   bibliothèque. Les templates ne sont PAS liés à un jour de la semaine.
2. **Une session est horodatée au moment de la saisie**. Le jour de la
   semaine est dérivé de `started_at`, jamais stocké.
3. **Feedback normalisé** : score de réussite, qualité d'exécution,
   concentration, atteinte des reps cibles, sensation muscle cible,
   état global. Les notes libres restent optionnelles et courtes.
4. **Historique résilient** : chaque session snapshot le nom du template
   et des exercices. Un rewrite du catalogue ne casse jamais l'historique.

## Démarrage local

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m scripts.seed_db
uvicorn app.main:app --reload
# → http://localhost:8000
```

## Tests

```bash
pip install pytest httpx
pytest -q                # 12 passed
```

## Structure

```
app/
  main.py                FastAPI entrypoint + lifespan seed
  config.py              Settings env-driven
  database.py            Engine SQLAlchemy, PRAGMA FK SQLite
  enums.py               Vocabulaires normalisés (feedback, kinds)
  templating.py          Jinja2Templates partagé
  models/
    catalog.py           WorkoutTemplate, TemplateExercise, RepTarget,
                         ReferenceDoc
    session.py           WorkoutSession, SessionExercise, SetLog
                         (snapshots + feedback normalisé)
  routers/
    health.py            GET /healthz
    pages.py             SSR: /, /library, /library/{slug},
                         /history, /progress
  schemas/catalog.py     Pydantic DTOs
  services/seed.py       Seed idempotent keyé par version
  templates/             Jinja2 mobile-first
  static/                CSS, manifest PWA, icons
data/
  reference_split.json   Catalogue templates (source de vérité)
scripts/seed_db.py       CLI de (re)seed
deploy/                  systemd + nginx + guide OVH
tests/                   pytest + httpx
```

## Modèle de données (résumé)

```
WorkoutTemplate (slug, name, kind, focus, suggested_label*)
  └── TemplateExercise (code, name, set_scheme, position)
        └── RepTarget (set_index, min_reps, max_reps, technique)

WorkoutSession (started_at, template_id?, template_*_snapshot,
                concentration, global_state, bodyweight_kg, free_note)
  └── SessionExercise (template_exercise_id?, *_snapshot, position,
                       success_score, muscle_sensation, free_note)
        └── SetLog (kind, set_index, weight_kg, reps, technique,
                    execution_quality, reps_target, completed)
```

`*_snapshot` : colonnes denormalisées. Les FK vers le catalogue sont
`ON DELETE SET NULL` → un reseed détruit proprement le catalogue
sans casser l'historique.

`suggested_label` : hint textuel non structurel (jamais utilisé par
la logique applicative).

## Niveaux de saisie figés (V1)

**Session**
- `concentration` (high / medium / low)
- `global_state` (good / flat / fatigued)
- `bodyweight_kg` (float optionnel)
- `free_note` (optionnelle, courte, ≤ 280 car.)

**Exercice**
- `success_score` (100 / 80 / 50)
- `muscle_sensation` (strong / partial / weak)
- `free_note` (optionnelle, courte, ≤ 140 car.)

**Set**
- `weight_kg`
- `reps`
- `execution_quality` (clean / acceptable / degraded)
- `reps_target` (target_hit / target_near / target_missed)
- `technique` (RP / DS / null)
- `completed` (bool)

## Warmup vs work sets (V1, uniforme)

Chaque `SetLog` porte un champ `kind` ∈ `{warmup, work}`. Les set
indexes sont numérotés séparément : warmup 1..N, work 1..M. Pas de
table dédiée, pas de logique spéciale.

À la création d'une session via `app/services/session_builder.py`,
le service pré-instancie pour chaque exercice du template :
- `N` lignes warmup vides (`N=2` par défaut, surchargeable)
- autant de lignes work qu'il y a de `RepTarget` prescrits
- toutes les lignes ont `completed=False` et des champs vides

La page séance n'a donc qu'à itérer sur des lignes existantes et
les remplir au tap — aucune création de ligne côté client.

## Flux de saisie (Sprint 1)

1. **Accueil** → tuile *Nouvelle séance*
2. **Bibliothèque** → bouton *Démarrer {template}* = `POST /sessions`
3. **Session detail** (`/sessions/{id}`) avec :
   - petit formulaire session-level au-dessus (concentration,
     global_state, bodyweight, note, *Enregistrer* / *Terminer*)
   - une **carte par exercice** avec ses sets (warmup + work),
     ses sélecteurs normalisés et son propre bouton *Enregistrer*
   - chaque carte est sauvegardée indépendamment
   - un bloc "Dernière fois" par carte (Sprint 2)
4. **Historique** liste les sessions passées avec filtre
   (Tout / En cours / Terminées) et badges (Sprint 2)
5. **Progression** : KPI cards (30 jours) + par-template (Sprint 2)
6. **Règles** : 8 cartes méthode consultables au gym, également
   rappelées en dépliable inline sur la page séance

## Alembic (Sprint 2)

```bash
alembic upgrade head              # apply pending migrations
alembic current                   # show current revision
alembic revision --autogenerate -m "add xxx"
```

Details in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md#alembic-workflow-sprint-2).

## Export / backup / restore

Trois URLs HTTP :
- **`/export`** — résumé du journal + dernier backup local + boutons
- **`/export/sessions.json`** — JSON versionné par `schema_version`
- **`/export/sessions.csv`** — CSV plat (une ligne par set), prêt pour Excel/Pandas

```bash
curl -sfL http://localhost:8000/export/sessions.json -o workout-journal-$(date +%F).json
curl -sfL http://localhost:8000/export/sessions.csv  -o workout-journal-$(date +%F).csv
```

Sauvegarde planifiée (Sprint 6) :

```bash
# Test manuel
BACKUP_DIR=./var/backups python -m scripts.backup_sessions
python -m scripts.list_backups
```

Sur le VPS, le timer systemd `workout-backup.timer` lance le
script chaque nuit à 03:30 UTC, avec rétention 30 jours par
défaut.

Vérification d'intégrité + health stricte (Sprint 7) :

```bash
# CLI : valide le dernier dump JSON, exit 0/1
python -m scripts.verify_backup

# Signal opérateur : DB + backup présent/valide
curl -sfL http://localhost:8000/healthz/strict | python -m json.tool
```

Le timer `workout-backup-verify.timer` lance `verify_backup`
chaque nuit à 04:00 UTC (30 min après la sauvegarde).

Restauration : trois scénarios documentés (rollback SQLite,
nouvelle machine, analyse spreadsheet) dans
[`deploy/README.md`](deploy/README.md#8-restauration).

Workflow complet d'exploitation (Alembic + drift check +
backups + nginx basic_auth + restore) :
[`deploy/README.md`](deploy/README.md).

## Déploiement OVH

Procédure complète : [`deploy/README.md`](deploy/README.md).
