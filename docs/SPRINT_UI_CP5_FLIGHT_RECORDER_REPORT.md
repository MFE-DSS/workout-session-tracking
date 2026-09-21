# `UI-CP5` — `FLIGHT_RECORDER`

> **Question possédée** : « Qu'est-ce qui vient réellement de changer ? »
> **Concept retenu** (arbitrage opérateur clos) : **A+ — EXPLAINABLE DEBRIEF**.
> B ne survit que comme **index de détail temporel**, jamais comme axe de
> magnitude anonyme.
> **Contrat** (`AUREN_INSTRUMENTS.md §FLIGHT_RECORDER`) :
> `ACTION = aucune. C'est une lecture.`

---

## 1. Ce qui n'allait pas, mesuré avant d'écrire une ligne

Sur un compte réel — 6 semaines, 21 séances, 639 séries — **deux surfaces
répondaient à la question et aucune ne la posait**.

| | `/history` | `/progress` |
|---|---|---|
| Écrans (390×844) | **4,72** | 3,74 |
| **Formulaires** | **42** | 0 |
| Plus grosse typo | **18 px — « Historique »** | 32 px — un relevé |

`/history` énumérait 21 rectangles identiques : la séance d'il y a une heure
pesait autant que celle d'il y a six semaines. Et elle portait **42
formulaires** sur un instrument dont le contrat dit « aucune action ».

**Et le défaut s'aggravait à mesure que le compte était mince** — c'est-à-dire
sur tout nouvel utilisateur. À 2 séances, la plus grosse typographie devenait
un *titre de section*. À 0 séance, `progression.any` valait `False` et **le
partiel entier disparaissait** : un vide silencieux, sans une phrase pour dire
pourquoi.

Le défaut était de **composition**, pas de données. Le produit avait les
réponses ; il n'avait pas l'instrument qui les pose.

---

## 2. Le cœur : `PRIMARY DEBRIEF SIGNAL`

