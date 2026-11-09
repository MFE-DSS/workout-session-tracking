# UX-CAL-02 — instrument natif compact, revue des pixels

9 novembre 2026. **IMPLEMENTED / PIXELS_ACCEPTED / DELIVERY_IN_PROGRESS / NOT_ACTIVATED.**
Base initiale fe9f6e9, réconciliée par avance rapide au canonique844cbfb ; ses
seules différences sont documentaires. GO BUILD et G1 reçus explicitement :
« Autoriser le build UX-CAL-02 et valider G1 ». Cette décision ne vaut pas
acceptation des nouveaux pixels ou permission de déploiement.

## Brainstorming / Options / Risques / Choix retenu

La compacité globale aurait affecté des surfaces verrouillées ; sept écrans
indépendants auraient dupliqué le comportement. Choix autorisé : contrôles
locaux, même instrument et mêmes mutations, détails progressifs et deux volets
du même brouillon. Décodage croisé et aide applicable sont des changements
fonctionnels testés séparément. Aucun moteur, inventaire SCI, migration, asset,
dépendance, couleur ou composant global ajouté/modifié.

## Croquis validé

[Design](../../../openspec/changes/ux-cal-02-native-density/design.md),
[scope](../../../openspec/changes/ux-cal-02-native-density/BUILD_SCOPE.md),
[croquis G1](../../../openspec/changes/ux-cal-02-native-density/UX_CAL_BOARD.md)
et [autorisation](../../../openspec/changes/ux-cal-02-native-density/BUILD_AUTHORIZATION.md).
Les mentions PROPOSED/G1_PENDING des premières pièces décrivent leur instant
initial ; l'autorisation reçue les complète, sans réécrire l'histoire.

## Inventaire — une information, une seule fois

| Élément visible | Source et frontière |
|---|---|
| Étape / volet | État UI local, pas décision scientifique |
| Mouvement, appareil, lieu | Profil recoupé et contexte propriétaire courant |
| Valeur / unité | Choix saisi, fait utilisé ou observation selon étape ; MACHINE_DISPLAY_KG et PER_IMPLEMENT distincts |
| Statut / permission | Résultat et actions serveur ; aucun positif recomputé par UI |
| Faits après essai | Brouillon sans défaut positif, même événement réel, occurrence explicite |
| Reprise / attente | Journal local, reçu exact et réponse possédée, pas succès déduit |
| Aide | Source/protocole hashés, blocs communs + réalisation + arrêt, jamais permission |

Entrée/reprise, choix, contexte, préparation, réglage, familiarisation, essai,
observation, décision et états de lecture utilisent le consommateur existant.
Proposition, accord temporel, MISSION et exécution restent hors recomposition.

## Comparaison avec la référence validée

Board contrôlé : http://127.0.0.1:8134/ . Références UX-CAL-01 copiées octet
pour octet ; paires nouvelles obtenues en rendant le code accepté et le nouveau
code avec les mêmes cas. Aucune baseline modifiée. Empreintes, sources et
receipts natifs conservés dans
`/private/tmp/auren-ux-cal-02-review-evidence/PIXELS_SUBMISSION_RECEIPT.json`.

Mesure sur PNG Android360dp/densité3 : remplissage du CTA d'entrée68→48dp,
−29,4%. À l'étape réglage machine, le CTA devient visible dans le premier écran
alors qu'il était sous la ligne de flottaison. Ce sont des mesures de ces cas
à fonte normale, pas une hauteur fixe promise aux grandes fontes.

Rendus iOS26.3/390pt et AndroidAPI36/360–480dp. Grandes fontes observées :
Android1,3× et2×, iOS1,353× et2,143×. Les contrôles croissent et le défilement
reste nécessaire. Arbre AX iOS observé : champ réglage/unité, actions, aide.
Le formulaire du second volet contient un brouillon synthétique explicitement
pré-saisi ; aucune observation n'est envoyée par cette mise en scène.

Les étapes détaillées réutilisent le présentateur de production et les vrais
contrôleurs/lectures HTTP dans un banc privé. Entrée/reprise rend le vrai
PlanV3FirstUseScreen. L'overlay Expo et le pied de revue sont identifiés comme
outils du banc. Ce n'est pas un binaire autonome ni une recette physique.
L'app ConnectedApp Android complète ne démarre pas dans cet hôte Expo Go
(module ExpoTopicSubscriptionModule absent) ; aucun module n'a été retiré pour
masquer ce blocage. CUA perd la fenêtre Simulator lors de la tentative de saisie :
clavier natif réussi, VoiceOver/TalkBack complets et retour matériel Android
ne sont pas prétendus validés. Aucun contrôle n'a été effectué sur l'iPhone
physique. Aucun mouvement animé nouveau ; modal d'aide statique, réglage OS
réduire les animations non recetté physiquement.

## Changement unique de l'itération

Même système partagé, hiérarchie et densité locales révisées sous G1. Le réglage
et son unité ont un porteur unique ; les explications secondaires et l'historique
sont accessibles à la demande. Les faits, UNKNOWN, l'arrêt et l'acceptation
explicite restent distincts. La cible tactile minimale48 et la fenêtre minimale112
sont extensibles avec la fonte. Aucun incrément ou rail E7 inventé.

## Vérifications et revues réellement effectuées

- Task1 : broad24suites/363tests et TypeScript passants après correction des
  liaisons setting/context/épisode/pilote ; relecture ciblée13tests passants.
- Task2 : broad25suites/376tests passants avant les dernières corrections ;
  navigation/focus ensuite vérifiés sur2suites/32tests + TypeScript.
