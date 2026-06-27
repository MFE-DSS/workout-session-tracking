# SPIGNOS — Body Signal Model Spec

**Sprint :** `Sx Body 01 — Body Signal Model Spec`
**Branche :** `sx-body-01-signal-model-spec`
**Date :** 2026-06-26
**Type :** SPEC-ONLY. **0 runtime, 0 migration, 0 dépendance, 0 provider.**
**Promotion de :** `docs/strategy/SPIGNOS_BODY_SIGNAL_MODEL_BRAINSTORMING.md` (`Sx Body 00`)
**Documents jumeaux :** `SPIGNOS_BODY_PRIVACY_AND_CONSENT_SPEC.md`, `SPIGNOS_BODY_MANUAL_PROFILE_BUILD_SPEC.md`

---

## 0. Contrat spec-driven

| Champ | Valeur |
|---|---|
| **Context** | Transformer le brainstorming `Sx Body 00` en spec technique précise, prête à guider `Sb Body 01 — Manual Body Profile`. |
| **Existing repo constraints** | FastAPI SSR / Jinja2 / SQLite / SQLAlchemy + Alembic. Hard contracts : **ADD COLUMN ONLY**, snapshot + drift guard + roundtrip, ruff budget verrouillé, ownership utilisateur (`user_id` + `ondelete=CASCADE`), deploy manuel. `BodyMeasurement` existe déjà (`app/models/measurement.py`, table `body_measurements`). `height_cm` existe sur `users`. Mesures écrites via `app/services/measurements.py`, route `/physique` (`app/routers/pages.py:478`). Export via `/export/sessions.{json,csv}`. **Aucun modèle de consentement n'existe.** |
| **Branch name** | `sx-body-01-signal-model-spec` |
| **Strict scope** | Spec du modèle de signal + mesures MVP + ratios MVP + recommandations MVP. |
| **Files allowed** | `docs/strategy/SPIGNOS_BODY_SIGNAL_MODEL_SPEC.md`, `docs/strategy/SPIGNOS_BODY_PRIVACY_AND_CONSENT_SPEC.md`, `docs/strategy/SPIGNOS_BODY_MANUAL_PROFILE_BUILD_SPEC.md`. |
| **Files forbidden** | `app/**`, `migrations/**`, `requirements.txt`, `pyproject.toml`, `.env*`, `deploy/**`, `scripts/**`. |
| **Required inspection** | ✅ faite : `app/models/measurement.py`, `app/models/user.py`, `app/routers/pages.py`, `app/routers/export.py`, `app/services/measurements.py`, brainstorming + roadmap Body. |
| **Data model impact** | **Conceptuel uniquement.** Aucune table/colonne créée. Définit ce que `Sb Body 01` devra ajouter en additif. |
| **Privacy impact** | Délégué à `SPIGNOS_BODY_PRIVACY_AND_CONSENT_SPEC.md`. |
| **Tests / checks** | Doc-only ; reviewable sans exécuter l'app (cf. §6). |
| **Acceptance criteria** | cf. §7. |
| **Rejection criteria** | cf. §8. |
| **Handoff report** | cf. §9. |

> **Garde-fous produit (valables partout) :** aucun diagnostic médical, aucune inférence de caractéristique protégée (ethnie/race/attractivité/santé mentale), aucun score humiliant, « morphotype » jamais vérité primaire. Wording : *aesthetic guidance / progression corporelle / priorités musculaires / équilibre visuel / posture indicative / tendance / signal non médical*.

---

## 1. Signal model

Le module manipule **7 états de signal**. Identifiants canoniques (machine) :

```text
primary_input
provider_raw_output
confirmed_measurement
derived_ratio
generated_recommendation
accepted_recommendation
ignored_recommendation
```

