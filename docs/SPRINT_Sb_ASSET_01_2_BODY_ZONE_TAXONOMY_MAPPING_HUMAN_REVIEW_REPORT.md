# Sb_ASSET_01.2 — Body Zone Taxonomy & Mapping Contract — HUMAN REVIEW REPORT

**Verdict :** 🟢 **HUMAN REVIEW: ACCEPTED**
**Type** : human review — **DOCS-ONLY** (aucune modif `design/**`/`tests/**`/`app/**`)
**Date** : 2026-07-20
**Programme** : `Sx_ASSET` — Auren Proprietary Visual Asset System (2ᵉ et dernier build du socle `Sx_ASSET_01`)
**Commit audité** : `86aba63` — *feat(assets): define Auren body zone mapping contract*

> Cette revue valide le **contrat sémantique** (taxonomie 11 zones, mapping 6 macros, IDs SVG). Elle **ne
> constitue pas** une validation anatomique/géométrique, ni une autorisation d'intégration runtime. L'`ASSET
> INTEGRATION GATE` **reste BLOCKED**.

---

## 1. État Git initial & 2. Baseline canonique
HEAD local = HEAD origin = `86aba63`, working tree clean, branche `claude/sprint-reporting-fitness-app-V7Qr6`.

## 3. Ascendance
`git merge-base --is-ancestor 86aba63 HEAD` → exit **0**. `git diff 86aba63..HEAD` = **vide** → **aucun drift
post-build** ; tous les fichiers du build (contrat/tests/docs) intacts.

## 4. Worktree & 5. Collisions
Worktree `work/sb-asset-01-2-human-review` sur `86aba63`. Anti-collision : `origin` contrôlé avant
revue/écriture/commit/FF/push. Aucun rebase/reset/amend/force-push ; **2 worktrees Custom intouchés**.

## 6. Commit audité
`86aba63` — 14 fichiers, **+890 / −18**. 7 design (2 neufs : `AUREN_BODY_ZONE_TAXONOMY.md`,
`source/bodymap/auren_bodymap_mapping.yaml` + README source ; 4 modifiés) + 2 tests + 5 docs. Pas d'amend.

## 7. Diff
Composition conforme : `design/auren/` (7) + `tests/` (2) + `docs/` (5). **0** `app/`/`data/`/`migrations/`/
`.github/`/`requirements*`/`pyproject.toml`/Custom.

## 8. Correction documentaire 01.1
La seule modif de `SPRINT_Sb_ASSET_01_1_..._HUMAN_REVIEW_REPORT.md` est **d'un caractère** :
`**Verdict** :` → `**Verdict :**` (marqueur reconnu par `check_spec_protocol`). **La décision et les constats
de la revue 01.1 sont inchangés.** Correction légitime d'un bug docs pré-existant (sa CI 01.1 avait été
légitimement skippée en docs-only).

## 9. Taxonomie — ELEVEN-ZONE RUNTIME PARITY: VERIFIED
Revérifié **indépendamment** (import `ZONE_LABELS`, sans faire confiance au test livré) : 11 zones exactes,
**ordre canonique** identique, **même ensemble**, **0 alias**, 0 code déprécié, 0 douzième zone.

## 10. Labels
`label_fr` **identiques** à `ZONE_LABELS` pour les 11 codes (revérifié). Pectoraux / Deltoïdes latéraux /
Deltoïdes postérieurs / Dos largeur / Dos épaisseur / Biceps / Triceps / Quadriceps / Ischios / Fessiers /
Mollets / Core / Abdos.

## 11. `unknown` — UNKNOWN STATE: HONEST AND NON-ANATOMICAL
`code: unknown · nature: qualification-state · anatomical_zone: false · label: À qualifier · visual: neutral`.
Absent de `zones`, absent des métriques de couverture, **0 `zone-unknown`**, aucune macro, aucune conversion
auto. Descriptor `unknown` → `zones = []` (revérifié sur 10 exercices).

