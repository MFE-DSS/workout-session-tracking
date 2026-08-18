# `DESIGN_DECISIONS_HOME_UIV2_01` — versionner le relevé de décisions Accueil

**Base** : `c2a2a45` · **Tier `check_scope`** : `ISOLATED` · **Aucune implémentation UI**

---

## 1. Pourquoi ce sprint existe

Le brainstorm Accueil du 2026-08-17 a produit cinq décisions validées par
l'opérateur. Elles vivaient dans `docs/DESIGN_DECISIONS_HOME_UIV2.md`, **non
suivi par git**, depuis une journée et quatre sprints.

Un relevé de décisions non versionné n'existe pas : il disparaît au premier
nettoyage de l'arbre de travail, et le travail de brainstorm avec lui. C'est le
seul objectif de ce sprint. **Rien n'est construit.**

---

## 2. Ce qui est versionné

| Décision | Contenu |
|---|---|
| **D1** | Contrat d'interactivité hybride — un registre d'étiquette, trois rangs de contrôle, tous ≥ 44 px |
| **D2** | Badge « RECOMMANDÉ ⓘ » en bleu, avec la vraie raison du moteur — **« Recommandé IA » interdit** |
| **D3** | Sémantique des couleurs : ambre = action, bleu = origine système, graphite = structure |
| **D4** | Quatre suppressions — retirer avant d'embellir |
| **D5** | Substitution descriptif → objets visuels de cockpit, dérivés des données et assets existants |

Plus la **rigueur de maquette** (ne jamais montrer une vignette amputée ; pas de
friction d'objets), qui vient de deux reproches opérateur explicites.

### Ce que le document a gagné en étant versionné

**Les cibles de D4 sont désormais localisées et vérifiées présentes** :

| À retirer | Où |
|---|---|
| « Aucune séance active » | `app/templates/index.html:48` |
| doublon « Aujourd'hui » | `app/templates/index.html:26` |
| vignette « Cette semaine » vide | `_partials/weekly_loop.html:8,14` · `_partials/home_coaching_loop.html:176` |

Vérifiées **encore présentes** au 2026-08-18 : la décision reste actionnable plus
tard sans rouvrir le dogfood. **Aucune suppression n'a été effectuée.**

### Une section corrigée, pas recopiée

Le brainstorm concluait que l'état corporel était « de l'assemblage ». **C'était
faux**, et quatre sprints l'ont établi depuis : le rendu colorait par rang DOM,
`zone_recovery` n'atteignait aucun template, 4 zones sur 11 seulement ont une
géométrie, et les maillages ne sont pas versionnés.

Recopier la conclusion d'origine aurait figé une erreur dans un document de
référence. La section est remplacée par l'état réel et par ce qui reste : de la
**géométrie**, produite hors dépôt.

---

## 3. La garde

Deux protections, volontairement légères. Aucune ne préjuge de l'implémentation.

**1 — le relevé survit.** `git ls-files --error-unmatch` vérifie que le document
est réellement suivi, et non simplement présent sur le disque. Les cinq décisions
et les cibles de D4 doivent y rester.

Cette garde s'est **auto-démontrée** : lancée avant `git add`, elle échouait avec
« is not tracked by git » — précisément le défaut qu'elle existe pour empêcher.

**2 — l'interdit de D2 est appliqué tout de suite.** Aucune surface applicative
ne peut revendiquer « Recommandé IA » (ni sept variantes). C'est la **seule**
décision exécutable avant build, parce qu'elle **interdit** quelque chose au lieu
d'exiger quelque chose. Le moteur se décrit lui-même comme *« Deterministic,
explainable, zero-ML »* : la revendication serait fausse le jour où quelqu'un
l'écrirait, pas le jour où on la relirait.

Un test exige aussi que le document **conserve la raison** de l'interdit — un
bannissement sans son motif se fait annuler par la personne suivante.

**Ce que la garde ne fait pas** : elle ne vérifie pas que l'Accueil a changé. Il
n'a pas changé, et un test qui l'exigerait serait faux.

---

## 4. Acceptation

| # | Critère | Méthode | Résultat |
|---|---|---|---|
| A1 | Document présent dans git | `git ls-files --error-unmatch` | **PASS** |
| A2 | Aucune modification `app/` | §5 | **PASS** |
| A3 | Aucune implémentation UI | §5 | **PASS** |
| A4 | Statut « documented, not built » | marqueur dans le doc + test | **PASS** |

---

## 5. A2 / A3 — parité

| Cible | Diff |
|---|---|
| `app/templates/**` · `app/static/**` · `app/routers/**` | **vide** |
| `app/services/**` · `app/models.py` · `migrations/` | **vide** |
| BodyMap (`bodymap_frames.py`, plaques, contrat) | **vide** |
| planificateur · substitution | **vide** |

Le sprint ajoute **un document** et **un fichier de test**. Rien d'autre.

---

## 6. Vérifications locales

| Check | Résultat |
|---|---|
| `check_scope.py` | `ISOLATED` |
| ruff (fichier neuf) | propre |
| `check_ruff_budget.py` | 281 ≤ 548 |
| `check_spec_protocol.py` | OK |
| Suite dédiée | **7 passés** |
| Broad sweep surfaces Accueil | **362 passés** |

---

## 7. Limites

**Aucune décision n'est implémentée.** D1 à D5 restent des décisions.

**Ce document n'est pas une spec de build.** Il fixe *quoi* a été décidé, pas
*comment* ni *dans quel ordre*. Les tranches d'implémentation restent à écrire.

**D5 reste une direction**, pas un inventaire d'objets visuels à produire.

**La traduction des bandes de récupération en libellés produit n'est pas
tranchée** — même piège de double vocabulaire que le ressenti musculaire, où
`Sb_SESSION_REVIEW_SIGNAL_01` a délibérément affiché la valeur brute plutôt que
d'inventer une seconde table de libellés.

**Une seule décision est gardée par test** (l'interdit D2). Les quatre autres
exigent du rendu pour être vérifiables ; les garder maintenant demanderait
d'inventer des sélecteurs pour une UI qui n'existe pas.

---

## Verdict

**DOCUMENTED — NOT BUILT.**

Cinq décisions validées sortent d'un fichier non suivi et entrent dans le dépôt,
avec les cibles de D4 localisées et vérifiées, et une section corrigée plutôt que
recopiée — le brainstorm se trompait en jugeant l'état corporel « de
l'assemblage », et un document de référence ne doit pas figer une erreur.

La garde la plus utile n'est pas celle qui protège le fichier : c'est celle qui
applique **maintenant** la seule décision applicable avant build. « Recommandé
IA » ne pourra pas apparaître par inadvertance dans six mois, quand personne ne
se souviendra que le moteur est déterministe et que le mot serait un mensonge.
