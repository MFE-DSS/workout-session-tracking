# Sb_DA_GOV_01_VISUAL_CONTRACT — contrat visuel et gate de régression

**Statut** : build — tier `ci_infra` (le pipeline change) · **Branche** : `sb/da-gov-01-visual-contract`
**Base** : canonique `2c12ee8` · **Commande** : brief opérateur `DA-GOV-01 — VISUAL CONTRACT & REGRESSION GATE` (2026-10-25)
**Autorité produite** : `docs/strategy/AUREN_VISUAL_CONTRACT.md`

---

## 1. Brainstorming · Options · Risques · Choix retenu (`CLAUDE.md §3`)

| Question | Options | Choix | Pourquoi |
|---|---|---|---|
| Outil de comparaison | Storybook + service tiers · Jest DOM snapshot · **Playwright `toHaveScreenshot` sur un build web** | **Playwright** | brief : capture d'écran, pas un instantané du DOM ; les bancs web existent déjà ; aucun service externe |
| Où rendre les fixtures | dans les bancs existants (contenu mouvant) · **une page qui rend UNE fixture choisie par URL** (`?fixture=<id>`, `EXPO_PUBLIC_GALLERY=contract`) | **page dédiée** | un banc qui évolue ferait bouger les baselines ; la page de contrat ne change qu'avec le contrat |
| Déterminisme | Chromium de la machine · **image Playwright épinglée par empreinte, la même en local et en CI** | **image épinglée** | les polices macOS et Linux diffèrent : une baseline faite sur Mac rougirait en CI pour une mauvaise raison |
| Écriture des baselines | mise à jour auto. sur échec · **jamais par le gate ; seulement `run.sh approve` + manifeste** | **jamais par le gate** | brief : seul l'opérateur approuve une baseline |
| Où ranger les PNG | `design/auren/` (raster interdit) · **`clients/mobile/visual-contract/baselines/`** | **hors design** | brief §3 ; la garde du design reste intacte |
| Tolérance | ratio de pixels · **0 pixel, bruit de couleur seul toléré** | **0 pixel** | même image, même rendu : un pixel qui bouge est un changement visuel |

| Risque | Parade |
|---|---|
| Une baseline modifiée en silence | manifeste avec sha256 et approbation ; `test_visual_contract_governance.py` rougit (mutation prouvée) |
| Un gate qui ne mord pas | mutation volontaire : ligne de base du rail 2 → 3 px, **4 fixtures sur 4 rouges** |
| Une dérive local / CI | même image épinglée par empreinte des deux côtés ; la garde vérifie l'égalité des chaînes |
| Playwright qui fuit en production | dépendance **dev** seulement, version exacte = celle de l'image ; vérifié par la garde |

## 2. Réalisation

| Fichier | Rôle |
|---|---|
| `docs/strategy/AUREN_VISUAL_CONTRACT.md` | statuts LOCKED / CONSTRAINED / EXPLORATION ; fiche complète de `CALIBRATION-LINE-V1` ; fiches courtes des 4 autres LOCKED ; protocole de test ; décisions de l'opérateur sur DA-02.4 ; chemin critique |
| `docs/templates/VISUAL_SPRINT_TEMPLATE.md` | AUTHORITY · CHANGE ALLOWED / FORBIDDEN · TARGET DELTA · FIXTURES · STOP CONDITIONS ; pré-vol et post-vol |
| `clients/mobile/src/ui/contract/fixtures.ts`, `ContractFixture.tsx`, `index.ts` | les 4 fixtures (données du banc DA-02.2, mot pour mot) ; une page qui rend une seule fixture |
| `clients/mobile/visual-contract/` | `playwright.config.ts`, `visual.spec.ts`, `serve.mjs` (serveur statique sans dépendance), `run.sh` (`test` / `approve`), `baselines/*.png` + `manifest.json`, `README.md` |
| `.github/workflows/ci.yml` | job `visual-contract` dans l'image épinglée ; captures et diffs publiées en artefact si échec |
| `clients/mobile/package.json` / lock | `@playwright/test` 1.63.0, **devDependency** exacte (+46 lignes de lock) |
| `tests/test_visual_contract_governance.py` | 10 gardes : manifeste ↔ fichiers ↔ sha256, approbation, fixtures = baselines, n'écrit jamais, même image, dépendance dev-only, job CI présent, contrat complet, aucun raster sous `design/auren` |

