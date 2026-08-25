# `LEGACY_SCORE_CONSUMER` — registre des consommateurs du score composite

**Statut : toléré, pas validé.** Ce registre existe parce que `TRAIN1-C` a
retiré la doctrine de score global de la surface Progression sans pouvoir la
retirer du dépôt : quatre modules la consomment encore, et les débrancher
sortirait du périmètre de Progression.

Un consommateur inscrit ici n'est **pas** approuvé par UX4. Il est *constaté*.

Une garde (`tests/test_train1c_progression_consolidation.py`) compare ce
registre à la réalité du code et rougit **dans les deux sens** : un appelant
qui s'ajoute sans être inscrit, un inscrit qui disparaît sans mise à jour.

---

## 1. Ce que la doctrine calcule

`app/services/muscle_scoring.py` → `compute_physique_dashboard(db, user_id,
window_days)` rend :

| Objet | Nature |
|---|---|
| `global_score` (0–100) | moyenne des axes du radar |
| `global_grade` (A/B/C) | seuils sur `global_score` |
| `radar_axes` / `radar_svg` | six axes agrégeant les onze zones |
| `zone_scores[].score` (0–100) | le **substrat** : `0,50·perf + 0,30·expo + 0,20·anthropo` |

Les onze scores de zone ne sont pas un détail du score global — le global est
la moyenne de leurs agrégats. Retirer la somme en gardant les termes aurait
masqué la doctrine sans la retirer.

### Pourquoi elle ne pouvait pas rester sur Progression

Le pilier d'exposition vaut :

```python
hard_sets / (ZONE_VOLUME_TARGET[zone] * window_days / 7) * 100
```

C'est un **pourcentage de cible**. L'en-tête de `app/services/zone_exposure.py`
s'interdit explicitement de le dire — « sous-entraîné · sur-entraîné · optimal ·
% de cible » — au motif que le dépôt ne produit que des bandes de
*planification* dont l'en-tête précise qu'aucune littérature ne justifie les
bornes. La barre de la carte de zone rendait ce ratio comme une progression
vers un objectif.

Deux autres piliers relèvent du même arbitrage : `_score_performance` classe
une variation de tonnage dans cinq paliers codés en dur ; `_score_anthropo`
note à 90 un tour de bras qui augmente et à 30 un qui diminue — inversé pour
la taille. Ce sont des jugements de valeur, pas des mesures.

---

## 2. Les consommateurs recensés

| Module | Ce qu'il lit | Statut |
|---|---|---|
| ~~`app/routers/leaderboard.py`~~ | ~~`dashboard.radar_svg`~~ | ✅ **SORTI** — `TRAIN1-E` / C4 |
| ~~`app/services/leaderboard.py`~~ | ~~`dashboard.radar_axes`~~ | ✅ **SORTI** — `TRAIN1-E` / C4 |
| `app/routers/body_intelligence.py` | `compute_physique_dashboard` complet | 🔒 `DO_NOT_ACTIVATE_AS_STANDALONE` — voir §5 |
| `app/services/dashboard.py` | `compute_physique_dashboard` complet | Alimente `dashboard.html`, **qu'aucune route ne rend** depuis Sb_27.6. Code mort conservé : huit fichiers de tests en dépendent. |

### Ce qui est sorti, et ce que cela change

`TRAIN1-E` / C4 a retiré l'analytique physique des **surfaces sociales**. Le
classement ne dépend plus du tout de `muscle_scoring` : il ne l'importe plus,
ne l'appelle plus une fois par ligne, et ne rend plus de radar.

**La lettre A/B/C reste, et ce n'est plus une tolérance.** Elle vient de
`compute_grade`, dérivée de la qualité de séance — pas du physique. Un
classement sans ordre n'est pas un classement : c'est une note **sociale**,
inscrite comme un choix.

Le radar vivait sous **trois classes CSS différentes** — `tooltip-radar` au
classement, `radar-wrap` au profil public, `profile-preview__radar` dans la
carte d'aperçu. Chercher une seule d'entre elles en aurait laissé deux en place ;
la garde les vise toutes les trois.

### Ce qui a quitté la liste

`app/routers/pages.py` → la route `/physique`. Elle était le **seul**
consommateur exposé par défaut à un utilisateur connecté. Elle redirige
désormais vers `/progress` (303).

---

