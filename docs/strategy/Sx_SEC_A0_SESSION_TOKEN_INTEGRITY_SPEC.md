# `Sx_SEC_A0_SESSION_TOKEN_INTEGRITY` — intégrité des jetons d'authentification

> **Statut :** `SPEC — PISTE SÉCURITÉ INDÉPENDANTE` · ouverte par l'arbitrage
> opérateur du 2026-10-23 (`ADR_AUREN_VNEXT_01` §7, **A0 ACCEPTED / P0**).
> **0 code dans cette spec.** La tranche de build recommandée est au §6.
>
> **Indépendante de vNext.** Elle ne dépend d'aucune décision mobile ; la
> tranche `Sb_VNEXT_NATIVE_N0_EXPERIENCE_LAB` n'en contient rien. En revanche,
> **aucun jeton de rafraîchissement mobile (D9) n'est émis avant sa clôture.**
>
> **Règle de rédaction (dépôt public) :** ce document énonce des **invariants** et
> les **tests qui les prouvent**. Il ne décrit ni mécanisme d'exploitation ni
> procédure de reproduction.

---

## 1. Périmètre

Le contrat d'authentification web actuel (`app/services/auth.py`,
`app/routers/auth_routes.py`) : jeton de session signé porté par cookie, jeton de
réinitialisation de mot de passe, connexion, déconnexion, changement et
réinitialisation de mot de passe. Identité `User` et logique de propriété
**inchangées**.

## 2. Invariants exigés

| # | Invariant | Énoncé vérifiable |
|---|---|---|
| **I1** | **Le type d'un jeton est vérifié à la lecture** | tout jeton porte un usage explicite ; un lecteur n'accepte que l'usage qu'il attend ; un jeton sans usage reconnu est refusé |
| **I2** | **Un identifiant de réinitialisation n'authentifie jamais une session applicative** | présenté là où une session est attendue, il est refusé comme un jeton invalide |
| **I3** | **Un jeton de session n'autorise jamais une réinitialisation** | symétrique de I2 |
| **I4** | **Les sessions existantes sont révocables côté serveur** | il existe un état serveur qui rend invalides, sans attendre leur expiration, des jetons déjà émis |
| **I5** | **Changement de mot de passe ⇒ révocation** | après un changement réussi, tout jeton de session émis **avant** est refusé ; la session de l'utilisateur qui vient de changer est ré-émise |
| **I6** | **Réinitialisation de mot de passe ⇒ révocation et usage unique** | après une réinitialisation réussie, toutes les sessions antérieures sont refusées **et** l'identifiant de réinitialisation utilisé est refusé s'il est représenté |
| **I7** | **Déconnexion ⇒ révocation côté serveur** | après déconnexion, le jeton de session qui était présenté est refusé même s'il est rejoué — supprimer le cookie du navigateur ne suffit pas |
| **I8** | **Comptes inactifs** | inchangé : un utilisateur `is_active = False` n'est jamais authentifié |
| **I9** | **Aucune décision d'authentification ne lit une heure fournie par le client** | expiration et révocation se décident sur l'horloge serveur seule (rappel de `ADR_AUREN_VNEXT_01` D11) |

### 2.1 Contrat de déconnexion — à trancher par l'opérateur

I7 admet deux formes ; la plus petite est recommandée pour A0.

| Forme | Effet d'une déconnexion | Coût | Recommandation |
|---|---|---|---|
| **E — époque par utilisateur** | révoque **toutes** les sessions web de l'utilisateur (« se déconnecter partout ») | **une** colonne additive (`users.session_epoch`, entier, défaut 0) portée par chaque jeton | **retenue pour A0** — la plus petite qui tient I4–I7 |
| **S — session par appareil** | révoque **cette** session seulement ; « partout » en option | une table de sessions | **reportée à D9**, qui introduit de toute façon des sessions d'appareil ; S pourra alors remplacer E sans rompre I4–I7 |

### 2.2 Transition au déploiement — à trancher par l'opérateur

| Option | Effet | Recommandation |
|---|---|---|
| **T1 — reconnexion forcée** | tout jeton émis avant le déploiement est refusé ; chaque utilisateur se reconnecte une fois | **retenue** — c'est la seule option qui invalide aussi les jetons déjà en circulation hors de tout contrôle |
| T2 — compatibilité | les anciens jetons de session restent acceptés jusqu'à expiration | rejetée : laisse ouverte la fenêtre que A0 ferme |

