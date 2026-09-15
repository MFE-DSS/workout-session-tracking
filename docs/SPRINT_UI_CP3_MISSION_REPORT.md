# UI-CP3 — MISSION ne possède qu'une question

**Tier `check_scope`** : `SHARED_CODE`.
**Arbitrage opérateur** : concept **B**, transition explicite vers **A**.

> Qu'est-ce que je fais maintenant ?

Tout ce qui ne répond pas à cette question, ne l'explique pas, ne l'exécute pas
ou n'en offre pas la sortie minimale quitte la surface.

---

## 1. Le sol, mesuré avant d'écrire une ligne

Labo semé du catalogue réel (98 exercices de gabarit), six séances terminées
aux valeurs variables, une recommandation authentique — « Pas de cardio récent
→ LISS suggéré pour équilibrer. » — et, pour l'état LIVE, une séance ouverte à
mi-parcours. Viewport 390×844, `checkVisibility()`, identité de page prouvée
avant chaque mesure.

| Compteur | RECO avant | RECO après | LIVE avant | LIVE après |
|---|---|---|---|---|
| Écrans | 1,98 | **1,18** | 1,50 | **1,13** |
| Mots visibles | 121 | **57** | 79 | **51** |
| Cliquables visibles | 7 | **5** | 6 | **4** |
| Champs **visibles** | 0 | 0 | 0 | 0 |
| Champs **dans le DOM** | 27 | **0** | 27 | **0** |
| Écart clé/valeur à 1280 px | ~1 400 px | **45 px** | — | — |
| Largeur de lecture | non bornée | **523 px, constante jusqu'à 1920** | | |

⚠ **Les deux lignes de champs disent la vérité et ne mesurent pas la même
chose.** Zéro champ était visible au repos ; vingt-sept existaient, repliés
dans des `<details>`. Le relevé précédent annonçait « 27 champs » et
surestimait donc ce que l'utilisateur voit. Les deux sont conservés,
étiquetés séparément, plutôt que d'en choisir un.

---

## 2. Cinq défauts mesurés, et un que j'ai failli inventer

1. **L'instrument changeait de grammaire selon son état** — bande à rail en
   RECO, **card encadrée** en LIVE. Même instrument, deux langages, et la card
   est la primitive que le programme retire.
2. **L'état LIVE ne disait pas où l'on en est.** Le labo portait deux exercices
   terminés sur quatre et le troisième entamé ; l'accueil affichait « depuis
   37 min ». Une durée n'est pas une position.
3. **Les lignes s'étiraient sur ~1 900 px en large** — « Core / Abdos » et sa
   valeur séparées par près de 1 400 px.
4. **Cinq objets sous la mission répondaient à d'autres questions.**
5. **Vingt-sept champs de readiness dormaient dans le DOM**, servis à chaque
   affichage.

⚠ **Le défaut que je n'ai PAS rapporté** : la barre de navigation apparaît au
milieu des captures pleine page. Vérifié avant d'écrire — elle est
`position: fixed`. Artefact de capture, pas défaut. Elle coûte en revanche
57 px de hauteur utile en permanence, et c'est compté ci-dessus.

---

## 3. Une grammaire, deux états (`§2`)

```
NOW        ce dont il s'agit
POSITION   où l'on en est            (LIVE)
EVIDENCE   pourquoi                  (RECO : la cause causale)
ACTION     la commande dominante, une seule
ESCAPE     la sortie minimale
```

**Le rail de l'état LIVE est GRAPHITE, pas bleu.** Le bleu signale une origine
système : sur l'état recommandé il relie la cause à la prescription parce que
le moteur les a produites. Une séance déjà ouverte n'est l'affirmation de
personne — la peindre en bleu ferait revendiquer au produit une décision qu'il
n'a pas prise. L'ambre n'apparaît qu'à la commande.

---

## 4. La position (`§3`) — et le coût annoncé qui n'était pas le bon

`app/services/mission_position.py` rend `exercise_index / exercise_total`,
`sets_done / sets_total`, l'exercice de reprise et la série locale.

**En UNE requête d'agrégation.** `AUREN_INSTRUMENTS` attribuait à ce readout le
coût de charger `session_exercises → set_logs` ; c'était le coût de
l'implémentation naïve, et celle-ci l'évite.

Aucun pourcentage, aucune estimation de temps restant : des comptes. Et la
position **se tait** quand elle n'apprend rien — un exercice sans série de
travail prescrite n'a pas de position, et « 1 sur 0 » serait pire que le
silence. Même discipline que le libellé « PASSER AUX SÉRIES » retiré en
`UI-CP2.1`.

---

## 5. Ce qui quitte MISSION, et où ça va (`CLAUDE.md §5.3`)

