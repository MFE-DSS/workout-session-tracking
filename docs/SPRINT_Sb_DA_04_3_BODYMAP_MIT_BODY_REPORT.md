# Sb_DA_04_3_BODYMAP_MIT_BODY — le BodyMap dessine le corps MIT

**Date :** 2026-10-31
**Branche :** `sb/da-04-3-bodymap-mit-body` (base canonique `2bbc7c5`, après DA-05.0)
**Verdict :** voir la fin du rapport.

## 0. Commande et décisions de l'opérateur

- Après les essais côte à côte de ressources sous licence compatible : « pour tous les trucs isolés de muscles,
  c'est bon, là on statique, on va dire que ça c'est ok » ; « restons là-dessus, on va pas s'entêter ».
- Sur la planche avant / après des 18 fenêtres : « ouais go on va se satisfaire de cela pour l'instant ».
- Hors périmètre, rangé pour la suite : le mouvement (« un zoom technico-fonctionnel »), jamais les images RepDB.

## 1. Brainstorming · Options · Risques · Choix retenu (`CLAUDE.md §3`)

| Option | Pour | Contre |
|---|---|---|
| A — garder le master BodyParts3D, attendre `ANATOMY-V2` | traçabilité déjà gouvernée | contours jugés trop grossiers en recadrage (dette §20 / §21) ; aucune échéance |
| B — corps de `react-native-body-highlighter` (MIT), vendorisé tel quel, nos caméras | essai côte à côte retenu par l'opérateur ; licence permissive ; parties nommées par muscle | un seul `deltoids` par vue ; pas de dorsal distinct du haut du dos |
| C — dépendre du paquet npm et de son composant | aucune extraction | code tiers exécuté, rendu imposé (couleurs, interactions), mise à jour qui déplace les baselines |
| D — reconstruction vectorielle à partir du mannequin Midjourney | identité AUREN | rejetée par l'opérateur (asymétries, ancien modèle musculaire plaqué) |

**Choix : B.** Les données seules (chaînes `slug` et `d`, lues comme texte, jamais exécutées) sont vendorisées avec
la `LICENSE` ; le module de l'app en est généré ; notre composant, nos caméras et notre traitement restent.

**Risques** : un chemin altéré à la main (→ garde au caractère près, tarball nommé par sha256) ; le crédit perdu
(→ garde LICENSE + crédit dans l'app) ; une zone sans partie (→ garde onze zones, chaque partie présente sur son
côté) ; une caméra qui sort de sa moitié (→ test `viewPresets`) ; la dette du master reportée à tort sur ce corps
(→ contrat §22 distingue).

## 2. Pré-vol

| # | Point | Valeur |
|---|---|---|
| 1 | baselines qui font foi | les 65 du contrat, dont les 18 BodyMap de §20 / §21 |
| 2 | fichiers LOCKED impliqués | `PUSH-A-BODYMAP-TRIPTYCH-V1`, `BODYMAP-ZONES-V1` : ids, libellés, règle de caméra, grille gardés |
| 3 | invariants | zone en `system` ; aucune revendication ; rien dans le runtime web ; Licences dans l'app |
| 4 | delta permis | la géométrie, les boîtes de caméra, le traitement du corps silencieux, le crédit |
| 5 | fichiers prévus | §4 |

## Croquis validé

```
 body.json (MIT, texte)  ──génère──▶  bodyGeometry.ts  ──▶  BodyMapView
  front: chest, deltoids…            BODY_PARTS          zone  → system plein, peinte en dernier
  back:  trapezius, gluteal…         ZONE_SLUGS (11)     reste → ink3 à 0,22, un seul ton
                                     PRESET_FRAMES       caméra → cameraFor (inchangée)
```

## Inventaire — une information, une seule fois

| Élément | Information | Source (contrat de données) | Doublon ? |
|---|---|---|---|
| zone en `system` | où se situe la zone | `ZONE_SLUGS[zone][side]` | non |
| corps silencieux | l'orientation | toutes les autres parties, un seul ton | non : aucune autre zone n'est nommée ni colorée |
| libellé de fenêtre | le nom de la zone | `label_fr` du contrat de mapping | non : le dessin dit **où**, le mot dit **quoi** |
| crédit | la source et sa licence | `BODY_SOURCE`, une fois, feuille Journal | non : jamais dans les fenêtres |

## Comparaison avec la référence validée

