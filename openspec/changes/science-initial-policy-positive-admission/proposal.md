# Why
L'étape négative est déjà livrée/archivée (#369/#370, canonique2cddf5da7d8c60bdc74e88ac60a24a36d9b45ad0). Elle protège l'admission mais ne peut produire de premier plan. Le modèle v2 opérationnel/qualitatif ne satisfait pas la représentation READY v1 ; l'absence d'une base temporelle applicable subsiste. Rejouer le build négatif ou ajouter un autre évaluateur négatif ne ferme pas cette dépendance.

# What Changes
- Définir explicitement le contrat successeur v2 (requête/résultat et références de binding) et sa compatibilité PLAN, au lieu de relâcher v1.
- Distinguer couverture qualitative des quinze zones, éventuelle comptabilité conventionnelle et réponse physiologique non estimée.
- Décrire prescriptions de bootstrap et réglages observés sans conversion en kg ni charge froide inventée.
- Conserver les six gates et la durée complète admise dans le budget avant READY. Nommer les données/décisions réellement manquantes ; pas de constantes pour les contourner.
- Préparer oracles et responsabilité des sources. Ne pas réimplémenter l'étape1 ou activer un producteur/runtime pendant cette préparation.

# Capabilities
## New Capabilities
- `science/first-plan-v2-binding` : représentation et conditions d'admission du successeur, côte à côte avec v1.
## Modified Capabilities
- Aucune exigence canonique modifiée à ce stade. Le contrat v2 est revu et exporté sous GO isolé ; il reste non servi et ne fournit pas d’admission positive. Le sens et les validateurs READY v1 restent inchangés.

# Impact
Propriétaire SCI : ce change et docs/science/sci-p02-initial-policy/positive-admission-01/. Futur apply à approuver : nouveaux modules/schémas/fixtures versionnés dédiés, puis binding/producteur seulement avec preuves admises. Aucun changement app/mobile, service corporel, catalogue/E0, registre historique ou API. PLAN consommera une version explicitement négociée dans son change distinct.

# Approval boundary
« ok go » autorise la continuation du chemin critique et la préparation concrète de la prochaine admission ; il ne remplace ni une preuve scientifique, ni les décisions de politique, ni la revue du nouveau contrat requise par CLAUDE.md§6. Ce dossier prépare le choix v2 recommandé précédemment et le scope d'apply suivant. Aucun GO de collecte de données personnelles, déploiement ou ouverture DATA/PLAN/MOB04 n'est inféré.

# Completion
Préparation terminée quand représentation, invariants, compatibilité, tests et décisions bloquantes sont revus. Le futur apply peut livrer un contrat sans positif fictif, mais ne doit pas annoncer cette livraison comme admission positive. Admission positive complète seulement avec SCI-POS01..07 satisfaits ; sinon décision explicite et preuve/protocole manquant identifiés.

# Apply isolé après revue
Le GO explicite « Valider le contrat v2 et ce build isolé » est enregistré dans BUILD_AUTHORIZATION.md. Cette PR livre uniquement le contrat/types/schémas/validations/tests et leur closeout. Les critères positifs SCI-POS01..07 sont conservés sans réduction dans docs/proposals/science-initial-policy-positive-admission.md et le parent. La fermeture du contrat ne signifie ni admission du bundle ni succès de ces preuves.
