# Sx_CUSTOM_PROGRAM_01 — Intelligent Program Builder Spec

**Type :** SPEC ONLY / PRODUCT ARCHITECTURE / DOMAIN DESIGN
**Date :** 2026-07-15
**Statut :** ⚪ SPEC DRAFT — pending human review
**Branche :** `spec/sx-custom-program-01-intelligent-builder` (depuis la branche canonique, docs-only)
**Track :** `Sx_CUSTOM_PROGRAM` — FUTURE PRODUCT TRACK, parallèle au cycle UI/Auren actif
**Autorisations :** build ❌ · migration ❌ · code `app/` ❌ · seed ❌ · CSS/JS/template ❌
**Audit source :** audit read-only PHASE 1 du 2026-07-15 (branche spec, aucun code touché)

---

## 1. Résumé exécutif

SPIGNOS/Auren ne propose aujourd'hui que des programmes **système** (16 templates
seedés depuis `data/reference_split.json`, catalogue Push/Pull/Legs + utility +
specialization). L'utilisateur ne peut ni composer son propre programme, ni le
sauvegarder, ni le relancer.

Ce track introduit le **Custom Program Builder intelligent** en trois couches :

1. **Custom Program Builder** — wizard guidé (durée / objectif / style / focus /
   matériel), proposition automatique **déterministe**, édition par cartes,
   validation, sauvegarde, réutilisation depuis la librairie.
2. **Exercise Knowledge Base (EKB)** — catalogue structuré d'exercices, variantes
   fines, machines, patterns moteurs, muscles ; s'appuie sur les fondations déjà
   livrées (Sx_32 `BodyZone`/`Muscle`/`ExerciseMuscleMapping`, `exercise_properties.json`
   Sb_22a, `cross_pattern_substitutions.json`).
3. **Program Quality Scoring A/B/C** — grille d'évaluation **explicable**
   (sous-scores + raisons + alertes + recommandations de correction), jamais
   présentée comme vérité scientifique absolue, avec distinction explicite entre
   théorie générale, profil utilisateur, historique réel et données manquantes.

**Recommandation de modèle : Option C (hybride)** — les brouillons vivent dans des
tables séparées `UserProgram*` (zéro risque de wipe par le seed, zéro pollution du
catalogue) ; la **publication** matérialise le programme validé en `WorkoutTemplate`
custom **protégé**, ce qui réutilise sans duplication tout le pipeline aval
(`session_builder`, overload, history, stats, KPIs). L'Option A naïve (étendre
`WorkoutTemplate` directement) est **rejetée** : le seed reconstruit intégralement
`workout_templates` à chaque bump de version (`seed.py`, DELETE sans filtre) et
détruirait les programmes utilisateur.

**Rien n'est buildé par cette spec.** Aucune migration, aucun code applicatif,
aucune modification du seed. Prochaine décision : human review de cette spec,
puis specs filles (`Sx_CUSTOM_PROGRAM_02` → `05`) avant tout build.

---

## 2. Problème utilisateur

- L'utilisateur avancé veut un programme **à lui** : split personnel, exercices
  choisis selon ses machines disponibles, focus sur ses points faibles — sans
  perdre le moteur de séance existant (console de saisie, dernière fois,
  overload hints, historique).
- Aujourd'hui, la seule échappatoire est la **substitution par slot** (V1, Sb_03),
  qui reste bornée au programme système prescrit.
- Composer un programme est difficile sans guidance : volume par groupe
  musculaire, équilibre push/pull/legs, fréquence, récupération, redondance
  d'exercices. Un builder « feuille blanche » produirait des programmes
  incohérents ; un builder **guidé + évalué** produit des programmes viables.
- Le besoin réel n'est pas « créer un programme custom » mais : **« construire un
  programme personnel cohérent, guidé par des règles d'entraînement, compatible
  avec le moteur de séance SPIGNOS, éditable à la carte, sauvegardable, puis
  évalué par une grille explicable A/B/C. »**

## 3. Vision produit

Trois couches découplées, chacune spécifiée puis buildée séparément :

| Couche | Rôle | Nature |
|---|---|---|
| Custom Program Builder | wizard → proposition → édition par cartes → validation → sauvegarde → librairie | Produit / UX (SSR Jinja, no-JS fallback, Auren Terminal) |
| Exercise Knowledge Base | catalogue exercices/variantes/machines/patterns/muscles, classification structurée | Données + modèle (fondations Sx_32 réutilisées) |
| Program Quality Scoring | note A/B/C + sous-scores + explications + alertes + corrections | Moteur pur, déterministe, explicable |

Principes produit hérités (Sx_TRANSFORM_01, contraignants) :

