# Sprint Sx_11a Report — Pre-Session Briefing Spec

**Date :** 2026-04-21
**Type :** SPEC ONLY — aucun code, aucune migration, aucun test
**Prérequis :** Session System V1 validé, 0 FAIL critique/haute résiduel, branche saine
**Livraison :** 2 documents (spec principale + ce rapport)
**Successeur :** Sb_11a_pre_session_briefing_build

---

## 1. Ce que j'ai inspecté pour écrire la spec

Surfaces relues pour cadrer le périmètre du briefing sans réécrire ce qui existe :

- [app/templates/session_detail.html](app/templates/session_detail.html) — structure `<details>` des cartes, `<summary>` compact actuel, bloc feedback exercice, footer CTA, placement du machine-panel et du peek éventuel.
- [app/routers/sessions.py](app/routers/sessions.py) `session_detail` — contexte template actuel : `jump_states`, `next_code_by_exercise`, `prev_code_by_exercise`, `atlas_data`, `hints`, `sb08_hints_by_exercise`.
- [app/services/stats.py](app/services/stats.py) — `last_time_by_exercise_code` et `_summarise_prior` (dispose déjà de `first_set`).
- [app/services/machine_atlas.py](app/services/machine_atlas.py) — `get_for_template_exercise` retourne `{machine, family}`, expose `execution_cues`.
- [app/services/quality_score.py](app/services/quality_score.py) — `session_kind(session)` alias public.
- [app/models/catalog.py](app/models/catalog.py) — `RepTarget` avec `min_reps/max_reps/technique`.
- [data/reference_split.json](data/reference_split.json) — templates cardio (`liss-only`, `liss-abs`) et leurs notes de cadre.

## 2. Décisions clés retenues dans la spec

1. **Deux surfaces, pas plus** — chip sur `<summary>` des cartes future + peek en bas de la carte active. Les variantes à base de `<details>` imbriqués (E3) et de toggle global (E4) ont été évaluées puis rejetées pour V1.
2. **Pas de nouveau modèle** — tout le contenu est calculable depuis `RepTarget` + `last_time` + `machine_atlas`. Zéro DB, zéro migration.
3. **Non-duplication explicite (§G3)** — le briefing ne réexpose ni delta, ni erreurs fréquentes, ni muscle_sensation. Ces éléments restent sur la carte active où ils sont pertinents à l'exécution.
4. **Format strength et cardio séparés** — chip `3×8-12 · dernière fois 60 kg × 10` pour strength ; `LISS 25min zone 115-135` pour cardio, avec last-time cardio en minutes+BPM.
5. **Cap strict des cues dans le peek** — 2 max, règle éditoriale « une phrase ≤ 60 chars ».
6. **Zéro JS** — tout en Jinja + CSS. Pas d'expand/collapse interactif du briefing lui-même.

## 3. Ce qui a été explicitement laissé hors scope

