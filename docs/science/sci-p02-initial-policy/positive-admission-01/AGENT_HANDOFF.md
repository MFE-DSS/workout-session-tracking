# AUREN — passation SCI du contrat premier plan v2

7 novembre2026. **Compte rendu du périmètre de contrat explicitement autorisé, pas admission du premier plan.** Ce document sera complété avec les preuves de publication après vérification. Les reçus de PR portent les SHA et verdicts distants effectivement observés.

## 1. Mandat et point de reprise
L'opérateur a demandé de terminer le critical path exécutable de l'injection puis de fournir le CR complet à l'agent. Il a ensuite accepté le design par **« Valider le contrat v2 et ce build isolé »**. Cette autorisation porte sur types, schémas, validations, fixtures et tests ; elle conserve explicitement v1/FirstPlanClient, API/UI, registre historique et activation. Ce GO ne fournit pas une admission scientifique positive ni les preuves C3/C6.

Base de cette réalisation : `2cddf5da7d8c60bdc74e88ac60a24a36d9b45ad0`, canonique après les PR369/370 du durcissement et de l'admission négative. Travail isolé : branche `spec/sci-positive-admission-01`. PR fonctionnelle : [#371](https://github.com/MFE-DSS/workout-session-tracking/pull/371). Aucune reprise de #353 : le socle MOB03 est déjà fusionné et archivé selon GOV-MOB03-SPLIT-01.

**État fonctionnel : contrat exécutable, NOT_ADMITTED / NOT_SERVED / READY_NOT_PRODUCED.** Il n'existe pas de producteur émettant une recommandation v2 admise. Le producteur isolé historique2.0.0 continue d'émettre son enveloppe avec recommandation v1 et sans premier plan READY. Aucun état de diagnostic ou succès de test n'est promu en preuve positive.

## 2. Ce qui est désormais réutilisable
| Élément | Entrée/usage réel | Limite |
|---|---|---|
| `FirstPlanRequestV2` | Blueprint v1, sujet/snapshot/révision/as_of, versions, bundle, observations de calibration et de temps | Les refs de sujet/snapshot vérifient la cohérence ; PLAN doit encore authentifier et construire le snapshot autoritaire |
| `FirstPlanRecommendationV2` | Résultat typé, assessment, blockers sourcés, références d'autorité, candidate_plan et confiance séparée | Forme complète ≠ preuve d'admission ; aucun transport activé |
| `PlanV2` | Sessions/slots uniques, intentions et comptabilité des séries physiques, quinze zones qualitatives | Ni volume efficace individuel, ni crédit numérique, ni diagnostic de faiblesse |
| Prescription observée | Réglage typé, contexte/exercice/réalisation/appareil/côté, essai et acceptation exacts | Réglage provisoire à réessayer ; pas optimum ni vrai RIR mesuré |
| Prescription bootstrap | Phases familiarisation/essai/observation/décision et références d'arrêt/réessai/temps | Aucune instruction ou borne universelle n'est admise par la seule présence des champs |
| Durée | UNKNOWN, diagnostic conditionnel ou SUPPORTED sous base et portée explicites | READY garde une borne complète supportée dans le budget ; le diagnostic expérimental ne suffit pas |
| Validation d'échange | Bundle réellement piné et registre d'admission réellement vide | Profil courant négatif uniquement ; faux moteur/binding/READY refusés |
| Exports | Deux schémas JSON, neuf exemples non servis, manifeste source et manifeste d'artefacts | Pas de fixture READY publique ou d'autorité de test servant au produit |

Entrées de code :
- `tools/science_contracts/blueprint_first_plan_v2.py` : modèles, assessment réutilisé, empreintes et exports.
- `tools/science_contracts/first_plan_v2_validation.py` : cohérence de l'échange et références sur l'autorité disponible.
- `tools/science_contracts/first_plan_v2_fixtures.py` : génération/vérification explicite d'exemples, aucun moteur de prescription.
- `tests/test_science_blueprint_first_plan_v2_contracts.py` : tests structurels, échanges adverses et reproduction des artefacts.
- `docs/science/sci-p01-p02/v2/` : seuls nouveaux exports scientifiques ; les anciens ne sont pas remplacés.

