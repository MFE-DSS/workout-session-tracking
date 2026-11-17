# REL03 OPS-02 — exécution locale et frontière opérationnelle

Parent 348dc8c3fda4a0c9a74be54fe1e92f159e382142. Mandat opérateur OPS-02 du 16 novembre, sections 2–5 : finir le raccordement image/configuration/isolation en local, puis soumettre une seule opération concrète avant toute mutation distante. Ce delta ne réimplémente ni application, ni SCI, ni migrations, ni EAS.

## Brainstorming / Options / Risques / Choix retenu

Réutiliser les codecs, le workflow manuel, la garde privée et le collecteur existants. Une registry nouvelle et un déploiement générique sont écartés. Transport image séparé du transport DB (caps DB inchangées), dépôt privé préexistant vérifié, même archive chiffrée puis lue avant publication de metadata. UNKNOWN durable après réponse perdue ; aucun second upload automatique.

Le VPS partagé impose un réseau QA nommé et fermé ; aucun changement global Docker. Le vhost QA doit écouter l'adresse publique qualifiée, pas une wildcard qui reproduirait la collision Tailscale déjà constatée. Ces adaptations explicites restent locales jusqu'au GO opérationnel. Aucun nouvel accès système ou secret réel créé.

## Global Constraints

- App, SCI, SQL, pixels DA08 et package/signature Android conservés.
- Aucun conteneur, volume, réseau, DNS, secret, compte ou GitHub environment créé en opération sans GO distinct.
- Un réseau interne dédié et un seul writer ; UID10001, rootfs RO, loopback8088, 1CPU/2Gio/128pids proposés.
- Plafond image fournisseur strictement inférieur à2Gio, enveloppe45octets incluse. Caps DB128Mio/256Mio inchangées.
- PREPARE et metadata ne prouvent jamais service, build ni acceptation installée.

### Task 1: Transport image réel préparé, sans publication

- [x] Tests RED : dépôt public/autre dépôt, mauvaise identité/source, taille enveloppe, checksum, réponse perdue sans second POST, redirection sans Bearer, destination existante.
- [x] Raccorder streaming chiffré et garde privée préexistante au producteur exact ; restauration privée des mêmes octets, sans Docker load.
- [x] Tests ciblés puis consommateurs image/proofs/pipeline ; aucun upload réel.

### Task 2: Isolation et routage du VPS partagé

- [x] Tests RED du réseau partagé/attachement supplémentaire et de la wildcard TLS incompatible avec Tailscale.
- [x] Collecteur/policy : réseau QA nommé interne acquis réellement ; vhost fermé avec écoute publique explicite et logs sans URL/corps.
- [x] Gardes configuration privée, commandes exactes et compatibilité existantes conservées ; tests consommateurs.

### Task 3: Qualification et décision unique

- [x] Observation fraîche bornée en lecture seule, état backup historique explicite.
- [x] Paquet exact : état actuel/proposé, commandes, identités, stockage, image, réseau, DNS/TLS, backup/restore/rollback et critères.
- [ ] check_scope, checks prescrits, revue indépendante, CI réelle et livraison locale sous GOV-MERGE-01 si toutes les gates du delta sont satisfaites.
- [ ] Soumettre le GO opérationnel ; aucune activation ni APK avant les gates correspondantes.

## Review Focus

Fuite Bearer lors d'une redirection ; upload accepté mais reçu perdu ; collision d'identité/environnement ; double attachement réseau ; nginx rechargé ou worker remplacé ; ancien compte QA02 ; sauvegarde récurrente faussement saine ; restauration post-effacement ; configuration et image seulement déclarées.

## Suivi du 17 novembre

Initialisation neuve ajoutée dans le périmètre OPS-02 : migrations/image et seeds canoniques, catalogue vérifié, pas de faits/consentements fabriqués. Deux Important de code et trois du paquet corrigés, relecture finale favorable. Sweep interrompu par plafond mémoire puis continuation sans changer les tests ni augmenter1600Mio ; résultat final à consigner. Les opérations distantes et l’APK restent exclues jusqu’à leurs GOs propres.

## Vérification finale locale

TierCI_INFRA. Campagne complète458fichiers,8810PASS/3ignorés après continuation bornée du script arrêté par mémoire ; aucun plafond augmenté ni source de test changé. OpenSpec28/28, Ruff259≤548, actionlint/protocole/Gitleaks passants. Revue fraîche code+paquet favorable après corrections. Source applicative, native, SCI et migration inchangée ; initialisation utilise les seeds existants. La CI réelle et la livraison restent à acquérir ; le GO opérationnel reste à soumettre après elles.
