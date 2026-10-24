# SPRINT Sb_SCI_V2_02 — Résolveur d'identité scientifique et registre d'exposition dérivé

**Spec :** `docs/strategy/Sx_SCI_V2_CATALOGUE_INTEGRATION_01_SPEC.md` (v3 : §6, §7) · **Base :**
`7aed4e4` · **Date :** 2026-10-24 · **Branche :** `sb/sci-v2-02-identity-exposure`

## 1. Objet

La tranche construit deux couches :
- **le résolveur** (§6) : nom historique ou `variant_key` → identité scientifique → fiche
  canonique, de façon déterministe, en lecture seule, et avec un inconnu explicite ;
- **le registre d'exposition** (§7) : une ligne par série de travail réalisée et par zone
  contributrice, avec le **rôle brut**, puis un agrégat par zone qui applique la politique de crédit
  à la lecture et ne transforme jamais un UNKNOWN en zéro.

Aucun consommateur du produit. Rien ne change : V3, l'exposition servie (`muscle_scoring`,
`zone_exposure`, `set_contribution`), TRAIN A, la base, l'UI et le laboratoire N0.

## 2. Brainstorming / Options / Risques / Choix retenu

### 2.1 La règle d'éligibilité que la spec désignait n'existait pas

La spec v2 citait « la règle de `set_contribution` ». Lecture faite, ce module ne compte que des
séries **planifiées** (`planned_sets`) : il n'a aucune règle sur les séries exécutées.

| Option | Pour | Contre |
|---|---|---|
| (a) Inventer une règle « raisonnable » | rapide | une seconde notion de « série faite » dans le dépôt, exactement ce que `zone_exposure` interdit en toutes lettres |
| (b) Reprendre la règle qui fait foi : `zone_exposure._work_sets` (= `kpis.work_sets_done_30d`) et les bornes de séance de `muscle_scoring` | une seule notion ; parité épinglable | `_work_sets` est privée |

**Choix : (b).** Le prédicat est écrit dans le module, puis une **garde de parité** le compare à
`zone_exposure._work_sets` sur des séances semées. C'est préférable à importer une fonction
privée d'un module servi, ce qui ferait de ce module une dépendance de l'ombre. La spec est
corrigée en v3, et la correction est déclarée.

### 2.2 Index du résolveur : dérivé ou stocké

La spec a déjà tranché pour un index **dérivé** de l'EKB au chargement (§15). Deux faits restaient
à traiter.
- **La collision mesurée sous `normalize`** (« Curl marteau câble (corde) » / « … corde ») : les
  deux fiches partagent la même identité scientifique. Elles se résolvent donc sans ambiguïté vers
  la fiche canonique. Une collision entre identités **distinctes** est refusée au chargement.
- **La garde de renommage** doit se souvenir de noms qu'aucun index dérivé ne connaît plus. Un
  relevé figé (`data/sci/legacy_name_ledger.json`) la porte. Il est **lu par les tests
  seulement**, jamais à l'exécution : ce n'est pas un pont stocké.

### 2.3 Que vaut l'étape « base » (`resolve_exercise`) ?

Aujourd'hui, la graine d'identité ne crée que des noms déjà présents dans l'EKB. L'étape 3 ne
résout donc rien que l'étape 2 ignore. Elle est gardée parce qu'un alias ajouté en base (geste
produit `add_alias`) doit rester lisible. Elle est **en lecture seule**, et une garde de
concordance vérifie que les étapes 2 et 3 donnent la même fiche sur tout le corpus semé.

### 2.4 Forme des sorties

- **Les lignes du registre portent le rôle brut, jamais le crédit.** L'agrégat applique
  `sci-exposure-credit-v1`. `UNKNOWN_CREDIT` refuse l'arithmétique ; l'agrégat compte donc
  l'inconnu à part et ne l'additionne jamais.
- **Une série d'identité inconnue** produit une ligne sans zone. Elle fait passer **toutes** les
  zones de la fenêtre en `MINIMUM`.
- **Une série sur une fiche en `CONTENT_EXECUTION_MISMATCH`** est décomptée en
  `execution_uncertain_sets`. La preuve exacte exige `EXACT` et ce décompte nul (§19.5).

### 2.5 Risques

| Risque | Parade |
|---|---|
| Divergence silencieuse avec la notion de série faite du dépôt | garde de parité contre `_work_sets` |
| Le résolveur écrit en base sans le dire (`ensure_exercise`) | garde : aucune ligne créée, session propre après résolution d'un inconnu |
| Correspondance floue introduite plus tard | garde : variantes proches (mot manquant, faute) ⇒ `UNKNOWN_IDENTITY` |
| Un module servi se met à importer l'ombre | garde : aucun module `app/` hors `sci_*` n'importe `sci_identity` ou `sci_exposure` |
| L'ombre lit le recommandeur, TRAIN A ou l'environnement | garde d'imports par préfixe |
| Garde verte qui ne mord pas | chaque garde est plantée (défaut introduit, garde rouge) avant d'être tenue pour vraie |

