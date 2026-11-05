# MOB-03 DELIVERY ACCELERATION — delta à revoir

5 novembre 2026. PR unique #353, base canonique bf847c7, HEAD publié d41eb2f. Mandat opérateur : finir le travail exécutable, préserver les compositions et données acceptées, aucune activation destructive ou scientifique non admise. Ce delta ne vaut pas politique de rétention ni autorisation de déploiement.

## Brainstorming / Options / Risques / Choix retenu

Les seuls ports de test laisseraient la durabilité serveur et le premier usage sans réalisation. Une purge et un premier plan de repli inventeraient des décisions absentes. Choix proposé : service serveur transactionnel durable non servi, fermé par une politique admise injectée ; parcours natif limité aux états prouvés, avec nouvelle page après revue du croquis/pixels. Aucun nouvel inventaire ni acquisition de poids/taille obligatoire. Pas de modification des baselines MISSION.

## Partie technique directement exécutable

- Contrôleur de premier usage sans composition : relit les préférences canoniques, distingue état d'identité/chargement/réseau et adaptateur Blueprint absent. Un port snapshot canonique futur fournit requête SCI et fingerprint ; le mobile ne les synthétise pas depuis les préférences. FirstPlanClient garde l'autorité des versions/propriétaire/validation. Aucun faux READY ou repli historique. Adaptateur et action de première séance absents par défaut.
- Tests de consommateurs, comptes A/B, changements d'identité et interruptions. Matrice de compatibilité backend/client, plan appareil et instructions de release/rollback sans déploiement.
- Analyse d'un split : proposition traçable seulement ; aucun changement des critères/PR ou merge partiel sans décision de gouvernance explicite.

## Extension serveur proposée pour revue

- Modèle dédié de demandes avec clé idempotente par propriétaire, une demande active, états PENDING/REJECTED/IN_PROGRESS/CONFIRMED, version de ligne et policy_ref. Les états sont serveur ; timeout/401/404 restent inconnus côté client. Modèle et service SQLAlchemy testés sur base jetable ; aucune migration appliquée ni import au démarrage, route ou worker activés dans cette passe. Le schéma futur/migration/HTTP gardent leur revue avant activation.
- Service partagé app/web, transports futurs Bearer/session-CSRF. Réauthentification canonique + CAS identité/époque/hash dans la transaction de demande. Pas de mot de passe/hash dans les métadonnées de demande. Clé stable relue ; autre clé pendant demande active ne crée pas une seconde opération.
- Aucun enregistrement ni acceptation avant politique admise. Registre de production vide. Politique de test synthétique uniquement pour les preuves. La politique doit préciser portée, rétention des demandes/reçus, mécanisme et durée de capacité ; aucun défaut juridique ou durée arbitraire.
- Lecture propriétaire authentifiée tant que le compte reste actif. Capacité de statut aléatoire, condensat seul stocké, portée propriétaire/demande et expiration explicitement fournie par politique admise ; émission/rotation sous réauthentification, jamais dans URL/log. Elle ne permet ni écrire ni supprimer. Tests après révocation sur fixtures isolées. Pas d'activation de révocation irréversible dans le service.
- Confirmation refusée sans autorité serveur injectée vérifiant révocation, périmètre/graphe23tables et copies/restauration. Aucun état DELETED sur simple champ JSON ou disparition de users. Pas de purge ni mode manuel approuvé par défaut. Si la politique retient le manuel, l'exécuteur et ses preuves seront raccordés explicitement ; aucune boîte de réception fictive.
- Tests de redémarrage, concurrence sur connexions distinctes, réponse perdue, réauthentification périmée, isolement des propriétaires et preuve incomplète. Les fixtures ne prouvent aucun effacement réel.

## Croquis ciblé proposé — une page après résultat « compte créé »

Entrée V1 et résultat existant conservés. « Continuer » ouvre cette page pour un compte nouvellement créé ; retour/reprise ne rejouent pas inscription. Le journal/séance en cours garde priorité. Les préférences restent modifiables depuis Profil.

```
┌──────────────────────────────────┐
│ Retour          AUREN            │
│ Ton premier entraînement        │
│                                  │
│ [Un seul message selon état]     │
│                                  │
│ [Action utile selon état]        │
│ Voir Aujourd'hui                 │
└──────────────────────────────────┘
```

Sources et actions (aucune donnée inventée) :
- chargement : « Un instant. » ; aucune action répétant une mutation ;
- snapshot/plan non servi : « Ton premier plan personnalisé n’est pas encore disponible. » ; « Mes préférences », puis « Voir Aujourd’hui » ; l'accès à MISSION ne prétend pas qu'un premier plan scientifique existe ;
- manque confirmé par SCI : « Quelques informations sont encore nécessaires. » ; accès aux préférences seulement si champ réellement éditable, sinon message d'indisponibilité honnête ;
- consentement réellement requis : « Ton accord est nécessaire pour ce traitement. » ; aucun octroi implicite ni formulaire de consentement sans contrat/texte ;
- réponse incertaine : « La réponse n’a pas pu être confirmée. » ; « Vérifier à nouveau » (lecture), préférences et sortie préservées ;
- indisponible/refusé : message explicite, nouvelle lecture possible, aucune recommandation fabriquée ;
- usable : seulement résultat admis, snapshot actuel et adaptateur de démarrage validé ; affichage/action issus de ce contrat futur, pas de prescription inventée.

La page réutilise AccountFrame/AccountMessage/PrimaryAction/AccountLink et les tokens existants. Pas de compteur, score ou illustrations nouveaux. Le croquis doit être accepté avant code de composition (G1), puis le rendu comparé et accepté avant commit UI (CLAUDE.md5.1). L'exécution technique indépendante peut continuer pendant cette revue.

## Livraison et limites

Les nouveaux objets restent NOT_SERVED tant que politique, migration et routes ne sont pas approuvées. Les choix légaux restent dans MOB03_DELETION_PRODUCER_DESIGN.md, sans doublonner les décisions techniques. Le change complet conserve ses gates science/données/appareils. Aucun split/merge partiel déduit, aucune deuxième PR, aucun MOB-04 BUILD.

## Décision de revue reçue

L'opérateur valide le 5 novembre : **« Valider le service isolé proposé »** et **« Valider ce croquis ciblé »**. Le modèle/service sans route/migration appliquée/purge/révocation irréversible et la composition ciblée sont ouverts au build. Les pixels restent à accepter avant commit UI ; aucune politique de rétention ni activation n'est déduite.
