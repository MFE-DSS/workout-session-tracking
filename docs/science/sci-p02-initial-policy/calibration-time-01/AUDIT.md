# Calibration/time01 — audit canonique avant proposition

6 novembre 2026. Canonique `8e987c634a576cf729612db4adcfb313bf8ab350`, CI42255223159 completed/success vérifiée lors du closeout précédent. Worktree frais `/private/tmp/auren-sci-p02-calibration-time-01`, branche `sb/sci-p02-calibration-time-01`. Root sale et worktrees MOB03/initial-policy/MOB02 conservés ; aucune lecture de credentials ou de données utilisateur. Sources/pins dans SOURCE_PINS.json.

## Autorités conciliées

| Autorité réelle | Conséquence du design |
|---|---|
| `AUREN_MANIFESTO_V1.md` §§10–14/22–27/35 | Exécuté ≠ prescrit ; signal demandé une fois ; charges contextualisées ; moteur déterministe, pas de sophistication ou collecte sans usage |
| `Sx_AUREN_SCIENTIFIC_ENGINE_V2_SPEC.md` §4bis | RIR facultatif, aucune correction par moyenne de population ; pas de coefficient de transfert ; pas de charge initiale par sexe/âge/taille |
| SCI-P01/P02 v1, HANDOFF/CONTRACT | Blueprint suffisant n'est pas politique admise. Contrat request ne porte aucun historique structuré de calibration/chronométrage |
| Change `science-initial-plan-policy`, approval historique | Producteur pur/registries/tests autorisés pour le design alors revu. Ce delta de protocole/temps et de binding v2 n'a pas encore de GO ; mandat courant prévoit l'arrêt pour revue |
| Pull01 REPORT/CONTRACT_DECISION | G17 qualifié seulement ; AVAILABLE ne prouve pas l'exécution ; nouveau snapshot effectif requis avant binding. Aucun GO du prochain spike implicite |
| `AUREN_INSTRUMENTS.md` §5.5/§6.2bis, VNEXT§8.11, `AUREN_CALIBRATION_SYSTEM.md` | Aucun rail sans scale/zones du moteur E7. La calibration de première charge ne fournit aucune de ces zones. Interdiction d'estimation future dans les instruments servis préservée : modèle scientifique isolé, pas d'affichage ajouté |

## Ce qui fonctionne réellement aujourd'hui

| Source | Comportement et limite constatés |
|---|---|
| `tools/science_initial_policy/producer.py::produce` | Fonction pure réelle ; missing/conflicting avant POLICY_UNAVAILABLE ; pas de Plan/READY. Appelle inspect_policy puis validate_exchange v1 |
| `registry.py` / `v1/policy.json` | Version1.0.0/politique0.1.0 pinées ; approved_policy_refs vide. Modifier ces pins en place casserait le rejeu ; futur successeur séparé |
| `planning.py::inspect_policy` | Allocation proposée2/3, sept intentions, charge null/CALIBRATION_REQUIRED ; pas de calibration ni de temps positif. Ancienne sélection ne consomme pas les nouveaux overlays |
| `time_feasibility.py::assess_time` | Repos connu seulement, séquentiel ; peut réfuter cette configuration, jamais certifier qu'elle tient. L'égalité budget/repos réfute car le travail prend du temps positif |
| `app/services/overload_engine.py` | Cinq états unknown/progress/consolidate/top-range/deload ; historique vide → cible null. Incréments par catégorie2.5/1.0kg, seuils qualité.75/.55 et facteur.90 historiques, pas protocole admis de première charge |
| `overload_inputs.py` | Identité snapshots/substitutions et propriété filtrées ; première série complétée, max3 signaux, provenance CP-1 conservée. Pas de contexte matériel exact/assistance/RIR ni de seuil de récence scientifiquement admis |
| `SetLog` / `WorkoutSession` | Poids/reps/technique/qualité/completed_at/rest_dismissed_at et début/fin séance. completed peut être dérivé d'un poids OU reps : ne prouve pas une tentative réussie ou son effort. Pas d'horodatages début/fin de travail par série ni RIR numérique structuré dans SetLog |
| `time_format.session_duration` / `session_review` | Durée écoulée réelle avec début/fin ; pas prédiction de séance future. Différence entre completed_at successifs inclut repos, saisie et opérations, pas le temps de travail seul |
| `UserProgram.duration_target_minutes` | Budget déclaré ; ni durée observée ni borne prédite |

## Contrat à préserver

Prescription v1 : load_mode `CALIBRATION_REQUIRED / HISTORY_SUPPORTED / NOT_DEFINED`, charge null obligatoire en CALIBRATION_REQUIRED. Aucune des cinq étapes conceptuelles du mandat n'est un enum de cycle de vie partagé à remplacer.

Duration v1 : UNKNOWN avec bornes/model_ref null, ou ESTIMATED avec deux bornes/référence/bases. READY demande borne haute≤budget, faisabilité CONFIRMED, plan revu/complet et politiques réellement admises. Les quatre ordinaux du mandat seront un diagnostic isolé, pas de nouveaux enums mobiles ni un contournement de cette gate.

`decision_fingerprint` couvre FirstPlanRequest v1, pas un argument d'historique caché. Le successeur doit donc conserver cette empreinte et ajouter une enveloppe/digest complet distinct, décrit dans DESIGN.md. Aucun slot E1…E7 ni nom libre ne devient identifiant scientifique de l'exercice réel.

## Résultat de portée

À cette passe : proposition/design/tests spécifiés et recherche, aucun nouvel exécutable. Le GO MERGE permanent n'est pas un GO BUILD du protocole. Le prochain accord doit porter sur le delta lié ; activation/runtime restent hors de cet accord. Pas de commit/push/merge de build prétendu réalisé ici.
