# AUREN — Muscle Focus Reference Research (`Sx_ASSET_03B`)

**Type** : recherche références + principes visuels + stratégie de sources — **DOCS-ONLY** (0 image importée,
0 SVG produit, 0 œuvre dupliquée).
**Date d'accès** : **2026-07-24** (relevés effectués à cette date sur les pages citées).
**Portée** : nourrir la spec `Sx_ASSET_03B`. **NON une conclusion juridique.** `OFFICIAL LICENSE EVIDENCE
RECORDED AT ACCESS DATE`, jamais `LEGAL CLEARANCE COMPLETE`. `PROFESSIONAL LEGAL CLEARANCE: NOT CLAIMED`.
**Méthode** : recherche parallèle en 4 axes (Product/UX · Visual/anatomical · Source/asset · IA/architecture)
puis **synthèse contradictoire** (une contradiction majeure arbitrée, cf. §0).

---

## 0. Arbitrage d'une contradiction (croisement adversarial)

La recherche parallèle a produit **une contradiction sur la licence de BodyParts3D**, arbitrée ici — c'est
précisément la valeur d'un croisement à plusieurs voix.

| Voix | Relevé | Source consultée | Verdict |
|---|---|---|---|
| Axe C (recherche fraîche) | **CC BY-SA 2.1 JP** (copyleft) — « risque #1 » | fichier `LICENSE_content` du **miroir GitHub** `Kevin-Mattheus-Moerman/BodyParts3D` | ❌ **source périmée** |
| Précédent repo (`AUREN_BODYMAP_OPEN_SOURCE_REUSE_STRATEGY.md`, 2026-07-23) | **CC BY 4.0** | **page officielle DBCLS** `dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html` (maj **2025-02-27**) | ✅ **officielle et courante** |

**Arbitrage retenu : BodyParts3D est CC BY 4.0.** Le miroir GitHub reproduit la licence de 2011 (release
`20110915`, CC BY-SA 2.1 Japan) ; DBCLS a **relicencié** en CC BY 4.0 (page officielle, maj 2025-02-27). Un
relevé « CC BY-SA » sur BodyParts3D **signale toujours une lecture du miroir figé**, jamais de la source
officielle. Ce piège a **déjà été documenté et résolu** au BodyMap ; il se **re-manifeste** ici et confirme
la règle : **télécharger et qualifier uniquement depuis l'archive officielle DBCLS**.

