# SPIGNOS — Body Signal Model Brainstorming

**Sprint :** `Sx Body 00 — Brainstorming & Architecture Framing`
**Branche :** `sx-body-00-brainstorming-spec`
**Date :** 2026-06-26
**Type :** SPEC-FIRST / brainstorming. **Aucun code, aucune migration, aucune dépendance.**
**Auteur de cadrage :** data architect / product architect / privacy-aware spec writer

---

## 1. Statut du document

| Champ | Valeur |
|---|---|
| Statut | ⚪ DRAFT (brainstorming) — à promouvoir en `Sx Body 01 — Signal Model Spec` |
| Portée | Cadrage conceptuel du futur module **Body Intelligence** |
| Niveau d'engagement | Aucun. Ce document **ne valide aucune implémentation**. Il prépare une spec. |
| Contraintes héritées | Hard contracts SPIGNOS (cf. `Sx_26 §`) : SQLite, deploy manuel, snapshots historiques, **ADD COLUMN ONLY**, ruff budget verrouillé, ownership utilisateur strict. |
| Interdits de ce sprint | Intégration Bodygram, intégration MediaPipe, modèle DB, migration Alembic, modification `requirements.txt` / `.env*` / `app/`. |
| Documents amont à lire | `docs/strategy/SPIGNOS_BODY_METRICS_READINESS_SPEC.md`, `docs/strategy/SPIGNOS_BODY_ENGINEERING_DASHBOARD_V1.md`, `docs/strategy/SPIGNOS_EXERCISE_SUBSTITUTION_GRAPH_SPEC_FINAL.md`, `docs/strategy/ROADMAP_AND_NEXT_STEPS.md`, `docs/strategy/SPEC_DRIVEN_ENGINEERING_PROTOCOL_v1.md`. |
| Document jumeau | `docs/strategy/SPIGNOS_BODY_INTELLIGENCE_ROADMAP.md` (roadmap des 5 lots). |

> **Avertissement central, valable pour tout le document :** Body Intelligence ne produit **aucun diagnostic médical**, **aucune inférence d'ethnie / race / attractivité / santé mentale / caractéristique protégée**. Le langage est sobre, non discriminatoire, orienté **progression esthétique actionnable**. Le terme « morphotype » n'est jamais une vérité primaire.

---

## 2. Résumé exécutif

SPIGNOS est aujourd'hui un cockpit de progression hypertrophie mobile-first (FastAPI SSR / Jinja2 / SQLite / SQLAlchemy + Alembic / Nginx / HTTPS), avec une discipline de production (backups, drift guard, smoke/deploy, ownership). Le module **Body Intelligence** vise à transformer une chaîne :

```
photos / mesures
  → signaux corporels contrôlés
  → ratios esthétiques
  → tags d'archetype physique (non médicaux)
  → recommandations training / nutrition simples
  → lien futur avec catalogue, programme, graphe de substitution
```

Le produit existant possède **déjà une base corporelle** sur laquelle s'appuyer :
- table `body_measurements` (poids, taille, tour de taille, mesures circonférences **latéralisées** comme source de vérité),
- `readiness_entries` (auto-évaluation 5 dimensions),
- le **Body Engineering Dashboard** (`GET /dashboard`) qui synthétise 5 axes scorés avec confiance et dégradation gracieuse,
- une **Signal Confidence Policy** (pas de tendance < 3 points, pas de score de zone < 2 séances, etc.).

Body Intelligence **n'est donc pas un greenfield** : c'est une couche d'interprétation explicable au-dessus de signaux déjà partiellement collectés, à étendre prudemment.

Le présent document fixe : la taxonomie des signaux (primaire / dérivé / provider raw / confirmé / recommandation générée / recommandation acceptée-ignorée), les mesures / ratios / signaux posture / archetype tags candidats, le modèle conceptuel de données, le cadrage privacy/RGPD, et un Q&A d'arbitrage de 30 entrées. Il se termine par des **décisions recommandées** (pas seulement des options) et des **acceptance criteria**.

---

## 3. Problème produit

### 3.1 Constat
L'utilisateur hypertrophie veut savoir **quoi prioriser** pour améliorer son physique visible. Aujourd'hui SPIGNOS optimise la **charge / le volume / la progression** (séances, tonnage, zones), mais ne relie pas explicitement ces efforts à une **lecture corporelle** (ratios, équilibre visuel, priorités musculaires visibles).

### 3.2 Douleur
- Les mesures existent (`body_measurements`) mais restent **descriptives**, pas **interprétées** en priorités actionnables.
- L'utilisateur ne sait pas traduire « tour de taille stable + épaules étroites » en « priorité deltoïdes latéraux / dorsaux + contrôle calorique simple ».
- Les approches concurrentes (body scan apps) sont soit **médicalisantes** (body fat clinique), soit **pseudo-scientifiques** (classement morphotype déterministe), soit **opaques** (score magique non drillable). SPIGNOS doit éviter les trois.

