# Sb_DA_03_3B_APP_ICON_MONO — l'icône de l'app en une encre

**Statut** : 🟡 PR ouverte — tier `isolated` · **Branche** : `sb/da-03-3b-app-icon-mono`
**Base** : canonique `8b453b1` · **Commande** : révision opérateur de DA-03.3 (2026-10-28)
**Gate visuel** : planche DA-03.3 (rendus Icon Composer), puis planche de comparaison I1 / I2 ; **« le défaut proposé en monochrome »**
**Autorité** : `AUREN_VISUAL_CONTRACT.md` §18 (`AUREN-MARK-V1`) et §19 (`AUREN-APP-ICON-V1`, révisé)

---

## 1. Brainstorming · Options · Risques · Choix retenu (`CLAUDE.md §3`)

L'opérateur, avant de partager le compte rendu final du chemin critique : « je préfère la version où c'est
du contraste, où il n'y a pas la couleur en gros orange-bleuâtre », puis : « le sombre trop sombre, le clair
trop clair : un monochrome équilibré », et enfin, devant la planche I1 / I2 : « ouais parfait […] le défaut
proposé en monochrome ».

| Question | Options | Choix | Qui |
|---|---|---|---|
| Quelle icône | I2 (deux couleurs, verrouillée la veille) · **I1** (une encre, `ink` sur `field`) · M1–M5 (fonds et encres intermédiaires pris dans les gris de la palette) | **I1, apparence par défaut** | opérateur |
| Pourquoi pas un gris intermédiaire (M1–M5) | rendus, non publiés : l'opérateur a tranché avant | écartés ; constat utile : en apparence sombre, iOS remplace le fond et garde l'encre, donc une **marque foncée** (M4, M5) y disparaît | opérateur ; mesure de l'agent |
| Identifiant | `AUREN-APP-ICON-V2` · **garder `-V1` et dire la révision** | **`-V1`, révisée** : comme R4 sur `CALIBRATION-LINE-V1`, l'identité de l'élément ne change pas, son rendu oui ; le manifeste porte `supersedes` | agent |
| Document | deux groupes en `ink` · **un groupe `mark`** | **un groupe** : exactement le document I1 que la planche a rendu, donc des baselines identiques à l'octet à ce que l'opérateur a vu | agent |
| Le reste de la marque | laisser les replis en deux couleurs · **tout en une encre** | **une encre partout** (Android, Expo, PWA, apple-touch, favicon) : le logo ne change pas de couleur d'une surface à l'autre | agent, sur la décision de l'opérateur |
| `signal` / `system` | retirés de partout · **retirés de la marque seulement** | **la marque seulement** : dans l'instrument, ils disent la décision et la prescription (`SEMANTIC-TOKENS-V1`) | agent |

| Risque | Parade |
|---|---|
| Les baselines ne sont pas l'icône choisie | les 10 rendus sont **identiques à l'octet** aux rendus I1 de la planche DA-03.3 (`compare_board.py`, rendu par la fonction `render()` du gate lui-même) |
| L'orange et le bleu reviennent par un repli ou un SVG | gardes neuves : `test_the_icon_carries_no_signal_or_system`, `test_the_brand_svgs_are_one_ink` |
| Le gate ne mord pas | mutation plantée (repère repassé en `system`) : garde CI rouge (2 tests) **et** gate macOS 0 / 10 ; rétabli : 10 / 10 |
| La retouche d'un script fait passer la tranche pour du `ci_infra` | la seule retouche de `scripts/check_app_icon.py` était une docstring inutile : retirée ; `check_scope` rend `ISOLATED` |

## 2. Pré-vol

