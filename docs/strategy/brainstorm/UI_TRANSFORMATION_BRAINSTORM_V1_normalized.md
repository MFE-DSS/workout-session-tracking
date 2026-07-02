---
name: UI_TRANSFORMATION_BRAINSTORM_V1_normalized
type: brainstorm-archive-normalized
source: session brainstorm produit (opérateur, 2026-07-02)
status: READ-ONLY BRAINSTORM ARCHIVE — do not amend
encoding_status: mojibake decoded, semantics untouched
raw_source: UI_TRANSFORMATION_BRAINSTORM_V1_raw.md
---

> **Note d'archivage :** ce fichier est la version décodée du raw. Aucune reformulation sémantique n'a été appliquée : uniquement correction du mojibake UTF-8 double, suppression des marqueurs internes de source `îfileciteî...î` et `îciteî...î` (non-sémantiques), et remise en état de la typographie française. La version raw reste la source de vérité de la trace. Pour la synthèse actionnable, voir `../UI_TRANSFORMATION_ROADMAP.md`.

---

# Cadre de transformation de Spignos vers une application mobile minimaliste de performance

## Point de départ du produit

Le bon diagnostic n'est pas « faire une refonte cosmétique », mais « réaligner le produit avec sa vraie promesse ». D'après les documents techniques déjà présents dans ton flux, ton application n'est pas un proto fragile : elle a déjà une base SSR FastAPI + Jinja, un mode séance mobile dédié, une feuille de style `session_focus.css` extraite, un fallback no-JS préservé, et une discipline de livraison par specs, rapports et closure docs. Autrement dit, tu as déjà l'ossature d'un produit sérieux ; ce qu'il manque, c'est une grammaire visuelle et informationnelle cohérente à l'échelle du produit.

Le point fort actuel n'est pas un « dashboard intelligent », mais l'exécution de séance. Les extraits déjà livrés montrent que `session_detail` a été découpé en partials ciblés, avec un header de focus, une carte d'exercice dédiée et un timer de repos séparé. Le template dogfood Sx_29 insiste d'ailleurs sur ce qui doit être testé en réel : header sticky, jump bar, carte active, sticky CTA, timer et frictions de logging sur mobile. Cela indique où est la valeur produit la plus tangible aujourd'hui : la séance en cours, pas l'habillage « cockpit ».

Le commentaire design le plus important est donc celui-ci : **ne détruis pas l'honnêteté fonctionnelle du produit en cherchant un « look premium » trop tôt**. Strong et Hevy se positionnent eux-mêmes sur la simplicité radicale du logging ; Strong revendique « the simplest interface », et Hevy insiste sur un tracker « simple » et « intuitive ». Cette logique est cohérente avec ce que ton produit a déjà commencé à faire techniquement.

## Ce que le produit doit devenir

Ta cible n'est pas un énième tracker de musculation noir, saturé, « hardcore gym bro ». Ta cible est plus rare : **un outil de performance corporelle calme, clinique, mobile-first, end-to-end**, où la musculation reste le cœur, mais où la présentation s'inspire davantage des apps de biométrie et de santé avancée que des apps de salle classiques. Apple Health se présente comme un lieu central et sécurisé pour les données de santé avec tendances et graphiques interactifs ; Levels parle de comprendre l'effet de l'alimentation, du sommeil, de l'exercice et du stress ; Ultrahuman d'un dashboard unifié de santé ; WHOOP structure l'expérience autour d'un score de récupération ; Oura met en avant plus de trente biométriques et une lecture approfondie du sommeil et de l'activité.

La bonne transformation consiste donc à déplacer le centre de gravité perceptif du produit. Aujourd'hui, « Spignos » peut être perçu comme un cockpit de tracking. Demain, l'application doit donner l'impression d'un **instrument de pilotage physiologique**, même quand elle parle simplement de séries, reps et charges. Cela veut dire : moins de chrome visuel, moins d'éléments en concurrence, plus d'unités lisibles, plus de hiérarchie typographique, plus de calme, et des surfaces qui ressemblent à de l'instrumentation de santé plutôt qu'à un tableau de bord de gamer. Cette direction est compatible avec les recommandations Apple et Material, qui ancrent la qualité perçue dans la hiérarchie, la couleur comme signal, et l'usage discipliné des composants, pas dans la décoration.

En clair, ton produit doit converger vers cette formule :

| Axe | Position actuelle utile | Position cible |
|---|---|---|
| Fonction | tracker de séance robuste | système de performance corporelle |
| Ton | technique / geek / cockpit | clinique / précis / calme |
| Mobile | déjà bien engagé sur la séance | shell mobile natif perçu partout |
| Esthétique | utilitaire fragmentée | biométrie blanche, chirurgicale, sobre |
| Valeur primaire | logger correctement | décider et exécuter la bonne séance, au bon rythme |

