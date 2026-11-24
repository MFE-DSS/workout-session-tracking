# UX11-C — composition instrumentale ciblée

24 novembre 2026. Même change, même branche, même fonction UX11. Les pixels précédents sont **NOT_ACCEPTED** ; leurs sources, 34 fichiers de travail, tests et captures sont figés dans `ux11c-evidence-20261124/preserved-ux11-before-c`. Aucun nouveau moteur, API ou contrat de commande.

## Brainstorming / Options / Risques / Choix retenu

Le défaut à corriger est la priorité du texte et du contenant sur l’objet manipulé. La voie retenue est une seule composition : deux lectures numériques situées dans la série courante, une référence compacte et une commande directement attachée. Réduire uniquement les espacements conserverait la structure refusée ; ajouter un graphique ou une calibration inventée n’a pas de source. Aucun autre concept proposé.

## Croquis validé

Source : demande précise de l’opérateur, « Keep the previous confirmed set visible without giving it the same visual priority as the performed values being entered », « maintain the same identifiable current-set object » et « At large text size, reflow rather than shrink critical content into unreadability ».

Le protocole `AUREN_UI_ITERATION_PROTOCOL` G1 précise : « Une demande ponctuelle et précise de l’opérateur […] vaut croquis pour ce seul changement. » Le mandat UX11-C borne cette correction. Le GO/G1 fonctionnel antérieur reste acquis ; aucun pixel nouveau accepté implicitement.

```text
×  Extension de jambes                         marque
S1    17,5 kg affichés × 9 rép.                 source ⓘ
S2 / 2                       état court (fixe à l’IME)
┌ Frame C — fenêtres de l’objet courant ─────────────┐
│ ┌ RecessedWindow ──────────┐ ┌ RecessedWindow ────┐ │
│ │ Appareil                │ │ Répétitions         │ │
│ │ 18,5 kg affichés         │ │ 8 rép.              │ │
│ └─────────────────────────┘ └─────────────────────┘ │
└───────────────────────────────────────────────────┘
 [annuler si édition]      [Enregistrer / Vérifier S2]
 Journal                                   Continuer*
```

`*` Une seule action Continuer, selon les gates déjà existantes. Après ACK, elle peut prendre la place de la commande principale ; le contrôle de relecture reste disponible dans les détails. Un refus ouvre les options canoniques. Aucun succès déduit d’une lecture ou d’un reçu manquant.

Le dessin transpose les demandes, pas un nouveau master autonome. La référence garde son porteur unique hors de la grande surface de lecture, reste visible à l’IME et n’est jamais bleue par simple origine manuelle. La série actuelle conserve son identifiant, ses deux zones numériques et leurs unités quand l’état change ; seules édition/lecture, commande et emphase changent.

Cotes de mise en œuvre à éprouver : gouttières20 dp existantes ; largeur320/440 dp à360/480 ; grille `u` existante ; fenêtres en proportion2:1 et espace2u ; rôle `figure`40 pour les valeurs et unités dérivées du readout verrouillé, texte secondaire `small`14. Grande fonte ou nombre long : fenêtres sur deux lignes pleine largeur, sans réduction des rôles ; ScrollView pour amener le champ actif, commande hors défilement et au-dessus de l’IME. Cibles48 dp indépendamment des marques visibles. Pas de nouvelle palette, de modification des géométries ni de baseline.

## Inventaire — une information, une seule fois

| Élément | Information | Source (contrat de données) | Doublon ? |
| --- | --- | --- | --- |
| Identité de l’objet | séance/exercice/série et position réelle | ContextTarget issu ExecutionV3 | non |
| Référence S1 | valeur et reps de la série précédente qualifiée | ContextRead.reference, même occurrence/contexte strict | non |
| Deux fenêtres | réglage/reps actuels, indépendants | draft React puis fait local/relu effectif | non |
| État court | à déclarer, incertain, refusé, reçu ou relu | mêmes localOperations/local_facts et lecture effective | non |
| Commande locale | action réellement disponible | mêmes handlers recordFact/sync/onContinue/onJournal | non |
| Repos/installation | permission courante, durée si connue | workPermissionV3, sans nouveau calcul d’autorité | non |
| Source et limites | identités, révisions, horodatage/provenance | mêmes disclosures, détail sur demande | non |

## Comparaison avec la référence validée

DA08, Frame C, RecessedWindow, NumericReadout, marque et tokens sont conservés octet pour octet. Le premier état du storyboard est l’UX11 refusé, explicitement étiqueté, pas une baseline acceptée. L’avant et l’après natifs seront exécutés sur une nouvelle occurrence synthétique identique entre versions ; aucune réécriture des faits de la première recette.

## Changement unique de l’itération

Priorité et continuité du même instrument Action. Les méthodes de source, horloges, UUID, payloads, autorisations et file durable restent inchangés. Preuve finale : avant prêt, après prêt, édition IME, reçu incertain ou relu ; contre-épreuve grande fonte et 360/480 dp. Nouvelle décision pixels opérateur avant tout commit UI.

## Limite des primitives

Aucune impossibilité démontrée à ce stade. Les géométries acceptent des fenêtres composées à la largeur disponible. Si leurs insets empêchent une lecture lisible malgré le reflow, consigner les bornes mesurées et proposer un amendement minimal ; ne pas modifier les primitives dans cette tranche.

## Qualification native finale du 24 novembre

Le premier contre-exemple à 178,6 % masquait S2 lors du défilement. La correction conserve la ligne S2/état dans le même objet, au-dessus des fenêtres défilantes, et condense la référence en un seul porteur. Aucune réduction typographique nouvelle : le cap de NumericReadout reste celui du composant verrouillé. L’entrée ferme le détail de source ; le focus utilise l’offset mesuré de chaque fenêtre.

Les captures finales couvrent 360 et 480 dp avec IME réel, puis 360 dp à 178,6 %. En grande fonte, la fenêtre inactive peut être partiellement hors champ et reste accessible par défilement ; S2, la référence, le champ actif, son unité et les commandes restent visibles. Ce scénario ne démontre pas de limitation exigeant un amendement de primitive.

Une lecture 409 transitoire après SET reste une indisponibilité explicite ; la vérification suivante acquiert une vraie référence qualifiée. La vue ne fabrique aucun cache de fraîcheur. Neuf transports PUT du même UUID et du même corps par l’expéditeur existant produisent une seule observation serveur, révision 1. La reprise SQLite conserve fait et intention exacts de pending à acked. Les six observations antérieures restent identiques. Aucun FINISH n’est envoyé dans cette campagne.
