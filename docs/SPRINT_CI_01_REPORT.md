# CI-01 — Jest et TypeScript mobiles dans la CI

Date : 2026-11-03. Branche : `sb/ci-01-mobile-checks`. Base : `fcfbcd7`.
Change OpenSpec : `mobile-ci-checks`. Statut : **BASE UPDATED / REVALIDATION PENDING** (PR #347, GO MERGE reçu).

## Brainstorming / Options / Risques / Choix retenu — avant le code

Le 3 novembre, après revue des propositions préparées, l'opérateur demande de continuer le chemin critique.
Le périmètre reste celui de `proposal.md` et `design.md` : aucun code métier ni dépendance changée.

| Option | Choix / conséquence |
|---|---|
| Ajouter Jest/typecheck au conteneur visuel | Écartée : mélange les diagnostics et durées |
| Job mobile dédié, Node 22, lock npm, Jest en série, types | Retenue : vérifications séparées et échecs bloquants |
| Filtrer uniquement les chemins mobiles | Écartée : les changements serveur doivent aussi exécuter le client |

Risques : mémoire bornée par `--runInBand`, runtime des actions mesuré, environnement local fixé au lock,
preuve CI réelle avant merge. La protection GitHub n'est pas modifiée automatiquement.

## Décisions d'exécution

- CODX-00 est préparé/commité séparément ; son push attend un GO PUSH explicite après refus de la revue automatique.
- CI-01 peut être implémenté et vérifié localement sur `fcfbcd7` sans dépendre du contenu de l'adaptateur. Son
  intégration avant MOB-02 respecte l'ordre de la roadmap ; la livraison n'anticipe aucun merge CODX-00.
- Python 3.11.14 installé via uv, venv dédié, FastAPI 0.141.1 depuis le lock ; `app.__file__` pointe sur ce worktree.
- Installation npm initiale : succès, mais l'exécution élevée a pris Node 25.8.2 malgré Node 22 dans le shell
  ordinaire. Les tests et types utiliseront explicitement Node 22.20.0 ; aucun lock modifié.

## Périmètre et preuves

| Contrôle | Résultat réellement observé |
|---|---|
| Garde avant ajout du job | 3 échecs attendus : « Jest et TypeScript absents de la CI » |
| Gardes après ajout du job, runtime des actions, shards, attestation et stabilité | 189 tests passants |
| Jest sous Node 22.20.0 | 32 suites, 422 tests passants |
| TypeScript sous Node 22.20.0 | exit 0 |
| Mutation Jest temporaire | `expect(1).toBe(2)` : exit 1, 1 test échoué / 422 passants ; fichier ensuite retiré |
| Mutation TypeScript temporaire | chaîne affectée à number : TS2322, exit 2 ; fichier ensuite retiré |
| Ruff fichiers Python touchés | propre |
| Budget ruff | 264 ≤ 548, inchangé |
| OpenSpec strict | 4 éléments passent |
| Protocole de specs | OK |
| Revue indépendante à contexte neuf | Aucun constat Critical, Important ou Minor actionnable |
| `actionlint .github/workflows/ci.yml` | SC2046 à la ligne 647 ; reproduit identiquement sur la base `fcfbcd7`, hors du nouveau job |
| `actionlint -shellcheck= .github/workflows/ci.yml` | exit 0 ; syntaxe/actionlint sans l'intégration shellcheck, distinct du résultat complet précédent |
| Full sweep local borné | **7147 tests passants, 378 fichiers, 95 lots, exit 0**, aucune adaptation ; pic 1825 Mo, budget 1869 Mo |
| CI réelle | Non lancée : push non autorisé par la revue automatique sans GO PUSH explicite |

Commandes ciblées exécutées depuis ce worktree :

```sh
.venv/bin/python scripts/check_scope.py
.venv/bin/python -m pytest tests/test_ci_mobile_checks.py -q
.venv/bin/python -m pytest tests/test_ci_mobile_checks.py tests/test_ci_action_runtime.py tests/test_ci_shard_topology.py tests/test_ci_canonical_attestation.py tests/test_ci_runner_stability.py -q
.venv/bin/ruff check tests/test_ci_mobile_checks.py tests/test_ci_action_runtime.py
.venv/bin/python scripts/check_spec_protocol.py
openspec validate --all --strict --no-interactive
```

Les commandes npm utilisent explicitement `/Users/martinfeldmann/.nvm/versions/node/v22.20.0/bin/node` et
`/Users/martinfeldmann/.nvm/versions/node/v22.20.0/lib/node_modules/npm/bin/npm-cli.js`, avec arguments
`test -- --ci --runInBand` puis `run typecheck`, depuis `clients/mobile`.
Les mêmes arguments ont été exécutés pour les mutations. Elles prouvent les sorties des commandes locales,
**pas encore le comportement d'un job GitHub**. Les preuves négatives/positives distantes restent requises.

`actions/setup-node@v6` a été mesurée en `node24` dans son `action.yml` officiel le 3 novembre :
https://github.com/actions/setup-node/blob/v6/action.yml. Cette action est ajoutée à la garde de runtime
existante ; aucun garde-fou node20 n'est relâché.

Aucune baseline, dépendance, migration ni logique d'entraînement changée. Les deux fichiers de mutation
temporaires sont retirés. Les warnings pytest observés concernent les dépréciations amont AnyIO/Pytest et
Starlette/httpx ; ils ne constituent pas des échecs de test.

Le GO PUSH explicite pour CODX-00 et CI-01 a ensuite été reçu. CODX-00 a été poussé ; sa PR #346 est ouverte,
sans merge, avec 8 jobs CI et tous les checks externes verts (run `41668162468`). La barrière d'autorisation de push est donc levée ; les résultats CI resteront consignés uniquement
après observation des jobs réels. Le test du job doit inclure deux étapes négatives identifiables, puis un HEAD
final vert sans les fichiers de preuve. Les mutations locales ci-dessus restent des preuves séparées.

## Verdict initial avant preuves GitHub (historique)

**⏳ ATTENDRE — implémentation et contrôles locaux vérifiés ; preuves GitHub négatives/positives et GO MERGE encore requis.**

## Preuve GitHub négative — réellement exécutée

PR **#347**, run **`41679982474`**, job **`126070762071`**, commit de sondes **`f1a8712`**.
Le code propre est livré dans le commit précédent **`eea4af1`**.

- Installation verrouillée : success.
- `Run mobile logic tests` : **failure**, assertion contrôlée `Expected: 2 / Received: 1`, 422 autres tests
  passants, **exit 1**.
- `Check mobile types` : **failure**, `ci01-type-probe.ts(2,14): TS2322`, **exit 2**.

Les deux sondes ont des causes et des étapes distinctes dans le même run : cela prouve que le diagnostic de
types s'exécute encore après le rouge Jest. Les logs du job ont été relus, pas seulement sa couleur.
Le présent retrait remet le client exactement dans l'état propre vérifié localement ; aucun changement
fonctionnel n'est apporté pour « réparer » ces échecs intentionnels.
Le HEAD final doit maintenant obtenir une CI complète verte. Aucun merge autorisé.

## État exact à la remise du CR architecte / PO

- PR **#347**, prête pour revue après retrait du brouillon, HEAD final **`764b4520c5fcd007ea53c29dce3467ef175f2ca8`**.
- Run final **`41680437230`** : **9/9 jobs completed/success**, dont le nouveau job mobile ; tous les checks
  externes sont verts, dont SonarCloud Code Analysis (résultats relus avec `gh pr checks`).
- Demande d'annulation de l'ancien run de sondes `41679982474` acceptée par GitHub après collecte des deux
  preuves ; ce run n'est pas le candidat à livrer. Aucun rerun ni affaiblissement du pipeline.
- Aucun thread de revue PR non résolu relevé ; revue indépendante du code sans constat important.
- État : **PR GREEN / MERGE PENDING** ; preuves négatives et positives réelles acquises.
- Le nom du check à proposer comme requis est **`mobile checks (Jest + TypeScript)`** ; les paramètres de
  protection GitHub n'ont pas été modifiés. Son ajout reste une décision de l'opérateur.

La PR et son descriptif sont prêts pour revue. L'intégration canonique de CODX-00 et CI-01 précède MOB-02 ;
ces deux merges restent soumis au GO MERGE distinct, non reçu.
Cette annexe de remise est locale et sera versionnée avec le suivi de livraison, sans changer le HEAD en cours
de validation uniquement pour y ajouter des statuts documentaires.

## Intégration séquentielle autorisée — nouvelle validation requise

GO MERGE explicite reçu pour #346 puis #347 par commits de merge, closeout et rebase MOB-02, sans build MOB-02.
CODX-00 intégrée par `60bea5d28eeaecc1eba1c71aefe7186793c4098a`. La branche CI-01 intègre cette canonique
sans réécriture ; conflit documentaire du registre résolu en conservant les deux entrées. Les documents locaux
ont été sauvegardés dans `/private/tmp/auren-closeout-backup-20261103` avant résolution.
Le vert du HEAD précédent ne vaut pas validation de ce nouvel arbre : contrôles locaux selon scope puis CI PR
réelle et qualité externe à relire avant le deuxième merge. La tâche 1.2 est désormais satisfaite.
