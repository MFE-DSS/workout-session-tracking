# Today / MISSION — preuve native avant décision pixels

## Brainstorming / Options / Risques / Choix retenu
Host seul aurait laissé READY inchangé. Le cockpit continu est autorisé par « Autoriser le scope, l’amendement et G1 », après le choix « Préparation dans le même instrument ». Risques : détourner une priorité propriétaire, inventer une composition complète ou masquer une commande. Choix : nouveau renderer purement présentatif, ports et priorités conservés, détails dépliables et footer hors contenu défilant. Aucun moteur, transport ou stockage nouveau.

## Croquis validé
UX_BOARD.md et AUTHORIZATION.json de today-mission-cockpit, décision du24novembre2026. Une seule composition : identité reçue, structure factuelle, BodyMap canonique, raison exacte, préparation du premier mouvement dans le même objet et action constamment disponible. Le GO G1 ne vaut pas acceptation des pixels.

## Inventaire — une information, une seule fois
| Élément | Source | Doublon ? |
|---|---|---|
| Nom proposé | HistoricalMission.template.name | non |
| Comptes | scope.exercise_count/work_set_count | non |
| Fenêtres anatomiques | zones, presetForZone ; codes inconnus omis, doublons retirés | non |
| Raison dominante | reason.phrase contextualisée au modèle si nouveauté ; trace exacte dans les sources | présentation et trace explicitement distinguées |
| Sources/limites | reason.reasons hors phrase déjà présente ; limiting non déjà porté par ces raisons ; provenance/horizon seulement reçus | non |
| Préparation | scope.first_exercise.name/set_scheme, sans composition complète ni matériel inventé | non |
| Reprise | payload.session.id/name, position facultative du même compte | non |
| Inconnu | currentOpening.kind seulement ; aucun ancien nom ou identifiant injecté | non |
| Action | callbacks existants et primary_action ; garde busy/single-flight inchangée | non |

## Comparaison avec la référence validée
MissionScreenV1 et quatre références complètes conservées, ainsi que DA08, BodyMap, mark, D4, NumericReadout, Frame C et RecessedWindow. Avant/après du vrai ConnectedApp Android local, mêmes projections canoniques synthétiques. Les contre-exemples de très longs noms/grands comptes sont explicitement des entrées de test de layout, séparées des vrais comptes du scénario principal. Aucun fait de rétablissement musculaire ni intensité.

## Changement unique de l’itération
Le cockpit Today conserve la continuité entre situation, préparation et commande. Préparer ne crée aucune demande, ne confirme rien et ne change pas d’écran. Le nouveau footer maintient Démarrer/Reprendre/Vérifier, selon le port déjà servi. Les raisons restent consultables mot pour mot. Une information manquante ne devient ni zéro ni permission.

## Revue et corrections bornées
Une revue indépendante du diff entier : zéro Critical, un Important de reflow à police normale (nom long/compteurs), zéro Minor. Réparation dans le composite local, aucune primitive modifiée ; preuve Android RED→GREEN conservée. Un défaut constaté nativement faisait ouvrir la préparation sous le fold : le dépliage fait désormais défiler le contenu jusqu’à la préparation, footer conservé. Deux gardes RED→GREEN évitent répétition d’une limite déjà citée et fenêtres répétées pour une zone. Les éléments non jugés par le reviewer (équilibre/focus/insets/pixels/physique/QA signée) gardent leurs preuves/gates distincts ; aucune seconde revue des correctifs prétendue.

## Vérification et limites
Source parent224ea54, B/closeout440/441 livrés avec CI canonique45489781273 verte. Aujourd’hui : travail non committé jusqu’à décision pixels ; tests locaux et native evidence décrits dans ENGINEERING_READINESS.json après acquisition. Tier minimal du script ISOLATED ; vérification élargie aux consommateurs partagés (suite mobile entière et backend mission/start/HTTP), sans full sweep backend local. Les77visuels protègent les références existantes, pas l’acceptabilité artistique du nouveau cockpit.

