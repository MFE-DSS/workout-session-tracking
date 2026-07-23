# AUREN — Third-Party Asset Licenses

Ce dossier conserve le **texte de licence complet** de chaque projet tiers dont un asset est ingéré dans
le pack source Auren.

## État (2026-07-23)
```
THIRD-PARTY LICENSES ACCEPTED INTO THE AUREN DESIGN SOURCE:
  tabler-MIT.txt — Tabler Icons v3.45.0 (commit 975920ff…), SPDX MIT, © Paweł Kuna 2020-2026.
  CC-BY-4.0.txt  — texte officiel Creative Commons Attribution 4.0 International (verbatim,
                   récupéré depuis creativecommons.org le 2026-07-23), partagé par les deux
                   sources du BodyMap ci-dessous.
  bodyparts3d-NOTICE.md          — BodyParts3D (DBCLS), CC BY 4.0 — source primaire du master BodyMap.
  servier-medical-art-NOTICE.md  — Servier Medical Art, CC BY 4.0 — zones lats/core du master BodyMap.
  Intake DESIGN SOURCE uniquement — human/legal review PENDING — 0 autorisation app/static/.
No other third-party license present (Health Icons ABSENT — NOT REQUIRED FOR P0).
```
- **`tabler-MIT.txt`** : premier projet tiers accepté (Sb_ASSET_02.1), pour le subset de 10 icônes outline.
  Le fichier conserve l'avis officiel MIT incluant **Paweł Kuna**. Aucune traduction/résumé/reconstruction.
- **`CC-BY-4.0.txt`** + **notices** : intake BodyMap `Sb_ASSET_03.2`. Le master BodyMap est une **œuvre
  dérivée sous attribution** de BodyParts3D (CC BY 4.0) et Servier Medical Art (CC BY 4.0). Le texte CC BY 4.0
  est le **legalcode officiel verbatim**, pas une reconstruction. Les notices déclarent l'attribution exacte,
  les modifications, la date d'accès et l'absence d'endossement. **NOT AUTHORIZED FOR APP INTEGRATION.**

## Règles
- **Un texte de licence complet par projet tiers**, récupéré depuis la **source officielle** au moment de
  l'intake (jamais un agrégateur, jamais une reconstruction ou un résumé).
- **Nommage recommandé** : `<PROJET>-<SPDX>.txt` (ex. `tabler-MIT.txt`, `health-icons-MIT.txt`).
- **Identifiant SPDX** consigné dans `AUREN_ASSET_PROVENANCE.md` (`license_spdx`).
- **Attribution** conservée si la licence l'exige (`attribution_required: yes`).
- **Version + date de récupération** de la source consignées dans la provenance.
- Relation avec le registre : chaque fichier de licence ici est **pointé** par une entrée de
  `AUREN_ASSET_PROVENANCE.md` (`license_text_location`).

## Interdits
- ❌ Créer une licence **reconstruite, résumée ou paraphrasée**.
- ❌ Récupérer le texte depuis un **agrégateur** comme source primaire.
- ❌ Copier `MIT.txt` / `Apache-2.0.txt` / `CC0-1.0.txt` **tant qu'aucun asset tiers correspondant n'est
  ingéré** (ce serait déclarer une dépendance inexistante). *(`CC-BY-4.0.txt` est désormais présent car le
  BodyMap l'exige réellement.)*
- ❌ Ingérer une licence **Health Icons** (non requise pour P0, déclarée absente).

## Intakes réalisés
- `Sb_ASSET_02.1` — subset Tabler → `tabler-MIT.txt`.
- `Sb_ASSET_03.2` — master BodyMap dérivé → `CC-BY-4.0.txt` + `bodyparts3d-NOTICE.md` +
  `servier-medical-art-NOTICE.md`.
