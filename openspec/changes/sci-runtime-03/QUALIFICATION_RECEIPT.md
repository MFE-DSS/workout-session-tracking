# AUREN — SCI-RUNTIME-03 : reçu et décision exacte

26 novembre2026. Parent vérifié `3d4c7577e5ffd39fb59de58d1aab3bded1936edb`.
**Banc natif exécuté et nettoyé. Lecteur toujours désactivé / NOT_QUALIFIED. Aucun correctif produit ni nouvelle CI livrés.**

Le dossier de décision contient quatre fichiers ; seul BUILD_AMENDMENT.md porte la demande de GO. Les bases, profils et tokens synthétiques restent dans les preuves privées, hors de ce paquet.

## Résultat utile

- Linuxamd64 **natif** sur le VPS existant, image config `sha256:5ee90ab09696c4312cbe2a99654d5d2368d26f2050839858cca0ec801128334e`, Debian13.3/Python3.11.14/SQLite3.46.1. SourceGit3d4c757 montéeRO et3347fichiers vérifiés. Ce n'est pas une image de déploiement reconstruite.
- Limites maintenues :1CPU/2Gio/sansswap, UID10001/caps0, enfant2/3sCPU,512MioAS,3swall. Les imports dominent (~1,22sCPU du nominal instrumenté) ; le double parsing du même catalogue coûte ~0,29sCPU au total. Mesures de sondes et de processus intact séparées.
- Nominal Legacy, V3 et100faits : succès observés. **Des V3 nominaux échouent aussi sur SIGXCPU vers2sCPU** ; conserver leur refus, même avec un JSON déjà écrit. La qualification n'est donc pas acquise.
- Défaut de digest prouvé : la validation du DTO transforme une valeur entière admissible en float ; le hash avait été calculé avant cette normalisation. Le parent actuel valide le format mais ne recalcule pas ce hash. Les comparaisons de champs seules n'en prouvaient pas l'intégrité ; les nouveaux témoins la vérifient séparément et conservent les échecs.
- Prototype privé (non livré) : une seule admission/parsing pour des octets identiques après chaque attestation, puis hash sur DTO final. Les3V3 terminent en1,602–1,795sCPU ; leurs champs comparés restent identiques et leurs digests recalculés concordent. Les copies indépendantes proposées restent à mesurer sur le futur vrai code.
-500/501séries : refus de ressources observés. W500 est un plafond de scan, **pas une promesse de500faits servis**. La sortie500faits dépasse aussi le plafond lexical65536 du parent. Ce refusUNAVAILABLE est conforme ; aucun relèvement de budget proposé.

## Sécurité et ressources effectivement éprouvées

HTTP réel loopback isolé : A200/reps9, B200/reps999, vide200/EMPTY ; sansBearer401, injection de chemin422, concurrence200+503. Aucune écriture de la base aprèsGET. Snapshot WAL : ancien9 conservé pendant une écriture concurrente vers88 ; nouvelle lecture88, intégritéOK. DML depuis la capture refusé.

SQL instrumenté :13/34/653/2003appels execute pour nominal/V3/100faits/préfixe ancien ; compteur applicatif19/57/1003/3203. Les mesures au pas1 donnent1730/2194/64622/142233instructions diagnostiques. Le compteur de garde au pas1000 n'est pas un total exact. Le témoin adversarial atteint le budget2millions et est refusé ; timeout et débordement de pipe tués/reaped. Le témoinCPU est tué/reaped, allocation600Mio refusée sousAS512Mio. Pic du conteneur de campagneHTTP181469184octets ; ne pas confondre ce pic parent+enfant et le RSS individuel.

Sources/autorités du candidat :3885entrées inspectées, root-owned sansbits022/ACL/symlink inattendus ; écriture et renommage refusés sousUID10001. Ancêtres réels des volumes vérifiés. Le volume SQLite est volontairement propriétaireUID10001 et isolé. Les essais de remplacement étaient séquentiels : aucune résistance à un administrateur privilégié modifiant un futur déploiement n'est revendiquée. **Confiance opérationnelle futureHOLD.**

## Contrôles et conservation

Local :332PASS/4skips de plateforme, budgetRuff260≤548, protocole documentaire et OpenSpec strict passants. Aucun nouveau Python produit ; pas de full sweep local. Ces tests ne sont pas une CI de correctif. Revue indépendante : défaut d'admission parent et différence catalogue valide/pin invalide corrigés dans le dossier ; aucun Important documentaire restant. Revue du futur code non encore réalisée.

Nettoyage normal de nos seuls conteneurs/volumes locaux et VPS, images conservées ; bases/bundle/profils synthétiques et logs archivés en privé. Les dix conteneurs préexistants et cinq états de services sont identiques avant/après. Seul l'ordre non sémantique de la liste Docker Mounts a dû être normalisé par Destination ; tous les champs sont conservés. Aucun autre worktree n'est modifié par ce scope.

## Une décision pour poursuivre

Autoriser **BUILD_AMENDMENT.md** : trois modules du lecteur et leurs trois tests, réutilisation confinée avec autorités indépendantes/vues séparées, digest du DTO final, requalification native, revue et CI du HEAD réel puis livraison gouvernée. Aucun budget, writer, SCI, TIME-01, SQL, DTO/schema, mobile, QA ou release à modifier.

Le lecteur conserveHOLD jusqu'aux preuves du code réel. L'autorisation du banc ne remplace pas ce GO produit. Pas de demande de merge routinière après ce GO si les gates sont satisfaits.
