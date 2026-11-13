# BODY-01 implementation ledger

2026-11-11: GO revised scope/normative amendment/G1 received; native execution inline. Plan self-review: B01-B08 each assigned; task interfaces preflight above. No product code yet.

Task 1: 15 RED missing feature ->15 GREEN, then additive migration RED missing table ->17 GREEN including migration. Boundary tests found inactive Session after synthetic receipt failure: explicit rollback on unexpected exceptions, RED->GREEN; final21/21. Task-done records same HEAD because changes remain uncommitted per UI/review gate, not a claim that code has shipped.
Task 2: all ten real reader cases plus wrapper confirmed RED (initial9 failures/2pass; strengthened latest-date and coach second observation witnesses2RED). Shared predicate/wrapper then32/32 including command and web tests. Web2RED missing token and unsafe erase ->2GREEN; source dates3RED under investigation (expected UNKNOWN provenance replaced by explicit acquisition precision).
Ruling: preserve legacy /body flag invisibility; minimal native receipt route will allow historical replay separately from new collection permission. New UI never interprets a flag-off replay as current fact access. Cost if wrong: legacy clients might need native status endpoint to recover an old receipt.
Ruling: explicit fixture schema provisioning in tests/helpers.py/conftest/custom body fixture, not startup DDL; migration refusal test drops sidecar to exercise real fail-closed. No auth or consent autogrant added.

### Task4 reprise — 11 novembre
- Ruling: le reçu contient command_digest et le stockage calcule les mêmes octets canoniques BODY que le serveur. Owner/backend restent des gardes séparées ; ce hash n'est aucun fingerprint SCI. Coût si erreur : faux inconnu ou mauvaise association ; témoin octets indépendant et digest divergent refusé.
- Ruling: validation de forme/identité/finite avant SQL, bornes actuelles après lookup de rejeu exact. Une évolution de plausibilité ne doit pas réinterpréter une commande déjà acquittée. Deux RED (rejeu sous bornes changées et ancien mollet seul/date) puis 48 tests commandes/API GREEN.
- Ruling: jour déclaré inclus dans le jour calendrier courant de la période, sans conversion en heure observée ; ancien instant UNKNOWN garde son filtre temporel. Un test du jour courant a échoué (0 au lieu de1), corrigé ; source DAY affichée en UTC pour ne pas glisser au jour précédent.
- Trois suites nouvelles client/resource/SQLite :22 PASS ; TypeScript PASS. 4 tests SQLite ferment/rouvrent le vrai fichier, gardent payload et partition, exigent vérification puis rejeu explicite, refusent ack divergent et réponse tardive. 5 tests d'intégration journal existants également passants (run séparé22 PASS avec API13+SQLite4+journal5).
- Pas de commande dans outbox/PLAN, pas de service background BODY, pas de deuxième chronologie locale. Préparation durable et état SENT_UNKNOWN relus avant HTTP. Les trois suites initiales sans modules documentent seulement l'absence, pas des assertions RED artificiellement comptées.

### Task5 — implémentation en cours, pas de livraison
- Famille native et branchements ConnectedApp/Profil/Progrès présents ; champs groupés, date explicite, null explicite, versions et effacement confirmé. Un writer n'est pas disponible dans la preview mémoire web. Journal BODY indépendant du flag PLAN.
- Tests locaux : 70 PASS sur13 suites (client/resource/SQLite/BODY/Progrès/journal) ; ensuite65 PASS sur12 suites affectées après ajustement de composition (journal existant non répété). TypeScript PASS après correction du type de ref TextInput. Le premier test de saisie utilisait le mauvais événement onChange : corrigé vers onChangeText comme les consommateurs existants, aucune correction produit déduite de ce faux échec.
- Banc synthétique HTTP8173, migrationbase→head réelle et APIconsommées nativement ; une première capture iOS BODY_IOS_OVERVIEW.png conservée, **pas un gate visuel complet ni acceptation**. Le banc externe importe les sources de production mais n'est pas ConnectedApp intégral.
- Problèmes de banc conservés : Metro localhost bind IPv6 seulement, diagnostic curl127/localhost, corrigé par NODE_OPTIONS=--dns-result-order=ipv4first dans le seul processus de test. Fast Refresh a laissé une vue blanche ; preuve de redémarrage non établie, ne pas déclarer PASS.
- Disque :4.8GiB avant recette ; création AVD neuf refusée (besoin7.3GB), essai read-only sur ancienne AVD avec COW temporaire ; espace tombé137MiB, automation failedToCreateImageDestination. Arrêt de notre seul émulateur (PID59824 vérifié -read-only/5586), overlays automatiquement retirés. Notre simulateur iOS dédié5F1041AE arrêté puis supprimé pour rendre2.5GB ; aucune autre AVD/device/VM ou données QA02 supprimée. Captures/audit/db/reçus conservés hors simulateur. Cette limitation empêche encore le board complet, pas une permission de remplacer du natif par des mocks.
- Question opérateur de statut : réponse explicite non, le critical path total n'est pas terminé ; BODY en cours, NUTmanuel/MOB06/MOB07 ensuite. Aucune PR, aucun APK/OTA ou déploiement de ce delta.

