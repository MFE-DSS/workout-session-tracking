# Passation d'agent — 2026-11-03 (fin de MOB-01)

Document de reprise pour l'agent qui continue le chemin critique d'AUREN. Il décrit l'état **vérifié** au
2026-11-03, les règles qui ne se négocient pas, les décisions de l'opérateur et la suite. En cas de doute entre ce
document et le dépôt, **le dépôt fait foi** : vérifier avec `git` avant d'agir.

## 1. Lire d'abord, dans cet ordre

1. `CLAUDE.md` — contrat d'exécution versionné, **prioritaire** : §1 `check_scope`, §2 CI / commit, §3 Brainstorming /
   Options / Risques / Choix dans chaque rapport, §4 livraison agentique (GO BUILD / GO MERGE, arrêts durs), §5
   contrat de livraison UI (rendu montré **avant** tout commit UI), §6 OpenSpec.
2. `openspec/config.yaml` — le contexte produit et les règles OpenSpec (proposal relue par l'opérateur avant apply,
   un change = une PR).
3. `docs/strategy/SPEC_REGISTRY.md` — l'état de chaque spec et change.
4. `docs/strategy/AUREN_VISUAL_CONTRACT.md` + `AUREN_VISUAL_BACKBONE.md` — avant toute surface.
5. `docs/strategy/AUREN_UI_ITERATION_PROTOCOL.md` — les quatre sections obligatoires d'un rapport de tranche UI
   (une garde CI les vérifie : `tests/test_ui_iteration_protocol.py`).
6. `openspec/specs/mobile/feature-migration-map/inventory.md` — le backlog natif (MOB-00).
7. `docs/strategy/AGENT_ONBOARDING_SPEC_DRIVEN.md` — pour un agent qui arrive sans mémoire : ordre des autorités de
   spec, carte des contrats de données et des tests, leçons déjà payées, ce qui manque au spec-driven.

## 2. Règles dures (rappel — le détail est dans `CLAUDE.md`)

- **Jamais** `pytest -n auto` ; **jamais** `scripts/run_ci_pytest.sh` sur le poste (il fait tomber la machine) ; sweep
  local = `scripts/run_local_sweep.sh`. La CI réelle est la source de vérité.
