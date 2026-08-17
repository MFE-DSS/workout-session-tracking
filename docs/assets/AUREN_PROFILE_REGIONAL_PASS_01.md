# `AUREN_PROFILE_REGIONAL_PASS_01` — bon de commande asset

**Remplace la formulation « profil corps entier ».**
Destinataire : workspace opérateur externe (BodyParts3D → Blender → Potrace →
Inkscape). Contrat de référence : `docs/strategy/Sb_BODYMAP_IDENTITY_CONTRACT_01.md`.

---

## 1. Ce qui était mal commandé, et pourquoi

Le CR *Atlas des Cadres* énonçait un résultat juste — **le plan profil révèle 9
zones sur 11** — mais il l'a formulé comme « produire le profil corps entier ».
Lu comme une commande d'asset, c'était inexploitable :

| Contrainte du runtime | Conséquence pour un SVG corps entier unique |
|---|---|
| Les panneaux font **2048 × 2048**, carrés | un corps entier de profil est un sujet **en portrait** : dans un panneau carré, un filet vertical entouré de vide |
| Le cadre recadre en `aspect-ratio: 1/1` | pas de dérogation possible sans toucher le moteur filmstrip |
| Le modèle ne connaît que `RegionalPlate(region, zones)` | **aucun type « plaque corps entier »** n'existe |
| Exigence « lisible à taille cockpit » | un corps entier réduit à une vignette de 320 px est illisible par construction |

**Le malentendu portait sur le mot « passe ».** « Profil corps entier » désignait
une **passe de caméra** — un seul réglage dans Blender éclaire 9 zones — pas
**un seul fichier livré**.

## 2. Ce qui est commandé

> **Une passe caméra `profile`, exportée en panneaux régionaux carrés.**

Même gain de production (un réglage de caméra, une session), zéro changement de
contrat, zéro changement de runtime.

### Table cible

| Plaque | État actuel | Cadres après la passe | Zones servies |
|---|---|---|---|
| `chest` | existe (`front`) | `front` + **`profile`** | `pecs` |
| `posterior` | existe (`back`) | `back` + **`profile`** | `posterior` |
| `back` | **n'existe pas** | `back` + **`profile`** | `lats`, `upper_back` |
| `arms` | **n'existe pas** | `front` + `back` + **`profile`** | `biceps`, `triceps` |
| `legs` | **n'existe pas** | `front` + `back` + **`profile`** | `quads`, `calves` |
| `core` | **n'existe pas** | `front` + **`profile`** | `core` |

Avec `shoulders` (déjà `front` + `back`, plan révélateur = `top`, hors de cette
commande), les **onze zones** sont couvertes exactement une fois.

### Séquencement — à ne pas manquer

Pour **7 des 9 zones**, le panneau `profile` arriverait sur une plaque qui n'a
**aucun autre panneau**. Commander « le profil » seul ferait rendre le corps deux
fois au workspace. La passe `profile` doit donc être produite **dans la même
session** que les cadres manquants des plaques `back`, `arms`, `legs` et `core`.

---

## 3. Contraintes de production

### 3.1 Géométrie du fichier

- Panneaux **2048 × 2048**, carrés. Sans exception.
- Filmstrip **horizontal** : N panneaux côte à côte,
  `viewBox="0 0 {2048×N} 2048"`, chaque vue translatée de `2048 × index`.
- **Pas de plaque corps entier.** `RegionalPlate` uniquement.

### 3.2 Structure de groupes

```xml
<svg id="auren-plate-region-{region}" viewBox="0 0 {2048*N} 2048">
  <g class="auren-mf-view-{frame}" transform="translate({2048*i},0)">
    <g class="auren-mf-context"> … </g>          <!-- TOUJOURS premier -->
    <g class="auren-mf-hero|auren-mf-part"> … </g>
  </g>
</svg>
```

- Le **cadre est porté par le groupe** `auren-mf-view-{frame}`, jamais déduit du
  nom d'un identifiant.
- **Contexte toujours premier** dans chaque cadre.
- **Ordre des surfaces identique** dans tous les cadres d'une même plaque.

### 3.3 Grammaire des identifiants

```
auren-plate-region-{region}--[{frame}-]{surface}-{NNN}
```

Segment `{frame}` obligatoire dès que la plaque a plus d'un cadre ; omissible sur
une plaque mono-cadre (précédent `chest`). Compteur à **trois chiffres**, à partir
de `000`.

### 3.4 Noms de surface attendus

Le validateur les connaît déjà : une surface hors de cette liste est **rejetée**.

| Plaque | Surfaces |
|---|---|
| `back` | `context`, `lats`, `upper-back` |
| `arms` | `context`, `biceps`, `triceps` |
| `legs` | `context`, `quads`, `calves` |
| `core` | `context`, `core` |
| `chest` | `context`, `hero` |
| `posterior` | `context`, `gluteus`, `hamstring` |

