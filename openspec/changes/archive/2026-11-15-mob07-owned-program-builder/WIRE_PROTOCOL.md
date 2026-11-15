# Protocole MOB-07 proposé — non implémenté

Version proposée program-builder/1.0.0, en-tête X-Auren-Program-Builder exact, Bearer owner serveur/no-store. Préfixe /api/mobile/v1/me/program-builder.

| Méthode / suffixe | Rôle proposé |
|---|---|
| GET /exercises | Picker borné/paginé, intersection identitéExercise et nomEKB exact, provenance/version |
| GET /programs | Index propriétaire borné des brouillons et programmes, watermark cohérent |
| GET /programs/{program_id} | Arbre courant, état/version/publications et digestCAS, slots manuels historiques identifiés |
| POST /commands | CREATE, SAVE_TREE, RENAME, VALIDATE, PUBLISH, NEW_CYCLE ou ARCHIVE explicites |
| GET /operations/{command_id} | Reçu exact propriétaire,404étranger=inconnu, jamais permission nouvelle |

Commande : command_id stable, operation, program_id saufCREATE, expected_source_digest saufCREATE, payload exact typé. SAVE_TREE contient séances/positions, mouvements identifiés ou slots historiques inchangés et séries/plages choisies ; aucune observation ou charge totale déduite. Le serveur calcule les textes set_scheme à partir des prescriptions explicites sans ajouter de conseil. Nombre/plages validés par les mêmes contraintes existantes, sans changement silencieux de limites.

Reçu technique : owner vérifié serveur, command_id, request_sha256, operation, program_id, resulting_source_digest, resulting_version, publication ids/selection provenance selon opération. Pas de copie numérique canonique de prescription dans la table de reçus. GETprogramme porte les valeurs actuelles ; le reçu historique ne les recrée pas après changement.

Unique(owner,command_id), mêmeclé/autrecorps409 ; exactreplay retourne le reçu sans réévaluer une permission fraîche. Si mutation nouvelle, relectureCAS et quota propriétaire dans une section sérialisée, transformations et reçus dans la même transaction. SQLite est la cible QA actuelle : writer sérialisé sur vraie connexion ; aucune qualification PostgreSQL implicite. Les hooks internes commit=False ne sont qu’un mécanisme, pas une preuve d’atomicité : freeze qualité, matérialisation, source et reçu doivent avoir un seul commit vérifié par injection de panne.

Les writers web passent par ce kernel et un digest de formulaire, gardent leur texte libre et leurs messages métier. Digest absent ou périmé : refus de précondition/relecture, aucune reconstruction d’arbre depuis une ancienne lecture. Les slots historiques non résolus peuvent rester inchangés avec owner/slot/digest/contenu vérifiés, mais aucun nouveau slot natif arbitraire n’est accepté.

Stockage local proposé program_builder_pending_commands_v1 sur journal possédé : clé/corps/hash conservés avant réseau, partitions compte/backend, aucune émission si commitlocal échoue. UNKNOWN après réponse perdue ; statut propriétaire puis reçu exact ; ni rePOST automatique, ni nouvelle clé après timeout. Un retour ultérieur ne ferme pas un formulaire d’un autre compte/révision.

Flags contrôlés fermés par défaut et données synthétiques seulement pour le premier build. Les règles de conservation/export des copies restent dans DATA, pas fixées arbitrairement par ce protocole. Future photo/AI/équipement/personnalisation scientifique horsscope.

## Précisions avant décision

CREATE porte title seul ; slug_base est dérivé par la même politique canonique que le web, collision refusée sans nom/identité aléatoire cachée. If-None-Match:* pourCREATE ; mutations de racine avec If-Match égal au expected_source_digest du corps. Absence428, désaccord entre en-tête/corps400, source périmée409, ownerétranger/inconnu404. Reçu exact lu avant préconditions de nouvelle mutation.

Nouvelles prescriptions natives : les bornes de formulaire existantes sont6séries maximum et1–50répétitions, min≤max ; ce sont des bornes de saisie historiques, pas une recommandation. Les slots historiques inchangés, y compris hors nouvelles bornes ou horsEKB, restent conservés exacts ; aucune invalidation rétroactive par le picker.

Forme proposée program_builder_operations_v1 : idPK ; user_idFKusersCASCADE ; command_idvarchar128 ; operationvarchar24 ; request_sha256varchar64 ; program_idFKuser_programsSETNULL nullable pour la réservation de création ; source_digest_beforevarchar64 nullableCREATE ; source_digest_aftervarchar64 ; result_versionInteger ; result_jsonText (ids/provenance/reçu, pas arbre numérique) ; created_atDateTimeUTC. Unique(user_id,command_id), index(user_id,program_id,id). Le résultatCREATE assigne sa racine et son reçu dans le même commit, aucune opération PREPARED partielle visible côté serveur. Pas de backfill et aucun appel réseau dans la transaction.

La canonicalisation de commande est JSONUTF8 à clés triées, séparateurs compacts, nombres entiers stricts et refus NaN/Infinity/champs inconnus ; la même projection contractuelle est persistée localement avant HTTP. Les normalisations de libellés métier restent celles du domaine, séparées du digest du corps exact. Le digest courant inclut l’arbre/stats/version/publications et wizard_answers ; une transformation web repart d’une lecture fraîche sous verrou, hors identity-map ORM périmée. Lecture des reçus et sources bornée/paginée, captransport avant transaction ; valeurs des caps documentées dans les DTO avant code.
