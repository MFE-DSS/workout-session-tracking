# Sx_ASSET_02 — Functional Iconography Selection — SPEC

**Type** : SPEC / AUDIT / OFFICIAL-SOURCE RESEARCH — **DOCS-ONLY**, NO SVG INTAKE, NO LICENSE FILE, NO APP CHANGE
**Statut** : 🔒 **CLOSED / HUMAN REVIEW COMPLETE** 2026-07-21 — cycle `Sx_ASSET_02` clos (spec + intake Tabler P0 accepté + correctif preview + re-review) ; cf. [`../SPRINT_Sx_ASSET_02_FINAL_CLOSEOUT_REPORT.md`](../SPRINT_Sx_ASSET_02_FINAL_CLOSEOUT_REPORT.md). `ICON SOURCE INTAKE: ACCEPTED FOR DESIGN SOURCE` ; 10 icônes NOT AUTHORIZED FOR APP INTEGRATION ; `ASSET INTEGRATION GATE: BLOCKED`. *(statut initial : SPEC RÉDIGÉE / READY FOR GO COMMIT 2026-07-20)*
**Programme** : `Sx_ASSET` — Auren Proprietary Visual Asset System · **2ᵉ cycle**
**Date** : 2026-07-20 · **Baseline** : `c1ad76c` (closeout Sx_ASSET_01)
**Due diligence** : [`../research/AUREN_ICON_VENDOR_DUE_DILIGENCE.md`](../research/AUREN_ICON_VENDOR_DUE_DILIGENCE.md)

> `Sx_ASSET_01` reste **CLOSED**, `Sx_UI` reste **CLOSED**. Ce cycle **ne rouvre ni l'un ni l'autre**. Il
> **sélectionne un vocabulaire visuel fonctionnel minimal** (sémantique d'abord), il **n'importe aucune
> bibliothèque**. Résultat visé : « vocabulaire minimal, stable, accessible, licencié, cohérent Auren
> Terminal », **pas** « importer une librairie d'icônes ».

---

## 1. Mission
Cartographier la sémantique de l'iconographie fonctionnelle Auren, sélectionner un subset **minimal et
versionné** d'icônes tierces (Tabler primaire, Health Icons secondaire conditionnel), identifier ce qui doit
rester **typographique**, et démontrer les **rares** gaps custom éventuels. Produit une spec exploitable pour
`Sb_ASSET_02.1` (intake) et, **seulement si gaps réels**, `Sb_ASSET_02.2` (glyphes custom).

## 2. Baseline
`c1ad76c`. `Sx_ASSET_01 CLOSED / HUMAN REVIEW COMPLETE` · `ASSET INTEGRATION GATE: BLOCKED` · `Sx_ASSET_02:
(cette spec)` · `Sx_UI CLOSED`. Aucun changement runtime.

## 3. Brainstorming (§7 — conclusion)
```
SEMANTICS BEFORE ICONS · MINIMAL SUBSET · TEXT REMAINS PRIMARY · NO MEDICALIZATION · NO AI SPARKLES
ONE CONCEPT / ONE METAPHOR · OFFICIAL SOURCES ONLY · VERSION AND COMMIT PINNED · NO RUNTIME LIBRARY
NO ASSET INTAKE IN SPEC · CUSTOM GLYPHS ONLY FOR PROVEN GAPS
```
Décisions structurantes (30 questions §7) : (a) l'iconographie runtime réelle est **minuscule** — seulement
**8 SVG inline** dans `base.html` (4 bottom-nav + 4 rail, identiques) ; tout le reste est **texte + quelques
glyphes/emoji non gouvernés** (`✓ ⚠ 💡 ☰`). (b) Le texte **reste primaire** ; l'icône n'abrège que des
contrôles **universels et répétés**. (c) Les 4 nav sont **comprises et cohérentes** → `existing-runtime-keep`
(pas de migration ce cycle). (d) Priorité de cohérence : **provenance > style de trait > métaphore > taille >
alignement** (un trait cohérent sans provenance gouvernée resterait une dette). (e) `RADAR_AXES`/scores/zones
= **jamais** iconifiés. (f) Health Icons **non requis pour P0** (Tabler + texte couvrent).

## 4. Sources officielles (relevé 2026-07-20 — détail dans la due diligence)
- **Tabler Icons** : `v3.45.0` (2026-07-17), commit **`975920ff99c12c4dc9e3fe61a03738330600f9b2`**, **MIT**
  (© Paweł Kuna), **5112 outline**, `viewBox 24 / fill none / stroke currentColor / stroke-width 2` =
  **contrat Auren exact**. → source **PRIMAIRE**.
- **Health Icons** : repo `resolvetosavelives/healthicons`, **0 tag** → commit **`891ace7addf4deb7a8b1ce8292d5906064fab36a`**
  (2025-09-04). **Icônes = CC0** ; **code repo = MIT** (distinction critique). → source **SECONDAIRE
  conditionnelle**, **NOT REQUIRED FOR P0**.

## 5. Audit runtime (lecture seule, baseline `c1ad76c`)
- **`app/templates/base.html`** : **8 `<svg>` inline** — bottom-nav (Séance, Programmes, Progression, Profil)
  + rail desktop (mêmes 4). `viewBox 24`, `currentColor`, `stroke-width 1.7`, `aria-hidden="true"`
  `focusable="false"`, **label texte visible** à côté. Menu secondaire = `<summary>☰</summary>`.
- **Glyphes/emoji non gouvernés** : `✓` (`session_done`, série validée), `⚠` (anomaly, coach report), `💡`
  (`exercise_card` hint conseils), `☰` (nav toggle), `✓` (texte du SVG welcome).
- **Hors scope icônes fonctionnelles** : `worked_area_body_map.html` (BodyMap → `Sx_ASSET_03`),
  `welcome.html` SVG et `science_diagram.svg` (illustrations/schémas).
- **Fait majeur** : l'app est **déjà quasi sans icônes** ; les concepts (substitution, guidance, completed,
  trend…) sont **portés par le texte**. Le besoin réel d'icônes est **faible et ciblé**.

