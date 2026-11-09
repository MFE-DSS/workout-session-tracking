# Design — UX-CAL-02 : instrument commun compact

9 novembre 2026. **Proposé, aucun apply autorisé.** Basefe9f6e9 ; le reçu final
de389 ferme le suivi de livraison du scope précédent. [Scope](BUILD_SCOPE.md),
[avant/après et sources](UX_CAL_BOARD.md), [tâches](tasks.md).

## Context — observations directes

- `CalibrationEncounterInstrument` est le vrai présentateur partagé consommé par
  `PlanV3FirstUseScreen`. Il affiche en permanence la définition du calibrage,
  le dernier essai, les actions d'aide/pause/retrait/relecture et les faits.
- `CalibrationInstrument` met le nom en rôle exercise30 et étend Frame C selon
  le contenu. `CalibrationSetting` réserve168pt avant adaptation de fonte.
- `PrimaryAction` global a une hauteur68 ; `AccountFrame` et `AccountLink`
  servent aussi le compte. Les changer globalement toucherait d'autres pixels.
- L'observation est un formulaire unique de choix verticaux : complétion,
  réussite, qualité, gêne, date/heure et motif ; tous sont distincts et sans
  défaut positif. `observedLoad` est séparé de `load` dans le brouillon existant.
- Les brouillons sont déjà par owner/encounter/draft_ref, fermés par reçu exact.
  Le contrôleur conserve pending, génération/auth et réconciliation propriétaire.
- `capabilityEnvelope` valide sept profils et leur masse, mais ne lie pas tous
  les tuples intention/réalisation/policy à supported_realizations ;
  `calibrationEnvelope` ne les recoupe pas avec les capacités courantes.
- L'aide reçoit texte/source_ref/sha256 dans les champs existants. Les six
  procédures ont des titres H2 stables par candidate_id, sections communes et
  arrêt. Le pilote a son propre matériau avec six sections numérotées.

## Brainstorming / Options / Risques / Choix retenu

1. Réduire tailles/hauteurs globales du compte : surface trop large, exclue.
2. Compacter seulement le CSS du long formulaire : garde tous les concurrents
   à l'écran et ne traite pas l'aide/décodage ; insuffisant pour le mandat.
3. Composition locale partagée, divulgation progressive et deux durcissements
   ciblés : choix proposé, correspondant au système unique demandé. Coût :
   états locaux, reprise/focus/back à tester ; aucun changement de décision SCI.

La direction et le besoin sont fixés par l'opérateur. Les valeurs de mise en
page ci-dessous sont des propositions à G1, pas des décisions déjà acceptées.

## D1 — Surfaces et composition

Un shell local de calibrage conserve marque/header/safe areas/scroll natifs et
réutilise les primitives. Il s'applique seulement aux branches entry, choose,
minimum, context et pilot. Facts/disponibilités, proposal, ack, observed hérité,
exécution/journal gardent leur composition et callbacks ; aucune nouvelle
navigation de domaine. Le retour système suit l'étape locale et conserve les
faits, jamais un retrait ou acquittement automatique.

Dans le module : titre d'étape court une fois ; nom de l'exercice et dispositif
en contexte secondaire, réglage dans une seule RecessedWindow. Statut SCI traduit
en français une fois, avec sa limite provisoire explicite. Pas de lecture de
l'ancien essai au-dessus du réglage courant par défaut : historique dépliable,
immédiatement accessible après retrait aussi. Réglage choisi et utilisé ne sont
jamais confondus ou présentés comme recommandation scientifique.

Commande principale locale : hauteur visuelle cible48pt/dp au lieu de68, texte
bodyStrong17 ; minimum48, croissance si texte/fonte réclame davantage. Les
actions secondaires restent sobres, cibles48 et noms accessibles complets.
L'action obligatoire reste visible, désactivée avec un motif court tant que ses
faits manquent ; elle n'apparaît pas par surprise après le dernier champ.
RecessedWindow cible minimale112 au lieu de168 pour le réglage, croissance selon
texte/fonte ; rôle numérique existant40 préservé. Ces cibles ne sont pas un
engagement de hauteur fixe ou une modification de Primitive LOCKED.

