# Design — réutilisation intra-job, autorité conservée

## Context
Parent3d4c7577. Image5ee90ab09696c4312cbe2a99654d5d2368d26f2050839858cca0ec801128334e, source Git montéeRO, Linuxamd64 natif sur VPS autorisé, Python3.11.14/SQLite3.46.1. Le service QA existant n'est pas le banc et n'est pas modifié. Limites2/3sCPU,512MioAS,3swall, conteneur1CPU/2Gio.

## Brainstorming / Options / Risques / Choix retenu
1. Réutiliser la vue du catalogue courant déjà admise dans le même enfant : choix proposé, coût et risque bornés, pin explicite et non-mutation à tester. Partage de parsing proposé uniquement pour les mêmes octets indépendamment attestés, en conservant les autorités séparées.
2. Refondre les imports ORM/normalisation partagés : coût dominant mais blast radius plus large ; non retenu dans ce scope.
3. Hausser CPU, max_tokens ou autre budget : non autorisé et non retenu. Les refus restent cohérents ; aucune réponse500 garantie depuis son seul plafond de scan.

## Decisions
Le cache est l'objet documentaire admis de ce seul job, identifié par son digest complet et ses limites. Son dataclass gelé n'implique pas l'immuabilité profonde du dictionnaire : le gabarit doit rester privé et fournir des copies indépendantes aux vues. Un nouveau job ne réutilise rien du précédent. Les octets/pins sont toujours vérifiés, le pin de la vue transférée doit être identique à celui de l'admission. Tous les bundles gardent leur admission propre, y compris leurs vérifications finales après parsing ; une sourceB valide différente provoque un miss et un parsing ordinaire, une différence avec son propre pin provoque le refus existant. Le digest est calculé sur le DTO normalisé retourné, sans changement de valeur métier.

## Risks / Trade-offs
Le gain CPU Legacy est réel mais varie ; la marge à la frontière reste petite. V3 peut conserver deux parsings justifiés par deux autorités. Le parent valide sortie+code retour+bornes lexicales+DTO+identité : un succès enfant seul ne vaut jamais admission. Le correctif de cache n'élargit pas la capacité de réponse et ne lève pas silencieusement les limites de ressources ou la qualification opérationnelle.

## Verification
Voir BUILD_AMENDMENT.md : RED→GREEN, non-mutation, pin divergent, jobs/owners distincts, Legacy/V3, validation parent complète, mêmes plafonds et nouvelle source/profil du HEAD réel, revue indépendante et CI obligatoire après GO. Le banc source-overlay n'atteste pas une future image reconstruite. Tout écart non qualifié conserve HOLD, lecteur désactivé.
