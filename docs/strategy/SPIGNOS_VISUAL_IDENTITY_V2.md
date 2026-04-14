# SPIGNOS Visual Identity V2 — Private Body Engineering Cockpit

**Date:** 2026-04-14
**Type:** Presentation-only refactor (zero backend/route/model changes)
**Scope:** CSS tokens, component grammar, lexicon, micro-copy, template markup

---

## 1. Diagnostic

### Ce qui fait "classique app web" aujourd'hui

| Probleme | Ou | Impact |
|----------|-----|--------|
| Labels anglais dans une app francophone | "Dashboard", "Logout", "Board", "Work", "Warmup", "Strong/Partial/Weak" | Rupture de ton, app hybride |
| Footer expose la stack | "SPIGNOS · FastAPI SSR · v1" | Amateur, pas un produit fini |
| Welcome page generique | "Workout Session Tracking" titre anglais | Pas de marque |
| Inline styles massifs | 80+ occurrences `style="margin..."` dans les templates | Source de verite eclatee |
| Couleurs hardcodees dans squad templates | `var(--c-success, #2ecc71)` — vars inexistantes | Fragilite, inconsistance |
| Accents manquants | "Activite", "Seance", "Metrique", "Donnees" | Negligence percue |
| Physique zone cards en bande | Empilement vertical sans grille | Page trop longue |
| Segmented controls anglais | "Strong/Partial/Weak", "High/Medium/Low" (post-fix partiel) | Incoherence avec le reste FR |

### Ce qui fait deja "cockpit"

- Nombres monospaces (JetBrains Mono, tabular-nums) — lecture instrument
- Indicateurs de tendance ↑↓→ — langage tactique
- Points de confiance colores — jauge
- Dark theme profond — concentration
- Barres de zone avec scores — tableau de bord
- Radar SVG hexagonal — visualisation technique
- `<details>` accordion — interaction sobre, zero JS
- Densite informationnelle sans decoration — pas de filler

---

## 2. Visual System V2 — Tokens

### 2.1 Palette surfaces (inchangee, rationalisee)

| Token | Hex | Role | WCAG note |
|-------|-----|------|-----------|
| `--bg` | `#0f1115` | Fond de page | — |
| `--surface` | `#161a22` | Cards, conteneurs | — |
| `--surface-2` | `#1e222c` | Inputs, surfaces imbriquees | — |
| `--border` | `#232834` | Separateurs discrets | — |

### 2.2 Palette texte

| Token | Hex | Sur --bg | Sur --surface | Usage |
|-------|-----|---------|--------------|-------|
| `--fg` | `#e8ecf1` | 15.2:1 | 12.8:1 | Texte primaire, titres, valeurs |
| `--fg-muted` | `#9aa3ad` | 6.1:1 | 5.1:1 | Labels, texte secondaire |
| `--fg-dim` | `#5a6270` | 3.2:1 | 2.7:1 | Hints, texte tertiaire (large text only, 3:1 OK pour 18px+) |

### 2.3 Accent unique

**Decision : garder `#f25f3a` (warm orange).** C'est l'identite visuelle SPIGNOS — energique sans etre criard. Pas de deuxieme accent.

| Token | Hex | Usage strict |
|-------|-----|-------------|
| `--accent` | `#f25f3a` | CTAs primaires, bordure focus, element actif, lien d'action |
| `--accent-soft` | `#f25f3a1a` | Background tint pour code exercice, highlight actif |

**Regles d'usage accent :**
- OUI : boutons primaires, bordure `<details>[open]`, exercise code badge, tile CTA, lien actif
- NON : texte long, fond de section, badge de statut, indicateur de tendance

### 2.4 Intent colors (reserves aux etats)

| Token | Hex | Semantique stricte |
|-------|-----|-------------------|
| `--ok` | `#2ecc71` | Termine, valide, positif. Jamais decoratif. |
| `--ok-soft` | `#2ecc711a` | Background tint ok |
| `--warn` | `#f4a261` | Attention, partiel, confiance moyenne |
| `--danger` | `#e74c3c` | Erreur, destructif, alerte |
| `--info` | `#3b82f6` | Informatif, cardio, neutre contextuel |

