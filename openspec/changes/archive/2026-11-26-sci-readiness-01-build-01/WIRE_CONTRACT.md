# Endpoint / DTO proposés — NOT_SERVED

## Request
`GET /api/mobile/v1/me/muscle-observed-load?from=<instant>&until=<instant>&time_zone=UTC`

`X-Auren-Muscle-Observed-Load-Contract: muscle-observed-load/1.0.0`, Bearer existant, no-store pour toute réponse dont erreurs. from/until obligatoires, offsets explicites normalisés UTC, from<until<=as_of ; time_zone vaut seulement UTC. Queries inconnues/dupliquées, body GET et header incompatible refusés, aucune session/owner arbitraire. Pas de cursor ni autre route dans BUILD01.

401 auth existante ;406 contrat absent/incompatible ;422 requête invalide sans écho ;503 UNAVAILABLE sur désactivation/profil non qualifié/ressources non sûres/DB indisponible ;200 seulement après validation complète d’un résultat OBSERVED/PARTIAL/UNKNOWN/EMPTY. Codes courts stables, aucun SQL/chemin/secret/corps brut en erreur. Toute erreur d’autorisation garde la sémantique existante ; pas de redirection HTML.

## Deux niveaux distincts de quantité
`evidence` garde la sémantique canonique ZoneExposure : comptes primary_sets/secondary_sets/minor_sets/unknown_sets, resolved_credit, bound et exact_evidence sur les faits inspectés admis dans ce registre. Sa portée est INSPECTED_ROLE_VECTOR ; exact_evidence ne certifie ni le temps ni l’exhaustivité. L’objet est NULL lorsqu’aucune contribution qualifiable à la zone n’existe ; pas de remplissage depuis un zéro interne.

`window_result` est une **nouvelle métadonnée proposée** : state, documented_sets, resolved_credit, bound et reasons. documented_sets = union de clés effectives certaines, datables et attribuables à cette zone dans la fenêtre canonique. Pas de somme des zones. bound EXACT seulement si toute couverture nécessaire et qualifications sont attestées ; MINIMUM seulement si une part certaine existe et des lacunes subsistent ; sinon bound et nombres NULL, state UNKNOWN/EMPTY selon preuve. Aucun conflit/CONTENT_EXECUTION_MISMATCH non résolu n’augmente le minimum. Crédit MINOR connu0 licite ; ne représente pas zéro effort.

Pour posterior : composants hamstrings/glutes séparés, union distincte certaine avec les mêmes règles de borne ; resolved_credit toujours NULL. Aucun compteur de rôle cumulé ni activation dérivée.

## Enveloppe stricte proposée
Tous les champs sont requis, nullable là où dit ; extras interdits, nombres finis, bool≠int, max15zones, max500facts, IDs positifs63bits. Aucun float de tonnage ou score.

| Champ | Type et autorité |
|---|---|
| contract_version | literal muscle-observed-load/1.0.0, nouveau contrat |
| availability | AVAILABLE ou UNAVAILABLE, convention des lectures existantes |
| state | OBSERVED/PARTIAL/UNKNOWN/EMPTY/UNAVAILABLE, état de cette projection ; ne pas mélanger avec bound |
| owner_id/read_id/as_of | owner authentifié, UUID de lecture, date de capture UTC ; pas des dates d’effort |
| window | from/until ISO-Z, time_zone UTC, convention de history adaptée à completed_at |
| membership | LIVE_BOUNDED_MEMBERSHIP ; état courant, pas replay d’une ancienne DB |
| policy_id/catalogue_versions/mapping_version | sources réellement utilisées et digests ; aucun catalogue par défaut non attesté |
| coverage | scan COMPLETE/TRUNCATED, temporal COMPLETE/PARTIAL, mapping COMPLETE/PARTIAL, reasons ; nouveaux champs documentaires |
| scan | ordre OWNER_ID_ASC_NESTED, plafonds et nombres effectivement inspectés, branches/sources omises bornées ; pas de total global à COUNT |
| consistency | READ_TRANSACTION, source digests, result_digest ; snapshot DB + sources immuables, pas révision globale |
| zones[] | zone SCI exacte ; evidence, window_result, last_qualified_observation nullable ; exactement15dimensions conservées |
| bodymap_projection | mapping_version,11cibles et3NOT_REPRESENTED, posterior composants/union sans scalaire ; aucun nouvel asset |
| facts[] | session_id/session_exercise_id/set_log_id ; kind/completed/completed_at/reps/weight_kg ; prescribed_name/executed_name, résolution/roles/evidence_refs, contexte/setting réellement conservés et qualification temporelle ; champs absents restent NULL |
| exclusions | compteurs des motifs réellement inspectés ; branche non explorée = quantité inconnue, pas0 ; aucune identité étrangère |

Les champs source viennent de SetLog, LedgerLine, IdentityResolution, ZoneExposure, FirstPlanExecutionBinding/Evaluation/SetObservation. Les nouveaux enveloppes/coverage/window_result/consistency/scan sont explicitement proposés ; leur présence n’est pas une API existante. `observation_json`/`receipt_json` complets ne sont jamais transmis : exposer uniquement op_id, expected/applied_revision, performed_at/estimated/adjusted, recorded_at et les preuves descriptives utiles, après validation.

