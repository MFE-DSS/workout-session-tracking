# SPRINT Sb_MORPHO_PROFILE_READMODEL_01 — inspectable, sans pouvoir (RAPPORT)

**Train :** `AUREN_MORPHO_RUNTIME_FOUNDATION_01`, tranche 2/3 ·
**Base canonique :** `8313dcd` · **Branche :** `sb/morpho-profile-readmodel-01`

---

## 1. Brainstorming / Options / Risques / Choix retenu

La tranche 1 a rendu le profil morphologique **calculable**. Celle-ci le rend
**lisible** — et tout le risque tient dans une phrase : une interface qui montre
une lecture morphologique suggère qu'elle sert à quelque chose. Or elle ne sert
encore à rien, par décision de train.

### Le problème de formulation, découvert dans le code

Le moteur attache à chaque descripteur un `non_medical_guardrail`. Sa valeur
réelle est un **démenti** :

```
"Lecture non médicale et non contraignante — aucune composition corporelle,
 aucune posture, aucun diagnostic, aucune longueur osseuse."
```

L'afficher tel quel aurait mis « posture », « diagnostic » et « longueur
osseuse » **sous les yeux du lecteur**, au moment précis où l'on prétend ne pas
parler de ça. C'est l'erreur que ce train a déjà commise deux fois (« no EMG
claim », « pas une fraction d'activation musculaire »), et qu'un test de
formulation avait refusée à chaque fois.

**Options.** (a) rendre le démenti — rejetée, il fabrique le cadre qu'il nie ;
(b) le supprimer du modèle — rejetée, il a une valeur d'audit réelle ;
(c) *(retenue)* **le conserver dans le read model, ne pas le rendre**. Un test
vérifie les deux moitiés : le garde-fou existe côté données, et la chaîne
« aucun diagnostic » n'apparaît pas sur la page.

### Risques et traitements

| Risque | Traitement |
|---|---|
| L'UI laisse croire à un effet sur le programme | phrase obligatoire rendue **et testée** : « Ces éléments ne modifient pas encore automatiquement ton programme. » |
| Une envergure absente devient une valeur neutre | la ligne ape index **n'existe pas** ; `missing` porte « Envergure non renseignée » |
| Une confiance devient un pourcentage | catégories seulement (`mesuré`, `calculé à partir de mesures`, `lecture qualitative, étayage faible`) ; test anti-`%` sur le texte visible |
| Doublons faits/lectures | les descripteurs `FACT` sont exclus des « Lectures » — ils répéteraient le tableau |

---

## 2. Ce qui est livré

`app/services/morphology_readmodel.py` — pure lecture, aucun `db.add`,
`db.commit`, `db.delete` ni `db.merge` (vérifié par test).

La carte « Mesures morphologiques » vit **sur la page profil existante**. Aucune
route dédiée : `/morphologie` et `/morphology` répondent 404, et un test le
vérifie plutôt que de le supposer.

Elle affiche les derniers faits connus avec **leur base** (« moyenne gauche +
droite », « côté gauche seul », « ancienne saisie unique », « profil »), l'ape
index **seulement si taille et envergure existent**, la liste explicite de ce
qui manque, puis les lectures du moteur avec couche et catégorie de confiance.

Quand les faits viennent de plusieurs dates, la carte le dit avant de les
montrer.

---

## 3. Preuves

| Preuve | Résultat |
|---|---|
| Tests dédiés | **45** |
| Balayage ciblé (9 fichiers touchant `/profile` + moteur + adaptateur) | **213** |
| Budget ruff | 536 ≤ 548 |
| Pré-scan Sonar (S9073 / S1192) | **0 / 0** sur les fichiers neufs |
| Écriture en base depuis le read model | **aucune** |

### Plantation — une garde faible démasquée

En faisant retourner à `_ape_index` une ligne `value=0.0, basis="neutre"`
lorsque l'envergure manque :

- `test_a_missing_wingspan_is_named_not_neutralised` **tombe** — garde vivante ;
- `test_the_page_never_shows_a_neutral_ape_index` **restait verte**.

La seconde n'interdisait que deux formulations littérales (« ape index neutre »,
« ape index : 0 ») que le rendu ne produit jamais : les cellules affichent
`Ape index` et `0.0 cm` dans des colonnes séparées. Elle vérifiait une tournure,
pas l'invariant. Elle affirme désormais que **la ligne est absente**. Replantée :
les deux tombent.

