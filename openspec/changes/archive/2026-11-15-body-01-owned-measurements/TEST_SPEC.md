> GO BODY-01/amendement/G1 reçu le 11 novembre 2026 : « Autoriser BODY-01, son amendement et G1 » (call_106057b169a74bc9887b1fea9f527f5d). Apply contrôlé en cours ; pixels non acceptés, aucune activation/release. Les statuts pré-GO ci-dessous gardent leur instant de préparation.

# TEST_SPEC — BODY-01 révisé

**NO_GO_BUILD.** Cas à implémenter après GO ; aucune exécution produit de cette feature revendiquée ici.

| ID | Assertion obligatoire |
|---|---|
| B01 | Nouveau poids puis tour même jour : deux racines, pas upsert ; BodyMeasurement source unique, aucun profil/séance backdaté. |
| B02 | CORRECT d'un tour : nouvelle ligne/tête ; ancienne ligne byte/faits/dates inchangés, champs absents/provenance hérités conservés. |
| B03 | Null explicite dans tête : champ vidé ; aucune résurrection depuis version superseded dans chaque lecteur. Autre racine indépendante suit sa règle historique. |
| B04 | Date corrigée : même racine, nouveau point courant à nouvelle date, ancien fait consultable ; created_at/recorded_at de version distincts du jour du fait. |
| B05 | Native date invalide/future refusée ; SSR fallback conservé et honnêtement marqué SERVER_CAPTURE_TIME. |
| B06 | Booléens/nonfinis/clés inconnues/bornes refusés sur champs nouveaux ; hérités invalides conservés et sérialisés sans NaN/0/omission. |
| B07 | Copier un champ hérité ne le requalifie pas USER_DECLARED/KNOWN ; corrected source ne s'applique qu'aux champs changés. |
| B08 | Deux observations même date restent indépendantes ; corrections n'augmentent pas fréquence/points/compteurs courants. G/D restent même ligne, côté inconnu distinct. |
| B09 | CREATE/CORRECT + sidecar/reçu atomiques ; panne intermédiaire rollback sans demi-fait ; unique parent/révision empêche branche. |
| B10 | Connexions SQLite fichier distinctes : même token, une correction réussie et une409 ; même request/digest un effet, digest différent409. Pas preuve par mutex. |
| B11 | SSR edit ajoute version et participe à garde ; ancien onglet web/native stale refusé ; profile create utilise allocator/kernel. |
| B12 | Replay ancien reçu après correction/effacement avant CAS/permis nouvelle mutation : ACK exact, sans lecture des anciennes valeurs ni nouvelle permission. |
| B13 | ERASE confirmé supprime toutes lignes numériques d'une racine, aucune résurrection ; autres racines/owners préservés ; metadata sans copie de nombres. |
| B14 | Replay ERASE après disparition exact ; ancien id/token ne modifie pas nouvelle racine. Aucun effacement global implicite. |
| B15 | Allocator CREATE/CORRECT tous owners : max canonique/références réservées ; table vide/id maximal effacé ne réutilise pas id ; borne safeinteger ferme writes. |
| B16 | Migration additive table/index seulement ; aucune ligne ancienne changée ; revision0 virtuelle ; pas PK/rebuild/AUTOINCREMENT/backfill/startupDDL. |
| B17 | Schéma/guard indisponible : writes SSR/native fermés, lecteurs truth-dependent indisponibles sans brut de secours ; rollback compatible garde audit. |
| B18 | Sélecteur partagé : body_profile/ledger/morphology/BI/measurements/scoring/dashboard/coach ne lisent pas les versions remplacées ; résultats legacy non corrigés et formules inchangés. |
| B19 | Budget requête body_ledger conservé sans N+1 ; période/as_of sur tête, aucune reconstruction historique de score prétendue. |
| B20 | Poids v1 DTO/décodeur inchangés, têtes seulement ; nouveau BODY source-aware, vrai Progrès relit valeur et provenance, pas seconde série/courbe calculée. |
| B21 | Curseurs BODY owner/plage/revision : mutation concurrente409/relecture ; ni fuite, trou/duplication silencieuse ni réponse tardive affichée sous autre période. |
| B22 | Ownership A/B pour toutes routes/audit/export/ops, inconnu/étranger404 identiques, no-store ; cookie seul non Bearer refusé. |
| B23 | Accord/flag absent : aucune collecte/grant implicite ; retrait ≠ effacement, ACK historique minimal ; effacement possédé sans nouveau grant de collecte selon contrat. |
| B24 | Export exhaustif versions/current/calf/qualités/provenance et dates ; legacy export forme conservée et têtes ; aucune déclaration d'effacement backups/local. |
| B25 | Local commit+relecture exacts avant HTTP ; panne stockage aucun HTTP. Kill avant envoi/après commit serveur/avant ACK local conserve même clé/corps/token. |
| B26 | GET receipt absent reste UNKNOWN ; replay explicite exact, aucune nouvelle clé/queue offline auto ; ACK terminal avant refresh. |
| B27 | A→B/logout/réponses tardives/owner retiré : aucune lecture ou émission de payload A sous B ; retour A retrouve sa partition. |
| B28 | Attachement BODY sans NUT ; outbox/séries/PLAN et décisions ownership inchangés ; preview mémoire interdit mutation. |
| B29 | Vrai ConnectedApp→HTTP→BodyMeasurement→correction→audit→Progrès ; équivalent SSR ; pas seulement gallery/mocks. |
| B30 | Board normal/grand texte iOS/Android, décimal FR/Done/retour/safeareas/unités/focus/labels/reduced-motion ; aucune cible <48dp ni action obligatoire cachée. |

## Gardes et preuves

Réutiliser sans affaiblir les suites body_profile, profile_measurements, mob03_weight_api, ui_cp75a et tous consommateurs listés B18. Adapter les attentes mutables uniquement comme delta normatif explicitement approuvé, avec témoins montrant l'original conservé ; ne pas enlever les contrôles ownership/NULL/héritage.

Après apply : check_scope en premier, tier migration attendu, scripts migration/drift/snapshot et sweep local borné requis, broad des consommateurs, mobile/TS, CI réelle finale, revue fraîche CAS/lecteurs/effacement/copies, pixel gate. Aucun full sweep de feature non construite dans cette préparation. Engineering/integration/external release trois reçus séparés ; aucune recette physique ou APK déduits de ces tests.
