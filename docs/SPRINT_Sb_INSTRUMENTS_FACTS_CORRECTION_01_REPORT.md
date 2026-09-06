# Sb_INSTRUMENTS_FACTS_CORRECTION_01 — l'ontologie relue contre le code

**Tier `check_scope`** : `DOCS`.
**Fichiers** : `docs/strategy/AUREN_INSTRUMENTS.md` + ce rapport.

---

## 1. Pourquoi cette tranche existe

`AUREN_INSTRUMENTS.md` a été écrit pour que l'opérateur y prenne des décisions
produit structurantes : quels objets survivent, lesquels fusionnent, lesquels
meurent. Un document dans ce rôle n'a pas le droit d'être approximatif —
**une affirmation fausse y coûte plus cher qu'une affirmation absente**, parce
qu'elle est arbitrée au lieu d'être cherchée.

Il a donc été relu **fait par fait** contre le code, avec une contrainte de
méthode : chaque réfutation devait elle-même être **contestée par un second
lecteur chargé de la démolir**, pour qu'aucune correction ne repose sur la
première impression d'un relecteur pressé.

**60 affirmations · 29 corrections · 11 réfutations franches · 2 réfutations
elles-mêmes réfutées** *(le premier relecteur avait tort sur la durée de séance
et sur `latest_open_session` ; le document avait raison, il reste inchangé).*

---

## 2. Brainstorming / Options / Risques / Choix retenu

### Option A — ne rien corriger, ajouter un avertissement général

*« Ce document est indicatif. »*

* ❌ Un document normatif sur les dispositions ne peut pas être indicatif sur
  les faits qui les motivent. C'est le pire des deux mondes : on garde
  l'autorité et on abandonne l'exactitude.

### Option B — réécrire le document entier

* ❌ 29 corrections sur 60 affirmations ne justifient pas de perdre les 31
  affirmations vérifiées **et** les dispositions, qui sont l'arbitrage de
  l'opérateur et ne sont pas en cause.
* ❌ Une réécriture efface la trace de l'erreur, donc son enseignement.

### Option C — corriger en place, en signalant chaque correction *(retenu)*

Les passages corrigés portent *« (corrigé) »*, et l'en-tête du document dit
franchement combien d'affirmations étaient fausses et **pourquoi**.

* ✅ Le lecteur voit ce qui a bougé et peut juger la fiabilité du reste.
* ✅ L'enseignement survit — il est en tête, pas enterré dans un rapport.
* ✅ Les dispositions, qui sont l'arbitrage opérateur, ne sont pas touchées.

### Risques

| Risque | Traitement |
|---|---|
| Une correction est elle-même fausse | Chaque réfutation a été contestée par un second lecteur ; 2 corrections ont été **rejetées** à ce titre |
| Le document devient illisible sous les mentions | Les *« (corrigé) »* sont posées sur le passage, pas sur chaque phrase |
| Le même travers recommence | Une **règle** est écrite en tête : aucun nombre, aucun « toutes », aucun « aucune » sans la ligne qui le prouve |

---

## 3. Les corrections qui changent une décision

### 3.1 — Le consentement corporel : plus grave, et ailleurs

**Affirmé** : *« Les routes `/body/*` vérifient toutes `has_active_consent` ;
`POST /profile/measurements` ne le vérifie pas. Cinq autres surfaces lisent
aussi les mesures sans vérifier. »*

**Réel** : `has_active_consent` n'est appelé qu'en **trois points de tout le
dépôt**, et l'un des trois ne garde rien. Sur les **8 routes** de
`app/routers/body.py`, **deux** sont gardées. **Quatre modifient, suppriment ou
exportent des mesures sans aucun contrôle** — vérifié au runtime, consentement
retiré : le POST d'édition écrit, la suppression supprime.

Et le compte de lecture est de **quatre**, pas cinq : `/physique` et
`/dashboard` sont des redirections 303 depuis `TRAIN1-C`.

**Le « toutes » masquait un trou plus grand que celui que je signalais.**

### 3.2 — Le programme « actif » existe, mais pas la distinction

**Affirmé** : *« Notion inexistante. Un index DB la prévoit en commentaire, rien
ne l'implémente. »*

**Réel** : `GET /programs` existe, est montée, est atteignable sous « Mes
programmes », et `list_drafts` rend les programmes **non archivés** — exactement
ce que `MAX_ACTIVE_PROGRAMS` appelle actifs. Ce qui n'existe pas, c'est la
notion d'**un** programme *actuellement suivi*, distinct des autres. Le
triptyque `ACTIF / MIENS / CATALOGUE` bute là, pas sur l'absence de liste.

### 3.3 — Le gâchis de `/progress` était déjà réparé

**Affirmé** : *« `build_weekly_loop` produit 14 clés, `/progress` n'en lit
que 2. »*

**Réel** : 15 clés, et depuis `TRAIN1-C` **`/progress` ne l'appelle plus du
tout** — il appelle `build_progress_week`, un producteur étroit qui ne calcule
que les deux clés rendues. La docstring documente le gâchis **au passé**, comme
sa raison d'être. J'accusais un état corrigé.

### 3.4 — Sept échelles de confiance, pas trois

