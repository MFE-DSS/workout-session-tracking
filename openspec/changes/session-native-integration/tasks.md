# Tasks

## 1. Décisions

- [ ] 1.1 Obtenir D-MOB02-1 (bilan : lectures serveur ou report) et D-MOB02-2 (écran de démarrage) ; les consigner dans `design.md`

## 2. Client

- [ ] 2.1 Exécuter `python scripts/check_scope.py` dans le worktree et suivre les vérifications locales qu'il exige
- [ ] 2.2 `serverStateFromOutbox` (pure, jest) et relecture au démarrage + à chaque statut ; relance → « reçue par AUREN »
- [ ] 2.3 Envoi unique de « Démarrer » / « Reprendre » (état d'attente) ; test du double appui
- [ ] 2.4 Textes de reprise : accord du pluriel, note hors ligne de la reprise serveur
- [ ] 2.5 Écran de démarrage selon D-MOB02-2
- [ ] 2.6 Substitution refusée / hors ligne : états explicites, exercice d'origine rendu sur refus
- [ ] 2.7 Bilan : valeurs sourcées ou omises (selon D-MOB02-1)

## 3. Serveur (si D-MOB02-1 = a)

- [ ] 3.1 `GET /api/mobile/v1/me/training-preferences` et `GET /api/mobile/v1/me/sessions` en lecture seule, isolés par `user_id`, avec tests
- [ ] 3.2 Déploiement du canonique en production avant la passe appareil

## 4. Revue et passe appareil

- [ ] 4.1 Gate du contrat visuel 77/77 ; tout changement de composition montré en avant / après avant commit
- [ ] 4.2 Passe émulateur Android sur la production : relance après série acceptée, double appui, substitution refusée, hors ligne, bilan ; puis iPhone
- [ ] 4.3 Rapport de sprint (§3, §5.2, quatre garde-fous du protocole UI) et ligne du registre ; PR

## Workflow follow-up

- Archiver après merge ; MOB-03 (onboarding / compte) ensuite.
