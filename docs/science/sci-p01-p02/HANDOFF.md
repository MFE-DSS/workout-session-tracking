# Handoff SCI-P01 / SCI-P02 → produit/mobile/API

**Paquet :1.0.0 — 5 novembre 2026. Producteur : agent science/contrats. Consommateurs : agents MOB-03, MOB-04 et architecte API.**

| Livrable | Statut de l'artefact | Disponibilité producteur réelle | Avertissement |
|---|---|---|---|
|BodyTrainingBlueprint 1.0.0|READY pour revue/intégration de contrat après livraison vérifiée|NOT_SERVED ; aucune API/persistance Blueprint ajoutée|Le profil d'exigences `first-bodybuilding-inputs-v1-proposed` est une proposition de collecte, pas une mesure d'aptitude |
|FirstPlanRequest/Recommendation 1.0.0|READY pour vérifier les échanges et leurs fixtures|BLOCKED pour un premier plan réellement produit : politiques et adaptateur manquants|READY du **paquet** ne signifie pas qu'un plan porte le statut READY |
|Fixtures et DTO|READY, données synthétiques et un extrait historique non validé|Aucune requête de compte, aucun stockage ou endpoint|Tous les exemples publics sont NOT_SERVED ; la fixture suffisamment renseignée rend POLICY_UNAVAILABLE |
|Premier plan utilisable end-to-end|BLOCKED|Aucun moteur SCI-P02 branché|Requiert politiques validées, fixture READY du vrai producteur et tests consommateurs avant exposition |

## À consommer dès maintenant

