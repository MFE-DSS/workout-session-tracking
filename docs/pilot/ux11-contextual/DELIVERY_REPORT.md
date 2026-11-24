# UX11-C — Action contextuelle, livraison contrôlée

24 novembre 2026. Parent `9dd90ac777d21291939bdf6b03d9a4b43ca59d21`.
Pixels acceptés pour ce consommateur par le mandat « UX11-C ACCEPTANCE & CRITICAL PATH CONTINUATION ». Aucun master universel, APK, OTA, DATA ou déploiement autorisé par cette décision.

## Brainstorming / Options / Risques / Choix retenu

La série précédente était noyée dans le même grand cadre que la saisie. La correction conserve une seule composition : référence secondaire, deux fenêtres numériques, commande située et identité S2 fixe pendant l’IME. Ni rail sans bornes, ni cible, ni comparaison entre occurrences.

La source précédente est une vraie observation serveur immédiatement antérieure, dans la même occurrence V3 propriétaire et le même contexte connu complet. Le pilote est borné à `leg-extensions-assises`, bilatéral et `MACHINE_DISPLAY_KG`. Les champs actuels restent vides. Les autres exercices et Legacy conservent leur consommateur canonique.

## Croquis validé

GO/G1 fonctionnel antérieur conservé ; demande précise UX11-C traitée comme croquis selon le protocole G1. L’opérateur accepte ensuite explicitement les vrais pixels du paquet `f6e0f378d35f4cca1ab93bf083caaabdee60be4952cc762fdc72d7fd66d7e492`. Le reçu `NATIVE_PIXEL_ACCEPTANCE_20261124.json` contient les empreintes des dix-huit sources produit/test approuvées, vérifiées identiques avant commit.

## Inventaire élément par élément

| Élément | Source | Portée |
|---|---|---|
| Exercice, série, prescription | execution/cursor/ContextTarget | identité et prévu distincts du fait |
| Référence S1 | lecture historique propriétaire + exécution V3, `SAME_RECORDED_CONTEXT_V1` | observation qualifiée, pas consigne |
| Valeurs actuelles | brouillon indépendant puis opération durable existante | aucun préremplissage |
| Réglage | observation typée + contexte complet | kg affichés, jamais kg externes totaux |
| À vérifier / reçu / relu / refus | état local, reçu et relecture distincts | même UUID/corps/horodatage, aucune seconde mutation créée par la vue |
| Source | binding, owner, révision, dates et référence d’index | divulgation progressive, lecture inconnue explicite |
| Action | callbacks canoniques | TIME-01, repos, SCI et journal inchangés |

## Comparaison avec la référence validée

La planche compare l’UX11 refusé au nouveau composite, sur la même séance synthétique13, source84 et série85. Une référence canonique antérieure DA08 est étiquetée comme une autre occurrence. Frame C, RecessedWindow, NumericReadout, marque, palette et baselines restent inchangés.

Relecture des décisions : D1 respectée (une action principale, contrôle≥48dp) ; D2 non concernée (aucune recommandation ni revendication IA) ; D3 respectée (ambre=action, faits manuels en encre neutre) ; D4 non concernée (accueil intact) ; D5 respectée (nombres manipulables, mémoire secondaire) ; D6 non concernée (aucun cycle ou état physiologique ajouté) ; D7 non concernée (pas de métrique de continuité) ; D8 non concernée (onglet Progrès intact) ; D9 respectée (pas de séance future inventée). Q1/Q2/Q3 non concernées ; Q4 instrument respecté selon la composition mobile expressément acceptée ; Q5/Q6/Q7/Q8 relues avec leur amendement vNext du23octobre, primitives et sémantique mobile conservées. Tokens bleus non ajoutés ; ordre historique de livraison non réinterprété comme autorisation SCI.

## Changement unique de l’itération

La série courante reste le même objet pendant lecture, édition, envoi incertain et relecture. En grande fonte la ligne S2 reste fixe, les fenêtres refluées défilent et le focus utilise un offset mesuré. Aucun changement de contrôleur, payload, horloge, authentification, stockage, backend ou production.

## Vérifications et revue

- Tier ISOLATED : pas de full sweep backend local. Tests ciblés/contextuels et consommateurs, suite mobile complète et TypeScript ; broad backend/historique/contrat visuel ciblé.
- Dernière campagne : 138 suites / 1 549 tests mobiles et TypeScript ; 90 tests backend/visuel ciblés. Budget Ruff259≤548, protocole, OpenSpec strict et Gitleaks. Aucun nouveau Python applicatif ; aucune dépendance changée.
- Revue indépendante entière : cinq Important corrigés RED→GREEN (terminal, brouillon négatif, correction inconnue/refusée, résolution/ACK inqualifiable, fait relu sans reçu local). Focus/source et provenance accessible également couverts. Aucun second avis indépendant des correctifs finaux revendiqué.
- Android ConnectedApp réel via client de revue existant : 360/480dp, IME système ; 360dp texte178,6 %. Source S1=17.5kg affichés/9rép., S2 vide puis18.5/8. Réponse de succès masquée, kill/reprise SQLite, même UUID, neuf PUT identiques par l’expéditeur existant, une observation appliquée/révision1. Six observations antérieures identiques ; aucun FINISH. Journal natif relu.

Rulings : le terminal canonique reste prioritaire (la récupération passe alors par le bilan/journal existant) ; une nouvelle révision négative invalide le brouillon une fois, puis exige une ressaisie ; une source indisponible n’est pas réutilisée comme fraîche. Coût : une navigation ou vérification supplémentaire lorsque l’autorité courante manque.

## Limites et suite

Émulateur, pas acceptation physique ni TalkBack exhaustif. À grande fonte/IME, fenêtre inactive partiellement hors champ mais défilante. `stale_identity` pendant reconfiguration de fonte a aussi été reproduit sur le canonique ; cause non corrigée ici. Après SET, une lecture409 transitoire reste inconnue jusqu’à la vérification suivante. Aucun ancien timestamp réécrit.

Code livré par PR#436, HEAD `dfc1f65e252fe9865df5cbda3cc91966485a3c29`, CI45386072355 success (11jobs : 8 896 backend/3ignorés, 138suites/1 549mobiles+TS, 77visuels), merge gardé `f0a010948e241ab257469c83d821870a2e4a4091`, arbre identique. CI canonique45389826580 completed/success, 11jobs et quatre checks protégés passants. Sonar canonique, analyse `3b805b95-3de5-48a4-909a-f224aabcd1d0` sur `f0a0109` : ERROR consultatif, 9bugs / 659smells / 8entrées externes Bandit classées vulnérabilités / 0hotspot, couverture app92,2%, nouvelle92,22626906442066%. Les 17 entrées inspectées concernent des fichiers byte-identiques à9dd ; aucun seuil ni état modifié, aucune innocuité générale revendiquée. Sonar PR436 OK, zéro issue, couverture app92,2%, nouvelle non fournie. Archive/closeout documentaire et nettoyage restent suivis par reçus vivants ; aucune acceptation physique ou publication QA déduite. La release consolidée attend DA09-B/C et sa propre autorisation protégée ; pas d’OTA par ce merge.
