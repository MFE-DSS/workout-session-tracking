# Sb_SONAR_GOVERNANCE_01 — Audit et correction de gouvernance SonarCloud

**Date** : 2026-08-12 · **Base mesurée** : `71d36cd` (dernière analyse Sonar de la branche
canonique : `609e876`, 2026-08-12T13:05:08Z) · **Type** : OPS / QUALITY GOVERNANCE
**Périmètre** : configuration SonarCloud + documentation d'exploitation. **Aucun changement de
comportement produit ou runtime.**

---

## 1. Conclusion exécutive

Le gate Quality **projet** de ce dépôt était `ERROR` en permanence, et cela **n'était pas de la
dette de code**. La définition de New Code n'avait jamais été fixée au niveau projet : elle
héritait de la valeur d'instance `previous_version`, et comme aucune `sonar.projectVersion` n'est
maintenue ici, la fenêtre « code neuf » est restée **gelée au 2026-04-10** pendant 124 jours. À
`71d36cd` elle contenait **79 854 lignes « neuves » pour un dépôt de 25 874 lignes** — soit 3,1×
la taille totale du projet. Tout l'historique comptait comme neuf.

> ### ⛔ ARRÊT DUR — la correction principale N'A PAS ABOUTI
>
> **La définition New Code est toujours `previous_version` / 2026-04-10 après merge.** L'écriture
> `settings/set sonar.leak.period=30` a été **acceptée et persiste à la relecture**, mais l'analyse
> canonique complète du 2026-08-13T06:50:15Z (commit `6d16357`, ~8 h plus tard) rapporte encore
> `mode: previous_version`, `date: 2026-04-10`, `new_lines: 81 825`. **Le réglage est inerte sur
> SonarCloud.**
>
> Permission exacte manquante : **`admin` (« Administer ») sur le projet
> `MFE-DSS_workout-session-tracking`**, portée par le groupe **`Owners`** de l'organisation
> `mfe-dss` (`Members` ne porte que `securityhotspotadmin` + `issueadmin` — ce qui explique que
> l'adjudication d'issues, elle, ait fonctionné). L'endpoint autoritatif
> `/api/v2/new-code-definitions` renvoie **403** avec ce token ; `api/new_code_periods/*` renvoie
> **404** (absent de Cloud).
>
> **Action opérateur requise** : UI SonarCloud → *Project Settings → New Code* → **Number of days
> = 30**. Aucun commit ne peut le faire. Détail et preuves en §11.

Corrections **effectivement** appliquées, toutes **sans toucher au Quality Gate, aux seuils, aux
exigences de merge, ni aux imports d'analyseurs externes** :

1. ❌ **New Code projet** — **ÉCHEC**, voir l'encadré ci-dessus. Le réglage écrit est **inerte**.
   Ne pas lire la valeur `sonar.leak.period = 30` comme une fenêtre de 30 jours active.
2. ✅ **Deux faux positifs CRITICAL** adjudiqués `FALSE POSITIVE`, preuve à l'appui, après
   re-vérification du source. **Confirmé par l'analyse post-merge : `bugs` 20 → 18.**
3. ✅ **Route de diagnostic Sonar** corrigée dans la documentation d'exploitation : la CLI `sonar`
   authentifiée remplace le contournement `component_tree` documenté comme obligatoire.

Un quatrième constat est **documenté mais non corrigeable depuis le dépôt** : l'agent de
remédiation automatique tourne tous les jours depuis le 2026-07-31 avec un rendement de **0/13**,
et son pilotage ne vit pas dans ce dépôt (§6).

> **Ce sprint ne résorbe aucune dette Sonar et n'affaiblit aucun gate.** Il corrige la
> **sémantique de mesure**. Le stock historique reste visible et la discipline Clean-as-You-Code
> intacte.

---

## 2. Cause racine mécanique du New Code

### Constat

```bash
sonar api GET '/api/settings/values?component=MFE-DSS_workout-session-tracking&keys=sonar.leak.period,sonar.leak.period.type'
# AVANT : {"key":"sonar.leak.period","value":"previous_version","parentOrigin":"INSTANCE"}
```

