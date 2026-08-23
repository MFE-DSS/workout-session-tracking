# `TRAIN1-B` — PROGRESSIVE_EXERCISE_COCKPIT (A10)

**Slice opérateur** : TRAIN 1, deuxième des trois — *tranche d'innovation UI majeure*
**Branche** : `sb/train1b-progressive-cockpit` · **base** : `b22098d`
**Tier `check_scope`** : `SHARED_CODE`

---

## 0. Brainstorming / Options / Risques / Choix retenu

*(CLAUDE.md §3)*

### Ce que l'audit préalable avait déplacé

La question n'était pas « quelle règle de comparaison inventer ». **La
primitive existait déjà**, dans `delta.py` :

> « The function NEVER infers a "delta" from partial data. »

Zéro seuil, zéro agrégat, `=` sur une égalité, `None` quand le côté précédent
n'a pas de série complétée. L'exigence opérateur « pas de score global inventé »
était **déjà le contrat écrit du dépôt**. Ce module la réutilise ; il ne la
réécrit pas.

Restaient deux questions **produit**, tranchées par l'opérateur.

### Décision 1 — l'identité franchit le gabarit

Mesuré sur le catalogue canonique, avant d'écrire une ligne :

| | |
|---|---|
| identités héritées `(gabarit, code)` | **106** |
| exercices réels (identité `A1`) | **68** |
| identités fusionnées | **38** |
| exercices vivant dans ≥ 2 gabarits | **28 sur 68** |

`Leg extensions assises` apparaît dans **4 gabarits sous 3 codes différents**
(`E3`, `E4`, `E5`) : même la clé héritée n'était pas stable pour lui, et son
historique était éclaté en quatre sans que rien ne le dise.

**Le gabarit devient une provenance.** Aucun rapprochement approximatif : la
résolution est **exacte après normalisation**, alias canoniques compris. Un nom
libre non résolu reste **explicitement** hors comparaison — il n'est jamais
rattaché au plus ressemblant.

### Décision 2 — le cardio ne rentre pas de force

Le modèle le disait déjà : `cardio_duration_min`, `cardio_bpm_avg`,
`cardio_machine_type` vivent sur `WorkoutSession`, **pas** sur
`SessionExercise`. Ni série, ni charge, ni répétition.

| Champ | Rôle |
|---|---|
| `cardio_duration_min` | **fait primaire** — la seule grandeur comparée |
| `cardio_bpm_avg` | **contexte** — rendu à côté, jamais comparé |
| `cardio_machine_type` | **condition** de comparabilité |
| `cardio_machine_calories` | **jamais** une métrique de progression |

Les calories ne sont pas seulement non affichées : elles ne sont **pas
chargées**. Ne pas les avoir est plus solide qu'une note disant de ne pas s'en
servir.

---

## 1. Ce qui est livré

| Module | Rôle |
|---|---|
| `progression_facts.py` | read-model, identité `A1`, comparaison des deux occurrences les plus récentes |
| `cardio_lane.py` | voie séance, une file par machine |
| `progression_view.py` | vue-modèle **pure** — ni `sqlalchemy` ni `datetime`, garde AST |
| `_partials/progression.html` | la surface |
| `exercise_history.get_exercise_history_by_slug` | drill-down convergé sur l'identité stable |
| route `/exercise-history/{slug}` | l'entrée convergée ; **l'entrée héritée reste servie** |

Rendu, par exercice :

```
Tirage poulie haute prise neutre     60 × 10 → 55 × 12
−5 kg  +2 reps

Chest Press machine                  70 × 10 → 72,5 × 10
+2,5 kg  = reps   2 programmes
```

**Aucune couleur de jugement** — vérifié au `getComputedStyle` : tous les
écarts rendus partagent une seule couleur, `rgb(167, 176, 186)` (`--fg-muted`).
Pas de vert, pas de rouge, pas de flèche montante. Un `−5 kg` est un fait ;
« moins bien » est une appréciation, fausse dès qu'une charge baisse
volontairement.

