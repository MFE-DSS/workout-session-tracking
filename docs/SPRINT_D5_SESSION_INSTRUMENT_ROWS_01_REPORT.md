# `D5_SESSION_INSTRUMENT_ROWS_01` — la ligne de série devient un instrument

**Base** : `9b41fa3` · **Tier `check_scope`** : `SHARED_CODE`
**Première tranche livrée sous `CLAUDE.md §5`** (contrat de livraison UI).

---

## 1. Le défaut, mesuré

La page `/sessions/{id}` — celle où l'utilisateur passe une heure entière, sur
un téléphone — était **cassée à 390 px**. Elle l'était depuis longtemps, et
**aucune des 4 898 gardes du dépôt ne l'a vue** : elles lisent toutes du HTML,
et le défaut n'était pas dans le HTML. Il était dans le rapport entre une piste
de grille de 40 px et un contenu de 101 px.

Mesure : `scrollWidth − clientWidth` sur chaque élément, dans un Chromium à
390 × 844.

| Catégorie | Avant | Après |
|---|---:|---:|
| Débordement **dur** (le texte déborde ou se superpose) | **31** | **0** |
| Troncature **gracieuse** (ellipse) | **7** | **0** |
| Défilement horizontal de page | non | non |

### Ce que ça donnait à l'écran

- **`Série #1 actif`** — 101 px de contenu dans une piste de 40 px, sans
  `overflow` déclaré : le débordement était **visible**, et le chiffre de série
  **passait sous le champ kg**. On ne pouvait pas savoir quelle série on
  remplissait.
- **`Enregistrer et passer à E2`** — comprimé à 60 px par son voisin, le
  libellé **s'imprimait par-dessus** le bouton « Enregistrer la série ». Les
  deux actions de la ligne étaient illisibles **en même temps**.
- **`Push A — Pecs épaisseur + Delts + Triceps`** — 292 px sur une piste de
  233, réduit par ellipse à **« Push A — Pecs épa… »**.

### Deux corrections à ma propre annonce

J'avais d'abord rapporté « 38 textes rognés ». Le décompte mélangeait deux
mécanismes distincts, et je l'ai corrigé avant d'écrire une ligne de code :

1. **7 sur 38 étaient des ellipses volontaires**, pas des défauts de structure.
2. **Les 31 autres ne « rognaient » pas** — elles débordaient en `overflow:
   visible`, donc se **superposaient** au contenu voisin. C'est pire que
   couper : deux textes lisibles séparément deviennent illisibles ensemble.
3. La barre `E1…E7` que j'avais signalée est un **défilement horizontal
   volontaire**. Faux positif — non touchée.

---

## 2. Brainstorming / Options / Risques / Choix (`CLAUDE.md §3`)

Les trois options ont été **rendues et exposées à l'opérateur** avant décision
(`§5.1`). Il a tranché **B**.

**Option A — réparation minimale.** Élargir les colonnes, laisser respirer.
Rapide et sûr. Rejetée : la page reste un mur de cartes, et la largeur gagnée
serait reprise au premier libellé plus long.

**Option B — retenue : la ligne devient un instrument.** Le libellé cesse
d'être une phrase (`Série #1` → `S1`), la place passe aux valeurs. Le rognage
est réglé **par construction** — un code de deux caractères ne peut pas
déborder — et non par élargissement.

**Option C — un exercice à la fois.** Le plus proche d'un cockpit, et de loin
le plus gros chantier. Différée ; **B est construit pour y mener** (la ligne est
déjà un objet autonome à trois zones : code, valeurs, annexe).

**Risque principal** : réduire un libellé, c'est retirer de l'information. Il
est neutralisé par la règle `§5.3` — rien ne part sans remplacement, et deux
tests le pinnent (`test_what_left_the_narrow_column_lives_in_the_annex`,
`test_the_active_marker_is_visual_and_still_named`).

---

## 3. Ce qui est construit

### La ligne

```
avant   [Série #1 actif ····· débordant] [kg] [reps]
après   [S1 ●]  [kg]  [reps]
        └─ annexe pleine largeur : technique · rappel de charge
```

- `grid-template-columns: 40px 1fr auto` → **`auto 1fr auto`**. La piste ne
  peut plus être plus petite que son contenu.
- Le mot **« actif » devient un point ambre** — substitution, pas soustraction :
  `role="img"` + `aria-label="Série active"` conservent le nom accessible.
- **L'annexe** reçoit ce que la piste étroite ne peut pas porter (technique,
  rappel de charge). `grid-column: 1 / -1` : elle occupe la ligne entière, donc
  rien n'y débordera jamais, quelle que soit la longueur future. Elle **n'est
  pas rendue si elle est vide**.

### L'action

`Enregistrer et passer à E2` → **`Valider · E2`** · `Enregistrer la série` →
**`Valider`**. Même verbe pour les deux issues, la **destination** porte
l'information.

Deux corrections structurelles derrière le libellé :

- `flex-wrap: wrap` sur la ligne d'action — le chevauchement devient
  **impossible par construction**, quelle que soit la longueur future.
