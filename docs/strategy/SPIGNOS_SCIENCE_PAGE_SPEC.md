# SPIGNOS Science Page — Spec

**Date:** 2026-04-14
**Type:** Product + editorial + information architecture
**Status:** Draft pending validation

---

## 1. Contexte

### Etat actuel

La page `/rules` (template `rules.html`, route `rules_page` dans `app/routers/sessions.py`) affiche une liste de 8 cartes chargees depuis `data/method_rules.json` :

1. Carnet d'entrainement et surcharge progressive
2. Plages de repetitions
3. Series d'approche (feeder sets)
4. Tempo
5. Temps de repos
6. Legende technique (RP / DS)
7. Series Rest-Pause
8. Drop Sets

**Structure actuelle :** un titre page "Regles", une lede "Rappels methode a consulter au gym", puis un simple `{% for rule in rules %}` qui rend chaque rule comme `<article class="card">` avec title + body.

### Constats

- Le contenu existant est **de tres bonne qualite** — sobre, concret, oriente usage reel. C'est la base editoriale la plus solide de l'app.
- Le titre "Regles" **sous-vend** le produit. Une app sincerement "body engineering cockpit" devrait assumer une page "Science" qui explique le pourquoi.
- Il manque **l'explication du produit lui-meme** — comment fonctionne SPIGNOS, quelle est la logique templates/seances/exercices/sets, pourquoi noter change la progression.
- Il manque la pedagogie sur le **cardio/LISS** (cf. spec cardio separee).
- Il manque un **visuel synthetique** montrant comment les modules s'articulent.

### Contraintes

- SSR + Jinja2, zero JS dependency
- Mobile-first
- Identite sobre, pas de marketing
- Pas de pseudo-science, pas de promesse medicale
- Coherent avec la politique "no-pseudo-science" deja etablie dans `SPIGNOS_SCORING_RULES_V1.md`
- Le contenu actuel de `method_rules.json` doit etre preserve (base editoriale) — enrichi, pas remplace

---

## 2. Probleme

Un utilisateur qui ouvre `/rules` aujourd'hui voit 8 rappels techniques. Tres bien pour une verification rapide au gym, mais :

- Il ne comprend pas **pourquoi** SPIGNOS existe
- Il ne sait pas **comment** les modules (templates, seances, historique, synthese, physique) s'articulent
- Il n'a pas de **cadre mental** sur la progression, le cardio utile, le tempo dans le contexte de l'app
- Un nouveau user rate la porte d'entree pedagogique qui rendrait le produit credible et differenciant

La page actuelle est un **memento**. La page cible est un **manuel sobre du produit et de la methode**.

---

## 3. Objectif produit

Transformer `/rules` en `/science` — une page qui couvre 4 roles :

1. **Pedagogie methode** : comprendre la surcharge progressive, les plages reps, le tempo, les temps de repos, les techniques (RP/DS)
2. **Pedagogie cardio** : comprendre le role du LISS dans un programme muscu
3. **Manuel du produit** : comprendre templates → seances → exercices → sets → historique → synthese
4. **Visuel d'architecture fonctionnelle** : une representation user-facing des modules et de leurs liens

### Ce que cette page n'est PAS

- Pas un blog
- Pas un tutoriel marketing "Get your best physique"
- Pas un health score page
- Pas une explication technique developpeur
- Pas un whitepaper scientifique avec citations

### Ce qu'elle EST

