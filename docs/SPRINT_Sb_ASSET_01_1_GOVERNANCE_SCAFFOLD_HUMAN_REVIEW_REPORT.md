# Sb_ASSET_01.1 — Governance Scaffold & Provenance Registry — HUMAN REVIEW REPORT

**Verdict :** 🟢 **HUMAN REVIEW: ACCEPTED** (avec 1 dette corrective enregistrée — §20/§24)
**Type** : human review — **DOCS-ONLY** (aucune modif `design/**`/`tests/**`/`app/**`)
**Date** : 2026-07-19
**Programme** : `Sx_ASSET` — Auren Proprietary Visual Asset System (1er build, `Sb_ASSET_01.1`)
**Commit audité** : `4603551` — *chore(assets): establish Auren asset governance scaffold*

> Cette revue statue sur la **gouvernance** du scaffold. Elle **ne dégage juridiquement** ni le nom Auren,
> ni les assets brand-bearing, ni aucun master. L'`ASSET INTEGRATION GATE` **reste BLOCKED**.

---

## 1. Baseline canonique
HEAD local = HEAD origin = `4603551`, working tree clean, branche `claude/sprint-reporting-fitness-app-V7Qr6`.

## 2. Ascendance
`git merge-base --is-ancestor 4603551 HEAD` → exit **0**. `git diff 4603551..HEAD` = **vide**.
→ HEAD = `4603551`, **aucun drift post-build** du scaffold.

## 3. Commit audité
`4603551` — 11 fichiers, **+841 / −1**. Message conforme (`chore(assets): …` + trailer Co-Authored-By).
Pas d'amend de `4603551`.

## 4. CI
Run **29697874021** (wf `CI`) sur SHA `46035517fc3e754b6d8fde3732104c1c28d0d757` :
- **pytest + QA scripts** = completed / **success** (coverage, catalog/atlas QA, Alembic drift, schema
  snapshot, migration patterns, migration roundtrip, perf smoke — tous success) ;
- **lint** (ruff budget + bandit + actionlint + shellcheck + pip-audit + gitleaks + spec protocol) =
  completed / **success** ;
- **SonarCloud** = completed / **success** (scan réellement exécuté).
- **Aucun step non-success ; aucun step obligatoire skippé.**
→ **CI VERIFIED — 3/3 SUCCESS.**

## 5. Diff
`git diff --name-status 6167485..4603551` :
```
A design/auren/AUREN_ASSET_INTAKE_CHECKLIST.md
A design/auren/AUREN_ASSET_PROVENANCE.md
A design/auren/AUREN_STYLE_RULES.md
A design/auren/AUREN_VISUAL_ASSET_MANIFEST.md
A design/auren/LICENSES/README.md
A design/auren/README.md
A docs/SPRINT_Sb_ASSET_01_1_GOVERNANCE_SCAFFOLD_REPORT.md
M docs/strategy/AUREN_ASSET_PROGRAM_ROADMAP.md
M docs/strategy/ROADMAP_AND_NEXT_STEPS.md
M docs/strategy/SPEC_REGISTRY.md
A tests/test_auren_asset_governance.py
```
**Absents (confirmés)** : `app/**`, `data/**`, `migrations/**`, `.github/**`, `requirements*`,
`pyproject.toml`, SVG/PNG/WebP/ICO/JPEG/font, YAML/JSON, licence tierce, master anatomique, asset importé.

## 6. Architecture du scaffold
`design/auren/` contient **exactement** les 6 fichiers utiles annoncés (README, manifest, style rules,
provenance, intake checklist, LICENSES/README). **Aucun** dossier vide trompeur, `.gitkeep`, structure
future présentée comme produite, master/export/preview fictif, faux fichier de licence. Les dossiers futurs
(`source/`, `exports/`, `previews/`, `references/`, `tokens/`) sont **documentés dans le README, non créés
vides**. → **SCAFFOLD MINIMAL AND HONEST.**

## 7. Manifest
- **16 champs normatifs** présents (id … deprecated_by).
- **8 statuts bornés** exactement (draft / provisional / human-review-required / anatomical-review-required
  / legal-review-required / approved / deprecated / rejected). `approved` exige product + technical +
  accessibility + license + mobile (si mobile) + anatomical (BodyMap), et **interdit** `license: UNKNOWN`.
