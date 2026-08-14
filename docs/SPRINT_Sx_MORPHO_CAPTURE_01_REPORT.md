# SPRINT Sx_MORPHO_CAPTURE_01 — Contrat de capture morphologique (RAPPORT)

**Base canonique :** `62ff4bd` · **Branche :** `spec/sx-morpho-capture-01` · **Tier :**
**DOCS** (`check_scope`) — diff 100 % `docs/`. **Aucun sweep de tests** : la CI consciente du
périmètre a classé la PR `NON_RUNTIME` et le job pytest a rendu son verdict en **9 secondes**.
**SPEC ONLY** — 0 code runtime · 0 migration · 0 modèle · 0 colonne · 0 déploiement.
**Tranche 1/3 du train `AUREN_MORPHO_RUNTIME_01`** ; **tranches 2 et 3 non ouvertes**.

## 1. Pourquoi cette tranche a pu être livrée alors que le train était bloqué

Le train `AUREN_MORPHO_RUNTIME_01` démarre nominalement après
`AUREN_CORE_ORCHESTRATION_01`, lui-même bloqué par le plafond mémoire de la CI. Ses tranches
2 et 3 dépendent effectivement d'un planificateur qui n'existe pas.

**La tranche 1 n'en dépend pas.** C'est un audit de code **déjà présent** au SHA canonique, et
son livrable est un document. Deux conséquences : elle ne nécessite aucune donnée issue des
sprints en attente, et — étant 100 % `docs/` — elle **ne traverse pas** le sweep de tests dont
la mémoire est saturée. Elle a donc été livrée pendant que la décision de capacité reste en
suspens, plutôt que d'attendre derrière elle.

## 2. Ce que l'audit a trouvé

Le moteur de morphologie est **livré et pur** ; personne ne l'alimente. Le blocage n'était pas
le câblage.

**(a) `wingspan_cm` n'a aucune colonne persistée.** Le moteur dérive l'ape index de
`wingspan − height`. Sans envergure stockée, **une branche entière du moteur est
inatteignable** sur n'importe quel compte réel.

**(b) Deux écrivains concurrents sur `body_measurements`, avec deux théories du temps.**
`auth_routes.profile_measurements_submit` fait un **upsert par date** ;
`body_profile.create_measurement` fait une **insertion systématique**. Même table, sémantiques
incompatibles, jamais arbitrées.

**(c) `shoulder_width_cm` est capturé, borné (30–60 cm), et lu par personne** — alors que
`OBSERVATION_VOCAB` attend un `clavicular_width` qualitatif.

## 3. Décisions

| Question | Décision |
|---|---|
| Écrivain canonique | **`create_measurement`** — il porte déjà la validation bornée, la liste blanche et le garde-fou de formulation non médical. La route délègue. |
| Temporalité | **Append-only**, de façon **prospective**. Les lignes upsertées existantes restent valides, **non migrées**. |
| `wingspan_cm` | **Colonne requise** — additive, nullable, **zéro backfill**. |
| `ape_index_cm` | **Dérivé, jamais stocké** : c'est une soustraction de deux faits, pas un fait. |
| Latéralité | Convention d'agrégation **nommée et versionnée** (moyenne, sinon le côté disponible), exposée dans le `basis`, étiquetée **convention comptable** et non vérité physiologique. |
| Asymétrie G/D | Conservée en base, **exclue** de `MorphologyFacts` — l'interpréter est un diagnostic postural. |
| `calf_cm` hérité | **Lu par précédence, jamais écrit**, ni fusionné ni supprimé. |
| `shoulder_width_cm` | **Question ouverte, non tranchée** — le seuil n'a aucune source dans le dépôt. |

L'envergure est mesurable au mètre ruban : elle entre dans le périmètre « faits directement
capturés », contrairement à une longueur osseuse. L'estimer depuis la taille fabriquerait
précisément l'ape index qu'on cherche à mesurer — d'où l'interdiction de backfill.

## 4. Garde-fous étendus à la capture

Les cinq interdits — photo · longueur osseuse inférée · inférence de masse grasse · diagnostic
postural · inférence d'insertion — existaient déjà dans le moteur via
`GUARDED_NOT_DEDUCTIBLE`. La spec les étend à la **surface de saisie** : ce qui n'est pas
déductible ne doit pas non plus être **demandé** sous une forme suggérant qu'il le deviendrait.

## 5. La limite énoncée, pas dissimulée

Aucune surface ne capture les `observations`, et la spec **n'en ouvre pas** : demander à un
utilisateur de qualifier ses propres « quadriceps relativement forts » transformerait une
déclaration en observation.

Conséquence directe : le runtime produira des descripteurs à **confiance structurellement
réduite**. C'est le comportement correct — mais il faut le savoir **avant** de brancher un
planificateur dessus, pas après.

## 6. Ce que la spec exige du runtime

Huit critères d'acceptation, dont : un seul écrivain canonique · envergure additive sans
backfill · convention latérale présente dans le `basis` · un fait manquant qui **réduit la
confiance** au lieu d'être comblé · et **priorité déclarée ≠ candidat morphologique**, les deux
sources restant distinguables conformément à `Sb_TRAINING_PREFERENCES_01`.

Quatre questions ouvertes consignées ; aucune ne bloque le runtime.

## Verdict

**Spec livrée et mergée. Runtime non ouvert.**

Valeur réelle de la tranche : elle a converti un blocage vague (« le moteur morpho n'est pas
branché ») en deux obstacles nommés et chiffrables — une colonne manquante et un conflit
d'écrivains — qui se règlent tous deux par une migration additive et une délégation, sans
toucher au moteur ni à une seule donnée historique.

**Limite assumée** : le document décide, il ne prouve rien à l'exécution. Les huit critères
du §8 de la spec sont ce qui transformera ces décisions en garanties, et ils appartiennent à
`Sb_MORPHO_PROFILE_RUNTIME_01`.

---

## 7. Closeout post-merge

| | |
|---|---|
| PR | **#88** — `MERGED` |
| Build | `b88d735` |
| Merge | **`efef5a2`** (`--merge --match-head-commit b88d735`, **sans squash / `--admin` / force**) |
| Gate PR | `CLEAN` · **6/6** dont le gate externe `SonarCloud Code Analysis` |
| Gitar | **0 finding** · **0 thread non résolu** |
| pytest | **9 s** — classé `NON_RUNTIME` par la CI consciente du périmètre |

**CI canonique légitimement SKIPPÉE et consignée.** Le merge est **100 % `docs/`** (vérifié :
`git diff --name-only 62ff4bd..efef5a2` ⇒ un seul fichier, zéro hors `docs/`), donc filtré par
le `paths-ignore` du trigger `push`. Ce n'est **pas** un `[skip ci]` manuel mais la policy
versionnée (`CLAUDE.md §2`) ; la **CI de PR fait foi**.

**Contrat mémoire du train respecté** : une spec docs-only ne doit pas consommer un sweep
complet. Elle n'en a consommé aucun.

**Nouvelle base canonique : `efef5a2`.**
