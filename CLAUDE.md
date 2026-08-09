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
- **Commande de référence du full sweep** (parallélisée depuis `Sb_OPS.ci-efficiency`,
  ~4 min au lieu de ~14, même couverture) :
  `pytest -n auto --dist worksteal --ignore=tests/test_v1_acceptance.py --cov=app --cov-report=xml -q`.
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