Le timeout Jest observé pendant la campagne nocturne est conservé, pas renommé PASS. Les traces macOS attestent plusieurs cycles veille/réveil ; la causalité exacte du timeout n’est pas certifiée. Le même test est rejoué sans modifier le timeout ou la source ; son résultat frais et celui de la suite entière sont consignés séparément. Les erreurs ADB transitoires et captures prises pendant le rechargement ne servent pas de captures finales.

Aucun APK/OTA/déploiement ni donnée personnelle. La cible QA signée/TIME01 reste intacte ; cette preuve utilise uniquement l’application de revue locale. Recette physique et gestes TalkBack exhaustifs non déduits de l’émulateur. Le footer D4 à très grande fonte et les labels BodyMap verrouillés restent qualifiés par les captures, sans rebaseline silencieuse.

## Ajustement natif de continuité
Le premier dépliage corrigé rendait le mouvement visible mais faisait défiler le nom de séance hors champ. L’identité READY a donc son unique porteur hors du contenu défilant, dans le même châssis ; valeurs et sources restent dans le contenu. Ce correctif ne change ni source, ni commande, ni primitive. Les captures FINAL_READY/FINAL_PREPARE constituent les pixels soumis, pas les captures intermédiaires.

## Résultats frais du25novembre
140suites/1607tests mobiles +TypeScript PASS sur source finale ;107backend ciblés/broad et55gardes PASS ;77visuels dans l’image CI épinglée PASS sans rebaseline. Budget259≤548, protocole/OpenSpec strict et Gitleaks candidat PASS. Zéro nouveau Python : Ruff neuf non applicable. La trace timeout nocturne reste conservée ; rerun ciblé7PASS puis suite finale1607PASS, sans relever le timeout.

Le bandeau source Programmes était rendu hors du châssis, blanc sur blanc et sous la barre système. Sa seule instruction existante passe maintenant par un slot présentatif du Host ; ni localOpening, ni priorité, ni source, ni commande ne changent. Le test consommateur Library vérifie toujours ce message, et la preuve native RED→GREEN conserve l’intention inconnue après Retour/réouverture.

## Revue sémantique opérateur du25novembre — avant code
Direction conservée, pixels toujours NON_ACCEPTÉS. Options : réécrire le moteur (hors scope), inventer une nouvelle projection physiologique (interdit), contextualiser les libellés reçus dans le même composite (retenu). Risque : « Jamais fait » concerne le modèle de séance, pas ses groupes musculaires ; « mesurée » est un état de cartographie du moteur, pas une mesure de récupération. Le KPI historique n’exige pas une série de travail accomplie : ne pas transformer absence de passage terminé retenu en preuve d’absence de travail musculaire.

Le défaut d’explication de couverture sans base de comparaison est identifié séparément par SCI-READINESS-00. Le texte hérité reste traçable dans les sources, qualifié explicitement, sans modifier le moteur ni son classement. Le DTO ne porte pas les deux bornes datées : aucune borne inventée. La fenêtre algorithmique est [now−14jours,now), basée sur started_at des séances retenues et leurs séries de travail complétées, pas sur une mesure physiologique ni sur performed_at qualifié TIME01.

PushA/delt_post provient du mouvement canonique Écarté arrière d’épaule câble (reference_split + EKB), pas d’une quatrième fenêtre ajoutée par l’UI. Assets radiographiques transmis : référence de matière appréciée, aucun nouveau mannequin ni remplacement du BodyMap autorisé ici. Le paquet pixels précédent reste conservé ; nouvelle soumission limitée au delta sémantique.

### Résultats du delta sémantique
Deux témoins initiaux RED→GREEN, puis un Important de revue sur le suffixe partiel corrigé RED→GREEN ; trace brute alternative conservée. Revue additionnelle limitée à cette nouvelle demande, pas une prétendue certification des pixels. Suite finale140suites/1610tests et TypeScript PASS ; protocole et OpenSpec strict PASS. Les107backend/55gardes/77visuels précédents restent conservés, non renommés comme une nouvelle campagne.

