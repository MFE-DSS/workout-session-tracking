# `Sb_TRAIN_A_ENVIRONMENT_EXPERIENCE_01` — TRAIN A devient une boucle produit

**Branche** : `sb/train-a-environment-experience` sur canonique `2e8df15`
**Nature** : `RUNTIME_FLOW` / décision servie partagée **et** surface visible.
**Migration** : **aucune** — la colonne existe depuis `x5y0s6t7v18`.

---

## 1. Ce que l'exploration a trouvé avant d'écrire une ligne

TRAIN A a livré en quatre tranches un système d'environnement complet **et
sans utilisateur**. Le closeout de l'activation nommait déjà le trou
principal : *aucune surface n'écrit `available_equipment_items`*.

L'audit de préflight de ce sprint en a trouvé **trois autres**, tous vivants
en canonique.

### 1.1 — Une seconde route de démarrage sans aucun préflight

`app/routers/user_programs.py:1097` — `user_program_start_session` appelle
`instantiate_session` puis committe, **sans** préflight d'environnement et
**sans** matérialisation d'adaptation.

C'est un défaut **de ma main**, au sprint précédent : j'ai câblé
`POST /sessions` et manqué `POST /programs/{id}/sessions/{sid}/start`.
Un propriétaire de programme publié démarre aujourd'hui sans adaptation,
même avec un environnement déclaré. C'est exactement la « famille aux deux
tiers » — une tranche qui s'arrête à ce qu'elle a ouvert.

### 1.2 — `plan_pour_template` ne sait pas refuser

`app/services/environment_activation.py:221-238`. Quand le catalogue rend
`NO_SERVABLE_CANDIDATE`, `plan_de_materialisation` rend `()` — **la même
valeur** que « tout est nativement exécutable ». Le signal de refus est jeté
exactement à la frontière que `create_session` utilise.

### 1.3 — Un `except Exception` autour d'une décision

`app/routers/sessions.py:168` : `except Exception: return 0`. Une panne
technique et « zéro adaptation légitimement requise » rendent le même `0`.
Une séance jugée *adaptable* peut donc démarrer **sans** l'adaptation qui la
rendait servable.

**Ces trois défauts se ferment AVANT d'ouvrir la déclaration.** Donner aux
utilisateurs le moyen d'atteindre un chemin cassé serait pire que le statu
quo, où la porte est inerte.

---

## 2. Brainstorming / Options / Risques / Choix retenu (`CLAUDE.md §3`)

### Option A — comment `START` devient autoritaire

| option | ce qu'elle coûte | verdict |
|---|---|---|
| déduire le refus d'un plan vide | `()` est ambigu — c'est le défaut 1.2 lui-même | **écartée** |
| instancier puis annuler si infaisable | `session_builder.py:82` pose déjà `db.add` ; on créerait pour défaire, et toute fuite laisse une séance orpheline | **écartée** |
| **préflight AVANT instanciation, résultat TYPÉ** | un contrat de plus | **RETENUE** |

Cinq états nommés, **aucun nombre** :

```
NON_APPLICABLE   environnement NULL → chemin hérité, strictement rien
NATIF            prouvé exécutable tel quel
ADAPTABLE        exécutable via substituts autorisés, plan non vide
INCERTAIN        §1.B — non bloquant, aucune adaptation fabriquée
REFUSE           prouvé incompatible → aucune séance n'est créée
```

**Invariant critique.** En `ADAPTABLE`, si le nombre d'adaptations posées ≠
attendu, c'est un **échec** : `db.rollback()` et refus. Une matérialisation
partielle ne se committe jamais comme un succès.

**Fail-open borné, et c'est une distinction de rôle.** Lire l'environnement
pour **classer** peut échouer sans conséquence — une recommandation dégradée
vaut mieux qu'un écran cassé. Lire l'environnement pour **décider de créer
une séance** ne le peut pas : là, une lecture qui échoue doit **remonter**,
jamais se déguiser en « non déclaré ». D'où un mode strict, utilisé par le
seul préflight.