- Un document de reference consultable au calme (pas au milieu d'une seance — pour ca le memento reste dans la session_detail)
- Un texte sec, technique, honnete
- Un schema visuel elegant mais lisible
- Le lieu qui donne au produit sa credibilite "serieux sans pseudo-science"

---

## 4. Principes editoriaux

| Principe | Application |
|----------|-------------|
| **Concret avant theorie** | Toujours partir d'un geste ou d'un cas reel, pas d'un concept abstrait |
| **Phrases courtes, pas de jargon gratuit** | "Echec mecanique a 8 reps" OK. "Intensite relative neurologique" NON. |
| **Tutoiement constant** | Coherent avec tout le produit |
| **Pas de superlatifs** | "Ameliore la progression" OK. "Transforme radicalement tes resultats" NON. |
| **Pas de promesse de resultat** | "Si tu notes tes seances, tu progresses plus serieusement" OK. "Tu vas prendre 5kg de muscle" NON. |
| **Conditionnel sur le scientifique** | "La litterature suggere" plutot que "La science prouve" |
| **Pas d'AI vocabulary** | Zero "intelligent", "adaptatif", "smart", "powered by" |
| **Vocabulaire aligne UI** | "Serie" (et pas "Work set"), "Echauf." (et pas "Warmup"), "Ressenti exercice" (et pas "Feedback") |

---

## 5. Architecture editoriale

### Hierarchie

```
/science (page)
├── Section 1: Pourquoi noter change la progression
├── Section 2: Comment fonctionne SPIGNOS (manuel produit)
├── Section 3: Methode d'entrainement
│   ├── Plages de repetitions
│   ├── Series d'approche
│   ├── Tempo
│   ├── Temps de repos
│   ├── Legende technique
│   ├── Rest-Pause
│   └── Drop Sets
├── Section 4: Place du cardio (LISS)
├── Section 5: Visuel d'architecture modules (diagramme)
└── Footer de page (brievete, pas de CTA marketing)
```

### Section 1 — Pourquoi noter change la progression

**Longueur cible :** 150-200 mots. 3-4 paragraphes courts.

**Contenu :**
- La memoire subjective est un mauvais outil de progression. Un carnet la remplace.
- La surcharge progressive suppose de savoir ce qu'on a fait la derniere fois. C'est tout.
- L'auto-illusion (croire qu'on progresse quand on stagne) est la premiere cause de stagnation reelle.
- Noter = imposer une discipline minimale qui rend la progression mesurable.
- Le journal devient une base objective pour ajuster la charge, le volume, la frequence.

**Pattern rhetorique :** pas de "tu dois". Plutot "quand tu notes, X se passe". Factuel.

### Section 2 — Comment fonctionne SPIGNOS

**Longueur cible :** 300-400 mots. Structuree avec sous-titres.

**Contenu :** manuel fonctionnel du produit.

#### 2.1 Le catalogue

Les programmes (ex: Push A, Pull B, Legs A) sont des **modeles de seance**. Chacun prescrit des exercices, des plages de reps, des techniques. Le catalogue est fige a chaque version — on peut le mettre a jour, mais l'historique ne bouge pas.

#### 2.2 La seance

Quand tu demarres une seance, SPIGNOS cree une **copie vivante** du modele : tu vas y inscrire tes poids, tes reps, ton ressenti. Cette copie ne change plus si le catalogue est modifie plus tard.

#### 2.3 Les exercices et les series

Chaque exercice de ta seance a des **series d'echauffement** (1 ou 2) et des **series de travail** (selon le programme). Tu saisis pour chaque serie : poids, reps, coche "fait". C'est tout.

#### 2.4 Le ressenti et le score

Le score de chaque exercice est calcule automatiquement a partir de tes reps vs la plage prescrite et du nombre de series completees. Tu n'as pas a donner un ressenti arbitraire — le chiffre vient de ce que tu as fait.

La sensation musculaire (optionnelle) reste une note subjective qui aide a repairer quelle zone travaille bien, sans pretendre a une mesure.

#### 2.5 L'historique

Chaque seance est conservee telle qu'elle a ete logguee. Tu peux revenir dessus, comparer aux seances passees pour le meme exercice, voir tes deltas.

#### 2.6 La synthese et le physique

La page **Synthese** (`/dashboard`) calcule 5 axes (regularite, progression, evolution corporelle, recuperation, equilibre musculaire) avec un niveau de confiance par axe. Si les donnees sont insuffisantes, l'axe est grise — pas de fausse precision.

La page **Physique** (`/physique`) montre l'equilibre de developpement par zone musculaire, base sur le volume d'entrainement et les mesures corporelles (si saisies).

#### 2.7 Ce qui reste prive

Tes mesures, ta readiness, tes notes, tes poids par serie : strictement privees. Meme dans une squad (groupe prive), seule l'activite agregee est partagee — jamais les details.

### Section 3 — Methode d'entrainement

**Reprise integrale des 8 method_rules existants.** Aucune reecriture — ils sont bons.

Reorganisation :
1. Carnet d'entrainement et surcharge progressive
2. Plages de repetitions
3. Series d'approche
4. Tempo
5. Temps de repos
6. Legende technique (RP / DS)
7. Series Rest-Pause
8. Drop Sets

**Nouveaute :** chaque rule-card affiche un **ancre deep-link** (`#rule-carnet-progression`) pour pouvoir pointer depuis d'autres pages de l'app vers un rappel precis.

### Section 4 — Place du cardio (LISS)

**Longueur cible :** 150-200 mots.

**Contenu :**
- Le LISS (Low Intensity Steady State) n'est pas un outil de perte de gras "magique". C'est un outil de **discipline cardio-vasculaire** et de **recuperation active**.
- Dans un programme muscu, le LISS a trois fonctions :
  1. Maintenir une base cardio sans tirer sur la recuperation musculaire
  2. Etre une seance "entre deux" qui preserve la regularite les jours ou on n'a pas le temps pour une vraie seance muscu
  3. Ameliorer la tolerance au volume (capacite a enchainer les seances)
