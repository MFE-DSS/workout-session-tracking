# UI-CP2 — A+, l'instrument d'exécution

**Tier `check_scope`** : `SHARED_CODE`.
**Question souveraine** : *que fais-je maintenant ?*
**Concept retenu par l'opérateur** : **A+** — instrument plein état + orientation
persistante minimale.

---

## 1. Ce que l'écran faisait, mesuré

Séance réelle `push-a`, 7 exercices, 29 séries. Chaque état atteint **par le
produit** et confirmé dans le DOM par `data-console-state` — jamais déduit.

| état | écrans | commandes | dont hors état | cibles < 44 px |
|---|---|---|---|---|
| warmup | 3,27 | 23 | 13 | 7 |
| current_set | 3,27 | 22 | 13 | 7 |
| rest | 3,17 | 23 | 13 | 7 |
| correction | 3,07 | 20 | 13 | 7 |
| **exercise_complete** | **3,50** | **26** | 13 | 7 |
| last_exercise_complete | 2,68 | 17 | 13 | 7 |

**L'état le plus lourd était celui où l'on a le moins à faire.**

Les treize commandes hors état, nommément : les six autres exercices · « Note
séance » · **« TERMINER LA SÉANCE »** · « Enregistrer sans terminer » · les
trois règles de méthode · « Voir toutes les règles ». Aucune n'avait de rapport
avec la série en cours, et elles étaient **identiques d'un état à l'autre**.

L'ambre plein le plus fort de l'écran terminait la séance, à la série 1 sur 21.

---

## 2. Ce que A+ rend

| état | écrans | commandes | dont hors état | cibles < 44 px |
|---|---|---|---|---|
| warmup | **1,10** | 17 | **0** | **0** |
| current_set | **1,10** | 16 | **0** | **0** |
| rest | **1,00** | 14 | **0** | **0** |
| correction | **1,00** | 15 | **0** | **0** |
| exercise_complete | **1,00** | 16 | **0** | **0** |

Les dix-sept commandes restantes se décomposent en **7 d'instrument** et **10
d'orientation** — retour, `E1/7`, `⋯`, et les sept pastilles. L'orientation est
ce que `§1` autorise explicitement ; **zéro** appartient au contenu d'un autre
état.

### Les six états, et ce qui disparaît

| état | question | action dominante | ce qui disparaît |
|---|---|---|---|
| WARMUP | comment je m'échauffe ? | ÉCHAUFFEMENT SUIVANT | les 6 autres exercices · le bilan · le rappel méthode |
| CURRENT_SET | quelle charge, combien de reps ? | SÉRIE SUIVANTE | idem · la recommandation dépliée |
| REST | combien de temps me reste-t-il ? | PASSER LE REPOS | **la bande de séries** · les champs de saisie · adapter · historique |
| CORRECTION | que corriger sur cette série ? | ENREGISTRER LA CORRECTION | la série courante · le repos · les sorties d'exercice |
| EXERCISE_COMPLETE | et ensuite ? | CONTINUER → *nom* | **la bande de séries** · tout le reste |
| LAST_EXERCISE_COMPLETE | et après la séance ? | ALLER AU BILAN | le formulaire de bilan lui-même |

**REST devient temps-souverain.** Le cadre du minuteur tombe — c'était la
*carte de minuteur* que `§5` interdit nommément — la bande de séries disparaît,
et il ne reste **qu'une sortie**. Le défaut `DF-B` ne peut plus se reproduire :
il naissait de la ligne de série portant une seconde affordance ambre face à
celle du dock, et cette ligne n'existe plus à cet état.

---

## 3. Capacités — aucune perdue

| capacité | où elle vit |
|---|---|
| atteindre les 6 autres exercices | `?active=<id>` — sélection **serveur**, pas une ancre ; bande d'orientation + sélecteur d'en-tête, sans JavaScript |
| bilan de séance, TERMINER LA SÉANCE | `?view=bilan` — atteint depuis `LAST_EXERCISE_COMPLETE` **et** depuis `⋯` à tout moment. Une séance incomplète reste closable (`Q2`) |
| rappel méthode | accompagne la clôture ; `/science` inchangé |
| référence historique d'un exercice | dans **sa** console, au point de décision |
| avancement de chaque exercice | nom accessible des pastilles d'orientation |
| récapitulatif d'un exercice terminé | contenu principal de `EXERCISE_COMPLETE` |
| saisie cardio | une séance sans exercice est **déjà** à sa clôture |

**Ce qui est réellement retiré** : la vue « les sept performances passées d'un
coup d'œil ». C'est le but de A+, et `§1` interdit de la réintroduire sous
forme de carte de séance permanente.

---

## 4. « Première fois » — une affirmation fausse, retirée

L'absence de référence **prescrite** ne prouve pas que l'utilisateur n'a jamais
fait le mouvement : la politique de sélection saute les occurrences
substituées. Quelqu'un ayant fait l'exercice il y a sept jours avec un
substitut se voyait annoncer « Première fois ». **Ce n'était pas une
information manquante, c'était une inférence sur la personne, et elle était
fausse.**

L'état est désormais nommé pour ce qu'il est : **« Aucune référence
prescrite »** — un fait sur la donnée.

⚠ **Le mot suit le vocabulaire du produit.** Ma première écriture disait
« repère », un mot concurrent de `Réf.` — l'étiquette employée deux lignes plus
haut — et qu'une garde existante interdisait précisément pour cette raison.
« Référence » est le mot dont `Réf.` est l'abréviation : aucun vocabulaire
n'est inventé.

