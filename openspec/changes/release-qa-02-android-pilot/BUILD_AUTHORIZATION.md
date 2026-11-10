# RELEASE-QA-02 — autorisation et direction reçues

10novembre2026. Décision opérateur : **« Autoriser ce build RELEASE-QA-02 contrôlé »**.
Même réponse : l'opérateur n'a pas d'Android ; le bêta-testeur téléchargera l'APK sur son appareil. La proposition USB initiale est conservée dans les preuves privées ; le design documente le transport distant avant implémentation.

Choix technique annoncé par l'agent : APK interne autonome, HTTPS temporaire vers le seul banc synthétique local. Fenêtre liée au fonctionnement du poste/tunnel ; aucune disponibilité durable promise. Ce choix ne vaut pas autorisation de toucher production ou un backend partagé. Aucune admission SCI nouvelle, donnée réelle, Store/OTA, nouvelle composition ou permission de contacter automatiquement le testeur.

Revue de conception puis revue avant exposition : garde d'inscription/login limitée aux identités synthétiques attribuées, email vide, délais maximums et fidélité du proxy. Important reproduits RED→GREEN avant exposition ; processus/DB/settings vérifiés et identité HTTPS comparée au banc. La signature QA dédiée peut être créée selon le GO, sans remplacer la signature du pilote public. Les contrôles finaux, preuve APK et recette restent requis ; le GO n'en anticipe pas le résultat.
