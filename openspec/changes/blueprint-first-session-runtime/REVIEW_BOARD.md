# PLAN V3 — board consolidé de croquis proposé

**G1 accepté le8novembre2026 («Valider ce croquis G1»). Pixels en cours de production, non acceptés ; aucun commit UI.** Un seul board de revue pour le parcours. Il définit les contenus/actions à comparer ensuite aux références AUREN validées ; il n'autorise aucune nouvelle géométrie. Réutiliser marque/tokens/primitives, aucune illustration nouvelle. MISSION et composition de séance restent LOCKED.

## Autorité visuelle et périmètre

Après GO et accord de ce croquis, le même board réunira vrais rendus à côté des références compte/premier usage/séance, états et largeurs applicables. Accord des pixels nécessaire avant commit de composition. Une information = un porteur/source ; pas d'affichage de hashes, noms de tables ou diagnostic scientifique dans le produit. Aucun visuel de session READY fabriqué : données de revue issues du vrai producteur avec entrée de test étiquetée, non servie en production.

## Croquis de parcours unique

```text
Compte accepté → Ton premier entraînement (état existant)
                         │
              [Préparer les réglages]
                         ▼
 A — Première rencontre / informations utiles progressivement
 [marque et primitives AUREN existantes]
 Aide lisible même sans réglage et informations complètes du plan
 Avant essai : cadre adulte/non clinique et limitations déclarés
 [Continuer]               [Revenir à Aujourd'hui]
                         │
                         ▼
 B — Pilote : extension de jambes assise bilatérale
 Appareil/réalisation et instructions réellement présents
 installation → familiarisation → essai → observation → acceptation
 Réglage [vide avant choix humain réel] + unité/sens explicites
 Faits d'un essai passé distincts de l'action actuellement permise
 [Action effectivement permise]     [Assistance / arrêter]
 Pas de répétition contre résistance inconnue
                         │
           [Poursuivre ma préparation] sans essai inventé
                         ▼
 A' — Informations nécessaires au plan, éditables plus tard
 Objectif [confirmation] ; cadence [préférence canonique]
 Temps disponible par séance [déclaration]
 Limitations [réponse explicite] ; manques/conflits conservés
 Autres réalisations : faits déjà observés ou indisponibilité
 Pas de guidage initial des six autres depuis le pilote
                         │
       si sept réalisations réellement qualifiées et admises
                         ▼
 C — Première proposition
 [séances/exercices/prescriptions du vrai résultat SCI validé]
 Réglage observé avec son sens, pas charge optimale
 Temps disponible [déclaration] ; durée totale [non établie]
 [Lire et reconnaître l'incertitude]
                         │
                         ▼
 D — Accord temporel explicite, plan exact
 « La durée totale n'est pas établie. La séance peut dépasser
    mon temps disponible ; je peux m'arrêter. »
 [action de reconnaissance non prévalidée]
 [Commencer] après ack confirmé → commande durable
 Navigation séance seulement après CREATED confirmé
                         │
                         ▼
 E — Séance native existante, composition LOCKED
 label de réglage typé + setup sans timer (deltas de ce board)
 pause / reprise / journal / fin ; faits réels, pas score fictif
```

Aucun écran d'inventaire. Aucun poids/taille/expérience requis pour ce binding. Objectif hypertrophie expliqué comme finalité du parcours et confirmé, pas transformé en préférence silencieusement déclarée. Cadre adulte/non clinique reste déclaration de l'utilisateur, jamais diagnostic. Copie définitive de consentement/finalité applicable fournie par DATA avant activation, pas inventée ici.

Le plan SCI limité n'admet pas un démarrage sans les sept réglages qualifiés. L'ouverture de A/B ne demande pas ces sept réglages. B consomme le seul pilote leg-extensions-assises admis (BOOTSTRAP_INTEGRATION) et des faits réels, pas une checklist prétendant qu'un essai a eu lieu. Les six autres accompagnements initiaux ne sont pas admis ici. Instructions spécifiques au dispositif et phases du protocole admis nécessaires ; si inconnues, arrêt/revue. Aucun kg, nombre d'essais ou temps de préparation par défaut. Une disponibilité seule n'est pas calibration, et une série dans la plage ne mesure pas un vrai2RIR.

## Inventaire information → source

