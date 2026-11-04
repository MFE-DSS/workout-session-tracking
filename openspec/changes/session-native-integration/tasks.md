# Tasks

## 1. Décisions

- [x] 1.1 D-MOB02-1=A et D-MOB02-2=AUREN-MARK-V1 seule acceptées le 2026-11-03 ; décisions consignées en annexe de `proposal.md` et `design.md`

## 2. Client

- [x] 2.1 Exécuter `python scripts/check_scope.py` dans le worktree et suivre les vérifications locales qu'il exige
- [x] 2.2 Journal complet et relecture au démarrage / statuts ; exécution et détail des séries accessible du vrai bilan : reçue / en attente / refusée / inconnue ; relance, retry, doublons et lectures tardives testés
- [x] 2.3 Envoi unique de « Démarrer » / « Reprendre » (état d'attente) ; test du double appui
- [x] 2.4 Textes de reprise : accord du pluriel, note hors ligne de la reprise serveur
- [x] 2.5 Écran de démarrage selon D-MOB02-2
- [x] 2.6 Substitution refusée / hors ligne : états explicites, exercice d'origine rendu sur refus
- [x] 2.7 Bilan : valeurs sourcées ou omises (D-MOB02-1) et ligne de contexte facultative à période explicite (D-MOB02-3)

## 3. Serveur (si D-MOB02-1 = a)

- [x] 3.1 `GET /api/mobile/v1/me/training-preferences` et `GET /api/mobile/v1/me/sessions` en lecture seule, isolés par `user_id`, avec tests
- [ ] 3.2 Déploiement du canonique en production avant la passe appareil

## 4. Revue et passe appareil

- [x] 4.1 Gate du contrat visuel 77/77 ; tout changement de composition montré en avant / après avant commit
- [ ] 4.2 Passe émulateur Android sur la production : relance après série acceptée, double appui, substitution refusée, hors ligne, bilan ; puis iPhone
- [x] 4.3 Rapport de sprint (§3, §5.2, quatre garde-fous du protocole UI) et ligne du registre ; PR

## Workflow follow-up

- Séquence arbitrée par l’opérateur le 2026-11-04 : mobile complet et revue visuelle → checks du HEAD complet → merge sous GO permanent → GO déploiement distinct → déploiement du canonique vérifié → recette Android puis iPhone connecté → closeout et archive après preuves.
- La fusion ne coche ni 3.2 ni 4.2. Selon le dernier mandat LAST MILE, préparer après merge les artefacts OpenSpec MOB-03 depuis MOB-00 ; aucune implémentation de sémantique ou surface nouvelle sans acceptation.
- Historique : refus du croquis de compteurs sous le bilan ; remplacé par D-MOB02-3 accepté et le détail progressif de 2.2, sans compteur permanent.
- Réponse suivante : « réfère toi à ma dernière prompt injection » ; la directive de finalisation D-MOB02-3 s’applique, avec sa ligne de contexte facultative, sans réintroduire l’ancien croquis de synchronisation. Rendu final à soumettre avant commit.

## LAST MILE — suivi d’exécution

D-MOB02-3 accepté fonctionnellement par le mandat opérateur, sans rouvrir sa sémantique.
2.2 est implémentée dans le vrai consommateur : le bouton existant du bilan ouvre la feuille canonique
des séries réalisées par exercice ; aucun compteur permanent. La géométrie candidate reste soumise
à l’unique acceptation visuelle de 4.1 avant commit UI.
Le mandat autorise explicitement l’ajout du seul état de détail normal/ouvert nécessaire à la planche des sept scénarios.
Le bilan fermé de ce scénario est identique au canonique octet pour octet en PNG.
La revue indépendante a signalé une course de substitution : reproduite rouge, corrigée par invalidation
des lectures traversant une nouvelle demande et sa persistance, puis suite mobile complète verte.
Les tâches déploiement / appareils restent ouvertes après merge jusqu’aux preuves effectives.

## Acceptation visuelle — 4 novembre 2026

L’opérateur a répondu exactement « ACCEPT — rendus MOB-02 complets » à la revue consolidée unique : sept scénarios corrigés, ligne D-MOB02-3 et détail des séries normal/ouvert par le bouton existant.
La gate CLAUDE.md §5.1 est satisfaite avant commit UI. Aucun nouveau baseline ni manifeste n’est créé ou approuvé automatiquement. Les fichiers mobiles sont identiques à ceux rendus et testés lors de la soumission.
Les décisions applicables §5.2 restent relues dans le tableau de ce rapport ; D-MOB02-1/2/3 respectées. Composition du bilan fermé conservée, détail secondaire accepté, données sourcées ou omises.
Le GO MERGE permanent reste actif ; publication complète dans #352 puis CI réelle sur son HEAD final. Deux tâches post-merge restent ouvertes : déploiement compatible 3.2 et recette Android/iPhone 4.2. Ne pas archiver avant leurs preuves.
