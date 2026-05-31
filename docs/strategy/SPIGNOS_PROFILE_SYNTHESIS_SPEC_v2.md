# SPIGNOS — Profile Synthesis Spec v2 (Sx_22b)

**Date :** 2026-05-09
**Type :** SPEC ONLY — refonte synthèse leaderboard + profil utilisateur.
**Prérequis :** Sb_19 livré (drilldown V1), Sx_21 méta-spec.
**Successeur build :** Sb_22b.
**Version :** v2 (v1 = Sx_19 Leaderboard Drilldown).

---

## A. Pourquoi v2

Sb_19 a livré : hover tooltip avec mini-radar 140×140 + page `/users/{username}` avec radar full + métadonnées.

**Retour dogfooding N2 (j+2) :**
- "le score au-dessus du radar et au centre fait doublon"
- "le hover doit montrer plus qu'une note — un mini hexagone qui montre la progression"
- "clic = profil avec synthèse, pas l'historique brut"
- "déterminer les détails idéaux pour faire la synthèse la plus courte et la plus efficace"

Diagnostic v1 vs v2 :
- v1 a livré le hover radar et la page profil **mais sans hiérarchiser** ce qui est utile pour la lecture rapide.
- v1 garde des redondances visuelles (score au-dessus du radar + dans le centre du radar).
- v1 n'a pas de **preview card** intermédiaire entre hover éphémère et clic full-page.

v2 vise la **synthèse à 3 niveaux** : ligne → preview card → page.

## A.bis — Hiérarchie 3 niveaux (verrouillée v2.1, contrat dur)

**Règle absolue :** chaque information n'apparaît qu'**au niveau le plus précoce où elle ajoute un signal**, et **jamais à un niveau plus tôt**. Aucune duplication ascendante. Tout build Sb_22b qui viole cette règle est rejeté.

| Niveau | Surface | Trigger | Vit ici (et nulle part ailleurs en double) |
|---|---|---|---|
| **L1 — Ligne** | `/leaderboard` ligne de tableau | toujours visible | rang · username · grade · score numérique · sessions/30j |
| **L2 — Preview card** | flottant 280×320 | hover desktop / double-tap mobile | mini-radar silhouette + 3-4 KPI courts (streak, cardio min/sem, volume Δ) + CTA "Voir profil →" |
| **L3 — Page profil** | `/users/{username}` | clic | radar full + score sous radar (1 fois) + métadonnées + agrégats 30j (top zone, neglected, pattern) + dernière séance |

Frontière dure :
- Score numérique : **L1 + L3 (sous le radar)**. **Jamais en L2** (badge grade L2 suffit). **Jamais au centre du radar**, sur aucun niveau.
- Radar : **L2 et L3 uniquement**. Toujours silhouette, sans score interne.
- Métadonnées (taille/poids/âge) : **L3 uniquement**.
- Activité (top zone, neglected zone, dernière séance) : **L3 uniquement**.

Cf §C pour la matrice complète.

## B. Modèle à 3 niveaux

### B.1 — Niveau 1 : Ligne du leaderboard (vue par défaut)

État actuel : `rang · username · grade · score · sessions/30j`.

Ajout v2 :
- Pas d'ajout — la ligne reste compacte. La densité existante est OK.

### B.2 — Niveau 2 : Preview card (NEW)

Déclenchée sur **hover desktop** *ou* **long-press mobile** *ou* **tap première fois** (mobile : 1 tap = ouvre preview, 2ème tap = navigue vers profil).

Contenu cible (carte ~280×320 px) :

```
┌──────────────────────────────┐
│ @username           [Grade]  │   ← header compact
│ ─────────────────────────────│
│   [mini-radar 200×200]       │   ← 30j, sans score au centre
│                              │
│ ─────────────────────────────│
│  Sessions 30j       12       │   ← 3-4 KPI courts
│  Streak             5j       │
│  Volume strength    +8 %     │   ← delta vs 30j précédents
│  Cardio min/sem     45'      │
│                              │
│ ─────────────────────────────│
│ Voir profil →                │   ← CTA
└──────────────────────────────┘
```

**Règles dataviz strictes (cf B3 dogfood) :**
- Score global **uniquement** dans le badge `[Grade]` du header. Jamais au centre du radar, jamais répété.
- Le radar est **silhouette pure** : axes, polygone, point. Pas de texte interne.
- KPI lignes : libellé court (≤ 16 chars) + valeur brute. Delta % en couleur si applicable.

### B.3 — Niveau 3 : Page `/users/{username}` (synthèse longue)

Refonte de la page Sb_19 actuelle :

```
┌──────────────────────────────────────────────┐
│  @username                          [Grade]  │
│  ──────────────────────────────────────────  │
│                                              │
│   [Radar 30j 360×360 — centré]               │
│                                              │
│   Score : 67/100                             │   ← une seule fois, sous le radar
│                                              │
│  ┌──────────┬──────────┬──────────┐          │
│  │ Sessions │ Streak   │ Cardio   │          │
│  │   12     │  5j      │  45'/sem │          │
│  └──────────┴──────────┴──────────┘          │
│                                              │
│  ─── Métadonnées ───                         │
│  178 cm · 78,5 kg · né 1992                  │   ← formats courts
│                                              │
│  ─── Activité 30j ───                        │
│  Top zone : Pecs (4 séances)                 │
│  Zone négligée : Lower (0 séance)            │
│  Pattern dominant : Push (45 %)              │
│                                              │
│  ─── Dernière séance ───                     │
│  Push A · il y a 2j · score 72               │
│                                              │
│  Voir activité publique (verrou) →           │   ← page activité plus tard
└──────────────────────────────────────────────┘
```