## 3. Réalisé

### 3.1 Fichiers

| Fichier | Rôle |
|---|---|
| `app/services/sci_identity.py` | résolveur à quatre étapes, index des noms dérivé de l'EKB, refus des collisions entre identités distinctes |
| `app/services/sci_exposure.py` | lignes du registre (rôle brut, provenance, exécution incertaine), chargement lecture seule, agrégat sur 15 zones |
| `data/sci/legacy_name_ledger.json` | relevé figé des 107 noms canoniques et des 2 alias déclarés, **outil de test** |
| `tests/test_sci_identity.py`, `tests/test_sci_exposure.py` | 51 tests |
| `docs/strategy/Sx_SCI_V2_CATALOGUE_INTEGRATION_01_SPEC.md` | v3, trois corrections déclarées |

### 3.2 Ce que les gardes établissent

- **Résolution du corpus.** Chaque nom du produit se résout : gabarits et substituts, 69
  propriétés, 109 lignes de curation, 107 noms EKB et 2 alias.
- **Concordance des étapes 2 et 3** sur ce corpus, dans une base semée par la vraie graine
  d'identité.
- **Alias.** Toute résolution aboutit sur une fiche CANONICAL. G12 vérifié : un ancien
  « Curl poulie basse » compte comme le curl barre.
- **Pas de ressemblance.** Un mot manquant, une faute de frappe ou un préfixe d'un nom réel
  rendent `UNKNOWN_IDENTITY`, avec sa raison.
- **Lecture seule.** La résolution d'inconnus ne crée aucune ligne `exercises` ni
  `exercise_aliases`, et la session reste propre. La construction du registre n'écrit rien.
- **Renommage.** Chaque nom relevé se résout toujours vers sa fiche, tout nom EKB nouveau doit
  être relevé, et un renommage sans alias rend le nom relevé irrésoluble (défaut planté).
- **Parité.** `is_done_work_set` est épinglé contre `zone_exposure._work_sets`, `executed_name`
  contre `actual_exercise_name`.
- **Éligibilité.** Seules comptent les séances `completed`, hors `excluded_from_stats`,
  appartenant à l'utilisateur, avec un début inclusif et une fin exclusive.
- **Crédit.** Aucune ligne ne stocke de crédit. Le crédit vient de `sci-exposure-credit-v1` à la
  lecture : 1,0 / 0,5 / 0. UNKNOWN est décompté à part et met la zone en `MINIMUM`, jamais en 0.
  Une identité inconnue met les 15 zones en `MINIMUM`.
- **Exécution incertaine.** Une fiche en `CONTENT_EXECUTION_MISMATCH` produit des lignes
  incertaines, et `exact_evidence` passe alors à faux.
- **Isolation.** Aucun module du produit n'importe la couche scientifique ; la garde est prouvée
  sur les trois formes d'import. La couche n'importe ni le recommandeur, ni la mémoire de conseil,
  ni TRAIN A, ni l'exposition servie, ni la substitution, ni les routes.

### 3.3 Contre-preuves (mutations en mémoire, aucun fichier touché)

**9/9 défauts plantés détectés** :
- série faite sans `completed` ;
- échauffement compté ;
- nom prescrit au lieu du nom exécuté ;
- UNKNOWN compté comme zéro exact ;
- exécution incertaine ignorée ;
- résolveur qui écrit en base ;
- alias rendu comme candidat ;
- correspondance floue par préfixe ;
- identité inconnue sans effet sur les bornes.

**Ce que la contre-preuve a attrapé chez moi.** Au premier passage, « UNKNOWN compté comme zéro
exact » passait : les tests comparaient la borne à la **constante du module**
(`sx.BOUND_MINIMUM`). Une mutation qui échange les constantes modifie alors les deux membres de la
comparaison à la fois. Les tests comparent désormais aux **valeurs du contrat**, écrites en clair.

### 3.4 Vérifications

| Contrôle | Résultat |
|---|---|
| `check_scope.py` | **SHARED_CODE** (`sci_exposure` importe `sci_identity`) |
| Tests de la tranche | 51 passés |
| Full sweep local (`run_local_sweep.sh`, 365 fichiers, lancé parce que 54 gardes balaient tout `app/`) | **6 956 passés, 0 échec**, 1 sauté préexistant ; pic 1 827 Mo |
| Budget ruff | 264, valeur du canonique : **aucun avertissement ajouté** |
| Pré-scan Sonar (S9073, S5863, S5778, S5806) | aucune occurrence dans les quatre fichiers neufs |
| `check_spec_protocol` | OK |

### 3.5 Périmètre interdit respecté

Rien n'est servi, aucun module du produit n'appelle la couche. `muscle_scoring`, `zone_exposure`,
`set_contribution`, V3, TRAIN A et `equipment_model` sont intacts. Aucune migration, aucune
écriture, aucune UI, rien sur le N0.

**Verdict :** `Sb_SCI_V2_02` est construite et vérifiée en local. Le statut final dépend de la CI
réelle.