- Toggle utilisateur `?briefing=on/off` — si un retour terrain montre que le peek est intrusif, on l'ajoutera en Sb_11a.1 plus tard.
- Briefing expandable cliquable sur cartes future — la chip statique couvre le besoin.
- Affichage d'erreurs fréquentes dans le briefing — rester sur la carte active via le machine-panel.
- Cardio machines (vélo, rameur, elliptique) dans l'atlas — hors scope V1 de l'atlas, probablement hors scope V2 aussi (peu de valeur d'exécution documentable).
- Rappel `confidence_score` ou `anomalies` précédentes — relèvent de la review, pas du briefing.
- Impact sur `/progress`, `/profile`, `/done` — aucun.

## 4. Ce qui est clairement présent et prêt à être consommé

| Signal | Source | Consommable immédiatement |
|--------|--------|--------------------------|
| `rep_targets` | `se.template_exercise.rep_targets` | oui |
| `last_time.first_set` | `last_time_by_exercise_code(db, session, now)` | oui, déjà calculé dans le router |
| `execution_cues` | `machine_atlas.get_for_template_exercise(se.template_exercise)["machine"]["execution_cues"]` | oui |
| `template.kind` | `session.template.kind` via `session_kind()` | oui |
| `next_code_by_exercise` | déjà calculé par `session_detail` | oui |

Le service `briefing.py` proposé ne fait que **composer** ces briques.

## 5. Ce qui est ambigu et à trancher au moment du build

- **Position exacte du peek dans le formulaire** : après le bloc feedback exercice et avant le footer CTA — à confirmer visuellement en dogfooding 375px. Alternative envisageable : juste après la set-list avant le ressenti.
- **Wording du label** : « Prochain » (retenu spec) vs « À suivre » vs « Ensuite ». Trancher pendant le build via preview.
- **Traitement du dernier exo** : bloc peek omis entièrement (retenu) vs peek remplacé par `Terminer la séance →` (alternative). Retenir la plus silencieuse.

## 6. Risques résiduels identifiés

Tous documentés §J de la spec. Les deux principaux à surveiller en dogfooding :

- **Densification du `<summary>` sur petit viewport** — si chip empiète sur la progression `0/3`, il faudra truncate.
- **Carte active rallongée par le peek** — si sur 375px le footer CTA disparait sous la ligne de flottaison, le placement est à revoir.

## 7. Recommandation build suivant

**Sb_11a — Pre-Session Briefing build**, scope strict §L de la spec.

- Effort : 5-7h.
- Zéro migration, zéro nouveau endpoint, zéro JS.
- 1 service (`briefing.py` ~80 lignes), 2 modifs template, 2 classes CSS, ~12 tests.

**Préalable explicite** avant de lancer Sb_11a :
- Session System V1 **mergé sur main** et déployé.
- Retour de dogfooding positif (cf. `docs/strategy/SPIGNOS_V1_DOGFOODING_CHECKLIST.md`).
- Commit de référence stable sur `main`.

## 8. Recommandation du prochain sprint de spec après Sb_11a

Deux candidats restants (alternatives non-mutuellement exclusives) :

| Candidat | Angle | Effort spec | Priorité (estimation) |
|----------|-------|-------------|----------------------|
| **Sx_11b — Programme-builder utilisateur** | Permettre à l'utilisateur de créer ses propres templates (pas seulement consommer). Nouveau modèle, nouveau flow, nouvelle surface. | 6-8h | Haute si besoin produit fort |
| **Sx_11c — Squad / social v2** | Enrichir `squad.py` existant : défis hebdo, comparaisons non-agressives, confidentialité renforcée. | 4h | Moyenne |

**Recommandation personnelle** : Sx_11b après Sb_11a. Le programme-builder est le prochain saut de valeur utilisateur logique une fois le flow séance maîtrisé. Squad v2 peut attendre.

À arbitrer par l'utilisateur.

## 9. Livrables produits par ce sprint

| Fichier | Action |
|---------|--------|
| `docs/strategy/SPIGNOS_PRE_SESSION_BRIEFING_SPEC_v1.md` | New |
| `docs/SPRINT_Sx_11a_pre_session_briefing_spec_REPORT.md` | New (ce rapport) |

Aucun code. Aucune migration. Aucun test.

## 10. Synthèse exécutive

- Briefing défini comme **deux surfaces minimales** (chip permanente sur cartes future + peek dynamique en bas de carte active), pas plus.
- **Zéro nouveau modèle, zéro migration, zéro JS**. Toutes les briques de données déjà livrées par Sb_07, Sb_08, Sb_09.
- Différenciation strength/cardio **explicite** : rep_targets compact vs duration+BPM.
- Non-duplication garantie avec delta / erreurs fréquentes / muscle_sensation / hints Sb_08.
- Build recommandé : **Sb_11a** (5-7h) à lancer **uniquement après** merge V1 et retour de dogfooding positif.
- Spec suivante à arbitrer : Sx_11b (programme-builder) ou Sx_11c (squad v2).
