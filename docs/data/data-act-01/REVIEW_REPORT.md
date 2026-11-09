# DATA-ACT-01 — rapport de préparation

9 novembre 2026 · branche `docs/data-act-01-controller` · base
`fe9f6e9beb585a271ae2c2726e338359057b9f58`.

## Mandat et résultat concret

Préparer les décisions du responsable, auditer les fondations en lecture seule,
compléter le périmètre par les copies PLAN et proposer les seules suites manquantes.
Livrables : [questionnaire D01–D09 / catégories C01–C11](CONTROLLER_DECISIONS.md),
[graphe PLAN](PLAN_COPY_GRAPH.md), [audit de réemploi](FOUNDATION_AUDIT.md) et
[delta OpenSpec](../../../openspec/changes/account-data-activation/proposal.md).
La proposition réservée antérieure est reliée, pas dupliquée ; append seul au registre.

## Brainstorming / Options / Risques / Choix retenu

Consigné avant les écritures dans [le point d'entrée](README.md) : réutiliser
account-data-activation, conserver DATA01–07 OPEN, un seul lieu de réponse.
Les documents historiques datés ne sont pas réécrits comme une politique actuelle.
Risques traités : oubli des copies PLAN, reconstruction d'une fondation existante,
confusion ack/consentement, prétendue restauration complète, politique tirée du
défaut logiciel, identité/URL inventées.

## Constats et manques

- Déjà présents : service de demandes isolé, capacité hashée/expirante, garde
  policy/proof, intention/retrait local, BodyConsent et historique corporel,
  ledger/snapshots/évaluations/commandes/bindings/observations PLAN, export JSON typé.
- Encore absents/non admis : décisions complètes du responsable, assessment DATA par finalité,
  début irréversible/exécuteur et preuve réelle, routes/migration workflow intégrées,
  identité stable/anti-réapparition serveur, contrat d'export compte PLAN complet,
  restauration typée/exclusion et inventaire de copies réellement exploitées.
- Le helper backup global construit JSON puis CSV ; le CSV refuse PLAN et les
  écritures suivent les deux constructions. Son existence ne prouve pas une
  sauvegarde PLAN exploitable. Le restore legacy refuse PLAN : protection existante,
  pas succès de restauration. Aucun de ces scripts exécuté.
- D01 a reçu une [réponse partielle de l'opérateur](CONTROLLER_DECISIONS.md#réponse-partielle-d01--9-novembre-2026)
  le 9 novembre 2026 : prise en charge personnelle du service à ce stade,
  formalisation envisagée ultérieurement. Identité légale publiable, coordonnées,
  entité formalisée, juridiction et public visé restent non établis. Les décisions
  D02–D09 et les catégories C01–C11 demeurent OPEN.

## Revue indépendante et delta de réponse

La préparation initiale a fait l'objet d'une revue indépendante **PASS, sans
finding**, avant la réponse D01. Source de ce constat : passation du parent
reçue le 9 novembre 2026 ; cette mention ne prétend pas que le delta de réponse
a été examiné par ce relecteur. La [citation exacte et ses limites](CONTROLLER_DECISIONS.md#réponse-partielle-d01--9-novembre-2026)
sont centralisées dans le relevé ; le présent delta synchronise son statut dans
le dossier et le registre, sans nouvelle question, code, commit ou push.

## Contrôles réels et preuves

Preuves locales : `/private/tmp/auren-data-act-01-review-evidence` ; sorties de
commandes, manifeste des sources et liste du delta. L'invocation littérale
`python scripts/check_scope.py` n'a pas démarré car `python` n'est pas disponible
dans ce shell ; même script exécuté avec `python3`, **exit 0 / DOCS** avant checks.

| Contrôle | Résultat réel |
|---|---|
| python3 scripts/check_scope.py | DOCS ; spec_protocol requis, broad/full/migration/ruff_budget sautés selon verdict |
| python3 scripts/check_spec_protocol.py | exit 0, protocole conforme |
| openspec validate account-data-activation --strict --no-interactive | exit 0, change valide |
| openspec validate --all --strict --no-interactive | exit 0 ; 17/17 changes/specs vivants validés |
| git diff --check | exit 0 |
| Liens Markdown locaux des fichiers changés | zéro cible absente ; sortie de relecture du delta D01 conservée dans les preuves (inclut le registre historique) |

Les sorties reflètent seulement cette préparation. Aucune CI distante, recette
appareil, test produit ou vérification d'un schéma déployé n'est revendiquée.
La CI réelle du futur HEAD de livraison appartient à l'intégration du parent ;
les documents OpenSpec sont hors `docs/**`, ne pas promettre le paths-ignore global.

## Verdict et frontières

**PREPARATION_READY_FOR_REVIEW / CONTROLLER_DECISIONS_OPEN / NOT_ACTIVATED.**
Pas de code/migration/secret/donnée personnelle, suppression, activation,
déploiement, nouveaux tests produit, commit, push ou PR dans ce mandat.
Les suites F01–F07 sont proposées avec gates ; aucune n'est un GO BUILD.
Le prochain arrêt utile concerne de vraies décisions du responsable, pas une
demande de réautoriser une préparation déjà mandatée.
