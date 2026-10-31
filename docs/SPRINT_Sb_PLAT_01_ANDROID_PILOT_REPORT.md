# Sb_PLAT_01_ANDROID_PILOT — un testeur Android sur le backend de production

**Date :** 2026-10-31
**Branche :** `sb/plat-01-android-pilot` (change OpenSpec `android-pilot-readiness`)
**Verdict :** voir la fin du rapport.

## 0. Commande et décisions de l'opérateur

- « Tu as quelqu'un qui doit utiliser Android dans quelques jours […] Il faut faire un Android Pilot Slice » : connexion,
  MISSION, séance, séries, repos, fin, bilan, même backend que l'iPhone ; vérifier safe areas, clavier, retour Android,
  cibles, BodyMap, icônes, polices, réseau, hors ligne / erreurs, performances. « Pas besoin de parité fonctionnelle
  totale. » « Do not create Android-specific redesigns. »
- Choix (2026-10-31) : backend = **déploiement du canonique sur `spignos.com`** ; build = **EAS Build** ; passe =
  **émulateur, puis le testeur** ; proposal relue avant apply.
- Proposal acceptée : « ok donc parfait continue sur ton critical path ». Correctif clavier accepté sur planche
  avant / après : « GO ».

## 1. Brainstorming · Options · Risques · Choix retenu (`CLAUDE.md §3`)

| Sujet | Options | Choix |
|---|---|---|
| Backend du pilote | tunnel depuis le Mac · **déploiement production** | production : le testeur n'est pas sur le réseau de l'opérateur ; données durables |
| Build | Gradle local · **EAS Build** | EAS : keystore géré, lien d'installation, aucun secret au dépôt |
| Retour matériel | un `BackHandler` par écran · **une décision pure, un abonnement** | une fonction testée (`backAction`) ; les écrans verrouillés n'apprennent pas la plateforme |
| Clavier | corriger d'avance · **mesurer, puis corriger** | mesuré : deux défauts réels ; correctif en un point (`platformUi`) |

**Risques et parades :** `auth_basic` nginx sur le vhost (→ smoke externe : 401 JSON `www-authenticate: Bearer`) ;
migration en production (→ additive, sauvegarde automatique) ; écart de rendu Android (→ mesuré sur émulateur,
montré, aucune baseline touchée) ; un émulateur n'est pas un téléphone (→ la checklist du testeur reste la preuve
physique, MESURÉ et RAPPORTÉ séparés).

## 2. Livré

- **Production** : `d6d2272` déployé (run `41227342844`, tag `deploy/prod/2026-10-31-1801-d6d2272`) — sauvegarde,
  migration `y6z1t7u8w19 → z7a2u8v9x20` (`device_sessions`) seule appliquée, smoke et dérive Alembic verts. Smoke
  externe : `GET /api/mobile/v1/mission` → 401 JSON `www-authenticate: Bearer` ; login invalide → `invalid_credentials`.
- **Retour matériel** (`src/native/backAction.ts` + test) : en série ou au repos, ouvre « Quitter la séance » (chemin de
  ✕) ; feuille ouverte → la ferme ; ailleurs → le système.
- **Identité d'appareil** (`src/native/deviceLabel.ts` + test) : `AUREN · <plateforme> · <modèle>` (≤ 64), plus de
  « iPhone AUREN » en dur.
- **Clavier** : `platformUi.keyboardAvoidance` (Android reçoit le `padding` d'iOS, l'affichage bord à bord d'Expo 58 ne
  redimensionne plus la fenêtre) ; consommé par la connexion, l'onboarding et la feuille dessinée. Connexion : marges
  dans une vue intérieure. Feuille : `keyboardShouldPersistTaps="handled"`, titre long qui passe à la ligne.
- **Distribution** : `eas.json` profil `pilot` (APK interne, autonome, `EXPO_PUBLIC_API_URL=https://spignos.com`),
  `android.versionCode = 1`, projet EAS `@grimais/auren-vnext-lab` (identifiants publics).

## Croquis validé

Aucune recomposition : les écrans verrouillés (`EXECUTION-SCREEN-V1`, `MISSION-SCREEN-V1`, `COMPLETE-SCREEN-V1`,
`BODYMAP-MIT-BODY-V1`) sont rendus tels quels. La référence de la connexion et de la feuille est leur rendu actuel ;
le seul changement visible est la position par rapport au clavier, validé sur la planche avant / après par
l'opérateur (« GO »).

## Inventaire — une information, une seule fois

| Élément | Information | Source (contrat de données) | Doublon ? |
|---|---|---|---|
| Bouton « Se connecter » | soumettre les identifiants | action locale → `POST /api/mobile/v1/auth/login` | non |
| Feuille « Charge (kg) » : champ | la charge saisie | état local de la série (`SET_VALUE`) | non — la valeur n'apparaît qu'une fois dans la feuille |
| Feuille : OK | confirmer la valeur | action locale | non |
| Titre de feuille | nom de l'exercice | `ExecutionPlan.exercises[].executed_name` | non |
| Feuille « Quitter la séance » (retour Android) | les 4 choix de sortie | `EXIT_OPTIONS` (existant) | non — même feuille que ✕ |

## Comparaison avec la référence validée

