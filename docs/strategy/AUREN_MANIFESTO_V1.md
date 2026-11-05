# AUREN — MANIFESTE PRODUIT & SCIENTIFIQUE CANONIQUE

**Version 1.0 — 5 novembre 2026**  
**Statut : document directeur / North Star / contrat anti-drift**  
**Produit : AUREN**  
**Nom historique : SPIGNOS — ne constitue plus la marque produit**

---

# 0. RÔLE DE CE DOCUMENT

Ce document définit ce qu’AUREN doit devenir.

Il se situe au-dessus :

- des tickets ;
- des sprints ;
- des specs de surface ;
- des choix d’implémentation ;
- des agents de développement ;
- de l’agent scientifique ;
- des opportunités fonctionnelles découvertes en cours de développement.

Lorsqu’une implémentation, une proposition UX, une règle scientifique ou une nouvelle fonctionnalité entre en conflit avec ce manifeste, **le manifeste prévaut**, sauf décision explicite de le modifier.

AUREN possède déjà des briques avancées de logging, historique, progression, feedback, Body Intelligence, substitution et adaptation. Ces briques ne doivent plus évoluer indépendamment. Le système existant avait déjà identifié que signal, UX d’exercice, adaptation, historique et analytics appartiennent à une seule architecture.

Ce document définit cette architecture dans son ensemble.

---

# 1. NORTH STAR

> **AUREN est le cockpit personnel de bodybuilding qui comprend le corps de l’utilisateur, construit son entraînement, guide son exécution, observe sa progression et ajuste continuellement la prochaine décision.**

AUREN ne doit pas simplement permettre de « suivre ses séances ».

Il doit supprimer progressivement cinq décisions que l’utilisateur prend aujourd’hui seul :

**Que dois-je entraîner ?  
Quels exercices dois-je faire ?  
Combien dois-je faire ?  
Que dois-je tenter aujourd’hui ?  
Que dois-je changer ensuite ?**

L’utilisateur reste maître de l’exécution et peut modifier le plan.

Mais il ne doit jamais avoir besoin d’être son propre programmeur sportif pour utiliser correctement AUREN.

---

# 2. AUREN EST UN PRODUIT DE BODYBUILDING

AUREN n’est pas une application généraliste de fitness.

Son domaine canonique est :

> **l’amélioration du physique par l’hypertrophie et la musculation.**

Il peut intégrer du cardio, de la récupération, de la nutrition ou des données de santé lorsqu’elles améliorent cette mission.

Mais il ne doit jamais dériver vers :

- une application de running ;
- un coach multisport ;
- un réseau social fitness ;
- une application wellness ;
- une application médicale ;
- un tracker de calories autonome ;
- un chatbot généraliste ;
- un atlas anatomique ;
- une collection de dashboards ;
- un générateur aléatoire d’entraînements.

Le brief visuel historique définissait déjà AUREN comme un **instrument de progression biomécanique**, explicitement distinct d’une application médicale, d’un produit fitness générique, d’un dashboard gamer ou d’une interface « IA » décorative.

Cette définition devient désormais une règle produit générale.

---

# 3. LA BOUCLE FONDAMENTALE D’AUREN

Toute feature doit renforcer au moins une étape de cette boucle :

**COMPRENDRE → PLANIFIER → EXÉCUTER → MESURER → INTERPRÉTER → ADAPTER**

### COMPRENDRE

Qui est cet utilisateur ?

Quelle est sa morphologie mesurée ou déclarée ?

Quel physique veut-il construire ?

Quelles zones paraissent prioritaires ?

Quelles sont ses contraintes réelles ?

Quel matériel possède-t-il ?

Quel est son niveau actuel ?

### PLANIFIER

Quelle quantité de travail doit être distribuée ?

Sur combien de séances ?

Sur quelles zones ?

Avec quels patterns et exercices ?

Dans quel ordre ?

Avec quelles séries, répétitions, charges, temps de repos et cibles d’effort ?

### EXÉCUTER

Quel est l’exercice actif ?

Quelle est la cible ?

Qu’a-t-il fait la dernière fois ?

Quelle charge est pertinente maintenant ?

Que faire si la machine est occupée ?

### MESURER

Qu’a-t-il réellement exécuté ?

Avec quelle charge ?

Combien de répétitions ?

Avec quel niveau d’effort ?

Quelle évolution corporelle est observable ?

Quelle alimentation et quel contexte ont accompagné la période ?

### INTERPRÉTER

Progresse-t-il ?

Où ?

À quelle vitesse ?

Qu’est-ce qui stagne ?

Quel stimulus fonctionne ?

Quel signal est fiable ?

### ADAPTER

Quelle séance vient ensuite ?

Faut-il augmenter une charge ?

Modifier un volume ?

Changer un exercice ?

Redistribuer la semaine ?

Donner davantage de priorité à une zone ?

