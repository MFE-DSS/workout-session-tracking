# `Sb_AUTH_PASSWORD_LENGTH_01` — fermeture de la troncature silencieuse

**Base** : `2e61aa1` · **Tier `check_scope`** : `SHARED_CODE` (traité au-dessus, §6)

---

## 1. Audit — les 8 capacités

| # | Capacité | Verdict |
|---|---|---|
| 1 | Validation à l'inscription | `auth_routes.py:309` — minimum seul |
| 2 | Validation à la connexion | `auth_routes.py:106` — **aucune** |
| 3 | Changement de mot de passe | `auth_routes.py:718` / `:732` — minimum seul sur le nouveau |
| 4 | Réinitialisation | `auth_routes.py:237` — minimum seul |
| 5 | Appels hash / verify | `app/services/auth.py:31,35` — `passlib.hash.bcrypt` |
| 6 | `CryptContext` utilisé ? | **non** — accès direct au handler `passlib.hash.bcrypt` |
| 7 | Rendu des erreurs | `error = "…"` puis `TemplateResponse(..., status_code=400)` |
| 8 | Tests auth existants | `test_auth.py`, `test_security.py`, `test_password_reset.py` — 41 tests, **aucun sur la longueur maximale** |

**Les quatre flux existaient et aucun n'était couvert.** Le brief faisait de la
couverture partielle un arrêt dur ; les quatre sont traités.

Hors périmètre, signalé : `scripts/create_user.py`, `perf_baseline.py` et
`visual_baseline_runtime.py` appellent aussi `hash_password`. Ce ne sont pas des
flux utilisateur ; sous bcrypt 5 ils lèveraient une erreur explicite plutôt que
de tronquer en silence.

---

## 2. Brainstorming / Options / Risques / Choix (CLAUDE.md §3)

**Option A — tronquer à 72 octets dans l'application.** Rejetée, et interdite par
le brief : ce serait reproduire le défaut **volontairement**. Un test interdit
désormais tout `password[:72]`.

**Option B — pré-hacher (SHA-256 puis bcrypt).** C'est la parade classique au
plafond de bcrypt. Rejetée : elle **change le format des hashes**, impose une
migration de tous les comptes, et le brief l'interdit explicitement.

**Option C — retenue : refuser au-delà de 72 octets, avec un message clair.**
Aucun hash touché, aucun compte migré, aucune migration. Le coût est reporté sur
l'utilisateur qui dépasse — et il le voit, au lieu de croire à tort qu'il est
protégé.

**Risque principal** : verrouiller des comptes existants. Traité en §5, dit et
non caché.

---

## 3. Le correctif

`app/services/password_policy.py` — source unique de la règle :

```python
BCRYPT_MAX_PASSWORD_BYTES = 72

def password_utf8_len(password: str) -> int:
    return len(password.encode("utf-8"))

def validate_password_policy(password, *, field_label=…, check_minimum=True) -> str | None
```

Retourner un message plutôt que lever une exception **épouse le motif déjà
présent** dans chaque route auth (`error = "…"` puis 400) : le câblage n'introduit
aucune forme de gestion d'erreur nouvelle.

`check_minimum=False` sert la connexion et la vérification du mot de passe
**actuel** : y appliquer un plancher verrouillerait tout compte créé avant que
`Sb_20.3` ne le relève de 4 à 8. Le **maximum**, lui, s'applique partout.

### La connexion, cas particulier

Le rejet intervient **avant** la requête base et avant bcrypt. Il ne fuit rien :
il ne dépend que de la longueur de l'entrée de l'attaquant, jamais de
l'existence du compte. La comparaison à temps constant contre le hash factice
reste intacte pour toute longueur acceptable.

---

## 4. Tests — T1 à T10

