# UX-CAL-02 — livraison du delta contrôlé

9 novembre 2026 — Europe/Paris. **PIXELS_ACCEPTED / CODE_MERGED / CODE_CANONICAL_VERIFIED / NOT_ACTIVATED.**
Code canonique vérifié. La publication du closeout et son nettoyage restent à
observer ; ce reçu conserve cet instant de livraison.

## Mandat et résultat

GO BUILD/G1 : « Autoriser le build UX-CAL-02 et valider G1 ». Pixels :
« Valider ce delta visuel contrôlé », reçus le 9 novembre avant le premier commit
UI `6d46e3ed07086204688f5351839d6a1826e6e2f6`.
[PR393](https://github.com/MFE-DSS/workout-session-tracking/pull/393).
GOV-MERGE-01 couvre code, corrections et closeout du seul périmètre autorisé.

L'instrument commun est plus compact ; détails et aide applicables sont
progressifs, les faits d'observation groupés en deux volets sans mutation
intermédiaire. Les tuples négociés inventaire/profil/intention/réalisation/policy/
sémantique sont recoupés côté client. L'aide commune/réalisation/arrêt est
contrôlée avant ouverture. Les deux mineurs différés de PLAN-CAL-01 sont traités
dans ce scope ; aucune nouvelle autorité scientifique n'est créée.

## Preuves réellement acquises

Le [SPRINT_REPORT](SPRINT_REPORT.md) conserve options, décisions, relecture des
contrats UI et chronologie des corrections. Contrôles frais précommit : tier
ISOLATED, broad consommateurs 25 suites/387 tests, TypeScript, protocole,
budget Ruff 260≤548, OpenSpec strict 20/20, Gitleaks staged et diff-check PASS.
Les passes antérieures 363/376 et reruns ciblés restent des instants distincts.
Revues indépendantes Task1/Task2 et globale : corrections traitées ; relecture
du correctif natif de brouillon ADDRESSED/PASS. Serializer strict conservé.

Le [reçu pixels versionné](../../../clients/mobile/visual-contract/review-receipts/ux-cal-02/receipt.json)
trace 31 nouvelles captures natives et trois références figées, sources/hashes
et acceptation. iOS26.3/390pt, AndroidAPI36/360–480dp ; fontes observées Android
1,3×/2× et iOS1,353×/2,143×. CTA d'entrée Android mesuré 68→48dp à fonte normale.
Le banc rend le présentateur de production et le vrai écran d'entrée avec
contrôleurs/HTTP propriétaires réels. Faits et brouillons synthétiques explicites,
aucune fixture SCI READY servie. La chaîne HTTP synthétique sept rencontres →
vrai V3 → refus d'ack altéré/ack exact → même séance 7 exercices/14 séries et
journal PER_IMPLEMENT n'est pas un parcours humain natif intégral.

Captures à `844cbfb6b2f11c656b129e47d9db63b2d117cc04` ; canonique avant
publication `3bb1f2d20ad87de3312f8784c0101a72484ebfdd`, avancée documentaire
sans changement des sources produit capturées. Contrats/source SCI, backend,
API, schémas, dépendances, composants globaux, MISSION/exécution et baselines
restent conservés.

## Reçu distant à compléter après observation

| Élément | Observation à cette préparation |
|---|---|
| HEAD code | `6d46e3ed07086204688f5351839d6a1826e6e2f6` |
| CI PR393 / quatre checks requis / readiness | [42689201348](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/42689201348) SUCCESS, 11 jobs sans retry : 8068 backend/3 skip, 73 suites/913 mobile + TypeScript, 77 visuels ; quatre requis, Sonar et Gitar success ; aucune revue/thread bloquant |
| SHA de merge code, garde HEAD/base | `c7215623e9806a8a7ce12590f5b5e7c099fc3128`, merge gardé sur HEAD6d46e3e/base3bb1f2d fraîchement relus |
| CI canonique code | [42692021095](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/42692021095), HEADc721562, completed/success, 11jobs sans retry ; 8068backend/3skip, 73suites/913mobile+TypeScript, 77visuels |
| Sonar PR393 | Quality Gate OK, 0 issue, coverage app92,5% ; cette couverture ne mesure pas TypeScript ; consultatif GOV-SONAR-01 |
| Sonar canonique | ERROR consultatif ; analyse `887f02a9-747f-4be9-bdc0-241341f1c48b`, révision exacte c721562, 9 novembre20:34:56 UTC : 8bugs / 549smells / 8entrées vulnérabilité externe / 0hotspot ; coverageapp92,5%, nouvelle92,5048%. Même dette que la base3bb1f2d ; aucune mesure TypeScript ni innocuité globale déduite |
| Archive | CLI après merge code : quatre exigences ajoutées au spec mobile existant ; validation active, tâches3.2/3.3 et livraison restante non simulées |
| PR closeout / CI applicable / merge / cleanup | PENDING — responsable livraison |

Aucun succès futur du closeout, archive publiée, CLOSED+CLEANED ou déploiement
n'est anticipé. [DEVICE_GATES](DEVICE_GATES.md) conserve les tâches3.2/3.3 partielles ;
DATA, RELEASE complet et MOB03 complet restent OPEN.
