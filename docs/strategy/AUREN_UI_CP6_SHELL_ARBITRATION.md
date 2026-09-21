# `UI-CP6 SHELL` — brief d'arbitrage

> **Ouvert le 2026-09-21**, après le closeout de `UI-CP5 FLIGHT_RECORDER`
> (merge `21e74d0`, CI canonique 7/7).
>
> **Ce document ne propose pas de refonte.** Il mesure la coque, sépare ce qui
> va déjà de ce qui coûte, et pose **quatre questions fermées**. L'opérateur
> tranche ; la tranche se construit ensuite.

---

## 0. Ce que la coque fait DÉJÀ BIEN, et qu'il ne faut pas « corriger »

Mesuré, pas supposé. Ces points sont **acquis** et une tranche `SHELL` qui les
défait serait une régression :

| Acquis | Mesure |
|---|---|
| Quatre destinations primaires, une seule fois chacune | `au_repos = 4` sur mobile |
| Aucune destination offerte **et** au repos **et** derrière le geste, dans une même structure | `repos_et_geste = []` aux deux ruptures |
| Le desktop ne paie **aucun** budget vertical | rail latéral → `coque_px = 0` à 1024 px |
| Zéro JavaScript | `<details>` natif, SSR |
| Un seul `aria-current` par page | mapping unique `is_sess` / `is_programs` / `is_prog` / `is_prof`, pas de recalcul |

La coque a déjà été assainie deux fois — `Sb_UI_03.3` a rétrogradé la topbar en
navigation **secondaire seulement**, et `UI-CP4` a retiré deux entrées qui
doublaient un onglet primaire.

---

## 1. Ce qui coûte, mesuré à 390 × 844 et 1024 × 768

```
mobile   topbar 69 px + barre basse 57 px = 126 px = 14,9 % de CHAQUE écran
         pied de page 135 px de plus, en bas du défilement
desktop  rail latéral → 0 px de budget vertical
         pied de page 79 px
```

### F1 — La topbar prend 8,2 % de chaque écran mobile pour porter deux choses

Sur mobile, `.topbar` (69 px) ne contient que **le mot-marque** et **le
chevron du menu**. Les quatre destinations primaires vivent dans la barre
basse ; les sept secondaires vivent derrière le chevron.

### F2 — `/` est offert DEUX FOIS au repos, aux deux ruptures

Le mot-marque « Auren » et l'onglet « Séance » mènent au même endroit, visibles
en même temps. `doublons_au_repos = [["/", 2]]`.

⚠ **Ce n'est pas automatiquement un défaut** : un mot-marque qui ramène à
l'accueil est une convention quasi universelle. Mais c'est exactement la forme
que `UI-CP3` et `UI-CP4` ont retirée ailleurs — « deux chemins vers la même
destination, à trois centimètres ». La règle ne peut pas valoir sur l'accueil et
pas sur la coque **sans une raison écrite**.

### F3 — `/contact` est offert deux fois, et au repos sur desktop

Le pied de rail et le pied de page le portent tous deux. Sur mobile, il est dans
le pied de page **et** derrière le chevron.

### F4 — Le pied de page coûte 135 px sur mobile pour un mot-marque et un lien déjà offert

Il ne contient que « Auren » et « Contact ».

### F5 — La navigation secondaire est écrite DEUX FOIS dans `base.html`

`.topbar__nav` et `.app-rail__secondary-nav` listent **les mêmes six liens**,
maintenus en parallèle. `UI-CP4` a dû éditer les deux.

⚠ **C'est le mode d'échec « famille aux deux tiers », déjà armé.** La prochaine
tranche qui touchera l'une oubliera l'autre, et la coque divergera entre mobile
et desktop sans qu'aucune garde ne le voie — les deux blocs ne sont jamais
rendus en même temps, donc aucun test de page ne les compare.

---

## 2. Les quatre questions

### Q1 — La topbar mobile mérite-t-elle ses 69 px ?

