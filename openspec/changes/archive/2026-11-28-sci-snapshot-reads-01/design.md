# Design approuvé — scope SQL borné

## Brainstorming / Options / Risques / Choix retenu
L'amendement approuvé écarte hausse de budgets, sous-comptabilisation et cache global. Choix : mémorisation par OwnedReadCapture pendant sa transaction SQLite figée. has_table conserve uniquement les deux noms internes déjà utilisés ; evaluation_for borne son stockage au plafond sessions existant, sans refuser les lectures hors cache ; runtime_authority conserve au plus une valeur. Les résultats retournés sont des copies indépendantes, y compris leurs raisons et JSON imbriqués. Les valeurs absentes restent absentes. Les appels réels conservent leurs compteurs et les délais restent contrôlés sur les hits.

À la fin de open_owned_capture, fermer obligatoirement SQLite et vider les seuls caches ajoutés, y compris sur exception. Aucun cache de verdict scientifique : qualify_v3 continue tous ses contrôles pour chaque fait. Une future capture reprend la DB et ses révisions ; le cache ne survit pas à une autre identité propriétaire.

Le cas100 V3 sera reconstruit comme fixture structurelle explicite avec bundle attesté réel ; il ne représente pas100 STARTs permis par le produit actuel. Les14 V3 canoniques et le mixte100 restent contrôlés par le parcours HTTP inventory2 existant. L'efficacité SQL n'établit ni budget CPU natif ni qualification de l'ancienne image.
