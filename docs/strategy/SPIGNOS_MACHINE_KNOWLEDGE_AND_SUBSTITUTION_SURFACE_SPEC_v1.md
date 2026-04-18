# SPIGNOS Machine Knowledge & Substitution Surface Spec v1

**Sprint:** Sx_07_machine_knowledge_and_substitution_surface_spec
**Date:** 2026-04-15
**Status:** Spec detaillee (SPEC ONLY)
**Prerequisite:** Sx_05 + Sx_06 valides
**Parallelisable avec:** Sx_08 (Session Review Intelligence)
**Debloque:** Sb_07 (Machine Knowledge + Substitution UX build)

---

## 0. Objet

Specifier 3 livrables qui ajoutent une **couche de connaissance machine** au produit sans alourdir le flow de saisie :

1. **Atlas machine** — taxonomie + catalogue minimal (30 machines V1)
2. **Lien exercice → machine/famille** — enrichissement du catalogue exercices
3. **Surfaces UX** — icone `i` dans chaque carte exercice + drawer substitution affine + page `/atlas` dediee

Respect strict des **6 garde-fous Sx_02 FINAL** : ne casse pas le composant exercice.

---

## 1. Principes directeurs

Reaffirme de Sx_05 + specificites Sx_07 :

| Principe | Application |
|----------|-------------|
| SSR only | Zero JS. `<details>` natif, navigation par fragment, progressive enhancement optionnel |
| Mobile-first | Panneau court, fermable au tap, ne deborde pas le viewport |
| Compact | Max 30 machines V1. Pas de prose encyclopedique. 3-6 cues par machine. |
| Optionnel | Carte exercice sans `machine_slug` reste fonctionnelle (degradation gracieuse) |
| Versionne | Atlas bumpe en version comme le catalogue |
| Zero migration | Loader in-memory V1, pas de table DB |

---

## 2. Atlas machine — schema et contenu

### 2.1 Fichier source

`data/machine_atlas.json` — fichier dedie, independant de `reference_split.json`.

Isolation de gouvernance : catalogue exercices et atlas machine evoluent separement, avec des cadences differentes.

### 2.2 Structure JSON proposee

```json
{
  "version": "2026-04-15.v1",
  "title": "Atlas machines SPIGNOS",
  "families": [
    {
      "slug": "pecs-press",
      "name": "Pectoraux — Developpe",
      "zone": "pecs",
      "description": "Pressing horizontal ou incline ciblant le grand pectoral. Charges modulables.",
      "machines": [
        {
          "slug": "chest-press-machine",
          "name": "Chest Press machine",
          "aliases": ["Chest press", "Presse pectorale"],
          "variants": ["convergente", "independante", "bras fixes"],
          "equipment": "machine",
          "laterality": "bilateral",
          "load_semantics": "total",
          "execution_cues": [
            "Dos plaque au dossier",
            "Omoplates basses et serrees en fin de course basse",
            "Ne pas verrouiller les coudes en haut"
          ],
          "common_mistakes": [
            "Dosage du poids trop lourd qui casse l'amplitude",
            "Elevation des epaules sur la phase positive"
          ]
        }
      ]
    }
  ]
}
```

### 2.3 Regles de contenu

| Champ | Type | Obligatoire | Role |
|-------|------|-------------|------|
| `slug` (family) | str (kebab-case) | Oui | Identifiant stable reference par exercices |
| `name` (family) | str | Oui | Libelle affichage |
| `zone` | str | Oui | Zone primaire (pecs/delt_lat/delt_post/lats/upper_back/biceps/triceps/quads/posterior/calves/core) — doit matcher `muscle_mapping.ZONE_LABELS` |
| `description` (family) | str court | Oui | 1-2 phrases max |
| `machines` | list | Oui | Au moins 1 machine par famille |
| `slug` (machine) | str | Oui | Identifiant stable reference par exercices |
| `name` (machine) | str | Oui | Libelle canonique |
| `aliases` | list[str] | Non | Synonymes courants (aide matching) |
| `variants` | list[str] | Non | Declinaisons courantes |
| `equipment` | str | Oui | machine/barre/haltere/cable/body/smith |
| `laterality` | str | Oui | bilateral/unilateral/both |
| `load_semantics` | str | Oui | total/per_side/bw_added |
| `execution_cues` | list[str] | Oui | 3-6 points cles, 1 phrase chacun |
| `common_mistakes` | list[str] | Non | 2-4 erreurs frequentes |