**Contrat de divulgation maintenu :**
- ❌ Pas de détails par exercice ni par set.
- ❌ Pas de notes libres.
- ✅ Métadonnées que l'user a explicitement renseignées (height, weight, year).
- ✅ Agrégats 30j (zones, patterns, fréquence).
- ✅ Dernière séance (template + score) — pas le contenu.

## C. Hiérarchie de l'information

| Bloc | Niveau 1 | Niveau 2 | Niveau 3 |
|---|---|---|---|
| Grade global | ✅ badge | ✅ badge | ✅ badge |
| Score numérique | ✅ texte | ❌ (redondant) | ✅ une fois sous radar |
| Radar 30j | ❌ | ✅ silhouette | ✅ full + axes labellés |
| Sessions 30j | ✅ | ✅ | ✅ |
| Streak | ❌ | ✅ | ✅ |
| Cardio min/sem | ❌ | ✅ | ✅ |
| Volume strength delta | ❌ | ✅ | ❌ (déjà vu N2) |
| Top zone | ❌ | ❌ | ✅ |
| Zone négligée | ❌ | ❌ | ✅ |
| Pattern dominant | ❌ | ❌ | ✅ |
| Métadonnées (taille/poids/âge) | ❌ | ❌ | ✅ |
| Dernière séance | ❌ | ❌ | ✅ |

Règle : chaque info apparaît **au niveau le plus précoce où elle apporte un signal lisible** et **jamais à un niveau plus tôt** (pas de duplication ascendante).

## D. Pattern preview-vs-clic mobile/desktop

| Geste | Desktop | Mobile |
|---|---|---|
| Hover sur ligne | Preview card s'affiche après 200ms | n/a |
| Tap court | Navigation `/users/X` | **1er tap : preview**, 2ème tap : navigation |
| Tap long (500ms+) | Preview en sticky | Preview en sticky |
| Échap / tap dehors | Ferme preview | Ferme preview |

L'**ambiguïté mobile** est volontairement résolue par le double-tap. Une icône `ⓘ` peut être ajoutée à droite de la ligne pour ouvrir directement la preview sans toucher le username (futur).

## E. Implémentation technique

### E.1 — Services à créer

- `services/profile_synthesis.py` :
  - `build_preview(user_id) -> PreviewPayload` — calcule les 3-4 KPI de niveau 2.
  - `build_page(user_id) -> PageSynthesis` — calcule les agrégats de niveau 3.
- `services/profile_metrics.py` (extrait de `stats.py`/`muscle_scoring.py`) :
  - `top_zone(user_id, days=30)`
  - `neglected_zone(user_id, days=30)`
  - `dominant_pattern(user_id, days=30)`
  - `cardio_min_per_week(user_id, days=30)`
  - `volume_delta(user_id, days=30)`

### E.2 — Templates

- `templates/_partials/profile_preview.html` (Niveau 2)
- `templates/user_profile.html` (refonte v2, sans changer l'URL)

### E.3 — Endpoint preview

- `GET /users/{username}/preview` → renvoie le HTML de la preview card (HTMX-style mais sans HTMX V1, juste fetch+innerHTML).

### E.4 — JS minimal

- Un seul fichier `app/static/js/preview.js` (~50 lignes) qui :
  - écoute hover/long-press sur `.leaderboard__user-link`
  - fetch `/users/{username}/preview`
  - injecte dans `.preview-portal` flottant
  - gère échap + click-outside

Pas de dépendance JS externe. SSR reste roi.

## F. Acceptance criteria Sx_22b

| Critère | Mesure |
|---|---|
| Score affiché 1 seule fois par niveau | Audit visuel V/V |
| Preview card chargée en < 300 ms | Mesure devtools |
| Niveau 2 fonctionnel desktop hover | Test manuel |
| Niveau 2 fonctionnel mobile tap-tap | Test manuel mobile |
| Contrat divulgation préservé | Test `test_user_profile_no_session_details` (existant Sb_19) |
| Page niveau 3 répond < 500 ms | Mesure |
| 0 régression leaderboard list | Tests Sb_19 verts |

## G. Risques

| Risque | Mitigation |
|---|---|
| Preview JS casse si fetch échoue | Fallback : tap = direct navigation à `/users/X` |
| KPI niveau 2 trompeurs sur compte récent | Afficher "Pas assez de données (< 30j)" au lieu de "0 %" |
| Tap-tap mobile confus | Tooltip discret "Re-tap pour ouvrir le profil" au premier tap |
| Charge BD profil leader → spike | Cache 5 min par username dans `services/profile_synthesis.py` |

## H. Migration de Sb_19 vers v2

- `compute_physique_dashboard()` reste — fournit le radar.
- `_DUMMY` data dans Sb_19 → remplacé par vrais KPI via `services/profile_metrics.py`.
- URL `/users/{username}` inchangée.
- Tests Sb_19 doivent rester verts (contrat de privacy + 404).

Pas de migration BD nécessaire.

## I. Lotissement build (Sb_22b)

| Lot | Sujet | Effort | Dépendance |
|---|---|---|---|
| Sb_22b.1 | `profile_metrics.py` + tests unitaires | 3 h | aucune |
| Sb_22b.2 | Refonte page `/users/{username}` (niveau 3) | 3 h | Sb_22b.1 |
| Sb_22b.3 | Endpoint `/preview` + partial | 2 h | Sb_22b.1 |
| Sb_22b.4 | JS preview.js + UX desktop/mobile | 3 h | Sb_22b.3 |
| Sb_22b.5 | Suppression score centre radar (fix complet B3) | 1 h | aucune |
| **Total** | | **12 h** | |
