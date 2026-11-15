# MOB-06 — bibliothèque native et lancement possédé

## Why
L'onglet Programmes renvoie encore au site alors que le domaine possède déjà un
catalogue et des programmes personnels. Le mandat MVP demande de les rendre
utiles au pilote. Le12novembre, l'opérateur a abandonné l'essai Maltin et demandé
la reprise de feature/bibliotheque-seances ; la restriction de gouvernance est
levée par le reçu docs/pilot/mob06-library/GOVERNANCE_RESUMPTION.md.

## What Changes
Bibliothèque native dans l'onglet existant : catalogue ordonné, programmes
possédés et détails des séances/compositions prévues. Choix explicite d'une séance
démarrable, confirmation, vrais préflights et création d'une séance possédée via
les services existants et les formes supportées par le lecteur natif. Cardio et
compositions sans série de travail restent lisibles mais non démarrables dans
cette tranche, sans prétendre à une parité de tout le catalogue.
Séance déjà ouverte ou commande incertaine prioritaire,
reprise du profil réel, aucun auto-retry. Le programme lui-même n'est pas une
séance et son dépli n'est pas une configuration active persistée.

## Capabilities
### New Capabilities
- `mobile/owned-program-library` : lecture typée propriétaire, sélection, détails,
  lancement explicite et réconciliation honnête de la réponse inconnue.
### Modified Capabilities
Aucune autorité scientifique modifiée. Les points de composition Today/journal
réutilisés conservent leurs permissions ; les changements de branchement sont
bornés dans BUILD_SCOPE.md, après leases BODY/NUT.

## Impact
Nouveaux adaptateurs mobile_library/libraryReadModel/client/présentateurs et tests,
montage dans mobile_api et Programmes/ConnectedApp. KEEP_DOMAIN pour loadout,
user_program_drafts, user_program_launch, session_builder, préflight environnement
et exécution/journal. Pas de nouveau moteur, table ou migration serveur. Une table locale opérationnelle
d’intentions sur la connexion/queue possédées évite d’écraser les snapshots Legacy/V3.

## Non-goals
Pas de constructeur MOB-07, modification/publication d'un programme, duplication
de son arbre, calendrier ou configuration active inventés, génération scientifique,
substitution nouvelle, score, estimation de durée ou asset anatomique. Un planning
hebdomadaire proposé n'est pas une semaine réellement programmée. L'admission SCI
ne se transfère pas d'un contexte par une ligne de catalogue. Aucune activation,
release ou APK dans ce change.

## Visual Authority and Gates
Frame C, RecessedWindow, typographie/marque/tokens et navigation quatre onglets
restent les références. Composition compacte de liste/détail à faire accepter par
G1 puis vrais pixels iOS/Android avant commit UI. Le master BODY non accepté reste
indépendant : aucune de ses études n'est copiée. Aucune baseline LOCKED modifiée.
Design/scope/G1 et futurs pixels restent proposés, sans GO BUILD déduit du seul
abandon de Maltin. GOV-MERGE-01 reste applicable après les gates.
