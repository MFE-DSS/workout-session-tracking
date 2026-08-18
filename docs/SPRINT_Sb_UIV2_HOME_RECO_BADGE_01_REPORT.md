# `Sb_UIV2_HOME_RECO_BADGE_01` — le hero dit quoi, le ⓘ dit pourquoi

**Base** : `ad5edc0` · **Tier `check_scope`** : `ISOLATED` (traité au-dessus, §6)
**Première tranche visible de la refonte Accueil.**

---

## 1. Pourquoi cette tranche existe

`app/templates/index.html` **n'avait pas été modifié depuis le 11 juillet**.

Les décisions D1–D5 étaient prises, validées, versionnées. Les maquettes
existaient — `reco-badge.html`, `interactivity-hybrid.html`, `etat-corporel.html`
— et l'opérateur les avait vues, ouvertes dans son navigateur, itérées pendant
des heures.

Elles vivaient dans `.superpowers/brainstorm/`, **un dossier exclu de git**.

L'opérateur a donc légitimement cru le travail intégré. Il ne l'était pas. Des
maquettes indiscernables du produit, montrées dans un navigateur et validées une
par une, créent cette confusion — le statut `DOCUMENTED — NOT BUILT` écrit dans
un fichier ne la compense pas.

---

## 2. Ce qui est construit

### D2 — le badge d'origine

```html
<details class="reco-origin">
  <summary class="reco-origin__badge">
    <span class="reco-origin__label">Recommandé</span>
    <span class="reco-origin__volume">21 séries</span>
    <span class="reco-origin__info">ⓘ</span>
  </summary>
  <p class="reco-origin__why">Bon premier template pour démarrer : Push A…</p>
</details>
```

Le ⓘ révèle **la vraie phrase du moteur** — `recommendation.py` la calcule depuis
toujours et rien ne l'affichait. Bleu = origine système (D3). `<details>` natif :
**zéro JS**, repli sans script intact. Cible tactile 44 px (D1, rang 2).

**Interdiction tenue** : aucune revendication d'IA. Le moteur se décrit comme
*déterministe, explicable, zero-ML* — c'est son avantage, il sait dire pourquoi,
ce qu'une boîte noire ne fait pas.

### D6 — l'état corporel explique la recommandation

C'est la conséquence de la décision opérateur la plus structurante de la session :

> Le cycle n'est pas un calendrier. C'est une rotation pilotée par la
> **récupération** — toujours travailler ce qui est physiologiquement
> disponible.

Donc l'état corporel n'est pas une vignette posée à côté de la recommandation :
**c'est son explication**. Sous la phrase du moteur, le ⓘ liste l'état des zones
que *cette* séance vise :

```
● Pectoraux             disponible
● Deltoïdes latéraux    récupération partielle
```

### D4 — les trois suppressions

| Cible | Traitement |
|---|---|
| « Aucune séance active » | **supprimé** — le CTA le disait déjà |
| Doublon « Aujourd'hui » | **vignette retirée** (53 lignes) |
| Vignette « Cette semaine » vide | **masquée** tant que `sessions_done == 0` |

**On retire le doublon, pas l'information.** Les raisons secondaires que portait
la vignette sont **repliées dans le ⓘ**. La vignette hebdomadaire réapparaît dès
qu'il y a un vrai signal : « pas encore de séance » n'apprend rien, « 3 séances »
si.

---

## 3. Brainstorming / Options / Risques / Choix (CLAUDE.md §3)

**Option A — un bloc « état corporel » séparé sur l'Accueil.** C'est ce que le
brainstorm envisageait. Rejetée après D6 : juxtaposer l'état et la recommandation
sans les relier rate précisément la décision que l'utilisateur doit comprendre.

**Option B — attendre la géométrie pour construire l'état corporel.** Rejetée :
7 zones sur 11 n'ont aucune plaque, la production dépend d'un workspace externe,
et attendre livrerait zéro.

**Option C — retenue : l'état corporel *dans* l'explication.** Textuel pour
l'instant, anatomique plus tard. Les plaques enrichiront cet objet quand elles
existeront ; elles ne le remplaceront pas.

**Risque principal** : afficher un état que le produit ne mesure pas. Neutralisé
par la règle de silence honnête — une zone sans estimation dit **« non
mesurée »**, jamais « disponible ». Un test le pinne.

---

## 4. Aucune plomberie nouvelle

Tout existait, rien n'était relié :

