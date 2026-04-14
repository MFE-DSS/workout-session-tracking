# SPIGNOS Session Entry + Science — Transversal Notes

**Date:** 2026-04-14
**Type:** Notes transversales couvrant 3 specs interdependantes
**Status:** Validated pending build

## 6 decisions verrouillees (pre-build)

Ces 6 arbitrages doivent etre respectes dans tout sprint build. Ils sont references dans les specs individuelles.

| # | Decision | Spec concernee |
|---|----------|----------------|
| 1 | **Launcher V1 ne montre jamais de branches vides.** Resolution dynamique : une branche sans template existant n'est pas affichee. | Launcher |
| 2 | **Launcher V1 s'appuie strictement sur le catalogue existant.** Pas d'ajout `short-lower`/`short-full-body` avant observation usage reel. | Launcher |
| 3 | **Cardio = Option A : 2 templates separes** (`liss-only` pur, `liss-core` cardio+abdos). Zero logique d'optionnel dans la seance. | Cardio |
| 4 | **Science page = manuel d'usage structure, PAS manifeste de marque.** Zero rhetorique marketing. | Science |
| 5 | **Diagramme bas de page = SVG SSR statique.** Pas de Mermaid, pas d'interaction hover en V1. | Science |
| 6 | **reference_split.json courant = seule source de verite catalogue.** Les anciens resumes markdown/txt sont informatifs, pas normatifs. | Toutes |

### Alerte methodologique

Certains resumes catalogue dans les docs anterieures sont obsoletes (ex: description "LISS + Abdos 0 exercice" alors que le template a 4 abdos en v7). **Regle ferme** : chaque sprint build doit lire et citer `data/reference_split.json` au moment du build, jamais un snapshot markdown.

---

## 1. Perimetre

Ces notes couvrent trois chantiers connexes :

1. **Intelligent Session Launcher** — `/launcher` guide a la place de la library plate
2. **Science Page** — `/science` remplace `/rules` avec manuel produit + diagramme
3. **Cardio Capture** — refonte `liss-abs` + capture duree/BPM/calories machine

Ils partagent : la vision "cockpit serieux sans pseudo-science", les modifications du tile home, et le wording FR aligne.

---

## 2. Cardio Capture — Spec complementaire

### 2.1 Probleme actuel

Le template `liss-abs` (section `utility`, kind `cardio`) contient :
- Un `cardio_note` texte : "20-30 min LISS (velo ou marche inclinee) a 120-130 bpm"
- 4 exercices d'abdos (roulette, crunch, releve de jambe, pallof press)

Constats :
- **Le cardio lui-meme n'est pas loggable.** Le champ `cardio_note` du catalogue est une instruction statique, pas une capture de donnee.
- **Les abdos saturent la seance** : 4 exercices x 3 series = 12 series d'abdos pour un template dont l'intention principale est le cardio.
- **Le session model n'a aucun champ cardio** : pas de `cardio_duration_min`, pas de `cardio_bpm_avg`, pas de `cardio_machine_calories`, pas de `cardio_distance_km`.
- **Le template est rigide** : un utilisateur qui veut du LISS pur sans abdos n'a pas d'option.

### 2.2 Objectif

Permettre de logger proprement une seance cardio, avec :
- Duree reelle (minutes)
- BPM moyen (optionnel, si cardiofrequencemetre)
- Calories machine (optionnel, **tag comme donnee machine, pas comme verite metabolique**)
- Machine/mode (velo, marche inclinee, rameur, etc.)
- Abdos optionnels — l'utilisateur choisit s'il ajoute une section abdos ou pas

### 2.3 Decisions proposees

#### Decision 1 : Separer cardio et abdos — **Option A verrouillee**

**Option A retenue (verrouillee)** — split en deux templates :
- `liss-only` — cardio pur, 0 exercice, juste la capture cardio
- `liss-core` — cardio + 4 abdos (equivalent actuel de `liss-abs`, renomme pour clarte)