### Option B — où vit la déclaration

`Mon plan`, section d'ancre `#equipement`, sous le bloc existant. Aucune page
neuve, aucun Gym Profile, aucune modale — le `§9` les interdit et le produit
n'en a pas besoin.

Les deux concepts restent séparés **et le disent**, parce que le code le dit :

| | influence, **prouvée par le code** |
|---|---|
| **familles** (6, existant) | construction du programme : `weekly_planner.py:637` → `morpho_program_generator.py:266` |
| **objets concrets** (29, neuf) | recommandation du jour : `recommendation_v3.py:731` → `environment_activation.py:174` |

Les familles **ne touchent pas** la séance du jour. La phrase
`plan.html:249` reste donc vraie — et sera resserrée pour nommer les
familles, afin qu'aucune lecture ne l'étende au module neuf.

### Option C — le refus de démarrage

Le dépôt a un idiome établi : `db.rollback()` + re-rendu avec `error=`
(`user_programs.py:1017`). Mais `POST /sessions` **redirige**, il ne rend
pas. La forme fidèle est donc celle que les préférences emploient déjà
(`/plan?pref_error=1`) :

```
303 → /plan?depart_bloque=<slug>#equipement
```

⚠ **Corollaire trouvé à l'audit** : `index.html:315` pointe aujourd'hui vers
`#declaration`, c'est-à-dire le **questionnaire de familles** — précisément
ce que le `§6` interdit (« do not link to the old family questionnaire and
pretend that it fixes the problem »). Il pointera vers `#equipement`.

### Risques et ce qui les tient

| risque | garde |
|---|---|
| régresser les utilisateurs `NULL` | `NON_APPLICABLE` : aucun appel de porte, aucune adaptation, aucune empreinte |
| séance orpheline après refus | refus **avant** `instantiate_session` ; garde comptant les `WorkoutSession` |
| matérialisation partielle silencieuse | comparaison attendu/posé + `rollback` ; mutation N−1 jouée |
| deux formulaires qui s'écrasent | le formulaire neuf poste sur une **route neuve** et n'appelle que `save_available_equipment_items` |
| casser une garde existante | sept repérées **avant** d'écrire, listées au `§9` |

### Arbitrages opérateur rendus avant le build

| question | réponse |
|---|---|
| sous-curation : le gabarit sans matériel gagne en environnement modeste | **laisser tel quel**, `§1.A` strict |
| forme du contrôle à trois états | **formulaire unique**, zéro case cochée = « sans matériel » |
| retour à `NULL` | formulaire unique **+ action discrète « Effacer ma déclaration »** |

Le troisième arbitrage existe parce que le second, seul, rendait `NULL`
**inatteignable** une fois une déclaration faite — or `NULL` est l'état qui
garantit le comportement hérité de la porte `G7`.

---

## 3. Ce qui a été construit

| fichier | nature |
|---|---|
| `app/services/environment_activation.py` | `PreparationDemarrage` + `preparer_demarrage()` ; mode **strict** de `environnement_declare` |
| `app/routers/sessions.py` | préflight **avant** instanciation ; `_poser_adaptations` remplace le `except Exception: return 0` |
| `app/routers/user_programs.py` | **seconde** route de démarrage câblée ; route d'écriture neuve `POST /plan/equipement` |
| `app/templates/user_programs/plan.html` | section `#equipement`, résumé à deux faits, « Effacer ma déclaration » |
| `app/templates/index.html` | ancre de récupération `#declaration` → `#equipement` |
| `data/equipment_registry.json` | champ `group` de **présentation** (5 groupes, 29 objets) |
| `app/services/equipment_model.py` | `equipment_groups()` |
| `tests/test_train_a_environment_experience.py` | 18 gardes de frontière |
| `tests/test_train_a_environment_product_proof.py` | les 10 cas du `§8` |

**Aucune migration** — la colonne existe depuis `x5y0s6t7v18`.

---

