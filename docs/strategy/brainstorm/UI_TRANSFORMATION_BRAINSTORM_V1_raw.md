---
name: UI_TRANSFORMATION_BRAINSTORM_V1_raw
type: brainstorm-archive-raw
source: session brainstorm produit (opérateur, 2026-07-02)
status: READ-ONLY BRAINSTORM ARCHIVE — do not amend
encoding_status: mojibake preserved verbatim
normalized_version: UI_TRANSFORMATION_BRAINSTORM_V1_normalized.md
---

> **Note d'archivage :** ce fichier préserve le texte source tel que livré par l'opérateur, y compris les artefacts d'encodage (mojibake UTF-8 double, marqueurs `îfileciteî...î` d'origine LLM). Pour une version lisible, voir `UI_TRANSFORMATION_BRAINSTORM_V1_normalized.md`. Pour la synthèse actionnable, voir `../UI_TRANSFORMATION_ROADMAP.md`.

---

# Cadre de transformation de Spignos vers une application mobile minimaliste de performance

## Point de dÃ©part du produit

Le bon diagnostic nâest pas âfaire une refonte cosmÃ©tiqueâ, mais ârÃ©aligner le produit avec sa vraie promesseâ. DâaprÃ¨s les documents techniques dÃ©jÃ  prÃ©sents dans ton flux, ton application nâest pas un proto fragile : elle a dÃ©jÃ  une base SSR FastAPI + Jinja, un mode sÃ©ance mobile dÃ©diÃ©, une feuille de style `session_focus.css` extraite, un fallback no-JS prÃ©servÃ©, et une discipline de livraison par specs, rapports et closure docs. Autrement dit, tu as dÃ©jÃ  lâossature dâun produit sÃ©rieux ; ce quâil manque, câest une grammaire visuelle et informationnelle cohÃ©rente Ã  lâÃ©chelle du produit. îfileciteîturn195file0îL66-L85î îfileciteîturn194file0îL13-L55î

Le point fort actuel nâest pas un âdashboard intelligentâ, mais lâexÃ©cution de sÃ©ance. Les extraits dÃ©jÃ  livrÃ©s montrent que `session_detail` a Ã©tÃ© dÃ©coupÃ© en partials ciblÃ©s, avec un header de focus, une carte dâexercice dÃ©diÃ©e et un timer de repos sÃ©parÃ©. Le template dogfood Sx_29 insiste dâailleurs sur ce qui doit Ãªtre testÃ© en rÃ©el : header sticky, jump bar, carte active, sticky CTA, timer et frictions de logging sur mobile. Cela indique oÃ¹ est la valeur produit la plus tangible aujourdâhui : la sÃ©ance en cours, pas lâhabillage âcockpitâ. îfileciteîturn173file0îL3-L31î îfileciteîturn174file0îL3-L45î îfileciteîturn196file0îL22-L69î

Le commentaire design le plus important est donc celui-ci : **ne dÃ©truis pas lâhonnÃªtetÃ© fonctionnelle du produit en cherchant un âlook premiumâ trop tÃ´t**. Strong et Hevy se positionnent eux-mÃªmes sur la simplicitÃ© radicale du logging ; Strong revendique âthe simplest interfaceâ, et Hevy insiste sur un tracker âsimpleâ et âintuitiveâ. Cette logique est cohÃ©rente avec ce que ton produit a dÃ©jÃ  commencÃ© Ã  faire techniquement. îciteîturn1search5îturn1search8îturn1search13î

## Ce que le produit doit devenir

Ta cible nâest pas un Ã©niÃ¨me tracker de musculation noir, saturÃ©, âhardcore gym broâ. Ta cible est plus rare : **un outil de performance corporelle calme, clinique, mobile-first, end-to-end**, oÃ¹ la musculation reste le cÅur, mais oÃ¹ la prÃ©sentation sâinspire davantage des apps de biomÃ©trie et de santÃ© avancÃ©e que des apps de salle classiques. Apple Health se prÃ©sente comme un lieu central et sÃ©curisÃ© pour les donnÃ©es de santÃ© avec tendances et graphiques interactifs ; Levels parle de comprendre lâeffet de lâalimentation, du sommeil, de lâexercice et du stress ; Ultrahuman dâun dashboard unifiÃ© de santÃ© ; WHOOP structure lâexpÃ©rience autour dâun score de rÃ©cupÃ©ration ; Oura met en avant plus de trente biomÃ©triques et une lecture approfondie du sommeil et de lâactivitÃ©. îciteîturn2search2îturn2search5îturn2search18îturn1search7îturn1search15î

