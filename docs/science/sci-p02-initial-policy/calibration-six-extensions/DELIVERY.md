# Livraison SCI — six rencontres de calibrage

9 novembre2026. **LOCAL_VERIFIED / REMOTE_PENDING** à rédaction. Publication
scientifique **ADMITTED_WITH_LIMITS / ACTIVE / NOT_SERVED**, six réalisations,
aucune activation produit. PR/SHA/CI/canonique/closeout sont suivis dans le reçu
vivant de publication après leur observation ; aucun succès distant anticipé.

## Brainstorming / Options / Risques / Choix retenu

Le design approuvé choisit un lot cohérent de six procédures avec verdicts
séparés par réalisation plutôt que six cycles ou modification du pilote piné.
Le successeur isolé utilise rencontre1.0.0/C3/V3 et helpers purs read-only.
Coût assumé : une nouvelle autorité explicite et son futur raccordement PLAN,
pas un transfert implicite des permissions de l'ancien pilote. Revue des
procédures limitée à conventions opérationnelles conditionnelles, sans mesure
humaine de technique/sûreté ni charge personnelle calculée.

## Mandat et réalisation

GO opérateur9novembre : « Valider ce design et le build SCI isolé », dans
openspec/changes/science-calibration-six-extensions/BUILD_AUTHORIZATION.md.
Base canonique fetchée ba2dbbc892b47e86c738af1d083e9087a57ff2d9. Exécution inline
sous plan approuvé, branche feat/sci-calibration-six-extensions et worktree
propre /private/tmp/auren-sci-calibration-extension-preparation. Checkout opérateur,
préparations ARCH/QA et scopes PLAN/CI clos préservés.

Cinq modules nouveaux tools/science_calibration_extension : initialisation,
policy (publication stricte), evaluator (six profils et gardes), validation
(canonical recomputation/C3/exact-setting), artifacts (génération explicite hors
runtime). Aucun fichier fonctionnel existant modifié. Aucune dépendance ajoutée,
API/UI/SDK, packaging app, migration, CI ou baseline changés.

Les six procédures concernent chest press, rowing avec appui, RDL haltères,
tirage neutre G17, élévations latérales machine et mollets debout, sous leurs
références exactes V3. Cinq MACHINE_DISPLAY_KG ; RDL PER_IMPLEMENT bilatéral.
Aide sans épisode ni charge ; choix humain puis familiarisation exacte après
préparation/contexte/choix avant essai. RDL sans haltères reste préparation
facultative distincte, jamais0kg/BODYWEIGHT/essai de travail. Aucune charge,
incrément, durée ou règle de reprise après préoccupation inventés.

## Autorité et résultat réel

- Registre initial-calibration-extension-registry/1.0.0 ; politique
  initial-calibration-extension/1.0.0 ; moteur calibration-extension-evaluator/1.0.0.
- Échange first-calibration-encounter/1.0.0 et contrats V1/V2/V3 inchangés.
- Registre SHA256 a0c9a20a48490bb47272c7b8e03edc3b06ef4369e0eaf671bdd45eff39acb6ff.
- Bundle autorité 36c86a58ac4ae42776faa925a732fa0808002629aaa6278248ee5969ecf42406.
- Parent V3 bundle 78b3e5d99fe05093d6141678fd40f16e744b88d3d87405f14b0f8be357724d94.
- Fermeture de sources90fichiers vérifiés ;82sources historiques identiques
  octet pour octet à la base, aucun nouveau hash réécrit dans leurs publications.

Trente états issus des vrais évaluateurs/validateurs (cinq par réalisation),
plus pont réel des six épisodes et du pilote historique vers le vrai V3.
Le premier V3 est SCIENTIFICALLY_READY limité / BUDGET_UNCERTAIN / duréeUNKNOWN /
REQUIRES_TIME_ACK. Ack exact synthétique puis recomputation/validation : ELIGIBLE.
Les28séries de travail du plan V3 sont conservées ; calibration n'est pas travail.
Un épisode manquant ou ack altéré échoue sous les propres gates historiques V3.

Exports étiquetés REAL_EVALUATOR_SYNTHETIC_INPUT_NOT_SERVED et
REAL_EVALUATORS_AND_V3_SYNTHETIC_INPUT_NOT_SERVED, reproductibles, jamais importés
par produit/loader. Le40kg des entrées historiques est un fait synthétique de
test réutilisé, pas un réglage moteur proposé à l'utilisateur. Aucun fait réel
acquis, compte créé ou séance servie pour cette preuve isolée.

## Vérifications réellement exécutées

Tier check_scope **ISOLATED** : pas de full sweep local. **125tests nouveaux
passants** ; broad ciblé **747tests/21modules**, deux avertissements de dépendance
AnyIO/Starlette déjà présents. Ruff fichiers neufs PASS, budget260≤548 sans seuil
modifié ; Bandit nouveaux modules -ll PASS ; Gitleaks nouveaux outils/dossier
sans fuite ; protocole PASS et OpenSpec strict16/16. Exports reproduits et
invariance82sources historiques vérifiée. Checks distants restent à observer.

## Revues et correction

Revue SCI et revue code fraîches distinctes. SCI recommande ADMITTED_WITH_LIMITS
par réalisation comme convention conditionnelle, pas validation humaine ;
publication décidée après leur revue effective. Un Important code commun à la
chronologie SCI : contexte d'épisode plus récent ignoré par la familiarisation.
Reproduit18cas RED, corrigé par ajout de son temps d'occurrence aux prérequis,
18cas + témoin GREEN. Reviewer code vérifie indépendamment18refus et6témoins
occurrence ancienne/saisie tardive. SCI relit la correction et rétablit son avis.
Aucun Critical/Important résiduel, aucun mineur code différé. Le mineur de clarté
documentaire SCI est traité ici : les documents PROPOSED/NO_GO_BUILD sont leurs
instantanés de préparation ; autorisation et authority/ portent le statut effectif.

Rapports complets, empreintes, RED/GREEN et ledger conservés hors worktree dans
/private/tmp/auren-sci-calibration-extension-review-evidence/. Ces revues ne
certifient pas CI/GitHub/Sonar, production ou sécurité globale.

## Dépendances restantes et handoff

[HANDOFF.md](HANDOFF.md) fixe les interfaces réellement implémentées et les gates
d'acquisition/confiance du prochain PLAN. Son worker produit ne supporte encore
que le pilote historique ; aucune capacité des six n'est exposée par ce scope.
PLAN doit approuver son delta de raccordement explicite, acquisitions et gardes
A/B/ledger/idempotence, contexte/setup/familiarisation distincts et pixels requis.
DATA/finalités/consentements/copies/effacement et RELEASE/appareils/GO distinct
restent ouverts. Aucun nouveau GO BUILD ou déploiement n'est fourni par ce reçu.
MOB03 complet n'est pas fermé par la livraison de ce bundle SCI isolé.
