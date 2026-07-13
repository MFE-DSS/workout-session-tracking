# Sprint Sx_TPL_01 — Template Detail Start CTA

**Statut** : 🟢 DELIVERED LOCALEMENT — **NON commité, NON poussé, CI non lancée** (LOCAL BATCH MODE)
**Type** : CODE BUILD — template-only functional CTA on template detail, SSR/Jinja, no-JS
**Date** : 2026-07-13
**Cycle** : batch local (à la suite de Sx_CAT_01 / FB_01 / SUB_01 / CLOSEOUT_01 / 07.3 / 07.4 / 07_CLOSEOUT — préservés)
**HEAD de référence** : `b60e749`

---

## 0. But produit

Permettre de **démarrer directement une séance depuis la fiche programme**
`/library/{slug}` sans repasser par `/library` ou `/launcher`. Réalisé **template-only**
en réutilisant `create_session` + la valeur telemetry `creation_source=library` déjà
whitelistée — donc **sans toucher `sessions.py`**.

---

## 1. Renversement de décision assumé (07.4 → TPL_01)

**Sx_UI_07.4** (dans le même batch, non commité) avait décidé : « fiche **descriptive**,
**pas de CTA** » (Option C rejetée, verrouillé par `test_no_post_form_added`).

**Sx_TPL_01 renverse cette décision** : la fiche devient **actionnable** (un CTA de
démarrage). Le batch n'étant **pas commité**, ce renversement se fait proprement dans le
même cycle : le test `test_no_post_form_added` de 07.4 est **ré-orienté** (pas affaibli,
pas masqué) vers la nouvelle vérité → `test_start_cta_form_present` (le form CTA EST
présent et légitime). Documenté ici **et** dans `SPRINT_Sx_UI_07_4_...REPORT.md`.

---

## 2. Étape 0 — Brainstorming / Options / Choix retenu

### Options

| Option | Description | Verdict |
|---|---|---|
| **A** | CTA template-only avec `creation_source=library` | ✅ **RETENU** |
| B | Ajouter `creation_source=template_detail` | ❌ toucherait `sessions.py` + whitelist |
| C | CTA haut + bas | ❌ bruit — un seul CTA clair |
| D | Pas de CTA | ❌ fiche = impasse UX |

### 15 sujets clivants tranchés

1. **Ajouter un CTA** (fiche actionnable).
2. **`creation_source=library`** (la fiche appartient au parcours catalogue/library ; valeur déjà whitelistée).
3. Placement : **après titre/focus/suggested_label/note fiche, avant la liste**.
4. **`sessions.py` non modifié** (template-only).
5. **Pas de confirmation** avant démarrage.
6. « ← Programmes » **conservé**.
7. **Pas de CTA secondaire launcher.**
8. Cartes exercices **non touchées**.
9. **Pas de JS.**
10. **Pas de CSS** (classes `btn btn--primary btn--sm` + `template-card__start` existantes).
11. Templates cardio : **même CTA** (pas de traitement différencié — un cardio peut se démarrer aussi).
12. **Double démarrage** : un seul CTA, pas de JS ; le risque relève du routeur existant (inchangé).
13. **Tests asservis** : `test_no_post_form_added` (07.4) ré-orienté ; telemetry/session_flow verts.
14. **Telemetry existante** : `creation_source=library` déjà géré (`test_recommendation_telemetry`).
15. **Suite** : recommandation §10.

**Choix : Option A** — CTA template-only, `creation_source=library`, un seul CTA.

---

## 3. Pourquoi `creation_source=library`

La fiche programme est **atteinte depuis `/library`** (lien « ← Programmes ») et
`/launcher` (lien « Détails → »). Elle appartient au **parcours catalogue**. La valeur
`library` est **déjà whitelistée** côté routeur (`test_recommendation_telemetry` :
`_creation_source(sid) == "library"`). La réutiliser :
- **évite de toucher `sessions.py`** (Option B rejetée) ;
- **évite un nouvel enum** telemetry ;
- garde la sémantique cohérente (démarrage depuis le catalogue).

---

## 4. Pourquoi `sessions.py` n'est pas modifié

`create_session` **accepte déjà** `template_slug` + `creation_source`, et la whitelist
**contient déjà `library`**. Le CTA n'a donc besoin **d'aucun** changement routeur : il
poste exactement ce que `/library` et `/launcher` postent déjà. **Template-only**, tier
ISOLATED.

---

## 5. Fichiers modifiés

| Fichier | Nature |
|---|---|
| `app/templates/template_detail.html` | + form POST CTA « Démarrer cette séance » (un seul) |
| `tests/test_template_detail_readability.py` | `test_no_post_form_added` → `test_start_cta_form_present` (**ré-orienté**, non affaibli) |
| `tests/test_template_detail_start_cta.py` | **nouveau** — 10 tests (dont end-to-end) |