Cette cible ne demande pas de changer ton moteur avant tout ; elle demande de **changer le langage de surface**.

## Benchmarks à copier et à éviter

Le benchmark ne doit pas être monolithique. Il faut séparer le benchmark **fonctionnel de strength tracking** du benchmark **esthétique de santé-tech**.

| Référence | Ce qu'il faut voler | Ce qu'il faut éviter |
|---|---|---|
| Strong | obsession de la simplicité, rest timer intégré, stats avancées sans bloquer le logging, logique progressive barbell | look trop « outil de log » si tu veux une identité plus premium santé-tech |
| Hevy | clarté des flows, progression par métriques, planification + log + stats au même endroit | dimension communautaire/sociale si ce n'est pas ton différenciateur |
| Fitbod | promesse d'adaptation intelligente, personnalisation orientée progression, lien direct entre algorithme et séance | dépendance à une promesse « AI trainer » trop forte si l'expérience de base n'est pas encore minimaliste |
| Apple Health | centralisation calme, lisibilité, sentiment de fiabilité, tendance plutôt que bruit | neutralité trop générique si tu perds l'intensité performance/strength |
| Levels | cadrage physiologique, explication personnalisée, pédagogie sans folklore | narration trop « métabolique » si tu oublies la musculation comme acte central |
| Ultrahuman | dashboard unifié, scores actionnables, posture « performance lab » | risque de sur-abstraction si la séance réelle devient secondaire |
| WHOOP | score de readiness/récupération, framing « what should I do today? » | dépendance au wearable, surcharge de métriques dérivées si le service ne les alimente pas encore |
| Oura | biométrie crédible, luxe calme, lecture profonde mais accessible | glissement trop wellness / lifestyle si tu veux rester strength-first |

Le benchmark template doit suivre la même logique. Pour la structure mobile et la discipline visuelle, tes meilleures bases sont les ressources officielles Apple et Material. Apple fournit des design resources officielles pour Figma et Sketch ; Material fournit son kit Figma M3 et une grammaire de composants complète. En revanche, les kits comme Untitled UI ou shadcn/ui sont excellents pour l'inspiration web, mais ils sont pensés autour de Figma web et, côté implémentation, de React/Tailwind. Dans ton cas, où la base existante est SSR/Jinja et où React est explicitement absent, les prendre comme code source augmenterait le drift. Il faut les utiliser au mieux comme galerie d'architecture visuelle, pas comme solution d'implémentation.

Le commentaire design central ici est simple : **copie la discipline d'Apple et Material ; copie la clarté fonctionnelle de Strong/Hevy ; copie le framing physiologique de Levels/WHOOP/Oura ; ne copie pas leur stack, ni leur marketing, ni leurs gimmicks**.

## Direction visuelle et UX cible

La cible visuelle peut se résumer ainsi : **fond blanc cassé, composants blancs francs, texte presque noir, un seul accent froid, beaucoup d'air, peu d'ombre, pas de gros visuels, pas de textures, pas de gradients « IA »**. Cette direction n'est pas en contradiction avec les guidelines de plateforme ; Apple insiste sur une hiérarchie lisible, une typographie structurée et des couleurs système adaptées à l'accessibilité, tandis que Material structure aussi l'interface par rôles de couleur et de typographie, plutôt que par surcharge décorative.

En pratique, je recommande ce langage :

- **Surfaces** : blanc pur, gris très léger, séparations fines.
- **Accent** : un turquoise froid ou un bleu minéral unique, réservé aux états actifs, scores favorables et CTA principaux.
- **Typographie** : très peu de tailles, mais une hiérarchie nette ; grands titres sobres, labels courts, unités explicites.
- **Icônes** : trait simple, sans remplissages lourds.
- **Charts** : fins, utiles, jamais héroïques.
- **Motion** : très discrète, jamais nécessaire pour comprendre l'écran.
- **Illustration** : quasi absente.

Côté UX, la règle qui doit tout gouverner est la suivante : **une décision principale par écran, une profondeur d'attention par moment**. NN/g décrit la progressive disclosure comme le fait de repousser les éléments avancés vers une couche secondaire pour réduire l'erreur et la complexité perçue. C'est exactement ce qu'il faut faire ici : pendant la séance, l'utilisateur n'a pas besoin d'un laboratoire entier ; il a besoin de savoir quoi faire maintenant, avec juste assez de contexte pour être confiant.

La navigation doit suivre cette discipline. Apple rappelle qu'une tab bar sert à naviguer entre sections, pas à lancer des actions, et Material dit la même chose pour la navigation bar, alors que l'action principale doit être représentée séparément. À l'échelle de ton produit, cela veut dire : **la bottom nav sert à aller de Aujourd'hui à Historique à Profil/Settings ; le logging de séance reste un CTA contextuel dans la surface de contenu**, à la manière de ton sticky CTA déjà livré dans le focus mode.

