# Contrat v2 / admission positive — revue du delta proposé

7 novembre2026, base2cddf5da7d8c60bdc74e88ac60a24a36d9b45ad0. Continuation « ok go » après étape1 déjà livrée, aucun code négatif refait. Ce reçu décrit seulement le dossier de prochain apply, pas une admission positive.

Proposition et design : openspec/changes/science-initial-policy-positive-admission/. Contrat v2 détaillé : quinze déclarations qualitatives, prescriptions OBSERVED_SETTING/BOOTSTRAP_PROTOCOL, autorité/version/fingerprints et durée admise complète avant READY. V1 inchangé ; FirstPlanClient/PLAN hors de ce build isolé. Aucun nouveau chiffre, JSON/schema exécutable, module, fixture READY, donnée collectée, API/UI ou activation.

Revue builder fraîche en lecture seule : aucune question importante restante pour un build isolé types/schémas/validateurs/tests. Aucune relaxation READY, autorité fabriquée ou dérive des pins historiques détectée. C3/C6 et le binding/producteur positifs restent explicitement hors de ce build.

Contrôles de préparation : check_scope DOCS, check_spec_protocol passant, OpenSpec strict10/10 et liens locaux vérifiés ; aucun sweep produit local pour ce tier. Pas de commit/push/PR ni nouveau résultat CI revendiqués. Le worktree est conservé avec son travail unique.

Prochaine décision requise par CLAUDE.md§6 : accepter le nouveau delta/contrat avant le build isolé des contrats. Ce GO ne créera pas les preuves C3/C6 ; aucune autre ouverture DATA/PLAN/RELEASE/MOB04 ou collecte/déploiement n'en découle. READY réel demeure bloqué sur les admissions et sources applicables listées dans READY_GATE_DECISIONS.md.
