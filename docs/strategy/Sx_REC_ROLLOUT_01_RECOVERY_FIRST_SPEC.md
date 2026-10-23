# Sx_REC_ROLLOUT_01 — La séance suivante se choisit par la récupération ; le cardio est le plan B

**Statut :** SPEC + BUILD (`Sb_REC_ROLLOUT_01_RECOVERY_FIRST`) · **Date :** 2026-10-23 ·
**Tier :** `shared_code` (`recommendation_v3`) · **Origine :** décision opérateur **D14**, après
le premier essai physique du client mobile vNext.

**Nature de la règle — à lire d'abord.** D14 est une **règle produit provisoire**, valable pour
un pratiquant dont l'objectif est la prise de muscle ou la force — ce que sont aujourd'hui tous
les gabarits du catalogue, et le moteur ne connaît encore aucun objectif. Ce n'est pas une
règle scientifique générale : pour un objectif « remise en forme », le cardio est un stimulus
de premier rang. Elle sera remplacée par la répartition par objectif du moteur scientifique V2
(en spécification). Elle corrige d'ici là un défaut vivant mesuré (§2).

## 1. Décision opérateur (D14)

> Quand on démarre rapidement une nouvelle séance, on propose les séances **par
> récupération** : la plus logique est celle dont **aucun muscle n'a été sollicité** ; la
> deuxième, celle où il en reste le moins à récupérer. Chaque muscle a besoin d'un certain
> temps de récupération. **Cardio + abdos est le plan B** : proposé seulement quand tous les
> autres groupes musculaires sont en récupération.

## 2. Ce que fait le moteur servi aujourd'hui — mesuré

Sonde sur trois nouveaux utilisateurs réels (base jetable, services canoniques), classement V3
complet après leur première séance :

| Première séance | Gagnant aujourd'hui | Pourquoi | Conforme à D14 ? |
|---|---|---|---|
| `push-a` | **`liss-abs`** (cardio) | cinq gabarits de force sont **pleinement récupérés** et égaux sur la couverture et la répétition ; le critère 4 **« modalité délaissée »** les départage en faveur du cardio | ❌ |
| `legs-a` | `push-a` | bande de récupération | ✅ |
| `full-body-morphotype-priority-v1` | `liss-abs` | **tous** les gabarits de force sont en bande `INSUFFISANTE` | ✅ — c'est le plan B |

Sur le corpus `REC-CP` (17 trajectoires, 78 décisions), V3 servait le cardio dans **64
décisions sur 78 (82 %)**. Le défaut tient en **un seul critère** : pour qui n'a jamais fait de
cardio, `days_since_last_cardio = None` vaut « le plus ancien de tous », et la modalité
délaissée donne au cardio **chaque** égalité.

## 3. La règle

Précédence V3 amendée, sans somme pondérée :

| # | Critère | Statut |
|---|---|---|
| 0 | éligibilité (archivé, fatigue, redondance 24 h) | inchangé |
| 1 | bande de récupération — pire zone du gabarit | inchangé |
| **1 bis** | **plan B : à bande égale, la force passe avant le cardio** | nouveau — le cardio ne gagne que si aucun gabarit de force n'est dans une bande au moins aussi bonne |
| **1 ter** | **le moins sollicité : moins de zones encore en récupération** (décision ≠ non limitante) | nouveau — « la deuxième la plus logique » |
| 2 | couverture longitudinale | inchangé |
| 3 | justification de répétition | inchangé |
| **3 bis** | **les muscles les plus reposés** : heures depuis la dernière charge de la zone la moins reposée ; jamais chargée = la plus reposée | nouveau — imposé par la mesure (§6) |
| ~~4~~ | ~~modalité délaissée~~ | **retiré** — remplacé par 1 bis |
| 5–6 | ancienneté du gabarit / de la famille, ordre de catalogue | inchangés |

**Pas de disponibilité fine 0–1 dans le rang.** L'estimation du contrat de récupération est une
estimation, pas une mesure ; départager 0,85 et 1,0 serait une fausse précision et rendrait la
couverture muette dans toute la bande récupérée. 1 ter est un **compte** ; 3 bis lit un **fait
horodaté** (heures depuis une charge enregistrée), placé **après** la couverture pour que
l'équilibre sur quatorze jours décide d'abord.

