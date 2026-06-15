# Sx_29 — Mobile Session Focus Mode & Visual Interaction Layer (SPEC ONLY)

> **Statut :** SPEC ONLY ouvert sous **human override #2** (sprint `Sb_28.override-build-authorization`, 2026-06-15) qui autorise **Option A uniquement** parmi les 5 options Sx_28. Dogfood Sx_27 reste **PENDING** — non simulé, non considéré acquis. Si dogfood arrive plus tard avec un signal différent, peut imposer un fix avant `Sb_29.1` via `Sb_28.dogfood-integration`. React production **INTERDIT** Sx_29. Voir §3.

**Auteur :** opérateur SPIGNOS + Claude Code (Opus 4.7).
**Date :** 2026-06-15.
**Version :** v1.
**Spec parente d'autorisation :** `docs/strategy/Sx_28_PRODUCT_ROADMAP_RECONCILIATION_SPEC.md §15.1bis + §16.bis + §20`.
**Source de vérité officielle :** `docs/strategy/SPEC_REGISTRY.md`.
**Document de reprise :** `docs/strategy/ROADMAP_AND_NEXT_STEPS.md`.

---

## 1. Executive summary

Sx_29 refond l'expérience mobile de séance (`GET /sessions/{session_id}`) pour réduire la friction en salle. L'objectif est d'obtenir une surface **concrète et testable** où l'utilisateur :

- voit **une seule carte exercice active** à la fois (focus visuel)
- **navigue rapidement** entre E1 / E2 / E3 (jump bar persistante)
- voit la **dernière performance utile** (delta + last_time)
- **log les sets** avec gros tap targets (no-JS form classique)
- a un **CTA sticky** clair (marquer terminé / passer suivant)
- utilise un **timer de repos** simple (JS progressif, fallback no-JS)
- passe à l'exercice suivant **sans friction**
- conserve un **fallback no-JS fonctionnel** verbatim