## 6. Inventaire des SVG actuels (matrice §11)
| ID provisoire | Fichier | Surface | Concept | Statut | Texte adjacent | Provenance |
|---|---|---|---|---|---|---|
| `inline.nav.session` | base.html | bottom-nav / rail | Navigation Séance | **existing-runtime-keep** (provisional) | oui (« Séance ») | repository-authored (Sb_UI_03.1) |
| `inline.nav.programs` | base.html | bottom-nav / rail | Navigation Programmes | **existing-runtime-keep** | oui | idem |
| `inline.nav.progress` | base.html | bottom-nav / rail | Navigation Progression | **existing-runtime-keep** | oui | idem |
| `inline.nav.profile` | base.html | bottom-nav / rail | Navigation Profil | **existing-runtime-keep** | oui | idem |
| `glyph.check` (`✓`) | session_done, exercise_card | status | Completed / validé | **REPLACE WITH VENDORED CANDIDATE** (ou typographic) | oui | emoji/glyphe (non gouverné) |
| `glyph.warn` (`⚠`) | session_done, coach_report | information | Avertissement | **REPLACE WITH VENDORED CANDIDATE** | oui | emoji/glyphe |
| `glyph.hint` (`💡`) | exercise_card | information | Guidance / conseil | **REPLACE WITH VENDORED CANDIDATE** | oui | emoji/glyphe |
| `glyph.menu` (`☰`) | base.html | secondary-nav | Ouvrir nav secondaire | **REPLACE WITH VENDORED CANDIDATE** | `aria-label` | glyphe |
| `illus.welcome` | welcome.html | onboarding | Illustration | **OUT OF SCOPE** (illustration) | — | repository-authored |
| `illus.science` | science_diagram.svg | science page | Schéma | **OUT OF SCOPE** | — | repository-authored |
| `bodymap.*` | worked_area_body_map.html | session-compact | BodyMap | **OUT OF SCOPE** (`Sx_ASSET_03`) | oui | prototype (01.1) |