## Règles de couverture et statut
- OBSERVED et bound EXACT de fenêtre : scan épuisé, sources pertinentes qualifiées, appartenance et attribution des faits à cette fenêtre prouvées selon D1 ; ne signifie pas totalité de l’entraînement réel ni heure physiologique exacte. PARTIAL_TIME d’origine suffit à garder state PARTIAL même si le décompte du journal est déterminable.
- PARTIAL : au moins une contribution certaine et une lacune de scan/temps/source ; seulement borne MINIMUM possible pour la quantité affectée. Les comptes exacts de rôles du sous-ensemble restent distincts.
- UNKNOWN : pas de part certaine, sources manquantes/troncature/non-datable ; nombres NULL. Un préfixe ancien sans fait dans la fenêtre n’est pas EMPTY.
- EMPTY : seulement domaine V1 effectivement épuisé, aucune donnée/candidat non qualifié susceptible d’affecter la fenêtre ; lecture « aucun fait documentaire admissible » et nombres externes NULL, pas zéro physiologique.
- UNAVAILABLE : impossible de produire une part sûre dans les limites, runtime non admis techniquement ou accès en échec. Aucune ancienne lecture réinjectée par le serveur.
- last_qualified_observation agrégé NULL dès couverture nécessaire incomplète, qualité d’origine non prouvée ou acquisition client non attestée. Une observation inspectée peut rester consultable par sa date sans être présentée comme dernière.

Les réglages machine/PER_IMPLEMENT restent des settings typés ; weight_kg NULL n’est pas comblé. Prescriptions/contextes ne deviennent pas exécutions. Les dates sans source ne sont jamais fabriquées.

## Schéma exact et invariants croisés proposés

`PROPOSED_RESPONSE.schema.json` fixe tous les objets imbriqués, types, enums, champs requis/nullables et plafonds structurels. C’est une source documentaire à implémenter après GO, pas un codec produit. Les IDs DB sont des entiers positifs63bits ; IDs d’évaluation/opération/scientifiques restent textuels, jamais convertis en position. Le schéma rejette tout champ supplémentaire ; contrôle UTF8/bytes/finitude/doublons JSON en amont, validation sémantique en aval.

Invariants croisés obligatoires (tests Task1/3/5) :
1. `availability=UNAVAILABLE` impose `state=UNAVAILABLE` et seulement l’erreur publique (HTTP401/406/422/503 selon code), aucune donnée propriétaire. AVAILABLE n’accepte pas stateUNAVAILABLE.
2. Les15codes SCI et11cibles sont uniques et exactement ceux de P07 ; trois non-représentés exacts. posterior.components=[hamstrings,glutes], son crédittoujoursNULL. Un set ne compte qu’une fois dans son union.
3. window.from<until<=as_of ; dates Z ; facts retournés seulement IN_WINDOW ou appartenance UNKNOWN, les autres ne sont que motifs/counters d’exclusion. Une membershipUNKNOWN n’augmente aucun minimum/total.
4. window_result boundEXACT exige couverture nécessaire complète, nombres déterminables et aucune inconnue affectant sa quantité ; MINIMUM exige au moins un faitcertain/date/mapping cohérents de la fenêtre, jamais le seul créditinterne0. UNKNOWN/EMPTY ont quantités et boundNULL. PARTIAL_TIME sans contradiction peut laisser un décompte EXACT **du journal canonique** si son appartenance est certaine, sans qualifier l’heure d’effort ; stateglobal restePARTIAL et dernierqualifiéNULL.
5. `evidence.exact_evidence` égale sa définition canonique (`bound=EXACT && execution_uncertain_sets=0`) sur son seul vecteur inspecté. Ne pas y réinjecter une exactitude de fenêtre. evidenceNULL si aucune ligne qualifiable à cette zone.
6. Si scan/qualification nécessaire partiels, aucun last agrégé ; sinon last doit pointer un factprésent, mêmecompleted_at/zone, provenancequalifiée, mappingcertain. Source d’acquisition nonattestée ->NULL, même si estimatedfalse.
7. Toutes les clés/parents de facts sont dans la capture du mêmeowner ; aucune paire de clés+zone dupliquée ; applied_revision=expected_revision+1 lorsqu’elles existent et identitéop/context/digest concordantes. Origin/effective operations indépendantes ; absenceLegacy=NULL.
8. `scan.truncated` concorde avec coverage.scan et les sentinelles/branches ; usage ne dépasse jamais les caps. UNKNOWN ne devient pas EMPTY parce que le préfixe n’a pas trouvé de fait dans la période. EMPTY exige épuisement et aucune inconnue susceptible d’affecter la réponse.
9. Les unités/side/load_semantics sont exactement ceux de la source validée ; champ setting inconnu ne devient pas MASS_KG/TOTAL_EXTERNAL. Nombres nonfinis ou boolen guise d’ID/reps rejetés ; données hors schéma signalées dans les omissions ou UNAVAILABLE, sans clamp/réécriture de DB.
10. Chaque source_ref est canonique/logique, pas un cheminabsolu privé ; version/digest correspond à la source réellement utilisée. Pas de rawJSON, motdepasse, token, note libre ou configuration dans facts/erreurs.

Le JSONSchema ne peut pas à lui seul prouver ces invariants ni les plafonds de ressources ; tous ont des tests de service et d’API dédiés au futur build.

`scan.usage.unvisited_frontiers` compte seulement les frontières d’arrêt reconnues dans le parcours, jamais le nombre total de branches/événements omis. Ce dernier est inconnu sans scan et resteNULL dans exclusions. `fact.set_index` est l’index réel du SetLog, sans devenir une identité universelle.
