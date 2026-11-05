# SCI-P02-INITIAL-POLICY — producteur isolé1.0.0

**IMPLEMENTED / NOT_SERVED. Politique0.1.0-proposed non admise.**5novembre2026. Base5fd18c3 ; FirstPlanClient de PR3530ee7ba3 vérifié sans modification. GO BUILD : « Valider le build isolé proposé ».

Lire le [rapport courant](REPORT.md), les [décisions/handoff](DECISIONS_AND_HANDOFF.md), puis le [design](../../../openspec/changes/science-initial-plan-policy/design.md) et les [sources/audit](EVIDENCE_AND_AUDIT.md).

API pure : `load_registry()`, `inspect_policy(request,registry)` (diagnostics non exécutables), `produce(request,registry)` (FirstPlanRecommendation v1 validée). Engine `initial-policy-producer/1.0.0` ; input fingerprint canonique ; registres immuables et hashes vérifiés. Aucun import par app/, endpoint ou UI.

[11fixtures](v1/producer-fixtures.json) générées par le producteur testé, depuis des inputs synthétiques ; toutes NOT_SERVED. Vérification : `python -m tools.science_initial_policy.fixtures` ; régénération explicite avec `--write`. Les fixtures canoniques SCI-P01/02 restent inchangées.

Pas de READY aujourd'hui : les paramètres de dose et le modèle de temps ne sont pas admis. Le producteur indique correctement POLICY_UNAVAILABLE, INSUFFICIENT_DATA ou CONFLICTING_DATA selon la requête. La proposition de7intentions/cadence2ou3 n'est pas une dose optimale personnelle certifiée. Les diagnostics ne doivent pas servir à démarrer une séance.

Le [manifest](manifest.json) identifie versions, source de base et hashes d'artefacts ; le reçu de PR indiquera le SHA publié et les contrôles distants. Aucun déploiement ni recette mobile déduit de ce producteur isolé.

[Reçu de livraison vérifiée](DELIVERY_RECEIPT.md) : code #357 mergé1313f2f, CI PR/canonique réussies. Politique/READY restent ouverts ; la gate Sonar canonique historique reste consultative et inchangée.