## 4. Les dix preuves produit du `§8` — jouées sur les vraies routes

`tests/test_train_a_environment_product_proof.py`, **16 tests, tous verts**.
Aucun verdict n'est choisi : l'aide `_un_etat()` **cherche** dans le catalogue
réel un gabarit produisant l'état visé, et la preuve échoue si aucun n'existe.

| # | cas | verdict |
|---|---|---|
| 1 | environnement `NULL` | reco inchangée (`environnement_actif` absent) ; START crée la séance, **0 substitution** |
| 2 | `[]` explicite | porte **active** ; `no-equipment-full-body` reste `NATIF` et démarre |
| 3 | salle équipée | reco consciente du lieu ; 4 environnements → **4 empreintes distinctes** |
| 4 | gabarit adaptable | START persiste **toute** la correspondance prescrit→exécuté |
| 5 | prouvé infaisable | **0 séance** créée ; `303 → /plan?depart_bloque=…#equipement`, page habitable |
| 6 | `UNKNOWN` | non bloquant ; **plan vide** — aucune adaptation fabriquée |
| 7 | familles grossières seules | inventaire concret **intact** ; cocher « cable » n'invente aucun appareil |
| 8 | écriture de l'inventaire | cadence / focus / familles **inchangées** |
| 9 | formulaire hérité | inventaire concret **non effacé**, même sur la soumission la plus destructrice |
| 10 | propriété | écriture et lecture strictement bornées au propriétaire du cookie |

### Le relevé mesuré des quatre classes

| environnement | objets | état catalogue | empreinte | `push-a` | `push-b` | `pull-a` | `legs-a` | sans matériel |
|---|---|---|---|---|---|---|---|---|
| salle complète | 29 | `servable` | `01a18998…` | **adaptable** (1) | incertain | **adaptable** (1) | **adaptable** (1) | natif |
| salle limitée | 24 | `servable` | `0da0debd…` | incertain | **refusé** | **adaptable** (2) | **adaptable** (1) | natif |
| maison (haltères + banc) | 2 | `servable` | `b3d0f2b1…` | incertain | **refusé** | **refusé** | **refusé** | natif |
| sans matériel `[]` | 0 | `servable` | `4422a1e6…` | incertain | **refusé** | **refusé** | **refusé** | natif |

Correspondances prescrit→exécuté réellement posées :

```
salle complète · push-a   pos 3  Dips pectoraux (buste penché) → Développé couché haltères
salle limitée  · pull-a   pos 5  Face pull câble               → Reverse fly machine
                          pos 7  Straight-arm pulldown câble   → Pullover câble (bras tendus)
```

**Quatre lectures qui comptent, et une qui dérange :**

1. le catalogue reste `servable` dans **les quatre** environnements — personne
   n'est jamais renvoyé sans séance, y compris en déclarant `[]` ;
2. les quatre empreintes sont distinctes — l'identité `G9` ne se replie pas
   sur une valeur commode ;
3. un `UNKNOWN` n'est **jamais** rapporté faisable, et ne produit jamais
   d'adaptation ;
4. ⚠ **en salle complète, `push-a` est quand même adapté.** « Dips pectoraux »
   est `UNKNOWN` — aucun poste à dips n'existe dans le registre des 29 objets,
   donc l'exercice n'est prouvable dans **aucun** environnement, et le
   résolveur lui préfère un substitut autorisé prouvé faisable.

Le point 4 n'est pas un défaut de ce sprint : c'est la conséquence stricte du
`§1.A` que vous avez arbitrée (« laisser tel quel »), rendue visible pour la
première fois parce que la déclaration est enfin atteignable. Elle se ferme
en curation — les 7 alias atlas vérifiés et les 39 identités `UNKNOWN` —, pas
en code, et ces deux chantiers vous appartiennent.

---

## 5. Relecture du relevé de décisions (`CLAUDE.md §5.2`)

`docs/DESIGN_DECISIONS_UIV2_SURFACES.md`, décision par décision.

