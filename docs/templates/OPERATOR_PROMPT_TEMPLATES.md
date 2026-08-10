# Templates de prompts opérateur — AUREN

Modèles à copier-coller pour piloter un agent sur ce repo. Ils s'appuient sur le **DELIVERY
AUTONOMY ENVELOPE** et sur `CLAUDE.md §4`, qu'ils **n'affaiblissent jamais**.

Chaque modèle a une **skill** correspondante, chargée automatiquement par l'agent :
`.claude/skills/auren-sprint-from-spec/` et `.claude/skills/auren-standing-merge/`.

---

## 1. Injection d'une spécification succincte

**Quand l'utiliser** : vous avez une idée produit courte et vous voulez une livraison complète,
sans subir quinze questions de clarification.

```
MISSION — GO BUILD <SPRINT_ID>

Use DELIVERY AUTONOMY ENVELOPE.

Canonical:
<SHA, ou "latest canonical after previous closeout">

User spec:
<votre spec concise, en clair>

Interpretation rules:
- Preserve the user's product intent.
- Convert vague terms into explicit acceptance criteria.
- Prefer additive implementation.
- Avoid architecture rewrite unless the spec explicitly requires it.
- Inspect existing repo before coding.
- Reuse existing services, models, fixtures, and QA.
- Keep current UX/session/publication semantics unless the spec explicitly changes them.
- If a contradiction exists between the user spec and existing canonical architecture, STOP with options.

Required output:
- implementation
- tests
- docs report
- registry / roadmap update when applicable
- PR body with scope, files, tests, risks, non-regressions

Autonomy:
- fix local/CI/Gitar/Sonar findings in-scope
- rerun until PR GREEN / MERGE PENDING
- do not merge without GO MERGE
- do not cleanup without GO CLEANUP

Final:
<SPRINT_ID> PR GREEN / MERGE PENDING
```

**Ce que l'agent fera** : préflight du repo réel → classification de risque (en montant d'un cran
en cas de doute) → plus petit design cohérent → tests ciblés → sweep proportionnel → checks →
PR → correction autonome des retours **dans le périmètre** → arrêt à `PR GREEN / MERGE PENDING`.

**Ce qu'il ne fera pas** : merger, nettoyer, réécrire l'architecture, toucher `AGENTS.md`, ou
inventer une donnée manquante.

---

## 2. Standing merge (pour aller plus vite)

**Quand l'utiliser** : uniquement quand vous voulez que l'agent merge **sans revenir vous
demander** une fois la PR verte. À coller **dans le prompt du sprint** — jamais après coup.

```
STANDING GO MERGE ENABLED FOR THIS SPRINT

After PR is GREEN:
- verify head SHA
- verify 0 unresolved review thread
- verify required checks green
- verify Sonar gate clean
- verify no scope drift
- merge with:
  gh pr merge <PR_NUMBER> --merge --match-head-commit <HEAD_SHA>
- no squash
- no --admin
- verify canonical CI if code changed
- if closeout is docs-only and push CI skips by paths-ignore docs/**, record as legitimate skip
- update closeout docs
- push closeout
- final CR

Cleanup remains separate unless explicitly stated:
cleanup included
```

**Points de vigilance** :
- Le gate **externe** « SonarCloud Code Analysis » est distinct du job interne « SonarCloud » :
  les deux doivent être verts.
- Un gate Sonar rouge n'est **jamais** un artefact — il est diagnostiqué puis corrigé.
- « cleanup included » ne vaut que pour le worktree/branche **propre** du sprint mergé.

---

## 3. Rappels transverses

- Un **« GO » nu** est ambigu (build ? merge ? cleanup ?) : l'agent demandera, puisque merge et
  cleanup ne sont jamais le défaut.
- `check_scope` annonçant `ISOLATED` n'autorise pas à sauter le sweep quand le changement touche
  une donnée ou un flux partagés — ce sur-check a déjà évité trois régressions réelles.
- La **CI réelle** reste la source de vérité ; un commit 100 % `docs/**` skippe légitimement la CI
  push via `paths-ignore` (ce n'est pas un `[skip ci]`).
