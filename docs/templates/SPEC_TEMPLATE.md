# Sx_NN — `<TITLE>` (SPEC ONLY)

> **Statut :** SPEC ONLY — aucun code livré à ce stade. Validation humaine explicite requise avant l'ouverture d'un Sb_NN.k correspondant. Voir `docs/strategy/SPEC_DRIVEN_ENGINEERING_PROTOCOL_v1.md`.

**Auteur :** `<nom + agent>` · **Date :** `YYYY-MM-DD` · **Version :** v1

---

## 1. Contexte

Pourquoi ce spec maintenant. Quel signal métier / opérationnel / risque l'a déclenché. État du repo + cycles précédents pertinents.

## 2. Objectif (un paragraphe + une liste max 7 items)

Ce que la spec couvre. Formulation en outcomes mesurables, pas en moyens.

## 3. Périmètre autorisé

Liste exhaustive des dossiers / modules / fichiers que les sprints Sb_NN.k pourront modifier. Tout le reste est par défaut **interdit**.

## 4. Périmètre interdit (Non-goals)

Liste explicite et verbatim de ce qui ne doit PAS être touché ou produit dans ce cycle. C'est la section que l'agent doit relire avant chaque commit. Format :

- Ne pas …
- Ne pas …
- Ne pas …

**Section obligatoire** : sans `Non-goals`, le spec ne peut pas être validé.

## 5. Hard contracts (verbatim)

Garanties non-négociables que tous les Sb_NN.k de ce cycle doivent préserver. Exemple : "Snapshots historiques restent sacrés", "scoring_version monotone", "ADD COLUMN ONLY". Format quote citable verbatim dans un sprint report.

## 6. Décomposition en lots (Sb_NN.1 → Sb_NN.k)

Max 8 lots. Pour chaque lot :

- **Sb_NN.1** — `<titre>` : objectifs · DoD spécifiques · périmètre · estimation effort (S/M/L).
- **Sb_NN.2** — …

## 7. Open questions (OQ-N)

Décisions ouvertes nécessitant tranchage humain. Chaque OQ avec :

- **OQ-N** : question · options · recommandation par défaut · qui tranche · délai.

Les OQ doivent être **tranchées** avant qu'un Sb_NN.k correspondant ne démarre. Si une OQ reste ouverte, le sprint dépendant est WAIT.

## 8. DoD globale du cycle

Critères mesurables à l'échelle du cycle Sx_NN complet (au-delà des DoD par sprint).

## 9. Risques

| Risque | Probabilité | Impact | Mitigation |
|---|---|---|---|
| | | | |

## 10. Fichiers / surfaces à inspecter avant tout build

Liste des chemins relatifs que l'agent doit relire (Read) avant d'écrire du code. Permet de prévenir le drift par méconnaissance.

## 11. Backlog post-cycle

Items volontairement reportés. Format :

- Item · Pourquoi reporté · Sprint cible (Sb_NN.next, Sb_(NN+1).0, etc.)

## 12. Verdict de la spec

- [ ] Section `Non-goals` présente
- [ ] Section `Hard contracts` présente
- [ ] Décomposition ≤ 8 lots
- [ ] OQ identifiées (ou liste vide explicitement)
- [ ] Pas de code livré, uniquement la spec

**Statut final :** `<DRAFT | READY FOR HUMAN REVIEW | VALIDATED>`

---

**Cf.** `docs/strategy/SPEC_DRIVEN_ENGINEERING_PROTOCOL_v1.md` · `docs/templates/BUILD_SPRINT_PROMPT_TEMPLATE.md`
