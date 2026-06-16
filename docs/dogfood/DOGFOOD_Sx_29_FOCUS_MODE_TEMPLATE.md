# Dogfood Template — Sx_29 Mobile Session Focus Mode

**Status :** PENDING (à exécuter par l'utilisateur, ne pas simuler)
**Cible :** une vraie séance, sur un vrai mobile, en conditions de salle.

---

## 1. Setup

| Item | Valeur |
|---|---|
| Date séance | _à remplir_ |
| Device | iPhone / Android — modèle |
| Viewport | 360×640 (ou 390×844 si plus large) |
| Connexion | Wi-Fi / 4G / hors-ligne |
| Mode JS | JS activé (par défaut) |
| Session ID | _à remplir_ |
| Branche app | `claude/sprint-reporting-fitness-app-V7Qr6` à la date du dogfood |

## 2. Checklist Sx_29 (mobile 360×640)

Cocher après usage réel pendant la séance.

### Sb_29.1 — Visual skeleton
- [ ] Header reste visible en scroll (sticky)
- [ ] Jump bar visible et lisible
- [ ] La carte de l'exercice courant est ouverte par défaut
- [ ] Tap targets ≥ 44×44 confortables (pas de mis-tap)
- [ ] Aucun scroll horizontal sur 360×640
- [ ] Lecture confortable d'un bras (ergonomie pouce)

### Sb_29.2 — Active navigation
- [ ] Je sais TOUJOURS quelle est ma carte active (regard rapide)
- [ ] États done / partial / skipped / substituted distinguables non-color
- [ ] Jump bar montre la progression réelle
- [ ] Bullet `•` ou check `✓` lisible en niveaux de gris

### Sb_29.3 — Sticky CTA
- [ ] "Enregistrer et passer à X" reste visible en bas pendant le scroll
  de la carte active
- [ ] Sur iPhone notch : pas de chevauchement avec home indicator
- [ ] CTA ne masque pas le contenu critique au-dessus
- [ ] Pas de scintillement (flicker) au scroll

### Sb_29.4 — Rest timer
- [ ] "Repos suggéré : 90s" visible après validation d'un set
- [ ] Countdown JS décrémente correctement
- [ ] Bouton "Skip rest" arrête le timer
- [ ] Aucun POST déclenché par le skip
- [ ] Aria-live "polite" lu par un lecteur d'écran (si testable)

### Sb_29.5 — Closure / cascade
- [ ] `session_focus.css` chargé sur la page (DevTools Network)
- [ ] Pas de FOUC (flash of unstyled content) entre app.css et session_focus.css
- [ ] Aucune erreur console JS

## 3. No-JS fallback (optionnel mais recommandé)

Désactiver JavaScript dans le navigateur :

- [ ] La page charge
- [ ] Sticky header + jump bar + active card OK (CSS pur)
- [ ] Sticky CTA OK (CSS pur)
- [ ] Rest timer affiche "Repos suggéré : 90s" STATIQUE (pas de countdown)
- [ ] Bouton "Skip rest" n'a aucun effet (mais n'envoie rien)
- [ ] Tous les POST update_exercise_card fonctionnent
- [ ] Navigation prev/next via boutons submit OK

## 4. Frictions identifiées

| # | Friction | Sévérité (low / med / high) | Suggestion |
|---|---|---|---|
| 1 | _ex : rest timer trop petit_ | _med_ | _agrandir font-size en mobile_ |
| 2 | | | |
| 3 | | | |

## 5. Mesures qualitatives

| Item | Avant Sx_29 | Après Sx_29 |
|---|---|---|
| Temps mental pour identifier "où suis-je ?" | | |
| Nombre de scrolls pour logger un set | | |
| Frictions globales (1–5) | | |

## 6. Verdict dogfood

Choisir une option :

- [ ] ✅ **PASS** — Sx_29 améliore réellement l'expérience mobile. Sx_30 peut ouvrir.
- [ ] ⚠️ **PASS avec réserves** — Sx_29 utile mais N frictions à traiter en `Sb_29.next.polish-1`.
- [ ] ❌ **FAIL** — Sx_29 introduit plus de friction qu'il n'en retire. Rollback ou refonte.

**Justification (3–5 lignes) :**

> _à remplir_

## 7. Suivi post-dogfood

- [ ] Issue ouverte pour chaque friction `Sévérité ≥ med`
- [ ] Closure report Sx_29 mis à jour avec verdict dogfood
- [ ] Sb_29.next.polish-1 priorisé si réserves
- [ ] Sx_30 débloqué si PASS strict

---

**Rappel contractuel :**
- Dogfood Sx_27 reste PENDING — ne pas le confondre.
- Options B/C/D/E restent bloquées tant que dogfood Sx_29 PENDING.
- Sx_30 ne s'ouvre PAS automatiquement après Sx_29 technically closed —
  override utilisateur ou validation dogfood explicite requise.
