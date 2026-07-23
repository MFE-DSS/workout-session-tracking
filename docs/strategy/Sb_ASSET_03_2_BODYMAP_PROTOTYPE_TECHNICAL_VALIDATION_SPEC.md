# Sb_ASSET_03.2 — BodyMap Prototype Technical Validation & Design-Source Intake — SPEC

**Type** : SPEC D'INTAKE TECHNIQUE · **Statut** : 🟢 **CODE COMPLETE / TECHNICAL VALIDATION PASSED (v2) /
HUMAN REVIEW PENDING** · **Date** : 2026-07-23 · **Programme** : `Sx_ASSET` cycle `Sx_ASSET_03`.

> Valide **techniquement et indépendamment** le prototype BodyMap produit par `Sb_ASSET_03.1`, puis l'accepte
> comme **design source** (`design/auren/`). **N'autorise pas** l'intégration runtime. **Ne prétend ni**
> validation médicale, **ni** revue anatomique professionnelle, **ni** clearance juridique.

## 1. Mission
Ne pas accepter les rapports du build comme preuve. Authentifier le package v2, vérifier sa sécurité et son
caractère auto-descriptif, **rejouer indépendamment** le pipeline depuis un workspace vide, reproduire master,
compact, previews et package byte-identiques, terminer les contrôles visuels/licences/gouvernance, accepter
les **deux SVG** dans le design source, ajouter les gardes automatisés, s'arrêter avant `app/**`.

## 2. Entrées immuables
- Package v2 : `f45e0dbf0a20fb9b11f0e0314c5588f19303724665e96b91ceb0e7c092957029`, 1 449 359 o, 62 entrées.
- master : `dbb57db333863434442b476277170017db442d83e2eced6e7191266ee9ecfa73`.
- compact : `8024fd4ced62ca2010808bf85f94c3eaca4d334dde2b7c3b7683c3e5a4676c9a`.

## 3. Gates (tous requis)
Identité v2 · sécurité archive + manifeste embarqué (`62 = 61 + 1`) · audit du correctif (117/157 IDs, graphe
complet) · **replay clean-room indépendant** (racine espace+Unicode, vierge) · validation SVG indépendante
(2 validateurs convergents) · 3 méthodes géométriques (parseur / Chrome `getBBox()` / Inkscape) ·
régression master↔compact (seuils fixés avant mesure, sur bbox **rendues**) · 32 previews · provenance CC BY
4.0 revalidée · intake design source + gardes.

## 4. Verdicts autorisés (jamais au-delà)
`ACCEPTED FOR DESIGN SOURCE` · `HUMAN REVIEW PENDING` · `LEGAL REVIEW REQUIRED` ·
`ANATOMICAL REVIEW REQUIRED` · `NOT AUTHORIZED FOR APP INTEGRATION`. Jamais `approved` / `legally-cleared` /
`professionally-anatomically-validated` / `runtime-integrated`.

## 5. Non-goals
Aucune modification `app/**` / `app/static/**` · aucun remplacement du prototype runtime · aucune surface
d'attribution implémentée · aucune ouverture de `Sx_ASSET_04` · aucune fermeture de l'`ASSET INTEGRATION
GATE` · aucune clearance/revue professionnelle revendiquée · aucun asset Custom.

## 6. Verdict

**Verdict :** 🟢 **Sb_ASSET_03.2: TECHNICAL VALIDATION PASSED (package v2) / HUMAN REVIEW PENDING.** Le premier
intake (package v1) avait bloqué en `NON-REPRODUCIBLE OUTPUT` (`INCOMPLETE EXECUTABLE BUILD GRAPH`) ; le
correctif `Sb_ASSET_03.1-fix` a réémis un package **auto-descriptif et déterministe**, et cet intake l'a
**validé indépendamment** : identité exacte, sécurité, manifeste embarqué, **replay clean-room byte-identique**
(master/compact/previews/package), SVG conformes au contrat, provenance CC BY 4.0 double. Les deux SVG entrent
en **design source** ; gardes automatisés ajoutés. `ASSET INTEGRATION GATE: BLOCKED`. **Prochaine action** :
`GO HUMAN REVIEW — Sb_ASSET_03.2 Auren BodyMap Design Source`.
