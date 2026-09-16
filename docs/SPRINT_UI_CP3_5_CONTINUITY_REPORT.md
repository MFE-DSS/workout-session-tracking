# UI-CP3.5 — CONTINUITÉ

**Tier `check_scope`** : `MIGRATION`.
**Arbitrage opérateur** : continuité adaptative RÉELLE, un seul déclencheur.

```
PLAN DE BASE  +  ADAPTATIONS ACTIVES APPLICABLES  =  PLAN EFFECTIF
```

---

## 1. Le problème, et la correction que l'opérateur a imposée

MISSION était **sans mémoire** : elle recalculait à chaque affichage, et le
même moteur avec le même état produisait la même phrase pour n'importe qui.

Ma première proposition contenait une contradiction que l'opérateur a relevée :
une adaptation ne peut pas être *consultative* et porter `adopted = true`
pendant que MISSION dit « ajusté ». **Recalculer `replan()` à chaque rendu
n'est pas une mémoire — une recomputation pure reste sans état.**

La cible est donc plus forte : la décision doit être **prise à un moment**,
**persistée**, et **changer réellement** la projection du plan.

---

## 2. Le déclencheur a changé — `LIMITING_RECOVERY` est écarté

L'arbitrage initial le visait. L'audit l'a déclaré **BLOCKED EVENT OWNERSHIP**,
sur quatre constats indépendants :

| | |
|---|---|
| **fonction pure du temps** | `estimate = clamp(heures / cible)` (`zone_recovery.py:211`). Le module l'écrit : *« No exponential decay, no half-life »* |
| **tautologique à la clôture** | seuil `LIKELY_FATIGUED` ≥ 9,6 h pour TOUTE zone ; l'écart à la clôture est ≈ 1–2 h. Toute zone entraînée est donc « limitante », toujours |
| **expire sans événement** | ≈2,4 j plus tard tout repasse `LIKELY_AVAILABLE`, sans action |
| **le contrat l'interdit** | `recovery_contract.py:869` : les seuils de bande sont des *« presentation thresholds […] Moving them changes wording, never a decision »* |

**`INCOMPLETE_SESSION` le remplace** — déclaré dans l'énumération depuis
l'écriture du moteur, **émis nulle part**. Piloté par un vrai événement de
domaine, daté par `ended_at`, immuable, non tautologique, et **sans identité
plan↔séance** puisque c'est une propriété de la séance seule.

**Seuil tranché par l'opérateur : moins de 50 %** du travail prescrit effectué.
Constante nommée, jamais un littéral dans une comparaison.

---

## 3. Trois mesures ont réfuté mes propres décisions

C'est le cœur de cette tranche, et il faut le lire dans l'ordre.

1. **Le report faisait GRIMPER une autre zone.** Reporter 6 séries de
   pectoraux rendait un plan effectif où la chaîne postérieure passait de
   **8 à 14 séries**, total conservé. Un utilisateur qui écourte une séance se
   verrait *ajouter* du travail.
2. **Mon garde-fou faisait pire.** Un plafond anti-croissance produisait
   **biceps 4 → 0** — exactement le défaut que la clé de classement n° 1 de
   l'allocateur existe pour empêcher : *« un utilisateur déclarant Bras
   recevait un programme sans le moindre curl »*.
3. **La cause était une erreur de catégorie, de moi.** Le plan de base
   **n'atteint jamais la bande basse du budget** — `pecs` a une bande basse de
   14 pour 12 servis, `biceps` 8 pour 4. Plafonner une BANDE par une
   COUVERTURE inverse la bande sur **huit zones sur onze**. Je comparais deux
   échelles.

Et une mesure isolante a tranché : **le plafond seul ne change rien**
(96 → 96, aucune zone bougée). C'est la combinaison qui déstabilisait.

### Conclusion, et arbitrage

**Dans ce planificateur, un report redistribue nécessairement.** Fait
d'architecture, pas préférence.

L'opérateur m'a laissé trancher. **Redistribution acceptée, MISSION dit
« ajusté »** — trois raisons :

* le plan effectif **diffère réellement** (empreinte + couverture, rejeu
  identique) : c'est la barre du §5, et elle est franchie ;
* rien ne devient plus agressif au sens du contrat — charge totale inchangée,
  cadence inchangée, aucune séance allongée. Le moteur nomme lui-même la
  redistribution comme une issue admise ;
* « proposé » aurait fait de la tranche une mémoire de proposition, ce que la
  correction de l'opérateur visait précisément à écarter.

