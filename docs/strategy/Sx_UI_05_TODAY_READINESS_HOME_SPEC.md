# Sx_UI_05 — Today / Readiness Home Spec

**Spec ID :** `Sx_UI_05_TODAY_READINESS_HOME_SPEC`
**Cycle :** `Sx_UI` — Auren Visual & Product Transformation
**Type :** SPEC ONLY (docs-only) — product / UX / technical specification
**Date d'ouverture :** 2026-07-07
**Auteur :** opérateur (Martin Feldmann) + agent Claude Code
**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`
**Depends on :**
- `Sx_UI_01_BRAND_FOUNDATION_SPEC.md` ✅ accepté
- `Sx_UI_02_DESIGN_TOKENS_SPEC.md` ✅ accepté
- `Sx_UI_03_APP_SHELL_NAVIGATION_SPEC.md` ✅ accepté
- `Sx_UI_04_FOCUSED_EXERCISE_FLOW_SPEC.md` ✅ **CLOSED** (cycle Focused Exercise Flow, commit `41af292`)

---

## §0. Status

- **SPEC ONLY**
- **BUILD NOT AUTHORIZED**
- **Docs-only strict** — aucun `app/`, `tests/`, `migrations/`, `scripts/`, `.github/` touché
- Aucun CSS / template / JS modifié
- Aucun modèle readiness backend créé
- Aucun changement `scoring/`, `overload_engine.py`, `coach_report.py`, `body_intelligence.py`
- Aucun rebrand SPIGNOS → Auren dans le code (réservé Sx_UI_10)
- Sx_UI_04 **ne doit pas être rouvert** ; référence produit uniquement.

## §1. Executive summary

Sx_UI_05 spécifie l'écran **Today / Readiness Home** comme **surface d'entrée mobile-first** du produit après la refonte Focus Mode (Sx_UI_04 clos). Le Home n'est **pas** un tableau de bord analytique complet : c'est une **surface de décision quotidienne** qui répond en < 5 s à « est-ce que je m'entraîne aujourd'hui, quelle séance, dans quel état, quelle action ». Il applique l'identité Auren (Clinical Instrument : calme, décisionnel, non anxiogène, non gamifié) et **réutilise uniquement des données déjà existantes** (sessions, readiness self-report, KPIs, recommandation, atlas). Aucun nouveau modèle, migration, ni moteur readiness médical.

## §2. Objectif produit

Le Home doit répondre immédiatement à :
1. Est-ce que je m'entraîne aujourd'hui ?
2. Quelle séance est prioritaire maintenant ?
3. Quel est mon état / readiness approximatif ?
4. Qu'est-ce qui a changé depuis la dernière séance ?
5. Quelle action principale dois-je faire ?
6. Comment reprendre une séance active ?
7. Comment voir mon progrès sans transformer l'accueil en dashboard lourd ?

**Décision forte** : une **CTA principale unique** guide l'utilisateur — reprendre séance active · démarrer séance prévue · choisir programme · ou repos/review si aucune séance pertinente.

## §3. Problème actuel du Home

État observé (lecture read-only de `app/templates/index.html` + `app/routers/pages.py::home`) :
- **P1. Densité type "board"** : le Home compose déjà KPIs globaux, sparkline 14j, recommandation, behavioral state, readiness, home payload coaching. Riche, mais tend vers un **tableau de bord** plutôt qu'une surface de décision.
- **P2. Hiérarchie décisionnelle diluée** : l'action principale (« que faire maintenant ») n'est pas visuellement dominante face aux métriques.
- **P3. Chrome pré-Auren** : le Home n'a pas reçu le reskin Auren (scope Sx_UI_04 = Focus Mode uniquement). Il reste sur l'ancienne grammaire visuelle.
- **P4. Readiness peu instrumental** : la donnée readiness (self-report) existe mais n'est pas présentée comme un **repère décisionnel calme**.
- **P5. Continuité biomécanique absente** : aucun lien léger avec le Worked Area / zones travaillées introduites en Sx_UI_04.

## §4. Relation avec Sx_UI_03 App Shell

Sx_UI_03 a défini la **bottom nav 4 entrées** (Séance / Programmes / Progression / Profil) + rail desktop. Le Home est la **destination par défaut** de l'app shell (route `/`).
- Le Home **respecte** l'app shell : il ne redéfinit pas la navigation globale, il vit à l'intérieur.
- Le Coach est **contextualisé** (pas d'entrée top-level bavarde) — cohérent avec Sx_UI_03.
- Les entrées Séance / Programmes / Progression restent la navigation ; le Home **oriente** vers elles via sa CTA et ses surfaces.

## §5. Relation avec Sx_UI_04 Focused Exercise Flow

Sx_UI_04 (clos) a livré le **cockpit d'exécution** de la séance. Le Home est **l'amont** :
- Si une **session active** existe (cockpit en cours), le Home doit permettre d'y **reprendre** immédiatement (surface active dominante, §10).
- Le Home peut réutiliser la **grammaire visuelle Auren** (tokens Sx_UI_02) et la **couche Worked Area** en résumé léger (§14) — surfaces B/C du Body Representation System (§23.2 de la spec Sx_UI_04).
- **Aucune modification du Focus Mode** dans ce cycle : le Home renvoie vers `/sessions/{id}` existant.

## §6. Utilisateur cible et contexte d'usage mobile

- **Contexte** : ouverture rapide avant/entre séances, souvent debout, une main, mobile 360×640, lumière variable (salle de sport).
- **Besoin** : décision en quelques secondes, pas de lecture longue, pas de calcul mental.
- **Anti-besoin** : pas de feed, pas de badges/streaks gamifiés, pas de graphes financiers, pas d'écran marketing.
- **Fréquence** : plusieurs fois/jour les jours d'entraînement ; check rapide les jours de repos.

## §7. Information architecture V1

Ordre vertical mobile (priorité décisionnelle décroissante) :

| # | Bloc | Rôle | Condition |
|---|---|---|---|
| A | **Header léger** | date + salutation sobre | toujours |
| B | **Hero Decision Surface** | CTA principale unique + contexte (§8) | toujours |
| C | **Active Session Surface** | reprise séance en cours | si `open_session` |
| D | **Next Workout Surface** | prochaine séance / meilleur programme | si pas de session active |
| E | **Readiness Snapshot** | repère état (self-report) | si `readiness_today` |
| F | **Recovery / load cues** | fatigue/charge récente (léger) | si donnée dispo |
| G | **Recent Progress Snapshot** | dernière séance + tendance | si historique |
| H | **Body Continuity (léger)** | zones récemment sollicitées / prochaine zone | optionnel V1 (OQ-05-E) |

Sur desktop 1440×900 : grille 2 colonnes possible (hero + active/next à gauche, readiness/progress à droite), hero toujours prioritaire.

**Anti-modèle** : empiler 8 cartes de métriques équivalentes. La hiérarchie **B > (C|D) > E > G** est stricte.

## §8. Today Decision Model

Le cœur du Home est une **décision unique**. Résolution (priorité) :

1. **Session active existe** (`open_session`) → CTA = « **Reprendre la séance** » (dominante, §10).
2. **Pas de session active, séance prévue / recommandée** (`reco`) → CTA = « **Démarrer {séance}** » (§11).
3. **Pas de recommandation claire** → CTA = « **Choisir un programme** » (vers Programmes).
4. **Repos pertinent** (ex. readiness basse + séance récente) → CTA = « **Jour de repos / Revoir mes séances** » (non impératif, OQ-05-D).

**Une seule CTA primaire** visible à la fois. Les autres actions restent secondaires (liens discrets).

## §9. Readiness Model V1 — présentation, pas moteur médical

**Base réelle existante** : `app.services.readiness` expose des **scales auto-déclarées 1-5** (sommeil, fatigue, courbatures, stress, motivation) via `get_today_readiness` + `READINESS_LABELS` / `READINESS_FIELD_LABELS` / `SCALE_FIELDS`. **C'est du self-report, pas une mesure physiologique.**

Contraintes V1 :
- **Conservateur** : affiché comme **repère**, jamais diagnostic.
- **Pas de score médical**, pas de promesse hormonale/récupération réelle.
- **Pas d'inférence invisible** : n'afficher que ce que l'utilisateur a déclaré (ou inviter à déclarer si absent).
- Présentation possible : **bande qualitative** (ex. « Plutôt en forme » / « État moyen » / « Fatigue signalée ») dérivée des scales existantes — **sans nouveau calcul backend** dans la spec (tout agrégat nouveau = future/deferred, OQ-05-B).
- Formulation sobre : « Repère du jour (auto-déclaré) », jamais « votre récupération est de X% ».
- Si `readiness_today` absent → invite légère « Renseigner mon état du jour » (vers le formulaire readiness existant), non anxiogène.

## §10. Active Session Surface

Si `open_session` :
- **Domine** l'écran (surface hero).
- Affiche : nom de séance (`template_name_snapshot`), durée depuis le début (`open_since` déjà calculé), progression (work sets done/total si dispo via données existantes).
- CTA = « **Reprendre la séance** » → `/sessions/{open_session.id}` (route existante).
- Ton calme, pas d'urgence gamifiée.

## §11. Next Workout Surface

Si pas de session active :
- Utilise `reco` (contexte recommandation déjà composé read-only côté `pages.py`).
- Affiche : séance/programme recommandé, raison courte si disponible, CTA « **Démarrer** » → launcher / route existante.
- Si pas de reco claire → « **Choisir un programme** » (vers Programmes).
- Aucune reco inventée : si la donnée n'existe pas, fallback sobre.

## §12. Recovery / load / fatigue cues

- Réutilise `behavioral` (behavioral state existant) et/ou les scales readiness (fatigue/courbatures).
- Présentation **légère** : une ligne de repère (ex. « Charge récente : soutenue » ou « Repos récent »).
- **Pas de modèle de charge (TSS/ACWR) nouveau** — tout calcul de charge réel = future/deferred.
- Jamais alarmiste ; jamais prescriptif médical.

## §13. Recent Progress Snapshot

- Lisible en **5 secondes** : dernière séance + tendance simple + prochaine action.
- Réutilise `sparkline_svg` existant (composite 14j) et `kpis` — mais **présentés sobrement**, pas comme un board analytique.
- Un seul indicateur de tendance dominant (ex. la sparkline), pas une grille de KPIs.
- Lien « Voir la progression → » vers l'onglet Progression (pas de dashboard inline).

## §14. Body / Worked Area continuation from Sx_UI_04

- **Résumé léger uniquement** : zones récemment sollicitées et/ou zone dominante de la prochaine séance, dérivées de l'atlas `family/zone` déjà disponible en contexte de séance.
- **Pas de heatmap complète V1.**
- **Pas de profil Body Intelligence** maintenant.
- Réutilise le contrat `body_map_descriptor` (§23.5 Sx_UI_04) **documentaire** ; toute qualification nouvelle = future.
- Placement : bloc H, secondaire, optionnel V1 (OQ-05-E).

## §15. Empty states

- **Nouvel utilisateur sans historique** (OQ-05-H) : hero = « **Commencer** » → choisir un programme / première séance. Pas de métriques vides affichées ; message d'accueil sobre.
- **Aucune session active + aucune reco** : CTA « Choisir un programme ».
- **Readiness non renseigné** : invite légère, non bloquante.
- **Pas d'historique de progression** : masquer le snapshot progress plutôt qu'afficher un graphe vide.

## §16. Edge states

- **Session active ancienne / oubliée** : proposer « Reprendre » **ou** « Terminer/clôturer » (via routes existantes), sans forcer.
- **Plusieurs sessions ouvertes** (si possible) : afficher la plus récente (`latest_open_session` existant).
- **Données partielles** (reco sans nom, readiness incomplet) : fallback sobre par champ, jamais d'erreur visible.
- **Séance terminée aujourd'hui** : hero peut basculer sur « Revoir la séance » / « Repos » (OQ-05-D).

## §17. Visual grammar

Direction Auren (tokens Sx_UI_02, scoped au Home) :
- Blanc / off-white (`#FFFFFF` / `#FAFBFC`), neutres froids.
- Teal chirurgical `#0F8A85` réservé à l'action / accent.
- Mono/tabular pour les metrics.
- **Faible chrome**, séparateurs fins, ombres minimales.
- **Interdits** : gradient IA, orange dominant, dark cockpit, coach bavard top-level, badges/streaks, celebration/confetti, illustrations héroïques.
- Hero surface = la plus élevée visuellement ; readiness/progress = surfaces calmes secondaires.

