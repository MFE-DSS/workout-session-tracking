# `UIV3_HOME_CAUSAL_COCKPIT` — la cause n'est plus repliée

**Base** : `1e761b2` · **Branche** : `sb/uiv3-home-causal-cockpit`
**Spec** : `Sx_UIV3_01` · `Sx_UIV3_04`
**Phase produit 1.** B2, B3, B4 et B5 livrées **ensemble** — l'unité de revue
humaine est une surface complète, jamais une somme de polissages.

---

## 1. Les défauts, mesurés

| Constat sur la canonique | Mesure |
|---|---|
| La cause de la recommandation n'était **jamais visible** sans interaction | **0 px** au-dessus de la ligne de flottaison |
| Ouvrir le pli **déplaçait la décision** vers le bas | l'explication était rendue **avant** le titre |
| Le hero réservait une hauteur qu'il ne remplissait pas | **422 px dont 115 vides** — 27 % |
| Trois échelles d'état concurrentes sur la même page | déclarée 1–5 · inférée 4 bandes · calculée 0–100 |
| Document | **2 463 px** = 2,9 écrans |

---

## 2. Ce qui est construit

### La chaîne causale

```
▎CE QUE DISENT TES SÉANCES     ← rail bleu, origine système
▎ Core / Abdos   ▮▮▮ disponible
▎ Mollets        ▮▮▮ disponible
┆ DONC                          ← rail pointillé
▎LA SÉANCE
▎ LISS cardio + abdos
▎ 12 séries · Core / Abdos
▎ Pas de cardio récent → …      ← phrase du moteur, bleue
┌─────────────────────────────┐
│ DÉMARRER                 →  │  ← ambre, 56 px, pleine largeur
└─────────────────────────────┘
──────────────────────────────
▮▮▮ 6   ▮▮ 4   ░ 1              ← bilan des 11 zones
──────────────────────────────
ÉCARTÉ — ET POURQUOI        2 ⌄
```

**Le rail reste bleu jusqu'à la prescription incluse** et ne cède à l'ambre
qu'au bouton. La séance proposée est produite par le moteur : c'est de
l'origine système, pas une action de l'utilisateur. La bascule chromatique
marque exactement ce passage (`Sx_UIV3_04 §1bis C2`).

### Ce que le contexte expose — trois `UI_DATA_GAP` refermés

`_home_causal_context()` fait **une** lecture de `build_zone_recovery` et en
dérive trois sorties :

| Sortie | Gap | Nature |
|---|---|---|
| `zones` | — | les zones que la séance vise |
| `tally` | `G3` | les 11 zones comptées par bande |
| `alternatives` | `G1` + `G2` | les options écartées **et la zone qui l'explique** |

**Aucune décision métier n'est créée.** Les alternatives et leur score sont
produits par `recommend_next_session` et transmis ; la zone limitante est un
**tri** des bandes existantes ; le comptage est une **somme**.
`recommendation.py` et `zone_recovery.py` ne sont pas touchés.

### Le différenciateur

« Écarté — et pourquoi » nomme la **zone limitante** de chaque option non
retenue : « Pull B → Dos épaisseur non mesuré ». Aucun des cinq produits
comparés ne montre l'inverse d'une recommandation. Le moteur d'AUREN le
calcule déjà ; l'affichage le jetait.

Quand toutes les zones d'une alternative sont disponibles, le motif devient le
**score** — afficher une zone « disponible » à côté du mot « écarté »
n'expliquerait rien.

---

## 3. Résultats mesurés

| Largeur | Document avant | après | écart | CTA avant | après |
|---|---:|---:|---:|---:|---:|
| 360 × 800 | 2 480 | **1 822** | −27 % | 359 | 359 |
| 390 × 844 | 2 463 | **1 804** | −27 % | 381 | **359** |
| 430 × 932 | 2 411 | **1 716** | −29 % | 367 | 361 |

| | Avant | Après |
|---|---:|---:|
| Cause visible sans tap | **0 px** | **170 px** |
| Vide réservé dans le hero | **115 px** | **0** |
| Débordement horizontal | 0 | **0** |
| Scroll avant l'action dominante | 0 | **0** |

Les quatre éléments signalés en débordement sont des `.sr-only` —
`clip: rect(0,0,0,0)`, volontairement hors écran. **Vérifié dans la feuille de
style, pas supposé.**

---

## 4. Relecture du relevé, décision par décision (`CLAUDE.md §5.2`)