### 1.1 `primary_input`
| Aspect | Définition |
|---|---|
| **Définition** | Donnée brute saisie par l'utilisateur (ou poussée par un device). Avant validation/confirmation. |
| **Source** | Saisie manuelle (`/physique`), futur device/balance. |
| **Persistance future** | Stockée telle quelle (valeur + unité + horodatage + source). Pour le MVP manuel, `primary_input` confirmé == `confirmed_measurement` (pas d'étape provider intermédiaire). |
| **Confiance** | Moyenne : dépend de la rigueur de saisie. Bornée par les min/max de plausibilité (§2). |
| **Correction utilisateur** | Oui, toujours. |
| **Usage analytics** | Aucun direct : ne nourrit jamais un ratio sans devenir `confirmed_measurement`. |
| **Risques** | Saisie aberrante, mauvaise unité, fautes de frappe → mitigés par bornes + confirmation. |

### 1.2 `provider_raw_output`
| Aspect | Définition |
|---|---|
| **Définition** | Réponse brute non normalisée d'un provider externe (Bodygram, MediaPipe). **Hors scope `Sb Body 01`** ; défini ici pour fermer le modèle. |
| **Source** | Provider externe (futur, flagué). |
| **Persistance future** | Champ JSON contrôlé, **minimisé**, traçable (provider, version, horodatage), **purgeable**. |
| **Confiance** | Inconnue tant que non normalisée. Jamais utilisée telle quelle. |
| **Correction utilisateur** | Non (lecture seule). L'utilisateur agit sur la `confirmed_measurement` dérivée. |
| **Usage analytics** | Aucun direct. Doit être normalisé → `confirmed_measurement`. |
| **Risques** | Donnée sensible, dépendance externe, RGPD. Mitigation : consentement + minimisation + purge (privacy spec). |

### 1.3 `confirmed_measurement`
| Aspect | Définition |
|---|---|
| **Définition** | Mesure retenue comme **source de vérité** SPIGNOS pour les calculs. |
| **Source** | `primary_input` confirmé, ou normalisation d'un `provider_raw_output`. |
| **Persistance future** | Colonnes typées (réutilise/étend `body_measurements`). Latéralisé = source de vérité ; moyennes = vues dérivées. |
| **Confiance** | Élevée (validée). Soumise aux seuils de la **Signal Confidence Policy** pour les tendances. |
| **Correction utilisateur** | Oui. Une mesure non corrigeable = boîte noire (interdit). |
| **Usage analytics** | Seul input autorisé des `derived_ratio`. |
| **Risques** | Édition de l'historique → tracer `created_at`/`updated_at`. |

### 1.4 `derived_ratio`
| Aspect | Définition |
|---|---|
| **Définition** | Calcul déterministe sur des `confirmed_measurement` (ratios, tendances, tags d'archetype). |
| **Source** | Moteur de ratios (pur, sans I/O), `ratio_engine_version`. |
| **Persistance future** | Optionnellement matérialisé pour l'historique, mais **toujours recalculable** + **versionné** (`ratio_engine_version`). |
| **Confiance** | Conditionnée à la présence + qualité des inputs (fallback si manquant, §3). |
| **Correction utilisateur** | Non (recalculable). L'utilisateur corrige les mesures sources. |
| **Usage analytics** | Input des `generated_recommendation` et de l'UI de synthèse. |
| **Risques** | Drift de formule → mitigé par versionnement et recalcul déterministe. |

### 1.5 `generated_recommendation`
| Aspect | Définition |
|---|---|
| **Définition** | Sortie du moteur de règles : priorité training / règle nutrition simple, avec *rationale*. |
| **Source** | Moteur de recommandation (pur), `recommendation_engine_version`. |
| **Persistance future** | Stockée horodatée + versionnée + *rationale* (quel signal/ratio/règle). |
| **Confiance** | Conservatrice : pas de reco sur données insuffisantes/aberrantes. |
| **Correction utilisateur** | Non (mais peut être acceptée/ignorée — états suivants). |
| **Usage analytics** | Mesure du taux d'acceptation, calibrage futur. |
| **Risques** | Reco humiliante / promesse → bannies par wording + conservatisme. |

### 1.6 `accepted_recommendation`
| Aspect | Définition |
|---|---|
| **Définition** | Recommandation explicitement acceptée par l'utilisateur. |
| **Source** | Action utilisateur. |
| **Persistance future** | Lien vers `generated_recommendation` + horodatage. |
| **Confiance** | N/A (fait utilisateur). |
| **Correction utilisateur** | Oui (peut basculer accepté/ignoré). |
| **Usage analytics** | Boucle de feedback (signal positif). |
| **Risques** | Interprétation comme consentement médical → non : c'est un choix de priorité, pas un acte de santé. |

### 1.7 `ignored_recommendation`
| Aspect | Définition |
|---|---|
| **Définition** | Recommandation explicitement ignorée / snoozée / rejetée. |
| **Source** | Action utilisateur. |
| **Persistance future** | Lien + raison optionnelle + horodatage. |
| **Confiance** | N/A. |
| **Correction utilisateur** | Oui. |
| **Usage analytics** | Boucle de feedback (signal négatif), évite de re-proposer en boucle. |
| **Risques** | Sur-sollicitation → respecter snooze, pas de relance agressive. |

### 1.8 Invariants de flux
```
primary_input ──confirm──▶ confirmed_measurement ◀──normalize── provider_raw_output
                                   │
                                   ▼ (ratio_engine_version)
                             derived_ratio
                                   │
                                   ▼ (recommendation_engine_version)
                          generated_recommendation
                                   │
                         ┌─────────┴─────────┐
                         ▼                   ▼
              accepted_recommendation   ignored_recommendation
```
- `derived_ratio` ne dépend QUE de `confirmed_measurement` + `ratio_engine_version`.
- `generated_recommendation` ne dépend QUE de `derived_ratio` + `recommendation_engine_version`.
- `provider_raw_output` ne nourrit JAMAIS directement un ratio ou une reco.

### 1.9 Versionnement du moteur (verrou)
Deux versions distinctes, à l'image de `overload_engine_version` (`Sb_30.3`) :
- `ratio_engine_version` — formules des `derived_ratio`.
- `recommendation_engine_version` — règles des `generated_recommendation`.

Toute valeur dérivée/recommandée stocke la version qui l'a produite → reproductibilité et anti-drift.

---

## 2. Mesures manuelles MVP (`Sb Body 01`)

> **Réconciliation schéma (critique).** Les noms canoniques demandés diffèrent des colonnes réelles. Règle : **réutiliser l'existant** (pas de renommage — `ADD COLUMN ONLY` interdit aussi les renommages destructifs), **ajouter en additif** ce qui manque. `bodyweight_kg` est un **alias canonique** de la colonne réelle `weight_kg`.

| Canonique (MVP) | Colonne réelle / cible | Unité | Min–Max plausible | Latéralisé | Correction | Fréquence | Statut | Usage ratios |
|---|---|---|---|---|---|---|---|---|
| `height_cm` | **`users.height_cm`** (existe, Integer) | cm | 120–230 | non | oui (profil) | quasi-statique | ♻️ reuse | `waist_to_height_ratio` |
| `bodyweight_kg` | `body_measurements.weight_kg` (existe) | kg | 30–300 | non | oui | quotidien OK | ♻️ reuse | tendance poids, nutrition |
| `waist_cm` | `body_measurements.waist_cm` (existe) | cm | 40–200 | non | oui | hebdo max | ♻️ reuse | shoulder/waist, waist/height, chest/waist, tendance taille |
| `neck_cm` | `body_measurements.neck_cm` (existe) | cm | 25–60 | non | oui | hebdo max | ♻️ reuse | (réserve) |
| `chest_cm` | `body_measurements.chest_cm` (existe) | cm | 60–160 | non | oui | hebdo max | ♻️ reuse | chest/waist |
| `shoulder_width_cm` | **NOUVELLE colonne** `shoulder_width_cm` | cm | 30–60 | non | oui | hebdo max | ➕ additif | shoulder/waist |
| `upper_arm_left_cm` | `body_measurements.arm_cm_left` (existe) | cm | 20–60 | **oui (G)** | oui | hebdo max | ♻️ reuse | arm_symmetry |
| `upper_arm_right_cm` | `body_measurements.arm_cm_right` (existe) | cm | 20–60 | **oui (D)** | oui | hebdo max | ♻️ reuse | arm_symmetry |
| `thigh_left_cm` | `body_measurements.thigh_cm_left` (existe) | cm | 30–90 | **oui (G)** | oui | hebdo max | ♻️ reuse | thigh_symmetry, upper/lower |
| `thigh_right_cm` | `body_measurements.thigh_cm_right` (existe) | cm | 30–90 | **oui (D)** | oui | hebdo max | ♻️ reuse | thigh_symmetry, upper/lower |
| `hip_cm` | `body_measurements.hip_cm` (existe) | cm | 60–180 | non | oui | hebdo max | ♻️ reuse | (réserve waist/hip) |
| `calf_left_cm` | **NOUVELLE colonne** `calf_cm_left` | cm | 20–60 | **oui (G)** | oui | hebdo max | ➕ additif | upper/lower (réserve) |
| `calf_right_cm` | **NOUVELLE colonne** `calf_cm_right` | cm | 20–60 | **oui (D)** | oui | hebdo max | ➕ additif | upper/lower (réserve) |

**Obligatoires / quasi-obligatoires :** `height_cm`, `bodyweight_kg`, `waist_cm`. **Toutes les autres optionnelles.** Entrées partielles tolérées : un champ manquant ne génère pas de faux signal.

**Décisions schéma :**
- **D-S1 — `height_cm` reste sur `users`** (réutilisé), pas dupliqué dans `body_measurements`.
- **D-S2 — colonnes additives `Sb Body 01`** : `shoulder_width_cm`, `calf_cm_left`, `calf_cm_right` (Float nullable). **ADD COLUMN ONLY**.
- **D-S3 — `calf_cm` (legacy single) conservé** en lecture (back-compat) ; les nouvelles saisies écrivent les colonnes latéralisées. Ne pas supprimer (`ADD COLUMN ONLY`).
- **D-S4 — pas de `bodyweight_kg` physique** : c'est un alias documentaire de `weight_kg`.

**OQ-S1 :** `shoulder_width_cm` est-il fiable en mesure manuelle (biacromiale au mètre) ? → si non fiable, le marquer « best-effort, faible confiance » et privilégier `chest_cm` comme proxy V-taper. (À trancher avant `Sb Body 04`.)

---

## 3. Ratios MVP

Tous = `derived_ratio` : recalculables, versionnés (`ratio_engine_version`), jamais saisis. Interprétation **prudente**, wording non médical.

| Ratio | Formule | Inputs requis | Fallback si input manquant | Interprétation prudente (autorisée) | Wording interdit |
|---|---|---|---|---|---|
| `shoulder_to_waist_ratio` | `shoulder_width_cm / waist_cm` | shoulder_width + waist | si pas de shoulder → **proxy** `chest_to_waist_ratio` (signalé comme proxy) ; sinon **non calculé** | « équilibre visuel haut du corps » | « idéal », « parfait », jugement |
| `waist_to_height_ratio` | `waist_cm / height_cm` | waist + height | si pas de height → **non calculé** (pas d'estimation) | « tendance de tour de taille relative » | « obésité », « risque santé », diagnostic |
| `chest_to_waist_ratio` | `chest_cm / waist_cm` | chest + waist | non calculé | « équilibre torse / taille » | jugement esthétique de valeur |
| `arm_symmetry_ratio` | `abs(arm_left - arm_right) / mean(arm)` | arm_left + arm_right | non calculé | « écart latéral bras indicatif » | « déformation », « anormal » |
| `thigh_symmetry_ratio` | `abs(thigh_left - thigh_right) / mean(thigh)` | thigh_left + thigh_right | non calculé | « écart latéral cuisses indicatif » | idem |
| `upper_lower_balance_proxy` | proxy normalisé `(chest + mean(arm)) vs (mean(thigh) + mean(calf))` | ≥ chest + mean(arm) + mean(thigh) | si calf absent → calculer sur thigh seul, marquer « proxy partiel » ; si bas absent → non calculé | « dominance haut/bas indicative » | « disproportion », jugement |

**Règles transverses :**
- **Seuils de confiance (réutilise Signal Confidence Policy)** : aucune **tendance** affichée < 3 points ; un ratio ponctuel n'est affiché que si **tous** ses inputs requis sont des `confirmed_measurement`.
- **Pas d'extrapolation** : input manquant ⇒ fallback documenté ou ratio non affiché. Jamais d'invention de valeur.
- **Proxy explicite** : tout fallback proxy est étiqueté `is_proxy=true` dans l'UI.
- **Versionnement** : chaque ratio matérialisé stocke `ratio_engine_version`.

---

## 4. Recommandations MVP

`generated_recommendation`, versionnées (`recommendation_engine_version`), avec *rationale* obligatoire. **Conservatrices.** Pointent vers **familles musculaires / intentions**, jamais d'exercice codé en dur (liaison graphe de substitution en `Sb Body 05`).

### 4.1 Training (autorisées)
| Reco (clé) | Déclencheur (ratio/tendance) | Familles musculaires cibles | Familles d'exercices indicatives |
|---|---|---|---|
| `priority_lateral_delts` | shoulder/waist faible (ou proxy chest/waist faible) | `lateral_delts` | lateral_raise |
| `priority_back` | shoulder/waist faible + objectif V-taper | `lats`, `mid_back` | pulldown, pullup, row |
| `priority_legs` | upper/lower proxy élevé (haut dominant) | `quads`, `hamstrings`, `glutes` | squat, leg_press, hip_hinge, lunge |
| `priority_arms` | (réserve) écart bras/avant-bras ou objectif déclaré | `biceps`, `triceps` | curl, pushdown, extension |
| `priority_upper_back_posture` | asymétrie/équilibre indicatif | `rear_delts`, `mid_back` | face_pull, rear_delt_fly, row |
| `priority_waist_control_neat` | tendance taille montante | (nutrition + NEAT/cardio) | cardio léger, NEAT — **pas** un exercice d'hypertrophie |

### 4.2 Nutrition (autorisées, simples, non médicales)
| Reco (clé) | Forme | Garde-fou |
|---|---|---|
| `protein_g_per_kg` | cible `g/kg` (fourchette simple) | indicatif, non prescriptif |
| `calorie_band` | maintenance / léger déficit / léger surplus (selon objectif déclaré) | estimation ± delta, jamais une ordonnance |
| `track_weight_and_waist` | règle de suivi poids + tour de taille | réutilise `body_measurements` |
| `food_pivots` | aliments pivots simples | non prescriptif, **pas** de liste stigmatisante |

### 4.3 Interdits absolus
- ❌ diagnostic médical, % body fat inventé, lecture clinique.
- ❌ jugement humiliant / note de valeur du corps.
- ❌ promesse de transformation garantie.
- ❌ programme automatique sans validation utilisateur (au MVP : **proposition uniquement**).
- ❌ inférence ethnie/race/attractivité/santé mentale.

### 4.4 Règles
- Max **1–2 priorités** simultanées (conservatisme).
- Chaque reco : *rationale* + `recommendation_engine_version` + état accepté/ignoré.
- Respecter `ignored_recommendation` (snooze, pas de relance agressive).

---

## 5. Privacy and consent (renvoi)

Le cadrage privacy/consentement complet est dans **`SPIGNOS_BODY_PRIVACY_AND_CONSENT_SPEC.md`**. Verrou : pour `Sb Body 01` (manuel, **sans photo, sans provider**), le consentement « capture photo / provider externe » n'est **pas requis** ; mais la **suppression**, l'**export** et la **minimisation** des mesures le sont (cf. privacy spec §MVP).

---

## 6. Reviewabilité sans exécution

Cette spec et ses jumelles sont **doc-only** : reviewables sans lancer l'app. Aucun test runtime requis pour `Sx Body 01`. Les *tests probables* de `Sb Body 01` sont listés dans `SPIGNOS_BODY_MANUAL_PROFILE_BUILD_SPEC.md`.

---

## 7. Acceptance criteria

- [ ] Les 7 états de signal sont définis (définition / source / persistance / confiance / correction / analytics / risques).
- [ ] Les mesures MVP sont spécifiées avec **mapping vers colonnes réelles** (reuse vs additif), unité, min/max, latéralisation.
- [ ] Les 6 ratios MVP ont formule + inputs + fallback + interprétation prudente + interdits + versionnement.
- [ ] Les recommandations MVP (training + nutrition) sont listées avec déclencheurs et interdits.
- [ ] Le build manuel est **spécifiable sans ambiguïté** (cf. build spec).
- [ ] **Aucune** intégration provider, **aucune** image analysis nécessaire.
- [ ] Le modèle distingue primaire / dérivé / confirmé / recommandé.
- [ ] La privacy est définie **avant** le code (spec jumelle).
- [ ] Les fichiers impactés futurs sont listés (build spec).
- [ ] Reviewable sans exécuter l'application.

## 8. Rejection criteria

- [ ] Une migration / colonne / table est créée.
- [ ] `app/`, `requirements.txt`, `pyproject.toml`, `.env*`, `deploy/`, `scripts/` modifiés.
- [ ] Un provider (Bodygram/MediaPipe) est intégré ou ajouté en dépendance.
- [ ] Un diagnostic médical / % body fat inventé / jugement humiliant apparaît.
- [ ] « morphotype » utilisé comme vérité primaire.
- [ ] Consentement / suppression / minimisation oubliés.

## 9. Handoff report

- **Livrables :** 3 docs (`...SIGNAL_MODEL_SPEC.md`, `...PRIVACY_AND_CONSENT_SPEC.md`, `...MANUAL_PROFILE_BUILD_SPEC.md`).
- **Runtime :** 0 changement. **Migration :** 0. **Dépendance :** 0.
- **Décisions clés :** réutilisation `body_measurements` + `users.height_cm` ; 3 colonnes additives futures (`shoulder_width_cm`, `calf_cm_left`, `calf_cm_right`) ; double versionnement (`ratio_engine_version`, `recommendation_engine_version`).
- **OQ ouvertes :** OQ-S1 (fiabilité `shoulder_width_cm`), + OQ héritées du brainstorming (rétention, granularité consentement, intégration UX `/dashboard` vs `/body`).
- **Prochain sprint :** `Sb Body 01 — Manual Body Profile` (build sous feature flag), **après** verrouillage de cette spec.
