# `UX4_02` / TRAIN 2 — tranche A : **Mon plan**

`OPERATOR_DECISION` C8 · branche `sb/train2-programs-discovery` · base `709b194`

---

## 1. Ce que cette tranche fait

Trois objets répondaient à la même question et vivaient sur deux écrans qui ne
la posaient pas :

| Objet | Où il vivait | Question à laquelle la surface répondait |
|---|---|---|
| La **déclaration** d'entraînement | Profil, niveau 2 | « Qu'est-ce qu'AUREN sait de moi ? » |
| Le **plan** qui en découle | Mes programmes | « Qu'est-ce que j'ai créé ? » |
| **« Pourquoi ce plan ? »** | Mes programmes | idem |

Aucun des trois ne pouvait se lire à côté des deux autres. On voyait un plan
sans pouvoir voir ce dont il découlait ; on modifiait une déclaration sans voir
ce qu'elle produisait.

Ils sont réunis sur **`/plan` — « Mon plan »**, dans l'ordre de la
lecture : ce que tu as déclaré → le plan → pourquoi ce plan → modifier la
déclaration.

**Rien n'est supprimé. Rien n'est dupliqué. Rien n'est deviné.**

---

## 2. Brainstorming / Options / Risques / Choix retenu (`CLAUDE.md §3`)

### Le problème posé par C8

> *« contextualized discovery over a common 13-template corpus, **no opaque
> recommendation engine**, use explicit plan context only, build My Plan / My
> Programs / Explore »*

La contrainte dure est **« contexte de plan explicite uniquement »**. Elle
interdit d'inférer ce que l'utilisateur veut : le produit ne peut utiliser que
ce qui a été **déclaré**. Or au démarrage de la tranche, la déclaration était la
chose la plus difficile à trouver du produit — trois écrans plus loin que le
plan qu'elle gouverne.

### Options examinées

**Option A — `/plan` réunit déclaration + plan + explication.** *(retenue)*
Un seul écran répond à « comment je veux m'entraîner ». La déclaration est
lisible en tête, le plan juste après, l'explication ensuite, l'éditeur en pied
derrière un geste.
· *Pour* : la boucle déclarer → voir → ajuster tient sur une surface. Le
contexte explicite exigé par C8 devient **visible**, pas seulement respecté.
· *Contre* : une surface de plus dans un onglet qui en a déjà deux.

**Option B — enrichir « Mes programmes » sans nouvelle surface.**
Ajouter la déclaration à l'écran qui portait déjà plan + explication.
· *Pour* : zéro nouvelle route.
· *Contre* : la surface répondrait alors à **deux** questions — exactement le
défaut que TRAIN 1 a passé quatre tranches à retirer d'ailleurs. Rejetée.

**Option C — garder l'éditeur sur le Profil, ne déplacer que le plan.**
· *Pour* : diff minimal.
· *Contre* : contredit C2 (« la configuration persistante quitte le niveau 1 du
Profil, attend TRAIN 2 / Mon plan »), et laisse la déclaration séparée de son
effet. Rejetée.

### Risques identifiés avant d'écrire, et ce qui les couvre

| Risque | Couverture |
|---|---|
| Le formulaire est **dupliqué** (deux éditeurs divergent en silence) | garde sur l'ARBRE de gabarits : exactement un hôte |
| Un **contrat de soumission** bouge (route, nom de champ) | route inchangée · noms vérifiés **sur le rendu**, pas sur la source |
| Un plan apparaît **sans déclaration** — le moteur opaque interdit | garde comportementale sur le producteur ET sur la page |
| Le plan **revient** sur « Mes programmes » | garde d'absence, maintenue sur `/programs` |
| Le déménagement **perd** un bout en route | garde sur les options offertes ; trois pertes réelles trouvées, voir §4 |

### Choix retenu

**Option A.** La surface qui répond à « comment je veux m'entraîner » existe et
porte les trois objets. `/programs` est recentrée sur « ce que j'ai créé ».

---

## 3. Ce qui a changé

