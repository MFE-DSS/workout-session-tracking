# Fiche native Smith — UNE composition PROPOSED

**G1_PENDING · PIXELS_NOT_RECEIVED · NO_GO_BUILD.** Croquis documentaire du9novembre2026, aucune UI/image produite. Le pilote concerne P:`push-a:E1` / `Incline Smith Press`, pas une réalisation de calibrage SCI. La route, le composant et la liaison exacte restent à spécifier dans un futur GO BUILD.

## Choix proposé

Fiche secondaire plein écran à défilement, ouverte volontairement depuis un futur accès au détail de l'exercice. Un seul slot carré conserve le cadrage de la paire ; une bascule accessible Début/Fin change seulement l'état illustré, initialement Début. Les deux états doivent être livrés et compatibles avant de présenter le premier. Pas d'animation de répétition, autoplay, nouvelle navigation principale ou action de calibration.

```text
┌─────────────────────────────────────┐
│ ‹ Retour                            │
│ Incline Smith Press                 │
│ [équipement exact si établi]         │
│                                     │
│  [Début sélectionné]   [Fin]          │
│ ┌──────── Frame C / fenêtre ───────┐ │
│ │                                 │ │
│ │  SLOT ILLUSTRATION SMITH         │ │
│ │  corps + machine + banc         │ │
│ │  même cadrage pour les 2 états   │ │
│ │  aucun asset reçu ici           │ │
│ └─────────────────────────────────┘ │
│                                     │
│ [Localisation fonctionnelle]        │
│ [BodyMap + label si zone fournie]    │
│                                     │
│ Instructions                        │
│ [texte de la source applicable OU   │
│  Instructions applicables non       │
│  disponibles]                       │
│ [source/licence applicable, si reçu] │
└─────────────────────────────────────┘
```

Les mentions entre crochets décrivent des slots de SPEC, pas du texte produit approuvé. L'état actuel de ce croquis utilise **« Illustration indisponible »** à la place du slot : le master et la paire n'existent pas. Aucun rendu n'est simulé avec les cinq références raster.

## Une information, une seule fois — inventaire de vraies sources

| Élément proposé | Source réellement disponible / champ | Observation et manque exact |
|---|---|---|
| Retour | Convention native future ; `IconButton`/navigation existants à réutiliser | Action locale, aucune donnée métier ; route/destination et préservation du contexte appelant pas encore implémentées. |
| Nom exact | Historique `data/reference_split.json` template`push-a` E1 `name` ; en séance V1 `PlanExercise.executed_name` ; en V3 `canonical_exercise_id` et capability `supported_realizations[].display_name` | Ne jamais afficher le nom Smith sous une substitution différente. V1 ne porte pas l'identité de réalisation suffisante pour lier un média ; le build devra obtenir une liaison explicite, pas parser le libellé. Aucun fallback de nom Smith sur réalisation inconnue. |
| Équipement | Historique E1 `machine_slug=incline-smith-press` ; V3 `prescription.context.equipment_ref` | Le slug catalogue n'est pas le modèle ; contexte Smith applicable absent de cette préparation. Si non établi, ne pas afficher de précision fabriquée. Le nom contient déjà Smith : aucun second badge « Smith » redondant. |
| Sélecteur Début/Fin | État local du futur présentateur ; métadonnées proposées de paire assetID/version/état | Aucun DTO de média existant ; labels locaux d'état, pas consignes de mouvement. Un seul état sélectionné, annoncé via rôle/état accessible ; pas de légende répétant la même information en dessous. |
| Illustration du geste | Futurs mannequin vectoriel + matériel + paire Smith ; référence `auren.mannequin.canonical.v1` v1.0.0 | Master, articulation, matériel, fichiers START/END, droits des dérivés et réception absents. Afficher fallback F0, jamais BodyMap comme substitut gestuel. |
| Localisation fonctionnelle, si fournie | V1 `PlanExercise.zone` / `secondary_zones`, issus du read model canonique ; `presetForZone` et `BodyMapView` | Une seule zone reçue et son label dans ce pilote. Aucun mapping depuis le nom, la pose ou les rôles SCI. V3 ne fournit pas automatiquement cette présentation BodyMap ; absence→pas de fenêtre ni label inventés. |
| Texte d'instructions | Catalogue historique E1 `notes` contient « Banc incliné30°… » ; SCI/PLAN acquièrent `instruction_ref` et `setup_ref` dans leur protocole propre | La note catalogue n'est pas une notice du modèle réel ; `PlanExercise` V1 ne porte même pas `notes`. Les sources d'instructions réellement applicables au Smith et leur DTO de lecture sont absents. Ne pas écrire des consignes depuis l'image ou réutiliser le protocole chest press. Le slot dit l'absence tant que ce contrat manque. |
| Sources et crédits | Provenance/manifeste de l'asset final futurs ; BodyMap natif `BODYMAP_ATTRIBUTION`/`LicencesSection` déjà présents | Crédit MIT central existant ; ne pas le répéter sous chaque fenêtre. Sources/droits finaux du mannequin/articulation/matériel à recevoir ; pas d'étiquette « libre de droits » inventée. |
| Charge, reps, séries, prescription, réglage observé, statut réseau | `ExecutionScreen` V1 et `PlanV3ExecutionScreen`/journal V3 existants | Ces données n'entrent pas dans cette fiche proposée : leur unique porteur reste l'écran/journal appelant. L'aide illustrée ne permet pas de valider une série ou qualifier un réglage. |

