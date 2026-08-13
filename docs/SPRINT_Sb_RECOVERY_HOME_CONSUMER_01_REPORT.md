# SPRINT Sb_RECOVERY_HOME_CONSUMER_01 — P0.4 visible sur la Home (RAPPORT)

**Base canonique :** `7f53188` · **Branche :** `sb/recovery-home-consumer-01` · **Tier :**
**SHARED_CODE** (`check_scope`) — la Home est une route chaude et partagée. **Full sweep
CI-identique exécuté** (exigé par la mission pour un consommateur vivant).
**Autorités :** `Sx_RECOVERY_READINESS_01_SPEC.md` §8 · chaîne P0.4 livrée · architecture Home.
**Premier consommateur vivant de P0.4.**
**0 migration · 0 modèle · 0 colonne · 0 activation Body Intelligence · 0 modif
`recommendation.py`/`behavioral.py` · 0 modif briefing · 0 nouvelle formule · 0 déploiement.**

## 1. Précondition Sonar — action opérateur toujours requise

Lecture autoritative au préflight (route documentée par `Sb_SONAR_GOVERNANCE_01`) :

```
periods: [{"mode": "previous_version", "date": "2026-04-10T12:45:26+0000"}]
```

**Verdict : `OPERATOR SONAR ACTION STILL REQUIRED`.** La définition New Code est **toujours**
`previous_version` sur la base d'avril. Le contournement obsolète `settings/set` **n'a pas été
tenté** — il est inerte, c'est établi.

Cela **ne bloque pas** le travail produit : le gate Sonar **au niveau PR** reste autoritatif et a
fonctionné (`OK`, **100 %** de couverture du code neuf, 0 smell, 0 bug). L'action reste manuelle :
*Project Settings → New Code → Number of days → 30*.

## 2. Brainstorming / Options / Risques / Choix retenu (CLAUDE.md §3)

**Audit de la hiérarchie Home avant de choisir la place et le nom.** Constat décisif : la Home
portait **déjà deux surfaces d'état**.

| Surface existante | Nature | Libellé réel |
|---|---|---|
| widget déclaratif | ce que l'utilisateur **déclare** (1–5, 1×/jour, + CTA de saisie) | **« État du jour »** |
| KPI hérité | `behavioral.readiness_score`, score **0–100** + phrase de conseil | **« disponibilité »** |

Le risque de nommage était donc réel et concret, pas théorique : « disponibilité » est déjà l'un
des **quatre** sens d'*availability* relevés par la spec §1.

**Options de placement / nommage :**

1. Réutiliser « État du jour » — **rejeté**, c'est le widget déclaratif ; homonymie directe.
2. Étendre le briefing pré-séance — **rejeté**, la mission l'interdit et son contrat sert
   l'exécution d'exercice (reps, dernière fois, cues), pas l'état.
3. **Nouvelle tuile dans la boucle de coaching, libellée « État d'entraînement », avec sous-titre
   de provenance** — **retenu**. Elle réutilise le gabarit `card tile` existant, ne redessine rien,
   et le sous-titre *« Estimé à partir de tes séances enregistrées. »* dit ce qu'aucun nom seul ne
   peut dire : **ce bloc est inféré**, les voisins sont déclaré et hérité.

**Verdict de coexistence : pas de HARD STOP.** Les trois surfaces restent distinguables par nom
**et** par provenance affichée. Le KPI hérité n'est **ni renommé ni retiré** (additif d'abord,
OQ-1) ; quatre tests épinglent la distinction et la survivance des deux surfaces héritées.

**Risques identifiés et parades :**

| Risque | Parade |
|---|---|
| Le bloc devient un tableau de bord | plafonds `HOME_MAX_ITEMS=3` / `HOME_MAX_ZONE_ITEMS=2`, testés |
| Double CTA de saisie | le `data_prompt` de l'explainer est **délibérément non repris** ; test |
| La tuile déplace une décision | parité `today`/`week` prouvée **octet pour octet** |
| Copie parallèle de récupération | tests d'absence des tables de l'explainer dans consommateur **et** gabarit |
| Une panne rend la Home indisponible | patron `_safe` existant, 6 tests de confinement |

## 3. Chaîne de données — une seule source de vérité

```
DB → build_training_state → build_proactive_explanation → vue-modèle → gabarit Home
```

Le consommateur **ne calcule rien**. Tests d'anti-duplication : aucune phrase de bande, aucun
libellé de confiance, aucun `.basis`, aucun `build_zone_recovery`, aucun `compute_behavioral_state`
dans le module — ni dans le gabarit.

## 4. Deux erreurs de conception trouvées par les tests, pas par la lecture

**(a) Le roll-up macro est structurellement muet.** Les axes radar (OQ-5) semblaient la granularité
évidente pour un bloc compact. **Mesuré** : `worst_zone_rollup` dégrade un axe en
`Confidence.NONE` dès qu'**une** de ses zones est inconnue, et un axe compte 2–3 zones. Sur un
compte réaliste les axes ne disent donc **rien** — j'aurais livré un bloc vide. C'est un
comportement **correct** de la tranche 4 (un axe partiellement inconnu ne se résume pas), pas un
défaut. La tuile lit des **zones nommées**, plafonnées à deux.

