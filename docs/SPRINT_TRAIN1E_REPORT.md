# `TRAIN1-E` — Hygiène de surface et surfaces sociales

**Canonique de départ** : `7342373` · **Tier `check_scope`** : `SHARED_CODE`
**Arbitrages exécutés** : C4 · C6 · C7 · C9 · C11

---

## 1. Brainstorming / Options / Risques / Choix retenu (`CLAUDE.md §3`)

### Ce que le parcours exhaustif a changé au cadrage

Avant cette tranche, la carte du produit reposait sur **13 surfaces choisies à
la main** sur 53 routes GET. Un parcours automatique du produit authentifié en
a atteint **69**, à 390 px **et à 1024 px**, avec une séance **en cours** dans
la graine — deux angles morts que la liste manuelle ne pouvait pas voir.

Deux constats ont directement changé le travail :

1. **Le radar physique vivait sous TROIS classes CSS différentes** —
   `tooltip-radar` au classement, `radar-wrap` au profil public,
   `profile-preview__radar` dans la carte d'aperçu. Une garde visant une seule
   d'entre elles en aurait laissé deux en place, et le relevé aurait affiché
   « 0 radar » en toute confiance.
2. **Mon propre instrument comptait faux sur l'Historique.** Je rapportais 17
   cibles sous 44 px. Vérifié au `checkVisibility()` et à `elementFromPoint` :
   divulgation fermée — l'état par défaut — les deux boutons de gestion rendent
   `false` et un appui à leur centre atteint la **carte** en dessous. **Ils ne
   sont pas tapables.** Le vrai chiffre est **une** cible par ligne.

### Le dossier que C6 rouvre

`UIV3_TARGETS_44_01` avait **déféré** ces cibles, avec une raison mesurée et
deux justifications. Une seule a expiré :

| Justification d'origine | Aujourd'hui |
|---|---|
| « les fermer demande de l'ESPACE, donc un changement structurel » | **toujours vraie** — remesuré : 26 px de haut, 8 px au-dessus, 4 px en dessous ; un remplissage à 44 px chevaucherait la carte et les boutons |
| « `history` est `TRANSITIONAL`, sa mise en page est programmée pour `UX4_03` » | **expirée** — `UX4_03` a été livré sans toucher l'Historique, et C6 tranche désormais explicitement sa forme |

Le changement structurel n'est donc plus une contractualisation prématurée :
c'est la forme décidée. **Coût assumé : +18 px par ligne repliée.**

---

## 2. Ce que la tranche livre

### C4 — l'analytique physique quitte les surfaces sociales

| Surface | Avant | Après |
|---|---|---|
| `/leaderboard` | 2 radars en infobulle, 4 lettres | **0 radar**, 4 lettres |
| `/users/{username}` | 1 radar + « Score · N/100 » | **0 radar, 0 score**, 1 lettre |
| `/users/{username}/preview` | 1 mini-radar | **0 radar**, 1 lettre |

**La lettre reste, et ce n'est plus une tolérance.** Elle vient de
`compute_grade`, dérivée de la qualité de séance — pas du physique. Un
classement sans ordre n'est pas un classement.

**Le score sur autrui était le pire survivant de la doctrine.** Un score sur
100 que le produit ne sait pas justifier est déjà discutable pour soi ; rendu
sur le profil de quelqu'un d'autre, il devient une comparaison — ce que le
contrat du rapport coach s'interdit explicitement (« pas de comparaison vs
autres utilisateurs »).

**Le classement ne dépend plus du tout de `muscle_scoring`** : il ne l'importe
plus et ne l'appelait pas moins d'**une fois par ligne affichée**.

### C6 — l'Historique

Les deux moitiés de la décision étaient **déjà en place** : la ligne est un
`<a>` de 358×101 px, et les actions de gestion vivent derrière une divulgation.
Ce qui manquait était l'espace.

| Contrôle | Avant | Après |
|---|---|---|
| `summary` « Gérer cette séance » | 358×**26** | 358×**44** |
| bouton « Exclure des KPI » | 130×**27** | 142×**44** |
| bouton « Supprimer » | 87×**27** | 99×**44** |
| lien « choisir un template » (état vide) | 160×**16** | **44** de zone |

**Historique : 17 → 2 cibles sous le standard**, et les deux restantes sont la
coque (marque de la topbar, lien Contact), communes à toutes les surfaces.

Les styles en ligne partent avec : rien ne pouvait être visé tant que tout
était écrit dans l'attribut `style`.