**Stack contraint** : FastAPI SSR + Jinja2 conservé. **Pas de React en production.** JS progressif autorisé uniquement pour timer / collapse local / sticky CTA / micro-interactions non critiques. Toute interaction critique (logger un set, valider une carte, passer à l'exercice suivant) doit fonctionner sans JS.

**Aucun service métier core touché** (scoring, recommendation, implicit_signal, quality_score, coach_report, body_tracking, substitution). **Aucune nouvelle migration.** **Aucun nouveau modèle SQLAlchemy.** La spec décompose le build en 5 lots (`Sb_29.1` à `Sb_29.5`).

**Verdict :** ✅ `READY FOR Sb_29.1` sous override #2 (cf. §20).

## 2. Pourquoi lancer Sx_29 malgré dogfood pending

Verbatim user (sprint `Sb_28.override-build-authorization`, 2026-06-15) :

> L'opérateur décide explicitement de ne pas attendre le dogfood pour avancer sur une piste de développement concrète.

Justification documentée par le Product Owner / Prompt Engineer (cf. `Sx_28 §15` recommandation provisoire et `ROADMAP_AND_NEXT_STEPS.md §7.1`) :

> Si le logging en salle n'est pas excellent, toute la couche recommandation/body analytics reposera sur un usage fragile. D'abord rendre le mode séance imbattable, ensuite enrichir le signal.

L'override #2 acte que :
- Option A (Mobile Focus Mode) répond au blocker **probable n°1** sans attendre la confirmation dogfood
- Si le dogfood futur révèle une autre friction prioritaire, Sb_28.dogfood-integration peut **reverser** Option A et imposer un fix avant `Sb_29.k`
- Le risque "build Sx_29 ne répond pas à la friction réelle" est **assumé** par l'opérateur et mitigé par la décomposition `Sb_29.1` → `Sb_29.5` avec validation entre chaque lot

**Sx_29 ne prétend PAS** que la friction logging est confirmée par dogfood. Elle est **anticipée** sous override explicite et borné.

## 3. Human override scope (rappel)

| Item | Statut |
|---|---|
| Option A — Mobile Session Focus Mode | ✅ AUTORISÉE — Sx_29 ouvrable en SPEC ONLY |
| Options B / C / D / E | 🔴 BLOQUÉES (override séparé requis pour chacune) |
| Sx_29 doit produire sa spec d'abord | ✅ ce document |
| Sb_29.k (build) | 🔵 ouvrable APRÈS validation humaine de cette spec |
| Stack | FastAPI SSR + Jinja2 conservé |
| React production | 🔴 INTERDIT dans Sx_29 et tous ses Sb_29.k |
| Lab React exploratoire | Acceptable comme proposition documentaire séparée ; JAMAIS dans le build principal Sx_29 |
| Hard contracts Sx_26 / Sx_27 | Inchangés (cf. §15.5) |
| Dogfood Sx_27 | Reste PENDING — peut reverser Option A si signal différent |

## 4. Source de vérité actuelle

| Document | Rôle |
|---|---|
| `docs/strategy/SPEC_REGISTRY.md` | source de vérité officielle des cycles livrés |
| `docs/strategy/ROADMAP_AND_NEXT_STEPS.md` | document de reprise éditorial |
| `docs/strategy/SPEC_DRIVEN_ENGINEERING_PROTOCOL_v1.md` | protocole spec-driven |
| `docs/strategy/Sx_28_PRODUCT_ROADMAP_RECONCILIATION_SPEC.md` | spec parente d'autorisation Sx_29 |
| `docs/SPRINT_Sb_28_OVERRIDE_BUILD_AUTHORIZATION_REPORT.md` | rapport override #2 |
| `docs/dogfood/DOGFOOD_Sx_27_DEFERRED.md` | position formelle "dogfood deferred" |
| Surfaces session actuelles | `app/routers/sessions.py`, `app/templates/session_detail.html`, `app/templates/session_done.html`, `app/templates/_partials/session_review.html`, `app/static/css/app.css` |

## 5. Audit de la page session actuelle

Inspection 2026-06-15 sur la branche courante.

### 5.1 Routes existantes (cf. `app/routers/sessions.py`)

| Route | Méthode | Rôle |
|---|---|---|
| `GET /sessions/{session_id}` | session detail (in_progress) | rendu de la page séance active |
| `GET /sessions/{session_id}/done` | session review V1 (Sb_27.2 + Sb_27.5) | post-séance |
| `POST /sessions/{session_id}` | mutate session-level (complete / skip / reopen) | end of session |
| `POST /sessions/{session_id}/exercises/{session_exercise_id}` | mutate one exercise card | per-card form submit |
| `POST /sessions` | create new session | from launcher |

### 5.2 Template `session_detail.html` (551 lignes)

| Bloc | Position | Caractéristiques |
|---|---|---|
| Back link "← Accueil" | tout en haut | link to home |
| `session-header` | top | titre template, jour, heure de début, badge statut, progress `done/total work sets` |
| `ex-jump` (jump bar) | sous header | liste les exercises, chaque entrée a un état (active, pending, partial, done, skipped, substituted), liens `#exercise-{id}` |
| `exercise-card` × N | corps | chaque carte est un `<details>` natif HTML (collapse no-JS), avec `<summary>` head + `<form>` POST par carte |
| `done-summary` | dans chaque carte si completed | weight str + reps str + score |
| `session-footer-actions` | bas | CTA "Terminer la séance" (POST `action=complete`) |

### 5.3 État du JS

- `app/static/js/preview.js` : existe (profile preview)
- **Aucun JS spécifique à la page session detail** actuellement
- Tous les inputs sont des `<form>` POST classiques
- Le collapse exercise card utilise `<details>` (natif HTML, fonctionne no-JS)

### 5.4 État du CSS (`app/static/css/app.css`)

- Classes `.exercise-card`, `.exercise-card__form`, `.exercise-card__head`, `.exercise-card__progress`, `.ex-jump__item`, `.session-header`, etc. déjà définies
- Variables CSS : `--space-md`, `--bg`, `--fg`, etc.
- Mobile-first via `@media (max-width: 480px)` (à vérifier au build)

### 5.5 Tests existants pertinents

- `tests/test_session_done.py` : page `/done` (Session Review V1)
- `tests/test_session_review.py` : Sb_27.2
- `tests/test_session_detail_done_focus.py` (existe ?) : à vérifier
- `tests/test_v1_acceptance.py` : exclu de CI
- `tests/test_ux_navigation.py` : nav Sb_27.6

**Constat** : la surface session detail est **déjà SSR-only, no-JS fonctionnelle, mobile-fit a minima**. Sx_29 va **améliorer le focus**, **réduire la friction**, **ajouter timer + sticky CTA progressifs**, et **ne CASSE rien** des routes / contrats existants.

## 6. Problèmes UX supposés

⚠️ **Sans dogfood réel**, ces problèmes sont **hypothèses fortes** documentées par le Product Owner (cf. `Sx_28 §10.1 + §12.1`). À confirmer par dogfood. Listés par fréquence supposée décroissante :

| # | Problème supposé | Pourquoi probable | Surface |
|---|---|---|---|
| 1 | **Surcharge cognitive** : N cartes exercice visibles en même temps → utilisateur perdu | 4-8 exercices listés tous ensemble en `<details>` collapse natif. Mobile 360×640 peut afficher 1-2 cartes ouvertes max sans scroll → mauvaise lisibilité | session_detail.html corps |
| 2 | **Jump bar peu visible en bas de page** : utilisateur scrolle pour revenir à la nav | `ex-jump` est sous header, scroll vers le bas la fait disparaître | jump bar |
| 3 | **Pas de timer de repos** : utilisateur compte de tête entre sets | aucun timer présent | manquant |
| 4 | **Tap targets** : inputs weight/reps peuvent être < 44×44px | bouton standard pas mesuré | exercise-card form |
| 5 | **CTA "Terminer" en bas, sans sticky** : utilisateur doit scroller pour conclure | session-footer-actions non sticky | footer |
| 6 | **Pas d'indication visuelle "exercice courant"** : tous équivalents | seule la jump bar montre `--active`, pas la carte elle-même | exercise-card |
| 7 | **Delta vs last_time non assez visible** : noyé dans summary | `briefing_chip` existe (Sb_11) mais discret | exercise-card |
| 8 | **Substitution UX dispersée** : entry point peu clair | substituted_name s'affiche mais pas le geste pour substituer | exercise-card |
| 9 | **Pas de "swipe / next" intuitif** : utilisateur scrolle | aucun raccourci | global |
| 10 | **Pas de feedback visuel à la complétion d'un set** : page se recharge en POST | UX classique SSR | form submit |

**Important** : Sx_29 traite ces hypothèses **comme des candidats à valider en dogfood**, pas comme des certitudes. Le build sera décomposé pour qu'un retour dogfood entre `Sb_29.k` puisse infléchir l'ordre des fixes.

## 7. User flow cible en salle

```
                       Utilisateur en salle, mobile 360×640
                                       │
                       (1) Arrive sur GET /sessions/{id}
                                       │
                                       ▼
       ┌──────────────────────────────────────────────────────┐
       │  Vue Focus Mode (Sx_29 cible)                        │
       │  ──────────────────────────────                      │
       │  Sticky header compact (template + progress 4/12)    │
       │  Sticky jump bar (E1 E2 E3 ...) avec active highlight│
       │                                                       │
       │  ┌────────────────────────────────────────────┐      │
       │  │  ACTIVE EXERCISE CARD (1 seule visible)    │      │
       │  │  - nom + code                              │      │
       │  │  - last_time block (ex: "80kg × 8 -2j")    │      │
       │  │  - delta indicator (+5kg ↑ ou rouge ↓)     │      │
       │  │  - set logger rows × N (gros tap targets)  │      │
       │  │  - feedback chips (briefing, substitution) │      │
       │  │  - CTA "Marquer terminé" sticky bottom     │      │
       │  └────────────────────────────────────────────┘      │
       │                                                       │
       │  [autres exercises collapsed par défaut]              │
       └──────────────────────────────────────────────────────┘
                                       │
                       (2) User logge ses sets via form
                                       │
                       (3) User tape "Terminer" → POST card
                                       │
                       (4) Page se recharge, prochain exercise active
                                       │
                       (5) Timer repos optionnel (JS progressif)
                                       │
                       (6) Quand tous exercices done → CTA "Terminer séance"
                                       │
                                       ▼
                       GET /sessions/{id}/done (Sb_27.2)
```

### 7.1 Cas dégradé no-JS

- Sticky CTA → CTA classique en bas de la carte (pas de sticky)
- Timer repos → input numérique "Temps de repos prévu" et message "Le timer JS est désactivé"
- Collapse → `<details>` natif HTML (déjà en place)
- Jump bar → ancres `#exercise-{id}` classiques (déjà en place)

### 7.2 Cas no-touch (desktop dogfood ou tests)

- Tap targets restent grands (44×44px min)
- Focus keyboard préservé (tab order respecté)
- Tout doit rester accessible au clavier seul

## 8. Composants visuels cibles

Chaque composant décrit ici sera implémenté en HTML + CSS + Jinja2 dans `Sb_29.1`. Aucun nouveau service métier requis.

### 8.1 Session header compact (sticky top)

- Titre template (Push A) — taille réduite vs version actuelle
- Compteur progress `N/M work sets`
- Badge statut (En cours / Terminée)
- Hauteur cible : ~48-56px
- **Sticky position** : `position: sticky; top: 0` avec backdrop

### 8.2 Jump bar (sticky sous header)

- Réutilise la classe `ex-jump` existante
- **Devient sticky** sous le header compact
- Hauteur cible : ~44px
- Tap targets ≥ 44×44px par item
- Active highlight visuel renforcé (border + bold)

### 8.3 Active exercise card

- **Une seule carte ouverte par défaut** (celle de l'exercice "active" selon `jump_states`)
- Autres cartes : `<details>` collapsed (already in place)
- Style "carte active" différencié (border accent, padding élargi)
- Hauteur cible : adapté au contenu (1-2 viewports max)

### 8.4 Set logger rows

- Une ligne par set : `Poids` `Reps` `[Complété ☐]`
- **Tap targets** : inputs ≥ 44×44px, checkbox ≥ 44×44px
- Layout `flex-row` mobile, label superscript
- Validation HTML5 native (no JS)
- Submit : un seul bouton "Valider la carte" en bas

### 8.5 Sticky CTA

- CTA principal de la carte active : **sticky bottom**
- Hauteur : ~56px
- Label dynamique selon état :
  - "Marquer terminé" si carte active
  - "Aller à E3" si tous sets logés, prochain disponible
  - "Terminer la séance" si dernier exercice complete
- **Fallback no-JS** : CTA non-sticky en bas de la carte (classique)

### 8.6 Rest timer (JS progressif)

- Apparaît **après** un POST card réussi (server peut injecter un flag `?started_rest=1`)
- Affichage : countdown `90s → 0s`
- Action : "Skip rest" ou attendre
- **Fallback no-JS** : pas de countdown ; affichage statique "Repos suggéré : 90s"
- Configurable côté serveur (durée par défaut depuis template_exercise si disponible)

### 8.7 Previous performance block

- Sous le titre de l'exercice actif :
  - `Dernière fois : 80kg × 8 (il y a 2j)` — déjà calculé par `last_time_by_exercise_code` (existant)
  - Réutilise `briefing_chips` (Sb_11) déjà passé au template

### 8.8 Delta block

- À côté du previous performance :
  - `+5kg ↑` (vert) si progression suggérée
  - `=` (neutre) si stable
  - `-` (rouge) si regression observée
- Déjà calculé par `compute_progression_hint` (existant, intact)

### 8.9 Substitution entry point

- Bouton/link discret dans la carte active : "Remplacer cet exercice →"
- Conduit vers une vue de substitution (route existante ou nouveau dialog ?)
- **OQ-A** : route séparée ou inline ? à trancher (cf. §19)

## 9. États UI

Chaque exercice peut être dans un état (déjà tracké par `jump_states` côté `pages.py`). Sx_29 amplifie le rendu visuel de chaque état.

| État | Quand | Rendu visuel cible |
|---|---|---|
| `pending` | aucun set logé | carte collapsed gris neutre, jump bar item gris |
| `active` | exercice courant (premier non-complete) | **carte OPEN par défaut**, border accent, jump bar item highlighted |
| `partial` | quelques sets logés mais incomplet | carte collapsed avec compteur partiel `2/4`, jump bar item jaune |
| `done` | tous work sets complete | carte collapsed verte avec ✓, jump bar item vert |
| `skipped` | utilisateur a marqué skip | carte collapsed grise barrée, jump bar item gris barré |
| `substituted` | exercice substitué | carte avec badge "Substitué", jump bar item avec icone ↔ |

**Cohérence avec l'existant** : ces 6 états correspondent à `jump_states` calculé déjà côté `sessions.py`. Sx_29 ajoute uniquement les classes CSS de différenciation visuelle.

## 10. No-JS fallback

**Toutes les interactions critiques fonctionnent sans JS.** Cette contrainte est verbatim user :

| Interaction | Comportement no-JS |
|---|---|
| Voir une carte exercice | `<details>` natif HTML — fonctionne sans JS |
| Logger un set | `<form>` POST classique — fonctionne sans JS |
| Naviguer entre exercices | ancres `#exercise-{id}` classiques — fonctionne sans JS |
| Sticky header / jump bar | `position: sticky` CSS — fonctionne sans JS |
| Sticky CTA | Si JS off : CTA classique en bas de la carte (CSS fallback) |
| Timer repos | Si JS off : message statique "Repos suggéré : 90s" |
| Substitution entry | Link classique vers `/sessions/{id}/exercises/{seid}/substitute` ou similaire — fonctionne sans JS |
| Marquer carte terminée | `<form>` POST `action=mark_complete` — fonctionne sans JS |
| Terminer la séance | `<form>` POST `action=complete` — déjà en place, fonctionne sans JS |

**Aucune feature ne devient inaccessible sans JS.** Tout JS est strictement progressive enhancement.

## 11. JS progressive enhancement

JS autorisé **uniquement** pour les surfaces suivantes :

| Surface JS | Effet | Sb_29 lot cible |
|---|---|---|
| Timer de repos countdown | UI dynamique 90s → 0s | Sb_29.4 |
| Sticky CTA enhancement | si CSS sticky pas supporté, fallback JS scroll-position | Sb_29.3 (CSS d'abord) |
| Collapse animation | transition smooth entre cartes (non critique) | Sb_29.1 ou Sb_29.4 |
| Auto-focus next input après tap checkbox | accélère le logging | Sb_29.2 ou Sb_29.4 |
| Micro-feedback "Set enregistré" toast | optionnel | Sb_29.4 (lab) |

### 11.1 Contraintes techniques JS

- **Pas de framework**. JS vanilla, dans `app/static/js/session_focus.js` (nouveau fichier dédié).
- **Pas de bundler** (cohérent avec stack actuel).
- **Pas de dépendance externe** (cohérent avec contrat user).
- Chaque feature JS doit avoir un fallback documenté + testé sans JS.
- **CSP** déjà restrictive (cf. `app/main.py:SecurityHeadersMiddleware`) — JS inline limité, préférer fichier externe `<script src=...>`.

### 11.2 Browser support cible

- iOS Safari 14+ (98% iPhones modernes)
- Chrome Android 90+ (99% Androids modernes)
- `position: sticky` supporté nativement ✓
- `<details>` supporté nativement ✓
- `requestAnimationFrame` pour timer ✓

## 12. Accessibilité mobile

### 12.1 Contraste et lisibilité

- Contrast ratio ≥ 4.5:1 pour le texte normal (WCAG AA)
- Contrast ratio ≥ 3:1 pour les états critiques (active, error)
- Pas de "seul couleur" pour signaler un état critique (toujours coupler avec un label ou icône)

### 12.2 Tap targets

- **Minimum 44×44px** sur tous les boutons / inputs / checkboxes (WCAG 2.5.5)
- Espacement entre cibles ≥ 8px

### 12.3 Focus keyboard

- Tab order respecté (HTML naturel)
- Focus visible (outline non supprimé sans alternative visible)
- Tous les contrôles atteignables au clavier seul

### 12.4 Labels et ARIA

- Tout input a un `<label>` explicite (visible ou sr-only)
- Jump bar : `aria-label="Aller à un exercice"` (déjà en place)
- Active exercise : `aria-current="step"` (déjà en place)
- Sticky CTA : `role="button"` si link, sinon `<button>`

### 12.5 Lecteurs d'écran

- Annonce vocale du timer optionnelle (live region `aria-live="polite"`)
- Compteur progress lisible `4 sur 12 sets validés`

### 12.6 Réduction du mouvement

- Respecter `prefers-reduced-motion: reduce` (désactiver les transitions JS)

## 13. Fichiers impactés

### 13.1 Templates (modifications ciblées, pas refonte)

| Fichier | Type changement | Sb_29 lot |
|---|---|---|
| `app/templates/session_detail.html` | refactor structurel ciblé : sticky header, sticky jump bar, active card rendering, sticky CTA fallback | Sb_29.1 |
| `app/templates/_partials/exercise_card.html` (nouveau) | extraction du bloc carte en partial pour clarté | Sb_29.1 |
| `app/templates/_partials/session_focus_header.html` (nouveau) | nouveau partial header compact | Sb_29.1 |
| `app/templates/_partials/rest_timer.html` (nouveau) | partial timer (JS-enhanceable) | Sb_29.4 |

### 13.2 CSS (modifications ciblées)

| Fichier | Type changement | Sb_29 lot |
|---|---|---|
| `app/static/css/app.css` | nouvelles classes `session-focus--*`, `sticky-header`, `sticky-cta`, `tap-target`, états `--active/--partial/--done/--skipped/--substituted` | Sb_29.1, Sb_29.2, Sb_29.3 |
| `app/static/css/session_focus.css` (nouveau, si volume justifié) | extraction CSS dédiée mode séance | Sb_29.1 (à OQ-B trancher) |

### 13.3 JS (nouveau, optionnel)

| Fichier | Type changement | Sb_29 lot |
|---|---|---|
| `app/static/js/session_focus.js` (nouveau) | timer, sticky fallback, auto-focus, collapse smooth | Sb_29.4 |

### 13.4 Routers (modifications minimales si besoin)

| Fichier | Type changement | Sb_29 lot |
|---|---|---|
| `app/routers/sessions.py` | éventuellement ajout `?started_rest=1` query param pour signaler "timer to start" après POST card | Sb_29.4 si retenu (OQ-C) |

**Aucun service métier core touché.** **Aucun nouveau modèle.** **Aucune migration.**

### 13.5 Tests (nouveaux)

| Fichier | Lot |
|---|---|
| `tests/test_session_focus_layout.py` (nouveau) | rendering test : sticky header présent, jump bar sticky, active card unique | Sb_29.5 |
| `tests/test_session_focus_accessibility.py` (nouveau) | tap target présence, labels, aria | Sb_29.5 |
| `tests/test_session_focus_no_js.py` (nouveau) | toutes les actions critiques fonctionnent sans JS (vérif via TestClient HTML pure) | Sb_29.5 |
| Tests existants `test_session_detail*`, `test_session_done*`, `test_ux_navigation` | doivent **rester verts** sans modification | tous lots |

## 14. Tests attendus

### 14.1 Contrats à valider par lot

| Lot | Tests obligatoires |
|---|---|
| Sb_29.1 | rendering test : header compact présent, partials extraits, classes CSS sticky présentes |
| Sb_29.2 | navigation test : active card unique, jump bar sticky, autres cards collapsed |
| Sb_29.3 | sticky CTA test : CSS sticky présent, fallback CSS no-JS testable |
| Sb_29.4 | timer test : JS chargé conditionnellement, fallback no-JS rendu testé, timer DOM présent quand JS on |
| Sb_29.5 | mobile smoke test : viewport 360×640, aucun scroll horizontal, tap targets ≥ 44×44px, aria présentes, accessibilité Lighthouse ≥ 90 |

### 14.2 Gates CI préservées

- pytest 1080+ doit rester vert sur tous les lots
- check_ruff_budget ≤ 548
- check_spec_protocol pass
- check_auth_scope_matrix pass
- check_alembic_drift pass (aucune migration)
- check_schema_snapshot pass (inchangé)
- perf baseline smoke `/sessions/{id}` doit rester within budget

### 14.3 Pas de test "dogfood réel" simulé

Sx_29 **n'invente pas** de retours utilisateur. Si dogfood arrive, un sprint `Sb_28.dogfood-integration` peut amender Sx_29 ou imposer un fix avant Sb_29.1.

## 15. Risques

| Risque | Probabilité | Mitigation |
|---|---|---|
| **Sticky position pas supporté** sur viewport spécifique | basse | fallback CSS non-sticky, test sur iOS Safari 14 + Chrome Android 90 |
| **Tap targets cassés** par CSS existant | moyenne | tests dédiés Sb_29.5 + revue manuelle viewport 360×640 |
| **Timer JS lourd** ou fuite mémoire | basse | JS vanilla, requestAnimationFrame, cleanup explicite |
| **Régression test session_detail existant** | moyenne | tous tests existants restent verts à chaque lot |
| **Régression perf `/sessions/{id}`** | basse | perf baseline smoke vérifié à chaque lot |
| **Sb_29.k introduit React par inadvertance** | très basse | contrat explicite §3 ; revue de PR humaine |
| **Le dogfood futur révèle une autre friction prioritaire** | moyenne (sans signal) | Sb_28.dogfood-integration peut reverser Option A et imposer fix avant Sb_29.k |
| **CSP bloque un script inline** | basse | utiliser `<script src=...>` (fichier externe), pas d'inline |
| **Override #2 contesté plus tard** | basse | spec et override documentés par écrit dans 3 docs croisés |
| **Tests visuels (Lighthouse, viewport) trop fragiles en CI** | moyenne | viser ≥ 90 Lighthouse, accepter ± 5 ; smoke test viewport via TestClient + assertion HTML structure |

## 16. Non-goals

Sx_29 **ne fait PAS** (verbatim contraintes user + protocole) :

- ❌ Pas de modification du flow de capture session existant (création, mutation, complétion)
- ❌ Pas de modification de service métier core (`scoring/`, `recommendation.py`, `reco/`, `implicit_signal.py`, `quality_score.py`, `coach_report.py`, `body_tracking.py`, `substitution.py`)
- ❌ Pas de nouveau modèle SQLAlchemy
- ❌ Pas de migration Alembic
- ❌ Pas de nouvelle route
- ❌ Pas de réécriture complète de `session_detail.html` — **refactor structurel ciblé** uniquement
- ❌ Pas de React, pas de Vue, pas de framework JS
- ❌ Pas de SPA
- ❌ Pas de bundler / build tool
- ❌ Pas de dépendance externe Python ou JS ajoutée
- ❌ Pas de LLM
- ❌ Pas de baisse de baseline ruff
- ❌ Pas de désactivation de gate Sx_26
- ❌ Pas de réouverture des décisions tranchées Sx_27 (OQ-1 à OQ-6) sans preuve dogfood
- ❌ Pas d'extension de l'override #2 aux Options B/C/D/E
- ❌ Pas de prétention que le dogfood est acquis
- ❌ Pas de notifications push, pas de service worker (réservé Option D PWA, bloquée)
- ❌ Pas de feature gamification (badges, streaks)
- ❌ Pas de partage social
- ❌ Pas de changement de palette ou de design system

## 17. Build queue

5 lots prévisionnels. **Aucun ne s'ouvre avant validation humaine de cette spec.** Chaque lot doit livrer un sprint report et passer la CI verte.

### Sb_29.1 — Visual skeleton (S-M)

**Objectif :** mettre en place la structure visuelle du focus mode sans logique dynamique.

**Livrables :**
- Extraction de `exercise-card` dans `app/templates/_partials/exercise_card.html`
- Création de `app/templates/_partials/session_focus_header.html` (sticky compact)
- Refactor `session_detail.html` pour utiliser ces partials
- Nouvelles classes CSS dans `app.css` (ou nouveau `session_focus.css`) : sticky header, sticky jump bar, active card highlight, 6 états visuels
- Tests `tests/test_session_focus_layout.py` (rendering test : présence des partials, classes, structure)
- Sprint report

**DoD spécifique :**
- session_detail.html reste fonctionnellement identique à l'avant (aucune route cassée)
- pytest 1080+ vert
- perf baseline smoke vert
- ruff budget ≤ 548

### Sb_29.2 — Active exercise navigation (S-M)

**Objectif :** rendre une seule carte active visible à la fois, jump bar sticky, navigation rapide.

**Livrables :**
- Logique Jinja : seule la carte de l'exercice "active" (selon `jump_states`) est ouverte par défaut
- CSS jump bar sticky sous header
- Anchors `#exercise-{id}` testées
- Tests `tests/test_session_focus_navigation.py` (active card unique, jump bar sticky CSS)
- Sprint report

**DoD spécifique :**
- `<details>` collapse natif HTML toujours utilisé (fallback no-JS automatique)
- Tests no-JS : la page reste utilisable
- Tap targets ≥ 44×44px sur jump bar items

### Sb_29.3 — Sticky CTA (S)

**Objectif :** CTA principal de la carte active devient sticky bottom avec fallback CSS no-JS.

**Livrables :**
- CSS `position: sticky` sur le bouton "Marquer terminé" de la carte active
- Fallback CSS non-sticky pour viewports non-supportés
- Tests : CSS classes présentes, fallback rendu dans HTML
- Sprint report

**DoD spécifique :**
- Si JS off ET sticky CSS pas supporté : CTA reste accessible en bas de la carte (classique)
- Aucune dépendance JS pour le sticky principal (CSS only)

### Sb_29.4 — Rest timer progressive enhancement (M)

**Objectif :** timer de repos vanilla JS avec fallback statique no-JS.

**Livrables :**
- `app/templates/_partials/rest_timer.html` partial avec contenu statique no-JS + DOM cible pour le countdown
- `app/static/js/session_focus.js` (nouveau fichier) : timer countdown 90s par défaut, requestAnimationFrame, cleanup
- Éventuel query param `?started_rest=1` après POST card (OQ-C à trancher)
- Tests `tests/test_session_focus_no_js.py` : timer partial rendu sans JS = message statique "Repos suggéré : 90s"
- Tests JS hors scope CI (lighthouse manuel)
- Sprint report

**DoD spécifique :**
- JS vanilla seulement
- CSP respectée (fichier externe `<script src=...>`)
- Pas de fuite mémoire (cleanup explicite à fin de countdown)
- Fallback no-JS rendu testé par TestClient

### Sb_29.5 — Template tests + mobile smoke + accessibility (M)

**Objectif :** verrouiller la qualité visuelle et l'accessibilité par tests automatisables.

**Livrables :**
- `tests/test_session_focus_accessibility.py` : tap targets, aria, labels, contrast (assertion HTML structure)
- `tests/test_session_focus_mobile_smoke.py` : viewport 360×640, pas de scroll horizontal (assertion CSS), structure mobile
- Lighthouse runbook (si disponible) ou audit manuel documenté
- Mise à jour `docs/AUTH_SCOPE_MATRIX.md` si une surface change
- Sprint report final + dogfood léger en option (cf. §18)

**DoD spécifique :**
- Lighthouse mobile ≥ 90 (si pratiqué)
- Accessibility audit documenté
- Tous les tests `tests/test_session_focus_*` verts
- Aucun test existant régressé

## 18. Conditions de validation humaine

Avant d'ouvrir `Sb_29.1`, l'opérateur doit confirmer :

| Condition | Vérification |
|---|---|
| Cette spec relue intégralement | ✅ humain commit |
| OQ-A, OQ-B, OQ-C tranchées (cf. §19) ou différées explicitement | ✅ humain commit |
| Override #2 toujours en vigueur (pas de dogfood reverse) | ✅ lire `Sx_28 §20` |
| Aucun blocker Sx_27 découvert entre temps | ✅ lire `Sx_27_CLOSURE_REPORT.md` + `DOGFOOD_Sx_27_DEFERRED.md` |
| React production reste interdit Sx_29 | ✅ verbatim §3 + §16 |
| Hard contracts Sx_26 / Sx_27 intacts | ✅ revue humaine |

### 18.1 Conditions de validation entre chaque lot

| Entre lots | Vérification |
|---|---|
| Sb_29.k → Sb_29.k+1 | CI verte sur Sb_29.k + sprint report livré + verdict explicite |
| Tout lot | Aucune régression sur tests existants (1080 base) |
| Tout lot | Aucune modification de service métier core |
| Tout lot | Aucune nouvelle migration |
| Sb_29.4 → Sb_29.5 | JS livré sans fuite mémoire ni CSP violée |

### 18.2 Conditions d'arrêt anticipé

Si l'un des signaux suivants se produit, Sx_29 doit être **mis en pause** et l'opérateur consulté :

- Dogfood Sx_27 arrive et révèle une friction non couverte par Sx_29 → Sb_28.dogfood-integration AVANT Sb_29.k+1
- Régression perf observable sur `/sessions/{id}` → fix obligatoire avant continuation
- Régression tests : un test existant casse → fix obligatoire dans le lot courant
- Demande explicite opérateur

## 19. Open questions

### OQ-A — Substitution entry point : route séparée ou inline dialog ?

Substituer un exercice peut être :
1. **Route séparée** : `GET /sessions/{id}/exercises/{seid}/substitute` qui rend une page de choix
2. **Inline dialog** : modal HTML (`<dialog>` natif HTML5) chargée dans la même page

**Recommandation par défaut :** route séparée (option 1) — cohérent avec stack SSR pur, no-JS friendly.

**Qui tranche :** opérateur. **Délai :** avant Sb_29.1.

### OQ-B — CSS dédié `session_focus.css` ou tout dans `app.css` ?

Si le volume CSS Sx_29 dépasse ~200 lignes, extraire dans `app/static/css/session_focus.css` chargé conditionnellement sur la page `/sessions/{id}`. Sinon, inline dans `app.css`.

**Recommandation par défaut :** inline dans `app.css` pour Sb_29.1, observer le volume, extraire en Sb_29.5 si besoin.

**Qui tranche :** agent au début de Sb_29.1, validation humaine au PR.

### OQ-C — Signal serveur "timer démarré" via query param ou attribut DOM ?

Pour démarrer le timer après un POST card, le serveur peut :
1. Rediriger avec `?started_rest=1&duration=90` → JS détecte au load
2. Attacher un attribut `data-start-rest="90"` au DOM de la carte qui vient d'être validée

**Recommandation par défaut :** option 2 (data attribute) — plus propre, pas de pollution URL, pas de bookmark fragile.

**Qui tranche :** opérateur ou agent au démarrage de Sb_29.4.

### OQ-D — Lighthouse en CI ou audit manuel ?

Lighthouse en CI peut être instable (jitter, cold start, network). Alternative : audit manuel documenté dans `docs/UX_SIMPLIFICATION_NOTES.md` ou un nouveau `docs/SESSION_FOCUS_AUDIT_<date>.md`.

**Recommandation par défaut :** audit manuel V1 (Sb_29.5), report dans docs. Lighthouse CI candidat pour Sb_29.next si stable.

**Qui tranche :** opérateur. **Délai :** au début de Sb_29.5.

### OQ-E — Reprise des micro-interactions retardée à un lot ultérieur ?

Toast "Set enregistré", auto-focus next input, collapse animation : utiles mais non critiques. Peut-on les déporter à `Sb_29.next.polish-1` plutôt que dans Sb_29.4 ?

**Recommandation par défaut :** oui — Sb_29.4 livre uniquement le timer + sticky JS. Le polish micro-interactions arrive en `Sb_29.next.polish-1` ou Sb_30+.

**Qui tranche :** opérateur. **Délai :** avant Sb_29.4.

## 20. Verdict

### ✅ **READY FOR Sb_29.1 (sous override #2)**

| Critère | Statut |
|---|---|
| Spec produite avec les 20 sections | ✅ |
| Justification de l'ouverture malgré dogfood pending | ✅ §2 |
| Scope override rappelé | ✅ §3 |
| Audit page session actuelle | ✅ §5 |
| Problèmes UX listés comme **hypothèses**, pas certitudes | ✅ §6 |
| User flow cible documenté | ✅ §7 |
| 9 composants visuels cibles | ✅ §8 |
| 6 états UI documentés | ✅ §9 |
| No-JS fallback verbatim | ✅ §10 |
| JS progressive enhancement borné | ✅ §11 |
| Accessibilité mobile détaillée | ✅ §12 |
| Fichiers impactés cartographiés | ✅ §13 |
| Tests attendus par lot | ✅ §14 |
| 10 risques + mitigations | ✅ §15 |
| Non-goals verbatim contraintes | ✅ §16 |
| Build queue 5 lots Sb_29.1 → Sb_29.5 | ✅ §17 |
| Conditions de validation humaine | ✅ §18 |
| 5 OQ ouvertes avec recommandations par défaut | ✅ §19 |
| React production INTERDIT marqué partout | ✅ §3, §10, §16 |
| Dogfood Sx_27 reste PENDING marqué | ✅ §2, §6, §15 |

### Prochaine action autorisée

| Acteur | Action |
|---|---|
| Opérateur | Relire cette spec, trancher OQ-A à OQ-E (ou différer explicitement) |
| Opérateur | Si OK : ouvrir `Sb_29.1` (visual skeleton) |
| Agent | Exécuter `Sb_29.1` selon §17, produire sprint report |
| Opérateur | Valider entre chaque lot (cf. §18.1) |
| Opérateur (parallèle) | Continuer à viser le dogfood Sx_27 — peut amender Sx_29 ou imposer fix |

### Limites strictes (verbatim override #2)

- Option A uniquement : **Options B / C / D / E restent bloquées**
- **React production INTERDIT** Sx_29 et tous les Sb_29.k
- Lab React exploratoire acceptable séparément, **jamais** dans le build principal
- FastAPI SSR + Jinja2 conservé
- Hard contracts Sx_26 / Sx_27 intacts
- Aucun service métier core touché
- Aucune migration, aucun nouveau modèle SQLAlchemy
- No-JS fallback obligatoire sur **toutes** les interactions critiques

---

**Statut de cette spec :** `DRAFT — READY FOR HUMAN REVIEW UNDER OVERRIDE #2`
**Build autorisé :** Option A uniquement (Mobile Session Focus Mode)
**Stack :** FastAPI SSR + Jinja2 — React production INTERDIT
**Dogfood Sx_27 :** PENDING (non simulé)
