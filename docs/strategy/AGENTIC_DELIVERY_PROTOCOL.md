# Agentic Delivery Protocol — Sb_OPS.agent-autonomy-01

**Statut :** NORMATIF · **Autorité :** `CLAUDE.md §4` (contrat versionné) — ce document en est le détail complet.
**Objectif :** réduire le copier/coller opérateur et les micro-GO en formalisant une **boucle de livraison spec-driven autonome** — **sans affaiblir aucun garde-fou** (`CLAUDE.md §1–§3`, check_scope, spec_protocol, ruff_budget, migration QA, CI xdist, coverage Sonar réparée, PR checks GitHub, validation Sonar API).

> Ce protocole **orchestre** les garde-fous existants ; il n'en supprime aucun. En cas de conflit entre ce document et `CLAUDE.md`, **`CLAUDE.md` prime** (contrat versionné).

---

## 1. L'ancienne boucle (problème)

La livraison était fragmentée en micro-GO, chacun suivi d'un CR :

```
GO PATCH → CR → GO COMMIT → CR → GO PUSH → CR → GO PR → CR → GO MERGE → CR → GO CLOSEOUT → CR → GO CLEANUP
```

Coût : **fatigue opérateur**, latence, copier/coller répété, et un CR par étape qui n'apporte pas de décision. Or le repo dispose déjà de garde-fous suffisants pour rendre l'essentiel de cette chaîne **déterministe et vérifiable** :
`check_scope` · `spec_protocol` · `ruff_budget` · migration QA (drift/snapshot/patterns/roundtrip) · CI xdist · coverage Sonar réparée · PR checks GitHub · validation Sonar API.

## 2. La nouvelle boucle (deux GO humains, le reste autonome)

```
GO BUILD  ──►  [autonome : branche → patch → checks check_scope → fix in-scope → commit → push → PR
                → recover CI dispatch ×1 si bloqué → fix CI/Sonar in-scope → push fix]
          ──►  STOP à : PR GREEN / MERGE PENDING   (ou BLOCKED : voir §5)

GO MERGE  ──►  [autonome : merge (méthode approuvée) → vérif CI canonique → vérif Sonar issues+coverage
                → closeout docs → push closeout docs-only → cleanup branche/worktree]
          ──►  STOP à : CLOSED + CLEANED
```

**Deux GO humains** encadrent la livraison ; entre eux, l'agent progresse **seul** jusqu'à un point d'arrêt défini. Un CR est produit **aux points d'arrêt** (PR GREEN, CLOSED+CLEANED, ou BLOCKED), pas à chaque micro-étape.

## 3. Autonomie autorisée après `GO BUILD`

L'agent PEUT, sans nouveau GO :

