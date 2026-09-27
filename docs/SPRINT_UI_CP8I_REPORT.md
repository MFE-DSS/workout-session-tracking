# `UI-CP8I` — Une saisie interrompue n'est plus perdue

**Statut** : `MERGÉ` · PR #255 · merge `eeff9de`
**Branche** : `sb/ui-cp8i-resilience-saisie` sur canonique `eb6e890`
**Tier `check_scope`** : `ISOLATED` — **traité en `shared_code`**, voir §9
**Migration** : aucune. **Aucune colonne, aucune table, aucune route.**

---

## 1. Le défaut, mesuré avant toute conception

Sur le produit qui tourne, une valeur tapée dans la série courante et non
validée disparaissait :

| mode d'interruption | avant | après | classe |
|---|---|---|---|
| `A` rechargement | `['80','8']` | `[]` | **LOST** |
| `B` naviguer dans AUREN et revenir | `['80','8']` | `[]` | **LOST** |
| `C` changer d'exercice et revenir | `['80','8']` | `[]` | **LOST** |
| `D` retour / avant du navigateur | `['80','8']` | `[]` | **LOST** |
| `E` arrière-plan → premier plan | `['80','8']` | `['80','8']` | `DOM_ONLY` |
| `F` `pagehide` / `pageshow` | `['80','8']` | `['80','8']` | `DOM_ONLY` |
| `G` nouvel onglet | — | `['','']` | indépendant |
| `H` POST réussi | — | enregistré | `SHOULD_DIE` |

**Quatre pertes, toutes à l'intérieur d'un même onglet.** `E` et `F`
survivaient déjà parce que la PAGE vit — c'était du `DOM_ONLY`, pas une
récupération : rien ne les protégeait d'un rechargement.

---

## 2. L'hypothèse a été vérifiée, pas supposée

`sessionStorage` a été mesuré **séparément**, sur exactement les mêmes
chemins. Confondre « les valeurs sont perdues » et « le tampon
survivrait » aurait été construire sur une hypothèse non testée.

| | tampon |
|---|---|
| `A` rechargement | **survit** |
| `B` navigation dans l'onglet | **survit** |
| `C` changement d'exercice | **survit** |
| `D` retour navigateur | **survit** |
| `G` nouvel onglet | `null` — indépendant |
| onglet fermé puis rouvert | `null` — aucune promesse |

C'est **exactement** la frontière produit visée. Donc : pas de table
serveur, pas de `localStorage`, pas de migration.

---

## 3. Brainstorming / Options / Risques / Choix (`CLAUDE.md §3`)

### Rejeté d'emblée — autosauver dans `SetLog`

`completed` est dérivé de la présence de `weight` OU `reps`. Écrire une
valeur à moitié saisie transformerait **un problème de récupération
d'interface en un événement de complétion de domaine** : la série se
cocherait, le repos démarrerait, la recommandation en tiendrait compte.

### Rejeté — `localStorage`

Il survit au navigateur entier : une persistance **plus large que le défaut
prouvé**. Elle promettrait une continuité qu'aucune mesure ne soutient, et
exigerait une politique d'expiration à inventer.

### Rejeté — table de brouillons côté serveur

Justifiable seulement sur preuve d'un besoin **au-delà d'une page-session** :
récupération après fermeture d'onglet, continuité entre appareils, propriété
partagée entre onglets. La mesure n'en a produit aucune. On ne construit pas
sur une exigence non mesurée.

### Retenu — tampon de récupération en `sessionStorage`

Non-autoritaire. Le serveur reste la seule source durable.

| risque | traitement |
|---|---|
| un brouillon écrase une vérité serveur plus récente | base canonique mémorisée, comparaison à la restauration |
| la restauration valide la série | aucun événement émis — garde dédiée |
| le brouillon survit à son propre POST | le serveur déclare les séries enregistrées |
| stockage bloqué (navigation privée stricte) | accès sous `try/catch`, la page ne casse pas |
| fuite entre comptes | clé portée par la séance ; le serveur refuse une séance d'autrui |

---

## 4. Le contrat

**Clé** — `auren:d:<session_id>:<set_id>`. L'identité de séance suffit à
l'isolation entre comptes : un autre compte ne peut pas RENDRE la page qui
lirait la clé. Y ajouter un identifiant d'utilisateur serait de la donnée
que la clé n'a pas besoin de porter.

**Charge** — les deux valeurs saisies, la valeur canonique au moment de la
saisie, un horodatage. Rien d'autre : pas d'historique, pas de profil, pas
d'identité. Pas d'ombre cliente de la base.

