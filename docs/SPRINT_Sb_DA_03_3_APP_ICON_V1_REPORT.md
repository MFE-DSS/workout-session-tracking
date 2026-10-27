# Sb_DA_03_3_APP_ICON_V1 — l'icône de l'app, verrouillée et intégrée

**Statut** : ✅ MERGÉE (`56773af`, closeout en annexe) — DA-03.3 **CLOSED** — tier `isolated` · **Branche** : `sb/da-03-3-app-icon-v1`
**Base** : canonique `7b32d29` · **Commande** : décision opérateur DA-03.3, « ACCEPT I2 — SEMANTIC » (2026-10-27)
**Gate visuel** : planche DA-03.3 revue par l'opérateur (rendus Icon Composer) ; **« ACCEPT I2 »**
**Autorité** : `AUREN_VISUAL_CONTRACT.md` §18 (`AUREN-MARK-V1`) et §19 (neuf)

---

## 1. Brainstorming · Options · Risques · Choix retenu (`CLAUDE.md §3`)

| Question | Options | Choix | Qui |
|---|---|---|---|
| Quelle icône | I1 Mono · **I2 Semantic** · I3 Instrument | **I2** ; I1 = expression de marque monochrome seulement ; I3 retiré | opérateur |
| Comment l'app la reçoit | PNG figés · **document Icon Composer** | **`.icon`** par `ios.icon` : Expo SDK 58 le copie dans le projet Xcode et règle `ASSETCATALOG_COMPILER_APPICON_NAME` (vérifié dans le code d'Expo, puis par prebuild) | agent |
| Comment verrouiller des pixels que dessine Apple | captures Playwright · **le moteur d'Apple** | **`ictool`**, déterministe (même document → mêmes octets) : tolérance zéro, sur macOS ; la CI (Linux) vérifie le document et les empreintes, jamais des pixels qu'elle ne sait pas produire | agent |
| Où vit le script du gate | à côté des baselines · **`scripts/`** | **`scripts/check_app_icon.py`** : la convention du dépôt y admet les sous-processus des scripts CLI ; à côté des baselines, ruff aurait remonté deux `S603` jusqu'à Sonar | agent |
| Android, web, PWA | rien · **replis plats** | **replis plats** de la même composition, sans verre ; Android à 54 % de la zone **visible** (l'adaptatif n'en montre que les 72/108) | agent |
| Le favicon web (16 px) | l'icône réduite · **la marque à son dessin de 16 px** | **`mark-compact`** : réduite, l'icône mettrait la marque sous 12 px, ce que l'opérateur interdit | agent, règle de l'opérateur |
| L'haltère | tout remplacer · **seulement comme marque** | **comme marque seulement** (favicon, PWA, apple-touch, `auren-mark.svg`) ; aucun pictogramme d'exercice n'existe (inventaire §6) | opérateur |

| Risque | Parade |
|---|---|
| Les baselines ne sont pas l'icône revue | les 10 rendus sont **identiques à l'octet** aux rendus I2 de la planche |
| Le gate ne mord pas | mutation plantée (1 px sur le curseur) : 0 / 10 ; sur le repère : garde CI rouge |
| Le gate « passe » là où il ne peut rien voir | hors macOS / sans Xcode il **refuse** (code 2) |
| Un changement d'`ictool` passe pour un changement d'icône | la version est enregistrée ; une autre version arrête le gate et demande une ré-approbation |
| Un haltère « exercice » remplacé par erreur | inventaire complet `app/` + `clients/mobile/` : aucun pictogramme ; le vocabulaire d'équipement n'est pas touché |

## 2. Pré-vol

| # | Point | Valeur |
|---|---|---|
| 1 | baselines qui font foi | les 46 du contrat (dont 9 `AUREN-MARK-V1`), toutes inchangées ; 10 neuves |
| 2 | fichiers LOCKED impliqués | aucun ; la marque est lue depuis sa source gouvernée |
| 3 | invariants | `AUREN-MARK-V1` ; la composition I2 approuvée (54 %, +16 px, deux groupes, matière retenue) |
| 4 | delta permis | l'icône de l'app et les fichiers de marque web |
| 5 | fichiers prévus | §4 |