- `flex: 1` → **`flex: 1 0 auto`** sur le CTA primaire. `flex: 1` implique
  `flex-basis: 0`, ce qui faisait du bouton principal le **premier candidat au
  rétrécissement** — l'inverse exact de son rang.

### Le titre

Ellipse sur une ligne → **trois lignes**, coupure aux mots. Trois et non deux,
**mesuré** : à 24 px sur 233 px, deux lignes s'arrêtaient encore à
« … + Delts… ».

Et un défaut découvert en le faisant : `.page-title` est **centré globalement**.
Invisible tant que le titre tenait en une ligne `nowrap` ; dès qu'il en occupe
trois, il se centrait au milieu d'un en-tête entièrement aligné à gauche.
Corrigé **dans la portée séance seulement**.

### La puce d'exercice

`3×12-20 RP · première fois` → **`3×12-20 RP`**. La queue débordait et l'ellipse
la mangeait à moitié. **Ce n'est pas une perte** : « première fois » est déjà
dit en entier par le bloc « Référence précédente : Non disponible » de la même
carte. La puce cessait de payer sa largeur pour un doublon.

Quand il y a une **charge réelle**, elle reste — c'est l'information qui vaut la
place. Un test dédié empêche que la suppression du cas vide devienne, plus tard,
la suppression du segment entier.

---

## 4. Relecture du relevé de décisions (`CLAUDE.md §5.2`)

### `DESIGN_DECISIONS_UIV2_SURFACES.md`

| | Décision | Verdict |
|---|---|---|
| **Q1** | connexion — écran d'identité sobre | **non concernée** |
| **Q2** | accueil — barres de récupération | **non concernée** |
| **Q3** | état du jour replié | **non concernée** |
| **Q4** | **la ligne devient un instrument** | **respectée** — objet de la tranche |
| **Q5** | trois rangs de surface | **non concernée** — aucun conteneur ajouté ni retiré ; l'annexe est un rang 3 (sans conteneur), donc cohérente par anticipation |
| — | tokens bleus | **non concernée** — aucune couleur introduite ; le point actif réutilise `--color-accent` (ambre existant) |

### `DESIGN_DECISIONS_HOME_UIV2.md`

| | Décision | Verdict |
|---|---|---|
| **D1** | contrat d'interactivité hybride | **respectée** — `Valider · E2` est un rang 1 (fond ambre plein, ≥ 44 px) ; `Valider` un rang 2 (bordure discrète, casse normale). Aucune étiquette n'a reçu de bordure ni de surface tapable. `S1` / `É1` sont des étiquettes : ni cadre, ni cible tactile |
| **D2** | badge d'origine | **non concernée** — accueil |
| **D3** | sémantique des couleurs | **respectée** — ambre = action / actif. Le point de série active est ambre, donc conforme au sens déclaré. Aucun bleu ici : rien sur cette ligne n'est « produit par le système » |
| **D4** | suppressions accueil | **non concernée** |
| **D5** | **descriptif → visuel** | **respectée** — c'est la tranche. Trois substitutions textuelles → visuelles : le mot « actif » → point ; les phrases de libellé → codes ; le verbe répété → destination |
| **D6** | cycle piloté par la récupération | **non concernée** |
| **D7** | régularité sans streak | **non concernée** |
| **D8** | onglet Progression | **non concernée** |
| **D9** | aucune anticipation au-delà de la séance proposée | **respectée** — `Valider · E2` nomme l'exercice **suivant dans la séance en cours**, pas une séance future. D9 interdit d'annoncer la séance N+2, pas de nommer la destination d'un bouton |

**Aucune décision violée.**

---

## 5. Le libellé qui mentait, attrapé par une garde

Ma première rédaction donnait au CTA primaire le `title` **« Enregistrer la
série et passer à E2 »**.

`test_cta_copy_does_not_claim_a_set_level_action` est tombé, et il avait
raison : ce bouton poste `nav=next` et fait avancer **l'exercice entier**.
Revendiquer une action de série l'aurait fait mentir. Le `title` dit désormais
« Enregistrer et passer à E2 » — la formulation honnête d'origine.

C'est la garde faisant exactement ce pour quoi elle a été écrite, contre l'agent
qui l'a écrite.

---

## 6. Tests

**14 tests dédiés** (`tests/test_session_instrument_rows.py`). Ils ne peuvent
pas mesurer un pixel — ils pinnent les **causes structurelles** du débordement,
celles qu'un futur commit réintroduirait sans s'en apercevoir :

- `test_the_row_label_no_longer_contains_a_sentence` — **aucun mot de trois
  lettres ou plus** dans le libellé de ligne. C'est l'assertion centrale : le
  défaut revient dès qu'une prose y retourne.
- `test_the_label_track_can_never_be_smaller_than_its_content` — la piste ne
  redevient pas une largeur fixe.
- `test_the_action_row_can_wrap_instead_of_overlapping`
- `test_the_primary_cta_is_not_the_first_to_shrink` — pinne `flex-basis ≠ 0`.
- `test_what_left_the_narrow_column_lives_in_the_annex` — garde de `§5.3`.
- `test_no_overflow_hidden_was_used_to_mask_the_defect` et
  `test_no_font_size_below_the_readable_floor` — les deux interdits explicites
  du sprint, pinnés plutôt que promis.