## 3. Tests de régression exigés

Chaque invariant a au moins un test qui **exerce le produit** (requête HTTP réelle,
état relu), pas un test qui lit la source.

| Test | Invariant | Forme |
|---|---|---|
| `test_reset_credential_never_authenticates_a_session` | I1, I2 | un identifiant de réinitialisation valide, présenté comme session, sur `/` et `/profile` ⇒ redirection vers la connexion, aucune donnée de compte servie |
| `test_session_credential_never_authorizes_a_reset` | I1, I3 | un jeton de session valide, présenté à la réinitialisation ⇒ lien refusé |
| `test_token_without_known_purpose_is_refused` | I1 | jeton correctement signé, usage absent ou inconnu ⇒ refusé |
| `test_password_change_revokes_prior_sessions` | I4, I5 | session A et session B ; changement de mot de passe via A ⇒ B refusée ; A ré-émise et acceptée |
| `test_password_reset_revokes_sessions_and_is_single_use` | I4, I6 | session existante ; réinitialisation réussie ⇒ session refusée ; même lien représenté ⇒ refusé |
| `test_logout_revokes_the_presented_session_server_side` | I4, I7 | jeton copié avant déconnexion, rejoué après ⇒ refusé |
| `test_tokens_issued_before_deploy_are_refused` | §2.2 T1 | jeton au format antérieur ⇒ refusé |
| `test_inactive_user_is_never_authenticated` | I8 | existant ou ajouté |
| `test_auth_never_reads_client_time` | I9 | garde statique ciblée sur le module d'authentification |

Ces tests ajoutent des **capacités** ; aucune garde existante n'est affaiblie. La
fixture d'authentification rapide des tests (`tests/conftest.py`, `create_session_cookie`
de production) doit continuer de produire un jeton conforme : elle suit le contrat
automatiquement puisqu'elle appelle la fonction de production.

## 4. Ce qui ne change pas

Le hachage bcrypt et sa politique de longueur, la durée de vie des sessions, les
drapeaux du cookie, la limitation de débit, l'identité `User`, toute la propriété
(`get_owned_session_or_404`…), les routes et leurs réponses.

## 5. Non-goals

- Pas d'authentification mobile (D9) — elle vient **après** A0.
- Pas de table de sessions par appareil (forme S) dans A0.
- Pas de changement de politique de mot de passe, de hachage, de durée de session.
- Pas de 2FA, pas de SSO, pas de fournisseur externe.
- Aucun mécanisme d'exploitation, aucune procédure de reproduction dans un
  document versionné.

## 6. Tranche de build recommandée

**`Sb_SEC_A0_SESSION_TOKEN_INTEGRITY_01`** — sur GO BUILD opérateur.

| Élément | Contenu |
|---|---|
| Périmètre | `app/services/auth.py`, routes de connexion / déconnexion / changement / réinitialisation dans `app/routers/auth_routes.py`, **une** migration additive (`users.session_epoch`), tests du §3 |
| Tier `check_scope` attendu | **`migration`** (colonne additive) — donc full sweep local + `check_migration_*` + drift + snapshot, et CI réelle |
| Ordre | migration additive → lecture typée (I1–I3) → époque (I4–I7) → transition T1 → tests §3 |
| Livraison | **une seule PR qui porte cette spec ET le correctif** ; merge puis déploiement dans la foulée |
| Clôture | CI verte, Sonar vert, déploiement vérifié, tous les tests du §3 verts en production-like ; puis D9 devient ouvrable |

**Divulgation — recommandation forte.** Le dépôt est public. Pousser cette spec
seule, avant que le correctif soit déployé, annoncerait qu'une faiblesse existe.
**Ne pas pousser la branche de cette spec avant que le correctif soit prêt** :
spec et correctif partent ensemble, et le déploiement suit le merge sans délai.

## 7. Verdict de la spec

**Statut final :** `READY FOR SEPARATE BUILD` — sous réserve des deux choix
opérateur du §2.1 (forme E recommandée) et du §2.2 (T1 recommandée).

**Choix opérateur (2026-10-24) :** §2.1 **forme E** (« se déconnecter » ferme toutes les
sessions web de l'utilisateur) ; §2.2 **T1** (reconnexion forcée au déploiement) ; déploiement
en production **immédiatement après le merge**. Build : `Sb_SEC_A0_SESSION_TOKEN_INTEGRITY_01`.
