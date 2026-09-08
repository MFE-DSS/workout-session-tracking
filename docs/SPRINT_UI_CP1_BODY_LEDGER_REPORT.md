# UI-CP1 — BODY_LEDGER, le premier cockpit de production

**Tier `check_scope`** : `SHARED_CODE`.
**Question souveraine** : *que sait AUREN de mon corps ?*
**Périmètre** : l'expérience d'information corporelle de `/profile`.

---

## 1. BEFORE / AFTER — mesuré, même labo, même sélecteur

Les deux colonnes décrivent **le même utilisateur** avec **le même
sélecteur**. C'est la correction imposée par la cinquième récidive de
`lab-must-be-representative-first` : un « avant » mesuré sur un profil vide
flatte toujours la proposition.

L'« avant » est rendu depuis le worktree `-close`, dont `profile.html` et
`app.css` sont **identiques au canonique** `d378937` (`git diff` vide sur ces
deux fichiers). Sa route calcule encore les clés retirées par CP-0, mais le
gabarit ne les lit pas : le rendu est le même, donc la mesure est valide.

| Profil peuplé | avant | après |
|---|---|---|
| écrans à 390 px | 2,49 | **2,13** |
| régions encadrées | 4 | **0** |
| mots | 240 | **227** |
| commandes visibles | 5 | 5 |
| champs au repos | 1 | 1 |

| Profil partiel | avant | après |
|---|---|---|
| écrans | 2,12 | **1,76** |
| régions encadrées | 4 | **0** |
| mots | 178 | **142** |
| commandes visibles | 6 | **7** |
| champs au repos | 1 | 1 |

| Profil vide | avant | après |
|---|---|---|
| écrans | 1,75 | **1,34** |
| régions encadrées | 4 | **0** |
| mots | 99 | **75** |
| commandes visibles | 10 | **7** |
| champs au repos | 1 | 1 |

**Blocs perçus : 8 → 4 couches** (RÉPONSE PRIMAIRE · RELEVÉ · CONTEXTE ·
APPROFONDISSEMENT), portées par 5 étiquettes de bande.

### Deux chiffres que je ne peux pas revendiquer, et il faut le dire

**Les commandes ne baissent presque pas**, et elles MONTENT d'une unité sur le
profil partiel. Le gain de cette tranche est structurel — cartes, hauteur,
mots — pas une réduction de commandes. Annoncer autre chose serait faux.

**« 45 champs au repos → 0 » reposait sur une mesure fausse, la mienne.** Le
compteur du programme utilisait `getBoundingClientRect()`, qui rend un
rectangle NON NUL pour le contenu d'un `details` fermé sous Chromium
(`content-visibility: hidden`). Il annonçait 18 champs au repos sur `/profile`
là où l'écran en montre **un**. Avec `checkVisibility()`, l'avant valait déjà
1 : la ligne de base du programme était gonflée, et la cible « → 0 » a été
calculée dessus. **Ce n'est pas un gain de cette tranche, c'est une correction
de sa propre métrique.**

---

## 2. Capacités PRÉSERVÉES

Aucune n'est perdue. Vérifié par test, pas par relecture.

| Capacité | Où elle vit maintenant |
|---|---|
| noter son poids du jour | inchangée, au repos, sur la réponse primaire |
| saisie morphométrique complète (14 champs) | tiroir « Mettre à jour mes mesures » |
| e-mail / taille / FC repos | tiroir « Données de référence » |
| changer son mot de passe | tiroir « Compte » |
| identité, e-mail, date d'inscription, statut | tiroir « Compte » |
| découverte de Body Intelligence | bande « Lecture corporelle », visible |
| avertissement de dates mêlées | bande « Portée » |
| limite « ne modifie pas encore ton programme » | bande « Portée », **désormais inconditionnelle** |
| lectures morphologiques | bande « Portée » |
| association libellé ↔ valeur pour lecteur d'écran | `dt` / `dd` natifs |
| écrivain canonique unique sur `body_measurements` | inchangé |

---

## 3. Capacités DÉPLACÉES

**Le compte sort de l'instrument.** Il ne répond pas à « que sait AUREN de mon
corps ? », et il occupait pourtant une carte de premier plan avec un
`h2.section-header` à 22 px — **typographiquement plus fort que le titre de la
carte « Corps » juste au-dessus**. L'identité criait plus fort que le corps sur
la surface corporelle du produit.

