# SCI-P02-ADMISSION-01 — admission initiale et faisabilité

6 novembre2026. **PARTIALLY_ADMITTED ; READY_NOT_PRODUCED ; NOT_SERVED.** Base canonique e9640da. Le mandat de cette passe demande un verdict scientifique, pas de fabriquer READY. L'ancien producteur1.0.0 et ses onze sorties restent reproductibles ; aucune API/UI, prescription servie, acquisition corporelle ou politique de production ajoutée.

## Brainstorming / Options / Risques / Choix retenu

Le[delta avant code](../../../../openspec/changes/science-initial-plan-policy/admission-01.md) évalue les quatre options de temps. Choix : borne structurelle partielle + classification négative, sans précision fictive. Les defaults peuvent être raisonnables sans être optimums ; cela n'admet pas automatiquement leur sélection contextuelle ni le plan entier. Une nouvelle version de décisions préserve l'ancien JSON et ses hashes. La logique pure est construite en TDD ; la validité scientifique reçoit une revue indépendante séparée du code.

## D1 — ADMIT_WITH_LIMITS

Cadre adulte déclaré, non clinique, objectif hypertrophie,2ou3séances/semaine : périmètre produit défendable, pas test d'aptitude ni exclusion physiologique des autres fréquences. Corps entier est une organisation possible à volume comparable ; aucune supériorité générale revendiquée. La répétition des sept slots est un bootstrap, pas une allocation personnalisée. Passer de2à3séances augmente de50% la dose hebdomadaire du producteur : ne pas présenter cela comme une comparaison de fréquence à volume égal. Aucun jour d'espacement précis ni calendrier personnel n'est inféré.

Inputs requis v1 conservés : objectif, population déclarée, cadence, budget par séance, réponse sur limitations ; provenance et conflits utilisables. Limitations non résolues : revue hors périmètre du filtre actuel, pas diagnostic ni refus médical. Expérience inconnue explicite ; poids/taille/priorités facultatifs. Une priorité déclarée n'est jamais une faiblesse analysée. Pas d'inventaire ; confirmations exercice/contexte progressives possibles.

## D2 — décisions indépendantes

| Paramètre | Admission | Utilité et limites / déclencheur de revue |
|---|---|---|
|2séries par intention | ADMITTED_AS_CONSERVATIVE_DEFAULT | Point de départ par slot, pas minimum biologique ou dose globale faible.4ou6séries directes/semaine pour une intention répétée ;14séries physiques/séance,28ou42/semaine. Les chevauchements changent la comptabilité musculaire. Revoir avec tolérance/adhérence/performance ; pas de progression automatique nouvelle |
|8–12répétitions | ADMITTED_AS_CONSERVATIVE_DEFAULT | Plage pratique modérée, pas optimum ni charge RM connue. Réalisation au poids du corps/unilatérale peut exiger variation ou calibration ; ne pas inventer un lest/assistance |
|2RIR | ADMITTED_AS_CONSERVATIVE_DEFAULT | Cible comportementale de non-échec, pas mesure. La capacité à l'estimer et l'exécution priment ; exactitude inconnue surtout sans familiarisation. Revoir incompréhension, forme et effort observé ; pas d'échec forcé pour calibrer |
|120s poly /90s mono | ADMITTED_AS_CONSERVATIVE_DEFAULT | Convention de repos initiale, pas optimum établi par classe. Peut nécessiter davantage ; ne pas raccourcir pour réussir le budget. Revoir qualité du travail/récupération/budget |
|Charge calibrée, null au départ | ADMITTED_WITH_LIMITS | Aucune formule poids/taille/sexe ni transfert entre exercices. Protocole de calibration concret reste à définir/revoir pour l'exercice et son contexte |

