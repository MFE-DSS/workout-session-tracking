# Sprint Sb_32.next.worked-area-descriptor-ui — Worked Area consumes body_map_descriptor

**Statut** : 🟢 DELIVERED — pending GO commit + CI + human review
**Date** : 2026-07-09
**Cycle** : Sx_32 Deep Feature/Object Refactor — **premier consommateur visible** de `body_map_descriptor`
**Sb_32.1 / .2 / .3 / OPS.scope-guard** : ✅ tous HUMAN REVIEW ACCEPTED.
**Règle produit** : le mode séance reste souverain ; le Worked Area aide à comprendre « quelle zone je travaille » sans ralentir la saisie.

---

## 0. Étape 0 — Brainstorming / Options / Risques / Choix retenu

> Règle permanente : raisonnement documenté AVANT code. + **garde-fou `check_scope.py` exécuté avant les checks locaux.**

### Contexte

Sb_32.3 a livré `body_map_descriptor` (service pur, prouvé invariant 91/91) mais
**non branché**. Ce sprint le rend visible dans le Focus Mode / Worked Area, sans
migrer aucun consommateur métier, sans UI lourde, sans casser le logging.

### Audit du réel

- Le Worked Area vit dans `app/templates/_partials/exercise_card.html`, rendu
  **uniquement sur la carte active** (`{% if is_active %}`, contrat Sx_UI_04.3).
- Il était alimenté par `atlas_data[se.id]` (source `machine_atlas.json` : zone/name/
  description) avec des fallbacks **hardcodés** « à qualifier » pour Assistants/Stabilisation.
- La route `session_detail` (`app/routers/sessions.py`) construit déjà `atlas_data`
  dans une boucle `for se in session.session_exercises`.
