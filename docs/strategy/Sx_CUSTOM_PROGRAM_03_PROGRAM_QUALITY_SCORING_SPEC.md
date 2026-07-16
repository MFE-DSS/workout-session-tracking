# Sx_CUSTOM_PROGRAM_03 — Program Quality Scoring Spec

**Type :** SPEC ONLY / ENGINE DESIGN / SCORING MODEL
**Date :** 2026-07-15
**Statut :** ⚪ SPEC DRAFT OPENED — pending human review · **BUILD NOT AUTHORIZED**
**Track :** `Sx_CUSTOM_PROGRAM` (parent : [`Sx_CUSTOM_PROGRAM_01`](Sx_CUSTOM_PROGRAM_01_INTELLIGENT_PROGRAM_BUILDER_SPEC.md) ✅ ACCEPTED ; EKB : [`Sx_CUSTOM_PROGRAM_02`](Sx_CUSTOM_PROGRAM_02_EXERCISE_KNOWLEDGE_BASE_SPEC.md) ✅ ACCEPTED)
**Branche :** `spec/sx-custom-program-01-intelligent-builder` (worktree isolé)
**Autorisations :** aucune migration · aucun seed · aucun code · aucune donnée modifiée

---

## 1. Verdict / statut

**SPEC ONLY.** Ce document définit le moteur de scoring A/B/C des programmes custom : contrat
moteur, modèle de sortie, sous-scores V1, règle de grade, régimes de vérité, microcopy,
persistance, QA future. **Rien n'est buildé** : `Sb_CUSTOM_PROGRAM_SCORING_*` NOT AUTHORIZED,
aucune migration, aucun seed, aucun code, aucune donnée modifiée.

## 2. Rôle du scoring

- **Évaluer un programme custom avant publication** — recalculé à chaque édition du brouillon,
  figé à la publication (§10).
- **Aider l'utilisateur à comprendre** les forces/faiblesses de SON programme : le grade
  résume, les sous-scores et raisons expliquent, les suggestions proposent des corrections
  actionnables — jamais d'injonction.
