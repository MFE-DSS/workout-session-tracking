# TIME-01 — qualification bornée et correction de restauration

22 novembre2026. **CORRECTION VÉRIFIÉE LOCALEMENT — CI/merge en attente — aucun PASS temporel global revendiqué.**
Base canonique vérifiée : dff03f3be3dfc41c403075edcb627fbd055c194f.
Le mandat TIME-01 autorise l'investigation et la correction minimale après
preuve, puis les contrôles et GOV-MERGE-01. Il n'autorise pas une nouvelle OTA.

## Brainstorming / Options / Risques / Choix retenu

Attribuer d'emblée l'écart à la VM ou à une ancre serait sans preuve.
Réécrire les faits ou substituer partout l'heure murale violerait le mandat.
Choix : retracer les octets persistés, reproduire un chemin à la fois,
corriger les défauts démontrés sans expliquer artificiellement l'incident.

## Incident exact

- SET edfcb649-e392-46fa-9d83-c5c7a15b4428, propriétaire synthétique2,
  séance5/set13. performed_at **2026-11-21T19:54:44.820Z**, estimated=false.
- recorded_at_ms local **1795319113034**, soit
  **2026-11-22T03:45:13.034Z**. Écart **28228,214 secondes**.
- Corps outbox et fact_json concordent. Le backup serveur acquis porte le même
  performed_at ; reçu APPLIED revision1, performed_at_adjusted=false.
  recorded_at serveur **2026-11-22 03:45:16**, précision seconde DB.
- FINISH e513aa2e-e7ba-412d-b8af-face522dcad2, created_at_ms
  **1795319182675** ; ended_at serveur **2026-11-22T03:46:22.674Z**.
- Source snapshot51, TIME_ACK conservé. Les sources JS de l'incident sont
  dff03f3 ; native3bd4099, runtime8c3af5da. Les empreintes des TAR sont
  conservées dans le dossier privé de preuve, pas des copies réinterprétées.

**Classification de l'incident : F — preuves insuffisantes.** La divergence
existe avant le stockage serveur ; aucune altération de la date par la chaîne
SQLite/outbox/serveur n'est observée. Il manque les lectures mono/wall, la
génération du Host et le moment d'acquisition de son ancre au clic historique.
Les horloges relues après l'incident ne comblent pas ce manque.

## Reproduction native distincte

APK signée réelle0.0.2/code3, update01a202c6-9348-7fe2-aded-8914eefdb8ca,
JSdff03f3, Android16/API36. Copie AVD en mode **read-only**, serial5588 ;
réseau coupé avant ouverture, sans route par défaut. Le seul SQLite du
propriétaire2 est restauré depuis AFTER_DFF03F3.private.tar dans l'overlay
jetable. L'AVD source et les preuves historiques ne sont pas remplacés.

Le vrai ConnectedApp relit la séance ; une saisie synthétique17,5/9 produit
une unique nouvelle SET locale e29fe07b-d617-4cde-979f-7cb89fee8e5c :
performed_at **2026-11-21T19:13:40.844Z**, enregistrement local
**2026-11-22T11:35:36.316Z**, écart **58915,472 secondes**, estimated=false.
L'ancien server_now était **2026-11-21T19:10:01.538860+00:00**.

**Ce chemin reproduit A : réappariement d'une ancre serveur persistée à une
nouvelle origine monotone.** Il ne prouve pas que ce chemin a causé l'incident
initial. Aucune SET/FINISH n'est envoyée au backend depuis cette copie.

Un test du vrai adaptateur React démontre aussi une date prise depuis l'ancien
rendu plutôt qu'au clic : attendu12:00:15, reçu12:00:00 ; même flag faux lorsque
l'action demande une estimation. C'est une reproduction contrôlée du défaut
de callback, pas une trace rétroactive du clic historique.

## Correction minimale

L'ancre est désormais possédée en mémoire par le contrôleur, créée depuis la
réception d'une lecture d'exécution confirmée, jamais depuis le DTO SQLite.
restore/pause/échec de lecture l'invalident ; une réponse d'une génération
antérieure ne la recrée pas. Le clic prélève sa date et son statut, sans
réutiliser le dernier rendu. Le repli D11 reste explicitement estimé.

