# SPIGNOS — Dogfooding Generalization Spec v1 (Sx_21)

**Date :** 2026-05-09
**Type :** SPEC ONLY — meta-spec d'élévation des retours dogfooding en chantiers système.
**Statut :** v1 draft, à valider avant ouverture des sprints aval Sx_22+.

---

## A. Pourquoi cette spec

Les passes de dogfooding successives (J+0 → J+N) génèrent une suite de retours terrain qui ont jusqu'ici été traités **comme des tickets locaux** :

- Sb_dogfood_fixpack v1 (`59a93ea`) — B1 wording, B2 textarea, B3 radar centre.
- Sb_catalog_v13 (`73ab0d0`) — C1 adductions, C2 Pull B tirage vertical.
- Sb_17 (`fffc282`) — F1 bodyweight merge.
- Sb_18 (`eda3512`) — F3 reco antagoniste/récup.
- Sb_19 (`c3693d9`) — F2 leaderboard drilldown.
- Sb_dogfood_fixpack v2 N6 (`2e4a823`) — CTA tile click restoration.

**Constat :** la même nature de retour revient. L'utilisateur signale "*adduction sans alternative*" alors que C1 a été codé. Il re-signale "*textarea blanc-sur-blanc*" alors que B2 couvre les 4 contextes. **La cause n'est plus le code manquant — c'est l'absence de modèle systémique** qui ferme la classe entière de problèmes.

Cette spec définit comment **généraliser** un retour de dogfooding au lieu de patcher au cas par cas.

## B. Audit des retours dogfooding à date

| # | Retour terrain | Nature primaire | Cause locale | Cause systémique | Décision cible | Sprint recommandé |
|---|---|---|---|---|---|---|
| **B1** | Bouton alt reco mal nommé | Lacune UX | Wording "{Template}" sans verbe | Contrat clic = action n'est pas explicite dans le DS | Audit CTA-wording cross-app | Sx_22 |
| **B2** | Textarea note blanc-sur-blanc | Bug réel | Style UA par défaut, dark theme partiel | DS sans token "form-control" garanti dark-theme | Cycle 1 — formaliser tokens form-control | Sx_22 |
| **B3** | Score dupliqué sur radar | Lacune UX | Hardcode score au centre + au-dessus | Pas de règle "un score = un emplacement" | Convention dataviz documentée | Sx_22 |
| **C1** | Adduction assise sans alternative | Lacune graphe substitution | 0 sub sur cet exercice | Graphe construit ad hoc, sans heuristique | **SUBSTITUTION_GAP_PACK_SPEC** | Sx_22 |
| **C2** | Pull B sans tirage vertical | Lacune graphe substitution | Idem | Idem | **SUBSTITUTION_GAP_PACK_SPEC** | Sx_22 |
| **F1** | Bodyweight séance invisible profil | Lacune synthèse analytics | 2 sources non mergées | Pas de spec d'unification des sources d'un signal | Cycle 2 — registres de signaux | Sx_23 |
| **F2** | Leaderboard sans drilldown | Lacune synthèse | Données dispos mais pas exposées | Pas de standard "résumé public d'un utilisateur" | **PROFILE_SYNTHESIS_SPEC v2** | Sx_22 |
| **F3** | Reco non plausible récup | Lacune modèle signal | Pas de notion d'antagoniste/récup | Modèle reco trop pauvre en variables physiologiques | Déjà traité Sb_18 — valider via télémétrie | Sx_24 |
| **N1** (dogfood j2) | Reco devrait expliquer "pourquoi maintenant" | Lacune UX + modèle | Phrase reco générique | Pas de narratif type "diagnosis" | Reco V3 — phrase narrative | Sx_24 |
| **N2** (dogfood j2) | Leaderboard hover + clic profil | Lacune synthèse | Hover livré Sb_19 mais pas mobile | Pas de pattern "preview-vs-clic" mobile/desktop | **PROFILE_SYNTHESIS_SPEC v2** | Sx_22 |
| **N3** (dogfood j2) | Textarea encore blanc-sur-blanc | Suspect régression / pas dans périmètre | Re-signalé après B2 | Soit user testait pré-deploy, soit cas hors B2 | À retester sur prod `2e4a823` | — |
| **N4** (dogfood j2) | Adduction encore sans subs | Re-signalé après C1 | Cf C1 | Cf C1 | À retester sur prod | — |
| **N5** (dogfood j2) | Pull B encore sans tirage vertical | Re-signalé après C2 | Cf C2 | Cf C2 | À retester sur prod | — |
| **N6** (dogfood j2) | CTA tile cassé après alt détails | Bug réel | Stacking context details | Pas de pattern "interactive disclosure safe" | Fixé `2e4a823` | — |
| **NEW-COACH** (dogfood j2) | Synthèse coach absente | Nouvelle feature | N/A | Pas de surface "coach view" | **COACH_REPORT_SPEC v1** | Sx_23 |

