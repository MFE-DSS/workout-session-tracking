# `Sx_UIV3_02B` — Console de séance : dossier de cadrage de construction

**Statut : `READY FOR OPERATOR REVIEW`** · 2026-08-19
**Tranche visée** : `UIV3_SESSION_EXECUTION_CONSOLE_01` (phase 2)
**Dépend de** `Sx_UIV3_02` (spec approuvée) et `Sx_UIV3_00` (contrat de socle),
qui prévalent en cas de conflit.

Ce document ne remplace pas la spec. Il apporte ce que la spec n'avait pas :
un **audit du runtime refait aujourd'hui**, l'**inventaire du contrat serveur
réellement en place**, la **charge de gardes** à migrer, et le **découpage de
construction**. Il corrige aussi deux chiffres de la spec qui ne se
reproduisent pas.

---

## 0. Ce que la mesure d'aujourd'hui change

Mesuré au navigateur — Chromium, DSF 2, copie de la base de dev en bac à
sable, séance `push-a` réelle, exercice E1 *Incline Smith Press*, connexion
unique réutilisée et assertion « la page mesurée EST la page de séance » à
chaque relevé.

### 0.1 — Le chiffre qui compte n'est pas celui qu'on citait

`Sx_UIV3_02 §1` retient **161 cibles sous 44 px**. Ce chiffre compte les
`input[type=radio]` de **1 × 1 px** cachés derrière chaque
`label.segmented__option` — or **ce n'est pas le radio qu'on touche, c'est le
label**. Les compter gonfle le budget et le rend inexploitable comme cible.

Décompte honnête, contrôles réellement tactiles uniquement :

