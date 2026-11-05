# MOB-03 — compte rendu et décisions pour le PO / l'architecte

5 novembre 2026. **Le critical path complet n'est pas terminé.** Le socle compte et préférences est réalisé ; le premier parcours personnalisé complet, les données corporelles, l'effacement et les recettes restent ouverts. Ce document est le point de reprise courant ; les rapports antérieurs conservent leurs états historiques.

Référence produit : [manifeste canonique v1.0](strategy/AUREN_MANIFESTO_V1.md). Change unique : `openspec/changes/account-onboarding-native/`. [PR draft #353](https://github.com/MFE-DSS/workout-session-tracking/pull/353). Base distante vérifiée : `90da8461803e87897c3d8f48627c4b704b3cfcd6`. Dernier HEAD publié avant cette correction : `5d73596a7c1ae8524676ec5e11c1cfcc7a1181c0`. Le SHA de correction et sa CI sont consignés dans le reçu de publication de cette passe.

## 1. Décisions produit effectivement reçues

- Entrée V1 ajustée acceptée : AurenMark existant, « AUREN AI » à l'entrée uniquement, accroche unique, champs centrés, sans grand titre redondant.
- Création et changement de mot de passe, préférences en deux pages acceptés ; priorités compactes en blocs, souhaits facultatifs distincts de points forts/faibles analysés.
- Ancien journal conservé ; attribution seulement après preuve serveur couvrant toutes les séances concernées. Aucune attribution par nom de compte.
- **Pas d'inventaire de matériel à gérer.** Après exposition du prototype : « Quelqu'un ne va pas commencer à manager la liste de son matériel ». Son API/client/page non committés ont été retirés. Les familles de matériel ne sont plus demandées dans « Ta disponibilité ». Les déclarations historiques restent conservées.
- Direction : profil → propositions de séances/exercices → substitutions selon les possibilités réelles. Cela ne prouve pas que la compatibilité d'une salle inconnue est résolue. Ni équipement complet supposé, ni algorithme inventé côté interface.
- Correction de disponibilité exposée en avant/après et acceptée : **« Valider la correction »**. Les futurs visuels/assets sont à préparer par tranches, selon le manifeste ; le moteur scientifique viendra par contrats versionnés et prompts fournis par l'opérateur.

## 2. Réalisé et limites

| Partie | Réalité vérifiable | Limite restante |
|---|---|---|
| Compte | API JSON inscription/changement ; validations partagées, unicité/concurrence, quotas et révocation ; consommateurs AuthSession natifs | Backend/client compatibles à déployer ; recette réelle |
| Résultats incertains | Aucune mutation automatiquement rejouée ; confirmation serveur distincte de refus/inconnu ; réponses d'un compte quitté neutralisées | Vérification sous interruption réseau/appareil |
| Journal | Partition par propriétaire, preuve avant accès/sync, ancien journal incertain conservé ; tests de changement de compte et réponses tardives | Preuve SQLite physique, force-kill et reprise appareil |
| Préférences | Lecture préalable, cadence et priorités, brouillon/confirmé séparés, enregistrement complet, refus et relecture après réponse perdue | Le Blueprint n'est pas ce formulaire de paramètres |
| Matériel | Domaine historique préservé ; aucun inventaire natif livré ; familles existantes conservées au PUT | Doctrine de contexte/compatibilité et de substitution à préciser |
| Navigation de compte | Défaut de retour identifié : remplacer ExpoRoot perdait l'onglet ; correction en gardant la coque montée, masquée aux gestes/accessibilité pendant le formulaire | Le test de montage ne remplace pas une recette native de navigation |
| Blueprint / premier plan | Quatre moments de composition disponibles sur banc isolé ; sorties MISSION existantes préservées | BodyTrainingBlueprint / FirstPlanRecommendation non reçus, aucune personnalisation complète revendiquée |
| Poids / consentement / suppression | Services existants repérés ; aucune nouvelle écriture corporelle ou suppression | Décisions et raccordements natifs restent à faire |

Le prototype de matériel a eu des tests intermédiaires mais a été retiré : ils ne sont pas comptés comme une fonctionnalité livrée. Aucun nouveau modèle, migration, moteur scientifique, asset final ou baseline validée n'est ajouté dans cette correction.

## 3. Vérifications et publication

Diff final de correction, après retrait du matériel :

- `python scripts/check_scope.py` : ISOLATED ; contrôles ciblés et broad mobile, aucun full sweep Python local.
- `npm --prefix clients/mobile test -- --runInBand` : **44 suites / 547 tests passants** ; `npm --prefix clients/mobile run typecheck` : passant.
- `pytest -q tests/test_ui_iteration_protocol.py tests/test_auren_muscle_focus_source_policy.py tests/test_native_feature_migration_map.py` : **35 passants**, deux avertissements de dépréciation de dépendances.
- Régressions observées rouges puis vertes : absence de saisie de matériel tout en conservant les familles déjà enregistrées ; un seul montage de la coque après préférences/retour. Mot de passe/résultat conserve aussi la coque ; journal inchangé.
- Budget Ruff **264 ≤ 548**, protocole et OpenSpec strict **5/5** passants. Aucun fichier Python produit changé dans le diff final.
- Export Expo + Chromium : neuf états, largeurs 320/360/430, pas de débordement horizontal, zéro erreur JS/requête externe. Build Xcode Release pour le banc iOS séparé : **BUILD SUCCEEDED**.
- Revue indépendante : défaut de navigation P2 corrigé et testé. Pas de second audit exhaustif revendiqué.

CI historique vérifiée du HEAD `5d73596` : [run 42051885745](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/42051885745), **neuf jobs réussis**, dont pytest/QA, lint/sécurité, mobile, contrat visuel et scan SonarCloud. **Check externe SonarCloud Code Analysis : failure**, titre « Quality Gate failed », condition « Code smells with severity Major found (required < Major) ». La CI du nouveau HEAD reste consignée séparément. Sonar est consultatif selon GOV-SONAR-01.

Le rendu web et la compilation iOS ne prouvent ni recette Android, ni clavier/VoiceOver/TalkBack, ni force-kill/SQLite natif. L'appareil QA MOB-02 et ses preuves sont préservés. **Aucun déploiement, merge ou archivage complet MOB-03 à ce stade.**

## 4. Paquet de tâches à retourner — PO / architecte / science

Ces tâches décrivent des livrables concrets à fournir ; elles n'ouvrent pas silencieusement un autre GO BUILD.

| ID / priorité | Responsable / décision demandée | Livrable attendu | Critère d'acceptation et suite débloquée |
|---|---|---|---|
| NEXT-01 · immédiat | Opérateur + architecte : D-MOB03-3 / STORE-00 | Matrice approuvée pour compte/credentials, séances/séries et journal local, mesures/consentements, fichiers éventuels, exports et sauvegardes : effacer/conserver, motif, durée, acteur, résultat vérifiable. Réauthentification, révocation et réponse perdue ; responsable et URL de confidentialité réels | Aucun conflit implicite avec l'invariance historique/additive-only ; exception destructive explicitement arbitrée avant code. Puis implémentation et tests sur fixtures isolées ; aucun faux effacement |
| NEXT-02 · immédiat | PO + architecte : D-MOB03-2 et périmètre corporel | Confirmer le lecteur de chronologie (`BodyMeasurement` / `body_profile.list_measurements`), traitement de `User.weight_kg` hérité sans date (proposition : omission du flux de mesures), unités réellement supportées et version/texte de consentement/retrait | Mesure datée distincte d'un héritage ; pas de date inventée, double-write ou seconde chronologie. Contrat propriétaire + sécurité/qualité avant exposition corporelle, puis croquis/API/consommateur/tests |
| NEXT-03 · fondation science | Agent scientifique, après injection opérateur ; SCI-P01 puis SCI-P02 | Contrats BodyTrainingBlueprint et FirstPlanRecommendation compatibles avec les sorties existantes : champs utiles/obligatoires/facultatifs, origine, suffisance/manques, explication, incertitude, version, fixtures. Inclure contexte matériel inconnu et rôle de la substitution, sans inventaire imposé | Tests domaine et consommateur ; aucun diagnostic de points forts/faibles à partir du simple souhait ; aucun score ou compatibilité fabriqué. Débloque compte → profil → première proposition réellement justifiée |
| NEXT-04 · recette / livraison | Architecte + opérateur + agent mobile | Plan de compatibilité backend/client, cible et rollback, GO déploiement distinct ; builds identifiés puis recette Android et iPhone connecté, en conservant MOB-02 | Compte A/B, reprise hors ligne, interruption/relance, mutation incertaine, clavier/accessibilité et journal vérifiés sur appareils identifiés. Pas de fermeture globale avant preuves |
| NEXT-05 · suite visuelle | PO designer + architecte, après ouverture explicite de tranche | Brief MOB-04 MISSION : action principale par état, composants compact/détail, explication et inconnus ; chaque donnée liée à sa source. Préparer emplacements d'assets selon la file existante | Croquis puis pixels comparés aux LOCKED, fixtures isolées étiquetées, aucune métrique décorative ni nouvel algorithme. Les données réelles attendent leurs contrats producteurs |

**Première tâche recommandée au PO/architecte : NEXT-01.** La politique des données bloque une vraie partie du compte et la préparation Store ; un nouvel écran ne peut pas la décider. NEXT-02 peut être cadrée en parallèle. Le S0 scientifique peut ensuite être lancé par l'opérateur avec ses prompts ; il doit livrer ses contrats avant de prétendre terminer le premier parcours personnalisé.

Aucune requête de secret ou création de compte Store anticipée n'est nécessaire pour ces décisions.

## 5. Roadmap maintenue et prochaine ouverture

Ordre adopté : terminer les critères MOB-03 → MOB-04 MISSION → MOB-05 Progrès/journal → MOB-06 programmes → MOB-07 constructeur → MOB-08 exercices → **réévaluer MOB-09 selon le recadrage sans inventaire** → MOB-10 substitutions → UX-LAB-PROFILE → MOB-11 profil → MOB-12 récupération/cardio → abonnement/plateforme → alpha avec preuves appareil. [Roadmap canonique](strategy/AUREN_MOBILE_CRITICAL_PATH_2026_11_03.md).

Les composants consommateurs peuvent être préparés à l'ouverture de leur tranche avec états présent/absent/en attente/inconnu/explication. Leur préparation ne ferme pas la science et ne justifie pas de remplir un cockpit de nombres fictifs. File assets conservée : mannequin de référence → Smith incliné START/END → fiche pilote → série après validation. Provenance et revue de l'asset consommé restent obligatoires ; BodyMap fonctionnel distinct des illustrations.

Le besoin matériel doit être résolu au service d'une proposition et d'une substitution, sans détour de gestion d'équipement. Le domaine de faisabilité reste en place tant qu'un changement accepté ne le remplace pas. L'inconnu n'est pas converti en salle complète.

## 6. Points différés et passage de relais

- Mineur existant : en-têtes `no-store` absents sur certaines erreurs génériques 400/401 ; aucune déclaration soumise recopiée. Ce constat ne constitue pas un audit sécurité global et n'est pas corrigé hors du diff courant.
- Le sélecteur impérial, durée, limitations et expérience n'ont pas de contrat de premier plan accepté. Un champ LAB ONLY ne doit pas être promu pour remplir le Blueprint.
- La récupération d'un compte sans email doit recevoir une aide et un parcours réellement possibles ; ne pas promettre une récupération automatique inexistante.
- PR conservée en draft : le GO MERGE permanent existe, mais les critères du change complet ne sont pas acquis. Aucun nouveau GO MERGE ponctuel à demander quand ils le seront.

À transmettre par l'opérateur : **ce CR**, [arbitrages D-MOB03](MOB03_ARCHITECT_DECISIONS_2026-11-05.md), [gaps consommateurs](MOB03_NATIVE_UI_DATA_GAPS.md), [registre science](strategy/AUREN_PRODUCT_SCIENCE_DEPENDENCIES.md) et `tasks.md` du change. Aucun message externe n'a été envoyé au PO, à l'architecte ou à un agent scientifique.

## 7. Annexe concrète pour NEXT-01 / NEXT-02 — données observées

Lecture des modèles/services et fichiers uniquement, sans inspection de données privées ni base de production. Les `ON DELETE` ci-dessous sont ceux du code ; ils ne prouvent pas que l'exécution sur une base déployée possède le même graphe ou que tout effacement est déjà sûr.

| Ensemble réel / source | Comportement observé | Réponse à fournir par l'architecte / responsable |
|---|---|---|
| Identité `users` : username, email facultatif, password_hash, session_epoch, taille et poids hérités — `app/models/user.py` | Les coordonnées/accès et le poids hérité partagent la racine de propriété | Effacement de l'identité et de ses accès ; traitement séparé de l'héritage sans date ; résultat après réponse perdue |
| Accès `device_sessions` — `app/models/device_session.py`, `device_auth` | FK users avec CASCADE ; révocation d'époque existante | Séquencement réauthentification/révocation/effacement et absence d'ancien credential encore utilisable |
| Séances `workout_sessions` → `session_exercises` → `set_logs` — `app/models/session.py` | Cascade déclarée dans le graphe ; historique métier à préserver lors des changements ordinaires | Conséquence explicite d'une suppression volontaire de compte, distinction avec l'invariance des changements ordinaires ; preuve sur graphe complet |
| Préférences, readiness, programmes personnels et enfants, refus d'adaptation — modèles `training_preferences`, `readiness`, `user_program`, `plan_adaptation_dismissal` | FK racine CASCADE déclarées ; aucun nouveau writer dans la correction | Effacement/conservation et dépendances des modèles publiés, sans détériorer les données d'autrui |
| Décisions `decision_traces`, `recommendation_episodes` — modèles homonymes | `decision_traces.RETENTION_POLICY_V1 = OWNER_LIFETIME`, pas de TTL ; trace immuable aux UPDATE, FK propriétaire CASCADE | Respecter cette politique existante ou proposer sa modification explicite ; ne pas réécrire les traces pour anonymiser sans contrat |
| Mesures `body_measurements` et consentements `body_consents` — `body_profile` | Consentement versionné/horodaté ; retrait change le consentement. La route `/body/consent` ne déclenche pas une suppression de mesures ; `delete_measurement` est une opération séparée | Texte/finalité/version et effet exact du retrait ; conservation ou effacement volontaire séparé, dépendances dérivées, chronologie et lecteur mobile |
| Références sociales historiques — `challenge.py`, `sharing.py`, `squad.py` | Certaines FK vers users n'ont pas de `ondelete` explicite : challenges, partages de modèles/séances, créateur/utilisateur de code d'invitation ; d'autres ont CASCADE | Résoudre toutes les références avant de prétendre que supprimer users suffit. Ne pas détruire les faits d'un autre membre. Cela n'ouvre aucune fonctionnalité sociale native |
| SQLite appareil — `journal.ts`, `ownershipStore.ts`, `legacyInspection.ts` | Tables `journal_sets`, `outbox`, `active_session`, `lab_metrics`, `lab_kv` ; métadonnées dans `auren-owners-v1.db` ; ancien `auren.db` conservé si propriété incertaine. `journal.reset()` efface plusieurs tables à la fois | Politique pour faits non envoyés, partition propriétaire et journal non attribué ; purge locale seulement après décision/propriété prouvée. Pas de réutilisation aveugle de reset |
| SecureStore — `credentialStore.ts` | Credential séparé du journal, clear supprime l'entrée SecureStore | Révocation serveur et retrait local cohérents ; conserver l'état inconnu si le serveur n'a pas confirmé |
| Exports et sauvegardes — `routers/export.py`, `scripts/backup_sessions.py`, `restore_latest_backup.py`, `list_backups.py` | Export web utilisateur existant et scripts de sauvegarde/restauration repérés ; aucune durée, localisation réelle ou preuve de purge déduite du nom de script | Inventaire des copies réellement exploitées, accès, durée, purge et comportement d'une restauration après effacement ; ne pas promettre l'effacement d'un export déjà téléchargé |

La [spec historique de confidentialité corporelle](strategy/SPIGNOS_BODY_PRIVACY_AND_CONSENT_SPEC.md) décrit les principes et des capacités futures ; elle n'est pas une preuve d'implémentation de toutes ses options photo/provider ou de suppression. NEXT-01/02 doivent confronter cette doctrine, le manifeste et les comportements effectivement servis. Aucun choix de durée, aucune activation photo/provider et aucune règle juridique nouvelle n'est pris par cette annexe.

## 8. Reçu de publication — correction validée

- Code et rendu accepté publiés au commit **`07b908f7461ae3901b03aba0f57a8ee66d360cf1`**, PR draft [#353](https://github.com/MFE-DSS/workout-session-tracking/pull/353).
- [CI 42058469592](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/42058469592) : **completed / success, neuf jobs Actions réussis**, dont les trois lots pytest, le job agrégé pytest/QA, lint/sécurité, contrat visuel, Jest/TypeScript, attestation et scan SonarCloud.
- Check externe de ce même commit : **SonarCloud Code Analysis = failure**, titre « Quality Gate failed », condition « Code smells with severity Major found (required < Major) ». Consultatif selon GOV-SONAR-01 ; aucune modification de seuil, issue, test ou protection pour passer.
- Base distante toujours `90da8461803e87897c3d8f48627c4b704b3cfcd6` à la vérification finale. La PR reste en draft : les critères globaux MOB-03 ne sont pas acquis, malgré les contrôles réussis du socle. Aucun merge, déploiement, archivage ou nettoyage du worktree portant la suite.
- L'annexe et ce reçu sont une publication **docs-only** postérieure au code testé ; les contrôles locaux applicables sont le protocole documentaire, sans nouveau sweep. La policy `paths-ignore: docs/**` explique l'absence attendue d'une nouvelle CI complète sur ce seul reçu, sans `[skip ci]` manuel.

Choix techniques de la passe : conserver les faits historiques en retirant leur édition de matériel ; utiliser les contrats existants tant que le Blueprint manque ; conserver la coque montée pour préserver la navigation. L'ancienne décision de ne pas refactorer un retour non démontré est remplacée par le défaut reproduit en test et sa correction P2. L'extraction commune des deux éditeurs envisagée pour le matériel a été retirée avec ce prototype. Les gates appareil demeurent, car les tests de pont SQLite ne prouvent pas une reprise après force-kill.