- **Sortie** : grade A/B/C + sous-scores + raisons + alertes + suggestions.
- **Jamais une vérité médicale ou scientifique absolue** — heuristique d'entraînement
  indicative, présentée comme telle (leçon `/physique` : pas de score opaque ; ici la
  **traçabilité intégrale** est la condition d'existence du grade).
- **Jamais un moteur LLM opaque** — moteur à règles, versionné, relu, reproductible.

## 3. Contrat moteur

Pattern éprouvé du repo : `overload_engine` (Sx_30) — moteur pur, testé exhaustivement.

- **Moteur pur** : aucune lecture DB dans le cœur, aucune I/O, aucune dépendance externe.
- **Déterministe** : même entrée ⇒ même `QualityReview`, bit à bit. Aucun aléa non seedé.
- **Versionné** : constante `PROGRAM_QUALITY_SCORING_VERSION` (int, démarre à 1) exposée sur
  chaque sortie — même sémantique que `OVERLOAD_ENGINE_VERSION`/`scoring_version` (Sb_24.1) :
  les règles peuvent évoluer, les évaluations passées restent interprétables.
- **Entrées** : `ProgramDefinition` (dataclass pure du moteur de génération, parent §11),
  profil déclaré (niveau, fréquence, durée cible, matériel, focus), EKB (version pinnée).
- **Sortie** : `QualityReview` (dataclass pure, §4).
- **Pas de LLM comme source de vérité** — ni dans les règles, ni dans les textes générés.

## 4. Modèle de sortie cible — `QualityReview`

```
QualityReview
  grade                 : "A" | "B" | "C"
  global_score          : int 0-100 | None   # optionnel, jamais mis en avant seul
  subscores_json        : {key: {score: 0-100, reasons: [str, ≤3]}}   # les 8 clés §5
  alerts_json           : [{subscore, severity: info|warn, message}]
  suggestions_json      : [{subscore, message}]                       # actionnable, non injonctif
  assumptions_json      : [str]        # défauts appliqués (« niveau supposé débutant »)
  missing_data_json     : [str]        # champs profil absents
  scoring_version       : int          # PROGRAM_QUALITY_SCORING_VERSION
  ekb_version           : str          # version EKB utilisée (traçabilité)
  computed_at           : datetime     # posé par l'appelant, hors moteur pur
```

Raisons/messages : français court, ≤ 3 raisons par sous-score (règle Sx_30), formulations §8.

## 5. Sous-scores V1 (8, chacun 0-100 + raisons)

| Clé | Mesure | Source |
|---|---|---|
| `volume_per_zone` | sets hebdo par `BodyZone` vs fourchettes prudentes par niveau déclaré | ProgramDefinition + EKB (`primary_body_zone`) |
| `push_pull_legs_balance` | ratios de sets hebdo entre familles de patterns | EKB (`movement_pattern`) |
| `frequency_per_zone` | fréquence hebdo de sollicitation par zone vs séances/semaine | ProgramDefinition |
| `recovery_spacing` | espacement des zones lourdement sollicitées entre séances consécutives | ProgramDefinition + EKB (`fatigue_class`) |
| `redundancy` | doublons `variant_group`/pattern dans une même séance, variantes quasi identiques | EKB (`variant_group`) |
| `duration_realism` | somme des `estimated_slot_minutes` vs budget déclaré par séance | EKB |
| `equipment_feasibility` | slots incompatibles avec le matériel déclaré | EKB (`equipment_family`, `machine_slug`) |
| `overload_compatibility` | part de slots avec ranges exploitables par le moteur Sx_30 (`overload_compatibility` EKB, rep ranges bornés) | EKB + ProgramDefinition |

Fourchettes et seuils : **constantes versionnées dans le moteur** (pas de config DB), valeurs
prudentes documentées avec leurs sources (références générales du parent §12 : WHO/ODPHP —
utilisées pour les planchers, jamais pour des promesses).

## 6. Règles de grade (comparaison)

| Option | Description | Pour | Contre |
|---|---|---|---|
| A — Moyenne pondérée simple | grade = tranches sur la moyenne pondérée | trivial | un 15/100 « matériel » peut être noyé par le reste — grade menteur |
| B — Min-score dominant | grade = tranche du pire sous-score | jamais menteur sur le point faible | brutal ; un seul sous-score moyen condamne tout, décourageant |
| **C — Hybride : moyenne pondérée + pénalités fortes** | moyenne pondérée, **plafonnée** par les sous-scores critiques : tout sous-score < 40 plafonne le grade à C ; < 60 plafonne à B | équilibré, explicable en une phrase (« ta moyenne est bonne mais le réalisme durée plafonne le grade »), non opaque | 2 constantes de plus |

**Recommandation : Option C (hybride).** Règle énonçable en une phrase, affichée dans l'UI
avec le sous-score plafonnant explicitement nommé. Seuils par défaut (OQ-SCORE-A à trancher) :
moyenne ≥ 80 → A, ≥ 60 → B, sinon C ; plafonds : sous-score < 40 ⇒ C, < 60 ⇒ B. Pondérations
par défaut : uniformes V1 (OQ-SCORE-B).

## 7. Régimes de vérité (affichés distinctement)

| Régime | Contenu | Rendu |
|---|---|---|
| Théorie générale | fourchettes volume/fréquence par défaut (constantes versionnées, sources prudentes) | implicite dans les raisons |
| Profil utilisateur déclaré | niveau/matériel/durée/focus saisis au wizard | base du calcul |
| Historique réel | **V2 seulement** — aucun signal de séance réelle en V1 | absent V1 (non-goal) |
| Données manquantes | champs absents → `missing_data_json` | listés, jamais tus |
| Inférences prudentes | défauts appliqués → `assumptions_json` (« volume estimé sur profil débutant par défaut ») | affichées à côté du grade |

Principe hérité : **silence ou prudence plutôt qu'invention** — une donnée manquante produit
une assumption visible, jamais une certitude implicite.

## 8. Microcopy (contraintes dures)

- **Interdits** : claim médical, promesse hormonale (« anabolisme », « boost de testostérone »),
  culpabilisation, **« tu dois »** (règle Sx_30 §6 reprise verbatim), « optimal »/« parfait »
  en absolu, vocabulaire de diagnostic.
- **Formulations indicatives obligatoires** : « peut aider », « semble élevé », « à vérifier »,
  « souvent utile », « d'après ton profil déclaré ».
- Mention permanente à côté du grade : **« Grille indicative — pas une vérité médicale ou
  scientifique absolue. »**
- **Grade C publiable avec avertissement explicite** (position par défaut OQ-CP-J du parent,
  reconfirmée ici en OQ-SCORE-C) — le scoring informe, il ne bloque pas ; sauf décision
  contraire future documentée.
- Ton : le programme appartient à l'utilisateur ; les suggestions sont des options, pas des
  ordres.

## 9. Persistance (comparaison)

| Option | Description | Pour | Contre |
|---|---|---|---|
| A — À la volée uniquement | recalcul à chaque affichage, rien en base | zéro schéma | perte de trace ; impossible d'auditer « le grade au moment de la publication » |
| B — Persisté à la publication seulement | snapshot unique sur l'objet publié | simple | pas d'historique des itérations du brouillon |
| **C — À la volée + trace versionnée `user_program_quality_reviews`** | recalcul à chaque édition (affichage), **une row de trace par version publiée** (grade, subscores, assumptions, `scoring_version`, `ekb_version`) — jamais réécrite | audite « pourquoi ce programme a été publié en B » ; aligne le pattern d'invariance historique du repo (rows figées + version pinnée) | une table de plus (déjà prévue au schéma parent §9) |

**Recommandation : Option C** — cohérente avec le schéma esquissé au parent
(`user_program_quality_reviews`) et avec la doctrine d'invariance historique (Sb_24.1/Sx_30 :
on fige et on versionne, on ne recompute jamais le passé).

