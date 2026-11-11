# MOB-05A — relecture du contrat visuel

10 novembre 2026, avant commit UI. G1 et build acquis ; pixels acceptés : « Valider ces pixels MOB-05A contrôlés ».
Sources relues : DESIGN_DECISIONS_HOME_UIV2, DESIGN_DECISIONS_UIV2_SURFACES avec
leurs amendements mobiles, Visual Contract, UI Iteration Protocol, références
UX-CAL-02 et MOB-04. Le contrat mobile accepté gouverne les primitives courantes.

| Décision | Application dans cette tranche |
|---|---|
| D1 — contrôle/étiquette | Respectée via primitives natives acceptées ; sélection explicite, cibles48 extensibles, texte d'étiquette séparé. Les chevrons/rangs web restent référence historique. |
| D2 — origine honnête | Respectée : aucun label IA, recommandation ou permission scientifique produit depuis l'historique. |
| D3 — couleurs | Référence legacy amendée : tokens natifs existants exclusivement. Faits mesurés et saisies ne deviennent pas une recommandation bleue. |
| D4 — retraits | Non concernée pour les objets d'accueil verrouillés ; ancien placeholder Progrès remplacé dans la même livraison, fallback sans consommateur conservé. |
| D5 — descriptif vers visuel | Direction conservée : valeur/fréquence et points datés, aide repliée ; aucun asset ou donnée anatomique inventé. |
| D6 — cycle/récupération | Non concernée : aucune nouvelle programmation ou bande de récupération. Période de lecture historique n'est pas un cycle prescrit. |
| D7 — régularité | Fréquence factuelle du journal uniquement ; pas de streak, récompense, repos ou qualité inventés. |
| D8 — onglet Progression | Respectée : onglet existant, sessions/exercices/poids, aucun onglet ajouté. |
| D9 — anticipation | Respectée : aucun N+2, planning daté ou cible future déduit de la cadence. |
| Q1 — connexion | Non concernée, comptes/auth visuels inchangés. |
| Q2 — ancre accueil | Non concernée, MISSION et BodyMap verrouillés. |
| Q3 — état du jour | Non concernée et amendement de décommissionnement respecté ; aucun questionnaire ressenti nouveau. |
| Q4 — ligne instrument | Exécution verrouillée intacte. Le détail historique est une lecture de faits, pas une commande de série. |
| Q5 — surfaces | Référence legacy amendée : AccountFrame et primitives natives conservés, sans nouveau conteneur global. |
| Q6 — typographie | Référence legacy amendée : tokens natifs existants ; aucun durcissement de taille limitant les grandes fontes. |
| Q7 — action souveraine | Respectée : lecture seule, navigation subordonnée ; aucun CTA d'entraînement ou faux consentement. |
| Q8 — opacité | Référence legacy amendée : aucune opacité décorative nouvelle ; états disabled des primitives acceptées conservés. |

Les engrenages/Tools des captures appartiennent à Expo Go. Les références
acceptées sont copiées et empreintées, jamais régénérées. Les overlays et limites
de banc ne deviennent pas des éléments de la baseline AUREN. Aucune modification
de MISSION, compte, calibrage ou exécution, ni d'asset/logo/couleur globale.

Sources d'information : comptes/faits depuis GET propriétaires ; chronologie
BodyMeasurement sous accord applicable ; statut SCI via vrai lecteur V3 et
validateur historique ; échec transport/lecture précédente explicitement séparé.
Les regroupements de mouvement ne donnent aucune équivalence de kilogrammes.

Vérification contrôlée : iOS390 pt, Android360/480 dp, fonte130%, ordre AX des
faits et retours dans le vrai ConnectedApp iOS. Graphiques statiques sans mouvement
requis. TypeScript et tests de callbacks ne certifient pas TalkBack, VoiceOver,
geste, iOS320pt, clavier/retour sur appareil physique ou APK distribué.

Aucune décision marquée violée dans le périmètre présenté ; les deux mineurs de
clarté et limites de recette restent divulgués dans DELIVERY et le board.

## Delta final du11novembre — pixels acceptés

Même inventaire D1..D9/Q1..Q8 relu contre le raffinement. D1 : Retour et liens48dp ;
D2/D7 : faits et fréquence, aucune inférence ; D3/Q6 : tokens existants, titre
bodyStrong17/23 et NumericReadout canonique, agrandissement préservé ; D4/D5 :
prose remplacée par instrument numérique et sources accessibles dans même delta ;
D8/Q2/Q4 : tabs/MISSION/exécution intacts ; D6/D9/Q1/Q3 : non concernés. Q5 :
composition historique locale HistoricalFactsFrame et Frame C, aucun changement de
AccountFrame global ; Q7/Q8 : navigation seule et états de primitives conservés.
Pas de décision violée identifiée ; aucune baseline éditée. L'acceptation de ce
delta est distincte de l'ancien reçu : « Valider le delta final MOB-05A », reçue
le11novembre avant commit UI. Les22frames et15sources finales sont revérifiées.
