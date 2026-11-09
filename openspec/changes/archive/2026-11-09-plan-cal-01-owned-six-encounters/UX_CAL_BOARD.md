# UX-CAL / PLAN-CAL-01 — croquis et sources proposés

9novembre2026. **G1 ACCEPTÉ : « Valider ce croquis UX-CAL G1 » / PIXELS CONTRÔLÉS ACCEPTÉS : « Valider ces pixels contrôlés ».**
Le GO de build et la décision G1 sont distincts ; les vrais pixels seront soumis
avant commit UI ; acceptation reçue sur le board natif réel décrit dans le receipt. Ce document reste le croquis historique, pas une app,
une capture native ou une preuve appareil.

## Croquis proposé

Références PLAN contrôlé du8novembre relues : first-use.png et discovery.png
vues, huit rendus/receipt PIXELS_ACCEPTED conservés. Cadre AccountFrame existant,
mark/retour/titre/typographie/champs/bouton primaire/links/espacement réutilisés.
Une action principale utile par état, contenu défilant et sortie accessibles.
Aucun nouveau rail, dessin anatomique, score, logo, token ou baseline.

```text
A — entrée conservée             B — choix, après le bouton
Retour     [mark] AUREN          Retour     [mark] AUREN
Ton premier entraînement        Choisir un mouvement
[texte actuel, factuel]          Une rencontre à la fois.
[Découvrir un mouvement]         Extension de jambes     [source actuelle]
Réglages déjà observés          Chest press             [source actuelle]
Disponibilités                  Rowing avec appui       [source actuelle]
...                             RDL avec haltères       [source actuelle]
                                Tirage neutre           [source actuelle]
                                Élévations latérales    [source actuelle]
                                Mollets debout          [source actuelle]
                                [Préparer le mouvement choisi]
                                Relire / Préférences / Aujourd’hui

C — contexte et préparation      D — réglage puis familiarisation
Retour     [mark] AUREN          Retour     [mark] AUREN
Ton contexte                    Se familiariser
[Nom réel, une fois]             [Nom réel, une fois]
Lieu / dispositif réels          [Observer l’installation sans essai chargé]
Disponibilité : inconnue         Réglage choisi [              ]
  Disponible / Indisponible      kg affichés OU kg par haltère (source)
Préoccupation : inconnue         [Confirmer ce réglage disponible]
  Aucune rapportée / Signaler    [Confirmer contexte et réglage]
[Confirmer ces faits]            [Confirmer familiarisation à CE réglage]
Notice réellement disponible    ... si permission SCI courante :
Installation applicable         [Choisir de faire un essai]
[Je comprends / contrôle]        Pause / Noter un fait passé / Préoccupation
Lire aide propre au mouvement
Aide / Pause / Aujourd’hui

E — observation                  F — décision et retour
Noter ce qui s’est passé         Examiner l’essai
[réglage observé typé]           [fait exact une fois]
Répétitions réellement faites    Réglage provisoire seulement si SCI le dit
Complétion / succès              [Accepter ce réglage exact] si permis
Contrôle / gêne                  [Demander un réessai] si applicable
Motif réellement rapporté       [Revenir à ma préparation]
  Terminé / arrêt volontaire    Nouvelle sélection explicite si autre contexte
  temps / préoccupation         Ancien historique lisible, pas permission
  échec / inconnu               Pause distincte du retrait explicite
[Enregistrer ce fait]            ... sept preuves applicables :
Ne donne pas permission de       proposition→ack exact→même séance native
recommencer                     (compositions déjà acceptées conservées)
```

Les `[source actuelle]` du croquis sont emplacements de statut en lecture seule,
pas un texte technique à afficher. Libellés possibles : «À préparer», «Observation
conservée», «Réglage provisoire», «À vérifier», «Guidage indisponible». Un seul
statut sourcé par ligne ; pas jauge7/7 ou grade de réussite depuis un nombre
local d'événements. Lire l'aide/choisir un mouvement ne nécessite pas sept réglages.
Les faits minimums déjà confirmés sont relus, pas redemandés à chaque exercice.

RDL : aide de préparation sans haltères distincte ; unité kg par haltère, aucune
maîtrise chargée inférée. Les cinq autres : kg affichés. Pas valeur préremplie,
0issu du champ vide, bouton+/-à incrément générique ou affichage d'une masse totale.
Les mots et étapes spécifiques ne sont pas copiés d'une notice d'un autre appareil.

