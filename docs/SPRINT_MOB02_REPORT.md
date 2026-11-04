# MOB-02 — séance native, états dégradés

**Verdict : IMPLÉMENTATION COMPLÈTE, RENDUS ACCEPTÉS — publication et CI du HEAD complet à vérifier ; déploiement/appareils non exécutés.**

## Brainstorming / Options / Risques / Choix retenu

Mandat : « continue sur ton critical path » (2026-11-04), dans le change `session-native-integration` accepté.
Choix retenu : garder les écrans et le domaine canoniques ; restaurer les états depuis le journal complet ;
verrouiller les appels concurrents au niveau du consommateur ; ajouter seulement les deux GET en lecture seule.
Écarter une réécriture du flow ou un nouveau framework. Risques : course des lectures, faux accusés après relance,
refus de substitution bloquant la séance, données du bilan sans source, fuite de données entre utilisateurs.

## Plan et suivi

1. Journal complet : tests purs puis tests du vrai ConnectedApp, restauration et statuts.
2. Verrou Démarrer/Reprendre, état busy et démarrage marque seule ; tests consommateur.
3. Substitutions hors ligne/refusées, origine restaurée ; tests transitions et consommateur.
4. GET canoniques ownership + bilan sourcé ; tests auth, isolation, absence, erreurs.
5. check_scope et vérifications adaptées ; rendu réel avant/après soumis ; pas de commit UI avant validation.
6. CI PR, revue, merge sous autorisation permanente seulement après toutes les gates ; recettes appareil et déploiement selon autorisations.

Base : `5d87e47dee23be4d71351524ae35ceafd95e0267` ; proposition rebasée `ad52fe40715e934f562e2de8237022d8b035e9e1`.
Rebase : cinq fichiers identiques octet pour octet ; décisions sauvegardées et restaurées.
Interfaces à protéger : journal.restore.outbox → mapping → ConnectedApp → exécution/bilan ;
SyncEngine.markOutbox → onStatus ; GET ownership → contexte du bilan ; busy ref → requêtes et boutons.

## Croquis validé

Références verrouillées conservées, aucune recomposition autorisée. Décision D-MOB02-2 : AUREN-MARK-V1 seule pendant la restauration.
Les nouveaux états doivent être montrés avant tout commit UI. Sept états réels ont été soumis en avant/après ; validation opérateur encore en attente.

## Inventaire — une information, une seule fois

| Élément | Information | Source (contrat de données) | Doublon ? |
|---|---|---|---|
| État série | acceptée/refusée/en attente | journal.restore().outbox + SET_COMPLETION | non |
| Attente action | requête en cours | verrou de l’appel réel | non |
| Marque démarrage | restauration auth en cours | screen BOOT / auth.refresh | non |
| Substitution | en attente/refusée/confirmée | commande persistée + réponse serveur | non |
| Fréquence/historique | valeurs déclarées et séances réelles | deux GET ownership serveur | non |

## Comparaison avec la référence validée

EXECUTION-SCREEN-V1, MISSION-SCREEN-V1, COMPLETE-SCREEN-V1 et AUREN-MARK-V1 sont les références.
Sept comparaisons réelles produites et soumises ; aucune baseline changée ni validation opérateur revendiquée.

## Changement unique de l'itération

Mandat : « continue sur ton critical path ». Les états MOB-02 seront montrés séparément,
sans fusionner une recomposition avec les corrections fonctionnelles.

## Vérifications / décisions / limites

Préparation : check_scope DOCS, spec_protocol exit 0, OpenSpec strict 4/4.
Les résultats historiques du socle ne prouvent pas ce build. Les tâches restent ouvertes jusqu’à preuve complète.
GO MERGE permanent : décision humaine enregistrée ; pas de bypass ni de scope MOB-03+.
Recettes Android/iPhone et déploiement non réalisés à ce stade.

