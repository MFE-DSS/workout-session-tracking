# MOB-04 — réconciliation PILOT VALUE DELIVERY

**État courant : GO_BUILD_CONTROLLED / G1_ACCEPTED / PIXELS_PENDING**, décision opérateur « Autoriser MOB-04 et valider G1 », [reçu](BUILD_AUTHORIZATION.md). Les paragraphes de proposition ci-dessous conservent leur instant historique ; la navigation B est retenue. Base de réalisation réconciliée d67f12a (REL03 livré et réservation MOB06 préservée).
10 novembre 2026. Base canonique **b9a334d22e6b75e9b83650eb1b2b833d4ed5d169**. **PROPOSED / NO_GO_BUILD / G1_PENDING.** Ce mandat demande la réalisation après approbation ; la proposition du9novembre est réutilisée, pas un deuxième change. Le dossier original est sauvegardé hors worktree avant réconciliation.

## Choix soumis et portée exacte

La façade propriétaire read-only et ses contrats de design.md sont retenus pour revue. Le choix de navigation **B** de UX_BOARD est précisé : Aujourd'hui utilise FIRST_USE pour le parcours contrôlé, sans changer de source après échec. Le parcours historique est une action secondaire explicite « Autres parcours », jamais un repli automatique ; il consomme la vraie recommandation historique et ne prétend pas à une admission SCI. Une séance ouverte possédée, quel que soit son profil, gagne dans les deux chemins. Aucun formulaire ni moteur d'onboarding recréé.

Première utilisation : action vers le contrôleur PLAN existant seulement si ses capacités réelles sont disponibles. Retour : reprendre séance ouverte ; après première séance clôturée, lire son handoff/histoire ou la recommandation historique explicitement demandée. Ce premier binding ne crée pas une deuxième séance SCI. Une nouvelle recommandation SCI non admise reste indisponible, jamais inventée pour remplir Today.

Les intentions locales pending/unknown, leur compte et la réconciliation du contrôleur/journal restent prioritaires sur toute proposition neuve. Tant qu'une création/fermeture durable n'est pas réconciliée, aucune action contradictoire de nouveau start. Le serveur ne voit pas forcément ces intentions : la ressource serveur seule n'est pas la vérité de leur réception. Une réponse CREATED relue est un fait possédé, pas une permission actuelle de travail.

## Surface et comportement

MISSION-SCREEN-V1 reste intact au pixel, y compris phrase exacte du moteur, géométrie/zones et bouton visible ; les détails supplémentaires sont disponibles à la demande **hors carte LOCKED**. Les nouveaux états d'orientation réutilisent la famille compacte acceptée UX-CAL-02, pas de nouvelles primitives, palette ou asset. Un CTA dominant : Reprendre / Continuer / Vérifier / Actualiser selon état réel. Chargement, cache précédent, commande locale en attente, refus confirmé et transport inconnu sont distincts. Aucun compteur ni charge synthétique.

Un seul propriétaire du journal et des contrôleurs dans ConnectedApp. Le host PLAN automatique ne masque plus Today/les quatre onglets hors séance ; le même contrôleur reste vivant pour restore/reconcile et reçoit l'ouverture explicite. Aucun second état de séance. Reconnexion/foreground : drain existant puis relecture, séquence/auth et source vérifiées ; réponse tardive A ne remplace pas B. Aucun nouveau réseau-sensor ou dépendance.

## Source actuelle et preuves

- QA02 source APK5ed4e0e, build EAS1c56f099 ; module natif présent, Updates désactivé. Les captures native-fresh-entry.png et native-main.png de /private/tmp/auren-release-qa-02-evidence ont été lues : host calibrage puis MISSION historique sont des surfaces existantes, pas notre nouvelle projection.
- UX-CAL-02 #393/#394 accepté et livré ; calibrage compact, ses deux mineurs sont déjà traités. Ce scope ne les reconstruit pas.
- Le poids a un adaptateur headless existant ; il ne relève pas de MOB04. Progrès reste PendingSpace au canonique.
- Manifesto conjoint produit/science, MOB00 inventory, critical path, CLAUDE et GOV relus. Les mentions historiques « pas de premier plan » ne révoquent pas PLAN379/380/388/389.

## Livraison / leases / test

BUILD_SCOPE reste applicable ; ajouter au lease documentaire ce fichier et PREPARATION_RECEIPT.md. Registre et migration map seront append/étendus dans la seule PR MOB04, pas simultanément par MOB05/REL03. L'ancien brouillon ARCH n'est ni déplacé ni exécuté : cette branche spec/mob04-pilot-opening est la seule ligne d'apply/PR proposée pour le présent mandat.

REL03 a désormais son GO contrôlé et ne touche ConnectedApp que pour l'observateur QA. **Séquence exclusive : REL03 → MOB04 → MOB05A** pour ce fichier ; préparation et tests de modules isolés indépendants possibles après leurs GO, jamais PR chevauchantes. Relecture/rebase après chaque merge avant patch de composition, sans réécrire un HEAD déjà publié. BODY/NUT restent en préparation.

Vrais tests HTTP : open legacy/SCI et plusieurs ouverts, owner étranger404, authority/capabilities fermées, first-handoff fermé, source explicite, négociation406 et GET sans mutation. Consommateur natif : boot/reprise/local pending/start inconnu/close pending, A/B et réponses tardives, offline/reconnexion sans cold restart obligatoire ni nouveau start, phrase/zones MISSION inchangées, contrôleur unique et ack inchangé. Rendus iOS/Android avec vrais composants/HTTP synthétiques ; pixels soumis avant commit. Physique reste UNAVAILABLE tant que le testeur n'a pas répondu ; aucun déploiement/publication déduit du GO BUILD.

## Priorité normative

Ce fichier complète et précise la proposition antérieure : base actuelle ci-dessus, option B désormais proposition unique, séquence exclusive explicite et pending local. Il remplace les mentions de choix A/B encore ouvert et de réconciliation ARCH non attribuée ; design/contrats n'ont pas d'autre changement. Aucune approbation n'est fabriquée.