---

## 5. Trois défauts que j'ai introduits, trouvés en mesurant

| # | Défaut | Trouvé par |
|---|---|---|
| 1 | **Une séance cardio rendait une page VIDE.** Elle n'a aucun exercice, et sa seule saisie était passée derrière `?view=bilan` | `test_cardio_capture` |
| 2 | **Ma bande d'orientation introduisait à elle seule les 7 cibles sous 44 px** — `padding` + marges négatives mesuraient **38 px**, et mon propre commentaire affirmait le contraire | sonde au navigateur |
| 3 | **Une ancre morte** — la redirection vers le repos posait `#set-N`, que cet état ne rend plus. Un fragment qui ne résout pas ramène en haut de page | `test_set_anchors_are_unique_in_every_rendered_state` |

Et une **duplication d'`aria-current`** : la bande et le sélecteur annonçaient
tous deux « vous êtes ici ». Deux navigations peuvent marquer leur élément
courant sans rien dire de faux ; ce qui serait fautif est d'annoncer **deux
exercices différents**. C'est cet invariant-là qui est désormais gardé — plus
fort que le comptage qu'il remplace.

---

## 6. Gardes — 36 converties, 8 neuves, aucune supprimée

### Converties (36)

Elles épinglaient la **composition en liste** ; elles tiennent désormais la
**capacité**. Deux se **renforcent** :

* « exactement un `aria-current` » → « un seul **exercice** annoncé courant » ;
* « une carte ouverte parmi N » → « une seule carte, et elle est ouverte ».

Deux gardes lisaient **leur propre prose** : elles interdisaient le mot
« repère » dans le fichier entier, commentaires Jinja compris — donc
interdisaient qu'on *parle* du mot autant que qu'on l'*affiche*. Elles
retirent désormais les commentaires avant de chercher, ce qui est le remède
que ce dépôt documente déjà.

### Neuves (8) — et pourquoi elles existent

**La replantation a révélé le trou.** Défaire la recomposition du repos —
c'est-à-dire le cœur de A+ — laissait la suite **entièrement verte**. Les
trente-six gardes converties protègent des capacités héritées ; **aucune ne
disait ce que A+ apporte**.

C'était l'oubli d'`UI-CP1` qui se répétait sur la tranche suivante : livrer une
capacité sans les gardes de sa substance.

`tests/test_ui_cp2_execution_aplus.py` tient : un seul exercice rendu · les
autres atteignables sans JavaScript · le bilan et le rappel méthode hors
exécution **et présents ailleurs** · le repos temps-souverain · aucune carte de
minuteur · l'exercice terminé léger · la cible tactile de la bande ·
l'orientation qui ne devient pas une carte de séance.

---

## 7. Vérifications

| Contrôle | Résultat |
|---|---|
| `check_scope` | `SHARED_CODE` |
| `ruff` | 1 `UP031` **préexistant**, aucun ajouté |
| `check_ruff_budget` | **267 ≤ 548**, inchangé |
| `check_spec_protocol` | OK |
| **Sweep local complet** | **328 fichiers / 328, tous les lots verts**, pic 1 744 Mo (budget 1 816) |
| **5 capacités replantées** | **5 suites rouges** |
| Pré-balayage AST S9073 / S5863 | **zéro assertion composite ajoutée** |
| Rendu exposé à l'opérateur | **avant le commit**, six états à 390 px |

## Closeout

| | |
|---|---|
| PR | **#229**, méthode `--merge` épinglée sur `476e3c6` |
| merge | `669244d6498285dc8f9160f6d6a3849c1427a875` |
| checks PR | **9/9 pass**, gate Sonar `OK` sur ses cinq conditions, **100 %** de couverture du nouveau code |
| CI canonique | run `34257276972` — **success, 7/7** |
| threads de revue | **0** non résolu |

**Séquence respectée cette fois** : brainstorm → artefact d'arbitrage →
décision opérateur → tranche d'habilitation (`UI-CP2.0`) → **rendu réel exposé**
→ arbitrage → implémentation → commit. `CLAUDE.md §5.1` est tenu dans le bon
ordre, ce qui n'avait pas été le cas sur `UI-CP1`.

### ⚠ CI rouge — un filtre `-k` n'est pas un sweep

**Job** : `pytest shard 2` et `shard 3`. **Quatre gardes**, dans
`test_briefing_surface.py` et `test_ui_command_intelligibility.py` — deux
fichiers qu'aucun de mes mots-clés n'atteignait, et dont la cause racine était
**exactement** celle des trente-deux déjà converties.

J'avais lancé `pytest -k "session or console or focus or …"` en croyant borner
un rayon d'impact. **Un filtre par mots-clés borne ce qu'on a pensé à
nommer** ; un rayon d'impact est précisément ce qu'on ne connaît pas. 1 535
verts en local, deux shards rouges en CI.

Ce dépôt documentait déjà quatre façons de mesurer le mauvais objet. C'est la
cinquième. **Règle retenue** : dès qu'une tranche change une *composition*, le
sweep complet passe avant le push.

---

## 8. Ce que la tranche ne fait PAS

CP-3 fermé · aucune refonte des six autres surfaces · aucune migration de
tokens · ni coque, ni MISSION, ni FLIGHT_RECORDER, ni social · aucun système de
cartes générique — ni `ActiveSetCard`, ni `RestCard`, ni `TimerCard`.

**Non-bloquant, consigné** : `test_vscode_settings_json_exists` échoue à
l'identique sur le canonique — il asserte sur un fichier **non suivi par git**.