### 2.4 Contraintes V1

- Max **30 machines** V1
- Max **8 familles** V1
- Max **6 cues** + **4 mistakes** par machine
- Total fichier < 100 lignes JSON (~10 KB)

### 2.5 Catalogue V1 propose (8 familles, 30 machines)

| Famille | Machines V1 |
|---------|-------------|
| Pectoraux — Developpe | Chest Press machine, Incline Smith Press, Developpe couche halteres, Developpe incline halteres 30° |
| Pectoraux — Fly / Ecarte | Butterfly machine, Cable cross-over, Ecarte halteres |
| Dos — Verticaux | Lat pulldown, Traction assistee machine, Pull-up poids corps, Pullover machine |
| Dos — Horizontaux | Rowing chest-supported, Rowing cable assis, Rowing haltere un bras |
| Epaules — Presse | Shoulder press machine, Smith shoulder press, Shoulder press halteres assis |
| Epaules — Lateral / Posterieur | Lateral raise machine, Elevations laterales cable, Rear delt fly machine, Face pull cable |
| Jambes — Quad dominant | Hack squat, Leg press, Smith squat, Leg extension |
| Jambes — Posterieur + mollets | RDL halteres, Hip thrust Smith, Leg curl assis, Leg curl allonge, Mollets debout, Mollets assis |

**Total : 30 machines.** Couvre 100% des exercices core v10.

### 2.6 Versionning + seed

- `data/machine_atlas.json` versione `YYYY-MM-DD.vN`
- Loader in-memory V1 (pas de seed en DB) : service `app/services/machine_atlas.py` lit le JSON au demarrage et expose un dict `{slug: machine}` + un dict `{family_slug: family}`
- Bumpe version a chaque ajout/modification de contenu
- QA script `scripts/machine_atlas_qa.py` valide : unicite slugs, zones existantes, cues minimum 3

### 2.7 Pourquoi in-memory plutot que DB

- Atlas est pure reference (lecture seule pour les users)
- Pas de FK depuis les tables DB vers l'atlas — lien se fait cote loader via string match
- Simplifie la gouvernance (git = source de verite)
- Pas de migration
- Charge negligeable (~10 KB)

---

## 3. Lien exercice → machine / famille

### 3.1 Enrichissement `reference_split.json`

Ajout de champs **optionnels** a chaque `TemplateExercise` :

```json
{
  "code": "E2",
  "name": "Chest Press machine",
  "set_scheme": "3x 8-12",
  "machine_slug": "chest-press-machine",
  "machine_family": "pecs-press",
  "substitutes": [...]
}
```

**Regle :** au moins un des deux doit etre renseigne si l'exercice a une correspondance dans l'atlas. Si aucun n'est renseigne, la carte exercice ne montre pas d'icone `i`.

### 3.2 Priorite de resolution

1. Si `machine_slug` renseigne → resolution precise (cue specifique)
2. Sinon si `machine_family` renseigne → resolution famille (generique)
3. Sinon → pas d'icone `i`

### 3.3 Nombre d'exercices concernes V1

Audit catalogue v10 : sur 96 exercices, **~30-40 peuvent etre lies** directement a l'atlas V1. Les autres (variations rares, exercices tres specifiques) restent sans lien — degradation gracieuse.

### 3.4 Version catalogue

Cette modification necessite bump `reference_split.json` → `2026-04-15.v11`.

Zero impact DB grace aux snapshots immutables des SessionExercise.

### 3.5 Regles de maintenance

Chaque nouveau exercice ajoute au catalogue doit :
- Soit referencer une machine existante (`machine_slug`)
- Soit la famille (`machine_family`)
- Soit explicitement declarer n'avoir pas de correspondance (champ absent, OK)

