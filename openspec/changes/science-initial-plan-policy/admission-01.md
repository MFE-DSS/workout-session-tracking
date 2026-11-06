# SCI-P02-ADMISSION-01 — delta de recherche et réalisation isolée

6 novembre 2026. Base e9640da. Mandat opérateur SCI-P02-ADMISSION-01 : admission D1–D4, modèle de faisabilité, artefact versionné, tests et revue indépendante ; aucun service. Ce delta précise la tranche scientifique déjà ouverte, sans étendre ses frontières API/UI/données. L'ancien GO BUILD du producteur et le présent mandat autorisent uniquement les outils purs et artefacts isolés décrits ici. L'admission partielle ne donne pas autorité au producteur de prescrire.

## Brainstorming / Options / Risques / Choix retenu

A. Durée ponctuelle : rejetée, travail/échauffement/installation/apprentissage non bornés.
B. Intervalle total : pas de borne haute défendable ; conserver seulement une borne structurelle partielle.
C. Faisabilité : retenue, calcul de repos intramouvement strictement séquentiel. Si le budget est inférieur ou égal à cette borne et du travail reste nécessaire, la configuration proposée dépasse le budget. Sinon TIME_UNCERTAIN. Ce n'est pas une preuve qu'aucun autre plan existe.
D. Calibration personnelle : cible ultérieure, exige observations contextualisées et validation hors échantillon ; pas de constante ni nombre minimal de séances choisi ici.

Risque central : transformer la permission scientifique d'une convention en certification individuelle. Choix : artefact0.2.0-partially-admitted de décisions, non enregistré comme politique approuvée ; producteur1.0.0 et v1 immuables. Deux séries/8–12/2RIR/90–120s peuvent être évalués comme bootstrap conventionnel, sans optimum ni sécurité universelle. Sélection et complétude de catalogue restent gates distinctes.

## Contrat du diagnostic de temps

Entrée : slots prescrits non vides, work_sets entier positif, rest_seconds entier positif ou null, budget entier positif ou absent. Structure explicitement TRADITIONAL_SEQUENTIAL, sinon UNKNOWN. Aucune inférence de tempo ; aucune addition d'attente ou transition. Somme des (work_sets−1)×repos connus ; pas de repos après le dernier set du mouvement, pas de multiplication par tous les sets, pas de cumul automatique entre exercices. Les autres composantes restent inconnues et peuvent chevaucher le repos.

Sortie isolée : borne des seuls repos connus, composantes manquantes, feasibility UNKNOWN/NOT_FEASIBLE et issue TIME_UNCERTAIN/CONSTRAINT_VIOLATION (vocabulaires v1 existants). Duration v1 reste UNKNOWN avec bornes/model_ref null ; v1 interdit une borne unilatérale dans Duration. La borne diagnostique ne devient pas un Plan v1, aucun nouveau statut de transport.

## Plan de réalisation (exécution inline)

- [x] Recherche vérifiée, admission D1–D4 et limites source par source ; conserver les IP historiques, citer E0 existant lorsque pertinent. Nouvelles sources bibliographiques restent proposées pour promotion E0, aucun second registre de preuve ni reconstruction silencieuse du catalogue épinglé.
- [x] Tests RED du diagnostic pur `tools/science_initial_policy/time_feasibility.py::assess_time`, puis implémentation GREEN. Égalité, repos manquant, un seul set, structure appariée, entrées invalides ; gros budget ne donne jamais READY.
- [x] Artefact de décision0.2.0 et audit reproductible des candidats/15zones via les vrais diagnostics1.0.0 ; tests des références, conventions/preuves et conservation des empreintes historiques.
- [x] Fixtures de diagnostic, schémas/fixtures historiques inchangés ; broad scientifique, lint/budget/sécurité/protocole/OpenSpec selon check_scope.
- [ ] Revue scientifique indépendante et jugement code séparé ; corrections démontrées, publication/CI sous GO permanent. Garder le change global ouvert tant que READY/runtime restent bloqués.

## Focus de revue

Repos qui chevauche autre travail → aucune borne séquentielle sous superset ; budget égal au repos seul → travail strictement positif encore requis ; candidat manquant → lacune, pas substitution arbitraire ; crédit inconnu → pas0 ; nouvelle admission → jamais réécriture de l'identité0.1.0.

## Frontières

Aucun fichier app/, client, schéma SCI v1, source catalogue/E0, contrat visuel, asset, API ou migration modifié. La promotion des nouvelles références E0 demanderait une release cohérente du catalogue et des pins historiques : documenter son delta pour la revue, sans le réaliser en concurrence. PLAN-03 seulement partiellement résolu ; PLAN04–06 et MOB04 reçoivent un handoff, aucun GO BUILD runtime.

## Relevé d'exécution avant publication

TDD26rouges/1vert puis28passants ; broad422passants/1ignoré. Deux revues indépendantes : scientifique PARTIALLY_ADMITTED et technique APPROVED, aucun Critical/Important. Suggestions de bibliographie récentes intégrées après vérification ; Minor technique sur Mapping mal formé différé (refus sûr, aucune faisabilité inventée). Ruling : conserver le producteur et schémas existants, ne pas reconstruire le catalogue/E0 épinglé pour admettre artificiellement un plan ; coût assumé, aucune fixture READY. Les conclusions portent uniquement cette tranche, pas les cases globales restées ouvertes.
