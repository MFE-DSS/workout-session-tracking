# Sprint Sb_24.7 + Sb_24.8 Build Report — Coach Report Implicite + audit, clôture cycle Sx_24

**Date :** 2026-06-01
**Type :** BUILD — derniers lots Sx_24, ferment le cycle.
**Prérequis :** Sb_24.1 → 24.6 + cleanup C livrés et déployés.

---

## 1. Résumé exécutif

### Sb_24.7

Le Coach Report `/coach-report` accueille un nouveau bloc **"Signaux d'effort 30j"** (taggé `Inféré`) qui agrège les `implicit_label` des sessions complétées de la fenêtre 30j :
- Total exercices labellés
- Label dominant
- Distribution % triée descending avec pastilles colorées

Cohérent avec Sb_24.6 (pastilles par exo sur `/done`) — Sb_24.6 = vision par séance, Sb_24.7 = vision macro 30j.

### Sb_24.8

Script CLI `scripts/audit_implicit_scoring.py` qui audite la pondération V2 sur les données réelles. Sortie : distribution `scoring_version`, distribution des labels, deltas V2-V1 (min/median/mean/max/stdev), verdict automatique (pondération équilibrée / trop généreuse / trop sévère).

Read-only, lance-le quand tu veux après quelques séances.

## 2. Contrats respectés

| Contrat | Mécanisme | Test |
|---|---|---|
| Spec §B.bis : tag `Inféré` obligatoire | Tag dans le H2 du bloc | `test_coach_report_implicit_block_tagged_inferred` |
| Cross-user isolation | Query filtre sur user_id | `test_block_isolates_users` |
| Fenêtre 30j strictement | `started_at >= now - 30d` | `test_block_ignores_sessions_outside_window` |
| Read-only | Aucune écriture BD | inspection code |
| Labels invalides ignorés | Filtre via `_LABEL_DISPLAY_30D` mapping | `test_block_ignores_invalid_label_values` |
| Empty state explicite | Bloc affiche message si total=0 | `test_coach_report_page_renders_empty_state` |

## 3. Fichiers modifiés / créés

| Fichier | Type | Nature |
|---|---|---|
| `app/services/coach_report.py` | Modify | +`ImplicitSignalsBlock` dataclass, +`_implicit_signals_30d()` agrégateur, +`_LABEL_DISPLAY_30D` mapping. `CoachReport` dataclass étendu (champ obligatoire). |
| `app/templates/coach_report.html` | Modify | Nouveau bloc inséré entre §6 discipline et §7 points forts. Empty state + distribution avec barres. Tag `Inféré`. |
| `tests/test_coach_report.py` | Modify | `_fake_report` étendu avec `implicit_signals` vide. |
| `tests/test_coach_report_implicit_block.py` | New | 8 tests : empty / aggregation / window / cross-user / invalid label / E2E page render / empty state / tag Inféré. |
| `scripts/audit_implicit_scoring.py` | New | CLI audit V1 vs V2 sur prod. Argparse `--days N --user-id N`. Read-only. |
| `docs/SPRINT_Sb_24_7_and_8_implicit_aggregate_BUILD_REPORT.md` | New | Ce rapport. |

**0 migration · 0 modèle touché · 0 réécriture historique.**

## 4. Diff métier visible

### Avant Sb_24.7

Coach Report affichait 10 blocs (identité, volume, ratio, zones, patterns, discipline, points forts, points faibles, axes, garde-fous). Les labels implicites étaient calculés (depuis Sb_24.3) mais **non agrégés** au niveau coach.

### Après Sb_24.7

Nouveau bloc "Signaux d'effort 30j" entre discipline et points forts :

```
Signaux d'effort 30j           [Inféré]
─────────────────────────────────────────
Sur 18 exercices labellés dans la fenêtre.
Dominant : Cohérente.

  Cohérente              ▓▓▓▓▓▓▓▓▓▓▓▓ 67% (12)
  Réserve probable       ▓▓▓▓▓ 28% (5)
  Incohérente            ▓ 6% (1)
```

Pastilles couleur cohérentes avec celles de `/sessions/{id}/done` (vert/orange/rouge calqué sur la contribution scoring).

### Sb_24.8 — usage

Quand tu as quelques séances réelles, lance :

```bash
sudo -u ubuntu /opt/workout-session-tracking/.venv/bin/python3 \\
    -m scripts.audit_implicit_scoring --days 30
```

Output type :

```
=== Audit Sb_24.8 — fenêtre 30j, 8 sessions completed ===

--- scoring_version ---
  v2: 8 sessions

--- Labels implicites (total 14 exos) ---
  trajectoire_coherente            8  (57%)
  reserve_probable                 4  (29%)
  pyramidal_ascendant              2  (14%)

--- Delta V2 - V1 (n=8) ---
  min   : -8
  median: +1
  mean  : +1.3
  max   : +6

--- Verdict ---
  Pondération w_implicit=0.25 équilibrée (mean delta +1.3).
```