Le QA script existant `scripts/catalog_qa.py` etendu pour verifier :
- Les `machine_slug` referencees existent dans l'atlas
- Les `machine_family` referencees existent dans l'atlas
- Warning si exercice sans machine_slug ni machine_family mais correspond visiblement a une machine connue (heuristique tolerance)

---

## 4. Surfaces UX — 3 points d'entree

### 4.1 Icone `i` dans la carte exercice active

**Positionnement :** dans le `<summary>` de la carte (header compact), apres le nom de l'exercice, avant le progress compteur.

**Variante compacte collapsee (carte fermee) :**
```
▶ E2 Chest Press machine ⓘ    0/3
```

**Variante expandee (carte ouverte) :**
Header avec `<details>` toggle, icone `ⓘ` cliquable qui ouvre un panneau contextuel.

### 4.2 Panneau contextuel SSR

**Implementation :** imbrication de `<details>` native dans le body de la carte exercice, position **6** de l'ordre vertical fige (apres delta/hint, avant set lists).

**Structure HTML proposee :**

```html
<details class="machine-panel" open="false">
  <summary class="machine-panel__toggle">
    ⓘ Info machine
  </summary>
  <div class="machine-panel__body">
    <h4>Chest Press machine · <em>Pectoraux — Developpe</em></h4>
    <ul class="machine-panel__cues">
      <li>Dos plaque au dossier</li>
      <li>Omoplates basses et serrees en fin de course basse</li>
      <li>Ne pas verrouiller les coudes en haut</li>
    </ul>
    <details class="machine-panel__mistakes">
      <summary>Erreurs courantes</summary>
      <ul>
        <li>Dosage du poids trop lourd qui casse l'amplitude</li>
        <li>Elevation des epaules sur la phase positive</li>
      </ul>
    </details>
    <a class="machine-panel__more"
       href="/science/atlas#machine-chest-press-machine">
      Voir fiche complete →
    </a>
  </div>
</details>
```

**Contraintes :**
- Panneau entierement ferme par defaut (`<details>` sans `open`)
- Cues visibles une fois ouvert (liste de 3-6 items)
- Erreurs courantes en sous-`<details>` (double niveau acceptable ici — cf Sx_02 §5)
- Lien "Voir fiche complete" vers page `/science/atlas` ancree sur la machine
- Zero JS. Toggle natif.

**Alternative ecartee :** modale ou bottom-sheet. Rejet = necessiterait JS ou etat navigation complexe.

### 4.3 Refonte drawer substitution

**Etat actuel (session_detail.html L98-123) :**
```html
<details class="substitute-picker">
  <summary>Machine indisponible ? Substituer →</summary>
  <!-- radio group liste longue -->
</details>
```

**Propositions d'affinement V1 :**

1. **Wording plus explicite** : "Machine occupee ou non dispo ? Choisis un substitut" (remplace "Substituer →")
2. **Structure visuelle** : style dedie `.substitute-picker--drawer` avec padding accru, fond `var(--surface-elevated)`, border-left accent
3. **Option "garder prescrit"** mise en avant en premier avec badge `(prescrit)`
4. **Count affiche** : "2 alternatives" a cote du summary si des substituts existent

**Exemple markup cible :**

```html
<details class="substitute-picker substitute-picker--drawer">
  <summary class="substitute-picker__toggle">
    <span class="substitute-picker__label">Machine occupee ?</span>
    <span class="substitute-picker__count">2 alternatives</span>
  </summary>
  <div class="substitute-picker__body">
    <label class="substitute-option substitute-option--prescribed">
      <input type="radio" name="substituted_name" value="" checked>
      <span>
        <strong>Chest Press machine</strong>
        <small>prescrit</small>
      </span>
    </label>
    <label class="substitute-option">
      <input type="radio" name="substituted_name" value="Developpe couche halteres">
      <span>Developpe couche halteres</span>
    </label>
    <label class="substitute-option">
      <input type="radio" name="substituted_name" value="Dips pectoraux (buste penche)">
      <span>Dips pectoraux (buste penche)</span>
    </label>
  </div>
</details>
```

