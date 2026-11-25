# AUREN — SCI-READINESS-01 : acte d’admission amendé D1–D5

**25 novembre 2026 — UNE pièce autonome à transmettre.**

**Statut : admission recommandée par l’architecte sous amendements ; acte opérateur NON REÇU. Aucun GO BUILD, APPLY, MERGE ou RELEASE.**

Références : retour architecte transmis le25novembre ; CR unique SCI-READINESS-01 ; canonique `1f0122bf4f2d30f7c95d4975b5994d1453363bc5`, revérifié après fetch pour cette révision. La qualification antérieure est conservée. Ce document amende le contrat proposé ; il ne change aucun produit servi.

## 1. Objet admis à la décision

Une mémoire descriptive du **travail musculaire documenté**, permettant d’explorer les séries enregistrées, leurs séances/mouvements, leurs contributions versionnées, leurs dates et leurs limites. Une série marquée accomplie est un fait enregistré, pas une preuve physique indépendante d’exécution. Aucun score d’énergie, récupération, activation physiologique, conseil ou changement d’allocation V3.

Les statuts ci-dessous décrivent **la proposition soumise**, jamais une acceptation opérateur déjà obtenue.

| Décision | Statut proposé | Contrat à admettre |
|---|---|---|
| **D1 — Faits et période** | **ACCEPT PROPOSED** | Owner serveur ; séance terminée et non exclue ; séries `work && completed`. Fenêtre UTC `[from, until)`, `until <= as_of`, fondée sur `SetLog.completed_at`. Aucun repli sur début/fin de séance ou heure de réception. Les séances ouvertes restent hors du sous-ensemble V1 annoncé. |
| **D2 — Autorité des contributions** | **ACCEPT PROPOSED sous preuve d’autorité** | Politique `sci-exposure-credit-v1` : PRIMARY1, SECONDARY0,5, MINOR0 ; UNKNOWN inconnu. Crédits conventionnels, pas physiologiques. Pour V3 : identité exécutée et rôles effectifs du catalogue/bundle applicable, version et digests attestés. Sans preuve : UNKNOWN, sans catalogue courant de repli, nom approximatif ou position E1–E7. |
| **D3 — SCI-P07** | **ACCEPT PROPOSED** | Mapping versionné `sci-p07-bodymap-projection/0.1.0` : quinze dimensions conservées, onze cibles BodyMap. Renommages lateral_delts→delt_lat, rear_delts→delt_post, abs→core. anterior_delts/adductors/hip_flexors restent accessibles hors dessin. posterior présente hamstrings et glutes séparément et l’union dédupliquée des séries : aucun crédit scalaire ni somme des compteurs de rôles. Les dix autres cibles conservent leur dimension source. BodyMap localise des données documentées. |
| **D4 — Lecture et complétude** | **AMENDED — soumis à admission** | Parcours déterministe, inspection bornée et couverture explicitement distincte de la fenêtre ; règles détaillées ci-dessous. Les limites n’assurent aucune représentativité temporelle. |
| **D5 — Provenance temporelle** | **ACCEPT PROPOSED** | Distinguer date canonique, observation d’origine, révision effective, reçu et heure de lecture. Une date de journal exploitable peut rester PARTIAL_TIME, avec dernier qualifié NULL. Le dernier flag estimated=false ne reconstitue pas l’origine. Une heure réemployée de décompletion/recompletion n’est pas une nouvelle heure d’effort. Aucun ancien timestamp réécrit. |

## 2. D4 amendé — six règles contractuelles

**1 — Ordre et récence.** Parcours imbriqué par IDs croissants : séances propriétaires, exercices de chaque séance, puis séries de travail accomplies ; opérations V3 par révision croissante. Budgets globaux proposés S200/E200/W500/R1000, avec sentinelles non contributives. Ce préfixe peut privilégier des séances anciennes et manquer les événements récents demandés. Un ID n’est pas une date. Aucun tri récent, échantillon représentatif ou exhaustivité implicite. Pas d’augmentation arbitraire des budgets.

**2 — Trois périmètres.** Séparer : **fenêtre demandée**, **sous-ensemble effectivement inspecté** et **couverture complète attestée**. Cette dernière exige l’épuisement des branches nécessaires et la qualification des sources nécessaires à chaque affirmation. Un scan épuisé ne résout pas automatiquement les dates ou mappings inconnus ; il ne prouve jamais la complétude de l’historique réel de l’athlète.

**3 — Candidats non qualifiables.** NULL, date illisible, futur à as_of ou épisode temporel contradictoire : pas de contribution à un total daté ni à sa borne minimale ; omission et cause explicites. Une branche tronquée reste inexplorée, jamais vide. Identité/rôle/source non prouvés : UNKNOWN. Une date canonique utilisable avec provenance estimée/inconnue reste présentable comme date du journal sous PARTIAL_TIME selon D5, sans certification physique ; cette tolérance ne couvre pas un épisode contradictoire.

**4 — Bornes et dernières observations.** MINIMUM ne contient que des contributions certaines, datables et attribuables à la fenêtre selon l’horloge canonique déclarée, dédupliquées dans la même capture. Sans part certaine : NULL/UNKNOWN. Le crédit0 d’une contribution MINOR connue ne signifie pas absence de travail. Si une couverture nécessaire manque : aucun total exhaustif, aucune absence de travail, aucun dernier événement agrégé prétendument exhaustif ; `last_qualified_observation = NULL`. Un fait inspecté reste consultable individuellement sans être présenté comme « le dernier ». Même avec parcours épuisé, une inconnue susceptible de modifier le résultat empêche sa certification.

