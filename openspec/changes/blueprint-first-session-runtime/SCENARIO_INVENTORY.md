# Scenario inventory — non-served

**NON_EXECUTABLE_SCENARIO_INVENTORY / NO_READY_FIXTURE / NOT_SERVED.** Textes d’entrées attendues seulement ; aucun JSON, réglage chiffré, propriétaire réel, fixture ou sortie positive exporté. Les faits synthétiques futurs restent dans les tests et ne font jamais autorité d’admission. Aucune collecte nouvelle réalisée ici.

| Cas | Entrées à acquérir ou construire seulement en test | État attendu, pas résultat déjà obtenu |
|---|---|---|
| S01 premier usage sans producteur | Préférences possédées éventuelles, port absent | no_plan_producer ; aucune MISSION scientifique |
| S02 manques/conflits | Objectif ou budgets absent ; deux limitations contradictoires sourcées | Assessment canonique exact ; pas poids/taille/inventaire ajouté |
| S03 sept observations limitées | Adulte déclaré non clinique, hypertrophie,2séances, limitations[], budgets déclarés ; sept contextes/settings bilatéraux exacts actuels qualifiés/acceptés par SCI ; inventaireUNKNOWN ; aucune anthropométrie | Producteur/registre réels requis avant science positive limitée ; tempsUNKNOWN, ack requis |
| S04 bootstrap seulement | Un contexte disponible, réglage/plage pas encore qualifiés | Draft/revue/DENIED, pas positif amorcé par fixture |
| S05 ack exact | Action explicite sur résultat S03 et mêmes références/empreintes/policy | ELIGIBLE possible selon autorité encore valide ; aucune durée compatible prétendue |
| S06 ack/requête périmés | Cadence/contexte/source/consentement/policy ou binding changé après capture | Nouvelle décision nécessaire ; aucune session créée |
| S07 autorité absente/altérée | Publication non disponible, registre vide, pin changé ou source retirée | Indisponibilité/refus fermé même si schéma positif valide |
| S08 premier start réel | S05 validé en ligne et représentable, aucune session ouverte | Une seule WorkoutSession possédée, dose/binding exacts ; pas cible traitée comme fait |
| S09 réponse perdue/course | S08 committé sans réponse ; double clé/double device/start historique/cancel | Relecture même session ou tombstone/refus ; jamais second handoff |
| S10 relance et journal | Session S08, observation d’une série, outbox pending/acked/refused/unknown puis relance | Même set/intent/context/setting typé, aucune correction ancienne rejouée |
| S11 préoccupation/retrait/offline | Session déjà créée, concern/policy retirée ou autorité non vérifiable | Faits lisibles/journalisables et sortie possible ; aucune nouvelle consigne autorisée par relecture |
| S12 contexte non représentable | Assistance/crans/côté inconnu ou autre réalisation que les sept admises | Refus avant création ; aucune conversion au kg/bilatéral |
| S13 consentement pertinent | Aucun consommateur corporel puis consommateur nécessitant contrat DATA explicite | Pas de gate body_measurements pour absence de traitement corporel ; autres finalités évaluées par DATA, sans NOT_REQUIRED automatique depuis absence de poids, aucune exigence corporelle globale |
| S14 bornes de temps | Repos applicables atteignent budget, puis cas sous budget avec travail/setup inconnus | TOO_LONG/DENIED puis UNKNOWN ; jamais durée0/SUPPORTED |

Le handoff/manifeste SCI PR375 (snapshots57ec puis74d30b documentés dans design) fournit les identités/versions du build isolé admis avec limites ; les pins canoniques finaux restent à recevoir. Identités concrètes des sept réalisations et sources/réglages runtime : exclusivement sources réelles capturées et autorité finale applicable, jamais les réglages synthétiques des exports SCI. Aucun READY copié depuis protocole V1, démonstrateur ou ancien paquet D. Les budgets/réglages utilisés ultérieurement en tests ne deviennent pas valeurs par défaut produit.

## Rencontres initiales réconciliées (compléments aux scénarios historiques)

- Zéro épisode, cadence/budgets inconnus : ouverture d’aide et acquisition progressive, pas sept prérequis à l’entrée.
- Pilote dispositif inconnu/instructions manquantes : aide/assistance, pas essai chargé.
- Pilote réellement préparé/choix humain/familiarisation antérieure : consigne depuis vraie politique rencontre ; enregistrement passé distinct de permission d’essai.
- Pilote QUALIFIED et six autres absents : observation réutilisable, pas de plan complet. Six autres accompagnements initiaux restent hors admission.
- Essai passé puis choix courant absent : science inchangée, faits et manque courant rendus séparément, aucun faux progrès ou essai autorisé.
