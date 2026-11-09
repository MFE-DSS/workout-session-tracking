# PLAN-CAL-01 / UX-CAL-01 — réalisation contrôlée

9 novembre 2026. Base canonique692d4c8 relue après fetch. GO BUILD et G1 reçus ; **pixels contrôlés acceptés : « Valider ces pixels contrôlés » ; publication/CI/merge à suivre au closeout**. Runtime réel non activé, aucun déploiement.

## Brainstorming / Options / Risques / Choix retenu

Inventaire1 seul ne sert que le pilote ; recopier SCI ou remplacer les hashes historiques casserait son autorité. Choix retenu avant code dans le design : inventaire2 parallèle et worker fixe attesté, mêmes contrats scientifiques et sept tables, même ledger propriétaire et même session/journal. Une seule interaction native est paramétrée par réalisation, contexte et unité. Aucun moteur, score, charge initiale, incrément, zone E7 ou migration ajouté.

## Croquis validé avant code

Opérateur : « Autoriser le build PLAN-CAL-01 contrôlé » et « Valider ce croquis UX-CAL G1 ». Parcours choix→contexte/setup→réglage/familiarisation exacts→essai/faits/motif→acceptation/réessai. Pause distincte du retrait. Le [board réel consolidé](../../../clients/mobile/visual-contract/review-receipts/plan-cal-01/index.html) conserve24captures natives brutes, les références existantes et leurs hashes ; receipt PIXELS_ACCEPTED sur décision explicite : « Valider ces pixels contrôlés ». G1 et réception des pixels restent tracés séparément.

## Une information, une seule fois

Source map : UX_CAL_BOARD.md et board rendu. Nom depuis catalogue attesté, unité depuis contexte SCI exact. Choix saisi dans le recess puis NumericReadout hors édition. Réglage réellement utilisé saisi séparément ou confirmé explicitement : aucune copie silencieuse du choix dans un fait. Disponibilité/préoccupation, complétion/succès/contrôle/gêne/motif/occurrence sont distincts ; UNKNOWN conservé. Le motif provient du ledger et n'est pas calculé depuis la complétion. Qualification provisoire, confianceLOW ; aucun optimum, sûreté médicale ou RIR mesuré revendiqué.

## Comparaison avec la référence validée

Références plan-v3-controlled du8novembre réutilisées sans régénération ; mark/tokens/FrameC/RecessedWindow/NumericReadout conservés. iOS26.3 dédié390×844pt et AndroidAPI36 dédié360/480dp, avec texte130%, réellement rendus. Le parcours connecté iOS machine a réellement acquis et accepté des témoignages synthétiques au serveur ; les autres vues utilisent le même présentateur de production dans un banc natif isolé avec vrais ports HTTP et décisions propriétaires. Ce banc n'est pas la seule preuve de câblage. Les états réseau sont des fautes de transport de test explicitement identifiées ; aucune fixture SCI positive servie.

Clavier décimal iOS réellement affiché (virgule/Done), focus et ordre AX observés. Pas de nouvelle animation. Clavier Android complet, retour système et lecture VoiceOver/TalkBack restent à la recette physique ; les captures et tests ne la remplacent pas. Les erreurs de configuration du banc (résolution Expo, module dev-menu indisponible dans ExpoGo, connexions de test répétées lors des changements de viewport) ont été corrigées hors produit. Les dernières captures viennent de sources rechargées ; aucun échec de ce banc n'est présenté comme une preuve scientifique ou un test produit rouge.

## Un changement par itération

Demande : « One Native Calibration Instrument, Seven Exercise Contexts ». Étendre le pilote aux six rencontres admises dans le cadre accepté, avec un présentateur commun réellement consommé par PlanV3FirstUseScreen. MISSION, compte, préférences, exécution et journal visuels préservés. Pas d'asset anatomique ou de science visuelle inventée.

## Fonctionnalité implémentée

