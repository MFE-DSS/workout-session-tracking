# SPRINT Sx_RECOVERY_READINESS_01 — Contrat sémantique readiness / récupération (RAPPORT)

**Base canonique :** `879d41d` · **Branche :** `spec/sx-recovery-readiness-01` · **Tier :**
**DOCS** (`check_scope`) — `check_spec_protocol` seul requis en local, conformément à `CLAUDE.md §1`
et au contrat CI conscient du périmètre (`Sb_CI_02_1`).
**Autorité primaire :** `Sx_AUREN_ORCHESTRATOR_01_GAP_CONSOLIDATION_SPEC.md` (§C.0, §C.2, §D, §E, §G).
**SPEC ONLY — 0 code runtime, 0 migration, 0 modèle, 0 flag, 0 déploiement.**

## 1. Brainstorming / Options / Risques / Choix retenu (`CLAUDE.md §3`)

### Ce que l'audit du code actif a réellement trouvé

L'audit a porté sur le **code vivant** au SHA `879d41d`, pas sur les anciens rapports :
`readiness.py`, `behavioral.py`, `recommendation.py`, `recommendation_explainer.py`, `dashboard.py`,
`home.py`, `session_review.py`, `weekly_loop.py`, les modèles `session`/`readiness`, et les
surfaces d'accueil. **17 signaux vivants** sont inventoriés dans la matrice §1.1 de la spec.

Six constats structurent tout le reste. Deux étaient annoncés par la roadmap canonique ; **quatre
sont des découvertes de cet audit** :

1. **Deux « readiness » qui ne se rencontrent jamais.** `ReadinessEntry` (déclaratif, 1–5,
   **persisté**, un questionnaire quotidien) et `behavioral.readiness_score` (calculé, 0–100,
   dérivé de la charge) portent le même mot. **Le questionnaire n'alimente aucune décision
   d'entraînement** : il ne sort pas du tableau de bord et de sa page d'historique. Quelqu'un qui
   déclare « épuisé » ce matin reçoit exactement la même recommandation que s'il avait déclaré
   « très frais ». C'est, produit, le constat le plus lourd de l'audit.

2. **Le mot « fatigue » change de direction selon l'endroit.**
   `ReadinessEntry.fatigue_level = 5` veut dire **« Très frais »** ; `behavioral.fatigue_score = 80`
   veut dire **« fatigué »**. Même mot, **directions opposées**, aucune conversion nommée entre les
   deux. C'est la même classe de défaut que `Sb_FATIGUE_SCALE_FIX_01`, sur un autre couple de
   champs.

3. **« Availability » désigne quatre choses.** Aptitude biologique par zone
   (`availability_by_zone`), familles d'équipement (`available_equipment`), **affichabilité d'un
   bloc d'UI** (`{"available": bool}` dans `home`, `session_review`, `weekly_loop`), et —
   inexistante en code — disponibilité d'agenda. Les trois premières coexistent aujourd'hui.

4. **Deux *fail-open* structurels subsistent.** Une zone **jamais entraînée** obtient
   `availability = 1.0` : l'absence de donnée est rendue comme la meilleure donnée possible. Et
   `Signals.fatigue_score = 0.0` sur exception est **toujours produit** — `Sb_FATIGUE_SCALE_FIX_01`
   en a neutralisé la *lecture* côté explainer, mais le producteur ment encore à tout futur
   consommateur qui ne passerait pas par `normalize_fatigue_score`.

5. **Le cardio est une île.** Quatre colonnes persistées, **zéro** contribution à la fatigue, à la
   readiness ou à la disponibilité.

6. **`RECOVERY_HOURS_TARGET` est un 4ᵉ exemplaire du dictionnaire des 11 zones**, et `BodyZone`
   n'a aucune colonne capable de le porter — il vit dans le fichier **non modifiable**.

### Options de conception

| # | Option | Verdict |
|---|---|---|
| A | Un `RecoveryScore` unique 0–1 | **Rejetée.** C'est exactement le piège que la mission interdit (« le but n'est pas de créer un score de plus »). Un scalaire unique masque *pourquoi*, et redevient le 7ᵉ chiffre incohérent. |
| B | Corriger chaque signal sur place | **Rejetée.** La moitié vit dans `recommendation.py`, non modifiable ; et corriger sans contrat commun reproduit la fragmentation. |
| C | Étendre `behavioral.py` en service central | **Rejetée.** Interdit par la mission, et `behavioral` ne connaît ni les zones, ni le cardio, ni le déclaratif. |
| D | **Contrat séparé, en lecture seule, exposant des primitives** | **Retenue.** |