| Retiré | Destination, dans la MÊME livraison |
|---|---|
| **Bilan 11 zones** | `/progress`. Pas par défaut : la page porte déjà « 11 zones suivies » via `zone_exposure`, mais l'exposition compte des SÉRIES quand ce bilan dit la RÉCUPÉRATION. Côte à côte, « j'ai beaucoup travaillé cette zone » et « elle n'est pas récupérée » se lisent enfin ensemble |
| **Déclaration de readiness** (27 champs) | `/readiness/history`, qui portait déjà la lecture. Porte ajoutée dans BODY_LEDGER |
| **Boucle de coaching** (dernière séance · semaine planifiée) | sortie « Qu'est-ce qui a changé ? » → `/progress` |
| **Tuiles Nouvelle séance / Historique** | la première doublait la sortie secondaire à trois centimètres ; la seconde est absorbée par la même sortie |
| **Lien Progression** | devient cette sortie, nommée par sa QUESTION plutôt que par sa destination |

### ⚠ Le seul retrait qui laisse un trou, et il est nommé

**« ÉTAT D'ENTRAÎNEMENT » n'a aujourd'hui aucune autre surface.** Ses données
et leur producteur survivent — une garde l'exige — mais BODY_LEDGER, que le
rail désigne, ne rend pas encore ce readout. Ce n'est pas masqué : c'est écrit
dans la garde elle-même, et c'est un candidat `UI-CP5`.

### La readiness : mesuré avant de décider

`recommendation.py` **ne lit la readiness nulle part** — zéro occurrence. Elle
ne changeait aucune recommandation, donc elle n'était pas une preuve de
MISSION. Par ailleurs `/readiness/history` n'était atteignable que depuis
l'accueil, **et seulement une fois l'état du jour déjà renseigné** — donc
invisible exactement à qui ne l'avait pas encore fait. Réunir la déclaration et
sa lecture referme les deux trous d'un coup.

---

## 6. Le pont, et sa date de péremption (`§6`, `§7`)

Le rail de transition **n'est pas une primitive de cockpit AUREN**. Deux
sorties de faible emphase, nommées par la question qu'elles servent, **zéro
métrique**.

> **QUAND `FLIGHT_RECORDER` EXISTE (`UI-CP5`), CE RAIL EST RÉÉVALUÉ ET RETIRÉ.**

Le critère est écrit dans le gabarit **et** dans la feuille de style, et une
garde échoue si la mention disparaît. Un pont sans date devient une fondation.

---

## 7. ⚠ Une garde de MESURE que j'ai raffinée — arbitrage à confirmer

`test_no_home_tile_leads_where_the_shell_already_leads` interdisait toute
destination d'accueil déjà présente dans la barre basse. Elle reposait sur un
constat : deux tuiles « Progression » et « Programmes » répétaient la coque, en
plus gros, à trois centimètres.

Mes deux sorties mènent à `/progress` et `/profile` — **toutes deux dans la
barre basse**.

La règle devient : *une sortie peut partager une destination de la coque à
condition d'être nommée par la QUESTION, jamais par le nom de la destination.*
« Progression » est un doublon de navigation ; « Qu'est-ce qui a changé ? » est
un renvoi de contenu.

**Mutation prouvée dans les deux sens**, y compris le cas vicieux — un nom
d'onglet déguisé en question (« Progression ? ») rougit aussi.

C'est un assouplissement d'une garde issue d'une mesure, sur la foi d'une
directive plus récente. **Signalé pour confirmation, pas présenté comme une
évidence.**

---

## 8. Cinq calculs morts retirés de la route

Relevé sur les gabarits, pas de mémoire : `kpis`, `sparkline_svg`,
`sparkline_has_mixed_kinds`, `behavioral` et `reco_zone_state` étaient
calculés à **chaque** affichage de l'accueil et consommés par **rien**.
`kpis` sert bien à `/progress` — mais `/progress` le calcule lui-même ; dans
`index.html`, son unique occurrence était un **commentaire**.

Le plus cher chargeait quatorze jours de séances avec
`session_exercises → set_logs` pour un score composite par séance. **C'est
exactement le coût que l'ontologie attribuait à la position intra-séance —
déjà payé, pour un rendu inexistant.**

Les services ne sont pas supprimés, et une garde l'exige : c'est l'appel MORT
sur cette route qui part.

---

## 9. Gardes

**21 gardes neuves** (`tests/test_ui_cp3_mission.py`), **8 mutations plantées,
8 rougissent la bonne garde**, arbre restauré — patch identique octet pour
octet avant/après.

**16 gardes converties ou reciblées**, chacune avec sa remplaçante nommée dans
le même fichier :

| Classe | Traitement |
|---|---|
| 8 dans `test_recovery_home_consumer` | reciblées sur la VUE-MODÈLE, qui survit ; plus une garde « MISSION ne rend plus la tuile » |
| 6 de composition d'accueil | le véhicule change (`today-home__secondary-zone` → `mission-bridge`), la propriété reste |
| `test_the_tile_renders_on_home` · `test_home_route_renders_coaching_loop_section` | supersédées par « le producteur survit » + « MISSION ne le rend plus » |
| 3 de duplication de coque | raffinées, voir `§7` |

