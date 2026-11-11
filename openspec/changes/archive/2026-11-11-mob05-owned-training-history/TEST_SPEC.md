# MOB-05A — tests de contrat et consommateurs

Tests futurs après GO, aucun PASS produit prétendu dans cette préparation.

1. Vrais GET authentifiés : propriétaires A et B, orphelins et inconnus rendent des 404 indistincts. no-store au succès comme à l'échec, aucun user_id choisi par le client, DB inchangée avant/après lecture. Limites strictes : booléens, nombres non finis, types et curseurs signés altérés ou étrangers refusés.
2. Périodes4w/12w/all, semaines partielles, DST IANA, until serveur figé, pagination keyset/live/ID réutilisé/restore ; entry_ref changed409 et aucune sélection fusionnée. Insertions supérieures plafond filtrées sans promesse lifetime.
3. Comptes fenêtre entière ≠ première page ; completed sans work fait ≠ réalisée, excluded distinct, SCI comptée sans score,0reps explicite distinctNULL, semaine courante partielle et pas adhérence/cadence→plan ; all sans agrégat illimité. counts_read_at/rows_read_at distincts, refresh remplace.
4. Raw legacy : template modifié/supprimé ne produit aucune ancienne dose ; valeurs0/NULL/warmup/incomplet/dateabsente conservées, aucun overload/delta/score appelé. Nom unresolved reste lisible au détail sans fausse identité.
5. SCI réel : créer et journaliser via vraies autorités/service, lire après retrait génération, mauvais binding/owner/slot/setting/semantics/date/revision refusé. 20PER_IMPLEMENT ne devient40TOTAL ; machine17.5 reste affichage. Prescrit absentdifférentobservé non réparé. Comparaison refusée si contexte inconnu/différent ; aucune courbe reliant legacy non contextualisé, aucun derivedmetric SCI.
6. Index/occurrences : lots200/plafond1000, scan0matchPARTIAL pasEMPTY, cursorsource!=display, namespaces séparés, références/dédoublonnage parlecture et fetchV3 seulement occurrence choisie, pas N+1 moteur pour graphe.
7. Vrai GET poids via BodyMeasurement/WeightHistoryClient/Resource : consent403/flag404/auth/empty/unknown ; aucun User/poidsfeedbackfallback. Période filtremeasured_at, même date+idsdistincts, invalidnonfinite/out-of-current-bounds conservés hors graphe et gaps, mesureisolée, paginationpartielle1000/borneinférieure/absenceaprèsépuisement ; aucune moyenne/prediction/interpolation.
8. Client/resource : A→B→A, logout, période/sélection mutées pendant GET, réponse retardée et pageéchouée, tokenrefresh, repriseoffline sanscachepersistantpromis ; aucun fait A rendu sous B, faitsanciens mêmeowner marqués et suiteperduepasfinliste.
9. Vrai wiring ConnectedApp→ShellContext→routeProgrès : lectures effectives, détailslegacy/V3 readonly sans commandes ni hostmutable ; unjournal/contrôleur, Today/calibrage/exécution/close inchangés. RetourAndroid niveaux puiscoque, clavierferméquandpasinput, focusAX/texteagrandi/safeareas/reducedmotion.
10. Board iOS/Android source-labellé avec vraiscomposants et HTTP synthétique, avantaprèsréférence, acceptationpixelsavantcommit ; APKQA02source distincte et physiqueUNAVAILABLE sanstesteur. Tests ciblés+broad réels seloncheck_scope ; CI obligatoire exacte/visualgate77inchangé/pasbaselineauto ; revue indépendante donnéesetnatif.


## Revue complète : régressions et témoins

Couvrir 503 après page confirmée, invalidation de scan poids au démontage, valeurs
legacy inf/entier non sûr, SCI complété sans observation, lien séance→exercice
exact et unique, se_id sélectionné visible, référence inventée refusée, réponse
tardive A/B ignorée, identité modifiée→409 puis faits lisibles avec référence neuve.
Les comptes de suites larges et reruns ciblés restent séparés dans la livraison.