*(Aucun SVG supprimé/modifié dans cette session.)*

## 7. Catégories sémantiques (chaque concept → exactement une)
`navigation` · `action` · `status` · `information` · `trend` · `category` · `decorative` · `typographic-only`.

## 8. Règles anti-iconification (normatives — §13)
1. Une icône ne remplace pas un label métier ambigu. 2. Une métrique numérique n'a pas de pictogramme
systématique. 3. Un bouton critique garde un libellé visible. 4. Une icône décorative n'a **pas** de faux
accessible name. 5. Icône seule = contrôles **universels et répétés** uniquement. 6. Concept nouveau =
enseigné par texte avant abréviation. 7. Une carte n'a pas une icône par ligne. 8. **Aucun emoji** dans le
système. 9. **Aucune étincelle « IA »** pour Coach/reco. 10. **Aucune croix médicale/stéthoscope** pour Body
Intelligence. 11. **Aucune flamme** « intensité » sans mesure. 12. Aucun muscle isolé = mesure anatomique.
13. Aucune icône seule ne porte primary/secondary. 14. Aucune tendance par la couleur seule. 15. **Une
métaphore = un seul concept canonique** (et réciproquement).

## 9. Contrat de sélection (schéma par concept retenu — §14)
Champs : `semantic_id` · `category` · `label_fr` · `label_en_internal` · `user_intent` · `candidate_source` ·
`candidate_icon_name` · `candidate_style` · `candidate_version` · `candidate_file_path` · `fallback_text` ·
`visible_label_required` · `accessibility_role` · `allowed_surfaces` · `forbidden_surfaces` · `status` ·
`reason` · `alternatives_rejected` · `custom_gap_reason`.
- **`semantic_id`** : `auren.icon.<domain>.<concept>` (ex. `auren.icon.navigation.session`,
  `auren.icon.action.substitute`, `auren.icon.status.completed`, `auren.icon.trend.up`). **Jamais** le nom du
  vendor dans l'ID — le mapping vendor peut changer sans changer le contrat métier.

## 10. Statuts de sélection (bornés — §15)
`existing-runtime-keep` · `vendor-candidate` · `vendor-selected-for-intake` · `custom-gap-candidate` ·
`typographic-only` · `rejected` · `deferred`. **Aucun** concept `approved`/`integrated`/`legally-cleared`
dans cette spec.

## 11. P0 — intake obligatoire (subset minimal du prochain build)
Concepts dont une icône apporte une valeur démontrable **et** répétée. Candidats Tabler épinglés à `v3.45.0`
(nom outline vérifié existant au tag, cf. §14) :