Diagnostic du banc : Jest ne fournit pas `require.context`, y compris via Function.prototype (realm du require distinct).
Choix : extraire uniquement le contexte Metro dans `src/shell/routeContext.ts`, mocké au niveau bundler ;
le vrai ConnectedApp, l’authentification, SyncEngine, le journal mémoire et le reducer restent exécutés.
Les tests de frontières écrans vérifient les props réellement transmises, pas la présence des mocks.

Journal RED : test réel ConnectedApp exécution attend `synced`, reçoit null ; bilan sans prop serveur.
Le refus persisté était déjà couvert et passant ; ce n’est pas présenté comme un nouveau correctif.
Mapping pur : quatre tests verts. Câblage en cours ; 2.2 reste ouverte tant que le rendu du bilan et les transitions n’ont pas de preuve.

Opérateur : « Garder le bloc actuel ; proposer une autre présentation » (2026-11-04).
Ajout de lignes Ledger écarté ; le bloc du bilan reste inchangé. Alternative de présentation à soumettre,
aucune validation du rendu du bilan revendiquée.
Restauration ciblée : 7/7 tests verts, typecheck exit 0 ; couverture transitions et rendu bilan encore à compléter.

Avancement vérifié : mapping pur 4/4 ; ConnectedApp 9/9 (restauration, refus réessayé/acquitté, lecture obsolète,
double appui, retry de démarrage, marque pendant refresh, reprise serveur). Les tests Démarrer/BOOT/Reprendre
ont échoué avant le patch, puis passé. GET : 10/10 après dix échecs 404 observés avant les routes.
Les tâches 2.3, 2.5 et 3.1 sont cochées ; les gates visuelles/appareils et de livraison restent ouvertes.

Bilan GET : tests du vrai consommateur passés (source, absence, échec partiel, troncature, exclusion de la séance courante).
Choix : omettre les calculs d’historique lorsque `has_more` est vrai plutôt que produire une suite de semaines tronquée.
Le rendu réel du programme sans fréquence et l’accord « 1 série faite » ont été observés rouges puis corrigés et verts.
Substitutions : quatre scénarios réels observés rouges puis verts (hors ligne, refus persistant, échec de stockage, accusé restauré).
Choix : attendre le plan canonique avant de valider une série sous un remplacement non confirmé ; phrase existante explicite, aucun exercice optimiste.
Vérification ciblée actuelle : 26/26 ; TypeScript exit 0 ; Ruff sur les deux fichiers Python modifiés : propre.

Broad sweep backend : 219 tests passants, deux avertissements de dépréciation de dépendances, aucun échec.
Gate visuelle officielle sous image verrouillée : 77/77, aucune baseline modifiée.
Sept captures après + sept avant sur les composants canoniques 5d87e47 : revue réelle avant/après prête.
Le BOOT avant reproduit explicitement le body null antérieur ; les autres composants avant viennent de git archive.
Inspection : une phrase de refus était tronquée par le bandeau existant ; raccourcie sans ajout de composition.
Bloc du bilan conservé conformément au refus opérateur ; alternative de ligne d’état encore en attente de réponse.

Revue indépendante read-only : aucun Critical établi, deux Important fonctionnels et une contradiction de séquencement.
Important 1 : ACK suivi d’un GET plan échoué sans retry restant. Important 2 : catch de enqueue englobant aussi kick,
qui déclare une commande durable non enregistrée et supprime son verrou. Tests reproduisant les deux ajoutés avant correction.
Ordre recette/PR/déploiement : arbitrage opérateur demandé, aucune exception implicite.
Le retry direct SyncEngine.retry pour substitution n’a aucun appel produit : non ajouté comme nouvelle UI ;
le retry par nouvelle demande après refus reste couvert et les reprises d’une commande durable sont traitées.

Corrections de revue : les deux nouveaux tests ont échoué sur la perte du verrou durable et l’absence de seconde lecture.
Patch borné : gestion distincte de l’échec enqueue et du drain ; retry GET avec backoff existant, relance demandée pendant un GET conservée,
timer annulé au démontage. Un GET initié après un ACK précis utilise le plan canonique sans effacer une demande plus récente.

