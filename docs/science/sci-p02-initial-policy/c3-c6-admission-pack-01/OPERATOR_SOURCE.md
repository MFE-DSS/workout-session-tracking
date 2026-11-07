# AUREN — SCI-P02 C3/C6 ADMISSION PACK

**Version : 1.0.0 — 7 novembre 2026**  
**Statut : dossier de décision scientifique préparatoire à l’admission positive du First Plan**  
**Référence contractuelle : FirstPlanRequest / FirstPlanRecommendation 2.0.0**  
**Producteur scientifique existant : `initial-policy-producer/2.0.0`**  
**État à l’entrée : `NOT_ADMITTED / NOT_SERVED / READY_NOT_PRODUCED`**

---

# 0. OBJET DU DOCUMENT

Ce document tranche la doctrine scientifique à appliquer aux deux dernières gates critiques avant admission du premier plan AUREN :

**C3 — comment démarrer réellement un exercice lorsqu’on ne connaît pas encore la charge personnelle pertinente ?**

et :

**C6 — comment affirmer honnêtement qu’une séance est compatible avec le temps disponible lorsqu’on ne connaît pas encore le temps réel de cette personne dans cette salle ?**

Ces deux problèmes possèdent une caractéristique commune :

> **AUREN doit produire une décision utilisable avant de disposer d’un historique individuel complet.**

Le système doit donc être capable de commencer avec :

- une connaissance scientifique de population ;
- un protocole conservateur ;
- beaucoup d’incertitude individuelle ;

puis apprendre progressivement à partir de l’exécution réelle.

---

# 1. DÉCISION DIRECTRICE

Le premier plan AUREN ne doit pas essayer de prédire exactement un utilisateur encore inconnu.

Il doit être :

> **scientifiquement admissible, opérationnellement réalisable, explicitement incertain et conçu pour apprendre.**

La doctrine devient :

**BOOTSTRAP → OBSERVATION → CALIBRATION → PERSONNALISATION**

et non :

**FORMULAIRE → FAUSSE PRÉCISION → PRESCRIPTION DÉFINITIVE**

---

# 2. C1 — POPULATION

## Décision

**ADMIT_WITH_LIMITS**

Population initiale :

- adulte déclaré ;
- contexte non clinique ;
- objectif hypertrophie/bodybuilding ;
- 2 ou 3 séances hebdomadaires ;
- limitations explicitement renseignées ;
- absence d’incompatibilité connue empêchant l’utilisation du programme.

Cette population constitue un **périmètre produit**.

Elle ne signifie pas que :

- 2–3 séances sont physiologiquement supérieures ;
- les autres fréquences sont moins efficaces ;
- l’utilisateur a été déclaré médicalement apte.

L’ACSM 2026 rappelle précisément que de nombreuses configurations de résistance produisent des adaptations et que simplicité, régularité et adéquation au contexte comptent davantage que de nombreuses techniques sophistiquées.

---

# 3. C2 — DOSE INITIALE

## Décision

**ADMIT_AS_CONSERVATIVE_BOOTSTRAP**

Le bundle initial peut conserver :

- 2 work sets par intention ;
- plage 8–12 répétitions ;
- cible comportementale autour de 2 RIR ;
- repos conventionnels actuels ;
- aucune charge initiale prédite.

Ces paramètres ne sont pas présentés comme :

- optimum individuel ;
- dose minimale biologique ;
- programme final ;
- prescription permanente.

Ils constituent :

> **une condition initiale raisonnable permettant à AUREN de commencer à observer la personne.**

La littérature actuelle soutient davantage les grands principes — entraînement progressif, volume suffisant, proximité raisonnable de l’échec — qu’une combinaison exacte universelle de séries, répétitions et RIR.

---

# 4. 2 RIR : SIGNAL COMPORTEMENTAL, PAS MESURE

Le RIR initial reste utile.

Mais sa confiance doit être faible chez un nouvel utilisateur.

Une étude 2026 montre que l’erreur d’estimation du RIR diminue sensiblement après plusieurs expositions ; les participants ont amélioré leur précision au cours de six séances.