| semantic_id | category | label_fr | source | candidate (Tabler v3.45.0 outline) | icône seule ? | statut |
|---|---|---|---|---|---|---|
| `auren.icon.navigation.session` | navigation | Séance | existing | *(inline actuel)* | non (label) | **existing-runtime-keep** |
| `auren.icon.navigation.programs` | navigation | Programmes | existing | *(inline actuel)* | non | **existing-runtime-keep** |
| `auren.icon.navigation.progress` | navigation | Progression | existing | *(inline actuel)* | non | **existing-runtime-keep** |
| `auren.icon.navigation.profile` | navigation | Profil | existing | *(inline actuel)* | non | **existing-runtime-keep** |
| `auren.icon.action.substitute` | action | Substituer | Tabler | `arrows-exchange` | non (label) | **vendor-selected-for-intake** |
| `auren.icon.action.timer-start` | action | Démarrer le repos | Tabler | `player-play` | oui (accessible name) | **vendor-selected-for-intake** |
| `auren.icon.action.timer-pause` | action | Pause repos | Tabler | `player-pause` | oui | **vendor-selected-for-intake** |
| `auren.icon.action.timer-reset` | action | Réinitialiser repos | Tabler | `rotate` | oui | **vendor-selected-for-intake** |
| `auren.icon.action.expand` | action | Déplier | Tabler | `chevron-down` | non | **vendor-selected-for-intake** |
| `auren.icon.action.collapse` | action | Replier | Tabler | `chevron-up` | non | **vendor-selected-for-intake** |
| `auren.icon.information.guidance` | information | Conseil | Tabler | `bulb` | non (label) | **vendor-selected-for-intake** (remplace `💡`) |
| `auren.icon.information.warning` | information | Avertissement | Tabler | `alert-triangle` | non (texte) | **vendor-selected-for-intake** (remplace `⚠`) |
| `auren.icon.status.completed` | status | Terminé | Tabler | `check` | non (texte) | **vendor-selected-for-intake** (remplace `✓`) |
| `auren.icon.action.menu` | action | Menu secondaire | Tabler | `menu-2` | oui (`aria-label`) | **vendor-selected-for-intake** (remplace `☰`) |

**Total P0 = 10 fichiers Tabler à vendorer** (les 4 nav restent inline, non comptés). ✅ **dans le budget
12-20** (§24). Chaque nom a été **vérifié existant** dans `icons/outline/` au tag `v3.45.0` (§14).

## 12. P1 — différé (utile, non nécessaire au 1ᵉʳ intake)
| semantic_id | label_fr | source candidate | raison différé |
|---|---|---|---|
| `auren.icon.trend.up` / `.stable` / `.down` | Tendance ↑/→/↓ | Tabler `trending-up` / `minus` / `trending-down` | tendance déjà exprimable par flèche+valeur textuelle ; icône = confort, pas nécessité |
| `auren.icon.status.excluded` | Exclu (historique) | Tabler `ban` ou `circle-off` | surface historique future |
| `auren.icon.status.substituted` | Substitué (historique) | Tabler `arrows-exchange` (réutilise action) | éviter double métaphore — à trancher au build |
| `auren.icon.category.history` | Historique | Tabler `history` | nav secondaire, label suffit aujourd'hui |
| `auren.icon.category.program` | Programme | Tabler `list-details` | catégorie, label suffit |

## 13. Typographic-only (rester texte — §12)
`kg` · `reps` · numéro de série · cible · **RIR** · durée précise · score numérique · **pourcentage** · noms
de zones · labels **primary/secondary** · **confidence score** (nombre + libellé). Justification : ce sont
des **valeurs**, pas des actions répétées ; une icône y ajouterait du bruit sans lever d'ambiguïté (règles
§8.2, §8.13).

## 14. Candidats Tabler (vérification au tag `v3.45.0`)
Tous les candidats P0 ci-dessus sont des noms **outline** dont l'existence au tag a été confirmée via l'API
(échantillon inspecté : `player-play`, `player-pause`, `arrows-exchange`, `chevron-down` → `<svg viewBox="0 0
24 24" fill="none" stroke="currentColor" stroke-width="2">`). **Doctrine de style** : **outline uniquement**
(filled interdit par défaut). Le subset final doit rester `viewBox 24 / stroke-width 2 / linecap round /
linejoin round / fill none / currentColor`. **Normalisation à déclarer en provenance** : strip des
commentaires d'en-tête Tabler (`tags:`/`category:`) ; harmonisation éventuelle `stroke-width` (l'inline actuel
est `1.7` ; Tabler est `2` — le build tranchera **une** valeur canonique et la déclarera). Les 4 nav inline
existantes **restent** (`existing-runtime-keep`) — pas de remplacement ce cycle.