**Regle : pas de couleur sans signification.** Si un element est colore, il communique un etat.

### 2.5 Typographie

| Element | Font | Size | Weight | Extras | Usage |
|---------|------|------|--------|--------|-------|
| Corps | Inter | 14px | 400 | — | Texte courant |
| Label champ | Inter | 12px | 400 | `--fg-muted` | Au-dessus des inputs |
| Section header | Inter | 13px | 600 | uppercase, 0.5px tracking | Titres de section |
| Page title | Inter | 18px | 600 | — | H1 pages |
| Valeur KPI | JetBrains Mono | 24px | 700 | tabular-nums | Nombres clefs |
| Score global | JetBrains Mono | 36px | 700 | tabular-nums | Hero score (dashboard, physique) |
| Badge | JetBrains Mono | 11px | 600 | — | Statut, compteurs |
| Code exercice | JetBrains Mono | 12px | 700 | accent-soft bg | E1, E2, SPGN-XXXX |
| Micro-copy | Inter | 12px | 400 | `--fg-dim` | Sous-labels, hints |

**Regle mono :** tout nombre, code, score, identifiant technique est en `--font-mono`. Tout texte narratif/label est en Inter.

### 2.6 Spacing (inchange)

Echelle conservee : xs(4) sm(8) md(16) lg(24) xl(32) 2xl(48).

### 2.7 Radius (inchange)

- `--radius` (8px) : cards, conteneurs
- `--radius-sm` (4px) : boutons, inputs, badges

---

## 3. Lexicon System

### 3.1 Navigation

| Actuel | V2 | Raison |
|--------|-----|--------|
| Dashboard | Synthèse | Francais, plus precis que "Tableau de bord" |
| Board | Classement | Le mot complet, en francais |
| Logout | Déconnexion | Francais standard |
| Squads | Squads | Conserve — terme adopte, court, sans equivalent elegant |
| Programme | Programmes | Pluriel coherent |

**Nav V2 :** Accueil · Programmes · Historique · Physique · Synthèse · Classement · Squads · Profil · Déconnexion

### 3.2 Session page

| Actuel | V2 | Raison |
|--------|-----|--------|
| Work | Travail | Francais. "Work #1" → "Série #1" |
| Warmup | Échauffement | Francais. "Warmup #1" → "Échauf. #1" |
| Fait (checkbox) | ✓ (visuel seul) | Le mot "Fait" est vague. La coche suffit. |
| Strong / Partial / Weak | Fort / Partiel / Faible | Francais. Coherent avec le reste. |
| Feedback session | Bilan de la séance | Deja corrige dans Sb_02 — confirmer partout. |
| Feedback exercice | Ressenti exercice | Plus naturel que "Feedback" |

### 3.3 Dashboard / Body Engineering

| Actuel | V2 | Raison |
|--------|-----|--------|
| Body Engineering | Synthèse corporelle | Francais, sobre, pas pseudo-scientifique |
| Training Consistency | Régularité | Deja dans le texte des regles |
| Overload / Progression | Progression | Mot unique, clair |
| Body Trend | Évolution corporelle | Francais |
| Recovery / Readiness | Récupération | Mot unique |
| Muscular Balance | Équilibre musculaire | Francais |

### 3.4 Readiness

| Actuel | V2 |
|--------|-----|
| Readiness du jour | État du jour |
| Historique Readiness | Historique état |
| Sommeil / Fatigue / Courbatures / Stress / Motivation | Inchange (deja FR) |

### 3.5 Pages titres

