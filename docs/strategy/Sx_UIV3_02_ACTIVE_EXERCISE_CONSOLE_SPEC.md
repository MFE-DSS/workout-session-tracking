# `Sx_UIV3_02` — Active Exercise Execution Console

**Statut : `APPROVED — OPERATOR`** (2026-08-18, avec les amendements A/B/C de `Sx_UIV3_04 §1bis`)
**Dépend de** `Sx_UIV3_00` (Foundation Contract), qui prévaut en cas de conflit.
**Portée : UI/UX uniquement.** Aucun changement de route, de modèle, de calcul.

---

## 1. Audit du runtime — mesuré, pas lu

Build local, `push-a` / E1 Incline Smith Press, Chromium.

| Mesure | 360 × 800 | 390 × 844 | 430 × 932 |
|---|---:|---:|---:|
| Document | 3 759 px | **3 651 px (4,3 écrans)** | 3 567 px |
| y de la série courante | 864 | **843** | 843 |
| Scroll requis pour la voir | **132 px** | **67 px** | 0 px |

**La série courante est sous la ligne de flottaison** aux deux largeurs les
plus fréquentes. L'utilisateur doit scroller pour voir ce qu'il est en train
de faire, **à chaque série**.

Autres constats :

- **Le bouton d'action est rendu avant la série sur laquelle il agit** :
  `.card__actions` à y = 775, `.set-row--active` à y = 843. L'ordre du
  document contredit l'ordre de la tâche.
- **34 contrôles interactifs** dans la carte active, dont **17 sous 44 px**.
  Sur la page entière : **161 occurrences** sous 44 px, dont 27
  `label.segmented__option` à 32 px et le CTA de séance à **38 px**.
- **Recouvrement sticky confirmé** dans un état réel : après `nav=stay`, la
  barre d'action collante couvre la ligne `É1`.
- **Toutes les séries terminées restent éditables** (2 champs chacune, 0
  verrouillé) — la correction est possible mais **rien ne le signale**.

Le durcissement précédent (`É1`/`S1`, `Valider`, `Valider · E2`, titre
multi-ligne) a supprimé 31 débordements. **C'est une hypothèse de hardening,
pas une spec cible** — et il n'a rien changé aux quatre points ci-dessus.

---

## 2. Contract audit

| Élément | Tier | Verdict |
|---|---|---|
| `nav=stay` et `nav=next` sont réellement traités par le routeur | **T1** | invariant |
| Aucun libellé ne revendique une action que la route n'exécute pas (`test_cta_copy_does_not_claim_a_set_level_action`) | **T3** | invariant de contrat, conservé **tel quel** — il a déjà attrapé une rédaction fautive |
| `completed` dérivé serveur, aucune checkbox | **T1** | invariant |
| Repli sans JS de toute la saisie | **T2** | invariant |
| Rappel de charge précédente `aria-hidden`, source accessible ailleurs | **T2** | invariant |
| Inventaire JS exact (3 fichiers) | T3 | conservé |
| « aucune action de série n'existe » dans une docstring historique | **STALE** | `nav=stay` **l'implémente** depuis `Sb_SESSION_SET_ACTION_01`. Une docstring ne définit pas le produit contre le runtime. |
| `min-height: 422px` et `margin-top:auto` sur le hero | **T5** | remplacé |
| `.card__actions--exercise` en position sticky | **T4** | à réévaluer : la spec la remplace par une commande d'état |
| `test_session_focus_sticky_cta` (16 tests) | **T5** | remplaçable quand la commande contextuelle existe |
| `test_session_instrument_rows` (14 tests) | T4 | **conservés** : ils pinnent des causes structurelles de débordement, valides quelle que soit la console |
| `label.segmented__option` à 32 px | **T2 violé** | dette à corriger, inscrite en `B8` |

---

## 3. Benchmark — patterns, pas styles

