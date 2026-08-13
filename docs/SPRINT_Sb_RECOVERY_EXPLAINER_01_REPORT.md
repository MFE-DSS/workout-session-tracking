# SPRINT Sb_RECOVERY_EXPLAINER_01 — Explication déterministe (RAPPORT)

**Base canonique :** `71d36cd` · **Branche :** `sb/recovery-explainer-01` · **Tier :**
**ISOLATED** (`check_scope`) — deux fichiers neufs, module feuille réel : rien ne l'importe hors
son propre test. **Full sweep local non requis** (CLAUDE.md §1) ; **broad sweep ciblé exécuté**.
**Autorité de spec :** `Sx_RECOVERY_READINESS_01_SPEC.md` §8, §11 (`Sb_RECOVERY_EXPLAINER_01`).
**Tranche 5/5 — dernière de la file P0.4.** **Dépend des quatre précédentes.**
**0 migration · 0 modèle · 0 colonne · 0 UI · 0 activation Body Intelligence ·
0 modif `recommendation.py`/`behavioral.py` · 0 décision d'entraînement · 0 LLM.**

## 1. Brainstorming / Options / Risques / Choix retenu (CLAUDE.md §3)

**Audit préalable des conventions existantes**, avant tout nommage. Deux précédents dans le repo :

| Précédent | Forme | Verdict |
|---|---|---|
| `recommendation_explainer.explain_recommendation` | renvoie un `dict[str, Any]` | Écarté : un dict libre ne porte aucune garantie structurelle, et c'est précisément la garantie qui est le livrable ici. |
| `program_quality_feedback` | wrapper de présentation **pur** sur `program_quality_engine`, `@dataclass(frozen=True)`, doctrine de microcopy documentée | **Retenu.** Même rôle, même contrainte (aucun recalcul), convention déjà éprouvée. |

**Options envisagées pour `Confidence.NONE`** — la vraie question produit de la tranche :

1. **Silence total, zone retirée.** Rejeté : une zone attendue qui disparaît est indiscernable
   d'une zone oubliée. L'utilisateur ne peut pas distinguer « on ne sait pas » de « on n'a pas
   regardé » — exactement le défaut que `Sb_ZONE_RECOVERY_ESTIMATE_01` a fermé côté données.
2. **Phrase neutre rassurante** (« rien à signaler »). Rejeté : c'est une affirmation sur le corps
   sans preuve, donc le fail-open du train transposé au langage.
3. **Message d'état de donnée, dans un champ séparé, dépendant de la surface.** **Retenu** — et
   c'est la décision opérateur. Une surface qui attend l'estimation dit explicitement que la donnée
   manque ; une surface proactive omet la zone.

**Risques identifiés avant d'écrire du code, et leur parade :**

| Risque | Parade |
|---|---|
| Le vocabulaire interdit du §8.2 atteint l'écran | Garde-fou exécuté **sur la sortie rendue réelle**, pas sur la source ; violations plantées pour prouver qu'il mord |
| Un « données insuffisantes » est trié comme une bande | Collections séparées **et** `recovery_rank_key` qui **lève** |
| La prose interne des `basis` fuit dans l'UI | Table de marqueurs **fermée** + motif anti-`snake_case` sur le rendu |
| La couche devient l'orchestrateur en douce | Liste de verbes de décision testée sur la sortie ; aucun accès DB, aucun `WorkoutSession` |
| Afficher une confiance que rien ne produit | `MAX_RENDERABLE_CONFIDENCE`, `HIGH` non rendable |

## 2. Contrat d'explication exact

```python
@dataclass(frozen=True)
class ExplanationItem:
    kind: str                        # zone_recovery | macro_axis | readiness | cardio | data_prompt
    message: str                     # phrase produit, déjà en français
    is_estimate: bool                # True = lecture de récupération ; False = état de donnée
    subject: str | None              # code machine (zone_code / axis_key) — NON rendu
    subject_label: str | None        # forme affichable, vocabulaire canonique
    confidence: Confidence | None    # plafonnée à MEDIUM
    confidence_label: str | None     # « Confiance faible » / « moyenne » / « Données insuffisantes »
    band: RecoveryBand | None        # tel que produit en amont — jamais recalculé
    reasons: tuple[str, ...]         # basis traduit, liste fermée
```

`__post_init__` **lève** si `is_estimate=True` sans confiance, et si `kind` sort du vocabulaire
fermé. La règle « toute phrase de disponibilité est accompagnée de sa confiance » (DoD §11) est donc
une **invariante de construction**, pas une convention.

