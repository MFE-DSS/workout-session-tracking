# SPIGNOS Intelligent Session Launcher — Spec

**Date:** 2026-04-14
**Type:** Product + UX spec, ancree sur repo reel (reference_split.json v2026-04-14.v7)
**Status:** Validated pending build

## Arbitrages verrouilles (pre-build)

| # | Decision | Impact |
|---|----------|--------|
| 1 | **Launcher V1 ne montre JAMAIS de branches vides.** | Dynamic branch resolution depuis reference_split.json. Si `BRANCH_TO_SLUGS[branch] == []`, la branche n'apparait pas dans le menu parent. |
| 2 | **Launcher V1 = catalogue existant uniquement.** | Pas d'ajout de templates `short-lower` ou `short-full-body` avant observation usage reel. |
| 3 | **reference_split.json (v7 courant) = seule source de verite catalogue.** | Les anciens resumes markdown/txt sont informatifs, pas normatifs. Le build doit lire le JSON courant, pas un snapshot. |

---

## 1. Contexte

### Flux actuel

L'entree "Nouvelle seance" depuis l'accueil est un tile qui mene a `/library`. La page `/library` affiche **tous les templates non-archives** groupes par section (`core`, `utility`, `specialization`). Chaque template est une carte avec nom, focus, lien vers `/library/{slug}`, et un bouton POST "Demarrer" qui appelle `POST /sessions` avec `template_slug`.

Le flux est **plat** : 1 tap sur "Nouvelle seance" → 1 page de 11 cartes → 1 tap "Demarrer". Zero filtrage, zero guidage, zero contexte.

### Catalogue reel (v2026-04-14.v7)

15 templates totaux, distribues ainsi :

| Section | Templates | Count |
|---------|-----------|-------|
| `core` | push-a, push-b, pull-a, pull-b, legs-a, legs-b | 6 |
| `utility` | liss-abs (cardio), short-upper | 2 |
| `specialization` | catch-up-shoulders, catch-up-arms, catch-up-back-width | 3 |
| `archived` | upper-pecs-delts, upper-back-arms, lower-quad-bias, lower-posterior-bias | 4 (masques du catalogue) |

**Constat structurel :**
- Les 6 templates `core` suivent une logique PPL (Push/Pull/Legs) — pas de full-body ni d'upper/lower dans le core.
- La section `utility` est sous-dimensionnee : un seul template court (short-upper) et un seul cardio (liss-abs).
- Les templates `archived` couvrent upper-pecs-delts, upper-back-arms, lower-quad-bias, lower-posterior-bias — ils existent en DB mais sont masques de la library. Ils pourraient redevenir utiles via un launcher guide.
- Aucun template "full body court", "full lower court", ou "cardio pur sans abdos".

### Contraintes architecturales

- FastAPI SSR + Jinja2 + SQLite — pas de SPA, pas de state client.
- Mobile-first strict, usage au pouce au gym.
- Cockpit prive sobre — pas de marketing, pas de "personnalisation AI".
- Coexistence obligatoire : "Nouvelle seance" (flux guide) et "Programmes" (catalogue complet, acces libre).

---

## 2. Probleme

Aujourd'hui, l'utilisateur au gym doit parcourir 11 cartes mentalement pour choisir une seance — alors que sa decision reelle se prend en 2-3 dimensions :

1. **Temps disponible** (session complete vs courte)
2. **Type d'effort** (force/muscu vs cardio)
3. **Zone ciblee** (haut vs bas, ou specialisation)

