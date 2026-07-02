# Sx_UI_03 — App Shell & Navigation Spec

**Spec ID :** `Sx_UI_03_APP_SHELL_NAVIGATION_SPEC`
**Cycle :** `Sx_UI` — Auren Visual & Product Transformation
**Date d'ouverture :** 2026-07-02
**Auteur :** opérateur (Martin Feldmann) + agent Claude Code (docs-only)
**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`
**Depends on :**
- `Sx_UI_01_BRAND_FOUNDATION_SPEC.md` ✅ accepté
- `Sx_UI_02_DESIGN_TOKENS_SPEC.md` ✅ accepté

---

## §1. Status

- **SPEC ONLY**
- **BUILD NOT AUTHORIZED**
- **Docs-only strict**
- Aucun template modifié
- Aucun CSS modifié
- Aucun JS modifié
- Aucun asset ajouté
- Aucune route modifiée
- Aucun renommage `SPIGNOS` → `Auren` dans le code

## §2. Why this spec exists

Le produit a accumulé 10 destinations de premier niveau visibles dans la topbar globale (`base.html` lignes 24-38). Chaque ajout produit a créé sa propre entrée sans hiérarchisation d'usage. Résultat : un shell « cockpit multi-systèmes » qui contredit le positionnement Auren posé en `Sx_UI_01` §6 (« interface calme, précise, mobile-first »).

Cette spec **précède** tout reskin visuel (`Sx_UI_04`) pour deux raisons :

1. **Un reskin sans hiérarchie de navigation reproduit la surcharge.** Peindre un cockpit en blanc reste un cockpit. Il faut d'abord décider quelles destinations méritent le premier niveau, quelles surfaces sont contextualisées, comment la session active s'intègre au shell.

2. **Le focus mode Sx_29 déjà livré est le prototype cible.** Header sticky, jump bar, sticky CTA, tap targets 44×44, WCAG 1.4.1 non-color cues, no-JS fallback — cette grammaire doit être étendue au shell global, pas dupliquée par écran.

Cette spec ne définit pas :
- comment implémenter la nav en templates ou CSS — décision `Sx_UI_04` et suivants
- quelles routes existent en runtime — décision `Sx_UI_04` (probablement aucune modif de route V1 : la nav utilise les routes existantes)
- comment générer les screenshots — décision `Sx_UI_11`

Elle définit **quelles destinations sont top-level, où vont les autres, quels états portent-elles, quelles règles régissent le shell mobile et desktop, quelles obligations d'accessibilité s'imposent**.

## §3. Current shell diagnosis

Observation directe de `app/templates/base.html` (lecture read-only autorisée) au SHA `fdfd71a` :

| Constat | Impact |
|---|---|
| 10 destinations dans `<nav class="topbar__nav">` : Accueil, Programmes, Historique, Physique, Progression, Classement, Squads, Profil, Coach, Déconnexion | Chrome global trop dense, aucune hiérarchie d'usage lisible |
| Navigation cachée derrière `<details class="topbar__menu">` — menu hamburger sans priorité | Toutes les destinations ont le même poids, ce qui = aucune priorité |
| `.active-banner` (session en cours) affiché en overlay `<a>` séparé | Traitement isolé de la session active, non intégré au shell principal |
| `topbar__brand` = "SPIGNOS" avec `href="{{ url_for('home') }}"` | Landing = home, pas de notion de "Today" ou "Séance" |
| Pas de bottom nav mobile | Toutes les navigations passent par le menu top ; aucune shortcut one-hand |
| Focus mode Sx_29 utilise `back="Accueil"` unique | Session detail sort du shell global, pas de bottom nav accessible pendant la séance |
| `<script>` conservé pour progressive enhancement uniquement (`session_focus.js`) | Base SSR + no-JS fallback préservée — c'est un atout pour Sx_UI_03 |

**Conclusion :** un modèle app-like manque. Auren doit passer d'un menu dense à une bottom nav ≤ 4 entrées mobile + surfaces contextualisées, sans renommer les routes, sans casser le no-JS fallback, sans introduire de framework.

## §4. App Shell Principles

Principes normatifs applicables à toute décision de navigation aval (`Sx_UI_04`, `Sx_UI_05`, `Sx_UI_06`, `Sx_UI_07`) :

1. **One primary task per screen.** Chaque écran a une décision principale explicite. Le shell la met en avant, ne la dilue pas.
2. **Navigation calme.** Zéro clignotement, zéro animation motrice ; les changements d'état passent par typo + accent (Sx_UI_02 §6 teal).
3. **Bottom nav courte.** ≤ 4 entrées top-level V1 (cf. §5). Toute exception = amendement `Sx_UI_03bis`.
4. **Action principale hors tab bar.** Apple HIG rappel : tab bar = navigation, pas action. Le CTA "Logger", "Continuer séance", "Démarrer" reste **contextuel dans le contenu**, jamais dans la bottom nav.
5. **Pas de destinations opportunistes.** Ce qui ne sert pas hebdomadairement au premier niveau va en surface secondaire. Squads / Classement n'ont pas leur place top-level (cf. §12).
6. **Surfaces secondaires contextualisées.** Coach n'est pas une destination, c'est une lecture qui apparaît là où elle est utile : Today, Progression, Session done (cf. §11).
7. **Safe-area mobile.** `env(safe-area-inset-bottom)` obligatoire sur bottom nav iOS notch/Dynamic Island (cf. §15).
8. **No-JS compatible.** Toute la navigation doit fonctionner sans JS. Progressive enhancement pour les états riches (badge session live, active state), jamais requis pour naviguer.
9. **SSR-first.** Aucune SPA, aucun bundler, aucun state client synchronisé. Chaque destination est un `<a href>` classique qui charge une page complète serveur.

## §5. Navigation model V1

**Décision V1 :** bottom nav mobile à 4 entrées. OQ-C tranchée par cette spec (recommandation V1) : 4, pas 5.

| Ordre | Destination | Route cible probable (existante) | Icône (24×24 line) | Rôle |
|---|---|---|---|---|
| 1 | **Séance** | `/` (home actuel) ou nouvelle route `/today` (cf. §7, OQ-N) | dumbbell / activity | Point d'entrée quotidien, Today + accès session en cours |
| 2 | **Programmes** | `/library` (existant, `url_for('library')`) | list / grid | Templates de séances, planification |
| 3 | **Progression** | `/progress` (existant, `url_for('progress')`) | trend line | Historique + tendances + physique (absorbé, cf. OQ-D) |
| 4 | **Profil** | `/profile` (existant, `url_for('profile_page')`) | user / cog | Compte, préférences, coach settings, squads, leaderboard, déconnexion |

**Pour chaque destination :**

### 5.1. Séance
- **Rôle** : décider et exécuter la bonne séance au bon moment.
- **Route cible probable** : `/` renommé conceptuellement en "Today" (V1 : garde `/` pour compat, contenu revu). Décision route physique = `Sx_UI_04`.
- **Contenu principal** : (a) reprendre séance en cours si active, (b) prochaine séance recommandée si pas active, (c) readiness compact (résumé signal principal), (d) accès rapide "démarrer autre séance". Cf. §7.
- **Ce qui n'y appartient pas** : historique complet, dashboards, analytics lourdes, coach report complet, physique complet.
- **État actif** : `aria-current="page"` + accent teal (Sx_UI_02 `--color-accent`) sur l'icône + texte.
- **Empty state** : "Aucune séance planifiée. Voir Programmes." avec CTA discret vers Programmes.

### 5.2. Programmes
- **Rôle** : bibliothèque de templates de séances + planification.
- **Route cible probable** : `/library` (existant).
- **Contenu principal** : templates disponibles, templates récents, création éventuelle de template custom (hors V1 UI reskin, se contente d'exposer l'existant).
- **Ce qui n'y appartient pas** : analytics de progression, historique granulaire des sessions loggées, social/community.
- **État actif** : `aria-current="page"` + accent teal.
- **Empty state** : "Aucun programme actif. Voir catalogue." (le catalogue existant reste accessible).

### 5.3. Progression
- **Rôle** : lire la trajectoire physique dans le temps.
- **Route cible probable** : `/progress` (existant), avec sous-onglets ou sections pour Historique + Physique + Coach insights (cf. OQ-D, OQ-O).
- **Contenu principal** : (a) volume / fréquence / PR récents, (b) tendances corporelles (Physique absorbé), (c) historique de sessions loggées, (d) Coach insights contextualisés (cf. §11).
- **Ce qui n'y appartient pas** : logging actif d'une séance, création de programme, social/leaderboard.
- **État actif** : `aria-current="page"` + accent teal.
- **Empty state** : "Aucune donnée encore. Log une première séance." avec CTA vers Séance.

### 5.4. Profil
- **Rôle** : compte utilisateur + tout ce qui est configuration, secondaire ou occasionnel.
- **Route cible probable** : `/profile` (existant, `profile_page`).
- **Contenu principal** : compte, préférences, coach settings (préférences narrative, seuils), squads (opt-in secondaire), leaderboard (opt-in secondaire), body intelligence entry point (Sx_31 existant), app settings, deconnexion, legal/privacy.
- **Ce qui n'y appartient pas** : logging, analytics primaires, templates.
- **État actif** : `aria-current="page"` + accent teal.
- **Empty state** : n/a (Profil est toujours peuplé au minimum par le compte utilisateur).

## §6. Destination mapping

Mapping normatif « surface actuelle → futur Auren V1 ».

| Actuel (base.html) | Route existante | Futur Auren V1 | Statut |
|---|---|---|---|
| Accueil | `url_for('home')` = `/` | **Séance (top-level)** — même route physique, contenu revu | Absorbé / renommé conceptuellement |
| Programmes | `url_for('library')` | **Programmes (top-level)** | Conservé |
| Historique | `url_for('history')` | **Progression → Historique (sous-section)** | Rétrogradé (cf. OQ-O) |
| Physique | `url_for('physique')` | **Progression → Physique (sous-section)** | Rétrogradé (cf. OQ-D) |
| Progression | `url_for('progress')` | **Progression (top-level)** | Conservé, enrichi |
| Classement | `url_for('leaderboard_page')` | **Profil → Classement (surface secondaire opt-in)** | Rétrogradé (cf. §12) |
| Squads | `url_for('squads_list')` | **Profil → Squads (surface secondaire opt-in)** | Rétrogradé (cf. §12) |
| Profil | `url_for('profile_page')` | **Profil (top-level)** | Conservé, enrichi |
| Coach | `url_for('coach_report')` | **Contextualisé (Séance, Progression, Session done)** | Rétrogradé / dispersé (cf. §11) |
| Déconnexion | form POST `url_for('logout')` | **Profil → Déconnexion (action en fin de liste)** | Déplacé dans Profil |
| Session active banner (`.active-banner`) | overlay | **Persistent resume affordance intégré** (cf. §13) | Repensé |
| Body Intelligence entrée profile-body-intel-link (Sx_31) | `/body/intelligence` | **Profil → carte "Lecture corporelle"** (existant) OU **Progression → Physique** | Conservé, placement à confirmer OQ-D |
| Body Capture Quality shell (Sb Body 02.1) | `/body/capture-quality` (flag OFF, 404) | **inchangé, hors nav V1** | Statu quo |

**Règle stricte de rétrogradation :** aucune route existante n'est supprimée, aucune redirection n'est mise en place dans `Sx_UI_03`. La rétrogradation est **purement de nav** — la route reste accessible directement par URL, seuls les liens dans le shell disparaissent du premier niveau.

## §7. Today / Séance decision

**Trois options considérées :**

- **A.** Today screen avec séance recommandée + readiness compact + résumé dernier training
- **B.** Launcher direct session (démarrer / reprendre uniquement)
- **C.** Hybride Today minimal : reprendre, recommandation, readiness compact, pas de dashboard

**Recommandation V1 : Option C — Hybride Today minimal.**

**Contenu de la destination Séance V1 :**

1. **Bloc 1 — Session en cours (conditionnel)** : si une session active existe, carte "Continuer" au sommet, dominante, teal accent. Contient nom du template, dernière série loggée, CTA "Continuer".
2. **Bloc 2 — Prochaine séance recommandée** : nom de la séance suggérée + rationale courte 1 ligne ("Push A — 3 jours depuis dernier travail poussée"). CTA "Démarrer".
3. **Bloc 3 — Readiness compact** : 1-3 signaux essentiels (volume 7j, jour depuis dernière séance, éventuel signal Body Intelligence si `BODY_INTELLIGENCE_ENABLED`). Format calme, tabular-nums (Sx_UI_02 §9).
4. **Bloc 4 — Actions secondaires** : "Voir toutes les séances" (→ Programmes), "Voir progression" (→ Progression).

**Ce qui NE doit PAS y être :**

- Pas de graphe de progression complet (relève de Progression)
- Pas de coach report complet (relève de Coach contextualisé, cf. §11)
- Pas de social / leaderboard
- Pas de body intelligence détaillé (7 blocs) — juste 1 signal si disponible
- Pas de motivational nudges (violation Sx_UI_01 §8 tone of voice)

**OQ-N tranchée par cette spec :** Today remplace conceptuellement Accueil, mais garde la route `/` en V1 pour éviter les cassures de bookmarks / historique navigation. La transition sémantique passe par le titre de la page et le contenu, pas par la route.

## §8. Programmes destination

- **Accès templates** : liste des templates disponibles (catalogue global) + templates récemment utilisés + templates personnels si applicable.
- **Historique de programmes** : si un utilisateur a une notion de programme actif (multi-semaines), le montrer ici. Sinon, hors-scope V1.
- **Pas d'analytics lourde** : la progression par exercice / par volume vit dans Progression, pas ici. Programmes = « quoi lancer », pas « comment j'ai progressé ».
- **Pas de social** : partage, followers, feed communautaire — hors-scope V1.

## §9. Progression destination

Section top-level qui absorbe Historique + Physique et intègre Coach insights contextuels.

**Structure V1 proposée (sous-onglets ou sections empilées, décision `Sx_UI_04`) :**

1. **Vue d'ensemble** : signal principal — dernière semaine — tendance 30j.
2. **Historique** : sessions loggées récentes, drill-down par date. Absorbe l'actuel `/history`.
3. **Physique** : mesures corporelles, body intelligence snapshot compact. Absorbe l'actuel `/physique`.
4. **Coach insights** (conditionnel `BODY_INTELLIGENCE_ENABLED=true` ou coach_report actif) : narrative structurée, snapshot Body Intelligence (Sx_31 existant), CTA vers coach_report complet.

**Note importante :** l'organisation Vue d'ensemble / Historique / Physique / Coach en **sous-onglets** (comme un `<details>` ou une nav secondaire) est **préférée** à une longue page qui empile tout, pour respecter le principe §4 « one primary task per screen » — la "task" ici étant "lire une facette de progression".

OQ-D et OQ-O tranchées par cette spec (recommandation V1) : Physique et Historique deviennent sous-sections de Progression, pas top-level.

## §10. Profil destination

Destination compte + tout ce qui est configuration, occasionnel ou opt-in.

**Structure V1 proposée :**

- **Compte** : identifiant, email si applicable, avatar éventuel.
- **Body Intelligence entry** : carte "Lecture corporelle" existante (Sx_31 profile-body-intel-link livré) — conservée telle quelle en V1.
- **Programme et coach settings** : préférences narrative coach, seuils, flags user-facing éventuels.
- **Squads** : accès squads si opt-in — carte discrète, jamais en tête de page.
- **Classement / Leaderboard** : accès classement si opt-in — carte discrète.
- **App settings** : notifications (hors-scope Sx_UI, réservé Sx_UI_08 PWA), thème (dark mode hors-scope V1 cf. Sx_UI_02 §19), langue, unités (kg/lbs).
- **Legal / Privacy** : liens conditions, mentions, contact.
- **Déconnexion** : action en **fin de liste**, form POST vers `url_for('logout')` (existant, non modifié).

## §11. Coach placement

**Décision V1 :** Coach n'est **pas** une destination top-level.

**Placement contextualisé :**

- **Sur Séance (Today)** : la recommandation de prochaine séance porte implicitement le raisonnement coach (rationale 1 ligne), pas de "coach report" complet.
- **Sur Progression** : section "Coach insights" contextualisée. Snapshot Body Intelligence + narrative structurée. CTA "Voir coach report complet" → route `/coach-report` existante.
- **Sur Session done (après séance)** : résumé factuel + éventuelle interprétation courte coach ("Volume +5% vs semaine dernière"). Format calme, pas de célébration.

**Rationale :** exposer Coach comme destination top-level demande à l'utilisateur de décider "j'ai envie de lire du coach maintenant", ce qui est une gestualité pratiquement inexistante en usage réel. En revanche, exposer une interprétation coach **au moment où elle a du sens** (juste après séance, en lisant sa progression, en décidant de sa prochaine séance) rend l'intelligence utile.

**OQ-E tranchée par cette spec :** Coach = contextualisé, pas top-level.

## §12. Squads / Leaderboard placement

**Décision V1 :** Squads et Classement ne sont **pas** top-level.

**Placement :**

- **Dans Profil** : carte "Squads" et carte "Classement" en surface secondaire, opt-in. Accès direct par URL préservé (`/squads/*`, `/leaderboard`).
- **Pas de badge, pas de notification, pas de red dot** dans le shell principal pour ces sections. Le shell Auren doit rester calme (Sx_UI_01 §8).

**Rationale :** le positionnement Auren est strength-first performance corporelle, pas fitness social. Squads et Classement restent des features accessibles mais **non prioritaires** dans la hiérarchie de navigation. Un utilisateur qui les utilise activement peut les épingler dans son parcours mental, mais l'utilisateur nouveau ne doit pas les voir se battre avec Séance et Progression.

Cette décision est **révisable** si dogfood futur montre une adoption forte de squads/leaderboard justifiant leur remontée. Ce serait un amendement `Sx_UI_03bis`.

## §13. Session active pattern

Comment une session active apparaît dans le shell.

**Actuellement (base.html) :**

```
<a class="active-banner" href="{{ url_for('session_detail', session_id=active_session.id) }}">
```

Une bannière `<a>` séparée qui n'est ni dans la nav, ni intégrée au contenu.

**Cible Auren V1 :**

1. **Sur Séance (Today)** : si session active, **bloc dominant en haut** de la page Today (cf. §7 bloc 1). Carte teal accent, non-dismissable. C'est la surface principale de reprise.
2. **Dans la bottom nav** : sur l'onglet "Séance", indicateur non-color cue : un point subtil (`--color-accent`, radius-full, 6px) à côté du label "Séance" pour signaler l'activité. Combiné avec un texte "En cours" au screen reader (`aria-label="Séance en cours"`). Jamais un badge rouge alarme.
3. **Sur autres destinations (Programmes, Progression, Profil)** : **pas** de bannière persistante flottante en haut. L'indicateur dans la bottom nav suffit — l'utilisateur voit "Séance • en cours" et sait où reprendre.
4. **Dans le focus mode session detail** : la bottom nav reste visible (WCAG one-hand reach) mais est visuellement discrète pour ne pas concurrencer le focus mode. Décision de style précise = `Sx_UI_04`.

**Interdits :**

- ❌ Pas de bannière modale bloquante
- ❌ Pas de couleur d'alerte (orange, rouge) sur la session active — un point teal suffit
- ❌ Pas de vibration, ping, notification navigateur
- ❌ Pas d'auto-scroll ou d'auto-focus sur la carte session active

## §14. Header / Topbar rules

Décisions pour le header global (non-focus-mode).

- **Brand presence Auren** : le mot "Auren" apparaît dans le header à partir de `Sx_UI_10` (rebrand execution). En V1 de `Sx_UI_04`, le header conserve "SPIGNOS" par défaut de code — c'est acceptable car `Sx_UI_10` reste bloqué (cf. Sx_UI_01 §14).
- **Title court** : titre de page à gauche, max 22 caractères visibles mobile. Truncate avec `text-overflow: ellipsis`. Familles : `--font-family-sans`, weight `--font-weight-medium` (500).
- **Pas de gros logo** : pas de wordmark massif, pas d'illustration. Le nom + éventuelle micro-icône, c'est tout.
- **Action secondaire max 1** : le header peut porter **une seule** icône-action à droite (menu overflow, recherche, ou notifications si Sx_UI_08 les active). Jamais 2+.
- **Profil / settings selon viewport** : sur mobile, accès profil via la bottom nav (destination Profil). Sur desktop (rail lateral), l'avatar profil peut apparaître en pied de rail. Pas de duplication.

**Focus mode** : le header du focus mode reste distinct (`session_focus_header.html` existant, Sx_29). `Sx_UI_04` fera converger le style visuel mais gardera la logique sticky et le contenu (nom template + progression + note optionnelle).

## §15. Mobile layout rules

- **Bottom nav sticky** : `position: fixed; bottom: 0; left: 0; right: 0;` avec `--z-sticky` (Sx_UI_02 §16).
- **Safe-area** : `padding-bottom: env(safe-area-inset-bottom);` obligatoire.
- **Tap target 44×44** : chaque destination de bottom nav a une zone tactile ≥ 44×44 CSS px, incluant icône + label empilés.
- **Aucune action principale dans la tab bar** : cf. §4 principe 4. Les 4 destinations sont des liens de navigation, pas des CTA.
- **Scroll content non masqué** : `padding-bottom` du contenu ≥ hauteur bottom nav + safe-area, pour éviter que le dernier élément soit sous la nav.
- **One-hand reach** : les CTA primaires (dans le contenu) restent dans la zone atteignable du pouce sur écran 360×640, i.e. hauteur ≤ 75 % du viewport visible depuis le bas.
- **Viewport meta** : `viewport-fit=cover` (déjà présent dans `base.html`) obligatoire pour rendre les safe-areas exploitables.
- **Focus mode session** : bottom nav visible mais **discrète** (opacité réduite ou hauteur légèrement réduite). Décision précise = `Sx_UI_04`. Elle **ne disparaît pas** — l'utilisateur peut toujours sortir vers Progression ou Profil.

## §16. Desktop layout rules

- **Rail latéral vs top nav** : décision **rail latéral gauche** V1 (cf. OQ-Q recommandation ci-dessous).
- **Rationale rail** : cohérence avec les apps de performance premium (Levels, Oura desktop), meilleure exploitation du viewport large, navigation persistante sans consommer de hauteur.
- **Bottom nav non obligatoire desktop** : au-delà de `≥ 1024px`, la bottom nav disparaît au profit du rail. En dessous, la bottom nav reste (tablette portrait).
- **Max-width content** : max-width du contenu ≤ 960px (lecture confortable), centré ou aligné à côté du rail selon largeur.
- **Hiérarchie cohérente avec mobile** : mêmes 4 destinations dans le rail, mêmes noms, mêmes ordres.
- **Pas de dashboard dense** : le desktop ne devient pas une opportunité de tout afficher. La même hiérarchie one-decision-per-screen s'applique.
- **Focus mode session en desktop** : le rail reste visible mais discret. Le contenu focus mode se centre dans un max-width plus étroit (~640px) pour préserver l'ergonomie mobile.

**OQ-Q tranchée par cette spec :** desktop = rail latéral gauche.

## §17. Accessibility

Règles a11y normatives applicables à toute implémentation aval :

- **`aria-current="page"`** sur la destination active de la bottom nav (ou du rail desktop).
- **Labels explicites** : chaque destination a un `<span>` texte visible + éventuelle icône décorative (`aria-hidden="true"`). Pas d'icône seule sans label — jamais.
- **Focus visible** : `outline: 2px solid var(--color-accent-focus-ring); outline-offset: 2px;` (Sx_UI_02 §12), jamais `outline: none`.
- **Non-color cues** : la destination active porte l'accent teal **ET** un indicateur non-color (bordure haute ou weight typo boldé). Conformité WCAG 1.4.1.
- **Keyboard navigation** : Tab entre destinations, Enter pour naviguer, Escape pour fermer menu overflow éventuel. Pas de trap.
- **Reduced motion compatible** : aucune animation obligatoire pour comprendre l'état actif. Les transitions (Sx_UI_02 §15) respectent `@media (prefers-reduced-motion: reduce)`.
- **44×44 tap targets** : cf. §15.
- **Screen reader flow** : `<nav aria-label="Navigation principale">` autour de la bottom nav / rail. Chaque destination annonce nom + état actif éventuel.
- **Session active screen reader** : `aria-label="Séance, en cours"` sur la destination Séance quand session active. Le point visuel est `aria-hidden="true"`.
- **Skip link** : `<a href="#main-content" class="skip-link">` en premier tab, visible au focus, pour sauter la nav et atteindre le contenu principal directement.
- **Route logout** : reste un `<form method="post">` (existant, non modifié) pour respecter la sémantique HTTP correcte + protection CSRF (Sb_26.4 rate limit sur `/logout` ? à confirmer, mais aucune modif de route dans Sx_UI_03).

## §18. Visual token dependency

Cette spec **ne définit pas** de tokens visuels. Elle consomme ceux de `Sx_UI_02` :

| Élément shell | Tokens consommés |
|---|---|
| Fond global | `--color-bg-base` (`#FFFFFF`) |
| Surface header | `--color-surface` avec `border-bottom: 1px solid var(--color-border-subtle)` |
| Séparateurs | `--color-border-subtle` |
| Destination active accent | `--color-accent` (teal chirurgical désaturé) |
| Destination active non-color cue | `--font-weight-medium` (500) ou bordure haute `--color-accent` |
| Session active dot | `--color-accent` + `--radius-full` + 6×6 px |
| Focus ring | `--color-accent-focus-ring` outline 2px |
| Typographie labels | `--font-family-sans`, `--font-size-body-sm` (13px), `--font-weight-medium` |
| Icon size | 24×24 line (Sx_UI_02 §21 principe icônes) |
| Spacing bottom nav interne | `--space-2` (8px) padding-block, `--space-3` (12px) padding-inline |
| Motion transitions | `--motion-duration-fast` (120ms) + `--motion-easing-standard` |
| Z-index | `--z-sticky` (100) pour bottom nav |

**Aucun nouveau token n'est introduit dans `Sx_UI_03`.** Toute proposition qui nécessiterait un token absent de `Sx_UI_02` déclenche un amendement `Sx_UI_02bis` explicite.

## §19. Screenshot baseline dependency

`Sx_UI_11` (Screenshot Regression Baseline) doit produire une baseline avant tout reskin en `Sx_UI_04`. Écrans à capturer par baseline :

| Écran | Route actuelle | Viewport mobile | Viewport desktop |
|---|---|---|---|
| Accueil / Today | `/` | 360×640 | 1440×900 |
| Session detail (focus mode) — vue vide | `/sessions/{id}` (session sans logs) | 360×640 | 1440×900 |
| Session detail (focus mode) — vue en cours | `/sessions/{id}` (session avec 2-3 exercices loggés) | 360×640 | 1440×900 |
| Session detail (focus mode) — vue terminée | `/sessions/{id}/done` | 360×640 | 1440×900 |
| Programmes / library | `/library` | 360×640 | 1440×900 |
| Progression | `/progress` | 360×640 | 1440×900 |
| Historique | `/history` | 360×640 | 1440×900 |
| Physique | `/physique` | 360×640 | 1440×900 |
| Profil | `/profile` | 360×640 | 1440×900 |
| Coach report | `/coach-report` | 360×640 | 1440×900 |
| Body Intelligence | `/body/intelligence` (flag ON) | 360×640 | 1440×900 |
| Login | `/login` | 360×640 | 1440×900 |
| Register | `/register` | 360×640 | 1440×900 |

**Total :** 13 écrans × 2 viewports = **26 screenshots baseline**.

**État attendu :** compte smoke `martin_prod_smoke_20260702_1037` en prod contient déjà login + profile + body/intelligence peuplés (avec DB vide côté séances). Pour les screens session (`/sessions/{id}`, `/history`), il faudra soit :
- ajouter des séances de démonstration (nécessite Sx_UI_11 spec pour trancher scénario)
- ou capturer les empty states (approche recommandée pour Sx_UI_11 V1)

**Ce sprint n'implémente pas la capture** — il **prépare la liste** que `Sx_UI_11` consommera.

## §20. Open Questions

Rappel des OQ liées à la navigation + résolutions apportées par cette spec.

| OQ | Question | Recommandation V1 (cette spec) | Statut |
|---|---|---|---|
| **OQ-C** | Bottom nav 4 ou 5 destinations ? | **4** (Séance / Programmes / Progression / Profil) | ✅ tranché V1 |
| **OQ-D** | Physique top-level ou sous Progression ? | **sous Progression** en sous-section | ✅ tranché V1 |
| **OQ-E** | Coach top-level ou contextualisé ? | **contextualisé** (Séance, Progression, Session done) | ✅ tranché V1 |
| **OQ-N** | Today remplace-t-il Accueil ? | **oui conceptuellement**, garde route `/` en V1 | ✅ tranché V1 |
| **OQ-O** | Historique devient-il sous Progression ? | **oui** en sous-section | ✅ tranché V1 |
| **OQ-P** | Squads / Classement restent-ils accessibles depuis Profil ? | **oui** en surfaces secondaires opt-in | ✅ tranché V1 |
| **OQ-Q** | Desktop = sidebar ou top nav ? | **rail latéral gauche** | ✅ tranché V1 |
| **OQ-R** | Comment séparer Vue d'ensemble / Historique / Physique / Coach dans Progression : sous-onglets, sections empilées, ou `<details>` ? | **à trancher `Sx_UI_04`** — probablement sous-onglets tab-like SSR (URL avec query param `?tab=history`) | ⚠️ pending Sx_UI_04 |
| **OQ-S** | Le "point actif" session live dans la bottom nav est-il `--color-accent` (teal) ou `--color-signal` (bleu minéral) ? | **teal `--color-accent`** — la session active est la primary task, teal cohérent | ✅ tranché V1 |
| **OQ-T** | Un utilisateur logged-out (public /login, /register) voit-il la bottom nav ? | **non** — le shell logged-out reste minimal, juste header brand + éventuellement lien réciproque login ↔ register | ✅ tranché V1 |
| **OQ-U** | La bottom nav apparaît-elle sur les pages d'erreur (404, 500) ? | **oui** si utilisateur authentifié, **non** sinon | ✅ tranché V1 |

**Note importante :** ces résolutions sont des **recommandations V1** de cette spec. Elles peuvent être révisées lors du human review de `Sx_UI_03`.

## §21. Non-goals

- Pas de code (aucun fichier `app/`, `tests/`, `migrations/`, `scripts/`, `.github/` modifié)
- Pas de template modifié (`base.html`, `session_detail.html`, `_partials/*.html`, etc.)
- Pas de CSS applicatif
- Pas de JS applicatif
- Pas de route ajoutée, modifiée, supprimée, redirigée
- Pas de modèle SQLAlchemy modifié
- Pas de migration Alembic
- Pas d'asset (icône SVG, image, police web) ajouté
- Pas de logo
- Pas de manifest update
- Pas de rebrand code (`SPIGNOS` reste dans les templates)
- Pas de suppression réelle de pages ou de routes
- Pas de redirection HTTP
- Pas de changement d'auth
- Pas de changement métier (aucun service touché : scoring, substitution, coach_report, body_intelligence, overload_engine, etc.)
- Pas de build (`Sb_UI_NN.k` non ouvert)
- Pas de screenshot capture (relève de `Sx_UI_11`)
- Pas de tokens visuels nouveaux (`Sx_UI_02` seul propriétaire)
- Pas de flag toggle (`BODY_INTELLIGENCE_ENABLED`, `BODY_ASSESSMENT_ENABLED`, `BODY_CAPTURE_QUALITY_ENABLED` inchangés)

## §22. Acceptance criteria

La spec est acceptable si :

- ✅ Navigation V1 bottom nav ≤ 4 entrées définie (§5)
- ✅ Surfaces actuelles mappées avec statut (§6)
- ✅ Destinations secondaires cadrées (Coach §11, Squads/Classement §12)
- ✅ Session active pattern défini (§13)
- ✅ Mobile layout rules définies (§15)
- ✅ Desktop layout rules définies (§16)
- ✅ Accessibility rules définies (§17)
- ✅ Tokens Sx_UI_02 consommés, aucun token nouveau (§18)
- ✅ Baseline `Sx_UI_11` préparée avec liste d'écrans (§19)
- ✅ Sx_UI_04 préparé sans écrire de code (résolutions §7, §9, §14 utilisables)
- ✅ OQ énumérées avec recommandation V1 (§20)
- ✅ Non-goals explicites (§21)
- ✅ Aucun fichier `app/`, `tests/`, `migrations/`, `scripts/`, `.github/`, static asset modifié

## §23. Build authorization status

**BUILD NOT AUTHORIZED.**

**Next action after human validation of this spec :**

Option 1 (recommandée) : `Sx_UI_11_SCREENSHOT_REGRESSION_SPEC` **SPEC ONLY** — produire la spec de la baseline avant tout reskin, car `Sx_UI_04` requiert cette baseline comme précondition.

Option 2 : `Sx_UI_04_SESSION_FOCUS_RESKIN_SPEC` **SPEC ONLY** — écrire la spec de reskin en parallèle de Sx_UI_11, à condition que Sx_UI_11 soit ouverte simultanément et que la baseline soit produite avant tout code Sx_UI_04.

Aucun build `Sb_UI_NN.k` d'implémentation n'est autorisé. Aucun fichier `app/`, `tests/`, `migrations/`, `.github/workflows/`, config runtime, `.env`, manifest, static assets ne peut être touché. Aucun renommage `SPIGNOS` → `Auren` ne peut être effectué dans le code.

`Sx_UI_04` (premier sprint autorisé à modifier du code visuel) reste bloqué par :

1. `Sx_UI_01` ✅ accepté (implicite via override opérateur)
2. `Sx_UI_02` ✅ accepté (2026-07-02)
3. `Sx_UI_03` (cette spec) — pending human review
4. `Sx_UI_11` baseline screenshots disponible
5. OQ résiduelles Sx_UI_02 (OQ-H hex, OQ-I font sans, OQ-J font mono, OQ-K scale) et OQ résiduelle Sx_UI_03 (OQ-R Progression sous-nav)

## §24. Final verdict

**READY FOR HUMAN REVIEW.**

---

## Références

- **Spec précédente :** `docs/strategy/Sx_UI_02_DESIGN_TOKENS_SPEC.md` ✅ accepted
- **Spec avant :** `docs/strategy/Sx_UI_01_BRAND_FOUNDATION_SPEC.md` ✅ accepted
- **Roadmap cycle :** `docs/strategy/UI_TRANSFORMATION_ROADMAP.md`
- **Registry :** `docs/strategy/SPEC_REGISTRY.md` §1quinquies
- **Roadmap globale :** `docs/strategy/ROADMAP_AND_NEXT_STEPS.md`
- **Brainstorm sources :** `docs/strategy/brainstorm/UI_TRANSFORMATION_BRAINSTORM_V1_normalized.md`, `..._V2_normalized.md`
- **Focus mode précurseur (SSR/Jinja/no-JS pattern hérité) :** `docs/strategy/Sx_29_CLOSURE_REPORT.md` + `app/templates/_partials/session_focus_header.html` + `app/templates/session_detail.html` (lecture seule)
- **Shell actuel (lecture seule) :** `app/templates/base.html`
- **CI cost optimization :** `docs/SPRINT_Sb_OPS_ci_path_filter_BUILD_REPORT.md` (path filter opérationnel, push docs-only n'engendre plus de CI)