**Garde-fous Sx_02 respectes :**
- Position picker inchangee (bloc 4 du body du `<details>` exercice)
- `name="substituted_name"` conserve → parsing server inchange
- `can_substitute` lock inchange
- Fallback summary inchange
- Zero JS

### 4.4 Page `/science/atlas` dediee

**Route :** `GET /science/atlas` (sous-section de /science existante).

**Contenu :** affichage structure de l'atlas complet.

**Template propose :**

```html
{% extends "base.html" %}
{% block content %}
<h1 class="page-title">Atlas machines</h1>
<p class="lede">Les machines courantes de salle, organisees par famille.</p>

{% for family in atlas.families %}
<section class="atlas-family" id="family-{{ family.slug }}">
  <h2 class="section-header">{{ family.name }}</h2>
  <p class="text-dim">{{ family.description }}</p>

  {% for machine in family.machines %}
  <article class="atlas-machine card" id="machine-{{ machine.slug }}">
    <h3 class="card__title">{{ machine.name }}</h3>
    <dl class="atlas-machine__meta">
      <dt>Equipement</dt><dd>{{ machine.equipment }}</dd>
      <dt>Lateralite</dt><dd>{{ machine.laterality }}</dd>
      <dt>Charge</dt><dd>{{ machine.load_semantics }}</dd>
      {% if machine.variants %}
        <dt>Variantes</dt><dd>{{ machine.variants | join(', ') }}</dd>
      {% endif %}
    </dl>
    <h4>Execution</h4>
    <ul class="atlas-machine__cues">
      {% for cue in machine.execution_cues %}
      <li>{{ cue }}</li>
      {% endfor %}
    </ul>
    {% if machine.common_mistakes %}
    <h4>Erreurs courantes</h4>
    <ul class="atlas-machine__mistakes">
      {% for mistake in machine.common_mistakes %}
      <li>{{ mistake }}</li>
      {% endfor %}
    </ul>
    {% endif %}
  </article>
  {% endfor %}
</section>
{% endfor %}
{% endblock %}
```

**Navigation :** lien "Atlas machines" ajoute dans la section /science existante.

---

## 5. Service `app/services/machine_atlas.py`

Loader minimaliste :

```python
"""In-memory loader for the machine atlas.

Reads data/machine_atlas.json at import time and exposes lookup helpers.
No DB backing. Pure reference.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from app.config import BASE_DIR

ATLAS_PATH = BASE_DIR / "data" / "machine_atlas.json"


def _load_atlas() -> dict:
    with ATLAS_PATH.open("r", encoding="utf-8") as fh:
        return json.load(fh)


_ATLAS: dict = _load_atlas()
_MACHINES_BY_SLUG: dict[str, dict] = {}
_FAMILIES_BY_SLUG: dict[str, dict] = {}
for fam in _ATLAS.get("families", []):
    _FAMILIES_BY_SLUG[fam["slug"]] = fam
    for m in fam.get("machines", []):
        _MACHINES_BY_SLUG[m["slug"]] = {**m, "family_slug": fam["slug"], "family_name": fam["name"]}


def get_machine(slug: str) -> Optional[dict]:
    """Return the machine dict by slug, or None."""
    return _MACHINES_BY_SLUG.get(slug)


def get_family(slug: str) -> Optional[dict]:
    """Return the family dict by slug, or None."""
    return _FAMILIES_BY_SLUG.get(slug)


def all_families() -> list[dict]:
    """Return the full families list for the atlas page."""
    return _ATLAS.get("families", [])


def get_for_exercise(template_exercise) -> Optional[dict]:
    """Resolve a TemplateExercise to its machine or family, priority
    machine_slug > machine_family > None.

    Returns a dict with {kind, data} where kind is 'machine' or 'family'.
    """
    slug = getattr(template_exercise, "machine_slug", None)
    if slug:
        m = get_machine(slug)
        if m:
            return {"kind": "machine", "data": m}
    fam_slug = getattr(template_exercise, "machine_family", None)
    if fam_slug:
        f = get_family(fam_slug)
        if f:
            return {"kind": "family", "data": f}
    return None
```

