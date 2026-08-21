# `UX4_03B_BEHAVIORAL_CONSUMER_ALIGNMENT`

**Statut : LIVRÉ, non commité au moment de la rédaction.** Le §3 (Brainstorming
/ Options / Risques / Choix) occupe les sections 1 à 4 et **précède** le code,
comme l'exige `CLAUDE.md §3`. Les décisions opérateur sont au §5, le livré au
§7.

---

## 1. Ce que la mesure dit, contre ce que j'avais enregistré

Le registre ouvert au closeout d'`UX4_03` classait quatre défauts. **Trois des
quatre entrées étaient inexactes**, et une correction en amont vaut mieux qu'un
sprint construit sur elles.

| # | Ce que j'avais écrit | Ce que la mesure dit |
|---|---|---|
| **B1** | « `readiness_score` … un compte sans données rend 25,0 » | **Vrai sur le calcul, faux sur l'exposition.** `behavioral.readiness_score` n'est rendu **nulle part** — aucun gabarit ne lit `behavioral.*` |
| **B2** | « Streak rendu dans le rapport coach » | **exact** — `coach_report.html:62`, seul défaut réellement à l'écran |
| **B3** | « `compute_recommendation` écrit *Série en cours* — **rendu en prose** » | **faux.** La chaîne vit dans `BehavioralState.recommendation`, passée à `profile.html`, **qui ne la lit pas** |
| **B4** | « trois cartes vides de `weekly_loop` » | exact, et **inchangé** par cette tranche |

### 1.1 — La collision de noms qui m'a induit en erreur

L'Accueil rend bien un bloc « readiness » : `readiness_today`, alimenté par le
modèle `ReadinessEntry` — **le questionnaire que l'utilisateur remplit**. Ce
n'est pas `behavioral.readiness_score`, qui est un composite dérivé.

`home_training_state.py:36-46` **avait documenté cette collision** et prévenu
qu'elle produirait exactement ce type de confusion. Je l'avais lue, citée, et
je m'y suis quand même fait prendre en lisant une ligne de tableau plutôt que
le code.

### 1.2 — Le vrai défaut est plus large que B1

En cherchant les consommateurs, j'ai trouvé autre chose :

```
auth_routes.py:430   behavioral = compute_behavioral_state(db, user.id)
auth_routes.py:524   "behavioral": behavioral,      → profile.html
profile.html         ne lit AUCUN champ de `behavioral`
```

`UX4_01` a retiré les modules analytiques du Profil sans retirer le calcul qui
les alimentait. **Chaque affichage du Profil exécute donc cinq requêtes et un
chargement de séances pour un objet que personne ne lit.**

Les consommateurs **vivants** de `BehavioralState` ne lisent qu'un seul champ :

| Consommateur | Champ lu |
|---|---|
| `recommendation.py:402` | `fatigue_score` |
| `training_state.py:243` | `fatigue_score` (via `normalize_legacy_fatigue`) |
| `auth_routes.py:524` | **aucun** — l'objet est passé, jamais lu |

`consistency_score`, `trend_direction`, `streak_days`, `readiness_score` et
`recommendation` ne sont donc lus que par `compute_recommendation`, dont la
sortie n'atteint aucun écran.

> **Le composite dangereux existe, et il ne touche personne.** Le risque n'est
> pas actuel : il est **latent**. Le jour où quelqu'un branche
> `readiness_score` sur une surface, il publie un nombre fabriqué — ce que
> `UX4_03` vient précisément de faire avec `fatigue_score`.

---

## 2. Le mur : `behavioral.py` est gelé

`test_no_decision_engine_was_touched` interdit **toute** modification de
`substitution.py`, `recommendation.py` et `behavioral.py` depuis `e8614bd`.

`UX4_03B` vient d'en faire l'expérience : cinq champs additifs y ont été
refusés, à raison.

