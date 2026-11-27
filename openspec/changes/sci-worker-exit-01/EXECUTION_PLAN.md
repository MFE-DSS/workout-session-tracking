# SCI-WORKER-EXIT-01 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans.

**Goal:** sortie explicite sûre du seul enfant après obligations complètes.
**Architecture:** main conserve les finally métier ; point d’entrée termine après statut+flush.
**Tech Stack:** Python3.11.14/Linuxamd64, SQLite3.46.1 pour qualification ; pytest local complémentaire.
**Spec:** specs/science/documented-muscular-exposure/spec.md et AUTHORIZATION.md.

## Global Constraints
Produit : worker.py uniquement ; tests : test_muscle_observed_load_worker.py. CPU2/3s,AS512Mio,wall3s,SQL4096,VM2M,sortie1Mio. LecteurDISABLED ; aucun cloud/QA/infra/mobile.

## Review Focus
- Flush qui échoue après écriture valide : aucun statut0.
- Fermeture readonly échouée : pas de résultat admis.
- Pipe partiellement écrit/rompu : refus et parent nettoyé.
- DTO/digest ou JSON invalides : pas de sortie réussie.
- Signal après sortie valide : refus et slot libéré.

### Task 1: Terminaison contrôlée et preuves
**Files:** worker.py, tests/test_muscle_observed_load_worker.py.
**Interfaces:** main() retourne0/1 ; supervisor.collect_child conserve exitcode/time/output ; parent DTO strict et owner/window.
- [ ] Écrire test de teardown coûteux au vrai point d’entrée et erreurs déterministes (flush, pipe, validation, close). Expected: RED pour fin/flush/digest non gardés, témoins déjà sûrs verts.
- [ ] Exécuter check_scope avant pytest ; conserver RED complet.
- [ ] Ajouter minimum de contrôle et finalisation uniquement dans worker.py.
- [ ] Rejouer le module et broad lecteur ; Expected: PASS, skipsLinux locaux explicités.
- [ ] Requalification native avec fixtures canoniques exportées14V3/mixte100, cas Legacy/adversariaux ; Expected: sorties0/digests sûrs et aucun dépassement nominal, sinon HOLD.
- [ ] Revue indépendante du diff complet ; fixes en scope RED→GREEN.
- [ ] Commit/push/PR/CI exacte puis merge autorisé et closeout ; aucun commitUI.