La page `/library` expose tout simultanement, ce qui :
- oblige un scroll mental inutile
- rend invisible le bon match entre contexte et template
- traite les templates de specialisation comme equivalents aux core (alors qu'ils ne sont pas le premier choix par defaut)
- n'a pas de chemin clair pour le cardio (liss-abs est perdu dans la section utility)

---

## 3. Objectif produit

Transformer "Nouvelle seance" en un **lanceur guide en 2 etapes max** qui :

1. Demande d'abord **l'intention** (type de seance + dimension temps)
2. Propose ensuite les templates **reellement pertinents** pour cette intention
3. Garde le catalogue complet accessible via `/library` (entree separee "Programmes")

Le lanceur doit rester **plus intelligent qu'un filtre basique**, sans tomber dans la taxonomie bureaucratique.

---

## 4. Principes produit

| Principe | Implication |
|----------|-------------|
| **Taper une fois, reflechir une fois, demarrer** | 2 etapes max, pas 3. Chaque etape elimine une dimension. |
| **Pas de taxonomie artificielle** | Les categories correspondent a des decisions reelles de l'utilisateur au gym, pas a une arborescence theorique. |
| **Zero catalogue invisible** | Si l'utilisateur ne trouve pas son template, il a un acces direct `/library` a tout moment. |
| **Preselection par defaut** | Chaque etape a une option par defaut raisonnable, pour qu'un tap rapide mene au "bon choix standard". |
| **Cardio = chemin de premiere classe** | Pas relegue en "autre", mais une option principale des l'etape 1. |

---

## 5. UX cible

### Decision tree (2 etapes)

```
Etape 1 : "Type de seance"
├── Seance standard   (defaut)
├── Seance courte
└── Cardio

Etape 2 : varie selon etape 1
```

**Si "Seance standard" :**

```
Etape 2 : "Quelle zone ?"
├── Haut du corps
│   ├── Push (pecs/epaules/triceps) → propose push-a, push-b
│   └── Pull (dos/biceps)           → propose pull-a, pull-b
├── Bas du corps
│   ├── Quads dominant              → propose legs-a
│   └── Posterieur dominant         → propose legs-b
└── Rattrapage (specialisation)
    ├── Epaules                     → propose catch-up-shoulders
    ├── Bras                        → propose catch-up-arms
    └── Dos largeur                 → propose catch-up-back-width
```

**Si "Seance courte" (V1 — catalogue-aware) :**

```
Etape 2 : "Quoi de court ?"
├── Full upper court                → propose short-upper
└── Specialisation courte           → propose catch-up-shoulders, catch-up-arms, catch-up-back-width
```

**Branches dynamiques :** si `short-lower` ou `short-full-body` sont ajoutes au catalogue plus tard, ils apparaissent automatiquement dans l'etape 2. Le code ne liste que les branches dont `BRANCH_TO_SLUGS` retourne au moins 1 slug existant dans le catalogue courant.

**Regle ferme :** pas de branche affichee avec message "aucun template disponible". Si la branche est vide, elle n'existe pas pour l'utilisateur.

**Si "Cardio" :**

```
Etape 2 : direct (pas d'etape 2 pour V1)
└── LISS + abdos                    → propose liss-abs
```

En V1, "Cardio" a un seul template possible. En V2 si d'autres templates cardio apparaissent, etape 2 se developpe.

### Format d'affichage par etape

Chaque etape est une page SSR avec :
- 1 titre court ("Quel type de seance ?" / "Quelle zone ?")
- 2-4 gros boutons tactiles (tile-grid existant)
- 1 lien discret en bas : "Voir tous les programmes →" vers `/library`
- 1 lien "← Etape precedente" si etape 2

**Pas de stepper visuel complique.** La page est simplement remplacee a chaque clic.

### Presentation finale (liste de templates filtres)

L'etape 2 peut mener directement a un seul template (cas cardio) ou a une liste courte (2-3 templates). Dans les deux cas :

- Si **1 seul template** : la page affiche directement la carte template_detail (prescheme, focus, exercices), avec le bouton "Demarrer" principal.
- Si **2-3 templates** : affichage en template-cards existantes, dans l'ordre de pertinence, avec "Demarrer" direct sur chaque carte.

Pas de troisieme etape "choisir parmi les templates filtres" — a ce stade l'utilisateur est suffisamment pres pour demarrer.

### Navigation et coexistence avec /library

| Entree | Destination | Audience |
|--------|-------------|----------|
| Tile "Nouvelle seance" sur `/` | `/launcher` (etape 1 du flux guide) | Usage quotidien par defaut |
| Lien "Programmes" dans la nav | `/library` (catalogue complet) | Exploration, power users |
| Lien "Voir tous les programmes →" dans le launcher | `/library` | Echappatoire si le guidage rate |

La nav topbar conserve "Programmes" tel quel. Le changement se situe uniquement au niveau du tile home et de la nouvelle route `/launcher`.

---

## 6. Mapping table complet

| Etape 1 | Etape 2 | Templates proposes (ordre) | Route |
|---------|---------|---------------------------|-------|
| Standard | Haut / Push | push-a, push-b | `/launcher?type=standard&zone=upper-push` |
| Standard | Haut / Pull | pull-a, pull-b | `/launcher?type=standard&zone=upper-pull` |
| Standard | Bas / Quads | legs-a | `/launcher?type=standard&zone=lower-quads` |
| Standard | Bas / Posterieur | legs-b | `/launcher?type=standard&zone=lower-post` |
| Standard | Rattrapage / Epaules | catch-up-shoulders | `/launcher?type=standard&zone=catch-shoulders` |
| Standard | Rattrapage / Bras | catch-up-arms | `/launcher?type=standard&zone=catch-arms` |
| Standard | Rattrapage / Dos | catch-up-back-width | `/launcher?type=standard&zone=catch-back` |
| Courte | Full upper | short-upper | `/launcher?type=short&variant=upper` |
| Courte | Specialisation | catch-up-* | `/launcher?type=short&variant=spec` |

**Branches NON affichees en V1** (parce que BRANCH_TO_SLUGS est vide) :
- `type=short&variant=lower` — pas de template short-lower existant
- `type=short&variant=full` — pas de template short-full-body existant

Ces branches seront ajoutees automatiquement si les templates correspondants sont seedees dans le catalogue.
| Cardio | — | liss-abs | `/launcher?type=cardio` |

Le filtrage est deterministe : chaque branche route vers une liste fixe de slugs. Le service est un simple dict `BRANCH_TO_SLUGS` dans `app/services/launcher.py`.

---

## 7. Analyse catalogue et recommandation

### Ce qui existe et est bien servi

- Standard haut/bas PPL : push-a/b, pull-a/b, legs-a/b — couverts parfaitement par 6 templates core.
- Rattrapage par zone : 3 templates specialization dedies.
- Short upper : 1 template utility.
- Cardio LISS + abdos : 1 template utility.

### Ce qui est mal servi par l'entree actuelle

- **Les templates archived sont invisibles** mais pourraient servir de "variantes plus compactes". Exemple : `upper-pecs-delts` (7 exercices) est similaire a push-a mais moins specialise. Decision V1 : les laisser archived, ne pas les exposer via le launcher.
- **Le cardio est une option de 3e classe** en `utility` alors qu'il represente un choix frequent (seance de recup, entre deux seances muscu).
- **Les templates specialization sont au meme niveau visuel que core** dans `/library` alors qu'ils sont des choix secondaires.

### Ce qui manque reellement

| Gap | Cas d'usage | Recommandation |
|-----|-------------|----------------|
| Full lower court | "J'ai 30 min, je veux travailler les jambes rapidement" | **A ajouter en Sprint catalogue (post-V1)** — un template `short-lower` ~5 exercices, squat+RDL+extensions+curls+mollets. |
| Full body court | "J'ai 30 min, je veux toucher tout" | **A ajouter en Sprint catalogue (post-V1)** — un template `short-full-body` ~6 exercices composes. |
| Cardio pur sans abdos | "Je veux juste du LISS ce soir" | **A evaluer** — soit rendre `liss-abs` flexible (cf. Spec Cardio separee), soit ajouter `liss-only`. |

### Recommandation explicite (verrouillee)

**V1 — Launcher strict sur catalogue existant. Branches vides interdites.**

- Les branches dont `BRANCH_TO_SLUGS` retourne une liste vide **ne sont pas affichees** a l'utilisateur.
- Le code filtre a l'execution : chaque menu d'etape 2 itere sur les branches definies, et garde uniquement celles qui ont au moins 1 slug existant dans le catalogue courant.
- Si un template est retire du catalogue (archived), la branche concernee disparait automatiquement.
- Si un template est ajoute (ex: `short-lower` en V2), la branche correspondante apparait sans changement de code launcher.

**Argument :** promettre une branche qui finit sur un message d'erreur ou un fallback library est une rupture de contrat UX. Mieux vaut 2 options solides que 4 options dont 2 en panne. Livrer sur 11 templates existants est immediatement utile.

**V2 (post-launcher) — Sprint catalogue :**
- Ajouter `short-lower` (utility, display_order 12)
- Ajouter `short-full-body` (utility, display_order 13)
- Decider si `liss-abs` devient `liss-cardio` avec abdos optionnels (cf. Spec Cardio)

---

## 8. Implications techniques

### Fichiers impactes

| Fichier | Nature du changement |
|---------|---------------------|
| `app/routers/pages.py` | Ajouter route `GET /launcher` (3 etats : sans param, `?type=X`, `?type=X&zone=Y`) |
| `app/services/launcher.py` | **Nouveau** — contient `BRANCH_TO_SLUGS`, helper `get_templates_for_branch()` |
| `app/templates/launcher.html` | **Nouveau** — rendu des 2 etapes + resultat final |
| `app/templates/index.html` | Modifier le tile "Nouvelle seance" pour pointer sur `/launcher` |
| `app/templates/base.html` | Pas de changement (la nav "Programmes" vers `/library` reste) |

### Route signature

```python
@router.get("/launcher")
def launcher(
    request: Request,
    db: DbSession,
    user: CurrentUser,
    type: str | None = Query(None),        # "standard" | "short" | "cardio"
    zone: str | None = Query(None),        # etape 2 value
    variant: str | None = Query(None),     # alt. name for etape 2 on "short"
) -> HTMLResponse:
    ...
```

### Pas de nouvelle migration

Le launcher est pur UX + routing. Il ne cree ni modele ni donnees.

### Pas de changement `POST /sessions`

Le launcher redirige vers le template detail existant ou affiche une carte qui appelle le meme `POST /sessions` qu'aujourd'hui. **Zero changement backend session.**

---

## 9. Dependances

- Depend du catalogue actuel (v2026-04-14.v7) — tous les slugs references existent.
- Pas de dependance sur Sb_04 (history alignment), sur les specs substitution, ni sur le dashboard.
- La coexistence avec `/library` est garantie car aucune route n'est supprimee.

---

## 10. Risques

| Risque | Mitigation |
|--------|------------|
| L'utilisateur "perd" ses habitudes si on cache la library | La nav topbar conserve un lien "Programmes" vers `/library` pour acces direct. |
| Branches vides frustrantes (short-lower, short-full-body) | Message clair + lien `/library`. Ne pas afficher les branches vides serait pire — cela camouflerait l'existence de la notion. |
| Surdimensionnement du launcher si le catalogue grandit | Le decision tree est code-as-data dans `launcher.py` — facile a etendre ou refactor si > 20 templates. |
| Conflit avec la spec Substitution | Aucun — la substitution agit au niveau session individuelle, le launcher au niveau choix de template. Orthogonaux. |
| Le launcher devient un "stepper lourd" | Regle dure : max 2 etapes. Si on en veut 3, c'est qu'il faut refondre la taxonomie. |

---

## 11. Conflits potentiels avec chantiers existants

| Chantier | Conflit | Resolution |
|----------|---------|------------|
| `SPIGNOS_EXERCISE_FEEDBACK_RATIONALIZATION.md` (Sb_01, done) | Aucun — le launcher n'touche pas au feedback par exercice. | — |
| `SPIGNOS_MOBILE_EXERCISE_ENTRY_UX.md` (Sb_02, done) | Aucun — intervient apres le choix du template, pas avant. | — |
| `SPIGNOS_EXERCISE_SUBSTITUTION_GRAPH_SPEC.md` (Sb_03, done) | Aucun — agit au niveau session, pas au niveau choix de template. | — |
| `SPIGNOS_EXERCISE_SYSTEM_ROADMAP.md` | Le launcher ne reassigne pas de categories d'exercices. | — |
| `SPIGNOS_VISUAL_IDENTITY_V2.md` | Le launcher doit utiliser les tokens, utility classes, et tile patterns deja definis. | Tiles sont le pattern natif. |

**Aucun conflit bloquant detecte.**

---

## 12. Acceptance criteria

### Fonctionnels

- [ ] Depuis `/`, le tile "Nouvelle seance" mene a `/launcher` (pas a `/library`)
- [ ] `/launcher` affiche 3 choix : Standard / Courte / Cardio
- [ ] `/launcher?type=standard` affiche les sous-choix Haut/Bas/Rattrapage avec sous-sous-options
- [ ] `/launcher?type=standard&zone=upper-push` affiche push-a + push-b
- [ ] `/launcher?type=cardio` affiche liss-abs directement
- [ ] Le bouton "Demarrer" sur chaque template filtre mene au meme POST /sessions qu'aujourd'hui
- [ ] Un lien "Voir tous les programmes →" est present a chaque etape, pointant vers `/library`
- [ ] La nav topbar conserve "Programmes" accessible directement
- [ ] Les branches sans template disponible **ne sont pas affichees du tout** (pas de message d'erreur, pas de fallback visible)
- [ ] Le service launcher lit dynamiquement reference_split.json au boot (via le seed) et resout les slugs a l'execution

### UX

- [ ] Chaque etape tient dans un viewport mobile sans scroll (4 tiles max par ecran)
- [ ] Les boutons tactiles respectent le 44px min
- [ ] L'utilisateur peut revenir a l'etape precedente via un lien "← Retour"
- [ ] Aucun JS requis — tout est SSR lien/form

### Tests

- [ ] Test route `GET /launcher` sans params
- [ ] Test route avec type=standard, zone=upper-push → templates attendus
- [ ] Test route avec type=cardio → liss-abs
- [ ] Test branche vide (type=short, variant=lower) → message + lien library
- [ ] Test que le tile home pointe sur /launcher
- [ ] Test que la library reste accessible via /library

---

## 13. Lotissement recommande

| Sprint | Contenu | Pre-requis |
|--------|---------|-----------|
| **Sb_launcher** | Route, service, template, tests, update index.html | Aucun |
| **Sb_catalog_short_full** (optionnel, V2) | Ajouter short-lower et short-full-body au catalogue | Evaluer l'usage du launcher pendant 2-3 semaines avant |
| **Sb_cardio_capture** (separe, voir spec dediee) | Refonte liss-abs + capture cardio | Peut se faire avant ou apres launcher |

---
