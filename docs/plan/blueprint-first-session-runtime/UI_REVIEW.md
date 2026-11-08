# PLAN V3 — revue visuelle du scope contrôlé

8 novembre 2026. G1 et **pixels acceptés** : réponse opérateur «Valider ces pixels PLAN contrôlés» le8novembre2026, avant commit UI.
Board réel : http://127.0.0.1:8099/ ; huit captures brutes et empreintes dans
`clients/mobile/visual-contract/review-receipts/plan-v3-controlled/receipt.json`.
Le reçu porte cette décision et les SHA256 des huit captures effectivement soumises.

## Croquis validé

Source : [REVIEW_BOARD](../../../openspec/changes/blueprint-first-session-runtime/REVIEW_BOARD.md),
réponse opérateur exacte «Valider ce croquis G1» et GO «Autoriser le build PLAN contrôlé».

```text
Compte créé → collecte progressive / rencontre pilote sans sept prérequis
            → observation réelle → proposition si sept réglages qualifiés
            → accord temporel explicite → CREATED → exécution existante
            → journal factuel / correction / reprise / sortie incomplète
```

Aucune nouvelle carte MISSION. AccountFrame, champs, boutons, rail, ValueDial,
RestRing et chips existants réutilisés. Une action principale par état ; aide,
relecture, préférences et sortie sont secondaires. La lecture factuelle après
pause n'est pas une permission de nouvelle série.

## Inventaire — une information, une seule fois

| Élément | Information | Source (contrat de données) | Doublon ? |
|---|---|---|---|
| Champs manquants | Familles utiles à compléter | assessment canonique V3 / source.facts | non |
| Phase de rencontre | Préparation/familiarisation/essai/observation/décision | calibration.result.phase et allowed_actions courantes | non |
| Découverte sans charge | Intention sans essai observé | INITIATE_FAMILIARIZATION, événement CALIBRATION_ACTION_REQUESTED | non |
| Champ réglage vide | Valeur choisie par personne, non calculée | setting_choice, contexte et load_semantics | non |
| Observations passées | Faits conservés indépendamment de permission | observation_progress / épisodes possédés | non |
| Première séance proposée | Dose, identité et contexte réellement évalués | recommendation.candidate_plan.sessions[0].slots | non |
| Minutes disponibles | Budget déclaré, pas estimation | session.duration.budget_minutes | non |
| Incertitude temporelle | Durée non établie et préparation/opérations inconnues | time_readiness, start_policy et start_permission | non |
| Action d'accord | Reconnaissance explicite exacte | ack lié sujet/snapshot/révision/empreintes/policy, date serveur | non |
| Consigne et cible | Réglage observé provisoire/reps/repos du binding | execution.exercises / prescribed_setting / dose | non |
| Installation suivante | Transition sans durée ni repos inventé | SETUP_NEXT_EXERCISE | non |
| Repos dans le slot | Décompte prescrit réel | REST_THEN_SET / rest_seconds | non |
| Journal de série | Réglage, contexte, reps, date et état factuels | SetLog + typed_observation et opération locale immutable | non |
| Refus conservé | Ancien fait refusé distinct de version courante | FAILED/RESOLVED avec preuve USE_SERVER_VERSION | non |
| Correction | Nouvelle opération explicite CAS | expected_server_revision/op_id/digest | non |
| Date estimée | Horodatage non connu précisément | performed_at_estimated, date ajustée serveur si différente | non |

La cible et le fait sont des rôles distincts dans les instruments existants.
MACHINE_DISPLAY_KG, PER_IMPLEMENT et TOTAL_EXTERNAL gardent leur sens ; aucun
réglage non massique n'est rendu comme kilogrammes totaux. Les identités de
contexte synthétiques visibles appartiennent aux entrées du test, pas à une
information d'implémentation ajoutée au produit.

## Comparaison avec la référence validée

| Référence validée | Tranche / date | Ce qui doit survivre | Survit ? |
|---|---|---|---|
| mob03-first-use-v1/firstuse-none et missing | MOB03 accepté | Cadre, mark, typographie, retour et sorties | oui |
| mob03-first-use-v1/firstuse-consent | MOB03 accepté | Consentement/action explicite dans le cadre natif | oui |
| execution-set-390x844-push-a-e0 | Contrat vNext LOCKED | Instrument de série, rail, ValueDial, hiérarchie | oui |
| execution-rest-next-390x844-push-a-e0 | Contrat vNext LOCKED | RestRing et prochaine action | oui |
| mob03-account-v1/created | MOB03 accepté | Primitives AccountFrame pour le nouveau journal | oui |

Board côte à côte : références390px et rendu natif393×852 points affichés à390px.
Les scénarios SCI sont nouveaux : les références démontrent les primitives et
la composition, pas une fausse équivalence de charge, état ou données. Les
captures exécution/setup/repos contiennent la pastille flottante Expo Go de
l'environnement de test ; elle ne fait pas partie du produit. Les autres
captures sont sans cette pastille. Capture proposition : haut visible identique
au code final ; le rendu final ne montre que la première séance (D9), sans
modifier l'allocation scientifique à deux séances ou ses empreintes.

Les captures sont de vrais états du consommateur natif avec serveur jetable.
L'erreur ultérieure de capture/fenêtre CUA empêche des recaptures de confort ;
les PNG simctl originaux restent lisibles et ne sont pas retouchés. Aucun
résultat de largeur320/430, Android ou appareil physique n'est déduit.

## Changement unique de l'itération

- Demande : «Valider ce croquis G1».
- Changement : réaliser la chaîne contrôlée proposée dans ce croquis, avec les
  informations/permissions réellement disponibles et le journal canonique.
- Avant : références du board ; après : huit captures natives du même board.
- Corrections de revue intégrées à cette réalisation : fraîcheur des permissions,
  réglages typés, historique/correction explicites et familiarisation sans charge.
  Aucun redesign MISSION ou baseline.

## Relecture des décisions, décision par décision

Sources relues : DESIGN_DECISIONS_UIV2_SURFACES et HOME_UIV2, amendements natifs
et contrat visuel vNext. Q1 respectée (compte), Q2 respectée (MISSION conservée),
Q3 non concernée (wellness), Q4 respectée (instruments sémantiques), Q5–Q8
respectées selon amendement natif (tokens/primitives, action principale unique).
D1 respectée (rôles/contrôles existants), D2 respectée (aucune nouvelle promesse
AI), D3–D5 respectées selon référence native, D6–D8 non concernées (pas nouvelle
progression/calendrier/streak). D9 respectée : seule première séance exposée ;
régression dédiée vérifie sept boutons de slots, pas anticipation de la seconde.
BodyMap inconnu omis selon règle existante, aucune correspondance15→11 inventée.
Aucun asset, token de couleur ou baseline LOCKED ajouté/remplacé.