La bonne transformation consiste donc Ã  dÃ©placer le centre de gravitÃ© perceptif du produit. Aujourdâhui, âSpignosâ peut Ãªtre perÃ§u comme un cockpit de tracking. Demain, lâapplication doit donner lâimpression dâun **instrument de pilotage physiologique**, mÃªme quand elle parle simplement de sÃ©ries, reps et charges. Cela veut dire : moins de chrome visuel, moins dâÃ©lÃ©ments en concurrence, plus dâunitÃ©s lisibles, plus de hiÃ©rarchie typographique, plus de calme, et des surfaces qui ressemblent Ã  de lâinstrumentation de santÃ© plutÃ´t quâÃ  un tableau de bord de gamer. Cette direction est compatible avec les recommandations Apple et Material, qui ancrent la qualitÃ© perÃ§ue dans la hiÃ©rarchie, la couleur comme signal, et lâusage disciplinÃ© des composants, pas dans la dÃ©coration. îciteîturn2search3îturn2search11îturn2search8îturn2search4îturn2search7î

En clair, ton produit doit converger vers cette formule :

| Axe | Position actuelle utile | Position cible |
|---|---|---|
| Fonction | tracker de sÃ©ance robuste | systÃ¨me de performance corporelle |
| Ton | technique / geek / cockpit | clinique / prÃ©cis / calme |
| Mobile | dÃ©jÃ  bien engagÃ© sur la sÃ©ance | shell mobile natif perÃ§u partout |
| EsthÃ©tique | utilitaire fragmentÃ©e | biomÃ©trie blanche, chirurgicale, sobre |
| Valeur primaire | logger correctement | dÃ©cider et exÃ©cuter la bonne sÃ©ance, au bon rythme |

Cette cible ne demande pas de changer ton moteur avant tout ; elle demande de **changer le langage de surface**.

## Benchmarks Ã  copier et Ã  Ã©viter

Le benchmark ne doit pas Ãªtre monolithique. Il faut sÃ©parer le benchmark **fonctionnel de strength tracking** du benchmark **esthÃ©tique de santÃ©-tech**.

| RÃ©fÃ©rence | Ce quâil faut voler | Ce quâil faut Ã©viter |
|---|---|---|
| Strong | obsession de la simplicitÃ©, rest timer intÃ©grÃ©, stats avancÃ©es sans bloquer le logging, logique progressive barbell | look trop âoutil de logâ si tu veux une identitÃ© plus premium santÃ©-tech îciteîturn1search1îturn1search5îturn1search9î |
| Hevy | clartÃ© des flows, progression par mÃ©triques, planification + log + stats au mÃªme endroit | dimension communautaire/sociale si ce nâest pas ton diffÃ©renciateur îciteîturn1search0îturn1search4îturn1search12î |
| Fitbod | promesse dâadaptation intelligente, personnalisation orientÃ©e progression, lien direct entre algorithme et sÃ©ance | dÃ©pendance Ã  une promesse âAI trainerâ trop forte si lâexpÃ©rience de base nâest pas encore minimaliste îciteîturn1search2îturn1search6îturn1search10î |
| Apple Health | centralisation calme, lisibilitÃ©, sentiment de fiabilitÃ©, tendance plutÃ´t que bruit | neutralitÃ© trop gÃ©nÃ©rique si tu perds lâintensitÃ© performance/strength îciteîturn2search2îturn2search19îturn2search24î |
| Levels | cadrage physiologique, explication personnalisÃ©e, pÃ©dagogie sans folklore | narration trop âmÃ©taboliqueâ si tu oublies la musculation comme acte central îciteîturn2search5îturn2search9îturn2search17î |
| Ultrahuman | dashboard unifiÃ©, scores actionnables, posture âperformance labâ | risque de sur-abstraction si la sÃ©ance rÃ©elle devient secondaire îciteîturn2search1îturn2search10îturn2search18î |
| WHOOP | score de readiness/rÃ©cupÃ©ration, framing âwhat should I do today?â | dÃ©pendance au wearable, surcharge de mÃ©triques dÃ©rivÃ©es si le service ne les alimente pas encore îciteîturn1search7îturn1search11îturn1search16î |
| Oura | biomÃ©trie crÃ©dible, luxe calme, lecture profonde mais accessible | glissement trop wellness / lifestyle si tu veux rester strength-first îciteîturn1search15îturn1news43î |

