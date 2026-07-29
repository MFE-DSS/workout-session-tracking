# AUREN — Muscle Focus Source Ledger (`Sb_ASSET_03B.1`)

> **⚠️ SOURCE RESET — Sb_ASSET_03B.2R (2026-07-29), prioritaire.** Pour la **géométrie de body-fitting**, la
> source primaire est désormais **BodyParts3D 4.0 (DBCLS officiel, CC BY 4.0)** ; **Servier** = `SUPERSEDED FOR
> BODY-FITTING GEOMETRY` (la classification historique ci-dessous est **conservée**, non réécrite). BodyParts3D =
> géométrie source **traçable**, **pas** vérité anatomique canonique (référence masculin adulte, peut contenir des
> erreurs). Preuves licence : workspace opérateur `01_acquisition/license_evidence/` — PDF officiel **type-vérifié**
> (non rendu texte, poppler absent) + 2 HTML corroborant **CC BY 4.0 / Release 4.0** ; **origine attestée
> manuellement par Martin** ; `PROFESSIONAL LEGAL CLEARANCE: NOT CLAIMED`. Doctrine + mapping P0 prouvé (exact-FMA,
> 35 reps) : [`../../strategy/Sb_ASSET_03B_2R_BODYPARTS3D_SOURCE_RESET_SPEC.md`](../../strategy/Sb_ASSET_03B_2R_BODYPARTS3D_SOURCE_RESET_SPEC.md).

**Type** : **registre de sources normatif** (revalidé) — **DOCS-ONLY**. Relevés officiels **2026-07-24**.
**NON une conclusion juridique** : `PROFESSIONAL LEGAL CLEARANCE: NOT CLAIMED` · `ASSET INTEGRATION GATE:
BLOCKED`.
**Amont** : [`AUREN_MUSCLE_FOCUS_SOURCE_STRATEGY.md`](AUREN_MUSCLE_FOCUS_SOURCE_STRATEGY.md) (stratégie) +
[`../../research/AUREN_MUSCLE_FOCUS_REFERENCE_RESEARCH.md`](../../research/AUREN_MUSCLE_FOCUS_REFERENCE_RESEARCH.md)
(recherche). **Ce ledger fige la classification par source** après **revalidation web réelle** (Axe C) et
**croisement adversarial** (Axe E), et **corrige** quatre points.

> Méthode : chaque licence ci-dessous provient de la **page officielle de l'éditeur** (récupération web
> 2026-07-24). Les formulations sont fidèles ; une relecture directe du texte source aux URL listées est
> requise avant tout intake contractuel. Ce document **n'accorde aucune autorisation** — il **enregistre** des
> faits de licence à une date.

---

## 0. Quatre corrections vs les brouillons versés (`ff9541a`)

| # | Correction | Avant | Après (revalidé 2026-07-24) |
|---|---|---|---|
| C1 | **NLM Visible Human** reclassifié | « domaine public · zéro contrainte » | **TERMS-BASED GOVERNMENT DATA** — attribution + non-endossement + divulgation de fraîcheur ; **rôle par défaut = validation/référence** |
| C2 | **OpenStax — clause anti-ingestion IA** | absente | **présente sur les 2 éditions** : interdit l'usage comme **entraînement/ingestion LLM/IA générative** sans permission — **s'ajoute** à la licence CC |
| C3 | **Gray's 1918 / atlas historiques** | « PD · zéro contrainte (<1929) » | **PD CONDITIONNEL** — par édition/scan/juridiction/provenance + **absence de couche moderne** ; couche **Lewis †1964** encore protégée en **UE** |
| C4 | **Servier (SMART)** périmètre | « CC BY 4.0 » (global) | CC BY 4.0 **des images seules** ; **logos/marque « SERVIER »/UI du site EXCLUS** ; **non-endossement** |

Ces corrections n'aggravent **aucune** dette : elles **resserrent** la doctrine source-reuse-first.

---

## 1. Registre par source

### 1.1 Servier Medical Art (SMART) — **PRIMARY DERIVATION (géométrie)**
- **Licence** : **CC BY 4.0** — *images seules*. Usage **commercial + adaptation** autorisés sous attribution.
- **EXCLU de CC BY** (C4) : **logos**, marque **« SERVIER »**/partenaires (marques déposées), **contenu du
  site / UI / navigation** (copyright site). **Non-endossement** : l'attribution ne doit pas suggérer que
  Servier endosse le produit. **Pas d'usage branding/logo** (déconseillé par Servier).
- **Attribution exacte** : « Image(s) provided by Servier Medical Art (https://smart.servier.com), licensed
  under CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/). »