| Décision | Verdict |
|---|---|
| **D2** `AMEND` | **respectée** — origine et raison toujours dites, hors de tout pli |
| **D6** `PROMOTE` | **respectée** — la récupération structure l'écran |
| **Q5** `ENFORCE` | **respectée** — le hero cesse d'être une carte ; seul le CTA en est une |
| **D8** `ENFORCE` | **respectée** — l'analytique quitte l'accueil |
| **Q2** `SUPERSEDE` | **respectée** — zones causales + bilan, pas 11 barres |
| **D9** | **respectée** — aucune séance N+2 annoncée |
| **D1** | **respectée** — un seul rang 1 (le CTA) ; les zones sont des étiquettes, ni cadre ni cible |
| **D3** / `Sx_UIV3_04 §3` | **respectée** — ambre = action seule, bleu = origine système, bandes en luminance neutre |
| `Sx_UIV3_00 §5` | **respectée** — aucun pourcentage ; une garde le pinne |
| `CLAUDE.md §5.3` | **respectée** — voir §5 |
| `Sx_UIV3_04 §8` | **respectée** — `:active` sur le CommandDock |

**Aucune décision violée.**

---

## 5. Jamais une soustraction seule

| Retiré | Remplacé par |
|---|---|
| `<details class="reco-origin">` | la cause rendue **sans interaction** |
| KPI « Disponibilité » | → Progression, toujours calculé et visible |
| Sparkline, « séances cette sem. » | → Progression, lien à un tap |
| Formulaire « État du jour » déplié (629 px) | replié, champs intacts, POST identique |
| Filet ambre horizontal du hero | le rail causal vertical — il relie au lieu de souligner |
| Eyebrow « Aujourd'hui » (branche reco) | « Ce que disent tes séances » |
| Carte du hero | Q5 : le hero n'est pas actionnable, c'est la page |

**Une chose a failli partir seule.** Les **raisons secondaires** du moteur, que
l'ancien `<details>` portait, avaient disparu de mon premier jet.
`test_the_secondary_reasons_were_kept_not_dropped` l'a signalé. Elles sont
rétablies dans la chaîne causale — même niveau, même filet bleu.

---

## 6. Migration de gardes — 18 tests, tier déclaré

| Module | Tier | Traitement |
|---|---|---|
| `test_home_reco_origin` (11) | **T5 → T2/T3** | **réécrit**, pas supprimé. La garde centrale devient « la cause est rendue sans aucune interaction », vérifiée en comptant les `<details>` ouverts entre le hero et la cause — la seule formulation qui attrape la régression |
| `test_uiv3_cockpit_ladder::no_new_token_consumer` (1) | **T5 — expirée** | voir ci-dessous |
| `test_home_decision_hero::eyebrow_today` (1) | T4 | l'eyebrow survit pour la séance active |
| `test_home_decision_hero::kpi_and_progress_link` (1) | T4 | protège désormais que l'analyse reste **à un tap** |
| `test_ui06_home_dedup` (1) | T4 | **se durcit** : interdisait deux KPI, les interdit tous |
| `test_board_kpis` (1) | T4 | idem |
| `test_sb_10_polish` (2) | T5 | l'inverse exact, délibérément |

### Ma propre garde B0 a expiré, et c'est le cas le plus instructif

`test_no_new_token_consumer_outside_the_approved_scope` exigeait **zéro
consommateur** de `--t-blue-*` et `--t-unknown`. C'était la preuve que `B0`
déclarait la palette **sans commencer le redesign**.

Cette phase les consomme légitimement. La garde tombe donc — **le jour où la
spec la remplace, pas avant**, exactement la règle T5 du registre.

Elle est remplacée par un invariant qui, lui, ne périme pas : **l'ambre ne
marque jamais un état de récupération**. L'ambre est l'action de
l'utilisateur ; une bande est un fait le concernant. Les confondre ferait lire
« à toi de jouer » là où le produit dit « voilà où tu en es », et rouvrirait la
porte au feu tricolore que `Sx_UIV3_00 §4` interdit.

### Gardes neuves

« la cause est rendue sans interaction » · « le bilan totalise exactement 11,
confronté à `canonical_zone_codes()` » · « aucun pourcentage de récupération » ·
« `unknown` n'est jamais rendu rempli » · « le CommandDock fait 56 px et
occupe sa colonne » · « chaque option écartée porte son motif ».

---

## 7. Trois défauts trouvés au rendu, invisibles au code

**Le CTA mesurait 139 px.** `display: inline-flex` le réduisait à la largeur de
son texte, et sa taille dépendait donc du libellé. Pire, `border` n'était
jamais remis à zéro : sur le `<button>` de la branche recommandée, le
navigateur appliquait son `2px outset`. Personne ne l'avait vu parce que la
capture de référence montrait l'état « séance active », servi par un `<a>`.

**Le rail était interrompu** — 10 px de vide au-dessus de la jonction, 7 px en
dessous. Un rail discontinu ne relie rien : il redevient trois accents
décoratifs empilés.

**Le harnais mesurait la page de connexion sans broncher.** Le serveur applique
un limiteur de tentatives (`429`, `retry-after`) ; à la troisième largeur le
login échouait, et le harnais rapportait « hero absent, document 602 px »
comme si c'était le produit. Corrigé deux fois : une assertion qui refuse de
mesurer autre chose que la Home, et **une seule authentification** réutilisée.

