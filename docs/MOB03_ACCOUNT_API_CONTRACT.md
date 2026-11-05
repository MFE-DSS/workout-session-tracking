# MOB-03 — contrat du socle JSON de compte

Statut : implémentation locale en cours de revue, non déployée et non raccordée à une nouvelle UI. Aucun changement de politique de mot de passe, de quota ou de schéma.

## Inscription

POST /api/mobile/v1/auth/register, JSON : username, password, password_confirm ; email et device_label facultatifs. Les règles web sont partagées : identifiant normalisé de 3 à 64 caractères ASCII autorisés ; mot de passe de 8 caractères minimum et 72 octets UTF-8 maximum ; email validé et normalisé quand fourni. Aucun objectif, unité, consentement ou fait corporel créé.

Succès 201 : token_type=Bearer, access_token, access_expires_in, refresh_token, server_now, user={id,username}. Aucun cookie web émis. Validation refusée : 400 avec detail.error et message canonique. Nom/email indisponible : 409. Champ d'identité supplémentaire ou JSON invalide : 422 avec seulement type/loc/msg, sans reprise du corps ni des secrets. Quota register partagé avec le web : 429 et Retry-After. Les réponses sensibles sont sans cache.

La contrainte SQL unique reste l'autorité sous concurrence ; un seul compte et une seule réponse de création réussie. Après réponse inconnue, le futur client doit indiquer l'incertitude : le rejeu n'est pas une confirmation. La connexion existante avec les mêmes identifiants permet de vérifier l'identité sans créer de second compte. Aucun secret ou clé d'idempotence nouvelle persisté.

## Changement de mot de passe

POST /api/mobile/v1/auth/password avec Bearer propriétaire et JSON current_password, new_password, new_password_confirm. Le secret actuel garde la compatibilité des anciens comptes courts ; la borne UTF-8 maximale s'applique toujours avant bcrypt. Les règles du nouveau secret sont celles de l'inscription.

Succès 200 : nouvelle paire Bearer et même identité, dans la transaction qui met à jour le hash et l'époque. Tous les anciens Bearer, refresh tokens et cookies web deviennent invalides. Aucun cookie web émis. Une concurrence devenue obsolète reçoit 409 credentials_changed ; elle ne réécrit pas le mot de passe et n'émet aucune nouvelle paire. Les autres refus de saisie sont 400. Cookie seul ou Bearer invalide : 401 ; champs d'identité forgée : 422. La vérification du secret actuel partage le quota login existant.

Le futur consommateur doit stocker la nouvelle valeur SecureStore avant d'utiliser le nouvel access token et gérer les réponses tardives et inconnues. Ce raccordement et les nouvelles surfaces ne sont pas déclarés livrés par le socle API.
