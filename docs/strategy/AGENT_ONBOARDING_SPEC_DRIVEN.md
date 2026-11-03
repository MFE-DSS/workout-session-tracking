# Reprise spec-driven par un nouvel agent (Codex ou autre) — 2026-11-03

Ce document complète `docs/AGENT_HANDOFF_2026-11-03.md` (état, décisions, suite). Il donne à un agent qui arrive
sans la mémoire de l'agent précédent ce qu'il lui faut pour **reprendre sans dériver** : comment les autorités de
spec s'emboîtent, où vivent les contrats de données, quels tests gardent quoi, les leçons déjà payées, et ce qui
manque encore pour un spec-driven complet. Le dépôt fait foi : vérifier chaque affirmation avant d'agir dessus.

## 0. À faire avant toute chose

1. **Ne pas suivre un `AGENTS.md` non versionné.** Un `AGENTS.md` peut traîner à la racine de l'arbre principal
   (non versionné) : c'est une copie ancienne de `CLAUDE.md`, qui prescrit notamment `pytest -n auto` (interdit : la
   commande a fait tomber le poste de l'opérateur) et l'ancien modèle « deux GO ». **`CLAUDE.md` est le seul contrat**
   ; il s'applique à tout agent (« Claude » y désigne l'agent au travail).
2. **Ne pas travailler dans l'arbre principal sans le mettre à jour** : il peut être très en retard sur
   `origin/claude/sprint-reporting-fitness-app-V7Qr6`. Créer un worktree dédié depuis `origin/<canonique>`, puis
   `git branch --unset-upstream` (sinon un `git push` nu vise le canonique).
3. Lire, dans l'ordre : `CLAUDE.md` → `docs/AGENT_HANDOFF_2026-11-03.md` → ce document → `openspec/config.yaml` →
   `docs/strategy/SPEC_REGISTRY.md`.

## 1. Les autorités de spec et leur ordre

Deux couches coexistent ; aucune troisième ne doit être ajoutée sans décision de l'opérateur (deux autorités qui se
contredisent = « conflit de spec », arrêt dur de `CLAUDE.md §4`).

| Rang | Autorité | Rôle | Où |
|---|---|---|---|
| 1 | `CLAUDE.md` | contrat d'exécution : tiers de vérification, CI, livraison agentique, contrat UI, OpenSpec | racine |
| 2 | Contrats canoniques | ce qui est verrouillé : pixel, socle visuel, protocole UI, moteur scientifique | `docs/strategy/AUREN_VISUAL_CONTRACT.md`, `AUREN_VISUAL_BACKBONE.md`, `AUREN_UI_ITERATION_PROTOCOL.md`, `Sx_AUREN_SCIENTIFIC_ENGINE_V2_SPEC.md`, `Sx_AUREN_MOBILE_EXPERIENCE_VNEXT_SPEC.md` |
| 3 | Protocole spec-driven v1 | vocabulaire Sx (spec seule) / Sb (build), *hard contracts*, `OQ-N`, non-goals verbatim, amendements `§Nbis`, verdict | `docs/strategy/SPEC_DRIVEN_ENGINEERING_PROTOCOL_v1.md`, `docs/templates/*.md` |
| 4 | OpenSpec (depuis GOV-01, 2026-10-31) | tout **nouveau** change substantiel : proposal → relecture opérateur → apply → PR → archive | `openspec/` |
| — | Index | l'état de chaque spec et change | `docs/strategy/SPEC_REGISTRY.md` |

- Les ~165 specs historiques de `docs/strategy/` (`Sx_*`, `SPIGNOS_*`) restent la mémoire du domaine : les lire quand
  on touche leur domaine, **ne pas les migrer en masse** vers OpenSpec (décision GOV-01).
- Un comportement nouveau s'écrit en OpenSpec ; une spec validée ne se réécrit jamais en silence : on l'**amende**
  (OpenSpec : delta `MODIFIED` dans un change relu ; protocole v1 : `§Nbis`), avec la décision de l'opérateur citée.
