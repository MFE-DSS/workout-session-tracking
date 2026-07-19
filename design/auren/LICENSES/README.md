# AUREN — Third-Party Asset Licenses

Ce dossier conserve le **texte de licence complet** de chaque projet tiers dont un asset est ingéré dans
le pack source Auren.

## État initial
```
No third-party asset has been accepted into the Auren source pack.
```
**Aucune licence tierce n'est présente** — aucun asset tiers n'a été ingéré dans `Sb_ASSET_01.1`. Le
premier intake tiers (subset **Tabler**) relève de `Sb_ASSET_02.1`.

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