Le benchmark template doit suivre la mÃªme logique. Pour la structure mobile et la discipline visuelle, tes meilleures bases sont les ressources officielles Apple et Material. Apple fournit des design resources officielles pour Figma et Sketch ; Material fournit son kit Figma M3 et une grammaire de composants complÃ¨te. En revanche, les kits comme Untitled UI ou shadcn/ui sont excellents pour lâinspiration web, mais ils sont pensÃ©s autour de Figma web et, cÃ´tÃ© implÃ©mentation, de React/Tailwind. Dans ton cas, oÃ¹ la base existante est SSR/Jinja et oÃ¹ React est explicitement absent, les prendre comme code source augmenterait le drift. Il faut les utiliser au mieux comme galerie dâarchitecture visuelle, pas comme solution dâimplÃ©mentation. îciteîturn6search0îturn6search21îturn6search3îturn6search7î îfileciteîturn195file0îL66-L85î

Le commentaire design central ici est simple : **copie la discipline dâApple et Material ; copie la clartÃ© fonctionnelle de Strong/Hevy ; copie le framing physiologique de Levels/WHOOP/Oura ; ne copie pas leur stack, ni leur marketing, ni leurs gimmicks**. îciteîturn2search7îturn7search1îturn1search5îturn2search5îturn1search7î

## Direction visuelle et UX cible

La cible visuelle peut se rÃ©sumer ainsi : **fond blanc cassÃ©, composants blancs francs, texte presque noir, un seul accent froid, beaucoup dâair, peu dâombre, pas de gros visuels, pas de textures, pas de gradients âIAâ**. Cette direction nâest pas en contradiction avec les guidelines de plateforme ; Apple insiste sur une hiÃ©rarchie lisible, une typographie structurÃ©e et des couleurs systÃ¨me adaptÃ©es Ã  lâaccessibilitÃ©, tandis que Material structure aussi lâinterface par rÃ´les de couleur et de typographie, plutÃ´t que par surcharge dÃ©corative. îciteîturn2search3îturn2search11îturn2search8îturn2search4î

En pratique, je recommande ce langage :

- **Surfaces** : blanc pur, gris trÃ¨s lÃ©ger, sÃ©parations fines.
- **Accent** : un turquoise froid ou un bleu minÃ©ral unique, rÃ©servÃ© aux Ã©tats actifs, scores favorables et CTA principaux.
- **Typographie** : trÃ¨s peu de tailles, mais une hiÃ©rarchie nette ; grands titres sobres, labels courts, unitÃ©s explicites.
- **IcÃ´nes** : trait simple, sans remplissages lourds.
- **Charts** : fins, utiles, jamais hÃ©roÃ¯ques.
- **Motion** : trÃ¨s discrÃ¨te, jamais nÃ©cessaire pour comprendre lâÃ©cran.
- **Illustration** : quasi absente.

CÃ´tÃ© UX, la rÃ¨gle qui doit tout gouverner est la suivante : **une dÃ©cision principale par Ã©cran, une profondeur dâattention par moment**. NN/g dÃ©crit la progressive disclosure comme le fait de repousser les Ã©lÃ©ments avancÃ©s vers une couche secondaire pour rÃ©duire lâerreur et la complexitÃ© perÃ§ue. Câest exactement ce quâil faut faire ici : pendant la sÃ©ance, lâutilisateur nâa pas besoin dâun laboratoire entier ; il a besoin de savoir quoi faire maintenant, avec juste assez de contexte pour Ãªtre confiant. îciteîturn3search1îturn3search6î