Planche : https://claude.ai/artifact/Mfi2zWvJJWeKDfFfa6V6kr — connexion clavier ouvert, saisie de charge, titre long,
connexion clavier fermé (contrôle : identique à l'origine). Gate du contrat visuel : **77 / 77 identiques au pixel**
avant et après les retouches (aucune baseline réapprouvée).

## Changement unique de l'itération

« La saisie reste au-dessus du clavier sur Android » — une seule règle (`keyboardAvoidance`), appliquée là où une
saisie existe. Les deux retouches de la feuille (un appui sur OK, titre qui passe à la ligne) sont sa conséquence
directe, mesurées dans la même passe.

## 3. Passe appareil — MESURÉ (émulateur Android 16, Pixel 7, 1080×2400 à 420 dpi, navigation gestuelle)

APK : build EAS `1736edfd` (commit `1c41519`) puis builds de mesure `e4ea2b92` et `d3903d0c` (correctif non committé).
Compte de test `auren-pilot-emu` créé par `/register` sur la production.

| Contrôle | Résultat |
|---|---|
| Installation APK, démarrage sans Metro | ✅ |
| Réseau → production, authentification | ✅ (touche « go » et bouton) |
| MISSION (compte neuf) | ✅ Push A, BodyMap 4 zones |
| Démarrage, permission de notification (Android 13+) | ✅ demandée au début de la séance |
| Séries, saisie, repos, exercice suivant | ✅ aucun débordement |
| Retour en série / au repos | ✅ « Quitter la séance », l'app reste |
| Retour sur feuille ouverte | ✅ la ferme, aucune commande |
| Retour sur la reprise → relance | ✅ système, puis reprise |
| Arrêt forcé (démarrage à froid) | ✅ « Séance en pause », séries gardées |
| Série hors ligne → réseau revenu | ✅ « 1 en attente », puis « enregistrée sur AUREN » |
| Notification de fin de repos | ✅ reçue |
| Bilan → MISSION suivante | ✅ séance close côté serveur ; Pull B proposé |
| Données effacées + reconnexion | ✅ la séance ouverte revient en reprise depuis le serveur |
| Clavier : connexion / saisie de charge | ❌ → ✅ après correctif (planche) |
| Étiquette de session d'appareil | ✅ `AUREN · android · <modèle>` |
| Navigation à trois boutons | ✅ tout tient au-dessus de la barre (la mise en page se resserre) ; la barre système est **claire** sur fond sombre — constat 7 |

## 4. Divergences iOS / Android consignées

Sortie de séance (ActionSheet iOS · feuille dessinée + retour matériel Android) ; retour hors séance (système) ;
notification de repos (sans alarme exacte, permission demandée au démarrage de séance sur Android 13+) ; polices
système ; étiquette d'appareil. Le clavier n'est **plus** une divergence : même `padding` sur les deux plateformes.

## 5. Constats hors périmètre (à traiter dans d'autres changes)

1. **Compte neuf** : MISSION affirme « Pectoraux, Deltoïdes latéraux : déjà bien servi sur 14 derniers jours »,
   étiqueté MESURÉ, sans aucune séance — affirmation non soutenue par les données (moteur de recommandation).
2. MISSION sur grand écran : avec 1–2 zones, vide sous « Démarrer » (comportement de la baseline verrouillée, amplifié
   à 914 dp).
3. « Démarrer » sans état d'attente pendant la requête (1–2 s).
4. Après relance, une série acquittée s'affiche « enregistrée sur l'appareil » ; le bilan dit « toutes sur l'appareil ».
5. « 1 séries faites » ; écran vide pendant le rafraîchissement du jeton au démarrage (BOOT).
6. Une session d'appareil orpheline de la sonde du 2026-10-31 (expire après 30 jours d'inactivité).
7. Navigation à trois boutons : la barre système est claire sur l'app sombre. Réglable dans `app.json`
   (`androidNavigationBar`), mais c'est un changement visible : à montrer à l'opérateur dans une tranche suivante.

## 6. Checklist du testeur (RAPPORTÉ — à rejouer sur son téléphone)

1. Créer son compte sur `https://spignos.com/register`. Aucune suppression de compte n'existe encore.
2. Autoriser l'installation d'applications de sources inconnues, installer l'APK du lien, l'ouvrir.
3. Se connecter ; vérifier que le bouton reste visible au-dessus du clavier.
4. Démarrer la séance proposée ; accepter les notifications.
5. Saisir une charge au clavier : la valeur et OK restent visibles, un appui sur OK suffit.
6. Valider des séries ; laisser le repos finir une fois avec l'app en arrière-plan (la notification arrive-t-elle ?).
7. Appuyer sur retour pendant une série : « Quitter la séance » doit s'ouvrir, l'app rester ouverte.
8. Fermer l'app de force en pleine séance, la rouvrir : la reprise doit s'afficher.
9. Passer en mode avion, valider une série, rétablir le réseau : la série doit passer à « enregistrée sur AUREN ».
10. Terminer, lire le bilan. Envoyer : modèle et version d'Android, captures, tout écran coupé ou recouvert.

## 7. Vérifications

- `check_scope` → ISOLATED ; jest 415 / 415 ; typecheck : seules les erreurs Playwright préexistantes (identiques
  sur le canonique) ; gardes Python touchant le client mobile vertes ; `openspec validate --strict` vert ; gate visuelle
  77 / 77.

## Verdict

**PLAT-01 PRÊT AU MERGE** — parcours pilote vert sur la production depuis Android 16 (émulateur), deux défauts de
clavier mesurés et corrigés avec l'accord de l'opérateur, aucune baseline modifiée. Restent : l'APK final sur le SHA
mergé, puis la checklist rejouée par le testeur sur son téléphone (preuve physique).
