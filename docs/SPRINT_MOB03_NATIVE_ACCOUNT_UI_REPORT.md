# MOB-03 — planche native de compte et premier usage

5 novembre 2026. Statut : **candidat rendu, acceptation visuelle en attente**. Worktree isolé `sb/mob-03-account-core-build`, HEAD publié toujours `da9b6a3` / PR draft #353 ; modifications de cette passe non committées. Aucun déploiement ni remplacement du client QA MOB-02.

## Brainstorming / Options / Risques / Choix retenu

Le mandat PRODUCT DELIVERY fixe l'entrée unique avec le vrai logo et un premier parcours progressif. Reprendre les primitives, champs natifs et API de compte existants permet des mutations réelles ; les acquisitions sans API restent uniquement sur un banc clairement marqué. Autre option écartée : brancher les fixtures du labo comme profil de compte, ce qui fabriquerait une persistance et une personnalisation.

Risques traités : double appui, réponse de compte perdue, secrets hors mémoire de formulaire/SecureStore, propriétaire non vérifié, vérifications concurrentes, retour Android, clavier et petites hauteurs. La preuve physique et les contrats scientifiques manquants ne sont pas remplacés par une preview web.

## Croquis validé

Source : [MOB03_REVIEW_BOARD_SKETCH.md](MOB03_REVIEW_BOARD_SKETCH.md), opérateur : **« Valider ce croquis pour la planche »**. Entrée avec AurenMark → inscription → résultat ; quatre moments Blueprint ; compte/mot de passe ; reprise/identité incertaine. La présente réalisation ne crée aucune nouvelle baseline approuvée.

## Inventaire — une information, une seule fois

| Élément | Information | Source | Doublon ? |
|---|---|---|---|
| AurenMark et nom adjacent | Marque, dessin décoratif et nom accessible | Composant LOCKED AurenMark, géométrie inchangée | non |
| Accroche d'entrée | Promesse éditoriale | Proposition reçue dans le recadrage | non |
| Champs compte | Brouillon de saisie, aucun résultat implicite | État mémoire du formulaire, envoyé à AuthSession | non |
| Refus / résultat incertain | Résultat réel d'une mutation ou absence de réponse | AccountOutcome issu de l'API canonique | non |
| Confirmation de compte / mot de passe | Confirmation serveur uniquement | AccountOutcome confirmed ; aucun timeout présenté comme succès | non |
| Compte en paramètres | Identité vérifiée, ou absence de nom confirmé hors ligne | /auth/me, jamais username seul pour attribuer le journal | non |
| Vérification du journal | Propriété à établir, chargement ou reconnexion | Garde ownership + état de requête, sans détails étrangers | non |
| Blueprint sur le banc | Composition candidate, champs non persistés | Croquis ; UI_DATA_GAP-01 à 04, pas un vrai profil | non |
| MISSION sur le banc | Référence visuelle existante de démonstration | Fixture canonique existante, explicitement étiquetée hors écran | non |

## Comparaison avec la référence validée

| Référence | Ce qui doit survivre | Constat |
|---|---|---|
| AUREN-MARK-V1 | Composant, géométrie, encres par tokens | réutilisé sans redessin |
| theme.ts / PrimaryAction / SheetRow | Rôles field, plate, ink, signal, system ; contrôle canonique | conservés ; aucune nouvelle palette ni dépendance |
| Connexion avant changement | Identifiant/mot de passe natifs, gestionnaire système, soumission protégée | nouveau rendu comparé à la source exacte HEAD dans entry-before.png |
| MISSION-SCREEN-V1 | Géométrie et données de la référence | composant/fixture inchangés, aucune nouvelle prescription |
| Nouveaux formulaires / Blueprint | Pas de composition précédente approuvée à prétendre reproduire | candidats du croquis validé, pixels à accepter |

La copie de l'ancien écran utilisée pour l'avant n'est pas intégrée au produit. Les baselines du contrat visuel restent intactes.

## Changement unique de l'itération

Mandat explicite : planche consolidée entrée/login, signup, résultat, point de départ, disponibilité, priorités/contraintes, premier plan, reprise/auth expirée, propriétaire incertain et paramètres/suppression. Chaque surface est isolée sur le banc ; les changements sont regroupés pour la revue demandée, pas fondus dans une prétendue acceptation globale.