La certitude sur les principes de dose/effort est LOW_MODERATE à MODERATE ; celle sur l'optimalité de ces valeurs exactes est INSUFFICIENT. Les statuts de défauts s'appuient sur E0 existant, avec justifications et limites dans[policy.json](policy.json), pas sur une fausse nouvelle étude du bundle. Hermann2025 (42entraînés, mono-série) apporte un contrepoint : certains gains hypertrophiques favorisent modestement l’échec, sans faire de2RIR un mauvais point de départ ; aucune équivalence absolue revendiquée. La combinaison est une **candidate de bootstrap conditionnelle**, pas encore un plan admis : sept mouvements, contexte, préparation et calibration peuvent rendre la séance trop complexe ou longue. Pas de sécurité universelle ni d'équivalence du résultat individuel annoncée. L'adaptation ultérieure reste un objectif, pas un moteur livré.

## D3 — principes ADMIT_WITH_LIMITS ; sélection concrète NOT_ADMITTED

Audit reproductible[audit.json](audit.json), depuis les vrais filtres et sources épinglées :40identités candidates canoniques dans sept intentions. L'appartenance à ce pool n'est pas une admission individuelle. Attribution brute et crédit0.5 secondaire restent séparés ; UNKNOWN empêche EXACT, ce n'est ni0 ni une preuve d'absence. Une somme de crédits n'est pas une prédiction biologique.

| Intention | Candidats actuels | Conclusion de revue |
|---|---:|---|
|Quadriceps |10|Squat/fente/extension du genou cohérents avec l'intention quad générique ; pas interchangeables comme apprentissage, stabilité ou développement régional |
|Poussée pectoraux |6|Poussée horizontale/PRIMARY conforme, variantes d'angle et contraintes d'épaule non assimilables ; aucune supériorité par ordre lexical |
|Row haut du dos |5|Chevauchement dorsal avec tirage vertical attendu mais non optimalisé ; variante prise large a rôle lats UNKNOWN |
|Charnière ischios |4|Hinge cohérent pour extenseurs de hanche ; ne remplace pas automatiquement le travail de flexion du genou, notamment couverture régionale. Good morning : rôle upper_back UNKNOWN |
|Tirage vertical |5|Tous ont au moins un rôle UNKNOWN (pecs et/ou rear_delts). L'exposition complète v1 n'est atteignable avec aucun candidat actuel de ce slot, même après confirmation matérielle |
|Deltoïde latéral |6|Abduction/PRIMARY conforme ; mono/poly et demande technique diffèrent. Upright row : rôle upper_back UNKNOWN |
|Mollets |4|Intention générique cohérente ; genou fléchi/tendu modifie la spécificité, pas de priorité gastrocnémien déduite du rôle global calves |

Bras : secondaire sans isolation directe ; glutéaux/adducteurs dépendants du choix ; abdominaux/fléchisseurs de hanche sans exposition créditée dans l'exemple. Ce ne sont pas quinze régions directement couvertes ni une analyse de déficits corporels. Sept intentions peuvent définir un démarrage limité, pas certifier une couverture esthétique complète. La pertinence des omissions et de la double traction doit rester visible au prochain audit.

Stabilité : aucune métadonnée dédiée curée dans le catalogue actuel ; UNKNOWN dans l'audit. Machine ne vaut pas automatiquement «adapté débutant». Curation historique reviewed et failure_safe ne prouvent pas la tolérance ni une technique acquise. Exclusions/limitations, équipement exact et réalisation unilatérale demandent vérification. Une exigence matériel RESOLVED est une description de l'exercice, pas disponibilité chez l'utilisateur.

Conserver intention→candidats→confirmation du contexte courant→exécution. La règle de disponibilité n'est pas une preuve biomécanique. Pas de TTL inventé ; revalider lors du contexte d'usage, conserver les conflits. Si tous candidats sont exclus ou une affectation distincte échoue : CATALOG_GAP. Pas d'extension silencieuse du pool, aucune substitution aléatoire pour supprimer les UNKNOWN. La curation de ces rôles exige les bases anatomiques/études appropriées, pas un remplacement par0.

## D4 — ADMIT_WITH_LIMITS du diagnostic, faisabilité positive non admise

[TIME_MODEL.md](TIME_MODEL.md) sépare prescription, opérations et observation personnelle ;[EVIDENCE.md](EVIDENCE.md) vérifie repos/tempo/échauffement/efficacité/supersets/densité/durée observée. OptionC avec borne partielleB ; rejet du point exactA ; calibrationD future.

