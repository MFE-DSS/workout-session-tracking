# SPRINT Sb_WEEKLY_PLAN_SET_ALLOCATION_01 — réalisation en séries (RAPPORT)

**Train :** `AUREN_WEEKLY_PLAN_PRODUCTIZATION_01`, tranche 2/4 ·
**Base canonique :** `e80e4c5` · **Branche :** `sb/weekly-plan-set-allocation-01` ·
**Tier `check_scope` :** **SHARED_CODE**

`WeeklyVolumeBudget` parlait en **séries/semaine**, `WeeklyPlan` en
**créneaux/semaine**. Cette tranche ferme le décalage d'unité — et le chiffre
qu'elle fait apparaître est le vrai livrable.

---

## 1. Brainstorming / Options / Risques / Choix retenu

### Bornes de dosage : mesurées, pas choisies

Il fallait un plafond de séries par exercice. L'inventer aurait produit une
politique de dosage que rien n'appuie. `reference_split.json` — le catalogue
**déjà validé** — prescrit entre **2 et 4 séries par exercice** (modale **3** :
89 entrées sur 106), pour des séances de **7–8 exercices / 20–24 séries**.
Emprunter ces bornes revient à dire « ce plan ressemble à ce que le dépôt
prescrit déjà », pas « voici la bonne dose ».

### Répétitions : hiérarchie, et la contradiction ne se tranche pas

| Niveau | Source | Couverture du pool (69) |
|---|---|---|
| 1 | `reference_split.json`, **par exercice** | **36** (plage unique) |
| 2 | prescription **par intention**, plage de répétitions **seule** | **33** (8 contradictoires + 25 absents) |
| 3 | **défaut produit nommé** | seulement si personne ne parle |

**Huit exercices portent deux plages différentes selon le template.** Une source
qui se contredit n'est pas une source : on descend d'un niveau et `basis` le
dit. Trancher par ordre de lecture aurait donné une réponse **stable et
arbitraire** — le pire des deux mondes, parce qu'elle aurait eu l'air décidée.

Du niveau 2, **seule la plage de répétitions** est reprise. Son nombre de séries
venait d'un modèle où le budget n'existait pas ; le réutiliser réintroduirait
une seconde vérité de volume. Les quatre intentions de la tranche 1 n'ont
aucune prescription et tombent donc au **niveau 3 nommé** — jamais un héritage
silencieux du mapper morpho, ce que le brief interdit explicitement.

### La question tranchée par le brief lui-même

Fallait-il **créer des créneaux** pour atteindre le budget ? Le brief répond :

> « allocation must respect: cadence, **feasible slot count**, per-session
> practical constraints already present in repo »

Le nombre de créneaux est une **contrainte d'entrée** de l'allocation, pas une
variable qu'elle ajuste. Le manque est donc **nommé**, pas comblé. C'est aussi
la seule lecture compatible avec « If even `planning_low_sets` cannot be
reached: mark explicit unmet volume ».

Multiplier les créneaux par zone changerait la **forme des séances** (7–8
exercices deviendraient 8–10) : c'est une décision produit, remontée au §5, pas
prise ici.

---

## 2. Ce qui a été livré

**`weekly_set_allocation.py`** — module pur : `ExercisePrescription`
(exercice · zone · intention · **séries** · plage de répétitions · **source** de
cette plage · rationale · origine du budget · `policy_version`),
`ZoneSetAllocation`, et l'allocation déterministe.

`ZoneCoverage` porte désormais **`planned_sets`** à côté de `planned_slots`, plus
`target_sets`, `slot_capacity_sets` et `allocation_basis`.
**La satisfaction du budget se juge sur `planned_sets`.**

`PlannedSlot` porte sa dose, donc une séance se lit seule.
`WeeklyPlan.prescriptions` expose l'unité que la tranche 4 pourra exécuter.

**Allocation** : cible = `baseline_sets`, ou `planning_high_sets` si la zone est
priorisée — **jamais au-delà**. Répartition en reste le plus grand, ordre
déterministe, chaque créneau borné à `[2, 4]`. Un créneau qui tomberait sous le
plancher du catalogue est **retiré** plutôt que de prescrire une série isolée.

**La cadence n'atteint pas l'allocateur.** Le budget est hebdomadaire, le dosage
aussi ; la cadence répartit ensuite. L'allocation tourne **avant** la
distribution, si bien qu'aucune cadence ne peut changer un total.

---

## 3. Le chiffre que cette tranche révèle

| | séries/semaine |
|---|---|
| Σ `planning_low` sur 11 zones | **126** |
| Σ `baseline` | **154** |
| **Réellement prescrit aujourd'hui** | **44** |

Le planificateur émet **un créneau par zone** (`calves` : deux). Une zone à 16
séries ne peut donc en porter que 4. **Dix zones sur onze sortent en
`UNMET_VOLUME`** ; `calves`, seule zone à deux intentions, atteint sa bande.

**Le référentiel hérité n'a jamais été un tout hebdomadaire cohérent** : 154
séries à la densité du catalogue (~22 séries/séance) demanderaient **~7 séances
par semaine**. Ce sont onze chiffres par zone, posés indépendamment, qu'aucune
somme n'a jamais validée.

