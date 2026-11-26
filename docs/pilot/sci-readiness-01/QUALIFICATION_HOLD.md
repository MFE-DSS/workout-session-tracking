# SCI-READINESS-01 BUILD-01 — qualification HOLD

25 novembre 2026, Europe/Paris. Parent vérifié : `1f0122bf4f2d30f7c95d4975b5994d1453363bc5`.

Le lecteur est livré désactivé. Aucun profil opérationnel QUALIFIED, activation QA, donnée réelle ou publication n’est acquis par son code.

## Limite nominale effectivement observée

Le catalogue canonique `data/sci/exercise_catalogue.json`, empreinte `7d1ae5d3c05c4b76c540789e9e07d0c2c0d96c9a4aa03a28c0b4f964441981fd`, contient à `/records/75/exercise_operational/curation/notes` une chaîne UTF-8 de **4 302 octets**. Le contrat d’admission JSON fixe **4 096 octets**. La lecture réelle refuse donc le catalogue, et le profil ne peut devenir opérable sur ces entrées. Aucun plafond n’est augmenté ; aucun commentaire/source historique n’est réécrit.

Les tests sémantiques de rôles utilisent un port explicitement synthétique : seul ce commentaire éditorial est omis **en mémoire**. Ils vérifient la projection, pas l’admission de ce catalogue ou de l’image réelle. Un test distinct conserve le refus réel du fichier canonique. La parité des algorithmes de composition/digest v2 et de l’extension est séparée de l’admission du bundle complet.

## Runtime

Le Mac n’est pas Linux. Docker local ne répondait pas au diagnostic en lecture ; seul ce CLI a été interrompu, sans toucher au daemon. Les témoins Linux réels CPU/AS sont réservés à la CI Linux et ne qualifient pas à eux seuls l’image Python3.11.14, son SQLite, son conteneur et sa concurrence. Les résultats CI exacts seront ajoutés au reçu après exécution. Aucun profil QUALIFIED n’est généré artificiellement depuis ces limites candidates.

Le service exige un profil serveur épinglé, une identité OS/Python/SQLite/machine correspondante, les mêmes plafonds, une référence de preuve et les hashes exacts des sources. Le worker applique CPU2/3s, AS512MiB et CORE0 avant imports applicatifs ; le parent borne le pipe et le délai, sans file ni changements de ses rlimits. Une vérification non prouvée reste UNAVAILABLE.

## Prochaine décision bornée — proposition seulement

Avant de chercher une activation, soumettre un amendement autorisant un **adaptateur sélectif des champs nécessaires du catalogue attesté**, qui laisse les notes éditoriales hors projection avant matérialisation, conserve les octets historiques/digests, et maintient les limites4096 des corps et champs effectivement admis. Il faut spécifier puis éprouver ce sélecteur ; il n’est pas implémenté par BUILD-01. L’alternative d’une hausse de plafond n’est ni appliquée ni recommandée sans nouvelle preuve.

Ensuite seulement : qualifier réellement l’image Linux/Python3.11.14 concernée, son manifeste de sources, les cas nominaux/adversariaux, mémoire/temps/concurrence et plans SQL. Les permissions OPS/DATA restent distinctes. Aucun contournement pour faire passer le cas nominal.