**Toute suppression de champ mort dans `behavioral.py` exige donc d'amender le
gel.** C'est une décision de contrat, pas un choix d'implémentation — et
`CLAUDE.md §4` en fait un arrêt dur (« conflit de spec »).

---

## 3. Options

### Option A — Périmètre minimal : couper l'alimentation, pas le moteur

Retirer `behavioral` du contexte de `profile.html` et l'appel qui le produit.
Le gel n'est pas touché : `auth_routes.py` est un **routeur**, pas un moteur.

- **Gagne** : supprime cinq requêtes mortes par affichage du Profil, et le seul
  chemin par lequel le composite pouvait ressortir par inadvertance.
- **Ne gagne pas** : `readiness_score` reste calculé.
- **Coût** : très faible. Un routeur, un test.
- **Risque** : nul côté données ; le gel reste intact.

### Option B — A + amender le gel pour retirer les champs morts

Ajouter au gel une exception argumentée, puis retirer `readiness_score`,
`recommendation`, `consistency_score`, `trend_direction` de `BehavioralState`.

- **Gagne** : le composite fabriqué **cesse d'exister**, donc ne peut plus être
  branché par erreur.
- **Coût** : élevé. `test_profile_behavioral` exige explicitement que
  `consistency_score` et `streak_days` **existent encore** — « la capacité a
  été perdue, pas déplacée ». Il faudrait migrer cette garde, donc rouvrir la
  question qu'elle protégeait.
- **Risque** : **affaiblir un gel pour du confort**. Le gel a déjà attrapé un
  vrai défaut cette semaine. L'amender juste après qu'il a servi est
  exactement le mouvement qu'un dépôt discipliné doit refuser sans décision
  humaine explicite.

### Option C — A + fermer B2, le seul défaut réellement à l'écran

Option A, plus le traitement de « Streak » dans le rapport coach.

- **Gagne** : ferme le seul écart **visible par un utilisateur**.
- **Coût** : moyen — et `CLAUDE.md §5.3` interdit une soustraction seule. Le
  retrait doit partir avec son remplacement, qui reste à définir.
- **Risque** : le rapport coach est une surface que je n'ai jamais mesurée.
  Y toucher sans exposition préalable violerait `§5.1`.

---

## 4. Choix recommandé

**Option A maintenant, C ensuite, B seulement sur décision explicite.**

Raisons, dans l'ordre :

1. **A supprime un coût réel et un risque latent sans toucher au gel.** C'est
   le seul des trois qui ne demande aucun arbitrage.
2. **C ferme le seul défaut visible**, mais exige d'abord une exposition du
   rapport coach (`§5.1`) et une décision sur le remplacement (`§5.3`).
3. **B est le plus tentant et le plus dangereux.** Supprimer du code mort est
   satisfaisant ; le faire en désarmant la garde qui vient de rattraper une
   erreur ne l'est pas. Le code mort ne blesse personne aujourd'hui — la garde,
   si.

`§5.5` — la centralité avant la facilité — pousse dans le même sens : B2 est
central (visible), B1 est périphérique (latent). A n'est retenu en premier que
parce qu'il est **sans arbitrage**, pas parce qu'il est facile.

---

## 5. Ce qui bloque, et vous revient

| # | Question | Pourquoi ce n'est pas à moi de trancher |
|---|---|---|
| **D6** | Amende-t-on le gel de `behavioral.py` pour retirer les champs morts ? | Affaiblir un gel est un changement de contrat, et celui-ci vient de prouver son utilité |
| **D7** | Portée de B2 : que remplace « Streak » dans le rapport coach ? | `§5.3` interdit la soustraction seule ; le remplacement est une décision produit |
| **D8** | `readiness_score` : dépréciation visible, comme `recovery_contract:177` l'anticipe ? | Le dépôt l'a nommé « candidate for visible deprecation » sans jamais fixer la date |

### 5.1 — Décisions rendues (2026-08-21)