Une autre étude 2026 retrouve des adaptations comparables entre une stratégie 1–3 RIR et l’échec sur l’extension de jambes dans sa population et son protocole.

AUREN doit donc enregistrer deux choses séparément :

**RIR déclaré**

et

**confiance dans ce RIR**.

Au début :

`rir_confidence = LOW`

La confiance pourra évoluer avec l’expérience.

---

# 5. C3 — PROTOCOLE INITIAL DE CALIBRATION

## Décision

**ADMIT_WITH_LIMITS**

AUREN doit disposer d’un protocole initial réellement utilisable sans :

- prédire des kg ;
- demander un 1RM ;
- imposer l’échec ;
- utiliser des standards de force ;
- transférer une charge depuis un autre exercice.

---

# 6. POURQUOI LA CHARGE LIBREMENT CHOISIE NE SUFFIT PAS

Une méta-analyse exploratoire sur les charges auto-sélectionnées trouve une moyenne proche de 53 % du 1RM, avec une forte dépendance au contexte et aux instructions.

Cela signifie que :

> **« prends un poids qui te semble bien » n’est pas un protocole scientifique suffisant.**

Mais cela ne justifie pas davantage qu’AUREN invente un poids.

La solution est une **boucle de calibration observée**.

---

# 7. C3 — MACHINE À ÉTATS

Pour chaque nouvelle réalisation d’exercice :

## STATE 1 — NEEDS_CALIBRATION

Aucune charge personnelle comparable et suffisamment récente n’existe.

AUREN connaît :

- exercice ;
- réalisation ;
- contexte ;
- plage de répétitions ;
- cible d’effort ;

mais pas encore la charge.

---

## STATE 2 — FAMILIARISATION

Objectif :

> permettre une première interaction avec le mouvement et le dispositif.

AUREN ne doit pas prétendre que cette étape :

- prévient une blessure ;
- possède une durée universelle ;
- nécessite exactement N séries.

La littérature récente sur l’échauffement montre précisément que son intérêt dépend du contexte, de la tâche et de la population. Le consensus international 2026 décrit l’échauffement comme une intervention contextuelle plutôt qu’un protocole numérique universel.

---

## STATE 3 — CALIBRATION ATTEMPT

L’utilisateur réalise une tentative.

AUREN observe au minimum :

- réglage/charge réellement utilisé ;
- répétitions ;
- arrêt ou completion ;
- RIR déclaré si exploitable ;
- problème ou gêne ;
- contexte exact ;
- côté si unilatéral.

Aucune charge n’est inventée avant cette observation.

---

## STATE 4 — ASSESSMENT

Le système compare l’observation à la prescription.

Trois familles de résultat :

### BELOW TARGET

La réalisation est trop difficile pour le cadre prévu.

### WITHIN TARGET

Elle est utilisable comme point de départ.

### ABOVE TARGET

Elle paraît trop facile pour le cadre prévu.

Ces états sont plus robustes qu’une fausse mesure de « force réelle ».

---

# 8. AJUSTEMENT DE CHARGE

L’ajustement doit utiliser :

> **les incréments réellement disponibles sur ce dispositif**

et non un pourcentage générique.

Exemples :

- stack machine ;
- disque disponible ;
- haltère suivant ;
- assistance ;
- réglage de machine.

Le système peut recommander :

- réduire ;
- conserver ;
- augmenter ;
- recalibrer ;

mais pas :

> « +2,5 kg » lorsque l’appareil ne propose pas +2,5 kg.

---

# 9. ACCEPTATION D’UNE CALIBRATION

`CALIBRATED` signifie :

> **un réglage personnel actuellement utilisable a été observé dans ce contexte.**

Cela ne signifie pas :

- optimum ;
- vrai 2 RIR ;
- 1RM connu ;
- charge transférable ailleurs ;
- réglage permanent.

La calibration doit rester liée à :

- utilisateur ;
- exercice ;
- réalisation ;
- appareil/contexte ;
- côté si pertinent ;
- date ;
- version de politique.

---

# 10. PREMIÈRE CALIBRATION ≠ HISTORIQUE ÉTERNEL

Une calibration peut devenir obsolète après :