- Inventaire privé `plan-calibration-inventory/2.0.0`, packaging existant1.0.0, worker v2 fixe : vrais loaders/évaluateurs/validateurs des extensions, pilote et V3 historiques délégués sans modification. Fermeture des fichiers et imports attestés, bytecode/untracked/symlink refusés, écritures pyc désactivées.
- Négociation explicite `X-Auren-Calibration-Inventory`, écho exact ; absence garde le pilote historique, inventaire non supporté refusé406, aucun downgrade vers six profils.
- Ouverture/sélection/acquisition propriétaire dans le ledger existant ; qualification courante recomputée avant projection du snapshot, sélection A/B et histoire des préoccupations/retraits conservées. Les épisodes C3 bruts restent des faits/replays historiques ; ils ne deviennent pas une qualification nouvelle sous inventaire2.
- Identité runtime/inventaire/package/génération capturée et comparée avant évaluation, ack, start et applicabilité. Capture factuelle possible sans autorité opérationnelle ; elle ne donne aucune permission et peut exiger une nouvelle capture.
- Brouillons complets par propriétaire/rencontre, occurrence réelle séparée de saisie, reçu d'essai exact qui ferme le formulaire même après réponse perdue. Réponse tardive, changement de compte ou action concurrente ne redonne pas d'anciennes instructions.
- Sept rencontres guidées réellement qualifiées alimentent snapshot→vrai V3→UNKNOWN/BUDGET_UNCERTAIN→ack exact→ELIGIBLE→commande existante→même séance possédée après réponse perdue. Journal RDL PER_IMPLEMENT conservé, jamais converti en masse externe totale.

Aucune nouvelle table, dépendance, API scientifique ou source historique réécrite. Client firstPlan V1, contrats SCI et baselines conservés ; l'inventaire parallèle n'est pas une version V4.

## Vérifications observées

TierSHARED_CODE : pas de sweep global local. Broad initial185PASS/2FAILsur187 ; les deux régressions de capture factuelle ont été corrigées puis rejouées2/2PASS, suivies de37tests des modules affectés et consommateurs PASS. Le broad initial et les reruns ne sont pas présentés comme un unique187/187final. Dernier ajout de provenance du motif : témoin RED→GREEN,1PASS.

Nouveaux tests de packaging :11/11PASS après format final, y compris six profils contre les vrais SCI et fermeture bytecode/fichiers. Parcours HTTP réel :4/4PASS, dont sept rencontres→V3→ack→séance→journal/recovery. Mobile final :70suites/773testsPASS ; TypeScriptPASS. Dernière correction de label du réglage réel : témoin RED→GREEN puis10tests d'écran et nouveau broad773PASS.

Ruff neufPASS, budget260≤548, protocolePASS, OpenSpec strict17/17PASS ; Bandit ciblé et Gitleaks passent aux instants de contrôle conservés. Le daemon Docker local est indisponible (socket docker.sock), donc le gate de comparaison dans son image pinée n’a pas été lancé localement. Aucun autre moteur de pixels ou baseline régénérée ne lui est substitué. Les contrôles du HEAD final, la CI réelle et son gate visuel obligatoire restent à observer après push. Aucun seuil/test/gate affaibli. Deux avertissements de dépendances Python et avertissement expérimental SQLite Node conservés.

## Revues et limites

Revue interface SCI et revue code fraîches, distinctes du builder. Quatre Important SCI et trois Important code ont été vérifiés et corrigés avec régressions RED→GREEN ; détails dans [REVIEW_AND_VALIDATION](REVIEW_AND_VALIDATION.md). Les corrections tardives issues du parcours natif (instructions périmées, valeur réellement observée, réglage réel distinct, reçu de brouillon, libellé accessible) sont vérifiées par les tests du consommateur et le broad, pas revendiquées comme une nouvelle revue indépendante du dernier SHA. Aucun nouvel audit scientifique/clinique.

Deux mineurs explicitement différés : liaison croisée plus stricte entre profils/inventaire/DTO décodés côté client ; aide avant ouverture et projection du protocole vers les seules sections applicables. Le serveur actuel fournit les profils cohérents et conserve toutes gates ; ces limites doivent être reprises avant élargissement/exposition.

## Dépendances et frontière de clôture

CI exacteHEAD, readiness/revues GitHub puis PR/merge/canonique/Sonar/closeout/cleanup restent à accomplir. DATA/finalités/consentements/copies/effacement, activation et distribution restent séparés. Android/iPhone physiques et GO déploiement distincts. MOB03 complet reste ouvert ; aucun succès de navigation ou de calibrage n'est un premier plan universel.

## Reçu de publication du code

PR388 fusionnée e6bca39387864eac8c1a9e5038d0710d0d365858 depuis HEAD05915e5.
CI PR42618931040 completed/success11jobs :8068backend/3skip,773mobile+TS et
77visuels ; les deux fichiers nouveaux passent isolément. SonarPR ERROR
consultatif,4smells/0bug-vuln-hotspot,coverageapp92,5%/nouveau63,1%.
Le [CLOSEOUT](CLOSEOUT.md) et le reçu vivant suivent canonique/maintenance/cleanup ;
la suite de livraison n'est pas encore prétendue terminée à ce point de publication.