### 3.3 Promesse
Aider l'utilisateur à comprendre ses **priorités corporelles visibles et actionnables** pour améliorer sa progression esthétique — de façon **explicable, conservatrice, non médicale, non discriminatoire** — et **relier** ces priorités au moteur d'entraînement existant (familles musculaires → familles d'exercices → graphe de substitution).

### 3.4 Ce que ce n'est pas
Body Intelligence est un **input enrichi**, pas le produit principal. SPIGNOS reste un cockpit de progression. Body Intelligence ne remplace pas le coach, ne modifie pas automatiquement le programme (au début), et **ne vit jamais à l'intérieur du mode séance**.

---

## 4. Non-goals

| # | Non-goal | Raison |
|---|---|---|
| NG-1 | Diagnostic médical, dépistage de pathologie, « body fat médical », analyse clinique | Hors compétence, hors mandat, exposition réglementaire (données de santé). |
| NG-2 | Inférence d'ethnie, race, origine, classe sociale, attractivité sexuelle, santé mentale | Interdit éthique + RGPD (caractéristiques protégées / biométrie d'identification). |
| NG-3 | Classement déterministe ectomorphe/mésomorphe/endomorphe comme vérité centrale | Pseudo-science non gouvernable, non actionnable. |
| NG-4 | Score physique global humiliant ou non drillable | Anti-pattern produit (boîte noire, jugement du corps). |
| NG-5 | Modification automatique du programme dès le MVP | Risque de drift + casse du mode séance. Différé. |
| NG-6 | Compteur de calories / journal alimentaire complet | Hors scope ; on produit des **règles simples**, pas un food tracker. |
| NG-7 | App mobile native obligatoire au départ | SSR / PWA d'abord ; natif éventuel plus tard. |
| NG-8 | Identification biométrique de la personne (reconnaissance faciale, ré-identification) | Strictement exclu. La photo sert la **qualité de capture** et la **mesure**, jamais l'identité. |
| NG-9 | Stockage par défaut des photos | Politique par défaut = analyse puis suppression. La conservation est une exception consentie. |

---

## 5. Principes directeurs

1. **Mesures observables → ratios → interprétation explicable → recommandations.** Jamais de raccourci « type de corps → programme ».
2. **Tout signal est traçable jusqu'à sa source** (saisie manuelle, provider, calcul) et **jusqu'à la version du moteur** qui l'a produit.
3. **Privacy-by-design dès la spec**, pas après l'intégration provider. Consentement explicite, minimisation, suppression, finalité déterminée.
4. **Conservatisme des recommandations.** En cas de doute, on recommande moins et plus prudemment. Pas de promesse, pas de jugement.
5. **Explicabilité obligatoire.** Toute recommandation expose son *rationale* (quel signal, quel ratio, quelle règle, quelle version).
6. **Corrigeabilité.** L'utilisateur peut corriger une mesure. Une mesure non corrigeable devient une boîte noire — interdit.
7. **Dégradation gracieuse**, comme le dashboard existant : pas assez de données → pas de signal inventé. Réutiliser la **Signal Confidence Policy** existante.
8. **Hors-session.** Body Intelligence n'ajoute aucune complexité pendant la saisie des sets.
9. **Providers derrière interfaces.** Bodygram / MediaPipe = implémentations d'interfaces abstraites (`BodyMeasurementProvider`, `CaptureQualityProvider`), jamais des dépendances dures dans le cœur.
10. **Feature-flag par défaut OFF.** Aucun impact production tant que le flag n'est pas activé, conformément à la convention `*_enabled: bool = Field(default=False)` de `app/config.py`.
11. **Non-discrimination linguistique.** Wording strict : `aesthetic guidance`, `progression corporelle`, `priorités musculaires`, `équilibre visuel`, `posture indicative`, `tendance`, `signal non médical`.
12. **Additivité (ADD COLUMN ONLY).** Toute future table/colonne suit le contrat de migration SPIGNOS : additif, snapshot, roundtrip, drift guard.

---

## 6. Taxonomie des signaux corporels

La taxonomie distingue **six états** d'un signal. C'est le cœur conceptuel du module.

| État | Définition | Exemple | Mutable par l'utilisateur ? | Stocké ? |
|---|---|---|---|---|
| **1. Signal primaire** | Donnée directement saisie ou mesurée. | poids, taille, tour de taille, photo, mesure provider brute confirmée | Oui (saisie manuelle) | Oui |
| **2. Provider raw output** | Réponse brute non normalisée d'un provider externe. | JSON Bodygram complet, landmarks MediaPipe | Non (lecture seule) | Oui, en JSON contrôlé, minimisé, purgeable |
| **3. Mesure confirmée** | Mesure que SPIGNOS retient comme source de vérité pour les calculs. | `waist_cm = 84` confirmé après revue utilisateur | Oui (correction explicite) | Oui |
| **4. Signal dérivé** | Résultat d'un calcul déterministe sur des mesures confirmées. | `shoulder_to_waist_ratio`, `waist_trend`, `symmetry_score`, `posture_tag` | Non (recalculable) | Oui, **versionné** (recalculable à la demande) |
| **5. Recommandation générée** | Sortie du moteur de règles, horodatée + versionnée. | « priorité deltoïdes latéraux » | Non | Oui, avec `engine_version` |
| **6. Recommandation acceptée / ignorée** | Décision utilisateur sur une recommandation. | accepted / dismissed / snoozed | Oui (action utilisateur) | Oui (feedback loop) |

