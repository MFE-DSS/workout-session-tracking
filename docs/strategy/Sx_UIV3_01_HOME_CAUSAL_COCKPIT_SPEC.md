# `Sx_UIV3_01` — Home · Causal Cockpit

**Statut : `APPROVED — OPERATOR`** (2026-08-18, avec les amendements A/B/C de `Sx_UIV3_04 §1bis`)
**Dépend de** `Sx_UIV3_00` (Foundation Contract), qui prévaut en cas de conflit.
**Portée : UI/UX uniquement.** Aucun calcul, aucune donnée nouvelle.

**Direction retenue par l'opérateur** : `CAUSAL COCKPIT`, concept C du Design
Lab Home × Recovery (67/80, le mieux noté).

---

## 1. La question à laquelle cet écran répond

> **« Qu'est-ce que je fais maintenant, et pourquoi ? »** — en moins de deux
> secondes, sans interaction.

La chaîne à rendre visible est :

```
ÉTAT CORPOREL  →  DONC  →  SÉANCE  →  ACTION
```

et **non** : carte recommandation + carte récupération + carte stats + texte.

**La récupération n'est pas un widget voisin de la recommandation. Elle est
une partie de son explication.** C'est la promotion de D6 en règle de
structure, décidée dans la Contract Migration ci-dessous.

---

## 2. Contract migration

| Décision | Action | Ancien | Nouveau |
|---|---|---|---|
| **D2** | `AMEND` | origine + raison **derrière un `<details>`** | origine système + raison **restent obligatoires**, mais la cause nécessaire à la décision est **immédiatement visible**. `<details>` redevient un outil de disclosure pour du **secondaire** (alternatives, historique). |
| **D6** | `PROMOTE TO STRUCTURAL RULE` | la récupération explique la reco, dans un pli | la récupération **est la cause visuelle** de la recommandation et structure l'écran |
| **Q5** | `ENFORCE` | trois rangs décidés, non appliqués | la surface encadrée n'est utilisée que si le conteneur apporte une **fonction** ; pas de carte dans carte ; le hero cesse d'être une carte |
| **D8** | `ENFORCE` | Progression décidée, analytics restées sur l'accueil | l'analytique exhaustive **quitte** l'accueil. Home = décision. Progression = analyse. |
| **Q2** | `SUPERSEDE` | 11 barres de récupération = ancre obligatoire | **nouveau contrat** : zones causales pertinentes au niveau 1 · bilan compact · état complet au niveau 2 |

### Gardes rendues caduques par cette migration

Aucune garde ne doit rester verte en protégeant un choix abandonné.

| Garde | Tier | Sort |
|---|---|---|
| `test_home_reco_origin` — pinne le `<details class="reco-origin">` | **T5** | **à remplacer** par une garde « la cause est rendue sans interaction » |
| `test_home_decision_hero::test_status_label_present_only_for_an_active_session` | T3 | conservée, inchangée |
| `test_home_decision_hero::TestHomeCss::test_css_cta_meets_tap_target` | **T2** | conservée, **renforcée** à la mesure navigateur |
| `test_home_design_decisions::test_no_surface_claims_the_recommendation_comes_from_ai` | **T1** | **intouchable** |
| `test_home_design_decisions::test_the_record_states_it_is_not_built` | **T5** | caduque dès que D1–D5 sont construites ; à retourner, pas à supprimer |
| `test_ui06_home_dedup` | T4 | à réévaluer : la dédup change de cible |

---

## 3. Structure — ordre vertical figé

