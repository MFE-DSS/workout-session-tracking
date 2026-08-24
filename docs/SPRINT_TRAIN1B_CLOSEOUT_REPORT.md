# TRAIN 1-B — closeout, et un garde-fou qui détruisait du travail

**Date** : 2026-08-24
**Canonique finale** : `78a6230`
**Base d'entrée** : `b22098d`

---

## 1. Ce qui est livré

| PR | Contenu | Merge | Méthode |
|---|---|---|---|
| #150 | `Sb_OPS_LOCAL_SWEEP_MEMORY_01` — le sweep local ne tue plus la machine | `8661122` | `--merge`, tête `1873c8d` |
| #147 | `TRAIN1-B` — instrument PROGRESSIF (A10) | `78a6230` | `--merge`, tête `f9f18eb` |

**Aucun squash, aucun `--admin`, aucun force.** Tête épinglée à chaque merge.
#150 d'abord : c'est l'outillage, il ne touche aucun code applicatif.

**CI canonique — source de vérité** : run
[`32723472115`](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/32723472115)
sur `78a6230` — **`success`, 6/6 jobs verts**. Elle couvre les deux merges
cumulativement, et vaut validation impérative pour le tier `CI_INFRA` de #150.

---

## 2. A10 — ce que l'audit avait déplacé

La question n'était pas « quelle règle de comparaison inventer ». **La
primitive existait déjà**, dans `delta.py` :

> « The function NEVER infers a "delta" from partial data. »

L'exigence opérateur « pas de score global inventé » était **déjà le contrat
écrit du dépôt**. Cette tranche la réutilise sur une identité qui, elle,
change.

### L'identité franchit le gabarit

| Mesuré sur le catalogue | |
|---|---|
| identités héritées `(gabarit, code)` | **106** |
| exercices réels | **68** |
| exercices dans ≥ 2 gabarits | **28** |
| `Leg extensions assises` | **4 gabarits, 3 codes** — même la clé héritée n'était pas stable |

Rendu à l'écran :

```
Tirage poulie haute prise neutre     60 × 10 → 55 × 12     −5 kg  +2 reps
Chest Press machine                  70 × 10 → 72,5 × 10   +2,5 kg  = reps   2 programmes
```

**Aucune couleur de jugement** — vérifié au `getComputedStyle` : tous les
écarts partagent `rgb(167,176,186)`. `Delta.score_trend` (`up`/`down`), le seul
champ de la primitive qui porte un verdict, est **écarté**.

### Le cardio ne rentre pas de force

Ses données vivent sur `WorkoutSession` : ni série, ni charge, ni répétition.
Durée en fait primaire, bpm en **contexte jamais comparé**, comparaison **à
machine identique** seulement. Les calories ne sont pas seulement masquées :
elles **ne sont pas chargées**. On ne peut pas afficher par distraction ce
qu'on n'a pas.

---

## 3. Trois défauts trouvés en construisant A10

1. **L'instrument dupliquait un bloc existant — vu au rendu.** « Activité
   récente par exercice » listait les mêmes faits sur l'identité héritée, et
   affichait « Chest Press machine » **deux fois, une par gabarit**. Livrer les
   deux aurait ajouté une duplication à l'écran que `TRAIN1-A` venait
   d'écrémer. Retiré, remplacé dans la même livraison :
   **3,4 → 2,7 écrans, 533 → 343 mots.**

2. **La table d'identité n'était pas semée au démarrage.** `A1` l'avait
   branchée sur `scripts/seed_db` ; le `lifespan` ne semait que le catalogue.
   Sur tout déploiement non reseedé, l'instrument n'affichait **rien, sans
   erreur ni message**. Une surface qui marche sur le poste du développeur et
   nulle part ailleurs.

3. **Les occurrences non rattachées devenaient invisibles** quand elles étaient
   seules — trouvé par un test migré, pas par relecture.

Et une garde de l'agent prise à lire la **docstring** du module cardio au lieu
du code. **Huitième occurrence** de ce motif dans ce dépôt ; réécrite sur
l'AST.

---

## 4. Le sprint que l'opérateur a imposé au milieu, et qui valait plus que la tranche

`CLAUDE.md §1` prescrivait `run_ci_pytest.sh` comme **la** commande de full
sweep, « CI comme local, même source de vérité ». Lancée sur un poste, elle a
tué VS Code **à répétition**.

Le coût n'est pas le sweep perdu. **Un garde-fou qui n'aboutit jamais ne rend
aucune information, et il détruit le travail d'à côté.** Trois sweeps ont dû
être abandonnés dans cette seule session.

### La formule était juste, l'hypothèse était fausse

Le plafond « ~5 Go par worker » raisonne sur la RAM **installée** — 16 Go, donc
2 workers autorisés. Mesuré : **5 365 Mo seulement étaient DISPONIBLES**.
Elle supposait la machine dédiée au sweep. Elle ne l'est jamais.

