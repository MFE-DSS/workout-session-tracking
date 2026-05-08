# Sprint Sb_20.4 Build Report — Intégration SonarCloud

**Date :** 2026-05-08
**Type :** Build CI / qualité — implémente §J Sb_20.4 de `SPIGNOS_SECURITY_HARDENING_AND_SONAR_INTEGRATION_SPEC_v1.md`
**Prérequis :** Sb_20.1 (coverage.xml), Sb_20.2 (ruff + bandit), Sb_20.3 (hardening fonctionnel).
**Successeur :** Sb_20.5 (verrouillage Quality Gate en required status check).

---

## 1. Objectif

Brancher SonarCloud sur le pipeline GitHub Actions :

1. Configuration `sonar-project.properties` complète (org, version Python, ingestion ruff/bandit, exclusions cohérentes avec `[tool.coverage.run]`).
2. Job `sonar` dans `ci.yml` qui consomme les artifacts `coverage-xml` (Sb_20.1) et `linter-reports` (Sb_20.2 enrichi ici).
3. Runbook §3.4 documentant : génération `SONAR_TOKEN`, désactivation de l'analyse automatique, configuration de la Quality Gate `Spignos Way`.
4. Template de triage pour les 296 issues legacy.

Sb_20.4 livre **l'infrastructure** ; le triage à proprement parler dépend de l'export CSV SonarCloud côté UI et sera complété par Martin avec le template fourni.

## 2. Fichiers modifiés

| Fichier | Type | Nature |
|---------|------|--------|
| `sonar-project.properties` | Modify | Ajout `sonar.organization=mfe-dss`, `sonar.python.version=3.11`, ingestion ruff (`sonar.python.ruff.reportPaths`) + bandit (`sonar.python.bandit.reportPaths`), `sonar.coverage.exclusions` alignée avec `[tool.coverage.run]`, `sonar.sourceEncoding=UTF-8`. |
| `.github/workflows/ci.yml` | Modify | Job `lint` enrichi : 2 nouveaux steps `ruff JSON report` + `bandit JSON report` + upload artifact `linter-reports`. Nouveau job `sonar` qui `needs: [test, lint]`, télécharge les 2 artifacts, lance `SonarSource/sonarcloud-github-action@v2` en `continue-on-error: true`. |
| `docs/CICD_RUNBOOK.md` | Modify | Nouvelle §3.4 SonarCloud — secret + Quality Gate (6 étapes pas-à-pas). |
| `docs/SONARCLOUD_TRIAGE_TEMPLATE.md` | New | Template de triage : procédure d'export, 3 catégories, starter pack faux-positifs, tableau à remplir. |
| `docs/SPRINT_Sb_20_4_REPORT.md` | New | Ce rapport. |

Aucune ligne de code applicatif (`app/`) touchée. Aucun test modifié.

## 3. Décisions d'implémentation

### D1 — Org SonarCloud `mfe-dss`

URL fournie par Martin : `https://sonarcloud.io/organizations/mfe-dss/`. Pas de placeholder — la config est immédiatement utilisable.

### D2 — `needs: [test, lint]` avec download d'artifact

Le job `sonar` n'exécute **pas** ruff/bandit/pytest une seconde fois. Il consomme les artifacts produits par les jobs amont :
- `coverage-xml` → `coverage.xml` (Cobertura).
- `linter-reports` → `ruff-report.json` + `bandit-report.json`.

Avantage : le scan SonarCloud reste cohérent avec ce que la CI a déjà rapporté. Si `lint` échoue, le download d'artifact en `continue-on-error: true` permet quand même de scanner avec la coverage.

### D3 — `continue-on-error: true` partout V1

Le job `sonar` n'échoue jamais le pipeline en V1. Conformément à l'option A retenue :
- Le scan tourne et publie sur SonarCloud à chaque PR/push.
- La Quality Gate côté SonarCloud peut être en *failed* sans bloquer le merge.
- Sb_20.5 retirera ce flag et activera le required status check.

