# Projection publique V3 — plan d’exécution et preuves

27 novembre 2026. Parent 1ac401f44b8af9444a8521b30cd47b7201fd1c8e. GO exact : AUTHORIZATION.md.

## Brainstorming / Options / Risques / Choix retenu
L’analyse et les options de BUILD_AMENDMENT.md sont conservées : projection explicite après vérification complète, sans changement de writer/DTO/SCI. Risque : masquer un champ ou une identité contradictoire ; tests négatifs obligatoires.

## Plan borné
1. Tests RED unitaires six/cinq propriétés, identité contradictoire et champ inconnu.
2. RED du readback des vrais services inventory2 → évaluation → START → 14 SET → FINISH.
3. Correction dans provenance.py uniquement ; GREEN ciblé puis broad consommateurs selon check_scope.
4. Banc Linux/amd64 du code corrigé : nominal, mixte100, propriétaires, absence de bundle et ressources ; ancienne image non mise à jour.
5. Revue indépendante du diff entier, sécurité/spec, PR/CI HEAD exact, merge/CI canonique, archive et nettoyage borné.

## Rulings
- Le diff ne touche aucune surface UI : pas de nouveau gate pixels.
- Les tests locaux peuvent utiliser l’environnement existant Python3.14.7 ; ils ne qualifient pas le runtime Linux3.11.14. Aucun environnement partagé n’est modifié.
- RTK.md absent dans le worktree et les chemins usuels vérifiés ; aucun remplacement du contrat par une hypothèse.
- La requalification par source corrigée montée readonly ne devient pas une qualification d’image de déploiement.

## Résultats
En cours ; aucun PASS final ni fusion revendiqués.

### Checkpoints locaux
- RED : 6 échecs/2 PASS sur projection six propriétés et contradictions ; 1 échec du vrai parcours inventory2 après14 SET/FINISH, `invalid_observed_load_response`,507,83s (Python3.14.7).
- GREEN provenance :38 tests PASS sur Python3.11.14 ; parcours complet et broad encore en cours à ce checkpoint.
- Revue indépendante fraîche du diff entier : aucun Critical/Important/Minor ; aucune exécution lente ou mutation par le reviewer. Readiness conditionnée aux autres gates effectives.
- Ruff fichiers modifiés/neuf, budget, protocole, Bandit, OpenSpec strict et diff-check PASS. Première invocation du budget sans Ruff dans PATH refusée par outillage, puis invocation correcte réussie ; aucune règle modifiée.
- Gitleaks sur documents nouveaux : PASS. Scan exhaustif des1370 commits de l’ascendance : trois findings historiques conservés (deux exemples documentés admin:admin et un identifiant d’issue Sonar, objet avec issueStatus/component/line/message). Aucun credential nouveau démontré ; ce scan exhaustif n’est pas déclaré vert. Aucune exception, baseline, règle ou `.gitleaksignore` modifiée. Le delta exact livré sera scanné séparément et la CI protégée reste obligatoire.

Broad local Python3.11.14 :109 PASS/4 SKIP existants/1 warning,177,79s ; modules reader/worker/contrat/catalogue/projection/HTTP et consommateur execution. Les SKIP ne sont pas créés par cet amendement ; leurs limites seront distinguées de la campagne Linux native.

Ruling : le binding du fait doit être comparé au binding d’exécution retourné par GET execution, et non au binding de politique de la recommandation. Les deux autorités sont distinctes ; assertion du nouveau test corrigée, sans modification de domaine. Le run déjà chargé garde sa version originale et sera conservé séparément.

### Préparation du checkpoint local et du banc
Le run Python3.11.14 initial termine effectivement avec38 PASS et1 échec de l’assertion de test erronée (digest de politique au lieu du binding d’exécution),588,10s. Aucune tentative de signal ne l’a atteint : il avait déjà terminé normalement. Le test corrigé est rejoué intégralement sur Python3.14.7. Le checkpoint local sert à pinner les octets de code du banc ; il ne constitue ni publication, ni fin de vérification, ni qualification. Aucun push avant ses résultats effectifs et la campagne native.
Le broad3.11.14 a terminé exit0 après sa collecte finale GC lente ; une répétition devenue inutile a été interrompue sans changement de test.

### Garde disque avant banc
Après création du payload privé39Mio, le Mac ne présente plus que20950204416octets libres (19,511Gio), contre21474836480requis : manque524632064octets. Précondition de mutation OPERATIONAL_DELTA§9 non satisfaite. Aucune création distante ni transfert de cette nouvelle campagne ; payload conservé, garde non abaissée. Demande de libération1Gio à l’opérateur pendant poursuite des contrôles indépendants.
Relecture complémentaire indépendante de l’assertion binding : pairing execution.binding_digest/provenance.binding_digest confirmé ; aucun autre décalage identifié.

### GREEN intégré et reprise du banc
Le test complet corrigé passe sur Python3.14.7 :1 PASS,267,52s. Il vérifie14 SET issus des vrais services, reçus rejoués exacts, FINISH, identités et rôles attestés, contexte public fermé, digest indépendant, historique mixte100 et compte vide, observations historiques inchangées. Avec38 unitaires et109 broad,148 tests PASS ; quatre SKIP Linux préexistants restent nommés.
L’espace Mac est remonté à21,798Gio sur nouvelle mesure, sans nettoyage supplémentaire par cette passe. Le garde20Gio passe ; nouvelle source26c6356 montée readonly sur l’image existante dans un banc neuf autorisé. Cela ne qualifie pas une nouvelle image de déploiement.
Gitleaks du commit exact1ac401f..26c6356 : PASS ; les trois findings historiques hors delta restent consignés sans exception nouvelle.

### Revue Sonar sur d8ab972
Les11jobs CI46026703302 passent, dont les4protégés. Le check externe SonarCloud Code Analysis est ERROR avec4MAJOR S9073 dans les seules nouvelles assertions de tests. Correction bornée :séparer les4assertions composites, sans modifier leurs expressions ou leur ordre ; équivalence AST vérifiée après aplatissement des assertions AND. Aucun produit ni profil scientifique modifié ; qualification native conservée par identité des1696fichiers source. Les tests de provenance sont rejoués et la CI complète du nouveau HEAD doit repasser ; pas de nouveau broad local redondant pour cette seule clarification. S8707 relu vivant OPEN/MAJOR, non modifié.
