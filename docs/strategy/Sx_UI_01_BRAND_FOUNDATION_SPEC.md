# Sx_UI_01 — Brand Foundation Spec

**Spec ID :** `Sx_UI_01_BRAND_FOUNDATION_SPEC`
**Cycle :** `Sx_UI` — Auren Visual & Product Transformation
**Date d'ouverture :** 2026-07-02
**Auteur :** opérateur (Martin Feldmann) + agent Claude Code (docs-only)
**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6`

---

## §1. Status

- **SPEC ONLY**
- **BUILD BLOCKED**
- **Auren** posé comme **working brand candidate** (product direction approved)
- **Legal/domain verification pending** — checklist §5
- **No app code touched** dans ce sprint (docs-only strict)
- Next authorized action after human validation : ouvrir `Sx_UI_02_DESIGN_TOKENS_SPEC` en SPEC ONLY

## §2. Why this spec exists

La transformation UI ne doit **pas** commencer par du CSS, un logo, un manifest, ou un renommage de templates. Ces mouvements, s'ils précèdent la fixation du langage produit, produisent un patchwork visuel et lexical impossible à réconcilier ultérieurement.

Cette spec **précède** toute décision d'implémentation. Elle sert de socle référentiel pour :

- toutes les specs UI ultérieures (`Sx_UI_02` → `Sx_UI_11`) qui devront s'y aligner en tone, positionnement, benchmarks, principes visuels autorisés/interdits ;
- toute décision de build (sprints `Sb_UI_NN.k`) qui devra pouvoir citer cette spec comme source de vérité de la marque et du langage produit ;
- toute décision de rebrand (`Sx_UI_10`) qui devra hériter du nom Auren et de son statut de working brand candidate documenté ici.

Cette spec **empêche** :

- le drift visuel (chaque écran conçu isolément avec son propre langage) ;
- le drift lexical (voix produit incohérente entre `/profile`, `/coach-report`, `/body/intelligence`, etc.) ;
- l'engagement prématuré sur un nom non vérifié juridiquement ;
- le mélange avec la logique métier (règle absolue du cycle Sx_UI).

## §3. Product diagnosis

Diagnostic hérité des brainstorms `docs/strategy/brainstorm/UI_TRANSFORMATION_BRAINSTORM_V1_normalized.md` et `..._V2_normalized.md`, ainsi que de l'observation directe du repo au SHA `1e4cd4c` :

- **SPIGNOS est fonctionnellement robuste.** Le repo dispose déjà d'une base SSR FastAPI + Jinja + SQLite, d'un mode séance mobile-first extrait dans `session_focus.css` (livré par Sx_29, closure `docs/strategy/Sx_29_CLOSURE_REPORT.md`), d'un fallback no-JS préservé, et d'une culture de livraison spec-driven avec closure reports.
- **La surface produit la plus forte aujourd'hui = le mode séance.** Le focus mode Sx_29 (header sticky, jump bar, carte active, sticky CTA, rest timer, `44×44` tap targets, non-color cues WCAG 1.4.1) est le prototype le plus proche du produit cible. Cf. `docs/dogfood/DOGFOOD_Sx_29_FOCUS_MODE_TEMPLATE.md` dont le verdict opérateur est ✅ satisfait.
- **Le problème n'est pas structurel — il est langagier.** Le design system public reste « cockpit dark utility » : fond sombre, surfaces empilées, accent orange chaud, chrome relativement lourd, 10 entrées de navigation au premier niveau. Cela lit comme « console d'opérateur », pas comme « produit biométrique chirurgical ».
- **La transformation est une migration de langage produit, pas une réécriture.** Ni changement de stack, ni React, ni SPA, ni bundler. Le SSR + Jinja + no-JS fallback reste. Ce qui change : la grammaire visuelle, la hiérarchie informationnelle, le tone of voice, et éventuellement le nom.

## §4. Brand hypothesis — Auren

**Hypothèse de travail :**

**Auren** est une application mobile-first de **performance corporelle**, qui aide à exécuter, mesurer et piloter l'entraînement avec une interface calme, précise et instrumentale.

**Attributs cibles :**

- **Court** — 5 lettres, mono-syllabe ou di-syllabe court, mémorisable.
- **Premium** — sonne santé-tech, pas gym-utility.
- **Calme** — n'évoque pas l'agression, la performance brute, ou le coaching motivationnel.
- **International** — prononçable en français et en anglais, sans consonne difficile.
- **Santé-tech** — proche de l'univers de Levels, Oura, Apple Health, plutôt que de Strong ou Hevy.
- **Instrument, pas coach** — nom qui pourrait figurer sur un appareil de mesure, pas sur une salle de sport.

**Contraintes explicites :**

- ❌ **Non validé juridiquement.** Aucune vérification INPI, EUIPO, USPTO, WIPO n'a été effectuée à la date d'ouverture de cette spec. Cf. §5.
- ❌ **Non validé domaine.** Aucun `auren.*` n'est réservé. Cf. §5.
- ❌ **Pas encore activé dans le code.** Aucun template, aucun manifest, aucune config, aucun service, aucun test n'a été modifié pour introduire le nom Auren. Le rebrand réel est réservé à `Sx_UI_10_REBRAND_MIGRATION_SPEC`, jamais avant.
- ✅ **Auren peut être utilisé dans les specs comme nom cible** de référence conceptuelle et de direction produit — tant que le statut « working brand candidate » est rappelé explicitement.

## §5. Naming due diligence gate

Cette section liste la due diligence obligatoire **avant** que Auren puisse être considéré comme marque figée. Tant que cette checklist n'est pas complétée avec verdict favorable, Auren reste `working brand candidate`.

**Registres officiels :**

- [ ] **INPI** (France) — recherche « Auren » classes de Nice 9 (logiciels), 42 (services SaaS), 44 (santé) — vérifier antériorités
- [ ] **EUIPO** (Union Européenne) — recherche « Auren » mêmes classes
- [ ] **USPTO** (États-Unis) — recherche « Auren » mêmes classes
- [ ] **WIPO Global Brand Database** — recherche internationale, si activité prévue hors UE/US

**Domaines cibles :**

- [ ] `auren.com` — disponibilité + coût acquisition
- [ ] `auren.app` — disponibilité
- [ ] `auren.health` — disponibilité
- [ ] `auren.fit` — disponibilité
- [ ] `auren.training` — disponibilité

**Handles sociaux :**

- [ ] Instagram `@auren` / `@auren.app` / `@auren_health`
- [ ] Twitter/X `@auren` / `@auren_app`
- [ ] TikTok `@auren` / `@auren.app`

**Recherche acteurs existants :**

- [ ] Google recherche « Auren app », « Auren fitness », « Auren health », « Auren training »
- [ ] LinkedIn : entreprises nommées Auren dans les secteurs santé/fitness/tech
- [ ] App Store + Google Play : apps déjà nommées Auren ou proches phonétiquement

**Décision de gate :**

- Si **≥ 1 conflit majeur** (marque déposée dans classes 9/42/44 en UE ou US, ou app active > 10k users) → **rebrand nécessaire**, retomber sur candidats V1 (`Teral`, `Nerva`) ou rouvrir brainstorm.
- Si **domaine `auren.com` indisponible + coût rachat > seuil acceptable** → décider si `auren.app` ou `auren.health` suffit, ou pivoter.
- Si **verdict favorable** → Auren figé dans `Sx_UI_10` pour rebrand exécution.

**Statut à la fermeture de `Sx_UI_01`** : cette checklist est **pending** et doit être exécutée hors-scope de ce sprint. La spec suivante `Sx_UI_02` peut être ouverte sans attendre ce verdict tant que Auren reste explicitement documenté comme working brand candidate.

## §6. Brand positioning

**Formulation cible officielle :**

> **Auren est une application de performance corporelle qui aide à exécuter, mesurer et piloter l'entraînement avec une interface calme, précise et mobile-first.**

**À éviter systématiquement dans toute copy produit, marketing, ou spec ultérieure :**

- ❌ « AI coach » / « AI trainer »
- ❌ « biohacking révolutionnaire »
- ❌ « crush your goals » / « push your limits »
- ❌ « body transformation magic » / « transform your body »
- ❌ « gym bro tracker »
- ❌ Claims médicaux (« diagnostic », « traitement », « santé garantie »)
- ❌ Superlatifs marketing (« la meilleure », « la plus avancée »)
- ❌ Injonctions énergisantes (« GO ! », « Let's smash it! »)
- ❌ Références culturelles gym (bro-science, hardcore culture, drop sets war)

**Positionnement narratif :**

Auren observe, mesure, explique et suggère. Auren ne motive pas — Auren informe. Auren n'infantilise pas — Auren respecte l'utilisateur comme un opérateur compétent. Auren n'exige pas — Auren propose.

## §7. Product promise

Trois formulations courtes proposées, à valider en `Sx_UI_02` ou lors du merge de la spec :

1. **« Train with signal. »** — anglais, sobre, instrumental, évoque la précision de la mesure. Traduction FR possible : « Entraîne-toi avec du signal. » (moins fluide, à retravailler).
2. **« Measure the work. Guide the next. »** — anglais, structure binaire, résume l'engine Sx_30 (overload) et Sx_31 (body intelligence). Traduction FR possible : « Mesurer l'effort. Guider la suite. »
3. **« Quiet control for physical progress. »** — anglais, très proche de l'univers Oura (« Subtle. Power. »). Traduction FR possible : « Un contrôle calme pour votre progression. » (« votre » ambigu tu/vous — décision `Sx_UI_02` tone editorial).

**Note bilingue :** ces formulations sont proposées en anglais par cohérence avec les benchmarks (Strong, Levels, Oura, WHOOP), mais **la UI applicative française reste possible et probable**. Une version FR de chaque formulation devra être produite et validée lors du choix final (probablement `Sx_UI_02` ou `Sx_UI_04`).

## §8. Tone of voice

**Règles applicables à toute copy produit, spec, template, error message, et documentation utilisateur.**

**Règles de forme :**

- Phrases **courtes** (idéalement < 12 mots).
- **Verbes sobres** : mesurer, observer, guider, suggérer, noter, ajuster. Éviter : booster, exploser, écraser, transformer, révolutionner.
- **Feedback factuel** : « Charge suggérée : 42 kg, +2 % vs séance précédente. » et non « Prêt à cartonner sur cette série ? »
- **Recommandations expliquées** : jamais de nombre sans justification. « Suggéré : 42 kg — dernière fois 40 kg, cible +2 % conservateur. »
- **Pas d'injonction directe** : préférer « À logger maintenant » à « Loggue ta série ! »
- **Pas de culpabilisation** : « Séance manquée depuis 6 jours » et non « Tu as arrêté depuis 6 jours ».
- **Pas d'hyperbole** : éviter les superlatifs et les métaphores dramatiques.
- **Pas de jargon IA** : éviter « algorithme intelligent », « AI-powered », « machine learning ». Préférer « moteur de recommandation », « historique de charge », « calcul automatique ».

**Exemples Do / Don't :**

| Contexte | ❌ Ne pas écrire | ✅ Écrire |
|---|---|---|
| Suggestion charge | « L'IA te recommande 42 kg — go ! » | « Suggéré : 42 kg (+2 % vs dernière fois) » |
| Séance terminée | « GG, tu as tout défoncé ! » | « Séance loggée. 3 exercices, 9 séries, 42 min. » |
| Overload hint | « Push it! Try +5 kg » | « ≈ 42 kg — cohérent avec l'historique récent » |
| Absence longue | « Tu nous manques ! Reviens ! » | « Dernière séance il y a 6 jours » |
| Body intelligence | « Ton corps a changé ! Découvre l'analyse ! » | « Lecture corporelle basée sur les séances loggées » |
| Empty state | « Aucune donnée. Commence à t'entraîner ! » | « Pas encore de données. À logger : première séance. » |
| Erreur système | « Oups ! Quelque chose s'est mal passé 😅 » | « Erreur. Réessayer. » |

**Note sur le tutoiement :** SPIGNOS utilise déjà le tutoiement informel (« tu ») dans les templates existants (`coach_report.html`, `body_intelligence.html`). Auren peut conserver ce choix, mais avec **désengagement** : le « tu » d'un instrument, pas d'un coach.

## §9. Visual principles allowed

Principes autorisés qui doivent être respectés par toute spec visuelle ultérieure (`Sx_UI_02` à `Sx_UI_09`) :

1. **White clinical surfaces** — fond blanc pur ou blanc cassé (`#FFFFFF` à `#F8F9FA`). Surfaces secondaires en gris très clair et froid.
2. **Cold neutral palette** — texte quasi-noir sur blanc, gris froids (bleu-gris), pas de gris chauds (beige, taupe).
3. **One accent only** — un seul accent coloré dans toute l'application. Réservé aux états actifs, scores favorables, CTA primaires. Amendement `Sx_UI_02bis` requis pour tout ajout d'accent secondaire.
4. **Typography-led hierarchy** — la hiérarchie visuelle est portée par la taille et le poids typographique, pas par la couleur, la boîte, ou l'ombre.
5. **Metric clarity** — les métriques (charges, reps, temps, %) sont rendues en **mono** ou en tabular figures, pour alignement vertical parfait dans les listes de séries.
6. **Thin separators** — séparateurs `1px` gris clair, jamais de bordures épaisses ou colorées comme structure.
7. **Minimal shadow** — ombres portées quasi absentes. Une ombre légère au maximum (`0 1px 2px rgba(0,0,0,0.05)`) pour signaler la surface flottante (rest timer, sticky CTA).
8. **No decorative illustration** — pas de personnages, pas d'illustrations conceptuelles, pas de mascotte. Les seuls éléments visuels non-typographiques sont les icônes fonctionnelles (trait simple, 24×24).
9. **Non-color cues for states** — chaque état signalé par la couleur doit aussi porter un indicateur non-coloré (icône, texte, forme, épaisseur de bordure). Conformité WCAG 1.4.1.
10. **Generous spacing** — beaucoup d'air. Densité informationnelle basse plutôt que haute. Une carte, un bloc, une décision par écran.

