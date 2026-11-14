# MOB-06 — candidat d’intégration conservé, livraison ouverte

13 novembre 2026. Branche `feature/bibliotheque-seances`, base canonique fraîche
`1462482a4e2bcd1fcde121d6f207a2131616e849`. GO BUILD/G1 acquis et conservé.
Aucun nouveau commit produit, PR, CI distante, merge, APK, OTA ou déploiement.

Le candidat raccorde le vrai ConnectedApp, Programmes, la connexion et la queue
SQLite du journal propriétaire, le parent API et l’inventaire des trois routes.
Création unique → adoption durable → Today → action réelle de reprise conserve
le même identifiant. Perte de réponse → redémarrage du composant et réouverture
SQLite fichier → vérification/reprise explicites, sans second POST. A/B/A et
offline/reconnect sont exercés dans le consommateur complet automatisé. Les
frontières OS/HTTP de ces tests sont synthétiques, pas des séances humaines.
Le backend réel confirme la même identité dans Mission, exécution et historique ;
les séries prescrites non réalisées restent sans répétitions/charge observées.

La répétition concurrente du départ est exclue par la séance ouverte (409).
Cela n’est pas un ledger serveur d’idempotence durable. Après reçu perdu, une
séance relue reste une reprise propriétaire et la création initiale UNKNOWN.
Le profil V3 garde son contrôleur/journal ; aucun nouveau claim scientifique.
La reprise V3 sans état local applicable n’est pas déclarée prouvée ici.

## Preuves locales finales du candidat

- Broad backend ciblé : **152 PASS**, `BACKEND_FINAL.log`.
- Mobile : **96 suites / 1 200 PASS**, TypeScript PASS (`MOBILE_FINAL.log`, `TS_FINAL.log`).
- Ruff neuf PASS, budget **260 ≤ 548**, protocole, Bandit et Gitleaks du patch PASS ;
  OpenSpec strict **25/25**. Tier SHARED_CODE, aucun full sweep backend local.
- Revue indépendante du raccordement : un Important navigation et un mineur de
  couverture corrigés RED→GREEN. Vérification indépendante nommée conservée dans
  `INDEPENDENT_REVIEW.md`. Pas de faux second avis sur tous les ajouts ultérieurs.
- Le correctif sans géométrie (notification de succès consommée une fois) est
  également conservé dans le worktree MOB-06 : **17 tests ciblés PASS**.
- Rendu du vrai ConnectedApp iOS/Expo Go sur simulateur dédié 390×844 pt avec
  API loopback synthétique : preuve de lecture, pas gate artistique final.
  Pilotage tactile interrompu par CUA `noWindowsAvailable`. Android ConnectedApp,
  reprise native tactile, grande fonte finale et physique restent des gates.
  Les échecs du banc (IPv6 localhost, puis bootstrap appelant une méthode Auth
  inexistante) sont conservés ; ils ne deviennent pas des PASS produit.

## Patch et leases

Dossier durable : `/Users/martinfeldmann/auren-review/mob06-integration-20261113/`.
`CONNECTED_INTEGRATION.patch` contient **13 chemins**, avec avant/après SHA256 dans
`CANDIDATE_MANIFEST.json`. `git apply --check` sur le worktree MOB-06 passe ;
**patch non appliqué** aux sources partagées. `candidate/` est une copie d’archive,
pas une nouvelle branche ni une PR concurrente. Les 33 fichiers initiaux sont
conservés dans `preserved-feature/` et `FEATURE_BEFORE.json`.

`PARENT_LEASE_PREVIEW.json` et `parent-preview/` conservent l’assemblage à blanc :
BODY exige résolution dans ConnectedApp, journal.ts, journalTypes.ts et mobile_api ;
NUT dans config.py. Ces brouillons ne sont ni des parents canoniques vérifiés,
ni une autorisation de couper leurs leases. Aucune source BODY/NUT modifiée.
Checkout opérateur et son empreinte `da808515…` préservés, aucun appareil personnel
réinitialisé, aucune baseline/primitives/SDK/lock modifiés.

## Direction et prochaine opération

Le rendu de raccordement réutilise G1 et n’est **pas** proposé comme master final
Programmes : sa présentation actuelle reste trop proche d’une liste. Le gate
artistique demandé reste ouvert : programme réellement consulté souverain,
structure ordonnée lisible, séances/actions dans leur contexte, quatre onglets.
Le domaine courant ne fournit ni programme actif persistant ni affectation aux
jours : aucune sélection consultée ne doit être renommée programme actif,
aucune position de séance devenir un jour. Pas de rail EASY/TARGET/PUSH.

Après libération des leases : reprendre le patch sur les parents effectivement
fusionnés, résoudre les conflits sans perdre leurs ports, refaire les consommateurs,
terminer la planche consolidée et obtenir les pixels. Puis contrôles/CI HEAD exact,
merge GOV-MERGE-01, canonique et closeout. Aucun GO BUILD/G1/merge routinier à
redemander. MOB-07 vient après cette livraison ; sa logique restera dans les
domaines canoniques, sans nouveau moteur de prescription client.