| Élément | Source et condition réelle | Action |
|---|---|---|
| Cadence/priorités éditables plus tard | TrainingPreferences, provenance de l'action | préférences existantes préservées |
| Objectif/cadre/budgets/limitations | déclarations serveur + contrat first-bodybuilding-inputs2.0.0 | capture authentifiée, refus/absence conservés |
| Consentement pertinent | autorité DATA, pas consentement body global | acquisition si réellement REQUIRED ; UNAVAILABLE reste inconnu |
| Nom/intention/exercice/sets/reps/repos | vrai résultat SCI validé et binding exact | aucune métrique décorative, aucun template fallback |
| Appareil/unité/réglage/qualité | ledger propriétaire, rencontre réelle evaluate/validate_result et épisodes confirmés | sens MACHINE_DISPLAY_KG/PER_IMPLEMENT/TOTAL_EXTERNAL distinct |
| Temps disponible | budget déclaré | pas renommé durée estimée |
| Durée et permission | time_assessments/start_permission | UNKNOWN explicite, ack séparé, aucun fit implicite |
| Séance à ouvrir | CREATED authentifié + session_id possédé puis GET execution | jamais depuis le seul DTO SCI |
| Statut de série/bilan | SetLog et observation typée | inconnus omis ; pas80/NULL→0/records incompatibles |

## États sur le même board

| État réel | Projection proposée, sans nouvelle recommandation |
|---|---|
| Manque d'information | manque précis du contrat, bouton compléter ; pas anthropométrie ou inventaire ajouté |
| Consentement applicable requis/inconnu | finalité réelle et parcours applicable, ou information indisponible ; pas faux accord |
| Producteur/capacité absent | proposition indisponible, sortie Aujourd'hui existante ; pas MISSION rebaptisée SCI |
| Chargement/commande incertaine | action bloquée contre doublon, vérifier même demande ; jamais nouveau request_id |
| Réglage inconnu/dispositif indisponible | ouverture d’aide possible ; consigne de pilote seulement selon allowed_actions, sinon assistance/revue/sortie ; aucune substitution inventée |
| Réponse refusée/conflit/périmée | motif utile et édition/relecture, pas succès depuis401/404 |
| Temps inconnu, science admise | reconnaissance explicite du plan exact, pas de durée positive |
| Séance créée puis retrait/concern/offline | lire/journaliser/sortir ; nouvelle consigne bloquée si applicabilité inconnue |
| Compte changé/réponse tardive | aucune information du compte quitté exposée |

## Comparaison et acceptations à obtenir

Références : entrée/formulaires/préférences et premier usage acceptés, MISSION-SCREEN-V1 et quatre baselines LOCKED, séance native MOB02. Le board de pixels montrera référence/rendu côte à côte, état, source, plateforme et largeur ; ne remplace ni Android/iPhone physiques ni force-kill SQLite.

Décisions distinctes : **GO BUILD de scope**, **acceptation du présent croquis**, puis **acceptation du board réel de pixels**. Un accord à l'un ne simule pas les deux autres. Le backend autorisé peut progresser pendant attente de pixels ; aucune nouvelle composition ne sera committée sans son acceptation.

## Réconciliation scientifique et progression d'observation

Sources actuelles b4a4242 et BOOTSTRAP_INTEGRATION. Le nom «pilote» décrit la portée en revue, pas un label scientifique décoratif à afficher. Aucun compteur «exercice1/7» n’impose sept observations pour ouvrir la première rencontre. Une personne déjà qualifiée peut entrer directement par A'/C selon les faits et ses préférences. Aucun écran déjà accepté n’est redessiné par ce croquis.

Le mineur SCI1.0.0 est conservé : le résultat peut redevenir state=SUPPORTED_INITIAL_EXPLORATION et phase=FAMILIARIZE si choix actuel absent alors qu’un essai passé existe. Projection proposée : présenter cet essai comme fait du ledger et la condition courante manquante, sans annoncer «aucune observation», sans transformer state ou ajouter une action. En ledger incomplet, progrès inconnu, pas0. L’accord G1 demandera explicitement cette distinction ; si elle n’est pas rendable, montage du pilote reste fermé jusqu’à correctif SCI versionné.

## Pixels réalisés et décision reçue — 8 novembre2026

Huit captures natives et références côte à côte : [UI_REVIEW](../../../docs/plan/blueprint-first-session-runtime/UI_REVIEW.md). Réponse opérateur «Valider ces pixels PLAN contrôlés», reçue avant commit UI. Les limites de simulateur, dimensions et sources synthétiques sont explicites ; aucune baseline LOCKED modifiée.
