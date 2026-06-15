# SPIGNOS — Roadmap & Next Steps (Reference Document)

**Auteur :** opérateur SPIGNOS + Claude Code (Opus 4.7).
**Créé :** 2026-06-15 (post-clôture technique Sx_27).
**Statut :** **document de référence vivant** — à relire à chaque reprise de session pour savoir quoi prompter ensuite.
**Source de vérité officielle :** `docs/strategy/SPEC_REGISTRY.md` (la table des sprints livrés). Ce document est la **lecture éditoriale** par-dessus.

---

## 1. Position actuelle (verrouillée)

| Item | Valeur |
|---|---|
| Sx_26 — Engineering Control Plane | ✅ clôturé 2026-06-14 (cf. `Sx_26_CLOSURE_REPORT.md`) |
| Sx_27 — Coaching Loop & Product Activation | ✅ **technically closed** 2026-06-15 (cf. `Sx_27_CLOSURE_REPORT.md`) |
| Sx_28 — Product Roadmap Reconciliation | ✅ **SPEC AMENDED** sous override humain 2026-06-15 (cf. `Sx_28_PRODUCT_ROADMAP_RECONCILIATION_SPEC.md`) |
| Sx_29 — Mobile Session Focus Mode & Visual Interaction Layer | ✅ **SPEC ONLY** ouverte 2026-06-15 sous override #2 (cf. `Sx_29_MOBILE_SESSION_FOCUS_MODE_SPEC.md`) |
| Product validation Sx_27 | ⏳ **pending real dogfood** (cf. `docs/dogfood/DOGFOOD_Sx_27_DEFERRED.md`) — non simulé, peut reverser Option A si livré plus tard |
| Build authorization | ✅ **AUTHORIZED FOR OPTION A** (Sx_29 Mobile Session Focus Mode) sous override explicite 2026-06-15. Options B/C/D/E **restent bloquées** (override séparé requis) |
| Dernier CI run vert | [#27554090915](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/27554090915) |
| Tests | **1080 passed** |
| Ruff budget | **534 ≤ 548** |
| Architecture | FastAPI SSR + Jinja2 + SQLite (inchangée) — **React production INTERDIT dans Sx_29** |

> ⚠️ **Note double override 2026-06-15** :
> 1. Override #1 (matin) : ouverture Sx_28 en SPEC ONLY sans dogfood reçu.
> 2. Override #2 (sprint `Sb_28.override-build-authorization`, après-midi) : bascule `BUILD AUTHORIZED FOR OPTION A` sans attendre le dogfood.
>
> **Le dogfood Sx_27 reste PENDING** : il n'est ni simulé, ni considéré acquis. Son arrivée future peut **reverser** Option A si elle révèle qu'une autre friction est prioritaire (cf. Sx_28 §15.2).
>
> **Limites strictes de l'override #2** (verbatim Sx_28 §20) :
> - Option A uniquement (Sx_29 Mobile Session Focus Mode)
> - Options B/C/D/E restent bloquées (override séparé requis)
> - FastAPI SSR + Jinja2 conservé ; React production INTERDIT dans Sx_29
> - Lab React exploratoire acceptable séparément, jamais dans le build principal Sx_29
> - Hard contracts Sx_26/Sx_27 inchangés
> - Sx_29 doit produire sa spec d'abord (SPEC ONLY), comme tout cycle Sx_

## 2. Protocole spec-driven — règle d'or

> **On ne développe plus de nouveau cycle produit tant que la boucle livrée n'a pas été vécue en conditions réelles.**

`docs/strategy/SPEC_DRIVEN_ENGINEERING_PROTOCOL_v1.md §9` (dogfooding) : *"Pas de dogfood report ⇒ pas de cycle suivant."*

Conséquences directes :
- **Ne PAS ouvrir Sx_28** avant `Sb_27.dogfood-1`.
- **Ne PAS ouvrir un nouveau Sx_** sur la base d'hypothèses produit non vérifiées.
- L'ancienne roadmap historique S0→S10 (cf. `SPIGNOS_EXERCISE_SYSTEM_ROADMAP.md`, daté 2026-04-14) **n'est plus la source de vérité** — elle a été partiellement absorbée par les cycles Sx_24 / Sx_26 / Sx_27 (cf. §4).

## 3. Roadmap réelle (post-réconciliation + post-override #2 2026-06-15)

```
   ┌──────────────────────────┐
   │  Sb_27.dogfood-1         │  ⏳ PENDING — peut arriver et reverser
   │  Real Product Dogfood    │     Option A si friction différente révélée
   └──────────────┬───────────┘
                  │ (parallèle, non bloquant après override #2)
                  ▼
   ┌──────────────────────────┐
   │  Sx_28 SPEC AMENDED ✅   │  Override #1: spec only sans dogfood
   │  + Sb_28.override-       │  Override #2: BUILD AUTHORIZED Option A
   │    build-authorization   │  Options B/C/D/E restent BLOQUÉES
   └──────────────┬───────────┘
                  │
                  ▼
   ┌──────────────────────────┐
   │  Sx_29 — Mobile Session  │  ✅ AUTORISÉ par override #2
   │  Focus Mode / Visual     │  📋 SPEC ONLY d'abord (protocole §4)
   │  Interaction Layer       │  🔒 FastAPI SSR + Jinja2 ; React INTERDIT
   └──────────────┬───────────┘
                  │
                  ▼
       ┌──────────────────────────────┐
       │ 🔴 Sx_30 (Overload)          │  Override séparé requis
       │ 🔴 Sx_31 (Body v2)           │  Override séparé requis
       │ 🔴 Sx_32 (PWA)               │  Override séparé requis
       │ 🔴 Sx_33+ (Health/API)       │  Override séparé requis
       └──────────────────────────────┘

       ↳ Sb_28.dogfood-integration (optionnel) :
         si dogfood arrive a posteriori, met à jour Sx_28 §15/§20.
         Peut reverser Option A → Option B/C/D selon signal réel.
```

## 4. Mapping ancienne roadmap S0→S10 vs repo réel

| Ancienne phase | Statut réel | Sprint(s) absorbant | Reste à faire |
|---|---|---|---|
| S0 Baseline repo + benchmark | partiel / obsolète | Sx_26 (Control Plane) | rien — réconcilier dans Sx_28 |
| S1 Signal exercice | ✅ largement fait | Sx_24 (implicit signal + quality V2), Sb_01 | clarifier dettes subjectives résiduelles |
| S2 Mode séance focus | partiel | session detail existant, mobile partials | **Sx_29 candidat fort** (focus mode + friction) |
| S3 Catalogue + taxonomie | partiel | catalog QA + machine atlas + substitution graph | normalisation taxonomie musculaire si dogfood le demande |
| S4 Substitution | ✅ V1 fait | Sx_22 substitution graph + `substituted_name` | option canonique différée |
| S5 Recommandation surcharge | partiel | Sx_27 (reco + explainer + narrative) | surcharge progressive stricte → **Sx_30 candidat** |
| S6 Body tracking | partiel | body metrics + readiness (Sb_22+) | photos / progression photos → **Sx_31 candidat** |
| S7 Body Engineering dashboard | réorienté | `/dashboard` déprécié Sb_27.6, valeur déplacée vers `/`, `/progress`, `/physique` | rien |
| S8 PWA premium | partiel | manifest + meta présents | service worker / offline / Lighthouse → **Sx_32 candidat** |
| S9 Health integrations prep | ❌ pas fait | — | reporté post-stabilisation → **Sx_33 candidat** |
| S10 API mobile prep | ❌ pas fait | — | reporté post-dogfood → **Sx_33+ candidat** |

**Conclusion** : la moitié de S0→S10 est déjà absorbée par les cycles Sx_24/26/27. Le reste devient des cycles Sx_29-33 **conditionnés par le dogfood Sx_27** et tranchés dans **Sx_28**.

## 5. Étape 1 — `Sb_27.dogfood-1` (PROCHAINE ACTION)

### 5.1 Objectif
Vérifier en usage réel si la boucle Sx_27 répond bien aux 5 questions :
1. Quoi faire aujourd'hui ?
2. Pourquoi cette séance ?
3. Que signifie ma dernière séance ?
4. Comment ajuster la suite ?
5. Est-ce que je progresse ou je dérive ?

### 5.2 Pré-requis
- Aucun (Sx_27 livré, runbook documenté dans `DOGFOOD_Sx_27_DEFERRED.md`)

### 5.3 Prompt à utiliser (copier verbatim)

```
GO Sb_27.dogfood-1 — Real Product Dogfood Report.

Repo :
MFE-DSS/workout-session-tracking

Contexte :
Sx_27 est technically closed mais product validation pending real dogfood.
Ne pas ouvrir Sx_28 avant ce dogfood.

Objectif :
Préparer et produire le cadre de dogfood réel pour valider la boucle de
coaching livrée par Sx_27.

Important :
Si aucun usage réel n'a encore été exécuté, ne pas inventer de résultats.
Créer seulement le protocole opérationnel et le template de saisie terrain.
Si l'opérateur fournit ensuite ses retours réels, produire le report final.

Livrables :
1. Vérifier docs/dogfood/DOGFOOD_Sx_27_DEFERRED.md.
2. Créer docs/dogfood/DOGFOOD_Sx_27_RUNBOOK.md si absent.
3. Créer docs/dogfood/DOGFOOD_Sx_27_FIELD_NOTES_TEMPLATE.md.
4. Ne modifier aucun code applicatif.
5. Ne modifier aucun test applicatif.
6. Ne pas créer de migration.
7. Ne pas ouvrir Sx_28.

Le runbook doit contenir :
- durée : 10-14 jours ;
- cible : 5-7 séances ;
- viewport : mobile 360×640 ;
- surfaces : /, /launcher, /sessions/{id}/done, /progress ;
- questions à noter avant / pendant / après séance ;
- critères de succès ;
- critères d'échec ;
- décision finale possible :
  A. Sx_28 peut être ouvert ;
  B. Sb_27.next.<fix> requis ;
  C. Product validation still deferred.

DoD :
- documentation only ;
- check_spec_protocol passe ;
- pytest reste vert ;
- CI verte ;
- verdict final explicite :
  DOGFOOD READY TO EXECUTE
  ou
  DOGFOOD REPORT PRODUCED si données réelles fournies.
```

## 6. Étape 2 — `Sx_28` (après dogfood)

### 6.1 Objectif
Réconcilier l'ancienne roadmap S0→S10, l'état réel du repo, les cycles déjà livrés, les résultats de dogfood Sx_27, et les dettes restantes. Trancher le prochain axe unique.

### 6.2 Pré-requis bloquants
- `Sb_27.dogfood-1` livré (runbook + report ou DEFERRED explicite)
- Si dogfood fait : retours réels documentés
- Si pas de dogfood dans 14-30 jours : décision explicite "indefinitely deferred"

### 6.3 Prompt à utiliser (copier verbatim)

```
GO Sx_28 — Product Roadmap Reconciliation & Next Cycle Selection.

Repo :
MFE-DSS/workout-session-tracking

Contexte :
Sx_26 est clôturé.
Sx_27 est technically closed.
Dogfood Sx_27 doit être pris en compte s'il existe.
La roadmap historique S0→S10 existe comme document conceptuel, mais elle
n'est pas la source de vérité actuelle.
La source de vérité actuelle est docs/strategy/SPEC_REGISTRY.md.

Objectif :
Produire une spec de réconciliation entre :
1. l'ancienne roadmap vNext S0→S10,
2. l'état réel du repo,
3. les cycles déjà livrés,
4. les résultats de dogfood Sx_27,
5. les dettes techniques et produit restantes.

Contraintes :
- SPEC ONLY.
- Ne modifie aucun code.
- Ne modifie aucun test.
- Ne crée aucune migration.
- Ne crée aucun modèle.
- Ne démarre aucun build.
- Distingue ce qui est déjà fait, partiellement fait, obsolète, ou encore pertinent.
- Ne pas réouvrir des décisions déjà tranchées sauf preuve dogfood.

Fichiers à inspecter :
- docs/strategy/SPEC_REGISTRY.md
- docs/strategy/Sx_26_CLOSURE_REPORT.md
- docs/strategy/Sx_27_CLOSURE_REPORT.md
- docs/strategy/ROADMAP_AND_NEXT_STEPS.md
- docs/dogfood/*
- docs/SPRINT_SYNTHESIS.md
- docs/strategy/SPIGNOS_EXERCISE_SYSTEM_CONSOLIDATION_SPEC.md
- docs/strategy/SPIGNOS_EXERCISE_SYSTEM_ROADMAP.md
- app/routers
- app/services
- app/templates
- tests

Livrable :
Créer docs/strategy/Sx_28_PRODUCT_ROADMAP_RECONCILIATION_SPEC.md

Structure obligatoire :
1. Executive summary.
2. Source de vérité actuelle.
3. Ancienne roadmap S0→S10.
4. Mapping ancienne roadmap vs repo réel.
5. Ce qui est déjà fait.
6. Ce qui est partiellement fait.
7. Ce qui est obsolète.
8. Ce qui reste produit-relevant.
9. Résultats dogfood Sx_27 si disponibles.
10. Options de prochain cycle :
    - Option A : Focus Mode / Logging Experience
    - Option B : Progressive Overload Engine
    - Option C : Body Tracking v2
    - Option D : PWA Premium
    - Option E : Cleanup only
11. Matrice impact / risque / valeur.
12. Recommandation.
13. Build queue proposée.
14. Non-goals.
15. Open questions.
16. Verdict :
    READY FOR HUMAN DECISION
    ou
    WAIT FOR DOGFOOD.

Ne code rien.
```

## 7. Étape 3 — `Sx_29` (recommandation par défaut post-Sx_28)

### 7.1 Pourquoi `Sx_29` Focus Mode et pas autre chose ?
Verbatim Product Owner / Prompt Engineer (rapport de planning) :

> Si le logging en salle n'est pas excellent, toute la couche recommandation/body analytics reposera sur un usage fragile.
> D'abord rendre le mode séance imbattable, ensuite enrichir le signal, ensuite seulement corps/graphes/imports santé.

Donc l'ordre logique post-dogfood (si pas de blocker majeur découvert) :
1. **Sx_29** Mobile Session Focus Mode — qualité du logging en salle
2. Sx_30 Progressive Overload Engine — meilleure reco après meilleur signal
3. Sx_31 Body Tracking v2 — photos / progression / source confidence
4. Sx_32 PWA Premium — service worker / offline / Lighthouse
5. Sx_33+ Health / API mobile — exports / intégrations

### 7.2 Pré-requis bloquants pour ouvrir Sx_29
- `Sb_27.dogfood-1` livré (✅ ou ❌ tranché)
- `Sx_28` validé par revue humaine
- Recommandation Sx_28 = Option A (Focus Mode) **ou** humain override explicite

### 7.3 Prompt à utiliser (copier verbatim)

```
GO Sx_29 — Mobile Session Focus Mode & Logging Friction Reduction.

Repo :
MFE-DSS/workout-session-tracking

Contexte :
Sx_27 a livré la boucle coaching.
Sx_28 a réconcilié la roadmap.
Le prochain axe retenu est l'expérience de logging en séance.

Objectif :
Spécifier une refonte mobile-first du mode séance pour réduire la
friction en salle :
- une carte exercice active,
- navigation rapide E1/E2/E3,
- dernier historique visible,
- delta visible,
- gros tap targets,
- CTA sticky,
- timer repos simple,
- fallback no-JS acceptable.

Contraintes :
- FastAPI SSR + Jinja2 conservé.
- Pas de SPA.
- JS progressif autorisé uniquement pour focus/timer/collapse local.
- Aucune rupture de route existante.
- Aucun changement historique destructif.
- Ne pas toucher au scoring core sauf nécessité explicitement justifiée.
- Mobile 360×640.
- Pas de scroll horizontal.
- No-JS fallback fonctionnel.

Livrable :
docs/strategy/Sx_29_MOBILE_SESSION_FOCUS_MODE_SPEC.md

Structure :
1. Audit de la page session actuelle.
2. Problèmes observés ou issus dogfood.
3. User flow cible en salle.
4. États UI : active, pending, done, skipped, substituted.
5. Header compact.
6. Jump bar.
7. Exercise card active.
8. Set rows.
9. Timer repos.
10. CTA sticky.
11. No-JS fallback.
12. Accessibilité.
13. Fichiers impactés.
14. Tests attendus.
15. Build queue :
    - Sb_29.1 template skeleton
    - Sb_29.2 active exercise navigation
    - Sb_29.3 sticky CTA
    - Sb_29.4 rest timer progressive enhancement
    - Sb_29.5 tests + dogfood report
16. Non-goals.
17. Verdict.
```

## 8. Ce qu'on NE fait PAS maintenant

Verbatim Product Owner :

> Je ne lancerais pas tout de suite :
> - S5 Progressive Overload Engine
> - S6 Photos/body tracking v2
> - S8 PWA premium
> - S9 Health integrations
> - S10 API mobile

Justification : le produit vient de recevoir une couche coaching complète. Il faut d'abord savoir si elle marche en vrai, puis améliorer la friction principale (le logging), puis seulement enrichir.

## 9. Erreurs à éviter à la reprise

| Tentation | Pourquoi NE PAS le faire |
|---|---|
| « GO Sx_28 directement » | Spec-driven §9 : pas de dogfood ⇒ pas de cycle suivant. Sx_28 doit consommer le dogfood report comme input. |
| « GO Sx_29 directement, on connaît déjà la friction » | Mêmes raisons. Et Sx_28 peut révéler qu'un autre cycle est prioritaire. |
| « Réouvrir l'ancienne S0→S10 telle quelle » | Obsolète : 5/11 phases déjà absorbées, le reste doit être réconcilié par Sx_28. |
| « Skip Sb_27.dogfood-1 si dogfood déjà fait » | Le dogfood doit avoir produit un report formel (`DOGFOOD_Sx_27_REPORT_<date>.md`). Sans le report, pas de signal exploitable par Sx_28. |
| « Coder direct sans spec » | Protocole §4 : `Sx_NN` ne livre jamais de code. Le code arrive dans `Sb_NN.k`. |
| « Modifier `recommendation.py` / scoring core » | Verrouillé par les hard contracts Sx_26 + Sx_27. Wrapper externe obligatoire (pattern `recommendation_explainer.py` Sb_27.4). |

## 10. Plan d'action immédiat (TL;DR) — révisé post-override #2 2026-06-15

**État au 2026-06-15 (après-midi) :**
- Sx_28 SPEC AMENDED (override #2 → Option A AUTORISÉE)
- Dogfood Sx_27 toujours PENDING (non simulé, peut reverser Option A si livré)
- Build Sx_29 (Mobile Focus Mode) **AUTORISÉ**
- Options B/C/D/E restent bloquées

**Séquence révisée :**

1. ~~**Prochaine action immédiate** : copier le prompt §7.3 → ouvrir Sx_29 SPEC ONLY~~ **✅ FAIT 2026-06-15** : `Sx_29_MOBILE_SESSION_FOCUS_MODE_SPEC.md` livrée
2. **Prochaine action maintenant** : relire la spec Sx_29, trancher OQ-A à OQ-E (§19), valider conditions §18, puis ouvrir `Sb_29.1` (visual skeleton)
3. **Stack contrainte** : FastAPI SSR + Jinja2 conservé ; **React production INTERDIT** dans Sx_29 ; lab React exploratoire acceptable séparément
4. **En parallèle (opérateur)** : viser le dogfood Sx_27. Si livré, ouvrir `Sb_28.dogfood-integration` pour vérifier qu'Option A reste pertinente. Sinon, `Sb_27.next.<fix>` à intercaler avant la suite de Sx_29.
5. **Options B/C/D/E** : restent bloquées tant qu'aucun override séparé n'est documenté
6. **Itérer** post-Sx_29 vers Sx_30 (Overload), Sx_31 (Body v2), Sx_32 (PWA), Sx_33+ (Health/API) — **chacun nécessite son propre override ou un dogfood arrivé**

**Anti-patterns à éviter (post-override #2) :**
- Ouvrir Sx_29 directement en BUILD `Sb_29.k` sans produire la spec d'abord — **interdit**, Sx_29 doit suivre le protocole spec-driven (§4 protocole)
- Étendre l'override à Options B/C/D/E sans documentation séparée — **interdit**, override #2 borné à Option A
- Introduire du React production dans Sx_29 — **interdit**
- Réouvrir OQ Sx_27 tranchées sans preuve dogfood — **interdit**
- Considérer Sx_27 comme product-validé — **interdit**, dogfood reste PENDING

**Ce document est la première chose à relire quand tu reprends une session.** Il évite de redécouvrir la position et de poser des questions déjà tranchées.

## 11. Maintenance du document

| Quand | Action |
|---|---|
| À la clôture d'un nouveau Sx_ | Mettre à jour §1 (Position actuelle) + §3 (Roadmap réelle) + §4 (Mapping si pertinent) |
| À la livraison d'un dogfood | Mettre à jour §5.3 (`Sb_27.dogfood-1` → ✅), avancer §6 en "PROCHAINE ACTION" |
| Si OQ tranchée modifie la queue | Mettre à jour §3 + §7-8 |
| Si un cycle est annulé | Documenter la raison dans §4 et §11 |

Ce document **n'est pas figé** — il évolue. Mais il est la source unique de "quoi prompter ensuite", et toute évolution doit être traçable dans un commit.

---

**Co-Authored-By :** Claude Opus 4.7