## §10. Visual anti-patterns forbidden

Anti-patterns interdits dans toute spec visuelle ultérieure :

1. **Gradients « AI »** — les dégradés violets/bleus/roses associés aux products IA (ChatGPT-style, Midjourney-style).
2. **Glassmorphism excessif** — les surfaces translucides avec blur (« frosted glass ») sont bannies. Sauf usage ponctuel documenté (ex : sticky header sur scroll long) et validé en `Sx_UI_02`.
3. **Hero 3D body** — pas de rendu 3D anatomique, pas de « body scan » visuel, pas de silhouette illustrée en hero.
4. **Dark cockpit par défaut** — le thème sombre n'est pas la valeur par défaut. Peut exister comme option utilisateur secondaire, jamais comme identité visuelle primaire.
5. **Orange warning-as-brand** — l'orange chaud actuel (`#f25f3a`) est éliminé du branding et retenu uniquement pour warnings/erreurs si nécessaire.
6. **Dashboard gamer** — pas d'écrans saturés de widgets, de gauges circulaires, de scores multicolores, de leaderboards visibles au premier niveau.
7. **Trop de badges** — un composant n'affiche pas plus de 2 badges. Un écran n'affiche pas plus de 5 badges simultanés. Si plus nécessaire, hiérarchie à retravailler.
8. **Trop de destinations top-level** — bottom nav ≤ 4 entrées (à confirmer en `Sx_UI_03`, OQ-C). Actuellement 10.
9. **Typographie bruyante** — pas de font-weight > 700 pour du corps de texte, pas de font-style italique décoratif, pas de web fonts multiples (max 1 famille avec ≤ 3 poids).
10. **Illustrations fitness cliché** — pas de haltères stylisés, pas de flexes, pas de body-building poses, pas de pictos de sport en gras coloré.
11. **Slogans agressifs** — cf. §6 liste noire.

