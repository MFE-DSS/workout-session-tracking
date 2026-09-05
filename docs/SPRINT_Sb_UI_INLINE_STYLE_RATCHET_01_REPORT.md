# `Sb_UI_INLINE_STYLE_RATCHET_01` — un invariant que rien ne regardait

## 1. Le constat

`docs/strategy/AUREN_VISUAL_BACKBONE.md §5` range cet invariant parmi les
**non négociables**, au même rang que la cible tactile 44 px et le
fonctionnement sans JavaScript :

> **Aucun style inline statique non contracté** — l'inline ne survit que pour
> une valeur réellement dynamique, allowlistée. Mesuré : **5 sur 708**.

Le « 5 » est **exact**, et cette tranche le vérifie : cinq `width: N%` calculés,
dans `coach_report.html` et `dashboard.html`, qui ne peuvent effectivement pas
vivre dans une feuille de style — une largeur de barre dépend de la donnée.

Ce qui manquait, c'est le reste de la phrase.

| | |
|---|---|
| styles inline **dynamiques** | **5** — conformes |
| styles inline **statiques** | **328** |
| gabarits concernés | **38 sur 65** |
| gardes qui les comptaient | **0** |

Les cinq plus chargés : `user_programs/detail.html` (31) ·
`_partials/home_coaching_loop.html` (25) · `_partials/session_review.html` (23) ·
`body_assessment/body_overview.html` (21) · `squad_detail.html` (20).

**Un invariant déclaré non négociable qu'aucun test ne regarde n'est pas un
invariant, c'est une intention.** C'est une sixième forme à ajouter au relevé
des gardes qui ne gardent rien : non pas une garde qui ne mord pas, mais une
règle qui n'a jamais eu de garde.

## 2. Brainstorming · options · risques · choix retenu

### Option 1 — résorber les 328 d'un coup

**Écartée.** Chaque suppression change un rendu : `style="font-size:12px;"`
retiré d'un `.text-dim` fait passer le texte de 12 à 14 px. Trois cent
vingt-huit changements de rendu dans une tranche, c'est exactement ce que
`CLAUDE.md §5.1` interdit — aucun d'eux ne serait exposé sérieusement.

### Option 2 — un budget global, comme le budget ruff

**Écartée.** Un total autorise un gabarit à empirer pendant qu'un autre
s'améliore. La dette n'est pas fongible : elle est localisée, et sa résorption
se fait par surface.

### Option 3 — un cliquet par fichier, puis résorption au fil des tranches

**✅ Retenue.** Le cliquet gèle la dette gabarit par gabarit et interdit qu'elle
grossisse. Chaque tranche qui touche une surface fait baisser son entrée, et le
diff le montre.

### Le risque, et comment il est traité

**Une ligne de base qui rote.** Si résorber n'oblige pas à serrer, la ligne de
base garde des valeurs périmées, et six mois plus tard elle **autorise une
régression silencieuse** vers un état déjà quitté.

L'égalité est donc **stricte dans les deux sens** : descendre sous la ligne de
base échoue aussi, avec un message qui dit quoi écrire. C'est le seul choix qui
rend le cliquet auto-entretenu.

## 3. Trois plantations, trois morsures

| Plantation | Message rendu |
|---|---|
| un `style=` ajouté | `science.html : 4 → 5` |
| un `style=` retiré sans serrer | `science.html : 4 → 3` + où serrer |
| `style='…'`, forme que la sonde ne lit pas | `des attributs style échappent à la sonde` + ligne |

**La troisième est celle qui compte.** Une garde aveugle à une forme
d'attribut compte juste et conclut faux — le pire des deux mondes, puisqu'elle
donne une confiance qu'elle ne mérite pas.
`test_the_probe_sees_every_form_of_the_attribute` fait que la sonde **se dénonce
elle-même** quand elle devient incomplète.

Une quatrième garde vérifie que le **chiffre du socle** et le code ne divergent
pas. Un document qui ment sur un invariant est pire que pas de document.

## 4. Ce que la garde ne compte pas, et pourquoi

Les commentaires Jinja sont retirés **avant** la recherche. `history.html` et
`index.html` documentent en commentaire des styles inline qu'ils ont **retirés** ;
les compter ferait rougir la garde sur la prose qui explique qu'on a bien fait
le travail. Le motif s'est présenté **neuf fois** dans ce dépôt.

## 5. Vérifications

`check_scope` **ISOLATED** · ruff **OK** · pré-scan Sonar `S9073` / `S1192` /
`S1764` **vide** · `check_spec_protocol` **OK** · sweep ciblé **1 061 tests
verts**.

**Aucun gabarit n'est modifié** : le diff est de deux fichiers de test et d'un
rapport.

## Verdict

**LIVRÉ.** L'invariant `§5` du socle a désormais une garde. La dette de 328
styles inline statiques est **gelée et localisée**, la conformité des 5
dynamiques est **vérifiée**, et le chiffre annoncé par le socle ne peut plus
diverger du code sans qu'un test le dise.

**Ce qui reste ouvert** — la résorption elle-même. Elle se fera surface par
surface, chaque tranche UI faisant baisser l'entrée du gabarit qu'elle touche.
Rien n'est corrigé ici, et c'est délibéré : 328 changements de rendu dans une
tranche ne pourraient pas être exposés sérieusement à l'opérateur.