### Trois mesures, et la troisième a retourné le raisonnement

| Lots de 12 | pics 724 → **2 896 Mo** · chien de garde déclenché au lot 20 |
| Lots de 6 | pics 131 → 1 793 · déclenchement au lot 39, à 2 326 Mo |
| **Par fichier** | 1346 + 697 + 334 Mo **séparément**, **2 157 en lot** |

La mémoire **n'est pas rendue d'un fichier à l'autre** dans un même processus.
Le plancher du pic n'est donc pas la taille du lot mais **le fichier le plus
lourd — 1,3 Go à lui seul**. Réduire le lot a un rendement décroissant, et un
budget plancher sous ce coût arrêterait le sweep au premier lot : le défaut
corrigé sous une autre forme.

Sans cette troisième mesure, j'aurais réduit le lot indéfiniment en croyant
descendre.

### Preuve de bout en bout

```
69/69 lots · tous verts · 0 échec
pic mémoire observé : 2 231 Mo (budget 2 397 Mo)
```

**Le sweep local aboutit** — ce qui n'était plus le cas.

### Le refus est mécanique, parce que la prose a déjà échoué

`run_ci_pytest.sh` refuse désormais de s'exécuter hors CI et **nomme**
l'alternative. La version précédente expliquait longuement le risque, en
commentaire **et** dans `CLAUDE.md` — et le script a quand même été lancé en
local plusieurs fois, **par l'agent, dans cette même session**. Une règle qu'on
peut enfreindre sans rien casser n'est pas une règle.

`ALLOW_LOCAL_CI_SWEEP=1` garde le diagnostic délibéré possible : **nommé**,
donc jamais accidentel. Le chemin CI est **intact**, vérifié avec `CI=true`.

---

## 5. Deux gardes réparées, dont une qui serait passée pour la mauvaise raison

`test_a_non_numeric_worker_count_is_refused` assertait `"REFUS" in stderr`. Mon
nouveau refus local dit **aussi** « REFUS » : la garde aurait continué à passer
**sans jamais éprouver le refus qu'elle vise**. Elle asserte désormais le
message propre à la valeur non entière.

`test_the_local_worker_count_is_capped_by_physical_ram` n'atteignait plus le
plafond qu'elle teste.

---

## 6. Vérifications

| Contrôle | #150 | #147 |
|---|---|---|
| `check_scope` | `CI_INFRA` | `SHARED_CODE` |
| Gardes | 75 → **89** | **30** dédiées |
| Broad sweep | sweep par lots **69/69** | **623** |
| CI PR | 8/8 · Sonar OK | 8/8 · Sonar OK · couverture neuve 88,7 % |
| Exposition §5.1 | — | **12 écrans entiers**, 360/390/430 × 3 comptes |

**Incidents Sonar, tous in-scope et corrigés à la source** : `css:S4666` —
`.cardio` était **déjà pris** par le paragraphe de `template_detail.html`, et
la règle préexistante suivant la mienne, les deux composants se stylaient l'un
l'autre ; renommé `.cardio-lane`. ⚠ Ma première réécriture, faite au `sed`, a
renommé **les deux** et cassé l'autre page — rattrapé, avec un commentaire qui
réserve le nom. `python:S8415` — 404 non documenté.

### Une faute de méthode répétée, et sa correction

`test_past_session_readability` est sorti **en CI** parce que ma sélection de
broad sweep était encore faite à la main : je l'avais incluse pour `TRAIN1-A`
et oubliée pour `TRAIN1-B`. **Deux cycles de CI perdus sur la même erreur.**

Sélection dérivée mécaniquement des fichiers modifiés : elle rend **274
fichiers de test, c'est-à-dire la suite entière**. Ce n'est pas un défaut du
procédé mais la réponse juste — quand un diff touche `pages.py`, `sessions.py`,
`main.py` **et** `app.css`, le rayon d'impact **est** la suite. Et c'est
précisément pourquoi #150 devait exister d'abord : le full sweep n'est utile
que s'il aboutit.

---

## 7. Ce que TRAIN 1-C peut maintenant faire

Sa condition d'entrée est **remplie** : les trois instruments existent.

| Instrument | Livré par |
|---|---|
| **Temporel** — rail inspectable, état vide compact | `TRAIN1-A` |
| **Anatomique** — exposition avec quatre états de preuve | `MUSCLE_MAPPING_TRUTH_01` |
| **Progressif** — comparaisons factuelles par exercice | `TRAIN1-B` |

L'inventaire du Dashboard peut donc commencer, et ne garder que ce qui répond
à une question **autrement sans réponse**.

Deux points déjà mesurés l'attendent : « Par programme » rend une carte pleine
pour dire « aucune session » sur un compte vide, et deux `—` subsistent dans
« Rythme récent » — exacts, mais dont le sort demande une décision produit sur
ce que rend un KPI sans dénominateur.
