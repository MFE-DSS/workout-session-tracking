# `design/auren/source/mannequin/` — Mannequin canonique V1

## État actuel (DA-05.0, 2026-10-29)

```
CANONICAL VISUAL REFERENCE ACCEPTED (5 views, operator)
VECTOR RECONSTRUCTION REQUIRED
NOT AUTHORIZED FOR APP INTEGRATION
```

- **Référence visuelle canonique** : un pack de cinq vues (face, profil, ¾ face, ¾ dos, dos), approuvé par
  l'opérateur. On **ne le redessine pas**. Il est généré par IA (Midjourney), il sert donc de **référence** et
  jamais de **source finale** (`AUREN_VISUAL_BACKBONE §8.2` : « IA = moodboard »).
- **Asset de production** : la **reconstruction vectorielle** de ces cinq vues, à produire selon
  `docs/strategy/AUREN_CANONICAL_MANNEQUIN_V1_SPEC.md`. C'est elle, et elle seule, qui entrera dans l'app.
- **Les rasters ne sont pas dans le dépôt** : aucun raster n'est permis sous `design/auren/`, et le dépôt est
  public. Ils sont identifiés par leur sha256 dans `auren_mannequin_v1_source.yaml` et gardés par l'opérateur.

## Fichiers

| Fichier | Rôle |
|---|---|
| `auren_mannequin_v1_source.yaml` | registre : empreintes des cinq vues, orientation, cadrage mesuré, statuts |
| `README.md` | ce document |

## Règle

La présence d'une référence n'autorise **aucune** intégration. L'intégration exige la reconstruction vectorielle et
une décision de l'opérateur, consignées dans le registre. Les droits d'usage des cinq vues sont déclarés complets
par l'opérateur, qui les a générées lui-même (2026-10-29).
