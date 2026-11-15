# Design — MOB-06 bibliothèque native

GO BUILD/G1 reçu (AUTHORIZATION.json), code contrôlé en cours, pixels non acceptés. Reconnaissance des domaines3cf77e1 ; base canonique de reprise
1462482a4e2bcd1fcde121d6f207a2131616e849 après PR405, correction documentaire
sans changement de ces domaines.

## Context — Observed
Programmes est PendingSpace, /library web réunit catalogue et programmes possédés.
Loadout distingue SessionRow/ProgramRow, ordre display_order/slug, sections
core/utility/specialization, filtres de zones demandés et résolution canonique.
Les lignes archived/user ne sont pas du catalogue partagé. list_drafts et
resolve_owned_published_template portent l'appartenance ; un brouillon ou un
programme archivé n'est pas démarrable. La publication matérialise ses templates.
TemplateExercise.id/code/name/machine_slug restent des identités de source ; une
égalité de nom ne prouve pas une réalisation scientifique canonique.

POST /api/mobile/v1/sessions existe pour les gabarits ; le web possède aussi le
lancement d'une séance d'un programme. Tous réutilisent instantiate_session et
les préflights. Le start natif actuel est lié à HISTORICAL_READY/MISSION : il ne
peut pas être branché tel quel à une sélection de bibliothèque. Le journal
possède déjà un marqueur de création legacy incertaine et les contrôleurs de
reprise Legacy/V3. Aucun reçu idempotent de création library n'est stocké dans
WorkoutSession ; le présent design ne prétend pas en disposer.

## Goals / Non-goals
Lire, comprendre, choisir et commencer une séance réellement admissible sans
passer par le web, puis retrouver ses faits dans l'exécution/journal existants.
Préserver la différence composition prévue / faits exécutés / permission actuelle.
Pas de classement opaque, second modèle de programme, writer de programme,
calendrier inventé, nouveau moteur SCI ou transfert d'une charge qualifiée.

## Brainstorming / Options / Risks / Choice
1. Consultation seule : contrat de lecture plus petit, mais le pilote reste privé
   du lancement depuis le choix effectué. Ancienne proposition agent non acceptée.
2. Bibliothèque et lancement contrôlé sur domaines existants : approche proposée,
   répond au mandat sans nouveau moteur ; exige de découpler le start de MISSION
   et d'expliciter l'incertitude legacy.
3. Inclure constructeur/génération/calendrier : élargissement écarté ; MOB-07 et
   les contrats d'une véritable organisation de semaine restent distincts.
Le périmètre et G1 sont acceptés par la décision exacte conservée dans AUTHORIZATION.json. Maltin n'est plus un choix ou une dépendance à lui faire arbitrer.

## Decisions — Proposed
D1. Un registre typé : catalogue commun et programmes de l'utilisateur, dans
leurs sections canoniques. Filtres explicites, pas de personnalisation cachée.
Le vide personnel reste visible sans déclarer un filtre vide « aucun programme ».
Pas de liste globale d'une autre personne, pas d'archive visible à lancer.
D2. Détail d'un programme = séances, état brouillon/publié, identité/version
existantes et champs réellement connus. Le programme n'a pas de bouton de départ
global. L'action sélectionne une séance publiée et liée à son template actuel.
D3. Pour catalogue et programme, création via un adaptateur propriétaire nouveau
qui revalide la sélection et son contenu courant, ownership, publication/archive,
auth/device courants sous guard_owner, puis admit_legacy_start(reject_any_open=True),
préparer_demarrage et matérialisation complète. Seule une transaction validée
crée la vraie séance ; creation_source='library', aucun épisode de recommandation
inventé. instantiate_session, exécution et journal restent les services possédés.
Le helper de programme est complété par la vérification explicite du statut
published courant ; ne pas considérer son lien seul comme admission fraîche.
D4. Deux créations concurrentes sont sérialisées par le verrou propriétaire et
la garde de séance ouverte. Aucun abandon automatique de l'autre séance. Une
séance SCI ouverte n'est jamais ouverte dans le contrôleur legacy. L'accord
exact V3 et les droits d'applicabilité restent entièrement à leur runtime.
D5. Réponse de création perdue : intention exacte durable avant POST dans une
table opérationnelle locale sur la connexion/queue du journal possédé, partition
compte/backend. Le snapshot active_session exclusif Legacy/V3 n'est pas utilisé
comme stockage transversal : saveSnapshot refuse V3 et claim/save remplacent son
JSON. Aucun envoi si préparation et relecture locales ne sont pas confirmées. Vérifier ensuite la vraie séance possédée. Un slug semblable ne prouve
pas que cette commande a réussi : offrir reprise de CETTE séance comme fait
serveur, jamais l'appeler reçu de la commande. Sans fait concluant, état UNKNOWN
et vérification/annulation explicite de l'intention locale ; aucun POST automatique.
Une nouvelle tentative humaine est une nouvelle intention fraîche, précédée de
la relecture propriétaire et des mêmes gardes, pas un rejeu idempotent promis.
La fermeture/abandon déjà en attente bloque le nouveau départ.
D6. Les entrées sont prévues : les séries précréées restent completed=false et
poids/reps observés NULL. Les prescriptions min/max de répétitions sont décrites
comme telles. Un poids historique saisi en kg n'est pas converti en masse totale ;
les réglages machine et PER_IMPLEMENT conservent leurs contrats. Les suggestions
existantes ne sont pas des faits effectués ou une qualification SCI actuelle.
D7. Hors ligne : lecture précédente en mémoire, datée et limitée au même
compte/backend/révision. Pas de nouveau cache canonique ni lancement hors réseau.
Une indisponibilité après erreur n'est ni un catalogue vide ni un refus SCI.
D8. Démarrabilité du domaine et support du lecteur natif sont distincts. Le
catalogue inclut du cardio pur (zéro exercice) que le session_builder sait créer,
mais le contrôleur natif courant suppose une série et un exercice actifs. Ces
compositions et celles sans série de travail sont visibles avec support natif
UNSUPPORTED / NATIVE_EXECUTION_UNSUPPORTED ; selection_ref=null et POST refusé
avant création. Pas d'élargissement de l'exécution ou de promesse de parité
universelle dans ce scope ; pas de restriction à une consultation seule pour les
formes strength effectivement supportées.
D9. Pas de programme actif ou semaine utilisateur persistés quand le domaine
n'en possède pas la sémantique. Programme possédé, plan SCI et proposition
hebdomadaire restent trois identités distinctes ; aucune transposition silencieuse.