### Reprise FINAL DELIVERY — mandat du11novembre
- Snapshot72fichiers relu : zéro écart avant nouvelles corrections ; même branche/worktree, aucun reset/stash/clean/recréation. Premier sweep fini437fichiers, neuf lots en échec,20noms de tests distincts ; aucun fichier sauté. Processus61942 terminé, aucun sweep concurrent.
- Ruling: les gardes CP7.5A conservent leurs preuves de champs absents/null/date mais lisent la tête effective et exigent original immuable/nouvel ID. Les fixtures acquièrent explicitement l'accord, jamais grant de startup. Coût si erreur : une ancienne sémantique de champ pourrait être masquée ; assertions de tous les autres champs et originaux renforcées.
- Ruling: la sentinelle EKB suit le head BODY autorisé et vérifie son parent PLAN ; aucune donnée/règle EKB modifiée. La garde Worked Area n'admet que les quatre chemins exacts de metadata BODY approuvés ; autres modèles/migrations interdits et services body_map_descriptor/muscle_mapping inchangés. Coût : allowlist à maintenir pour une future migration autorisée, aucune exemption de dossier globale.
- Ruling: classification des onze routes BODY dans les deux features MOB00 existantes (mesures9/consent2), invariant exact-une-feature conservé ; statut REWRITE_NATIVE, pas VERIFIED_NATIVE anticipé. Le mandat de reprise autorise ce raccordement documentaire.
- Ruling: suppression des nouveaux styles inline et usage du disclosure accepté via CSS locale BODY. Le ratchet quantitatif inline21→20 est resserré car la dette a diminué ; aucune baseline pixel n'est régénérée. Nouveau fichierCSS et tests/inventaire ci-dessus sont les seuls leases techniques ajoutés par le mandat de reprise.
- Premier rerun des neuf modules :148PASS/2FAIL (accord non acquis dans un cas SSR et ratchet inline à resserrer), corrections appliquées ; run final ciblé en cours.
- Neuf modules repris après les vingt échecs du premier sweep :150PASS. CP7.5A confirme maintenant les versions courantes et l'immuabilité, les protections EKB/WorkedArea restent bornées aux seuls chemins BODY autorisés. Les deux derniers échecs du rerun étaient des montages de test et ratchet : corrigés, aucun startupDDL.
- Nouveau test du ConnectedApp entier : clients/ressources/resolveJournal/ownershipBook/journal/SQLite fichier réels, OS et RPC synthétiques explicites. 4PASS : Profile→BODY→Progress, décimal, correction/audit/effacement, réponse perdue→fermeture/réouvertureSQLite→relecture du même reçu sans secondPOST, accord requis puis retrait. Les échecs de construction du banc étaient fetch capturé avant spy, book de test resté lié à une connexion fermée et fenêtre UTC différente de la requête ; pas présentés comme bugs produits.
- Recette iOS réelle ConnectedApp via ExpoGo58 : tabs natifs→Profil→Mesures, sourceowner synthétique relue, date choisie explicitement,71,5kg entrés via champ accessible, POST200 et lectureconfirmée root6. Module notifications conservé ; avertissements ExpoGo présents, pas d'exception bloquante iOS observée.
- Ruling: séquencer sweep et recette quand le disque passe sous500Mo. Second sweep déjà lancé, pas doublé ; parent6232 suspendu entre lots pendant les captures (enfant finit son lot), à reprendre SIGCONT. Aucune limite mémoire/gate modifiée ; coût : durée du sweep, pas un PASS anticipé.
- Défaut CTA de création sans nombre : test RED (day seul active), correction hasFact pour CREATE, date-seule CORRECT conservée ; GREEN en cours. Le serveur refusait déjà le relevé vide, aucune observation inventée.

