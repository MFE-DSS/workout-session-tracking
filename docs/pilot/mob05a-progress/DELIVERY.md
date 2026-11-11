# MOB-05A — Progress Core livré dans le code contrôlé

11 novembre2026. **Code fusionné, CI canonique réussie ; publication du closeout en cours.** [PR403](https://github.com/MFE-DSS/workout-session-tracking/pull/403), HEAD `0343ecf289d278ae60636978df3c8f21aad4fe5c`, merge `18e04bd25ae424e97ac9f810321972e1b101dcae`. Aucun nouvel APK, activation DATA ou déploiement de ce slice.

## Fonction réellement raccordée

L'onglet Progrès existant monte le vrai TrainingHistoryHost depuis ConnectedApp : séances récentes et faits par série, fréquence factuelle sur4/12semaines civiles ouTout, exercice exact et occurrences, chronologie BodyMeasurement datée sous accord applicable. Les lectures cessent au départ de l'onglet ; refresh et foreground revalident. Le journal, AuthSession, les producteursSCI, quatre tabs, MISSION et exécution restent les consommateurs canoniques existants.

Quatre GET propriétaires sous `/api/mobile/v1/me/training-history`, Bearer, no-store, absence/étranger404 identiques et refs signées. Changement de référence demande refresh ; échec de pagination conserve les faits connus du même compte comme lecture précédente. Scan cinq lots de200 maximum, continuation partielle distincte de vide. Comptes sur toute la période, pas les seules lignes reçues.

Un statut terminé sans série de travail complétée et fait de reps/charge reste visible sans compter comme travail effectué. Planning daté absent : inconnu, pas objectif ou taux d'adhérence inventé. Legacy : faits capturés et `kg saisis`, matériel/prescription non capturés. SCI : vrai lecteurV3 et validation historique stricte, observation typée conservée après retrait de guidage ; aucune commande de travail issue de l'historique. MACHINE_DISPLAY_KG etPER_IMPLEMENT ne deviennent jamais une masse externe totale ou une équivalence entre appareils.

Poids : source unique BodyMeasurement, measured_at et qualité conservés ; pas de writer, fallback profil, seconde série, cache persistant, lissage ou prédiction. Les points inconnus/invalides ne deviennent pas0 ; pagination bornée explicite.

## Hiérarchie finale acceptée

Le détail historique utilise un en-tête local compact et FrameC/RecessedWindow/NumericReadout existants. Titre30→17sp, marge28→0dp, écart de corps24→12dp ; Retour44→48dp, liens/disclosures48dp. Valeurs/unités, date/statut et contexte court visibles ; dates exactes, provenance, limites et prescription capturée à la demande. Zéro, absent, invalide et observation SCI incomplète restent distincts.

L'opérateur a accepté le premier board puis le delta final : **« Valider le delta final MOB-05A »**, avant commit UI.22captures/15sources,15frames antérieures intactes. Aucune primitive globale, palette, logo ou baselineLOCKED modifiés. Rendus/limites et décisions dans [REVIEW_AND_VALIDATION](REVIEW_AND_VALIDATION.md) et le [reçu final](../../../clients/mobile/visual-contract/review-receipts/mob05a/receipt.json).

## Preuves et gates restantes

CI PR42983311724 et canonique42986290983 : completed/success,11jobs chacune ;8476backend/3ignorés,88suites/1122mobiles+TypeScript,77visuels réellement exécutés. Local151backend ciblés/broad et1122mobiles+TypeScript ; protocole/OpenSpec24/24, Ruffbudget260≤548, Bandit/Gitleaks passants. Revue initiale5Important corrigés, nouveau détail1Important corrigé, témoinsRED→GREEN ; pas de second avis indépendant des derniers correctifs revendiqué. Deux mineurs restent divulgués.

iOS : vrai ConnectedApp/HTTP ; Android : Host/présentateurs réels dans banc natif synthétique, app complète ExpoGo limitée par module natif conservé. Aucune recette physique ou cohorteSCI native complète nouvelle. TalkBack/VoiceOver/focus/gestes complets et nouveau build installé restent à vérifier. Les chiffres visibles ne sont pas des faits personnels du testeur.

Sonar PR final ERROR consultatif :8smells,0nouveau bug/vulnérabilité/hotspot, couverture app92,5%/nouvelle93,6548%. Canonique exact18e :ERROR,8bugs/565smells/8entrées externesBandit/0hotspot ; fichiers des huit entrées inchangés depuis la base, sans déclaration globale d'innocuité. [Closeout](CLOSEOUT.md) conserve les références exactes et l'historiqueS6680 corrigé, sans baisse de seuil ou disposition d'issue manuelle.

[Parité](PARITY.md) distingue preuve contrôlée et APK QA02, qui ne contient pas ce slice. [Passation QA](QA_RELEASE_HANDOFF.md) borne l'opération REL-03. BODY/NUT restent des préparations séparées avec décisions/GO propres ; MOB-06/Maltin, compte, journal et moteurs acquis ne sont pas rouverts.
