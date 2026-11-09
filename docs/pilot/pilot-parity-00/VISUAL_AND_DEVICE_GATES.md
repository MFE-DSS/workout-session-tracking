# Familles de revue et preuve installée

## Familles proposées, pas nouvelles baselines

| Famille | Surfaces/contrat | Gate |
|---|---|---|
| MISSION/orientation | Références MISSION-SCREEN-V1 intactes ; choix source, reprise et inconnus ; host calibrage existant non recomposé | Board G1 MOB04 avec variante d'entrée à choisir, puis vrais pixels iOS/Android |
| Historique entraînement | Liste/détail séance/exercice MOB05 ; grammaire date/période/unité/lecture native | Une planche consolidée de la famille entraînement avec tous états, pas un GO par écran/exercice |
| Mesures corporelles | Relevé/poids/mensurations/saisie BODY01 ; mêmes primitives de chronologie lorsque leur contrat convient | Une planche consolidée de la famille corporelle ; source/côté/date/qualité propres, pas une approbation par mesure |
| Déclaration nutrition | Jour, valeurs/cibles déclarées, complétude, historique et correction | Board NUT01, vrais rendus sourcés et états manquants/replay/conflit |

Réutiliser tokens, mark, FrameC, RecessedWindow, NumericReadout, BodyMap fonctionnel seulement quand ses sources le justifient. Graphiques déterministes natifs, pas de raster/Jinja copié ; pas de vert nouveau, score, tableau décoratif ou cinquième onglet. Nutrition/corps dans sous-surfaces Progrès/Profil cohérentes ; Programmes garde sa destination. Pas d'asset biologique produit pour remplir un manque. Screenshots externes = fonctions/hiérarchie, pas DA copiée.

## Evidence required for the pilot milestone

| Couche | Preuve attendue | État à cette préparation |
|---|---|---|
| Sources | SHA JS/natif/backend, config effective, bundle/génération SCI, schéma/migrations | Dernier dossier contrôlé connu, pas artefact courant du pilote attesté |
| Build | Android/iOS compatibles installables, identités QA/config/réseau autorisés ; pas hôte Expo Go confondu avec binaire autonome | Aucun artefact QA autonome actuel attesté |
| HTTP réel | Auth, ownerA/B, refus de tiers, productionV3/ack/commande existants, nouvelles routes de chaque slice sous GO | Preuves historiques fe9/UX contrôlé conservées, pas nouveaux tests de ces futures routes |
| Consommateur réel | Navigation quatre onglets et sous-surfaces réelles, pas galerie seule ; journal/outbox/retours/reprise | À éprouver après builds approuvés |
| Native interaction | Clavier/décimal/locale/focus, grandes fontes/safe areas, retour Android, VoiceOver/TalkBack, mouvement réduit, interruption/relance/réseau | Gates ouvertes ; anciennes captures ne sont pas une nouvelle recette |
| Physical | Device/OS/build/backend et données de test identifiés, walkthrough Android/iPhone effectivement observé | Aucune preuve nouvelle, pas de substitution par HTTP/Playwright |
| Real data / release | Politique/finalités/consentements/copies/exports/effacement, sécurité/qualité cible et rollback puis GO déploiement | Ouvert, aucun Store/OTA/déploiement autorisé |

Sortie : chaque capacité absente rend son vrai motif et une action réellement disponible, jamais un faux écran de réussite. Une merge/CI n'est ni parité pilote ni activation. Les compteurs de données incomplètes et les états UNKNOWN restent visibles à la bonne profondeur.