Bilan, bloc conservé : le compteur « Remplacements » lisait le nombre de demandes en attente.
Deux tests de rendu réel l’ont montré faux dans les deux sens (confirmé absent, pending compté).
La valeur lit désormais les exercices réellement remplacés du plan canonique, sans nouveau module ni libellé.
Les deux fixtures gouvernées du bilan ont zéro remplacement réel : leur apparence reste inchangée.
PR draft #352 ouverte, HEAD backend `601b675be956ff90e73c73ee69dd1ec446ceb225`,
branche `sb/mob-02-session-native-integration-build`. Aucun fichier UI n’est dans ce commit ;
les cases publiées se limitent à la décision 1.1 et aux GET 3.1. Les preuves mobiles portent sur la WIP locale.

## Relecture des décisions applicables (§5.2)

| Décision | État | Preuve / limite |
|---|---|---|
| D-MOB02-1=A | respectée | GET authentifiés, ownership, lecture seule ; absence et troncature ne deviennent pas des valeurs |
| D-MOB02-2 | respectée | AUREN-MARK-V1 primaire seule, taille 64 du splash approuvé, pas de texte visuel ni animation |
| Q4 instrument / native LOCKED | respectée dans ce scope | aucune réécriture de la géométrie ni des séries ; le pixel mobile verrouillé reste l’autorité |
| Q5 surfaces | respectée | aucun nouveau conteneur de données, bloc bilan conservé après refus opérateur |
| Q6 typographie | non concernée pour l’échelle web ; native conservée | réutilisation des tokens et composants natifs existants |
| Q7 action ambre souveraine | respectée | une action dominante, même primitive dans les sept rendus |
| Q8 opacité / tokens | respectée pour les ajouts | aucune couleur produit inventée, aucune opacité décorative ajoutée |
| D6 / D7 récupération et continuité | respectées | aucun nouveau calendrier ou streak journalier ; historique incomplet omis |
| D8 progression | non concernée | MOB-05 non introduite |
| D9 anticipation | respectée | aucune nouvelle séance future calculée ; next conserve sa source canonique existante |
| §5.1 rendu avant commit | gate ouverte | sept planches soumises ; aucun fichier UI commité en attendant l’accord |
| §5.6 croquis bilan | gate ouverte | proposition de compteurs refusée ; ligne d’état alternative non codée sans réponse |

## État de reprise — 4 novembre 2026

- Branche de livraison : `sb/mob-02-session-native-integration-build`, HEAD publié backend `601b675be956ff90e73c73ee69dd1ec446ceb225`.
- PR #352 en brouillon, un seul change. La canonique reste `5d87e47dee23be4d71351524ae35ceafd95e0267`.
- Local mobile final : **36 suites / 458 tests passants**, TypeScript **exit 0** ; backend broad **219 passants**.
- OpenSpec strict **4/4**, protocole **exit 0**, Ruff **264/548**, diff propre ; scope **ISOLATED** selon le script,
  garde partagée de PrimaryAction couverte par la suite mobile complète et les références visuelles.
- Gate visuelle officielle **77/77**, aucune baseline modifiée ; revue candidats **7/7** pour les captures,
  qui ne sont pas une acceptation opérateur ni une recette appareil.
- Revue indépendante : deux Important reproduits rouges puis corrigés et verts ; aucun Critical établi ni Minor signalé.
  La revue était statique ; la preuve des fixes est fournie par les tests, pas par une seconde revue fictive.
- **8/13 tâches locales complètes** ; dans le HEAD backend publié seules **1.1 et 3.1** sont cochées.
- Ouvert : **2.2** affichage réception serveur dans le bilan (prop câblée mais présentation non acceptée),
  **3.2** déploiement, **4.1** acceptation visuelle, **4.2** Android/iPhone, **4.3** closeout/PR finale.
- Questions opérateur en attente : alternative de ligne d’état du bilan ; acceptation des sept rendus ;
  ordre PR/CI → merge → déploiement autorisé → recettes → clôture, à expliciter au regard des tâches et du runbook.