> Note honnête : mon premier test anti-pourcentage scannait le HTML brut et
> tombait sur `width:100%` — une largeur CSS, pas une confiance. Le scan porte
> désormais sur le texte **visible**, balises retirées.

---

## 4. Isolation du planificateur

Aucun des **8 modules gelés** ne mentionne `morphology_readmodel` (test
paramétré). Charger la page profil ne déplace pas l'empreinte du plan
hebdomadaire, vérifié avant/après insertion d'un jeu complet de faits.

Le read model n'a aucun consommateur planificateur : il est appelé par la seule
route profil.

---

## 5. Limites énoncées

- **Aucune observation** n'alimente le moteur (aucune surface ne les capture),
  donc les lectures restent à **confiance structurellement réduite**. La page
  affiche la catégorie de confiance telle quelle, sans la compenser.
- `shoulder_width_cm` reste capturé et non consommé (OQ-1 de la spec de capture).
- Le `non_medical_guardrail` n'est pas rendu — décision assumée, testée.

## Verdict

Le profil morphologique est **inspectable et sans pouvoir**. Ce qui manque est
nommé, ce qui est calculé dit d'où il vient, et la page déclare explicitement
qu'elle ne change pas encore le programme.

Le vrai piège de la tranche n'était pas l'affichage : c'était de rendre un
démenti et de croire que c'était une précaution. Il est resté côté audit.

---

## Closeout (post-merge)

| | |
|---|---|
| PR | **#104** — `--merge --match-head-commit`, **sans** squash / `--admin` / force |
| Build | `f39a665` — **vert au premier passage**, aucun correctif |
| Merge | **`e559059`** |
| CI canonique | run `31935918896` — **succès, 3/3** |
| Gate Sonar | **`OK`** — 0 smell, 0 bug, 0 vulnérabilité, couverture new code **100,0 %** |
| Threads / Gitar | **0 / 0** |
| Tests CI | 2 174 + 2 249 = **4 423** |

### Capacité CI — **HEALTHY, mais la marge se resserre**

| | Shard A | Shard B |
|---|---|---|
| min MemAvailable | **4 666 Mo** | **4 380 Mo** |
| min SwapFree | 3 071 Mo — **jamais entamé** | 3 071 Mo — **jamais entamé** |
| `workers=` | 2 | 2 |

Les deux shards restent au-dessus du seuil `HEALTHY` de 4 Go, donc **aucune
règle d'arrêt n'est déclenchée**. Mais la tendance mérite d'être dite plutôt que
découverte au prochain train :

| Tranche | Shard A | Shard B |
|---|---|---|
| `Sb_CI_TMPSTATE_FLAKE_01` | 5 195 Mo | 5 065 Mo |
| `Sb_MORPHO_PROFILE_RUNTIME_01` | 4 838 Mo | 4 772 Mo |
| **`Sb_MORPHO_PROFILE_READMODEL_01`** | **4 666 Mo** | **4 380 Mo** |

Le shard B a perdu **685 Mo en deux tranches**, dont ~390 Mo sur celle-ci, et
n'est plus qu'à **~380 Mo** du plancher. Trois tranches ne font pas une loi,
mais la pente est régulière et elle suit l'ajout de tests (4 314 → 4 378 →
4 423). Le prochain train devrait **vérifier la capacité avant** d'ouvrir une
tranche runtime, pas après.
