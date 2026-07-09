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
| `shared_code` | ci-dessus **+ full sweep local** | — |
| `migration` | ci-dessus + tous les `check_migration_*` / drift / snapshot | — |
| `ci_infra` | ruff + budget + spec + **full sweep local** + **validation CI réelle impérative** | — |

Règles d'application :

- **Ne PAS lancer un full sweep local (`pytest --ignore=... -q`, ~10-15 min)
  quand le tier est `isolated` ou `docs`.** C'est de l'overcheck : un fichier
  neuf non importé ailleurs ne peut pas régresser un test hors de sa surface.
  Le **broad sweep ciblé** (module + consommateurs potentiels) suffit en local.
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
- **Attendre un GO explicite** avant commit, et un GO explicite avant push
  (deux GO distincts) sauf instruction contraire du sprint.
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
