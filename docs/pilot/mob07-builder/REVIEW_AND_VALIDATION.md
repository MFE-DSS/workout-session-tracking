# MOB07 — vérification et décisions visuelles

15novembre2026. Parent f31b6e7 ; implémentation non committée. GO BUILD/amendement/G1 reçus ; pixels acceptés pour le pilote avec limites. Les références SVG rejetées ne sont pas une baseline. Les campagnes locales ne constituent ni CI de PR ni acceptation physique.

## Brainstorming / Options / Risques / Choix retenu

Le design et G1 autorisés conservent UserProgram, les identités canoniques et la famille DA08. Choix appliqué : un kernel CAS commun web/natif, une migration additive de reçus et un seul objet d’édition dans Programmes. Les risques de quota concurrent, anciennes pages web, perte de réponse, identité inconnue et reprise locale ont des témoins comportementaux. Aucun moteur scientifique ou programme actif/calendrier ajouté.

## Croquis de départ

UX_BOARD.md du change MOB07, accepté avec le GO propre call_dd254c785ba7430897ac13dc9b579cbc. Le constructeur prolonge la bibliothèque livrée : programme → séances ordonnées → mouvement sélectionné → séries/plages manuelles → sauvegarde/validation/publication. Le départ reste dans MOB06.

## Inventaire de redondance

Programme : titre/statut/version issus de la source propriétaire. Séquence : noms et ordre des séances, nécessaires à la sélection ; l’instrument porte l’objet courant. Nombre de séries et chaque plage sont déclarés, sans défaut numérique. Le nom résolu actuellement ne devient pas preuve d’identité historique. La commande inconnue et la source possédée peuvent coexister ; seule la réception du reçu exact clôt la commande. Le board8290 inventorie les sources de chaque module.

## Comparaison avec la référence validée

Board8290 : captures MOB06/DA08 acceptées intactes, puis vrai ConnectedApp iOS et petit delta SSR. Aucun changement Frame C, RecessedWindow, NumericReadout, MISSION, shell D4 ou baseline. La source réutilise InstrumentSurface, EmbeddedAction, CalibrationLink/Choices, marque et tokens existants. Android complet/physique non acceptés ; les limites de Host, clavier/focus et grands textes sont exposées.

## Delta unique

Ajouter le constructeur autorisé dans la bibliothèque existante. Les correctifs de revue sont fonctionnels dans ce même scope ; aucune nouvelle variante de direction artistique. Décision opérateur : **« Accepter pour le pilote, avec les limites indiquées »**, call_8c8924d28fa04247b1cfb692f2868145, avant commit UI. Android et physique restent non acceptés ; limites de focus/insets/gestes conservées.

## Relecture CLAUDE§5.2, avant tout commit UI

Registres DESIGN_DECISIONS_HOME_UIV2 et DESIGN_DECISIONS_UIV2_SURFACES relus en entier, amendements mobiles compris.

| Décision | Statut | Application au delta |
|---|---|---|
| HOME D1 | Respectée dans sa sémantique native | Étiquettes/commandes séparées ; cibles48dp, composants DA08. Anciens rangs web inchangés. |
| HOME D2 | Respectée | Aucun badge Recommandé IA ou moteur nouveau. |
| HOME D3 | Référence legacy ; tokens natifs respectés | Signal local sur action ; pas de bleu décoratif. |
| HOME D4 | Non concernée | Aucun retrait de l’accueil web. |
| HOME D5 | Direction respectée, géométrie legacy | Structure de programme réelle ; aucun asset biologique ajouté. |
| HOME D6 | Non concernée / frontière conservée | Aucun calcul de récupération. Ordre de séances déclaré, aucun calendrier déduit. |
| HOME D7 | Non concernée | Aucun streak/fréquence/qualité inventés. |
| HOME D8 | Respectée | Onglet Progrès livré conservé, aucune cinquième tab. |
| HOME D9 | Respectée | Programme personnel consultable ≠ recommandation anticipée N+2. |
| SURFACES Q1 | Non concernée | Authentification et login inchangés. |
| SURFACES Q2 | Non concernée / NOT_SERVED conservé | Aucune barre de récupération sans admission SCI spécifique. |
| SURFACES Q3 et amendement | Respectée | Aucun état du jour1–5 réintroduit. |
| SURFACES Q4 et amendement | Sémantique respectée | Valeurs manuelles et état explicite ; aucune ligne d’exécution ni glyphes E/S modifiés. |
| SURFACES Q5 | Référence legacy pour mobile | Pas de carte universelle nouvelle ; instrument DA08 actif et contexte secondaire. Templates web gardent leur grammaire. |
| SURFACES Q6 | Référence legacy pour mobile | Rôles type existants, pas de nouveau rôle global ou changement de font verrouillée. |
| SURFACES Q7 | Principe respecté | Une commande d’enregistrement souveraine dans l’état actif ; confirmations distinctes. |
| SURFACES Q8 | Référence legacy ; composants natifs acceptés | Aucune nouvelle couleur/opacité globale ; états désactivés existants réutilisés. |
| Tokens bleus | Respectés | Aucun nouveau token ni repli hex ; pas de nouvelle origine scientifique. |
| Convergence / ordre ancien | Non concerné | Pas de refonte Accueil ou login. L’ordre MVP autorisé est conservé. |

## Vérifications réalisées et limites

127suites/1448tests mobiles+TypeScript passent après les corrections ; kernel/API/SSR/caps ont des campagnes ciblées/broad conservées dans BACKEND_LEDGER.md. Revue indépendante3Important puis revue bornée des correctifs : tous résolus, aucun nouveau finding démontré. Ruff neuf/budget, migration patterns/roundtrip et OpenSpec28/28 passent ; Gitleaks0 et Bandit nouveaux modules0. Visuel obligatoire77PASS ; HTTP/inventaire sous FastAPI/Starlette du lock24PASS et relecture historique HTTP réelle complètent les preuves. Revue supplémentaire des pins QA sans finding. Sweep MIGRATION terminé :454fichiers/114lots,8764PASS/1ignoré, sortie0, pic2763MiB sous3000. Après ce passage, le seul delta tardif JSON/test du modèle PREPARE actif a son RED→GREEN et270tests QA rejoués. Aucun code produit modifié après le sweep ; CI distante à compléter. Aucun Sonar de MOB07 ni PASS CI inventé.

Preuves durables privées : /Users/martinfeldmann/auren-review/mob07-implementation-20261115/. Paquet public de captures sans identifiants : MOB07_NATIVE_PIXEL_REVIEW.zip, SHA256940cacbcbeeca5f4991d678b2216496fc6bb0a0869f1f71265f335b6e4ea3cbe. Les identifiants synthétiques restent hors Git/paquet.

## Suivi après publication

Le relevé ci-dessus conserve son instant avant commit. HEAD c614241123eae018df4b7c4d3a176bdc9091c38e puis PR414 fusionnée dbad35d4634442e985b2964ff85fad6254efae74 ; CI PR43750397616 success,11jobs,8755backend/3ignorés,1448mobiles+TypeScript et77visuels. Le [closeout](CLOSEOUT.md) consigne Sonar réel, suivi canonique, préparation non distribuable et conservation. Aucune acceptation Android ou release n’en découle.