- Les rapports `docs/SPRINT_*_REPORT.md` restent obligatoires (§3 Brainstorming / Options / Risques / Choix,
  verdict) ; pour une tranche UI, plus les quatre sections du protocole d'itération (garde CI).

## 2. État OpenSpec au 2026-11-03

| Élément | État |
|---|---|
| Specs vivantes (`openspec/specs/`) | `mobile/feature-migration-map` seulement (inventaire MOB-00 + garde d'exhaustivité) |
| `android-pilot-readiness` (PLAT-01) | mergé, **non archivé** — attend le retour du testeur ; porte `mobile/android-platform`, `mobile/internal-distribution` |
| `native-navigation-shell` (MOB-01) | mergé, **non archivé** — attend la passe iPhone (tâche 4.1b) ; porte `mobile/navigation-shell` |
| `session-native-integration` (MOB-02) | proposal écrite, **en attente de relecture** — branche `sb/mob-02-session-native-integration` |

Tant que les deux changes mergés ne sont pas archivés, leurs exigences ne figurent pas dans `openspec/specs/` : les
lire dans `openspec/changes/<change>/specs/`. `openspec archive <change> --yes` fusionne les deltas ; vérifier
ensuite que l'archive n'a rien laissé hors de `openspec/changes/archive/`.

## 3. Carte des contrats de données

| Contrat | Source de vérité | Garde aujourd'hui |
|---|---|---|
| Schéma de base | migrations Alembic (additive-only) → `data/schema_snapshot.sql` | `scripts/check_schema_snapshot.py`, dérive Alembic, gardes de migration (CI) |
| API mobile `/api/mobile/v1` (11 routes : auth, mission, séances, séries, substitution, fin, abandon) | `app/routers/mobile_api.py` | `tests/test_d9_mobile_sessions.py` (comportement ; présence des routes lue dans l'OpenAPI servi) — **aucun instantané du schéma des corps** |
| Types du client | `clients/mobile/src/api/types.ts`, `src/api/http.ts` | jest ; **aucun lien mécanique avec le schéma serveur** |
| Journal et outbox locaux (SQLite) | `clients/mobile/src/storage/{journal,journalTypes,outbox,serial}.ts` | `outbox.test.ts`, `serial.test.ts` |
| Synchronisation | `clients/mobile/src/sync/{syncEngine,reconcile,routes}.ts` | tests jest jumeaux |
| Domaine de séance (réducteur, horodatage D11, minuteur) | `clients/mobile/src/domain/{workout,performedAt,timer}.ts` | tests jest jumeaux |
| Décisions de navigation | `clients/mobile/src/native/{shellNav,backAction}.ts` | tests jest jumeaux |
| Pixel | fixtures `clients/mobile/src/ui/contract/` → 77 baselines `clients/mobile/visual-contract/baselines/` | `visual-contract/run.sh test` (CI, image Docker épinglée) |
| Provenance des assets | `design/auren/AUREN_ASSET_PROVENANCE.md` | `tests/test_auren_asset_governance.py` |
| Fonctions du web → destination native | `openspec/specs/mobile/feature-migration-map/inventory.yaml` | `tests/test_native_feature_migration_map.py` (toute route servie est inventoriée) |

## 4. Tests et gardes

| Commande | Ce qu'elle garde | Quand |
|---|---|---|
| `python scripts/check_scope.py` | le tier de risque du diff et les vérifications locales suffisantes | avant toute vérification locale |
| `python scripts/check_spec_protocol.py` | verdict des rapports, non-goals des specs, gabarits, registre | tout tier |
| `openspec validate --all` | structure des changes et specs OpenSpec | tout change OpenSpec |
| `npm --prefix clients/mobile test` + `npx --prefix clients/mobile tsc -p clients/mobile --noEmit` | la logique et les types du client | toute modification mobile |
| `bash clients/mobile/visual-contract/run.sh test` | 77 baselines au pixel | toute modification visible |
| `bash scripts/run_local_sweep.sh` | la suite Python par lots, mémoire bornée | doute de rayon d'impact (jamais `run_ci_pytest.sh` sur le poste, jamais `-n auto`) |
| CI de PR (3 shards pytest, lint, contrat visuel, Sonar) | la non-régression globale | **source de vérité** |

## 5. Leçons déjà payées (exportées de la mémoire de l'agent précédent)

**Mesurer le bon objet**

- Le répertoire courant de l'outil shell peut être l'arbre principal, et l'installation éditable y épingle `app` :
  un script lancé « depuis » un worktree mesure l'autre arbre. Se placer explicitement dans le worktree ; vérifier par
  `python -c "import app; print(app.__file__)"`.
- Le venv local n'est pas forcément le lock (FastAPI 0.135 local contre 0.141 en CI) : une garde verte localement peut
  être rouge en CI.
- Un filtre `-k` n'est pas un sweep ; un `| tail` sur un sweep remplace son code de sortie ; un chemin relatif dans un
  `.ini` suit le `cwd`.
- Un sweep parallèle saturé rend de faux échecs : rejouer en série avant d'accuser le produit.
- Une PR sans aucun run CI : `mergeable = CONFLICTING` → merger le canonique ; `CLEAN` → pousser un commit.
  `paths-ignore: docs/**` ne vaut que pour le push : une PR docs reçoit la CI complète.

**Des gardes qui gardent vraiment**

- Une garde qui construit elle-même l'état qu'elle observe, qui exige le défaut, ou qu'aucun code n'appelle, ne garde
  rien. Planter le défaut d'origine pour prouver qu'elle mord.
- Chercher les sœurs d'un défaut par classe (AST), jamais par nom : une garde corrigée sur 16 sœurs a été vue.
- `monkeypatch` par chaîne peut patcher une autre génération d'un module que la fixture a purgé de `sys.modules`.
- Inverse : une garde statique qui trouve beaucoup de coupables accuse souvent du code sain — vérifier une accusation à
  la main avant de la publier.
- Sonar : localiser la règle et la ligne avant de toucher au code ; ne jamais adjuger un lot de constats « jumeaux »
  sans les lire un par un (sur 4 « faux positifs évidents », un était un vrai bug).

**Explorer sans se tromper**

- Une exploration de code se trompe souvent : 29 corrections sur 60 affirmations mesurées. « Toutes » / « aucune » et
  un grep négatif sur un seul fichier sont suspects ; vérifier chaque affirmation qui fonde une décision.
- Un labo non représentatif fait conclure faux : noms tirés du vrai catalogue, valeurs qui varient, cas discriminant
  semé, et la boucle fermée (l'utilisateur suit le conseil) comparée à la boucle ouverte.
- Avant d'écrire une pièce, chercher celle qui existe déjà, et pourquoi elle n'a pas été prise (exemple de cette
  reprise : le patron « instantané figé + script de vérification » existe pour le schéma de base ; il manque pour
  l'API).

**Interface**

- Rendu réel montré à l'opérateur **avant** tout commit ; montrer des écrans entiers, pas des recadrages ; quand un
  compteur contredit une capture, c'est le compteur qui a tort.
- Une information, un seul porteur : la marque ou le mot, jamais les deux.
- L'absence n'est pas une affordance : un fait absent n'a pas de ligne ; un état vide représente le domaine et offre
  au plus une action.
- Réduire sans perdre l'ADN validé ; jamais une soustraction seule.
- Une décision s'applique à toute la classe de surfaces, pas là où c'est commode (les surfaces sociales sont celles
  qu'on oublie).
- Une baseline transforme ce qu'elle capture en contrat : ne geler que les surfaces souveraines.
- La cible tactile de 44 est un standard produit, pas une exigence WCAG (24 × 24 avec exception d'espacement).
- Tout nouvel écran est mobile (`clients/mobile`) ; l'app tutoie ; AUREN-MARK-V1 n'est jamais redessinée (dessins
  optiques 32 / 16 / 12) ; une zone BodyMap se dessine en `system`, jamais en `signal`.

**Domaine et sécurité**

- Ne rien inventer : bornes, charges de départ, récupération, anatomie, scores, recommandations. Le moteur
  scientifique V2 fixe le modèle de décision avant toute curation du catalogue.
- `exercise_properties` est le registre de substitution : y ajouter une entrée crée des arêtes pour tous les exercices
  de même motif et zone.
- Un formulaire partiel suit le contrat « soumis → écrit, absent → inchangé, vide → effacement explicite » (une
  violation a perdu des données en production).
- bcrypt borne à 72 **octets** (pas caractères) ; bcrypt 5 est incompatible avec passlib — ne pas merger la montée
  tant que passlib n'est pas remplacé.
- Aucune image sous `docs/` (hors `uiv3`) : une garde CI la refuse. Tout asset tiers est déclaré dans le registre de
  provenance et sa notice voyage avec l'app.

## 6. Ce qui manque pour un spec-driven complet (propositions, chacune = un change OpenSpec relu)

1. **Garder une seule couche de spec.** OpenSpec + les contrats canoniques suffisent ; un second cadre (Spec Kit,
   Kiro…) en parallèle créerait deux autorités. Un outil supplémentaire ne s'ajoute que par un change de
   gouvernance accepté par l'opérateur.
2. **Brancher OpenSpec sur l'agent.** `openspec init --tools codex` configure les commandes de l'agent : le lancer sur
   une branche, relire le diff, ne laisser aucun fichier de contrat (`CLAUDE.md`, `AGENTS.md`, `openspec/config.yaml`)
   réécrit sans revue.
3. **Figer le contrat de l'API mobile** (change `mobile-api-contract` proposé) : instantané versionné de l'OpenAPI de
   `/api/mobile/v1` (même patron que `data/schema_snapshot.sql`), vérification CI de la dérive, et types du client
   vérifiés contre lui — générés (`openapi-typescript`, dépendance de développement à faire accepter) ou comparés.
   Les tests de propriétés à partir du schéma (Schemathesis) peuvent suivre.
4. **Tracer exigence → test** : chaque `Scenario` OpenSpec cité par au moins un test (`// spec: mobile/navigation-shell
   › Retour depuis la racine de PROFIL`), et une garde qui liste les scénarios sans test — c'est la limite « pas de
   lien spec ↔ code » déjà notée au §14 du protocole v1.
5. **Rendre les specs vivantes** : archiver `android-pilot-readiness` et `native-navigation-shell` dès que leurs tâches
   restantes sont faites (ou les reporter dans un petit change de suivi), pour que `openspec/specs/` décrive le produit.

**Définition de fini d'un change** : proposal relue → deltas `WHEN / THEN` → tâches → `check_scope` → tests + gate
visuelle → rendu montré (UI) → rapport (§3, §5.2, quatre sections UI, verdict) → ligne du registre → PR → CI + Sonar
→ merge → closeout → archive.

## 7. Décisions ouvertes, à demander à l'opérateur

- MOB-02 : relecture de la proposal ; D-MOB02-1 (bilan : lectures serveur ou report) ; D-MOB02-2 (écran de démarrage).
- Politique d'archive des changes mergés aux tâches restantes (archiver maintenant + change de suivi, ou attendre).
- `AGENTS.md` : le remplacer par un pointeur vers `CLAUDE.md` et, éventuellement, le versionner (autorisation
  explicite requise par `CLAUDE.md §4`) ; trailer de commit pour un agent autre que Claude.
- Suppression du worktree jetable `workout-session-tracking-mob01-spike` (modifications non commitées).
- Identifiant d'app définitif avant tout upload Store.
