> GO BODY-01/amendement/G1 reçu le 11 novembre 2026 : « Autoriser BODY-01, son amendement et G1 » (call_106057b169a74bc9887b1fea9f527f5d). Apply contrôlé en cours ; pixels non acceptés, aucune activation/release. Les statuts pré-GO ci-dessous gardent leur instant de préparation.

# UX_BOARD — BODY-01 / G1 familial proposé

11 novembre 2026. **G1_PENDING / NO_GO_BUILD / PIXELS_NOT_PRODUCED.** Une famille compacte, aucune nouvelle tab/palette/primitives. Références : Progrès MOB05A accepté, formulaires et disclosure UX-CAL-02, Frame C / RecessedWindow / NumericReadout LOCKED. La direction de correction est reçue ; les croquis et le build restent à approuver.

## Croquis commun

```text
PROGRÈS — bloc poids existant
Poids                                 Saisir
[ 75,0 kg · 11 nov                       ]
[ graphique existant : points réels      ]
[ Mensurations >       Historique >      ]

SAISIR UN RELEVÉ                    Fermer
Poids · kg / Bras · cm / autre champ choisi
[ Jour de mesure : choisir/confirmer     ]
[ valeur ]  OU  [ Gauche     | Droit      ]
[ Enregistrer                           ]
Source : saisie personnelle  · Aide >

RELEVÉ DU 11 NOVEMBRE                Retour
[ 75,0 kg                               ]
Saisie personnelle · jour déclaré
[ Corriger                              ]
Versions (2) >             Supprimer >

CORRIGER CE RELEVÉ                  Annuler
[ Jour du fait ]     [ valeur / côté     ]
Effacer ce champ > (explicite, jamais vide implicite)
[ Enregistrer la correction             ]
L'original reste consultable.

VERSIONS                           Retour
Courante · 11 nov · 75,0 kg · corrigée le…
Précédente · 11 nov · 750,0 kg · source inconnue
[ Sources et champs modifiés >           ]
Aucune commande active sur la version remplacée.

EFFACEMENT
Supprimer ce relevé et ses 2 versions ?
[ Confirmer la suppression              ]
Annuler

RÉSULTAT À VÉRIFIER
Envoi sans confirmation serveur.
[ Vérifier                              ]
Détails de la tentative >
Rejouer la même demande > (seulement après vérification)
```

Nombres purement synthétiques, pas capture produite ni mesure réelle. Pas double affichage du poids dans l'overview : le bloc existant est son seul porteur. Profil → Mesures ouvre le même consommateur BODY. Une feuille porte un champ ou une paire G/D ; pas questionnaire de tous les tours. L'utilisateur peut laisser l'autre côté inconnu. Jour visible et explicitement choisi/confirmé, aucune occurrence déduite de l'envoi.

## Information → source unique

| Élément | Source et sens |
|---|---|
| Valeur/unité | BodyMeasurement, NumericReadout, kg/cm réels ; jamais score |
| Date | measured_on déclaré / convention UTC explicite dans détail ; pas heure de pesée inventée |
| Source | provenance du champ ; UNKNOWN visible si inconnue, détails dépliables |
| Statut version | tête/liaison metadata serveur, pas nouvelle observation comptée |
| Graphique | têtes courantes du lecteur BODY, points réels ; pas moyenne/interpolation ajoutée |
| Ancienne version | audit serveur, marquée remplacée ; pas graphique courant |
| Modification | champs présents et null explicites, aperçu avant geste ; aucune acceptation déduite |
| Suppression | racine et nombre de versions serveur sous token, confirmation explicite |
| En attente/inconnu | commande durable même owner/backend ; pas succès avant ACK |
| Accord | BodyConsent/version applicable, texte accessible, action réelle |

## États et contrôles

Vide, chargement, historique précédent/hors ligne, accord requis, legacy hors bornes/nonfini, côté unique, conflit de tête, schéma indisponible, réponse perdue/kill, A/B et suppression confirmée. Inconnu ≠ zéro/vide. Valeurs absentes restent absentes ; effacer un champ exige action dédiée, dernier fait exige effacement du relevé.

Contrôles visuellement compacts, cibles >=48dp, texte extensible sans couper unité/action obligatoire. Clavier décimal FR/point, focus/Done, safe areas, retour Android et confirmation du brouillon, fontes normales/grandes, labels VoiceOver/TalkBack valeur/unité/côté/statut, ordre de focus logique, reduced-motion sans animation requise. Pas graphique en bitmap ni couleur de poids bon/mauvais.

Web : édition existante avec token et libellé « Enregistrer la correction » ; suppression affiche la portée des versions avant confirmation. Ce petit delta sera dans la même comparaison, pas refonte du site.

## Gate

G1 propose placement/hiérarchie et sémantique de versions/effacement. Après GO : un board réel iOS/Android, normal/grande fonte, vrais consommateurs/sources de test et états étiquetés, comparé aux références acceptées. Décision pixels avant commit UI, zéro rebaseline automatique. Appareil physique/accessibilité exhaustive et release distincts. Aucun rendu réel prétendu dans ce dossier.