- changement d’appareil ;
- longue interruption ;
- changement de réalisation ;
- variation majeure de performance ;
- changement de côté ;
- substitution ;
- incohérence répétée.

Elle doit alors revenir vers :

`NEEDS_RECALIBRATION`

---

# 11. ÉCHAUFFEMENT : DOCTRINE AUREN

AUREN ne doit pas construire un énorme échauffement générique avant chaque séance.

Pour le bodybuilding :

> **la préparation spécifique au mouvement est prioritaire lorsque nécessaire.**

Une revue sur l’entraînement efficace en temps recommande elle aussi de privilégier les warm-ups spécifiques plutôt qu’une accumulation systématique de préparation générale.

Des expériences montrent que la performance peut dépendre de la charge utilisée pendant l’échauffement spécifique, mais les protocoles diffèrent et ne justifient pas une formule universelle.

---

# 12. C3 — POLITIQUE BÊTA

Pour la bêta :

**pas de nombre universel de warm-up sets ;**

**pas de temps universel d’échauffement ;**

**pas de charge d’échauffement universelle.**

Le moteur utilise plutôt :

- `NO_SPECIAL_PREPARATION`
- `FAMILIARISATION`
- `CALIBRATION_REQUIRED`
- `CONTEXT_DEPENDENT`
- `RECALIBRATION_REQUIRED`

Les détails seront appris progressivement par exercice et utilisateur.

---

# 13. C4 — BUNDLE DE SÉLECTION

## Décision

**ADMIT_WITH_LIMITS**

L’admission doit porter uniquement sur :

> **les réalisations réellement utilisées par le premier plan.**

Il n’est pas nécessaire d’admettre scientifiquement l’intégralité du catalogue avant la bêta.

Pour chaque slot sélectionné :

- intention admise ;
- candidat admis ou conditionnel ;
- contexte compatible ;
- aucune exclusion ;
- calibration possible ;
- UNKNOWN non bloquant explicitement conservé.

Les quatre candidats pull encore incertains n’ont pas besoin d’être résolus s’ils ne sont pas utilisés par le bundle initial.

---

# 14. C5 — REPRÉSENTATION 15 ZONES

## Décision

**ADMIT_QUALITATIVE_REPRESENTATION**

Les 15 zones peuvent être utilisées pour :

- identité ;
- exposition qualitative ;
- coverage ;
- direct/indirect/minor/unknown ;
- explicabilité.

Elles ne doivent pas être présentées comme :

- volume hypertrophique exact ;
- activation quantitative ;
- croissance prévue ;
- score biologique.

Ainsi :

`DIRECT`

ne signifie pas :

`100 % stimulus`

et :

`UNKNOWN`

ne signifie pas :

`0`.

---

# 15. LE PROBLÈME C6

Pour un nouvel utilisateur, AUREN connaît :

- sets ;
- reps ;
- repos prescrits ;
- exercices ;
- budget déclaré.

Mais il ne connaît pas encore correctement :

- vitesse réelle ;
- temps d’installation ;
- familiarisation ;
- changement d’appareil ;
- attente ;
- environnement ;
- comportement utilisateur.

Donc :

> **une durée exacte lors de la première séance n’est pas scientifiquement identifiable.**

---

# 16. C6 — LES TROIS ROUTES

Le contrat actuel propose :

## ROUTE A — MODÈLE VALIDÉ

Construire un véritable modèle temporel à partir de données réelles et le valider indépendamment.

## ROUTE B — CONVENTION PRODUIT BORNÉE

Définir explicitement une convention pratique, avec hypothèses et limites.

## ROUTE C — INCONNU / BLOQUÉ

Ne produire aucune compatibilité positive tant qu’une base suffisante manque.

---

# 17. DÉCISION C6 POUR LA BÊTA

## Recommandation

**ROUTE B POUR LE BOOTSTRAP, ROUTE A COMME CIBLE LONGITUDINALE.**

Mais la Route B ne doit jamais être présentée comme un modèle physiologique.

Elle sert seulement à permettre au produit de commencer.

---

# 18. CE QUE ROUTE B DOIT DIRE

