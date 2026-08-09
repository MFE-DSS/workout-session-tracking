# SPRINT Sb_CUSTOM_PROGRAM_DOGFOOD_01 — Dogfood du cycle Custom Program (RAPPORT)

**Base canonique :** `ecb5b4b` · **Branche :** `sb/custom-program-dogfood-01` · **Tier :** ISOLATED (templates + tests ; **zéro migration · zéro code service/router**)
**Livré sous le protocole agentique** (`CLAUDE.md §4`) : `GO BUILD` → autonome jusqu'à `PR GREEN / MERGE PENDING`.

## 1. Méthode

Parcours produit complet du cycle Custom Program, surface par surface (SSR owner, no-JS) :
créer → générer une base → éditer séances/exercices → prévisualiser la qualité → valider → publier → lancer une séance publiée → nouveau cycle d'édition v+1 → republier v+1 → vérifier que les anciens v{n} restent privés/non-lançables. Lecture des 6 templates (`list`, `new`, `detail`, `generate`, `quality`, `publish`) et des routes de `app/routers/user_programs.py`.

## 2. Évaluation des critères dogfood

| Critère | Verdict |
|---|---|
| L'owner comprend l'état du programme ? | ⚠️ **friction F1** — badge en anglais brut (`draft`/`validated`/…) dans une UI FR → **corrigé** |
| L'action suivante est-elle évidente à chaque état ? | ⚠️ **friction F2** — après publication, aucun CTA pour lancer → **corrigé** ; ailleurs : OK (CTA publier/valider/générer/nouvelle version présents) |
| Les actions destructives/irréversibles sont-elles expliquées ? | ✅ OK — publication « définitive » (warning), régénération WIZARD_06 (3 chiffres + confirmation), édition d'un validé « repasse en brouillon » |
| Distinguer draft / validated / published / nouvelle version ? | ⚠️ partiel (F1) + `Version {n}` affichée → **corrigé** par les libellés FR |
| Trouver et lancer les séances publiées ? | ✅ OK (CTA « Démarrer cette séance » par séance sur le détail, PUBLICATION_03) + **F2** rend le chemin évident après publication |
| Le flux évite-t-il les impasses ? | ✅ OK après F2 (retour + CTA de lancement) ; toutes les pages ont un lien retour |
| Les anciennes versions publiées sont-elles invisibles sans confusion ? | ✅ OK (PUBLICATION_04 : v{n} privés/non-lançables/exclus `/library`) |
| Expérience mobile / no-JS acceptable ? | ✅ OK — formulaires POST natifs, `flex-wrap`, datalist no-JS, aucun JS requis |

## 3. Findings

| # | Sévérité | Constat | Décision |
|---|---|---|---|
| **F1** | **P1** | Le badge d'état rend la valeur DB brute (`draft`/`validated`/`published`/`archived`) — anglais technique dans une UI française — sur **5 surfaces** (`list`, `detail`, `publish`, `quality`, `generate`). | ✅ **CORRIGÉ** — macro FR partagée |
| **F2** | **P1** | Après publication, la page publish annonce que les séances sont lançables mais n'offre **aucun bouton** pour les atteindre (seulement « ← Retour au programme »). Le lancement vit sur le détail. | ✅ **CORRIGÉ** — CTA primaire « Voir et démarrer mes séances » |
| P2-a | P2 | La page publish montre le slug interne (`up1-…-v1-s1`) à l'owner. | ⏸️ **DIFFÉRÉ** — utile au support, non trompeur ; hors P0/P1 |
| P2-b | P2 | Un programme `archived` afficherait un état sans CTA (impasse). | ⏸️ **DIFFÉRÉ** — **inatteignable via l'UI** (aucune route archive/unarchive exposée) ; le corriger imposerait un flux d'archivage = hors périmètre |
| P2-c | P2 | Sur un programme publié, la liste des séances (avec « Démarrer ») ressemble à l'éditeur, sans titre « séances lançables » distinct. | ⏸️ **DIFFÉRÉ** — polish subjectif, non P0/P1 |

## 4. Fixes appliqués (templates uniquement)

- **F1 — libellés d'état FR** : nouveau partiel `app/templates/user_programs/_status.html` exposant une macro `status_label(status)` (`Brouillon`/`Validé`/`Publié`/`Archivé`, fallback = valeur brute pour un statut futur). Importée et utilisée dans `list.html`, `detail.html`, `publish.html`, `quality.html`, `generate.html`. **Un seul point de vérité** — aucune duplication.
- **F2 — CTA post-publication** : sur `publish.html`, à l'état `is_published`, ajout d'un CTA primaire **« Voir et démarrer mes séances »** vers `user_program_detail` (où vivent les boutons de lancement PUBLICATION_03). Le warning « publication définitive » de l'état publiable est **conservé**.

## 5. Fixes explicitement différés

P2-a (slug technique), P2-b (impasse `archived` — inatteignable, corriger = flux d'archivage hors périmètre), P2-c (heading « séances lançables ») — **aucun n'est P0/P1** ; les traiter dépasserait « small UX copy/layout/CTA » ou toucherait le modèle de cycle de vie. Aucun ne bloque le parcours.

## 6. Garanties (contraintes tenues)

**Zéro migration · zéro nouvelle table · zéro `WorkoutTemplate.user_id` · zéro exposition `/library` globale · zéro partage · zéro navigateur d'historique · zéro ASSET/BodyMap · zéro EKB_04 · zéro réécriture scoring/`session_builder` · zéro refonte UI · zéro refactor large · zéro changement de router/service.** Uniquement des templates (`app/templates/user_programs/`) + tests + docs.

## 7. Tests

`tests/test_user_program_dogfood_ux.py` — **8 passés** : libellé FR sur détail draft/validated/published, sur la liste, sur la page qualité (+ assertion « le brut ne fuit pas dans le badge ») ; CTA « Voir et démarrer mes séances » présent sur la page publish publiée **et** après le POST de publication ; warning « définitive » conservé sur l'état publiable (CTA de lancement bien réservé au publié).
Test existant mis à jour (`test_user_programs_http.py`) : l'assertion `"draft" in detail.text` devient `"Brouillon"` (conséquence directe de F1).

**Broad sweep ciblé** (user_program* + publish/launch/new_version/quality/generate/editor + library + session_builder + catalog_integrity) : **321 passés**.

## 8. Validation

check_scope **ISOLATED** (templates = feuilles + fichiers de test neufs ; full sweep local skippé par le garde-fou CLAUDE.md §1) · `check_spec_protocol` PASS · `check_ruff_budget` **543 ≤ 548** · `ruff check` fichiers touchés **clean**. CI PR = filet de vérité.

## Verdict

**Verdict :** 🟢 **Sb_CUSTOM_PROGRAM_DOGFOOD_01 — PATCH COMPLETE / PR PENDING.** Dogfood du cycle complet mené ; **2 frictions P1 corrigées** (libellés d'état FR sur 5 surfaces ; CTA de lancement post-publication), **3 P2 différées** avec justification. **Templates + tests uniquement — zéro migration, zéro exposition `/library`, zéro changement de service/router.** Merge = GO humain.

---
