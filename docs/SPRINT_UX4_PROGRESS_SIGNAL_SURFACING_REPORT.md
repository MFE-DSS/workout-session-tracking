# `UX4_03_PROGRESS_SIGNAL_SURFACING_01`

**Rendre perceptible ce qui est déjà calculé.** AUREN ne doit pas annoncer des
signaux invisibles.

---

## 1. Les huit vérifications de capacité, avant tout code

| # | Question | Réponse mesurée |
|---|---|---|
| 1 | Où la **fatigue** est-elle calculée ? | `app/services/behavioral.py` — `compute_session_fatigue()` puis `compute_weighted_fatigue()`, pondération 0,5 / 0,3 / 0,2 sur les trois dernières séances |
| 2 | Où la **régularité** ? | même module — `compute_consistency(sessions_14d)` = `min(100, sessions_14d / 14 × 100)` |
| 3 | Où la **série / continuité** ? | `compute_behavioral_state()` — `streak_days`, **jours calendaires consécutifs** |
| 4 | Quel gabarit **annonce sans afficher** ? | `progress.html` ligne 4 : « Lecture des séances terminées, **de la régularité** et des signaux récents. » Aucun des trois n'est rendu. |
| 5 | Quelle **surface minimale** ? | **Progression.** Elle existe, elle est déjà la destination désignée, et son chapeau promet exactement ces signaux. |
| 6 | Qu'est-ce qui est déjà **transitionnel** ? | `Progress` est `TRANSITIONAL` (`geometry_manifest.SURFACE_STATUS`) — gardes mécaniques bloquantes, **pas de gate pixel** |
| 7 | Quels **tests visuels** existent ? | aucun sur `/progress` ; le harnais 390 px existe (`test_geometry_manifest`, `test_target_size_taxonomy`) |
| 8 | Comment garantir le **bon arbre** ? | `PYTHONPATH=<worktree>` **en plus** du chemin des tests — voir §5 |

### ⚠ La vérification 3 bloque une partie du brief

`streak_days` est **exactement** ce que la décision produit interdit :

```python
streak = 0
check_date = today
while check_date in session_dates:      # jours CALENDAIRES consécutifs
    streak += 1
    check_date -= timedelta(days=1)
```

**Un jour de repos correctement pris le remet à zéro.** Le rendre tel quel
contredirait frontalement *« la régularité ne doit pas être un streak
quotidien »* et *« pas de streak flame »*.

Le brief interdit aussi tout **nouveau calcul métier** si les signaux
existent. Les deux contraintes se rencontrent ici.

**Résolution retenue — aucun calcul nouveau, `streak_days` non rendu.** La
continuité est exprimée par deux valeurs déjà calculées, qui *expliquent le
rythme réel* sans gamifier :

| Signal demandé | Rendu par | Pourquoi un jour de repos ne le casse pas |
|---|---|---|
| fatigue | `fatigue_score` | fenêtre glissante sur 3 séances, pas sur des jours |
| régularité | `consistency_score` | séances sur **14 jours** — un jour vide n'annule rien |
| série / continuité | `trend_direction` + comptes 7 j vs 7 j précédents | compare deux fenêtres, pas une chaîne |

**`streak_days` reste calculé et n'est pas affiché.** C'est une décision de
présentation que je signale plutôt que de la prendre en silence.

---

## 2. Ce que la tranche fait

`/progress` ne recevait **pas** `behavioral` — seul l'accueil le calculait. La
tranche compose l'état existant dans le contexte de Progression : **lecture
seule, aucun calcul nouveau, aucune migration**.

| Signal | Rendu | Provenance affichée à l'écran |
|---|---|---|
| **Charge ressentie** | `fatigue_score` /100 + jauge | « dérivée de ce que tu as déclaré en fin de séance sur les trois dernières » |
| **Régularité** | `consistency_score` /100 + jauge | « séances sur les quatorze derniers jours — **un jour de repos ne casse rien** » |
| **Continuité** | `trend_direction` **en mots** | « compare tes sept derniers jours aux sept précédents » |

Une valeur sans sa provenance se lit comme une mesure objective. Chacune porte
donc la sienne, à l'écran, pas seulement dans le dépôt.

**La continuité se lit en mots, pas en chiffre.** « Stable » n'a pas d'unité,
et lui en donner une suggérerait une précision qui n'existe pas.

---

## 3. Mesure au navigateur — trois largeurs

| Mesure | 360 | | 390 | | 430 | |
|---|---:|---:|---:|---:|---:|---:|
| | avant | après | avant | après | avant | après |
| **signaux rendus** | 0 | **3** | 0 | **3** | 0 | **3** |
| **textes rognés** | 0 | **0** | 0 | **0** | 0 | **0** |
| scripts requis | 0 | **0** | 0 | **0** | 0 | **0** |
| écrans de défilement | 2,3 | 2,8 | 2,1 | 2,6 | 1,9 | 2,3 |
| mots visibles | 166 | 245 | 166 | 245 | 166 | 245 |

