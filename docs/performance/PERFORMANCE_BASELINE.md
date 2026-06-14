# Performance Baseline — Sb_26.6

**Audience :** contributeurs SPIGNOS + opérateur.
**Créé :** 2026-06-14 (sprint Sb_26.6).
**Statut :** baseline V1. Aucune stack lourde (Prometheus/Grafana/Locust) — juste un benchmark TestClient reproductible et une gate CI conservatrice.

---

## 1. Ce qui est mesuré (V1)

| Route | Type | Pourquoi |
|---|---|---|
| `GET /healthz` | liveness probe | doit rester quasi-instant (SELECT 1 + JSON) |
| `GET /healthz/strict` | strict health | DB + backup verify + disk + deploy_state |
| `GET /welcome` | landing non-auth | premier rendu pour un nouvel utilisateur |
| `GET /login`, `/register`, `/forgot-password` | forms non-auth | surfaces ciblées par le rate limiter |
| `GET /` | home authentifié | seed lifespan + session list + reco |
| `GET /history` | DB-heavy | liste paginée |
| `GET /progress` | DB + analytics | calculs d'agrégats |
| `GET /dashboard` | DB + render | KPIs |

Pour chaque route, le script `scripts/perf_baseline.py` mesure `min / median / p95 / max` en millisecondes via `time.perf_counter()` autour d'appels `TestClient`.

