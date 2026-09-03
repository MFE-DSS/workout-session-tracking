# `Sx_CI_CONTROL_COVERAGE_01` — ce que la CI ne voyait pas

**Tranche de contrôle, pas de calcul.** Le chantier précédent
(`Sx_CI_FINAL_IMPACT_RECHECK_02`) a établi qu'il n'y a plus de calcul à
économiser sûrement, et s'est fermé sur `CLOSE_AS_IS`. Celui-ci n'économise
rien : il augmente ce que la CI **voit**.

---

## 1. Brainstorming / Options / Risques / Choix retenu

**Le problème.** Sur dix défauts UI réels plantés dans la console de séance et
joués contre les 293 fichiers de test, **trois ne faisaient rougir personne**.
Et le 2026-09-03, la canonique est tombée sur un test que **personne n'avait
touché**.

**Options examinées.**

| Option | Ce qu'elle apporte | Écartée parce que |
|---|---|---|
| Installer Playwright en CI | voit réellement les pixels | contredit `Sb_UI_11.1`, décision documentée ; coût runner ; hors périmètre |
| Seuil dur « tout ≥ 44 px » | simple | **rouge sur du code sain** (9 sites préexistants légitimes) ou impose de retoucher des surfaces acceptées — `CLAUDE.md §5.5` |
| `pytest-randomly` en CI | révèle les dépendances d'ordre | rend la CI non déterministe et les échecs non reproductibles ; ne dit pas QUI dépend de qui |
| **Cliquets à inventaire gelé** | verts sur le code sain, rouges sur toute entrée neuve | **RETENU** — motif déjà éprouvé par `.ruff-budget.json` |
| **Isolation des seuls fichiers modifiés** | attrape la classe au moment où elle est introduite | **RETENU** — quelques secondes par fichier |

**Risque principal du choix retenu** : un cliquet peut se relâcher en silence si
l'inventaire garde des entrées périmées. Deux gardes dédiées l'interdisent
(`test_the_floor_inventory_does_not_rot`, `test_the_summary_inventory_does_not_rot`).

---

## 2. `P1` — la bombe temporelle

### Le défaut

```
NOW = datetime(2026, 8, 21, 12, 0, tzinfo=UTC)   ancrage GELÉ
_session(db, uid, days_ago=2)                    donnée au 2026-08-19
client.get("/progress")                          la route lit l'heure RÉELLE
WINDOW_DAYS = 14
```

| Jour réel | Début de fenêtre | Donnée |
|---|---|---|
| 2026-09-01 | 2026-08-18 | dedans |
| 2026-09-02 | 2026-08-19 | dedans (pile sur la borne) |
| **2026-09-03** | **2026-08-20** | **dehors** |

**La canonique est tombée à minuit UTC** (run `33732658392`), dix-neuf jours
après la pose de la bombe, sans qu'aucun commit n'ait touché produit ni test.

### Ce que j'ai d'abord conclu, et qui était faux

J'ai attribué la rougeur au **décalage des shards** : la tranche précédente
ajoutait un fichier de test, ce qui déplaçait la cible du shard 3 au shard 1 —
vérifié par calcul, et vrai. **Mais ce n'était pas la cause** : rejouée,
l'ancienne partition est rouge elle aussi. Le calcul était juste, la conclusion
non.

### Le correctif

Ancrage **flottant** : `datetime.now(UTC).replace(hour=12, …)`. Le déterminisme
dans un run est préservé — l'horloge est lue une fois, au chargement du module —
et la distance à la fenêtre glissante reste constante d'un jour à l'autre. Les
tests de service continuent de recevoir `now=NOW` : rien n'y dérive.

Deux fichiers : celui qui a explosé, et **`test_ux4_zone_exposure.py` qui
portait la même bombe, encore verte**. Corrigée avant l'incident.

### La garde

`test_time_bomb_guard.py` interdit la combinaison ancrage gelé + route réelle,
et **laisse passer le cas légitime** (`now=` injecté), ce qu'une garde dédiée
vérifie. Replantée avec le défaut d'origine : **elle rougit**, avec le bon
message.

---

## 3. `P2` — le garde local sous-classait exactement ce qui est global

`check_scope.py` détectait le « code partagé » par les **imports Python**. Une
feuille de style et un gabarit ne s'importent pas : ils étaient donc
**indétectables**, et classés `isolated` — le niveau de vérification **le plus
bas**.

Mesuré par observation dynamique de **1391 tests** :