- **UI** : rendu réel (émulateur, simulateur, capture) **montré à l'opérateur avant tout commit** ; l'opérateur seul
  approuve une baseline (`visual-contract/run.sh approve` est une action d'opérateur).
- **Merge** : `gh pr merge <N> --merge --match-head-commit <SHA>` ; jamais squash, jamais `--admin`. Un merge
  autonome n'est permis que dans l'enveloppe « standing GO MERGE » (tranche commandée + CI verte + Sonar OK, findings
  corrigés jamais adjugés pour verdir).
- **Jamais** committer `AGENTS.md`. Migrations **additive-only**. Aucun secret au dépôt (dépôt public).
- **Domaine** : ne jamais inventer de bornes, charges, récupération, anatomie, scores ni recommandations.
- **Shell** (`CLAUDE.local.md`, fichier personnel de l'opérateur) : une commande atomique par appel, pas de `&&` /
  `|` / `;`, pas de `cd` (utiliser `git -C`, des chemins absolus).

## 3. État au 2026-11-03

**Canonique** : `claude/sprint-reporting-fitness-app-V7Qr6`, merge de MOB-01 = `8a21657` (+ cette clôture).

| Tranche | État |
|---|---|
| GOV-01 OpenSpec | ✅ mergée (#336, #338) |
| PLAT-01 pilote Android | ✅ mergée (#337, #340) ; prod `d6d2272` sert `/api/mobile/v1` ; change **non archivé** (après retour du testeur, en stand-by jusqu'à l'alpha) |
| MOB-00 inventaire web | ✅ mergée (#339, #341), archivée |
| MOB-01 coque native | ✅ mergée (#343, `8a21657`) ; change **non archivé** : reste la passe iPhone connectée (tâche 4.1b) |
| MOB-02 intégration de séance | 📝 proposal écrite, **en attente de relecture** — worktree `…-mob02`, branche `sb/mob-02-session-native-integration` |

**MOB-01 livré** : Expo Router + NativeTabs sous l'entrée actuelle ; 4 espaces (AUJOURD'HUI · PROGRAMMES · PROGRÈS ·
PROFIL) ; séance plein écran au-dessus ; `initialSpace` / `backInShell` purs et branchés ; icônes D4 jeu A
(`clients/mobile/assets/tabs/`, provenance + licence ISC Lucide). Rapport :
`docs/SPRINT_Sb_MOB_01_NATIVE_NAVIGATION_SHELL_REPORT.md`.

## 4. Décisions de l'opérateur à respecter

- **Produit** = app mobile téléchargeable ; toute nouvelle UI en mobile (`clients/mobile`), jamais en Jinja.
- **Stores** (2026-10-31) : finir les tranches natives du chemin critique, puis **alpha** Google Play + TestFlight,
  **bêta** la semaine suivante. Avant tout upload : décider l'**identifiant d'app définitif** (permanent dans les
  Stores ; aujourd'hui `dev.auren.vnext.lab`), **suppression de compte dans l'app** (exigence Store), politique de
  confidentialité, comptes Google Play / Apple Developer (créés par l'opérateur), mises à jour OTA (`expo-updates`).
- **Navigation** : D1 (4 espaces, séance plein écran, social sous PROFIL), D2 (barre système, icônes AUREN),
  D3 « Famille C » **rejetée**, D4 jeu A **acceptée** (la marque + 3 utilitaires simples). Spec amendée : *terminer ou
  abandonner ramène à la coque ; mettre en pause montre la reprise*.
- **MOB-00** : réinitialisation de mot de passe, contact, export, administration restent web ; le social migre.
- **Profil** : l'octogone = profil d'entraînement / allocation ; pas de « deltoïdes 62/100 » ; un exercice
  personnalisé n'a ni calibration ni substitution sans données.

## 5. Suite du chemin critique (dans l'ordre)

1. **MOB-02** : obtenir D-MOB02-1 (bilan : lectures serveur en lecture seule ou report) et D-MOB02-2 (écran de
   démarrage) → apply → passe émulateur (relance après série acceptée, double appui, substitution refusée, hors ligne)
   + iPhone → PR.
2. Passe iPhone de MOB-01 (4.1b) puis archive du change.
3. MOB-03 onboarding / compte (dont suppression de compte) → MOB-04 MISSION (corriger « déjà bien servi » sur un
   compte neuf) → MOB-05 Progrès / journal → MOB-06/07/08 programmes, constructeur, bibliothèque → MOB-09/10 salle,
   substitution → UX-LAB PROFILE → MOB-11 profil / octogone → MOB-12 récupération → BIZ-01 abonnement → PLAT-02/03 →
   bêta publique. Chaque change : proposal OpenSpec relue par l'opérateur avant apply.

## 6. Outils et environnement

- **EAS** : projet `@grimais/auren-vnext-lab`, `npx eas-cli@25.1.1` ; profil `pilot` = APK interne contre
  `https://spignos.com`. EAS construit l'arbre de travail, commité ou non. Un APK simple ne se met **pas** à jour seul.
- **Android** : SDK `/opt/homebrew/share/android-commandlinetools`, AVD `auren-pilot` (Pixel 7, Android 16) ;
  l'émulateur meurt si un build Xcode tourne en parallèle (16 Go) — un seul à la fois.
- **iOS** : `npm --prefix <wt>/clients/mobile run expo -- run:ios --device <udid>` (avec `LANG=en_US.UTF-8`). Le
  simulateur **n'accepte aucune saisie scriptée** ici (pas d'accessibilité pour `osascript`, deep links confirmés à la
  main) : la passe connectée se fait sur l'iPhone de l'opérateur.
- **Compte de test** de l'émulateur : `auren-pilot-emu` ; son mot de passe n'est **pas** dans le dépôt — le demander à
  l'opérateur ou en créer un nouveau par l'inscription web.
- **Gate visuelle** : `bash clients/mobile/visual-contract/run.sh test` (Docker, image épinglée) — 77 baselines.
- **OpenSpec** : CLI global 1.14.3 ; lancer depuis le worktree (`python3 -c "import os,subprocess,sys;
  os.chdir('<wt>'); …"`).

## 7. Pièges payés cher (à ne pas rejouer)

- **Le cwd de l'outil Bash est l'arbre PRINCIPAL**, et l'installation éditable épingle `app` dessus : un script lancé
  « depuis » un worktree mesure l'autre arbre. Toujours `os.chdir(<worktree>)` explicite.
- **Le venv local n'est pas le lock** (FastAPI 0.135 local contre 0.141 en CI) : une garde verte en local peut être
  rouge en CI ; vérifier avec un venv installé depuis `requirements.lock` en cas de doute.
- **Un rapport de tranche UI** doit porter les quatre sections du protocole d'itération (croquis, inventaire au gabarit
  exact, comparaison, changement unique) — sinon CI rouge.
- **`expo-symbols` tire `expo-font@58.0.11`** → crash dyld au lancement iOS ; `expo-font` est épinglé `58.0.9`.
- **Une nouvelle branche créée depuis `origin/<canonique>` en suit l'amont** : `git branch --unset-upstream` puis
  `git push -u origin <branche>`, sinon un `git push` nu viserait le canonique.
- **Une fonction pure testée mais non branchée est une garde qui ne garde rien** — vérifier qu'elle a un appelant.
- **L'app tutoie** (« Ton compte », « tu valides ») — tout texte nouveau aussi.

## 8. Worktrees de ce chantier

- `…-mob01` : branche mergée — nettoyable.
- `…-mob01-spike` (`spike/mob-01-router`) : jetable, **jamais poussé** — nettoyable.
- `…-mob02` : MOB-02 en cours.
- Ne pas toucher les autres worktrees sans demande de l'opérateur (sessions parallèles possibles).
