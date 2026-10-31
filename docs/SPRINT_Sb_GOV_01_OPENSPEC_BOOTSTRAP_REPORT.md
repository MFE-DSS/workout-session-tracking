# Sb_GOV_01_OPENSPEC_BOOTSTRAP — OpenSpec devient la couche de gouvernance des changements

**Date :** 2026-10-31
**Branche :** `sb/gov-01-openspec-bootstrap` (base canonique `2413178`, après le closeout de COMPLETE)
**Verdict :** voir la fin du rapport.

## 0. Commande de l'opérateur

- « Je passe de 2 à 4 workstreams » : A · Visual Assets (P1 continu), B · Native Product (P0), C · Product
  Intelligence (P1), D · Platform/Business (P0/P1). « Et OpenSpec devient la couche de gouvernance au-dessus.
  Le Visual Contract actuel reste souverain pour le pixel. OpenSpec ne le remplace surtout pas. »
- Tranche zéro « AUREN — OPENSPEC BOOTSTRAP » : installer la CLI officielle courante, l'initialiser, ne pas
  migrer la documentation DA historique, créer la configuration minimale, écrire le pilotage AUREN (produit,
  cibles mobiles, autorité visuelle, autorité de domaine, règle de migration), fixer le cycle obligatoire, puis
  créer quatre changes indépendants (`android-pilot-readiness`, `native-feature-migration-map`,
  `native-navigation-shell`, `session-native-integration`), « Do not combine them into one PR ».
- En cours de tranche : « aussi il faut qu'on installe openspec ici ».

## 1. Brainstorming · Options · Risques · Choix retenu (`CLAUDE.md §3`)

| Option | Pour | Contre |
|---|---|---|
| A — OpenSpec à côté du registre, sans lien | rapide | deux autorités de spec : conflit de spec (`CLAUDE.md §4`) au premier désaccord |
| B — **OpenSpec sous le registre et `CLAUDE.md`, préséance écrite** | une seule chaîne d'autorité ; le registre recense chaque change | une ligne de registre de plus par change |
| C — migrer la doc canonique dans `openspec/specs/` | une seule arborescence | interdit par la commande ; réécrirait des contrats verrouillés |

**Choix : B.** Pilotage dans `openspec/config.yaml` (le champ `context` est injecté dans chaque instruction
d'artefact ; les `rules` contraignent proposal, design et tasks). Préséance : `CLAUDE.md` > contrats canoniques
> changes OpenSpec (`CLAUDE.md §6`, registre §1sexdecies).

**Risques et parades :**
- *`openspec init` écrit un `AGENTS.md`* (interdit au commit) → init limité à l'outil Claude ; constaté : aucun
  `AGENTS.md` produit.
- *Fichiers générés par un tiers dans un dépôt public* → les 12 fichiers lus ou balayés avant commit : aucune
  adresse externe, aucune commande hors `openspec` (`allowed-tools: Bash(openspec:*)`).
- *Version trop fraîche* → 1.14.3 (publiée le 2026-10-17, dépôt officiel `Fission-AI/OpenSpec`), épinglée ;
  1.15.0 et 1.16.0 ont moins de deux semaines.
- *Coût CI* → la CI traite `openspec/` comme du code (`classify_change_scope.NON_RUNTIME_PREFIXES =
  ("docs/", ".claude/skills/")`) : chaque PR de spec reçoit la CI complète (~11 min). Accepté ; l'élargissement
  de la liste est une tranche `ci_infra` séparée, pas celle-ci.

## 2. Ce qui est livré

- **CLI** : `@fission-ai/openspec@1.14.3` installée sur le poste (`openspec --version` → `1.14.3`).
- **`openspec/`** : `config.yaml` (schéma `spec-driven`, langue `fr`, mots-clés structurels et SHALL/MUST en
  anglais), `specs/`, `changes/archive/`.
- **Claude Code** : 6 skills (`.claude/skills/openspec-{explore,propose,apply-change,update-change,sync-specs,archive-change}`)
  et 6 commandes (`.claude/commands/opsx/*`), générées par la CLI, non modifiées.
- **Pilotage AUREN** (`config.yaml` → `context`) : produit mobile d'abord, le web comme source de domaine et
  jamais gabarit ; iOS + Android, code Expo partagé, divergences consignées ; autorité visuelle (LOCKED
  intouchable, exploration → revue opérateur → ACCEPT → baseline → intégration) ; autorité de domaine (rien
  d'inventé : bornes, récupération, anatomie, mappings, scores, recommandations ; aucune revendication
  d'activation ou de blessure) ; règle de migration KEEP_DOMAIN / REWRITE_NATIVE / WEB_ONLY / DEPRECATE /
  BLOCKED ; ce qu'OpenSpec ne remplace pas ; cycle obligatoire ; rappel des garde-fous du dépôt.
- **Règles d'artefacts** (`config.yaml` → `rules`) : hors-périmètre explicite, primitives verrouillées nommées,
  dépendances bloquantes nommées (proposal) ; observé vs proposé, divergences iOS / Android (design) ;
  `check_scope`, rendu exposé avant commit, aucune baseline sans approbation (tasks).
- **`CLAUDE.md §6`** : le cycle, la préséance, « les §1 à §5 restent intégralement en vigueur ».
- **Registre §1sexdecies** : la section OpenSpec et les quatre changes à venir.

## 3. Hors périmètre

- Aucun change ouvert dans cette PR : chacun des quatre a sa propre PR (consigne de l'opérateur).
- Aucune migration de la documentation existante ; aucun code produit ; aucune CI modifiée.

## 4. Vérifications

- `python scripts/check_scope.py` → tier rendu dans la PR.
- `openspec validate --all` ; `python scripts/check_spec_protocol.py`.
- Tests ciblés : gouvernance de `CLAUDE.md` et des skills (liste dans la PR).

## Verdict

**GOV-01 LIVRÉ EN PR** — OpenSpec installé et initialisé, pilotage AUREN écrit, préséance fixée sous `CLAUDE.md`
et les contrats canoniques. Suite : proposal `android-pilot-readiness`, soumise à la revue de l'opérateur avant
tout apply.

## Annexe — closeout (2026-10-31)

- **Merge** : PR #336, `--merge --match-head-commit 0a88fcc` → commit de merge `d6d2272` (aucun squash, aucun
  `--admin`). Barrière vérifiée avant le merge : tous les checks verts, gate Sonar `OK` (0 / 0 / 0), 0 fil de revue
  ouvert, `CLEAN`.
- **CI canonique** : run `41225920266` sur `d6d2272`, **verte**.
- **Production** : `d6d2272` déployé le même jour pour PLAT-01 (run `41227342844`, tag
  `deploy/prod/2026-10-31-1801-d6d2272`) — sauvegarde, migration additive `device_sessions`, smoke et contrôle de
  dérive Alembic verts. GOV-01 n'y ajoute rien d'exécuté (docs et outillage).
- **Suite** : la proposal `android-pilot-readiness` a été acceptée par l'opérateur (« ok donc parfait continue sur
  ton critical path ») ; son apply est en PR #337.

**Verdict final : GOV-01 CLOSED.**
