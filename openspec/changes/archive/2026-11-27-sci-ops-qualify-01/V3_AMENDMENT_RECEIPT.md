# SCI-OPS-QUALIFY-01 — reçu du correctif V3

27 novembre2026. **Correctif fonctionnel PASS ; runtime HOLD ; lecteur NOT_QUALIFIED / DISABLED.**

## Source et frontière
Parent canonique1ac401f44b8af9444a8521b30cd47b7201fd1c8e. Candidat de code26c6356da649dfef91932aed70e94ec1f0cbf2f3 ; publication/CI finales à renseigner depuis les reçus vivants. Un seul module produit modifié : provenance.py. Contexte intégral vérifié avant projection explicite des cinq champs publics ; identité dans resolution ; propriétés inconnues et contradictions conservatrices. Aucun schéma, writer, SCI, SQL, budget, TIME-01 ou client modifié.

## RED → GREEN et revue
- RED unitaire :6échecs/2PASS sur six propriétés et contradictions.
- RED intégré réel :inventory2 → évaluation → START →14SET → FINISH, puis refus DTO strict,507,83s.
- GREEN :38tests provenance et109 broad PASS ;4SKIP Linux préexistants. Vrai parcours corrigé et historique mixte100 :1PASS/267,52s. Total148PASS locaux ; pas de full sweep local au tierSHARED_CODE.
- Une assertion du nouveau test confondait binding de politique et binding d’exécution ; échec conservé, assertion corrigée et parcours complet rejoué.
- Revue fraîche et relecture du pairing d’autorités : aucun finding résiduel. Ruff fichiers, budget260≤548, Bandit, protocole, OpenSpec strict et diff-check PASS.
- Gitleaks des fichiers et du delta1ac..26c PASS ; scan des1370ancêtres conserve3findings documentaires historiques (deux exemples admin:admin, une clé d’issue Sonar). Aucun ignore, baseline ou règle modifié ; pas de déclaration de scan historique global vert.

## Linux contrôlé — code corrigé, image inchangée
Image support sha256:6baa24c49404b2dd8ad74a3d5b4d6f9af3c83c6923a5711a1ae1bf79aebe5e8c, source embarquée1ac401f inchangée. Montage readonly du code26c6356 :1696fichiers attestés, un seul différent. Profil synthétique18pins, pas une admission opérationnelle. Debian13.3/amd64,Python3.11.14,SQLite3.46.1,UID/GID10001 ;1CPU/2Gio,caps supprimées,rootfsro,réseau fermé,aucun port.

| Campagne déclarée | Résultat admis par le parent | CPU user+system mesuré |
|---|---|---|
| Legacy1fait |5/5|1,576117–1,648759s|
| Legacy100faits |3/3|1,624427–1,705629s|
| V3 réel14SETcompleted |4/7 ;3SIGXCPU|1,874936–2,005450s|
| Mixte14V3+86Legacy |4/7 ;3SIGXCPU|1,856550–2,009131s|

Les sept sorties V3 et les sept sorties mixtes ont un digest recalculable, y compris les sorties refusées à cause de la terminaison anormale. Cela ne les rend pas toutes admissibles. RSS nominal maximal74 792 960octets ; tous les enfants échantillonnés sont récupérés. Lecture de référence complète V3 :identités,14opérations/révisions,contextes cinq champs,rôles SCI,unités et timestamps exacts PASS ; réglages machine/PER_IMPLEMENT non convertis.

## Isolation, limites et états conservateurs
HTTP loopback du banc :A14faits/B1fait999répétitions/vide0, deux lectures chacun200 ; absence Bearer401 ; injection configuration422. Lectures concurrentes :une200/une503 sans file d’attente ; slot libéré, aucun enfant restant. Base inchangée après GET.
Capture instrumentée séparée :V3 464unitésSQL/258appelsrows ; mixte825/526 ;742363/744050octetsDB. Ce diagnostic direct ne remplace pas le worker borné.
Bundle effectif absent sur vraie bindingV3 :2/2refus génériques(exit1), pas de catalogue courant en fallback. Marqueur V3 sans chaîne :UNKNOWN ; préfixe ancien :UNKNOWN avec zéro fait affiché, jamais zéro inventé ; texte surdimensionné :UNKNOWN.
500/501 :4/4refus, aucun succès conservé artificiellement. VM2M coupe la requête adversariale. AS512Mio réel/refus600Mio ; CPU2/3s ; sortie1Mio et wall3s effectivement coupés, enfants kill/wait. Wall collect mesuré3,001737–3,002246s, sans garantie temps réel sur création du processus. Snapshot :avant9/durant9/suivant88, DML refusé, intégritéok.
Confiance des chemins du banc :parents,UID/permissions,ACL,montages,symlinks,digests et remplacements non privilégiés PASS. Ne certifie pas les futurs chemins QA ni root/hôte/Docker ; S8707 reste suivi OPEN.

## Défauts du banc distincts du produit
Un script privé de limites avait un mode600 :premier lancement refusé ; permission du seul fichier corrigée, tous les témoins rejoués PASS. Export sous root sans capacitéDAC puis sous tmpfs éphémère refusés ; export durable sousUID10001 réalisé. Ces erreurs et reçus ne sont pas effacés. Aucun budget produit changé.

## Verdicts
- Frontière contexte/DTO, parité SCI et digest :PASS.
- Qualification fiable du candidat Linux :HOLD, refus nominauxSIGXCPU intermittents.
- Image opérationnelle :ancien paquet non mis à jour ; aucune nouvelle construction ou publication.
- Confiance des futurs chemins QA et activation :HOLD/NO. Lecteur toujoursDISABLED.

Un témoin diagnostique situe une coupure après main/atexit ; le coût exact et le correctif de terminaison demandent le scope distinct RUNTIME_HOLD_NEXT_AMENDMENT.md. Aucun changement worker n’a été appliqué. Le mandat autorise la livraison du correctif tout en conservant explicitement HOLD lorsque les scénarios nominaux atteignent SIGXCPU ; cette réserve empêche l’activation, pas la conservation du correctif désactivé.

Preuves privées : `/Users/martinfeldmann/auren-review/sci-ops-qualify-01-evidence-20261127/v3-context-amendment-20261127/`. Reçus de cleanup et préservation, PR/CI/SHA finaux à compléter depuis leurs résultats effectifs.

## Conservation exécutée
16conteneurs et4volumes de ce seul banc retirés normalement, sans force. Deux exports privés empreintés conservés avant retrait ; image support conservée. Les10conteneurs préexistants (ID,image,PID,démarrage,configurations et montages), volumes préexistants et services sont identiques avant/après. Aucun QA actif modifié.