L'avant/après concerne l'entrée existante ; les autres nouvelles compositions sont exposées séparément. La MISSION constitue une référence de continuité, pas un écran redessiné.

## Réalisation vérifiable

- `LoginScreen`, `AccountForms` : entrée, inscription et mot de passe avec vraie saisie native, gestionnaire de mots de passe, confirmation, garde synchrone, chargement, refus et résultat inconnu. Les erreurs ne reprennent aucun secret.
- `ConnectedApp` : nouveaux consommateurs de /auth/register et /auth/password ; confirmation, identité vérifiée, journal attribué avant MISSION. Aucun profil LAB ONLY promu.
- Réauthentification après mot de passe incertain : les commandes restent dans leur partition ; la vérification des accès ne dépend pas d'un faux effacement ou de l'envoi préalable de commandes avec des accès potentiellement révoqués.
- Paramètres dans l'espace Profil, distincts du futur cockpit profil ; export/récupération web annoncés comme externes, pas de Bearer dans une URL. Confidentialité seulement si une URL HTTPS réelle est configurée ; cette destination reste ouverte dans STORE-00.
- Suppression indisponible dite explicitement, aucun bouton de faux effacement. Politique backend toujours bloquante pour son implémentation.
- Banc `EXPO_PUBLIC_GALLERY=mob03-account` : vingt cas candidats/référence, sans réseau ni persistance ; les quatre étapes Blueprint restent isolées dans `account/review` et ne sont pas branchées sur le compte réel.

## Rendus et vérifications

Planche web réelle : `http://127.0.0.1:8093/`. Cas plein cadre : `?case=entry`, `signup`, `password`, `password-done`, `owner-offline`, etc. Les captures et logs de la passe sont conservés dans `.superpowers/sdd/native-account-delivery/review/` (local, ignoré par git).

Export Expo web réalisé ; Chromium : aucune erreur JS ni requête externe pendant la capture et le parcours de démonstration. Parcours du banc exercé : entrée → inscription, confirmation différente refusée, correction → compte créé → premier moment Blueprint. Largeurs 320/360/430 : pas de débordement horizontal, action atteignable en petite hauteur 430. Cela ne prouve pas le clavier système, VoiceOver/TalkBack ou les grandes tailles de texte natives.

Dernière vérification : **41 suites / 523 tests mobiles verts**, TypeScript vert, **18 gardes UI/contrat visuel vertes** (deux avertissements de dépendances), protocole vert et OpenSpec strict 5/5. Export web et contrôles navigateur passants. La preuve iOS est consignée séparément après compilation. Aucune recette Android physique ou émulateur disponible dans cette passe.

## Revue et limites

La revue indépendante a identifié une vérification propriétaire sans single-flight : corrigée avec verrou immédiat, état checking et test rouge puis vert. La confirmation password absente du banc, initialement classée mineure, est traitée comme importante pour cette livraison : elle doit être exposée pour respecter l'approbation visuelle avant commit ; cas password-done et test dédié rouge puis vert ajoutés. Aucun autre verdict d'audit exhaustif revendiqué.

L'outil de contrôle visuel a refusé l'accès à Simulator ; les gestes et le clavier natifs ne sont donc pas déclarés vérifiés par ce moyen. La compilation/capture via Xcode constitue une preuve différente, à consigner lorsqu'elle est obtenue. La suppression, le Blueprint persistant et le contrat FirstPlanRecommendation restent des travaux non livrés.


## Preuve iOS obtenue et revue opérateur restante

Build Xcode **Release iphonesimulator réussi**, application de banc séparée `dev.auren.review.mob03`, installée uniquement sur **iPhone 16e simulé / iOS 26.3**. JavaScript embarqué ; aucune connexion backend du banc. L'entrée native est capturée dans `ios-entry.png` (1170×2532, @3) et inspectée visuellement. Le reçu `ios-render-receipt.json` conserve l'identifiant, la configuration et l'empreinte du bundle.

L'ouverture des autres cas via URL a déclenché une confirmation système « Ouvrir dans AUREN MOB03 Review ». Ces fichiers ne sont pas comptés comme rendus natifs valides ; une capture de l'obstacle est conservée distinctement. Le contrôle visuel Simulator avait été refusé par l'outil : aucune confirmation système n'a été contournée, aucune interaction/clavier natif revendiqué. Les vingt cas complets sont disponibles en rendu web, les formats étroits restant des previews et non des recettes Android.