| | |
|---|---|
| **A** | **La retirer sur mobile.** Le chevron descend dans la barre basse en 5ᵉ position (« Plus »), le mot-marque disparaît sous 1024 px. Gain : **8,2 % de chaque écran**. Coût : la barre basse passe de 4 à 5 cibles, soit 78 px par cible à 390 px de large — au-dessus du plancher de 44. |
| **B** | **La garder, la réduire.** 69 → 44 px. Gain : 3 % par écran. Le mot-marque survit. |
| **C** | **Ne rien changer.** Le coût est réel mais assumé ; l'identité de produit vaut 69 px. |

**Ma recommandation : B.** A est plus propre en budget, mais il met une
destination non primaire (« Plus ») au même rang visuel que les quatre
primaires, ce que le socle interdit ailleurs. B prend le gain sans créer ce
conflit de rang.

### Q2 — Le mot-marque doit-il rester un lien vers `/` ?

| | |
|---|---|
| **A** | **Oui, et on l'écrit.** La convention l'emporte ; le doublon est justifié par écrit dans le relevé de décisions, pour qu'aucune tranche future ne le « corrige ». |
| **B** | **Non.** Le mot-marque devient du texte. Une seule route vers `/` : l'onglet. |

**Ma recommandation : A.** Le doublon est réel, mais un mot-marque non cliquable
casse une attente forte, et l'onglet « Séance » ne *se lit* pas comme « accueil ».
La règle « pas deux chemins vers la même destination » a été écrite contre des
**tuiles de navigation**, pas contre une identité de produit. Il faut juste que
l'exception soit **écrite**, pas tacite.

### Q3 — Que devient le pied de page ?

| | |
|---|---|
| **A** | **Le retirer des surfaces d'instrument**, le garder sur les documents (`coach_report`, `export`, `science`, `atlas`). Contact reste dans la navigation secondaire. Gain : 135 px sur mobile. |
| **B** | **Le réduire** à une ligne de 44 px, partout. |
| **C** | **Ne rien changer.** |

**Ma recommandation : A.** `AUREN_INSTRUMENTS §2bis` sépare déjà **cockpit** et
**documents** et exige que la frontière soit perceptible. Un pied de page est un
objet de document ; l'avoir sur un instrument brouille précisément cette
frontière. Et Contact n'est perdu nulle part.

### Q4 — Les deux navigations secondaires doivent-elles fusionner en une source ?

| | |
|---|---|
| **A** | **Oui — un partiel unique**, rendu deux fois avec des classes différentes. Une seule liste à maintenir. |
| **B** | **Oui, et une garde le tient** : un test compare les deux ensembles de destinations et échoue s'ils divergent. |
| **C** | **Non.** Les deux structures ont des contraintes différentes ; les coupler les fige ensemble. |

**Ma recommandation : B, qui contient A.** Le partiel unique règle le cas
d'aujourd'hui ; la garde règle le cas où une tranche future décide, pour une
bonne raison, de les re-séparer — elle échouera alors **en disant pourquoi**,
au lieu de laisser la divergence s'installer en silence. C'est exactement la
leçon que `UI-CP5` vient de payer cinq fois.

---

## 3. Hors périmètre proposé pour `UI-CP6`

À confirmer par l'opérateur :

- **aucune** refonte des quatre destinations primaires — elles sont arbitrées ;
- **aucun** changement de la rupture 1024 px ;
- **aucun** JavaScript ;
- **aucune** route supprimée ou renommée ;
- `/science`, `/atlas`, `coach_report`, `export` — la **frontière** cockpit /
  document est nommée en Q3 mais leur mise en forme propre reste une autre
  tranche.

---

## 4. Ce que je n'ai PAS mesuré, et qu'il faudra mesurer avant de construire

Honnêteté de portée — ces points ne sont pas couverts par ce brief :

- le comportement de la coque **pendant une séance active**
  (`is-session-focus-mode` change le corps entier) ;
- les ruptures intermédiaires entre 390 et 1024 px ;
- le rendu sur un viewport **court** (paysage mobile), où 126 px de coque
  pèsent beaucoup plus lourd que 14,9 % ;
- l'état **non connecté**, où la coque n'a pas les mêmes destinations.

Ces quatre mesures sont la première étape de la tranche, une fois l'arbitrage
rendu.