**Corollaire tranché** : MISSION annonce **le report**, pas la réaffectation.
Celle-ci n'est pas une décision — c'est la réponse déterministe du
planificateur — et sa conséquence est déjà visible dans la ligne causale de la
recommandation.

---

## 4. Ce qui est persisté, et ce qui ne l'est pas

### Le ledger existait déjà, à moitié

`decision_traces` porte l'identité d'exécution, l'identité de contenu
(excluant volontairement `created_at`), l'empreinte de plan, la justification,
l'horodatage — et son **immuabilité est imposée** par un écouteur
`before_update` qui lève plutôt que de laisser réécrire une preuve. Le type
`REPLAN_DELTA` y était **déclaré et jamais émis**. On l'émet.

**Seul le cycle de vie manquait**, et c'est structurel : une trace immuable ne
peut pas porter un `dismissed_at`. D'où une table neuve qui ne contient **que**
`decision_id` + `dismissed_at`.

| État | Représentation |
|---|---|
| `ACTIVE` | une trace `REPLAN_DELTA` sans ligne d'écartement, dont l'empreinte de plan vaut encore |
| `DISMISSED` | une ligne dans la table étroite |
| `SUPERSEDED` | **dérivé** — l'empreinte de plan ne correspond plus au contexte courant |

`SUPERSEDED` n'est pas stocké **délibérément** : le marquer exigerait d'écrire
pendant un `GET`. Le dériver le rend automatique — un changement de cadence
périme les anciennes décisions sans qu'aucun code ne s'en occupe.

### Le piège d'ancrage, évité et documenté

L'adaptation s'ancre sur l'empreinte du plan de **BASE**, jamais de l'effectif.
Ancrer sur l'effectif créerait une boucle : l'adaptation change le plan,
l'empreinte change, l'adaptation paraît périmée, le plan revient.

---

## 5. Où l'on écrit, et où l'on ne écrit pas

**Un seul site d'écriture** : la clôture de séance (`sessions.py`, branche
`action == "end"`), **après** `db.commit()`.

### ⚠ L'ordre n'est pas un détail, et une garde l'a prouvé

Première écriture : l'appel était AVANT le commit. La garde « la trace ne coûte
jamais la clôture » a rougi — la panne simulée déclenchait un `rollback` de la
transaction **entière**, donc de la clôture, et la séance restait
`in_progress`. **La trace emportait le fait qu'elle devait décrire.**

Le précédent du dépôt le fait dans cet ordre pour cette raison exacte :
*« le brouillon prime sur sa trace »* (`user_programs.py`,
`observe_plan_generation`). Patron de sûreté repris tel quel — ne lève jamais,
`rollback` imbriqué, journalisation.

**Aucune écriture au `GET`.** Une garde compte les lignes avant et après
plusieurs affichages de l'accueil.

---

## 6. Où le plan effectif est consommé

| Surface | Effet |
|---|---|
| **matérialisation** (`POST /programs/from-plan`) | le programme créé suit le plan EFFECTIF — sans cela, MISSION dirait « ajusté » pendant que le produit matérialiserait le plan d'avant |
| **aperçu** (`/plan`, `/programs`) | montre ce qui serait réellement matérialisé |
| accueil | **non câblé, délibérément** — MISSION ne rend plus le plan depuis `UI-CP3` ; composer l'adaptation là coûterait deux constructions de plan sur la route la plus chaude, pour un rendu inexistant. Exactement les cinq calculs morts que `UI-CP3` vient de retirer |

Un **point d'entrée unique** (`effective_plan_for_user`) : deux surfaces qui
composeraient l'adaptation chacune à leur manière divergeraient au premier
correctif.

---

## 7. Deux défauts que seul le RENDU a trouvés

### Une séance entièrement abandonnée ne déclenchait rien

Mesuré : 0 série sur 21, clôturée, **zéro trace**. Cause —
`work_sets_by_zone` omettait les zones à zéro, donc une séance abandonnée
paraissait « aucune zone touchée », quand une séance à UNE série produisait un
report. Exactement à l'envers.

**Les deux absences ne sont pas la même** : un exercice que le résolveur ne
sait pas classer est une IGNORANCE ; un exercice classé qui a livré zéro est un
FAIT. Corrigé, avec une garde pour chacune des deux.

Les gardes unitaires ne l'avaient pas vu : elles n'exerçaient que des séances
partiellement faites.

### MISSION redevenait un flux

