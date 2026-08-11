# SPRINT Sb_OPS_DEPLOY_SAFETY_01 — Durcissement du chemin de déploiement (RAPPORT)

**Base canonique :** `ae0c0e8` · **Branche :** `sb/ops-deploy-safety-01` · **Tier :** **CI_INFRA**
(full sweep local **obligatoire** + **validation CI réelle impérative**, `CLAUDE.md §1`).
**Origine :** constats réels du déploiement production du 2026-08-10 (run `31436196439`).
**Périmètre : OPS / CI-CD uniquement. Aucun déploiement production dans ce sprint.**

## 0. Correction d'interprétation du run 31436196439 — à consigner

Lors du CR de synchronisation, j'ai signalé comme **anomalie potentielle de perte de données**
le fait qu'Alembic semblait rejouer **toute** la chaîne depuis `initial baseline` sur une base
censée être estampillée. **C'était une fausse alerte, et l'erreur est de moi.**

`scripts/check_alembic_drift.py` s'exécute **avant** la migration et crée délibérément une
**base SQLite temporaire de dérive**, sur laquelle il rejoue **l'intégralité** de l'histoire
jusqu'à `head` afin de comparer les métadonnées. Ce sont **ses** lignes que j'ai lues.

La migration **production réelle** — celle capturée et préfixée `✓` par `deploy_prod.sh` — a
appliqué **exactement les 5 révisions attendues** :

```
k2l7f3g4i65 → l3m8g4h5j76 → m4n9h5i6k87 → n5o0i6j7l98 → o6p1j7k8m09 → p7q2k8l9n10
```

Vérifié après coup : `grep "Running upgrade" | grep "✓"` renvoie **5** lignes, exactement la
chaîne calculée par l'audit `Sb_OPS_PROD_SYNC_01`. La base était correctement estampillée à
`k2l7f3g4i65`. **Aucun correctif Alembic de récupération ou de `stamp` n'est nécessaire, et
aucun n'est fait ici.** Leçon retenue : ne pas mélanger deux flux de logs dans une même lecture,
et distinguer la sortie *capturée* d'un script de sa sortie *directe*.

## 1. Ce qui est livré — 4 volets

### WS1 · Vrai SHA de rollback

**Défaut** : `deploy_from_github_actions.sh` faisait `git reset --hard $TARGET` **avant** que
`deploy_prod.sh` ne lise `PRE_SHA` — qui valait donc… la cible. Le SHA précédent était **perdu**,
et `deploy_state.json` ne le contenait pas : le rollback reposait sur l'archéologie de tags.

**Correctif** : le wrapper capture `HOST_PRE_SHA` **avant** le reset et l'exporte ;
`deploy_prod.sh` le préfère (`${HOST_PRE_SHA:-…}`, repli sur la lecture locale pour les runs
manuels) ; `POST_SHA` est **relu depuis l'arbre** au lieu d'être recopié de `PRE_SHA` ; les deux
sont journalisés et `write_deploy_state.py` gagne un champ **`previous_sha`** (clé additive, les
lecteurs existants ignorent l'inconnu). Sémantique de déploiement par SHA exact : **inchangée**.

### WS2 · Backup SQLite fail-closed

**Défaut** : le chemin était **codé en dur** (`${APP_DIR}/var/workout.db`). Si `DATABASE_URL`
pointait ailleurs, le fichier était « introuvable », le script **avertissait**… et enchaînait sur
`alembic upgrade head` **sans aucune sauvegarde**. `/healthz/strict` n'assurant pas la présence
d'un backup, le trou était **invisible**.

**Correctif** : nouveau module **`scripts/resolve_sqlite_path.py`** (stdlib uniquement — il
tourne **avant** `pip install`) qui résout le fichier réel depuis `DATABASE_URL`. Ses **codes de
sortie sont l'API** : `0` chemin résolu · `3` non-SQLite (PostgreSQL → on saute, comportement
**inchangé**) · `4` SQLite sans fichier (mémoire). `deploy_prod.sh` **abandonne avant Alembic**
si : résolution impossible · chemin vide · fichier absent · **pas un fichier régulier** ·
échec du backup · **backup vide**. Le message est explicite : *refusing to migrate without a backup*.

### WS3 · Smoke Custom Program

Les **16 routes `/programs`**, montées **sans flag** et représentant l'essentiel de la synchro du
10 août, n'avaient **aucune couverture smoke**. Ajout de deux contrôles **non authentifiés et non
destructifs** : `GET /programs` et `GET /programs/new` doivent répondre **303**, ce qui prouve à
la fois que le routeur est monté **et** qu'il est protégé par propriétaire.

**Aucun identifiant inventé, aucun programme créé ou supprimé.** Le harnais smoke ne dispose
d'aucun compte et n'en recevra pas ici : une vérification authentifiée exigerait un secret
nouveau, hors périmètre. La limite est documentée plutôt que contournée.

### WS4 · Sécurité du `ref` de déploiement

**Défaut** : l'input `ref` avait pour défaut `"main"` — **branche inexistante** dans ce repo
(le tronc est `claude/sprint-reporting-fitness-app-V7Qr6`). Un dispatch par défaut échouait au
checkout.

**Choix retenu : supprimer le défaut, pas le remplacer par la branche canonique.** Un défaut de
branche déploierait une **tête mobile**, alors que la discipline du repo est de déployer le
**SHA exact validé par la CI**. Champ vide ⇒ choix conscient. Le SHA exact reste évidemment
supporté, le **SHA complet résolu est journalisé**, et un **avertissement GitHub** est émis si le
`ref` fourni n'est pas déjà un SHA complet. `workflow_dispatch` seul et `environment: production`
(approbation) : **inchangés**. `docs/CICD_RUNBOOK.md` corrigé (4 occurrences de `main`).

