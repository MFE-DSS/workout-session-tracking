# SCI admission — tasks du seul apply étape1

Autorisation : [BUILD_AUTHORIZATION](BUILD_AUTHORIZATION.md), « Valider uniquement ce build SCI isolé ». Le design initial comporte aussi des travaux futurs ; leurs critères sont conservés distinctement ci-dessous. Aucun GO positif/READY/runtime n'en découle.

## 1. Préparation et bornage
- [x] Audit C1..C6, douze sorties, provenance/pins et limites, protocole temps et handoff préparés.
- [x] Revues fraîches builder/science du design, aucune Important résiduelle.
- [x] GO BUILD étape1 reçu ; préserver v1/v2 et quatre autres paquets hors PR.
- [x] Plan précis et tests RED écrits avant diagnostics/verifier/fixtures.

## 2. Apply étape1 autorisé
- [x] Diagnostics successeurs calibration : ancien historique non actif, concerns conservés.
- [x] Vérification stricte des types contre recomputation v2 ; bool/int/float/nonfinite refusés.
- [x] Borne basse partielle sûre disjointe réellement consommée, sans Duration/READY.
- [x] Registre vide piné et évaluateur à six gates négatives, versions/digests/empreintes complets.
- [x] Dix-huit fixtures issues du vrai évaluateur sur faits synthétiques, refus/invalidations non servis.
- [x] Exécuter `python scripts/check_scope.py` et minimum du tier final, broad science, pins historiques, Ruff/budget/Bandit/protocole/OpenSpec.
- [x] Revues code et science indépendantes, correction Important avec régression RED→GREEN.
- [x] Commit/push/CI PR exacte et merge commit sous GO permanent réalisés ; contrôle canonique/Sonar et closeout tracés dans la PR vivante après exécution.
- [ ] Reçu, archive de ce seul scope et cleanup sans travail unique ; handoff négatif à PLAN.

## 3. Critères différés conservés — NON ACQUIS, hors GO étape1
- [ ] Admission positive des six gates sur bundle exact, reviewers/décisions applicables réels.
- [ ] Protocole initial opérationnel admis et préparation réellement temporalisée.
- [ ] Choix explicite projection numérique v1 ou contrat successeur revu avec consommateurs.
- [ ] Base temporelle positive applicable (modèle/convention admise), collecte/validation sous autorité si nécessaire.
- [ ] Binding positif/producteur de plan/fixture READY réels, jamais autorité de test promue.

Ces cinq éléments sont repris sans réduction dans le handoff et restent sous le parent science-initial-plan-policy. Un prochain apply exige son delta et GO distincts ; la réussite de l'étape1 n'est pas la réussite de ces critères. MOB03, DATA/PLAN/RELEASE et runtime restent ouverts.
