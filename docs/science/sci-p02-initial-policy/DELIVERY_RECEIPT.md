# SCI-P02 — reçu de livraison du producteur isolé

5 novembre 2026. **Module livré, politique scientifique encore proposée, NOT_SERVED.** Ce reçu ferme la livraison technique isolée autorisée ; il ne ferme pas l'admission de dose/temps, le premier READY, le change scientifique complet ou MOB-03.

## Autorisation et périmètre

GO BUILD opérateur : **« Valider le build isolé proposé »**. Le design autorise producteur pur, registres dédiés, tests et fixtures ; aucune API/UI, modèle partagé, activation ou déploiement. Les paramètres non soutenus doivent rester bloquants. Merge sous GOV-MERGE-01, avec HEAD attendu, sans nouveau GO ponctuel, squash, force-push ou bypass.

## Révisions et contrôles réels

| Élément | Référence | Résultat |
|---|---|---|
| Base canonique | `5fd18c3291cd93533cf7b1f7ab50862c85a7a205` | Contrats SCI-P01/P02 déjà mergés ; non refaits |
| Code + tests finaux | `1c3e7fd2308874b10cd2fcb50f6ba0140b6a9f10` | [PR #357](https://github.com/MFE-DSS/workout-session-tracking/pull/357), deux commits |
| CI PR finale | [42111402648](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/42111402648) | Neuf jobs Actions réussis, 7229 tests backend passants, 3 ignorés ; mobile, visuel, sécurité, QA et Sonar réussis |
| Merge de code | `1313f2f32e1ac3ce6fa3c77d9ac9fcf127615ffc` | Arbre identique au HEAD testé, vérifié par diff ; base/revues/threads vérifiés avant merge |
| CI canonique | [42113516143](https://github.com/MFE-DSS/workout-session-tracking/actions/runs/42113516143) | Completed/success, neuf jobs Actions réussis ; 7229passants/3ignorés, shards réellement rejoués |

L'attestation canonique est en SHADOW MODE : les shards sont réellement rejoués, aucun réemploi n'a été activé. Les trois constats Sonar de tests sur le premier HEADd30137a ont été corrigés sans toucher le producteur : comparaison d'un input équivalent dont l'ordre des clés varie ; chargement du registre sorti des blocs raises. Aucun seuil ou état d'issue modifié.

Sonar PR final : **Quality Gate OK**, nouveau bug/code smell/vulnérabilité =0, hotspot=0 ; coverage93,8%, new_coverage non exposée sur ce diff sans app/. Les compteurs ne mesurent pas la couverture du nouveau module tools/. Canonique1313f2f vérifié par revision de l’analyse : gate ERROR consultative,447smells/8bugs/6vulnérabilités/0hotspot, coverage93,8%, new_coverage93,95215767305095%. Ces compteurs sont identiques au relevé avant merge ; aucune nouvelle faille confirmée par cette tranche, aucun audit sécurité exhaustif revendiqué. Les remarques historiques restent ouvertes et aucun seuil/état d’issue n’a été modifié.

## Artefacts exécutables et limites

- Engine `initial-policy-producer/1.0.0` ; politique `initial-hypertrophy-policy/0.1.0-proposed`, non admise.
- `load_registry`, `inspect_policy`, `produce` dans tools/science_initial_policy ; sortie v1 validée par les contrats existants et fingerprint canonique.
-11fixtures générées par le vrai producteur depuis des inputs synthétiques ; aucune READY. CLI de vérification de régénération fournie.
- Diagnostic séparé avec executable=false :7intentions proposées, sélection canonique/contextuelle, affectation globale distincte et attribution15zones ; UNKNOWN reste inconnu, charge initiale non déduite.
- Inputs opérationnels requis du profil : objectif, population déclarée, cadence, budget par séance et réponse sur limitations. Anthropométrie/priorités facultatives ; expérience inconnue explicitée ; aucun inventaire obligatoire.

Validation locale : check_scope ISOLATED, 72tests producteur/contrats, broad scientifique503passants/1ignoré, deux avertissements de dépendances ; Ruff neuf/budget264≤548, Bandit, protocole, OpenSpec6/6 et Gitleaks passent. Aucun full sweep local.

Consommateur réel : AuthSession/FirstPlanClient de PR353 au SHA0ee7ba3 accepte les11sorties avec vérification canonique. Absence de producteur=NOT_SERVED sans requête de recommandation. Aucun fichier mobile modifié ; pas de recette HTTP/appareil ou de déploiement déduit de ce contrôle.

## Revue et décisions d'exécution

Revue indépendante5fd18c3..d30137a : aucun Critical/Important. Les clarifications suivantes ne changent que les tests et le manifest. Validité scientifique de la dose/du temps et efficacité individuelle non jugées par cette revue de code ; elles restent des gates explicites.

**Mineur différé :** le diagnostic ne réordonne pas le mollet pour une priorité lower seule, et ne signale pas l'absence de couverture directe pour arms. Aucun effet sur une prescription exécutable ou un statut READY ; à traiter lors de la prochaine tranche autorisée.

Choix conservés : diagnostics hors Plan v1 pour éviter une fausse admission (coût : aucune séance démarrable issue de ce paquet) ; engine explicitement versionné (coût : appelant tenu de demander cette version). Un oracle de test initial a été corrigé pour respecter les vrais rôles UNKNOWN du catalogue, sans transformer la source en crédit exact.

## Handoff et état restant

MOB-03 à0ee7ba3 est préservé. Aucun app/, clients/, data/ ou schéma v1 modifié. [Décisions et handoff](DECISIONS_AND_HANDOFF.md), [rapport](REPORT.md), [preuves](EVIDENCE_AND_AUDIT.md), [manifest](manifest.json).

Il reste à admettre/amender la dose, les candidats et leur contexte, ainsi qu'un modèle de temps avec bases couvrant préparation/apprentissage/transitions. L'approbation du build n'ajoute aucune preuve pour ces nombres. Sans politiques admises, POLICY_UNAVAILABLE prévaut ; aucune fixture READY ou fallback n'est inventé. Nouveaux inputs/persistance, adaptateur propriétaire/API, démarrage mobile et gates données/appareils restent distincts.

Le change OpenSpec reste actif, tâches d'admission/READY ouvertes ; aucune archive de complétude. Ce reçu est un delta docs-only livré par PR sous les mêmes règles de checks. Le SHA et la CI de sa PR figurent dans son reçu GitHub ; le push canonique100%docs suit paths-ignore sans skip manuel.
