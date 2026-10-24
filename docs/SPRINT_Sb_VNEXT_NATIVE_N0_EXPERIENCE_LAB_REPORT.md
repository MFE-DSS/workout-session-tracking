# `Sb_VNEXT_NATIVE_N0_EXPERIENCE_LAB` — rapport

**Statut :** `N0 NATIVE EXPERIENCE GATE — OPERATOR DECISION REQUIRED`
**Branche :** `sb/vnext-native-n0-experience-lab` (worktree `workout-session-tracking-n0`), ouverte sur
`da1beb2` (gouvernance C2 acceptée), elle-même sur le canonique `7d34fa2`.
**Autorité :** `ADR_AUREN_VNEXT_01` **ACCEPTED — C2** (opérateur, 2026-10-23) ;
`Sx_AUREN_MOBILE_EXPERIENCE_VNEXT_SPEC §0quater, §9.4`.
**Non commité** : `CLAUDE.md §5.1` interdit tout commit d'interface avant l'exposition d'un
rendu réel à l'opérateur ; le rendu sur appareil n'a pas encore eu lieu (§6).

La question unique de N0 : *« Cette expérience est-elle si nettement meilleure que
l'opérateur veut abandonner l'interface de séance actuelle ? »* — elle ne se tranche que
sur un téléphone réel. Ce rapport livre l'application, ses preuves hors appareil, et la
liste exacte de ce qui reste à voir sur l'appareil.

---

## 1. Brainstorming / Options / Risques / Choix retenu (`CLAUDE.md §3`)

| Sujet | Options | Choix | Pourquoi |
|---|---|---|---|
| Navigation | Expo Router · état unique | **un état unique, pas de routeur** | la séance est un MODE : aucune destination, aucune pile, aucune décision de navigation (G-NAV) ; N0 ne construit que 5 états |
| Animations | Reanimated · `Animated` natif | **`Animated` (pilote natif)** | une transition par changement d'état, opacité + translation ; aucun module natif de plus pour N0 ; Reanimated reste ouvert si une mesure le réclame |
| Feuilles | bibliothèque tierce · `Modal` natif | **`Modal` `pageSheet` (iOS)** | c'est la feuille système d'iOS, sans dépendance |
| Persistance | AsyncStorage · Expo SQLite | **Expo SQLite, transaction EXCLUSIVE** | la série, sa commande et l'instantané de l'instrument doivent être durables **ensemble** ; la doc SDK 58 précise que seule la variante exclusive isole la transaction |
| Données | maquettes · fixtures générées | **fixtures générées par les services canoniques** | aucune valeur inventée ; script versionné, rejouable |
| Minuteur | compteur décrémenté · échéance | **échéance** (`deadlineMs`) | rendu, arrière-plan, verrouillage, redémarrage recalculent tous depuis elle |
| Heure d'une série | horloge murale · ancre + monotone | **ancre + temps monotone** (D11 amendé) | l'horloge murale n'est jamais seule autorité ; hors lien monotone ⇒ `estimated` |
| Typographie | police embarquée · police système | **système** (SF Pro / Roboto), chiffres tabulaires | rendu natif, texte dynamique gratuit, rien à charger |

**Risques identifiés avant d'écrire** : logique de domaine qui glisse dans le client
(parade : table de transitions suivie, test qui le prouve) ; perte silencieuse
(parade : commit transactionnel, état « non enregistrée » visible) ; labo non
représentatif (parade : historique semé réaliste, voir §3.2) ; captures web prises pour
une preuve d'appareil (parade : séparées et étiquetées, §6).

## 2. Ce qui est construit — `clients/mobile/`

| Élément | Fichier | Contrat |
|---|---|---|
| Machine à états | `src/domain/workout.ts` | `MISSION → SET → REST → SET → REST(exercice suivant) → … → COMPLETE` ; **suit** `plan.on_complete`, ne calcule jamais la position ; une substitution est une **demande** (`REQUIRES_SYNC`), jamais appliquée sur l'appareil |
| Minuteur | `src/domain/timer.ts` | échéance ; ±15 s borné (jamais sous « maintenant », plafond 10 min) ; affichage arrondi au-dessus |
| Heure d'exécution | `src/domain/performedAt.ts` | ancre serveur + monotone ; `estimated` hors lien ; bornes serveur reproduites pour le journal du labo |
| Journal + outbox | `src/storage/journal.ts` | Expo SQLite, WAL, `withExclusiveTransactionAsync` : **série + commande + instantané en une transaction** ; mesure du commit (G-LOCAL) |
| Restauration | `src/storage/outbox.ts` | après un arrêt forcé, **le journal gagne** sur l'instantané ; une série crue en attente mais absente du journal s'affiche **« non enregistrée »**, jamais en silence |
| Haptique | `src/native/feedback.ts` | 6 mots : cran (±) · série sûre (après commit) · fin de repos (fort, une fois) · exercice suivant (léger) · refus · échec ; réglages système respectés |
| Notification | `src/native/restNotification.ts` | locale, planifiée à VALIDER, replanifiée à ±15 s, annulée à PASSER ; **mesurée** (retard reçu − prévu), jamais vérité du minuteur, aucun privilège d'alarme exacte |
| Maintien d'écran | `App.tsx` | actif en `SET` / `REST` seulement |
| Écrans | `src/ui/*` | MISSION · EXECUTION (une composition par état) · COMPLETE · feuilles natives · journal du labo |
| Fixtures | `scripts/generate_fixtures.py` → `src/fixtures/lab_fixture.json` | services canoniques sur base jetable (§3) |

