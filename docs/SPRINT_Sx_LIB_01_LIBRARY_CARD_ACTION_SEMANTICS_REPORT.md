# Sprint Sx_LIB_01 — Library Card Action Semantics

**Statut** : 🟢 DELIVERED LOCALEMENT — **NON commité, NON poussé, CI non lancée** (LOCAL BATCH MODE)
**Type** : CODE BUILD — template-only semantic cleanup on `/library`, SSR/Jinja, no-JS
**Date** : 2026-07-13
**Cycle** : batch local (à la suite de Sx_CAT_01 / FB_01 / SUB_01 / CLOSEOUT_01 / 07.3 / 07.4 / 07_CLOSEOUT / TPL_01 — préservés)
**HEAD de référence** : `b60e749`

---

## 0. But produit

Rendre les cartes de `/library` **structurellement robustes** : clic sur la carte →
détail programme ; clic sur « Démarrer » → création de séance ; **plus de formulaire
POST imbriqué dans un lien `<a>`**. Correction HTML **sans changer le comportement
métier**.

---

## 1. Problème avant — form POST imbriqué dans un lien

`library.html` avait, par carte :

```html
<li>
  <a class="template-card__link" href="template_detail">
    …contenu…
    <form method="post" action="create_session"
          onclick="event.stopPropagation();"
          onkeydown="event.stopPropagation();">
      …hidden template_slug + creation_source=library + bouton Démarrer…
    </form>
  </a>   ← le form était DANS le lien
</li>
```

**Pourquoi c'est un bug de structure** : un `<form>` interactif (avec `<button>`) à
l'intérieur d'un `<a>` est **HTML invalide** — le comportement navigateur est indéfini
(le clic « Démarrer » pouvait déclencher la navigation du lien). D'où les **hacks**
`onclick/onkeydown="event.stopPropagation();"` pour empêcher la propagation. Fragile,
non-sémantique, et dépendant de JS inline pour un comportement de base.

---

## 2. Étape 0 — Brainstorming / Options / Choix retenu

### Options

| Option | Description | Verdict |
|---|---|---|
| **A** | Template-only semantic cleanup (sortir le form du lien + retirer stopPropagation) | ✅ **RETENU** |
| B | Template + CSS minimal | ❌ non nécessaire (mise en page inchangée) |
| C | Refonte complète des cards | ❌ trop large |
| D | Changer route/telemetry | ❌ hors sujet |

### 15 sujets clivants tranchés

1. **Corriger la structure** (form hors du lien).
2. **Sortir uniquement le form** (pas de refonte).
3. **`template-card__link`** conservé sur le bloc détail.
4. **`template-card__start`** conservé sur le form.
5. **Supprimer `onclick/onkeydown stopPropagation`** (inutiles une fois le form hors du lien).
6. **Pas de CSS** (le form reste enfant du `<li>` ; mise en page inchangée).
7. **`pages.py` non modifié.**
8. **`creation_source` inchangé** (library).
9. Bouton reste **`btn--ghost`** (brief).
10. Tests asservis library **préservés**.
11. **Mobile** : inchangé (mêmes classes) — voire plus robuste.
12. **Accessibilité clavier** : **améliorée** (form hors du lien = tab/enter cohérents, plus de hack JS).
13. **Pas de JS** — au contraire on **retire** 2 handlers inline.
14. **`/launcher` non touché.**
15. **Suite** : recommandation §9.

**Choix : Option A** — template-only, form sorti du lien, handlers retirés.

---

## 3. Structure après (valide)

```html
<li class="template-card …">
  <a class="template-card__link" href="template_detail">
    …contenu (name/kind/focus/cardio_note/suggested_label)…
  </a>                                    ← lien fermé AVANT le form
  <form method="post" action="create_session" class="template-card__start">
    <input type="hidden" name="template_slug" value="…" />
    <input type="hidden" name="creation_source" value="library" />
    <button type="submit" class="btn btn--ghost btn--sm">Démarrer</button>
  </form>
</li>
```

Le `<form>` est désormais **frère** du lien dans le `<li>` — HTML **valide**, **aucun
JS**, comportement identique (lien → détail, bouton → POST).

---

## 4. Preuve — comportement inchangé

- **Rendu réel** : 12 cartes, **0 `<form>` imbriqué dans un `<a>`** (heuristique regex
  sur le HTML rendu), `stopPropagation` **absent** du rendu, 12 boutons « Démarrer ».
