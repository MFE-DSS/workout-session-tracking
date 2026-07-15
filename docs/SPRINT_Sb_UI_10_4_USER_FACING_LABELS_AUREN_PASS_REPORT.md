# Sprint Sb_UI_10.4 — User-Facing Docs / Labels Auren Pass (SPIGNOS → Auren) — BUILD

**Statut** : 🟢 **CODE COMPLETE — CI PENDING — HUMAN REVIEW PENDING**
**Type** : CODE BUILD — surfaces documentaires (science/atlas/coach-report + SVG diagramme), **string-only pass**, SSR/no-JS
**Date** : 2026-07-15
**Spec** : `Sx_UI_10` — migration visible SPIGNOS → Auren (split `10.1` shell → `10.3` auth → **`10.4` docs/labels** ; `10.2` PWA/icons **BLOCKED BY ASSETS**)
**Baseline Git** : HEAD `0d01e1c` (== origin après alignement du commit concurrent 10.3 test-count, poussé en début de session)

> Ce sprint ne prétend **pas** ACCEPTED. CI et human review restent des étapes séparées.

---

## 1. État initial
- Branche `claude/sprint-reporting-fitness-app-V7Qr6`, HEAD de départ `0d01e1c` (aligné local==origin).
- Prérequis : `Sb_UI_10.1` (shell) + `Sb_UI_10.3` (auth) ✅ HUMAN REVIEW ACCEPTED.
- `Sb_UI_10.2` (manifest/icons) reste **BLOCKED BY ASSETS** — non commencé ici.

## 2. Baseline Git & anti-collision
Triple verrou anti-collision exécuté (avant modif / avant commit / avant push) : **origin stable ==
`0d01e1c`** aux 3 points. Voir §2bis pour les collisions de sessions détectées et l'arbitrage.

## 2bis. Anomalies — collision de sessions & arbitrage opérateur (2026-07-15)

- **Collision active** : deux sessions Claude ont travaillé simultanément sur `Sb_UI_10.4` dans le
  même working tree. Le build templates (8 chaînes) a été réalisé par une session pendant que l'autre
  auditait ; **deux fichiers de tests dédiés concurrents** ont existé transitoirement
  (`test_auren_user_facing_docs_strings.py`, 14 tests vs `test_auren_user_facing_labels.py`, 12 tests).
  Les deux sessions ont découvert **indépendamment** le même résidu data-seedé (§5) — convergence qui
  valide le diagnostic.
- **Arbitrage opérateur (verbatim)** : une seule session propriétaire de `10.4` ; **conservé** :
  `tests/test_auren_user_facing_labels.py` (guard template-wide + sentinelle résidu pinnée `== 1` +
  non-régression 10.1/10.3 + garde non-médicale) ; **supprimé** :
  `tests/test_auren_user_facing_docs_strings.py`.
- **Écart de séquence assumé** : le commit `7bdf4ba` a été poussé par la session parallèle **avant**
  réception de l'ordre d'arrêt (course de timing, non destructeur : contenu conforme, fichier de tests
  conservé = celui de l'arbitrage). Le présent complément docs (renommage du rapport vers le nom
  canonique mandaté `..._USER_FACING_LABELS_...`, cette section, `Sb_UI_10.4b` nommé) rétablit la
  conformité au mandat opérateur.

## 3. Matrice d'occurrences (inventaire)

| Fichier / ligne | Occurrence | Visible au rendu ? | Catégorie | Décision |
|---|---|---:|---|---|
| `science.html:4` (lede) | « Comment SPIGNOS transforme… » | oui | A PRODUCT_VISIBLE | → Auren ✅ |
| `science.html:39` | « SPIGNOS capture : durée, BPM… » | oui | A | → Auren ✅ |
| `science.html:70` (h2) | « Comment SPIGNOS materialise… » | oui | A | → Auren ✅ |
| `science.html:74` | « …SPIGNOS en fait une copie vivante… » | oui | A | → Auren ✅ |
| `science.html:115` (h2) | « Architecture du cockpit SPIGNOS » | oui | A (cockpit=produit) | → Auren ✅ |
| `atlas.html:4` (lede) | « …machines qui reviennent dans SPIGNOS » | oui | A | → Auren ✅ |
| `coach_report.html:245` | « …données saisies … dans SPIGNOS » | oui | A | → Auren ✅ |
| `science_diagram.svg:4` | `<title>Architecture des modules SPIGNOS` | oui (a11y) | A (`<title>` visible ; `id="diagram-title"` interne conservé) | → Auren ✅ |
| **`data/method_rules.json:13`** | « …score d'un exercice dans **SPIGNOS** est dérivé… » | oui (injecté sur /science) | **A mais DATA** | **OPEN / DÉFÉRÉ** (hors périmètre `data/**` §9) |

**Total : 8 chaînes template migrées ; 1 occurrence `data/` laissée OPEN.**

## 4. Occurrences migrées (8)
`science.html` (5) + `atlas.html` (1) + `coach_report.html` (1) + `science_diagram.svg` `<title>` (1).
Chacune = **remplacement chirurgical** SPIGNOS → Auren (aucun `sed` global ; contexte préservé).