| Page | Titre actuel | Titre V2 |
|------|-------------|----------|
| `/` | Accueil | Accueil |
| `/dashboard` | Body Engineering | Synthèse |
| `/physique` | Physique | Physique |
| `/library` | Programmes de séance | Programmes |
| `/history` | Historique | Historique |
| `/progress` | Progression | Progression |
| `/leaderboard` | Leaderboard | Classement |
| `/squads` | Squads | Squads |
| `/profile` | Profil | Profil |
| `/readiness/history` | Historique Readiness | Historique état |
| `/export` | Export | Sauvegarde |

### 3.6 Welcome page rebrand

| Actuel | V2 |
|--------|-----|
| "Workout Session Tracking" | "SPIGNOS" |
| "Suis ta progression..." | "Cockpit privé d'entraînement et de suivi corporel." |
| Footer "FastAPI SSR · v1" | "SPIGNOS" (sans mention tech) |

### 3.7 Micro-copy tone rules

- **Voix :** tutoiement, factuel, court. Pas de superlatifs. Pas de vocabulaire IA.
- **Longueur :** labels ≤ 3 mots. Descriptions ≤ 15 mots.
- **Pattern :** [Verbe imperatif] ou [Nom + contexte]. Ex: "Enregistrer E2", "Séance terminée", "Données insuffisantes — renseigner tes mesures."

---

## 4. Page Map

### 4.1 Surface types

| Type | Definition | Pages |
|------|-----------|-------|
| **Action surface** | L'utilisateur fait quelque chose (logger, creer) | Session, Squad create/join, Challenge create |
| **Evidence surface** | L'utilisateur voit ses donnees brutes | History, Exercise history, Readiness history, Export |
| **Analytics surface** | Synthese calculee + confiance | Dashboard, Physique, Progress, Challenge standings |
| **Privacy surface** | Donnees partagees avec un scope controle | Squad detail, Leaderboard, Compare, Shared sessions |

### 4.2 Par page

| Page | Surface | Layout mobile | Composants | Micro-copy cle |
|------|---------|--------------|------------|----------------|
| `/` (Accueil) | Action + Analytics | Linear: readiness widget → insight → KPIs → sparkline → tiles | insight-block, kpi-row, segmented, tile-grid, sparkline | "État du jour", "disponibilité", "Nouvelle séance" |
| `/sessions/{id}` | Action | Linear: header → jumpbar → accordion cards → bilan | exercise-card (details), set-row, segmented, jumpbar | "Série #1", "Échauf. #1", "Enregistrer E2" |
| `/dashboard` | Analytics | Linear: hero score → filter → 5 axis cards → regles | metric-strip, confidence-chip, filter-bar, rules-details | "Synthèse", "Basé sur N axes", "Données insuffisantes" |
| `/physique` | Analytics | Linear: radar → filter → zone grid | radar-svg, zone-card (grid), filter-bar | "Physique", "Détail par zone" |
| `/history` | Evidence | Linear: filter → session cards | filter-bar, session-card | "Historique", "en cours", "terminée" |
| `/progress` | Analytics | Linear: KPIs → per-template → activity → timelines | kpi-row, stats-list, timeline-svg | "Progression", "Activité récente" |
| `/library` | Action | Linear: section groups → template cards | section-header, template-card | "Programmes", "Démarrer" |
| `/squads/{id}` | Privacy | Linear: leaderboard → challenges → activity → sharing forms | leaderboard-table, challenge-card, activity-item, sharing-form | "Classement", "Activité de la squad" |
| `/squads/{id}/compare` | Privacy | Linear: member selects → comparison table | comparison-table, member-select | "Comparer deux membres" |
| `/squads/{id}/challenges/{cid}` | Analytics + Privacy | Linear: meta → standings | standings-table, metric-badge | "Classement du défi" |
| `/leaderboard` | Privacy | Linear: ranking table + privacy note | leaderboard-table, privacy-note | "Classement global", "Données privées protégées" |
| `/profile` | Action + Evidence | Linear: identity → 30d → measurements → charts | stats-list, measurement-form, timeline-svg | "Profil", "Évolution corporelle" |
| `/readiness/history` | Evidence | Linear: entry cards | readiness-card, badge-row | "Historique état" |