- **une décision par écran** ; mobile-first SSR ; pas de React ; no-JS fallback ;
- **pas de score opaque** : la leçon `/physique` (score A/B/C opaque en cours de
  dépréciation, cf. `Sb_BI_01.next`) s'applique — le grade A/B/C du builder n'est
  acceptable **que** parce qu'il est intégralement traçable (sous-scores +
  raisons lisibles), et les sous-scores priment sur la lettre dans l'UI ;
- **silence plutôt que fausse donnée** ; confidence visible ; non-médical ;
- **aucune génération LLM opaque comme source de vérité** : la génération est
  déterministe et reproductible ; un LLM pourrait au mieux, dans un futur non
  spécifié ici, proposer des suggestions clairement étiquetées, jamais faire
  autorité sur le contenu d'un programme.

## 4. Périmètre

### V1 (ce track, après acceptance des specs filles)

- Wizard guidé : durée de séance, nb séances/semaine, objectif (hypertrophie
  V1), style de split, zones de focus, matériel disponible.
- Génération déterministe d'une proposition de programme complet (1 à N
  templates de séance) avec set schemes et rep targets.
- Édition par cartes : réordonner, remplacer un exercice (via EKB + graphe de
  substitution), ajuster séries/rep ranges, supprimer/ajouter un slot.
- Scoring A/B/C explicable, recalculé à chaque édition, avec alertes et
  suggestions de correction.
- Sauvegarde en brouillon, validation, **publication** (le programme devient
  lançable comme séance), réutilisation depuis la librairie (section dédiée).
- Compatibilité totale du pipeline séance : console de saisie, snapshots,
  dernière fois, overload hints, history, KPIs, export.

### V2 (hors périmètre V1, esquissé)

- Intégration du programme custom dans le moteur de **recommandation**.
- Partage de programmes entre utilisateurs (squad).
- Personnalisation par l'historique réel (charges initiales suggérées,
  détection de redondance avec l'historique, readiness).
- Blocs cardio avancés (intervalles) ; périodisation multi-semaines.
- Suggestions assistées (couche optionnelle, jamais source de vérité).

### Non-goals — hors périmètre définitif de ce track

- Diagnostic médical, prescription pour blessure/pathologie, promesse
  hormonale ou « anabolisme mesuré » — interdits durs.
- Training to failure imposé.
- Réécriture du catalogue système ou du seed existant au-delà des gardes
  strictement nécessaires (cf. §15).
- Renommage SPIGNOS/Auren dans le code (réservé `Sx_UI_10`).

## 5. User stories

- **US-1** — En tant qu'utilisateur, je lance un wizard qui me demande combien
  de temps je peux m'entraîner, combien de fois par semaine, mon objectif, mon
  niveau et mon matériel, et j'obtiens une proposition de programme complète.
- **US-2** — Je modifie la proposition carte par carte : je remplace « élévation
  latérale haltères debout » par « élévation latérale câble unilatéral » parce
  que c'est ce que ma salle propose.
- **US-3** — À chaque modification, je vois la note A/B/C évoluer et je
  comprends **pourquoi** (ex. « volume épaules élevé + 2 exercices redondants sur
  le même pattern »), avec une suggestion de correction.
- **US-4** — Je sauvegarde mon programme en brouillon et je le reprends plus tard.
- **US-5** — Je publie mon programme validé ; il apparaît dans ma librairie dans
  une section « Mes programmes » et je peux lancer une séance dessus exactement
  comme sur un template système.
- **US-6** — Mes séances lancées sur mon programme alimentent « dernière fois »,
  les deltas, l'historique par exercice et les hints d'overload, comme pour un
  programme système.
- **US-7** — Si je modifie un programme déjà publié, mon historique passé reste
  intact et cohérent (aucune réécriture, aucune contamination inter-versions).
- **US-8** — Si mes réponses au wizard sont incomplètes, le builder choisit des
  défauts prudents et me le dit (« volume estimé sur profil débutant par
  défaut »), au lieu d'inventer une certitude.

## 6. Flux UX wizard (V1, SSR, no-JS fallback)

Chaque étape = un écran, une décision (principe Auren). Formulaires POST
classiques ; l'état du wizard vit dans le brouillon `UserProgram` (statut
`draft`), jamais côté client.

1. **Cadre** — séances/semaine (2–6), durée cible par séance (30/45/60/75/90 min).
2. **Objectif & niveau** — objectif V1 : hypertrophie (seul choix actif V1,
   libellés prudents) ; niveau déclaré : débutant / intermédiaire / avancé.
