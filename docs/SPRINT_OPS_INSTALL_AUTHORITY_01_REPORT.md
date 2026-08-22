# `Sb_OPS_INSTALL_AUTHORITY_01` — le lock gouvernait les machines, pas les humains

**Tranche** : `Sb_OPS_INSTALL_AUTHORITY_01` (arbitrages opérateur **A13** et **A14**)
**Branche** : `sb/ops-install-authority-01` · **base canonique** : `c714f36`
**Tier `check_scope`** : `CI_INFRA` → full sweep local **exigé** + CI réelle impérative

---

## 0. Brainstorming / Options / Risques / Choix retenu

*(CLAUDE.md §3)*

### Le défaut, mesuré

`Sb_DEPENDENCY_LOCK_AUTHORITY_01` a fait de `requirements-lock.txt` le contrat
d'installation et converti **les deux consommateurs automatisés** — la CI
(`ci.yml:95`, `:251`) et `scripts/deploy_prod.sh` (`:190`). Il a oublié les
procédures que suit **un humain**.

Mesuré le 2026-08-22, **9 directives vivantes** installaient encore la
déclaration source à plages ouvertes :

| Fichier | Lignes |
|---|---|
| `README.md` | 47 |
| `deploy/CHECKLISTS.md` | 37, 174 |
| `deploy/DEPLOY_OVH.md` | 38 |
| `deploy/README.md` | 27, 200, 210 |
| `docs/SECURITY_BASELINE.md` | 218 |
| `docs/V1_ACCEPTANCE_CHECKLIST.md` | 16 |

Un déploiement suivi à la main installait donc des versions que la CI n'avait
**jamais testées** — le défaut même que le lock existe pour fermer, rouvert par
la porte de derrière. Aggravant : l'en-tête de `regen_lockfile.sh` affirmait
déjà que « CI et `deploy_prod.sh` installent le lock ». C'était vrai, et
insuffisant : la prose décrivait un monde où le chemin humain n'existait pas.

### Options

| # | Option | Verdict |
|---|---|---|
| A | Corriger les 9 lignes | Nécessaire, **insuffisant** — rien n'empêche la 10ᵉ. |
| B | Supprimer le chemin manuel, n'autoriser que le script | **Rejetée pour l'instant.** Le repli manuel sert précisément quand le script est cassé ; le supprimer serait une soustraction (§5.3). |
| **C** | **A + faire du chemin manuel un repli explicite du script + une garde qui balaie tout fichier suivi** | **Retenue.** C'est l'ordre opérateur A13 = A + B lu correctement : le manuel devient un *wrapper*, pas une seconde procédure. |

### La garde a été plantée avant d'être crue

Les cinq nouvelles gardes ont été écrites **puis lancées sur l'arbre non
corrigé**. Elles ont rougi sur les 9 sites réels. Seulement ensuite les
documents ont été corrigés.

Une garde a été prise en flagrant délit dans ce cycle :
`test_a10_the_bcrypt_ceiling_states_its_reason_in_the_source_spec` cherchait
« passlib » n'importe où au-dessus du pin — et **passait**, satisfaite par la
ligne de dépendance `passlib[bcrypt]>=1.7`. Elle mesurait la présence d'un
paquet, pas celle d'une explication. Corrigée : elle exige un **commentaire**.

---

## 1. A13 — une seule autorité d'installation

- Les **9 directives vivantes** installent désormais `requirements-lock.txt`.
- `deploy/CHECKLISTS.md` §1.2 explique **pourquoi** (source spec vs contrat
  d'installation), là où l'opérateur lit.
- `deploy/CHECKLISTS.md` §2.2 déclare explicitement que le chemin manuel
  **tient lieu de `scripts/deploy_prod.sh`** et doit lui rester identique.
- `docs/SECURITY_BASELINE.md` auditait `requirements.txt` avec `pip-audit` :
  auditer des **plages** plutôt que des versions. Corrigé sur le lock, ce que
  la CI fait déjà (`ci.yml:445`).

### Les comptes rendus historiques ne sont PAS réécrits

Cinq documents citent l'ancienne commande dans un récit daté. Les réécrire
falsifierait un compte rendu. Ils sont exclus **nominativement** —
`HISTORICAL_RECORDS` — et une garde vérifie que chaque exclusion désigne encore
un fichier réel, pour qu'un trou ne s'élargisse pas en silence. Un glob sur
`docs/` aurait été plus court et aurait absous `V1_ACCEPTANCE_CHECKLIST` et
`SECURITY_BASELINE`, qui sont vivants.

---

## 2. A14 — bcrypt 5 fermée, et la raison posée où on édite

**PR #7 fermée** ([commentaire](https://github.com/MFE-DSS/workout-session-tracking/pull/7#issuecomment-5379355062)).
Le plafond `bcrypt>=4.0,<5` **existait déjà** dans `requirements.txt` — mais
**sans dire pourquoi**. Le prochain dependabot, ou le prochain humain, l'aurait
retiré de bonne foi.

Il porte maintenant sa raison en commentaire, à côté du pin :

> passlib 1.7.4 sonde bcrypt en interne avec un mot de passe de **255 octets** ;
> bcrypt 5.0 lève `ValueError` au-delà de 72 octets au lieu de tronquer. Le
> backend passlib échoue à se charger et **toute** l'authentification tombe.

Chemin de réouverture : remplacer passlib (chantier auth séparé), **puis**
relever le plafond. Deux gardes tiennent la ligne — la raison en commentaire, et
le majeur du lock < 5.

---

## 3. Vérifications — tier `CI_INFRA`

| Contrôle | Résultat |
|---|---|
| `check_scope` | `CI_INFRA` — full sweep local exigé |
| ruff (fichier touché) | `All checks passed!` |
| `check_ruff_budget` | 281 ≤ 548 |
| `check_spec_protocol` | PASS |
| `test_dependency_lock_authority.py` | 21 → **26 passed** |
| Full sweep local (`scripts/run_ci_pytest.sh`) | *cf. §5* |
| **CI réelle** | **source de vérité impérative** (CLAUDE.md §1) |

---

## 4. Périmètre et non-régressions

- **Aucun changement de version** de quoi que ce soit — `requirements.txt` et
  `requirements-lock.txt` gardent les mêmes pins. Le seul ajout est un
  commentaire.
- **Aucun changement de `ci.yml`** ni de `deploy_prod.sh` : ils installaient
  déjà le lock. La tranche aligne les **documents** sur eux.
- **Aucun test affaibli** — 5 gardes ajoutées, 0 retirée.
- **Aucun secret, aucune migration, aucun déploiement déclenché.**

---

## 5. Note d'honnêteté sur ce qui reste ouvert

Cette tranche ferme la divergence **documentaire**. Elle ne prouve pas que
l'environnement de production actuel corresponde au lock : personne n'a
inspecté le VPS, et je n'y ai pas accès. La prochaine exécution de
`scripts/deploy_prod.sh` alignera l'environnement ; jusque-là,
**l'état réel de la production reste NON MESURÉ**.
