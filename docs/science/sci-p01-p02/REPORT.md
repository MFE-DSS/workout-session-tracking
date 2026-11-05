# Rapport SCI-P01 / SCI-P02 — contrats isolés

**Point de reprise courant : [reçu final de livraison](DELIVERY_RECEIPT.md).** Les états « en cours au moment de la préparation » ci-dessous sont historiques ; le reçu final porte les vérifications postérieures.

5 novembre 2026. Branche `spec/sci-p01-p02-blueprint-first-plan`, base 90da846. Réalisation autorisée après revue du design : « Valider les contrats et tests isolés ». Pas de moteur servi, de nouvelle règle de prescription, d'UI ou de migration.

## Brainstorming / Options / Risques / Choix retenu

Envelopper directement le planificateur historique masquerait ses baselines et l'absence de temps utilisateur. Réécrire l'orchestration serait hors périmètre. Choix retenu : audit + DTO/JSON Schemas/fixtures/tests isolés, en distinguant disponibilité de données, de politique et de compatibilité. Les artefacts ne sont importés par aucun module app/. Le module ne choisit pas d'exercice ni ne génère une prescription ; il valide la forme et la cohérence d'un échange proposé.

## Audit et décisions

18 gabarits,107 fiches scientifiques/84 identités canoniques, taxonomies11/15 zones et deux familles de générateurs repérées. La chaîne hebdomadaire est réellement servie sur le web ; elle reste inchangée. Probes purs : cadence 1/2/3/4 avec familles inconnues →24/48/72/96 séries physiques, statuts historiques partial. Baselines par zone total 148, distinct des séries physiques. Aucun de ces nombres ne devient une dose recommandée.

Le manifeste est identique au blob reçu dans la PR mobile #353 à 2ba9fd4, absent de la base canonique ; copie explicitement tracée. Les sources d'ancrage incluent ACSM 2026, dose-réponse volume/fréquence, split/full-body, effort et repos. Les limites de lecture (notamment texte intégral ACSM inaccessible) sont explicites ; aucune revue systématique complète ou validation prédictive anthropométrique revendiquée.

Revue de construction : trois clarifications réglées dans le design (politique nullable/priorité de statuts ; profil d'inputs séparé de la dose ; impossibilité démontrée distincte de l'inconnu). Les décisions restantes avant un moteur sont dans HANDOFF.md ; elles n'empêchent pas le paquet isolé demandé.

## Validation locale

check_scope : ISOLATED ; pas de full sweep local. Premiers tests rouges sur absence du module, puis sur fausses compatibilités, sources de conflits identiques, prior de population présenté comme fait personnel, date future, moteur absent, exposition inconnue/exacte et durée sans modèle. Corrections ciblées puis tests verts.

À cette passe : **43 tests de contrat**, inclus dans **341 tests ciblés et de voisinage passants** (44,02 s), avec deux avertissements de dépréciation de dépendances. Ruff nouveau code propre ; budget **264 ≤ 548** ; protocole et OpenSpec strict **5/5** passants. Les trois JSON Schemas correspondent à l'export des DTO et les huit fixtures se valident avec les références du dépôt. Les tests READY utilisent seulement une autorité synthétique, aucune politique réelle promue.

La revue indépendante finale a relevé deux problèmes importants, sans critique ni mineur : une confirmation disponible pouvait masquer un refus dans le même contexte ; la provenance de l'équipement et des confirmations était insuffisamment contrainte. Huit cas de régression ont d'abord échoué (35 autres passants), puis les deux corrections ont été appliquées en une passe. La vérification finale de 341 tests inclut ces huit cas. Une contradiction ne devient plus une compatibilité confirmée ; une disponibilité connue exige une source personnelle/contextuelle explicite.

Le diff hors manifeste est sans erreur d’espacement. Les doubles espaces du manifeste sont ses sauts de ligne Markdown d’origine, conservés pour maintenir une copie byte-identique à la source opérateur. Les empreintes du manifest ont été vérifiées.