Il ne déménage pas vers une autre route, et c'est **mesuré** : la coque n'a
aucune destination « compte » — `/profile` **est** cette destination, 4ᵉ item
du rail. Il devient donc un tiroir du bas de page. `CLAUDE.md §5.3` est tenu :
la soustraction et son remplacement partent dans la même livraison.

**Le protocole de mesure** (« mesurer le matin, à jeun… ») descend dans le
tiroir qu'il explique, au lieu d'introduire une carte au milieu de la page.

---

## 4. Objets RETIRÉS ou FUSIONNÉS

| Objet | Sort |
|---|---|
| carte « Corps » | **fusionnée** dans la réponse primaire + le relevé |
| section « Compte » | **déplacée** en tiroir |
| carte « Nouvelle mesure » | **fusionnée** dans son tiroir |
| section « Mesures morphologiques » | **fusionnée** — devient une bande du relevé |
| carte « Données de référence » | **fusionnée** dans son tiroir |
| carte « Lecture corporelle » | **aplatie** en bande |
| `card__actions` (mot de passe) | **déplacé** dans le tiroir Compte |
| tableau à 3 colonnes | **remplacé** par un relevé `dl` |
| ligne « Morphologie · N mesures » | **retirée** — le relevé montre chaque fait, un compte serait redondant |
| 17 attributs `style` | **retirés** — cliquet resserré 17 → 0 |

---

## 5. Comportement de confiance des données

Le contrat est appliqué par régime, pas uniformément — c'est là qu'il gagne
son utilité.

| Régime | Donnée | Rendu |
|---|---|---|
| OBSERVATION | poids | `78.4 kg` · « Pesé il y a 2 j » |
| OBSERVATION | tours morphologiques | `104.0 cm` · « mesure directe · il y a 28 j » |
| RÉFÉRENCE STABLE | taille | `180.0 cm` · « Donnée de référence · profil » — **aucun âge** |
| DÉRIVÉ | ape index | `8.0 cm` · « envergure − taille · dérivé » — pas d'âge propre |
| **INCONNU** | FC repos | `58 bpm` · *« profil · date inconnue »* |
| ABSENT | tout manque | « Non renseigné », jamais une valeur neutre |

**`users.resting_hr` est un `Integer` nu : le schéma n'a PAS de colonne de
date.** Ce n'est pas un oubli d'horodatage, c'est une impossibilité — donc
l'inconnu se dit, il ne se maquille pas.

**Ce que la tranche rend enfin lisible.** Le produit affichait déjà « ces
valeurs sont prises à des dates différentes » et refusait de chiffrer
lesquelles. Sur le profil peuplé, on lit maintenant côte à côte « Tour de
taille · il y a 5 j » et « Tour de poitrine · il y a 28 j ». L'affirmation et
sa preuve sont sur le même écran pour la première fois.

**Aucun verdict de péremption.** Aucune couleur d'alerte ne se pose sur une
donnée ancienne : aucun seuil de validité corporelle n'existe dans ce dépôt, et
emprunter ceux de `recovery_contract` — qui portent sur la récupération
d'entraînement — aurait été inventer une règle en la déguisant en réemploi.
L'implémentation de référence écrite en amont posait un ambre sur la ligne la
plus ancienne : **il a été retiré**.

**Un seul propriétaire d'action.** L'ambre plein ne se pose que sur « Noter ».
Cliquet ambre inchangé à 1.

---

## 6. Preuve visuelle au runtime

`RUNTIME_MEASURED` — Playwright/Chromium, labo semé, **trois états de données ×
deux tailles**, `/profile` rendu et photographié en pleine page.

Le labo sème le **cas discriminant** : trois relevés à trois dates, dont un qui
ne porte que le tour de taille — sans lui, `is_mixed_date` ne bascule pas et
l'instrument n'aurait pas été éprouvé sur ce pour quoi il existe.

Aucun débordement horizontal sur aucun des six rendus.

---

## 7. Régressions trouvées PENDANT le dogfood

Aucune n'est déduite du code : chacune vient d'un rendu ou d'une plantation.

