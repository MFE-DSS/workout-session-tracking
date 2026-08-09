# Sb_ASSET_04.2 — Muscle Focus Enrichment P1 (SPEC)

**Programme :** `Sx_ASSET` (Auren) — sous-cycle Muscle Focus · **Amont :** `Sb_ASSET_04.1-P0` (runtime `/science`, CLOSED / DELIVERED, PR #49 `ae10737`)
**Type :** enrichissement visuel/produit · **Tier attendu :** `isolated`/`shared_code` (template + CSS ; **pas** de migration/modèle/score)
**Statut :** 🟢 **SPEC — NOT YET BUILT** (build sur GO séparé)

> **Classification du dogfood (opérateur) :** `MAJOR NEXT-ITERATION`. **Ni dette mineure, ni rejet** de la fondation. La fondation technique P0 est acceptée ; P1 monte la **valeur perçue** sans toucher aux contrats d'anatomie.

---

## 1. Problem statement

Le P0 a livré une fondation runtime **techniquement correcte** : 3 plaques P0 (chest / shoulders / posterior) rendues **SSR / no-JS** sur `/science`, byte-exact, attribution BodyParts3D CC BY 4.0 visible, disclaimers non médicaux, toggle épaules face/dos accessible, zéro overflow 360 px. Martin a **accepté la fondation** — mais le rendu **produit** n'atteint pas encore la valeur perçue attendue : les planches paraissent **« pas assez avancées / pas assez grandes »**, les libellés fins (« quel chef est sollicité ») sont **« micro », illisibles**, et la hiérarchie éducative autour des plaques est trop plate pour un onglet « premium ». Le besoin exprimé est **« un vrai upgrade visuel »**, pas un ajustement cosmétique.

P1 doit **augmenter la lisibilité, la hiérarchie et la valeur pédagogique** de la surface Muscle Focus **sans** produire de nouvelle anatomie, sans réécrire de géométrie, et sans introduire de claim interdit.

## 2. Dogfood observations (verdict réel Martin, 2026-08-07)

- **Direction artistique** : intéressante, à conserver.
- **Mobile** : « bon début, continuer » — hiérarchie mobile à renforcer.
- **Taille / présence des plaques** : « pas assez avancées / grandes » — les figures manquent de présence sur desktop.
- **Micro-libellés** : les noms de faisceaux / provenance (« quel chef sollicité ») sont **illisibles** (trop petits, noyés dans la caption).
- **Attente** : **upgrade visuel réel**, perçu comme un saut de valeur — classé **enrichissement majeur de prochaine itération**.
- **Non négociable** : la fondation (SSR/no-JS, plaques byte-exact, provenance, non médical) **reste acceptée** — on **construit dessus**, on ne la refait pas.

## 3. Visual / product goals

1. **Lisibilité** : les libellés de faisceaux / provenance deviennent **lisibles** (taille, contraste AA, séparation de la caption).
2. **Présence** : les plaques gagnent en **échelle et cadrage** perçus sur desktop, sans déformer la géométrie (mise en page, pas réécriture SVG).
3. **Hiérarchie éducative** : chaque région porte une **carte de synthèse** claire (nom, ce que la plaque montre, exercices liés déjà présents dans l'EKB/`/science`) au lieu d'une seule caption dense.
4. **Divulgation progressive honnête** : un bloc **« ce que ceci montre / ce que ceci ne montre pas »** par région — renforce la posture non médicale et l'honnêteté (aucun claim d'activation).
5. **Rythme mobile/desktop** : cartes/onglets/espacement donnant un rythme visuel « premium », responsive, **no-JS d'abord**.

## 4. Non-goals

- **Aucune nouvelle région / nouvelle plaque anatomique** (les 5 régions restantes + N3 fibres/insertions/mechanics restent **P2+**).
- **Aucune illustration générée** ni overlay « médical-like ».
- **Aucune réécriture de géométrie** des 3 SVG P0 (freeze sha `7a4167ea` / `5eb7bedf` / `b84c8bce` conservés).
- **Aucun** changement de route / modèle / score / migration.
- **Aucun** claim d'activation / EMG / recrutement / % — voir §5.
- **Aucune** revendication de validation anatomique / juridique / médicale professionnelle.

## 5. Hard guardrails (verrouillés)

| Garde-fou | Règle |
|---|---|
| Pas de % d'activation | Aucun pourcentage d'activation musculaire affiché ou impliqué |
| Pas de claim EMG | Aucune référence à l'électromyographie / mesure d'activité |
| Pas de % de recrutement | Aucun pourcentage de recrutement de fibres/faisceaux |
| Non médical | Langage éducatif / biomécanique seulement ; disclaimers conservés |
| Provenance BodyParts3D | Attribution **CC BY 4.0 visible** préservée sur chaque plaque |
| Pas d'anatomie finale IA | `ai_usage: NONE` pour toute géométrie/anatomie finale |
| Contrat additif uniquement | Évolution des contrats de plaque / descripteur **additive** (jamais de rupture) |
| SSR / no-JS préféré | Rendu serveur d'abord ; JS **optionnel et progressif** seulement si strictement nécessaire, jamais requis pour l'info |
| Pas de réécriture géométrie | Sauf autorisation **explicite** séparée |
| Pas de score/modèle/migration | Sauf approbation **séparée** |

## 6. Image-reference policy

- Toute image fournie par l'utilisateur est traitée **uniquement comme référence visuelle** : direction artistique, inspiration de layout, **preuve de dogfood**, critère d'acceptation.
- **Aucun asset image volumineux n'est committé** sans autorisation explicite. Décrire l'image dans la spec (direction / inspiration / evidence) plutôt que la stocker.
- Si un stockage de références s'avère nécessaire → **proposer d'abord une décision `docs/assets` séparée** (budget, provenance, licence), jamais un commit d'asset ad hoc.
- Rappel : les 3 SVG P0 restent la **seule** source graphique de la surface ; P1 ne produit pas de nouveau graphisme anatomique.

## 7. Options / Risques / Choix retenu (CLAUDE.md §3)

| Option | Contenu | Risque | Verdict |
|---|---|---|---|
| **A** — Captions & hiérarchie éducative seulement | Réécrire captions, séparer provenance, tailles lisibles | Trop léger seul → perçu « minor debt » (contredit la classification MAJOR) | **Partiel** (nécessaire, insuffisant seul) |
| **B** — Layout / cartes / rythme visuel sur `/science` | Grille responsive, présence des plaques, espacement, hiérarchie mobile/desktop | Toucher `app.css` partagé = blast radius CSS | **RETENU** (cœur du saut de valeur perçue) |
| **C** — Cartes de synthèse par région reliées aux 3 plaques | Une carte/région (nom, ce que ça montre, exercices liés) | Doit rester factuelle (pas de claim) | **RETENU** |
| **D** — Divulgation progressive « ce que ça montre / ne montre pas » | `<details>` no-JS par région | Rédaction honnête à cadrer | **RETENU** |
| **E** — Nouvelles régions / nouvelles plaques | Produire 5 régions restantes / N3 | Production anatomique gatée (revue humaine + provenance) — hors P1 | **REJETÉ (→ P2+)** |
| **F** — Illustrations générées / overlays médical-like | IA / overlays d'activité | Viole garde-fous (IA anatomie, non médical, activation) | **INTERDIT** |

**Choix retenu : B + C + D + A** (un P1 **petit mais à fort gain de valeur perçue**), **sans E ni F**. On améliore layout, cartes explicatives, sémantique de région, hiérarchie mobile/desktop et lisibilité — **sans nouvelle anatomie, sans claim, sans réécriture géométrique**.

## 8. Recommended P1 scope

**Un seul build, template + CSS, no-JS.**

1. **Lisibilité (A)** : sortir les libellés de faisceaux/provenance de la caption dense → typographie lisible, contraste AA (garde `Sb_UI_09.3` réutilisée), micro-texte supprimé.
2. **Présence & rythme (B)** : grille responsive pour les 3 régions ; plaques agrandies par la **mise en page** (conteneur/`max-width`/cadrage CSS — **jamais** le `viewBox`) ; rythme premium mobile (empilé) / desktop (grille) ; zéro overflow 360 px conservé.
3. **Cartes de synthèse par région (C)** : chaque région (chest / shoulders / posterior) = une carte avec **nom**, **une phrase « ce que la plaque montre »**, et **les exercices déjà reliés** (réutiliser la donnée `/science` existante, aucune nouvelle source).
4. **Divulgation progressive (D)** : par région, un `<details>` **« ce que ceci montre / ce que ceci ne montre pas »** (rappel honnête : géométrie éducative, **pas** une mesure d'activation), no-JS.

**Explicitement exclu de P1** : nouvelles plaques/régions (E), génération/overlays (F), tout claim activation/EMG/recrutement/score.

## 9. Files likely touchable in a future patch (indicatif, NON modifié ici)

- `app/templates/_partials/muscle_focus.html` — structure cartes / captions / `<details>` (additif).
- `app/templates/science.html` — hiérarchie de la section `#section-muscle-focus` (additif).
- `app/static/css/app.css` — bloc scopé `.muscle-focus` (layout/typo/rythme ; tokens Auren Terminal, **zéro nouvelle couleur**).
- `tests/test_auren_muscle_focus_runtime.py` — nouveaux tests SSR (voir §11).
- Les 3 SVG `_partials/muscle_focus_plate_*.svg` : **inchangés** (référencés, jamais réécrits).

*(Ce document ne modifie aucun de ces fichiers — il les recense pour le build P1 à venir.)*

## 10. Acceptance criteria

- **AC1 — Lisibilité** : les libellés de faisceaux/provenance sont lisibles (taille ≥ corps de texte de la surface, contraste ≥ AA) ; plus aucun micro-texte illisible.
- **AC2 — Présence/rythme** : sur desktop, les 3 régions forment une grille lisible avec des plaques de présence accrue ; sur mobile 360 px, empilement propre, **`scrollWidth === clientWidth`** (zéro overflow horizontal).
- **AC3 — Cartes de synthèse** : chaque région porte nom + phrase « ce que ça montre » + exercices liés (issus de la donnée existante).
- **AC4 — Divulgation honnête** : chaque région expose un bloc « ce que ça montre / ne montre pas » (no-JS, `<details>`), sans aucun claim d'activation.
- **AC5 — Garde-fous** : zéro % activation/recrutement, zéro EMG, non médical, attribution BodyParts3D visible, `ai_usage: NONE`, aucun `viewBox`/géométrie SVG modifié, aucun changement route/modèle/score/migration.
- **AC6 — No-JS** : toute l'information est disponible sans JavaScript ; fallback silhouette décorative préservé.
- **AC7 — Non-régression** : les tests SSR P0 existants restent verts, réorientés seulement si un contrat de présentation change **intentionnellement** (jamais affaiblis).

## 11. Test strategy

- **SSR runtime** (`test_auren_muscle_focus_runtime.py`, additif) : présence des cartes de synthèse par région ; libellés lisibles rendus dans le HTML initial (no-JS) ; blocs `<details>` « montre / ne montre pas » présents ; attribution + disclaimers toujours rendus ; **assertions non tautologiques** (leçon `python:S9073` / nit Gitar 04.1 : asserter l'état exact, jamais `X or 'y' in w`).
- **Garde anti-claim** : test négatif vérifiant l'**absence** des termes interdits (`%`, `activation`, `EMG`, `recruitment`, `recrutement`) dans la section rendue.
- **Overflow 360 px** : vérif serveur/HTML de la structure responsive (le test visuel réel reste au dogfood).
- **Guards d'immutabilité** : les 3 SVG et leurs sha restent référencés/inchangés (le guard existant `test_auren_muscle_focus_plates.py` couvre déjà les plaques).
- **Non-régression** : broad sweep ciblé `/science` + Muscle Focus.

## 12. Explicit out-of-scope (P1 ne fait PAS)

- Nouvelles régions / nouvelles plaques anatomiques (5 restantes, N3 fibres/insertions/mechanics) → **P2+**.
- Partition du chest (plaque entière conservée) → différée.
- Toute génération d'image / overlay médical-like / IA anatomie.
- Tout claim d'activation, EMG, recrutement, pourcentage.
- Toute réécriture de géométrie SVG (`viewBox`, chemins).
- Tout changement de route, modèle, score, migration, EKB.
- Toute revue anatomique / juridique / médicale professionnelle (non revendiquée).
- Toute décision de stockage d'assets images (relève d'une décision `docs/assets` séparée, §6).
- Publication / Vortex / AGENTS.md / design source — hors périmètre.

---

**Verdict :** 🟢 **Sb_ASSET_04.2 — SPEC RECORDED / BUILD NOT AUTHORIZED.** P1 = enrichissement **template + CSS, no-JS**, à fort gain de valeur perçue (layout + cartes de synthèse + divulgation progressive + lisibilité), **sans nouvelle anatomie, sans claim, sans réécriture géométrique**. Build sur `GO BUILD — Sb_ASSET_04.2` séparé. **Périmètre interdit** : §4 non-goals + §5 garde-fous + §12 out-of-scope.
