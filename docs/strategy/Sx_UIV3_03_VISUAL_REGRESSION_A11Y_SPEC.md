# `Sx_UIV3_03` — Visual Regression & Accessibility

**Statut : `APPROVED — OPERATOR`** (2026-08-18, avec les amendements A/B/C de `Sx_UIV3_04 §1bis`)
**Dépend de** `Sx_UIV3_00`, `Sx_UIV3_01`, `Sx_UIV3_02`.
**Portée : UI/UX uniquement.** Outillage de vérification, aucun code applicatif.

---

## 1. Pourquoi cette spec existe

Quatre défauts ont été livrés en production avec **CI verte, Sonar vert et
4 898 tests passants** :

| Défaut | Ce qui aurait dû l'attraper |
|---|---|
| Badge d'accueil au registre typographique faux, token inexistant | aucune garde ne regarde un pixel |
| 31 débordements de texte sur la console de séance | idem |
| Série courante sous la ligne de flottaison | idem |
| 161 cibles tactiles sous 44 px | idem |

**Le dépôt possède 656 gardes UI et aucune ne rend une page.** Elles lisent du
HTML et du CSS. Les quatre défauts ci-dessus ne sont pas dans le HTML : ils
sont dans le **rapport géométrique** entre des éléments rendus.

`CLAUDE.md §5.1` impose déjà l'exposition d'un rendu à l'opérateur avant tout
commit UI. Cette spec en fait un **outillage reproductible** — le jugement
humain reste la garde finale, mais il cesse d'être la seule.

---

## 2. Golden states

### HOME — 5 états

| # | État | Fixture requise |
|---|---|---|
| `H1` | reco normale | historique produisant une reco + zones visées mesurées |
| `H2` | zones visées `unknown` | reco dont au moins une `primary_zone` est sans preuve |
| `H3` | partially recovered | au moins une zone en bande intermédiaire |
| `H4` | séance active | une session `in_progress` |
| `H5` | aucune reco | utilisateur sans template éligible |

### SESSION — 8 états

| # | État | Fixture requise |
|---|---|---|
| `S1` | warmup en cours | session neuve, échauffements non saisis |
| `S2` | série S1 courante | échauffements terminés |
| `S3` | série S2 courante | S1 enregistrée |
| `S4` | repos | une série vient d'être enregistrée |
| `S5` | dernière série | S1 et S2 enregistrées |
| `S6` | exercice terminé | 3/3 enregistrées |
| `S7` | substitution ouverte | surface `Adapter` dépliée |
| `S8` | correction d'une série passée | une série terminée en édition |

**13 golden states × 3 viewports = 39 captures.**

---

## 3. Viewports

| Largeur | Rôle |
|---|---|
| **360 × 800** | plancher — **fait foi en cas de conflit** |
| **390 × 844** | référence |
| **430 × 932** | confort |

`device_scale_factor: 2`. Chromium uniquement — la baseline vérifie la
**géométrie du produit**, pas la compatibilité navigateur.

---

## 4. Assertions mesurées, pas seulement des images

Une baseline d'image seule produit du bruit et se fait mettre à jour sans
réflexion. Chaque golden state porte donc aussi un **relevé chiffré** en JSON,
qui est la partie **bloquante**.

Par état, obligatoirement :

```json
{
  "state": "S3", "viewport": "390x844",
  "hard_overflow": 0,
  "clipped_text": 0,
  "targets_below_44": 0,
  "dominant_cta_y": 272,
  "dominant_cta_bottom": 328,
  "live_object_y": 135,
  "scroll_before_action": 0,
  "document_height": 1180,
  "sticky_overlaps": []
}
```

### Seuils d'échec — bloquants

| Métrique | Seuil |
|---|---|
| `hard_overflow` | **0** — texte débordant sans ellipse |
| `targets_below_44` | **0** sur les surfaces V3 |
| `scroll_before_action` | **0 px** |
| `sticky_overlaps` | **liste vide** |
| `document_height` | Home ≤ 1 200 px · Session ≤ 1 400 px par exercice |
| contraste de tout token utilisé | ≥ 4,5:1 texte · ≥ 3,0:1 non textuel, **mesuré sur le fond réel** |

**Ces seuils sont la vraie garde.** L'image sert au jugement humain ; les
nombres servent à la CI.

---

## 5. Distinguer troncature gracieuse et débordement dur

Une mesure naïve de `scrollWidth − clientWidth` **confond deux choses** — cette
confusion a produit une annonce fausse (« 38 textes rognés » pour 31
débordements réels et 7 ellipses volontaires).

| Cas | Détection | Verdict |
|---|---|---|
| **Débordement dur** | `overflow-x: visible` et `scrollWidth > clientWidth` | **échec** — le texte se superpose au voisin |
| **Troncature gracieuse** | `text-overflow: ellipsis` **et** `overflow: hidden` | **avertissement** — signalé, non bloquant |
| **Défileur volontaire** | `overflow-x: auto | scroll` | **ignoré** |

Le harnais **doit** implémenter ces trois branches. Une garde qui les mélange
crie au loup et sera désactivée au bout de trois sprints.

---

## 6. Règles de mise à jour des baselines

**Une baseline ne peut jamais être mise à jour pour faire passer un diff.**