Une zone **sans charge observée** reste **non limitante** (arbitrage TRAIN A, inchangé) : elle ne
compte pas en 1 ter et vaut « la plus reposée » en 3 bis, sans partager la **preuve** d'une zone
connue (l'explication continue de les distinguer).

## 4. Explication

« La modalité la plus délaissée. » disparaît avec son critère. Le plan B reçoit sa phrase,
vraie par construction et toujours énoncée en premier : **« Tout le reste récupère encore :
séance cardio. »** 1 ter et 3 bis ne s'énoncent que lorsqu'ils ont départagé (« Le moins de
zones encore en récupération. », « Les muscles les plus reposés. »). `CRITERES_DU_RANG` et
les gardes de parité d'explication (`REC-CP5`) sont mises à jour **dans la même tranche** : on
remplace un critère, on n'affaiblit aucune garde.

Le contexte de la recommandation porte un nouveau drapeau, `departage_sans_historique` :
égalité de tête dont aucune zone des deux candidats n'a d'historique de charge.

## 5. Tests d'acceptation (`tests/test_rec_rollout_01_recovery_first.py`)

1. Nouvel utilisateur, après `push-a` : le gagnant est un gabarit **de force** en bande
   récupérée ; le cardio n'est pas premier.
2. Après `full-body-morphotype-priority-v1` : le cardio est premier (plan B), toute la force fait
   moins bien, la phrase est celle du plan B.
3. Après `legs-a` : une séance de force est première.
4. Jamais de cardio fait, tout récupéré : la force gagne ; aucun cardio n'est marqué plan B.
5. 1 ter : compte des zones en récupération ; carte absente = neutre.
6. 3 bis : le repos est un fait ; zone jamais chargée = la plus reposée ; gabarit sans zone = neutre.
7. Le critère et la phrase de la modalité ont disparu du module.

## 6. Mesures du build (2026-10-23)

**Gagnants changés sur le corpus `REC-CP`** : **64 / 78**, **tous** du même motif — `liss-abs`
→ une séance de force. Aucun changement inverse, aucun hors motif.

**Boucle fermée « nouvel utilisateur »** (12 décisions, sans échauffement) : avant
`push-a → liss-abs → pull-b → full-body → pull-a → legs-a → …` ; après
`push-a → pull-b → legs-a → pull-a → full-body → full-body → …`. En boucle fermée, la part
tranchée par le catalogue reste à 0,10–0,20 (inchangée).

**Garde `REC-CP2` « ≤ 15 % de décisions tranchées par le catalogue » — arbitrage opérateur.**
Retirer la modalité faisait passer cette part de 0 % à 67 % sur le corpus ouvert ; 3 bis la
ramène à 47 %. Sur les égalités restantes, la grande majorité opposent deux séances dont
**aucune zone n'a d'historique de charge** : aucun fait ne peut les séparer. Le 0 % d'avant
n'était pas une preuve : il était produit par le défaut lui-même. **Décision (opérateur,
2026-10-23)** : la garde ne compte plus que les égalités **où un historique existait**
(mesuré : **4 %**) ; la part sans historique (44 %) est **publiée** par le test, et chaque
décision concernée doit porter une phrase.

**Défauts préexistants rendus visibles**, hors périmètre, à traiter dans leurs propres
tranches :
- les zones d'un gabarit sont les zones primaires présentes dans au moins un quart de ses
  exercices (`recommendation._primary_zones_of`) : `full-body-morphotype-priority-v1` (8
  exercices, seuil 2) ne garde que « mollets » ;
- les séances **utilitaires** (`short-upper`, `no-equipment-full-body`) entrent dans la rotation
  par défaut.

## 7. Ce que cette spec superséde

`SPRINT_REC_CP2_POLICY_V3_REPORT` critère 4 « modalité délaissée ». La leçon de ce critère reste
juste — V2 offrait trente points permanents au cardio — et 1 bis la tient plus fermement : le
cardio n'a plus aucun bonus, il devient le recours quand la force n'est pas disponible.

## 8. Non-goals

- Aucune migration ; aucune modification du contrat de récupération ni des cibles
  `RECOVERY_HOURS_TARGET`.
- Aucun changement d'éligibilité, de couverture ou de mémoire de conseil.
- Aucune correction des zones de gabarit ni des séances utilitaires (§6, tranches propres).
- Aucune UI : le web et le client mobile rendent le nouveau gagnant sans changement de code.
- Le choix de la **première** séance d'un nouvel utilisateur n'est pas ici : il n'a pas
  d'historique à classer.