`parentOrigin: INSTANCE` est le point clé : **le projet n'avait aucune définition propre**, il
héritait du défaut d'instance SonarCloud. Combiné à l'absence de `sonar.projectVersion` dans
`sonar-project.properties`, `previous_version` ne pouvait jamais basculer.

Effet mesuré à `71d36cd` :

| Métrique | Valeur | Lecture |
|---|---|---|
| période `mode` | `previous_version` | jamais renouvelée |
| période `date` | `2026-04-10T12:45:26+0000` | 124 jours ouverts |
| `new_lines` | **79 854** | « code neuf » |
| `ncloc` | **25 874** | dépôt entier |

Le gate PR, lui, borne son périmètre au diff de la PR : c'est pourquoi **toutes les PR passaient
au vert pendant que le gate projet restait rouge**. Ce n'est pas une contradiction, c'est deux
périmètres différents — mais le gate projet ne mesurait plus rien d'utile.

### Correction appliquée

`api/new_code_periods/set` **n'existe pas sur SonarCloud** (`404 Unknown url`) ; le mécanisme
Cloud est le réglage `sonar.leak.period` :

```bash
sonar api POST '/api/settings/set' \
  --data '{"component":"MFE-DSS_workout-session-tracking","key":"sonar.leak.period","value":"30"}'
sonar api GET  '/api/settings/values?component=MFE-DSS_workout-session-tracking&keys=sonar.leak.period'
# APRÈS : {"key":"sonar.leak.period","value":"30"}
```

**Raison du choix « 30 jours »** : supprime la dépendance à une `sonar.projectVersion` non
maintenue · garde une fenêtre de code récent glissante · préserve l'analyse stricte de new code au
niveau PR.

**Non modifiés** : définition du Quality Gate · seuils de couverture · seuils de sévérité ·
required status checks · imports `sonar.python.ruff.reportPaths` / `sonar.python.bandit.reportPaths`.

> ### ⛔ La preuve est revenue NÉGATIVE — ce réglage est INERTE
>
> SonarCloud n'expose pas de lecture `mode = NUMBER_OF_DAYS` (`new_code_periods/*` → `404`,
> `/api/v2/new-code-definitions` → `403`). La preuve autoritative était donc la période rapportée
> par la première analyse canonique postérieure au changement. **Elle est revenue inchangée :**
>
> ```
> analyse 6d16357 — 2026-08-13T06:50:15+0000
> periods: [{"mode": "previous_version", "date": "2026-04-10T12:45:26+0000"}]
> new_lines: 81 825   (79 854 avant — la fenêtre gelée continue de grossir)
> ```
>
> `sonar.leak.period` est un réglage **hérité, sans effet** sur la définition New Code de
> SonarCloud. L'écriture a été acceptée (204) et persiste — précisément **parce qu'elle ne pilote
> plus rien**. Le vrai mécanisme est le store `new-code-definitions`, dont l'accès exige la
> permission **`admin`** que ce token n'a pas.
>
> **La valeur `sonar.leak.period = 30` a été laissée en place** : elle est inoffensive et enregistre
> l'intention. **Elle ne doit pas être lue comme une fenêtre de 30 jours active.**

**Vérification de portée (faite, concluante).** Le sibling `MFE-DSS_platret-ops-app` renvoyant lui
aussi `30`, la question « mon écriture a-t-elle fuité au niveau instance ? » a été tranchée :

```bash
sonar api GET '/api/settings/values?keys=sonar.leak.period'                              # {} — rien au global
sonar api GET '/api/settings/values?component=workout-session-tracking&keys=sonar.leak.period'  # {} — projet orphelin intact
```

Le projet orphelin **non touché** ne renvoie rien : les valeurs sont bien **par projet** et
l'écriture **n'a pas fuité**. `parentOrigin: INSTANCE` désigne l'origine de la *définition* du
réglage, pas la portée de sa *valeur*. Que `platret` porte `30` de son côté corrobore au passage
que `30` est bien la représentation SonarCloud d'une fenêtre de 30 jours.

---

## 3. Mesures BEFORE → AFTER

**BEFORE** : `71d36cd`, analyse `609e876` du 2026-08-12T13:05:08Z.
**AFTER** : analyse `6d16357` du **2026-08-13T06:50:15Z** (CI canonique `31675257579`, 3/3 verte).

