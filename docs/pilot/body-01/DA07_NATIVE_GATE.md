# BODY — gate natif DA07 du 14 novembre 2026

Statut : reconstruction locale contrôlée, pixels soumis avant commit UI.
Le master est accepté ; les pixels ConnectedApp ne le sont pas encore.
Canonique relu : `1462482a4e2bcd1fcde121d6f207a2131616e849` ; checkpoint
BODY `f899b735486e1e258982462ae8f7b96ad15f6984`, PR407 draft. Aucun merge,
APK, OTA, déploiement ou rebaseline produit par cette passe.

## Croquis validé

Décisions call_e22888c3c8c64715bb1544af27dc95fb : « Accepter A — BODY »,
« Accepter B — NUT », « Accepter C — Programmes ». Reçu séparé dans
DA07_MASTER_ACCEPTANCE.json ; archive artistique immuable
`45fd765cdbe95c05b3598e8bc2bfd75136697558f30732d1fcd04c9100f1a697`.
Les décisions B/C seront consommées dans leurs propres scopes et parents.
Le plan préalable est docs/superpowers/plans/2026-11-14-body-da07-native.md.

## Inventaire — une information, une seule fois

| Élément | Information | Source du contrat | Doublon ? |
|---|---|---|---|
| Instrument | Valeur sélectionnée et unité | BodyEntry.fields, field key | Non |
| Jour | Jour déclaré ou précision inconnue | measured_at, date_precision | Non |
| Chronologie | Têtes courantes datées et connues | page.entries, field quality | Non |
| Référence choisie | Observation antérieure et période exacte | Deux identités explicitement choisies, même champ/unité | Non |
| Comparaison | B−A neutre, sans sens biologique | Nombres connus et jours déclarés strictement ordonnés | Non |
| Instruments auxiliaires | Autres champs, inconnus indépendants | Même DTO, aucune copie d'un côté à l'autre | Non |
| Éditeur | Brouillon actif et date explicite | État local ; référence en lecture seulement, initial de correction distinct | Non |
| Sources et versions | Provenance et versions remplacées | owned head, versions et sidecar | Non |
| Effacement minimal | Identité/jour/révision/nombre de versions | purpose ERASURE, jamais BodyEntry numérique | Non |
| Résultat à vérifier | Commande durable et reçu exact | body_pending_commands_v1, operation lookup | Non |

La position temporelle ne fabrique pas d'heure pour deux observations du même
jour. Le dernier jour ambigu exige un choix explicite. Une comparaison fige ses
deux identités : une actualisation ne remplace pas silencieusement son endpoint.
Aucune moyenne, tendance interpolée, appréciation positive/négative ou formule
scientifique n'est ajoutée.

## Comparaison avec la référence validée

Board unique : http://127.0.0.1:8252/ . Master BODY accepté placé à côté du vrai
ConnectedApp390×844pt, puis acquisition, confirmation, sources/versions,
inconnus bilatéraux, grande fonte et gestion d'effacement. Les PNG sources et
références copiées sont intacts ; CAPTURE_MANIFEST.json porte leurs empreintes.

| Autorité | Application | Résultat |
|---|---|---|
| Frame C / RecessedWindow / NumericReadout | Composants réels, géométrie non redessinée | Conservés |
| Tokens / marque / D4 | Pas de couleur, logo ou onglet ajouté | Conservés |
| Rôles typographiques | Composition locale, grande fonte en reflow | Conservés, comportement borné montré |
| MISSION / exécution / journal | Aucun delta de composition | Non concernés |
| Gates SCI et contrats de faits | Aucun moteur ou unité d'entraînement modifié | Conservés |
| Baselines LOCKED | Aucune régénération | Conservées |

Les proportions du master sont reconstruites avec les primitives et la vraie
place du clavier. Le jour et les valeurs actuels du banc ne sont pas figés aux
données de la maquette. À grande fonte l'instrument devient vertical ; les
commandes gardent au moins48dp et leur hauteur naturelle. La sélection/correction
reste un objet local, le brouillon ne préremplit pas une acquisition numérique.

## Changement unique de l'itération

Demande : « Accepter A — BODY ». Reconstruction du master dans le consommateur
BODY autorisé, avec ses états réels. Avant : master artistique et anciennes
études non admises comme production. Après : ConnectedApp natif dans sa coque
D4 ; aucune nouvelle variante artistique. L'effacement minimal reste un parcours
spécialisé sans réutilisation du graphique ni exposition numérique.