Réessai reste une demande humaine, jamais événement d'essai fabriqué. UNKNOWN
de qualité/gêne/motif reste sélection explicite possible et ferme guidage selon
SCI. Le motif n'est pas calculé depuis complétion/succès/gêne. Retrait : écran de
confirmation explique sa portée sur cette préparation, conservation des faits et
absence de règle de reprise admise. Pause/retour simple n'émet pas de retrait.

## Inventaire — une information, une seule fois

| Élément | Information et source | Porteur unique |
|---|---|---|
| Nom de mouvement | catalogue canonique attested inventory profiles display_name | ligne puis titre du mouvement dans le détail ; pas nom libre |
| Éligibilité du profil | capability inventory version, exact candidate/realization/semantics | commande montrée seulement sous profil supporté |
| Statut courant de préparation | sélection propriétaire et vraie évaluation de rencontre, même source_revision | un libellé par ligne, pas compteur décoratif |
| Historique | observation_progress factuel, même après withdrawal/absence d'autorité | module des faits, distinct des actions courantes |
| Contexte/device/availability | déclarations et ledger, UNKNOWN conservé | champs puis résumé source, jamais full gym |
| Aide/setup par réalisation | OPERATIONAL_PROTOCOL publié, sections commune + candidat + arrêt ; référence de notice réelle donnée par utilisateur | texte propre au mouvement, refs/hashes techniques non exposés |
| Réglage | actual SettingChoice + ContextKey.load_semantics | champ vide puis fait typé, pas valeur calculée |
| Familiarisation | événement explicite Setting exact + phase/actions SCI courantes | confirmation distincte du bouton d'intention |
| Essai/qualité/gêne/motif | CALIBRATION_EVENT_REPORTED et stop_reason réellement saisis | formulaire factuel unique, pas diagnostic |
| Qualification/acceptation | canonical result + exact trial/acceptance refs ; action humaine | statut provisoire/actions permises, pas succès de navigation |
| Plan/temps/ack | vrais V3, budget déclaré et time UNKNOWN, fingerprints et politique exacts | composants existants de proposition/ack |
| Demande/start/reprise | reçus/handoff possédés, CREATED/session_id | surfaces existantes, aucune séance avant preuve CREATED |

## Comparaison avec la référence validée

- First-use/discovery : clients/mobile/visual-contract/review-receipts/plan-v3-controlled/{first-use,discovery}.png, acceptés8novembre,393×852points.
- Proposition/ack/exécution/setup/rest/journal : six autres captures et receipt du même dossier ; préserver composition, limites et types.
- Cadre MOB03 et six baselines exécution/MISSION : inchangés ; aucun re-générateur de baseline automatique.

Après GO, produire des captures NATIVES non retouchées des nouveaux choix/contexte/
familiarisation/observation/reprise : cinq profils machine et RDL typé, état
inconnu/concern/retrait/reprise après relance. Board côte à côte, dimensions et
source des données synthétiques identifiées. Ajouter preuves que chaîne guidée
sert vrai serveur jetable, pas un storyboard/fixture de READY. Simulator ≠ recette
Android/iPhone physiques. Tester clavier/retour/grand texte et préciser ce qui
n'a pu être exercé. L'acceptation pixels8novembre n'est pas étendue par défaut.

## Changement unique de l'itération

Demande : «connect the six new SCI encounters to the existing owned PLAN runtime».
Delta proposé : sélectionner et acquérir chaque rencontre sous son vrai profil,
dans les cadres acceptés, avec familiarisation Setting exact et motif explicite.
Avant : pilote seul ; après : pilote+six sous leurs gates, aucun redesign de
l'onboarding global, MISSION ou exécution. Les compositions restent G1 proposées.

## Réemploi et limites

SDK Expo58.0.17 observé, dépendances/primitives existantes ; skills Expo consultés.
Aucun nouveau composant @expo/ui/package installé pour cette préparation : on
conserve le système déjà accepté. Si une nouvelle primitive non couverte devenait
nécessaire, la documenter séparément, pas la faire entrer par un remplacement global.
Pas d'assets finaux ou de nouvelle anatomie/mesure exposés pour résoudre un manque
backend. Les valeurs synthétiques des futures captures ne sont jamais des réglages
utilisateur ou des paramètres de prescription.
