# MOB-05A — Progress Core : réalisation contrôlée

10 novembre2026 — BUILD / PIXELS_ACCEPTED_CONTROLLED, non fusionné. GO/G1 explicites reçus,
aucune activation personnelle, publication APK/OTA ou modification QA02/OVH.

## Comportement réalisé

Un seul onglet Progrès dans la coque quatre tabs : séances récentes et leurs faits,
fréquence sur période civile explicite4/12semaines/Tout, index d'exercices exact
et occurrences, poids daté depuis BodyMeasurement sous consentement applicable.
Pas de second modèle, cache SQLite d'historique ou writer. Les comptes couvrent
toute la période, pas seulement les cinq lignes visibles. Une clôture sans série
de travail renseignée ne compte pas comme séance avec faits réalisés. Le planning
daté absent est NOT_PERSISTED, jamais fabriqué depuis une cadence.

Les quatre routes `/api/mobile/v1/me/training-history` et ses sous-routes
`sessions/{session_id}`, `exercises`, `exercises/{exercise_ref}` sont montées dans
l'app réelle. Bearer propriétaire, no-store, foreign/unknown404 identiques,
références signées à fenêtre/propriétaire/identité, changement→READ_CHANGED puis
refresh. Lectures sans DML ; scan borné/pagination explicite et partiel≠vide.

Legacy : noms et faits capturés, contexte/prescription inconnus ; valeurs invalides
distinctes des absences. SCI : vrai client V3 existant puis projection historique
stricte sans action/permission, faits typés conservés même sans guidage actuel.
MACHINE_DISPLAY_KG/PER_IMPLEMENT ne deviennent jamais un total externe. Les
regroupements d'identité ne sont pas une politique de comparaison de charges.

ConnectedApp monte TrainingHistoryHost via ShellContext et vraie route Progrès,
seulement focalisée. AuthSession/WeightHistory existants, mémoire liée au compte,
réponses tardives/refresh/période/unmount gardés. Une erreur5xx garde les faits
confirmés du même compte comme lecture précédente ; elle ne devient pas EMPTY.
Le détail propose le lien serveur exact vers le mouvement et son occurrence
sélectionnée ; back revient par niveaux. Foreground revalide les lectures.

## Tests et revue

Revue unique de toute la branche :0Critical/5Important/2Minor ; une vague de
correction, témoins RED→GREEN. Les cinq corrections :503/pagination, fin des scans
poids au départ de Progrès, valeurs legacy invalides visibles, refus SCI sans
observation typée, lien séance→exercice exact et repère d'occurrence. Aucun second
avis indépendant du correctif final prétendu.

Broad final141tests backend PASS ;87suites/1117tests mobiles PASS. Après le broad,
TSC a relevé un argument requis dans le seul témoin BackHandler : corrigé, puis
TypeScript et4tests de callbacks PASS. Les140PASS/1FAIL antérieurs restent dans
les logs, suivis du module corrigé25PASS puis du broad141PASS, sans résultat
réécrit. Ruff neuf/budget260≤548, Bandit et protocole passent ; CI réelle à venir.

Deux mineurs conservés : échec initial index trop peu explicite (Actualiser
racine reste disponible) ; borne supérieure de période à la date sans heure.
Le type/lien nouveau du contrat historique non publié n'altère aucun DTO SCI.

## Rendus et limites

Board contrôlé :15frames dont2références acceptées intactes et14sources runtime
empreintées. iOS390×844pt : vrai ConnectedApp/AuthSession/SQLite/HTTP, route
initialisée par adaptateur de banc ; actions AX séance→exercice→occurrence et
retours observés. Android : Host/présentateurs de production dans banc HTTP natif,
360/480dp, fonte100/130%. App Android complète Expo Go toujours limitée par module
natif conservé ; aucune suppression/shim, aucun nouvelAPK.

Vues basses positionnées par banc externe après noWindowsAvailable CUA ; pas de
recette gestuelle. Gear/Tools sont overlays Expo Go. Corps/poids/répétitions sont
témoignages synthétiques, pas des faits du testeur. Android vide non confirmé
(délai de reçu), pas de PASS prétendu ; iOS vide/accord requis réellement lu.
Historique SCI réel couvert par services/tests clients, pas un parcours natif
complet revendiqué. Tentative locale avec ancien rawC3 refusée par inventaire2,
règles préservées, aucune séance issue de cette tentative.

Physique, VoiceOver/TalkBack complets, geste, iOS320pt et APK pilote actualisé restent
ouverts. DATA et déploiement/OVH/REL03 restent séparés. Aucune baseline modifiée.
