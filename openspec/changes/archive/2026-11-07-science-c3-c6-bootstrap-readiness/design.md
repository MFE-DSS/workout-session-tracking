# Context
Base a572079, contrat request/result2.0.0 livré et non servi, vrai registre d'admission vide. Le producteur historique2.0.0 embarque une recommandation v1, pas le nouveau contrat v2. `_ready_shape` v2 exige SupportedDuration et upper≤budget ; la spec canonique l'impose aussi. Calibration1.1.0-isolated qualifie des réglages observés provisoires et garde les préoccupations ; elle n'ajuste aucune charge automatiquement. Le paquet reçu recommande Route B puis A et une séparation future de readiness, sans fournir encore ses autorisations produit ou une convention numérique.

# Goals / Non-Goals
Rendre le premier apprentissage possible sous un contrat honnête explicitement accepté. Préserver cinq faits requis, anthropométrie/priorités facultatives et absence d'inventaire. Représenter les inconnus temporels et d'effort ; empêcher toute autorité inventée.

Hors scope : code de nouveau scope dans cette préparation ; modification READY1/2 ou de leurs sources/pins ; moteur de durée personnel, nouvelle dose chiffrée, supersets automatiques, acquisitions privées, nouveau formulaire/UI/SDK/API, activation ou collecte. L'absence d'une borne de temps ne justifie pas de déclarer que toutes les séances sont impossibles.

# Brainstorming / Options / Risques / Choix retenu
1. Garder v2 et fournir une vraie borne temporelle positive, modèle ou convention complète admise : compatible avec l'existant ; aucune borne applicable n'est fournie dans la pièce. Cette route reste possible si le PO choisit de maintenir cette condition de démarrage.
2. Contrat v3 : séparer admissibilité scientifique, temps et permission produit d'exploration. Suit la recommandation §24–25 et évite de produire une fausse borne ; exige une décision produit explicite, de nouveaux validateurs et une négociation PLAN future.
3. Ajouter une enveloppe « scientifique ready » autour d'un résultat v2 POLICY_UNAVAILABLE : écarté, deux autorités contradictoires et risque de contourner le client existant.

**Choix proposé par l'agent : option2**, documentaire à ce stade. Ni l'approche ni le droit de démarrer un temps incertain ne sont déclarés déjà approuvés.

# Decisions
## D1 — Trois axes v3, sans READY v2 renommé
Noms proposés : `first-plan-request/3.0.0`, `first-plan-recommendation/3.0.0`. Blueprint v1 reste les faits ; observation/protocole successeurs versionnés si leurs champs changent. Éviter un READY global qui ferait disparaître le temps :

| Axe | Valeurs proposées | Autorité |
|---|---|---|
| scientific_readiness | SCIENTIFICALLY_READY / INSUFFICIENT_DATA / CONFLICTING_DATA / POLICY_UNAVAILABLE / REVIEW_REQUIRED / CONSTRAINT_UNSATISFIABLE | Binding scientifique complet sur bundle exact, pas simple forme de JSON |
| time_assessment | SUPPORTED / BUDGET_COMPATIBLE_BY_POLICY / BUDGET_TIGHT / BUDGET_UNCERTAIN / STRUCTURALLY_TOO_LONG | Source/politique temporelle applicable, inconnus et portée explicites |
| start_permission | DENIED / REQUIRES_TIME_ACK / ELIGIBLE | Politique produit admise et reconnaissance explicite liée au snapshot/plan/version |

PENDING/UNKNOWN/NOT_SERVED transport restent séparés. SCIENTIFICALLY_READY ne donne pas seul permission de démarrer. Le label ne certifie ni temps ni optimalité personnelle. Aucun résultat positif réel n'est généré dans cette préparation.

Par défaut sans politique produit applicable : DENIED, reason START_POLICY_NOT_ADMITTED. Ce défaut protège un futur scope de build ; ce n'est pas un nouveau moteur négatif à réécrire. V1/v2 continuent de refuser la nouvelle enveloppe. Aucun downcast en READY v2. La permission est évaluée depuis autorité, jamais depuis un `ack=true` ou label approuvé du caller.

## D2 — C6 sans temps inventé
Le budget est une contrainte. Le modèle v3 doit distinguer borne prédictive supportée, convention de planification admise et inconnu. SUPPORTED garde base/applicabilité/intervalle/provenances et couverture réelle travail/repos/préparation-calibration/opérations. BUDGET_COMPATIBLE_BY_POLICY exige une convention explicite applicable, ses hypothèses et limites ; sans celle-ci il est interdit de générer une compatibilité positive ou probabilité.

