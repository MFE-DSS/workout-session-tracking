# Sprint Report — Sx_UI_05 Today / Readiness Home Spec

**Sprint ID :** `Sx_UI_05_TODAY_READINESS_HOME`
**Type :** SPEC ONLY (docs-only) — product / UX / technical specification
**Date :** 2026-07-07
**Auteur :** opérateur (Martin Feldmann) + agent Claude Code
**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`
**Verdict :** ✅ **READY FOR HUMAN REVIEW**

---

## 1. Résumé

Sprint spec-only qui **ouvre le prochain écran** du cycle Sx_UI après la clôture de Sx_UI_04 (Focused Exercise Flow) : le **Today / Readiness Home**, surface d'entrée mobile-first du produit. La spec cadre un Home **décisionnel** (« quoi faire aujourd'hui ») plutôt qu'un tableau de bord, en identité Auren (Clinical Instrument), en réutilisant **uniquement des données déjà existantes** (sessions, readiness self-report, KPIs, recommandation, atlas) — aucun nouveau modèle, migration ni moteur readiness médical.

**BUILD BLOQUÉ** tant que cette spec n'est pas acceptée + OQ confirmées.

## 2. Fichiers créés / modifiés

### Créés
- `docs/strategy/Sx_UI_05_TODAY_READINESS_HOME_SPEC.md` — spec principale, 28 sections
- `docs/SPRINT_Sx_UI_05_REPORT.md` — ce rapport

### Modifiés
- `docs/strategy/SPEC_REGISTRY.md` — Sx_UI_05 🟢 SPEC delivered pending review
- `docs/strategy/ROADMAP_AND_NEXT_STEPS.md` — prochaine action = human review Sx_UI_05

La spec `Sx_UI_05_TODAY_READINESS_HOME_SPEC.md` **n'existait pas** → créée comme spec complète (pas d'amendement).

## 3. Confirmation docs-only

**Scope strict respecté.** Aucun fichier hors `docs/` modifié :
- ❌ `app/` (lecture read-only uniquement : `index.html`, `pages.py::home`, `readiness.py`)
- ❌ `tests/`, `scripts/`, `migrations/`, `.github/`
- ❌ deps, PNG, runtime, DB, secret
- ❌ Aucun rebrand SPIGNOS → Auren
- ❌ Aucun code readiness / modèle créé

## 4. Décisions produit prises (§ de la spec)

| # | Décision | Section |
|---|---|---|
| 1 | Home = **surface de décision quotidienne**, pas tableau de bord | §1, §2, §8 |
| 2 | **CTA principale unique** (reprendre / démarrer / choisir / repos) | §8 |
| 3 | Session active **domine** si elle existe | §8, §10, OQ-05-C |
| 4 | Readiness = **bande qualitative self-report**, jamais score médical | §9, OQ-05-B |
| 5 | Progress = **snapshot + lien**, pas dashboard inline | §13, OQ-05-F |
| 6 | Body continuity = **résumé léger**, pas heatmap | §14, OQ-05-E |
| 7 | **Data contract : existing data only** (sessions, readiness, KPIs, reco, atlas) | §19 |
| 8 | Home **entièrement no-JS** V1 | §18, OQ-05-I |
| 9 | Auren scoped, faible chrome, pas de gamification | §17 |
| 10 | Build split 5 sous-sprints (IA/hero → active/next → readiness → progress/body → empty/a11y) | §21 |

## 5. Décisions OQ (10 tranchées avec recommandation)

| OQ | Recommandation V1 |
|---|---|
| **OQ-05-A** route `/` | reste **Today** (pas de redirect forcé) |
| **OQ-05-B** readiness | **bande qualitative** (sans nouveau calcul) |
| **OQ-05-C** active + prévue | **active domine** |
| **OQ-05-D** repos | **oui, non impérative** |
| **OQ-05-E** body sur Home | **résumé léger**, pas de heatmap |
| **OQ-05-F** vs Progression | **snapshot + lien** |
| **OQ-05-G** coach | **micro-note contextuelle** |
| **OQ-05-H** nouvel utilisateur | hero **« Commencer »** |
| **OQ-05-I** no-JS | **oui, entièrement** |
| **OQ-05-J** personnalisation | **aucune nouvelle pref** V1 |

## 6. Build split proposé

- **Sb_UI_05.1** Home IA + Hero Decision Surface
- **Sb_UI_05.2** Active Session / Next Workout Cards
- **Sb_UI_05.3** Readiness / Recovery Snapshot
- **Sb_UI_05.4** Recent Progress + Body Continuity
- **Sb_UI_05.5** Empty States + Accessibility + Screenshot Hardening

## 7. Ancrage sur données réelles existantes (audit read-only)

Lecture de `app/routers/pages.py::home` : le contexte Home expose déjà `open_session`/`open_since`, `kpis`, `sparkline_svg`, `reco`, `behavioral`, `readiness_today` (+labels/scales), `home` payload. Lecture de `app/services/readiness.py` : readiness = **scales auto-déclarées 1-5** (sommeil/fatigue/courbatures/stress/motivation) — **self-report, pas mesure physiologique**. La spec s'appuie sur ces données réelles ; tout agrégat nouveau est marqué **future/deferred**.

## 8. Limites

- La spec **ne construit rien** : elle cadre. Le readiness V1 s'appuie sur du self-report existant ; aucune bande qualitative agrégée n'est calculée tant qu'un build ne l'implémente (marqué future si nouveau calcul).
- Le Home actuel est riche (board-like) ; la bascule vers « surface de décision » exigera de dé-prioriser certaines métriques — à trancher au build .1.
- Body continuity dépend de la disponibilité des zones atlas côté Home (à confirmer au build).

## 9. Confirmations sécurité et compat

- ✅ Aucun secret / cookie / token affiché ou committé
- ✅ Aucun PNG / runtime / DB committé
- ✅ Aucun changement de contrat métier (services/models/migrations intacts)
- ✅ Aucun claim médical / physiologique dans la spec
- ✅ Sx_UI_04 non rouvert (référence produit uniquement)

## 10. Statut post-livraison

| Item | Statut |
|---|---|
| `Sx_UI_05_TODAY_READINESS_HOME_SPEC` | 🟢 **SPEC delivered — pending human review** |
| `Sb_UI_05.1` → `.5` | ⏸️ **BLOCKED** tant que la spec n'est pas acceptée + OQ confirmées |
| `Sx_UI_06 Exercise Intelligence Presentation` | ⚪ future, not opened |
| Release tag | ⏸️ deferred |

## 11. Prochaine action recommandée

1. **Human review** de `Sx_UI_05_TODAY_READINESS_HOME_SPEC` (opérateur).
2. **Confirmer / ajuster OQ-05-A → OQ-05-J** (§23).
3. **Puis ouvrir `Sb_UI_05.1 Home IA + Hero Decision Surface`** sur override explicite.

## 12. Verdict

✅ **READY FOR HUMAN REVIEW.**

**Aucun build ouvert. Sx_UI_06 future, not opened. Aucun release tag.**