La sortie ne doit pas être :

> `durée estimée : 47 minutes`

mais plutôt :

- `BUDGET_COMPATIBLE_BY_POLICY`
- `BUDGET_TIGHT`
- `BUDGET_UNCERTAIN`
- `STRUCTURALLY_TOO_LONG`

ou vocabulaire contractuel équivalent.

Il s’agit d’une **classification de planification**.

Pas d’une prédiction chronométrique.

---

# 19. CE QUE ROUTE B PEUT UTILISER

Le système connaît objectivement :

- nombre de séries ;
- repos prescrits ;
- structure séquentielle ;
- nombre d’exercices ;
- éventuelle unilatéralité ;
- préparation/calibration requise.

Ces données définissent une partie du coût de séance.

---

# 20. CE QUE ROUTE B NE DOIT PAS INVENTER

Pas de :

- 30 secondes par transition ;
- 2 minutes par machine ;
- 10 secondes par répétition ;
- temps d’attente moyen ;
- coefficient arbitraire de salle.

Si une constante opérationnelle est adoptée comme convention produit, elle doit explicitement être :

> **une hypothèse de design validée par le PO, pas un fait scientifique.**

---

# 21. POURQUOI LES SUPERSETS NE RÉSOLVENT PAS AUTOMATIQUEMENT C6

Les supersets peuvent réduire fortement la durée.

Une méta-analyse 2025 retrouve des séances plus courtes avec des adaptations chroniques globalement comparables dans les études disponibles.

Une revue systématique très récente montre cependant que l’effet dépend énormément du type de paired-set : certaines configurations réduisent la durée d’environ 40–50 %, mais peuvent aussi réduire répétitions ou volume.

Donc :

> **AUREN ne doit pas compresser automatiquement une séance en supersets pour la faire rentrer dans le temps.**

Un superset est une structure de programme.

Pas une astuce comptable.

---

# 22. TIME EFFICIENCY : VARIABLE DU PROGRAMME

À terme, AUREN pourra proposer :

### Traditional

Priorité à la qualité/performance locale.

### Paired / antagonist

Réduction du temps lorsque compatible.

### Compact

Structure volontairement optimisée pour contrainte de temps.

Mais ces architectures doivent être scientifiquement gouvernées.

Pas activées silencieusement.

---

# 23. PREMIÈRE SÉANCE ET TEMPS

Le problème logique suivant doit être évité :

> pas de première séance parce que nous ne connaissons pas la durée personnelle ;

alors que :

> nous ne pouvons apprendre la durée personnelle qu’après une première séance.

Le système doit pouvoir **explorer sans mentir**.

---

# 24. RECOMMANDATION CONTRACTUELLE

Si le contrat v2 actuel impose une Duration positivement supportée pour tout READY, je recommande de séparer dans une version ultérieure :

## Scientific readiness

Le plan est scientifiquement cohérent et exécutable.

## Time confidence

La durée est :

- supported ;
- policy-bounded ;
- uncertain.

Cela évite de faire du temps une condition impossible à satisfaire avant la première observation.

---

# 25. PAS D’ASSOUPLISSEMENT SILENCIEUX

Cette séparation exige un contrat versionné.

Il est interdit de transformer :

`Duration.UNKNOWN`

en :

`SUPPORTED`

simplement pour faire passer READY.

Si cette évolution est retenue, elle doit devenir :

> **une décision explicite de FirstPlan contract v2.x/v3**, avec consommateurs et migration documentés.

---

# 26. BOUCLE TEMPORELLE LONGITUDINALE

Après les premières séances, AUREN observe :

- début session ;
- fin session ;
- début/fin exercice ;
- début/fin set lorsque disponible ;
- repos ;
- préparation ;
- transitions ;
- interruptions.

Progressivement :

> convention population → historique personnel.

---

# 27. ROUTE A — MODÈLE PERSONNEL FUTUR

Lorsque suffisamment de données existent, AUREN pourra estimer :

`P(duration <= budget | planned session, user, context)`

ou une représentation équivalente.

Il n’est pas nécessaire d’utiliser un modèle complexe.

Une estimation empirique bien calibrée peut être préférable à une IA opaque.

