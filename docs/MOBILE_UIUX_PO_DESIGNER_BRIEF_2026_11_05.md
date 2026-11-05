# AUREN mobile — dossier de cadrage pour le Product Owner designer

Date : 5 novembre 2026. Auteur : agent de réalisation. Destinataires : opérateur, Product Owner designer, architecte.

**Point de reprise :** [CR courant PO/architecte](MOB03_CR_PO_ARCHITECT_2026_11_05.md), incluant le refus d’un inventaire manuel et la correction acceptée de disponibilité.

**Statut courant : compte V1 ajustée accepté ; extension des préférences acceptée, grille compacte revue par délégation ; Blueprint complet et autres surfaces encore à arbitrer.**
**Actualisation après recadrage opérateur du 5 novembre :** lire le [recalage produit/science/artistique](strategy/AUREN_PRODUCT_SCIENCE_REALIGNMENT_2026_11_05.md) et le [registre des dépendances scientifiques](strategy/AUREN_PRODUCT_SCIENCE_DEPENDENCIES.md). Ils précisent les orientations reçues et les besoins encore ouverts. L'entrée composée est désormais la direction retenue ; le Blueprint en quatre moments est une cible à confronter au domaine, pas une maquette acceptée. Le [manifeste canonique v1.0](strategy/AUREN_MANIFESTO_V1.md) est désormais reçu et conservé intégralement ; il est distinct du mandat scientifique S0.
Le mandat PRODUCT DELIVERY reçu ensuite ouvre l'exécution MOB-03 dans son change existant, avec approbations visuelles et contrats de domaine applicables. Les autres tranches ne sont pas ouvertes par ce brief.
Révisions historiques du diagnostic : base `90da8461803e87897c3d8f48627c4b704b3cfcd6` ; socle de compte MOB-03 :
`da9b6a3e3328d4affbc59d69d57c1564585301d6`, PR draft [#353](https://github.com/MFE-DSS/workout-session-tracking/pull/353).
Les constats ci-dessous résultent d'une lecture du dépôt, pas d'une nouvelle recette appareil ou d'un audit utilisateur.

## 1. Mandat et décisions déjà obtenues

Demande opérateur : « Juste avoir la DA auren avec le LOGO et le style d'une page d'accueil d'une application digne de ce nom […] avancer sur tout les niveau UIUX […] et faire un rapport complet de ce qui te manque comme information et que mon product owner designer te donnes les informations. »

- L'identité AUREN et son logo existants sont à reprendre ; aucune nouvelle identité n'est demandée.
- Le précédent croquis réduit aux champs de compte doit être revu avant de coder l'UI.
- La transition prudente du journal est acceptée : ancien journal conservé intact, attribution après vérification serveur, connexion initiale nécessaire une fois pour cette attribution. La réalisation et ses preuves restent à faire.
- Le GO initial concernait le socle API ; le mandat PRODUCT DELIVERY autorise désormais la suite native MOB-03 sous ses gates, sans déploiement ni ouverture implicite de MOB-04.
- La recette MOB-02 reste à terminer avec l'opérateur ; ses résultats acquis ne valent pas recette des futurs écrans.

La demande porte sur une expérience cohérente. Ajouter seulement le logo au formulaire existant ne suffit pas à définir l'accueil, les transitions et les états dégradés.

## 2. Brainstorming / Options / Risques / Choix retenu

Trois approches examinées :

| Approche | Apport | Limite / risque |
|---|---|---|
| Habiller uniquement la connexion | Premier rendu rapide avec les éléments existants | Ne résout pas le premier usage ni la cohérence des autres espaces |
| Dessiner tous les écrans détaillés immédiatement | Vue globale | Fige des fonctions, acquisitions et données encore non décidées ; nombreux écrans à refaire |
| Cadrer l'expérience entière puis détailler dans l'ordre critique | Donne au designer une vue complète et débloque les premières surfaces utiles | Nécessite ses arbitrages avant la composition finale |

**Proposition de l'agent : troisième approche.** Le présent dossier exécute la demande de diagnostic global ; le choix des compositions reste au PO designer et à l'opérateur. Risques à maîtriser : nouveau style générique, promotion d'un écran de laboratoire, collecte sans usage, apparence de synchronisation sans confirmation, confusion entre un lien web et une fonction native.

Le recadrage conserve l'ordre des sprints, place MOB-03 au centre du premier vrai parcours AUREN et donne une direction d'entrée ; il n'est donc plus nécessaire de rouvrir une exploration générale sur le nombre d'écrans d'accueil.

## 3. Sources à fournir au designer — ne pas repartir de zéro

| Référence | Ce qu'elle établit | Conséquence |
|---|---|---|
| [Contrat visuel](strategy/AUREN_VISUAL_CONTRACT.md) | Statuts LOCKED / CONSTRAINED / EXPLORATION, logo, instruments, MISSION, exécution et bilan | Les références verrouillées restent la base ; leur modification exige une décision explicite |
| [Socle visuel](strategy/AUREN_VISUAL_BACKBONE.md) | Instrument d'allocation de ressource, profondeur structurelle, rôles visuels | Transposer la logique produit, éviter la décoration sans fonction |
| [Protocole d'itération](strategy/AUREN_UI_ITERATION_PROTOCOL.md) | Croquis préalable, information unique, comparaison à la référence, changement borné | Croquis puis rendu réel revus ; aucun test ne remplace l'acceptation visuelle |
| [Chemin critique adopté](strategy/AUREN_MOBILE_CRITICAL_PATH_2026_11_03.md) | Ordre MOB-03 → MOB-12 → abonnement → plateforme → alpha | La couverture de ce brief ne signifie pas ouverture simultanée des tranches |
| [Arbitrages MOB-03](MOB03_ARCHITECT_DECISIONS_2026-11-05.md) | Objectifs/unités, poids, suppression, acquisitions encore à décider | Les réponses doivent distinguer choix produit et possibilité technique |
| [Inventaire de migration](../openspec/specs/mobile/feature-migration-map/inventory.yaml) | Capacités natives, web, bloquées ; frontières métier | Ne pas dessiner une capacité bloquée comme déjà livrable |
| [Blueprint historique](strategy/AUREN_UI_BLUEPRINT.md) | Doctrine de placement/acquisition et antécédents web | Contexte, pas une instruction de recopier la plateforme ou le CSS historiques dans le natif |

Assets et implémentations à réutiliser :

- Logo : `design/auren/source/brand/mark/mark-primary.svg`, variantes compact/micro ; composant `clients/mobile/src/ui/brand/AurenMark.tsx`. Géométrie validée ; statut de nom/provenance provisoire conservé selon le contrat.
- Tokens natifs : `clients/mobile/src/ui/theme.ts` ; fond `field`, surfaces `plate`, encres, `signal` pour l'action de l'utilisateur, `system` pour l'information produite par AUREN. Aucune palette neuve demandée.
- Primitives : `clients/mobile/src/ui/components.tsx`, instruments et fenêtres déjà contractualisés. Les besoins nouveaux doivent être identifiés avant d'ajouter un composant.
- Références rendues approuvées : manifeste et images dans `clients/mobile/visual-contract/baselines/`. À ouvrir avec le designer ; le présent dossier ne constitue pas une revue de ces pixels.

## 4. État natif observé

| Surface | Réalité dans le dépôt | Écart à traiter |
|---|---|---|
| Connexion | AurenMark existant, entrée V1 ajustée avec « AUREN AI », accroche unique et champs centrés ; rendu accepté | Recette appareil, clavier et accessibilité native à terminer |
| Démarrage / reprise | Boot, reprise, journal et séance existent | Distinguer lancement, restauration, compte expiré et attribution du journal ; conserver les preuves hors ligne |
| Aujourd'hui | Route branchée sur les états MISSION de `ConnectedApp` | MISSION visuellement LOCKED ; MOB-04 reste la tranche d'extension du parcours |
| Programmes / Progrès / Profil | Routes présentes avec `PendingSpace` et ouverture du site | Coque réelle, fonctions principales pas encore migrées ; ne pas les présenter comme déjà natives |
| Onboarding | `OnboardingFlow.tsx` utilise notamment `src/lab/profile` | Référence exploratoire ; champs, valeurs et étapes pas une décision pour le compte connecté |
| Séance / repos / bilan | Surfaces existantes et contrats visuels ; recette MOB-02 partiellement acquise | Préserver ce parcours lors des nouveaux branchements, poursuivre la recette physique |
| Inscription / changement de mot de passe | API et consommateurs natifs raccordés, garde propriétaire testée, surfaces compte exposées et acceptées | Recettes appareil et déploiement compatible restent distincts |

## 5. Les deux accueils à distinguer

**Entrée sans session authentifiée** : une seule surface de marque composée, accès direct à la connexion et à l'inscription. Un utilisateur reconnu ne repasse pas par une page de bienvenue. Direction fournie dans le recadrage ; rendu et détails à valider.

**Accueil connecté « Aujourd'hui »** : orienter vers l'action réelle du moment — reprise ou MISSION — à partir des faits disponibles. Il possède déjà une référence MISSION verrouillée ; ce n'est pas une page marketing.

Options examinées dans le cadrage initial, avec décision de direction désormais reçue :

| Option d'entrée | Bénéfice | Coût |
|---|---|---|
| Accueil de marque distinct puis connexion / inscription — non retenu | Présentation claire de la promesse et des deux parcours | Une étape supplémentaire pour un utilisateur connu |
| Connexion enrichie servant d'accueil — direction retenue | Accès direct au compte, moins d'étapes | Composition réelle avec le vrai AurenMark encore à revoir |

Le brief doit encore préciser les états de retour et d'absence de réseau. Un splash ne doit pas devenir un obstacle répété. Proposition éditoriale transmise : « Ton entraînement, construit autour de toi. » ; elle sera présentée dans le rendu réel, sans page commerciale supplémentaire.

## 6. Couverture UI/UX par tranche — travaux et informations nécessaires

P0 = nécessaire au prochain parcours MOB-03 ; P1 = préparation du chemin critique suivant ; P2 = cadrage ultérieur, sans retarder MOB-03.

| ID / priorité | Surfaces et parcours à concevoir | Informations attendues du PO designer | Dépendance / garde |
|---|---|---|---|
| U01 · P0 · Entrée | Accueil avant connexion, connexion, accès inscription, récupération web | Option d'entrée, promesse exacte, ordre des actions, présence/échelle du logo, ton, contenu de pied de page | Logo existant, champs système, clavier et gestionnaire de mots de passe |
| U02 · P0 · Compte | Création, confirmation de résultat, conflit, changement de mot de passe | Rôle de l'email facultatif, textes d'aide, sortie après succès, placement des accès compte | Validation canonique ; mot de passe oublié/reset et export restent web selon MOB-00 |
| U03 · P0 · Reprise / compte | Restauration, ancien journal non attribué, vérification impossible, changement de compte | Explication courte, action de récupération, emplacement du statut, sortie sans perte | Politique de transition approuvée ; preuve serveur de toutes les séances concernées, aucune attribution par nom de compte |
| U04 · P0 · Premier usage | De la création à une première séance exploitable | Informations réellement nécessaires, facultatives/différables, ordre, possibilité de passer, retour/modification | Objectifs et unités D1 ouverts ; ne pas réutiliser les valeurs LAB ONLY |
| U05 · P0 · Préférences / environnement | Déclarations existantes utiles au démarrage | Champs exacts, vocabulaire, choix unique/multiple, non-déclaré, effet expliqué | Contrats serveur ; environnement initial distinct de l'éditeur MOB-09 |
| U06 · P0 · Compte et données | Consentement/retrait, poids éventuel, export, suppression | Compréhension et placement, parcours de sortie, confirmation, textes approuvés | D2 poids ; D3 politique effacement/rétention ; responsable/URL confidentialité STORE-00. Décisions opérateur/architecte nécessaires |
| U07 · P1 · MOB-04 MISSION | Proposition, reprise prioritaire, aucune séance, erreur, adaptation | Action principale par état, divulgation des raisons, place de l'adaptation | Référence MISSION LOCKED ; tout indicateur doit avoir sa source et sa sémantique métier |
| U08 · P1 · MOB-02 continuité | Série, repos, remplacement en attente/refusé, bilan | Éventuels problèmes réellement observés, textes incompris, hiérarchie des statuts | Préserver les surfaces verrouillées ; ne pas rouvrir tout le design de séance ; recette appareil restante |
| U09 · P1 · MOB-05 Progrès | Journal, détail séance/exercice, tendances, absence de données | Question prioritaire, période, comparaison, accès depuis bilan, densité de lecture | Pas de progrès ou score inventé ; coach-report bloqué selon son inventaire tant que dépendances non levées |
| U10 · P1 · MOB-06 Programmes | Bibliothèque, filtres, détail, sélection, plan de semaine | Critères de choix, hiérarchie modèle/personnel, effet et confirmation du changement | Domaine serveur conservé ; conflit avec séance en cours explicite |
| U11 · P1 · MOB-07 Constructeur | Création/édition, sélection exercices, prescription, sauvegarde | Modèle mental, ordre des opérations, limites et validation, sortie avec brouillon | Décider le contrat du brouillon ; ne pas promettre édition hors ligne sans support |
| U12 · P1 · MOB-08 Exercices | Recherche, fiche, historique, atlas matériel | Recherche/filtres utiles, place des illustrations et des consignes | Assets approuvés/provenance ; custom-exercise et science-muscle-focus restent bloqués selon leurs gates |
| U13 · P1 · MOB-09 Salle | Environnement, équipement disponible, changement de salle | Granularité, vocabulaire, états vide/incomplet, effet sur les propositions | Pas de matériel déduit d'un défaut local ; contrats de faisabilité conservés |
| U14 · P1 · MOB-10 Substitutions | Liste, comparaison, choix, confirmation/refus | Informations utiles au choix, filtres et ordre de lecture | Niveaux fournis par moteur ; pending distinct de confirmé ; conserver la garde de série déjà faite |
| U15 · P2 · UX-LAB-PROFILE puis MOB-11 | Compte, profil d'entraînement, mesures, octogone | Rôle de chaque zone, séparation déclaré/mesuré/calculé, navigation, confidentialité | Exploration profil obligatoire avant build ; photos et analyses gardent leurs propres gates |
| U16 · P2 · MOB-12 Récupération/cardio | Déclaration, lecture, historique selon périmètre futur | Usage attendu, information utile, limites de lecture | Aucune nouvelle formule ni interprétation médicale ; récupération sans feu tricolore |
| U17 · P2 · BIZ-01 | Présentation de l'offre, achat/restauration, droits | Offre et prix à décider par responsable produit, gratuits/payants, textes et support | Contrat commercial et plateformes distinct ; aucun paywall fictif à coder |
| U18 · Hors priorité centrale · Social | Capacités historiques à réévaluer | Prouver leur contribution à la boucle bodybuilding avant nouvelle spec | Manifeste §2/32 : ni feed ni leaderboard centraux ; présence dans le web ou le placeholder Profil ne les impose pas au produit natif |
| U19 · P2 · PLAT / alpha | Liens externes, permissions, mises à jour, support | Comportement des liens/retours, support, politique de communication | PLAT-02/03 à reprendre de leurs propositions ; OTA, identifiants et confidentialité STORE-00 ouverts |

## 7. Exigences transversales à spécifier pour chaque parcours

Le designer fournit un comportement pour chacun des états applicables, pas seulement l'écran nominal :

| Situation | Ce qui doit être défini |
|---|---|
| Chargement initial / actualisation | Information conservée, action disponible, attente annoncée sans valeur fictive |
| Première utilisation / vide | Ce qui manque et action pour avancer ; absence distincte de zéro |
| Hors ligne / retour réseau | Ce qui reste lisible et modifiable, fait local/en attente/confirmé, récupération |
| Résultat serveur inconnu | Aucune réussite inventée ni répétition automatique d'une mutation de compte |
| Erreur de validation / refus métier | Champ ou commande concerné, texte actionnable, données conservées |
| Authentification expirée / autre compte | Accès au journal protégé, reconnexion et sortie sans fuite |
| Interruption / relance / retour Android | Destination de reprise, clavier, brouillon et traitement des changements non sauvegardés |
| Action risquée | Conséquence compréhensible, réauthentification si décidée, résultat incertain traité |
| Accessibilité | Lecture VoiceOver/TalkBack, ordre du focus, libellés, grandes tailles de texte, contraste réel, cible produit au moins 44 pt, mouvement réduit |
| Formats | Petites/grandes largeurs, safe areas, clavier affiché, textes longs, iOS et Android ; aucune parité déduite d'une seule capture |

Les permissions doivent être demandées au moment utile, avec un parcours après refus. Leur besoin effectif sera défini par chaque tranche. Le designer n'a pas à résoudre les mécanismes de token, SQLite ou synchronisation : l'architecte en fournit les contraintes visibles.

## 8. Réponses attendues — paquet prioritaire MOB-03

Le PO designer peut répondre dans ce tableau, avec une référence Figma ou un document équivalent si disponible. Un lien Figma n'est pas requis pour trancher les premières questions.

| Décision | Réponse attendue | Qui tranche | État |
|---|---|---|---|
| P01 — entrée | Une seule connexion-accueil de marque ; accès inscription, pas de bienvenue répétée pour utilisateur reconnu | Direction transmise par l'opérateur | V1 AJUSTÉE ACCEPTÉE |
| P02 — message | « Ton entraînement, construit autour de toi. » | Proposition éditoriale reçue | ACCEPTÉE DANS LA V1 AJUSTÉE |
| P03 — composition | Hiérarchie fournie dans le recadrage ; vrai AurenMark, CTA et accès récupération/confidentialité | PO designer ; validation opérateur | COMPTE V1 AJUSTÉE ACCEPTÉ ; autres surfaces selon leurs gates |
| P04 — compte | Identifiant, mot de passe et confirmation à la création ; email non obligatoire artificiellement ; aide/récupération et placement changement à préciser | PO + architecte ; validation opérateur | DIRECTION REÇUE ; détails ouverts |
| P05 — acquisitions | Blueprint cible en quatre moments ; pour chaque champ : usage consommateur, obligatoire/facultatif et stockage | PO + agent scientifique/architecte | CIBLE REÇUE ; D1/D4 partiellement ouverts |
| P06 — poids | Mesure datée/historisable ; héritage sans date séparé ; chronologie et unités supportées à contractualiser | PO + architecte | PRINCIPES REÇUS ; D2 à finaliser |
| P07 — données | Politique suppression/rétention et devenir du journal local ; responsable et URL confidentialité ; textes | Opérateur/responsable + architecte, puis designer | D3/STORE-00 OUVERTS |
| P08 — états | Textes et actions de reprise, réseau absent, résultat incertain, refus, conflit | PO designer avec contrats techniques | À concevoir |
| P09 — critères de réussite | Proposition exploitable et démarrage, ou indication claire des informations manquantes | Direction transmise par l'opérateur ; contrat scientifique requis | CRITÈRE REÇU ; scénarios à prouver |

Pour les tranches P1/P2, les réponses peuvent suivre leur ordre d'ouverture ; elles ne sont pas toutes nécessaires à la première maquette MOB-03.

## 9. Livrables attendus du designer et critères d'entrée en réalisation

1. Carte des parcours MOB-03 : entrée composée retenue, accueil connecté distinct par son rôle, entrées/sorties et conditions de passage.
2. Croquis d'entrée, inscription et gestion du mot de passe avec le logo et les primitives AUREN, puis les états critiques du tableau §7. Chaque composition soumise à validation avant code.
3. Inventaire élément → information → source : champ serveur, état local ou texte éditorial approuvé. Une information ne figure qu'une fois.
4. Références visuelles annotées : ce qui est repris des baselines, ce qui est nouveau, toute demande de modification d'un élément LOCKED séparément signalée.
5. Textes finaux, spécification d'accessibilité et comportement clavier/retour ; aucun jeu de données réel ni secret dans les maquettes.
6. Validation de la composition par l'opérateur ; ensuite seulement réalisation scoped, rendu réel comparé aux références et acceptation avant commit UI.

La remise d'une maquette ne vaut pas changement du contrat métier. Si elle requiert une donnée absente, enregistrer un `UI_DATA_GAP` et faire arbitrer la capacité avant de la promettre dans l'app.

## 10. Travail possible pendant les réponses

- Préparer les contrats et cas de test de partition du journal selon la transition acceptée ; prouver l'absence d'affichage/envoi sous un autre propriétaire avant de brancher un nouveau compte.
- Préparer les états des mutations de compte, doubles appuis, réponses tardives et réponses perdues ; aucune UI nouvelle nécessaire pour définir ces contrats.
- Relier chaque décision PO à OpenSpec et au contrat API ; conserver les choix ouverts comme ouverts.
- Préparer la prochaine revue visuelle à partir des assets/baselines existants, puis réaliser la tranche autorisée après acceptation de sa conception.

Ce dossier n'annonce pas ces travaux techniques comme déjà implémentés. Il ne valide ni les fonctionnalités P1/P2, ni le déploiement, ni les recettes appareil manquantes.

## 11. Compte rendu de cette passe

Livré localement : inventaire des surfaces natives et des références, couverture UI/UX du chemin critique, décisions manquantes avec responsables et priorités, paquet de réponse pour le PO designer. Aucun nouveau composant, écran, dépendance ou baseline modifié. Aucun message envoyé au PO/architecte ; dossier prêt à transmettre par l'opérateur.

## Reprise d'exécution après mandat PRODUCT DELIVERY

Le manifeste est reçu ; [croquis consolidé](MOB03_REVIEW_BOARD_SKETCH.md) soumis avant code des nouvelles compositions. [Gaps consommateurs](MOB03_NATIVE_UI_DATA_GAPS.md) et plan natif dans le change OpenSpec. Les mutations AuthSession et la garde propriétaire sont implémentées localement avec tests ; aucune nouvelle planche visuelle n'est encore acceptée, aucun parcours Blueprint complet prétendu livré.


## Planche réalisée après validation du croquis

L'opérateur a validé le croquis le 5 novembre : "Valider ce croquis pour la planche". La [planche et son reçu de réalisation](SPRINT_MOB03_NATIVE_ACCOUNT_UI_REPORT.md) sont maintenant candidats au rendu. Les mutations de compte sont branchées au client ; les quatre moments Blueprint restent visuels et leurs gaps explicites. Aucune approbation de pixels ni livraison complète MOB-03 déduite de l'acceptation du croquis.


## Validation du rendu V1 ajustée — 5 novembre

Réponse opérateur : « Ouais, très bien, continue maintenant sur ton critical pass. On va dire que c'est validé. » La V1 ajustée est retenue : logo et accroche V1, sans grand titre d'entrée, champs centrés, « AUREN AI » uniquement à l'entrée. Le [rapport UI](SPRINT_MOB03_NATIVE_ACCOUNT_UI_REPORT.md) conserve l'avant/après et cette décision. Les mentions de candidat ci-dessus décrivent les étapes antérieures ; elles ne remettent pas cette acceptation en question. Les gaps Blueprint, la politique d'effacement et les preuves appareil restent distincts.

## Suite demandée — visuels préparés puis alimentés par la science

L'opérateur confirme le 5 novembre : poursuivre le critical path, puis enrichir la roadmap selon le manifeste par les composants, fonctionnalités visuelles et assets ; il fournira les prompts d'injection du moteur scientifique. Cette direction n'ouvre pas simultanément les autres tranches.

- Priorité actuelle : rendre utilisables les déclarations existantes, conserver compte/journal/séance et finir leurs preuves, avec les blocages Blueprint/effacement explicités.
- À l'ouverture des tranches suivantes : préparer les composants consommateurs et leurs états (donnée présente, absente, en attente, explication) avec fixtures de démonstration ; réserver les projections compacte et détaillée permises par les contrats. Aucun score, seuil, mensuration ou pourcentage décoratif.
- Assets : suivre l'ordre déjà reçu, mannequin de référence → Smith incliné START/END → fiche pilote → série après validation, avec provenance et disponibilité réelles. Préparer les emplacements ne prouve pas qu'un asset final soit livré. Le BodyMap fonctionnel reste distinct des illustrations.
- Intégration scientifique : contrats et fixtures versionnés, audit de compatibilité, tests consommateurs, puis alimentation des composants par le moteur. Le premier plan reste ouvert tant que son contrat manque.

Le croquis des deux pages de préférences est accepté : « Valider ce parcours ciblé ». Le profil complet web reste accessible en lien secondaire de cet éditeur afin de conserver le parcours existant ; ce détail est signalé dans le rendu de revue. Aucun nouvel écran P1/P2 ou nouvel asset n'est réalisé par ce seul relevé.

## Correction produit après exposition du matériel

L'opérateur refuse la gestion d'une liste de matériel ; le prototype non livré est retiré. La disponibilité native conserve la fréquence uniquement et les priorités restent compactes/facultatives ; les données historiques de matériel sont préservées. Rendu corrigé exposé et accepté : « Valider la correction ». La direction est profil → propositions → substitutions, sans déduire la compatibilité d'une salle générique. Le contrat métier de cette résolution reste à fournir ; il ne sera pas inventé côté UI. U05/U13 et l'ancienne proposition MOB-03 4.3 sont donc à relire avec ce recadrage, pas comme une obligation d'éditeur matériel. Voir le CR courant et le delta OpenSpec explicite.
