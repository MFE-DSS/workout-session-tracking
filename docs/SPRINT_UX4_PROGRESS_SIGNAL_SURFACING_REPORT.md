# `UX4_03` — rendre perceptible ce qui est déjà calculé

**Statut : `UX4_03B` construit et exposé, NON COMMITÉ.** En attente du verdict
opérateur sur le rendu (`CLAUDE.md §5.1`).

Ce rapport remplace celui de `UX4_03`, dont le rendu a été refusé.

---

## 1. Pourquoi une seconde version

`UX4_03` a livré trois signaux réels, sur la bonne surface, avec CI verte et
17 gardes. **L'opérateur a refusé le rendu au premier coup d'œil.**

Le défaut n'était pas graphique. Les trois valeurs **habillaient une donnée
absente en mesure** :

| Rendu refusé | Ce que la valeur était réellement |
|---|---|
| `Charge ressentie 45/100` + jauge à 45 % | **45,0 est le défaut** de `compute_session_fatigue(None, None)` |
| `Régularité 0/100` + jauge | le `/100` pose **une séance par jour** comme la cible : 3 séances → `21/100` |
| `Continuité stable` | `compute_trend(0, 0)` rend `"stable"` — à qui n'a **jamais** rien enregistré |

Les trois sont **mesurés**, pas déduits (`docs/UX4_03A_BEHAVIORAL_SIGNAL_SEMANTICS.md`).

### Le dépôt avait déjà écrit la règle

`recovery_contract.py:196-199`, antérieur à cette tranche :

> Both inputs ``None`` → ``None``: ``compute_session_fatigue`` would happily
> return its 50/40 defaults, but **"the user told us nothing" is not a
> measurement and must not be dressed up as a neutral reading.**

Et `FatigueSignal` (`:796-807`) refuse l'agrégat scalaire par construction :
« there is deliberately **no aggregate** […] coefficients no evidence in this
repository supports ». Le `45/100` était exactement ce scalaire.

**La tranche n'a rien inventé : elle a appliqué un contrat déjà versionné que
la première version contournait.**

---

## 2. Ce que `UX4_03B` rend

| Signal | Connu | Inconnu |
|---|---|---|
| **Ressenti général** | `Moyen` · déclaré en fin de séance | `inconnu` · aucun ressenti déclaré |
| **Séances** | `5` · 14 derniers jours | `aucune` · 14 derniers jours |
| **Cadence 7 j** | `3 → 2` · 7 jours précédents, puis les 7 derniers | `—` · aucune séance sur 14 jours |

Plus une divulgation **unique et repliée** — « Comment AUREN calcule ces
signaux » — à la place des trois notes par signal.

### 2.1 — Pourquoi la valeur n'est pas rebinnée

`global_state` **naît catégoriel** : trois boutons. `compute_session_fatigue`
le convertit en 80/50/20, moyenne trois séances, et un affichage en bandes le
rebinnerait en trois mots. Cet aller-retour perd l'information et **en invente
une autre** : une précision décimale que la saisie n'a jamais eue.

Le dépôt fournit pourtant tout le nécessaire pour bander —
`band_for_estimate()` avec ses seuils déjà nommés « *presentation thresholds,
not physiology* », et une phrase française par bande dans `recovery_explainer`.
**Ils n'ont pas été utilisés**, et c'est délibéré : la présentation honnête
d'une catégorie est la catégorie.

Les libellés viennent du formulaire que l'utilisateur a rempli
(`session_detail.html:133`) — `En forme` · `Moyen` · `Fatigué`. **Zéro copie
nouvelle, zéro seuil inventé.**

### 2.2 — Pourquoi « Ressenti général » et pas « Charge perçue »

*(correction opérateur du 2026-08-21)*

Le formulaire demande, mot pour mot :

```
Énergie générale
Comment te sentais-tu pendant la séance ?
En forme · Moyen · Fatigué
```

C'est une question sur le **ressenti**, pas sur l'effort. « Charge perçue » est
le vocabulaire du **RPE**, une échelle d'effort perçu que ce dépôt ne collecte
nulle part. L'employer ferait passer une question d'humeur pour une mesure
d'intensité — et **rendrait le terme indisponible** le jour où AUREN mesurera
réellement l'effort perçu.

### 2.3 — Pourquoi la déclaration porte sa date

Remonter jusqu'à la dernière déclaration **réelle** est le bon comportement :
se taire parce que la séance la plus récente a été terminée sans répondre
perdrait une information vraie.

