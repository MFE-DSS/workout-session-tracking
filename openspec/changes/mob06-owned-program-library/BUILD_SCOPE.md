# Build scope — MOB-06

BUILD_AUTHORIZED / G1_ACCEPTED / PIXELS_PENDING. Décision reçue le12novembre :
« Autoriser MOB-06 et valider G1 », call_4321044cec284c79898cb7d2dd483990,
conservée dans AUTHORIZATION.json. Aucun pixel final, traitement réel ou
déploiement accepté par ce GO. Maltin n'est plus une dépendance.

## Fichiers proposés
Nouveaux app/services/library_read_model.py, library_start.py,
app/routers/mobile_library.py et tests ciblés. Réutilisation read-only des
loadout/user_program_drafts/user_program_launch/session_builder et préflight.
Natif api/library.ts/libraryResource.ts et tests, libraryVocabulary.json fermé
et lié par test au vocabulaire canonique, ui/library/LibraryHost.tsx et
LibraryScreen.tsx/tests ; contrôleur sync/libraryOpening.ts/tests sans nouveau
modèle de programme ou journal d'entraînement. Nouveau
storage/libraryPendingOpenings.ts/tests : une table SQLite opérationnelle,
pas une copie canonique des faits.

Partagés à séquencer après BODY/NUT : app/config.py (flag fermé),
app/routers/mobile_api.py (montage), clients/mobile/ConnectedApp.tsx,
src/routes/programmes.tsx, shell/ShellContext.tsx et API missionOpening.ts pour le garde global ;
storage/journal.ts, journalTypes.ts, journal.web.ts pour attacher les intentions
à la connexion/queue existantes. Schémas active_session/outbox et états V3
conservés, pas de nouveau fichier de journal ou d’outbox de séries. Tests et inventaire MOB-00/registre.

Read-only : SCI/PLAN/ack/exécution, BodyMeasurement/NUT, schémas/DB historiques,
exécution native (cardio/zéro série non démarrables ici),
legacy routes web, marque/primitives/tokens/baselines/assets/navigation4onglets,
SDK/lock/EAS/CI/QA02. Aucun constructeur, mutation de programme ou génération.

## Gates
Contrats/budgets/leases finalisés, revue builder, GO scope/G1 avant apply.
check_scope réel avant tests, ciblés/broad/TypeScript/mobile/sécurité/OpenSpec,
revue indépendante, vrais rendus iOS/Android acceptés avant commit UI, CI HEAD
exact et GOV-MERGE-01. Pas de question de merge routinière ; déploiement séparé.
Le retour utilisateur n'a pas choisi « consultation seule » : lancement prévu
quand son domaine le permet, sans contourner ses préconditions ou le profil SCI.
