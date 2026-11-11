# MOB-05A — passation du consommateur Progrès

11 novembre 2026. Code [PR403](https://github.com/MFE-DSS/workout-session-tracking/pull/403),
HEAD `0343ecf289d278ae60636978df3c8f21aad4fe5c`, merge
`18e04bd25ae424e97ac9f810321972e1b101dcae`. Consulter le reçu de closeout et son
suivi vivant pour le canonique final ; repartir après fetch, pas d'un onglet ou
du checkout opérateur historique. Cette passation ne donne aucun nouveau GO BUILD
ou GO de release.

## Réemploi du vrai consommateur

- `TrainingHistoryHost` est monté par la vraie route Progrès seulement focalisée,
  depuis ConnectedApp/ShellContext. Il réutilise AuthSession, le transport et le
  client V3 existants ; ne pas créer un second compte, journal ou contrôleur de
  séance pour l'historique. Foreground/refresh revalident ; unmount invalide les
  scans poids et les réponses tardives.
- `TrainingHistoryClient` décode strictement les quatre GET possédés. Les refs
  opaques de lecture/exercice/occurrence se transmettent telles quelles ; ni nom,
  code ni ID nu ne les remplacent. READ_CHANGED exige refresh. Une référence
  étrangère/inconnue ne révèle aucun fait. Les nouvelles écritures de mesure
  n'appartiennent pas à ce client.
- La lectureV1 d'une séanceSCI refuse `execution_profile_required`, puis le vrai
  lecteurV3 est recoupé avec le descripteur avant projection historique. Actions,
  curseur, transitions et permission courante ne donnent aucune commande depuis
  Progrès. Révocation de guidage n'efface pas les faits historiques lisibles.
- Les valeurs proviennent de SetLog legacy ou de l'observation SCI typée, jamais
  de la dose prescrite. Legacy `kg saisis` garde le contexte absent ; machine et
  PER_IMPLEMENT conservent leurs unités. Une observation incomplète reste un
  fait, même sans charge/répétitions ; une ligne vierge n'en devient pas un.
- Les identités d'exercice ne sont pas une politique de comparaison de charges.
  Pas de record, delta,1RM, score ni courbe qui relie des contextes incompatibles.
  Le plafond de scan est cinq lots de200 ; source/affichage et continuation
  partielle restent distincts. Les comptes de fréquence couvrent la période,
  pas les lignes affichées ; planning non persisté reste inconnu.
- Le poids utilise BodyMeasurement/consentement/client existants, fenêtre
  measured_at et IDs datés. Pas de fallback users.weight_kg, moyenne, zéro absent,
  interpolation, seconde série ou copie persistée de DTO. Pagination bornée et
  suite explicite ; lectures précédentes du même compte restent étiquetées.

## Contrat visible conservé

Le [board final](../../../clients/mobile/visual-contract/review-receipts/mob05a/index.html)
et son [reçu](../../../clients/mobile/visual-contract/review-receipts/mob05a/receipt.json)
portent les22frames,15sources et les deux décisions opérateur. La dernière :
« Valider le delta final MOB-05A », avant commit du détail compact. Frame C,
RecessedWindow, NumericReadout et liens48 existants ; source/limites à la demande,
statut/valeur/unité/contexte courts visibles. Pas de baseline ou primitive
globale changée. Toute nouvelle composition conserve ses gates propres.

Preuves/limites dans [REVIEW_AND_VALIDATION](REVIEW_AND_VALIDATION.md).
Physique/vocal/focus/grands textes exhaustifs et Android app complète nouvelle
ne deviennent pas positifs depuis le banc. Deux mineurs restent : échec initial
de l'index peu explicite ; borne haute de période sans heure.

## Release et prochains scopes

[QA_RELEASE_HANDOFF](QA_RELEASE_HANDOFF.md) donne le couplage réel serveur/client.
L'APK QA02 n'a pas reçu cette fonction ; build/OTA/hébergement/cutover/OVH/DATA
restent séparés. Une fusion Git ne met pas à jour le téléphone du testeur.
La recette physique et la parité de son artefact demeurent ouvertes.

BODY-01 est préparé séparément, réconcilié au codeMOB05 : première écriture datée
vers BodyMeasurement, puis vrai readback Progrès. **Conflit normatif append-only
versus correction manuelle à trancher explicitement avant apply et GO BUILD.**
Ne pas appeler une route web mutante pour contourner ce conflit. Les copies
locales, writer partagé, correction/date/concurrence et DATA gardent leur contrat.

NUT-01 Smart Capture est préparé séparément : étiquette pour100g, portion humaine,
candidat/correction/confirmation et manuel autonome. Provider/modèle/coût et
traitement des copies restent à décider avant GO. Aucune portion, cible,
nutrition ou body-fat inférés ; aucune image générative. Reprendre ces dossiers,
pas de nouveau change concurrent qui duplique leurs décisions.

Réserver les leases de composition en séquence ; ne pas ouvrir de PR BODY/NUT
chevauchante sur ConnectedApp/ShellContext/Progrès. MOB-06 reste réservé à Maltin.
Checkout opérateur et préparations ARCH/QA/REL03 préservés ; seuls les éléments
de livraison MOB05 sans travail unique peuvent être nettoyés après preuve.