```
┌─ barre d'application ───────────────────────── 86 px
│
│  ▎CE QUE DISENT TES SÉANCES        ← L2 · rail bleu
│  ▎ Core / Abdos    ▮▮▮    prête
│  ▎ Mollets         ▮▮▮    prête
│  ┆
│  ┆ DONC                            ← L2 · rail pointillé bleu
│  ▎
│  ▎LA SÉANCE                        ← L1 · rail ambre
│  ▎ LISS cardio + abdos
│  ▎ 12 séries · 35 min
│  ▎ Pas de cardio récent → …        ← bleu, origine système
│  ▎┌───────────────────────────┐
│  ▎│ DÉMARRER              →   │    ← L1 · action dominante
│  ▎└───────────────────────────┘
│  ──────────────────────────────
│  ▮▮▮ 6  ▮▮ 3  ▮ 1  ░ 1            ← L2 · bilan 11 zones
│  ──────────────────────────────
│  ÉCARTÉ — ET POURQUOI              ← L3
│  Pull B              Dos ép. n.m.
│  Rattrapage dos      Dos ép. n.m.
│       Choisir quand même ⌄
└──────────────────────────────────── 844
```

**Le rail est le mécanisme propre à AUREN.** Un filet vertical continu part
des zones, traverse un segment pointillé marqué `DONC`, et se prolonge en
**ambre** derrière la séance et son bouton. La causalité devient une
**continuité graphique**. Aucun des cinq produits comparés (Gravl, Fitbod,
Alpha Progression, Boostcamp, Hevy) ne dessine ce lien — ils juxtaposent.

Implémentation visée : pseudo-éléments CSS. **Aucun JS.**

---

## 4. Above-the-fold budget · 390 × 844

Mesuré sur le prototype `/tmp/auren-ui-lab/home/c-causal-cockpit.html`.

| Bloc | Hauteur | Niveau |
|---|---:|---|
| Barre d'application | 86 px | — |
| Cause — 2 zones + rail | 132 px | L2 |
| Jonction « DONC » | 38 px | L2 |
| Décision + CTA | 147 px | **L1** |
| Bilan 11 zones | 60 px | L2 |
| Écarté — et pourquoi | 185 px | L3 |
| **Libre avant 844** | **196 px** | — |

**Bas du CTA dominant : 403 px.** Scroll requis avant l'action principale :
**0 px**, aux trois largeurs.

Comparaison avec l'existant, même viewport :

| | Actuel | Cible |
|---|---:|---:|
| Hauteur du hero | 422 px | — (plus de hero encadré) |
| px vides réservés | **115 px** | **0** |
| Cause visible sans tap | **0 px** | **170 px** |
| Bas du CTA | 436 px | 403 px |
| Document total | 2 441 px (2,9 écrans) | ≤ 1 200 px cible |

---

## 5. Encodage de la récupération

Conforme à `Sx_UIV3_00 §5`, sans dérogation.

- **3 / 2 / 1 segments** pour disponible / partielle / chargée.
- **`unknown`** : contour pointillé + hachure diagonale, **jamais rempli**,
  jamais coloré, libellé « non mesurée ».
- **Aucun pourcentage.** L'`estimate` 0–1 ne quitte jamais le service.
- **Libellé toujours présent** à côté du glyphe (no-color-only, `§7`).

### Zones affichées au niveau 1

**Uniquement les zones que la séance recommandée vise** (`reco.top.primary_zones`),
au plus **3**. Au-delà de 3, la spec impose de replier sur le bilan : quatre
lignes de zones repoussent le CTA sous 500 px et le budget de densité échoue.

### Bilan compact — les 11 zones en une ligne

```
▮▮▮ 6    ▮▮ 3    ▮ 1    ░ 1
```

Comptage **dérivé** de `build_zone_recovery`, jamais écrit à la main. Toute
bande à zéro est omise. Total obligatoirement égal à 11 — une garde le pinne.

> Cette ligne referme le trou du concept C, qui ne montrait que les zones
> visées. Elle coûte 60 px là où onze barres en coûtaient 150.

### Niveau 2 — l'état complet

La ligne de bilan est **tapable** et ouvre la matrice 11 cellules du concept B
(`BODY_LEDGER_PAGE_01`, tranche B-queue). **Elle ne vit pas sur l'accueil.**

---

## 6. États de la Home

