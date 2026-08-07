# SPRINT Sb_CUSTOM_PROGRAM_PUBLICATION_02 — Nouveau cycle d'édition (RAPPORT)

**Base canonique :** `a4e54c5` · **Branche :** `sb/custom-program-publication-02` · **Tier :** SHARED_CODE (**zéro migration**)
**Spec :** [`Sb_CUSTOM_PROGRAM_PUBLICATION_02_SPEC.md`](strategy/Sb_CUSTOM_PROGRAM_PUBLICATION_02_SPEC.md)
**Livré sous le protocole agentique** (`CLAUDE.md §4`) : `GO BUILD` → autonome jusqu'à `PR GREEN / MERGE PENDING`.

## 1. Ce qui change

Un programme **publié** peut **démarrer un nouveau cycle d'édition** : le **même** `UserProgram` repasse en `draft` à `current_version + 1`, réutilisable via les flux WIZARD/éditeur existants. L'artefact publié v{n} (`WorkoutTemplate`) reste **immuable**.

## 2. Brainstorming / Options / Risques / Choix retenu (CLAUDE.md §3)

**Préflight = STOP + arbitrage.** Le libellé initial (« copie draft, original reste publié ») contredisait spec 04 §6-7 + spec 05 §6-7 (mono-row : le même row repasse en draft +1). Reporté à l'opérateur → **Option A retenue**.

| Option | Verdict |
|---|---|
| **A** mono-row : le même row → `draft` v+1 (spec-compliant) | ✅ **RETENU (opérateur)** — zéro migration/table/copie |
| **B** modèle « copie » (2ᵉ row, original reste publié) | ✗ contredit specs + OQ-PERS-D/OQ-LAUNCH-D (table différée hors V1) ; imposerait migration/table |

**Risques traités** :
1. **Double-incrément** → seul `published` incrémente ; après le 1ᵉʳ appel le statut est `draft`, le re-POST retombe en « déjà éditable ». *Testé (#3, #12).*
2. **Mutation d'artefact publié** → le service ne touche **jamais** une `WorkoutTemplate` (ni mutation ni suppression). *Testé (#8, #9).*
3. **Quality review** → aucune écriture au nouveau cycle (gel à la publication). *Testé (#10).*
4. **Lignée de version** → `current_version` sur le row (mono-row, aligné OQ-PERS-D). Liens de séance v{n} effacés ; templates v{n} orphelines survivent (archivage à la re-publication, hors scope).

## 3. Fichiers touchés (4 + docs)

| Fichier | Changement |
|---|---|
| `app/services/user_program_versioning.py` (**neuf**) | `start_new_edit_cycle` : published → draft v+1, efface `published_template_id`/`template_slug_snapshot`, garde l'arbre ; draft/validated = no-op idempotent ; archived = refus doux ; owner-scope 404 |
| `app/routers/user_programs.py` | import + `POST /programs/{id}/new-version` (303 éditeur / refus doux / 404) |
| `app/templates/user_programs/detail.html` | CTA « Créer une nouvelle version modifiable » **uniquement** si `status=published` |
| `tests/test_user_program_new_version.py` (**neuf**) | 14 tests (service + HTTP) |
| docs | spec + rapport + registry/roadmap |

## 4. Interdits tenus

Zéro copie / 2ᵉ row · zéro table de versions · **zéro migration** · zéro mutation/suppression de `WorkoutTemplate` · zéro unpublish · **zéro archivage** ce sprint · zéro `session_builder`/EKB_04/ASSET/BodyMap · PUBLICATION_01 réutilisé (import), non réécrit · zéro écriture de quality review.

## 5. Tests

`tests/test_user_program_new_version.py` — **14 passés** :
même-row transition (#1) · +1 exact (#2) · pas de double-incrément (#3) · pas de 2ᵉ row (#4) · arbre conservé (#5) · liens effacés (#6, #7) · templates v{n} inchangées (#8) et non supprimées (#9) · pas de quality write (#10) · owner-scope 404 (#11) · draft/validated/archived sans incrément (#12) · CTA uniquement publié (#13) · l'éditeur ouvre le brouillon retourné (#14). + refus foreign 404 · redirection non-auth.

**Broad sweep ciblé** (new_version + publish service/http + editor/generate http + drafts + quality reviews/preview + children_schema) : **171 passés**.

## 6. Validation

check_scope **SHARED_CODE** · `check_spec_protocol` PASS · `ruff check` **clean** · budget **546 ≤ 548**. Full sweep local non systématique (SHARED_CODE) — la CI PR parallélisée est le filet.

## Verdict

**Verdict :** 🟢 **Sb_CUSTOM_PROGRAM_PUBLICATION_02 — PATCH COMPLETE / PR PENDING.** Versioning **mono-row spec-compliant** : le même `UserProgram` publié → `draft` `current_version + 1`, liens de séance effacés, **templates v{n} intactes**, **zéro migration/copie/table/archivage/quality-write**. **Merge = GO humain.**
