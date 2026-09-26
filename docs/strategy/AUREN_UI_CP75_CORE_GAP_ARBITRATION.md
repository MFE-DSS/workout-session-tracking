# `UI-CP7.5` — paquet d'arbitrage des deux manques du cœur

> Ouvert le 2026-09-26, après la clôture de `UI-CP7` et de `REC-CP5`.
> **Rien n'est commité sur les gabarits de production avant votre arbitrage.**

---

## 1. `CP7` — état final

| | |
|---|---|
| Merge | `fbb4942` |
| CI | 10/10 · Sonar `OK`, couverture nouveau code **100 %** |
| Revalidation | canonique remontée, re-rendue aux deux largeurs |

**Matériellement équivalent au rendu approuvé.** Mesures identiques :

| surface | écrans | cartes | replis | max px | cibles < 44 |
|---|---|---|---|---|---|
| `/science` | 11,1 | 0 | 6 | 32 | 2 |
| `/science/atlas` | 3,9 | 0 | 9 | 32 | 0 |
| `/coach-report` | 3,8 | 0 | 0 | 32 | 2 |
| `/export` | 1,5 | 3 *(voulu)* | 0 | 32 | 0 |

Colonne desktop 68 / 64 / 75 c/l · signature partout · pied générique nulle
part · zéro débordement. Seul écart : `coach-report` 507 → 510 mots, variance
de fixture.

---

## 2. `V3` — **SERVI**

`POLITIQUE_SERVIE = "v3"` · `MEMOIRE_SERVIE = True`

Le blocage de `REC-CP4` était un défaut d'**énoncé**, pas de classement :

1. la **couverture** — critère primaire du rang — se taisait dans sa bande
   médiane (dite seulement > 0,75 ou < 0,25) ;
2. **« jamais fait »** parlait pour tout candidat jamais effectué, qu'il ait
   départagé ou non.

`REC-CP5` corrige les deux. Ce qui a décidé est désormais **lu dans le rang** —
`critere_decisif` rend le premier indice où deux clés lexicographiques
diffèrent — et non deviné.

### Porte franchie, sept conditions

| condition | preuve |
|---|---|
| invariants REC verts | 76 gardes, `CP0a → CP5` |
| mémoire du conseil verte | 23 gardes |
| répétition après refus corrigée | **0/8** (8/8 sans mémoire) |
| répétition légitime possible | garde `CP2` verte |
| ordre de catalogue réduit | **0,10** contre 0,40 |
| explication non appauvrie | **parité mesurée** ci-dessous |
| Mission compréhensible | rendue |

### Parité d'explication, données IDENTIQUES

| | recommandation | raisons |
|---|---|---|
| **V2** | LISS cardio + abdos | « Core 3 j sans muscu — frais à travailler. » · « Niveau de fatigue bas — bon moment pour pousser. » |
| **V3** | LISS cardio + abdos | « Core / Abdos : peu servi sur 14 derniers jours. » · « Zones récupérées. » |

Trois facteurs de chaque côté (la raison principale est rendue en tête). Les
deux de V3 décrivent des critères qui ont **réellement participé au
classement** ; la bande de fatigue globale de V2 n'explique pas le choix de
*ce* gabarit.

⚠ **Le classement de V3 n'a pas bougé d'un pouce**, et une garde l'épingle en
lisant la source de `classer_candidats` pour refuser qu'aucune fonction
d'explication y apparaisse.

---

## 3. Matrice de couverture de la boucle primaire

| surface | ontologie | état | atteignable en prod |
|---|---|---|---|
| Mission | `MISSION` | **2.0** | oui |
| Séance active | `EXECUTION` | **2.0** | oui |
| Débrief | `FLIGHT_RECORDER` | **2.0** | oui |
| Catalogue | `LOADOUT` | **2.0** | oui |
| Coque | `SHELL` | **2.0** | oui |
| Documents | `DOCUMENT` | **2.0** (`CP7`) | oui |
| Lecture corps | `BODY_LEDGER` | **2.0** | oui (`/body/intelligence`) |
| **Acquisition corps** | — | **hérité** | **partiellement** — voir `§4` |
| **Closeout de séance** | — | **hérité** | oui |

---

## 4. `CP7.5A` — acquisition corps

### 4.1 ⚠ La prémisse est plus étroite que prévu, et c'est mesuré

La directive dit : *« `measurement_form` expose encore la matrice de champs »*.
C'est vrai — **de `/body/measurements/new`, qui rend 404 en production.**