- Recette iOS finale : vrai ConnectedApp Profil→Mesures, création synthétique71,5kg, correction71,25kg, lecture des deux versions puis effacement explicite de la seule lignée6. Le registre courant ne la retourne plus. Banc supplément pending : commit HTTP réel puis perte injectée de réponse, Vérifier→reçu confirmé sans second POST. Progrès réel consomme les têtes restantes et affiche72kg du10novembre ; aucun point supprimé réintroduit.
- Clavier logiciel iOS : après réglage du seul simulateur dédié via menu I/O, pavé décimal réel1/3/,/5 utilisé pour31,5cm (pas seulement setValue). Grande fonte accessibility-medium observée, Done visible, ordre AX conservé ; VoiceOver vocal/focus exhaustif non certifié. En-tête feuille autorisé à revenir à la ligne, cibles48 conservées. Icône flottante ExpoGo visible et signalée comme outil de recette.
- Formulaire vide : test date-seule RED bouton activé→GREEN avec exigence d’au moins un nombre pour CREATE ; correction de date seule conservée. Deux suites formulaire/fullConnected7PASS. FullConnected4tests utilisent SQLite fichier/fermeture-reprise, correction/audit/effacement, readbackProgrès et accord/retrait ; frontières OS et réponses HTTP de test identifiées, aucun shim produit.
- Ancienne vue blanche FastRefresh non reproduite dans le banc neuf séquencé. FastRefresh peut réinitialiser la navigation/auth du banc ; cold launch retrouve les faits serveur/local. Cause historique non démontrée : ne pas annoncer une correction certaine par simple corrélation disque.

### 12 novembre — DA suspendue, revue technique indépendante
- Décision opérateur : DA-06C refusée ; aucune nouvelle itération autonome de pixels BODY. Le prochain livrable est un brief de master externe, pas DA-06D en code. GO BODY/amendement/G1 conservés ; backend/API/SQLite et tests continuent indépendamment. Aucun commit UI, baseline, activation ou release.
- Revue technique fraîche : Important B01 — un nombre legacy hors bornes resoumis inchangé bloque la correction d'un autre champ, alors que l'héritage absent fonctionne ; Minor B04 — le parser SSR fait ses bornes avant le kernel de rejeu exact. Preuves mémoire indépendantes conservées hors worktree.
- Options/risques/choix avant patch : supprimer une ancienne valeur ou lui donner une nouvelle provenance est exclu. Dupliquer une politique de plausibilité dans le SSR dériverait. Choix : parsing structurel/finite sans bornes pour les adapters transactionnels ; kernel sous garde propriétaire/tête valide tous les nombres de CREATE et seulement les vrais changements de CORRECT ; le corps/digest reste exact. Le SSR garde son rendu400 existant pour une nouvelle erreur numérique via une erreur métier typée, sans nouvelle composition ni template.
- Tests RED attendus : commande complète avec legacy800 inchangé/taille85 ; vrai formulaire SSR complet ; CREATE/CORRECT rejoués sous bornes nouvelles ; corps divergent409 ; nouvelle valeur hors bornes et non-fini refusés. Le sweep8555PASS/1ignoré couvre le snapshot précédent ; il ne devient pas automatiquement une validation globale du correctif.