---

# 4. PREMIÈRE CONNEXION : AUREN DOIT APPRENDRE QUI EST L’UTILISATEUR

Le premier lancement ne doit pas être un formulaire administratif.

C’est la construction du **Body & Training Blueprint** de l’utilisateur.

L’onboarding doit utiliser une divulgation progressive : AUREN recueille immédiatement les informations nécessaires pour construire un premier plan crédible, puis enrichit son modèle au fil des premières séances.

## Niveau 1 — Essentiel

En quelques écrans simples :

- taille ;
- poids ;
- expérience en musculation ;
- nombre réaliste de séances par semaine ;
- temps disponible par séance ;
- environnement d’entraînement ;
- matériel disponible ;
- exercices appréciés ou refusés ;
- limitations connues ;
- priorités physiques perçues ;
- préférence éventuelle entre séances courtes fréquentes et séances longues moins fréquentes.

Le choix d’objectif ne doit pas demander « running, endurance, bodybuilding, crossfit ? ».

Le domaine bodybuilding est acquis.

L’utilisateur exprime plutôt **la manière dont il veut construire son physique** : développement global, prise de masse, recomposition, accent esthétique ou développement prioritaire de certaines zones.

## Niveau 2 — Blueprint corporel

AUREN peut ensuite proposer des mesures simples et compréhensibles :

- tour de taille ;
- épaules ;
- poitrine ;
- bras ;
- cuisses ;
- mollets ;
- envergure ;
- éventuellement d’autres mesures anthropométriques si l’agent scientifique démontre leur utilité.

Les mesures difficiles à reproduire ou dont la valeur décisionnelle est faible ne doivent pas être demandées uniquement parce qu’elles semblent scientifiques.

## Niveau 3 — Questions fonctionnelles

Des questions simples valent souvent davantage qu’une inférence sophistiquée.

Exemples :

« Les mouvements au-dessus de la tête sont-ils confortables ? »

« Arrives-tu à descendre profondément au squat sans gêne ? »

« Certains exercices te donnent-ils systématiquement une douleur ou une gêne ? »

« Sur les presses, sens-tu plutôt les pectoraux ou surtout les triceps/épaules ? »

« Y a-t-il un mouvement que tu évites toujours ? »

Ces réponses deviennent des contraintes ou préférences du moteur.

## Niveau 4 — Photos optionnelles

AUREN peut demander un protocole photographique standardisé :

- face ;
- profil ;
- dos ;
- distance et cadrage guidés ;
- éclairage stable ;
- pose stable ;
- conditions reproductibles.

Le marché utilise déjà cette logique pour comparer une évolution visuelle ; Hevy recommande notamment face/profil/dos et des conditions similaires d’une prise à l’autre.

Une API vision telle que celle d’OpenAI peut analyser plusieurs images et comprendre des caractéristiques visuelles générales.

Mais AUREN doit imposer une frontière stricte :

> **Une photo est un signal visuel. Ce n’est ni un scanner médical, ni une DEXA, ni une mesure exacte des os, ni une mesure fiable du pourcentage de masse grasse.**

Le système peut raisonnablement produire des observations comme :

« développement relatif des épaules visuellement inférieur au torse » ;

« asymétrie visuelle à confirmer » ;

« évolution visuelle probable des bras entre deux prises standardisées ».

Il ne doit pas affirmer :

« ton humérus mesure X cm » ;

« tu as 13,2 % de masse grasse » ;

« cette structure osseuse impose cet exercice ».

OpenAI documente lui-même les limites de précision et de localisation des entrées visuelles.

---

# 5. BODY BLUEPRINT : SÉPARER MESURE, OBSERVATION ET INFÉRENCE

Chaque information corporelle doit porter sa provenance.

AUREN doit distinguer au minimum :

**MEASURED**  
Valeur directement mesurée ou importée.

**USER_REPORTED**  
Information déclarée.

**OBSERVED**  
Observation issue d’une photographie ou d’une interaction.

**INFERRED**  
Conclusion calculée à partir d’autres signaux.

**UNKNOWN**  
Donnée absente ou insuffisante.

Cette distinction doit survivre jusque dans le backend scientifique.

Une inférence ne devient jamais une mesure parce qu’elle a été produite par une IA.

---

# 6. BODY INTELLIGENCE : LE CORPS COMME COCKPIT

Le Body Intelligence est la traduction corporelle de toute l’activité AUREN.

Il ne doit pas être un « score fitness ».

Il doit répondre à trois questions :

> **Qu’est-ce qui est actuellement fort ?  
> Qu’est-ce qui est en retard ?  
> Sur quoi AUREN agit-il maintenant ?**

AUREN possède déjà une taxonomie visuelle structurée autour de onze zones canoniques : `pecs`, `delt_lat`, `delt_post`, `lats`, `upper_back`, `biceps`, `triceps`, `quads`, `posterior`, `calves`, `core`, avec agrégation possible pour les petites surfaces.

