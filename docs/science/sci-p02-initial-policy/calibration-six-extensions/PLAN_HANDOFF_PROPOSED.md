# Handoff PLAN proposé — future autorité de six rencontres

**PROPOSED / NOT_IMPLEMENTED / NOT_ADMITTED / NOT_SERVED.** Ne pas brancher ce
fichier comme capacité disponible. PLAN contrôlé #379/#380 reste clôturé, son
pilote et ses pins inchangés ; DATA/activation/RELEASE demeurent ouverts.

## Après livraison SCI seulement

- Échange existant first-calibration-encounter/1.0.0 et CalibrationEpisode inchangés.
- Autorité future initial-calibration-extension-registry/1.0.0, politique
  initial-calibration-extension/1.0.0 ; pins effectifs à recevoir après build/revue,
  pas de digest candidat promu en autorité.
- API Python proposée : load_extension_authority(root) ; evaluate(raw,authority) ;
  validate_result(raw,response,authority), résultat canonique recomputé. Noms
  finaux seront fixés dans le plan après GO et publiés dans le vrai reçu.
- Chaque profil nomme ID/réalisation/sémantique/protocole/revue/version et retrait.
  Client/serveur doivent supporter explicitement ce profil, pas seulement le JSON
  Schema1.0.0. Politique inconnue = refus ; aucun downgrade implicite vers le pilote.

Le worker produit actuel importe le pilote historique ; ce scope SCI ne modifie
ni son packaging ni ses capabilities. Future intégration PLAN doit versionner
l'inventaire privé et conserver l'ancien replay. Les nouveaux modules scientifiques
ne sont pas importés depuis app/startup dans ce build.

## Acquisitions et preuves

Sujet depuis auth, owner/revision/as_of, contexte exact et source des instructions,
compréhension/contrôle réellement déclarés ; disponibilité UNKNOWN reste UNKNOWN.
Déclarations, préparation, choix, confirmations et essai/acceptation sont des faits
append-only, jamais résultats de navigation. Dates réelles avant essai et source
persistée ; ordre explicite compatible avec la granularité d'horloge, pas durée0
ou délai chiffré déduits. Aucun choix client ne désigne une autorité arbitraire.

Avant choix : aide/installation, RDL rehearsal sans haltères si applicable, pas
ATTEMPT_OBSERVED/setting0. Avant nouvel essai et qualification des extensions :
familiarisation explicite au réglage choisi, au bon contexte, après préparation/
choix/contexte et avant essai. Une ancienne confirmation ou booléen seul ne suffit
pas. Nouvelle charge humaine ne déclenche ni incrément moteur ni auto-retry.

QUALIFIED pointe l'essai/acceptation/réglage exacts et épisode portable ; il ne
crée ni séance ni travail accompli. Après sept épisodes applicables, snapshot et
vrai V3/ack/commande possédée restent la voie existante. Concern/retrait/authority
unknown ferme le guidage ; faits et journal déjà acquis restent distincts.

Réponses perdues : mêmes clés/corps et relecture propriétaire, pas nouveau fait
pour contourner UNKNOWN. Source/context/binding changé invalide futur guidage,
pas les faits historiques. A/B et réponses tardives restent sous garde PLAN.
Consentements pertinents réels doivent être satisfaits avant activation ; absence
DATA n'est jamais masquée par le fait que l'anthropométrie n'est pas requise.

## Critères du prochain delta PLAN

Raccordement explicite de l'autorité réellement livrée ; decoder/profil négocié ;
fam/setup vs loaded-fam présentés séparément ; vrai ledger/restart/A-B ; nouveaux
textes/surfaces soumis aux gates visuelles applicables. MISSION demeure LOCKED.
Aucune demande de refaire le socle, le producteur V3 ou le journal canonique.