| décision | statut |
|---|---|
| **Q1** — la connexion porte l'identité | **non concernée** — aucune surface d'auth touchée |
| **Q2** — ancre visuelle de l'accueil | **respectée** — seule l'`href` de récupération change (`#declaration` → `#equipement`), aucun pixel d'accueil |
| **Q3** — « État du jour » décommissionné | **non concernée** |
| **Q4** — la ligne de série est un instrument | **non concernée** — `Session` intouchée |
| **Q5** — trois rangs de surfaces | **respectée** — aucune page neuve ; la déclaration vit dans `Mon plan`, rang existant |
| **Q6** — échelle 32/22/15/12 | **respectée** — aucune taille neuve, les blocs réutilisent `prefs-block` |
| **Q7** — un seul aplat ambre par écran | **tension réelle, arbitrée par l'opérateur** (ci-dessous) |
| **Q8** — aucune opacité décorative | **respectée** — aucune opacité, aucune couleur neuve, zéro token ajouté |
| **Tokens bleus** | **respectée** — aucun hex écrit, aucun `var(--token, #hex)` de repli |

### Q7 — ce que je n'ai pas tranché seul

Le marqueur de case cochée est **ambre** : c'est la primitive de sélection
existante du dépôt (`choice_row`). Le formulaire de familles en montre au
plus 6 ; le mien peut en montrer **29**, et le harnais de rendu en a affiché
**25 simultanément** éditeur ouvert.

La garde `test_one_amber_fill_per_screen.py` reste **verte** (3/3) : elle
mesure l'aplat de surface, pas le marqueur de contrôle, et le bouton neuf est
`btn--ghost`, jamais `btn--primary`. La baseline `/plan` reste à **1**.

Restyler cette primitive **partagée** serait une refonte, que le `§9` de la
mission interdit. J'ai donc exposé le pire cas en rendu réel et posé la
question. **L'opérateur a accepté.** Je consigne aussi que mon propre
compteur d'ambre était faux — il mesurait des boîtes de mise en page, pas la
visibilité — et que la barre de navigation qui coupe une rangée dans les
captures pleine page est un artefact de capture (`position: fixed`), pas un
recouvrement réel.

### `§5.1` — exposition visuelle préalable

**Faite avant tout commit d'UI.** Neuf rendus réels authentifiés : états A–E,
le pire cas éditeur ouvert, le gros plan du module, et D/E en 1280 px.
Relevé à 390 px : référence 866 px · A 866 · B 848 · C 848 · D 2 545
(éditeur ouvert) · E 926. **88 contrôles, 0 débordement horizontal, 0 texte
tronqué** dans tous les états. Une disclosure neuve, repliée par défaut. Les
43 cibles sous 44 px sont **identiques à l'état de référence** (éléments
`a11y-input` 1×1 masqués, et le lien de marque).

### `§5.3` — jamais une soustraction seule

Rien n'est retiré. La seule substitution est l'ancre de récupération, qui
part **dans la même livraison** que la section qu'elle vise.

---

## 6. Gardes existantes : aucune affaiblie

Les sept repérées **avant** d'écrire sont vertes, et **305 tests** d'UI et de
préférences passent sans modification d'aucune garde :

`test_ui_interaction_primitives` · `test_ui_profile_preferences` ·
`test_form_controls_use_the_shells` · `test_no_disclosure_relies_on_the_browser` ·
`test_train2_mon_plan` · `test_training_preferences` ·
`test_one_amber_fill_per_screen`.

Aucune racine de classe neuve dans `interaction.css`. Aucun `style=` inline.
Aucun `<input>` nu. `profile_preferences_submit` reste hébergé par le seul
`plan.html`.

Quatre **mutations** ont été jouées et toutes ont été attrapées : préflight
retiré · fail-open large rétabli · N−1 adaptations posées · démarrage direct
d'un gabarit `REFUSE`.

---

## 7. Non-goals tenus (`§9` de la mission)

