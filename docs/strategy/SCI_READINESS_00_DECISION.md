# SCI-READINESS-00 — disponibilité musculaire : audit de décision

25 novembre 2026, Europe/Paris. Base vérifiée : `224ea54f25f4ff40ee7e35a4a53efc852fb5dcd6`.
**AUDIT / SPEC ONLY — aucun nouveau modèle, score, runtime ou permission SCI.**

## Décision proposée

Conserver le BodyMap comme localisation anatomique, puis construire une mémoire de **travail exécuté documenté**, avant toute nouvelle estimation de récupération. Ne pas réactiver les anciennes barres web comme mesure d’énergie. La récupération estimée existe déjà dans le code historique et influence V3 ; son existence ne prouve pas sa validation physiologique. Le nouveau consommateur mobile de disponibilité reste NOT_SERVED.

La référence radiographique/3D plaît à l’opérateur pour sa matière et sa présence. Elle reste une référence artistique : ni nouveau mannequin admis, ni activation mesurée, ni remplacement des assets LOCKED. La demande jointe interdit explicitement la génération anatomique dans cette tranche.

## Brainstorming / Options / Risques / Choix retenu

Trois voies : remettre les anciennes jauges immédiatement ; inventer un nouveau score ; auditer les producteurs puis séparer mémoire factuelle, modèle et allocation. La troisième est retenue. Risques principaux : vocabulaire physiologique sur un ratio temporel, séries prévues traitées comme accomplies, mélange de deux taxonomies, absence assimilée à récupération et historique mal horodaté. Le présent audit n’applique aucune de ces transformations.

## 1. Ce que fait réellement le code canonique

| Voie | Formule / données | Absence et limites | Usage réel |
|---|---|---|---|
| Disponibilité ancienne | `clamp(hours_since_last / T_zone,0,1)` ; 14 jours ; dernière séance strength avec au moins une série `work && completed`, zone principale ; temps depuis **started_at de séance** | Pas de passage : 8760 h et 1,0 ; lecture partielle : 0,5. Ces valeurs de repli ne mesurent rien. | Ancien score décisionnel ; ne pas confondre avec le producteur web canonique actuel. |
| `zone_recovery`, policy v1 | Même ratio temporel, lookback 30 jours via `training_state` ; principales et secondaires | Absence : valeur NULL, UNKNOWN/NONE. Mapping formel : confiance au plus MEDIUM ; repli : LOW. Cardio peut abaisser la confiance. | Estimation web et bandes consommées par la politique V3 actuellement servie. |
| Couverture 14 jours | Séries de travail complétées ; propriétaire ; séance terminée, non exclue ; `[now−14j,now)` sur started_at ; crédit secondaire `round(n×0,3)` | Crédit conventionnel, pas fraction physiologique observée. Aucun contrôle TIME-01 de qualité temporelle dans cette agrégation. | Critère de couverture V3, distinct de récupération. |
| Ledger SCI d’exposition | Séries réalisées, identité réellement exécutée, rôles bruts et provenance ; fenêtre propriétaire bornée ; UNKNOWN / EXACT / MINIMUM | PRIMARY=1 ; SECONDARY=0,5 ; MINOR=0 ; UNKNOWN reste UNKNOWN. Politique versionnée distincte de 0,3 legacy. | **Non servi** à MISSION ; permission limitée V3 initiale ≠ autorisation générale. |

Cibles historiques : pecs/lats/upper_back 48 h ; delt_lat/delt_post/biceps/triceps/calves 36 h ; quads/posterior 72 h ; core 24 h. Bandes historiques : ≥0,8 disponible ; ≥0,4 partielle ; sinon fatiguée. **Ce sont des paramètres de logiciel, pas des délais universels admis par cet audit.**

Sources : [recommendation.py](../../app/services/recommendation.py) lignes69–84,405–534 ; [training_state.py](../../app/services/training_state.py) lignes314–365,520–544 ; [zone_recovery.py](../../app/services/zone_recovery.py) lignes63–218,329–358 ; [recovery_contract.py](../../app/services/recovery_contract.py) lignes245–282,868–886 ; [muscle_scoring.py](../../app/services/muscle_scoring.py) lignes93–170 ; [sci_exposure.py](../../app/services/sci_exposure.py) lignes62–185 ; [politique SCI](../../data/sci/exposure_credit_policy.json).