| État | Cause | Décision | CTA | Écarté |
|---|---|---|---|---|
| **reco normale** | 2–3 zones visées + bandes | nom + volume + durée | `DÉMARRER` | 2 alternatives + motif |
| **séance active** | **masquée** — la cause a déjà été acceptée | nom de la séance en cours + « depuis N min » | `REPRENDRE` | « Démarrer une autre séance » (L3) |
| **zones visées `unknown`** | zones affichées avec le glyphe hachuré + « non mesurée » | inchangée | `DÉMARRER` | inchangé |
| **toutes zones `unknown`** (nouvel utilisateur) | une seule ligne : « Pas encore assez de séances pour estimer ton état. » | inchangée | `DÉMARRER` | masqué |
| **aucune reco** | masquée | « Prêt à t'entraîner ? » | `DÉMARRER UNE SÉANCE` → launcher | masqué |

**Règle d'honnêteté.** L'état « toutes zones unknown » **ne fabrique pas** une
cause. Il dit qu'il n'en a pas. C'est la même exigence que l'interdit
« Recommandé IA ».

---

## 7. Éléments supprimés ou déplacés

| Élément | Sort | Motif |
|---|---|---|
| `<details class="reco-origin">` | **supprimé** | D2 amendée : la cause ne se replie plus |
| Carte « ÉTAT D'ENTRAÎNEMENT » (prose + confiance) | **supprimée de l'accueil** | doublon de la cause, en prose, sous le pli, dans un second vocabulaire |
| KPI « DISPONIBILITÉ » 0–100 | **déplacé vers Progression** | quatrième échelle d'état ; exprime en % ce que `zone_recovery` refuse d'exprimer ainsi |
| Formulaire « État du jour » déplié | **replié** (Q3-A) | 629 px de saisie devant la décision |
| Sparkline + « séances cette sem. » | **déplacé vers Progression** | D8 |
| Tuiles Historique / Progression / Programmes / Science | **conservées**, sous le pli | navigation, L3 |

**§5.3 — jamais une soustraction seule.** Chacune de ces suppressions part
dans la **même tranche** que son remplacement : la cause visible remplace le
`<details>` et la carte prose ; le bilan 11 zones remplace le KPI
« Disponibilité » ; la ligne compacte remplace le formulaire déplié.

---

## 8. Alternatives — « écarté, et pourquoi »

**Le différenciateur produit.** Aucun des cinq produits comparés ne montre ce
qui a été **écarté**. Le moteur d'AUREN le calcule déjà et l'affichage le jette.

Format, une ligne par alternative :

```
Pull B — Dos épaisseur + Biceps          Dos épaisseur non mesuré
Rattrapage dos largeur                   Dos épaisseur non mesuré
```

**Zone limitante** = la zone de l'alternative dont la bande est la pire, dans
l'ordre `unknown` → `fatigued` → `partial` → `available`. Si toutes les zones
sont disponibles, le motif est le **score** : « score 65 < 78 ».

> ⚠️ **`UI_DATA_GAP` — voir §12.** La zone limitante est **dérivable** des
> bandes déjà calculées, mais le contexte de la Home n'expose ni les
> alternatives ni leur score aujourd'hui.

Cette section est **L3** et repliable — ce n'est pas la cause de la décision,
c'est sa justification étendue.

---

## 9. Comportement mobile

| Largeur | Comportement |
|---|---|
| **360 × 800** | identique ; les libellés de bande passent en forme courte (« prête », « partielle », « chargée », « n.m. ») |
| **390 × 844** | référence |
| **430 × 932** | identique ; l'espace gagné va à l'espacement, **jamais** à un bloc supplémentaire |

Aucun débordement horizontal à aucune largeur. La ligne de bilan ne défile
jamais : si elle ne tient pas, les bandes à zéro sont omises en premier.

---

## 10. Accessibilité

- Chaque groupe de segments porte `role="img"` + `aria-label` avec le libellé
  complet de la bande. Un span vide sans rôle n'est annoncé par aucun lecteur.