## 10. Interaction avec l'Option C d'architecture (parent §9)

- Le scoring s'applique aux **brouillons `UserProgram*`** — c'est là que vivent wizard et
  édition par cartes.
- **Recalculé à chaque édition** (chaque POST d'édition re-score et réaffiche grade +
  sous-scores + alertes).
- **Figé à la publication** : la version publiée écrit sa row de trace (`quality_reviews`,
  §9-C) avec `scoring_version` + `ekb_version` pinnées.
- Le **`WorkoutTemplate` custom matérialisé ne devient jamais source de vérité du score** :
  il porte au plus une copie d'affichage (grade), la vérité reste la trace côté
  `UserProgram*`. Ni le catalogue système ni les tables catalogue custom ne stockent de
  logique de scoring.

## 11. QA future (tests à livrer avec le moteur)

1. Programme équilibré (fixture PPL 3j cohérente) → grade A ou B attendu.
2. Programme redondant (2× même `variant_group` dans une séance) → `redundancy` baisse +
   alerte dédiée.
3. Programme trop long (slots > budget déclaré) → `duration_realism` baisse + suggestion.
4. Matériel incompatible (slot machine sans machine déclarée) → alerte
   `equipment_feasibility`.
5. Profil incomplet → `assumptions_json` non vide + `missing_data_json` exact ; jamais de
   grade silencieusement optimiste.
6. **Déterminisme** : même entrée ⇒ même `QualityReview` (comparaison structurelle stricte).
7. Microcopy : lexique interdit absent (grep : termes médicaux/hormonaux) sur toutes les
   chaînes produites.