## 5. Occurrences SPIGNOS conservées & justification
- **`data/method_rules.json:13`** — texte de règle de méthode **stocké en données** et injecté sur
  /science. **`data/**` est hors périmètre absolu (§9)** ⇒ **non modifié**. Classé **OPEN/DÉFÉRÉ** :
  la migration de cette chaîne relève d'un futur pass **données** (pas docs/labels). Une occurrence
  SPIGNOS reste donc rendue sur /science — **tolérée et documentée** (test sentinelle pinne
  **exactement 1** occurrence : `assert body.count("SPIGNOS") == 1` — elle ne peut ni croître ni
  disparaître silencieusement). **Micro-pass recommandé : `Sb_UI_10.4b` — Method Rules User-Facing
  Data String Pass** (1 chaîne dans `data/method_rules.json` ; `seed_method_rules` réécrit la table à
  chaque boot, sans version-gate → correction triviale et sûre, sur GO opérateur explicite).
- **Identifiants internes SVG** (`id="diagram-title"`, `id="diagram-desc"`, `viewBox`, `id="arrow"`)
  — techniques, **conservés**.
- **Base.html** commentaire technique « SPIGNOS reste le nom interne » — hors périmètre 10.4, non touché.

## 6. Fichiers modifiés
| Fichier | Nature |
|---|---|
| `app/templates/science.html` | 5 chaînes A→Auren (lede, cardio capture, 2 h2, paragraphe programmes) |
| `app/templates/atlas.html` | 1 chaîne A→Auren (lede) |
| `app/templates/coach_report.html` | 1 chaîne A→Auren (note footer l.245) |
| `app/templates/_partials/science_diagram.svg` | `<title>` A→Auren (`id` interne conservé) |
| `tests/test_science_page.py` | assertion de marque ré-orientée (« Comment SPIGNOS materialise » → « Comment Auren materialise ») |
| `tests/test_auren_user_facing_labels.py` | **nouveau** — 12 tests dédiés (surfaces rendues + sentinelle data OPEN) |

**Non modifiés** : `data/**`, manifest, favicon, assets, `app/static/**`, routers, services, models,
migrations, base.html, login/register/welcome, CSS, JS, `.github/**`. Aucun renommage interne SPIGNOS.

## 7. Comportements explicitement préservés
- Sens scientifique / biomécanique / concepts coach / atlas **inchangés** (seule la marque change).
- Structure + accessibilité du SVG (`viewBox`, `role=img`, `aria-labelledby`, `id`s) **intacte**.
- Routes `/science`, `/science/atlas`, `/coach-report` **inchangées** ; pages héritent toujours de base.html.
- Aucun calcul / champ / contrat backend / donnée touché.

## 8. Tests exécutés (validation locale)
- `test_auren_user_facing_labels.py` (12) + `test_science_page` + `test_atlas_routes` +
  `test_coach_report_body_snapshot` = **49 passed**.
- Occurrence `data/` correctement tolérée (sentinelle) ; 0 SPIGNOS dans les **templates** (source, hors commentaires).

## 9. Garde-fous exécutés
`check_scope` = **ISOLATED** (7 fichiers) — **non promu** : surfaces documentaires bornées (science/atlas/
coach), pas de shell partagé. ruff budget **543 ≤ 548** ; spec protocol **PASS** ; ruff test neuf clean.
**CI complète au push = source de vérité** (templates partagés utilisateurs → suite complète attendue).

## 10. Risques / ambiguïtés
- **`data/method_rules.json`** : 1 SPIGNOS produit rendu sur /science, **hors périmètre** (data), **OPEN**.
  À migrer dans un futur pass données si souhaité. Signalé, non traité silencieusement.
- Aucun autre cas ambigu (les 8 occurrences template sont sans équivoque de la marque produit).

## 11. Statut CI
**PENDING** — sera lancée au push ; verdict effectif des 3 jobs à confirmer avant toute annonce.

## 12. Éléments différés
- **`Sb_UI_10.2`** — PWA Manifest + App Icons Auren — **BLOCKED BY ASSETS**.
- **`Sx_UI_10` Closeout** — après déblocage de 10.2.
- **Dogfood Focus F1/F2/F3** — chantier séparé.
- **`Sb_UI_10.4b` — Method Rules User-Facing Data String Pass** — migration de la chaîne
  `data/method_rules.json:13` (hors 10.4, sur GO explicite).

## 13. Human review
**PENDING** — reste une session **séparée** (`GO VALIDATE Sb_UI_10.4`). Ce commit ne contient pas de revue.

---

## Verdict

**Verdict :** 🟢 **Sb_UI_10.4 — CODE COMPLETE (string-only pass, non encore CI/review).** Les 8 chaînes
produit visibles des surfaces documentaires (science ×5, atlas, coach-report, SVG diagramme `<title>`)
migrent SPIGNOS → **Auren**, sens scientifique et structure inchangés. **1 occurrence `data/method_rules.json`
laissée OPEN** (hors périmètre `data/**`). Aucun backend/route/manifest/asset/CSS/JS touché ; aucun
renommage interne ; identifiants SVG conservés ; zéro Orion. 12 tests dédiés + surfaces = 49 verts local.

**Recommandation** : GO COMMIT + CI (attendre le verdict effectif des 3 jobs), puis `GO VALIDATE`
(revue séparée). `10.2` reste bloqué (assets) ; migration `data/` = pass ultérieur distinct.
