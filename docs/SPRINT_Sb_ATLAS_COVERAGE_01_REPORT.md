# SPRINT Sb_ATLAS_COVERAGE_01 — couverture 7/7, sans toucher au catalogue (RAPPORT)

**Base canonique :** `270a2ff` · **Branche :** `sb/atlas-coverage-01`

---

## 1. Diagnostic — ce n'était pas un alias manquant

Les trois exercices sans cue portent `machine_slug=None` **et**
`machine_family=None` dans `data/reference_split.json` : **aucun lien atlas**.

| code | exercice | cause | famille |
|---|---|---|---|
| **E3** | Dips pectoraux (buste penché) | machine absente de `pecs-press` | existe |
| **E6** | Écarté arrière d'épaule câble | machine absente de `shoulders-lateral-posterior` | existe |
| **E7** | Triceps extension poulie haute (corde) | **famille absente** — l'atlas ne couvrait aucun bras | à créer |

---

## 2. Le piège du catalogue, mesuré avant d'agir

Le réflexe naturel — remplir `machine_slug` dans `reference_split.json` — est
**un piège**, et il fallait le mesurer pour le voir.

`seed_reference_split()` est verrouillé sur la **version du payload** : sans
bump, il retourne `False` et n'écrit rien. Le mapping serait donc resté
**inerte**, c'est-à-dire de la donnée morte que A7 interdit.

Et bumper la version déclenche un wipe des lignes SYSTEM. Mesuré sur **copie
jetable** de la base :

```
AVANT reseed    template_link=7/7    cue=4/7
APRÈS reseed    template_link=0/7    cue=0/7
```

`SessionExercise.template_exercise_id` est `ondelete="SET NULL"`. Les
snapshots préservent l'identité pour l'analytique — c'est le dessein
documenté — **mais le cue se résout par le lien vivant**, pas par les
snapshots.

**Couvrir trois exercices aurait retiré le cue de toutes les séances
historiques.** Les deux chemins content-only violaient donc une contrainte :
sans bump, donnée morte ; avec bump, régression historique. D'où le HARD STOP,
et la décision opérateur d'autoriser une modification minimale du résolveur.

---

## 3. Le correctif — trois lignes, et la couverture devient rétroactive

`get_for_session_exercise()` gagne un **dernier recours par nom**, après
l'échec du `template_exercise` :

```python
machine = get_machine_by_name(
    getattr(session_exercise, "exercise_name_snapshot", None)
)
```

`get_machine_by_name()` existait déjà — correspondance exacte nom/alias,
insensible à la casse — et servait au chemin substitution.

Ce que ce choix change, et c'est le point :

* **aucun reseed, aucun bump de version** — le catalogue n'est pas touché ;
* le **snapshot de nom est justement conçu pour survivre au reseed**, donc la
  couverture devient **indépendante du seed** ;
* elle est **rétroactive** : une séance déjà enregistrée gagne son cue sans
  qu'aucune ligne ne bouge. Vérifié sur une séance créée **avant** le
  changement.

---

## 4. Contenu ajouté — strictement additif

| famille | machine | statut |
|---|---|---|
| `pecs-press` | `chest-dips` | machine ajoutée |
| `shoulders-lateral-posterior` | `cable-rear-delt-fly` | machine ajoutée |
| **`arms-triceps`** *(nouvelle)* | `triceps-pushdown-rope` | famille + machine |

**8 → 9 familles, 29 → 32 machines. Diff : 62 insertions, 0 suppression.**

Le premier essai passait par `json.dumps()` et reformatait les tableaux courts
que le fichier garde en ligne — 254 insertions **et 50 suppressions**. Rejeté
et refait par insertion textuelle : un patch de contenu ne doit pas réécrire
ce qu'il n'ajoute pas.

**La zone `triceps` n'est pas inventée** : c'est un code canonique existant
(`ZONE_LABELS`, `RADAR_AXES["arms"].zones`). Un test l'exige désormais pour
**toutes** les familles.

**Aucune clé morte** : ni `setup_checklist`, ni `correction_hints` — la leçon
de `Sb_FEEDBACK_SIGNAL_AUDIT_01`, gardée par un test.

---

## 5. Couverture, avant / après

```
AVANT                                          APRÈS
E1 Incline Smith Press        incline-smith-press      inchangé
E2 Chest Press machine        chest-press-machine      inchangé
E3 Dips pectoraux             UNMAPPED            →    chest-dips
E4 Neutral Grip Shoulder      shoulder-press-machine   inchangé
E5 Élévations latérales       cable-lateral-raise      inchangé
E6 Écarté arrière d'épaule    UNMAPPED            →    cable-rear-delt-fly
E7 Triceps extension          UNMAPPED            →    triceps-pushdown-rope

                              4/7                 →    7/7
```

---

## 6. Une garde existante a attrapé une vraie erreur