Le contrat fixait déjà l'échelle — `L1 debrief · L2 dernier mouvement · SHEET
détail`. **L1 n'existait nulle part.** C'est la case qui est remplie.

### Précédence — sémantique, versionnée, jamais un score

```
1. ATTENTION   — la dernière séance porte un signal nommable
2. MOUVEMENT   — sinon, progression["lead"] is not None
3. INSUFFISANT — sinon
```

Trois booléens, un `if/elif/else`. **Les kilos ne rencontrent jamais les
anomalies.** `PRECEDENCE_VERSION` (`L1-DEBRIEF/1`) et `ORDRE_PRECEDENCE` sont
épinglés **dans la même assertion** : réordonner force à toucher la ligne qui
porte la version.

Une garde AST interdit `sorted` / `max` / `min` / la multiplication dans le
module : il n'y a **pas d'endroit où un classement pourrait s'écrire**.

### Deux modules, patron `overload_engine` / `overload_inputs`

* **`app/services/flight_recorder.py`** — **pur**. Ni `sqlalchemy`, ni
  `datetime` (garde AST).
* **`app/services/flight_recorder_inputs.py`** — **une** requête bornée :
  dernière séance `completed`, non exclue, `limit(1)`, `selectinload` chaînés
  jusqu'à `template_exercise.rep_targets`.

⚠ **COÛT — LE PLAN ANNONÇAIT UNE ÉCONOMIE QUI N'EST PAS LIVRÉE, ET JE LE DIS
PLUTÔT QUE DE LA RECOPIER.**

Le plan prévoyait « +1 aller-retour, **−N chargements paresseux** », en
supposant que `build_progress_week` serait réduit à `{"dominant_templates"}`
une fois `top_anomaly` sorti de la route. **Ce n'est pas fait, et ne pouvait pas
l'être dans ce périmètre** : deux gardes épinglent ce producteur —

* `test_weekly_loop.py` exige `set(payload) == {"dominant_templates",
  "top_anomaly"}` ;
* la même famille exige que la chaîne `build_progress_week(db, user)` figure
  dans `pages.py`.

Les affaiblir pour livrer une économie serait exactement ce que la consigne
permanente interdit. **Coût réel livré : +1 aller-retour borné, et le détecteur
d'anomalies tourne désormais DEUX fois par chargement de `/progress`** — une
fois dans `build_progress_week`, dont le `top_anomaly` n'est plus lu sur cette
route, une fois dans le debriefing. C'est une dette **nommée**, pas une
économie. Sa résorption est une tranche à part : elle touche le contrat d'un
producteur partagé et son consommateur `narrative.py`.

### `FLIGHT_RECORDER` possède son sélecteur — et pourquoi

**`build_progress_week()["top_anomaly"]` n'est PAS réutilisé.** Trois raisons,
toutes vérifiables dans le dépôt :

1. **La fenêtre est structurellement fausse.** Elle est bornée à la semaine ISO
   courante (`weekly_loop.py:93-95`) : le lundi matin, la dernière séance est
   dans la semaine précédente et le signal se tait, alors que « depuis ta
   dernière séance » doit encore parler.
2. **Défaut mesuré, et il est dans le dépôt** : `_load_window_sessions` trie
   `started_at.asc()` et `_pick_top_anomaly` rend la **première** séance
   porteuse d'anomalies — **la plus ancienne gagne**.
3. `severity` vaut toujours `"info"` : il n'y a **pas** de « top ». On nomme ce
   qu'on fait — *premier signal nommable de la dernière séance*.

⚠ **La règle C reste DORMANTE, et c'est une décision, pas un oubli.**
`stats.last_time_by_exercise_code` scope « la dernière fois » sur l'identité
**héritée** `(gabarit, code)` que `progression_facts` a délibérément abandonnée
(106 identités héritées pour 68 exercices réels). La réveiller ferait cohabiter
**deux « dernière fois » contradictoires dans le même instrument**. Inscrit en
docstring et tenu par une garde source.

### `INSUFFISANT` dit toujours POURQUOI

Cinq causes, chacune prouvée par un champ **existant** — aucune inventée :

| Cause | Prouvée par |
|---|---|
| aucune séance terminée | `derniere is None` ∧ `progression["any"] is False` |
| **aucun mouvement comparable** | `derniere is not None` ∧ `any is False` |
| pratiqué une seule fois | `awaiting[].reason == RAISON_UNE_SEULE_SEANCE` |
| revu sans série notée | `awaiting[].reason == RAISON_AUCUNE_SERIE` |
| nom non rattaché | `unresolved` / `unresolved_names` |

⚠ **La 2ᵉ a été trouvée en traçant le compte cardio-seulement** : les quatre
autres rendaient un tuple **vide**, c'est-à-dire « pas encore possible » sans
dire pourquoi. C'est précisément l'état que cette tranche existe pour fermer.

### Variantes typées — l'état illégal est inexprimable

* `DebriefInsuffisant` n'a **aucun** champ pouvant porter un écart ou une
  performance → une comparaison inventée est inexprimable ;
* `DebriefMouvement` n'a aucun champ pouvant porter un message d'anomalie ;
* **aucune** variante n'a de champ de rang, de poids ou de score → un moteur de
  signification n'a **pas d'endroit où écrire**.

Gardes de champs via `dataclasses.fields()` — **pas** `__dataclass_fields__`,
qui inclut les pseudo-champs `ClassVar` (leçon déjà payée en `UI-CP4`).

### Confiance — empruntée, jamais dupliquée

`zone_exposure` **est** l'implémentation de référence `TRUST EXPRESSION`. Ses
quatre littéraux (`known` / `zero` / `partial` / `unknown`) sont **recopiés**
— le module doit rester chargeable sans base — et **une garde compare les deux
jeux** pour que la copie ne dérive pas.

Signal et état sont **orthogonaux** : un `ATTENTION` en état `zero` est
honnête. Aucun score global, aucun badge, aucune couche de fiabilité — vérifié
par une garde qui cherche `confidence` / `badge` / `fiabilite` dans le code
exécutable du module.

---

## 3. Un défaut trouvé au rendu, que les gardes statiques ne pouvaient pas voir

**C'est le fait le plus important de cette tranche, et il mérite d'être lu
avant les chiffres.**

La première écriture de la route ne vidait le relevé de progression que sur le
signal `mouvement`. Mesuré sur le compte de labo `pilote-anomalie` :

> le L1 annonçait **« À VÉRIFIER · Rowing machine chest-supported »** à 22 px,
> et le relevé de progression gardait ses **32 px juste en dessous**.

Le plus gros objet de l'écran était donc un **« 37,5 » sans rapport avec la
réponse** — très exactement l'inversion de hiérarchie que `UI-CP5` existe pour
fermer, revenue par la branche qu'on regardait le moins.

**Aucune taille déclarée n'était fautive.** Les gardes de
`test_progression_sovereign_readout.py` comparent des tailles écrites dans la
feuille ; ici c'est leur **coexistence sur un même écran** qui était le défaut.
Seul un rendu pouvait le voir. C'est l'argument de `CLAUDE.md §5.1` dans sa
forme la plus littérale.

**Correctif** — `_demettre_le_releve_de_progression`, et il a deux moitiés :

* `lead` est vidé **sans condition**. Un `if` sur le signal est la porte par
  laquelle le défaut est entré la première fois ;
* sur `mouvement`, le L1 **EST** ce mouvement : il ne redescend pas, sinon la
  promotion se lit comme une duplication ;
* sur tout autre signal, le L1 parle d'**autre chose** : le mouvement redescend
  **en tête de liste**. Il perd son rang, pas son existence. `§5.3` — jamais
  une soustraction seule : `build_progression_view` l'avait *sorti* de `rows`
  en le promouvant, et se contenter de le vider l'aurait effacé de la page.

**Deux gardes le tiennent, et la seconde a dû être réécrite** : posée d'abord
sur la seule fixture `client`, elle restait **verte le défaut planté** — ce
compte n'a aucun mouvement comparable, donc `lead` y valait déjà `None` et il
n'y avait rien à démettre. *Une garde qui observe un état que son corpus ne
produit jamais n'est pas une garde.* L'état discriminant est désormais **semé**
(un mouvement comparable **et** une anomalie sur la dernière séance) et sa
présence est vérifiée **avant** l'invariant.

---

## 4. `/progress` — 12 blocs → 5 couches

Ordre livré, **aucune couche n'est une carte** :

```
<h1>Progression</h1>
L1   _partials/debrief_signal.html     ← souverain, ZÉRO <h2> au-dessus
L2   _partials/progression.html        ← lead vidé, rang libéré
     EXPOSITION / CONTEXTE DE CONFIANCE  (zone_exposure + cockpit__tally + ctx)
     Par programme                     (sans .card)
     <details> « Comment AUREN choisit ce qu'il montre en premier »
     DÉTAIL TEMPOREL                   ← rail 14 j + entrée vers /history
     POIDS CORPOREL                    ← Y = kg, nommé et vrai
     .kpi-note                         ← réécrite : n'explique que ce qui reste