Cette taxonomie constitue la vérité fonctionnelle initiale.

Le visuel du cockpit peut utiliser une forme octogonale, des rails, des axes ou d’autres représentations AUREN, mais **la géométrie graphique ne doit jamais créer artificiellement huit vérités biologiques parce que le cadre possède huit côtés**.

Le Body Intelligence peut combiner :

- volume de travail récent ;
- fréquence ;
- progression de performance ;
- données corporelles ;
- évolution des mensurations ;
- évolution photographique ;
- priorités utilisateur ;
- état de récupération estimé ;
- adhérence au programme.

Chaque zone doit pouvoir être inspectée.

Un score opaque est interdit.

Si AUREN affiche « épaules : priorité haute », l’utilisateur doit pouvoir comprendre pourquoi.

Le BodyMap lui-même reste une représentation fonctionnelle et non une mesure d’activation musculaire ; le brief AUREN l’avait déjà explicitement posé.

---

# 7. LE PROGRAMME N’EST PAS UNE LISTE D’EXERCICES

La structure scientifique fondamentale doit être :

> **objectif hebdomadaire → zone → intention/slot → exercice → prescription → exécution**

Un programme ne doit pas être défini conceptuellement comme :

« Incline Press / Lateral Raise / Curl / etc. »

Il doit d’abord exprimer :

« travail de poussée orienté haut de pectoraux » ;

« abduction d’épaule orientée deltoïde latéral » ;

« extension de hanche / chaîne postérieure » ;

puis choisir un exercice concret compatible avec le contexte.

Cela permet :

- substitution ;
- changement de salle ;
- préférence individuelle ;
- adaptation du matériel ;
- création de séances ;
- conservation d’une logique scientifique malgré un exercice différent.

Le précédent blueprint avait déjà commencé à formaliser cette architecture en `slots` d’intention plutôt qu’en listes fixes.

---

# 8. LE MOTEUR DE PROGRAMMATION

Le moteur scientifique doit calculer une allocation de travail à l’échelle de la semaine.

La fréquence des séances et leur durée sont **des contraintes de distribution**, pas des objectifs isolés.

Si deux utilisateurs ont un besoin comparable mais que :

- A s’entraîne 3 fois 75 minutes ;
- B s’entraîne 5 fois 40 minutes ;

AUREN doit pouvoir répartir intelligemment un stimulus hebdomadaire cohérent entre ces deux organisations.

Plus la fréquence disponible augmente, plus les séances peuvent naturellement être courtes.

Moins elle augmente, plus le travail doit être regroupé.

Le moteur doit tenir compte notamment de :

- niveau d’entraînement ;
- historique réel ;
- volume récent ;
- volume toléré ;
- zones prioritaires ;
- matériel ;
- temps ;
- fréquence ;
- performances ;
- proximité de l’échec ;
- récupération estimée ;
- exercices refusés ou préférés ;
- adhérence.

La littérature 2026 place le volume parmi les variables les plus robustes pour l’hypertrophie : l’ACSM observe un bénéfice des volumes hebdomadaires plus élevés, autour d’au moins une dizaine de séries hebdomadaires par groupe dans son résumé, tandis qu’une méta-régression récente retrouve une relation dose-réponse avec rendements décroissants.

Cela interdit néanmoins une implémentation simpliste du type :

`10 sets = good / 20 sets = better`.

AUREN doit apprendre progressivement la quantité utile pour l’utilisateur.

---

# 9. PAS DE FAUSSE SOPHISTICATION SCIENTIFIQUE

Le rôle du moteur n’est pas de maximiser le nombre de variables utilisées.

Il doit maximiser **la qualité des décisions**.

La mise à jour ACSM 2026, fondée sur 137 revues systématiques et plus de 30 000 participants, conclut également que plusieurs raffinements populaires produisent beaucoup moins de différence que le discours fitness ne le suggère : atteindre systématiquement l’échec, choisir machines plutôt que poids libres, complexifier la périodisation ou multiplier les techniques avancées n’améliore pas systématiquement les résultats.

AUREN doit donc préférer :

- cohérence ;
- volume approprié ;
- progression ;
- effort suffisant ;
- bonne sélection d’exercices ;
- régularité ;
- adhérence ;

à de la pseudo-précision.

---

# 10. PROGRESSION : LA RECOMMANDATION DOIT ÊTRE LOCALE

AUREN doit pouvoir recommander pour le prochain set :

- une charge ;
- une fourchette de répétitions ;
- éventuellement une cible d’effort ;
- un repos ;
- ou une conservation de la performance précédente.

Il ne doit pas considérer que progresser signifie battre obligatoirement le set précédent.