**Écriture** — à la frappe (`input`), jamais sur `unload` / `beforeunload` :
ces événements ne se déclenchent pas de façon fiable sur mobile, où un
onglet évincé par l'OS ne les voit jamais. `visibilitychange` est un filet,
pas l'unique occasion.

**Restauration** — remplit les champs, **et rien d'autre**. Aucun événement
synthétique : un `change` réveillerait l'auto-validation de `DF-B` et
soumettrait la série.

**Effacement** — la valeur canonique a changé, ou le serveur déclare la
série enregistrée, ou les deux champs sont vides, ou déconnexion.

---

## 5. Deux choses que la mesure a corrigées dans la conception

### L'auto-validation rétrécit le défaut, et a faussé mes premières mesures

`DF-B` soumet dès que les deux champs portent une valeur et qu'un `change`
part. Une paire complète se valide donc **en quittant le second champ**.

Mon premier harnais utilisait `fill()` de Playwright — qui émet `change`.
Il **validait la série** et mesurait ensuite « saisie non validée » sur une
page où la série était enregistrée. Deux blocs ont planté sur un élément
détaché : c'était la soumission, pas un défaut du tampon.

Les états réellement exposés sont donc : **une saisie partielle** (charge
notée, répétitions pas encore) et une paire complète que l'utilisateur n'a
pas quittée. Le harnais tape au clavier sans quitter le dernier champ.

### La mutation a révélé un défaut de conception, pas seulement un trou de test

Ma première règle d'effacement jetait le brouillon dès que le serveur
déclarait la série enregistrée. Elle tuait aussi les brouillons de
**correction** : rouvrir une série validée pour la corriger, être
interrompu, et perdre la correction — le défaut d'origine simplement
déplacé.

Règle corrigée : la liste des séries enregistrées ne sert que **lorsque
aucun champ n'est rendu** (l'état `REPOS`, où il n'y a rien à comparer).
Quand les champs sont là, c'est la comparaison canonique qui tranche.

---

## 6. Preuves runtime (`§14`) — douze, au navigateur

| | propriété | résultat |
|---|---|---|
| `A` | 80/8 · rechargement → restauré | ✅ |
| `A-bis` | saisie **partielle** → restaurée | ✅ |
| `B` | restauré ⇒ série toujours incomplète en base | ✅ |
| `C` | POST → base à jour **et** brouillon effacé | ✅ |
| `D` | le serveur bouge → le brouillon n'écrase pas | ✅ |
| `E` | aucune fuite vers une autre séance | ✅ |
| `F` | nouvel onglet indépendant, origine intacte | ✅ |
| `G` | un brouillon vide n'existe pas | ✅ |
| `H` | restauration ⇒ **aucun repos déclenché** | ✅ |
| `I` | le brouillon de **correction** survit | ✅ |
| `J` | …mais pas si le serveur a bougé | ✅ |

### Mutations jouées

| mutation | attrapée par |
|---|---|
| garde de péremption retirée | **personne** d'abord → `I`/`J` ajoutées, puis `J` |
| nettoyage post-POST retiré | `C` · `D` |
| l'auto-validation écoute `blur` | `df_b` · `df_f` |
| le minuteur persiste son ajustement | `uiv3_session_console` |

---

## 7. Trois gardes sœurs, et j'en avais oublié une

La propriété `D9` — « la validation implicite n'écoute ni la frappe ni le
`blur` » — est gardée dans **trois** modules. Les trois balayaient
`session_focus.js` ENTIER ; le tampon écoute légitimement `input` pour
écrire un brouillon d'affichage.

J'ai corrigé `test_df_b_session_flow.py` et
`test_uiv3_session_console.py`, puis j'ai cru la famille close. **Le sweep
complet a trouvé `test_df_f_session_micro_closure.py`.**

C'est le défaut « famille aux deux tiers » : une tranche s'arrête à ce
qu'elle a ouvert, et la sœur restante n'a plus de propriétaire. La famille
se cherche par **balayage de la classe**, jamais de mémoire.

Les trois visent désormais la RÉGION de l'auto-validation — le même
rétrécissement que `DF-B` avait déjà fait subir à une garde sœur quand
l'auto-validation a eu besoin de sa propre racine. Aucune n'est affaiblie :
les deux concernées ont été vues rouges sur un `blur` réintroduit.

---

## 8. Une garde neuve qui accusait du code sain