- SPIGNOS capture le cardio avec : duree, BPM moyen (optionnel), machine utilisee. Les calories affichees par la machine peuvent etre notees mais elles sont une **donnee machine informative**, pas une verite metabolique.
- Les seances de LISS n'entrent pas dans le scoring muscle (physique dashboard) mais contribuent a la regularite globale.

**Note :** cette section doit rester synchrone avec la spec Cardio separee (`SPIGNOS_CARDIO_CAPTURE_SPEC.md` a produire). Si le modele de donnees cardio est etendu, le wording de cette section suit.

### Section 5 — Visuel d'architecture modules

Voir section 6 ci-dessous.

---

## 6. Visuel d'architecture

### Intention

Une representation **user-facing** (pas developpeur) des modules du produit et de leurs liens. L'utilisateur doit comprendre en 5 secondes ce qui alimente quoi.

### Contenu du schema

Nodes (modules du produit) :
- **Programmes** (catalogue)
- **Seance** (log en cours)
- **Historique** (seances passees)
- **Etat du jour** (readiness)
- **Mesures** (body measurements)
- **Synthese** (dashboard 5 axes)
- **Physique** (11 zones musculaires)
- **Classement** (leaderboard global)
- **Squads** (groupes prives)

Edges (flux de donnees logiques) :
- Programmes → Seance (instancie)
- Seance → Historique (archive)
- Historique → Synthese (alimente regularite + progression)
- Historique → Physique (alimente volume par zone)
- Etat du jour → Synthese (alimente recuperation)
- Mesures → Synthese (alimente evolution corporelle)
- Mesures → Physique (valeurs de reference zones)
- Historique → Classement (agrege score)
- Historique → Squads (activite partagee, filtree)

### Format recommande

**Recommandation : SVG inline genere cote serveur** via un helper Jinja ou un simple template Jinja qui rend du SVG avec les memes tokens CSS que le reste de l'app. C'est le pattern deja utilise pour le radar chart physique et les timelines.

Pourquoi pas Mermaid :
- Mermaid necessite un JS runtime cote client (`mermaid.min.js` ~300kb)
- Le rendu depend du JS charge, ce qui casse le principe "zero JS required"
- Les couleurs Mermaid sont difficiles a aligner avec les tokens SPIGNOS

Pourquoi pas HTML/CSS pur :
- Les liens (edges) entre modules sont quasi impossibles a dessiner proprement sans SVG

**Pattern SVG propose :**

```html
<figure class="science-diagram">
  <svg viewBox="0 0 800 600" xmlns="http://www.w3.org/2000/svg" role="img"
       aria-labelledby="diagram-title diagram-desc">
    <title id="diagram-title">Architecture des modules SPIGNOS</title>
    <desc id="diagram-desc">
      Programmes alimente Seance. Seance alimente Historique. Historique
      alimente Synthese, Physique, Classement, Squads. Etat du jour et
      Mesures alimentent Synthese et Physique.
    </desc>

    <!-- Nodes stylises avec les tokens CSS -->
    <g class="diagram-node">
      <rect x="50" y="50" width="140" height="50" rx="8"
            fill="var(--surface)" stroke="var(--accent)" />
      <text x="120" y="80" text-anchor="middle" fill="var(--fg)">Programmes</text>
    </g>
    <!-- ... autres nodes ... -->

    <!-- Edges avec fleches -->
    <line x1="190" y1="75" x2="250" y2="75" stroke="var(--fg-muted)"
          marker-end="url(#arrow)" />
    <!-- ... autres edges ... -->

    <defs>
      <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5"
              markerWidth="6" markerHeight="6" orient="auto">
        <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--fg-muted)" />
      </marker>
    </defs>
  </svg>
  <figcaption>Les donnees alimentent un cockpit personnel unique.</figcaption>
</figure>
```

Le SVG est **servi directement par le template**, sans generation Python dynamique (les nodes et liens sont statiques). Si on veut rendre le diagramme reactif a l'etat des donnees user (ex: greyser "Squads" si l'user n'a pas de squad), on peut passer un contexte Jinja `modules_active`.

### Styling

- Nodes : `rect` arrondi avec `fill=var(--surface)`, `stroke=var(--accent)` ou `var(--border)` selon centralite
- Texte : `font-family: var(--font-mono)` 11px
- Edges : `stroke=var(--fg-muted)`, marker-end fleche
- Layout : grille 3x3 approximative, pas de force-directed
- Responsive : `viewBox` + `preserveAspectRatio` pour scale mobile-friendly