**5 — Capture et ressources.** Même capture cohérente pour faits effectifs, owner/graphes, révisions, observations/reçus, bindings et sources/politiques applicables. SQLite : lecteur neuf, transaction explicite avant première lecture, aucun cache périmé ; sources externes immuables épinglées par digest. Caps d’entrée proposés inchangés :8KiB par observation/reçu,128KiB par binding,2MiB cumulés avant parse. Ils ne bornent pas à eux seuls mémoire des objets, CPU ou sortie. Plafonds explicites et éprouvés de forme/profondeur JSON, temps SQL/total, mémoire et sortie sérialisée sont obligatoires avant service. **Leurs valeurs et l’intégration de déploiement restent à qualifier : runtime HOLD jusque-là.**

**6 — Échec fermé.** PARTIAL seulement si la part publiée reste certaine, cohérente et dans tous les plafonds ; sinon UNAVAILABLE. Aucun parse incomplet utilisé comme preuve. PostgreSQL, autre runtime ou stratégie non qualifiée restent HOLD. Une fenêtre trop grande peut légitimement demeurer PARTIAL ou UNAVAILABLE.

## 3. Trois invariants non négociables

- **Temporalité :** événement non datable ≠ contribution à un total certifié d’une fenêtre ; inconnue ≠ absence d’entraînement.
- **Complétude :** `exact_evidence` qualifie les rôles/crédits du sous-ensemble, pas l’historique complet ni la provenance exacte de l’heure.
- **Autorité :** catalogue actuel de repli, géométrie anatomique ou correction locale non relue ne remplacent jamais l’identité effective et sa source qualifiée.

## 4. Première implémentation proposée — sans autorisation actuelle

Après admission SCI seulement, préparer un **GO BUILD propre pour la projection serveur read-only et son transport strict**, sur le runtime SQLite qualifié. Inclure owner, faits effectifs Legacy/V3, rôles/politiques, P07, fenêtre, détails de sources, capture et limites/UNKNOWN/PARTIAL. Une source V3 non prouvable reste UNKNOWN. Forme finale de route/DTO, inventaire, fichiers et leases à fixer dans ce futur paquet.

Pas de nouveau writer, migration/index opportuniste, moteur de récupération, modification de classement, auth, TIME-01, SQLite de reprise ou journal historique. Pas d’UI dans cette première tranche proposée. L’instrument natif viendra avec scope/GO explicites ; G1 artistique DA-READINESS-01 conservé et gate des vrais pixels maintenu.

Le lecteur ne sera servi qu’après qualification du runtime exact, des limites et des invariants, tests ciblés/broad, revue et CI applicables. Les40cas documentaires et les expériences isolées antérieures **ne sont pas un GREEN du futur endpoint**. Ajouter notamment les témoins préfixe ancien/manque récent, branche tronquée, rôles exacts/couverture incomplète, borne minimale et dépassements de ressources. Aucun de ces nouveaux tests produit n’a été exécuté dans cette révision documentaire.

## 5. Risques résiduels et correctifs séparés

Chaînes de reçus/catalogues manquants, dates Legacy peu qualifiées et réemploi V3 peuvent maintenir des résultats UNKNOWN ou un dernier qualifié NULL. Les mesures SQL/snapshot/transport isolées ne certifient ni ORM complet, ni mémoire RSS, ni latence réelle, ni PostgreSQL. Ces limites ne sont pas contournées par l’admission du contrat.

Ordre architecte proposé, **aucun GO BUILD reçu pour ces correctifs** :

1. **hist-01 coverage-explanation** : ne plus dire « déjà bien servi » sans base de comparaison ; prouver l’invariance des classements, candidats et gagnants.
2. **hist-04 provenance-language** : corriger les consommateurs restants, garder le wire hérité ; ne pas rouvrir MISSION déjà corrigé.
3. **hist-02 recorded-strength-evidence** : distinguer exercice planifié et série enregistrée, après admission de l’effet sur les entrées de récupération/allocation ; expliquer les divergences.
4. **hist-03 template-recency** : maximum de récence par slug, après admission séparée des effets sur rang, alternatives et gagnant.

L’ordre3/4 peut dépendre des leases ; aucun regroupement opportuniste. Les findings temporels V3 restent autonomes ; aucune réattribution de l’ancien incident TIME-01.

## 6. Acte opérateur — à recevoir

**Verdict actuel : HOLD_SIGNATURE_OPÉRATEUR.** D1/D2/D3/D5 restent ACCEPT PROPOSED ; D4 est AMENDED ; runtime de déploiement et PostgreSQL restent HOLD de qualification.

Décision possible à enregistrer : **« J’admets le contrat descriptif SCI-READINESS-01 amendé D1–D5 du25novembre2026, y compris les six règles D4. Cette admission ne vaut pas GO BUILD, APPLY, MERGE, DATA ou RELEASE. »**

Alternative : préciser les amendements demandés et maintenir HOLD. Référence/date de l’acte : **non renseignées**. L’architecte a recommandé l’admission ; aucune signature opérateur n’est déduite de son retour ou de l’envoi de ce document.

PILOT-01/DATA, QA, TIME-01, APK/OTA et acceptation physique gardent leurs décisions indépendantes.