```

### Retraits, et ce qui les remplace

| Retiré | Pourquoi | Ce qui le remplace |
|---|---|---|
| lede | 4ᵉ ligne de prose concurrente du L1 | son périmètre part dans le `<details>` |
| **RYTHME RÉCENT** (`.kpi-grid`, 4 tuiles) | quatre comptages au-dessus de la réponse | une ligne de contexte `.ctx` |
| **Qualité des séances** (courbe) | son axe Y est un **score composite tracé en hauteur** | survit par programme, déjà rendu |
| bloc `top_anomaly` | **absorbé par L1** | rendu une fois, jamais deux |

**Survie fait par fait des quatre tuiles** — aucun fait n'est perdu en silence :

| Tuile | Survie |
|---|---|
| `0` `sessions_this_week` | pas de surface propre. ⚠ **le champ de service RESTE** : `test_ux4_progress_signals.py` découpe la SOURCE de `compute_global_kpis` sur `"sessions_this_week = "` et lèverait `IndexError` |
| `13` `completed_last_30` | ligne de contexte — c'est le dénominateur de tout ce que la page affirme sur 30 j |
| `100 %` `completion_rate_30d` | qualificatif de provenance, rendu **inconditionnellement** |
| `82` `avg_success_score_30d` | **ne survit pas ici** — c'est un score, et `TRAIN1-C`/`TRAIN1-E` ont passé deux tranches à retirer la doctrine de score de cette page |
| `absent_measures` | **garde son rendu** comme clause de provenance |

**Aucun score composite de remplacement.**

### L1 réutilise le véhicule souverain

`.lead__value` vaut 32 px et est **épinglé inter-surface** à
`--font-size-metric-lg` (`session_focus.css`). Créer un `.debrief__value` à
32 px aurait cassé cet épinglage et créé **deux rangs souverains**.

→ L1 réutilise le vocabulaire `.lead__*`. **Un seul relevé souverain par
écran** ; *quel objet l'occupe* est la décision du service.

| Signal | Fente souveraine 32 px |
|---|---|
| `MOUVEMENT` | charge / reps + `avant N` + écart signé — identique à avant |
| `ATTENTION` | **personne** — voir l'arbitrage ci-dessous |
| `INSUFFISANT` | **personne** — la cause nommée, au rang `SECTION` |

⚠ **ARBITRAGE, SIGNALÉ PARCE QU'IL S'ÉCARTE DU PLAN.** Le plan prévoyait que
`ATTENTION` occupe la fente 32 px avec « la variable nommée qui a déclenché
l'attention, avec son unité ». **Le détecteur d'anomalies n'expose aucune
grandeur numérique structurée** — seulement un message. La seule façon de
remplir la fente aurait été d'extraire un nombre du texte ou d'en fabriquer un,
et le plan l'interdit dans la même phrase (« jamais un nombre de gravité
inventé »).

Retenu : **sur `ATTENTION`, aucun élément n'atteint le rang souverain**, et le
plus gros objet de l'écran est l'exercice à vérifier, au rang `SECTION`. C'est
cohérent avec le reste du socle — le rang `DISPLAY` est pour un relevé
**mesuré**, et `ATTENTION` n'a pas de mesure propre : elle a un **objet**.

**Conséquence à connaître** : sur cet état, la réponse partage son rang avec les
titres de section, et s'en distingue par la graisse et la casse, pas par la
taille. C'est visible sur la capture. **À trancher par l'opérateur.**

---

## 5. `/history` — la couche de détail, plus la réponse

La route est conservée (cible de lien profond). Ce qui change : **elle cesse de
promettre une seconde réponse à la même question** — son lede le dit
explicitement (« Ce qui a changé se lit sur Progression »).

* **La frise** — X = temps, un marqueur = une séance. **Aucun axe Y, aucune
  hauteur, aucune aire n'encode quoi que ce soit.** État par **forme** :
  `completed` plein · `in_progress` contour pointillé · `excluded_from_stats`
  **hachuré** (`#auren-hatch`, le motif de `zone_exposure`). Sélection par
  **bordure**, jamais par la couleur seule.