`MorphologyDescriptor` (4) · `RatioResult` (3) · `ZoneScore` (3, en français) ·
`AxisScore` (4, en français **aussi mais pas les mêmes**) ·
`recovery_contract.Confidence` (4) · `confidence.py` (3, **homonyme** : qualité
du logging d'une séance) · `recommendation_explainer`. **Aucune constante
partagée.** Un `BODY_LEDGER` qui affiche une confiance doit d'abord en élire une.

### 3.5 — Du code mort à l'intérieur du code mort

`adaptive_replan.py` : 387 lignes ✓, mais **trois** dataclasses et non quatre —
`TrainingState` et `WeeklyPlan` y sont *importées*, et `DivergenceKind` est un
`StrEnum`. Et son `DivergenceKind` déclare 5 déclencheurs dont **4 seulement
sont émis** : `INCOMPLETE_SESSION` n'est construit nulle part, ni par son nom ni
par sa valeur.

Le module est **couvert par trois fichiers de tests** et importé par aucun
routeur ni service.

### 3.6 — Deux affirmations que la contestation a sauvées

Le premier relecteur voulait corriger « aucune colonne de durée sur
`WorkoutTemplate` » et « `latest_open_session` rend l'entité ORM entière ». Le
second lecteur, chargé de le démolir, a montré que **le document avait raison**.
Les deux passages restent inchangés.

C'est la justification de la méthode : sans l'étape de contestation, deux
affirmations exactes auraient été « corrigées » en affirmations fausses.

---

## 4. Ce que la passe apprend, et qui vaut plus que les corrections

Trois causes, chacune vue plusieurs fois :

1. **La dette déjà remboursée.** J'accusais des états passés — `/progress`,
   `/physique`, `/dashboard`, la divergence des tokens du viseur (fermée le
   2026-09-04). Un dépôt qui bouge vite rend périmée une exploration d'une nuit.
2. **Le compte fait de mémoire.** 20 au lieu de 18, 14 au lieu de 15, 4 au lieu
   de 3, 3 au lieu de 7, « 6 points » pour une trace qui en compte de 2 à 6.
3. **Le « toutes » et le « aucune ».** Les deux quantificateurs universels les
   plus coûteux du document, et les deux faux. L'un masquait un trou de sécurité
   plus grand ; l'autre transformait un **problème de place** (un repli de
   niveau 3 qui disparaît quand une séance est ouverte) en **problème
   d'absence**, ce qui appelle une tranche entièrement différente.

**Règle écrite en tête du document** : aucun nombre, aucun « toutes », aucun
« aucune » sans la ligne de code qui le prouve.

---

## 5. Vérifications

| Contrôle | Résultat |
|---|---|
| `check_scope` | `DOCS` |
| `check_spec_protocol` | `OK` |
| Périmètre | docs uniquement — aucun fichier d'application, aucun test |

Les **dispositions** — l'arbitrage de l'opérateur sur les 22 objets et les 50
gabarits orphelins — ne sont **pas touchées**. Seules les affirmations
factuelles qui les motivent le sont.

---

## Verdict

**LIVRÉ.** L'ontologie dit désormais ce que le code fait, et signale les
29 endroits où elle disait autre chose.

La correction la plus importante n'est pas dans le tableau : c'est que
**la moitié de ce qu'une exploration de code produit en une nuit est inexact ou
périmé**, et qu'un document destiné à l'arbitrage doit être relu contre le code
*avant* d'être arbitré, pas après. Cette passe a coûté une fraction de ce
qu'aurait coûté une tranche de production bâtie sur « les routes `/body/*`
vérifient toutes le consentement ».

Reste ouvert, et nommé : **le périmètre du consentement corporel** est
maintenant décrit exactement, et il appelle une décision produit — édition,
suppression et export de mesures sont ouverts alors que la création est gardée.
C'est le seul état qui ne se défende pas.

---

## Appendice de clôture — post-merge

| | |
|---|---|
| **PR** | [#220](https://github.com/MFE-DSS/workout-session-tracking/pull/220) |
| **Méthode** | `--merge`, `--match-head-commit 70182f4` |
| **Commit de merge** | `f712786` |
| **CI de PR** | 10/10 verts |
| **Gate Sonar** | `OK` |
| **Fils de revue non résolus** | 0 |
| **CI canonique** | tranche 100 % `docs/` — la CI au push est **légitimement skippée** par `paths-ignore: ['docs/**']`. Ce n'est pas un `[skip ci]` manuel (`CLAUDE.md §2`). Source de vérité : la CI de PR, 10/10 |

### Un écart de pratique à signaler, que je n'ai pas comblé seul

`docs/strategy/SPEC_REGISTRY.md §8` demande que le registry soit mis à jour
**« à la fermeture d'un sprint », « dans le même commit que le sprint report »**.

Relevé : **aucune des ~15 dernières tranches du programme UI n'y figure** — ni
`Sb_UI_SQUAD_FAMILLE_01`, ni `Sb_UI_PHANTOM_TOKENS_01`, ni les autres. La pratique
a cessé sans être abrogée.

Je ne l'ai **pas ravivée pour mes trois tranches seules** : inscrire trois sprints
dans un registre qui en ignore quinze produirait un registre plus trompeur que
vide — il donnerait l'impression que les quinze autres n'existent pas. C'est la
même erreur de forme que la « famille aux deux tiers ».

**C'est une décision d'opérateur** : soit le registry est réanimé et rattrapé sur
les quinze, soit `§8` est amendé pour dire ce qui est réellement pratiqué. Les deux
se défendent ; l'état actuel — une règle écrite que rien n'applique — ne se défend pas.
