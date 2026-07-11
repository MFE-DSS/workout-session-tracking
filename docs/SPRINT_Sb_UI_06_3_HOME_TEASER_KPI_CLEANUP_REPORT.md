# Sprint Sb_UI_06.3 — Home Teaser / KPI Density Cleanup

**Statut** : 🟢 DELIVERED — pending GO commit + CI + human review
**Date** : 2026-07-11
**Cycle** : Sx_UI_06 Information Density / Dedup
**Spec** : [`docs/strategy/Sx_UI_06_INFO_DENSITY_DEDUP_SPEC.md`](strategy/Sx_UI_06_INFO_DENSITY_DEDUP_SPEC.md)
**Précondition** : `Sb_UI_06.2` HUMAN REVIEW ACCEPTED ✅ (vérifié dans le repo).

---

## 0. Feedback / contexte

Après dogfood, la home était **dense et redondante** : deux CTA de démarrage
(hero « Démarrer une séance » **et** bloc « Prochaine séance suggérée »), un
teaser readiness qui n'affichait qu'un renvoi (« détail plus bas ») **au-dessus**
du widget readiness complet, une dernière séance chargée (Ressenti + Qualité), et
3 KPI 30j **recopiés sur /progress**. Règle produit : *une information = un seul
endroit* ; la home = **cockpit de décision**, pas dashboard complet.

---

## 0bis. Brainstorming / Options / Risques / Choix retenu — sujets clivants

> Étape obligatoire. Les 10 sujets clivants du brief, tranchés (3 confirmés
> opérateur, 7 décidés logiquement selon Option A « Home = décision stricte »).

| # | Sujet clivant | Décision | Justification |
|---|---|---|---|
| 1 | CTA hero : démarrer la séance suggérée direct ou ouvrir le launcher ? | **Démarrer la reco direct** (form POST) | Une décision, 1 tap ; même contrat `POST /sessions`. |
| 2 | Supprimer « Prochaine séance suggérée » de la home ? | **Oui** | Redondant avec le nouveau CTA hero. Le détail reste au launcher. |
| 3 | Dernière séance : nom+date, ou aussi un état ? | **Nom + date compacts** | Ressenti/Qualité = analytique → session-done / /progress. |
| 4 | Teaser readiness dans le hero ou dans les readouts ? | **Retiré du hero** | Il ne portait aucune donnée (« détail plus bas ») → widget unique. |
| 5 | KPI 30j sur home ou seulement /progress ? | **Réduits à « cette sem. »** | 1 KPI décisionnel ; analytiques (score moyen, complétion 30j) → /progress. |
| 6 | Garder « Disponibilité » sur home ou renommer ? | **Conservé** (reskin/microcopy) | Signal décisionnel utile ; pas retiré. |
| 7 | Blocs legacy : reskin ou suppression ? | **Reskin / retrait ciblé** | On retire le redondant, on ne casse pas le dashboard dé-priorisé. |
| 8 | Actionnable vs analytique ? | Home = décision ; analytique → /progress | Sépare clairement les deux plans. |
| 9 | Que garder sur mobile 360×640 ? | Moins de blocs = moins de scroll | Les retraits (reco, teaser, 2 KPI, ressenti/qualité) réduisent la hauteur. |
| 10 | Différer vers Body Intelligence ? | **Deferred** | Aucune migration Body Intelligence dans ce sprint. |

### Options comparées (globale)

| Option | Description | Verdict |
|---|---|---|
| **A** | Home = décision stricte (hero CTA unique, reco au launcher, dernière compacte, KPI réduits) | ✅ **RETENU** |
| B | Home = cockpit mixte (plus de readouts) | ❌ REJETÉ — garde la redondance |
| C | Home = dashboard complet | ❌ REJETÉ — contraire à Sx_UI_06 |

### Risques / parades
| Risque | Parade |
|---|---|
| Perte de la reco (détail + alternatives) | Conservée **au launcher** (`next_session_reco.html` y reste inclus). |
| CTA hero = form POST → contrat de création | Identique à l'ancien bloc reco : `POST /sessions` + `template_slug` + `creation_source=reco_top`. Aucun nouvel endpoint. |
| Tests asservissant teaser / reco block / KPI / CTA anchor | **Ré-orientés vers la nouvelle vérité** (hero direct-start, widget readiness, launcher reco), jamais affaiblis. |
| Templates partagés non vus par le garde-fou | Surclassement `isolated → shared_code` → full sweep. |

---

## 1. Changements effectués

### 1.1 `app/templates/index.html` (MODIFIÉ)

- **Hero (cas `not open_session`)** : si `reco.top` existe → **CTA form POST**
  « Démarrer → » qui démarre le template recommandé directement
  (`template_slug` + `creation_source=reco_top`), titre = nom de la reco. Sinon
  fallback launcher (« Démarrer une séance »).
- **Teaser readiness du hero retiré** (renvoi vide « détail plus bas »).
- **Include `next_session_reco.html` retiré** de la home (plus de double CTA).
- **KPI-row réduite** à « séances cette sem. » (retrait de « score moy. » et
  « complétion 30j » → /progress ; lien « Voir analyse complète » conservé).