| Donnée | Source | État avant |
|---|---|---|
| la raison | `reco.top.phrase` | déjà dans le contexte, **jamais affichée** |
| les zones visées | `reco.top.primary_zones` | déjà exposé, jamais lu |
| les bandes | `zone_recovery.build_zone_recovery` | jamais atteint par un template |
| les libellés | `muscle_mapping.ZONE_LABELS` | — |

Seul ajout : **une requête d'agrégat** pour le volume, dans la route — comptée en
SQL plutôt qu'en parcourant `template.exercises[*].rep_targets` en Jinja, ce qui
aurait déclenché des N+1 à chaque rendu. **`recommendation.py` reste intact**
(non modifiable).

---

## 5. Tests

**15 tests dédiés**, dont trois qui portent le sens de la tranche :

- `test_the_listed_zones_are_the_ones_the_session_targets` — le lien D6 : ce ne
  sont pas des zones quelconques, ce sont **les siennes**.
- `test_a_zone_without_evidence_reads_as_unmeasured_never_available` — la règle
  de silence honnête.
- `test_no_ai_claim_is_rendered` — vérifié sur le **HTML servi**, pas sur le
  template.

### Plantations

| Violation injectée | Résultat |
|---|---|
| zones arbitraires (`["quads","calves"]`) au lieu des zones visées | **détectée** |
| zone sans preuve rendue « disponible » | **détectée** |

`pages.py` restauré à l'identique après chaque plantation.

### Deux tests retournés, aucun affaibli

`test_status_label_present` exigeait « Aucune séance active », que D4 supprime.
Il affirme désormais l'inverse **et dit pourquoi** — le libellé survit pour la
séance *active*, où « Séance active » est une vraie information.

Et **ma garde D2 attrapait le commentaire qui documente l'interdit** :
`index.html` écrit légitimement « Interdit : Recommandé IA » à côté du badge pour
expliquer la règle. Bornée au texte rendu. **Dixième occurrence** de ce motif
dans le programme — une garde ne doit pas lire de la prose.

---

## 6. Vérifications locales

`check_scope` a classé `ISOLATED`. **Traité au-dessus** : la page d'accueil est
la surface la plus vue du produit.

| Check | Résultat |
|---|---|
| ruff (fichiers touchés) | propre |
| `check_ruff_budget.py` | 281 ≤ 548 |
| Suite dédiée | **15 passés** |
| Suites Accueil | **466 passés** |
| Full sweep local | **4 898 passés** |
| Rendu HTML | badge **et** zones vérifiés dans la réponse servie, pas dans le template |

---

## 7. Décisions opérateur consignées (D6–D9)

| | Décision | Conséquence |
|---|---|---|
| **D6** | le cycle est piloté par la récupération, pas par un calendrier | l'état corporel **explique** la recommandation ; les deux objets se conçoivent ensemble |
| **D7** | la régularité est une métrique de premier plan | **pas de streak quotidien** — un jour de repos bien pris ne casse rien ; continuité = séances/semaine + qualité du repos + qualité du travail |
| **D8** | un onglet Progression | ce qui **décide** reste sur l'Accueil, ce qui **s'analyse** déménage |
| **D9** | aucune anticipation au-delà de la séance proposée | le moteur ne connaît pas la N+2 : elle dépend de la performance de celle en cours |

D9 mérite d'être relevée : c'est la même exigence d'honnêteté que l'interdit
« Recommandé IA », sous une autre forme. Ne pas promettre ce que le système ne
sait pas.

---

## 8. Limites

- **L'état corporel est textuel.** Les plaques anatomiques viendront quand la
  géométrie existera ; 4 zones sur 11 en ont une aujourd'hui.
- **Sans historique, tout dit « non mesurée ».** C'est correct, et c'est ce que
  montre le rendu de test — mais un nouvel utilisateur verra donc un ⓘ peu
  informatif. Le produit ne peut pas inventer un état qu'il n'a pas.
- **D7 et D8 ne sont pas construits.** Cette tranche livre D2, D4 et D6.
- **Le fourre-tout « Résumé · indicateurs et navigation » subsiste** — il est du
  ressort de D8.

---

## Verdict

**L'Accueil bouge enfin, et il dit maintenant pourquoi.**

La tranche ne doit pas être lue comme du câblage : elle introduit une
**affirmation produit**. Avant, l'application proposait une séance sans se
justifier. Elle explique désormais son choix en termes de récupération — ce qui
est, d'après la décision D6, la logique réelle du produit.

Le plus notable est que **rien n'a dû être calculé**. La raison, les zones
visées, les bandes de récupération : tout existait et rien n'était relié. La
valeur de cette tranche tient dans trois liaisons, pas dans un moteur nouveau.
