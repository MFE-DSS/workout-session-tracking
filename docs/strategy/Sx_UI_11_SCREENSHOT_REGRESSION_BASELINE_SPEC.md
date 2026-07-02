# Sx_UI_11 — Screenshot Regression Baseline Spec

**Spec ID :** `Sx_UI_11_SCREENSHOT_REGRESSION_BASELINE_SPEC`
**Cycle :** `Sx_UI` — Auren Visual & Product Transformation
**Date d'ouverture :** 2026-07-02
**Auteur :** opérateur (Martin Feldmann) + agent Claude Code (docs-only)
**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`
**Depends on :**
- `Sx_UI_01_BRAND_FOUNDATION_SPEC.md` ✅ accepté
- `Sx_UI_02_DESIGN_TOKENS_SPEC.md` ✅ accepté
- `Sx_UI_03_APP_SHELL_NAVIGATION_SPEC.md` ✅ accepté

---

## §1. Status

- **SPEC ONLY**
- **BUILD NOT AUTHORIZED**
- **Docs-only strict**
- Aucun script ajouté (aucun `scripts/screenshot*.py`, aucun `tests/visual/*.py`)
- Aucun outil installé (Playwright, Puppeteer, snapshot-py — aucun)
- Aucun screenshot capturé
- Aucun package Python / Node ajouté aux dépendances
- Aucun CI workflow modifié (`.github/workflows/` intact)
- Aucun renommage `SPIGNOS` → `Auren` dans le code

## §2. Why this spec exists

`Sx_UI_04_SESSION_FOCUS_RESKIN_SPEC` sera le **premier sprint autorisé à modifier du code visuel** (surface CSS + templates, jamais services métier). Il consommera :

- les tokens de `Sx_UI_02` (palette teal chirurgical désaturé, mono metrics, spacing 4px-based)
- la structure de nav de `Sx_UI_03` (bottom nav 4 entrées, session active pattern, rail desktop)
- l'identité de `Sx_UI_01` (Auren wordmark — reporté à `Sx_UI_10` — tone of voice, principes visuels)

Sans une **baseline visuelle documentée avant reskin**, il est impossible de distinguer :

- **régression fonctionnelle** : un CTA qui n'est plus cliquable, un formulaire qui perd un champ
- **changement esthétique volontaire** : passage cockpit dark → clinical white attendu
- **drift accidentel** : un padding qui saute, une couleur qui perdure
- **perte de lisibilité mobile** : chevauchement bottom nav / sticky CTA, safe-area non respectée
- **régression a11y** : contraste dégradé, focus non visible, tap target < 44×44

Cette spec **n'implémente pas la baseline** — elle définit le **protocole** que consommera `Sb_UI_11.1` (Screenshot Tooling Build) au moment où l'opérateur autorisera un premier sprint de build.

## §3. Baseline purpose

Objectifs normatifs de la baseline :

1. **Documenter l'avant refonte** — état visuel SPIGNOS 2026-07-02 (SHA `88ca206` à la date d'ouverture de cette spec) figé comme référence historique et comparateur de reskin.
2. **Protéger les flux critiques** — priorité 1 aux écrans que les utilisateurs traversent chaque séance : Home/Today, Session detail active, Session done, Progression.
3. **Permettre comparaison human review** — pendant `Sx_UI_04` PR review, les screenshots avant/après doivent apparaître côte à côte pour valider explicitement les changements.
4. **Vérifier que le reskin Auren ne casse pas** :
   - la navigation (10 destinations → 4 bottom nav sans perdre de features)
   - la session detail (sticky header, jump bar, sticky CTA, rest timer conservés)
   - les CTA primaires (poids-reps logging à ≤ 3s de friction)
   - le no-JS fallback (chargement sans JS reste utilisable)
   - les états vides (empty states cohérents, pas de "Whitescreen")

**Non-objectifs :**
- Pas de baseline "pixel-perfect" — les screenshots servent à la revue humaine, pas à un gate binaire strict.
- Pas de test unitaire visuel — les tests HTML structurels (`test_body_intelligence_route.py` et al.) restent la source de vérité fonctionnelle.

## §4. Tooling decision

**Comparaison rapide des options :**

| Outil | Force | Faiblesse |
|---|---|---|
| **Playwright** | Standard web, contrôle viewports, compatible SSR/Jinja, multi-browser (Chromium/Firefox/WebKit), scriptable Python + Node | Dépendance lourde (~200 MB binaires), Node.js pour CLI native ; wrapper Python OK mais moins mature |
| **Puppeteer** | Léger, Chromium seul | Node-only, un seul navigateur ; suffit pour V1 mais moins portable |
| **Percy / Chromatic / SaaS externe** | Diff visuel géré, historique, revue équipe | Coût récurrent, dépendance vendor, secret token à gérer, moins bien pour un solo maintainer |
| **Screenshots manuels navigateur** | Zéro dépendance | Non reproductible, humain-dépendant, aucune convention |
| **pytest + screenshot custom (Selenium ou WebDriver bas niveau)** | Intégration test suite existante | Réinvention, brittle |

**Recommandation V1 : Playwright (Python binding).**

Rationale :

- Standard web reconnu (Microsoft, adoption massive)
- Contrôle précis des viewports (`viewport={"width": 360, "height": 640}`)
- Compatible SSR (récupère la page rendue serveur, pas de client-side hydration à attendre)
- Une seule dépendance : `pip install playwright` + `playwright install chromium`
- Utilisable en local (Sb_UI_11.1) **et** en CI plus tard (Sb_UI_11.2 si nécessaire) sans changer d'outil
- Compatible fixture pytest (`playwright pytest` plugin)
- Python-first — cohérent avec le stack backend du repo

**Ce sprint n'installe pas Playwright.** L'installation, la configuration `conftest.py`, et le premier `capture.py` relèveront de `Sb_UI_11.1` — sprint de build ultérieur qui **touchera** `.github/workflows/`, `scripts/`, ou `tests/` selon décision opérateur.

## §5. Screenshot matrix

Matrice normative des écrans à capturer par la baseline. Les routes sont **existantes** en 2026-07-02 (inventoriées par grep sur `app/routers/*.py`).

| # | Page | Route | Auth required | Data fixture required | Mobile 360×640 | Desktop 1440×900 | Priority | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | Home / Today | `/` | ✅ | user + optional active session | ✅ | ✅ | P0 | Point d'entrée quotidien, absorbé par Séance V1 |
| 2 | Home no-active-session | `/` | ✅ | user sans session active | ✅ | ✅ | P0 | Empty state critique |
| 3 | Session detail active | `/sessions/{id}` | ✅ | session en cours + 3 exos (1 done, 1 active, 1 future) | ✅ | ✅ | P0 | Cœur du produit, focus mode Sx_29 |
| 4 | Session detail done | `/sessions/{id}` (session terminée) | ✅ | session `status=completed` avec logs | ✅ | ✅ | P0 | Review post-séance |
| 5 | Programmes / library | `/library` | ✅ | catalogue seedé (existant) | ✅ | ✅ | P1 | Bibliothèque templates |
| 6 | Program detail | `/library/{slug}` | ✅ | 1 template slug valide | ✅ | ✅ | P1 | Détail template avant lancement |
| 7 | Progression | `/progress` | ✅ | user avec ≥ 3 séances loggées | ✅ | ✅ | P0 | Absorbe Historique + Physique + Coach insights en V1 Auren |
| 8 | Progression empty | `/progress` | ✅ | user sans historique | ✅ | ✅ | P1 | Empty state critique |
| 9 | Historique | `/history` | ✅ | user avec historique | ✅ | ✅ | P1 | Sera absorbé sous Progression en V1 Auren |
| 10 | Physique | `/physique` | ✅ | user avec ≥ 1 measurement | ✅ | ✅ | P1 | Sera absorbé sous Progression en V1 Auren |
| 11 | Profil | `/profile` | ✅ | user standard | ✅ | ✅ | P0 | Contient carte Body Intelligence (Sx_31 OQ-G) |
| 12 | Coach report | `/coach-report` | ✅ | user avec ≥ 1 séance | ✅ | ✅ | P1 | Sera contextualisé en V1 Auren (§11 Sx_UI_03) |
| 13 | Body Intelligence | `/body/intelligence` | ✅ | `BODY_INTELLIGENCE_ENABLED=true` | ✅ | ✅ | P1 | 7 blocs + badges Mesuré/Dérivé/Inféré/Hors de portée |
| 14 | Leaderboard | `/leaderboard` | ✅ | opt-in, données ranking | ✅ | ✅ | P2 | Sera rétrogradé vers Profil secondaire V1 Auren |
| 15 | Squads list | `/squads` (existant) | ✅ | 0 ou 1+ squads | ✅ | ✅ | P2 | Sera rétrogradé vers Profil secondaire V1 Auren |
| 16 | Login | `/login` | ❌ | anonyme | ✅ | ✅ | P0 | Point d'entrée public |
| 17 | Register | `/register` | ❌ | anonyme | ✅ | ✅ | P0 | Point d'entrée public |
| 18 | Forgot password | `/forgot-password` | ❌ | anonyme | ✅ | ✅ | P2 | Écran occasionnel |

**Compte total baseline V1 :**

- P0 (critique, obligatoire pour Sx_UI_04) : 7 écrans × 2 viewports = **14 screenshots**
- P1 (haut, recommandé avant Sx_UI_04) : 8 écrans × 2 viewports = **16 screenshots**
- P2 (moyen, différable) : 3 écrans × 2 viewports = **6 screenshots**
- **Total maximal : 18 écrans × 2 viewports = 36 screenshots**
- **Baseline minimale acceptable pour débloquer Sx_UI_04 : P0 seuls = 14 screenshots** (dérogation §14)

**Note importante :** cette matrice inclut 5 écrans supplémentaires par rapport aux 13 écrans indiqués dans `Sx_UI_03 §19` — l'inventaire des routes a révélé `/library/{slug}`, `/forgot-password`, home no-active-session (variante), progression empty (variante), session done (variante). Ces variantes valident les empty states, critiques pour éviter les régressions "whitescreen" post-reskin.

## §6. Auth strategy

Comment les captures gèrent l'authentification :

**Règles normatives :**

- **User connecté** : cookie de session obtenu via un POST /login préalable dans le script de capture, jamais via un cookie hardcodé.
- **Compte de test local** : utiliser un compte dédié fixture (`baseline_user_local`), **jamais** un compte prod (`martin_prod_smoke_20260702_1037` ou similaire).
- **Login screen (anonyme)** : GET `/login` sans cookie préalable.
- **Register screen (anonyme)** : GET `/register` sans cookie préalable.
- **Routes privées** : redirect 303 → `/login` attendu si non-authentifié. La capture peut valider ce comportement (screenshot du login).
- **État anonyme sur page publique** : `/healthz`, `/rules`, `/science` — pas de cookie.

**Interdit :**

- ❌ **Jamais de password en clair dans scripts, logs, commits.** Utiliser :
  - variables d'environnement (`BASELINE_USER`, `BASELINE_PASSWORD`) — chargées depuis un `.env.baseline` local **non versionné** (`.gitignore` requis)
  - ou fixture pytest qui crée le user à la volée avec un password random puis logge
- ❌ Aucun secret prod. Aucun réutilisation de credentials smoke.
- ❌ Aucun logging du password (`--verbose` interdit sur curl/playwright quand secret transite).

**Recommandation V1 :**

Playwright fixture crée un user de test au démarrage de la baseline (call à `/register` avec username `baseline_YYYYMMDD_HHMM` + password random 24-chars alphanumériques), le stocke en mémoire de session pytest, l'utilise pour toutes les captures P0/P1 privées, puis expire naturellement (le user reste dans la DB de test, jamais en prod).

## §7. Data fixture strategy

États nécessaires pour peupler les captures P0/P1.

**Recommandation V1 :** créer une **fixture déterministe locale**, jamais dépendante de prod.

**États à provisionner :**

| Fixture ID | Description | Utilisé par |
|---|---|---|
| `db.empty` | DB fraîche, aucun user, aucune session | Register, Login |
| `db.user.standard` | Compte user + password créés, aucun historique | Home no-active, Progression empty |
| `db.user.with_history` | User + 3-5 séances complètes loggées (chargées via seed déterministe) | Home, Session done, Progression, Historique, Coach report |
| `db.user.with_active_session` | User + 1 session en cours (3 exos, 1 done, 1 active, 1 future) | Home avec active, Session detail active |
| `db.user.with_measurements` | User + 1-3 body measurements | Physique |
| `db.body_intelligence.enabled` | Flag `BODY_INTELLIGENCE_ENABLED=true` + user avec historique | Body Intelligence |

**Interdit :**

- ❌ Fixture dépendante de prod (jamais de dump `/opt/workout-session-tracking/var/workout.db` copié)
- ❌ Fixture non déterministe (pas de random seed non-stable, pas de timestamps courants)
- ❌ Fixture qui traverse le réseau (pas d'appel API externe)

**Storage fixture :** JSON ou script Python seedé, versionné dans `tests/fixtures/baseline/` (à créer en `Sb_UI_11.1`, hors-scope de cette spec).

## §8. Session active scenario

Scénario précis à capturer pour "Session detail active" (P0, entrée #3 de la matrice §5).

**Composition minimale :**

- 1 session en cours (`status="in_progress"`)
- Session avec **≥ 3 exercices** dans le template :
  - Exercice #1 : **done** (2-3 séries loggées avec poids × reps)
  - Exercice #2 : **active** (curseur / focus attendu, aucune série loggée encore)
  - Exercice #3 : **future** (grisé ou visuellement en attente)
- **Sticky CTA visible** ("Logger" / "Continuer") au bas de l'écran mobile 360×640
- **Rest timer** : si session détient un timer actif, il apparaît dans le partial `_partials/rest_timer.html` (Sx_29). Sinon état neutre.
- **Jump bar** (`.ex-jump`) : visible en haut, avec 3 pastilles reflétant done/active/future
- **Header sticky** : nom template snapshot + progression (X / Y séries loggées) + note optionnelle

**Viewports :**

- Mobile 360×640 : capture pleine hauteur, scroll simulé jusqu'à voir l'exercice actif ET le sticky CTA
- Desktop 1440×900 : capture pleine hauteur (probablement pas de sticky CTA si viewport suffisamment large)

**Non-goals du scénario :**

- Pas de coach report affiché
- Pas de body intelligence intégrée dans la session detail
- Pas de body capture-quality (flag OFF, 404)

## §9. No-JS / reduced-motion scenario

**Recommandation V1 :**

- **JS enabled par défaut** pour tous les screenshots baseline. Playwright charge le DOM après tous les scripts.
- **No-JS baseline séparée : hors-scope V1.** Le no-JS fallback est **déjà validé** par la suite de tests existants (`test_session_focus_layout.py`, `test_session_focus_navigation.py`, `test_session_focus_sticky_cta.py`, `test_session_focus_rest_timer.py` de Sx_29). Une baseline visuelle no-JS peut être ajoutée en `Sb_UI_11.2` optionnel si demande explicite.
- **`prefers-reduced-motion` emulation** : reporté à `Sx_UI_09` (Accessibility & Motion Spec). Playwright supporte `emulate_media(reduced_motion="reduce")` — mais la décision d'inclure cette variante dans la baseline appartient à Sx_UI_09.
- **Zoom / text scaling** : hors-scope V1. Peut être ajouté en test ciblé plus tard, pas dans la baseline générale.

Justification : ajouter chaque variante multiplie le compte de screenshots (× 2 no-JS, × 2 reduced-motion, × 2 text-scaled = ×8 potentiel). Concentrer V1 sur le mode par défaut suffit à protéger 95 % des régressions visuelles.

## §10. File storage strategy

**Comparaison rapide :**

| Option | Force | Faiblesse |
|---|---|---|
| **Versionnés dans repo** (`baseline/` git-tracked) | Historique lisible, diff par commit, portable | Taille repo qui gonfle (36 PNG × ~50-200 KB = 2-7 MB baseline initiale ; multipliée par les updates), git peut devenir lent |
| **Artefacts CI** (GitHub Actions artifact retention) | Aucun impact taille repo, historique retenu par CI | Rétention limitée (90j par défaut), coût artefact, moins reviewable en PR |
| **Locaux non commités** (`.gitignore` sur `baseline/`) | Zéro impact repo | Aucun partage, aucun historique cross-machine |
| **Hybrid (git-tracked pour P0 uniquement + artefacts CI pour tous)** | Compromis équilibré | Complexité de config |

**Recommandation V1 :**

- **Baseline non versionnée par défaut** au premier `Sb_UI_11.1`. `.gitignore` sur `baseline/` ou `tests/visual/baseline/`.
- **Sauvegarde locale** dans le dossier utilisateur (`~/.spignos-baseline/` ou équivalent) pendant `Sb_UI_11.1`, décision de storage définitif à trancher en fin de sprint build.
- **Alternative envisageable pour finalisation :** artefact CI + release git tag `baseline-2026-07-02-preauren`. Les 36 screenshots sont uploadés une fois comme artefact, référencés par URL depuis un `docs/baselines/INDEX.md`.

**Décision finale reportée à `Sb_UI_11.1`** — cette spec définit les options acceptables.

## §11. Naming convention

Convention normative pour les fichiers baseline :

```
baseline/{page-slug}/{viewport}-{state}.png
```

**Composants :**

- `page-slug` : slug kebab-case dérivé de la matrice §5 (`home`, `session-detail`, `progress`, etc.)
- `viewport` : `mobile` (360×640) ou `desktop` (1440×900)
- `state` : `authenticated`, `anonymous`, `active`, `done`, `empty`, `with-history`, etc.

**Exemples :**

```
baseline/home/mobile-authenticated.png
baseline/home/mobile-authenticated-no-active-session.png
baseline/home/desktop-authenticated.png
baseline/session-detail/mobile-active.png
baseline/session-detail/mobile-done.png
baseline/session-detail/desktop-active.png
baseline/progress/mobile-with-history.png
baseline/progress/mobile-empty.png
baseline/profile/mobile-authenticated.png
baseline/body-intelligence/mobile-flag-on.png
baseline/coach-report/mobile-with-history.png
baseline/leaderboard/mobile-opt-in.png
baseline/login/mobile-anonymous.png
baseline/register/mobile-anonymous.png
```

**Règles :**

- Kebab-case strict (jamais snake_case, jamais CamelCase)
- Pas de timestamp dans le nom (le git tag ou l'artefact CI porte le contexte temporel)
- Pas de suffixe `.v1`, `.v2` — versioning porté par git / release
- Pas de nom de user (le compte fixture est un détail d'implémentation)

## §12. Diff tolerance

Principes normatifs pour les comparaisons visuelles ultérieures (`Sb_UI_11.2` si outillage diff installé) :

- **Tolérance faible pour layout shift** — un décalage vertical/horizontal ≥ 4 pixels (`--space-1`) sur un élément signifiant (CTA, header, sticky nav) est **rejeté par défaut**, revue humaine obligatoire.
- **Tolérance plus souple pour antialiasing** — les différences pixel-perfect sur du texte anti-aliasé (Δ ≤ 2 sur 256 par pixel) sont **acceptées** — le rendu variant selon OS/browser.
- **Aucun blocage sur pixel-perfect si pas pertinent** — les micro-variations de police, ombres subtiles (`--shadow-sm`), timestamp affichés dynamiquement — ne bloquent pas.
- **Revue humaine obligatoire pour changements intentionnels** — tout reskin (`Sx_UI_04` et suivants) génère explicitement des différences. Le workflow attendu :
  1. `Sx_UI_04` produit un patch code visuel
  2. Baseline courante montre "avant"
  3. Capture new montre "après"
  4. PR review humaine juge : "changement voulu" ✅ ou "régression accidentelle" ❌
  5. Si voulu → baseline rebasée sur le nouveau state après merge
- **Aucun gate CI binaire strict** V1 — la baseline sert la revue, pas l'automatisation coercitive.

**Seuils numériques à trancher en `Sb_UI_11.2` (OQ-Z).** Cette spec pose les principes, pas les paramètres.

## §13. Accessibility visual checks

Ce que les screenshots doivent aider à vérifier lors de la revue humaine :

- **Tap targets non masqués** : sur mobile, aucune zone tactile ne doit être recouverte par la bottom nav ou le sticky CTA
- **Bottom nav non chevauchante** : sur mobile, la bottom nav ne cache pas le dernier élément de contenu (padding-bottom suffisant sur le body scroll)
- **Sticky CTA visible** : sur session detail mobile, le CTA "Logger" reste visible pendant tout le scroll de la carte active
- **Safe-area** : le padding-bottom respecte `env(safe-area-inset-bottom)` — vérifiable sur les screenshots iOS-like (Playwright supporte `has_touch` + `device_scale_factor` sur mobile viewport)
- **Contraste perçu** : les textes body (`--color-fg-default`) sont **lisibles** sur les fonds (`--color-bg-base`, `--color-bg-elevated`, `--color-surface-alt`). Vérification par l'œil humain V1 ; outillage automatisé possible en `Sb_UI_11.2`.
- **Lisibilité métriques** : les valeurs mono (`--font-family-mono`, `tabular-nums`) sont alignées verticalement dans les listes de séries
- **Aucun horizontal scroll** : `overflow-x: hidden` respecté ; le contenu ne dépasse jamais du viewport 360px

**Non-goals a11y automatisés :**

- Pas de tests axe-core / Lighthouse dans cette spec — relève de `Sx_UI_09`
- Pas de vérification contraste programmatique — la revue humaine des baselines suffit V1

## §14. Sx_UI_04 dependency

**Règle dure :** `Sx_UI_04` build ne peut pas démarrer tant que :

1. **`Sx_UI_11` spec est acceptée** (cette spec, en human review post-livraison)
2. **Baseline strategy est validée** — les OQ V1 tranchées par l'opérateur (§19)
3. **Au minimum les écrans P0 sont capturables** — tooling `Sb_UI_11.1` livré, ou au moins un script minimal Playwright fonctionnel local ; les 14 screenshots P0 disponibles pour comparaison "avant"
4. **OU dérogation humaine explicite documentée** — l'opérateur peut lever la précondition baseline via un override écrit (comme `Sb_28.override-build-authorization`), en acceptant explicitement de perdre la comparaison avant/après.

**Rationale de la règle stricte :**

Sans baseline, `Sx_UI_04` review devient une revue "à l'aveugle" — impossible de valider qu'un changement CSS ne casse pas un empty state ou un état de session active. La discipline spec-driven du repo (`docs/strategy/SPEC_DRIVEN_ENGINEERING_PROTOCOL_v1.md §9` sur les dogfoods) applique ici la même logique aux reskins : pas de proof visuelle avant/après ⇒ pas de build.

**Alternative pragmatique acceptable si tooling `Sb_UI_11.1` s'avère trop lourd :**

- Screenshots manuels sur navigateur physique avec convention nommage §11 respectée
- Uploadés dans un release tag `baseline-preauren-2026-XX-XX`
- Référencés dans `docs/baselines/INDEX.md`
- Suffisant pour comparaison PR review, insuffisant pour test régression automatisé futur

## §15. CI policy

**Spec `Sx_UI_11` = docs-only pur** : push actuel ne touche que `docs/`, **path filter `Sb_OPS.ci-path-filter` skippe la CI** (comportement validé sur `b3ae3a9`, `fdfd71a`, `88ca206`).

**Futur `Sb_UI_11.1` (build tooling)** :

- Touchera potentiellement `scripts/`, `tests/`, `.github/workflows/`, `requirements-lock.txt`, `pyproject.toml`
- **Déclenchera une CI complète** au push (aucun fichier sous `docs/` = `paths-ignore` ne s'applique pas)
- Devra passer les gates existants : `check_ruff_budget`, `check_spec_protocol`, `pip-audit`, `gitleaks`, `bandit`, etc.
- Si Playwright installé, ajouter cache CI pour éviter le download des 200 MB de binaires à chaque run

**Règle stricte :** ne pas mélanger spec Sx_UI_11 et install de tooling dans le même commit. Les deux vivent dans des sprints séparés :

- `Sx_UI_11` = SPEC ONLY (docs, cette spec) → push docs-only, CI skip
- `Sb_UI_11.1` = BUILD (install + premier capture.py + fixtures) → push full, CI complète

## §16. Risks

Risques identifiés + mitigations proposées.

| Risque | Impact | Mitigation |
|---|---|---|
| **Screenshots trop fragiles** (moindre changement font système déclenche diff) | Faux positifs paralysants | Diff tolerance §12 souple, revue humaine primaire, pas de gate CI strict V1 |
| **Données non déterministes** (timestamps courants, IDs UUID, séquences aléatoires) | Diff inutile à chaque run | Fixture déterministe §7, freeze `Date.now()` via Playwright `page.clock.install()` |
| **Secrets dans scripts ou logs** | Compromission credentials | `.env.baseline` git-ignore, `--data-urlencode` masqué, no `--verbose` |
| **Dépendance navigateur lourde** (200 MB Chromium sur chaque runner) | Coût CI + temps de setup | Cache CI action Chromium, éventuellement Playwright hosted par Microsoft |
| **Storage baseline trop volumineux** (36 × 200 KB × N versions = plusieurs MB rapidement) | Repo lourd | Baseline non versionnée par défaut §10, artefact CI + release tag |
| **Faux sentiment de sécurité pixel-perfect** | Régressions logiques masquées | Revue humaine primaire, tests HTML structurels restent la référence fonctionnelle |
| **Baseline devient stale** (drift silencieux si non maintenue) | Baseline inutile après quelques mois | Baseline rebasée automatiquement après chaque `Sx_UI_*` accepté, tag release par sprint |
| **Injection de comptes de test en prod** | Pollution DB prod | Fixture strictement local, jamais en prod (§6, §7) |

## §17. Non-goals

- **Pas de Playwright installé** dans ce sprint
- **Pas de `pip install`, `npm install`, ou modification `requirements*.txt`, `pyproject.toml`, `package.json`**
- **Pas de package ajouté** aux dépendances
- **Pas de script screenshot** créé (`scripts/capture_baseline.py` ou équivalent)
- **Pas de CI modifiée** (`.github/workflows/` intact)
- **Pas de screenshot capturé** — aucun `.png` produit dans ce commit
- **Pas de CSS applicatif** modifié
- **Pas de template** modifié
- **Pas de JS** modifié
- **Pas d'asset** (icône, image, police web) ajouté
- **Pas de route** ajoutée / modifiée / redirigée
- **Pas de migration** Alembic
- **Pas de modèle SQLAlchemy** modifié
- **Pas de build** (`Sb_UI_11.k` non ouvert)
- **Pas d'auth de test** implémenté (fixture user reste théorique dans cette spec)
- **Pas de logo** / manifest modifié
- **Pas de renommage** SPIGNOS → Auren dans le code
- **Pas de flag toggle** modifié

## §18. Acceptance criteria

La spec est acceptable si :

- ✅ Matrice screenshots définie (§5, 18 écrans × 2 viewports = 36 max, 14 P0 minimum)
- ✅ Viewports définis (360×640 mobile + 1440×900 desktop)
- ✅ Outil recommandé et justifié (Playwright Python binding, §4)
- ✅ Stratégie auth décrite avec règle anti-secret (§6)
- ✅ Stratégie fixtures décrite avec 6 fixture IDs (§7)
- ✅ Session active scenario décrit précisément (§8)
- ✅ Storage options documentées avec recommandation V1 (§10)
- ✅ Convention nommage définie (§11)
- ✅ Diff tolerance principes posés (§12)
- ✅ Dépendance `Sx_UI_04` explicitée avec règle dure + alternative pragmatique (§14)
- ✅ Politique CI clarifiée : spec docs-only vs build tooling full-CI (§15)
- ✅ Risques identifiés avec mitigations (§16)
- ✅ Non-goals explicites (§17)
- ✅ OQ énumérées avec recommandation V1 (§19)
- ✅ Aucun fichier `app/`, `tests/`, `migrations/`, `scripts/`, `.github/`, static asset modifié

## §19. Open Questions

Rappel des OQ liées à screenshot regression + résolutions V1.

| OQ | Question | Recommandation V1 (cette spec) | Statut |
|---|---|---|---|
| **OQ-G** | Playwright confirmé pour screenshot regression ? | **✅ oui** — cf. §4. Alternatives Puppeteer / SaaS écartées V1. | ✅ tranché V1 |
| **OQ-V** | Screenshots versionnés dans repo ou artefacts CI ? | **artefacts CI + release tag** V1. `.gitignore` sur `baseline/` local. Réversible en `Sb_UI_11.1`. | ✅ tranché V1 (réversible) |
| **OQ-W** | Fixture DB dédiée ou seed existant ? | **fixture dédiée** V1 (6 IDs §7), 100 % locale. Seed existant (`data/reference_split.json`) réutilisé pour le catalogue. | ✅ tranché V1 |
| **OQ-X** | Screenshots sur CI ou local seulement ? | **local seulement V1** (`Sb_UI_11.1`), CI optionnelle en `Sb_UI_11.2` si nécessaire. | ✅ tranché V1 |
| **OQ-Y** | No-JS baseline séparée ou tests HTML existants suffisent ? | **tests HTML suffisent V1** (Sx_29 suite validée). No-JS baseline reportée à `Sb_UI_11.2` optionnel. | ✅ tranché V1 |
| **OQ-Z** | Seuil de diff visuel strict ou review humaine prioritaire ? | **review humaine prioritaire V1**. Seuils numériques automatisés reportés à `Sb_UI_11.2`. Principes §12 posés. | ✅ tranché V1 (paramètres différés) |
| **OQ-AA** | Playwright Python binding vs CLI Node ? | **Python binding V1** (cohérence stack backend). Réversible si friction. | ✅ tranché V1 (réversible) |
| **OQ-AB** | Baseline captures P0 seulement (dérogation §14 acceptable) ou P0+P1 obligatoires avant Sx_UI_04 ? | **P0 obligatoires, P1 recommandés, P2 différables**. Dérogation P0-only autorisée avec override opérateur explicite. | ✅ tranché V1 |

**Aucune OQ ne bloque l'ouverture de `Sx_UI_04` SPEC ONLY** — mais la baseline P0 doit exister avant le premier code applicatif Sx_UI_04.

## §20. Build authorization status

**BUILD NOT AUTHORIZED.**

**Next action after human validation of this spec :**

Deux options possibles selon décision opérateur :

**Option A (recommandée) :** `Sx_UI_04_SESSION_FOCUS_RESKIN_SPEC` **SPEC ONLY**.
Rationale : produire la spec du reskin session en parallèle du build baseline `Sb_UI_11.1`. Les deux sprints peuvent progresser sans se bloquer mutuellement. Le premier code applicatif `Sx_UI_04` (`Sb_UI_04.k`) reste bloqué jusqu'à disponibilité baseline P0.

**Option B :** `Sb_UI_11.1_SCREENSHOT_TOOLING_BUILD` **BUILD**.
Rationale : outiller la baseline avant d'écrire la spec Sx_UI_04. Sprint hors-cycle Sx_UI, car il touche `scripts/`, `tests/`, potentiellement `.github/workflows/`. **Déclenchera une CI complète** au push (comportement voulu).

**Non autorisé :**

- Aucun sprint `Sb_UI_11.k` d'implémentation ouvert automatiquement — override explicite requis
- Aucun fichier `app/`, `tests/`, `migrations/`, `.github/workflows/`, config runtime, `.env`, manifest, static assets modifié par cette spec
- Aucun `pip install`, `npm install`, aucune modification `requirements-lock.txt`
- Aucun renommage `SPIGNOS` → `Auren` dans le code

`Sx_UI_04` (Session Focus Reskin — premier sprint autorisé à toucher du code visuel) reste bloqué par (cumul depuis Sx_UI_01) :

1. `Sx_UI_01` ✅ accepté
2. `Sx_UI_02` ✅ accepté
3. `Sx_UI_03` ✅ accepté
4. `Sx_UI_11` (cette spec) — pending human review
5. `Sb_UI_11.1` (baseline tooling) livré ou dérogation opérateur explicite
6. Baseline P0 disponible (14 screenshots minimum)
7. OQ résiduelles Sx_UI_02 tranchées (OQ-H hex, OQ-I sans, OQ-J mono, OQ-K scale, OQ-M naming)
8. OQ résiduelle Sx_UI_03 (OQ-R Progression sub-nav)

## §21. Final verdict

**READY FOR HUMAN REVIEW.**

---

## Références

- **Spec précédente :** `docs/strategy/Sx_UI_03_APP_SHELL_NAVIGATION_SPEC.md` ✅ accepted
- **Specs avant :** `docs/strategy/Sx_UI_02_DESIGN_TOKENS_SPEC.md`, `docs/strategy/Sx_UI_01_BRAND_FOUNDATION_SPEC.md` ✅ accepted
- **Roadmap cycle :** `docs/strategy/UI_TRANSFORMATION_ROADMAP.md`
- **Registry :** `docs/strategy/SPEC_REGISTRY.md` §1quinquies
- **Roadmap globale :** `docs/strategy/ROADMAP_AND_NEXT_STEPS.md`
- **Brainstorm sources :** `docs/strategy/brainstorm/UI_TRANSFORMATION_BRAINSTORM_V1_normalized.md`, `..._V2_normalized.md`
- **Focus mode précurseur (SSR/Jinja/no-JS pattern hérité) :** `docs/strategy/Sx_29_CLOSURE_REPORT.md` + `docs/dogfood/DOGFOOD_Sx_29_FOCUS_MODE_TEMPLATE.md`
- **CI cost optimization :** `docs/SPRINT_Sb_OPS_ci_path_filter_BUILD_REPORT.md` (path filter opérationnel, 5 pushes docs-only skippés)