### Caption

Une ligne sous le diagramme, factuelle : "Les donnees alimentent un cockpit personnel unique. Les zones en pointille sont privees."

---

## 7. Ton rédactionnel : exemples concrets

**BIEN :**
> "Noter ta seance, c'est remplacer ta memoire subjective par une trace objective. Tu n'as pas a croire que tu as progresse — tu peux le verifier."

**MAL :**
> "SPIGNOS t'aide a atteindre tes objectifs grace a un suivi intelligent de tes performances."

---

**BIEN :**
> "La synthese calcule 5 axes. Si les donnees sont insuffisantes sur un axe, il est grise. Tu ne vois jamais un score qu'on ne peut pas calculer honnetement."

**MAL :**
> "Notre algorithme avance analyse vos metriques pour vous donner un score de performance globale."

---

**BIEN :**
> "Le LISS n'est pas magique. C'est un outil de discipline cardio et de recuperation active. Ce qui compte, c'est la regularite."

**MAL :**
> "Maximisez votre bruler de gras avec du cardio LISS scientifiquement optimise."

---

## 8. Microcopy / vocabulaire

### A utiliser

| Mot | Contexte |
|-----|----------|
| Serie | Set de travail |
| Echauf. | Serie d'echauffement |
| Ressenti | Feedback exercice (subjectif) |
| Confiance | Niveau de fiabilite d'une mesure/score |
| Regularite | Frequence d'entrainement |
| Progression | Evolution mesurable |
| Discipline | Pratique systematique |
| Cockpit | Terme accepte pour designer l'app (introduit dans welcome) |

### A eviter

| Mot | Raison |
|-----|--------|
| Intelligent, Smart | Vocabulaire SaaS generique |
| Optimiser | Suggere une promesse non mesurable |
| Transformer | Marketing |
| Objectif (en verbe) | "Atteindre tes objectifs" est creux |
| Performances (pluriel) | Trop flou |
| Metriques (si generique) | Jargon sans contenu |
| Powered by, Driven by | Anglicismes commerciaux |
| Health score, Fitness score | Donne une impression de verite qu'on n'a pas |

---

## 9. Implications UI / templates

### Fichiers impactes

| Fichier | Changement |
|---------|-----------|
| `app/templates/rules.html` | **A renommer** ou remplacer par `science.html`. Nouvelle structure (5 sections). |
| `app/templates/science.html` | **Nouveau** — structure editoriale complete avec diagramme SVG. |
| `app/routers/sessions.py` (route `rules_page`) | **Renommer** en `science_page`, URL `/science`. Garder `/rules` comme alias redirect 301 vers `/science` pour compat. |
| `app/templates/base.html` | Lien nav — le tile "Regles" sur home passe a "Science". |
| `app/templates/index.html` | Mettre a jour le tile "Regles" → "Science". |
| `data/method_rules.json` | Inchange — reutilise tel quel. |
| `app/models/catalog.py` (MethodRule) | Inchange. |
| `app/services/seed.py` | Inchange. |
| Tests | Adapter `test_session_flow.py::test_rules_page_renders_seeded_rules` et similar. |

### Sectioning dans le template

```html
{% extends "base.html" %}
{% block content %}
<h1 class="page-title">Science</h1>

<section class="science-section" id="section-journal">
  <h2 class="section-header">Pourquoi noter change la progression</h2>
  <!-- 150-200 mots -->
</section>

<section class="science-section" id="section-manual">
  <h2 class="section-header">Comment fonctionne SPIGNOS</h2>
  <!-- 7 sous-sections 2.1-2.7 -->
</section>

<section class="science-section" id="section-method">
  <h2 class="section-header">Methode d'entrainement</h2>
  <!-- loop sur rules -->
  {% for rule in rules %}
  <article class="card rule-card" id="rule-{{ rule.slug }}">
    <h3 class="card__title">{{ rule.title }}</h3>
    <p class="rule__body">{{ rule.body }}</p>
  </article>
  {% endfor %}
</section>

<section class="science-section" id="section-cardio">
  <h2 class="section-header">Place du cardio</h2>
  <!-- 150-200 mots -->
</section>

<section class="science-section" id="section-diagram">
  <h2 class="section-header">Architecture du produit</h2>
  <figure class="science-diagram"><!-- SVG --></figure>
</section>
{% endblock %}
```

### CSS ajouts

Minimaux :
- `.science-section` avec `margin-bottom: var(--space-xl)` pour aerer
- `.science-diagram` centre, responsive

Pas de nouveaux tokens requis. Tout reutilise les tokens V2.1.

