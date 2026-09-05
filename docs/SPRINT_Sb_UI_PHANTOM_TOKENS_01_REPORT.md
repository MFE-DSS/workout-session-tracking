# `Sb_UI_PHANTOM_TOKENS_01` — les couleurs que personne n'avait choisies

`CLAUDE.md §5.4` interdit une écriture précise :

> **Interdit** : `var(--token-inexistant, #hex)` — le repli masque l'absence.

Le dépôt en comptait **166 occurrences**. Cette tranche montre pourquoi le
nombre brut ne dit rien, et ce qu'il fallait en extraire.

## 1. Cent-soixante-six replis, dont deux défauts

Le mécanisme est sournois parce qu'il **fonctionne**. Rien ne casse, rien ne
s'affiche en noir : une couleur est peinte. Simplement, ce n'est pas celle de
la palette, elle n'a jamais été mesurée sur le fond réel, et elle vient
souvent d'une génération antérieure du produit.

| | |
|---|---|
| tokens définis dans les feuilles | **134** |
| usages avec repli | **166** sur 40 tokens |
| **replis morts** — le token existe, le repli ne part jamais | **150** |
| **replis vivants** — le token est fantôme, le repli PEINT | **16**, sur 9 tokens |

Lus un par un, ces seize se répartissent en trois familles très différentes —
et la troisième interdit de traiter le lot comme un lot :

**Deux défauts visuels réels.**

* `--success` → `#2e7d32`, mesuré à **3,41 : 1** sur la surface du produit,
  **sous le seuil AA de 4,5 : 1**. C'est le message qui confirme la
  publication d'un programme ;
* `--bg-elev` (×3) → un voile **noir** à 2 %. Sur un produit sombre, un voile
  noir rend l'élément **plus sombre que sa surface**, quand son nom dit
  « élevé ». L'élévation ne se produit pas.

**Six couleurs justes qu'aucun token ne portait** — `--good`, `--bg-soft`,
`--warn-soft`, `--danger-soft`. Elles fonctionnaient. Le défaut n'est pas la
couleur, c'est qu'elle n'existait nulle part : *la palette cible est ce qui est
écrit et mesuré dans la feuille de style, pas un souvenir* (`§5.4`).

**Une non-violation.** `--mf-frames` n'est pas une couleur :
`calc(var(--mf-frames, 1) * 100%)` est le **compteur de cadres** du filmstrip
BodyMap, et `1` est le bon défaut. La condamner aurait cassé le socle
multi-cadres pour satisfaire une règle qui ne la visait pas.

C'est, à l'envers, la leçon consignée sur les findings jumelles : *jamais
adjuger un lot sans lire chacune*. Sur seize « violations évidentes », **deux
étaient des défauts, une n'en était pas une du tout.**

## 2. Le moyen existait — quatorzième occurrence

`--success` n'a jamais existé. Mais **`--ok: #6E9E7A` existe**, dans le bloc
« États sémantiques » de `app.css`, à **5,69 : 1**.

De même, `.trend--up` peignait `var(--good, #4ade80)` — un vert vif venu d'une
autre palette — alors que l'état « bon » du produit s'appelle `--ok`.

Deux couleurs inventées, deux fois, à côté du token qui les portait déjà. C'est
le diagnostic du programme, pour la quatorzième fois : *le produit ne manque
pas de la décision, il manque du moyen de l'appliquer* — et ici le moyen
existait, personne ne l'atteignait.

## 3. Le couple sémantique avait un membre sur trois

`--ok-soft` existait. `--warn-soft` et `--danger-soft` étaient invoqués avec un
repli en dur — et **ce repli venait d'une génération antérieure de la palette**.

Mesuré au navigateur, sur le badge réel de la page réelle :

| Badge | Texte | Fond |
|---|---|---|
| **avant** `moyen` | `rgb(199,123,84)` terracotta | `rgba(224,160,48,.18)` **ambre** |
| **après** `moyen` | `rgb(199,123,84)` | `rgba(199,123,84,.14)` |
| **avant** `faible` | `rgb(184,92,92)` | `rgba(230,80,80,.18)` |
| **après** `faible` | `rgb(184,92,92)` | `rgba(184,92,92,.14)` |

Le fond et le texte ne se répondaient pas. Les deux frères manquants sont
désormais **dérivés de leur propre token**, au patron exact de `--ok-soft`
(alpha 0.14).

## 4. Ce que je n'ai PAS fait, et pourquoi

La dérivation **améliore sans sauver** :