Pour structure traditionnelle séquentielle seulement, conserver le calcul existant de repos prescrits entre séries comme **borne partielle** R. S'il est prouvé que R > budget_en_secondes, cette configuration est STRUCTURALLY_TOO_LONG ; cela ne réfute pas tous les autres plans. R<budget ne fournit aucune borne haute : travail, préparation/calibration, opérations et attente restent inconnus. À R=budget, les repos consomment déjà tout le budget et le travail strictement positif reste à faire : la réfutation est valide sans inventer de seconde minimale ou epsilon. Cette frontière préserve l’oracle historique time_feasibility.py ; aucune modification de ce code piné. Unilatéral non appairé, structure inconnue ou supersets non admis invalident ce calcul simplifié ; ne pas soustraire les repos.

Sans convention chiffrée ou base positive, BUDGET_TIGHT n'est pas déduit d'un seuil de proximité improvisé, et BUDGET_COMPATIBLE_BY_POLICY reste indisponible. Le résultat est BUDGET_UNCERTAIN avec les composantes manquantes. Aucun coefficient par rep/machine/transition, marge ou taux de réduction en superset nouveau.

**Proposition produit à faire trancher :** autoriser l'exploration avec BUDGET_UNCERTAIN, uniquement si science/bundle/protocole sont admis, contexte sélectionné compatible, aucun blocage et reconnaissance explicite « durée non garantie » liée au plan. Si autorisée, un événement de limite utilisateur ne provoque pas d'accélération/repos raccourci ou de poursuite obligatoire : sortie/arrêt sûr, séance incomplète conservée, redistribution seulement sous politique admise ultérieure. Le moteur ne promet pas d'achever le plan dans le budget. Le comportement UI et les commandes de séance seront PLAN/MOB02 sous leur scope, pas réalisés ici.

Une horloge manquante, une app interrompue ou une pause ambiguë ne peuvent produire un « temps actif » exact. Conserver écoulé, phases couvertes et interruptions séparés, sans retrancher l'attente nécessaire. Route A reste le protocole empirique existant, soumis à politique DATA et validation indépendante ; aucun nombre d'observations ne promeut automatiquement le modèle.

## D3 — C3 : ce que le paquet apporte et ce qui doit être opérationnalisé
Machine proposée : NEEDS_CALIBRATION → FAMILIARISATION → ATTEMPT_OBSERVED → ASSESSMENT → ACCEPTED_FOR_RETRY ou RECALIBRATION_REQUIRED/REVIEW_REQUIRED. États successeurs séparés des cinq états historiques, sans réécrire leurs sorties. Une action proposée n'est pas un événement exécuté ni un SetLog de travail.

Avant essai : identité exacte sujet/exercice/réalisation/appareil/côté, capacité d'utiliser le dispositif confirmée et instructions propres à la réalisation connues. La valeur initiale vient d'un réglage réellement choisi/observé dans ce contexte, sans kg prédits/1RM/standards/transfert entre exercices. Si l'utilisateur ne peut choisir/manipuler un réglage avec contrôle, demander assistance ou substituer ; aucune charge minimale universelle ou garantie de sécurité n'est déduite de l'appareil.

Essai : consigner réglage/unité, répétitions, completion, cause d'arrêt si connue, qualité/gêne/succès et RIR facultatif avec provenance. L'import d'un ancien essai ne devient pas une acceptation courante. Préparation/essais séparés du travail prescrit et du budget temporel observé.

Évaluation : BELOW/WITHIN/ABOVE ne doit pas masquer une observation insuffisante. Reps seules ne prouvent ni effort ni charge trop lourde/légère : interruption ou arrêt volontaire hors cible → non évaluable pour cette causalité. Dans la plage prescrite et essai qualifié/acceptation actuelle, un réglage peut être provisoirement accepté sans RIR connu, en conservant effort inconnu ; cela ne signifie pas vrai2RIR. Les seuils d'une décision automatique « trop facile/difficile » et la tolérance autour de2RIR ne sont pas fournis, donc aucune règle numérique inventée. Le futur protocole doit préciser sa portée ou conserver la décision de réessai sous confirmation explicite de l'utilisateur.

Ajustement : direction suggérée seulement depuis observation qualifiée et politique admise. Réglages/incréments effectivement disponibles et ordre d'effort proviennent du dispositif confirmé ; aucune liste de matériel à gérer. Sans échelle/direction/unité connue : pas de prochain réglage numérique, demande de confirmation/substitution. Assistance, charge par implément, masse affichée et réglage non massique restent distincts ; « cran suivant » ne représente pas toujours un effort supérieur. Aucun pourcentage ou +kg générique.