`RecoveryExplanation` sépare `zone_items` · `data_state_items` · `macro_items` ·
`readiness_item` · `cardio_item` · `data_prompt`. Une surface qui itère naïvement **ne peut pas**
afficher « données insuffisantes » au milieu de bandes de récupération.

## 3. `Confidence.NONE` — comportement exact

**Silence sur la physiologie, explicite sur la donnée manquante.**

- Aucune phrase de récupération n'est émise : ni « probablement disponible », ni « encore chargée »,
  ni prudence, ni réassurance.
- Le seul énoncé autorisé porte sur la **donnée** : `« Pas assez de données récentes pour estimer
  cette zone. »`, étiquetée `« Données insuffisantes »`.
- Cet item est `is_estimate=False`, vit dans `data_state_items`, et **`recovery_rank_key` lève un
  `ValueError`** s'il lui est passé.

**Cas limite tranché :** une bande exploitable arrivant avec `Confidence.NONE` est traitée comme un
état de donnée. **C'est la confiance qui décide, pas la bande** — sinon une affirmation sur le corps
passerait sans preuve.

| Surface | Zone `NONE` | Total pour un compte neuf |
|---|---|---|
| détaillée | visible, état de donnée explicite | **11 zones + 6 axes** structurellement présents, **0** explication physiologique |
| proactive | **omise** | **1** message agrégé, jamais onze |

## 4. Exemples de sortie réelle

**MEDIUM** — `« Cette zone semble probablement disponible. »` · *Confiance moyenne* ·
raison : « Du travail en force a été enregistré récemment pour cette zone. »

**LOW** — `« Cette zone semble encore chargée par l'entraînement récent. »` · *Confiance faible* ·
raisons : travail en force · « Une exposition cardio récente est prise en compte pour cette
zone. » · « L'attribution de certains exercices à cette zone reste approximative. »

**NONE** — `« Pas assez de données récentes pour estimer cette zone. »` · *Données insuffisantes* ·
aucune raison inventée.

**Cardio** — `« Ton activité cardio récente (vélo) est prise en compte comme exposition récente
pour : Quadriceps, Ischios / Fessiers. »` · « Exposition enregistrée, pas une mesure de fatigue
musculaire. » Les zones viennent de `cardio_zone_exposure`, table canonique de l'adaptateur.
Modalité hors vocabulaire ⇒ **aucune zone nommée**.

**Readiness** — `« Tu as déclaré te sentir moins frais aujourd'hui. »` · « Déclaration personnelle,
pas une mesure. » Bonne readiness ⇒ `« Tu as déclaré te sentir en forme aujourd'hui. »`, **jamais**
une autorisation d'escalade (OQ-7). Déclaration périmée ⇒ contexte, surface détaillée uniquement.

## 5. Traduction des `basis` : liste fermée, sinon omission

Les `basis` amont sont de la prose d'ingénierie (`readiness_entry 2026-08-11 (3d old)`,
`no usable cardio_duration_min`, `behavioral producer unavailable (OperationalError)`). **Aucune
n'est rendue.** Les raisons viennent des **champs structurés** plus une **table de marqueurs
fermée** ; un `basis` non reconnu est **omis**, jamais deviné.

Deux tests le prouvent : un `basis` inconnu portant un nom de sentinelle ne sort pas, et l'ajouter
ne change **rien** aux raisons produites.

Le nom de modalité cardio est le seul fait que seul le `basis` porte. Il n'est lu que dans les
entrées portant un marqueur cardio connu, et n'est retenu que s'il appartient au vocabulaire fermé
`CardioModality` — `autre` et `unknown` en sont exclus par construction.

## 6. Le garde-fou de formulation mord (§8.4)

Il exécute **l'explainer public réel** sur neuf états représentatifs plus des états construits
**depuis un compte persisté**, et scanne chaque chaîne rendue : liste de termes (§8.2 + verbes de
décision + champs cardio non individualisés) et motifs (`%`, durées chiffrées, `snake_case`).

**Preuve exécutée.** Planter dans le module une phrase de bande en langage interdit
(`« Cette zone est récupérée à 100 % »`, `« Récupération musculaire mesurée »`, `« Repose-toi, il te
faut encore 24 heures »`) et une raison fuyant un identifiant fait échouer **10 tests**, dont
**deux passant par la base réelle**. Après retrait : 158/158.

Les codes machine (`subject`) sont **exclus** du scan : `delt_lat` est un code, pas du texte
affiché, et le scanner condamnerait le vocabulaire canonique lui-même — la seule issue serait
d'affaiblir le motif.

## 7. Aucun langage de décision

