# REC-CP3 — l'explication structurée, lue au lieu d'être re-dérivée

**Statut** : livré · **Branche** : `sb/rec-cp3-explication` · **Base** : `242674b`

⚠ **V3 n'est toujours pas promu.** Cette tranche le rend *promouvable* — il
produit désormais une phrase et une explication — mais la politique de
production reste V2, et la garde du `§12` le vérifie par balayage des
importations réelles.

---

## 1. Le défaut corrigé

`recommendation_explainer.py` reconstruisait ses raisons depuis un contexte
appauvri : `cold_start`, `fallback`, `days_since_last_*`, `fatigue_score`, plus
la phrase déjà écrite par le moteur. Il **re-devinait donc ce que le moteur
savait et n'avait pas transmis**.

Tant qu'aucune politique ne produisait de trace, c'était le seul moyen
disponible. V3 en produit une. La reconstruction devient alors non seulement
inutile mais nuisible : deux logiques parallèles finissent par diverger, et
c'est celle qui devine qui a tort.

`explain_recommendation` lit désormais `top["explication"]` quand elle existe.
**Le chemin de re-dérivation reste entier** pour V2 — le retirer en même temps
aurait silencieusement vidé l'explication de la seule politique que
l'utilisateur voit.

---

## 2. Ce que le moteur dit maintenant

```python
{
  "facteurs_gagnants":        ("core / abdos : le moins servi sur 14 derniers jours",
                               "zones récupérées", "la modalité la plus délaissée"),
  "facteurs_limitants":       (),
  "horizon":                  "14 derniers jours",
  "famille":                  "liss",
  "justification_repetition": None,
  "provenance":               "mesurée",   # ou "partielle"
  "rang":                     0,
}
```

- **`horizon`** dit *« 14 derniers jours »*, jamais « cycle » ni « récupération
  complète ». Le `§8` l'impose : quatorze jours est une **mémoire**, pas une
  vérité physiologique. Une garde interdit ce vocabulaire.
- **`provenance`** réutilise la grammaire de `zone_exposure`
  (`REC-CP0b`) au lieu d'en créer une seconde.
- **`justification_repetition`** n'est renseignée que quand la répétition est
  portée par la couverture — `REPEAT_REQUIRES_EVIDENCE` rendu visible à
  l'utilisateur, et non seulement vrai dans le code.

**Aucun nombre n'en sort.** Ni score 0-100, ni déficit, ni jours. Une garde
balaie le texte rendu caractère par caractère et n'autorise que l'horizon
d'observation.

---

## 3. Ce que l'utilisateur lit — `RUNTIME_MEASURED`

```
── push lourd → liss-abs
     · Core / Abdos : le moins servi sur 14 derniers jours.
     · Zones récupérées.
     · La modalité la plus délaissée.

── rotation → pull-b
     · Dos épaisseur, Biceps : le moins servi sur 14 derniers jours.
     · Zones récupérées.
     · Jamais fait.

── jambes lourdes → short-upper
     · Deltoïdes latéraux, Pectoraux : le moins servi sur 14 derniers jours.
     · Zones récupérées.
     · Jamais fait.
```

Les libellés viennent de `ZONE_LABELS`, le vocabulaire déjà utilisé par le
produit — pas d'un second glossaire.

---

## 4. ⚠ Le défaut qu'aucune garde de structure ne voyait

Les trois premières gardes vérifiaient des clés et des ensembles. Toutes
vertes. Puis j'ai écrit une garde qui regarde le **texte rendu**, et elle a
échoué au premier essai :

```
AssertionError: push lourd : ne commence pas par une capitale — 'zones récupérées'
```

Les facteurs sont rédigés en minuscule et sans point, pour se composer dans la
phrase compacte. Affichés tels quels comme raisons autonomes, ils produisaient
« zones récupérées » — sans capitale ni ponctuation.

C'est le même mode d'échec que la cible tactile de 18 px d'`UI-CP5` : une
structure correcte, un rendu fautif, et **aucune garde de structure capable de
le voir**. La mise en forme appartient à l'explainer (`_en_phrase`), pas au
moteur : le moteur dit ce qui a décidé, l'explainer décide comment ça se lit.

---

## 5. Gardes — 8, dont la centrale vérifiée par mutation

| Garde | Ce qu'elle tient |
|---|---|
| `…suit_la_trace_et_ignore_le_contexte_qui_la_contredit` | **la garde centrale** |
| `…ce_que_l_utilisateur_lit_reellement` | le rendu, pas la structure |
| `aucun_nombre_ne_traverse_l_explication` | `§` — pas de score comme vérité |
| `…horizon_est_nomme_comme_une_observation` | `§8` |
| `…phrase_n_est_pas_redigee_deux_fois` | une seule plume |
| `…observation_partielle_se_dit_et_ne_se_confond_pas` | deux notes distinctes |
| `…chemin_de_re_derivation_reste_entier_pour_v2` | V2 non dégradé |

### La garde centrale est construite pour mordre

Elle fabrique une charge dont la **trace** dit une chose et dont le **contexte**
en dit une autre, incompatible : `cold_start: True`, `fallback: True`,
`fatigue_score: 90`. Si l'explainer re-dérivait, il produirait les raisons du
contexte.

**`MUTATION`** — branche de lecture désactivée (`trace = None`) : deux gardes
rougissent, dont celle-ci. Une charge cohérente serait passée avec l'ancien
chemin et n'aurait rien prouvé.

### ⚠ Une seconde liste, évitée de justesse

J'avais écrit ici une garde `§12` avec **sa propre** liste de lecteurs
autorisés de V3. La garde de `REC-CP2` a rougi en voyant ce module — et elle
avait raison sur les deux plans : il fallait déclarer le nouveau lecteur, et il
ne fallait pas un second registre. Deux listes du même fait divergent ; le
dépôt en porte plusieurs exemples. Le doublon a été supprimé, la déclaration
faite dans le registre unique.

### Deux notes que l'on aurait pu confondre

« Pas encore assez de données pour personnaliser » et « un exercice de ton
historique n'a pas pu être classé » ne disent pas la même chose. Les confondre
ferait passer une lacune de **classement** pour une absence d'historique — et
l'utilisateur corrigerait la mauvaise chose.

---

## 6. La promotion de V3 — état de la porte `§12`

`REC-CP3` lève le **blocage technique** : V3 rendait `phrase: ""`, donc le
promouvoir aurait livré une explication vide sur MISSION. Ce n'est plus le cas.

Ce qui est établi, mesuré, en faveur de V3 :

| Défaut mesuré en `REC-CP1` | V2 | V3 |
|---|---|---|
| décisions tranchées par l'ordre du catalogue (boucle fermée) | 0,40 | **0,10** |
| histoires opposées → séquences identiques | oui | **non** |
| concentration du gagnant (boucle fermée) | 0,40 | **0,20** |

Ce qui **n'est pas** établi, et que je n'affirme pas :

- V3 n'est pas « meilleur parce qu'il varie davantage » (`§11`). Les trois
  lignes ci-dessus sont la réparation de défauts **mesurés**, pas un goût pour
  la variété.
- **Le cas « conseil décliné » n'est traité par aucune des deux politiques.**
  C'est le vrai énoncé de la plainte de dogfood, et il déborde le scoring : il
  suppose de mémoriser ce qui a été **proposé**, pas seulement ce qui a été
  fait. Aucune persistance nouvelle n'a été inventée ici.

La promotion reste donc un geste séparé, explicite, et non inclus dans cette
tranche.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
