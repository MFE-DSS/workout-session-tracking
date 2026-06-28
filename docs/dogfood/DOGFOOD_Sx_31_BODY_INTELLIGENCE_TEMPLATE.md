# Dogfood Template — Sx_31 Body Intelligence v2

**Status :** PENDING (à exécuter par l'utilisateur, ne pas simuler)
**Cible :** ≥ 2 semaines d'usage réel sur les 2 surfaces (`/body/intelligence` + `/coach-report`).

---

## 1. Setup

| Item | Valeur |
|---|---|
| Date début dogfood | _à remplir_ |
| Date fin dogfood | _à remplir_ |
| Nombre de consultations `/body/intelligence` | _≥ 4 recommandé_ |
| Nombre de consultations `/coach-report` | _≥ 2 recommandé_ |
| Device principal | iPhone / Android — modèle |
| Viewport | 360×640 (ou 390×844 si plus large) |
| Mode JS | activé par défaut |
| Branche app | `claude/sprint-reporting-fitness-app-V7Qr6` |
| Surface canonique | `/body/intelligence` (collision `/body` = Body Manual Profile PR #15) |

## 2. Checklist Sx_31

### A. Page `/body/intelligence`

**Lisibilité headline + bullets**
- [ ] Headline lisible d'un coup d'œil (`Lecture corporelle…` / `Lecture partielle…` / `Données insuffisantes…` selon statut).
- [ ] Bullets ≤ 4 informatifs (séances loggées, delta volume, message priorité).
- [ ] Le statut global (`ok` / `partial_data` / `insufficient_data`) est compréhensible **hors couleur** (cue `•` / `~` / `?`).

**Utilité des 7 blocs**
- [ ] `training_consistency` — j'y lis bien ma régularité 7/30/90j.
- [ ] `body_metrics` — taille / poids / waist / trend / **BMI** affichés clairement (BMI accompagné du disclaimer).
- [ ] `muscle_zone_balance` — top et bottom 3 zones lisibles.
- [ ] `push_pull_legs_balance` — ratios push/pull et haut/bas explicites (marqueur "à confirmer" si déséquilibré).
- [ ] `quality_and_confidence` — quality_score moyen 30j + confidence visibles.
- [ ] `implicit_signal_summary` — distribution labels lisible.
- [ ] `unavailable_or_limits` — toujours présent, mentionne explicitement composition / esthétique / posture / cardio / médical.

**Compréhension des badges classification**
- [ ] **Mesuré** — je comprends que c'est une donnée saisie / enregistrée.
- [ ] **Dérivé** — je comprends que c'est calculé à partir des Mesurés.
- [ ] **Inféré** — je comprends que c'est probabiliste, à vérifier.
- [ ] **Hors de portée** — je comprends que SPIGNOS ne le sait pas.

**Crédibilité des priorités**
- [ ] La (les) priorité(s) ressemble(nt) à ce que j'aurais conseillé à moi-même ?
- [ ] Le détail "Pourquoi ?" (déplié) est mécaniquement clair (pas du bullshit).
- [ ] Aucune priorité ne se contredit avec une autre.
- [ ] Cap 3 respecté (jamais plus de 3 cartes priorité).

**Clarté des limites**
- [ ] Le bloc `Hors de portée` est immédiatement repérable.
- [ ] Je comprends sans ambiguïté ce que SPIGNOS **ne sait pas** mesurer.
- [ ] L'`overload_compliance_status = not_available_v1` est rendu visible (information honnête).

**Comportement mobile réel (360×640)**
- [ ] Aucun scroll horizontal.
- [ ] Aucun débordement sur badges classification (les libellés longs ne cassent pas le head).
- [ ] Padding suffisant pour le tap target sur le summary "Pourquoi ?".
- [ ] Texte lisible sans zoom.
- [ ] Outline clavier visible si Tab utilisé.

### B. Bloc Snapshot dans `/coach-report`

**Utilité**
- [ ] Le snapshot apporte une vraie synthèse rapide avant d'attaquer les sections détaillées 2-9.
- [ ] Le badge status est clair (`Sur les séances loggées` / `Partiel` / `Données partielles`).
- [ ] Bullets et priorités ≤ 3 — pas de mur de texte.

**Non-redondance avec la page complète**
- [ ] Le snapshot **ne réimprime PAS** les 7 blocs (différent volontairement de `/body/intelligence`).
- [ ] Pas de double affichage du headline ou des limites.
- [ ] Pas de duplication des chiffres déjà présents dans la Section 1 Identité.

**Clarté du CTA "Voir le détail"**
- [ ] Le lien est visible et identifiable comme actionnable.
- [ ] Au lecteur d'écran, l'aria-label *"Voir le détail de la lecture corporelle Body Intelligence"* est lu correctement.
- [ ] La flèche `→` est purement visuelle (ne brouille pas l'annonce AT).

**Pertinence emplacement section 1bis**
- [ ] L'enchaînement Identité → Snapshot Body → Volume me semble logique.
- [ ] Aucune section coach existante n'est cassée visuellement.
- [ ] Le format print A4 (`window.print()`) reste correct.

### C. Critères terrain

- [ ] **≥ 2 semaines** entre première et dernière consultation.
- [ ] **≥ 4 consultations** `/body/intelligence`.
- [ ] **≥ 2 consultations** `/coach-report`.
- [ ] **≥ 3 observations utiles** notées dans la section 4 ci-dessous.

## 3. Frictions / observations utiles

| # | Friction / observation | Sévérité (low / med / high) | Suggestion |
|---|---|---|---|
| 1 | _ex : padding du bloc body_metrics trop petit sur iPhone SE_ | _low_ | _bumper à 12px en 360px_ |
| 2 | | | |
| 3 | | | |
| 4 | | | |

## 4. Questions à trancher après dogfood

| Question | Réponse | Si OUI : sprint candidat |
|---|---|---|
| Faut-il ajouter un **lien `/profile` → `/body/intelligence`** ? | _OUI / NON_ | `Sb_31.next.profile-link` |
| Faut-il ajouter une **carte home mini-summary** ? | _OUI / NON_ | `Sb_31.next.home-card` |
| Faut-il **raffiner les seuils** du composer (MIN_SESSIONS_CONSISTENCY, LOW_QUALITY, IMBALANCE_*) ? | _OUI / NON_ | `Sb_31.next.thresholds-v2` (bump `BODY_INTELLIGENCE_VERSION` à 2) |
| Faut-il **intégrer overload compliance** (agrégat 30j des hints Sx_30) ? | _OUI / NON_ | `Sb_31.next.overload-compliance` |
| Faut-il **simplifier certains blocs** (ex : fusionner push/pull/legs avec muscle_zone_balance) ? | _OUI / NON_ | `Sb_31.next.blocks-merge` |

## 5. Verdict dogfood

Choisir une option :

- [ ] ✅ **PASS** — Sx_31 améliore réellement la lecture corporelle. Aucune régression. Prêt pour Sx_32 / Sx_33+.
- [ ] ⚠️ **WARN** — Sx_31 utile mais N frictions à traiter (`Sb_31.next.*`) avant ouverture nouveau cycle.
- [ ] ❌ **FAIL** — Lecture pas convaincante / pseudo-scientifique perçue. Rollback ou refonte composer (bump v=2).

**Justification (3-5 lignes) :**

> _à remplir_

## 6. Suivi post-dogfood

- [ ] Issue ouverte pour chaque friction `Sévérité ≥ med`.
- [ ] Closure Sx_31 mise à jour avec verdict dogfood (`Sx_31_CLOSURE_REPORT.md §11`).
- [ ] Sprint `Sb_31.next.*` priorisé selon les questions §4.
- [ ] Sx_32 / Sx_33+ débloqués si PASS strict.

---

**Rappel contractuel :**
- Dogfoods Sx_27 et Sx_30 restent indépendamment **PENDING**.
- Track parallèle **Body Signal Model** (`/body` Manual Profile via PR #15) reste indépendant de Body Intelligence v2.
- Sx_32 (PWA) / Sx_33+ (Health/API) restent bloqués sauf override séparé.
- OQ-E `Sb_30.next.placeholder` du cycle Sx_30 livrée 2026-06-27 — pas de dette overload UX restante.
