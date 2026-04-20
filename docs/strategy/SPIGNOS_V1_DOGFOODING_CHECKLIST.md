# SPIGNOS Session System V1 — Dogfooding Checklist

**Version :** v1 — 2026-04-20
**Cycle validé :** Sb_05 → Sb_10 + catalog v12
**Branche :** `claude/sprint-reporting-fitness-app-V7Qr6` @ commit `598fd38`
**Portée :** Session System V1 uniquement. G3 et chantiers V2 hors scope.
**Objectif :** passer en revue chaque surface produit en conditions réelles **avant merge**.

---

## Préparation

1. `alembic upgrade head` → appliquer migrations locales.
2. `uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`.
3. Se connecter en tant qu'utilisateur ayant **au moins 5 séances complétées** (dont 1 cardio + 1 strength) sur les 30 derniers jours. Créer 1-2 séances supplémentaires si besoin avant de démarrer la passe.
4. Tester sur viewport **375px large** (simulateur mobile) **et** desktop.

---

## Convention de résultat

Pour chaque scénario, reporter un résultat dans le tableau de synthèse final (§Résultats). Valeurs admises :

- **PASS** — comportement conforme à l'attendu.
- **FAIL** — symptôme d'échec observé.
- **N/A** — scénario non applicable (ex. pas d'historique pour tester un delta).
- **Notes** — texte libre très court pour consigner un détail utile (ex. « rendu OK mais gap visuel sur 320px »).

Règle : ne pas juger un scénario « en partie OK ». Soit il passe, soit il échoue. Les nuances vont dans Notes.

---

## Surface 1 — Home `/`

### Scénario 1.1 — Accueil avec séances mixtes sur 14j
- **Action :** ouvrir `/` après avoir complété ≥ 1 cardio + ≥ 1 strength dans les 14 derniers jours.
- **Attendu :** sparkline visible, dots orange (strength) + teal (cardio), **légende `Musculation · Cardio` visible** sous le sparkline (compacte, alignée à droite).
- **Symptôme d'échec :** légende absente alors que deux couleurs visibles, ou légende présente alors qu'une seule couleur.
- **Gravité KO :** moyenne.

### Scénario 1.2 — Accueil monochrome
- **Action :** sur un compte n'ayant fait que des séances strength sur 14j.
- **Attendu :** sparkline monochrome orange, **pas de légende** (évite le bruit visuel).
- **Symptôme d'échec :** légende présente alors que couleur unique.
- **Gravité KO :** faible.

### Scénario 1.3 — Séance en cours remontée
- **Action :** démarrer une séance sans la terminer, revenir sur `/`.
- **Attendu :** carte « Séance en cours » avec `open_since` lisible (ex. `12 min`).
- **Symptôme d'échec :** affichage UTC brut, ou carte absente.
- **Gravité KO :** haute.

---

## Surface 2 — Lancement de séance

### Scénario 2.1 — Ouvrir un template depuis `/library`
- **Action :** `/library` → cliquer sur un template (ex. Push A) → démarrer.
- **Attendu :** redirect vers `/sessions/{id}` en statut `in_progress`, première carte ouverte en position 1 (E1).
- **Symptôme d'échec :** ouverture sur une autre carte que E1, ou 404.
- **Gravité KO :** haute.

### Scénario 2.2 — Démarrage Pull A v12
- **Action :** démarrer Pull A.
- **Attendu :** **7 exercices** E1–E7 dans le DOM, dont E6 « Pullover machine » et E7 « Straight-arm pulldown câble ».
- **Symptôme d'échec :** seulement 5 exercices visibles (= catalog pas reseedé).
- **Gravité KO :** haute (preuve que v12 n'est pas chargé).

### Scénario 2.3 — Template LISS
- **Action :** démarrer `liss-abs` ou `liss-only`.
- **Attendu :** carte cardio, champs `cardio_duration_min` / `cardio_bpm_avg` / `cardio_machine_type` visibles dans le feedback.
- **Symptôme d'échec :** rendu comme une séance strength.
- **Gravité KO :** haute.

---

## Surface 3 — Flow des cartes

### Scénario 3.1 — Une seule carte active
- **Action :** ouvrir une séance en cours.
- **Attendu :** **exactement une** carte est ouverte (`<details open>`), les autres compactes avec `<summary>` visible (code, nom, progression).
- **Symptôme d'échec :** toutes les cartes ouvertes OU aucune.
- **Gravité KO :** haute.

### Scénario 3.2 — Jump bar 4 états
- **Action :** compléter E1, ouvrir E2 mais ne pas la terminer, laisser E3+ intactes, descendre vers le feedback.
- **Attendu :** jump bar en haut avec 4 états visibles : E1 = done (vert), E2 = active (accent), E3+ = future (dim), FB = feedback.
- **Symptôme d'échec :** tous les items au même style, ou état incohérent.
- **Gravité KO :** moyenne.

### Scénario 3.3 — Recap line sur carte done
- **Action :** compléter E1 avec 3×10 reps à 50 kg.
- **Attendu :** au collapse, `<summary>` de E1 affiche `50 / 50 / 50 kg · 10 / 10 / 10 reps`.
- **Symptôme d'échec :** recap absent ou incorrect.
- **Gravité KO :** moyenne.

### Scénario 3.4 — Scroll minimal en séance
- **Action :** sur viewport 375px, compléter successivement E1 → E2 → E3 via les boutons Suivant.
- **Attendu :** la carte active reste dans la zone visible sans scroll manuel après chaque Suivant (anchor `#exercise-{id}`).
- **Symptôme d'échec :** nécessité de scroller à chaque changement de carte.
- **Gravité KO :** haute.

---

## Surface 4 — Save / Précédent / Suivant

### Scénario 4.1 — Save-on-next
- **Action :** saisir 2 séries sur E2 (weight + reps), cliquer « Enregistrer et passer à E3 ».
- **Attendu :** redirect vers E3 active, **les deux séries saisies sur E2 sont persistées** (retour en arrière les montre toujours).
- **Symptôme d'échec :** données perdues, ou pas de redirect.
- **Gravité KO :** **critique**.

### Scénario 4.2 — Save-on-prev
- **Action :** sur E2, saisir une série, cliquer « ← E1 ».
- **Attendu :** redirect sur E1 active, donnée sur E2 persistée malgré le retour arrière.
- **Symptôme d'échec :** donnée E2 perdue.
- **Gravité KO :** **critique**.

### Scénario 4.3 — Bouton Précédent sur E1
- **Action :** carte E1 active (première).
- **Attendu :** **pas** de bouton « ← » (rien à précéder).
- **Symptôme d'échec :** bouton présent mais inerte, ou erreur au clic.
- **Gravité KO :** faible.

### Scénario 4.4 — Bouton Suivant sur dernier exo
- **Action :** dernière carte active, cliquer Suivant.
- **Attendu :** redirect vers `#session-feedback` (le bloc en bas de page), pas d'erreur.
- **Symptôme d'échec :** 500, redirect en boucle, ou aucun effet.
- **Gravité KO :** haute.

### Scénario 4.5 — Virgule dans un poids
- **Action :** saisir `52,5` dans un champ weight_kg.
- **Attendu :** valeur persistée comme `52.5`, affichée de façon cohérente au retour.
- **Symptôme d'échec :** rejeté, ou stocké comme `525`.
- **Gravité KO :** **critique** (Sb_06 étape 1).

---

## Surface 5 — Note séance

### Scénario 5.1 — Note séance repliée par défaut
- **Action :** ouvrir le bloc feedback séance d'une séance neuve.
- **Attendu :** `<details class="session-feedback__note">` **replié**, summary « Note séance (optionnel) » cliquable.
- **Symptôme d'échec :** textarea pleine hauteur visible d'emblée.
- **Gravité KO :** faible.

### Scénario 5.2 — Auto-ouverture si note existante
- **Action :** sur une séance avec une note déjà écrite, revenir plus tard.
- **Attendu :** `<details>` **ouvert** d'office, note lisible immédiatement.
- **Symptôme d'échec :** note cachée derrière le summary replié.
- **Gravité KO :** moyenne.

### Scénario 5.3 — Persistance POST
- **Action :** écrire 50 caractères dans la note, cliquer Enregistrer.
- **Attendu :** note persistée, visible après refresh.
- **Symptôme d'échec :** note perdue (refacto `<details>` aurait cassé le POST).
- **Gravité KO :** **critique**.

---

## Surface 6 — Substitution locale

### Scénario 6.1 — Drawer visible avant 1ʳᵉ série travail
- **Action :** sur une carte active d'un exercice avec substitutes (ex. Push A E2 Chest Press).
- **Attendu :** drawer `<details class="substitute-picker--drawer">` visible avec badge count « N alternatives ».
- **Symptôme d'échec :** drawer absent alors que substitutes définis dans le catalogue.
- **Gravité KO :** moyenne.

### Scénario 6.2 — Lock après 1ʳᵉ série
- **Action :** sur une carte avec substitutes, cocher « Fait » sur la première série travail avec weight + reps saisis. Recharger.
- **Attendu :** drawer disparu ; si une substitution avait été choisie, un badge « Substitué : … (prescrit : …) » reste visible.
- **Symptôme d'échec :** drawer encore visible (lock non appliqué).
- **Gravité KO :** haute (risque d'écraser un choix fait).

### Scénario 6.3 — Substitution persistée
- **Action :** choisir un substitut dans le drawer, cliquer Suivant, revenir sur la carte.
- **Attendu :** le nom substitué apparaît sur le `<summary>` et en en-tête du formulaire. `exercise_name_snapshot` (prévu) reste inchangé en base.
- **Symptôme d'échec :** retour au nom prévu, ou incohérence entre affichage et DB.
- **Gravité KO :** haute.

---

## Surface 7 — Atlas / info machine

### Scénario 7.1 — Panel `<details>` sur un exo lié
- **Action :** ouvrir E1 de Push A (Incline Smith Press, lié à l'atlas).
- **Attendu :** bloc `<details class="machine-panel">` visible avec icône `ⓘ`, replié par défaut ; à l'ouverture : 2-3 cues d'exécution, 2-4 erreurs fréquentes, note load_semantics.
- **Symptôme d'échec :** panel absent, ou contenu vide.
- **Gravité KO :** moyenne.

### Scénario 7.2 — Absence de panel sur un exo non lié
- **Action :** ouvrir un exercice du catalogue sans `machine_slug` (ex. un curl isolation).
- **Attendu :** **aucun** bloc machine-panel rendu sur cette carte.
- **Symptôme d'échec :** panel vide affiché à tort.
- **Gravité KO :** faible.

### Scénario 7.3 — Page `/science/atlas`
- **Action :** ouvrir `/science/atlas`.
- **Attendu :** TOC 8 familles cliquables, 29 machines listées avec cues + erreurs + charge + latéralité, version d'atlas affichée en bas.
- **Symptôme d'échec :** page vide, 404, ou familles manquantes.
- **Gravité KO :** moyenne.

### Scénario 7.4 — Lien depuis `/science`
- **Action :** sur `/science`, chercher la section « Atlas des machines ».
- **Attendu :** CTA `Ouvrir l'atlas →` qui renvoie vers `/science/atlas`.
- **Symptôme d'échec :** section absente, lien brisé.
- **Gravité KO :** faible.

---

## Surface 8 — Session detail (carte active enrichie)

### Scénario 8.1 — Hint Sb_08 A (charge +10%)
- **Action :** sur un exo avec historique (≥ 1 séance précédente avec 1ʳᵉ série complétée), saisir un poids **15% au-dessus** du prior sur la 1ʳᵉ série.
- **Attendu :** hint `💡 +15% de charge vs dernière fois — prudence sur l'exécution` visible **uniquement sur la carte active**.
- **Symptôme d'échec :** hint absent, ou visible sur cartes non actives.
- **Gravité KO :** moyenne.

### Scénario 8.2 — Hint Sb_08 B (reps réduites)
- **Action :** sur un exo avec historique ≥ 2 séries précédemment complétées, saisir `reps < prior - 3` sur la série 2.
- **Attendu :** hint `💡 Set 2 : reps réduites vs dernière fois — fatigue installée ?`.
- **Symptôme d'échec :** hint absent ou sur mauvais index.
- **Gravité KO :** faible.

### Scénario 8.3 — Delta vs dernière fois
- **Action :** avoir un historique sur l'exo, saisir une 1ʳᵉ série complétée.
- **Attendu :** ligne `Delta : +X kg · +Y reps · score en hausse/stable/baisse` visible au-dessus des inputs.
- **Symptôme d'échec :** delta absent ou figures incohérentes.
- **Gravité KO :** moyenne.

### Scénario 8.4 — Last-time
- **Action :** même condition que 8.3.
- **Attendu :** ligne `Dernière fois · il y a N jours · A / B / C kg · X / Y / Z reps`.
- **Symptôme d'échec :** date UTC brute, ou « aucune séance précédente » à tort.
- **Gravité KO :** haute.

### Scénario 8.5 — Note exercice repliée
- **Action :** ouvrir une carte active.
- **Attendu :** `<details class="exercise-card__note">` replié par défaut (summary « Note exercice (optionnel) »), ouvert si déjà rempli.
- **Symptôme d'échec :** textarea visible d'emblée.
- **Gravité KO :** faible.

---

## Surface 9 — `/done` (session review)

### Scénario 9.1 — Terminer une séance propre
- **Action :** compléter toutes les séries d'une séance strength, remplir feedback, cliquer « Terminer ».
- **Attendu :** redirect `/sessions/{id}/done` avec 4 blocs :
  - Résumé (work sets, bodyweight, concentration, état, **badge « Confiance du logging : eleve (≥80) »**)
  - **Top progression** (si historique et delta positif)
  - **Zones sollicitées** (top zones avec count de sets)
  - **À vérifier** (vide si séance propre)
- **Symptôme d'échec :** blocs manquants, badge absent, `/done` ne se charge pas.
- **Gravité KO :** haute.

### Scénario 9.2 — Déclencher une anomalie A
- **Action :** en cours de séance, cocher « Fait » sur une série **sans** saisir weight ni reps. Terminer.
- **Attendu :** bloc `À vérifier` contient `⚠ E{N} · Set #{i} marqué fait sans reps ni charge saisis`.
- **Symptôme d'échec :** anomalie absente.
- **Gravité KO :** moyenne.

### Scénario 9.3 — Confidence dégradée
- **Action :** répéter 9.2 sur 2 séries et terminer sans remplir concentration ni global_state.
- **Attendu :** badge de confiance passe à `moyen` ou `faible` selon le volume de bruit.
- **Symptôme d'échec :** badge reste à `eleve` malgré les anomalies.
- **Gravité KO :** moyenne.

### Scénario 9.4 — Recap de substitution
- **Action :** substituer E2 avant la 1ʳᵉ série, compléter, terminer.
- **Attendu :** sur `/done` bloc « Par exercice », ligne E2 affiche `→ {nom substitué}` et le compteur « Substitutions : 1 ».
- **Symptôme d'échec :** nom prévu encore affiché.
- **Gravité KO :** haute.

---

## Surface 10 — `/progress`

### Scénario 10.1 — Timeline qualité kind-aware
- **Action :** `/progress` avec séances strength + cardio sur 30j.
- **Attendu :** chart « Qualité de séance » avec dots orange/teal, **légende visible**.
- **Symptôme d'échec :** dots unicolores ou légende absente.
- **Gravité KO :** moyenne.

### Scénario 10.2 — Bodyweight chart
- **Action :** même page.
- **Attendu :** si bodyweight renseigné sur ≥ 2 séances, chart dédié avec plage mean±2σ.
- **Symptôme d'échec :** chart absent ou Y-axis incohérent.
- **Gravité KO :** faible.

---

## Surface 11 — `/profile`

### Scénario 11.1 — Timeline 30j + légende
- **Action :** `/profile`.
- **Attendu :** timeline qualité 30j avec légende kind (même pattern que `/progress`).
- **Symptôme d'échec :** légende absente.
- **Gravité KO :** faible.

### Scénario 11.2 — KPIs cohérents
- **Action :** même page.
- **Attendu :** `sessions_30d`, `streak_days`, tendance 30j vs 30j précédents cohérents avec l'historique.
- **Symptôme d'échec :** chiffres obsolètes ou faux.
- **Gravité KO :** moyenne.

---

## Surface 12 — Cardio vs strength

### Scénario 12.1 — Scoring cardio
- **Action :** terminer une LISS 25 min à 125 bpm avec abs complétés et feedback `high`/`good`.
- **Attendu :** quality_score proche de 100, visible sur `/done` et dans la timeline.
- **Symptôme d'échec :** score bas (< 70) → dispatcher ne route pas sur cardio.
- **Gravité KO :** **critique** (Sb_06 étape 3).

### Scénario 12.2 — Scoring strength inchangé
- **Action :** terminer un Push A complet avec success_score élevés.
- **Attendu :** quality_score ≥ 85, cohérent avec avant Sb_06.
- **Symptôme d'échec :** régression quantitative sur le calcul strength.
- **Gravité KO :** haute.

### Scénario 12.3 — Export v2
- **Action :** `curl http://127.0.0.1:8000/export/sessions.json | jq '.schema_version, .sessions[0] | {session_kind, quality_score, confidence_score, confidence_level}'`.
- **Attendu :** `schema_version: 2`, et les 4 champs présents avec des valeurs cohérentes.
- **Symptôme d'échec :** champ manquant ou schema_version incorrect.
- **Gravité KO :** moyenne (impact backup/restore).

---

## Go / No-Go — Merge de branche

Cocher après passe complète :

- [ ] Aucun scénario **critique** en KO (save-on-next, save-on-prev, virgule, persistance note, scoring cardio).
- [ ] Aucun scénario **haute gravité** en KO sur les surfaces 3, 4, 6, 8, 9.
- [ ] Full test suite verte localement : `pytest --ignore=tests/test_deploy_artifacts.py --ignore=tests/test_v1_acceptance.py -q`.
- [ ] `python scripts/catalog_qa.py` → PASS.
- [ ] `python scripts/machine_atlas_qa.py` → PASS.
- [ ] Les KO faibles identifiés sont listés pour suivi (pas bloquants).
- [ ] Branche à jour avec `main` (rebase ou merge OK, pas de conflit résiduel).
- [ ] Aucun secret ou fichier local (`.env`, DB) dans `git status`.

Si tout coché → **GO merge**.

---

## Go / No-Go — Déploiement prod

Cocher après merge :

- [ ] CI verte sur la PR fusionnée.
- [ ] Backup récent (< 24h) disponible : `python scripts/list_backups.py`.
- [ ] Point de rollback identifié (commit précédent la série V1, ex. avant `edd435e`).
- [ ] `alembic upgrade head` testé localement sur une copie de la DB prod (migration `20260418_add_machine_atlas_links.py` à appliquer).
- [ ] `scripts/smoke_deploy.sh` passe localement.
- [ ] Schema v2 de l'export validé sur un `curl /export/sessions.json` (prod ou staging) après déploiement : présence de `session_kind`, `quality_score`, `confidence_score`, `confidence_level`.
- [ ] Vérifier `/healthz/strict` retourne `status: "ok"` post-déploiement.
- [ ] Monitorer les 2 premières séances complétées en prod pour valider le flow carte active + save-on-next.

Si tout coché → **GO deploy**.

---

## Note terminale

Si un KO bloquant surface pendant la passe : **ne pas le corriger dans ce cycle**. Noter l'observation dans le fichier, revenir à une boucle Sb_XX ciblée avant de rouvrir le merge. G3 reste hors périmètre en V2 conformément à Sx_06 §1.6.

---

## Résultats — à remplir pendant la passe

### Tableau de synthèse

| Scénario | Surface | Gravité KO | Résultat | Notes |
|----------|---------|-----------|----------|-------|
| 1.1 | Home | moyenne | | |
| 1.2 | Home | faible | | |
| 1.3 | Home | haute | | |
| 2.1 | Lancement | haute | | |
| 2.2 | Lancement | haute | | |
| 2.3 | Lancement | haute | | |
| 3.1 | Flow cartes | haute | | |
| 3.2 | Flow cartes | moyenne | | |
| 3.3 | Flow cartes | moyenne | | |
| 3.4 | Flow cartes | haute | | |
| 4.1 | Save/Prev/Next | **critique** | | |
| 4.2 | Save/Prev/Next | **critique** | | |
| 4.3 | Save/Prev/Next | faible | | |
| 4.4 | Save/Prev/Next | haute | | |
| 4.5 | Save/Prev/Next | **critique** | | |
| 5.1 | Note séance | faible | | |
| 5.2 | Note séance | moyenne | | |
| 5.3 | Note séance | **critique** | | |
| 6.1 | Substitution | moyenne | | |
| 6.2 | Substitution | haute | | |
| 6.3 | Substitution | haute | | |
| 7.1 | Atlas | moyenne | | |
| 7.2 | Atlas | faible | | |
| 7.3 | Atlas | moyenne | | |
| 7.4 | Atlas | faible | | |
| 8.1 | Session detail | moyenne | | |
| 8.2 | Session detail | faible | | |
| 8.3 | Session detail | moyenne | | |
| 8.4 | Session detail | haute | | |
| 8.5 | Session detail | faible | | |
| 9.1 | /done | haute | | |
| 9.2 | /done | moyenne | | |
| 9.3 | /done | moyenne | | |
| 9.4 | /done | haute | | |
| 10.1 | /progress | moyenne | | |
| 10.2 | /progress | faible | | |
| 11.1 | /profile | faible | | |
| 11.2 | /profile | moyenne | | |
| 12.1 | Cardio/Strength | **critique** | | |
| 12.2 | Cardio/Strength | haute | | |
| 12.3 | Cardio/Strength | moyenne | | |

### Totaux

- Nombre de **FAIL critique** : …
- Nombre de **FAIL haute** : …
- Nombre de **FAIL moyenne** : …
- Nombre de **FAIL faible** : …
- Nombre de **N/A** : …

### Décision finale

Cocher une seule case :

- [ ] **GO merge** — 0 FAIL critique, 0 FAIL haute, QA/catalog/atlas OK, tests verts.
- [ ] **GO merge with low-priority follow-up** — 0 FAIL critique, 0 FAIL haute, mais ≥ 1 FAIL moyenne ou faible listés pour un Sb_11 ultérieur (non bloquant).
- [ ] **NO-GO** — ≥ 1 FAIL critique OU ≥ 1 FAIL haute. Action : ouvrir un mini sprint `Sb_11_session_v1_fixpack` ciblé avant toute reprise du merge.

**Observateur :** _________________
**Date :** _________________
**Commit testé :** _________________