## 3. Ce que Progression a repris

Un seul fait, et c'est le seul que la surface Physique portait sans que
Progression l'ait : les **séries de travail validées par zone**, absorbées dans
l'instrument d'exposition.

Trois conditions à cette reprise, et les trois comptent :

- **même fenêtre** — quatorze jours, pas le sélecteur 30/60/90 ;
- **même résolveur** — `resolve_zone` (`MUSCLE_MAPPING_TRUTH_01`), pas
  `resolve_exercise_zones` : deux autorités d'attribution auraient mis deux
  comptes contradictoires sur une même ligne ;
- **aucun coefficient, aucune cible** — une série compte une fois, sur la zone
  primaire, rendue comme un entier.

### Ce qui n'a pas suivi, et pourquoi

| Objet | Décision |
|---|---|
| score de zone, tendance, barre | doctrine — retirée, non déplacée (ordre opérateur) |
| `confidence` (« élevée / moyenne / faible ») | un compte de signaux présents avec des seuils arbitraires ; pas une mesure |
| `top_exercises` | fait réel, mais l'instrument progressif nomme déjà les exercices avec leur performance ; trente-trois noms de plus dans le détail par zone iraient contre la densité visée |
| `measurement_trend` (« +1,5 cm ») | fait réel, autre question. **Aucune surface ne peut le produire aujourd'hui** : rien n'écrit de `BodyMeasurement` hors du parcours `/body`, désactivé par défaut. Il appartient à la surface où l'on saisit des mesures. |

---

## 4. Condition de sortie

Ce fichier disparaît quand `compute_physique_dashboard` n'a plus d'appelant.
Cela suppose deux décisions qui ne relèvent pas de Progression :

1. ce que le **classement public** montre à la place du radar ;
2. ce que devient **Body Intelligence** — la surface, pas seulement son drapeau.

Tant qu'elles ne sont pas prises, la doctrine survit là où elle est inscrite
ci-dessus, et **nulle part ailleurs**.


---

## 5. `DO_NOT_ACTIVATE_AS_STANDALONE` — Body Intelligence

**Arbitrage C9.** Body Intelligence n'est **pas** activable comme surface
autonome. Le drapeau `body_intelligence_enabled` reste à `false`, et son
passage à `true` n'est pas une décision d'implémentation.

Ce que cela veut dire, précisément :

- **les internes réutilisables sont préservés** — `body_intelligence.py`,
  `body_intelligence_inputs.py` et le bloc de snapshot du rapport coach restent
  en place et testés. Le travail n'est pas jeté ;
- **aucune nouvelle surface** ne s'y branche ;
- **les anciens consommateurs analytiques partent progressivement**, tranche
  par tranche, à mesure que chacun trouve son remplacement. C4 en a retiré deux
  d'un coup ;
- **la condition de sortie de `muscle_scoring` passe donc par ici.** Il ne
  reste que deux appelants, et tous deux sont des surfaces que rien ne rend :
  Body Intelligence derrière son drapeau, et le tableau de bord mort.

Autrement dit : **`compute_physique_dashboard` n'a plus aucun consommateur
atteignable par un utilisateur.** Le supprimer est désormais un travail de
nettoyage, plus un arbitrage produit — mais il reste hors du périmètre de
Progression, et les huit fichiers de tests du tableau de bord attendent leur
propre tranche.

---

## 6. Statut des surfaces (arbitrage C11)

| Surface | Statut | Ce que cela implique |
|---|---|---|
| **Accueil** · **Séance** | `SOVEREIGN` | une dérive est une régression |
| **`PROGRESSION_L1`** | `SOVEREIGN` | l'architecture de premier niveau — signaux, rail, exposition, instrument progressif, rythme — est **gelée**. La toucher demande une décision explicite. |
| **`PROGRESSION_L2`** | `EVOLVABLE` | les niveaux d'inspection (détail du rail, détail par zone, `prog__more`) peuvent évoluer sans que ce soit une régression. |
| Profil · Bibliothèque · Historique | `TRANSITIONAL` | refonte structurelle attendue, pas une régression |

La distinction L1/L2 est ce qui rend le gel praticable : quatre tranches de
travail sont protégées **sans** interdire d'approfondir l'inspection, qui est
précisément là où la cible `FAIT → INSTRUMENT → INSPECTION → PROVENANCE`
continue de se construire.