- L'identité d'exercice = **`actual_exercise_name(se)`** (`substituted_name or
  exercise_name_snapshot`) — suit la substitution, déjà utilisée par muscle_scoring/
  session_recap. C'est le `name` à passer à `build_body_map_descriptor(name,
  exercise_code=name, db=db)` (convention Sb_32.2 `exercise_code = name`).

### Options comparées

| Option | Description | Verdict |
|---|---|---|
| **A** | Injection SSR minimale côté route : `body_map_data[se.id]` calculé dans la boucle existante, rendu dans le partial | ✅ **RETENU** |
| B | Appel du service directement depuis le template Jinja | ❌ REJETÉ : logique/DB dans le template, non testable proprement, anti-pattern |
| C | Endpoint/API + JS pour charger le descriptor | ❌ REJETÉ : casse le no-JS, endpoint interdit, friction |

### Évaluation

- **Friction UI** : nulle (SSR, valeurs déjà dans le HTML initial).
- **No-JS** : strict (rendu serveur).
- **Testabilité** : route + template testables via TestClient.
- **Périmètre** : route + 1 partial + tests — minimal.
- **Risque Focus Mode** : contrats logging/rest-timer/substitution préservés (non touchés).
- **Compat Sb_32.4** : la route calcule déjà le descriptor → réutilisable pour la bascule métier.

### Choix retenu

Option **A**. Descriptor calculé côté route via `actual_exercise_name`, injecté
en contexte, rendu dans le Worked Area. Labels primary/secondary réels ; unknown →
`"À qualifier"` ; `resolution_path` en `data-*` discret. Aucune UI lourde, aucune
illustration anatomique, microcopy non médicale.

### Résultat du garde-fou (`scripts/check_scope.py`)

Tier **`ISOLATED`** → `full_sweep_local` **skippé** ; broad sweep ciblé requis.
**Raffinement prudent documenté** : je modifie `exercise_card.html`, un template
**partagé** que le garde-fou (analyse d'imports Python) ne détecte pas. Par
conservatisme, j'ai élargi le broad sweep à **tout ce qui rend ce partial**
(`session/focus/mobile/cockpit/worked_area/substitution/overload`). La CI réelle
au push reste la source de vérité.

### Risques / limites

- Worked Area rendu **carte active seulement** (contrat Sx_UI_04.3 préservé) —
  les cartes non-actives restent compactées, sans descriptor.
- En **test** (DB `create_all` sans backfill Sb_32.2), `resolution_path =
  substring_fallback` ; en **prod** (DB migrée), `db_lookup`. Les deux donnent les
  **mêmes zones** (invariance 91/91 prouvée en `.3`).

---

## 1. Objectif

Rendre visible dans le Worked Area la zone corporelle **réellement résolue** par
`body_map_descriptor` : zone principale, assistants, état mapped/unknown, fallback
« À qualifier », `resolution_path` discret — SSR, no-JS, sans allégation médicale,
sans ralentir le logging.

---

## 2. Changements effectués

### 2.1 `app/routers/sessions.py` (MODIFIÉ)

- Import de `build_body_map_descriptor` + `actual_exercise_name`.
- Dans la boucle `for se`, calcul de `body_map_data[se.id] =
  build_body_map_descriptor(actual_exercise_name(se),
  exercise_code=actual_exercise_name(se), db=db)`.
- Ajout de `"body_map_data": body_map_data` au contexte template.

### 2.2 `app/templates/_partials/exercise_card.html` (MODIFIÉ, Worked Area seul)

- `{% set _bmd = body_map_data.get(se.id) ... %}` ; `_bmd_mapped = status == "mapped"`.
- Row **Principal** → `_bmd.primary_label` (fallback `_family.name` puis « À qualifier »).
- Row **Assistants** → `_bmd.secondary_labels | join(" · ")` si présents, sinon « À qualifier ».
- Chip de zone + forme CSS décorative pilotés par `_bmd.primary_zone` quand mapped.
- `data-resolution-path="..."` discret sur le conteneur (pas de badge technique intrusif).
- Note prudente : « **Lecture indicative issue du mapping exercice — repère
  d'entraînement, non diagnostic médical.** »
- Rôles renommés « Principal » / « Assistants » (microcopy brief). Classes Auren
  Terminal **inchangées**.

### 2.3 `tests/test_worked_area_descriptor.py` (NOUVEAU, 14 tests)

### 2.4 `tests/test_body_map_descriptor.py` (MODIFIÉ — tests d'isolation caducs remplacés)

Sb_32.3 avait 3 tests d'isolation **par git-diff** (`test_no_ui_file_touched`,
`test_no_consumer_file_touched`, `test_no_model_migration_schema_file_touched`)
qui affirmaient « ce sprint ne touche pas l'UI/les consommateurs ». Corrects pour
`.3` (sprint isolé), ils devenaient **caducs** dès qu'un sprint ultérieur touche
légitimement l'UI — ce qui est **exactement l'objet de `.next`**. Ils étaient
couplés au diff d'un autre sprint, un anti-pattern. Ils sont remplacés par des
invariants **permanents et stables** (indépendants du diff) : signature publique
du service + service reste **pur** (aucun `db.add/commit/delete`). L'intention
réelle de `.3` (le service lui-même ne change pas) est préservée. Édition
in-scope (le brief autorise `tests/test_*body_map_descriptor*`).

---

## 3. Rendu Worked Area (mapped vs unknown)

| Cas | Principal | Assistants | resolution_path | Note |
|---|---|---|---|---|
| Chest Press machine | **Pectoraux** | **Triceps** | db_lookup (prod) / substring_fallback (test) | présente |
| exercice inconnu | **À qualifier** | À qualifier | unknown | présente |

Rendu **carte active uniquement** (1 bloc worked-area par page). SSR strict :
tout le contenu est dans le HTML initial (no-JS).

---

## 4. Règles unknown / À qualifier

- `status == "unknown"` → « À qualifier » sur Principal, aucune zone inventée,
  slot propre et non anxiogène.
- `secondary_labels` vide → « À qualifier » sur Assistants.
- Stabilisation reste « À qualifier » (non peuplée par le descriptor V1).
- Aucune allégation médicale ; disclaimer prudent conservé.

---

## 5. Tests exécutés

### 5.1 `tests/test_worked_area_descriptor.py` — 14/14 verts

route injecte le descriptor (1) · known → primary label réel (2) · known →
assistants (3) · unknown → « À qualifier » (4) · aucun wording médical interdit +
note prudente présente (5) · no-JS contenu initial (6) · contrats Focus Mode
préservés — console/inputs/worked-area-list/rest-timer (7) · service
`body_map_descriptor` non modifié (8) · `muscle_mapping` non modifié (9) · aucun
model/migration/schema (10) · classes Auren Terminal préservées (11) · a11y section
nommée + labels textuels (12) · smoke carte active (13) · fallback unknown propre (14).

### 5.2 Garde-fou + checks (verts)

| check | résultat |
|---|---|
| `scripts/check_scope.py` | tier **ISOLATED** (full sweep local skippé) |
| `check_ruff_budget` | ✅ **541 ≤ 548** (aucune dette nette ajoutée) |
| `check_spec_protocol` | ✅ pass |
| broad sweep élargi (session/focus/worked_area/…) | ✅ (voir §Verdict) |

> Note ruff : `C901 session_detail too complex (25>15)` est **préexistant**
> (déjà dans le budget), non introduit par ce sprint (budget global inchangé 541).

---

## 6. Invariants préservés

- **Aucun changement** `classify_exercise` / `body_map_descriptor` / `muscle_mapping`
  / scoring / coach / body intelligence / substitution / readiness.
- **Aucun** modèle / migration / schema snapshot / endpoint / JS / rebrand / asset.
- Contrats Focus Mode (logging console, inputs, rest timer, substitution, overload,
  anchors) **préservés** (non touchés).
- Worked Area = carte active seulement (contrat Sx_UI_04.3).

---

## 7. Fichiers modifiés (whitelist respectée)

| Fichier | État |
|---|---|
| `app/routers/sessions.py` | MODIFIÉ (injection descriptor) |
| `app/templates/_partials/exercise_card.html` | MODIFIÉ (Worked Area seul) |
| `tests/test_worked_area_descriptor.py` | NOUVEAU |
| `tests/test_body_map_descriptor.py` | MODIFIÉ (tests d'isolation caducs → invariants stables) |
| `docs/SPRINT_Sb_32_next_WORKED_AREA_DESCRIPTOR_UI_REPORT.md` | NOUVEAU |
| `docs/strategy/SPEC_REGISTRY.md` · `ROADMAP_AND_NEXT_STEPS.md` | MODIFIÉS |

Zones interdites (services métier / models / migrations / schema / scripts /
.github / CLAUDE.md / .check-policy.json / deps) : **intactes**. Aucun artefact.

---

## 8. Limites (V1)

- Descriptor rendu **carte active** seulement (par contrat).
- `body_map_descriptor` non modifié (service `.3` réutilisé tel quel).
- Stabilisation non peuplée (aucune anatomie inventée).

---

## 9. Next step recommandé

- **Sb_32.4** : bascule des consommateurs métier (coach / body intelligence /
  scoring) vers le lookup DB + descriptor, prouvée non-régressive — **ou**
- **Closeout Sx_32 (partial foundation)** : acter que la fondation
  BodyZone/Muscle/Mapping/descriptor + 1er consommateur UI est livrée, et
  différer la bascule métier.

**Aucun des deux n'est ouvert dans ce sprint.**

---

## Verdict

**Verdict :** 🟢 **Sb_32.next.worked-area-descriptor-ui livré — 1er consommateur du descriptor branché, invariants préservés — pending GO commit + CI + human review.**

Le Worked Area du Focus Mode affiche désormais la zone corporelle **réellement
résolue** par le mapping Sx_32 (primary + assistants réels, « À qualifier » pour
l'inconnu), en SSR strict, sans allégation médicale, sans toucher au logging ni à
aucun service métier. Le garde-fou anti-overcheck a classé le sprint `isolated`
(full sweep local skippé, broad sweep élargi joué par prudence sur le template
partagé). Prêt pour GO commit ; la CI réelle fera foi de non-régression globale.
