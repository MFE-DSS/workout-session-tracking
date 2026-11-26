# Revue indépendante SCI-RUNTIME-03

Relecteur frais : sci03_evidence_review,26novembre2026, lecture seule. Portée : preuves, comparaisons et amendement proposé ; aucune revue de code produit nouveau n'est prétendue.

1. Sortie enfant/JSON ≠ admission parent : conservé et éprouvé par bounded_json, DTO et codes retour. Le refus lexical500faits est attendu selon le contrat, pas une obligation de servir500.
2. Parité des champs ≠ intégrité du result_digest : vérification ajoutée ; défautV3 integer→float prouvé, correctif de producteur proposé aprèsGO.
3. CatalogueB valide différent deA : miss+parsing ordinaire et résultat historique propre. DifférenceB/proprepin : refus. Les scénarios et documents ont été corrigés puis relus indépendamment.
4. Le contexte doit être disponible au parsing interne du bundle, avant ses contrôles finaux obligatoires. Aucun cache ne vaut admission d'autorité.

Verdict final du relecteur : « Point important clos. L'amendement est prêt pour la décision de GO BUILD. » Le coût CPU/mémoire des copies indépendantes et le code livré restent à vérifier après autorisation. Les futurs chemins/configurations QA ne sont pas qualifiés par ce banc.