## §11. Brand references and what to copy

Pour chaque référence, le point spécifique à copier est explicité — pas la référence dans sa globalité.

| Référence | À copier | Pourquoi |
|---|---|---|
| **Strong** | Friction minimale de logging | La sensation « think less, lift more » doit se retrouver dans le mode séance Auren. Si un utilisateur met > 3 secondes à logger une série, on a échoué. |
| **Hevy** | Clarté log / progression / structure de routines | La grammaire fonctionnelle du workout tracking (routines, exercices, séries, poids × reps) est bien résolue chez Hevy. Auren doit conserver cette lisibilité fonctionnelle. |
| **Levels** | Calme clinique + narration pédagogique | La grammaire visuelle blanche, aérée, explicative, sans dashboard gamer. Le ton éditorial (« private, secure, personalized ») transposé au strength tracking. |
| **Oura** | Premium discret, calcul invisible | La désirabilité health-tech qui n'a pas besoin de crier pour paraître avancée. « Subtle. Power. » comme mantra structurel. |
| **WHOOP** | Hiérarchie de signaux, zero distractions | La discipline UX : peu de signaux, mais chaque signal a un poids. Le framing « what should I do today? » — traduit chez Auren en Today/Home orienté readiness (`Sx_UI_05`). |
| **Apple Health** | Confiance et centralisation, tendance plutôt que bruit | La sensation d'un lieu central de vérité corporelle, lisible, sécurisé. Utile comme référence de composition d'écrans Progression et Physique. |
| **Material Design (M3)** | Discipline de rôles de couleur et typographie | Les composants Material posent une grammaire de tokens et de rôles qui peut inspirer `Sx_UI_02` sans copier le look. |
| **Apple HIG** | Discipline de navigation (tab bar navigation, pas action) | Rappel que la navigation n'est pas la surface d'action. Inspiration directe pour `Sx_UI_03`. |