Aucune chaîne rendue ne contient `augmente` · `baisse` · `remplace` · `reporte` · `repose-toi` ·
`entraîne-toi` · `skip` · `ajoute des séries` · `tu peux pousser` · `tu devrais` (test paramétré,
11 cas). Aucun classement de séance : le module ne mentionne pas `WorkoutSession`, n'ouvre aucune
`Session` SQLAlchemy et n'importe ni `recommendation` ni `behavioral`.

**Le seul impératif** est `« Renseigne ton état du jour pour améliorer l'estimation. »` : il porte
sur la **collecte**, il vit dans son propre champ `data_prompt`, et il disparaît dès qu'une
déclaration existe.

`recovery_rank_key` ordonne des **items à l'écran** (plus contraint d'abord) et ne choisit ni séance,
ni volume, ni exercice.

## 8. Divergences héritées — inchangées

Cette tranche **n'ajoute aucune divergence**. Les trois de `zone_recovery.LEGACY_DIVERGENCES`
(zone jamais entraînée rendue disponible · sentinelle `24×365` · cardio absent du chemin hérité)
restent la seule liste, toujours épinglée par son test. `recommendation_explainer` est intact : son
point d'entrée et ses 134 tests de non-régression passent, et le nouveau module ne l'importe pas.

**Écart de vocabulaire assumé** : la couche héritée dit `ok`/`low`, celle-ci dit une bande ordinale.
Rien n'est aligné de force ; la conversion canonique reste `confidence_from_legacy_label`.

## 9. Amendement de spec (§8.4 / DoD §11)

La DoD disait `confiance none ⇒ **silence**, jamais une phrase rassurante`. La décision opérateur la
**précise sans la contredire** : silence sur toute interprétation corporelle, **plus** un état de
donnée explicite et séparé sur une surface qui attend l'estimation. Le silence porte sur la
physiologie, pas sur la transparence. Consigné ici plutôt qu'appliqué en silence.

## 10. Le faux échec de CI — et ce qu'il dit de ma stratégie de vérification

**Un seul test a échoué en CI**, et sa cause n'était pas le contrat :

```
assert MAX_RENDERABLE_CONFIDENCE is CARDIO_MAX_CONFIDENCE
AssertionError: assert <Confidence.MEDIUM: 'medium'> is <Confidence.MEDIUM: 'medium'>
```

`MAX_RENDERABLE_CONFIDENCE` était lié **à la collecte**, `CARDIO_MAX_CONFIDENCE` importé **dans**
le test. La `conftest` purgeant `app.*`, les deux venaient de **générations différentes** de
`recovery_contract` : deux enums `Confidence` distincts, valeurs identiques, identité fausse.

Corrigé en résolvant **les deux côtés dans la même génération**, **sans** relâcher `is` en `==` —
changer d'opérateur aurait verdi la CI en masquant la cause. Un **second site latent** (vocabulaire
des modalités) a été rendu explicite : il ne survivait que parce que `StrEnum` compare par valeur.

**Ce que ça corrige dans la méthode, au-delà de ce sprint.** 158 tests ciblés et **1411** de broad
sweep étaient verts. Cette classe d'échec **n'apparaît que sous l'ordonnancement du full sweep**.
Donc dès qu'un fichier de tests mélange imports de niveau module et imports locaux d'`app.*`, le
verdict de tier ne suffit pas : lancer le full sweep avec **l'invocation exacte de la CI**
(`-n auto --dist worksteal --ignore=tests/test_v1_acceptance.py`, ~4 min). Consigné en mémoire.

## 11. Finding de revue Gitar — un âge inconnu ne prétend plus à la fraîcheur

`ReadinessSignal.age_days` vaut `None` par défaut et peut l'être alors que `overall` est renseigné.
Le choix `« aujourd'hui »` / `« récemment »` reposait sur `age_days == 0`, donc un âge **inconnu**
— et un âge **négatif** (horloge décalée) — se rendait silencieusement en `« récemment »`.

Gitar a jugé l'impact faible, `build_training_state` peuplant toujours un entier. **La formulation
justifiait le correctif quand même** : affirmer une fraîcheur que la donnée ne porte pas est
exactement la fabrication que cette tranche interdit partout ailleurs, et c'était le **seul** endroit
où une valeur absente produisait une affirmation.

Un âge inconnu ou négatif ne produit désormais **aucun mot de temps**. Retirer la garde fait échouer
**2 tests** ; un âge connu de 2 jours dit toujours `« récemment »` — la correction **borne** le cas
inconnu **sans désactiver** le cas connu.

## 12. Tests

| Portée | Tests |
|---|---|
| Dédiés `test_recovery_explainer.py` | **163** |
| Chaîne P0.4 (contrat · cardio · agrégateur · estimateur · explainer) | **539** |
| Explainer hérité + P0.1 / P0.2 / P0.3 | **134** |
| Broad sweep ciblé (dashboard · home · profile · body · reco · recovery · cardio · zone · muscle) | **1411** |
| **Full sweep, invocation identique à la CI** | **3691, 0 échec** |

