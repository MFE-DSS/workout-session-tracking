# `OQ_POSITIONAL_CSS_01` — la couleur suit l'identité, plus le rang

**Base** : `75cd4eb` · **Tier `check_scope`** : `ISOLATED` (traité en `SHARED_CODE`, voir §6)

---

## 1. Audit des règles positionnelles (livrable 1)

Cinq règles de couleur de plaque existaient, **trois** positionnelles. Toutes
localisées, aucune supposée.

| Sélecteur | Surface **réellement** ciblée | Couleur |
|---|---|---|
| `#…-shoulders .auren-mf-view-front\|back > g:nth-of-type(3) path` | `delt-lateral` | `--accent-hover` |
| `#…-shoulders .auren-mf-view-front\|back > g:nth-of-type(4) path` | `delt-posterior` | `--accent-muted` |
| `#…-posterior .auren-mf-view-back > g:nth-of-type(3) path` | `back-hamstring` | `--accent-soft` |

La colonne du milieu n'est pas une lecture du nom : elle a été **extraite** en
parcourant chaque vue et en listant les jetons de surface des chemins contenus
dans chaque groupe. Se tromper de rang aurait recoloré le mauvais muscle.

**Rangs implicites, qui tombent sur le repli** — `delt-anterior` (rang 2),
`back-gluteus` (rang 2), `hero` du chest (rang 2) gardaient l'accent partagé.

### Les identifiants existants suffisent — pas de HARD STOP

Vérification décisive : les `id` sont portés par les **`<path>`**, pas par les
groupes. Chaque identifiant contient son jeton de surface
(`auren-plate-region-shoulders--front-delt-lateral-000`). Un sélecteur
d'attribut sur le chemin suffit donc, **sans toucher un seul SVG**.

### Capacités auditées

| # | Capacité | Verdict |
|---|---|---|
| 1 | Règles `nth-of-type` | 3, listées ci-dessus |
| 2 | Lesquelles colorent une surface anatomique | les 3 |
| 3 | Ids/classes disponibles | ids sur les chemins ; classes `auren-mf-{context,hero,part,view-*}` sur les groupes |
| 4 | Les ids suffisent-ils | **oui** |
| 5 | Table exploitable du contrat | oui — grammaire §5.1 de `Sb_BODYMAP_IDENTITY_CONTRACT_01` |
| 6 | Tests SHA sur les SVG | `test_auren_muscle_focus_runtime.py`, 3 SHA gelés — intacts |
| 7 | Tests reduced-motion déjà corrigés | intacts (extraction par accolades, non re-cassée) |
| 8 | Tests viewport / skip CI | Playwright jamais installé en CI V1 — voir §5 |

---

## 2. Brainstorming / Options / Risques / Choix (CLAUDE.md §3)

**Option A — sélecteur d'attribut à égalité de spécificité.**
`.muscle-focus path[id*="-delt-lateral-"]` vaut `(0,2,1)`, exactement comme le
repli `.muscle-focus .auren-mf-part path`. Le gagnant dépendrait alors de
**l'ordre dans la feuille de style**. Rejetée : on échangerait une fragilité
d'ordre DOM contre une fragilité d'ordre source, sans la supprimer.

**Option B — remonter la spécificité** par un sélecteur plus long ou un `id`.
Rejetée : le brief demande explicitement de minimiser la spécificité et
d'éviter les sélecteurs longs.

**Option C — retenue : neutraliser la spécificité du repli avec `:where()`.**
`:where()` contribue **zéro**. Le repli tombe à `(0,1,1)`, les règles de surface
restent à `(0,2,1)` et gagnent **strictement**. Déplacer une règle dans le bloc
ne peut plus rien changer. Aucun `!important`, aucun sélecteur d'id.

**Risque principal, et comment il a été traité** : recolorer silencieusement une
surface. Neutralisé non par relecture mais par **mesure** — §4.

---

## 3. Le patch

