# Sb_VNEXT_MOBILE_EXEC_DOGFOOD_01 — les notes d'exécution du dogfood

**Statut** : ✅ mergée (PR #284, `8e71d03`) · **Branche** : `sb/vnext-mobile-exec-dogfood-01` · **Base** : canonique `bca942d` (D9 mergée)
**Source** : retours de dogfood opérateur sur iPhone, `SPRINT_Sb_VNEXT_NATIVE_N0_EXPERIENCE_LAB_REPORT.md §6quater` (R1–R16) et `SPRINT_Sb_VNEXT_MOBILE_D9_01_REAL_BACKEND_BRIDGE_REPORT.md §6.1` (R17–R20).

Ordre opérateur du 2026-10-25 : « go next step sur le critical path ». Les notes qui ne demandent
**aucun asset** passent d'abord ; celles qui en demandent attendent le cahier des charges remis le
même jour (logo, DA par famille, images d'exercice).

---

## 1. Brainstorming · Options · Risques · Choix retenu (`CLAUDE.md §3`)

### 1.1 Périmètre — par centralité (`§5.5`)

| Rang | Note | Pourquoi ce rang |
|---|---|---|
| 1 | **R10** passer une série (« très important ») | touche chaque série ; aujourd'hui l'utilisateur est bloqué sur une série qu'il ne fera pas |
| 2 | **R12** passer un exercice entier | même blocage, à l'échelle de l'exercice (machine absente, douleur) |
| 3 | **R8 + R11** remplacer à chaque série, liste classée N1→N3 | le remplacement existe mais est caché et non classé |
| 4 | **R13** lecture de la performance par ligne au bilan | le calcul existe (`performance.ts`), seul le rendu manque |
| 5 | **R6** « première fois » = la charge devient la référence | une phrase |
| 6 | **R9** journal de l'appareil hors du menu utilisateur | instrumentation, pas un écran produit |

**Hors tranche** : R14 (texte de l'explication servie, partagé avec le web — tranche MISSION),
R18–R20 (refonte MISSION, attend la DA par famille), R1, R2, R4, R5, R7 (assets).

### 1.2 Les sémantiques — aucun état neuf

| Geste | Représentation | Écriture serveur |
|---|---|---|
| **Passer une série** | la série reste **non faite** : c'est déjà la sémantique produit (série non validée = série non faite) | **aucune** ; à la fin, `completion_of` la compte comme non faite et la continuité l'enregistre comme le web |
| **Passer un exercice** | toutes ses séries restantes restent non faites | **aucune** |
| **Annuler un « passer »** | retour à l'état d'avant, pendant quelques secondes | aucune — rien n'avait été écrit |

Le curseur suit **la table de transitions du serveur** (`on_complete`) : passer une série, c'est
prendre la transition de cette série sans repos ; passer un exercice, c'est suivre les transitions
jusqu'à changer d'exercice. Aucune logique de séance n'est recréée sur l'appareil.

### 1.3 ⚠ Conflit entre une note et une règle du domaine — R8

L'opérateur veut le remplacement **disponible à chaque série**. La règle canonique (`can_substitute`,
web et API) l'interdit **dès qu'une série de travail de l'exercice est faite** : une séance porte
**un** nom exécuté par exercice ; changer de machine en cours d'exercice ferait porter aux séries
déjà faites le nom du remplaçant — un faux fait.

| Option | Coût | Verdict |
|---|---|---|
| A — icône visible à chaque série ; après la 1ʳᵉ série faite, elle dit pourquoi le remplacement n'est plus possible | aucun changement de domaine | **retenue pour cette tranche** |
| B — permettre le changement en cours d'exercice | découper l'exercice en deux occurrences (le fait d'avant reste sous l'ancien nom) : changement de modèle, donc spec et probablement migration | **à arbitrer par l'opérateur**, hors tranche |

### 1.4 Options d'interface et risques

| Question | Choix | Risque couvert |
|---|---|---|
| Où « passer la série » ? | action **secondaire** grise sous « Valider la série », séparée par un espace | toucher par erreur : en plus, un bandeau **« Série passée — Annuler »** pendant 5 s |
| Où « passer l'exercice » ? | dans le ⋯ de l'exercice, qui devient le menu des **gestes d'exercice** | même bandeau d'annulation |
| Où « remplacer » ? | une **icône dédiée ⇄** à droite du nom de l'exercice (R8), la liste classée s'ouvre depuis elle | l'icône ne doit pas concurrencer « Valider » : taille et ton secondaires |
| Niveaux de remplacement (R11) | le serveur envoie déjà N1/N2/N3 et leurs badges (« Équivalent », « Proche », « Élargi ») ; le read model les transmet | les couleurs vert → orange **ne portent jamais seules le sens** : le badge écrit les double ; elles deviennent des **tokens mesurés** (`§5.4`) et ne doivent pas se confondre avec l'ambre d'action ni le corail d'alerte |
| Performance au bilan (R13) | chaque ligne d'exercice dit **au-dessus / conforme / en dessous** de la prescription, avec un marqueur et un libellé ; première séance = « repère posé », sans jugement | mêmes contraintes de tokens |
| Journal (R9) | visible seulement dans les builds de développement (`__DEV__`) ; la déconnexion reste accessible depuis la mission | une build de production n'expose plus l'instrumentation |

**Choix retenu** : R10, R12, R8 (option A), R11, R13, R6, R9 dans une tranche, rendu iPhone
**avant tout commit d'interface** (`§5.1`), tokens mesurés et soumis (`§5.4`).

---

## 2. Réalisation

| Note | Ce qui est livré | Où |
|---|---|---|
| R10 | « Passer cette série », action secondaire grise sous « Valider » ; la série reste non faite, aucun repos, rien d'écrit ; bandeau **« Série passée — Annuler »** 5 s ; pastille « — passée » | `workout.ts` (`SKIP_SET`), `ExecutionScreen`, `ConnectedApp` |
| R12 | « Passer cet exercice » dans le ⋯ ; les séries restantes de l'exercice, trouvées en suivant la table de transitions du serveur ; même annulation | `workout.ts` (`SKIP_EXERCISE`, `remainingOfExercise`) |
| R8 | icône **⇄** à droite du nom de l'exercice, à chaque série ; après la 1ʳᵉ série faite, elle explique pourquoi le remplacement n'est plus possible (option A, §1.3) | `ExecutionScreen` |
| R11 | liste **classée par le moteur** N1 → N3, badge du moteur (« Équivalent », « Proche », « Élargi ») et teinte ; le read model transmet `substitute_options` dans l'ordre du moteur | `mobile_read_models.py`, `SwapSheet` |
| R13 | chaque ligne du bilan : ▲ au-dessus · ● conforme · ▼ en dessous · ◆ repère posé (première fois, sans jugement) — marque, mot et bordure, jamais la couleur seule | `performance.ts` (`lineReading`), `CompleteScreen` |
| R6 | « Première fois : la charge que tu valides devient ta référence. » | `ExecutionScreen` (`Guidance`) |
| R9 | le journal n'apparaît dans le ⋯ de l'app connectée qu'en build de développement | `ExecutionScreen` |

**Garde-fou d'annulation** : passer la *dernière* série mène au bilan, qui envoie la clôture au
serveur. La clôture attend la fin de la fenêtre d'annulation, sinon « Annuler » arriverait après
une séance déjà close côté serveur.

**Tokens (`§5.4`)**, mesurés le 2026-10-25 sur les surfaces réelles et inscrits dans `theme.ts` :

| Token | Valeur | Sur `plate` #191C22 | Sur `field` #0A0B0D | Distance aux rôles pris |
|---|---|---|---|---|
| `subN1` Équivalent | #6FD69A | 9,56 : 1 | 11,03 : 1 | ΔE ambre 77 · corail 87 |
| `subN2` Proche | #C9D46B | 10,66 : 1 | 12,29 : 1 | ΔE ambre 41 · corail 66 |
| `subN3` Élargi | #E8935F | 7,13 : 1 | 8,22 : 1 | ΔE ambre 29 · corail 20 — la plus proche ; teinte + badge, jamais un aplat |
| `perfAbove` | #6FD69A | 9,56 : 1 | — | — |
| `perfBelow` | #B7A3F0 | 7,73 : 1 | — | ΔE corail 67 : « en dessous » est une lecture, pas une erreur |

## 3. Rendu soumis à l'opérateur (`CLAUDE.md §5.1`)

Rendu sur iPhone 15 Plus (build de développement, backend réel du Mac), le 2026-10-25 :
**validé par l'opérateur** (« ouais, ça me va, tu peux commit l'interface »). Les couleurs et
l'option A de R8 ont été présentées comme points à trancher, et acceptées en l'état.

Preuve observée au passage — **porte G de D9, moitié « abandonner »** : la séance Push A du
dogfood est close et exclue (`completed`, `excluded_from_stats`), sa série faite (5 kg × 6) est
restée en base.

## 4. Relecture des décisions (`CLAUDE.md §5.2`)

Relevé applicable : spec vNext (`§0quater`, `§0quinquies`) ; les relevés web
(`DESIGN_DECISIONS_*`) ne sont pas concernés (aucune route HTML touchée).

| Décision | Verdict |
|---|---|
| D3 — une commande par série | **respectée** : passer n'écrit rien, valider reste le seul geste qui écrit une série |
| D5 — une action primaire | **respectée** : « Passer cette série » est secondaire, grise, séparée de « Valider » |
| D6 — préremplissage | non concernée |
| D7 — 90 s par défaut | **respectée** : passer ne déclenche aucun repos (rien n'a été fait) |
| D8 — mouvement réduit, haptique | **respectée** : haptique légère sur passer ; rien d'animé en plus |
| D11 — heure | non concernée (aucune écriture) |
| D12 — score + récompense | **respectée** : R13 lit la séance contre la prescription, sans score ni total |
| D14 — récupération d'abord | non concernée |
| O1 — « l'IA » | non concernée |

## 5. Vérifications

| Porte | Résultat |
|---|---|
| `check_scope` | **SHARED_CODE** (`mobile_read_models.py`) |
| Sweep large ciblé | read model, API mobile, substitution (7 fichiers), TRAIN A, mémoire de conseil : **205 verts** |
| Client | `tsc` propre · **107 tests jest** (dont passer une série / un exercice, bilan R13) |
| ruff · pré-scan Sonar | propres sur le code applicatif |

**Verdict :** les six notes d'exécution sans asset sont livrées et validées sur iPhone ; aucun
état neuf, aucune écriture neuve. Restent la refonte MISSION (R18–R20) et les notes qui attendent
les assets (R1, R2, R4, R5, R7), ainsi que l'option B de R8 si l'opérateur la veut.

---

## Closeout

| | |
|---|---|
| PR | [#284](https://github.com/MFE-DSS/workout-session-tracking/pull/284) — merge commit, tête épinglée `4c45b7a` (GO MERGE permanent) |
| Merge | `8e71d030e320f6f84bcd712ff00cf5e13cb03c60` |
| CI canonique | run `40173875266` sur `8e71d03` — **verte** |
| Sonar (PR) | gate **OK** — 0 bug, 0 smell, 0 vulnérabilité, duplication 0 % ; la couverture du nouveau code n'est pas rapportée (le code neuf est surtout TypeScript, hors couverture Python ; il est couvert par les 107 tests jest) |
| Threads de revue | 0 |
| Migration | aucune |

### Incidents

Aucun : premier passage vert sur tous les jobs.

### Ce qui reste ouvert

- Refonte MISSION (R18–R20, R14) : demande un read model d'historique et la DA par famille.
- Notes qui attendent les assets (R1, R2, R4, R5, R7) : cahier des charges et prompt designer remis
  à l'opérateur le 2026-10-25.
- R8 option B (changer de machine en cours d'exercice) : changement de modèle, arbitrage opérateur.
- Portes E–F–G de D9 sur appareil ; L3 distribution (D10).
