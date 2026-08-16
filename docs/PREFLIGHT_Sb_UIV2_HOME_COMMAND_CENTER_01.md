# PRÉFLIGHT Sb_UIV2_HOME_COMMAND_CENTER_01 — hiérarchie avant CSS

**Programme :** `AUREN_UI_V2_PRODUCT_QUALITY_01`, tranche 1/7 ·
**Base :** `fbed54b` · **Statut : PRÉFLIGHT SEUL — aucune implémentation.**

Le programme impose que la hiérarchie de chaque écran existe **avant** toute
modification CSS. Ce document est cet artefact pour Home. Il n'est pas un
rapport de sprint : rien n'a été implémenté.

---

## 1. Audit des tuiles actuelles (`app/templates/index.html`, 232 lignes)

| # | Tuile | Ce qu'elle porte | Verdict |
|---|---|---|---|
| 1 | **Héros** `today-home__hero` | séance active · sinon séance suivante · sinon « Prêt à t'entraîner ? » | **KEEP PRIMARY** |
| 2 | **État du jour — rempli** | badges 1-5 par champ + FC repos + lien historique | **KEEP CONTEXT**, compacter |
| 3 | **État du jour — vide** | `<details open>` avec le formulaire d'échelles complet | **MOVE LOWER** — voir §3 |
| 4 | **Disponibilité** `details.insight` | score 0-100 + reco + explication dans une carte imbriquée | **MOVE LOWER** — voir §4 |
| 5 | **Carte KPI** | « séances cette sem. » + sparkline + lien /progress | **KEEP CONTEXT**, à enrichir |

---

## 2. Hiérarchie cible

**PRIMARY — une seule action dominante**
Le héros, inchangé dans son principe : reprendre la séance active, sinon
démarrer la séance proposée, sinon inviter à démarrer.

**SECONDARY — contexte de la semaine**
Ce qui manque aujourd'hui et que le programme demande :
séances faites **sur cadence déclarée** (le Home affiche « séances cette sem. »
sans jamais la comparer à la cadence que l'utilisateur a déclarée) · prochaine
séance planifiée · **une** contrainte significative.

**TERTIARY — état d'entraînement**
Disponibilité, énoncée court.

**HIDDEN UNTIL REQUESTED**
Le détail du calcul de disponibilité · le formulaire d'état du jour · la
sparkline et l'analyse.

---

## 3. Le défaut le plus net : la variante vide de « État du jour »

Quand aucun état n'est saisi, le widget rend un `<details open>` contenant le
**formulaire complet** d'échelles 1-5, bordure `--warn` à gauche, juste sous le
héros.

Résultat : un utilisateur qui n'a pas rempli son état voit **deux** surfaces qui
réclament une action au-dessus de la ligne de flottaison — le héros et un
formulaire. C'est exactement la concurrence que la doctrine §1 interdit
(« une seule action visuellement dominante »).

**Correction visée** : replier par défaut, réduire à une invite d'une ligne, et
laisser le formulaire derrière la disclosure.

---

## 4. Cadre imbriqué à supprimer

`details.insight` → `<div class="card">` : une carte **à l'intérieur** d'une
disclosure elle-même dans la colonne cockpit. Trois surfaces encadrées pour une
explication de score.

**Correction visée** : grammaire `.disclosure` livrée en tranche 1 du train
précédent — résumé, filet, contenu. Pas de carte fille.

---

## 5. Données déjà disponibles, non affichées

Le contexte hebdomadaire demandé existe côté serveur et n'est **pas** consommé
par Home :

- `TrainingPreferences.sessions_per_week` — la cadence déclarée ;
- `build_weekly_plan_for_user()` — le plan et ses contraintes non satisfaites ;
- `WeeklyPlan.unmet_constraints` — la « contrainte significative » unique.

**Aucune donnée nouvelle à inventer.** La tranche 1 est du câblage et de la
hiérarchie, pas du calcul. Le gel produit reste entier : Home consomme, ne
décide pas.

---

## 6. Risques identifiés pour l'implémentation

- **`index.html` est truffé de `style="…"` en ligne** — les retirer touche des
  tests qui épinglent le balisage ; inventorier avant d'éditer.
- **Le widget d'état du jour utilise `.segmented`** (échelles 1-5), corrigé en
  accessibilité mais dont la présentation reste à revoir.
- **Coût CI** : Home est couvert par plusieurs fichiers de tests
  (`test_home_decision_hero`, `test_ui06_home_dedup`, `test_board_behavioral`…).
  Inventaire dépôt entier obligatoire avant édition.

## Verdict du préflight

Le héros est déjà la bonne PRIMARY. Les deux vrais défauts sont **une seconde
action qui lui fait concurrence** quand l'état du jour est vide, et **un cadre
imbriqué** pour l'explication de disponibilité.

Le manque, lui, est un manque de **contexte** : Home ne dit pas où en est la
semaine par rapport à la cadence déclarée, alors que la donnée existe.

**Aucune ligne de CSS ou de gabarit n'a été modifiée.** L'implémentation reste
à faire.