- Le rendu natif a révélé le champ observationSection undefined dans l'autosave
  strict : deux témoins RED avec vrai contrôleur/journal, puis2suites/34tests
  et TypeScript passants. Champ absent omis, jsonCopy inchangé. Captures après
  reprises sur cet état ; aucun faux broad final376/376 n'est déduit des reruns.
- DTO réels des sept rencontres du serveur contrôlé acceptés par les nouveaux
  décodeurs. Le vrai parcours HTTP synthétique acquiert sept épisodes, produit
  V3 incertain, refuse l'ack altéré, accepte l'ack exact puis retrouve la même
  séance7exercices/14séries et journal PER_IMPLEMENT. Ce n'est pas un parcours
  humain natif de sept essais ; backend inchangé, sources/faits de test étiquetés.
- Scope ISOLATED, protocole/budget260≤548 et diff-check passants ; aucun nouveau
  Python et aucun full sweep backend local. OpenSpec strict19/19 après mise à
  jour de base documentaire. CI du futur commit UI reste à exécuter.
- Revues indépendantes Task1/Task2 et globale : corrections exigées traitées
  avec RED→GREEN et relectures ciblées ; dernier correctif natif ADDRESSED/PASS.
  Les revues ne remplacent pas l'acceptation humaine des pixels.

## Décisions et coûts conservés

- Exécuter sous GO/G1 existants sans re-question de plan/merge : coût si erroné,
  rework visible dans le scope ; aucune activation déduite.
- Conserver le diff UI sans commit jusqu'aux pixels : coût, travail local et
  preuves à préserver ; les notes SDD sont conservées hors worktree avant cleanup.
- Réconcilier uniquement les documents canoniques avant livraison : code du
  runtime et sources SCI identiques ; aucune nouvelle autorité implicite.
- Limiter les affirmations natives aux observations réellement obtenues : les
  limites d'outillage et les gates appareils restent ouvertes.

## Sortie encore ouverte

Acceptation opérateur du board → commit/push/PR → quatre checks obligatoires
sur HEAD exact → merge gardé → CI canonique/Sonar → archive/closeout/cleanup.
Aucun de ces résultats futurs n'est anticipé ici. DATA, artefacts installables,
recette physique, qualité/sécurité de cible et GO de déploiement sont séparés.

Réconciliation ultérieure : avance rapide à3bb1f2d après PR392, différences uniquement documentaires ; pixels capturés à844cbfb et code fonctionnel identique.

## Acceptation réelle avant commit UI

9 novembre2026, Europe/Paris : **« Valider ce delta visuel contrôlé »** reçu pour le board8134 et les31captures natives soumises, leurs références et limites annoncées. Sources client et SHA des PNG comparés au reçu soumis avant enregistrement. Les pixels sont acceptés avant le premier commit UI de ce change ; aucune recette physique ou activation n’en est déduite. Le reçu versionné porte la décision ; le reçu de soumission antérieur est conservé dans les preuves.

## Relecture des décisions au premier commit UI

Relecture de DESIGN_DECISIONS_HOME_UIV2 et DESIGN_DECISIONS_UIV2_SURFACES,
amendements mobiles compris, puis du contrat/protocole natifs et de G1 :

| Décision | Verdict sur ce diff |
|---|---|
| HomeD1 | Respectée pour hiérarchie/choix lisibles/cibles ; motifs de contrôles web non réinterprétés, primitives natives acceptées réutilisées |
| HomeD2 | Respectée : aucune revendication IA ni nouvelle raison scientifique fabriquée |
| HomeD3/D4/D5 | Références legacy pour mobile selon amendement ; pas de modification de palette, retraits d'accueil ou nouvel asset |
| HomeD6 | Non concernée : récupération/cycle et MISSION inchangés, aucune dérivation corporelle |
| HomeD7 | Non concernée : ni streak ni nouvelle métrique de continuité |
| HomeD8 | Non concernée : onglets/navigation globale inchangés |
| HomeD9 | Respectée : aucune anticipation de séance suivante ajoutée |
| SurfacesQ1 | Non concernée : identité/authentification/accroche inchangées |
| SurfacesQ2 | Non concernée : accueil/récupération inchangés |
| SurfacesQ3 et amendement | Respectés : aucun questionnaire quotidien1–5 ni règle d'état dérivée ; faits de calibrage distincts |
| SurfacesQ4 et amendement | Sémantique instrument respectée ; lignes de séries/glyphes/exécution inchangés, calibrage jamais promu en série de travail |
| SurfacesQ5/Q6/Q7/Q8 et ancien .btn | Références legacy mobiles ; rôles/tokens natifs existants conservés ; une action dominante, état pressé/désactivé fonctionnel |
| Tokens bleus | Aucun token nouveau, repli hex ou usage système inventé |
| Convergence/ordre historique | Non concerné pour les anciens lots ; slice central commun des sept rencontres, sans rouvrir les surfaces LOCKED |
| G1/G2/G3/G4 | Croquis et pixels acceptés ; inventaire sourcé, références comparées, un delta de densité partagé |

## Contrôles précommit frais après décision pixels

Scope ISOLATED ; broad API/plan/calibration **25suites/387tests PASS**, TypeScript
PASS, protocole PASS, budget260≤548 et OpenSpec20/20 PASS. Le premier lancement
budget n'a pas trouvé ruff dans PATH ; relance avec le PATH du venv existant
réussie, aucun changement de dépendance ou de seuil. Aucun full sweep backend
local. Le résultat CI du commit reste à produire et n'est pas anticipé.
