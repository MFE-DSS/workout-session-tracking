---
name: UI_TRANSFORMATION_BRAINSTORM_V2_normalized
type: brainstorm-archive-normalized
source: session brainstorm produit (opérateur, 2026-07-02)
status: READ-ONLY BRAINSTORM ARCHIVE — do not amend
encoding_status: mojibake decoded, semantics untouched
raw_source: UI_TRANSFORMATION_BRAINSTORM_V2_raw.md
---

> **Note d'archivage :** ce fichier est la version décodée du raw. Aucune reformulation sémantique n'a été appliquée : uniquement correction du mojibake UTF-8 double, suppression des marqueurs internes de source `îfileciteî...î` et `îciteî...î` (non-sémantiques), et remise en état de la typographie française. La version raw reste la source de vérité de la trace. Pour la synthèse actionnable, voir `../UI_TRANSFORMATION_ROADMAP.md`.

---

# Transformer SPIGNOS en application biomécanique minimaliste

## Diagnostic du produit actuel

Ton produit n'est pas un prototype vide à « habiller » : c'est déjà une web app mobile-first de suivi de séance, pensée pour être utilisée au gym, avec feedback normalisé, page session dédiée et ambition déclarée de devenir une PWA complète. Le README situe clairement la cible sur téléphone, en usage réel, et place la « PWA complète » comme évolution de la base FastAPI SSR actuelle.

La bonne nouvelle, c'est que la couche technique de portabilité est déjà amorcée. Le shell HTML déclare `viewport-fit=cover`, un `theme-color`, le mode `mobile-web-app-capable`, un manifest web, et charge une feuille CSS globale plus une feuille dédiée à la page session. Autrement dit, l'app est déjà pensée comme un objet installable et « app-like », pas comme un simple site responsive.

Le vrai problème n'est donc pas l'absence de structure, mais le langage visuel actuel. Aujourd'hui, le design system public du repo reste très « cockpit dark utility » : fond `#0f1115`, surfaces gris foncé, accent orange `#f25f3a`, cartes sombres, topbar utilitaire, bannière de séance active avec dot animé, et un menu qui expose beaucoup de surfaces produit dès le niveau global. Cela donne un rendu puissant mais plus « console d'opérateur » que « produit biométrique chirurgical ».

Le shell navigation confirme cette impression de cockpit multi-systèmes : Accueil, Programmes, Historique, Physique, Progression, Classement, Squads, Profil, Coach, puis Déconnexion. Ce n'est pas absurdement mauvais, mais sur mobile cela fait beaucoup pour une marque qui voudrait respirer la précision, la sobriété et la maîtrise. En clair : ton produit a gagné des features plus vite que sa hiérarchie visuelle.

En revanche, la page séance actuelle est déjà ton meilleur point d'appui pour la refonte. Le cycle Sx_29 a livré un focus mode mobile avec header sticky, jump bar, carte active, CTA sticky, timer de repos no-JS friendly, CSS dédiée et JS vanilla minimal. La closure dit explicitement que cette refonte a été construite en SSR/Jinja/CSS/JS vanilla, sans bundler ni framework, avec fallback no-JS intact. C'est très précieux : ton futur design peut être ambitieux sans casser l'architecture qui fait déjà ta force.

Il y a enfin une contrainte de gouvernance à respecter : la roadmap du repo note explicitement que la « UI renovation » est bloquée tant que le gate de stabilisation production n'est pas conclu. Cela veut dire qu'au bon niveau de maturité, ce que tu dois lancer maintenant n'est pas un coup de peinture opportuniste, mais un chantier préparé : benchmark, direction visuelle, spec de tokens, réduction du chrome global, puis refactor page par page.

## Les références les plus pertinentes pour ta cible

Pour le cœur « bodybuilding end-to-end », les meilleures références produit ne sont pas les apps wellness grand public, mais les trackers de musculation qui ont déjà résolu la friction de logging. Hevy se présente comme un workout tracker iOS/Android centré sur le logging, la progression, les timers de repos, les notes, les charts, l'Apple Watch / WearOS et même un usage desktop. C'est une excellente référence fonctionnelle pour tout ce qui touche au journal de séance, aux routines, à la progression et à la portabilité multi-surface.

Strong joue la même partition mais avec une promesse encore plus nette : « Think less. Lift more. », « the simplest, most intuitive workout tracking experience », « designed to stay out of your way », et « Your Training. Any Device. » avec iPhone, Android et Apple Watch. Pour ton cas, Strong est la référence à copier sur un point précis : la sensation de friction quasi nulle pendant la séance. Si ton redesign devient plus « beau » mais moins évident que Strong pour logguer vite, tu vas dans la mauvaise direction.

