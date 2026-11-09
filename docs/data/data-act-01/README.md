# DATA-ACT-01 — paquet unique de décisions du responsable

9 novembre 2026 · base auditée `fe9f6e9beb585a271ae2c2726e338359057b9f58`.
**PREPARATION_ONLY / CONTROLLER_DECISIONS_OPEN / NOT_ACTIVATED.**

Point d'entrée unique : [questionnaire et relevé de décisions](CONTROLLER_DECISIONS.md).
Le responsable peut répondre dans ce tableau, par référence à un document signé,
ou marquer une ligne OPEN avec son décideur. Une ligne vide n'est jamais une
acceptation. Aucune identité, durée, finalité autorisée, base juridique ou URL
publique n'est déduite du nom AUREN, d'un domaine existant ou d'un défaut logiciel.

Pièces de lecture : [copies PLAN et périmètre complet](PLAN_COPY_GRAPH.md),
[audit des fondations existantes et manquantes](FOUNDATION_AUDIT.md),
[rapport de préparation et vérification](REVIEW_REPORT.md).
La [proposition réservée account-data-activation](../../proposals/account-data-activation.md)
est conservée ; son [delta OpenSpec](../../../openspec/changes/account-data-activation/proposal.md)
borne cette préparation DATA-ACT-01 sans ouvrir un deuxième projet d'activation.

Une [réponse partielle D01 du 9 novembre 2026](CONTROLLER_DECISIONS.md#réponse-partielle-d01--9-novembre-2026)
est consignée : l'opérateur assume personnellement le service à ce stade et
envisage une formalisation ultérieure. Identité légale publiable, coordonnées,
juridiction et public visé ne sont pas établis par cette réponse. D01 reste
PARTIELLE ; D02–D09 et C01–C11 restent OPEN, sans politique admise ni activation.

Ce dossier décrit le dépôt et les décisions à obtenir. Il ne constitue pas une
revue juridique : les énoncés réglementaires de la spec Body historique ne sont
pas revalidés ici, et ne deviennent pas une conclusion actuelle de conformité.
Une revue compétente et sourcée, adaptée à la juridiction effectivement fournie,
reste une entrée du responsable lorsque nécessaire. Aucun test produit, accès à
une base, inspection de sauvegarde privée, donnée personnelle ou secret utilisé.

## Brainstorming / Options / Risques / Choix retenu

Option A : nouveau change autonome couvrant à nouveau DATA01–07. Risque : deux
backlogs et une fausse impression de nouvelle autorisation. Option B retenue :
réutiliser le nom réservé `account-data-activation`, ne spécifier maintenant que
le paquet de décisions, compléter son graphe par les copies PLAN déjà livrées.
Les critères hérités restent OPEN ; un éventuel build aura son scope, sa revue
et son GO propres. Ni le GO MERGE permanent ni les builds contrôlés PLAN/SCI
n'autorisent un traitement réel, un effacement ou un déploiement DATA.
