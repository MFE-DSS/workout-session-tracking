# Dogfood Template — Sx_30 Progressive Overload Engine

**Status :** PENDING (à exécuter par l'utilisateur, ne pas simuler)
**Cible :** plusieurs séances réelles sur ≥ 2 semaines pour observer les 5 états sur l'historique vivant.

---

## 1. Setup

| Item | Valeur |
|---|---|
| Date début dogfood | _à remplir_ |
| Date fin dogfood | _à remplir_ |
| Nombre de séances réelles | _≥ 4 recommandé pour observer ≥ 2 états_ |
| Device principal | iPhone / Android — modèle |
| Viewport | 360×640 ou 390×844 |
| Mode JS | activé par défaut |
| Branche app | `claude/sprint-reporting-fitness-app-V7Qr6` |

## 2. Checklist Sx_30

### Sb_30.1 — Moteur (sanity contractuel, hors dogfood)
- [ ] Aucun crash sur la page session (engine = pure function, déterministe).
- [ ] `engine_version=1` propagé dans le DOM (`data-engine-version="1"` sur le wrapper).

### Sb_30.2 — Inputs + injection
- [ ] L'historique consulté semble correct (cf. "Dernière fois" et `kg/reps` cohérents).
- [ ] Pas de hint sur les exercices sans historique (état `unknown` silencieux).

### Sb_30.3 — UI first render
- [ ] Le hint apparaît UNIQUEMENT sur la carte active.
- [ ] Le hint est lisible en mode mobile 360×640 (pas de scroll horizontal).
- [ ] Les 5 états observables (au moins 2/5 vus pendant le dogfood) :
  - [ ] `progress` : "Tenter d'augmenter la charge" + cible kg+reps
  - [ ] `consolidate` : "Consolider la charge actuelle"
  - [ ] `top-range` : "Atteindre le bas de range"
  - [ ] `deload` : "Alléger temporairement"
  - [ ] `unknown` : silencieux (test indirect : exercices nouveaux n'affichent rien)
- [ ] Border-left + icône unicode (↑ → 🏁 ↓ ?) visibles en niveaux de gris.
- [ ] `<details>` "Pourquoi ?" s'ouvre / ferme correctement.

### Sb_30.4 — Legacy supprimé
- [ ] Aucun bloc "Repère :" n'apparaît plus sur la page session.
- [ ] Pas de redondance entre hints (1 seule source de guidance).

### Sb_30.5 — A11y consolidé
- [ ] Au clavier, Tab atteint le `summary` "Pourquoi ?".
- [ ] Le focus est visible (anneau ou équivalent).
- [ ] Si lecteur d'écran disponible : VoiceOver / TalkBack lit d'abord
      l'intent (`aria-labelledby`) puis le contenu.
- [ ] La cible chiffrée (102.5 kg · 6-10 reps) est mise en valeur visuellement
      (élément `<strong>`).

## 3. Frictions identifiées

| # | Friction | Sévérité (low/med/high) | Suggestion |
|---|---|---|---|
| 1 | _ex : icône trop discrète_ | _low_ | _augmenter font-size_ |
| 2 | | | |
| 3 | | | |

## 4. Validité du moteur (qualitatif)

| Question | Réponse |
|---|---|
| Le hint correspond-il à ce que tu aurais décidé manuellement ? (≥ 70% est un bon signal) | |
| Y a-t-il des cas où le hint te paraît clairement faux ? (lister) | |
| Le `deload` se déclenche-t-il quand tu te sens vraiment crammé ? | |
| Le `progress` te pousse-t-il à monter quand c'est légitime ? | |
| Le hint réduit-il le temps mental avant le premier set ? | |

## 5. Verdict dogfood

Choisir une option :

- [ ] ✅ **PASS** — Sx_30 améliore l'expérience. Engine v=1 stable.
- [ ] ⚠️ **PASS avec réserves** — Sx_30 utile mais N frictions à traiter
      (Sb_30.next.polish-1) ou règle à ajuster (Sb_30.next.engine-v2).
- [ ] ❌ **FAIL** — Engine v=1 trop souvent à côté du besoin. Itérer ou rollback.

**Justification (3-5 lignes) :**

> _à remplir_

## 6. Suivi post-dogfood

- [ ] Issue créée pour chaque friction sévérité ≥ med.
- [ ] Si v2 nécessaire : nouvelle migration `overload_engine_version` (Sb_30.next).
- [ ] Si v1 PASS : closure définitive Sx_30 + ouverture Sx_31 (Body v2) ou Sx_32 (PWA).

---

**Rappel contractuel :**
- Dogfood Sx_27 reste PENDING indépendamment.
- OQ-E (placeholder cible dans les inputs poids/reps) explicitement
  différée à `Sb_30.next.placeholder` sous override séparé.
- Options Sx_31 / Sx_32 / Sx_33+ restent bloquées tant qu'aucun
  override séparé n'est documenté.
