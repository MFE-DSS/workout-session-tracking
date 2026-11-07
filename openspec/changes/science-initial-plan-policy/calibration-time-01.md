# SCI-P02-CALIBRATION-TIME-01 — delta proposé pour revue

6 novembre 2026. Base canonique **8e987c634a576cf729612db4adcfb313bf8ab350**. **PROPOSED / GO BUILD NON REÇU pour ce delta.** Le mandat courant demande expressément de préparer la proposition puis de s'arrêter à cette frontière si le GO manque. Le GO historique du producteur isolé est conservé : il autorisait le design initial avec charge null/CALIBRATION_REQUIRED, pas ce nouveau protocole d'observations ni son binding versionné.

**Actualisation — GO BUILD reçu :** après exposition du delta/design et demande de validation, l'opérateur répond **« continue »**. Cette réponse ouvre le build isolé présenté, ses tests/revues/publication sous GO permanent ; elle ne transforme aucune hypothèse scientifique en admission, ni n'autorise API/UI/activation. Les mentions de proposition/non-réception ci-dessous décrivent l'étape précédente. Plan d'apply : [calibration-time-implementation.md](calibration-time-implementation.md).

## Pourquoi et périmètre

Rapprocher le vrai producteur initial d'une admission par une calibration traçable et une faisabilité temporelle conditionnelle. Ne pas produire un nouveau rapport sans trajectoire d'implémentation. PULL_EXPOSURE_01 est clos (#364/#365) ; son unique rôle G17 dérivé reste qualitatif et conditionnel.

## Brainstorming / Options / Risques / Choix retenu

| Option | Apport | Limite et décision proposée |
|---|---|---|
| Réutiliser directement overload_engine et ses incréments/qualité | Service servi existant | Ne possède ni pas réel confirmé, ni RIR, ni protocole de première charge ; constantes historiques non admises ici. Écarté pour cette politique, service préservé |
| Ajouter deux diagnostics isolés sans lien au producteur | Faible couplage | Répète le blocage sans exercer un premier plan réel. Insuffisant |
| Successeur versionné du producteur isolé + observations/composantes explicites | Tests end-to-end du moteur hors runtime, ancien rejeu préservé | **Choix de l'agent proposé à l'approbation**. Ne donne pas admission scientifique ou READY par lui-même |

## Livrables d'apply proposés

- `tools/science_initial_policy/calibration_time_contracts.py`, `load_calibration.py`, `session_time.py`, `v2_registry.py`, `v2_producer.py`, `v2_fixtures.py` : modèles stricts/purs, replay et producteur successeur `initial-policy-producer/2.0.0`, non importés au démarrage.
- Tests dédiés `tests/test_science_load_calibration.py`, `test_science_session_time.py`, `test_science_initial_policy_v2.py`. Conservation des tests et onze sorties v1, ancien rest-floor et sept diagnostics pull.
- Artefacts sous `docs/science/sci-p02-initial-policy/calibration-time-01/` : politiques proposées versionnées, schémas isolés, sorties réellement générées et preuves. Le dossier présent est seulement le design avant apply.
- Composition explicitement versionnée de dose0.2, curation1.0, overlay pull1.0 et nouvelles décisions ; aucun changement des anciennes autorités/pins. Un futur snapshot effectif possède son propre identifiant/digest, jamais celui du catalogue historique inchangé.
- Enveloppe scientifique isolée request v1 + snapshot d'exécution/temps ; empreinte complète distincte de `decision_fingerprint(v1)`. Aucun fait décisionnel caché dans une chaîne libre du Blueprint.
- Modèle de temps : travail, repos, préparation/calibration, opérations, couverture et chevauchements ; bornes et quatre états ordinaux lorsque justifiés. Rest-floor conservé pour les réfutations partielles.
- Tests du producteur sur les cas Phase D, revues scientifique/code indépendantes, publication d'une seule PR scopée après GO, CI/readiness et merge sous GOV-MERGE-01. Une PR de closeout documentaire reste celle prévue par le protocole existant.

## Admission et frontière humaine

Approuver ce delta autoriserait le **build isolé décrit**, les conventions opérationnelles explicitement signalées dans DESIGN.md et leurs tests ; pas une correction individuelle du RIR, une dose biologique validée, des secondes universelles ni une admission automatique. Tout paramètre scientifique non soutenu reste bloquant. Par défaut : NOT_ADMITTED / NOT_SERVED / READY_NOT_PRODUCED.

Le producteur v2 ne publiera un READY que si une admission de références réelles est effectivement reçue et vérifiée après les revues ; des références d'autorité TEST_ONLY, un JSON APPROVED, une observation isolée ou un budget élevé ne suffisent jamais. Si ces gates restent ouvertes, le livrable autorisé sera le vrai producteur non-READY et ses diagnostics/fixtures réels, pas une fixture READY artificielle.

## Non-goals / périmètre interdit

Aucun app/, client mobile, modèle/table/migration, acquisition persistée, API, activation, déploiement, dessin d'instrument ou seuil E7. Aucun catalogue/E0/crédit/curation/pull/v1 réécrit. Aucune rampe kg ou durée par défaut ; aucune équivalence entre appareils/assistance, transfert d'exercice, faiblesse inférée des priorités, inventaire obligatoire ou raccourcissement du repos pour réussir le temps. Aucune archive du change global ou fermeture MOB03.

## Dossier prêt pour décision

- [Audit et sources canoniques](../../../docs/science/sci-p02-initial-policy/calibration-time-01/AUDIT.md)
- [Design exécutable après GO](../../../docs/science/sci-p02-initial-policy/calibration-time-01/DESIGN.md)
- [Spécification de tests, pas résultats](../../../docs/science/sci-p02-initial-policy/calibration-time-01/TEST_SPEC.md)
- [Preuves primaires et limites](../../../docs/science/sci-p02-initial-policy/calibration-time-01/EVIDENCE.md)
- [Décision/handoff et admission suivante](../../../docs/science/sci-p02-initial-policy/calibration-time-01/DECISIONS_AND_HANDOFF.md)

Revue de construction indépendante terminée : trois ambiguïtés clarifiées, contrôle final « nothing important left », sans admission scientifique implicite. Contrôles documentaires : check_scope DOCS et check_spec_protocol passant. Aucune implémentation de ces nouveaux modules ni test exécutable nouveau avant acceptation de ce delta.
