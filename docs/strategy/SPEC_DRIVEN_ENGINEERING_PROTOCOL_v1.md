# SPIGNOS — Spec-Driven Engineering Protocol v1

**Auteur :** opérateur SPIGNOS + Claude Code (Opus 4.7).
**Date :** 2026-06-14 (formalisation Sb_26.5).
**Statut :** verrouille la méthodologie spec-driven du projet à partir du cycle Sx_27. Les cycles Sx_20 → Sx_26 ont été menés selon ce protocole de facto ; ce document le formalise pour empêcher le drift sur les cycles futurs.

---

## 1. Pourquoi ce protocole

SPIGNOS est développé par un opérateur humain seul avec un agent (Claude Code) sur un cadence intense. Sans discipline explicite :

- l'agent **code** au lieu de specifier (drift vers la satisfaction immédiate)
- les **non-goals** se perdent entre conversations
- les **hard contracts** s'oublient à la 4ème itération
- les **sprints** s'élargissent sans tranchage explicite
- les **DoD** se relâchent quand "ça marche en local"
- les **amendements** réécrivent l'historique au lieu d'ajouter du contexte

Le protocole impose une séparation **rigide** entre `spec` et `build`, des templates verrouillés, et des gates automatisables (cf. `scripts/check_spec_protocol.py`).

## 2. Vocabulaire

| Terme | Définition |
|---|---|
| `Sx_NN` | **Spec sprint** — produit UNIQUEMENT des documents (spec, amendements). AUCUN code livré. Numéroté par cycle. |
| `Sb_NN.k` | **Build sprint** — implémente un lot précis du `Sx_NN` parent. Numéroté `k = 1..8`. |
| `Sb_NN.next.<topic>-N` | Sprint additionnel hors cycle initial, ouvert post-livraison (cleanup, polish, fix incrémental). |
| `Hard contract` | Garantie verbatim non-négociable d'un `Sx_NN` que tous les `Sb_NN.k` doivent préserver. |
| `OQ-N` | **Open question** — décision ouverte dans un `Sx_NN`, doit être tranchée avant l'ouverture du `Sb_NN.k` dépendant. |
| `Non-goals` | Liste explicite et verbatim de ce qu'un sprint ne doit PAS toucher / produire. |
| `Amendment §Nbis` | Modification d'une spec validée. Ajoute une section, ne réécrit pas l'originale. |
| `Verdict` | Décision finale écrite à la fin d'un sprint report : ✅ Sb_NN.k+1 PRÊT ou ⏳ attendre. |

## 3. Cycle complet (spec → build → review → dogfood)

```
   ┌──────────────┐         ┌──────────────────┐     ┌────────────┐
   │  Brainstorm  │ ──────▶ │  Sx_NN (SPEC)    │ ──▶ │   HUMAN    │
   │  / signal    │         │  no code         │     │   REVIEW   │
   └──────────────┘         │  templates §1..12│     └─────┬──────┘
                            └──────────────────┘           │
                                                ┌──────────▼─────────┐
                                                │ VALIDATED ?        │
                                                └────┬───────────────┘
                                                     │ yes (verbatim "GO")
                            ┌────────────────────────▼────────────┐
                            │  Sb_NN.1 (BUILD)                    │
                            │  - reprend non-goals + hard contracts│
                            │  - livre code + tests + sprint report │
                            └────────────────────────┬────────────┘
                                                     │ ✅ verdict
                            ┌────────────────────────▼────────────┐
                            │  HUMAN GO/NO-GO REVIEW              │
                            │  template GO_NO_GO_REVIEW_TEMPLATE  │
                            └────────────────────────┬────────────┘
                                                     │ GO
                            ┌────────────────────────▼────────────┐
                            │  Sb_NN.2 .. Sb_NN.k                 │
                            └────────────────────────┬────────────┘
                                                     │
                            ┌────────────────────────▼────────────┐
                            │  DOGFOOD                            │
                            │  template DOGFOOD_REPORT_TEMPLATE   │
                            │  produit signal pour Sx_(NN+1)      │
                            └─────────────────────────────────────┘
```

## 4. Règle d'or — SPEC ONLY ≠ BUILD

Un `Sx_NN` ne livre **jamais** :