---

## 8. Accessibilité

- **Le glyphe de bande n'est nommé que lorsqu'il porte seul le sens.** Dans une
  ligne de zone, le libellé est déjà affiché : annoncer la bande ferait
  entendre l'état **deux fois**, donc elle est `aria-hidden`. Dans le bilan,
  où seul un compte l'accompagne, un nom accessible est servi par du texte hors
  écran — pas par `role="img"` sur un `<span>` de présentation.
- CommandDock **56 px**, `:active`, `:focus-visible`.
- `rejected__summary` **44 px**.
- Aucun état par la couleur seule.
- Rail décoratif, `aria-hidden` de fait (pseudo-éléments).
- **Aucun JS.** Tout est `<form>` et `<details>` natifs.

---

## 9. Vérifications locales

| Check | Résultat |
|---|---|
| `check_scope` | `ISOLATED` — **remonté d'un cran** : `pages.py` porte les routes, `home.css` est partagé |
| ruff | **propre** |
| `check_ruff_budget` | 281 ≤ 548 |
| `check_spec_protocol` | **OK** |
| Broad sweep Accueil | **787 passés, 0 échec** |
| Rendu, 3 largeurs | 0 débordement · 0 scroll avant l'action |

---

## Verdict

**L'Accueil répond enfin à la question qu'il pose.** État → donc → séance →
action, lisible d'un bloc, sans un tap.

Le plus notable est que **rien n'a dû être calculé**. Les alternatives, leur
score, les bandes des onze zones : tout existait dans le moteur et
l'affichage le jetait. La valeur de cette phase tient dans trois liaisons et
une suppression, pas dans un moteur nouveau.

Et le défaut le plus coûteux du lot n'était pas dans le produit : c'était un
**harnais qui mesurait la page de connexion en croyant mesurer la Home**. Une
mesure silencieusement fausse est pire qu'une mesure absente.

---

## Annexe de clôture (post-merge)

| | |
|---|---|
| Base | `1e761b2` |
| PR | **#131 MERGED** — 6 commits |
| Merge | **`f10af0a`** via `--merge --match-head-commit f1ce7f7` — sans squash, sans `--admin`, sans force |
| CI PR | **8/8 pass** |
| CI canonique | **6/6 success** sur `f10af0a` |
| Sonar | gate **`OK`** — 94,4 % de couverture du code neuf, 0 bug, 0 smell, 0 duplication |
| Threads de revue | **0** |
| UI | **validée par l'opérateur** avant merge (`CLAUDE.md §5.1`) |

### Quatre CI rouges, quatre causes distinctes — aucune dans le produit

| # | Cause | Traitement |
|---|---|---|
| 1 | `test_a8_zone_recovery_reaches_no_template` lisait ses **commentaires Jinja** | garde corrigée, plantation vérifiée |
| 2 | Sonar `S3776` — complexité cognitive **16 pour 15** | `_rejected_alternatives` extrait, sortie identique vérifiée |
| 3 | Sonar `S6466` — « IndexError » sur un **slice** | **`FALSE POSITIVE`** adjugé avec preuve empirique |
| 4 | `test_no_raw_binary_source_in_git_docs` sur les captures de référence | exception étroite **et plafonnée**, 4 plantations détectées |

**Deux annulations d'infra** en plus, sur le même job `lint`, toutes deux à
5 min 20 : `timeout-minutes: 5` et un cache de dépendances froid. Le re-run sur
le **même commit** passe en 1 min 16 — même code, durée différente. Traitées
comme `CLAUDE.md §2` l'exige : **re-run sans nouveau commit**, jamais une
cascade de correctifs.

> **À corriger hors périmètre** : le budget de 5 minutes du job `lint` est trop
> serré à cache froid. C'est du tier `ci_infra`, donc une tranche à part —
> et la CI réelle en est la seule preuve valable.

### Un défaut trouvé en écrivant la référence visuelle

En ajoutant les captures au blueprint, j'ai ouvert `/progress` **pour la
première fois** et découvert que la Disponibilité n'y est pas : elle vit sur
`/dashboard`. J'avais donc déplacé un KPI « vers Progression » sans jamais
regarder la destination, et le lien de l'accueil promettait ce qu'elle ne
tient pas.

Corrigé. Et la correction honnête du libellé a fait tomber **trois gardes qui
passaient parce que le mot figurait dans un lien**.

### Ce que cette phase débloque

L'accueil est propre — et c'est précisément ce qui rend les **incohérences des
surfaces périphériques visibles**. `/progress` mesure 2 735 px et n'a jamais
été spécifiée sous UIV3.

L'architecture cible en quatre instruments est désormais tranchée
(`AUREN_UI_BLUEPRINT §2.5`), et son traitement est **délibérément différé** à
une phase 4 : la Séance reste la surface souveraine avec le plus gros déficit
mesuré.