Pré-scan Sonar (S9073 · S1192 · S5863/S1764 · S1244) exécuté sur **le fichier applicatif ET le
fichier de test** avant **chaque** push — trois littéraux dupliqués extraits en constantes au total.
Gate Sonar **`OK`**, couverture du code neuf **99.5 %**, **0** smell, **0** bug.

## 13. Ce que cette tranche ne fait pas

Aucun consommateur n'est branché. `recovery_explainer` est importé par son seul test : la frontière
d'intégration de la mission est respectée, et le branchement Home / Body Intelligence appartient à
un sprint consommateur explicite ultérieur. Body Intelligence **n'est pas activée**.

---

## Verdict

**Livré, mergé, canonique verte.** La file **P0.4 est complète (5/5)**.

Ce que cette tranche apporte tient en une phrase : **une absence de donnée ne peut plus se déguiser
en estimation** — ni dans le calcul (les quatre tranches précédentes s'en chargeaient), ni
désormais **dans les mots**. `Confidence.NONE` ne produit aucune phrase sur le corps, le constat de
donnée manquante vit dans une collection séparée, et le tri **refuse** de le classer comme une
bande. La séparation est structurelle : un consommateur ne peut pas confondre les deux **même en
itérant naïvement**.

**Limite assumée, à ne pas oublier au branchement** : rien ne consomme cette couche. Elle est
prouvée sur des `TrainingState` synthétiques **et** sur un compte persisté réel, mais la première
surface qui l'affichera devra vérifier qu'elle respecte la règle de contexte (détaillée = garder les
onze zones ; proactive = omettre, sans inonder). Le garde-fou de formulation vit dans le module et
reste exécutable par n'importe quel consommateur — c'est délibéré.

## 14. Closeout post-merge

| | |
|---|---|
| PR | **#83** — `MERGED` |
| Build → correctif CI → correctif Gitar | `7f363f7` → `57325c5` → `46c7cbd` |
| Merge | **`534cbc2`** (`--merge --match-head-commit 46c7cbd`, **sans squash / `--admin` / force**) |
| Gate PR | `CLEAN` · **4/4** dont le gate **externe** `SonarCloud Code Analysis` |
| Sonar | **`OK`** · couverture du neuf **99.5 %** · **0** smell · **0** bug · **0** vulnérabilité |
| Threads de revue | **0 non résolu** (le thread Gitar résolu **après** correctif poussé) |
| CI canonique faisant foi | **`31675257579` — 3/3 GREEN** sur `6d16357` |

**Pourquoi la CI canonique n'est pas celle du commit de merge — et pourquoi c'est légitime.**
Deux incidents d'infrastructure successifs, **aucun n'ayant produit de commit en réponse** :

1. Le run `31674056214` sur `534cbc2` est **rouge sur un échec réseau pur** : l'étape `Checkout`
   n'a pas pu joindre `github.com:443` (3 tentatives ~133 s, `exit 128`). **Le code n'a jamais
   tourné.** Conformément à `CLAUDE.md §2` — distinguer un échec de test d'une annulation
   d'infra — la réponse a été un **re-run des jobs échoués**, sans nouveau commit.
2. Ce re-run a ensuite été **annulé par le groupe de concurrence** : la **session parallèle** a
   mergé la **PR #84** (`sb/sonar-governance-01`) sur la canonique à 06:48, déclenchant le run
   `31675257579` qui a préempté le précédent.

La CI faisant autorité pour ce code est donc celle de `6d16357`, **vérifiée verte 3/3** et dont il
est **prouvé** qu'elle contient ce merge : `git merge-base --is-ancestor 534cbc2 6d16357` ⇒ `0`, et
`app/services/recovery_explainer.py` est présent à ce SHA au commit `46c7cbd`. La garantie est
**plus forte** que le run initial, pas plus faible : la suite complète a tourné sur un arbre
contenant à la fois cette tranche et la gouvernance Sonar.

**Coordination avec la session parallèle.** La PR #84 touche `ROADMAP_AND_NEXT_STEPS.md` et
`SPEC_REGISTRY.md`, **les deux mêmes fichiers** que ce closeout. Les éditions locales, faites contre
la version antérieure, ont été **retirées puis ré-appliquées** contre le nouveau contenu après
fast-forward, plutôt que fusionnées à l'aveugle : `git diff --stat` confirme **2 insertions,
0 suppression** — aucune ligne de la session parallèle n'a été écrasée.
