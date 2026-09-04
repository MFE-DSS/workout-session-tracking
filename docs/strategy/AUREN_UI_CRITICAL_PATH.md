# `AUREN_UI_CRITICAL_PATH` — la voie critique de bout en bout

> **Objet : rendre l'exécution autonome.** Tout ce qu'il faut pour avancer sans
> re-demander — état de départ, voies, ordre, critères d'acceptation, recette de
> vérification, conditions d'arrêt. Écrit le 2026-09-04.
>
> Se lit avec `AUREN_VISUAL_BACKBONE` (le **quoi**, gravé) ·
> `AUREN_UI_ARBITRATION_QUESTIONS` (les 37 **décisions** restantes) ·
> `AUREN_UI_REARBITRATION_REGISTER` (les 79 **objets**).

---

## 0. État de départ, vérifié

| | |
|---|---|
| Canonique | `4549d8f` — merge PR #182, closeout du chantier CI |
| Production | déployée à `4549d8f`, smoke 15 PASS, `DF-E` et `DF-F` en ligne |
| Arbre de travail | **propre**, hors 4 documents de stratégie non commités + `AGENTS.md` (jamais commité) |
| Chantier CI | **clos**. PR code ≈ 20,0 min-runner · push canonique 28,3 · PR docs 2,2 |
| `BLOC 0` | fermé 9/9 · `P-03` validé sur rendu réel |

---

## 1. Ce qui est **réellement** parallélisable

⚠ **Je ne fabrique pas quatre voies parallèles pour faire joli.** La voie UI est
**séquentielle par construction** : le châssis consomme les tokens, l'instrument
consomme le châssis. Le vrai parallélisme est ailleurs.

```
VOIE 1 — UI  (séquentielle, c'est le chemin critique)
  U1 tokens de rôle ──▶ U2 primitive de châssis ──▶ U3 instrument de séance ──▶ U4 accueil

VOIE 2 — DETTE NON-UI  (vraiment parallèle : zéro fichier en commun avec la voie 1)
  D1 arbitrages CI restants · D2 passlib → bcrypt 5 · D3 défaut de scoring de substitution
```

**Surface de collision entre les deux voies : nulle.** La voie 1 touche
`app/static/css/**` et `app/templates/**` ; la voie 2 touche `.github/**`,
`requirements*`, `app/services/**`. Deux worktrees, deux branches, deux PR —
conforme à *une PR = un agent*.

---

## 2. VOIE 1 — les tranches UI, dans l'ordre

### `U1` — Le socle de tokens de rôle · **débloqué, faisable maintenant**

**Ce que c'est.** Introduire les **16 rôles** de `§3.1` du backbone comme tokens,
**aliasés sur les valeurs existantes et déjà mesurées**. Zéro changement visuel.

**Pourquoi en premier.** C'est la seule tranche qui ne dépend d'**aucun** des 37
arbitrages, et dont **toutes** les autres dépendent. Elle transforme
« ambre = action » en `RÔLE → TOKEN → VALEUR` sans rien déplacer à l'écran.

**Critères d'acceptation**
- Les 16 rôles existent, chacun avec sa **mesure de contraste sur le fond réel**.
- `origin-system` et `support-information` sont **deux tokens distincts**, même
  s'ils aliasent la même valeur. Idem `action-primary` / `state-active`.
- **Aucun** `var(--token, #hex)` de repli introduit (`§5.4`).
- Rendu **identique** avant/après — c'est une tranche d'aliasing, la preuve est
  qu'on ne voit rien.

**Piège connu.** 100 tokens de couleur cohabitent sur **3 générations**
(`--t-*`, `--color-*`, et la génération courante). `U1` **ajoute une couche de
rôles ; il ne supprime aucune génération** — la table de migration est une
tranche à part (`§5.3` : jamais une soustraction seule).