**Pourquoi Option A :**
- SPIGNOS est SSR + template-driven + historique resilient. Un template flexible a logique optionnelle alourdit le modele et brouille la lecture historique.
- L'intention de la seance reste claire : l'utilisateur choisit `liss-only` ou `liss-core` des le launcher. Aucune micro-decision en cours de seance.
- Analytics plus lisibles : une seance `liss-only` est distincte d'une `liss-core` sans logique de filtrage complexe.
- Zero changement modele (pas de `is_optional` sur TemplateExercise).

**Impact catalogue :**
- Le template actuel `liss-abs` est **renomme** `liss-core` (ou un split : on garde `liss-abs` et on ajoute `liss-only`).
- **A trancher operationnellement :** renommage ou ajout ? Impact snapshot historique a verifier.
  - Si renommage : les sessions historiques ont `template_slug_snapshot = "liss-abs"` qui pointe vers un slug qui n'existe plus. Acceptable grace au mecanisme snapshot/ON DELETE SET NULL, mais une requete "historique des seances liss-core" manquera les anciennes.
  - Si ajout : on garde `liss-abs` tel quel et on ajoute `liss-only`. Propre pour l'historique.
- **Recommandation : ADD, pas rename.** Preserver `liss-abs` (eventuellement renomme en `liss-core` dans le catalogue mais le slug reste), ajouter `liss-only`. Zero impact historique.

**Options ecartees :**
- Option B (template flexible avec abdos optionnels) : rejetee — trop de complexite modele + UX pour un benefice marginal.
- Option C (reduire a 2 abdos) : rejetee — ne resout pas le cas "LISS pur".

#### Decision 2 : Champs cardio sur WorkoutSession

**Nouveaux champs SessionModel :**

```python
# cardio fields (nullable, relevant only for kind=cardio templates)
cardio_duration_min: Mapped[int | None]
cardio_bpm_avg: Mapped[int | None]
cardio_machine_calories: Mapped[int | None]
cardio_machine_type: Mapped[str | None]  # "velo", "marche", "rameur", "autre"
cardio_distance_km: Mapped[float | None]  # optionnel
```

Migration Alembic : 5 colonnes nullable. Aucune donnee historique a migrer.

#### Decision 3 : UI de capture cardio

Si `session.template.kind == "cardio"` :
- La page session affiche en tete d'une section "Cardio" :
  - Input duree (number, min), obligatoire
  - Input BPM moyen (number, optionnel)
  - Select machine (velo, marche inclinee, rameur, autre)
  - Input calories machine (number, optionnel) avec label discret "selon affichage machine"
  - Input distance km (number, optionnel)
- Les exercices abdos (si presents) sont dans une section "Abdos (optionnel)" qu'on peut replier

### 2.4 Garde-fous anti pseudo-science (verrouilles)

**Doctrine produit explicite :**

> **SPIGNOS stocke des donnees cardio operatoires, pas des verites physiologiques absolues.**

Wording strict par champ :

| Champ | Statut | Wording UI cible |
|-------|--------|-----------------|
| `cardio_duration_min` | Donnee brute saisie | "Duree (min)" |
| `cardio_bpm_avg` | Donnee machine ou montre, informative | "BPM moyen (si mesure)" |
| `cardio_machine_calories` | Estimation machine, jamais depense reelle certifiee | "Calories machine (indicatif)" — label explicite |
| `cardio_machine_type` | Contexte materiel | "Machine : velo / marche / rameur / autre" |
| `cardio_distance_km` | Donnee machine optionnelle | "Distance (km)" — **NON inclus en V1** si surcharge UI |

Regles non-negociables :

