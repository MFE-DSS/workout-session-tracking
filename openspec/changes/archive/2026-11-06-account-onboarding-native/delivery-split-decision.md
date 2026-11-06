# MOB-03 — possibilité de scission, sans l'exécuter

5 novembre 2026. Un change=une PR ; GOV-MERGE-01 ne fournit pas d'exception aux critères COMPLETE. Aucun deuxième change/PR créé, aucune case globale retirée, aucun merge partiel autorisé par ce document.

Une scission cohérente est techniquement possible : livrer le socle compte et les consommateurs honnêtement indisponibles, puis séparer activation des données et intégration scientifique. Elle exige une décision opérateur versionnée et revue avant de modifier le scope courant ; elle ne peut pas être déduite de la CI verte.

| Critère actuel / code conservé dans #353 | Délimitation proposée si approuvée | État actuel sans scission |
|---|---|---|
| Compte natif/signup/password, préférences compactes, pas d'inventaire, journal propriétaire et mutations inconnues | Socle compte cohérent, contrats et acceptations visuelles existants conservés | Implémenté, preuves locales/CI ; aucune recette physique complète déduite |
| Chronologie poids unique et SDK/consommateur read-only, consentement respecté | Lecture technique dans le socle ; saisie/consentement natifs dans suite corporelle explicite | Pas de nouveau formulaire corporel ; acquisitions restent ouvertes |
| Demandes durables côté client et service serveur isolé | Code non servi dans le socle ; routes/migration/exécuteur/capacité de suivi app/web dans suite politique dédiée | Politique absente : aucune suppression/manuelle/purge acceptée réellement |
| Blueprint progressif, premier plan justifié puis séance | Page d'état honnête dans le socle ; snapshot/input canoniques, admission SCI et premier démarrage dans suite d'intégration distincte | Pas de READY réel ou passage prétendu personnalisé |
| Déploiement compatible, force-kill/SQLite, clavier/accessibilité Android/iPhone | Gates de release explicites ; leur éventuel report hors acceptation du socle doit être approuvé, jamais silencieux | Gates actuelles toujours obligatoires pour COMPLETE |

Si une scission est retenue : réécrire proposal/design/tasks et registre en conservant chaque ancien critère et son nouveau propriétaire ; ouvrir les suites en proposition uniquement, sans code concurrent ou duplication de PR ; nommer l'état du socle distinctement de «MOB-03 complet» ; garder la matrice des gates de release. Les critères nécessaires à la sûreté du socle ne peuvent être reportés au seul motif qu'ils sont difficiles.

**Décision actuelle : pas de split exécuté.** Sans arbitrage explicite, #353 reste draft et conserve tous ses critères COMPLETE. Cette analyse ne vaut ni GO BUILD d'une suite ni autorisation de MOB04.

## Décision concrète proposée à l'opérateur

Autoriser dans la même PR353 une redéfinition explicite de `account-onboarding-native` en **socle compte natif et consommateurs non servis**. Son acceptation exige CI complète du HEAD, revue sécurité/qualité, pixels acceptés et contrats/tests consommateurs ; elle n'affirme ni premier plan utilisable, ni effacement disponible, ni recette physique complète ou conformité Store. Le périmètre de code déjà approuvé est conservé.

Les critères encore ouverts sont transférés intégralement, avec ancienne case → nouvelle case :
- `account-data-activation` (proposition seulement) : politiques, migration/routes/service d'effacement app/web, suivi après révocation, traitement des faits locaux et copies ; acquisitions/consentement corporels et écritures éventuelles autorisées séparément.
- `blueprint-first-session-runtime` (proposition seulement) : acquisitions réellement nécessaires/snapshot canonique, admission SCI externe, vrai READY, handoff à une séance possédée et tests de démarrage. Ne possède pas les fichiers du producteur scientifique isolé ni ses décisions d'admission.
- `account-native-release-acceptance` (proposition seulement) : recette physique MOB03 Android/iPhone, clavier/accessibilité, comptesA/B/force-kill, compatibilité déployée/rollback et GO de déploiement distinct. Se limite aux comptes MOB03 ; ne remplace pas android-pilot-readiness, navigation-shell ou la recette MOB02.

La roadmap portera simultanément **socle livré** et **MOB03 complet ouvert**. Toute ancienne exigence transférée restera visible avec sa raison, son propriétaire et le critère d'acceptation de la suite ; aucune tâche de suite n'est marquée réussie. Aucun second PR concurrent/chevauchant ; les suites restent des propositions sans GO BUILD. Sans cette décision, aucune réécriture de scope ni fusion n'est exécutée.

## Décision opérateur reçue

**« Approuver cette scission traçable »**. Appliquée par scope-split-traceability.md et tasks.md ; trois documents de proposition réservés, sans nouveaux changes actifs ou PR concurrentes. Les paragraphes «sans décision» ci-dessus décrivent l’état antérieur. Aucun critère différé déclaré réussi.