### D4 — `automatic analysis` à désactiver côté SonarCloud

Documenté dans le runbook §3.4 étape 3. Sans ça, SonarCloud refuse les analyses CI-based avec l'erreur `automatic analysis enabled`. Étape manuelle UI, une seule fois.

### D5 — Quality Gate `Spignos Way` sur *New Code* uniquement

Sx_20 §F.4 : le legacy code n'est pas re-noté V1, on grade le nouveau code. Conditions :
- Coverage on New Code ≥ 70 %.
- Maintainability/Reliability/Security Rating on New Code = A.
- Security Hotspots Reviewed = 100 %.

Cette gate n'est pas durcie sur le legacy avant la fin du triage Sb_20.4 (template fourni). Le but : éviter de bloquer la branche pour des issues qu'on a pas encore classées.

### D6 — Triage en mode template, pas en mode "j'attaque les 296 issues"

Le triage des 296 issues est un travail d'UI (ouvrir chaque issue, lire le contexte, classer). Pas faisable depuis Claude Code sans accès SonarCloud. La spec §H prévoyait déjà 6-8h pour cette partie ; on livre un template (`SONARCLOUD_TRIAGE_TEMPLATE.md`) pour structurer le travail :
- 3 verdicts : real / accepted / false-positive.
- Starter pack de 6 règles à muter en lot (faux-positifs probables documentés Sx_20 §B.2).
- Synthèse à coller dans le rapport final.

Une fois le triage rempli, soit on étend ce rapport, soit on commit un addendum `chore(sonar): triage`.

## 4. État des tests

```
739 tests passing (inchangé Sb_20.3)
coverage : 89.97 %
ruff : 478 warnings (advisory)
bandit : 0 Medium / 0 High
```

Aucun changement de tests dans ce sprint — c'est de l'infra CI pure.

## 5. Pré-requis utilisateur avant le premier scan

Avant que le job `sonar` ne tourne effectivement, Martin doit suivre le runbook §3.4 :

1. Générer `SONAR_TOKEN` côté SonarCloud.
2. L'ajouter en repository secret GitHub.
3. Désactiver *Automatic Analysis* côté SonarCloud (étape critique).
4. Configurer la Quality Gate `Spignos Way`.

Sans ces 4 étapes, le step `SonarCloud scan` log un échec mais ne bloque pas le merge (advisory V1).

## 6. Triage des 296 issues — à compléter

Voir `docs/SONARCLOUD_TRIAGE_TEMPLATE.md`. Une fois rempli, attendu :

```
Real à corriger          : ___ → reportés Sb_21 si non triviaux
Real à reporter          : ___
Accepted (won't fix)     : ___
False-positive           : ___
Hotspots reviewed        : ___ / 13
```

## 7. Limites assumées

1. **Triage non fait dans ce sprint** — voir D6. Template livré, exécution UI à la charge de Martin.
2. **Quality Gate pas encore en required** — V1 advisory. Sb_20.5 verrouille.
3. **Pas de scan PR-decoration** — non configuré V1 (besoin d'une app GitHub SonarCloud installée). Pourrait être activé en Sb_20.5 si utile.
4. **Pas de mypy intégré** — la spec §E listait mypy en optionnel. Reporté.
5. **Bandit en JSON depuis V1** — donc le step screen reste là pour la lisibilité PR mais on a le double output.

## 8. Synthèse

- 2 fichiers infra modifiés (`sonar-project.properties`, `ci.yml`), 1 doc modifié (`CICD_RUNBOOK.md` §3.4), 2 nouveaux docs (template triage + ce rapport).
- 0 ligne `app/` touchée.
- 739 tests verts inchangés.
- Pipeline prêt à faire tourner SonarCloud dès que le secret + l'UI sont configurés (4 étapes runbook).
- Triage des 296 issues : template prêt, exécution à venir.
- Sb_20.5 (verrouillage CI gate + runbook final + bilan avant/après) peut commencer une fois le triage validé.