La navigation doit suivre cette discipline. Apple rappelle quâune tab bar sert Ã  naviguer entre sections, pas Ã  lancer des actions, et Material dit la mÃªme chose pour la navigation bar, alors que lâaction principale doit Ãªtre reprÃ©sentÃ©e sÃ©parÃ©ment. Ã lâÃ©chelle de ton produit, cela veut dire : **la bottom nav sert Ã  aller de Aujourdâhui Ã  Historique Ã  Profil/Settings ; le logging de sÃ©ance reste un CTA contextuel dans la surface de contenu**, Ã  la maniÃ¨re de ton sticky CTA dÃ©jÃ  livrÃ© dans le focus mode. îciteîturn3search3îturn7search11îturn7search2î îfileciteîturn196file0îL22-L69î

Enfin, il faut garder comme contrainte dure le confort mobile. WCAG 2.2 formalise une taille minimale de cible de 44 Ã 44 CSS pixels pour rÃ©duire les activations accidentelles. Comme ton produit a dÃ©jÃ  commencÃ© Ã  intÃ©grer cette logique dans Sx_29, il faut la hisser au rang de principe global, pas de dÃ©tail local. îciteîturn3search2îturn3search7î îfileciteîturn194file0îL13-L43î

## Chantiers de transformation sans casser le produit

La bascule la plus sÃ»re nâest pas une refonte âbig bangâ. Câest une **migration par couches**. Ton avantage, câest que le produit est dÃ©jÃ  organisÃ© par specs et par surfaces. Il faut donc faire une convergence visuelle **sans toucher Ã  la logique mÃ©tier**, puis remapper progressivement les Ã©crans les plus critiques. La prÃ©sence dâun `session_focus.css` dÃ©diÃ©, chargÃ© aprÃ¨s `app.css`, est un trÃ¨s bon point de dÃ©part pour une Ã©volution pilotÃ©e par tokens et par route. îfileciteîturn194file0îL45-L55î

Je te recommande cet ordre de chantiers :

| Chantier | Pourquoi câest le bon ordre | Ce quâil ne faut pas faire |
|---|---|---|
| Fondation visuelle | fixe la grammaire avant de repeindre les Ã©crans | commencer par des maquettes spectaculaires sans tokens ni rÃ¨gles |
| App shell mobile | donne immÃ©diatement un sentiment âappâ cohÃ©rent | refaire toute lâIA en mÃªme temps |
| Re-skin sÃ©ance active | câest dÃ©jÃ  le point le plus fort du produit et le plus proche dâun usage rÃ©el | repartir dâune page blanche alors que le focus mode existe dÃ©jÃ  |
| Home/Today | permet de traduire le produit en langage âreadiness / next best sessionâ | y entasser toutes les analytics |
| Historique / progression | convertit la donnÃ©e accumulÃ©e en lecture plus calme et premium | faire des dashboards lourds |
| PortabilitÃ© | rend lâapp installable et plus native perÃ§ue avec le code existant | lancer une rÃ©Ã©criture native ou SPA maintenant |
| Rebrand | ne vient quâune fois le langage du produit suffisamment stabilisÃ© | changer de nom avant dâavoir stabilisÃ© le shell et les Ã©crans clÃ©s |

Pour la portabilitÃ©, la bonne trajectoire nâest pas âReact Nativeâ, ni âSPA obligatoireâ. MDN dÃ©finit les PWA comme des applications construites avec les technologies web capables dâoffrir une expÃ©rience proche du natif depuis un codebase unique ; web.dev rappelle quâune architecture SPA augmente la complexitÃ© et le coÃ»t initial de chargement. Comme ton produit part dÃ©jÃ  dâun SSR propre avec no-JS fallback, la meilleure stratÃ©gie est : **app web installable dâabord, native plus tard seulement si lâusage le justifie**. Safari sur iPhone permet dÃ©jÃ  dâajouter un site Ã  lâÃ©cran dâaccueil et de lâouvrir comme une web app. îciteîturn5search1îturn5search16îturn5search6î îfileciteîturn195file0îL66-L85î

Le commentaire produit le plus stratÃ©gique est donc celui-ci : **la âmise Ã  lâÃ©chelleâ doit dâabord signifier cohÃ©rence visuelle, navigation propre, installation facile et robustesse mobile â pas changement de stack**. îciteîturn5search1îturn5search5îturn5search10î

## Corpus de specs Ã  Ã©crire en premier

