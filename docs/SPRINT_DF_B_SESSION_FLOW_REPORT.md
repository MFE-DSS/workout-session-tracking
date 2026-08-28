# `DF-B` — la console de séance avait un bouton de trop

`OPERATOR_DECISION` — dogfood réel du 26 août · branche `sb/df-b-flow` · base `01af8db`

---

## 1. Le défaut

Trois gestes là où l'intention en compte un :

```
saisir kg + reps  →  taper VALIDER Sx  →  taper PASSER LE REPOS
```

Le domaine dit pourtant **déjà** que la donnée remplie est la preuve du set :
`completed` se dérive de `weight OR reps`, et la case « Fait » a été retirée
pour cette raison précise. L'interface refusait encore de l'admettre. En
dogfood, le tap `VALIDER` est régulièrement oublié — et c'est logique : après
avoir noté la charge et les répétitions, l'acte est mentalement terminé.

Le nouveau contrat :

```
SAISIR → VALIDATION IMPLICITE → REPOS → PROCHAINE SÉRIE
```

---

## 2. Ce qui a changé, et ce qui n'a pas bougé

| | |
|---|---|
| **Validation implicite** | sur `Entrée`/`Done` — une **transition explicite**. Jamais à la frappe, jamais au `blur`. |
| **Reprise** | la ligne de la prochaine série est un **lien natif** vers la même page sans `rest=1` |
| **Sortie à T=0** | le minuteur suit la même URL — les deux chemins mènent au même état |
| **Sortie manuelle** | conservée, **démotée** au ton secondaire |
| **`±15 s`** | inchangé : local à la requête, jamais persisté |
| **Minuteur** | raisonne sur une **échéance**, plus sur un décrément |
| **Marqueur `.substitute-picker__summary`** | replié dans cette tranche, marqueur seul |

**Aucune migration, aucune colonne, aucun nouvel état, aucune prescription de
repos.** Les six états de `console_state` sont inchangés ; `REST_FALLBACK_SECONDS`
reste à 90. Le serveur demeure l'unique autorité de persistance : le JS appelle
`form.requestSubmit(boutonDominant)` — exactement la soumission qu'un appui
aurait produite, avec les mêmes `<input hidden>` des séries déjà faites.

> ⚠ Le formulaire **sérialise toutes les valeurs de la carte**. Un mini-POST qui
> n'enverrait que la série courante effacerait les autres. C'est pourquoi il n'y
> a **aucun endpoint parallèle**, et une garde l'interdit.

### Pourquoi l'échéance, et pas le décrément

`setInterval` n'est pas une horloge. Le navigateur bride les rappels en
arrière-plan, en économie d'énergie, ou quand le fil est occupé. Chaque rappel
manqué devenait **une seconde de repos qui n'a pas existé**, et la dérive
s'accumule d'autant plus qu'on ne regarde pas l'écran. On fixe donc une
échéance et chaque tick ne fait que lire l'heure : un rappel en retard
**corrige** au lieu de dériver. Le retour d'arrière-plan rattrape
(`visibilitychange`).

### Pourquoi la sortie manuelle est démotée et non retirée

Mesuré **au rendu** à 390 px : pendant le repos, l'écran portait **deux
affordances ambre pour une seule intention** — « Commencer S2 » sur la ligne et
`PASSER LE REPOS` pleine largeur juste en dessous. C'est le bouton de trop.

La consigne dit « manual skip remains available » : il reste donc, **au ton
secondaire**, bordé et transparent. Le libellé, lui, **n'a pas bougé** — trois
gardes l'épinglent, et le réécrire aurait été un choix d'écriture que personne
n'a demandé.

---

## 3. Preuve d'exécution

Séquence réelle jouée par un navigateur : échauffements → première série de
travail → `Entrée` → repos → tap sur la ligne → saisie.

| Étape | Chromium | WebKit |
|---|---|---|
| `blur` (sans `Entrée`) | **aucune navigation, aucun repos** | idem |
| `Entrée` | `?active=…&rest=1` · lien de reprise présent · `1:30` | idem |
| repos, +2,6 s | **1:30 → 1:28** | idem |
| tap sur la ligne S2 | repos terminé · **champs saisissables** | idem |
| `−15 s` ×6 | `1:15 → 1:00 → 0:45 → 0:30 → 0:15` puis **sortie automatique** | idem |
| erreurs console | aucune | aucune |