## 15. Candidats Health Icons — **HEALTH ICONS NOT REQUIRED FOR P0**
Aucun concept P0 n'est corporel/anatomique non couvert par Tabler. Les candidats corporels (`body`, `arm`,
`leg`, joints, spine, skeleton) évoquent l'anatomie/pathologie et **médicaliseraient** Auren (§18.4) —
rejetés pour P0. La zone corporelle est déjà couverte par le **BodyMap** (`Sx_ASSET_03`), pas par une icône
générique. Verdict : **HEALTH ICONS NOT REQUIRED FOR P0** (source secondaire gardée éligible **CC0** pour un
éventuel besoin futur démontré, épinglée au commit `891ace7a…`).

## 16. Gaps custom (§19) — **CUSTOM GLYPH TRACK: NOT REQUIRED**
Test des 8 concepts candidats :
| Concept | Tabler adéquat ? | Texte suffit ? | Verdict |
|---|---|---|---|
| Body Intelligence | — | **oui** (label produit) | **CUSTOM GLYPH NOT JUSTIFIED** — le texte suffit (§20 : ni cerveau, ni étincelle) |
| Confidence score | — | **oui** (nombre + libellé) | **NOT JUSTIFIED** (typographic-only) |
| Zone worked | BodyMap couvre | oui | **NOT JUSTIFIED** (BodyMap = `Sx_ASSET_03`) |
| Substitution preserving pattern | `arrows-exchange` approche | oui (texte) | **NOT JUSTIFIED** — icône générique substitution + texte ; pas de glyphe destructif |
| Proposed overload | — | **oui** (texte `overload_hint`) | **NOT JUSTIFIED** |
| Substituted / excluded history | Tabler P1 | oui | **NOT JUSTIFIED** (P1 vendor) |
| Push/pull pattern | — | oui (texte) | **NOT JUSTIFIED** |

