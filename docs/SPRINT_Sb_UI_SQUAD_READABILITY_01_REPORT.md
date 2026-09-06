# `Sb_UI_SQUAD_READABILITY_01` — la surface sociale rejoint les décisions du produit

Quatre défauts sur un écran, tous du même genre : **une décision existait, et
cette surface ne l'avait pas reçue.** Trois d'entre eux étaient visibles à
l'œil nu au premier rendu.

## 1. Le fil d'activité n'était plus une phrase

Servi à l'écran :

```
marin        recommande        Push A — Pecs épaisseur…        essai de bout en bout
```

Quatre colonnes, sans espaces. Le gabarit, lui, **contient bien les espaces** :

```jinja
<strong>{{ item.username }}</strong> recommande <em>{{ item.template_name }}</em>
```

La cause est dans la feuille. `.stats-list li` vaut
`display:flex; justify-content:space-between` — c'est une ligne **clé/valeur**,
et son `span:first-child` en sourdine le dit. Le fil d'activité l'empruntait
pour de la **prose** : flex a fait de `<strong>`, du texte « recommande » et de
`<em>` trois éléments de flux, les blancs entre eux ont disparu, et
`space-between` les a poussés en colonnes.

**Ce n'est pas une faute de frappe, c'est une classe de mise en page empruntée
pour une forme de contenu qu'elle ne sert pas.** J'ai commis exactement la même
erreur il y a deux tranches, avec `.pd-sessions` — et je l'avais écrite dans la
feuille pour ne pas la refaire.

Balayage de la classe : sur **dix usages** de `.stats-list`, **un seul** est ce
détournement. Les autres sont bien des lignes clé/valeur — vérifiées une par
une au rendu, pas comptées.

## 2. « owner » et « member » atteignaient l'écran

`Sb_UI_SESSION_DONE_01` a fermé ce défaut il y a quelques heures, pour trois
énumérations du récap de séance. **Il l'a fermé là où je regardais.**

Deux gabarits — `squad_detail` et `squads_list` — rendaient encore la valeur
brute de `role`. C'est le mode d'échec consigné sous *une décision appliquée là
où c'était commode*, avec sa signature : **l'oubli tombe sur les surfaces
sociales**.

La clé reste la clé — trois gabarits comparent dessus
(`membership.role == 'owner'`), et la renommer casserait l'autorisation. Seul
l'affichage est traduit, par `SQUAD_ROLE_LABELS`, qui vit **dans le module qui
déclare la colonne** : les séparer garantirait qu'ils divergent.

## 3. « 586.0 pts », à côté d'un « 75,6 kg » correct

Le produit avait tranché d'écrire les nombres en français. Il l'appliquait avec
**trois orthographes différentes** :

```jinja
{{ x | string | replace(".", ",") }}
{{ "%.1f" | format(x) | replace('.', ',') }}
{{ x | round(1) | string | replace(".", ",") }}
```

**Deux des trois viennent de moi**, écrites dans `Sb_UI_SESSION_DONE_01`. Et le
classement de squad n'avait rien du tout.

La décision existait ; le moyen de l'appliquer n'existait pas, donc chacun l'a
réinventé — et le quatrième a oublié. **Seizième occurrence du diagnostic.**

### La garde a trouvé ce que mon balayage avait manqué

J'avais relevé trois occurrences. La garde écrite pour les interdire en a
trouvé **six, sur cinq gabarits** : `coach_report.html` (×2) et
`user_profile.html` n'étaient pas dans mon grep.

C'est le bon sens de l'erreur — une garde qui trouve plus que son auteur est
une garde qui sert. Les six passent désormais par `nombre_fr`.

### Le zéro décimal disparaît, sauf là où il a été mesuré

Le filtre distingue deux cas, et le rendu le confirme sur le récap :

| | avant | après |
|---|---|---|
| poids de corps | `75,6 kg` | `75,6 kg` — **inchangé** |
| delta de charge | `+57,0 kg` | `+57 kg` |
| qualité de séance | `55,0` | `55` |

Un poids de corps s'écrit avec `nombre_fr(1)` : le dixième y a été **mesuré**,
il ne s'escamote pas. Un delta calculé qui tombe juste n'a pas de dixième à
montrer — « +57,0 » promettait une précision que la soustraction n'a pas.

## 4. Un texte blanc sur un aplat vert

`style="background:var(--ok); color:#fff"` — un hexadécimal en dur, mesuré à
**3,07 : 1** sur `--ok`. Sous AA.

Le produit possède déjà la couleur du texte posé sur un aplat : `--on-accent`,
qui rend **6,37 : 1** sur le même fond. Encore le même schéma.

## 5. Ce que je n'ai PAS fait — et qui attend un arbitrage

**Quatre aplats ambre s'affichent simultanément** sur cet écran : « Nouveau »,
« Recommander », « Partager », « Générer un code ». Quatre commandes
souveraines, donc aucune. `Q7` dit « un seul aplat ambre par écran,
strictement ».