Arrêt : préoccupation signalée, technique/gêne incertaine ou échec ne déclenchent pas une augmentation ou un retry automatique. REVIEW_REQUIRED et sortie/assistance/substitution, sans diagnostic médical. Aucun nombre universel d'essais, échec imposé ou promesse de prévention des blessures. Reprise après préoccupation exige une autorité/protocole spécifique, pas effacement du fait.

Recalibration : nouveau contexte/exercice/réalisation/côté ou substitution invalident l'identité de référence ; interruption/performance incohérente déclenchent revue selon faits sourcés. Aucun délai de « longue pause » ou seuil de « variation majeure » n'est fixé ici. Un historique ancien n'est réutilisable qu'avec qualification courante réelle. Les critères numériques supplémentaires et l'acceptation du protocole restent des décisions à versionner.

## D4 — Effort et confiance
RIR déclaré et cible comportementale sont séparés. RIR inconnu reste nul/UNKNOWN ; son absence ne devient pas un 2RIR mesuré. La confiance initiale LOW/UNKNOWN est une convention de représentation, pas une probabilité calibrée. Aucune montée automatique à MODERATE/HIGH à la sixième séance ou à un nombre choisi d'expositions. Toute progression de confiance nécessite des critères de comparabilité et une politique/proof admise ; l'apprentissage peut être absent ou non monotone. Confiance locale ≠ preuve de la dose globale.

## D5 — Binding et décisions formelles
Conserver les recommandations C1/C2/C4/C5 et leur portée limitée. C1 adulte déclaré/non clinique n'est pas aptitude médicale. C2 conventions actuelles comme départ, pas dose optimale/minimale ; cadence2→3 augmente le travail hebdomadaire si la séance se répète. C4 uniquement réalisations sélectionnées et conditions réelles ; candidats incertains non utilisés hors enquête. C5 rôle qualitatif PRIMARY/SECONDARY/MINOR/UNKNOWN canonique, sans conversion physiologique des noms DIRECT/INDIRECT du paquet ni crédit numérique inventé.

Le futur binding lie contrat/profil, blueprint, code/engine/policy, curation/pull/réalisation, protocole C3, politique temporelle/produit, preuves, sources/digests et retrait. Il doit aussi prouver quelles inconnues sont explicitement non bloquantes dans ce protocole. Aucun registre existant n'est modifié ou élargi ; le registre vide reste rejouable. L'auteur/reviewer et la décision d'applicabilité manquent encore pour transformer les recommandations du paquet en autorité exécutable. GO BUILD, admission et déploiement restent séparés.

## D6 — Séquence de build proposée, pas GO actuel
Étape1 après revue : contrat v3/protocole typé et oracles isolés, sans nouveau moteur négatif ; ancien v1/v2 et snapshots sources préservés. L'étape doit couvrir précisément la décision produit obtenue, et ne pas prétendre positif si cette décision ou l'admission du protocole manque.

Étape2 séparément autorisée après décisions formelles : véritable binding/producteur successeur, validation indépendante et fixture positive depuis le producteur réel si toutes gates du nouveau contrat sont acquises. Sans autorité, refus explicite ; pas de fixture synthétique promue. Pas de collecte ni moteur temporel personnel par inférence du GO.

Étape3 PLAN distinct : négociation déclarée, snapshot propriétaire/consentement pertinent, transport et commande de séance idempotente, reprise/limite utilisateur. Les pins historiques incluent le SDK ; définir les snapshots historiques avant tout changement partagé. Aucune modification simultanée de ces fichiers dans le scope SCI.

# Migration Plan
Côte à côte : anciens contrats inchangés, v3 non annoncé ni servi tant qu'aucun producteur/adapter admis n'existe. Aucune conversion automatique de status/readiness ou temps. Rollback futur : retirer le binding/port successeur, pas effacer faits ou historique ; pas de repli SCI depuis MISSION. Pas de migration DB dans ce scope.

# Open Questions
Décision opérateur sur optionv3 et build étape1 ; décision produit sur permission TIME_UNCERTAIN/ack/sortie à la limite ; admission formelle C3 et bundle exact avec responsables identifiés. Les références disponibles étayent la prudence mais ne prescrivent pas l'algorithme d'ajustement ni une borne de temps personnelle. Les seuils/marges/incréments inconnus restent inconnus.