L’allocation servie est `v3` avec mémoire active ([advice_memory.py](../../app/services/advice_memory.py),77–78), malgré un préambule historique périmé de recommendation_v3. Son classement est lexicographique ; UNKNOWN n’est pas une preuve positive de récupération. Aucun nouveau rang ou poids n’est proposé ici.

## 2. Écarts prouvés à traiter avant promotion

| Priorité | Constat vérifié à la source | Conséquence / réparation à cadrer séparément |
|---|---|---|
| P0 | Médiane de couverture nulle → déficit0,0, puis facteur « déjà bien servi ». | Un compte sans base de comparaison reçoit une explication positive de couverture. La source reste propriétaire ; **aucune fuite de compte démontrée**. Corriger l’explication sans modifier le classement exige un delta séparé, hors MISSION présentatif. |
| P0 | `training_state._zone_evidence` retient tout exercice mappé d’une séance terminée, sans vérifier ses séries accomplies. | L’estimation peut prendre un exercice seulement planifié comme sollicitation. Ne pas promouvoir cette projection comme volume exécuté. |
| P1 | Cette voie a une borne basse, pas de borne haute. `_hours_between` rejette ensuite le futur. | Une séance future peut remplacer la dernière preuve passée et conduire à UNKNOWN ; cela ne prouve pas une fatigue faussement fraîche. |
| P1 | `mesurée` signifie seulement `observation_partielle=False`. | Ne garantit ni historique non vide, ni série accomplie, ni récupération mesurée. Renommer dans la présentation ; garder la trace source. |
| P1 | KPI groupé par slug **et nom snapshot**, puis dict indexé par slug. | Plusieurs noms d’un même modèle peuvent écraser une récence ; cas de non-régression à créer avant correction. Aucun historique à réécrire. |

Preuves des explications : [recommendation_v3.py](../../app/services/recommendation_v3.py),140–165,379–400,632–747 ; [kpis.py](../../app/services/kpis.py),345–405. « Jamais fait » est l’absence de passage **terminé et retenu pour le modèle de séance**, sur l’historique disponible, non l’absence de travail de ses muscles ni la preuve d’une prescription exacte jamais exécutée. Le KPI exclut notamment les séances `science:v3:first-session` et n’exige pas une série de travail terminée.

Le cas synthétique MISSION observé le24novembre et audité le25novembre reçoit Push A7exercices/21séries et une explication « bien servi » alors que le compte n’a aucune séance ; lecture du code ci-dessus explique le défaut. Cette observation locale ne certifie pas tous les comptes ni l’état du site distant. Les preuves privées d’identité restent hors dépôt.

## 3. Inventaire des entrées et qualification temporelle

| Entrée | Producteur / autorité | Admission pour une future mémoire |
|---|---|---|
| Programme, séance, prescriptions, ordre | Domaine canonique et snapshots | Structure prévue seulement ; jamais comptée comme exécutée. |
| Série exécutée | `SetLog.kind/completed`, reps, charge, qualité, technique | Distinguer work/préparation ; valeurs optionnelles ; contexte exact d’équipement. |
| Épisode historique | `SetLog.completed_at` nullable | NULL reste heure inconnue ; ne pas remplacer par started_at ou date de lecture. |
| Legacy mobile | `SetCompletionBody`, validation et ACK | `performed_at_estimated` accepté mais pas conservé comme champ SetLog ; `adjusted` dans le reçu. Qualité temporelle non récupérable depuis la seule ligne. |
| V3 | Observation JSON, setting/context, révision et reçus immuables | Poids seulement MASS_KG/TOTAL_EXTERNAL ; machine/PER_IMPLEMENT ne deviennent pas masse totale. |
| Temps TIME-01 | performed_at d’événement, recorded_at local, server_now/snapshot.as_of et reçu | Autorités distinctes ; drapeaux estimé, décalage et réconciliation à conserver ; horloge monotone ≠ temps d’événement. |
| Identité exécutée | Substitution sinon snapshot du nom | E1…E7 sont des positions réutilisées, pas identités universelles d’exercice. |
| Ressenti / effort | ReadinessEntry1–5 et feedback de séance ; effort local seulement si réellement présent | Déclaratif subjectif ; ne pas fabriquer RIR, effort local ou mesure de récupération à partir d’un ressenti global. |
| Correction, annulation, effacement | Lignées/révisions et exclusions canoniques du domaine concerné | Relire les versions effectives, éviter le double comptage, retrait/effacement ne deviennent pas zéro physiologique. BODY ne corrige pas les faits SET. |