```css
.muscle-focus :where(.auren-mf-context) path { fill: var(--fg-dim); }
.muscle-focus :where(.auren-mf-hero, .auren-mf-part) path { fill: var(--accent); }
.muscle-focus path[id*="-delt-lateral-"]   { fill: var(--accent-hover); }
.muscle-focus path[id*="-delt-posterior-"] { fill: var(--accent-muted); }
.muscle-focus path[id*="-hamstring-"]      { fill: var(--accent-soft); }
```

Cinq règles avant, cinq après. **Aucun SVG modifié, aucun template modifié,
aucun code applicatif modifié.** Le sprint est entièrement contenu dans onze
lignes de CSS et des tests.

`delt-anterior` est **délibérément absent** : Option A du contrat en fait une
surface de la plaque épaules, jamais une zone adressable. Il garde donc l'accent
de repli, exactement comme avant.

---

## 4. Équivalence de rendu — mesurée, pas plaidée

Le même balisage SSR a été rendu deux fois dans Chromium, avec l'ancienne puis
la nouvelle feuille de style, et le `fill` **calculé** de chaque chemin comparé.

> **53 chemins mesurés. Zéro changement de couleur.**

| Surface | `fill` calculé | Origine |
|---|---|---|
| `context` | `rgb(138, 148, 160)` | `--fg-dim` |
| `hero` | `rgb(200, 162, 75)` | `--accent` |
| `delt-anterior` | `rgb(200, 162, 75)` | `--accent` (repli) |
| `delt-lateral` | `rgb(215, 180, 92)` | `--accent-hover` |
| `delt-posterior` | `rgb(138, 117, 56)` | `--accent-muted` |
| `gluteus` | `rgb(200, 162, 75)` | `--accent` (repli) |
| `hamstring` | `rgba(200, 162, 75, 0.12)` | `--accent-soft` |

La comparaison avant/après était un montage jetable ; la table ci-dessus est
devenue une **garde permanente**
(`test_surface_colour_follows_identity_not_dom_rank`), qui relit ces couleurs
dans un navigateur au lieu de vérifier qu'un sélecteur existe.

---

## 5. Acceptation

| # | Critère | Méthode | Résultat |
|---|---|---|---|
| A1 | Zéro couleur par rang | 3 gardes + garde héritée | **PASS** |
| A2 | Surface ciblée par identité | jeton présent dans les assets, unicité vérifiée, spécificité prouvée | **PASS** |
| A3 | Assets inchangés | 3 SHA gelés | **PASS** |
| A4 | Rendu inchangé | **53 chemins mesurés avant/après** | **PASS** |
| A5 | Filmstrip inchangé | 42 tests `Sb_BODYMAP_FRAME_ATLAS_01` conservés | **PASS** |
| A6 | No-JS inchangé | garde script/on\*/WebGL/canvas | **PASS** |
| A7 | Pas de `zone_recovery` | garde existante maintenue | **PASS** |
| A8 | OQ retirée | garde inversée remplacée dans le **même commit** | **PASS** |
| A9 | Clarté CI | voir ci-dessous | **PASS** |
| A10 | Diff métier vide | §7 | **PASS** |

### A8 — la garde inversée a fonctionné comme prévu

`Sb_BODYMAP_IDENTITY_CONTRACT_01` avait posé
`test_positional_css_still_present_because_this_sprint_changes_no_runtime`, qui
**exigeait** que le défaut soit encore là, précisément pour qu'un correctif ne
puisse pas coexister avec une question ouverte périmée.

Elle est tombée dès le patch appliqué. Remplacée dans le **même commit** par
`test_positional_css_defect_is_gone_from_the_runtime`, et l'OQ passée à
`RESOLVED` dans le contrat. Le mécanisme a rempli exactement son office.

L'histoire du défaut est **conservée** dans le contrat (§3, encadré de mise à
jour) : la supprimer laisserait une future régénération d'assets réintroduire des
sélecteurs positionnels sans que personne ne se souvienne pourquoi ils avaient
été bannis. Une garde l'exige.

