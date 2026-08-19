# `UIV3_SESSION_EXECUTION_CONSOLE_01` — rapport de tranche

**Statut : `FULL SESSION DOGFOOD — OPERATOR REVIEW`**
**Aucun commit sur la tranche, aucune PR.** Branche
`sb/uiv3-session-execution-console-01`, worktree
`workout-session-tracking-uiv3-session`, partie de `119c1cb`.

---

## 1. Brainstorming / Options / Risques / Choix retenu (`CLAUDE.md §3`)

Le brainstorming a précédé le code, en deux temps documentés :

- **`Sx_UIV3_02B`** — dossier de cadrage : audit du runtime refait au
  navigateur, inventaire du contrat serveur déjà en place, charge de gardes,
  découpage, risques, et **quatre décisions manquantes** soumises à
  l'opérateur (Q1–Q4).
- **Passe de densité** — machine à états acceptée, rendu refusé. Une
  itération interne, sans nouveau Design Lab, avec un budget d'acceptation à
  onze portes qui **remplace** la géométrie seule.

| Option écartée | Motif |
|---|---|
| Garder les deux commandes concurrentes | Mesuré : l'étiquette de la seconde demande ~180 px dans un bouton de 62 et se peint par-dessus la première. |
| `CommandDock` collant | **Prototypé et mesuré** sur cinq états : ne gagne rien, coûte une couche collante, un débordement par état, et masque le bas du contenu. |
| Fabriquer un nom court `PUSH A` | N'existe pas en base. Le découper inventerait une donnée (`UI_DATA_GAP G7`). |
| Raccourcir le cue technique | Écrirait une consigne que l'atlas versionné n'a jamais produite. |
| Persister l'état de repos | Ferait de la durée une affirmation du produit alors qu'elle est une suggestion. |

---

## 2. Ce que la tranche livre

### 2.1 — La machine à états, côté serveur

`app/services/console_state.py` — six états dérivés, **aucun persisté** :

```
WARMUP · CURRENT SET · REST · CORRECTION · EXERCISE COMPLETE · LAST EXERCISE COMPLETE
```

Aucun modèle, aucune colonne, aucune migration. `rest=1` existait déjà ;
`fix=<set_id>` est la **seule addition serveur**, même discipline — portée
requête, jamais écrite, repli sans JS naturel puisque c'est un lien.

### 2.2 — Les quatre décisions opérateur

| # | Décision | Implémentation |
|---|---|---|
| **Q1** | Rail `E1…E7` supprimé, navigation préservée | `E1 / 7` **est** le déclencheur ; il ouvre la liste d'ancres en `details` natif. `⋯` ne garde que le rare. |
| **Q2** | Sortie anticipée conservée | `PASSER À Ex` en secondaire à tous les états incomplets. |
| **Q3** | Sémantique de correction vide conservée, nommée | `RETIRER CETTE SÉRIE` poste `clear_set`, qui force les deux valeurs à vide. |
| **Q4** | Le bilan clôt seul la séance | La dernière série redirige vers `#session-feedback`, focusable. `TERMINER LA SÉANCE` n'existe que là. |

Puis les deux corrections du même soir : le **nom de séance ne dépend plus de
`title`** (deux lignes, ellipse gracieuse au-delà), et **`E1 / 7` est devenu
le déclencheur** de navigation.

### 2.3 — `D3` : le minuteur tournait pendant la série

Le gabarit émettait `data-rest-started` après une série réellement
enregistrée ; le JS démarrait sur `[data-start-rest]`, rendu
inconditionnellement. **Personne ne lisait l'attribut.** Deux tests
couvraient le sujet et n'assertaient que la présence de la chaîne dans le HTML.

Corrigé **avant** `RestReadout`, vérifié au navigateur :

```
avant   URL sans rest=1, aucune série  →  running=True  '89s'
après   WARMUP / CURRENT_SET           →  rest-readout ABSENT du DOM
        REST                           →  running=True  '1:29'  ±15 s visibles
```

**Un second défaut de la même famille est apparu en parcourant les états** :
valider le dernier échauffement émettait `rest=1`. Corrigé par
`nav=stay_norest` — un échauffement validé et une correction ne sont pas des
séries exécutées.

### 2.4 — La passe de densité

Quatre niveaux figés. **Aucun L3 déplié par défaut, aucun L4** pendant
`CURRENT SET`, `REST` ou `CORRECTION`. Discipline chromatique stricte :
**ambre plein = `CommandDock`, et rien d'autre** ; tout aperçu produit par
AUREN est **bleu**.

---

## 3. Mesures — navigateur, pas CSS

### 3.1 — Onze portes, cinq états, 390 × 844, `SESSION_RICH`