| Fichier | Observé par | `check_scope` disait |
|---|---|---|
| `app/static/css/app.css` | **54,8 %** de la suite | `isolated` |
| `app/static/css/interaction.css` | 52,0 % | `isolated` |
| `app/static/css/target_closure.css` | 51,7 % | `isolated` |
| `app/templates/base.html` | **50,7 %** | `isolated` |
| `app/services/briefing.py` | — | `shared_code` ✓ |

`AUREN_UI_BLUEPRINT §8` l'avait signalé sans le chiffrer. **À la veille d'une
phase de refonte UI, c'était le mauvais sens d'erreur.**

Correctif : une liste `global_surfaces` dans `.check-policy.json` (versionné,
donc modifiable seulement par commit), avec **le pourcentage mesuré attaché à
chaque entrée**. Trois gardes : les globaux remontent en `shared_code`, les
fichiers cadrés (`home.css`, `index.html`) **restent** `isolated`, et aucune
entrée ne peut être ajoutée sans sa mesure.

---

## 4. `P3` — trois familles de défaut UI qu'aucun test ne voyait

| Famille plantée | Avant | Après |
|---|---|---|
| plancher 44 px abaissé à 24 | **aveugle** | rouge |
| marqueur d'un `<summary>` supprimé | **aveugle** | rouge |
| sélecteur renommé dans un script | **aveugle** | rouge |

Cause assumée et documentée : `pyproject.toml` (`Sb_UI_11.1`) — Playwright n'est
**jamais** installé en CI. Le signal UI y est entièrement textuel. Ces gardes
n'y changent rien : elles sont en **Python pur, sans navigateur, sans dépendance
neuve**, et mesurent des **invariants de source** que les trois défauts violent
tous.

### Une garde trouvée creuse, et réparée

La garde `<summary>` cherchait d'abord « summary » **dans le nom du sélecteur
CSS**. Plantée, elle est restée **verte** : `.overload-hint__why-toggle` EST un
`<summary>` — le « Pourquoi ? » de la console — et son nom ne le dit pas.

Réancrée sur les **gabarits** — qui savent quels éléments sont des `<summary>` —
elle est passée de **13 à 27 règles recensées** : elle en manquait la moitié.

> **Le nom d'une classe est une convention ; le gabarit est la source.**

### La troisième ferme le versant encore ouvert de `DF-03`

L'incident du dogfood — minuteur figé sur `1:30`, contrôles `±15 s` absents —
venait d'un script cherchant `[data-start-rest]` quand le HTML n'émettait plus
que `[data-rest-started]` : zéro racine, sortie par un `return` silencieux,
**aucune erreur, aucun 404**. `STATIC_ASSET_COHERENCE_01` a fermé le versant
« asset périmé » par l'empreinte d'URL ; le versant « sélecteur incohérent »
restait ouvert. Mesuré : **zéro incohérence aujourd'hui**, et un renommage la
fait rougir.

---

## 5. `P4` — un test modifié doit passer seul

Le verdict de la suite dépendait du **groupement**. Deux propriétés du dépôt
rendaient le défaut invisible :

1. **L'ordre est entièrement déterministe** — `pytest-randomly` n'est pas
   installé. *(Mes propres `-p no:randomly` étaient donc sans effet.)*
2. **Mais la liste de fichiers bouge** : le shardage est un tourniquet **par
   index**, et ajouter un seul fichier de test déplace **229 fichiers sur 292
   (79 %)**.

Un défaut d'isolation surgit donc sur une PR sans rapport, et disparaît sur la
suivante.

`scripts/check_test_isolation.py` rejoue **chaque fichier de test modifié par la
PR, seul**. Vérifié : il rougit sur le défaut d'origine.

**Ce que cette étape n'est pas** : un test peut passer seul ET polluer ses
voisins. C'est l'autre sens, et il demanderait une exécution croisée. Cette
étape ferme le sens qui a réellement coûté une canonique.

---

## 6. Ce qui a été écarté, et pourquoi

**`P5` — stabiliser la partition des shards par hachage.** Le churn tomberait de
79 % à **0 %**, mais l'équilibre se dégraderait à **89 / 82 / 121** fichiers,
soit environ **+25 % de wall-clock** sur le shard le plus lourd.

> Le churn n'est pas le défaut — la **dépendance au groupement** l'est. Le churn
> ne fait que la rendre non reproductible. `P4` traite la cause ; `P5`
> masquerait le symptôme en coûtant du temps.