* **La légende ne liste que les états réellement présents** — la première
  écriture annonçait « en cours » inconditionnellement et faisait échouer une
  garde réelle qui vérifie qu'une séance terminée n'est pas annoncée en cours.
* **Sélection sans JavaScript** : `?session=<id>`, précédent documenté
  `?loadout=` et `?active=`. Chaque marqueur **reporte le filtre courant**.
* **Le rôle compact** — une *ligne* par séance, sans chrome de carte, **aucune
  commande**. 21 lignes, pas 21 rectangles.

⚠ Le titre de la frise disait d'abord « SIX DERNIÈRES SEMAINES ». **C'était une
revendication fausse** — la bande rend jusqu'à 100 séances. Corrigé en « Frise
des séances ».

`.limit(100)` et l'absence de pagination sont **conservés** — dette nommée, y
toucher serait de la dérive (§14).

---

## 6. `SESSION_LIFECYCLE` — la capacité est préservée, la charge retirée

**La capacité avait déjà une surface** : `/admin/sessions` rendait déjà les deux
formulaires. `UI-CP5` ne construit pas une surface — il **nomme** une
responsabilité et cesse de la dupliquer 42 fois.

* `/history` rend **zéro** formulaire, **quel que soit le nombre de séances**
  (garde d'invariant de compte, pas de lecture de gabarit : l'ancienne comptait
  le corps d'une boucle et exigeait « exactement 1 », alors que l'écran en
  portait **une par séance**).
* **Une** entrée discrète par détail de séance : « Gérer cette séance ».
* Route `/admin/sessions` **conservée** — la renommer toucherait
  `AUTH_SCOPE_MATRIX.md` et son script de vérification.

### Le reniflage de `Referer` est supprimé

`admin.py` choisissait sa redirection en cherchant `"/history"` dans l'en-tête
`Referer`. **Load-bearing** : le jour où les formulaires bougent, toute action
rebondit vers `/admin/sessions`. `Referer` est en outre absent sous
`Referrer-Policy: no-referrer`.

→ champ `next` + **allowlist serveur** fermée (`DESTINATIONS_DE_RETOUR`).

### Suppression — confirmation **serveur** en deux temps

La protection était `onsubmit="return confirm(...)"` : **client seulement**,
non appliquée côté serveur, et du JavaScript sur une surface gardée contre le
JavaScript.

1. `GET /admin/sessions/{id}/delete` → une vue qui **nomme** la séance, sa date,
   ses comptes d'exercices et de séries, et ce qui disparaît en cascade ;
2. le POST exige un champ que seule cette vue produit. Absent → 303 vers la
   confirmation, **jamais** de suppression ;
3. la vue offre **l'alternative réversible** (« Exclure des KPI ») en ligne.

⚠ **Aucune machinerie CSRF n'existe dans l'application, et le deux-temps n'en
est pas une.** Écrit ici noir sur blanc pour que personne ne le lise ainsi plus
tard.

La vue est **atteignable par lien** depuis `/admin/sessions`, sinon elle
échapperait à `check_overflow.py`, qui découvre par exploration.

---

## 7. Convergence `MISSION` B → A

`<nav class="mission-bridge">` est retiré de l'accueil, avec ses règles CSS.

**Raison mesurée, pas préférence** : ses deux sorties menaient à `/progress` et
`/profile` — **des onglets primaires de la barre basse**. C'est le défaut que
`UI-CP4` venait de retirer de la coque.

**La prose n'est pas supprimée : elle est mise au passé.** Le bloc devient une
**stèle** — ce que le pont était, pourquoi, et que `UI-CP5` l'a retiré **selon
son propre critère écrit**. Elle contient toujours `FLIGHT_RECORDER`, donc
`test_ui_cp3_mission.py:309` passe **verbatim, et pour la bonne raison** : la
garde passe d'une promesse à tenir au registre d'une promesse tenue.

`test_every_remaining_exit_answers_a_question` avait écrit son propre point
d'arrêt : « quand `FLIGHT_RECORDER` répondra à *qu'est-ce qui a changé ?*, la
sortie n'aura plus de raison d'être. » Elle vérifie désormais que la
soustraction a bien été un **tri** : plus aucune sortie, et chaque destination
toujours atteignable par la coque.

⚠ La sonde `_exits()` **s'auto-assertait** sur `mission-bridge` : le pont
retiré, elle aurait **levé** au lieu d'échouer, et huit gardes seraient tombées
sans dire ce qu'elles protégeaient. Elle lit désormais tous les liens hors
héros.

---

## 8. Mesures — 390 × 844, sur données réelles semées

### Les deux métriques que le §13 exigeait et qui n'existaient pas

| | peuplé | anomalie | partiel | **creux** |
|---|---|---|---|---|
| **défilement avant la réponse** | **0 px** | **0 px** | **0 px** | **0 px** |
| `h2` avant L1 | **0** | **0** | **0** | **0** |
| **gestes requis** | **0** | **0** | **0** | **0** |

### Densité

