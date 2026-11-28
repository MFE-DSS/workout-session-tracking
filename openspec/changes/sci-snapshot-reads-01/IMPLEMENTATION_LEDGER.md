# Exécution — 28 novembre2026

Parent c8b413efa027467600654a445521ca8e564b4384, GO SQL borné enregistré. Produit : seul sqlite_source.py ; deux tests autorisés et documents associés.

## RED / GREEN
- SQLite initial :3 échecs attendus de budget de lectures répétées,18passes ; après correctif et gardes additionnelles24passes.
- Structure100 V3 : refus SQL4096 initial, confirmé BudgetExceeded(statements), puis100 faits avec provenance qualifiée et digest valide, sous budgets inchangés. La fixture est explicitement structurelle, pas100 STARTs actuels.
- Un témoin de hash a d'abord observé le checkpoint WAL différé d'un writer de fixture encore ouvert. Fermer explicitement les writers de test avant le témoin a résolu ce défaut du harness, sans changement produit.
- Broad reader/SCI :331passes,4skips Linux existants sur Mac ;14passes HTTP consommateur. Tests d'échéance/copies ajoutés ensuite repassés dans les24 SQLite. Pas de full sweep local shared_code.
- Anciennes bases du banc exact relues sans writer :V3=14/SQL282 ;mixte100/SQL557 ;structure100V3/SQL3918 ;Legacy100/SQL904. Comptes A/B/vide isolés ;UNKNOWN conservé sur préfixe/autorité absente/texte horsplafond.10digests et hashDB valides. Local Python3.14.7/Darwin : ne qualifie pas le runtime cible.

## Choix retenus et limites
Deux présences de tables internes maximum ; évaluations bornées au plafond sessions existant et lectures hors cache toujours permises sous budget réel ; une autorité runtime. Copies indépendantes au premier retour et sur hits. Deadline conservée sur tous les accès. Fermeture SQLite obligatoire et caches ajoutés vidés même sur exception. Aucun verdict SCI en cache.

Les budgets SQL4096,VM2M,CPU2/3s,AS512Mio,wall3s et JSON/sortie sont intacts. Le gain de SQL ne prouve pas le budget CPU/AS de l'image corrigée. L'image opérationnelle1f81d5b8 reste inchangée et le lecteur DISABLED / qualification opérationnelle HOLD. Aucun run cloud, montage candidat, transfert ou changement OVH exécuté.

Ruff ciblé/budget et Bandit passent ; annotations B608 historiques inchangées. OpenSpec strict et protocole documentaire passent. Revue indépendante du diff entier : aucun finding bloquant ou mineur à corriger. Publication et CI exacte restent à finaliser.