- **URL** : smart.servier.com · /terms-of-use/ · /how-to-cite-servier-medical-art/ · /using-smart-images-what-you-can-do/.
- **Rôle Auren** : socle géométrique + continuité visuelle avec le BodyMap. `attribution_required: true`.

### 1.2 OpenStax *Anatomy & Physiology* **1ʳᵉ éd. (2013)** — **PRIMARY DERIVATION (géométrie, par figure)**
- **Licence** : **CC BY 4.0** — dérivation, y compris **commerciale**, sous attribution.
- **Attribution** : « Access for free at https://openstax.org/books/anatomy-and-physiology/pages/1-introduction »
  (sur chaque page, numérique + imprimé). **Marques OpenStax/Rice réservées** (nom, logo, couvertures — hors CC).
- **⚠ C2 — clause anti-ingestion IA (sur les 2 éditions)** : « This book may not be used in the training of
  large language models or otherwise be ingested into large language models or generative AI offerings without
  OpenStax's permission. » → **Ne jamais** injecter du contenu OpenStax comme **entrée** d'un système génératif
  sans permission. Cohérent avec notre §Politique IA (jamais d'image source en entrée générative).
- **URL** : openstax.org/books/anatomy-and-physiology/pages/preface · /pages/1-introduction.
- **Rôle Auren** : planches musculaires locales (crédit **par figure**). `attribution_required: true`.

### 1.3 OpenStax *A&P* **2ᵉ éd.** — **EXCLU**
- **Licence** : **CC BY-NC-SA 4.0** — **NC éliminatoire** (pas de dérivé commercial) + **SA** (copyleft). **Ne
  jamais confondre avec la 1ʳᵉ éd.** Exclu de toute dérivation du master livré.

### 1.4 NLM Visible Human — **VALIDATION / RÉFÉRENCE par défaut** (C1)
- **Statut réel** : **NON « PD zéro contrainte »**. Œuvre du gouvernement fédéral US **non soumise au copyright
  aux US**, **mais accès conditionné** : le **NLM Data License** (renouvellement annuel) a été **remplacé en
  juillet 2019** par des **Terms & Conditions** ; **le téléchargement vaut acceptation**.
- **Obligations** : **attribution** « Courtesy of the U.S. National Library of Medicine » (clear & conspicuous)
  · **non-endossement** (ne pas impliquer que NLM endosse) · **divulgation de fraîcheur** (maintenir la version
  courante **ou** signaler que les données ne reflètent pas la version la plus récente).
- **Mesh protégé** : une **segmentation/maillage tiers** dérivée des cryosections Visible Human est une
  **expression protégée** (pas un fait libre) — même doctrine que BodyParts3D.
- **URL** : nlm.nih.gov/research/visible/getting_data.html · /web_policies.html · /databases/download/terms_and_conditions.html.
- **Rôle Auren** : **validation/référence** par défaut ; **promotion en dérivation** seulement après vérification
  **plaque par plaque** des T&C de l'asset précis. **Pas** groupé avec le PD « zéro contrainte ».

### 1.5 Gray's Anatomy 1918 + atlas historiques — **PD CONDITIONNEL** (C3)
- **Gray's 1918** (Gray/Carter, 20ᵉ éd. US, éd. **W. H. Lewis**, Lea & Febiger) : **PD aux US** (règle 95 ans /
  publié avant 1931). Tag Wikimedia `PD-Gray's Anatomy plate`.
- **Juridiction** : **US = publication** (PD) ; **UE = 70 ans pma** → Gray †1861, **Carter †1897** PD ; **Lewis
  †1964** ⇒ toute contribution **propre à Lewis** dans l'éd. 1918 reste **protégée en UE jusqu'au 1ᵉʳ janv.
  2035**. Ne pas présumer « 1918 = PD partout ».
- **Piège couche moderne** : un **scan fidèle** d'une œuvre 2D PD **n'ajoute pas** de copyright (*Bridgeman v.
  Corel*, US ; **Art. 14 Directive UE 2019/790**, UE). Mais **réédition moderne**, **colorisation récente**,
  **restauration créative**, **légendes/labels modernes** = **couche neuve protégée**.
- **Checklist à enregistrer avant de qualifier « PD » et de dériver** : (1) édition exacte ; (2) scan/source
  (URL Wikimedia/IA + uploader + tag de licence) ; (3) juridiction de diffusion ; (4) provenance ; (5) absence
  d'élément éditorial moderne protégé ; (6) dates de mort auteurs/illustrateur.