**Règles de flux :**
```
[provider raw output]  ──normalisation──▶  [mesure confirmée] ◀──saisie/correction── [signal primaire]
                                                  │
                                                  ▼ (calcul déterministe, versionné)
                                            [signal dérivé : ratios, posture, archetype]
                                                  │
                                                  ▼ (moteur de règles, engine_version)
                                            [recommandation générée]
                                                  │
                                                  ▼ (action utilisateur)
                                            [recommandation acceptée / ignorée]
```

**Invariants :**
- Un **signal dérivé** ne dépend QUE de **mesures confirmées** + d'une **version de règles** → toujours reproductible.
- Une **recommandation** ne dépend QUE de **signaux dérivés** + `engine_version`.
- Le **provider raw output** n'alimente jamais directement un ratio ni une recommandation : il doit d'abord devenir **mesure confirmée**.

---

## 7. Mesures corporelles candidates

Ces mesures sont **candidates**, pas validées. La table existante `body_measurements` couvre déjà une partie (latéralisé = source de vérité).

| Mesure | Clé candidate | Source possible | Déjà dans `body_measurements` ? | Sensibilité |
|---|---|---|---|---|
| Poids | `weight_kg` | manuel / balance | ✅ | faible |
| Taille | `height_cm` | manuel | (profil) | faible |
| Tour de taille | `waist_cm` | manuel / provider | ✅ | moyenne |
| Tour de poitrine | `chest_cm` | manuel / provider | ✅ | faible |
| Tour de hanches | `hip_cm` | manuel / provider | ✅ | moyenne |
| Tour de cou | `neck_cm` | manuel / provider | ✅ | faible |
| Tour de bras G/D | `arm_cm_left` / `arm_cm_right` | manuel / provider | ✅ (latéralisé) | faible |
| Tour de cuisse G/D | `thigh_cm_left` / `thigh_cm_right` | manuel / provider | ✅ (latéralisé) | faible |
| Tour de mollet | `calf_cm` | manuel / provider | ✅ | faible |
| Largeur d'épaules (biacromiale) | `shoulder_width_cm` | provider (photo) / manuel difficile | ❌ candidat | moyenne |
| Tour d'avant-bras G/D | `forearm_cm_left/right` | manuel / provider | ❌ candidat | faible |
| Body composition **indicative** (non médicale) | `bodycomp_indicative_pct` | provider (Bodygram, 2 photos) | ❌ candidat, **flagué non médical** | **élevée** |

**Doctrine source de vérité (héritée) :** les colonnes latéralisées (G/D) sont la source de vérité ; les moyennes sont des **vues dérivées**. Toute nouvelle feature d'asymétrie doit lire le brut latéralisé.