- Le rail est **décoratif** : pseudo-éléments, invisible aux technologies
  d'assistance. La causalité est portée en texte par « DONC » et par les
  intitulés de section.
- CTA ≥ 56 px, mesuré au navigateur.
- Aucun état distingué par la couleur seule.
- `prefers-reduced-motion` : aucune animation introduite.

---

## 11. No-JS

L'écran entier fonctionne sans JavaScript. `DÉMARRER` est un `<form method="post">`
vers `/sessions` — contrat inchangé. Les alternatives sont un `<details>` natif.

---

## 12. `UI_DATA_GAP`

| # | Gap | Existe déjà ? | Pass-through possible ? |
|---|---|---|---|
| **G1** | `reco.alternatives` (nom, slug, score, `primary_zones`) n'est pas passé au template de la Home | **oui** — `recommend_next_session()` retourne `alternatives` | **oui** — pass-through de présentation pur : la valeur existe, aucun score recalculé, aucune décision métier créée, contrat source identique |
| **G2** | La zone limitante d'une alternative | **non**, mais **dérivable** des bandes existantes par un tri | **oui**, si le tri vit dans la **couche de présentation** et ne redéfinit aucune sémantique de bande |
| **G3** | Le comptage 11 zones par bande | **non**, dérivable de `build_zone_recovery` | **oui**, même condition que G2 |

**Aucun de ces trois gaps ne justifie de toucher un service métier.** Si un
build futur estime le contraire, il **bloque** et remonte la décision.

---

## 13. Blockers — résolus le 2026-08-18

- **`BLOCKER-1` — RÉSOLU : OUI.** « Disponibilité » **quitte l'accueil** et
  rejoint Progression / Analyse. Motif opérateur : la métrique introduit une
  quatrième lecture concurrente de l'état ; la Home explique **une** décision,
  elle ne fournit pas trois modèles de readiness.
- **`BLOCKER-2` — RÉSOLU : OUI.** Q2 est officiellement `SUPERSEDE`. Les
  « 11 barres comme ancre Home » sont remplacées par **zones causales + tally
  compact**. Le relevé complet des 11 zones reste une **surface N2 future**,
  jamais au-dessus du CTA. Motif : AUREN explique **ce qui a déterminé la
  séance** plutôt que d'afficher tout ce qu'il sait — c'est la force du Causal
  Cockpit contre la heatmap conventionnelle.

### Reste ouvert

- Le nombre exact de zones causales affichées (2 ou 3), à valider sur rendu
  réel — porte de glanceability (`Sx_UIV3_00A §10`).

## 14. Amendement `00A`

Cette spec est **postérieure** à `Sx_UIV3_00A` dans la queue et doit consommer
sa grammaire :

- le rail causal devient la primitive **`CausalRail`** (`00A §3`) ;
- les segments deviennent **`RecoveryBand`**, le bilan **`ZoneTally`**, la
  phrase du moteur **`SystemOrigin`**, le CTA **`CommandDock`** ;
- les surfaces se posent sur l'escalier corrigé de `00A §1`, **après B0** ;
- `SystemOrigin` porte le filet bleu 2 px de `00A §2` ;
- la section « écarté — et pourquoi » est éligible au **popover** (`00A §7`)
  puisqu'elle est L3 — sous réserve du repli en flux obligatoire.

---

## Non-goals

- Aucun changement du moteur de recommandation ni de `zone_recovery`. La Home
  n'affiche que ce qui est déjà produit.
- Aucun pourcentage de récupération : l'`estimate` 0–1 ne quitte pas le service.
- Aucune BodyMap sur l'accueil tant que 7 zones sur 11 n'ont pas de plaque
  approuvée — un corps à moitié gris mentirait sur ce que le produit sait.
- Aucune matrice 11 cellules au-dessus du CTA : elle est une surface de
  second niveau (`BODY_LEDGER_PAGE_01`).
- Aucune anticipation au-delà de la séance proposée (D9).
- Aucune revendication d'IA.
