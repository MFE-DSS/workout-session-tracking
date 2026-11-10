# REL-03 — vérifications contractuelles et consommateurs

## Négatifs obligatoires
- Candidat sale/non fusionné/CI manquante/approbation absente → aucune publication.
- Cible non attestée, tunnel/temporaire, production, projet/channel/plateforme différents → refus fermé.
- APK QA02 Updates disabled/runtime absent → jamais déclaré OTA-compatible.
- Module/plugin/native config/local-schema modifiés ou empreinte différente → nouvel APK ; aucun contournement du runtime SDK.
- Source native et JS différentes après OTA → identité distincte, pas réattribution du Git SHA du binaire.
- Certificat différent ou versionCode réutilisé → upgrade/distribution refusés.
- DB neuve avec user_id réutilisé, snapshot incomplet, refresh/subject_ref non conservés, rotation refresh concurrente pendant capture ou source écrivante après bascule, schema/FK/autorité inconnus → cutover refusé, anciens faits conservés.
- Backups manquants/corrompus, restore vers chemin existant, downgrade incompatible → refus avant mutation historique.
- Procès serveur/gateway mort, DB indisponible, autorité retirée, upstream redirects/timeout → transport honnête ; pas de READY/DENIED scientifique fabriqué.
- Compte/email non attribué, path traversant, requête surdimensionnée/lente ou réponse secrète → refus sans acquisition.
- Environnement GitHub non protégé/secrets non configurés → job publiant bloqué, job prepare possible.

## Preuves réelles
1. Copier base QA synthétique complète par SQLite backup API vers copie isolée ; comparer tables/PK/FK/auth, snapshots, source events, commandes idempotentes, bindings, typed set facts ; ne pas utiliser restore JSON legacy.
2. Démarrer le nouveau paquet serveur en environnement isolé, rebooter sans seed/requalification, vérifier persistance, health/version exacts et retrait SCI séparé. Mesurer sous budget CPU/RAM cible ; pas de plan payant déclaré suffisant sans mesure.
3. Upgrade réel sur émulateur possédé : installer APK QA02, créer login/pending/draft, conserver empreintes SQLite/owner, installer nouvel APK même signature sans uninstall, relancer/auth/session/unité/A-B/offline/reconnexion et journal sans perte.
4. Source/build/manifest/DEX/signature/URL/runtime/channel réels ; module notifications conservé. Compte source du build, nouveau versionCode et checksum vérifiés contre reçu final.
5. OTA : vrai SDK/client installé sur canal QA autorisé, empreinte compatible, publication de métadonnées JS consommées B, download/launch réel, updateId/isEmbeddedLaunch/sourceJS et nativeversion constatés ; redémarrer, conserver token/SQLite/session ; rollback connu/embedded constaté. Incompatible runtime refusé/classifié sans livrer code natif manquant.
6. Rejouer parcours7→V3→ack exact→même séance et contexte MACHINE_DISPLAY_KG/PER_IMPLEMENT via vrais consommateurs. Les calibrages synthétiques ne deviennent pas des séries physiques ni une permission actuelle offline.
7. Reprendre checklist QA02 avec résultats HTTP/émulateur/physique distincts et échec→réconciliation conservé. Appareils personnels non touchés. Physique UNAVAILABLE jusqu'au testeur ; présence d'une capture ne clôt rien.

## Gates
check_scope avant vérifications ; tier conservateur ci_infra si YAML/package/lock, full sweep local uniquement par `scripts/run_local_sweep.sh` avec garde mémoire ; pas de `pytest -n auto`, ni full CI script sur poste. Tests ciblés + broad consommateurs, TypeScript/Jest, sécurité/dépendances/protocole/OpenSpec, vraie CI finale/canonique et revues indépendantes. Baselines verrouillées, exposition humaine si pixels changent. Aucun seuil affaibli.

Paquet indépendant prêt sans fournisseur = PREPARED seulement. COMPLETE exige cible stable servie + nouveau APK réellement installable + chemin de release réellement vérifié et reçus exacts. Aucun succès à cocher par anticipation.