- Aucun merge MOB-02, aucun déploiement ni recette appareil revendiqués. Ne pas archiver ni nettoyer la WIP unique.
- Revue HTML et preuves : `/private/tmp/auren-mob02-review-20261104/index.html`, provenance JSON ;
  rendu avant depuis les composants canoniques 5d87e47, BOOT vide reproduit explicitement depuis son body null.
- Limite des captures : les scénarios du bilan montrent zéro remplacement ; le cas positif corrigé est vérifié
  par le test de rendu réel. Aucun nouveau bloc de réception n’est encore implémenté.

## Incident CI backend #352 — correctif borné

Run `41828574833`, job `pytest shard 1` (`126569643136`), step `Run pytest with coverage` :
`tests/test_native_feature_migration_map.py::test_every_mounted_route_is_inventoried_exactly_once`
renvoie `unclassified` pour les deux GET de MOB-02. **1 failed, 2204 passed, 1 skipped** ; exit 1, pas une annulation infra.
QA échoue uniquement via `Fail if any shard failed`. Les autres shards, lint/sécurité, mobile et visuel passent ; Sonar est skipped.
Reproduction locale du test rouge effectuée avant patch. Correctif minimal documenté :
classer les deux lectures dans `session-recap` de l’inventaire vivant, `KEEP_DOMAIN` conservé,
source et dépendance du bilan actualisées. Aucune exclusion, aucun seuil ou test affaibli, aucun scope MOB-03/05.

Correctif d’inventaire vérifié : 24 tests inventaire + GET passants, OpenSpec strict4/4 et protocole OK.
Publié dans `f84178bdaa1ed55926f511fc7b41b67e064f9342`, même PR #352, sans UI commité.
Nouvelle CI réelle : `41831604449`, terminée SUCCESS sur `f84178b` : neuf jobs Actions réussis ; SonarCloud Code Analysis SUCCESS sur ce même HEAD. Le run précédent reste FAILURE dans le CR.
La réussite éventuelle de cette CI backend ne prouve pas la WIP mobile, absente du HEAD publié.

## Finalisation — directive et dernier arbitrage opérateur

Le 2026-11-04, la directive de finalisation fixe explicitement l’ordre : mobile complet dans #352,
validation des rendus avant commit UI, checks du HEAD complet, statut GitHub relu, merge sous GO permanent,
GO déploiement distinct, canonique vérifié déployé, Android puis iPhone connecté, closeout/archive sur preuves.
Cette décision lève la contradiction de séquencement signalée par la revue indépendante.
Les mentions historiques d’un arbitrage de séquence en attente ci-dessus sont remplacées par cette décision.

Dernière réponse opérateur : « Conserver zéro ajout sous le bloc ». Aucun ajout sous le bilan.
D-MOB02-3, qui proposait une ligne de contexte factuelle, n’est pas codé par interprétation de cette réponse ;
la clarification du périmètre de ce refus reste attendue. La réception serveur dans le bilan (2.2) reste ouverte.
La restauration, la transmission au vrai consommateur et l’affichage en exécution sont implémentés ;
la simple prop `serverStateOf` du bilan ne satisfait pas une exigence d’affichage.

GitHub relu : canonique `5d87e47dee23be4d71351524ae35ceafd95e0267`,
PR #352 draft, MERGEABLE/CLEAN, HEAD `f84178bdaa1ed55926f511fc7b41b67e064f9342`, aucune revue déposée.
CI `41831604449` : 9/9 jobs Actions SUCCESS et check externe SonarCloud Code Analysis SUCCESS.
Cette preuve valide le backend publié et le mobile antérieur ; les modifications mobiles locales en sont absentes.
Le verdict Sonar canonique historique FAILURE n’est pas réécrit par le verdict vert de cette PR.

La planche consolidée garde les sept scénarios et précise état, delta exact, dimensions et
références verrouillées concernées. Elle reste un candidat soumis ; aucune auto-approbation.
Aucun merge MOB-02, déploiement ou test appareil n’a été exécuté.