- Les calories machine ne rentrent dans aucun scoring (dashboard axes, physique zones).
- Le BPM n'est pas traduit en "zone cardio", "intensite relative", "pourcentage FC max".
- Pas de calcul VO2 max estime, pas de "calories brulees corrigees", pas de "zone bruleur de graisse".
- Le scoring "regularite" du dashboard inclut les sessions cardio completees **sans valorisation differentielle** : 1 seance = 1 seance.
- Les `liss-only` et `liss-core` comptent pareil dans regularite, mais aucun ne contribue a "progression muscle" (axe progression, physique zones).

### 2.5 Acceptance criteria (cardio)

- [ ] `WorkoutSession` a 5 nouveaux champs cardio nullable
- [ ] Migration Alembic appliquee
- [ ] La page session d'un template `kind=cardio` affiche la section Cardio en premier
- [ ] Les calories ont un label anti-pseudo-science visible
- [ ] Les abdos de `liss-abs` (renomme ou flexibilise) sont presentes comme optionnels
- [ ] Le dashboard regularite compte les seances cardio terminees
- [ ] Aucun scoring physique (zones musculaires) ne se base sur les champs cardio
- [ ] Export CSV/JSON inclut les champs cardio

---

## 3. Coordination entre les 3 chantiers

### Dependances

```
[Launcher spec V1 (standalone)]
     |
     | (optionnel: launcher v2 peut prendre en compte de nouveaux cardio templates)
     v
[Cardio Capture spec]
     |
     | (la section 4 de Science fait reference aux champs cardio)
     v
[Science Page spec]
     |
     v
[Science diagramme final]  -- mentionne cardio comme module a part
```

### Ordre recommande

1. **Launcher spec + build** d'abord — impact UX majeur, desenclave la decouverte du catalogue. Pas de dependance sur le reste.
2. **Cardio Capture spec + build** ensuite — necessite migration + nouveau modele. Peut se faire en parallele du point 3.
3. **Science Page spec + build** en dernier — absorbe les decisions Launcher et Cardio dans la redaction.

### Impacts communs

| Surface | Launcher | Cardio | Science |
|---------|----------|--------|---------|
| `index.html` (tile home) | "Nouvelle seance" → /launcher | — | "Regles" → "Science" |
| `base.html` (nav) | — | — | — (nav inchange) |
| `library.html` | — | Si catalogue cardio change | — |
| `session_detail.html` | — | Section cardio en tete | — |
| `rules.html` | — | — | Renomme ou remplace |
| Route changes | +`/launcher` | — | +`/science`, redirect `/rules` |
| Model changes | Aucun | +5 champs cardio | Aucun |
| Migration | Aucune | 1 migration | Aucune |
| Catalogue v7→v8 | Aucun (V1) | Si Option B cardio adoptee | Aucun |
| Tests | Nouveaux tests /launcher | Tests cardio + abdos optionnels | Tests /science |

---

## 4. Conflits globaux et resolutions

### 4.1 Conflit : nom du tile home

Aujourd'hui :
- "Nouvelle seance" → /library
- "Regles" → /rules

Apres :
- "Nouvelle seance" → /launcher
- "Science" → /science

**Resolution :** un seul commit index.html qui change les deux tiles simultanement dans le sprint Nav commun.

### 4.2 Conflit : contenu Science section cardio

La section 4 de Science parle de LISS, BPM, calories. Elle depend de la spec Cardio Capture.

**Resolution :** si Cardio Capture n'est pas encore buildee, la section 4 reste generique (role du LISS) sans mentionner les champs specifiques. Une fois Cardio Capture buildee, la section 4 s'enrichit d'un paragraphe sur ce que SPIGNOS capture.

### 4.3 Conflit : modification catalogue (Option B cardio)

Si on choisit l'Option B (un seul template `liss-cardio` avec abdos optionnels), il faut :
- Ajouter un champ `is_optional` sur `TemplateExercise`
- Adapter session_builder pour ne pas pre-creer les SetLog pour les exercices optionnels non-selectionnes
- Ajouter un UX "Ajouter les abdos ?" au demarrage de session

