# `TRAIN1-A` — TEMPORAL_COCKPIT_CLOSURE (A4 + A5 + A11)

**Slice opérateur** : TRAIN 1, première des trois
**Branche** : `sb/train1a-temporal-closure` · **base** : `a71ac24`
**Tier `check_scope`** : `SHARED_CODE`
**État visé** : `TEMPORAL_LAYER = PARETO_CLOSED`

---

## 0. Brainstorming / Options / Risques / Choix retenu

*(CLAUDE.md §3)*

### Ce qui a été mesuré avant d'écrire une ligne

Trois états rendus en HTTP réel, comptés — pas supposés.

**Compte peuplé, avant :**

| Fait | Occurrences sur un même écran |
|---|---|
| comptage de séances | **5** |
| fenêtre temporelle nommée | **12**, sur **5 fenêtres différentes** |
| dominance par programme | **2** blocs (« Séances dominantes » · semaine, « Par programme » · historique) |

`UX4_03D` déclarait la cadence « absorbée par le rail » et retirait l'objet
`Cadence 7 j`. **Elle survivait dans `weekly_loop`** : « 3 séances cette
semaine » + « Semaine précédente : 2 (+1) ».

**Compte vide, avant :** la carte d'en-tête rendait **deux fois la même
phrase** — « Pas encore assez de données cette semaine » comme `volume_signal`
puis comme `data_quality_note` — et « Semaine précédente : 0 » sur un compte
sans historique.

### Un quatrième défaut, trouvé en construisant

`DayTrace` documente **quatre** natures de jour depuis le premier jour, dont
`none` — « hors historique : le compte n'existait pas encore ». La vue-modèle
sait la rendre (classe `rail__c--void`, titre dédié), l'équivalent textuel a sa
phrase.

**Le producteur ne l'a jamais émise.** Un compte créé la veille rendait
**quatorze traces `rest`** : treize affirmations « il pouvait s'entraîner, il ne
l'a pas fait » sur des jours où il n'avait pas de compte.

Trois chemins de code et une phrase de lecteur d'écran étaient morts, et aucune
garde ne l'avait vu — elles éprouvaient `none` via une **fabrique de test**,
jamais via le producteur réel.

### Options pour A11

| # | Option | Verdict |
|---|---|---|
| A | Garder `weekly_loop`, resserrer sa copie | **Rejetée** — `UX4_03D` a déjà fait le correctif le moins cher ; les duplications ont survécu. |
| B | Retirer le conteneur, jeter son contenu | **Rejetée** — l'anomalie est un fait unique. §5.3 : jamais une soustraction seule. |
| **C** | **Retirer le conteneur, absorber ses faits uniques** | **Retenue** = l'ordre opérateur. |

L'absorption s'est révélée plus fine que prévu : la **dominance** n'est pas un
fait unique — « Par programme » la porte déjà, sur une autre fenêtre. Elle
rejoint donc ce bloc en **seconde colonne** plutôt que de disparaître : une
ligne, deux comptes, aucun fait perdu.

---

## 1. Ce qui est livré

### A4 — l'état vide est une ligne, pas l'instrument avec des blancs

Sans aucune trace dans la fenêtre : **une ligne**, `Aucune séance · 14 j`.
Ni signaux, ni rail, ni axe, ni divulgation.

**Aucun CTA.** L'Accueil porte déjà l'appel à démarrer et
`home_training_state` a explicitement refusé de le dupliquer ; le rouvrir ici
rejouerait la duplication que cette tranche ferme. Une garde le vérifie.

**La règle s'applique à l'écran, pas à un bloc choisi.** Vu au rendu réel :
« Rythme récent » affichait encore deux `kpi-card__value` à `—` sur un compte
vide. Un tiret est le rendu de « rien à diviser », pas une mesure. La grille se
réduit à `Aucune séance terminée · 30 j` — **fenêtre de trente jours**, donc
prédicat distinct (`completed_last_30`), pas `has_traces`.

### A5 — le rail devient inspectable, sans nouvelle route

Le rail entre dans un `<details>` dont le `<summary>` **mesure exactement
44 px** et couvre toute la largeur. Les quatorze traces restent décoratives :
en faire des cibles violerait quatorze fois le standard produit.