Aucun des 17 interdits n'a été touché : les 7 alias atlas en attente ne sont
pas appliqués · les 39 `UNKNOWN` ne sont pas corrigés · `exercise_properties`
n'est pas élargi · `N1/N2/N3` inchangés · `pattern_motor` inchangé · aucun
schéma de série temporisé · pas de Front Plank · pas de lieux multiples · pas
de surcharge d'environnement par séance · aucune inférence depuis l'historique
ni depuis les familles grossières · `Mon plan`, `Home` et `Session` non
redessinés · aucune dépendance de framework · **aucune migration** · politique
de récupération et de score inchangée.

---

## 8. Vérification exécutée

| contrôle | résultat |
|---|---|
| `scripts/check_scope.py` | `SHARED_CODE` — **traité en `RUNTIME_FLOW`** comme le `§10` l'exige |
| `ruff` sur **tout le diff Python** | propre, hors un `C901` **préexistant en canonique** sur `session_detail` (complexité 25, identique avant/après, fonction non touchée) |
| scan `S9073` par AST | **0** assertion composite sur les 6 fichiers |
| `check_ruff_budget` | 264 ≤ 548 — OK |
| `check_spec_protocol` | OK |
| gardes de frontière | 18/18 |
| preuves produit `§8` | 16/16 |
| sweep ciblé UI + préférences | 305/305 |
| full sweep local, arbre **gelé** | voir ci-dessous |

### Le premier full sweep était ROUGE — deux gardes m'ont attrapé

Les deux sont des gardes du dépôt qui ont fait exactement leur travail, et
aucune n'a été élargie pour me laisser passer.

**1. `test_rec_cp2_policy::test_v3_n_est_reference_que_par_le_banc_et_la_composition`**

Mon fichier de preuves importait `recommander_v3` directement. Le registre des
lecteurs autorisés de V3 existe pour que la promotion passe par la porte du
`§12`, pas par une importation.

Le réflexe aurait été d'ajouter mon fichier à la liste blanche. Le défaut
était ailleurs : **je mesurais une politique que j'avais choisie**, pas celle
que le produit sert. Corrigé en appelant le point de composition unique —
`advice_memory.recommander(..., politique=POLITIQUE_SERVIE,
avec_memoire=MEMOIRE_SERVIE)`, la ligne exacte de `pages.py:104`. La preuve
est plus fidèle **et** la liste blanche n'a pas bougé.

**2. `test_train_a_activation_environnement::test_no_second_resolver_was_introduced`**

J'avais écrit `ADAPTABLE = "adaptable"` dans `environment_activation.py`. Le
résolveur le définit déjà, **avec la même valeur et le même sens**. La garde
interdit cette redéfinition précisément parce que deux définitions du même
fait divergent toujours. Corrigé par un import, pas par un assouplissement.

---

## Verdict

**Ce qui est prouvé.** `START` est devenu autoritaire sur **les deux** routes
de démarrage ; une matérialisation partielle ne se committe jamais ; `NULL`,
`[]` et un inventaire peuplé restent trois états distincts et chacun
atteignable par l'utilisateur ; les familles grossières et les objets concrets
ne se dérivent **dans aucun sens** ; les dix cas du `§8` passent par les
vraies routes.

**Ce qui est connu et non résolu.** « Dips pectoraux » est substitué même en
salle complète, parce que la curation ne peut pas le prouver. Ce n'est pas un
défaut de code : c'est le `§1.A` strict, visible pour la première fois. Il se
ferme par les 7 alias vérifiés et les 39 identités `UNKNOWN` — deux décisions
qui vous appartiennent.

**Ce que je n'ai pas tranché.** Le marqueur ambre de la case cochée, primitive
partagée que ce sprint n'a pas le droit de redessiner. Exposé en rendu réel,
**accepté par l'opérateur**.

`Sb_TRAIN_A_ENVIRONMENT_EXPERIENCE_01` — **PR GREEN / MERGE PENDING**.
Aucun merge sans `GO MERGE`.

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)
