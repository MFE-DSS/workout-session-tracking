# AUREN — Third-Party Asset Licenses

Ce dossier conserve le **texte de licence complet** de chaque projet tiers dont un asset est ingéré dans
le pack source Auren.

## État (2026-07-20)
```
FIRST THIRD-PARTY LICENSE ACCEPTED INTO THE AUREN DESIGN SOURCE:
  tabler-MIT.txt — Tabler Icons v3.45.0 (commit 975920ff…), SPDX MIT, © Paweł Kuna 2020-2026.
  Texte officiel copié byte-for-byte depuis le commit épinglé.
  Intake DESIGN SOURCE uniquement — human/legal review PENDING — 0 autorisation app/static/.
No other third-party license present (Health Icons ABSENT — NOT REQUIRED FOR P0).
```
- **`tabler-MIT.txt`** : premier projet tiers accepté (Sb_ASSET_02.1), pour le subset de 10 icônes outline.
- Le fichier conserve l'avis officiel MIT incluant **Paweł Kuna**. Aucune traduction/résumé/reconstruction.

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
- ❌ Copier `MIT.txt` / `CC-BY-4.0.txt` / `Apache-2.0.txt` **tant qu'aucun asset tiers correspondant n'est
  ingéré** (ce serait déclarer une dépendance inexistante).

## Prochain intake tiers
`Sb_ASSET_02.1 — Vendored Icon Subset & License Intake` : au moment où un subset Tabler sera copié, son
texte de licence officiel sera déposé ici, avec l'entrée de provenance correspondante.
