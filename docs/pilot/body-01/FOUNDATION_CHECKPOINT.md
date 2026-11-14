# BODY-01 — checkpoint technique de la tâche 1

Parent canonique1462482. Ce commit contient uniquement modèle/metadata, migration
additive, kernel de commandes, lecture des lignées et leurs témoins. Pas de route
BODY nouvelle montée, pas de nouveau consumer visible ou géométrie UI.

Les adaptateurs legacy/readers/API, templates SSR, ports natifs et composition
restent dans le worktree non committé. Le comportement BODY complet ne se déduit
pas de ce checkpoint. Les anciens consommateurs restent ceux du parent jusqu’à
la suite du même change. Une seule PR BODY en brouillon ; pas de merge partiel
ni d’archive avant fermeture des gates applicables.

Le plan d’implémentation autorise ce checkpoint de fondation sans UI. Les pixels
SSR et le master BODY natif restent non acceptés, NUT dépend de cette migration
et MOB06 dépend des parents partagés. Aucun APK, activation, OTA ou déploiement.
