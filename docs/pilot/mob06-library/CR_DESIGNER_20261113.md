# AUREN — CR de continuation et passation au designer

**13 novembre 2026 — opérateur, designer et architecte/PO.**

**Le MVP n’est pas terminé. Les métiers BODY/NUT et la bibliothèque sont conservés ; l’assemblage mobile a progressé en copie isolée. Les masters BODY et Programmes, leurs validations natives et la release restent ouverts.** Ce CR est final pour cette passation, pas un reçu de clôture du produit.

## 1. Ce qui est réellement acquis

Canonique fetché : **`1462482a4e2bcd1fcde121d6f207a2131616e849`**, dépôt `MFE-DSS/workout-session-tracking`. MOB-04 et MOB-05A sont déjà fusionnés. Les travaux ci-dessous restent non committés dans leurs branches conservées ; aucune nouvelle PR produit, CI distante, fusion, APK, OTA ou activation n’a été effectuée pendant cette continuation.

| Voie | État réel | Sortie encore attendue |
|---|---|---|
| BODY-01 | Domaine, correction avec original conservé, migration additive, API et reprise SQLite récupérés ; GO métier/amendement/G1 acquis | Master externe accepté ; reconstruction fidèle, preuve native complète et gates finaux |
| NUT-01 | GO **technique** acquis ; journal manuel, cibles déclarées, accord distinct et reprise développés ; modules natifs éprouvés | Parent/migration intégrables, sweep final ; composition/G1/pixels et consommateur ConnectedApp complet |
| MOB-06 | Lectures et départ contrôlé, journal propriétaire, adaptation Programmes→Today et reprise éprouvés en candidat | Application aux parents vérifiés, master Programmes/pixels, CI et livraison |
| MOB-07 | Suite du mandat, non implémentée dans cette passe | Plus petit constructeur sur identités et structures existantes, scope/gates propres après MOB-06 |
| REL-03 | Préparation de distribution existante ; aucun nouveau candidat distribué ici | Qualification/autorisation du QA séparé sur infrastructure existante, compatibilité et recette installée |

Autorisations conservées : BODY `call_106057b169a74bc9887b1fea9f527f5d`, NUT technique `call_c1496d1a84e04b1a8dd61ad04f063aa6`, MOB-06/G1 `call_4321044cec284c79898cb7d2dd483990`. Aucun de ces GO ne vaut acceptation du nouveau master ou permission de déploiement. Aucun GO métier ou merge routinier n’est à redemander.

## 2. Travail poursuivi depuis le dernier jalon

Le patch MOB-06 de **13 chemins** est conservé avec ses empreintes et passe `git apply --check` sur la branche `feature/bibliotheque-seances`. Il n’a pas été appliqué par-dessus les fichiers réservés BODY/NUT.

Les **cinq fichiers en conflit textuel** ont maintenant une proposition d’assemblage : ConnectedApp, journal natif, types du journal, routeur mobile et configuration. Ce sont des conflits d’ajouts simultanés ; leurs résolutions sont préparées, sans supprimer de port BODY ou bibliothèque. Les fichiers serveur sont des **prévisualisations syntaxiques**, pas un backend combiné activé. La relecture indépendante ciblée ne relève pas de régression nouvelle ; elle a rejoué 11 tests sur trois suites et relu les deux prévisualisations serveur sans les importer.

Une copie mobile combine les sources BODY conservées, le candidat MOB-06 et les modules NUT indépendants. **106 suites / 1 276 tests et TypeScript passent** sur cette copie. Un nouveau témoin SQLite vérifie les intentions BODY et bibliothèque concurrentes, leur relecture, l’isolation A/B et la conservation de l’état V3 sans série fabriquée. Ce test utilise SQLite réel via l’adaptateur OS de test ; ce n’est pas une recette physique.

Le candidat MOB-06 précédent dispose séparément de **152 tests backend broad passants**, dont relecture du même identifiant par Mission, exécution et historique ; **1 200 tests mobiles**, revue d’intégration corrigée, contrôles statiques et OpenSpec 25/25. Ces résultats ne deviennent pas une CI du nouvel assemblage et ne s’additionnent pas aux 1 276 tests.

BODY conserve sa campagne composée du 12 novembre : 8 562 backend passants / un ignoré, complétée par 18 SSR et quatre témoins Chromium ; ils n’ont pas été rejoués ici. NUT conserve ses preuves de modules et reprise native synthétique, mais son sweep global a été interrompu avec le drift connu d’une migration encore draft. Le graphe de migrations composé a été éprouvé séparément sur copie synthétique ; son parent n’est pas fusionné. Aucun de ces faits ne clôt une release.