## 12. Zones agrégées — FUNCTIONAL AGGREGATES: GRANULARITY HONEST
`upper_back` et `posterior` = `semantic_kind: functional-aggregate`. `aggregate_notes` : `upper_back` ne
prétend PAS distinguer trapèzes/rhomboïdes/faisceaux/insertion ; `posterior` ne prétend PAS localiser chaque
muscle. Règle : « le futur BodyMap reflète la granularité de la donnée, jamais davantage ». ✔

## 13. Six macros — COMPACT MACRO PARITY: VERIFIED
`chest/shoulders/back/arms/legs/core`. Chaque zone dans **exactement une** macro ; **union = 11 zones** ; 0
orpheline ; 0 doublon ; 0 macro supplémentaire.

## 14. Parité Jinja (extraction indépendante)
`_WA_ZONE_TO_REGION` extrait **par mes soins** via `ast.literal_eval` du littéral isolé (sans rendu HTML,
sans réutiliser le test) → **identique** au mapping du contrat. ✔

## 15. Différence radar — VISUAL / ANALYTICAL MODEL SEPARATION: VERIFIED
`BODYMAP COMPACT MACROS ARE NOT RADAR_AXES` présent (contrat + taxonomie). Confirmé indépendamment :
`back` (BodyMap) fusionne `lats`+`upper_back` **pour le rendu compact** ; `RADAR_AXES` conserve `back_width`
(lats) + `back_thickness` (upper_back) **séparés** ; `core` présent dans les macros, **absent** de
`RADAR_AXES` ; `legs` visuel ≈ `lower` fonctionnel **sans être identiques**.

## 16. `RADAR_AXES` inchangé
`git diff --quiet 7da5334..86aba63 -- app/services/muscle_mapping.py` → **0** (byte-identique). Valeurs
runtime confirmées : `RADAR_AXIS_ORDER == [pecs, shoulders, back_width, back_thickness, arms, lower]`.
**Aucun score ni agrégat analytique modifié.**

## 17. YAML — STRUCTURED CONTRACT: PARSABLE AND NON-RUNTIME
YAML 1.2 en syntaxe **JSON-compatible**, `json.loads` OK **sans PyYAML** (absent de `requirements`/
`pyproject`, seulement transitif dans le lock). Déterministe, pas de commentaire nécessaire au parsing. Les
14 champs requis présents (schema … invariants). `runtime_sources.note` : **« design contract MIRRORS runtime
truth ; does NOT replace runtime truth »**. Le contrat n'est **pas** chargé par l'app, n'est **pas** une
config métier, n'est **pas** une migration active.

## 18. IDs SVG — SVG ID CONTRACT: STABLE / GEOMETRY NOT PRODUCED
14 IDs exacts (`auren-bodymap`, `body-front-base`, `body-back-base`, `zone-<11>`). Unicité ; 1 ID/zone ; **0
`zone-unknown`** ; **0 ID genré** ; 0 alias ; 0 ID dépendant de la macro. Décrits comme **API future**, pas
comme éléments SVG présents (aucune géométrie associée).

## 19. États
5 exacts : `neutral/primary/secondary/unknown/disabled`. **0 couleur / 0 hex** dans le YAML (vérifié par
regex). `unknown` ≠ erreur ; `disabled` ≠ zone anatomique absente ; palette pilotée par tokens runtime ;
non-color cue requis.

## 20. Surfaces
`session-compact: current` (preuve : `exercise_card.html` inclut `worked_area_body_map.html`) ;
**`body-intelligence: not-yet-integrated`** — **audit indépendant confirme** que `body_intelligence.html`
inclut son propre `body_intelligence_zone_card.html`, **PAS** le BodyMap worked-area. Autres = `future`.
**Aucun consumer inventé ; body-intelligence n'est PAS faussement déclaré intégré.** ✔