- Valeurs inconnues **distinguées** : `NOT APPLICABLE` ≠ `UNKNOWN — MANUAL VERIFICATION REQUIRED` ≠
  `NOT YET REVIEWED` / `NOT YET PRODUCED`. Aucune valeur inconnue masquée par `N/A`.

## 8. Entrées initiales (runtime existant — référencé, non copié)
| id | runtime_file | type | status | vérif |
|---|---|---|---|---|
| `auren.runtime.bodymap.prototype` | `app/templates/_partials/worked_area_body_map.html` (4490 o) | anatomical-map-prototype | **provisional** | prototype explicite, `NOT YET PRODUCED` master, 11 zones |
| `auren.runtime.pwa.mark` | `app/static/icons/auren-mark.svg` (248 o) | brand-mark | **provisional** | brand-bearing, clearance open |
| `auren.runtime.pwa.favicon` | `favicon.svg` (256 o) | favicon | **provisional** | idem |
| `auren.runtime.pwa.apple-touch` | `apple-touch-icon.png` (1582 o) | pwa-icon | **provisional** | idem |
| `auren.runtime.pwa.icon.192` | `icon-192.png` (1475 o) | pwa-icon | **provisional** | idem |
| `auren.runtime.pwa.icon.512` | `icon-512.png` (6567 o) | pwa-icon | **provisional** | idem |
| `auren.runtime.pwa.maskable.512` | `icon-maskable-512.png` (6567 o) | maskable-icon | **provisional** | idem ; **pas** de maskable-192 (non inventé) |
| `auren.runtime.shell.inline-icons` | `app/templates/base.html` (12997 o) | functional-inline-icon-set | **provisional** | repository-authored (Sb_UI_03.1) |

IDs uniques, runtime_file réels (tous existants aux poids déclarés), consumers réels, types cohérents.
**Aucune** entrée `approved`. Masters futurs (§5 du manifest) documentés, **non créés** (0 faux master).

## 9. Statuts
`re.findall(r"(?m)^\s*status:\s*approved\b", manifest)` → **∅**. Aucune entrée `approved`. La seule
occurrence prose du mot documente qu'il n'apparaît sur aucune entrée. ✔

## 10. Audit propriété / provenance — point critique (§11)
- **§11.5** — `license_spdx: NOT APPLICABLE` signifie bien « aucune licence tierce applicable connue »
  (œuvre du repo), **non** « droits commerciaux prouvés ». La distinction est consignée. ✔
- **§11.3 / §11.4** — `status: verified-repository-authored` **n'est pas** présenté comme une clearance
  juridique : le `legal_note` PWA porte **« BRAND-BEARING … EXTERNAL PROFESSIONAL CLEARANCE OPEN »** et
  `review.legal: NOT YET REVIEWED` ; le README §71-72 : **« Ce scaffold ne constitue aucune conclusion
  juridique »**. ✔
- **§11.1 — champ `owner`** : les 3 entrées portent `owner: MFE-DSS/workout-session-tracking` (nom de
  repository) **sans qualificatif littéral**. Le brief attend une valeur nuancée
  (`OPERATIONAL REPOSITORY OWNER, IP OWNERSHIP NOT LEGALLY VERIFIED`).
  **Analyse** : pris dans son ensemble, le registre présente `owner` comme **propriétaire opérationnel du
  repository**, jamais comme propriétaire juridique démontré (cf. legal_note / review.legal / README /
  license NOT APPLICABLE). Ce n'est **pas** une fausse revendication de clearance ; l'imprécision porte sur
  la seule formulation du champ. → **décision humaine : ACCEPTED avec dette corrective** (nuancer le champ
  `owner` en `OPERATIONAL REPOSITORY OWNER — IP OWNERSHIP NOT LEGALLY VERIFIED`), à traiter dans un build
  séparé (`Sb_ASSET_01.2`), **jamais** dans cette revue docs-only. Voir §20.

