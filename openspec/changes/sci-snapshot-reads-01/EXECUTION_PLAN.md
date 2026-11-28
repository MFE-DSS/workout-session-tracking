# SCI bounded snapshot reads Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:executing-plans. Steps use checkbox syntax.

**Goal:** supprimer les lectures SQL redondantes dans une seule capture, sans modifier les autorités.
**Architecture:** caches locaux bornés et copies indépendantes ; transaction readonly et règles SCI inchangées.
**Tech Stack:** Python/SQLite, pytest réel en série ; aucun nouveau paquet.
**Spec:** BUILD_AMENDMENT.md + AUTHORIZATION.md + design.md.

## Global Constraints
Trois fichiers exacts de FILE_LEASES.json. SQL4096,VM2M,CPU2/3s,AS512Mio,wall3s inchangés. Pas de nouveau runtime distant ou image. CI ne remplace pas la qualification exacte d'image.

## Review Focus
Propriétaires distincts ; JSON restitué mutable ; absence puis apparition concurrente ; stockage sous nombreuses identités ; réutilisation après fermeture/exception. Tests réels dans test_muscle_observed_load_sqlite.py pour chacun.

## Task1 — capture locale (produit sqlite_source.py / tests sqlite)
- [ ] Ajouter tests SQLite : premiers accès réels, répétitions sans nouvelle lecture physique, valeurs inchangées malgré mutation d'un résultat, ownerA/B, nouveau snapshot après correction, absences, stockage borné, accès après fermeture et budgets réels toujours appliqués.
- [ ] Lancer check_scope puis observer RED attendu avant produit.
- [ ] Implémenter les trois caches privés bornés ; conserver deadline et clear/close.
- [ ] Vérifier GREEN de ces tests et fichier complet.

## Task2 — projection et parité (test writer_readback uniquement)
- [ ] Construire le témoin100 séances/100 faits avec vrais SourceView/bundle/P07 et port SQLite ; déclarer les références de requête synthétiques.
- [ ] Préserver RED SQL4096 sur l'ancien fichier ; GREEN avec copies/caches sans changer les budgets ni les états.
- [ ] Rejouer le parcours inventory2→START→SET→FINISH réel existant,14 V3, mixte100, isolation, unités et digest.

## Task3 — livraison
- [ ] Tier réel : targeted + broad SCI et consommateurs ; sécurité/OpenSpec ; pas de full sweep local shared_code.
- [ ] Revue indépendante puis PR/CI HEAD exact ; merge si toutes les gates.
- [ ] Archive/closeout, CI canonique et cleanup après preuve d'ancestralité. Image opérationnelle reste non mise à jour ; aucun GO opérationnel déduit.
