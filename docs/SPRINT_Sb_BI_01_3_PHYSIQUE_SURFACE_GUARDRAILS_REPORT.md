# Sprint Sb_BI_01.3 — Physique Surface Guardrails

**Statut** : 🟢 DELIVERED — pending GO commit + CI + human review
**Type** : CODE BUILD — guardrails UI sur `/physique`, SSR/Jinja, mobile-first
**Date** : 2026-07-11
**Cycle** : Body Intelligence (reprise Sx_BI_01, Option B)
**Préconditions** : `Sb_BI_01.next` ACCEPTED ✅ · `Sb_BI_01.1` ACCEPTED ✅ · `Sb_BI_01.2` ACCEPTED ✅ · `body_intelligence_enabled` OFF prod ✅ (toutes vérifiées).

---

## 0. But produit

Encadrer la surface **live** `/physique` (score A/B/C + radar) pour éviter qu'elle
soit perçue comme la nouvelle vérité corporelle principale **avant** l'activation de
`/body/intelligence` : microcopy d'encadrement + rappel « lecture synthétique » +
rappel « non médical » + lien conditionnel vers `/body/intelligence` (si flag actif),
**sans toucher `compute_physique_dashboard`**.

---

## 1. Étape 0 — Brainstorming / Options / Choix retenu

### Options

| Option | Description | Verdict |
|---|---|---|
| **A** | Microcopy d'encadrement légère sur `/physique` | ✅ **RETENU** |
| B | Masquer score/radar | ❌ trop brutal, régression utilisateur |
| C | Rediriger `/physique` → BI | ❌ prématuré (flag OFF) |
| D | Modifier `compute_physique_dashboard` | ❌ **interdit** (service partagé leaderboard/user_profile) |

### 15 sujets clivants tranchés

1. Encadrer **près du score** (dans la card, sous grade/radar).
2. Parler de **« lecture synthétique »** + « score indicatif ».
3. **Pas** de lien si flag OFF (pas de lien mort 404).
4. Lien **uniquement si flag ON**.
5. Titre `/physique` **inchangé**.
6. Grade A/B/C **conservé** (pas masqué).
7. Radar **conservé** (pas masqué).
8. Score **non déplacé** sous les zones (option rejetée).
9. `compute_physique_dashboard` **non touché**.
10. Leaderboard + user_profile **préservés** (service intact).
11. Microcopy non médicale (fournie).
12. Encadrement **léger** (pas de re-densification).
13. Test **score non renforcé** (valeurs inchangées).
14. Test **BI non activée** (flag OFF → pas de lien).
15. Suite : `Sb_BI_01.activation`.

**Choix : Option A** — guardrails UI minimaux, route/service inchangés (hors passage du flag au template), prépare l'activation BI.

### Risques / parades

| Risque | Parade |
|---|---|
| Casser leaderboard/user_profile | **Ne pas toucher `compute_physique_dashboard`** ; test sentinelle |
| Lien mort 404 si flag OFF | lien **conditionnel** au flag serveur |
| Renforcer le score | microcopy le **relativise** (« indicatif »), aucun nouveau score |
| Re-densifier | 2 lignes de microcopy + 1 lien conditionnel, opacity sobre |

---

## 2. Fichiers modifiés

| Fichier | Nature |
|---|---|
| `app/routers/pages.py` | + `from app.config import get_settings` (ordre correct) ; route `/physique` passe `body_intelligence_enabled` au contexte |
| `app/templates/physique.html` | + bloc `.physique-guardrails` (microcopy + lien conditionnel), **sous** score/grade/radar inchangés |
| `tests/test_bi01_physique_guardrails.py` | **nouveau** — 9 tests |

**Non modifiés** : `muscle_scoring.py` (`compute_physique_dashboard` intact),
`leaderboard.py`, `user_profile.html`, `index.html` (Home), `body_intelligence.py`,
`body_intelligence.html`, partial zone card, modèles, migrations, JS. Aucune
nouvelle couleur (styles inline avec tokens `--space-*` + `text-mono` + `opacity`).

---

## 3. Microcopy ajoutée

- « **Lecture synthétique · Score indicatif, non médical.** »
- « Cette lecture agrège des signaux d'entraînement et d'exposition. La lecture
  détaillée par zones devient la surface principale lorsque Body Intelligence est
  activé. »
- Lien conditionnel (flag ON) : « **Voir la lecture par zones** » → `/body/intelligence`.