## Croquis validé

Validé par l'opérateur sur la planche DA-03.3 (rendus `ictool`), 2026-10-27 :

```
  ┌───────────────────────┐
  │                       │   couche 0 : field
  │        ██ ██          │   couche 2 : curseur, signal (devant)
  │        █████          │
  │                       │   l'écart : la géométrie seule les sépare
  │        ██ ██          │   couche 1 : repère, system
  │        █████          │
  │                       │   marque à 54 % de la hauteur, +16 px
  └───────────────────────┘   masque, verre, apparences : le système
```

## Inventaire — une information, une seule fois

| Élément | Information | Source (contrat de données) | Doublon ? |
|---|---|---|---|
| icône | l'app AUREN | — (le nom est dit par le système sous l'icône) | non |
| curseur (`signal`) | la décision de l'opérateur | sens d'`ACTIVE-CURSOR-V1` | non |
| repère (`system`) | la prescription du système | sens de `REFERENCE-MARKER-V1` | non |

## Comparaison avec la référence validée

| Référence validée | Tranche / date | Ce qui doit survivre | Survit ? |
|---|---|---|---|
| I2 de la planche DA-03.3 | 2026-10-27 | tout | **oui** : document identique, 10 rendus identiques à l'octet |
| `AUREN-MARK-V1` | DA-03.2 | la géométrie, la règle de taille | **oui** : couches calculées depuis `mark-primary` (garde) ; favicon en `mark-compact` |
| toutes les baselines du contrat | DA-02 → DA-03.2 | tout | **oui** : 46 identiques à l'octet |

## Changement unique de l'itération

- Changement : **AUREN a son icône** — sur iOS (Icon Composer), Android et web ; l'haltère n'est plus la marque.
- Rien d'autre : aucun écran n'est modifié.

## 3. Relecture du relevé de décisions (`CLAUDE.md §5.2`)

| Décision | Verdict |
|---|---|
| ne pas redessiner la marque ni ses proportions | **respectée** (garde : couches = `mark-primary` × 24, centrée, +16) |
| 54 %, pas d'étirement, +16 px | **respectée** |
| trois couches : field · repère `system` · curseur `signal` ; rien d'autre | **respectée** (deux groupes, garde) |
| comportement monochrome : deux pièces distinctes par la géométrie | **respectée** (Mono / Tinted baselines) |
| effets côté système, rien d'inscrit dans les SVG | **respectée** (garde : aucun filtre, flou, dégradé, opacité) |
| matière retenue | **respectée** : ombre neutre 0,35, aucune translucidité |
| I1 pas une icône concurrente ; I3 retiré | **respectée** : `auren-mark.svg` = expression monochrome ; aucun I3 |
| baselines : 7 apparences + 60 / 40 / 29 pt | **respectée** (10) |
| baselines de la marque inchangées | **respectée** |
| haltère remplacé comme marque seulement | **respectée** (§6) |
| ne pas supprimer l'historique | **respectée** : géométrie de l'haltère consignée dans la provenance, et interdite de retour |
| `CLAUDE.md §5.4` — couleur = token | **respectée** : `field`, `signal`, `system`, `ink` |

## 4. Réalisation

| Fichier | Rôle |
|---|---|
| `clients/mobile/assets/AurenAppIcon.icon/` | le document Icon Composer (source conservée) |
| `clients/mobile/app.json` | `ios.icon` → le document |
| `clients/mobile/assets/{icon,favicon,android-icon-*}.png` | replis plats (remplacent les gabarits Expo) |
| `app/static/icons/{icon-192,icon-512,icon-maskable-512,apple-touch-icon}.png`, `favicon.svg`, `auren-mark.svg` | la marque web : l'haltère remplacé |
| `scripts/check_app_icon.py` | gate : rendu Apple, zéro pixel, macOS seulement |
| `clients/mobile/visual-contract/app-icon/baselines/` | 10 baselines + manifeste |
| `tests/test_auren_app_icon_v1.py` | garde CI : document, configuration, empreintes |
| `tests/test_auren_pwa_assets.py` | évolution : épingle la marque neuve et interdit le retour de l'haltère |
| `tests/test_auren_asset_governance.py` | docstring : l'icône vit avec son consommateur |
| `design/auren/*` | manifeste (§4.2, §5quinquies), provenance, README |
| `AUREN_VISUAL_CONTRACT.md` | registre, §19 |