| # | Défaut | Comment il est apparu | Correctif |
|---|---|---|---|
| 1 | **`.link` n'a AUCUNE règle CSS** dans toute la feuille — `a` vaut `color: inherit; text-decoration: none`. « Voir Body Intelligence → » se rendait en texte ordinaire, indiscernable de la prose. Classe posée sur 3 gabarits | capture 390 px | `.link` écrite : `--fg` + soulignement |
| 2 | **`.stat-add` n'existait que sous `.stats-list`** — posée ailleurs, ni ambre, ni soulignement, ni cible 44 px | capture 390 px | règle autonome, identique à celle en liste |
| 3 | **Le script d'amélioration progressive était INERTE depuis TRAIN 2** — ses trois points d'accroche vivent dans `user_programs/plan.html`, qui ne le chargeait pas ; `profile.html` le chargeait sans en porter un seul | découvert en retirant la balise morte | script déplacé sur `plan.html`, garde retargetée |
| 4 | **Filets de séparation cassés** — la gouttière de grille empêchait les deux bords de se rejoindre | capture 390 px | `column-gap: 0` + `padding-right` |
| 5 | **`dd` hérite `margin-left: 40px`** du navigateur — provenance décalée sous sa valeur | capture 390 px | remise à zéro explicite |
| 6 | **Lignes étirées sur ~1400 px en desktop** — l'œil perd l'appariement libellé↔valeur | capture 1280 px | `max-width: 760px` |
| 7 | **Ma bande ABSENT réintroduisait les sept façons de dire la même absence** que la décision UX4_01 avait bannies | garde `test_a_new_user_sees_the_surface…` | énumération seulement quand elle DISCRIMINE |
| 8 | **La bande « Portée » disparaissait sur un profil vide**, emportant la limite que le produit s'impose | garde | bande rendue inconditionnellement |
| 9 | **Mon compteur de champs au repos surcomptait × 18** | contradiction capture / chiffre | `checkVisibility()` |
| 10 | **Mon compteur de cartes surcomptait 9 pour 4** — `[class^="card"]` attrape `card__title` | relecture après le piège documenté par le dépôt | comptage par jeton de classe |
| 11 | **Ma passe desktop a photographié l'écran de CONNEXION et l'a chiffré** — 429 du limiteur, que j'avais conclu inexistant depuis un grep sur le mauvais fichier | assertion d'identité de page ajoutée | `RATE_LIMIT_ENABLED=0` au labo |

---

## 8. Gardes converties — moyen → capacité, aucune supprimée

Sept gardes épinglaient une **écriture** de l'ancienne ontologie. Aucune n'est
supprimée ; chacune est réécrite sur la **propriété** qu'elle prétendait tenir,
et **chacune a été vérifiée en replantant son défaut d'origine**.

| Garde | Épinglait | Vérifie désormais |
|---|---|---|
| `test_the_profile_opens_on_what_auren_knows` | `count('class="pstate') >= 3` — **trois domaines**, soit l'ontologie que BODY_LEDGER défait | la réponse primaire précède tout formulaire de l'instrument |
| `test_every_acquisition_form_sits_behind_an_explicit_update` | jeton `pstate__edit`, qui n'a jamais eu une ligne de CSS | l'**imbrication** : tout formulaire d'acquisition s'ouvre à profondeur ≥ 1 |
| `test_no_acquisition_form_is_open_by_default` | deux écritures exactes autour d'un jeton disparu | **aucun** `details` ouvert, quel que soit l'ordre des attributs |
| `test_every_state_section_is_flat` | tolérait UNE carte d'état | **aucune** région encadrée |
| `_section` (31 gardes du read-model) | découpe depuis un titre de carte | l'instrument entier — **sur-ensemble strict** |
| `test_no_forbidden_wording_…` | un seul bloc | la page entière |
| `test_the_enhancement_script_…` | le mauvais gabarit, et restait verte | le gabarit qui porte les points d'accroche |

Deux gardes **se resserrent** (`>= 1 carte` → `0`, comptage → imbrication) ;
quatre **élargissent leur champ**. Une garde **neuve** remplace la capacité
d'accessibilité que portait le tableau retiré :
`test_each_measured_fact_is_associated_with_its_value`.

### Le trou qu'une plantation a révélé

`disclosures >= acquisition` comparait deux **totaux**, donc ne disait rien sur
l'imbrication : le tiroir « Compte », sans formulaire, payait pour un
formulaire resté à découvert. **Mesuré** : en sortant le formulaire de données
de référence de son tiroir, la garde restait VERTE. Elle vérifie désormais la
profondeur.

### Deux accusations que j'ai portées à tort, et vérifiées à la main

