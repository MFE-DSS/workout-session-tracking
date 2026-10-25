# Sb_VNEXT_MOBILE_D9_01 — le pont vers le vrai backend

**Statut** : ✅ MERGÉE (PR #282, `bca942d`) · **Branche** : `sb/vnext-mobile-d9-01-real-backend-bridge` · **Base** : canonique `07c0eea`
**Spec** : `Sx_AUREN_MOBILE_EXPERIENCE_VNEXT_SPEC.md` §8 (contrats), §8.9 (D9), §8.10 (écarts nommés de cette tranche)

Le labo `N0` accepté devient la première tranche verticale **connectée** :

```
CONNEXION RÉELLE → MISSION RÉELLE → DÉMARRAGE RÉEL → EXÉCUTION
  → SÉRIE CONFIRMÉE SUR L'APPAREIL → OUTBOX SÛRE HORS LIGNE → SYNCHRO FASTAPI
  → HISTORIQUE RÉEL, avec une sortie de séance (R16)
```

Le parcours d'entraînement n'est **pas** redessiné : MISSION / SÉRIE / REPOS / EXERCICE
SUIVANT / BILAN, une action primaire, l'haptique, le journal et l'outbox SQLite, le
modèle d'échéance du repos et le mouvement réduit sont ceux du labo, adoptés tels quels.

---

## 1. Brainstorming · Options · Risques · Choix retenu (`CLAUDE.md §3`)

### 1.1 Audit du cycle de vie d'une séance — avant tout code (R16)

Mesuré dans le code (`app/enums.py:21`, `routers/sessions.py`, `routers/admin.py`) :

| Fait | Constat |
|---|---|
| Statuts | **deux** : `in_progress`, `completed` (« Only two states in V1 ») |
| Clôture | `POST /sessions/{id}` `action=end` : `ended_at`, `completed`, étiquettes implicites figées, puis continuité si la séance est **matériellement incomplète** (`completion_of`, < 50 %) — « séance terminée à N séries sur M, travail reporté, non supprimé » |
| Reprise | `latest_open_session` = la séance `in_progress` la plus récente, sans borne de temps |
| Suppression | admin seulement, avec confirmation — **efface** les faits |
| Exclusion | `excluded_from_stats`, rebasculable ; l'historique web l'affiche **« exclue »** ; KPI, exposition, récupération et scoring l'ignorent |

**Verdict de l'audit : aucune migration pour R16.** Les trois sémantiques ont déjà
leur représentation canonique :

| Choix R16 | Représentation | Ce qui n'est PAS fait |
|---|---|---|
| **TERMINER MAINTENANT** | la clôture du web ; la fin anticipée est **dérivée** des séries (`completion_of`) et la continuité l'enregistre comme le web | aucun motif inventé, aucune série complétée ou effacée |
| **METTRE EN PAUSE** | **aucune écriture** : la séance reste `in_progress`, donc la mission rend `RESUME` | — |
| **ABANDONNER LA SÉANCE** | `completed` + `excluded_from_stats` — l'état « exclue » existant | **rien n'est effacé** ; les séries restent en base et ne comptent plus ; pas de continuité (on ne reporte pas le travail d'une séance qu'on renonce à compter) |
| **ANNULER** | rien | — |

### 1.2 La migration — démontrée inévitable, isolée

`users.session_epoch` (A0) révoque **tout** un compte. Deux exigences de D9 n'ont aucune
expression sans état serveur **par appareil** : la déconnexion mobile qui ne révoque que
**son** appareil, et le refus d'un jeton de rafraîchissement **déjà échangé** (un jeton
signé sans état reste valide jusqu'à son expiration). D'où **une** table additive,
`device_sessions` (`z7a2u8v9x20`), née vide, dans son **propre commit**, toutes portes de
migration passées (§5). C'est l'exception nommée par la spec (`§8.6`, `§8.9`).

### 1.3 Options et choix

| Question | Options | Choix | Pourquoi |
|---|---|---|---|
| Jeton d'accès | JWT · itsdangerous signé | **itsdangerous**, sel `auren.auth.access.v1`, 15 min | le dépôt signe déjà ainsi (A0) ; pas de dépendance neuve ; usage typé tenu deux fois (sel + `purpose`) |
| Rafraîchissement | ligne par rotation · condensat tourné en place | **en place** (`rt1.<id>.<secret>`, SHA-256) | même détection de réutilisation, sans croissance ; la ligne est la famille |
| Révocation globale | marquer les lignes dans `revoke_sessions` · recopier l'époque | **recopier l'époque** à l'émission | aucun appelant de `revoke_sessions` n'a à connaître la table ; impossible d'en oublier un |
| Démarrage | extraire la composition dans un service · l'appeler par le module du web | **les fonctions du web, appelées par leur module** (`web_sessions._poser_adaptations`, `_enregistrer_episode_de_conseil`) | une garde existante remplace `routeur._poser_adaptations` par `monkeypatch` : une extraction l'aurait aveuglée, et changé le web. Ainsi une seule fonction couvre les deux routes, et le web n'est pas touché |
| Écriture d'une série | réutiliser le formulaire d'exercice · une commande par série | **une commande par série** (D3) | le formulaire réécrit note, sensation et substitution absentes (`partial-form-replacement`) |
| D11 hors bornes | refuser (422) · heure de réception | **heure de réception, signalée dans l'ACK** (`§8.8bis`) | un fait réel n'est jamais perdu pour une horloge d'appareil |
| Remplacement en séance | le laisser `REQUIRES_SYNC` à vie · le synchroniser | **commande `SUBSTITUTE`** dans l'outbox, avant les séries | sinon les séries faites sur le remplaçant seraient enregistrées sous le nom prescrit : un faux fait |
| Client | réécrire `App.tsx` · une seconde racine | **`ConnectedApp.tsx`**, choisie par `EXPO_PUBLIC_API_URL` ; le labo reste intact | le labo reste l'outil de design hors ligne ; aucun risque sur ses preuves |

### 1.4 Risques

| Risque | Parade |
|---|---|
| Réutiliser le cookie web comme session native | `require_api_user` ne lit **que** `Authorization` ; garde « le cookie n'ouvre pas l'API » et « le jeton n'ouvre aucune route HTML » |
| Deux rafraîchissements parallèles dépensent le même jeton → révocation | une seule rotation en vol côté client (`AuthSession`) ; côté serveur, `UPDATE … WHERE refresh_hash = <présenté>` conditionnel |
| Réponse de rafraîchissement perdue | **assumé** : reconnexion (aucun délai de grâce — §8.10) |
| Séance close avant ses séries | l'outbox est FIFO et s'arrête au premier échec transitoire ; fin et abandon y passent **après** les séries |
| Lab → serveur réel | base locale distincte (`auren.db` ≠ `auren-n0-lab.db`) : aucune commande de labo ne peut atteindre le vrai backend |
| Déconnexion qui ferait disparaître des séries | refusée tant qu'une commande n'est pas partie (`§8.4`) |
| Historique de séance absent de l'appareil | la carte « Ton programme » du bilan est **omise** plutôt qu'affichée à 1/N (aucun read model ne porte l'historique ; hors périmètre) |

---

## 2. Modèle d'authentification

| Élément | Réalisation |
|---|---|
| Accès | signé, `{purpose: access, user_id, epoch, dsid}`, 900 s, **mémoire seule** |
| Rafraîchissement | `rt1.<dsid>.<secret 256 bits>`, condensat SHA-256 seul en base, **tourné à chaque usage** ; présenter un secret non courant **révoque l'appareil** ; inactif 30 jours ⇒ reconnexion |
| Stockage client | `expo-secure-store`, Keychain `AFTER_FIRST_UNLOCK_THIS_DEVICE_ONLY` — ni AsyncStorage, ni SQLite, ni fichier, ni journal (gardes `authSession.test.ts`) |
| Révocation | appareil seul (déconnexion mobile) · compte entier (époque A0 : mot de passe changé ou réinitialisé, **déconnexion web — forme E**) |
| Temps | horloge serveur seule ; ni `performed_at` ni en-tête `Date` n'entrent dans une décision d'auth (garde) |
| Débit | la connexion mobile partage le quota de `/login` |
| Journaux | `device_auth.py` n'écrit aucun log (garde AST) ; aucun secret dans les journaux capturés (garde `caplog`) |

## 3. Surface `/api/mobile/v1`

| Route | Rôle |
|---|---|
| `POST /auth/login` · `POST /auth/refresh` · `POST /auth/logout` · `GET /auth/me` | connexion, rotation, révocation de CET appareil, identité |
| `GET /mission` | `READY` (recommandation servie V3 + mémoire, identité de décision) · `RESUME` (séance ouverte, position comptée) · `NO_MISSION` |
| `POST /sessions` | `START` : composition du web + **409 `session_open`** ; refus TRAIN A ⇒ 409 `start_blocked` ; rend le plan d'exécution |
| `GET /sessions/{id}/execution` | le plan entier (exercices, séries, table `on_complete`, séries faites, curseur, actions permises) |
| `PUT /sessions/{id}/sets/{set_id}` | une série ; idempotente par nature ; D11 borné |
| `POST /sessions/{id}/exercises/{se_id}/substitute` | remplaçant proposé par le serveur, avant la première série |
| `POST /sessions/{id}/finish` · `POST /sessions/{id}/abandon` | R16 |

Aucune route HTML n'a changé ; aucune route de cette API ne rend de HTML (garde).

## 4. Le client

- **Écriture locale d'abord** (inchangée depuis N0) : la série et sa commande dans **une**
  transaction SQLite exclusive, haptique, REPOS immédiat ; la synchro est asynchrone.
- **Outbox → serveur** (`src/sync/syncEngine.ts`) : FIFO, une commande à la fois ;
  transitoire (réseau, 5xx, 429, 401 après rotation) ⇒ `pending`, arrêt du drain, reprise
  seule avec backoff ; refus répétable (404/409/422) ⇒ `failed`, visible, gardé, renvoyable.
  Une commande `inflight` laissée par un arrêt forcé repart au démarrage — le serveur
  acquitte un fait qu'il détient déjà.
- **Reprise** (`src/sync/reconcile.ts`) : au relancement, journal d'abord, puis
  rafraîchissement, état canonique, réconciliation, écran **REPRENDRE**.
- **États secondaires calmes** : hors ligne, reconnexion nécessaire, à vérifier — une
  ligne sous l'en-tête, rien sur le chemin nominal ; la série au repos dit
  « enregistrée sur l'appareil » → « enregistrée sur AUREN » → « refusée par AUREN ».
- **R16** : ✕ à gauche de l'en-tête (l'action de séance, distincte du ⋯ d'exercice) →
  feuille système iOS : Terminer maintenant · Mettre en pause · Abandonner la séance
  (destructif) · Annuler.

## 5. Vérifications

| Porte | Résultat |
|---|---|
| `check_scope` | **MIGRATION** |
| `check_alembic_drift` · `check_schema_snapshot` · `check_migration_patterns` · `check_migration_roundtrip` | OK · OK · OK · OK (58 objets avant et après aller-retour) |
| `check_auth_scope_matrix` | OK (matrice complétée) |
| Tests D9 backend | `test_d9_mobile_auth.py` + `test_d9_mobile_sessions.py` — **76 verts** |
| Mutations (arbre jetable, `app` vérifié résolu dans cet arbre) | **16/16 détectées**. Premier passage 12/14 : les deux survivantes retiraient UNE de deux couches redondantes (condensat + `UPDATE` conditionnel ; usage + sel). Aucune faille, mais aucune garde ne tenait une couche seule : deux gardes ajoutées (usage lu sous le bon sel ; sel propre), mutation de réutilisation retirant les deux couches |
| Client | `tsc` propre · **97 tests jest** (auth, outbox → routes, moteur de synchro, réconciliation, R16, labo) |
| Sweep local complet (`run_local_sweep.sh`) | **369/369 fichiers, tous les lots verts**, aucun fichier sauté — lancé sur le commit backend (`7e458b3`) ; l'alignement D11 (`8bab76d`) est couvert par les 76 tests ciblés et les mutations |
| gitleaks | premier passage CI **rouge** : le mot de passe factice d'un test (`generic-api-key`, entropie 3,5) — pas un secret, mais la porte vaut pour tous. Corrigé à la convention du dépôt (`newpass123`) et **replié dans le commit d'origine** (branche non mergée réécrite, accord opérateur) : aucune exception ajoutée à la porte. Plage de la PR rescannée : 0 fuite |

## 6. Porte physique (§14) — iPhone 15 Plus, iOS 27.0.1, backend réel du Mac, compte dédié

Build de développement native reconstruite (module `expo-secure-store`) ; backend = ce code
FastAPI sur le réseau local, base SQLite dédiée, compte de test `dogfood_d9`.

| Porte | Observé | Preuve serveur |
|---|---|---|
| A — connexion | connexion réussie depuis le téléphone (`POST /auth/login` 200 depuis l'iPhone) | session d'appareil `iPhone AUREN` créée, non révoquée |
| B — mission réelle | Push A — *Pecs épaisseur + Delts + Triceps*, phrase et raisons du moteur servi | `GET /mission` = recommandation V3 + mémoire |
| C — un démarrage, une séance | un appui sur Démarrer | **exactement 1** séance (`push-a`, `in_progress`) |
| D — séries | série confirmée, REPOS immédiat | série `5,0 kg × 6` en base, `completed_at` = l'heure **ancrée** de l'appareil (ms près) — D11 tenu |
| R16 — rendu | ✕ en haut à gauche → feuille système « Terminer maintenant / Mettre en pause / Abandonner / Annuler » | **validé par l'opérateur** (« il est très bien ce truc ») |
| E, F, G | **non jouées sur appareil** — hors ligne + arrêt forcé, reprise, TERMINER / ABANDONNER sur iPhone | couvertes par les tests (outbox, rejeu, réconciliation, fin, abandon) ; merge sur décision explicite de l'opérateur (« GO MERGE ») avant ces trois portes |

Incident de porte, corrigé dans la tranche : l'écran de connexion envoyait **deux** requêtes
par appui (le « go » du clavier et le bouton, avant que l'état `busy` n'arrive) — garde par
référence ajoutée. Le premier échec de connexion était un mot de passe de test ambigu
(`l`/`I`), pas l'application.

### 6.1 Retour de dogfood (opérateur, 2026-10-25) — R17 à R20

| # | Constat | Traitement |
|---|---|---|
| R17 | ⋯ de l'exercice « pas customisé » : il disait encore « Journal local du labo » et proposait un remplacement que le serveur refuserait | **corrigé ici** : « Journal de l'appareil » dans l'app connectée ; remplacement affiché *plus possible* dès qu'une série de l'exercice est enregistrée (`can_substitute`) |
| R18 | MISSION : raison en « mais » (« jamais fait, mais … déjà bien servis sur 14 jours ») — l'info doit être **centrée, en formats**, pas en prose concessive | **tranche suivante** (refonte visuelle de MISSION) — texte produit par l'explication servie (`REC-CP3/CP5`) |
| R19 | doublon « 14 jours » : « Mesuré · 14 derniers jours » répète la raison ; à remplacer par une **chronologie des 14 derniers jours** avec les séances | **tranche suivante** — exige un read model d'historique, absent aujourd'hui |
| R20 | le triptyque *pecs épaisseur · delts · triceps* doit être **représenté visuellement**, avec une DA propre à chaque famille (push, pull, legs…) sur l'accueil | **tranche suivante** — direction artistique, hors périmètre D9 (`§12`) |

## 7. Relecture des décisions (`CLAUDE.md §5.2`)

Les relevés `DESIGN_DECISIONS_HOME_UIV2.md` / `DESIGN_DECISIONS_UIV2_SURFACES.md` gouvernent
les surfaces **web** : **non concernés** (aucune route HTML touchée). Le relevé applicable au
client mobile est la spec vNext (`§0quater`, `§0quinquies`) :

| Décision | Verdict |
|---|---|
| D1 — React Native + Expo + FastAPI | **respectée** |
| D2/D4 — client `clients/mobile/`, rien dans `app/static/` | **respectée** |
| D3 — une commande par série | **respectée** (`PUT …/sets/{set_id}`) |
| D5 — une action primaire | **respectée** : R16 est une action **secondaire** (✕), la primaire reste Valider / Passer le repos |
| D6 — préremplissage (labo) | **respectée**, sans changement |
| D7 — 90 s par défaut, jamais « repli » affiché | **respectée** |
| D8 — mouvement réduit, haptique | **respectée**, inchangées |
| D9 — accès court + rafraîchissement tournant révocable, coffre de l'appareil | **respectée** (écarts nommés `§8.10`) |
| D10 — distribution (signature) | **non concernée** |
| D11 — heure ancrée + bornes serveur | **respectée** (`§8.8bis`, aligné dans `8bab76d`) |
| D12 — score de séance + récompense | **non concernée** (bilan inchangé) |
| D13 — premier lancement / profil d'entrée | **non concernée** : l'app connectée part du compte existant ; l'accueil D13 reste dans le labo — **à reprendre** avec la refonte MISSION (R18–R20) |
| D14 — récupération d'abord | **respectée** : la mission est celle du moteur servi, non recalculée |
| O1 — « l'IA » | **non concernée** par cette tranche (texte du bilan hérité du labo, inchangé) |

**Verdict :** pont livré et mergé. L'app connectée tient le parcours réel de bout en bout sur iPhone (portes A–D et rendu R16 observés). Les portes E–F–G restent à jouer sur appareil ; elles le seront au premier dogfood en salle de la tranche suivante.

---

## Closeout

| | |
|---|---|
| PR | [#282](https://github.com/MFE-DSS/workout-session-tracking/pull/282) — merge commit, tête épinglée `47dbd60` |
| Merge | `bca942d493fa8abdc66cb25040a39a87873c9fb9` |
| CI canonique | run `40170553004` sur `bca942d` — **verte** |
| Sonar (PR) | gate **OK** — couverture du nouveau code 96,9 %, 0 bug, 0 smell, 0 vulnérabilité |
| Threads de revue | 0 |
| Migration en production | `z7a2u8v9x20` (`device_sessions`) — **non déployée** : la production n'a pas encore de client mobile ; le déploiement suit la distribution (L3, D10) |

### Incidents résolus dans le périmètre

1. **gitleaks** — le mot de passe factice d'un test pris pour une clé. Remplacé par la convention du dépôt et replié dans le commit d'origine (réécriture de la branche non mergée, accord opérateur) : la porte n'a reçu aucune exception.
2. **Shard 1** — la garde « aucune route mobile ne rend de HTML » lisait `app.main.app.routes` : liste vide en CI (FastAPI 0.141 du lock), pleine en local (0.135). Elle lit désormais l'OpenAPI de l'application servie, et mord.
3. **bandit B105** importé par Sonar (CRITICAL côté vulnérabilités) — `"token_type": "Bearer"` lu comme un mot de passe. Le schéma est une constante nommée ; aucune adjudication.

### Ce qui reste ouvert

- Portes E–F–G sur appareil.
- Notes de dogfooding R6, R8–R14 (tranche suivante, exécution) ; R18–R20 (refonte MISSION) ; R1, R2, R4, R5, R7 (assets — cahier des charges remis à l'opérateur le 2026-10-25).
- L3 distribution : programme Apple Developer payant (D10), décision opérateur.
