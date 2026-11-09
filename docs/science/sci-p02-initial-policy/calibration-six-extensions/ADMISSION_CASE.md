# Cas d'admission proposé — six rencontres, aucune admission acquise

9 novembre2026, ba2dbbc. **PROPOSED / NOT_ADMITTED / NOT_SERVED.**
Cette passe prépare une convention opérationnelle limitée ; aucun nouveau test
humain, résultat clinique ou seuil biologique n'est revendiqué. Les revues
SCI/code et la publication du bundle effectif restent après le GO de build.

## Réalisation et sémantique exactes

Sélection issue du vrai registre V3 publié, pas de la seule ligne historique de
curation. G17 utilise la résolution conditionnelle déjà livrée ; ne pas rouvrir
les quatre autres pulls, ni transformer UNKNOWN en zéro/crédit numérique.

| Candidat | Intention | Sémantique proposée | Réalisation V3 inchangée |
|---|---|---|---|
| `chest-press-machine` | `initial_press_v1` | `MACHINE_DISPLAY_KG` | `initial-candidate-realisation/1.0.0@477c8e570e9260cdf20a3b6502490d68c7243059d526d0734ae68568f5ef9642` |
| `rowing-chest-supported` | `initial_row_v1` | `MACHINE_DISPLAY_KG` | `initial-candidate-realisation/1.0.0@f65ee15f870e8d6c57dafa5bc9afa359ec2d774272f704a2cfd6884c61a6f773` |
| `romanian-deadlift-halteres` | `initial_hinge_v1` | `PER_IMPLEMENT` | `initial-candidate-realisation/1.0.0@b857f3bdb563e90e2a84f17403d407d3eb4936fa183bddf05c2d7cd7f15d29f1` |
| `tirage-poulie-haute-prise-neutre` | `initial_vertical_pull_v1` | `MACHINE_DISPLAY_KG` | `initial-candidate-realisation/1.0.0@0e07dc7086decdddf1411bc1821ef3a1dc987b227fa43ef43396c1dd4c50a234` |
| `elevations-laterales-machine` | `initial_lateral_delt_v1` | `MACHINE_DISPLAY_KG` | `initial-candidate-realisation/1.0.0@07e1300036de7f302e8b2c76303f731a9cd050f11658487f215659e0ec8eb5cf` |
| `releves-mollets-debout-machine` | `initial_calf_v1` | `MACHINE_DISPLAY_KG` | `initial-candidate-realisation/1.0.0@650be74db4ab9e31eb4fabdf21e99637159e345ebd8be40bd89287dcb94da1cc` |

## Dossier par réalisation

Les préconditions communes sont celles du design : adulte déclaré non clinique,
limitations connues vides, ledger complet sans préoccupation, instructions et
contexte actuels compris, réglage choisi humainement et familiarisation chargée
applicable. Aucun épisode requis pour ouvrir l'aide ; pas d'inventaire global.

| Réalisation | Faits supplémentaires réellement requis | Ce qui reste incertain et ferme le guidage |
|---|---|---|
| Chest press | Dispositif et réglage de siège/dossier/poignées, trajectoire/release applicables, affichage kg identifié | Nom machine ou notice d'un autre modèle ne prouve ni contrôle ni résistance disponible |
| Row avec appui | Appui thoracique/poignées et voie de retour réellement compris ; contexte machine à affichage kg | Un row sans appui ou autre mécanisme n'est pas cette réalisation |
| RDL haltères | Réalisation bilatérale, prise/manipulation et parcours de retour contrôlés ; kg par haltère identifié ; familiarisation au réglage après choix | Rehearsal sans haltères ne prouve pas contrôle chargé ; aucune compétence de charnière n'est inférée d'une checkbox ou du poids corporel |
| Tirage neutre G17 | Station câble, accessoire neutre, installation et trajet qualifiés dans G17, source réelle des instructions | Une notice de pulldown général ne prouve pas cet accessoire/réalisation ; aucun transfert d'une machine à bras fixes supposé |
| Élévations latérales machine | Appuis/axes/retour du modèle réellement présent ; affichage kg identifié | Pas de réglage ou amplitude universel depuis le nom du candidat |
| Mollets debout | Dispositif debout et appuis, accès/sortie sous contrôle, affichage kg réel | Un calf assis ou une notice de montage seule ne couvre pas le contexte debout |

Les textes décrivent les informations à acquérir, pas une série de consignes
posturales universelles. Les déclarations de compréhension/contrôle restent
subjectives. Si elles ne peuvent être établies, assistance réelle si disponible,
aide/revue/pause/retrait ; aucune aide ou maîtrise présumée.