Pour la direction « biotech / santé physique avancée », Levels est sans doute la référence la plus proche de ce que tu décris. Leur proposition est blanche, calme, explicative, presque clinique, avec un langage de confiance très net : « Private, secure, and personalized », app-first, personnalisation progressive par les données, logs de repas, logs d'habitudes, tendances long terme, puis enrichissement par de la donnée connectée. Ce qui est intéressant ici n'est pas le sujet métabolique lui-même, mais la grammaire visuelle implicite : peu de bruit, beaucoup d'espace, une autorité calme, et une narration de données qui évite l'effet « dashboard gamer ».

Oura apporte une autre brique essentielle : la désirabilité « health-tech premium ». Leur site résume très bien le territoire avec « Subtle. Power. » puis « Form meets function », et relie design discret, mesures nombreuses et guidance quotidienne. Le vrai point à retenir n'est pas l'anneau, mais l'idée de calcul invisible : l'interface n'a pas besoin de crier pour paraître avancée. Elle peut être douce, silencieuse, très neutre visuellement, tout en donnant l'impression d'être plus sérieuse et plus futuriste.

WHOOP, enfin, est utile moins pour sa palette que pour sa discipline d'UX. Leur message est « lasting progress », « complete picture of your health », puis surtout « Zero distractions » grâce à un design screen-free sans « pings » ni « bells & whistles ». Même si WHOOP reste plus sombre, plus sport-performance et plus masculine/agressive que la cible que tu décris, il y a une leçon très forte ici : une interface sérieuse de santé/performance ne surcharge pas l'utilisateur, elle orchestre les signaux.

Si je résume brutalement : Strong et Hevy t'apprennent la cadence du logging ; Levels et Oura t'apprennent la crédibilité biométrique ; WHOOP t'apprend la discipline de hiérarchie. La future identité de ton produit doit réunir les trois, mais sans reprendre ni le noir compétitif de WHOOP, ni le côté « fitness social » de Hevy, ni la douceur presque trop lifestyle d'Oura.

## La cible esthétique qui semble la plus juste

La direction qui ressort le plus clairement de ta demande n'est ni « app SaaS moderne », ni « app sport énergique », ni « app AI glossy ». C'est une direction que j'appellerais **performance clinique**. Le mot important n'est pas « futuriste » au sens marketing, mais au sens **instrumental** : quelque chose qui paraît issu d'un labo de biomécanique ou d'un produit de suivi physiologique premium.

Concrètement, cela implique un renversement complet de la logique visuelle actuelle. Aujourd'hui, ton système repose sur fonds sombres, surfaces empilées, accent chaud, et chrome relativement lourd. La cible que tu décris demande au contraire une base blanche ou blanc cassé, beaucoup de vide, des bordures fines, des gris froids, un accent très parcimonieux — idéalement un bleu minéral, un teal chirurgical ou un vert menthe extrêmement désaturé — et des états qui privilégient la structure plutôt que les aplats. Le produit doit donner l'impression qu'il mesure et clarifie, pas qu'il « motive ». Cette rupture est cohérente avec le fait que ton repo possède déjà une architecture app-like et une page séance très rationalisée ; il manque surtout un nouveau système de tokens et une réduction du chrome global.

Je te proposerais de penser la direction visuelle en trois territoires, puis d'en valider un seul.

Le premier territoire est **Clinical Lab**. Fond blanc, gris pierre, accent cobalt très contenu, micro-typo stable, grands espacements, presque aucun aplat décoratif, cartes qui ressemblent à des panneaux de mesure. C'est la piste la plus « Levels + Oura », et probablement la plus alignée avec ton envie de biotech minimaliste.

Le deuxième territoire est **Quiet Instrument**. Toujours clair, mais avec davantage de repères techniques : grille légère, mono pour les métriques, séparateurs précis, badges ultra-dosés, composants qui ressemblent à des blocs opératoires ou à des instruments calibrés. Cette piste colle très bien à ton ADN actuel de produit structuré, parce qu'elle conserve la sensation d'ingénierie sans garder l'esthétique sombre du cockpit. Elle serait probablement la plus naturelle pour faire évoluer SPIGNOS sans tout dénaturer d'un coup.

Le troisième territoire est **Soft Biomechanics**. Base blanche aussi, mais avec un peu plus de chaleur humaine : photo ou texture extrêmement discrète, fond ivoire, accent sauge ou aqua, moins « labo », plus « médecine préventive premium ». C'est séduisant, mais pour ton produit de séance bodybuilding, je pense que ce serait moins juste que les deux premiers : le risque est de glisser vers le wellness au lieu d'une vraie machine de progression.

Ma recommandation claire est donc un **hybride Clinical Lab + Quiet Instrument**. Autrement dit : fond blanc, structure chirurgicale, métriques nettes, micro-interactions minimalistes, une seule couleur de signal, aucun gradient « AI », aucune 3D, aucune illustration héroïque, aucune rhétorique « crush your goals ». Les slogans et les composants doivent parler comme un capteur de confiance, pas comme un coach qui crie. Cette lecture est d'ailleurs cohérente avec les références qui performent le mieux : Strong dit « think less », Levels dit « stop guessing », Oura dit « subtle », WHOOP dit « zero distractions ».

