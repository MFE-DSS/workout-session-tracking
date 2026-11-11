# DOGFOOD — TRAIN A Environment 01 — PROTOCOLE TERRAIN

**Statut** : 🟡 **READY FOR FIELD EVIDENCE / OPERATOR EVIDENCE PENDING**
**Type** : protocole terrain — docs-only (aucun code, test, gabarit, CSS ni donnée)
**Préparé le** : 2026-10-09
**Version servie** : `7d34fa237e7744f8d070c76454fe2447f25dd3eb` — canonique = production,
vérifié sur `/healthz/strict` le 2026-10-09 (déployée le 2026-10-04 22:05 UTC)
**Ligne de base** : 109 séances en production au déploiement, **109 au 2026-10-09** — aucune
séance enregistrée depuis la mise en ligne de TRAIN A. La fenêtre part de zéro.
**Fenêtre cible** : 5 séances de force réelles **ou** 10 jours calendaires, le premier atteint.

**⚠️ Aucune observation n'est préremplie, et aucune ne le sera.** Pas d'environnement, de
séance, d'attente ni de résultat fabriqués. Les matrices synthétiques existent déjà dans les
tests de TRAIN A ; cette phase est **terrain**. Un seul environnement réellement fréquenté =
un seul environnement rapporté.

---

## 1. Les cinq questions auxquelles le terrain doit répondre

| # | question | qui peut y répondre |
|---|---|---|
| Q1 | Puis-je déclarer mon environnement réel sans friction ni doute ? | vous seul |
| Q2 | AUREN garde-t-il des séances plausibles, ou devient-il trop prudent ? | base + vous |
| Q3 | Les adaptations automatiques sont-elles utiles et compréhensibles ? | base (partiel, voir §4) + vous |
| Q4 | START refuse-t-il un jour ce que je juge exécutable ? | **vous seul** (voir §4) |
| Q5 | La recommandation consciente du lieu augmente-t-elle ou baisse-t-elle ma confiance ? | vous seul |

Aucune de ces questions ne se tranche par un test unitaire.

---

## 2. Dette connue — enregistrée AVANT le terrain

Ces sujets ne comptent **pas** comme des découvertes du dogfood. Chaque occurrence est
consignée avec son **impact utilisateur** (§8.5), rien de plus.

| id | dette | classe |
|---|---|---|
| `KNOWN-CUR-01` | « Dips pectoraux (buste penché) » n'est prouvable natif nulle part : le registre de 29 objets n'a aucun poste à dips. En environnement complet, il peut être substitué. | `KNOWN DEBT` — curation |
| `KNOWN-DEF-01` | 7 alias atlas vérifiés, non appliqués | `KNOWN DEBT` — différé |
| `KNOWN-DEF-02` | identités d'exercice restées inconnues | `KNOWN DEBT` — différé |
| `KNOWN-DEF-03` | trous du vocabulaire `pattern_motor` | `KNOWN DEBT` — différé |
| `KNOWN-DEF-04` | un seul lieu par utilisateur | `KNOWN DEBT` — capacité future |
| `KNOWN-DEF-05` | pas de surcharge d'environnement pour une séance | `KNOWN DEBT` — capacité future |

**`KNOWN-CUR-01` s'escalade** si le terrain montre l'un de ces effets : gêne réelle ·
substitut mauvais · perte de confiance · contournement manuel répété · évitement de la
recommandation. L'escalade change sa priorité, pas sa classe.

Aucun de ces sujets n'est implémenté pendant le dogfood.

---

## 3. Ce que le produit enregistre déjà — vous n'avez pas à vous en souvenir

Lu dans le code de `7d34fa2`, pas dans la prose.

| signal (§7 de la mission) | où il vit | fiabilité |
|---|---|---|
| recommandation présentée + alternatives | `recommendation_episodes.proposed_top_slug`, `proposed_alt_slugs` | MESURÉ |
| acceptée ou non | `recommendation_episodes.outcome`, `chosen_slug`, `session_id` | MESURÉ |
| environnement déclaré au moment de la décision | suffixe `\|env:<identité>` de `context_fingerprint` — absent si non déclaré | MESURÉ — à confirmer à la 1ʳᵉ ingestion |
| changement d'environnement entre deux décisions | changement de ce suffixe | MESURÉ (date d'effet, pas le contenu) |
| inventaire déclaré | `training_preferences.available_equipment_items` + `updated_at` | **PARTIEL** — seule la valeur courante est conservée, pas l'historique |
| prescrit → exécuté | `session_exercises.exercise_name_snapshot` → `substituted_name` | MESURÉ |