Le calcul peut prouver qu'une configuration traditionnelle séquentielle dépasse le budget par ses seuls repos. Il ne démontre jamais qu'elle tient. Même75min ne fournit pas de borne d'installation/familiarisation. Les données expérimentales de durée et économies en supersets ne s'importent pas comme overhead ou facteur universel.

Contrat v1 inchangé : Duration.UNKNOWN ne peut transporter une borne seule ; l'information arithmétique reste diagnostic isolé. POLICY_UNAVAILABLE prévaut aujourd'hui, TIME_UNCERTAIN reste explicite. Aucun nouveau statut mobile ni dégradation du validateur pour autoriser READY.

## Version, preuves et READY

Ancien `initial-hypertrophy-policy/0.1.0-proposed` inchangé, NOT_ADMITTED/NOT_SERVED, SHA8aef079da6a15298bfa2ec1bdec1b417588b6f535224c61afb2f50f98612dfb4. Nouveau `initial-hypertrophy-policy/0.2.0-partially-admitted` : **artefact de décisions non exécutable**, pas remplacement chargé par engine1.0.0. Aucun approved_policy_ref ajouté. Confiance de réponse individuelle NOT_ESTIMATED, même quand la preuve de groupe est modérée.

E0 reste unique ; correspondance IP→EV et bibliographie réellement utilisée dans[EVIDENCE.md](EVIDENCE.md). Les nouvelles sources ne sont pas faussement promues dans un snapshot approuvé. La promotion coordonnée doit préserver les autorités/versionnements historiques.

**READY_NOT_PRODUCED.** Conditions nécessaires : Blueprint suffisant/provenance valide + politique entièrement admise et version moteur liée + candidats/intention/contextes applicables + quinze expositions exactes selon v1 + estimation temporelle conditionnelle soutenue + aucune issue bloquante. Puis seulement une fixture générée par ce producteur et validée par validate_exchange. Produire un READY depuis la seule admission des defaults serait incorrect.

## Handoff MOB04 / PLAN

- **READY TO CONSUME** : rapport D1–D4, décision versionnée, audit40candidats/15zones, diagnostic de budget négatif reproductible ; schémas et onze réponses historiques restent compatibles.
- **NOT READY** : aucune nouvelle prescription, nouveau payload SCI READY ni adaptateur servi. Le mobile conserve NOT_SERVED ; MISSION historique n'est pas un repli scientifique.
- **UNKNOWN** : durée du travail/préparation/opérations, stabilité non curée, réponse individuelle et rôles explicitement inconnus ; compatibilité tant que non confirmée.
- **BLOCKING** : curation/sélection/couverture, modèle positif de temps et protocole de calibration/préparation, puis admission complète/binding producteur. L'architecture doit encore livrer snapshot/consentement pertinent/owner/handoff/reprise.
- **NEXT PRODUCER** : révision isolée explicite d'initial-policy-producer après ces gates, avec vraies références admises et fixtures ; aucun endpoint implicite.

PLAN-03 partiellement avancé ; PLAN04–06 informés, aucun critère de parcours/runtime clos. Change science-initial-plan-policy conservé actif et non archivé. Aucun nouveau GO BUILD produit ou déploiement.

## Vérifications et revue

Baseline72tests. RED observé26échecs/1passant avant implémentation ; GREEN initial27tests. Suite large et revue finale consignées dans[VERIFICATION.md](VERIFICATION.md) après exécution. Les confirmations de pixels et tests appareils ne sont pas concernés et ne sont pas déduits des outils scientifiques.

## NEXT SCIENCE SPIKE

**SCI-P02-CANDIDATE-CURATION-01** : curer les sept intentions et leurs candidats pour ce bootstrap (rôles UNKNOWN, stabilité/contraintes, couverture régionale/omissions, préparation/calibration concrète) avec delta catalogue/E0 versionné et revue indépendante. Ce spike borné est nécessaire avant de calibrer un protocole temporel sur des exercices réellement admissibles ; il ne doit pas promettre seul READY ni ouvrir un moteur adaptatif.