> **Playwright WebKit n'est pas Safari iOS** : même famille de moteur, ni le
> même navigateur, ni le même système.

### Repli sans JavaScript, JS coupé

* le bouton dominant valide → `rest=1` ✅
* le repos est rendu ✅
* le lien de reprise est présent et **fonctionne** → champs saisissables ✅
* les `±15 s` restent masqués — sans JS il n'y a rien à ajuster ✅

---

## 4. Exposition §5.1 — 360 · 390 · 430

Trois états réels, atteints par la séquence et non fabriqués.

| État | 360 | 390 | 430 | CTA |
|---|---|---|---|---|
| échauffement | 3,5 écr | 3,3 | 2,8 | 4 |
| série en cours | 3,5 | 3,2 | 2,8 | 4 |
| **repos** | 3,4 | 3,2 | 2,8 | **3** |

* **0 débordement horizontal** sur les 9 rendus ;
* le lien de reprise est présent dans les trois largeurs de l'état repos ;
* **5 cibles < 44 px**, toutes des `<summary>` (28 px et 39 px de haut) —
  **mesurées, non touchées**. L'ordre porte sur le *marqueur d'affordance*
  du sélecteur de substitution, « no separate redesign » : en changer les
  hauteurs serait précisément la refonte exclue. Consigné pour arbitrage.

---

## 5. Gardes

`tests/test_df_b_session_flow.py` — **18 gardes**, organisées par ce qu'elles
ferment : endpoint parallèle · validation à la frappe ou au `blur` · correction
auto-validée · repos redevenu une porte · minuteur redevenu un décrément ·
repli sans JS disparu · prescription de repos introduite.

Une garde existante a été **resserrée, pas affaiblie** :
`test_the_countdown_is_gated_on_the_server_signal` exigeait que le script ne
fasse **qu'une seule** sélection par attribut. L'auto-validation a légitimement
besoin de la sienne (`[data-session-form]`), sans rapport avec le minuteur. La
garde vise désormais la ligne qui assigne les **racines du minuteur** — ce
qu'elle a toujours voulu protéger — et reste insensible aux sélections voisines.

---

## 6. Fautes de l'agent

Toutes dans l'**instrument**, aucune dans le produit — mais elles m'ont fait
accuser le produit trois fois.

1. **Un clic de test qui perturbait la page.** Ma sonde de `blur` cliquait
   ailleurs à l'écran ; le clic pouvait atteindre un autre contrôle. Elle
   appelle maintenant `blur()` directement.
2. **`wait_for_load_state("networkidle")` retournait avant la navigation.** La
   page était déjà au repos réseau, donc l'attente rendait la main
   immédiatement et je lisais **l'URL précédente**. J'en ai conclu deux fois
   que l'auto-validation ne fonctionnait pas. Elle fonctionnait. Le harnais
   attend désormais la **navigation elle-même**.
3. **Un test qui pressait `Entrée` sur des champs vides** et s'étonnait qu'il
   ne se passe rien — c'était le comportement correct.
4. **Le serveur de lab ne recharge pas Python.** J'ai mesuré une absence de
   classe CSS alors que le gabarit était juste : le processus tournait sur
   l'ancien `console_state`. Les gabarits Jinja se rechargent, pas les modules.

La leçon est la même que celle de la tranche précédente, sous un quatrième
angle : **un instrument non vérifié mesure son propre défaut.** Ici il m'a fait
soupçonner le produit à trois reprises, et la vérification ciblée a chaque fois
montré que le produit était juste.

---

## 7. Vérifications

| Vérification | Résultat |
|---|---|
| `check_scope.py` | **`SHARED_CODE`** |
| `tests/test_df_b_session_flow.py` | **18 passés** |
| Gardes de la console de séance (5 fichiers) | **117 passés** |
| ruff (rapport CI reproduit) | **276 / 276** |
| Full sweep local | *(reporté en closeout)* |

**Aucune couleur introduite** : le ton secondaire réutilise les tokens des
sorties existantes du dock, et la reprise emploie `--accent`, déjà mesuré à
7,26:1 sur `--surface`.

---

## 8. Hors périmètre

* **`DF-C`** — la sémantique visuelle `É`/`S` (microglyphes) : tranche suivante.
* **`DF-D`** — le repos adaptatif : différé par l'ordre, et rien ici ne
  l'anticipe.
* **Les hauteurs des `<summary>`** de l'écran de séance : mesurées, non
  touchées, soumises à arbitrage.