Si tu veux rester en mode spec-driven avec ton code superpower sans drift, il faut Ã©viter les specs âfourre-toutâ. Chaque spec doit porter une surface, une intention, des protections, et un mode de vÃ©rification. Voici le corpus que je te recommande dâÃ©crire avant tout gros chantier UI.

| Spec | Objet | Pourquoi elle doit exister |
|---|---|---|
| **Sx_UI_01 Brand Foundation Spec** | nom de marque, tone of voice, slogan court, principes visuels interdits/autorisÃ©s | Ã©vite que le chantier UI dÃ©rive en patchwork |
| **Sx_UI_02 Design Tokens Spec** | palettes, surfaces, typo, rayons, bordures, ombres, espacements, Ã©tats, chart tokens | permet de repeindre sans rÃ©inventer Ã©cran par Ã©cran |
| **Sx_UI_03 App Shell and Navigation Spec** | top bar, bottom nav, titres, actions globales, safe areas, breadcrumb de contexte | fixe la structure app-like et Ã©vite les Ã©crans orphelins |
| **Sx_UI_04 Session Focus Reskin Spec** | refonte visuelle du flow sÃ©ance dÃ©jÃ  livrÃ©, sans changer le moteur | capitalise sur le meilleur usage actuel |
| **Sx_UI_05 Today and Readiness Home Spec** | Ã©cran dâentrÃ©e orientÃ© âquoi faire aujourdâhuiâ | traduit le produit en systÃ¨me de performance plutÃ´t quâen archive |
| **Sx_UI_06 Exercise Intelligence Presentation Spec** | comment prÃ©senter recommandation, surcharge, historique rÃ©cent, explainer | Ã©vite que lâintelligence produit soit cachÃ©e ou trop bavarde |
| **Sx_UI_07 History and Progress Spec** | historique, tendances, PR, volume, cycles, comparaisons | transforme la data en lecture premium et utile |
| **Sx_UI_08 Portability and Installability Spec** | manifest, icÃ´ne, install prompt, cache minimal, mode offline utile | fait passer lâapp de âsiteâ Ã  âoutil transportableâ |
| **Sx_UI_09 Accessibility and Motion Spec** | contrastes, cible tactile, focus, reduced motion, aria, comportement no-JS | empÃªche la dette UX silencieuse |
| **Sx_UI_10 Rebrand Migration Spec** | mapping Spignos â nouveau nom, copy, assets, slug, compat, Ã©cran de transition | permet de renommer sans casser la reconnaissance ni lâexistant |
| **Sx_UI_11 Screenshot Regression Spec** | golden screens, viewport mobile/desktop, critÃ¨res de non-rÃ©gression visuelle | protÃ¨ge contre le drift pendant les sprints |

La rÃ¨gle dâor pour ces specs est la suivante : **une spec de surface ne touche pas Ã  la logique mÃ©tier**. Si tu modifies lâalgorithme et le visuel dans le mÃªme sprint, tu perds immÃ©diatement ta capacitÃ© Ã  diagnostiquer les rÃ©gressions. Ce principe est particuliÃ¨rement important dans ton repo, justement parce quâil a dÃ©jÃ  une culture de protection des services core et de livraisons fermÃ©es par closure report. îfileciteîturn195file0îL66-L85î

Le chantier recommandÃ© pour basculer proprement serait donc :

1. Ã©crire **Brand Foundation** et **Design Tokens** ;
2. Ã©crire **App Shell** ;
3. re-skinner **Session Focus** sur cette base ;
4. seulement ensuite Ã©crire **Today/Home** ;
5. puis **History/Progress** ;
6. puis **Portability** ;
7. puis **Rebrand Migration**.

Câest le chemin le plus propre parce quâil suit la structure dÃ©jÃ  amorcÃ©e par le produit au lieu de la nier. îfileciteîturn173file0îL3-L31î îfileciteîturn174file0îL3-L45î îfileciteîturn194file0îL45-L55î

## Pistes de nommage aprÃ¨s Spignos

âRatelâ marche pour une raison simple : câest court, mÃ©morable, nerveux, dur, et Ã§a sonne comme un outil. Son dÃ©faut, pour ta cible future, câest que lâimaginaire animal/agressif tire un peu plus vers la tÃ©nacitÃ© brute que vers la prÃ©cision clinique.

