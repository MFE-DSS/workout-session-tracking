# Contrat de rencontre proposé et handoff PLAN

**first-calibration-encounter/1.0.0 — proposition, aucun export exécutable livré.** Ce contrat est une activité d'acquisition distincte ; FirstPlanRequest/Recommendation3.0.0 restent inchangés.

## Entrée de l'évaluateur pur proposé
- contract_version, encounter_ref, subject_ref, source_revision, as_of UTC et références de politique réellement chargée.
- Faits déclarés population/limitations avec leur provenance et états connus/inconnus/refusés/conflit ; pas d'anthropométrie requise.
- ContextKey existant (champs inconnus permis pour ouverture), disponibilité et références d'instructions spécifiques, preuve de leur source/type (notice réelle/aide humaine), compréhension déclarée courante, préparation/contrôle connus ou inconnus.
- Setting existant seulement après choix humain réel ; null reste null avant choix, jamais zéro par défaut.
- Raison d’arrêt effective dans une métadonnée de rencontre typée : COMPLETED / USER_STOPPED / TIME_LIMIT / CONCERN / FAILURE / UNKNOWN ; cohérence avec la revue TrialReviewV3 existante à vérifier, sans en modifier les enums. Ne pas déduire successful=False d’une simple interruption volontaire.
- Épisode actuel optionnel d'événements existants, plus statut de retrait/complétude propriétaire et préoccupations/prédécesseurs pertinents. PLAN doit garantir ledger exhaustif et auth, le body ne s'autocertifie pas.
- Politique de rencontre pinée, références exactes du V3/curation sans modification. Pas de registre ou décision APPROVED arbitraire fourni par le téléphone.

## Résultat
state = CALIBRATION_REQUIRED / SUPPORTED_INITIAL_EXPLORATION / OBSERVED / QUALIFIED / CONCERN_REVIEW / UNAVAILABLE / INSUFFICIENT_EVIDENCE / WITHDRAWN.
phase = IDENTIFY / FAMILIARIZE / TRIAL / OBSERVE / DECIDE ; activity_kind = CALIBRATION_ACTIVITY.
allowed_actions typées : READ_GUIDANCE, PROVIDE_FACTS, REQUEST_ASSISTANCE, CONFIRM_CONTEXT, INITIATE_FAMILIARIZATION, CONFIRM_FAMILIARIZATION, INITIATE_TRIAL, RECORD_TRIAL, ACCEPT_EXACT_SETTING, PAUSE, WITHDRAW. Aucune START_WORK_SET. INITIATE_FAMILIARIZATION autorise seulement la familiarisation sous préconditions de population/limitations/contexte/instructions/compréhension ; INITIATE_TRIAL exige en plus un réglage réel confirmé, familiarisation antérieure et état courant sans blocage. Ces permissions sont recalculées séparément des actions d’enregistrement, jamais déduites de RECORD_TRIAL. Les actions positives physiques sont absentes sans autorité/contexte applicables. RECORD_TRIAL peut enregistrer un fait déjà survenu même si le guidage courant est bloqué : journaliser un fait n'autorise pas sa répétition.

Références et empreinte d'entrée, règles/manques/blocages sourcés, réglage qualifié nullable, event/acceptance exacts et épisode exportable inchangé. Confidence LOW/UNKNOWN ; effort sufficiency UNKNOWN, durée UNKNOWN, aucune prédiction médicale. Pas de success score ou exposure credit.

## Progression réelle
1. Aucun historique : ouvrir READ_GUIDANCE/PROVIDE_FACTS sans sept réglages.
2. Réalisation/dispositif/instructions/conditions du pilote établis : familiarisation contextuelle, sans kg/reps/minutes imposés par défaut.
3. Réglage choisi et confirmé par la personne, familiarisation réellement antérieure : possibilité d'essai contrôlé visant, s'il est toléré, la fenêtre de qualification C3 ; arrêt libre, pas d'échec requis.
4. Relever exactement réglage/unité/reps/date/completion/qualité/gêne et éventuellement effort subjectif. OBSERVED reste OBSERVED jusqu'à satisfaction exacte C3 et décision d'acceptation présente.
5. Accepter la dernière tentative comparable sans préoccupation, dans son contexte exact : QUALIFIED provisoire ; pas automatiquement plan complet.
6. Acquérir les autres réalisations sous leurs procédures applicables, puis snapshot/evaluation V3 réels. Plan SCIENTIFICALLY_READY peut encore demander time_ack exact et ne crée toujours pas une séance.