Alpha Progression illustre bien l’état de l’art : sa recommandation tient compte de la séance de référence, des sets déjà effectués dans la séance, des répétitions prévues, des poids réellement disponibles dans la salle et éventuellement du RIR. La recommandation peut également diminuer lorsque la performance réelle est inférieure à l’attendu.

C’est cette logique de **guidance révisable** qu’AUREN doit conserver.

La donnée réellement exécutée reste toujours la vérité historique.

---

# 11. RIR, FEEDBACK ET SIGNAL

AUREN ne doit demander à l’utilisateur que des informations qui ajoutent réellement un signal.

Les specs existantes avaient déjà posé la règle correcte :

> un signal primaire doit être saisi une seule fois au niveau le plus proche de l’action.

Trois familles doivent rester distinctes :

**Performance mécanique**  
Poids, répétitions, completion.

**Qualité d’exécution**  
Mouvement propre, compromis, dégradation éventuelle.

**Ressenti / ciblage**  
Sensation du muscle ou adéquation subjective.

Tout score global dérivable doit être calculé, pas redemandé.

AUREN ne doit jamais transformer une séance en questionnaire.

---

# 12. EXERCISE SELECTION

Le choix d’un exercice doit être un arbitrage multi-critères.

Au minimum :

1. intention musculaire ;
2. tolérance de l’utilisateur ;
3. historique de performance ;
4. matériel disponible ;
5. stabilité appropriée ;
6. amplitude exploitable ;
7. profil de résistance pertinent ;
8. préférence ;
9. coût de fatigue ;
10. place dans la séance.

Les données anthropométriques peuvent participer à cet arbitrage mais ne doivent jamais le déterminer seules.

La biomécanique montre bien que des paramètres individuels et techniques modifient les demandes mécaniques d’un mouvement, par exemple sur le squat ; cela justifie une adaptation, pas une typologie rigide des corps.

Les données récentes sur l’entraînement à des longueurs musculaires élevées sont suffisamment intéressantes pour appartenir au corpus de l’agent scientifique, mais restent nuancées et dépendantes de l’exercice.

AUREN doit donc parler en **probabilité et confiance**, pas en dogme.

---

# 13. SUBSTITUTION : PRÉSERVER L’INTENTION

Une machine occupée ne doit jamais casser le programme.

Le système doit posséder un graphe de substitution.

Sa règle absolue est déjà définie :

> **La substitution préserve l’intention du programme sans réécrire l’histoire du template.**

AUREN distingue toujours :

- exercice prévu ;
- exercice réellement exécuté ;
- raison éventuelle ;
- proximité entre les deux.

L’historique de performance des deux mouvements n’est pas artificiellement fusionné.

En séance, l’utilisateur touche **Substituer**, voit quelques options pertinentes classées, choisit et continue.

Pas de navigateur de catalogue au milieu de l’effort.

Gravl confirme la pertinence marché de ce pattern avec un swap contextualisé par muscle et équipement.

---

# 14. PROFILS DE SALLE

AUREN doit connaître l’environnement réel.

Un `GymProfile` peut contenir :

- équipements ;
- machines ;
- plages de charges ;
- incréments ;
- haltères disponibles ;
- unités ;
- préférences éventuelles.

Un changement de salle doit pouvoir modifier la sélection d’exercices sans détruire le programme.

Fitbod applique déjà l’équipement comme contrainte forte de génération, et Gravl reconstruit ses séances autour du matériel du lieu sélectionné.

Pour les machines dont la mécanique diffère réellement, l’historique de charge doit rester contextualisé.

---

# 15. LE MODE SÉANCE EST LA SURFACE SOUVERAINE

Tout le produit peut être sophistiqué.

Mais au gym, AUREN doit redevenir extrêmement simple.

Une seule profondeur d’attention :

> **l’exercice actif.**

L’utilisateur voit immédiatement :

- où il en est ;
- ce qu’il doit faire ;
- sa cible ;
- ce qu’il avait fait précédemment ;
- ce qu’AUREN recommande ;
- son timer ;
- comment substituer ;
- comment valider.

Puis il passe au suivant.

Les autres exercices existent comme rail/jump bar et contexte, pas comme énorme page verticale concurrente.

La DA historique avait déjà posé que la friction minimale et la souveraineté du mode séance étaient des principes fondamentaux.

Le standard qualitatif est celui de Strong : l’interface doit « rester hors du chemin » de l’utilisateur. Strong associe aujourd’hui templates, RPE, timers, mesures corporelles, heat map et analytics tout en conservant cette proposition de simplicité.

---

# 16. CRÉATION MANUELLE DE SÉANCES

AUREN n’enferme jamais l’utilisateur dans les séances générées.

Il doit être possible de :

**Créer une séance → ajouter un bloc → choisir une intention ou un exercice → régler les sets → enregistrer.**

Le builder doit être tactile, rapide et basé sur les mêmes cartes que le reste du produit.

AUREN peut aider silencieusement :

