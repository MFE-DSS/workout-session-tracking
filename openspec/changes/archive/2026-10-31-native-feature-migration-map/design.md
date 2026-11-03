# Design — native-feature-migration-map

## Context

Motivation : `proposal.md`. Exigences : `specs/mobile/feature-migration-map/spec.md`.

**Observé (canonique `36b971a`)** : `app.main` monte 114 routes, dont **110 routes d'API** réparties sur 18 modules (`auth_routes` 19, `user_programs` 19, `squads` 16, `sessions` 11, `mobile_api` 11, `pages` 9, `body` 8, `admin` 4, `export` 3, `leaderboard` 3, `health` 2, et 6 modules à une route) ; les 4 autres sont `/openapi.json`, `/api/docs`, `/docs/oauth2-redirect` (désactivés en production) et le montage `/static`. 69 gabarits Jinja. Inventaires partiels existants : vNext `§2` (par actif, ~23), `§13` (ordre MISSION → EXECUTION → fin de séance → LOADOUT → BODY_LEDGER → ACCOUNT), `AUREN_INSTRUMENTS §6.3` (63 gabarits → instrument cible), `AUREN_UI_BLUEPRINT §5ter.3` (~13 capacités).

## Goals / Non-Goals

**Goals :** une source unique, lisible par machine, exhaustive par construction ; un rendu que l'opérateur lit d'un trait.
**Non-Goals :** aucune priorisation nouvelle (l'ordre reste celui de la roadmap de l'opérateur) ; aucun contenu de fonction neuve.

## Decisions

1. **Granularité = fonction utilisateur, pas route.** Une fonction regroupe ses routes (`routes: [GET /body, POST /body/measurements, …]`). *Alternative écartée :* une ligne par route — 110 lignes illisibles, et une même action utilisateur coupée en trois.
2. **YAML dans le change, spec vivante à l'archive.** `inventory.yaml` (données) + `inventory.md` (rendu généré par un script du change, jamais édité à la main). À l'archive, la spec vivante `openspec/specs/mobile/feature-migration-map/` porte les exigences ; l'inventaire déménage à côté (`openspec/specs/mobile/feature-migration-map/inventory.yaml`) et la garde le suit.
3. **Garde d'exhaustivité par `app.routes`.** La garde importe l'application et compare l'ensemble (méthode, chemin) monté à l'ensemble inventorié — dans les deux sens. Routes de documentation et montage statique : exclus par une liste nommée de 4 entrées, elle-même vérifiée (une exclusion qui ne correspond plus à rien échoue). *Alternative écartée :* lire les décorateurs par AST — un routeur inclus avec un préfixe ou monté conditionnellement échapperait.
4. **Les routes mobiles existantes sont inventoriées aussi** (`/api/mobile/v1`, statut `KEEP_DOMAIN`, destination = écrans natifs déjà livrés) : l'inventaire dit aussi ce qui est fait.
5. **Les STATUS `DEPRECATE` et `WEB_ONLY` sont des propositions** marquées `proposed: true` tant que l'opérateur ne les a pas tranchées ; la garde ne valide que la forme.

## Risks / Trade-offs

- [Classement faux par lecture rapide] → chaque fonction est rattachée à ses routes ET à son gabarit et à son service propriétaire, lus dans le code ; un échantillon est vérifié à la main avant publication (leçon : « la moitié d'une exploration est fausse »).
- [La garde accuse une route légitime ajoutée plus tard] → c'est le but : l'auteur de la route la classe dans le même commit.
- [Coût de la garde] → import de l'application seulement, aucune base ni requête.

## Migration Plan

PR unique, docs + un test ; aucun déploiement.
