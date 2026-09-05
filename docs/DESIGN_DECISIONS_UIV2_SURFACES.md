# Registre des décisions — surfaces UI V2 (arbitrage 2026-08-18)

**Statut : `DECIDED`** · décisions **tranchées par l'opérateur** sur exposition
visuelle rendue, conformément à `CLAUDE.md §5.1`.

Ce relevé couvre les **trois surfaces** — connexion, accueil, séance — et les
**motifs transverses**. Il complète `DESIGN_DECISIONS_HOME_UIV2.md` (D1–D9),
qui reste en vigueur pour l'accueil.

> **Comment ces décisions ont été prises.** Les trois pages ont été rendues à
> 390 px sur un serveur local, capturées, et soumises à l'opérateur avec les
> options et leurs coûts. Il a tranché question par question. C'est la
> procédure que `CLAUDE.md §5.1` rend désormais obligatoire — elle existe
> parce que la tranche précédente ne l'avait pas suivie.

---

## Q1 — La connexion porte l'identité du produit ✅ **B, version sobre**

Pas une page d'atterrissage marketing. **Une porte premium, terminale,
silencieuse, avec une phrase forte.** C'est la seule surface qu'un visiteur non
connecté voit ; elle doit dire ce qu'est Auren.

```
AUREN
Train with biomechanical intent.
```

**Structure retenue** : marque · une phrase · formulaire · liens secondaires
**hiérarchisés** (aujourd'hui trois liens de poids égal, donc aucun chemin
principal).

**Supprimer « ← Retour »** si le visiteur n'a pas de page précédente réelle.

### Accroche — **en français**, tranché le 2026-08-19

```
AUREN
S'entraîner avec intention biomécanique.
```

`Train with biomechanical intent.` au milieu d'une interface entièrement
française **paraîtrait un vestige de maquette anglophone**, pas une signature
internationale volontaire.

La traduction littérale « Entraîne-toi avec une intention biomécanique » est
trop lourde. La forme retenue est **légèrement inhabituelle en français, et
c'est délibéré** : assez singulière pour devenir une signature, froide,
précise, cohérente avec le positionnement déjà écrit — AUREN est un
**instrument biomécanique**, pas une application de bien-être.

*Alternative écartée* : « La progression guidée par la biomécanique » — plus
naturelle, mais elle perd l'idée d'**intention**, qui est le mot porteur.

---

## Q2 — L'ancre visuelle de l'accueil ✅ **A, barres de récupération par zone**

**Immédiatement**, sans attendre la géométrie.

Motifs opérateur, dans l'ordre : `build_zone_recovery` **calcule déjà** ces
bandes et rien ne les affiche · elles **expliquent la recommandation du jour** ·
elles **ne dépendent pas** des plaques anatomiques · elles appliquent **D6** —
le hero dit « Push A », les barres disent *pourquoi*.

**Le corps anatomique reste la destination premium, pas l'ancre.** Avec 7 zones
sur 11 sans géométrie, il **mentirait visuellement**.

**La bande hebdomadaire** (D7) est utile, mais elle explique la **régularité**,
pas la recommandation immédiate. Elle vient après.

---

## Q3 — « État du jour » ✅ **A, replié, ouvert d'un geste**

Le formulaire **ne doit plus dominer l'accueil**. Il devient une ligne compacte :

```
État du jour · prêt · sommeil moyen · fatigue basse      Modifier
État du jour · non renseigné                             Saisir
```

Le formulaire complet se déploie au toucher. **Trente secondes de saisie ne
sont pas l'objet principal d'un cockpit.**

### ⚠ AMENDEMENT — la feature est **décommissionnée**, supersède le 2026-09-06

Le repli ci-dessus était un **compromis de placement** sur une fonctionnalité
dont l'opérateur a depuis tranché qu'elle ne devait pas exister sous cette
forme. La question n'était pas *où mettre le formulaire* mais *pourquoi
demander à quelqu'un de noter son état de 1 à 5*.