3. **Style de split** — proposé automatiquement selon la fréquence (2j : full
   body ; 3j : full ou PPL ; 4j : upper/lower ×2 ; 5-6j : PPL + focus), avec
   override manuel.
4. **Focus** — 0 à 2 zones prioritaires (les 11 `BodyZone` existantes),
   optionnel.
5. **Matériel** — familles d'équipement disponibles (barre, haltères, machines,
   câble, poids de corps) ; V1 grossier par famille, V2 par machine.
6. **Proposition** — programme généré (cartes par séance), grade A/B/C +
   sous-scores affichés immédiatement.
7. **Édition par cartes** — remplacer (liste filtrée par EKB : même pattern /
   même zone / matériel compatible), réordonner, ajuster séries/reps,
   ajouter/supprimer. Re-score à chaque POST.
8. **Validation & sauvegarde** — récap + alertes restantes ; sauvegarde
   brouillon à tout moment ; publication explicite (« Rendre lançable »).

Microcopy contraint : jamais d'injonction (« tu dois » interdit — règle Sx_30),
jamais de claim médical, mention visible « Grille indicative, pas une vérité
médicale ou scientifique absolue ».

## 7. Domain model actuel (état des lieux, audit 2026-07-15)

- **Catalogue** : `WorkoutTemplate` → `TemplateExercise` → `RepTarget`
  (`app/models/catalog.py`). 100 % système, aucun champ de propriété
  (`user_id`/`origin` inexistants). `slug` UNIQUE global. Groupage par
  `catalog_section` (`core`/`utility`/`specialization`/`archived`) + `display_order`.
- **Seed** (`app/services/seed.py`) : à chaque changement de `version` de
  `reference_split.json`, **DELETE intégral sans filtre** de `RepTarget`,
  `TemplateExercise`, `WorkoutTemplate` puis reconstruction. C'est le danger
  n°1 pour toute donnée utilisateur logée dans ces tables.
- **Instanciation séance** : `POST /sessions` → `instantiate_session()`
  (`session_builder.py`) fige `template_slug_snapshot` / `exercise_code_snapshot`
  / `exercise_name_snapshot`, pré-crée les rows warmup/work depuis `RepTarget`.
  FKs catalogue nullables `ON DELETE SET NULL` : l'historique survit à un reseed.