- Vérification corrective terminée : les sept nouveaux cas ont donné5FAIL/2PASS avant patch puis7/7PASS. Le broad borné de17modules et consommateurs donne320PASS, pic1516Mo pour budget1800Mo. Ruff des trois sources/deux tests, budget260≤548, Bandit des trois sources et protocole passent. Reçu : BODY_REVIEW_FIX_GREEN_RECEIPT.json ; aucun nouveau sweep global/CI ni résultat mobile final déduit de cette campagne.
- Relecture indépendante du diff correctif : B01/B04 résolus côté backend ; gardes propriétaire/CAS/rejeu/digest et bornes des acquisitions fraîches conservées. Limite distincte : les attributsHTML min/max du formulaire existant peuvent bloquer une valeur legacy avantHTTP ; aucune recette navigateur complète ni modification de template revendiquée.
- Brief externe livré dans /Users/martinfeldmann/auren-review/body-cockpit-master-20261112, avec contraintes390×844, contenu synthétique typé et copies empreintées des référencesLOCKED. Aucun master créé/accepté, aucune génération/envoi tiers, aucun nouveau pixel. Avant livraison BODY : master accepté puis reconstruction fidèle, consommateurs/browser/device, revue finale et contrôlesMIGRATION/CI sur le HEAD final ; aucun commit/PR/merge anticipé.

### 12 novembre — continuation du critical path après étude externe
- Base canonique fetchée3cf77e1, worktree BODY conservé. Préparation NUT vide après crash : récupération documentaire AST des huit documents du11novembre, nouveau worktree durable distinct, ancien temporaire laissé intact. RéservationMOB06/Maltin relue, pas de nouveau scope concurrent ; fileassets indépendante enregistrée. GOV/CLAUDE relus, GO BODY/amendement/G1 non redemandés.
- Tier MIGRATION relu80fichiers : sweep complet borné1800Mo lancé via scriptcanonique,4fichiers puis adaptation automatique vers1 ; aucun second sweep backend lancé. Les trois nouveaux cas SSR ont été ajoutés APRES son démarrage, de même que la correction attributs/formatage ; les résultats du sweep et du rerun SSR final doivent donc être rapportés comme campagne composée, pas tous comme un seul snapshot immuable.
- Revue SSR indépendante : bornesHTML pouvaient empêcher de corriger un autrechamp si legacy800/12 ; step0.1 bloquait71.25. Tests rendus3RED, attributs stepany et bornesedit englobant le nombre rendu, CREATE borné et kernel strict inchangés. Aucun CSS/géométrie/primitives changé, aucun commitUI.
- Revue a aussi signalé le formatage:g à6chiffressignificatifs :71.123456 devenait71.1235 et pouvait être acquis involontairement. Important factuel dans ce scope. Test étendu1RED/3PASS puis formatage roundtrip str avec retrait du seul suffixe.0 ; suite SSR finale18PASS. Correction ne déplace aucun fait et ne change aucune provenance des nombres inchangés ; les nouveaux vrais changements hors bornes restent refusés.
- Browsercheck synthétique : quatre valeurs800/12/71.25/71.123456 réellement valides dans Chromium sur le HTML SSR servi ; FormData du navigateur vers vrais endpointsTestClient, seul waist changé, original/poids exacts conservés ; nouvelle800 refusée côté navigateur. Redirect non exercé, pas recette native/physique/acceptationpixels. Deux erreurs du banc conservées séparément (sélecteur ambigu/logout puis pont de redirect), pas des défauts produit.
- Migrationpatterns stricts, roundtripvide, Alembicdrift, snapshot :4/4PASS sur copies neuves. Gitleaks diff+nouveauxfichiers avant correctifSSR :PASS ; première invocation pointait une config absente, erreuroutil conservée puis commande par défaut correcte, aucun secret détecté. Contrôles finaux et sources actualisées seront consignés après fin des campagnes.

- Fin de campagneglobale :365fichierspassés avantstopmémoiretraining_preferences(1928Mo), reprise97nodesexacts+71fichiersrestants sous1800Mo, tousverts.8562PASS/1ignoré, piclotaccepté1795Mo. Aucunfichier sauté ; ne pas inclure les résumés des lots interrompus dans le total. SSR18PASS/4Chromium comme complémentpostcorrectif, pas fauxsnapshotunique. Mobile94suites/1155PASS ; TypeScript1024MoPASS après plafond384MoOOMlocal, pas régressionproduit. StatiqueRuff/budget260≤548/protocole/Bandit etGitleaksdiffcourantPASS. AucunCI/Sonar/PRBODYnouveau, aucunUI/masteraccepté ni déploiement.


