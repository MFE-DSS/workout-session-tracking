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

| Module | Ce qu'il lit | Pourquoi il reste |
|---|---|---|
| `app/routers/leaderboard.py` | `dashboard.radar_svg` (profil public) | Surface **sociale**, avec sa propre doctrine de note (`compute_grade`). La refondre est un sujet à elle seule. |
| `app/services/leaderboard.py` | `dashboard.radar_axes` (mini-radar par ligne) | Idem — c'est le même produit que ci-dessus. |
| `app/routers/body_intelligence.py` | `compute_physique_dashboard` complet | Derrière `body_intelligence_enabled`, **désactivé par défaut**. Zéro surface de production tant que le drapeau est à `false`. |
| `app/services/dashboard.py` | `compute_physique_dashboard` complet | Alimente `dashboard.html`, **qu'aucune route ne rend** depuis Sb_27.6. Code mort conservé : huit fichiers de tests en dépendent. |

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
