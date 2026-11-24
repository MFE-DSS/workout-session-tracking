# UX11-C — revue et corrections, 24 novembre 2026

Revue indépendante : agent ux11c_final_review, sources intégrales non committées sur parent 9dd90ac. Sources produit et tests conformes au manifeste de revue ; seul le ledger avait évolué pendant sa lecture. Aucune acceptation artistique déduite.

| Important | Correctif vérifié RED→GREEN |
|---|---|
| Une séance close pouvait ouvrir une nouvelle saisie. | Bilan terminal canonique prioritaire ; deux témoins phase COMPLETE / statut completed. |
| Une correction serveur négative pouvait ressusciter le brouillon envoyé. | Invalidation du brouillon une seule fois par nouvelle révision effective ; ressaisie explicite nécessaire. |
| Une correction négative pending/inflight/refusée exposait un nouveau SET. | Mutation verrouillée ; vérification ou journal. Trois témoins, aucun nouvel appel recordFact. |
| Résolution non réalisée ou ACK inqualifiable bloquait la continuation. | Relecture de la consigne accessible après résolution ; continuation de l’ACK disponible sans réinventer de valeur. |
| Un fait serveur indépendant nécessitait indûment un ACK local. | Fait qualifié relu affiché en lecture seule ; synchronisation du contrôleur requise. Cas voisin inqualifiable aussi bloqué. |

Le focus qui visait la fin des métadonnées est remplacé par l’offset de la fenêtre. La saisie referme la source. Le contre-exemple natif a ensuite révélé S2 hors champ à 178,6 % ; sa ligne est désormais fixe dans le même objet. Les deux captures sont conservées, aucune réduction typographique ajoutée.

Ruling : la fausse mention de référence « confirmée » pendant une lecture indisponible a été reclassée Important pour son effet sur la certitude des données. Le libellé est conditionnel et son absence a un témoin RED→GREEN. Coût si ce choix était erroné : une information de provenance trop discrète, accessible dans le détail.

Le libellé d’accessibilité de la référence inclut désormais valeur, unité et répétitions : test RED→GREEN séparé. Le terminal utilise le bilan/journal existant pour récupérer les opérations, au lieu d’un nouvel éditeur ; cela conserve une étape de navigation en séance close.

Dernier résultat complet : 138 suites / 1 549 tests mobiles, TypeScript. 90 tests ciblés backend/historique/contrat visuel. Pas de second avis indépendant des correctifs finaux revendiqué ; leurs témoins et la suite complète servent de vérification. Aucun mineur de revue restant différé.