---

## 5. Component Grammar

### 5.1 Card variants

| Variant | Classe | Usage | Style |
|---------|--------|-------|-------|
| **Command card** | `.card` | Forms, actions (session feedback, squad create) | `--surface`, `--border`, standard padding |
| **Signal card** | `.card.card--signal` | Alertes, insight, readiness widget | Bordure gauche accent (3px) |
| **Metric strip** | `.card.card--metric` | Axe dashboard, zone physique | Compact padding, barre de score inline |
| **Evidence panel** | `.card.card--evidence` | History row, readiness entry | Surface plus legere, pas de bord accent |

### 5.2 Status chips

| Chip | Classe | Couleur | Usage |
|------|--------|---------|-------|
| Confiance élevée | `.chip--confidence-high` | `--ok` text, `--ok-soft` bg | Dashboard axes, zone cards |
| Confiance moyenne | `.chip--confidence-medium` | `--warn` text | Dashboard axes |
| Confiance faible | `.chip--confidence-low` | `--fg-dim` text | Dashboard axes |
| Données insuffisantes | `.chip--insufficient` | `--fg-dim` text, dashed border | Axe grise |
| Privé | `.chip--private` | `--fg-dim` text, lock icon prefix | Squads privacy indicator |
| Terminée | `.badge--completed` | `--ok` | Session status |
| En cours | `.badge--in_progress` | `--accent` | Session status |

### 5.3 Navigation

**Topbar V2 :** conserve le pattern sticky, mais le menu deborde sur mobile. Solution :

```html
<header class="topbar">
  <a class="topbar__brand" href="/">SPIGNOS</a>
  <details class="topbar__menu">
    <summary class="topbar__toggle" aria-label="Menu">☰</summary>
    <nav class="topbar__nav">
      <a href="/">Accueil</a>
      <a href="/library">Programmes</a>
      <a href="/history">Historique</a>
      <a href="/physique">Physique</a>
      <a href="/dashboard">Synthèse</a>
      <a href="/leaderboard">Classement</a>
      <a href="/squads">Squads</a>
      <a href="/profile">Profil</a>
      <form method="post" action="/logout">
        <button type="submit">Déconnexion</button>
      </form>
    </nav>
  </details>
</header>
```

**Zero JS.** Le `<details>` ouvre/ferme le menu. Sur desktop (>768px), la nav est toujours visible en ligne. Sur mobile, elle est cachee dans le hamburger.

### 5.4 `<details>`/`<summary>` patterns

| Pattern | Style `<summary>` | Style `[open]` | Usage |
|---------|-------------------|---------------|-------|
| Exercise accordion | Code + nom + progress + recap. Curseur pointer. | Bordure accent. | Session page |
| Readiness form | "État du jour". Curseur pointer. | — | Home |
| Scoring rules | "Règles de calcul". Dim text. | — | Dashboard |
| Substitution picker | "Machine indisponible ?". Dim text. | — | Exercise card |
| Sensation musculaire | "Ressenti musculaire (optionnel)". Dim text. | — | Exercise card |
| Mobile nav | Hamburger icon. | Nav visible. | Topbar |

---

## 6. Plan de refactor presentation-only

### Ordre d'execution