- ❌ pas de code
- ❌ pas de migration
- ❌ pas de modification de fichier sous `app/`
- ❌ pas de modification de CI
- ❌ pas de nouveau test

Il livre **uniquement** :

- ✅ `docs/strategy/Sx_NN_<TITLE>.md` (spec)
- ✅ amendements d'autres specs si nécessaire (`§Nbis`)
- ✅ mise à jour `docs/strategy/SPEC_REGISTRY.md`

Si pendant un `Sx_NN` la spec révèle un besoin urgent de code (ex: un bug critique découvert), c'est **un autre sprint** (`Sb_NN.next.urgent-fix-N`) ouvert séparément après validation humaine.

## 5. Critères GO / WAIT pour ouvrir un `Sb_NN.k`

L'utilisateur ne dit "GO" qu'après vérification explicite que :

1. Le `Sx_NN` parent est validé (statut `VALIDATED` dans `SPEC_REGISTRY.md`).
2. Toutes les `OQ-N` impactant ce lot sont **tranchées**.
3. Les hard contracts du `Sx_NN` ont été lus.
4. Les non-goals ont été lus.
5. Le `Sb_NN.k-1` précédent est livré ET la GO/NO-GO review humaine est faite.
6. Le sprint précédent a un verdict ✅ PRÊT dans son report.

Si UN seul de ces critères manque → **WAIT**, pas de GO.

## 6. Format de prompt d'ouverture d'un `Sb_NN.k`

Reprendre **mot pour mot** la structure de `docs/templates/BUILD_SPRINT_PROMPT_TEMPLATE.md` :

- Contexte (état des sprints livrés + run CI + ruff budget)
- Objectif
- Périmètre autorisé
- Périmètre interdit (**verbatim** des non-goals du Sx_NN parent + spécifiques au lot)
- Hard contracts (**verbatim**)
- Livrables attendus
- Tests attendus
- DoD (incluant toutes les gates Sb_26.1 → 26.4+)
- Rollback
- OQ à trancher

Un prompt qui manque l'un de ces blocs **invite l'agent à drifter**.

## 7. Discipline en cours de sprint

### 7.1 Citation de la spec dans le code non trivial

Tout fichier nouveau ou modification non triviale doit porter un commentaire `Sb_NN.k —` ou `Sx_NN §N` au sommet du bloc, citant la spec. Sert à :

- répondre à un `git blame` futur ("pourquoi ce code ?") en un coup
- détecter le code orphelin (pas de spec → soit le code est mort, soit la spec a été oubliée)

Exemple :

```python
# Sb_26.4 — Per-IP rate limiter for sensitive public auth endpoints.
# In-memory single-process buckets, see docs/SECURITY_BASELINE.md §2.
```

### 7.2 Ne pas toucher aux non-goals

Si pendant l'implémentation l'agent identifie qu'un non-goal est en fait nécessaire :

1. **Arrêter immédiatement.**
2. Documenter le besoin dans un commentaire dans le sprint report (§ "Limites").
3. Proposer un `Sb_NN.next.<topic>` à l'utilisateur.
4. Ne **PAS** étendre le sprint en cours pour le couvrir.

### 7.3 Sprint report obligatoire

Aucun sprint ne se termine sans `docs/SPRINT_Sb_NN_k_REPORT.md`. Ce fichier est l'**artefact de revue** principal — il doit suivre `SPRINT_REPORT_TEMPLATE.md`. Section `## 11. Verdict` (ou équivalente) obligatoire.

### 7.4 Pas de code mort

Si un sprint livre une feature flag, un kill switch, ou un wiring conditionnel : la spec doit le justifier. Sinon, le pattern `Don't add features beyond what the task requires` s'applique.

## 8. Gestion des amendements

Une spec `Sx_NN` validée n'est **jamais réécrite**. Si une décision change :

1. Ouvrir un sprint `Sb_NN.next.amend-§N`.
2. Utiliser `AMENDMENT_TEMPLATE.md` pour créer une section `§Nbis` dans la spec.
3. Marquer la section originale comme `✅ TRANCHÉE <date>` → `§Nbis`.
4. Si l'amendement crée de nouveaux hard contracts, les versionner `HC-<DOMAIN>-<N>`.
5. Reflétez l'amendement dans `SPEC_REGISTRY.md`.

