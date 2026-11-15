# R02 — accès propriétaire à l'effacement après retrait

Correctif du B06/B23 déjà autorisé, données synthétiques uniquement. Le retrait
ne supprime pas les faits et ne doit pas forcer un nouveau grant pour les effacer.
Les lecteurs de valeurs et les nouvelles captures/corrections restent soumis à
l'accord courant. Aucun master/pixel BODY n'est accepté par ce correctif.

## Choix borné avant apply

Une lecture complète sans accord republierait les valeurs : exclu. Un token
calculé par le client ou une reprise du token gardé en mémoire ne permettrait
pas le redémarrage/CAS courant : exclu. Retenu : projection minimale explicite
sur les deux GET existants, sans nouvelle route, table ou version SCI.

`GET /me/body/measurements?purpose=erasure` et
`GET /me/body/measurements/{root_ref}?purpose=erasure` gardent Bearer, négociation
exacte, no-store et isolation propriétaire. La projection exige le schéma et
le périmètre de test de l'effacement ; elle ne dépend pas du grant de collecte
ni du flag d'acquisition. Sans purpose, les lecteurs actuels restent inchangés.

La page transporte les clés existantes contract_version/owner_id/body_revision/
state/entries/next_cursor/window, et `projection: ERASURE_ONLY`, sans
field_specs. Chaque entrée est fermée : root_ref, measurement_id, revision,
head_token, measured_at, date_precision, version_count. Aucun champ corporel,
valeur, ratio, qualité scientifique ou provenance de champ n'est publié.
Sans plage explicite, toutes les racines courantes sont parcourables par pages
bornées ; une plage fournie conserve les bornes existantes. Curseur lié au
purpose/propriétaire/plage/révision, changement409 plutôt que lecture mélangée.

Le GET de tête retourne contract_version/owner_id/projection/entry, avec les
mêmes métadonnées minimales et un token courant. Inconnu et étranger gardent
le même404. L'effacement reste POST existant, confirmation de toutes versions,
même commande durable et CAS ; conflit409 oblige à relire et reconfirmer.
Ni ce GET ni une vérification de commande ne donnent un grant de collecte.

## Consommateurs et preuves

Le client décode cette projection dans un type séparé, jamais comme BodyEntry.
Le chemin de gestion s'ouvre sur action explicite, montre uniquement le relevé
daté/identifiant/versions et reprend la confirmation existante. Même compte et
backend après relance, absence de grant et état inconnu restent distincts.
La composition et les labels requis restent à exposer au designer/opérateur ;
aucun nouveau pixel n'est committé. Le SSR doit offrir la même portée explicite
sans republier les nombres après retrait, dans son delta visuel encore ouvert.

Témoins requis : retrait→reprise→sélection→effacement sans grant ; liste/tête
sans valeurs ; anciennes valeurs et autres racines conservées avant confirmation ;
token périmé409 ; inconnu/étranger404 ; captures/corrections toujours refusées ;
pagination, A/B, perte de réponse/reçu exact et stockage avant HTTP conservés.