« ce mouvement couvre déjà une intention présente » ;

« le volume épaules devient élevé » ;

« il manque un travail direct de chaîne postérieure » ;

« cet exercice n’existe pas dans cette salle ».

Mais il ne doit pas transformer le builder en outil expert complexe.

Une séance personnelle doit pouvoir devenir un template réutilisable.

L’intelligence de progression AUREN doit continuer à fonctionner sur une séance créée manuellement lorsque les données disponibles le permettent.

---

# 17. LES PROGRAMMES PAR DÉFAUT

AUREN doit proposer dès l’onboarding un plan immédiatement utilisable.

Ces plans ne sont pas de simples exemples.

Ils doivent constituer des **archétypes scientifiques robustes** adaptés par le moteur.

PPL, Upper/Lower, Full Body ou d’autres distributions peuvent exister, mais elles restent des manières d’organiser un programme d’hypertrophie.

Le catalogue SPIGNOS historique ne peut pas être considéré comme vérité scientifique : il contient encore des asymétries de volume, des triceps dans un Pull, une duplication d’identifiant et un programme « abdos » sans exercice abdominal effectif.

Le futur catalogue doit donc être audité et gouverné par l’agent scientifique.

---

# 18. LE COCKPIT DE DONNÉES

AUREN doit valoriser quatre familles de données.

## Training

- charge ;
- répétitions ;
- sets ;
- fréquence ;
- volume ;
- progression ;
- RIR ou proxy ;
- repos ;
- substitutions ;
- PR ;
- historique.

## Body

- poids ;
- mensurations ;
- photographies ;
- tendances ;
- Body Intelligence ;
- mesures importées ;
- observations visuelles.

## Context

- sommeil si disponible ;
- activité/cardio ;
- disponibilité ;
- fatigue déclarée ;
- contexte de salle.

## Nutrition

- calories ;
- protéines ;
- glucides ;
- lipides ;
- éventuellement autres nutriments lorsqu’ils répondent à une question produit.

Chaque donnée doit porter :

- source ;
- date ;
- confiance ;
- caractère mesuré ou inféré.

---

# 19. NUTRITION : SUPPORTER LE BODYBUILDING, PAS DEVENIR MYFITNESSPAL

AUREN doit pouvoir suivre l’alimentation parce que l’alimentation conditionne la progression physique.

Mais la nutrition est une couche auxiliaire.

Le produit doit permettre :

- saisie manuelle ;
- aliments favoris ;
- éventuellement scan de code-barres ;
- photo ;
- photo + texte ;
- correction avant validation ;
- import depuis les plateformes santé lorsque disponible.

L’état de l’art confirme que la reconnaissance photographique réduit fortement la friction. MyFitnessPal propose désormais un Meal Scan ; MacroFactor utilise photo, photo + texte et plusieurs photos pour pré-remplir des aliments éditables.

AUREN doit reprendre surtout le principe suivant :

> **L’IA propose. L’utilisateur valide.**

Une image de lasagnes ne fournit pas magiquement les grammes exacts de chaque ingrédient.

L’IA identifie et estime.

Une base nutritionnelle fournit les valeurs.

L’utilisateur corrige si nécessaire.

Apple HealthKit possède déjà des types de données dédiés à l’énergie, aux protéines, glucides et lipides, tandis que Health Connect expose nutrition, poids, masse maigre, masse grasse, séances d’exercice et autres signaux utiles.

Ces plateformes peuvent devenir des sources de données, jamais la logique métier d’AUREN.

---

# 20. RÉCUPÉRATION

AUREN peut estimer la récupération par zone.

Mais il ne doit pas prétendre mesurer directement l’état biologique d’un muscle s’il ne possède pas cette mesure.

La récupération est un **modèle**.

Elle peut incorporer :

- temps depuis le dernier stimulus ;
- volume ;
- effort ;
- historique ;
- fatigue déclarée ;
- cardio ;
- sommeil disponible ;
- tendance de performance.

Elle doit être exprimée avec une confiance appropriée.

Une bande :

**ready / normal / loaded / uncertain**

peut être scientifiquement plus honnête qu’un faux « 83 % récupéré ».

Fitbod utilise déjà la récupération musculaire comme facteur de sélection de séance.

AUREN doit faire mieux sur l’explicabilité :

> « Pull recommandé aujourd’hui : dos suffisamment reposé, jambes encore chargées après la séance précédente. »

---

# 21. BODY REPORTS ET SCIENTIFIC REPORTS

AUREN ne doit pas seulement stocker les données.

Il doit régulièrement les transformer en compréhension.

Trois niveaux de synthèse doivent exister.

## Post-session

Très court.

- ce qui a été fait ;
- principales progressions ;
- événements notables ;
- implication éventuelle pour la prochaine séance.

## Weekly Review

