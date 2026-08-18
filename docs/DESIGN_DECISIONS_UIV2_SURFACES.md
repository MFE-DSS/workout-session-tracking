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