L'entrée donne l'action courante : Reprendre si rencontre possédée disponible,
sinon Commencer le calibrage. L'autre voie reste secondaire ; choix/qualification
de plan uniquement depuis sources réelles. Liens de gestion regroupés sous
Détails, jamais une opération pending à réconcilier ou une alerte bloquante.
La progression initiale affiche observations conservées, pas « n/7 qualifiés »
déduit de leur nombre. Un compte exact n'est dessiné que si le DTO le prouve.

## D2 — Observation et reprise, sans changement de faits

Deux sous-étapes locales : « Ton essai » (réglage réellement utilisé, reps,
complétion et réussite explicites) puis « Ton ressenti » (qualité, gêne, motif et
occurrence). Bouton Continuer ne persiste aucune observation et ne déclenche
aucune consigne physique. Enregistrer reste la seule mutation d'observation,
avec le même payload et les mêmes gates. Retour permet de corriger les valeurs.

Choix groupés et flex-wrap, sélection visible et annoncée ; aucune valeur
précochée. « Inconnu » explicite distinct de non saisi. La date « vient de se
terminer » n'est jamais activée à la reprise ; date/heure passée s'ouvrent à la
demande et restent obligatoires si occurrence non définie. Aucun horodatage
renouvelé sans action. Formulaire de fait passé reste accessible quand le
guidage est retiré ; il ne donne aucune permission de refaire l'essai.

Le sous-écran observation est un état UI optionnel du brouillon existant,
compatible avec les anciens brouillons sans champ : valeurs conservées, choix
de sous-écran explicite ou reprise à la première section incomplète, sans perte
du contenu de la seconde. Ni version locale ni table supplémentaire. La garde
du reçu committed_event_ref garde la priorité sur tout sous-écran restauré.

## D3 — Mineur A : décodage client transversal strict

Un petit module de compatibilité client porte les sept tuples exacts livrés par
SCI : candidate_id, intent_id, realization_ref, policy_ref, load_semantics et
version d'inventaire. Sources des tuples : registry stage2-v3, registry des six
extensions et policy du pilote ; leurs fichiers restent read-only. Ce miroir
dit ce que le client sait représenter, jamais ce que SCI admet aujourd'hui.

Sous inventaire2, les capacités doivent contenir exactement les sept identités
uniques. La vérification joint par candidate_id les projections effectivement
servies : inventory.profiles porte candidat/intention/réalisation/policy/type ;
supported_realizations porte candidat/intention/réalisation/type et le libellé ;
initial_calibration_pilot identifie le seul pilote ; authority de rencontre porte
policy/version/bundles/génération. Aucun intent ou policy_ref absent d'un de ces
porteurs n'est exigé sur ce porteur, aucun champ serveur ajouté. Comparer les
champs disponibles aux tuples compatibles et entre eux. Intention
manquante, échange de realization, type de kg différent, policy incompatible,
duplication/omission ou inventaire non négocié ferment le nouveau guidage.
L'absence volontaire de négociation conserve uniquement le chemin pilote
historique, pas un fallback des six. Les réponses sans autorité gardent leurs
faits lisibles et n'ajoutent aucun allowed_action.

Le décodage de rencontre et son contrôleur recoupent le contexte/setting courant,
résultat qualifié, éventuel épisode portable et policy/bundle/génération avec
les capacités négociées du même propriétaire. Les événements historiques
conservent leur contexte exact propre : ne pas imposer à tous les anciens
réglages la valeur du choix courant, ni rejeter les faits UNKNOWN comme faux
zéros. Un mauvais DTO n'est jamais « réparé » ou converti en PER_IMPLEMENT/total.
En incohérence, conserver brouillon et retirer permission/consigne actuelle.
Un contexte d'ouverture load_semantics UNKNOWN reste valide pour aide/collecte,
jamais une consigne chargée. Ces faits ne sont pas convertis en sémantique connue.

Les ports de test sont typés explicitement pour le profil demandé ; l'en-tête
transport réellement émis et reçu reste testé. Aucun serveur ne fait confiance
à ce miroir pour autoriser une opération : toute validation autoritaire existante
reste nécessaire. Pas de changement de format JSON SCI/transport.

