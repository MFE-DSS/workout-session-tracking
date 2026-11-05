# GOV-MOB03-SPLIT-01 — socle livré, MOB03 complet ouvert

5 novembre 2026. Décision opérateur : **« Approuver cette scission traçable »**, sur le dossier `delivery-split-decision.md` de #353. Autorise la redéfinition explicite de `account-onboarding-native` en socle compte natif et consommateurs non servis ; ne déclare aucun critère différé réussi.

L'ancien scope est conservé au commit `d41eb2f49257d233b8b0adac94af6299d4c0e3ad`. La table `scope-split-traceability.md` du change/archive relie toutes ses tâches1.1–6.5 à CORE ou aux propositions réservées :
- [Données / effacement / consentement](../proposals/account-data-activation.md) : DATA01–07, tous ouverts.
- [Blueprint / première séance réelle](../proposals/blueprint-first-session-runtime.md) : PLAN01–07, tous ouverts.
- [Acceptation physique / release MOB03](../proposals/account-native-release-acceptance.md) : RELEASE01–06, tous ouverts.

Les trois suites restent des documents de proposition, sans change actif/PR concurrent ou GO BUILD. Leurs futures implémentations auront leurs OpenSpec/revue/PR propres. Les gates de sécurité, tests/CI du HEAD final, pixels applicables et revue du socle restent obligatoires ; le GO MERGE permanent s'applique seulement après leur réussite. L'archive du socle n'archive ni MOB03 complet, ni les politiques/science/recettes. Déploiement et Store restent séparément bloqués. MOB04 peut être préparé après livraison du socle, sans recommandations inventées ou GO BUILD implicite.