| | avant | après |
|---|---|---|
| `/progress` — écrans, peuplé | 3,74 | **2,91** |
| `/progress` — écrans, anomalie | — | **2,45** |
| `/progress` — écrans, partiel | — | **2,00** |
| `/progress` — écrans, **creux** | — | **1,08** |
| `/history` — écrans, peuplé | 4,72 | **3,02** |
| **`/history` — formulaires** | **42** | **0** |
| cibles < 44 px, `/progress` **et** `/history` | — | **0** (3 comptes, après correction — voir §11) |
| styles en ligne, les deux gabarits | 0 | **0** (strict, cliquet tenu) |
| aplats ambre par écran | — | **0** |
| débordement horizontal (390) | — | **aucun** |

### La plus grosse typographie **est** la réponse, sur les quatre états

| état | plus gros objet rendu |
|---|---|
| peuplé | **32 px — « 40 »** (le relevé) |
| anomalie | **22 px — « Rowing machine chest-supported »** |
| partiel | **22 px — « 7 exercices pratiqués une seule fois. »** |
| **creux** | **22 px — « Aucune séance terminée : il n'y a encore rien à comparer. »** |

Sur un compte neuf, le plus gros objet était auparavant **« Exposition · 14 j »**
— un titre de section. C'est l'inversion la plus visible que la tranche ferme.

### La surface de cycle de vie, mesurée elle aussi

| | mesuré |
|---|---|
| `/admin/sessions` — liens vers la confirmation | **21** (un par séance, atteignable par exploration) |
| vue de confirmation — nomme la séance et sa date | **oui** |
| — dit « définitive » et chiffre la cascade | **oui** — « 7 exercices et 30 séries » |
| — offre l'alternative réversible | **oui**, en ligne |
| — offre « Annuler » | **oui** |
| — cibles < 44 px | **0** |

Le bouton destructif réutilise `.btn--danger` → `var(--danger)`, **un token
existant, sans repli hexadécimal** (`§5.4`). Aucune couleur n'est introduite par
cette tranche.

⚠ **Une mesure DOM lit 3 `style=""` sur cette vue — ce n'est pas de la dette.**
Ce sont trois attributs **vides** posés par Chromium sur des `<input>`
(heuristique d'autofill). La source du gabarit en contient **zéro**, vérifié au
grep, et le cliquet du dépôt lit le **gabarit**, pas le DOM. Noté ici pour que
le chiffre ne soit pas relu plus tard comme une régression.

### ⚠ Un chiffre qui ne dit PAS ce qu'on aimerait lui faire dire

Le compteur de **conteneurs** passe de 87 à **89** sur `/history` et de 26 à
**27** sur `/progress` peuplé. **Ce n'est pas une amélioration, et je ne la
revendique pas.** Décomposition mesurée sur `/history` :

```
badge           43     les pastilles « 7/7 exos », « durée 1 h 17 » — conservées,
                       une garde les exige explicitement
hroster__row    20     un FILET de séparation, pas une carte
tband__mark     24     les marqueurs de la frise : la bordure EST l'état
filter-bar       2     inchangé
```

Le compteur additionne un **filet de 1 px** et une **carte à fond plein** sous
le même nom. Il ne sépare pas ce qui a changé. Les grandeurs qui décrivent
réellement la tranche sont les **écrans** (4,72 → 3,02) et les **formulaires**
(42 → 0). Ce compteur avait déjà rendu 90 sur un écran visiblement plus léger
en comptant des bordures transparentes ; il a été corrigé alors, il reste
grossier ici.

---

## 9. Relecture décision par décision (`CLAUDE.md §5.2`)

`docs/DESIGN_DECISIONS_UIV2_SURFACES.md` :

| Décision | Verdict |
|---|---|
| **Q1** — la connexion porte l'identité | non concernée |
| **Q2** — ancre visuelle de l'accueil | non concernée (l'accueil ne perd que le pont) |
| **Q3** — « État du jour » (décommissionnée) | non concernée |
| **Q4** — la ligne de série est un instrument | non concernée |
| **Q5** — trois rangs de surface | **respectée**. L1 est rang 2 (filet, aucun fond) ; les causes et le contexte sont rang 3 (**aucun conteneur**) ; les puits du relevé restent rang 1, inchangés |
| **Q6** — échelle 32 / 22 / 15 / 12, *un seul DISPLAY par écran* | **respectée**, et c'est elle qui a fait trouver le défaut du §3. ⚠ Précision : la mesure compte **2 éléments** à 32 px sur l'état peuplé — ce sont les **deux puits** (charge, reps) d'**un seul** relevé, le véhicule pré-existant repris verbatim. Un relevé, deux grandeurs ; pas deux relevés |
| **Q7** — un seul aplat ambre par écran | **respectée** — mesuré **0** aplat sur les quatre états |
| **Q8** — aucune opacité décorative | **respectée** — aucune opacité introduite ; la hachure est un `<pattern>` SVG, pas un voile |

`no-color-only-state` : **respectée** — les trois états de la frise sont
distingués par la **forme** (plein / contour pointillé / hachure) **et** par un
libellé de légende ; la sélection par une **bordure**.

---

