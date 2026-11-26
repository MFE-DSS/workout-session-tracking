# Plan RED/GREEN à exécuter après GO — aucun nouveau test produit exécuté

Les82tests de la qualification initiale et19tests documentaires du retour architecte étaient des campagnes antérieures : ne pas les réutiliser comme CI du futur lecteur. Les40cas source restent des spécifications/témoins, pas un GREEN du nouvel endpoint. Ici RED et GREEN sont des **résultats attendus**, non observés.

| Tests proposés | RED attendu avant code / GREEN futur exigé |
|---|---|
| contract::strict_request_and_nullable_states | module absent puis from/until/UTC/header, extras/dupes/body refusés ; absence reste NULL ; EXACT/MINIMUM séparés de state/availability |
| sqlite::old_id_prefix_misses_recent_window | avant lecteur : absence de réponse ; après : fenêtre récente sans lignes dans préfixe ancien ->UNKNOWN/TRUNCATED, jamais EMPTY/global last/0 |
| sqlite::global_budgets_and_sentinels | S/E/W/R/G globaux, sentinelles non comptées, aucune augmentation automatique ; row/statement/VM caps observés |
| sqlite::time_boundaries | from inclus/until exclu, session commencée avant from admissible ; NULL/futur/contradiction ne contribuent pas au minimum |
| sqlite::owner_and_read_only | deux owners+NULL, alias global lecture seule, SQL trace zéro DML/DDL même après échec ; GET ne crée ni série ni reçu |
| sqlite::snapshot_facts_receipts_and_sources | mutation concurrente atomique après première lecture : paire ancienne cohérente ; nouveau read : paire nouvelle ; pas de mapping/capture mutable mélangé |
| sqlite::text_admission_before_materialization |2MiBTEXT contre cap8KiB, row étrangère, byte total épuisé, mapping/évaluation128KiB ; aucun read/parse interdit |
| provenance::v3_authority_and_graph | mauvais owner/profil/digest/évaluation/contexte/side/setmapping, substitution, graphe tronqué G ->UNKNOWN ; pas d’appel owned_binding/guard_owner |
| provenance::effective_catalogue_missing | absent/ancienne version/overlayeffectiveroles différent : pas de fallback statique ou E1 ; source correcte exactpinned seulement |
| provenance::origin_revision_and_recomplete | correctionfalse flag, decomplete/recomplete, réceptionperdue/rejeu et révisiontrouée ; état courant unique, date contradictoire non placée ; aucun timestamp réécrit |
| provenance::legacy_estimated_adjusted | canonique datable + provenanceinconnue ->PARTIAL_TIME/lastNULL ; appareil/clientversion absente non inventée |
| projection::completed_work_and_uncertainty | vide, warmup, incomplète, séanceouverte/exclue, donnéespartielles ; aucune prescription promue en fait |
| projection::roles_and_p07 | PRIMARY/SECONDARY/MINOR/UNKNOWN, créditconventionnel inchangé, trois dimensions sans dessin, posterior union sans scalar, doublons/révisions dédupliqués |
| projection::minimum_vs_inspected_exact | exact_evidence de rôles vrai mais couverture tronquée ; quantitéfenêtre MINIMUM si contributioncertaine/datée, sinonNULL ; aucun dernieragrégé |
| projection::machine_and_context | settings MACHINE/PER_IMPLEMENT conservés, weight_kgNULL sans tonnage ni masseeffective inférée |
| worker::caps_and_cleanup | Linuxréel : CPU/AS/SQLVM/deadline/profondeur/tokens/UTF8/clésdupes/output dépassés ->réponsebornée/UNAVAILABLE, kill+wait seulchild, pas mémoire démesurée sur Mac |
| worker::concurrency_and_profile |2erequête sansqueue ->503 ; profil réel différent/manquant, OS/dialecte non qualifié, flagfalse ->UNAVAILABLE ; parentsrlimits inchangés |
| http::bearer_negotiation_inventory | cookie seul401, ownerinjectérefusé, no-store toutesréponses, un GET correctementinventorié, pas de nativeparitédéduite |
| guards::only_exact_descriptive_importer | gardeSCI rouge avec nouvelimportavant amendement, puis whitelist exactprojection.py seulement ; tout autrenouvelimportmoteur reste refusé |

Noms et assertions à développer dans les six fichiers neufs indiqués dans BUILD_SCOPE. Les campagnes futures doivent conserver nom, commande, résultat et SHA. Linux resource tests dans runtime isolé ; sur autre OS tester explicitement UNAVAILABLE, sans déclarer une qualification Linux à partir de mocks. Aucun test dangereux d’allocation sans preuve préalable d’une limite OS effective.

## Local / CI futurs
Exécuter check_scope sur le vrai diff ; prévision shared_code : Ruff fichiers neufs/budget, protocole, tests ciblés +broad obligatoires, **pas full sweep systématique**. Broad proposé : testsSCI exposition/identité/catalogue, history, first_plan execution/persistence/runtime HTTP, mobile_api/protocol/inventaire ; affiner selon imports réels sans omettre les consommateurs. Pas pytest -n auto.

Puis sécurité Bandit/Gitleaks, revue indépendante du diff complet, CI protégée du HEAD réel (backend/mobile/visuel selon pipeline, même sans nouveau pixel) et Sonar réel consultatif. GOV-MERGE-01 seulement après admission/GO/gates satisfaits, sans bypass ; aucune demande routinière de merge. Aucune publication ni nouvelle qualification physique par ce code.

Compléments de revue : tests du schéma complet (chaque objet/extra/enum/nullabilité) et des10invariants croisés ; parité de composition des rôles v2 et digests, manifestes historiques différents du checkout, inventaire2/extension, imports étrangers et plafonds avant loader. Les nouveaux cas restent NON_EXÉCUTÉS.
