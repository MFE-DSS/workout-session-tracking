# SCI-RUNTIME-03 — livraison et qualification du candidat

26 novembre 2026, Europe/Paris. Parent initial `3d4c7577e5ffd39fb59de58d1aab3bded1936edb`. Code vérifié : `7393ac1cd15b74764cba0c436aa9e548662e32ef`, PR #452. Merge code : `7327256d678d681a3efa170795933daae094715c`, arbre identique au HEAD testé. CI PR [45891313230](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/45891313230) completed/success, onze jobs ; 9 038 backend/3 ignorés, 140 suites/1 610 mobiles, TypeScript et 77 visuels. La CI canonique [45893610967](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/45893610967) est encore en cours à cet instant de rédaction ; aucun succès canonique n’est anticipé.

## Résultat

La réutilisation du catalogue est privée au job, au propriétaire et au profil. Chaque source reste attestée indépendamment ; les consommateurs reçoivent des vues distinctes et les changements d’autorité invalident le contexte. Le digest décrit le DTO normalisé effectivement retourné et est recalculé par une voie indépendante. Aucun budget, contrat SCI, SQL, writer, TIME-01, modèle, client ou asset n’a changé.

Le candidat contrôlé est qualifié sur Linux/amd64, Debian 13.3, Python 3.11.14, SQLite 3.46.1, image existante `5ee90ab…` avec le code Git exact monté en lecture seule. Cette preuve ne qualifie ni une future image reconstruite, ni les chemins d’un déploiement opérationnel. **Chemins opérationnels : HOLD ; activation : DISABLED.**

## Mesures du processus intact

| Cas | Admissions parent | CPU total min–max | Moyenne / écart-type population | Wall min–max |
|---|---:|---:|---:|---:|
| Legacy | 5/5 | 1,563–1,643 s | 1,600 / 0,032 s | 1,633–1,722 s |
| V3 | 5/5 | 1,626–1,708 s | 1,665 / 0,034 s | 1,700–1,790 s |
| 100 faits | 2/2 | 1,707–1,715 s | 1,711 / 0,004 s | 1,793–1,797 s |

Les temps user et system individuels figurent dans le reçu JSON. Les trois sondes instrumentées, distinctes des mesures intactes, montrent un seul parsing. Les digests des 18 réponses admises concordent. Aucun résultat PARTIAL/UNKNOWN n’est promu à EXACT.

Pic RSS nominal V3 : 68,35 Mio ; VmPeak échantillonné : 90,59 Mio. Limites inchangées : enfant 2/3 s CPU, 512 Mio AS, supervisor 3 s wall ; conteneur 1 CPU/2 Gio/sans swap. Le pic parent+enfants du conteneur HTTP est consigné séparément.

## Refus, SQL et propriétaires

Les quatre essais 500/501 séries sont refusés SIGXCPU ; les deux sorties JSON 501 dépassent aussi le plafond lexical du parent. Un JSON écrit avant la terminaison n’est jamais présenté comme une réponse admise. Préfixe ancien, bundle V3 manquant et texte excessif restent UNKNOWN.

SQL : 13/34/653/2 003 appels execute diagnostiques pour Legacy/V3/100/préfixe ancien ; compteurs applicatifs 19/57/1 003/3 203. Mesures diagnostiques au pas 1 : 1 730/2 194/64 622/142 233 instructions. Le compteur normal au pas 1 000 n’est pas un total exact. Le témoin adversarial atteint 2 000 000 puis est refusé. Timeout et débordement de pipe sont tués et récoltés ; allocation 600 Mio refusée sous AS 512 Mio.

Snapshot WAL : lecture 9 conservée pendant l’écriture concurrente vers 88, puis nouvelle lecture 88, intégrité OK ; DML depuis la capture refusé. HTTP isolé : A → 9, B → 999, compte vide EMPTY ; sans Bearer 401, injection de chemin 422, concurrence 200+503. Base inchangée après GET, enfants récoltés et slot libéré.

## Tests et revue

RED→GREEN : parsing doublé, digest entier/float et corruption, nouvelle génération refusée laissant une vue périmée, manifeste sans pin. Local : 346 PASS/4 skips Linux ; runtime exact : 349 PASS/1 skip optionnel jsonschema, absent de l’image. Aucun skip ajouté. Ruff 260 ≤ 548, Bandit, Gitleaks, protocole et OpenSpec strict passants. Pas de full sweep local pour SHARED_CODE.

Revue indépendante intégrale : un Important (pin de manifeste vide/NULL) et un mineur (isolation de globals du test) corrigés puis relus ; aucun constat ouvert. La campagne native et ses 18 empreintes ont aussi été relues.

Incidents du harnais conservés : premier essai zéro test (py.py manquant) ; collecteur 180 s expiré juste avant la fin réelle de pytest, sortie 0 vérifiée ; première campagne HTTP 401 (clé synthétique incohérente), puis assertions strictes passantes. La requête récursive invalide d’un ancien diagnostic SQL n’est pas réutilisée ; le témoin VM crossjoin réel est conservé. Aucun changement produit n’a servi à masquer ces incidents.

## Conservation et limites

3 362 fichiers Git et 3 904 entrées d’autorités vérifiés ; aucune divergence, ACL, symlink ou permission inattendue dans le candidat. Écriture/renommage refusés sous UID 10001, volumes de sources RO, caps nulles, réseau fermé, aucun port publié. Les essais ne certifient pas un futur déploiement ni sa résistance à une modification privilégiée.

Bancs nettoyés normalement : premier essai 3 conteneurs/5 volumes, second 9 conteneurs/5 volumes et leurs scratchs uniquement. Dix conteneurs préexistants et cinq services identiques avant/après ; image conservée. Preuves, sources, fixtures et profils synthétiques privés conservés hors Git. Aucun service QA, secret existant, configuration VPS, donnée réelle, APK ou OTA modifié.

Prochaine opération : préparer puis autoriser séparément la qualification de l’image et des chemins opérationnels exacts du futur paquet QA. Toute activation reste une décision distincte.
