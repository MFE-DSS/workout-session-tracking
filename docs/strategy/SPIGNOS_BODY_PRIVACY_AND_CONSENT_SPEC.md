# SPIGNOS — Body Privacy & Consent Spec

**Sprint :** `Sx Body 01 — Body Signal Model Spec`
**Branche :** `sx-body-01-signal-model-spec`
**Date :** 2026-06-26
**Type :** SPEC-ONLY. **0 runtime, 0 migration, 0 dépendance.**
**Documents jumeaux :** `SPIGNOS_BODY_SIGNAL_MODEL_SPEC.md`, `SPIGNOS_BODY_MANUAL_PROFILE_BUILD_SPEC.md`

> **Principe fondateur : privacy-by-design dès la spec, pas après l'intégration provider.** Ce document doit être verrouillé **avant** tout build manipulant des données corporelles.

---

## 0. Contrat spec-driven

| Champ | Valeur |
|---|---|
| **Context** | Définir le cadre privacy/consentement du module Body Intelligence, applicable dès `Sb Body 01` (manuel) et étendu pour photo/provider (`Sb Body 02/03`). |
| **Existing repo constraints** | Ownership strict (`user_id` + `ondelete=CASCADE`), export existant (`/export/sessions.{json,csv}` via `app/routers/export.py`), aucun modèle de consentement existant, secrets via `app/config.py` (`Field(default=...)`). |
| **Branch name** | `sx-body-01-signal-model-spec` |
| **Strict scope** | Consentement, suppression, conservation photo, conservation raw provider, export, wording non médical, provider externe, feature flags, minimisation. |
| **Files allowed / forbidden** | cf. spec jumelle (docs only ; `app/**`, `migrations/**`, deps interdits). |
| **Data model impact** | Conceptuel. Aucune table créée. |
| **Tests / checks** | Doc-only, reviewable sans exécution. |

---

## 1. Cadre réglementaire (RGPD)

Les photos corporelles, mensurations, body composition et posture peuvent relever de **catégories sensibles**. Le RGPD interdit en principe le traitement des **données biométriques d'identification** et des **données de santé**, **sauf exception** — notamment le **consentement explicite** pour des **finalités déterminées**.