## §18. Accessibility / no-JS / mobile-first

- **No-JS fallback** : le Home doit rester utilisable sans JS (SSR ; la CTA est un `<a>`/`<form>` vers une route existante). Recommandation V1 : **Home entièrement no-JS** (OQ-05-I).
- **WCAG 44×44** tap targets (CTA, liens).
- **Focus visible universel** (outline 2px teal, cohérent Sx_UI_04.1).
- **`prefers-reduced-motion`** respecté (aucune animation lourde ; la sparkline SVG est statique).
- **Mobile-first 360×640** : hiérarchie claire, pas de scroll horizontal, CTA atteignable au pouce.
- Contraste AA sur texte/accent.
- Readiness/labels lus sémantiquement (pas seulement couleur).

## §19. Data contract — existing data only

Le futur build **ne consomme que des données déjà présentes** dans le contexte `home` (`app/routers/pages.py::home`) :

| Donnée | Source existante |
|---|---|
| Session active | `open_session`, `open_since` |
| KPIs globaux | `kpis` (`compute_global_kpis`) |
| Tendance 14j | `sparkline_svg`, `sparkline_has_mixed_kinds` |
| Recommandation / next | `reco` (`_build_reco_context`) |
| État comportemental | `behavioral` (`compute_behavioral_state`) |
| Readiness self-report | `readiness_today`, `readiness_labels`, `readiness_field_labels`, `readiness_scale_fields` |
| Payload coaching home | `home` (`build_home_payload`) |
| Zones (léger) | atlas `family/zone` (déjà disponible côté séance) |

