# `UX4_01` — le Profil répond à deux questions, et à deux seulement

**Premier chantier de `AUREN_EXPERIENCE_ARCHITECTURE_V4`.** Le Profil mesurait
**6,6 écrans, 641 mots, 39 contrôles, 18 régions encadrées** — une interface
d'administration de base de données.

> « Que sait AUREN de moi ? » et « que puis-je changer volontairement ? »
> **Il ne répond plus à « comment est-ce que je progresse ? »** — cette
> question appartient à `PROGRESSION`, qui existe.

---

## 1. Brainstorming / Options / Risques / Choix retenu (`CLAUDE.md §3`)

| Option | Ce qu'elle donne | Risque | Retenue |
|---|---|---|---|
| **A** — retirer la tension et s'arrêter là | applique la seule décision normative initiale | laisse **6,6 écrans** : une soustraction seule, interdite par `§5.3` | **non** |
| **B** — refondre le Profil entier en une passe | cible atteinte d'un coup | dépasse les lignes `OPERATOR_DECISION` ; le registre dit qu'un candidat n'est pas une décision | non |
| **C** — appliquer **exactement** les lignes tranchées, et faire voyager la soustraction avec l'état lisible | la dette décidée, et rien d'autre | demande une seconde revue opérateur pour élargir | **OUI** |

**Choix : C**, puis élargi par cinq décisions supplémentaires du 2026-08-20.

---

## 2. Résultat mesuré — trois largeurs, écrans entiers

| Mesure | 360 | | 390 | | 430 | |
|---|---:|---:|---:|---:|---:|---:|
| | avant | après | avant | après | avant | après |
| écrans de défilement | 7,2 | **2,1** | 6,6 | **2,0** | 5,7 | **1,8** |
| mots visibles | 641 | **140** | 641 | **140** | 641 | **140** |
| contrôles de premier rang | 39 | **10** | 39 | **10** | 39 | **10** |
| modules analytiques visibles | 6 | **0** | 6 | **0** | 6 | **0** |
| formulaires d'acquisition visibles | 3 | **1** | 3 | **1** | 3 | **1** |
| contrôles au-dessus du pli | 6 | 8 | 7 | 8 | 9 | 8 |
| disclosures | 2 | 5 | 2 | 5 | 2 | 5 |

**Régions encadrées : 18 → 4**, toutes `INTERACTIVE_OBJECT`. Zéro
`PURE_GROUPING`, zéro état encadré.

**Promesses non tenues : 0.** Les douze liens internes rendus ont été **suivis
un par un** — douze fois HTTP 200.

### Les deux lignes qui montent

Elles sont dans le tableau, et elles doivent y être.

- **Contrôles au-dessus du pli** : +2 à 360 et 390. Mécanique — la page fait
  deux écrans au lieu de sept, donc l'état lisible et le quick-log tiennent
  dans le premier.
- **Disclosures : 2 → 5.** C'est le **prix direct** du choix « le formulaire
  s'ouvre par un geste » : trois gestes de plus pour atteindre l'édition.
  Assumé, pas gratuit.

Sélectionner les lignes qui descendent est une façon de mentir avec des
chiffres exacts.

---

## 3. Les six décisions appliquées

| Décision | Ce qui a été fait | Ce qui n'a PAS été fait |
|---|---|---|
| **Tension → `REMOVE_NO_ASK`** | retirée de l'acquisition, **données préservées**, handler n'assigne plus les colonnes | non supprimée de la base ni du rapport coach |
| **Analytique corporelle → `PROGRESSION / BODY`** | neuf cartes vides retirées du Profil | **aucun lien posé** — la destination n'a pas de route |
| **Configuration → `PROGRAMMES / PLAN`** | résumé compact en lecture seule, éditeur **marqué transitionnel à l'écran** | éditeur non déplacé — exige la surface de destination |
| **Poids → `QUICK_LOG`** | saisie compacte là où la donnée se lit | aucun canal santé connecté |
| **Morphométrie → `ONCE_SETUP`** | signalée « saisie complète », mécanisme de repli | **assistant guidé non construit** |
| **États vides** | un seul par domaine | — |

---

## 4. Le piège que la phase 2 avait déjà enseigné, et qui était bien là

`profile_body_submit` écrivait `user.bp_systolic = _int_or_none(bp_systolic)`
avec un défaut de formulaire à `""`. **Retirer le champ du gabarit suffisait à
effacer la tension stockée au prochain enregistrement.**

La garde `test_existing_blood_pressure_survives_a_profile_save` **échouait sur
le produit d'avant** : la préservation n'existait que par aller-retour du
formulaire, jamais dans le handler. Il n'assigne plus ces colonnes — c'est ce
qui rend « données existantes préservées » vrai.

---

## 5. Quatre défauts que la CAPTURE a montrés, invisibles à la relecture

| Défaut | Conséquence |
|---|---|
| `.quicklog__input` sans style | **champ BLANC** au milieu d'une interface graphite |
| `.pstate__legacy` sans style | « Mettre à jour mes mesures saisie complète » en une ligne |
| état vide morphologie par champ | sept façons de dire la même absence |
| **« 0 / 13 mesures » en haut, « 6 mesures attendues » trois écrans plus bas** | deux modèles distincts de la morphologie, donc **deux comptes contradictoires** |

Le dernier est le plus instructif : deux sources de vérité pour un même
concept, à trois écrans d'intervalle. Le décompte vit désormais **une fois**.

---

## 6. Trois erreurs de mesure et de rapport, de mon fait

