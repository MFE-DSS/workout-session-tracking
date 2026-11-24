# UX11 — G1 proposé, pas pixels acceptés

Une composition fonctionnelle unique. Le dessin suivant décrit les rôles et la continuité, pas un master pixel ni un nouvel asset. Mise en œuvre dans les primitives DA08/FrameC/RecessedWindow/NumericReadout inchangées.

```text
[×]  Extension de jambes                 S2 / 2
     Prescription capturée : 8–12 rép.
┌ instrument ─────────────────────────────────┐
│ série précédente enregistrée               │
│ 17,5 kg affichés · 9 rép.     [source ›]     │
│ même contexte enregistré                   │
│ ────────────────────────────────────────── │
│ série actuelle — à déclarer                 │
│ [ — kg affichés ]       [ — répétitions ]   │
│ [              Enregistrer S2             ] │
│ état situé : brouillon / envoi à vérifier / │
│ enregistré / refusé / fait relu   │
└────────────────────────────────────────────┘
[Journal/options]       repos/setup canoniques
```

Le17,5/9 vient du cas synthétiqueSOURCE_FEASIBILITY, pas d’une prescription UX11. Référence secondaire dans le même instrument, sans carte supplémentaire. Le bleu ne colore pas un fait utilisateur en preuve du moteur ; encre/mémoire neutres, signal uniquement pour l’action actuelle. Pas de railEASY/TARGET/PUSH sans bornes appropriées.

## Transitions situées
- Toucher le nombre courant ouvre l’IME dans l’instrument ; l’autre brouillon est préservé. Annuler/Retour restaure la saisie précédente, aucun envoi.
- Enregistrer appelle recordFact avec le temps de c.eventTime et les paramètres canoniques. Le champ ne devient pas succès avant commit local. Pending/unknown conserve les valeurs et propose seulement les actions canoniques de vérification ; pas de nouvelle commande.
- Au reçu : « Enregistré » qualifie seulement la commande ; « fait relu » exige la lecture indépendante. Les détails techniques/IDs sont dans une disclosure. Aucun changement plein écran automatique pour le statut.
- Le focus sur la série soumise reste pendant le feedback ; le curseur moteur, repos et permission suivante restent souverains. Passer à la suite est explicite et appelle les actions existantes.
- Sans référence : même acquisition, indication compacte indisponible ; aucune valeur héritée ni faux zéro. Le fait actuel reste saisissable sous ses permissions.

## Fonte et clavier — preuve à produire après GO
360/480dp, normal et1,786×. Priorité d’espace à l’exercice/série, au champ actif et à la commande ; mémoire secondaire se replie lors de l’IME, accessible à nouveau sans écran dédié. Aucun fontScale désactivé, champ masqué ou limite de lignes sur valeur/unité/statut. La présence exacte dans viewport et le nombre de défilements seront mesurés nativement, pas garantis par ce texte. Touch targets≥48dp, focus exercice→référence/source→réglage→répétitions→validation, Retour d’abord clavier/annulation puis sortie canonique.

## Comparaison à soumettre
Une seule paire principale avant/après du V3 actuellement canonique (inchangé parUX10) contre UX11, mêmes données/source/séance. Annexes strictement nécessaires : référence non qualifiée, pending/refus et360/480dp/grande fonte. Maximum8captures représentatives + vidéo courte et sources, pas une nouvelle série de concepts. Pixels et recette physique toujours à décider séparément.


Limite d’état soumise au GO : le journal expose pending/inflight/acked/failed/resolved, sans marqueur permettant de distinguer « jamais tenté » et « réponse perdue ». L’instrument distingue brouillon, local durable, reçu, refus et état d’envoi incertain ; l’attente et le résultat inconnu sont réunis sous « Envoi à vérifier ». Pas de promesse de six états séparément observables ni de nouvel état métier.
