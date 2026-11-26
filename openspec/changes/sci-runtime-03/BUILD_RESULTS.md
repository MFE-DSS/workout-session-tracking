# SCI-RUNTIME-03 — résultats après GO, checkpoint local

Parent3d4c7577. GO opérateur26novembre2026, autorisation exacte dans AUTHORIZATION.json ; aucun budget ou contrat scientifique modifié.

## Changements
Contexte de parsing privé par worker/owner/profil, maximumdeuxgabarits et vues indépendantes. Octets vérifiés avant hit, catalogue valide distinct=miss, changement d'autorité invalide cache et vueV3. Contrôles de bundle finaux inchangés. Digest calculé après DTO strict et vérifié indépendamment avant retour ; observations et writers intacts.

## Preuves locales
RED initial7FAIL/2PASS : double parsing2vs1, digest entier non stable et corruption acceptée ; les floats admissibles étaient déjà stables. Garde supplémentaireRED→GREEN pour vueV3 invalide après refus d'une nouvelle génération ; plafonds de sources inchangés. Régressions10PASS, puis suiteciblée+broad344PASS/4skips de plateforme (15fichiers). Après extraction du helper de normalisation :56PASS/4skips pour les trois fichiers touchés. Aucun skip ajouté. Ruff fichiersmodifiésPASS, budget260≤548, BanditPASS, OpenSpec strict/protocolePASS. Pas de full sweep local pour SHARED_CODE.

## Limites et étapes restantes
Ce checkpoint n'est pas la qualification native du nouveau code. Les anciens prototypes/témoins rouges restent dans les preuves privées. Nouvelle archiveGit, profil et sourcepins exacts requis pour la campagneLinux. Revue indépendante, CI, merge, CI canonique et closeout restent à effectuer. Aucune activationQA/DATA/release ; lecteurdisabled.