Ce n'est pas une régression introduite ici : c'est ce que la conversion en
séries rend enfin visible. Tant que la couverture se comptait en créneaux, un
exercice de pectoraux valait seize séries de pectoraux.

---

## 4. Ce que les plantations ont trouvé — deux gardes non porteuses

**Le résultat méthodologique de cette tranche.** Deux invariants écrits de bonne
foi ne prouvaient **rien**, et une seule plantation l'a montré à chaque fois.

**(a) Le plafond de bande.** `test_priority_can_never_push_sets_above_the_high_bound`
parcourait un plan réel. Or la capacité (4 séries × 1 créneau) plafonne **très
en dessous** de la borne haute : l'assertion passait sans jamais éprouver la
garde. Plantation `planning_high + 4` ⇒ **le test ne tombait pas.** Ajout d'un
cas où le plafond est la **contrainte active** (4 créneaux, borne haute 8) ; la
re-plantation le fait tomber.

**(b) L'étanchéité de la cadence.** Même cause, même illusion :
`test_cadence_never_changes_the_weekly_set_total` comparait `planned_sets`, que
la capacité écrase. Plantation injectant la cadence dans la cible ⇒ **33 tests
verts.** Les assertions comparent désormais aussi `target_sets` — l'intention
*avant* plafonnement — et une garde **structurelle** vérifie que la signature de
l'allocateur ne reçoit ni cadence ni séance.

Leçon consignée : **sur ce plan, la capacité domine tout**, donc tout invariant
de dosage éprouvé uniquement sur un plan réel est vacant par construction. Il
faut soit fabriquer la configuration où la borne mord, soit tester la grandeur
qui précède le plafonnement.

---

## 5. Un défaut de justesse corrigé au passage

Le manque de volume touchant presque toutes les zones, il remontait
mécaniquement en **contrainte d'axe déclaré**, avec le texte « aucun exercice
disponible ne peut les servir » — **faux** : un curl *est* prescrit, il est
seulement court en séries.

Les contraintes d'axe restent donc réservées aux raisons de **servabilité**
(aucune intention · aucun candidat · matériel). Le déficit de séries se lit zone
par zone dans `unmet_budget`, là où il est exact. Sans cette séparation, chaque
axe déclaré aurait été signalé en défaut et les vraies lacunes — `core`, les
triceps sans câble — auraient disparu dans le bruit.

---

## 6. Tests — 34 dédiés

Le test central est **`test_a_single_slot_never_covers_a_sixteen_set_zone`** :
c'est exactement le cas d'acceptation du brief (`baseline_sets=16`,
`planned_slots=1` ⇒ **non couvert**).

Couverture : bande respectée ou raison nommée sur les 11 zones · priorité vers
le haut sans jamais dépasser · plafond éprouvé là où il mord · cadence sans
effet sur cible **et** réalisé · garde structurelle sur la signature ·
répartition sans reste caché · plancher catalogue respecté · aucune série
fractionnaire · les trois niveaux de source de répétitions · repli toujours
visible dans `basis` · une zone sans candidat ne rapporte pas un manque de
volume · le matériel prime sur le volume · déterminisme · **et le déficit
structurel épinglé** pour qu'il ne se referme pas en silence.

Quatre tests existants mis à jour : ils confondaient « servie » et « sans aucune
raison de manque ». Ils portent désormais sur la **servabilité**, ce qu'ils
testaient réellement. Aucun n'a été supprimé ni relâché.

---

## 7. Non-régressions

Aucune persistance, aucune migration · aucune comptabilité fractionnaire —
l'unité reste la série entière · `recommendation.py` / `behavioral.py` /
`substitution.py` non touchés · `_INTENT_PRESCRIPTION` **lu, jamais modifié**, et
son nombre de séries délibérément ignoré · aucun exercice dupliqué, aucun
créneau fabriqué.

## Verdict

Le décalage d'unité est fermé : **la couverture du budget se juge en séries**, et
une zone à seize séries n'est plus déclarée couverte par un exercice.

Le chiffre qui en sort — **44 séries prescrites pour 126 en borne basse** —
n'est pas un défaut de cette tranche : c'est la première mesure honnête d'un
écart que le comptage en créneaux masquait. Il appelle une décision produit
(§5 ci-dessous), pas un correctif silencieux.

Deux gardes que j'avais écrites ne prouvaient rien, et seules les plantations
l'ont révélé. Elles sont désormais éprouvées là où elles peuvent réellement
être franchies.

**Suivi recommandé, non ouvert** — `Sb_WEEKLY_PLAN_SLOT_EXPANSION_01` : donner à
une zone autant d'exercices **distincts** que sa bande l'exige, tirés des
candidats que le générateur classe déjà, plafonnés par
`MAX_EXERCISES_PER_SESSION` × cadence. Faisable dès 4 séances/semaine
(≈ 32 créneaux nécessaires pour 40 disponibles), impossible à 2 — et c'est une
décision sur **la forme des séances**, donc la vôtre.