## D4 — Mineur B : aide ciblée, avant ouverture

Aide présente sur choix/contexte avant POST d'ouverture, puis à chaque étape.
Une réalisation doit être sélectionnée pour les paragraphes spécifiques ; sans
sélection, aide générale sans consigne chargée. La projection lit le matériau
du pilote pour le pilote, celui des extensions pour les six ; ne les mélange pas.

Pour les extensions : sections « Conditions communes et portée », « Séquence
réelle », candidate_id exact, « Arrêt, réessai et retrait » et frontière de preuve.
Pour le pilote : sections numérotées du seul pilote, dont arrêt et limites.
Afficher par étape les blocs applicables et garder toutes les conditions
communes/arrêt accessibles dans la même aide. Titres et pagination sont de la
présentation ; texte source conservé, aucune nouvelle instruction scientifique.

La table de présentation vérifie source_ref et SHA256 attendu des matériaux
livrés ; l'intégrité effective du texte est vérifiée avec l'outil de hash déjà
disponible, avant affichage comme procédure. Absence/dérive/section manquante =
procédure indisponible, faits conservés, pas de texte d'un autre exercice ni de
fallback qui autorise une action. Préoccupation/retrait affichent leur limite
et l'accès à sortie/historique immédiatement, pas cachés dans Détails.
La procédure n'est pas la notice d'un appareil réel ; acquisition réelle des
références et confirmations continue d'être exigée par le serveur.

## D5 — Touch, plateformes et accessibilité

Même sémantique métier iOS/Android. Différences natives : clavier décimal et
commande Terminé iOS ; Android back ferme d'abord clavier/aide puis revient
dans le formulaire sans envoi ni suppression. Un brouillon dirty reste conservé.
KeyboardAvoidingView/ScrollView/safe areas existants réutilisés localement.

Ordre de focus : titre, état/contexte, entrée/choix actifs, action dominante,
secondaires puis aide. Fieldsets nommés, sélection/disabled/busy annoncés,
informations critiques non limitées à la couleur. Après erreur, focus/annonce
du message utile ; ouvrir/fermer aide ramène au déclencheur. Pas d'animation
nouvelle : reduced motion statique. Fonte normale et130%/200% sans recouvrement,
options flex-wrap, scroll autorisé plutôt que troncature de fait essentiel.
Clavier visible ne masque pas définitivement la commande : scroll/focus la rend
accessible. Aucun clic dans l'aide ne confirme contexte ou acceptation.

## D6 — Mesure avant/après et board

Comparer mêmes dimensions, état et jeux de données nommés. Cibles à mesurer,
pas résultats déjà obtenus : commande68→48 hors Dynamic Type, fenêtre168→112
minimum, une seule commande dominante, moins de mots initialement visibles et
moins de défilement sur entrée/réglage. Rapporter hauteur réelle, nombre de
mots/commandes et accès à l'action pour360/390/480 et grandes fontes.
Ne pas revendiquer moins de données en supprimant leur acquisition obligatoire.

Board unique : entrée/choix, machine et haltères, familiarisation, essai,
observation, qualification/réessai/préoccupation, progression/reprise, pending/
inconnu/retrait, clavier et grandes fontes. Avant = captures natives388 ; après
= composants produits par le vrai consommateur et état serveur de test sourcé.
Vues de banc supplémentaires identifiées ; aucun payload READY servi.
Le croquis ci-joint est G1 seulement ; les pixels réels attendent le build et
leur acceptation distincte avant commit UI. Baselines existantes intouchées.

## D7 — Vérification et sortie

Tests adverses de décodage pour chaque candidat, tests de projection d'aide
verbatim/absence/dérive, vrais consommateurs contrôleur/écran/SQLite/HTTP,
équivalence des commandes avant/après, reprise/draft/ack exact et sept épisodes
vers V3/même séance. Revue code et interface SCI indépendantes. Scope-check
avant checks ; broad ciblé consommateurs, pas full sweep local systématique.
CI réelle et pixels acceptés, merge sous GOV-MERGE-01, canonique/Sonar, archive,
closeout et cleanup des seuls éléments possédés. DATA/RELEASE restent ouverts.
