# SCI-RUNTIME-03 — résultats après GO, checkpoint local

Parent3d4c7577. GO opérateur26novembre2026, autorisation exacte dans AUTHORIZATION.json ; aucun budget ou contrat scientifique modifié.

## Changements
Contexte de parsing privé par worker/owner/profil, maximumdeuxgabarits et vues indépendantes. Octets vérifiés avant hit, catalogue valide distinct=miss, changement d'autorité invalide cache et vueV3. Contrôles de bundle finaux inchangés. Digest calculé après DTO strict et vérifié indépendamment avant retour ; observations et writers intacts.

## Preuves locales
RED initial7FAIL/2PASS : double parsing2vs1, digest entier non stable et corruption acceptée ; les floats admissibles étaient déjà stables. Garde supplémentaireRED→GREEN pour vueV3 invalide après refus d'une nouvelle génération ; plafonds de sources inchangés. Régressions10PASS, puis suiteciblée+broad344PASS/4skips de plateforme (15fichiers). Après extraction du helper de normalisation :56PASS/4skips pour les trois fichiers touchés. Aucun skip ajouté. Ruff fichiersmodifiésPASS, budget260≤548, BanditPASS, OpenSpec strict/protocolePASS. Pas de full sweep local pour SHARED_CODE.

## Correctifs de revue avant qualification
La relecture des deux correctifs conclut : aucun point de revue ouvert ; qualification native et CI restent requises. Une revue indépendante a identifié le pin vide/NULL du manifeste comme Important : deux témoins sur bundle réel et contexte chaud échouent avant correction, puis passent après refus explicite du digest invalide avant lecture. Le test worker restaure désormais ses modifications globales. Campagne ciblée+broad après correctifs : **346PASS/4skips Linux**, sans nouveau skip, en88,11s.

Le premier essai Linux sur916cf2d a exécuté0test : harnais pytest incomplet (`py.py` absent). Logs, fixtures et sources conservés ; seuls ses3conteneurs,5volumes et scratch ont été nettoyés. Une nouvelle copie doit qualifier le prochain HEAD corrigé ; aucune preuve native du nouveau produit n’est encore revendiquée.

## Limites et étapes restantes
Ce checkpoint n'est pas la qualification native du nouveau code. Les anciens prototypes/témoins rouges restent dans les preuves privées. Nouvelle archiveGit, profil et sourcepins exacts requis pour la campagneLinux. Revue indépendante, CI, merge, CI canonique et closeout restent à effectuer. Aucune activationQA/DATA/release ; lecteurdisabled.

## Actualisation après campagne native et merge code
Code7393ac1 qualifié dans le banc Linux natif : 349PASS/1skip optionneljsonschema ; Legacy5/5, V3 5/5,100faits2/2 admis, digests concordants, un parsing par sonde. V3CPU1,626–1,708s ; refus500/501 et ressources conservés. Voir docs/pilot/sci-runtime-03 pour mesures et incidents de harnais. Revue finale sans point ouvert. PR452 fusionnée en7327256 ; CI PR45891313230 completed/success (9038backend/3skips,1610mobiles+TS,77visuels), SonarERROR consultatif8smells/0bug/0vulnérabilité/0hotspot,nouvellecoverage95,8%. CI canonique en cours au moment de cette actualisation.
