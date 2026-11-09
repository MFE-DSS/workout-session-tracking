# UX-CAL-02 — passation bornée

9 novembre 2026 — Europe/Paris. **PIXELS_ACCEPTED / CODE_MERGED / CODE_CANONICAL_VERIFIED.**
Lire [DELIVERY](DELIVERY.md), [SPRINT_REPORT](SPRINT_REPORT.md), le
[reçu pixels](../../../clients/mobile/visual-contract/review-receipts/ux-cal-02/receipt.json)
et [DEVICE_GATES](DEVICE_GATES.md). PR code393, HEAD
`6d46e3ed07086204688f5351839d6a1826e6e2f6`, fusionné en
`c7215623e9806a8a7ce12590f5b5e7c099fc3128`. CI PR42689201348 SUCCESS11jobs,
8068backend/3skip, 73suites/913mobile+TS, 77visuels. SonarPR OK/0issue/coverageapp92,5% (pas mesure TypeScript), aucune revue/thread
bloquant. CI canonique [42692021095](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/42692021095) completed/success11jobs, mêmes comptes réellement rejoués.
Sonar canonique : ERROR consultatif ; analyse `887f02a9-747f-4be9-bdc0-241341f1c48b`, révision exacte c721562, 9 novembre20:34:56 UTC : 8bugs / 549smells / 8entrées vulnérabilité externe / 0hotspot ; coverageapp92,5%, nouvelle92,5048%. Même dette que la base3bb1f2d ; aucune mesure TypeScript ni innocuité globale déduite.
Maintenance/cleanup restent PENDING ; aucun résultat futur déduit.

## Décisions et coûts conservés

- Exécuter le plan précis sous GO/G1 existants sans revue routinière ou nouvelle
  question de merge : coût si erroné, rework visible borné ; aucune activation.
- Ordre Task1 → revue → Task2 → revue → recette/pixels/livraison ; conserver les
  interfaces producteurs/consommateurs avant tâche suivante. Une interaction
  native et un ledger, pas sept implémentations indépendantes.
- Fixes Task1 : absence/réglage indisponible conserve l'essai, contexte des preuves
  recoupé, intention pilote legacy recoupée ; faits UNKNOWN conservés. Fixes
  Task2 : back racine Android, sélection avant await, focus aide et état busy du
  candidat. Coût : RED→GREEN/relecture ciblée, aucune règle SCI changée.
- Aucun commit UI Task1/2 avant pixels : conserver diff unique et preuves hors
  worktree. Le rendu natif a révélé observationSection undefined ; omettre le
  champ absent à l'appelant, garder jsonCopy strict. Deux vrais témoins
  contrôleur/journal RED→GREEN ; relecture ADDRESSED/PASS.
- Captures antérieures au correctif NOT_FOR_ACCEPTANCE ; seule soumission finale
  31 captures/3 références acceptée. « Valider ce delta visuel contrôlé » avant
  commit ; reçus initial soumis et final accepté distincts et conservés.
- Réconcilier seulement les documents canoniques : capturebase844cbfb, avant
  publication3bb1f2d, code capturé identique. Coût : garder bases/empreintes dans
  les reçus sans attribuer les pixels à une autre base.
- Décrire limites Expo Go/CUA et gates physiques sans prétendre à une recette
  complète. Coût : RELEASE/QA reprend les gates3.2/3.3 explicites.

## Reprise de livraison

Ne pas redispatcher Task1/Task2/correctif natif terminés ni rouvrir SCI, données,
assets, API ou dépendances. Vérifier sur HEAD final/base actuelle quatre checks
obligatoires, contrôles sécurité applicables, readiness et absence de revue/thread
bloquant. Sous GOV-MERGE-01 : commit de merge avec garde SHA, CI canonique, Sonar
réel consultatif consigné, archive puis closeout via PR, cleanup des seuls
éléments possédés après ancestralité/état propre/zéro travail unique. Aucun bypass,
force-push, squash ou nouvel élargissement.

Les rulings/états SDD antérieurs sont dans
`/private/tmp/auren-ux-cal-02/.superpowers/sdd/IMPLEMENTATION_PLAN/progress.md`,
à préserver dans les preuves avant cleanup ; cette passation en copie les
éléments utiles sans modifier ce ledger. Preuves/rendus/logs/revues :
`/private/tmp/auren-ux-cal-02-review-evidence/`. Conserver ces preuves, les
worktrees d'autrui et le checkout opérateur. DATA, RELEASE et MOB03 complets OPEN.
