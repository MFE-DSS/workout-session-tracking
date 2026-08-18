# Politique de longueur des mots de passe — 72 octets

**Statut : appliquée** depuis `Sb_AUTH_PASSWORD_LENGTH_01`.
Source unique : `app/services/password_policy.py`.

---

## Le défaut fermé

bcrypt ne hache que les **72 premiers octets** d'un mot de passe et ignore le
reste. passlib ne l'en empêche pas : son réglage `truncate_error` vaut `False`
par défaut, si bien que le secret complet part au backend et y est tronqué en
silence. L'application n'imposait qu'un **minimum** de 8 caractères, aucun
maximum.

Mesuré sur le code livré, avant correctif :

```
verify(mot_de_passe, hash)                    -> True
verify(72_premiers_octets + autre_fin, hash)  -> True   ← le défaut
```

**Deux mots de passe différents partageant leurs 72 premiers octets ouvraient le
même compte.** Personne n'a choisi cette propriété : elle naît de
l'implémentation C de bcrypt rencontrant une application sans borne haute. Un
utilisateur qui saisit une longue phrase de passe croit légitimement que toute
sa longueur le protège.

Portée réelle : modérée. Il faut un secret de plus de 72 octets, et l'attaquant
doit déjà en connaître les 72 premiers. Mais c'est une garantie que le produit
laissait croire sans la tenir.

## La règle

> `len(password.encode("utf-8")) <= 72`

**Des octets, pas des caractères.** « é » pèse 2 octets, « 🏋 » en pèse 4. Une
phrase de 37 caractères accentués fait 74 octets et serait tronquée : un
contrôle par `len()` la laisserait passer. C'est pourquoi le message utilisateur
dit **octets** — écrire « 72 caractères » serait faux pour quiconque écrit en
français.

**Aucune troncature applicative.** Tronquer dans le code reproduirait le défaut
volontairement au lieu d'accidentellement. La politique **refuse** et le dit. Un
test interdit tout `password[:72]` dans `app/`.

## Où elle s'applique

Les quatre flux utilisateur qui atteignent bcrypt :

| Flux | Route | Contrôle |
|---|---|---|
| Inscription | `POST /register` | minimum + maximum |
| Connexion | `POST /login` | **maximum seul** |
| Changement | `POST /profile/password` | maximum sur l'actuel, minimum + maximum sur le nouveau |
| Réinitialisation | `POST /reset/{token}` | minimum + maximum |

### Pourquoi la connexion ne contrôle pas le minimum

Deux raisons. Un contrôle de plancher à la connexion **verrouillerait** tout
compte créé avant que le plancher ne passe de 4 à 8 (`Sb_20.3`). Et il dirait
quelque chose sur les identifiants stockés.

Le **maximum**, lui, est appliqué partout : c'est lui qui empêche un secret
surdimensionné d'atteindre bcrypt.

Le rejet à la connexion intervient **avant** la requête base et avant bcrypt. Il
ne fuit rien : il ne dépend que de la longueur de l'entrée de l'attaquant,
jamais de l'existence du compte. La comparaison à temps constant contre un hash
factice reste intacte pour toute longueur acceptable.

## Conséquence assumée pour les comptes existants

Un compte dont le mot de passe dépasse 72 octets se connecte aujourd'hui avec la
chaîne complète — silencieusement tronquée. Après ce correctif, il devra saisir
ses **72 premiers octets**, ou passer par « mot de passe oublié ».

C'est le prix de la fermeture, et il est dit plutôt que caché. **Aucun hash n'est
modifié, aucun compte n'est migré, le format `$2b$` est inchangé.**

## Lien avec bcrypt 5.0

bcrypt 5.0.0 lève `ValueError` au-delà de 72 octets au lieu de tronquer — il
**refuse précisément de faire** ce qui cause ce défaut. C'est la ceinture en plus
des bretelles.

Sans la présente politique, l'adopter transformerait inscription, connexion,
changement et réinitialisation en **500**. Avec elle, aucun chemin utilisateur ne
peut plus atteindre bcrypt avec un secret trop long : la montée devient sûre.

`Sb_AUTH_PASSWORD_LENGTH_01` **ne monte pas** la dépendance. La PR #7 reste
ouverte et devient mergeable.

## Ce que la politique ne fait pas

- Elle ne juge pas la **force** d'un mot de passe (entropie, dictionnaire).
- Elle ne borne pas les mots de passe créés par les scripts opérateur
  (`scripts/create_user.py`), qui ne sont pas un flux utilisateur. Sous bcrypt 5,
  un script passant plus de 72 octets lèverait une erreur explicite — bruyante,
  pas silencieuse.
- Elle ne détecte pas les comptes **déjà** porteurs d'un secret tronqué : les
  hashes sont opaques, c'est indécidable.
