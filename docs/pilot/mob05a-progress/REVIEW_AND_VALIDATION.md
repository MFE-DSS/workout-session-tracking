# MOB-05A — preuves, décisions et limites de validation

11 novembre 2026. Code intégré par PR403, merge
`18e04bd25ae424e97ac9f810321972e1b101dcae` ; la clôture canonique est suivie
séparément. Le [reçu visuel final](../../../clients/mobile/visual-contract/review-receipts/mob05a/receipt.json)
conserve l'acceptation opérateur et les sources/frames, y compris l'ancien reçu.

## Vérifications effectivement observées

Local :151 tests backend ciblés/broad des consommateurs ;88 suites/1122 tests
mobiles et TypeScript. Ruff neuf, budget260≤548, Bandit, Gitleaks, protocole et
OpenSpec strict24/24 passent. Le tier complet estSHARED_CODE ; aucun full sweep
backend local systématique, aucun seuil ou test affaibli. Les erreurs initiales
de configuration du banc, typage de tests, lecture/pagination et assertions
restent dans les logs ; leurs reruns verts ne réécrivent pas les anciens résultats.

CI PR finale [42983311724](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/42983311724),
HEAD `0343ecf289d278ae60636978df3c8f21aad4fe5c` : completed/success,11 jobs,
8476 backend passants/3 ignorés ;88 suites/1122 mobiles+TypeScript ;77 visuels.
Les tests ont réellement tourné ; attestationSHADOW, pas de réutilisation
présentée comme exécution. Les quatre contrôles protégés ont réussi.

Deux revues distinctes dans le temps : revue complète initiale de branche, puis
nouvelle revue bornée au raffinement demandé par l'opérateur. Pas de boucle de
relecture générale ni d'avis indépendant inventé sur les corrections finales.

| Revue | Important confirmé et corrigé | Preuve |
|---|---|---|
| Branche I1 | Une503 en pagination effaçait la lecture connue | RED→GREEN ; faits du même compte conservés comme précédents |
| Branche I2 | Le scan poids pouvait continuer après unmount | RED→GREEN ; invalidation sur refresh/unmount et séquence/auth |
| Branche I3 | Valeur legacy invalide présentée comme absence | RED→GREEN ; état invalide et représentation source séparés |
| Branche I4 | Faits SCI sans observation/révision cohérentes acceptés | RED→GREEN ; refus historique strict sans prescription de remplacement |
| Branche I5 | Lien séance→exercice et sélection de l'occurrence manquants | RED→GREEN ; référence serveur exacte et scellée, repèrese_id |
| Nouveau détail I1 | Observation SCI incomplète confondue avec ligne vierge | Un témoinRED puis présence d'observation préservée et suite1122PASS |

Revue initiale :0Critical/5Important/2Minor ; nouvelle revue :0Critical/
1Important/0Minor. La dernière correction est vérifiée par son test et la suite,
sans second verdict indépendant prétendu. Les derniers fichiers du détail et
les captures examinées sont empreintés dans les preuves conservées.

## Pixels et consommateurs réels

Première décision : « Valider ces pixels MOB-05A contrôlés ». Le mandat suivant
a demandé une hiérarchie locale plus compacte ; le croquis précis opérateur a
servi deG1 selon le protocole. Décision finale du11novembre : **« Valider le delta
final MOB-05A »**, question call_3bf814ef514c414996496828a7220ce8, avant commit UI.

22 captures dont15 anciennes intactes ;15 sources runtime finales empreintées.
Titre30→17sp, marge du titre28→0dp, écart avant corps24→12dp ; Retour44→48dp,
liens/disclosures48dp. Cadres mesurés, NumericReadout et unités canoniques ; un
contexte court visible, dates et limites dépliables. Aucun composant global,
palette, logo ou baselineLOCKED modifié.

iOS390×844pt : vrai ConnectedApp/AuthSession/SQLite/HTTP, initialisation de route
par adaptateur de banc, actionsAX réelles séance/disclosure/exercice/occurrence.
Dynamic Type normal etXXXL. Android360/480dp et fonte100/130% : vrais Host et
présentateurs de production, AuthSession/SQLite/HTTP dans banc externe. Les
nouveaux loading/unknown proviennent du vrai Host avec attente/échec de transport
contrôlé ; aucun DTO de succès injecté. Le read_state d'un préchargement externe
dans les sidecars n'est pas présenté comme état interne observé du Host.

