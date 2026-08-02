# SPRINT Sb_CUSTOM_PROGRAM_WIZARD_06 — Controlled Regeneration (RAPPORT)

**Base canonique :** `5a85d67` · **Tier :** ISOLATED · **Statut :** PATCH COMPLETE / REVIEW PENDING
**Spec :** [`Sb_CUSTOM_PROGRAM_WIZARD_06_CONTROLLED_REGENERATION_SPEC.md`](strategy/Sb_CUSTOM_PROGRAM_WIZARD_06_CONTROLLED_REGENERATION_SPEC.md)

## 1. Ce qui change

Le refus dur de générer sur un programme non vide devient une **confirmation explicite**.

Le garde-fou d'origine était correct sur le fond — `replace_draft_tree` remplace l'arbre entier, donc
générer par-dessus détruit le travail manuel — mais il laissait l'utilisateur sans issue : vider
l'arbre séance par séance, ou abandonner le programme. La protection est conservée **intégralement**
(un POST non confirmé ne touche jamais l'arbre) et cesse d'être une impasse.

## 2. Fichiers touchés

**Modifiés (5)**

| Fichier | Changement |
|---|---|
| `app/routers/user_programs.py` | `confirm_replace` sur le POST ; refus conditionnel ; 4 clés de résumé dans `_render_generate` |
| `app/templates/user_programs/generate.html` | avertissement, résumé chiffré, case à cocher ; formulaire rendu dans les deux cas |
| `tests/test_user_programs_generate_http.py` | 17 tests ajoutés (15 → 32 fonctions) |
| `docs/strategy/SPEC_REGISTRY.md` | entrée WIZARD_06 |
| `docs/strategy/ROADMAP_AND_NEXT_STEPS.md` | statut WIZARD_06 |

**Ajoutés (2)** — la spec et ce rapport.

Aucun autre fichier. Aucune migration, aucun service, aucun modèle.

## 3. Comportement

| Situation | Résultat |
|---|---|
| Programme **vide** | inchangé : génération directe, `303` vers l'éditeur, aucune confirmation demandée |
| Non vide, **sans** `confirm_replace` | `200`, message doux, résumé + case à cocher, **arbre intact** |
| Non vide, **avec** `confirm_replace` | `generate_program_tree` + `replace_draft_tree`, `303` vers l'éditeur |
| `validated` + confirmation | remplacement autorisé ; le service repasse le programme en `draft` |
| `published` / `archived` | refusés par le service existant, **même confirmés** ; arbre intact |

Deux choix méritent d'être explicités.

**Le non-confirmé n'est pas une erreur.** Il renvoie `200`, pas un échec : l'utilisateur n'a rien fait
de faux, le formulaire n'a simplement pas encore été accepté. Le message le dit ainsi.

**La confirmation n'est pas une autorité.** Elle exprime un consentement à perdre l'arbre, jamais un
droit sur le cycle de vie : `published` et `archived` restent refusés par le service, et un test le
prouve avec `confirm_replace=true`.

## 4. Le résumé chiffré

Le formulaire affiche **séances / exercices / séries** de l'existant, comptés sur l'arbre réel
(`sessions → exercises → rep_targets`). « Cette action remplacera votre programme » n'est pas un
consentement éclairé ; trois nombres le sont.

## 5. Sans JavaScript

La case n'est **pas** `required`. Un envoi non confirmé doit atteindre le serveur et revenir avec le
résumé, plutôt que d'être stoppé par une infobulle du navigateur : la garantie est le contrôle
serveur, et la case n'est que la façon d'exprimer le consentement. Aucun JS n'est introduit.

## 6. Tests

`tests/test_user_programs_generate_http.py` — **41 passés** (15 existants + 17 ajoutés, dont des
cas paramétrés).

Ajoutés : génération vide inchangée · non vide sans confirmation (`200` + arbre, exercices et nom de
séance inchangés) · non vide avec confirmation (`303` + arbre remplacé, séance semée disparue) ·
`validated` repassé `draft` · `published` refusé confirmé · `archived` refusé confirmé · avertissement
et case présents au GET · résumé séances/exercices/séries · aucune case sur programme vide ·
owner-scope `404` et absent `404` **indistincts** · aucune `UserProgramQualityReview`, aucun
`WorkoutTemplate`.

Un test existant, `test_generate_on_nonempty_program_refused`, reste vert sans modification : le
message conserve « contient déjà des séances » et l'arbre reste à une séance. La compatibilité du
comportement non confirmé est donc prouvée par un test écrit **avant** ce sprint.

## 6bis. Revue adversariale — un REQUIRED

Sept angles passés ; les points incertains ont été **sondés**, pas supposés.

**Aucun bypass de confirmation.** `""`, `false`, `False`, `0`, `off`, `no`, `maybe`, `TRUE-ish` :
l'arbre reste intact dans les huit cas (`200` ou `422`). Un champ `confirm_replace` **dupliqué**
`false`+`true` renvoie `422` sans remplacer — il n'est pas résolu au dernier. Les valeurs acceptées
sont l'ensemble booléen standard (`true/True/1/on/yes`).

**REQUIRED corrigé — le ton contredisait la spec.** Le message non confirmé passait par la variable
`error`, rendue en `color:var(--danger)`. La spec affirme que ce n'est *pas* une erreur ; l'UI disait
l'inverse. Une variable `notice` distincte a été introduite, rendue en gras neutre. La couleur
`--danger` reste réservée aux vraies erreurs de saisie, et un test le prouve dans les deux sens.

**Résumé sur collections vides.** Une séance sans exercice et un exercice sans série rendent
correctement (`0` affiché) — aucune expression de template ne casse.

**Double POST confirmé.** Un remplacement par requête ; aucune `UserProgramQualityReview` ni
`WorkoutTemplate` supplémentaire (mesuré avant/après).

Aucun BLOCKER. Une limitation acceptée : le résumé reste un instantané (§8).

## 7. Interdits — vérifiés

Aucune migration · aucun snapshot DB · aucun nouveau service · `user_program_generator.py` non
modifié · `user_program_drafts.py` non modifié · `program_quality_*` non modifiés · aucune
`UserProgramQualityReview` écrite · aucun `WorkoutTemplate` créé · EKB_04 non ouvert · JSON EKB non
touchés · ASSET / BodyMap non touchés · aucun JS obligatoire.

## 8. Limites assumées

**Le remplacement est irréversible.** Il n'existe ni sauvegarde ni historique de l'arbre précédent :
le résumé chiffré est la seule protection, et elle est humaine. Un historique de versions serait un
sprint à part (modèle, migration, rétention).

**Le résumé est un instantané.** Il décrit l'arbre au moment du rendu ; une édition concurrente dans
un autre onglet le rendrait obsolète, et le remplacement porterait alors sur un contenu légèrement
différent de celui annoncé. Le verrouillage optimiste relève de l'éditeur.

## Verdict

**WIZARD_06 PATCH COMPLETE / REVIEW PENDING** — non commité, non poussé, aucune PR.