1. **Un chiffre énoncé sans être lu.** J'ai rapporté « formulaires visibles
   4 → 1 » en le déduisant, pas en le lisant. La mesure disait 4 → 2.
2. **Une étiquette qui ne correspondait pas à son objet.** La sonde comptait
   **tous** les `<form>` non repliés, dont la **déconnexion** — qui n'acquiert
   aucune donnée. Le compte réel est **3 → 1** : le « avant » était faux aussi.
3. **Deux lignes omises du résumé**, précisément les deux qui montent.

Une sonde dont l'étiquette dépasse ce qu'elle mesure produit un chiffre exact
et faux.

---

## 7. Un défaut que seul le lint a pu voir

Ma f-string réutilisait le guillemet extérieur avec échappement : **syntaxe
valide en 3.12+, INVALIDE sur le Python 3.11 de la CI**. Le poste tourne en
3.14, donc les 22 gardes passaient en local et **la CI aurait cassé à la
collecte**.

---

## 8. Gardes — migrées, pas supprimées

**22 gardes neuves**, dont cinq rouges sur le produit d'avant. Et **trois
gardes existantes migrées** parce qu'elles protégeaient un placement
officiellement déplacé (`GUARD_MIGRATION_REGISTER`, règle 6) :

| Garde | Ce qu'elle exigeait | Ce qu'elle exige maintenant |
|---|---|---|
| `test_profile_shows_fatigue` | fatigue **sur le Profil** | son **absence** du Profil |
| `test_profile_shows_consistency` | régularité sur le Profil | idem, plus **le service produit toujours les signaux** |
| `test_profile_renders_for_authenticated_user` | « Sessions totales » | les **faits d'identité** — le compteur vit sur `PROGRESSION`, qui le rend déjà |

Aucune n'a été affaiblie pour verdir : chacune garde un invariant qui survit au
déplacement.

---

## Verdict

**`UX4_01` — direction appliquée, cible non close.**

Le Profil passe de **6,6 à 2 écrans** et de **39 à 10 contrôles**, sans perdre
une donnée ni une capacité. Les six lignes `OPERATOR_DECISION` sont appliquées ;
**aucune ligne candidate ne l'est**.

---

## 9. Dépendance enregistrée — NON résolue ici

> **`PROGRESSION` annonce « la régularité » dans son chapeau et ne la rend
> pas.** Entre cette tranche et `UX4_03`, fatigue, régularité et série sont
> **calculées mais visibles nulle part**.

L'opérateur interdit toute refonte de Progression dans `UX4_01`. Le trou est
donc **assumé et signalé**, pas comblé — c'est le coût d'un déplacement en deux
temps, et l'arbitrage lui appartient.

Deux autres dépendances ouvertes : l'**éditeur de préférences** attend sa
destination dans `Programmes` ; l'**analytique corporelle** attend
`PROGRESSION / BODY`, qui n'a pas de route.

---

## 10. CLOSEOUT

| | |
|---|---|
| PR | [#137](https://github.com/MFE-DSS/workout-session-tracking/pull/137) **MERGED** |
| merge | **`d146cdb`** — sans squash, sans `--admin`, sans force, tête épinglée |
| CI de PR | 8/8 · gate Sonar `OK` · 0 issue · 0 thread |
| **CI canonique** | **6/6 success** |
| diff | +878 / −96 sur 10 fichiers |

### La CI a trouvé cinq échecs que mon sweep local déclarait verts

Trois causes, dont deux de fragilité de harnais :

- **`_capture_form()`** s'ancrait sur la première occurrence de
  `/profile/measurements`. Le quick-log poste vers la **même route canonique**
  et vient avant dans la page : la garde lisait un formulaire à un champ et
  concluait que le protocole d'envergure avait disparu. Sa docstring disait
  « le formulaire de mesure SEULEMENT » — l'intention était juste, l'ancrage ne
  l'était plus. **Réparé, pas affaibli.**
- **Trois gardes de placement** migrées, chacune avec l'invariant qui survit au
  déplacement. Pour « 30 derniers jours », une **seconde garde** vérifie que la
  lecture existe sur `PROGRESSION` — sans elle, le retrait passerait aussi si
  la capacité avait disparu.

### Le défaut le plus instructif de la tranche est dans l'instrument

**Mon « full sweep local » a rendu 5053 passed sur une tranche où la CI a
trouvé cinq échecs.**

`scripts/run_ci_pytest.sh` **ne contient aucun `cd`** : il lance pytest dans le
répertoire courant du shell, qui revient à la canonique. La preuve était
visible — `coverage.xml` s'est écrit dans la canonique, jamais dans le
worktree.

**Et la correction a échoué une seconde fois, plus subtilement.** En passant
`pytest <worktree>/tests`, **5071 tests** ont été collectés — donc les tests
venaient bien du worktree — mais **`import app` résolvait encore vers la
canonique**. Tests d'un arbre, application d'un autre : deux gardes neuves
rendaient l'ancien gabarit.

> Le compte de tests prouvait qu'on avait changé d'arbre, ce qui donnait
> confiance dans un résultat encore faux.

La seule forme correcte impose `PYTHONPATH=<worktree>` en plus du chemin des
tests. **Pour une tranche développée en worktree, la CI reste la source de
vérité** — et c'est elle qui a tranché ici.

---

## 11. Ce que la tranche ne fait pas

Aucun canal santé connecté · aucun assistant guidé de morphométrie · aucune
refonte de Progression · aucun changement de modèle métier · aucune migration ·
`recommendation.py` non ouvert.