Wording interdit **absent** : diagnostic, body fat, morphotype, attractivité,
pathologie, score de santé, vérité corporelle, composition corporelle, bilan médical.

---

## 4. Comportement flag OFF / flag ON

| État | Comportement |
|---|---|
| **flag OFF** (défaut prod) | microcopy d'encadrement affichée ; **aucun lien** vers `/body/intelligence` (pas de lien mort 404) |
| **flag ON** (test / futur prod) | microcopy **+** lien « Voir la lecture par zones » → `/body/intelligence` |

Le flag est lu **côté serveur** (`get_settings().body_intelligence_enabled`) et passé
au template. **Config prod inchangée** (flag reste OFF).

---

## 5. Preuves : score / grade / radar / service intacts

- **score** (`.global-score`), **grade** (`.grade-badge`), **radar** (`.radar-wrap`)
  toujours rendus au-dessus de la microcopy (test `test_physique_keeps_score_grade_radar`) ;
- **valeurs inchangées** : la microcopy n'altère ni `dashboard.global_score` ni
  `global_grade` ni `radar_svg` ;
- **`compute_physique_dashboard` non touché** : test sentinelle
  (`test_muscle_scoring_not_modified_by_guardrails`) vérifie que le marqueur
  `physique-guardrails` n'apparaît **pas** dans `muscle_scoring.py` ;
- **leaderboard / user_profile intacts** : test sentinelle sur ces fichiers.

---

## 6. Tests

### `tests/test_bi01_physique_guardrails.py` (NOUVEAU, 9 tests)
1. **Rendu** : microcopy d'encadrement affichée · score/grade/radar conservés.
2. **Flag OFF** : pas de lien vers `/body/intelligence` (pas de lien mort).
3. **Flag ON** (client HTTP réel authentifié) : lien « Voir la lecture par zones » → `/body/intelligence`.
4. **Non-régression** : `compute_physique_dashboard` non modifié · leaderboard/user_profile/Home/BI templates intacts.
5. **Non-goals** : pas de JS.
6. **Wording interdit** absent.

### Résultats
- Dédiés : **9/9 verts**.
- **Broad sweep** (physique/muscle_scoring/leaderboard/user_profile/body_intelligence/bi01/progress/body_profile) : **301 passed, 0 failed** — aucune régression.
- `check_scope` = **ISOLATED** → **promu manuellement SHARED_CODE** (`pages.py` monté dans `main.py`, angle mort classifier). CI complète = source de vérité.
- ruff clean sur fichiers touchés, budget **543 ≤ 548** ; spec protocol vert.

---

## 7. Limites

- **Guardrails UI seulement** : le score A/B/C reste techniquement présent et
  identique (relativisé, pas retiré) — la dépréciation reste progressive.
- **Pas de dépriorisation nav** de `/physique` (futur).
- **Flag OFF prod** : le lien BI n'apparaît pas encore en prod (attend `Sb_BI_01.activation`).
- **CSS inline** (pas de fichier `physique.css` dédié ; `app.css` global hors périmètre) — cohérent avec le reste de `physique.html` qui utilise déjà `style="..."`.

---

## 8. Next

- **Human review** attendue (docs-only).
- Ensuite (sur GO séparé) : **`Sb_BI_01.activation`** Controlled BI Flag Activation
  (rendre `/body/intelligence` visible en prod) — **maintenant que `/physique` est
  encadré**, l'ordre validé en `.next` est respecté. Ou dogfooding terrain.

---

## Verdict

**Verdict :** 🟢 **Sb_BI_01.3 Physique Surface Guardrails — DELIVERED, pending GO commit + CI + human review.**

La surface live `/physique` est **encadrée** sans être cassée : microcopy « lecture
synthétique · score indicatif, non médical » relativise le score A/B/C **sans le
renforcer ni le masquer** ; lien vers `/body/intelligence` **conditionnel au flag**
(jamais un lien mort). Score/grade/radar **conservés** ; `compute_physique_dashboard`
**intact** (leaderboard + user_profile préservés, tests sentinelles) ; flag OFF prod
inchangé ; aucune nouvelle couleur / JS / modèle / migration / suppression. 9 tests
dédiés verts ; broad sweep 301 passed (0 régression) ; ruff clean, budget 543 ≤ 548 ;
spec vert. L'ordre `.next` est respecté : `/physique` encadré **avant** toute
activation BI.