- **Autres atlas** (même règle, par édition/juridiction) : **Vesalius †1564**, **Bourgery †1849**, **Sobotta
  †1945** (PD UE depuis 2016 — anciens tirages seulement), **Spalteholz †1940** (PD UE depuis 2011). **Rééditions
  modernes protégées.**
- **Rôle Auren** : dérivation PD (relief fin / coupes profondes) **uniquement avec la checklist renseignée**.

### 1.6 BodyParts3D / Anatomography — **VALIDATION SEULEMENT**
- **Licence** : **CC BY 4.0** (page officielle **DBCLS**, maj **2025-02-27**) — **PAS** le miroir GitHub figé en
  2011 (CC BY-SA 2.1 JP). Un relevé « CC BY-SA » vient **invariablement du miroir** (piège documenté + résolu au
  BodyMap, re-confirmé par croisement adversarial Axe E).
- **Rôle Auren** : **validation** attaches/FMA/nommage. **Mesh = expression protégée** → on **redessine à partir
  du savoir**, on ne **trace/retopologise jamais**.

### 1.7 Z-Anatomy — **VALIDATION / INSPIRATION seulement**
- **Licence** : **CC BY-SA 4.0** — **copyleft contaminant** → jamais dérivé dans le master. Rôle : couches
  superficiel/profond.

### 1.8 MuscleWiki · BioDigital · BioRender · Complete Anatomy · Muscle&Motion — **INSPIRATION seulement**
- **Copyright** → **consulter, jamais dériver**. Rôle : conventions de cadrage/zoom UX uniquement.

---

## 2. Règles de licence dures (rappel, héritées BodyMap)

1. **CC BY** = dérivation propriétaire licite **+ attribution irrévocable**. **CC BY-SA** = copyleft →
   validation/inspiration. **CC BY-NC** = **éliminatoire**. **CC0** = liberté totale. **PD** = **conditionnel**
   (édition/scan/juridiction/couche moderne). **Copyright** = inutilisable.
2. **Un mesh 3D / une segmentation est une expression protégée** même quand le fait anatomique ne l'est pas.
3. **Agrégateurs = licence par fichier** (Wikimedia, AnatomyTOOL, Sketchfab, Internet Archive) — remonter à la
   source, journaliser licence + URL **par asset**.
4. **IA = plan B/C borné** : moodboard/compo/style **sur géométrie déjà validée de source propre** ; **jamais
   géométrie livrée** ; **toujours déclarée** ; **jamais** d'image propriétaire **ni** de contenu OpenStax en
   **entrée** générative (renforcé par C2).
5. **Séparation physique** des espaces géométrie-CC BY vs référence-SA/NC/copyright ; **aucune archive/image
   committée dans Git** à ce stade.

## 3. Surface d'attribution à provisionner (dette héritée, non aggravée)

`ATTRIBUTION SURFACE: NOT YET IMPLEMENTED`. Le produit devra porter, dans une surface de crédits :
```
Servier Medical Art — Les Laboratoires Servier — CC BY 4.0                        (si image incorporée)
OpenStax Anatomy & Physiology (1ʳᵉ éd., 2013) — CC BY 4.0                          (si figure incorporée)
BodyParts3D, © The Database Center for Life Science — CC BY 4.0                    (si validation citée)
Courtesy of the U.S. National Library of Medicine                                 (si Visible Human utilisé, + fraîcheur)
Gray's Anatomy of the Human Body (20ᵉ éd. US, 1918, dom. public) — <scan/URL>      (si planche PD dérivée)
```
Aucune entrée `approved` / `verified` / `legally-cleared` tant que la revue professionnelle n'a pas abouti.

---

## Verdict

**Verdict :** 🟢 **`MUSCLE FOCUS SOURCE LEDGER: LOCKED / REVALIDATED (DOCS-ONLY).`** Classification par source
figée après revalidation web réelle et croisement adversarial, avec **4 corrections** : NLM Visible Human
**reclassifié** terms-based (validation par défaut), clause **anti-ingestion IA OpenStax** enregistrée, Gray's/
atlas **PD conditionnel** (checklist + couche Lewis †1964 UE), périmètre **Servier images-only** (marques/UI
exclues). Servier + OpenStax 1ʳᵉ éd. = géométrie dérivable ; BodyParts3D/Z-Anatomy = validation ; MuscleWiki/
BioDigital = inspiration ; OpenStax 2ᵉ éd. = exclu. **Aucune autorisation accordée, aucun asset acquis.**
`PROFESSIONAL LEGAL CLEARANCE: NOT CLAIMED` · `ASSET INTEGRATION GATE: BLOCKED`.