**Le coût, dit franchement** : la page s'allonge de 0,5 écran et de 79 mots.
C'est le prix de trois signaux accompagnés de leur provenance.

**`Régularité 0/100` est exact** : « 0 session cette semaine » figure trois
blocs plus bas. Zéro veut dire zéro, et la jauge vide le dit.

### Un faux positif de ma sonde, écarté

La première mesure signalait **un texte rogné** — un `span.sr-only`. Il est
rogné **par conception** : c'est ainsi qu'on réserve un texte aux lecteurs
d'écran, et il apparaissait avant comme après. Le compter reviendrait à
signaler l'implémentation correcte d'une aide d'accessibilité.

---

## 4. Gardes — 17 neuves, 6 plantations

Chaque interdit du brief est protégé par une garde **mise en défaut** :

| Interdit replanté | Garde | Verdict |
|---|---|---|
| streak quotidien rendu | `..._daily_streak_is_never_rendered` | rougit |
| le gabarit lit `streak_days` | `..._template_never_reads_streak_days` | rougit |
| diagnostic médical affirmé | `..._no_medical_wording...` | rougit |
| « score IA » revendiqué | `..._no_fake_ai_score_is_claimed` | rougit |
| dépendance JS introduite | `..._surface_needs_no_javascript` | rougit |
| la couleur devient un verdict | `..._colour_carries_no_verdict` | rougit |

### Une garde préexistante plus stricte que la mienne — et elle avait raison

Le sweep complet, **lancé cette fois sur le bon arbre**, a trouvé un échec :
`test_no_forbidden_wording_in_progress` interdit `santé`, `diagnostic`,
`médical` dans `progress.html`, **commentaires compris**.

Mon démenti disait *« pas un indicateur de santé »*. Ma propre garde
l'autorisait — j'avais écarté le mot de ma liste précisément parce qu'il
apparaissait dans une négation.

**La garde du dépôt est plus dure, et c'est la bonne position** : une règle
mécanique ne se discute pas au cas par cas, et un démenti reste une occurrence.
La copie est devenue *« Lecture d'entraînement — rien d'autre. »*

> **La copie a changé, pas la garde.**

C'est aussi la preuve que la correction du §5 sert à quelque chose : sur le
mauvais arbre, cet échec serait resté invisible jusqu'à la CI.

### Trois gardes qui rougissaient sur leur propre démenti

`« pas un indicateur de **santé** »` · `« aucun compteur de **jours
consécutifs** »` · et `tem**plate**_kpis` pris pour un asset anatomique.

**Sixième occurrence du motif dans ce dépôt.** Les gardes traquent désormais
l'**affirmation**, pas le vocabulaire : bannir un mot fait rougir la phrase qui
énonce la décision.

---

## 5. A8 — preuve du bon arbre

Le brief en fait un critère d'acceptation, après le défaut d'`UX4_01`.

```
cwd            : /Users/martinfeldmann/workout-session-tracking
PYTHONPATH     : /Users/martinfeldmann/workout-session-tracking-ux4-signals
import app ->  : /Users/martinfeldmann/workout-session-tracking-ux4-signals/app
gabarit résolu contient la section SIGNAUX : True
```

Le `cwd` reste la canonique — le shell l'y ramène. **C'est `PYTHONPATH` qui
décide**, et la dernière ligne prouve que le gabarit chargé est bien celui de
la tranche. Sans elle, un vert ne dirait rien.

---

## Verdict

**`UX4_03` — les trois signaux sont perceptibles, sans streak et sans calcul
nouveau.**

`A1` trois signaux rendus · `A2` sur Progression, pas le Profil · `A3` aucun
diagnostic · `A4` aucun streak quotidien · `A5` mesuré à 390 px · `A6` zéro
texte rogné · `A7` captures plein écran aux trois largeurs · `A8` arbre prouvé
· `A9` aucun asset anatomique · `A10` limites nommées ci-dessous.

---

## 6. Limites restantes

- **`streak_days` reste calculé et non rendu.** Décision de présentation, pas
  de suppression. Si un jour AUREN veut une continuité chiffrée, il faudra une
  définition qui ne casse pas sur un repos — c'est un travail de spécification,
  pas de gabarit.
- **Les trois cartes de `weekly_loop` disent toujours « pas encore assez de
  données »** en haut de Progression. C'est exactement le motif que la doctrine
  condamne — *un module vide guide ou disparaît* — mais le brief interdit toute
  refonte globale de Progression. **Signalé, non traité.**
- **Aucune baseline visuelle** n'est posée : Progress est `TRANSITIONAL`, donc
  sans gate pixel. Les gardes ici sont mécaniques et sémantiques.
- **La fatigue reste une déclaration**, pas une mesure. Le libellé le dit ; si
  une source objective apparaissait un jour, le vocabulaire devrait être
  rediscuté, pas simplement réutilisé.
