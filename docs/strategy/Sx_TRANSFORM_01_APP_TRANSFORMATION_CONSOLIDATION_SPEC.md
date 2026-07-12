# Sx_TRANSFORM_01 — App Transformation Consolidation (Master Doc)

**Type** : SPEC / STRATEGY — docs-only, **aucun code**.
**Date** : 2026-07-11
**Statut** : 🟢 SPEC LIVRÉE — READY FOR HUMAN DECISION
**Option retenue** : **A** — document maître unique ; les documents sources restent en place.
**Audit associé** : [`../SPRINT_Sx_TRANSFORM_01_APP_TRANSFORMATION_CORPUS_AUDIT_REPORT.md`](../SPRINT_Sx_TRANSFORM_01_APP_TRANSFORMATION_CORPUS_AUDIT_REPORT.md)

> **Rôle de ce document** : source de vérité **consolidée** de la transformation
> produit. Il **ne remplace pas** les documents sources (roadmap UI, specs Auren,
> benchmarks, brainstorms) — il les **synthétise, réaligne et tranche les
> contradictions** pour être directement exploitable. En cas de divergence entre
> un ancien document et celui-ci, **ce document prime** pour la direction ; les
> contrats de gouvernance versionnés (CLAUDE.md, `.check-policy.json`) priment sur
> tout.

---

## 0. Étape 0 — Brainstorming / Options / Risques / Choix retenu

### Options comparées

| Option | Description | Verdict |
|---|---|---|
| **A** | **Document maître de consolidation** (les sources restent) | ✅ **RETENU** |
| B | Réécrire les documents un par un | ❌ trop large ; risque de perte d'historique |
| C | Créer directement une roadmap build | ❌ prématuré sans consolidation (peut être une **sortie** de A — voir §6) |
| D | Ne rien faire | ❌ rejeté (vocabulaire dispersé, contradictions) |

### 15 sujets clivants tranchés

| # | Sujet | Décision |
|---|---|---|
| 1 | Plusieurs docs ou un maître ? | **Un maître** (ce document) ; sources conservées comme références. |
| 2 | Renommer « Auren » ou garder « SPIGNOS » ? | **Les deux, séparés** : SPIGNOS = nom historique/repo/domaine fonctionnel ; Auren = direction produit/UI. **Pas de rebrand code** hors sprint dédié (`Sx_UI_10`). |
| 3 | Contradiction white clinical ↔ Auren Terminal ? | **Déjà résolue** (Sx_UI_02 → **Sx_UI_02b**, 2026-07-07, livré). Auren Terminal (dark/mono/amber) est l'identité **active**. White clinical = inspiration de calme, **pas** palette active. |
| 4 | React Native / React comme horizon ? | **Encadré hors repo actuel** : la gouvernance **interdit** React/SPA/bundler dans le repo. PWA-first ; natif seulement si l'usage le justifie, **jamais** dans ce repo. |
| 5 | Hiérarchie finale ? | **Mode séance › Home › cohérence charge/substitution › Body Intelligence (zones) › Progress/Physique › PWA › Rebrand.** |
| 6 | Éviter que BI re-densifie l'app ? | **Pas de widget Home V1** ; BI vit sur sa page ; Home reste décisionnelle légère (acquis Sx_UI_06). |
| 7 | Intégrer « silence plutôt que faux poids » ? | **Principe informationnel actif** (issu de Sx_DOGFOOD_01) — voir §5. |
| 8 | Intégrer « pas de score opaque » ? | **Principe actif** pour BI (issu de Sx_BI_01) : zone cards traçables, pas de note globale opaque en premier — voir §5. |
| 9 | Principes figés vs ouverts ? | Figés/ouverts explicités en §3 et §9 (repris de la roadmap UI + Sx_UI_02b). |
| 10 | Anciens docs = archives / références / actifs ? | **Références actives** (non archivées, non réécrites) ; ce maître est la porte d'entrée. |
| 11 | Rendre la roadmap exploitable par Claude/Superpower ? | Ce document + la table `ROADMAP_AND_NEXT_STEPS.md` = point d'entrée unique ; principes formulés en règles actionnables (§5) et interdits (§8). |
| 12 | Passages « interdits » ? | React/SPA/bundler, big-bang redesign, claims médicaux, dashboard trop dense, 2e accent, mutation métier en sprint UI, nouveau score opaque — voir §8. |
| 13 | Passages « principes actifs » ? | SSR/Jinja, mobile-first, no-JS fallback, une décision par écran, confidence visible, non-médical explicite, silence plutôt que faux poids — voir §5. |
| 14 | Articuler Auren Terminal ↔ activation BI ? | BI zone cards **héritent** des tokens Auren Terminal (graphite/mono/amber, un seul accent) ; pas de nouvelle couleur ; confidence en badge sobre — voir §4 + §5. |
| 15 | Prochain build après dogfooding ? | Séquence recommandée §6 : dogfooding Sx_DOGFOOD_01 → décision Sx_BI_01 (faite) → deploy si terrain OK → `Sb_BI_01.1` zone cards → transformation shell/progress si nécessaire. |