| Etape | Fichier(s) | Changement | Risque |
|-------|-----------|-----------|--------|
| 1 | `app/static/css/app.css` | Ajouter card variants, chip classes, topbar mobile menu, utility classes (`.mt-md`, `.mb-sm`, etc.). Supprimer classes mortes. | Nul — additif |
| 2 | `app/templates/base.html` | Renommer nav labels (Synthese, Classement, Deconnexion). Ajouter `<details>` hamburger mobile. Nettoyer footer. | Faible — label changes |
| 3 | `app/templates/welcome.html` | Rebrand: titre "SPIGNOS", sous-titre FR, supprimer mention tech | Nul |
| 4 | `app/templates/session_detail.html` | Franciser: Travail/Echauffement, Fort/Partiel/Faible, "Ressenti exercice". Remplacer inline styles par classes. | Faible — texte + CSS |
| 5 | `app/templates/dashboard.html` | Renommer axes FR, titre "Synthese". Remplacer inline styles. | Faible |
| 6 | `app/templates/index.html` | "Etat du jour", nettoyer inline styles | Faible |
| 7 | `app/templates/history.html` | Remplacer inline styles par classes | Nul |
| 8 | `app/templates/physique.html` | Titre "Physique", nettoyer inline styles zone grid | Nul |
| 9 | `app/templates/leaderboard.html` | Titre "Classement", ajouter privacy chip visible | Faible |
| 10 | `app/templates/squad_*.html` | Fixer accents (Activite→Activité, Seance→Séance), remplacer vars hardcodees, ajouter privacy chips | Moyen — 8 templates |
| 11 | `app/templates/progress.html` | Labels FR, nettoyer inline | Nul |
| 12 | `app/templates/profile.html` | Labels FR, nettoyer inline | Nul |
| 13 | `app/templates/readiness_history.html` | Titre "Historique état" | Nul |
| 14 | `app/templates/export.html` | Titre "Sauvegarde", supprimer texte dev-facing | Faible |
| 15 | Tests | Adapter assertions qui matchent sur texte exact (labels changes) | Moyen |

### Regles strictes

- **Aucune route ne change**
- **Aucun modele DB ne change**
- **Aucune logique metier ne change**
- **Aucun fichier Python de service ne change**
- Uniquement : `app.css` + `app/templates/*.html` + tests (assertions textuelles)

---

## 7. Acceptance Criteria

### Coherence marque

- [ ] Toutes les nav labels sont en francais (zero mot anglais dans la topbar)
- [ ] Footer ne mentionne plus la stack technique
- [ ] Welcome page affiche "SPIGNOS" + tagline FR
- [ ] "Body Engineering" remplace par "Synthèse" partout
- [ ] "Leaderboard" remplace par "Classement" partout

### Lexique stabilise

- [ ] "Work" → "Travail" / "Série" dans session_detail
- [ ] "Warmup" → "Échauffement" / "Échauf." dans session_detail
- [ ] "Strong/Partial/Weak" → "Fort/Partiel/Faible"
- [ ] Tous les accents presents (Activité, Séance, Métrique, Données)
- [ ] Tous les titres de page en francais

### Mobile UX

- [ ] Pas de scroll horizontal sur aucune page (viewport 375px)
- [ ] Topbar hamburger menu fonctionne sans JS sur mobile
- [ ] Cibles tactiles ≥ 44px sur tous les boutons/liens
- [ ] Zone cards physique en grille responsive (pas de bande verticale)

### Lisibilite low-light

- [ ] Texte `--fg` sur `--bg` ≥ 15:1 (deja OK)
- [ ] Texte `--fg-muted` sur `--surface` ≥ 4.5:1 (#9aa3ad sur #161a22 = 5.1:1 OK)
- [ ] Texte `--fg-dim` utilise uniquement pour text ≥ 18px ou non-essentiel

### Privacy cues

- [ ] Leaderboard affiche une note privacy visible ("Données privées protégées")
- [ ] Squad detail montre un indicateur "Activité partagée · Données privées protégées"
- [ ] Aucun poids/reps/note/readiness dans les vues squad/leaderboard

### Dashboard non pseudo-scientifique

- [ ] Score global affiche nombre d'axes actifs ("Basé sur N axes sur 5")
- [ ] Chaque axe insuffisant affiche guidance ("Renseigner vos mesures")
- [ ] Regles de calcul accessibles (collapsible en bas)
- [ ] Confiance affichee par axe et globalement

### Zero inline styles

- [ ] Aucun attribut `style="..."` dans les templates (ou < 10 exceptions justifiees)
- [ ] Toutes les valeurs de spacing utilisent les tokens CSS (`--space-*`)
