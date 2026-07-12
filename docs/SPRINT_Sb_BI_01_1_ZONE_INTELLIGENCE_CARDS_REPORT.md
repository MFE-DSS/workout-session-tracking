# Sprint Sb_BI_01.1 — Zone Intelligence Cards

**Statut** : 🟢 DELIVERED — pending GO commit + CI + human review
**Type** : CODE BUILD — Body Intelligence UI activation, SSR/Jinja, mobile-first
**Date** : 2026-07-11
**Cycle** : Body Intelligence (reprise Sx_BI_01, Option A)
**Préconditions** : `Sx_BI_01` ACCEPTED ✅ · `Sx_TRANSFORM_01` ACCEPTED ✅ · `Sx_DOGFOOD_01` CLOSED ✅ (toutes vérifiées dans le repo).

---

## 0. But produit

Rendre Body Intelligence lisible, traçable, sobre et non médicale via une section
**« Lecture par zones »** sur la surface existante `/body/intelligence` : cards par
zone (volume récent, tendance, contribution, confidence), état vide sobre si données
insuffisantes, mention non médicale, **aucun score global opaque en tête**.

---

## 1. Étape 0 — Brainstorming / Options / Choix retenu

### Options

| Option | Description | Verdict |
|---|---|---|
| **A** | Enrichir `/body/intelligence` (flag existant) avec zone cards | ✅ **RETENU** |
| B | Modifier `/physique` | ❌ surface live avec score opaque, risque de casse |
| C | Widget Home | ❌ re-densifie Home (contraire Sx_UI_06 / Sx_TRANSFORM_01) |
| D | Full BI dashboard | ❌ trop large, trop dense |

### 15 sujets clivants tranchés