## 2. Fichiers touchés

| Fichier | Changement |
|---|---|
| `scripts/resolve_sqlite_path.py` (**neuf**) | résolveur `DATABASE_URL` → fichier SQLite, codes de sortie contractuels |
| `scripts/deploy_from_github_actions.sh` | capture + export de `HOST_PRE_SHA` **avant** le reset ; journalisation previous/target |
| `scripts/deploy_prod.sh` | `PRE_SHA` depuis le wrapper · `POST_SHA` relu de l'arbre · **backup fail-closed** · `--previous-sha` |
| `scripts/write_deploy_state.py` | champ additif `previous_sha` |
| `scripts/smoke_deploy.sh` | 2 contrôles `/programs` |
| `.github/workflows/deploy-production.yml` | plus de défaut `main` · SHA résolu journalisé · avertissement tête mobile |
| `docs/CICD_RUNBOOK.md` | consignes `main` corrigées |
| `tests/test_deploy_safety.py` (**neuf**) | 40 tests |
| **code applicatif · UI · migrations · schéma · flags** | **aucun** |

## 3. Tests — 40

**Logique réelle** (résolveur) : chemins relatifs/absolus, `+pysqlite`, query string, la paire
production exacte, `:memory:`, rejet PostgreSQL/MySQL, détection de dialecte, **contrat de codes
de sortie** (0/3/4), exécution **en sous-processus sur interpréteur nu** (il tourne avant
`pip install`).

**Gardes d'ordre et de fail-closed sur les sources shell** — assumées comme telles : les défauts
corrigés étaient précisément un défaut d'**ordre** (SHA lu après le checkout qui l'écrase) et un
défaut de **fail-open** (un avertissement là où il fallait abandonner). Une garde de source
attrape la régression de l'un comme de l'autre ; un hôte simulé, non. Pinnés : capture **avant**
`git reset` (ancrée sur la **commande exécutée**, pas sur une mention en commentaire) · export ·
`POST_SHA` non recopié · `--previous-sha` transmis et **round-trip réel du JSON** · chemin non
codé en dur · `skipping backup` **supprimé** · fichier régulier + backup non vide exigés · échecs
`sqlite3`/`cp` fatals · **bloc backup antérieur à l'appel Alembic** · **branche PostgreSQL non
contaminée** · smoke `/programs` sans identifiants · workflow sans défaut `main`, `ref` requis,
SHA résolu journalisé, dispatch-only + approbation conservés.

**Full sweep local (exigé par le tier CI_INFRA)** : **3035 passés, 0 échec** en 1 min 59 s.
**Validation sur CI réelle** : PR #74 **5/5 PASS** · gate Sonar **OK** · **CI canonique `31472257665` 3/3 GREEN** sur `43e3934` (`pytest + QA` 9 min 48 s).

## 4. Interdits tenus

**0 code produit · 0 UI · 0 migration · 0 modification de schéma · 0 changement de flag ·
0 auto-déploiement après merge · 0 automatisation de rollback mutant la base · 0 refonte de CI ·
0 déploiement production dans ce sprint.** Comportement PostgreSQL **inchangé**. Aucun correctif
Alembic de récupération (l'anomalie était une erreur de lecture, cf. §0).

## Verdict

**Verdict :** ✅ **Sb_OPS_DEPLOY_SAFETY_01 — MERGED + CANONICAL CI GREEN.** Le chemin de déploiement
passe de *fail-open* à *fail-closed* sur la sauvegarde, retrouve un **vrai SHA de rollback**
enregistré de façon exploitable, couvre la surface Custom Program au smoke, et supprime un défaut
de `ref` qui pointait vers une branche inexistante — sans toucher une ligne de code produit.

---

## Appendice post-merge (closeout)

- **Merge** : PR **#74 MERGED** 2026-08-11, build `8162e34` + corrections de revue `1f37703`,
  merge commit **`43e3934`** via `--merge --match-head-commit 1f37703` — **sans squash, sans
  `--admin`, sans force** (gate `CLEAN`, **0 thread non résolu**).
- **CI canonique** : run **`31472257665`** (`push`) **3/3 GREEN** sur `43e3934`.
- **Faux signal d'échec CI, à consigner** : le premier watch de la PR est sorti en erreur avec
  `error connecting to api.github.com`. Ce n'était **pas** un échec de CI — le run était en
  `attempt: 1`, `conclusion: success`, 3/3. Vérifié avant toute action : **aucun correctif n'a été
  déclenché sur un problème fantôme** (`CLAUDE.md §2` : distinguer un échec de test d'un incident
  d'infrastructure).
- **2 findings Gitar traités in-scope** :
  1. *Premier déploiement / reprise sur hôte vierge* — l'abandon fail-closed se déclenchait là où
     il n'y a légitimement rien à sauvegarder. **L'option « avertir plutôt qu'abandonner » a été
     refusée** : « fichier absent » est indistinguable de « `DATABASE_URL` pointe ailleurs », donc
     dégrader rouvrirait le trou même que ce sprint ferme. Résolu par un **opt-in explicite** :
     message nommant `SKIP_BACKUP=1`, raisonnement inline, **section 5bis** du runbook, 2 tests.
  2. *Commentaire du résolveur inexact* — `Path.resolve(strict=False)` **résout** bien les liens
     symboliques ; seul le contrôle d'existence est relâché. Commentaire corrigé (comportement
     déjà correct).
- **Cleanup** : branche `sb/ops-deploy-safety-01` + worktree `workout-session-tracking-deploy-safety`
  supprimés.
- **Aucun déploiement production** dans ce sprint. Les durcissements s'appliqueront au **prochain**
  déploiement.