| # | Décision |
|---|---|
| **D6** | **Oui** — amender le gel avec une exception documentée |
| **D7** | « Streak » du rapport coach → **« N séances · 14 j »** |
| **D8** | `readiness_score` → **marqué déprécié dans le code + registre**, avec garde |

### 5.2 — Une tension entre D6 et D8, résolue plutôt que renvoyée

D6 autorise la suppression de quatre champs, dont `readiness_score`. D8 demande
que ce même champ soit **marqué déprécié avec une garde** — donc qu'il
**reste**. Les deux ne peuvent pas s'appliquer littéralement au même champ.

D8 est la décision **spécifique** à `readiness_score`, D6 la décision générale.
Le spécifique l'emporte. D6 s'applique donc aux champs morts **que rien ne
retient** :

| Champ | Sort | Pourquoi |
|---|---|---|
| `recommendation` | **supprimé** | c'est le défaut B3 — la chaîne « Série en cours » que rien ne rend |
| `trend_direction` | **supprimé** | son unique lecteur est `compute_recommendation`, qui part avec |
| `consistency_score` | **conservé** | entrée de `compute_readiness`, et `test_profile_behavioral` exige son existence |
| `readiness_score` | **conservé, déprécié, gardé** | D8 |

Si cette lecture inverse votre intention sur l'un des quatre, c'est le seul
point à corriger — le reste de la tranche n'en dépend pas.

### 5.3 — Ce que D7 impose avant tout commit

`coach_report.html` est une **surface visible**. `CLAUDE.md §5.1` exige un
rendu réel soumis à l'opérateur **avant** commit. La tranche s'arrêtera donc à
l'exposition, quelle que soit la couleur des tests.

---

## 6. Note de conformité

Le closeout d'`UX4_03` (`ac1210a`) est un commit **100 % `docs/`**. La CI a été
**légitimement skippée** par `paths-ignore: docs/**` (`CLAUDE.md §2`) — ce
n'est pas un `[skip ci]` manuel. La source de vérité pour le code de la tranche
reste la CI canonique **6/6 verte** sur `fc786a2`.

---

## 7. Livré — `UX4_03B` + `UX4_03D`

Deux trains se sont enchaînés dans la même tranche : l'alignement des
consommateurs comportementaux (`B`), puis l'architecture d'information de
Progression (`D`).

### 7.1 — Alignement des consommateurs (`UX4_03B`)

| Décision | Livré |
|---|---|
| **D6** — amender le gel | `behavioral.py` sort du gel *par diff*, remplacé par une garde d'**API** : l'état ne peut plus GROSSIR. `substitution` et `recommendation` restent gelés par diff. |
| **D6** — champs morts | `compute_trend` et `compute_recommendation` supprimés, avec leurs champs. Ce n'était pas du code mort neutre : la seconde lisait un composite fabriqué et écrivait « Série en cours », la chaîne que `DO_NOT_SURFACE` interdit. |
| **D7** — streak du rapport coach | Remplacé par « Séances 14 j ». Mesuré : « Streak 1j » s'affichait pour quelqu'un qui s'était entraîné **cinq fois en quatorze jours**. |
| **D8** — `readiness_score` | Déprécié en place, avec une garde qui épingle l'ensemble exact de ses lecteurs. Un compte sans données rend `25,0`, dont la **totalité** vient du défaut de fatigue. |
| Option A | L'appel mort au moteur retiré du Profil — cinq requêtes par affichage pour un objet que le gabarit ignorait depuis `UX4_01`. |

### 7.2 — Architecture d'information (`UX4_03D`)

L'audit a mesuré, sur `/progress`, **neuf comptages de séances, cinq fenêtres
et deux sémantiques de filtre**. Un couple était en contradiction ouverte.

