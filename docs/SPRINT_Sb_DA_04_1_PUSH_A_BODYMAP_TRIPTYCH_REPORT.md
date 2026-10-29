# Sb_DA_04_1_PUSH_A_BODYMAP_TRIPTYCH — trois caméras sur le même master

**Date :** 2026-10-28 → 2026-10-29
**Branche :** `sb/da-04-1-push-a-triptych` (base canonique `965e9b5`)
**Prérequis :** DA-04.0b fusionnée (PR #317) — master autorisé en builds internes avec contraintes.
**Verdict :** voir la fin du rapport.

## 0. Commande et décisions de l'opérateur

- Brief DA-04.1 (2026-10-28) : trois vues `push-pecs`, `push-delt-lat`, `push-triceps` dérivées du même master ;
  caméras seulement ; une zone dominante, contexte très réduit ; Frame C / Recessed Window ; T1 et T2 proposés,
  l'opérateur choisit ; attribution accessible ; galerie isolée ; aucun montage en carte de séance.
- Décision (2026-10-29) : **« ACCEPT T1 — THREE EQUAL WINDOWS »** ; **« Do NOT extend `signal` to anatomical
  localisation […] Use `system` for the foreground BodyMap zone »** ; cible 35–50 % ramenée à une préférence,
  **« Orientation takes precedence over active-zone percentage »**, les trois caméras mesurées acceptées ; dette
  `ANATOMY-V2` à consigner ; créer `PUSH-A-BODYMAP-TRIPTYCH-V1` avec cinq baselines.
- Gate final sur les rendus T1 en `system` : **« oui go »**.

## 1. Brainstorming · Options · Risques · Choix retenu (`CLAUDE.md §3`)

**Comment porter le master dans React Native**

| Option | Pour | Contre |
|---|---|---|
| A — importer le SVG via un transformeur Metro | aucun fichier généré | nouvelle dépendance de build ; aucune garde de parité possible côté CI Python |
| B — module TypeScript **généré** depuis le master, `d` copiés tels quels | aucune dépendance ; parité vérifiable au caractère près en CI | un fichier de 60 Ko de données |
| C — redessiner des zones simplifiées pour le mobile | léger | interdit : seconde anatomie |

**Choix : B**, avec la garde `tests/test_auren_bodymap_runtime.py` (le module = le master, sha256 nommé, mutations
rejouées).

**Comment cadrer** : une **boîte à garder visible** par préréglage, élargie au format de chaque fenêtre (jamais
coupée), dans sa moitié du master. Un préréglage vaut ainsi pour toutes les tailles de fenêtre.

**Deux côtés ou un ?** Mesuré : un cadrage d'un seul côté ne fait pas mieux pour le deltoïde (17 % contre 21 %),
et le torse symétrique oriente l'œil. **Deux côtés** pour les trois caméras.

**Deltoïde latéral de face ou de dos ?** De dos, le `delt_post` du master recouvre presque exactement le
`delt_lat` (boîtes 157–171 / 158–171). **De face.**

**Risques** : géométrie source grossière en grand (→ T1 retenu, dette consignée) ; confusion de sens de couleur
(→ `system`, décision de l'opérateur) ; atteinte au runtime web (→ garde) ; baselines existantes modifiées
(→ vérifié : 46 inchangées).

## 2. Pré-vol

| # | Point | Valeur |
|---|---|---|
| 1 | baselines qui font foi | les 46 du contrat (inchangées) |
| 2 | fichiers LOCKED impliqués | `FRAME-C-V1`, `RECESSED-WINDOW-V1`, `SEMANTIC-TOKENS-V1`, `INSTRUMENT-CONTROLS-B3` lus, jamais modifiés ; `WindowContentSpec` reçoit un cas **ajouté** (`bodymap-view`), les cas existants rendent à l'identique |
| 3 | invariants | master intouché ; aucune revendication d'activation ; attribution centrale |
| 4 | delta permis | nouveau dossier `clients/mobile/src/ui/bodymap/`, section Licences, nouvelles fixtures |
| 5 | fichiers prévus | §4 |

## Croquis validé

```
 ┌ Frame C ─────────────────────────────────────────────┐
 │ ┌ fenêtre ─────┐ ┌ fenêtre ─────┐ ┌ fenêtre ─────┐   │
 │ │ PECTORAUX    │ │ DELTOÏDES    │ │ TRICEPS      │   │   libellé : interface, eyebrow
 │ │   (face)     │ │ LATÉRAUX     │ │   (dos)      │   │
 │ │  ▓▓▓  ▓▓▓    │ │  ▓      ▓    │ │ ▓        ▓   │   ▓ zone : system, plein
 │ │  silhouette  │ │  silhouette  │ │  silhouette  │   │   silhouette ink3 0,16, zones voisines en filet
 │ └──────────────┘ └──────────────┘ └──────────────┘   │
 └▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄┘   rail de Frame C
```

## Inventaire — une information, une seule fois

| Élément | Information | Source (contrat de données) | Doublon ? |
|---|---|---|---|
| zone en `system` | où se situe la famille musculaire mise en avant | `MASTER_ZONES` + préréglage | non |
| libellé de fenêtre | le nom de la zone (la couleur ne nomme pas) | `label_fr` du contrat de mapping | non : le dessin dit **où**, le mot dit **quoi** |
| silhouette + filets | l'orientation (face / dos, torse) | `MASTER_BASE` | non |
| section Licences | sources, licence, mention non médicale | `auren_bodymap_source.yaml` | non : une seule fois, hors des fenêtres |

## Comparaison avec la référence validée

| Référence validée | Tranche / date | Ce qui doit survivre | Survit ? |
|---|---|---|---|
| master BodyMap | Sb_ASSET_03.2 / DA-04.0b | chaque chemin | **oui** : module identique au caractère près (garde CI) |
| `FRAME-C-V1`, `RECESSED-WINDOW-V1` | DA-02.3 / DA-02.5 | structure, écarts 2u | **oui** : composés, jamais modifiés ; 46 baselines inchangées |
| `SEMANTIC-TOKENS-V1` | DA-02.2 | `signal` = action de l'opérateur | **oui** : l'anatomie est en `system` ; le seul ambre de la vue en contexte est le curseur |
| planche finale DA-04.1 | 2026-10-29 | les cinq rendus | **oui** : baselines identiques à l'octet aux captures 1× revues |

## Changement unique de l'itération

- Changement : **le BodyMap entre dans l'app mobile sous forme de trois caméras T1**, zone en `system`, avec sa
  section Licences.
- Rien d'autre : la vraie carte de séance n'est pas touchée ; aucun écran produit ne monte le triptyque.

## 3. Relecture du relevé de décisions (`CLAUDE.md §5.2`)

| Décision | Verdict |
|---|---|
| « Use the existing canonical master only » / ne pas redessiner, simplifier, régénérer | **respectée** (garde de parité, mutations rejouées) |
| aucune revendication d'activation, d'intensité, de pourcentage, de récupération | **respectée** : aucun chiffre affiché, libellé d'accessibilité « zone mise en avant » |
| une vue par zone ; PECS face ; TRICEPS dos ; DELT LAT une seule vue | **respectée** (face, justifiée par le recouvrement du master) |
| caméras seulement (viewBox) | **respectée** ; seul l'ordre de peinture de la zone mise en avant change |
| 35–50 % préféré, l'orientation prime | **respectée** : pectoraux 49–58 %, deltoïdes 15–21 %, triceps 17–22 % — acceptés |
| contexte très réduit, pas d'aplats sombres | **respectée** : silhouette 0,16, zones voisines en filet |
| Frame C / Recessed Window, pas de carte arrondie, pas d'ombre, pas de dégradé | **respectée** |
| T1 retenu, T2 non retenu | **respectée** : T2 retiré du code, consigné ici |
| zone mise en avant en `system`, jamais `signal` | **respectée** |
| attribution accessible, centrale, sources marquées adaptées, mention non médicale | **respectée** (section Licences, texte du registre, garde) |
| libellés = texte d'interface, jamais dans le SVG | **respectée** |
| aucun montage dans la carte de séance | **respectée** (rendu « en contexte » = composition de banc) |
| ne pas modifier les baselines verrouillées | **respectée** : 46 / 46 identiques |
| `CLAUDE.md §5.3` — jamais une soustraction seule | **non concernée** (ajout) |
| `CLAUDE.md §5.4` — couleur = token | **respectée** : `system`, `ink3`, `field` ; contrastes mesurés (§20 du contrat) |

## 4. Réalisation

| Fichier | Rôle |
|---|---|
| `clients/mobile/src/ui/bodymap/masterGeometry.ts` | le master transcrit, **généré**, 28 chemins, sha256 nommé |
| `clients/mobile/src/ui/bodymap/viewPresets.ts` | `BodyMapViewPreset`, les trois préréglages, `cameraFor` |
| `clients/mobile/src/ui/bodymap/BodyMapView.tsx` | une caméra : silhouette, filets, zone en `system` ; image accessible |
| `clients/mobile/src/ui/bodymap/triptychLayout.ts`, `BodyMapTriptych.tsx` | T1 dans Frame C |
| `clients/mobile/src/ui/bodymap/attribution.tsx`, `LabSheet.tsx` | section Licences |
| `clients/mobile/src/ui/instrument/RecessedWindowFixture.tsx` | cas de contenu `bodymap-view` (ajout) |
| `clients/mobile/src/ui/contract/fixtures.ts`, `ContractFixture.tsx`, `candidates.ts` | cinq fixtures `PUSH-A-BODYMAP-TRIPTYCH-V1` ; candidats vidés |
| `clients/mobile/visual-contract/baselines/` + `manifest.json` | cinq baselines, approbation citée |
| `clients/mobile/visual-contract/review.spec.ts` | un libellé coupé fait échouer une capture de revue |
| `docs/strategy/AUREN_VISUAL_CONTRACT.md` | registre, sens de `system` précisé, §20 |
| `design/auren/source/bodymap/auren_bodymap_source.yaml`, `README.md` | surface d'attribution livrée |
| `tests/test_auren_bodymap_runtime.py` | garde neuve (9 tests) |
| `tests/test_auren_bodymap_master.py`, `tests/test_visual_contract_governance.py` | statut d'attribution ; identifiant LOCKED |

## 5. Post-vol

- Baselines : 46 existantes **inchangées** (`git status` : seuls 5 PNG ajoutés) ; 5 nouvelles **identiques à
  l'octet** aux captures revues (`85fe1848…`, `27fecd6e…`, `c7eb688e…`, `d024b555…`, `bf05df27…`).
- Contrastes sur `field` : zone / silhouette 8,99 : 1 ; filet 2,1 : 1 ; silhouette 1,22 : 1.
- `viewPresets.test.ts` 6 / 6 ; `tsc` propre sur `src/` (seul `@playwright/test`, absent de l'environnement local
  emprunté, manque aux fichiers du gate — préexistant).

## 6. Dette `ANATOMY-V2` (master intouché)

- **pecs** : petites crêtes au bord supérieur en fort agrandissement ; aucun blocage pour T1.
- **delt_lat** : se lit d'abord comme « épaule » ; accepté pour la localisation fonctionnelle.
- **triceps** : encoche / dédoublement en haut, visible à la taille de la carte ; candidat V2.
- **lats / core** (contexte, Servier) : contours dentelés dans la caméra de dos ; atténuables par le traitement de
  contexte, non redessinés.

## 7. Incidents

- Une garde neuve accusait `app/services/muscle_mapping.py` : un commentaire y cite le nom d'un test. Resserrée sur
  ce qui charge réellement le master (le fichier `.svg`, le module généré).
- Docker recrée un dossier `node_modules` vide après chaque passage : un lien posé ensuite atterrit **dedans**.
  Retiré et reposé au bon endroit (piège déjà connu).

## Annexe de clôture (2026-10-29)

- Gate vérifié juste avant fusion : tête `93879d1`, 11 / 11 checks verts (dont le contrat visuel : 51 baselines
  identiques au pixel en CI), Sonar PR `OK` (0 sur toutes les conditions), 0 fil ouvert, `CLEAN`.
- PR #319 fusionnée en `--merge --match-head-commit` (GO MERGE permanent, tranche commandée) : **`13cfefa`**.
- **CI canonique** sur le push : run `40871507944`, **verte**.
- Suite ouverte dans la foulée : DA-04.2 (les 11 zones, un panneau par séance), en revue chez l'opérateur, non
  commitée. Constat à trancher : le modèle de lecture mobile classe encore les zones par l'ancien classifieur.

**Verdict :** `PUSH-A-BODYMAP-TRIPTYCH-V1` **LOCKED** — T1, zone en `system`, cinq baselines approuvées par
l'opérateur, master intouché, attribution livrée ; aucun écran produit ne le monte encore.