## Wire and Reading Boundary
Adaptateur Bearer /me/library, contrat/écho owned-library/1.0.0, no-store, owner
serveur, version incompatible406 et aucun downgrade silencieux. Liste et détail
séparés, budget de lecture explicite ; pagination liée au propriétaire et à la
révision de source, refus409 si source mutable changée entre pages, pas de vue
COMPLETE recomposée avec deux révisions. Curseur étranger/inconnu404 indistinct.
Les limites effectives et schémas fermés sont fixés dans WIRE_AND_RECOVERY.md,
sans scanner/charger un arbre personnel non borné via les constructeurs de
lignes après list_drafts avant d'appliquer les limites.

L'index fournit type/clé de source/nom/état/comptes confirmés ou inconnus, sections
et action de détail ; il ne prescrit ni poids ni possibilité matérielle. Le détail
porte les références exactes template ou program/session/publication. Une capacité
de sélection est revalidée au POST ; pas d'autorité scientifique dans un pictogramme.
Le service de départ renvoie la vraie projection d'exécution legacy possédée,
ou la séance ouverte à reprendre, ou un refus typé. Un transport inconnu n'est
jamais converti en succès, refus définitif ou permission hors réseau.

## Native Composition / Platforms
Une route Programmes et un présentateur liste/détail commun, primitives existantes.
Une action dominante : ouvrir, démarrer une séance admissible, reprendre la séance
possédée ou vérifier une commande ; aides/provenance dépliables. Pas de nouvelle
palette, logo, tableau dense ou illustration. Cibles48dp Android et adaptations
texte/clavier/safe areas natives, retour Android conserve sélection et intention.
Représentation explicite loading/empty/previous/unknown/unavailable et A/B tardif.
G1 puis board familial réel avec les références approuvées ; aucune acceptation
Android déduite d'Expo Go sans module natif compatible. La preuve native complète
et la recette physique restent séparées.

## Shared Leases / Rollout
Pas de PR de sources en parallèle avec BODY/NUT sur ConnectedApp/mobile_api/journal.
Adapter ces sources seulement au canonique réel, sans recopier une ancienne
version de leur fichier. Un nouveau flag fermé bibliothèque/test sera proposé
au GO technique ; aucune activation réelle par le montage. Pas de SDK ou lock,
EAS/OTA, migration serveur, serveur externe ou secrets dans ce périmètre proposé.
Rollback : couper les départs bibliothèque, garder les séances/journaux existants
et lectures compatibles ; ne pas retirer les faits d'une séance créée.

## Technical Protocol Before Build
Le protocole fermé proposé est WIRE_AND_RECOVERY.md : endpoints, bornes, révision
mutable, sélection, refus et intention locale. Revue builder fraîche avant GO.
Les données disponibles ne permettent pas d'inventer un reçu idempotent serveur.
La validation du paquet et de G1 est reçue ; implémentation et vérifications contrôlées dans IMPLEMENTATION_LEDGER.md, pixels et intégration finale encore ouverts.

## Rulings techniques du builder
Table locale library_pending_openings_v1 sur la connexion existante, pas un
second journal ; hydratation/guard communs à Legacy et V3, sans sérialisation
parasite dans active_session. La reprise/annulation locale ne requalifie pas une
création UNKNOWN en succès ou échec. Formes cardio/zéro-work-set non supportées
restent lisibles, mais jamais dotées d'un bouton de départ trompeur.
Le programme s'ouvre en liste de séances, chacune avec sa propre sélection ;
aucune selection_ref globale de programme. Choix techniques proposés et bornés,
pas des réponses opérateur prétendument issues du test Maltin abandonné.