## 3. Entrées minimales et gestion des inconnus
Le profil `first-bodybuilding-inputs/2.0.0` garde exactement les cinq familles requises : objectif hypertrophie, population adulte non clinique déclarée, séances/semaine, budget déclaré par séance, limitations déclarées. L'expérience peut être inconnue ; ni poids, ni taille, ni priorité facultative n'est ajoutée au manque nécessaire pour contourner une politique absente.

Les faits KNOWN/UNKNOWN/WITHHELD/CONFLICT conservent valeur, provenance, source et dates. Une priorité est une préférence ordonnée, jamais un point faible analysé. Pas d'inventaire d'équipement obligatoire, pas de salle complète supposée ; une possibilité d'exercice doit avoir sa source dans le contexte réel. Les déclarations historiques restent conservées dans le socle, sans réintroduire leur formulaire.

Les observations sont liées au sujet, à l'instant de décision et au contexte. Les importations historiques ne deviennent pas des commandes courantes grâce à leur seule date d'import. Un poids hérité sans date n'acquiert pas une date ; aucune nouvelle chronologie ou écriture corporelle n'est introduite.

## 4. Versions, empreintes et confiance
Versions proposées exécutables : `first-plan-request/2.0.0`, `first-plan-recommendation/2.0.0`, `first-plan-contract-artifacts/2.0.0`. Le Blueprint de faits reste `body-training-blueprint/1.0.0`, les zones restent `zones-15-v1`.

L'empreinte de requête v2 lie faits, sujet, snapshot/révision, as_of, versions et bundle. L'empreinte complète lie aussi les observations de calibration/temps. Réordonner des événements équivalents ne crée pas une décision différente ; modifier une observation change l'empreinte complète sans prétendre que les faits déclarés ont changé. L'ordre des priorités et des budgets par séance conserve son sens. Ces empreintes v2 ne sont pas renommées empreintes v1.

Les exports citent le vrai bundle historique et le vrai registre vide. Un hash identifie du contenu, il n'en prouve ni l'auteur ni l'approbation. Le futur adaptateur PLAN devra obtenir le snapshot propriétaire, le consentement pertinent, les versions supportées et le binding depuis des autorités distinctes du corps client.

Le profil d'échange actuel accepte seulement CONFLICTING_DATA, INSUFFICIENT_DATA ou POLICY_UNAVAILABLE selon les faits, et demande le blocker correspondant. Il n'existe pas de moteur v2 contractuel ; engine/policy/binding restent nuls dans ces exemples. Les statuts futurs READY/REVIEW_REQUIRED/CONSTRAINT_UNSATISFIABLE sont représentables mais ne sont pas validables comme sorties autoritaires sur le registre vide. Cela évite de renommer le moteur historique en prétendant qu'il a produit v2.

Un draft observé peut vérifier la cohérence de ses références et de la convention de dose partielle historique. Il reste DRAFT/POLICY_UNAVAILABLE. Les bases bootstrap, temps positif et projection conditionnelle G17 ne sont pas admises par ce validateur. Aucune borne temporelle synthétique, conversion d'assistance en kg ou contribution inconnue en zéro.

## 5. Vérifications et revue
Le reçu final relèvera le HEAD exact, les CI de PR et de merge et le verdict Sonar. Les preuves locales à cette étape couvrent les nouveaux cas et le broad ciblé scientifique/historique conformément au tier ISOLATED ; pas de full sweep local systématique. Les artefacts sont reproductibles depuis le vrai inventaire piné et sont validés par les modèles et la frontière d'échange.

Les revues code et cohérence scientifique sont séparées et fraîches. Elles évaluent ce contrat et ses frontières ; elles ne sont ni examen clinique, ni nouvelle preuve biologique, ni validation de temps réel. Les défauts importants sont à corriger avec reproduction RED→GREEN avant merge ; les mineurs seront explicités dans le reçu de clôture.

Aucune UI, baseline, source parent pinée, ancienne fixture, table ou migration n'est modifiée. Les contrôles visuels et mobile de CI restent applicables ; leur réussite ne constitue pas une recette physique. Aucune donnée QA privée, donnée de production ou collecte utilisateur n'a été nécessaire.

