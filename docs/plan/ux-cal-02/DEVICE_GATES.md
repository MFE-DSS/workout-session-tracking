# UX-CAL-02 — gates natives et release encore ouverts

9 novembre 2026 — Europe/Paris. **OPEN / NOT_ACTIVATED.** L'acceptation du delta
visuel contrôlé ne ferme pas la recette appareil. Les exigences OpenSpec restent
inchangées ; 3.2/3.3 ne seront cochées qu'après preuves complètes.

| Gate / tâche | Preuve acquise | Reste requis / responsable |
|---|---|---|
| 3.2 chaîne native complète | Vrais contrôleurs/HTTP, sept DTO décodés, parcours HTTP synthétique jusqu'à même séance/journal ; vrais présentateur/écran natifs | RELEASE / recette mobile : parcours de recette bout en bout sur comptes synthétiques dans l’app native complète : sept rencontres → snapshot/V3 → ack exact → même séance/journal, SQLite et reprise ; conserver captures/logs/SHA/cible |
| App Android complète | Banc Expo Go natif séparé et vrai écran d'entrée | RELEASE / intégration mobile : vérifier la cible possédant ExpoTopicSubscriptionModule ; son absence bloque ConnectedApp dans l'hôte actuel, aucun module supprimé pour contourner |
| 3.3 clavier / décimal / safe areas | Champs/unité observés, rendus natifs | RELEASE / QA mobile : saisie effective décimale, clavier visible, défilement/actions atteignables et safe areas ; tentative CUA interrompue sans preuve de succès |
| 3.3 grande fonte | Android1,3×/2× ; iOS1,353×/2,143×, défilement observé | RELEASE / QA mobile : vérification interactive exhaustive du parcours/actions à grande fonte ; captures seules insuffisantes |
| 3.3 retour Android | Tests consommateur de back et gardes sélection/focus | RELEASE / QA Android : retour système/matériel réel, racine/aide/sous-étapes et brouillon conservé, sans validation implicite |
| 3.3 accessibilité | Arbre AX iOS champ/unité/actions/aide ; tests ciblés de focus | RELEASE / QA accessibilité : VoiceOver/TalkBack effectifs, ordre/annonces/focus modales/reprise ; aucun PASS lecteur d'écran prétendu |
| 3.3 interruption / mouvement réduit | Tests brouillon strict/ancien draft/reçu exact et modale statique | RELEASE / QA mobile : interruption/force-kill/reprise/SQLite et réglage OS réduire les animations sur vraie cible |
| Appareils physiques / binaire autonome | Aucun contrôle physique ou binaire autonome nouveau | RELEASE / opérateur et QA appareils : artefacts installables identifiés et recette Android/iPhone physiques autorisée |

Le scope contrôlé permet de nommer une gate inexécutable comme limite, pas de
modifier l'exigence ni d'en fabriquer le PASS. Les tâches ouvertes sont reprises
par RELEASE/QA mobile avant déclaration de recette complète, élargissement ou
activation réelle. Elles ne créent pas de GO BUILD implicite.

DATA : politique, finalités/consentements applicables, copies/export/effacement
et autorisation du traitement réel OPEN. RELEASE : cible/SHA/config/artefacts,
autorité opérationnelle, sécurité/qualité applicable et GO déploiement séparé
OPEN. MOB03 complet OPEN. Aucun Store/OTA/activation autorisé par ce closeout.