Lecture **uniquement sur un export en lecture seule**. Jamais la base de production en
place, jamais une écriture en production.

---

## 4. Ce que le produit ne sait PAS — trois angles morts de l'instrument

Constatés dans le code **avant** le terrain. Ce ne sont pas des découvertes du dogfood, et
**aucun n'est corrigé pendant le dogfood** (no-goal : pas de code de production). Ils bornent
ce qu'on aura le droit de conclure.

**`IA-01` — adaptation automatique et substitution manuelle sont indiscernables en base.**
La pose d'avant START (`app/routers/sessions.py:168`) et la substitution en cours de séance
(`app/routers/sessions.py:1311`) écrivent le même `substituted_name`, sans marqueur de
source. Une reconstruction par rejeu du préflight est possible, mais c'est une **INFÉRENCE**,
valide seulement si l'environnement n'a pas changé depuis le START. Votre note tranche.

**`IA-02` — un START refusé ne laisse aucune trace en base.** Le refus sort
(`sessions.py:221` et `:236`) **avant** l'écriture de l'épisode de conseil (`sessions.py:248`).
**Q4 repose donc entièrement sur vos notes.** C'est le seul événement à me signaler sans
faute, même en un mot.

**`IA-03` — compréhension, préférence, confiance.** Par nature, seulement vous.

---

## 5. Forme d'une note — la plus courte qui serve

```
ÉCRAN / MOMENT     :
CE QUE JE FAISAIS  :
CE QUE J'ATTENDAIS :
CE QUI S'EST PASSÉ :
```

Facultatif : capture · id de séance · exercice · changement d'environnement · gravité
ressentie.

**Aucun diagnostic demandé.** « Pourquoi il m'a recommandé ça ? » est une preuve valable.
« Le résolveur a mal classé un inconnu » est une hypothèse, que je vérifie. Dicté en vrac,
dans n'importe quel ordre, ça marche. **Il n'y a pas de questionnaire à remplir.**

---

## 6. Mon contrat d'ingestion — ce que je fais de chaque note

1. **Archiver verbatim** (§8.3). Je ne reformule jamais la note d'origine.
2. **Croiser** avec l'export en lecture seule (§3), séance par séance.
3. **Tester l'arrêt dur d'abord** (§7). Rien d'autre n'est conclu tant qu'il n'est pas écarté.
4. **Une seule classe primaire** par constat — jamais deux :

   | classe | critère | exemple |
   |---|---|---|
   | `DEFECT` | objectivement cassé, faux, perdu, incohérent ou dangereux | données de séance perdues |
   | `PRODUCT DECISION` | conforme au contrat, mais le choix produit est mauvais | reco correcte mais absurde à l'usage |
   | `CAPABILITY ABSENCE` | la V1 ne le permet tout simplement pas | un lieu Maison et un lieu Salle |
   | `KNOWN DEBT` | documenté au §2 avant le terrain | Dips substitué faute de poste à dips |

5. **Étiqueter la preuve** : `MESURÉ` (base) · `INFÉRENCE` (reconstruction) · `RAPPORTÉ` (vous).
6. Aucun vocabulaire de capacité interne dans ce que vous lisez.

---

## 7. Arrêt dur — règle de correction immédiate

L'un de ces constats **arrête le dogfood structurel** :

- séance non persistée ;
- mauvais exercice persisté ;
- lignée prescrit → exécuté perdue ;
- environnement déclaré perdu silencieusement ;
- l'environnement d'un utilisateur visible par un autre ;
- START contourne un refus ;
- une adaptation requise partiellement posée atteint la console ;
- une donnée fausse présentée comme un fait.

