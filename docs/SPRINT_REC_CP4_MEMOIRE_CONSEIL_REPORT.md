# REC-CP4 — la mémoire du conseil, et la porte de promotion

**Statut** : livré · **Branche** : `sb/rec-cp4-memoire-conseil` · **Base** : `9bd8350`

---

## 1. Le défaut, énoncé au plus juste

`REC-CP1..CP3` a établi par mesure que le moteur **n'est pas bloqué** :

    conseil SUIVI    → il tourne, six gabarits sur dix décisions
    conseil DÉCLINÉ  → il répète le même conseil indéfiniment

> **AUREN n'a aucune notion d'avoir déjà donné un conseil que l'utilisateur a
> explicitement écarté.**

Ce n'est pas un poids de score. C'est une mémoire d'interaction.

---

## 2. Le modèle de mémoire

### 2.1 Ce qui est persisté

Une table bornée, `recommendation_episodes` — **pas** un journal d'événements
générique, **pas** une préférence utilisateur.

| | |
|---|---|
| identité | `context_fingerprint`, `policy_version`, `decided_at`, `resolved_at` |
| proposition | `proposed_top_slug`, `proposed_alt_slugs` |
| issue | `outcome`, `chosen_slug`, `session_id` |

Une garde épingle **la liste exacte des colonnes** et interdit tout nom
contenant `score`, `penalty`, `preference`, `count`… : la mémoire ne doit
jamais se mettre à tenir un goût durable.

### 2.2 Trois états, un seul persisté

⚠ **La doctrine n'est pas inventée ici.** Elle est reprise mot pour mot de
`plan_adaptation_dismissals` (`UI-CP3.5`), qui avait déjà résolu exactement ce
problème pour les adaptations de plan :

| état | support |
|---|---|
| `UNRESOLVED` | **l'absence de ligne** |
| `RESOLVED` | **la ligne**, avec son issue |
| `SUPERSEDED` | **dérivé** à la lecture, en comparant l'empreinte |

Il n'y a donc **pas** de colonne `lifecycle`. Elle serait la seule source
possible d'un état périmé, et la marquer exigerait d'écrire pendant un `GET`.

### 2.3 Aucun backfill

`creation_source` dit d'où vient une séance **créée** ; il ne dit jamais
**quelle** recommandation était affichée. Fabriquer des épisodes historiques
affirmerait une présentation que personne n'a observée.

---

## 3. La sémantique d'événement

### 3.1 Les gestes qui disent quelque chose

| geste | issue |
|---|---|
| démarrer le conseil | `ACCEPTED_TOP` |
| démarrer une alternative offerte | `ACCEPTED_ALTERNATIVE` |
| démarrer autre chose, conseil affiché | `CHOSE_OTHER` |
| écarter sans rien démarrer | `EXPLICITLY_DISMISSED` |
| **ne rien faire** | **aucune ligne** |

⚠ **`EXPLICITLY_DISMISSED` n'est produit par aucune surface, et c'est une
décision.** Il faudrait un bouton « écarter » — donc une affordance de
rétroaction permanente, que le `§9` exclut tant qu'aucune preuve ne l'exige.
L'issue existe dans le contrat parce que « j'ai fait autre chose » et « j'ai
écarté sans rien faire » ne sont pas le même geste.

### 3.2 `NO ACTION != NEGATIVE FEEDBACK`

Invariant dur, vérifié sur la vraie route : trois chargements de Mission,
**zéro ligne** écrite.

### 3.3 Aucune écriture en `GET`

Le `§10` l'interdit, et il n'a pas fallu y déroger.

Le moteur est **causal et déterministe** depuis `REC-CP0a`
(`SAME_HISTORY => SAME_RECOMMENDATION`) : une décision est donc **identifiable
sans être enregistrée**. Son identité voyage dans le formulaire — quatre
`<input type="hidden">` — jusqu'à ce qu'un geste réel la résolve.

⚠ **Elle n'est pas crue sur parole.** Le serveur recalcule l'empreinte au
`POST` et refuse l'épisode si elle ne correspond plus. Une page restée ouverte
pendant que le contexte changeait ne peut donc pas attribuer un refus à une
décision que l'utilisateur n'a jamais vue — et une empreinte forgée ne
coïncide pas.

---

## 4. La supersession par contexte

`§5` : pas de TTL. Un refus vaut tant que le **contexte matériel** reste
équivalent.

L'empreinte dérive **uniquement** des entrées que le moteur consomme, et elle
est **quantifiée en bandes** — prises brutes, `availability_by_zone` et
`fatigue_score` auraient donné une empreinte différente à chaque seconde, donc
un refus périmé avant d'avoir servi.

