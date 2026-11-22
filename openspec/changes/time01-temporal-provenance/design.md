## Context

Base dff03f3. Les fichiers originaux sont empreintés hors Git dans
auren-review/time01-20261122. Les données de reproduction sont synthétiques,
dans une copie AVD read-only, réseau coupé avant ouverture de l'app.

## Goals / Non-Goals

Corriger le défaut de restauration prouvé. Ne pas attribuer la cause de
l'incident original, ne pas convertir heure murale et durée monotone, ne pas
modifier les historiques ou le producteur scientifique. Pas de nouvelle
architecture générale d'horloges, seuil de dérive ou dépendance native.

## Brainstorming / Options / Risques / Choix retenu

1. Réancrer le DTO restauré : reproduit précisément le défaut, rejeté.
2. Substituer partout Date.now : contredit D11, rejeté.
3. Ancre éphémère acquise sur lecture confirmée, invalidée à la restauration
   et à la pause : retenu. Sans elle, réutiliser le repli D11 estimé existant.

Le choix ne qualifie pas une suspension sans événement de cycle de vie, ni la
latence d'une réponse ancienne. Ces cas sont observés/testés séparément et
restent UNKNOWN tant qu'une preuve manque ; aucun seuil arbitraire ajouté.

## Decisions

- Le contrôleur possède la liaison lecture serveur / instant monotone ;
  SQLite conserve le DTO server_now comme fait de lecture, jamais comme
  autorité temporelle fraîche.
- Les callbacks d'acquisition demandent l'heure à l'instant de l'action,
  indépendamment du dernier tick de rendu.
- Les corrections explicites gardent set.completed_at lorsqu'il existe ;
  sinon le formulaire existant utilise une nouvelle date explicitement
  estimée. Le contrat recordFact reste identique. SET/outbox et FINISH
  existantes ne sont pas retouchées.
- Une lecture échouée préserve COMPLETE après clôture durable, comme le
  faisaient déjà pause() et la lecture confirmée. Pas de nouvelle commande.
- Pas de modification de composition, tokens, texte, styles ou baselines.
  La qualification de pixels ne vaut pas qualification temporelle native.

## Risks / Trade-offs

Le repli estimé contient une lecture murale déclarée incertaine, pas une heure
d'effort vérifiée. Une ancre en mémoire peut encore être insuffisante face à
un gel de l'horloge monotone sans AppState ; l'incident original reste inconnu.
La publication séparée est nécessaire pour tester le correctif dans l'APK.

## Migration Plan

Aucune migration ; données et commandes déjà préparées restent identiques.

## Open Questions

Origine de la divergence historique ; horloges contemporaines absentes.
Qualification sommeil/latence/discontinuités complète avant readiness PASS.