Trois gardes sont d'abord restées vertes sous plantation. **Deux étaient mes
mutations qui ne mutaient rien** : l'une renommait `bl-answer__readout` en
`bl-answer__readout_X`, que `str.index` retrouvait par préfixe ; l'autre visait
la bande MESURÉ, non rendue pour l'utilisateur nu du test. Contester chaque
réfutation a sauvé deux gardes correctes — et laissé la seule vraie.

---

## 9. Vérifications

| Contrôle | Résultat |
|---|---|
| `check_scope` | `SHARED_CODE` |
| `ruff` (fichiers touchés) | 1 `E402` **préexistant** (l. 54), aucun ajouté |
| `check_ruff_budget` | 267 ≤ 548 — **inchangé** |
| `check_spec_protocol` | OK |
| `test_profile_query_budget` | **6 passés** — budget strict à **5**, inchangé : zéro requête ajoutée |
| `test_no_new_inline_style` | vert après resserrage **17 → 0** |
| `test_one_amber_fill_per_screen` | vert, cliquet à **1** |
| `test_morphology_readmodel` | **45 passés** |
| `test_ux4_profile_acquisition` | **20 passés** |
| Hygiène de surface, coque, cibles tactiles | **166 passés** |
| **Broad sweep ciblé** (profil · morpho · ux4 · train1/2 · visuel · coque · plan · corps · cliquets · cibles · dépliants · préférences) | **1 932 passés · 0 échec** en 6 min 16 |
| **7 défauts replantés** | **7 gardes rouges** |
| Arbre restauré après plantation | à l'identique |

---

## 10. Ce que la tranche ne fait PAS

Conformément à `§8` de la directive : aucune recommandation de surcharge ne
change · CP-3 n'est pas ouvert · aucune prescription de séance n'est touchée ·
la lignée temporelle CP-1 est intacte · le viseur intra-séance n'est pas
approché · aucune disponibilité, aucun programme actif, aucune durée planifiée
n'est inventé.

**Hors périmètre, nommé, non traité** :

* **`POST /profile/measurements` n'a aucune vérification de consentement**, là
  où toutes les routes `/body/*` l'exigent. C'est une décision produit sur le
  périmètre du consentement, pas une décision de cockpit.
* **`update_measurement` remet à `NULL` les champs absents** — contrainte dure
  sur la future capture guidée.
* **Le titre de page reste « Profil »**, nom de la destination dans le rail.
  Renommer l'entrée du rail est un changement de coque, hors périmètre.
* **`.link` n'est écrite que maintenant** : son troisième usage, hors de cette
  surface, en bénéficie aussi.

---

## 11. Closeout

**Mergé** — PR **#226**, méthode `--merge` épinglée sur son head
(`--match-head-commit de0cfdce`), le 2026-09-07 à 13:10 UTC.

| | |
|---|---|
| commit de merge | `cd4a04ce654f50f36757e0bb1d07fb95bb6dee4b` |
| canonique | `d378937` → **`cd4a04c`** |
| checks PR | **10/10 `pass`**, dont le gate externe requis `SonarCloud Code Analysis` |
| gate Sonar (autorité) | **`OK`** sur ses cinq conditions |
| threads de revue non résolus | **0** |
| `mergeable` / `mergeStateStatus` | `MERGEABLE` / `CLEAN` au moment de l'appel |
| **CI canonique** (source de vérité) | run `34125868186` sur `cd4a04c` — **`success`, 7/7 jobs** : lint · attestation · 3 shards pytest · pytest+QA · SonarCloud |

### Gate Sonar, condition par condition

| Métrique | Seuil | Mesuré |
|---|---|---|
| `new_coverage` | ≥ 80 | **100,0** |
| `new_duplicated_lines_density` | ≤ 3 | **0,0** |
| `new_bugs_severity` | ≤ 9 | **0** |
| `new_code_smells_severity` | ≤ 14 | **0** |
| `new_vulnerabilities_severity` | ≤ 9 | **0** |

Le gate est vert **sur ses cinq conditions**, pas seulement « pas rouge ». La
couverture du nouveau code à 100 % reflète que la tranche part avec ses gardes
plutôt qu'après.

### Exposition visuelle — ordre non conforme, dit explicitement

