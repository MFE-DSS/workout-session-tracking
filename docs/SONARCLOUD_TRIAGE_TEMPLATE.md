# SonarCloud Triage Template — Sb_20.4

**Audience :** Martin, après le premier scan SonarCloud post-Sb_20.4.
**Objectif :** classer chaque issue en `real`, `accepted`, `false-positive` selon §H de la spec Sx_20.

---

## 1. Procédure d'export

1. SonarCloud → projet `workout-session-tracking` → onglet *Issues*.
2. Filtrer par sévérité (commencer par *Blocker* et *Critical*).
3. Clic sur ⋮ → *Export to CSV*.
4. Coller la CSV ci-dessous (ou linker en gist privé) puis remplir la colonne `verdict`.

## 2. Catégories

| Verdict | Action côté SonarCloud | Action côté code |
|---------|------------------------|------------------|
| `real` | laisser ouvert | corriger en Sb_20.4 ou ouvrir un ticket Sb_21+ |
| `accepted` | *Resolve as Won't Fix* + commentaire de justification | aucune (pattern volontaire) |
| `false-positive` | *Resolve as False Positive* + commentaire | aucune |

Justification commentaire SonarCloud : 1-2 phrases, citer Sx_20 §B ou un fichier de spec.

## 3. Faux-positifs probables (starter pack)

À muter en lot dès le premier scan, sans triage individuel :

| Rule | Pattern | Justification |
|------|---------|---------------|
| `python:S106` (logger over print) sur `scripts/**` | scripts CLI utilisent print volontairement | scripts hors prod |
| `python:S2245` (random non-crypto) | utilisé pour random workout suggestions | pas de contexte crypto |
| `python:S5547` (use modern Python) sur `from __future__ import annotations` | pattern volontaire pour PEP 563 | annotations sont string |
| `python:S5527` (verify SSL certificate) sur tests | tests utilisent TestClient en mémoire | pas de réseau réel |
| `python:S1192` (string literal duplicated 3x) sur templates | les noms de templates sont volontairement dupliqués pour clarté | refactor sans ROI |
| Hardcoded credentials sur `tests/conftest.py`, `tests/test_*` | mots de passe de tests en clair | fixtures de tests |

Commentaire à coller dans SonarCloud pour chacun :
> "Pattern volontaire documenté Sx_20 §B.2 / §H. Code applicatif sain confirmé par audit factuel — pas de remédiation prévue."

## 4. Tableau de triage à remplir

| # | Rule | File:Line | Sev | Verdict | Justification |
|---|------|-----------|-----|---------|---------------|
| 1 |      |           |     |         |               |
| 2 |      |           |     |         |               |
| … |      |           |     |         |               |

## 5. Synthèse attendue (à compléter post-triage)

```
Total issues scannés     : 296 (rapport initial)
Real à corriger          : ___
Real à reporter (Sb_21+) : ___
Accepted (won't fix)     : ___
False-positive           : ___
Hotspots reviewed        : ___ / 13
Coverage post-scan       : ___ %
Security rating          : ___
Reliability rating       : ___
Maintainability rating   : ___
```

## 6. Sortie attendue

Une fois rempli :
1. Copier le tableau dans `docs/SPRINT_Sb_20_4_REPORT.md` §6.
2. Si verdict `real` non triviaux → ouvrir un ticket par item (ou un sprint Sb_21).
3. Commit : `chore(sonar): Sb_20.4 triage — N real / N accepted / N FP`.
4. Passer à Sb_20.5 (verrouillage CI gate).