| Produit | `CURRENT SET → LOG → REST → NEXT SET` |
|---|---|
| **Gravl** | chaque série est **pré-remplie** en charge et répétitions ; un tap « done » **démarre le repos automatiquement** ; minuteur réglé **par exercice** |
| **Fitbod** | enregistrer une série **démarre le compte à rebours** ; son/vibration à la fin ; le minuteur est **sous le nom de l'exercice** ; tap pour ajuster |
| **Hevy** | démarrage en 2 taps ; le logging est le seul objet de l'écran |
| **Boostcamp** | séries/répétitions/repos posés d'avance ; auto-progression |

**Le pattern de marché est unanime : enregistrer une série fait passer à
l'état REPOS, automatiquement.** L'utilisateur ne choisit pas entre « rester »
et « avancer » — le système le sait.

| Produit | `EXERCISE → SUBSTITUTE → RETURN` |
|---|---|
| **Fitbod** | « Swap » en haut à droite, menu unique regroupant toutes les substitutions |
| **Gravl** | adaptation à l'équipement disponible |

AUREN conserve son langage — graphite, mono, ambre, rail. **Le pattern est
emprunté ; le style ne l'est pas.**

---

## 4. La machine à états, tranchée

```
WARMUP → CURRENT SET → REST → CURRENT SET → … → EXERCISE COMPLETE → NEXT EXERCISE
```

**Question posée** : peut-on remplacer la coexistence permanente
`Valider` + `Valider · E2` par une **commande principale contextuelle** ?

**Réponse mesurée : oui.** Justification, dans l'ordre :

1. **La coexistence est un artefact de réparation.** Elle est née d'un
   chevauchement de libellés, pas d'un besoin de deux actions simultanées.
2. **Elle demande à l'utilisateur une décision que le système possède.**
   « Rester » ou « avancer » est déterminé par `work_done < work_total`.
   Le proposer, c'est déléguer un calcul connu.
3. **Le marché entier a tranché dans l'autre sens** (§3).
4. **Mesure** : les quatre prototypes à commande contextuelle placent la
   commande à une position **stable** (y = 731 à 775 selon le concept) avec
   **0 cible sous 44 px** et **0 scroll**. La console actuelle a deux boutons
   concurrents, 17 cibles sous 44 px et 67 px de scroll.

**Réserve honnête** : `nav=stay` reste utile pour **corriger** une série déjà
enregistrée sans quitter l'exercice. Il ne disparaît pas ; il **cesse d'être
une action dominante permanente** et devient l'action de l'état `CORRECTION`.

### Commande par état

**Libellés figés par l'amendement opérateur B (`04 §1bis`).** Aucune autre
formulation n'est autorisée. `Valider · E2` est **définitivement supprimé** :
il faisait porter à une commande de *série* la destination d'un *exercice*.

| État | Commande dominante | Secondaire |
|---|---|---|
| `WARMUP` | `VALIDER É1` | passer l'échauffement |
| `CURRENT SET` | **`VALIDER Sx`** — sous-titre « → repos 90 s » | adapter · historique |
| `REST` | **`PASSER LE REPOS`** — sous-titre « S3 → » | +30 s |
| `EXERCISE COMPLETE` | **`CONTINUER → Ex`** — sous-titre nom de l'exercice | revoir l'exercice |
| `LAST EXERCISE COMPLETE` | **`TERMINER LA SÉANCE`** | continuer à saisir |
| `CORRECTION` | `ENREGISTRER LA CORRECTION` | annuler |

**`REST` est un état de présentation à portée de requête, jamais un état métier
persisté** (`04 §1bis C`). Il est dérivé du fait qu'une série vient d'être
enregistrée ; il n'est écrit nulle part.

---

## 5. Design Lab — quatre consoles

Prototypes : `/tmp/auren-ui-lab/session/`. Quatre états chacun : avant S1 ·
S2 active · repos après S2 · exercice terminé.

| | Concept | y de la commande | Objet vif | Cibles < 44 px | Scroll |
|---|---|---:|---:|---:|---:|
| **A** | Current Set Instrument | 731 (stable) | 87 (stable) | **0** | **0** |
| **B** | Dense Expert Logger | 775 (stable) | 133 → 200 | **0** | **0** |
| **C** | Stateful Command Dock | 773 (stable) | 83 → 116 | **0** | **0** |
| **D** | AUREN Future Console | 272 → 292 | 91 → 224 | **0** | **0** |

