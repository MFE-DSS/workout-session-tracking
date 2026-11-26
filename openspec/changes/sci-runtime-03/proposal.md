# SCI-RUNTIME-03 — attribution et réutilisation bornée du catalogue

## Why
Le nominal du lecteur canonique tient dans les budgets du banc Linux amd64 natif. Ses imports dominent le CPU et le parsing du catalogue courant est répété. Les témoins à500 faits atteignent la limite CPU ; leurs sorties doivent aussi satisfaire les plafonds lexicaux et le DTO du parent. Un JSON écrit ne constitue pas une lecture admise.

## What Changes
- Exécuter les expériences synthétiques et la qualification du banc natif explicitement autorisé, sans activation QA.
- Proposer la réutilisation intra-job de la seule vue du catalogue courant déjà attestée, sans cache inter-propriétaires, avec partage de parsing entre racines uniquement pour les mêmes octets indépendamment attestés, sans changement de budget.
- Corriger le digest de résultat calculé avant normalisation du DTO, sans modifier ses faits.
- Conserver les refus de ressources et les résultats UNKNOWN/PARTIAL/UNAVAILABLE ; ne pas promettre500 faits retournés depuis le seul plafond de scan500.
- Séparer la qualification du banc, celle d'un futur déploiement et toute autorisation d'activation.

## Capabilities
### Modified Capabilities
- `science/documented-muscular-exposure`: admission et confinement d'une vue courante déjà vérifiée dans le même worker.

## Impact
GO d'analyse/banc et **GO produit reçus le26novembre2026**, voir AUTHORIZATION.json. Correctif appliqué dans le scope ; qualification native et livraison encore soumises à leurs preuves. Scope exact : `worker.py`, `provenance.py`, `projection.py` et leurs trois fichiers de tests existants, plus documents du change et reçu. Aucun changement de SCI, catalogue, DTO, SQL, CI, mobile, budget ou service QA. Le prototype AST n'est pas du code produit livré.