Une garde n'a pas été « reciblée » mais **supersédée honnêtement** :
`test_the_tile_uses_a_semantic_heading` était une propriété de RENDU dont
l'objet n'a plus de surface. La recibler aurait été mentir ; elle garde
désormais ce qui conditionne le futur rendu — un libellé distinct et non vide.

---

## 10. Cinq défauts que seul le sweep a trouvés

Le premier sweep a rendu **26 échecs**, et cinq n'étaient pas des gardes
périmées mais des défauts que j'avais introduits :

| Défaut | Nature |
|---|---|
| `--t-fg-faint` sur la flèche du rail | **faute de token** — je l'avais traitée comme décorative parce qu'elle est `aria-hidden` ; elle reste du texte rendu |
| seconde déclaration de `.today-home__hero--active` | j'écrasais une règle au lieu de la corriger (`css:S4666`) |
| clé de contexte `zone_recovery_tally` | le NOM contenait `zone_recovery` et déclenchait la garde qui interdit à un gabarit d'appeler ce service. Renommée `zone_tally` — la garde n'est pas affaiblie |
| aplat ambre sur `readiness_history.html` | **le même bouton a déménagé** : index 5 → 4, readiness 0 → 1, total produit inchangé |
| `index.html` : 13 styles en ligne → **0** | le cliquet est strict DANS LES DEUX SENS et exigeait le resserrement |

Deux défauts de rendu, trouvés seulement en regardant : un séparateur `·`
**orphelin en fin de ligne** quand la position passe à la ligne, et le champ
« FC repos (bpm) » **plus étroit que son propre libellé** — 150 px de plafond
pour 138 px nécessaires. Ce second est PRÉÉXISTANT : il vivait replié sur
l'accueil, le déplacement l'a mis en lumière.

---

## 11. Vérifications

| Contrôle | Résultat |
|---|---|
| `check_scope` | `SHARED_CODE` |
| **Sweep local complet** | **`tous les lots sont verts.`** — lu dans le journal, **125/125 lots**, **329/329 fichiers**, **0 ligne `FAILED`**, `Aucun fichier sauté`, **sortie 0 du script lui-même** |
| commande du sweep | chemin **absolu**, **aucun pipe** — le script fait `cd` vers l'arbre du SCRIPT, donc un appel relatif depuis la canonique aurait balayé la canonique |
| `ruff` | propre sur les fichiers touchés |
| `check_ruff_budget` | 268 ≤ 548 |
| `check_spec_protocol` | OK |
| pré-scan `S9073` | 0 — une assertion composite a été réécrite avant le push, elle aurait cassé le gate à elle seule |
| Rendu exposé à l'opérateur | **avant tout commit de gabarit** (`CLAUDE.md §5.1`) |

⚠ **La leçon de la tranche précédente est appliquée, pas seulement citée** :
`UI-CP2.1` avait été poussée sur un sweep dont la sortie passait par
`grep | tail` — le motif ne contenait pas la ligne d'échec, `tail` jetait les
105 premiers lots, et le code de sortie venait de `tail`. Ici le verdict est la
**présence de la phrase de succès**, jamais l'absence de phrases d'échec.

---

## 12. Relecture du relevé de décisions (`CLAUDE.md §5.2`)

| Décision | Statut |
|---|---|
| Une seule commande dominante par état | **respectée** — gardée, et le compteur a dû être corrigé (`today-home__cta` est une sous-chaîne de `today-home__cta-form`) |
| Ambre = action utilisateur, bleu = origine système | **respectée** — et c'est ce qui a imposé le rail graphite en LIVE |
| `card` n'est plus une primitive souveraine | **respectée** — l'état LIVE cesse d'en être une |
| Jamais de couleur seule pour distinguer un état | non concernée — aucun état nouveau |
| Zéro framework, SSR socle fonctionnel | **respectée** — aucun script ajouté |
| Pas de score composite, pas de feu tricolore | **respectée** — la position est faite de comptes |
| Cible tactile 44 px | **respectée** — `min-height: 44px` sur les sorties du rail |
| Token mesuré, jamais de repli `var(--x, #hex)` | **respectée après correction** — voir `§10` |

---

## 13. Ce que cette tranche N'EST PAS

Elle rend MISSION **sobre et souveraine**. Elle ne la rend **pas encore
personnelle**.

MISSION reste **sans mémoire** : elle recalcule à chaque affichage, et le même
moteur avec le même bilan de zones produit la même phrase pour n'importe qui.
Le triptyque du récit de données — *ce qui a changé · pourquoi ça compte · quoi
faire* — n'en porte que les deux derniers tiers.

C'est le périmètre de **`UI-CP3.5 CONTINUITÉ`**, ouvert séparément. Cette
tranche en est le socle : poser la continuité sur l'empilement de cinq blocs
qu'on vient de retirer en aurait fait le sixième.