`test_all_machines_have_valid_enums` a refusé `equipment: "poids-du-corps"` —
le vocabulaire valide est `{barbell, bodyweight, cable, haltere, machine,
smith}`. Corrigé en `bodyweight`. La garde de schéma a fait son travail avant
la CI.

---

## 7. Une garde à moi, rendue structurelle plutôt que desserrée

`test_worked_area_primary_shown_on_exactly_the_two_authorised_surfaces`
comptait une sous-chaîne sur toute la page. Le nombre était passé de 1 à 2
quand le résumé compact est arrivé ; il serait passé à **3** ici, parce qu'un
exercice qui n'avait pas de famille en a maintenant une et que le bloc
« Intention » affiche « Bloc <famille> » — **une amélioration, pas une
duplication**.

Relever la constante une troisième fois aurait desserré la garde sans rien
prouver. Elle vérifie donc maintenant la **structure** : chaque surface
autorisée nomme la cible **au plus une fois**, et le total de la page doit
être exactement la somme des surfaces reconnues. **Plus strict qu'un
compteur** — une quatrième surface, ou un doublon dans une surface existante,
échoue.

---

## 8. Preuves

| | |
|---|---|
| Couverture | **4/7 → 7/7** |
| Rétroactivité | vérifiée sur une séance créée avant le changement |
| Atlas | **62 insertions, 0 suppression** ; 9 familles / 32 machines |
| Contrat atlas | 3 cues + 2 erreurs sur **32/32** machines |
| `reference_split.json` | **non touché** |
| `app/models` · `migrations` · `app/routers` · `app/templates` · `app/static` | **diff vide** |
| Ruff | aucun finding introduit |
| Sweep complet | **4689 tests, 0 échec**, lancé **depuis le worktree** |

**13 tests dédiés.** Plantation : repli par nom désactivé → 2 gardes tombent,
dont celle qui vérifie la survie à un lien `template_exercise` absent.

---

## 9. Limites restantes

- **La couverture vaut pour le split de référence testé.** D'autres templates
  peuvent contenir des exercices hors atlas ; la garde `push-a` ne les couvre
  pas. Un exercice non mappé reste **silencieux**, jamais générique.
- **`machine_slug` reste nul** dans le catalogue pour ces trois exercices. Ce
  n'est pas une dette cachée : la résolution par nom est désormais le chemin
  assumé, et le remplir exigerait le reseed que ce sprint a écarté.
- **La famille `arms-triceps` ne contient qu'une machine.** Biceps, et les
  autres mouvements de triceps, restent hors atlas.

## Verdict

La couverture passe de 4/7 à 7/7 **et devient rétroactive**, sans reseed, sans
migration, sans toucher le catalogue.

Le travail utile n'a pas été d'écrire des cues : c'est d'avoir mesuré que le
chemin évident — remplir le catalogue — aurait effacé les cues de tout
l'historique pour en gagner trois.

---

## Closeout (post-merge)

| | |
|---|---|
| PR | **#118** — `--merge --match-head-commit 399b81a`, **sans** squash / `--admin` / force |
| Merge | **`99ef904`** |
| CI canonique | run `32018420408` — **succès 6/6** |
| Gate Sonar | **`OK`** — 0 bug, 0 smell, 0 vulnérabilité, 0 % duplication, **couverture code neuf 100 %** |
| Threads / Gitar | **0 / 0** |
| CI PR | **9 checks verts au premier passage, aucun aller-retour** |

### La leçon appliquée, cette fois

Le sprint précédent s'était conclu sur un aller-retour Sonar évitable
(`python:S9073`) faute de pré-scan AST avant commit. Ici le scan a été fait
**avant** de pousser — et la PR est passée verte du premier coup, gate
comprise. C'est la deuxième fois que ce scan décide de la présence ou non d'un
cycle CI supplémentaire.

### Capacité CI — `HEALTHY`, partition serrée

| Shard | Fichiers | min MemAvailable | min SwapFree |
|---|---|---|---|
| 1 | 85 | 8 101 Mo | 3 071 — intact |
| 2 | 85 | 7 048 Mo | 3 071 — intact |
| 3 | 84 | 6 794 Mo | 3 071 — intact |

`workers=2`, manifeste respecté, jamais `-n auto`. Shard bas à **6 794 Mo**,
très au-dessus du plancher de 4 Go. **85/85/84** — la partition reste
équilibrée alors que la suite a encore grandi.

### Effet de bord bénéfique, non demandé

Le repli par nom ne profite pas qu'aux trois exercices visés : **tout**
exercice dont le nom figé correspond à une entrée d'atlas résout désormais son
cue, y compris dans les séances déjà enregistrées et y compris si son lien
`template_exercise` venait à disparaître. La couverture a cessé de dépendre de
l'état du catalogue.

### Suite

`Sb_SUBSTITUTION_COCKPIT_01` peut maintenant s'appuyer sur une base sémantique
complète pour la surface testée — c'était la condition posée par le rationnel
du sprint.