1. **Créer ou réutiliser** une branche + worktree (jamais un worktree non lié ; jamais réutiliser un worktree portant de la WIP non commitée d'un autre flux — en créer un frais et le signaler).
2. **Implémenter le patch scopé** (uniquement les fichiers autorisés par le sprint).
3. **Lancer les checks locaux exigés par `check_scope`** (§1 de `CLAUDE.md`) — le tier dicte le minimum suffisant ; **remonter d'un cran en cas de doute**, jamais descendre.
4. **Corriger les échecs dans le périmètre** (test qui casse légitimement, lint, budget, snapshot à régénérer, tests-gardiens de schéma/migration à mettre à jour pour refléter le schéma **approuvé**).
5. **Commit** (message conforme, trailer `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`).
6. **Push** la branche.
7. **Ouvrir la PR** (base = canonique).
8. **Récupérer une seule fois** un dispatch CI bloqué (GitHub Actions qui ne crée aucun run) via **close/reopen** de la PR — jamais un 2ᵉ nudge ; si toujours rien → STOP « PERSISTENT ACTIONS TRIGGER FAILURE ».
9. **Inspecter les logs CI** en cas de rouge.
10. **Corriger les problèmes CI/Sonar dans le périmètre** et pousser des commits de fix.
11. **S'arrêter** à `PR GREEN / MERGE PENDING` (5 checks verts + `mergeStateStatus CLEAN` + Sonar delta conforme) **ou** à un `BLOCKED` (§5).

## 4. Autonomie autorisée après `GO MERGE`

L'agent PEUT, sans nouveau GO :

1. **Merger avec la méthode approuvée** (celle indiquée par l'opérateur : typiquement `--merge`, no squash, **no `--admin`** quand le gate est `CLEAN`) avec garde `--match-head-commit`.
2. **Vérifier la CI canonique** (run push sur le merge commit → 3 jobs verts).
3. **Vérifier Sonar** : delta issues (0 attendu), `new_coverage ≥ seuil`, `coverage > 0` (non-régression), gate.
4. **Rédiger le closeout** (appendice post-merge au rapport de sprint + entrées registry/roadmap).
5. **Pousser le closeout docs-only** sur le canonique (`paths-ignore: docs/**` → CI légitimement non déclenchée ; **ce n'est pas un `[skip ci]`**).
6. **Nettoyer** branche + worktree du sprint (seulement ceux du sprint ; jamais un worktree non lié).
7. **S'arrêter** à `CLOSED + CLEANED`.

## 5. Conditions d'arrêt dur (STOP + rapport, GO humain requis)

L'agent **DOIT s'arrêter** et rapporter (fichier/erreur exacts + plus petit fix proposé) dès l'une de ces conditions — **jamais passer outre** :

- **conflit de spec** (le mandat contredit une spec versionnée) ;
- **ambiguïté de forme de migration** (multi-head, forme de colonne/contrainte non tranchée) ;
- **action destructive de données** (DROP/RENAME/UPDATE/DELETE de données historiques, reset/seed destructif) ;
- **faille de sécurité** ;
- **exposition de secret** (secret en clair, à committer, dans un log) ;
- **credential de service externe requis** (token/MCP/API non fourni) ;
- **thread de revue non résolu exigeant un changement de code** (un nit non bloquant, gate `CLEAN`, ne bloque pas — mais un thread qui **impose** une modif de code est un stop) ;
- **CI rouge hors périmètre du sprint** (régression dans un fichier non touché → ne pas « réparer en cascade ») ;
- **décision de merge** (merge, squash, `--admin`, choix de méthode) ;
- **dérive de périmètre au-delà des fichiers autorisés**.

**Jamais en autonomie** (même hors liste ci-dessus) : merge · squash · bypass `--admin` · suppression de branche/worktree · affaiblir un test/gate · éditer un secret · committer `AGENTS.md` sans autorisation explicite · toucher un worktree non lié · amender **silencieusement** une spec versionnée.

## 6. CR requis (aux points d'arrêt seulement)

Un CR est produit **à un point d'arrêt**, pas à chaque micro-étape. Contenu minimal :

- **PR GREEN / MERGE PENDING** : branche · commit SHA · fichiers changés · résultats de validation (check_scope tier · tests · migration QA le cas échéant) · run CI + statut des jobs · Sonar (delta issues · new_coverage · coverage) · `mergeStateStatus` · nombre de threads non résolus · si close/reopen utilisé · si rebase nécessaire.
- **CLOSED + CLEANED** : merge commit · run CI canonique + jobs · Sonar · closeout commit SHA (docs-only, poussé) · éléments nettoyés (branche/worktree) · éléments préservés.
- **BLOCKED** : condition d'arrêt exacte · fichier/erreur · plus petit fix proposé · options si arbitrage requis.

## 7. Règles spéciales — tier `MIGRATION`

- **`check_scope` = MIGRATION** → checks locaux : `isolated` + **full sweep local** + les 4 migration QA (`check_alembic_drift` · `check_schema_snapshot` · `check_migration_patterns` · `check_migration_roundtrip`) + régénération `data/schema_snapshot.sql`.
- **Additive-only** (contrat #1) : pas de DROP/RENAME/UPDATE/DELETE de données historiques ; downgrade symétrique ; aucun backfill non trivial sans GO.
- **FK sur SQLite** via `batch_alter_table` ; `check_migration_patterns` ne scanne que `upgrade()` (drops en `downgrade` OK).
- **Tests-gardiens** qu'une migration déclenche et qu'il **faut** mettre à jour dans le périmètre (reflet du schéma approuvé, jamais affaiblissement) : sentinelle du head Alembic, jeu de colonnes des tables enfants, « zéro FK vers le catalogue » si une FK sanctionnée est ajoutée. Un faux-échec **working-tree** (`git diff --name-only HEAD` non vide en mode PATCH/non commité) se résout **au commit** → le désélectionner et le documenter, ne pas le « réparer ».
- **Full sweep worktree** : les workers xdist n'héritent pas d'un `sys.path.insert` du contrôleur → propager `PYTHONPATH=<worktree>` + `os.chdir(<worktree>)` (piège de l'install éditable).
- **CI PR obligatoire** : la migration QA doit **tourner verte dans le job CI**, pas seulement en local.

## 8. Règles spéciales — travail `ASSET` / anatomie

- **Garde-fous durs** (Muscle Focus et dérivés) : pas de % d'activation · pas de claim EMG · pas de % de recrutement · **non médical** · provenance **BodyParts3D CC BY 4.0 conservée** · **pas d'anatomie finale générée par IA** (`ai_usage: NONE`) · **évolution de contrat additive uniquement** · pas de réécriture de géométrie (`viewBox`/chemins) sauf autorisation **explicite** séparée.
- **`ASSET INTEGRATION GATE`** : reste `BLOCKED` pour l'intégration générale ; toute surface runtime est une **exception owner-autorisée documentée**, jamais un flip de gate.
- **Revue anatomique / juridique / médicale professionnelle : NON revendiquée.**
- **Politique image** : images fournies = **références visuelles seulement** ; **aucun asset volumineux committé** sans une **décision `docs/assets` séparée** (budget/provenance/licence).
- Design source (`design/auren/**`), SVG de plaque et sha figées : **non réécrits** — référencés uniquement.

## 9. Règles spéciales — specs docs-only

- **`check_scope` = docs** → seul `check_spec_protocol` est requis en local ; le reste est overcheck (la CI est légitimement `paths-ignore`).
- Un commit **100 % `docs/**`** ne déclenche pas la CI (`paths-ignore`) ; un push docs-only sur le canonique protégé affiche un « bypass required status checks » **attendu** (les checks requis n'existent pas faute de run) — **ce n'est pas un `[skip ci]` manuel**.
- **Attention** : `CLAUDE.md`, `.check-policy.json` et autres fichiers **hors `docs/**`** ne sont **pas** couverts par `paths-ignore` → un sprint qui les touche **déclenche la CI** (tier ≥ `isolated`/`ci_infra` selon le fichier) et se livre **via PR**, pas par push docs-only direct.
- Toute nouvelle spec `Sx_*` doit porter un marqueur non-goals / « Périmètre interdit » (spec_protocol) ; tout nouveau rapport `SPRINT_Sb_*_REPORT.md` doit porter un marqueur de verdict.
- **Ne jamais amender silencieusement une spec versionnée** : un amendement passe par un commit documenté et justifié.

## 10. Périmètre interdit (non-goals de ce protocole)

- Ce protocole **n'autorise pas** merge/squash/`--admin`/suppression en autonomie (toujours GO/action humaine).
- Il **ne réduit pas** la CI ni les gates ; il **ne remplace pas** `check_scope`/`spec_protocol`/migration QA.
- Il ne modifie **aucun comportement produit** de l'app.
- Il ne s'applique **jamais** pour passer outre une condition d'arrêt du §5.

---

**Verdict :** 🟢 **AGENTIC DELIVERY PROTOCOL — DÉFINI.** Deux GO humains (`GO BUILD`, `GO MERGE`) encadrent une boucle autonome bornée par des garde-fous durs et des conditions d'arrêt explicites. Réduit les micro-GO sans réduire la sécurité. **Périmètre interdit** : §5 (arrêts durs) + §10 (non-goals).
