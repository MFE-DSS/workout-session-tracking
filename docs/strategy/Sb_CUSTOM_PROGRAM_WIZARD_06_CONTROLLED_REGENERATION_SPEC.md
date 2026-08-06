# Sb_CUSTOM_PROGRAM_WIZARD_06 — Controlled Regeneration (SPEC)

**Statut :** ✅ VALIDATED (build complete) · **Base canonique :** `5a85d67` · **Tier :** ISOLATED

## 1. Problème

`POST /programs/{program_id}/generate` refuse **tout** programme contenant déjà des séances :

```python
if program.sessions:
    return _render_generate(..., error="Ce programme contient déjà des séances. "
                                       "Videz-le ou créez-en un autre pour générer une base.")
```

Ce refus dur avait une bonne raison — `replace_draft_tree` remplace l'arbre **entier**, donc générer
par-dessus un programme rempli détruit le travail manuel. Mais il laisse l'utilisateur sans issue :
pour régénérer une base sur un programme dont il n'est pas satisfait, il doit **vider l'arbre à la
main, séance par séance**, ou créer un second programme et abandonner le premier. Le garde-fou
protège la donnée et bloque l'intention.

## 2. Solution

Remplacer le refus par une **confirmation explicite**.

Le refus dur devient conditionnel : il ne s'applique que tant que l'utilisateur n'a **pas** confirmé.
La protection est donc conservée intégralement — un POST non confirmé ne touche jamais l'arbre — mais
elle cesse d'être une impasse.

La confirmation n'a de valeur que si l'utilisateur sait **ce qu'il perd**. Le formulaire affiche donc
le décompte exact de l'existant : séances, exercices, séries. « Cette action remplacera votre
programme » n'est pas un consentement éclairé ; trois nombres le sont.

## 3. Décisions verrouillées

- **Mécanisme** : un champ de formulaire `confirm_replace: Annotated[bool, Form()] = False`.
- **Défaut** : `False`. L'absence du champ ne vaut jamais consentement.
- **Non confirmé** : `200` avec le résumé et la case à cocher — **pas** une erreur. L'utilisateur n'a
  rien fait de faux ; le formulaire n'a simplement pas encore été accepté. Le message passe donc par
  une variable de contexte `notice` **distincte** de `error`, et n'est **pas** rendu dans la couleur
  `--danger` réservée aux vraies erreurs de saisie (split inconnu, nombre de séances hors bornes).
- **Consentement parsé côté serveur** : `""`, `false`, `0`, `off`, `no` et toute valeur malformée ne
  remplacent jamais l'arbre ; une valeur malformée est un `422`. Un champ `confirm_replace` dupliqué
  (`false` puis `true`) est refusé en `422`, jamais résolu au dernier. Le comportement du navigateur
  ne prouve rien : un POST direct peut porter n'importe quelle chaîne.
- **Arbre intact** : un POST non confirmé n'appelle **pas** `replace_draft_tree`. C'est l'invariant
  central du sprint.
- **Confirmé** : le chemin existant, inchangé — `generate_program_tree` puis `replace_draft_tree`,
  puis redirect `303` vers l'éditeur.
- **Programme vide** : comportement **strictement inchangé**. Aucune case à cocher n'est affichée, et
  aucune confirmation n'est demandée : un programme vide n'a rien à perdre, et exiger un
  consentement serait de la cérémonie.
- **`validated`** : remplacement autorisé sous confirmation. `replace_draft_tree` le repasse en
  `draft` via `_owned_editable` — comportement **existant**, non modifié ici, mais désormais testé :
  la validation attestait d'un contenu qui n'existe plus, donc garder le badge serait une affirmation
  fausse.
- **`published` / `archived`** : refusés par le service existant, **même avec** `confirm_replace=true`.
  La confirmation est un consentement à perdre l'arbre, jamais une autorité sur le cycle de vie.
- **Aucun JS** : la case à cocher n'est pas `required`, pour qu'un envoi non confirmé **atteigne le
  serveur** et revienne avec le résumé, plutôt que d'être bloqué par une infobulle du navigateur. La
  garantie est le contrôle serveur ; la case n'est que la façon d'exprimer le consentement.

## 4. Périmètre livré

- `app/routers/user_programs.py`
  - `_render_generate` calcule et expose `has_existing_tree`, `existing_session_count`,
    `existing_exercise_count`, `existing_set_count` (l'arbre est `sessions → exercises →
    rep_targets`).
  - `user_program_generate` accepte `confirm_replace` et ne refuse que si l'arbre existe **et** que la
    confirmation est absente.
- `app/templates/user_programs/generate.html`
  - avertissement explicite d'irréversibilité ;
  - résumé chiffré de ce qui sera remplacé ;
  - case `confirm_replace` affichée **uniquement** si l'arbre n'est pas vide ;
  - le formulaire est désormais rendu dans les deux cas (il était masqué sur un programme non vide) ;
  - libellé du bouton adapté (« Remplacer et générer » / « Générer la base »).
- `tests/test_user_programs_generate_http.py` — 11 tests ajoutés (§5).

## 5. Preuves

| # | Cas | Attendu |
|---|---|---|
| 1 | programme vide | `303`, arbre créé, aucune confirmation demandée |
| 2 | non vide sans `confirm_replace` | `200`, séances/exercices **inchangés**, nom de séance inchangé |
| 3 | non vide avec `confirm_replace` | `303`, arbre remplacé, la séance semée a disparu |
| 4 | `validated` + confirmation | `303`, statut repassé à `draft` |
| 5 | `published` + confirmation | `200`, arbre intact |
| 6 | `archived` + confirmation | `200`, arbre intact |
| 7 | GET non vide | avertissement + case à cocher présents |
| 8 | GET non vide | résumé affichant séances / exercices / séries |
| 9 | GET vide | **aucune** case à cocher |
| 10 | autre utilisateur / absent | `404` **indistinct** dans les deux cas |
| 11 | régénération | aucune `UserProgramQualityReview`, aucun `WorkoutTemplate` |
| 12 | valeurs non acceptées (8 cas) | `200` ou `422`, arbre **et** exercices intacts |
| 13 | champ `confirm_replace` dupliqué | `422`, arbre intact |
| 14 | page non confirmée | **pas** de rendu `--danger` ; une vraie erreur l'est toujours |
| 15 | page non confirmée | renvoyable telle quelle avec la confirmation → `303` |
| 16 | séance sans exercice / exercice sans série | résumé rendu, `0` affiché |

## 6. Non-goals (vérifiés)

Aucune migration, aucun snapshot DB, aucun nouveau service. `user_program_generator.py`,
`user_program_drafts.py` et `program_quality_*` ne sont pas modifiés. Aucune
`UserProgramQualityReview` n'est écrite, aucun `WorkoutTemplate` créé. EKB_04 n'est pas ouvert, les
JSON EKB ne sont pas touchés, ASSET / BodyMap non plus. Aucun JavaScript obligatoire n'est introduit.

## 7. Limites assumées

- **Pas d'annulation.** Le remplacement est irréversible : il n'existe ni sauvegarde ni historique de
  l'arbre précédent. Le résumé chiffré est la seule protection, et elle est humaine. Un historique de
  versions serait un sprint à part entière (nouveau modèle, migration, rétention) et sort du cadre.
- **Le résumé est un instantané.** Il décrit l'arbre au moment du rendu. Entre l'affichage et le POST,
  une édition concurrente dans un autre onglet le rendrait obsolète — le remplacement porterait alors
  sur un contenu légèrement différent de celui annoncé. Le verrouillage optimiste de l'arbre relève
  de l'éditeur, pas de ce sprint.