**Hors scope V1** : routes POST (création de sessions, scoring), endpoints internes (`/admin`, `/export`), routes batch (`/coach-report` qui dépend d'un cache LLM).

## 2. Comment lancer le benchmark localement

```bash
# Full run (50 itérations par route) + écriture du JSON
PYTHONPATH=. python scripts/perf_baseline.py

# Smoke (5 itérations) sans écrire
PYTHONPATH=. python scripts/perf_baseline.py --smoke --no-write

# Smoke + check budget (équivalent gate CI Sb_26.6)
PYTHONPATH=. python scripts/perf_baseline.py --smoke --check-budget --no-write

# Iterations personnalisées
PYTHONPATH=. python scripts/perf_baseline.py --iterations 200
```

Le script crée un TestClient isolé (temp SQLite), crée un user de test, se logge, hit chaque route N fois, agrège, écrit le JSON.

## 3. Interpréter median vs p95

- **median** = expérience typique. Tendance moyenne.
- **p95** = expérience worst-case "réaliste" pour un utilisateur. La gate CI compare le **p95**, pas la médiane — c'est ce qui signale une régression vécue par l'utilisateur, pas par les statistiques agrégées.
- **max** = informationnel uniquement. Trop sensible au jitter (GC, JIT, page swap, etc.) pour servir de gate.

Règle d'or : si p95 explose mais median reste stable, c'est probablement un cas particulier (cold cache, lock). Si **median ET p95 explosent**, c'est une vraie régression.

## 4. Pourquoi les budgets CI sont volontairement larges

GitHub Actions runners varient en CPU (2 vCPU, partagés). Le jitter peut multiplier la latence par 2-3x entre un runner "frais" et un "occupé". Si on serre le budget à p95 ≈ mesure locale, la CI flap toutes les semaines.

Choix V1 : budget = **5-10x** la médiane observée localement. Cela signifie :

- ✅ une régression d'ordre de grandeur (route qui passe de 5ms à 500ms) est détectée
- ❌ une régression de 50% (5ms → 7.5ms) n'est PAS détectée par CI — il faut lancer le benchmark local

C'est le compromis assumé "détecter les régressions énormes uniquement" du user constraint.

| Route | Budget V1 p95 (ms) | Mesure typique locale (ms) | Marge |
|---|---:|---:|---:|
| `GET /healthz` | 100 | 1-3 | ~30x |
| `GET /healthz/strict` | 800 | 1-5 | ~150x |
| `GET /welcome` | 500 | 1-3 | ~150x |
| `GET /login` | 500 | 1-3 | ~150x |
| `GET /register` | 500 | 1-3 | ~150x |
| `GET /forgot-password` | 500 | 1-3 | ~150x |
| `GET /` | 2500 | 5-20 | ~120x |
| `GET /history` | 2500 | 2-10 | ~250x |
| `GET /progress` | 2500 | 3-15 | ~150x |
| `GET /dashboard` | 2500 | 3-15 | ~150x |

## 5. Comment updater la baseline

```bash
# 1. Lancer le benchmark complet (50 itérations)
PYTHONPATH=. python scripts/perf_baseline.py

# 2. Inspecter docs/performance/PERFORMANCE_BASELINE_V1.json
cat docs/performance/PERFORMANCE_BASELINE_V1.json

# 3. Si nouveau matériel ou refactor majeur :
#    Ajuster .performance-budget.json AVEC justification dans le commit
vim .performance-budget.json

# 4. Commit + push
git add docs/performance/PERFORMANCE_BASELINE_V1.json .performance-budget.json
git commit -m "chore(perf): refresh baseline post-<reason>"
```

**Interdit en sprint feature** : changer un budget juste parce que "ça passe pas". Cause root d'abord, budget ensuite.

## 6. Comment investiguer une régression

1. **Locale d'abord** : `python scripts/perf_baseline.py` — la régression est-elle reproductible hors CI ?
2. **Comparer** : diff entre l'ancien et le nouveau `PERFORMANCE_BASELINE_V1.json`
3. **Activer slow query log** :
   ```bash
   PERF_LOG_SLOW_QUERIES_ENABLED=1 \
   PERF_SLOW_QUERY_MS=50 \
   PYTHONPATH=. python scripts/perf_baseline.py --iterations 20
   ```
   Logs → ligne `WARNING spignos.slow_query: slow query 65ms (threshold 50ms): SELECT ...`
4. **Activer request timing** :
   ```bash
   PERF_REQUEST_TIMING_ENABLED=1 \
   PYTHONPATH=. python scripts/perf_baseline.py --smoke
   ```
   Logs → ligne `INFO spignos.request_timing: request GET / -> 200 in 12.3ms`
5. **Profiler ciblé** : `python -m cProfile -o profile.out scripts/perf_baseline.py` puis `snakeviz profile.out`

## 7. Slow query logging — opt-in détaillé

Implémentation : `app/database.py:_maybe_register_slow_query_logger()` enregistre 2 event listeners SQLAlchemy (`before_cursor_execute`, `after_cursor_execute`) **uniquement si** `PERF_LOG_SLOW_QUERIES_ENABLED=1`. Quand désactivé (défaut), aucun listener n'est attaché — coût runtime = un `bool` au démarrage de process.

| Env var | Défaut | Effet |
|---|---|---|
| `PERF_LOG_SLOW_QUERIES_ENABLED` | `false` | enable / disable le listener |
| `PERF_SLOW_QUERY_MS` | `250` | seuil de log en ms |

**Ce qui est loggé** :
- `WARNING spignos.slow_query: slow query <ms>ms (threshold <ms>ms): <statement tronqué à 200 chars>`

**Ce qui n'est PAS loggé** :
- ❌ pas de paramètres (peuvent contenir hash bcrypt, email, etc.)
- ❌ pas de result set
- ❌ pas de stack trace

Test : `tests/test_performance_baseline.py::test_slow_query_logger_*`.

## 8. Request timing middleware — opt-in

Implémentation : `app/main.py:RequestTimingMiddleware`. Sans `PERF_REQUEST_TIMING_ENABLED=1`, le middleware ne mesure même pas le temps (`return await call_next(request)` en première instruction).

**Pas de header HTTP** : aucun `X-Response-Time` / `Server-Timing` ne fuite. Pour exposer publiquement (jamais en V1), il faudrait un sprint dédié + amendement.

Test : `tests/test_performance_baseline.py::test_request_timing_*`.

## 9. Limites V1

| Limite | Pourquoi | Reporté à |
|---|---|---|
| Pas de load testing (Locust, k6) | Hors scope V1 — stack lourde | Sb_27+ |
| Pas de profiling SQL persistant | Hors scope V1 | Sb_27+ |
| Pas de métriques business (sessions/jour, etc.) | Hors scope perf | hors Sx_26 |
| Pas de distributed tracing | Stack OpenTelemetry hors V1 | post-Sx_26 |
| TestClient ≠ uvicorn prod (pas de ASGI server overhead) | Mesure relative pertinente, pas absolue | acceptable V1 |
| Budgets ne couvrent pas POST routes | TestClient supporterait, mais besoin de fixtures plus lourdes | Sb_27+ |
| Pas de mesure réseau (latence client / serveur) | TestClient = in-process | acceptable V1 |
| Pas d'export Prometheus | Hors contrat user "Pas de Prometheus" | hors Sx_26 |

## 10. Backlog perf

| Item | Priorité | Sprint cible |
|---|---|---|
| Locust scenario `/login` + `/` avec users concurrent | basse | Sb_27.next.perf-load-1 |
| Persistance des baselines historiques (chart) | basse | Sb_27.next |
| Profiling SQL N+1 détecté en CI | moyenne | Sb_27.next |
| Budgets per-percentile (p50 + p95 + p99) | basse | Sb_27.next |
| Mesure cold-start uvicorn vs warm | basse | Sb_27.next |
| Endpoints POST (création session, scoring) | moyenne | Sb_26.next.perf-post-1 |

## 11. Gate CI Sb_26.6

```yaml
- name: perf baseline smoke + budget (required — Sb_26.6)
  env:
    PYTHONPATH: .
  run: python scripts/perf_baseline.py --smoke --check-budget --no-write --environment ci
```

- **smoke** : 5 itérations par route → ~50 requêtes total → < 5s en CI
- **check-budget** : exit 1 si p95 > budget
- **no-write** : ne pollue pas le repo CI
- budgets actuels : voir §4, marge 30x→250x

Si la gate flap (>2 fois en 2 semaines sur des branches valides), élargir les budgets dans `.performance-budget.json` avec justification, **jamais** désactiver la gate.
