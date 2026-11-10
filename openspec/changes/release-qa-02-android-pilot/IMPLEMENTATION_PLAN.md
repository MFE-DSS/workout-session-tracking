# RELEASE-QA-02 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans. Les étapes sont exécutées inline sous le GO contrôlé et la direction distante reçus, sans GO routinier supplémentaire.

**Goal:** APK EAS Android autonome attesté et accessible au testeur distant sur données synthétiques.
**Architecture:** Profil QA séparé, configuration validée et cible HTTPS exacte. Backend local migré et vrai SCI derrière passerelle API bornée/tunnel temporaire ; aucun backend partagé ou production changé.
**Tech Stack:** Expo58/RN0.88 verrouillés, EAS27.2, Python/stdlib gateway, cloudflared existant, ADB/API36 pour preuve émulateur complémentaire.
**Spec:** [design](design.md), notamment la direction distante du10novembre qui remplace l'option USB initiale.

## Global Constraints

- Aucun module supprimé, SDK majeur mis à niveau, pixel/baseline/domaine scientifique modifié.
- QAHTTPS exacte, package distinct, pas de galerie, comptes/valeurs synthétiques uniquement ; aucune signature ou credential dans git/APK.
- Source propre et archive EAS attestée ; modification code/config/lock après build = rebuild.
- HTTP/émulateur/physique séparés ; physique UNAVAILABLE tant que le testeur n'a pas rendu sa recette.
- Check_scope gouverne les vérifications locales ; CI complète réelle avant merge, Sonar consultatif consigné.

## Review Focus

- Variables QA contradictoires : refus avant construction, hors QA configuration historique inchangée.
- Proxy manipulé : aucune sortie vers un hôte arbitraire, aucun accès web/admin/fichier ni framing ambigu.
- Perte d'amont : vraie erreur de transport sans succès ou refus SCI fabriqué.
- Source affichée différente de l'archive : comparaison du SHA EAS et des fichiers effectivement uploadés.
- Testeur distant : APK sans câble/Metro, disponibilité temporaire explicitée, aucun compte réel.

### Task 1: Configuration QA

**Files:** clients/mobile/eas.json, clients/mobile/app.config.js, clients/mobile/qa.config.js, clients/mobile/release-qa-target.json, clients/mobile/src/native/releaseQAConfig.test.ts.
**Interfaces:** qa.config.js applique `applyQA(config, env)` ; consomme cible attestée JSON, produit identité QA/extra sans secret ; configuration normale passée inchangée hors variante.
- [ ] Écrire tests de refus/publicHTTP/galerie/révision invalide/priorité controlled et préservation normale ; observer RED.
- [ ] Implémenter helper et profil qa-android internal/APK autonome ; aucune permission cleartext.
- [ ] Cible réelle renseignée seulement après identité HTTPS attestée ; tests ciblés/Jest/TypeScript GREEN.

### Task 2: Passerelle QA contrôlée

**Files:** tools/release_qa_gateway.py ; tests/test_release_qa_gateway.py.
**Interfaces:** passerelle loopback8141 vers backend fixé8140, `allowed_path(path)` fermé API v1/v3 ; identité expurgée séparée ; CLI avec receipt local, jamais URL upstream arbitraire.
- [ ] Tests RED sur path traversal/URL absolue/admin/framing/taille, forward exact JSON/contrat/If-Match et amont indisponible.
- [ ] Implémentation minimale stdlib, limites corps/concurrence/temps/débit, absence de logs sensibles.
- [ ] GREEN ciblé + broad consommateurs ; revue indépendante de l'exposition avant tunnel.

### Task 3: Build et preuves

**Files:** reçus versionnés/privés et checklist, registre du change ; aucun secret.
- [ ] Finir parcours HTTP vrai sur nouvelle DB, rollback de test et identité packaging/génération.
- [ ] Ouvrir HTTPS temporaire du seul banc revu ; vérifier TLS/identité distante et refus des autres chemins ; figer URL exacte.
- [ ] Scope/checks requis, revue, commit/push/PR/CI ; source propre à l'upload EAS et archive/config/lock empreintés.
- [ ] EAS build qa-android ; conserver ID/URI/source/toolchain, télécharger APK, inspecter signature/manifeste/DEX/JS.
- [ ] Installer/lancer sur émulateur attribué sans Metro et vérifier absence exception ; ne pas rebaptiser en preuve physique.
- [ ] Fournir APK et checklist testeur ; catégories PASS/FAIL/UNAVAILABLE, fenêtre HTTPS et limite DATA explicites.
- [ ] Merge gardé, CI canonique, Sonar, closeout et conservation des seuls services nécessaires à la recette distante.