L'historique de décision est ainsi traçable : on voit la trajectoire, pas une réécriture.

## 9. Dogfooding

Après une livraison de cycle complet (`Sx_NN` + tous ses `Sb_NN.k`), faire au moins une session d'usage réelle, et la documenter selon `DOGFOOD_REPORT_TEMPLATE.md`. Les frictions deviennent l'input du prochain `Sx_NN+1`.

Pas de dogfood report ⇒ pas de cycle suivant. C'est le mécanisme principal anti-`build for the sake of building`.

## 10. Rôles

### 10.1 Architecte humain (utilisateur)

- décide quand un cycle s'ouvre (signal métier ou friction dogfood)
- valide les `Sx_NN`
- tranche les OQ-N
- dit GO ou WAIT après chaque `Sb_NN.k`
- est seul à pouvoir invoquer `git push --force`, `git revert`, ou réviser un hard contract

### 10.2 Agent Claude Code

- propose un `Sx_NN` ou un `Sb_NN.k` à partir d'un signal
- ne livre **jamais** du code dans un `Sx_NN`
- respecte verbatim les non-goals + hard contracts d'un `Sb_NN.k`
- arrête au premier signal de scope creep et propose un sprint séparé
- produit un sprint report complet avec verdict

### 10.3 SuperPower / skills

- ne contournent **jamais** la règle SPEC ONLY ≠ BUILD
- ne fusionnent **jamais** deux sprints sans validation humaine explicite
- ne réécrivent **jamais** une spec validée (utilisent amendement §Nbis)

## 11. Format de décision finale (verdict)

Tout sprint report finit par UN ET UN SEUL marqueur :

- `### ✅ Sb_NN.k+1 PRÊT` — le sprint suivant peut être ouvert
- `### ⏳ ATTENDRE — <raison>` — conditions de levée explicites

Pas de verdict ⇒ sprint **non clos**, même si le code est mergé.

## 12. Lotissement max 8 lots par cycle

Un `Sx_NN` ne peut pas planifier plus de 8 `Sb_NN.k`. Au-delà, le cycle est trop large : il doit être **scindé** en `Sx_NN` + `Sx_NN+1`.

Justification : 8 sprints × ~1 journée chacun = 1-2 semaines de build, période au-delà de laquelle le contexte humain dérive (frictions oubliées, priorités changées).

Les `Sb_NN.next.<topic>` ne comptent **pas** dans cette limite (sprints additionnels post-cycle).

## 13. Gates automatisables

Le script `scripts/check_spec_protocol.py` vérifie de manière conservative :

- tout `docs/SPRINT_Sb_*_REPORT.md` contient un marqueur de verdict
- tout `docs/strategy/Sx_*` contient une section non-goals (ou `Périmètre interdit` ou `Non-goals`)
- les 6 templates `docs/templates/*.md` existent
- `docs/strategy/SPEC_REGISTRY.md` existe

Allowlist explicite pour fichiers historiques pré-Sb_26.5 (cf. `.spec-protocol-allowlist.json`). La gate ne fait **aucune** analyse sémantique du texte — uniquement présence de marqueurs robustes.

## 14. Limites du protocole v1

- Pas de validation NLP de la cohérence spec ↔ code
- Pas d'auto-link spec ↔ commits (Sb_26.next.spec-traceability-1 candidat)
- Pas de gate sur le `git log` (commit messages libres tant que la convention `feat(sb_NN_k): ...` est suivie)
- Pas de mécanisme d'enforcement automatique du verdict (humain valide à la lecture)

Ces limites sont **acceptables V1** : le protocole optimise la discipline humaine, pas l'automation totale.

## 15. Évolution

Tout changement au protocole passe par un sprint dédié `Sb_26.next.protocol-v2` (ou ultérieur) qui livre :

- un nouveau `SPEC_DRIVEN_ENGINEERING_PROTOCOL_v2.md`
- une note de migration v1 → v2
- mise à jour des templates
- mise à jour de `check_spec_protocol.py`

Ce document v1 reste l'autorité tant que v2 n'est pas validé.