Vérifié sur `spignos.com` :

```
/body                    → 404      (body_assessment_enabled = OFF)
/body/measurements/new   → 404
/body/intelligence       → 303      (body_intelligence_enabled = ON)
/profile                 → 303
```

La **seule** surface d'acquisition atteignable est `/profile`, et elle fait
déjà l'essentiel de ce que le `§8` demande :

| `/profile` — mesuré | |
|---|---|
| écrans | 0,9 |
| **champs au repos** | **1** (`weight_kg`) |
| replis | 3 — « Mettre à jour mes mesures · saisie complète » (14 champs), « Données de référence » (3), « Compte » |

### 4.2 Le vrai manque

1. **`/profile` ne sait que CRÉER**, jamais corriger : il appelle
   `create_measurement` et pose une nouvelle ligne datée. « Corriger un fait »
   n'y existe pas.
2. **`/body` sait corriger, mais il est 404.**
3. **Le contrat d'écriture rendait la correction destructrice** — corrigé,
   voir `§4.3`.
4. **Le consentement est vérifié sur le chemin inatteignable et absent du
   chemin atteignable.**

### 4.3 Contrat d'écriture — **FAIT** (non visuel, `§7`)

`update_measurement` acceptait `cleaned` et écrivait **tous** les champs :
absent → `NULL`. Corriger son tour de taille effaçait poids, bras et cuisses.
**La matrice entière était la seule forme que ce contrat autorisait** — ce
n'était pas un choix de mise en page.

Désormais : `champs_soumis` fourni → seuls ces champs sont écrits ; un champ
**soumis vide** reste un effacement explicite ; `champs_soumis=None` conserve
le remplacement historique, pour ne pas faire muter en silence des appelants
non relus.

