# AUREN Science — SCI-P01 / SCI-P02 v1.0.0

Paquet de contrats isolés pour le Blueprint et le premier plan d'hypertrophie. **Aucun endpoint, moteur de prescription ou écran n'est activé.** Le périmètre de réalisation des contrats/tests a été approuvé le5 novembre 2026.

- [Handoff mobile/API et dépendances](HANDOFF.md) — point d'entrée court pour le consommateur, disponibilité réelle et décisions à fournir.
- [Contrat](CONTRACT.md) — champs, provenance, suffisance, états de réponse, durée/allocation/candidats et incertitude.
- [Audit et preuves](AUDIT_AND_EVIDENCE.md) — comportements réellement servis et limites scientifiques.
- [Relevé des18 gabarits et probes](audit_repo.json) — résultats déterministes et versions épinglées, aucune donnée privée.
- [Schemas et 8 fixtures](v1/) — structure proposée, distincte des invariants sémantiques inter-objets.
- [Rapport de validation/livraison](REPORT.md) — commandes, résultats, review, publication et limites.
- [Manifeste canonique](../../strategy/AUREN_MANIFESTO_V1.md) et [change OpenSpec](../../../openspec/changes/archive/2026-11-05-science-blueprint-first-plan/proposal.md).

## Utilisation de vérification

Depuis la racine du dépôt, avec les dépendances Python existantes :

```bash
python scripts/check_scope.py
python -m pytest -q tests/test_science_blueprint_first_plan_contracts.py
```

API de validation : `Blueprint`, `FirstPlanRequest`, `FirstPlanRecommendation`, `input_assessment`, `decision_fingerprint`, `validate_exchange(..., references=ReferenceSnapshot(...))` dans `tools/science_contracts/blueprint_first_plan_v1.py`. `exported_schemas()` produit les trois schémas autonomes présents dans v1 ; le test vérifie qu'ils correspondent exactement aux DTO.

Une fixture avec des données utilisateur suffisantes peut retourner POLICY_UNAVAILABLE : le catalogue historique n'a pas été promu en politique approuvée. Les tests couvrent aussi la forme future de READY avec une autorité **purement synthétique de test** ; ils ne fournissent aucune approbation réelle ni prescription destinée à un utilisateur.