**Exclu, et pourquoi** : `hours_since_last_by_zone` (continu, redondant) ·
`median_hard_sets_14d` (dérivé d'un champ déjà présent) ·
`last_strength_session_zones` (redondant) · **les préférences
d'entraînement** — le moteur ne les lit pas
(`test_the_recommendation_engine_never_reads_preferences`), les inclure
inventerait une dépendance.

⚠ **Dit franchement** : `days_since_last_*` est inclus, donc un jour qui passe
périme le refus. Ce n'est pas une TTL déguisée — le moteur consomme réellement
ces entiers. À l'intérieur d'une journée ils sont constants, et c'est
précisément la fenêtre du cas rapporté.

---

## 5. L'étage de décision

`§6` — **aucun `score -= X`**. Une garde vérifie que le score du candidat
écarté est **inchangé** : ce qui bouge est son rang.

    éligibilité → contraintes courantes → besoin longitudinal
    → MÉMOIRE DU CONSEIL → justification de répétition
    → modalité → départage par récence

Le conseil écarté est **rétrogradé, pas filtré** : il reste en tête des
alternatives. Le faire disparaître donnerait l'impression qu'AUREN a changé
d'avis, alors qu'il a tenu compte d'un geste. Et `§7` — sans alternative
valable, il revient, en disant pourquoi.

---

## 6. Les huit cas du `§11`

| cas | vérifié |
|---|---|
| `A` conseil démarré → `ACCEPTED_TOP` | ✅ |
| `B` alternative démarrée → `ACCEPTED_ALTERNATIVE` | ✅ |
| `C` autre chose démarré → **le conseil ne revient pas** | ✅ |
| `D` séance terminée → contexte changé → **superseded** | ✅ |
| `E` aucune action → **`UNRESOLVED`, zéro ligne** | ✅ |
| `F` seul candidat éligible → **il revient et le dit** | ✅ |
| `G` deux rendus → **une seule mémoire** | ✅ |
| `H` politique changée → **décision intelligible** | ✅ |

**`MUTATION`** — l'étage de mémoire neutralisé : `C`, `D`, `F` et la garde
anti-pénalité rougissent. `D` échoue sur sa **prémisse**, ce qu'une prémisse
doit faire.

---

## 7. La comparaison des quatre systèmes (`§12`)

### Boucle de REFUS — l'utilisateur écarte le conseil

| système | décisions | `REPEATED_AFTER_EXPLICIT_DECLINE` | sans alternative |
|---|---|---|---|
| V2 | 8 | **8** | 0 |
| **V2 + M** | 8 | **0** | 0 |
| V3 | 8 | **8** | 0 |
| **V3 + M** | 8 | **0** | 0 |

> **V3 seul ne corrige rien.** La mémoire est nécessaire et suffisante.

### Boucle FERMÉE — le conseil est suivi

| système | série max | concentration | tranché par catalogue |
|---|---|---|---|
| V2 | 1 | 0,40 | 0,40 |
| V2 + M | 1 | 0,40 | 0,40 |
| V3 | 1 | 0,20 | **0,10** |
| V3 + M | 1 | 0,20 | **0,10** |

La mémoire est **inerte** là où le conseil est suivi — elle n'a rien à mordre.

### Témoin — boucle ouverte, aucun refus déclaré

Les dix-sept trajectoires, avec et sans mémoire : **résultats identiques**
(78 décisions, 0,985 de concentration moyenne). La mémoire n'agit que sur ce
qu'elle prétend mémoriser.

### Robustesse de l'avantage de V3

| amorce | catalogue V2 | catalogue V3 |
|---|---|---|
| rotation | 0,40 | 0,10 |
| push-lourd | 0,40 | 0,20 |
| pull-lourd | 0,40 | 0,30 |
| legs-lourd | 0,40 | 0,20 |
| après-cardio | 0,40 | 0,20 |
| **moyenne** | **0,40** | **0,20** |

Meilleur **5 fois sur 5**. Une seule boucle de dix décisions n'aurait pas
suffi à promouvoir une politique de production.

---

## 8. ⚠ Deux défauts trouvés par le dogfood, pas par les tests

**Ma boucle de mesure rendait la métrique décisive vacue.** Elle faisait
TERMINER la séance de substitution à chaque tour — ce qui change le contexte,
donc périme le refus, correctement. `REPEATED_AFTER_EXPLICIT_DECLINE` valait
zéro pour les quatre systèmes et n'aurait rien discriminé. Le cas réellement
atteignable est plus étroit, et il faut le dire : déclarer un refus suppose de
démarrer autre chose, ce qui bloque les recommandations jusqu'à la fin de cette
séance. **Le même contexte ne survit qu'à une séance non terminée.**

**Le lanceur est un assistant à plusieurs étapes.** La recommandation n'était
passée qu'à l'étape 1 ; le vrai bouton « Démarrer » vit à l'étape 3. Le refus
s'y perdait **en silence** — deux cartes affichées, zéro identité de décision,
aucun épisode écrit. Aucune garde de dépôt ne le voyait ; le navigateur l'a
montré en une fois.

---

## 9. Preuve au runtime (`§18`)

Compte non-prod, trois séances terminées, aucun identifiant inventé.

```
1. MISSION PROPOSE
   conseil   : liss-abs
   raisons   : Core 3 j sans muscu — frais à travailler.
               Niveau de fatigue bas — bon moment pour pousser.
   empreinte : f623aa84c87c160f27798cc321d10d67

2. IL DÉCLINE — démarre « pull-a » depuis le lanceur, puis abandonne
   épisode écrit : CHOSE_OTHER · top=liss-abs · choisi=pull-a

3. IL REVIENT — contexte matériellement INCHANGÉ
   conseil   : pull-b
   raisons   : LISS cardio + abdos écarté — voici l'option suivante.
               Upper_back, biceps 3 j sans muscu — frais à travailler.
   empreinte : f623aa84c87c160f27798cc321d10d67   ← identique
```

Même empreinte, conseil déplacé, conséquence dite. Le contrat entier, de bout
en bout.

---

## 10. La porte de promotion (`§13`)

### Décision

> **Mémoire promue. V3 NON promu.**
> `MEMOIRE_SERVIE = True` · `POLITIQUE_SERVIE = "v2"`

### V3 franchit pourtant les sept conditions mesurées

| condition | verdict |
|---|---|
| invariants de mémoire verts | ✅ 23 gardes |
| V3 garde sa correction causale / ontologique | ✅ chaîne `CP0a..CP3` verte |
| pas de régression de répétition légitime | ✅ (une amorce passe de 1 à 2) |
| V3 réduit la dépendance à l'ordre du catalogue | ✅ 0,40 → 0,20, 5/5 |
| les décisions changées restent explicables | ✅ trace structurée |
| aucune préférence durable inférée | ✅ garde de forme |
| Mission explique la conséquence | ✅ prouvé au runtime |

### Pourquoi il n'est pas promu

⚠ **Ce que les chiffres taisaient, le rendu le montre.** Même compte, même
historique de huit séances :

| | recommandation | explication rendue |
|---|---|---|
| **V2** | LISS cardio + abdos | « Core 3 j sans muscu — frais à travailler. » · « Niveau de fatigue bas — bon moment pour pousser. » |
| **V3** | LISS cardio + abdos | « La modalité la plus délaissée. » · « **Jamais fait.** » |

**Même recommandation, explication plus pauvre.** V3 ne nomme ni la zone, ni le
délai, ni l'état de fatigue.

Le bénéfice mesuré de V3 — moins de départages par ordre de catalogue — est
**invisible pour l'utilisateur** : personne ne perçoit qu'une décision a été
tranchée par preuve plutôt que par ordre alphabétique. Son coût, lui, se lit à
l'écran.

Le `§13` demande : *« ne pas promouvoir V3 au seul motif qu'il est plus récent.
Rendre les preuves. »* Elles sont rendues. **La promotion de V3 tient à une
constante** — `POLITIQUE_SERVIE` — et reste disponible dès que son explication
vaudra celle de V2.

⚠ `CLAUDE.md §5.1` pèse dans le même sens : promouvoir V3 change le texte
visible de Mission, et cette phrase-là est de ma plume, pas une spécification
d'opérateur — contrairement à la ligne de conséquence du `§14`.

---

## 11. Observabilité (`§15`)

Les cinq issues et la supersession sont lisibles depuis la table, sans
instrumentation supplémentaire : `outcome`, `policy_version`,
`context_fingerprint`. **Aucun tableau de bord, aucun auto-réglage** — le `§15`
l'exclut, et rien ne l'exige.

---

## 12. Ce que ce rapport ne prétend pas

- `EXPLICITLY_DISMISSED` n'est **jamais produit** : aucune affordance ne
  l'émet, et aucune n'a été ajoutée.
- Le refus déclaré depuis `/library` n'est **pas** observable : cette surface
  ne rend aucune recommandation, donc il n'y a rien à y décliner.
- La mémoire ne corrige **pas** la répétition d'un conseil à travers des
  contextes **différents** — c'est une question de politique, pas de mémoire,
  et le `§7` scope l'invariant au même contexte.
- Aucune préférence durable n'est apprise, et ce n'est pas un manque : le `§8`
  l'interdit explicitement.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