---

# 28. PAS DE POINT ESTIMATE EN PREMIER

Une sortie future devrait préférer :

> **intervalle ou probabilité calibrée**

à :

> **47 minutes**.

Exemple :

> « habituellement 42–51 min dans cette configuration »

est scientifiquement plus honnête que :

> « 46 min ».

---

# 29. VALIDATION DU FUTUR MODÈLE TEMPOREL

Avant promotion de Route A :

- données réelles séparées train/validation ;
- protocole préspécifié ;
- performance hors échantillon ;
- erreur ;
- calibration ;
- couverture des intervalles ;
- segmentation ;
- dérive ;
- version.

Aucune validation sur les données ayant servi à créer directement les règles.

---

# 30. DONNÉES À COLLECTER POUR C6

Pour chaque séance réelle :

- session ID ;
- plan version ;
- session structure ;
- exercise IDs ;
- prescriptions ;
- temps effectifs ;
- phases de calibration ;
- transitions ;
- attente si volontairement déclarée/détectable ;
- contexte ;
- substitutions ;
- séance incomplète ;
- interruptions.

Les données doivent distinguer :

> **temps du programme**

de :

> **temps perdu ou interrompu.**

---

# 31. LE BUDGET UTILISATEUR

Le budget déclaré :

> « j’ai 45 minutes »

est une **contrainte**.

Pas une mesure.

Le moteur doit adapter :

- nombre d’intentions ;
- sets ;
- structure ;

mais ne doit pas affaiblir automatiquement :

- effort ;
- repos nécessaire ;
- qualité ;

juste pour respecter artificiellement le chiffre.

---

# 32. SI LE PLAN NE RENTRE PAS

Ordre de décision recommandé :

1. réduire la quantité de travail de cette séance dans une politique admise ;
2. redistribuer une partie du travail vers une autre séance ;
3. utiliser une structure plus efficace si scientifiquement compatible ;
4. signaler la contrainte.

Ne pas :

> raccourcir tous les repos arbitrairement.

---

# 33. C6 — ÉTAT D’ADMISSION

La science peut aujourd’hui admettre :

> **la doctrine de faisabilité**, pas encore un modèle universel de durée.

Le statut approprié devient :

`ADMITTED_PRODUCT_BOUNDED_BOOTSTRAP`

pour Route B,

à condition que :

- la convention soit explicitement approuvée par le PO ;
- ses hypothèses soient visibles ;
- elle ne prétende pas être prédictive ;
- elle soit destinée à être remplacée par les données individuelles.

---

# 34. CE QUI RESTE À FAIRE POUR ROUTE B

Le PO/architecte doit définir les seules conventions nécessaires au produit.

Notamment :

- quelle marge de prudence, s’il en existe une ;
- quel statut autorise le démarrage ;
- comment représenter `TIME_UNCERTAIN` ;
- comment agir si l’utilisateur approche de sa limite en séance.

Ces valeurs ne doivent pas être inventées par l’agent scientifique.

---

# 35. C3 + C6 : LE CERCLE D’APPRENTISSAGE

Première séance :

**beaucoup d’incertitude**

↓  

AUREN observe :

**charge + reps + RIR + temps + contexte**

↓  

Deuxième séance :

**meilleure calibration**

↓  

Plusieurs séances :

**historique comparable**

↓  

AUREN remplace progressivement :

**defaults population**

par :

**modèle personnel**.

---

# 36. DÉCISION C1–C6 CONSOLIDÉE

| Gate | Décision recommandée |
|---|---|
| C1 Population | `ADMITTED_WITH_LIMITS` |
| C2 Dose | `ADMITTED_AS_CONSERVATIVE_BOOTSTRAP` |
| C3 Protocole initial | `ADMITTED_WITH_LIMITS` |
| C4 Candidats/réalisation | `ADMITTED_FOR_BOUND_BUNDLE` |
| C5 Représentation | `ADMITTED_QUALITATIVE` |
| C6 Temps | `ROUTE_B_RECOMMENDED / ROUTE_A_TARGET` |

---

# 37. CE QUE CETTE ADMISSION NE SIGNIFIE PAS