### 1.2 `app/templates/_partials/home_coaching_loop.html` (MODIFIÉ)

- **Dernière séance compacte** : retrait des lignes « Ressenti » / « Qualité ».

`next_session_reco.html` **non modifié** (reste inclus par le launcher).
`home.css` **non modifié** (retrait CSS non strictement nécessaire).

---

## 2. Avant / Après (home, pas de séance active)

| Surface | Avant | Après |
|---|---|---|
| CTA démarrage | hero « Démarrer une séance » (→ launcher) **+** bloc « Prochaine séance suggérée » (« Démarrer X ») | **1 CTA hero** « Démarrer → » qui lance la reco direct |
| Readiness | teaser hero (« détail plus bas ») **+** widget complet | **widget unique** |
| Dernière séance | nom + date + Ressenti + Qualité | **nom + date** |
| KPI home | cette sem. + score moy. + complétion 30j | **cette sem.** (+ lien /progress) |

Rendu réel vérifié : teaser hero absent · bloc reco absent · CTA form POST présent
· score moy./complétion 30j absents · cette sem. présent · Ressenti/Qualité absents
· lien /progress conservé.

---

## 3. Tests

### 3.1 Nouveau
- `tests/test_ui06_home_dedup.py` (NOUVEAU, 8 tests) : reco block retiré / hero
  direct-start / launcher garde la reco / teaser retiré / dernière compacte /
  KPI réduits / SSR no-JS.

### 3.2 Ré-orientés vers la nouvelle vérité (non affaiblis)
- `test_home_decision_hero.py` : CTA unique (a ou button form) · CTA no-JS
  (anchor ou POST form) · start CTA (Démarrer/Reprendre) · teaser retiré + widget présent.
- `test_recommendation_surface.py` : bloc reco déplacé au hero (home) ; phrase reco
  vérifiée sur le launcher.
- `test_library.py` : CTA accepte Démarrer / Reprendre / Nouvelle séance.

### 3.3 Résultats
- Ciblés home/reco/library + dedup : **verts** (voir §Verdict pour le broad sweep).
- ruff **543 ≤ 548** ; spec protocol vert.
- **Full sweep local** : non exécuté (test préexistant hang localement, documenté,
  absent en CI). La **CI réelle** fait le full.

---

## 4. Invariants préservés

- **Contrat de création de session inchangé** : `POST /sessions` + `template_slug`
  + `creation_source` (le CTA hero reco réutilise exactement ce contrat).
- Reco (détail + alternatives) **conservée au launcher**.
- **Aucun** changement route / service / modèle / migration / schema / Sx_32
  backend / `body_map_descriptor` / Body Intelligence / scoring / coach /
  substitution / readiness service / JS / endpoint.
- SSR / no-JS strict ; readiness non médical ; Auren Terminal cohérent.

---

## 5. Fichiers modifiés (whitelist)

| Fichier | État |
|---|---|
| `app/templates/index.html` | MODIFIÉ (hero + teaser + reco include + KPI) |
| `app/templates/_partials/home_coaching_loop.html` | MODIFIÉ (dernière compacte) |
| `tests/test_home_decision_hero.py` | MODIFIÉ (ré-orienté) |
| `tests/test_recommendation_surface.py` | MODIFIÉ (ré-orienté) |
| `tests/test_library.py` | MODIFIÉ (ré-orienté) |
| `tests/test_ui06_home_dedup.py` | NOUVEAU |
| `docs/SPRINT_Sb_UI_06_3_HOME_TEASER_KPI_CLEANUP_REPORT.md` | NOUVEAU |
| `docs/strategy/SPEC_REGISTRY.md` · `ROADMAP_AND_NEXT_STEPS.md` | MODIFIÉS |

Aucun service / modèle / migration / route / JS touché. Aucun artefact.

---

## 6. Limites / statut

- `next_session_reco.html` conservé au launcher (non touché).
- CSS `home.css` non nettoyé (classes readiness teaser désormais inutilisées ;
  inerte, cleanup ultérieur possible).
- **Body Intelligence : deferred.**

---

## 7. Next step recommandé

- **`Sb_UI_06.4`** (écrans secondaires : session done / coach report), **ou**
- reprise **Body Intelligence** maintenant que l'UI (carte exercice + Worked Area
  + home) est dé-densifiée et stabilisée.

---

## Verdict

**Verdict :** 🟢 **Sb_UI_06.3 Home density cleanup livré — une décision unique, readouts simplifiés, KPI réduits — pending GO commit + CI + human review.**

La home est désormais un **cockpit de décision** : un seul CTA (qui démarre la
séance recommandée directement), plus de bloc reco redondant, plus de teaser
readiness vide, dernière séance compacte (nom + date), KPI réduits au signal
« cette semaine » (analytique → /progress). Contrat de création de session et reco
launcher intacts ; aucun backend / route / Body Intelligence touché. Tests
ré-orientés vers la nouvelle vérité. Prêt pour GO commit ; la CI réelle fait le full sweep.
