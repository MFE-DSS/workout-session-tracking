# PLAN-CAL-01 — reçu de préparation et de faisabilité

9novembre2026. **PREPARATION_COMPLETE / NO_GO_BUILD / G1_PENDING / NOT_ACTIVATED.**
Base et distant après fetch : `692d4c8e9af2dcdb5f912eff6b9fb2b158089c0c`.
Worktree /private/tmp/auren-plan-cal-01, branche spec/plan-cal-01, travail unique
local non committé. Aucune PR/push/merge/CI distante nouvelle pour cette passe.

## Ce qui est prêt

Delta OpenSpec complet (proposal/design/tasks/spec) pour le runtime mobile
existant, lease, tests consommateurs T01–18, board UX-CAL/source inventory et
décisions concrètes [GO BUILD/G1](DECISION_FOR_OPERATOR.md). Les fichiers et
interfaces à raccorder sont identifiés, pas un nouvel audit générique.

Le code actuel a été lu : worker/builder privés pilote, autorité/génération,
ledger/projection snapshot et guards evaluate/ack/start, adaptateurs/contrôleur
natifs et composition. Deux captures acceptées first-use/discovery effectivement
vues ; UI_REVIEW et receipt huit captures relus. Joint manifeste produit/science
V1.0 conservé comme référence précédemment choisie ; aucune seconde autorité
scientifique manquante inventée. Inventaire des worktrees relevé sans cleanup.

## Choix proposés et coût

Inventaire2 dans un nouveau bundle immuable, packaging de format1 conservé et
worker v2 attesté réemployant les opérations historiques. Une génération, pas
deux travailleurs d'admission concurrents. Contexte courant choisi explicitement
dans ledger, projection de vraie qualification guidée avant V3 ; histoire/
préoccupation/retrait conservés hors filtrage. Métadonnées runtime exactes à
capture/ack/start empêchent faux frais malgré mêmes pins V3.

Ces choix techniques de l'agent demandent le GO du nouveau scope. Aucun profil
SCI n'est réadmis, aucune source/hash historique réécrit et aucune table ajoutée.
Le mandat réel reste contrôlé sur données synthétiques isolées, hors activation.

## Revue indépendante

Lecteur frais /root/plan_cal_01_builder_review, distinct de l'auteur, a recoupé
les cinq documents centraux et le code réel : packaging/ancien worker/builder,
authorité/calibration/snapshot/évaluation/start, évaluateur/validateur des six,
contrôleur/décodeur/UI. Verdict exact : **nothing important left**.
Rapport hors checkout /private/tmp/auren-plan-cal-01-review-evidence/BUILDER_CHECK.md.
Aucune modification, suite de tests, admission ou preuve runtime revendiquée
par cette revue de faisabilité. Revues code/frontière SCI effectives restent
requises après le futur build et son bundle final.

## Contrôles réellement exécutés

check_scope : **DOCS**, uniquement Markdown et append SPEC_REGISTRY. Protocole
**PASS**, OpenSpec `--all --strict --no-interactive` **17/17PASS**, liens locaux
et `git diff --check` **PASS**. Sept sources de frontière comparées octet pour
octet à HEAD (builder/worker historiques, trois interfaces six SCI, deux fichiers
SDK V1) : inchangées ; preuve preserved-sources.json hors checkout.

Aucun test produit/cible/broad/full local, installation, scaffold fonctionnel,
migration ou nouvelle capture native. Les quatre CI historiques de SCI386/387
et les reçus PLAN379/380 sont des entrées déjà vérifiées, pas de nouvelles
exécutions de cette préparation. RTK.md recherché hors travaux grixis non liés,
absent ; règles AGENTS fournies/CLAUDE canonique/GO permanent appliquées.

## Reprise après décisions

Après A et B : plan inline/TDD, build dans le lease, vrais consommateurs HTTP et
app native contrôlée, rendu comparé/pixels soumis avant commit UI, checks tier,
revues/CI/merge gardé/canonique/closeout/cleanup sans question routinière. Une
nouvelle migration, changement SCI/CI ou primitive visuelle globale est hors lease.

Aucun critère PCAL-01..07, DATA, RELEASE ou MOB03 global déclaré PASS par cette
préparation. Le dossier local et le worktree sont conservés tant qu'ils portent
ce travail unique ; checkout opérateur61ca08c/ARCH/QA restent préservés.
