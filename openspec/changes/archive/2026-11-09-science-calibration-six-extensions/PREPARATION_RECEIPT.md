# Reçu de préparation — six rencontres de calibrage

9 novembre 2026. **PROPOSED / NO_GO_BUILD / NOT_ADMITTED / NOT_SERVED.**

Base canonique relue : `ba2dbbc892b47e86c738af1d083e9087a57ff2d9`.
Worktree propre à cette préparation : `/private/tmp/auren-sci-calibration-extension-preparation`,
branche `docs/sci-calibration-extension-preparation`. Aucun commit, push, PR ou
résultat CI nouveau pour ce dossier. PLAN #379/#380 et CI #381/#382 restent clos.

## Livrable concret

[Design](design.md), [décision proposée](DECISION_FOR_OPERATOR.md), proposal,
tasks, delta de spec et tests spécifiés ; [cas d'admission par réalisation](../../../../docs/science/sci-p02-initial-policy/calibration-six-extensions/ADMISSION_CASE.md)
et [frontière PLAN](../../../../docs/science/sci-p02-initial-policy/calibration-six-extensions/PLAN_HANDOFF_PROPOSED.md).
Le registre documentaire reçoit uniquement un ajout de proposition.

Le contrat encounter1.0.0 représente déjà les faits nécessaires. Le nouveau
scope proposé porte sur six procédures et leur autorité/évaluateur isolés :
aucun nouveau contrat, code fonctionnel, test exécutable, fixture positive,
registre admis, SDK, route ou donnée utilisateur n'est livré par la préparation.
Les deux notices constructeur ont été consultées en lecture seule hors dépôt,
avec URL et empreintes ; leurs exemples ne qualifient pas tout appareil ou G17.
Les références professionnelles RDL et l'étude RIR ont leurs limites explicites.
Cette lecture ciblée n'est ni revue systématique ni validation humaine du pilote.

## Revue indépendante

Lecteur frais distinct de l'auteur, accès direct aux contrats et helpers :
**aucun point important restant pour planifier après GO**. Il a vérifié la
distinction rehearsal sans réglage / familiarisation au réglage exact, les
gardes nouvelles autour des helpers historiques en lecture seule, l'admission
par réalisation, le pont réel sept épisodes/V3/ack et la frontière PLAN.
Rapport conservé dans `/private/tmp/auren-sci-calibration-extension-review-evidence/BUILDER_CHECK.md`.
Cette revue de faisabilité n'est pas la future revue SCI du bundle effectif.

## Contrôles de préparation

`check_scope.py` classe ce diff **DOCS** : contrôle protocole documentaire,
sans suites produit, broad ou full sweep local. Résultats réellement obtenus :
protocole **PASS**, OpenSpec `--all --strict --no-interactive` **16/16 PASS**,
liens locaux des neuf nouveaux Markdown **PASS**, `git diff --check` **PASS**.
Aucun résultat distant n'en est déduit.

Sept sources historiques ont été comparées octet pour octet à la base : **PASS**, dont
contrats/évaluateur/autorité du pilote, producteur/validateur V3 et client V1.
L'inventaire et les preuves restent hors worktree. Aucun install de dépendance,
lecture de secret QA, migration, test appareil ou opération de production.

## Frontière restante

Recevoir l'approbation du design et du GO BUILD scientifique isolé. Ensuite
seulement : plan d'implémentation, code/tests réels, revue SCI par réalisation,
preuve positive depuis les vrais évaluateurs et V3, revue code, CI et livraison
sous GO MERGE permanent. Un manque scientifique conserve son statut et son
responsable ; aucune admission personnelle, garantie de sûreté ou activation
n'est créée par l'approbation d'ingénierie.

Le travail unique reste local et conservé. Les préparations ARCH, l'ancien
checkout opérateur et les preuves QA demeurent protégés. MOB03 complet reste ouvert.
