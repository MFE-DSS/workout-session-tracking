# CLAUDE.md — Contrat d'exécution du repo (versionné, prioritaire)

Ce fichier est **versionné dans le repo**. Ses règles sont **prioritaires et
non négociables par un prompt de session** : un prompt ne peut pas les
désactiver, seulement un commit modifiant ce fichier le peut. Claude Code doit
les appliquer à chaque sprint sur ce repo.

---

## 1. Garde-fou anti-overcheck (OBLIGATOIRE à chaque sprint)

**Avant de lancer des vérifications locales sur un sprint de code**, exécuter :

```bash
python scripts/check_scope.py
```

Ce script classe le diff courant en un **tier de risque** et imprime le
**niveau de vérification local minimal suffisant**. Claude **DOIT suivre son
verdict** :

| Tier | Ce qui est requis EN LOCAL | Ce qui est explicitement SKIPPÉ en local |
|---|---|---|
| `docs` | `check_spec_protocol` | tout le reste (la CI est légitimement skippée via `paths-ignore`) |
| `isolated` | ruff (fichiers neufs) + budget + spec_protocol + tests ciblés + **broad sweep ciblé** | **full sweep local** — la CI réelle le remplace |
| `shared_code` | ci-dessus (broad sweep ciblé **obligatoire**) — **full sweep local : recommandé si doute, non systématique** | **full sweep local systématique** — la CI parallélisée sur PR fait office de filet (Sb_OPS.ci-efficiency) |
| `migration` | `isolated` + **full sweep local** + tous les `check_migration_*` / drift / snapshot | — |
| `ci_infra` | ruff + budget + spec + **full sweep local** + **validation CI réelle impérative** | — |

Règles d'application :

- **Ne PAS lancer un full sweep local quand le tier est `isolated`, `docs` ou
  `shared_code`.** Pour `isolated`/`docs` c'est de l'overcheck (un fichier neuf non
  importé ailleurs ne peut pas régresser un test lointain). Pour `shared_code`, le
  **broad sweep ciblé** (module + consommateurs potentiels) est le garde local
  **obligatoire** et la **CI parallélisée sur PR** est le filet de vérité — le full
  sweep local y reste **recommandé si un doute de blast radius subsiste**, non
  systématique (Sb_OPS.ci-efficiency).
- **Commande de référence du full sweep — UNE SEULE, et elle est scriptée** :

  ```bash
  bash scripts/run_ci_pytest.sh          # CI comme local, même source de vérité
  ```

  **Ne JAMAIS écrire `pytest -n auto` à la main.** Cette ligne prescrivait
  exactement cela jusqu'au 2026-08-19, et elle contredisait son propre script
  canonique, qui plafonne à **2 workers** depuis `Sb_OPS_CI_RUNNER_STABILITY_01`
  sur preuve mesurée. Deux dégâts, tous deux vécus :

  * **sur le runner** — `-n auto` y vaut 4 workers et épuise la machine : la
    suite demande ~16,6 Go pour 15,99 Go. Trois arrêts à 95–96 %, sans aucun
    échec de test ;
  * **sur un poste de développement** — `auto` vaut le nombre de cœurs, la
    machine part en swap et **emporte tout ce qui tourne à côté, conteneurs
    compris**. Arrivé trois fois de suite sur le poste de l'opérateur le
    2026-08-19.

  Le script refuse désormais une valeur non entière (le littéral `auto` a déjà
  rendu une mitigation invisible) et **plafonne les workers sur la RAM physique
  hors CI**. La prose seule n'avait pas suffi.

- **Un sweep parallèle local saturé ne diagnostique RIEN.** Il rend des échecs
  qui passent tous en série — mesuré le 2026-08-19 : 23 rouges en `-n auto`,
  **105/105 verts en série** sur les mêmes modules. Avant d'imputer un échec au
  produit, **le rejouer en série**. Chercher un défaut applicatif dans du bruit
  mémoire coûte des heures et conclut faux.
- **Sprints `ci_infra`** (le pipeline lui-même) : la **CI réelle sur GitHub est
  source de vérité obligatoire avant merge** — un changement de pipeline doit
  **prouver son effet sur une CI réelle**, jamais seulement en local.