*(référence : console actuelle — commande à 775, objet vif à 843, 17 cibles
sous 44 px, 67 px de scroll)*

### A — Current Set Instrument
Une série occupe l'écran : code en 34 px, deux champs en 56 px, la référence
dessous. Le reste est une liste compacte. **Le plus lisible en salle.**
*Faiblesse* : beaucoup d'espace libre ; l'expert qui veut voir ses trois
séries d'un coup doit scroller.

### B — Dense Expert Logger
Les trois séries visibles en permanence, la courante en ambre. La mise en page
**ne bouge jamais** entre les états. *Faiblesse* : la commande change de sens
sans que la page change d'aspect — le changement d'état est peu signalé.

### C — Stateful Command Dock
La liste défile, un dock inférieur porte l'état (« état · repos ») et la
commande. *Faiblesse* : le dock mange 120 px en permanence ; le libellé d'état
au-dessus du bouton est de la redondance textuelle.

### D — AUREN Future Console
La séance est une **bande verticale** — le même vocabulaire de rail que la Home
(`Sx_UIV3_01 §3`). Séries passées en points ambre atténués, série courante en
point haloé, futures en fantômes, repos en point pointillé.
**Commande à y = 272** — de loin la plus haute. *Faiblesse* : c'est le concept
le plus neuf, donc le moins éprouvé ; le rail doit être compris comme une
syntaxe et pas comme une décoration.

### Classement

| Critère | A | B | C | D |
|---|:-:|:-:|:-:|:-:|
| Lisibilité en salle | **9** | 6 | 8 | 8 |
| Efficacité expert | 5 | **9** | 7 | 8 |
| Clarté du changement d'état | 8 | 4 | **9** | **9** |
| Continuité avec la Home V3 | 5 | 5 | 6 | **10** |
| Densité | 4 | **9** | 7 | 8 |
| Coût technique | **9** | 8 | 7 | 6 |
| **Total /60** | 40 | 41 | 44 | **49** |

---

## 6. Recommandation

**D — AUREN Future Console**, avec deux emprunts :

- **de A** : l'ampleur des champs de saisie de la série courante (56 px,
  chiffres en 22 px) — on saisit avec les mains moites, debout ;
- **de C** : le libellé d'état, mais **fusionné dans la commande** plutôt
  qu'empilé au-dessus (le sous-titre « → repos 90 s » le porte déjà).

**Pourquoi D plutôt que C**, alors que C est plus conventionnel : D place la
commande à **272 px** contre 773, et surtout il **partage le rail avec la
Home**. Une même syntaxe visuelle — le filet vertical qui relie des états
dans le temps — sur les deux surfaces principales. C'est ce que
`Sx_UIV3_04_HOME_SESSION_CONVERGENCE` viendra sceller.

---

## 7. Spécification de la console retenue

### 7.1 Hiérarchie de l'information

