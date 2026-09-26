# REC-CP5 — la parité d'explication, et la promotion de V3

**Statut** : livré · **Merge** : `42258ce` · **Base** : `fbb4942`

---

## 1. Le blocage venait de l'énoncé, pas du classement

`REC-CP4` avait refusé de promouvoir V3 pour une raison que seul le rendu
montrait : sur un compte réel de huit séances, V3 rendait **la même
recommandation que V2** en n'expliquant plus que

    « La modalité la plus délaissée. »  ·  « Jamais fait. »

La cause n'était pas le classement. C'étaient deux défauts d'**énoncé**, tous
deux dans `expliquer` :

1. **La couverture — critère PRIMAIRE du rang — se taisait dans sa bande
   médiane.** Elle n'était dite qu'au-dessus de 0,75 ou en dessous de 0,25,
   c'est-à-dire jamais dans le cas le plus fréquent.
2. **« Jamais fait » parlait toujours**, pour tout candidat jamais effectué,
   qu'il ait départagé ou non — devenant l'explication entière d'une décision
   qu'il n'avait pas prise.

---

## 2. Ce qui a décidé est **lu**, pas deviné

`critere_decisif(gagnant, dauphin)` rend le **premier indice où les deux clés
lexicographiques diffèrent**. V3 rangeant par précédence, ce rang EST,
littéralement, le critère qui a tranché.

Aucune pondération inventée, aucune heuristique : le `§3` est tenu en lisant
le classement plutôt qu'en le paraphrasant. « Jamais fait » ne parle donc plus
que lorsqu'il a effectivement séparé le gagnant de son dauphin.

La couverture, elle, est désormais **toujours énoncée**, graduée sur quatre
paliers — « le moins servi », « peu servi », « servi moins que la moyenne »,
« déjà bien servi » — le dernier étant un facteur **limitant**, pas gagnant.

---

## 3. ⚠ Le classement n'a pas bougé d'un pouce

C'est ce qui fait de `REC-CP5` une micro-tranche plutôt qu'un changement de
politique déguisé.

Une garde lit la **source** de `classer_candidats` et refuse qu'aucune
fonction d'explication y apparaisse. Une seconde épingle la table
`CRITERES_DU_RANG` contre la clé réelle.

Mesures identiques avant/après : catalogue **0,10**, concentration **0,20**,
mêmes gagnants sur les dix-sept trajectoires.

---

## 4. Porte de promotion — franchie

| condition (`§4`) | preuve |
|---|---|
| invariants REC verts | **76 gardes**, `CP0a → CP5` |
| mémoire du conseil verte | 23 gardes |
| répétition après refus corrigée | **0/8** (8/8 sans mémoire) |
| répétition légitime possible | garde `CP2` verte |
| ordre de catalogue réduit | **0,10** contre 0,40 |
| explication non appauvrie | **parité mesurée**, ci-dessous |
| Mission compréhensible | rendue au navigateur |

### Parité, sur données IDENTIQUES et même recommandation

| | recommandation | raisons rendues |
|---|---|---|
| **V2** | LISS cardio + abdos | « Core 3 j sans muscu — frais à travailler. » · « Niveau de fatigue bas — bon moment pour pousser. » |
| **V3** | LISS cardio + abdos | « Core / Abdos : peu servi sur 14 derniers jours. » · « Zones récupérées. » |

Trois facteurs de chaque côté — la raison principale est rendue en tête, au
dessus des deux sous-raisons.

Sur le fond, les **deux** raisons de V3 décrivent des critères qui ont
réellement participé au classement. La bande de fatigue globale de V2
n'explique pas le choix de *ce* gabarit-là.

    POLITIQUE_SERVIE = "v3"
    MEMOIRE_SERVIE   = True

---

## 5. ⚠ Un défaut trouvé par le sweep, pas par les tests ciblés

`test_resume_banner_only_shows_own_sessions` cherchait la sous-chaîne nue
« Pull A » dans la page d'accueil, pour prouver qu'aucune séance d'un **autre**
utilisateur n'y figure. Depuis que V3 sert, Mission peut légitimement
**recommander** Pull A.

**Vérifié avant de toucher la garde** — une garde de propriété qui rougit
mérite d'être crue jusqu'à preuve du contraire :

* « Reprendre » était **absent** → aucune affordance de reprise ;
* la chaîne trouvée portait le **suffixe de catalogue** (« — Dos largeur +
  Delts postérieurs »), que le snapshot de la séance étrangère (« Pull A »
  tout court) n'a pas.

Les deux ne pouvaient donc pas être le même objet. **Collision de texte, pas
fuite de propriété.**

La garde épingle désormais **l'identifiant de séance** : un `id` ne peut pas
entrer en collision avec un nom de gabarit, donc c'est strictement plus fort
qu'un libellé. Vérifiée par mutation — filtre `user_id` retiré de
`latest_open_session`, elle rougit.

C'est la deuxième fois de la séquence qu'une sous-chaîne est prise pour un
objet, et la première fois que je l'avais écrite moi-même (`\bcard\b` attrapant
`rule-card`, `UI-CP7`).

---

## 6. Gardes repointées, aucune affaiblie

| garde | propriété inchangée |
|---|---|
| `…politique_servie_est_declaree…` | la promotion doit être **écrite**, pas subie |
| `…ce_qui_sert_est_declare…` | idem, avec ses preuves |
| `test_home_reco_origin._reco` | interrogeait V2 **en dur** ; passe par le point de service, donc insensible à la prochaine promotion |
| `test_resume_banner_only_shows_own_sessions` | identifiant au lieu du libellé |

---

## 7. Closeout

| | |
|---|---|
| PR | [#250](https://github.com/MFE-DSS/workout-session-tracking/pull/250) |
| Merge | `42258cef5b169a4f5ed3c20d48565e7ac9fa792e` |
| CI PR | **10/10 verte** |
| Sonar | gate `OK` — couverture nouveau code **100 %**, 0 smell |
| Sweep local | 343/343 fichiers, `tous les lots sont verts.` |
| Threads de revue | 0 |

### Suite

Le travail de politique de recommandation est **gelé** (`§4`) : pas de réglage
supplémentaire sans nouvelle preuve de production.

Reste ouvert : `UI-CP7.5`, dont le paquet d'arbitrage est livré et attend trois
décisions — consentement, composition du closeout, sort des deux scores.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