Toute mise à jour exige, dans le commit :

1. la **référence de la décision UI versionnée** qui la justifie —
   `Sx_UIV3_0x §y`, ou une entrée de `DESIGN_DECISIONS_*` ;
2. le **tier de garde** concerné (`Sx_UIV3_00 §11`) ;
3. le **rendu exposé à l'opérateur** et son arbitrage (`CLAUDE.md §5.1`) ;
4. le **delta chiffré** avant/après sur les métriques du §4.

Une mise à jour de baseline sans les quatre est un **STOP**.

**Corollaire.** Une baseline qui change *sans* qu'aucune décision UI n'ait
changé est la définition d'une régression visuelle. C'est exactement le cas
que cette spec existe pour attraper.

---

## 7. Outillage

`scripts/visual_baseline_capture.py` existe déjà (`Sb_UI_11.1`) : CLI
Playwright, `--dry-run`, `--priority`, `--viewport`, `--base-url`, `--out-dir`,
`--state-file`, import Playwright paresseux. **Il est réutilisé, pas
réécrit.**

Ce qui manque, et que la tranche `B9` doit ajouter :

- les **13 golden states V3** dans le catalogue de captures ;
- le **relevé JSON** du §4 à côté de chaque PNG ;
- les **trois branches de détection** du §5 ;
- un **comparateur** qui échoue sur les seuils, pas sur les pixels.

**Playwright n'est pas dans la CI** (extra `.[baseline]`). La capture reste
donc **locale et opérateur-déclenchée** ; le relevé JSON, lui, est versionné et
peut être comparé en CI sans navigateur.

---

## 8. Accessibilité — vérifications automatisables

| Vérification | Méthode | Tier |
|---|---|---|
| Cible ≥ 44 × 44 px | `getBoundingClientRect` sur tout contrôle | **T2** |
| Nom accessible sur tout contrôle | `aria-label` / texte / `role="img"` | **T2** |
| Aucun état par la couleur seule | inventaire des états, ≥ 2 signaux | **T2** |
| Contraste sur fond réel | calcul WCAG sur les tokens effectivement composés | **T2** |
| `prefers-reduced-motion` respecté | présence de la media query | **T2** |
| No-JS | rendu avec `javaScriptEnabled=False`, actions critiques présentes | **T2** |

**Le rendu no-JS devient un golden state à part entière** pour `H1` et `S3`.
C'est aujourd'hui affirmé par des gardes qui lisent le template ; ce sera
vérifié sur du HTML servi sans JS.

---

## 9. Extensions imposées par `Sx_UIV3_00A`

Trois assertions supplémentaires, **bloquantes**, ajoutées au relevé JSON du §4 :

| Métrique | Seuil | Origine |
|---|---|---|
| `surface_ladder_min_step` | **≥ 1,12:1** entre deux surfaces adjacentes | `00A §1.2` |
| `text_tokens_below_aa` | **0** — tout token porteur de texte mesuré **sur le fond où il est réellement composé**, pas sur `--t-base` | `00A §1.3` |
| `controls_without_active_state` | **0** — tout `CommandDock` et tout contrôle personnalisé possède un `:active` | `00A §5` |

```json
{
  "surface_ladder": [1.065, 1.124, 1.161, 1.299, 1.410],
  "surface_ladder_min_step": 1.124,
  "text_tokens_below_aa": [],
  "controls_without_active_state": 0
}
```

**Captures et mouvement.** Aucune capture n'est prise **pendant** une View
Transition (`00A §8`) : les baselines saisissent des états stables. Le harnais
force `prefers-reduced-motion: reduce` à la capture, ce qui rend les baselines
déterministes **et** vérifie au passage que la garde T2 tient.

**Overlays.** Un golden state supplémentaire par popover spécifié, capturé
**dans son repli en flux** — c'est la version dégradée qui doit rester
utilisable, donc c'est elle qu'on pinne.

**Glanceability.** Non automatisable, volontairement (`00A §10`). Le relevé
JSON porte un champ `glanceability_dogfood` renseigné **à la main** :
`{state, viewport, operator, verdict, date}`. Un état sans verdict opérateur
ne peut pas passer en `BUILD`.

## 10. Ce que cette spec ne fait pas

- Elle **ne remplace pas** `CLAUDE.md §5.1`. Un harnais vert n'est pas une
  exposition. L'opérateur tranche toujours.
- Elle ne vérifie pas la beauté. Elle vérifie la **géométrie, la lisibilité et
  l'accessibilité**. Le jugement esthétique reste humain — c'est le seul
  domaine où il est la seule garde possible.
- Elle n'introduit aucun navigateur dans la CI.

---

## Non-goals

- Ne remplace pas `CLAUDE.md §5.1`. Un harnais vert n'est pas une exposition ;
  l'opérateur tranche toujours.
- Ne vérifie pas la beauté. Géométrie, lisibilité et accessibilité seulement.
- N'introduit aucun navigateur dans la CI : la capture reste locale et
  déclenchée par l'opérateur ; seul le relevé JSON est comparé en CI.
- Ne teste pas la compatibilité navigateur — Chromium uniquement, parce que
  l'objet mesuré est la géométrie du produit.
- N'autorise jamais la mise à jour d'une baseline pour faire passer un diff.
