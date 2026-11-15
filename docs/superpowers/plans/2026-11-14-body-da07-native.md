# BODY — reconstruction native du master DA07 accepté

Autorité : décision A de call_e22888c3c8c64715bb1544af27dc95fb,
archive 45fd765cdbe95c05b3598e8bc2bfd75136697558f30732d1fcd04c9100f1a697.
Les décisions B/C restent acquises pour les scopes suivants. Aucun pixel natif
n'est accepté par cette décision de master.

## Brainstorming / options / risques / choix retenu

Options : servir les SVG ; réécrire le contrôleur métier ; reconstruire le seul
présentateur avec les interfaces existantes. Choix : troisième option. Les SVG
restent une référence de proportions ; Frame C, W1 et NumericReadout restent les
composants réels. Le contrôleur d'authentification, CAS, accord, effacement et
commandes durables reste l'autorité. Aucun nouveau modèle ou API.

Risques : fausse chronologie intrajournalière, comparaison de legacy invalide,
copie silencieuse d'une valeur dans une acquisition, fuite numérique après
retrait, débordement grande fonte et clavier. Les témoins couvrent ces cas.

## Tâches et preuves

1. [x] Figer l'acceptation et sauvegarder le diff avant reconstruction.
2. [x] TDD du modèle de lecture : têtes courantes, jours connus, même date sans
   ordre inventé, comparaison explicitement sélectionnée et neutralité du signe.
3. [x] Présentateur compact : instrument, mémoire sélectionnable, mesures
   secondaires indépendantes, sources/versions et absence de données.
4. [x] Éditeur situé : unité, jour explicite, inconnus bilatéraux, correction
   exacte, clavier réel, conservation/abandon du brouillon.
5. [x] Raccorder le vrai consommateur BODY sans toucher aux parents NUT/MOB06.
   Conserver l'effacement minimal et relire toute lignée avant mutation.
6. [x] check_scope, ciblés/broad, TypeScript et Jest ; revue indépendante entière
   et correctifs RED→GREEN. Le tier réel détermine le sweep backend nécessaire.
7. [ ] ConnectedApp iOS normal/grande fonte et clavier, Android si supporté ;
   une décision de pixels BODY avant commit UI. Aucun résultat physique déduit.
8. [ ] Après décision : finaliser #407, CI HEAD exact, merge GOV-MERGE-01,
   canonique/closeout puis libération des leases pour #406 et #408.

## Rulings de portée

- L'arithmétique d'affichage est limitée au B−A du même champ/unité entre deux
  observations choisies explicitement, avec jours et période exacts ; pas de
  moyenne, score, recommandation ou interprétation biologique. C'est la règle du
  master accepté, pas une modification SCI. Coût si incorrect : lecture trompeuse.
- @expo/ui absent : conserver Modal/KeyboardAvoidingView et l'accessoire clavier
  existants évite une nouvelle dépendance native. Leurs comportements seront
  vérifiés sur le véritable écran. Coût : adaptation IME à vérifier séparément.
- Les commandes et gardes demeurent dans BodyMeasurementsSurface ; le nouveau
  modèle/presentateur est sans stockage ou transport. L'effacement minimal ne
  reçoit aucune BodyEntry numérique. Coût : conserver des tests de branchement.
- Aucun commit de géométrie, baseline ou release avant les gates applicables.

## Review focus

Vérifier particulièrement les observations de même jour, les champs invalides,
les pages partielles, les changements A/B et de consentement, les réponses
tardives, l'effacement minimal sans grant, et le clavier à grande fonte. Les
tests du présentateur ne remplacent ni la reprise SQLite réelle ni ConnectedApp.

## Relevé de gate natif

DA07_NATIVE_GATE.md consigne le résultat : 233 backend, 1204 mobiles et TS ;
quatre Important de revue corrigés RED→GREEN, ConnectedApp iOS réel et reprise
SQLite exacte. Android reste un Host natif borné. Board8252 : décision de
pixels BODY pendante ; aucun commit UI/CI nouvelle/merge avant ce gate.