## 5. Post-vol

| # | Point | Résultat |
|---|---|---|
| 1 | fichiers modifiés | §4 |
| 2 | tests | gardes icône / assets / contrat **45 / 45** · PWA et têtes web **108 / 108** · coque web **100 / 100** · jest **387 / 387** |
| 3 | régression visuelle | contrat **47 / 47** (46 identiques + fixture inconnue) · icône **10 / 10** (`check_app_icon.py`) |
| 4 | mutations | 1 px sur le curseur → 0 / 10 ; 1 px sur le repère → garde CI rouge |
| 5 | intégration | `expo prebuild` : document copié dans `ios/AURENLab/`, `ASSETCATALOG_COMPILER_APPICON_NAME = AurenAppIcon` (Debug et Release) ; `actool` : `Assets.car`, `CFBundleIconName = AurenAppIcon`, repli `60x60@2x` |
| 6 | non vérifié | l'installation sur l'iPhone : elle demande un nouveau build natif (une mise à jour JS ne change pas une icône) |

## 6. Inventaire des usages de l'haltère

| Où | Rôle | Décision |
|---|---|---|
| `app/static/icons/favicon.svg` | onglet du navigateur (marque) | **remplacé** : la marque à 16 px |
| `app/static/icons/auren-mark.svg` | fichier de marque (aucun gabarit ne le lit) | **remplacé** : expression monochrome |
| `app/static/icons/icon-192.png`, `icon-512.png`, `icon-maskable-512.png` | icônes PWA (manifest) | **remplacés** : `AUREN-APP-ICON-V1` plat |
| `app/static/icons/apple-touch-icon.png` | raccourci web sur iPhone | **remplacé** |
| `clients/mobile/assets/*` | gabarits Expo (« A » bleu, grille) — jamais l'haltère | **remplacés** ; `splash-icon.png` (gabarit non référencé) laissé tel quel |
| « haltère(s) » / `dumbbell` dans `app/` et `clients/mobile/` | noms d'exercices, famille d'équipement, aides de saisie | **non touchés** : du vocabulaire, pas une marque |
| pictogramme d'exercice en forme d'haltère | — | **aucun n'existe** (le glyphe « série de travail » est une barre) |

## 7. Incidents

- `npm exec` lancé hors du dossier de l'app a cherché le projet à la racine du dépôt (et a lu son `.env`, sans rien afficher que des noms de variables) ; relancé par le script `expo` de l'app, dans le bon dossier.
- Le script du gate, d'abord à côté des baselines, aurait porté deux `S603` jusqu'à Sonar ; déplacé dans `scripts/`, où la convention du dépôt couvre les sous-processus.

**Verdict :** `AUREN-APP-ICON-V1` est verrouillée et branchée : iOS par Icon Composer, Android et web par des replis fidèles. L'haltère ne représente plus AUREN, et rien de ce qui voulait dire « exercice » n'a été touché.

---

## Annexe — closeout post-merge

| Élément | Valeur |
|---|---|
| PR | #312, mergée par `--merge --match-head-commit` (head `49bfb61`) sous GO MERGE permanent, après « ACCEPT I2 » |
| Commit de merge | `56773af549b8b8162d2faab8e60cbf061cc29bc7` |
| CI de la PR | 11 checks verts, dont `visual contract (DA-GOV-01)` sur les 46 baselines du contrat |
| CI canonique (push) | run `40490441312` : **8 jobs sur 8 verts** |
| Sonar | gate PR `OK`, **0 issue**, 0 fil de revue non résolu |
| Gate icône (macOS) | `scripts/check_app_icon.py check` : 10 / 10 identiques avant merge ; la CI Linux ne peut pas le jouer, elle vérifie le document et les empreintes |
| Reste à faire | installer l'icône sur l'iPhone : nouveau build natif (`expo prebuild` + build signé) |
| Incidents | aucun dans le périmètre |
| Nettoyage | worktree et branche `sb/da-03-3-app-icon-v1` supprimés |
