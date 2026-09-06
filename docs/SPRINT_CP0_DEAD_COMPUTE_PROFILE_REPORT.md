# CP-0 — `/profile` cesse de calculer pour personne

**Tier `check_scope`** : `ISOLATED` annoncé, **traité en `SHARED_CODE`** — la
tranche modifie un routeur, et `check_scope` ne voit que des fichiers neufs en
feuille. `CLAUDE.md §1` : en cas de doute, remonter d'un cran.
**Fichiers** : `app/routers/auth_routes.py` · `tests/test_profile_query_budget.py`
**Changement produit : AUCUN.** Aucune information visible ne bouge.

---

## 1. Le défaut

Le routeur du Profil construisait **19 clés de contexte. Le gabarit en lit 9.**

Les dix autres — `session_count`, `completed_count`, `quality_svg`,
`sessions_30d_count`, `trend`, `trend_label`, `measurement_charts`,
`measurement_labels`, `measurement_fields`, `related_templates` — étaient
calculées **à chaque affichage** et lues par personne.

`RUNTIME_MEASURED`, par instrumentation de `before_cursor_execute` et
attribution de chaque requête à sa ligne via la pile d'appel :

| Ligne | Ce qu'elle calcule | Requêtes |
|---|---|---|
| `:474` | dix courbes SVG, une par champ de mesure | **11** |
| `:390` | qualité de chaque séance sur 30 jours | **4** |
| `:373` `:384` | séances 30 j en cascade `selectinload` | **3** |
| `:358` `:362` `:399` | compteurs, tendance 30 j vs 30 j | **3** |
| `:485` | **la table des templates en entier** | **1** |
| | **total jeté** | **22 sur 27** |

### Ce n'est pas une découverte, c'est une récidive

Le routeur porte déjà, en commentaire, le même défaut corrigé une première
fois — `UX4_03B` :

> *« `UX4_01` a retiré les modules analytiques du Profil sans retirer le calcul
> qui les alimentait. Le gabarit ne lisait plus aucun champ, mais chaque
> affichage exécutait quand même les requêtes du moteur. »*

**Même défaut, même route, déjà diagnostiqué et déjà réparé.** Il est revenu.

### Et personne ne le surveillait — au sens fort

`TEST_PROVEN` : le retrait a été joué sur **44 fichiers, 1 348 tests — zéro
échec**. Les fichiers qui *mentionnent* ces noms testent les **fonctions de
service** (`find_related_templates`, `_trend_label`), jamais les clés de la
route.

**Aucun test du dépôt n'a jamais observé les dix clés.** C'est pourquoi le
défaut a pu revenir, et pourquoi une troisième occurrence était certaine.

---

## 2. Brainstorming / Options / Risques / Choix retenu

### Option A — retirer le calcul, sans garde

* ✅ Le geste minimal.
* ❌ **C'est exactement ce qui a été fait à `UX4_01`**, et le défaut est revenu.
  Un retrait sans garde est un retrait qui se répète.

### Option B — un analyseur statique « clé de contexte inutilisée »

Balayer chaque gabarit et signaler les clés qu'il ne lit pas.

* ✅ Générique, attraperait d'autres routes.
* ❌ **Le dépôt montre qu'il serait peu fiable** : `base.html` lit
  `active_session`, qu'un balayage du seul `profile.html` déclarerait morte.
  Une garde qui accuse du code sain est un mode d'échec déjà relevé cinq fois
  ici.
* ❌ Et il mesurerait ce que la route **déclare**, pas ce qu'elle **fait**.

### Option C — retrait + cliquet de requêtes sur la route *(retenu)*

* ✅ Le compteur mesure le **comportement**, pas la déclaration.
* ✅ Il attrape la récidive suivante, y compris sous une forme qu'on n'a pas
  prévue — un module rebranché coûte des requêtes quel que soit son nom.
* ✅ Il ne prétend à rien d'autre : ce n'est pas un jugement de performance.

### Risques et leur traitement

| Risque | Traitement |
|---|---|
| Un budget lâche ne serre rien | Budget **strict à la valeur mesurée** — les 4 combinaisons de chemin rendent exactement 5. Un premier jet posait 12 « pour la marge » : le plus petit module retiré coûte **une** requête, la marge l'aurait laissé revenir |
| Le compteur cesse d'être branché et le budget passe à vide | `test_le_compteur_voit_bien_des_requetes` exige un compte non nul |
| Une page cassée respecte le budget | `test_le_profil_repond_toujours` — 200 et « Profil » présent |
| Le retrait change le rendu | Équivalence `SHA₂₅₆`, **deux utilisateurs représentatifs** |
| Les gardes ne mordent pas | Copiées dans le worktree **non patché** : 21 requêtes contre 5, **4 échecs** |