## Vérifications et revue

Tier réel du diff courant : SHARED_CODE. Broad ciblé233PASS ; suite mobile
97suites/1204PASS et TypeScript exit0 sur le dernier code. Ruff neuf, budget
260≤548, Bandit, protocole, OpenSpec strict, drift, patterns38 et snapshot
passent. Pas de full sweep local systématique ; la migration appartient déjà
au checkpoint et les preuves migration-tier historiques restent distinctes.

Revue indépendante fraîche du BODY entier : quatre Important reproduits puis
corrigés RED→GREEN : versions numériques conservées après retrait externe ;
endpoint de comparaison glissant après refresh ; lignée legacy calf_cm seule
inaccessible ; création bilatérale non atteignable. Le contrôleur invalide
désormais les lectures/version sélectionnées et garde leur branche sous accord.
Les témoins ConnectedApp/SQLite et historiques sont conservés.

Les constats natifs ont aussi conduit à conserver la sélection lors d'une
annulation, à supprimer le flex compressant les commandes à grande fonte et à
réserver la hauteur d'axe nécessaire. Ces derniers correctifs ont tests et
captures ; aucun second avis indépendant de leur octet final n'est prétendu.
Mineur différé : le statut de qualité legacy est visible dans Sources mais pas
immédiatement dans le nombre principal. Le legacy ne devient pas comparable.

Le Docker local du gate visuel piné est arrêté : aucun résultat local de ses
77tests n'est prétendu. Ils doivent réellement passer sur le futur HEAD de PR.
Aucune CI/Sonar nouvelle ne couvre ce diff non committé ; l'ancienne CI du
checkpoint ne remplace pas les nouveaux contrôles.

## Preuve native et limites

iOS26.3 dédié390×844pt, vrais ConnectedApp, clients HTTP, accord et SQLite.
Création71,3 puis correction71,2, original/version actuelle lus ; retrait puis
effacement de toutes les versions sans nouveau grant. Le banc remplace une
réponse HTTP200 après vrai commit par503 une fois. Résultat inconnu préservé,
fermeture forcée et relance ; lecture exacte du reçu puis ACKED local. Audit :
un POST d'effacement, un GET du reçu, lignes9/10 réellement absentes, aucun
nouveau grant durant la reprise. C'est une faute contrôlée de réponse, pas une
preuve de perte TCP physique. Tous les nombres/comptes sont synthétiques.

Clavier décimal logiciel réel et catégorie accessibility-medium observés.
Fast Refresh Expo Go a échoué avec « Timed out waiting for modules to be
invalidated » ; capture conservée. Relance à froid : token, Profil et BODY
retrouvés, annulation du côté droit retestée sans retour indu au poids.
Pas de réussite OTA ou de correction du framework déduite.

Android : présentateur BODY/journal/HTTP/SQLite de production dans Host natif,
fenêtres360/480×592dp et texte130%. Ce n'est pas ConnectedApp Android complet :
Expo Go ne contient pas le module requis conservé. Fenêtre Qt non pilotable
par CUA ; IME, Retour et gestes Android non validés. Overlay Expo Go visible,
troncature du label Programmes à130% dans la barre native existante divulguée.
Pas de certification VoiceOver/TalkBack ni d'acceptation physique.

SSR : vrais templates TestClient et styles, données synthétiques isolées,
lecture/correction/toutes versions et gestion après retrait. Le premier export
a demandé l'ancien ID après correction et reçu409 ; export corrigé en lisant
l'ID courant, sans changer le produit. Preview sandboxée sans soumission.

## Reprise de livraison

Attend une décision de pixels BODY sur ce board selon CLAUDE.md5.1, avant commit
UI. Puis contrôles finaux, PR407 complète, CI exacte, GOV-MERGE-01 et canonique.
Ensuite seulement NUT406 reprend le parent BODY et ses leases, puis MOB06408.
Les trois masters acceptés et les GO existants ne sont pas redemandés.
DATA, QA stable/REL03, release consolidée et recette physique restent séparés.

Preuves privées conservées sous
/Users/martinfeldmann/auren-review/da07-native-reconstruction-20261114/ : snapshot
préexistant, sources empreintées, logs RED/GREEN, revue, DB et reçus. Le board
ne sert que public/ ; secrets et bases hors Git et hors racine HTTP.