Sur cette même séance, le bloc rendait **quatre lignes de report** —
« Deltoïdes latéraux 12 → 0 · Deltoïdes postérieurs 8 → 0 · Pectoraux 12 → 1 ·
Triceps 4 → 0 ». Un flux d'historique, ce que `§11` interdit, et un écran qui
se lit « ta semaine est annulée ».

On montre la zone la plus **matérielle**, on compte les autres, et on dit le
total. Rien n'est caché — seule l'énumération disparaît. Une garde pinne
**une** ligne de report.

Plus un défaut de grammaire : « 12 → 1 **séries** ». Le filtre `pluriel`
existait déjà.

---

## 8. Vocabulaire (`§9`, `§10`, et `SPEC §8.4`)

Jamais « manqué », jamais « en retard » : sans instance planifiée datée, ces
mots imputent une faute que le modèle ne peut pas prouver. Du factuel —
*« Séance terminée à 1 série sur 21 »*, *« reportées »*.

`Sx_RECOVERY_READINESS_01_SPEC §8.4` **exige** un test de wording dans toute
tranche produisant du texte utilisateur. Il est embarqué, il lit le **HTML
rendu** et non le gabarit, et il porte sa propre garde d'anti-vacuité.

---

## 9. Les sept preuves du contrat

| | Preuve | Tenue par |
|---|---|---|
| **A** | une clôture qualifiante crée UNE décision | `test_preuve_A_*` + sa moitié inverse : une séance à 90 % n'en crée aucune |
| **B** | des `GET` répétés n'écrivent **rien** | comptage des lignes avant/après huit affichages |
| **C** | des `GET` répétés exposent la **même identité, même date, même delta** | trois lectures, un seul tuple distinct |
| **D** | le **plan effectif reflète** le delta | empreinte + couverture, comparaison directe base vs effectif |
| **E** | la décision reste **immuable** | l'écouteur `before_update` lève sur nos lignes |
| **F** | l'écartement **retire l'effet**, la trace **survit** | les deux moitiés dans la même garde |
| **G** | un contexte supersédant **empêche** l'action | cadence 3 ↔ 4, le plan effectif redevient le plan de base |

Plus : aucune augmentation · cardio ne déclenche jamais · l'échauffement ne
compte pas · un exercice non classé reste omis · une seule ligne de report.

**36 gardes.** **Dix mutations plantées, dix rougissent la bonne garde**, arbre
restauré octet pour octet.

### ⚠ Deux de mes gardes ne gardaient rien

Attrapées par mutation, et pour la même raison les deux fois : **mon entrée
n'atteignait jamais la branche protégée**. Un dictionnaire vide passé à une
fonction qui itère dessus ; un report négatif écarté avant la transformation.
Vertes pour une raison qui n'était pas la leur. Corrigées, puis re-mutées.

---

## 10. Vérifications

| Contrôle | Résultat |
|---|---|
| `check_scope` | **`MIGRATION`** |
| `check_migration_patterns` | OK |
| `check_alembic_drift` | OK |
| `check_schema_snapshot` | OK |
| `check_migration_roundtrip` | OK |
| `ruff` | propre sur les fichiers de la tranche ; 1 `C901` **préexistant** sur `session_detail` |
| pré-scan `S9073` | 0 |
| Rendu exposé à l'opérateur | **avant tout commit de gabarit** (`§5.1`), dans les trois états |

⚠ **Le drift m'a accusé à tort, et c'est moi qui avais tort.** Je lançais
`python scripts/check_alembic_drift.py` — par chemin de fichier, ce qui met
`scripts/` sur `sys.path` **à la place de la racine** et fait résoudre `app`
vers un autre arbre. La docstring du script dit `python -m`. C'est la troisième
forme consignée de « mesurer le mauvais objet », et j'y suis retombé.

---

## 11. Ce que cette tranche N'OUVRE PAS

`MISSED_SESSION` (bloqué jusqu'à des instances planifiées datées) ·
`SHORTENED_SESSION` (bloqué jusqu'à une durée planifiée) · `CONSTRAINT_CHANGE`
(différé) · `LIMITING_RECOVERY` (écarté) · architecture visuelle de MISSION ·
BODY_LEDGER · EXECUTION · readiness · Shell · social · migration de tokens.

**Suite : `UI-CP3.6 TRUST EXPRESSION` uniquement**, puis `UI-CP4 LOADOUT` →
`UI-CP5 FLIGHT_RECORDER` → `UI-CP6 SHELL`. La continuité ne devient pas un
programme backend.