| Fichier | Nature |
|---|---|
| `app/templates/user_programs/plan.html` | **neuf** — les trois objets réunis |
| `app/routers/user_programs.py` | route `/plan` (`user_plan`) + sentinelle `_NO_PREFERENCES` ; `/programs` allégé |
| `app/routers/auth_routes.py` | redirections de préférences → `/plan` ; contexte Profil purgé |
| `app/templates/profile.html` | l'éditeur et sa mention transitionnelle partent |
| `app/templates/user_programs/list.html` | proposition + explication partent |
| `app/templates/base.html` | `is_plan` ; l'onglet Programmes groupe ses trois destinations |
| `tests/test_train2_mon_plan.py` | **neuf** — 20 gardes |
| 5 fichiers de tests existants | retargetés sur la nouvelle adresse (§5) |

**Contrats délibérément intacts** : la route `POST /profile/preferences`, les
noms de champs `sessions_per_week` / `focus_1..3` / `equipment` /
`equipment_declared`, la sémantique `NULL ≠ []`, la route
`user_program_from_weekly_plan`. Un déménagement de formulaire ne justifie pas
de rompre un contrat de soumission.

---

## 4. Trois défauts que seule la mesure a trouvés

### 4.1 — L'éditeur rendait **zéro option**, sans une erreur

Les vocabulaires `sessions_range`, `focus_vocab` et `equipment_vocab` sont du
**contexte de route**. Déplacer le gabarit ne les déplace pas. Oubliés, Jinja
itère sur `Undefined` **sans lever** : le formulaire rendait ses trois légendes
et pas une seule case à cocher.

Le piège d'instrumentation qui allait avec : ma première garde cherchait
`name="sessions_per_week"` dans la **source** du gabarit. Il n'y est pas — les
`<input>` sortent des macros `choice_row` / `select_shell`. Elle accusait un
renommage inexistant tout en étant incapable de voir un vrai renommage dans la
macro. La garde lit désormais le **rendu**, et compte les **options offertes** :
les trois menus `focus_N` viennent d'une boucle sur le littéral `[1, 2, 3]`,
donc leurs `name` survivent intacts à un vocabulaire absent — seules les
options disparaissent.

Mesuré après correction : **7 cadences · 6 familles de matériel · 18 options de
priorité**.

### 4.2 — Le déménagement du plan n'était pas verbatim

Trois choses manquaient à l'arrivée, et les tests existants les ont nommées :

* la branche de **statut** — « Proposition partielle — 7 zones restent sous le
  volume visé » et la liste des contraintes non programmables ;
* la phrase « Crée un **brouillon** modifiable. Rien n'est publié ni lancé sans
  ton accord. » ;
* le libellé du bouton, que j'avais réécrit en « Créer ce programme ».

La première est la **mécanique d'honnêteté** de la proposition : sans elle, un
plan partiel s'annonce comme complet. Restaurées à l'identique.

### 4.3 — Une phrase qui promettait en montrant l'absence

Sur un compte vierge, la carte d'édition disait *« Ce que tu déclares ici — et
rien d'autre — produit le plan **ci-dessus** »*, alors qu'au-dessus se trouvait
la ligne « Aucun plan proposé ». La phrase pointait vers un objet inexistant.
Elle suit désormais l'état : *« produira le plan proposé »* tant qu'il n'y en a
pas. **Vu à l'écran, pas dans le gabarit** — c'est précisément ce que `§5.1`
existe pour attraper.

---

## 5. Vingt-trois tests existants pointaient l'ancienne adresse

Le sweep ciblé a rendu **23 rouges** — tous le même fait : des gardes qui
vérifient l'éditeur de préférences ou la proposition hebdomadaire **là où ils
étaient**. Aucune n'est un défaut produit ; aucune n'a été affaiblie ni
supprimée.

Deux de ces gardes **nommaient TRAIN 2 comme ce qui les rendrait caduques** :

> *« L'emplacement reste déclaré transitionnel — c'est `TRAIN2` qui lui donne
> son domicile. »* — `test_ux4_profile_acquisition`
> *« Elle répond à « comment je veux m'entraîner », qui est la question de Mon
> plan. `TRAIN2` lui donne son domicile. »* — `test_train1d_epistemic_convergence`

Traitement, fichier par fichier :