---

## 3. Les preuves exigées, rendues

| Preuve | Résultat | Classe |
|---|---|---|
| Requêtes SQL sur `/profile` | **27 → 5** | `RUNTIME_MEASURED` |
| Clés de contexte | **19 → 9** | `RUNTIME_MEASURED` |
| Rendu, utilisateur **avec** mesures | 19 302 o → 19 302 o, **SHA identique** | `RUNTIME_MEASURED` |
| Rendu, utilisateur **sans** mesures | 16 882 o → 16 882 o, **SHA identique** | `RUNTIME_MEASURED` |
| Sweep large — 46 fichiers | **1 370 passés · 0 échec** | `TEST_PROVEN` |
| Cliquet de requêtes | 6 gardes | `TEST_PROVEN` |
| **Le cliquet mord sur le défaut d'origine** | **21 > 5, 4 échecs** sur le canonique non patché | `RUNTIME_MEASURED` |

### Le budget, et pourquoi il est strict

Les **quatre** combinaisons de chemin — avec/sans mesure × avec/sans séance
ouverte — rendent **exactement 5 requêtes**. Aucune marge n'est justifiée par
une variation observée.

Les 5 qui restent : la session d'authentification · le read-model morphologique
(×2) · la dernière mesure · la séance ouverte, lue par `base.html`.

**Relever ce nombre est une décision, pas un ajustement.**

---

## 4. Périmètre — la frontière tracée par la mesure

Neuf imports deviennent orphelins et sont retirés. **Cinq fonctions de service
se retrouvent alors sans aucun appelant applicatif** :

| Symbole | Consommateurs `app/` après CP-0 |
|---|---|
| `build_measurement_timeline_svg` · `get_measurement_series` · `find_related_templates` · `MEASUREMENT_LABELS` · `MEASUREMENT_UNITS` | **0** |
| `build_quality_timeline_svg` · `TimelinePoint` | encore lus par `pages.py` |
| `compute_session_quality` | 16 |

**Signalé, non inclus.** Retirer un appel qui laisse sa fonction sans appelant
déplace le code mort d'un cran ; le retirer aussi est une **autre décision**, et
l'inclure sans le dire serait de la dérive de périmètre.

`MEASUREMENT_FIELDS` **reste** : il porte encore le `calf_cm` historique et
alimente `latest_values`, qui est rendu.

---

## 5. Vérifications

| Contrôle | Résultat |
|---|---|
| `check_scope` | `ISOLATED` → **traité en `SHARED_CODE`** |
| `ruff` (fichiers touchés) | **1 erreur, préexistante** — `E402` ligne 53, identique au canonique (ligne 57, décalée par le retrait). **Zéro erreur neuve** |
| `check_ruff_budget` | `267 ≤ 548` |
| `check_spec_protocol` | `OK` |
| `tests/test_profile_query_budget.py` | **6 passés** |
| **Sweep large** — 46 fichiers consommateurs | **1 370 passés · 0 échec** en 4 min 30 |

---

## 6. Ce que cette tranche ne fait PAS

* **Elle ne redessine pas `/profile`.** Aucun gabarit, aucune feuille de style.
* **Elle ne change aucune information visible.** Prouvé par `SHA₂₅₆`.
* **Elle n'introduit aucune abstraction produit.**
* **Elle ne se mêle ni à la consolidation cockpit ni au travail temporel.**
* Elle ne retire pas les cinq fonctions devenues orphelines (§4).
* Elle ne construit pas d'analyseur générique de contexte inutilisé (§2, option B).

---

## Verdict

**LIVRÉ.** `/profile` passe de 27 à 5 requêtes SQL pour un rendu strictement
identique, octet pour octet, chez un utilisateur avec mesures comme chez un
utilisateur sans.

Ce qui compte davantage que les 22 requêtes : **le défaut était déjà documenté
dans le fichier, déjà corrigé une fois, et invisible à 1 348 tests.** Un
retrait de plus l'aurait reconduit une troisième fois. Le cliquet de requêtes
est la seule partie de cette tranche qui empêche la suivante.
