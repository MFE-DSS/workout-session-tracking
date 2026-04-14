# SPIGNOS Session Entry + Science — Transversal Notes

**Date:** 2026-04-14
**Type:** Notes transversales couvrant 3 specs interdependantes
**Status:** Draft

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

#### Decision 1 : Separer cardio et abdos

**Option A — Split en deux templates :**
- `liss-only` — cardio pur, 0 exercice, juste la capture cardio
- `liss-plus-abs` — cardio + 4 abdos (equivalent actuel de liss-abs)

**Option B — Un seul template avec section abdos optionnelle :**
- `liss-cardio` unique
- Les 4 abdos deviennent "exercices complementaires" marques comme optionnels dans le catalogue
- Au demarrage, question "Ajouter une section abdos ?" → si non, les exercices sont skip

**Option C — Reduire les abdos a 2 exercices (au lieu de 4) et garder un template :**
- Moins de saturation
- Simplicite
- Mais ne resout pas le "LISS pur sans abdos"

**Recommandation : Option B** — plus flexible, permet au user de choisir. Requiert d'ajouter un champ `is_optional` sur `TemplateExercise` ou une logique de "section optionnelle".

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

### 2.4 Garde-fous anti pseudo-science

- Label explicite sur calories : "Valeur indicative selon machine — pas une mesure physiologique."
- Les calories machine ne rentrent dans aucun scoring (dashboard axes, physique) — elles sont stockees comme donnee brute pour l'utilisateur, point.
- Le BPM moyen n'est pas traduit en "zone cardio" ou "intensite relative" — c'est juste la valeur telle que saisie.
- Pas de calcul "VO2 max estime" ou similaire.
- Le scoring "regularite" du dashboard peut inclure les sessions cardio — mais sans valorisation differente (une seance cardio = une seance, point).

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

1. **Option A vs B cardio** : split templates vs template flexible
2. **Short-lower et short-full-body** : ajouter au catalogue V2 ou laisser les branches vides
3. **Ancre deep-link depuis session_detail vers Science** : "Rappel methode" actuel pointe-t-il vers `/science#rule-X` ou reste en inline `<details>` ?
4. **Diagramme Science V2** : doit-il etre interactif (hover pour faire clignoter une fleche) ou strictement statique ?

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