---

## 10. Dependances

- Depend des 8 method_rules actuels — ils restent la base editoriale de la section 3.
- Depend de la spec Cardio pour synchroniser la section 4 (sinon, V1 sans details cardio data).
- Depend de la spec Launcher pour coherence des wording "Programmes", "Seance", "Historique".
- N'interfere avec aucune autre spec.

---

## 11. Risques

| Risque | Mitigation |
|--------|------------|
| La page devient trop longue et personne ne la lit | Structure en sections avec ancres deep-link. TOC flottant possible en V2 si besoin. |
| Contenu editorial divergent des conventions UI | Regle dure : tout vocabulaire renvoie a ce qui est dans l'interface. Si le mot n'est pas dans l'app, il ne devrait pas etre dans la page Science. |
| Le diagramme SVG devient complique a maintenir | Le code SVG est dans un seul template, facile a modifier. Pas de generation runtime. |
| Pseudo-science involontaire | Chaque claim doit etre formulable au conditionnel ou factuel observable. Revue editoriale obligatoire avant merge. |
| Contenu "Comment fonctionne" devient obsolete | Synchroniser avec la doc DOMAIN_MODEL.md a chaque sprint qui touche au modele. |

---

## 12. Conflits potentiels avec chantiers existants

| Chantier | Conflit | Resolution |
|----------|---------|------------|
| `SPIGNOS_EXERCISE_FEEDBACK_RATIONALIZATION.md` | Section 2.4 doit refleter que success_score est derive, pas saisi | Deja prevu dans la redaction. |
| `SPIGNOS_MOBILE_EXERCISE_ENTRY_UX.md` | Section 2.3 doit refleter l'accordion `<details>` sans pretendre que c'est "revolutionnaire" | Redaction factuelle : "une seance affiche un exercice a la fois, les autres restent accessibles". |
| `SPIGNOS_EXERCISE_SUBSTITUTION_GRAPH_SPEC.md` | Section 2.3 peut mentionner la substitution. | Optionnel — ne pas forcer si ca alourdit. |
| `SPIGNOS_SQUADS_PRIVACY_MODEL.md` | Section 2.7 doit refleter exactement le privacy model | Reprise directe du wording du privacy model. |
| `SPIGNOS_VISUAL_IDENTITY_V2.md` | Ton editorial aligne avec le lexicon V2.1 | Verification obligatoire. |
| `SPIGNOS_SCORING_RULES_V1.md` | Section 2.6 doit refleter la politique "no false precision" | Reprise du pattern "axe grise si donnees insuffisantes". |

**Aucun conflit bloquant detecte.**

---

## 13. Acceptance criteria

### Editorial

- [ ] Les 5 sections sont presentes dans l'ordre defini
- [ ] Chaque section respecte sa longueur cible
- [ ] Aucun mot de la liste "A eviter" n'apparait dans la page
- [ ] Tout vocabulaire utilise est coherent avec l'UI (Serie, Echauf., etc.)
- [ ] Aucune promesse de resultat
- [ ] Aucune citation pseudo-scientifique non sourcee
- [ ] Section 2 couvre les 7 sous-sections produits
- [ ] Les 8 method_rules sont integralement reprises en section 3

### Technique

- [ ] Route `/science` existe et rend la page
- [ ] Route `/rules` redirige 301 vers `/science`
- [ ] Le tile home est "Science" au lieu de "Regles"
- [ ] Ancre deep-link fonctionne pour chaque method_rule (`#rule-carnet-progression`, etc.)
- [ ] SVG diagramme est accessible (title + desc)
- [ ] SVG respecte les tokens CSS SPIGNOS
- [ ] Page responsive mobile (viewport 375px, pas de scroll horizontal hors diagramme si inevitable)
- [ ] Zero JS requis

### Tests

- [ ] Test `/science` retourne 200 et contient "Science"
- [ ] Test `/rules` redirige vers `/science`
- [ ] Test que les 8 rules apparaissent dans la page
- [ ] Test que l'ancre `#rule-carnet-progression` est presente
- [ ] Test que le SVG diagramme est rendu (contains `<svg`)

---

## 14. Lotissement recommande

| Sprint | Contenu | Duree estimee |
|--------|---------|--------------|
| **Sb_science_editorial** | Redaction des 5 sections (texte + integration des method_rules), renommage route, template | Moyen |
| **Sb_science_diagram** | SVG architecture modules, CSS associe | Moyen |
| **Sb_science_nav** | Tile home, nav, redirect `/rules → /science`, tests | Petit |

Ces sprints peuvent se faire sequentiellement ou en parallele selon les ressources.

---
