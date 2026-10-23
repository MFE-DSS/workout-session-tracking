# `Sb_REC_ROLLOUT_01_RECOVERY_FIRST` — rapport

**Spec :** `docs/strategy/Sx_REC_ROLLOUT_01_RECOVERY_FIRST_SPEC.md` · **Date :** 2026-10-23 ·
**Branche :** `sb/rec-rollout-01-recovery-first` (depuis `7d34fa2`) · **Tier :** `shared_code`

## 1. Brainstorming / Options / Risques / Choix retenu (`CLAUDE.md §3`)

**Constat mesuré** : V3 servait `liss-abs` dans 64 des 78 décisions du corpus `REC-CP`, et
envoyait un nouvel utilisateur au cardio dès sa deuxième séance. Cause : le critère 4
« modalité délaissée » départage toute égalité de force récupérée en faveur du cardio.

| Option | Pour | Contre |
|---|---|---|
| A. Borner la modalité (cardio seulement après N jours) | changement minime | garde un bonus au cardio, contraire à D14 ; seuil arbitraire |
| B. **Retirer la modalité, placer « force avant cardio » juste après la récupération** | le cardio devient le plan B par construction ; aucun seuil | laisse des égalités que la modalité tranchait |
| C. Classer par disponibilité fine 0–1 | départage presque tout | fausse précision (estimation, pas mesure) ; couverture rendue muette |

**Choix : B**, complété par deux départages factuels : 1 ter (compte des zones en
récupération) et 3 bis (heures depuis la dernière charge, après la couverture).

**Risques** : la garde `REC-CP2` des égalités de catalogue (≤ 15 %) — tenue à 0 % par le défaut
lui-même — devait rougir ; arbitrée par l'opérateur (§3). Les explications et la parité
d'explication (`REC-CP5`) dépendent de la forme du rang — mises à jour dans la tranche.

## 2. Ce qui change

| Fichier | Changement |
|---|---|
| `app/services/recommendation_v3.py` | `_bande_de_modalite` retirée ; `_bande_de_plan_b`, `_zones_en_recuperation`, `_repos_minimal` ; rang à 10 composantes ; facteurs `plan_b`, `zones_en_recuperation` ; carte `heures` dans `RecuperationCanonique` ; phrases du plan B, du moins sollicité, du repos ; drapeau de contexte `departage_sans_historique` |
| `scripts/reco_replay.py` | `Decision.egalite_sans_historique`, `resumer()["part_egalites_sans_historique"]` |
| `tests/test_rec_rollout_01_recovery_first.py` | 7 tests d'acceptation (nouveaux) |
| `tests/test_rec_cp5_parite_explication.py` | table `CRITERES_DU_RANG` et clés de rang à la nouvelle forme (même rigueur) |
| `tests/test_rec_cp2_policy.py` | garde des égalités de catalogue recentrée sur les égalités avec historique ; part sans historique publiée et chaque décision concernée doit porter une phrase |

## 3. Mesures

- **Gagnants changés** sur le corpus `REC-CP` : **64 / 78**, tous `liss-abs` → séance de force,
  aucun hors motif.
- **Nouvel utilisateur en boucle fermée** : `push-a → pull-b → legs-a → pull-a → …` (avant :
  `push-a → liss-abs → …`).
- **Égalités tranchées par le catalogue** : 47 % au total, dont 44 % sans aucun historique de
  charge → **4 % là où un historique existait** (garde ≤ 15 % : verte). Arbitrage opérateur du
  2026-10-23 : la garde mord sur les égalités que la preuve aurait dû trancher.
- Boucles fermées : part catalogue 0,10–0,20, série maximale ≤ 2 (inchangées).

## 4. Défauts préexistants rendus visibles — hors périmètre

- Zones d'un gabarit : `full-body-morphotype-priority-v1` réduit à « mollets » par le seuil
  d'un quart (`recommendation._primary_zones_of`) ; il pèse dans 19 des égalités restantes.
- Séances utilitaires (`short-upper`, `no-equipment-full-body`) servies comme séances
  régulières.

Les deux sont posés comme questions au chercheur du moteur scientifique V2.

## 5. Vérifications

Voir §6 (rempli au moment du commit) : `check_scope`, sweep ciblé exécuté depuis l'arbre de la
branche (contrôle `app.__file__`), ruff, protocole de spec, CI.

## 6. Exécution

| Contrôle | Résultat |
|---|---|
| `check_scope.py` | **`CI_INFRA`** (touche `scripts/reco_replay.py`) → full sweep local + CI réelle impérative |
| `run_local_sweep.sh` (`PYTHONPATH` = arbre de la branche) | 90 lots, 359 fichiers, pic 2,4 Go ; **1 échec** : `test_v3_n_est_reference_que_par_le_banc_et_la_composition` — le nouveau fichier de tests n'était pas déclaré lecteur de V3. Déclaré dans le registre unique ; le fichier rejoué : 19/19 verts. Preuve que le sweep a mesuré la bonne arborescence : la garde a cité un fichier qui n'existe que sur cette branche |
| Fichiers V3 ciblés (rec_cp2/3/4/5, train_a, rollout_01) | 58 + 19 verts, depuis l'arbre de la branche (`app.__file__` contrôlé) |
| `ruff` (fichiers touchés) · budget | propre · 264 ≤ 548 |
| `check_spec_protocol.py` | OK |
| CI GitHub | au push |

## Verdict

**Verdict :** `PR GREEN / MERGE PENDING` attendu après CI — décision de merge à l'opérateur.