## 6. Gates scientifiques qui restent réellement ouvertes
| Gate | Acquis conservé | Pièce qui manque pour une admission positive |
|---|---|---|
| C1 — population | Périmètre adulte déclaré non clinique identifié | Décision explicite liée au bundle/version et à ses limites d'applicabilité |
| C2 — dose/allocation | Conventions partielles0.2.0 conservées ; cadences2/3, sept intentions auditées | Admission du bundle effectif et de son allocation ; ne pas présenter2→3 comme fréquence à volume égal |
| C3 — protocole initial | Calibration observée et sémantique courante durcies | Protocole opérationnel versionné, familiarisation/essai/réessai/acceptation/arrêt et son auteur/revue ; bootstrap sans charge connue et sa préparation couverts |
| C4 — candidats/réalisation | Curation40candidats et sept intentions, qualification G17 conditionnelle conservées | Binding des réalisations réellement sélectionnées et conditions de disponibilité/exclusions/substitution ; ne pas réouvrir quatre pulls non nécessaires |
| C5 — représentation | Choix v2 explicitement approuvé, contrat qualitatif livré | Admission de la projection/bundle consommé et revue des futurs consommateurs ; couverture15zones n'est pas exposition numérique exacte |
| C6 — temps | Diagnostic/arithmétique et protocole de collecte existants | Base positive applicable couvrant travail/repos/préparation/calibration/opérations : modèle validé ou convention produit bornée explicitement acceptée |

C3/C6 ne sont pas fermées par un nouveau test ou une constante choisie pour produire READY. Pour C6, la sortie actuelle reste **C : preuve insuffisante**. Le protocole `docs/science/sci-p02-initial-policy/admission-system-01/TIME_PROTOCOL.md` décrit les options : A modèle réel préenregistré/validé, B convention produit explicite avec hypothèses/limites, C blocage précis tant que les moyens/décisions manquent. Aucune donnée réelle ou convention chiffrée applicable n'a été fournie dans cette passe.

Les critères SCI-POS01..07 restent dans `docs/proposals/science-initial-policy-positive-admission.md`. Le contrat peut être livré et clôturé sans marquer ces critères positifs. Le parent scientifique reste ouvert ; une future admission exige son périmètre de réalisation et ses preuves, pas une réouverture de l'ancien build négatif.

## 7. Dépendances mobiles et produit, inchangées
| Voie | Suite nécessaire | Ce que ce contrat ne remplace pas |
|---|---|---|
| DATA01–07 | Décisions D-POL01–05, texte/traitement corporel pertinent, copies/restauration et mode de traitement réel, activation revue | Politique du responsable, API app/web d'effacement et preuve autoritaire DELETED |
| PLAN01–07 | Snapshot propriétaire/révision, négociation explicite v1/v2, adaptateur de confiance, vrai binding/producteur puis handoff idempotent vers séance possédée | Authentification, persistance, démarrage/reprise et absence de doublon |
| RELEASE01–06 | Cible/configurations/builds, compatibilité/rollback, GO distinct et Android/iPhone physiques | Tests de force-kill/SQLite, clavier/retour/accessibilité et verdict de release |
| MOB04 | Scope/résolveur/croquis puis pixels acceptés sur la référence verrouillée | Une nouvelle carte ou un fallback MISSION ne crée pas un premier plan SCI |

Le socle #353 reste livré. Le compte → premier passage explicite → préférences/Aujourd'hui fonctionne dans son périmètre accepté ; **MOB03 complet reste ouvert** tant que DATA/PLAN/RELEASE applicables ne sont pas acquis. MISSION historique démarrable et premier plan scientifique ne sont pas interchangeables.

Le worktree `auren-arch-po-packs-01` contient les préparations A–F et leur travail unique : le préserver. Les quatre autres scopes ne deviennent pas autorisés par ce GO SCI. Repartir du HEAD distant après fetch ; ni le fichier ouvert dans l'IDE ni une branche historique n'identifie à lui seul le canonique.

## 8. Prochaine injection utile à préparer par l'architecte
**Priorité : `SCI-P02-C3-C6-ADMISSION-PACK`.** Fournir les décisions/protocole réellement nécessaires, pas un nouveau squelette de refus. Le paquet doit nommer :