**Posture SPIGNOS :**
- Finalité unique et déterminée : **guidance esthétique non médicale** (priorités d'entraînement, équilibre visuel).
- **Aucune** identification biométrique de la personne, **aucune** ré-identification, **aucune** reconnaissance faciale.
- **Aucune** donnée de santé / diagnostic / caractéristique protégée.

---

## 2. Consentement explicite

### 2.1 Granularité (3 consentements distincts)
| Consentement | Couvre | Requis pour | Défaut |
|---|---|---|---|
| `consent_body_measurements` | saisie & traitement de mensurations manuelles | `Sb Body 01` | **OFF** (opt-in à l'activation du module) |
| `consent_photo_capture` | capture/analyse de photo corporelle (qualité, posture) | `Sb Body 02` | **OFF** |
| `consent_external_provider` | envoi à un provider externe (Bodygram) | `Sb Body 03` | **OFF** |

> **OQ-6 (héritée) tranchée ici :** **granularité à 3 consentements**, pas un consentement global. Un consentement n'implique jamais les autres.

### 2.2 Propriétés
- **Explicite** : action positive de l'utilisateur (case non pré-cochée), jamais implicite.
- **Finalité claire** : libellé indiquant l'usage exact + (pour provider) le nom du tiers.
- **Horodaté + versionné** : on stocke quelle version du texte de consentement a été acceptée.
- **Retirable à tout moment** : le retrait stoppe le traitement futur et déclenche les options de suppression (§3).
- **Provider externe = mention explicite** : aucun envoi à Bodygram (ou tout tiers) sans `consent_external_provider` actif et nom du tiers affiché (cf. §7).

### 2.3 MVP `Sb Body 01`
Seul `consent_body_measurements` est en jeu. **Pas** de photo, **pas** de provider → `consent_photo_capture` et `consent_external_provider` restent hors scope du build manuel.

---

## 3. Suppression des données

L'utilisateur peut supprimer, par catégorie et en totalité :
- photos (binaires),
- `provider_raw_output` (JSON brut),
- assessments / captures,
- `confirmed_measurement` (mesures),
- `derived_ratio` matérialisés,
- `generated_recommendation` + feedback,
- consentements (retrait).

**Règles :**
- Suppression **réelle** (hard delete), pas un soft-delete masqué.
- Ownership : on ne supprime que les données de `user_id`.
- Cohérence : supprimer une mesure invalide les ratios/recos dérivés qui en dépendent (recalcul ou suppression en cascade applicative).
- **MVP `Sb Body 01`** : suppression d'une mesure et suppression de tout le profil corporel (réutilise la sémantique CASCADE existante sur `body_measurements`).

---

## 4. Conservation des photos

Trois politiques supportées (choix utilisateur) :
| Politique | Description | Recommandation |
|---|---|---|
| `analyze_then_delete` | analyse immédiate puis suppression du binaire | **DÉFAUT recommandé** |
| `retain_limited` | conservation bornée (durée définie, ex. 30/90 j) puis purge auto | opt-in |
| `retain_user` | conservation explicite tant que l'utilisateur ne supprime pas | opt-in |

**Règles :**
- Photo **jamais conservée par défaut**.
- Si conservation (`retain_*`) : **chiffrement au repos obligatoire**.
- **MVP `Sb Body 01`** : pas de photo du tout → cette section ne s'active qu'à `Sb Body 02+`.

> **OQ-4 (héritée) tranchée ici :** défaut = `analyze_then_delete` (le plus protecteur).

---

## 5. Conservation du raw provider output

- Stocké **uniquement** si `consent_external_provider` actif.
- **Minimisé** : on ne conserve que les champs nécessaires à la normalisation + traçabilité (provider, version, horodatage).
- **Purgeable** indépendamment du reste.
- **Pas de PII d'identification** dans le raw conservé.
- **MVP `Sb Body 01`** : aucun provider → aucun raw.

---

## 6. Export utilisateur

- L'utilisateur peut **exporter ses données corporelles** (mesures, ratios, recommandations, consentements) — extension du mécanisme d'export existant (`/export/sessions.{json,csv}`).
- Format : JSON (structuré) ± CSV (plat), cohérent avec l'existant.
- L'export ne contient **pas** de données d'un autre utilisateur (ownership).
- **MVP `Sb Body 01`** : export des mesures manuelles + consentement.

---

## 7. Wording non médical (garde linguistique)

| Autorisé | Interdit |
|---|---|
| aesthetic guidance, progression corporelle, priorités musculaires, équilibre visuel, posture **indicative**, tendance, signal **non médical** | diagnostic, pathologie, risque médical, maladie, body fat **médical**, analyse clinique, jugement humiliant, catégorie protégée |

- Garde applicative recommandée : une revue de wording à chaque release du moteur (réutiliser la discipline anti-"vous" de `coach_inference.py`).
- Tout signal posture est suffixé `_indicative` + disclaimer « observation visuelle non médicale ».

---

## 8. Provider externe futur

- Activé uniquement derrière `BODY_PROVIDER_BODYGRAM_ENABLED=false` (défaut OFF) **et** `consent_external_provider`.
- **Clé API jamais côté client** : token court généré côté serveur (Headless SDK).
- Nom du tiers affiché explicitement avant tout envoi.
- Body composition provider = **indicative non médicale** ; **OQ-5** : exposée à l'utilisateur ou interne ? (à trancher en `Sb Body 03`).

---

## 9. Feature flags (convention `app/config.py`)

Tous `bool`, défaut **OFF** (`*_enabled: bool = Field(default=False)`), introduits au build correspondant :
```text
BODY_ASSESSMENT_ENABLED=false          # active le module (Sb Body 01)
BODY_PHOTO_CAPTURE_ENABLED=false       # Sb Body 02
BODY_PROVIDER_BODYGRAM_ENABLED=false   # Sb Body 03
```
**Aucun impact production** tant que le flag n'est pas activé. Aucun flag n'est créé dans `Sx Body 01` (spec only) — ils sont **spécifiés** pour `Sb Body 01+`.

---

## 10. Minimisation des données

- Ne collecter que le strict nécessaire à la finalité (guidance esthétique).
- **Pas** de photo par défaut ; raw provider minimisé ; **aucune** donnée d'identité.
- Entrées partielles tolérées (pas de collecte forcée).
- Pas d'usage secondaire non consenti.

---

## 11. Matrice privacy par lot

| Donnée | `Sb Body 01` (manuel) | `Sb Body 02` (capture) | `Sb Body 03` (provider) |
|---|---|---|---|
| Consentement requis | `consent_body_measurements` | + `consent_photo_capture` | + `consent_external_provider` |
| Photo | aucune | capture qualité (défaut delete) | front+side (selon politique) |
| Raw provider | aucun | landmarks métadonnées | JSON Bodygram minimisé |
| Suppression | mesures + profil | + captures/landmarks | + raw provider |
| Export | mesures + consentement | + métadonnées capture | + raw (si conservé) |
| Flag | `BODY_ASSESSMENT_ENABLED` | + `BODY_PHOTO_CAPTURE_ENABLED` | + `BODY_PROVIDER_BODYGRAM_ENABLED` |

---

## 12. Acceptance criteria
- [ ] Consentement explicite défini (granularité 3, propriétés, retrait).
- [ ] Suppression définie par catégorie + totale, hard delete, ownership.
- [ ] Conservation photo : 3 politiques, défaut `analyze_then_delete`, chiffrement si conservation.
- [ ] Conservation raw provider : consenti, minimisé, purgeable.
- [ ] Export utilisateur défini (extension de l'existant).
- [ ] Wording non médical défini (autorisé/interdit).
- [ ] Provider externe : consentement + clé serveur + mention du tiers.
- [ ] Feature flags spécifiés (OFF par défaut), non créés en spec.
- [ ] Minimisation définie.
- [ ] Privacy définie **avant** le code.

## 13. Rejection criteria
- [ ] Photo conservée par défaut, ou sans chiffrement.
- [ ] Envoi provider sans consentement / sans mention du tiers / clé côté client.
- [ ] Consentement global non granulaire ou pré-coché.
- [ ] Suppression impossible ou soft-delete masqué.
- [ ] Wording médical / caractéristique protégée.
- [ ] Migration / code / dépendance créés dans ce sprint.

## 14. Handoff report
- **Décisions tranchées :** OQ-4 (défaut delete), OQ-6 (3 consentements). OQ-5 (exposition body comp) reste pour `Sb Body 03`.
- **MVP `Sb Body 01` privacy surface :** `consent_body_measurements` + suppression + export + minimisation. Pas de photo, pas de provider.
- **Pré-requis avant `Sb Body 01` :** ce document verrouillé.