Sources : [models/session.py](../../app/models/session.py),244–288 ; [mobile_api.py](../../app/routers/mobile_api.py),391–460 ; [journal V3](../../app/services/plan_v3/journal.py),64–143 ; [provenance TIME-01](../pilot/time01/PROVENANCE.md). Le nouveau contrat doit décider explicitement la fenêtre sur l’événement ou sur la séance, les inclusions aux frontières et le traitement des temps anciens/estimés/incohérents ; les anciennes heures ne sont jamais réécrites.

## 4. Compatibilité anatomique : localisation ≠ comptabilité

| Zone BodyMap | Preset / vue | Correspondance SCI à faire admettre |
|---|---|---|
| pecs | push-pecs / front | pecs : candidat direct |
| delt_lat | push-delt-lat / front | lateral_delts : renommage explicite |
| delt_post | zone-delt-post / back | rear_delts : renommage explicite |
| lats | zone-lats / back | lats : candidat direct |
| upper_back | zone-upper-back / back | upper_back : candidat direct |
| biceps | zone-biceps / front | biceps : candidat direct |
| triceps | push-triceps / back | triceps : candidat direct |
| quads | zone-quads / front | quads : candidat direct |
| posterior | zone-posterior / back | hamstrings + glutes : agrégation avec perte de détail, pas somme implicite |
| calves | zone-calves / back | calves : candidat direct |
| core | zone-core / front | abs = paroi antérolatérale, pas seulement grand droit ; correspondance explicite |

`unknown` est un état, pas une douzième zone. `anterior_delts`, `adductors`, `hip_flexors` n’ont pas d’équivalent11zones à inventer. Les quinze zones SCI ont quatre rôles et une politique de crédit propre. **Aucune correspondance ci-dessus n’est admise par le présent tableau** : SCI-P07 doit versionner le mapping15→11, ses pertes, sa non-additivité et les UNKNOWN.

Sources : [presets](../../clients/mobile/src/ui/bodymap/viewPresets.ts),19–78 ; [géométrie](../../clients/mobile/src/ui/bodymap/bodyGeometry.ts) ; [11zones](../../app/services/muscle_mapping.py),24–36 ; [schéma15zones](../../data/sci/exercise_catalogue.schema.json),770–789 ; [dépendances SCI](AUREN_PRODUCT_SCIENCE_DEPENDENCIES.md).

**Push A / delt_post : justifié.** E6 « Écarté arrière d’épaule câble »,3×12–15, est dans [reference_split.json](../../data/reference_split.json),144–164 ; son entrée [EKB](../../data/exercise_knowledge_base.json),1830–1836, porte delt_post ; le matcher [muscle_mapping.py](../../app/services/muscle_mapping.py),117–118, le reconnaît. [session_zones](../../app/services/mobile_read_models.py),85–98,142–144, dérive les principales depuis les exercices réels et déduplique. L’autorité suit correction relue → mapping DB → repli substring ([body_zone_source.py](../../app/services/body_zone_source.py),162–202). Le chemin DB exact de la fixture n’a pas été interrogé ; le DTO reçu et les sources canoniques concordent. Aucun remplissage arbitraire de quatre fenêtres.

## 5. Littérature primaire vérifiée et limites

Ces études humaines définissent des facteurs et des limites ; **aucune ne valide un score personnel0–100 issu du journal AUREN**. Les protocoles ne fournissent pas les constantes de24–72h par zone du logiciel.