### Risques / parades

| Risque | Parade |
|---|---|
| Le maître fige une contradiction déjà résolue | §7 documente les résolutions **comme des amendements datés**, pas des débats ouverts |
| Vocabulaire re-dispersé | §1 fixe SPIGNOS vs Auren une fois pour toutes |
| Réintroduire React « en horizon » | §8 le classe **interdit repo** ; §4 le cadre PWA-first |
| BI re-densifie l'app | §5 (« ne pas re-densifier la home ») + §6 (pas de widget Home V1) |

---

## 1. Décision de marque provisoire

- **SPIGNOS** = **nom historique / repo / domaine fonctionnel**. Reste dans le code,
  les services, migrations, modèles, tests, config, systemd, DNS. **Aucun renommage
  code** dans un sprint non dédié.
- **Auren** = **direction produit / UI actuelle** (face marketing/produit). Choisi
  parmi les finalistes brainstorm (Teral / Nerva / **Auren**). **Pas encore dans le
  code** — réservé à `Sx_UI_10_rebrand_migration_spec`, **après** stabilisation du
  langage visuel.
- **Auren Terminal** = **codename de l'identité visuelle** (voir §2).
- **« Spinos »** = **n'existe pas** dans le corpus (variante fantôme) ; ne pas
  l'introduire.
- **Pas de rebrand complet sans sprint dédié** (`Sx_UI_10`, exécuté d'un bloc,
  jamais par touches successives, uniquement après validation de `Sx_UI_04`).

---

## 2. Direction visuelle active

- **Auren Terminal** — **dark / mono / amber**, identité **primaire** (pas une option).
- Surfaces : **graphite dense** (`#0A0C0F` → `#1B2029`).
- Typographie : **tout-mono** (terminal) — texte ET chiffres, une seule famille
  monospace système.
- Accent : **ambre readout `#C8A24B`** — **un seul accent** (action primaire / état
  actif). Aucune 2e couleur d'accent sans amendement `Sx_UI_02bis` explicite.
- **Pas de retour automatique au white clinical.** Le « Clinical Lab clair » (Sx_UI_02
  initial) a été **révisé** par **Sx_UI_02b** (2026-07-07) et **livré** (Home + Focus +
  Shell cohérents graphite/mono/amber, closeout accepté).
- **White clinical conservé comme inspiration de calme** (espacement, retenue, zéro
  décoratif) — **pas comme palette active**.

---

## 3. Garde-fous architecture (figés)

- **FastAPI SSR + Jinja2** — conservé.
- **No React** dans le repo. **No SPA / no bundler applicatif.**
- **No-JS fallback** préservé ; **JS vanilla progressive enhancement uniquement**
  (pattern `Sx_29`).
- **PWA progressive possible** (`Sx_UI_08`) — installabilité + offline **ciblé sur la
  séance active**, **pas** une réécriture native.
- **Aucune mutation métier en sprint UI** : un sprint UI ne modifie jamais
  `scoring/`, `substitution.py`, `coach_report.py`, `body_intelligence.py`,
  `overload_engine.py`, `overload_inputs.py`, `overload_explainer.py`,
  `recommendation.py`.