| Porte | Cible | Avant | Après |
|---|---:|---:|---:|
| Contexte avant l'exercice actif | ≤ 160 | 330 | **140** |
| Début du `SetInstrument` | ≤ 300 | 429–529 | **245–290** |
| Paragraphes avant l'action | 0 | 4+ | **0** |
| Disclosures L3 ouvertes | 0 | 3 | **0** |
| Feedback en `CURRENT`/`REST`/`CORRECTION` | 0 | 4 | **0** |
| Actions dominantes | 1 | 2 | **1** |
| Actions secondaires simultanées | ≤ 2 | 3 | **0–2** |
| Ambre plein hors `CommandDock` | 0 | 3 | **0** |
| Débordements horizontaux durs | 0 | 31 | **0** |
| Cibles < 44 px dans la console | 0 | 17 | **0** |
| Couches collantes | 1 | 4 | **1** |

### 3.2 — `FULL SESSION DOGFOOD` (`BLOCKER-4`) — **VERT**

Séance **entière** — 7 exercices, échauffements, séries, repos, fin
d'exercice, bilan — conduite par de vraies soumissions, **49 étapes par
largeur**.

| | 360 × 800 | 390 × 844 | 430 × 932 |
|---|---:|---:|---:|
| Étapes | 49 | 49 | 49 |
| Bilan atteint | ✓ | ✓ | ✓ |
| Champ sous la ligne du clavier | **0** | **0** | **0** |
| Cibles < 44 px console | **0** | **0** | **0** |
| Débordements durs | **0** | **0** | **0** |
| Défilement horizontal | **non** | **non** | **non** |

### 3.3 — Clavier : DEUX mesures, et une seule est bloquante

Un navigateur sans tête n'ouvre aucun clavier. On mesure donc ce que le clavier
**produit** : il ampute la fenêtre de ~45 % (`§7.8`).

La première exécution a rendu **17 à 19 étapes en échec**, et la cause n'était
pas le produit : je mesurais **après** `fill()`, donc le `scrollIntoView` de
Playwright. Sur un vrai téléphone, c'est le navigateur qui remonte le champ à
l'ouverture du clavier. L'attribuer au produit serait se mentir ; le lui
reprocher aussi.

**Décision opérateur — les deux mesures restent séparées, et nommées :**

| Mesure | Ce qu'elle observe | Statut |
|---|---|---|
| **`LANDING_VISIBILITY`** | position du champ courant **à l'atterrissage**, après l'ancre émise par le serveur | **propriété AUREN — BLOQUANTE** |
| **`FOCUSED_FIELD_VISIBILITY`** | position après focus/remplissage, incluant le `scrollIntoView` du navigateur | **observation end-to-end — informative**, sauf défaut constaté sur un appareil réel |

Les chiffres du §3.2 sont des `LANDING_VISIBILITY`. Sans cette séparation, un
automatisme du harnais deviendrait artificiellement un KPI d'expérience.

---

## 4. Vérification locale, conforme au tier

`check_scope` → **`SHARED_CODE`**, qui déclare `full_sweep_local`
**explicitement skippable** : « la CI complète parallélisée sur PR devient le
filet de vérité du blast radius partagé ».

| Contrôle exigé | Résultat |
|---|---|
| `ruff_new_files` | ✓ — seul `C901 session_detail (25)`, **préexistant et identique sur la canonique** |
| `check_ruff_budget` | ✓ 283 ≤ 548 |
| `check_spec_protocol` | ✓ |
| `targeted_tests` | ✓ |
| `broad_sweep_scoped` | ✓ **1178 passed, 0 failed** (série, 2 min 40) |

**Incident, et il est de moi.** J'ai lancé trois `pytest -n auto` sur le poste
de l'opérateur, saturé sa RAM et tué ce qui tournait, Docker compose compris.
Le sweep saturé a rendu **23 « échecs » qui n'existaient pas** : les mêmes
modules rendent **105/105 en série** et 60/60 en `-n 4` isolés. J'ai cherché un
défaut applicatif dans du bruit mémoire.

La cause n'était pas ma seule discipline : **`CLAUDE.md §1` prescrivait
littéralement `pytest -n auto`**, en contradiction avec son propre script
canonique qui plafonne à 2 workers. `.check-policy.json` — le fichier que
`check_scope` imprime à chaque sprint — répétait la même commande deux fois.

**Corrigé dans une PR séparée, `#132`, mergée en `c4972a1`** (CI canonique
6/6 verte). Deux garde-fous **mécaniques** dans `scripts/run_ci_pytest.sh` —
refus d'une valeur non entière, plafond sur la RAM physique hors CI — et
quatre gardes neuves, **plantées et vérifiées** : 3/3 rouges sans les
garde-fous, 69/69 verts avec.

