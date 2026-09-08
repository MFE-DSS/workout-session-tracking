# UI-CP2.0 — rendre l'instrument d'exécution possible

**Tier `check_scope`** : `SHARED_CODE`.
**Périmètre** : `console_state.py` · `sessions.py` (`_persist_set_values`) ·
une suite de gardes neuve. **Aucun gabarit, aucune feuille de style, aucun
pixel.**

Trois verrous, tous trouvés en **mesurant une séance réelle** au labo — aucun
par relecture. Ils ne sont pas des micro-défauts : ils interdisent le cockpit
piloté par l'état que `UI-CP2` doit construire.

---

## 1. F1 + F2 — un seul défaut de sémantique d'état

### Ce qui se passait

La branche `WARMUP` était évaluée **avant tout le reste, sans condition** :

```python
if pending_warmups and not (skip_warmup and pending_works):
    return WARMUP
```

Deux conséquences, mesurées :

**F1 — l'exercice ne pouvait pas se terminer.** Trois séries de travail sur
trois faites, un échauffement non coché ⇒ état `WARMUP`, commande dominante
**« PASSER AUX SÉRIES »** — vers des séries déjà faites. `EXERCISE_COMPLETE`
n'était **jamais** atteint, donc « CONTINUER → E2 » n'apparaissait jamais.

`skip_warmup` ne sauvait pas : sa garde exige qu'il **reste** du travail.

**F2 — le signal de repos était avalé.** Même verrou : tant qu'un échauffement
restait en attente, `?rest=1` était ignoré. On pouvait enregistrer une série de
travail et voir l'instrument réclamer l'échauffement.

Le chemin est **ordinaire, pas exotique** : sauter l'échauffement — qui, par
décision produit `Q-C`, **n'écrit rien** — puis faire ses séries.

### Le contrat ajouté : LA PROGRESSION EST MONOTONE

L'invariant n'est pas un réordonnancement. Il tient en une phrase :
**l'échauffement cesse d'être souverain dès que le travail a commencé**, et la
preuve du départ est une donnée d'entraînement réelle (`work_done > 0`), pas un
paramètre d'URL.

`skip_warmup` reste une pure navigation à portée de requête : il fait avancer
l'affichage, il n'écrit toujours rien, il ne survit pas au rechargement.

### La table de vérité

| échauffements | travail | `rest` | `skipwarm` | suivant | état |
|---|---|---|---|---|---|
| aucun fait | aucun fait | — | — | E2 | `warmup` |
| 1 sur 2 fait | aucun fait | — | — | E2 | `warmup` |
| aucun fait | aucun fait | — | **oui** | E2 | `current_set` |
| aucun fait | **1 fait** | **oui** | — | E2 | **`rest`** ⟵ F2 |
| aucun fait | 1 fait | — | — | E2 | `current_set` |
| tous faits | 1 fait | — | — | E2 | `current_set` |
| **aucun fait** | **tout fait** | — | — | E2 | **`exercise_complete`** ⟵ F1 |
| aucun fait | tout fait | — | — | **aucun** | **`last_exercise_complete`** ⟵ F1 |
| tous faits | tout fait | — | — | E2 | `exercise_complete` |
| aucun fait | tout fait | **oui** | — | E2 | **`exercise_complete`** ⟵ F1 |
| aucun fait | *aucune série* | — | — | E2 | `warmup` |
| tous faits | *aucune série* | — | — | E2 | `exercise_complete` |
| aucun fait | *aucune série* | — | oui | E2 | `exercise_complete` |
| tous faits | 1 sur 3 fait | oui | — | E2 | `rest` |

`CORRECTION` prime sur toute la table — inchangé.

**Le cas « exercice sans série de travail » est une garde délibérée** : ses
échauffements *sont* son travail, et la première branche ne doit pas le
déclarer fini avant qu'ils le soient.

---

## 2. F3 — l'écriture de séance devient un patch partiel

### Ce qui se passait

`_persist_set_values` parcourait **toutes** les séries de l'exercice et écrivait
chacune depuis le formulaire. Une clé absente valait `None`, donc
`completed = False`.

Le contrat était **tout-ou-rien à l'échelle de l'exercice**. Mesuré au labo :
**trois séries postées une à une, une seule survivait** — chaque envoi effaçait
le précédent.

Invisible aujourd'hui, parce que le gabarit rendu poste toujours toutes ses
séries. **Mortel pour un instrument d'exécution qui envoie une série à la
fois** — c'est-à-dire pour A+.

### Le contrat neuf

| dans le formulaire | signification |
|---|---|
| série **citée**, valeur remplie | mise à jour |
| série **citée**, valeur vide | **effacement explicite** — `Sx_24 §E`, inchangé |
| série **absente** | **INCHANGÉE** |
| `clear_set=<id>` | effacement nommé, inchangé |

**« ABSENT » n'est pas « VIDE ».** La distinction est le cœur du correctif :
deux gardes existantes dépendent du vide effaçant, et elles postent des chaînes
vides, pas des clés manquantes. Vérifié avant d'écrire une ligne.

**Le formulaire complet d'aujourd'hui ne change pas d'un iota** — une garde le
prouve explicitement.

---

## 3. Brainstorming / Options / Risques / Choix retenu

### F1+F2 — trois options