1. Les trois [JSON Schemas](v1/) et le [contrat humain](CONTRACT.md), pour préparer un consommateur isolé et ses états, sans changer de composition mobile ici.
2. Les [huit fixtures](v1/fixtures.json) : sufficient, insufficient, conflicting, unknown_gym, optional_conflict, withheld_required_input, undated_legacy_weight et legacy_candidate_requires_policies_and_review.
3. Les règles de provenance : déclarations distinctes d'observations, mesure datée distincte d'héritage, inconnu distinct de vide, réponse individuelle non estimée, incompatibilité distincte de disponibilité inconnue.
4. Les versions/empreintes du [manifest](manifest.json) et le contexte scientifique actuel dans [l'audit](AUDIT_AND_EVIDENCE.md).

Le JSON Schema valide la structure ; les invariants d'échange utilisent `validate_exchange` et un ReferenceSnapshot construit côté producteur depuis les sources autoritaires. Ce n'est ni une fonction mobile à recopier, ni une autorisation d'activer un plan. Les DTO n'authentifient personne : les gardes Bearer/propriétaire/consentement doivent être appliquées par le futur adaptateur.

## Dépendances — ordre par décision débloquée

| ID / statut | Producteur → consommateur | Source réelle / ce qu'il faut livrer | Repli honnête |
|---|---|---|---|
|D01 / PARTIAL|Compte/données → Blueprint|TrainingPreferences existant ; déclarations JSON dans PR353 ; taille/poids et consentement via User/BodyMeasurement/body_profile. Manquent stockage/API de disponibilité temporelle, expérience, limitations et contexte du nouveau snapshot|Snapshot de contrat synthétique ; aucun formulaire qui prétend sauvegarder les nouveaux champs |
|D02 / BLOCKED|Science dose initiale → premier plan|Audit des18 gabarits, baseline11 zones et preuve générale disponibles. Revoir admissibilité des archétypes, dose initiale et effort/calibration par profils de contraintes ; traiter explicitement expérience inconnue|POLICY_UNAVAILABLE, pas de nouvelle mensuration demandée pour masquer le manque de politique |
|D03 / BLOCKED|Science + architecte temps → premier plan|Session.duration_target_minutes est une cible de programme, pas disponibilité personnelle. Modèle de durée avec composantes/borne/incertitude à définir et valider|Budget déclaré conservé ; estimation UNKNOWN. Le titre « 45 min » du catalogue ne suffit pas |
|D04 / BLOCKED|Taxonomie/exposition → allocation|Catalogue15 zones et crédit `sci-exposure-credit-v1` existants ; planificateur servi11 zones/set_contribution. Projection ou remplacement explicitement approuvé, sans posterior→hamstrings/glutes implicite|Ne pas certifier une allocation15 zones depuis le seul budget11 zones |
|D05 / PARTIAL|Catalogue/identité → slots/candidats|107 fiches/84 identités canoniques, alias traçables ; intentions existantes à relier explicitement aux15 zones et à l'archétype admis|Identité/exigence/role inconnu reste inconnu ; pas de candidat ou d'intention inventés pour combler un trou |
|D06 / BLOCKED pour extension|Domaine environnement/substitution → propositions|Gardes et niveaux existants servis ; inventaire absent historiquement non appliqué. Définir confirmation au niveau exercice/contexte, sa validité et le comportement après substitution, sans inventaire obligatoire|UNKNOWN et revue/substitution contextuelle ; aucune chaîne de salles réputée entièrement équipée |
|D07 / BLOCKED|Producteur API → mobile|Implémentation SCI-P01/02, versions, snapshot propriétaire/consenti, fixtures issues du vrai producteur et compatibilité ; l'intégration demande son propre delta OpenSpec|MISSION et services actuels inchangés ; aucun nouvel endpoint promis |
|D08 / OPEN produit|PO/opérateur/architecte → collecte et données|Population d'usage adulte/non clinique, collecte progressive, gestion des conflits, consentement/poids hérités, conservation et confidentialité|Ne pas ajouter de questionnaire médical ni de collecte sans finalité par défaut |

## Arbitrages opérateur nécessaires avant le premier moteur

- **O1 — profil de collecte et population :** confirmer le cadre adulte/non clinique et le caractère progressif de taille/poids/expérience. Le contrat propose cadence, budgets et réponse sur limitations comme minimum de planification ; il ne les a pas persistés. Si un autre profil est choisi, versionner son identifiant et ses fixtures, sans convertir un inconnu en fait.
- **O2 — politique de dose :** ouvrir une proposition scientifique ciblée pour l'admission d'archétypes et la dose initiale, avec le cas froid/expérience inconnue. Choix à éviter : emprunter automatiquement 148 cibles de zones ou 24 séries par séance au motif que le code les utilise déjà. La littérature est un prior de groupe, pas une validation de ces nombres exacts.
- **O3 — temps et compatibilité :** approuver la méthode d'estimation et de confirmation en contexte ; une borne non vérifiée n'est pas une promesse de durée, une absence d'inventaire n'est ni une salle vide ni une salle complète.
- **O4 — intégration et données :** faire produire les lectures/écritures réelles de nouveaux faits avec ownership et consentement ; coordonner avec D-MOB03-2/3 et STORE-00. Aucune action destructive ou migration autorisée par ces contrats.

Le prochain spike scientifique recommandé est **SCI-P02-INITIAL-POLICY** : « Quelle politique initiale de dose/effort peut-on justifier pour un plan d'hypertrophie sous cadence et temps déclarés, avec expérience éventuellement inconnue ? » Il doit choisir des archétypes audités, expliciter conventions/preuves, fournir une vraie fixture READY et un modèle de temps séparé ou déclarer son blocage. Ne pas ouvrir toute l'autorégulation, récupération ou Body Intelligence en même temps.

## Frontières de collaboration

Aucun fichier UI, baseline, modèle/table partagé, endpoint ou référentiel scientifique existant n'est modifié. Le manifeste est copié **identiquement** depuis la PR353 car absent de la base canonique ; un merge ultérieur de la même copie ne doit pas créer une deuxième doctrine. Risque de collision restant : ajout proche dans SPEC_REGISTRY ; conserver les lignes de l'autre change. Les futurs adaptateurs toucheront training_preferences/mobile_read_models/API, donc vérifier status/diff avant ces writes et annoncer producteur/consommateur/versions.

Les nouveaux champs et statuts sont une proposition versionnée qui ne remplace pas les contrats web/mobile actuels. Changement de sens de provenance, taxonomie, statut ou suffisance = changement incompatible à annoncer ; pas de réinterprétation silencieuse d'une recommandation historique. Aucun message externe n'a été envoyé ; le dépôt porte le handoff.
