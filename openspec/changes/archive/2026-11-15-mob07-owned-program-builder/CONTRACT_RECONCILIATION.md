# MOB-07 — amendement explicite proposé des préconditions d’écriture

15 novembre 2026. PROPOSED, pas appliqué. Ce document accompagne le même GO BUILD/G1 demandé, sans rouvrir les décisions scientifiques ou les scopes livrés.

| Autorité actuelle | Conservé | Nouveau contrat soumis dans MOB-07 |
|---|---|---|
| Sx_CUSTOM_PROGRAM_04, UserProgram* | Source d’édition, owner, quotas, statut, nomEKB figé, zéroFK versEKB/catalogue | Table additive de reçus techniques, pas nouveau programme numérique |
| Services user_program_drafts / quality_reviews / publish / versioning | Règles métier, snapshots et templates immuables, validation≠publication, cycle mono-row | Hooks transactionnels internes, kernel commun et commit atomique source+review+templates+reçu |
| Router/formulaires web actuels | Routes, affichage, saisie libre et génération existante ; aucun moteur modifié | Précondition de source de la vue rendue pour tout writer d’arbre/statut ; un ancien formulaire sans jeton doit être relu |
| Picker web historique | Texte libre permis ; aucun remapping de ses anciens slots | Le nouveau picker natif exige une identité résolue pour les ajouts/remplacements seulement |
| Publication existante | Grade/qualité calculés par le serveur existant, jamais nouvelle admission SCI | Atomicité de la trace et de la matérialisation, pas modification des formules ni grade comme permission scientifique |
| MOB-06 | API et départ contrôlé, UNKNOWN, gates Legacy/V3, journal et historique | Readback du nouveau programme par les mêmes consommateurs ; pas second départAPI |

**Impact intentionnel à approuver :** une page web rendue avant un changement concurrent (ou avant l’ajout du jeton) ne peut plus remplacer l’arbre silencieusement. Source périmée→409 ; précondition absente→428/relecture via le rendu d’erreur existant. Les scénarios de succès web existants gardent leurs faits et transitions. Ceci est un amendement de protocole, pas une compatibilité wire inchangée prétendue. Les tests web doivent obtenir le vrai jeton depuis GET, jamais le désactiver.

Le replay d’une commande native déjà reçue reste vérifié par owner/clé/hash avant les permissions de mutation fraîche. Il rend un reçu historique, pas la preuve que le programme est encore lançable. Les branches HEAD BODY/NUT/408/411 et leurs contrats restent intacts. Les cibles tactiles et éventuels messages SSR modifiés gardent leur preuve/gate applicable ; aucun changement silencieux de baseline.

Les déclarations SPEC_ONLY/BUILD_NOT_AUTHORIZED des anciennes specs de juillet décrivent leur étape historique ; les services canoniques sont déjà livrés et testés. Le nouveau scope est borné par ce paquet, son GO propre et la protection des templates/historiques existants. Aucun ancien GO n’est substitué au nouveau.
