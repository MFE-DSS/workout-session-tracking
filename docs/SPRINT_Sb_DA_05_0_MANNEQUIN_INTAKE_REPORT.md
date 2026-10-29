# Sb_DA_05_0_MANNEQUIN_INTAKE — le mannequin canonique V1 entre comme référence

**Date :** 2026-10-29
**Branche :** `sb/da-05-0-mannequin-intake` (base canonique `aa62d47`)
**Nature :** intake et spécification — aucune géométrie produite, aucune surface touchée, aucun raster versionné.

## 0. Commande

L'opérateur a produit sous Midjourney cinq vues d'un mannequin neutre (face, profil, ¾ face, ¾ dos, dos) et
demande : « create the intake and production specification for AUREN's canonical exercise mannequin V1 » — six
livrables (spécification d'asset, nommage, cadrage, simplification anatomique, reconstruction vectorielle, note
aval) ; « Do not redesign the mannequin. Do not introduce new stylistic language. Treat the approved 5-view pack as
the canonical visual source. »

## 1. Brainstorming · Options · Risques · Choix retenu (`CLAUDE.md §3`)

**Conflit de spec examiné.** `AUREN_VISUAL_BACKBONE §8.2` est fermé : « jamais d'IA comme source finale (IA =
moodboard) » et « un mannequin vectoriel commun articulé ».

| Option | Pour | Contre |
|---|---|---|
| A — déclarer les rasters IA source finale | littéral du brief | contredit une décision fermée du backbone, sans amendement |
| B — le pack = **référence visuelle canonique** figée ; l'asset de production = sa **reconstruction vectorielle** | tient le brief (« canonical visual source », guide de reconstruction demandé) **et** le backbone | une étape de plus avant l'app |

**Choix : B.** Aucune décision verrouillée n'est modifiée. Si l'opérateur veut que les rasters soient eux-mêmes la
source finale, c'est un amendement explicite de `§8.2`.

**Où vivent les rasters.** La garde permanente interdit tout raster sous `design/auren/`, et le dépôt est public :
les cinq fichiers sont identifiés par **sha256** dans le registre et restent chez l'opérateur.

**Risques** : dos ambigu (deux candidats proches) → retenu celui identique au pixel à l'image jointe
(`mannequin_back_v1.png`), l'autre nommé et écarté ; droits d'usage des sorties IA → déclarés complets par l'opérateur, qui les a générées lui-même
(« le droit d'usage est complet, c'est généré par moi-même ») : `legal_review: waived-by-operator` ;
mesures fausses dans la spec → seules les mesures robustes sont publiées (toile, crâne, sol, hauteur, centrage,
entrejambe) ; un repère d'épaule calculé contredisait l'image (les bras en A faussaient la largeur) et n'a pas été
retenu.

## 2. Livrables

| Livrable demandé | Où |
|---|---|
| 1. spécification d'asset (rôle, usages permis / interdits, invariants, aval) | spec §1 |
| 2. convention de nommage | spec §2 ; registre `views[].file` |
| 3. règles de cadrage | spec §3 — mesurées : toile 1024², corps 91,8 %, crâne y 38–40, sol y 978–980, centrage −20 à +10 px à normaliser |
| 4. simplification anatomique | spec §4 |
| 5. reconstruction vectorielle (fidèle / simplifié / normalisé, articulation) | spec §5 — masses identifiées par les **11 codes de zone** du BodyMap |
| 6. note de roadmap aval | spec §6 ; backbone §8.4, ligne `DA-05.0` |

## 3. Changements

| Fichier | Changement |
|---|---|
| `docs/strategy/AUREN_CANONICAL_MANNEQUIN_V1_SPEC.md` | la spécification |
| `design/auren/source/mannequin/auren_mannequin_v1_source.yaml`, `README.md` | registre (5 vues, sha256, orientation, cadrage mesuré, statuts) |
| `design/auren/AUREN_ASSET_PROVENANCE.md` | entrée de provenance (IA, référence seulement) |
| `docs/strategy/AUREN_VISUAL_BACKBONE.md` §8.4 | ligne `DA-05.0` |
| `docs/strategy/SPEC_REGISTRY.md` | ligne de la tranche |
| `tests/test_auren_mannequin_v1.py` | garde neuve (8 tests) |
| `tests/test_auren_asset_governance.py` | registre ajouté à la liste des fichiers structurés permis |

## 4. Vérification

- `check_scope` : `ISOLATED` ; 138 tests ciblés verts (dont 8 neufs) ; protocole de spec et ruff OK.
- Les cinq vues du paquet canonique de l'opérateur ont été recopiées sous leurs noms canoniques ; chaque sha256
  correspond au registre.

## Annexe de clôture (2026-10-29)

- Gate vérifié avant fusion : tête `51ffd4a` (la déclaration de droits de l'opérateur ajoutée), 10 checks verts —
  Gitar, bot non requis, n'a pas reposté —, Sonar PR `OK`, 0 fil ouvert, `CLEAN`.
- PR #324 fusionnée en `--merge --match-head-commit` : **`12fbdfa`** ; CI canonique `40936833333` **verte**.

**Verdict :** pack de cinq vues accepté comme **référence visuelle canonique** du mannequin V1 ; spécification de
production écrite ; reconstruction vectorielle requise avant toute intégration ; décision `§8.2` respectée.