| Cible | Occurrences | Dimension |
|---|---:|---|
| `label.segmented__option` | **27** | 95–105 × **32** |
| `summary` (disclosures) | **12** | 292–324 × 17–28 |
| `textarea` | **7** | 292–306 × **39** |
| `a.exercise-card__code--link` | **7** | 145 × **14** |
| `.btn` (barre d'action) | **2** | 127/186 × **38** |
| divers (`topbar`, `back`, pied) | 14 | — |
| **Total** | **69** | |

**69, pas 161.** Toutes les violations sont des violations de **hauteur** ;
aucune de largeur. C'est une bien meilleure nouvelle pour le coût de la
tranche, et une bien pire nouvelle pour la crédibilité d'un budget qu'on
n'avait pas recompté.

### 0.2 — La géométrie ne reproduit pas non plus

| Mesure | Spec `§1` (18/08) | Mesuré (19/08) |
|---|---:|---:|
| y de la série courante @390 | 843 | **644** (É1 à faire) · **467** (S1 courante) |
| Document @390 | 3 651 | **2 946** |
| Ordre action / série | action **avant** la série | action **après**, 91 à 618 px plus bas |

**Cause : le fixture de mesure est plus pauvre qu'un vrai utilisateur.**
`baseline_local` n'a pas d'historique exploitable, donc **8 blocs optionnels
sur 13 ne sont pas rendus** :

> absents — Guidance de progression (hint de surcharge) · Hints `Sb_08` ·
> Dernière fois · Delta · rappel de charge sur la ligne · Adapter l'exercice ·
> Up next · chip de briefing
>
> rendus — Référence précédente · panneau machine · Cues techniques ·
> Zone travaillée · Intention

**Les chiffres ci-dessous sont donc un plancher, pas une moyenne.** La page
d'un utilisateur avec de l'historique est plus haute. Aucun budget de la
tranche ne doit être calé sur ce fixture sans en tenir compte — c'est
directement un point de sortie du dogfood.

### 0.3 — Relevé, trois largeurs, état « É1 à faire »

| | 360 × 800 | 390 × 844 | 430 × 932 |
|---|---:|---:|---:|
| Document | 3 030 (3,79 écrans) | 2 946 (3,49) | 2 862 (3,07) |
| y série courante | 656 | 644 | 644 |
| y commande dominante | 703 | 747 | 835 |
| Débordements **durs** | 32 | **31** | 29 |
| Cibles < 44 px | 69 | **69** | 69 |

*Débordement dur* = `scrollWidth > clientWidth` **et** `overflow-x: visible`
**et** pas d'ellipse. Une ellipse gracieuse et un défileur volontaire ne sont
pas comptés — c'est l'erreur commise puis corrigée en `D5`.

---

## 1. Sept défauts mesurés, dont deux inconnus de la spec

### D1 — La barre de saut **recouvre le titre de la séance** ★ nouveau

Trois couches collantes se partagent la **même bande de 109 px** en haut de
l'écran, et elles se recouvrent **en z, pas en y** :

| Couche | `position` | Bande occupée |
|---|---|---|
| `.topbar` | sticky | 0 → 66 |
| `.session-focus__sticky-header` | sticky | 0 → 100 |
| `.session-focus__sticky-jump` | sticky | 56 → 109 |
| `.session-focus__sticky-cta` | sticky | 98 px, dans la carte active |

Résultat visible dès qu'on défile : **`Push A — Pecs épa…` et le badge
`En cours` sont coupés en deux** par la bande `E1 … E7`. Le titre de la séance
est illisible pendant toute l'exécution.

`Sx_UIV3_02 §7.9` ne supprime que **la barre d'action** collante. Elle ne dit
rien des **trois autres**. C'est un trou de spec, pas un détail
d'implémentation — voir la question **Q1**.

*Correction d'un chiffre que j'ai d'abord annoncé faux* : la bande haute coûte
**109 px**, pas 263. Les trois couches se superposent au lieu de s'empiler.

### D2 — La commande principale déborde de son propre bouton

`Enregistrer et passer à E2` est rendu dans un bouton de **62 px de large**.
L'étiquette en demande ~180. Le texte **se peint par-dessus** le bouton voisin
`Enregistrer la série` et par-dessus le contenu situé derrière la barre.

Les boîtes ne se chevauchent pas (77–275 et 283–345) : **c'est le texte qui
déborde**, ce qui est pire, parce qu'aucune règle de mise en page ne le
rattrape.

C'est la démonstration visuelle de la thèse de `§4` : *la coexistence des deux
commandes est un artefact de réparation.* Elle ne tient littéralement pas dans
la largeur d'un téléphone.

### D3 — Le minuteur de repos tourne **pendant la série** ★ nouveau

Le gabarit émet `data-rest-started="1"` **uniquement** quand le serveur a posé
`rest=1`, c'est-à-dire après une série réellement enregistrée. C'est le
contrat écrit dans `_partials/rest_timer.html`, et il est correct.

**Aucun code ne lit cet attribut.** `session_focus.js:81` démarre le compte à
rebours sur tout élément portant `[data-start-rest]` — attribut rendu
**inconditionnellement**.

Mesuré, sur une URL **sans** `rest=1` et sans qu'aucune série ait été
enregistrée :

```
REPOS  affichage='89s'   running=True   attr-started=False
```

Deux tests couvrent le sujet — `test_session_set_action.py:236` et `:250` —
et **tous deux n'assertent que la présence ou l'absence de la chaîne dans le
HTML**. Aucun n'exerce le comportement. Le contrat est écrit, publié, gardé,
et inopérant.

C'est la **douzième occurrence** du même motif dans ce dépôt : *une garde qui
vérifie que le HTML dit la bonne chose, alors que le comportement qu'elle
prétend protéger n'existe pas.* Le précédent immédiat est `zone_recovery`,
présent trois fois en commentaire Jinja et zéro fois dans le balisage vivant.

**Ce n'est pas du polissage d'UI : c'est un défaut de comportement vivant.**
Il entre dans le périmètre de la phase 2 via `RestReadout`.

### D4 — `Skip rest` est en anglais

Au milieu d'une interface entièrement française, exactement le motif que
l'accroche de connexion vient de faire trancher : *un vestige de maquette
anglophone, pas une signature*. `Sx_UIV3_02 §4` fixe déjà le libellé français —
`PASSER LE REPOS`.

### D5 — La même progression est affirmée quatre fois

`1/3` apparaît, sur un seul écran :

`.exercise-card__progress` · `.session-focus__console-progress-value` ·
`.card__actions__recap` · le chip `E1` de la barre de saut.

Trois dans la carte active, une dans la bande. Aucune n'ajoute d'information.

### D6 — La série à venir est aussi grosse que la série courante

`SÉRIE #2` (courante) et `SÉRIE #3` (à venir) sont rendues avec **la même
hauteur, les mêmes champs, la même typographie**, distinguées par un liseré
ambre discret. L'amendement B exige : *passé compact · courante développée ·
futur compact.* Aujourd'hui, les trois sont identiques.

### D7 — L'absence de référence occupe une ligne pour ne rien dire

`RÉFÉRENCE PRÉCÉDENTE — Non disponible`. `§7.12` tranche déjà :
**`PREMIÈRE FOIS`**, une seule fois, dans le bloc référence.

---

## 2. Contrat serveur — ce qui existe déjà, et c'est beaucoup

Point le plus important de ce dossier pour l'estimation : **la machine à états
de `§4` est presque entièrement dérivable de ce qui tourne aujourd'hui.**

| Élément | État | Où |
|---|---|---|
| `nav=stay` — enregistrer et rester | **existe** | `sessions.py:788` |
| Ancrage sur la **prochaine série non complétée** | **existe** | `stay_redirect_target()`, `:698-703` |
| `rest=1` — signal de départ **émis par le serveur** | **existe** | `:703` |
| `rest_active` exposé au gabarit | **existe** | `:468` |
| `nav=next` / `nav=prev` | **existe** | `:793-824` |
| `completed` dérivé de la présence de `weight` **ou** `reps` | **existe** | `:756` |
| Repli intégral sans JS | **existe** | `details/summary` natifs |
| Signal d'état `CORRECTION` | **manque** | — |

`UI_DATA_GAP G4` — « l'état `REST` n'est pas un état serveur » — est déclaré
**clos par la spec**. Il est en réalité **déjà implémenté dans le runtime**,
exactement sous la forme prescrite : un signal à portée de requête, jamais
persisté. La spec ignorait que le dépôt l'avait devancée.

### 2.1 — Dérivation complète des six états

Aucun modèle, aucune migration, aucune colonne. Un seul paramètre de requête
nouveau.

| État | Dérivation |
|---|---|
| `WARMUP` | il reste un `warmup` non complété |
| `CURRENT SET` | plus de `warmup` en attente · il reste un `work` non complété · pas de signal de repos |
| `REST` | `rest=1` **et** il reste un `work` non complété |
| `CORRECTION` | **`fix=<set_id>`** — paramètre de requête à créer |
| `EXERCISE COMPLETE` | `work_done == work_total` **et** un exercice suivant existe |
| `LAST EXERCISE COMPLETE` | `work_done == work_total` **et** aucun exercice suivant |

`fix=<set_id>` respecte la même discipline que `rest=1` : **portée requête,
rien de persisté, repli sans JS naturel** (c'est un lien `href`). C'est la
seule addition serveur de toute la tranche.

---

## 3. La charge réelle : le poids du legacy

| Fichier | Lignes |
|---|---:|
| `_partials/exercise_card.html` | **1 008** |
| `static/css/session_focus.css` | **1 968** |
| `templates/session_detail.html` | 221 |
| `static/js/session_focus.js` | 95 |

`exercise_card.html` porte les sédiments de **quinze tranches** identifiables
dans ses seuls commentaires (`Sb_UI_04.3`, `Sb_29.1`, `Sb_30.3`, `Sb_30.4`,
`Sb_08`, `Sb_22a`, `Sb_SESSION_UX_01.2/.2b/.3/.4`, `Sb_UIV2_SESSION_FOCUS_02`,
`Sb_SESSION_SET_ACTION_01`, `Sb_SUBSTITUTION_COCKPIT_01`,
`Sb_ATLAS_TECHNICAL_GUARDS_01`, `Sx_UI_06 D1/D2/D3`). Plusieurs de ces
commentaires **documentent des déplacements successifs du même bloc**.

C'est le vrai coût de la tranche — pas le CSS.

### 3.1 — Gardes de séance

**25 modules mesurés, 389 gardes.** Les plus exposés :

| Module | Gardes | Tier dominant |
|---|---:|---|
| `test_session_focus_cockpit` | 34 | T3/T4 |
| `test_session_focus_logging_console` | 32 | T3/T4 |
| `test_session_focus_worked_area` | 30 | T1/T4 |
| `test_ui_session_choices` | 22 | T3 |
| `test_session_focus_layout` | 21 | **T5** |
| `test_session_focus_rest_timer` | 20 | T3 → **à requalifier** (D3) |
| `test_session_focus_navigation` | 19 | T1 |
| `test_session_focus_terminal` | 19 | T4 |
| `test_session_ux_alternatives_order` | 17 | T5 |
| `test_session_set_action` | 16 | T1 + 2 gardes creuses (D3) |
| `test_session_focus_sticky_cta` | **16** | **T5 — remplaçable** (`§2`) |
| `test_session_ux_cues_density` | 16 | T4 |
| `test_session_ux_console_priority` | 12 | T4 |

**Neuf modules épinglent les couches collantes** par leur nom de classe. Le
registre de migration (`AUREN_UIUX_V3_GUARD_MIGRATION_REGISTER`) doit être
rempli **avant** la première ligne de code — c'est la leçon de la phase 1, où
trois CI rouges sur quatre venaient de gardes non migrées.

---

## 4. Découpage de construction

**Une seule tranche, un seul PR, une seule revue humaine** — le modèle validé
en phase 1. Les étapes ci-dessous sont du **séquencement interne**, pas des
livraisons séparées : `CLAUDE.md §5.3` interdit qu'une soustraction parte
seule, et retirer la barre collante sans la commande contextuelle serait
exactement cela.

L'ordre suit la **centralité** (`§5.5`), pas la facilité.

| # | Étape | Livre | Défauts fermés |
|---|---|---|---|
| **1** | **Dérivation d'état** — `_console_state()` côté routeur + paramètre `fix` | aucun changement visuel ; testable en pur Python | — |
| **2** | **`CommandDock`** — une commande contextuelle par état, `:active` obligatoire ; les deux boutons concurrents et la barre collante disparaissent **ensemble** | la commande dominante | **D2** |
| **3** | **`SetInstrument` + `DeltaReadout`** — trois positions temporelles, **une seule** surface de saisie, référence juste au-dessus | la série courante au-dessus de la ligne de flottaison | **D6, D7** |
| **4** | **`RestReadout`** — l'état `REST` honore enfin `data-rest-started` ; `−15 s / PASSER LE REPOS / +15 s` ; français | le repos | **D3, D4** |
| **5** | **Dégraissage de la bande haute** — trois couches collantes → une | le titre de séance redevient lisible | **D1** |
| **6** | **Relégation en L3** — `Adapter` en popover ancré, cues, zone travaillée, Up next ; déduplication de la progression | la densité | **D5** |
| **7** | **44 px sur la console** + migration des gardes T5 | l'accessibilité de la console | — |

**Hors périmètre, explicitement** : les 27 `segmented__option` à 32 px
appartiennent aux formulaires de ressenti, pas à la console — ils reviennent à
la phase 3 `UIV3_TARGETS_44_01`, comme décidé.

### 4.1 — Porte de sortie

`BLOCKER-4` est **bloquant** : la console n'est pas figée avant qu'une
**séance complète soit réellement exécutée** — sept exercices, échauffements,
séries de travail, une correction, une substitution, la clôture — sur
**360 / 390 / 430**, et validée à l'œil par l'opérateur.

Motif : les 69 cibles hors norme et les 31 débordements prouvent que la
qualité de cette surface **ne peut plus être inférée du CSS**.

Exposition visuelle rendue **avant tout commit** (`CLAUDE.md §5.1`), avec les
alternatives quand il y en a. L'opérateur tranche.

---

## 5. Risques

| Risque | Pourquoi il est réel ici | Parade |
|---|---|---|
| **`check_scope` sous-classe la tranche** | `.set-row`, `.card__actions`, `.btn`, `.segmented` sont partagés avec `app.css`. Le précédent `exercise_properties` a été classé `ISOLATED` **à tort** pour la même raison. | Traiter d'office en `shared_code` ; balayage large obligatoire ; full sweep si le moindre doute de rayon. |
| **389 gardes, 9 modules sur le collant** | Trois des quatre CI rouges de la phase 1 venaient de gardes non migrées. | Registre de migration rempli **avant** le code, pas après. |
| **Plafond mémoire du runner CI** | La suite demande ~16,6 Go pour 15,99 Go de machine ; fuite ~4,4 Mo/test. | Vérifier `[ci-pytest] workers=N` avant de croire un run vert. |
| **Faux échecs sous xdist** | Purge conftest : `ModuleNotFoundError` et fausse identité d'énumération entre deux générations — invisible hors full sweep. | Ne pas diagnostiquer un échec xdist sans le rejouer en série. |
| **Sonar `S1192` / `S3776`** | Un gabarit neuf et une fonction de dérivation à six branches les attirent tous les deux. | Pré-scan `app/` **et** `tests/` avant push ; extraire tôt. |
| **Le fixture de mesure ment par omission** | 8 blocs sur 13 absents (`§0.2`). | Le dogfood se fait sur un compte **avec historique**, pas sur `baseline_local`. |

---

## 6. Quatre décisions qui manquent

Ces points ne sont pas tranchés par `Sx_UIV3_02`, et aucun défaut ne permet de
les déduire. Ils ne bloquent pas l'étape 1, mais bloquent l'étape 2.

### Q1 — Que devient la bande `E1 … E7` ?

Trois couches collantes, 109 px, et le titre de séance recouvert. La spec ne
supprime que la barre d'action. Options :

- **a** — la bande de saut reste collante, le header de séance ne l'est plus ;
- **b** — la bande de saut cesse d'être collante et vit en tête de page ;
- **c** — la bande fusionne dans le `CommandDock` (l'exercice courant y est
  déjà nommé par la commande `CONTINUER → E2`).

*Penchant* : **c**. Une bande de navigation permanente est un aveu que la page
est trop longue — et la tranche existe précisément pour qu'elle ne le soit
plus. Mais c'est la soustraction la plus visible de la phase, donc c'est à toi.

### Q2 — Peut-on encore quitter un exercice sans l'avoir fini ?

Aujourd'hui `nav=next` le permet à tout moment. Dans la table de `§4`,
`CONTINUER → Ex` n'apparaît qu'à l'état `EXERCISE COMPLETE`. Si la commande
dominante est la **seule** sortie, on **retire une capacité existante** — donc
une soustraction, interdite seule.

Faut-il conserver une sortie d'exercice en secondaire à tous les états
(« passer à E2 »), ou l'exercice devient-il un passage obligé ?

### Q3 — Une correction qui vide les deux champs, c'est quoi ?

`completed` est dérivé de la **présence** de `weight` ou `reps`. Donc
`ENREGISTRER LA CORRECTION` avec deux champs vidés **dé-complète** la série.

Est-ce le comportement voulu — « je m'étais trompé, cette série n'a pas eu
lieu » — ou faut-il refuser une correction vide ? Le premier est le
comportement actuel et il est défendable ; il n'est simplement **écrit nulle
part**.

### Q4 — Où mène `TERMINER LA SÉANCE` ?

Le formulaire de bilan (`#session-feedback` : concentration, énergie, poids,
note, cardio) fait une centaine de lignes et vit après les sept cartes.
`LAST EXERCISE COMPLETE → TERMINER LA SÉANCE` y conduit-il, ou termine-t-il
directement la séance en laissant le bilan optionnel ?

---

## Non-goals

Repris de `Sx_UIV3_02` et **inchangés** : aucune route métier nouvelle, aucun
modèle, aucune migration · aucun état de repos persisté · aucun RIR/RPE par
série (`G6`, bloqué) · aucun pré-remplissage inventé · aucun `CausalRail` en
Session · aucun JS requis pour saisir, enregistrer, corriger ou terminer.

Ajouts propres à ce dossier :

- **Aucun `rest_target_seconds` par exercice** — ce serait une prescription,
  donc une feature métier, pas un glissement UI.
- **Aucune correction des 27 `segmented__option`** — phase 3.
- **Aucune reprise des surfaces périphériques** (`/progress`, `/dashboard`) —
  phase 4, délibérément différée.