Tu peux le rerunner après chaque batch de séances pour suivre l'évolution.

## 5. État des tests

```
Tests neufs Sb_24.7 :
  - tests/test_coach_report_implicit_block.py : 8/8 verts
  - tests/test_coach_report.py : _fake_report patché (existing 19/19 verts)

Full suite : 890 passing (vs 882 avant — +8, 0 régression)
```

## 6. Limites assumées

1. **Audit Sb_24.8 = script CLI read-only** — pas d'UI dédiée. Si tu veux un dashboard d'audit côté web, Sb_25 (Coach Report v2 narratif) ou un futur Sb_24.next pourrait l'intégrer.
2. **Le bloc Implicite 30j n'a pas de "garde-fou"** — il affiche brut. Pas d'avertissement type "encore peu de données". Acceptable V1.
3. **Pas de comparaison vs période précédente** — agrégation absolue 30j, pas de "vs 30j d'avant". Pourrait être ajouté Sb_24.next si signal utile.
4. **Pas d'export du bloc dans CSV / JSON** — V1 SSR + print uniquement.
5. **Le script audit lance verdict automatique simple** — seuils naïfs (±3 = équilibré, ±6 = à ajuster). Si la pondération doit vraiment être tunée, retour humain prime.

## 7. Clôture cycle Sx_24

Tous les lots planifiés du lotissement Sx_24 §K sont livrés :

| Lot | Sujet | Statut |
|---|---|---|
| **Sb_24.1** | Migration BD (scoring_version + implicit_label) | ✅ |
| **Sb_24.2** | Service `implicit_signal.py` (5 labels + classifier) | ✅ |
| **Sb_24.3** | Hook persistance à la complétion | ✅ |
| **Sb_24.4** | Dépréciation checkbox "fait" | ✅ |
| **Sb_24.5** | Formule `quality_score` V2 | ✅ |
| **Sb_24.5.cleanup (C)** | Normalisation scoring_version sur historique | ✅ |
| **Sb_24.6** | UI pastilles + breakdown sur `/done` | ✅ |
| **Sb_24.7** | Coach Report bloc Implicite 30j | ✅ |
| **Sb_24.8** | Script audit empirique | ✅ |

**Cycle Sx_24 techniquement clos.**

## 8. Bilan global cycle Sx_24

### Métriques

| | Avant Sx_24 | Après Sx_24 |
|---|---|---|
| Tests | 809 | 890 (+81) |
| Migrations BD | 13 | 15 (+2) |
| Services touchés | — | 3 nouveaux (`implicit_signal.py`, étendus `coach_report.py`, `quality_score.py`) |
| Friction utilisateur (clics/séance) | — | -24 clics (suppression checkbox `fait`) |
| Signaux par scoring | 4 (déclaratif pur) | 5 (déclaratif + implicit) |

### Contrats respectés

- **Invariance V1 absolue** — historique bit-pour-bit identique avant/après (validé par tests dédiés)
- **Pas de recalcul rétroactif** — Sb_24.5.cleanup bumpe le flag mais pas les valeurs
- **Pondération conservatrice** — `w_implicit = 0.25`, non touchée pendant tout le cycle
- **Sobre UX** — pas de pastille sur carte active (spec §G Q1=C respecté)
- **Triptyque vocabulaire** — `Mesuré`/`Inféré`/`Non déductible` maintenu sur Coach Report (spec Sx_23 §B.bis + Sx_24 §C)

### Backlog post-cycle (à arbitrer si dogfood signal)

- **Sb_24.next.tuning** — ajustement `w_implicit` selon retour terrain audit
- **Sb_24.next.labels** — ajout/raffinement des 5 patterns selon vraies sessions
- **Sb_24.next.swipe-left** — skip volontaire dans la saisie (Q3 limit assumée)
- **Sb_25** — Coach Report v2 LLM narratif encadré (spec déjà livrée Sx_25)

## 9. Recommandation suite

**Ton dogfood général** — comme tu l'as demandé. Toi qui valides en salle sur quelques séances :
- Pastilles sur `/sessions/{id}/done` cohérentes avec ton ressenti
- Breakdown V1/V2 lisible et juste
- Bloc Coach Report "Signaux d'effort 30j" pertinent
- Plus globalement : friction réduite avec la disparition de la checkbox, score V2 plausible

Tu reviendras avec une liste de retours. Je classifierai selon le framework Sx_21 méta-spec (bug / lacune UX / lacune signal / etc.) et on enchaînera sur le sprint le plus pertinent — qui peut être Sb_24.next* si retours ciblés, ou Sb_25 (LLM narratif) si tu veux ouvrir un nouveau chantier.

Cycle Sx_24 livré et fermé proprement.