## 11. Audit BodyMap
`auren.runtime.bodymap.prototype` — `repository (Sb_BODYMAP_01.1)`, `source_type: repository-authored`,
`source_project: NOT APPLICABLE`, `status: verified-repository-authored`, evidence =
`docs/SPRINT_Sb_BODYMAP_01_1_INLINE_BODYMAP_HUMAN_REVIEW_REPORT.md` (**accessible**). Classé **prototype /
provisional**, `anatomical: NOT YET REVIEWED`, master `NOT YET PRODUCED`. Le registre confirme **uniquement**
ce qui est démontré (hand-authored dans le repo, prototype runtime) sans conclure « œuvre entièrement
originale / droits exclusifs / absence de toute inspiration ». ✔

## 12. Audit PWA
`repository (Sb_UI_10.2)` — glyphe haltère existant **recoloré `#f25f3a`→`#C8A24B`**, PNG rasterisés via
`sips` ; commit d'origine réel `9203e4c`. evidence =
`docs/SPRINT_Sb_UI_10_2_PWA_MANIFEST_APP_ICONS_AUREN_HUMAN_REVIEW_REPORT.md` (**accessible**). **Brand-bearing
→ provisional jusqu'à clearance** ; `review.legal: NOT YET REVIEWED`. Le SVG `auren-mark.svg` ne porte
aucune mention d'outil/bibliothèque tierce. La provenance du glyphe original antérieur au rebrand relève
d'une vérification manuelle éventuelle — mais l'entrée **ne prétend pas** de clearance juridique ; l'état
`provisional` + `legal NOT YET REVIEWED` couvre correctement l'incertitude. ✔

## 13. Audit icônes inline shell
`repository (Sb_UI_03.1)` — `source_project: NOT APPLICABLE` (**PAS Tabler/Health**, dessinées à la main) ;
commit d'origine réel `5a35ba8`. evidence = `docs/SPRINT_Sb_UI_03_*_HUMAN_REVIEW_REPORT.md` (3 rapports
**accessibles** : bottom-nav / rail / hardening). « repository-authored — upstream not documented » est
présenté comme **état opérationnel**, non comme clearance ; le subset gouverné (Tabler vendored) fera l'objet
d'un intake tiers complet en `Sb_ASSET_02.1`. ✔

## 14. Licences
`design/auren/LICENSES/` = **`README.md` seul** (vérifié). Le README exige texte officiel complet + SPDX +
source officielle + version/date + attribution + lien provenance, interdit reconstruction/agrégateur/copie
prématurée `MIT.txt`/`CC-BY-4.0.txt`/`Apache-2.0.txt`, et déclare **« No third-party asset has been accepted
into the Auren source pack. »**. Aucune licence fabriquée. ✔

## 15. Style rules
Positionnement **biomécanique non médical** (non atlas/gamer/pseudo-IA) ; identité **Auren Terminal**
(graphite / mono / ambre `#C8A24B` / **0 nouvelle couleur** / `currentColor`) ; contrat SVG (`viewBox 24`,
`stroke-width 2`, round caps/joins, `fill none`, `currentColor`) ; interdits (gradient/filtre/ombre/bitmap/
script/URL/emoji/webfont/hex) ; anatomie **11 zones** (« jamais une 12ᵉ ») ; accessibilité (BodyMap décoratif
`aria-hidden`/`focusable=false`, action labellisée, non-color cue). **Aucune** prétention qu'un master existe.
✔

## 16. Intake checklist
Couvre identification / provenance / technique / sémantique / accessibilité / revues / verdict. Distingue
**`ACCEPTED FOR DESIGN SOURCE`** de **`NOT AUTHORIZED FOR APP INTEGRATION`** ; l'intake **n'est jamais**
présenté comme le franchissement du gate global. Revue anatomique scoped **BodyMap uniquement**. ✔