### A9 — ce que la CI vérifie, et ce qu'elle ne vérifie pas

`pyproject.toml` §`[baseline]` interdit Playwright en CI V1. Les tests de
`tests/test_bodymap_frame_atlas_viewport.py` — dont **la nouvelle preuve de
couleur calculée** — **skippent en CI**. Ils tournent en local avec un vrai
Chromium.

Les gardes **structurelles** (`test_bodymap_surface_identity.py`,
`test_bodymap_identity_contract.py`) tournent, elles, en CI : un retour du
`nth-of-type` sera attrapé automatiquement. Ce qui n'est pas attrapé en CI, c'est
une régression de **couleur calculée** qui passerait par un autre chemin que le
sélecteur positionnel.

### Gardes prouvées par plantation

Réintroduction de la règle positionnelle supprimée →
**cinq gardes indépendantes tombent**, réparties sur deux fichiers. Plantation
retirée, `git diff` vide sur `app.css` hors du patch.

---

## 6. Vérifications locales

`check_scope` a classé le diff `ISOLATED`. **Verdict volontairement remonté d'un
cran** : `app.css` est la feuille de style **globale**, et `CLAUDE.md` §1
avertit qu'un `ISOLATED` ne dispense pas du sweep quand le changement touche du
partagé — cet over-check a déjà attrapé trois régressions réelles.

| Check | Résultat |
|---|---|
| ruff (fichiers touchés) | propre |
| `check_ruff_budget.py` | 281 ≤ 548 |
| `check_spec_protocol.py` | OK |
| Suites BodyMap | **80 passés** |
| Broad sweep élargi (CSS global) | **843 passés** |

---

## 7. A10 — diff sur les fichiers protégés

| Cible | Diff |
|---|---|
| `app/services/recommendation.py` | **vide** |
| planificateur / `slot_intent` | **vide** |
| `migrations/` · `app/models.py` | **vide** |
| `app/services/muscle_mapping.py` | **vide** |
| les 3 SVG | **vide** (SHA gelés vérifiés) |
| `app/templates/**` | **vide** |
| `app/services/**` | **vide** |
| palette / tokens de couleur | **vide** (mêmes variables) |
| PR dependabot | non touchées |

---

## 8. Limites restantes

**Le rendu est robuste, la structure reste normative.** L'ordre des groupes n'est
plus lu par le CSS, mais §5.2 du contrat reste exigé : le moteur filmstrip
attend toujours `view → context → surfaces`, et une plaque qui inverserait
l'ordre des **vues** afficherait le mauvais cadre. Ce sprint supprime la
fragilité de **couleur**, pas celle de **cadrage**.

**La correspondance jeton → couleur reste dans le CSS**, pas dans le contrat
déclaratif. Ajouter une plaque avec un nouveau jeton coloré demandera une ligne
de CSS. C'est assumé pour V1 : générer le CSS depuis
`bodymap_frames.py` ajouterait une étape de build pour trois règles.

**La preuve de couleur ne tourne pas en CI** (§A9).

---

## Verdict

**RÉSOLU — la couleur ne dépend plus d'aucun ordre.**

Ni de l'ordre DOM des groupes, ni de l'ordre des règles dans la feuille de style :
`:where()` met le repli à spécificité nulle, si bien que les règles de surface
gagnent strictement. Le choix de conception importe plus que le patch — l'Option A
évidente aurait échangé une fragilité d'ordre contre une autre.

L'équivalence de rendu n'est pas affirmée, elle est **mesurée** : 53 chemins,
deux feuilles de style, zéro écart. Et la table de mesure est devenue une garde
permanente plutôt qu'un tableur jeté après usage.

Le dernier verrou technique avant la commande de géométrie est levé. Ce qui reste
entre AUREN et le profil corps entier n'est plus dans le dépôt.