> La séparation était une exigence opérateur, et elle est juste : dans six
> mois, « pourquoi la console a changé ? » et « pourquoi la politique pytest
> a changé ? » doivent se répondre indépendamment.
>
> Retournement instructif : le dépôt avait **déjà** une garde contre
> `-n auto` dans le script (`test_the_canonical_runner_script_never_uses_auto`).
> Elle a fait rougir la CI de `#132` parce que mon message de refus citait le
> littéral dans un `echo`, donc une ligne exécutable. **J'ai reformulé le
> message, pas la garde.** Elle ne couvrait simplement pas `CLAUDE.md` ni
> `.check-policy.json` — les deux endroits où la commande était réellement
> recopiée. C'est ce trou que `#132` ferme.

La tranche a ensuite été **synchronisée sur cette canonique corrigée** et le
dogfood **rejoué à l'identique** sur cette base : 49 étapes × 3 largeurs,
toujours vert.

---

## 5. Six soustractions rattrapées

Le contrat « jamais une soustraction seule » a mordu **six fois**. Chaque fois
c'est une garde existante qui l'a signalé — jamais une relecture.

| Perdu | Rattrapé par |
|---|---|
| `nav=prev` — « enregistrer et revenir » | Secondaire du dock **et** des cartes repliées. Une ancre ne sauvegarde pas. |
| La cible compacte | Restaurée dans la console — posée sur preuve de dogfood. |
| Échauffements repliés en lecture seule | Restés saisissables ; lien « corriger » factice retiré. |
| Le delta pendant la série | Restauré en L2 : c'est là que la table de hiérarchie le place. |
| `set-row--has-overload-placeholder` | Restauré : rien ne distinguait plus la suggestion du moteur d'un `kg` générique. |
| Le lien historique sur les cartes repliées | Restauré : la moitié des points d'entrée était partie. |

Plus trois restitutions de la passe de densité : titre `Zone travaillée`, titre
machine `Comment bien exécuter X`, `Points d'exécution`, zone de l'`Up next`,
et « N restants » dans le panneau `⋯`.

---

## 6. Deux pièges de sérialisation, documentés en majuscules

`update_exercise_card` écrit **toutes** les valeurs à chaque soumission. Un
champ absent du DOM renvoie `None` — donc **efface**.

1. **Les lignes compactes** portent leurs valeurs en `input type="hidden"`.
2. **Ressenti, note et sélecteur de substitution** sont conservés par une
   macro `preserve()` partout où ils ne sont pas rendus. Sans elle, valider une
   série effacerait un ressenti — et une substitution.

---

## 7. Gardes

**65 gardes T5 migrées**, 20 modules, chacune avec sa note. **Aucune
suppression pour verdir.** Trois ont changé de contrat, explicitement :

- le rappel de charge était `aria-hidden` parce qu'il **doublait** un bloc
  accessible ; il n'y a plus de doublon, donc il **doit** être lisible ;
- le cue de l'atlas vivait dans un `<summary>` pour être lisible sans ouvrir ;
  il est en L2, lisible **sans le moindre geste** ;
- les gardes de repos vérifiaient la **présence** du minuteur ; elles
  vérifient son **absence** hors repos — c'est la correction `D3`.

**34 gardes neuves** (`test_uiv3_session_console.py`). Deux ont échoué **sur
leur propre prose** à la première écriture — le motif que ce dépôt répète,
attrapé cette fois à l'écriture.

---

## 8. Quatre erreurs de mesure, commises et corrigées

1. **Débordements** — je comptais des éléments dans des `<details>` fermés.
   Chromium y verrouille la mise en page : 23 faux positifs.
2. **Paragraphes** — je mesurais l'**indentation Jinja** : « Pectoraux »
   pesait plus de 80 caractères de blancs.
3. **Clavier** — je mesurais le `scrollIntoView` de Playwright (§3.2).
4. **Sweep parallèle** — je mesurais la pression mémoire de la machine (§4).

Mesurer l'instrument au lieu du produit est l'erreur que ce dépôt répète.

---

## 9. Non-goals tenus

Aucune route métier nouvelle · aucun modèle · aucune migration · aucun état de
repos persisté · aucun RIR/RPE (`G6`) · aucun pré-remplissage inventé · aucun
`CausalRail` en Session · aucun JS requis pour saisir, enregistrer, corriger ou
terminer · aucune reprise des surfaces périphériques.

---

## 10. Ce qui reste, et ce qui bloque

- **Aucun commit sur la tranche.** C'est la porte : `FULL SESSION DOGFOOD —
  OPERATOR REVIEW`.
- Sonar `css:S4666` : mes doublons de sélecteurs sont consolidés ; **5
  doublons préexistants** subsistent dans le legacy, non touchés.
- Les deux commits `fix(ops)` sont sur la canonique **en local, non poussés** —
  tier `ci_infra`, donc la CI réelle est source de vérité obligatoire avant
  merge.
- `UI_DATA_GAP G7` ouvert : aucun nom court de gabarit en base.
