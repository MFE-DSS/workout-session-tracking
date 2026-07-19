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
