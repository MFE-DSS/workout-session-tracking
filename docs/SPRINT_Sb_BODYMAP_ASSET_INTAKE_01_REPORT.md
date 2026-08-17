# `Sb_BODYMAP_ASSET_INTAKE_01` — porte structurelle et bon de commande

**Base** : `57be4f4` · **Tier `check_scope`** : `CI_INFRA` · **Aucun asset produit**

---

## 1. Ce que le sprint livre

Deux choses, et rien d'autre :

1. **Une porte structurelle** — `scripts/bodymap_asset_intake.py` valide un SVG
   candidat contre le contrat d'identifiants **avant** qu'un humain n'y dépense
   une revue anatomique.
2. **Un bon de commande versionné** —
   `docs/assets/AUREN_PROFILE_REGIONAL_PASS_01.md` remplace la formulation
   « profil corps entier » par « passe caméra `profile` exportée en panneaux
   régionaux ».

Le dépôt **ne produit pas de SVG**, **n'exécute pas** Blender/Potrace/Inkscape et
**ne juge pas** l'anatomie. C'est une porte, pas une usine.

---

## 2. Brainstorming / Options / Risques / Choix (CLAUDE.md §3)

**Option A — validateur permissif** qui accepte toute surface et se contente de
la lister. Rejetée : le brief exige le rejet d'une surface non reliable à une
zone métier, et une porte qui laisse tout passer donne une fausse assurance.

**Option B — validateur qui déduit la zone du nom de surface.** Rejetée : c'est
exactement la porte dérobée par laquelle un asset créerait une zone métier.
`delt-anterior` en est la preuve vivante — un nom anatomique légitime qui ne doit
**pas** devenir une zone.

**Option C — retenue : table de correspondance explicite.**
`SURFACE_ZONE_MAP` déclare chaque surface porteuse d'état, `NON_ZONE_SURFACES`
adjuge celles qui n'en portent pas (`context` → IGNORE, `delt-anterior` → MERGE),
et **toute surface inconnue est une erreur bloquante**. Le modèle métier
gouverne ; l'asset ne propose rien.

**Risque principal** : écrire une porte qui rejette les assets déjà livrés. Il
s'est **matérialisé** — voir §4.

---

## 3. Le bon de commande corrigé

La formulation initiale était inexploitable, et la cause est mesurable :

| Contrainte runtime | Effet sur un SVG corps entier unique |
|---|---|
| panneaux **2048 × 2048** carrés | sujet en portrait → filet vertical entouré de vide |
| `aspect-ratio: 1/1` | pas de dérogation sans toucher le filmstrip |
| `RegionalPlate(region, zones)` seul type | **aucune plaque corps entier** n'existe |

« Profil corps entier » désignait une **passe de caméra**, pas un fichier.
Reformulé : une passe, exportée en **6 plaques régionales**, couvrant les onze
zones exactement une fois — un test le vérifie
(`test_ordered_regions_cover_the_eleven_zones_exactly`).

**Séquencement signalé** : pour 7 des 9 zones, le panneau `profile` arriverait
sur une plaque sans aucun autre panneau. Commander le profil seul ferait rendre
le corps deux fois. La passe doit sortir dans la **même session** que les cadres
manquants de `back`, `arms`, `legs`, `core`.

---

## 4. Ma propre porte a rejeté un asset approuvé

Premier passage du validateur sur les trois plaques livrées :

```
=== PASS ===  chest
=== FAIL ===  shoulders   7 × FORBIDDEN_ZONE_TOKEN
=== PASS ===  posterior
```

**L'asset avait raison, mon guard avait tort.** `FORBIDDEN_ZONE_TOKENS`
contenait `"delt-ant"`, testé en **sous-chaîne de l'identifiant** — or
`delt-ant` est un préfixe de `delt-anterior`, la surface que le contrat autorise
explicitement en MERGE.

Correction de fond, pas de contournement : l'interdit porte désormais sur le
**jeton de surface normalisé**, comparé **exactement** à un ensemble de codes de
zone, et une surface déjà adjugée dans `NON_ZONE_SURFACES` en est **exemptée** —
le contrat a statué qu'elle est une surface, et une surface n'est pas une zone.
Un test pinne précisément ce cas
(`test_adjudicated_surfaces_are_exempt_from_the_forbidden_check`).

C'est la **sixième** occurrence du même motif dans ce programme : une garde
formulée trop largement. Elle a été attrapée ici parce que la porte a été
essayée sur du **réel** avant d'être déclarée bonne.

### Un avertissement retiré parce qu'il poussait au mauvais choix

Le validateur signalait initialement un ordre de cadres non canonique.
`FRAME_ORDER` vaut `(front, profile, back, top)` : pour une plaque `back`,
respecter cet ordre placerait `profile` **en premier**, donc **en cadre par
défaut** — l'inverse de l'intention produit, où le plan logique doit s'ouvrir.

Le workspace aurait « corrigé » ses livraisons pour faire taire l'avertissement,
tranchant la question **par accident**. L'avertissement est supprimé et la
tension enregistrée en `OQ_FRAME_DEFAULT_ORDER_01`. **Un validateur ne doit pas
suggérer une décision que personne n'a prise.**

---

## 5. Acceptation