| Niveau | Contenu |
|---|---|
| **L1** | la série courante (ou l'état courant) + la commande |
| **L2** | séries de l'exercice (passées, courante, futures) · cible et schéma · référence de la dernière séance |
| **L3** | cues techniques · zone travaillée · substitution · notes · ressenti · Up Next détaillé |

### 7.2 États visuels

| État | Bande | Marqueur | Commande |
|---|---|---|---|
| `WARMUP` | `É1`, `É2` en tête, atténués après validation | point plein ambre atténué | `VALIDER É1` |
| `CURRENT SET` | point haloé, champs ouverts en 50 px | halo ambre | `VALIDER S2 · → repos 90 s` |
| `REST` | point **pointillé** ambre, minuteur à la place des champs | pointillé | `PASSER LE REPOS · S3 →` |
| `COMPLETED SET` | valeur figée `60 × 10 ✓`, opacité 0,6, **tapable pour corriger** | point plein ambre | — |
| `FUTURE SET` | `—`, opacité 0,32 | point gris | — |
| `EXERCISE COMPLETE` | résumé `3/3 · 177 kg` | point plein | `CONTINUER → E2` |

### 7.3 Échauffement

Dans la même bande que les séries de travail, **en tête**, avec le préfixe `É`.
Une fois tous terminés, le groupe se replie en **une ligne** :
`échauffement 2/2 ✓` — tapable pour rouvrir. C'est du L3 une fois fait.

### 7.4 Correction d'une série passée

`FLOW D` est aujourd'hui possible mais **muet** : les champs sont éditables et
rien ne le dit. La spec impose :

- une **affordance visible** sur une ligne terminée (le code devient tapable,
  soulignement au survol/focus) ;
- taper une ligne terminée entre dans l'état `CORRECTION` : ses champs
  s'ouvrent, la commande devient `ENREGISTRER LA CORRECTION`, secondaire
  `annuler` ;
- la sortie de `CORRECTION` **rend la main à l'état précédent**, jamais au
  début de l'exercice ;
- route inchangée : c'est `nav=stay` qui la sert.

### 7.5 Minuteur

Amélioration progressive (`Sx_UIV3_00 §10`). Sans JS, l'état `REST` affiche
`repos suggéré : 90 s` en statique et la commande `PASSER LE REPOS` reste
fonctionnelle. Avec JS, le compte à rebours s'anime.

**Pattern de marché adopté** : valider une série **entre automatiquement en
`REST`**. Aucun tap supplémentaire.

### 7.6 Substitution

Surface **L3**, un seul point d'entrée nommé `Adapter`, regroupant :
remplacer l'exercice · alternatives · matériel indisponible. Aujourd'hui trois
contrôles concurrents se disputent la ligne. Un menu unique, sur le modèle du
« Swap » de Fitbod, **avec le langage AUREN**.

Le retour de la substitution **revient à l'état courant de la série**, jamais
en haut de la carte.

### 7.7 Cues techniques · zone travaillée · Up Next

L3. Repliés par défaut, sous la bande. `Up Next` reste, réduit à une ligne :
`E2 Chest Press machine · 3×8-12`.

### 7.8 Clavier

- `inputmode="decimal"` pour la charge, `inputmode="numeric"` pour les
  répétitions — contrat existant, conservé.
- La série courante est **au-dessus** de la zone couverte par le clavier
  virtuel : cible ≤ 45 % de la hauteur du viewport. À 390 × 844, la série
  courante doit rester **sous 380 px**. Le prototype D la place à 91–135 px.
- Aucun `position: fixed` sous la série courante : c'est la cause des
  recouvrements mesurés.

### 7.9 Sticky

**La barre d'action collante actuelle est supprimée.** Elle a produit un
recouvrement mesuré (`É1`) et elle n'est nécessaire que parce que la commande
est loin. Avec la commande à 272 px, il n'y a rien à rendre collant.

### 7.10 No-JS

Saisir, enregistrer, naviguer, corriger, terminer : tout fonctionne sans JS.
Seul le décompte du minuteur est enrichi.

### 7.11 Accessibilité

- Tout contrôle fréquent ≥ 44 × 44 px, **mesuré au navigateur**. Cible : **0
  occurrence** sous 44 px sur la console.
- Chaque champ garde son `aria-label` complet (« Charge en kg — série 2 »).
- Le point d'état porte `role="img"` + `aria-label`.
- Le changement d'état est annoncé par le **libellé de la commande**, pas
  seulement par la couleur.
- Rail décoratif, invisible aux technologies d'assistance.

### 7.12 États vides et inconnus

| Cas | Rendu |
|---|---|
| Aucune référence précédente | `première fois` — une seule fois par exercice, dans le bloc référence, **jamais** répété sur la puce |
| Aucune donnée saisie | champs vides avec placeholder `kg` / `reps`, jamais de valeur pré-remplie inventée |
| Exercice substitué | le nom substitué prime, le nom d'origine en L3 |

**AUREN ne pré-remplit pas** la charge et les répétitions comme Gravl : ce
serait une prédiction que le moteur ne produit pas. La référence de la
dernière séance est **affichée à côté**, pas injectée dans le champ.

### 7.13 Budget mobile

| Mesure | Cible | Prototype D |
|---|---:|---:|
| y de la série courante | ≤ 380 px | **91–135 px** |
| y de la commande | ≤ 400 px | **272–292 px** |
| Scroll avant l'action dominante | **0 px** | **0 px** |
| Cibles sous 44 px | **0** | **0** |
| Document par exercice | ≤ 1 400 px | à mesurer au build |

---

## 8. `UI_DATA_GAP`

| # | Gap | Existe ? | Pass-through ? |
|---|---|---|---|
| **G4** | L'état `REST` n'est pas un état serveur | non, et **il ne doit pas le devenir** | **CLOS** par `04 §1bis C` : `REST` est un **état de présentation à portée de requête**, dérivé du fait qu'une série vient d'être enregistrée. Jamais persisté, jamais un champ, jamais un modèle. Le persister ferait de la durée de repos une affirmation du produit alors qu'elle est une suggestion. |
| **G5** | Volume total de l'exercice (`177 kg`) affiché à l'état terminé | dérivable des `SetLog` déjà rendus | **oui**, somme de présentation, aucun score |

---

## 9. Blockers — résolus le 2026-08-18

- **`BLOCKER-3` — RÉSOLU : OUI.** La coexistence permanente `Valider` /
  `Valider · E2` est supprimée. **L'état devient le contrôleur de la
  commande** : `VALIDER S2 → REPOS → VALIDER S3 → CONTINUER E2`. Le contrat
  d'interaction **T3** change **par cette spec**, ce qui est la seule voie
  autorisée (`Sx_UIV3_00 §11`). `nav=stay` survit comme action de l'état
  `CORRECTION`.
- **`BLOCKER-4` — RÉSOLU : OUI, dogfood obligatoire.** La Future Console
  **n'est pas figée** avant une séance complète réellement exécutée sur
  360 / 390 / 430. Motif opérateur : les 161 cibles sous 44 px prouvent que la
  qualité de cette interface **ne peut plus être inférée du CSS**. Le dogfood
  est une **porte bloquante** de la tranche `B6`, pas une recommandation.

### Reste ouvert

- Le nombre de séries visibles simultanément dans la bande à 360 px — à
  trancher au dogfood.

## 10. Amendement `00A`

- La commande devient la primitive **`CommandDock`**, la série courante
  **`SetInstrument`**, le repos **`RestReadout`**, la référence
  **`DeltaReadout`**.
- **`CausalRail` n'entre PAS en Session** (amendement opérateur A,
  `04 §1bis`). La bande verticale de la console est un **filet structurel
  neutre** sans sémantique ; la séquence passé/courant/futur est portée par les
  `SetInstrument` eux-mêmes (profondeur, opacité, marqueur d'état).
  **Conséquence assumée** : le « rail partagé avec la Home » ne peut plus être
  invoqué comme argument du choix de D. Le classement du §5 est corrigé —
  D passe de **49 à 46**, contre 44 pour C. D reste retenu sur sa seule
  supériorité mesurée : commande à **y = 272** contre 773.
- Les six états du §7.2 se conforment à la table d'illumination `00A §4` :
  **trois signaux minimum** par changement d'état, jamais le libellé seul.
- `:active` obligatoire sur `CommandDock` (`00A §5`) — sans lui, la latence
  SSR fait retaper l'utilisateur.
- `Adapter` (§7.6) devient un **popover ancré** (`00A §7`), avec repli en flux
  obligatoire ; il cesse d'allonger la console.
- Les transitions `série validée → repos` et `repos → série suivante` sont les
  deux seules animations autorisées ici (`00A §6`, `00A §8`).

### Correction de périmètre — RIR

Une maquette d'illustration de cette console faisait apparaître **« RIR 2 »**.
**Vérifié : `SetLog` ne porte ni `rir` ni `rpe`.** Les deux notions n'existent
que dans les services de planification hebdomadaire, jamais comme valeur
journalisée par série. L'afficher exigerait un champ, donc un modèle et une
migration — hors périmètre absolu.

**La console V3 affiche charge, répétitions et référence. Pas de RIR.**
Enregistré comme `UI_DATA_GAP G6`, **bloqué**.