## §12. Brand references and what not to copy

Risques identifiés lors de l'usage de ces mêmes références :

| Risque | Pourquoi c'est un piège |
|---|---|
| **Copier la stack React/Tailwind d'Untitled UI / shadcn/ui** | Ces kits sont excellents pour l'inspiration mais pensés pour Figma web + React. Le repo Auren est SSR + Jinja + CSS + no-JS fallback. Utiliser leur code source augmenterait le drift architectural. Les prendre comme galerie visuelle, pas comme solution d'implémentation. |
| **Surpromesse AI (comme Fitbod)** | Le moteur Auren (Sx_30 overload, Sx_31 body intelligence) est déterministe, explicable, conservateur. Le vendre comme « AI trainer » serait un mensonge de posture. |
| **Trop wellness (comme Oura pur)** | Le glissement vers le lifestyle / self-care contredit le positionnement « strength-first performance corporelle ». |
| **Trop médical (comme Levels sur métabolique)** | Les claims médicaux sont interdits (cf. §6). Auren mesure et suggère ; Auren ne diagnostique pas. |
| **Trop social (comme Hevy)** | La dimension communautaire de Hevy (partage de séances, feed d'amis) n'est pas le différenciateur d'Auren. Squads reste optionnel et secondaire dans la nav. |
| **Trop dashboard (comme WHOOP mobile app pleine de widgets)** | La hiérarchie WHOOP est bonne, mais le rendu multi-cartes/multi-charts est trop dense pour la cible « une décision principale par écran ». |

## §13. Information hierarchy philosophy

**Principe fondateur :** **une décision principale par écran, une profondeur d'attention par moment.**

**Application par contexte :**

| Contexte | Priorité 1 (visible immédiatement) | Priorité 2 (secondaire, accessible) | Priorité 3 (drill-down, opt-in) |
|---|---|---|---|
| **Pendant la séance** | Action de logging (série actuelle, CTA `Loguer`) | Prochaine série dans la même séance | Historique de l'exercice, alternatives, notes |
| **Après séance** | Interprétation / synthèse (volume total, PR éventuels) | Feedback exercice par exercice | Détails par série, comparaisons long terme |
| **Home / Today** | « Quoi faire maintenant » (prochaine séance suggérée, readiness) | Résumé bref de la dernière séance | Analytics et tendances |
| **Progression** | Signaux utiles (tendance charges, volume 30j) | Détails par exercice | Comparaisons année sur année, cycles |
| **Physique** | Tendance corporelle (poids, mesures principales) | Détails par mesure | Explications de dérivation (`Sx_31 Body Intelligence`) |
| **Coach** | Snapshot Body Intelligence + narrative structuré | Sections détaillées | Annexes et raw data |

**Règle de progressive disclosure :** tout élément « avancé » (comparaison long terme, dérivation d'un calcul, historique complet) est repoussé vers une couche secondaire. Le premier niveau reste toujours minimal et actionnable.

## §14. Relationship to existing product

**SPIGNOS et Auren ne sont pas en opposition. Auren hérite de SPIGNOS.**

| Aspect | SPIGNOS | Auren |
|---|---|---|
| Nom applicatif utilisateur | Actuel, visible | Cible, à activer en `Sx_UI_10` |
| Nom moteur / repo / engine | Legacy interne, conservé | Reste `workout-session-tracking` côté code |
| Identité visuelle | Cockpit dark utility | Clinical instrument, blanc, calme |
| Logique métier | Inchangée | Inchangée (contrat dur : aucun sprint UI ne modifie la logique métier) |
| Templates Jinja | Existants avec strings « SPIGNOS » | À migrer en `Sx_UI_10` uniquement |
| Manifest / theme-color / meta | Existants | À migrer en `Sx_UI_10` uniquement |
| Base de code (`app/`, `tests/`, `scripts/`) | Nom d'origine conservé | Repo reste `MFE-DSS/workout-session-tracking` — pas de renommage repo prévu |
| Config / .env / secrets | Nom d'origine conservé | Pas de renommage |
| Service systemd VPS | `workout` | Pas de renommage (risque prod, hors scope UI) |

**Règle de migration :**

- Aucune suppression brutale de la mention SPIGNOS n'a lieu avant `Sx_UI_10`.
- Aucun mélange lexical n'a lieu (« SPIGNOS / Auren » dans le même écran est interdit sauf écran de transition explicite documenté dans `Sx_UI_10`).
- La migration est **atomique par surface** : chaque template migré en une fois, jamais en patchwork.
- `Sx_UI_10` doit produire un **écran de transition** pour informer les utilisateurs existants du changement de nom, si utilisateurs existants au moment du rebrand.

## §15. Dependency map

**`Sx_UI_01` (ce document) débloque en aval :**

- **`Sx_UI_02_DESIGN_TOKENS_SPEC`** — palettes, typo, tokens CSS. Sera écrit en SPEC ONLY après validation humaine de `Sx_UI_01`.
- **`Sx_UI_03_APP_SHELL_NAVIGATION_SPEC`** — top bar, bottom nav ≤ 4 entrées, safe areas. Dépend de `Sx_UI_02` pour les tokens visuels.
- **`Sx_UI_11_SCREENSHOT_REGRESSION_SPEC`** — baseline outil (Playwright ?) et périmètre viewport. Peut être écrit en parallèle de `Sx_UI_02` / `Sx_UI_03`, mais **doit produire une baseline utilisable avant `Sx_UI_04`**.

**Puis seulement :**

- **`Sx_UI_04_SESSION_FOCUS_RESKIN_SPEC`** — premier sprint UI autorisé à modifier du code (CSS + templates surface uniquement, jamais services). Précondition : `Sx_UI_01`, `Sx_UI_02`, `Sx_UI_03` validés + baseline `Sx_UI_11` disponible.

**Aval de `Sx_UI_04` (rappel roadmap) :**

`Sx_UI_05` (Today/Home) → `Sx_UI_06` (Exercise Intelligence Presentation) → `Sx_UI_07` (History & Progress) → `Sx_UI_08` (Portability) → `Sx_UI_09` (Accessibility, parallèle possible dès `Sx_UI_04`) → `Sx_UI_10` (Rebrand Migration, exécuté au plus tôt après `Sx_UI_04` validé) → `Sx_UI_11` (Screenshot regression continu).

## §16. Open Questions

Questions à trancher hors-scope de `Sx_UI_01`. Aucune n'empêche l'ouverture de la spec, mais chaque OQ doit avoir un propriétaire de décision explicité au moment de l'ouverture de la spec dépendante.

| OQ | Question | Propriétaire de décision | Bloque quoi |
|---|---|---|---|
| **OQ-A** | Auren est-il juridiquement disponible (INPI + EUIPO + USPTO + domaines) ? | opérateur + juridique externe | `Sx_UI_10` execution (pas `Sx_UI_02`/`03`/`04`) |
| **OQ-B** | Accent final = teal chirurgical désaturé ou bleu minéral ? | opérateur, décision `Sx_UI_02` | `Sx_UI_02` merge |
| **OQ-C** | Bottom nav finale = 4 ou 5 destinations ? | opérateur, décision `Sx_UI_03` | `Sx_UI_03` merge |
| **OQ-D** | Physique est-il top-level dans la nav, ou secondaire (accédé depuis Profile) ? | opérateur, décision `Sx_UI_03` | `Sx_UI_03` merge |
| **OQ-E** | Coach est-il top-level, ou contextualisé (accédé depuis Home ou Progression) ? | opérateur, décision `Sx_UI_03` | `Sx_UI_03` merge |
| **OQ-F** | Rebrand complet en `Sx_UI_10`, ou dual-label « Auren by SPIGNOS engine » pendant une période transitoire ? | opérateur, décision `Sx_UI_10` | `Sx_UI_10` execution |
| **OQ-G** | Playwright est-il confirmé pour screenshot regression, ou alternative (Puppeteer, Playwright + Percy, snapshot-py) ? | opérateur + revue tooling, décision `Sx_UI_11` | `Sx_UI_11` merge + baseline avant `Sx_UI_04` |

**Note sur OQ-A :** cette OQ est **la plus critique**. Un verdict défavorable (Auren juridiquement bloqué) invalide toutes les mentions Auren dans les specs Sx_UI et déclenche un `Sx_UI_01bis` de renommage. La checklist §5 doit être exécutée le plus tôt possible.

## §17. Non-goals

**Ce sprint `Sx_UI_01` ne produit et ne modifie explicitement rien de tout cela :**

- Pas de code applicatif.
- Pas de CSS applicatif.
- Pas de tokens CSS définitifs.
- Pas de logo.
- Pas de favicon.
- Pas de mise à jour du manifest.
- Pas de renommage de routes.
- Pas de remplacement de « SPIGNOS » dans les templates.
- Pas de mise à jour PWA.
- Pas de shell nav ou de reduction du chrome.
- Pas d'installation ou configuration de screenshot tooling.
- Pas de re-skin de la page session.
- Pas de refonte UX.
- Pas de modification métier (aucun service, aucun modèle, aucune migration, aucun test métier).
- Pas de modification des flags (`BODY_INTELLIGENCE_ENABLED`, `BODY_ASSESSMENT_ENABLED`, `BODY_CAPTURE_QUALITY_ENABLED`, `RATE_LIMIT_ENABLED`, `SENTRY_ENABLED`, `PERF_REQUEST_TIMING_ENABLED`).
- Pas d'ouverture de `Sx_UI_02` / `Sx_UI_03` / `Sx_UI_04` / autres sprints Sx_UI.
- Pas d'ouverture de sprint de build `Sb_UI_NN.k`.

## §18. Acceptance criteria

La spec est acceptable si **toutes** les conditions suivantes sont respectées :

- ✅ Auren est défini comme working brand candidate (§4), pas comme marque figée.
- ✅ Legal/domain due diligence est explicitement documentée comme pending (§5 checklist), aucun engagement juridique n'est pris.
- ✅ Tone of voice est défini avec règles + exemples Do/Don't (§8).
- ✅ Principes visuels autorisés (§9) et interdits (§10) sont listés et compréhensibles sans ambiguïté.
- ✅ Benchmarks sont cadrés : quoi copier (§11) et quoi éviter (§12).
- ✅ Hiérarchie informationnelle est définie par contexte (§13).
- ✅ Relation SPIGNOS ↔ Auren est explicite (§14) et exclut tout renommage code prématuré.
- ✅ Dépendances `Sx_UI_02` / `Sx_UI_03` / `Sx_UI_11` / `Sx_UI_04` sont documentées (§15).
- ✅ Aucun build n'est ouvert (§17 non-goals).
- ✅ Aucun fichier `app/`, `tests/`, `migrations/`, `scripts/` (autre que `docs/`) n'est modifié dans ce sprint.
- ✅ Les OQ (§16) sont explicites avec propriétaire de décision.

## §19. Build authorization status

**BUILD NOT AUTHORIZED.**

**Next authorized action after human validation of this spec :** `Sx_UI_02_DESIGN_TOKENS_SPEC` **SPEC ONLY**.

- Aucun sprint `Sb_UI_NN.k` d'implémentation ne peut être ouvert.
- Aucun fichier `app/`, `tests/`, `migrations/`, `.github/workflows/`, config runtime, `.env`, manifest, static assets ne peut être touché.
- Aucun renommage `SPIGNOS` → `Auren` ne peut être effectué dans le code.
- `Sx_UI_10` (rebrand execution) reste bloqué jusqu'à `Sx_UI_04` minimum validé, ET verdict favorable sur due diligence §5.

## §20. Final verdict

**READY FOR HUMAN REVIEW.**

---

## Références

- **Brainstorm sources (archive) :**
  - `docs/strategy/brainstorm/UI_TRANSFORMATION_BRAINSTORM_V1_normalized.md` — cadre transformation mobile minimaliste, family de noms Teral/Nerva/Auren
  - `docs/strategy/brainstorm/UI_TRANSFORMATION_BRAINSTORM_V2_normalized.md` — biomécanique minimaliste, family de noms MYON/VYON/RATEL
  - `docs/strategy/brainstorm/INDEX.md` — traçabilité archivage + décodage mojibake
- **Synthèse actionnable :** `docs/strategy/UI_TRANSFORMATION_ROADMAP.md`
- **Registry :** `docs/strategy/SPEC_REGISTRY.md` §1quinquies
- **Roadmap globale :** `docs/strategy/ROADMAP_AND_NEXT_STEPS.md` §1
- **Gate OPS déblocant :** `docs/OPS_PROD_STABILIZATION_PROFILE_BODY_COACH_REPORT.md` §10 (verdict signé 2026-07-02)
- **Focus mode précurseur :** `docs/strategy/Sx_29_CLOSURE_REPORT.md` + `docs/dogfood/DOGFOOD_Sx_29_FOCUS_MODE_TEMPLATE.md`