`instruction_ref` et `setup_ref` sont ici des références de protocole et non des preuves que leur contenu externe a été vérifié ; le nom exact des champs du futur DTO Smith reste à spécifier. Aucun contrat média/instructions n'est prétendu disponible.

## Vraies surfaces natives observées

- `clients/mobile/src/ui/ExecutionScreen.tsx` : écran réel V1 plein écran, zone canonique via fenêtre instrument, nom exécuté, séries/cadrans/repos/substitution. `EXECUTION-SCREEN-V1` LOCKED, six baselines acceptées le31octobre ; aucun mannequin ni START/END.
- `clients/mobile/src/ui/SessionSetDetails.tsx` : feuille du journal de séries et états de livraison serveur, **pas** fiche technique d'exercice.
- `clients/mobile/src/ui/plan/PlanV3ExecutionScreen.tsx` : vrai présentateur V3, identité des réalisations supportées, dose et charge typée ; aucun consommateur de média d'exercice. Le contexte conserve réalisation/équipement/côté/unité sans devenir un asset.
- `clients/mobile/src/ui/plan/PlanV3FirstUseScreen.tsx` et `clients/mobile/src/api/calibrationV1.ts` : vraies acquisitions/lectures de calibrage ; leur disponibilité d'instructions et leurs permissions SCI ne sont pas remplacées par cette fiche.
- `clients/mobile/src/routes/programmes.tsx` : `PendingSpace` avec lien `/library` ; aucune bibliothèque native d'exercices autonome reçue.
- `clients/mobile/src/ui/bodymap/{BodyMapView,BodyMapTriptych,viewPresets,bodyGeometry,attribution}.tsx/ts` : géométrie native MIT3.2.0 vendorisée, caméras déterministes, a11y et attribution ; pas le master BodyParts3D/Servier servi comme runtime natif.

Les lab fixtures et captures du visual contract servent de preuves de rendu de leurs surfaces, jamais de données runtime de la nouvelle fiche. Une acceptation de PLAN-CAL ne vaut pas G1 ou pixels de cette fiche.

## Primitives LOCKED réutilisées et garde d'itération

| Décision applicable | Statut de cette proposition |
|---|---|
| Tokens `theme.ts`, `system` pour localisation, `signal` pour geste opérateur | Préservés ; aucun hex ni token créé. Contraste sur fond réel à mesurer au futur rendu, pas de ratio inventé ici. |
| Frame C / Recessed Window | Réemploi proposé comme cadre ; intérieur média nouveau à soumettre. Pas de redessin de géométrie LOCKED. |
| BodyMap §20–22 | Présentation fonctionnelle existante conservée si zone reçue ; chemins MIT intouchés ; aucune anatomie supplémentaire. |
| Exécution §24, MISSION §25, bilan §26 | Pas de modification proposée de leur composition ni baseline. La future entrée vers la fiche fera partie d'un scope UI explicite. |
| Croquis avant code (§5.6) | Ce croquis est PROPOSED, validation opérateur non reçue. |
| Une information une fois (§5.7) | Inventaire ci-dessus ; labels d'état uniques, pas de valeurs de travail dupliquées. |
| Comparaison référence (§5.8) | Aucune référence acceptée de cette nouvelle fiche. Au futur rendu : montrer le croquis alors accepté et les surfaces adjacentes LOCKED applicables ; aucun faux avant/après. |
| Un changement par itération (§5.9) | Une composition proposée, aucune variante produite ; demandes supplémentaires hors de cette itération. |

## Cadrage, petite taille et accessibilité — critères proposés

Le slot cible320×320pt sur cadre390pt avec marges natives ; carré entier, sans crop indépendant de START/END, fond de l'écran et aucune lumière cuite. La caméra Smith doit cadrer le corps et le matériel sur **les deux états**, sans appliquer mécaniquement le91,8% de la référence debout. ViewBox exact et taille du SVG/budget restent à mesurer ; export3× éventuel960×960px est une cible proposée, pas une résolution de fichier reçu.

À320pt et texte130%, la fiche défile et garde fermeture/retour atteignables ; le sélecteur ne masque pas la figure. Cibles tactiles≥44pt, ordre nom→sélecteur→figure→localisation→instructions ; état sélectionné annoncé sans couleur seule ; interne SVG non focalisable, une seule annonce concise par état. Retour Android dépile la fiche, fermeture iOS revient au même appelant sans modifier séance/rencontre ; le comportement exact exige vrai prototype et recette après GO. VoiceOver/TalkBack, marges système et exposition des pixels restent **NOT YET REVIEWED**.

Si fichier absent/corrompu, état unique manquant, contexte incompatible ou format non rendu : une seule absence explicite F0, aucun appel extérieur pour générer/remplacer, aucune permission de geste fabriquée. Le texte applicable demeure lisible indépendamment du média. Hors ligne, aucune garantie de cache n'est inventée : sa stratégie fait partie du futur build borné.