La lecture échouée après une clôture locale conserve aussi la phase COMPLETE,
comme pause() et la lecture confirmée le faisaient déjà. La reproduction native
hors réseau montrait une FINISH durable puis une phase PAUSED à tort. Le test
attend COMPLETE, reçoit PAUSED avant réparation, et passe après ce seul garde.
Cela ne constitue pas la cause de l'écart temporel historique.

Ni SCI, ni transition prescrite, ni route, schéma, auth ou journal historiques
ne changent. Aucun texte, style, géométrie, primitive ou baseline changé ;
les adaptateurs visibles conservent leurs composants acceptés. Une recette
native corrigée reste distincte de la reproduction dans l'APK actuelle.

## Vérifications et limites

RED réels du Host, de l'action, de la réponse après restore, du cycle
arrière-plan et du FINISH local ; GREEN final **129 suites / 1495 tests
mobiles**, TypeScript PASS. Broad backend **12 PASS** : exécution/dates HTTP,
persistance et autorité V3, sans changement de code serveur. Gouvernance
visuelle ciblée **35 PASS**, distincte des pixels CI. check_scope ISOLATED ;
contrôles consommateurs élargis, pas de full sweep backend local redondant.
Budget Ruff **259 ≤ 548** ; protocole et OpenSpec strict **29/29** passent.
Gitleaks sur les13 fichiers candidats : aucun secret détecté. Le reçu final
complétera la CI exacte et les résultats Sonar réels.

Deux premiers harnais RED étaient invalides : onChange au lieu de
onChangeText ; AppState.currentState mocké comme fonction. Ils sont conservés
et ne sont pas revendiqués RED produit. Après correction des harnais, les
assertions du produit échouent réellement puis passent après réparation.

Revue indépendante du diff entier : deux Important corrigés (réponse pendant
arrière-plan et trace brute non validée), deux mineurs traités (ticker sans
exécution et formulation documentaire sur les corrections). Les traces QA
n'émettent que les epochs normalisées/null, génération et UUID de commande,
pas les chaînes brutes du DTO. Le nouveau garde COMPLETE est relu séparément, sans Important. Il prévient
une nouvelle rétrogradation ; il ne répare pas les phases PAUSED déjà
persistées dans les archives ou sur des installations antérieures. Le cas
statut serveur completed avec ancienne phase PAUSED est testé aussi.
Aucun nouveau rendu, texte ou style n'est livré : le jugement de composition
ne change pas ; le contrôle visuel obligatoire reste applicable en CI.

La reprise native5s, sommeil/réveil20s et discontinuité murale+3600s sont
observés dans le seul guest hors réseau, puis horloge guest restaurée. Le
test long dure **301,727 secondes**, pas7h50. Les lectures /proc/uptime ne
sont pas présentées comme des lectures de performance.now du moteur JS.
La commande SET garde UUID/corps/date après relance. Les tentatives offline
passent6→8, état pending conservé : ce n'est pas une égalité complète d'outbox.
Six autres tables durables sont identiques pour les deux propriétaires.

Après le test long, une FINISH explicite est préparée, toujours sans réseau :
f64d2e6a-c8a4-4dbc-8f2e-16eb42c3b68e. Après force-kill et redémarrage, les
deux commandes propriétaire2 (une SET et une FINISH) ont les mêmes corps,
UUID et dates ; aucune nouvelle commande, aucune mutation envoyée. Le défaut
PAUSED après clôture est conservé comme échec de l'APK initiale ; sa correction
est vérifiée en tests, pas dans une OTA non publiée. Le clone read-only5588
est arrêté normalement, archives conservées ; aucun autre appareil touché.

**Encore non qualifiés :** cause originale, continuité mono JS pendant longue
suspension, durée réelle du repos après veille, réponse réseau ancienne à
réception, recette dans l'APK après correctif et appareil physique. Aucune
publication QA/production, aucun APK nouveau, aucune reprise destructrice DB.

[Provenance des horloges et points de persistance](PROVENANCE.md).