- **Identité analytique** : `(template_slug_snapshot, exercise_code_snapshot)`
  — consommée par `stats.last_time_by_exercise_code` (substitution-aware,
  Sb_DOGFOOD_01.1), `overload_inputs` (garde d'identité Sb_30.bugfix),
  `exercise_history`, `kpis`, `anomalies`, `session_recap`, `session_review`,
  `export_builder`, `sharing`, `briefing`, `restore`, router sessions, 2 templates.
- **Overload** : `build_overload_input_for_exercise` exige `se.template_exercise`
  non-NULL **et** des `rep_targets` — un modèle de programme user sans lien vers
  `template_exercises` rend l'overload définitivement muet.
- **Reco** : `recommendation._load_templates` charge tout `WorkoutTemplate` sauf
  `archived` — toute row user dans cette table entrerait silencieusement dans le
  moteur. **Launcher** : immunisé (BRANCH_TREE hardcodé par slugs système).
- **Codes exercice** : `TemplateExercise.code` = slot par template (E1..E7).
  Découverte Sb_32.2 : l'identité stable pour le mapping musculaire est le
  **nom** d'exercice (`exercise_code = name`). L'identité historique par slot ne
  survit pas à une réorganisation du programme — d'où l'exigence de versioning (§15).
- **Fondations EKB déjà livrées** : `BodyZone` (11 zones seedées), `Muscle`
  (table vide V1, aucune anatomie inventée), `ExerciseMuscleMapping`
  (91 exercices, primary/secondary), `exercise_properties.json` (Sb_22a :
  pattern moteur, zone, muscle_group, equipment_family, chain),
  `cross_pattern_substitutions.json` (ponts inter-patterns), graphe de
  substitution V1 (JSON, Sb_03/Sb_22).

## 8. Options de modèle cible

### Option A — Étendre `WorkoutTemplate` (rejetée comme défaut naïf)

Colonnes additives sur les tables catalogue : `owner_user_id`, `is_custom`,
`source`, `status`, `parent_template_id`, `quality_grade`, `quality_score_json`.

- ✅ Réutilisation immédiate et totale du pipeline aval (builder, overload,
  history) ; zéro nouvelle table.
- ❌ **Wipe par le seed** : `seed_reference_split` fait `DELETE` sans filtre ;
  chaque bump de version du catalogue système détruirait les programmes user.
  Corriger exige de modifier le seed — précisément le composant le plus
  sensible — **avant** toute première row user, et d'en faire une garde testée
  à vie.
- ❌ Pollution silencieuse : reco (`catalog_section != 'archived'`), `/library`,
  et tout futur consommateur du catalogue devraient être filtrés un par un ;
  chaque oubli est une fuite.
- ❌ Namespace de slugs partagé avec le système : collision possible avec tout
  slug système futur.
- ❌ Les états de brouillon (wizard en cours, invalide, non lançable) n'ont pas
  leur place dans une table que 15+ consommateurs traitent comme « catalogue
  lançable ».

### Option B — Tables séparées `UserProgram*` (pur)

`user_programs`, `user_program_exercises`, `user_program_rep_targets`,
`user_program_quality_reviews`. Aucun contact avec les tables catalogue.

- ✅ Isolation parfaite : zéro risque seed, zéro pollution reco/librairie,
  namespace propre, états draft naturels.
- ❌ **Lancement de séance** : `instantiate_session` prend un `WorkoutTemplate` ;
  il faudrait soit une abstraction `ProgramDefinition` dans `session_builder`
  (refactor d'un service central), soit un chemin parallèle dupliqué.
- ❌ **Overload muet** : `SessionExercise.template_exercise_id` resterait NULL →
  pas de rep targets lisibles → hint `unknown` à vie, set scheme prescrit non
  rendu. Corriger exige soit une FK additive `user_program_exercise_id` sur
  `session_exercises` + généralisation de `overload_inputs` (code analytique le
  plus sensible du repo, déjà durci deux fois), soit d'accepter la perte.
- ❌ Chaque consommateur qui rend le « prescrit » via `template_exercise` doit
  apprendre une seconde source.

### Option C — Hybride : drafts `UserProgram*`, publication en `WorkoutTemplate` custom protégé

Les brouillons et tout le cycle wizard/édition/scoring vivent dans
`UserProgram*` (Option B pour la phase de construction). À la **publication**,
le programme est **matérialisé** en `WorkoutTemplate` + `TemplateExercise` +
`RepTarget` marqués custom (`owner_user_id` non NULL, `catalog_section`
réservée `user`), avec slug namespacé. Le `UserProgram` garde la main
(source d'édition, versions, scoring) ; le template custom matérialisé est un
**artefact de publication**, régénéré à chaque nouvelle version publiée.

- ✅ Isolation de la phase risquée (brouillons hors catalogue, jamais wipés).
- ✅ Pipeline aval intact **sans duplication** : `instantiate_session`, overload
  (FK `template_exercise` + `rep_targets` réels), history, stats, KPIs, export
  fonctionnent tels quels sur les séances lancées.
- ✅ Périmètre des gardes minimal et énumérable (cf. §15) : filtre du DELETE du
  seed, filtre reco, section librairie, namespace slug. Quatre gardes, toutes
  testables unitairement.
- ⚠️ Coût : une étape de matérialisation à spécifier proprement (idempotente,
  versionnée), et les 4 gardes ci-dessus à livrer **avant** la première
  publication (ordonnancement imposé dans la build queue, §20).

## 9. Recommandation de modèle

**Option C (hybride), recommandée.** Option B conservée comme repli documenté si
la review humaine refuse toute écriture user dans les tables catalogue — au prix
de l'abstraction `ProgramDefinition` dans `session_builder` et d'une
généralisation d'`overload_inputs`, jugées plus risquées que les 4 gardes de
l'Option C car elles touchent le cœur analytique. **Option A rejetée** comme
défaut naïf (wipe seed + pollution + namespace partagé).

Contrats durs attachés à l'Option C (non négociables au build) :

1. **Wipe-guard seed** : le DELETE du seed devient
   `WHERE owner_user_id IS NULL` (ou équivalent par `catalog_section`),
   livré + testé (test « un bump de version ne détruit jamais une row custom »)
   **avant** toute matérialisation. Ce sera l'unique modification autorisée du
   seed, dans un build dédié.
2. **Namespace de slugs** : slugs custom préfixés (proposition :
   `up{user_id}-{slug}-v{n}`), collision avec les slugs système impossible par
   construction ; format tranché en OQ-CP-A.
3. **Filtres catalogue** : reco (`_load_templates`) et `/library` filtrent ou
   séparent les templates custom ; launcher inchangé (immunisé).
4. **Immutabilité des versions publiées** : une version publiée n'est jamais
   modifiée en place ; éditer = nouvelle version (nouveau slug versionné),
   l'ancienne passe `archived`. Protège l'identité historique
   `(template_slug_snapshot, exercise_code_snapshot)` — cf. §15.

Modèle de données cible (esquisse, à affiner dans `Sx_CUSTOM_PROGRAM_04`) :

```
user_programs             (id, user_id FK, title, status[draft|validated|published|archived],
                           wizard_answers_json, current_version, quality_grade,
                           quality_score_json, created_at, updated_at)
user_program_sessions     (id, user_program_id FK, position, name, kind[strength|cardio], focus)
user_program_exercises    (id, user_program_session_id FK, position, exercise_name,
                           variant_key, equipment_family, set_scheme, notes)
user_program_rep_targets  (id, user_program_exercise_id FK, set_index, min_reps, max_reps)
user_program_quality_reviews (id, user_program_id FK, version, grade, subscores_json,
                           alerts_json, computed_at)   # trace, jamais réécrite
-- publication → WorkoutTemplate(owner_user_id, catalog_section='user',
--                slug='up{user_id}-{slug}-v{n}') + TemplateExercise + RepTarget
```

Toutes les migrations futures : **additive-only**, une à la fois, chacune dans
son propre build (contrat CLAUDE.md §2).

## 10. Exercise Knowledge Base (EKB)

Objet de la spec fille `Sx_CUSTOM_PROGRAM_02`. Exigences posées ici :

- **Ne pas repartir de zéro** : consolider `exercise_properties.json` (Sb_22a),
  `ExerciseMuscleMapping` (91 exos), `cross_pattern_substitutions.json` et les
  substituts du catalogue en une base **unique, versionnée, déterministe**.
- Classification par exercice/variante : muscle principal (`BodyZone` V1,
  `Muscle` quand la table sera peuplée), muscles secondaires, équipement
  (famille + machine), pattern moteur, chaîne (compound/isolation), stabilité
  (libre/guidé/machine), classe de fatigue systémique (haute/moyenne/basse),
  difficulté technique (débutant/intermédiaire/avancé).
- **Variantes fines** de premier ordre — exemple canonique :
  élévation latérale haltères debout · haltères assis · câble unilatéral ·
  machine assis · machine guidée = 5 entrées distinctes partageant un
  `variant_group` (« élévation latérale ») pour la détection de redondance et
  la substitution.
- Identité : le **nom canonique** reste la clé (cohérent avec Sb_32.2) ; un
  `variant_group` + attributs structurés s'y ajoutent. Aucun renommage des
  noms historiques (invariance analytique).
- Stockage : OQ-CP-D (JSON versionné seedé en DB via le pipeline existant —
  recommandé — vs JSON pur lu à chaud). Dans les deux cas : additive-only,
  QA script de classifiabilité (comme Sb_03), pas de suppression de noms.
- L'EKB sert 3 consommateurs : génération (§11), édition par cartes (listes de
  remplacement filtrées), scoring (§12 : volume par zone, redondance, fatigue).

## 11. Generation Engine

Objet détaillé de `Sx_CUSTOM_PROGRAM_02`/`04` ; contrat posé ici :

- **Fonction pure et déterministe** : `(wizard_answers, EKB version, seed
  optionnel) → ProgramDefinition`. Même entrée ⇒ même programme. Pas d'accès
  DB dans le cœur (pattern `overload_engine`), pas d'aléa non seedé, pas de LLM.
- Génération par contraintes, pas par magie : budget temps par séance →
  nombre de slots ; split choisi → patterns requis par séance ; focus → volume
  additionnel borné sur 1-2 zones ; matériel → filtre EKB ; niveau → plafonds
  de volume et de fatigue, part de guidé vs libre.
- Sortie **explicable** : chaque slot porte une raison courte (« pattern push
  horizontal requis par le split », « focus épaules : +1 isolation »).
- Rep targets et set schemes générés depuis des gabarits par objectif/niveau
  (hypertrophie V1 : ranges type 6-10 / 8-12 / 12-15 selon le rôle du slot),
  jamais de prescription d'échec systématique.
- Le moteur émet un `ProgramDefinition` (dataclass pure) — la même structure
  que consommera l'étape de matérialisation. C'est l'abstraction qui isole le
  moteur du modèle de persistance.

## 12. Program Quality Scoring A/B/C

Objet détaillé de `Sx_CUSTOM_PROGRAM_03` ; contrat posé ici :

- **Moteur pur, déterministe, versionné** (`SCORING_ENGINE_VERSION`, pattern
  Sx_30) : `(ProgramDefinition, profil, EKB) → QualityReview`.
- **Sous-scores V1** (chacun 0-100 + raisons en français court) :
  1. volume par groupe musculaire vs fourchettes prudentes par niveau ;
  2. équilibre push/pull/legs (ratios de sets hebdo) ;
  3. fréquence par zone vs séances/semaine ;
  4. récupération (espacement des zones sollicitées entre séances) ;
  5. redondance (doublons de `variant_group`/pattern dans une même séance) ;
  6. réalisme durée (temps estimé vs budget déclaré) ;
  7. faisabilité matériel (slots incompatibles avec l'équipement déclaré) ;
  8. compatibilité progression (ranges exploitables par le moteur d'overload).
- **Grade A/B/C** = agrégation transparente des sous-scores (règle simple
  documentée, ex. min pondéré) ; l'UI montre d'abord les sous-scores et les
  alertes, la lettre est un résumé — **jamais un score opaque** (leçon
  `/physique`).
- **Alertes + corrections** : chaque sous-score dégradé produit une alerte
  actionnable (« 9 sets épaules le jour 1 et 8 le jour 2 : espace-les ou
  réduis »), formulée sans injonction médicale ni « tu dois ».
- **Quatre régimes de vérité, affichés distinctement** :
  - *théorie générale* — les fourchettes par défaut (sources §« Références ») ;
  - *profil utilisateur* — niveau/matériel/durée déclarés ;
  - *historique réel* — V2 : signaux issus des séances loggées ;
  - *données manquantes* — défauts prudents + mention explicite (« estimé,
    profil incomplet ») ; le silence ou la prudence priment sur l'invention.
- Le score n'est **jamais bloquant** V1 : un programme C reste sauvegardable et
  publiable avec avertissement (OQ-CP-J confirme ou infirme).

### Références (prudentes, non prescriptives)

- **WHO physical activity guidance** — toute activité compte, « any amount of
  physical activity is better than none » ; le renforcement musculaire est
  bénéfique pour tous les adultes. Utilisée pour le ton (encourageant, jamais
  culpabilisant) et les planchers de fréquence.
- **ODPHP Physical Activity Guidelines for Americans** — cadre evidence-based
  pour les fourchettes d'activité et de renforcement (≥ 2 séances/semaine de
  renforcement des grands groupes musculaires).
- **Principes généraux du resistance training** — individualisation,
  régularité, progression graduelle, récupération, adéquation à l'objectif.
  Aucune promesse hormonale, aucun « anabolisme mesuré », aucune vérité absolue :
  la grille est une **heuristique indicative** et se présente comme telle.

## 13. Personalization Model

- **Entrées V1** : réponses wizard (fréquence, durée, objectif, niveau déclaré,
  focus, matériel). Toutes déclaratives.
- **Défauts prudents** : niveau absent → débutant ; matériel absent → familles
  courantes de salle commerciale ; focus absent → programme équilibré. Chaque
  défaut appliqué est affiché (régime « données manquantes », §12).
- **V2 (non buildé, à spécifier)** : croisement avec l'historique réel
  (volumes récents par zone via `muscle_scoring`, charges de départ via
  `last_time`), readiness, Body Intelligence. Contrainte posée dès maintenant :
  ces signaux **s'ajoutent** comme sous-scores/annotations traçables, ils ne
  transforment pas le moteur en boîte noire.
- Aucune donnée de santé, de blessure ou de pathologie n'est collectée ni
  utilisée. Pas de branche « douleur/blessure » dans le wizard : hors périmètre
  définitif (non-médical).

## 14. Cardio Support

- Le modèle existant sait déjà représenter le cardio : `kind="cardio"`,
  0 exercice + `cardio_note`, ou exercices simples (cf. `liss-only`, `liss-abs`) ;
  capture dédiée sur la séance (durée, bpm, calories machine indicatives).
- V1 : le wizard propose optionnellement d'ajouter **1 bloc LISS** par semaine
  (séance cardio dédiée dans le programme, `kind=cardio`), sans prétention de
  prescription cardio fine. Le scoring le traite en neutre (n'améliore ni ne
  dégrade les sous-scores force ; compte dans le réalisme durée).
- Intervalles, zones cardio, périodisation cardio : V2+, hors périmètre V1
  (OQ-CP-G peut restreindre encore : cardio entièrement différé en V2).

## 15. Intégration session_builder / history / overload

Par construction (Option C), une séance lancée sur un programme custom passe
par le chemin **existant** : template custom matérialisé → `instantiate_session`
→ snapshots → console → analytics. Contrats d'identité :

1. **Slug versionné immuable** : `up{user_id}-{slug}-v{n}`. L'historique d'une
   version est étanche par slug — exactement la sémantique que la garde
   d'identité Sb_30.bugfix et `last_time` attendent. Éditer un programme publié
   crée `-v{n+1}` ; l'ancien template passe `archived` (invisible librairie,
   historique intact via snapshots + FK SET NULL).
2. **Codes de slot stables par version** : E1..E7 attribués à la publication,
   figés pour la version. La continuité inter-versions (« mon E2 de v2 est le
   même exercice que le E3 de v1 ») n'est **pas** promise V1 — c'est le même
   trade-off que le catalogue système assume déjà entre versions de seed ;
   documenté dans l'UI de l'historique le cas échéant (OQ-CP-B).
3. **Overload** : fonctionne nativement (FK `template_exercise` + `rep_targets`
   réels). La politique de substitution existante s'applique sans modification.
4. **KPIs/exports/history** : keyés snapshots — aucune modification requise.
5. **Pas de modification de `session_builder`** tant qu'une abstraction
   `ProgramDefinition` n'a pas été spécifiée et acceptée ; V1 n'en a pas besoin
   côté lancement (la matérialisation produit des rows catalogue standard).
   `ProgramDefinition` reste l'interface interne moteur → matérialisation (§11).

## 16. Branching and Integration Plan (obligatoire)

- Ce track vit sur **branche dédiée** ; la présente spec sur
  `spec/sx-custom-program-01-intelligent-builder`, créée depuis la branche
  canonique à jour.
- **PR draft docs-only** pour ce sprint spec ; aucun merge tant que les builds
  UI actifs (cycle Sx_UI/Auren, batch SESSION_UX, Sb_UI_10.x) ne sont pas
  stabilisés et mergés selon la décision opérateur.
- Le futur build est découpé en **petites branches** (`sb/custom-program-01-…`,
  une par sprint Sb), chacune rebasée sur la canonique **avant chaque PR**.
- **Migrations futures isolées** : une migration par build, additive-only,
  jamais groupées. **Aucune migration tant que le modèle cible (§9) n'est pas
  accepté en human review.**
- **Aucune modification du seed avant validation** explicite du wipe-guard
  (contrat §9.1) ; le wipe-guard est un build dédié, testé, antérieur à toute
  matérialisation.
- **Aucune modification de `session_builder`** avant spec d'abstraction
  `ProgramDefinition` acceptée (V1 n'en requiert pas côté lancement).
- **Pas de concurrence avec les sprints UI/Auren** : aucun fichier template/CSS/
  JS partagé ne sera touché par ce track tant que le cycle UI actif n'est pas
  clos ; les écrans wizard viendront après, sur leurs propres partials.
- **CI complète obligatoire** pour tout build touchant `models/`, `services/`,
  ou quoi que ce soit lié aux sessions ; le garde-fou `check_scope.py`
  s'applique, avec promotion manuelle en `shared_code` au moindre doute.
- Compatibilité agents parallèles : ce document est la source de vérité du
  track ; tout agent travaillant sur une autre branche doit considérer
  `Sx_CUSTOM_PROGRAM` comme **SPEC ONLY, build not authorized**.

## 17. Risques

| # | Risque | Sévérité | Mitigation |
|---|---|---|---|
| R1 | Wipe des programmes user par le seed (si publication sans wipe-guard) | Critique | Contrat §9.1 : wipe-guard livré+testé avant toute matérialisation ; ordonnancement imposé §20 |
| R2 | Fuite des templates custom dans reco/librairie système | Haute | Filtres §9.3 livrés dans le même build que la matérialisation ; tests dédiés |
| R3 | Corruption d'identité historique par édition de programme | Haute | Versions publiées immuables (§15.1) ; nouveau slug par version |
| R4 | Collision de slugs user/système | Moyenne | Namespace réservé par construction (§9.2) |
| R5 | Score A/B/C perçu comme vérité scientifique | Moyenne | Sous-scores d'abord, microcopy « indicatif », régimes de vérité affichés (§12) |
| R6 | EKB incohérente avec les noms historiques (invariance analytique) | Haute | Clé = nom canonique existant ; QA classifiabilité ; aucun renommage |
| R7 | Interférence avec le cycle UI/Auren en cours | Moyenne | §16 : branche dédiée, aucun fichier partagé, merge après stabilisation UI |
| R8 | Scope creep (périodisation, partage, LLM…) | Moyenne | Périmètre V1 fermé (§4) ; toute extension = nouvelle spec |
| R9 | Wizard produisant des programmes irréalistes malgré le scoring | Moyenne | Génération par contraintes bornées (§11) + scoring bloquant en alerte, jamais silencieux |
| R10 | Croissance non bornée de templates matérialisés (versions) | Basse | Archivage systématique des versions remplacées ; quota OQ-CP-F |

## 18. Open questions (à trancher avant build)

| OQ | Question | Position par défaut proposée |
|---|---|---|
| OQ-CP-A | Format du namespace slug custom | `up{user_id}-{slug}-v{n}` |
| OQ-CP-B | Continuité d'historique inter-versions d'un programme (E2 v1 ↔ v2) | Non promise V1 ; étanchéité par version |
| OQ-CP-C | Programmes custom dans le moteur de recommandation | Non en V1 ; OQ rouverte en V2 |
| OQ-CP-D | Stockage EKB : JSON versionné seedé en DB vs JSON à chaud | JSON versionné + seed DB (pipeline existant) |
| OQ-CP-E | Persistance du scoring : à la volée vs persisté | Calcul à la volée + trace persistée par version (`quality_reviews`) |
| OQ-CP-F | Quota de programmes/versions par utilisateur | Quota simple V1 (ex. 10 programmes actifs) |
| OQ-CP-G | Cardio dans le wizard V1 ou différé V2 | Inclus V1 minimal (1 bloc LISS optionnel) |
| OQ-CP-H | Couche suggestions LLM (future) | Hors périmètre track ; nécessiterait sa propre spec ; jamais source de vérité |
| OQ-CP-I | Entrée launcher pour « Mes programmes » | V1 : librairie seulement ; launcher V2 |
| OQ-CP-J | Publication d'un programme grade C | Autorisée avec avertissement explicite (liberté utilisateur) |

## 19. Acceptance criteria

**Pour cette spec (Sx_CUSTOM_PROGRAM_01) :**

- [ ] Human review de la spec (structure 20 sections, options A/B/C comparées,
      recommandation motivée, contrats durs §9, plan de branching §16).
- [ ] OQ-CP-A → OQ-CP-J tranchées ou explicitement différées par l'opérateur.
- [ ] Enregistrement au `SPEC_REGISTRY.md` (track FUTURE, build not authorized)
      et mention courte dans `ROADMAP_AND_NEXT_STEPS.md` — sans perturber le
      cycle UI actif.
- [ ] Aucun fichier `app/`, `tests/`, `data/`, aucune migration, aucun seed,
      aucun template/CSS/JS touché (vérifiable au diff).

**Gates pour la suite (aucun n'est franchi par cette spec) :**

- [ ] Specs filles `Sx_CUSTOM_PROGRAM_02` → `05` rédigées et acceptées.
- [ ] Override opérateur explicite pour ouvrir le build (`Sb_CUSTOM_PROGRAM_01`).
- [ ] Wipe-guard seed livré, testé et accepté **avant** toute matérialisation.
- [ ] Chaque build : migration additive-only isolée, CI 3/3, human review.

## 20. Build queue proposée (aucune n'est ouverte par cette spec)

**Spec queue :**

| Spec | Objet |
|---|---|
| `Sx_CUSTOM_PROGRAM_01` | Intelligent Program Builder Spec (ce document) |
| `Sx_CUSTOM_PROGRAM_02` | Exercise Knowledge Base Spec (modèle EKB, variantes, sources, QA) |
| `Sx_CUSTOM_PROGRAM_03` | Program Quality Scoring Spec (sous-scores, agrégation, microcopy) |
| `Sx_CUSTOM_PROGRAM_04` | User Program Persistence Spec (tables, statuts, versions, quotas) |
| `Sx_CUSTOM_PROGRAM_05` | Session Instantiation Compatibility Spec (matérialisation, wipe-guard, filtres, slugs) |

**Build queue future (chacun : branche dédiée, review-gated, CI complète) :**

| Build | Objet | Dépendances |
|---|---|---|
| `Sb_CUSTOM_PROGRAM_01` | User program persistence + draft CRUD (tables `UserProgram*`, migrations additive-only isolées) | Sx_04 accepté |
| `Sb_CUSTOM_PROGRAM_02` | Exercise catalog normalization (EKB consolidée + QA) | Sx_02 accepté |
| `Sb_CUSTOM_PROGRAM_03` | Wizard UX skeleton (SSR, no-JS, écrans 1-5, brouillons) | 01 |
| `Sb_CUSTOM_PROGRAM_04` | Deterministic generation engine (`ProgramDefinition`, moteur pur + tests) | 02 |
| `Sb_CUSTOM_PROGRAM_05` | A/B/C scoring engine (moteur pur versionné + tests) | 02, Sx_03 accepté |
| `Sb_CUSTOM_PROGRAM_06` | Launch custom program as session (**wipe-guard seed d'abord**, matérialisation, filtres reco/librairie, namespace slug) | 01-05, Sx_05 accepté |
| `Sb_CUSTOM_PROGRAM_07` | Analytics/history/overload alignment (vérification bout-en-bout, dogfood template) | 06 |

---

*Spec draft — build, migrations et code applicatif explicitement non autorisés.
Prochaine décision : human review de ce document.*