Publication réalisée via la [PR #354](https://github.com/MFE-DSS/workout-session-tracking/pull/354), HEAD `da3986617699296744aee9bb986da6f05393c6ea`, merge par commit `9120efc44cd14f7a14c955499780a1bc14aae71f`. Le relevé détaillé ci-dessous distingue validation de PR et suivi canonique. Aucun test mobile/visuel nouveau requis localement puisqu'aucune surface ni consommateur produit ne change ; la CI existante reste applicable selon son déclenchement.

## État servi et limites

Les contrats sont proposés et vérifiables, non servis. Pas de snapshot Blueprint persistant, de premier plan produit, d'estimation de durée validée ou de fixture READY issue d'un vrai moteur. Le module n'authentifie pas et ne certifie pas la vérité scientifique des données qu'un producteur de confiance lui fournit. Aucune mutation de app/, clients/, data/, schémas backend partagés, DB ou tokens.

Le handoff donne versions, champs, inconnus, table de dépendances, producteurs/consommateurs, compatibilité et breaking changes. Les prochaines tâches nécessitent un change scientifique/API dédié ; aucun GO BUILD de moteur ou déploiement ne se déduit du présent paquet.

## Publication et reçu post-merge

- [CI du HEAD final de #354](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/42079203279) : **9 jobs réussis**, dont les quatre contrôles requis ; trois shards totalisant **7 200 passants / 3 ignorés**. Aucun dispatch récupéré ni rebase. PR MERGEABLE, aucun thread/revue bloquant, base restée 90da846. `mergeStateStatus` brut **UNSTABLE**, dû seulement au check Sonar consultatif ci-dessous ; aucun bypass.
- Sonar PR : job Actions réussi et check « SonarCloud Code Analysis » **failure**, gate **ERROR**. **7 code smells MAJOR dans les tests** : S9073 (assertion composite) et six S5778 (préparation/plusieurs appels dans une assertion d'exception). Aucun nouveau bug, vulnérabilité ou hotspot ; coverage exposée **93,8 %**, `new_coverage` absent pour cette PR. Ces sept remarques restent ouvertes ; ni faux vert ni résolution automatique. GOV-SONAR-01 les rend consultatives.
- Référence Sonar avant merge, révision exacte 90da846 : coverage 93,8 %, new_coverage 93,95215767305095 %, 440 smells, 8 bugs, 6 vulnérabilités, 0 hotspot, gate ERROR. Ce relevé ne constitue pas une nouvelle confirmation de faille ni un audit de ces constats historiques. Les nombres de branche et de PR n'ont pas le même périmètre ; ils ne sont pas soustraits pour fabriquer un delta.
- [CI canonique du merge 9120efc](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/42081554961) : en cours **au moment de la préparation du présent reçu**. Attestation WOULD_REUSE de l'arbre `239c11916add`, mais mécanisme en SHADOW MODE : les shards sont réellement rejoués. Le verdict final et le relevé Sonar canonique doivent être vérifiés avant fusion de la PR de clôture et consignés dans son reçu de livraison.
- Contrôles locaux de clôture : check_scope DOCS, check_spec_protocol passant, OpenSpec strict 5/5, diff sans erreur ; aucun sweep local relancé.
- Archive préparée **après** le merge principal : `openspec/changes/archive/2026-11-05-science-blueprint-first-plan/`, trois exigences synchronisées sans changement dans `openspec/specs/science/blueprint-first-plan/spec.md`. Le Purpose précise le périmètre non servi ; aucune règle de prescription ajoutée. Cette clôture documentaire passe par sa propre PR et les gates réellement déclenchées, sans les élargir ni les affaiblir.

Les travaux mobiles (#353), worktrees étrangers, preuves appareil et identifiants QA sont préservés. Le nettoyage concerne uniquement les branches/worktree de cette tranche sans travail unique, après clôture vérifiée. Aucun moteur, endpoint, déploiement ou nouveau GO BUILD n'est déduit de l'archive.

## Rulings et suites

Trois précisions de construction sont retenues : politique nullable/statuts ordonnés ; profil d'inputs versionné séparé de la dose ; impossibilité démontrée distincte de l'inconnu. La revue finale ajoute la provenance contextuelle stricte et la résolution obligatoire d'un refus contradictoire. Aucun mineur issu de la revue indépendante n'est différé ; les sept remarques Sonar sur la structure des tests restent explicitement ouvertes.

Le prochain livrable recommandé reste **SCI-P02-INITIAL-POLICY** (HANDOFF.md, D02/D03/D04) : admission d'archétypes, dose/effort initial et modèle de temps, avec incertitude matérielle et vraie fixture READY du producteur. L'intégration API/mobile et la politique des données ont leurs propres décisions et périmètres. Le critical path mobile complet reste ouvert.