1. **Réutiliser `/body/intelligence`** (flag-off), pas de nouvelle route.
2. **Enrichir le template** existant (pas d'activation du flag en prod).
3. Cards **en tête** (après header, avant priorities/blocks).
4. Afficher **uniquement les zones avec volume** (hard_sets > 0) — pas 11 cards vides.
5. Zones sans données → **non affichées** ; si **aucune** zone → état vide sobre « Données insuffisantes ».
6. Pas de 2e score opaque : on **n'affiche pas** `ZoneScore.score` ni le grade A/B/C.
7. Réutiliser `ZoneScore` (muscle_scoring) **en lecture** ; contribution = **part arithmétique** (hard_sets zone / total), pas un score.
8. Confidence = **badge texte** (« Confiance élevée/moyenne/faible »), déjà dans ZoneScore.
9. Tendance = **flèche sobre** ↑/→/↓ (déjà dans ZoneScore), neutre, sans sur-interprétation.
10. `/physique` **inchangé** ; on ne le touche pas.
11. **Pas de lien** poussant vers le score opaque de `/physique`.
12. **Auren Terminal** : tokens sémantiques existants, **aucune nouvelle couleur** ; flèche tendance neutre (`--fg-dim`) = un seul accent respecté.
13. Microcopy : « Estimation non médicale. » / « Données insuffisantes ».
14. Test garantissant **pas de score /100, pas de grade, pas de radar** dans la section.
15. **Flag inchangé** (`body_intelligence_enabled=False` en prod) ; activation **en test uniquement** (fixture `BODY_INTELLIGENCE_ENABLED=1`).

**Choix : Option A** — enrichir `/body/intelligence`, réutiliser `ZoneScore`, aucun nouveau score, aucun radar, aucun widget Home, flag existant respecté.

### Risques / parades

| Risque | Parade |
|---|---|
| 2e score opaque | on n'affiche ni `score` ni `grade` ; test le verrouille |
| Re-densification (11 cards vides) | zones sans volume droppées ; état vide sobre |
| Contamination substitution | volume par zone via `classify_exercise` (identité d'exercice) — héritage Sx_DOGFOOD_01 |
| Casser `/physique` | lecture seule de `compute_physique_dashboard` ; `/physique` non touché ; test de régression |
| Nouvelle couleur | uniquement tokens Auren Terminal existants |

---

## 2. Surface activée

**`/body/intelligence`** (route canonique existante, flag `body_intelligence_enabled`).
La section « Lecture par zones » s'insère **en tête** des blocs du composer. **Le flag
reste OFF en prod** (défaut inchangé) — la surface reste invisible jusqu'à décision
explicite d'activation. Les tests activent le flag via fixture (`BODY_INTELLIGENCE_ENABLED=1`),
jamais en config prod.

---

## 3. Données réutilisées (aucun nouveau score)

Source : `muscle_scoring.compute_physique_dashboard(db, user_id, window_days=30)` →
`list[ZoneScore]`, **appelé en lecture depuis le router** (lieu d'orchestration).
Champs réutilisés par card :

| Card | Source `ZoneScore` |
|---|---|
| Nom de zone | `label` |
| Volume récent | `hard_sets` + `session_count` |
| Tendance | `trend` (up/down/stable) |
| Confidence | `confidence` (élevée/moyenne/faible) |
| **Contribution** | **dérivée** : `round(100 × hard_sets / Σ hard_sets)` — part arithmétique traçable, **pas un score** |

**Jamais affichés** : `ZoneScore.score` (0..100), `PhysiqueDashboard.global_grade`
(A/B/C), `radar_svg`. Le score opaque existe dans la donnée mais **n'est pas surfacé**.

---

## 4. Fichiers modifiés

| Fichier | Nature |
|---|---|
| `app/routers/body_intelligence.py` | + `_build_zone_cards(list[ZoneScore]) -> list[dict]` (présentation, part relative dérivée) ; injecte `zone_cards` dans le contexte via `compute_physique_dashboard` en lecture |
| `app/templates/body_intelligence.html` | + section « Lecture par zones » en tête ; état vide sobre ; note non médicale |
| `app/templates/_partials/body_intelligence_zone_card.html` | **nouveau** — card par zone (label, volume, tendance, contribution, confidence) |
| `app/static/css/body_intelligence.css` | + styles `.zone-card*` Auren Terminal (tokens existants), mobile-first, média ≤360px ; **aucune nouvelle couleur** |
| `tests/test_bi01_zone_intelligence_cards.py` | **nouveau** — 12 tests |

**Non modifiés** : `muscle_scoring.py` (lecture seule), `physique.html`, `index.html`
(Home), modèles, migrations, `/physique`, JS.

---

## 5. Ce qui reste flag-off

`body_intelligence_enabled=False` reste le **défaut prod** — la surface (et donc les
zone cards) reste **invisible** jusqu'à une décision d'activation explicite. Aucune
config prod modifiée.

---

## 6. Non-goals respectés

Aucun : modèle · migration · schema · `index.html`/Home · session focus · overload ·
substitution · recommendation · coach_report · `/physique` (sauf lecture de son
service, sans le modifier) · leaderboard · JS · React/SPA/bundler · **nouveau score
global** · radar V1 · rebrand · deploy · release tag. Aucune nouvelle couleur. Aucun
claim médical.

---

## 7. Tests

### `tests/test_bi01_zone_intelligence_cards.py` (NOUVEAU, 12 tests)
1. **Route/flag** : 404 si flag off (client dédié) · rend les zone cards si flag on + données.
2. **Contenu cards** : volume (« séries ») · confidence (« Confiance ») · mention « Estimation non médicale. » · contribution (« % du volume »).
3. **Pas de score opaque** : la section zones ne contient ni radar, ni /100, ni grade, ni « note globale », ni « score global ».
4. **Données insuffisantes** : état vide sobre, aucune card, aucun chiffre inventé.
5. **Non-goals** : pas de `<script>`/`onclick` · router réutilise ZoneScore sans lire `.score`/`.global_grade` · Home non touchée.
6. **Régression** : `/physique` ne référence pas le partial zones · limites non médicales du composer conservées.
7. **Wording interdit** : ni diagnostic, body fat, morphotype, attractivité, pathologie.

### Résultats
- Dédiés : **12/12 verts**.
- **Broad sweep** (body_intelligence/muscle_scoring/physique/progress/body_map/body_profile/leaderboard) : **284 passed, 0 failed** — aucune régression.
- `check_scope` = **ISOLATED** (classifier) → **promu manuellement SHARED_CODE** : `body_intelligence.py` est monté dans `main.py` via l'import groupé que le classifier ne reconnaît pas (angle mort connu). Broad sweep élargi en conséquence.
- ruff : **mes fichiers clean** ; budget **543 ≤ 548** (les 6 warnings de `muscle_scoring.py` sont **préexistants** — fichier non touché). spec protocol vert.

---

## 8. Limites

- **Score opaque de `/physique`** toujours présent sur sa surface (non touché) ; la décision produit (garder/encadrer/déprécier) reste à cadrer (`Sb_BI_01.next`).
- **Muscle table vide** (OQ-32) : lecture au niveau **zone** uniquement, pas d'anatomie fine.
- **Zones secondaires** peu peuplées (corpus improvement non bloquant, différé) — le volume affiché est le **primaire** via `classify_exercise`.
- **Flag off en prod** : la surface n'est pas visible tant que l'activation n'est pas décidée.
- `top_exercises` réutilisé mais **non affiché** en V1 (réservé au drill `Sb_BI_01.2`).

---

## 9. Statut futur

- **Human review** attendue (docs-only).
- **Dogfooding** : le dogfooding terrain Sx_DOGFOOD_01 reste pending ; la validation visuelle des zone cards (mobile étroit, flag on en test) suivra.
- **Deploy** : deferred until explicit GO (et décision d'activation du flag).
- **Suite** : `Sb_BI_01.2` drill zone → détail (top exercices, historique volume) ; `Sb_BI_01.next` décision score `/physique`.

---

## Verdict

**Verdict :** 🟢 **Sb_BI_01.1 Zone Intelligence Cards — DELIVERED, pending GO commit + CI + human review.**

La surface `/body/intelligence` gagne une section **« Lecture par zones »** sobre et
traçable : cards par zone (volume récent, tendance, contribution, confidence) en tête
des blocs, état vide sobre si données insuffisantes, mention non médicale. Réutilise
les signaux `muscle_scoring ZoneScore` **en lecture** — **aucun nouveau score**, le
score opaque `.score`/A-B-C **jamais surfacé** ; aucun radar, aucun widget Home, aucune
nouvelle couleur (Auren Terminal), aucun modèle/migration/JS/mutation métier ; flag
`body_intelligence_enabled` **inchangé** (off en prod). 12 tests dédiés verts ; broad
sweep 284 passed (0 régression) ; ruff clean sur mes fichiers, budget 543 ≤ 548 ;
spec protocol vert.
