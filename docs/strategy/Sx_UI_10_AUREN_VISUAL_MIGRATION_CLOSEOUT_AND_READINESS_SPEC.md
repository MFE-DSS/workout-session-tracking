# Sx_UI_10 — Auren Visual Migration Closeout & Visible Rebrand Readiness — SPEC

**Type** : SPEC / AUDIT / CLOSEOUT ONLY — **NO CODE**, docs-only
**Statut** : ✅ **FINAL STATUS — CLOSED** (voir section finale ; commité `49fa7d3`, closeout final ci-dessous)
**Date** : 2026-07-15
**Remplace** : le brouillon erroné « ORION » (non canonique, jamais committé, supprimé — voir §0.4)

> Cette spec **audite** et **planifie** ; elle n'insère aucun asset et ne modifie aucun fichier
> applicatif. Le rebrand visible est **produit uniquement** (surfaces user-facing), **jamais** le
> code/repo/packages/routes/models/DB.

---

## 0. Étape 0 — Brainstorming / Options / Risques / Choix retenu

### 0.1 Canon (non négociable)
- **SPIGNOS** = **repo / code / domaine technique** (modules, migrations, env vars, routes, models,
  tables, docs techniques). **Reste SPIGNOS.**
- **Auren** = **produit / nom visible cible** (ce que l'utilisateur voit).
- **Auren Terminal** = **identité visuelle** : graphite (dark), tout-mono système, **accent ambre
  unique `#C8A24B`**.
- **« Orion »** = erreur d'expression, **non canonique, abandonnée** — aucune entrée Orion ne subsiste.

### 0.2 Décision : **Option A** — Closeout visuel + readiness audit (Auren visible only)
| Option | Description | Verdict |
|---|---|---|
| **A** | Acter la migration Auren Terminal (closeout) + auditer la migration visible SPIGNOS→Auren ; **aucun renommage code/repo/package** | ✅ **RETENU** |
| B | Rebrand total code + repo maintenant | ❌ trop risqué, hors besoin produit |
| C | Insertion directe logos/icons/assets | ❌ auditer les surfaces + définir les assets d'abord |
| D | Attendre le dogfood avant tout audit Auren | ⚠️ partiel : le dogfood valide l'**UX séance**, pas l'**inventaire de marque** (qui peut avancer) |

### 0.3 Questions tranchées
| # | Question | Décision |
|---|---|---|
| 1 | Déjà terminé (Auren Terminal) ? | voir §2 (design system, re-skins, cockpit). |
| 2 | Reste avant migration visible totale ? | voir §3 (strings produit, PWA, auth, docs user, due diligence). |
| 3 | Surfaces affichant encore SPIGNOS ? | voir §4.A (base.html, welcome, science, atlas, coach_report, manifest générique). |
| 4 | Surfaces à garder SPIGNOS (internes) ? | voir §5 (repo, modules, migrations, env, routes, docs techniques). |
| 5 | Renommer le repo ? | **NON.** |
| 6 | Renommer packages/modules/env/routes/models/tables ? | **NON.** |
| 7 | Manifest PWA ? | migrer `name`/`short_name` (« Workout Session Tracking » → **Auren**). |
| 8 | Title PWA / apple title ? | `<title>` + `apple-mobile-web-app-title` → **Auren**. |
| 9 | Favicon / app icon / maskable ? | assets **Auren** (voir §6) — sprint PWA dédié. |
| 10 | welcome/login/register ? | pass Auren (title/brand/copy visibles) — §4.A. |
| 11 | Textes publics produit ? | « SPIGNOS » visible → **Auren** (science, atlas, coach_report, welcome). |
| 12 | Doc technique ? | **reste SPIGNOS** (interne). |
| 13 | Doc utilisateur ? | pass Auren (labels/copy) — §3. |
| 14 | Due diligence nom/domaine Auren ? | **pending** — gating avant tout public externe (§10). |
| 15 | Split de build Sx_UI_10 ? | voir §9. |

### 0.4 Nettoyage « Orion » (fait)
Les 2 fichiers `Sx_ORION_VISUAL_01_*` (non committés) ont été **supprimés** ; les entrées Orion
ajoutées localement à `SPEC_REGISTRY.md` / `ROADMAP_AND_NEXT_STEPS.md` ont été **restaurées à HEAD**.
`grep -R "ORION|Orion" docs/` = **0 occurrence**. Aucune trace canonique. Cette spec **reprend**
l'inventaire d'assets utile en le rattachant au canon **Auren** (pas « Orion »).

### 0.5 Risques
| Risque | Parade |
|---|---|
| Rebrand incomplet (patchwork SPIGNOS/Auren) | inventaire exhaustif §4 + closeout §11. |
| Confusion SPIGNOS/Auren | canon §0.1 : SPIGNOS interne / Auren visible, ligne nette. |
| PWA partiellement renommée | sprint PWA dédié `Sb_UI_10.2` (manifest + title + icons ensemble). |
| Auth pages anciennes | `Sb_UI_10.3` pass auth/welcome. |
| Asset pack non prêt | §6 inventaire ; production = agent artistique `docs/design/auren/**`. |
| Due diligence nom/domaine non tranchée | **gating** §10 avant public externe. |
| Dogfood UX non fait | indépendant (UX séance ≠ marque) ; ne bloque pas l'audit. |
| Renommer code par erreur | non-goal §7 formel. |

---

## 1. Définition stricte
- **SPIGNOS** = interne (code, repo, modules, migrations, env, routes, models, tables, docs techniques).
- **Auren** = visible (nom produit affiché à l'utilisateur).
- **Auren Terminal** = identité (graphite / mono / ambre `#C8A24B`).
- **« Orion »** = non canonique, abandonné.

---

## 2. Conclusion des sprints visuels déjà livrés (CLOSEOUT)

La migration **Auren Terminal** (identité visuelle) est **substantiellement livrée** :
- **`Sx_UI_02b` Auren Terminal** — design system graphite/mono/ambre, zéro webfont → **CLOSED**.
- **Home re-skin** · **Focus/séance re-skin** · **Shell/nav hardening** (topbar état actif `Sx_NAV_01`).
- **Session active cockpit** : BodyMap silhouette (`Sb_BODYMAP_01.1`) · console priority (`01.2`) ·
  previous-load (`01.3`) · alternatives below console (`01.2b`) · cues collapsed (`01.4`) — **tous ACCEPTED**.
- **Readability** : Progress (`Sx_UI_07.1`) · History (`07.2`) · Library/Launcher (`07.3`) · Template
  detail (`07.4`) — ACCEPTED.
- **PWA baseline partielle** (`Sx_UI_08.1`) · **Auth heads alignment partiel** (`Sx_UI_08.2`).

→ **L'IDENTITÉ visuelle (Auren Terminal) est acquise.** Ce qui reste = le **NOM visible** (SPIGNOS → Auren)
+ compléter PWA/auth/docs user. **Aucun renommage code.**

---

## 3. Ce qui reste à faire (gaps Auren)
- **Migration nom visible SPIGNOS → Auren** : **PENDING** (strings user-facing).
- **Renommage code/repo/packages/routes/models/DB** : **NON-GOAL explicite** (§7).
- **PWA icon/title/manifest Auren** : à auditer/produire (`name`/`short_name` génériques aujourd'hui).
- **Auth/welcome/public pages Auren** : à passer (title, brand, copy visibles).
- **Due diligence nom/domaine Auren** : **PENDING** (gating externe §10).
- **Assets Auren** : à inventorier (§6) — produits par agent artistique, intégrés par sprint code.

---

## 4. Inventaire des surfaces à auditer

### 4.A — surfaces affichant « SPIGNOS » visible (à migrer → Auren)
| Surface | Occurrence(s) | Action |
|---|---|---|
| `base.html` | `<title>… · SPIGNOS`, `apple-mobile-web-app-title=SPIGNOS`, `topbar__brand>SPIGNOS`, footer `<small>SPIGNOS` | → **Auren** (`Sb_UI_10.1`) |
| `welcome.html` | `<title>SPIGNOS`, `<h1>SPIGNOS`, apple-title, « Parcours SPIGNOS » | → **Auren** (`Sb_UI_10.3`) |
| `login.html` / `register.html` | `apple-mobile-web-app-title=SPIGNOS` | → **Auren** (`Sb_UI_10.3`) |
| `science.html` | « Comment SPIGNOS transforme… », « cockpit SPIGNOS » (×4) | → **Auren** (`Sb_UI_10.4`) |
| `atlas.html` | « …reviennent dans SPIGNOS » | → **Auren** (`Sb_UI_10.4`) |
| `coach_report.html` | « données saisies … dans SPIGNOS » | → **Auren** (`Sb_UI_10.4`) |
| `_partials/science_diagram.svg` | `<title>… modules SPIGNOS` | → **Auren** (`Sb_UI_10.4`) |
| `manifest.webmanifest` | `name: "Workout Session Tracking"`, `short_name: "Workout"` (ni SPIGNOS ni Auren) | → **Auren** (`Sb_UI_10.2`) |

### 4.B — autres surfaces à vérifier (audit à l'exécution)
home · session active · library/launcher/template detail · progress/history · body
intelligence/physique · emails éventuels · exports éventuels · docs utilisateur.

### 4.C — hors périmètre visible (exclure)
docs techniques historiques · specs d'architecture.

---

## 5. Surfaces à conserver SPIGNOS (internes — NE PAS toucher)
- **Nom du repo** · **noms de modules** (`app/…`) · **noms de migrations** · **variables
  d'environnement** existantes · **docs techniques historiques** · **références d'architecture** ·
  **URLs/routes** existantes (sauf décision explicite future distincte).

---

## 6. Assets Auren nécessaires (inventaire — production hors ce cycle)
| Asset | Format | Cible |
|---|---|---|
| favicon Auren | SVG | `app/static/icons/` |
| app icon 192 | PNG | manifest |
| app icon 512 | PNG | manifest |
| maskable icon 512 | PNG (safe zone) | manifest |
| apple-touch-icon 180 | PNG | head |
| monogramme Auren | SVG | brand/head |
| wordmark Auren | SVG | topbar brand / welcome |
| *(BodyMap V2)* | SVG inline | **hors Sx_UI_10** sauf besoin explicite |

Palette : **tokens Auren Terminal only** (accent `#C8A24B`, `#0f1115` PWA). **Pas d'asset « Orion ».**
Production = agent artistique borné à **`docs/design/auren/**`** ; intégration = sprint code.

---

## 7. Non-goals
- ❌ Aucun code ; aucun `app/**`, `tests/**`, `static/**`, `templates/**`, CSS modifié dans ce cycle.
- ❌ Aucun rebrand **code/repo/package/module/env/route/model/table/schema**.
- ❌ Aucun React / SPA.
- ❌ Aucun changement route/service/model/schema.
- ❌ Aucun deploy, aucun tag/release.
- ❌ Aucune activation Body Intelligence. ❌ Aucun fix Delt_lat sans capture.
- ❌ Aucune insertion d'asset hors sprint d'intégration dédié.
- ❌ Aucune réintroduction de « Orion ».

---

## 8. Risques
Voir §0.5 : rebrand incomplet · confusion SPIGNOS/Auren · PWA partiellement renommée · auth pages
anciennes · asset pack non prêt · due diligence nom/domaine non tranchée · dogfood UX non fait.

---

## 9. Plan de build recommandé (split Sx_UI_10)
| Sprint | Portée | Tier | Note |
|---|---|---|---|
| **`Sb_UI_10.1`** Visible Product Strings Audit/Fix | `base.html` (title/apple-title/brand/footer) → Auren | SHARED_CODE (base.html) | le plus visible ; template-only |
| **`Sb_UI_10.2`** PWA Manifest + App Icons Auren | `manifest.webmanifest` + `<link>` head + icons `app/static/icons/` | isolated→shared | **nécessite assets §6 prêts** |
| **`Sb_UI_10.3`** Public Auth / Welcome Auren Pass | welcome/login/register (title/brand/copy) | isolated (pages standalone) | pass texte + heads |
| **`Sb_UI_10.4`** User-Facing Docs / Labels Pass | science/atlas/coach_report + science_diagram.svg + docs user | isolated | strings produit visibles |
| **`Sx_UI_10` Closeout** | acter la migration visible complète | docs | après revue des 4 builds |

Chaque build code : template/CSS only, **aucun renommage code**, CI 3/3, revue.

---

## 10. Gating
- **Due diligence nom/domaine Auren** (disponibilité marque + domaine) **AVANT** tout domaine public /
  lancement externe. L'audit interne peut avancer sans elle ; la **bascule publique** l'exige.
- **Dogfood séance** (UX carte active) : indépendant, ne bloque pas le rebrand.
- **CI complète** sur chaque build code (3 jobs).
- **Docs-only commits** skippés par `paths-ignore: docs/**`.

---

## Non-goals (rappel structurel)
Aucun code · aucun rebrand code/repo/package · aucun React · aucun changement route/service/model/
schema · aucun deploy · aucune activation BI · aucun fix Delt_lat sans capture · aucune réintroduction
de « Orion ».

---

## Verdict

**Verdict :** 🟢 **Sx_UI_10 — SPEC RÉDIGÉE (Option A : closeout Auren Terminal + readiness audit rebrand
visible).** Le brouillon « Orion » (non canonique, jamais committé) est **supprimé** (0 occurrence
résiduelle). Le canon est fixé : **SPIGNOS interne / Auren visible / Auren Terminal identité**. La
migration **d'identité visuelle** (Auren Terminal) est **actée comme substantiellement livrée**
(design system + re-skins + cockpit séance + readability + PWA/auth partiels). Le **gap restant** est
le **NOM visible** (SPIGNOS→Auren) sur les surfaces user-facing (base.html, welcome/login/register,
science/atlas/coach_report, manifest PWA) + assets Auren (§6) + due diligence nom/domaine. **Aucun
renommage code/repo/package** (non-goal formel). Split proposé : `Sb_UI_10.1` strings → `.2` PWA+icons
→ `.3` auth/welcome → `.4` docs/labels → closeout. **Aucun asset inséré, aucun fichier applicatif
touché.**

**Recommandation** : **GO COMMIT SPEC** (docs-only) pour graver le canon + le plan. Premier build
recommandé : **`Sb_UI_10.1` Visible Product Strings** (le plus visible, template-only, sûr). En
parallèle : agent artistique sur `docs/design/auren/**` (assets §6) ; due diligence nom/domaine avant
tout public.

---

## FINAL STATUS — CLOSED

**Sx_UI_10 — CLOSED / HUMAN REVIEW COMPLETE** (2026-07-15).

Le plan de cette spec a été exécuté intégralement. Les 5 builds (`Sb_UI_10.1`/`.3`/`.4`/`.4b`/`.2`) sont
**human-review accepted**, chacun avec **CI 3/3 verte** (SHA exacts) ; le gate `Sb_UI_10.2a` a été
débloqué par arbitrage opérateur (glyphe haltère approuvé, `#f25f3a`→`#C8A24B`, path canonique inchangé).
La migration **visible** SPIGNOS→Auren est **complète** sur les surfaces couvertes : shell (`base.html`),
auth/welcome (welcome/login/register), docs (science/atlas/coach_report + science_diagram.svg), donnée
seedée rendue (`method_rules.json`), packaging PWA (manifest name/short_name « Auren » + pack d'icônes).
Les **non-goals sont préservés** (aucun renommage code/repo/package/route/model/table). **0 Orion
applicatif.** SPIGNOS reste volontairement le nom **interne**.

**Gate externe encore ouvert** : la **due diligence juridique / commerciale / domaine du nom Auren**
reste un **EXTERNAL OPEN ITEM** avant toute exposition ou lancement public à grande échelle. Elle ne
bloque pas ce closeout technique interne.

**Preuve complète** : `docs/SPRINT_Sx_UI_10_AUREN_VISUAL_MIGRATION_FINAL_CLOSEOUT_REPORT.md`
(matrice build/CI/review, audit des objectifs, non-goals, résidus classifiés, risques acceptés).

*L'intention historique ci-dessus (Option A, canon, split, inventaire) est conservée telle quelle ;
cette section n'ajoute que le statut final.*