**Resolution :** c'est un vrai sprint catalogue separe. Si trop lourd, fallback sur Option A (split en 2 templates) qui ne touche ni le modele ni le session_builder — juste le catalogue JSON.

### 4.4 Conflit : Synthese dashboard et cardio

Le dashboard axe "Regularite" compte les seances completees. Question : une seance cardio compte-t-elle pareil qu'une seance muscu ?

**Resolution :** oui, toutes les seances `status=completed, excluded_from_stats=false` comptent. C'est la politique actuelle et elle est coherente avec "regularite = frequence d'entrainement tout type confondu".

L'axe "Progression" (tonnage muscu) ne compte pas les seances cardio — c'est deja le cas car il cherche du tonnage sur les work sets muscu.

---

## 5. Ce qui est decide vs. ce qui reste ouvert

### Decide

- Launcher : 2 etapes max, catalogue existant V1, coexistence avec /library
- Science : renommage /rules → /science, structure 5 sections, diagramme SVG server-rendered
- Cardio : 5 champs ajoutes a WorkoutSession, calories machine tag "donnee machine"

### Ouvert (a trancher avant build)

1. **Ancre deep-link depuis session_detail vers Science** : "Rappel methode" actuel pointe-t-il vers `/science#rule-X` ou reste en inline `<details>` ?
2. **Renommage `liss-abs` → `liss-core`** ou ajout d'un slug `liss-only` aux cotes de `liss-abs` preserve ? (Recommandation : ADD pour preserver historique — cf. section 2.3)

### Ferme (decide par les 6 arbitrages)

- ~~Option A vs B cardio~~ → A verrouillee
- ~~Short-lower/short-full-body V1~~ → branches dynamiques, non affichees si vides
- ~~Diagramme interactif vs statique~~ → statique verrouille

### Pas tranchee (volontairement)

- Politique sur les BPM zones cardio (peut venir plus tard avec des donnees reelles)
- Integration cardio au physique dashboard (non, pas prevu)
- Export des cardio data vers fichier detaille (peut attendre)

---

## 6. Sprint queue recommandee (globale)

| Ordre | Sprint | Type | Depend de |
|-------|--------|------|-----------|
| 1 | `Sx_launcher_spec` | Spec | — (deja produit) |
| 2 | `Sx_science_spec` | Spec | — (deja produit) |
| 3 | `Sx_cardio_spec` | Spec | — (deja produit dans ce doc) |
| 4 | `Sb_launcher_v1` | Build | #1 |
| 5 | `Sb_cardio_capture` | Build | #3 |
| 6 | `Sb_science_editorial` | Build | #2 + #5 (pour section cardio) |
| 7 | `Sb_science_diagram` | Build | #6 |
| 8 | `Sb_science_nav` | Build | #7 |
| 9 | `Sb_catalog_short_templates` (optionnel V2) | Build | Observation usage #4 |
| 10 | `Sb_catalog_cardio_refactor` (optionnel selon Option B) | Build | Decision Option A/B |

### Dependances critiques

- Sb_science_editorial a besoin de savoir si Cardio Capture est deja build ou pas (pour le wording section 4).
- Sb_launcher_v1 est totalement independant — peut se faire en premier.
- Sb_cardio_capture introduit une migration, a scheduler hors des sprints UI purs.

---

## 7. Conclusion

Les 3 specs peuvent avancer en parallele sur le plan editorial. Les builds doivent respecter l'ordre : Launcher (independant) → Cardio Capture (migration) → Science (qui depend des deux pour etre fidele).

Aucun conflit structurel avec les chantiers deja menes (feedback, mobile UX, substitution, visual identity V2.1, squads, challenges). Les 3 nouvelles specs respectent :
- SSR / no SPA
- Mobile-first
- Lexicon FR V2.1
- Privacy model squads
- No-pseudo-science policy
- Catalogue governance (bump version, seed idempotent)