- **Aucune migration Alembic** dans un cycle UI.
- **Screenshot regression** (`Sx_UI_11`) = baseline obligatoire avant toute refonte
  visuelle large.
- **Tap targets 44×44** conservés/étendus.

---

## 4. Priorités produit

Ordre souverain (réaligné avec les sprints livrés) :

1. **Mode séance souverain** — le meilleur point d'appui du produit ; re-skin Auren
   Terminal livré (Sx_UI_04 / Sb_UI_02b.2). Toute évolution respecte « une décision
   par écran ».
2. **Home décisionnelle légère** — dé-densifiée (Sx_UI_06.3) ; CTA de reco en tête ;
   **ne pas re-densifier**.
3. **Cohérence charge / substitution** — « silence plutôt que faux poids » (Sx_DOGFOOD_01,
   CLOSED) ; placeholders cible compacts mobile (Sb_DOGFOOD_01.3).
4. **Body Intelligence par zones traçables** — angle **Zone Intelligence Cards**
   (Sx_BI_01, ACCEPTED) ; hérite des tokens Auren Terminal ; **pas de 2e score opaque**.
5. **Progress / Physique** — lecture calme ensuite ; décision produit sur le score
   A/B/C opaque de `/physique` à cadrer (`Sb_BI_01.next`).
6. **PWA** (`Sx_UI_08`) puis **Rebrand** (`Sx_UI_10`) — tardifs.

---

## 5. Principes informationnels (actifs)

Règles **actionnables** appliquées à tout sprint produit/UI :

1. **Une décision principale par écran** (one action per screen).
2. **Silence plutôt que faux poids** — jamais une donnée non comparable ; état vide
   existant (« Non disponible ») plutôt qu'une valeur trompeuse (Sx_DOGFOOD_01).
3. **Pas de score opaque en premier** — chiffres traçables et sourcés avant toute
   note synthétique ; pour BI, zone cards avant radar/score global (Sx_BI_01).
4. **Confidence visible** — badge sobre (élevée / moyenne / faible) ; statut
   `insufficient_data` assumé.
5. **Non-médical explicite** — aucun diagnostic / composition / posture ; wording
   `FORBIDDEN_WORDING` conservé ; `DEFAULT_LIMITS` affichés.
6. **Ne pas re-densifier la home** — acquis Sx_UI_06 protégé.
7. **Un seul accent** — pas de signal couleur concurrent.
8. **Placeholder = indication légère** — jamais `value=`, jamais préremplissage
   (Sx_DOGFOOD_01.3).

---

## 6. Roadmap recommandée