| # | Point | Valeur |
|---|---|---|
| 1 | baselines qui font foi | les 46 du contrat de l'app (inchangées) ; les 10 de l'icône, réapprouvées |
| 2 | fichiers LOCKED impliqués | `AUREN-APP-ICON-V1` (révision décidée par l'opérateur) ; `AUREN-MARK-V1` lu, jamais modifié |
| 3 | invariants | géométrie de la marque, 54 %, +16 px, matière retenue, effets côté système |
| 4 | delta permis | l'encre de l'icône et des fichiers de marque |
| 5 | fichiers prévus | §4 |

## Croquis validé

```
  ┌───────────────────────┐
  │                       │   couche 0 : field
  │        ██ ██          │   couche 1 : la marque, ink — curseur au-dessus…
  │        █████          │
  │                       │   l'écart : la géométrie seule les sépare
  │        ██ ██          │   …du repère, même encre, même couche
  │        █████          │
  │                       │   marque à 54 % de la hauteur, +16 px
  └───────────────────────┘   masque, verre, apparences : le système
```

## Inventaire — une information, une seule fois

| Élément | Information | Source (contrat de données) | Doublon ? |
|---|---|---|---|
| icône | l'app AUREN | — (le nom est dit par le système) | non |
| la marque (une encre) | le fabricant : la décision au-dessus de la prescription | `AUREN-MARK-V1` | non |

## Comparaison avec la référence validée

| Référence validée | Tranche / date | Ce qui doit survivre | Survit ? |
|---|---|---|---|
| I1 de la planche DA-03.3 | choisie le 2026-10-28 | tout | **oui** : 10 rendus identiques à l'octet |
| `AUREN-MARK-V1` | DA-03.2 | la géométrie, la règle de taille | **oui** : chemins calculés depuis `mark-primary` (garde) ; favicon en `mark-compact` |
| baselines du contrat de l'app | DA-02 → DA-03.2 | tout | **oui** : aucun fichier source de l'app touché |

## Changement unique de l'itération

- Changement : **l'icône et la marque web passent en une encre** (`ink` sur `field`).
- Rien d'autre : géométrie, échelle, centrage, matière et écrans inchangés.

## 3. Relecture du relevé de décisions (`CLAUDE.md §5.2`)

| Décision | Verdict |
|---|---|
| « sans la couleur orange-bleuâtre » | **respectée** : aucune trace de `signal` / `system` dans l'icône ni dans les SVG de marque (gardes) |
| « le défaut proposé en monochrome » | **respectée** : I1, apparence par défaut, identique à l'octet à la planche |
| ne pas redessiner la marque ni ses proportions (DA-03.2) | **respectée** |
| 54 %, pas d'étirement, +16 px (DA-03.3) | **respectée** |
| effets côté système, rien d'inscrit dans les SVG | **respectée** |
| matière retenue (ombre neutre 0,35, sans translucidité) | **respectée** |
| baselines : 7 apparences + 60 / 40 / 29 pt | **respectée** (10, réapprouvées) |
| baselines de la marque et du contrat inchangées | **respectée** |
| haltère : ne pas revenir | **respectée** (garde inchangée) |
| ne pas supprimer l'historique | **respectée** : I2 consigné dans la provenance, fichiers dans l'historique git (PR #312) |
| `CLAUDE.md §5.3` — jamais une soustraction seule | **respectée** : la couleur part avec ce qui la remplace (I1 complet, partout) |
| `CLAUDE.md §5.4` — couleur = token | **respectée** : `field`, `ink` |

## 4. Réalisation

| Fichier | Rôle |
|---|---|
| `clients/mobile/assets/AurenAppIcon.icon/` | un groupe `mark`, `Assets/mark.svg` (deux pièces en `ink`) ; `cursor.svg` / `marker.svg` retirés |
| `clients/mobile/visual-contract/app-icon/baselines/` | 10 baselines réapprouvées + manifeste (`approved_by`, `supersedes`) |
| `clients/mobile/assets/{icon,favicon,android-icon-foreground}.png` | replis plats en une encre (fond et monochrome Android inchangés) |
| `app/static/icons/{icon-192,icon-512,icon-maskable-512,apple-touch-icon}.png`, `favicon.svg` | la marque web en une encre |
| `tests/test_auren_app_icon_v1.py` | composition I1, un groupe, garde anti-retour `signal` / `system` |
| `tests/test_auren_pwa_assets.py` | favicon en `ink`, garde « une encre » sur les SVG de marque |
| `design/auren/*` | manifeste (§5quinquies, 1.1.0), provenance (révision, I2 conservé), README |
| `docs/strategy/AUREN_VISUAL_CONTRACT.md` | registre, §18 (couleur), §19 (révisé) |
| `docs/strategy/AUREN_VISUAL_BACKBONE.md`, `SPEC_REGISTRY.md` | ligne `DA-03.3b` |

## 5. Post-vol

| # | Point | Résultat |
|---|---|---|
| 1 | fichiers modifiés | §4 |
| 2 | tests | gardes icône, assets, marque, PWA, têtes, coque web, chaînes publiques : **222 / 222** ; protocole d'itération UI **6 / 6** |
| 3 | régression visuelle | icône **10 / 10** (`check_app_icon.py`) ; contrat de l'app : aucun fichier source touché, la CI le rejoue |
| 4 | mutation | repère en `system` → garde CI rouge (2) et gate 0 / 10 ; rétabli → 10 / 10 |
| 5 | replis plats | décodés : exactement `#0A0B0D` + `#F5F3EE` aux échelles entières (icône Expo, PWA 512) ; ailleurs, seulement des gris d'anticrénelage entre les deux |
| 6 | non vérifié | l'icône sur l'iPhone : nouveau build natif après le merge |

## 6. Incidents

- `check_scope` a d'abord classé la tranche `ci_infra` à cause d'une retouche de docstring dans `scripts/check_app_icon.py` ; la retouche n'apportait rien, elle a été retirée plutôt que de lancer un sweep complet pour un commentaire.
- La garde `test_ui_iteration_protocol` a refusé l'en-tête abrégé de la table d'inventaire ; rétabli mot pour mot.

**Verdict :** `AUREN-APP-ICON-V1` est en une encre, comme l'opérateur l'a choisi, sur iOS, Android et web. La géométrie est intacte, et le retour de l'orange et du bleu sur la marque est désormais gardé.