**Les assemblages ne sont pas des arbitrages artistiques.** Ils restent à appliquer et revérifier sur les parents canoniques après libération des leases. Les worktrees, les travaux uniques et le checkout opérateur sont préservés.

## 3. Commande au designer : deux masters complémentaires

L’étude externe BODY est **conservée mais NON ACCEPTÉE**. Les itérations autonomes de pixels BODY restent suspendues. Les anciens rendus DA-06 ne sont pas des masters de production. Le rendu fonctionnel actuel de Programmes reste une liste de raccordement ; il n’est pas proposé comme direction finale.

Produire **une direction cohérente, matérialisée par deux compositions maîtresses** :

**BODY — instrument personnel de mesure.** Un écran complet articule lecture du dossier, instrument sélectionné et acquisition de ce même objet. La mesure, sa mémoire et sa provenance doivent sembler appartenir à un seul instrument. Montrer repos, acquisition avec place réelle du clavier, puis confirmation serveur. Correction et original/version restent accessibles ; un côté absent demeure inconnu. Une mémoire insuffisante ne reçoit ni tendance inventée, ni score, ni recommandation corporelle.

La cible reste l’« instrument scientifique européen haut de gamme », avec une interface industrielle de précision adaptée au smartphone, reconnaissable sans textes.

**Programmes — instrument d’organisation de l’entraînement.** L’objet consulté et sa structure doivent dominer la lecture ; les séances sont des modules ordonnés sélectionnables et leurs actions restent dans leur contexte. Montrer bibliothèque/choix, programme publié et séances, séance sélectionnée avec départ explicite, puis départ à vérifier et reprise. Éviter grandes cartes répétées, liste de fichiers, dashboard décoratif ou bouton global « démarrer le programme ».

**Limite décisive de données : le domaine courant ne possède ni programme actif persistant ni affectation aux jours de semaine.** Montrer un *programme consulté* et l’ordre réel de ses séances. Ne pas transformer la première entrée en programme actif, ni les positions 1/2 en lundi/jeudi. Une véritable allocation hebdomadaire exigerait un contrat produit distinct ; elle n’est pas nécessaire pour concevoir ce master honnêtement.

`BODY_CONTENT.json` conserve le snapshot synthétique du brief existant. `PROGRAMMES_CONTENT.json` provient d’une lecture du vrai domaine sur la base QA synthétique, ouverte en lecture seule et inchangée : un programme VALIDATED, un PUBLISHED, chacun avec deux séances et quatre séries prescrites. Les références de routage signées ont été retirées du paquet. Aucun de ces contenus n’est une prescription nouvelle ou une donnée humaine.

## 4. Contraintes de composition et de vérité

- Canevas principal **390 × 844 pt** ; prévoir Android 360/480 dp, fonte agrandie et défilement. Coter séparément dessin et cible tactile **48 × 48**. Pas de hauteur fixe qui tronque un nom long, une unité ou une action obligatoire.
- BODY s’ouvre depuis Profil/Progrès au-dessus du shell avec retour au parent. Programmes conserve les **quatre onglets natifs D4**. Aucun cinquième onglet ; ne pas refaire MISSION ou l’exécution.
- Réemployer les géométries exactes **Frame C, RecessedWindow, NumericReadout**, marque et tokens. La sophistication doit venir de la composition, des alignements, de la typographie et des transitions d’attention. Une éventuelle évolution d’une primitive LOCKED se présente comme delta séparé, jamais comme remplacement silencieux.
- `field/plate/ink` structurent les surfaces ; **signal** désigne l’action courante de l’athlète ; **system** une information réelle du moteur. Une saisie manuelle enregistrée ne devient pas bleue par sa seule sauvegarde. Aucun nouveau code couleur scientifique.
- Le rail horizontal reste une référence de famille géométrique. **Aucun EASY/TARGET/PUSH, optimum corporel ou jauge de charge** sans contrat et bornes applicables. BodyMap uniquement depuis les zones réellement disponibles sous son contrat ; l’exercice synthétique non cartographié n’acquiert pas de zone décorative.
- Distinguer brouillon, préparation durable, envoi incertain, reçu exact et relecture. Une animation ne confirme pas une mutation. Dans la bibliothèque, reprendre une séance possédée ne certifie pas la création initiale dont la réponse a été perdue.
- Distinguer séries prévues et faits exécutés ; charge machine, kg par haltère et masse externe totale ne sont pas interchangeables. Aucun nombre manquant n’est remplacé par zéro.
- Les détails avancés se divulguent progressivement ; un blocage, l’incertitude ou un accord obligatoire ne disparaît pas. Une information possède un seul porteur principal.