**Protocole de mesure (réutiliser l'existant) :** même moment / mêmes conditions (matin, à jeun), hebdo max pour circonférences, mètre à plat, mêmes repères, deux côtés, entrées partielles tolérées (un champ manquant ne génère pas de faux signal).

---

## 8. Ratios esthétiques candidats

Tous les ratios sont des **signaux dérivés** (état 4) : recalculables, versionnés, jamais saisis.

| Ratio | Formule candidate | Lecture (non médicale) | Confiance minimale |
|---|---|---|---|
| Épaules / taille (V-taper) | `shoulder_width_cm / waist_cm` (ou `chest_cm / waist_cm` en proxy si largeur absente) | équilibre visuel haut du corps | nécessite largeur OU chest + waist confirmés |
| Taille / hanches | `waist_cm / hip_cm` | équilibre du tronc | 2 mesures confirmées |
| Bras / avant-bras | `arm_cm / forearm_cm` | développement du bras | 2 mesures confirmées |
| Symétrie bras | `abs(arm_left - arm_right) / mean(arm)` | asymétrie latérale indicative | latéralisé requis |
| Symétrie cuisses | `abs(thigh_left - thigh_right) / mean(thigh)` | asymétrie latérale indicative | latéralisé requis |
| Haut / bas du corps | proxy `(chest+arm) vs (thigh+calf)` normalisé | dominance haut/bas indicative | ≥ 4 mesures confirmées |
| Tendance taille | régression simple sur `waist_cm` sur fenêtre 30/60/90j | tendance (stable / montant / descendant) | **≥ 3 points** (Signal Confidence Policy) |
| Tendance poids | régression simple sur `weight_kg` | tendance | **≥ 3 points** |

**Règle :** aucun ratio affiché si ses mesures sources ne franchissent pas le seuil de confiance. Réutiliser explicitement la **Signal Confidence Policy** (pas de tendance < 3 points). Les ratios sont **versionnés** : on stocke `ratio_engine_version` pour pouvoir recalculer après évolution de formule.

---

## 9. Signaux posture candidats

La posture est **indicative**, jamais médicale. Source : MediaPipe (33 landmarks) **comme outil de qualité de capture et d'observation géométrique**, pas comme diagnostic.

| Signal posture | Dérivation candidate | Lecture autorisée | Lecture INTERDITE |
|---|---|---|---|
| Inclinaison d'épaules | différence de hauteur des landmarks épaules (front) | « épaules visuellement non alignées sur la photo » | « scoliose », « déséquilibre pathologique » |
| Tilt de bassin (indicatif) | hauteur relative des landmarks hanches (front) | « bassin visuellement incliné sur la photo » | diagnostic orthopédique |
| Projection de tête (side) | position tête vs épaules (side) | « tête projetée en avant sur la photo » | « cervicalgie », pronostic |
| Symétrie globale (indicative) | écart bilatéral agrégé des landmarks | `posture_balance_priority` (tag actionnable) | jugement médical |

**Cadre strict :**
- Tout signal posture est suffixé `_indicative` et accompagné du disclaimer « observation visuelle non médicale, sur la base d'une photo unique ».
- La posture **ne génère jamais** d'exercice correctif médical ; au plus, une **priorité d'équilibre** (`posture_balance_priority`) reliée à des familles musculaires.
- MediaPipe sert d'abord à valider que la photo est **exploitable** (cf. §15).

---

## 10. Archetype tags candidats

Un archetype SPIGNOS est un **tag dérivé, actionnable et explicable** — pas une catégorie pseudo-scientifique, pas un jugement.

**Tags candidats (actionnables) :**

| Tag | Déclencheur candidat | Priorité induite |
|---|---|---|
| `v_taper_priority` | ratio épaules/taille faible + tendance taille stable/montante | deltoïdes latéraux, dorsaux, contrôle calorique simple |
| `upper_body_dominant` | ratio haut/bas élevé | équilibrage bas du corps |
| `lower_body_lagging` | ratio haut/bas élevé (vu côté bas) | quadriceps / ischios / fessiers |
| `waist_control_priority` | tendance taille montante | contrôle calorique simple + suivi taille |
| `posture_balance_priority` | asymétrie posturale indicative | travail d'équilibre / unilatéral |
| `arm_development_priority` | ratio bras/avant-bras ou bras/épaules faible | biceps / triceps |
| `symmetry_priority_left` / `_right` | asymétrie latérale > seuil | travail unilatéral du côté faible |

**Tags INTERDITS (jamais produits) :** `alpha physique`, `ethnic type`, `genetic winner`, `bad body`, tout label de valeur humaine, esthétique sexuelle, ou catégorie protégée.

**Règles :**
- Un tag est toujours **dérivé de mesures/ratios confirmés** et porte son *rationale* + sa version de règles.
- Le mot « archetype » est un **tag explicatif**, jamais une vérité déterministe ni un pré-requis de programme.
- Un tag est **transitoire** : il évolue avec les mesures. On versionne et on horodate.

---

## 11. Recommandations training candidates

Le module **ne code jamais d'exercice en dur**. Il pointe vers des **familles musculaires** et des **intentions**, que le moteur d'entraînement (et plus tard le **graphe de substitution**) traduit en exercices.

**Chaîne de liaison :**
```
archetype tag  →  muscle families  →  exercise families / patterns  →  (graphe de substitution) exercices concrets
```

**Exemple :**
```
tag: v_taper_priority
  → muscle families: lateral_delts, lats
  → exercise families: lateral_raise, pulldown, pullup, row
  → graphe de substitution: propose les exercices disponibles équivalents
```

| Tag | Muscle families candidates | Exercise families candidates |
|---|---|---|
| `v_taper_priority` | `lateral_delts`, `lats` | `lateral_raise`, `pulldown`, `pullup`, `row` |
| `lower_body_lagging` | `quads`, `hamstrings`, `glutes` | `squat`, `leg_press`, `hip_hinge`, `lunge` |
| `arm_development_priority` | `biceps`, `triceps` | `curl`, `pushdown`, `overhead_extension` |
| `posture_balance_priority` | `rear_delts`, `mid_back` | `face_pull`, `rear_delt_fly`, `row` |
| `symmetry_priority_left/right` | côté faible identifié | variantes **unilatérales** des familles concernées |

**Garde-fous :**
- **Pas de modification automatique du programme** au début : on **propose** des priorités, l'utilisateur décide.
- La recommandation pointe vers une **famille / intention**, jamais un exercice figé → compatible avec le graphe de substitution (qui distingue déjà *prévu* / *réalisé* et préserve l'historique).
- Conservatisme : on propose 1–2 priorités max, pas une refonte.

---

## 12. Recommandations nutrition simples

**Pas de compteur de calories, pas de menus, pas de journal alimentaire.** Uniquement des **règles simples et conservatrices**, non médicales.

| Recommandation candidate | Forme | Garde-fou |
|---|---|---|
| Protéines | cible en `g/kg` de poids de corps (fourchette simple) | pas de prescription médicale, fourchette large |
| Calories | maintenance estimée ± delta simple (léger surplus / léger déficit selon objectif déclaré) | estimation, jamais une « ordonnance » |
| Aliments | priorité aux aliments simples / peu transformés (pivots alimentaires) | pas de liste interdite stigmatisante |
| Suivi | surveiller **poids + tour de taille** comme boucle de contrôle | réutilise `body_measurements` existant |

**Style :** « règle de 3 » et **pivots alimentaires**, jamais de menu imposé. Toute recommandation nutrition porte un disclaimer « non médical, indicatif » et reste désactivable.

---

## 13. Modèle conceptuel de données

> ⚠️ **Conceptuel uniquement.** Aucune table, aucune colonne, aucune migration n'est créée dans ce sprint. Ceci décrit l'intention pour `Sx Body 01` / `Sb Body 01+`.

**Entités conceptuelles (futures) :**

| Entité conceptuelle | Rôle | État de signal dominant | Notes |
|---|---|---|---|
| `body_measurement` (existe déjà) | mesures primaires / confirmées | primaire + confirmé | latéralisé = vérité ; **réutiliser**, ne pas dupliquer |
| `body_capture` | métadonnée d'une capture (photo/scan), **pas la photo elle-même par défaut** | primaire | porte consentement, politique de rétention, source |
| `body_provider_raw` | réponse brute provider, JSON contrôlé | provider raw output | minimisé, traçable, **purgeable** |
| `body_derived_signal` | ratios, posture tags, archetype tags | dérivé | versionné (`signal_engine_version`), recalculable |
| `body_recommendation` | recommandations générées | recommandation générée | porte `engine_version`, *rationale*, horodatage |
| `body_recommendation_feedback` | accepté / ignoré / snoozé | recommandation acceptée/ignorée | boucle de feedback |
| `body_consent` | consentements (analyse photo, provider externe, rétention) | métadonnée légale | finalité + retrait + horodatage |

**Principes de modélisation :**
- **ADD COLUMN ONLY** : toute extension est additive, conforme au contrat de migration SPIGNOS (snapshot, linter, roundtrip, drift guard).
- **Séparation stricte** raw (provider) ↔ confirmé (SPIGNOS) : un champ JSON contrôlé pour le raw, des colonnes typées pour le confirmé.
- **Versionnement** des signaux dérivés et des recommandations (`*_engine_version`), à l'image de `overload_engine_version` déjà introduit (`Sb_30.3`).
- **Purge** : chaque entité sensible (capture, provider_raw, derived, recommendation, measurement) doit être supprimable par l'utilisateur (cf. §14, Q27).
- **Pas de stockage photo par défaut** : `body_capture` référence une politique de rétention ; le binaire photo n'est conservé que sous consentement explicite (et chiffré si conservé).

---

## 14. Privacy, consentement et conservation

**Contexte réglementaire (RGPD) :** les photos corporelles, mensurations, body composition et posture peuvent relever de catégories sensibles. Le RGPD interdit en principe le traitement des données biométriques d'identification et des données de santé, **sauf exception** (notamment consentement explicite pour des finalités déterminées). SPIGNOS adopte donc une posture **privacy-by-design** dès la spec.

**Exigences :**

| Exigence | Décision de cadrage |
|---|---|
| **Consentement explicite** | Requis avant toute analyse de photo corporelle et tout envoi à un provider externe. Finalité claire, granulaire (analyse / provider externe / rétention), retirable à tout moment. |
| **Minimisation** | On ne collecte que le nécessaire. Provider raw stocké minimisé. Pas de photo conservée par défaut. Pas de donnée d'identité. |
| **Finalité déterminée** | Mesures & ratios pour guidance esthétique. **Jamais** identification, profilage protégé, ou usage secondaire non consenti. |
| **Politiques de rétention photo** | Trois politiques supportées : (a) **analyse puis suppression immédiate** (défaut recommandé), (b) **conservation limitée** (durée bornée), (c) **conservation explicite utilisateur**. |
| **Chiffrement** | Si conservation : chiffrement au repos obligatoire. Sinon, préférer analyse-puis-suppression. |
| **Droit à la suppression** | L'utilisateur peut supprimer : photos, provider raw outputs, assessments, measurements, recommendations, consents. Suppression réelle (pas soft-delete masqué). |
| **Transparence provider** | Aucun envoi à Bodygram (ou tout tiers) sans mention explicite et consentement préalable. |
| **Protection des clés** | Clé API provider **jamais côté client** : token court généré côté serveur (cf. §15). |
| **Pas de catégorie protégée** | Aucune inférence d'ethnie/race/santé/attractivité. Garde linguistique au niveau du moteur de wording. |

**Posture par défaut recommandée :** analyse-puis-suppression de la photo, consentement granulaire OFF par défaut, providers OFF par défaut (feature flags).

---

## 15. Intégrations futures : MediaPipe / Bodygram

> Ces intégrations sont **préparées conceptuellement**, **pas codées** dans ce sprint. Elles vivront derrière des interfaces et des feature flags.

### 15.1 MediaPipe — d'abord un outil de **qualité de capture**
MediaPipe Pose Landmarker détecte les landmarks du corps (image / vidéo / live), renvoie des coordonnées image + world et une segmentation optionnelle (~33 landmarks, optimisé fitness on-device). Dans SPIGNOS, rôle **MVP** :
- vérifier le cadrage,
- vérifier la présence d'**une seule personne**,
- vérifier la pose **front / side**,
- détecter si la photo est **exploitable**,
- produire un **score de qualité d'image**.

**Pas** de recommandation hypertrophie directe depuis MediaPipe. Interface candidate : `CaptureQualityProvider`.

### 15.2 Bodygram — option de **mesure** future
Bodygram peut estimer des mesures corporelles et générer un avatar 3D à partir de stats ; l'ajout de **deux photos (front + right side)** débloque body composition et posture data. Le **Headless SDK** permet une UI custom, avec un **serveur** nécessaire pour générer un **token court** et **protéger la clé API**.

Dans SPIGNOS : Bodygram = source possible de **provider raw output** → normalisé en **mesures confirmées**. Interface candidate : `BodyMeasurementProvider`. Intégration serveur sécurisée, consentement obligatoire, body composition strictement **indicative non médicale**.

### 15.3 Règle d'isolation
Les deux providers sont des **implémentations d'interfaces**, derrière feature flags OFF par défaut :
```
BODY_ASSESSMENT_ENABLED=false
BODY_PHOTO_CAPTURE_ENABLED=false
BODY_PROVIDER_BODYGRAM_ENABLED=false
```
(convention `app/config.py` : `*_enabled: bool = Field(default=False)`).

---

## 16. Q&A for product/technical arbitration

> 30 entrées d'arbitrage. Chaque réponse est une **décision de cadrage recommandée**, pas une simple option.

### Produit
**Q1. Quelle est la promesse exacte du module Body Intelligence ?**
Aider l'utilisateur à comprendre ses priorités corporelles **visibles et actionnables** pour améliorer sa progression esthétique, **sans diagnostic médical**.

**Q2. Est-ce qu'on fait une app de body scan ?**
Non. SPIGNOS reste un cockpit de progression hypertrophie. Le body scan est un **input**, pas le produit principal.

**Q3. Est-ce que le module remplace le coach ?**
Non. Il produit des recommandations **simples, explicables, conservatrices**.

**Q4. Classe-t-on l'utilisateur en ecto/méso/endomorphe ?**
Non comme vérité centrale. « Archetype » reste un **tag explicatif dérivé** de mesures/ratios, jamais une pseudo-science déterministe.

**Q5. Qu'est-ce qu'un bon archetype SPIGNOS ?**
Un tag **actionnable** : `v_taper_priority`, `upper_body_dominant`, `lower_body_lagging`, `waist_control_priority`, `posture_balance_priority`, `arm_development_priority`. **Jamais** `alpha physique`, `ethnic type`, `genetic winner`, `bad body`.

### Data model
**Q6. Différence mesure brute / mesure confirmée ?**
La brute vient du provider ou de l'utilisateur ; la **confirmée** est celle que SPIGNOS utilise pour ratios et recommandations.

**Q7. Stocke-t-on la réponse brute du provider ?**
Oui, dans un **champ JSON contrôlé**, minimisé, avec traçabilité de source et **purge** possible.

**Q8. Stocke-t-on les photos ?**
Optionnel. Trois politiques : analyse-puis-suppression immédiate (défaut), conservation limitée, conservation explicite utilisateur.

**Q9. Qu'est-ce qu'un signal primaire ?**
Une donnée **directement saisie ou mesurée** : poids, taille, tour de taille, photo, mesure provider.

**Q10. Qu'est-ce qu'un signal dérivé ?**
Un **calcul** : shoulder/waist ratio, waist trend, symmetry score, posture tag, archetype tag.

**Q11. Stocke-t-on les ratios ?**
Oui pour préserver l'historique interprétable, **mais** recalculables et **versionnés**.

**Q12. Versionne-t-on le moteur de recommandation ?**
Oui. Toute recommandation sait avec quelle **version de règles** elle a été générée (cf. précédent `overload_engine_version`).

### UX
**Q13. Peut-on lancer Body Intelligence depuis l'app SSR actuelle ?**
Oui pour le **Manual Body Profile** et la revue des résultats. Pour la capture photo avancée : compatibilité progressive **mobile web / PWA**, puis natif éventuel.

**Q14. UX minimale du premier build ?**
Profil corporel manuel → poids / taille / tour de taille → quelques mesures optionnelles → photos optionnelles **sans analyse auto** → résumé simple.

**Q15. À quoi sert MediaPipe dans le MVP ?**
Vérifier la **qualité de capture** : cadrage, orientation, pose, personne unique, landmarks exploitables.

**Q16. À quoi sert Bodygram plus tard ?**
Produire des **mesures**, avatar, body composition **indicative** et posture à partir de stats + 2 photos, via une **intégration serveur sécurisée**.

**Q17. L'utilisateur peut-il corriger les mesures ?**
Oui. Une mesure non corrigeable devient une **boîte noire** — interdit.

**Q18. Affiche-t-on un score physique global ?**
Seulement s'il est **drillable et explicable**. **Aucune** note humiliant le corps.

### Recommandations training
**Q19. Comment relier Body Intelligence au catalogue d'exercices ?**
Via **familles musculaires, patterns et priorités**, pas via des exercices codés en dur. Ex. `v_taper_priority → lateral_delts, lats → lateral_raise, pulldown, pullup, row`.

**Q20. Le module modifie-t-il automatiquement le programme ?**
Non au début. Il **propose** priorités et recommandations ; la modification auto vient plus tard.

**Q21. Comment éviter de casser le mode séance ?**
Body Intelligence vit **hors session**. Il n'injecte aucune complexité pendant la saisie des sets.

**Q22. Comment relier au futur graphe de substitution ?**
Une recommandation pointe vers une **famille / intention** ; le graphe de substitution propose ensuite les exercices adaptés (en préservant *prévu* / *réalisé* et l'historique).

### Nutrition
**Q23. Fait-on un compteur de calories ?**
Non dans ce chantier. On produit des **règles simples**.

**Q24. Quelle nutrition minimale recommander ?**
Protéines en `g/kg` ; calories maintenance ± delta simple ; priorité aliments simples ; surveillance poids + tour de taille.

**Q25. Donne-t-on des menus ?**
Pas au départ. On donne des **règles de 3** et des **pivots alimentaires**.

### Privacy / légal
**Q26. Quel consentement prévoir ?**
Consentement **explicite** pour analyse de photos corporelles et données sensibles, **finalité claire**, **retrait possible**, granularité (analyse / provider / rétention).

**Q27. Que doit pouvoir supprimer l'utilisateur ?**
Photos, raw provider outputs, assessments, measurements, recommendations (et consents).

**Q28. Peut-on envoyer les photos à Bodygram sans prévenir ?**
Non. Le provider externe doit être **explicitement mentionné** et consenti.

**Q29. Faut-il chiffrer les images ?**
Oui **si conservation**. Sinon, préférer **analyse puis suppression**.

**Q30. Comment éviter une dette réglementaire ?**
**Privacy-by-design dès la spec**, pas après l'intégration.

---

## 17. Risques

| # | Risque | Gravité | Mitigation |
|---|---|---|---|
| R-1 | Glissement vers le diagnostic médical | Élevée | Wording verrouillé, suffixes `_indicative`, disclaimers, revue à chaque release de wording. |
| R-2 | Inférence accidentelle de caractéristique protégée | Élevée | Le moteur ne traite que mesures/ratios/posture ; aucune feature ethnie/race/visage/identité. |
| R-3 | Dette RGPD (photos, provider externe) | Élevée | Privacy-by-design, consentement granulaire, suppression, défaut analyse-puis-suppression, flags OFF. |
| R-4 | Recommandation humiliante / jugement du corps | Moyenne-haute | Conservatisme, score drillable, ban des tags de valeur, revue linguistique. |
| R-5 | Boîte noire (mesures non corrigeables, signaux non explicables) | Moyenne | Corrigeabilité obligatoire, *rationale* obligatoire, versionnement. |
| R-6 | Casse du mode séance | Moyenne | Body Intelligence hors-session, 0 complexité dans la saisie des sets. |
| R-7 | Indisponibilité provider | Moyenne | Interfaces + dégradation : fallback manuel, pas de blocage du parcours. |
| R-8 | Mesures incohérentes (provider ou saisie) | Moyenne | Bornes de plausibilité, demande de confirmation, pas de recommandation sur données aberrantes. |
| R-9 | Drift de modèle / formules non reproductibles | Moyenne | Versionnement des signaux dérivés et recommandations, recalcul déterministe. |
| R-10 | Conflits de migration avec autres chantiers | Moyenne | `Sb Body 01` crée les tables de base ; autres lots partent après son merge (cf. roadmap). |
| R-11 | Sur-collecte de données | Moyenne | Minimisation, photo non stockée par défaut, raw minimisé. |
| R-12 | Faux signaux sur données partielles | Faible-moyenne | Réutiliser la Signal Confidence Policy (seuils de points/séances). |

---

## 18. Décisions recommandées

| # | Décision | Verdict recommandé |
|---|---|---|
| D-1 | Posture produit | Body Intelligence = **couche d'interprétation hors-session**, input enrichi, pas le produit principal. ✅ |
| D-2 | Morphotype | « archetype » = **tag dérivé actionnable**, jamais vérité primaire. ✅ |
| D-3 | Réutilisation | **Étendre** `body_measurements` / readiness / dashboard existants, ne pas dupliquer. ✅ |
| D-4 | Taxonomie | Adopter les **6 états** (primaire / provider raw / confirmé / dérivé / recommandation générée / acceptée-ignorée). ✅ |
| D-5 | Photos | Défaut **analyse-puis-suppression** ; conservation = exception consentie + chiffrée. ✅ |
| D-6 | Providers | Derrière interfaces `BodyMeasurementProvider` / `CaptureQualityProvider`, **flags OFF par défaut**. ✅ |
| D-7 | Versionnement | Tout signal dérivé et toute recommandation portent une `engine_version`. ✅ |
| D-8 | Modification programme | **Manuelle** au début (proposition), pas d'auto-modif. ✅ |
| D-9 | Liaison training | Recommandations → **familles musculaires / intentions** → graphe de substitution. Jamais d'exercice codé en dur. ✅ |
| D-10 | Nutrition | **Règles simples** uniquement (protéines g/kg, calories ±, pivots), pas de compteur ni menus. ✅ |
| D-11 | Ordre de build | `Sb Body 01` (Manual Profile, crée tables de base) avant tout provider. ✅ |
| D-12 | Migration | **ADD COLUMN ONLY**, snapshot, drift guard, conformité contrat SPIGNOS. ✅ |

---

## 19. Questions ouvertes (OQ)

| OQ | Question | À trancher en |
|---|---|---|
| OQ-1 | Largeur d'épaules : mesurable manuellement de façon fiable, ou réservée au provider ? | `Sx Body 01` |
| OQ-2 | Fenêtres de tendance corporelle : 30/60/90j alignées sur le dashboard, ou spécifiques ? | `Sx Body 01` |
| OQ-3 | Seuils d'asymétrie (% au-delà duquel un tag symétrie se déclenche) ? | `Sb Body 04` |
| OQ-4 | Politique de rétention par défaut : suppression immédiate stricte, ou fenêtre courte par défaut ? | `Sx Body 01` / privacy model |
| OQ-5 | Body composition Bodygram : exposée à l'utilisateur ou conservée interne (trop sensible) ? | `Sb Body 03` |
| OQ-6 | Granularité du consentement : un seul consentement global ou trois (analyse / provider / rétention) ? | privacy model |
| OQ-7 | Le tag archetype est-il visible à l'utilisateur ou seulement le *rationale* + priorités ? | `Sb Body 04` |
| OQ-8 | Body Intelligence dans le dashboard existant (6ᵉ axe) ou page dédiée `/body` ? | `Sx Body 01` |

---

## 20. Acceptance criteria

### Sprint is accepted if…
- [ ] **2 documents** Markdown propres sont créés : ce document + `SPIGNOS_BODY_INTELLIGENCE_ROADMAP.md`.
- [ ] **0 migration**, **0 modification `app/`**, **0 modification `requirements.txt` / `.env*`**, **0 dépendance** ajoutée.
- [ ] Le modèle conceptuel distingue clairement **primaire / dérivé / provider raw / confirmé / recommandation générée / acceptée-ignorée**.
- [ ] Une **roadmap claire** des 5 lots est fournie (doc jumeau).
- [ ] Un **Q&A complet** (≥ 25 entrées — ici **30**) est présent.
- [ ] Une **stratégie de branches / merge** est documentée (doc jumeau).
- [ ] Un **cadrage privacy explicite** (consentement, minimisation, suppression, RGPD) est présent.
- [ ] **Aucun** diagnostic médical, **aucune** inférence ethnie/race/attractivité/santé/caractéristique protégée.
- [ ] « morphotype » **n'est pas** une vérité primaire.

### Sprint is rejected if…
- [ ] Une intégration **Bodygram** est codée.
- [ ] **MediaPipe** est ajouté directement (code/dépendance).
- [ ] `requirements.txt` est modifié.
- [ ] Une **migration** est créée.
- [ ] Un **diagnostic médical** est écrit.
- [ ] Des **inférences ethniques / raciales** (ou autre caractéristique protégée) sont proposées.
- [ ] « morphotype » est utilisé comme **vérité principale**.
- [ ] Consentement / suppression / minimisation sont **oubliés**.
