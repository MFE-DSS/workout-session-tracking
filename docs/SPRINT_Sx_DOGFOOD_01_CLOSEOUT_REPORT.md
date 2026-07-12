# Closeout — Sx_DOGFOOD_01 Load Hint / Substitution Coherence

**Statut** : ✅ **CLOSED / READY FOR FIELD DOGFOOD**
**Type** : CLOSEOUT — docs-only (aucun code touché par ce closeout)
**Date** : 2026-07-11
**Précondition** : `Sb_DOGFOOD_01.3` HUMAN REVIEW ACCEPTED ✅ (vérifié dans le repo).

---

## 1. Origine dogfood

- **Problème détecté terrain** : la charge précédente / le placeholder cible
  pouvaient devenir **incohérents** quand un **exercice alternatif** (substitution)
  avait été utilisé lors d'une séance passée — l'app affichait alors la charge
  d'un exercice **différent** comme si elle était comparable.
- **Risque produit** : perte de confiance, **fausse intelligence**, comparaison
  inter-exercice trompeuse (« tu as fait 80 kg la dernière fois » alors que
  c'était sur une autre machine).
- **Règle produit finale** : **« silence plutôt que faux poids »** — en l'absence
  d'historique **comparable** (même identité prescrit/substitué), l'app se tait
  plutôt que d'afficher une charge non comparable.

---

## 2. Audit + spec

- **`Sx_DOGFOOD_01` audit/spec docs-only** livré (`Sx_DOGFOOD_01_LOAD_HINT_SUBSTITUTION_COHERENCE_SPEC.md`
  + `SPRINT_Sx_DOGFOOD_01_LOAD_HINT_SUBSTITUTION_COHERENCE_AUDIT_REPORT.md`).
- **Asymétrie confirmée** :
  - `overload` **déjà** substitution-aware / silencieux (silence si substitué) ;
  - `last_time_by_exercise_code` **non** substitution-aware au départ → source du bug.
- **5 surfaces contaminées** (consommatrices de `last_time`) :
  1. Référence précédente (console) ;
  2. Dernière fois (carte) ;
  3. delta ;
  4. hints Sx_08 ;
  5. chip / peek (briefing).
- **Matrice S1→S5** documentée :
  - S1 prescrit → prescrit (comparable, visible) ;
  - S2 prescrit → substitué (non comparable, silence) ;
  - S3 substitué récent + prescrit ancien → prescrit courant (prescrit ancien visible, substitution jamais) ;
  - S4 substitué → même substitut (comparable, visible) ;
  - S5 substitué → autre substitut (non comparable, silence).
- **Option A** retenue : patch **source** `last_time` (aligner sur la politique de
  substitution d'`overload_inputs`).
- **Option B** future : service central `exercise_load_identity`.
- **Option D** rejetée V1 : transfert de charge inter-machine.

---

## 3. Sb_DOGFOOD_01.1 — source fix

| Item | Valeur |
|---|---|
| Commit build | `b5776fbec2da73b1d904d6cd700656aeeece7854` |
| Human review | `a8d7a1f43daa1624848547b76f4e41f2ef0c0391` |
| CI | [`29160746462`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29160746462) ✅ 3/3 |
| Tests | **1896 passed** |

**Résultat** :
- `last_time_by_exercise_code` (`stats.py`) devient **substitution-aware** ;
- prescrit ↔ prescrit ; substitué X ↔ même X ; **sinon absence** (silence) ;
- **contrat de retour `dict[str, dict]` inchangé** → les 5 surfaces héritent ;
- aucun modèle / migration / router / overload / template / CSS / BI / JS / `value=`.

---

## 4. Sb_DOGFOOD_01.2 — consumer propagation verification

| Item | Valeur |
|---|---|
| Commit build | `306620e3e8e6f1bbf906393956acfc5e27ce4b14` |
| Human review | `5d8451259a3d7f92dd170299e1c20df677d57035` |
| CI | [`29164774428`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29164774428) ✅ 3/3 |
| Tests | **1904 passed** |

**Résultat** :
- **verification-only** ;
- console / delta / hints / briefing **héritent** du fix source `.1` ;
- **S2/S3/S5** silencieux ou cohérents (jamais la charge d'un autre exercice ;
  S3 → prescrit ancien) ;
- **S1/S4** restent visibles (référence comparable) ;
- **aucun code applicatif** (les consommateurs géraient déjà l'absence de `last_time`) ;
  8 tests bout-en-bout le verrouillent.

---

## 5. Sb_DOGFOOD_01.3 — mobile placeholder proportion

| Item | Valeur |
|---|---|
| Build fonctionnel | `e7dd1e158f0ab54f2ccaac22f768ef332da6a2d2` |
| Fix CI infra | `3474b0c3d43d8818d9ed9f55c337a935a9d62890` |
| Human review | `da4ab7840570dfa312366015f7e5457150483e83` |
| CI | [`29169942718`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/29169942718) ✅ 3/3 |
| Tests | **1913 passed** |

**Résultat** :
- `≈ 102.5` → `102.5` ; `≈ 6-10` → `6-10` (formatter `_build_overload_placeholder` compact) ;
- CSS mobile `::placeholder` sous `@media (max-width: 380px)` (ligne d'overload) ;
- **tap target 44 px** et **anti-zoom iOS 16 px** préservés ;
- aucun `value=` / JS / engine / history identity / substitution / modèle / migration / BI.

**Note CI** :
- timeout job `pytest + QA scripts` **25 → 35 min** accepté comme **infra-only** ;
- **full QA préservée** (aucun step retiré) ;
- **aucun test affaibli** — le build était valide (1913 passed), seul le job
  dépassait 25 min (annulation reproductible au step `Migration roundtrip`).

---

## 6. Statut final

| Élément | État |
|---|---|
| **Sx_DOGFOOD_01** | ✅ **CLOSED / READY FOR FIELD DOGFOOD** |
| Dogfooding terrain | 🗓️ **prévu demain matin** |
| Body Intelligence | ⏸️ **deferred until dogfood feedback** |
| Deploy | ⏸️ **deferred until explicit GO** |
| Release tag | ⏸️ **deferred** |
| Option C (unité séparée) | 💡 **future UI sprint, seulement si le dogfood le justifie** |

Le cycle est cohérent de bout en bout : **audit → `.1` fix source → `.2` vérif
consommateurs → `.3` mobile placeholder**, tous **HUMAN REVIEW ACCEPTED**, CI
réelle verte à chaque étape. La cohérence charge ↔ substitution est corrigée à la
source et prouvée sur les 5 surfaces ; la lisibilité mobile des placeholders cible
est réglée.

---

## 7. Dogfooding checklist terrain

À dérouler demain matin sur mobile étroit (≤ 380 px ou DevTools iPhone SE) :

- [ ] **Lancer depuis Home** ;
- [ ] **Démarrer la séance recommandée** ;
- [ ] **Vérifier la carte active** (exercice en cours mis en avant) ;
- [ ] **Vérifier « Référence précédente »** (comparable → visible) ;
- [ ] **Substituer au moins un exercice** (choisir un alternatif) ;
- [ ] **Vérifier qu'une charge non comparable devient silencieuse** (S2/S5 →
      « Non disponible », jamais la charge d'un autre exercice) ;
- [ ] **Vérifier qu'une charge comparable reste visible** (S1/S4 → référence ;
      S3 → prescrit ancien) ;
- [ ] **Vérifier le placeholder poids/reps sur mobile étroit** (`102.5` / `6-10`
      sans `≈`, tient dans la case, grisé, jamais prérempli) ;
- [ ] **Logguer des sets** (saisie normale, pas de zoom iOS au tap) ;
- [ ] **Enregistrer et passer à l'exercice suivant** ;
- [ ] **Terminer la séance** ;
- [ ] **Noter toute impression de « charge faussement intelligente »** (le moindre
      cas où l'app suggère une charge non comparable = régression à remonter).

---

## 8. Next decision

**Après le dogfooding terrain de demain matin** :
- si le terrain confirme la cohérence → envisager **deploy** (sur GO explicite) et
  reprise **Body Intelligence** (deferred until dogfood feedback) ;
- si le terrain remonte un cas de « charge faussement intelligente » → rouvrir un
  build ciblé (source ou consommateur selon la surface) ;
- **Option C** (unité séparée valeur/kg) seulement si le dogfood juge le placeholder
  compact encore ambigu.

Autres pistes hors cycle (aucune ouverte sans GO) : `Sb_UI_06.4`, `Sb_32.4`,
release tag, smokes UI auth prod.

---

## Verdict

**Verdict :** ✅ **Sx_DOGFOOD_01 Load Hint / Substitution Coherence — CLOSED / READY FOR FIELD DOGFOOD.**

Le cycle dogfood est bouclé : la règle **« silence plutôt que faux poids »** est
implémentée à la source (`.1`), prouvée sur les 5 surfaces consommatrices (`.2`)
et complétée par des placeholders cible lisibles sur mobile étroit (`.3`) — le
tout sans toucher au moindre modèle, migration, engine, substitution graph, JS,
`value=` ou Body Intelligence. Trois sprints HUMAN REVIEW ACCEPTED, CI réelle
verte 3/3 à chaque étape. **Prochaine étape : dogfooding terrain demain matin**,
puis décision (deploy / Body Intelligence / build correctif) selon le retour.
Body Intelligence, deploy et release tag restent **deferred** jusqu'au feedback
terrain.