Mais rendre une déclaration de trois jours comme si elle datait de la dernière
séance **fabriquerait une fraîcheur** — le défaut du 45,0 déplacé du contenu
vers le temps. D'où `dernière déclaration · 18/08`, **et seulement dans ce
cas** : dater ce qui vient de la dernière séance ajouterait du bruit sans rien
apprendre. La date signale un **écart**, pas une provenance.

### 2.4 — La correction est structurelle, pas typographique

Le routeur ne passe plus `behavioral` : il passe `signals`, une vue-modèle
pure. Le gabarit **ne peut plus lire** `fatigue_score`, `consistency_score` ni
`trend_direction`.

Vérifié en replantant `{{ behavioral.fatigue_score }}` : Jinja tourne en
`StrictUndefined`, la page **plante** au lieu de rendre du vide. Corriger les
seuls libellés aurait laissé les trois champs à portée du gabarit.

### 2.5 — Pourquoi les faits vivent hors du moteur

**Première version : cinq champs additifs dans `BehavioralState`.** C'était
tentant — le moteur calcule déjà ces comptages, puis les **jette** pour ne
garder que les scores qui en dérivent.

`test_no_decision_engine_was_touched` a rougi. Depuis `e8614bd`, trois moteurs
sont **gelés** — `substitution`, `recommendation`, `behavioral` — au nom d'un
invariant : **la présentation ne décide de rien.** `UX4_03B` est une tranche de
présentation ; faire grossir un moteur gelé pour qu'une surface soit servie
inverse exactement la dépendance que ce gel protège.

L'argument « ce n'est qu'additif » est **celui que la garde existe pour
refuser** : un champ additif aujourd'hui est une lecture couplée demain.

Vérifié avant de conclure : `git diff e8614bd` est **vide** sur les trois
fichiers de la canonique. Le gel était intact ; l'échec ne venait que de moi.

D'où `app/services/progress_facts.py` — un producteur de faits qui ne connaît
aucun moteur. `behavioral.py` est de nouveau **identique à la version gelée**,
au caractère près.

La chaîne est donc :

```
DB → progress_facts (requêtes)  →  progress_signals (pur)  →  gabarit
```

La séparation n'est pas cosmétique : `progress_signals` n'importe ni
`sqlalchemy` ni `datetime`, ce qu'une garde AST vérifie. C'est ce qui permet de
tester chaque état de rendu — connu, inconnu, déclaration périmée — sans base
ni serveur.

---

## 3. Mesure au navigateur — deux états, trois largeurs

|  | inconnu 360 | 390 | 430 | connu 360 | 390 | 430 |
|---|---:|---:|---:|---:|---:|---:|
| écrans de défilement | 2,7 | 2,5 | 2,2 | 2,8 | 2,6 | 2,3 |
| mots visibles | 197 | 197 | 197 | 221 | 221 | 221 |
| **textes rognés** | 0 | 0 | 0 | 0 | 0 | 0 |
| **jauges proportionnelles** | 0 | 0 | 0 | 0 | 0 | 0 |
| **valeurs « /100 »** | 0 | 0 | 0 | 0 | 0 | 0 |
| notes par signal | 0 | 0 | 0 | 0 | 0 | 0 |
| scripts requis | 0 | 0 | 0 | 0 | 0 | 0 |
| **contrôle de divulgation** | 358×50 | 358×50 | 398×50 | 328×50 | 358×50 | 398×50 |

**Coût en mots : +31** sur la ligne de base (166 → 197 en état inconnu), contre
**+79** pour `UX4_03`. La divulgation étant repliée, son texte ne compte pas
dans les mots visibles — c'est le principe d'un niveau 2, et le dire vaut mieux
que laisser croire à une gratuité.

### 3.1 — Trois choses que la mesure a corrigées, et que le HTML ne pouvait pas donner

- **La fixture « riche » ne prouvait rien.** Elle remplit une séance *en
  cours* ; `compute_behavioral_state` ne compte que les séances *terminées*.
  Mesuré : elle rendait des signaux **identiques** au compte vide. Une seconde
  fixture (`seed_declared.py`) pose l'état connu. Sans elle, la mesure aurait
  affirmé que le signal fonctionne sans jamais l'avoir vu fonctionner.