### Trois décisions de conception qui méritent d'être justifiées

**`TrainingState` n'expose délibérément aucun score global.** C'est une contrainte, pas un oubli :
un champ `overall_score` deviendrait « le » chiffre affiché, et six mois plus tard personne ne
saurait plus ce qu'il agrège. Un consommateur qui veut un scalaire le dérive lui-même et **assume
sa formule**.

**La direction de la fatigue reste « plus haut = plus fatigué », et son complément est un champ
nommé** (`as_availability = 1.0 − overall`). L'alternative — tout exprimer en disponibilité —
aurait été plus homogène, mais aurait imposé une inversion silencieuse à la frontière, précisément
ce que le constat 2 punit.

**Le champ `fatigue_level` du questionnaire est renommé `self_reported_freshness` à la frontière**,
parce que `5 = « Très frais »`. Garder le nom d'origine sur un axe « plus haut = mieux »
perpétuerait l'inversion. La **colonne persistée n'est pas renommée** — aucune migration : le
renommage vit dans l'adaptateur.

### Risques et traitement

| Risque | Traitement dans la spec |
|---|---|
| Fabriquer de la précision physiologique à partir du cardio | Plafond de confiance **`medium`**, jamais `high` (§5.2) ; table de distribution par zone **déclarée heuristique** ; vocabulaire interdit testé (§8.4) |
| Créer une 5ᵉ taxonomie de zones | Interdit explicite (§6) : attribution via le contrat `Sb_32.4`, projection macro via `radar_axis_for_zone` de P0.1, **aucune recopie** |
| Une tranche future exige `recommendation.py` | Frontière posée (§7) : lire est autorisé, modifier est un **HARD STOP** avec arbitrage séparé |
| Réintroduire un fail-open | §4 rend l'interdit normatif et **nomme les deux cas vivants** à corriger |
| Réimplémenter `normalize_fatigue_score` | §3.1 impose la **réutilisation** ; la DoD de la tranche 1 exige un test qui échoue en cas de duplication |
| Figer une pondération sans base | Les pondérations ne sont **pas** décidées ici — OQ-3 et OQ-4 remontent à l'opérateur |

## 2. Ce qui est livré

`docs/strategy/Sx_RECOVERY_READINESS_01_SPEC.md` — 14 sections :

- **§1** inventaire de **17 signaux vivants** + matrice de source de vérité (producteur · sémantique
  · échelle · direction · persistance · fenêtre · données manquantes · consommateurs · décide ou
  affiche) + les 6 constats + **ce qui est déjà bien fait** (`compute_recovery_axis` et
  `normalize_fatigue_score` servent de modèles) ;
- **§2** les 5 concepts : `ReadinessSignal`, `FatigueSignal` (à **3 composantes séparées**),
  `ZoneRecoveryEstimate`, `AvailabilitySignal` (**4 sens désambiguïsés**), `TrainingState` ;
- **§3** règle 0.0–1.0 + **table de conversion de 13 échelles héritées**, chaque conversion
  **nommée normativement** ;
- **§4** politique *fail-closed* : `sufficient` / `partial` / `insufficient` / `stale`, interdits
  explicites, et les 3 conditions d'un neutre acceptable ;
- **§5** cardio V1 **sur les données réellement capturées** (4 colonnes nullable, texte libre) ;
- **§6** intégration BodyZone sans nouvelle taxonomie ;
- **§7** frontière `recommendation.py` ;
- **§8** garde-fous de formulation, **avec test de wording exigé** ;
- **§9** diagramme d'architecture + graphe de dépendances ;
- **§10** migration/dépréciation des signaux hérités, **divergences attendues à pinner** ;
- **§11** file de build de **5 tranches**, chacune avec dépendances, risques et DoD ;
- **§12** **7 questions ouvertes** exigeant une décision opérateur ;
- **§13** DoD de la spec · **§14** non-goals.

### Écart assumé vs la décomposition suggérée

La mission proposait 5 tranches et autorisait de les renommer « si l'audit prouve une meilleure
frontière ». **Les 5 noms sont conservés à l'identique** — l'audit n'a pas produit de meilleure
frontière. Deux précisions ont toutefois été ajoutées, et elles sont justifiées :