**(b) Une séance musculation **et** cardio ne produit aucune estimation.** Le cardio dégrade la
confiance de zone jusqu'à `NONE` (tranche 4). Ma première version supprimait alors **toute** la
tuile — jetant avec l'estimation absente un contexte cardio et un état déclaré parfaitement
**honnêtes**. C'était appliquer le principe P0.4 trop grossièrement. Désormais le **message unique**
d'état de donnée et le **contexte** coexistent : ce qui doit rester tu, c'est l'**interprétation
physiologique**, jamais le **fait enregistré**. Six tests dédiés épinglent ce cas.

## 5. Ce qui s'affiche — contrat exact

| Cas | Rendu |
|---|---|
| estimations disponibles | ≤ 3 items : contexte déclaré · 1–2 zones les plus contraintes (`recovery_rank_key`) · contexte cardio |
| `Confidence.NONE` partout | **un seul** message : *« Pas assez de données récentes pour estimer ton état d'entraînement. »* |
| aucune estimation mais contexte réel | le message **plus** le contexte cardio / déclaré |
| compte neuf | le message seul, **zéro** interprétation corporelle |
| readiness périmée | **non remontée** en proactif |
| bonne readiness | état déclaré, **aucun** langage d'escalade |
| cardio | *exposition récente* ; ni BPM, ni calories, ni durée |
| panne | tuile absente, Home et reco intactes |

Le budget d'items est **calculé** et non codé en dur : les contextes prennent leur place, les zones
remplissent le reste, et **au moins une** zone est montrée dès qu'une estimation existe.

`GLOBAL_INSUFFICIENT_MESSAGE` prend la formulation de l'opérateur et **reste dans l'explainer** :
la décision « explicite sur la donnée manquante » garde un seul point de définition, et une seconde
surface héritera du texte sans le recopier.

## 6. Le piège Jinja qui a coûté un cycle

`{% for item in home.training_state.items %}` résout **la méthode `.items` du dict**, pas la clé —
`TypeError: 'builtin_function_or_method' object is not iterable`, **Home en 500**. La clé est
renommée `entries` : aucun futur auteur de gabarit ne peut retomber dessus.

Second piège du même rendu : Jinja échappe l'apostrophe, donc `État d'entraînement` arrive en
`État d&#39;entraînement`. Les assertions comparent désormais le texte **décodé**, tel qu'un
lecteur le voit.

## 7. Garanties prouvées mordantes par plantation

Planter dans le consommateur une légende physiologique avec pourcentage, un libellé de confiance
écrit à la main, et un plafond de densité retiré fait échouer **4 tests** sur **4 gardes
distinctes** (densité · onze zones · anti-duplication de libellé · garde-fou de formulation).

## 8. Exploitation

- **Une seule** construction de `TrainingState` par requête Home (espion).
- **Aucun N+1** : à noms distincts constants, multiplier les séances ne change pas le nombre de
  requêtes. Le test ne compare **pas** deux jeux de noms distincts — de nouveaux noms exigent
  légitimement de nouvelles résolutions, et l'exiger constant reviendrait à interdire la
  résolution elle-même.
- **Zéro écriture** (filtre `INSERT|UPDATE|DELETE` sur les requêtes émises).
- Coût borné par un garde de régression.

## 9. Piège d'outillage — 60 faux échecs, zéro défaut produit

Lancer `pytest <chemin absolu du worktree>` **depuis le cwd du repo principal** fait résoudre `app`
**depuis le repo principal** : le sprint teste alors l'**ancien** code. `PYTHONPATH` ne suffit
pas. Symptômes trompeurs : `ModuleNotFoundError` sur le module neuf, et des assertions qui échouent
parce que le payload n'a pas le champ qu'on vient d'ajouter. Le fichier seul passait, ce qui
orientait à tort vers un problème d'ordre.

**Règle consignée en mémoire** : tout sweep de worktree se lance avec `cd <worktree>` et des
chemins **relatifs**. Après correction : **1193** puis **3764** verts.

## 10. Tests

| Portée | Tests |
|---|---|
| Dédiés `test_recovery_home_consumer.py` | **73** |
| Broad sweep ciblé (home · dashboard · reco · readiness · recovery · cardio · zone · auth · narrative · weekly) | **1193** |
| **Full sweep, invocation identique à la CI** | **3764, 0 échec** |

Un test existant a **légitimement** changé : `test_payload_always_has_three_keys` épinglait
exactement trois clés de payload. Il en épingle **quatre** — assertion gardée **exacte** plutôt que
relâchée en sous-ensemble, car un sous-ensemble cesserait de détecter une tuile disparue.

## Verdict

**Livré, mergé, canonique verte.** P0.4 est **visible** pour la première fois.

La valeur de cette tranche n'est pas le bloc d'interface — c'est que la chaîne tient **jusqu'à
l'écran** sans qu'aucune de ses prudences ne se perde en route : pas de pourcentage, pas de
confiance inventée, pas d'interprétation quand la preuve manque, et pas une seule décision
d'entraînement déplacée.

**Limite assumée** : la tuile est le **seul** consommateur. La granularité « zones nommées » a été
choisie sur une contrainte mesurée (les axes sont muets), pas sur un test utilisateur ; si le
dogfood montre que deux zones nommées sont trop techniques pour un cockpit, le remède est côté
sélection, pas côté contrat.
