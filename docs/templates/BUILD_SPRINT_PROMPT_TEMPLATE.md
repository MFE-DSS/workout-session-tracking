# Sb_NN.k — Build Sprint Prompt Template

> Ce template est à copier dans la prompt utilisateur au moment d'ouvrir un sprint **build** (qui livre du code). Pour un sprint **spec only** (Sx_NN), utiliser `SPEC_TEMPLATE.md` à la place.

---

## GO Sb_NN.k — `<TITLE>`

### Contexte

Quels sprints sont déjà livrés. Référencer les derniers run CI verts (numéro + SHA). Citer l'état du ruff budget, baseline.

### Objectif Sb_NN.k

Un paragraphe + une liste numérotée des objectifs concrets et mesurables. Doit refléter **exactement** la décomposition du Sx_NN parent (sans scope creep).

### Périmètre autorisé

Liste exhaustive et **plus restrictive** que le périmètre du Sx_NN parent.

- ✅ ...
- ✅ ...

### Périmètre interdit

Reprendre verbatim les non-goals du Sx_NN parent, **plus** les non-goals spécifiques à ce sprint.

- ❌ Ne touche pas à …
- ❌ Ne modifie pas …
- ❌ Ne casse pas …

### Hard contracts (verbatim — non négociables)

Reprendre verbatim les hard contracts du Sx_NN parent. Tout sprint qui viole un hard contract est rejeté en review.

### Livrables attendus

Liste explicite des fichiers à créer / modifier. Pour chaque livrable, mentionner s'il est TEST, SCRIPT, DOC, CONFIG, CODE.

### Tests attendus

- pytest spécifique au domaine ;
- gates CI existantes doivent rester vertes ;
- nouveaux tests pour les nouvelles surfaces.

### DoD

- [ ] pytest passe
- [ ] catalog_qa passe
- [ ] machine_atlas_qa passe
- [ ] check_alembic_drift passe
- [ ] check_schema_snapshot passe (Sb_26.2+)
- [ ] check_migration_patterns passe (Sb_26.2+)
- [ ] check_migration_roundtrip passe (Sb_26.2+)
- [ ] check_ruff_budget passe (≤ baseline en vigueur)
- [ ] pip-audit passe (Sb_26.4+)
- [ ] gitleaks passe (Sb_26.4+)
- [ ] lint job passe
- [ ] CI réelle verte sur les 3 jobs
- [ ] sprint report livré dans `docs/SPRINT_Sb_NN_k_REPORT.md`
- [ ] verdict explicite : ✅ Sb_NN.k+1 PRÊT ou ⏳ attendre

### Rollback

Procédure si le sprint doit être annulé après merge. Si non-applicable (sprint purement doc/tooling), écrire "N/A — sprint sans impact runtime."

### Open questions à trancher en pré-build (si applicable)

- **OQ-N** : … · options · recommandation par défaut.

---

**Cf.** `docs/strategy/SPEC_DRIVEN_ENGINEERING_PROTOCOL_v1.md` · `docs/templates/SPRINT_REPORT_TEMPLATE.md`