## 21. Variantes — BODY VARIANTS: CONTRACT ONLY
3 variantes (`male_neutral_v1`, `female_neutral_v1`, `neutral_abstract_v1`), **aucune available**, aucun
fichier source, `geometry_status: NOT YET PRODUCED`. 0 genre dans les codes ; 14 IDs identiques entre
variantes ; `male_neutral_v1` **non** présenté comme choix final approuvé.

## 22. Absence de géométrie
`rg` géométrie sur le YAML → **0 clé/donnée** (path/polygon/coordinates/activation/percentage/EMG/`<svg>`).
Les mentions dans le MD sont de la **prose normative d'interdiction** (distinction interdiction ≠ donnée
respectée). `find design/auren/source/bodymap` → **`README.md` + `auren_bodymap_mapping.yaml` uniquement**.

## 23. Descriptor
`build_body_map_descriptor` **byte-identique** (0 diff). Test indépendant sur 10 exercices : tous les codes
produits ∈ `ZONE_LABELS ∪ {unknown}` ; mapped → primary canonique + secondaires dédupliquées, primary
d'abord ; unknown → `primary=unknown`, `zones=[]`, `needs_qualification=true`. Forme/ordre/champs/résolution
DB-fallback inchangés. « No anatomy is invented » tenu.

## 24. Owner/IP — IP OWNERSHIP CLAIMS: PROPERLY QUALIFIED
Champ `ip_ownership_status` ajouté (`not-legally-reviewed | verified | unknown | not-applicable`). Les 3
entrées runtime + l'entrée contrats portent `owner: … — OPERATIONAL REPOSITORY CUSTODIAN` +
`ip_ownership_status: not-legally-reviewed` + `IP OWNERSHIP NOT LEGALLY VERIFIED`. Documenté : « owner =
gardien opérationnel OU titulaire revendiqué ; ≠ propriété juridiquement démontrée ». **Aucune** entrée
réellement `ip_ownership_status: verified` (valeur seulement documentée comme autorisée — accepté). La dette
§11.1 de la revue 01.1 est **résolue**.

## 25. Garde évolutive — GOVERNANCE GUARD: EVOLVABLE BUT STILL CLOSED TO ASSETS
Distinction vérifiée : binaires (svg/png/webp/ico/jpeg/gif/fonts/blend/fig) **permanents interdits** ;
**allowlist exacte** (`design/auren/source/bodymap/auren_bodymap_mapping.yaml`, pas un glob/répertoire) ;
tout autre `.yaml/.yml/.json` refusé ; **SVG toujours interdits**. Le test documente la permanence de la
garde binaire + l'évolution future vers validation adossée au manifest (`Sb_ASSET_02.1`/`03.2`). **Test
négatif exécuté par mes soins** : ajout d'un YAML/JSON non-allowlisté → `test_structured_files_only_via_allowlist`
échoue ; ajout d'un SVG → `test_no_asset_binaries_under_design_auren` échoue ; après suppression → les 2 tests
repassent, working tree propre (aucun fichier temporaire résiduel). La dette §16 de la revue 01.1 est
**résolue**.

## 26. Tests
`test_auren_body_zone_contract.py` (**29**) + `test_auren_asset_governance.py` (**23**) — stdlib only (YAML lu
par `json`), **0 SHA fixe**, comparaisons au **runtime réel** (import + `ast.literal_eval`), non tautologiques.
Le test `RADAR_AXES` inspecte les **valeurs runtime** (pas une chaîne documentaire) et reste évoluable par un
futur sprint analytics légitime. Résultats en revue : **52 passed** ; suites adjacentes **185 passed** ;
descriptor indépendant OK.

## 27. Absence d'asset
`find design/auren` binaires/fonts → **∅**. 0 master/preview/export/token JSON/licence tierce/subset d'icônes.
Le YAML est un **contrat sémantique**, pas un asset visuel.