## 10. Nettoyage CSS — et une famille morte trouvée par une garde généralisée

`test_progression_sovereign_readout.py` nommait ses sélecteurs un par un — donc
elle devait être remise à jour à chaque tranche, donc elle finissait par ne plus
couvrir ce qu'on venait d'ajouter. Elle **énumère désormais toutes les tailles
déclarées** dans `app.css` et exige qu'aucune ne tombe entre le rang `SECTION`
(22 px) et le relevé souverain (32 px).

**Elle a mordu au premier lancement**, sur deux objets de natures différentes :

1. **`.kpi__value`, 24 px** — dans une famille `.kpi-row` / `.kpi` /
   `.kpi__value` / `.kpi__label` / `.kpi--accent` **sans aucun consommateur de
   gabarit**, vérifié classe par classe. Un rang intermédiaire **dormant**,
   prêt à être réemployé par la prochaine tranche cherchant « une classe de
   valeur qui existe déjà ». **Retirée**, avec sa stèle, plus les quatre règles
   de `home.css` qui ne neutralisaient plus qu'elle et la règle
   `.insight .kpi__value` qui ne désignait plus rien.
2. **`.user-profile__name`, 24 px** — le `<h1>` du profil **public**. C'est un
   **nom**, pas un comptage, et `user_profile` est une surface `TRANSITIONAL`
   hors du périmètre de cette tranche. **Inscrit dans `DETTE_HORS_ECHELLE`**
   avec sa raison. Le registre est **fermé par la garde** (tout intrus doit y
   figurer) **et se vide tout seul** (une seconde garde échoue si une entrée
   n'a plus d'objet), donc il ne peut ni grossir en silence ni conserver une
   exemption périmée.

⚠ Ma stèle contenait `app/templates/**` — dont le `/**` **ouvre un
commentaire**. Une garde existante du dépôt (`test_css_comment_delimiters_are_balanced`)
l'a attrapée immédiatement. Reformulé.

