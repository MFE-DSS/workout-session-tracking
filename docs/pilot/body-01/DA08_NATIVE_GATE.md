# BODY — gate natif DA‑08, 14 novembre 2026

Famille acceptée : « Accepter la famille DA‑08 », call_cbab5c2ca76c4afd8bb803eb3115f699.
Reçu DA08_FAMILY_ACCEPTANCE.json. Canonique relu 1462482a4e2bcd1fcde121d6f207a2131616e849,
checkpoint BODY f899b735486e1e258982462ae8f7b96ad15f6984, PR407 draft.

## Reconstruction vérifiée

Surface ouverte, actions intégrées, mémoire à échelle/jours réels et sources ;
création simple, correction et bilatéral utilisent la famille acceptée. Parseur,
clear explicite, jour source/date seule, héritage hors bornes et ports conservés.
Aucun modèle, migration ou endpoint nouveau dans cette reconstruction.

Vrai ConnectedApp iOS26.3 390×844, entrée Progrès, IME décimal/virgule/Terminé,
création réelle puis confirmation, correction réelle de racine8 (original71,4,
version2 71,2 ; autres champs conservés), versions lues. Témoins synthétiques.
Dynamic Type accessibility-medium : reflow et clavier observés, contenu secondaire
défilable. Le viewport et les modals possèdent leurs safe areas ; aucun changement
des primitives/tokens/D4. Rotation/focus/VoiceOver exhaustifs non certifiés.

Après retrait de l'accord : aucune mesure numérique dans le lecteur de gestion.
Sélection propriétaire relue, confirmation explicite puis panne503 injectée après
commit serveur de l'effacement synthétique11. Même request_id durable après kill,
aucun grant pour récupérer, GET exact200 et un seul POST au total. Sauvegarde SQLite
privée avant test ; reçus et captures dans le dossier de preuves.

## Vérifications actuelles

- 100 suites /1215 tests mobiles et TypeScript PASS, après les derniers correctifs.
- Backend ciblés179 PASS ; broad lecteurs/SSR/migration244 PASS. Campagnes distinctes,
  chevauchement possible, pas de total unique inventé.
- Ruff fichiers neufs, budget260≤548, Bandit applicatif, protocole et OpenSpec25/25.
- Gitleaks sur les sources modifiées : aucune détection. Scan arbre entier : un
  résultat dans docs/SONAR_AUDIT_01_REPORT.md identique au canonique et hors diff ;
  aucun secret reproduit ni déclaration globale d'innocuité.
- Revue indépendante entière puis addendum limité au nouveau portage de correction :
  aucun Critical/Important. Mineurs symbole manuel/selection et busy/expanded
  corrigés avec RED→GREEN. Les corrections finales ne sont pas une seconde revue.

## Board et décision

Board unique : http://127.0.0.1:8260/ ; sources/captures/logs/reçu de reprise.
Preuves persistantes : /Users/martinfeldmann/auren-review/body-da08-integration-20261114/.
La référence acceptée vient du banc antérieur distinct ; les cohortes ne deviennent
pas un faux avant/après de données identiques. Prototype : simulateur dédié
AUREN-BODY01-FINAL-20261111, exp://127.0.0.1:8251, backend loopback8250.

Android : clone dédié tenté sans cible ADB exploitable ; seul son PID vérifié a été
arrêté. Aucun nouveau PASS Android/IME/Retour/grande fonte/physique. Pas de shim du
module natif absent. Les références Android DA‑08 sont historiques et étiquetées.

**Pixels BODY acceptés globalement avec réserves de finition**, le 14 novembre :
« Alors oui, globalement, j'accepte les pixels […] Mais sinon c'est OK. »
Reçu DA08_NATIVE_ACCEPTANCE.json et POLISH_BACKLOG.md. Le ZIP présenté reste figé
(SHA256 fb8bdae85ff957b41087e6198bfb2d9c78a02862d17ea3408863e0904f7a299e).
À cet instant d'enregistrement, aucun commit UI, nouvelle CI ou merge de cette
reconstruction. Les contrôles du HEAD final suivent le gate humain ; les anciens
résultats ne les remplacent pas.
NUT/MOB06 conservés sans modifications (statuts/HEADs comparés). Ensuite finaliser
#407 sous GOV-MERGE-01, puis vrais parents NUT406/MOB06408. Aucun APK/OTA/déploiement.

## 15 novembre — vérification locale finale

Pixels acceptés la veille ; sources produit inchangées depuis les rendus.
Campagne complète438 fichiers :8597 PASS/1ignoré. Arrêt mémoire1613>1600Mo,
puis tous les74cas de recovery-home,97cas de préférences et178fichiers restants
passants sur les mêmes empreintes, sans hausse du plafond. Les quatre contrôles
de migration passent ; mobile100suites/1215 et TypeScript passent. Reçu
FINAL_LOCAL_RECEIPT.json dans le dossier persistant, synthèse versionnée
LOCAL_VERIFICATION_20261115.md. Aucun PASS CI ou merge encore anticipé.
Banc8250/8251 et simulateur BODY arrêtés après acceptation ; ancien clone qemu5592
resté vivant après SIGTERM, même PID/commande/cwd relus puis SIGINT confirmé.
Aucun autre appareil arrêté, aucune suppression de données.
