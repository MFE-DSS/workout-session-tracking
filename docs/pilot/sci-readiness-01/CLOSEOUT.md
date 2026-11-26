# SCI-READINESS-01 BUILD-01 — reçu de livraison technique

26 novembre 2026 — Europe/Paris. **Code fusionné et contrôles canoniques obligatoires passants. Archive documentaire réalisée ; publication de ce closeout et nettoyage suivis par reçus vivants. Activation HOLD, lecteur désactivé.**

## Résultat et autorités

Le GET propriétaire versionné, la capture SQLite cohérente bornée, la projection descriptive Legacy/V3/P07 et le worker Linux isolé sont implémentés. Les faits historiques, writers, TIME-01, allocation SCI, mobile et primitives visuelles restent hors diff. Aucune configuration VPS, donnée réelle, activation, APK ou OTA.

Actes : admission SCI D1–D5/six règles D4 et GO BUILD distinct du25 novembre ; amendement du26 novembre limité aux deux fingerprints historiques et au format documentaire des 112 empreintes. Les 112 SHA-256 correspondent aux octets Git du parent1f0122bf ; aucune valeur ni règle de scan modifiée.

## Révisions et vérifications

| Objet | Preuve |
|---|---|
| Parent | `1f0122bf4f2d30f7c95d4975b5994d1453363bc5` |
| [Code PR446](https://github.com/MFE-DSS/workout-session-tracking/pull/446) — HEAD testé | `81e5e568fc5389a02bb834a2857e1111029591f7` |
| Merge code | `1be45a4f655d8edeeb18889e0bcbdf06ad35e52e` ; arbre identique au HEAD testé |
| [CI PR finale](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/45779277494) | Quatre checks protégés PASS ;8 983 tests backend / 3 ignorés, 1 610 tests mobiles + TypeScript, 77 visuels |
| [CI canonique code](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/45788108352) | Quatre contrôles protégés PASS ; 8 983 backend / 3 ignorés ; 1 610 mobiles + TypeScript ; 77 visuels |

Local :122 PASS / 2 témoins Linux ignorés sur Darwin ; campagne complémentaire du locator d’archive : 66 PASS. Broad antérieurs : 150 PASS puis 221 PASS / 2 ignorés, conservés séparément. Ruff neuf, budget 260 ≤ 548, protocole/OpenSpec strict, Bandit nouveaux modules et Gitleaks sur l’historique pertinent passent. Aucun sweep complet local systématique. Le locator du schéma exige un document unique et l’égalité intégrale avant/après archive : RED→GREEN, sans source runtime changée.

## Revue et diagnostic conservés

Une revue indépendante du backend complet a demandé des corrections Important, effectuées par l’auteur avec témoins RED→GREEN. Aucun second avis global des correctifs n’est prétendu. Deux revues complémentaires favorables bornées : amendement Gitleaks/pins, puis locator d’archive. Aucun Minor différé par ces reviewers.

Sonar PR446 : **ERROR consultatif**,0 bug, 1 vulnérabilité signalée, 91 smells, 0 hotspot, couverture 91,6 % / nouvelle 80,4042 %. Alerte 13 / S8707 examinée indépendamment : aucun chemin contrôlé par la requête trouvé dans le flux HTTP. La configuration serveur et les répertoires parents demeurent de confiance ; O_NOFOLLOW ne couvre que le dernier composant. Le fil de revue est résolu avec justification, l’issue Sonar reste ouverte. Aucun seuil/règle/état d’issue changé ; aucune innocuité globale déduite.

Les détails, rulings, contre-exemples et limites de chaque avis sont dans [REVIEW_AND_VALIDATION.md](REVIEW_AND_VALIDATION.md). Sonar canonique sur `1be45a4`, analyse `91e09d81-ad74-4627-b7a3-e76337935b52` : **ERROR consultatif**, 9 bugs, 9 vulnérabilités, 750 smells, 0 hotspot ; couverture 91,6 %, nouvelle 91,5072 %. Ces totaux globaux ne constituent pas une revue exhaustive de la dette.

## Deux blocages opérationnels indépendants

1. Le catalogue canonique comporte une chaîne de 4 302 octets pour un plafond admis de 4 096 octets. Refus conservé, aucun budget augmenté ou octet historique réécrit. Les ports positifs qui omettent en mémoire une note éditoriale sont synthétiques et ne qualifient pas ce catalogue.
2. Les témoins CI Linux / Python 3.11.18 passent ; ils ne qualifient pas l’image cible 3.11.14, son conteneur, ses sources, la concurrence et ses chemins de configuration. Aucun profil QUALIFIED fabriqué.

Avant une activation : amendement précis du lecteur sélectif de champs, puis qualification effective de l’image et autorisations OPS/DATA propres. [HOLD complet](QUALIFICATION_HOLD.md). Aucun GO opérationnel demandé ou inféré dans cette livraison.

## Brainstorming / Options / Risques / Choix retenu

Intégrer le code désactivé conserve une tranche vérifiée sans prétendre résoudre les deux HOLD. Hausser une limite ou modifier le catalogue pour obtenir un vert masquerait l’écart : options écartées. Les anciens contrats byte-pinnés sont conservés ; l’admission descriptive est enregistrée dans son document propre et le registre, sans réécriture historique.

## Conservation et clôture

Preuves privées : `/Users/martinfeldmann/auren-review/sci-build01-delivery-evidence-20261126`. L’archive CLI ajoute cinq exigences canoniques ; OpenSpec strict passe 32/32 après remplacement du Purpose généré en placeholder. Le warning historique du titre « What Changes — … » reste non bloquant. Le snapshot de tâches conserve un seul suivi administratif pour publication/CI/nettoyage. La CI de closeout et le nettoyage ne sont pas encore déclarés terminés à cet instant ; le reçu privé FINAL_LIVE_RECEIPTS.json et la PR de closeout établiront leurs SHA et résultats, sans réécrire cet instant d’archive. Aucun autre worktree ni appareil n’est à nettoyer dans ce scope.