## Le cadre de benchmark à utiliser pour éviter le goût personnel

Le benchmark ne doit pas être « qu'est-ce qui est joli ? », mais « qu'est-ce qui rend le produit plus fort, plus portable et plus crédible ? ». Pour ton cas, je te recommande six critères seulement.

Le premier critère, le plus important, est la **friction de logging**. Une séance doit pouvoir être enregistrée à une main, vite, sans ambiguïté. Strong et Hevy sont les références ici, non parce qu'ils sont magnifiques, mais parce qu'ils ramènent tout à l'action essentielle : journaliser, voir la progression, repartir. Si ton redesign ajoute du spectacle et ralentit le logging, il échoue.

Le deuxième critère est la **lisibilité biométrique**. Levels, Oura et WHOOP montrent qu'une interface « santé avancée » n'a pas besoin d'une densité massive d'écrans. Elle doit d'abord dire clairement : voici le signal principal, voici son contexte, voici ce que cela veut dire. C'est cette hiérarchie — signal, contexte, interprétation — qui doit devenir ton standard sur Home, Progression, Physique et Coach.

Le troisième critère est la **portabilité réelle**. MDN rappelle qu'une PWA forte doit capitaliser sur une base unique multi-plateforme, installable, potentiellement offline et bien intégrée à l'OS. Ton app a déjà manifest, mode standalone, viewport mobile, et shell app-like ; le vrai benchmark ici est donc de pousser cette base jusqu'à un niveau de finition où l'utilisateur a la sensation d'ouvrir une vraie app, quel que soit le device, sans réécriture native prématurée.

Le quatrième critère est la **sobriété de chrome**. Le produit ne doit pas afficher dix destinations différentes comme si elles avaient toutes la même importance. Aujourd'hui ton shell expose beaucoup d'entrées globales ; demain, la coque doit juste permettre de revenir à la séance, voir les programmes, lire la progression, et accéder au profil/coach depuis une surface secondaire. Tout le reste doit être subordonné à la tâche principale. C'est exactement la logique des meilleurs produits de santé/performance : peu d'entrées, mais chacune très nette.

Le cinquième critère est la **confiance**. Levels insiste sur « private, secure, personalized » et sur des standards comme HIPAA / SOC 2 ; WHOOP met en avant des données chiffrées, des labs, de la sécurité des données ; Oura travaille son territoire premium sur la continuité et la discrétion. Si tu veux passer de « cockpit geek » à « plateforme de bio-hacking technologique », ta UI doit visuellement exprimer la confiance avant l'excitation. Cela veut dire moins d'effets, plus de structure, des labels plus précis, et un ton éditorial moins énergisant.

Le sixième critère est l'**accessibilité tactile et perceptive**. W3C rappelle le seuil de 44×44 CSS pixels et explique pourquoi le mobile, le one-hand use et les tâches séquentielles rendent ce sujet critique. Ton repo est déjà bon sur ce point : le focus mode introduit précisément des tap targets 44×44, des non-color cues et une structure sticky pensée pour le gym. Il faut donc conserver ce niveau et l'étendre au shell entier lors de la refonte.

## Brainstorming de marque et de nom

Le nom actuel **SPIGNOS** est très visible dans le shell, le titre et le footer. Il fonctionne comme nom de système, mais il sonne plus « moteur interne » ou « outil d'ingénierie » que « produit biométrique premium ». Si ta direction assumée est de transformer le cockpit geek en produit bio-tech minimaliste, le rebrand a du sens.

Le bon nom pour cette cible doit respecter cinq règles simples : être court, facile à prononcer en français et en anglais, ne pas sonner « AI startup », ne pas faire médical réglementé, et pouvoir exister aussi bien sur une app blanche premium que sur une page séance utilitaire. Il faut un mot qui évoque le signal, le corps, la précision ou le mouvement — sans tomber dans les racines trop génériques du fitness type « fit », « gym », « strong », « boost », « prime ».

Je te propose trois familles nominales.

La première famille est **muscle / biomécanique**. Ici, les meilleurs candidats sont **MYON**, **KINE**, **SOMA**. Mon préféré est **MYON** : très court, très mémorable, ancré dans l'idée musculaire sans être littéral, visuellement fort sur une interface minimaliste. **KINE** est élégant et international, mais déjà sémantiquement très chargé en français. **SOMA** est superbe mais probablement trop utilisé ailleurs.

La deuxième famille est **instrument / signal**. Ici, les bons candidats sont **VYON**, **NEMA**, **AXYL**, **SYRO**. Mon préféré est **VYON** si tu veux quelque chose de très brandable, très contemporain, presque clinique, sans signification trop explicite. Il a une bonne tête de marque blanche haut de gamme.