Six gardes, dont **une sur la vraie route** (`_form_to_raw` fabriquait les
treize clés, donc une garde de service n'aurait rien vu). Vérifiée par
mutation.

| preuve exigée par le `§7` | état |
|---|---|
| taille seule → le reste intact | ✅ |
| poids seul → le reste intact | ✅ |
| effacement explicite borné | ✅ |
| `measured_at` véridique | ✅ |

### 4.4 ⚠ Consentement — une **décision produit**, pas un correctif

Le `§9` demande de finir l'asymétrie `/body` vs `/profile`. Mesuré :

* `/body/*` exige `has_active_consent` avant toute écriture ;
* `/profile` écrit **sans aucune vérification** ;
* **`/body/consent` — le seul endroit où le consentement se donne — est 404
  en production.**

Appliquer le `§9` tel quel **retirerait une capacité existante** : plus
personne ne pourrait enregistrer de mesure, faute de pouvoir consentir.

Trois issues, et le choix vous revient :

| | |
|---|---|
| **A** | allumer `body_assessment_enabled` → `/body` devient atteignable, l'asymétrie se ferme d'elle-même |
| **B** | déplacer l'octroi du consentement sur `/profile`, et l'y exiger |
| **C** | statu quo, consigné comme dette ouverte |

Je ne tranche pas : c'est l'exposition d'une surface, pas une correction.
Aucune interprétation juridique n'est en jeu — la politique est close, c'est sa
**joignabilité** qui manque.

### 4.5 Groupement proposé, **dérivé du produit**

`ZONE_MEASUREMENT` déclare déjà quelle mesure adosse quelle zone
d'entraînement. Le groupement en découle, il n'est pas inventé :

| unité | champs | justification dans le code |
|---|---|---|
| **Poids** | `weight_kg` | seul champ au repos aujourd'hui ; alimente `body_intelligence` |
| **Suivi** | `waist_cm` | `ZONE_MEASUREMENT["core"]`, + tendance `dashboard` |
| **Zones d'entraînement** | `chest_cm`, `arm_*`, `thigh_*` | `ZONE_MEASUREMENT` : pecs, biceps/triceps, quads/posterior |
| **Charpente** | `shoulder_width_cm`, `wingspan_cm`, `hip_cm`, `neck_cm`, `calf_*` | lus par `morphology_readmodel` |

⚠ J'ai failli déclarer `calf_cm_*` orphelin parce que
`ZONE_MEASUREMENT["calves"]` vaut `None`. **Il est consommé** par
`morphology_readmodel` et `body_profile:200`. Vérifié avant d'écrire.

---

## 5. `CP7.5B` — closeout de séance

### 5.1 Ontologie actuelle, mesurée sur une séance réaliste

`/sessions/23/done` — 7 exercices, 21 séries validées :

| | |
|---|---|
| écrans | **2,7** |
| cartes | **8** |
| titres de même rang | 5 |
| sorties de navigation | **5** |
| champs de saisie | **0** |

Blocs rendus : en-tête · **Récap séance** (qualité 92, ressenti) · **Mouvements
remarquables** · invite textuelle + 2 CTA · **Résumé** (work sets,
concentration, énergie, fiabilité 90) · **Top progression** · **Zones
sollicitées** · **Par exercice** (7 lignes) · 2 CTA · **Rouvrir pour éditer**.

### 5.2 Ce que le rendu montre et que les chiffres taisaient

1. **Cinq sorties** sur un écran de transition : « Retour Accueil »,
   « Nouvelle séance → », « Voir la synthèse → », « Historique → », « Rouvrir
   pour éditer ». Aucune n'est dominante.
2. **Deux scores côte à côte, non reliés** : « Qualité : 92 » et « Fiabilité de
   la saisie : élevée (90) ». Rien ne dit ce qu'ils décident.
3. **L'invite de déclaration est du texte, pas une action** : « Pense à
   indiquer ton ressenti sur les **prochaines** séances ». L'écran demande de
   déclarer plus tard au lieu de laisser déclarer maintenant — le `§13` est
   exactement inversé.
4. ⚠ **Collision de vocabulaire, pas contradiction.** « Ressenti : Non
   déductible » (signal **implicite**, dérivé du comportement des séries) et
   « Énergie générale : En forme » (`global_state` **déclaré**) coexistent à
   quatre blocs d'écart dans le même registre lexical. J'ai vérifié avant de
   crier au bug : ce sont deux faits distincts, mal nommés.

### 5.3 Classement des faits (`§14`)

| fait | classement | justification |
|---|---|---|
| en-tête de complétion | **requis** | dit que la séance est close |
| concentration, énergie | **requis à déclarer** | consommés par `behavioral` → `fatigue_score` → **moteur de recommandation** |
| note libre, sensation par exercice | **requis à déclarer** | audit fait : consommés par `quality_score`, `confidence` |
| work sets 21/21 | **utile immédiat** | confirme que la saisie est complète |
| top progression | **`FLIGHT_RECORDER`** | analyse longitudinale |
| zones sollicitées | **`FLIGHT_RECORDER`** | idem |
| par exercice (7 lignes) | **`FLIGHT_RECORDER`** | détail d'analyse |
| mouvements remarquables | **duplication** | sous-ensemble de « par exercice » |
| qualité 92 | **à justifier (`§15`)** | quelle décision soutient-il ici ? |
| fiabilité 90 | **à justifier (`§15`)** | idem, et sa coexistence avec la qualité est illisible |
| rouvrir pour éditer | **`SESSION_LIFECYCLE`** | profondeur, pas transition |

⚠ **Les signaux déclarés ne sont PAS vestigiaux.** L'audit demandé par le `§13`
est fait : `concentration` et `global_state` alimentent `behavioral`, donc le
`fatigue_score`, donc le moteur. Les collecter est justifié — les demander
*« pour les prochaines fois »* ne l'est pas.

### 5.4 Composition candidate

    1. LA SÉANCE EST CLOSE        en-tête, une ligne
    2. CE QUI RESTE À DÉCLARER    l'objet PRIMAIRE — concentration, énergie,
                                  note ; absent si rien n'est requis
    3. CONFIRMATION MINIMALE      work sets 21/21 — la saisie est complète
    4. UNE transition dominante   « Voir le débrief → »
    5. profondeur discrète        rouvrir pour éditer

Top progression, zones et par-exercice **partent vers `FLIGHT_RECORDER`**, qui
les possède déjà. Aucune capacité perdue : la transition y mène.

---

## 6. Ce que j'attends de vous

1. **`§4.4`** — consentement : **A**, **B** ou **C** ?
2. **`§5.4`** — la composition candidate du closeout est-elle la bonne ?
3. **`§5.3`** — « qualité 92 » et « fiabilité 90 » : l'un des deux survit-il au
   closeout, et lequel ?

Les rendus « avant » des deux surfaces vous ont été envoyés. Je produirai les
rendus « après » des quatre états du `§17` dès que ces trois points sont
tranchés.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