Autres retraits, **chacun avec la prose qui le motivait déplacée avec lui** :
`.session-list` / `.session-card*`, `.history-item*` (13 règles — la prose
`TRAIN1-E/C6` est conservée et nomme `UI-CP5` comme ce qui l'a périmée),
`.mission-bridge*`.

**Non dédupliqués, volontairement** : `.band*` et `.cockpit__tally*`, présents
dans `app.css` **et** `home.css` avec un test qui explique pourquoi. La frise
porte un préfixe distinct (`.tband*`), `.band` étant déjà pris.

**Dette résiduelle nommée** : la famille `.insight` / `.insight__reco` est elle
aussi sans consommateur. Elle n'est **pas** retirée ici — aucune garde ne
l'exige, et l'élargissement serait de la dérive. Consignée pour une prochaine
tranche.

---

## 11. Gardes — repointées sur leur propriété, jamais supprimées

14 blocages recensés au plan, tous traités. Les repointages significatifs :

| Garde | Propriété réelle, tenue autrement |
|---|---|
| `test_the_history_row_is_the_primary_action` | *la ligne entière est l'action* → cherche le **jeton** `hroster__link`, jamais une écriture d'attribut |
| `test_the_instrument_carries_no_command…` | *la gestion ne se répète pas par ligne* → **invariant de compte** : 0 formulaire quel que soit le nombre de séances |
| `test_every_history_control_declares_44px` | sélecteurs suivis jusqu'à leurs nouveaux contrôles ; **extraction une par une** conservée (la version « quelque part dans le bloc » laissait passer un contrôle à 26 px) |
| `test_no_count_reaches_the_rank…` | **généralisée** — voir §10 |
| `_exits()` (accueil) | ne s'auto-asserte plus ; lit tous les liens hors héros |
| `test_ui_cp3_mission.py:309` | **assertion inchangée**, contenu re-fondé en stèle |

### ⚠ QUATRE GARDES DE PLUS SONT TOMBÉES AU SWEEP — ET MON INVENTAIRE LES AVAIT TOUTES RATÉES

Le plan recensait 14 blocages. Le **sweep complet en a trouvé quatre autres**,
que ni le relevé par nom ni mes séries ciblées n'avaient vus. C'est la
démonstration la plus nette de ce que vaut un sweep sur un tier `SHARED_CODE`,
et elle mérite d'être écrite plutôt que résumée en « corrigé ».

| Garde | Ce qu'elle pointait | Traitement |
|---|---|---|
| `test_ownership.py::test_history_does_not_show_other_user_sessions` | ancre `session-card__name` — **une garde d'APPARTENANCE**, donc de sécurité | repointée sur `hroster__name`, **compte exact `== 1` conservé** : zéro dirait aussi bien « rien ne fuit » que « la sonde ne lit plus rien » |
| `test_ui_surface_guards.py::test_the_summary_inventory_does_not_rot` | `ui_surface_inventory.json` gardait `target_closure.css::.history-item__toggle` pour une règle retirée | entrée supprimée. La garde dit exactement pourquoi : *« elles autorisent d'avance un défaut futur »* |
| `test_weekly_loop.py::…no_longer_renders_the_weekly_container` | cherchait le jeton `top_anomaly` dans `progress.html` | repointée sur `debrief_signal.html` — **le porteur change, l'invariant non**. Épingler l'ancien nom reviendrait à exiger son retour |
| `test_session_management.py::test_history_has_management_actions` | exigeait les commandes **sur chaque ligne** de `/history` — ce que la tranche retire | **scindée en deux**, la capacité sur `/admin/sessions` et le chemin sur `/history`. Et la conjonction `or` qui cachait laquelle des deux étiquettes on exige est levée (`S9073`) |

### ⚠ ET UNE VRAIE SOUSTRACTION SEULE, ATTRAPÉE PAR UNE GARDE

`test_science_page.py::test_science_is_reached_from_the_question_not_from_the_home`
est tombé avec : *« `/science` n'est plus atteignable que depuis
`['coach_report.html', 'session_detail.html']` — une zone d'archive sans entrée
contextuelle est une page orpheline »*.

**Elle avait raison.** `/progress` portait une entrée vers `/science`, accrochée
à la tuile « score moyen exercices (30 j) » — « Comment c'est calculé → ».
Cette tuile part avec « Rythme récent » (§4), et **j'ai emporté l'entrée avec
elle sans la replacer**. C'est `§5.3` au sens littéral : une soustraction seule.

L'entrée est rétablie **dans la divulgation « Comment AUREN choisit ce qu'il
montre en premier »**, et elle y est mieux placée que là où elle était : la
garde exige qu'on atteigne `/science` « depuis l'endroit où la question se
pose ». Une tuile de score ne posait aucune question ; ce paragraphe explique
comment le signal de tête est choisi, et la règle des plages de répétitions est
précisément celle qui déclenche le « reps sous la cible » que le L1 rend.

*Deux tranches de suite, c'est une garde du dépôt — pas ma relecture — qui a vu
la soustraction.*

#### Et le remplacement a introduit son propre défaut, qu'AUCUNE garde ne voit

En vérifiant une affirmation de ma propre PR — « cibles < 44 px : **0** » — j'ai
mesuré `/progress` et trouvé **une** cible à **18 px** : le lien vers `/science`
que je venais d'ajouter.

**Aucune garde du dépôt ne pouvait le voir** : l'inventaire
`ui_surface_inventory.json` se dérive de la **feuille de style**, pas de la
géométrie rendue, et un lien en prose n'y apparaît pas. Le sweep était vert, et
il avait raison de l'être.

Le lien vit seul dans son paragraphe : il reçoit le plancher de 44 px
(`.rule-entry`), qui ne coûte rien à la lecture. Mesuré après : **0** cible sous
44 px sur `/progress` **et** `/history`, sur trois comptes.

⚠ **Et le premier nom de cette classe était fautif.** Je l'avais appelée
`.signals__how-rule` — un nom qui contient la sous-chaîne `signals__how`, si
bien qu'une garde comptant les divulgations partagées en a vu **deux** : « il
doit y avoir exactement une divulgation partagée ». La garde avait raison de
compter ; c'est le nom qui rendait le compte indécidable. Un modificateur qui
préfixe le nom d'un autre objet est illisible pour tout compteur textuel.

### Gardes neuves — 22, dont trois vérifiées par **mutation**

* **`test_le_signal_d_attention_vient_de_la_derniere_seance_pas_de_la_plus_ancienne`** —
  vérifiée **sans rien planter** : le défaut est déjà dans le dépôt. Brancher
  `_pick_top_anomaly` rend `"D"` au lieu de `"B"`. Rouge cité ici comme preuve.
* **`test_le_rang_souverain_appartient_au_l1_quel_que_soit_le_signal`** — le
  défaut d'origine replanté **en entier** la rend rouge (`rows=[]`, le
  mouvement disparu).
* **`test_le_mouvement_demis_perd_son_rang_mais_pas_son_existence`** — idem.
* **La rareté est un cas paramétré**, jamais latéral : les **cinq** corpus, avec
  `causes != ()` **toujours**.

⚠ **Mon harnais de mutation a d'abord menti.** Patché à
`pytest_sessionstart`, il était écrasé par le `conftest`, qui repeuple le module
avant le test : la garde rendait « verte » alors qu'elle n'avait jamais vu le
défaut. Déplacé à `pytest_runtest_call`, elle est rouge. *Neuvième forme de
« mesurer le mauvais objet » — cette fois dans l'instrument de mesure.*

---

## 12. Hors périmètre, tenu (§14)

Aucun système de graphiques global · aucun nouveau moteur d'anomalie ou de
score · aucune migration globale de cards · aucune refonte de coque ·
`/science` intouché · aucune politique de recommandation ·
`recommendation.py` **intouché** · aucun framework générique de chronologie —
la frise est un objet fermé sur **une** surface, et le rail 14 j de `/progress`
reste tel quel · `.limit(100)` et l'absence de pagination conservés · CSRF hors
sujet, **et dit**.

---

## 13. Contrôles

