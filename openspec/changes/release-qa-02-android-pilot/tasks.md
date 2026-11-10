## 1. Preparation
- [x] Réconcilier canonique/contrats et préserver checkout/worktrees.
- [x] Vérifier graphe natif verrouillé, session EAS et profil existant sans lancer pilot public.
- [x] Documenter choix, périmètre et blocages observés.
- [x] Obtenir revue/GO du delta de configuration avant apply, avec direction du testeur distant.
## 2. Authorized build
- [x] Ajouter profil/config HTTPS QA bornés et passerelle, tests de refus et préservation hors QA ; aucun cleartext/Metro.
- [x] Préparer backend SQLite/bundle/autorité synthétiques et migrations réellement vérifiées ; retrait/restauration de test et identité HTTPS.
- [ ] check_scope puis checks appropriés, tests consommateurs, revue indépendante et CI exacte.
- [ ] Construire EAS internal APK ; archiver source/identité/signature/build/URI/empreintes.
## 3. Device and delivery
- [ ] Installer sur Android physique autorisé et vérifier absence d'exception native.
- [ ] Exécuter la checklist avec PASS/FAIL/UNAVAILABLE et preuves séparées HTTP/émulateur/physique.
- [ ] Tester retrait/rollback du seul banc ; pas de suppression de données ou déploiement partagé.
- [ ] Livrer APK/checklist/résultats, merge gardé si readiness, canonique/Sonar et closeout borné.