### Deux tests retournés, aucun affaibli

- `test_the_set_action_button_posts_stay` cherchait `« Enregistrer la série »`
  **n'importe où** dans le bloc du bouton. Il serait resté vert sur le seul
  `title`, sans plus rien vérifier du libellé rendu. Ouvert en deux : le libellé
  visible **et** la phrase entière, chacun asserté là où il vit.
- `test_chip_present_on_future_card_summary` exigeait `« première fois »`.
  Il vérifie désormais que **toute** puce porte son schéma, et deux tests neufs
  encadrent la suppression du cas vide des deux côtés.

---

## 7. Vérifications locales

`check_scope` classe **`SHARED_CODE`** (`app/services/briefing.py` est importé
ailleurs). Checks exigés à ce tier, tous passés :

| Check | Résultat |
|---|---|
| ruff (fichiers neufs) | **propre** — les 3 alertes du diff sont **préexistantes**, vérifiées identiques à `HEAD` |
| `check_ruff_budget` | **281 ≤ 548** |
| `check_spec_protocol` | **OK** |
| Tests dédiés | **14 passés** |
| Broad sweep ciblé | *(voir annexe)* |
| **Rendu réel à 390 px** | **0 débordement** — mesuré, capturé, exposé |

Le full sweep local est **explicitement skippable** à ce tier
(`Sb_OPS.ci-efficiency`) ; la CI parallélisée sur PR est le filet.

---

## 8. Ce qui n'est PAS fait, et pourquoi

- **La barre d'action collante recouvre les lignes S2/S3** quand la carte
  active est en haut de l'écran (mesuré : actions 775→836, S2 767→825). C'est
  le comportement **voulu** d'un CTA collant, **préexistant**, et inchangé par
  cette tranche — la hauteur de la barre est identique. Signalé à l'opérateur,
  pas corrigé : ce serait une dérive de périmètre.
- **Les cartes d'exercice E2…E7** cassent leurs noms sur trois ou quatre lignes
  avec beaucoup de vide à droite. Laid, mais **rien n'y déborde**. C'est du
  ressort de Q4-C.
- **Un exercice à la fois** (Q4-C) — non retenu par l'opérateur pour cette
  tranche.
- **Aucun token bleu écrit.** C'est `UI_TOKENS_BLUE_SYSTEM_01`, qui doit
  précéder tout usage du bleu.

---

## 9. Périmètre

| Fichier | Nature |
|---|---|
| `app/templates/_partials/exercise_card.html` | libellés, annexe, marqueur, CTA, puce |
| `app/static/css/app.css` | grille de ligne, code, annexe, ligne d'action |
| `app/static/css/session_focus.css` | marqueur d'état, titre sur trois lignes |
| `app/services/briefing.py` | **une clé additive** (`has_prior`) — aucune logique modifiée, `_last_time_chip` intact |
| `tests/test_session_instrument_rows.py` | **neuf** — 14 tests |
| `tests/test_briefing_surface.py` | 1 test retourné, 2 neufs |
| `tests/test_session_set_action.py` | 1 test ouvert en deux |
| `docs/DESIGN_DECISIONS_UIV2_SURFACES.md` | **neuf** — Q1–Q5, tokens, ordre |
| `CLAUDE.md` | **§5 — contrat de livraison UI** |

**Interdits du sprint, tous tenus** : aucune refonte de séance · aucun JS
(`test_no_javascript_was_introduced`) · aucun changement de modèle · aucune
migration · planner intact · BodyMap intact · aucune logique métier modifiée ·
aucune police sous 11 px · aucun `overflow: hidden` masquant.

---

## 10. Acceptation

| | Critère | Verdict |
|---|---|---|
| **A1** | zéro texte critique rogné à 390 px | ✅ **0** (31 + 7 → 0), mesuré |
| **A2** | bouton principal lisible | ✅ `Valider · E2`, capture à l'appui |
| **A3** | libellés série/échauffement compacts | ✅ `S1` / `É1` |
| **A4** | valeurs plus visibles que libellés | ✅ champs 72 px vs code ~24 px |
| **A5** | navigation `E1…E7` ne déborde pas | ✅ défileur volontaire, page à 390 px |
| **A6** | no-JS conservé | ✅ pinné |
| **A7** | tests HTML + rendu | ✅ 14 tests + mesure navigateur |
| **A8** | rapport avec capture avant/après | ✅ §1 et exposition |

---

## Verdict

**La page centrale du produit était cassée sur un téléphone, et le dépôt entier
ne pouvait pas le savoir.** Aucune garde ne regarde un pixel : c'est
exactement le trou que `CLAUDE.md §5` vient combler, et cette tranche est la
première à passer par lui.

Le plus instructif n'est pas la réparation, c'est **comment le défaut a été
trouvé** : en ouvrant la page dans un navigateur à la taille d'un téléphone.
Trois minutes. La tranche précédente avait livré CI verte, Sonar vert et
4 898 tests passants sans jamais faire ça.