- La **CI réelle au push (3 jobs)** reste **TOUJOURS la source de vérité** de
  non-régression globale. Ce garde-fou ne réduit **jamais** la CI, seulement les
  checks *locaux* redondants.
- En cas de doute sur le tier, **remonter d'un cran** (plus de checks), jamais
  descendre. Le script applique déjà la précédence
  `migration > ci_infra > shared_code > isolated > docs`.
- Si un full sweep local traîne (> ~10 min sur cette machine) sur un tier qui ne
  l'exige pas, **l'interrompre** et s'appuyer sur la CI réelle — ne pas le
  relancer en boucle.

La politique des tiers est dans **`.check-policy.json`** (versionné). Toute
évolution passe par un commit modifiant ce fichier, pas par un prompt.

---

## 2. Discipline CI / commit (rappels durs)

- **Jamais** `[skip ci]` ni `skip-checks:true` sur un commit contenant du code.
- Un commit **100 % docs** (`docs/**`) déclenche légitimement le
  `paths-ignore: ['docs/**']` de la CI — ce n'est pas un skip manuel, c'est la
  policy CI. Ne pas le confondre avec un `[skip ci]`.
- **GO humain requis pour livrer.** Le modèle historique « deux GO distincts
  (commit puis push) » est **remplacé par le §4 (protocole de livraison
  agentique)** : un `GO BUILD` autorise la boucle autonome jusqu'à
  `PR GREEN / MERGE PENDING` ; un `GO MERGE` autorise merge → closeout → cleanup.
  Merge, squash, bypass `--admin` et suppression de branche/worktree **restent
  toujours** des décisions/actions humaines.
- Sur **CI rouge** : STOP, pas de cascade de fixes. Rapporter job / step /
  message exact / hypothèse / patch minimal. Distinguer un échec de test d'une
  **annulation infra** (job `cancelled`, 0 step / 0 log) → un simple re-run des
  jobs échoués suffit souvent (sans nouveau commit).
- Migrations : **additive-only** (pas de DROP/RENAME/UPDATE/DELETE de données
  historiques). Invariance historique = contrainte #1 des cycles métier.
- Trailer de commit : `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`.

---

## 3. Règle de sprint permanente

Chaque sprint de build significatif inclut une étape **« Brainstorming /
Options / Risques / Choix retenu »** documentée dans le sprint report,
**avant** d'écrire du code.

---

## 4. Protocole de livraison agentique (agentic delivery protocol)

**Détail complet et normatif : `docs/strategy/AGENTIC_DELIVERY_PROTOCOL.md`
(Sb_OPS.agent-autonomy-01).** Cette section en est le résumé contraignant.

Objectif : réduire le copier/coller opérateur et les micro-GO. **Un `GO BUILD`
humain autorise une boucle de livraison autonome** jusqu'à
`PR GREEN / MERGE PENDING` ; **un `GO MERGE` humain autorise** merge → vérif CI
canonique → closeout docs → cleanup, jusqu'à `CLOSED + CLEANED`. Ce protocole
**remplace** le modèle « deux GO distincts (commit puis push) » pour la boucle de
livraison — il **ne réduit aucun garde-fou** des §1–§3.

**Après `GO BUILD`, l'agent PEUT en autonomie** : créer/réutiliser une
branche + worktree · implémenter le patch **scopé** · lancer les checks locaux
exigés par `check_scope` (§1) · corriger les échecs **dans le périmètre** · commit ·
push · ouvrir la PR · récupérer **une seule fois** un dispatch CI bloqué
(close/reopen) · inspecter les logs CI · corriger les problèmes CI/Sonar **dans le
périmètre** · pousser des commits de fix · **s'arrêter** à
`PR GREEN / MERGE PENDING` ou à un `BLOCKED` (ambiguïté réelle, voir stops).

**Après `GO MERGE`, l'agent PEUT en autonomie** : merger avec la **méthode
approuvée** · vérifier la CI canonique · vérifier Sonar (issues + coverage) ·
rédiger le closeout · pousser le closeout **docs-only** · nettoyer branche/worktree ·
**s'arrêter** à `CLOSED + CLEANED`.