Le niveau 2 liste les **quatorze jours, du plus récent au plus ancien** —
l'inverse du rail, parce qu'une frise se lit de gauche à droite et une liste du
plus pertinent au moins.

**Lien uniquement sur une séance terminée et identifiable**, vers
`/sessions/{id}/done` — la surface qui existe déjà. **Aucun lien sur un jour de
repos** : un lien qui n'ouvre rien est une promesse. Une séance sans
identifiant reste lisible sans devenir ouvrable — on ne fabrique pas de cible.

`<details>` est le socle SSR, pas un pis-aller : zéro ligne de script. Un
enrichissement interactif viendra **par-dessus**, jamais à sa place.

### A11 — le conteneur part, ses faits uniques restent

| Contenu de `weekly_loop` | Sort | Motif |
|---|---|---|
| `volume_signal` + semaine précédente + delta | **supprimé** | duplication mesurée de « Séances » et du rail |
| `data_quality_note` | **supprimé** | rendait la même phrase que `volume_signal` |
| `hint` | déjà retiré par `UX4_03D` | — |
| **dominance hebdomadaire** | **absorbée** dans « Par programme » | même fait, autre fenêtre → une ligne, deux colonnes |
| **anomalie** | **absorbée** en ligne de l'instrument temporel | fait unique, et **absente quand il n'y a rien** |

`build_weekly_loop` **n'est pas supprimé** : la décision porte sur le conteneur,
pas sur la capacité. Une garde le vérifie.

### Le quatrième défaut, fermé

`_first_known_offset` borne la fenêtre à la création du compte. `none` devient
atteignable depuis le producteur ; les trois chemins morts de la vue-modèle et
la phrase « hors historique » se rendent enfin.

⚠ **La donnée passe avant la borne.** Une séance enregistrée ce jour-là
**prouve** que le compte existait, quoi qu'en dise `created_at` — un import ou
une horloge de travers ne doit pas effacer une séance réelle. La première
écriture testait la borne en premier et **faisait disparaître des séances** ;
une garde tient l'ordre.

---

## 2. Avant / après, mesuré au rendu réel

Densité **visible** — le contenu d'un `<details>` fermé ne se voit pas et est
compté à part.

| | avant | après |
|---|---|---|
| compte vide · mots visibles | 166 | **123** |
| compte vide · cartes | 6 | **2** |
| compte vide · écrans | — | **1,3–1,4** |
| compte peuplé · mots visibles | 268 | **228** |
| compte peuplé · cartes | 9 | **3** |
| compte peuplé · écrans | — | **2,3–2,4** (3,0–3,1 rail ouvert) |
| comptages de séances sur un écran | 5 | **3** |
| blocs de dominance | 2 | **1** |

Aucun défilement horizontal à 360, 390 ni 430. `<summary>` à **44 px** aux trois
largeurs.

### Cibles sous 44 px

Deux sur l'écran vide, trois sur l'écran peuplé : `topbar__brand`,
`foot__contact`, et le lien « Comment c'est calculé → ». **Toutes
préexistantes**, présentes sur chaque page du produit, hors périmètre de cette
tranche.

---

## 3. Exposition visuelle (CLAUDE.md §5.1)

**Neuf écrans entiers** capturés en navigateur réel — jamais un recadrage —
sur deux comptes × trois largeurs, plus le niveau 2 ouvert.

Deux défauts n'ont été vus **qu'en regardant**, et aucune mesure ne les aurait
signalés :

1. **« Par programme » se cassait à 390 px** — « 1× cette sem. » s'écrasait
   contre le nom du programme et contre « 2 sessions ». Les deux comptes sont
   désormais empilés et alignés à droite.
2. **La divulgation « Comment AUREN calcule ces signaux » se rendait sur
   l'écran vide** — elle proposait d'expliquer des signaux qui n'étaient pas
   affichés. Rattachée à l'instrument.

Et un troisième, lu dans le texte de cette divulgation : elle décrivait encore
**« Cadence 7 j »**, objet retiré par `UX4_03D` — une explication d'un signal
absent de l'écran depuis deux tranches. Elle décrit maintenant les quatorze
traces.

### Un piège de cascade, évité de justesse