**Ce que le croisement conserve de la voix erronée** (apport réel, indépendant de l'erreur de licence) :
1. **Nuance juridique majeure** : *les faits anatomiques ne sont pas protégeables, mais un maillage 3D
   spécifique est une expression protégée*. Tracer/retopologiser un mesh sous copyleft produit un dérivé
   copyleft ; **redessiner à partir du savoir anatomique** (multi-sources) produit une œuvre nouvelle.
2. **Sources domaine public ajoutées** : Gray's Anatomy (1918), NLM Visible Human, atlas historiques PD.
3. **Exclusions confirmées** : MuscleWiki (copyright), BioDigital / BioRender / Complete Anatomy
   (propriétaires), OpenStax **2ᵉ éd.** (NC).
4. **Hygiène agrégateurs** : Wikimedia / AnatomyTOOL / Sketchfab = licence **par fichier**, jamais globale.

## 1. Familles de références étudiées — principes extraits

> **Cadre IP** : tout ci-dessous extrait des **principes de représentation**. **Aucune œuvre citée n'est
> reproduite, redessinée ou re-stylisée.** Netter et Delavier sont des **références conceptuelles**
> (grammaire pédagogique), **jamais** des gabarits — leurs illustrations sont protégées.

| Famille | Exemples | Principe extractible | Force (produit sobre) | Faiblesse |
|---|---|---|---|---|
| **A. Atlas pédagogiques imprimés** | Netter, Kenhub Color Atlas, Delavier (geste) | « la clarification est le but » → **une plaque = un message unique** ; muscle cible en aplat, contexte en trait neutre ; légende à codes couleur | hiérarchie cible/contexte immédiate, économie de moyens | rendu peint/réaliste = trop « médical/atlas » (interdit ici) |
| **B. Logiciels d'anatomie 3D** | Complete Anatomy, BioDigital, Anatomy 3D Atlas | **couches superficiel→profond « pelables »** ; isolate/fade ; **cartographie origine/insertion sur l'os** | gèrent nativement superficiel vs profond | rendu volumétrique réaliste = esthétique refusée |
| **C. Biomécanique de l'exercice** | Muscle & Motion Strength | **rôle fonctionnel codé couleur** (prime mover / synergiste / stabilisateur / antagoniste) | mappe directement la hiérarchie principal/synergiste/adjacent | animation 3D lourde, non requise |
| **D. Biomécanique scientifique** | pennation, ligne d'action, OpenSim/AnyBody | **le vecteur de force suit la direction des fibres** ; angle de pennation | légitime le positionnement « instrument biomécanique » via overlay technique | rigueur = risque de surcharge → overlay activable, pas défaut |
| **E. « Muscle maps » produit fitness** | Muscle Map app, DAREBEE, heatmaps | silhouette plate + muscles highlightables ; couleur runtime évidente | perf mobile, sobriété native | **corps entier = zéro pédagogie locale** — c'est le vide que les Focus Plates comblent |

**Grammaire « Auren Terminal » retenue** (synthèse A–E) : cadrage local · hiérarchie à 3 rangs (aplat cible /
teinte désaturée synergiste / trait seul adjacent) · clean view + technical overlay · **profondeur par le
trait pointillé atténué, jamais par gradient/ombre** · ancrage osseux minimal · ≤ 3 teintes actives · label
hors surface.

## 2. Réutilisable / dérivable / seulement consultable — matrice de sources

Licences **vérifiées** aux URL officielles (2026-07-24). Rôles : **G**éométrie · **S**tyle · **V**alidation ·
**I**nspiration.

| Source | Licence (vérifiée) | Rôle | Dérivable master propriétaire ? |
|---|---|---|---|
| **Servier Medical Art** | **CC BY 4.0** | G + S | ✅ oui — attribution |
| **OpenStax A&P 1ʳᵉ éd. (2013)** | **CC BY 4.0** | G + V | ✅ oui — attribution (vérifier crédit **par figure**) |
| **Gray's Anatomy (1918)** | **Domaine public** | G + S | ✅ oui — sans obligation (attribution = courtoisie) |
| **NLM Visible Human** | **PD / T&C** (accord de licence retiré 2019, *acknowledgment* NLM subsiste) | G + V | ✅ oui (géométrie), acknowledgment NLM |
| **Atlas historiques PD** (Bourgery, Vesalius, Sobotta/Spalteholz < 1929) | **Domaine public** | G + S | ✅ oui |
| **BodyParts3D / Anatomography** | **CC BY 4.0** (DBCLS officiel, maj 2025-02-27) | V | ⚠️ dérivation licite **mais** rôle retenu = **validation** (mesh = expression protégée → on ne trace pas) |
| **Z-Anatomy** | **CC BY-SA 4.0** (+ composants NC) | V | ❌ non (SA + NC) — validation/nommage seulement |
| **AnatomyTOOL** | **par ressource** (CC BY / SA / NC / CC0) | V (CC BY/CC0) | ⚠️ item par item, jamais en bloc |
| **Wikimedia Commons** | **par fichier** (PD / CC0 / BY / SA / non-libre) | G si PD/CC0/BY | ⚠️ fichier par fichier |
| **OpenStax A&P 2ᵉ éd.** | **CC BY-NC-SA 4.0** | — | ❌ **exclu** (NC + SA) |
| **MuscleWiki** | **Copyright — all rights reserved** | — | ❌ inutilisable |
| **BioDigital / BioRender / Complete Anatomy / Kenhub / Muscle&Motion** | Propriétaire | I | ❌ inspiration via accès licencié seulement |

**Wikimedia `Muscles front and back.svg`** (CC BY-SA 4.0, dérivé OpenStax) : **prototype jetable uniquement**,
**exclu de tout master livré** (héritage BodyMap) — un prototype ShareAlike **ne se blanchit pas**.

## 3. Implications licence (règles de tri, héritées du BodyMap)

- **CC BY (4.0/3.0)** → dérivation propriétaire **licite** + **attribution irrévocable** (crédit + lien
  licence + mention « modifié »). Voie royale : **Servier + OpenStax 1ʳᵉ éd.**
- **CC BY-SA** → **copyleft** : dérivation rediffusée sous la même licence → **incompatible master
  propriétaire**. BodyParts3D **n'est pas SA** (cf. §0) mais son **mesh** reste une expression protégée →
  rôle **validation**. Z-Anatomy = SA → validation seulement.
- **CC BY-NC / NC-SA** → **exclu** (produit commercial visé). OpenStax **2ᵉ éd.** hors-jeu.
- **CC0 / PD** → liberté totale (attribution = traçabilité). Gray's 1918, Visible Human, items CC0.
- **Copyright** → inutilisable (MuscleWiki, BioDigital, BioRender).
- **Agrégateurs** (Commons, AnatomyTOOL, Sketchfab, PICRYL) → **licence par fichier**, jamais globale ;
  remonter à la page-source, journaliser licence + URL par asset.

**Nuance conservée** (identique au BodyMap) : Auren possède **sa contribution créative** (simplification,
stylisation, regroupement fonctionnel), **pas** les données anatomiques sous-jacentes. « Auren owns the plate »
sans qualification resterait **faux** ; formulation honnête = *« plaque Auren, œuvre dérivée de <source>
(CC BY 4.0), attribution conservée »*.

## 4. Politique IA (last resort borné)

Plan **B/C, jamais A**. **Jamais vérité anatomique** (validation obligatoire contre BodyParts3D/Z-Anatomy/
Gray's) · **jamais géométrie finale livrée** · périmètre = moodboard / palette / composition non anatomique /
variantes de rendu **sur géométrie déjà validée de source propre** · **toujours déclarée** (registre par
asset, rôle exact) · **ne jamais injecter une image propriétaire en entrée**.

## 5. Cas d'exigence — faits anatomiques (domaine du savoir, extractibles)

Faits biomécaniques utilisés comme **contraintes de forme** dans la spec §16 (sources factuelles, non
protégées) :
- **Pectoraux** : chef claviculaire (fibres inféro-latérales) + chef sterno-costal (fibres horizontales)
  **convergent en éventail** vers l'humérus (lèvre latérale du sillon intertuberculaire) → dessiner la
  **convergence**, pas deux blobs (« poumons »).
- **Deltoïdes** : origines antérieur = clavicule · latéral = acromion · postérieur = épine scapulaire ;
  insertion commune tubérosité deltoïdienne → **3 faisceaux ancrés sur l'os**.
- **Chaîne postérieure** : grand fessier (extenseur de hanche) + ischios (biceps fémoral, semi-tendineux,
  semi-membraneux) ; insertion ischiatique commune ; couple de force avec les abdominaux.
- **Lats vs upper_back** : grand dorsal = nappe large/fine (largeur, V-taper, traction verticale) ;
  trapèzes+rhomboïdes = épaisseur (traction horizontale), rhomboïdes **sous** les trapèzes.
- **Core** : rectus (six-pack, intersections tendineuses) + obliques (diagonaux) + transverse (profond,
  **corset horizontal**) → message **stabilité/fonction**.

## 6. Conséquences produit

- La **valeur différenciante** d'Auren vs les « muscle maps » plein-corps = **crop local + marquage
  d'insertion** (absents de la famille E).
- La grammaire **clean view / technical overlay** (fibres + vecteur suivant les fibres) porte le
  positionnement « instrument biomécanique » **sans** rendu médical.
- Les **5 garde-fous anti-caricature** sont des **contraintes de forme anatomique**, pas des choix de style —
  donc **objectivement vérifiables** en revue.
- La stratégie de sources est **cohérente avec le précédent BodyMap** (source-reuse-first, CC BY, attribution,
  non-médical) → dette existante `ATTRIBUTION SURFACE: NOT YET IMPLEMENTED` **héritée**, non aggravée.

## 7. Limites de ce document

- **Pas un avis juridique.** Qualification finale (œuvre dérivée vs originale, portée d'attribution) = conseil
  professionnel. Relevés **datés 2026-07-24** — re-vérifier à chaque acquisition réelle (BodyParts3D vient
  précisément d'administrer la preuve qu'une licence change).
- **Aucune archive téléchargée, aucun mesh inspecté, aucun asset produit.**
- `PROFESSIONAL LEGAL CLEARANCE: NOT CLAIMED` · `ASSET INTEGRATION GATE: BLOCKED`.

## Sources consultées (2026-07-24)

**Licences officielles** : BodyParts3D DBCLS `https://dbarchive.biosciencedbc.jp/en/bodyparts3d/lic.html`
(CC BY 4.0, maj 2025-02-27) · miroir GitHub **historique/périmé** `Kevin-Mattheus-Moerman/BodyParts3D`
(CC BY-SA 2.1 JP) · Servier `https://smart.servier.com/terms-of-use/` (CC BY 4.0) · OpenStax A&P 1ʳᵉ éd.
`https://openstax.org/books/anatomy-and-physiology/pages/preface` (CC BY 4.0) · OpenStax A&P 2ᵉ éd.
`https://openstax.org/books/anatomy-and-physiology-2e/pages/1-introduction` (CC BY-NC-SA 4.0) · Z-Anatomy
(CC BY-SA 4.0) · AnatomyTOOL `https://anatomytool.org/legal-information` (par ressource) · MuscleWiki
`https://musclewiki.com/copyright` (copyright) · NLM Visible Human
`https://www.nlm.nih.gov/research/visible/getting_data.html` (PD/T&C) · Gray's 1918 (PD, Wikimedia) ·
textes CC : `creativecommons.org/licenses/by/4.0/`, `/by-sa/4.0/`, `/by-nc-sa/4.0/`, `/publicdomain/zero/1.0/`.

**Principes anatomiques/biomécaniques** (domaine du savoir) : pennation/ligne d'action (Springer
`10.1007/s10237-024-01837-3`, PNAS `10.1073/pnas.0709212105`) · pectoral (StatPearls NBK525991) · deltoïde
(fitstep muscle anatomy) · chaîne postérieure (JOSPT `10.2519/jospt.2010.3025`, ischios StatPearls NBK546688)
· lats/dos (Kenhub latissimus-dorsi) · core (Cleveland Clinic 21755, Physiopedia Abdominal_Muscles).

**Œuvres/produits protégés — références conceptuelles NON copiables** : Netter, Delavier (Human Kinetics),
Complete Anatomy, BioDigital, Muscle & Motion, Kenhub Atlas, Proko, Muscle Map app, DAREBEE.

## Verdict

**Verdict :** 🟢 **MUSCLE FOCUS REFERENCE RESEARCH: DONE.** Familles de références étudiées et **principes
extraits** (jamais d'œuvre copiée) ; **contradiction de licence BodyParts3D arbitrée** par croisement
adversarial (**CC BY 4.0** officiel, le relevé « CC BY-SA » venait du miroir GitHub figé — piège déjà résolu
au BodyMap) ; matrice de sources vérifiée (**Servier + OpenStax 1ʳᵉ éd. + PD = géométrie dérivable** ;
**BodyParts3D/Z-Anatomy = validation seulement** ; **MuscleWiki/BioDigital/BioRender/OpenStax 2ᵉ éd. =
exclus**) ; nuance mesh-vs-fait conservée ; IA = plan B/C borné et déclaré ; 5 cas d'exigence exprimés en
contraintes de forme vérifiables. **Aucun asset produit, aucune œuvre dupliquée, aucune archive téléchargée.**
`PROFESSIONAL LEGAL CLEARANCE: NOT CLAIMED` · `ASSET INTEGRATION GATE: BLOCKED`.
