# SPRINT Sb_SEC_A0_SESSION_TOKEN_INTEGRITY_01 — Intégrité des jetons d'authentification

**Spec :** `docs/strategy/Sx_SEC_A0_SESSION_TOKEN_INTEGRITY_SPEC.md` (choix opérateur 2026-10-24 :
§2.1 forme E, §2.2 T1, déploiement après merge) · **Base :** `8f9e3df` · **Date :** 2026-10-24 ·
**Branche :** `sb/sec-a0-session-token-integrity-01`

> Règle de rédaction (dépôt public) : ce rapport énonce des invariants et les tests qui les
> prouvent. Il ne décrit ni mécanisme d'exploitation ni procédure de reproduction.

## 1. Objet

Tenir les invariants I1 à I9 du contrat de jeton web. La tranche ajoute une colonne additive et
les tests de régression du §3. Les routes, leurs réponses, le hachage, la durée de session, les
drapeaux du cookie et l'identité `User` ne changent pas.

## 2. Brainstorming / Options / Risques / Choix retenu

### 2.1 Typage des jetons (I1 à I3)

| Option | Pour | Contre |
|---|---|---|
| (a) Un champ « usage » vérifié à la lecture | minimal | un lecteur qui oublie la vérification rouvre le défaut |
| (b) Un **sel de signature distinct par usage** | un jeton d'un usage ne se vérifie même pas sous l'autre | seul, il ne dit rien du contenu |
| (c) **(a) + (b)** | défense en profondeur : signature **et** contenu typés | deux mécanismes à tenir |

**Choix : (c).** Le sel neuf a un effet de bord **voulu** : il réalise la transition T1. Tout jeton
signé avant le déploiement ne se vérifie plus, et chacun se reconnecte une fois.

### 2.2 Révocation (I4 à I7), forme E retenue par l'opérateur

- **L'époque.** Une colonne `users.session_epoch` (entier, défaut 0, migration additive) est
  portée par chaque jeton. Le seul lecteur qui fait autorité, `get_current_user`, refuse un jeton
  dont l'époque n'est pas celle de l'utilisateur.
- **Ce qui l'incrémente.** Le changement de mot de passe, la réinitialisation et la déconnexion.
  La session de l'utilisateur qui change son mot de passe est ré-émise à la nouvelle époque.
- **Usage unique du lien de réinitialisation (I6).** Il porte l'époque de son émission ; la
  réinitialisation l'incrémente, et le lien ne vaut donc plus rien après usage. Aucune table
  supplémentaire n'est nécessaire.
- **Ce qui échoue fermé.** Un appelant qui émettrait un jeton sans époque explicite produirait
  l'époque 0. Elle est refusée dès que l'utilisateur a déjà révoqué une fois.

### 2.3 Risques

| Risque | Parade |
|---|---|
| La fixture rapide des tests cesse de produire un jeton valide | elle appelle la fonction de production ; un utilisateur neuf a l'époque 0 ; `test_auth_fixture_fastpath` le garde |
| Un lecteur secondaire du cookie qui ne vérifierait pas l'époque | mesuré : un seul lecteur fait autorité (`get_current_user`, via `deps.CurrentUser`) |
| La déconnexion d'un appareil ferme les autres | c'est la forme E, choisie par l'opérateur ; la forme S viendra avec les sessions mobiles (D9) |
| Le tier `migration` rate une garde de migration | full sweep local, tous les `check_migration_*`, drift et snapshot de schéma, puis CI réelle |
| Exposition publique avant correctif | spec et correctif dans **une seule PR** ; la branche de la spec n'a jamais été poussée ; déploiement aussitôt après le merge |

## 3. Réalisé

### 3.1 Fichiers

| Fichier | Changement |
|---|---|
| `app/services/auth.py` | jetons typés : usage, sel propre à l'usage, époque ; `get_current_user` confronte l'époque ; `resolve_reset_user` ; `revoke_sessions` |
| `app/routers/auth_routes.py` | la connexion et l'inscription émettent à l'époque courante ; la déconnexion, la réinitialisation et le changement de mot de passe révoquent ; le changement ré-émet la session |
| `app/models/user.py`, `migrations/versions/20261024_add_users_session_epoch.py` | `users.session_epoch` : entier, non nul, défaut 0, additif ; downgrade symétrique |
| `data/schema_snapshot.sql` | une seule colonne ajoutée, régénérée par l'outil depuis ce worktree |
| `tests/test_sec_a0_session_token_integrity.py` | 13 tests (§3 de la spec, plus une garde de séparation par signature) |
| `tests/test_exercise_knowledge_base.py` | sentinelle de tête Alembic → `y6z1t7u8w19`, avec sa raison, comme chaque migration précédente |
| spec, `SPEC_REGISTRY.md` | choix opérateur consignés |

Les contrats existants sont tenus **sans amendement** des tests d'authentification. Les 100 tests
d'auth et de preuve produit passent, dont la fixture rapide, qui appelle la fonction de
production. Les routes et leurs réponses sont inchangées.