**Exposition `§5.1`.** Une tranche invisible se prouve par **deux captures
identiques** + le diff de tokens. C'est le seul cas où « rien n'a bougé » est le
résultat attendu, et il doit être **montré**, pas affirmé.

### `U2` — La primitive de châssis · dépend de `U1`

**Ce que c'est.** Les 4 niveaux de profondeur de `§2`, plus la couche de texture
(scanlines, grain, phosphore) de `§3.5`, comme primitive isolée — **construite et
exposée, pas encore appliquée** aux surfaces existantes.

**Critères d'acceptation**
- 4 niveaux distincts et **lisibles comme tels** sur rendu réel.
- La texture tient dans les deux thèmes et sous `prefers-reduced-motion`.
- La lisibilité du texte **par-dessus le grain** est mesurée, pas supposée —
  c'est la contrainte de premier rang de `K-06`.
- `SYS-078` et `VIS-015` sont marqués superseded **dans le contrat**, pas
  seulement dans le backbone.

### `U3` — L'instrument de séance · dépend de `U2` **et de `BLOC 1`**

**Bloqué sur 4 arbitrages** : `S-08` `S-09` `S-10` `S-11`. La métaphore, elle,
est acquise — `V1` / `V2` / `V3` validés sur rendu.

**Critères d'acceptation** — le patron de `§4.1` du backbone, plus :
- Le contrat de lecture **à deux coups d'œil** tient sur écran 390×844.
- Le `density budget` `§9` est **mesuré** en contexte `EFFORT`, scroll avant
  action = **0**.
- Tout fonctionne **sans JavaScript** (`§10`) — démarrer, saisir, valider.
- `is_correcting` est représenté (dès que `S-11` est tranché).

**Illustration.** Le viseur part avec un **placeholder assumé**. L'illustration
biomécanique professionnelle est un chantier **parqué**, branché sur le programme
d'assets existant (17 specs, 3 plaques régionales produites) — pas un second
pipeline.

### `U4` — L'accueil · dépend de `U2` et de `BLOC 2` (7 arbitrages)

La jauge d'allocation **14 jours** est le cœur de cette tranche, et la première
matérialisation de `PH-01` hors séance.

---

## 3. VOIE 2 — la dette non-UI

⚠ **Provenance des trois éléments : reportés de sessions antérieures, non
revérifiés au code aujourd'hui.** Je les revérifie **avant** d'ouvrir chaque
tranche — comme `R-05` et `N-04` viennent de le rappeler, un défaut reporté n'est
pas un défaut prouvé.

| | Sujet | Nature |
|---|---|---|
| `D1` | Deux arbitrages CI restants : le `if:` du job `sonar` (PR de fork → check requis en attente ; **0/120 occurrences** observées) et **3→5 shards** (−3,6 min/PR pour +0,6 min-runner) | décision, pas code |
| `D2` | `passlib` → `bcrypt 5.x`. ⚠ **`bcrypt 5` est incompatible avec `passlib`** (probe interne de 255 octets) — il faut **remplacer passlib**, pas lever le plafond. **Ne pas merger la PR #7.** Débloque au passage le plafond `bcrypt<5` devenu sans motif | `shared_code`, sécurité |
| `D3` | Défaut de scoring de substitution (`None == None`) | à revérifier |

---

## 4. Recette de vérification — **par tier, pas par habitude**

**Toujours d'abord :**

```bash
python scripts/check_scope.py
```

Son verdict **fait loi** (`CLAUDE.md §1`). Attendus par tranche :

| Tranche | Tier attendu | Vérification locale |
|---|---|---|
| `U1` `U2` | `shared_code` (CSS partagé) | ruff + budget + spec_protocol + tests ciblés + **broad sweep ciblé obligatoire** |
| `U3` `U4` | `shared_code` | idem + `test_ui_surface_guards` + `check_test_isolation` |
| `D2` | `shared_code` | idem + **full sweep local recommandé** (blast radius auth) |
| docs seuls | `docs` | `check_spec_protocol` uniquement |