Le `score_trend` de `Delta` — le seul champ de la primitive qui porte un
jugement (`up`/`down`) — est **délibérément écarté**. Le laisser passer
réintroduirait par la petite porte l'appréciation que le contrat exclut.

---

## 2. Trois défauts trouvés en construisant

### 2.1 — L'instrument dupliquait un bloc existant. **Vu au rendu.**

« Activité récente par exercice » listait les mêmes faits — dernière charge,
dernières reps, par exercice — sur trente jours. Et il était clavé sur
l'identité **héritée** : sur le compte de test, « Chest Press machine » y
apparaissait **deux fois, une par gabarit**. La fragmentation qu'`A1` corrige,
affichée comme deux exercices distincts.

Livrer les deux blocs aurait ajouté une duplication à l'écran même que
`TRAIN1-A` venait d'écrémer. Le bloc est **retiré**, et ce n'est pas une
soustraction seule (§5.3) : le remplacement part dans la même livraison et est
strictement plus riche — mêmes faits, identité entière, écart calculé,
drill-down convergé.

**Effet mesuré** : `plein` passe de **3,4 à 2,7 écrans** et de **533 à
343 mots**.

### 2.2 — La table d'identité n'était pas semée au démarrage

`A1` a branché le peuplement de `exercises` sur `scripts/seed_db`. Le
`lifespan` de l'application, lui, ne semait que le catalogue et les règles de
méthode.

Conséquence : **sur tout déploiement où `seed_db` n'a pas été rejoué depuis A1,
la table est vide**, `resolve_exercise` ne rend jamais rien, et l'instrument
progressif n'affiche aucun exercice — **sans erreur, sans message**. Une
surface qui marche sur le poste du développeur et nulle part ailleurs.

`seed_exercise_identity` rejoint le démarrage. Elle est idempotente, prouvée
sur base réelle (102 puis +0). Une garde vérifie que la table est peuplée.

### 2.3 — Les occurrences non rattachées devenaient invisibles

`build_progression_view` ne rendait la section que s'il y avait des lignes
comparables ou en attente. Un compte dont **toutes** les occurrences portent un
nom non rattachable rendait donc une section absente — et un compte de
non-rattachés **invisible**.

C'est exactement ce que la règle interdit : taire la donnée manquante fait
passer une couverture nulle pour une absence de pratique. Même faute que l'état
`PARTIAL` de l'exposition anatomique ferme.

**Trouvé par un test migré**, pas par relecture.

---

## 3. Exposition visuelle (CLAUDE.md §5.1)

**Douze écrans entiers**, trois comptes × trois largeurs, plus le niveau 2
ouvert. Jamais un recadrage.

| État | écrans | mots | lignes | cible | provenance | non rattachés |
|---|---|---|---|---|---|---|
| `vide` 360/390/430 | 1,1–1,2 | 112 | 0 | — | — | — |
| `plein` 360/390/430 | 2,6–2,7 | 343 | 2 | **44 px** | 1 | oui |
| `plein` ouvert | 3,0–3,1 | 402 | 2 | 44 px | 1 | oui |
| `cardio` 360/390/430 | 2,2–2,3 | 228 | 3 files | **44 px** | — | — |

Vérifié à la mesure du DOM : **aucune mention de calorie**, **aucun
défilement horizontal**, **aucun débordement de ligne**, une **seule couleur**
pour tous les écarts.

**Un défaut vu seulement en regardant** : la provenance affichait les **noms
complets** des deux programmes (« Pull B — Dos épaisseur + Biceps · Push A —
Pecs épaisseur + Delts + Triceps »), qui débordaient sur deux lignes à 390 px
et prenaient plus de place que le fait qu'ils annotent. Remplacée par
« 2 programmes » ; le détail par occurrence vit dans le drill-down, à sa place.

### Cibles sous 44 px