> ⚠ **44 px est le STANDARD PRODUIT AUREN**, pas le seuil WCAG 2.2 (24×24 avec
> exception d'espacement, déjà satisfait avant cette tranche). Aucune
> non-conformité réglementaire n'est corrigée ici, et je ne l'annoncerai pas
> comme telle.

### C7 — les modules vides

- **Export** : la carte « Sauvegarde planifiée » ne s'instancie plus pour dire
  « Aucune sauvegarde locale détectée ». Les deux `—` du résumé disparaissent
  avec leurs lignes — dans un tableau dont la première ligne dit déjà
  « 0 sessions », un tiret ne faisait que répéter ce zéro.
- **Mes programmes** : « Pourquoi ce plan ? » ne s'affiche plus sans
  explication ; la liste vide devient une ligne compacte.
- **PAS de second CTA.** Le bouton « Créer un programme » existe déjà en tête
  de page, toujours visible. En ajouter un dans l'état vide aurait rejoué
  exactement la duplication qu'A4 interdit — une garde compte qu'il y en a
  **un seul**.

### C9 — `DO_NOT_ACTIVATE_AS_STANDALONE`

Consigné dans `docs/LEGACY_SCORE_CONSUMERS.md` : internes réutilisables
préservés, aucune nouvelle surface branchée, anciens consommateurs retirés
progressivement.

**Conséquence mesurable** : il ne reste que **deux** appelants de
`compute_physique_dashboard`, et **aucun n'est atteignable par un
utilisateur** — Body Intelligence derrière son drapeau éteint, et le tableau de
bord qu'aucune route ne rend. Sa suppression devient un travail de nettoyage,
plus un arbitrage produit.

### C11 — statut des surfaces

`PROGRESSION_L1 = SOVEREIGN` · `PROGRESSION_L2 = EVOLVABLE`, consigné avec ce
que la distinction permet : geler quatre tranches de travail **sans** interdire
d'approfondir l'inspection, qui est précisément là où la cible
`FAIT → INSTRUMENT → INSPECTION → PROVENANCE` continue de se construire.

---

## 3. Relecture des décisions UI (`CLAUDE.md §5.2`)

| Règle | Verdict |
|---|---|
| **5.1** exposition préalable | **respectée** — géométrie relevée au pixel avant ET après, sur les six surfaces touchées |
| **5.2** relecture consignée | **respectée** — ce tableau |
| **5.3** jamais une soustraction seule | **respectée** — le radar part, la lettre et les KPI publics restent et deviennent le contenu ; la carte de sauvegarde part, « Télécharger » reste la réponse à « comment j'archive » ; « Pourquoi ce plan ? » part, la liste dit déjà l'absence |
| **5.4** toute couleur est un token mesuré | **non concernée** — aucune couleur introduite ; les changements sont dimensionnels |
| **5.5** centralité avant facilité | **respectée** — C4 (la doctrine survivant sur le profil des autres) avant C6, puis les modules vides |

---

## 4. Mes propres fautes

1. **Mon relevé comptait 17 cibles là où il y en a une.** La sonde mesurait
   `getBoundingClientRect()` sans `checkVisibility()` : elle comptait des
   boutons dans une divulgation fermée, que personne ne peut toucher.
   **Troisième instrument défectueux de la semaine**, et celui-ci a failli
   me faire dimensionner un travail trois fois trop gros.
2. **Une garde passait pour la mauvaise raison** — `min-height: 44px` cherché
   **quelque part** dans la section CSS : abaisser le seul
   `.history-item__toggle` la laissait verte, satisfaite par la règle voisine.
   Elle extrait désormais chaque sélecteur séparément. *Trouvée en plantant le
   défaut.*
3. **Deux `{% if true %}` laissés en échafaudage** par des éditions scriptées,
   nettoyés avant commit.
4. **Mon script de géométrie a d'abord mesuré la page de connexion** — cookie
   refusé en silence, zéro ligne rendue, aucune erreur. Le garde-fou existait
   dans mes autres sondes et manquait dans celle-ci.

---

## 5. Vérifications

| Contrôle | Résultat |
|---|---|
| `check_scope.py` | `SHARED_CODE` |
| ruff, reproduction exacte du rapport CI | **0** occurrence sur une ligne de la tranche |
| `check_ruff_budget.py` | **276** ≤ 548 (−2 : du code est parti) |
| `check_spec_protocol.py` | OK |
| pré-scan AST | 1 `S9073` trouvée dans mon code neuf, corrigée avant push |
| gardes plantées | **13 / 13 rougissent** |
| gardes existantes migrées | **5**, aucune supprimée ni affaiblie |
| suite complète en local | 113 lots + queue de 48 fichiers, **tout vert** |

**Une garde a signalé son propre sujet.** `test_the_remaining_score_consumers_are_the_recorded_ones`,
écrite en `TRAIN1-C` pour rougir **dans les deux sens**, a rougi parce que deux
consommateurs avaient *disparu* sans que le registre soit mis à jour. C'est
exactement ce pour quoi elle existe.

---

## 6. Ce que je n'ai pas fait, et pourquoi

- **Les cibles sous 44 px du classement et du profil public** (4 liens de nom à
  17 px, un « ← Retour » à 21 px) restent. Je les avais proposées ; l'opérateur
  a répondu de m'en tenir à l'Historique. Mesurées et consignées ici plutôt que
  corrigées au passage.
- **`/` déborde horizontalement à 1024 px** — seule surface du produit dans ce
  cas, et elle est `SOVEREIGN`. Découverte par le parcours exhaustif, hors
  périmètre de cette tranche, remontée à l'arbitrage.
- **`/science/atlas` — 15,3 écrans, 2 074 mots, 32 boîtes** : la surface la
  plus lourde du produit, absente de toutes les cartes précédentes.
- **`rules.html` est un second gabarit mort** (comme `dashboard.html`) :
  `/rules` redirige vers `/science`.
