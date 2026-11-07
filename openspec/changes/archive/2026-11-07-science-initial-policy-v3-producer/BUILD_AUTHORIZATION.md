# SCI-P02 stage2 — décisions reçues

7 novembre2026. Réponses opérateur aux deux questions exactes de DECISION_FOR_OPERATOR :

1. **« Valider ce cas d’admission limitée »** : adulte déclaré non clinique, deux séances, sept réglages observés/qualifiés/acceptés, conventions de dose explicites et C6 exploratoire sous temps inconnu/ack exact. La publication de l’admission reste soumise à la revue SCI du bundle effectif ; aucune durée positive ou admission du bootstrap non qualifié n’en découle.
2. **« Autoriser ce build isolé »** : registre successeur, vrai producteur v3, validation canonique du profil admis, tests déterministes et sorties positives vérifiées, CI/merge/closeout sous règles permanentes. Contrats/validateurs historiques, SDK/API/UI et activation hors modification.

Le mandat PLAN reçu entre-temps est une préparation séparée sans GO d’implémentation. Il n’étend pas le build SCI aux modèles, routes, journaux ou migrations. L’admission finale est une décision SCI sur le bundle effectif documentée après sa revue, pas une inférence depuis les tests ou le seul GO BUILD. GO MERGE permanent applicable au scope complet et à sa maintenance ; aucun déploiement.