`topbar__brand`, `foot__contact`, lien « Comment c'est calculé → ». **Toutes
préexistantes**, présentes sur chaque page. Les lignes de l'instrument mesurent
exactement 44 px.

---

## 4. Relecture du relevé de décisions (CLAUDE.md §5.2)

| Décision | Verdict |
|---|---|
| §5.1 exposition préalable | **Respectée** — 12 écrans, 1 défaut trouvé à l'œil |
| §5.2 relecture consignée | **Respectée** — ce tableau |
| §5.3 jamais une soustraction seule | **Respectée** — le bloc retiré est remplacé dans la même livraison, par plus riche |
| §5.4 toute couleur est un token | **Respectée** — **aucune couleur neuve** |
| §5.5 centralité avant facilité | **Respectée** — c'est la tranche d'innovation majeure désignée |
| AMBRE = action / BLEU = système | **Respectée** — `--accent` sur la seule affordance, écarts en `--fg-muted` |
| Cible 44 px | **Respectée** — mesurée au DOM, pas supposée |
| SSR, zéro framework | **Respectée** — `<details>`, aucun script |

---

## 5. Vérifications

| Contrôle | Résultat |
|---|---|
| `check_scope` | `SHARED_CODE` |
| ruff | `All checks passed!` |
| pré-scan AST S9073 / S5863 | **0 / 0** |
| `check_ruff_budget` | 282 ≤ 548 |
| `check_spec_protocol` | PASS |
| Gardes dédiées | **30 passed** |
| **Broad sweep** — 31 fichiers, rayons Python **et** contrats CSS | **623 passed** |

Le broad sweep inclut les contrats CSS dès la sélection : c'est la leçon
explicite de `TRAIN1-A`, où un défaut de feuille de style était sorti en CI
parce que la sélection avait été bâtie sur le seul rayon Python.

### Trois tests migrés, aucun affaibli

| Test | Ancien invariant | Nouveau |
|---|---|---|
| `test_progress_activity_rows_link_to_exercise_history` | lien vers `(gabarit, code)` | lien vers l'**identité stable**, + une garde neuve que l'entrée héritée **répond encore** |
| `test_progress_keeps_per_program_and_recent_activity` | « ce bloc existe » | bloc dupliqué **absent** + remplaçant présent |
| — | — | et une garde neuve : la section se rend **même** quand tout est non rattaché |

Une garde de ma propre écriture a été prise en flagrant délit : elle lisait la
**docstring** du module cardio, qui explique que le cardio ne vit pas dans
`SessionExercise`. Huitième occurrence de ce motif dans ce dépôt. Réécrite pour
lire l'**AST**, donc le code.

---

## 6. Non-régressions

- **0 score, 0 seuil, 0 agrégat de « progrès »** — gardes textuelles et AST.
- **0 rapprochement approximatif** — correspondance exacte après normalisation.
- **0 nouvelle métrique cardio** ; les calories ne sont **pas chargées**.
- **0 route cassée** — l'entrée héritée `(gabarit, code)` répond encore ; une
  garde le vérifie.
- **0 moteur de décision touché** — garde sur `recommendation`,
  `substitution`, `behavioral`.
- **0 migration, 0 modèle, 0 couleur neuve, 0 script.**
- La règle de comparaison est **partagée** entre les deux drill-downs, pas
  recopiée : deux surfaces qui compareraient des points différents se
  contrediraient.

---

## 7. Constaté, hors périmètre

- **« Par programme » rend une carte pleine pour dire « Aucune session
  terminée »** sur un compte vide — relève de **TRAIN 1-C**.
- **Deux `—` dans « Rythme récent »** sur un compte sans `SetLog` : exact
  (rien à diviser), mais demanderait une décision produit sur ce que rend un
  KPI sans dénominateur.
- **`KEEP_OCCURRENCES = 6` et `TOP_N = 5`** sont des bornes d'affichage, pas
  des seuils de jugement. Elles limitent ce qui est **rendu**, jamais ce qui
  est **comparé**.