Elle ne signifie pas :

- politique servie ;
- moteur runtime ;
- API ;
- mobile READY ;
- première séance créée ;
- admission médicale ;
- programme optimal ;
- durée exacte ;
- charge optimale.

Elle signifie :

> **la doctrine nécessaire pour construire le prochain producteur positif est suffisamment définie, sous réserve des décisions produit explicites C6 Route B.**

---

# 38. BINDING SCIENTIFIQUE FUTUR

Lorsque le paquet est formellement admis :

le futur registre doit lier exactement :

- version de contrat ;
- version Blueprint ;
- policy version ;
- curation version ;
- calibration protocol version ;
- time-policy version ;
- evidence digest ;
- producteur version.

Aucun `approved=true` isolé.

---

# 39. READY

Un vrai READY ne doit être généré que si :

- Blueprint suffisant ;
- population admise ;
- policy admise ;
- chaque slot possède une réalisation admissible ;
- contexte confirmé lorsque nécessaire ;
- prescription disponible ;
- calibration possible ;
- aucune limitation bloquante ;
- représentation cohérente ;
- politique temporelle applicable ;
- fingerprints valides.

---

# 40. READY N’EST PAS « PERSONNALISÉ À LA PERFECTION »

Au premier jour, READY signifie :

> **suffisamment personnalisé et suffisamment justifié pour commencer à apprendre.**

Pas :

> **programme biologiquement optimal de cette personne.**

Cette distinction est fondamentale.

---

# 41. ÉVOLUTION DE LA CONFIANCE

La confiance doit progresser avec les observations.

### Première exposition

LOW.

### Plusieurs expositions cohérentes

MODERATE.

### Historique personnel stable

Potentiellement HIGH pour certaines décisions locales.

La confiance d’une prescription locale ne devient jamais la confiance de toute la science du programme.

---

# 42. CRITÈRES D’ACCEPTATION DU PAQUET C3/C6

Le paquet est acceptable si :

- aucune charge initiale universelle n’est inventée ;
- aucune obligation d’échec n’existe ;
- RIR est reconnu comme signal entraînable et imparfait ;
- calibration est locale au contexte ;
- warm-up reste contextuel ;
- C6 distingue prédiction et convention ;
- aucune durée précise n’est inventée ;
- l’historique réel est prévu comme future source dominante ;
- les supersets ne sont pas utilisés comme compression implicite ;
- le contrat READY n’est pas silencieusement affaibli ;
- toute évolution du contrat est versionnée ;
- l’incertitude reste explicitement représentable.

---

# 43. DÉCISION RECOMMANDÉE AU PO

Je recommande d’approuver :

### C3

La machine à états de calibration adaptative décrite dans ce document.

### C6

La stratégie :

> **Route B pour la première bêta, explicitement comme convention produit bornée ; Route A construite ensuite à partir des données réelles.**

Et de ne pas approuver :

> un modèle de durée exact pour un utilisateur neuf.

---

# 44. PROCHAINE ÉTAPE APRÈS APPROBATION

Une fois ce paquet accepté :

1. produire l’artefact scientifique final/versionné ;
2. lier le bundle exact ;
3. construire le producteur positif isolé ;
4. générer une vraie fixture READY ;
5. la faire passer au validateur v2 ;
6. seulement ensuite ouvrir le binding runtime PLAN.

Aucune UI n’est nécessaire pour cette admission.

---

# 45. DOCTRINE FINALE

Le premier entraînement AUREN doit être conçu comme :

> **la première expérience d’un système qui apprend**, pas comme le résultat d’un oracle.

Au premier jour, AUREN connaît davantage la science générale que la personne.

À chaque séance, ce rapport doit s’inverser progressivement.

Le state of the art n’est donc pas de prétendre connaître dès le départ :

- la charge parfaite ;
- la durée parfaite ;
- le RIR réel ;
- la réponse hypertrophique exacte.

Le state of the art est de construire un protocole dans lequel :

> **chaque inconnue importante peut être observée, chaque observation correctement conservée, et chaque nouvelle décision devenir plus personnelle que la précédente.**