# SPRINT Sb_CI_02_2_AUTH_FIXTURE_FASTPATH — retirer bcrypt du chemin chaud des tests (RAPPORT)

**Base canonique :** `9dc4815` · **Branche :** `sb/ci-02-2-auth-fixture-fastpath` · **Tier :** **CI_INFRA / SHARED TEST INFRA**
**Livré sous** DELIVERY AUTONOMY ENVELOPE (skill `auren-sprint-from-spec`).

## 1. Problème

`Sb_CI_02_1` a supprimé le coût des PR non-runtime, **sans rien changer** au cas runtime
(12 min 45 s, volontairement). Le poste dominant restant est la fixture générique `client` :
elle payait **deux opérations bcrypt(cost 12) par test authentifié** —
`hash_password("testpass")` à la création de l'utilisateur, puis `verify_password` via un
`POST /login`. Avec **~1 400 tests** prenant `client`, c'est l'essentiel du temps de suite.

## 2. Ce qui est livré

| Fichier | Changement |
|---|---|
| `tests/helpers.py` | `TESTPASS_BCRYPT_HASH` (hash bcrypt **réel** de `"testpass"`, `$2b$12$`) + `TESTPASS_PLAIN`. Contrat partagé, une seule définition. |
| `tests/conftest.py` | La fixture stocke le hash **précalculé** (même mot de passe) et **frappe le cookie via le helper de production** `create_session_cookie`, puis laisse **httpx parser lui-même** l'en-tête `Set-Cookie`. Plus aucun bcrypt, plus aucun aller-retour HTTP de login. |
| `tests/test_auth_fixture_fastpath.py` (**neuf**) | 15 tests |
| docs | ce rapport + registry |

**Inchangé, comme exigé** : fixture `client` **function-scoped** · **une base SQLite par test** ·
reset de module applicatif par test · `TestClient` + lifespan par test · xdist ·
**comportement d'authentification en production** · **coût bcrypt en production** · tous les
tests existants.

## 3. Décisions de conception

**Le contrat de signature n'est jamais dupliqué.** Le cookie est produit par la fonction de
production `create_session_cookie`, puis **injecté via `httpx.Cookies.extract_cookies`** — donc
c'est httpx qui parse l'en-tête réel. Si le contrat change (nom, flags, durée), la fixture suit
automatiquement.

**Le hash stocké est un vrai bcrypt du même mot de passe.** Conséquence voulue : les tests qui
exercent la **vraie** route `/login` continuent d'exécuter le hash/verify complet. Un test pinne
que `verify_password("testpass", HASH) is True`, donc une évolution de passlib/bcrypt échouerait
**bruyamment** au lieu de casser silencieusement tous les tests de login.

**Le login n'a aucun effet de bord** (`auth_routes.py:90-117` : aucune écriture, pas de
`last_login`) — le contourner dans la fixture générique est **comportementalement équivalent**.

## 4. Piège réel rencontré et corrigé

Première implémentation : `client.cookies.set(SESSION_COOKIE, token)`. Le client était bien
authentifié… **mais le logout ne déconnectait plus**. Cause : une entrée de jar posée à la main
n'a pas le même domaine qu'un cookie posé par le serveur — httpx normalise l'hôte sans point en
`testserver.local` avec `domain_specified=False` —, donc le `delete_cookie` du serveur **ne
matchait pas** l'entrée. Poser `domain="testserver"` explicitement casse l'authentification
(règles de domain-matching de `http.cookiejar`).

**Correctif** : ne pas reproduire ces détails à la main — laisser **httpx extraire le cookie de
l'en-tête de production**. Parité exacte avec un vrai login. C'est `test_logout_still_clears_the_session`
qui a attrapé le défaut ; sans lui, la régression serait passée.

## 5. Tests

**Second piège attrapé, dans mes propres tests.** Le test de falsification retournait le
**dernier** caractère du token. Il passait isolément mais a **échoué au full sweep** : en
base64url, le caractère final porte des **bits inutilisés**, donc selon le token — qui change
chaque seconde via l'horodatage `itsdangerous` — la modification peut décoder vers les **mêmes
octets** et rester valide. Test **non déterministe**, remplacé par deux falsifications
déterministes par construction : un token **signé avec une autre clé**, et un token **tronqué de
sa signature**. Diagnostiqué, pas relancé jusqu'à ce que ça passe.