1. Auteur/reviewer responsables, versions et applicabilité du bootstrap C3 ; instructions utilisables, acceptation/réessai/arrêt et préparation réelle sans charge inférée.
2. Route C6 choisie A/B/C. Pour A : moyens réels, politique des observations, préenregistrement et validation indépendante. Pour B : hypothèses/valeurs/périmètre et limites explicitement acceptés par les responsables ; pas d'optimalité prédictive revendiquée. C conserve le blocage avec son propriétaire et les pièces manquantes.
3. Bundle exact C1/C2/C4/C5 et règle de retrait ; contrat v2 cité, sources historiques conservées. Les preuves ne viennent pas d'un label APPROVED ou d'un hash caller.
4. Scope de build séparé du binding/producteur et de ses tests, uniquement après revue du dossier. Premier READY depuis le vrai producteur si toutes gates sont acquises ; sinon refus explicite.
5. Fichiers SCI possédés, coordination PLAN, critères COMPLETE et déploiement séparé. Aucun changement FirstPlanClient ou schéma/backend partagé sans son delta approuvé.

En parallèle, le responsable complète B/D-POL01–05 ; l'architecte peut faire revoir le snapshot/commande PLAN préparé, en laissant le raccordement positif fermé. Ces décisions ne demandent ni secret Store, ni inventaire matériel, ni nouvelle DA.

## 9. Résultat à transmettre
Le prochain agent doit lire ce CR, le design/autorisation du change, les schémas v2 et leur générateur, le paquet READY_GATE_DECISIONS, le protocole C6 existant et les propositions SCI-POS/DATA/PLAN/RELEASE. Il doit conserver les décisions déjà reçues et traiter les preuves/décisions identifiées avant toute activation positive.

Le présent compte rendu ne contient pas de nouveau GO BUILD ou GO DEPLOY. La livraison finale de ce périmètre sera consignée dans le closeout avec PR/SHA/tests/revues/Sonar/cleanup effectivement observés.

## 10. Décisions d'exécution et limites de revue conservées
Ces décisions ont été consignées dans le ledger pendant la réalisation ; elles ne sont pas des admissions scientifiques :

| Décision | Motif | Risque/condition pour la suite |
|---|---|---|
| Exécuter le design approuvé sans nouvelle question de plan/merge | GO de contrat explicite et autorisation permanente versionnée | Toute extension substantielle requiert son delta revu ; aucun GO positif implicite |
| Réutiliser le vrai registre vide, sans second moteur/registre négatif | Éviter une autorité ou un chantier redondant | Aucun READY validable tant que le vrai successeur admis manque |
| Modèles/export et validation Pydantic plutôt qu'ajout de dépendance JSON Schema | Validateur indépendant absent de l'environnement/dépendances actuels | PLAN devra vérifier l'interopérabilité de son consommateur avant exposition |
| C1–C6/protocole/temps restent hors preuve de ce GO | Une réussite d'ingénierie ne prouve pas les conditions scientifiques | Ne pas brancher un positif sans leur véritable admission |
| Une forme READY hypothétique peut exister comme type | Définir le contrat successeur, sans fabriquer son autorité | Le consommateur devra obligatoirement passer par l'adaptateur de confiance ; registre courant refuse |
| Un DRAFT partiel décrit seulement des références cohérentes | Pas de producteur positif livré | Future allocation/cadence complète à vérifier avant READY ; jamais présenter ce draft comme premier plan |
| Interopérabilité indépendante laissée au scope PLAN | Pas d'API/SDK dans ce build | Absence de certification d'un futur client JSON Schema explicitement reconnue |
| Authentification/consentement/UI/biologie non certifiés | Frontière pure SCI isolée, sources privées non consultées | Aucun runtime sensible avant ses propres gates et son snapshot propriétaire |
| Readiness distante vérifiée par l'agent de livraison | Les reviewers n'ont pas certifié GitHub/merge | Fusion uniquement après contrôles du HEAD final et base courante |

Les revues fraîches n'ont pas relevé de mineur à différer dans ce contrat. Les dettes antérieures et le verdict Sonar consultatif restent distincts, sans faux effacement ni correction massive hors scope.
