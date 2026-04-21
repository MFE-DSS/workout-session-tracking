# Sprint Sx_13 Report — Recommendation Calibration Spec

**Date :** 2026-04-21
**Type :** SPEC ONLY — aucun code produit, aucune migration, aucun test
**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6` @ commit `91c54b1`
**Livraison :** 2 documents (spec + ce rapport)
**Successeur :** Sb_13_recommendation_telemetry_and_tuning

---

## 1. Surfaces inspectées

Lecture directe ciblée sur le chantier calibration :

- [app/services/recommendation.py](../app/services/recommendation.py) — constantes centralisées en tête, signature publique `recommend_next_session`, structure des candidats, slots de `_build_phrase`.
- [app/routers/sessions.py](../app/routers/sessions.py) — route `POST /sessions` (ligne 78–99) : signature `template_slug: Form` uniquement aujourd'hui, sans champ pour tracer la provenance.
- [app/templates/_partials/next_session_reco.html](../app/templates/_partials/next_session_reco.html) — formulaire CTA principal + liens alternatives (actuellement vers `/launcher?preselect=...` sans relais de provenance).
- [app/templates/launcher.html](../app/templates/launcher.html), [app/templates/library.html](../app/templates/library.html) — autres points de démarrage de session.
- [app/models/session.py](../app/models/session.py) — `WorkoutSession` SQLAlchemy, pour dimensionner le coût d'une colonne additive.
- `scripts/catalog_qa.py`, `scripts/machine_atlas_qa.py` — patterns existants d'outil CLI sans UI, référence pour le script calibration.

Aucune lecture superflue, aucune exploration de services non concernés par la calibration.

## 2. Ce qui existe déjà dans Sb_12 et reste acquis

- Moteur déterministe complet (scoring 4 composants, filtres, fallback, fallback cold-start, phrase composée).
- **Toutes les constantes nommées en tête de fichier** — la barrière technique au tuning est déjà tombée.
- 11 tests unitaires + 6 tests surface qui protègent la logique cœur. Un changement de constante qui casse le sens génère une régression immédiate.
- Phrase explicative ≤ 140 chars, jamais vide, neutre — pas d'enjeu éditorial lourd, seulement des slots à affiner si trop répétitifs.
- Surface UI discrète, cohérente avec le reste du produit (pas de badge IA, pas d'effet magique).

**Ce qui rend la calibration peu chère** :
- Constantes ajustables sans toucher à la logique.
- Tests rapides (4s sur le fichier service).
- Moteur testé sans DB pour la partie pure (`_staleness_from_hard_sets`, `_build_phrase` implicite via les tests surface).

## 3. Ce qui manque pour calibrer

Trois manques concrets, tous adressés dans §J de la spec principale :

### 3.1 Pas de trace de la provenance d'une session

Aujourd'hui, une `WorkoutSession` en DB ne porte aucun indicateur disant si elle a été lancée via la reco top, une alternative, le picker classique, ou un démarrage depuis `/library`. Sans ce signal, `reco_acceptance_rate` et `alt_click_rate` sont incalculables.

**Besoin** : un champ `creation_source String(16) NULL` sur `workout_sessions` + transit dans le formulaire POST.

### 3.2 Pas d'agrégation pour l'observation

Le dashboard home ne montre pas les taux d'acceptation, et il ne doit pas le montrer (c'est un outil utilisateur, pas un outil admin). Il faut un **script CLI** séparé, aligné avec `catalog_qa.py`.

**Besoin** : `scripts/reco_calibration_report.py` qui lit les dernières sessions et produit un rapport stdout court.

### 3.3 Pas de protocole structuré de dogfooding

Sans protocole écrit, l'observation sera anecdotique, dispersée, non exploitable. Il faut un rituel léger (< 2 min / jour × 7 jours) et un fichier dédié `DOGFOOD_SB_12_NOTES.md`.

**Besoin** : protocole formel documenté (§E de la spec) sans créer d'outillage supplémentaire.

## 4. Points à calibrer en priorité

Hiérarchie suggérée après observation :

### P0 — Fatigue threshold & redundancy cutoff
`FATIGUE_HIGH_THRESHOLD=70` et `REDUNDANCY_HARD_SETS_CUTOFF=4` ont un effet binaire visible immédiatement (déclenchement ou pas d'un filtre). Si la passe dogfooding montre que la reco dégrade à tort (fatigue perçue faible) ou exclut à tort un template pourtant souhaité, **ajuster ces deux-là en premier** — l'effet est direct et lisible.

### P1 — Pondération staleness vs catalog affinity
`WEIGHT_STALENESS=40` et `AFFINITY_CORE=15` se marchent sur les pieds : la staleness pousse vers les zones fraîches, l'affinité core biaise vers les 6 templates principaux. Si on observe que les spécialisations ne sortent jamais (P1 symptôme), il faut rééquilibrer ces deux. Probablement baisser `AFFINITY_CORE` de 15 → 10 avant de toucher à `WEIGHT_STALENESS`.

### P2 — Specialization ratio
`SPECIALIZATION_STALE_RATIO=0.5` est le seul verrou qui fait apparaître un catch-up dans le top-3. Si les catch-up n'apparaissent jamais malgré une zone manifestement faible, ouvrir à 0.6 ou 0.7.

### P3 — Phrase fallback
La phrase « Suite naturelle après ton historique récent → {name} » est le filet de sécurité de `_build_phrase`. Si elle revient trop souvent (>3 fois sur 10), c'est que les autres slots se déclenchent trop peu. Action éditoriale, pas de constante.

### P4 — Surfaces UI
Si `bypass_rate` est élevé sans raison évidente dans les notes, suspecter un problème d'affichage (bloc trop bas sur la page, CTA peu visible). Action visuelle, pas logique.

## 5. Ambiguïtés ouvertes

1. **Volume utilisateur V1 = 1** — les indicateurs vont être qualitatifs, jamais statistiquement significatifs. Assumer dès le début et ne pas pondérer les décisions comme si on avait 1000 utilisateurs.
2. **Phrase recalculée post-hoc peut diverger** de celle réellement affichée (si les signaux ont bougé entre l'affichage et le POST de création). V1.5 : acceptable. V2 : persistance optionnelle possible.
3. **Quand arrêter de calibrer ?** — pas de règle stricte. Proposition : quand 2 passes consécutives de 7 jours ne suggèrent aucune modification de constante, le moteur est considéré stable.
4. **Interaction avec readiness quotidienne** (non consommée V1) — si la calibration montre que fatigue_score est souvent faux, faudra-t-il intégrer readiness ? Probable, mais c'est un Sx_14 dédié, pas une calibration de Sb_13.
5. **Cold-start calibré sur `< 3 séances lifetime`** — si l'utilisateur pré-existant a des centaines de séances, le signal est parfait. Si le cas « reset DB + compte neuf » arrive, comportement cold-start attendu — documenté.

## 6. Pourquoi cette calibration est le meilleur prochain sprint

Quatre raisons alignées avec le principe Sx_10 (« ne pas ouvrir de chantier parallèle non nécessaire ») :

1. **ROI direct** — 4–6h de build produisent une boucle d'amélioration **permanente** de la reco. Programme-builder (Sx_11b, 15–20h) n'améliore pas la reco, il l'ignore.
2. **Protection du moteur existant** — sans calibration, un éventuel changement dans un sprint ultérieur (ex. nouveaux templates dans un Sx_14) ne pourra pas s'appuyer sur un moteur validé.
3. **Cohérence discipline** — Sx_12 §M listait explicitement « calibrage V1 mal ajusté » comme **premier risque**. Le traiter avant toute extension respecte le contrat spec → build → validation.
4. **Effort marginal** — les briques sont là (constantes nommées, tests en place), il reste à ajouter 1 colonne + 1 script + 1 protocole. Rapport effort/valeur extrêmement favorable.

**Alternative rejetée :** Sx_11b programme-builder maintenant. Valeur utilisateur incontestable à terme, mais bâtir par-dessus un moteur non-calibré revient à empiler deux incertitudes. À ouvrir après Sb_13 + une passe dogfooding.

## 7. Recommandation explicite du prochain build

**Sb_13 — Recommendation Telemetry & Tuning**, scope §M de la spec principale.

Contenu :
- Migration additive `creation_source` sur `workout_sessions`.
- Router accepte + persiste ; templates injectent les 4 valeurs (`reco_top`, `reco_alt`, `launcher`, `library`).
- Script CLI `scripts/reco_calibration_report.py` produisant 4 métriques + top phrases.
- 5 tests service + 3 tests script.
- Report de build.

**Effort estimé :** 4–6h.

**Précondition immédiate avant Sb_13 :** aucun bug bloquant sur affichage Sb_12 (micro-dogfooding déjà effectué selon les préconditions du prompt). Si un bug apparaît, le corriger en Sb_12.1 d'abord.

**Séquence post-Sb_13 :**
1. Déployer Sb_13.
2. Lancer la passe dogfooding 7 jours selon §E (notes dans `docs/DOGFOOD_SB_12_NOTES.md`).
3. J+7 : exécuter `scripts/reco_calibration_report.py`.
4. Décider une ou deux modifications de constantes (ou aucune).
5. Arbitrer l'ouverture du chantier suivant : **Sx_11b programme-builder** (si reco validée) ou **Sx_13.1 cycle calibration 2** (si reco encore douteuse).

## 8. Livrables produits par ce sprint

| Fichier | Action |
|---------|--------|
| `docs/strategy/SPIGNOS_RECOMMENDATION_CALIBRATION_SPEC_v1.md` | New |
| `docs/SPRINT_Sx_13_recommendation_calibration_spec_REPORT.md` | New (ce rapport) |

Aucun code. Aucune migration. Aucun test.

## 9. Synthèse exécutive

- Calibration possible **uniquement** avec un signal minimal de provenance → un seul champ DB additif (`creation_source`), un script CLI, un protocole dogfooding 7j.
- 4 indicateurs retenus : `reco_acceptance_rate`, `alt_click_rate`, `bypass_rate`, `phrase_repetition_rate`. Pas de mesure JavaScript, pas de dashboard.
- **Option H1 retenue** (signal passif uniquement). Pas de bouton « pas cette suggestion » V1.5. Trop de bruit pour un signal que le bypass capte déjà.
- 16 constantes calibrables cartographiées avec priorité de tuning. P0 : fatigue threshold + redundancy cutoff.
- Aucune extension produit (programme-builder, squad v2) à ouvrir avant d'avoir validé que la reco tape juste.
- **Build recommandé : Sb_13** (4–6h), puis **passe dogfooding 7j**, puis arbitrage produit. Séquence disciplinée, ROI direct sur la qualité du moteur.
