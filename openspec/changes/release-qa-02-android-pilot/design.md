# Design — APK QA Android réel et cible locale

## Context

Source actuelle b8f5ffc ; Expo58.0.17/RN0.88.0, expo-modules-core58.0.24, notifications58.1.6, dev-client58.0.14 présents au lock. EAS CLI27.2.0 disponible en cache, session authentifiée, projet existant c7243bfc-29b3-4486-aafe-e69b9c904bbe. Le profil pilot vise le backend public et reste inchangé. Le poste dispose d'ADB/emulator, sans platforms/build-tools Android installés ; Java25 et8,9Gio libres ne constituent pas une toolchain locale attestée. Aucun Android connecté au premier relevé. Credentials de signature EAS à établir sans les publier ni les remplacer silencieusement.

## Brainstorming / Options / Risques / Choix retenu

1. Réessayer ExpoGo ou enlever son consommateur : ne fournit pas le module demandé, rejeté.
2. Installer tout SDK/JDK et compiler localement : coût disque/toolchain non justifié ici.
3. EAS internal/APK autonome, dépendances verrouillées et backend QA loopback : retenu. Le dev-client existe au graphe ; un APK autonome évite une dépendance Metro pour force-kill/hors-ligne. Aucun abonnement ou achat nouveau. Si EAS refuse les ressources/credentials, conserver les erreurs exactes et poursuivre les opérations indépendantes.

## Exact permitted changes

- `clients/mobile/eas.json` : ajouter `qa-android`, internal, developmentClient=false, android.buildType=apk ; API http://127.0.0.1:8140, controlled_test=1, aucun gallery, environnement EAS explicite. Le profil pilot et son URL ne changent pas.
- `clients/mobile/app.config.js` et helper/plugin QA local : activer seulement sous variante QA explicite, prioritaire sur la variante controlled_test existante ; package `dev.auren.releaseqa02`, scheme distinct, version/build relevés ; révision source et cible de test dans les métadonnées sans secret ; refuser URL différente, galerie ou révision absente/invalide. Préserver exactement la configuration normale hors QA et tester explicitement cette priorité.
- Plugin Android QA : réseau cleartext limité au seul127.0.0.1 par networkSecurityConfig, base cleartext interdite. Aucune permission réseau claire globale ou changement sur builds ordinaires. Tester le manifeste et le XML générés.
- Tests de configuration, documentation, registre et reçus de distribution ; aucun code métier SCI/auth/exécution/observation modifié. Fichier de lock conservé si aucune incompatibilité réelle ne l'exige ; tout correctif de dépendance plus large revient en revue.

## Backend and migration

Nouveau backend détenu par ce banc uniquement, b8f5ffc ou révision exacte du scope finalement construit, APP_ENV=test, port8140 loopback. Nouvelle SQLite dédiée ; appliquer réellement la chaîne Alembic base→head sur copie jetable et relever révision/schéma/FK. En cas d'échec, conserver la preuve ; ne jamais rebaptiser create_all/stamp en replay de migration réussi. Nouveau bundle privé immuable inventory2, loader/évaluateurs/validateurs vrais, packaging/science/binding/génération attestés. Activation des flags et autorité seulement sur cette base synthétique. Aucun secret ou compte dans l'APK ; comptes A/B de test.

USB/adb reverse tcp:8140 établit explicitement la connexion vers le serveur de l'hôte ; localhost du téléphone seul ne suffirait pas. Chaque commande ADB cible le numéro de série de l'appareil de test autorisé ; ne jamais cibler implicitement un téléphone personnel ou plusieurs appareils. Le test de rupture coupe/rétablit le seul reverse créé ici : mode avion ne coupe pas forcément le transport USB. Aucun tunnel public, backend public ou serveur partagé. Les accès LAN/distants éventuels demanderont leur cible/contrôle séparé. Le mode loopback est une limite explicite du premier APK et de sa checklist ; il ne ferme pas le pilote HTTPS sans câble `android-pilot-readiness`. La règle réseau borne HTTP clair et la cible API, elle n'est pas présentée comme pare-feu universel interdisant tout HTTPS.

## Build, evidence and rollback

Commit/HEAD propre avant upload, CI obligatoire et OpenSpec strict avant publication finale ; upload EAS du SHA et attestation de l'archive effective, config finale et lock hash. Toute modification de code/config/lock après construction impose un nouveau build ; une clôture documentaire ultérieure garde distincts SHA de build, SHA de merge et égalité des sources produit. L'APK reçu est inspecté : manifeste compilé/package/version, certificat réel et vérification de signature, classe native/module enregistré dans le DEX et bundle JS attestés, pas seulement graphe source ou logs FINISHED. Réutiliser signature QA applicable si disponible ; ne pas modifier une signature de distribution existante. Génération nouvelle de signature QA seulement pour l'identité QA séparée et selon accès autorisés, jamais secret dans git. Relever build ID/URI, APK SHA256/taille et preuves. Un build commencé ou FINISHED seul ne prouve pas son lancement ni une recette physique.