### 3.2 Couverture des invariants (requêtes HTTP réelles)

| Invariant | Test |
|---|---|
| I1, I2 | `test_reset_credential_never_authenticates_a_session` |
| I1, I3 | `test_session_credential_never_authorizes_a_reset` |
| I1 | `test_token_without_known_purpose_is_refused`, `test_usages_are_separated_at_the_signature_itself` |
| I4, I5 | `test_password_change_revokes_prior_sessions` (session courante ré-émise et acceptée) |
| I4, I6 | `test_password_reset_revokes_sessions_and_is_single_use`, `test_a_used_reset_link_resolves_to_nobody` |
| I4, I7 | `test_logout_revokes_the_presented_session_server_side` (forme E) |
| T1 | `test_tokens_issued_before_deploy_are_refused` |
| I8 | `test_inactive_user_is_never_authenticated` |
| I9 | `test_auth_never_reads_client_time` (garde statique ciblée) |

### 3.3 Contre-preuves (worktree jetable, défaut réintroduit un à la fois)

**8/8 détectés**, dont **le défaut d'origine en entier**. Le premier passage en laissait passer
deux : sel commun à tous les usages, et sel d'origine pour les sessions. Ce n'étaient pas des
trous : chacune retirait une couche **redondante**, et l'invariant tenait par l'autre couche (le
champ d'usage relu, l'absence d'époque dans les anciens jetons). Une couche que rien ne garde peut
toutefois disparaître sans bruit. Une garde explicite de séparation par signature a donc été
ajoutée, et elle mord.

### 3.4 Vérifications (tier MIGRATION)

| Contrôle | Résultat |
|---|---|
| `check_scope.py` | **MIGRATION** |
| `check_alembic_drift` | OK, aucun écart |
| `check_schema_snapshot` | OK |
| `check_migration_patterns` | OK, aucun motif dangereux |
| `check_migration_roundtrip` | OK : 56 objets, schéma identique avant et après l'aller-retour |
| Full sweep local (`run_local_sweep.sh`, 366 fichiers) | **6 968 passés, 1 échec**. L'échec est `test_worked_area_descriptor::test_no_model_migration_schema_touched`, qui compare l'arbre de travail à `HEAD` et voit donc les fichiers non commités. Il est **rejoué après commit** (§3.5). |
| Budget ruff | 264, valeur du canonique. Un UP045 sur une ligne neuve a été corrigé avant push. |
| Pré-scan Sonar | aucune occurrence |
| `check_spec_protocol` | OK |

### 3.5 Après commit

`tests/test_worked_area_descriptor.py`, rejoué après le commit `063846a` : **14/14 passés**.
L'échec du sweep venait bien de l'arbre de travail non commité. Le fichier lit
`git diff --name-only HEAD`, qui est vide après le commit comme sur le checkout propre de la CI.

**Verdict :** `Sb_SEC_A0_SESSION_TOKEN_INTEGRITY_01` est construite et vérifiée en local
(tier MIGRATION). Le statut final dépend de la CI réelle. Le déploiement suivra le merge sur
choix opérateur, après confirmation de ce qu'il embarque.

## 4. Closeout — MERGÉE ET DÉPLOYÉE (2026-10-24)

| Élément | Valeur |
|---|---|
| PR | #280, merge commit (sans squash ni `--admin`), tête épinglée `c62d2d0` ; spec et correctif dans la même PR |
| SHA canonique | `ff4239d` |
| CI de PR | 10/10 verts au premier passage |
| CI canonique (push sur `ff4239d`) | run `40086199645`, **7/7 succès** |
| Porte Sonar de la PR | **OK** : couverture du nouveau code 97,1 %, 0 bug, 0 code smell, 0 vulnérabilité |
| Déploiement production | run `40087180522` sur le SHA complet `ff4239d…`, après confirmation explicite de l'opérateur : poussée sur le VPS, smoke et tag **verts**. Tag `deploy/prod/2026-10-24-1046-ff4239d`. |
| Contenu du déploiement | la production passe de `dfcd3bf` (2026-09-28) à `ff4239d`. Elle reçoit A0 et les merges #261 à #279 : TRAIN A environnement concret, D14, tranches SCI. Une seule migration est appliquée, `y6z1t7u8w19`. |
| Effet visible | reconnexion forcée unique de chaque utilisateur (T1) ; « se déconnecter » ferme toutes les sessions web (forme E) |

**D9 (authentification mobile) devient ouvrable** : c'était la condition posée par la spec A0 et
par `ADR_AUREN_VNEXT_01`.

**Verdict :** ✅ **MERGÉE + DÉPLOYÉE** — `Sb_SEC_A0_SESSION_TOKEN_INTEGRITY_01` CLOSED, canonique et
production `ff4239d`, CI canonique 7/7, smoke de production vert.