## Pourquoi cette extension est candidate et ce qu'elle ne démontre pas

- Acquis : candidats/réalisations et qualification observée V3 limités déjà admis ;
  types de faits et rencontre/pilote1.0.0 disponibles.
- Hypothèse à faire admettre : leur première rencontre peut suivre une procédure
  conditionnelle spécifique, avec choix humain et familiarisation au réglage,
  sans algorithme de charge. Ce n'est pas le transfert automatique du pilote.
- RDL : préparation facultative du geste sans haltères, distincte de l'essai ;
  chargement uniquement après choix réel et familiarisation chargée courante.
  Pas d'import d'un nombre de répétitions d'apprentissage ou d'une charge de manuel.
- Durée, vrai RIR, aptitude médicale et sûreté individuelle restent inconnus ;
  C3 qualifie provisoirement les faits, pas une technique objectivement mesurée.
- Manque avant positif : GO de politique/build, implémentation stricte, puis revue
  SCI du bundle effectif et sources par réalisation. Un refus doit préciser ce
  qui manque ; pas une nouvelle liste générique de gates.

## Sources primaires ciblées et limites de transfert

Aucune nouvelle enquête anatomique. Sources externes vérifiées le9novembre,
PDF téléchargés hors repo pour lecture ; aucun schéma/asset/texte de notice
réutilisé en produit ou committé. Résumés propres courts, pas de citation longue.

| Source | Accès effectif / portée | Limite pour ce dossier |
|---|---|---|
| [Life Fitness Insignia Rev BE](https://kb.cybexintl.com/Owners_Manuals/Strength/Life_Fitness_Insignia_Series_Owners_Manual_9481201_Rev_BE.pdf), [index officiel](https://support.lifefitness.com/hc/en-us/articles/360043013933-Life-Fitness-Insignia-Series-Strength-Owner-s-Manual) | PDF complet récupéré ; pagesPDF18/27/31/33 lues, vues31/33 inspectées : procédures séparées par modèle | Exemples seulement. Aucune instruction de ce modèle ne prouve une autre machine ou le contexte G17 neutre. Aucun poids/incrément de la fiche importé |
| [Hammer Select9510901](https://kb.cybexintl.com/Owners_Manuals/Strength/Hammer_Select_9510901.pdf) | PDF récupéré, pagePDF60 (imprimée58) lue/inspectée : accès et sortie du HS-SC debout | Source constructeur de ce modèle, pas validation novice ou étiquette de tout calf ; pas assimilation au calf assis |
| [ACE, Pete McCall2016](https://www.acefitness.org/continuing-education/prosource/january-2016/5767/ace-technique-series-romanian-deadlift/) | Article professionnel original, passages RDL/haltères et apprentissage sans charge lus | Orientation technique, pas essai clinique/charge personnelle. Ses nombres et promesses de prévention ne sont pas repris |
| [NSCA2019, extrait officiel](https://www.nsca.com/education/articles/kinetic-select/romanian-deadlift-rdl/) | Extrait de manuel barbell lu | Ne constitue pas preuve directe de premier usage haltères ; pas de transfert de charge ou d'amplitude chiffrée |
| [Wiedenmann et al.2026](https://link.springer.com/article/10.1186/s13102-026-01997-y) | Étude primaire, méthodes lues :26adultes avec expérience RT, BP/LP supervisés, estimation puis échec | Ne valide aucun de nos six premiers essais novices ; conserve incertitude RIR et aucune promotion automatique de confiance |

Hashes de récupération : Insignia e59815babff8e232439a9fe8f49123b97d4d7eb73d782fcf70b6e7bfe1448b9e ;
Hammer4014619722c47af343deb9dcc99fd85b657fc8c351fd9230f7a781f3dc2b994a.
Les outils web ont refusé ces PDF trop volumineux ; téléchargement direct puis
PDFKit macOS utilisés, sans installation de dépendance. Textes/images de lecture
restent sous /private/tmp/auren-sci-calibration-extension-review-evidence/.

## Responsabilités après ce dossier

SCI : conventions/procédures, revue et registre effectifs, évaluateur positif et
pont V3 réel. PLAN : acquérir les faits depuis compte, ledger exhaustif/révision,
provenance et sélection explicite du nouveau profil sous un autre delta. DATA :
finalités/consentements/copies/retrait/effacement avant données personnelles.
RELEASE : environnement, appareils et GO distinct. Aucun de ces faits n'est
créé par un hash, la préparation ou une fixture.