## 13 novembre — reprise sur branche réelle

Fast-forward préservant les 80 fichiers de travail vers1462482 (delta parent100%
documentaire). Aucune réapplication du patch combiné. Témoin de downgrade
réconcilié vers le parent exact PLAN, identique au correctif revu sur assemblage.
Revalidation sur cette branche, sans nouveau composant ni commit UI.
Le checkpoint backend prévu par IMPLEMENTATION_PLAN reste distinct de toute
readiness UI/PR ; SSR et master natif non acceptés.

Ruling : le checkpoint tâche1 expose seulement des modules internes et une migration,
pas les writers/readers publics encore couplés au SSR. Une nouvelle revue a
reproduit le consentement ORM périmé (RED) ; le kernel relit désormais la ligne
sous le verrou d’écriture avec populate_existing. GREEN30 puis48 témoins, dont
startup réel sans sidecar. Aucun changement du comportement des replays exacts.

## 13 novembre — orchestration des trois PRs, correctifs du reliquat

PR407 reste au checkpoint technique1fd97eba ; UI/master et reliquat public non
livrés. Revue fraîche du reliquat : R01 saisie native d'un pair/date bloquée par
un nombre historique inchangé hors bornes ; R02 effacement nouveau inaccessible
après retrait/reprise faute de sélection/token. Aucun Critical identifié ; ni
la revue ni les CI du checkpoint ne certifient les composants non committés.

Ruling R01 : reconnaître l'égalité numérique finie d'un champ historique avant
les bornes d'acquisition, l'omettre de la commande, puis conserver le parser et
les bornes stricts pour tout nombre nouveau/changé. Cela préserve aussi le
préremplissage historique négatif/exponentiel sans autoriser de nouvelle saisie
de ce type. Coût si erreur : un champ changé pourrait être omis ; témoins de
pair/date réels et rejets de nouvelles valeurs sont exigés. RED4FAIL/8PASS
reproduit la barrière native ; aucune géométrie ni politique SCI à changer.


Ruling R02 avant apply : protocole ERASURE_ACCESS_PROTOCOL.md, projection
minimale explicite des GET existants, aucun chiffre corporel/grant/table/route
nouvelle. Curseurs liés au purpose/owner/plage/révision, tête CAS fraîche avant
effacement explicite de toutes versions. Chemins natif/SSR de gestion gardés
hors commit UI ; retrait ne force pas de nouvel accord pour supprimer.
RED HTTP2, client9, resource3, ConnectedApp1 et SSR1 reproduisent les barrières.
GREEN HTTP2, client/resource puis mobile complet1178, lecture/SSR42 ; ces campagnes
sont distinctes. TS final exit0. Relecture corrective R01/R02 sans nouveau
Critical/Important ; une limitation mineure du formulaire SSR clear-only
partiel reste visible, sans bloquer l'effacement.

Checkpoint ports prévu dans Draft407 : helpers read minimaux + témoins, client,
resources, pending/recovery et tests unitaires, delta type-only du graphe poids ;
aucun mount/APIpublic/SSR/UI/journal attach/ConnectedApp. Le reliquat corrigé
reste sauvegardé, le master BODY toujours NOT_ACCEPTED. Pas de nouveau GO ni
merge de scope incomplet. Les vérifications/CI exactes suivent leur reçu réel.


CI43522207147 du checkpoint2b328bf : mobile1159PASS, puis typecheck échoue
WeightTrend.tsx12 TS2345. Cause exacte : type partagé élargi à WeightPoint tandis
que historyView/UI du worktree n'était pas publié. Pas panne infra. Ruling :
conserver WeightEntry comme défaut de WeightWindowState, spécialiser seulement
le port BODY. Aucun décodeur historique ou UI à publier. Export du client du
HEAD committé reproduit le rouge, puis même export+3fichiers de correctif donne
TS exit0 et Jest1160PASS. Nouveau témoin compile-only de compatibilité legacy
RED TS2322→GREEN. Worktreecomplet TS exit0. Addendum de revue indépendant sans
Critical/Important ; aucun reset/stash/cascade de modifications. Nouvelle CI
exacte requise après ce patch minimal, sans transformer le premier rouge enPASS.