- séances prévues / réalisées ;
- volume par zone ;
- progression ;
- respect des cibles ;
- poids/tendance corporelle ;
- macros disponibles ;
- anomalies ;
- prochain ajustement probable.

## Cycle Review

À une cadence scientifique définie par le moteur.

- évolution du physique ;
- évolution des performances ;
- zones qui répondent ;
- zones qui stagnent ;
- adhérence ;
- changements de volume ;
- substitutions fréquentes ;
- recommandations du cycle suivant.

Un rapport doit pouvoir être exporté ou partagé.

Mais son contenu est d’abord construit à partir de métriques structurées.

Le LLM peut **expliquer** le rapport.

Il ne doit pas inventer les résultats du rapport.

---

# 22. L’IA N’EST PAS LE MOTEUR SCIENTIFIQUE

C’est une règle architecturale fondamentale.

AUREN possède deux types d’intelligence.

## Intelligence déterministe / scientifique

Elle gouverne :

- volume ;
- progression ;
- historique ;
- scheduling ;
- contraintes ;
- substitutions ;
- sélection d’exercices ;
- récupération ;
- scoring ;
- recommandations quantitatives.

Elle est testable.

Versionnée.

Reproductible.

## Intelligence générative

Elle peut intervenir pour :

- comprendre une réponse libre ;
- analyser une photographie ;
- reconnaître un repas ;
- importer un programme depuis du texte ou une image ;
- expliquer une recommandation ;
- synthétiser un rapport ;
- transformer une règle scientifique en langage compréhensible.

Mais un LLM ne doit pas directement décider :

« ajoute 8 séries de pecs ».

Il peut produire un signal structuré.

Le moteur scientifique accepte, rejette ou contextualise ce signal.

---

# 23. TOUTE RECOMMANDATION DOIT ÊTRE EXPLICABLE

Une recommandation AUREN doit conceptuellement contenir :

**ACTION**  
Ce que le système propose.

**TARGET**  
Exercice, zone, séance ou paramètre concerné.

**INPUTS**  
Données utilisées.

**RATIONALE**  
Pourquoi.

**CONFIDENCE**  
Niveau de confiance.

**EVIDENCE / RULE**  
Règle scientifique ou règle produit à l’origine.

**ALTERNATIVE**  
Que faire si la recommandation n’est pas applicable.

**ENGINE VERSION**  
Version du moteur ayant produit la décision.

L’utilisateur ne verra pas nécessairement tous ces champs.

Mais le système doit pouvoir les produire.

---

# 24. L’AGENT SCIENTIFIQUE

L’agent scientifique est propriétaire de la cohérence biologique et méthodologique d’AUREN.

Il ne développe pas « des features fitness ».

Il entretient une **doctrine scientifique versionnée**.

Ses responsabilités sont :

- veille scientifique ;
- audit du catalogue ;
- taxonomie des mouvements ;
- taxonomie des zones ;
- règles de volume ;
- règles de progression ;
- règles d’effort ;
- gestion du RIR ;
- exercice × longueur musculaire ;
- fréquence ;
- récupération ;
- substitution ;
- méthodes de scoring ;
- Body Intelligence ;
- interprétation anthropométrique ;
- niveau de confiance ;
- validation des hypothèses du moteur.

Chaque règle importante doit posséder une provenance.

La hiérarchie des sources privilégie :

1. position stands / consensus ;
2. systematic reviews / meta-analyses ;
3. essais contrôlés ;
4. littérature mécanistique pertinente ;
5. expertise pratique explicitement identifiée.

Aucune règle ne devient scientifique parce qu’un blog ou un influenceur la répète.

L’agent scientifique doit également pouvoir conclure :

> **« données insuffisantes : ne pas implémenter de règle »**.

C’est une sortie valide.

---

# 25. REGISTRE DE PREUVES

Pour éviter que le backend devienne un ensemble de constantes magiques, chaque doctrine scientifique importante doit être versionnée avec :

- `rule_id` ;
- claim ;
- population ;
- outcome ;
- direction de l’effet ;
- force de l’évidence ;
- incertitude ;
- sources DOI/PMID ;
- date de revue ;
- paramètres affectés ;
- conditions d’application ;
- exceptions connues ;
- version du moteur.

Le code n’a pas besoin de contenir les articles.

Mais une décision scientifique doit toujours pouvoir être remontée vers son raisonnement.

---

# 26. L’AGENT PRODUIT / MOBILE

L’agent produit est propriétaire :

- des flows ;
- de l’application mobile ;
- du shell ;
- de l’onboarding ;
- de la session ;
- du builder ;
- de la présentation Body Intelligence ;
- de l’historique ;
- des interactions ;
- de l’accessibilité ;
- de la performance perçue ;
- de la persistance nécessaire au produit ;
- de la qualité UX.

Il n’est **pas autorisé à inventer une règle scientifique** pour terminer une feature.

Si une décision métier manque, il doit définir le contrat requis et la transmettre au chantier scientifique.

