# `Sb_UI_HOME_WEEKLY_01` — la carte de l'accueil dit au lieu de compter

## 1. Le constat

La carte « Semaine planifiée » de l'accueil rendait, en ligne souveraine à
16 px gras :

```
4 séances proposées
Prochaine séance proposée
  · Dos largeur — Traction assistée machine
  · Pectoraux — Chest Press machine
  · Biceps — Curl EZ-bar debout
  · Ischios / Fessiers — Romanian Deadlift barre
  · Deltoïdes latéraux — Élévations latérales haltères
  · Quadriceps — Leg extensions assises
```

**306 px** — un tiers d'écran — dont la ligne la plus grosse est un
**comptage**, tandis que la substance qui l'accompagne, déjà présente dans la
charge utile, tient en 13 px sous un intertitre.

Même inversion que sur `/plan`, un rang plus bas. C'est la douzième instance du
motif : *le produit ne manque pas de la donnée, il manque du moyen de la
promouvoir.*

## 2. Brainstorming · options · risques · choix retenu

Trois variantes rendues **sur la page réelle** et soumises à l'opérateur :

| | Forme | Hauteur | Verdict |
|---|---|---|---|
| **D** | zones en tête, tout conservé | 277 px | écartée — ligne souveraine sur 3 lignes, dispute le hero |
| **E** | D + le fil des séances 2 à 4 | 356 px | écartée — la plus haute, sur un écran déjà à 1,95 écran |
| **F** | 3 zones + « +3 », exercices renvoyés à `Mon plan` | **153 px** | ✅ **retenue** |

### Le risque, nommé avant l'arbitrage

**F est la seule variante qui RETIRE quelque chose de cet écran** — les noms
d'exercices. `CLAUDE.md §5.3` interdit une soustraction seule ; ici elle ne
l'est pas :

* ce qui la remplace part **dans la même livraison** — les zones deviennent la
  ligne souveraine ;
* les noms d'exercices ne disparaissent pas du produit : `Mon plan` les rend,
  et **les rend mieux**, depuis sa refonte mergée ce matin (PR #198).

Le risque a été **écrit dans l'option** soumise à l'opérateur, pas découvert
après. Il a tranché F en le sachant.

### Pourquoi la carte doit rester basse

Le service le dit lui-même : *« CONTEXTE hebdomadaire, à côté de la décision du
jour — il ne la remplace pas »*. Le hero porte la décision à 24 px. La ligne
souveraine de la carte est à **17 px**, sous ce rang : deux objets au même rang
se disputeraient le premier regard.

## 3. Ce qui est calculé, et ce qui ne l'est pas

Aucun calcul neuf. `upcoming.slots` portait déjà zone et exercice. Le service
en dérive deux champs :

```python
"next_session_zones": tuple(dict.fromkeys(
    s.zone_label for s in slots if s.zone_label
)),
"next_session_exercises": len(slots),
```

**Dédupliqué** : une séance peut travailler deux fois la même zone, et
« Pectoraux · Pectoraux » gaspillerait un tiers d'une ligne qui n'en compte que
trois. `dict.fromkeys` préserve l'ordre du plan, qui est celui de la séance.

`next_session_slots` est **remplacé**, pas conservé : une charge utile que rien
ne rend est exactement le défaut corrigé partout ailleurs aujourd'hui. Aucun
test ne le consommait — vérifié avant.

## 4. Six styles inline partent avec la refonte

Le cliquet livré une heure plus tôt (`Sb_UI_INLINE_STYLE_RATCHET_01`) a **servi
immédiatement**, et exactement comme prévu.

En retirant les six `style="…"` de cette carte, il a **refusé de laisser passer
l'amélioration en silence** :

```
dette RÉSORBÉE mais ligne de base non mise à jour.
  _partials/home_coaching_loop.html : 25 → 19
```

C'est le comportement pour lequel l'égalité stricte **dans les deux sens** avait
été choisie : une ligne de base qu'on ne resserre pas rote, et finit par
autoriser un retour vers un état déjà quitté. **328 → 322**, première
résorption.

Le nettoyage part **avec** la refonte, pas dans une tranche séparée : rouvrir le
même gabarit deux fois coûte deux expositions `§5.1` pour un seul changement
visuel.

## 5. Deux plantations, deux morsures — et une faute dans ma garde

| Plantation | Garde qui rougit |
|---|---|
| le comptage remis devant les zones | `the_zones_are_the_sovereign_line_not_the_count` |
| un `style="margin:0"` remis dans la carte | garde locale **et** cliquet global (`19 → 20`) |

⚠ **Ma garde s'orientait sur ce qu'elle effaçait.** `test_the_card_carries_no_inline_style`
délimitait le bloc entre `home-wk` et le commentaire `{# ── This week ── #}` —
or `_corps()` retire les commentaires Jinja **avant** de chercher. L'ancre
disparaissait avec eux, et la garde échouait sur un gabarit sain.

Une garde ne peut pas s'orienter sur ce qu'elle vient de supprimer. Elle est
désormais ancrée sur `home.week `, une expression vivante.

## 6. Relecture du relevé de décisions (`CLAUDE.md §5.2`)

`docs/DESIGN_DECISIONS_UIV2_SURFACES.md` :

| Décision | Verdict |
|---|---|
| **Q1** connexion | non concernée |
| **Q2** — ancre visuelle de l'accueil = barres de récupération | **respectée** : l'ancre n'est pas touchée, et cette carte reste au rang de contexte qu'elle avait |
| **Q3** — « État du jour » replié | non concernée |
| **Q4** — « les valeurs deviennent l'objet, le texte recule » | **respectée**, littéralement : « 4 séances proposées » était du texte autour d'un nombre ; les zones sont la valeur |
| **Q5** — trois rangs de surface | **respectée** : la carte garde son rang **2 (informatif)**. Aucune bordure ajoutée, aucun rang promu — lire son plan n'est pas agir |
| Tokens bleus · feu tricolore | non concernés — aucune couleur introduite |

## 7. Vérifications

`check_scope` **SHARED_CODE** · ruff **OK** · gardes de la tranche **6 vertes**,
2 plantations vérifiées · cliquet des styles inline **vert après resserrage** ·
garde du pluriel **verte** · broad sweep ciblé *(voir appendice)*.

Rendu exposé (`§5.1`) sur la page réelle avant arbitrage — trois variantes — et
après implémentation.

**Mesuré** : carte **306 → 153 px**, page d'accueil **1 821 → 1 700 px**.
La carte dit davantage en occupant moitié moins.

## Verdict

**LIVRÉ.** La carte « Semaine planifiée » nomme ce que la semaine travaille au
lieu de compter ses séances, en moitié moins de place. Le comptage reste, en
support. Six styles inline quittent le gabarit et la dette du dépôt passe de
328 à 322.

**Ce qui reste ouvert** — la résorption des 322 styles restants. Le pire
gabarit, `user_programs/detail.html` (31), porte **19 `margin-top`** : ce n'est
pas un déplacement mécanique vers une feuille, c'est un écran **sans mise en
page**, où les marges individuelles remplacent un `gap`. Sa tranche est une
tranche de layout, et elle mérite son propre arbitrage.
