# `Sb_AUTH_PASSLIB_TO_BCRYPT_DIRECT_01` — passlib sort du chemin d'authentification

**Base** : `cfbfd17` · **Tier `check_scope`** : `SHARED_CODE` (traité au-dessus, §6)

---

## 1. Audit — les 8 capacités

| # | Capacité | Verdict |
|---|---|---|
| 1 | `CryptContext` instancié où ? | **nulle part** — usage direct du handler `passlib.hash.bcrypt` |
| 2 | Appels `hash_password` | `auth_routes.py:237, 309, 732` + 3 scripts opérateur |
| 3 | Appels `verify_password` | `auth_routes.py:106` (login), `:718` (changement) |
| 4 | Format des hashes | `$2b$12$…` — bcrypt 2b, coût 12 |
| 5 | `bcrypt.checkpw` sur hashes existants | **compatible, mesuré** (§2) |
| 6 | Politique 72 octets avant hash | oui, `Sb_AUTH_PASSWORD_LENGTH_01`, 4 flux |
| 7 | Tests auth existants | 79 sur 5 fichiers, dont un qui **épingle un hash produit par passlib** |
| 8 | Messages d'erreur | motif `error = "…"` puis 400 |

**passlib n'apparaissait qu'à un seul endroit du runtime** : `app/services/auth.py:17`.
Tout le reste était commentaires et tests.

---

## 2. La compatibilité, mesurée avant d'écrire une ligne

```
hash passlib      : $2b$12$bt8DQV53UjYe/gVHv9FIl.…
checkpw(passlib)  : True          ← bcrypt direct vérifie un hash passlib
checkpw(mauvais)  : False

hash direct       : $2b$12$7ghyFGEiko0sFKFPk3DgMO…
passlib.verify    : True          ← et passlib vérifie un hash direct
```

Même ident, même coût, compatibilité **dans les deux sens**. La migration est
donc transparente : aucun hash réécrit, aucun compte migré, aucune
réinitialisation forcée.

---

## 3. Brainstorming / Options / Risques / Choix (CLAUDE.md §3)

**Option A — garder passlib et l'isoler derrière une façade.** A1 l'autorise
(« ou isolé derrière une compatibilité documentée »). Rejetée : isoler une
bibliothèque qui **ne peut pas fonctionner** avec la version cible ne débloque
rien. Le problème n'est pas l'API de passlib, c'est sa sonde de backend.

**Option B — `CryptContext` avec plusieurs schémas** pour préparer une rotation
d'algorithme. Rejetée : c'est *plus* de passlib, et aucune rotation n'est
demandée.

**Option C — retenue : appeler bcrypt directement.** Trois fonctions,
`hashpw`/`checkpw`/`gensalt`, toutes présentes en bcrypt 5. Le format ne bouge
pas, donc la migration est invisible pour les données.

**Risque principal** : rendre invérifiables les hashes existants. Neutralisé
avant d'écrire le code (§2), et **déjà épinglé par un test qui existait** —
`test_precomputed_hash_really_is_testpass` vérifie un digest produit par passlib.

---

## 4. Le changement

```python
BCRYPT_ROUNDS = 12          # ce que passlib utilisait par défaut

def hash_password(plain):
    if is_password_too_long(plain):
        raise PasswordTooLongError(TOO_LONG_MESSAGE)
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt(BCRYPT_ROUNDS)).decode("utf-8")

def verify_password(plain, hashed):
    if is_password_too_long(plain):
        return False
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
```

### Deux comportements choisis, et pourquoi ils diffèrent

**`hash_password` lève** au-delà de 72 octets. Créer un hash ambigu est le défaut
que tout ce chantier ferme ; le refus doit être bruyant. Cela couvre aussi les
appelants **hors route** — `scripts/create_user.py` n'a aucune validation devant
lui.

**`verify_password` retourne `False`.** Aucun mot de passe de plus de 72 octets
n'a pu produire un hash par cette couche, donc la vérification ne peut pas
légitimement réussir ; et sous bcrypt 5, `checkpw` lèverait, transformant une
mauvaise saisie en 500. C'est un refus **choisi**, pas une erreur avalée — le
contrat du sprint interdit le silencieux non choisi, pas le refus documenté.

`BCRYPT_ROUNDS = 12` est explicite : c'est la valeur que passlib appliquait, donc
les hashes d'avant et d'après sont **indiscernables**. L'augmenter est une
décision séparée, avec un coût de latence — pas un effet de bord de la migration.

---

## 5. Acceptation

| # | Critère | Résultat |
|---|---|---|
| A1 | passlib hors du chemin bcrypt runtime | **PASS** — garde sur `app/` **et** `tests/` |
| A2 | Hashes existants vérifiables | **PASS** — sur un digest produit par passlib |
| A3 | Nouveaux hashes vérifiables | **PASS** — `$2b$12$`, longueur identique |
| A4 | Mauvais mot de passe refusé | **PASS** — sur hash ancien et nouveau |
| A5 | > 72 octets refusé avant bcrypt | **PASS** — lève au hash, `False` à la vérification |
| A6 | bcrypt 5 readiness | **PASS** — voir §7 |
| A7 | PR #7 non mergée | **PASS** — borne et pin inchangés, vérifiés par test |
| A8 | bcrypt 5 mergeable après ? | voir §7 |

### La preuve la plus forte : passlib rendu introuvable

Un bloqueur d'import posé sur `sys.meta_path`, puis :

```
passlib chargé ?      : False
hash hérité vérifié   : True
nouveau hash          : $2b$12$…
nouveau hash vérifié  : True
mauvais mot de passe  : False
```

Et sur l'application entière :