| Référence validée | Tranche / date | Ce qui doit survivre | Survit ? |
|---|---|---|---|
| `PUSH-A-BODYMAP-TRIPTYCH-V1` | DA-04.1 / 2026-10-29 | T1, trois caméras, `system`, Licences | **oui**, géométrie remplacée par décision (§22) |
| `BODYMAP-ZONES-V1` | DA-04.2 / 2026-10-29 | une caméra par zone, panneaux dérivés, grille | **oui** : mêmes ids, mêmes formes de grille |
| spec de cadrage (focus) | 2026-10-31 | centre sur la zone, hauteurs validées | **oui** : `PRESET_FRAMES` en est calculé |
| 47 autres baselines | DA-02 → DA-03 | tout | **oui**, identiques au pixel |

## Changement unique de l'itération

- Changement : **le corps dessiné par le BodyMap.**
- Rien d'autre : aucun écran produit ne monte le BodyMap ; le master BodyParts3D, son registre et ses gardes sont
  intouchés ; le serveur n'est pas touché.

## 3. Relecture du relevé de décisions (`CLAUDE.md §5.2`)

| Décision | Verdict |
|---|---|
| zones isolées statiques sur ce corps (opérateur, 2026-10-31) | **respectée** |
| §20 — zone en `system`, jamais `signal` | **respectée** |
| §20 — orientation avant pourcentage ; jamais serrer une caméra pour un chiffre | **respectée** : hauteurs de la spec de cadrage |
| §20 — « un seul master, redessiner aucun chemin » | **remplacée par §22** sur décision : un seul corps (MIT), aucun chemin retouché |
| §20 — Licences dans l'app qui porte le BodyMap | **respectée** : crédit MIT, mention non médicale gardée |
| §21 — une caméra par zone, panneau dérivé, trois par ligne au plus | **respectée** |
| `CLAUDE.md §5.3` — jamais une soustraction seule | **respectée** : `masterGeometry.ts` retiré dans la même livraison que son remplaçant |
| `CLAUDE.md §5.4` — couleur = token | **respectée** (`system`, `ink3`, `field` ; contrastes mesurés au §22) |
| backbone §8.2 — l'IA n'est jamais source finale de l'anatomie | **respectée** : aucune géométrie générée |

## 4. Réalisation

| Fichier | Rôle |
|---|---|
| `clients/mobile/vendor/react-native-body-highlighter/LICENSE`, `body.json` | licence MIT verbatim ; données du corps et leur provenance (sha256 du tarball et des assets) |
| `clients/mobile/src/ui/bodymap/bodyGeometry.ts` | généré : `BODY_SOURCE`, `BODY_PARTS`, `ZONE_SLUGS`, `PRESET_FRAMES` |
| `clients/mobile/src/ui/bodymap/viewPresets.ts` | mêmes caméras sur les nouvelles boîtes, nouveau canevas |
| `clients/mobile/src/ui/bodymap/BodyMapView.tsx` | traitement : zone `system`, reste `ink3` à 0,22 |
| `clients/mobile/src/ui/bodymap/attribution.tsx` | crédit MIT lu de `BODY_SOURCE` |
| `clients/mobile/src/ui/bodymap/masterGeometry.ts` | retiré (remplacé) |
| `clients/mobile/visual-contract/baselines/` + `manifest.json` | 18 baselines, approbation citée |
| `docs/strategy/AUREN_VISUAL_CONTRACT.md` | registre, renvoi en §20, §22 |
| `design/auren/AUREN_ASSET_PROVENANCE.md` | entrée corps MIT ; note sur le master |
| `tests/test_auren_bodymap_runtime.py` | réécrit pour le corps MIT, avec deux mutations |
| `clients/mobile/src/ui/bodymap/viewPresets.test.ts` | chaque caméra contient sa zone, reste dans sa moitié |

## 5. Post-vol

- 47 baselines inchangées au pixel ; 18 refaites, identiques à l'octet aux rendus de la planche revue.
- Contrastes sur `field` : zone / corps 8,10 : 1 ; zone / fond 10,99 : 1 ; corps / fond 1,36 : 1.

## 6. Suite proposée (hors tranche)

Le mouvement : un zoom biomécanique de la zone (fibres qui se raccourcissent et s'allongent, angle articulaire),
sans revendication de blessure — proposition séparée à l'opérateur.

**Verdict :** `BODYMAP-MIT-BODY-V1` **LOCKED** — le BodyMap dessine le corps MIT, crédité, chemins intouchés ;
18 baselines approuvées par l'opérateur ; aucun écran produit ne le monte encore.