- **La divulgation mesurait 26 px de haut.** Conforme au seuil WCAG 2.2 AA
  (24 px), **sous** le standard produit AUREN de 44 px. Portée à **50 px** par
  le **rembourrage** — la taxonomie `B8` a établi que « zone tactile ≥ 44 » et
  « chrome visible ≥ 44 » sont deux choses distinctes.
- **Le fichier SQLite ne se remplace pas sous un serveur vivant.** Réinitialiser
  la fixture entre deux passes invalide le pool et refuse toutes les connexions
  suivantes. Une passe = une base neuve + un serveur neuf.

---

## 4. Gardes — 33, dont 10 défauts replantés

| Défaut replanté | Garde | Verdict |
|---|---|---|
| `UNKNOWN_VALUE` remis à `45/100` | `..._undeclared_feeling_reads_as_unknown...` | rougit |
| `NO_CADENCE_VALUE` remis à `stable` | `..._never_having_trained_is_not_a_stable_rhythm` | rougit |
| `« Moyen »` renommé `« Modéré »` | `..._declared_labels_match_the_form...` | rougit |
| `/100` réintroduit | `..._no_score_out_of_one_hundred_survives...` | rougit |
| jauge et `behavioral.` remis au gabarit | `..._template_cannot_read_the_rejected_scores` | rougit |
| `.signal__fill` revenu dans la feuille | `..._gauge_styles_are_gone_from_the_sheet` | rougit |
| `« Charge perçue »` restauré | `..._not_named_after_perceived_exertion` | rougit |
| fraîcheur ignorée | `..._older_declaration_carries_its_date` | rougit |
| import d'un moteur gelé | `..._surface_does_not_grow_a_frozen_decision_engine` | rougit |
| comptage de demi-fenêtre faux | `..._facts_are_counted_against_a_real_database` | rougit |

### 4.1 — Deux gardes m'ont arrêté, les deux avaient raison

**La mienne** traquait la sous-chaîne `"session"` pour vérifier qu'aucun calcul
n'avait été écrit — et rougissait sur `_sessions`. **Septième occurrence** dans
ce dépôt d'une garde qui traque un fragment plutôt qu'un nom. Remplacée par une
garde AST : imports interdits (`sqlalchemy`, `app.models`, `datetime`) et
**aucun `ast.BinOp`**.

**Celle du dépôt**, `test_recommendation_and_behavioral_are_not_modified`,
interdit la chaîne `training_state` dans `behavioral.py`, **prose comprise**,
pour protéger le **sens de la dépendance**. Mon commentaire nommait le module.
La garde est plus stricte que nécessaire pour un commentaire, et elle a raison :
nommer un module en prose est le premier pas vers l'importer.

> **La copie a changé, pas la garde.** Deuxième fois dans cette tranche.

### 4.2 — Deux défauts que seul le sweep complet pouvait trouver

Le tier `SHARED_CODE` n'exige **pas** le full sweep local. Il a été lancé
quand même, sur demande d'exhaustivité — et il a rapporté **deux** choses que
523 tests ciblés avaient manquées :

1. **`test_no_decision_engine_was_touched`** — le gel des moteurs (§2.5). Aucun
   test du rayon d'impact de `behavioral` ne le portait : la garde vit dans
   `test_ui_session_choices.py`, un fichier qu'aucune heuristique de proximité
   n'aurait désigné.
2. **Un `TypeError` naïf/aware.** Après relocalisation, `progress_facts`
   chargeait les dates de la fenêtre et dérivait la demi-fenêtre **en Python**.
   SQLite rend des datetimes **naïfs** même pour une colonne déclarée
   `DateTime(timezone=True)` : `naïf >= aware` lève.

   Les tests de la vue-modèle **ne pouvaient pas le voir** — ils construisent
   des `ProgressFacts` à la main et ne touchent jamais la base. Le moteur
   comparait déjà en SQL ; ce n'était pas un détail d'écriture.

Les deux ont reçu une garde locale, pour ne plus dépendre d'un sweep de
31 minutes : `..._surface_does_not_grow_a_frozen_decision_engine` et
`..._facts_are_counted_against_a_real_database` — cette dernière vérifie des
**valeurs**, pas seulement l'absence d'exception, sinon elle ne garderait que
contre le crash.

### 4.3 — Une garde qui s'annonce comme un proxy

`..._disclosure_control_is_not_sized_below_the_product_standard` lit un token
CSS, **pas une hauteur rendue**. `Progress` est `TRANSITIONAL`, donc sans gate
pixel en CI : aucune garde mécanique ne peut mesurer ce pixel ici. La preuve
est la mesure navigateur du §3, et la garde le dit dans sa propre docstring
plutôt que de se faire passer pour ce qu'elle n'est pas.

