# SCI — contrat premier plan v2, livraison isolée

7 novembre2026. GO reçu : **« Valider le contrat v2 et ce build isolé »**. Base2cddf5d ; les résultats distants/SHA de livraison seront consignés dans le reçu de PR après exécution. **Contrats exécutables, NOT_ADMITTED / NOT_SERVED / READY_NOT_PRODUCED.** Aucun producteur de plan v2 ou registre positif n'est livré.

## Brainstorming / Options / Risques / Choix retenu
Conserver v1 imposait des crédits exacts non calculés et des charges massiques qui ne représentent pas tous les réglages. Modifier silencieusement v1 aurait changé le sens de READY et cassé ses consommateurs. Choix explicitement approuvé : contrat successeur côte à côte, quinze rapports qualitatifs, prescriptions typées, durée complète toujours requise. Les anciennes sources/pins et leurs rejeux restent inchangés.

## Implémenté
- `first-plan-request/2.0.0` et `first-plan-recommendation/2.0.0`, profil `first-bodybuilding-inputs/2.0.0`. Faits Blueprint v1 et observations datées/contexte typées réutilisés, sans nouvelles acquisitions.
- Cinq faits minimaux inchangés : objectif, population déclarée, cadence, budgets par séance et limitations. Poids/taille/expérience/priorités restent facultatifs ; souhaits distincts des observations. Matériel inconnu reste inconnu.
- Empreinte des faits/snapshot/propriétaire/révision/as_of/versions/bundle séparée de celle de l'évaluation complète avec observations. Ordre d'événements normalisé, ordre des priorités conservé. Les copies Pydantic non validées sont revalidées aux frontières.
- Prescriptions `OBSERVED_SETTING` (appareil/réalisation/côté/unité et épisode/essai/acceptation exacts) ou `BOOTSTRAP_PROTOCOL` (quatre phases et références instruction/arrêt/réessai/temps). Les références textuelles ne sont pas admission. Aucun kg de départ ou incrément nouveau.
- Quinze zones : rôles qualitatifs sourcés, UNKNOWN ou absence de rôle supporté sous preuve spécifique. Aucun `credited_sets` accepté ; couverture des déclarations distincte d'un volume efficace ou d'un diagnostic individuel.
- Durée UNKNOWN, CONDITIONAL_DIAGNOSTIC ou SUPPORTED. READY structurel exige plan revu, faisabilité, références et borne supportée couvrant travail/repos/préparation-calibration/opérations dans le budget, y compris bootstrap. Une forme valide ne prouve aucune de ces autorités.
- Validation d'échange sur vrais bundle piné et registre d'admission vide inchangés. Sujet/snapshot/révision/as_of/versions/empreintes et sources contrôlés ; conflit → manque → politique. Réglage provisoire vérifié par calibration1.1.0-isolated. Rôles/exclusions/intentions et réalisation contrôlés pour les drafts observés.
- Schémas JSON et neuf exemples de contrat reproductibles, manifestes de sources/code/artefacts. Aucun exemple public READY ; nul engine/policy/binding car aucun producteur n'émet ce contrat. Générateur de fixtures uniquement, pas nouveau moteur négatif.

## Profil d'autorité réellement disponible
Le validateur actuel accepte seulement les refus cohérents avec l'autorité vide : CONFLICTING_DATA, INSUFFICIENT_DATA ou POLICY_UNAVAILABLE. Les autres états restent représentables pour un futur producteur admis, mais ne sont pas validables sur ce registre. Il refuse les faux bindings, moteurs v1 relabellisés v2 et toute revendication READY, même de forme complète.

Un draft observé peut illustrer les références et la dose partielle historique ; cela n'admet ni son allocation ni le bundle. Un bootstrap n'a pas aujourd'hui de protocole admis ; SUPPORTED/diagnostic n'ont pas de base temporelle v2 liée. Ces revendications sont donc refusées à l'échange. La qualification G17 nécessite son futur binding de projection ; aucun rôle conditionnel n'est déduit d'un libellé générique. Ce profil conservateur sera étendu par une prochaine version revue, pas un paramètre caller.

Le schéma est produit depuis Pydantic ; ses exemples sont validés avec les modèles et l'échange. Aucun validateur JSON Schema indépendant ajouté aux dépendances. PLAN devra vérifier l'interopérabilité et négocier explicitement v2 ; FirstPlanClient et les exports v1 restent inchangés et refusent v2. Les owner refs sont cohérence contractuelle, jamais authentification d'un compte.

## Vérification et responsabilités différées
Tests nouveaux, scoped broad scientifique/historique, contrôles tier et revues séparées seront consignés avec leurs résultats effectifs avant publication. Aucun full sweep local, test appareil, appel de production ou nouvelle validation biologique/temporelle n'est déduit de ces checks.

SCI-POS01..07 restent dans la [proposition réservée](../../../proposals/science-initial-policy-positive-admission.md) et le parent scientifique. Le choix v2 est reçu ; la représentation est livrée sans admission C5 ni modification de v1. C1/C2/C3/C4/C5/C6 sur bundle exact, protocole initial et base temporelle positive restent à décider/prouver ; vrai binding/producteur/READY puis handoff PLAN non livrés. DATA, RELEASE et MOB04 demeurent hors de ce GO.
