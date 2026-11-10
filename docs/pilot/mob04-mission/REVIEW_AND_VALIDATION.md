# MOB-04 — revues, décisions et contrat visuel

## Revue fraîche et corrections
Revue globale par lecteur frais : I1 issue legacy perdue puis GET négatif, I2 froid offline idle et lecture V3, I3 ancien snapshot11 vs séance999, I4 réponse execution11 tardive après999, I5 claimV3 vierge bloquant beginLegacy. Chacun reproduit RED puis corrigé GREEN dans son consommateur ; SQLite réelle pour claim et snapshot. Re-review limitée supplémentaire, déviation de la méthode inline documentée : deux résiduels (A tardif après cleanup sur B ; preuve négative oubliée après échec réseau) reproduits RED→GREEN. Broad mobile final1038PASS/TS. Aucun nouveau cycle de reviewer lancé et aucun avis final indépendant de ces deux derniers correctifs prétendu.

## Rulings I made
- Exécution inline, modules isolés pendant REL-03 puis lease partagé après merge : évite chevauchement, coût : raccordement attend livraison/base fraîche.
- Transport MissionAction fixe portant ses en-têtes négociés, distinct du transport V1 générique : coût un adaptateur local, aucune mutation du SDK historique.
- Host isolé d'abord, montage produit ensuite ; carte MISSION retournée directement sans wrapper/footer : coût vraie preuve consumer exigée en plus du banc.
- Marque de start inconnu/exclusion de reprise dans JSON local possédé existant : aucune commande serveur inventée ; coût blocage possible jusqu'à réconciliation, aucune suppression factuelle.
- V3 existant et pending legacy incompatibles gardent le refus SQL : coût réconciliation explicite, jamais effacement ou second journal.
- Visuel/physique/Expo Go : accepter seulement portée rendue, coût pas de prétendue app Android complète ou recette physique.
- Crash/reprise : namespaces et SQLite de test isolés, coût validation APK/appareil séparée.
- Full broad local ne remplace pas CI finale : coût attente obligatoire des contrôles requis.
- Seconde première séance, SCI nouvelle et MOB-06 hors scope : coût capacités futures non ajoutées.
- Pureté sans DML promise au nouveau GET ; capabilities historique peut conserver ses verrous : coût pas de fausse certification de tous GET existants.

## Deferred minors
M1 : l'orientation Today peut attendre refresh/foreground après sortie de PLAN créé, sans deuxième start possible. Limites AX/physique et Android Expo Go sont des gates de release déclarées, pas des PASS.

## Croquis validé
OptionB et famille dans UX_BOARD/PILOT_VALUE_SCOPE acceptées : « Autoriser MOB-04 et valider G1 ». Réponse pixels ultérieure : « Valider ces pixels MOB-04 contrôlés ». Receipt lie sources/captures au rendu. Aucun code UI committé avant cette décision.

## Inventaire — une information, une seule fois
| Élément | Source | Doublon ? |
|---|---|---|
| Orientation primaire et reprise | action possédée serveur et état local de commande | non |
| Fait/session/position | DTO mission-action puis relecture execution du profil | non |
| MISSION historique | projection historique exacte après choix explicite | non |
| Détails | raison/navigation applicable à la demande | non |
| Indisponible/inconnu | résultat serveur ou transport distincts | non |
| Journal/menu | commandes de navigation, pas prescription | non |

## Comparaison avec la référence validée
MISSION-SCREEN-V1 et UX-CAL-02 : sources/baselines intactes ; deux références historiques incluses dans board, pas régénérées. Famille nouvelle Today/projection uniquement. Compositions calibrage/ack/exécution conservées. Contraste et couleurs issus des tokens existants, aucun nouveau repli couleur.

## Relecture décision par décision — CLAUDE §5.2
| Décision | Verdict contre ce diff |
|---|---|
| HOME D1, contrôle identifiable et une action dominante | Respecté avec primitives natives acceptées ; habillage web historique non transposé |
| D2, pas « Recommandé IA », vraie provenance/raison | Respecté, historique exact sur choix explicite |
| D3, D4, D5 | LEGACY_VISUAL_REFERENCE en mobile ; nouveaux tokens/objets interdits, MISSION LOCKED préservée |
| D6, pas calendrier de cycle inventé | Respecté, aucune anticipation ou récupération calculée localement |
| D7, continuité sans streak | Non concerné, aucun compteur ajouté |
| D8, Progrès dédié | Respecté, quatre tabs inchangés ; feature MOB-05A séparée |
| D9, pas séance N+2 | Respecté, aucune proposition future ajoutée |
| SURFACES Q1, identité connexion et accroche FR | Non concerné visuellement, compte/auth UI conservés |
| Q2, ancienne ancre récupération | Référence web historique, MISSION mobile LOCKED ultérieure intacte ; aucune bande/reco inventée |
| Q3 et amendement retrait état du jour | Respecté, aucun nouveau formulaire readiness |
| Q4 et amendement type/état des lignes | Non concerné, exécution et sémantique séries intactes |
| Q5, Q6, Q7, Q8 et .btn | LEGACY_VISUAL_REFERENCE selon ADR mobile ; primitives/tokens natifs existants conservés, une action dominante |
| Tokens bleus et convergence | Sémantique system/signal conservée, aucun littéral couleur/score ajouté ; pas de récupération/continuité fictive pour remplir Today |

## Un changement par itération
Demande opérateur « current real recommendation or honest unavailable state », « resume-first », géométrie MISSION conservée. Delta : orientation/action propriétaire autour des consommateurs existants. Avant/après dans board. Aucune refonte du design, compte, calibrage ou exécution.