```
app.main importée sans passlib : True
routes enregistrées            : 96
```

La dépendance est sortie du chemin d'exécution — **pas seulement de `auth.py`**.

### Un test que ce sprint a rendu faux, comme annoncé

`Sb_AUTH_PASSWORD_LENGTH_01` avait laissé un test documentant le défaut
sous-jacent : `verify_password(jumeau, hash) is True`. Son docstring disait :
*« si ceci cesse d'être vrai … la politique est passée de garde unique à ceinture
supplémentaire »*.

C'est arrivé — non parce que bcrypt 5 a atterri, mais parce que **la couche
elle-même refuse** désormais. Le test affirme la nouvelle vérité et cite ce qui
l'a changée. Un second test couvre le refus au hachage.

### Un piège de test évité grâce à une leçon déjà consignée

`pytest.raises(PasswordTooLongError)` échouait alors que l'exception était bien
levée : `conftest::client` purge `app.*` de `sys.modules` à chaque test, si bien
qu'un import **dans** la fonction produisait une **seconde génération** de la
classe. Import remonté au niveau module. Même famille que le faux échec
d'identité d'enum déjà rencontré sur ce dépôt.

### Pré-scan Sonar, cette fois utile

`python:S5863` attrapé **avant le push** : `assert hash_password(x) != hash_password(x)`
présente deux expressions syntaxiquement identiques, ce que Sonar lève en **BUG**.
Lié à deux variables. Pré-scan AST des quatre fichiers touchés : zéro `S9073`,
zéro `S5863` restant.

---

## 6. Vérifications locales

`check_scope` a classé `SHARED_CODE`. **Traité au-dessus** : l'authentification
traverse tous les chemins connectés.

| Check | Résultat |
|---|---|
| ruff (fichiers touchés) | propre — les 2 `UP045` restants sont sur des lignes **hors diff** (dette `Optional`) |
| `check_ruff_budget.py` | 281 ≤ 548 |
| `check_spec_protocol.py` | OK |
| Suites auth (5 fichiers) | **79 passés** |
| Suite migration dédiée | **19 passés** |
| **Full sweep local** | **4 898 passés** (13 min 13 — au-delà du repère de ~10 min de `CLAUDE.md`, mais lancé volontairement sur un tier qui ne l'exige pas, et mené à terme) |

---

## 7. bcrypt 5 — A6 et A8

**Ce qui est prêt**, et vérifié par test :

| Condition | État |
|---|---|
| Aucun import `passlib` en runtime | ✅ |
| Aucun import `passlib` dans les tests | ✅ — un test chargeant `passlib.hash` déclencherait la sonde de 255 octets |
| Aucun chemin ne dépasse 72 octets vers bcrypt | ✅ |
| API bcrypt utilisées stables en 5.0 | ✅ `hashpw`, `checkpw`, `gensalt` |

**Ce qui reste**, et qui est exactement le contenu de la PR #7 :

| Reste | Détail |
|---|---|
| Relever `bcrypt>=4.0,<5` | → `>=5.0.0,<6` |
| Régénérer le lock | `bash scripts/regen_lockfile.sh` — le lock est autoritaire depuis `Sb_DEPENDENCY_LOCK_AUTHORITY_01` |

**A8 — réponse.** Oui, bcrypt 5 peut être adopté immédiatement après ce sprint —
**mais pas en mergeant la PR #7 telle quelle** : elle modifie
`requirements-lock.txt` à la main, or le lock doit être **régénéré** par l'outil
depuis `requirements.txt`, et sa version dans la PR est antérieure à la
régénération pour Python 3.11. La forme correcte est une tranche courte :
relever la borne, régénérer, laisser la CI installer et jouer la suite.

`passlib` reste **déclaré** dans `requirements.txt`. Installé mais jamais
importé, il ne peut pas casser bcrypt 5 : la sonde ne s'exécute qu'au chargement
de `passlib.hash.bcrypt`. Le retirer est une tranche d'entretien distincte — la
mélanger à un changement d'authentification serait précisément ce que le sprint
précédent a appris à ne pas faire.

---

## 8. Limites

- **Le coût 12 n'est pas réévalué.** Il reproduit passlib à l'identique. Le
  relever est une décision de sécurité avec un coût de latence, hors sujet ici.
- **Aucun compte n'est re-hashé.** Un hash écrit par passlib le reste ; il est
  simplement vérifié par bcrypt direct. Aucune rotation n'est prévue ni requise.
- **Les scripts opérateur** (`create_user.py`, `perf_baseline.py`,
  `visual_baseline_runtime.py`) appellent `hash_password` sans validation de
  route. Ils bénéficient désormais du refus explicite — mais ils lèveront là où
  ils tronquaient silencieusement, ce qui est le comportement voulu.
- **bcrypt 5 n'est pas testé ici.** Ce sprint rend l'adoption possible ; il ne la
  démontre pas. Seule une CI installant bcrypt 5 le fera.

---

## Verdict

**passlib est hors du chemin d'authentification, et les données n'ont pas
bougé.**

La compatibilité a été mesurée **avant** d'écrire une ligne, dans les deux sens,
et l'absence de passlib a été prouvée en le rendant *introuvable* — l'application
entière démarre sans lui.

Ce que le sprint apprend au-delà du code : le blocage n'était pas dans l'API de
bcrypt mais dans **ce qu'un appelant en faisait**. passlib hachait un secret de
255 octets pour tester son backend ; c'est cela, et non le changement d'API de
bcrypt 5, qui verrouillait le projet sur `bcrypt<5`. Aucun changelog ne pouvait
le dire — il fallait lire la CI qui avait réellement installé les deux ensemble.