**`main` dans `push.branches`** : retiré. La branche n'existe pas sur le remote
(`git ls-remote --heads origin main` ne rend rien). Hygiène, zéro effet calcul.

**Le `if:` du job `sonar`** (une PR de fork laisserait le contrôle requis en
*pending*) et **le passage de 3 à 5 shards** restent **soumis à arbitrage** —
0 PR de fork sur 120, et le second est un levier de latence, pas de contrôle.

---

## 7. Fautes de l'agent

1. **Une cause fausse, affirmée avec une preuve juste.** Le décalage des shards
   était réel et mesuré ; il n'était pas la cause. *Vérifier une hypothèse ne
   suffit pas : il faut vérifier qu'aucune autre ne suffit.*
2. **Une garde creuse, troisième fois de la série.** La garde `<summary>`
   cherchait un mot dans un nom de classe. Trouvée par plantation, réancrée sur
   la source de vérité.
3. **Deux plantations mal ancrées** — j'ai muté un commentaire JS et une règle
   CSS sans rapport, puis conclu « défaut invisible ». C'est exactement la faute
   que `DF-C` a consignée, et elle s'est reproduite.
4. **Un outil que je croyais actif ne l'était pas.** `-p no:randomly` dans toutes
   mes commandes, alors que `pytest-randomly` n'est pas installé.

---

## 8. Vérifications

| | |
|---|---|
| `check_scope.py` | **`CI_INFRA`** — full sweep local obligatoire, validation CI réelle impérative |
| Gardes neuves | **21** · 6 défauts plantés, 6 rouges après réancrage |
| Familles UI aveugles fermées | **3 / 3** |
| ruff · budget · spec | propre · 275 / 548 · OK |
| Pré-scan AST | `S9073` · `S5863` · `S1192` · `S7632` → 0 sur le code neuf |
| Inventaire gelé | 9 planchers · 27 règles `<summary>` |

---

## 9. Ce qui reste à l'opérateur

1. **Arbitrer** le `if:` du job `sonar` et le nombre de shards.
2. **Déployer** — `DF-E` et `DF-F` sont mergées et absentes de production
   (dernier déploiement `32cf5ee`, 2026-08-29).
3. **Reprendre le chemin critique UI** : `DF-D`, puis `B9`
   (`UIV3_VISUAL_BASELINE_01`), puis `AUREN_EXPERIENCE_ARCHITECTURE_V4`.

---

## 10. Closeout

**Mergée le 2026-09-03** — PR #181, merge `0898f41`, `--merge` tête épinglée
`153abb8`, sans squash ni `--admin`.

| | |
|---|---|
| CI de PR | **verte**, aucun cycle rouge |
| Gate Sonar | **OK** — 0 code smell, 0 bug, 0 vulnérabilité, 0 duplication |
| Fils de revue ouverts | 0 |
| **CI canonique** | **7/7 verte** (run `33748502362`), `SonarCloud` compris |

### La canonique est réparée

Le run canonique précédent (`33732658392`) était rouge sur la bombe temporelle.
Celui qui suit ce merge est **vert de bout en bout**. Le défaut est fermé, et la
garde qui l'interdit est en place.

### L'étape d'isolation a réellement tourné

Vérifié dans les logs de la CI réelle, et pas seulement en local :

```
[isolation] 5 fichier(s) de test modifié(s) — chacun joué SEUL.
[isolation] OK   tests/test_scope_guard.py
[isolation] OK   tests/test_time_bomb_guard.py
[isolation] OK   tests/test_train1c_progression_consolidation.py
[isolation] OK   tests/test_ui_surface_guards.py
[isolation] OK   tests/test_ux4_zone_exposure.py
```

Le fichier qui avait fait tomber la canonique passe désormais **seul**.

### Ce qui reste ouvert, et n'appartient pas à cette tranche

1. **Arbitrage** — le `if:` du job `sonar` (une PR de fork laisserait le
   contrôle requis en *pending* ; 0 occurrence sur 120 PR) et le passage de
   **3 à 5 shards** (−3,6 min par PR pour +0,6 runner-minute, à information
   identique).
2. **Déploiement** — `DF-E` et `DF-F` sont mergées et **absentes de
   production** (dernier déploiement `32cf5ee`, 2026-08-29).
3. **Le chemin critique UI** reprend : `DF-D`, puis `B9`
   (`UIV3_VISUAL_BASELINE_01`), puis `AUREN_EXPERIENCE_ARCHITECTURE_V4`.

**Le chantier CI/CD est fermé.**
