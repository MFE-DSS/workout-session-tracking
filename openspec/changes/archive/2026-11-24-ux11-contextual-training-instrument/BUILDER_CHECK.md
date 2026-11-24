# UX11 — relecture de faisabilité avant décision

23novembre2026, `/root/ux11_builder_check`, lecture seule du paquet et des consommateurs sur9dd90ac. Aucun code ou test exécuté par le relecteur.

Aucun conflit de domaine ni besoin démontré de nouveau backend/API/contrôleur. TrainingHistoryClient.sessions→detail→GETV3 strict peut fournir la source. Trois Important de rédaction avant GO, corrigés dans les documents :

1. Lifecycle : l’interdiction vise les handlers canoniques ; un nouvel abonnement AppState read-only du resource est explicitement permis et nettoyé au démontage. Aucune ancre de temps utilisée pour qualifier la référence.
2. Observabilité : pending et résultat réseau inconnu ne sont pas distinguables dans LocalPlanOperationV3. Même état d’incertitude « Envoi à vérifier », limite explicitement soumise à l’opérateur ; aucun champ métier neuf.
3. Provenance : read_id/rows_read_at seulement dans la page d’index ; détailSCI qualifié par endpoint/identités/révision/server_now, sans readIdinventé.

Minor traité : pin du set soumis avant le routage vers exercice suivant ou COMPLETE, avec cas négatifs à tester. Les corrections sont dans le design/scope/contrat ; ne pas les présenter comme des tests produit ni une acceptation humaine. Le relecteur confirme la faisabilité et conditionne le GO à ces corrections ; aucune seconde revue des corrections prétendue ici.