**Non modifiés** : `sessions.py`, `pages.py`, services, data (`reference_split.json` =
Sx_CAT_01 préservé), `library.html`/`launcher.html` (07.3 préservés), session/progress/
history/index/BI/physique templates, models, migrations, static, app.css.

---

## 6. Comportement avant / après

| | Avant (07.4) | Après (TPL_01) |
|---|---|---|
| Fiche `/library/{slug}` | descriptive : lien retour + focus + note + structure, **aucun démarrage** | **actionnable** : + bouton « Démarrer cette séance » (POST `create_session`, `creation_source=library`) |
| Parcours | fiche → retour `/library` → carte → démarrer | fiche → **démarrer directement** |

**Conservé** : « ← Programmes », titre, focus, cardio note, suggested_label, empty state,
liste exercices (code/name/set_scheme/notes/rep_targets), notes readability 07.4.

---

## 7. Preuves du formulaire

```html
<form method="post" action="{{ url_for('create_session') }}" class="template-card__start">
  <input type="hidden" name="template_slug" value="{{ template.slug }}" />
  <input type="hidden" name="creation_source" value="library" />
  <button type="submit" class="btn btn--primary btn--sm">Démarrer cette séance</button>
</form>
```

- **1 seul** form `create_session` · **1** `creation_source=library` · **1** « Démarrer cette séance » (grep) — pas de double CTA.
- `template_slug` = `{{ template.slug }}` (hidden).
- **End-to-end** : `test_cta_creates_session_with_library_source` poste le form → session créée (303/200).

---

## 8. Tests locaux

### `tests/test_template_detail_start_cta.py` (NOUVEAU, 10 tests)
CTA présent · form POST → create_session · hidden `template_slug`+`creation_source=library`
· **un seul** CTA · **end-to-end** (POST crée une session) · contrat readability/data
préservé (← Programmes, exercise-list, rep ranges, notes 07.4) · garde cardio strength ·
non-goals (no JS/CSS, pas de valeur `template_detail`, `pages.py` non modifié).

### `tests/test_template_detail_readability.py` (07.4 ré-orienté)
`test_start_cta_form_present` remplace `test_no_post_form_added` — vérifie que le form CTA
est **présent** (un seul), reflétant la nouvelle décision. **11/11 verts.**

### Résultats locaux
- Dédiés TPL_01 : **10/10** · 07.4 (réorienté) : **11/11**.
- **Tests asservis existants** (`test_recommendation_telemetry`, `test_session_flow`, `test_library`) : **38 passed** — 0 cassé (telemetry `library` cohérente ; count « Démarrer » ≥6 satisfait).
- **Sweep ciblé** (template_detail/library/launcher/create_session/session_flow/telemetry) : **100 passed, 0 failed**.
- `check_scope` = **ISOLATED** (template + tests). ruff clean, budget 543 ≤ 548 ; spec vert.

> **LOCAL BATCH MODE** : rapide, pas de full suite, pas de CI. Aucun commit/push.

---

## 9. Chemins interdits vérifiés

✅ Aucun : `sessions.py`, `pages.py`, `services/**`, `models/**`, `migrations/**`,
`schema_snapshot.sql`, `static/**`, session/progress/history/index/BI/physique templates.
`reference_split.json` (CAT_01), `library.html`/`launcher.html` (07.3),
`test_catalog_integrity_cleanup.py` : **préservés, non modifiés** par ce sprint. **TPL_01
n'a touché que `template_detail.html` + les 2 tests template detail.**

---

## 10. Impact batch & recommandation

Le batch contient désormais **3 changements de code** (le CTA modifie `template_detail.html`
déjà dans le batch via 07.4 — pas un 4e fichier neuf) + le test réorienté + le test TPL_01.
Le **plan de commit** (closeout) doit inclure `test_template_detail_start_cta.py` +
ce rapport dans le commit code, et noter le renversement 07.4→TPL_01.

**Recommandation finale : GO BATCH COMMIT + CI complète.** Le batch est mûr (data +
templates readability + CTA fonctionnel) et vérifié localement. Fermer maintenant
sécurise l'ensemble via la CI réelle.

---

## Verdict

**Verdict :** 🟢 **Sx_TPL_01 Template Detail Start CTA — DELIVERED LOCALEMENT (batch, non commité).**

La fiche programme `/library/{slug}` devient **actionnable** : un CTA unique « Démarrer
cette séance » (POST `create_session`, `creation_source=library` déjà whitelisté) permet
de lancer la séance sans détour. **Template-only** : `sessions.py`/`pages.py`/services/
data **inchangés** ; aucun nouvel enum telemetry ; aucun JS/CSS/confirmation/double CTA.
Renversement assumé de la décision 07.4 (fiche descriptive → actionnable), test 07.4
**ré-orienté** (non affaibli). Données/textes/notes readability préservés. 10 tests
dédiés (dont end-to-end) + 07.4 11/11 + 38 asservis + sweep 100 passed ; ruff clean ;
spec vert. Batch préservé. Recommandation : **GO BATCH COMMIT + CI**.
