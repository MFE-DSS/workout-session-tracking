# Stage2 — preuve exigée et handoff PLAN proposé

**Spécification de tests, pas tests déjà écrits/exécutés.** Aucun artefact positif créé dans la préparation. Les anciens contrats et leurs exemples ne sont pas reproduits sous un autre nom.

| ID | Vérification future concrète | Oracle attendu |
|---|---|---|
| P01 | Sept réglages/essais comparables qualifiés et acceptés au présent, inventaire globalUNKNOWN, sans anthropométrie | Vrai producteur + registre admis : prescriptions observées provisoires, science positive limitée, tempsUNKNOWN, REQUIRES_TIME_ACK |
| P02 | Ack explicite exact depuis P01 | Même plan+temps et faits/observations, empreinte d’évaluation différente, ELIGIBLE sans changer l’état de temps |
| P03 | Réalisation disponible mais un réglage/plage non qualifié, encore bootstrap | Draft/revue et DENIED ; aucun SCIENTIFICALLY_READY ou CONFIRMED inventé, aucune charge à froid |
| P04 | Une branche valide syntaxiquement mais dose/candidat/allocation/source modifiés | Refus par invariants canoniques indépendants puis recomputation, pas simple validation du schéma |
| P05 | Subject/snapshot/révision/versions/3empreintes/plan+temps/policy/date d’ack incompatibles | Refus ; aucun autre propriétaire ou ancien plan reconnu |
| P06 | Champs requis manquants, conflit utilisé, cadence3 ou limitations non vides | Manque/conflit/revue précis ; aucun nouveau blocage poids/taille/expérience |
| P07 | Confirmation de salle sans réalisation/appareil/côté/sémantique source ; conflit ou un contexte indisponible | Aucun gym complet ou candidate compatible inventé ; pas de substitution hors binding |
| P08 | Préoccupation, ancien import, précédent bloqué, absence de règle de reprise | Refus/revue, pas de retry automatique ou nouvelle acceptation fabriquée |
| P09 | Restfloor≥budget puis restfloor<budget | TOO_LONG/DENIED dans le premier cas ; UNKNOWN dans le second, jamais fit/SUPPORTED |
| P10 | Structure/pairing différente du binding | Pas de borne séquentielle appliquée à une autre structure |
| P11 | Registre/index/binding/source retirés, altérés ou pin obsolète | Fail-closed ; ancien résultat/ack inutilisable avant nouveau handoff |
| P12 | Bool/nombre, NaN/inf, copies Pydantic imbriquées, ordre des événements équivalents | Types stricts, données invalides refusées, résultats canoniques reproductibles pour entrées équivalentes |
| P13 | Quinze zones et G17 | Rôles sourcés conditionnels seulement, absences documentaires UNKNOWN ; aucun crédit/activation ou nouveau claim |
| P14 | Rejeu complet des sources et artefacts historiques + clients v1 actuels | Octets/pins/output inchangés, v1 ne reçoit pas v3 sans négociation, aucune nouvelle importation de production |
| P15 | Export du positif | Produit seulement par l’engine réel et validé contre le vrai registre admis ; artifact_kind REAL_PRODUCER_SYNTHETIC_INPUT_NOT_SERVED, aucune clé d’autorité de test |

## Handoff précis que PLAN recevra après livraison

- `FirstPlanRequestV3` existant : snapshot serveur propriétaire, revision/as_of, cinq familles requises/provenances, exclusions réellement utilisées, contexte d’exercices/épisodes et versions de policy/engine/catalogue/bundle. L’inventaire global peut être UNKNOWN.
- Résultat3.0.0 : admission_ref/binding_ref et digests exacts, références de retrait, inputs consommés et explications, prescription observée qualifiée pour le positif, bootstrap hors positif, plan_time_fingerprint comme identité logique stable ; aucune identité persistée supplémentaire.
- Profils d’autorité : ancien validate_exchange v3 négatif conservé pour rejeu ; nouveau validate_admitted_exchange_v3 canonique déclaré pour le binding admis. PLAN doit choisir explicitement le bon profil, pas reconnaître un statut JSON positif de sa propre initiative.
- TempsUNKNOWN et permission distincts. Sans ack applicable : REQUIRES_TIME_ACK. Avec ack exact et autorité encore applicable : ELIGIBLE au sens du plan observé exploratoire, pas commande de séance ou promesse de temps. Aucun transport exposé par ce scope.
- Retrait/version/contexte/source changés : nouvelle décision nécessaire ; pas de retry de mutation ou ancienne validation mise en cache faisant foi. Préoccupation/limite : arrêt et faits incomplets ; aucune règle de reprise après préoccupation n’est admise.
- PLAN possède authentification/ownership réels, construction du snapshot, négociation v1/v3, fraîcheur d’autorité, affichage/ack réel, commande idempotente de séance et reprise ; aucune donnée du caller n’est authentifiée par le moteur pur.

## Fichiers et coordination

SCI possède uniquement les nouveaux modules v3 et son dossier. Pas de modification partagée du SDK/API ou des modèles historiques. Les anciennes références pinent notamment le SDK actuel : PLAN devra versionner ses références et préserver le rejeu, sans réécrire silencieusement des anciens hashes. Le manifeste du nouveau binding évitera les chemins actifs destinés à l’archive et les cycles de digest du loader.