## 17. Tests
`tests/test_auren_asset_governance.py` — **21 tests, stdlib only** (`re`, `pathlib`). Vérifient réellement
les fichiers (non tautologiques) : 8 statuts bornés, faux `approved` détecté (regex ligne d'entrée YAML),
binaire/asset détecté (`rglob` + suffixes), master interdit détecté, licence tierce prématurée détectée,
runtime paths vérifiés, **aucun SHA fixe**. → **21 passed** en revue.
**Temporalité (§16)** : `test_no_asset_binaries_under_design_auren` interdit tout SVG/PNG sous
`design/auren/` — garde **légitime pour ce lot**, mais devra évoluer au premier intake autorisé
(`Sb_ASSET_02.1`, subset Tabler dans `design/auren/source/…`). Cette temporalité n'est **pas** documentée
en toutes lettres dans le test. Test facile à faire évoluer → **dette enregistrée** (§20), **pas** un motif
de rejet.

## 18. Absence d'assets
`find design/auren -type f (svg|png|webp|ico|jpg|jpeg|gif|woff|woff2|ttf|otf|blend|fig)` → **∅**.
`find … (yaml|yml|json)` → **∅**. `design/auren/` = **6 fichiers Markdown** (+ `LICENSES/README.md`).
Aucun asset runtime déplacé ou dupliqué. ✔

## 19. Absence d'app changes
`git diff --quiet 6167485..4603551 -- app/` → exit **0**. `git diff --name-only … | grep '^app/'` → **∅**.
Aucun template / CSS / manifest / icône runtime / router / service / modèle / donnée modifié. Test
`test_no_runtime_asset_moved_or_removed` confirme les 7 assets runtime **en place**. ✔

## 20. Risques / dettes
1. **[DETTE — §11.1] Champ `owner` non nuancé** — les entrées provenance portent
   `owner: MFE-DSS/workout-session-tracking` sans qualificatif. Corriger en
   `OPERATIONAL REPOSITORY OWNER — IP OWNERSHIP NOT LEGALLY VERIFIED` (ou `UNKNOWN — MANUAL VERIFICATION
   REQUIRED`) lors d'un **build séparé** (`Sb_ASSET_01.2` ou correctif dédié). N'affecte pas l'acceptation
   du scaffold (l'intention opérationnelle est claire par le contexte ; aucune clearance juridique n'est
   affirmée). **Ne pas corriger dans cette revue docs-only.**
2. **[DETTE — §16] Temporalité du garde binaire** — documenter, dans le test ou le manifest, que
   l'interdiction de tout SVG/PNG sous `design/auren/` est un **garde du lot Sb_ASSET_01.1** appelé à évoluer
   au premier intake tiers (`Sb_ASSET_02.1`, `design/auren/source/…`). À traiter avec l'intake, build séparé.
3. **[OUVERT — non régressif] Clearance nom Auren** — brand-bearing assets `provisional` ; clearance
   professionnelle externe **OPEN** (hors périmètre de ce programme, déjà tracé).

Aucun de ces points n'est un **défaut matériel** au sens §21 (pas de PI affirmée sans preuve, pas d'upstream
interne fabriqué, pas de faux `verified` de clearance, pas de licence inférée, pas d'`approved` prématuré,
pas d'asset caché, pas d'app modifiée).

## 21. Décision humaine
🟢 **HUMAN REVIEW: ACCEPTED.** Les 16 critères §21 sont remplis : (1) commit canonique et ancêtre ;
(2) CI 3/3 vérifiée ; (3) scaffold minimal ; (4) 0 asset produit ; (5) 0 app modifiée ; (6) manifest borné ;
(7) 0 `approved` ; (8) runtime référencé sans copie ; (9) provenance inconnue explicite ; (10) aucune PI non
démontrée présentée comme certaine (le champ `owner` reste opérationnel, dette cosmétique enregistrée) ;
(11) 0 licence tierce prématurée ; (12) style rules cohérentes ; (13) intake ≠ intégration ; (14) tests réels
non tautologiques ; (15) gate d'intégration toujours **BLOCKED** ; (16) `Sx_UI` toujours **CLOSED**.

## 22. Prochaine action (non commencée)
`GO BUILD — Sb_ASSET_01.2 Body Zone Taxonomy & Mapping Contract` — qui **absorbera** les 2 dettes ci-dessus
(nuancer `owner` ; documenter la temporalité du garde binaire).

---

**Statut final**
```
Sb_ASSET_01.1        : CODE COMPLETE · CI GREEN · HUMAN REVIEW ACCEPTED
ASSET INTEGRATION GATE : BLOCKED PENDING HUMAN / ANATOMICAL / LEGAL / MOBILE APPROVALS
Sb_ASSET_01.2        : NOT OPENED
Sx_UI                : CLOSED / HUMAN REVIEW COMPLETE
```
Non marqué : scaffold legally cleared · runtime assets legally cleared · asset pack approved ·
integration authorized.
