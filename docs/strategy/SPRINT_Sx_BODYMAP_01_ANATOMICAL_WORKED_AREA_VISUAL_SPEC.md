# Sx_BODYMAP_01 — Anatomical Worked Area Visual — SPEC

**Type** : SPEC ONLY / DESIGN DECISION — **NO CODE**
**Statut** : 🟢 SPEC RÉDIGÉE — **non commité** (attente GO), aucun build autorisé
**Date** : 2026-07-14
**Origine** : DOGFOOD_DEBRIEF_01 (commit `c21bd9c`), irritant #2 CONFIRMÉ
**Surface** : carte d'exercice active (`_partials/exercise_card.html`), bloc « Zone travaillée »

> Cette spec ne modifie aucun code. Elle **spécifie** le remplacement du visuel
> « Zone travaillée ». Le build fera l'objet d'un sprint ultérieur `Sb_BODYMAP_01.k`
> sous **BUILD AUTHORIZED** explicite.

---

## 1. Problème (terrain confirmé)

Le visuel actuel de « Zone travaillée » est un **blob abstrait décoratif**
(`session_focus.css:1547-1584`), volontairement **non-anatomique** pour éviter tout
claim médical. En salle réelle (DOGFOOD_DEBRIEF_01) : il **occupe de l'espace sans
transmettre d'information** — l'utilisateur attend une silhouette avec la zone
surlignée, il voit une forme arrondie qui ne « dit » rien.

**Objectif** : une visualisation qui aide réellement à **localiser la zone
travaillée**, tout en restant **explicitement non-médicale**, **SSR / Jinja / no-JS**,
sans activer Body Intelligence.

---

## 2. Fondations existantes (audit lecture seule — à réutiliser, ne rien réinventer)

| Élément | Emplacement | Rôle pour la spec |
|---|---|---|
| **11 zones canoniques** | `muscle_mapping.py` `ZONE_LABELS` | `pecs, delt_lat, delt_post, lats, upper_back, biceps, triceps, quads, posterior, calves, core` — les codes que la silhouette doit savoir surligner |
| **6 macro-axes** | `muscle_mapping.py` `RADAR_AXES` | `pecs · shoulders · back_width · back_thickness · arms · lower` — **regroupement naturel** pour un premier niveau de silhouette (moins de régions à dessiner que 11 muscles) |
| **Descriptor résolu** | `body_map_descriptor.py` `build_body_map_descriptor` | fournit déjà `primary_zone`, `secondary_zones`, `primary_label`, `status` (mapped/unknown) au template via `body_map_data[se.id]` |
| **Données template** | `exercise_card.html:116,122-123,147` | `_bmd.primary_zone` / `_zone_code` **déjà disponibles** côté Jinja — la silhouette n'a besoin d'aucune nouvelle donnée |
| **Relation DB Sx_32** | `ExerciseMuscleMapping (exercise_code, body_zone_code, role)` | source explicite primary/secondary/stabilizer si l'on veut surligner plusieurs zones (déjà backfillé primary+secondary) |
| **Ancre anti-claim** | `exercise_card.html:176` « Estimation indicative, non médicale. » | microcopy existante à **conserver/renforcer** |
| **Assets** | `app/static/icons/` (seul `favicon.svg`) | **aucune silhouette n'existe** → asset à créer de zéro |

**Conséquence clé** : le mapping code-zone → région-visuelle **existe déjà** (via
`primary_zone` + `RADAR_AXES`). Le build consiste à créer **un asset silhouette** +
**une correspondance région↔zone**, pas à refaire la résolution métier.

---

## 3. Étape 0 — Brainstorming / Options / Risques / Choix retenu (CLAUDE.md §3)

### 3.1 Options de visualisation

| Opt | Description | Pour | Contre |
|---|---|---|---|
| **A** | **Silhouette SVG inline mono-vue (face)** avec régions colorables par `currentColor`/classe CSS | SSR pur, no-JS, 1 asset, surlignage par classe zone | dos non couvert (delt_post/lats/posterior) |
| **B** | **Silhouette SVG inline double-vue (face + dos)**, rendue conditionnellement selon la zone | couvre 100 % des 11 zones, lisible | 2× le dessin, plus de CSS |
| **C** | **Sprite SVG `<use>`** (symboles réutilisables) | DRY, cache | complexité `xlink`, peu de gain à cette échelle |
| **D** | **Image raster (PNG) par zone** | simple à produire | non colorable, poids, non responsive net, N images |
| **E** | **Garder décoratif mais honnête** (pastille couleur/label seulement, retirer le blob) | quasi zéro effort, zéro claim | n'apporte pas la localisation demandée en salle |

### 3.2 Sujets clivants à trancher (proposés → décision recommandée)