Séquence exploitable (chaque étape sur GO explicite ; aucune ouverte d'office) :

1. **Dogfooding terrain Sx_DOGFOOD_01** — checklist §7 du closeout (pending).
2. **Décision humaine Sx_BI_01** — **faite** (Option A, Zone Intelligence Cards, ACCEPTED).
3. **Deploy** si le terrain confirme la cohérence (GO explicite, jamais compte prod).
4. **`Sb_BI_01.1` Zone Intelligence Cards** — build BI par zones (dépend d'un mapping
   propre : voir note corpus ci-dessous).
5. **Transformation shell / progress** si nécessaire (`Sx_UI_07`) — lecture calme.
6. **PWA** (`Sx_UI_08`) puis **Rebrand** (`Sx_UI_10`).

> **Note corpus (dépendance `Sb_BI_01.1`)** : un audit read-only a montré que le
> mapping exercice→zone couvre déjà **11/11 zones en primaire, 0 exercice
> « unknown »** (65 noms distincts, 87 lignes `ExerciseMuscleMapping` backfillées).
> Les gaps sont sur les **zones secondaires** (seules biceps/triceps peuplées comme
> secondaires) et les **stabilisateurs / muscles fins** (volontairement vides,
> OQ-32). Un « corpus improvement » n'est donc **pas un préalable bloquant** aux
> zone cards V1 (le socle primaire suffit) — il reste une amélioration possible
> **après**, sur GO séparé.

---

## 7. Contradictions résolues

| Contradiction | Résolution (datée) |
|---|---|
| White clinical vs Auren Terminal | **Sx_UI_02 → Sx_UI_02b** (2026-07-07) : dark/mono/amber devient l'identité ; teal retiré ; **livré** (closeout accepté). |
| React Native future vs React interdit repo | Gouvernance : **React/SPA/bundler interdits dans le repo** ; PWA-first ; natif hors repo, seulement si l'usage le justifie. |
| Dashboard riche vs app minimaliste | **App minimaliste** ; une décision par écran ; pas de cockpit dense ; Home dé-densifiée (Sx_UI_06). |
| Score global opaque vs zone cards | **Zone cards traçables d'abord** (Sx_BI_01) ; le score A/B/C de `/physique` n'est pas dupliqué ; sa décision produit est reportée (`Sb_BI_01.next`). |
| BI flag-off vs `/physique` live | Constat acté : composer `/body/intelligence` **flag-off** ; `/physique` **live** avec score opaque. La reprise BI = zone cards sur `/body/intelligence`, sans réveiller un 2e score. |

---

## 8. Non-goals (interdits actifs)

Ce sprint : **pas de code**, pas de UI build, pas de rebrand complet, pas de deploy,
pas de release tag, pas de React, pas de claims médicaux, pas de nouveau score.

Interdits **permanents** portés par la transformation (rappel) :
- **React / SPA / bundler / dépendance front lourde** — hors repo.
- **Big-bang redesign** — transformation par sprints ciblés + screenshot regression.
- **Claims médicaux / diagnostic corporel.**
- **Dashboard trop dense / re-densification de la home.**
- **2e couleur d'accent** sans amendement explicite.
- **Mutation métier en sprint UI** (scoring/substitution/overload/BI/reco).
- **Nouveau score opaque** (BI = zone cards traçables).

---

## 9. Principes figés vs ouverts (synthèse)

**Figés (verrouillés)** : SSR/Jinja2 · no-JS fallback · no React/SPA/bundler · JS
vanilla progressive enhancement · tap targets 44×44 · un seul accent · Auren Terminal
dark/mono/amber = identité · aucune mutation métier en sprint UI · aucune migration
Alembic en cycle UI · screenshot regression avant refonte large · rebrand uniquement
`Sx_UI_10` post-`Sx_UI_04`.

**Ouverts (à trancher au sprint concerné)** : validation finale de l'accent ambre
(dogfood) · densité compact vs intermédiaire · toggle clair futur éventuel · ordre
final de la bottom nav (`Sx_UI_03`) · outillage screenshot (`Sx_UI_11`) · périmètre
offline PWA (`Sx_UI_08`) · disponibilité domaine/marque « Auren » (pré-gate `Sx_UI_01`) ·
décision produit sur le score `/physique` (`Sb_BI_01.next`) · corpus improvement
(zones secondaires / stabilisateurs) sur GO séparé.

---

## 10. Verdict

**Verdict :** 🟢 **Sx_TRANSFORM_01 App Transformation Consolidation — SPEC LIVRÉE, READY FOR HUMAN DECISION.**

Le corpus de transformation est **consolidé en un document maître unique** (Option A)
sans réécrire ni archiver les sources. Vocabulaire fixé (**SPIGNOS** repo / **Auren**
produit / **Auren Terminal** identité ; « Spinos » inexistant). Direction visuelle
active **Auren Terminal (dark/mono/amber)** — la contradiction white clinical est
**déjà résolue** (Sx_UI_02b livré). Architecture figée (**SSR/Jinja, no React**,
no-JS fallback, PWA-first). Priorités réalignées (**mode séance › Home › cohérence
charge › BI zones › Progress › PWA › Rebrand**) et principes informationnels rendus
**actionnables** (silence plutôt que faux poids, pas de score opaque, confidence
visible, non-médical, une décision par écran, ne pas re-densifier). Contradictions
tranchées (§7), interdits explicités (§8). Aucun code, aucun rebrand, aucun deploy.
Prochaine décision : GO (ou ajustement) ; puis reprise de la séquence roadmap (§6).