| Option | Verdict |
|---|---|
| **Réordonner les branches** — mettre le travail avant l'échauffement | ❌ La directive l'interdit explicitement : « ne pas résoudre par un simple réordonnancement sans prouver les invariants ». Et un réordonnancement nu casserait l'exercice neuf, qui doit proposer son échauffement |
| **Marquer les échauffements faits au saut** | ❌ Fabriquerait des données d'entraînement que l'utilisateur n'a pas produites. La décision `Q-C` l'interdit, et la directive demande de la préserver |
| **Invariant de monotonie** *(retenu)* | ✅ L'échauffement perd sa souveraineté sur **preuve de progression**, pas sur un paramètre. Rien n'est écrit, rien n'est inventé |

### F3 — deux options

| Option | Verdict |
|---|---|
| **Champ témoin** (`set_{id}_present=1`) dans le formulaire | ❌ Impose un changement de gabarit — hors périmètre — et ajoute un état que la présence de la clé porte déjà |
| **Présence de la clé** *(retenu)* | ✅ Aucune donnée nouvelle, aucun gabarit touché, et le formulaire actuel se comporte à l'identique |

### Risques et traitement

| Risque | Traitement |
|---|---|
| Le réordonnancement casse l'exercice neuf | `test_l_echauffement_reste_souverain_tant_que_rien_n_a_commence` — la garde de la garde |
| « Absent » confondu avec « vide » | `test_f3_un_champ_vide_reste_un_effacement_explicite` |
| Le formulaire actuel régresse | `test_f3_le_formulaire_complet_se_comporte_exactement_comme_avant` |
| `nav=prev` cesse d'enregistrer | `test_f3_la_navigation_arriere_enregistre_toujours` |
| Les échauffements emportés par une écriture de travail | `test_f3_les_echauffements_ne_sont_pas_emportes` |
| L'invariant tenu par un seul exemple | `test_l_invariant_de_monotonie_tient_sur_toute_la_table` balaie **toute** la table |

---

## 4. Vérifications

| Contrôle | Résultat |
|---|---|
| `check_scope` | `SHARED_CODE` |
| `ruff` (fichiers touchés) | `All checks passed!` |
| **Pré-balayage AST** S9073 / S5863 | **3 assertions composites trouvées et corrigées AVANT le push** — la règle qui avait fait rougir le gate la veille |
| `tests/test_ui_cp2_0_execution_enablement.py` | **26 passés** |
| **Défauts d'origine replantés** | **2 → 2 suites rouges** (9 et 4 échecs) |
| **Broad sweep ciblé** (séance · console · série · feedback · surcharge · viseur · exercice · progression) | **1 839 passés**, 2 échecs traités ci-dessous |
| Arbre restauré après plantation | à l'identique |

### Les deux échecs du sweep, traités séparément

**`test_the_probe_would_notice_a_missing_field` — le dépôt m'avait laissé la
consigne.** C'est une garde-de-la-garde qui prouvait que les deux gardes de
préservation ne passaient pas à vide, en retirant un champ et en vérifiant que
la série était **bel et bien effacée**. Sa docstring portait son propre mode
d'emploi : *« si ce test cesse d'échouer à l'effacement, c'est que
`_persist_set_values` a changé de comportement — les réécrire avant de
continuer »*. C'est exactement ce qui est arrivé.

Elle est **réécrite, pas assouplie**. Ce qui pourrait encore rendre les gardes
de préservation creuses, c'est un routeur qui n'écrirait plus rien : la sonde
prouve donc les deux moitiés du contrat — **l'écrivain est vivant** (une valeur
soumise et modifiée est persistée) et **le chemin destructeur reste
atteignable** (un champ soumis vide efface toujours). Une garde neuve,
`test_an_absent_field_no_longer_erases`, fige l'acquis.

La suite gardait une **perte de données** ; elle garde désormais la
**composition**. Sa prose et le message d'échec de
`test_every_form_carries_all_the_sets_it_will_overwrite` sont corrigés en
conséquence — une garde dont le commentaire décrit un défaut réparé ment sur le
code qu'elle protège.

**`test_vscode_settings_json_exists` — préexistant, hors périmètre.** Il échoue
à l'identique sur le canonique non modifié. Il asserte sur
`.vscode/settings.json`, un fichier **non suivi par git** que l'éditeur local
réécrit. Une garde posée sur un fichier hors versionnement ne peut pas tenir.
**Consigné, non corrigé** (`§11`).

### La mutation qui ne mutait rien — troisième fois

La première plantation de F3 retirait seulement le `continue`. Elle ne
restaurait **rien** : l'implémentation retombe sur `sl.weight_kg` quand la clé
est absente, donc les valeurs survivaient et la garde restait verte. J'ai failli
en conclure que la garde ne gardait rien.

Le défaut d'origine est la **lecture inconditionnelle** du formulaire. Une
mutation doit restaurer le code d'origine, pas une approximation.

---

## 5. Ce que la tranche ne fait PAS

Aucun gabarit · aucune feuille de style · aucun comportement de recommandation ·
CP-3 fermé · aucune refonte d'historique · aucun cadre de persistance générique.

**Arrêt avant toute production de gabarit**, conformément à `§4` de la
directive. La suite est l'artefact d'arbitrage A+ à six états.