Le correctif de « Par programme » a d'abord été écrit près du bloc du rail
(ligne ~1950). Les définitions d'origine de `.template-kpi__count` et
`.template-kpi__name` suivent dans le fichier (ligne ~2270) : **même
spécificité, la dernière gagne**. Le correctif n'avait aucun effet, et rien ne
l'aurait signalé. Il est écrit dans les règles d'origine.

---

## 4. Relecture du relevé de décisions (CLAUDE.md §5.2)

| Décision | Verdict |
|---|---|
| §5.1 exposition visuelle préalable | **Respectée** — 9 écrans entiers, 3 défauts trouvés à l'œil |
| §5.2 relecture consignée | **Respectée** — ce tableau |
| §5.3 jamais une soustraction seule | **Respectée** — anomalie et dominance partent dans la MÊME livraison que le retrait du conteneur |
| §5.4 toute couleur est un token | **Respectée** — **aucune couleur neuve** ; tout vient de `--fg-dim`, `--border`, `--accent`, `--fg-muted` |
| §5.5 centralité avant facilité | **Respectée** — la duplication temporelle est le défaut central de Progression |
| AMBRE = action / BLEU = système | **Respectée** — le chevron et les liens en `--accent`, les traces en `--fg-muted` ; aucune inversion |
| Cible 44 px = standard produit | **Respectée** — `<summary>` à 44 px mesurés, lignes de lien à 44 px |
| Pas de framework, SSR pur | **Respectée** — `<details>`, zéro ligne de script |

---

## 5. Vérifications

| Contrôle | Résultat |
|---|---|
| `check_scope` | `SHARED_CODE` |
| ruff (fichiers touchés) | `All checks passed!` |
| pré-scan AST S9073 / S5863 | **0 / 0** sur les trois fichiers de test |
| `check_ruff_budget` | 281 ≤ 548 |
| `check_spec_protocol` | PASS |
| Gardes dédiées | **28 passed** |
| **Broad sweep** — 27 fichiers du rayon d'impact | **476 passed** |

### Quatre tests migrés, aucun affaibli

| Test | Ancien invariant | Nouveau |
|---|---|---|
| `test_progress_route_renders_weekly_section` | « le conteneur existe » | conteneur **absent** + ses deux faits présents ailleurs |
| `test_progress_renders_with_empty_db` | « la grille de KPI existe » | ligne compacte présente + **aucun `—`** en valeur |
| `test_progress_kpis_are_scoped` | « un `0` apparaît quelque part » | **rien de l'autre compte** + la page dit qu'elle n'a rien |
| 7 gardes HTTP d'`UX4_03B` | supposaient l'instrument toujours rendu | reçoivent des traces via `_with_traces` |

Le troisième est **renforcé** : chercher un `0` quelconque était un proxy
faible de l'étanchéité — n'importe quel zéro le satisfaisait.

---

## 6. Non-régressions

- **0 nouvelle métrique** — le niveau 2 projette les mêmes `facts.days` ; une
  garde AST interdit tout `BinOp` dans `build_rail_days`.
- **0 nouvelle route** — la troisième marche pointe vers `/sessions/{id}/done`,
  qui existe déjà. Gardes sur `/progress/day` et `/progress/jour`.
- **0 moteur de décision touché.**
- **0 migration, 0 modèle** — sauf `TemplateKPI.week_count`, champ **additif à
  défaut**, rempli par la surface et non par une seconde requête.
- **0 couleur neuve, 0 ligne de script.**
- `build_weekly_loop` et `narrate_week` **intacts**.

---

## 7. Constaté, hors périmètre, non traité

- **« Par programme » et « Activité récente » rendent chacun une carte pleine
  pour dire « Aucune session terminée »** sur un compte vide — le même défaut
  qu'A4 ferme, dans des blocs qui relèvent de **TRAIN1-C** (A6/A7,
  consolidation). Signalé plutôt qu'absorbé en silence.
- **Deux `—` subsistent dans « Rythme récent » sur un compte peuplé sans
  `SetLog`** — « work sets validés » et « score moyen ». Ici le tiret est
  **exact** : il n'y a rien à diviser. Le changer demanderait une décision
  produit sur ce que rend un KPI sans dénominateur.