Inversement, l’agent scientifique n’est pas autorisé à réinventer l’interface pour exposer sa sophistication.

Le produit cache la complexité scientifique.

---

# 27. FRONTIÈRE ENTRE LES DEUX AGENTS

La frontière doit être constituée de contrats structurés.

Le moteur scientifique reçoit :

**faits utilisateur + historique + contexte**

et retourne :

**décisions + explications + confiance**.

Le produit décide comment les présenter.

Exemple :

Le scientifique retourne conceptuellement :

`recommendation = increase_load`

`exercise = incline_machine_press`

`next_load = 72.5`

`rep_target = 8–10`

`confidence = high`

`reason = upper range achieved twice with acceptable effort`

Le produit choisit de montrer simplement :

**72,5 kg · 8–10**  
*+2,5 kg proposé*

Cette séparation est essentielle.

---

# 28. ARCHITECTURE PRODUIT ACTUELLE : RÈGLE DE SUPERSESSION

AUREN est désormais construit vers une expérience mobile native iOS/Android, tandis que la logique domaine existante reste une source de vérité à préserver.

Les anciens documents SSR/PWA restent précieux pour :

- les règles métier ;
- l’historique ;
- les contrats ;
- les comportements déjà validés ;
- les surfaces web qui restent utiles.

Ils ne doivent pas obliger le nouveau front mobile à reproduire l’ancienne interface.

De même :

> **native mobile ne signifie pas réécrire arbitrairement le domaine.**

Le nouveau front consomme la vérité métier.

Il ne la recrée pas.

---

# 29. DIRECTION ARTISTIQUE

AUREN reste un instrument.

Pas un coach qui crie.

Pas une app de bodybuilding flashy.

Pas un produit médical anxiogène.

Pas une UI « AI magic ».

La DA doit communiquer :

**precision / calm / control / signal / body / machine**

L’interface est minimaliste en surface et complexe en profondeur.

Chaque écran doit privilégier :

- une action dominante ;
- peu de texte ;
- forte hiérarchie ;
- métriques lisibles ;
- visualisations courtes ;
- micro-explications accessibles à la demande.

Aucune sophistication visuelle ne justifie une augmentation de friction pendant une séance.

---

# 30. STATE OF THE ART À ABSORBER — SANS COPIER

AUREN ne doit copier aucun concurrent.

Il doit absorber leurs solutions déjà validées.

**Strong**  
Référence pour la friction minimale du workout logger.

**Hevy**  
Référence pour la combinaison logging, historique, statistiques par groupe musculaire, mensurations et photos de progression.

**Alpha Progression**  
Référence pour la recommandation opérationnelle set par set tenant compte de l’historique et des contraintes réelles de charge.

**Fitbod**  
Référence pour la génération dépendant du but, du matériel, de la durée, de l’historique, de la récupération et des préférences. Il permet également de faire varier une séance du jour selon la durée ou le matériel.

**Gravl**  
Référence pour les profils de salle, substitutions en temps réel, récupération et import de programmes/images.

**MacroFactor / MyFitnessPal**  
Référence pour la réduction de friction nutritionnelle par photo avec résultat modifiable.

**MeThreeSixty**  
Référence pour la visualisation longitudinale du corps et la comparaison de scans/mesures, pas comme source scientifique absolue.

AUREN doit réunir ce que ces produits séparent.

---

# 31. LE POSITIONNEMENT DIFFÉRENCIANT

AUREN n’essaie pas d’être meilleur que chaque concurrent dans son produit entier.

Il assemble une chaîne qu’aucun de ces benchmarks ne définit comme cœur unique :

> **corps → priorités → entraînement → exécution → nutrition/context → évolution du corps → nouvelle programmation**

C’est cette boucle qui constitue le produit.

Le bodybuilding n’est pas un module parmi d’autres.

Il est la colonne vertébrale qui donne un sens commun à toutes les données.

---

# 32. CE QU’AUREN NE DOIT PAS CONSTRUIRE PAR DÉFAUT

Le manifeste interdit le drift vers :

- feed social central ;
- leaderboard central ;
- gamification envahissante ;
- challenges génériques ;
- badges et flammes ;
- coaching conversationnel omniprésent ;
- catalogue vidéo devenu produit principal ;
- score unique « santé » ;
- diagnostic médical ;
- identification de blessures par photo ;
- chiffres biomécaniques inventés ;
- body-fat estimé avec fausse précision ;
- analytics sans action associée ;
- panneau de cinquante métriques ;
- fonctions multisport qui n’améliorent pas la musculation.

Une fonctionnalité n’est pas pertinente parce qu’un concurrent l’a.

---

# 33. LE TEST D’UNE FEATURE

Avant d’ouvrir une spec, répondre :

**Quel problème de la boucle AUREN cette feature résout-elle ?**