## D-MOB02-3 — reprise selon la directive de finalisation

Réponse suivante de l’opérateur : « réfère toi à ma dernière prompt injection ».
La directive MOB-02 FINALIZATION devient la référence pour la suite : ligne de contexte factuelle optionnelle acceptée,
bloc existant conservé, aucun retour au croquis de compteurs de synchronisation.
Brainstorming / options : réintroduire les compteurs rejetés (écarté) ; employer la fréquence déclarée comme activité
(écarté) ; contextualiser le nombre de séances effectivement terminées dans l’historique serveur (retenu).
Choix d’implémentation : période de la semaine UTC, du lundi à la fin de la séance courante attestée par le GET ;
count de cet historique complet uniquement, sans ajouter une séance locale ni lire la fréquence déclarée.
La ligne est omise si la séance courante n’est pas encore dans l’historique, si la page est tronquée,
si les dates/identifiants sont invalides ou dupliqués, ou si la lecture échoue. Aucun jugement ni comparaison.
Plan borné : tests consommateur et vrai rendu rouges, fonction de contexte + câblage minimal, suite mobile et TypeScript,
nouveau rendu réel consolidé avant commit. L’exigence distincte de réception par série du bilan (2.2) reste ouverte.

D-MOB02-3 vérifié : absence de la ligne observée rouge sur le vrai consommateur et le vrai écran
(6 assertions en échec avant câblage, 22 passantes). Après implémentation : 28/28 ciblés,
puis **37 suites / 468 tests mobiles passants**, **TypeScript exit 0**.
Les tests couvrent également page tronquée, séance courante absente, identifiant dupliqué, dates invalides/inversées,
frontière de semaine UTC et passage d’année, exclusion des séances postérieures à la borne attestée,
indépendance de la fréquence déclarée et placement après le bloc existant.
Ce contexte d’activité serveur ne remplace pas la vérité de réception par série exigée par 2.2.

Rendu final D-MOB02-3 montré à l’opérateur en comparaison réelle, dans la planche des sept scénarios.
Nouveaux captures candidats : 7/7 ; gate officielle sur cette dernière WIP : **77/77**, exit 0,
aucune baseline, manifeste ou fixture approuvée modifié. OpenSpec strict **4/4**, protocole et diff propres.
Protection GitHub relue : quatre checks obligatoires toujours actifs (application 15368, strict=false).
Sur le HEAD backend f84178b, les quatre sont SUCCESS ; aucun thread de revue. Aucun commit UI ni CI du mobile complet.
La PR reste draft. Gates immédiates : décision humaine sur le rendu final (§5.1) et conformité de la réception
par série du bilan (2.2). Déploiement non autorisé/non effectué ; Android et iPhone non exécutés.
MOB-02 non fermé/non archivé ; MOB-03 non prêt. Aucun nouveau GO MERGE n’est requis pour une future PR prête.
Une sauvegarde complète de la WIP reste dans `/private/tmp/auren-mob02-finalization-20261104/`.

## LAST MILE — mandat d’exécution et plan 2.2

Mandat opérateur : finir l’ingénierie disponible, une seule demande d’acceptation visuelle finale.
D-MOB02-3 accepté fonctionnellement, sans rouvrir ses décisions. Aucun GO déploiement acquis.
Inspection : CompleteScreen a un bouton « … » ouvrant le journal du labo ; ses lignes exercice sont des View
sans détail interactif. LabSheet expose des mesures techniques, pas les états par série.
Brainstorming / Options / Risques / Choix retenu : ajouter des compteurs permanents (rejeté) ;
réécrire les lignes verrouillées comme accordéons (rejeté) ; réutiliser le bouton « … » et la primitive Sheet
pour un détail de séance (retenu). Le bilan fermé reste identique au pixel ; la feuille groupe seulement les séries
réalisées de cette séance par exercice, avec reçue / en attente / refusée-à vérifier / état inconnu.
Le journal technique existant reste accessible depuis cette feuille. Pas de journal historique MOB-05.
Croquis candidat : bouton existant → « Séries de la séance » [Fermer] → nom exercice → Série 1 + état →
Série 2 + état → … → Journal local existant. La composition sera soumise dans l’unique revue finale
exigée par le mandat, avant tout commit UI ; aucune nouvelle géométrie ou baseline auto-acceptée.