Ma première version de `test_aucune_persistance_serveur_de_brouillon`
interdisait le mot « draft » dans toutes les migrations. Or
`user_programs` en porte un depuis des mois — c'est un **statut de cycle de
vie** de programme (`draft / validated / published / archived`), sans le
moindre rapport avec une saisie en cours.

Une garde qui cherche un MOT au lieu d'une PROPRIÉTÉ trouve des homonymes.
Elle vérifie maintenant ce qui est décidable : les colonnes de `SetLog` sont
exactement celles que `CP8R` a laissées.

---

## 9. `check_scope` dit `ISOLATED` — traité en `shared_code`

La tranche touche `exercise_card.html`, partiel rendu sur **toutes** les
cartes d'exercice, et `session_focus.js`, script partagé. C'est du flux
d'exécution partagé.

`CLAUDE.md §1` : « en cas de doute sur le tier, remonter d'un cran ».
Full sweep local exécuté — et il a trouvé la troisième sœur qu'aucun test
ciblé n'atteignait. **`tous les lots sont verts.`**

---

## 10. Relecture du relevé de décisions (`CLAUDE.md §5.2`)

| décision | verdict |
|---|---|
| zéro framework, zéro dépendance | **respectée** — aucune, aucun réseau |
| le serveur est l'unique autorité de persistance | **respectée** — le tampon n'est pas du domaine |
| `Sx_24 §E` : `completed` dérivé de la présence d'une valeur | **respectée** — rien n'écrit `SetLog` |
| `DF-B` : saisir est valider, sur transition explicite | **respectée** — la restauration n'émet aucun événement |
| `CLAUDE.md §5.3` : jamais une soustraction seule | **non concernée** — addition pure |
| `CLAUDE.md §5.4` : toute couleur est un token | **non concernée** — aucune couleur |
| aucun aplat ambre ajouté | **respectée** — aucune surface visuelle neuve |
| `Sx_UIV3_04 §1bis C` : la durée de repos est une suggestion | **non concernée** — `±15 s` inchangé |

Aucun rendu nouveau : la tranche ne change **aucun pixel**. Les champs
affichent une valeur là où ils affichaient du vide. `CLAUDE.md §5.1` ne
s'applique pas — rien de visuel n'est à arbitrer.

---

## 11. Ce qui reste ouvert

| sujet | état |
|---|---|
| Safari iOS, processus tué par l'OS | **`NEEDS_OPERATOR_DEVICE`** → `CP11` |
| onglet fermé ⇒ saisie perdue | frontière assumée, non mesurée comme insuffisante |
| déconnexion depuis une page hors séance | le tampon meurt avec l'onglet ; isolation structurelle |

**Aucune dérive hors ligne / PWA** (`§18`) — une garde l'épingle.

---

## 12. Closeout

| | |
|---|---|
| **PR** | [#255](https://github.com/MFE-DSS/workout-session-tracking/pull/255) |
| **Merge** | `eeff9def1fdffe9eb7bccf6dc4161633e5fd1464` |
| **Méthode** | `--merge` avec `--match-head-commit 1c3131f` — pas de squash, pas de `--admin`, pas de force |
| **CI de PR** | 10/10 verts |
| **CI canonique** | run [`36306266072`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/36306266072) — **7/7 verts** |
| **Sonar** | `OK` — **0 code smell pondéré**, 0 bug, 0 vulnérabilité, 0 duplication |
| **Threads de revue** | 0 non résolu |
| **Migration** | aucune — et c'est le résultat, pas un raccourci |
| **Sweep local** | `tous les lots sont verts.` sur l'arbre committé |

**Zéro finding Sonar au premier passage.** Les quatre règles qui avaient
mordu sur `CP8R` — `Web:S6819` sur une balise citée en prose,
`external_ruff:UP045` sur une ligne neuve, `python:S8415` sur une 404 —
ont été évitées en amont plutôt que corrigées après coup.

### Ce que la tranche laisse derrière elle

| résidu | destination |
|---|---|
| Safari iOS, processus tué par l'OS | `CP11` — `NEEDS_OPERATOR_DEVICE` |
| onglet fermé ⇒ saisie perdue | frontière assumée, non mesurée comme insuffisante |
| déconnexion hors surface de séance | le tampon meurt avec l'onglet ; isolation structurelle |

`CP8I` clôt le constat ouvert par la matrice d'interruption de `CP8R`.
Suite du chemin critique : `CP8N` (navigation / propriété), `CP8U` (cycle
de vie), `CP9` (arbitrage social), `CP10` (convergence), `CP11` (dogfood
sur appareil réel).

🤖 Generated with [Claude Code](https://claude.com/claude-code)
