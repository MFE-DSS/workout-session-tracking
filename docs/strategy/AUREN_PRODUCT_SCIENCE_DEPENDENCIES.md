# AUREN — registre produit / science


**État courant — continuation MOB-03 DATA & FIRST PLAN :** SCI-P01/P02 v1 sont reçus sur le canonique 5fd18c3 ; FirstPlanClient contrôle leurs schémas et états avec AuthSession. Moteur isolé initial-policy-producer/1.0.0 reçu via #357 et son reçu #358, mais non servi/non admis ; politiques dose/temps/candidats, vrai READY et adaptateur runtime restent requis. Le producteur absent du port mobile reste NOT_SERVED. Voir le [rapport courant](../MOB03_DATA_FIRST_PLAN_CONTINUATION_REPORT.md). Les formulations de besoin initial ci-dessous conservent le contexte historique ; elles ne signifient pas que les contrats sont encore absents.
**Actualisation SCI-P02-ADMISSION-01 —6novembre2026 :** [admission partielle](../science/sci-p02-initial-policy/admission-01/REPORT.md), décisions `initial-hypertrophy-policy/0.2.0-partially-admitted`, non exécutables/non servies. D1 borné et paramètres D2 permis comme defaults conventionnels ; D3 sélection/couverture non admise (notamment tous les tirages verticaux avec rôles UNKNOWN). D4 fournit un diagnostic isolé de borne des repos, pas une durée totale ni preuve positive de compatibilité temporelle. READY_NOT_PRODUCED. Producteur1.0.0/politique0.1.0 et schémas/hashes inchangés. PLAN-03 partiellement avancé ; aucune fermeture PLAN/MOB04. Prochaine opération proposée : SCI-P02-CANDIDATE-CURATION-01 ; aucun GO BUILD runtime déduit.

Version du registre : `0.1.0` — 5 novembre 2026. Responsable de cette première saisie : agent produit/mobile.
Référence : [recadrage opérateur](AUREN_PRODUCT_SCIENCE_REALIGNMENT_2026_11_05.md). Ce document exprime des besoins consommateurs, **pas un schéma API accepté ni un verdict scientifique S0**.

## Convention de lecture et handoff

Chaque entrée porte un identifiant stable, une version, un producteur, des consommateurs, des champs/sémantiques attendus, un comportement inconnu et une preuve de disponibilité.

| Statut | Signification |
|---|---|
| PROPOSED | Besoin ou contrat proposé, pas accepté ni nécessairement implémenté |
| READY | Contrat accepté, version et fixtures de domaine prêtes pour implémentation ; ne signifie pas endpoint déployé |
| IMPLEMENTED | Producteur et projection livrés avec références et tests consommateurs ; déploiement consigné séparément |
| BLOCKED | Décision, preuve ou producteur manquant empêche l'usage cible ; le repli est explicitement limité |

Les versions ci-dessous sont celles des **demandes de handoff**, pas des moteurs historiques. Un statut BLOCKED décrit l'extension cible, pas une panne du comportement existant. Chaque promotion exige un lien vers la spec acceptée, le commit producteur, les tests, la projection API et les consommateurs compatibles. Les preuves historiques servent au repérage, pas de certification à jour.

## Dépendances prioritaires