## 28. Absence d'app changes
`git diff --quiet 7da5334..86aba63 -- app/` → **0**. `muscle_mapping.py`, `body_map_descriptor.py`,
`worked_area_body_map.html` **byte-identiques**. 0 router/service/model/migration/template/CSS/JS/manifest/
icône runtime/data.

## 29. Tests locaux
52 dédiés + 185 adjacents + descriptor indépendant · ruff clean · budget 543 ≤ 548 · spec PASS · scope
ISOLATED.

## 30. CI exacte — CI VERIFIED — 3/3 SUCCESS
Run `29702926887` (wf `CI`) sur SHA `86aba63a6c0d2fdefebcecefbc44761c7ffccf5d` : pytest+QA / lint /
SonarCloud = completed/**success**. **Aucun step non-success ; aucun step obligatoire skippé.**

## 31. Gate d'intégration
`ASSET INTEGRATION GATE: BLOCKED PENDING HUMAN / ANATOMICAL / LEGAL / MOBILE APPROVALS` — inchangé. La
validation du contrat **n'autorise pas** : validation anatomique/géométrique, production auto du master,
intégration `app/static/`, clearance juridique du nom/assets, import Tabler, approbation des variantes.
Acquis après 01.2 : **taxonomie sémantique · mapping compact · IDs futurs · gouvernance · tests de parité.**

## 32. Risques / dettes
- **Aucune dette bloquante.** Les 2 dettes de la revue 01.1 (`owner` nuancé §24 ; garde évolutive §25) sont
  **résolues**.
- **[OUVERT — non régressif, hors périmètre]** clearance nom Auren (brand-bearing `provisional`) ; production
  humaine du master anatomique (`OPERATOR_ASSET_03.1`) ; intake technique (`Sb_ASSET_03.2`) — déjà tracés.
Aucun critère de REJECTED (divergence `ZONE_LABELS`/`_WA_ZONE_TO_REGION`, fusion radar, unknown-zone,
géométrie, contrat runtime, SVG prématurés, IP verified, gate ouvert, test factice) ni de BLOCKED (drift,
collision, source inaccessible, CI non vérifiable) n'est déclenché.

## 33. Décision
🟢 **HUMAN REVIEW: ACCEPTED.** Les 20 critères §28 sont remplis (revérifiés **indépendamment** du test livré :
parité 11 zones/labels, unknown non-anatomique, 6 macros, parité Jinja, séparation & invariance radar, IDs,
0 géométrie, 0 variante produite, YAML parsable sans dépendance, contrat miroir non-runtime, IP nuancée,
garde allowlistée prouvée par test négatif, 0 app, 0 asset, gate bloqué, tests non tautologiques).

## 34-35. Statut & prochaine action
Le socle `Sx_ASSET_01` est **implémenté** (01.1 + 01.2 acceptés) → **COMPLETE / READY FOR CLOSEOUT** (le
closeout `Sx_ASSET_01` reste une action séparée). **`Sx_ASSET_02` NON ouvert.**

## 36. Prochaine action (non commencée)
`GO CLOSEOUT — Sx_ASSET_01 Architecture, Governance & Production Gate`.

---

**Statut final**
```
Sb_ASSET_01.1              : HUMAN REVIEW ACCEPTED
Sb_ASSET_01.2              : CODE COMPLETE · CI GREEN · HUMAN REVIEW ACCEPTED
Sx_ASSET_01 implementation : COMPLETE / READY FOR CLOSEOUT
ASSET INTEGRATION GATE     : BLOCKED PENDING HUMAN / ANATOMICAL / LEGAL / MOBILE APPROVALS
Sx_ASSET_02                : NOT OPENED
Sx_UI                      : CLOSED / HUMAN REVIEW COMPLETE
```
Non marqué : contrat legally cleared · master authorized · integration authorized · `Sx_ASSET_01 CLOSED`
(closeout séparé requis).