Audit npm de départ :29avis (3high,25moderate,1low), dont node-forge1.4.0 via CLI/code-signing-certificates et zod3.25.76 via CLI. Qualifier les appels réels de build/signature et les entrées contrôlées, sans conclure « runtime innocent » ni supprimer un gate ; faille exploitable confirmée = STOP. Le contrôle Expo propose13 alignements dont safe-area-context5.10→5.11 n'est pas un patch. Aucune correction automatique, upgrade global ou override de sécurité déduit du mandat. Correction locale dans le SDK58 seulement si un défaut réel est démontré et dans le scope revu ; changement plus large retourne en revue.

Rollback : couper les seuls flags/autorité de test sous nouvelle génération, conserver lectures/commandes/faits, vérifier BLOCKED et rejeu CREATED même séance. Arrêter uniquement processus du banc ; retirer adb reverse après recette, sans effacer application/journal/appareil utilisateur ni downgrade DB. APK QA distinct n'écrase pas une installation personnelle.

## Acceptance

Installer et lancer sur Android physique autorisé, relever modèle/OS/signature/version et logcat sans exception native. Puis signup/login/token, clavier décimal/Back, acquisition réelle de sept contextes sous données synthétiques explicitement étiquetées, V3/incertitude/ack exact, création/rejeu, journal machine et PER_IMPLEMENT, force-kill/SQLite, réseau, A/B, clôture/lecture. Pas de faux statut natif depuis HTTP. Progrès/Nutrition non intégrés : UNAVAILABLE, pas placeholders nouveaux. Émulateur et HTTP sont preuves complémentaires séparées.


## Operator GO and remote-tester steering — 10 novembre2026

GO explicite : « Autoriser ce build RELEASE-QA-02 contrôlé ». Dans la même réponse, l'opérateur précise qu'il ne possède pas d'Android ; le pilote téléchargera l'APK sur son téléphone. Le design USB ci-dessus conserve l'instant de proposition, copié dans le reçu privé USB_DESIGN_AT_GO. Le transport effectif suivant remplace l'option USB avant tout code de configuration ; aucune nouvelle fonctionnalité ou activation réelle n'est autorisée.

Choix d'ingénierie annoncé : APK autonome QA distant, API HTTPS temporaire via cloudflared déjà installé, vers ce seul banc local synthétique. Le poste doit rester allumé pendant une fenêtre de recette ; arrêt du tunnel rend l'APK hors ligne, pas connecté à production. Un hébergement permanent/partagé ou changement de production demande sa cible/autorisation distincte. Pas de compte cloud nouveau, achat, DNS de production ou secret de tunnel dans APK. Le fournisseur termine TLS : aucune donnée personnelle ou compte réel ne doit traverser ce banc.

Delta effectif borné : profil `qa-android` internal/APK non dev-client, package `dev.auren.releaseqa02`, flag controlled1, URL HTTPS exacte attestée/pinée au build et SHA source. `app.config.js` délègue au helper QA uniquement sous variante explicite prioritaire ; configuration ordinaire préservée. Refuser galerie, URL publique du pilote, HTTP/LAN/loopback, mauvaise révision ou cible non identifiée. **Pas de plugin cleartext ni d'exception HTTP dans cet APK distant.** Aucun Metro ou fixture servi.

Ajouter `tools/release_qa_gateway.py` et tests : passerelle loopback8141 vers backend fixé127.0.0.1:8140, seuls chemins mobile API v1/v3 et identité QA expurgée ; aucun web/admin/docs/fichier, URL arbitraire ou redirection vers autre hôte. JSON/formulaires transmis sans altérer le corps/empreinte ni les headers de contrat/If-Match. Bearer validé par le vrai backend ; limites de taille/concurrence/temps et débit, rejet de framing ambigu/paths traversants, pas de journal d'URL sensible, corps, token ou IP personnel. Connexion HTTPS terminée au tunnel puis lien loopback. Tests de proxy réel, parcours HTTP réels et revue indépendante avant exposition API. La preuve TLS et d'identité distante est acquise avant de figer la cible dans l'APK. Les erreurs d'amont restent des erreurs de transport, jamais un DENIED scientifique inventé.

La fenêtre distante ne ferme pas `android-pilot-readiness`, DATA ou la release. Une fiche courte pour le testeur exige comptes/valeurs synthétiques, modèle/OS, version/empreinte et retours PASS/FAIL/UNAVAILABLE. Pas de contact automatique du testeur, de recette physique inventée ni de nouvelle baseline.