| # | Objet | Résultat |
|---|---|---|
| T1 | 72 octets acceptés | **PASS** |
| T2 | 73 octets refusés proprement | **PASS** |
| T3 | multi-octets mesuré juste — `é`×36 = 72 o, `é`×37 = 74 o, `🏋`×18 = 72 o | **PASS** |
| T4 | le jumeau surdimensionné est refusé par la politique | **PASS** |
| T5 | aucun hachage n'est atteint au-delà de 72 octets | **PASS** |
| T6 | inscription > 72 o → **400**, pas 500 | **PASS** |
| T7 | connexion > 72 o → **400**, pas 500 | **PASS** |
| T8 | changement **et** réinitialisation > 72 o → 400 | **PASS** |
| T9 | mot de passe normal : inscription + connexion inchangées ; plancher intact | **PASS** |
| T10 | aucun `password[:72]` dans `app/` ; le message ne dit jamais « caractères » | **PASS** |

**21 tests dédiés.** Un test conserve délibérément la démonstration du défaut
sous-jacent (`verify(jumeau, hash) is True`) : le jour où il tombera, c'est que
bcrypt 5 aura été adopté, et la politique sera passée de garde unique à ceinture
supplémentaire.

### Plantation

Plafond porté de 72 à 10 000 → **9 gardes indépendantes tombent**, dont les
quatre flux HTTP. Plantation retirée, fichier restauré à l'identique.

---

## 5. Acceptation

| # | Critère | Résultat |
|---|---|---|
| A1 | Politique centralisée | **PASS** — un test interdit à toute route de mesurer les octets ou de coder le plafond en dur |
| A2 | Limite en octets UTF-8 | **PASS** |
| A3 | Aucun chemin utilisateur ne passe > 72 o au hash | **PASS** — 4 flux |
| A4 | Aucun 500 sur mot de passe trop long | **PASS** — 400 partout |
| A5 | Format de hash inchangé | **PASS** — `$2b$`, vérifié par test |
| A6 | Comptes existants préservés | **PASS avec réserve** — voir ci-dessous |
| A7 | PR bcrypt #7 non incluse | **PASS** — dépendance non touchée |
| A8 | Rationnel documenté | **PASS** — `docs/SECURITY_PASSWORD_LENGTH_POLICY.md` |
| A9 | bcrypt 5 devient mergeable | **NON TENU** — l'affirmation était fausse, voir §7 |

### A6 — la réserve, dite et non cachée

Un compte dont le mot de passe dépasse 72 octets se connecte aujourd'hui avec la
chaîne complète, silencieusement tronquée. Après ce correctif, il devra saisir
ses **72 premiers octets**, ou passer par « mot de passe oublié ».

Aucun hash n'est modifié, aucun compte n'est migré, aucune donnée n'est perdue.
Mais un utilisateur concerné verra un message au lieu d'être connecté. C'est le
prix de la fermeture.

**Combien de comptes sont concernés ? Indécidable.** Les hashes sont opaques ; on
ne peut pas savoir si un secret d'origine dépassait 72 octets. Prétendre le
contraire serait faux.

---

## 6. Vérifications locales

`check_scope` a classé `SHARED_CODE`, qui n'exige pas le full sweep. **Traité
au-dessus** : l'authentification traverse tous les chemins connectés, ce qui est
exactement le doute que `CLAUDE.md` §1 dit de lever.

| Check | Résultat |
|---|---|
| ruff (fichiers touchés) | propre — le seul `E402` est ligne 52, **hors diff**, dette préexistante |
| `check_ruff_budget.py` | 281 ≤ 548 |
| `check_spec_protocol.py` | OK |
| Suite dédiée | **21 passés** |
| Suites auth existantes | **41 passés**, aucune modifiée |
| Broad sweep auth | **728 passés** |
| **Full sweep local** | **4 858 passés** en 4 min 29 |

---

## 7. bcrypt 5 — A9 ÉTAIT FAUX, correction

> **Cette section a affirmé l'inverse et se trompait.** Elle est corrigée plutôt
> que réécrite : l'erreur est instructive.