`CLAUDE.md §5.1` exige le rendu **avant tout commit** touchant un gabarit ou
une feuille de style. Les rendus ont bien été produits — trois états × deux
tailles, au runtime — et ils ont trouvé **six des onze défauts** de la §7. Mais
ils ont été soumis à l'opérateur **après le commit local**, avant le push et le
merge. L'arbitrage a donc eu lieu, l'ordre non. Consigné plutôt que lissé.

### Nettoyage

Fait sur `GO CLEANUP` opérateur. **10 worktrees mergés et propres supprimés**
avec leurs branches locales, plus la branche distante du sprint. L'arbre
principal, resté **20+ commits en retard**, a été remis sur le canonique — le
piège que ce dépôt paie en boucle.

Deux branches ont refusé `-d` pour cette raison même ; vérifiées par
`merge-base --is-ancestor` contre le canonique **réel** avant tout `-D`.

⚠ **Le nettoyage a failli détruire `AUREN_CRITICAL_PASS.md`** — 483 lignes,
statut `NORMATIF`, écrites sur direction d'opérateur, non commitées depuis une
journée. Versionné avant suppression du worktree, avec un état d'exécution
daté. Zéro ligne perdue, vérifié par diff.

---

## 12. ⚠ Ce que cette tranche a livré SANS ses gardes — corrigé par #227

**Trouvé au nettoyage, pas à la relecture.** En inspectant `-fresh` avant de
le supprimer, j'ai constaté que le canonique ne contenait **aucun test** de la
substance livrée ici.

Les gardes d'`UI-CP1` vérifiaient la **structure** — association `dt`/`dd`,
zéro carte, zéro tiroir ouvert, la réponse avant le formulaire. **Aucune** ne
vérifiait que l'âge atteint un œil, que l'inconnu se dit, que l'horodatage
naïf de SQLite ne fait pas tomber la page, ni que `as_of` gouverne
l'ancienneté.

C'est le mode d'échec que ce dépôt catalogue depuis des semaines, commis sur
la tranche qui le documentait.

**PR #227 — huit gardes**, toutes exerçant le produit :

| Garde | Ce qu'elle empêche |
|---|---|
| l'âge d'un fait atteint la page | le retour du défaut d'origine |
| le poids porte le sien | la seule clé ajoutée à la route, la moins gardée |
| **les trois régimes ne se confondent pas** | traiter observation, référence stable et inconnu à l'identique — ce qui détruit l'information apportée |
| **aucune couleur d'alerte sur l'ancienneté** | le retour de l'ambre-sur-la-plus-vieille, interdit faute de seuil corporel |
| le dérivé se dit dérivé | « date inconnue » sur l'ape index serait faux |
| l'horodatage naïf | la page tombait en 500 — gardé au niveau unitaire **et** page |
| `as_of` gouverne | un profil rejoué mentirait sur la seule chose ajoutée |
| provenance et âge = **un seul fait** | la quatrième colonne, réfutée par le rendu à 390 px |

**Une garde héritée était fausse** : `assert _age(...) == "hier" or "j" in
_age(...)`, dont la seconde branche est vraie pour « il y a 2 j », « il y a
30 j » **et** « il y a 3 mois ». Elle ne pouvait pratiquement pas échouer.
Valeurs exactes désormais.

### Le gate Sonar rouge, et ce qu'il a appris

Première passe : **`new_code_smells_severity` 15 contre un seuil de 14**, dix
autres checks verts. Une seule finding — `python:S9073` MAJOR, et **un MAJOR
pèse 15** : il dépassait le seuil à lui seul.

`assert rendu and "il y a" in rendu` ne disait pas, à l'échec, si l'ancienneté
était **absente** ou **mal formatée** — les deux défauts que la garde prétend
distinguer. Sonar avait raison sur le fond, pas seulement sur la forme.

La ligne venait de l'implémentation de référence, **reprise sans être relue**,
et le pré-balayage AST que ce dépôt prescrit pour S9073 / S5863 / S1192 n'avait
pas tourné. Il tourne désormais avant push.

| | |
|---|---|
| merge | `29e8deead470727b0eb4cfd4e0a8f973a44eb05d` |
| checks | **9/9 pass**, gate Sonar `OK`, `new_code_smells_severity` **15 → 0** |
| CI canonique | run `34226508102` — **success, 7/7** |
| replantation | **8 défauts → 8 gardes rouges**, avant ET après le correctif Sonar |

### Suite

**UI-CP2 SESSION_TRUST** — non commencé, conformément à la directive.