| # | Critère | Méthode | Résultat |
|---|---|---|---|
| A1 | Commande corrigée | garde sur la section « ce qui est commandé » | **PASS** |
| A2 | Pas de nouveau type runtime | balayage `app/**` (`FullBodyPlate`, …) | **PASS** |
| A3 | Validateur exécutable | CLI, codes de sortie 0/1/2, sous-processus réel | **PASS** |
| A4 | SVG existants inchangés | SHA gelés + 3/3 PASS à l'intake | **PASS** |
| A5 | Grammaire et unicité des ids | fixtures | **PASS** |
| A6 | Structure `view → context → surfaces` | fixtures | **PASS** |
| A7 | Rejet des tokens interdits | fixture `pec-clavicular` | **PASS** |
| A8 | Structure ≠ anatomie | présent dans **chaque** rapport | **PASS** |
| A9 | Diff métier vide | §7 | **PASS** |

### Preuves par plantation

Quatre altérations injectées dans une **plaque réelle**, chacune rejetée pour la
bonne raison :

| Altération | Code émis |
|---|---|
| identifiant renommé | `SURFACE_UNMAPPED` |
| compteur non `NNN` | `ID_GRAMMAR` |
| surface `pec-clavicular` | `FORBIDDEN_ZONE_TOKEN` + `SURFACE_UNMAPPED` |
| `style="fill:…"` inline | `INLINE_FILL` |

Et huit fixtures structurelles couvrent contexte non premier, ordre de surfaces
instable, panneau non carré, `<script>`, `<image>`.

### Les fixtures ne contiennent aucune anatomie

Chaque `<path>` porte `M0 0 L1 1` — un segment de deux points. **Un test
l'exige** (`test_fixtures_contain_no_anatomical_geometry`) : le dépôt ne dessine
pas d'anatomie, pas même en donnée de test.

### Sécurité de l'entrée

Les candidats viennent d'un workspace externe : l'entrée est **non fiable**.
Plutôt que de taire l'avertissement `S314`, la classe d'attaque est **éliminée** —
un fichier déclarant une DTD ou des entités est rejeté (`DTD_PRESENT`) avant tout
parsing, et une plaque n'a aucune raison d'en porter une.

---

## 6. Vérifications locales

Tier `CI_INFRA` — **full sweep local exigé**, contrairement aux sprints
précédents. Le script n'est invoqué par aucun workflow, mais `CLAUDE.md` §1 dit
de remonter d'un cran en cas de doute, jamais de descendre.

| Check | Résultat |
|---|---|
| `check_scope.py` | `CI_INFRA` |
| ruff (fichiers neufs) | propre |
| `check_ruff_budget.py` | 281 ≤ 548 |
| `check_spec_protocol.py` | OK |
| Suite d'intake | **33 passés** |
| **Full sweep local** | **4 830 passés** en 4 min 18 |

---

## 7. A9 — diff sur les fichiers protégés

| Cible | Diff |
|---|---|
| `app/services/recommendation.py` | **vide** |
| planificateur / `slot_intent` | **vide** |
| `app/models.py` · `migrations/` | **vide** |
| `app/services/muscle_mapping.py` | **vide** |
| runtime BodyMap (`bodymap_frames.py`, templates, CSS) | **vide** |
| les 3 SVG | **vide** |
| PR dependabot | non touchées |

Le sprint n'ajoute que `scripts/`, `tests/` et `docs/`.

---

## 8. Limites

**Pas de production SVG.** Les maillages BodyParts3D ne sont pas versionnés ; le
dépôt ne peut produire aucun cadre.

**Pas de revue anatomique.** Un `PASS` structurel dit que le fichier se câblera
et se colorera correctement. Il ne dit **rien** de la justesse des formes. Le
rapport le répète à chaque exécution, et un test l'exige.

**Aucune garantie cockpit sans asset réel.** La lisibilité d'une plaque en
vignette 360 px ne peut être vérifiée qu'après intégration d'une géométrie
véritable. Le §6 du bon de commande fixe la règle de simplification — dérivée,
jamais redessinée — mais elle reste à éprouver.

**La table des surfaces est déclarative, pas devinée.** `back`, `arms`, `legs`
et `core` y figurent avec les noms attendus : c'est ce qui rend le bon de
commande vérifiable par machine. Une plaque livrée avec d'autres noms est
rejetée, ce qui est le comportement voulu — mais suppose que le workspace lise
le §3.4.

**`OQ_FRAME_DEFAULT_ORDER_01` reste ouverte.** À trancher avant l'intégration de
la première plaque `back`/`arms`/`legs`/`core`, pas avant leur production.

---

## Verdict

**PORTE LIVRÉE, COMMANDE EXPLOITABLE.**

Le validateur accepte les trois plaques livrées et rejette huit classes de
non-conformité, chacune prouvée par fixture ou par plantation sur un asset réel.
Le bon de commande remplace une formulation qui aurait produit un fichier
inaffichable.

Le fait marquant du sprint n'est pas le validateur : c'est qu'il a **rejeté un
asset approuvé au premier essai**, et que le défaut était dans ma garde, pas dans
l'asset. Une porte structurelle qui n'est pas essayée sur du réel avant d'être
déclarée bonne est une panne en attente.

Second fait, moins visible : un avertissement a été **retiré** parce qu'il aurait
poussé le workspace à trancher une question ouverte sans le savoir. Un outil de
validation doit refuser ce que le contrat interdit — pas orienter ce que le
contrat n'a pas décidé.