Sortie : **`DOGFOOD BLOCKED BY FUNCTIONAL DEFECT`**, avec observation exacte, reproduction si
établie, route et données touchées, preuve, et plus petit périmètre de réparation.

**Aucun correctif automatique** sans `GO BUILD` explicite sur ce défaut. Aucune conclusion
d'usage ne se tire sur une base corrompue.

---

## 8. Registre de terrain — vide, rempli par moi à chaque note

### 8.1 Environnements réellement fréquentés

| lieu (générique) | état déclaré | première séance | dernière séance |
|---|---|---|---|
| | | | |

État déclaré ∈ `NON DÉCLARÉ` · `SANS MATÉRIEL` · `INVENTAIRE`.

### 8.2 Séances observées

| date | séance | état env. | reco présentée | acceptée | l'env. a changé le gagnant | adaptations auto | substitutions manuelles | refus START | source |
|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | |

### 8.3 Notes brutes, verbatim

*(aucune)*

### 8.4 Constats classés

| # | classe | constat | preuve | étiquette | gravité ressentie |
|---|---|---|---|---|---|
| | | | | | |

### 8.5 Occurrences de dette connue

| date | id | ce qui s'est produit | impact utilisateur | escalade ? |
|---|---|---|---|---|
| | | | | |

### 8.6 Impact des identités inconnues — entrée du prochain sprint de curation

| identité canonique | équipement réel visé | vous l'aviez ? | conséquence |
|---|---|---|---|
| | | | |

Conséquence ∈ `AUCUNE` · `SUBSTITUTION EN TROP` · `REFUS À TORT` · `CONTOURNEMENT MANUEL` ·
`PERTE DE CONFIANCE`. **Trié par impact observé**, jamais par ordre alphabétique ni par
facilité. Les 7 alias déjà vérifiés restent candidats sans primer d'office.

### 8.7 Confiance dans la recommandation, avant / après

Note qualitative ordinale (« moins » · « pareil » · « plus »), jamais un score fabriqué.

| moment | lecture | ce qui l'a fait bouger |
|---|---|---|
| | | |

---

## 9. Ce qu'on ne pourra pas conclure

- Un seul lieu fréquenté ne dit **rien** des environnements Maison ou Sans matériel.
- Cinq séances ne donnent **aucune** fréquence ; elles donnent des cas.
- Une adaptation dite « automatique » sans votre confirmation reste une **INFÉRENCE** (`IA-01`).
- Une absence de refus en base ne prouve **pas** qu'aucun refus n'a eu lieu (`IA-02`).
- Les tests synthétiques de TRAIN A ne remplacent aucune ligne de ce registre.

---

## 10. Verdicts autorisés en fin de terrain

| verdict | quand |
|---|---|
| `PASS — TRAIN A PRODUCT VALIDATED FOR CURRENT V1` | les cinq questions répondent favorablement, aucun défaut |
| `PASS WITH CURATION FOLLOW-UP` | produit sain, frictions concentrées sur des identités inconnues |
| `PRODUCT ARBITRATION REQUIRED` | au moins une décision produit à trancher par vous |
| `DOGFOOD BLOCKED BY FUNCTIONAL DEFECT` | un arrêt dur du §7 |
| `INSUFFICIENT REAL EVIDENCE` | fenêtre écoulée sans assez de séances |

Une décision anticipée n'est permise que pour un défaut fonctionnel dur, ou un échec produit
répété, à fort impact, avec preuve suffisante.

---

## Verdict (préparation)

**Verdict :** 🟡 **TRAIN A DOGFOOD — READY FOR FIELD EVIDENCE.**

Version servie vérifiée (`7d34fa2`, production = canonique). Ligne de base : 109 séances,
aucune depuis la mise en ligne. Dette connue enregistrée **avant** le terrain, pour qu'aucune
ne soit redécouverte. Trois angles morts de l'instrument identifiés dans le code et bornés,
dont un décisif : **un START refusé ne laisse aucune trace en base**, donc Q4 dépend de vos
notes. Registre vide. Aucune observation inventée.

**Prochaine action** : à la première note réelle, ingestion selon le §6 — d'abord le test
d'arrêt dur, puis le classement.