- **Diff** : 18 insertions / 13 suppressions — le form + ses inputs sont **déplacés**
  (ré-indentés), pas modifiés ; `action`, `template_slug`, `creation_source=library`
  **identiques** (seule l'imbrication change).
- **End-to-end** : `test_cta_still_creates_session` poste le form → session créée (303/200).

---

## 5. Preuve — telemetry inchangée

`creation_source=library` (hidden, Sb_13) **conservé à l'identique** — le POST vers
`create_session` est byte-identique côté données. `test_recommendation_telemetry`
(`_creation_source == "library"`) **vert**. Aucun nouvel enum, `sessions.py` non touché.

---

## 6. Fichiers modifiés

| Fichier | Nature |
|---|---|
| `app/templates/library.html` | form sorti du `<a>` + `onclick/onkeydown stopPropagation` retirés (18 ins / 13 del — déplacement structurel) |
| `tests/test_library_card_action_semantics.py` | **nouveau** — 11 tests |

**Non modifiés** : `pages.py`, `sessions.py`, services, data (`reference_split.json` =
Sx_CAT_01), `launcher.html` (07.3), `template_detail.html` (07.4+TPL_01), session/progress/
history/index/BI/physique templates, models, migrations, static, app.css. **La readability
07.3 de `library.html` (lede « classées par usage ») est conservée** (le fix LIB_01 s'y
cumule).

---

## 7. Tests locaux

### `tests/test_library_card_action_semantics.py` (NOUVEAU, 11 tests)
- cartes rendues + lien détail · **LE FIX** : aucun `<form>` dans un `template-card__link`
  `<a>` (rendu réel) · `stopPropagation`/`onclick`/`onkeydown` absents (rendu + source) ·
  form/link **siblings** (`</a>` suivi de `<form`) · contrat form préservé (template_slug +
  creation_source=library + « Démarrer » ghost) · **end-to-end** (POST crée une session) ·
  vocabulaire library préservé · `pages.py` non modifié · pas de JS.

### Résultats locaux
- Dédiés : **11/11 verts**.
- **Tests asservis existants** (`test_library`, `test_library_launcher_readability` (07.3), `test_recommendation_telemetry`, `test_session_flow`) : **50 passed** — 0 cassé.
- **Sweep ciblé** (library/launcher/template_detail/create_session/telemetry) : **95 passed, 0 failed**.
- `check_scope` = **ISOLATED** (template + test). ruff clean, budget 543 ≤ 548 ; spec vert.

> **LOCAL BATCH MODE** : rapide, pas de full suite, pas de CI. Aucun commit/push.

---

## 8. Limites

- **Cleanup structurel seulement** : la mise en page visuelle est **inchangée** (mêmes
  classes) — on ne corrige que la validité HTML + on retire les hacks JS.
- **Pas de CSS** : si un futur besoin visuel émerge (séparer visuellement lien et bouton),
  ce serait un sprint dédié.
- **`/launcher`** : le form y était déjà bien structuré (hors lien) — non concerné.

---

## 9. Impact batch & recommandation

Ce sprint modifie `library.html` (déjà dans le batch via 07.3) — pas un fichier neuf, +
1 test. Le batch garde ses changements de code (data + templates + CTA + ce cleanup). Le
**plan de commit** (closeout) doit inclure `test_library_card_action_semantics.py` + ce
rapport dans le commit code.

**Recommandation finale : GO BATCH COMMIT + CI complète.** Le batch est mûr et vérifié ;
ce cleanup améliore la robustesse HTML/a11y sans risque. Fermer maintenant sécurise
l'ensemble via la CI réelle.

---

## Verdict

**Verdict :** 🟢 **Sx_LIB_01 Library Card Action Semantics — DELIVERED LOCALEMENT (batch, non commité).**

Le `<form>` de démarrage des cartes `/library`, auparavant **imbriqué dans le lien `<a>`**
(HTML invalide → hacks `stopPropagation`), est **sorti du lien** comme frère dans le `<li>` :
structure **valide**, **plus aucun JS inline**, accessibilité clavier + robustesse
améliorées. Comportement **strictement inchangé** (lien → détail, « Démarrer » → POST
`create_session`, `creation_source=library`) — prouvé end-to-end et par 50 tests asservis
verts (0 cassé). Template-only : `pages.py`/`sessions.py`/services/data/CSS **inchangés** ;
readability 07.3 conservée. 11 tests dédiés + sweep 95 passed ; ruff clean ; spec vert.
Batch préservé. Recommandation : **GO BATCH COMMIT + CI**.