Arbitrage, dans les termes de l'opérateur :

> « L'état du jour va être décommissionné dans la façon dont il est
> aujourd'hui. La personne ne va pas rentrer des chiffres de un à cinq. Ça va
> être déterminé par ses performances sportives et par ce qui est rempli à la
> fin de ses séances : il dit qu'il est focalisé, fatigué, distrait. Cette
> feature qu'on a aujourd'hui à l'accueil, elle est complètement
> décommissionnée. »

**Ce qui est tranché :**

1. la **saisie manuelle 1–5 disparaît** — ce n'est pas un déplacement vers une
   autre surface, c'est un retrait ;
2. la lecture d'état devient **dérivée** : performances sportives + déclarations
   de **fin de séance** ;
3. la surface de saisie **existe déjà** — c'est le bilan de fin de séance, où
   l'utilisateur répond « Focalisé · Correct · Distrait » et « En forme · Moyen
   · Fatigué ».

**Ce qui rend le retrait possible sans appauvrir le produit** (`CLAUDE.md §5.3`
— jamais une soustraction seule) : la matière première est **déjà collectée et
désormais entièrement libellée**. `DECLARED_STATE_LABELS` traduisait l'énergie
depuis `Sb_SESSION_REVIEW_SIGNAL_01` ; `DECLARED_CONCENTRATION_LABELS` a été
ajouté par `Sb_UI_SESSION_DONE_01` (PR #207), qui a fermé la dernière fuite de
clé de programme à l'écran. Les deux questions du bilan sont donc citables.

**Ce qui n'est PAS tranché, et bloque l'implémentation** — la **règle de
dérivation** elle-même : sur combien de séances, avec quelle pondération entre
performance et déclaration, et ce que le produit affiche quand il n'y a pas
encore de séance. Ce sont des décisions produit. Tant qu'elles ne sont pas
prises, retirer la saisie livrerait un vide — précisément ce que `§5.3`
interdit.

**État : décision prise, implémentation en attente d'une règle.**

---

## Q4 — La page de séance ✅ **B, la ligne de série devient un instrument**

Pas « réparer les colonnes ». **Régler le rognage par design, pas par largeur.**

| Avant | Après |
|---|---|
| `Série #1 actif` | `S1` + point d'état |
| `Échauf. #1` | `É1` |
| `Enregistrer et passer à E2` | `Valider · E2` |
| `3×12-20 RP · première fois` | `3×12-20 RP` |

**Les valeurs deviennent l'objet, le texte recule.** L'utilisateur vient
enregistrer une action, pas lire une carte.

**C n'est pas retenu maintenant** (« un exercice à la fois » — trop gros), mais
**B doit être construit pour pouvoir y mener**.

→ Livré par `D5_SESSION_INSTRUMENT_ROWS_01`.

### ⚠ AMENDEMENT — `É1` / `S1` sur les LIGNES, superséde le 2026-08-29

**Autorité** : note de dogfood de séance de l'opérateur, point `DF-03` — « `É`/`S`
sont des **codes techniques**, pas la sémantique visuelle d'AUREN ». Puis l'ordre
`GO DF-C — SESSION VISUAL SEMANTICS & TARGET CLOSURE`.

Cet amendement est **explicite et daté** : `CLAUDE.md §4` interdit d'amender
silencieusement une spec versionnée, et de passer outre un conflit de spec. Le
conflit est réel — la table ci-dessus **décidait** `É1` et `S1`.

**Ce qui est superséde** : la colonne « Après » pour les deux premières lignes,
**sur les lignes de série uniquement**.

| Ligne | Q4 (2026-08) | `DF-C` (2026-08-29) |
|---|---|---|
| échauffement | `É1` | microglyphe `╱` + `1` |
| série de travail | `S1` | microglyphe `▬` + `1` |

**Ce qui reste entier** — et c'est pourquoi ce n'est pas un revirement :

* « les valeurs deviennent l'objet, le texte recule » est **renforcé** : le code
  à déchiffrer devient une forme perçue, et le nombre — la seule part utile —
  survit inchangé ;
* le **point d'état** (`✓ ● ○`) de Q4 est **conservé tel quel**. Deux
  dimensions, deux porteurs : le glyphe dit le TYPE, le point dit l'ÉTAT ;
* la 3ᵉ et la 4ᵉ ligne du tableau ne sont **pas** touchées.

**Ce qui reste ouvert** : le libellé de la commande dominante dit encore
`VALIDER É1` / `VALIDER S1`. Plus rien à l'écran ne porte ce nom. C'est un
arbitrage d'écriture soumis à l'opérateur, **non tranché par l'agent**.

---

## Q5 — Les surfaces ✅ **A, trois rangs**

La carte bordée **cesse d'être le conteneur universel**. Une carte qui entoure
tout n'entoure plus rien.

| Rang | Traitement | Exemples |
|---|---|---|
| **1 — actionnable** | carte bordée, fond plus présent | séance recommandée, exercice actif, formulaire ouvert |
| **2 — informatif** | simple filet, séparateur, module compact | barres de récupération, continuité, progression courte |
| **3 — ambiant** | **aucun conteneur** — typographie et espace seuls | contexte, micro-copie, état vide |

Même principe que les trois rangs de **contrôle** de D1, appliqué aux
**surfaces**. La carte redevient un **signal**, pas un décor.

---

## Q6 — L'échelle typographique ✅ **E3 — 32 / 22 / 15 / 12**

Quatre rangs, quatre seulement. Ils portent les noms que le socle visuel leur
donne déjà (`AUREN_VISUAL_BACKBONE §3.2`) ; ce qui manquait était **leur
valeur**.

| Rang | Taille | Ce qu'il porte |
|---|---|---|
| **DISPLAY** | **32 px** | le relevé souverain, le titre d'écran — *un seul par écran* |
| **SECTION** | **22 px** | les titres de bloc |
| **BODY** | **15 px** | le texte courant |
| **META** | **12 px** | provenance, étiquettes, légendes |

**Pourquoi c'était urgent de l'écrire.** Cette échelle gouvernait déjà
l'accueil, le récap de séance et les onze surfaces de `Sb_UI_SECTION_RANK_01`
— sans exister dans un seul fichier du dépôt. Une décision appliquée trois fois
et écrite zéro fois est une décision que la session suivante ne connaît pas.

**Le défaut qu'elle ferme.** Le socle documentait, sans pouvoir le corriger :
« body 14 px, section-header 13 px … **sur 101 usages** ». Un titre de bloc
plus petit que le texte qu'il introduit ne hiérarchise rien.

**Règle d'application** : un rang se propage **par classe, jamais par écran**.
Corriger la surface où l'on a trébuché en laissant ses dix sœurs est le mode
d'échec relevé sous *une décision appliquée là où c'était commode*.

**Limite connue** : la primitive partagée `.btn` reste à 14 px, et `.card__title`
à 13. Toutes deux sont portées par le **viseur intra-séance**, seul objet validé
au rendu par l'opérateur — elles ne bougent pas sans lui.

---

## Q7 — Un seul aplat ambre par écran ✅ **strict**

L'ambre désigne **l'action souveraine**. Deux aplats ambre sur un écran, c'est
deux commandes souveraines — donc aucune.

**Ce que la règle ne dit pas** : elle porte sur ce qu'un œil voit *à un instant
donné*, pas sur ce qu'un gabarit contient. Un gabarit peut légitimement écrire
plusieurs aplats dans des **branches Jinja mutuellement exclusives**, ou dans
des **tiroirs repliés**.

C'est mesuré : la première garde, écrite en « un par gabarit », a accusé
**cinq surfaces saines** avant d'être remplacée par un **cliquet par gabarit**,
strict dans les deux sens. La garde de vérité reste le **harnais de rendu** —
seul endroit où l'on compte ce qui est réellement visible ensemble.

---

## Q8 — Aucune opacité décorative ✅ **tout passe par un token mesuré**

`opacity: 0.6` sur du texte produit une couleur que **personne n'a mesurée** et
que la palette ne connaît pas. Le contraste réel dépend alors du fond, qui
change d'un rang de surface à l'autre.

Toute atténuation devient un **token de couleur**, avec son ratio documenté sur
le fond réel — exactement la règle `CLAUDE.md §5.4`, étendue à ce qui
n'apparaissait pas comme une couleur.

S'applique **aux écrans touchés**, au fil des tranches — pas en une passe
globale : un remplacement en masse changerait des contrastes sans les mesurer,
ce qui est le défaut qu'on corrige.

---

## Tokens bleus ✅ validés, mesurés

Le bleu signifie **origine système / explication moteur / information
calculée**. Jamais « IA magique » — l'interdit de D2 reste entier.

L'ambre reste **l'action**. Le graphite reste **la structure**. Le bleu devient
**la preuve que ceci vient du système**.

| Token | Valeur | Rôle | Contraste sur `#0F1318` | Seuil |
|---|---|---|---|---|
| `--t-blue-fg` | `#7DD3FC` | texte, chiffre d'origine système | **11,18:1** | ≥ 4,5 ✓ |
| `--t-blue-line` | `#4A7FB5` | filet, bordure, contour | **4,43:1** | ≥ 3,0 ✓ |
| `--t-blue-mid` | `#5FA8D3` | trait de donnée, jauge | **7,13:1** | ≥ 3,0 ✓ |

> **Pourquoi cette table existe.** `Sb_UIV2_HOME_RECO_BADGE_01` a écrit
> `var(--t-accent-blue, #2c5282)` — un token **inexistant** avec un repli tiré
> d'une maquette qui tournait sur un autre fond. Mesurée sur le fond réel, la
> bordure valait **2,34:1**, sous le minimum de 3:1.
>
> **Le bleu n'était pas l'erreur** : il avait été validé. L'erreur était de
> l'employer sans l'inscrire ni le mesurer. `CLAUDE.md §5.4` l'interdit
> désormais : une couleur validée **s'ajoute** à la palette, avec sa mesure.

**Ces tokens ne sont pas encore écrits dans `home.css`** — c'est l'objet de
`UI_TOKENS_BLUE_SYSTEM_01`, qui précède tout usage.

---

## Convergence Gravl → Auren

Gravl gagne aujourd'hui sur quatre dimensions : plan prêt · enregistrement très
rapide · récupération connectée · progression automatique.

**Auren ne doit pas être « Gravl avec une autre peau ».**

> Gravl = *just show up, the plan is ready.*
> Auren = *understand why this is the right session, then execute with precision.*

**Conséquence** : trois objets seulement au-dessus de la ligne de flottaison de
l'accueil.

1. **Recommandé maintenant** — Push A · 21 séries · pourquoi ⓘ
2. **Récupération par zone** — 11 barres visuelles, **pas une phrase**
3. **Continuité sans streak** — rythme hebdomadaire compact

Tout le reste est **replié, déplacé ou supprimé**.

---

## Ordre de livraison

L'ordre suit la **centralité**, pas la facilité (`CLAUDE.md §5.5`).

| # | Tranche | État |
|---|---|---|
| 1 | `D5_SESSION_INSTRUMENT_ROWS_01` — la séance | **en cours** |
| 2 | `UI_TOKENS_BLUE_SYSTEM_01` — les tokens bleus | à faire |
| 3 | `RECOVERY_ZONE_BARS_HOME_01` + `DAY_STATE_COLLAPSE_01` — l'accueil | à faire |
| 4 | `LOGIN_IDENTITY_GATE_01` — la connexion | à faire |
| 5 | D7 — continuité sans streak | à faire |
| 6 | D8 — onglet Progression | à faire |

**Les tokens passent avant l'accueil** : si le bleu sert dans le badge, les
barres ou l'explication système, il doit **exister comme token officiel**, pas
en repli sauvage. C'est la leçon directe de la tranche rejetée.