**Test :** `tests/test_machine_atlas.py` — 5-8 tests (load, lookup, fallback, family).

---

## 6. Impacts sur les modeles existants

### 6.1 `TemplateExercise` — nouveaux champs

Ajout de 2 colonnes **optionnelles** :

```python
# app/models/catalog.py
machine_slug: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
machine_family: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
```

**Migration Alembic requise** : ALTER TABLE additive, sans rewrite. Zero impact historique.

### 6.2 Consumers a ajuster

| Surface | Impact | Action Sb_07 |
|---------|--------|--------------|
| `app/services/seed.py` | Lire `machine_slug` et `machine_family` depuis JSON v11, persister en DB | Ajout mineur |
| `app/routers/sessions.py` | Passer `machine_info` au contexte template (via `get_for_exercise`) | Ajout mineur |
| `app/templates/session_detail.html` | Afficher le panneau machine selon `machine_info` | Ajout |
| `app/templates/session_done.html` | Inchange (pas d'info machine sur /done) | Neutre |
| `app/routers/pages.py` ou nouveau `atlas.py` | Route `/science/atlas` | Ajout |
| `app/templates/science.html` | Lien "Voir atlas machines" | Ajout mineur |
| `scripts/catalog_qa.py` | Valider les `machine_slug` / `machine_family` referencees | Extension |

### 6.3 Snapshot SessionExercise

**Aucun changement snapshot.** `SessionExercise` ne stocke pas `machine_slug` — la resolution se fait via le lien `template_exercise` (nullable, peut etre perdu au reseed). C'est acceptable : l'info machine est editoriale, pas historique.

Si le template_exercise est detache (reseed avec slug change), la carte exercice perd le panneau `i`. Degradation gracieuse.

---

## 7. UX detaillee — flux complet

### 7.1 Carte exercice avec machine reconnue

```
┌──────────────────────────────────────┐
│ ▶ E2 Chest Press machine  ⓘ     0/3  │  ← compact, icone i visible
└──────────────────────────────────────┘

Au clic (carte active):
┌──────────────────────────────────────┐
│ ▼ E2 Chest Press machine  ⓘ     0/3  │
│                                      │
│   Voir historique →                  │
│   3x 8-12                            │
│                                      │
│   ▶ Machine occupee ? 2 alternatives │  ← drawer subst refait
│                                      │
│   ▶ ⓘ Info machine                   │  ← panneau machine natif
│                                      │
│   Dernière fois · il y a 3j          │
│   ...                                │
└──────────────────────────────────────┘

Au clic "ⓘ Info machine":
┌──────────────────────────────────────┐
│   ▼ ⓘ Info machine                   │
│   Chest Press machine                │
│   Pectoraux — Developpe              │
│                                      │
│   • Dos plaque au dossier            │
│   • Omoplates basses et serrees      │
│   • Ne pas verrouiller les coudes    │
│                                      │
│   ▶ Erreurs courantes                │
│                                      │
│   Voir fiche complete →              │
└──────────────────────────────────────┘
```

### 7.2 Exercice sans machine (degradation)

```
┌──────────────────────────────────────┐
│ ▶ E7 Ab wheel (roulette)    0/3      │  ← pas d'icone i, carte normale
└──────────────────────────────────────┘
```

Aucune gene visuelle. La carte fonctionne normalement.

### 7.3 Page `/science/atlas`

Navigation typee table des matieres implicite (scroll). Chaque machine est ancree par slug, accessible via lien direct `#machine-...`.

---

## 8. Tests prevus

### Unit

- `tests/test_machine_atlas.py` (nouveau) :
  - load JSON sans erreur
  - `get_machine` retourne dict correct pour slug valide
  - `get_machine` retourne None pour slug inconnu
  - `get_family` idem
  - `get_for_exercise` priorite machine > family > None
  - `all_families` retourne liste non-vide

### Integration

- `tests/test_atlas_routes.py` (nouveau) :
  - `GET /science/atlas` retourne 200
  - Contenu inclut familles + machines
  - Ancre `#machine-chest-press-machine` presente

### Regression catalogue

- `tests/test_catalog_integrity.py` etendu :
  - Chaque `machine_slug` reference existe dans atlas
  - Chaque `machine_family` reference existe dans atlas

### Regression session

- `tests/test_session_flow.py` : panneau `i` rendu conditionnel, carte sans machine fonctionne

---

## 9. Risques

| Risque | Probabilite | Mitigation |
|--------|------------|------------|
| Atlas V1 trop pauvre (users veulent plus de machines) | Moyen | OK, iterer. Gouvernance atlas simple = ajout incremental rapide. |
| `<details>` imbriques 2 niveaux (machine panel + mistakes) sur mobile | Faible | Sx_02 FINAL tolere 2 niveaux max ; teste iOS/Android |
| User deteste l'icone `i` sur chaque carte | Faible | Discrete par design, cliquable optionnel. Si feedback negatif, icone peut disparaitre. |
| Seed lit atlas qui n'existe pas | Tres faible | Fichier committe dans git = toujours present |
| Refacto drawer substitution casse Sb_02.1 mobile polish | Faible | Garde-fous Sx_02 respectes. Changements purement CSS + wording. |

---

## 10. Acceptance criteria Sx_07

| Critere | Statut |
|---------|--------|
| Schema `machine_atlas.json` defini exhaustivement | ✓ §2.3 |
| Contraintes V1 chiffrees (30 machines, 8 familles) | ✓ §2.4 |
| Catalogue V1 propose (listing 30 machines) | ✓ §2.5 |
| Lien exercice → machine/famille specifie | ✓ §3 |
| Service `machine_atlas.py` documente | ✓ §5 |
| UX panneau `i` detailee SSR | ✓ §4.2 |
| Refonte drawer substitution cadree (respecte Sx_02) | ✓ §4.3 |
| Page `/science/atlas` specifiee | ✓ §4.4 |
| Impacts consumers + migration Alembic mineure identifies | ✓ §6 |
| Tests prevus (unit + integration + regression) | ✓ §8 |
| Risques + mitigation | ✓ §9 |
| Zero JS, zero rework Sx_02 composant | ✓ |

---

## 11. Livrables Sb_07 attendus

| Fichier | Action |
|---------|--------|
| `data/machine_atlas.json` | **New** — V1 (30 machines, 8 familles) |
| `app/services/machine_atlas.py` | **New** — loader + lookup |
| `data/reference_split.json` | Modify — version v11 + 30-40 exercices lies |
| `app/models/catalog.py` | Modify — TemplateExercise +2 colonnes |
| `migrations/versions/20260416_add_machine_fields.py` | **New** — ALTER TABLE additive |
| `app/services/seed.py` | Modify — persister machine fields |
| `app/routers/sessions.py` | Modify — context machine_info |
| `app/templates/session_detail.html` | Modify — panneau `i` + drawer refait |
| `app/routers/pages.py` ou `atlas.py` | Modify / New — route `/science/atlas` |
| `app/templates/atlas.html` | **New** — page atlas |
| `app/templates/science.html` | Modify — lien atlas |
| `app/static/css/app.css` | Modify — styles `.machine-panel`, `.substitute-picker--drawer` |
| `scripts/catalog_qa.py` | Modify — validate machine refs |
| `scripts/machine_atlas_qa.py` | **New** — QA atlas |
| `tests/test_machine_atlas.py` | **New** |
| `tests/test_atlas_routes.py` | **New** |
| `tests/test_catalog_integrity.py` | Extend |

**Effort estime Sb_07 : 6-8h.**

---

## 12. Synthese executive

- Atlas machine = JSON dedie, 30 machines V1 couvrant 100% exercices core
- Lien exercice → machine via 2 champs optionnels `machine_slug` / `machine_family`
- UX panneau `i` natif SSR (imbrique `<details>`), position bloc 6 du body carte
- Drawer substitution affine (wording, count, style distinctif) en respectant garde-fous Sx_02
- Page `/science/atlas` dediee, navigation par ancres
- 1 migration additive, loader in-memory, zero JS
- Effort Sb_07 estime 6-8h
