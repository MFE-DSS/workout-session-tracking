# NUT-01 — revue, décisions et validation contrôlée

**Verdict prépublication : contrôles locaux passants et pixels acceptés pour le pilote ; CI du HEAD final et merge encore à observer.**

## Brainstorming / Options / Risques / Choix retenu
Conserver le checkpoint isolé bloque le MVP ; appliquer l’ancienne copie combinée risque de perdre BODY. Choix : reprendre le même worktree, sauvegarder152fichiers avant commit, intégrer les sources exactes BODY puis leur ascendance normale, conserver un scope/PR NUT et laisser la CI finale contrôler l’arbre réel. Risque : résolution partagée incomplète ; garde : empreintes des parents, tests consommateurs et CI. Pas de nouvelle architecture ou de permission implicite.

## Croquis validé avant le code —5.6
G1 fonctionnel, masterB DA07 et familleDA08 reçus avant reconstruction ; reçu natif finalement accepté avant commit. La décision du15novembre porte sur le pilote avec réserves artistiques. Les anciens refus et limites du banc sont conservés, pas réécrits comme des succès.

## Une information, une seule fois —5.7
| Élément | Source | Porteur |
| --- | --- | --- |
| Jour/zone | DAY.local_day/timezone | sélection datée explicite |
| Énergie/macros | DAY.values.*_milli | un NumericReadout typé par champ |
| Complétude | DAY.declared_complete | commande séparée des valeurs |
| Référence personnelle | DAY.target_ref/version TARGET exacte | cible distincte et calcul arithmétique explicite |
| Historique | têtes applicables +coverage/totals | points sans interpolation, dates/échelle et jours exacts |
| Source | provenance de chaque révision | détail progressif, pas une certification |
| Réception incertaine | commande SQLite/reçu exact | action de vérification distincte du fait serveur |
Les valeurs cibles restent dans leur contexte de cible ; aucune alimentation manquante n’est remplacée par zéro. Pas de muscles, scores, période favorable ou objectif nutritionnel inventés.

## Comparaison avec la référence validée —5.8
Board8264 expose DA07B, familleDA08 acceptée puis17captures natives actuelles, séparant ConnectedApp et Hosts. Primitive/tokens/mark/D4, baselines et SDK/lock inchangés par NUT. Aucun rebaseline ni copie d’une UI externe.

## Un changement par itération —5.9
Reconstruction du même NUT manuel selon masterB/familleDA08 ; corrections de revue bornées, sans quatrième proposition artistique. Demande opérateur finale citée exactement : « Accepter les pixels NUT pour le pilote, avec réserves artistiques ». Les raffinements de DA sont un suivi distinct ; aucune nouvelle variante réalisée après ce gate.

## Relecture décision par décision —5.2
HOME_UIV2 D1 : hiérarchie/cibles tactiles respectées sous supersession native ; D2 respecté, aucune revendication IA ; D3/D4/D5 anciennes références mobiles, tokens et famille natifs actuels souverains ; D6 hors scope récupération, inchangée ; D7 pas de streak ou qualité de repos inventée ; D8 respecté, entrée dans Progrès existant ; D9 respecté, aucune anticipation de séance.
SURFACES Q1 connexion inchangée ; Q2 récupération hors scope, conservée ; Q3 état du jour décommissionné non ressuscité ; Q4 exécution/lignes de série inchangées ; Q5/Q6/Q7/Q8 legacy mobile selon amendement, tokens actuels et DA08 utilisés ; action dominante unique dans l’éditeur,48dp, reflow et commandes secondaires séparés. Tokens bleus web inchangés ; system réservé ici au résultat arithmétique justifié. Aucune primitive ou palette parallèle.

## Revues et corrections
Revue indépendante entière fraîche du15novembre :70sources, aucun Critical,5Important. Corrections en une passe RED→GREEN : frontières de lecture secondaires et génération ; fallback du même jour ; brouillon conservé après refus définitif/relecture explicite ; cible zéro/différence sans division ; mémoire/couverture7/30jours.29tests de correctifs/consommateurs verts puis108suites/1291mobiles+TS ; témoin mémoire30jours ajouté ensuite,6PASS séparément avant le dernier run de livraison. Pas de second avis indépendant prétendu.

Deux mineurs différés : audit de journée désactivé en lecture seule et accès direct à ancienne cible liée hors candidats ; états ACTIVE/WITHDRAWN/enabled/complétude non résumés dans chaque ligne d’audit. Réserves artistiques opérateur non bloquantes pour le pilote.

## Vérification locale
MIGRATION.447fichiers/8668PASS/1ignoré dans une campagne composée :267initiaux avant arrêt mémoire1906Mo,171nœuds des2fichiers lourds sous garde1600Mo,178queue verte. Pics305/1166Mo. Ce n’est pas un run ininterrompu. Sources app/migration inchangées ; tri d’imports d’un test puis relecture3PASS, sans second fullsweep inutile. Quatrechecks migration/drift/snapshot PASS ; Ruff neuf/budget260≤548, protocole, Bandit-ll et Gitleaks passent ; OpenSpec26/26.

CI exacte et Sonar seront rapportés avec leurs résultats réels. Aucune ancienne CI du checkpoint ne couvre la nouvelle intégration. Physique, geste/focus exhaustif, Android complet, traitement réel et release restent ouverts.

## Dernier relevé avant intégration Git
15novembre :108suites/1292tests mobiles PASS et TypeScript PASS sur la source soumise à l’opérateur, sans nouvelle modification UI. Quatre checks migration et25gardes de contrat UI/documentaires PASS. Les reçus antérieurs1291+6 décrivent leurs campagnes historiques, sans addition de compteurs.