La troisième famille est **animal / densité / impact**, plus proche de ton exemple **RATEL**. Là, les candidats pourraient être **RATEL**, **ORYX**, **KORA**. Mon avis honnête : **RATEL** est mémorable, dur, vivant, mais moins « biotech chirurgical » que **MYON** ou **VYON**. C'est plus un nom de machine de performance qu'un nom de produit santé avancée.

Si je devais te pousser vers trois finalistes à valider créativement, ce serait **MYON**, **VYON** et **RATEL**.

**MYON** si tu veux la meilleure fusion entre bodybuilding, biologie et minimalisme.
**VYON** si tu veux la meilleure option premium, abstraite et très brandable.
**RATEL** si tu veux un nom plus instinctif, plus mémorable, plus agressif.

Ma recommandation nette, à ce stade, serait **MYON** comme piste A, **VYON** comme piste B, et **RATEL** comme benchmark de tonalité plutôt que comme choix principal. Je ne présente pas ici de validation juridique ou de disponibilité de domaine : ce serait une étape séparée.

## Le chantier recommandé pour faire la bascule sans casser le produit

Le premier chantier ne doit pas être du code visuel, mais un **cadre directeur de redesign**. La roadmap actuelle bloque la rénovation UI tant que la stabilisation prod n'est pas close ; c'est cohérent. La bonne séquence consiste donc à produire un spec de rebrand / visual system avant de toucher les templates.

La première phase devrait être **la refonte des fondations**. Elle comprend le nouveau nom, la nouvelle palette, les tokens, la typo, les rayons, les bordures, le système d'icônes, les densités d'espacement et les règles de ton éditorial. Il faut passer d'un système « dark surfaces + orange accent » à un système « white surfaces + cold neutrals + one signal accent + mono métrique ». Techniquement, ton repo est déjà bien préparé pour cela parce qu'il utilise des variables CSS racine et une feuille dédiée à la session.

La deuxième phase devrait être **la réduction du chrome global**. Avant même de redessiner les cartes, il faut redessiner la coque : topbar, menu, bannière de séance active, footer, titres de page, structure des vues analytiques. Le but n'est pas d'enlever des fonctionnalités, mais de faire comprendre qu'il y a une mission principale et des surfaces secondaires. Sur mobile, j'irais vers un shell avec quatre entrées maximum visibles au premier niveau, puis le reste derrière un menu profil ou « More ».

La troisième phase devrait être **l'extension du langage Sx_29 au reste de l'app**. La page séance est déjà ton meilleur prototype de produit du futur : sticky header, jump bar, carte active, CTA sticky, timer de repos, JS minimal, no-JS intact. Il ne faut pas la jeter ; il faut l'utiliser comme matrice et lui appliquer le nouveau langage clair. Ensuite seulement, tu déclines les mêmes principes sur Accueil, Programmes, Historique, Progression, Physique et Coach.

La quatrième phase devrait être **la portabilité perçue**. MDN rappelle qu'une vraie PWA gagne en valeur quand une base unique se comporte comme une app sur plusieurs devices, avec installabilité, intégration OS, et éventuellement offline/background. Cela veut dire que, pour toi, la prochaine marche n'est probablement pas React Native ni Flutter : c'est d'abord une PWA plus mature, plus nette, plus installable, avec raccourcis utiles, manifest peaufiné, icônes propres, et éventuellement offline ciblé sur la séance active.

La cinquième phase devrait être **la validation par dogfood visuel**, pas par goût théorique. W3C rappelle pourquoi les targets 44×44, le one-hand use et les tâches séquentielles sont structurants sur mobile ; ton repo a déjà commencé à internaliser ces règles dans le focus mode. La bonne façon d'achever la rénovation sera donc de tester une vraie séance, un vrai enchaînement home → programme → séance → progression, puis de corriger les frictions hautes, pas de polir des outils Dribbble pour eux-mêmes.

Le point décisif, au fond, est simple : tu n'as pas besoin de « plus de modernité ». Tu as besoin d'un **langage produit unique**. Aujourd'hui, Workout Session Tracking / SPIGNOS a une base technique propre, une page séance déjà solide, et beaucoup de surfaces utiles, mais il parle encore comme une console de features. La cible la plus crédible n'est pas une app fitness plus sexy ; c'est une **machine de progression biomécanique**, blanche, calme, précise, presque clinique, qui fait sentir à l'utilisateur qu'il est entre les mains d'un instrument fiable. Les références qui t'y mènent sont déjà identifiées : Strong pour l'évidence, Hevy pour la couverture séance, Levels pour la confiance blanche, Oura pour la subtilité premium, WHOOP pour la hiérarchie sans distraction.
