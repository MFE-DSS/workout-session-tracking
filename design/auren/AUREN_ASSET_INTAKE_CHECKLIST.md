# AUREN — Asset Intake Checklist

Grille d'acceptation/refus de **tout futur asset** (original ou tiers) avant son entrée dans
`design/auren/source/`. **L'intake n'est pas une autorisation d'intégration runtime** (celle-ci exige le
franchissement de l'`ASSET INTEGRATION GATE`).

---

## 1. Identification
- [ ] asset ID stable, namespacé (`auren.<domaine>.<objet>[.variant]`)
- [ ] version (semver)
- [ ] type (cf. manifest §3)
- [ ] statut initial (borné, ≠ `approved`)
- [ ] propriétaire (owner)

## 2. Provenance
- [ ] source **officielle** identifiée (URL de référence)
- [ ] auteur
- [ ] licence + identifiant **SPDX**
- [ ] attribution requise ? (yes/no)
- [ ] date d'accès
- [ ] **copie du texte de licence** conservée dans `LICENSES/` (pour un asset tiers)
- [ ] entrée créée dans `AUREN_ASSET_PROVENANCE.md`

## 3. Technique
- [ ] SVG valide (XML bien formé)
- [ ] `viewBox` présent (jamais supprimé)
- [ ] **pas** de `<script>`
- [ ] **pas** d'URL externe
- [ ] **pas** de raster intégré (bitmap embarqué)
- [ ] IDs **uniques** (pas de collision ; IDs = API)
- [ ] poids ≤ budget (cf. spec §Budgets)
- [ ] rendu **déterministe** (resvg identique sur 2 runs)
- [ ] couleurs via **tokens/`currentColor`** (0 hex codé en dur)

## 4. Sémantique
- [ ] fonction explicite
- [ ] surface(s) autorisée(s)
- [ ] consumer identifié
- [ ] **contrat métier non modifié** (pas de nouvelle zone, pas de changement de scores/données)
- [ ] **aucune zone inventée** (taxonomie 11 zones respectée)

## 5. Accessibilité
- [ ] rôle (`decorative` \| `action`)
- [ ] label (si action)
- [ ] texte adjacent (si décoratif)
- [ ] focus visible (si interactif)
- [ ] contraste ≥ AA (cf. `Sb_UI_09.3` contrast guard)
- [ ] non-color cue (état non porté par la couleur seule)

## 6. Revues (toutes requises pour `approved`)
- [ ] product
- [ ] technical
- [ ] accessibility
- [ ] legal (licence/PI)
- [ ] anatomical (BodyMap uniquement)
- [ ] mobile 360 px

## 7. Verdict d'intake
```
ACCEPTED FOR DESIGN SOURCE
REJECTED
REVISION REQUIRED
LEGAL REVIEW REQUIRED
ANATOMICAL REVIEW REQUIRED
NOT AUTHORIZED FOR APP INTEGRATION
```
> Le verdict d'intake statue sur l'entrée dans `design/auren/source/`. Il **n'autorise pas** l'intégration
> runtime (`app/static/`), qui reste subordonnée à l'`ASSET INTEGRATION GATE` (15 approbations : humaine,
> anatomique, juridique, mobile).

## Intake réalisé — BodyMap master (Sb_ASSET_03.2, 2026-07-23)
```
ACCEPTED FOR DESIGN SOURCE
HUMAN REVIEW PENDING
ANATOMICAL REVIEW REQUIRED
LEGAL REVIEW REQUIRED
NOT AUTHORIZED FOR APP INTEGRATION
```
Master + compact acceptés : contrat SVG validé indépendamment (viewBox `0 0 240 200`, 14 IDs, 11 zones,
0 `zone-unknown`, surface statique sûre), hashes immuables (`dbb57db3…`/`8024fd4c…`), compact ≤ 12 Ko,
**reproductibilité vérifiée indépendamment** (package v2 déterministe `f45e0dbf…`), provenance CC BY 4.0
double (BodyParts3D + Servier) avec notices d'attribution, `ai_usage: none`, revue anatomique professionnelle
**non revendiquée**, gardes automatisés (`tests/test_auren_bodymap_master.py`). Statut initial **≠ approved**.

## Gate runtime statué — BodyMap master (DA-04.0, 2026-10-28)
```
OUTCOME B — NOT AUTHORIZED FOR APP INTEGRATION
```
| Revue (§6) | État | Preuve |
|---|---|---|
| technical | **faite, passe** | `svg`/`g`/`path` seulement, `currentColor`, 0 raster / police / URL / transformation ; garde du sous-ensemble `react-native-svg` |
| anatomical | **manquante** | `professional_anatomical_review: not-claimed` ; provenance `reviewer: NOT YET REVIEWED` |
| legal | **manquante** | `legal_review: required` |
| attribution (surface) | **manquante** | `attribution_surface: not-yet-implemented` ; aucune mention dans l'app mobile |
| product · accessibility · mobile 360 px | non statuées ici | relèvent de l'intégration (DA-04.1), après le gate |

Rien n'a été promu. Le gate passe quand le registre porte une autorisation explicite (date, base de revue,
hashes, contraintes) et que ce document, le README du dossier et la provenance la disent aussi.

## Décision du propriétaire — BodyMap master (DA-04.0b, 2026-10-28)
```
ACCEPT_INTERNAL_P0_WITH_CONSTRAINTS
AUTHORIZED FOR AUREN INTERNAL BUILDS WITH CONSTRAINTS
PUBLIC RELEASE NOT AUTHORIZED
```
L'opérateur choisit la voie (b) du rapport DA-04.0. Les deux sources sont sous CC BY 4.0 (adaptation
autorisée sous attribution) ; c'est un compromis de gouvernance, pas un avis juridique.

| Revue (§6) | État après décision | Preuve |
|---|---|---|
| technical | faite, passe | inchangé depuis DA-04.0 |
| anatomical | **tenue par la décision du propriétaire**, professionnelle non réalisée | `owner_decision`, `professional_anatomical_review: not-claimed` |
| legal | requise **pour la diffusion publique** | `legal_review: required`, `public_release_authorization: blocked` |
| attribution (surface) | **à livrer** avant tout montage produit (`DA-04.1`) | `missing_for_runtime` |

Portée : builds internes de l'app mobile. Jamais le runtime web, jamais un store public. Contraintes et
texte d'attribution exacts : `source/bodymap/auren_bodymap_source.yaml`.
