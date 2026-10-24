# `Sx_AUREN_MOBILE_EXPERIENCE_VNEXT` — réinitialisation délibérée de la couche de présentation

> **Statut :** `SPEC + LAB D'ARCHITECTURE` — **0 code de production · 0 migration ·
> 0 suppression d'UI héritée.** Rédigé le 2026-10-23 sur le canonique
> `7d34fa237e7744f8d070c76454fe2447f25dd3eb` (`origin/HEAD`, merge PR #267).
>
> **Décision d'architecture associée :** `docs/strategy/ADR_AUREN_VNEXT_01_PRESENTATION_ARCHITECTURE.md`
> (statut **`ACCEPTED — C2`**, arbitrage opérateur du 2026-10-23 — §0quater).
>
> **Cadres de référence :** `docs/assets/vnext/AUREN_VNEXT_REFERENCE_FRAMES.html`
> (source versionnée, autonome, sans dépendance) — statut
> **`VNEXT_INTERACTION_REFERENCE_FRAME`** depuis la révision r2 (§11.4) : ils
> gouvernent la hiérarchie, l'état, l'action souveraine, la géométrie de base ; ils
> **ne figent pas** la forme. Les rendus PNG **ne sont pas versionnés** :
> `tests/test_auren_muscle_focus_source_policy.py:125-138` interdit toute image sous
> `docs/` hors `docs/assets/uiv3/`, et cette exception « doit être rediscutée, pas
> élargie en silence ».
>
> **Révisions :**
> * **r1 (2026-10-23)** — critère : expérience immédiate **en minimisant
>   l'introduction d'une seconde plateforme**. Recommandation : option **B** (coquille
>   web TypeScript même origine).
> * **r2 (2026-10-23, re-arbitrage opérateur)** — **critère changé par l'opérateur** :
>   *maximiser la qualité de l'expérience d'APPLICATION MOBILE, même si cela impose
>   de quitter la pile de présentation historique.* Recommandation : option **C2**
>   (React Native + Expo, backend FastAPI). Ce qui change est consigné au **§0bis** ;
>   le raisonnement r1 reste lisible là où il a été écrit.
>
> **Verdict (§17) : `C2 ACCEPTED / SPEC GOVERNANCE UPDATED`** (2026-10-23).
> *(r2 était `ARCHITECTURE DECISION REQUIRED — C2 RECOMMENDED` ; l'opérateur a
> tranché A0 et D1–D11, avec amendements — §0quater.)* Tranche ouverte :
> `Sb_VNEXT_NATIVE_N0_EXPERIENCE_LAB`. Piste sécurité séparée :
> `Sx_SEC_A0_SESSION_TOKEN_INTEGRITY`.

**Règle d'écriture héritée d'`AUREN_INSTRUMENTS` :** aucun nombre, aucun « toutes »,
aucun « aucune » sans la ligne de code ou la mesure qui le prouve. Les affirmations
ci-dessous portent leur référence ; celles issues d'une exploration et non
revérifiées à la main sont marquées *(non revérifié)*.

---

## 0. Ce que l'opérateur doit trancher — onze décisions (r2), dans l'ordre de centralité

`CLAUDE.md §5.5` : la décision centrale et difficile passe devant la commode.

| # | Décision | Recommandation | Ce qu'elle lève / amende |
|---|---|---|---|
| **D1** | Architecture de présentation | ~~r1 : option B « framework-light », coquille web TS même origine~~ → **r2 : OPTION C2 — client mobile React Native + Expo + TypeScript (iOS + Android, une base de code), backend de domaine FastAPI.** Modules Swift/Kotlin ciblés **seulement** là où la plateforme apporte une valeur réelle (Live Activity, notification continue Android) | `Sx_UIV3_00A §9` (FastAPI+Jinja KEEP, HTML/CSS natif PRIMARY, **React Native REJECT**, Capacitor FUTURE GATE) — **décision figée 2026-08-18** |
| **D2** | Mode de rendu des surfaces vNext | Les surfaces vNext **ne sont plus SSR-fonctionnelles**. L'invariant « une écriture critique reste récupérable si le JS échoue » est **reformulé** : *aucune écriture d'entraînement n'est perdue en silence* (accusée par le serveur **ou** retenue localement et visiblement en attente), et la **surface héritée SSR reste le repli** sur la même séance | `AUREN_VISUAL_BACKBONE §5bis` · `Sx_UIV3_00 §10` (no-JS) · `tests/test_df_b_session_flow.py:66` · `tests/test_ui_cp8i_resilience_saisie.py:298` |
| **D3** | Canal d'écriture | Une commande JSON **par série** (`SET_COMPLETION_COMMAND`) — le danger qui justifiait l'interdiction (`test_df_b_session_flow.py:67-69`, « un mini-POST effacerait les autres ») est **déjà neutralisé** par `UI-CP2.0 F3` (`sessions.py:478-503`) | garde « aucun chemin de sauvegarde parallèle » |
| **D4** | Outillage de build | ~~r1 : `clients/mobile/` TS + bundler vers un chemin web~~ → **r2 : `clients/mobile/` = projet Expo / React Native / TypeScript, avec sa CI native** (typecheck, lint, tests unitaires sur chaque PR ; builds iOS/Android signés par un service de build cloud, distribution interne) | « zéro framework » (`tests/helpers.py:171`) : la garde ne scanne que `app/static/js/*.js` (`helpers.py:88-91`) et **reste vraie** — le client mobile ne livre rien dans `app/static/`. Ce n'est pas une évasion : le client n'est plus une page du produit web, et la levée est écrite (§16) |
| **D5** | Repos entre deux exercices | La dernière série d'un exercice ouvre un **REPOS dont le sujet est l'exercice suivant**, puis l'ouvre seule | `console_state.py:417-421` (« REST n'existe que s'il reste quelque chose à faire après ») · libellés figés `Sx_UIV3_02 §4` (`CONTINUER → E2`) |
| **D6** | Valeurs proposées dans la saisie | La saisie s'ouvre **pré-remplie** (cible du moteur de surcharge, sinon dernière série faite) ; **VALIDER confirme ce qui est affiché**. Aujourd'hui la cible n'est qu'un *placeholder*, jamais pré-remplie | sémantique de saisie `Sx_UIV3_02` · risque : journaliser la cible sans l'avoir faite (§14 R6) |
| **D7** | Durée de repos | **Aucune prescription inventée.** Le lab sert `REST_FALLBACK_SECONDS = 90` (`console_state.py:59`) **étiqueté comme repli**. Une prescription par exercice est une feature métier séparée | confirme `Sx_UIV3_04 §1bis C` — *ne lève rien*, fixe une limite |
| **D8** | Statut des références visuelles actuelles | Les rendus et captures déclarés canoniques deviennent **`LEGACY_VISUAL_REFERENCE`** par la table de supersession du §4, **pas** par suppression | `AUREN_UI_BLUEPRINT §2.3` · `Sx_UIV3_03 §6` · `SPRINT_UIV3_VISUAL_BASELINE_REPORT` · `scripts/visual_contract.py` |
| **D9** *(r2)* | Authentification mobile | **Adaptateur porteur de jeton** à côté du cookie : jeton d'accès **court** + jeton de rafraîchissement **rotatif et révocable côté serveur**, stocké dans le coffre de l'appareil (Keychain / Keystore). Identité `User` et propriété **inchangées**. Exige **une** migration **additive** (table de sessions d'appareil) dans une tranche dédiée — **pas dans cette mission** (§8.9) | `AUTH_SCOPE_MATRIX.md` · `SECURITY_BASELINE.md` · prérequis **A0** (§0ter) |
| **D10** *(r2)* | Comptes de services externes | L'opérateur ouvre et détient : compte développeur Apple, console Google Play, compte du service de build/distribution. **Aucun agent ne crée ni ne manipule ces identifiants** | `CLAUDE.md §4` (« credential de service externe requis » = arrêt dur) |
| **D11** *(r2)* | Horloge d'une série validée hors-ligne | La commande porte `performed_at` (heure de l'appareil corrigée du décalage serveur) ; le serveur l'**accepte bornée** (`started_at ≤ t ≤ now_serveur`, monotone par exercice), sinon il garde son heure. Sans cela, une série synchronisée en retard reçoit l'heure de **synchronisation** et fausse le repos dérivé, la durée réelle et le relevé | `UI-CP8R` : « l'horloge du client n'entre jamais dans cette écriture » (`sessions.py:452-455`) — **conflit trouvé par l'analyse C2** |

**Ce qui ne demande AUCUNE décision** (déjà tranché, réutilisé tel quel) : pas de
durée estimée pour une séance future (`AUREN_INSTRUMENTS §6.2bis-3`), pas de score
global de préparation (`§6.2bis-1`), `MIENS · CATALOGUE` sans `ACTIF` (`§6.2bis-4`),
consentement corporel (`§6.2bis-2`), cible tactile 44 px, `no-color-only-state`,
contraste comme contrat de couple, aucune revendication d'activation musculaire.

---

## 0bis. Re-arbitrage r2 — le critère a changé, pas les faits

**Changement de prémisse, de niveau opérateur, explicite :**

| | r1 | r2 |
|---|---|---|
| Critère d'optimisation | expérience immédiate **en minimisant une seconde plateforme** | **qualité maximale de l'expérience d'application mobile**, même au prix de quitter la pile de présentation historique |
| Poids de la conservation de pile | élevé | **faible** — le domaine reste un actif, la présentation n'est pas une contrainte |
| Poids du plafond UX et des capacités natives | moyen | **dominant** |

**Ce que r2 garde de r1, sans le rouvrir** (présumé valide faute de preuve contraire) :
`MISSION_READ_MODEL` · `EXECUTION_READ_MODEL` · une commande par fait
(`START_SESSION`, `SET_COMPLETION`, `REST_SKIP`, `SUBSTITUTE`) · autorité du domaine
côté serveur · `console_state` comme autorité de position · aucune logique de
domaine dans la présentation · machine `MISSION → EXECUTION → REST → NEXT` ·
écritures idempotentes · synchronisation en attente **visible** · migration
étrangleuse · parité legacy · cadres = propositions, jamais du code de production.

**Ce que r2 change :**

| Élément | r1 | r2 | Pourquoi |
|---|---|---|---|
| Client | page web TS même origine | **app React Native + Expo** (§7) | plafond UX, haptique iOS, notification locale, écran verrouillé — impossibles ou bridés sur web iOS (§12) |
| Persistance locale | IndexedDB | **Expo SQLite** : journal + outbox transactionnels (§8.7) | survit à la mort du processus ; transactions réelles ; une seule source locale |
| Auth | cookie même origine | **jetons porteurs, coffre de l'appareil** (§8.9, D9) | le cookie `samesite=strict` n'est pas un contrat robuste dans un client natif ; et A0 |
| Hors-ligne | file de requêtes | ~~séance entière exécutable hors-ligne après START~~ → **chemin nominal d'une séance déjà matérialisée exécutable hors-ligne** (§0quater) grâce à une **table de transitions fournie par le serveur** (§8.8) ; le reste en `REQUIRES_SYNC` | sans elle, le client devrait recalculer « série suivante / exercice suivant » — logique de domaine |
| Horodatage d'une série | heure serveur à la requête | `performed_at` borné (D11) | une synchro tardive fausserait repos, durée, relevé |
| Comptes externes | aucun | Apple / Google / build cloud (D10) | distribution native |
| Coquille `/x/*` | servie par FastAPI | **supprimée du plan** — le legacy web reste le repli | il n'y a plus de client web vNext |

**Trois conflits que B ne rencontrait pas, trouvés par l'analyse C2** : la position
hors-ligne (→ §8.8), l'horloge d'une série synchronisée en retard (→ D11), la
robustesse de l'authentification (→ D9 + A0). Aucun n'est bloquant ; chacun est
une décision écrite.

---

## 0ter. Condition préalable de sécurité **A0** — avant tout jeton mobile

L'audit du contrat d'authentification (exigé par le re-arbitrage) a mis au jour
**deux défauts du contrat de jeton de session actuel**, **démontrés au labo** le
2026-10-23 sur une base jetable, **en production aujourd'hui** et **indépendants
de vNext**.

Le dépôt étant **public**, leur mécanisme et leur reproduction ne sont **pas**
décrits ici ; ils ont été remis à l'opérateur hors document versionné.
Conformément à `CLAUDE.md §4` (« faille de sécurité » = arrêt dur), **rien n'a été
corrigé** dans cette mission.

**Conséquences pour cette spec :**

1. **A0 est une tranche de sécurité autonome**, prioritaire sur tout le programme
   vNext, à ouvrir sur décision opérateur — elle ne dépend d'aucune décision D1–D11.
2. **Aucun jeton mobile n'est émis** (D9) avant que A0 soit livré : un jeton
   d'appareil longue durée hériterait des deux défauts.
3. Le contrat D9 (§8.9) exige par construction : **usage typé vérifié à la
   lecture** (un jeton n'est accepté que pour l'usage pour lequel il a été émis) et
   **révocabilité côté serveur** (déconnexion, changement de mot de passe, perte
   d'appareil).

---

## 0quater. Arbitrage opérateur du 2026-10-23 — décisions, pas recommandations

**Ces décisions remplacent l'état d'arbitrage en attente du §0.** Le §0 reste
lisible comme l'instruction qui les a précédées.

| # | Verdict opérateur | Amendement porté par l'opérateur |
|---|---|---|
| **A0** | **ACCEPTED / P0** — piste sécurité indépendante | aucun jeton de rafraîchissement mobile avant la clôture de A0 ; le labo N0 avance **sans** authentification mobile |
| **D1** | **ACCEPTED** — React Native + Expo + FastAPI | C2 est l'architecture cible ; la pile FastAPI/Jinja n'est pas une contrainte du vNext |
| **D2** | **ACCEPTED** | invariant de remplacement : **AUCUNE ÉCRITURE D'ENTRAÎNEMENT NE PEUT ÊTRE PERDUE EN SILENCE** ; le web legacy est le repli pendant la migration |
| **D3** | **ACCEPTED** | une commande par fait ; une série = une commande dédiée, **jamais** la route actuelle d'enregistrement d'exercice entier |
| **D4** | **ACCEPTED** | `clients/mobile/` = projet Expo / React Native / TypeScript ; CI/build natifs autorisés |
| **D5** | **ACCEPTED** | après la dernière série : REPOS → ouverture automatique de l'exercice suivant ; aucun geste de navigation sur le chemin nominal |
| **D6** | **ACCEPTED POUR LE LABO / PAS FIGÉ COMME PRODUIT** | le dogfood réel **doit mesurer** la confirmation silencieuse (valeurs validées sans modification) avant d'en faire un invariant |
| **D7** | **ACCEPTED** | 90 s est une durée par défaut, pas une prescription ; **le vocabulaire d'ingénierie (« repli », « fallback ») ne s'affiche pas** — on écrit « 90 s par défaut » |
| **D8** | **ACCEPTED** | legacy → `LEGACY_VISUAL_REFERENCE` surface par surface ; cadres HTML → `VNEXT_INTERACTION_REFERENCE_FRAME` (hiérarchie et état, pas la forme native) |
| **D9** | **ACCEPTED APRÈS A0** | accès court + rafraîchissement rotatif révocable + stockage sécurisé sur l'appareil ; **ne pas implémenter avant la clôture de A0** |
| **D10** | **AMENDÉ** | les comptes Apple / Google / service de build **ne sont pas** des prérequis du premier labo local ; ils le deviennent avant la distribution signée, TestFlight / test interne Play, les stores, et toute capacité native qui exige ces identifiants. **L'administration de comptes ne bloque pas N0** |
| **D11** | **ACCEPTED AVEC AMENDEMENT D'INTÉGRITÉ** | **jamais l'horloge murale brute de l'appareil comme seule autorité** : ancre serveur + temps monotone + validation bornée + invariants d'ordre (§8.8bis) ; aucune décision d'authentification ou de sécurité ne dépend jamais d'une heure client |

**Amendements de portes et de vocabulaire, portés par le même arbitrage :**

1. **Notifications** — aucune exigence dure de délai sur une notification de l'OS
   (§10.2, G-NOTIF scindé : minuteur in-app = contrat dur ; notification OS =
   distribution mesurée et publiée ; Android inacceptable ⇒ tranche d'extension,
   **pas** de privilège d'alarme exacte pour satisfaire un chiffre de labo).
2. **Hors-ligne** — ~~« une séance démarrée s'exécute entièrement hors-ligne »~~ →
   **« LE CHEMIN NOMINAL D'UNE SÉANCE DÉJÀ MATÉRIALISÉE PEUT S'EXÉCUTER
   HORS-LIGNE »** : série courante → valider → repos → série suivante → exercice
   suivant → fin. Les mutations non nominales (substitution soumise à
   autorisation serveur, correction complexe, replanification, état divergent
   inconnu) passent en **`REQUIRES_SYNC` visible** au lieu de dupliquer le domaine
   sur l'appareil.

**Séparation des quatre natures de contrat** (exigée par l'arbitrage) :

| Nature | Ce qu'elle couvre | Où |
|---|---|---|
| `RETAINED DOMAIN INVARIANT` | autorité serveur du domaine et de l'historique ; console = autorité de position ; repos dérivé, jamais persisté comme état ; pas de durée estimée, pas de score de préparation, pas de prescription de repos inventée ; aucune revendication « IA » (D2 accueil) ni d'activation musculaire ; une commande par fait | §3.1, §8 |
| `RETAINED ACCESSIBILITY INVARIANT` | cible ≥ 44 points ; aucun état par la couleur seule ; contraste de couple sur fond réel ; mouvement réduit pleinement fonctionnel ; lecteur d'écran ; texte dynamique | §3.2, §10 |
| `LEGACY_VISUAL_REFERENCE` | rendus, captures, tokens, échelles, compositions du web | §4.3 (marqueurs posés le 2026-10-23) |
| `VNEXT MOBILE CONTRACT` | read models, commandes, plan de séance + table de transitions, journal/outbox, `REQUIRES_SYNC`, auth D9, mode séance sans navigation, langage haptique, portes sur appareil | §5, §7, §8, §10, §11.5–11.6 |

---

## 0quinquies. Arbitrage opérateur du 2026-10-23, après le premier essai physique N0 — D12, D13

Ces deux décisions viennent de l'opérateur, téléphone en main (rapport N0 §6bis). Elles
**renversent** des décisions versionnées antérieures, listées ci-dessous : ce n'est pas un
amendement silencieux.

| # | Verdict opérateur | Contenu |
|---|---|---|
| **D12** | **ACCEPTED — SCORE ASSUMÉ, COMPLÉTÉ PAR UNE MÉCANIQUE DE RÉCOMPENSE** | les séries sont **scorées** ; un **score de séance** est affiché et **explique** ce qui a été fait — c'est l'exigence première (« que le score explique bien les choses ») ; il tient compte de ce qui a été **fait** et de ce qui a été **substitué** ; la **gamification complète le score** : mécanique de récompense assumée, agent **expressif** dans l'expérience (mouvement, haptique, voix du produit), objectif d'usage répété ; concret avant tout |
| **D13** | **ACCEPTED — PARCOURS DE PREMIER LANCEMENT** | « Tu es sur le cockpit AUREN. Une seule chose à faire : choisir ta première séance » ; l'utilisateur choisit un **objectif** (les champs réels de la pratique) et une **famille** — haut du corps / bas du corps / corps entier — **jamais** un nom de gabarit (« Push A ») ; une séance est proposée depuis le catalogue existant, adaptée au matériel ; **un tutoriel court** avant de lancer (ce qui est à gauche, en bas, à droite) ; puis l'explication de ce qui suit : le moteur lit les séries et prépare la séance suivante, en rotation, pour une progression continue. C'est l'un des seuls moments où l'utilisateur choisit sa séance |

**D14 (opérateur, même jour) — la séance suivante se choisit par la récupération ; le cardio
est le plan B.** La plus logique est celle dont aucun muscle n'a été sollicité, puis celle où il
en reste le moins à récupérer ; chaque muscle a son temps de récupération ; cardio + abdos ne
vient que lorsque tous les autres groupes récupèrent. Mesure et règle :
`Sx_REC_ROLLOUT_01_RECOVERY_FIRST_SPEC` — un seul critère en cause (« modalité délaissée »).
**Requalifiée le même jour** après la revue scientifique : **règle produit provisoire** pour un
objectif muscle / force, pas une règle scientifique générale ; elle sera remplacée par la
répartition par objectif de `Sx_AUREN_SCIENTIFIC_ENGINE_V2_SPEC` (le cardio y est un stimulus de
premier rang pour la remise en forme).

**D13, précision du même jour** : la première séance se choisit **parmi les gabarits existants**
du catalogue — présentés par les muscles qu'ils travaillent, pas par leur nom.

**D13, amendement du même jour — le profil d'entrée.** Le récit d'accueil dit que l'utilisateur
n'a qu'à faire ses séances : AUREN gère la suite, séance après séance, jusqu'à son plein
potentiel. **Avant la première séance**, il renseigne son profil : taille, poids, âge, sexe,
activité quotidienne et les autres mesures biologiques qu'il connaît facilement. Ces données
entrent dans la chaîne (proposition de la première séance, charges de départ, lectures
corporelles) et vivent ensuite dans son profil.

État du domaine, relevé dans le code le 2026-10-23 :

| Donnée | Existe ? | Déjà consommée par |
|---|---|---|
| taille, poids | ✅ `users.height_cm`, `users.weight_kg` (+ `body_measurements`) | morphologie, registre corporel, surcharge |
| tour de taille, FC repos, tension | ✅ `users.waist_cm`, `resting_hr`, `bp_*` | lectures corporelles |
| mensurations (bras, cuisse, épaules, envergure…) | ✅ `body_measurements` | morphologie |
| âge | ❌ — `coach_report` prévoit `year_of_birth` (« column doesn't exist ») | personne ; `coach_inference` dit aujourd'hui à l'utilisateur « AUREN ne connaît ni ton âge ni ton état de santé » |
| sexe | ❌ | personne |
| activité quotidienne / professionnelle | ❌ | personne |
| ancienneté d'entraînement | ❌ | personne |

**Règles du profil d'entrée** (contrat, pas goût) :
1. **Chaque champ demandé a un consommateur nommé** — une donnée qu'aucun calcul ne lit
   n'est pas demandée. Un champ nouveau arrive **avec** le calcul qui le lit.
2. **Chaque champ dit pourquoi il est demandé**, en une ligne, au moment où il l'est.
3. **Tout est passable**, et l'utilisateur peut corriger ensuite. Un champ absent rend le
   calcul qui en dépend **moins précis et le dit** ; il ne bloque jamais la première séance.
4. Les champs nouveaux (âge, sexe, activité, ancienneté) sont une **migration additive** :
   tranche métier, `CLAUDE.md §2`.

**D12 — AMENDÉ le même jour par l'arbitrage scientifique (ruling 11 du moteur V2).** Le
**score unique /100 est retiré**. La mécanique de récompense reste, sans note : trois concepts
séparés — la trace de décision (interne, jamais une note pour l'utilisateur), la
**performance** (chaque exercice contre l'historique personnel comparable : progrès, repères,
records réels) et l'**assiduité** au programme convenu, repos prévu compris (semaines
tenues). Aucune récompense pour des séances ou séries en plus, le tonnage ou un entraînement
pendant un repos prévu. Le labo N0 applique cet amendement ; la liste ci-dessous reste vraie
pour la part « gamification ».

**Ce que D12 superséde, pour le vNext** (le web legacy garde son état jusqu'à sa bascule) :
`AUREN_UI_BLUEPRINT` D7 (« Pas de flamme. Pas de streak. […] pas une mécanique de
récompense ») · `Sx_27` (« Pas de gamification type badges/streaks ») · `Sx_UI_05`
(« pas de badges/streaks gamifiés ») · `app/templates/session_done.html` (« AUCUN SCORE
NUMÉRIQUE ICI ») · le non-goal « aucun **score global** » du §15 de cette spec.

**Ce que D12 ne superséde PAS** : le **score de préparation** reste interdit (§11.6) — un
score de séance mesure ce qui a été fait, un score de préparation prétendrait mesurer le
corps. Aucune revendication d'activation musculaire.

**Une raison du retrait d'origine est conservée, parce qu'elle était juste** : « Qualité 92 »
et « Fiabilité 90 » cohabitaient sans que rien ne dise ce qu'ils décidaient. D'où, pour D12 :
**un** score de séance, dont **chaque point se lit** (quel fait l'a produit) — jamais deux
nombres concurrents sans explication.

**Arbitrage des points ouverts (opérateur, 2026-10-23, même jour)** :

| # | Verdict opérateur | Note de l'agent |
|---|---|---|
| O1 | **marketer AUREN comme une intelligence artificielle** — produit B2C, grand public, pratiquants de musculation en France | aujourd'hui l'allégation est **inexacte** : moteur déterministe, zéro ML ; risque d'allégation trompeuse auprès de consommateurs, et un système fondé sur des règles écrites par des humains est, sous réserve, hors de la définition de l'AI Act (considérant 12) — à faire valider. **Chemin qui la rend vraie** : tranche « agent IA », voix de l'agent (réactions, explications, compte-rendu) produite par un modèle de langage **ancré sur les faits du moteur** (`SPIGNOS_COACH_REPORT_LLM_NARRATIVE_SPEC_v2` existe) — à livrer **avant toute sortie publique**. Le labo N0, privé, emploie le mot dès maintenant |
| O2 | **les deux** — régularité du programme en principal, série de jours en secondaire | la série de jours ne doit pas rompre sur un jour de repos **prévu** par le programme, sinon elle récompense l'entraînement pendant la récupération que le moteur protège ; **moteur V2** : la longueur de série est une récompense affichée, **jamais** un objectif d'optimisation du moteur |
| — | **mécaniques de récompense retenues : toutes** — records personnels · niveaux / paliers · objectifs de semaine · réaction de l'agent | un record n'est annoncé que s'il dépasse le meilleur **enregistré** ; jamais un record inventé |
| N0 | **`PROMISING — ITERATE N0`** | itération 1 : accueil + fin de séance scorée, sur fixtures |

**Points ouverts — à trancher par l'opérateur avant la tranche concernée :**

| # | Question | Pourquoi elle se pose | Proposition |
|---|---|---|---|
| O1 | Dire « l'IA » dans l'accueil ? | le moteur est déterministe, **zéro ML** (`DESIGN_DECISIONS_HOME_UIV2` D2, gardé par test) : « l'IA » serait **faux**, pas seulement déconseillé | « AUREN lit tes séries et prépare la suivante » — ce que le moteur fait réellement |
| O2 | Récompenser la régularité par jours consécutifs ? | une série de jours consécutifs récompense l'entraînement **pendant** la récupération que le moteur protège | régularité comptée **sur le programme** (séances prévues tenues), jamais pénalisée par un jour de repos prévu |
| O3 | Un score juste après substitution | `compute_success_score` juge contre la cible de l'exercice **prescrit** ; deux specs se contredisent (`SPIGNOS_EXERCISE_SUBSTITUTION_GRAPH_SPEC_FINAL` §9.7 / `SPIGNOS_EXERCISE_SYSTEM_CONSOLIDATION_SPEC` §5.3) | score calculé sur l'exercice **réellement fait** — tranche métier, spec + tests |
| O4 | Taxonomie des objectifs | dépend de ce que le domaine porte déjà (inventaire en cours) | réutiliser les objectifs existants avant d'en créer |
| O5 | Quelles mesures biologiques demander | le meilleur prédicteur de la charge de départ et du rythme de progression est l'**ancienneté d'entraînement**, que l'opérateur n'a pas citée ; l'activité professionnelle prédit peu | taille · poids · année de naissance · sexe (avec « je préfère ne pas répondre ») · **ancienneté d'entraînement** · activité quotidienne en trois niveaux ; tour de taille et FC repos en option, déjà stockés |
| O6 | Consentement | âge, sexe, poids, tension sont des données personnelles, certaines relèvent de la santé | consentement explicite à l'accueil, finalité dite champ par champ, effacement possible ; à valider avant la tranche qui stocke les champs nouveaux |

---

## 1. Diagnostic de l'état actuel

### 1.1 Ce que le produit est, mesuré

| Fait | Valeur | Preuve |
|---|---|---|
| Rendu | 100 % serveur, Jinja ; chaque écriture = formulaire POST → **303** → GET d'un document complet | `sessions.py:259-261`, `:1184` ; trace d'exécution |
| API JSON du parcours en salle | **aucune** route. Les seuls JSON : `/healthz`, `/healthz/strict`, `/export/sessions.json`, `/body/export.json` (+ le 429 du limiteur) | `grep JSONResponse app/routers` |
| Routes | 101, dont 11 dans `sessions.py` *(compte d'exploration, non revérifié)* | — |
| Gabarits | 73 fichiers (69 `.html`, 4 `.svg`), 10 801 lignes ; `exercise_card.html` seul = 1 003 lignes | `find`/`wc` |
| CSS / JS | 14 283 lignes CSS (6 feuilles) · 865 lignes JS (3 scripts) · **0 étape de build · 0 TypeScript** | `find`/`wc` |
| PWA | manifeste présent ; **service worker, hors-ligne, vibration, Wake Lock, notifications : absents — et interdits par des gardes** | `tests/test_pwa_installability.py:121`, `test_ui_cp8i_resilience_saisie.py:298-301` |
| Baselines visuelles | **0 PNG de baseline versionné**, jamais capturé en CI (Playwright = extra optionnel) ; `may_promote_to_canonical()` rend `False` | `.gitignore:39-44`, `pyproject.toml:40`, `scripts/visual_contract.py` |
| Migrations | 34 révisions linéaires, tête `x5y0s6t7v18` | `migrations/versions/` |
| Gardes | 362 fichiers de test ; 57 nommés UI/visuel/a11y/cockpit/console ; 145 lisent des gabarits | `ls tests/` + grep |

### 1.2 La boucle en salle, mesurée au labo (2026-10-23)

Sonde in-process (`TestClient`, SQLite, **sans réseau**), utilisateur avec
**8 séances d'historique** (sans historique, le moteur de surcharge et « la dernière
fois » sont muets et la mesure flatte la route), 6 itérations, 18 séries :

| Geste | Médiane | p95 |
|---|---|---|
| `GET /` (MISSION, reco calculée) | **103,7 ms** | 127,6 ms |
| `POST /sessions` (START) | 4,9 ms | 5,7 ms |
| `GET /sessions/{id}` (premier rendu EXECUTION) | 25,1 ms | 83,4 ms |
| `POST` série `nav=stay` (écriture VALIDER) | 3,4 ms | 4,2 ms |
| `GET` après série (rendu REPOS) | 24,3 ms | 25,8 ms |
| **VALIDER → REPOS visible, coût serveur** | **27,8 ms** | 29,5 ms |
| HTML de la page de séance | 12,5 Kio | — |

**Lecture :** le serveur n'est **pas** le goulot. Le temps perçu en salle est
`2 × RTT + transfert + parse/paint d'un document entier` — le POST puis le GET de
redirection — et il est **nul en l'absence de réseau** : sans réseau, la série ne
part pas et le repos ne commence pas. C'est exactement ce que la mesure in-process
**ne peut pas** montrer, et ce que le lab doit mesurer sur appareil (§10).

**Constat de comportement :** après la dernière série d'un exercice, l'état rendu
est `exercise_complete` **6 fois sur 6** — aucun repos, et l'utilisateur doit
toucher `CONTINUER → E2`. C'est **voulu** (`console_state.py:417-421`) ; c'est aussi
l'écart le plus net avec le parcours cible (§0 D5).

**Constat de coût :** la recommandation est calculée **deux fois** par `GET /`
(`pages.py:104` via `_build_reco_context`, `home.py:173` via `_build_today`).

### 1.3 Le diagnostic, en une phrase

> **Le cerveau est mûr ; le corps de l'interface ne l'est pas — et la frontière
> entre les deux n'existe pas.**

Le moteur sait décider la séance, expliquer ce qui a décidé (`recommendation_v3.critere_decisif`,
`expliquer`, `phrase_de`), adapter à l'équipement (`environment_activation.preparer_demarrage`),
dériver l'état de la série (`console_state.build_console_state`), proposer une charge
(`overload_engine.compute_overload_hint`). Mais **une part substantielle de la
décision de session vit dans le routeur et dans les gabarits** :

| Logique de domaine hors service | Où |
|---|---|
| écriture d'une série, épisode de complétion | `sessions.py:449` `_persist_set_values`, `:515` `_appliquer_episode_de_completion` |
| orchestration du START (préflight, adaptations, mémoire de conseil) — **dupliquée** dans un second routeur qui **importe le premier** | `sessions.py:186-261` ; `user_programs.py:54`, `:1137-1176` |
| choix de l'exercice actif, états de saut, voisin suivant/précédent, deltas | `sessions.py:796-878` |
| navigation après écriture | `sessions.py:1184` `stay_redirect_target` |
| prescription lue **brute** dans le gabarit | `exercise_card.html:316-317, 382` (`set_scheme`) |
| regroupement et plafond des substitutions | `exercise_card.html:881-888` |
| zone limitante, rangs de bandes, compte de séries de travail | `pages.py:115-430` |
| fin de séance, labels implicites, continuité hebdomadaire | `sessions.py:284`, `:316`, `:1083-1176` |

**Trois dérivations concurrentes de « où en suis-je »** : le routeur (premier
exercice incomplet, `sessions.py:824-839`), `mission_position.open_session_position`
(`set_index = done + 1`, suppose l'ordre), `console_state` (première série en attente
par index). Elles peuvent diverger.

**Deux défauts du contrat d'écriture actuel, vérifiés à la lecture du code :**

1. **`POST /sessions` n'a ni garde de séance ouverte ni idempotence**
   (`sessions.py:186-261`) : un double appui crée deux séances en cours.
2. **`update_exercise_card` réécrit `free_note`, `muscle_sensation` et
   `substituted_name` à CHAQUE POST** (`sessions.py:1304-1313`) : une clé absente
   vaut effacement. Le formulaire complet d'aujourd'hui les renvoie (champ caché
   `preserve()`, `exercise_card.html:928`), donc rien ne casse. **Une écriture
   par série qui réutiliserait cette route effacerait la note, la sensation — et
   l'adaptation d'équipement TRAIN A posée au START**, puisque `can_substitute`
   reste vrai tant qu'aucune série de travail n'est persistée. C'est la classe de
   défaut « remplacement sur formulaire partiel », déjà vue trois fois dans ce
   dépôt. **Conséquence : le client vNext ne doit jamais appeler cette route.**

---

## 2. Carte de récupération du domaine — `KEEP` · `ADAPT` · `REBUILD` · `RETIRE FROM PRIMARY UX`

**Règle :** aucun comportement de domaine n'est réécrit parce que l'interface
l'est. `ADAPT` signifie **extraire sans changer le comportement** (même résultat,
mêmes tests), jamais « réécrire ».

| Actif | Verdict | Détail |
|---|---|---|
| Base / migrations (34, tête `x5y0s6t7v18`) | **KEEP** | le lab n'ajoute **aucune** colonne (§8.6) |
| Authentification cookie signé, `samesite=strict` (`auth.py:89-99`) · propriété (`ownership.get_owned_session_or_404`) | **KEEP** (identité, propriété) · **ADAPT** (transport) | ~~r1 : même origine ⇒ cookie réutilisé~~ → r2 : une dépendance **porteur de jeton** distincte (`require_api_user`) résout le **même** `User` ; la propriété reste `get_owned_session_or_404`. Les routes `/api/*` rendent **401 JSON** au lieu du 303 vers `/login` (`main.py:298-300`). Prérequis **A0** (§0ter) |
| Recommandation V3 + mémoire de conseil (`advice_memory.recommander`, `POLITIQUE_SERVIE="v3"`, `MEMOIRE_SERVIE=True`) | **KEEP** | appelée **une fois** par le read model (corrige le double calcul) |
| Explication (`recommendation_v3.expliquer`/`phrase_de`, `recommendation_explainer.explain_recommendation`) | **KEEP** | la raison est servie telle quelle, jamais réécrite côté client |
| Récupération / readiness (`zone_recovery`, `training_state`, `recovery_explainer`) | **KEEP** | lue par la reco ; exposée seulement via `facteurs_gagnants/limitants` |
| Environnement TRAIN A (`environment_activation.preparer_demarrage`, `appliquer`, `environment_resolution`) | **KEEP** · **ADAPT** | `_poser_adaptations` / `_demarrage_bloque` quittent le routeur pour un service de démarrage |
| Mémoire de conseil — écriture d'épisode | **ADAPT** | `_enregistrer_episode_de_conseil` (`sessions.py:105`) → service ; l'identité de décision voyage dans la commande START au lieu de champs cachés |
| Constructeur de séance (`session_builder.instantiate_session`) | **KEEP** | inchangé |
| Écriture de série et épisode de complétion | **ADAPT** (prioritaire) | `_persist_set_values` + `_appliquer_episode_de_completion` + `feedback.compute_success_score` → `session_commands.complete_set(...)`. La sémantique `absent → inchangé / vide → effacement` est **conservée à l'identique** |
| Lignée prévu → réalisé (`exercise_name_snapshot` / `substituted_name`, `substitution.actual_exercise_name`) | **KEEP** | le read model expose les **deux** identités ; ⚠ aucune colonne ne dit si une substitution vient de TRAIN A ou d'un geste manuel — **constat**, pas un chantier du lab |
| Substitution (`can_substitute`, `compute_suggestions` N1/N2/N3) | **KEEP** · **ADAPT** | le nom soumis **n'est pas validé** contre la liste permise (`sessions.py:1309-1311`) : la commande vNext le valide contre `all_suggestions_flat` (durcissement **de l'adaptateur**, pas du domaine) |
| Surcharge / historique (`overload_inputs`, `overload_engine`, `overload_explainer`, `stats.last_time_by_exercise_code`, `delta`) | **KEEP** | `_build_overload_placeholder` (`sessions.py:393`) → read model |
| État de console (`console_state.build_console_state`, `command_for`, `secondary_for`, `rest_remaining_seconds`) | **KEEP** comme **source unique de « où en suis-je »** | les deux autres dérivations deviennent des lectures de celle-ci |
| Préférences d'entraînement (`training_preferences`) | **KEEP** | hors tranche (LOADOUT) |
| BODY / progression (`body_ledger`, `progression_view`, `zone_exposure`, `session_recap`, `flight_recorder`) | **KEEP** | hors tranche, sauf `build_recap` pour SESSION COMPLETE |
| `adaptive_replan.replan` (387 lignes, non importé) | **KEEP** (inchangé) | hors périmètre — ne pas le brancher par opportunisme |
| Composition routes / contexte (`pages.home`, `sessions.session_detail` ≈ 340 lignes de dict inline) | **REBUILD** | en **read models** de service, consommés par l'API vNext. Le legacy **peut** les adopter plus tard ; il n'y est pas obligé |
| Gabarits Jinja (73) | **RETIRE FROM PRIMARY UX** *(à terme, surface par surface)* | **restent en service** pendant tout le lab — repli et parité |
| CSS (14 283 l.) | **RETIRE FROM PRIMARY UX** | aucune réutilisation de classe ; seules les **mesures** (contraste, 44 px) survivent comme invariants |
| JS (`session_focus.js` etc.) | **RETIRE FROM PRIMARY UX** | sa logique de repos fondée sur l'échéance (`Date.now`, rattrapage `visibilitychange`) est **reprise comme principe**, pas comme code |
| Assets visuels (icônes PWA, plaques BodyMap SVG, `design/auren/`) | **KEEP** (assets) · forme libre | les plaques restent la source anatomique ; leur mise en page n'est pas contrainte |
| Baselines visuelles et harnais (`visual_baseline_*`, `visual_contract.py`, `geometry_manifest.py`) | **ADAPT** | le harnais Playwright devient l'outil de **mesure** du lab (§10) ; les contrats SOVEREIGN deviennent `LEGACY` (§4) |
| Gardes UI (57+) | **KEEP sur le legacy** · **non transposées** | elles gardent le legacy tant qu'il sert. Le vNext reçoit **ses propres** gardes de **capacité** (§10.3), jamais des gardes de **moyen** qui lisent du HTML servi |

---

## 3. Ce qui est préservé — trois natures, séparées

### 3.1 Sémantique produit (préservée intégralement)

1. **Une question par instrument** (`AUREN_INSTRUMENTS §2`) : MISSION « Qu'est-ce que je
   fais maintenant, et pourquoi ? », EXECUTION « Qu'est-ce que je fais sur cette série ? ».
2. **Une action dominante par état** (`Sx_UIV3_00 §2`).
3. **Cause avant action** : la raison de la reco est visible sans geste (`AUREN_UI_BLUEPRINT §2.5` — l'ordre cause → donc → séance → action).
4. **Donnée saisie · importée · dérivée** jamais confondues (`AUREN_INSTRUMENTS §4`).
5. **La précision ne dépasse pas le modèle** : pas de durée estimée, pas de score
   global, pas de pourcentage de récupération, pas de revendication d'activation.
6. **Le repos est dérivé, jamais persisté comme état** (`console_state.py:23-33`) :
   deux faits durables, `completed_at` et `rest_dismissed_at`.
7. **Une décision de saut ne survit jamais à une nouvelle exécution**
   (`_appliquer_episode_de_completion`, les quatre transitions).
8. **Allocation, pas suffisance** (`AUREN_VISUAL_BACKBONE §1`) : aucune jauge ne dit « assez ».
9. **La récupération n'a jamais de sémantique feu tricolore.**
10. **Le moteur dit ce qui a décidé** — le client n'en reconstruit jamais la raison.

### 3.2 Invariants d'accessibilité (préservés, re-mesurés sur la nouvelle forme)

- cible tactile **≥ 44 × 44 px** pour toute commande primaire (standard produit ;
  WCAG 2.2 AA = 24 px) ;
- **`no-color-only-state`** : tout état porte une forme ;
- **contraste = contrat de couple**, mesuré sur le fond réel (≥ 4,5:1 texte,
  ≥ 3:1 non-texte significatif) ;
- **`prefers-reduced-motion`** désactive toute transition, et l'écran reste
  **intégralement jugeable sans transition** (`Sx_UIV3_00A §8`) ;
- nom accessible pour toute commande ; ordre de focus = ordre de lecture ;
- validation implicite par **Entrée / Done**, jamais au `blur` ;
- zoom texte 200 % sans perte de fonction.

### 3.3 Forme visuelle (jetable)

Cartes, rails bleus, ambre unique, échelle typographique E3, gouttières 14/16/20,
« châssis remplace la carte », phosphore, scanlines, compositions `P-03`, captures
`docs/assets/uiv3/*.png`, hex `#C8A24B` etc. **Rien de cela n'est un invariant.**
Ce qui en survit, survit parce que le §11 le reprend **pour une raison**, pas par héritage.

---

## 4. Superséder l'autorité visuelle — `LEGACY_VISUAL_REFERENCE`

### 4.1 Le mécanisme

On réutilise **les conventions existantes du dépôt**, aucune nouvelle :

1. **Table « Ce que ce document supersède »** (patron `AUREN_VISUAL_BACKBONE §6`) —
   colonnes `Contrat ancien | Remplacé par | Portée | Condition`, chaque ligne
   `⏳ préparé` jusqu'au GO opérateur puis `✅ appliqué`.
2. **Marqueur en ligne** dans le document superseded, au point exact (patron
   `AUREN_VISUAL_BACKBONE:221`) :
   `~~<énoncé>~~ — **LEGACY_VISUAL_REFERENCE le <date>** pour les surfaces vNext. Voir Sx_AUREN_MOBILE_EXPERIENCE_VNEXT §4.`
3. **Amendement `§Nbis`** (`SPEC_DRIVEN_ENGINEERING_PROTOCOL_v1 §8`) pour les specs
   `APPROVED — OPERATOR` : on n'en réécrit **aucune** ligne.
4. **Ligne au `SPEC_REGISTRY`** dans le même commit que l'amendement.

**Portée, et c'est le point qui évite la casse :** la supersession est **par
surface**, pas globale. Tant que le legacy sert une surface, ses contrats (gardes,
baselines, décisions) **continuent de garder le legacy**. `LEGACY_VISUAL_REFERENCE`
signifie : *ne gouverne plus la forme des surfaces vNext ; reste la référence
historique et le garde du legacy tant qu'il est en service.* On ne supprime rien ;
on retire un pouvoir.

### 4.2 Statut cible

| Statut | Sens |
|---|---|
| `LEGACY_VISUAL_REFERENCE` | rendu historique ; ne contraint plus la forme vNext ; continue de garder la surface legacy |
| `RETAINED_INVARIANT` | extrait **nommément** d'un document legacy et maintenu (sémantique ou a11y) |
| ~~`VNEXT_REFERENCE_FRAME`~~ → **`VNEXT_INTERACTION_REFERENCE_FRAME`** *(r2)* | proposition vNext qui gouverne hiérarchie, état, action souveraine, géométrie de base et zéro tableau de bord — **pas la forme** (§11.4) ; ne devient canonique que par une décision opérateur versionnée sur **rendu d'appareil**, et seulement pour la surface concernée |

### 4.3 La table (préparée, non appliquée)

| Contrat ancien | Remplacé par | Ce qui est `RETAINED_INVARIANT` | Condition |
|---|---|---|---|
| `AUREN_UI_BLUEPRINT §2.3` « référence visuelle canonique » + 3 PNG `docs/assets/uiv3/` | `LEGACY_VISUAL_REFERENCE` pour MISSION/EXECUTION vNext | §2.5 une question souveraine par surface ; ambre jamais sur la récupération ; contraste mesuré par niveau | ✅ appliqué 2026-10-23 (portée mobile) |
| `AUREN_UI_BLUEPRINT` « GOLDEN / SOVEREIGN : Home · Session » | idem | — | ✅ appliqué 2026-10-23 (portée mobile) |
| `Sx_UIV3_03 §6` règles de baseline + 13 états × 3 viewports | **ne s'applique plus** aux surfaces vNext ; nouvelles portes §10 | §8 table a11y (44 px, nom accessible, couleur seule interdite, contraste réel, reduced motion) | ✅ appliqué 2026-10-23 (portée mobile) |
| `SPRINT_UIV3_VISUAL_BASELINE_REPORT` (SOVEREIGN) + `scripts/visual_contract.py SURFACE_STATUS` + `geometry_manifest.py:68-71` | entrée `vnext-*` distincte ; `home`/`session-*` restent SOVEREIGN **pour le legacy** | — | ⏳ non appliqué — le harnais web ne connaît aucune surface mobile ; les scripts restent inchangés tant qu'aucune surface web ne bascule |
| `DESIGN_DECISIONS_UIV2_SURFACES` Q5/Q6/Q7/Q8 (rangs, échelle E3, un ambre plein, opacité) · « `.btn` 14 px portées par le viseur » | `LEGACY_VISUAL_REFERENCE` | Q4 (la ligne de série est un instrument) → sémantique reprise | ✅ appliqué 2026-10-23 (portée mobile) |
| `DESIGN_DECISIONS_HOME_UIV2` D3/D4/D5 (couleurs, retraits, direction) | `LEGACY_VISUAL_REFERENCE` | **D2** (badge d'origine sans revendication « IA », gardé par `test_home_design_decisions.py`) · **D9** (pas d'anticipation) | ✅ appliqué 2026-10-23 (portée mobile) |
| `AUREN_UIUX_V3_FOUNDATION_CONTRACT §4` (hex), `§8` (typo), `§9` gouttières | `LEGACY_VISUAL_REFERENCE` | **§1** hiérarchie L1/L2/L3 · **§2** une action dominante · **§3** 44 px + taxonomie A–E · **§5** encodage récupération · **§6** la cause ne se replie jamais · **§7** no-color-only · **§9 density budget** (objectifs, pas tokens) | ✅ appliqué 2026-10-23 (portée mobile) |
| `AUREN_UIUX_V3_FOUNDATION_CONTRACT §10` no-JS | amendé pour vNext par **D2** | « aucune écriture perdue en silence » (§0 D2) | ✅ appliqué 2026-10-23 (`§10bis`) |
| `Sx_UIV3_00A §9` Framework admission gate | amendement `§9bis` par **D1** | la **porte d'admission** elle-même (« framework only after measured need ») reste en vigueur **à l'intérieur** du client vNext | ✅ appliqué 2026-10-23 (`§9bis`) |
| `Sx_UIV3_01` structure Home « ordre vertical figé » | `LEGACY_VISUAL_REFERENCE` | migration D2/D6/Q5/D8/Q2 (sémantique) | ✅ appliqué 2026-10-23 (portée mobile) |
| `Sx_UIV3_02` ordre figé `SystemOrigin → DeltaReadout → SetInstrument → CommandDock`, libellés figés `§4` | `§4bis` : libellés vNext ; ordre libre | états `WARMUP/CURRENT_SET/REST/CORRECTION/EXERCISE_COMPLETE/LAST_EXERCISE_COMPLETE` ; REST jamais persisté | ✅ appliqué 2026-10-23 (`§4bis`) |
| `Sx_UIV3_04` libellés figés, 360 px « fait foi », gouttières | `LEGACY_VISUAL_REFERENCE` ; plancher vNext = **360 × 640 ET 390 × 844** (§10) | — | ✅ appliqué 2026-10-23 (portée mobile) |
| `AUREN_VISUAL_BACKBONE §2` (4 niveaux), `§3.1` (hex), `§3.5` textures, `§4` patron `P-03` | `LEGACY_VISUAL_REFERENCE` | **§1 PH-01** (allocation, pas suffisance) · **§3.1 rôles** (ACTION ≠ SYSTEM ≠ DONNÉE, provenance ≠ feedback) · **§3.4** mouvement subordonné à l'état · **§4.3** lecture en deux coups d'œil · **§5** invariants (hors no-JS) | ✅ appliqué 2026-10-23 (portée mobile) |
| `AUREN_VISUAL_BACKBONE §5bis` SSR baseline · « zéro framework » | amendé par **D1/D2** pour vNext | « aucune écriture d'entraînement ne dépend du client pour **survivre** » → reformulé §0 D2 | ✅ appliqué 2026-10-23 (portée mobile) |
| `AUREN_INSTRUMENTS §5` primitives visuelles et implémentations de référence (`session_focus.css:2212-2222`) | `LEGACY_VISUAL_REFERENCE` | **§2** sept instruments · **§3** test de survie · **§4** contrat d'objet (7 champs) · **§6.2bis** les quatre questions closes · **§7** ce que la donnée ne sait pas faire | ✅ appliqué 2026-10-23 (portée mobile) |
| `Sx_UI_11` / `SPRINT_Sb_UI_11_3` « Final Auren Baseline » · `Sx_UI_02/02b` palette terminal · `SPIGNOS_VISUAL_IDENTITY_V2` | `LEGACY_VISUAL_REFERENCE` (déjà historiques de fait) | — | ✅ appliqué 2026-10-23 (portée mobile) |
| `Sb_ASSET_03B_1` « PLATE CONTRACT LOCKED » · `Sx_ASSET_01` taxonomie 11 zones | **non superseded** | la taxonomie et le contrat de plaque sont du **domaine anatomique**, pas de la forme d'écran | — |

**Documents non touchés** : `AUREN_UI_REARBITRATION_REGISTER` (il refuse déjà de
figer l'ontologie, l. 10-11), `AUREN_UI_DECISION_BACKLOG` (« AUCUN objet n'est
gelé », L-09), les arbitrages `CP6/CP7/CP75` (mesures, pas de canon visuel).

---

## 5. Les instruments cibles

### 5.1 MISSION — « Qu'est-ce que je fais maintenant, et pourquoi ? »

| États | Données | Action souveraine |
|---|---|---|
| `READY` | séance proposée (nom), **raison** (`phrase_de` + facteurs), portée (n exercices, n séries de travail), premier exercice | `DÉMARRER` |
| `RESUME` | séance ouverte, position (exercice k/n, série) | `REPRENDRE` |
| `BLOCKED` | `environnement_etat == "no_servable_candidate"` ou départ `REFUSE` | `DÉCLARER MON ÉQUIPEMENT` (vers legacy `/plan#equipement` pendant le lab) |
| `NO_RECO` | `recommander` rend `None` hors séance ouverte | `CHOISIR UNE SÉANCE` (vers legacy) |

Ouverture → START = **un seul geste** quand aucun bloqueur n'existe. Les
alternatives et le « pourquoi » complet sont **une** divulgation (feuille).

### 5.2 EXECUTION — « Qu'est-ce que je fais sur cette série ? »

Machine à états **du client**, alimentée par le read model, avec une seule
source serveur de vérité de position (`console_state`) :

```
              VALIDER (optimiste)                 fin du compte à rebours | PASSER
 CURRENT_SET ───────────────────▶ REST(série k+1) ─────────────────────────────▶ CURRENT_SET(k+1)
      │                                                                              
      │ VALIDER la dernière série de l'exercice (D5)                                 
      ▼                                                                              
 REST(exercice suivant) ── fin | PASSER | COMMENCER ──▶ CURRENT_SET(E+1, S1)
      │ (dernier exercice)
      ▼
 LAST_EXERCISE_COMPLETE ──▶ bilan (legacy pendant le lab) ──▶ SESSION_COMPLETE
```

États transverses : `CORRECTION` (toucher une série passée), `PENDING_SYNC`
(écriture non accusée — §8.4), `OFFLINE` (même machine, file locale).

**REST est un état d'EXECUTION, pas une destination** : même écran, même
instrument, autre forme. Les secondaires (substituer, note, méthode, cues) sont
derrière **une** feuille.

---

## 6. Options d'architecture — A, B, C

### 6.1 Définitions

- **A — Reset sur la pile actuelle.** FastAPI + Jinja + HTML/CSS + JS progressif ;
  écriture par formulaire, éventuellement `hx-boost` / View Transitions.
- **B — Coquille web mobile.** Domaine FastAPI inchangé + **client TypeScript
  dédié** consommant des **contrats de présentation explicites** (JSON). Servi
  même origine. Capacitor évalué **plus tard** comme pont natif.
- **C — Client natif d'abord.** React Native (ou équivalent) consommant la même API.

### 6.2 Comparaison

| Critère | A — Jinja reset | B — TS shell | C — natif |
|---|---|---|---|
| **Réutilisation du code** | maximale (routes, auth, gabarits partiels) | domaine 100 % ; **contrats de présentation à écrire** (les mêmes que C) ; auth cookie réutilisée | domaine 100 % ; contrats idem ; **auth à refaire** (cookie `samesite=strict` → jeton), tout l'écran à refaire |
| **Latence VALIDER → REPOS** | `2×RTT + document` à **chaque** geste — mesuré : 27,8 ms serveur, le reste est réseau ; **aucun repos sans réseau** | **0 RTT perçu** : transition locale immédiate, écriture en arrière-plan | 0 RTT perçu |
| **Justesse du minuteur** | échéance serveur (`completed_at`) + JS ; ±15 s non persisté *(un défaut probable après −15 s est signalé par l'exploration, non revérifié)* | échéance locale ancrée sur `completed_at` serveur + décalage d'horloge ; état reconstructible au rechargement | idem + horloge native |
| **UI optimiste** | contraire à `test_df_b_session_flow.py:66` ; exige de toute façon D3 | native au modèle | native |
| **Minuteur en arrière-plan / écran verrouillé** | non (onglet suspendu) | non sur web pur ; **oui** via Capacitor (notifications locales) | oui |
| **Haptique** | non (`navigator.vibrate` absent d'iOS Safari) | non sur web iOS ; oui via Capacitor | oui |
| **Hors-ligne / réseau dégradé** | **impossible** sans service worker (interdit, `test_ui_cp8i_resilience_saisie.py:298`) — et un formulaire ne se met pas en file | file d'écritures idempotentes en local (IndexedDB) ; service worker en phase 2 | file locale native |
| **Accessibilité** | SSR = sémantique HTML gratuite | HTML sémantique **à tenir à la main** (pas de framework qui l'abîme) | composants natifs accessibles, mais VoiceOver/TalkBack à tester par plateforme |
| **Tests** | 362 fichiers existants, mais **gardes de moyen** qui lisent du HTML | contrats Python + réducteur TS (unitaires) + Playwright réel 390×844 (déjà dans le dépôt) | contrats + Detox/Maestro + appareils ; **nouvelle CI** |
| **Liberté visuelle** | limitée par 14 k lignes CSS et les gardes de moyen | totale | totale |
| **Animation / transitions d'état** | View Transitions entre documents | transitions d'état in-page, reduced-motion trivial | natives |
| **App Store** | PWA seulement | PWA ; Capacitor = binaire App Store (risque guideline 4.2 « web wrapper » atténué par des fonctions natives réelles) | natif direct |
| **Coût de maintenance** | bas à court terme ; la dette de routeur reste | **une seconde surface** pendant la migration ; une pile JS/TS en plus | **deux piles** (Python + RN), deux pipelines, mises à jour de stores |
| **Duplication de logique métier** | aucune | **aucune si §8 est respecté** (le client ne décide rien) | idem, risque plus fort (tentation hors-ligne) |
| **Risque de migration** | faible techniquement, mais **ne résout pas** le réseau | moyen, borné par le strangler (§13) | élevé |
| **Ergonomie Claude/Superpowers** | excellente (pile connue, gardes fines) | bonne (TS typé, tests rapides, Playwright déjà maîtrisé) ; **perte** des gardes HTML à remplacer par des gardes de capacité | plus faible (simulateurs, builds natifs, signature) |

### 6.3 Lecture r1 *(sous le critère r1 — conservée pour l'historique)*

- **A ne peut pas tenir la cible « immédiat » en salle** sans lever la même
  interdiction que B (écriture hors formulaire) — et même levée, A garde un
  document par geste et **zéro tolérance au réseau**. A reste la meilleure option
  si l'opérateur juge que le réseau de sa salle n'est pas un problème : c'est
  **mesurable** (§10, porte G-NET) et c'est la raison pour laquelle D1 est une
  décision et non une évidence.
- **C paie dès la tranche 1 ce que seules les extensions (§12) exigent.** Live
  Activity et minuteur verrouillé sont réels, mais ils ne bloquent pas le lab.
- **B est le seul qui achète l'immédiateté et la tolérance au réseau sans payer
  une seconde plateforme**, et qui garde la porte native ouverte (Capacitor) sans
  réécriture.

**Pas de framework par mode.** B ne veut pas dire React. La tranche de lab compte
cinq états et deux écrans : un **réducteur pur** (TypeScript) + des fonctions de
rendu DOM explicites suffisent, et gardent la porte d'admission de
`Sx_UIV3_00A §9` **vivante à l'intérieur** du client : un framework UI n'entrera
qu'avec un défaut mesuré.

### 6.4 Re-arbitrage r2 — quatre options sous le nouveau critère

**C est scindé**, parce que r1 l'avait évalué comme un épouvantail (« deux piles,
deux stores, tout à refaire ») :

- **C1 — natif complet** : deux bases de code Swift/SwiftUI + Kotlin/Compose, **ou**
  React Native « nu » sans outillage Expo (projets natifs maintenus à la main) ;
- **C2 — React Native + Expo** : **une** base TypeScript pour iOS et Android ;
  modules Expo pour haptique, notifications locales, SQLite, coffre sécurisé,
  maintien d'écran, liens profonds ; **modules Swift/Kotlin ciblés** (Expo Modules)
  seulement pour Live Activity / Dynamic Island et la notification continue
  Android ; builds et distribution par service cloud, mises à jour JS à chaud
  pour les correctifs.

**Notation 1–5** (jugement argumenté, pas une mesure ; la ligne « Pourquoi » dit
sur quoi il repose). **Pondération r2** : le plafond UX et les capacités natives
pèsent ×3, la fiabilité hors-ligne et le cycle de vie ×2, le reste ×1.

| Critère | Poids | A | B | C1 | **C2** | Pourquoi |
|---|---|---|---|---|---|---|
| Plafond UX | ×3 | 2 | 3 | 5 | **4,5** | C2 rend des vues natives, gestes et animations sur le fil UI ; C1 garde l'avantage des composants système purs (SwiftUI) |
| Fiabilité hors-ligne | ×2 | 1 | 3 | 5 | **5** | B : IndexedDB peut être évincé par iOS ; C1/C2 : SQLite sur disque de l'app |
| Intégration native | ×3 | 1 | 2 | 5 | **4,5** | iOS web : ni haptique, ni notification locale planifiée, ni Live Activity ; C2 y arrive par modules, C1 nativement |
| Cycle de vie de l'app | ×2 | 1 | 2 | 5 | **4,5** | onglet suspendu vs `AppState` / tâches natives |
| Accessibilité | ×1 | 4 | 3 | 5 | **4** | SSR = HTML sémantique gratuit ; C2 = rôles/labels RN + Dynamic Type à tenir ; C1 = composants système |
| Qualité d'animation | ×1 | 2 | 3 | 5 | **4,5** | transitions de document vs animations natives à 60/120 Hz |
| Haptique | ×3 | 1 | 1 | 5 | **5** | même API système des deux côtés pour C2 |
| Séance sur écran verrouillé | ×3 | 1 | 1 | 5 | **4** | C2 : extension widget Swift + module ; C1 : natif |
| App Store / Play | ×1 | 1 | 2 | 5 | **5** | C2 distribue des binaires natifs ; B via Capacitor = risque « web wrapper » |
| Maintenance (1 opérateur + agents) | ×1 | 5 | 4 | 1 | **3,5** | C1 = deux bases ; C2 = une base TS, outillage géré ; agents très à l'aise en TS/React |
| Complexité CI | ×1 | 5 | 4 | 1 | **3** | C2 : typecheck/tests sur chaque PR, builds natifs dans le cloud (pas de runner macOS maison) |
| Réutilisation backend | ×1 | 5 | 5 | 5 | **5** | contrats identiques ; aucun domaine dupliqué |
| Coût d'authentification | ×1 | 5 | 5 | 2 | **2** | jetons + coffre + révocation (D9), et A0 avant |
| Testabilité | ×1 | 4 | 4 | 2 | **3,5** | Jest sur réducteur/outbox + E2E scriptés sur simulateur/appareil |
| Vitesse de déploiement | ×1 | 5 | 5 | 1 | **4** | revue store pour le natif ; correctifs JS à chaud pour C2 |
| Risque de re-plateforme | ×2 | 1 | 2 | 5 | **4,5** | B devrait migrer vers natif pour l'écran verrouillé ; C2 a l'issue native intégrée |
| **Total pondéré** (/ 135 — somme des poids 27 × 5) | | **57** | **70** | **117** | **116,5** | |

**Lecture r2 :**

- **C1 et C2 font jeu égal sur le total ; ils ne pèsent pas pareil au quotidien.**
  C1 gagne de peu sur le plafond et l'écran verrouillé, et perd sur ce qui décide
  de la survie d'un produit tenu par **un** opérateur : deux bases de code, deux
  langages UI, deux pipelines, et toute fonctionnalité écrite deux fois. C2 tient
  **une** base et garde C1 **comme issue locale** (un module Swift ou Kotlin là où
  il paie) — c'est-à-dire qu'il n'y a pas de re-plateforme à prévoir.
- **B ne passe plus** : son avantage (pas de seconde plateforme) est exactement ce
  que le nouveau critère a cessé de valoriser, et ses manques sur iOS (haptique,
  notification locale, écran verrouillé) sont des limites de plateforme, pas de
  mise en œuvre.
- **A** reste le repli web, pas une option vNext.

**Bloquant concret cherché, non trouvé** : rien dans le dépôt n'empêche C2 — le
domaine est déjà côté serveur, les contrats §8 ne supposent rien du client. Trois
conflits **à trancher** en sont sortis (§0bis), aucun **bloquant**.

**Porte d'admission de `Sx_UIV3_00A §9`, instruite plutôt que contournée** — ses
quatre conditions, pour C2 :

1. *défaut mesuré que la plateforme web ne résout pas* — dépendance réseau de
   VALIDER → REPOS (mesurée, §1.2) ; absence d'haptique, de notification locale
   planifiée et d'activité d'écran verrouillé sur iOS web (limites de plateforme) ;
2. *View Transitions ne suffit pas* — une transition de document ne supprime ni
   l'aller-retour ni la dépendance réseau ;
3. *maintien du contrat no-JS* — **sans objet pour un client natif** ; le legacy
   web le garde intégralement ;
4. *coût de retrait écrit* — retirer C2 = cesser de distribuer l'app ; les
   contrats §8 et les services extraits restent utiles au legacy ; aucun domaine
   ne vit dans le client.

---

## 7. Architecture recommandée — r2 : C2

*(Le schéma r1, coquille web même origine, est remplacé ; ses principes 1–3 sont
conservés à l'identique.)*

```
┌──────────────── clients/mobile — Expo · React Native · TypeScript (iOS + Android) ──────────────┐
│  state      réducteur pur  MissionState | ExecutionState — interprète la table de transitions   │
│  timer      échéance = anchor(performed_at) + durée ; ±15 s local ; notification locale planifiée│
│  journal    Expo SQLite : séries validées + outbox de commandes (une transaction par geste)     │
│  sync       worker : au commit, au retour au premier plan, au retour du réseau ; backoff        │
│  cache      dernier MISSION / EXECUTION_READ_MODEL + plan de séance (exécution hors-ligne)      │
│  auth       jeton d'accès court + rafraîchissement rotatif, coffre Keychain/Keystore (D9)       │
│  native     haptique · maintien d'écran · liens profonds · (E1) Live Activity / notif continue   │
│  view       vues natives, feuilles natives, safe areas, Dynamic Type, VoiceOver/TalkBack        │
└───────────────▲──────────────────────────────────────────────────────────┬──────────────────────┘
                │ HTTPS JSON (read models)        Authorization: Bearer      │ HTTPS JSON (commandes)
┌───────────────┴────────────────────────── FastAPI (domaine, autorité) ───▼──────────────────────┐
│  app/routers/vnext_api.py     /api/vnext/*  — adaptateur MINCE : auth porteur, propriété,        │
│                                validation, 401/404/409/422 JSON. Aucune décision.                │
│  app/routers/mobile_auth.py   /api/vnext/auth/*  — émission / rotation / révocation (D9, après A0)│
│  app/services/presentation/   mission_read_model · execution_read_model · session_plan           │
│  app/services/session_commands.py  start_session · complete_set · dismiss_rest · substitute      │
│        ▲ extraits SANS changement de comportement du routeur legacy, qui les appelle             │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│  DOMAINE INCHANGÉ : advice_memory · recommendation_v3 · environment_activation · session_builder │
│  console_state · overload_* · stats · substitution · session_recap                               │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
        legacy Jinja (/, /sessions/*) reste en service, lit la MÊME base — repli et parité
```

**Principes :**

1. **Le client ne décide rien.** Il affiche des read models, émet des commandes,
   et **interprète** une table de transitions **fournie** par le serveur (§8.8) :
   il ne calcule ni le choix de séance, ni l'adaptation, ni la surcharge, ni la
   récupération, ni les substitutions, ni l'exercice logique suivant.
2. **Le serveur reste l'autorité de l'historique durable** ; le client est
   l'autorité du **temps perçu** (transition immédiate, puis réconciliation).
3. **Une écriture par fait** (une série), idempotente par construction.
4. **Local d'abord pour l'exécution, serveur d'abord pour la décision** : START et
   le choix de séance exigent le réseau (une fois, à l'entrée de la salle) ;
   ~~la séance entière s'exécute ensuite sans lui~~ → **le chemin nominal de la
   séance matérialisée** s'exécute ensuite sans lui ; le reste passe en
   `REQUIRES_SYNC` (§0quater).
5. **La séance active est un MODE, pas une navigation** : pendant `EXECUTION`, pas
   de barre d'onglets, pas de tableau de bord, une seule action souveraine ;
   tout le reste vit dans une feuille native. **Cible : zéro décision de
   navigation pendant une séance normale.**
6. **Natif là où il paie, partagé partout ailleurs** : un module Swift ou Kotlin
   n'entre qu'avec une capacité que la couche partagée ne peut pas rendre (§12).

---

## 8. Frontière API / présentation — contrats dérivés du code réel

Les noms sont de travail ; les **sources** sont des fonctions qui existent.

### 8.1 `MISSION_READ_MODEL` — `GET /api/vnext/mission`

| Champ | Source réelle |
|---|---|
| `state` ∈ `READY · RESUME · BLOCKED · NO_RECO` | `session_state.latest_open_session` (RESUME) · `advice_memory.recommander(..., politique=POLITIQUE_SERVIE, avec_memoire=MEMOIRE_SERVIE)` · `context.environnement_etat` |
| `recommendation.template` `{slug, name}` | `top["template"]` (ORM → sérialisé) |
| `recommendation.reason` `{phrase, winning[], limiting[], horizon, provenance, decisive}` | `top["phrase"]`, `top["explication"]` (`expliquer`), `critere_decisif` |
| `recommendation.alternatives[]` `{slug, name, phrase}` | `reco["alternatives"]` (≤ 2) |
| `recommendation.environment` `{active, adapted, state}` | `context.environnement_actif/adapte/etat` |
| `scope` `{exercise_count, work_set_count, first_exercise{name, set_scheme}}` | `_template_work_set_count` (`pages.py:115`, **à extraire**) · `TemplateExercise.set_scheme` |
| `decision_identity` `{fingerprint, policy, top, alternatives}` | `context.empreinte_contexte`, `politique`, slugs — ce que `_partials/_decision_identity.html` met en champs cachés |
| `open_session` `{id, position{exercise_index, exercise_count, set_index}}` | `mission_position.open_session_position` (**à aligner** sur `console_state`, §1.3) |
| `primary_action` `{kind: START·RESUME·DECLARE_EQUIPMENT·CHOOSE, target}` | dérivé de `state` |
| **absent par décision** | durée estimée, score de préparation, pourcentage de récupération |

### 8.2 `EXECUTION_READ_MODEL` — `GET /api/vnext/sessions/{sid}/execution`

| Champ | Source réelle |
|---|---|
| `session` `{id, template_name, started_at, status}` | `WorkoutSession` |
| `position` `{exercise_index, exercise_count}` | **une seule** dérivation : celle de `console_state` appliquée à la séance |
| `exercise` `{se_id, prescribed_name, executed_name, code, set_scheme, rep_range{min,max}}` | `exercise_name_snapshot` · `substitution.actual_exercise_name` · `template_exercise.set_scheme` · `RepTarget` |
| `console` `{state, current_set{id, index, kind}, done_sets[], future_sets[]}` | `console_state.build_console_state` |
| `prefill` `{weight_kg, reps, origin: OVERLOAD·LAST_SET·NONE}` | `OverloadHint.target_weight_kg/target_reps_max` sinon dernière série faite — **D6** |
| `guidance` `{state, intent_label, target_summary, reasons[], silent}` | `overload_explainer.explain_overload_hint(compute_overload_hint(build_overload_input_for_exercise(...)))` |
| `previous` `{relative, weights_str, reps_str, condensed}` | `stats.last_time_by_exercise_code` + `console_state.condense_reference` |
| `rest` `{anchor_completed_at, default_seconds, dismissed, remaining_at_server_now}` | `serie_portant_le_repos` · `REST_FALLBACK_SECONDS` · `rest_dismissed_at` · `rest_remaining_seconds` |
| `server_now` | horloge serveur (calcul du décalage client) |
| `next` `{kind: SET·EXERCISE·BILAN, exercise{name, set_scheme, guidance, previous}?}` | voisin suivant (aujourd'hui `sessions.py:847-878`, **à extraire**) |
| `secondary` `{can_substitute, substitutes{N1[],N2[],N3[]}, note, sensation}` | `can_substitute` · `compute_suggestions` (plafond/regroupement **déplacés hors du gabarit**) |
| `commands` | liste des commandes permises dans cet état (le client n'en invente pas) |

### 8.3 Commandes

| Commande | Route | Corps | Service (extrait) | Réponse |
|---|---|---|---|---|
| `START_SESSION` | `POST /api/vnext/sessions` | `{template_slug, decision_identity, op_id}` | `session_commands.start_session` = préflight `preparer_demarrage` → `instantiate_session` → adaptations → épisode de conseil — **le même enchaînement** que `sessions.py:186-261` | `201 {session_id, execution}` · **`409 {open_session_id}` si une séance est ouverte** (corrige le double appui, dans l'adaptateur) · `409 BLOCKED` si `REFUSE` |
| `SET_COMPLETION` | `PUT /api/vnext/sessions/{sid}/sets/{set_id}` | `{weight_kg, reps, op_id, performed_at}` *(`performed_at` : r2, D11)* | `session_commands.complete_set` = `_persist_set_values` restreint **à une série** + `_appliquer_episode_de_completion` + `compute_success_score` | `200 {execution}` |
| `SET_CLEAR` | `DELETE /api/vnext/sessions/{sid}/sets/{set_id}` | — | même service, `clear_set` | `200 {execution}` |
| `REST_SKIP` | `POST /api/vnext/sessions/{sid}/exercises/{se_id}/rest/skip` | `{op_id}` | `dismiss_rest` extrait (idempotent : premier horodatage gardé) | `200 {execution}` |
| `SUBSTITUTE` | `PUT /api/vnext/sessions/{sid}/exercises/{se_id}/substitution` | `{name \| null}` | `can_substitute` + **validation contre `all_suggestions_flat`** | `200` · `409` si une série de travail est faite · `422` nom hors liste |

**`REST_ADJUST` (±15 s) n'est PAS une commande.** Le dépôt a tranché que la durée
est une suggestion locale (`console_state.py:30-32`). Le client ajuste son
échéance locale ; au rechargement, l'échéance revient au repli de 90 s. Limite
**assumée et visible**, pas un oubli — la rendre durable exigerait une colonne,
donc une migration, hors lab.

**`SESSION_TRANSITION` n'est pas une commande non plus** : passer à l'exercice
suivant n'écrit rien (la position est dérivée). C'est une transition du client,
autorisée par `next` dans le read model.

### 8.4 Idempotence, ordre, hors-ligne — sans migration

- `SET_COMPLETION` est **idempotente par nature** : `PUT` d'une valeur sur une
  ligne pré-créée ; `completed_at` est **préservé** sur COMPLÈTE → COMPLÈTE
  (`_appliquer_episode_de_completion`). Rejouer la même commande ne change rien.
  `op_id` sert au **dédoublonnage côté client** et aux journaux ; il n'est **pas**
  persisté (pas de colonne).
- Ordre : la file du client est **par série** ; deux écritures sur la même série
  se compactent (la dernière gagne) **avant** envoi.
- `START_SESSION` est rendue sûre par la garde de séance ouverte (409), pas par un
  jeton persisté.
- Accusé visible : une série non accusée porte l'état `PENDING_SYNC` (glyphe + texte,
  jamais couleur seule). ~~r1 : la déconnexion purge la file après avertissement~~ →
  r2 : **la déconnexion est refusée tant que la file n'est pas vide**, sauf
  abandon explicite série par série (§8.7) — aucune série ne disparaît par effet de bord.

### 8.5 Validation dans l'adaptateur (pas dans le domaine)

`weight_kg` fini, `0 ≤ w ≤ 1000` ; `reps` entier `0 < r ≤ 200` ; séance `in_progress`
sinon 409. Le legacy accepte aujourd'hui `nan` et les négatifs *(exploration, non
revérifié)* : on **ne change pas** le legacy dans le lab, on n'hérite pas de son
laxisme.

### 8.6 Ce que le contrat n'ajoute pas

Aucune table, aucune colonne, aucune migration, aucune modification de
`recommendation*.py`, `console_state.py`, `overload_*.py`, `environment_*.py`.
**Les extractions (§2 `ADAPT`) sont des déplacements de code** dont la preuve est
que les tests legacy existants passent inchangés.

**Exception r2, nommée et isolée :** l'adaptateur d'authentification mobile (D9,
§8.9) exige **une** table additive de sessions d'appareil. Elle vit dans **sa
propre** tranche (tier `migration`), après A0 — jamais mêlée aux contrats de
présentation, et **pas dans cette mission**.

### 8.7 *(r2)* Exécution locale d'abord — journal et outbox Expo SQLite

**Pourquoi SQLite et pas un stockage clé-valeur** : une validation doit écrire
**deux** faits ensemble (la série au journal, la commande à l'outbox) ou aucun.
Seule une base transactionnelle le garantit ; elle survit à la mort du processus
et au redémarrage, et ne peut pas être évincée par le système comme un cache web.

**Schéma local** (base de l'app, **pas** une migration serveur) :

| Table | Colonnes | Rôle |
|---|---|---|
| `journal_sets` | `set_id` PK · `session_id` · `se_id` · `weight_kg` · `reps` · `performed_at` · `local_state` (`saved_local` · `synced` · `rejected`) · `server_ack_at` | ce que l'utilisateur a fait, tel qu'il l'a fait |
| `outbox` | `op_id` PK (UUID) · `kind` · `target` · `payload` JSON · `created_at` · `attempts` · `next_attempt_at` · `state` (`pending` · `inflight` · `acked` · `failed`) · `last_error` | les commandes à envoyer, dans l'ordre |
| `read_models` | `key` PK · `json` · `server_now` · `fetched_at` | dernier MISSION / EXECUTION / plan de séance (§8.8) |

**Le geste VALIDER, dans l'ordre exact :**

```
t0  appui            → le réducteur passe en REST (prochain cadre, sans attendre quoi que ce soit)
                     → haptique de confirmation (§11.5)
t1  une transaction  → INSERT journal_sets + INSERT outbox            (porte G-LOCAL)
                     → la série affiche « enregistrée sur l'appareil »  ← SÛRE à partir d'ici
t2  worker           → PUT /api/vnext/.../sets/{set_id}  (asynchrone)
t3  ACK 200          → outbox.acked · journal.synced · read model réconcilié → « synchronisée »
    échec réseau     → backoff exponentiel, rejoué au retour du réseau, au retour au premier plan,
                       au redémarrage de l'app — l'outbox est sur disque
    échec 4xx        → outbox.failed · journal.rejected · VISIBLE, action explicite
                       (réessayer / ouvrir la séance en version classique / abandonner CETTE série)
```

**Trois états visibles d'une série, jamais la couleur seule :** `enregistrée sur
l'appareil` → `synchronisée` → (`refusée par le serveur` le cas échéant). Une
série n'est **jamais** retirée de l'outbox sans ACK ou sans abandon explicite.

**Si t1 échoue** (disque plein, base corrompue) : le REPOS déjà affiché reste, mais
la série passe en `non enregistrée` avec une alerte bloquante — c'est le **seul**
cas où l'optimisme recule, et il ne recule pas en silence.

**Compaction** : deux commandes `pending` sur la même série fusionnent (la dernière
gagne) ; une commande `inflight` n'est jamais réécrite.

**Réconciliation** : à l'ACK, le read model serveur remplace le cache **pour ce qui
est acquitté** ; les commandes encore `pending` sont réappliquées par-dessus.
Si le serveur montre un fait que le journal ignore (série saisie dans le legacy
pendant ce temps), **le serveur gagne** et le journal s'aligne.

### 8.8 *(r2)* Plan de séance et table de transitions — l'hors-ligne sans logique de domaine

**Le problème trouvé** : hors réseau, après VALIDER, le client doit savoir si
l'état suivant est un repos avant la série k+1, un repos avant l'exercice suivant,
ou le bilan. Le calculer, ce serait recopier `console_state` (« première série de
travail en attente ») — interdit.

**La solution** : à START et à chaque ACK, le serveur fournit le **plan de séance**
avec, pour chaque série, la transition que `console_state` produirait si la série
était faite **dans l'ordre** :

| Champ | Contenu | Source |
|---|---|---|
| `plan.exercises[]` | `se_id`, identités prévue/réalisée, `set_scheme`, `guidance`, `previous`, `substitutes` | services du §8.2, pour **tous** les exercices |
| `plan.sets[]` | `set_id`, `se_id`, `index`, `kind`, `prefill_policy` (`OVERLOAD_TARGET` · `REPEAT_PREVIOUS` · `NONE`) | `SetLog` + D6 |
| `plan.on_complete[set_id]` | `REST_THEN_SET(set_id')` · `REST_THEN_EXERCISE(se_id')` · `BILAN` | **calculé serveur** par `console_state` appliqué à l'hypothèse « cette série faite » |

Le client **interprète** cette table : il ne décide pas, il suit un pointeur. Hors
du chemin nominal (substitution soumise à autorisation serveur, correction
complexe, replanification, état divergent inconnu), le client passe en
**`REQUIRES_SYNC` visible** — il garde le dernier read model connu, n'invente
aucune position, et attend le serveur (§0quater).
`REPEAT_PREVIOUS` est une règle **de présentation** (recopier la dernière saisie
validée), pas une règle de domaine.

**START et le choix de séance restent en ligne** : les identifiants de série
naissent côté serveur (`session_builder`), et la recommandation est une décision du
moteur. ~~Une séance démarrée s'exécute ensuite intégralement hors-ligne.~~
**Le chemin nominal d'une séance déjà matérialisée peut s'exécuter hors-ligne**
(série courante → valider → repos → série suivante → exercice suivant → fin).

### 8.8bis *(arbitrage 2026-10-23, D11)* Heure d'exécution d'une série — intégrité

**Règle opérateur : ne jamais faire de l'horloge murale brute de l'appareil la
seule autorité.**

| Élément | Contrat |
|---|---|
| **Ancre serveur** | chaque read model porte `server_now` ; le client enregistre le couple (`server_now`, horloge **monotone** de l'appareil au même instant) |
| **Temps écoulé monotone** | à VALIDER, le client calcule `performed_at = ancre_serveur + (monotone_maintenant − monotone_à_l'ancre)` ; une horloge murale modifiée par l'utilisateur ou par le réseau ne le déplace pas |
| **Repli sans monotone fiable** (redémarrage de l'appareil entre l'ancre et la série) | `performed_at` est marqué `estimated` ; il reste soumis aux mêmes bornes |
| **Validation serveur bornée** | accepté si `session.started_at ≤ performed_at ≤ now_serveur` ; **aucune date future** ; hors bornes ⇒ le serveur garde son heure de réception et marque la série |
| **Invariants d'ordre** | au sein d'un exercice, `performed_at` est non décroissant dans l'ordre des séries ; une violation ⇒ heure de réception + marquage, jamais de réordonnancement silencieux |
| **Sécurité** | aucune décision d'authentification, d'expiration de jeton ou de limitation de débit ne lit une heure fournie par le client |
| **Web legacy** | inchangé : heure serveur seule (`UI-CP8R`) |

### 8.9 *(r2)* Authentification mobile — le plus petit adaptateur sûr

**Contrat actuel, audité** (`app/services/auth.py`) : jeton itsdangerous signé
contenant `{"user_id"}`, cookie `session_token` `httponly`, `samesite="strict"`,
`secure` en production, durée 30 jours, **aucun état serveur** ; mots de passe
bcrypt coût 12. *(Le docstring du module dit encore `samesite=lax` ; le code pose
`strict`, l. 99 — dérive documentaire mineure.)* Deux défauts de ce contrat →
**A0** (§0ter).

| Option | Sécurité | Maintenabilité | Verdict |
|---|---|---|---|
| **Réutiliser le cookie dans RN** | le magasin de cookies natif est partagé par la pile réseau, hors coffre ; `samesite` n'a pas de sens hors navigateur ; aucune révocation ; le login rend un 303 HTML | fragile : comportement différent iOS/Android, expiration et effacement non maîtrisés | **REJET** |
| **Jeton porteur longue durée sans état** | vol = 30 jours d'accès, non révocable | simple | **REJET** |
| **Accès court + rafraîchissement rotatif révocable, coffre de l'appareil** | accès ~15 min ; rafraîchissement à usage unique, **haché côté serveur**, révocable (déconnexion, changement de mot de passe, perte d'appareil), détection de réutilisation → révocation de la famille ; jetons à **usage typé** vérifié à la lecture | une table, deux routes, une dépendance FastAPI ; standard, testable | **RETENU (D9)** |

**Forme retenue :**

- `POST /api/vnext/auth/token` `{username, password, device_label}` → vérifie via
  `verify_password` (inchangé, même politique de longueur) → `{access, refresh,
  expires_in}` ; soumis au limiteur de débit du middleware (réponse 429,
  `main.py:243` *(exploration, couverture de cette route à vérifier dans la tranche)*).
- `POST /api/vnext/auth/refresh` → rotation ; `POST /api/vnext/auth/logout` → révocation.
- `require_api_user` (dépendance FastAPI) lit `Authorization: Bearer` et rend le
  **même** `User` (`is_active` filtré) : `get_owned_session_or_404` et toute la
  propriété restent **inchangées**. Le cookie web n'est **jamais** accepté sur
  `/api/vnext/*`, et un jeton mobile jamais sur les routes web.
- Stockage client : **coffre de l'appareil** (Keychain / Keystore) pour le
  rafraîchissement ; l'accès vit en mémoire.
- **Une** table additive (`device_sessions` : `id`, `user_id`, `refresh_hash`,
  `family_id`, `device_label`, `created_at`, `last_used_at`, `revoked_at`) — tranche
  `migration` dédiée, **après A0**.
- Liens profonds : schéma d'app + liens universels / App Links sur le domaine du
  produit (fichiers d'association servis par FastAPI) pour « reprendre la
  séance » ; la réinitialisation de mot de passe **reste** un flux web.

### 8.10 *(2026-10-24, `Sb_VNEXT_MOBILE_D9_01`)* Ce que D9 a livré — amendements nommés

Les §8.1–8.9 restent la référence. Ce qui suit dit **où la livraison s'en écarte, et
pourquoi** ; aucun autre écart n'existe.

| Point | Spec | Livré | Motif |
|---|---|---|---|
| Préfixe | `/api/vnext/*` (noms de travail, §8) | **`/api/mobile/v1/*`** | surface versionnée exigée par le GO BUILD ; `vnext` désignait le chantier, pas un contrat |
| `device_sessions` | colonne `family_id` | **pas de `family_id`** ; la ligne EST la famille, le condensat tourne en place | une ligne par rotation n'apportait que de la croissance ; la détection de réutilisation est identique (secret ≠ courant ⇒ révocation de la ligne) |
| `device_sessions` | — | **+ `session_epoch`** (époque A0 recopiée à l'émission) | changement / réinitialisation du mot de passe et déconnexion web ferment l'application **sans** qu'aucun appelant de `revoke_sessions` ait à connaître la table |
| D11, hors bornes | « le serveur garde son heure de réception et **marque** la série » | heure de réception gardée ; la marque est dans la **réponse** (`performed_at_adjusted`), pas en base | une marque persistée est une colonne, que §8.6 interdit ; l'ACK la porte jusqu'au client |
| D11, tolérance | `≤ now_serveur` | `≤ réception + 120 s`, **écrit** `min(t, réception)` | un léger décalage d'horloge n'est pas une anomalie ; aucune date future n'est jamais écrite |
| `SET_COMPLETION` | réponse `200 {execution}` | réponse **`ACKNOWLEDGED`** `{op_id, set_id, applied, performed_at, performed_at_adjusted}` | le client n'a besoin que de l'acquittement ; il relit l'exécution à la reprise. `applied: false` = le fait existait déjà (§10) |
| `SUBSTITUTE` | `PUT …/substitution {name \| null}` | `POST …/exercises/{se_id}/substitute {op_id, name}` ; validé contre `compute_suggestions` (tous niveaux) ; pas d'effacement | le labo n'offre pas de retour à l'exercice prévu ; l'effacement viendra avec son geste |
| États de MISSION | `READY · RESUME · BLOCKED · NO_RECO` | `READY · RESUME · NO_MISSION` ; un refus TRAIN A au démarrage rend `409 start_blocked` | `DECLARE_EQUIPMENT` n'a pas encore d'écran mobile (hors périmètre) |
| R16 — fin de séance | — | **TERMINER** = la clôture du web (`completed`, continuité si incomplète) · **PAUSE** = aucune écriture, la séance reste `in_progress` donc `RESUME` · **ABANDONNER** = `completed` + `excluded_from_stats` | aucun état neuf : l'abandon est l'état canonique existant (« exclue » dans l'historique web, rebasculable par l'administration) ; rien n'est effacé |
| Schéma local §8.7 | `read_models`, `next_attempt_at`, `last_error`, `journal.local_state ∈ synced/rejected` | schéma N0 conservé ; l'état serveur d'une série se lit dans l'outbox (`acked` / `failed`) ; le backoff vit en mémoire | le labo accepté est adopté tel quel ; la mission hors ligne sans séance ouverte n'est pas mise en cache (écran « Hors ligne ») |
| Non livrés | `SET_CLEAR`, `REST_SKIP` serveur, `next`, `secondary` | — | `REST_SKIP` reste local (D7) ; le plan de séance porte déjà `next` et les substituts |
| Rotation | — | un jeton déjà échangé est refusé **sans délai de grâce** | conséquence assumée : une réponse de rafraîchissement perdue en route impose une reconnexion |

---

## 9. Le lab — une tranche verticale, isolée, sous drapeau

### 9.1 Parcours exigé

`MISSION → DÉMARRER (vraie reco) → EXECUTION (vrai premier exercice) → série réelle
→ REPOS → série suivante → fin d'exercice → exercice suivant`. Services canoniques
réels, compte de test, legacy disponible en parallèle, **aucun remplacement en
production**.

### 9.2 Drapeau et bascule

- Aucun drapeau par utilisateur n'existe (seulement des réglages globaux,
  `config.py:71-104`). Le lab ajoute un réglage **global** `VNEXT_LAB_USERS`
  (liste d'identifiants, vide par défaut) : ~~r1 : `/x/*` et~~ `/api/vnext/*` rend
  **404** à tout autre compte — **0 colonne**.
- ~~r1 : lien « Essayer vNext » dans le web~~ → r2 : la **bascule est
  l'installation** : l'app n'est distribuée qu'en **distribution interne** (testeurs
  iOS / piste de test interne Android) aux comptes du lab. Dans l'app, « Ouvrir en
  version classique » ouvre la **même séance** dans le legacy web (lien profond
  vers `/sessions/{id}`). Les deux lisent la même base : une séance commencée dans
  l'un se **reprend** dans l'autre.
- **Pas de redirection automatique** du web vers l'app pendant le lab.

### 9.3 Découpage en tranches — r2 (après D1–D11 **et** A0)

**Changement d'ordre r2 (`CLAUDE.md §5.5` — la centralité d'abord)** : la question
centrale n'est plus « le contrat tient-il ? » mais « **l'opérateur choisirait-il
cette app plutôt que le legacy, tout de suite ?** ». Elle passe donc **avant** les
tranches backend : le **labo de design natif N0** tourne sur **fixtures réelles**,
sans toucher au serveur.

| Tranche | Contenu | Tier `check_scope` attendu |
|---|---|---|
| **A0 — sécurité** *(indépendante de vNext, prioritaire)* | correction des deux défauts du jeton de session (§0ter) | `shared_code` minimum ; **remonter d'un cran si doute** |
| **N0 — labo de design natif** | `clients/mobile/` : **les cinq écrans seulement** (§9.4), fixtures réelles, haptique, notification locale, maintien d'écran, journal SQLite contre un faux serveur ; **build de développement sur l'appareil de l'opérateur** | `isolated` (répertoire neuf, rien d'importé ailleurs) + première CI mobile → **`ci_infra`** |
| **L0 — extraction** | `session_commands` + read models + **plan de séance / table de transitions** extraits du routeur ; **le routeur legacy les appelle** ; 0 changement de comportement | `shared_code` (broad sweep ciblé sur les tests du §1.3 + CI) |
| **L1 — API** | `vnext_api.py` + schémas Pydantic + tests de contrat (dont : **un `PUT` de série n'efface ni note, ni sensation, ni substitution TRAIN A** ; `performed_at` borné, D11) | `shared_code` |
| **L1a — auth mobile** | `device_sessions` + `mobile_auth.py` + `require_api_user` (D9) | **`migration`** |
| **L2 — intégration** | l'app N0 branchée sur l'API réelle : outbox → serveur, réconciliation, conflits, G-LOSS / G-KILL | `ci_infra` |
| **L3 — distribution interne** | builds signés, distribution aux comptes `VNEXT_LAB_USERS` | `ci_infra` · **D10** |
| **L4 — exposition et dogfood** | séances réelles en salle, mesures §10 sur **appareil**, verdict opérateur | `docs` |
| **E1 — surface de séance continue** *(extension)* | Live Activity / Dynamic Island (module Swift + extension widget) · notification continue Android (module Kotlin) | `ci_infra` |
| **E2 — raccourcis** *(extension)* | raccourcis d'app, bouton Action (App Intents), raccourcis Android | `isolated` |

### 9.4 *(r2)* Le labo de design natif N0 — avant toute migration de production

**Ne construit que :** 1 MISSION / READY · 2 EXECUTION / SÉRIE · 3 EXECUTION / REPOS
· 4 EXECUTION / EXERCICE SUIVANT · 5 SÉANCE TERMINÉE.

**Fixtures réelles** : JSON produits par les **services canoniques** sur la base de
labo semée (même méthode que les sondes du 2026-10-23 : `advice_memory.recommander`,
`explain_overload_hint`, `last_time_by_exercise_code`, `build_recap`), versionnés
avec le client et **validés contre les schémas** des read models dès que L1 existe.
Aucune valeur inventée ; une fixture de cas discriminant au minimum (reco
`BLOCKED` par l'équipement, exercice substitué, première fois sans historique).

**Objectif — une seule question :** *« L'opérateur choisirait-il ceci plutôt que le
produit actuel, immédiatement ? »* Pas la parité avec les cadres HTML : ils fixent
la hiérarchie, l'état et l'action, **pas** la forme (§11.4).

**Rendus sur appareil réel** : build de développement sur le téléphone de
l'opérateur, en salle si possible (éclairage, une main, gants), captures et
enregistrement d'écran de l'appareil — **jamais** un simulateur seul.

**Sortie de N0** : verdict opérateur `CHOISIRAIT / NE CHOISIRAIT PAS` + les portes
§10.2 mesurées sur appareil + la liste des écarts. `NE CHOISIRAIT PAS` arrête le
programme avant toute tranche backend : le coût engagé est alors celui d'un
répertoire neuf, et aucune ligne du produit n'a bougé.

---

## 10. Portes UX mesurables

### 10.1 Portes géométriques

*(r2 : sur l'app, elles se mesurent sur **appareil et simulateur** dans les zones
sûres réelles — encoche, îlot, barre d'accueil — aux tailles d'écran du plus petit
iPhone pris en charge et d'un Android 360 dp. La colonne « Mesure » ci-dessous
décrit la mesure **web** des cadres de référence ; sur l'app, son équivalent est
l'inspection de la hiérarchie de vues + capture d'appareil.)*

| Porte | Seuil | Mesure |
|---|---|---|
| G1 débordement horizontal | `scrollWidth == clientWidth` sur chaque état | script (patron `check_overflow.py`) |
| G2 exercice courant compris sans scroll | nom, série k/n, cible, guidage, précédent **au-dessus du pli** | `getBoundingClientRect` **ET** capture regardée (un compteur n'est pas la visibilité) |
| G3 série saisissable sans scroll | les deux valeurs, leurs ± et VALIDER au-dessus du pli | idem |
| G4 une action souveraine par état | exactement 1 commande primaire rendue | DOM |
| G5 cibles | toute commande primaire ≥ 44 × 44 px ; aucune commande < 24 px | `target_size_taxonomy.py` réutilisé |
| G6 pas de tableau de bord en séance | aucun graphique, aucune liste de plus d'un exercice pendant `EXECUTION` | DOM |
| G7 reduced motion | `transition-duration: 0s` partout ; parcours complet rejoué avec `reduced_motion="reduce"` | Playwright |
| G8 secondaires derrière une feuille | substituer / note / méthode : 0 contrôle visible hors feuille | DOM |

**Les cadres de référence passent déjà G1, G4, G5, G7** (mesuré : 0 débordement,
0 cible < 44 px, 1 commande souveraine par cadre à y = 742 px, 68 px de haut,
`transition-duration` = 0 s sous reduced-motion). Ce n'est **pas** une preuve pour
le client : c'est la preuve que la forme proposée est tenable.

### 10.2 Portes d'interaction (mesurées dans le lab, sur appareil)

| Porte | Seuil | Comment |
|---|---|---|
| **G-OPEN** ouverture → DÉMARRER | **1** geste sans bloqueur | parcours scripté |
| **G-VAL** VALIDER → REPOS visible | **p95 ≤ 100 ms** de l'événement d'entrée à la peinture du REPOS, **indépendant du réseau** | r2 : horodatage à l'appui (`onPressIn`) → premier cadre peint de l'état REST, instrumentés dans l'app, rapport exporté ; *(r1 : `performance.mark` web)* |
| **G-NET** même mesure sous réseau dégradé | p95 inchangé à 400 ms RTT et **hors-ligne** ; la série atteint le serveur au retour du réseau | conditionneur réseau de l'OS + mode avion réel |
| **G-LOCAL** *(r2)* commit local | p95 ≤ 20 ms entre l'appui et la fin de la transaction journal + outbox | instrumentation de l'app, appareil Android d'entrée de gamme inclus |
| **G-KILL** *(r2)* mort du processus | 50 arrêts forcés de l'app à des instants aléatoires pendant validation/synchro → **0** série perdue, **0** doublon serveur | script E2E sur appareil |
| ~~**G-NOTIF** notification à ± 2 s sur iOS~~ *(retiré par l'arbitrage du 2026-10-23 : la livraison d'une notification par l'OS n'est pas un contrat déterministe)* | — | — |
| **G-TIMER-APP** *(arbitrage 2026-10-23)* minuteur in-app — **contrat dur** | dérive **≤ 1 s** dans les scénarios testés : premier plan, arrière-plan, écran verrouillé, reprise | appareils réels |
| **G-NOTIF-DIST** *(arbitrage 2026-10-23)* notification locale de l'OS — **mesure, pas contrat** | distribution réelle publiée : médiane / p95 / pire observé, iOS et Android ; **ne fait pas échouer l'architecture** | appareils réels ; si Android est matériellement inacceptable → tranche d'extension E1 (service de premier plan / séance continue), **sans** demander de privilège d'alarme exacte |
| **G-AWAKE** *(r2)* | l'écran ne se met pas en veille pendant `EXECUTION` ; il le peut à nouveau hors séance | appareils réels |
| **G-NAV** *(r2)* zéro décision de navigation | une séance normale complète (7 exercices, 21 séries) se fait **sans aucun geste de navigation** — seulement VALIDER, ±, et éventuellement PASSER | parcours scripté + compte de gestes |
| **G-A11Y** *(r2)* | parcours complet au lecteur d'écran (VoiceOver **et** TalkBack) ; chaque changement d'état est **annoncé** (repos commencé, repos fini, exercice suivant) | appareils réels |
| **G-TYPE** *(r2)* texte dynamique | aux deux plus grandes tailles standard **et** à une taille d'accessibilité : aucune valeur souveraine tronquée, VALIDER toujours visible sans défilement | simulateur + appareil |
| **G-MOTION** *(r2)* | « réduire les animations » du système → transitions coupées, écrans jugeables ; à 60 Hz et 120 Hz, aucune image perdue visible pendant les transitions d'état | moniteur de performance de l'app sur appareil |
| **G-AUTO-SET** REPOS → série suivante | automatique à 0, sans geste | parcours scripté |
| **G-AUTO-EX** dernière série → exercice suivant | automatique (D5), sans geste | parcours scripté |
| **G-TIMER** justesse | écart ≤ 1 s après 5 min écran verrouillé puis retour ; rechargement au milieu du repos → reprise à ± 1 s | appareil iOS + Android |
| **G-LOSS** perte d'écriture | **0** série perdue sur 200 validations avec coupures réseau aléatoires | test de chaos scripté |
| **G-PARITY** | une séance faite en vNext se relit identique en legacy (`session_record`) | comparaison base |

**Référence legacy mesurée** (§1.2) : 27,8 ms de coût serveur ; la mesure perçue
sur appareil sera prise **avec la même sonde** pour les deux interfaces, sur le
même compte, afin que la comparaison décrive le même utilisateur.

### 10.3 Gardes du client vNext — de capacité, jamais de moyen

- **le client ne contient aucune règle de domaine** : garde statique sur les
  sources TS (pas de calcul de charge, pas de `min_reps`, pas de choix de séance) +
  revue ;
- **tout état rendu provient d'un read model** : tests de contrat qui rejouent les
  fixtures du serveur dans le réducteur ;
- **aucune écriture perdue** : G-LOSS en CI (Playwright, réseau coupé) ;
- **un `PUT` de série ne touche qu'une série** : test Python sur la base.

---

## 11. Reset visuel — contrat de direction artistique

Dérivé des principes produit, **pas** du polissage des cartes actuelles.

### 11.1 Principes → règles

| Principe | Règle de forme |
|---|---|
| **instrument mobile** | une colonne, pouce en bas : la commande souveraine vit **toujours au même endroit** (bas, pleine largeur, 68 px) |
| **premium, calme, minimal** | peu d'objets, beaucoup de vide utile ; aucun ornement qui ne porte pas un état |
| **physique** | valeurs manipulées par des **pavés ±** larges (52 px) ; un nombre est un objet qu'on pousse |
| **lisible en salle, contraste fort** | valeurs ≥ 56 px, `tabular-nums` ; texte ≥ 4,5:1 sur fond réel (§11.3) |
| **précis** | aucune valeur sans unité ; aucune valeur que le moteur ne calcule pas ; « 90 s par défaut » plutôt qu'un faux 90 s prescrit *(arbitrage D7 : pas de vocabulaire d'ingénierie à l'écran)* |
| **fortement à états** | **l'état change la composition entière**, pas un badge : REPOS remplace la saisie par le compte à rebours |
| **le mouvement dit la transition** | une transition = un changement d'état ; 200–280 ms ; **aucune** animation d'agrément ; reduced-motion ⇒ coupure nette, écran jugeable |
| **pas de densité de tableau de bord** | jamais deux instruments en concurrence sur un écran de séance |

### 11.2 Rôles de couleur (rôles d'abord — `AUREN_VISUAL_BACKBONE §3.1` conservé comme méthode)

| Rôle | Sens | Valeur proposée |
|---|---|---|
| `signal` | **à toi de jouer** — une seule occurrence pleine par écran | `#FFB238` |
| `system` | ce qu'AUREN produit **et le temps** (raison, guidage, repos) | `#7CCBF5` |
| `ink` / `ink-2` / `ink-3` | donnée · contexte · méta | `#F4F1EA` · `#B4B8BF` · `#8A9099` |
| `field-work` / `field-rest` | fond d'état | `#0B0C0E` · `#06141C` |
| `plate` / `plate-rest` | module posé sur le fond | `#1B1E23` · `#10293A` |
| `line` | séparation non-texte | `#2A2E35` |

**Règle qui en sort :** pendant le REPOS, **aucun ambre plein** — ce n'est pas au
pratiquant de jouer ; la commande devient un **trait** `system`.

### 11.3 Contrastes mesurés (WCAG 2.x, couple sur fond réel, 2026-10-23)

| Couple | Ratio | Plancher |
|---|---|---|
| `ink` / `field-work` · `plate` · `plate-rest` | 17,35 · 14,82 · 13,29 | 4,5 |
| `ink-2` / `field-work` · `plate` · `plate-rest` | 9,83 · 8,40 · 7,53 | 4,5 |
| `ink-3` / `field-work` · `plate` · `plate-rest` | 6,08 · 5,20 · 4,66 | 4,5 |
| `system` / `field-work` · `plate` · `field-rest` · `plate-rest` | 10,92 · 9,33 · 10,42 · 8,37 | 4,5 |
| `signal` / `field-work` · `plate` | 10,88 · 9,29 | 3,0 |
| `on-signal` / `signal` | 10,88 | 4,5 |
| `plate` / `field-work` · `plate-rest` / `field-rest` | 1,17 · 1,25 | 1,12 (plancher de perception du dépôt) |
| `field-rest` / `field-work` | **1,05** | — ⇒ **le fond ne porte JAMAIS seul l'état REPOS** : anneau, compte à rebours et libellé le portent |

Ces valeurs sont des **propositions de lab**. Elles ne deviennent des tokens de
production (`CLAUDE.md §5.4`) qu'avec la décision opérateur sur rendu.
*(r2 : la palette n'est plus figée par les cadres — voir §11.4. Le contrat qui
survit est celui des **couples mesurés** : toute palette du labo N0 republie sa
table de contrastes, mesurée sur l'appareil en luminosité maximale et minimale.)*

### 11.4 Les cinq cadres — `VNEXT_INTERACTION_REFERENCE_FRAME` *(reclassés en r2)*

| Ils GOUVERNENT | Ils NE FIGENT PAS |
|---|---|
| la hiérarchie d'information · l'état · l'action souveraine (une, en zone du pouce) · la géométrie de base (rien sous le pli qui soit nécessaire) · le principe **zéro tableau de bord** | la typographie · la mise en page exacte · la forme des composants · la géométrie des plaques · l'iconographie · la palette · le mouvement · le chrome de navigation · le langage haptique · le traitement des feuilles natives · l'affordance de saisie numérique |

**Le labo N0 a explicitement le droit d'avoir l'air sensiblement mieux.** Un écran
N0 qui s'écarte des cadres sur la forme n'est pas une dérive ; un écran qui ajoute
une seconde action souveraine, montre un tableau de bord en séance ou exige un
défilement pour valider en est une.

`docs/assets/vnext/AUREN_VNEXT_REFERENCE_FRAMES.html` — un cadre 390 × 844 par
état, chacun marqué `data-frame` ; rendu PNG @2x par capture Playwright de
l'élément `.device` (hors dépôt, cf. en-tête) :

1. `mission-ready` — MISSION / READY
2. `execution-current-set` — EXECUTION / SÉRIE
3. `execution-rest` — EXECUTION / REPOS
4. `execution-next-exercise` — EXECUTION / EXERCICE SUIVANT
5. `session-complete` — SÉANCE TERMINÉE

**Données :** gabarit `push-a` réel ; raison au format exact de `phrase_de` et
facteurs de `expliquer` ; guidage mot pour mot de `explain_overload_hint`
(`"Consolider la charge actuelle"`, `"viser 10 reps avant d'augmenter la charge"`,
relevés au labo) ; bilan = champs de `build_recap` relevés sur une `push-a`
complète (`21/21`, `0` substitution, `Pectoraux 9 · Deltoïdes latéraux 6 ·
Deltoïdes postérieurs 3 · Triceps 3`). Les **saisies historiques** (47,5 × 9…)
sont des valeurs d'utilisateur semées, pas des sorties du moteur.

**Constat de labo à remonter, sans le corriger ici :** sur un historique de six
séances dont deux LISS **sans données cardio saisies**, V3 propose encore
`liss-only` avec « La modalité la plus délaissée. » + « Mais même famille que la
dernière séance. ». Plausiblement juste (des séances LISS vides ne servent pas la
modalité), mais à confirmer par `REC-*` — c'est exactement le genre de phrase que
MISSION mettra en tête d'écran.

### 11.5 *(r2)* Langage haptique — retenu, jamais décoratif

| Événement | Retour | Pourquoi |
|---|---|---|
| `±` charge / reps | **sélection** (le plus léger) | une marche franchie, comme un cran |
| VALIDER accepté localement (t1, §8.7) | **succès** | confirme que la série est **sûre**, pas seulement touchée |
| fin du repos, app au premier plan | **impact fort**, une fois | le corps doit le sentir sans regarder |
| fin du repos, app en arrière-plan / verrouillée | **notification locale** avec vibration système | le seul canal qui traverse l'écran verrouillé |
| ouverture automatique de l'exercice suivant | **impact léger** | signale le changement d'objet, pas une réussite |
| commande refusée / invalide (409, 422, valeur hors bornes) | **avertissement** | distinct du succès au toucher |
| série refusée par le serveur (`rejected`) | **erreur** + bannière persistante | jamais un retour sans texte |

**Interdits** : retour au défilement, à l'ouverture d'une feuille, à chaque seconde
du compte à rebours, aux 3 dernières secondes, en boucle. **Respect** du réglage
système (haptique désactivée ⇒ rien) et d'un réglage in-app ; « réduire les
animations » ne coupe **pas** l'haptique, mais aucun retour ne doit être le **seul**
porteur d'un état (le texte et la forme restent, pour qui ne sent rien).

### 11.6 *(r2)* Barre de qualité native

L'objectif n'est plus « une page web propre à 390 px » mais :

- **zones sûres natives** et **usage à une main** : la commande souveraine dans la
  zone du pouce, rien de nécessaire dans le tiers supérieur pendant `EXECUTION` ;
- **séance = mode** : barre d'onglets **masquée** pendant `EXECUTION`, retour
  impossible par geste accidentel (glisser-retour désactivé dans le mode),
  sortie explicite par la feuille ;
- **saisie numérique** : par défaut **aucun clavier** — pavés ± ; un appui long ou
  un toucher sur la valeur ouvre un pavé numérique décimal, avec gestion réelle du
  clavier (la commande reste visible au-dessus) ;
- **cycle de vie** : reprise exacte après mise en arrière-plan, appel entrant,
  redémarrage ; maintien d'écran pendant la séance seulement ;
- **luminosité et éclairage de salle** : contraste mesuré à luminosité minimale ;
  aucune information portée par une nuance faible ;
- **texte dynamique** aussi grand que la mise en page le permet (G-TYPE) ;
- **VoiceOver / TalkBack** de bout en bout, annonces d'état (G-A11Y) ;
- **fluidité perçue** à 60 et 120 Hz : animations sur le fil UI, jamais dépendantes
  d'un aller-retour (G-MOTION) ;
- **feuilles natives** pour tout secondaire (substituer, note, méthode, sortir) ;
- **dépendance réseau imperceptible** pendant une séance normale (G-NET, §8.7).

**Vérités dures conservées** : pas de fausse précision scientifique, pas de score de
préparation inventé, pas de prescription de repos inventée, aucune revendication
médicale, **aucune perte de donnée cachée**.

---

## 12. Chemin des capacités natives — r2 : extensions de première classe

*(r1 comparait web et Capacitor ; sous C2 la question devient : **par quel moyen**,
et **dans quelle tranche**. Les noms de modules sont ceux de l'écosystème Expo
connus au 2026-10-23 et sont **à reconfirmer, version épinglée exacte, à
l'ouverture de N0**.)*

| Capacité | Moyen sous C2 | Tranche | Web iOS (rappel) |
|---|---|---|---|
| Haptique iOS + Android | module haptique Expo (sélection / impact / notification) | **N0** | **non** |
| Notification locale de fin de repos | module de notifications Expo, déclencheur à intervalle, planifiée à VALIDER, replanifiée à ±15 s, annulée à PASSER | **N0** | non (Web Push = serveur) |
| Maintien de l'écran allumé | module keep-awake Expo, actif seulement en `EXECUTION` | **N0** | à vérifier |
| Avant-plan / arrière-plan | `AppState` + recalcul de l'échéance + rejeu de l'outbox | **N0** | partiel |
| Persistance locale | Expo SQLite (§8.7) | **N0** | IndexedDB évinçable |
| Stockage sécurisé des jetons | module SecureStore (Keychain / Keystore) | **L1a** | — |
| Liens profonds | schéma d'app + liens universels / App Links | **L2** | — |
| Distribution native | service de build et de soumission cloud ; distribution interne puis stores | **L3** · **D10** | PWA |
| Mise à jour des correctifs JS | mises à jour à chaud du bundle JS (dans les limites des règles des stores) | **L3** | natif au web |
| Live Activity / Dynamic Island (iOS) | **module Swift ciblé** (ActivityKit) + **extension widget** ajoutée par plugin de configuration ; le compte à rebours s'affiche par l'horloge système (pas de mise à jour par seconde) | **E1** | impossible |
| Séance continue Android | **module Kotlin ciblé** : service de premier plan + notification continue avec compte à rebours ; type de service et déclaration Play **à vérifier** | **E1** | impossible |
| Bouton Action / raccourcis d'app (iOS) | App Intents (Swift, module ciblé) — « démarrer la séance du jour », « passer le repos » | **E2** | impossible |
| Raccourcis Android | raccourcis d'app statiques/dynamiques | **E2** | partiel (manifeste) |

**Pourquoi c'est « de première classe » et pas une re-plateforme future** : chaque
ligne E1/E2 est un **module ajouté** au même projet, appelé par le même réducteur ;
aucune ne demande de réécrire un écran, un contrat ou le domaine.

Ordre recommandé **après** le lab : (1) PWA + Wake Lock, (2) Capacitor + haptique +
notification locale, (3) Live Activity. Chaque étape est un **amendement** de
`Sx_UIV3_00A §9` (« Capacitor = FUTURE GATE V4 »), pas une implicite.

## 12bis. Portabilité iOS — préparation de la distribution *(notes, 2026-10-24)*

**Finalité produit (opérateur, 2026-10-24).** AUREN est une **application mobile que les gens
téléchargent pour faire leur séance**. Le site web n'est qu'un relais, pour la continuité
d'usage. Le dogfooding passe par l'app : elle est construite et servie depuis le Mac (Metro,
build de développement), puis utilisée sur l'iPhone.

**État mesuré du labo** (`clients/mobile`, non commité) :
- Expo SDK 58, React Native 0.88, build de développement (`expo-dev-client`) ;
- bundle `dev.auren.vnext.lab`, nom « AUREN Lab », portrait, iPhone seul (`supportsTablet: false`) ;
- signature par une **équipe Apple personnelle gratuite**, lue dans l'environnement au build ;
  aucun identifiant personnel n'est versionné ;
- notifications **locales** seulement (`enableRemoteNotifications: false`) ;
- données de démonstration : **aucune** connexion au backend.

| Sujet | Ce qu'il faut préparer | Quand |
|---|---|---|
| **Expiration de la signature** | un profil de signature d'équipe personnelle expire au bout de **7 jours** : le build installé le 2026-10-23 cessera de s'ouvrir vers le **2026-10-30**. Le réinstaller depuis le Mac le relance pour 7 jours. Le seul remède durable est l'Apple Developer Program. | avant chaque session de dogfooding, tant qu'il n'y a pas de compte payant |
| **Compte Apple Developer Program** (payant, annuel) | requis pour TestFlight, l'App Store et les notifications distantes | **D10**, à décider avant toute distribution hors de l'iPhone de l'opérateur |
| **Identité de l'app** | bundle et nom de production, distincts du labo (`dev.auren.vnext.lab` reste le labo), icône, écran de lancement, numérotation de version et de build | tranche de distribution |
| **Chaîne de build** | archive Xcode locale, ou service de build et de soumission cloud ; App Store Connect ; **TestFlight** (testeurs internes sans revue, testeurs externes après revue bêta) ; puis revue App Store | **L3 / D10** |
| **Connexion au backend** | **D9**, ouvrable depuis le déploiement d'A0 (2026-10-24, `ff4239d`) : sessions d'appareil, jeton dans le Keychain (SecureStore), lecture de mission et d'exécution (§8.1–8.3), outbox rejouée (§8.7) | D9, puis L1 |
| **Exigences App Store à anticiper** | **manifeste de confidentialité** de l'app et étiquette « confidentialité » d'App Store Connect (taille, poids, âge, sexe, séances : catégories santé et forme) ; **suppression du compte depuis l'app**, obligatoire dès qu'on peut créer un compte ; pas d'allégation médicale ni de « score de préparation » (règle produit déjà en vigueur) ; classification d'âge | avant la première soumission TestFlight externe |
| **Notifications distantes** | désactivées aujourd'hui, compatibles avec l'équipe gratuite. Les activer exige le compte payant, une clé APNs et une décision de produit. | après D10 |
| **Android** | même base de code (`dev.auren.vnext.lab` déclaré). Ni build ni dogfooding pour l'instant. | après iOS |

**Les points à vérifier au moment de la tranche de distribution** sont dans ce tableau. Les règles
de l'App Store, les noms de modules et les durées sont ceux connus au 2026-10-24. Ils sont à
reconfirmer, version épinglée, à l'ouverture de cette tranche.

---

## 13. Migration étrangleuse

1. **MISSION** — lecture seule, risque le plus bas, valide l'amorce et le read model.
2. **EXECUTION** — le cœur ; valide commandes, outbox, minuteur.
3. **Fin de séance / FLIGHT_RECORDER** — `build_recap` + `construire_debriefing`.
4. **LOADOUT / plan** — préférences, équipement, programmes.
5. **BODY_LEDGER** — après décision sur l'échelle de confiance (`AUREN_INSTRUMENTS §7.1`).
6. **ACCOUNT / documents** (`coach_report`, `export`, `science`, `atlas`) — en dernier ;
   les documents peuvent **rester** SSR (`AUREN_INSTRUMENTS §2bis`).

**Règles :**

- jamais deux surfaces basculées dans la même livraison ;
- **une surface ne bascule en défaut** qu'après : portes §10 vertes sur appareil,
  dogfood opérateur, parité G-PARITY, et décision opérateur versionnée ;
- **une surface legacy ne se supprime** que dans la livraison qui la remplace
  (`CLAUDE.md §5.3`) et après une période où les deux coexistent ;
- les gardes legacy d'une surface **partent avec elle**, jamais avant ;
- la bascule utilisateur reste réversible jusqu'à la suppression.
- *(r2)* **le web legacy reste le client de repli sur tout appareil** pendant toute
  la migration — une séance commencée dans l'app se termine dans le navigateur si
  l'app tombe, et inversement ; les surfaces non migrées restent atteignables
  depuis l'app par lien vers le web, jamais réimplémentées « vite fait ».

---

## 14. Risques

| # | Risque | Mitigation |
|---|---|---|
| R1 | **Duplication de logique métier** dans le client | §7 principe 1 ; `next` et `commands` fournis par le serveur ; garde §10.3 |
| R2 | **Extraction L0 qui change un comportement legacy** | déplacement pur ; suite legacy du §1.3 inchangée = preuve ; `shared_code` ⇒ broad sweep + CI |
| R3 | **Écriture partielle qui efface** (classe de défaut connue, §1.3 défaut 2) | commande par série dédiée ; test « un `PUT` n'efface ni note, ni sensation, ni substitution » ; **jamais** d'appel à `update_exercise_card` |
| R4 | **Deux interfaces divergent sur la même séance** | une seule dérivation de position (`console_state`) ; G-PARITY |
| R5 | **Perte silencieuse d'une série hors-ligne** | outbox persistée, `PENDING_SYNC` visible, G-LOSS |
| R6 | **Pré-remplissage = journaliser la cible sans l'avoir faite** (D6) | la valeur affichée est celle validée ; l'origine (`OVERLOAD`/`LAST_SET`) est portée par le read model ; dogfood mesure les validations « sans modification » |
| R7 | **Perte des gardes HTML** (gardes vertes et aveugles) | gardes de capacité §10.3 ; exposition au rendu §5.1 conservée |
| R8 | **Nouvelle chaîne de build** (CI, déploiement, `ci_infra`) | tranche L2 isolée ; CI réelle exigée avant merge (`CLAUDE.md §1`) |
| R9 | ~~r1 : Capacitor refusé à l'App Store~~ → r2 : **refus ou retard de revue store** | distribution interne d'abord (L3) ; l'app porte des fonctions natives réelles ; les correctifs JS passent par mise à jour à chaud dans les limites des règles |
| R10 | **Le lab devient la production par glissement** | drapeau `VNEXT_LAB_USERS`, 404 hors liste, distribution interne seulement, verdict §17 |
| R11 | **Nouvelle autorité visuelle par capture** — la leçon de `Sb_UIV2_HOME_RECO_BADGE_01` à l'envers | statut `VNEXT_INTERACTION_REFERENCE_FRAME` ; aucune baseline tant que l'opérateur n'a pas tranché sur rendu d'appareil |
| R12 *(r2)* | **Jeton mobile émis sur un contrat de session défaillant** | **A0 avant L1a**, sans exception (§0ter) |
| R13 *(r2)* | **Le client se met à décider hors-ligne** (tentation de recalculer la position) | table de transitions serveur (§8.8) ; garde statique : aucune référence à `min_reps`, `set_scheme` parsé, ni règle de position dans les sources TS |
| R14 *(r2)* | **Horodatage faux après synchro tardive** | D11 `performed_at` borné ; test : série hors-ligne de T, synchro à T+20 min ⇒ `completed_at` = T (± décalage) |
| R15 *(r2)* | **Fragmentation des versions** (une vieille app parle à un nouveau serveur) | contrats versionnés `/api/vnext/v1` ; le serveur sert N et N-1 ; l'app refuse proprement une version trop ancienne |
| R16 *(r2)* | **Charge de maintenance d'une pile JS/natif pour un opérateur seul** | une seule base TS ; modules natifs limités à E1/E2 ; dépendances épinglées exactement ; mise à niveau de l'outillage = tranche planifiée, jamais opportuniste |
| R17 *(r2)* | **Comptes externes et secrets de signature** | détenus par l'opérateur (D10) ; aucun agent ne les crée ni ne les lit ; secrets de CI dans le coffre du service, jamais dans le dépôt (dépôt **public**) |
| R18 *(r2)* | **Notification de fin de repos en retard sur Android** (alarmes inexactes) | publier la distribution mesurée (G-NOTIF-DIST) ; E1 (service de premier plan) si l'écart est inacceptable ; **jamais** de privilège d'alarme exacte pour satisfaire un chiffre |

---

## 15. Non-goals — Périmètre interdit

- **Aucun build d'UI de production** dans cette mission ; aucun gabarit, aucune
  feuille de style, aucun script du produit modifié.
- **Aucune migration**, aucune colonne, aucune table (y compris pour `op_id`,
  pour une durée de repos, pour un drapeau par utilisateur).
- **Aucune suppression** d'UI, de garde, de baseline ou de document.
- Aucune modification du moteur (`recommendation*`, `advice_memory`,
  `console_state`, `overload_*`, `environment_*`, `session_builder`).
- Aucun **chatbot** comme interface primaire ; l'explication est à la demande.
- Aucune **prescription de repos** inventée ; aucune **durée** de séance estimée ;
  ~~aucun **score global**~~ (superséde par **D12**, §0quinquies) ; aucune revendication
  d'activation musculaire.
- ~~r1 : React Native hors tranche~~ → r2 : **aucun projet Expo / React Native
  créé dans cette mission** ; aucun Expo en production ; aucun écran natif construit.
- **Aucun jeton d'authentification ajouté**, aucune route modifiée, aucune
  correction de sécurité appliquée (A0 attend la décision opérateur).
- Aucune réécriture de surface hors MISSION / EXECUTION pendant le lab.
- Aucun amendement **appliqué** à une spec existante, aucun marqueur
  `LEGACY_VISUAL_REFERENCE` posé : la table du §4.3 est **préparée**, son
  application attend D1–D11.
- Aucun compte de service externe créé ni configuré (D10).

---

## 16. Specs à amender ou superséder (liste explicite)

| Document | Action | Déclencheur |
|---|---|---|
| `docs/strategy/Sx_UIV3_00A_COCKPIT_CAPABILITY_CONTRACT.md` §9 | amendement **`§9bis`** — ~~r1 : option B~~ → r2 : **C2** lève « React Native REJECT » et « Capacitor FUTURE GATE V4 » pour le client mobile vNext ; la porte d'admission est **instruite** (§6.4) et reste en vigueur pour le web legacy | D1 |
| `docs/SPRINT_UI_CP8R_REPORT.md` / doctrine `UI-CP8R` (`sessions.py:452-455`, « l'horloge du client n'entre jamais dans cette écriture ») | amendement : `performed_at` client **borné** accepté pour les écritures de l'API mobile ; le web legacy garde l'heure serveur | D11 |
| `docs/AUTH_SCOPE_MATRIX.md` · `docs/SECURITY_BASELINE.md` | ajout du transport porteur de jeton, de la rotation et de la révocation | D9, A0 |
| `docs/strategy/AUREN_VISUAL_BACKBONE.md` §5bis, §2, §3.1 (valeurs), §3.5, §4 | marqueurs en ligne `LEGACY_VISUAL_REFERENCE` + nouvelle ligne au §6 | D1, D2, D8 |
| `docs/strategy/AUREN_UIUX_V3_FOUNDATION_CONTRACT.md` §4, §8, §9 (gouttières), §10 | amendement `§10bis` (D2) + marqueurs | D2, D8 |
| `docs/strategy/AUREN_UI_BLUEPRINT.md` §2.3, tableau GOLDEN/SOVEREIGN | marqueurs `LEGACY_VISUAL_REFERENCE` (portée vNext) | D8 |
| `docs/strategy/Sx_UIV3_03_VISUAL_REGRESSION_A11Y_SPEC.md` §6 | amendement `§6bis` : ne s'applique pas aux surfaces `vnext-*` | D8 |
| `docs/strategy/Sx_UIV3_02_ACTIVE_EXERCISE_CONSOLE_SPEC.md` §4 (libellés figés), ordre figé | amendement `§4bis` (libellés vNext, repos inter-exercice) | D5, D6 |
| `docs/strategy/Sx_UIV3_04_HOME_SESSION_CONVERGENCE_SPEC.md` libellés, 360 px | marqueurs ; plancher vNext = 360 × 640 et 390 × 844 | D8 |
| `docs/strategy/Sx_UIV3_01_HOME_CAUSAL_COCKPIT_SPEC.md` §3 structure figée | marqueur | D8 |
| `docs/DESIGN_DECISIONS_UIV2_SURFACES.md` Q5–Q8 | bloc daté « AMENDEMENT — portée vNext » (patron l. 149) | D8 |
| `docs/DESIGN_DECISIONS_HOME_UIV2.md` D3/D4/D5 | idem ; **D2 et D9 RETAINED** | D8 |
| `docs/strategy/AUREN_INSTRUMENTS.md` §5 | marqueur (les primitives et leurs implémentations deviennent LEGACY) ; §2–§4, §6.2bis, §7 inchangés | D8 |
| `docs/SPRINT_UIV3_VISUAL_BASELINE_REPORT.md` + `scripts/visual_contract.py` `SURFACE_STATUS` + `scripts/geometry_manifest.py:68-71` | nouvelle surface `vnext-*` ; SOVEREIGN reste **legacy** | D8 (tranche L3) |
| `docs/strategy/Sx_UI_11_SCREENSHOT_REGRESSION_BASELINE_SPEC.md`, `docs/SPRINT_Sb_UI_11_3_FINAL_AUREN_BASELINE_REFRESH_PROTOCOL.md`, `Sx_UI_02`, `Sx_UI_02b`, `SPIGNOS_VISUAL_IDENTITY_V2.md` | marqueur `LEGACY_VISUAL_REFERENCE` (historiques de fait) | D8 |
| `docs/strategy/SPIGNOS_ARCHITECTURE_AND_ROBUSTNESS_SYNTHESIS_v1.md:43` (« zéro client-state, zéro framework JS ») | marqueur `SUPERSÉDÉ` pour vNext | D1 |
| **Gardes** `tests/test_df_b_session_flow.py:66` · `tests/test_ui_cp8i_resilience_saisie.py:298` · `tests/helpers.py:171` (`assert_aucun_framework`) · `tests/test_pwa_installability.py:121` | **requalifiées en capacité** sur le legacy ; **non affaiblies** ; le client vNext reçoit les siennes (§10.3) | D2, D3, D4 — chaque requalification dans la tranche qui la rend nécessaire |
| `docs/strategy/SPEC_REGISTRY.md` | ligne `Sx_AUREN_MOBILE_EXPERIENCE_VNEXT` (ajoutée avec cette spec) | — |

---

## 17. Verdict

**`C2 ACCEPTED / SPEC GOVERNANCE UPDATED`** — arbitrage opérateur du 2026-10-23 (§0quater).

*(Historique : r1 `ARCHITECTURE DECISION REQUIRED`, option B ; r2
`ARCHITECTURE DECISION REQUIRED — C2 RECOMMENDED`. Le texte ci-dessous est le
verdict r2, conservé tel qu'écrit.)*

---

**Verdict r2 (historique) :** `ARCHITECTURE DECISION REQUIRED — C2 RECOMMENDED`

Pourquoi C2 : sous le critère r2, le plafond UX et les capacités natives
dominent ; C2 y fait presque jeu égal avec le natif complet (116,5 contre 117 sur
135, §6.4) avec **une** base de code au lieu de deux, et garde le natif comme
issue **locale** (modules ciblés), donc sans re-plateforme future. Aucun bloquant
concret n'a été trouvé dans le dépôt ; le domaine est déjà côté serveur et les
contrats du §8 ne supposent rien du client.

Pourquoi ce n'est pas `READY` : C2 lève des décisions opérateur **figées**
(`Sx_UIV3_00A §9`, `AUREN_VISUAL_BACKBONE §5bis`, `Sx_UIV3_02 §4`, doctrine
`UI-CP8R` pour D11), exige des comptes externes que seul l'opérateur peut ouvrir
(D10), et l'audit d'authentification a mis au jour une **faille de sécurité**
(A0). Chacun de ces points est un arrêt dur de `CLAUDE.md §4`.

**Ce qui fait basculer le verdict :** l'opérateur remplit le §7 de
`ADR_AUREN_VNEXT_01` (D1–D11) et décide de A0. Le premier travail est alors **A0**
(indépendant), puis le **labo de design natif N0** — qui répond à la seule
question qui compte avant tout backend : *l'opérateur choisirait-il cette app
plutôt que le produit actuel, tout de suite ?*

**ARRÊT pour arbitrage opérateur.** Aucun build n'est commencé.
