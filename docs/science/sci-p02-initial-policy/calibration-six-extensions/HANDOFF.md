# Handoff consommateur — six rencontres de calibrage

**ADMITTED_WITH_LIMITS / ISOLATED / NOT_SERVED.** Admission et pins effectifs sont lus dans
`authority/registry.v1.json` et le reçu DELIVERY.md, pas dans la préparation
PLAN_HANDOFF_PROPOSED.md historique. Aucune capacité app/serveur nouvelle ouverte.

## Interfaces réellement implémentées

- `tools.science_calibration_extension.policy.load_authority(root: Path = ROOT)`
  retourne ExtensionAuthority, ou refuse publication/source/parent dérivés.
- `tools.science_calibration_extension.evaluator.evaluate(raw, authority=None)`
  retourne EncounterResult1.0.0 ; sans vraie autorité, aucune permission positive.
- `tools.science_calibration_extension.validation.validate_result(raw,response,authority=None)`
  vérifie strictement et retourne la décision canonique recomputée, jamais le
  corps client comme autorité. QUALIFIED exige épisode exact/C3/loaded guard.
- `compile_candidate` est une recherche non admise, pas un fallback public.
- `artifacts` est générateur de données synthétiques hors runtime ; aucun
  consommateur produit ne doit charger ses exemples pour remplacer les faits.

Politique initial-calibration-extension/1.0.0, moteur calibration-extension-evaluator/1.0.0,
registre initial-calibration-extension-registry/1.0.0 ; même échange1.0.0/V3.
Six IDs exacts et realizations/semantics/reviews/protocols dans la publication.

## Contrat à intégrer par un futur delta PLAN

1. Autorité serveur choisie/pinée explicitement, négociation du profil même si
   la forme JSON est1.0.0 ; jamais policy/authority libre du client. Ancien pilote
   et rejeux conservés. Refus de source dérivée/révocation, pas downgrade implicite.
2. Sujet depuis auth et ledger append-only exhaustif propriétaire/révision ;
   contexte exact/disponibilité et sources des instructions réellement acquises.
   Le code pur ne vérifie ni contenu d'un source_ref ni présence d'appareil.
   Acquéreur doit établir l'applicabilité des instructions au modèle/accessoire,
   et conserver les déclarations de compréhension/contrôle comme subjectives.
3. Préparation/choix/confirmation/familiarisation/essai/acceptation distincts,
   dates d'occurrence et ordre réels. Confirmation chargée Setting exact après
   choix/setup/contexte courants. Préparation RDL sans haltères sans réglage
   distincte, jamais0kg/BODYWEIGHT/essai PER_IMPLEMENT ou travail.
4. Faits et permission courante séparés. QUALIFIED porte épisode/réglage/essai/
   acceptation exacts, confianceLOW, temps/effortUNKNOWN. Retrait ou préoccupation
   ferme guidage ; facts/read/journal restent possibles. Pas de reprise après
   préoccupation admise, même sous nouvel ID. Retry volontaire explicite seulement.
5. Réponses perdues et A/B : identités/corps durables, relecture propriétaire,
   invalidation auth/source context, pas nouvelle observation synthétisée. Le
   consentement/finalités/copies DATA applicables restent un préalable distinct.
6. Après sept épisodes effectivement qualifiés et snapshot actuel : vrai V3,
   UNKNOWN/BUDGET_UNCERTAIN, ack explicite lié au plan, puis commande possédée
   idempotente existante. Encounter ne crée ni plan ni séance ni série de travail.

## Frontière produit préservée

Le worker PLAN actuel consomme le pilote historique. Aucun import/route/capability,
SDK, packaging, navigation ou pixel n'est modifié ici. Nouvelle intégration
nécessite delta PLAN et gates visuelles applicables ; MISSION reste LOCKED.
Ni CI ni bridge synthétique ne prouve une expérience physique ou une activation.
