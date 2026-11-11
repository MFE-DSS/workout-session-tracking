# MOB-05A — final visual refinement, 11 novembre 2026

Le mandat opérateur conserve le modèle fonctionnel et autorise une retouche
locale du détail historique. Même change et même GO BUILD. Une seule nouvelle
acceptation du board final est requise avant commit de cette retouche.

## Croquis validé

Source : demande précise de l'opérateur, citée selon G1 du protocole :
« compact header and session identity », « primary per-set numeric readout »,
« one short visible context status », « progressively disclosed provenance and limitations ».

```text
Retour                 AUREN       Historique       [cibles48]
Séance conservée · nom court                         [17/23]
Date · Terminée / Abandonnée · lecture précédente si nécessaire
┌ Frame C : mouvement réellement capturé ────────────┐
│ Matériel non capturé / contexte enregistré         │
│ ┌ RecessedWindow : série1 · complétée ────────────┐ │
│ │ 17,5 kg saisis             9 rép.               │ │
│ └───────────────────────────────────────────────┘ │
│ Historique du mouvement                           │
│ Sources et limites                               │
│   (date ISO exacte, source, prescription inconnue) │
└───────────────────────────────────────────────────┘
```

## Brainstorming / Options / Risques / Choix retenu

Choix local : en-tête compact et instruments de faits dans la seule famille
history. Les titres/espaces globaux AccountFrame restent inchangés. Modifier sa
primitive globale toucherait des surfaces verrouillées ; recréer un système de
cartes serait superflu. Frame C, RecessedWindow, NumericReadout et liens48 existants
portent les mêmes faits, sans quantité prescrite ou état inféré. Les cadres
mesurent leur contenu et grandissent avec les fontes ; aucune hauteur de corps
tronquante, aucune borne de charge ou incrément.

## Inventaire — une information, une seule fois

| Élément | Information | Source (contrat de données) | Doublon ? |
|---|---|---|---|
| Identité/date/statut | séance possédée et statut historique | LegacySessionFacts.session / HistoricalScienceExecution | non |
| Contexte court | absence de matériel capturé ou contexte SCI connu | equipment_context / observation.context | non |
| Valeur et unité typée | masse réellement saisie/observée | SetLog.weight_kg / observation.setting et load_semantics | non |
| Répétitions et complétion | faits distincts par série | reps, completed ; jamais dose prescrite | non |
| Sources repliées | dates ISO, source, substitution/limites | completed_at / observation.performed_at et estimated / noms capturés | non |
| Prescription repliée SCI | cibles historiques capturées | prescription.dose, distincte des observations | non |
| Lien mouvement | référence propriétaire exacte | exercise_links / se_id | non |

## Comparaison avec la référence validée

Avant : android-session.png et ios-connected-session.png du board accepté.
Conserver les fichiers et leurs hashes ; produire de nouveaux noms final-*.
Références AUREN UX-CAL-02/MOB04 et primitives verrouillées conservées.

## Changement unique de l'itération

La seule famille retouchée est le détail historique : titre, hiérarchie numérique,
contexte court et divulgation progressive. Les demandes liées ci-dessus sont
montrées avant/après dans le même board. Overview, fréquence, exercice et poids
réutilisent leurs consommateurs existants ; compléter loading/unknown avec fautes
contrôlées de transport, sans DTO de succès inventé.

## Plan d'exécution limité

- [x] Tests RED de détail compact, provenance repliée mais accessible, faits/unités/UNKNOWN et48dp.
- [x] Composition locale history ; aucune modification de primitive globale, source SCI ou API.
- [x] Tests consommateurs/unités et captures iOS/Android normal/grande fonte ; compléter le board existant.
- [x] Une acceptation finale opérateur avant commit UI ; revue indépendante de ce delta et correction RED→GREEN.
- [ ] CI du HEAD final, merge gardé et CI canonique.
- [ ] Merge gardé, CI canonique et archive/closeout ; préparer BODY/NUT sans les appliquer.

## Revue et correction de ce delta

Revue indépendante bornée au nouveau détail :0Critical/1Important/0Minor. Une
observation SCI enregistrée mais incomplète ne doit pas devenir « Aucun fait
enregistré ». Témoin1RED puis conservation explicite de la présence de
l'observation, sans API/SCI modifiés. Suite finale88suites/1122tests mobiles et
TypeScript PASS ; aucun second avis indépendant du correctif prétendu. Les
limites physiques/vocales et les deux mineurs de branche restent conservés.

Mesures de composition : titre local30→17sp ; marge haute de titre28→0dp ;
espacement de groupe24→12dp ; cibles de Retour44→48dp et disclosures48dp. Les
valeurs sont des NumericReadout40sp avec unité typée, le statut et le contexte
court restent visibles. La hauteur des cadres suit le contenu, sans prétendre
que toute fonte/accessibilité ou tout libellé a été physiquement certifié.

Décision opérateur du11novembre : **« Valider le delta final MOB-05A »**,
question call_3bf814ef514c414996496828a7220ce8, reçue avant commit du delta.
