# `design/auren/source/bodymap/` — BodyMap Design Source

**État actuel** : ce dossier contient **le contrat de mapping uniquement**
([`auren_bodymap_mapping.yaml`](auren_bodymap_mapping.yaml)). **Aucun master anatomique n'est présent.**

## Contenu autorisé aujourd'hui
- `auren_bodymap_mapping.yaml` — contrat sémantique versionné (Layer A), YAML 1.2 en syntaxe JSON-compatible
  (lu par la stdlib `json`, sans PyYAML). 0 géométrie.
- `README.md` — ce fichier.

## Ce qui n'est PAS ici (et pourquoi)
- **Aucun master anatomique / SVG / PNG / géométrie / path / coordonnée.** Aucun asset ne peut entrer sans
  **intake** (cf. [`../../AUREN_ASSET_INTAKE_CHECKLIST.md`](../../AUREN_ASSET_INTAKE_CHECKLIST.md)).
- Le futur **master humain** appartient à `OPERATOR_ASSET_03.1` (production humaine + validation anatomique).
- L'**intake technique** (optimisation, IDs, budgets) appartient à `Sb_ASSET_03.2`.
- L'**intégration runtime** appartient à `Sb_ASSET_04.1`, **après** franchissement de l'`ASSET INTEGRATION
  GATE`.

## Règle
```
La présence d'un fichier dans ce dossier NE signifie PAS qu'il est autorisé
dans app/static/. L'intégration runtime exige le franchissement de
l'ASSET INTEGRATION GATE (humaine / anatomique / juridique / mobile).
```

Le contrat `auren_bodymap_mapping.yaml` **miroir** la vérité runtime (`ZONE_LABELS`, `_WA_ZONE_TO_REGION`),
il ne la **remplace pas** dans `Sb_ASSET_01.2`.
