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
| A9 | bcrypt 5 devient mergeable | **PASS** — voir §7 |

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

## 7. bcrypt 5 devient mergeable (A9)

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