**Règles :**
- **Aucun nouveau modèle**, aucune migration.
- **Aucun nouveau service obligatoire** dans la spec.
- Tout **nouveau calcul** (agrégat readiness, charge, body summary) doit être **explicitement marqué future/deferred**.
- Le build peut **recomposer/présenter** ces données, jamais en créer de nouvelles côté DB.

## §20. Forbidden changes

- ❌ `scoring/`, `overload_engine.py`, `substitution.py`, `coach_report.py`, `body_intelligence.py`, `recommendation.py` — inchangés.
- ❌ Aucun modèle readiness backend nouveau.
- ❌ Aucune migration.
- ❌ Aucun score readiness pseudo-scientifique non sourcé.
- ❌ Aucune donnée physiologique inventée.
- ❌ Aucune modification du Focus Mode (Sx_UI_04 clos).
- ❌ Aucun rebrand SPIGNOS → Auren dans le code (Sx_UI_10).
- ❌ Aucune ouverture Sx_UI_06 / Sx_UI_10.
- ❌ Aucun release tag.

## §21. Build split proposal

| Sous-sprint | Portée |
|---|---|
| **Sb_UI_05.1 Home IA + Hero Decision Surface** | topologie Home (IA §7) + hero CTA unique (Today Decision Model §8), Auren scoped. Bascule perception board → décision. |
| **Sb_UI_05.2 Active Session / Next Workout Cards** | surface active (§10) + next workout (§11), CTA contextualisée, reprise séance. |
| **Sb_UI_05.3 Readiness / Recovery Snapshot** | présentation readiness self-report (§9) + recovery cues légers (§12), conservateur. |
| **Sb_UI_05.4 Recent Progress + Body Continuity** | progress snapshot (§13, réutilise sparkline) + body continuity léger (§14). |
| **Sb_UI_05.5 Empty States + Accessibility + Screenshot Hardening** | empty/edge states (§15/§16), a11y/no-JS (§18), baseline P0 Home + hardening. |