Enfin, il faut garder comme contrainte dure le confort mobile. WCAG 2.2 formalise une taille minimale de cible de 44 × 44 CSS pixels pour réduire les activations accidentelles. Comme ton produit a déjà commencé à intégrer cette logique dans Sx_29, il faut la hisser au rang de principe global, pas de détail local.

## Chantiers de transformation sans casser le produit

La bascule la plus sûre n'est pas une refonte « big bang ». C'est une **migration par couches**. Ton avantage, c'est que le produit est déjà organisé par specs et par surfaces. Il faut donc faire une convergence visuelle **sans toucher à la logique métier**, puis remapper progressivement les écrans les plus critiques. La présence d'un `session_focus.css` dédié, chargé après `app.css`, est un très bon point de départ pour une évolution pilotée par tokens et par route.

Je te recommande cet ordre de chantiers :

| Chantier | Pourquoi c'est le bon ordre | Ce qu'il ne faut pas faire |
|---|---|---|
| Fondation visuelle | fixe la grammaire avant de repeindre les écrans | commencer par des maquettes spectaculaires sans tokens ni règles |
| App shell mobile | donne immédiatement un sentiment « app » cohérent | refaire toute l'IA en même temps |
| Re-skin séance active | c'est déjà le point le plus fort du produit et le plus proche d'un usage réel | repartir d'une page blanche alors que le focus mode existe déjà |
| Home/Today | permet de traduire le produit en langage « readiness / next best session » | y entasser toutes les analytics |
| Historique / progression | convertit la donnée accumulée en lecture plus calme et premium | faire des dashboards lourds |
| Portabilité | rend l'app installable et plus native perçue avec le code existant | lancer une réécriture native ou SPA maintenant |
| Rebrand | ne vient qu'une fois le langage du produit suffisamment stabilisé | changer de nom avant d'avoir stabilisé le shell et les écrans clés |

Pour la portabilité, la bonne trajectoire n'est pas « React Native », ni « SPA obligatoire ». MDN définit les PWA comme des applications construites avec les technologies web capables d'offrir une expérience proche du natif depuis un codebase unique ; web.dev rappelle qu'une architecture SPA augmente la complexité et le coût initial de chargement. Comme ton produit part déjà d'un SSR propre avec no-JS fallback, la meilleure stratégie est : **app web installable d'abord, native plus tard seulement si l'usage le justifie**. Safari sur iPhone permet déjà d'ajouter un site à l'écran d'accueil et de l'ouvrir comme une web app.

Le commentaire produit le plus stratégique est donc celui-ci : **la « mise à l'échelle » doit d'abord signifier cohérence visuelle, navigation propre, installation facile et robustesse mobile — pas changement de stack**.

## Corpus de specs à écrire en premier

Si tu veux rester en mode spec-driven avec ton code superpower sans drift, il faut éviter les specs « fourre-tout ». Chaque spec doit porter une surface, une intention, des protections, et un mode de vérification. Voici le corpus que je te recommande d'écrire avant tout gros chantier UI.

| Spec | Objet | Pourquoi elle doit exister |
|---|---|---|
| **Sx_UI_01 Brand Foundation Spec** | nom de marque, tone of voice, slogan court, principes visuels interdits/autorisés | évite que le chantier UI dérive en patchwork |
| **Sx_UI_02 Design Tokens Spec** | palettes, surfaces, typo, rayons, bordures, ombres, espacements, états, chart tokens | permet de repeindre sans réinventer écran par écran |
| **Sx_UI_03 App Shell and Navigation Spec** | top bar, bottom nav, titres, actions globales, safe areas, breadcrumb de contexte | fixe la structure app-like et évite les écrans orphelins |
| **Sx_UI_04 Session Focus Reskin Spec** | refonte visuelle du flow séance déjà livré, sans changer le moteur | capitalise sur le meilleur usage actuel |
| **Sx_UI_05 Today and Readiness Home Spec** | écran d'entrée orienté « quoi faire aujourd'hui » | traduit le produit en système de performance plutôt qu'en archive |
| **Sx_UI_06 Exercise Intelligence Presentation Spec** | comment présenter recommandation, surcharge, historique récent, explainer | évite que l'intelligence produit soit cachée ou trop bavarde |
| **Sx_UI_07 History and Progress Spec** | historique, tendances, PR, volume, cycles, comparaisons | transforme la data en lecture premium et utile |
| **Sx_UI_08 Portability and Installability Spec** | manifest, icône, install prompt, cache minimal, mode offline utile | fait passer l'app de « site » à « outil transportable » |
| **Sx_UI_09 Accessibility and Motion Spec** | contrastes, cible tactile, focus, reduced motion, aria, comportement no-JS | empêche la dette UX silencieuse |
| **Sx_UI_10 Rebrand Migration Spec** | mapping Spignos → nouveau nom, copy, assets, slug, compat, écran de transition | permet de renommer sans casser la reconnaissance ni l'existant |
| **Sx_UI_11 Screenshot Regression Spec** | golden screens, viewport mobile/desktop, critères de non-régression visuelle | protège contre le drift pendant les sprints |

