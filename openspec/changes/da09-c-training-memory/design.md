# DA09-C — frontières de livraison

## Brainstorming / Options / Risques / Choix retenu
Le design accepté est conservé byte pour byte. Commiter B avec C élargirait la décision humaine ; retirer temporairement B détruirait un état utile. Choix : staging exact de C, export de l’arbre indexé pour vérification, PR C indépendante. Le worktree mixte B/C reste préservé. Aucune nouvelle composition n’est décidée ici.

## Sources et états
Semaines depuis weekly_counts et window, fin exclusive et coupure serveur ; segments comptés sans position datée individuelle. Séries depuis les faits effectifs, unités machine/PER_IMPLEMENT et statuts conservés sans masse totale inférée. Poids BodyMeasurement : points valides sans interpolation, identité/date/unité/source/version exactes, groupe accessible atomique et commandes séquentielles. Jour déclaré UTC distinct du moment de journalisation. Sans accord : aucun nombre corporel ni graphique ; inconnu/partiel/précédent restent distincts du vide confirmé.

## Autorité et preuves
GO DA09/G1 C préexistant, puis décision directe « Valider les pixels finaux DA09-C du 24 novembre 2026 ». Le ZIP accepté contient11planches/27écrans natifs ; empreinte dans AUTHORIZATION.json et docs/pilot/da09-c/VISUAL_ACCEPTANCE.json. Les sources courantes sont comparées à leurs empreintes acceptées avant staging.

## Risques et réserves
Date.parse trie à la milliseconde : ordre sous-ms non qualifié, identités toujours consultables. Gestes TalkBack au doigt non qualifiés ; D4 tronqué à178,6% ; recette physique ouverte. Ces réserves ne sont ni corrigées silencieusement ni transformées en acceptation globale. Aucun OTA autorisé.

## Livraison
Base canonique fraîche, check_scope, tests sur arbre C exact, revue indépendante entière déjà effectuée et correctifs RED→GREEN vérifiés ; CI protégée du HEAD réel, merge gardé GOV-MERGE-01, CI canonique, archive/closeout. Aucune nouvelle demande GO MERGE.