Plan d’implémentation inline (spec : openspec/changes/session-native-integration/specs/mobile/session-integration/spec.md) :
1. Étendre les tests du vrai ConnectedApp pour monter le vrai CompleteScreen, ouvrir le détail et vérifier les
   textes issus du journal persisté : ack, pending/inflight, refus, source absente ; doubles commandes, retry, relance et réponses obsolètes.
2. Étendre l’unique sélecteur serverStateFromOutbox aux états pending/unknown ; conserver l’adaptation de l’exécution
   et ne pas introduire de cache ou source de vérité secondaire. Invalider un résultat devenu non vérifiable après échec de lecture.
3. Ajouter SessionSetDetails (présentation seule, sans I/O), câbler le bouton existant du vrai CompleteScreen ;
   aucune prop de test dans le produit, aucune métrique nouvelle. Tester les vrais états affichés et fermeture.
4. Tests ciblés puis Jest complet / TypeScript, broad ciblé selon check_scope ; revue indépendante des changements
   matériels et correctifs bornés ; rendre les sept scénarios + détail normal/ouvert si nécessaire.
5. Une seule acceptation visuelle opérateur ; pendant son attente finir tests et documentation indépendants.
   Ensuite seulement commit complet, push #352, CI réelle du HEAD complet et merge sous GO permanent si gates satisfaites.
Review focus : une commande locale ne vaut pas ACK ; commande plus récente après ACK ; lecture tardive après erreur ;
source inconnue ; séries d’autres séances ou ignorées ne doivent pas devenir des confirmations de cette séance.

### Résultat technique LAST MILE

2.2 est désormais implémentée : le vrai CompleteScreen ouvre la feuille secondaire depuis son bouton
existant ; chaque série réalisée est groupée sous son exercice et rend son état persisté.
Aucune nouvelle source de vérité : serverStateFromOutbox est l’unique sélecteur, la feuille est une présentation sans I/O.
Aucun ACK pour une commande pending/inflight ; source absente ou dernier restore indisponible → inconnu.
Le journal local existant reste accessible ; aucun détail historique MOB-05, onglet ou compteur permanent ajouté.

Tests RED avant code : six scénarios ConnectedApp + vrai bilan échouaient sur l’absence de l’affordance.
Après câblage : reçue persistée, pending/offline, inflight, refusée, source inconnue, retry après refus sans doublon.
Compléments : ancienne commande ACK suivie d’un nouvel envoi, réponse tardive après indisponibilité,
absence d’invention d’une série non réalisée. RN Pressability est actionné via son événement réel d’accessibilité ;
seule la présentation modale native est remplacée dans Jest, pas CompleteScreen, IconButton ou SheetRow.
Le scénario navigateur ouvre et ferme la vraie Sheet, sans mock de présentation.

Revue indépendante du change complet : aucun Critical signalé ; un Important de course de substitution.
Reproduction : refus A persistant, lecture A différée, nouvelle demande B identique pendant enqueue,
puis ancienne réponse qui supprimait le verrou de B. Test rouge sur requiresSync devenu undefined.
Correctif borné : invalider les lectures avant la mutation et à la fin de la persistance ; ne pas réconcilier
pendant les écritures en cours. La réponse complète ExecutionPlan de B remet ensuite le plan canonique.
Le test utilise des UUID uniques à la frontière native, conformément au contrat de production.
Résultat final après correction : **37 suites / 478 tests mobiles passants**, **TypeScript exit 0**.
Route GET + inventaire revérifiés : **24/24** ; deux dépréciations dépendances préexistantes, pas d’échec.
Ruff concerné propre ; budget **264 ≤ 548**, scope **ISOLATED**, pas de full sweep local.

