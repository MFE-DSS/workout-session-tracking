# SCI-RUNTIME-02 — correctif autorisé et résultats après GO

Reçu préparatoire conservé ; état de livraison dans [CLOSEOUT.md](CLOSEOUT.md).

26 novembre 2026, Europe/Paris. Parent `c454af863278b0801a568437038eb4efb94db588`.
GO exact : « Autoriser ce correctif SCI-RUNTIME-02 », référence `call_12d65838fae34f55aee3aee31ea82f69`.

## Changement et frontières

Le worker installe d'abord ses limites puis fixe l'ORM incident sur `sqlite:///:memory:` avant tout import applicatif. La base réellement consultée reste l'argument serveur séparé, ouverte en lecture seule avec ses gardes propriétaire/snapshot. Seuls worker.py et son test changent côté produit ; aucun budget, SCI, writer, TIME-01, configuration QA, mobile ou flag n'est modifié.

## Preuves exécutées

- Régression RED sur Linux/source readonly : deux échecs réels avant correction ; GREEN ensuite : **128 tests passants**, zéro skip.
- Revue indépendante : un Important du garde de test corrigé. `PermissionError` pouvait être absorbé lorsque var existait ; `RuntimeError` ne l'est pas. Un nouveau témoin de mutation avec worker original et var préexistant échoue effectivement. Aucun changement du test de résultat propriétaire ou de la base attendue.
- Campagne combinée après ce correctif du garde : **356 PASS / 1 FAIL / 1 skip existant**. Le refus nominal intermittent n'est pas effacé par les 128 précédents. Son mécanisme n'est pas prouvé ; le candidat reste HOLD.
- Worker réel corrigé : une série propriétaire/PARTIAL, reps9, sortie14 076octets ;1,9792s monotone,1,5771s CPU enfant, RSS échantillonné86 720 512octets, retour0/reaped/slot libéré.
- HTTP réel isolé, un processus Uvicorn : premier compteA503, compteB200/PARTIAL/reps999, comptevide200/EMPTY ; sansBearer401, configuration injectée422. En parallèle : une réponse200/PARTIAL/reps9 et un503 rapide compatible avec refus busy. Aucun fait étranger ; DB inchangée avant/après GET ; serveur et enfants nettoyés.
- Témoins AS512Mio/CPU2–3s/CORE0 maintenus ; allocation600Mio refusée, enfant CPU tué/reaped. Le traçage diagnostic Python a lui-même rencontré SIGXCPU : ce run instrumenté ne démontre pas la cause du premier503 non instrumenté.
- Captation instrumentée séparément :19statements budgétés,11SELECT après setup,18sources/676321octets, DML refusé ;0,1271s inclut capture et projection. Pas de mesure exacte des instructions VM ni du temps SQL pur.
- Après correction du garde, normalisation des modes du seul volume jetable et sonde série, les mêmes quinze fichiers passent : **357 PASS / 1 skip existant** dans APPROVED_CHECKS_AFTER_PROBE.log (24,42s). Ce passage ne transforme pas les refus intermittents précédents en qualification runtime réussie.
- Sonde série ultérieure :5/5 lecturesPARTIAL/reps9,0,866–1,145s,CPU0,854–1,124s, retour0 et enfants reaped. Elle montre une réussite bornée ; elle ne résout ni ne masque les refus précédents.

## Profil réellement éprouvé et confiance

Même base historique attestée que le [reçu initial](QUALIFICATION_RECEIPT.md) : Debian13.3/Python3.11.14/SQLite3.46.1, amd64 émulé sur DockerDesktopARM64, source candidate montée readonly. Ceci n'est pas une nouvelle image de déploiement ni une qualification OVH/amd64 natif.

La première préparation après GO a conservé les permissions tar0664/0775 ; cette campagne ne reprend pas le précédent constat « aucun bit022 ». Le montage readonly et les refus UID10001 sont des preuves séparées. Les modes du volume jetable ont ensuite été normalisés644/755 avant la sonde série ; son inventaire ne relève plus de chemin mutable, propriétaire inattendu ou symlink. Aucun fichier du dépôt ou hôte QA n'a été chmodé.

Le profil porte TEST_FIXTURE_NOT_OPERATIONAL ; son digest provient de la préparation privée contrôlée, jamais du HTTP. Les sources intégrales et digests restent requis. L'inspection de copies négatives n'est pas présentée comme un durcissement du loader produit. L'alerte SonarS8707 reste à consigner sans modifier son état ; la confiance des parents, ACL, volumes et digest de tout futur déploiement doit être qualifiée séparément.

## Verdict

Catalogue et parités SCI composants : PASS. Correction du bootstrap EROFS : démontrée.
**Runtime opérationnel : HOLD. Chemins opérationnels : HOLD. Lecteur : NOT_QUALIFIED, désactivé par défaut.**
Contrôles locaux : tier ISOLATED, broad ciblé exigé et exécuté, aucun full sweep local ; Ruff fichiers modifiés et budget260≤548, Bandit ciblé/broad sans Medium/High, protocole et OpenSpec33/33, Gitleaks du delta sans finding. Revue indépendante finale : aucun Critical/Important restant ; le garde corrigé a été relu. La livraison exige encore la CI réelle du HEAD final ; aucune fusion n'est annoncée ici. Les refus intermittents et mesures manquantes restent des limites à qualifier, sans hausse de budget.

Preuves privées conservées dans `/Users/martinfeldmann/auren-review/sci-runtime-02-evidence-20261126` : APPROVED_RED_RETRY, APPROVED_GREEN, APPROVED_GUARD_RED, APPROVED_FINAL_TESTS, APPROVED_QUALIFICATION, APPROVED_REPEAT_PROBE. Aucun Bearer, profil d'activation ou base de test n'est publié.