| ID / version / statut | Producteur → consommateurs | Besoin / champs et sémantiques à établir | Inconnu ou repli | Référence existante / preuve encore attendue |
|---|---|---|---|---|
| SCI-P01 · 0.1.0 · PROPOSED | Science S0 puis responsable Blueprint → MOB-03/04 | Inputs utiles, provenance, indispensables/facultatifs, suffisance pour une première proposition, raisons d'insuffisance | Collecte limitée aux contrats existants ; aucun champ déclaré nécessaire sans consommateur ; expliciter le manque lorsque le domaine le fournit | TrainingPreferences et body_profile existants ; contrat Blueprint consommable et critères de suffisance à recevoir |
| SCI-P02 · 0.1.0 · PROPOSED | Science + propriétaire recommandation/API → MOB-03/04 | Proposition/cible, inputs utilisés, raison, confiance ou incertitude, règles de preuve, version moteur ; projections compacte et détails | Garder les sorties servies ; ne pas fabriquer confiance, durée ou cause de NO_MISSION côté UI | `mission_read_model` et `src/api/types.ts` : explications/provenance et fingerprint/policy partiels ; enveloppe complète non établie ici |
| SCI-P03 · 0.1.0 · BLOCKED | Science E7 → instrument de séance | Bornes/zones de charge, paramètres, validité et explication de leur origine | Instrument de calibration maintenu sur le banc tant que les bornes ne sont pas fournies ; contrôles produits actuels conservés | Contrat visuel et spec moteur V2 ; bornes servies/versionnées + fixtures manquantes pour intégration |
| SCI-P04 · 0.1.0 · PROPOSED | Science ontologie/intentions → MOB-06/07/10 | Identité de slot, intention, contraintes volume/distribution, exercice prévu/réalisé, exclusions, prescription supportée | Éditeur limité aux capacités autorisées ; aucun volume ou slot nouveau inventé | `app/services/slot_intent.py`, rapport Sb_PROGRAM_SLOT_INTENT_01 ; périmètre et contrat de construction à confirmer par S0 |
| SCI-P05 · 0.1.0 · PROPOSED | Science graphe + service substitution → MOB-02/09/10 | Identités et niveaux canoniques, équivalence/exclusions, conditions de validité, effet analytique | Options canoniques existantes uniquement ; pending/refus/confirmé distincts ; historique prévu/réalisé préservé | `app/services/substitution.py` et contrats MOB-02 ; validation des extensions par audit/tests S0 puis spike ciblé |
| SCI-P06 · 0.1.0 · BLOCKED | Science Blueprint/Body Intelligence → UX-LAB-PROFILE/MOB-11 | Priorités déclarées vs inférées, taxonomie, provenance, dimensions réellement calculables, limites | Déclaration utilisateur seulement pour une priorité sans interprétation validée ; aucune dimension biologique inventée pour remplir l'octogone | Spec moteur V2 et contrats profil historiques à auditer ; dimensions/projections acceptées à recevoir |
| SCI-P07 · 0.1.0 · PROPOSED | Science sémantique/taxonomie + BodyMap → MOB-04/08/11 | Correspondance versionnée zones de comptabilité, zones de présentation et zones d'exercice ; regroupements/perte de précision | Aucun mapping implicite ou passage de 11 zones de dessin à des dimensions de profil | BodyMap fonctionnel et résolveur existants ; spec V2 mentionne 15 zones atomiques ; correspondance à confirmer explicitement |
| SCI-P08 · 0.1.0 · PROPOSED | Science historique/adaptation → MOB-05 et futurs rapports | Faits historiques, comparabilité, fenêtres temporelles, tendance vs interprétation, confiance, version de décision historique | Montrer faits disponibles et absence ; aucun score, progrès, stagnation ou récit calculé localement sans contrat | Historique canonique, performed_at, « dernière fois » et services d'analyse à auditer ; critères/projections à recevoir |
| SCI-P09 · 0.1.0 · PROPOSED | Science récupération → MOB-04/12 | Estimation vs mesure, inconnues, validité temporelle, règle/politique séparées et explication | Conserver contrat servi ; absence ne devient jamais récupération complète ; aucun pourcentage fictif | `zone_recovery` / `recovery_contract` et spec V2 ; contrat de remplacement à proposer, pas de changement ici |
| SCI-P10 · 0.1.0 · BLOCKED | Science + responsable données/photos → futur change photo | Protocole reproductible, observation vs inférence, consentement, limites et provenance | Cible de suivi photographique privé sans analyse ; aucun stockage photo nouveau autorisé par ce repli | Futur contrat séparé, politique données et revue sécurité requis ; pas une dépendance MOB-03 |

