# Sb_MOB_00_FEATURE_MIGRATION_MAP — l'inventaire exhaustif du web, devenu backlog de la migration native

**Date :** 2026-10-31
**Branche :** `sb/mob-00-feature-migration-map` (change OpenSpec `native-feature-migration-map`, base `36b971a`)
**Verdict :** voir la fin du rapport.

## 0. Commande de l'opérateur

- « MOB-00 doit produire un catalogue exhaustif, pas une simple liste de routes » — pour chaque fonction : FEATURE ·
  LEGACY LOCATION · DOMAIN OWNER · API · DATA · USER ACTIONS · NATIVE DESTINATION · STATUS · DEPENDENCIES · VISUAL
  ASSETS · MIGRATION RISK. « Et c'est cette matrice qui devient notre backlog produit. »
- Fonctions citées qui ne doivent pas passer entre les mailles : profil, onboarding, poids, photos, forces / faiblesses,
  programmes modèles et personnels, ajout d'exercices, planning, substitutions, équipement, historique, récupération,
  abonnement, journal, reprise.
- Proposal acceptée et apply lancé : « GO faut qu'on avance sur le refactoring complet des autres espaces ».

## 1. Brainstorming · Options · Risques · Choix retenu (`CLAUDE.md §3`)

| Option | Pour | Contre |
|---|---|---|
| Une ligne par route (110) | mécanique | illisible ; une action utilisateur coupée en trois |
| Une ligne par gabarit (69) | proche de `AUREN_INSTRUMENTS §6.3` | rate les routes sans gabarit (POST, JSON, mobile) |
| **Une entrée par fonction utilisateur, routes rattachées, garde d'exhaustivité** | lisible ET exhaustive par construction | classement à vérifier contre le code |

**Choix :** fonctions utilisateur dans `inventory.yaml`, chaque route montée rattachée à une seule fonction, garde
qui lit `app.routes` dans les deux sens.
**Risques et parades :** classement de mémoire (→ extraction mécanique par route : fonction, docstring, gabarits rendus,
services appelés ; puis contre-vérification automatique des propriétaires et des tables, voir §3) ; garde dépendante de
l'ordre des tests (→ lecture des routes via la fixture `client`, jamais par import direct — piège déjà documenté au
dépôt) ; décisions produit prises en douce (→ `WEB_ONLY` / `DEPRECATE` marqués `proposed` tant que l'opérateur n'a pas
tranché).

## 2. Livré

- `openspec/changes/native-feature-migration-map/inventory.yaml` — **38 fonctions**, **110 routes** rattachées,
  4 exclusions nommées (documentation d'API et `/static`). Statuts : REWRITE_NATIVE 17 · BLOCKED 9 · WEB_ONLY 7
  (dont 6 proposés) · KEEP_DOMAIN 4 · DEPRECATE 1.
- `inventory.md` — rendu par famille, généré par `render_inventory.py` (jamais édité à la main).
- `tests/test_native_feature_migration_map.py` — 13 tests : forme de chaque entrée, statut fermé, `BLOCKED` avec cause,
  proposition limitée à `WEB_ONLY` / `DEPRECATE`, exhaustivité dans les deux sens, exclusions périmées ; cas négatifs.

## 3. Vérifications contre le code (la moitié d'une exploration est fausse)

- Couverture : 0 route non classée, 0 fantôme, 0 doublon, sur les 110 routes de `app.routes` du worktree (preuve :
  `app.__file__` dans le worktree, pas l'installation éditable de l'arbre principal).
- **Propriétaires de domaine** contre `app/services/` : **7 noms écrits de mémoire étaient faux** (`progression`,
  `recovery`, `catalog`, `weekly_plan`, `body_consent`, `exercise identity`…) — corrigés (`progress_facts` /
  `progression_view`, `recovery_contract` / `zone_recovery`, `loadout`, `weekly_planner` /
  `weekly_plan_materialization`, `body_profile`, `exercise_identity`).
- **Tables** contre les `__tablename__` : **4 corrections** (`body_consents`, `exercise_muscle_mappings`, les deux
  tables de partage de squad, `user_program_rep_targets` oubliée).
- Mutation de bout en bout : `GET /launcher` retirée de l'inventaire → la garde échoue en la nommant ; restaurée → verte.
- **Incident CI (premier push)** : la garde était verte en local et rouge en CI (`'_IncludedRouter' object has no
  attribute 'path'`). Cause : le venv local porte **FastAPI 0.135.3**, la CI installe le lock **0.141.1**, qui ne
  met plus à plat les routeurs inclus dans `app.routes`. Correctif : lecture récursive (`original_router` +
  `include_context.prefix`), plus un test d'un routeur inclus non aplati. Vérifié : mêmes 114 entrées sous les deux
  versions, garde verte dans un environnement installé depuis `requirements-lock.txt`. Le venv local n'est pas aligné
  sur le lock : tout test local sensible à la version de FastAPI peut mentir.

## 4. Ce que l'inventaire révèle

1. **L'hexagone existe déjà** : `radar.build_radar_svg` (SVG serveur « hexagonal radar chart for physique
   dashboard »), utilisé par le profil public, le classement et Body Intelligence. La phase profil le revalorise, elle
   ne part pas de zéro ; ses axes restent à décider (UX-LAB PROFILE).
2. **Le poids existe deux fois** : `users.weight_kg` (écrasé à chaque saisie) et `body_measurements.weight_kg`
   (série datée par `measured_at`). La série temporelle demandée existe ; il faut choisir une source unique, pas en
   créer une troisième.
3. **Absents du web** : onboarding (un parcours n'existe que dans le labo mobile), photos de progression (seul un
   consentement `photo_capture` est prévu), abonnement, exercice personnalisé, **suppression de compte** — bloquante
   pour toute diffusion publique (exigence des Stores).
4. **Social** : 19 routes (squads, défis, classement, profils publics) sans destination décidée — proposées
   `WEB_ONLY`, à trancher.
5. **Programmes personnels** : 16 routes, l'éditeur le plus riche du web — à découper V1 → V4.

## 5. Arbitrages de l'opérateur (2026-10-31)

Planche de revue : https://claude.ai/artifact/DsGo6zKv4djWg3egCBg7MG.

- « Oui, les 6 restent web » et, pour le social, « À migrer dans l'app ». Lecture cohérente des deux réponses : la
  réinitialisation du mot de passe, le contact, l'export et l'administration **restent web** (décidés, plus
  proposés) ; **squads, classement et profils publics passent en `REWRITE_NATIVE`** (espace social sous PROFIL,
  place exacte fixée après MOB-01).
- Navigation retenue pour MOB-01 : AUJOURD'HUI (la MISSION) · PROGRAMMES · PROGRÈS · PROFIL ; barre système, icônes
  AUREN.
- Statuts après arbitrage : REWRITE_NATIVE 19 · BLOCKED 9 · WEB_ONLY 5 · KEEP_DOMAIN 4 · DEPRECATE 1 ; aucune
  proposition ouverte.

## 6. Hors périmètre

Aucun code produit, aucune route modifiée, aucun écran ; aucune décision de navigation (MOB-01).

## Verdict

**MOB-00 LIVRÉ EN PR** — inventaire exhaustif par construction (110 / 110), gardé par la CI, arbitré par l'opérateur
(4 fonctions restent web, le social migre). Suite : `native-navigation-shell` (MOB-01), qui part de cette matrice.
