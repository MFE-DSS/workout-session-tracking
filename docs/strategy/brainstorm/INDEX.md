---
name: brainstorm-index
type: brainstorm-archive-index
status: READ-ONLY BRAINSTORM ARCHIVE
created: 2026-07-02
---

# Brainstorm Archive — UI Transformation

Ce dossier archive des sessions de brainstorming produit sur la transformation UI de SPIGNOS. Ces documents ne sont **pas** des specs exécutables. Ils servent de matière première à la roadmap `docs/strategy/UI_TRANSFORMATION_ROADMAP.md` et aux futures specs `Sx_UI_01 → Sx_UI_11`.

## Statut d'archivage

Chaque source livrée par l'opérateur est archivée en **deux versions** :

- `..._raw.md` — capture verbatim tel que reçu, encodage inclus (référence de trace)
- `..._normalized.md` — même contenu, encodage UTF-8 réparé (mojibake corrigé), typographie remise en état ; **aucune reformulation sémantique**

Corrections d'encodage appliquées dans les fichiers `normalized` :

| Mojibake | Décodage |
|---|---|
| `Ã©` | é |
| `Ã¨` | è |
| `Ãª` | ê |
| `Ã ` | à |
| `Ã§` | ç |
| `Ã®` | î |
| `Ã¯` | ï |
| `Ã´` | ô |
| `Ã»` | û |
| `Å"` | œ |
| `â€™` | ’ |
| `â€œ` | “ |
| `â€` | ” |
| `â€“` | – |
| `â€”` | — |
| `â€¦` | … |
| `â` (isolé, contexte tiret) | — |
| `Â` (parasite avant espace/ponctuation) | supprimé |
| `îfileciteî...î` | supprimé (marqueur interne LLM source, non-sémantique) |
| `îciteî...î` | supprimé (marqueur interne LLM source, non-sémantique) |

**Règle stricte :** aucune reformulation d'idée, aucune correction de style, aucune amélioration. Si un passage reste incertain après décodage, un marqueur `TODO_ENCODING_REVIEW` est inséré et signalé ci-dessous en section « Écarts ».

## Documents archivés

| Fichier | Rôle | Statut | Notes |
|---|---|---|---|
| [UI_TRANSFORMATION_BRAINSTORM_V1_raw.md](UI_TRANSFORMATION_BRAINSTORM_V1_raw.md) | Source V1 verbatim | archive | Cadre transformation mobile minimaliste. Encodage cassé (mojibake UTF-8 double). |
| [UI_TRANSFORMATION_BRAINSTORM_V1_normalized.md](UI_TRANSFORMATION_BRAINSTORM_V1_normalized.md) | Source V1 décodée | référence | Version lisible. Base de synthèse pour `UI_TRANSFORMATION_ROADMAP.md`. |
| [UI_TRANSFORMATION_BRAINSTORM_V2_raw.md](UI_TRANSFORMATION_BRAINSTORM_V2_raw.md) | Source V2 verbatim | archive | Transformation biomécanique minimaliste. Encodage cassé. |
| [UI_TRANSFORMATION_BRAINSTORM_V2_normalized.md](UI_TRANSFORMATION_BRAINSTORM_V2_normalized.md) | Source V2 décodée | référence | Version lisible. Base de synthèse (complément de V1). |
| [UI_TRANSFORMATION_BRAINSTORM_V3_duplicate_of_V2_raw.md](UI_TRANSFORMATION_BRAINSTORM_V3_duplicate_of_V2_raw.md) | Source V3 verbatim | archive | **Doublon quasi complet de V2** (voir ci-dessous). Pas de `normalized` créé. |

## Doublon V3 vs V2

**Constat :** V3 partage le même titre (« Transformer SPIGNOS en application biomécanique minimaliste »), la même structure de sections (Diagnostic → Références → Cible esthétique → Cadre de benchmark → Brainstorming marque → Chantier), les mêmes benchmarks (Strong, Hevy, Levels, Oura, WHOOP), les mêmes trois territoires visuels (Clinical Lab / Quiet Instrument / Soft Biomechanics), les mêmes trois finalistes de nom (MYON / VYON / RATEL), et les mêmes recommandations finales que V2.

**Écarts V3 vs V2 :** aucun écart substantiel détecté au moment de l'archivage. V3 apparaît comme une re-livraison bit-à-bit ou quasi-bit-à-bit de V2 dans le flux opérateur.

**Traitement :**
- V3 est archivé en `raw` uniquement (traçabilité).
- Aucun fichier `V3_normalized.md` créé.
- V3 n'est **pas** utilisé comme source dans `UI_TRANSFORMATION_ROADMAP.md`.
- Si un futur diff révèle une section unique dans V3, elle sera extraite ici sous la rubrique « Écarts V3 substantiels ».

## Écarts V3 substantiels

_(aucun écart substantiel détecté à ce jour ; section vide, à remplir si un diff futur en révèle)_

## Passages à réviser (TODO_ENCODING_REVIEW)

_(aucun marqueur `TODO_ENCODING_REVIEW` inséré à ce jour ; section vide, à remplir si un passage résiste au décodage)_

## Utilisation

- Pour la **synthèse actionnable** : lire [`../UI_TRANSFORMATION_ROADMAP.md`](../UI_TRANSFORMATION_ROADMAP.md).
- Pour la **matière brute d'inspiration** : lire les `..._normalized.md` (V1 et V2).
- Pour la **traçabilité forensique** : lire les `..._raw.md` (encodage d'origine préservé).

## Interdits d'usage

- Ne pas modifier les `_raw.md` (source de vérité de la trace).
- Ne pas altérer sémantiquement les `_normalized.md` (correction d'encodage uniquement).
- Ne pas dériver des specs `Sx_UI_*` directement depuis un fichier brainstorm : passer d'abord par la roadmap synthèse.
- Ne pas renommer les fichiers ni le dossier sans mise à jour de cet index et des références dans la roadmap.