| Contrôle | Résultat |
|---|---|
| `check_scope.py` | **`SHARED_CODE`** |
| `ruff` (fichiers touchés) | **vert** |
| `check_ruff_budget.py` | **267 / 548** |
| `check_spec_protocol.py` | **vert** |
| pré-scan `S9073` / `S1764` | **aucune assertion composite neuve** (une, de ma main, corrigée) |
| cliquet styles en ligne | **vert**, les deux gabarits à **zéro** |
| sweep local complet, arbre **gelé** | **lancé**, verdict en avenant. ⚠ Le premier sweep a été **arrêté et relancé** : il avait commencé sur un arbre que mes correctifs modifiaient en cours de route, et un sweep sur arbre mixte ne mesure rien |
| `test_v1_acceptance.py` (4 rouges locaux) | **hors sujet et pré-existant** — il vérifie une configuration VSCode locale (`.vscode/` est gitignoré) et il est **délibérément exclu** de `run_ci_pytest.sh` **et** de `run_local_sweep.sh` |
| **Portail visuel `§5.1`** | **4 états rendus + l'état sélectionné**, soumis à l'opérateur |

---

## 14. Ce qui reste à trancher par l'opérateur

1. **`ATTENTION` n'occupe pas la fente 32 px** (§4). Écart assumé au plan, avec
   sa raison. Alternative si refusée : exposer une grandeur structurée depuis le
   détecteur d'anomalies — ce qui est une tranche à part entière.
2. **La famille `.insight` reste morte** dans `app.css` (§10).
3. **`.user-profile__name` reste à 24 px**, inscrit comme dette (§10).
4. **Le détecteur d'anomalies tourne deux fois par chargement de `/progress`**
   (§2). Le plan annonçait l'inverse ; deux gardes l'empêchent dans ce
   périmètre. À résorber dans une tranche qui possède le contrat de
   `weekly_loop` et son consommateur `narrative.py`.

---

## AVENANT POST-MERGE — closeout

**Mergée le 2026-09-21.** PR **#240**, méthode `--merge` avec SHA de tête
épinglé (`bb6f500`), commit de merge **`21e74d0`**. Aucun squash, aucun
`--admin`, aucun force.

### Les six portes, revérifiées juste avant le merge

| Porte | État |
|---|---|
| SHA de tête connu et inchangé | `bb6f5002a2e1365b4066d10981617f740476a405` |
| Tous les contrôles requis | **9/9 pass**, dont le gate **externe** `SonarCloud Code Analysis` |
| Gate Sonar, par API | **`status: OK`**, 5/5 conditions |
| Threads de revue non résolus | **0** |
| `mergeable` / `mergeStateStatus` | `MERGEABLE` / `CLEAN` |
| Dérive de périmètre | aucune |

### CI canonique sur le commit de merge — la source de vérité

Run **35641762351**, `conclusion: success`, **7/7** :
`canonical attestation` · `lint` · `pytest shard 1/2/3` · `pytest + QA scripts`
· `SonarCloud`.

Aucun rouge d'infrastructure cette fois — contrairement au closeout de `UI-CP4`,
où sept contrôles étaient sautés derrière la dette `actionlint` / node20. Cette
dette a été fermée par `Sb_CI_NODE24_RUNTIME_01` (PR #235).

### Qualité du nouveau code

| Condition | Valeur | Seuil |
|---|---|---|
| `new_coverage` | **98,2 %** | ≥ 80 |
| `new_duplicated_lines_density` | **0,0 %** | ≤ 3 |
| `new_bugs_severity` | **0** | ≤ 9 |
| `new_code_smells_severity` | **0** | ≤ 14 |
| `new_vulnerabilities_severity` | **0** | ≤ 9 |

### L'incident Sonar, et ce qu'il dit de ma méthode

Le gate a été **rouge au premier passage**, sur `new_code_smells_severity = 15`
pour un seuil de 14. L'arithmétique tranchait avant toute recherche — MAJOR pèse
15 — donc **une** finding, et une seule : `external_ruff:I001` sur
`tests/test_train1e_surface_hygiene.py:136`, une ligne vide qui coupait un bloc
d'imports en deux.

⚠ **La faute est en amont, et elle est de méthode.** J'avais lancé `ruff` sur une
**liste de fichiers écrite à la main** — ceux que je croyais avoir touchés —
plutôt que sur le diff. Ce fichier n'y figurait pas. La commande juste dérive sa
liste de `git diff --name-only`, et c'est celle qui a vérifié le correctif.

⚠ **Et le job interne `SonarCloud` passait pendant que le gate externe
échouait.** Les deux ne disent pas la même chose ; c'est l'**externe** qui est
l'autorité de merge. Un closeout qui ne regarderait que le job interne
conclurait faux.

### Ce que cette tranche laisse derrière elle

Rien de bloquant. Quatre points sont consignés au §14 ci-dessus, dont **un
arbitrage qui appartient à l'opérateur** — le rang de la réponse sur l'état
`ATTENTION` — et **une dette de coût nommée**, la double exécution du détecteur
d'anomalies sur `/progress`.

**Déploiement en production : non fait dans ce closeout.** Il reste une décision
séparée.