## Croquis validé

Source : brief de l'opérateur, cité. Aucune composition d'écran n'est créée ni modifiée : la seule surface nouvelle est la
page technique des fixtures, qui rend le rail **tel qu'approuvé en DA-02.2**, sans rien autour.

```
┌─ page de contrat (?fixture=calibration-line-390-push) ─┐
│  [ CalibrationRail DA-02.2, 390 px, données du banc ]  │
└─────────────────────────────────────────────────────────┘
```

## Inventaire — une information, une seule fois

| Élément | Information | Source (contrat de données) | Doublon ? |
|---|---|---|---|
| rail en ligne (fixture) | le composant gouverné, tel qu'approuvé | `CONTRACT_FIXTURES` (données du banc DA-02.2) | non |
| page « Fixture inconnue » | un identifiant de fixture absent, dit, jamais rendu vide | paramètre `fixture` de l'URL | non |

## Comparaison avec la référence validée

| Référence validée | Tranche / date | Ce qui doit survivre | Survit ? |
|---|---|---|---|
| rail en ligne pleine largeur | DA-02.2 (PR #286), 2026-10-25 | ligne horizontale, bande de zones, curseur dessus / repère dessous, géométrie des marqueurs | oui : les baselines **sont** ce rendu ; `git diff` vide sur `src/ui/calibration/` |

## Changement unique de l'itération

- Demande : « This sprint adds visual governance only. Do NOT redesign any product component. »
- Changement : ajout du contrat, des baselines DA-02.2 et du gate. Aucun composant produit modifié.
- Avant / après : sans objet pour l'interface. Les 4 baselines sont jointes au rapport opérateur.

## 3. Vérifications

| Porte | Résultat |
|---|---|
| `check_scope` | **CI_INFRA** |
| Gate visuel, local (image épinglée) | **5/5 verts**, deux fois de suite, rendu identique au pixel |
| Mutation du gate | ligne de base 2 → 3 px : **4/4 fixtures rouges** (16 à 32 pixels), puis retour exact (`git diff` vide) |
| Mutation de la gouvernance | un octet ajouté à une baseline : `test_every_baseline_png_is_in_the_manifest_with_its_exact_hash` **rouge**, fichier restauré |
| Client (dans l'image) | `tsc` propre · **274 tests jest** |
| Gardes Python liées | 288 verts (CI, scope, lock, gouvernance d'assets, protocole UI, contrat visuel) |
| ruff · shellcheck (`run.sh`) · actionlint | propres (actionlint : un avertissement **préexistant** ligne 647, hors de cette tranche) |
| Full sweep local | voir §5 |
| CI réelle | voir §5 |

## 4. DA-02.4 — ce qui est gardé, ce qui ne l'est pas

Conformément au §9 du brief et à la décision n° 7 de l'opérateur :
- **la composition DA-02.4 n'est pas committée** ; elle n'a aucune autorité ;
- **sont retenus pour une revue séparée** : le principe REST / ADJUSTING / COMMITTED, le correctif des noms de zone (boîtes à la
  largeur du nom, bords vérifiés) et les mesures compactes. Ils restent sur la branche locale `sb/da-02-4-instrument-surface`, à
  extraire dans DA-02.4B.

## 5. Preuves sur CI réelle

*(complété après exécution de la CI de la PR)*

**Verdict :** à rendre après la CI réelle (exigence `ci_infra`).