Les références Oura/Instrument, Tonal, Linear et MacroFactor expriment les intentions données par le PO : profondeur de lecture, commandes intégrées, précision de finition, économie de gestes. Elles ne donnent pas permission de copier leurs écrans, palette, scores ou cadrans. Les fichiers AUREN joints restent les références de reconstruction.

## 5. Réponse attendue, regroupée en un seul retour

Le designer peut répondre avec un paquet unique :

1. **Composition choisie pour BODY et Programmes**, avec relations entre châssis, objet actif, mémoire/structure et action. Justifier les proportions ; ne pas seulement réduire les boutons.
2. **Cotes et typographie** : grille, marges, alignements, tailles/poids/interlignages, unités, zones tactiles, frontières du clavier et des safe areas. Toute exception aux primitives est isolée et motivée.
3. **États et transitions** : éditer/annuler/confirmer/corriger pour BODY ; sélectionner/consulter/démarrer/vérifier/reprendre pour Programmes. Fournir le comportement sans historique, vide confirmé, lecture précédente hors ligne, inconnu, indisponible et fonte agrandie. Le prochain geste doit rester évident.
4. **Sources éditables et planche comparative** : les mêmes données et dimensions entre états, références acceptées à côté, silhouette sans textes/chiffres, ordre de lecture/focus. Le test de silhouette ne remplace pas les libellés accessibles.

Le premier jugement porte sur ces masters reconstructibles. Après acceptation opérateur : Codex reproduit les géométries, branche les consommateurs existants et soumet les **vrais pixels natifs**. L’acceptation artistique externe ne vaut ni test d’appareil, ni baseline mise à jour, ni acceptation automatique de la reconstruction.

Nutrition n’est pas un troisième chantier artistique à ouvrir ici. Prévoir la transférabilité des règles, tout en conservant quatre mesures typées par journée, inconnus distincts de zéro, cibles déclarées et complétude explicite. Son G1 et ses pixels resteront propres à sa tranche ; aucun objectif calorique ou macro par défaut.

## 6. Besoins d’ingénierie et de release — hors décision du designer

| Besoin | Traitement et preuve encore nécessaires |
|---|---|
| Parents et leases | BODY/NUT ne sont pas fusionnés. Résolutions conservées en copie ; application séquencée puis tests des vrais parents, revue et CI exactes. Le designer n’arbitre pas le contenu des fichiers Git. |
| Nutrition | Activer son graphe de migration après parent vérifié, terminer sweep/drift et attachement au journal ; aucun backend complet déclaré vert depuis les seuls tests mobiles. |
| Recette native | Rendu ConnectedApp iOS obtenu. Pilotage CUA interrompu par `noWindowsAvailable` ; reflow/grande fonte/safe areas et parcours tactile complet restent à vérifier. Android Expo Go reste incompatible avec le module natif conservé ; utiliser une cible compatible lors de l’intégration, sans retirer le module. Physique séparé. |
| DATA | Accords de domaine, copies terminales/sauvegardes, export/effacement et conditions de traitement réel ne se déduisent pas d’un test synthétique. Aucun traitement réel nouveau n’est autorisé par ce CR. |
| QA stable | Réemploi OVH existant préféré par l’opérateur. Pas de service stable/cutover/DNS autorisé ou vérifié dans cette passe ; ne pas relancer Render ou un tunnel temporaire comme solution définitive. |
| Candidat Android | Consolider les slices réellement fusionnés, API/schéma/runtime, bundle SCI/génération, signature/upgrade/rollback et smoke installé. Pas d’APK par merge. Release et OTA exigent leur autorisation opérationnelle distincte. |

Ordre de continuation : finaliser les travaux métier indépendants et préparer l’assemblage ; obtenir les deux masters ; intégrer leurs compositions selon leurs gates ; tests/revues/CI/merges sous GOV-MERGE-01 ; puis candidat MVP consolidé et recette autorisée. MOB-07 utilisera les structures et identités canoniques, sans prescription scientifique inventée dans le client.

La file illustrative demeure indépendante : **master BODY externe → mannequin canonique productible → Smith incliné START/END → fiche exercice native pilote → sept Push A → équipements/catalogue ; MOTION-V2 différé**. Le master Programmes accompagne le produit ; aucune image anatomique nouvelle n’est requise pour livrer MOB-06. Le lot Push A n’est pas le lot des sept calibrages.

**Sortie de cette passe : assemblage mobile préparé et testé, contenu de design fourni, décisions artistiques regroupées. Aucun nouveau master accepté ou produit livré implicitement.**