À faire avant commit UI : acceptation opérateur du rendu candidat conformément à CLAUDE.md §5.1 (« L'opérateur tranche. »). Cette validation de pixels ne ferme ni les UI_DATA_GAP, ni la suppression, ni la recette physique MOB-03. PR #353 demeure en draft au HEAD publié initial ; aucun déploiement réalisé par cette passe.

Retour au bon onglet après le parcours de mot de passe : à vérifier dans la recette native connectée. La revue statique n’a pas démontré une régression de route ; aucun refactor spéculatif du routeur n’a été fait pour la masquer.


## Itération V2 — logo, mots-clés et axe central

Demande opérateur précise : marque beaucoup plus grande, possibilité de filigrane centré, identifiant/mot de passe centrés ; remplacer l'introduction en phrases par des mots-clés de bodybuilding donnant accès au cockpit personnel.

### Croquis validé

La demande précise vaut croquis pour cette modification (G1), consignée dans MOB03_REVIEW_BOARD_SKETCH.md §Itération V2. Options : grand emblème d'en-tête ou filigrane central. Choix retenu : exemple de filigrane central transmis par l'opérateur, sans modification de géométrie AurenMark. Aucun nouvel instrument, chiffre, profil connu ou résultat d'IA ajouté.

### Inventaire — une information, une seule fois

Entrée : AUREN nomme la marque ; grand symbole décoratif ; « Cockpit bodybuilding » nomme le produit ; « Intelligence d'entraînement » pose sa fonction ; Corps / Programme / Progression orientent les usages. Les deux champs restent des brouillons natifs, le CTA garde sa sémantique d'authentification. Inscription : Profil / Données / Entraînement, puis champs réels. Confirmation : seul fait confirmé de création et accès à la suite. Aucun « parfaitement personnalisé » ni score d'IA prétendu.

### Comparaison avec la référence validée

V1 capturée avant cette passe dans review-v2-before/ (entry, signup, created) ; V2 dans review/. Comparatif local : http://127.0.0.1:8093/comparatif.html. AurenMark géométrie inchangée ; tokens inchangés ; MISSION/instruments/baselines intacts. La V1 avait été soumise et commentée, pas approuvée comme nouvelle baseline.

Filigrane : token ink à alpha 0,075 sur field, pic résultant mesuré #1C1C1E. Contraste minimum des encres sur ce pic : ink **15,31:1**, ink2 **9,01:1**, ink3 **5,63:1**. Les champs opaques gardent leur couple de contraste existant ; le décor est non interactif et masqué à l'accessibilité. Aucun nouveau token sémantique créé.

### Changement unique de l'itération

Une même correction de hiérarchie, présentée séparément sur trois surfaces demandées : entrée, inscription, confirmation. Aucun changement d'API, de mutation ou de journal. Les autres états reprennent ces compositions lorsqu'ils montrent ces mêmes formulaires.

Vérification V2 : 523 tests mobiles/41 suites et TypeScript verts ; export Expo et contrôles navigateur verts, zéro erreur JS, zéro requête externe ; 320/360/430 px sans débordement, CTA accessible à faible hauteur. Pixels toujours candidats, aucun commit UI ou déploiement.

Build iOS V2 incrémental réussi. La capture est encore recouverte par la confirmation système d’ouverture : conservée comme `ios-entry-v2-obstructed.png`, elle n’est pas comptée comme écran V2 natif intégral vérifié. La revue V2 exploitable est le rendu web et son comparatif ; aucune capture masquée ou retouchée ne remplace cette limite.

Précision « tout en étant minimaliste » : retrait du descripteur « Intelligence d’entraînement », qui doublait la promesse du titre. Logo en fond, titre unique, trois mots-clés, saisie et CTA ; aucun ajout de bloc. Ajustement demandé directement, sans modification de comportement ni nouvelle palette.

## Retour opérateur — V1 ajustée, remplace la proposition V2

### Croquis validé

Demande : « je préfère […] la V1 », « retire ton espace entraînement », « identifiant mot de passe […] centré », et « AUREN AI […] juste […] ce moment-là spécifiquement ». La demande précise constitue le croquis de cette correction ; elle est consignée dans MOB03_REVIEW_BOARD_SKETCH.md. Choix retenu : rétablir la V1 et limiter les ajustements à l'entrée. La V2 est conservée comme historique, sans être retenue.

### Inventaire — une information, une seule fois

Logo V1 conservé ; nom « AUREN AI » uniquement sur l'entrée ; accroche « Ton entraînement, construit autour de toi. » présente une seule fois. Le titre « Ton espace d'entraînement » est retiré. Libellés et saisie identifiant/mot de passe centrés. Connexion, création et récupération conservent leurs actions. Inscription et confirmation retrouvent la V1. Aucun résultat d'IA ni personnalisation calculée revendiqué.

### Comparaison avec la référence validée

Le comparatif http://127.0.0.1:8093/comparatif.html expose V1 initiale et V1 ajustée. Capture actuelle `review/entry.png` inspectée ; logo, palette et accroche V1 conservés. Ni la préférence V1 ni cette correction ne sont interprétées comme acceptation préalable des nouveaux pixels. Le rendu iOS antérieur ne constitue pas une capture de cette version ajustée.

### Changement unique de l'itération

Retour à la composition V1 avec correction ciblée de l'entrée : suppression du titre, centrage des champs et nom d'entrée demandé. Aucun changement de comportement, d'API, de journal ou de nom ailleurs dans le produit.

Vérifications de cette correction : **48 tests ciblés formulaires/ConnectedApp et TypeScript verts** ; export web actualisé ; parcours navigateur et formats 320/360/430 px passants, action atteignable en hauteur 430 px, aucune erreur JS ni requête externe. Le résultat 523 tests ci-dessus appartient à la passe précédente. Aucun commit UI, push ou déploiement ; acceptation du rendu encore attendue.


## Acceptation opérateur — 5 novembre 2026

Après exposition du comparatif V1 ajustée, réponse reçue : « Ouais, très bien, continue maintenant sur ton critical pass. On va dire que c'est validé. » Le rendu V1 ajustée est accepté ; la proposition V2 est abandonnée. Cette acceptation autorise la livraison des compositions de compte exposées, sans transformer les quatre moments Blueprint de démonstration en parcours persistant, ni valider un contrat scientifique absent. Aucun déploiement ou recette physique supplémentaire n'en est déduit.

## Suite indépendante — déclarations d'entraînement canoniques

### Brainstorming / Options / Risques / Choix retenu

Options : étendre la lecture minimale MOB-02 existante, ou fournir une ressource explicite de déclarations. Choix technique : `GET/PUT /me/training-preferences/declarations`, sans changer la réponse historique utilisée par le bilan. L'API délègue au service canonique `training_preferences`, conserve null/[] et l'ordre des priorités, et ne change aucun vocabulaire ni effet de recommandation. Le PUT exige les trois champs hérités ; l'environnement concret a son propre writer et reste intact. Aucun nouveau champ durée, expérience, poids ou anatomie n'est introduit.

Préflight : adaptateur limité dans `app/routers/mobile_api.py`, inventaire de routes MOB-00, tests de vraie API et client TypeScript isolé. Le service, les modèles et la science restent inchangés. Pas de collision observée dans ce worktree ; aucun changement de schéma. Risques : effacement implicite par requête partielle, coercition de booléens/chaînes, reprise d'une écriture après réponse perdue, réponse d'un compte quitté. Tests attendus pour chacun. Le client n'applique pas de cache ou file hors ligne ; erreur réseau = résultat inconnu, lecture explicite pour vérifier, aucune répétition automatique du PUT. Cette tranche ne raccorde pas encore les quatre acquisitions de la planche au produit.


## Relecture des décisions avant livraison native

Registres relus : DESIGN_DECISIONS_HOME_UIV2 et DESIGN_DECISIONS_UIV2_SURFACES avec leurs amendements mobiles.

| Décision | Résultat pour cette tranche |
|---|---|
| D1 | Contrôles natifs canoniques réutilisés ; pas de portage du CSS web. |
| D2 | Aucune recommandation « IA » revendiquée. « AUREN AI » est le nom d'entrée expressément demandé et accepté le 5 novembre, sans effet scientifique attribué au moteur. |
| D3, D4, D5 | Références visuelles legacy selon amendement ; tokens natifs conservés, aucune suppression des surfaces entraînement. |
| D6 | Non concernée : logique du cycle et MISSION non modifiées. |
| D7 | Non concernée : aucune nouvelle métrique ou streak. |
| D8 | Non concernée : onglets inchangés. |
| D9 | Respectée : aucune séance N+2 ou résultat futur inventé. |
| Q1 | Structure sobre marque/accroche/formulaire/actions respectée ; texte remplacé par la direction MOB-03 et accepté avec la V1 ajustée. Aucun retour d'entrée sans destination. |
| Q2 | Non concernée : accueil connecté conservé. |
| Q3 | Respectée : aucune saisie d'état quotidien 1–5 réintroduite. |
| Q4 | Sémantique de série conservée ; aucune géométrie d'instrument changée. |
| Q5, Q6, Q7, Q8 | Références legacy mobiles selon amendement ; primitives/tokens natifs réutilisés, une action principale par formulaire. |

Preuves web conservées dans [entrée](evidence/mob03-account-v1/entry.png), [inscription](evidence/mob03-account-v1/signup.png) et [confirmation](evidence/mob03-account-v1/created.png). Ces fichiers sont des reçus de revue, pas une promotion de baseline LOCKED ni une preuve physique.

## Revue indépendante de l'adaptateur des déclarations

Aucun Critical/Important démontré. Un Minor différé : les erreurs génériques 400/401 ne portent pas toutes Cache-Control: no-store ; aucune valeur de déclaration n'y est renvoyée. Les réponses de données et 422 sanitisées portent cet en-tête. Périmètre de revue limité aux routes/client déclarations et option d'auth sans replay ; les autres limites de recette et du Blueprint ne sont pas levées.


## Vérification avant publication de cette passe

Tier effectif `SHARED_CODE` après l'adaptateur de routes ; aucun full sweep Python local. **42 suites / 531 tests mobiles verts, TypeScript vert ; 274 tests backend ciblés/broad et gouvernance UI verts** (deux avertissements de dépendances). Ruff nouveau code propre, budget **264/548** ; Bandit ciblé propre ; protocole et OpenSpec strict **5/5** verts. Le lancement initial du broad a été corrigé après un nom de fichier de test inexistant, et le budget relancé avec le chemin Ruff du venv ; aucun échec produit masqué par ces corrections de commande.

Le rendu compte accepté et les artefacts sont prêts pour la PR draft #353. Les gardes de livraison complète restent ouvertes : Blueprint connecté, SCI-P01/P02, données/effacement, recettes appareils et déploiement séparé. La publication du sous-ensemble ne vaut pas readiness globale de merge ou archivage MOB-03.


Le manifeste est conservé octet pour octet depuis la pièce fournie : les fins de ligne à deux espaces sont les sauts Markdown du texte canonique, pas une réécriture. `git diff --cached --check` signale ces espaces intentionnels ; contrôle du reste du diff propre, exception limitée à ce document et empreinte d'origine vérifiée.

## Arrêt CI et correction minimale du faux positif documentaire

Run 42042184665, job `lint (ruff budget + bandit + actionlint + shellcheck)`, étape `gitleaks scan (required — Sb_26.4)` : `leaks found: 1`, règle `generic-api-key`, brief UI/UX ligne 8 dans le commit publié. Inspection du fichier : référence de révision Git, dont l'objet est vérifié par `git cat-file`, aucun credential. Reproduction locale avec le même intervalle Git : une seule détection, même fichier/ligne/empreinte. Scanner local 8.30.1, CI 8.24.3 : versions consignées, résultat CI réel requis après correction.

Options : réécrire l'historique publié (interdit), exclure tout le document (trop large), ou qualifier cette seule occurrence. Choix : une empreinte historique exacte dans `.gitleaksignore`, sans changement de règle, de workflow ou de scan. Aucun faux secret dans un test versionné ; un signal synthétique temporaire vérifie que le scanner continue de détecter d'autres occurrences. Pas de correction produit en cascade pendant cet arrêt.


Correction vérifiée localement : le scan historique passe de 1 détection/exit2 à 0/exit0 ; une nouvelle occurrence synthétique dans le même nom de document et à la même ligne reste détectée/exit2. Valeur synthétique détruite avec son répertoire temporaire, jamais imprimée ni versionnée. check_scope classe ce delta ISOLATED ; aucun code Python/TypeScript changé, budget264/548 et protocole verts. L'exception ne couvre que l'empreinte de révision documentée. Validation CI réelle du commit correctif encore requise.