| Fichier | Traitement |
|---|---|
| `test_ui_profile_preferences.py` | `PROFILE_URL` → `EDITOR_URL = "/plan"` — 15 assertions inchangées |
| `test_training_preferences.py` | `PROFILE_URL` → `CAPTURE_URL = "/plan"` — 9 appels, assertions inchangées |
| `test_ux4_profile_acquisition.py` | la garde vérifie maintenant les **deux** moitiés du déménagement ; l'unicité de l'éditeur se compte sur l'**arbre de gabarits**, plus sur un seul fichier |
| `test_weekly_plan_materialization.py` | `TestUserSurface` suit la surface **et gagne** une garde : la proposition n'est pas *restée* sur `/programs` |
| `test_train1d_epistemic_convergence.py` | la garde suit l'adresse ; sa jumelle vérifie le départ du Profil |

**Un seuil a bougé** : `test_every_acquisition_form_sits_behind_an_explicit_update`
passe de `>= 3` à `>= 2` formulaires sur le Profil, l'éditeur étant parti. Ce
n'est pas un assouplissement de la règle — la règle est l'invariant
`disclosures >= acquisition`, inchangé, et il vaut aussi sur `/plan` (garde
jumelle : l'éditeur y est derrière un `<details>` fermé). Le seuil reste un
cliquet contre une disparition silencieuse.

---

## 6. Gardes plantées

Chaque garde structurante a été vérifiée **en plantant son défaut**. Une garde
qu'on n'a jamais vue rouge ne garde rien — ce dépôt en a compté vingt.

| Défaut planté | Garde | Verdict |
|---|---|---|
| `sessions_range` retiré du contexte | options offertes | 🔴 |
| `focus_vocab` retiré du contexte | options offertes | 🔴 |
| `equipment_vocab` retiré du contexte | options offertes | 🔴 |
| `sessions_per_week` renommé dans la macro | noms de champs | 🔴 |
| classe active sur le mauvais onglet | accord des deux marqueurs | 🔴 |
| `aria-current` sur le mauvais onglet | accord des deux marqueurs | 🔴 |
| `is_plan` désactivé | onglet allumé | 🔴 |
| Progression s'allume aussi sur `/plan` | onglet unique | 🔴 |
| la proposition revient sur `/programs` | garde d'absence | 🔴 |
| le plan se propose sans déclaration | cœur de C8 | 🔴 |
| l'explication cesse de citer ses sources | sources nommées | 🔴 |
| l'enregistrement renvoie sur le Profil | redirection | 🔴 |
| la déclaration perd son titre | les trois objets | 🔴 |
| un second éditeur sur le Profil | unicité produit | 🔴 |
| l'URL de Mon plan change | surface servie | 🔴 |

**Deux mutations ont d'abord été trop faibles** et sont documentées comme telles :

* changer la classe `is-active` laissait la garde verte, parce qu'elle ne lisait
  que `aria-current`. Le gabarit pose les deux marqueurs par **deux conditions
  Jinja distinctes** : ils peuvent diverger, et alors l'œil voit un onglet
  pendant que la synthèse vocale en annonce un autre. La garde exige désormais
  leur **accord**, ce qui a rendu les deux mutations rouges ;
* mon script de plantation remplaçait la **première** occurrence du motif, qui
  se trouvait dans le rail de navigation haut, pas dans la barre basse mesurée.
  Corrigé en scindant le gabarit sur `class="app-bottom-nav"` d'abord.

---

## 7. Exposition §5.1 — rendus réels

Serveur de lab sur le worktree, base de bac à sable, comptes **déclaré** (uid 3,
cadence 4/sem · priorités Dos largeur + Bras · 3 familles) et **vierge** (uid 1).
Le plan du compte déclaré a été matérialisé **par le bouton réel** : sans traces
de décision, « Pourquoi ce plan ? » ne s'instancie pas, et l'exposition
n'aurait rien prouvé sur le troisième objet.

| Surface | Compte | Écrans (390) | Mots | Cartes | Déclaration | Plan | Pourquoi | Éditeur |
|---|---|---|---|---|---|---|---|---|
| `/plan` | déclaré | 2,1 | 243 | 3 | ✅ | ✅ | ✅ | ✅ |
| `/plan` éditeur ouvert | déclaré | 3,4 | 359 | 3 | ✅ | ✅ | ✅ | ✅ |
| `/plan` | vierge | 1,0 | 54 | 1 | ✅ (3× « À déclarer ») | — *dit* | — | ✅ |
| `/programs` | déclaré | 1,0 | 12 | 1 | — | — | — | — |
| `/programs` | vierge | 1,0 | 8 | 0 | — | — | — | — |
| `/profile` | les deux | 1,4 – 1,6 | 86 | 3 | — | — | — | — |

Mesuré à **360×800 · 390×844 · 430×932**, sur les deux comptes :

* **0 débordement horizontal** sur les 20 rendus ;
* **0 tiret nu**, **0 carte quasi vide** ;
* **0 cible tactile < 44 px dans `<main>`** — les seules restantes sont
  `topbar__brand` (45×21) et `foot__contact` (51×18), chrome préexistant, hors
  du périmètre C6 arbitré (« tiens-toi à l'historique ») ;
* l'onglet **Programmes** est allumé sur `/plan` et `/programs`, et lui seul.

**Un piège de mon propre instrument, corrigé** : la première passe comptait
2 cibles fines sur une page et 3 sur une autre plus courte. `elementFromPoint`
ne teste que le **viewport** — tout contrôle sous la ligne de flottaison rendait
`null` et sortait du compte **sans le dire**, faisant paraître une page longue
plus propre qu'une page courte. Le recensement final amène chaque candidat dans
le viewport avant le test de frappe, `<details>` ouverts.

---

## 8. Relecture du relevé de décisions (`CLAUDE.md §5.2`)

`docs/DESIGN_DECISIONS_UIV2_SURFACES.md`, décision par décision :

| Décision | Verdict |
|---|---|
| **Q1** — la connexion porte l'identité | non concernée |
| **Q2** — ancre visuelle de l'accueil | non concernée |
| **Q3** — « État du jour » replié | non concernée |
| **Q4** — la ligne de série devient un instrument | non concernée |
| **Q5** — les surfaces, trois rangs | ⚠ **violée par héritage** — voir ci-dessous |
| **Tokens bleus** | respectée — aucune couleur introduite, aucun hex écrit |
| **Convergence Gravl → Auren** | non concernée |
| **Ordre de livraison** | respectée — C8 est la tranche ordonnancée par l'opérateur |

**Q5, en clair.** Le relevé dit : rang 1 actionnable = carte bordée ; rang 2
informatif = filet ou module compact ; rang 3 ambiant = aucun conteneur.
Sur `/plan` :

* « Ce que tu as déclaré » — pas de conteneur, rang 2/3. ✅
* « Aucun plan proposé » — `empty-line`, rang 3. ✅
* « Programme proposé » — carte bordée, contient l'action primaire, rang 1. ✅
* Préférences — carte bordée, contient le formulaire, rang 1. ✅
* **« Pourquoi ce plan ? » — carte bordée, alors que c'est un objet purement
  informatif (rang 2).** ❌

Cette carte arrive **telle quelle** de « Mes programmes » : le manquement est
antérieur au déménagement, et le corriger serait un **changement d'apparence**
qui dépasse une tranche de déplacement. Il est consigné ici, non maquillé, et
proposé comme arbitrage : trois cartes bordées sur un écran de 2,1 écrans
approchent le seuil que Q5 nomme — *« une carte qui entoure tout n'entoure plus
rien »*.

Autres règles du contrat UI :

* **§5.1** — rendus produits et exposés avant commit ✅
* **§5.3 jamais une soustraction seule** — les trois objets retirés de deux
  surfaces arrivent sur une troisième **dans la même livraison** ✅
* **§5.4 toute couleur est un token** — aucune couleur introduite ✅
* **§5.5 centralité avant facilité** — la déclaration est l'entrée la plus
  centrale de C8 ; elle passe avant « Explorer », qui est la tranche B ✅

---

## 9. Vérifications (`CLAUDE.md §1`)

`check_scope` classe le diff **`ISOLATED`**. **Verdict remonté d'un cran à la
main** : `base.html` est la coque de **toutes** les pages et le contexte de
`/profile` change — c'est un rayon d'effet partagé, et `§1` dit de remonter en
cas de doute, jamais de descendre. C'est le même écart que celui déjà consigné
pour `exercise_properties` (`Sb_MORPHO_*`).

| Vérification | Résultat |
|---|---|
| `check_scope.py` | `ISOLATED` → traité en `shared_code` |
| Sweep ciblé, 14 fichiers consommateurs | **420 passés, 0 échec** |
| `tests/test_train2_mon_plan.py` | **20 passés** |
| ruff (rapport CI reproduit, `--output-format=json`) | **276 avant, 276 après** — aucune régression |
| `check_ruff_budget.py` | OK (276 ≤ 548) |
| `check_spec_protocol.py` | OK |
| Pré-scan AST S9073 / S5863 / S1192 | 0 nouveau ; littéral `/profile/preferences` hissé en constante |
| `Web:S6819` | corrigé avant push — `role="status"` → `<output>` |

---

## 10. Ce que cette tranche ne fait pas

* **Explorer** (`/library` contextualisée) — tranche B, non commencée. La
  conception est arrêtée : `WorkoutTemplate.focus` est du **texte libre**, donc
  un appariement gabarit ↔ priorité serait flou — interdit par C8. `WeeklyPlan`
  raisonne au niveau **zone** (`ZoneCoverage`, `ExercisePrescription`), pas
  gabarit. La voie honnête est d'annoter chaque gabarit des zones qu'il couvre
  via le `resolve_zone` canonique, et de relier cette annotation au plan
  **déclaré**.
* Aucun changement de moteur : `weekly_planner`, `orchestrator_explainer`,
  `training_preferences` sont lus, jamais modifiés.
* Aucune migration. Aucune écriture de schéma.

---

## 11. Closeout post-merge

| | |
|---|---|
| PR | **#161** |
| Merge | **`6a5bb68`** — `--merge`, tête épinglée `a80041d`, **pas de squash, pas de `--admin`, pas de force** |
| Mergée le | 2026-08-25 15:30 UTC |
| CI de PR | 8/8 `pass` |
| CI canonique (`push` sur le merge) | run **32866883846** — **6/6 succès** |
| Sonar (gate PR) | **OK** — couverture neuve **93,3 %** · 0 bug · 0 code smell · 0 vulnérabilité · duplication 0,0 % |
| Fils de revue non résolus | 0 |

### L'incident du cycle rouge, et ce qu'il apprend

Un cycle CI rouge, **un seul échec, dans ma propre garde** — pas dans le
produit.

`test_the_submit_route_is_unchanged` lisait `app.main.app.routes` sans prendre
la fixture `client`. Verte en local, rouge sur le shard 1, où la table ne
contenait que les routes par défaut de FastAPI :

```
assert '/profile/preferences' in {'', '/api/docs', '/docs/oauth2-redirect',
                                  '/openapi.json', '/static'}
```

La cause est la fixture elle-même : elle **purge tout `app.*` de
`sys.modules`** puis réimporte. Un test qui lit l'état global d'un module sans
posséder ce cycle de vie lit **une génération d'application qui n'est pas la
sienne** — et l'ordre des tests décide alors du résultat, ce qui diffère entre
un fichier lancé seul et un shard. Le dépôt connaît déjà ce piège : faux échecs
d'identité d'enum entre deux générations, invisibles hors full sweep.

Ce n'était donc pas rattrapable par un sweep local plus large : c'est le
**partitionnement** de la CI qui expose la dépendance d'ordre.

La garde POSTe désormais sur la route et exige un `303`. Un `404` est de toute
façon le **vrai symptôme** d'un contrat de soumission rompu — plus proche du
signet cassé que l'inspection d'une table de routage. Vérifiée en plantant le
renommage de la route : rouge. Les deux autres gardes du fichier qui touchent à
l'application prennent déjà `client` ; les autres lisent des fichiers sur
disque.

**Règle à retenir** : dans ce dépôt, une garde qui inspecte l'état global d'un
module d'application **doit** prendre la fixture qui en possède le cycle de
vie, ou se poser sur le comportement.

### Reste ouvert

* **Arbitrage Q5** (§8) — « Pourquoi ce plan ? » en carte bordée pour un objet
  de rang 2. Trois cartes bordées sur 2,1 écrans.
* **Tranche B — Explorer** : conception arrêtée, non commencée (§10).