8. Aucun « tu dois » dans raisons/alertes/suggestions (test exhaustif sur le corpus généré).
9. Grade C reste publiable (si OQ-SCORE-C confirme) : le moteur n'émet jamais d'état bloquant.
10. Versionnage : `scoring_version` et `ekb_version` présents sur toute sortie.

## 12. Non-goals

Pas de build · pas d'UI (écrans wizard = builds parent) · pas de migration · pas de seed ·
pas de moteur de génération (spec parent §11) · pas de launch session · **pas d'historique
réel V1** (signaux de séances loggées = V2, OQ-SCORE-E) · pas de LLM · pas de recommandation
médicale · pas de modification de `quality_score.py`/`muscle_scoring.py` existants (scores de
séance/physique : domaines distincts, non touchés).

## 13. Open questions

| OQ | Question | Position par défaut proposée |
|---|---|---|
| OQ-SCORE-A | Seuils A/B/C exacts | moyenne ≥ 80 → A, ≥ 60 → B ; plafonds < 40 ⇒ C, < 60 ⇒ B |
| OQ-SCORE-B | Pondération des sous-scores | uniforme V1 ; pondérations si le dogfood le justifie |
| OQ-SCORE-C | Grade C publiable ou blocage doux | **publiable avec avertissement explicite** (aligné OQ-CP-J) |
| OQ-SCORE-D | Scoring persisté ou à la volée | Option C : à la volée + trace versionnée à la publication |
| OQ-SCORE-E | Historique réel : V2 ou V1 minimal | **V2 strict** — V1 purement déclaratif |
| OQ-SCORE-F | Précision des durées estimées | minutes entières par slot (EKB), tolérance ±20 % avant alerte |
| OQ-SCORE-G | Cardio / abdos / gainage | cardio neutre (parent §14) ; abdos/gainage comptés en volume `core` mais exclus du plafonnement overload (`overload_compatibility: limited/none`) |
| OQ-SCORE-H | Exposition des assumptions dans l'UI | bloc « Hypothèses utilisées » sous les sous-scores, toujours visible si non vide — jamais replié par défaut |

## 14. Acceptance criteria (cette spec)

- [ ] 8 sous-scores V1 définis (§5) avec sources EKB/ProgramDefinition.
- [ ] Règle de grade proposée et comparée (§6, Option C hybride).
- [ ] Modèle `QualityReview` esquissé (§4) avec versionnage moteur + EKB.
- [ ] Microcopy contrainte (§8, interdits durs + formulations obligatoires).
- [ ] Régimes de vérité distingués (§7) ; persistance recommandée (§9).
- [ ] QA future définie (§11, 10 tests).
- [ ] Registry/roadmap mis à jour (`SPEC DRAFT OPENED`).
- [ ] Build toujours interdit — human review de cette spec = prochaine décision.

## 15. Build queue proposée (aucune n'est ouverte par cette spec)

| Build | Objet | Gate |
|---|---|---|
| `Sb_CUSTOM_PROGRAM_SCORING_01` | Moteur pur + dataclasses (`QualityReview`) + tests unitaires (dont déterminisme + lexique) | spec 03 acceptée + EKB draft disponible |
| `Sb_CUSTOM_PROGRAM_SCORING_02` | Microcopy + alertes + suggestions (corpus complet, tests « tu dois »/lexique exhaustifs) | SCORING_01 |
| `Sb_CUSTOM_PROGRAM_SCORING_03` | Persistance `user_program_quality_reviews` (**si Option C §9 acceptée** ; migration additive-only isolée) | Sx_CUSTOM_PROGRAM_04 accepté |
| `Sb_CUSTOM_PROGRAM_SCORING_04` | Intégration wizard future (re-score à l'édition, figé à la publication) | builds wizard parent |

---

*Spec draft — build, migrations, seed et code applicatif explicitement non autorisés.
Prochaine décision : human review de ce document. Spec suivante dans la queue parent :
`Sx_CUSTOM_PROGRAM_04 — User Program Persistence Spec`.*
