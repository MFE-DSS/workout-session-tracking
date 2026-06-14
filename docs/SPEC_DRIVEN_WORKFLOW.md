# SPIGNOS — Spec-Driven Workflow (Operator Guide)

**Audience :** opérateur SPIGNOS (humain) qui pilote Claude Code.
**Date :** 2026-06-14 (Sb_26.5).
**Référence :** `docs/strategy/SPEC_DRIVEN_ENGINEERING_PROTOCOL_v1.md` (le protocole formel) — **ce document est le mode d'emploi pratique**.

---

## 1. Cinq prompts que tu dois savoir écrire

| Type | Quand l'utiliser | Template |
|---|---|---|
| **Spec** | nouveau besoin / cycle | `docs/templates/SPEC_TEMPLATE.md` |
| **Build** | un lot Sb_NN.k à livrer | `docs/templates/BUILD_SPRINT_PROMPT_TEMPLATE.md` |
| **Review** | sprint livré, décider GO/WAIT | `docs/templates/GO_NO_GO_REVIEW_TEMPLATE.md` |
| **Correction** | un sprint a dérivé, recadrer | (cf. §6) |
| **Dogfood** | après livraison d'un cycle complet | `docs/templates/DOGFOOD_REPORT_TEMPLATE.md` |

## 2. Prompt **Spec** — quand tu ouvres un cycle

Format à coller :

```text
Tu travailles dans le repo MFE-DSS/workout-session-tracking.

Objectif : produire le sprint de spécification Sx_NN — <TITRE>.

Contraintes dures :
- SPEC ONLY : tu ne livres AUCUN code.
- Tu produis uniquement docs/strategy/Sx_NN_<TITRE>.md + éventuellement
  amendements §Nbis d'autres specs.
- Tu suis docs/templates/SPEC_TEMPLATE.md verbatim — toutes les sections.
- Tu listes explicitement les Non-goals et les Hard contracts.
- Tu décomposes en max 8 lots Sb_NN.k.
- Tu identifies les OQ-N à trancher avant tout build.

Contexte produit :
- <quel signal métier / friction dogfood / risque opérationnel a déclenché ce cycle>
- <quels cycles Sx_* précédents sont concernés>
- <quels hard contracts existants doivent être préservés>

Périmètre à couvrir :
- <surfaces métier ou technique à toucher>
- <fichiers à inspecter en amont>

Périmètre interdit (non-goals candidats — à raffiner) :
- <liste verbatim>
```

**Ce que tu obtiens :** un fichier `Sx_NN_<TITRE>.md`. Tu le lis, tu tranches les OQ-N que l'agent te pose, tu marques `VALIDATED` dans `SPEC_REGISTRY.md`. **À ce stade aucun code n'a été touché.**

## 3. Prompt **Build** — quand tu ouvres un lot

Format à coller (copier `BUILD_SPRINT_PROMPT_TEMPLATE.md`, remplir TOUS les blocs) :

```text
GO Sb_NN.k — <TITRE>.

Contexte :
<rappel sprints livrés + run CI vert + ruff budget courant>

Objectif Sb_NN.k :
<paragraphe + liste des objectifs concrets, MIROIR EXACT de la décomposition Sx_NN §k>

Périmètre autorisé :
<liste exhaustive>

Périmètre interdit :
<verbatim non-goals du Sx_NN parent + spécifiques lot>

Hard contracts (verbatim — non négociables) :
<verbatim hard contracts Sx_NN parent>

Livrables attendus :
<liste explicite>

DoD :
<checklist incluant toutes les gates Sb_26.1 → 26.4>

Verdict final attendu :
✅ Sb_NN.k+1 PRÊT ou ⏳ attendre.
```

**Règle d'or :** si tu omets un bloc, l'agent va drifter. Le template est un anti-drift contractuel.

## 4. Prompt **Review** — quand un sprint est livré