**Interdits mécaniques, rappelés parce qu'ils ont coûté cher :**

- ⛔ **Jamais `pytest -n auto`.** Sur ce poste, `auto` = nombre de cœurs, la
  machine part en swap et **emporte les conteneurs voisins**.
- ⛔ **Jamais `run_ci_pytest.sh` sur un poste.** Le script **refuse** désormais de
  s'exécuter hors CI. Pour un sweep local : `bash scripts/run_local_sweep.sh`.
- ⚠ Un sweep parallèle saturé **rend de faux rouges**. Avant d'imputer un échec
  au produit, **le rejouer en série** — 23 rouges en `-n auto`, 105/105 verts en
  série, mesuré.
- ⚠ Un sweep lancé depuis un **worktree** teste la **canonique** si le script n'a
  pas de `cd` : vérifier que `coverage.xml` apparaît **dans le worktree**, sinon
  le vert ne porte sur rien.

**Gardes UI à ne pas casser** — `test_ui_surface_guards` (plancher 44 px ·
marqueurs `<summary>` · cohérence sélecteurs JS↔templates) et
`tests/ui_surface_inventory.json` (9 planchers, 27 règles gelés). Un cliquet qui
monte est légitime ; un cliquet qu'on desserre pour verdir est interdit.

---

## 5. Contrat de livraison UI — les 5 règles, appliquées

Aucune tranche de la voie 1 n'atteint `PR GREEN` sans que ces cinq soient tenues :

1. **`§5.1` Exposition** — rendu réel exposé **avant** tout commit UI. Vérifier
   une classe dans le HTML **ne vaut pas** exposition ; un test vert non plus.
2. **`§5.2` Relecture** — les relevés `DESIGN_DECISIONS_*` relus **décision par
   décision**, consignés dans le rapport : respectée / non concernée / violée.
3. **`§5.3` Jamais une soustraction seule** — ce qui remplace part dans la
   **même** livraison. Concerne directement `R-06`, `N-02`, `N-03`.
4. **`§5.4` Toute couleur est un token mesuré** — pas de hex de maquette sans
   recalibrage sur le fond réel, pas de `var(--absent, #hex)`.
5. **`§5.5` Centralité avant facilité** — d'où l'ordre `U1→U4` et
   `BLOC 1→2→3→7→6→4→5`, et non l'inverse.

---

## 6. Ce que je fais seul, et où je m'arrête

**Après un `GO BUILD`, en autonomie** : branche + worktree · patch **scopé** ·
checks exigés par `check_scope` · correction des échecs **dans le périmètre** ·
commit · push · PR · **une seule** récupération d'un dispatch CI bloqué
(vérifier `mergeable` **avant** — un `refs/pull/N/merge` inconstructible signifie
**conflit**, pas panne GitHub) · lecture des logs CI · correctifs CI/Sonar dans le
périmètre · arrêt à `PR GREEN / MERGE PENDING`.

**Jamais sans `GO` humain** : merge · squash · `--admin` · suppression de
branche/worktree · changement de périmètre · affaiblissement d'un test ou d'une
garde · `AGENTS.md`.

**Arrêts durs** : conflit de spec · ambiguïté de forme de migration · action
destructive de données · faille ou secret · CI rouge **hors périmètre** ·
**et, propre à ce programme : tout écart au rendu que vous avez validé.**

**Ce qui ne justifie PAS un arrêt** : un lint local, un test à réparer dans le
périmètre, un rouge CI diagnostiqué et imputable à ma tranche, l'ajout d'un test
de régression, la doc interne à la tranche.

---

## 7. Prochain pas immédiat

`U1` — le socle de tokens de rôle. **Zéro dépendance sur les 37 arbitrages**,
et tout le reste en dépend. C'est la seule tranche qui avance pendant que vous
arbitrez, sans préempter une seule de vos décisions.

En parallèle réel : `D1`, qui est une décision et non du code.