### 3.5 Interdits

- **Aucune nouvelle zone métier.** Notamment ni `delt_ant`, ni scission de
  `pecs` (`pec_clavicular` / `pec_sternal`).
- **Aucune anatomie générative.** Production déterministe depuis BodyParts3D.
- Pas de `<script>`, pas de `<image>`, pas de raster embarqué.
- Pas de `style="fill:…"` inline : la couleur appartient au contrat, une valeur
  inline la reprendrait au runtime.
- Aucun renommage d'identifiant existant.

---

## 4. Double porte de recette

Une livraison franchit **deux portes distinctes**, dans cet ordre.

**Porte 1 — structurelle, automatique, dans le dépôt.**

```bash
python scripts/bodymap_asset_intake.py chemin/vers/candidat.svg
```

Vérifie : racine et `viewBox`, panneau carré, cohérence panneaux ↔ cadres,
contexte premier, ordre des surfaces stable, grammaire et unicité des
identifiants, cadre lu sur le groupe, correspondance surface → zone métier,
absence de zone interdite, sûreté runtime. Sort `PASS`/`FAIL` avec la table
`cadre / surface / zone / id`, les surfaces non mappées et les zones attendues
non couvertes.

**Porte 2 — anatomique, humaine, hors dépôt.**

Un `PASS` structurel dit que le fichier **se câblera et se colorera
correctement**. Il ne dit **rien** de la justesse anatomique des formes. Le
rapport le répète à chaque exécution. Le dépôt ne dessine pas d'anatomie et n'en
juge pas.

---

## 5. Livrables attendus par plaque

1. le SVG conforme au §3 ;
2. la sortie du validateur d'intake en `PASS` ;
3. la liste surfaces / identifiants (le validateur la produit) ;
4. la capture de **revue anatomique humaine**, avec le nom du relecteur ;
5. une note de simplification si le tracé est trop dense pour la vignette
   cockpit — voir §6.

---

## 6. Simplification cockpit

Une planche `4096 × 2048` est superbe en pleine page *science* et illisible dans
une vignette d'accueil. Si le tracé est trop dense :

- la simplification doit être **dérivée** des tracés — réduction du nombre de
  points en conservant l'implantation osseuse et l'orientation des fibres ;
- **jamais un redessin libre**, qui rendrait la fidélité affaire de jugement au
  lieu d'être une propriété du fichier ;
- les identifiants et l'ordre des groupes sont **conservés à l'identique** entre
  la planche dense et la version simplifiée.

---

## 7. Décision ouverte

### `OQ_FRAME_DEFAULT_ORDER_01` — quel cadre est le cadre par défaut

Le sélecteur coche le **premier cadre déclaré**. Or `FRAME_ORDER` vaut
`(front, profile, back, top)` : pour une plaque `back`, l'ordre canonique
placerait `profile` **avant** `back`, faisant du plan révélateur le cadre par
défaut — l'inverse de l'intention produit, où le **plan logique** doit s'ouvrir
en premier.

Trois issues possibles :

1. réordonner `FRAME_ORDER` en `(front, back, profile, top)` — les plans logiques
   d'abord, le révélateur ensuite ; `shoulders` reste inchangé et toutes les
   plaques commandées tombent juste ;
2. dissocier « ordre canonique » et « cadre par défaut », en déclarant le défaut
   par plaque ;
3. laisser chaque plaque déclarer ses cadres dans l'ordre voulu, sans ordre
   canonique.

**Non tranchée ici** : elle touche le runtime, hors périmètre de ce sprint. Le
validateur **n'émet volontairement aucun avertissement** sur l'ordre des cadres —
il pousserait le workspace à livrer `profile` en premier, c'est-à-dire à trancher
la question par accident.

À décider **avant** l'intégration de la première plaque `back`, `arms`, `legs` ou
`core` — pas avant la production, qui n'en dépend pas.

---

## Verdict

**COMMANDE EXPLOITABLE.**

La formulation « profil corps entier » est remplacée par une passe caméra
exportée en panneaux régionaux carrés : même gain biomécanique, compatible avec
le moteur livré, sans changement de contrat ni de runtime.

Ce que le dépôt apporte : une grammaire non ambiguë, une structure imposée, des
critères de rejet explicites, et une **porte structurelle automatique** exécutable
avant qu'un humain ne dépense une revue anatomique sur un fichier mal câblé.

Ce que le dépôt n'apporte pas, et ne prétend pas apporter : la géométrie, la
revue anatomique, et la garantie de lisibilité cockpit — cette dernière ne pourra
être vérifiée qu'après intégration d'un asset réel.