**Ce que j'avais conclu** : bcrypt 5.0.0 n'a qu'un changement cassant — `hashpw`
lève `ValueError` au-delà de 72 octets — donc, une fois la politique en place,
aucun chemin utilisateur ne peut le provoquer et la PR #7 devient mergeable.

**Ce qui est vrai** : bcrypt 5.0.0 est **incompatible avec passlib 1.7.4**,
indépendamment de la politique.

La preuve existait déjà, et je ne l'avais pas cherchée : la CI de la PR #7
(run `27494766766`, 2026-06-14, `passlib 1.7.4` + `bcrypt 5.0.0`) a échoué sur
`_stub_requires_backend` — passlib ne trouvait **aucun backend bcrypt
utilisable**, et chaque appel `bcrypt.hash()` tombait.

Le mécanisme, dans `passlib/handlers/bcrypt.py` :

```python
# détection du bug de wraparound BSD, au chargement du backend
secret = (b"0123456789" * 26)[:255]      # 255 OCTETS
if verify(secret, bug_hash):
```

**passlib hache lui-même 255 octets** pour tester son backend. Sous bcrypt 5
l'appel lève, la détection échoue, et l'authentification entière est morte. Une
politique applicative ne peut rien y faire : l'appel précède l'existence de tout
mot de passe utilisateur.

**Pourquoi je me suis trompé** : j'ai raisonné depuis le changelog de bcrypt, qui
décrit correctement le seul changement cassant *de son API publique*, sans
vérifier ce que **l'appelant** en fait. Le changelog était juste ; ma déduction
sur l'intégration ne l'était pas. La CI de la PR portait la réponse depuis deux
mois.

### Ce que bcrypt 5 exige réellement

**Remplacer passlib, pas relever une borne.** Le chemin le plus court est
d'appeler `bcrypt.hashpw` / `bcrypt.checkpw` directement : le format `$2b$` est
identique, **les hashes existants restent valides**, et passlib — non maintenu
depuis 2020 — sort de la chaîne d'authentification.

C'est un sprint à part entière. `bcrypt>=4.0,<5` reste la bonne borne, et la
**PR #7 ne doit pas être mergée telle quelle**.

### Ce qui reste vrai

La politique de 72 octets ferme la faille et vaut par elle-même. Elle sera aussi
une **précondition** du jour où l'authentification passera à bcrypt direct — mais
elle n'est pas suffisante, et ce rapport l'affirmait à tort.

---

## 7bis. Note d'origine (conservée, erronée)

bcrypt 5.0.0 a **un seul** changement cassant : `hashpw` lève `ValueError`
au-delà de 72 octets au lieu de tronquer. `hashpw`/`checkpw` subsistent, et
l'avertissement `__about__` visible dans les logs est **antérieur** (bcrypt 4.1)
et inoffensif — passlib le piège déjà.

Avant ce sprint, adopter bcrypt 5 aurait transformé les quatre flux en **500**.
Désormais aucun chemin utilisateur ne peut atteindre bcrypt avec un secret trop
long : **la PR #7 est mergeable**.

Elle demandera de relever la borne de `requirements.txt` (`bcrypt>=4.0,<5`),
posée précisément pour cette raison, et de vérifier que `passlib 1.7.4` — non
maintenu depuis 2020 — reste fonctionnel avec la version 5.

---

## 8. Limites

- La politique ne juge pas la **force** d'un mot de passe.
- Elle ne borne pas les scripts opérateur (hors flux utilisateur).
- Elle ne peut pas **détecter** les comptes déjà porteurs d'un secret tronqué.
- `passlib` reste **non maintenu**. Ce sprint réduit la dépendance à son
  comportement, il ne la supprime pas.

---

## Verdict

**FAILLE FERMÉE — sur les quatre flux, pas seulement l'inscription.**

