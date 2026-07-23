# AUREN — BodyMap IP, Provenance & Source Disclosure Requirements

**Cycle** : `Sx_ASSET_03`.

```
PROCUREMENT / LEGAL REQUIREMENTS CHECKLIST
NOT A FINAL LEGAL CONTRACT · NOT LEGAL ADVICE · PROFESSIONAL COUNSEL REQUIRED
```

> Ce document **définit les exigences** que le futur contrat de production devra couvrir. Il **ne constitue
> pas** un contrat juridique, ni un avis juridique. `PROFESSIONAL LEGAL CLEARANCE: NOT CLAIMED`.

---

## 1. Le contrat de production humaine devra couvrir (minimum)
- identité de l'auteur ; organisation ;
- **originalité déclarée** (le master est une œuvre originale, non dérivée automatiquement d'un dataset) ;
- **liste des références** consultées (avec licence de chacune) ;
- **liste des outils** (nom + version) ;
- **liste des composants tiers** éventuels ;
- **déclaration d'usage d'IA** (outil/version/fonctions/finalité/parties affectées/redessin humain) ;
- remise des **sources natives** ;
- remise du **SVG canonique** ;
- droit de **modification** · **adaptation** · **exploitation commerciale** · **exploitation internationale** ;
- **durée et territoires** à définir par conseil juridique ;
- capacité à produire des **variantes** (female/abstract/latérale futures) et des **exports** ;
- **absence d'asset tiers non déclaré** ;
- obligations d'**attribution** éventuelles (voir §2) ;
- procédure de **correction** · procédure de **rejet** ;
- **conservation des preuves de création**.

## 2. Impact des références sous licence (due diligence) — **amendé 2026-07-23**
> **Correction majeure** : la mention « CC BY-SA 2.1 Japan » provenait d'un **miroir GitHub figé en 2011**.
> La page de licence **officielle DBCLS** (mise à jour **2025-02-27**) donne **CC BY 4.0 International**.

- **BodyParts3D = CC BY 4.0 International** (**aucune clause ShareAlike**) : la **dérivation est licite**, y
  compris pour un master commercial propriétaire, **sous attribution obligatoire et irrévocable** :
  *« BodyParts3D, © The Database Center for Life Science licensed under CC Attribution 4.0 International »*.
  La classification finale dérivé/original reste du ressort d'un conseil → `LEGAL CLASSIFICATION PENDING`.
- **Servier Medical Art = CC BY 4.0** : incorporable sous attribution.
- **AnatomyTOOL** : licences **par ressource** ; seules CC BY / CC0 (compatibles commercial) sont éligibles,
  **qualifiées individuellement** ; NC / étudiant écartés.
- **OpenStax** : **1ʳᵉ éd. CC BY 4.0** éligible ; **2e éd. CC BY-NC-SA 4.0 exclue** (NC).
- **Z-Anatomy** (CC BY-SA 4.0, sources mélangées dont un composant **NC**) et **Wikimedia
  `Muscles front and back.svg`** (CC BY-SA 4.0) : **jamais dans le master livré**.
- Le contrat — ou, en dérivation interne, le registre de provenance — doit **garantir** que le master ne
  contient **aucun asset tiers non déclaré** et **aucun composant copyleft ou NC**.
- **L'attribution n'est pas optionnelle et ne s'éteint pas** avec la stylisation : même fortement simplifié,
  un master dérivé de BodyParts3D reste soumis à l'attribution CC BY 4.0.

## 3. Interdiction de revendication prématurée
Ne **jamais** affirmer :
```
AUREN OWNS THE MASTER
```
avant : contrat signé · sources remises · revue juridique · provenance acceptée.

## 4. Statuts autorisés (aucun ne vaut clearance)
```
contract-requirements-defined
contract-draft-pending
professional-review-required
signature-pending
rights-not-yet-confirmed
```
Statut initial du cycle : **`contract-requirements-defined`** (ce document) → tout le reste `NOT STARTED` /
`PENDING`.

## 5. Provenance à renseigner (au moment de l'intake `Sb_ASSET_03.2`)
Champs (miroir de `AUREN_ASSET_PROVENANCE.md`) : `asset_id` · `author` · `owner` (avec
`ip_ownership_status: not-legally-reviewed` tant que non signé) · `source_project` (références) · `source_type`
(`original-auren` visé ; `reference-only` pour BodyParts3D/AnatomyTOOL) · `license_spdx` (des références, si
réutilisées) · `access_date` · `source_reference` · `attribution_required` · `usage_nature` · `modifications`
· `tooling` · `ai_usage` · `reviewer` · `review_date` · `evidence` · `status`.
**Aucune entrée** ne portera `verified` / `approved` / `legally-cleared` tant que la revue juridique
professionnelle n'a pas abouti.