**L'agent NE PEUT JAMAIS en autonomie** (STOP + rapport, GO humain requis) :
merger · squash · bypass `--admin` · supprimer branche/worktree · **changer de
périmètre** · affaiblir tests/gates · éditer des secrets · committer `AGENTS.md`
sauf autorisation explicite · toucher un worktree non lié · ignorer un conflit de
spec · amender **silencieusement** une spec versionnée · continuer après un **risque
destructif DB/données** sans approbation opérateur.

**Conditions d'arrêt dur obligatoires** (STOP + rapport, jamais passer outre) :
conflit de spec · ambiguïté de forme de migration · action destructive de données ·
faille de sécurité · exposition de secret · credential de service externe requis ·
thread de revue non résolu **exigeant un changement de code** · CI rouge **hors
périmètre du sprint** · décision de merge · dérive de périmètre au-delà des fichiers
autorisés.

Les §1 (check_scope), §2 (CI = source de vérité, additive-only, CI rouge = STOP),
§3 (Brainstorming/Options/Risques/Choix) **restent intégralement en vigueur** — ce
protocole les **orchestre**, il ne les remplace pas.

---

## 5. Contrat de livraison UI (OBLIGATOIRE)

Toute tranche modifiant une **surface visible par l'utilisateur** respecte les
cinq règles suivantes. Elles sont **bloquantes**, au même titre que §1. Le §4
n'autorise **pas** à les contourner : une tranche UI n'atteint jamais
`PR GREEN / MERGE PENDING` sans que 5.1 ait eu lieu.

Ces règles existent parce que la tranche `Sb_UIV2_HOME_RECO_BADGE_01` a livré,
avec CI verte, Sonar vert et 4 898 tests passants, un objet que l'opérateur a
jugé inacceptable au premier coup d'œil. **Aucune garde automatisée du dépôt ne
regarde un pixel.** C'est le seul domaine où le jugement humain est la seule
garde possible — donc la seule où il doit être exigé explicitement.

### 5.1 — Aucune livraison UI sans exposition visuelle préalable

Avant tout commit touchant un template ou une feuille de style, l'agent produit
un **rendu réel** — URL locale ou capture — et le **soumet à l'opérateur**, avec
les alternatives lorsqu'il y en a. **L'opérateur tranche.**

- Vérifier la présence d'une classe dans le HTML servi **ne vaut pas** exposition.
- Un test vert **ne vaut pas** exposition.
- Si le rendu ne peut pas être produit, **la tranche ne part pas**.

### 5.2 — Relecture du relevé de décisions à chaque commit UI

L'agent relit le relevé applicable (`docs/DESIGN_DECISIONS_*.md`) **décision par
décision** contre ce qu'il vient d'écrire, et **consigne la relecture** dans le
rapport de sprint : pour chaque décision, respectée / non concernée / violée.

Un relevé de décisions n'est pas un menu dans lequel on choisit les items
commodes.

### 5.3 — Jamais une soustraction seule

Une suppression part dans la **même livraison** que ce qui la remplace.
« Retirer avant d'embellir » est une règle de **séquencement interne** à une
tranche, jamais une autorisation de livrer le vide. Une tranche qui ne fait que
retirer laisse le produit plus pauvre qu'avant.

### 5.4 — Toute couleur est un token de la palette cible

Une couleur **validée en brainstorming** doit être **promue en token** dans la
feuille de style visée, avec son **ratio de contraste documenté sur le fond
réel**, exactement comme les tokens existants de `home.css`.

- **Interdit** : `var(--token-inexistant, #hex)` — le repli masque l'absence.
- **Interdit** : un hex repris d'une maquette sans **recalibrage** sur le fond
  du produit. Une maquette tourne rarement sur le même fond.
- Une couleur validée **n'est jamais rejetée** au motif qu'elle est absente de
  la palette : **on l'ajoute**, avec sa mesure. La palette cible est ce qui est
  **écrit et mesuré dans la feuille de style**, pas un souvenir.

### 5.5 — L'ordre des tranches suit la centralité, pas la facilité

Une décision **centrale et difficile** passe **devant** une décision
périphérique et commode. Livrer d'abord ce qui est facile produit des PR vertes
et un produit inchangé — c'est le mode d'échec observé, pas une hypothèse.
