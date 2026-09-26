# `UI-CP8R` — La vérité temporelle du repos

**Statut** : `MERGÉ` · PR #253 · merge `58b9e29` · migration `w4x9r5s6u17` appliquée
**Branche** : `sb/ui-cp8r-verite-temporelle`, ouverte sur `d6931ef`, canonique `fb42535` (CP8D) fusionnée dedans avant la PR
**Tier `check_scope`** : `MIGRATION`
**Rendus soumis à l'opérateur** (`CLAUDE.md §5.1`) : artifact publié avant
tout commit de gabarit.

---

## 1. Le défaut, reproduit avant d'être corrigé

```
série validée          → REPOS 1:30
attendre 3 s
recharger              → REPOS 1:30   ← identique
```

`?rest=1` ne peut affirmer qu'une chose : « un repos vient de démarrer sur
**cette** requête ». Il ne porte aucune origine de temps. Le gabarit en
faisait `data-rest-started`, un **drapeau booléen**, et le décompte repartait
de `data-rest-duration` — la durée nominale — à chaque rendu.

**Le minuteur n'était pas en cause.** `session_focus.js` raisonnait déjà sur
une échéance (`Date.now() + durée`) et rattrapait déjà au retour
d'arrière-plan. On lui donnait simplement une durée pleine.

Le dépôt avait nommé ce chantier lui-même, au-dessus du producteur du
paramètre : *« le repos n'est pas historisé ici : un tracé durable exigerait
une migration, donc un sprint séparé (`Sb_REST_EVENT_TRACE_01`) »*. C'est ce
sprint.

---

## 2. Brainstorming / Options / Risques / Choix (`CLAUDE.md §3`)

### Option A — une seule colonne, `rest_until` (échéance)

Elle porterait les deux faits : le repos court tant que `now < rest_until`, et
passer le repos s'écrirait `rest_until = now`.

**Rejetée.** L'heure de complétion n'en serait plus déductible que par
`rest_until − REST_FALLBACK_SECONDS`, c'est-à-dire **à travers une constante
de politique**. Le jour où cette constante change, toute la chronologie
historique glisse en silence. `§8` sépare explicitement vérité et politique.

### Option B — `completed_at` seule

Suffisante pour la vérité temporelle, et **insuffisante pour le saut**.

Preuve par inventaire, pas par préférence. Aujourd'hui, passer le repos est un
**lien GET vers la même URL sans `rest=1`** ; le gabarit l'écrivait mot pour
mot : « aucune donnée persistée, aucun état écrit ». Ça ne survit au
rechargement que parce que l'URL rechargée ne porte plus le paramètre. En
retirant au paramètre son autorité (`§7`), on retire au saut son unique
mécanisme : le rendu suivant re-dériverait REPOS et **annulerait la décision
de l'utilisateur** — ce que `§10` interdit.