## Contrat commun à négocier avec S0

Les concepts à couvrir sont : identité/type de recommandation, cible, action/paramètres, inputs réellement utilisés, explication, confiance/incertitude, règles de preuve, alternatives, génération et version du moteur. **Ne pas adopter d'emblée un nouveau payload** : auditer les sorties existantes et produire une correspondance champ par champ avant évolution.

Séparer les projections : sortie de domaine ; API/service ; résumé compact ; détails d'explication ; lecture analytique ; état inconnu/insuffisant. La structure conservée par le domaine peut être plus riche que ce qui est montré à l'écran.

La confiance doit venir du producteur et ses termes être définis. Les niveaux de certitude de la preuve (`HIGH` à `INSUFFICIENT` dans le mandat S0) ne deviennent pas automatiquement une probabilité de recommandation personnelle. Même précaution pour les vocabulaires MEASURED / USER_REPORTED / OBSERVED / INFERRED / UNKNOWN : ne pas supprimer les deux axes preuve/origine déjà décrits par le contrat scientifique V2 sans résolution explicite.

## Changements partagés et ordre d'intégration

1. Le producteur propose un delta OpenSpec compatible avec la sortie actuelle ou décrit la rupture et sa migration.
2. Les deux volets relisent sémantique, inconnu, preuve et projections ; responsabilités et décisions sont consignées.
3. Le producteur fournit fixtures et tests de domaine ; le consommateur teste la lecture et les états sans réimplémenter la règle.
4. Intégration explicite du producteur compatible puis du consommateur ; si contrat incompatible, définir d'abord la fenêtre de compatibilité et le rollback. Aucun consommateur n'est livré contre une forme hypothétique.
5. Mise à jour du registre avec commits, versions, résultats et déploiement réel. Les recommandations historiques ne sont pas réécrites sous une nouvelle version.

Surfaces à risque de collision : modèles/préférences, `mobile_read_models.py`, types API mobiles, schémas d'exercice, recommandations/substitutions et contrats de taxonomie. Vérifier status/diff avant toute écriture, privilégier un delta étroit. Ce registre n'autorise aucune modification de ces fichiers.

## Handoff produit → agent scientifique S0

**Besoin immédiat : SCI-P01 puis SCI-P02.** MOB-03 doit savoir quelles données permettent une proposition servable aujourd'hui et comment représenter honnêtement les informations manquantes. Cela ne demande pas de résoudre toute la planification hypertrophie pendant S0.

Le mobile peut déjà consommer les états et champs canoniques de MISSION/exécution ; aucune nouvelle garantie de validation scientifique globale n'est déduite de leur existence. Il attend le handoff S0 pour les écarts, les contrats futurs et leur ordre. À ne pas coder côté produit : volume optimal, taxonomie nouvelle, seuil de récupération, score de confiance, bornes E7, interprétation anthropométrique ou huit dimensions biologiques.

À retourner pour chaque demande : statut, version, sources/fixtures acceptées, champs disponibles maintenant, champs en investigation, inconnues, compatibilité et prochain livrable. Aucune réception du handoff scientifique ni achèvement S0 n'est revendiqué à cette passe.


## Précision opérateur — souhait déclaré et analyse, 5 novembre

Les priorités choisies dans l'éditeur sont facultatives et expriment un souhait, sans être le déterminant unique attendu du futur moteur. Les points forts/faibles doivent résulter de l'interprétation justifiée des observations et de l'historique, selon les contrats scientifiques à livrer ; aucun rang déclaré n'est une mesure ou une faiblesse diagnostiquée. SCI-P01/P02 devront préciser la place de ce signal parmi les autres inputs et les états inconnus, sans coefficient arbitraire défini par l'UI. Cette précision ne modifie pas les règles opérationnelles historiques sans audit ni spec scientifique.
