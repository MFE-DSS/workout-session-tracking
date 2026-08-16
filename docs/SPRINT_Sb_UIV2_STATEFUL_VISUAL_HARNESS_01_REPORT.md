# SPRINT Sb_UIV2_STATEFUL_VISUAL_HARNESS_01 — la revue visuelle devient un gate (RAPPORT)

**Programme :** `AUREN_UI_V2_PRODUCT_QUALITY_01`, tranche 0/7 ·
**Base canonique :** `bc5103d` · **Branche :** `sb/uiv2-stateful-visual-harness-01`

---

## 1. Pourquoi cette tranche existe

Le train précédent a livré une correction d'accessibilité P0 **sans produire une
seule capture**. Raison exacte : le harnais pilote des **routes**, et les
défauts rapportés par le dogfood vivent dans des **états d'interaction** —
« alternatives ouvertes », « une alternative retenue », « disclosure machine
ouverte » — qu'aucune URL n'atteint.

Tant que c'est vrai, la revue visuelle finale du programme n'a rien à examiner.
C'est donc la tranche 0, pas un préambule.

---

## 2. Contrat de scénario

Une entrée porte désormais deux champs de plus :

```python
actions: tuple[Action, ...] = ()   # gestes après chargement
expect_visible: str = ""           # état attendu ensuite
```

Le vocabulaire d'actions est **fermé et minuscule** :
`click` · `check` · `open_details` · `press` · `wait_for`.

**Aucune évaluation JavaScript arbitraire** n'est un type d'action. Forcer un
état par JS produirait la capture d'un écran que **personne ne peut atteindre** —
une image qui a l'air d'une preuve sans en être une. `Action` refuse un type
inconnu et un sélecteur vide ; un test le vérifie pour chaque type.

`open_details` clique le `<summary>` plutôt que de poser l'attribut `open` : le
geste réel exerce la sémantique native.

---

## 3. `expect_visible` — le garde contre la preuve vide

C'est le point central de la tranche.

Si un geste échoue silencieusement — sélecteur renommé, timing —, la capture
montrerait **l'écran fermé en le faisant passer pour l'écran ouvert**. Le
programme entier reposerait alors sur des images fausses.

`expect_visible` transforme ce cas en **échec bruyant**. Un test le prouve avec
une page simulée qui refuse de rendre le sélecteur attendu : l'exécuteur lève.

---

## 4. Scénarios GOLDEN — la preuve « AVANT »

Quatre entrées gèlent l'état **canonique actuel** :

| Slug | État atteint | Gestes |
|---|---|---|
| `uiv2-session-alternatives-closed` | carte d'exercice par défaut | — |
| `uiv2-session-alternatives-open` | **alternatives dépliées** | `wait_for` + `open_details` |
| `uiv2-profile-preferences` | panneau de préférences | `wait_for` |
| `uiv2-programs-proposal` | proposition hebdomadaire | — |

Elles décrivent ce qui **existe**, pas une cible souhaitée.

**Priorité `P1` délibérément.** Le contrat P0 historique est documenté et testé
comme « 8 slugs × 2 viewports = 16 captures ». Ces scénarios servent un autre
objectif ; gonfler un ensemble dont la **taille est un contrat** aurait forcé la
mise à jour de tests qui n'ont rien à voir. La priorité existante `P1` dit la
chose juste.

**Viewport mobile : 360 × 640**, la baseline déjà présente dans le dépôt — le
brief demande de la préférer plutôt que d'imposer 390 × 844.

---

## 5. Preuves

| Preuve | Résultat |
|---|---|
| Tests dédiés | **20** |
| Balayage harnais visuel complet | **177** |
| Dry-run CLI | les 4 scénarios planifiés |
| Nouveau framework navigateur | **aucun** — Playwright existant |
| Périmètre | **2 fichiers**, aucune dérive |

Aucun test historique n'a été modifié : le contrat P0 est intact.

---

## 6. Limite de cette tranche

**Aucune capture n'est produite ici.** Le harnais sait désormais atteindre les
états ; il faut un environnement avec compte et session de démonstration
(`AUREN_BASELINE_*`) pour exécuter la capture réelle. La tranche livre la
**capacité**, pas les images.

## Verdict

La revue visuelle peut devenir un gate d'ingénierie : les états que le dogfood a
jugés mauvais sont atteignables par des gestes réels, et une capture d'un état
non atteint échoue au lieu de mentir.

Le vrai risque n'était pas d'ajouter des actions — c'était qu'un geste raté
produise une image plausible. C'est ce que `expect_visible` rend impossible.

---

## Closeout (post-merge)

| | |
|---|---|
| PR | **#112** — `--merge --match-head-commit`, **sans** squash / `--admin` / force |
| Merge | **`fbed54b`** |
| CI canonique | run `31958394501` — **succès** |
| Gate Sonar | **`OK`** — 0 bug, 0 smell, 0 vulnérabilité, 0 % duplication |
| Threads / Gitar | **0 / 0** |
| Périmètre final | `scripts/visual_baseline_matrix.py` · `scripts/visual_baseline_capture.py` · tests dédiés |

### Capacité CI (run `31958394501`) — **HEALTHY**, marge regagnée

| Shard | Fichiers | min MemAvailable | min SwapFree |
|---|---|---|---|
| 1 | 83 | 7 137 Mo | 3 071 — intact |
| 2 | 83 | **6 467 Mo** | 3 071 — intact |
| 3 | 83 | 8 662 Mo | 3 071 — intact |

Le shard bas remonte de **5 973 → 6 467 Mo** et repasse au-dessus de 6 Go, avec
une partition parfaitement équilibrée (83/83/83). Manifeste de shards respecté,
`workers=2` — jamais `-n auto`. La règle de capacité du programme est donc
satisfaite pour ouvrir la tranche suivante.

### Incident de forme, consigné sans correction

Le message de commit de cette tranche contient des backticks non échappés que le
shell a substitués : les noms de champ `actions` et `expect_visible` ont été
mangés. Le commit était **déjà poussé**, et la réécriture d'historique publié est
interdite par la consigne permanente — aucun force-push n'a donc été tenté. Le
texte intégral figure dans le corps de la PR #112 et dans ce rapport.
**Règle retenue : pas de backticks dans un message de commit passé au shell.**