| Étude / DOI | Population et mesure | Résultat utile ; limite de transfert |
|---|---|---|
| [Morán-Navarro et al.,2017](https://pubmed.ncbi.nlm.nih.gov/28965198/),10.1007/s00421-017-3725-7 | 10hommes entraînés ; squat/couché ;3×5,6×5 ou3×10 sur10possibles ; vitesse/saut/marqueurs jusqu’à72h | L’échec entraîne une récupération plus lente même à répétitions totales égalisées avec6×5. Ne calibre pas une décroissance individuelle ni des poids musculaires. |
| [Refalo et al.,2023](https://pubmed.ncbi.nlm.nih.gov/36752989/),10.1186/s40798-023-00554-y | 12hommes/12femmes entraînés ;6séries couché75%1RM, échec/1RIR/3RIR ; vitesse et ressentis | Proximité de l’échec associée à plus de baisse aiguë ; différences plus faibles à24h et s’atténuant à48h. Volume différent entre conditions ; pas de48h universelles. |
| [Ferreira et al.,2017](https://pubmed.ncbi.nlm.nih.gov/28595855/),10.1016/j.physbeh.2017.06.001 | 26hommes entraînés ;8séries couché à l’échec ; couple, travail répété, courbatures jusqu’à96h | Couple et travail total ne récupèrent pas au même rythme. « Récupéré » dépend de ce qu’on mesure ; ne prouve pas une interdiction de s’entraîner avant96h. |
| [Chen,2006](https://pubmed.ncbi.nlm.nih.gov/17020080/),10.1080/02701367.2006.10599370 | 24étudiants ; contractions excentriques des fléchisseurs du coude,30contractions ; force/douleur/CK | Différences individuelles de réponse, classification fondée sur CK ; exercice particulier, pas de correspondance CK→readiness applicative. |
| [Chen et al.,2019](https://pubmed.ncbi.nlm.nih.gov/30663816/),10.1111/sms.13388 | 15hommes sédentaires ;9exercices excentriques5×10, seconde exposition2semaines après | Région et exposition antérieure modifient les réponses ; protocole inhabituel/dommageable, aucune constante universelle par région chez les entraînés. |
| [Miranda et al.,2018](https://pubmed.ncbi.nlm.nih.gov/28195973/),10.1519/JSC.0000000000001840 | 16hommes entraînés ;3variantes de couché,4séries maximales chacune ;24/48/72h entre séances | Répétitions réduites avec24h dans ce contexte. Une capacité à cette tâche n’est pas toute la récupération, ni une preuve de prévention de blessure. |

Contrôles d’identité complémentaires : [Pareja-Blanco2017](https://pubmed.ncbi.nlm.nih.gov/26970332/),10.1111/cpf.12348 (online2016, volume non égalisé), et [2020](https://pubmed.ncbi.nlm.nih.gov/30036284/),10.1519/JSC.0000000000002756. Les mentions génériques de « revues2024/2025 » de la note opérateur restent non identifiées : elles ne servent pas de preuve dans cette décision.

**Inférence méthodologique proposée**, distincte des résultats des études : choisir une tâche/endpoint, mesurer sa répétabilité, recueillir prospectivement ses vrais prédicteurs, comparer au temps seul et à une base personnelle simple, valider hors échantillon calibration/erreur individuelle/utilité. Ne pas baptiser un ratio de temps « énergie ».

## 6. Découpage exécutable, admissions et tests

| Tranche proposée | Résultat | Gates propres |
|---|---|---|
| Correctif explication historique | Absence de comparaison reste absente ; texte uniquement, classement intact | Nouveau delta borné d’explication/tests, scope autorisé avant apply ; pas dissimulé dans MISSION UI. |
| Correctif de récence slug/nom | Préserver la dernière occurrence applicable lors des changements de nom ; effet possible sur départage/gagnant | Scope et tests d’allocation séparés, aucun résultat identique présumé. |
| SCI-READINESS-01 | Projection descriptive de travail accompli, propriétaire/fenêtre exacte, dates et unités qualifiées, couverture/missingness | Contrat producteur/consommateur, SCI-P07, admission des sources et ledger ; aucun score/prior temporel nouveau. |
| DA-READINESS-01 | Un instrument BodyMap adjacent aux faits, réutilisable | G1 puis vrais pixels ; aucune géométrie appliquée ici, pas de nouveau mannequin. |
| SCI-READINESS-02 | Hypothèse de récupération estimée, endpoint et validation prospectifs | SCI-P09/politique versionnée, incertitude, validation ; pas de pourcentage mesuré ni délai universel. |
| MISSION IntelligenceV2 | Usage éventuel d’un signal qualifié pour comparer les séances | Admission et amendement séparés de la politique d’allocation, traçabilité de l’effet ; jamais prescription silencieuse. |

Tests existants inventoriés, **non rejoués par cet audit documentaire** : `test_zone_recovery`, `test_training_state`, `test_sci_exposure`, `test_recovery_contract`. Nouveaux témoins à prévoir : vide+mesurée ; séance terminée sans série ; sériework/nonwork/noncomplétée ; deux comptes ; futur/NULL/estimated/adjusted ; frontière de fenêtre ; séancecommencéeavant et sérieaprès ; nom modifié pour même slug ; substitution ; correction/version/exclusion ; réglage machine ; rôles multiples et UNKNOWN ; mapping15→11 sans doublecompte. Les seules observations de runtime réutilisées sont les lectures synthétiques explicitement étiquetées de MISSION.

## 7. Contrats exacts concernés, non modifiés ici

- [Sx_RECOVERY_READINESS_01_SPEC](Sx_RECOVERY_READINESS_01_SPEC.md) §2.3/§3/§8 et OQ2/5/7 : sémantique et suffisance, futur modèle de récupération.
- [Sx_AUREN_SCIENTIFIC_ENGINE_V2_SPEC](Sx_AUREN_SCIENTIFIC_ENGINE_V2_SPEC.md),24–42,60–76 : heures anciennes = priors, pas validation personnelle ; volume/effort/nouveauté à qualifier.
- [Intégration catalogue SCI](Sx_SCI_V2_CATALOGUE_INTEGRATION_01_SPEC.md) §3/§7.1/§9/§16 : promotion du ledger et changement d’horloge de fenêtre ; gardes de non-consommation actuelles.
- SCI-P07/P09 dans [AUREN_PRODUCT_SCIENCE_DEPENDENCIES](AUREN_PRODUCT_SCIENCE_DEPENDENCIES.md) : mapping anatomique et récupération, pas réglés par l’art.
- [Visual Contract](AUREN_VISUAL_CONTRACT.md) §20–22 : BODYMAP-ZONES-V1/BODYMAP-MIT-BODY-V1, localisation sans activation/intensité ni récupération anatomique ; aucune modification nécessaire pour garder ce sens et présenter des faits adjacents. Changer ce sens demanderait amendement explicite.
- SEMANTIC-TOKENS-V1 / Calibration System : EASY/TARGET/PUSH/HIGH COST ne deviennent pas une échelle de récupération. Aucune nouvelle palette.
- Politique V3/recommendation_explainer : amendment séparé si changement de décision ou de raisons, jamais embarqué silencieusement dans un rendu.

## 8. Proposition unique du premier instrument Push A — spécification, pas pixels

Un groupe sélectionné parmi les **zones réellement reçues** (pecs, delt_lat, delt_post, triceps pour ce snapshot), BodyMap existant et un registre adjacent : fenêtre datée, nombre de séries de travail **connues** attribuées selon policy identifiée, dernier événement qualifié, sources/UNKNOWN. Aucun chiffre d’exécution n’est inventé depuis les7exercices/21séries prescrits. Faute de projection admise, le prototype futur montrera « Historique non qualifié » et récupération désactivée ; il ne remplira pas une barre.

Sélection du groupe et disclosure de sources dans le même objet, sans nouveau POST ; aucune proposition graphique supplémentaire ici. Le prochain scope doit fixer ces sources et faire accepter la géométrie avant intégration. Un historique incomplet n’autorise ni0série comme total réel ni100%récupéré.

## Verdict et frontière de livraison

Audit00 réalisé, preuves code et littérature identifiées, hypothèses et écarts explicites. **Aucune activation READINESS-01/02 autorisée par cet audit.** MISSION garde son propre gate pixels et son moteur intact. QA/PILOT/DATA, APK/OTA et acceptation physique restent indépendants ; aucun état externe n’est revérifié par ce document. Les anciens contrats ne sont ni remplacés ni réécrits.

Revue indépendante documentaire : deux Important (pointeur de seuils, portée du correctif de récence) et deux Minor corrigés. Source-only ; aucune revue indépendante de modèle implémenté ni exécution de campagne produit revendiquée.

Relecture indépendante de la littérature : identités, DOI, effectifs, résultats et limites concordants ; une précision mineure de protocole corrigée. Aucun modèle AUREN validé par cette relecture.