`tests/test_auth_fixture_fastpath.py` — **16 passés** :
hash précalculé vérifie réellement `"testpass"` (et rejette un mauvais mot de passe) · l'utilisateur
est stocké avec ce hash exact · client authentifié · **le cookie décode vers le vrai `user_id`**
via le lecteur de production · cookie **absent** → 303 `/login` · cookie **signé avec une autre
clé** → 303 · cookie **tronqué de sa signature** → 303 · cookie **poubelle** → 303 · **logout**
déconnecte réellement · la **vraie** route `/login` réussit
avec le mot de passe en clair · échoue avec un mauvais · **espion prouvant que `/login` appelle
toujours `verify_password`** (garde anti-« optimisation » future de la production) · isolation
propriétaire (non-propriétaire → 404) · **une base par test** (marqueur écrit / base vierge) ·
**pas de fuite d'état de cookie** entre tests.

Tests d'authentification dédiés (login succès/échec, hachage, rate limiting, reset de mot de
passe, falsification, logout) : **inchangés**, ils passent toujours par les chemins de production.

## 6. Mesures

**Commande identique avant/après** :
`pytest -n auto --dist worksteal --ignore=tests/test_v1_acceptance.py --cov=app --cov-report=xml --cov-report=term -q`

| Mesure | Avant | Après |
|---|---|---|
| Tests | 2981 | **2997** (+16) |
| Couverture | 92.26 % | **92.29 %** |
| Workers xdist (`-n auto`) | 10 | 10 |
| Wall-clock local | **386,44 s** (6:26) | **170,04 s** (2:50) — **2,27×** |

⚠️ **Nuance d'honnêteté sur le wall-clock local** : cette machine est bruitée — la même charge a
mesuré 279 s, 386 s et **533 s** selon la contention. Le 533 s a été observé sur une première
exécution « après » et **n'était pas une régression** : deux mesures **contrôlées** ci-dessous le
démontrent, et la ré-exécution au calme donne 170 s. Le chiffre de 2,27× n'est donc pas présenté
seul.

**A/B dos-à-dos, même état machine, 105 tests client** (seul le conftest change) :

| Variante | Durée |
|---|---|
| Sans fastpath (conftest d'origine) | **46,76 s** |
| Avec fastpath | **17,04 s** |

⇒ **2,75× plus rapide, −283 ms par test**.

**Micro-benchmark déterministe du chemin modifié** (médiane sur 10 itérations) :

| Chemin | Médiane |
|---|---|
| Ancien : `hash_password` + `POST /login` | **390 ms** |
| Nouveau : constante + frappe du cookie | **~0 ms** |

⇒ **−390 ms par test authentifié**, soit ~1 400 × 390 ms ≈ **9 minutes de CPU retirées** par run,
réparties sur les workers xdist.

**Le chiffre qui fait foi est celui de la CI GitHub** (runners homogènes) — relevé au closeout.

## 7. Interdits tenus

**Aucun** monkeypatch global de bcrypt · **aucun** mode fast-auth en production · **aucun**
raccourci `APP_ENV` dans l'authentification de production · **aucun** test d'authentification
affaibli · **aucune** modification du cycle de vie ou de l'isolation DB · **aucun** partage de
`TestClient`/app/DB entre tests · **aucune** touche à l'architecture de purge `sys.modules` ·
**aucune** touche au rate limiting · **aucun** template de base par worker.

## Verdict

**Verdict :** ⏳ **Sb_CI_02_2_AUTH_FIXTURE_FASTPATH — en validation CI.** Le double bcrypt par
test authentifié est retiré de la fixture générique **sans toucher** à l'isolation, au cycle de
vie, ni à l'authentification de production — celle-ci reste exercée par ses tests dédiés, et un
espion garantit que la route `/login` appelle toujours `verify_password`. **Suite complète
386,44 s → 170,04 s (2,27×), 2997 passés, couverture 92,29 %** ; confirmé par un A/B contrôlé
(**2,75×** sur 105 tests client) et un micro-benchmark déterministe (**−390 ms** par test
authentifié). **Deux défauts trouvés et corrigés dans ce sprint même** : le logout cassé par un
cookie posé à la main, et un test de falsification non déterministe — les deux diagnostiqués,
jamais contournés.
