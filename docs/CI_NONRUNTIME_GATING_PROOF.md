# Preuve d'exécution — chemin NON_RUNTIME (Sb_CI_02_1_PATH_AWARE_GATING)

Document **temporaire** servant de charge utile à une PR de preuve. Son unique rôle : produire une
pull request dont le **diff entier** est sous `docs/**`, afin d'exercer réellement le chemin
`NON_RUNTIME` du gating avant de merger le sprint.

## Pourquoi une PR séparée est nécessaire

Le classifieur évalue le **diff complet de la PR contre sa base**, pas le dernier commit. C'est
délibéré : juger au dernier commit permettrait à une PR contenant du code runtime de **sauter la
suite de tests** sur un commit docs final — un trou de sécurité réel.

Conséquence : la PR du sprint (#71) contient `.github/workflows/ci.yml`, `scripts/` et `tests/`,
elle est donc `RUNTIME_OR_INFRA` **de bout en bout**, y compris après un commit docs-only. Elle ne
peut pas, par construction, prouver le chemin `NON_RUNTIME`.

Cette PR-ci a pour **base la branche du sprint** : son diff est uniquement ce fichier, le workflow
gaté est présent des deux côtés, et le chemin `NON_RUNTIME` est donc exercé pour de vrai — sans
rien merger.

## Attendu

- le job `pytest + QA scripts` **existe et réussit**, sans exécuter pytest, la couverture, ni les 8 scripts QA ;
- l'étape « Non-runtime change — full suite intentionally skipped » s'exécute ;
- le job `lint` s'exécute **intégralement** (gitleaks, spec protocol, ruff budget, bandit, actionlint, shellcheck, pip-audit) ;
- le check **externe** « SonarCloud Code Analysis » est émis et **SUCCESS** ;
- **aucun** check requis ne reste `Expected`/`Pending`.

Cette PR est **destinée à être fermée sans merge** une fois la preuve relevée.
