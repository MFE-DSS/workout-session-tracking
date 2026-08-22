# V1 Acceptance Checklist

Checklist finale avant de considérer la V1 comme validée pour un
usage quotidien personnel. Chaque étape donne la commande exacte
et le résultat attendu.

Répertoire de travail : racine du repo.

---

## Prérequis

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements-lock.txt
cp .env.example .env
```

---

## 1. Migrations

```bash
rm -rf var/workout.db
alembic upgrade head
```

- [ ] `Running upgrade  -> ef67ec29e3e0, initial baseline`
- [ ] `var/workout.db` existe

---

## 2. Tests

```bash
pytest -q
```

- [ ] `176 passed` (ou plus), zéro FAIL

---

## 3. Drift guard

```bash
python -m scripts.check_alembic_drift
```

- [ ] `Alembic drift check: OK (no diff).`
- [ ] Exit 0

---

## 4. Boot de l'app

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

- [ ] Uvicorn démarre sans traceback
- [ ] Le lifespan seed le catalogue et les règles

---

## 5. Navigation — pages principales

Ouvrir dans le navigateur (ou via curl) :

| URL               | Attendu                                    |
|-------------------|--------------------------------------------|
| `/`               | 5 tuiles, pas de Reprendre                 |
| `/library`        | 6 templates avec boutons Démarrer          |
| `/history`        | Liste vide ou sessions passées             |
| `/progress`       | KPI cards (valeurs 0 ou réelles)           |
| `/rules`          | 8 cartes méthode                           |
| `/export`         | Résumé + téléchargements + état backup     |
| `/healthz`        | `{"status":"ok"}`                          |
| `/healthz/strict` | JSON avec `"status":"ok"`                  |

- [ ] Chaque URL retourne 200

---

## 6. Création de séance

1. `/library` → cliquer **Démarrer Push A**
2. Redirigé vers `/sessions/1`

- [ ] 8 cartes exercice (E1..E8)
- [ ] Jump bar en haut avec 8 chips + FB
- [ ] Sous-titres Warmup / Work dans chaque carte
- [ ] "Dernière fois : Aucune séance précédente" sur chaque carte
- [ ] Pas de Repère (pas d'historique)

---

## 7. Saisie d'un exercice

Sur la carte E2 (Incline Smith Chest Press) :
- Work #1 : 60 / 10, Fait, clean, target_hit
- Work #2 : 62.5 / 8, Fait, acceptable, target_near
- Work #3 : 55 / 12, Fait, clean, target_hit
- Score 80, Muscle strong
- Cliquer **Enregistrer E2**

- [ ] Redirection vers la carte E3 (anchor suivant)
- [ ] Jump bar montre E2 en vert (3/3)
- [ ] Carte E2 a la bordure verte `exercise-card--done`

---

## 8. Feedback session + Terminer

Dans le formulaire session-level :
- Concentration : High
- Global state : Good
- Bodyweight : 78.5
- Note : "V1 acceptance"
- Cliquer **Enregistrer**, puis **Terminer la séance**

- [ ] Badge passe à "Terminée"
- [ ] "Séance terminée — éditable via Rouvrir"
- [ ] Carte E2 montre le done-summary strip
- [ ] Bouton Rouvrir visible

---

## 9. Deuxième séance → Dernière fois + Delta + Repère

1. `/library` → Démarrer Push A → `/sessions/2`
2. Sur E2, remplir Work #1 : 62.5 / 10, Fait, score 100

- [ ] "Dernière fois" montre "60 / 62.5 / 55 kg · 10 / 8 / 12 reps"
- [ ] "Repère" affiché (basé sur l'historique)
- [ ] Après Enregistrer E2 : "Delta" affiché (+2.5 kg · +2 reps · score en hausse)

---

## 10. Historique d'exercice

Cliquer le badge **E2** dans la carte → `/exercise-history/push-a/E2`

- [ ] 2 occurrences listées (newest first)
- [ ] Delta badge sur la plus récente
- [ ] Pas de delta sur l'ancienne (dernière dans la liste)
- [ ] Chaque ligne cliquable vers `/sessions/{id}`

---

## 11. Historique + filtre

`/history`

- [ ] 2 sessions (1 terminée, 1 en cours)
- [ ] Badges de statut, durée, X/Y exos
- [ ] Filtre "Terminées" montre 1 session
- [ ] Filtre "En cours" montre 1 session

---

## 12. Progression

`/progress`

- [ ] KPI cards avec des valeurs réelles (sessions_this_week ≥ 2)
- [ ] Par template : Push A avec 1 session terminée
- [ ] Activité récente par exercice : E2 avec ses poids/reps
- [ ] Lignes d'activité cliquables vers l'historique d'exercice

---

## 13. Active session banner

Naviguer vers `/library`, `/history`, `/progress`, `/rules` :

- [ ] Bandeau vert "Séance en cours · Push A · Reprendre →"
- [ ] Pas de bandeau sur `/` (Reprendre tile suffit)
- [ ] Pas de bandeau sur `/sessions/2` (déjà dessus)

---

## 14. Export

### 14.1 Page `/export`

- [ ] Résumé (sessions totales, terminées, work sets)
- [ ] Boutons Télécharger JSON et CSV
- [ ] État backup (présent ou absent)

### 14.2 JSON

```bash
curl -sfL http://localhost:8000/export/sessions.json | python -m json.tool | head -20
```

- [ ] `schema_version: 1`
- [ ] `count` cohérent
- [ ] Sessions avec exercises et sets

### 14.3 CSV

```bash
curl -sfL http://localhost:8000/export/sessions.csv | head -5
```

- [ ] Header avec 24 colonnes
- [ ] Lignes de données

---

## 15. Backup + verify

```bash
BACKUP_DIR=./var/backups python -m scripts.backup_sessions
python -m scripts.list_backups
BACKUP_DIR=./var/backups python -m scripts.verify_backup
```

- [ ] `backup_sessions: wrote sessions-...json ... and sessions-...csv`
- [ ] `list_backups: 2 file(s)`
- [ ] `verify_backup: [OK ] ...` + exit 0

---

## 16. Restore drill (optionnel mais recommandé)

```bash
export DRILL_DB=/tmp/drill-$$.db
DATABASE_URL=sqlite:///${DRILL_DB} alembic upgrade head
DATABASE_URL=sqlite:///${DRILL_DB} BACKUP_DIR=./var/backups \
  python -m scripts.restore_latest_backup
rm -f ${DRILL_DB} && unset DRILL_DB
```

- [ ] `restore: OK — restored N sessions, M exercises, P sets`

---

## 17. Mobile (téléphone sur le même Wi-Fi)

```bash
# Trouver l'IP locale
ip addr show | grep 'inet ' | grep -v 127.0.0.1
# ou: hostname -I

# Lancer uvicorn sur toutes les interfaces
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Ouvrir depuis le téléphone : `http://<IP_LOCALE>:8000`

- [ ] Home s'affiche
- [ ] Navigation fluide, pas de scroll horizontal
- [ ] Tap targets ≥ 44px
- [ ] Segmented controls lisibles

> **Sécurité** : `0.0.0.0` expose l'app sur tout le réseau local.
> Acceptable en dev Wi-Fi domestique. Ne PAS utiliser en réseau
> public (café, coworking). Revenir à `127.0.0.1` après le test.

---

## 18. Verdict

Si les étapes 1–15 sont toutes cochées :

**V1 ACCEPTÉE. Prêt pour un usage quotidien.**

Étapes 16 (restore) et 17 (mobile) sont recommandées mais
optionnelles pour le verdict V1.