Je te conseille donc de garder deux familles de noms en tÃªte :

**La famille âdur minimalâ**, qui garde lâÃ©nergie de Ratel, mais avec une tonalitÃ© moins ferale.
**La famille âclinical performanceâ**, qui sonne plus biomÃ©trie, prÃ©cision, systÃ¨me nerveux, lecture du corps.

Voici les meilleurs candidats que je te proposerais Ã  ce stade, **sans prÃ©tendre Ã  une disponibilitÃ© lÃ©gale ou domaine garantie** :

| Nom | Pourquoi il fonctionne | Risque |
|---|---|---|
| **Teral** | trÃ¨s proche de lâÃ©nergie de Ratel, plus abstrait, plus marque que mot commun | peut paraÃ®tre un peu froid |
| **Nerva** | Ã©voque le systÃ¨me nerveux, la commande du corps, trÃ¨s âbio-performanceâ | dÃ©jÃ  assez proche de racines mÃ©dicales existantes |
| **Auren** | premium, propre, santÃ©-tech, facile Ã  prononcer en FR/EN | moins âdurâ si tu veux garder une impression de puissance |
| **Silex** | minÃ©ral, prÃ©cis, net, mÃ©morisable | un peu plus âmatiÃ¨reâ que âcorpsâ |
| **Teryn** | court, moderne, facilement brandable, neutre | plus artificiel, moins immÃ©diatement signifiant |
| **Velor** | mouvement, Ã©lan, premium, mÃ©morisable | peut rappeler des marques dÃ©jÃ  proches phonÃ©tiquement |
| **Synor** | science, systÃ¨me, signal, sonne produit structurÃ© | plus âtech startupâ que âsantÃ© calmeâ |
| **Norel** | doux mais net, crÃ©dible pour une app santÃ©/performance | moins distinctif que Teral ou Nerva |

Ma recommandation Ã©ditoriale serait la suivante :

- **si tu veux garder lâÃ©nergie de Ratel** : prends **Teral** ;
- **si tu veux accentuer le cÃ´tÃ© biohacking / physiologie / prÃ©cision** : prends **Nerva** ;
- **si tu veux une marque plus premium, plus Apple Health que gym app** : prends **Auren**.

Mon trio final serait donc : **Teral**, **Nerva**, **Auren**.

Le plus alignÃ© avec ton intention âapplication du futur, blanche, chirurgicale, physique avancÃ©eâ est probablement **Nerva** si tu assumes le registre physiologique, ou **Teral** si tu veux garder une duretÃ© mÃ©morable sans tomber dans lâanimal brut.

## Recommandation nette

La meilleure voie nâest pas de ârÃ©volutionnerâ le produit par une rÃ©Ã©criture. La meilleure voie est de **faire converger le produit existant vers une identitÃ© de performance corporelle premium** en exploitant ce quâil a dÃ©jÃ  de plus fort : son exÃ©cution de sÃ©ance mobile, sa base SSR robuste, son no-JS fallback, et sa discipline spec-driven. îfileciteîturn195file0îL66-L85î îfileciteîturn194file0îL13-L55î

Le chantier recommandÃ©, dans lâordre, est donc :

- figer la **marque** et la **direction visuelle** ;
- Ã©crire la spec **tokens + shell** ;
- re-skinner le **focus mode sÃ©ance** ;
- crÃ©er un **Today/Home** orientÃ© readiness et dÃ©cision ;
- rÃ©Ã©crire lâ**historique** en langage calme et clinique ;
- rendre lâapp **installable** et plus native perÃ§ue ;
- seulement ensuite opÃ©rer le **rebrand** complet.

Si tu me demandes oÃ¹ commence vraiment la transformation, la rÃ©ponse est simple : **pas par un nouveau logo, pas par un nouveau moteur, pas par React â mais par la premiÃ¨re spec âBrand Foundation + Design Tokens + App Shellâ**. Câest elle qui te donnera enfin une langue visuelle stable pour faire Ã©voluer `workout-session-tracking` sans drift, sans casser la logique existante, et sans perdre ce qui fait dÃ©jÃ  la valeur rÃ©elle du produit.