Colonnes existantes examinées une par une : `SetLog` (aucune colonne
temporelle), `SessionExercise.implicit_label_computed_at` (horodate un calcul
de score, pas une décision d'utilisateur), `WorkoutSession.started_at` /
`ended_at` (portée séance), la série suivante (n'existe pas encore à l'instant
du saut), `?active=` (paramètre d'URL). **Aucune ne change quand
l'utilisateur passe le repos.**

### Option C — deux colonnes · **RETENUE**, approuvée par l'opérateur

| colonne | nature | portée |
|---|---|---|
| `SetLog.completed_at` | un **FAIT** — quand la série a été faite | par série |
| `SetLog.rest_dismissed_at` | une **DÉCISION** — dépasser ce repos | par série |

Portée par **série** et non par séance : la décision appartient à la
transition qui l'a produite. Portée séance, corriger une vieille série
effacerait la décision prise sur la série courante.

### Risques identifiés et traités

| risque | traitement |
|---|---|
| naïf/aware sur SQLite | normalisation à la comparaison, comme les 7 services existants |
| un saut périmé hérité par une exécution neuve | invariant d'épisode (`§2`), garde `J-bis` |
| `<form>` imbriqué pour le POST de saut | `formaction` sur le formulaire existant |
| rotation d'attribut invisible chez un client au cache tiède | `STATIC_ASSET_COHERENCE_01` (empreinte de contenu) couvre déjà |
| bump de `SCHEMA_VERSION` invalidant les sauvegardes | non bumpé — voir §7 |

---

## 3. Le contrat d'écriture — l'épisode de complétion

```
INCOMPLÈTE → COMPLÈTE      completed_at = now UTC · rest_dismissed_at = NULL
COMPLÈTE   → COMPLÈTE      les DEUX préservés
COMPLÈTE   → INCOMPLÈTE    les DEUX effacés
INCOMPLÈTE → COMPLÈTE (2)  nouvel horodatage · rest_dismissed_at = NULL
```

**La préservation sur COMPLÈTE → COMPLÈTE porte la règle de correction sans
aucune branche spéciale** : l'horodatage reste ancien, donc
`now − completed_at > D`, donc `restant = 0`. Corriger une faute de frappe
n'impose jamais 90 secondes.

---

## 4. La dérivation

```
D  = REST_FALLBACK_SECONDS (90, inchangé — §8)
S  = la série de TRAVAIL la plus récemment complétée de l'exercice ACTIF
T0 = S.completed_at

REPOS  ⟺  S existe ∧ T0 ≠ NULL ∧ S.rest_dismissed_at = NULL
          ∧ il reste du travail ∧ (now − T0) < D

restant = max(0, D − (now − T0))
```

### Correction à mon propre paquet de conception

Le paquet écrivait « la série la plus récemment complétée **qui a encore une
série en attente après elle** », par index. **Le producteur d'aujourd'hui ne
compare aucun index** : `stay_redirect_target` émet `rest=1` dès qu'il reste
une série non complétée, où qu'elle soit. Poser la condition par index aurait
changé la sémantique produit sur les complétions dans le désordre — ce que
`§8` interdit à cette tranche. C'est la règle d'aujourd'hui qui est portée.

`§9` « un exercice terminé ne vole pas le repos de l'actif » est fermé dans
`_console_context` : la dérivation n'est faite que pour la carte active.

---

## 5. Extinction de `?rest=1`

| élément | disposition |
|---|---|
| `stay_redirect_target` émettait `&rest=1` | **retiré** — la destination est une URL d'exercice ordinaire |
| `request.query_params.get("rest")` ×2 | **retirés** |
| `build_console_state(rest_signal=…)` | **remplacé** par `rest_remaining: int` |
| `rest_active` (contexte de page) | **retiré** — remplacé par `cs.rest_remaining_seconds`, par exercice |
| `data-rest-started` / `data-rest-duration` | **remplacés** par `data-rest-remaining` |
| lien de reprise + commande du dock | **remplacés** par des `POST` vers `dismiss_rest` |
| `?rest=1` entrant | **inerte** — plus personne ne le lit |

L'inertie est la forme la plus sûre de l'extinction : pas de branche de
compatibilité à maintenir, donc pas de second système de vérité.

Un booléen de page ne pouvait de toute façon pas dire de **quelle série** il
parlait ; la valeur vit désormais sur l'état de la console, par exercice.

---

## 6. Le saut devient un POST — conséquence, pas choix de style

Il écrit un fait, et un `GET` n'écrit pas dans ce dépôt. Un `<form>` imbriqué
dans celui de la carte serait du HTML invalide (le navigateur le supprime
silencieusement, et la sortie de repos cesserait d'exister) : `formaction`
dévie un bouton de soumission du formulaire existant. **Repli sans JavaScript
intact** — c'est une soumission native.

La route n'a **qu'un seul droit d'écriture** et ignore délibérément les
valeurs de série que le formulaire sérialise ; l'élargir en ferait un second
point de persistance des séries, la classe de défaut que `UI-CP2.0` a payée.

Idempotence applicative : si `rest_dismissed_at` est déjà posé, il est
**préservé**. Un double tap ne réécrit pas un instant vécu.

---

## 7. Export / restore — Option A, sans bump de version

Les deux champs partent dans l'export JSON **et** dans le CSV (colonnes
**appendues**, jamais insérées : un consommateur qui lit par index n'est pas
décalé). `restore` les relit quand ils sont présents.

**`SCHEMA_VERSION` n'est pas incrémenté**, et c'est motivé :
`backup_verifier` refuse toute charge dont la version **diffère** de la
courante. L'incrémenter invaliderait d'un coup toutes les sauvegardes déjà
écrites sur disque — pour signaler deux clés *optionnelles* dont l'absence a
exactement le même sens que `null` (« heure inconnue »). Le remède serait plus
destructeur que l'absence de remède.

---

## 8. Migration et rollback

`w4x9r5s6u17` · additive · deux colonnes nullables · **aucun `UPDATE`** ·
idempotente (`_has_column`) · downgrade = deux `drop_column`.

**Aucun backfill, et c'est le cœur de la tranche.** Une ligne existante porte
`completed = 1` et `completed_at = NULL` : *série exécutée, heure inconnue*.
Rien ne permettait de reconstituer cette heure — ni `session.started_at`, ni
l'ordre des séries, ni la durée de séance, ni un repos estimé, ni les séries
voisines. La fabriquer aurait fait dériver un état REPOS de temps imaginaires
sur des séances vieilles de plusieurs mois.

Preuve exécutée sur une base réelle : construite à `v3w8q4r5t16`, peuplée d'une
séance complétée **avant que les colonnes existent**, puis migrée.

```
colonnes AVANT     : … completed
colonnes APRÈS     : … completed, completed_at, rest_dismissed_at
lignes             : (1, completed=1, 80.0, 8, NULL, NULL)
downgrade          : colonnes retirées, données d'entraînement intactes
ré-upgrade         : propre
check_migration_roundtrip : 56 objets avant / 56 après, schéma identique
```

Le retour arrière rend le produit au comportement `?rest=1`. Aucune donnée
d'entraînement n'est perdue : ce qui disparaît est la chronologie fine, qui
n'existait pas avant.

---

## 9. Preuve runtime (`§16`)

Chromium 390×844, produit en cours d'exécution, base migrée.

| état | `data-rest-remaining` | affiché | écran |
|---|---|---|---|
| repos au départ | 89 | `1:29` | REPOS |
| **rechargement à T0+35 s** | **54** | **`0:54`** | REPOS |
| au-delà de la fenêtre | absent | — | série saisissable |
| après un saut | absent | — | série saisissable |
| **saut + rechargement** | **absent** | — | série saisissable |
| ligne d'avant la migration | absent | — | série saisissable |
| `?rest=1` entrant | absent | — | inerte |

Les quatre derniers écrans sont **identiques à l'octet près** : quatre causes,
une issue correcte. C'est la signature d'un état dérivé plutôt que stocké.

---

## 10. Gardes — vues rouges avant d'être vertes

Nouveau module : `tests/test_ui_cp8r_verite_temporelle_du_repos.py`
(17 gardes : `A`–`I`, `J`, `J-bis`, `K`, `L`, `M`, `N`, extinction).

| mutation | attrapée par |
|---|---|
| le restant ignore le temps écoulé *(le défaut d'origine)* | `A` `B` `C` `E` |
| un saut survit à une nouvelle exécution | **personne** → `J-bis` ajoutée |
| le saut répété réécrit son horodatage | `L` |
| une correction réécrit `completed_at` | `E` `K` + `test_une_correction_ne_relance_aucun_repos` |
| `?rest=1` reprend l'autorité | `M` + extinction |

### La mutation qui a survécu

L'effacement de `rest_dismissed_at` à l'entrée d'un nouvel épisode n'était
protégé par aucune garde : `J` passe par « retirer la série », qui efface déjà
les deux champs. L'état existe pourtant vraiment — `restore` lit `completed`,
`completed_at` et `rest_dismissed_at` **indépendamment** depuis le JSON, donc
une charge restaurée peut porter une série incomplète avec un saut
enregistré. `J-bis` sème exactement cet état.

**Une ligne qu'aucune garde ne peut tuer n'est protégée par personne.**

---

## 11. Gardes existantes migrées — propriété par propriété

Treize gardes sont tombées. Aucune n'a été affaiblie ; chacune a été jugée
séparément.

| garde | verdict |
|---|---|
| `test_rest_is_a_request_scoped_presentation_state` | **prémisse tombée** — « disparaît au rechargement » ÉTAIT le défaut. Renommée `..._is_a_derived_state_never_a_stored_one` ; le cœur (aucune colonne d'état) survit et est **renforcé** : on vérifie l'absence de `rest_state`/`resting`/`rest_seconds`/`rest_until` |
| `test_the_next_set_row_is_a_real_link_during_rest` | exigeait la **forme** (`<a>`), pas la propriété. Renommée `..._works_without_js_during_rest` ; contrôle désormais soumission native + `formaction` + absence de `onclick`/`fetch` |
| `test_rest_starts_only_after_a_saved_work_set` | **mesurait le mauvais objet depuis le début** : son titre parle d'échauffement, son corps postait `sets[0]`, que `_first_exercise` filtre sur `kind == "work"`. Elle comparait deux valeurs de `nav`, jamais deux kinds. Corrigée, et elle sépare enfin vraiment les deux |
| `test_the_anchor_target_exists_in_the_rendered_page` | **ne visitait pas la destination** : elle jetait l'URL de redirection et chargeait la page nue. Suit maintenant la redirection réelle |
| `test_rest_timer_has_aria_live_polite` | `Web:S6819` (MAJOR) signalait ce bloc depuis des mois. Passé à `<output>`, qui porte nativement `role="status"` ; la garde vérifie l'élément annonceur et **refuse le retour au `<div>`** |
| 2 gardes d'accessibilité | leur laboratoire **ne pouvait pas porter l'état mesuré** : `_seed` ne pose qu'une série de travail, la condition était `if len(work) >= 2`, donc rien n'était jamais complété — `?rest=1` imposait un REPOS impossible |
| `test_set_inputs_keep_their_accessible_names` | postait une série de travail sous `stay_norest`, combinaison qu'**aucun écran ne produit** ; passe par le vrai chemin (valider les échauffements) |
| table de vérité `CP2.0` (15 cas) | **inchangée d'une ligne** — seule l'origine du signal change, pas la machine |
| `test_every_selector_a_script_reads_exists_in_a_template` | **lisait les commentaires comme du code** — voir §12 |
| sentinelle de head Alembic | entrée de registre ajoutée |

### Vérification que `stay_norest` reste fidèle

`nav=stay_norest` ne suffit plus à empêcher un repos : c'est le **fait** d'avoir
complété une série de travail qui le déclenche. Les deux seuls écrans qui
émettent `stay_norest` restent pourtant inchangés, et c'est prouvé :

* **validation d'échauffement** — la dérivation ne regarde que `kind == "work"` ;
* **correction** — `_resolve_correction` exige `sl.completed`, donc la
  transition est toujours COMPLÈTE → COMPLÈTE, donc `completed_at` est
  préservé (garde `test_une_correction_ne_relance_aucun_repos`).

---

## 12. Trois défauts d'outillage corrigés au passage

### Une garde statique accusait du code sain

`test_every_selector_a_script_reads_exists_in_a_template` accusait
`session_focus.js` de lire `[data-start-rest]` — qu'il ne fait que **nommer**,
dans le commentaire racontant l'incident `DF-03`. Le remède naturel aurait été
d'effacer l'explication pour satisfaire l'outil. Le biais existe dans les deux
sens : un commentaire Jinja nommant un attribut retiré aurait **disculpé** un
script réellement orphelin. Commentaires retirés des deux côtés, plus une
garde prouvant que le filtre ne mange pas le code.

### `python scripts/x.py` depuis un worktree mesure le **mauvais arbre**

`check_alembic_drift` rapportait une dérive inexistante. Cause :
`python scripts/x.py` met `scripts/` en `sys.path[0]`, pas la racine — et une
**installation éditable** (`__editable__.workout_session_tracking…`) résout
alors `app` vers `/Users/martinfeldmann/workout-session-tracking`, le worktree
**principal**, tandis que les migrations viennent du worktree courant
(`script_location` relatif au `cwd`). La « dérive » était l'écart entre le
modèle neuf et l'ancien.

Le script documentait déjà la bonne invocation dans sa propre docstring :
`python -m scripts.check_alembic_drift`. **Neuvième forme de « mesurer le
mauvais objet » dans ce dépôt.**

### Prose périmée alignée sur le comportement

* `SetLog.completed` (`§5` de la directive) décrivait un drapeau « explicite »
  que l'utilisateur cocherait ; la case a été retirée par `Sb_24.4` et
  `completed` est dérivé de la présence de weight/reps. **Le comportement
  n'est pas touché** — c'est la prose qui est alignée sur lui.
* `console_state` affirmait « aucun état n'est persisté » ; section réécrite.
* `static_assets` affirmait que le HTML « n'émet plus que
  `[data-rest-started]` ».

---

## 13. `±15 s` et l'horloge client

`±15 s` reste **local et non persisté** ; un rechargement revient à la base
serveur. Aucun champ n'est ajouté « par symétrie » : `UI-CP8R` rend durable
l'**origine de temps**, jamais la consigne.

Le client reçoit `data-rest-remaining` et en fait une échéance
`Date.now() + restant`. **`performance.now()` est explicitement refusé** : sur
WebKit elle n'avance pas de façon fiable au travers d'une mise en veille de
l'OS, donc un téléphone verrouillé figerait le décompte. `Date.now()` n'est
pour autant la vérité de rien — c'est une horloge d'affichage entre deux
rendus serveur, jetée à chaque rechargement. Aucun horodatage client n'est
persisté. **Aucun service worker** (`§17`).

---

## 14. Relecture du relevé de décisions (`CLAUDE.md §5.2`)

| décision | verdict |
|---|---|
| `Q6` échelle typographique, un `DISPLAY` par écran | **non concernée** — aucun rang modifié |
| un seul aplat ambre par écran | **respectée** — la sortie de repos reste l'unique commande dominante ; le passage de `<a>` à `<button>` conserve `dock__cmd` |
| bleu = provenance système | **respectée** — le chrono reste bleu, il est une lecture produite par AUREN |
| `CLAUDE.md §5.3` jamais une soustraction seule | **respectée** — le lien retiré part avec le POST qui le remplace, dans la même livraison |
| `CLAUDE.md §5.4` toute couleur est un token | **non concernée** — aucune couleur ajoutée |
| `Sx_UIV3_04 §1bis C` la durée est une suggestion | **respectée** — `REST_FALLBACK_SECONDS` inchangé, `±15 s` non persisté |
| `UI-CP2` le repos est un état, pas une porte | **renforcée** — il est désormais un état *dérivé de faits*, pas d'une URL |
| `UI-CP2` aucune ancre vers le repos | **respectée** |
| cibles tactiles ≥ 44 | **non concernée** — le bouton reprend les dimensions du lien |

---

## 15. Ce qui n'a pas été ouvert (`§15`)

Repos adaptatif · par muscle · par exercice · ajustement à la fatigue · PWA /
service worker · refonte de navigation · refonte de cycle de vie ·
persistance de brouillon · nouvelle UI de chronométrage. **Aucun.**

---

## 16. `CP8I` — constat reporté, nommé, non enterré (`§14`)

**`CP8I` — RÉSILIENCE DE SAISIE.** Les valeurs saisies mais non validées sont
**perdues** au rechargement (mesuré : `['80','8']` → `[]`). Classe **P1**.

Hors périmètre de `CP8R` : le corriger demanderait une persistance par frappe
ou un brouillon, donc une décision produit distincte — et
`CLAUDE.md` classe une nouvelle persistance comme un arrêt dur. **`CP8I` suit
`CP8R`, avant toute convergence de navigation.**

---

## 17. À vérifier sur appareil réel — `NEEDS_OPERATOR_DEVICE` (`§13`)

La couverture automatisée couvre le rechargement, `visibilitychange` et
l'indépendance aux rappels. **Chromium n'est pas une preuve pour Safari iOS.**

À exécuter sur iPhone Safari, et à consigner en `CP11` :

1. démarrer un repos, **verrouiller l'écran**, déverrouiller **avant** échéance ;
2. démarrer un repos, verrouiller, déverrouiller **après** échéance.

Le serveur re-dérive à chaque rendu, donc le risque résiduel est un
**affichage** figé entre deux rendus, jamais un état faux.

---

## 18. Closeout

| | |
|---|---|
| **PR** | [#253](https://github.com/MFE-DSS/workout-session-tracking/pull/253) |
| **Merge** | `58b9e29f5eab658dd32f60fbdc0804ff4541e682` |
| **Méthode** | `--merge` avec `--match-head-commit 80ecb4e` — pas de squash, pas de `--admin`, pas de force |
| **CI de PR** | 9/9 verts |
| **CI canonique** | run [`36273576860`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/36273576860) — **7/7 verts** |
| **Sonar (PR)** | `OK` — couverture nouveau code **95,9 %**, 0 bug, **0 code smell pondéré**, 0 duplication |
| **Threads de revue** | 0 non résolu |
| **Migration** | `w4x9r5s6u17` — appliquée, additive, sans backfill |
| **Sweep local** | `tous les lots sont verts.` sur l'arbre committé |

### Les quatre findings Sonar, et celui que j'ai causé moi-même

Premier passage : `new_code_smells_severity = 15` pour un seuil de 14 — un
seul MAJOR ferme la porte. Corrigés en `80ecb4e`.

* **`Web:S6819` était un faux positif de MA prose.** Le parseur HTML de
  Sonar ne connaît pas les commentaires Jinja : il a lu une balise écrite
  dans mon explication comme du balisage **vivant**. L'analyseur signalait
  donc une phrase qui disait que le défaut était corrigé — alors qu'il
  l'était. `exercise_card.html` porte **exactement le même avertissement**,
  dans ces termes. Le piège était écrit dans le dépôt et j'y suis tombé.
* **`external_ruff:UP045` ×2** — les deux colonnes neuves suivaient le style
  `Optional[...]` de leurs voisines. La dette couvre tout le fichier et le
  budget la tolère sur l'existant ; une **ligne neuve** tombe dans le code
  nouveau. Converties, voisines laissées en place (dérive de périmètre).
* **`python:S8415`** — la 404 de `dismiss_rest` est documentée suivant la
  convention déjà posée par `user_programs.py`, plutôt qu'une inventée.

### Ce qui reste ouvert après `CP8R`

| résidu | destination |
|---|---|
| valeurs saisies non validées perdues au rechargement (**P1**) | **`CP8I`** |
| iPhone Safari, écran verrouillé pendant le repos | `CP11` — `NEEDS_OPERATOR_DEVICE` |
| sept orthographes de la normalisation naïf/aware | non planifié, hors périmètre |
| `ACCOUNT`, `PROGRAM_LIFECYCLE`, `BODY_DATA_CONTROL` | `UI-CP8` (suite) |

🤖 Generated with [Claude Code](https://claude.com/claude-code)