Natif : quatre profils exécutés dans ConnectedApp local, mêmes template/scope/zones/raison vérifiés par lecture HTTP fraîche et sourcehashes. Défilement réel pour atteindre les sources ; préparation et Démarrer accessibles. Les erreurs de pilotage (casse du label, contrôle hors viewport, attente d’un texte sous le fold) sont conservées et distinguées d’un défaut métier. Aucun POST métier ; aucune modification de QA signée. D4 très grande fonte et labels BodyMap gardent leurs limites héritées. Nouveau paquet AUREN_MISSION_SEMANTIQUE_2026-11-25, cinqplanches/diximages avec sources ; ancien paquet intact. Pixels toujours PENDING, aucun commitUI.

## Acceptation opérateur du25novembre et livraison
**« ACCEPT des pixels MISSION corrigés présentés le 25 novembre 2026 pour le périmètre sémantique et la composition native Android examinés. »** Reçu PIXEL_ACCEPTANCE_20261125.json, ZIP dd9a74c1020b6e95e36d27a26e27f5b3c865765aaffe379a560ddd02deabf8d7. Les quatre sources produit sont inchangées depuis ces pixels. L’ancienne soumission demeure historique, pas acceptée rétroactivement. Réserves : reflow LOCKED/grandefonte sans conformitéglobale, TalkBack exhaustif/physique ouverts ; « déjà bien servi » non admis scientifiquement ; aucun score/récupération/release.

Dernière revue indépendante du diff produit complet :0Critical/0Important/0Minor produit ; un Important de réconciliation documentaire (reçus, contrat§25, registre) corrigé ici sous le GO acquis. Les deux revues précédentes et leurs corrections restent conservées ; aucun nouveau défaut produit ni variante n’est introduit.

Relecture des décisions avant commit (registres lus sur le parent effectif) :

| Décision | Verdict sur ce diff |
|---|---|
| HOME D1 interactivité | Respectée via contrôles existants, cibles48dp et état ouvert, une action dominante. |
| D2 origine déterministe | Respectée, raison et trace système ; aucune revendication IA. |
| D3 couleurs / D4 suppressions / D5 substitution | Legacy visual references pour mobile selon ADR ; tokens mobiles et BodyMap canoniques conservés. |
| D6 cycle sans calendrier | Respectée : aucune semaine/programme actif inventé ; nouveau producteur de récupération hors scope et dépendant SCI. |
| D7 régularité | Non concernée : aucun streak ou nouveau score ; mémoire Progrès déjà livrée inchangée. |
| D8 Progrès | Respectée : quatre onglets existants, analyse exhaustive non déplacée dans Today. |
| D9 pas d’anticipation | Respectée : pas de séance N+2 ou durée/permission inventée. |
| Surfaces Q1 connexion | Non concernée, auth et écran inchangés. |
| Q2 barres de récupération | Non concernée comme producteur web ; aucun nouveau signal admis dans MISSION, audit SCI00 distinct. |
| Q3 état du jour décommissionné | Respectée : aucun questionnaire1–5 réintroduit et aucune dérivation nouvelle. |
| Q4 ligne de série / amendement É1/S1 | Non concernée : instruments Action/UX11-C inchangés. |
| Q5–Q8 rangs/typo/ambre/opacité | Supersédées pour le mobile par ADR ; contrôles et tokens mobiles existants réutilisés, aucune géométrie LOCKED changée. |
| Tokens bleus / origine système | Respectée selon tokens mobiles ; bleu pour raison du moteur, ambre pour action courante, aucune couleur physiologique. |

Contrats DA08, marque/D4, BodyMap, NumericReadout, FrameC/RecessedWindow et CalibrationRail : sources inchangées. L’amendement§25 se limite au nouveau consommateur approuvé. Les réserves opérateur ne sont pas renommées conformité globale.

Contrôles frais après acceptation, parent0d4fcfa :140suites/1610mobiles+TS,34backend ciblés/broad et69gardes,77visuels en image épinglée, OpenSpec33/33/protocole/Gitleaks PASS, budget259≤548. Le premier appel budget ne trouvait pas Ruff dans PATH ; même script relancé avec le venv existant, PASS sans changer code ni seuil. Aucun full sweep backend local. Les107backend/55gardes précédents restent une campagne distincte.
