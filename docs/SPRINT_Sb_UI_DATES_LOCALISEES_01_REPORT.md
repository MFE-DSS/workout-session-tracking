# `Sb_UI_DATES_LOCALISEES_01` — la séance de minuit, rangée la veille

## 1. Le défaut, prouvé plutôt que déduit

```
séance réellement commencée : 06/09/2026 à 00 h 30 (Paris)
stockée en UTC              : 05/09/2026 22:30

strftime brut       → « 05/09/2026 »   ← ce que l'écran affichait
strftime | local    → « 06/09/2026 »   ← la vraie date
```

Paris est **en avance** sur UTC. Tout ce qui se passe entre minuit et 01 h ou
02 h locale s'affichait **la veille**. Pour quelqu'un qui s'entraîne tard, ce
n'est pas un détail de fuseau : c'est sa séance rangée au mauvais jour, dans
son export comme dans son profil.

La preuve est **exécutable** — `test_the_defect_is_real_and_this_is_the_case`
la porte. Elle a aussi été rendue à l'écran : sur `/export`, une séance de
labo semée à 00 h 30 heure de Paris affiche `08/08/2026` sur la canonique et
`09/08/2026` sur cette tranche.

## 2. Le motif, pour la quatrième fois aujourd'hui

Le filtre `local` existe dans `templating.py` depuis longtemps. **Trois** sites
l'utilisaient ; **quatorze** ne l'utilisaient pas.

C'est le même constat que `date_fr`, que `select_shell`, que le filtre
`pluriel` : *la pièce existait, elle n'était pas **atteignable** sans la
connaître.* La différence ici est qu'aucune garde ne pouvait le dire — un
`strftime` brut est du code parfaitement valide.

## 3. Brainstorming · options · risques · choix retenu

### Option 1 — `| local` partout où il manque

**Écartée, et c'est le cœur de la tranche.** En vérifiant le type réel de
chaque valeur, 6 des 14 **ne doivent pas** être localisées :

| Site | Type réel | Pourquoi il reste brut |
|---|---|---|
| `readiness_history.html::recorded_on` | `Date` | un état du jour est rattaché à un **jour**, pas à un instant |
| `squad_challenge_detail.html::starts_at` / `ends_at` | `Date` | un défi qui commence le 6 septembre commence le 6 septembre **partout** |
| `squad_challenges.html::starts_at` / `ends_at` | `Date` | idem |
| `export.html::modified_at` | `datetime` **naïf, heure locale** | `fromtimestamp(st_mtime)` **sans `tz`** — le localiser l'avancerait d'une à deux heures |

**Un correctif global aurait cassé six rendus corrects pour en réparer huit.**

### Option 2 — un filtre `date_safe` qui détecte le type à l'exécution

**Écartée.** Il ne peut pas distinguer un `datetime` UTC d'un `datetime` naïf
déjà local : les deux sont des `datetime`. Il devinerait, et un filtre qui
devine sur un fuseau produit une erreur silencieuse d'une heure — pire que
l'erreur d'un jour qu'il corrige, parce qu'invisible.

### Option 3 — corriger les 8, exempter les 6 **avec leur raison**, garder

**✅ Retenue.** Chaque exemption est inscrite dans la garde avec son motif, et
un test vérifie qu'aucune ne dort.

## 4. Le tableau complet

**Corrigés (8)** — colonnes `DateTime(timezone=True)` :

`export.html` × 2 (`first_started`, `last_started`) ·
`profile.html` (`user.created_at`) · `progress.html` (`tk.last_done_at`) ·
`squad_detail.html` × 2 (`item.created_at`, `latest_code.expires_at`) ·
`squads_list.html` (`item.squad.created_at`) ·
`user_programs/list.html` (`program.updated_at`)

**Laissés bruts (6)** — voir le tableau du §3. Chacun porte désormais un
commentaire `⛔ PAS de | local ICI, et ce n'est pas un oubli`, avec sa raison :
sans cela, la prochaine personne « complétera la série » et cassera six
rendus.

## 5. Trois plantations, trois morsures

| Plantation | Garde qui rougit |
|---|---|
| `| local` retiré d'un site corrigé | `every_timestamp_is_localised_unless_exempt`, avec le nom du site |
| `| local` **ajouté** sur un site exempté | `no_exemption_is_stale` — l'exemption ne décrit plus rien |
| une exemption sans motif | `every_exemption_carries_a_reason` |

La deuxième est celle qui manque d'habitude. **Une liste d'exemptions qui ne se
périme pas finit par autoriser des sites qu'elle ne décrit plus** — c'est la
même faille que la ligne de base non serrée du cliquet des styles inline,
livré plus tôt aujourd'hui.

⚠ La troisième garde m'a attrapé moi-même : mes premiers motifs disaient
« colonne `Date` », quatorze caractères, sous le seuil que j'avais fixé. Elle
avait raison — c'est une étiquette, pas une raison.

## 6. Relecture du relevé de décisions (`CLAUDE.md §5.2`)

`docs/DESIGN_DECISIONS_UIV2_SURFACES.md` : **Q1** · **Q2** · **Q3** · **Q4** ·
**Q5** · tokens bleus · interdit du feu tricolore — **aucune n'est concernée**.
La tranche ne touche ni conteneur, ni couleur, ni hiérarchie : elle corrige la
valeur d'une date. Le relevé est relu en entier, et il ne dit rien de ce cas.

## 7. Vérifications

`check_scope` dit **ISOLATED** ; la tranche est traitée en **SHARED_CODE** —
dix gabarits sur cinq surfaces, et `CLAUDE.md §1` demande de remonter d'un cran
en cas de doute.

Gardes de la tranche **4 vertes**, 3 plantations vérifiées · cliquet des styles
inline (mergé ce jour) **vert** malgré les commentaires ajoutés · broad sweep
ciblé *(voir appendice)*.

Rendu exposé (`§5.1`) : `/export` capturé sur **deux serveurs vivants** — la
canonique et la tranche — avec la même donnée et un jour d'écart.

## 8. Trouvaille hors périmètre

`backup_inspector.py:45` calcule `datetime.fromtimestamp(stat.st_mtime)`
**sans** fuseau ; `backup_verifier.py:93` calcule la même chose **avec**
`tz=timezone.utc`. Deux services, la même valeur, deux conventions. L'un des
deux se trompe, et ce n'est pas cette tranche qui doit le trancher.

## Verdict

**LIVRÉ.** Huit dates cessent d'être fausses d'un jour pour les séances de fin
de soirée. Six sites qui devaient rester bruts le restent, documentés, et une
garde empêche autant d'en oublier un que d'en « corriger » un de trop.

**Ce qui reste ouvert** — l'incohérence des deux services de sauvegarde (§8), et
la question de savoir si `modified_at` devrait devenir UTC-aware comme son
jumeau. Signalées, non tranchées.