- **`Sb_CARDIO_FATIGUE_ADAPTER_01` doit commencer par un audit des valeurs réelles de
  `cardio_machine_type`.** C'est un `String(32)` en **texte libre** : le vocabulaire réellement
  présent en base est inconnu et probablement sale. Construire une table de distribution par zone
  sur un vocabulaire supposé serait exactement le genre d'invention que la mission interdit.
- **`Sb_ZONE_RECOVERY_ESTIMATE_01` doit pinner sa divergence** avec `availability_by_zone` sur les
  zones jamais entraînées (`None` vs `1.0`). C'est la méthode qui a fonctionné en `Sb_32.4` : une
  divergence connue et testée plutôt qu'une surprise.

## 3. Vérifications locales

`check_scope` : **DOCS** — `check_spec_protocol` est le **seul** contrôle local requis, et le reste
est explicitement skippable à ce tier. Aucun pytest local n'a été lancé : ce serait de l'overcheck
au sens de `CLAUDE.md §1`, et le diff ne peut pas atteindre le runtime.

| Contrôle | Résultat |
|---|---|
| `check_scope` | **DOCS** |
| `check_spec_protocol` | **PASS** (section Non-goals présente) |
| Fichiers touchés | **100 % `docs/**`** |

## 4. Interdits tenus

**Non-goals de la mission, tous tenus** : 0 code runtime · `recommendation.py` non modifié ·
`behavioral.py` non modifié · 0 migration · 0 modèle / table · Body Intelligence non activée ·
0 flag de production · accueil non refondu · aucun planificateur ni replanification construits ·
aucun wearable · moteur morpho, substitution et overload intacts · aucun profil de salle ·
aucun déploiement · **aucun score global unique créé** · **aucune tranche ouverte**.

**Interdits du contrat de livraison** : pas de force-push, pas de rebase, pas de squash, pas de
merge `--admin`, `AGENTS.md` non touché.

## Verdict

**Livré.** Le contrat sémantique existe : quatre mots qui désignaient chacun plusieurs choses
— readiness, fatigue, récupération, disponibilité — ont maintenant une définition unique, une
échelle, une direction et une politique de données manquantes. Les 17 signaux vivants sont
inventoriés avec leur producteur et leurs consommateurs réels, et les **13 conversions d'échelle**
nécessaires sont nommées avant d'être écrites.

Le résultat n'est **pas un score de plus** : `TrainingState` expose des primitives et refuse
délibérément d'agréger un chiffre unique.

Trois défauts vivants sont documentés avec leur correction prévue : le questionnaire de readiness
qui n'influence aucune décision, la zone jamais entraînée rendue « parfaitement disponible », et le
cardio sans effet sur quoi que ce soit.

**Sept questions ouvertes** remontent à l'opérateur — mais **aucune ne bloque la première
tranche**, faite de types et de conversions.

## Closeout — ✅ MERGED

**PR #78 MERGÉE.** Base canonique `879d41d` → build `25e2997` → **merge `7369141`** via
`--merge --match-head-commit 25e2997…` — **sans squash, sans `--admin`, sans force**. Gate
re-vérifié **autoritativement juste avant** le merge : head SHA confirmé, `CLEAN` / `MERGEABLE`,
**5/5 checks** (dont le gate **externe** `SonarCloud Code Analysis`), gate Sonar **`OK`**,
**0 thread non résolu**. Aucun finding Gitar.

**Le contrat CI conscient du périmètre a fonctionné comme prévu.** `Sb_CI_02_1` a classé la PR
`NON_RUNTIME` : le job `pytest + QA scripts` a pris **7 secondes** au lieu de ~11 minutes, pendant
que `lint` tournait **intégralement** (53 s) et que le gate externe Sonar restait évalué. C'est
exactement le comportement conçu — les jobs ne disparaissent jamais, seules les étapes coûteuses
sont conditionnelles.

**CI canonique légitimement SKIPPÉE, et c'est consigné.** Le merge est **100 % `docs/**`**, filtré
par le `paths-ignore: ['docs/**']` du trigger `push`. Ce n'est **pas** un `[skip ci]` manuel : c'est
la policy CI versionnée (`CLAUDE.md §2`). Vérifié : `git diff --name-only 879d41d..7369141` ne
renvoie que des chemins sous `docs/`.

**Aucune tranche d'implémentation n'est ouverte.** Les 5 tranches du §11 de la spec attendent
chacune un `GO BUILD` explicite.

**Statut final : `Sx_RECOVERY_READINESS_01_SPEC MERGED + CLOSED + CLEANED`.**