Le cliquet ambre enregistre bien `squad_detail.html: 4` — mais **son propre
commentaire dit « ce n'est PAS un compte d'écran »**. Il a gelé la dette sans
la juger, et personne n'avait regardé le rendu. Je l'ai regardé : les quatre
sont bien là ensemble.

**Lequel garde l'ambre n'est pas une correction, c'est un arbitrage** — deux
des quatre sont des boutons de soumission de formulaires ouverts, ce qui est
défendable ; les deux autres sont des commandes de page. Porté au tableau
d'arbitrage plutôt que tranché à six heures du matin.

## 6. Le même trou de garde a mordu deux tranches en une nuit

Le commentaire CSS de cette tranche cite `` `#fff` `` pour expliquer le
contraste corrigé. Les trois gardes anti-hexadécimal du shell l'ont lu comme du
code — **exactement comme elles avaient lu le `#2e7d32` de
`Sb_UI_PROGRAM_EDITOR_STYLES_01`, deux heures plus tôt.**

Deux tranches indépendantes, la même nuit, sur le même trou. Le correctif
(retrait des commentaires, sonde partagée dans `tests/helpers.py`) part avec
`#211` ; cette branche en hérite par la canonique plutôt que de le dupliquer.

## 7. Relecture du relevé de décisions (`CLAUDE.md §5.2`)

| Décision | Verdict |
|---|---|
| **Q1** · **Q2** · **Q3** | non concernées |
| **Q4** — « les valeurs deviennent l'objet » | **respectée** : `owner` est une clé de programme, pas une valeur ; elle recule derrière son libellé |
| **Q4 amendement `DF-C`** | **respectée, et étendue** : le même raisonnement retire la valeur brute du rôle |
| **Q5** — trois rangs de surface | **respectée** : aucun conteneur ajouté ni retiré |
| **Q6** — échelle E3 | **non appliquée, et c'est signalé** : cet écran porte ses titres en `<h2>` à 21 px, hors de la classe `.section-header` promue par `#208`. Le rapprocher demande de décider si un `<h2>` de page est un rang SECTION — pas au détour d'une tranche de lisibilité |
| **Q7** — un seul aplat ambre par écran | **VIOLÉE, constatée, non corrigée** — voir `§5`. Quatre aplats simultanés, portés à l'arbitrage |
| **Q8** — aucune opacité décorative | non concernée |
| **`§5.3`** jamais une soustraction seule | respectée : rien ne disparaît ; deux libellés et un filtre sont ajoutés |
| **`§5.4`** toute couleur est un token mesuré | **appliquée** : `#fff` → `--on-accent`, avec ses deux ratios écrits |
| **`§5.5`** la centralité avant la facilité | respectée : le fil illisible est traité d'abord, la dette d'attributs ensuite |

## 8. Vérifications

`check_scope` **SHARED_CODE** · broad sweep ciblé · gardes de la tranche
**5 vertes** · cliquet des styles inline resserré **20 → 0** sur
`squad_detail.html` · ruff OK.

Rendu exposé (`§5.1`) avant/après sur `/squads/1`, avec les trois corrections
lues dans le DOM plutôt que jugées à l'œil :

| | avant | après |
|---|---|---|
| fil d'activité | `marin ⏎ recommande ⏎ Push A ⏎ ⏎ ⏎ essai…` | `marin recommande Push A — Pecs épaisseur + Delts + Triceps` |
| points | `586.0 pts` | `586 pts` |
| rôles | `owner · member` | `Propriétaire · Membre` |

Hauteur **2,37 → 2,39 écrans** (+0,8 %).

## Verdict

**LIVRÉ.** Un fil d'activité redevenu lisible, deux valeurs d'énumération
sorties de l'écran, six conversions décimales artisanales remplacées par un
filtre nommé, un texte remonté de 3,07 à 6,37 : 1, et vingt attributs `style`
résorbés. Une violation de `Q7` constatée au rendu et portée à l'arbitrage
plutôt que devinée.

## 9. Ce qui reste ouvert

* **les quatre aplats ambre** — arbitrage, voir `§5` ;
* **l'échelle typographique de cet écran** — `<h2>` à 21 px hors de la classe
  promue ; demande de décider ce qu'est un `<h2>` de page ;
* **`squads_list.html`** garde 5 attributs `style` : ils n'étaient pas dans le
  périmètre mesuré de cette tranche, et les traiter au passage aurait élargi le
  diff sans rendu de contrôle ;
* **le tableau de classement est à l'étroit**, vu au rendu : « 586 pts » passe
  sur deux lignes, l'en-tête « Séances 14 j » aussi, et la colonne Grade rend
  une phrase de trois lignes. Six colonnes sur un écran de téléphone. Retirer
  le zéro décimal l'a marginalement soulagé, **ça ne le résout pas** — c'est un
  problème de nombre de colonnes, donc une décision sur ce que le classement
  doit montrer ;
* **le cliquet ambre ne juge pas ce qu'il gèle.** Son commentaire le dit ; son
  nom ne le dit pas. Une garde qui compte par gabarit ne remplacera jamais un
  regard sur l'écran — et c'est précisément ce que `CLAUDE.md §5.1` exige.