Le défaut n'était pas théorique : mesuré sur le code livré, deux mots de passe
différents ouvraient le même compte. La correction tient en un module de
politique et quatre points de câblage — aucune migration, aucun changement de
format, aucun compte touché.

Deux choix méritent d'être relevés. **Refuser plutôt que tronquer** : tronquer
dans le code aurait reproduit le défaut volontairement, et un test l'interdit
désormais. **Mesurer en octets** : un contrôle par `len()` aurait laissé passer
37 caractères accentués — 74 octets, donc tronqués — en croyant bien faire.

La réserve A6 est réelle et n'est pas minimisée : un compte au secret trop long
devra saisir ses 72 premiers octets ou se réinitialiser. On ne peut pas savoir
combien de comptes sont concernés, et le rapport le dit plutôt que de rassurer à
tort.

---

## Annexe de clôture (post-merge)

| | |
|---|---|
| Base | `2e61aa1` |
| PR | **#126 MERGED** |
| Merge | **`aca4eb9`** via `--merge --match-head-commit 899c622` — **sans squash, sans `--admin`, sans force** |
| CI canonique | **`32118026792` — 6/6 success** |
| Sonar | gate **`OK`** — smells code neuf **20 → 0**, couverture **96,8 %**, 0 bug, 0 vulnérabilité |
| Gitar | pass |
| Threads | **0** |

### Un aller-retour Sonar, et le piège qui l'a presque doublé

Le gate **externe** est tombé rouge au premier passage (`new_code_smells_severity` 20 > 14) alors
que le job interne était vert. Une seule issue, **causée par ce sprint** : `python:S1192`, le
littéral `"login.html"` porté à **trois** occurrences par la branche de rejet. Corrigé par une
constante `LOGIN_TEMPLATE`.

**Le piège** : juste après le push du correctif, le gate affichait **encore 20**. Lu tel quel, cela
signifie « le correctif n'a rien changé » et invite à retoucher le code une seconde fois. C'était
l'analyse **précédente** — le job SonarCloud du nouveau commit tournait encore. Après vérification
de l'état du job puis relecture : **0**. Une cause, un correctif.

Changer du code sur la foi d'un nombre agrégé périmé est exactement ce que la route de diagnostic du
dépôt interdit, et ce qui a déjà coûté trois cycles CI ici.

### Ce qui n'a délibérément pas été corrigé

`auth_routes.py` contient d'autres littéraux dupliqués — `reset_password.html` (×4),
`contact.html` (×4), `page_title` (×20). Sonar ne les signale pas : ils sont **préexistants** et hors
du code neuf de la PR. Les « corriger » aurait touché des lignes non testées d'un fichier
d'authentification pour satisfaire une règle qui ne les vise pas.

### Pré-scan, et sa limite

Un pré-scan AST des trois fichiers touchés a confirmé zéro `S9073` et zéro autre `S1192` en code
applicatif neuf. Il **n'a pas** évité l'aller-retour : `S1192` compte les occurrences par fichier
entier, or mon scan mesurait le fichier tel qu'écrit sans distinguer neuf et préexistant. La leçon
n'est pas « pré-scanner davantage » mais « compter les littéraux du fichier, pas seulement les
siens ».

### L'erreur la plus coûteuse du sprint n'était pas dans le code

A9 affirmait que bcrypt 5 devenait mergeable. **C'était faux** (§7), et la preuve dormait dans la
CI de la PR #7 depuis deux mois. J'ai déduit une conclusion d'intégration depuis un changelog
d'API, au lieu d'aller lire le seul run qui avait réellement installé `passlib 1.7.4` avec
`bcrypt 5.0.0`.

Un changelog dit ce qu'une bibliothèque change. Il ne dit pas ce que son appelant en fait. La règle
à retenir : **quand une PR de dépendance a déjà tourné, lire son échec avant de raisonner sur sa
faisabilité.**