---

## 5. Relecture du relevé de décisions (`CLAUDE.md §5.2`)

| Décision | Verdict |
|---|---|
| §5.1 — exposition visuelle avant commit | **respectée** — rendu publié, commit en attente |
| §5.2 — relecture consignée | **respectée** — ce tableau |
| §5.3 — jamais une soustraction seule | **respectée** — les trois `/100` et les trois jauges partent avec les valeurs qui les remplacent ; « un jour de repos ne casse rien » survit dans la divulgation |
| §5.4 — toute couleur est un token mesuré | **non concernée** — aucune couleur nouvelle ; `--fg-dim` et `--border` préexistent |
| §5.5 — la centralité avant la facilité | **respectée** — le défaut sémantique passe avant le polish, et les quatre consommateurs faciles sont enregistrés plutôt que traités |
| `Sx_UIV3_01` — pas de barre proportionnelle | **respectée** — c'est la correction centrale |
| `Sx_UIV3_00 §7` — aucun état par la couleur seule | **respectée** — l'inconnu change de graisse et de style, et porte un libellé |
| Cible tactile 44 (standard produit) | **respectée** — 50 px mesurés, portés par le rembourrage |
| `DO_NOT_SURFACE` sur le streak | **respectée sur cette surface**, violée ailleurs → `B2`, `B3` |

---

## 6. Périmètre — ce qui n'est PAS dans ce patch

Enregistré sous **`UX4_03B_BEHAVIORAL_CONSUMER_ALIGNMENT`**
(`docs/UX4_03A_BEHAVIORAL_SIGNAL_SEMANTICS.md §9`), **à terminer avant le
closeout final d'`UX4_03`** :

- **B1** — `readiness_score` consomme le `consistency_score` hérité ; un compte
  sans données rend `25,0`, **entièrement fabriqué** par le défaut de fatigue.
- **B2** — « Streak » rendu dans le rapport coach par un **second** producteur.
- **B3** — `compute_recommendation` écrit « Série en cours, garde le rythme ! ».
- **B4** — les trois cartes vides de `weekly_loop`.

Aucun n'est corrigé ici : élargir un correctif de vocabulaire en refonte de
quatre consommateurs est la dérive de périmètre que `CLAUDE.md §4` érige en
arrêt dur.

---

## 7. Checks locaux — tier `SHARED_CODE`

```
check_scope          SHARED_CODE (full sweep local non requis)
ruff (py311)         All checks passed  — fichiers neufs et modifiés
                     les 7 de behavioral.py sont PRÉEXISTANTES (vérifié
                     sur la canonique, diff nul)
check_ruff_budget    281 ≤ 548
check_spec_protocol  OK
targeted_tests       31 passed
broad_sweep_scoped   523 passed  (behavioral · recommendation · training_state
                     · recovery_contract · home · coach_report · progress)
```

**Preuve du bon arbre** : `PYTHONPATH=<worktree>` **en plus** des chemins de
tests absolus. `run_ci_pytest.sh` n'a aucun `cd` — sans cela, `import app`
résout sur la canonique et un vert ne mesure rien.

---

## 8. Fichiers

| Fichier | Nature |
|---|---|
| `app/services/progress_facts.py` | **neuf** — producteur de faits, trois requêtes, aucun score |
| `app/services/progress_signals.py` | **neuf** — vue-modèle pure, aucune requête, aucune arithmétique |
| `app/services/behavioral.py` | **INTACT** — identique à la version gelée depuis `e8614bd` |
| `app/routers/pages.py` | compose faits → vue-modèle ; n'appelle plus le moteur |
| `app/templates/progress.html` | instrument compact, divulgation unique, chapeau réaligné |
| `app/static/css/app.css` | jauges supprimées, contexte en ligne, état inconnu, cible 44 |
| `tests/test_ux4_progress_signals.py` | 31 gardes |
| `docs/UX4_03A_BEHAVIORAL_SIGNAL_SEMANTICS.md` | **neuf** — audit sémantique + registre `UX4_03B` |

Aucune migration · aucun modèle · aucun asset anatomique · aucune dépendance JS
· **les trois moteurs de décision gelés sont intacts**, `git diff e8614bd` vide.

---

**`UX4_03B` — EXPOSÉ, NON COMMITÉ. En attente du verdict opérateur.**
