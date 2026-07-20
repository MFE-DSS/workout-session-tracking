# AUREN — Icon Semantic Map

**Build** : `Sb_ASSET_02.1` — Vendored Icon Subset & License Intake.
**Subset** : `auren.icons.vendor.tabler.p0` **v0.1.0** · **Tabler Icons v3.45.0** (commit
`975920ff99c12c4dc9e3fe61a03738330600f9b2`) · licence **MIT**.
**État** : intake **source de design uniquement** — **HUMAN REVIEW PENDING** · **NOT AUTHORIZED FOR APP
INTEGRATION**.

> Cartographie sémantique des icônes fonctionnelles Auren. Contrat machine-lisible :
> [`source/icons/auren_icon_subset.yaml`](source/icons/auren_icon_subset.yaml). Le `semantic_id` est stable ;
> le mapping vendor peut changer sans changer le contrat métier.

---

## A. Identité du subset
- **P0** · **v0.1.0** · Tabler outline **v3.45.0** · commit `975920ff…` · **MIT** (© Paweł Kuna 2020-2026).
- Intake **source de design uniquement** ; **human/legal review pending** ; **0** `app/static`.

## B. Quatre navigations conservées (`existing-runtime-keep`)
| Concept | Statut | Note |
|---|---|---|
| Séance | `existing-runtime-keep` | SVG inline `base.html` (Sb_UI_03.1) — **non copié** dans le subset |
| Programmes | `existing-runtime-keep` | idem |
| Progression | `existing-runtime-keep` | idem |
| Profil | `existing-runtime-keep` | idem |

Les 4 nav restent leur SVG inline actuel ; elles **ne sont pas** vendored dans ce build (pas de migration
runtime ici).

## C. Dix fichiers vendored (Tabler v3.45.0 outline)
| semantic_id | label FR | en interne | fichier | catégorie | intent | rôle a11y | texte visible | surfaces | statut | alternatives rejetées |
|---|---|---|---|---|---|---|---|---|---|---|
| `auren.icon.action.substitute` | Substituer | Substitute exercise | `arrows-exchange.svg` | action | remplacer un exercice | decorative | oui (label) | exercise-card, session-console, history-row | `vendor-selected-for-intake` | `switch-horizontal` (moins neutre) |
| `auren.icon.action.timer-start` | Démarrer le repos | Start rest timer | `player-play.svg` | action | lancer le timer | action | icône seule OK (accessible name) | rest-timer, session-console | `vendor-selected-for-intake` | `play` (alias) |
| `auren.icon.action.timer-pause` | Pause repos | Pause rest timer | `player-pause.svg` | action | mettre en pause | action | icône seule OK | rest-timer, session-console | `vendor-selected-for-intake` | — |
| `auren.icon.action.timer-reset` | Réinitialiser repos | Reset rest timer | `rotate.svg` | action | remettre à zéro | action | icône seule OK | rest-timer, session-console | `vendor-selected-for-intake` | `refresh` (charge > sens) |
| `auren.icon.action.expand` | Déplier | Expand | `chevron-down.svg` | action | ouvrir un panneau | decorative | oui | exercise-card, program-card, history-row | `vendor-selected-for-intake` | `plus` (ambigu) |
| `auren.icon.action.collapse` | Replier | Collapse | `chevron-up.svg` | action | fermer un panneau | decorative | oui | exercise-card, program-card, history-row | `vendor-selected-for-intake` | `minus` (ambigu) |
| `auren.icon.information.guidance` | Conseil | Guidance hint | `bulb.svg` | information | afficher un conseil | decorative | oui | exercise-card, session-console | `vendor-selected-for-intake` | `info-circle` (générique) ; remplace `💡` |
| `auren.icon.information.warning` | Avertissement | Warning | `alert-triangle.svg` | information | signaler une alerte | decorative | oui (texte) | form-feedback, session-console, exercise-card | `vendor-selected-for-intake` | `alert-circle` ; remplace `⚠` |
| `auren.icon.status.completed` | Terminé | Completed | `check.svg` | status | marquer validé | decorative | oui (texte) | form-feedback, history-row, session-console | `vendor-selected-for-intake` | `circle-check` (plus lourd) ; remplace `✓` |
| `auren.icon.action.menu` | Menu secondaire | Open secondary menu | `menu-2.svg` | action | ouvrir la nav secondaire | action | icône seule OK (`aria-label`) | secondary-nav | `vendor-selected-for-intake` | `menu` (v1) ; remplace `☰` |

**Surfaces interdites communes** : `bottom-nav`, `desktop-rail`, `body-intelligence` (icône seule bannie ;
nav primaire = label ; Body Intelligence reste textuel).

## D. P1 différé (décisions de la spec, **non copiés**)
Tendances (`trending-up`/`minus`/`trending-down`), `excluded` (`ban`), `substituted history`, `history`,
`program` (`list-details`). **Aucun SVG P1 ingéré** dans ce build.

## E. Typographic-only (restent texte)
`kg` · `reps` · numéro de série · cible · **RIR** · durée exacte · score numérique · pourcentage · noms de
zones · labels **primary/secondary** · **confidence score**.

## F. Rejetés (anti-médicalisation / anti-gamification / anti-IA)
sparkles IA · robot Coach · cerveau · stéthoscope/croix médicale/ECG/seringue/cœur médical · flamme effort ·
éclair performance · trophée progression ordinaire · cible reco · haltère générique · silhouette anatomique
générique · **tout emoji**.

## G. Custom
```
CUSTOM GLYPH TRACK: NOT REQUIRED
```
Aucun gap custom démontré (cf. spec §16). Dossier `source/icons/custom/` **non créé**.

## H. Gate
```
NOT AUTHORIZED FOR APP INTEGRATION
ASSET INTEGRATION GATE: BLOCKED PENDING HUMAN / ANATOMICAL / LEGAL / MOBILE APPROVALS
```
La présence de ces 10 fichiers dans `design/auren/source/icons/` **n'autorise pas** leur écriture dans
`app/static/`. Le remplacement runtime des glyphes/emoji (`✓ ⚠ 💡 ☰`) relève d'un build ultérieur
(`Sb_ASSET_04.1`), après franchissement du gate.