Android ConnectedApp complet reste limité dans Expo Go par le module natif
conservé ; aucun shim ni suppression pour passer. Gear/Tools sont externes.
Positions basses programmatiques après `noWindowsAvailable` CUA : aucune preuve
de geste. Android empty n'a pas eu son reçu matching ; pas dePASS revendiqué,
iOS vide/accord requis réellement observé. Cohorte SCI historique réelle testée
par services/clients ; tentative rawC3 du banc refusée, aucune qualification
personnelle ou séance nativeSCI complète fabriquée. Tous les chiffres visibles
restent des témoignages synthétiques.

## Mineurs et points hors jugement conservés

Deux mineurs différés : premier échec d'index d'exercice trop peu explicite
(Actualiser reste disponible) ; borne temporelle supérieure affichée à la date,
sans l'heure. Ils ne disparaissent pas avec la CI ou les nouveaux pixels.

VoiceOver/TalkBack complets, focus après disclosure, gestes/appareils physiques,
iOS320pt et nouveau build installé : gatesRELEASE ouvertes. Les captures ne
certifient pas ces comportements. Les autres domaines, DATA et prescriptions
scientifiques ne sont pas revalidés par cette revue de lecture historique.

## Décisions prises et coûts

| Décision consignée dans le ledger | Motif et coût conservé |
|---|---|
| Modules propres avant disponibilité du leaseMOB04 ; montage partagé après ses merges | Travail indépendant autorisé ; imports/consommateurs revalidés après nouvelle base, aucune fonction servie avant montage |
| Plafond d'ID calculé sur le propriétaire, indépendant de la fenêtre | Pas de fuite du volume d'autrui ; nouveaux inserts hors plafond attendent un refresh, pas de snapshot immuable promis |
| occurrence_ref optionnelle vérifiée avant dispatch de profil ; index source distinct du curseur d'affichage | Pas de cinquième route ni de déduction floue ; identité changée exige nouvelle lecture et références exactes |
| Host monté seulement sur onglet focalisé, période4w à chaque montage | Évite lectures cachées et nouveau stockage ; l'utilisateur peut devoir rechoisir la période |
| Liens d'exercice produits par la même identité serveur que l'index et scellés dansentry_ref | Pas de rapprochement client nom/code ; changement d'identité invalide l'ancien lien et demande refresh |
| Primitives AUREN existantes plutôt que dépendanceUI supplémentaire | ContratsLOCKED/scope sansdeps respectés ; recette vocale complète reste à faire |
| GO MERGE permanent et garde anti-overcheck gouvernent la finalisation | Pas de micro-GO ou full sweep local interdit ; aucun nouveau build/deploy/physique implicitement autorisé |

Les points écartés du jugement sont traités comme gates explicites : pixels
obtenus, registre sous lease, physique/vocal hors preuve et autres domaines hors
scope. Aucun de ces points ne devient silencieusement positif.

## Sonar et historique du signal de sécurité

CI initiale42903697834/5025c79 verte mais signal potentielS6680CRITICAL : merge
suspendu pour analyse. Bornes existantes1..100 et1000 lignes confirmées ;11
témoins adversariaux/budgetGREEN avant et après, pas d'exploit illimité reproduit.
Refactor minimal vers cinq lots constants de200, même réponse/curseur/budget.
CI raffinée42908162450/6d6b1ba :8476backend/3skip,1117mobiles+TS,77visuels.
Le bot a résolu le thread obsolète après analyse ; aucun statut d'issue/gate
changé manuellement. Ce n'est pas un RED d'une vulnérabilité confirmée.

Analyse PR finale : ERROR consultatif,8CODE_SMELL (S7500/S5713MINOR,
S3358/S5778MAJOR, S3776CRITICAL de complexité),0nouveau bug/vulnérabilité/
hotspot ; couverture app92,5%, nouvelle93,65482233502539%. Les sévérités Sonar
restent distinctes des défauts fonctionnels de revue. Résultat canonique et
dettes externes inspectées à consigner dans le reçu de clôture, sans déclaration
globale de conformité/sécurité.
