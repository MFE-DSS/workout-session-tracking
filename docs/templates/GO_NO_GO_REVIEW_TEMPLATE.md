# Sb_NN.k — GO / NO-GO Review

> À utiliser au moment où un sprint Sb_NN.k est marqué `LIVRÉ` par l'agent et que l'utilisateur doit décider d'enchaîner sur Sb_NN.k+1 ou d'attendre. Le but : forcer une revue explicite des DoD, pas une approbation tacite.

**Sprint reviewé :** `Sb_NN.k`
**Sprint report :** `docs/SPRINT_Sb_NN_k_REPORT.md`
**CI run :** [#NNNNNNNNNN](URL) commit `<sha>`
**Date de la revue :** `YYYY-MM-DD`
**Reviewer :** `<utilisateur>`

---

## 1. Verdict agent (rappel)

Citation verbatim du verdict final écrit par l'agent dans le sprint report.

## 2. Vérification DoD (revue humaine)

Cocher seulement ce qui a été **vérifié à la main** (CI sortie + lecture diff + spot check).

- [ ] pytest passe (vu dans le log CI)
- [ ] catalog_qa passe (vu dans le log CI)
- [ ] check_alembic_drift passe (vu dans le log CI)
- [ ] check_schema_snapshot passe (Sb_26.2+)
- [ ] check_migration_patterns passe (Sb_26.2+)
- [ ] check_migration_roundtrip passe (Sb_26.2+)
- [ ] ruff budget respecté (Sb_26.1+)
- [ ] pip-audit passe (Sb_26.4+)
- [ ] gitleaks passe (Sb_26.4+)
- [ ] diff lu : aucun fichier hors périmètre autorisé
- [ ] diff lu : aucun secret commité
- [ ] sprint report lu en entier, verdict cohérent avec le diff

## 3. Vérification des hard contracts du Sx_NN parent

Pour chaque hard contract verbatim, confirmer non-violation.

| Hard contract | Vu / non vu dans le diff |
|---|---|
| | |

## 4. Items signalés par l'agent à reporter ou trancher

Reprendre verbatim la section "Limites assumées" du sprint report et décider : on backlog / on tranche / on demande un Sb_NN.next dédié.

## 5. Décision

- ✅ **GO** Sb_NN.k+1 — sprint suivant peut démarrer
- ⏳ **WAIT** — `<raison + condition de levée>`
- ❌ **REVERT** — `<raison + commit à revert>`

## 6. Si WAIT : conditions de levée

Liste explicite de ce qui doit être fait avant de pouvoir dire GO. Format actionnable.

## 7. Trace

Cette revue doit être commitée si elle modifie un état durable (registry, amendement). Sinon, la conserver dans l'historique de chat.