Rendus : sept scénarios conservés + seul détail normal/ouvert requis par §3 du mandat, huit captures
candidats passantes ; contrôle navigateur des quatre états et de fermeture. Le PNG du bilan normal de
ce scénario est identique octet pour octet au canonique avant. Aucun fichier de baseline ou manifeste modifié.
L’acceptation visuelle unique est demandée ; elle seule est attendue avant commit UI.
Les autres opérations indépendantes continuent ; aucun succès de CI mobile publiée, merge, déploiement
ou recette appareil n’est revendiqué pour cette WIP encore non commitée.

### Vérifications indépendantes achevées en attente de la revue visuelle

Gate finale : 77/77, exit 0 dans l’image Playwright verrouillée. Exports natifs du vrai chemin connecté iOS et Android réussis (Metro/Hermes, Node 22.20.0, deux workers). Ce ne sont ni des installations ni des recettes appareil. Simulateur disponible : iPhone 17 Pro / iOS 26.3, sans recette revendiquée.

### Déploiement et rollback — préparation sans exécution

Après merge : relire le SHA canonique complet et sa CI, enregistrer le client compatible et capturer la révision effectivement déployée pour rollback avant de demander le GO distinct.
Workflow existant Deploy production : ref=SHA complet, skip_smoke=false, approbation de l’environnement production. Aucun dispatch à ce stade. Vérifier smokes, tag deploy/prod et révision réellement servie.
Rollback : même workflow sur previous_sha de var/deploy_state.json ou dernier tag vérifié (CICD_RUNBOOK §§5–6). Aucun rollback de DB ; MOB-02 n’a aucune migration.

### Checklist appareil consolidée — après déploiement compatible

Compte de recette prévu ; relever backend SHA, client SHA/build, OS/modèle et appareil physique ou simulateur.
1. Démarrage lent : marque seule, puis vraie route.
2. Démarrer/Reprendre : double appui, un seul démarrage ; nouvelle tentative après échec.
3. Série acceptée : fermeture forcée, relance, état reçu dans exécution et détail du bilan.
4. Hors ligne : persistance, relance, attente distincte de reçu ; retour réseau sans doublon.
5. Refus : à vérifier, conservation locale, retry et accusé réel.
6. Substitution : hors ligne, refus et origine praticable ; ACK suivi du plan canonique ; lectures retardées ou coupées.
7. Bilan : ouvrir/fermer le détail ; quatre états selon les faits ; aucune confirmation inventée ; valeurs absentes omises ; période UTC de D-MOB02-3.
8. Repos : anneau, ±15 s, notification ; safe areas, clavier, retour Android.
9. Export de preuve existant, captures et observations ; un scénario non obtenu reste non vérifié.
Ordre : Android puis iPhone connecté. Aucune passe physique cochée sans exécution réelle ; aucune archive avec gate appareil manquante.
MOB-03 : préparer les artefacts OpenSpec après merge depuis MOB-00 ; aucun build de sémantique ou surface non approuvée.

## Acceptation visuelle — 4 novembre 2026

L’opérateur a répondu exactement « ACCEPT — rendus MOB-02 complets » à la revue consolidée unique : sept scénarios corrigés, ligne D-MOB02-3 et détail des séries normal/ouvert par le bouton existant.
La gate CLAUDE.md §5.1 est satisfaite avant commit UI. Aucun nouveau baseline ni manifeste n’est créé ou approuvé automatiquement. Les fichiers mobiles sont identiques à ceux rendus et testés lors de la soumission.
Les décisions applicables §5.2 restent relues dans le tableau de ce rapport ; D-MOB02-1/2/3 respectées. Composition du bilan fermé conservée, détail secondaire accepté, données sourcées ou omises.
Le GO MERGE permanent reste actif ; publication complète dans #352 puis CI réelle sur son HEAD final. Deux tâches post-merge restent ouvertes : déploiement compatible 3.2 et recette Android/iPhone 4.2. Ne pas archiver avant leurs preuves.