## Frontière PLAN
PLAN possède identité authentifiée et subject opaque, acquisition réelle/UTC/révision, ledger append-only/provenance/consentement pertinent, idempotence/concurrence/relecture, retrait/refresh d'autorité. Une hash/checkbox ne prouve ni identité, ni instructions réellement obtenues, ni qualification humaine. Qualification partielle n'est jamais séance native créée ; l'API et le journal de travail ne doivent pas recevoir des séries fictives pour amorcer le moteur.

Changement d'appareil/réalisation/côté/unité ou préoccupation invalide futur guidage/qualification ; faits antérieurs restent. Aucun retry de mutation après réponse inconnue sans relecture de même identité. Une perte de réponse n'est ni absence d'événement ni consentement. Même si un futur GET retrouve QUALIFIED, vérifier révision/owner/autorité avant nouvelle consigne. Compte B ne reçoit pas épisodes ou réglages A. Réponses tardives après logout/changement de compte neutralisées.

Les limitations/observations sont des données à gouverner avec DATA avant stockage/activation réelle ; le build isolé n'en déduit ni base légale ni durée. SDK/API/navigation/visuel MISSION restent hors lease. Le change PLAN préparé est indépendant et doit recevoir son GO ; lui fournir contrat/export/policy digest/revue et exemples étiquetés après livraison.

## Arrêt volontaire et préoccupation — distinction obligatoire

USER_STOPPED/TIME_LIMIT avec completed=False, successful=null et qualité ACCEPTABLE/gêne NO_CONCERN effectivement rapportées reste OBSERVED non qualifié. Ce null décrit absence de conclusion de réussite, pas une réussite cachée. successful=False, FAILURE, CONCERN, manque de contrôle ou qualité/gêne inconnues restent CONCERN_REVIEW. Une raison UNKNOWN ne permet pas de nouvelle consigne avant clarification réelle. Ne jamais transformer un False ou un signal préoccupant en null pour rouvrir le flux. Un nouvel essai non préoccupant exige une décision explicite de l’utilisateur, disponibilité/maîtrise actuelles et règles applicables ; aucune poursuite automatique.

## Prévisualisation de recherche et entrée autoritaire

Une compilation de tests avant admission porte `DRAFT_EVALUATION_SYNTHETIC_NOT_AUTHORITY`, jamais une permission utilisable. L'évaluateur public ne rend INITIATE_* ou QUALIFIED autoritaires qu'après chargement de la vraie politique de rencontre revue/admissible. Réutiliser le noyau pur candidat derrière cette frontière, sans deuxième moteur ni registre de test approuvé. Ces previews ne sont pas des payloads PLAN servis.

## Interfaces livrées après GO et revue SCI

Le statut initial PROPOSED décrit la préparation. Contrat/politique1.0.0 désormais réalisés et admis avec limites, toujours NOT_SERVED ; reçu DELIVERY.md et décision authority/ADMISSION.md.

`load_authority(root=ROOT)` charge la publication réelle ; `evaluate(raw, authority)` rend EncounterResult ; `validate_result(raw,response,authority)` revalide strictement et retourne la décision recomputée. `validated_input(raw)` et `input_digest(raw)` lient toutes observations/preuves/retraits/révision. Sans autorité, evaluate reste NOT_ADMITTED et ne promeut pas une qualification de preview. La source PLAN ne doit jamais appeler compile_candidate pour produire une permission.

Les observations portables restent CalibrationEpisode existant, avec sujet/contexte/événements/références/acceptation exacts ; V3 ne reçoit aucun nouveau champ. Réacquérir/relire les faits sous propriétaire et politique applicables, ne pas transférer une sortie synthétique comme observation. Les4exports sous exports/ sont de recherche/test ; aucun payload ne sert de fallback runtime.