> **Facteur de confusion à déclarer.** Entre les deux analyses, **une autre session a mergé la PR
> #83 (`Sb_RECOVERY_EXPLAINER_01`) en `534cbc2`**. `ncloc` +476 et la baisse de duplication lui
> appartiennent, **pas à ce sprint**. Ce sprint n'a touché aucun fichier `app/`. Constat utile :
> ce code entrant n'a produit **aucune issue nouvelle** (`code_smells` inchangé à 723, familles
> externes inchangées).

| Mesure | BEFORE | AFTER | Effet attribué |
|---|---|---|---|
| New Code — mode | `previous_version` | **`previous_version`** | ⛔ **SETTING — SANS EFFET** |
| New Code — début | `2026-04-10T12:45:26+0000` (124 j) | **`2026-04-10T12:45:26+0000`** (125 j) | ⛔ **SETTING — SANS EFFET** |
| `new_lines` | 79 854 | **81 825** | fenêtre toujours gelée, elle grossit |
| `ncloc` | 25 874 | 26 350 | **CODE CHANGE — PR #83, pas ce sprint** |
| Quality Gate projet | **ERROR** (4 conditions) | **ERROR** (5 conditions) | voir §3bis |
| `reliability_rating` | **4.0 (D)** | ✅ **3.0 (C)** | **ADJUDICATION** |
| `security_rating` | 2.0 (B) | 2.0 (B) | — |
| `sqale_rating` | 1.0 (A) | 1.0 (A) | — |
| `security_review_rating` | 3.0 (C) | 3.0 (C) | — |
| `coverage` | 92.2 % | ⚠️ **0.0 %** | **ARTEFACT CI** — voir §3bis |
| `new_coverage` | 91.7 % (OK) | ⚠️ **0.0 % (ERROR)** | **ARTEFACT CI** — voir §3bis |
| `duplicated_lines_density` | 0.4 % | 0.3 % | CODE CHANGE (PR #83) |
| `new_duplicated_lines_density` | 0.115 % | 0.112 % | — |
| `bugs` | 20 | ✅ **18** | **ADJUDICATION (−2)** |
| `vulnerabilities` | 6 | 6 | — |
| `code_smells` | 723 | 723 | — |
| Issues ouvertes — total | 749 | ✅ **747** | **ADJUDICATION (−2)** |
| Issues ouvertes — Sonar-native | 233 | ✅ **231** | **ADJUDICATION (−2)** |
| Issues ouvertes — `external_ruff` | 510 | 510 | — |
| Issues ouvertes — `external_bandit` | 6 | 6 | — |
| `FALSE_POSITIVE` | 1 | ✅ **3** | **ADJUDICATION (+2)** |

`FIXED` passe de 29 à 28 et le total de 779 à 778 : **purge**, pas régression —
`sonar.dbcleaner.daysBeforeDeletingClosedIssues = 30`.

### 3bis. Le gate reste ERROR, avec une condition de PLUS

| Condition | Seuil | BEFORE | AFTER | Lecture |
|---|---|---|---|---|
| `new_coverage` | ≥ 80 | 91.7 **OK** | **0.0 ERROR** | ⚠️ **nouvelle défaillance — artefact** |
| `new_duplicated_lines_density` | ≤ 3 | 0.1 OK | 0.1 OK | — |
| `new_bugs_severity` | ≤ 9 | 20 | **15** | amélioré par l'adjudication |
| `new_code_smells_severity` | ≤ 14 | 20 | 20 | inchangé |
| `new_sca_severity_any_issue` | ≤ 9 | 10 | 10 | inchangé (risques de dépendances) |
| `new_vulnerabilities_severity` | ≤ 9 | 10 | 10 | inchangé (100 % `external_bandit`) |

`new_bugs_severity` 20 → 15 est cohérent avec le retrait des deux BUG CRITICAL, **mais la métrique
n'est pas une somme linéaire** et sa formule exacte n'a pas été vérifiée dans cette session — le
chiffre est rapporté, pas expliqué.

**⚠️ `new_coverage` 0.0 — mécanisme établi, ce n'est pas une perte de tests.** Le merge de ce
sprint ne touche que `docs/**` et `.claude/skills/**`. Le classifieur `Sb_CI_02_1` l'a donc rangé
en **`NON_RUNTIME`** et a **volontairement sauté pytest + coverage** (log du run `31675257579` :
*« Non-runtime change — full suite intentionally skipped »*). Sans `coverage.xml`, le scanner
rapporte `coverage = 0.0`.

Le commentaire de conception de `Sb_CI_02_1` (`ci.yml:346-351`) juge cela sûr :
*« with no new lines of code, the quality gate does not evaluate `new_coverage` at all (verified on
PR #69 and #70) »*. **Cette hypothèse est vraie au périmètre PR et fausse au périmètre
branche/projet** : la fenêtre New Code gelée contient 81 825 lignes de code, donc `new_coverage`
**est** évaluée — et vaut 0.

> **C'est le défaut de New Code qui rend l'optimisation CI dangereuse.** Les deux se corrigent
> d'un coup : une fenêtre de 30 jours glissants ne contiendrait pas de code un jour où seuls des
> docs changent, et `new_coverage` cesserait d'être évaluée — exactement ce que `Sb_CI_02_1`
> supposait déjà.

**Transitoire** : la prochaine analyse canonique portant un `coverage.xml` (donc le prochain merge
runtime) restaure la couverture. **Aucun changement fabriqué n'a été poussé pour la forcer** —
c'est explicitement interdit par le périmètre de ce sprint.

Conditions du gate BEFORE :

| Condition | Seuil | Réel | Statut |
|---|---|---|---|
| `new_coverage` | ≥ 80 | 91.7 | OK |
| `new_duplicated_lines_density` | ≤ 3 | 0.1 | OK |
| `new_bugs_severity` | ≤ 9 | **20** | ERROR |
| `new_code_smells_severity` | ≤ 14 | **20** | ERROR |
| `new_sca_severity_any_issue` | ≤ 9 | **10** | ERROR |
| `new_vulnerabilities_severity` | ≤ 9 | **10** | ERROR |

### Séparation stricte des effets

- **SETTING EFFECT** — redéfinition de la fenêtre New Code. Ne supprime **aucune** issue ; change
  seulement lesquelles comptent comme « neuves ».
- **FALSE-POSITIVE ADJUDICATION EFFECT** — retire exactement **2 BUG** de l'inventaire ouvert
  (`pythonbugs:S6466`, `Web:S7930`). Aucun autre.
- **CODE CHANGE EFFECT** — **nul**. Ce sprint ne modifie aucun fichier de `app/`. `ncloc`,
  `coverage` et `duplicated_lines_density` ne doivent pas bouger ; s'ils bougent, la cause est
  ailleurs et doit être investiguée.

---

## 4. Stock ouvert : natif vs externe

Mesure paginée dédupliquée sur `.key` (779 issues au total ; **un appel non paginé en aurait perdu
279 sans avertissement** — la CLI plafonne à 500/page) :

```bash
for p in 1 2; do sonar list issues --project MFE-DSS_workout-session-tracking \
  --format json --page-size 500 --page $p; done
```

| Famille | Ouvertes | Part |
|---|---|---|
| `external_ruff` | **510** | 68.1 % |
| `Sonar-native` | **233** | 31.1 % |
| `external_bandit` | **6** | 0.8 % |
| autre externe | 0 | — |

Total ouvert **749** · FIXED 29 · FALSE_POSITIVE 1 (avant ce sprint).
Sévérités ouvertes : MAJOR 668 · CRITICAL 48 · MINOR 33. Types : CODE_SMELL 723 · BUG 20 ·
VULNERABILITY 6.

**Conséquence de gouvernance** : les 4 règles les plus volumineuses du projet
(`UP017` 136, `I001` 135, `UP045` 122, `F401` 63) sont **toutes** `external_ruff`. Elles sont
ingérées telles quelles depuis `ruff-report.json` et **ne portent aucun moteur de règle Sonar** :

- modifier un Quality Profile Sonar **ne peut pas** les corriger ni les taire ;
- elles ne sont **pas éligibles** à la remédiation automatique Sonar-native ;
- leur pilotage appartient à `pyproject.toml` (`[tool.ruff.lint]`, `[tool.bandit]`) et à
  `.ruff-budget.json`.

Note : `sonar.dbcleaner.daysBeforeDeletingClosedIssues = 30`. Le compte d'issues fermées est donc
un **plancher**, jamais un cumul historique.

---

## 5. Les deux faux positifs — preuves et adjudication

Les deux issues ont été **re-vérifiées contre le source à `71d36cd`** et confirmées `OPEN` avant
toute mutation.

### 5.1 `pythonbugs:S6466` — `AZ8LG_c4ZSTbxoM2Q4sD`

`app/services/body_intelligence.py:570` · CRITICAL · RELIABILITY:HIGH · ouverte depuis 2026-06-27
Message : *« Fix this access on a collection that may trigger an 'IndexError'. »*

`textRange` offsets 17-28 sur la ligne `    return tuple(bullets[:4])` désignent `bullets[:4]`.

**C'est une tranche, pas un accès indexé.** Le slicing Python est **total** : il borne, il ne lève
jamais. Le flow moteur déduit correctement que `bullets` peut ne contenir qu'un élément, puis
traite la tranche comme un subscript.

```bash
python3 -c "b=['x']; print(b[:4])"   # ['x'] — aucune exception
python3 -c "b=['x']; b[3]"           # IndexError — le cas que la règle vise réellement
```

### 5.2 `Web:S7930` — `AZ9vNjbE3y4VQkKuhkCW`

`app/templates/base.html:132` · CRITICAL · MAINTAINABILITY:HIGH + RELIABILITY:HIGH · ouverte
depuis 2026-07-17
Message : *« Duplicate id "main-content" found. First occurrence was on line 28. »*

```bash
grep -n 'main-content' app/templates/base.html
# 28:       existants. Cible le <main id="main-content">. #}   ← DANS un commentaire Jinja
# 29:    <a class="skip-link" href="#main-content">…</a>        ← fragment href, pas un id
# 132:    <main id="main-content" class="container">            ← la seule occurrence rendue
```

Le commentaire Jinja est ouvert ligne 26 et fermé ligne 28. **L'analyseur Web ne retire pas la
syntaxe `{# … #}`** et a lu un exemple de documentation comme du markup vivant. Il n'existe qu'un
seul `id="main-content"` rendu.

### 5.3 Adjudication

```bash
sonar api POST '/api/issues/do_transition' --data '{"issue":"<KEY>","transition":"falsepositive"}'
sonar api POST '/api/issues/add_comment'   --data '{"issue":"<KEY>","text":"<justification>"}'
```

Relecture autoritative (`api/issues/search?issues=…`) :

| Clé | Règle | `status` | `resolution` | `issueStatus` | `lastChangeSource` |
|---|---|---|---|---|---|
| `AZ8LG_c4ZSTbxoM2Q4sD` | `pythonbugs:S6466` | RESOLVED | FALSE-POSITIVE | FALSE_POSITIVE | USER |
| `AZ9vNjbE3y4VQkKuhkCW` | `Web:S7930` | RESOLVED | FALSE-POSITIVE | FALSE_POSITIVE | USER |

**`FALSE POSITIVE` et non `ACCEPTED`** : dans les deux cas l'analyseur se trompe **sur le code**.
`ACCEPTED` enregistrerait l'outil comme ayant raison et masquerait le défaut de son moteur. Cette
distinction est désormais normative — skill `auren-sonar-diagnosis`.

**Aucune autre issue n'a été adjudiquée.** Pas de marquage en masse.

---

## 6. Agent de remédiation — rendement 0/13 et où vit sa configuration

### Mesure

```bash
git branch -r | grep -c 'remediate-claude'                       # 13
for b in $(git branch -r | grep 'remediate-claude' | tr -d ' '); do
  git rev-list --count origin/claude/sprint-reporting-fitness-app-V7Qr6..$b; done   # 0 × 13
gh pr list --state all --search "remediat" --json number,state   # []
```

| Exécutions | Branches avec ≥1 commit | PR ouvertes | Mergées |
|---|---|---|---|
| **13** (quotidiennes, depuis 2026-07-31, ~09:01) | **0** | **0** | **0** |

Les 13 têtes de branche sont des ancêtres du tronc. Rendement = **0/13**.

### Diagnostic

| Hypothèse | Verdict |
|---|---|
| Non activé pour ce tier | **REJETÉE** — 13/13 exécutions à l'heure. |
| Ne vise que le code neuf, déjà propre | **REJETÉE** — la fenêtre New Code contenait 79 854 lignes, 547 code smells neufs, 19 bugs neufs. |
| Personne ne relit ses branches | **REJETÉE comme cause** — 0 commit, donc aucune PR possible. Conséquence, pas cause. |
| Base périmée / dérive | **PARTIELLE** — les 6 premières exécutions (31/07 → 05/08) partent toutes de `5a85d67` (30/07) alors que le tronc avançait de 7 commits ; suivi du tronc à partir du 06/08. Réel, mais n'explique pas un rendement nul. |
| **Le jeu de règles éligibles ne recoupe pas les règles du projet** | **✅ RETENUE** |

**68,9 % du stock ouvert est `external_*`**, que l'agent ne peut structurellement pas corriger —
y compris les 4 règles les plus volumineuses. Il tourne, ne trouve rien d'éligible, et laisse une
branche vide.

### Le pilotage n'est PAS contrôlé par le dépôt

```bash
git ls-files | grep -iE 'sonarcloud|sonarlint|\.sonar|remediat|autofix'
# docs/SONARCLOUD_TRIAGE_TEMPLATE.md   ← un document, aucune configuration
grep -rl -i 'remediat' .github/        # aucun résultat
```

Aucun workflow, aucun sélecteur d'éligibilité, aucun fichier de configuration dans le dépôt. La
fonctionnalité est un service **côté SonarQube Cloud** agissant via la GitHub App, gouverné par :

```bash
sonar api GET '/api/settings/values?component=…&keys=sonar.issues.issueResolution.enabled'
# {"value":"true","inherited":true,"parentValue":"true","parentOrigin":"ORGANIZATION"}
```

→ **réglage au niveau ORGANISATION `mfe-dss`**, hérité par le projet sans surcharge locale.

**Aucun remplacement n'a été inventé.** Le modèle de files A/B/C
(`SONAR_NATIVE_ACTIONABLE` / `EXTERNAL_ANALYZER` / `ADJUDICATION_REQUIRED`) et la règle « si la
file native est vide, ne pas créer de branche » **ne sont pas implémentables depuis ce dépôt**.

### Action de suivi minimale (hors périmètre de ce sprint)

Décision opérateur, dans l'UI SonarCloud de l'organisation `mfe-dss` :

1. soit **désactiver** la remédiation automatique pour ce projet tant qu'elle ne produit rien —
   supprime 13 branches vides par quinzaine ;
2. soit la **conserver** et lui donner du travail éligible : c'est le lot §8, uniquement composé
   de règles Sonar-natives.

Ces deux options exigent un accès d'administration à l'organisation. Aucune n'est réalisable par
un commit.

---

## 7. Stock d'accessibilité réel — à traiter séparément

L'adjudication des deux CRITICAL ne doit pas masquer ceci : **le reste des BUG est légitime et
non traité.**

| Règle | Ouvertes | Nature |
|---|---|---|
| `Web:InputWithoutLabelCheck` | **13** | champs sans nom accessible |
| `Web:ItemTagNotWithinContainerTagCheck` | 5 | `<li>` hors `<ul>`/`<ol>` |

Vérifié sur échantillon — `app/templates/_partials/exercise_card.html:353` :

```html
<input type="text" inputmode="decimal" pattern="[0-9]*[.,]?[0-9]*"
       autocomplete="off" name="set_{{ sl.id }}_weight_kg" placeholder="kg" … />
```

Ni `id`, ni `aria-label`, ni `<label>` associé. **Un `placeholder` n'est pas un nom accessible.**

**Recommandation** : tranche A11Y explicite et séparée. Ne pas la mélanger à un sprint de
gouvernance — ce sont de vraies corrections d'interface, avec un vrai risque de régression
visuelle, et elles méritent leur propre revue.

---

## 8. Lot de remédiation différé — proposé, NON exécuté

Cible : le stock **Sonar-natif** que le gate Clean-as-You-Code ne fermera jamais et qu'aucun
humain ne priorisera.

| Règle | Ouvertes | Effort Sonar | Emplacement | Nature |
|---|---|---|---|---|
| `python:S9073` | 46 | 230 min | 100 % `tests/` | mécanique |
| `python:S5778` | 13 | 65 min | 100 % `tests/` | mécanique |
| `css:S4666` | 11 | 11 min | 2 fichiers CSS | mécanique |
| `python:S9083` | 10 | 10 min | 100 % `tests/` | trivial |
| **Total** | **80** | **316 min (5,3 h)** | **46 fichiers, 0 module applicatif** | |

Coût de revue humaine estimé : ~1,5-2 h pour 80 hunks mécaniques sans logique métier.
`sonar remediate --issues` plafonne à 20 clés → 4 invocations.

**Réserve honnête** : vider l'arriéré `S9073` **n'empêche pas** de futurs échecs de gate sur
`S9073`, puisque le gate PR ne regarde que le diff. Le remède contre la récurrence est le
pré-scan AST local (`f5097c9`), pas ce lot. Le lot achète la note projet et la résorption, pas la
stabilité des PR.

**À ne jamais déléguer** : `python:S3776` ×27 (complexité cognitive, 407 min) — refactoring de
logique métier, exige un humain avec la spec.

**Aucune de ces 80 issues n'a été touchée par ce sprint.**

---

## 9. Canal PR et route de diagnostic

### Le bot Sonar ne porte aucun finding localisé

6 PR mergées échantillonnées sur toute la période (#19, #37, #47, #55, #67, #82) :

| Canal | Constat |
|---|---|
| `sonarqubecloud[bot]` — commentaires de conversation | 1 par PR, **résumé de Quality Gate uniquement** (pass/fail, compteurs, couverture, liens) |
| `sonarqubecloud[bot]` — commentaires de revue **inline** | **0 sur les 6 PR** |
| `gitar-bot[bot]` — inline | **le seul** à poster des findings localisés (#67: 2, #82: 2) |

Chronologie sur la PR #82 : dernier commit `fda8a2e` à 12:02:50Z, commentaire Sonar créé à
12:16:13Z et **jamais édité** → **+13 min 23 s après la dernière poussée**.

**Le commentaire Sonar ratifie ; il ne déclenche pas.** Le vrai canal d'interopérabilité est
**local** : échec du check requis en CI → requêtes API locales → correction → re-mesure locale,
le tout **avant que le commit existe** (`f5097c9`, poussé 57 min avant le commentaire du bot).

### Route de diagnostic corrigée

La consigne consignée dans `ROADMAP_AND_NEXT_STEPS.md` (« `api/issues/search` renvoie `TOTAL 0`,
auth manquante ») **n'est plus vraie**. La CLI authentifiée rend le finding exact en un appel :

```bash
sonar auth status   # [✓ Connected] — token en trousseau OS, jamais dans le dépôt
sonar list issues --project MFE-DSS_workout-session-tracking --pull-request 82 --format json
# total: 1 → python:S9073 MAJOR …:tests/test_zone_recovery.py
```

C'est exactement le finding que `4ef0c9f` documente comme ayant coûté « deux suppositions » et
« trois cycles de CI » à localiser.

**Livré** : skill `auren-sonar-diagnosis` (route ordonnée, piège de pagination, distinction
`FALSE POSITIVE` / `ACCEPTED`, non-fixabilité des règles externes) · `auren-standing-merge`
pointe désormais vers cette route · la leçon périmée du roadmap est marquée **partiellement
périmée** sans réécriture de l'historique.

> **La CLI est une aide au diagnostic. Le Quality Gate SonarCloud distant reste l'autorité de
> merge.**

---

## 10. Liaison VS Code

`.vscode/settings.json` (**non versionné** — `.gitignore:20`) déclarait une liaison Connected Mode
vers `projectKey: "workout-session-tracking"`, **le projet orphelin** laissé par `4945c5a`, et non
le projet gaté `MFE-DSS_workout-session-tracking`. Les deux clés existent encore dans
l'organisation.

**Décision** : la liaison obsolète a été retirée localement ; les réglages `python.testing.*` non
liés ont été **préservés**. L'extension SonarQube for IDE a immédiatement rétabli la liaison
d'elle-même, cette fois vers la **clé canonique** `MFE-DSS_workout-session-tracking`. État final
correct, toujours local, **aucun commit** (chemin ignoré par git).

**Aucune liaison écrite à la main n'a été commitée. Aucun identifiant n'a été inventé ou
versionné.**

Si une liaison partagée en équipe devient souhaitable, le mécanisme canonique est le
**shared binding exporté par SonarQube for IDE sous `.sonarlint/connectedMode.json`** — export
depuis l'IDE, jamais un fichier rédigé à la main.

Observation annexe, non corrigée (hors périmètre) : ce fichier active `unittest` avec le motif
`*_test.py` alors que le dépôt utilise `pytest` avec `test_*.py`. Signalé, laissé tel quel.

---

## 11. Appendice de closeout

### Livraison

| | |
|---|---|
| PR | **#84** — 5 checks verts (Gitar, SonarCloud, SonarCloud Code Analysis, lint, pytest+QA) |
| Head mergé | `8d8f388` (merge épinglé `--match-head-commit`) |
| Merge commit | **`6d16357`** — `--merge`, **sans squash, sans `--admin`, sans force** |
| Gate Sonar PR | `status: OK` (0 new issue) · 0 thread non résolu · Gitar **Approved, no issues found** |
| CI canonique | **`31675257579` — 3/3 success** sur `6d16357` |
| Analyse Sonar canonique | `6d16357`, 2026-08-13T06:50:15Z |
| Fichiers | 5 — `.claude/skills/**` ×2, `docs/ops/**` ×1, `docs/strategy/**` ×2. **0 fichier `app/`.** |

La CI canonique **n'a pas été skippée** : deux fichiers sont sous `.claude/skills/`, hors du glob
`paths-ignore: docs/**`. Le job `test` s'est bien exécuté, mais a classé le diff `NON_RUNTIME` et
sauté la suite — d'où l'artefact de couverture analysé en §3bis.

### ⛔ Arrêt dur — ce que ce sprint n'a PAS obtenu

**PHASE 2 a échoué.** La définition New Code est inchangée. Preuve, permission manquante et action
opérateur : encadrés §1 et §2.

**Action requise, non automatisable :** UI SonarCloud → *Project Settings → New Code* →
**Number of days = 30**, par un membre du groupe **`Owners`** de `mfe-dss`. Tant que ce n'est pas
fait :

- le gate projet restera `ERROR` pour une raison de périmètre et non de code ;
- tout merge `NON_RUNTIME` continuera de faire tomber `new_coverage` à 0 sur la branche canonique.

### Registres — mis à jour, après attente d'une session parallèle

Au moment de rédiger le closeout, une **autre session** détenait des modifications **non
commitées** dans `SPEC_REGISTRY.md` et `ROADMAP_AND_NEXT_STEPS.md` (sa ligne
`Sb_RECOVERY_EXPLAINER_01`). Les stager aurait aspiré son travail en cours dans ce commit —
`git add` prend le fichier entier, pas un hunk. **Les deux fichiers ont donc été laissés
intacts** jusqu'à ce que cette session commite et pousse son closeout (`d68fa3d`).

Une fois `origin` et le local alignés sur `d68fa3d` (0 commit d'écart, rien de non poussé chez
l'autre agent), les deux registres ont été mis à jour :

- statut → **`🟠 MERGED — CORRECTION NEW CODE NON ABOUTIE, action opérateur requise`** ;
- la phrase « Corrigé en 30 jours glissants » a été **remplacée par le constat d'échec** dans les
  deux registres — elle était fausse et aurait survécu comme un fait.

### Vérification de portée des mutations SonarCloud

Aucune fuite hors du projet ciblé — prouvé par le projet orphelin non touché (§2). Deux mutations
seulement, toutes deux relues :

| Mutation | État final |
|---|---|
| `sonar.leak.period` = `30` | persiste, **inerte**, laissée en place, documentée comme telle |
| `pythonbugs:S6466` `AZ8LG_c4ZSTbxoM2Q4sD` | `FALSE_POSITIVE` / `lastChangeSource: USER` + justification |
| `Web:S7930` `AZ9vNjbE3y4VQkKuhkCW` | `FALSE_POSITIVE` / `lastChangeSource: USER` + justification |

### Observation d'exploitation

`gitar-bot[bot]` signale que le budget de traitement automatique de son essai est **épuisé pour la
période** : les revues automatiques sont **en pause** et devront être déclenchées à la main
(commentaire `Gitar review`) jusqu'à mise à niveau. Ce sprint a bien reçu sa revue (Approved).
