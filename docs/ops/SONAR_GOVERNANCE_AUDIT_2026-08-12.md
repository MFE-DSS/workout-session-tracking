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

Trois corrections ont été appliquées, toutes **sans toucher au Quality Gate, aux seuils, aux
exigences de merge, ni aux imports d'analyseurs externes** :

1. **New Code projet** : `previous_version` (hérité) → **30 jours glissants**.
2. **Deux faux positifs CRITICAL** adjudiqués `FALSE POSITIVE`, preuve à l'appui, après
   re-vérification du source.
3. **Route de diagnostic Sonar** corrigée dans la documentation d'exploitation : la CLI `sonar`
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

> **Preuve de mode différée.** SonarCloud n'expose pas de lecture `mode = NUMBER_OF_DAYS` : les
> endpoints `new_code_periods/*` renvoient `404` et `/api/v2/new-code-definitions` renvoie `403`
> avec ce token. La preuve autoritative est donc la **période rapportée par la première analyse
> de la branche canonique** postérieure au changement — consignée en §3 (AFTER).

---

## 3. Mesures BEFORE → AFTER

**BEFORE** : `71d36cd`, analyse `609e876` du 2026-08-12T13:05:08Z.
**AFTER** : voir l'appendice de closeout (§11) — nécessite une analyse de la branche canonique
postérieure au merge.

| Mesure | BEFORE | AFTER | Effet attribué |
|---|---|---|---|
| New Code — mode | `previous_version` (hérité INSTANCE) | *(closeout §11)* | **SETTING** |
| New Code — début | `2026-04-10T12:45:26+0000` (124 j) | *(closeout §11)* | **SETTING** |
| `new_lines` | **79 854** | *(closeout §11)* | **SETTING** |
| `ncloc` | 25 874 | *(closeout §11)* | — (aucun code touché) |
| Quality Gate projet | **ERROR** | *(closeout §11)* | SETTING + ADJUDICATION |
| `reliability_rating` | **4.0 (D)** | *(closeout §11)* | **ADJUDICATION** (2 BUG retirés) |
| `security_rating` | 2.0 (B) | *(closeout §11)* | — |
| `sqale_rating` (maintenabilité) | 1.0 (A) | *(closeout §11)* | — |
| `security_review_rating` | 3.0 (C) | *(closeout §11)* | — |
| `coverage` | 92.2 % | *(closeout §11)* | — |
| `new_coverage` | 91.7 % | *(closeout §11)* | SETTING (périmètre change) |
| `duplicated_lines_density` | 0.4 % | *(closeout §11)* | — |
| `new_duplicated_lines_density` | 0.115 % | *(closeout §11)* | SETTING |
| Issues ouvertes — Sonar-native | **233** | *(closeout §11)* | ADJUDICATION (−2) |
| Issues ouvertes — external | **516** | *(closeout §11)* | — |

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

## 11. Appendice de closeout — mesures AFTER

*(Complété après merge, sur la première analyse de la branche canonique postérieure au changement
de définition New Code. Voir §3 pour les valeurs BEFORE correspondantes.)*