```text
Sb_NN.k vient d'être livré. CI run #NNNNNNNNNN.

Avant que je dise GO pour Sb_NN.k+1, fais une review honnête en suivant
docs/templates/GO_NO_GO_REVIEW_TEMPLATE.md.

Vérifie spécifiquement :
- aucun fichier hors périmètre autorisé n'a été touché
- les non-goals verbatim ont été respectés
- les hard contracts n'ont pas été violés
- le sprint report est complet et le verdict cohérent avec le diff
- aucun secret commité
- aucune gate CI désactivée

Sortie : GO, WAIT ou REVERT, avec raisons explicites.
```

Si l'agent dit WAIT, tu lis les raisons et tu décides :
- corriger maintenant → prompt **Correction** (cf. §6)
- backloguer → ajouter au `SPEC_REGISTRY.md` comme `Sb_NN.next.<topic>`
- ignorer (assume) → documenter dans le sprint report en cours

## 5. Quand dire GO

Tu ne dis **GO** que si **toutes** ces conditions sont vraies :

- [ ] Le sprint précédent a un verdict ✅ PRÊT
- [ ] CI réelle verte sur les 3 jobs
- [ ] Diff lu : aucun fichier hors périmètre
- [ ] Sprint report cohérent (pas de "Verdict : ✅" alors que le diff dit autre chose)
- [ ] Hard contracts du Sx_NN parent : tu en as cité au moins un de tête et confirmé non-violation
- [ ] Les OQ-N éventuelles du prochain sprint sont tranchées dans ton chat
- [ ] Tu te sens reposé (pas de GO à 2h du matin sur un sprint complexe)

## 6. Quand dire WAIT

