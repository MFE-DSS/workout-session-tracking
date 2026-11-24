# mobile/owned-program-library Specification

## Purpose
Définir la bibliothèque native propriétaire, ses compositions prévues et son départ contrôlé, avec reprise factuelle Legacy/V3 et incertitude conservée après réponse perdue.

## Requirements

### Requirement: Bibliothèque propriétaire de compositions prévues
La bibliothèque SHALL servir catalogue commun et programmes possédés sous leurs
identités de source, sans classer opaque, inventer un programme actif ni convertir
les prescriptions prévues en séries effectuées. Les détails SHALL conserver
brouillon/publication/archive, champs manquants et provenance.

#### Scenario: Programme étranger
- **WHEN** un compte demande un identifiant de programme étranger ou inconnu
- **THEN** le refus404 est identique et aucune composition privée n'est divulguée.

#### Scenario: Données d'équipement absentes
- **WHEN** la source ne documente pas la réalisation matérielle ou l'unité précise
- **THEN** cette information reste inconnue sans équivalence machine/PER_IMPLEMENT/masse totale inventée.

### Requirement: Départ frais et transaction possédée
Un nouveau départ SHALL revalider la sélection actuelle, propriétaire/publication,
préflight matériel et admission existante sous garde d'authentification courante.
La création SHALL utiliser les services canoniques et produire des séries non
complétées sans poids/répétitions observés fabriqués.

#### Scenario: Une séance est ouverte
- **WHEN** une autre séance possédée existe au moment du départ
- **THEN** aucun second départ ou abandon automatique ne survient et la reprise utilise son profil réel.

#### Scenario: Préflight devenu défavorable
- **WHEN** une lecture semblait démarrable mais le contexte actuel refuse le départ
- **THEN** aucun fait de séance n'est créé ni permission SCI obtenue par la lecture précédente.

### Requirement: Réception inconnue et isolation native
Le consommateur SHALL conserver une intention exacte dans le journal possédé avant
POST et bloquer l'envoi si cette sauvegarde échoue. Une réponse perdue MUST NOT
être rejouée automatiquement ou prouvée par un simple slug semblable. Les réponses
et intentions SHALL rester liées au compte/backend/révision applicables.

#### Scenario: Réponse perdue puis relance
- **WHEN** la réponse de création est inconnue lors d'une reprise
- **THEN** le client vérifie les faits propriétaires, conserve l'incertitude restante et n'invente pas un reçu idempotent absent du domaine.

#### Scenario: Changement de compte
- **WHEN** un résultat du compte A arrive après passage au compte B
- **THEN** il ne remplace aucune lecture, séance ou intention de B.

### Requirement: Vérité des lectures et gates visuelles
Les lectures SHALL distinguer loading/empty/previous/unknown ; les parcours de
pages MUST NOT certifier COMPLETE après changement de révision de source.
Toute nouvelle composition SHALL obtenir G1 et vrais pixels acceptés avant commit
UI, sans rebaseline des primitives LOCKED.

#### Scenario: Hors ligne
- **WHEN** une lecture précédente est disponible mais le serveur ne répond plus
- **THEN** elle reste datée et explicitement précédente, sans nouvelle permission de départ.

### Requirement: Composition structurelle sourcée du programme
Le consommateur natif SHALL distinguer les comptes agrégés de l’index et la distribution réellement reçue au détail, conserver l’ordre des séances et des positions d’exercices, et représenter les prescriptions typées sans inventer un programme actif ou un calendrier.

#### Scenario: Composition partielle ou bornée
- **WHEN** des comptes, exercices ou rep_targets sont absents, partiels ou dépassent la borne graphique
- **THEN** la qualification et le reliquat exact restent visibles ou consultables
- **AND** aucune quantité manquante ne devient zéro ou distribution fabriquée

### Requirement: Module sélectionnable et commande propriétaire située
Le consommateur SHALL garder les actions attachées à la source et à la sélection actuelles, préserver PUBLISHED versus VALIDATED et les gardes natives Legacy/V3 existantes, et distinguer une création inconnue d’une occurrence propriétaire retrouvée.

#### Scenario: Sélection et départ incertain
- **WHEN** une séance est sélectionnée ou une réponse de création est perdue
- **THEN** la sélection seule ne crée rien et aucun POST n’est rejoué automatiquement
- **AND** la vérification et l’adoption explicite conservent leurs callbacks et identités existants

### Requirement: Prescriptions visibles et accessibles concordantes
Le consommateur SHALL produire le dessin et le libellé accessible de la séance à partir des mêmes groupes ordonnés, avec exercices, répétitions, préparations et reliquats reçus, et conserver les commandes atteignables par reflow/défilement.

#### Scenario: Ordre et nombreuses prescriptions
- **WHEN** les tableaux reçus ne suivent pas leurs positions ou dépassent les bornes de rendu
- **THEN** chaque mouvement affiché est annoncé une fois dans le même ordre, avec les unités et reliquats correspondants
- **AND** les valeurs et l’action réelle restent consultables sans réduction du texte critique