**Langage visuel « instrumentation athlétique »** : champ graphite, **une** voix chaude
(« à toi de jouer », une seule action pleine par écran), **une** voix froide (ce qu'AUREN
calcule, et le temps), chiffres tabulaires larges, action souveraine toujours au même
endroit sous le pouce (68 pt). Pendant le repos, plus d'ambre : l'action devient un
trait — ce n'est pas au pratiquant de jouer.

## 3. Données — sorties canoniques, pas invention

### 3.1 Ce que V3 a réellement servi

Sur l'historique semé, la recommandation servie est **« Rattrapage épaules »**, raison
**« Jamais fait. »**, puis « Deltoïdes latéraux, Deltoïdes postérieurs : servi moins que
la moyenne sur 14 derniers jours. » et « Zones récupérées. » ; alternatives Push B
(« Jamais fait. ») et Push A. C'est l'écran MISSION tel quel.

### 3.2 Deux corrections de représentativité, faites sur le SEMIS, jamais sur le moteur

1. **Tout semé « maintenant » ⇒ V3 propose le cardio**, à juste titre : toutes les zones
   paraissent non récupérées. L'historique est étalé sur 15 jours (J-15 … J-2).
2. **Toutes les charges égales (47,5 kg partout, élévations latérales comprises)** ne
   décrivent aucun utilisateur : charges de départ réalistes par exercice (données
   d'utilisateur semées, pas des sorties du moteur), +5 %/semaine.

### 3.3 Les deux chemins exposés

- **Première fois** (séance servie) : guidage « Première fois sur cet exercice », aucune
  charge proposée, l'action devient « Indique la charge ».
- **Pratiquant de retour** (alternative Push A, choisie depuis la feuille « Pourquoi ») :
  guidage réel (« Consolider la charge actuelle · 52,5 kg · 6–10 reps », « viser 10 reps
  avant d'augmenter la charge »), « La dernière fois · il y a 1 sem · 52,5 kg × 11 · 10 · 9 ».

**Une règle d'affichage ajoutée** : les reps pré-remplies ne descendent jamais sous la
cible basse du moteur (`target_reps_min`) — pré-remplir 11 quand le guidage dit « viser au
moins 12 » ferait se contredire l'écran. C'est une lecture de la sortie du moteur, pas une
règle d'entraînement.

## 4. Vérifications hors appareil

| Vérification | Résultat |
|---|---|
| `tsc --noEmit` (strict) | ✅ 0 erreur |
| Tests unitaires (Jest, `jest-expo`) | ✅ **34 / 34** — dont : la table de transitions est suivie même quand elle saute là où l'appareil ne pourrait pas le déduire ; une séance nominale entière (21 séries) se fait sans aucun événement de navigation ; la substitution ne modifie pas le plan local ; l'horloge murale déplacée ne déplace pas l'heure d'exécution ; après arrêt forcé le journal gagne et une série absente s'affiche « non enregistrée » |
| `check_scope` | `ISOLATED` (39 fichiers neufs, rien d'importé ailleurs) |
| `ruff` sur le script Python neuf · budget ruff · `check_spec_protocol` | ✅ · ✅ 264 ≤ 548 · ✅ |
| Balayage ciblé | aucun test ni étape CI ne parcourt la racine du dépôt ni ne cherche `package.json`/`node_modules` ; Sonar ne scanne que `app/` |
| Contraste de la palette (couples sur fond réel) | ✅ texte ≥ **5,40:1** partout, signal 9,50:1, plaques ≥ 1,15:1 ; `REST` vs `WORK` = 1,04:1 ⇒ l'état est porté par la **composition** (anneau, compte à rebours, libellé), jamais la couleur seule |
| **Aperçu web** 390 × 844 @3x, parcours complet piloté (Playwright) | aucun débordement horizontal ; **0** cible < 44 pt ; **1** action souveraine par état, au même endroit (y 764–832, 68 pt) ; rien de nécessaire sous le pli ; 0 erreur de page ; identique sous « réduire les animations » |

⚠ **L'aperçu web n'est pas une preuve d'appareil.** Il valide la hiérarchie, la
composition et la machine à états de bout en bout. Il ne prouve rien sur l'haptique, les
notifications, la durabilité SQLite (le web utilise un journal **en mémoire**,
`journal.web.ts`), le cycle de vie, le texte dynamique ou la fluidité native.

## 5. Relecture des relevés de décisions (`CLAUDE.md §5.2`)

| Décision | Verdict |
|---|---|
| `DESIGN_DECISIONS_HOME_UIV2` **D2** — aucune revendication « IA » | **respectée** (« validé par AUREN », jamais « IA ») |
| `DESIGN_DECISIONS_HOME_UIV2` **D9** — pas d'anticipation | **respectée** (aucune séance future, aucune durée estimée) |
| `DESIGN_DECISIONS_HOME_UIV2` D1, D3–D8 | **non concernées** (accueil web ; `LEGACY_VISUAL_REFERENCE` pour le mobile) |
| `DESIGN_DECISIONS_UIV2_SURFACES` **Q4** — la ligne de série est un instrument | **respectée** (pastilles S1–S3 : ✓ / ● / ○, forme + texte) |
| `DESIGN_DECISIONS_UIV2_SURFACES` — une seule action souveraine par écran | **respectée** (mesuré : 1 par état) |
| `DESIGN_DECISIONS_UIV2_SURFACES` Q5–Q8 | **non concernées** (supersédées pour le mobile) |
| `AUREN_VISUAL_BACKBONE` — invariants retenus (cible 44, aucun état par la couleur seule, contraste de couple, aucune revendication d'activation, validation explicite) | **respectés** |
| `AUREN_INSTRUMENTS §6.2bis-3` — aucune durée estimée | **respectée** (`duration_estimate: null` testé) |
| D7 — vocabulaire | **respecté** (« 90 s par défaut », jamais « repli ») |

## 5bis. Durcissement — `PHYSICAL_DEVICE_GATE` (indépendant de la plateforme)

Raffinement du 2026-10-23, sans reconstruire N0 ni toucher à C2.

| Élément | Ce qui est livré |
|---|---|
| **Une porte, pas une porte iPhone** | `PHYSICAL_DEVICE_GATE` : même checklist, même record de preuve, mêmes seuils sur iOS et Android. Une exécution iOS ne valide jamais Android ; un simulateur/émulateur ne compte jamais (`physical: false`) |
| **Exécuteur unifié** | `npm --prefix clients/mobile run device` (`scripts/device.mjs`, sans dépendance). Découvre les appareils (CoreDevice pour iOS, `adb` pour Android, simulateurs listés mais jamais retenus), **préfère le physique**, sélection automatique s'il y en a un, choix s'il y en a plusieurs, rapport des prérequis s'il n'y en a aucun. `--check` et `--json` : préflight en lecture seule. Il **diagnostique** ; Expo **construit** (`expo run:ios --device <udid>` / `expo run:android --device <nom>`). Rien de câblé en dur (ni nom, ni UDID, ni version) |
| **Verdict de Xcode lui-même** | l'exécuteur lit `xcodebuild -showdestinations` (lecture seule) : composant de plateforme manquant et refus d'un appareil précis remontent avec la raison exacte de Xcode, en **une** action |
| **Adaptateurs natifs** | `Platform.*` n'apparaît plus que dans `src/native/*` (`platformUi`, `restNotification`, `feedback`, `deviceInfo`). **Zéro** dans `src/domain/`, **zéro** dans les écrans, **zéro** dans `App.tsx` (vérifié par recherche). Nouveaux adaptateurs : `keepAwake`, `platformUi` (feuille native + polices), `deviceInfo` ; `restNotification` exposé comme un service |
| **Record de preuve commun** | `src/lab/evidence.ts`, schéma `auren.n0.physical-device-evidence/1`, documenté dans `clients/mobile/DEVICE_EVIDENCE.md`, exporté depuis l'app (⋯ → Journal du labo → Exporter la preuve). Champs mesurés automatiquement, observations opérateur à `null` jusqu'à saisie. 6 tests prouvent : forme identique iOS/Android, simulateur jamais compté, `cross_platform: false`, rien de deviné |
| **Instrumentation ajoutée** | séries validées, enchaînements automatiques (série / exercice), sauts de repos, décisions de navigation (feuilles secondaires ouvertes), retard de détection de fin de repos (premier plan / retour), notifications demandées, séries restaurées après relance |
| **Expo Go** | rétrogradé en **aperçu rapide** seulement — jamais une preuve de porte |
| **Dépendances** | `expo-device`, `expo-constants` (déclaré explicitement, n'était que transitif), `expo-system-ui` (fond sombre natif dès le lancement) — versions exactes, `expo install --check` : à jour |
| **Projet natif iOS** | `expo prebuild --platform ios` + CocoaPods : ✅ (`ios/` ignoré par git) |

**Tests :** 40 / 40 (34 + 6 du schéma de preuve). **Typecheck :** ✅.

## 6. La porte d'appareil — OUVERTE

`IOS PHYSICAL GATE` : build de développement installé sur l'iPhone de l'opérateur (signature
équipe personnelle, aucun identifiant dans le dépôt), **premier essai en main fait le
2026-10-23** (§6bis). `ANDROID PHYSICAL GATE: OPEN — NO DEVICE AVAILABLE`. Le mode d'emploi
est dans `clients/mobile/README.md`. Les mesures ci-dessous restent ouvertes tant que la preuve
JSON exportée de l'appareil ne les a pas remplies.

| À mesurer sur appareil | État |
|---|---|
| portée du pouce · lisibilité en salle · zones sûres | ⏳ ouvert |
| clavier (toucher une valeur) | ⏳ ouvert |
| sensation haptique (6 mots) | ⏳ ouvert |
| sensation des transitions, 60 / 120 Hz | ⏳ ouvert |
| minuteur : premier plan, arrière-plan, écran verrouillé, reprise (≤ 1 s) | ⏳ ouvert |
| **preuve d'arrêt forcé** : série présente après réouverture | ⏳ ouvert — la logique est testée, la durabilité réelle ne l'est que sur appareil |
| G-VAL (appui → repos peint) · G-LOCAL (commit) | ⏳ instrumentés, non mesurés |
| distribution de livraison des notifications (médiane / p95 / pire) | ⏳ instrumentée, non mesurée |
| grand texte · réduire les animations | ⏳ ouvert (aperçu web seulement) |
| **Android physique** | ⏳ **ouvert** — aucun appareil ; ne sera pas déclaré fermé par simulateur |

## 6bis. Premier essai physique (iPhone, 2026-10-23) — retours opérateur

**Ce qui est compris sans aide** : la mission et son action, « Série 1 sur 3 », la fourchette
« 8 à 12 reps », « Première fois sur cet exercice », le repos et son saut, le report
automatique de la charge à la série 2, l'exercice suivant (élévation latérale câble), la
remplaçabilité (« machine prise / remplacer »), « Commencer maintenant ».

**Défaut bloquant constaté — « non enregistrée » au passage à l'exercice suivant.** Pour un
outil dont la règle première est *aucune série perdue en silence*, c'est le défaut le plus
grave de l'essai. La série n'a pas été perdue en silence : l'écran l'a dit, et c'est le
comportement voulu en cas d'échec. Mais l'échec n'aurait pas dû se produire.
- **Cause probable, NON confirmée par un journal d'appareil** (Metro n'a remonté aucune ligne
  pendant l'essai) : `withExclusiveTransactionAsync` ouvre sa propre connexion SQLite ; au
  même instant, l'app écrivait une métrique du labo (`SET-VALIDATED`, `NOTIF-REQUESTED`) et
  l'instantané de séance sur la connexion principale. SQLite refuse alors l'un des écrivains.
- **Correction** : toutes les écritures du journal passent par une file unique
  (`src/storage/serial.ts`, testée), `busy_timeout` de 2 s, nouvel essai borné du commit
  (rendu idempotent : `INSERT OR IGNORE` sur la commande d'outbox), et **l'erreur exacte est
  désormais journalisée** (`[N0] set commit failed` + métrique `COMMIT-FAILED`).
- **Fermeture** : seulement sur nouvel essai physique sans `COMMIT-FAILED` dans la preuve
  exportée. Si l'échec revient, le journal donne la vraie cause et l'hypothèse ci-dessus tombe.

**Itération de PRÉSENTATION — périmètre N0** (aucune règle métier nouvelle) :

| # | Retour | Traduction |
|---|---|---|
| P1 | « Push A pas centré », « pas cockpit, très textuel » | composition centrée de la mission et du titre d'exercice ; moins de prose, plus d'instrument |
| P2 | « Objectif 8 à 12 » compris, mais la cible précise manque | afficher la cible de la série (la valeur pré-remplie) à côté de la fourchette |
| P3 | silhouette du haut du corps zoomée sur les groupes ciblés, couleurs par zone d'intensité | réutiliser les plaques régionales existantes (BodyParts3D, `REGIONAL_PLATES`) ; **l'intensité = allocation de séries prévues, jamais une activation % / EMG** (invariant maintenu) |
| P4 | guide visuel d'exécution entre « première fois » et la charge : repères, consignes, pièges, état de l'art | afficher les consignes et pièges **déjà présents** dans le catalogue ; ce qui n'existe pas en donnée n'est pas inventé dans le labo |
| P5 | représentation visuelle du but de l'exercice | même source que P3 (zones ciblées), pas de nouvelle donnée |
| P6 | remplaçants classés par pertinence (direct / indirect) | afficher l'ordre, le niveau N1/N2/N3 et la raison que `substitution.compute_suggestions` **rend déjà** |

**Tranches MÉTIER — hors N0**, chacune son sprint, sa spec, ses tests :

| # | Retour | Où ça se joue |
|---|---|---|
| M1 | la charge d'une première fois n'est pas définie | proposition de charge à froid (absence d'historique) — moteur de surcharge |
| M2 | série 2/3 : charge normale ou dégressive ? | prescription par série (constante / dégressive) — moteur de surcharge |
| M3 | un remplaçant mécaniquement éloigné doit remodeler la suite de la séance | re-planification consciente des substitutions ; `adaptive_replan` existe et n'est branché nulle part |

**Preuve d'arrêt forcé — vue par l'opérateur** : séance fermée de force puis rouverte, les
séries validées sont toujours là. À confirmer par la preuve JSON exportée (absence de
`COMMIT-FAILED`, `RELAUNCH-RESTORED-SETS`).

**Second retour — SÉANCE TERMINÉE et accueil :**
- « Dans l'ensemble c'est bien », mais il **manque des infos** : les statistiques et
  validations de séance vues dans AUREN, et surtout **une gamification** — séries scorées, un
  score **pertinent** qui tienne compte de ce qui a été fait et de ce qui a été substitué.
- Accueil : la forme convient, mais l'app doit **revaloriser ce qu'AUREN calcule déjà**, en
  hyper-intuitif mobile.

**Défaut du labo trouvé en relisant l'écran** : « Séries par zone » affiche le relevé serveur
d'une séance du même gabarit **complétée par le générateur**, pas les séries réellement faites
sur l'appareil. À calculer depuis les séries validées de la séance en cours.

**Ce qui existe déjà** (inventaire du code, points décisifs relus à la main) :
- par exercice : `feedback.compute_success_score` → 100 / 80 / 50 (cible haute atteinte /
  fourchette / sous) — calculé **contre la cible de l'exercice prescrit**, donc injuste après
  une substitution (accepté par `SPIGNOS_EXERCISE_SUBSTITUTION_GRAPH_SPEC_FINAL` §9.7, contredit
  par `SPIGNOS_EXERCISE_SYSTEM_CONSOLIDATION_SPEC` §5.3, non construit) ;
- par séance : `quality_score.compute_session_quality` 0–100, alimente le classement
  (`/leaderboard`, points, grade A/B/C) mais **n'est pas affiché en fin de séance** ;
- relevé `session_recap.build_recap` : progression marquante, zones, anomalies, confiance —
  une partie seulement est rendue ;
- accueil : `home.build_home_payload` calcule dernière séance, semaine, état
  d'entraînement, plan hebdomadaire — **seules les raisons de la recommandation sont lues**.

**⚠ Conflit de spec — décision opérateur requise** (`CLAUDE.md §4`). La demande de score en
fin de séance contredit des décisions versionnées : `session_done.html` (« AUCUN SCORE
NUMÉRIQUE ICI, ET C'EST UNE DÉCISION »), `AUREN_UI_BLUEPRINT` D7 (« Pas de flamme. Pas de
streak. […] Une trajectoire, pas une mécanique de récompense »), `Sx_27` (pas de badges /
streaks, « option ultérieure si dogfood le réclame »), `Sx_UI_05`. La spec vNext ne tranche
pas. Ces décisions ne sont pas amendées en silence : le labo n'affiche aucun score tant que
l'opérateur n'a pas tranché.

**Tranché le même jour** : **D12** (score assumé + mécanique de récompense) et **D13**
(parcours de premier lancement + profil d'entrée), inscrits dans la spec `§0quinquies` et
l'ADR `§8`, avec marqueurs sur les décisions qu'elles renversent.

**Ce que D13 trouve dans le domaine** (inventaire, points décisifs relus à la main) :
- **aucun champ d'objectif** nulle part (modèle, enum, formulaire) ; `TrainingPreferences`
  porte des zones prioritaires, une cadence et le matériel — et le moteur servi ne lit que le
  matériel ;
- **aucun champ haut / bas / corps entier** : la famille se déduit du préfixe de slug ; les
  quatre gabarits haut / bas sont `archived` ; corps entier = `full-body-morphotype-priority-v1`
  (spécialisation) et `no-equipment-full-body` (utilitaire) ;
- **démarrage à froid** : V3 (servi) n'a pas de branche sans historique — à égalité partout, le
  départage par `display_order` sert `push-a` ; aucune charge de départ n'existe
  (`overload_engine` rend `target_weight_kg=None`) ;
- **aucun parcours d'accueil** : l'inscription redirige vers `/` ;
- **rotation de programme** : aucune ; la « rotation » est le classement V3 sur tout le
  catalogue.

**⚠ Défaut probable hors périmètre — à confirmer par un test, non corrigé ici** :
`recommendation._load_templates` (utilisé par V3) n'exclut que `archived`. Les gabarits publiés
par un utilisateur (`catalog_section="user"`, slug `up{user_id}-…`) entrent donc
vraisemblablement dans le vivier de **tous** les utilisateurs ; aucune exclusion trouvée dans
`recommendation_v3`, `recommendation`, `advice_memory`, `environment_activation`. Conséquence
possible : le programme d'un utilisateur recommandé à un autre. Non prouvé par exécution.

**Ordre proposé des tranches (`CLAUDE.md §5.5` — centralité d'abord)** :

| Ordre | Tranche | Nature |
|---|---|---|
| 1 | itération N0 : accueil (objectif → famille → profil → tutoriel → séance) et fin de séance scorée, **sur fixtures**, exposés sur l'iPhone | présentation, labo |
| 2 | spec + build : première séance sans historique — objectif × famille × matériel | métier |
| 3 | spec + build : score de séance qui explique, calculé sur l'exercice réellement fait, et mécanique de récompense | métier |
| 4 | spec + build : profil d'entrée (migration additive âge / sexe / activité / ancienneté, consentement) | métier, migration |
| 5 | charges de départ (lit le profil) · prescription par série (M2) | métier |
| 6 | rotation de programme · replanification après substitution (M3) | métier |

**Verdict de l'opérateur (2026-10-23)** : **`PROMISING — ITERATE N0`**, avec feu vert pour la
tranche 1. Arbitrages O1 / O2 / récompenses : spec `§0quinquies`.

## 6ter. Itération 1 — accueil (D13) et fin de séance scorée (D12)

**Brainstorming / Options / Risques / Choix retenu (`CLAUDE.md §3`)**

| | |
|---|---|
| Options — données de l'accueil | (a) séances écrites à la main par famille ; (b) **un vrai nouvel utilisateur par famille, sur les services canoniques** ; (c) attendre la tranche métier 2 |
| Choix | **(b)** : `generate_fixtures.py` crée trois utilisateurs vides ; première séance = premier gabarit de la famille **dans l'ordre de V3** (hors utilitaires) ; séance suivante = ce que V3 + mémoire proposent **une fois la première faite**. Rien n'est inventé ; le vrai choix objectif × famille × matériel reste la tranche 2 |
| Options — score | (a) afficher `quality_score` existant ; (b) **un score en trois parts lisibles** (volume 40, cibles 40, progression 20) sur l'échelle de `compute_success_score` ; (c) une note unique opaque |
| Choix | **(b)** — chaque point dit quel fait l'a produit ; un exercice remplacé est jugé sur ce qui a été fait (ni la cible ni l'historique de l'exercice prescrit) ; un record n'est annoncé que s'il bat le meilleur **enregistré** (même gabarit, même code — portée de `last_time_by_exercise_code`) |
| Risques | score « gratuit » à la première séance (progression = repères posés, 20/20) — **assumé** pour l'accueil, à rejuger en tranche 3 ; un objectif choisi qui **ne change encore rien** à la proposition ; formule de labo calculée sur l'appareil, alors qu'en produit le serveur calcule (D3) |

**Construit** (non commité, `§5.1`) : `OnboardingFlow` (promesse → objectif → famille → profil
passable, chaque champ dit pourquoi → proposition), `Tutorial` (4 étapes sur la première série,
passable, une fois), `CompleteScreen` refait (anneau de score animé — coupé sous « réduire les
animations » —, trois parts, records / premiers repères, niveau, semaine, série active, séries
par zone **réellement faites**, séance suivante préparée), MISSION centrée, mot haptique
`reward`, profil / persona / séances dans `lab_kv` (SQLite), `commit_failures` dans la preuve.
Tests : 59 verts (score, progression, profil, persona sur la vraie fixture), typecheck propre.
Rendu web vérifié écran par écran (19 captures, 0 débordement, 0 cible < 44 pt).

**Constats livrés par les données canoniques — à trancher, non corrigés ici :**
- après une première séance **haut du corps**, V3 envoie le nouvel utilisateur au **cardio +
  abdos** (« La modalité la plus délaissée ») ; idem après le **corps entier** ;
- le gabarit `full-body-morphotype-priority-v1` n'a, pour V3, **qu'une zone primaire :
  « Mollets »**, alors que ses exercices couvrent six zones — défaut de dérivation des zones
  du gabarit ;
- deux vocabulaires de zones cohabitent (« Chaîne postérieure » du relevé, « Ischios /
  Fessiers » de `muscle_mapping`) ; le labo n'emploie que celui du relevé.

**Limite de labo connue** : après la **deuxième** séance du nouvel utilisateur, la fixture n'a
pas de troisième proposition ; la deuxième est remontrée.

## 6quater. Dogfooding opérateur sur iPhone (2026-10-24) — retours, en cours

**Préparation.** Les données du labo ont été régénérées par le **moteur de production** (`ff4239d`,
D14 compris), en exécutant le générateur dans un worktree jetable au SHA déployé. Mission du jour :
inchangée (« Rattrapage épaules »). En revanche, la séance suivante du parcours « corps entier »
devient « Tout le reste récupère encore : séance cardio », c'est-à-dire le plan B de D14. 64 tests
du labo sont verts. L'ancienne version est sauvegardée hors dépôt.

### Validé (on garde)

- **Le front plaît.** Les composants sont jugés intéressants, et le cockpit d'entraînement est
  « bien ».
- **Promesse d'accueil** : « Choisis ta première séance et fais-la normalement. »
- **Objectifs** : prendre du muscle, gagner en force, sécher sans perdre de muscle, se mettre en
  forme.
- **Profil** : taille, poids, année de naissance, sexe, niveau, activité, séances par semaine. Le
  parcours est fluide.
- **Écran de série** : la progression en haut, la série au centre, **une seule action en bas**, les
  options en haut à droite.

### À changer (retours opérateur)

| # | Sujet | Retour | Nature |
|---|---|---|---|
| R1 | Marque | Logo et nom « AUREN » à rendre **plus futuristes** | DA |
| R2 | Accueil | Le fond est **statique** : il faut **du mouvement** qui montre visuellement les liens et « l'intelligence ». Les trois points actuels sont à repenser dans ce sens. | DA + UI |
| R3 | Discours « IA » | Renforcer le discours, sans excès : l'IA analyse **toutes** tes séries, génère la **séance suivante optimale**, et analyse ta progression séance après séance jusqu'à ton plein potentiel. Le dire **partout où la donnée est réutilisée**. | copie — **voir point ouvert O1** |
| R4 | Choix de la première séance | « 7 séances au choix », « 2 », « 1 » ne parle pas. Il faut **montrer ce que sont ces séances**, avec un peu de terminologie technique : haut du corps (pectoraux, deltoïdes latéraux, dos largeur, dos épaisseur…), bas du corps (chaîne postérieure, antérieure…), corps entier (full body). On doit comprendre **ce que chaque séance cible**. | UI + DA |
| R5 | Texte et image | **Tout texte qui désigne un muscle ou un exercice est couplé à une image.** C'est l'état de l'art ; à inscrire au cahier du designer. Des assets existent déjà (`Sx_ASSET_*`, BodyMap, Muscle Focus). | DA, règle transversale |
| R6 | « Première fois sur cet exercice » | Dire que cette charge devient la **référence** sur laquelle s'appuieront les estimations suivantes. | copie |
| R7 | Écran de série | Il reste **de l'espace libre** entre l'en-tête et la saisie charge/répétitions. On y valorise les **assets d'exécution** déjà produits mais non utilisés : bonne et mauvaise exécution, consignes, erreurs fréquentes, zoom sur l'exercice. | UI + DA |
| R8 | Remplacer un exercice | Ne plus le cacher dans les « trois points ». Une **icône dédiée** à droite du nom de l'exercice (flèches de substitution), disponible **à chaque série**, avec des propositions **cohérentes** (moteur de substitution N1→N3). | UI |
| R9 | « Journal local du labo » | C'est l'**instrumentation du labo** (journal SQLite et export de preuve JSON), pas un écran produit. À retirer du menu utilisateur, ou à garder derrière un mode développeur. L'opérateur y voit peut-être « un asset à valoriser plus tard », par exemple un historique ou un export de ses données. | décision |
| R10 | **Passer ou annuler une série** (« très important ») | Sous « Valider la série », une action **secondaire**, en gris, placée pour **ne pas être touchée par erreur**, qui passe la série en cours. **Mesuré : absente aujourd'hui.** Seuls « Passer le repos » et « Commencer maintenant » existent. À trancher : la série passée est-elle *non faite* (elle sort du volume) ou *annulée* ? La sémantique produit actuelle est que série non validée = série non faite. | UI + règle |
| R11 | Liste de remplacement **classée par cohérence** | Tri du plus logique au moins logique, avec un **code couleur de fond** : du vert (vrai remplacement) à l'orange (remplacement approximatif). **Mesuré : la liste du labo n'affiche aucun niveau.** Le moteur de substitution en possède pourtant trois : N1 curé, N2 même schéma et même zone, N3 « élargi, intention proche ». Les couleurs doivent être des **tokens mesurés** (CLAUDE.md §5.4) et **jamais le seul porteur du sens** : un libellé de niveau les accompagne, pour l'accessibilité. | UI + DA |
| R12 | **Passer un exercice entier** | Pouvoir sauter toute la carte d'un exercice, au-delà de la série en cours. **Mesuré : absent aujourd'hui.** La place est à concevoir avec R8, la même icône d'action d'exercice. | UI |
| R13 | Bilan de séance : **lecture de la performance par ligne** | Le bilan « Push A » est **validé**, « premier repère posé » compris. Chaque ligne d'exercice gagne un code couleur ou une animation selon la performance : **au-dessus** (« ce qu'il a déchiré »), **conforme** à la prescription, **en dessous** (« plus lazy »). Les couleurs sont des tokens mesurés, toujours doublées d'un libellé. À la première séance, la ligne reste « repère posé », sans jugement. | UI + DA |
| R14 | Raison de la séance suivante **après une première séance** | « Le moins servi sur les 14 derniers jours » sonne creux quand il n'existe qu'une séance. Garder la phrase est acceptable (opérateur : « pourquoi pas »), mais une formulation adaptée au **démarrage** serait plus juste, par exemple « on équilibre ta semaine : tu viens de faire le haut, place au dos ». | copie, mineur |
| R15 | Bloc « l'IA AUREN a préparé ta prochaine séance » (Pull B : dos épaisseur, biceps) et « Voir ma prochaine séance » | **Validé**, le bouton existe déjà. | — |
| **R16** | **Quitter la séance — BLOQUANT** | Pendant une séance, par exemple « exercice 1/7 en cours », l'utilisateur est **enfermé** : il ne peut ni terminer plus tôt, ni mettre en pause, ni sortir. **Mesuré : le menu ne contient que « Remplacer cet exercice » et « Journal local du labo ».** Il faut une sortie **systématique, toujours au même endroit**, qui distingue trois issues : **terminer maintenant** (bilan de ce qui a été fait), **mettre en pause et reprendre plus tard** (l'état est déjà conservé sur l'appareil, il survit à la fermeture de l'app), **abandonner**. Elle passe par une confirmation, pour éviter la sortie par erreur. Les issues sont à aligner sur les états de séance du produit servi. | UI + règle, **priorité 1** |

### Verdict opérateur (2026-10-24)

« Ça a l'air pas mal dans l'ensemble. » **Le modèle du labo est conservé, et on itère.** L'axe
d'itération désigné : **valoriser le côté « IA » et l'interopérabilité de tout ce qui existe déjà**
(moteur, substitution, assets, historique), en le **montrant** à chaque endroit où une donnée est
réutilisée (voir O1).

**Non commentés pendant ce passage**, donc à observer au prochain : le minuteur de repos et sa
notification de fin, les vibrations, le maintien de l'écran allumé.

### Point ouvert à trancher par le product owner

- **O1 — vérité du mot « IA ».** Le moteur est **déterministe** : règles et calculs sur
  l'historique, aucun apprentissage automatique (`epistemic.py`, spec moteur V2). « Analyse chacune
  de tes séries et prépare la séance suivante » est **vrai**. « Intelligence artificielle » laisse
  entendre un modèle qui apprend. Pour un produit B2C vendu en France, un argument commercial qui ne
  correspond pas au produit expose au grief de pratique trompeuse. Deux voies cohérentes :
  - (a) un vocabulaire **exact et fort**, comme « intelligence d'entraînement » ou « ton coach
    analyse chacune de tes séries » ;
  - (b) **rendre le mot vrai**, par une brique réellement apprenante (par exemple un agent
    conversationnel ou un modèle de réponse), décidée comme une tranche à part entière.

### Cahier du designer (à fournir par l'opérateur)

Ce sont R1, R2, R4, R5 et R7. La règle transversale est que **tout texte qui désigne un muscle ou
un exercice a son image**. Les assets existants sont à revaloriser avant d'en commander de
nouveaux. La manière dont l'agent DA de l'opérateur livrera ses objets visuels reste à définir.

## 7. Écarts et dettes connus

- `npm audit` : 24 avis « high » dans l'outillage de développement transitif (`glob`,
  `inflight` dépréciés via Jest) ; non corrigés (`--force` casserait les versions alignées
  sur le SDK) — à revoir à la mise en CI mobile.
- `react-native-svg` : les props `rotation`/`origin` de l'anneau sont dépréciées — à
  remplacer par une transformation, sans effet visible aujourd'hui.
- Le cœur de rendu du SET garde un grand vide entre le guidage et les cadrans : choix de
  composition (cadrans et action sous le pouce) **à juger sur appareil**, pas une
  contrainte.
- `G-NAV` est prouvé en logique (test) ; sa preuve d'usage est le dogfood.

## 8. Non-goals tenus

Aucune auth, aucun jeton, aucune écriture serveur, aucune migration, aucune réécriture
recommandation / récupération / TRAIN A / surcharge, aucun Live Activity, aucun service de
premier plan Android, aucun store, aucun TestFlight, aucune navigation complète, aucun
BODY / LOADOUT / profil / social / chatbot. Aucun fichier de `app/` modifié.

## Verdict

**Verdict :** `N0 NATIVE EXPERIENCE GATE — OPERATOR DECISION REQUIRED`

Verdicts permis à l'opérateur, **après** l'avoir eue en main sur son téléphone :
`WOW — CONTINUE C2` · `PROMISING — ITERATE N0` · `NO MATERIAL UX GAIN — REASSESS ARCHITECTURE`.
Aucune intégration API ou auth ne démarre avant ce verdict.