Cas typiques :
- diff montre une modification non autorisée (un fichier `app/services/` métier touché alors que `Non-goals` l'interdisait)
- la CI a une gate qui flap (gitleaks faux positif non documenté)
- l'agent a écrit le sprint report avant les tests verts
- une OQ-N a été tranchée par l'agent sans validation humaine
- tu identifies un risque non documenté dans le sprint report
- ton intuition dit "trop vite, trop large"

Format de prompt :

```text
WAIT sur Sb_NN.k. Raisons :
1. <raison 1 — verbatim>
2. <raison 2>
3. <raison 3>

Condition de levée :
- <chose 1 à faire>
- <chose 2>

Ne touche pas au code en cours. Ouvre Sb_NN.next.<correction-topic>
quand je dirai GO sur la correction.
```

## 7. Prompt **Correction** — quand un sprint a dérivé

Cas : tu as mergé Sb_NN.k mais en relisant tu vois qu'un fichier a été touché qui ne devait pas l'être. Tu ne dois **pas** ré-écrire l'histoire — tu ouvres un correctif :

```text
GO Sb_NN.k.fix — <correction concise>.

Contexte :
Sb_NN.k a été mergé (CI #NNN). En review post-merge, j'ai vu que <fichier>
a été modifié alors qu'il était dans Non-goals.

Objectif :
- revert la modification non autorisée
- documenter dans le sprint report Sb_NN.k qu'un fix a été appliqué
- ajouter une ligne dans SPEC_REGISTRY.md

Périmètre autorisé : <fichier à revert + le sprint report + registry>
Périmètre interdit : tout le reste (pas de re-design, pas d'extension).
```

## 8. Comment éviter le scope creep

| Pattern de dérive | Réponse |
|---|---|
| Agent propose "tant qu'on y est on pourrait aussi…" | "Non. Reporté en `Sb_NN.next.<topic>`." |
| Agent dit "j'ai vu un bug, je le corrige" | "Documente-le dans le sprint report §Limites. Ouvre `Sb_NN.next.bugfix-N` si critique." |
| Agent commence à refactor pour "faire propre" | "Pas dans ce sprint. Le code peut rester laid si la fonction marche." |
| Agent veut bumper une dépendance "au passage" | "Non. Dependabot s'en occupe. Si urgent, sprint séparé `Sb_26.next.deps-bump-N`." |
| Agent réécrit une spec validée | "Interdit. Amendement §Nbis via AMENDMENT_TEMPLATE.md." |

## 9. Comment forcer l'agent à NE PAS coder

Pour les sprints SPEC ONLY (Sx_NN), répète littéralement :

> SPEC ONLY. AUCUN code. AUCUNE modification de fichier sous `app/`, `tests/`,
> `migrations/`, `scripts/` non documentaire. Si tu identifies un besoin de
> code, mentionne-le dans la spec comme `Sb_NN.k` ou backlog — ne le code pas.

Si l'agent commence à écrire du code, interromps tout de suite :

> Stop. Tu es en SPEC ONLY. Reviens à la rédaction de docs/strategy/Sx_NN_<TITRE>.md.

## 10. Comment exiger un sprint report

À la fin de chaque sprint, vérifie que :

1. `docs/SPRINT_Sb_NN_k_REPORT.md` existe
2. Il suit `SPRINT_REPORT_TEMPLATE.md` (sections : Résumé, Périmètre livré, Tests, Sécurité, CI réelle, Risques, Contraintes respectées, Limites, Backlog, Verdict)
3. La section Verdict contient un marqueur (`✅ PRÊT` ou `⏳ ATTENDRE`)
4. `SPEC_REGISTRY.md` est mis à jour avec le nouveau sprint
5. `scripts/check_spec_protocol.py` retourne exit 0 (la gate CI le fait automatiquement à partir de Sb_26.5)

Si l'un de ces points manque :

> Le sprint Sb_NN.k n'est pas clos tant que :
> - le sprint report est produit
> - le registry est à jour
> - check_spec_protocol passe
> Pas de GO pour Sb_NN.k+1 avant.

## 11. Cas spéciaux

### 11.1 Un sprint dérive massivement

Tu peux dire **REVERT** :

```text
REVERT Sb_NN.k. La dérive est trop large pour être corrigée en place.

git revert <merge-sha>
git push

Ouvre Sb_NN.k-bis avec :
- périmètre re-resserré : <liste plus stricte>
- non-goals additionnels : <liste>
- aucun héritage du code reverté

Documente dans SPEC_REGISTRY.md la ligne Sb_NN.k comme ❌ abandonné.
```

### 11.2 Une OQ-N n'est pas tranchable seul

Tu peux ouvrir un sprint dédié à la décision :

```text
SPEC ONLY — Sb_NN.next.amend-OQ-N.

Objectif : trancher OQ-N de Sx_NN.

Suis docs/templates/AMENDMENT_TEMPLATE.md. Présente-moi les options,
ta recommandation par défaut, et la justification. Ne tranche pas
toi-même ; je te dirai GO sur l'une des options.
```

### 11.3 Le dogfood révèle un blocker

```text
Dogfood report : voir docs/<...>_DOGFOOD_REPORT.md.

Le friction #1 est <description>. C'est un blocker.

Ouvre Sb_NN.next.<topic> avec scope minimal pour résoudre uniquement
cette friction. Pas de refactor associé. Documente la trace dans
SPEC_REGISTRY.md.
```

## 12. Anti-patterns à NE jamais faire

- ❌ Dire "GO continue" sans lire le diff
- ❌ Laisser l'agent fusionner deux sprints "pour gagner du temps"
- ❌ Demander un sprint sans hard contracts explicites
- ❌ Approuver un sprint dont le report n'est pas livré
- ❌ Réécrire une spec validée au lieu d'un amendement
- ❌ Ouvrir un Sx_NN+1 sans dogfood du cycle précédent
- ❌ Ignorer un WAIT et dire GO "parce qu'on est pressé"

Chacun de ces anti-patterns ouvre la porte au drift. La discipline V1 = ne céder sur aucun.
