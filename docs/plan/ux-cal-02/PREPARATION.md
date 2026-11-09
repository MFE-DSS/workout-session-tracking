# UX-CAL-02 — reçu de préparation scope et croquis

9 novembre 2026 — Europe/Paris. **PROPOSED / NO_GO_BUILD / G1_PENDING.**
Canonique après fetch : fe9f6e9beb585a271ae2c2726e338359057b9f58.
Worktree /private/tmp/auren-ux-cal-02, branche spec/ux-cal-02. Checkout opérateur
61ca08c et empreinte des treize entrées préexistantes préservés. Sources388/389
et documents historiques intacts ; aucune nouvelle livraison distante.

## Brainstorming / Options / Risques / Choix retenu

Le mandat fixe une seule interaction native partagée et l'équivalence des sept
contextes. Réduire les primitives globales toucherait le compte et d'autres
surfaces ; seulement réduire les fontes garderait toutes les explications et
actions concurrentes. Proposition retenue : composition locale plus compacte,
détails progressifs et deux corrections comportementales bornées. Risques :
perdre un fait obligatoire, faire passer UNKNOWN pour valeur par défaut,
confondre choix et réglage observé, casser reprise/focus ou afficher une notice
inapplicable. Les invariants et scénarios adverses sont inscrits au design/spec.

## Livrables préparés et observations

[Proposition](../../../openspec/changes/archive/2026-11-09-ux-cal-02-native-density/proposal.md),
[design](../../../openspec/changes/archive/2026-11-09-ux-cal-02-native-density/design.md),
[scope](../../../openspec/changes/archive/2026-11-09-ux-cal-02-native-density/BUILD_SCOPE.md),
[tâches](../../../openspec/changes/archive/2026-11-09-ux-cal-02-native-density/tasks.md),
[delta](../../../openspec/changes/archive/2026-11-09-ux-cal-02-native-density/specs/mobile/blueprint-first-session-runtime/spec.md)
et append de SPEC_REGISTRY. Lectures ciblées des trois modules partagés, écran
et contrôleur réels, décodeurs/capacités/ledger et matériaux de protocole.
Le texte SCI complet et les commandes globales68 sont constatés dans le code,
pas déduits des seules captures. Aucun nouveau code fonctionnel ou type produit
modifié ; aucun schéma serveur, migration, dépendance, asset ou baseline modifié.

Revue fraîche de faisabilité `/root/ux_cal_02_builder_check` : une ambiguïté
Important corrigée puis relue. Le durcissement joint les projections réellement
servies par candidate_id ; il n'exige pas policy_ref sur supported_realizations
ou intent_id sur authority quand ces porteurs ne les servent pas. Aucun champ
serveur nouveau et UNKNOWN collecte préservé. Verdict après précision :
**nothing important left**. Ce n'est pas une revue du code à implémenter.

## Croquis validé

**Pas encore validé : G1_PENDING.** [Composition avant/après proposée](../../../openspec/changes/archive/2026-11-09-ux-cal-02-native-density/UX_CAL_BOARD.md).
L'entrée donne une priorité courante ; cadre partagé avec contexte, une valeur
et unité, action compacte locale et détails. Les sous-étapes d'observation ne
font aucune mutation avant Enregistrer. Cibles proposées48contre68 et fenêtre
112contre168 minimum, à mesurer réellement après build, croissance grande fonte.
Ce croquis ASCII n'est pas un rendu iOS/Android nouveau.

## Inventaire — une information, une seule fois

L'[inventaire détaillé](../../../openspec/changes/archive/2026-11-09-ux-cal-02-native-density/UX_CAL_BOARD.md)
lie chaque élément à un champ effectivement servi ou à un état de formulaire.

| Élément | Information | Source (contrat de données) | Doublon ? |
|---|---|---|---|
| Réglage et unité | Choix ou fait utilisé distinct | CalibrationDraft.load/observedLoad et profil négocié/context | non |
| État SCI | Décision courante/provisoire | result/authority/allowed_actions | non |
| Contexte | Identité réelle déclarée | progress.context ou formulaire avant ouverture | non |
| Aide | Commun/profil/arrêt sourcés | protocol_material source_ref/sha256/text | non |
| Historique | Anciennes observations, pas permission | progress.observations/reported_stop_reasons | non |

## Comparaison avec la référence validée

Avant = [receipt PLAN-CAL-01](../../../clients/mobile/visual-contract/review-receipts/plan-cal-01/receipt.json),
pixel_decision « Valider ces pixels contrôlés ». Entrée/machine/haltères sont
liés dans le board G1. Même Frame C/RecessedWindow/NumericReadout/mark/tokens ;
MISSION/exécution/ack restent read-only. Pas de comparaison après native ni
acceptation revendiquée dans cette préparation.

## Changement unique de l’itération

Demande : « The calibration UI has too much text, oversized CTAs and insufficient
visual efficiency for a mobile device. » Recomposition bornée G1 avant code.
Les demandes de densité, aide et groupes factuels seront présentées séparément
avant/après au board réel. Les mineurs A/B sont comportementaux et ont leurs
tests/revue, sans modifier la science ou masquer leur portée par une retouche.

## Vérifications réellement exécutées / à compléter

- check_scope : **DOCS**, vérification locale requise check_spec_protocol ;
  aucun sweep, budget Ruff ou suite produit nécessaire à cette préparation.
- check_spec_protocol : passant.
- OpenSpec `validate --all --strict --no-interactive` : **17/17**.
- Aucun test produit nouveau, rendu natif après, CI distante, Sonar ou preuve
  physique nouvelle revendiqué. Les liens/sources de ce dossier sont relus.

GO BUILD + G1 attendus avant apply conformément au mandat et CLAUDE.md §6/5.6.
Après réception : tests/implémentation/revues, board de pixels natifs réel et
acceptation avant commit UI (§5.1), puis livraison autonome sous GOV-MERGE-01.
Ce reçu n'est pas une demande de GO MERGE ni une autorisation de déploiement.

Preuves de préparation conservées hors worktree dans
/private/tmp/auren-ux-cal-02-review-evidence/ ; ne pas nettoyer le worktree avec
son travail documentaire unique. DATA et RELEASE restent ouverts.
