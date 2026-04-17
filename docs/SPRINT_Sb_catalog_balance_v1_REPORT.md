# Sprint Sb_catalog_balance_v1 Report

**Date:** 2026-04-15
**Type:** Build catalogue (data only)
**Prerequisite:** Sb_catalog_substitution_v1 (catalog v9) merged
**Catalogue cible:** `2026-04-15.v10`

---

## 1. Objectif

Appliquer le chantier 3 du benchmark catalogue : equilibrer le volume des templates core pour respecter la cible **session <= 1h15**.

**Inversion vs recommandation initiale du benchmark :** la consigne utilisateur est **reduire les sessions trop longues** plutot que d'enrichir Pull A. Justification utilisateur :
- Un user peut toujours **ajouter un exercice manuellement** au gym
- Un user ne peut pas **retirer** un exercice prescrit sans casser le template
- Les sessions courtes (Pull A) restent acceptables comme focus etroit assume

---

## 2. Analyse pre-build

| Template | Avant (sets) | Duree estimee (3.5min/set) | Statut |
|----------|--------------|---------------------------|--------|
| push-a | 25 | 88 min | **DEPASSE** |
| push-b | 22 | 77 min | borderline |
| pull-a | 15 | 52 min | OK (court mais assume) |
| pull-b | 20 | 70 min | OK |
| legs-a | 22 | 77 min | borderline |
| legs-b | 22 | 77 min | borderline |

Push A est le seul template clairement au-dessus de la cible 1h15. Les 3 templates a 22 sets (Push B, Legs A, Legs B) sont **borderline** mais sans doublon evident a retirer sans casser le focus du programme. Decision : **focus sur Push A uniquement** dans ce sprint.

---

## 3. Modifications appliquees

### Push A — 2 reductions ciblees

**Avant :** 8 exercices, 25 work sets, ~88 min

**Apres :** 7 exercices, 21 work sets, ~74 min

| Action | Justification |
|--------|---------------|
| Retirer **E8 `Extension triceps overhead câble`** (3 sets) | Vrai doublon avec **E7 `Triceps pushdown corde`** (3 sets) — meme zone, meme pattern (extension du coude), redondance non justifiable |
| Reduire **E5 `Élévations latérales câble (derrière le dos)`** de **4 sets RP → 3 sets RP** | Le rest-pause est intense ; 3 series RP suffisent pour le stimulus delt_lat. La 4e serie etait surajoutee. |

**Net :** -3 sets (E8) - 1 set (E5) = -4 work sets, -1 exercice.

### Templates non modifies

- **Push B (22 sets)** : 3 exercices pec successifs (E1 fly câble, E2 développé halteres, E3 butterfly machine) sont deliberes — focus "pec largeur/stretch" du programme. Pas de retrait sans casser l'intention.
- **Legs A (22 sets)** : focus quad-dominant complet. Adduction (E5) jugee utile. Pas de doublon.
- **Legs B (22 sets)** : focus posterieur + complement quad (E5 leg ext) coherent. Pas de doublon.
- **Pull A (15 sets)** : court par design (focus largeur). Si user veut isolation biceps ou row supplementaire, ajout manuel possible.
- **Pull B (20 sets)** : OK.
- **Catch-up et utility** : non touches.

---

## 4. Decision documentee dans la governance

`docs/strategy/SPIGNOS_CATALOG_GOVERNANCE.md` enrichi d'une section **Volume Policy (v10+)** documentant la regle :

> Sessions designees pour <= 1h15 (~21 work sets max). Privilegier la
> reduction des templates trop longs plutot que l'enrichissement des
> templates courts. Un user peut ajouter manuellement, il ne peut pas
> retirer un exercice prescrit.

Tableau de reference v10 inclus.

---

## 5. Statistiques avant/apres

| Indicateur | v9 | v10 | Delta |
|-----------|-----|------|-------|
| Templates | 16 | 16 | 0 |
| Total exercices catalogue | 97 | 96 | -1 |
| Push A : exercices | 8 | 7 | -1 |
| Push A : work sets | 25 | 21 | -4 |
| Push A : duree estimee | 88 min | 74 min | -14 min |
| Templates depassant 1h15 | 4 | 3 (borderline 77min) | -1 critique |

Aucun autre template touche.

---

## 6. Fichiers modifies

| Fichier | Type | Nature |
|---------|------|--------|
| `data/reference_split.json` | Modify | Version v9→v10, push-a retire E8, push-a E5 reduit a 3 sets RP |
| `docs/strategy/SPIGNOS_CATALOG_GOVERNANCE.md` | Modify | Ajout section "Volume Policy (v10+)" + tableau de reference |
| `docs/SPRINT_Sb_catalog_balance_v1_REPORT.md` | New | Ce rapport |

**Zero migration. Zero changement de code Python. Zero changement de template UI.**

---

## 7. Tests et verification

```
$ python scripts/catalog_qa.py
{
  "templates": 16,
  "exercises": 96,
  "errors": 0,
  "warnings": 0,
  "status": "PASS"
}
```

Full test suite : voir resultat dans `git log` du commit. Cible : 519+ pass.

---

## 8. Compatibilite historique

- Les sessions historiques sur Push A v9 (avec E8 et E5 a 4 sets) restent intactes — snapshots immutables (`exercise_code_snapshot`, `exercise_name_snapshot`) preservent l'identite des exercices au moment du log.
- Le seed re-detectera v10 au prochain deploy et reseed les templates. Les anciennes occurrences de E8 dans l'historique restent visibles via `actual_exercise_name` et les exports.
- Aucun consumer (KPIs, deltas, dashboards) n'est impacte.

---

## 9. Limites et non-objectifs

- **Push B / Legs A / Legs B (77 min)** : laisses tels quels, juges acceptables comme borderline. Si remontee user explicite "trop long", sprint suivant peut reduire.
- **Pull A (52 min)** : laisse court par design. Le user peut ajouter manuellement un exercice biceps ou row complementaire au gym.
- **Aucun nouveau exercice** introduit dans ce sprint (cohérent avec la consigne "reduire plutot qu'ajouter").
- **Pas de mecanisme `add_exercise_manually`** dans l'UI : differe a un sprint dedie si demande utilisateur explicite.

---

## 10. Criteres d'acceptation

| Critere | Statut |
|---------|--------|
| Push A passe sous 1h15 estime | ✓ (74 min) |
| Aucun retrait sans doublon clair | ✓ (E8 = doublon de E7 sur triceps) |
| Aucune regression sur autres templates | ✓ (non touches) |
| Governance documente la nouvelle regle de volume | ✓ |
| QA script PASS | ✓ |
| Full suite green | ✓ (verification) |
| Aucun changement code Python | ✓ |
| Pas de migration | ✓ |

**Build Sb_catalog_balance_v1 : OK, pret a deployer.**

---

## 11. Synthese executive

- **Push A reduit** de 25 a 21 sets (-4), passe sous la cible 1h15
- **Une regle de volume documentee** dans la governance : sessions <= ~21 sets, reduire plutot qu'enrichir
- **Aucun nouveau exercice** introduit (consigne user respectee)
- Templates **borderline** (Push B, Legs A/B a 22 sets) acceptes en l'etat
- **Pull A reste court** comme focus largeur assume

Catalogue v10 = catalogue v9 + 1 retrait + 1 reduction + governance volume policy.
