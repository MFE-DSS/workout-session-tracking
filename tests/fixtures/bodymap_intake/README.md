# Fixtures d'intake BodyMap

**Ces fichiers ne contiennent AUCUNE anatomie.**

Chaque `<path>` porte un tracé volontairement dégénéré (`M0 0 L1 1` — un segment
de deux points). Ce sont des **squelettes structurels** dont le seul rôle est
d'exercer le validateur `scripts/bodymap_asset_intake.py` : grammaire des
identifiants, ordre des groupes, correspondance surface → zone, sûreté runtime.

Le dépôt ne dessine pas d'anatomie et n'en génère pas. La géométrie réelle vient
du workspace opérateur externe et passe une **revue anatomique humaine** que ces
fixtures ne simulent pas et ne remplacent pas.

| Fichier | Ce qu'il exerce |
|---|---|
| `valid_back_two_frames.svg` | plaque conforme : 2 cadres, contexte premier, ordre stable, surfaces déclarées |
| `invalid_context_not_first.svg` | le contexte n'est pas le premier groupe |
| `invalid_id_grammar.svg` | identifiant hors grammaire contractuelle |
| `invalid_unmapped_surface.svg` | surface ne correspondant à aucune zone métier |
| `invalid_forbidden_zone.svg` | surface nommant une zone métier interdite |
| `invalid_not_square.svg` | panneau non carré |
| `invalid_runtime_unsafe.svg` | `<script>`, `<image>` et `style` inline |
| `invalid_surface_order.svg` | ordre des surfaces différent entre deux cadres |

`lats` et `upper_back` sont utilisés dans la fixture valide parce que ce sont les
zones que la plaque `back` doit servir d'après le bon de commande — **aucune zone
nouvelle n'est inventée ici**.