## C. Modèle de classification permanent

À adopter pour chaque future passe dogfood, chaque retour est classé :

1. **Bug réel** — comportement contraire au contrat documenté.
2. **Lacune UX** — comportement contractuel mais friction utilisateur.
3. **Lacune de recommandation** — sortie d'un service de calcul (reco, scoring, hint) jugée non pertinente.
4. **Lacune de graphe de substitution** — donnée manquante dans le catalogue / atlas.
5. **Lacune de synthèse analytics** — donnée présente mais mal exposée / pas agrégée.
6. **Lacune de modèle de signal** — le service ne possède pas la variable nécessaire pour produire le résultat attendu.

**Règle :** un retour n'est pas "fixé" tant que sa **classe** n'a pas été adressée. C1 corrige le cas adduction ; tant qu'une heuristique générale ne couvre pas les futurs trous similaires, la classe est ouverte.

## D. Critères de décision "patch local vs spec système"

| Critère | Patch local OK | Spec système requise |
|---------|----------------|----------------------|
| Nombre de retours similaires | 1 isolé | ≥ 2 du même type |
| Coût de patch unitaire | < 30 min | > 1 h ou récurrent |
| Risque de récurrence | nul (one-shot) | élevé (catalogue, DS, modèle) |
| Surface impactée | 1 fichier | ≥ 3 fichiers transverses |
| Demande ou non d'un coach/expert externe | non | oui (cf coach report) |

Si **2 critères "spec système" sont remplis → ouvrir une spec**. Sinon patch local + journal.

## E. Quatre chantiers ouverts par cette spec

| Sprint spec | Doc livré | Cible |
|---|---|---|
| Sx_22 — Substitution Gap Pack | `SPIGNOS_SUBSTITUTION_GAP_PACK_SPEC_v1.md` | Combler les 38+ trous du graphe substitution, formaliser heuristique zone/pattern/équipement. |
| Sx_22 — Profile Synthesis v2 | `SPIGNOS_PROFILE_SYNTHESIS_SPEC_v2.md` | Élever leaderboard+profile en synthèses lisibles, supprimer redondances dataviz. |
| Sx_23 — Coach Report | `SPIGNOS_COACH_REPORT_SPEC_v1.md` | Page `/coach-report` (SSR, exportable) — synthèse 2 min pour coach externe. |
| Sx_24 — Reco V3 narrative | (futur) | Reco avec phrase narrative "diagnosis" + télémétrie acceptance. |

## F. Garde-fous (v1.1)

- **Mesuré vs Inféré vs Non déductible** — chaque spec aval doit étiqueter ses sorties avec exactement l'un de ces trois tags. Aucun autre vocabulaire toléré. Le tag `Non déductible` est obligatoire dès qu'une donnée attendue par le user ne peut pas être produite par SPIGNOS (ex : VO2max, masse maigre, qualité d'exécution biomécanique).
- **Historique propre** — aucun chantier ne réécrit les sessions passées.
- **Mobile-first** — toute affordance hover desktop doit avoir un équivalent tap mobile.
- **Lotissement** — pas plus de 1 chantier de spec par semaine.
- **Re-test obligatoire** — chaque retour clos n'est validé qu'après re-test prod par l'utilisateur (cf N1-N5 re-signalés).

## G. Acceptance criteria Sx_21

- [x] Audit dogfooding consolidé (§B).
- [x] Modèle de classification adopté (§C).
- [x] Règle patch-vs-spec documentée (§D).
- [x] 3 specs aval ouvertes (§E).
- [x] Garde-fous (§F).

Sx_21 fournit la **méta-règle** que les sprints aval Sx_22+ doivent respecter.