1. **Face seule vs face+dos** → **face + dos** (Option B) : `delt_post`, `lats`,
   `upper_back`, `posterior` sont dorsales ; une face seule laisserait ~4/11 zones
   non localisables. **Rendu conditionnel** : n'afficher la vue dos que si la zone
   primaire est dorsale (évite d'afficher 2 silhouettes systématiquement).
2. **Granularité : 11 zones vs 6 macro-axes** → **6 macro-axes en V1** (regions =
   `RADAR_AXES`), surlignage primaire. Raison : 6 régions dessinables proprement,
   déjà mappées, extensible aux 11 plus tard. La finesse muscle reste au **texte**.
3. **Surlignage : primaire seul vs primaire+secondaires** → **primaire plein +
   secondaires en teinte atténuée** (données `_bmd.secondary_zones` déjà là),
   dégradable à primaire-seul si `status=unknown`.
4. **SVG inline vs `<img src>`** → **SVG inline** (Option B) : colorable par CSS,
   pas de requête réseau, cohérent no-JS/SSR, CSP-safe.
5. **Couleur de surbrillance** → réutiliser `var(--color-accent)` /
   `--color-accent-weak` (déjà utilisés par le blob actuel) → **aucune nouvelle
   couleur**, cohérence budget.
6. **Zone `unknown` / non mappée** → **silhouette neutre (aucune région
   surlignée) + texte « À qualifier »** ; jamais de région inventée (invariance
   #1, cohérent OQ-32-F « no anatomy invented »).
7. **`core` / `calves`** → présents dans la silhouette mais **basse priorité de
   dessin** (fallback macro-axe `lower` pour calves ; `core` = tronc central).
8. **Accessibilité** → la silhouette reste **`aria-hidden="true"`** (décor) ; **toute
   la sémantique reste portée par le texte** « Principal / Assistants / Pattern »
   (règle Sx_UI_06 D3 « une info = un seul endroit » **préservée**). Alt textuel
   déjà couvert par la liste.
9. **Non-médical explicite** → **conserver** « Estimation indicative, non
   médicale. » + la silhouette est **stylisée/schématique** (jamais planche
   anatomique) → pas de claim. Formes simplifiées, pas de détail musculaire réel.
10. **Emplacement du build** → asset dans `app/static/` (nouveau
    `body-silhouette.svg` ou SVG inline dans un **nouveau partial**
    `_partials/body_silhouette.html`), CSS dans `session_focus.css` (remplace les
    règles blob). Template : remplacer **uniquement** le bloc lignes 144-148 de
    `exercise_card.html`.
11. **Perf / poids** → SVG inline schématique < ~3 KB ; pas de JS ; pas de webfont.
12. **Fallback no-CSS** → si CSS absent, la silhouette ne doit pas casser la carte
    (SVG dimensionné, `aria-hidden`) ; le texte reste la source de vérité.

### 3.3 Risques & parades

| Risque | Parade |
|---|---|
| **Claim médical implicite** (silhouette = diagnostic) | silhouette **schématique** non-anatomique + microcopy « non médicale » conservée + `aria-hidden`. Zones = régions grossières, pas de muscles dessinés. |
| **Régression Sx_UI_06 D3** (dupliquer l'info zone) | silhouette **décorative aria-hidden** ; le texte reste l'unique porteur sémantique — pas de nouveau label dans le SVG. |
| **Zone non mappée → région fausse** | `unknown` → **aucune** région surlignée + « À qualifier ». Jamais d'invention (invariance #1 / OQ-32-F). |
| **Budget CSS / nouvelle couleur** | réutiliser `--color-accent*` existants ; pas de hex nouveau. |
| **Poids / réseau / CSP** | SVG **inline** (0 requête), pas de CDN, pas de JS. |
| **Casse tests asservis carte active** | auditer AVANT build les tests `session_focus` / `exercise_card` qui asservissent la structure `body-map` (leçon transverse batch). |

### 3.4 Choix retenu

**Option B — Silhouette SVG inline face + dos (rendu conditionnel), régions =
6 macro-axes `RADAR_AXES`, surlignage primaire plein + secondaires atténués,
`aria-hidden`, non-médical explicite, texte inchangé comme source de vérité.**
Fallback `unknown` = silhouette neutre + « À qualifier ». Aucune nouvelle couleur,
aucun JS, SSR/Jinja.

---

## 4. Spécification fonctionnelle (pour le futur build, NON exécutée ici)

### 4.1 Périmètre build (quand BUILD AUTHORIZED)
- **Nouveau** : asset silhouette (SVG inline schématique face+dos) + partial
  `_partials/body_silhouette.html` (paramétré par `primary_zone`, `secondary_zones`).
- **Modifié** : `exercise_card.html` — remplacer le bloc `body-map` (l.144-148) par
  l'inclusion du partial. **Rien d'autre touché** dans la carte.
- **Modifié** : `session_focus.css` — remplacer les règles `.session-focus__body-map*`
  blob par les règles silhouette (surlignage par classe `--zone-{macro_axis}`).
- **Aucun** service / route / modèle / data / migration touché (le descriptor fournit
  déjà `primary_zone`/`secondary_zones`).

### 4.2 Mapping région ↔ zone (V1, 6 macro-axes)
```
pecs         → région poitrine (face)
shoulders    → épaules (face pour delt_lat, dos pour delt_post)
back_width   → grand dorsal (dos)
back_thickness → haut du dos (dos)
arms         → bras (face: biceps? / dos: triceps? — V1: bras génériques)
lower        → cuisses/jambes (face quads, dos posterior, bas calves)
```
Vue **dos** rendue si `primary_zone ∈ {delt_post, lats, upper_back, posterior}`.

### 4.3 États
| Cas | Rendu silhouette | Texte (inchangé) |
|---|---|---|
| `mapped`, primaire connu | région primaire pleine + secondaires atténuées | Principal / Assistants |
| `mapped`, sans secondaires | région primaire pleine | Principal |
| `unknown` | silhouette **neutre**, aucune région | « À qualifier » |

### 4.4 Invariants non-négociables
- **`aria-hidden="true"`** sur la silhouette ; texte = seule source sémantique.
- Microcopy « Estimation indicative, non médicale. » **conservée**.
- **Aucune** zone inventée ; `unknown` ⇒ neutre.
- **No-JS**, SSR, SVG inline, CSP-safe, pas de nouvelle couleur.
- **Body Intelligence reste OFF** — cette carte est indépendante du flag.

---

## 5. Questions ouvertes — **TRANCHÉES** (opérateur, 2026-07-14)

| OQ | Décision | Implication build |
|---|---|---|
| **OQ-BM-A** — 6 axes vs 11 zones | **6 macro-régions visuelles**, **texte 11 zones conservé** | Silhouette = 6 régions colorables (`RADAR_AXES`) ; la liste texte « Principal/Assistants » garde la finesse `ZONE_LABELS` (11) — aucune perte d'info textuelle. |
| **OQ-BM-B** — biceps/triceps | Visuel macro **Bras** ; libellé texte garde **Biceps/Triceps** | Une seule région « bras » surlignée (face+dos) ; distinction fine reste au texte. |
| **OQ-BM-C** — core | **Core dessiné sobrement** sur le tronc (pas texte-only) | Ajouter une région tronc central (face), surlignage sobre ; reste `aria-hidden`. |
| **OQ-BM-D** — double-vue | **Face + dos TOUJOURS visibles** (pas de conditionnel) | 2 silhouettes côte à côte **systématiques** → lève l'ambiguïté dos/postérieur. **Densité mobile à surveiller** (2 SVG compacts, hauteur maîtrisée). |
| **OQ-BM-E** — asset | **SVG inline dans un partial Jinja** (V1), **aucun asset externe** | `_partials/body_silhouette.html` contient le SVG inline ; 0 fichier `static/*.svg`, 0 requête, CSP-safe. |

> Ces décisions **remplacent** les défauts recommandés du §3.4 là où elles diffèrent :
> - **D** : la double-vue est désormais **toujours affichée** (le §3.2-1 proposait
>   « conditionnelle » ; **arbitrage opérateur = face+dos systématiques**).
> - **C** : `core` est **dessiné** (le §3.2-7 le laissait basse priorité).
> Le §4 (spéc fonctionnelle) est à lire avec ces arbitrages : rendu **face+dos
> constant**, région **core** présente, région **bras** unique.

---

## 6. Definition of Ready (avant BUILD AUTHORIZED)
- [ ] OQ-BM-A→E tranchées.
- [ ] Tests asservis `session_focus`/`exercise_card` sur la structure `body-map`
      audités (liste des assertions impactées).
- [ ] Maquette silhouette validée (schématique, non-médicale).
- [ ] check_scope anticipé : `session_focus.css` + `exercise_card.html` partagés →
      **SHARED_CODE** (CI réelle = source de vérité).

---

## Verdict

**Verdict :** 🟢 **Sx_BODYMAP_01 — SPEC RÉDIGÉE, prête pour arbitrage.**

Le remplacement du visuel « Zone travaillée » est spécifié : **silhouette SVG inline
face+dos, régions = 6 macro-axes existants (`RADAR_AXES`), surlignage primaire +
secondaires atténués, `aria-hidden`, non-médical explicite, texte inchangé comme
source de vérité, SSR/no-JS, aucune nouvelle couleur, Body Intelligence OFF**. Les
fondations (11 zones, 6 axes, descriptor `primary_zone`/`secondary_zones`, relation
Sx_32) **existent déjà** — le build crée un asset + un mapping région↔zone, sans
toucher au métier. **Aucun code écrit**, aucun SVG ajouté, aucun template/CSS/service
/data/migration modifié. 5 questions ouvertes (OQ-BM-A→E) restent à trancher avant
**BUILD AUTHORIZED**.

**Recommandation** :
1. Trancher **OQ-BM-A→E** (ou déléguer les défauts recommandés).
2. **En parallèle** : fournir la **capture** de l'irritant #1 (`Delt_lat`) — indépendant
   de cette spec, débloque un éventuel micro-fix label.
3. Sur GO : ouvrir **`Sb_BODYMAP_01.1`** (BUILD AUTHORIZED) après audit des tests
   asservis. Tier attendu : **SHARED_CODE** (CI réelle obligatoire).