La règle d'or pour ces specs est la suivante : **une spec de surface ne touche pas à la logique métier**. Si tu modifies l'algorithme et le visuel dans le même sprint, tu perds immédiatement ta capacité à diagnostiquer les régressions. Ce principe est particulièrement important dans ton repo, justement parce qu'il a déjà une culture de protection des services core et de livraisons fermées par closure report.

Le chantier recommandé pour basculer proprement serait donc :

1. écrire **Brand Foundation** et **Design Tokens** ;
2. écrire **App Shell** ;
3. re-skinner **Session Focus** sur cette base ;
4. seulement ensuite écrire **Today/Home** ;
5. puis **History/Progress** ;
6. puis **Portability** ;
7. puis **Rebrand Migration**.

C'est le chemin le plus propre parce qu'il suit la structure déjà amorcée par le produit au lieu de la nier.

## Pistes de nommage après Spignos

« Ratel » marche pour une raison simple : c'est court, mémorable, nerveux, dur, et ça sonne comme un outil. Son défaut, pour ta cible future, c'est que l'imaginaire animal/agressif tire un peu plus vers la ténacité brute que vers la précision clinique.

Je te conseille donc de garder deux familles de noms en tête :

**La famille « dur minimal »**, qui garde l'énergie de Ratel, mais avec une tonalité moins ferale.
**La famille « clinical performance »**, qui sonne plus biométrie, précision, système nerveux, lecture du corps.

Voici les meilleurs candidats que je te proposerais à ce stade, **sans prétendre à une disponibilité légale ou domaine garantie** :

| Nom | Pourquoi il fonctionne | Risque |
|---|---|---|
| **Teral** | très proche de l'énergie de Ratel, plus abstrait, plus marque que mot commun | peut paraître un peu froid |
| **Nerva** | évoque le système nerveux, la commande du corps, très « bio-performance » | déjà assez proche de racines médicales existantes |
| **Auren** | premium, propre, santé-tech, facile à prononcer en FR/EN | moins « dur » si tu veux garder une impression de puissance |
| **Silex** | minéral, précis, net, mémorisable | un peu plus « matière » que « corps » |
| **Teryn** | court, moderne, facilement brandable, neutre | plus artificiel, moins immédiatement signifiant |
| **Velor** | mouvement, élan, premium, mémorisable | peut rappeler des marques déjà proches phonétiquement |
| **Synor** | science, système, signal, sonne produit structuré | plus « tech startup » que « santé calme » |
| **Norel** | doux mais net, crédible pour une app santé/performance | moins distinctif que Teral ou Nerva |

Ma recommandation éditoriale serait la suivante :

- **si tu veux garder l'énergie de Ratel** : prends **Teral** ;
- **si tu veux accentuer le côté biohacking / physiologie / précision** : prends **Nerva** ;
- **si tu veux une marque plus premium, plus Apple Health que gym app** : prends **Auren**.

Mon trio final serait donc : **Teral**, **Nerva**, **Auren**.

Le plus aligné avec ton intention « application du futur, blanche, chirurgicale, physique avancée » est probablement **Nerva** si tu assumes le registre physiologique, ou **Teral** si tu veux garder une dureté mémorable sans tomber dans l'animal brut.

## Recommandation nette

La meilleure voie n'est pas de « révolutionner » le produit par une réécriture. La meilleure voie est de **faire converger le produit existant vers une identité de performance corporelle premium** en exploitant ce qu'il a déjà de plus fort : son exécution de séance mobile, sa base SSR robuste, son no-JS fallback, et sa discipline spec-driven.

Le chantier recommandé, dans l'ordre, est donc :

- figer la **marque** et la **direction visuelle** ;
- écrire la spec **tokens + shell** ;
- re-skinner le **focus mode séance** ;
- créer un **Today/Home** orienté readiness et décision ;
- réécrire l'**historique** en langage calme et clinique ;
- rendre l'app **installable** et plus native perçue ;
- seulement ensuite opérer le **rebrand** complet.

Si tu me demandes où commence vraiment la transformation, la réponse est simple : **pas par un nouveau logo, pas par un nouveau moteur, pas par React — mais par la première spec « Brand Foundation + Design Tokens + App Shell »**. C'est elle qui te donnera enfin une langue visuelle stable pour faire évoluer `workout-session-tracking` sans drift, sans casser la logique existante, et sans perdre ce qui fait déjà la valeur réelle du produit.