**Aucun gap custom démontré** → **`Sb_ASSET_02.2: NOT REQUIRED`** (réévaluable si un besoin futur émerge à
l'usage). Aucun glyphe n'est créé.

## 17. Concepts rejetés / à éviter (§20)
Interdits par défaut (exception = justification explicite fondée sur le contexte réel) : sparkles IA · robot
Coach · cerveau intelligence · stéthoscope/croix médicale/ECG/seringue/cœur médical (Body Intelligence) ·
flamme effort · éclair performance · trophée progression ordinaire · cible reco · bouclier confiance · œil
consultation · haltère devant chaque exercice · silhouette anatomique comme icône générique · **tout emoji**.

## 18. Accessibilité (§21)
- **Décorative** (texte adjacent) : `aria-hidden="true"` `focusable="false"`, 0 info supplémentaire.
- **Action + texte** : icône décorative, label porté par le bouton/lien, pas de répétition dans l'accessible
  name.
- **Icône seule** (timer play/pause/reset, menu) : `accessible name` requis · `title` jamais unique mécanisme
  · focus visible · **cible ≥ 44 px** mobile · état non porté par couleur · pas de tooltip requis pour l'action
  essentielle.
- **Statut** : toujours texte/contexte accessible. **Tendance** : forme/direction + valeur + texte, **jamais
  couleur seule**.

## 19. Surfaces (§23) — matrice d'usage
| Surface | Taille | Label visible | Icône seule ? | Densité max |
|---|---:|---|---|---|
| bottom-nav | 24 | **obligatoire** | non | 4 |
| desktop-rail | 20-24 | **obligatoire** | non | 4 (+secondaires labellisées) |
| secondary-nav | 20 | obligatoire | non | 1/entrée |
| session-console | 20-24 | oui (contrôles) | timer only (accessible name) | ≤3 |
| exercise-card | 16-20 | oui | non | ≤1 catégorie/ligne |
| sticky-cta | 20 | **obligatoire** | non | 1 |
| rest-timer | 24 | durée typographique | play/pause/reset icon-only OK | 3 contrôles |
| program-card | 16-20 | oui | non | ≤1 catégorie |
| history-row | 16 | oui | non | ≤1 statut |
| progress-card | 16-20 | oui | non | ≤1 catégorie (métriques typo) |
| body-intelligence | 16-20 | oui | non | ≤1 (texte primaire) |
| empty-state | 32-48 | oui | non-décoratif si texte insuffisant | 1 |
| form-feedback | 16 | oui | non | 1 (warning/completed) |

## 20. Tailles
Autorisées : **16 · 20 · 24** (usuel), **32/48** (empty-state). `stroke-width` canonique tranché au build
(cible **2**, cohérence contrat Auren). Optique cohérente entre tailles.

## 21. Budgets (§24)
Subset P0 cible **12-20 SVG** → **10 sélectionnés** ✅. Max sans arbitrage : 24. **≤ 2 Ko/icône optimisée** ·
**0** package npm runtime / webfont / CDN / sprite externe / JS d'icônes / SVG filled non gouverné · **1
copie canonique** par icône. Sélection **< 24** → pas de `SPEC BLOCKED — ICON SUBSET TOO BROAD`.

## 22. Stratégie de vendoring (préparée, non exécutée — §25)
Dossiers **gouvernés** (créés au build `02.1`, non maintenant) :
```
design/auren/source/icons/vendor/tabler/v3.45.0/outline/     # commit 975920ff…
design/auren/source/icons/vendor/health-icons/<commit>/outline/  # si besoin futur (891ace7a…)
design/auren/source/icons/custom/                            # vide tant que 0 gap
```
Export runtime éventuel `app/static/icons/functional/` **uniquement** après intake+provenance+licence+
validation+spec d'intégration (`Sb_ASSET_04.1`). **`design/` = source gouvernée ; `app/static/` ≠ autorisé.**

## 23. Provenance future (champs à renseigner au build — §26)
`asset_id` · `semantic_id` · `vendor` · `vendor_project` · `vendor_version` · `vendor_tag` · `vendor_commit`
· `upstream_path` · `upstream_blob_sha` · `access_date` · `license_spdx` · `license_source_path` ·
`usage_nature` · `modifications_planned` · `selected_by` · `review_status`. Le fichier téléchargé **devra être
comparé au blob officiel** (SHA) à l'intake.

## 24. Versioning (§27)
Épinglage **obligatoire** : tag officiel (**Tabler `v3.45.0`**), **commit SHA** (`975920ff…` ; Health Icons =
commit `891ace7a…` faute de tag), chemin upstream, version manifest Auren. **Interdits** : `latest`/`main`/
`master`/URL flottante/package non verrouillé/copie sans trace. Toute mise à niveau = nouvelle version subset
+ diff SVG + revue renommages/suppressions/licence + tests + human review.

## 25. Stratégie de migration des icônes inline (proposée, non exécutée — §28)
Recommandation à évaluer au build : **B/partials Jinja ou macros locales** contrôlées pour les icônes
`currentColor`, **sans** bibliothèque runtime ni loader JS (SSR/no-JS préservés). Les 4 nav inline actuelles
= **A (conserver)** ce cycle (comprises, cohérentes, accessibles). Les glyphes/emoji (`✓ ⚠ 💡 ☰`) →
remplacement futur par le subset vendored (partial). **Aucune implémentation dans la spec.**

## 26. Tests prévus pour `Sb_ASSET_02.1` (§29)
- **Manifest** : chaque SVG a une entrée · `semantic_id` unique · source/version/commit présents · licence
  renseignée · statut ≠ `approved` avant review.
- **Fichiers** : allowlist exacte · 0 fichier non manifesté · 0 raster · XML bien formé · `viewBox 0 0 24 24`
  · 0 `<script>` · 0 URL externe · 0 image embarquée · **0 hex** (currentColor) · 0 ID dupliqué · **≤ 2 Ko**.
- **Licence** : texte officiel présent · SPDX cohérent (Tabler `MIT`, Health Icons assets `CC0-1.0`) · chemin
  licence existant · provenance complète.
- **Sémantique** : 1 `semantic_id` → 1 fichier · 0 concept dupliqué · nom vendor **jamais** contrat métier ·
  **tous les concepts P0 ont une décision**.
- **Scope** : 0 `app/**` · 0 dépendance · 0 lock modifié · 0 runtime import. **Tests sans snapshot pixel**
  (assertions structurelles XML/attributs, pas de rendu bitmap).

## 27. Human review future du subset (§30)
Critères : lisibilité **16/20/24 px** · cohérence trait/optique · compréhension sans tooltip ·
non-médicalisation · non-gamification · cohérence Auren Terminal · contraste · focus · mobile 360 px · labels
visibles · **0 collision sémantique**. Previews générables au build `02.1`, **non intégrées au runtime**.

## 28. Gates (§35)
`ASSET INTEGRATION GATE: BLOCKED PENDING HUMAN / ANATOMICAL / LEGAL / MOBILE APPROVALS` — **inchangé**. Cette
spec rend `ICON INTAKE GATE: READY FOR Sb_ASSET_02.1` (**pas** `ASSET INTEGRATION GATE: OPEN`). Elle
n'autorise ni `app/static` · ni remplacement shell · ni modif manifest PWA · ni BodyMap · ni publication
commerciale.

## 29. Queue de builds (§34)
- **`Sb_ASSET_02.1` — Vendored Icon Subset & License Intake** : créera `AUREN_ICON_SEMANTIC_MAP.md` + subset
  **P0 (10 SVG Tabler v3.45.0)** + licences officielles (Tabler MIT) + provenance + manifest + tests +
  previews de revue. **0 `app/**`.**
- **`Sb_ASSET_02.2` — Custom Auren Functional Glyphs** : **NOT REQUIRED** (aucun gap démontré).
- **`Sx_ASSET_02` Closeout** : après `02.1` accepté (+ `02.2` non requis) + licences/provenance validées +
  human review.

## 30. Verdict
```
Sx_ASSET_02:
SPEC READY FOR COMMIT

ICON INTAKE GATE:
READY FOR Sb_ASSET_02.1

CUSTOM GLYPH TRACK:
NOT REQUIRED

ASSET INTEGRATION GATE:
BLOCKED (inchangé)
```

## Non-goals
Aucun SVG téléchargé/importé · aucun texte de licence copié · aucun `AUREN_ICON_SEMANTIC_MAP.md` (= build
`02.1`) · aucun glyphe custom · aucune modif `app/**`/`design/**`/`tests/**` · aucune dépendance/webfont/CDN ·
aucune ouverture de l'`ASSET INTEGRATION GATE` · aucune réouverture `Sx_ASSET_01`/`Sx_UI` · aucun fichier
Custom · aucun changement métier.

---

## Verdict

**Verdict :** 🟢 **Sx_ASSET_02: SPEC READY FOR COMMIT · ICON INTAKE GATE: READY FOR Sb_ASSET_02.1 · CUSTOM
GLYPH TRACK: NOT REQUIRED.** Vocabulaire visuel fonctionnel **minimal** défini (sémantique d'abord) : audit
runtime réel (8 SVG inline + glyphes/emoji non gouvernés), **10 concepts P0** couverts par **Tabler v3.45.0**
(commit `975920ff…`, MIT, format = contrat Auren exact), P1 différé, `confidence`/`RIR`/métriques =
**typographic-only**, **Health Icons NOT REQUIRED FOR P0** (distinction **CC0 assets / MIT code** enregistrée),
**0 gap custom démontré**. Versioning épinglé (tag + commit), provenance/tests/human-review préparés,
budget 10 ≤ 20 ✅. `ASSET INTEGRATION GATE` **reste BLOCKED** ; `Sx_ASSET_01`/`Sx_UI` restent **CLOSED**.
Aucune conclusion juridique absolue (evidence at access date, clearance = `02.1`).

**Prochaine action** (séparée, non commencée) : `GO COMMIT SPEC — Sx_ASSET_02 Functional Iconography
Selection`.
