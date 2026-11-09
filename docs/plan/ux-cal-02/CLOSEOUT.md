# UX-CAL-02 — closeout contrôlé en cours

9 novembre 2026 — Europe/Paris. **CODE_MERGED / CODE_CANONICAL_VERIFIED / NOT_ACTIVATED.**
La préparation n'est pas une déclaration de livraison finale.

Le GO BUILD/G1 puis les vrais pixels ont été explicitement acceptés avant commit
UI. [DELIVERY](DELIVERY.md) consigne HEAD6d46e3e, PR393 et CI42689201348
SUCCESS11jobs sans retry (8068backend/3skip, 73suites/913mobile+TS, 77visuels), readiness sans revue/thread bloquant et merge gardé
`c7215623e9806a8a7ce12590f5b5e7c099fc3128` sur base3bb1f2d. SonarPR OK,
0issue, coverageapp92,5% (pas mesure TypeScript). CI canonique code [42692021095](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/42692021095) completed/success11jobs, mêmes comptes effectivement rejoués.
Sonar canonique : ERROR consultatif ; analyse `887f02a9-747f-4be9-bdc0-241341f1c48b`, révision exacte c721562, 9 novembre20:34:56 UTC : 8bugs / 549smells / 8entrées vulnérabilité externe / 0hotspot ; coverageapp92,5%, nouvelle92,5048%. Même dette que la base3bb1f2d ; aucune mesure TypeScript ni innocuité globale déduite.
Closeout publié et cleanup restent PENDING ; aucun succès futur anticipé.

## Archive et suivi

Après merge code, `openspec archive ux-cal-02-native-density --yes` a archivé
le change en [2026-11-09-ux-cal-02-native-density](../../../openspec/changes/archive/2026-11-09-ux-cal-02-native-density/proposal.md).
Validation active, sans --skip-specs ni --no-validate ; quatre exigences ajoutées
au spec mobile existant. La CLI a signalé six tâches incomplètes avant cette
consolidation ; seuls les résultats ensuite observés sont cochés.
3.2/3.3 restent partielles et ouvertes avec critères et responsables dans
[DEVICE_GATES](DEVICE_GATES.md). L'archive clôt le changement contrôlé accepté,
pas ces gates de release ; aucun contrat canonique assoupli. Livraison/cleanup
ne sont cochés qu'après observation.

La PR de closeout contient uniquement documentation, archive et spec mobile
consolidé ; aucun produit, SCI, API, baseline, PNG ou dépendance modifié.
Contrôles DOCS après check_scope : protocole, OpenSpec strict et diff-check ; pas
de suite produit ni sweep local. CI applicable au closeout à observer.

## Préservation et limites

[AGENT_HANDOFF](AGENT_HANDOFF.md) conserve les décisions/rulings et le chemin du
ledger SDD ; preuves natives, reçus soumis/accepté, RED→GREEN et revues restent
dans `/private/tmp/auren-ux-cal-02-review-evidence/`. Aucun cleanup à cette
préparation ; ne supprimer que les éléments possédés sans travail unique après
preuve d'intégration. Le reçu final vivant doit nommer branches/worktrees
réellement nettoyés et preuves/travaux préservés.

DATA, artefacts installables/RELEASE complet, clavier/accessibilité/retour Android,
parcours natif complet et recettes Android/iPhone physiques restent OPEN.
MOB03 complet OPEN. Runtime réel non activé ; aucun GO déploiement, Store ou OTA.