Puis :

**Quelle décision devient meilleure ?**

Puis :

**Quelle donnée lui est nécessaire ?**

Puis :

**Cette donnée est-elle fiable ?**

Puis :

**Quelle surface doit la montrer ?**

Puis :

**Peut-on atteindre le même résultat avec moins de friction ?**

Si aucune décision ne devient meilleure, la feature ne doit probablement pas exister.

---

# 34. DÉFINITION DU PRODUIT TERMINÉ

AUREN aura atteint sa vision lorsque l’expérience suivante sera réelle.

Un nouvel utilisateur installe AUREN.

Il comprend immédiatement qu’il s’agit d’un instrument personnel de construction physique.

Il donne quelques informations simples.

Il peut compléter un Blueprint corporel et éventuellement des photos.

AUREN lui explique sobrement ce qu’il a compris, ce qu’il ne sait pas et ce qu’il considère prioritaire.

Il lui propose un programme de bodybuilding adapté à son temps, sa fréquence, son matériel et son profil.

Il comprend pourquoi.

Il ouvre sa première séance.

Il ne voit pas vingt décisions.

Il voit ce qu’il doit faire maintenant.

AUREN connaît son exercice, sa cible, sa dernière performance et la charge pertinente.

La machine est occupée.

Il substitue en un geste sans détruire le programme.

Il log ses séries.

AUREN ne lui pose aucune question inutile.

La séance se termine.

Les données rejoignent son historique.

Après plusieurs semaines, le cockpit corporel montre ce qui évolue, ce qui stagne et ce qui devient prioritaire.

Les mensurations et photos éventuelles enrichissent cette lecture.

Sa nutrition peut être ajoutée manuellement, importée ou estimée depuis une photo puis corrigée.

AUREN rapproche entraînement, alimentation, contexte et évolution corporelle.

Un rapport lui explique ce qui semble fonctionner.

Le moteur modifie ce qui doit l’être.

La prochaine séance est déjà prête.

L’utilisateur ne voit jamais toute la complexité nécessaire pour produire cette décision.

Il voit seulement :

> **ce qu’il faut faire maintenant — et pourquoi.**

---

# 35. CRITÈRES D’ACCEPTATION DU MANIFESTE

Aucune évolution produit majeure ne doit être considérée alignée si elle viole l’un des principes suivants :

**AUREN reste bodybuilding-first.**

**Le mode séance reste la surface souveraine.**

**La complexité reste principalement dans le backend.**

**Une donnée primaire n’est jamais redemandée inutilement.**

**Mesuré, déclaré, observé et inféré restent distinguables.**

**Toute personnalisation importante possède une explication.**

**Toute science importante possède une provenance et une confiance.**

**Une IA générative ne remplace pas le moteur scientifique.**

**Une visualisation ne prétend jamais mesurer davantage que les données disponibles.**

**Le prévu et le réalisé ne sont jamais confondus.**

**Les substitutions préservent l’intention.**

**L’utilisateur peut toujours modifier ou construire ses propres séances.**

**Le système apprend de l’exécution réelle.**

**Les analytics débouchent sur une décision.**

**Nutrition, cardio, wearables et récupération servent le bodybuilding ; ils ne deviennent jamais le nouveau produit.**

**Le mobile reste immédiatement compréhensible et utilisable pendant un entraînement.**

---

# 36. ORDRE DE PRIORITÉ PRODUIT

Lorsque plusieurs chantiers sont possibles, la priorité est :

**P0 — vérité scientifique et modèle de données**

**P1 — onboarding et Body Blueprint**

**P1 — moteur programme / progression / slots / substitutions**

**P1 — Session Focus native irréprochable**

**P1 — historique et données réellement exécutées**

**P2 — Body Intelligence complet**

**P2 — custom workout builder**

**P2 — récupération et contexte**

**P2 — reports / recommandations longitudinales**

**P3 — nutrition assistée**

**P3 — HealthKit / Health Connect / wearables enrichis**

**P3 — import intelligent de programmes**

**P4 — enrichissements non essentiels**

L’ordre peut être adapté aux dépendances techniques, mais jamais au point d’améliorer un dashboard pendant que la boucle de décision centrale reste incomplète.

---

# 37. DOCTRINE FINALE

AUREN ne doit pas donner l’impression qu’une IA entraîne l’utilisateur.

Il doit donner l’impression qu’un **instrument extrêmement bien conçu comprend son entraînement**.

Il n’est pas intelligent parce qu’il parle.

Il est intelligent parce qu’il :

**observe correctement ;  
conserve correctement ;  
raisonne correctement ;  
propose correctement ;  
explique suffisamment ;  
et demande très peu.**

La mission finale est donc :

> **Construire le système personnel de référence pour transformer un corps par la musculation — avec la simplicité d’un carnet parfait en surface et la rigueur d’un moteur scientifique en profondeur.**