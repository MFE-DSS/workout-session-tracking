# Sb_GATE_TOOLING_NPM_CACHE — un gate local qui ne tombe plus une passe sur deux

**Statut** : ✅ MERGÉE (`62d0367`, closeout en annexe) · **Branche** : `sb/gate-tooling-npm-cache`
**Base** : canonique `8263ea0` · **Commande** : opérateur, 2026-10-26 (« faire tous les R + l'outillage du gate »)
**Périmètre** : outillage LOCAL du gate visuel (`clients/mobile/visual-contract/run.sh`). Le job CI `visual-contract` n'est pas touché.

---

## 1. Brainstorming · Options · Risques · Choix retenu (`CLAUDE.md §3`)

**Le défaut, observé à chaque passe pendant DA-02.4B → DA-02.6** : dans le conteneur épinglé, sur le volume nommé partagé, `npm ci` échouait une passe sur deux (`TAR_ENTRY_ERROR`, fichiers manquants) **tout en sortant en 0** ; l'export échouait ensuite (« No platforms are configured », `expo` absent). Il fallait relancer à la main.

| Question | Options | Choix | Pourquoi |
|---|---|---|---|
| Éviter la réinstallation | toujours `npm ci` · **réutiliser une installation qui correspond exactement au lock** | réutiliser, avec un tampon (`node_modules/.auren-lock`) comparé au lock | la plupart des passes n'installent plus rien : plus rapides, plus de fenêtre pour le défaut |
| Croire `npm ci` | son code de retour · **une vérification `npm ls --depth=0`** | vérifier | le code de retour mentait : c'est le cœur du défaut |
| Réparer | relancer à la main · **réessayer depuis un `node_modules` vidé** | 3 tentatives | une installation partielle ne se répare pas en la complétant |
| Un volume par worktree | séparer · garder le volume partagé | partagé | le tampon compare le lock : deux worktrees au même lock réutilisent la même installation, un lock différent réinstalle |

| Risque | Parade |
|---|---|
| `npm ls` rougit sur une installation saine | prouvé faux : 3 passes vertes, dont 2 sans réinstallation |
| Le tampon cache une installation abîmée | le tampon seul ne suffit pas : `npm ls` est aussi exigé avant de réutiliser ; prouvé par mutation (§3) |
| Le CI change | non : le job CI installe lui-même ; seul le script local change |

## Croquis validé

Sans objet : **aucune surface visible n'est créée ni modifiée**. La tranche ne touche que l'installation des dépendances du gate local ; les 35 baselines restent identiques (prouvé : 36 / 36 sur 4 passes).

## Inventaire — une information, une seule fois

| Élément | Information | Source (contrat de données) | Doublon ? |
|---|---|---|---|
| message « npm ci skipped » / « installed and verified » | l'état de l'installation du gate, pour qui lance `run.sh` | `install-deps.sh` | non (sortie console, aucune interface produit) |

## Comparaison avec la référence validée

| Référence validée | Tranche / date | Ce qui doit survivre | Survit ? |
|---|---|---|---|
| tout le contrat visuel (35 baselines) | DA-GOV-01 → DA-02.6 | chaque baseline, au pixel | **oui** : 36 / 36 à chaque passe |

## Changement unique de l'itération

- Changement : **l'installation des dépendances du gate local est réutilisée, vérifiée et réparée** au lieu d'un `npm ci` aveugle.

## 2. Réalisation

| Fichier | Rôle |
|---|---|
| `clients/mobile/visual-contract/install-deps.sh` | réutilise si le lock correspond **et** `npm ls` passe ; sinon vide le volume, `npm ci`, vérifie, jusqu'à 3 fois ; tampon écrit seulement après vérification |
| `clients/mobile/visual-contract/run.sh` | appelle `install-deps.sh` au lieu de `npm ci` |
| `tests/test_visual_contract_governance.py` | garde : l'installation passe par le script, le lock est comparé, les deux chemins sont vérifiés par `npm ls`, 3 tentatives |

## 3. Vérifications

| Porte | Résultat |
|---|---|
| shellcheck | propre (`run.sh`, `install-deps.sh`) |
| gate local, 3 passes consécutives | **36 / 36 ×3** ; passe 1 « installed and verified (attempt 1) », passes 2 et 3 « npm ci skipped » |
| **mutation : le défaut d'origine planté** (`expo` retiré du volume, tampon intact) | détecté par `npm ls`, réinstallé, vérifié, **36 / 36** — avant ce correctif, ce même état faisait échouer l'export |
| gardes Python | contrat visuel + voisines |

**Verdict :** le gate local ne dépend plus d'un `npm ci` qui ment ; il réutilise ce qui est sain, vérifie ce qu'il installe et répare ce qui ne l'est pas.

---

## Annexe — closeout post-merge

| Élément | Valeur |
|---|---|
| PR | #303, mergée par `--merge --match-head-commit` (head `d8d8705`) sous GO MERGE permanent |
| Commit de merge | `62d03671854358d240b0c9441b0410ea346e6e48` |
| CI de la PR | 11 checks verts, dont `visual contract (DA-GOV-01)` |
| CI canonique (push) | run `40294150299` : 8 jobs sur 8 verts |
| Sonar | gate PR `OK`, 0 fil de revue non résolu |
| Incidents | aucun (la commande de suivi des checks a échoué une fois sans que la CI échoue) |
| Nettoyage | worktree `workout-session-tracking-tool` et branche `sb/gate-tooling-npm-cache` supprimés après ce closeout |