Granularité à ajuster si le build découvre mieux (ex. fusionner .3/.4 si léger).

## §22. Tests and baseline expectations

- **Baseline P0 Home** à prévoir : mobile 360×640 + desktop 1440×900, états :
  - active session · no active session · empty/new user · with recent history · with measurements (si fixture existante le supporte).
- Le futur build doit conserver : **P0 capture `ok=16`** (ou matrice élargie **documentée** si les états Home ajoutent des slugs) ; **aucun PNG committé** ; **anti-404 obligatoire**.
- Tests structurels attendus (au build) : hero CTA unique présente · résolution du Today Decision Model par état · readiness présenté sans claim médical · no-JS fallback · anchors/nav intactes · data contract respecté (aucune donnée inventée) · Auren scoped (pas de fuite globale).

## §23. Open Questions (avec recommandation produit)

| ID | Question | Options | **Recommandation V1** |
|---|---|---|---|
| **OQ-05-A** | Route `/` reste Today ou redirect vers Séance ? | (a) reste Today ; (b) redirect si session active ; (c) redirect toujours | **(a) reste Today** — le Home est la surface de décision ; si session active, le hero propose « Reprendre » sans forcer le redirect (préserve l'orientation). |
| **OQ-05-B** | Readiness = score numérique / bande qualitative / état textuel ? | (a) score 0-100 ; (b) bande qualitative ; (c) état textuel | **(b) bande qualitative** dérivée des scales existantes, **sans nouveau calcul** (agrégat = future) — conservateur, non médical. |
| **OQ-05-C** | Priorité si session active + séance prévue coexistent ? | (a) active domine ; (b) prévue domine ; (c) choix utilisateur | **(a) active domine** — reprendre l'en-cours prime (Today Decision Model §8). |
| **OQ-05-D** | Afficher une recommandation de repos ? | (a) oui, non impérative ; (b) non ; (c) seulement si readiness basse | **(a) oui, non impérative** — « Jour de repos possible » quand readiness basse + séance récente, jamais prescriptif. |
| **OQ-05-E** | Place de Body Representation sur Home V1 ? | (a) résumé léger ; (b) absent V1 ; (c) heatmap | **(a) résumé léger** (zones récentes / prochaine zone), optionnel, secondaire. **Pas de heatmap.** |
| **OQ-05-F** | Relation avec l'onglet Progression ? | (a) Home = snapshot + lien ; (b) Home = dashboard complet ; (c) pas de progress sur Home | **(a) snapshot + lien** — Home reste léger, la profondeur vit dans Progression. |
| **OQ-05-G** | Coach : micro-note ou absent ? | (a) micro-note contextuelle ; (b) absent ; (c) bloc dédié | **(a) micro-note contextuelle** (cohérent Sx_UI_03), jamais bavard/top-level. |
| **OQ-05-H** | Fallback nouvel utilisateur sans historique ? | (a) hero « Commencer » ; (b) onboarding ; (c) vide | **(a) hero « Commencer »** → premier programme/séance, sans métriques vides. |
| **OQ-05-I** | Home entièrement no-JS ? | (a) oui ; (b) enhancement JS optionnel ; (c) JS requis | **(a) oui** — Home 100% no-JS (SSR), cohérent avec le reste de l'app. |
| **OQ-05-J** | Niveau de personnalisation sans compte/settings additionnels ? | (a) aucune nouvelle pref ; (b) prefs légères ; (c) settings dédiés | **(a) aucune nouvelle pref** V1 — le Home s'adapte aux données existantes, pas de nouveau réglage. |

## §24. Acceptance criteria

Au futur build, un reviewer doit pouvoir dire : **« Ce n'est pas un tableau de bord ; c'est une surface qui me dit quoi faire aujourd'hui. »**

Critères :
- ✅ Une **CTA principale unique** dominante, résolue par le Today Decision Model.
- ✅ Session active reprenable immédiatement quand elle existe.
- ✅ Readiness présenté comme **repère self-report**, jamais diagnostic/score médical.
- ✅ Progress lisible en 5 s (snapshot + lien), pas un dashboard.
- ✅ Body continuity léger (si activé), pas de heatmap.
- ✅ Auren appliqué, scoped, pas de fuite globale.
- ✅ No-JS + WCAG 44×44 + mobile 360×640 + reduced-motion respectés.
- ✅ **Aucune donnée inventée** ; data contract §19 respecté.
- ✅ Baseline P0 capturable ; aucun PNG committé.

Rejet si : le Home reste un board de métriques · pas de CTA dominante · readiness affiché comme score médical · données physiologiques inventées · nouveau modèle/migration · Focus Mode modifié · no-JS cassé.

## §25. Non-goals

- ❌ Dashboard analytique complet.
- ❌ Score readiness pseudo-scientifique / médical.
- ❌ Données physiologiques inventées / inférence invisible.
- ❌ Modèle readiness backend nouveau / migration.
- ❌ Heatmap corporelle complète / profil Body Intelligence.
- ❌ Feed social / gamification / streaks / badges.
- ❌ Coach bavard top-level.
- ❌ Modification Focus Mode / réouverture Sx_UI_04.
- ❌ Rebrand SPIGNOS → Auren dans le code (Sx_UI_10).
- ❌ Ouverture Sx_UI_06.
- ❌ Release tag.
- ❌ React / SPA / bundler / dépendance front lourde.

## §26. Rollout / dependency map

- **Précondition** : Sx_UI_04 clos ✅ ; tokens Sx_UI_02 ✅ ; app shell Sx_UI_03 ✅.
- **Ordre** : Sb_UI_05.1 (IA + hero) → .2 (active/next) → .3 (readiness/recovery) → .4 (progress/body) → .5 (empty/a11y/hardening).
- **Aval** : `Sx_UI_06 Exercise Intelligence Presentation` (future) pourra approfondir la couche intelligence ; `Sx_UI_07 History & Progress` approfondira le progress renvoyé en lien par le Home.
- **Baseline** : chaque build `Sb_UI_05.k` conserve P0 capturable + anti-404 + aucun PNG committé.

## §27. Verdict attendu

- **READY FOR HUMAN REVIEW**
- **Aucun build ouvert** (Sb_UI_05.1 reste bloqué tant que cette spec n'est pas validée + OQ confirmées)
- **Aucune capture screenshot** dans ce sprint
- **Aucune release tag**

## §28. Références croisées

- Cycle précédent (clos) : `docs/SPRINT_Sx_UI_04_FINAL_CLOSEOUT_REPORT.md` + `docs/strategy/Sx_UI_04_FOCUSED_EXERCISE_FLOW_SPEC.md`
- Brand : `docs/strategy/Sx_UI_01_BRAND_FOUNDATION_SPEC.md`
- Tokens : `docs/strategy/Sx_UI_02_DESIGN_TOKENS_SPEC.md`
- App shell : `docs/strategy/Sx_UI_03_APP_SHELL_NAVIGATION_SPEC.md`
- Baseline P0 : `docs/BASELINE_P0_CAPTURED_2026_07_04.md`
- Home actuel (lecture only) : `app/templates/index.html` + `app/routers/pages.py::home`
- Readiness service (lecture only) : `app/services/readiness.py`
- Registry : `docs/strategy/SPEC_REGISTRY.md`
- Roadmap : `docs/strategy/ROADMAP_AND_NEXT_STEPS.md`