| Couple | Avant | Après | AA |
|---|---|---|---|
| `--ok` sur `--ok-soft` | 4,67 : 1 | 4,67 : 1 | ✅ |
| `--warn` sur `--warn-soft` | 3,85 : 1 | **4,41 : 1** | ⛔ |
| `--danger` sur `--danger-soft` | 3,21 : 1 | **3,42 : 1** | ⛔ |

Atteindre AA demande d'éclaircir `--warn` et `--danger` **eux-mêmes**. Le
remède est calculé, à teinte et saturation constantes :

| Token | Actuel | Calibré | Résultat |
|---|---|---|---|
| `--warn` | `#C77B54` | **`#CF8D6B`** (+0,06 L) | **5,16 : 1** |
| `--danger` | `#B85C5C` | **`#C78080`** (+0,10 L) | **4,68 : 1** |

**Je ne l'ai pas livré.** Ces deux tokens servent aussi de **fond** dans quatre
règles : les éclaircir change le sol sous des textes que je n'ai pas mesurés.
Réparer un couple en dégradant quatre autres est exactement le mode d'échec que
cette tranche combat. C'est un arbitrage de palette — il te coûte un mot, pas
une recherche.

## 5. Le viseur, deux fois

Quatre des seize replis vivants sont dans `session_focus.css` — la feuille du
**viseur intra-séance**, interdit par le mandat. Ils sont **exemptés avec leur
raison écrite**, pas ignorés.

Et le rendu l'a confirmé plutôt que supposé : en injectant le CSS de la tranche
sur une séance en cours, **le viseur ne bouge pas d'un pixel** — aucun des
sélecteurs touchés n'y vit.

## 6. La garde

Elle traque **uniquement les tokens fantômes**. Compter les 150 replis morts
comme des fautes noierait les deux défauts réels dans cent-cinquante
broutilles.

Quatre tests : aucun fantôme non exempté · la sonde reconnaît les deux
écritures de repli (hexadécimal et `var()` imbriqué) · aucune exemption
périmée · chaque exemption porte une raison lisible.

Les deux derniers existent parce qu'une liste d'exemptions sans entretien
devient un cimetière : elle grossit, plus personne ne sait lesquelles mordent
encore, et la première vraie régression s'y glisse sans bruit.

## 7. Relecture du relevé de décisions (`CLAUDE.md §5.2`)

| Décision | Verdict |
|---|---|
| **Q1** · **Q2** · **Q3** · **Q4** · **Q4/DF-C** | non concernées |
| **Q5** — trois rangs de surface | **respectée** : aucun conteneur touché |
| **Q6** — échelle E3 | non concernée — la tranche ne touche aucune taille |
| **Q7** — un seul aplat ambre par écran | **respectée** : aucun aplat ajouté ; `--warn-soft` est un voile à 14 %, pas un aplat de commande |
| **Q8** — aucune opacité décorative | **respectée, et c'est le sujet** : chaque voile devient un token nommé, avec son contraste mesuré sur le fond réel |
| **`§5.3`** jamais une soustraction seule | respectée : rien n'est retiré, quatre tokens sont ajoutés |
| **`§5.4`** toute couleur est un token mesuré | **c'est le motif de la tranche** |
| **`§5.5`** la centralité avant la facilité | respectée : les 150 replis morts (faciles, cosmétiques) sont laissés ; les 2 défauts visuels (difficiles, mesurés) sont traités |

## 8. Vérifications

`check_scope` **SHARED_CODE** · broad sweep ciblé · gardes de la tranche
**4 vertes** · ruff OK · budget OK.

Rendu exposé (`§5.1`) : les deux variantes de badge mesurées au navigateur
avant/après, et la non-régression du viseur constatée au rendu.

## Verdict

**LIVRÉ.** Neuf tokens fantômes : deux défauts visuels corrigés en pointant
vers le token qui existait déjà, quatre couleurs justes enfin déclarées avec
leur contraste, une fausse violation épargnée, trois exemptions écrites avec
leur raison. Et un arbitrage de palette posé, chiffré, prêt à trancher.

## 9. Ce qui reste ouvert

* **`--warn` / `--danger` sous AA** — remède calculé au `§4`, décision opérateur ;
* **150 replis morts** — le token existe, le repli est décoratif. Dette de
  style, pas défaut visuel : à résorber au fil des tranches, jamais en une
  passe globale ;
* **`/body/intelligence` répond 404** derrière son drapeau de fonctionnalité :
  le correctif `--bg-elev` est écrit et mesuré, mais **non vérifié au rendu**
  faute de surface atteignable. Dit explicitement plutôt que passé sous
  silence ;
* **les quatre replis du viseur** attendent son ouverture avec l'opérateur.
