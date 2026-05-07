# SPIGNOS — Passe de Dogfooding v1

**Début :** 2026-04-21
**Fin cible :** 2026-04-28 (7 jours)
**Branche prod :** `claude/sprint-reporting-fitness-app-V7Qr6` (SHA de début : `19c9c52`)
**Mode :** observation structurée, usage réel en salle, pas de modification produit pendant la passe.

---

## Pourquoi cette passe

Le cycle Session System V1 est livré (Sb_05 → Sb_10), enrichi de Sb_11a (vignettes chip + peek) et de Sb_12 (recommandation next-session). Sb_13 a ajouté la télémétrie `creation_source` + le CLI `scripts/reco_calibration_report.py`. Il manque maintenant **la validation d'usage réel** avant d'ouvrir un nouveau chantier produit (Sx_11b programme-builder, Sx_13.1 calibration, etc.).

**Contrat de la passe :**
- 1 note rapide par jour (< 2 min).
- Aucune modification de constantes / scoring / templates pendant les 7 jours (garder le signal lisible).
- À J+7 : `python scripts/reco_calibration_report.py --days 7 --user-id <ID>` + synthèse §Résultats.
- Ensuite : décision produit (calibrer Sx_13.1 / ouvrir Sx_11b / autre).

---

## Axes d'observation

Les 4 zones à surveiller pendant chaque séance. Je note uniquement ce qui m'**agace** ou ce qui me **surprend** — pas besoin de cocher « tout va bien ».

### Z1 — Cartes session (Sb_05)

- Une seule carte ouverte à la fois ? Pas de friction pour scroller entre exos ?
- Le bouton « Enregistrer et passer à E{next} » est-il naturel ? Le « ← E{prev} » est-il visible quand utile ?
- Recap line (`N kg · N reps`) sur la carte pliée aide-t-elle réellement ?
- Jump bar en haut est-elle consultée ? Jamais ? Souvent ?

### Z2 — Vignettes briefing (Sb_11a)

- **Chip** sur le `<summary>` des cartes futures : le `3×8-12 · dernière fois 60 kg × 10` est-il lisible du premier coup d'œil ?
- **Peek** en bas de carte active : le rappel du prochain exo (code + nom + 2 cues) est-il utile pour préparer pendant le repos ?
- Les cues d'atlas affichées dans le peek sont-elles pertinentes ou juste du bruit ?
- Mobile 375px : la densité tient-elle sans surcharge ?

### Z3 — Recommandation (Sb_12)

- La suggestion top-1 sur `/` matche-t-elle mon intuition du jour ? Dans combien de cas sur 7 ?
- La phrase d'explication est-elle crédible ou générique ?
- Est-ce que je clique souvent sur les alternatives plutôt que le top-1 ? Est-ce que je bypass carrément via `/library` ou `/launcher` ?
- Aucun cas où la reco a paru clairement hors-piste ? (noter lequel + pourquoi)

### Z4 — Télémétrie (Sb_13)

Passive, pas à observer activement pendant la séance. À J+7 :

```bash
python scripts/reco_calibration_report.py --days 7 --user-id <TON_ID>
```

Reporter les 4 indicateurs en §Résultats : `reco_acceptance_rate`, `alt_click_rate`, `bypass_rate`, `phrase_repetition_rate`.

---

## Rituel quotidien

**Temps estimé : 90 s / jour.**

1. Avant la séance : ouvrir `/`, noter la reco top + phrase.
2. Décider : accepter, alternative, ou bypass (via `/library` ou `/launcher`). Si bypass, noter **pourquoi**.
3. Pendant la séance : laisser les vignettes faire leur boulot, observer sans intervenir.
4. Après la séance : en 2 phrases max, reporter ce qui a agacé ou surpris (voir §Journal quotidien).

**Règle stricte :** ne pas modifier de constante, ne pas ouvrir de PR de fix UX, ne pas changer de template. La passe est figée sur SHA `19c9c52`.

---

## Journal quotidien

Format par entrée : date, template utilisé, 1-3 bullets d'observation. Ajouter au fil de l'eau.

### 2026-04-21 (Jour 1)

- Template choisi : …
- Reco proposée : …
- Observation(s) : …

### 2026-04-22 (Jour 2)

- …

### 2026-04-23 (Jour 3)

- …

### 2026-04-24 (Jour 4)

- …

### 2026-04-25 (Jour 5)

- …

### 2026-04-26 (Jour 6)

- …

### 2026-04-27 (Jour 7)

- …

---

## Résultats à J+7 (2026-04-28)

### Télémétrie Sb_13

Lancer :

```bash
python scripts/reco_calibration_report.py --days 7 --user-id <ID>
```

Reporter tel quel :

```
Sessions (window)     : …
reco_acceptance_rate  : …
alt_click_rate        : …
bypass_rate           : …
phrase_repetition_rate: …
Top phrases           : …
```

### Synthèse qualitative

**Cartes Sb_05 — verdict :**
- Friction observée : …
- Feature non utilisée : …
- Feature manquante : …

**Vignettes Sb_11a — verdict :**
- Chip utilisée en vrai ? oui / non / parfois
- Peek utile ? oui / non / parfois
- Cues atlas pertinents ? …

**Recommandation Sb_12 — verdict :**
- La reco a tapé juste N/7 fois
- Phrases qui reviennent trop souvent : …
- Cas clairement hors-piste : …

### Décision produit post-passe

Trois chemins possibles (voir Sx_13 §M) :

- [ ] **Chemin A** — reco stable, calibration OK → ouvrir **Sx_11b programme-builder utilisateur**.
- [ ] **Chemin B** — reco bruyante → ouvrir **Sx_13.1 cycle calibration 2** (ajuster 1-2 constantes).
- [ ] **Chemin C** — friction UX sur vignettes/cartes identifiée → mini sprint Sb_11a.1 ciblé.

Cocher une seule case. Justifier en 2 lignes.

---

## Commandes utiles pendant la passe

```bash
# Voir le SHA en prod
ssh ubuntu@vps-491c685f.vps.ovh.net "cd /opt/workout-session-tracking && git rev-parse HEAD"

# Voir les derniers deploys
ssh ubuntu@vps-491c685f.vps.ovh.net "cd /opt/workout-session-tracking && git log --oneline -5"

# Générer le rapport reco à J+7
python scripts/reco_calibration_report.py --days 7 --user-id <TON_ID>

# Rollback rapide si problème critique observé en séance (quasi impossible mais au cas où)
# → GitHub Actions → Deploy production → Run workflow → ref: <SHA-précédent>
```

---

## Ce qu'on ne fait PAS pendant la passe

- Aucun commit sur des templates, services, ou constantes de reco.
- Aucun nouveau sprint de spec.
- Aucun nouveau build.
- Aucun rollback sauf incident bloquant en séance.
- Aucune modification des systemd timers pendant la fenêtre (stabilité des signaux).

La passe est un **gel technique volontaire** de 7 jours pour laisser le signal utilisateur parler.
