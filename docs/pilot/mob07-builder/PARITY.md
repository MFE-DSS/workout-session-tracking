# MOB07 — parité réellement éprouvée

15 novembre 2026. Code fusionné par PR414 au merge dbad35d ; CI canonique43753463939 vérifiée success11jobs. Pixels acceptés pour le pilote avec limites. Données synthétiques uniquement ; aucun nouveau binaire ou déploiement.

| Capacité | Domaine/HTTP | Vrai ConnectedApp iOS simulateur | Android complet / physique |
|---|---|---|---|
| Créer/composer avec identités canoniques et répétitions manuelles | Vérifié | VERIFIED_NATIVE | UNAVAILABLE |
| Valider/publier puis consulter dans MOB06 | Vérifié | VERIFIED_NATIVE | UNAVAILABLE |
| Départ, même séance dans Today et journal | Vérifié Legacy ; V3 gardé par tests | VERIFIED_NATIVE Legacy | UNAVAILABLE |
| Reçu perdu, kill/restart, GET exact sans nouveau POST | Vérifié | VERIFIED_NATIVE | UNAVAILABLE |
| Compte/backend isolés, conflits et keep historique | Vérifié ; SQLite et consommateurs A/B/A | PARTIAL : tests du consommateur complet + scénario natif propriétaire | UNAVAILABLE |
| Historique de séance et prescriptions conservées | Vérifié ; séance synthétique0réalisée/2prévues | Journal de clôture natif ; readback Progress non rééprouvé dans ce banc | UNAVAILABLE |

Le Host Android utilise le présentateur et HTTP/SQLite réels mais son menu Expo masque les pixels ; il ne vaut pas application complète ou acceptation. La CI PR du HEAD c614241 est verte et le merge effectué ; le reçu canonique est consigné dans CLOSEOUT.md. Android complet/pixels, nouveau binaire installé et physique restent ouverts. Aucun programme actif, calendrier, récupération musculaire ou prescription scientifique cliente ajoutés.