| Décision | Livré |
|---|---|
| **1** — comptage canonique | `PROGRESSION_SESSION_COUNT = COMPLETED_STAT_ELIGIBLE`. `kpis.sessions_this_week` comptait TOUS les statuts et affichait **3** à côté du **2** de `weekly_loop`, sur la même semaine ISO. Prouvé en semant une séance ouverte. |
| **2** — déduplication | L'objet « Cadence 7 j » retiré : il rendait `3 → 2`, et le rail rend les quatorze jours qui composent ces deux nombres. |
| **3** — fenêtres explicites | « Push A · 2× · cette semaine » contre « Push A · 5 sessions · historique ». La position dans la page ne porte plus la fenêtre. |
| **4** — prose du weekly_loop | Phrase narrative et carte « Hint » retirées du L1. Les producteurs restent ; **dominantes et anomalie sont conservées** — recomposition, pas démontage. |
| **5** — type de séance | Encodé par **texture**, jamais par couleur. Un type inconnu ne reçoit aucune texture : `session_kind()` retombe sur « strength », repli sûr pour un score et mensonge pour un affichage. |

### 7.3 — Le blocage d'accessibilité, et pourquoi il était juste

Le rail est `aria-hidden` — `Web:S6819` avait raison, le compte est déjà rendu
en texte au-dessus. Mais le rail porte **davantage** : répartition des jours,
terminée contre en cours, couverture de l'historique, type de séance.

`build_rail_summary` rédige l'équivalent textuel **à partir des mêmes
`facts.days`** que le rail. Une seule source : la divergence entre ce qu'on
voit et ce qu'on entend devient structurellement impossible. Rendu serveur,
aucun script, `.sr-only`.

Vérifié en pilotant la page servie :

```
l'œil        14 traces · 5 terminées · 1 en cours · 0 hors historique
l'oreille    « Quatorze derniers jours. 5 séances terminées : 08/08, 10/08,
               12/08, 18/08, 20/08. Séance en cours, non comptée : 21/08. »
surface      1 px²
```

**Ce qui reste vrai :** le détail jour par jour n'est pas encore inspectable.
Le niveau 2 du rail reste à construire.

### 7.4 — Deux gardes faibles corrigées en route

- La mienne inspectait **toute** `compute_global_kpis` et restait verte quand
  le filtre disparaissait, parce que `status == "completed"` apparaît ailleurs
  dans le même corps. Resserrée sur la requête visée.
- Une garde du dépôt a rougi sur ma **concaténation de chaînes**, comptée
  comme arithmétique. J'ai reformaté sans `+` plutôt que de l'affaiblir.

### 7.5 — Contrôles

```
check_scope          SHARED_CODE
ruff (py311)         31 findings avant / 31 après — ZÉRO ajouté
check_ruff_budget    281 ≤ 548
check_spec_protocol  OK
full sweep local     5118 passed, 0 échec (25 min, 2 workers)
                     coverage.xml écrit DANS LE WORKTREE
navigateur           /progress re-rendue à 390 px, avant et après
```

| Mesure | avant | après |
|---|---:|---:|
| comptages rendus | 9 | **8** |
| fenêtres distinctes | 5 | **4** |
| sémantiques de filtre | 2 | **1** |
| **faits contradictoires** | **1** | **0** |
| écrans | 2,6 | **2,4** |
| mots | 221 | **198** |
| régions encadrées | 14 | **12** |

### 7.6 — Enregistré, non implémenté

`UX4_03D_ANATOMICAL_EXPOSURE` — prototype d'architecture exposé et accepté avec
six corrections, **aucune implémentation**. L'instrument répond à « où ai-je
travaillé pendant les mêmes quatorze jours ? », sur la géométrie prototype du
dépôt, sans jamais dire *sous-entraîné*, *optimal* ni *N / cible sets* : le
dépôt ne produit que des **bandes de planification** dont l'en-tête précise
qu'aucune littérature ne justifie ses bornes.

Restent ouverts : le niveau 2 du rail · l'instrument PROGRESSIF
(`exercise_history` existe, l'agrégat non) · le PRESCRIPTIF (moteur gelé).
